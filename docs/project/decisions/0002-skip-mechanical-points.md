# ADR-0002: Skip mechanical points, first-start on ECU-controlled fixed-timing ignition

**Status:** Accepted (refined by [ADR-0004](0004-kick-start-flat-battery.md) and [ADR-0006](0006-modern-magneto-replacement.md))
**Date:** 2026-09-28

## Context

The user's original brief planned to first run the engine with the
original points ignition and stock carburettor as a baseline
configuration, then later replace the points with a custom ECU. The
motivation was to have a real reference for the specific engine rather
than relying on generic assumptions.

Two problems with that plan surfaced during scoping:

1. The K181's points system's baseline data is contaminated by contact
   bounce, point-gap drift, cam wear and magneto ageing. What would be
   measured is "engine + noisy trigger," not the engine.
2. A 36-1 crank trigger wheel is being installed regardless, for later
   characterisation. Once installed, the mechanical cam-and-contact
   system inside the flywheel becomes redundant.

## Decision

Skip mechanical points entirely. First engine run is with the ECU in
**fixed-timing mode**, behaviourally equivalent to a well-adjusted points
system but implemented in firmware. No timing map, no load compensation,
no adaptive logic — just a single timing advance value read from the
config store, applied to the coil driver on every trigger-wheel sync.

This becomes the ignition baseline against which mapped timing (phase 4),
load-compensated timing (phase 6) and any later adaptive control are
compared.

Consequences of removing the mechanical points:

- The K181's magneto's integrated HT coil is abandoned. An external
  inductive coil is driven by an ECU-owned low-side IGBT driver.
- A vehicle battery becomes necessary (small LiFePO4 sized to the ECU
  and starting/idle loads).
- The magneto stator continues to charge the battery via a
  regulator/rectifier. If the magneto's charging capacity is
  insufficient, a permanent-magnet alternator replaces it.

## Consequences

Positive:

- Clean, jitter-free ignition trigger from day one. Repeatability of the
  ignition baseline is limited by the engine and the measurement chain,
  not the ignition mechanism.
- No mechanical wear items in the ignition path.
- ECU hardware is validated at first engine start rather than at some
  later phase-5 milestone. First-firmware surface area is minimal
  (fixed-timing loop), so first-start failure modes remain tractable.

Negative:

- **ECU becomes first-start critical.** Mechanical assembly and ECU
  development are now parallel tracks that must converge. Phase 2 (ECU
  bring-up on HIL) blocks phase 3 (first start). This is a schedule
  constraint, not just a plan preference.
- A "true mechanical points" data point in the sequence of experiments
  is no longer available on this bike. The reference for later ignition
  work is fixed-timing ECU-driven ignition. This is accepted given the
  known contamination of points-baseline data.
- New failure mode: ECU fault at the roadside. Mitigated by boot-into-
  safe-timing on any config fault and by internal fault logging.

## Alternatives considered

- **Keep mechanical points as first configuration.** Rejected: noisy
  baseline, mechanical wear items, and the points and 36-1 trigger
  cannot coexist cleanly on the flywheel.
- **Discrete analog fixed-timing ignition (crank trigger → schmitt →
  monostable delay → IGBT) as an interim.** Retained as a fallback if
  the ECU schedule slips behind the mechanical assembly. Not the
  primary plan.
- **First start on ECU with mapped ignition immediately.** Rejected:
  couples "does the engine run" with "does the map work." Fixed-timing
  first is a strictly smaller firmware surface.

## Related

- [ADR-0001](0001-two-node-can-topology.md) — two-node CAN topology.
- [Staged plan](../staged-plan.md) — reflects the reordering that this
  ADR causes.
