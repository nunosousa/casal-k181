# CAN bus architecture

Protocol design for the vehicle CAN bus connecting the ECU and the
handlebar controller. This document is the human-readable rationale;
the machine-readable canonical definition lives in
[`protocol/messages.yaml`](../../protocol/messages.yaml).

Constrained by:

- [ADR-0001: Two-node CAN topology](../project/decisions/0001-two-node-can-topology.md)
- [System architecture](system.md)
- [ECU subsystem](ecu.md)

## 1. Scope

Defines:

- Physical-layer parameters.
- Identifier allocation scheme.
- Message categories and cycle times.
- Bus-load budget.
- Multi-frame handling.
- Time-sync approach.
- Error and heartbeat behaviour.
- Diagnostic/configuration protocol layer.
- Extension guidelines.

Does not define:

- Individual signal encodings — those live in `messages.yaml`.
- Application-layer semantics — those live in the subsystem docs
  (ecu.md, handlebar-controller.md).

## 2. Physical layer

- Standard CAN 2.0B (classic), operated on STM32 FDCAN peripherals in
  classic mode.
- **Bit rate: 500 kbit/s.**
- **Identifier width: 11-bit.** Sufficient for a 2-node system and
  simpler than 29-bit. 29-bit is not needed until we add a third node or
  adopt J1939.
- Twisted pair, 120 Ω termination at each end of the bus (both nodes
  are physical bus ends).
- Nominal common-mode range and drive per ISO 11898-2.
- Transceivers: TCAN1042 (ECU side) or SN65HVD230 class, ESD-protected.
- Bus stub length ≤ 30 cm at each node.

## 3. Identifier allocation scheme

CAN arbitration is dominance-of-zero — a lower ID transmits ahead of a
higher ID when both nodes contend. IDs are allocated so that priority is
implicit in the numeric range.

| Range | Class | Producer | Typical rate |
|---|---|---|---|
| 0x000–0x03F | Emergency / critical events | Any | Event |
| 0x040–0x0FF | Reserved (future emergency) | — | — |
| 0x100–0x1FF | ECU fast periodic | ECU | 100 Hz |
| 0x200–0x2FF | ECU medium/slow periodic | ECU | 1–10 Hz |
| 0x300–0x3FF | Handlebar controller fast periodic | Handlebar | 100 Hz |
| 0x400–0x4FF | Handlebar controller medium/slow periodic | Handlebar | 1–10 Hz |
| 0x500–0x6FF | Reserved (future third node, expansion) | — | — |
| 0x700–0x77F | Diagnostic request/response | Any | Event |
| 0x780–0x7FF | Bootloader / firmware update | Any | Event |

Emergency IDs get numerically-lowest values, ensuring they win
arbitration against any periodic traffic.

Rationale for producer-partitioned ranges: makes trace-reading trivial
(any 0x1xx frame is from the ECU), avoids the trap of two nodes
competing for the same ID range, keeps room for future producers.

## 4. Message categories

### 4.1 Emergency (event-driven, 0x000–0x03F)

Fired by either node when a fault requires the other node's immediate
attention.

- `ecu_emergency_stop` — ECU shutting down engine due to critical fault.
- `ecu_fault_event` — new entry added to the ECU fault log.
- `handlebar_emergency_stop` — rider or handlebar controller requests
  engine stop.
- `handlebar_fault_event` — new entry added to the handlebar fault log.
- `session_event` — start, stop, sleep, wake transitions.

Consumers must act on emergency frames within one bus cycle
(~1 ms worst case at 500 kbit/s with maximum non-emergency queue depth).

### 4.2 ECU fast periodic (100 Hz, 0x100–0x1FF)

Frames the handlebar needs at gauge-refresh rate.

- `engine_state_fast` — RPM, commanded ignition advance, coil dwell
  actual, engine-running flag.
- `vehicle_state_fast` — wheel speed, distance-since-boot, movement
  flag.
