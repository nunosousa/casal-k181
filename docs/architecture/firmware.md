# Firmware architecture

Cross-cutting firmware architecture for both nodes. Covers application
partition, language choices, RTOS approach, flash layout, bootloader
design, task decomposition, config and log storage, build system,
testing, and firmware update flow.

Constrained by:

- [ADR-0002: Skip mechanical points](../project/decisions/0002-skip-mechanical-points.md)
- [ADR-0003: MCU family selection](../project/decisions/0003-mcu-family-selection.md)
- [ADR-0004: Kick-start with flat battery](../project/decisions/0004-kick-start-flat-battery.md)
- [ECU subsystem](ecu.md)
- [Handlebar controller subsystem](handlebar-controller.md)
- [CAN bus](can-bus.md)

## 1. Scope

Defines architectural decisions at firmware-image level. Does not
define:

- Specific algorithms (ignition maps, needle-motion profiles) — those
  live in per-subsystem docs or per-experiment protocols.
- Individual API boundaries — those live with the code.
- HIL test rig — separate doc.

## 2. Application partition

**ECU** — three firmware images:

- **Bootloader** (C). Minimal, fast cold-boot, image selection, safe-
  fallback logic.
- **Riding application** (Ada). Engine control, sensor acquisition,
  data logging, CAN, fault handling, diagnostic-CAN responder. No USB.
- **Loader/service application** (C). USB device stack, firmware
  update, bulk log download, extended calibration. Entered from the
  bootloader when requested; not resident during normal operation.

**Handlebar controller** — two firmware images:

- **Bootloader** (C). Same pattern as ECU bootloader plus a small CAN-
  based firmware-update protocol (there is no USB on this node).
- **Application** (Ada). Everything: gauge drive, switchgear, lamps,
  GPS, TPS, CAN, diagnostic responder.

Total: five firmware images across two nodes.

### 2.1 Language rationale

**Ada for engine control and vehicle logic.** Both nodes run Ada
applications for their main runtime, using the **Ravenscar** tasking
profile on GNAT bare-metal. Ravenscar's task model, protected objects
with single-entry semantics, ceiling-priority protocol, and freedom
from dynamic memory allocation are exactly the properties this project
wants for real-time engine control and analysable dashboard behaviour.

Contracts and preconditions (`with Pre => …`, `with Post => …`) on
critical procedures make invariants visible. SPARK-provable subsets
of certain modules — ignition-timing calculation, fault-code
classification, CAN frame encoders — are a plausible future goal;
Ravenscar-compliant Ada is a fine starting point without formal proof.

**C for bootloaders and USB stack.** Bootloaders benefit from minimal
runtime init (no Ada elaboration cost) and use CMSIS/HAL heavily. USB
stacks in Ada exist but are experimental; STMicro's USB device library
and TinyUSB are C, mature, and well-understood. Not worth wrapping.

**No mixed-language linking within one image.** Each firmware image is
single-language. Bootloader → app image transitions are hardware jumps
via reset-vector redirection, not linker-level unification.

## 3. Flash memory layout

### 3.1 ECU (STM32H723ZG, 1 MB internal flash)

| Region | Size | Contents |
|---|---|---|
| Bootloader | 64 KB | C, immutable after production |
| Loader/service app | 128 KB | C, updateable but no A/B |
| Riding app slot A | 384 KB | Ada, updateable, current-slot at boot per config |
| Riding app slot B | 384 KB | Ada, updateable, current-slot at boot per config |
| Config store | 32 KB | LSKV, wear-levelled across ≥ 2 sectors |

Sum: 992 KB. 32 KB reserved for future.

### 3.2 Handlebar controller (STM32G474RE, 512 KB internal flash)

| Region | Size | Contents |
|---|---|---|
| Bootloader | 32 KB | C, includes CAN update protocol |
| App slot A | 224 KB | Ada |
| App slot B | 224 KB | Ada |
| Config store | 16 KB | LSKV, wear-levelled |

Sum: 496 KB. 16 KB reserved.

### 3.3 External storage

- **ECU:** 128 MB SPI NAND (W25N01GV) — log data only, see §7.
- **Handlebar:** 2 MB SPI NOR (W25Q16JV) — odometer + redundant copy +
  fault log, see §8.

## 4. Bootloader design

### 4.1 Responsibilities

- Cold-boot the MCU with minimum init.
- Check the "boot request" magic word in a reserved RAM region.
- Verify the target application slot's integrity.
- Jump to the target application.
- On any integrity failure or three consecutive boot failures on a
  freshly-updated slot: fall back to the other slot (ECU) or to
  loader-mode (handlebar).

