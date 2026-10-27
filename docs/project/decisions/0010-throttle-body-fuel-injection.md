# ADR-0010: Explore throttle-body fuel injection

**Status:** Accepted
**Date:** 2026-10-27

## Context

The original project constraints prohibited fuel injection at any phase.
The project now includes an objective to explore replacing the carburettor
with a throttle body and electronically controlled injector, using sensors
and ECU calibration to control fuel delivery.

Carburettor baselines remain necessary to isolate the effects of ignition
development and to determine whether injection improves the vehicle.

## Decision

Replace the blanket prohibition with a gated, late-stage throttle-body
fuel-injection experiment in [phase 9](../staged-plan.md). Acceptance of
this objective does not commit the final vehicle to injection or select
specific fuel-system hardware.

- Retain carburettor-based first start, optimisation and reference datasets.
- Retain piston-port induction, the existing cylinder port geometry and
  two-stroke lubrication requirements. This is not a direct-injection or
  reed-valve conversion.
- Use ECU-controlled fuel delivery with sensor-based load and operating
  condition compensation. Sensor selection, fuel-system design, driver
  allocation and calibration strategy require bench evidence before
  adoption.
- Preserve ECU ownership of fuel control;
  injector and pump power-stage placement is a later hardware decision,
  consistent with the separation of control logic and power switching.

- Revalidate electrical capacity and the flat-battery kick-start
  requirement from [ADR-0004](0004-kick-start-flat-battery.md), including
  fuel pressure generation and injector operation.
- Validate fuel-system shutdown and fault handling before riding tests.
  A fixed-timing ignition fallback alone is insufficient for injection;
  fuel-calibration faults also require a validated fallback, while loss
  of safe fuel control requires shutdown.

The original two-node premise is superseded by
[ADR-0012](0012-distributed-dashboard-can-nodes.md); fuel control remains on
the ECU in the four-node architecture.

## Consequences

- Fuel delivery becomes an experimental optimisation variable alongside
  ignition, with measured comparison against a preserved carburettor setup.
- Additional fuel plumbing, sensors, power switching, firmware scheduling,
  calibration and fault testing will be needed if implementation proceeds.
  Existing hardware and protocol definitions are not assumed sufficient.
- Packaging, electrical demand, safe operation and reliability are gates,
  not assumed solved. Returning to the carburettor is a valid outcome.
- Phase 9 does not require successful crank-dynamics estimation or
  adaptive ignition; it uses the last validated ignition configuration.

## Related

- [Project constraints](../constraints.md)
- [Staged plan](../staged-plan.md)
- [ECU architecture](../../architecture/ecu.md)
- [Measurement plan](../../measurement-plan.md)
