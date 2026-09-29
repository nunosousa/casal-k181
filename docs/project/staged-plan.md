# Staged plan

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
- Handlebar controller hardware designed, built and bench-verified.
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

Add RPM-based ignition-timing map. Dashboard integrated and driven from
CAN broadcasts. Re-characterise. Compare against phase 3.

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

Only if phase 7 results justify it. Otherwise stop at phase 6.

## What is deferred / uncertain

- Wideband lambda in the exhaust. Two-stroke oil contamination shortens
  sensor life; worth revisiting after phase 4.
- MAP sensing. Value unclear on a naturally aspirated piston-port
  two-stroke; deferred.
- Fuel-consumption instrumentation beyond weigh-before/weigh-after.