### 4.2 Boot flow (ECU)

    Reset
      |
      v
    Bootloader entry (C)
      |
      +-- Read reset-cause register
      +-- Read boot-request magic from noinit RAM
      |
      v
    Which target?
      |
      +-- BOOT_REQ_LOADER --> jump to loader app
      +-- Else read config store: slot_preference (A or B)
      |
      v
    Verify slot header + CRC32
      |
      +-- Fail --> try other slot; if both fail, jump to loader app
      +-- OK
      |
      v
    Set VTOR, jump to slot's reset handler

### 4.3 Cold-boot budget (ECU)

Total budget from stable rail to first spark possible: **100 ms**
(ADR-0004).

| Step | Budget | Notes |
|---|---|---|
| MCU POR + RCC setup | 5 ms | HSE oscillator startup dominates |
| Bootloader entry, VTOR | 1 ms | |
| CRC32 of riding-app image (384 KB) | 5 ms | Hardware CRC unit, DMA-driven |
| Ada elaboration + runtime init | 20 ms | Ravenscar minimal runtime; keep out-of-band init to a minimum |
| Application peripheral init | 20 ms | TIM, ADC, SPI, CAN, GPIO |
| Sensor bring-up (crank Hall armed, coil driver armed) | 10 ms | |
| **Total** | **~61 ms** | 39 ms margin |

If cold-boot exceeds budget in practice: strategies include

- Skip runtime CRC on cold-boot; trust the "last-boot-was-healthy"
  flag from the config store, defer full CRC to a low-priority
  background task.
- Precompile Ada elaboration into a static ROMable form (GNAT
  supports this on constrained targets).

The signature check (ECDSA/Ed25519 verify) is **not** in the cold-boot
path. It runs exactly once, on the first boot after a slot update,
after which the slot is marked "verified" in the config store.

### 4.4 Boot flow (handlebar controller)

Similar, but the fallback on all-slots-fail is to enter a small
CAN-based firmware-update mode inside the bootloader itself. This is
the only way the handlebar can be recovered without opening the
enclosure (no USB).

### 4.5 Bootloader-application interface

Reserved noinit RAM region (defined in linker scripts) contains:

- `boot_request` magic word — set by the application before soft-
  reboot to request a specific target.
- `last_reset_reason` — surfaced from the RCC reset flags for
  application logging.
- `boot_counter` — increments each cold boot; used to detect boot
  loops.

## 5. Loader/service application (ECU only)

Resident in a dedicated flash region, entered from the bootloader on
explicit request. Not entered during normal riding.

Responsibilities:

- USB device stack (CDC-ACM + MSC or vendor-specific for bulk).
- Firmware update protocol: receive new riding-app image, write to
  inactive slot, verify signature, commit slot swap.
- Bulk log download from the SPI NAND log store.
- Extended calibration (long-form config-store updates that don't fit
  the CAN diagnostic message envelope).

Kept small and boring. No RTOS. Bare-metal state machine + USB
interrupts.

Language: C. Built against STMicro's USB device library or TinyUSB.

## 6. Riding application (ECU)

Ada, Ravenscar profile, GNAT bare-metal runtime targeting STM32H7.

### 6.1 Task decomposition

Tasks are declared statically. Priorities follow rate-monotonic
assignment; the ignition path gets the highest priority.

| Task | Priority | Period / trigger | Responsibility |
|---|---|---|---|
| Ignition_Task | Highest | Event (crank ISR via PO) | Compute timing advance, arm coil driver output compare |
| Sensor_Task | High | 10 ms (100 Hz) | Read TPS-from-CAN, wheel-speed timer capture, coil sense window; publish to shared state |
| Slow_Sensor_Task | Medium | 100 ms (10 Hz) | Read MAX31855 EGT/CHT, battery/bus voltages via ADC scan |
| Ambient_Task | Low | 1 s | Read BME280 |
| CAN_Tx_Task | Medium-high | Multi-rate (10 ms, 100 ms, 1 s cycles) | Emit periodic broadcast frames per messages.yaml |
| CAN_Rx_Task | High | Event (CAN Rx ISR via PO) | Dispatch incoming frames to handlers |
| Log_Task | Medium-low | 10 ms | Assemble log records, DMA-write to SPI NAND |
| Fault_Task | Medium | Event | Persist faults to config store, emit CAN fault event |
| Charge_Ctrl_Task | Medium | 100 ms | Arbitrate battery charge/discharge FETs |
| Housekeeping_Task | Lowest | 1 s | Watchdog refresh, config-store maintenance, boot-health flag |