- `throttle_state` — TPS echoed by the ECU as it observed the value
  (handlebar-produced TPS mirrored to make the ECU's view visible for
  logging and cross-check).

Handlebar consumes `engine_state_fast` and `vehicle_state_fast` for the
tachometer and speedometer needles.

### 4.3 ECU medium periodic (10 Hz, 0x200–0x22F)

- `thermal_state` — EGT, CHT, MCU internal temperature.
- `power_state` — Vbat, Vbus, charge current.
- `ignition_diag` — spark energy proxy, misfire counters, dwell error.

### 4.4 ECU slow periodic (1 Hz, 0x230–0x2FF)

- `ambient_state` — ambient temperature, pressure, relative humidity.
- `ecu_heartbeat` — firmware version, uptime, fault-summary bits,
  running-hours counter.

### 4.5 Handlebar fast periodic (100 Hz, 0x300–0x3FF)

- `user_input_fast` — TPS raw and filtered.
- `handlebar_switches` — indicator, horn, headlight, mode-button state
  bits.

### 4.6 Handlebar medium periodic (5 Hz, 0x400–0x41F)

- `gps_position` — latitude and longitude as int32 at 1e-7 degrees.
- `gps_speed_alt` — GPS-derived speed, altitude, HDOP, satellite count.

### 4.7 Handlebar slow periodic (1 Hz, 0x420–0x4FF)

- `gps_fix_state` — fix quality, UTC time, geoidal separation.
- `handlebar_heartbeat` — firmware version, uptime, fault-summary bits.

### 4.8 Diagnostic (event, 0x700–0x77F)

Simple request/response protocol for calibration, log queries and
config uploads. Not UDS — this is a hobby project. See §9.

### 4.9 Bootloader (event, 0x780–0x7FF)

Handled by bootloader firmware only. Application firmware ignores
these IDs.

## 5. Bus loading estimate

Frame size for classic CAN with 8-byte payload: ~135 bits including
stuffing. At 500 kbit/s that's ~270 µs per frame.

| Class | Frames/s | Bus time |
|---|---|---|
| ECU fast × 3 messages × 100 Hz | 300 | 81 ms/s |
| ECU medium × 3 × 10 Hz | 30 | 8 ms/s |
| ECU slow × 2 × 1 Hz | 2 | 0.5 ms/s |
| Handlebar fast × 2 × 100 Hz | 200 | 54 ms/s |
| Handlebar medium × 2 × 5 Hz | 10 | 3 ms/s |
| Handlebar slow × 2 × 1 Hz | 2 | 0.5 ms/s |
| Diagnostic / events (peak) | 20 | 5 ms/s |
| **Total** | ~565 | **~152 ms/s ≈ 15 %** |

15 % steady-state utilisation. Comfortable — leaves headroom for
transient bursts of event frames and for future expansion. Worst-case
frame latency for a medium-priority message at 15 % load with priority
ordering is well under 5 ms.

## 6. Multi-frame handling

For phase 1, all messages fit in a single 8-byte CAN frame. Any future
message requiring more than 8 bytes uses **ISO-TP (ISO 15765-2)**
segmentation. Reserved IDs for ISO-TP:

- Handlebar → ECU multi-frame: 0x780
- ECU → Handlebar multi-frame: 0x781

These are only exercised by the diagnostic protocol (e.g. downloading
a chunk of the fault log). Not used in periodic traffic.

## 7. Time synchronisation

The ECU is the time master. Both nodes maintain a monotonic
microsecond-resolution timer in local firmware. Every 1 s, the ECU
broadcasts its current session time in a diagnostic frame; the
handlebar controller tracks the offset between its local clock and the
ECU's.

For log analysis, the ECU's clock is authoritative. Handlebar-produced
frames carry a local-timer field that the ECU maps to session time via
the tracked offset.

Precision required: ~1 ms. Well within reach of the periodic 1 Hz
sync given the bus's bounded latency.

Wall-clock time (UTC) comes from GPS via the handlebar heartbeat once a
fix is acquired, and is used only to stamp session logs at
start/stop — not for real-time control.

