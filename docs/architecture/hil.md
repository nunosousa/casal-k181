# HIL bench architecture

Hardware-in-the-loop bench for validating the ECU (and handlebar
controller) firmware and hardware before first engine start.

Phase 2 of the [staged plan](../project/staged-plan.md) is not
complete until the HIL bench has validated the full ignition path
end-to-end: trigger acquisition, timing calculation, coil driver
output, cold-boot budget compliance, and fault handling. Phase 3
(first engine start) does not begin until phase 2 is closed.

Constrained by:

- [ADR-0004: Kick-start with flat battery](../project/decisions/0004-kick-start-flat-battery.md)
  — cold-boot time is a hard requirement and must be verified on the
  bench, not on the engine.
- [ECU subsystem](ecu.md)
- [Firmware architecture](firmware.md)
- [Measurement plan](../measurement-plan.md) — the HIL rig is also
  the platform for calibrating the ignition-timing measurement chain.

Scope note: this is a hobby HIL rig, not a certified test bench.
The aim is to catch class-of-defect problems early — not to
demonstrate qualification-level coverage.

## 1. Test objectives

The HIL bench must be able to answer these questions independent of
the engine:

1. **Does the ECU cold-boot within 100 ms?** (ADR-0004 budget.)
2. **Does the coil driver fire the coil at the commanded crank
   angle**, to within the timing accuracy documented in [measurement
   plan §9.1](../measurement-plan.md#91-sensor-level-uncertainties-targets)
   (± 0.7° end-to-end)?
3. **Does dwell match the commanded value** across the operational
   Vbat range (9-16 V)?
4. **Does the crank-sync algorithm** find and hold the missing-tooth
   sync from cold start, across the RPM range 200-8000?
5. **Does the sensor chain** — Hall, thermocouple, TPS, ambient,
   battery — broadcast correctly onto CAN at the specified rates?
6. **Does the firmware update flow** work end-to-end, including
   boot-healthy fallback on a deliberately-corrupted new slot?
7. **Do injected faults** propagate to the fault log, to CAN fault
   events, and to safe-timing fallback where relevant?
8. **Can the ECU be kick-started** — i.e. does it cold-boot from a
   supercap-only power profile with the trigger wheel spinning at
   kick speed?

## 2. Rig architecture

    +------------------+           +---------------------+
    | Host PC          |<---USB--->| USB-CAN dongle      |
    | Python test      |           +---------+-----------+
    | framework        |                     |
    |                  |                   CAN bus (500 kbit/s,
    |                  |                    120 Ω termination
    |                  |                    each end)
    |                  |<---USB--->| HIL controller MCU  |
    |                  |           | (Teensy or Pico)    |
    |                  |           +----+----------------+
    |                  |                |  |  |
    |                  |                |  |  +--> Thermocouple sim
    |                  |                |  +----> Wheel speed sig gen
    |                  |                +-------> BLDC ESC command
    |                  |                              |
    |                  |                              v
    |                  |                       Trigger motor +
    |                  |                       36-1 wheel + Hall
    |                  |                       + optical reference
    |                  |
    |                  |<---USB--->| ECU under test              |
    |                  |           |   (in service mode)          |
    |                  +---LAN-----|                              |
    |                              |     Coil drive out --> Dummy |
    |                              |                        load  |
    |                              +----------+-------------------+
    |                                         |
    +--------LAN or USB----------------> Scope +
                                             (4-ch, ≥ 20 MHz)
                                         + differential probe

- **Host PC** runs the test framework. Talks to the ECU on USB (for
  service and log download), to the CAN bus via USB-CAN dongle (for
  message inspection and diagnostic requests), to the HIL controller
  for scenario stimulus, and to the scope for waveform capture.
- **HIL controller** is a small MCU (Teensy 4.x or Raspberry Pi Pico
  class) that closes the loop between the host and the rig's stimulus
  outputs. Runs a small firmware exposing a USB-serial command
  protocol.
- **ECU under test** sits on the bench with its real vehicle-harness
  connector routed to a breakout board that fans out to bench signals.

## 3. Rig components

### 3.1 Crank trigger simulator

- **Motor:** small brushless DC motor with a hobby-grade ESC (Racer or
  drone class, ~1000 kV). Commanded via PWM/DShot from the HIL
  controller.
- **Trigger wheel:** a laser-cut or 3D-printed prototype of the same
  36-1 wheel that will fit the flywheel. First rig version can be
  larger for handling; final wheel identical to vehicle.
- **Hall sensor:** identical part to the vehicle install (Honeywell
  SS411A or chosen equivalent), on a rigid bracket, in the same
  physical relationship to the wheel it will have on the engine.
- **Optical reference:** slotted disc or reflective mark on the wheel,
  aligned with the "TDC" tooth position (or a known reference tooth),
  sensed by a photointerrupter/photoreflector. Provides an independent
  ground-truth signal for timing verification on the scope.

**RPM range required:** 200 (below idle for warm-boot testing) to
8000 (above operational envelope). BLDC + ESC easily covers this.

**Transient profiles the rig must reproduce:**

- Kick-start: 0 → 500 RPM in ~200 ms, decays if engine doesn't
  catch.
- Idle: 1500 RPM ± 100 RPM.
- Acceleration ramp: 2000 → 7000 RPM in ~3 s.
- Fast decel: 7000 → 2000 RPM in ~1 s.
- Steady-state at settable RPM within ±20 RPM.

### 3.2 Coil load

Two configurations:

- **Dummy load** (primary bring-up): inductor sized to match the
  chosen ignition coil's primary inductance (typically 3-6 mH),
  in series with a low-value sense resistor. IGBT clamp voltage still
  develops on the drain during fly-back. No high-voltage secondary,
  no EMI, no spark. Safe for extensive bench work.

- **Real coil in a grounded spark box** (final validation): actual
  ignition coil with HT secondary connected to a sparkplug mounted
  inside a grounded metal box with viewing window. Realistic load
  and spark event, contained EMI, no fire hazard. Introduced only
  after dummy-load testing passes.

Sense: primary voltage on the drain (differential probe) and primary
current via low-side shunt into a current-shunt monitor IC. Both go to
the scope.

### 3.3 Sensor emulation board

Custom small PCB (or perfboard for phase 1) driven by the HIL
controller:

- **Thermocouple output** (EGT, CHT): two channels of a low-voltage
  precision DAC scaled to 0-50 mV, representing K-type outputs. Cold-
  junction offset added digitally by the host. Alternative: real
  thermocouples in temperature-controlled water baths — more
  realistic, less flexible.
- **TPS**: a physical AS5600 on the emulator board with a small
  servo or manual knob for angle. The ECU's Vehicle-Bus receives TPS
  over CAN from the handlebar or a stand-in.
- **Wheel speed**: HIL controller PWM output driving a level-shifted
  logic signal into the ECU's wheel-Hall input pin, generating a
  square wave at whatever frequency corresponds to the target vehicle
  speed.
- **Ambient (BME280)**: real BME280 on the emulator board. Sees
  ambient bench conditions. Not typically stimulated in phase 1.
- **Battery / bus voltage simulation**: a programmable bench PSU feeds
  the ECU's power input. See §3.6.

### 3.4 CAN traffic

- **USB-CAN dongle** — CANable or Peak PCAN-USB. Talks to the CAN
  bus at 500 kbit/s.
- Represents the handlebar controller during ECU bring-up, generating
  synthetic user-input frames per `messages.yaml`. Later replaced by
  the real handlebar controller when that node is ready.
- Terminated at 120 Ω on the dongle side; ECU has its own 120 Ω on the
  other end.
- Python `python-can` bindings on the host drive it.

### 3.5 USB service

The ECU's USB service connector plugs into the host directly. Standard
USB-CDC/MSC device enumeration; the loader app's protocol is exercised
via the same tool the vehicle will use.

### 3.6 Programmable power supply

- **Requirement:** 6-16 V DC output, 5 A capable, programmable voltage
  and current, current-reading readout.
- Simulates: normal battery voltage, weak battery, cranking dips,
  bus overvoltage.
- Kick-start simulation: PSU commanded through a voltage-vs-time
  profile that mimics the supercap charging curve from stator input.
  This is the specific ADR-0004 cold-boot test.
- Candidates: Rigol DP832 or DP821 (~€400) if not already owned; a
  cheap bench PSU (~€100) is sufficient for phase-1 bring-up and can
  be upgraded later.

### 3.7 Scope

Existing lab equipment assumed. Requirements:

- 4 channels.
- ≥ 20 MHz bandwidth (coil driver events have ~100 kHz spectral
  content; 20 MHz gives comfortable margin).
- Digital storage with sample memory ≥ 1 M points per channel.
- USB or LAN remote control (for automated capture from the test
  framework). Optional but strongly preferred; manual capture works
  too.

Channels during timing tests:

- CH1: Optical reference edge from the trigger wheel.
- CH2: Coil driver gate signal (from the ECU's IGBT gate).
- CH3: Coil primary voltage (differential probe on IGBT drain).
- CH4: Coil primary current (from shunt monitor).

## 4. HIL controller firmware

Small firmware on the Teensy/Pico. Written in C (Arduino-style is
fine; no need for the vehicle's Ada + Ravenscar apparatus here).

Responsibilities:

- USB-CDC command protocol from the host. Commands include:
  `set_rpm <rpm>`, `ramp_rpm <from> <to> <duration_ms>`,
  `kick_profile`, `stop`, `set_thermocouple <ch> <mv>`,
  `set_wheel_speed <hz>`, `fault_inject <type>`.
- BLDC ESC command output.
- PWM/square-wave generation for wheel-speed input.
- SPI/I2C to the emulator board's DACs.
- Digital I/O for fault-injection (e.g. cutting a sensor line via
  a solid-state relay).

Kept boring. Bare-metal or Arduino-runtime, no tasking. The host
drives; the HIL controller executes.

## 5. Host-side test framework

**Language:** Python 3 (broad, quick to script, CAN and USB libraries
available).

**Structure:** `tools/hil/` in the repo.

    tools/hil/
      framework/            # shared helpers (CAN, USB, scope, controller)
      tests/                # per-test-case scripts
        test_cold_boot.py
        test_timing_accuracy.py
        test_dwell.py
        test_sync_recovery.py
        test_can_broadcast.py
        test_fw_update.py
        test_fault_injection.py
        test_kick_start_profile.py
      configs/              # rig configuration (device IDs, channels)
      results/              # gitignored; per-run test output

**Dependencies:** `python-can`, `pyusb`, `pyvisa` (scope), `pyserial`
(HIL controller), `pytest` for orchestration.

**Test execution:**

    make hil                       # build test infrastructure
    pytest tools/hil/tests/        # run full suite
    pytest -k "timing_accuracy"    # run one test

Each test emits pass/fail + measurement values in a JSON result file
committed to `results/YYYY-MM-DD-<sha>/`.

Regression-style: full suite must pass before any firmware release
candidate is promoted.

## 6. Test cases (phase 1 target set)

### 6.1 Power and boot

- `test_rails_sequence` — bench PSU commanded to nominal 12 V; scope
  verifies 5 V and 3.3 V rails appear in order.
- `test_cold_boot_time` — reset the ECU; measure time from POR to
  first CAN heartbeat. Must be ≤ 100 ms. Repeated 10× for statistics.
- `test_kick_start_profile` — bench PSU driven through a supercap-
  charge profile (rising from 0 to 12 V over ~200 ms while HIL
  controller ramps trigger wheel from 0 to 500 RPM). Verify ECU
  cold-boots and fires spark within the first 5 revolutions.
- `test_brownout_recovery` — dip PSU to 6 V briefly; verify ECU
  either sustains operation or performs a controlled reboot with
  fault log entry.

### 6.2 Trigger and timing

- `test_sync_acquisition` — spin the wheel at 500 RPM; verify sync
  acquired within 2 revolutions.
- `test_sync_loss_recovery` — inject a Hall edge dropout for 500 ms;
  verify sync-loss fault and recovery.
- `test_timing_accuracy_steady` — spin at 3000 RPM steady, command
  20° BTDC advance; scope captures optical reference and gate signal;
  measured advance must be within ± 0.7° of commanded, across 100
  consecutive events.
- `test_timing_across_rpm` — repeat previous at 500, 1000, 3000,
  6000, 8000 RPM. Timing accuracy must hold at all points.
- `test_timing_under_transient` — 2000 → 6000 RPM ramp in 3 s;
  verify sync held throughout and timing follows commanded map.

### 6.3 Coil driver

- `test_dwell_accuracy_vbat` — at 9, 12, 14, 16 V input, command
  2 ms dwell; scope measures actual dwell (primary current fall-off
  minus gate rising edge). Must be within ± 100 µs.
- `test_open_coil_detection` — disconnect coil primary; verify
  fault code `coil_open` appears on CAN within 3 spark cycles.
- `test_shorted_coil_detection` — parallel a low-value resistor
  across primary; verify fault code within 3 cycles.
- `test_primary_current_profile` — capture primary current during
  dwell; verify it matches the expected inductor-charging curve to
  within measurement noise.

### 6.4 CAN broadcast

- `test_all_periodic_present` — record 10 s of CAN traffic; verify
  every periodic message defined in `messages.yaml` appears at its
  specified rate ± 5 %.
- `test_signal_roundtrip` — for each sensor, inject a known value
  via the emulator; verify the corresponding CAN signal reports it
  correctly (after scaling).
- `test_diag_request_response` — send each diagnostic service ID;
  verify well-formed response with correct payload.

### 6.5 Firmware update

- `test_update_happy_path` — build a trivially-modified riding-app
  image; upload via USB loader; verify slot swap; verify
  boot-healthy flag set after N seconds; reboot; verify new
  image running.
- `test_update_corrupt_fallback` — upload a deliberately-corrupted
  image; verify boot fails, bootloader falls back to previous slot
  after 3 unhealthy boots.
- `test_config_persistence` — write a config value; power cycle;
  verify value persists.
- `test_config_corruption_recovery` — corrupt a sector in the
  config store on-chip flash; reboot; verify safe defaults loaded,
  fault logged.

### 6.6 Fault injection

- `test_cut_crank_signal_while_running` — kill Hall input while
  engine "running" (wheel spinning + trigger cranked). Verify
  `crank_sensor_fault` reported.
- `test_can_bus_off` — force bus into error state; verify
  peripheral recovers and rejoins.
- `test_overtemp_ecu` — heat gun on MCU (or firmware-injected
  false reading); verify fault and log.
- `test_battery_low_shutdown` — ramp Vbat down to brownout; verify
  clean shutdown, config-store final flush, no NAND corruption.

## 7. Safety

- **Bench PSU on GFCI-protected mains, always.**
- **Coil driver testing with dummy load** by default. Real coil +
  spark plug only in a grounded box, only when required.
- **BLDC motor guarded** — a mechanical guard around the spinning
  trigger wheel and motor shaft to prevent contact.
- **Emergency stop button** wired to cut ESC power. HIL controller
  monitors and cuts if watchdog trips.
- **Fume extraction not required** because there's no combustion on
  the bench.
- **EMI considerations** — coil-driver testing generates significant
  di/dt. Keep scope probes short; ground scope and PSU to the same
  reference; avoid ground loops.

## 8. Handlebar controller HIL variant

Small separate bench, simpler:

- Two real stepper motors + gauges (or LED indicator strips for phase
  1 while dial faces are sourced).
- Warning-lamp LEDs on a small panel.
- Physical switch panel (indicator L/R, hazard, horn, headlight, kill,
  mode buttons).
- **Incandescent-load test set** — real 12 V incandescent bulbs
  (headlight, tail/brake, indicator) mounted on the bench, or
  resistive equivalents sized to match the steady-state and cold-
  inrush characteristics per
  [ADR-0005](../project/decisions/0005-retain-incandescent-exterior-lamps.md).
  Exercises the MOSFET / relay drive stages under realistic load,
  including inrush.
- Real AS5600 on a knobbed shaft.
- Ambient light sensor exposed to bench light.
- USB-CAN dongle simulating the ECU (or the real ECU via the vehicle
  CAN link).
- GPS: either the real module with a small active antenna and sky
  view via a window, or a UART GPS simulator on the HIL controller.

Test cases mirror the ECU set but focused on the handlebar's
responsibilities: gauge accuracy (commanded vs. observed needle
angle), switch debounce, turn-signal timing, GPS parsing correctness,
lamp control via CAN commands, **inrush-current handling on cold-lamp
switch-on** (scope-captured current profile against MOSFET/relay
datasheet safe-operating-area).

## 9. Bring-up sequence

Recommended order of standing-up the bench:

1. **Bare-PCB power-on** of the ECU on a bench PSU; verify rails.
2. **HIL controller firmware** on the Teensy/Pico. Manual command
   from a serial terminal to verify RPM output and thermocouple DAC.
3. **BLDC motor and trigger wheel** spinning under host command;
   verify Hall signal on the scope at expected frequencies.
4. **Optical reference** aligned and verified against tooth counts.
5. **Coil driver dummy load** wired up.
6. **First ECU firmware** (bootloader + minimal riding app) loaded via
   SWD.
7. **Sync acquisition test** — spin the wheel, verify ECU firmware
   detects the missing tooth and reports sync via UART or CAN.
8. **First timed spark event** — command a fixed advance, verify on
   scope against optical reference. This is a milestone.
9. **Automated test suite** wired up incrementally as each subsystem
   comes online.

## 10. Cost estimate

Rough one-off costs assuming shop already has scope + soldering
equipment:

| Item | Cost (€) |
|---|---|
| BLDC motor + ESC + prop shaft/adapter | 40 |
| 36-1 trigger wheel (prototype) + Hall sensor + bracket | 20 |
| Optical reference (photointerrupter + slot disc) | 15 |
| Coil dummy load (inductor + resistor + mount) | 20 |
| Sensor emulator board parts + PCB | 40 |
| HIL controller (Teensy 4.x or Pi Pico) | 20 |
| USB-CAN dongle (CANable or CANable Pro) | 40 |
| Bench PSU (if not owned; programmable) | 200 |
| Frame / base plate / connectors / wiring | 40 |
| **Total (no PSU)** | **~235** |
| **Total (with PSU)** | **~435** |

Handlebar HIL variant: additional ~€80 for stepper drivers, panel,
GPS simulator or module.

## 11. Open questions

- **BLDC vs. stepper for trigger motor.** BLDC preferred for
  transient dynamics; stepper considered for very-low-RPM precision.
  Decision: start with BLDC, add stepper option if needed for cold-
  start testing at < 200 RPM.
- **Scope automation.** Manual capture works; automated capture via
  pyvisa is much nicer for the timing-accuracy tests which require
  100 samples per RPM point. Depends on scope model.
- **Sensor-emulator PCB fabrication.** Perfboard for phase 1, PCB
  spin if the emulator becomes long-lived.
- **Coil dummy load specification.** Depends on the chosen coil,
  which is TBD in [ecu.md](ecu.md). Provisional: 5 mH inductor rated
  for 10 A pulses.

## 12. Related

- [Staged plan](../project/staged-plan.md)
- [ADR-0004: Kick-start with flat battery](../project/decisions/0004-kick-start-flat-battery.md)
- [ECU subsystem](ecu.md)
- [Firmware architecture](firmware.md)
- [Measurement plan](../measurement-plan.md)
