# ADR-0006: Replace stock magneto with modern 12 V VAPE-class unit

**Status:** Accepted
**Date:** 2026-09-29

## Context

The original K181 flywheel magneto is a 50-year-old assembly comprising:

- Stator (nominally 6 V-class, ~30-40 W output at operating RPM).
- Rotor / flywheel with embedded magnets.
- Integrated high-tension ignition coil.
- Mechanical points and cam.

Earlier ADRs pushed on parts of this assembly:

- [ADR-0002](0002-skip-mechanical-points.md) removed the mechanical
  points from the ignition path in favour of ECU-controlled fixed-
  timing ignition. The magneto's integrated HT coil was already
  planned to be abandoned in favour of an external coil.
- [ADR-0005](0005-retain-incandescent-exterior-lamps.md) roughly
  doubled the running load budget by requiring incandescent exterior
  lamps.
- [`power.md`](../../architecture/power.md) previously anticipated
  keeping the original stator core with a rewind (Path A) as the
  default plan, with PMA replacement (Path B) as a fallback.

The user has since decided to source a **complete modern 12 V
magneto assembly** — stator, rotor, and ignition components — from a
supplier such as VAPE (vape.eu), which specialises in 12 V conversion
kits for classic small motorcycles. This is functionally close to
Path B but sourced as a purpose-built product rather than adapted
from another vehicle.

## Decision

Replace the full stock magneto assembly (stator, rotor, integrated
HT coil, points, cam) with a modern 12 V equivalent, sourced as a
complete kit.

Preferred source: **VAPE.eu** or equivalent supplier offering a Casal
M151-compatible 12 V conversion kit.

Usage of the new assembly:

- **Charging side** — stator AC output feeds the shunt-type MOSFET
  R/R, which produces the 12 V DC bus. This is the primary reason for
  the change.
- **Ignition side** — any CDI unit or points-emulation module included
  with the kit is **not used**. The custom ECU handles ignition per
  ADR-0002 with its own crank trigger (see below) and its own coil
  driver.
- **HT coil** — the modern coil supplied with the VAPE kit is a
  candidate for use as the external inductive coil driven by the
  ECU's IGBT. A separate modern automotive coil is an equally valid
  alternative. Choice deferred to the ECU schematic phase.
- **Crank trigger** — the 36-1 trigger wheel per
  [ADR-0002](0002-skip-mechanical-points.md) and
  [trigger-wheel.md](../../mechanical/trigger-wheel.md) is installed
  on the new rotor's outer face. VAPE kits typically ship with a
  single-tooth Hall trigger for their own ignition; we ignore that
  and use our 36-1 pattern for consistency with the phase 7 crank-
  dynamics ambitions in the [staged plan](../staged-plan.md).

## Consequences

Positive:

- **Stator capacity resolved.** Typical VAPE 12 V kits produce ~90-100 W
  at operating RPM, comfortably above the ~50 W ADR-0005 load budget.
  Battery drain during rides ceases to be routine.
- **Turnkey mechanical parts** with known thermal and vibration
  behaviour. No rewind coordination.
- **Fresh components** — no unknown-state 50-year-old windings.
- **Path A (stator rewind) removed** from `power.md`. Simpler.
- ADR-0004 supercap bootstrap remains valid — passive rectifier +
  supercap doesn't care whose stator feeds it. In fact, the new
  stator's higher low-RPM output makes kick-start bootstrap more
  robust.

Negative:

- **Character concession.** The magneto is no longer original.
  Visually similar under the flywheel cover but not authentic. Judged
  to remain inside the "recognisable as a K181" constraint boundary
  because the magneto is not externally visible.
- **BOM cost delta: +€150-200** vs. the prior rewind plan (kit at
  €200-350 vs. rewind at €100-200).
- **Fit dependency.** VAPE must offer a Casal M151-compatible kit,
  or a similar supplier must. Verify availability before ordering
  other magneto-side parts.
- **Kit trigger geometry conflict.** VAPE-integrated trigger is
  ignored, but the physical feature (tooth, magnet, or Hall) remains
  on the rotor. It must not interfere with the 36-1 wheel mounting.
  Confirm during physical inspection of the ordered rotor.
- **Wiring must be adapted.** VAPE stator output is not a drop-in
  replacement for the original — different pin count, different
  colour code. Harness rework required.

## Alternatives considered

- **Stator rewind (previous Path A).** Rejected in favour of turnkey
  replacement. Cheaper but requires a knowledgeable rewinder, and
  the resulting output would still be lower than a purpose-built
  modern kit.
- **Aftermarket generic PMA (previous Path B).** Rejected — the
  VAPE-class purpose-built kit is essentially a specialised PMA
  already, with the mechanical fit already engineered for the
  intended vehicle class.
- **Accept battery drain (previous Path C).** Rejected earlier.
- **Retain original stator, no rewind, LED lamps.** Rejected via
  ADR-0005 (LED lamps illegal in stock housings).

## Relation to prior ADRs

- **[ADR-0002](0002-skip-mechanical-points.md)** — reinforced. The
  mechanical points and integrated HT coil were part of the assembly
  being replaced.
- **[ADR-0004](0004-kick-start-flat-battery.md)** — unchanged. Kick-
  start bootstrap works with any stator that can deliver DC via a
  passive rectifier at low RPM.
- **[ADR-0005](0005-retain-incandescent-exterior-lamps.md)** — the
  load-budget concern that partially motivated this decision is now
  resolved.

## Open questions

- **Specific VAPE (or equivalent) kit selection** — depends on M151
  compatibility, in-stock availability, and kit contents. Confirm
  before ordering.
- **HT coil selection** — VAPE-supplied vs. separate modern
  automotive part. Deferred to ECU schematic phase.
- **Whether to remove the kit's Hall trigger** at installation
  (physically remove or leave-and-ignore). Physical removal is
  cleaner if the trigger tab interferes with the 36-1 wheel
  mounting; leave-in-place otherwise.
- **VAPE stator pin-out and voltage envelope** — used to size the
  R/R input side and any additional protection.

## Related

- [ADR-0002: Skip mechanical points](0002-skip-mechanical-points.md)
- [ADR-0004: Kick-start with flat battery](0004-kick-start-flat-battery.md)
- [ADR-0005: Retain incandescent exterior lamps](0005-retain-incandescent-exterior-lamps.md)
- [Power architecture](../../architecture/power.md) — rewritten
  charging-source section
- [Trigger wheel](../../mechanical/trigger-wheel.md) — mounting
  substrate revised
