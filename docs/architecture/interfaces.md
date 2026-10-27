# Interface control document

Status: draft contracts and interface inventory, not a released pinout.
See the [requirements](../project/requirements.md), [framework](../project/engineering.md)
and closure work in the [backlog](../project/backlog.md).

## Interface inventory

| ID | Endpoints / direction | Contract and ownership | Unresolved before release |
|---|---|---|---|
| IF-01 | Stator / R/R / PDM / battery / ECU / three instruments | PDM owns distribution, protection, supercap and charge FETs. ECU gets protected DC bus power; each instrument gets a protected switched branch. ECU input target is 8-16 V. | Per-node connector pins, fuses, conductor sizing, grounds, fault/transient envelope, bootstrap profile and revised four-node power budget; PAR-02/04, TASK-04. |
| IF-02 | ECU to PDM control; PDM to ECU sense | ECU owns charge/lamp/ignition logic; PDM owns physical switching, including coil driver per ADR-0009. Keep coil primary current out of ECU sensor returns. | Full signal count, levels, polarity, pull states, reset behaviour, drive/sense bandwidth, reference/return allocation and short/open detection; TASK-03. |
| IF-03 | Crank and wheel targets to ECU | 36-1 crank acquisition and front-wheel capture owned by ECU; independent timing reference used for verification. | Final sensors, air gap, mounting datum, polarity, conditioning, thresholds and timer/pin allocation; PAR-03/12, TASK-05. |
| IF-04 | Engine/environment sensors to ECU; twistgrip TPS to warning cluster | ECU owns thermal, ambient and power measurements; warning cluster acquires/calibrates twistgrip TPS and publishes it over CAN. Actual throttle-body position is a separate phase-9 decision. | Verify satellite cable integrity, calibration, error, freshness and disconnected-input response; TASK-03. |
| IF-05 | PDM to coil, lamps and horn | High-current actuator wiring terminates at PDM; ECU commands switching. Stock-format incandescent exterior lamps retained. | Load ratings, connectors, protection, coil selection, maximum dwell, shutdown and fuse coordination; TASK-02/03/04. |
| IF-06 | ECU / speedometer / tachometer / warning-cluster CAN | Four nodes, classic CAN at 500 kbit/s, 11-bit IDs. Exactly two 120-ohm end terminations on the physical trunk, not on all four nodes. One producer per defined message. | Harness order/endpoints/drops, pinout, timing tolerances, invalid values and shared-bus fault policy; TASK-03. |
| IF-07 | Rider/switchgear/TPS/GPS/ALS to warning cluster; ECU/cluster CAN to gauges | Each enclosure contains its own MCU/transceiver and local display drive. Speedometer owns odometer; tachometer owns RPM display; warning cluster owns remaining dashboard/handlebar functions and shared brightness. Exterior switching remains in PDM. | Debounce, stop independence, GPS antenna location, gauge calibration, local stale indication, brightness fallback and odometer power-loss persistence; TASK-02/03/06. |
| IF-08 | Service host to ECU USB; service host to each of four nodes via CAN | Separate diagnostic and ISO-TP address pairs per node in YAML v2/CAN spec. Individual instrument updates with target-role validation; SWD internal only. | Service-state guards, connector/pins, command lengths, compatibility, errors, write guards and recovery behaviour; TASK-03/06. |
| IF-09 | MCU / bootloader / applications / calibration / storage | Riding application Ada/Ravenscar; boot and ECU USB service images C, as currently proposed. Logs stored externally. | Exact runtime support, sector-aligned image layout, memory/DMA ownership, calibration format and compatibility; TASK-06. |
| IF-10 | ECU / future power stages / injector / pump / fuel sensors | ECU owns fuel control if phase 9 proceeds; no existing pin or driver allocation is assumed adequate. | Mechanical fit, lubrication, pressure/plumbing, driver placement, sensor selection, electrical demand and shutdown/prime contracts; TASK-10. |

## Protocol specification authority

The [CAN YAML](../../protocol/messages.yaml) is the source for identifiers,
producers/consumers, bit positions, scaling, units and declared periods.
The [CAN specification](can-bus.md) provides transport/diagnostic behaviour;
subsystem documents provide application meaning. Do not copy encoding tables
here. New or changed messages update all affected consumers and tests in the
same reviewed baseline.

Before a protocol baseline, specify DLC/padding, reserved/invalid values,
range violations, freshness, startup/recovery, version compatibility and
transport error handling. These details are not implied by the existence
of a YAML field or a proposed code generator.

## Topology revision and release blockers

- [ADR-0012](../project/decisions/0012-distributed-dashboard-can-nodes.md)
  supersedes the former central handlebar controller. Instrument controllers
  are local, not passive gauge housings. TPS acquisition is now explicitly
  warning-cluster-owned; stale-throttle behaviour still needs validation.
- Some system, power, ECU and PDM text/diagrams predate ADR-0008/0009:
  direct battery feeds, ECU-local high-current drivers and old cable counts
  are not released wiring instructions. Accepted ADR-0009 places the coil
  driver in the PDM (or the selected smart coil).
- YAML version 2 defines four node identities, separate diagnostic and
  ISO-TP endpoints, peer heartbeats and shared dimming. Transport pairs
  are shared between the respective target's service/bootloader modes,
  not between nodes. Payload/version/role checks still need implementation.
  Logs currently use ECU receive timestamps; distributed time-sync messages
  are not defined.
- Continued operation on warning-cluster loss conflicts with relying on that
  link for stop requests or fresh load inputs unless explicit fault
  policies are provided. An emergency frame name does not prove a stop path.
- MCU package descriptions and firmware partition sizes are provisional.
  Verify exact ordering codes, Ada support, flash sectors and full-roadmap
  pin/resource allocation and each instrument's enclosure fit before PCB
  release. The H743-class suggestion is
  a candidate for review, not an accepted replacement for proposed ADR-0003.

TASK-03 closes cross-document interface contradictions; TASK-02, TASK-04,
TASK-05 and TASK-06 supply the corresponding safety, power and MCU contracts.
Do not fabricate pin assignments or numerical limits to close this inventory.

## Interface release checklist

For each populated connector/signal record: interface ID, endpoints, pin,
direction, level/range, reference/return, current/loading, timing, power-up
default, disconnected/short behaviour and test reference. For mechanical
interfaces include datum, clearance, material compatibility and retention.
Release those records with the schematic/harness baseline after review.