Communication between tasks: protected objects only. No queues with
dynamic sizing, no dynamic dispatch, no allocators. Ravenscar-
compliant throughout.

### 6.2 Interrupt handlers

- Crank Hall input capture (TIM1) — captures timestamp into a protected
  object; posts to Ignition_Task.
- Wheel Hall input capture (TIM2) — captures timestamp; posts to
  Sensor_Task via a different PO.
- Coil driver output compare (TIM8) — self-disarming, fires spark at
  scheduled time.
- CAN Rx (FDCAN1) — posts frame to CAN_Rx_Task.
- SPI DMA complete — posts to Log_Task.
- ADC EOC — posts to Slow_Sensor_Task.
- Window watchdog window-open — refreshed by Housekeeping_Task.

Interrupt priorities align with Ravenscar ceiling-priority protocol.
No interrupts nest above the highest-priority task's ceiling.

### 6.3 Crank sync algorithm

- Circular buffer of last N inter-tooth intervals.
- Running mean of stable-interval subset.
- Missing tooth detected as an interval > 1.5 × mean.
- Sync flag latches on detection; tooth counter reset.
- Loss of sync (three consecutive out-of-range intervals): fault event,
  ignition suppressed until re-sync.

Interpolation between teeth for sub-tooth timing accuracy:

- Given last-tooth timestamp and estimated angular velocity, spark
  event scheduled by loading TIM8 compare register with
  `last_tooth_time + (target_deg - last_tooth_deg) / omega`.
- ω estimate updated per tooth; two-point extrapolation for
  responsiveness under acceleration.

### 6.4 Ignition timing map (phase 1)

Phase 1 uses a **single fixed advance value** from the config store
(per ADR-0002). No RPM axis, no load axis. This is deliberate — see
staged plan.

Phase 4 adds an RPM-indexed 1D map. Phase 6 adds a 2D map with load
axis. All map data lives in the config store, updateable via
diagnostic CAN or the loader app.

### 6.5 Safe map fallback

If the config store is unreadable at boot, or the map integrity CRC
fails, the riding app boots with a **hardcoded safe map**: a
conservative single fixed advance value (e.g. 15° BTDC) compiled into
the image. Vehicle remains rideable, warning lamp illuminated via
handlebar controller.

## 7. Log store (ECU)

### 7.1 Format

Custom binary log, append-only. Written directly to SPI NAND.

Structure per session:

    +-----------------------------+
    | Session header               |  Session ID, wall clock, FW ver,
    |                              |  channel table (name, type, rate)
    +-----------------------------+
    | Record block                 |  Fixed size (e.g. 128 KB, one
    |   Header (session ID, seq)  |  NAND erase block).
    |   Records                    |
    |     Timestamp + channel bits |
    |     + values                 |
    |   ...                        |
    |   Trailer CRC                |
    +-----------------------------+
    | Record block                 |
    | ...                          |

Records are variable-rate — fixed-rate frames are batched with a
common timestamp; event frames (fault, session boundary) carry their
own timestamp.

Multiple sessions are stored back-to-back. Circular overwrite when
full: oldest session evicted first. Sessions marked "protected"
(containing a high-rate window or a flagged fault) are not evicted
until downloaded.

### 7.2 Post-download tooling

Off-device conversion to **MCAP** (an open format with tool support
via `mcap`, `foxglove`, and Python bindings). MCAP is not written on
device because the on-device format is optimised for append-only NAND
writes and known-schema efficiency, not for arbitrary future channel
sets.

The channel table in each session header is the ground truth for
decoding; the converter reads it and produces MCAP with matching
schemas.

### 7.3 SPI NAND handling

- Bad-block table maintained in a spare region.
- Wear leveling implicit: writes advance sequentially across blocks;
  circular overwrite reuses blocks over time.
- ECC: Winbond W25N01GV has on-chip 1-bit ECC per 528-byte page,
  sufficient for our use.

## 8. Config store

Log-structured key-value store on internal MCU flash. Same design on
both nodes.

Keys are enumerated at compile time — no dynamic key sets. Values are
typed: uint8, uint16, uint32, int32, float32, blob (bounded size).

Sector layout:

