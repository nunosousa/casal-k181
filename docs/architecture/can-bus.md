# CAN bus architecture and protocol specification

Protocol version 2 for ECU, speedometer, tachometer and warning-cluster
controllers, per [ADR-0012](../project/decisions/0012-distributed-dashboard-can-nodes.md).
The [CAN YAML](../../protocol/messages.yaml) owns wire encodings, node
identities and declared periods. This document owns transport behaviour;
the [ICD](interfaces.md) tracks unresolved acceptance details. No compatibility
with the retired version-1 handlebar node is claimed.

## 1. Physical layer and topology

- Classic CAN using 11-bit identifiers at 500 kbit/s.
- One transceiver per controller; suitable automotive/vehicle EMC protection.
- Linear twisted-pair trunk with nominal 120-ohm termination at **exactly
  two physical ends**, regardless of the four-node count.
- Short instrument stubs, target <=30 cm; final layout, total length,
  termination locations and signal integrity verified at harness release.
- Four node addresses: ECU 0x01, warning cluster 0x02, speedometer 0x03,
  tachometer 0x04. These logical addresses are not CAN arbitration IDs.
- Service tools are external participants, not additional permanent vehicle
  controllers. A service connection must not add another termination.

## 2. Identifier allocation

Lower identifiers win arbitration. One defined producer owns each vehicle
message; `any` on diagnostics means one active external service master,
not permission for competing simultaneous writers.

| Range | Owner / class |
|---|---|
| 0x000-0x03F | Emergency, node fault and session events |
| 0x040-0x0FF | Reserved |
| 0x100-0x1FF | ECU fast telemetry |
| 0x200-0x2FF | ECU medium/slow telemetry and heartbeat |
| 0x300-0x3FF | Warning-cluster rider inputs |
| 0x400-0x4FF | Warning-cluster GPS, heartbeat and brightness |
| 0x500-0x5FF | Speedometer heartbeat / future telemetry |
| 0x600-0x6FF | Tachometer heartbeat / future telemetry |
| 0x700-0x77F | Node-addressed single-frame diagnostics |
| 0x780-0x787 | Target-specific ISO-TP request/response transport |
| 0x788-0x7FF | Reserved |

## 3. Message ownership and semantics

- ECU `engine_state_fast` at 100 Hz feeds tachometer and warning cluster;
  `vehicle_state_fast` at 100 Hz feeds speedometer and warning cluster.
- ECU `throttle_state` echoes the TPS it consumed. Thermal, power,
  ignition diagnostics and ambient messages feed the warning cluster.
- Warning cluster produces `user_input_fast` and `handlebar_switches` at
  100 Hz. The latter name identifies physical switchgear, not a separate
  handlebar controller. Indicator/hazard bits are steady rider intent;
  ECU generates exterior blink phase, cluster generates local repeaters.
- GPS position/speed at 5 Hz and fix/UTC at 1 Hz originate at the cluster.
- Cluster `dashboard_brightness` at 10 Hz feeds both gauges; each applies
  a local curve and uses usable local brightness on stale/invalid input.
- Each node emits its own heartbeat at 1 Hz and its own fault events.
  ECU and cluster consume gauge heartbeats; gauges also consume ECU and
  cluster heartbeats. Cluster loss must not blank gauge displays.
- ECU session boundaries reach all three instruments. Gauge heartbeat
  fault-summary bits report local health, not a claim that the engine is safe.

Critical events have arbitration priority, but a frame's identifier alone
does not prove an end-to-end response bound. Derive and measure deadlines,
queueing, interrupt and actuator delay under PAR-06/08/09/12.

## 4. Bus-load budget

Conservative estimate: 135 bits per 8-byte classic frame including stuffing,
or about 270 microseconds at 500 kbit/s. Additional consumers do not duplicate
broadcast frames.

| Periodic producer/class | Frames/s |
|---|---|
| ECU fast (3 x 100 Hz) | 300 |
| ECU medium (3 x 10 Hz) | 30 |
| ECU slow (2 x 1 Hz) | 2 |
| Cluster rider input (2 x 100 Hz) | 200 |
| Cluster GPS (2 x 5 Hz + 1 x 1 Hz) | 11 |
| Cluster heartbeat (1 Hz) | 1 |
| Cluster brightness (10 Hz) | 10 |
| Speedometer/tachometer heartbeats (1 Hz each) | 2 |
| **Total periodic** | **556** |

