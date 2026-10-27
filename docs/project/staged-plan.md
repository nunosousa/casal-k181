# Staged plan

Milestone roadmap under the [engineering framework](engineering.md).
The [backlog](backlog.md) tracks executable work and dependencies; the
[V&V plan](verification-plan.md) defines hardware-release, bench, engine and
riding gates. Requirements and interface review precede affected design
release, without forcing optional research into the first-start baseline.

The project proceeds in numbered phases. Each phase produces a preserved
dataset, and no phase begins until the previous phase's baseline is
documented.

The plan reflects one significant reordering from the user's original brief:
the ECU work moves *earlier* because the decision to skip the mechanical
points ignition entirely (see
[ADR-0002](decisions/0002-skip-mechanical-points.md)) makes ECU-controlled
fixed-timing ignition a first-start prerequisite rather than a phase 5
upgrade.

## Phase 0 — Mechanical restoration

Frame, forks, wheels, brakes, bearings, seals. Engine bottom end inspected
and restored. Nothing electrical yet. Ends when the rolling chassis is
complete and the engine bottom end is ready to accept the Eurocilindro top
end.

## Phase 1 — First running configuration mechanical build

Assemble the first running configuration:

- Eurocilindro 60 cc top end with matched cylinder head and squish
  clearance chosen from measured stroke and installed deck height.
- 5-speed gearbox.
- Original carburettor.
- 36-1 crank trigger wheel installed on the crank end, with the sensor
  bracket mounted rigidly to the crankcase.
- No ignition system yet.

Port timing on the actual Eurocilindro measured and documented. Squish
clearance measured with solder. Baseline jetting chosen with rationale
recorded.

## Phase 2 — ECU hardware and HIL bring-up

In parallel with phase 1:

- ECU hardware designed, built and bench-verified.
- Speedometer, tachometer and warning-cluster controller hardware designed,
  packaged in their respective enclosures and bench-verified as three CAN
  nodes; shared handlebar functions reside in the warning-cluster unit.
- CAN protocol drafted in `protocol/messages.yaml`.
- HIL bench: trigger wheel spun by a small motor, ECU fires an external
  coil into a dummy load, ignition timing verified against an independent
  optical trigger on a scope.

Phase 2 must be complete before phase 3.

## Phase 3 — First start, fixed-timing baseline

First engine run with the ECU in fixed-timing mode — behaviourally the
electronic equivalent of a well-adjusted points system. No timing map, no
load compensation. This is the reference against which all later ignition
work is measured.

Characterisation runs per the [measurement plan](../measurement-plan.md).

## Phase 4 — Mapped ignition timing and dashboard integration

Add RPM-based ignition-timing map. All three instrument CAN nodes integrated,
with local display drive and independent health/service checks. Re-characterise.
Compare against phase 3.

## Phase 5 — Carburettor optimisation

If phase 3–4 data justify it: jetting sweep, needle profile, slide cut-away
review. Possibly a different carburettor. Re-characterise.

## Phase 6 — Ignition refinement

Load-dependent timing compensation, dwell tuning, spark-energy
characterisation. Re-characterise.

## Phase 7 — Crank-dynamics-based engine-state estimation

Instantaneous crank angular velocity captured per tooth. Investigate
whether per-cycle Δω and its harmonics carry usable information about
load, combustion phasing, misfire and knock-equivalent phenomena. This
phase is exploratory: outcome may be "yes, useful" or "no, noise floor
too high," and either is a valid result.

## Phase 8 — Model-based or adaptive ignition control

Only if phase 7 results justify it. Otherwise retain phase-6 ignition
control. Phase 9 does not depend on adaptive ignition being adopted.

## Phase 9 — Throttle-body fuel injection exploration

Explore replacing the carburettor with a throttle body and electronically
controlled injector, using sensors and ECU calibration to control fuel
delivery (see
[ADR-0010](decisions/0010-throttle-body-fuel-injection.md)). This is an
experiment, not a commitment to retain injection.

- Preserve a characterised carburettor configuration and dataset as the
  comparison baseline. Hold ignition calibration and engine hardware
  constant during the fuel-system comparison.
- Assess throttle-body fit, injector sizing and minimum controllable pulse
  width for the 60 cc two-stroke, regulated fuel supply, filtration,
  plumbing and retention of two-stroke lubrication.
- Evaluate actual throttle-position sensing, intake-air and engine
  temperature, supply voltage and fuel pressure. Compare RPM/TPS-based
  fuelling with MAP-based load estimation only if the pulsating
  piston-port intake signal proves usable.
- Define ECU injector scheduling, fuel maps, injector dead-time
  compensation, starting/warm-up and transient enrichment. Decide driver
  and pump-switching hardware allocation before implementation; do not
  assume the current ECU/PDM already supports injection.
- Bench/HIL-verify injector control, fuel-system leak/pressure behaviour,
  shutdown on loss of crank synchronisation or engine stop, and sensor
  and calibration fault handling before engine tests. Revalidate the
  power budget and flat-battery kick-start capability with fuel-system
  loads included.
- Calibrate progressively, then re-characterise starting, idle, throttle
  response, performance, fuel consumption, EGT and CHT against the
  carburettor baseline per the [measurement plan](../measurement-plan.md).
  Evaluate wideband lambda as supporting evidence, accounting for
  two-stroke scavenging and oil contamination rather than treating it as
  an unquestioned mixture reference.

Proceed to riding tests only after bench checks and controlled engine
tests establish safe fuel delivery. Retain the carburettor if packaging,
power, reliability or measured results do not justify injection.

## What is deferred / uncertain

- Wideband lambda in the exhaust. Two-stroke oil contamination shortens
  sensor life; worth revisiting after phase 4 and for phase-9 calibration.
- MAP sensing. Value unclear on a naturally aspirated piston-port
  two-stroke; deferred to load-sensing evaluation for phase 9.
- Fuel-consumption instrumentation beyond weigh-before/weigh-after.
