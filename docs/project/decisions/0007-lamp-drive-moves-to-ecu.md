# ADR-0007: Move exterior lamp drive from handlebar controller to ECU enclosure

**Status:** Accepted (physical drive location subsequently refined by [ADR-0008](0008-separate-power-distribution-module.md); logic-ownership decision stands)
**Date:** 2026-09-29

## Context

[ADR-0001](0001-two-node-can-topology.md) placed all vehicle exterior
lamp drive (headlight, tail, brake, front and rear indicators, horn)
with the handlebar controller. That decision was made when the
lamps were assumed LED, with small MOSFET drives and negligible
thermal footprint.

[ADR-0005](0005-retain-incandescent-exterior-lamps.md) reversed the
lamp technology to incandescent, which grew the drive-stage
substantially:

- Headlight and horn now driven by automotive relays.
- Indicator, brake, tail channels use 10 A-class MOSFETs with TVS
  protection.
- Per-lamp fuses upsized.
- Cold-filament inrush requirements add stress margin.

The handlebar controller's target enclosure is small — ~60 × 40 × 20 mm
inside the headlight nacelle — and now shares that space with
stepper drivers, GPS module, CAN transceiver, TPS I2C, MCU, switch
inputs, and their protection. The lamp drive stage would consume the
majority of that PCB area.

Meanwhile, the current wire topology routes exterior-lamp power *up*
from the ECU (in-frame) to the handlebar controller, and *back down*
through the frame harness to the rear lamps. That's the largest
continuous current in the vehicle taking the longest path.

## Decision

Move all vehicle exterior lamp drive from the handlebar controller
to the ECU enclosure.

**Handlebar controller retains:**

- Handlebar switchgear input processing.
- Dashboard drive (stepper motors, warning lamps, dial-face
  illumination).
- TPS I2C.
- GPS UART.
- All interior lighting.

**ECU gains:**

- Lamp drive stage: 7 MOSFETs (front indicator L/R, rear indicator
  L/R, rear tail, rear brake, 2 headlight drive if MOSFET rather than
  relay — see below) + 2 automotive relays (headlight, horn).
- Per-lamp fuses relocated from the previously-planned handlebar-side
  fuse box.
- Turn-signal blink timing (generated locally from steady-state rider
  intent bits in `handlebar_switches`).

**CAN protocol:** unchanged.
`handlebar_switches.indicator_left / indicator_right / hazard` bits
now carry the **rider intent** (steady-state "L requested"), not the
blink phase. The ECU consumes those bits and generates the blink at
~1.5 Hz locally. Dashboard indicator repeaters (still handlebar-owned
per interior-lighting responsibility) blink on the handlebar's own
timer; small phase drift between rear lamps and dashboard repeaters
is acceptable and not visually noticeable.

**Wiring topology:**

- Handlebar controller feed from ECU: switched-rail power (small,
  ~0.5 A for the controller electronics only, not for lamps) + CAN.
  Wire gauge to the handlebar drops accordingly.
- Front lamps (headlight, front indicators, horn if handlebar-
  mounted): direct wire from the ECU up to the handlebar area.
- Rear lamps (tail, brake, rear indicators): direct wire from the
  ECU to the tail, avoiding the up-and-back-down routing.

## Consequences

Positive:

- Handlebar controller enclosure shrinks. Realistic new target ~50 ×
  35 × 15 mm inside the headlight nacelle.
- Better thermal environment for high-current lamp drive components
  (ECU compartment has more airflow and radiating surface).
- Cleaner ownership: handlebar processes logic, ECU switches power.
- Rear-lamp wire path no longer "up + back down."
- Fuse box consolidates at the ECU location.

Negative:

- ECU enclosure grows to accommodate ~40 × 40 mm of lamp-drive PCB
  and ~2 W of additional dissipation. Modest.
- Front-lamp power now runs from the ECU up to the handlebar area
  as ~3-4 dedicated conductors rather than being distributed from a
  shared handlebar-side power bus. Similar net copper.
- Turn-signal blink phase between exterior lamps and dashboard
  repeaters may drift by a fraction of a cycle. Both use ~1.5 Hz
  targets; drift is imperceptible.
- HIL incandescent-load testing moves from handlebar HIL variant to
  the ECU HIL rig.
- ECU firmware gains a new (soft-RT, low-priority) responsibility:
  lamp state machine + blink timer. Modest.

## Alternatives considered

- **Keep drives at handlebar (status quo).** Rejected on
  space/thermal grounds under ADR-0005 loads.
- **Split ownership (handlebar drives front, ECU drives rear).**
  Rejected — creates two lamp-drive stages, splits the state machine
  across two nodes, offers no compelling benefit.
- **Add a third node dedicated to lamp / body-control drive.**
  Rejected — undoes ADR-0001's two-node rationale; overkill for a
  moped.
- **Retain the LED assumption from before ADR-0005.** Not available:
  regulatory constraint.

## Related

- [ADR-0001: Two-node CAN topology](0001-two-node-can-topology.md) —
  ownership refined by this ADR
- [ADR-0005: Retain incandescent exterior lamps](0005-retain-incandescent-exterior-lamps.md) —
  motivates the drive-stage BOM growth
- [System architecture](../../architecture/system.md) — updated
- [ECU subsystem](../../architecture/ecu.md) — updated
- [Handlebar controller](../../architecture/handlebar-controller.md) —
  updated
- [Power architecture](../../architecture/power.md) — fuse location
  updated
- [CAN bus](../../architecture/can-bus.md) — semantic note on
  indicator bits