## 8. Error handling and heartbeat

### 8.1 Heartbeats

Each node broadcasts a heartbeat at 1 Hz containing at minimum:

- Firmware version (major.minor.patch, 3 bytes).
- Uptime seconds (uint32 rolls over at ~136 years).
- Fault-summary bitfield.

Consumer behaviour when heartbeat is missing:

- **Handlebar detects missing ECU heartbeat** (3 consecutive missed →
  3 s timeout): freeze gauge needles at last-known values, illuminate a
  general warning lamp, log a fault, keep displaying gauges as "last
  known + timeout indicator." Do not blank the display.

- **ECU detects missing handlebar heartbeat**: log a fault, keep
  running the engine (the ECU does not depend on the handlebar for any
  control function), continue broadcasting periodic frames so the
  handlebar can resynchronise when it recovers.

### 8.2 Bus errors

Standard CAN error-frame handling by the transceivers and FDCAN
peripheral. Firmware monitors bus-off state; on bus-off, waits for the
peripheral's built-in recovery (128×11 recessive bits) then rejoins.
Bus-off event logged.

### 8.3 Signal plausibility

Consumers apply plausibility checks on received signals (range, rate-
of-change). Implausible values logged as a bus-integrity fault but do
not automatically shut down the producer node.

## 9. Diagnostic / configuration protocol

Lightweight request/response over reserved IDs 0x700-0x77F. Two IDs per
node pair for symmetry:

- 0x700: request → ECU
- 0x701: response from ECU
- 0x702: request → handlebar controller
- 0x703: response from handlebar controller

Each request frame's first byte is a service ID; remaining bytes are
service-specific. Long payloads use ISO-TP over 0x780/0x781.

Service IDs (initial set, extensible):

| Service | Description |
|---|---|
| 0x01 | Read fault log entry N |
| 0x02 | Clear fault log |
| 0x03 | Read config parameter by index |
| 0x04 | Write config parameter (guarded; requires unlock) |
| 0x05 | Unlock config-write session |
| 0x06 | Read live signal (bypass periodic broadcast) |
| 0x10 | Read firmware version + build hash |
| 0x20 | Reset to safe-timing map |
| 0xF0 | Reboot to bootloader |

Config-writes are session-guarded to prevent accidental overwrites from
a stray tool. Session unlocked with a passphrase, expires after 60 s of
inactivity.

## 10. Boot and node discovery

There is no explicit "node discovery" — the bus is fixed at two nodes
and each knows the other's ID ranges statically. However:

- On boot, each node waits ≤ 200 ms observing bus activity before
  transmitting anything. Prevents boot-race collisions.
- First message from each node is its heartbeat, immediately.
- If a node observes the other's heartbeat at boot, it logs "peer alive
  at boot" for later correlation.
- If a node observes no traffic within 1 s, it starts periodic
  transmission anyway (isolated operation).

## 11. Version and compatibility

- The protocol has a single version integer, recorded in `messages.yaml`
  as `version` and in each firmware image at build time.
- Nodes running mismatched protocol versions log the mismatch and
  continue operating with any messages they both understand. Older
  fields are always preserved when adding new signals.
- Breaking changes bump the version and require both firmware images
  to be updated together. This is a hobby project — we do not attempt
  to preserve multi-version compatibility, only detection.

## 12. Extension guidelines

When adding new signals or messages:

- Prefer adding a new signal to an existing periodic message before
  creating a new message ID.
- Preserve existing signal positions (start_bit, length_bits). Never
  reorder; append instead.
- Bump the `version` in `messages.yaml`.
- Update this document's message tables (§4).
- Regenerate protocol headers for both firmware images.
- Note the change in a decision record if it changes ownership of any
  signal.

## 13. Related

- [`protocol/messages.yaml`](../../protocol/messages.yaml) — canonical
  definition, used by codegen for both firmware images.
- [System architecture](system.md)
- [ECU subsystem](ecu.md)
- Handlebar controller — to be written