- 2+ flash sectors per node, wear-levelled.
- Each entry: key, type, length, value, entry CRC.
- New value = append new entry with same key; latest wins on read.
- Sector full or wear count exceeded: compact live values to next
  sector, erase old.

Committed values on both nodes include:

**ECU:**

- Ignition timing (single value in phase 1; extended to map in phase 4+).
- Crank angle sync offset (calibration).
- TPS calibration (idle-position degrees, full-open degrees).
- Thermocouple cold-junction offset per channel.
- Battery divider ratios.
- Vehicle-frame IMU rotation matrix.
- Slot preference (A / B) and per-slot verified flag.
- Boot-healthy counter.
- Fault log (recent entries).

**Handlebar:**

- Gauge zero-position offsets (per stepper).
- Gauge full-scale values (RPM at full-scale tach; m/s at full-scale
  speedo).
- Illumination default level and auto-dim curve parameters.
- Slot preference and verified flags.
- Fault log.
- Odometer counter (mirrored in external W25Q16, with the internal
  copy as a checksum verifier).

## 9. Handlebar application

Ada, Ravenscar. Mirror pattern to the ECU riding app but simpler.

Tasks:

| Task | Priority | Period / trigger | Responsibility |
|---|---|---|---|
| CAN_Rx_Task | High | Event | Dispatch engine-state frames to needle setpoints |
| CAN_Tx_Task | Medium | Multi-rate | Emit periodic user-input, GPS, heartbeat frames |
| Needle_Task | High | 5 ms | Sinusoidal PWM update for both stepper motors |
| Switch_Task | Medium | 10 ms | Debounce switches; broadcast state via CAN_Tx |
| Lamp_Task | Medium | Event / 10 Hz | Turn-signal blink, hazard, warning-lamp state |
| TPS_Task | Medium | 10 ms | I2C read AS5600; broadcast |
| GPS_Task | Low | Event (UART Rx) | Parse NMEA/UBX; broadcast at 5 Hz / 1 Hz |
| ALS_Task | Lowest | 1 s | Ambient light sensor; adjust illumination PWM |
| Housekeeping_Task | Lowest | 1 s | Watchdog, odometer persist, config maintenance |

## 10. Shared modules

Code shared between the ECU riding app and the handlebar app:

- **Protocol** — CAN message struct definitions, encoders, decoders.
  Generated from `protocol/messages.yaml` by `tools/protocol-gen/`.
- **Common types** — engineering-unit types (RPM, temperature, angle,
  m/s), scaled integer helpers, endian conversions.
- **Config store** — LSKV implementation, same code on both nodes.
- **Fault log** — persistent circular buffer format.
- **Ravenscar startup** — shared minimal runtime configuration.

Directory: `firmware/shared/`.

## 11. Codegen

`tools/protocol-gen/` reads `protocol/messages.yaml` and emits:

- **Ada spec + body** per node, defining record types for each message
  and pack/unpack subprograms. Emitted into
  `firmware/shared/protocol/generated-ada/`.
- **C header + source** for the loader app (for USB-side inspection of
  live values). Emitted into `firmware/shared/protocol/generated-c/`.
- **DBC file** for third-party CAN tools. Emitted into
  `tools/dbc/generated.dbc`.

Codegen is invoked by the build system as a prerequisite; generated
files are gitignored.

Language of the codegen tool: Python 3 (broad, portable, no runtime
build burden).

## 12. Build system

Top-level orchestration via **Makefile** at repo root. Sub-builds:

- Ada images (bootloader-adjacent runtimes, riding app, handlebar app)
  built via **Alire** (`alr build`) which invokes gprbuild.
- C images (bootloaders, ECU loader app) built via **cmake** invoking
  the ARM GNU toolchain.

Top-level targets:

    make protocol       # regenerate protocol code
    make ecu            # bootloader + loader + riding app
    make handlebar      # bootloader + app
    make all            # both nodes
    make test           # host-side unit tests
    make hil            # host-side HIL harness build
    make clean          # everything

Individual images buildable via subdirectory targets for iteration.

## 13. Testing strategy

Layered:

**Host-side unit tests** for pure algorithms:

- Crank sync algorithm (fed synthetic tooth interval sequences).
- Ignition timing calculation.
- Fault classifier.
- CAN protocol codegen output (round-trip encode/decode).
- Config store integrity handling (fault injection into flash images).

Ada tests via **AUnit** or **GNATtest**, run on host with a native
compile. C tests via **Unity** or similar. Executed on every commit
via `make test`.

