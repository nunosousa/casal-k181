# ADR-0012: Separate CAN controllers inside each dashboard enclosure

**Status:** Accepted
**Date:** 2026-10-27

## Context

ADR-0001 made the three stock-style instrument enclosures passive and
connected them to one handlebar controller. The project now requires a
controller inside each enclosure to preserve the stock appearance and avoid
remote gauge/LED drive wiring.

## Decision

Supersede ADR-0001's two-node topology with four intelligent CAN nodes:

| Node | Responsibilities |
|---|---|
| ECU | Engine control, wheel/crank acquisition, engine/environment sensing, logging, exterior-lamp and charge-control logic. |
| Speedometer | Its own needle/backlighting, speed display, odometer and odometer persistence. |
| Tachometer | Its own needle/backlighting and RPM display. |
| Warning cluster | Warning LEDs/repeaters and all remaining dashboard/handlebar functions: switchgear, twistgrip TPS, GPS, ambient-light acquisition and shared brightness command. |

Each instrument controller, power conversion, CAN transceiver and local
output stage lives inside its own existing-style enclosure. There is no
additional central handlebar controller. The PDM remains passive and owns
physical exterior-lamp, coil and charge switching as already decided.

The residual-function rule concerns dashboard/handlebar functions, not a
transfer of existing ECU/PDM engine or power responsibilities.

Retain classic CAN, 500 kbit/s and 11-bit identifiers. Use a linear trunk
with short instrument drops and exactly two terminations at physical ends,
not one termination per controller. Endpoint positions remain a harness
decision.

Protocol version 2 replaces the old `handlebar` node with `warning_cluster`
and adds `speedometer` and `tachometer`. Define individual heartbeats,
fault events, diagnostic endpoints and update transport addresses. No
version-1 compatibility is claimed. Preserve `handlebar_switches` as the
message name for physical rider switchgear, not the name of a controller.

## Consequences

- Four MCUs/transceivers and four separately addressable firmware identities
  replace two. Common instrument hardware/software is encouraged, but each
  unit operates, resets, reports health and updates independently.
- Odometer persistence moves specifically to the speedometer; GPS, TPS and
  switchgear belong specifically to the warning cluster.
- A speedometer or tachometer loss must not disable the other instruments
  or engine through a software dependency. A shorted shared bus or power
  branch still needs system-level fault analysis.
- Warning-cluster loss removes rider-input acquisition and shared GPS/ALS;
  stale-input fallback and stop-path independence remain explicit blockers.
- Recalculate power, bus loading, connectors and enclosure fit. MCU
  selection is not finalised by this decision.

## Related

- [Dashboard controllers](../../architecture/dashboard.md)
- [CAN specification](../../architecture/can-bus.md)
- [ICD](../../architecture/interfaces.md)
- [Requirements](../requirements.md)