Periodic utilisation is about **15.0%**. A provisional 20 frames/s
event/diagnostic allowance gives about **15.6%**. This is a capacity estimate,
not a latency proof. Validate burst traffic and priority behaviour. Bulk
updates are service-mode operations, not part of the riding load budget.

## 5. Diagnostics and update transport

| Target | Single-frame request / response | ISO-TP tool request / target response |
|---|---|---|
| ECU | 0x700 / 0x701 | 0x780 / 0x781 |
| Warning cluster | 0x702 / 0x703 | 0x782 / 0x783 |
| Speedometer | 0x704 / 0x705 | 0x784 / 0x785 |
| Tachometer | 0x706 / 0x707 | 0x786 / 0x787 |

Use the target's ISO-TP pair in both application service and bootloader mode.
Only one image for that target may respond at a time; the range is not
bootloader-only. ISO-TP supplies segmentation/flow control, not an image
update command format. Define update payloads, sequence/error handling,
target-role checks and version compatibility before implementation.
An ECU USB service bridge relays to the selected target; it does not broadcast
one image to all instruments.

Initial service IDs remain:

| ID | Service |
|---|---|
| 0x01 / 0x02 | Read / clear fault entry |
| 0x03 / 0x04 | Read / guarded write configuration |
| 0x05 | Unlock configuration write session |
| 0x06 | Read live signal |
| 0x10 | Firmware version and build identity |
| 0x20 | ECU safe-timing selection (unsupported on instruments) |
| 0xF0 | Enter target bootloader/service |

Write sessions expire after 60 s inactivity under the existing proposal.
Unlock format, service-specific payloads and physical/service guards need
review; an unlock passphrase is not a security assurance. `not_supported`
is explicit for services a target does not implement.

## 6. Freshness, startup and recovery

- Each instrument detects three consecutive missed ECU 1 Hz heartbeats.
  Gauges hold their own last-known needles and indicate staleness locally;
  the cluster independently warns. Local indication pattern and recovery
  guards remain PAR-09, not assumed from peer visibility.
- Cluster detects each gauge loss separately and warns. ECU logs node
  health and continues engine control; gauge software is not an engine
  prerequisite.
- ECU must handle cluster loss and stale TPS/switch inputs under a validated
  fallback policy. The cluster/CAN stop-request path must not be assumed
  available during the fault that removed it.
- Data freshness is per message, not inferred from a live heartbeat.
  Range/rate checks, invalid/reserved encodings, receive age limits, period
  tolerances and recovery hysteresis require PAR-09 closure.
- CAN bus-off is logged; recovery follows the peripheral's CAN recovery
  procedure and a bounded retry policy to be defined in PAR-09. Do not
  represent stale state as recovered simply because the peripheral rejoined.
- Fixed identities need no dynamic discovery. Send a heartbeat on readiness
  then periodic traffic; ECU ignition readiness must not wait for peers.
  A node rejoining an active bus must not reset other nodes.

## 7. Time and protocol evolution

ECU monotonic session time is authoritative for logs. GPS UTC comes from
cluster `gps_fix_state`, not a heartbeat. Existing YAML does not provide
a distributed time-sync exchange or sender timestamp in each telemetry
frame; do not claim those capabilities. Use ECU receive timestamps until
a reviewed time-sync interface is added if measurements require it.

Change encodings, ownership or transport addresses through a reviewed
protocol version and update all consumers/tests. Wire DLC/padding,
compatibility checks, invalid data and firmware-image target identity remain
release work under TASK-03/06. The YAML is a specification; protocol code
generation is planned, not yet implemented.

## Related

- [Dashboard](dashboard.md), [firmware](firmware.md), [HIL](hil.md)
- [Requirements](../project/requirements.md), [V&V](../project/verification-plan.md)

## Specification regression checks

Install [test dependencies](../../tools/requirements-dev.txt) in a development
virtual environment, then run from the repository root:

```sh
python3 -m pip install -r tools/requirements-dev.txt
python3 -m unittest discover -s tools -p 'test_*.py'
```

These check topology, ownership, frame layout, per-node service/health
endpoints, transport collisions and the periodic load calculation. They
validate the specification, not on-target CAN operation or V&V completion.