**Target-native tests** for hardware-adjacent modules — small test
executables cross-compiled to the MCU, run on a devkit, results
reported via UART.

**HIL** for full-system testing:

- Trigger-wheel spinner (small DC or stepper motor) driving a real
  crank Hall.
- Dummy coil (or oscilloscope + resistor bank) receiving coil drive.
- Bench PSU and current shunt for power measurement.
- USB-CAN dongle emulating the handlebar controller.
- Log-file playback tool for regression against captured sessions.

Details in a future `docs/architecture/hil.md`.

**On-vehicle** as final validation.

## 14. Firmware update flow

### 14.1 ECU update via USB

1. Host tool sends `diag_request_ecu` service `0xF0` (reboot to
   bootloader) over CAN, or via USB CDC control.
2. Riding app validates request, writes `BOOT_REQ_LOADER` magic word
   to noinit RAM, requests soft reset.
3. Bootloader reads magic word, jumps to loader app.
4. Loader app enumerates USB; host completes DFU-like transaction.
5. Loader app writes image to the inactive riding-app slot.
6. Loader app verifies signature, computes CRC.
7. Loader app updates config store: `slot_preference` = new slot,
   `verified_a`/`verified_b` = true for new slot.
8. Loader app requests soft reset.
9. Bootloader reads slot preference, jumps to new riding app.
10. Riding app runs; sets `boot_healthy` flag after N seconds.
11. If step 10 fails (crash before flag set): bootloader detects
    unhealthy boot on next cold-boot, reverts to old slot.

### 14.2 Handlebar update via CAN

1. Host tool sends `diag_request_handlebar` service `0xF0` over CAN.
2. Handlebar app writes `BOOT_REQ_UPDATE_CAN` magic word, resets.
3. Handlebar bootloader enters CAN-update mode.
4. Host tool sends image in fixed-size chunks over ISO-TP-framed CAN.
5. Handlebar bootloader writes to inactive slot, verifies CRC + sig.
6. Slot preference updated in config store.
7. Reset into new application.

### 14.3 Update via ECU-as-CAN-bridge

For convenience, the host tool can update the handlebar via the ECU's
USB service connector: the loader app relays ISO-TP chunks to the
handlebar bootloader over CAN. Same protocol on the handlebar side;
different transport on the host side.

## 15. Directory layout

    firmware/
      shared/
        protocol/
          generated-ada/      # from tools/protocol-gen/
          generated-c/
        common-types/
          src/                # Ada
        config-store/
          src/                # Ada
        fault-log/
          src/                # Ada
      ecu-bootloader/         # C
        src/
        include/
        linker/
        CMakeLists.txt
      ecu-loader/             # C, USB service app
        src/
        include/
        linker/
        CMakeLists.txt
      ecu-riding-app/         # Ada
        src/
        gnat/
        ecu_riding.gpr
        alire.toml
      handlebar-bootloader/   # C
        ...
      handlebar-app/          # Ada
        src/
        gnat/
        handlebar.gpr
        alire.toml
    tools/
      protocol-gen/           # Python
      loader/                 # Host-side USB and CAN client
      log-analysis/           # Python, MCAP conversion
      dbc/                    # generated.dbc

## 16. Open questions

- **Signature scheme** — ECDSA-P256 vs Ed25519. Ed25519 verify is
  faster and simpler; ECDSA has broader tooling. Ed25519 preferred
  but not decided.
- **USB stack choice** — STMicro USBD library vs TinyUSB. TinyUSB is
  more portable and better maintained upstream; STMicro's is
  vendor-supported. TinyUSB tentatively preferred.
- **Ada tasking profile** — Ravenscar vs Jorvik (Ravenscar++).
  Jorvik permits multiple entries and other conveniences at some
  analysability cost. Ravenscar preferred for the ECU; Jorvik
  potentially fine for the handlebar. Confirm during first-code
  bring-up.
- **Log format vs MCAP-on-device** — custom binary appended, converted
  offline (chosen), vs writing MCAP directly on device (rejected for
  phase 1; MCAP's schema-per-file model is not ideal for NAND).
- **SPARK on which modules** — no proof effort planned for phase 1,
  but writing critical modules (ignition timing, config store CRC,
  fault classifier) in SPARK-compatible subset costs little and
  enables later formal proof. Discretionary.

## 17. Related

- [ECU subsystem](ecu.md)
- [Handlebar controller](handlebar-controller.md)
- [CAN bus](can-bus.md)
- HIL — to be written
- [Measurement plan](../measurement-plan.md)
