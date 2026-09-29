# Cylinder head and squish clearance

Head selection, squish-clearance measurement, and target values for
the Eurocilindro top end. Squish clearance is one of the few
combustion parameters we can choose within the project's hard
constraints (no porting modifications, no reed valve, etc.) — worth
getting right.

## 1. What squish clearance is and why it matters

On a two-stroke with a hemispherical or bowl-shape combustion chamber,
the piston crown at TDC comes very close to a **squish band** —
a flat annular region around the periphery of the combustion chamber.
As the piston approaches TDC, the mixture trapped between the piston
crown and the squish band is expelled radially inward at high
velocity, generating turbulence that improves flame propagation.

Effects of squish clearance:

- **Too tight** (< 0.7 mm): piston contacts head during transient
  overspeed, rod stretch, or thermal expansion — catastrophic.
  Also increases detonation risk at moderate compression.
- **Too loose** (> 1.5 mm on this bore): weak squish flow, sluggish
  combustion, lower peak power.
- **Correct** (0.8-1.2 mm typical for 44 mm bore): brisk combustion,
  responsive tuning, safe margin against contact.

## 2. Target for the Eurocilindro 60 cc build

**Target squish clearance:** 1.0 mm ± 0.05 mm, measured hot at TDC on
a cold-assembled engine using the solder method (§4).

Justification:

- 44 mm bore in the "moderate performance two-stroke" class.
- The Eurocilindro is a good-quality NOS kit with reasonable rod-to-
  bore geometry, but exact stretch behaviour at 7000+ RPM is not
  known to us. 1.0 mm gives a comfortable margin.
- If phase 3-4 measurements suggest the engine wants tighter squish
  (lower BSFC, faster ignition, richer high-RPM torque), the head
  can be re-machined to 0.9 mm in phase 5.
- Never go below 0.8 mm without measuring rod stretch, which we do not
  have equipment to do.

## 3. Head selection

Options:

### 3.1 Existing Eurocilindro-matched head

If a period Casal (or Eurocilindro-branded) head that matches the
44 mm bore is available in known-good condition, use it. Measure its
combustion chamber volume, squish-band diameter, and squish-band
recess (if any) as the baseline for the calculations in §5.

### 3.2 Custom-machined head

If no known-good head is available, machine one from:

- An aluminium billet (raw material approach; expensive, full
  control).
- A slightly-oversized period head (turn the squish band flat, rebore
  the combustion chamber to spec, install a new plug thread if
  needed).

Custom machining is a phase-1 sub-project. Deferred until the K181's
existing head is inspected.

### 3.3 Head geometry parameters to specify

Regardless of source:

- **Squish-band OD:** 44.0 mm nominal (matches bore).
- **Squish-band ID:** ~34-36 mm (governs squish-band area; wider band
  = more squish flow, higher peak combustion pressure).
- **Squish-band recess (from head deck):** 0 mm — flat squish band
  sits directly on the cylinder deck (or on a compressible gasket, see
  §6).
- **Combustion chamber shape:** hemispherical or slightly toroidal
  bowl. Volume chosen to yield the target compression ratio (§7).
- **Plug angle:** central or slightly offset; no strong preference
  for phase 1.
- **Plug reach:** matches sparkplug thread reach (typically NGK B/BR
  series for this class of engine — verify against the intended plug).

## 4. Measuring squish clearance — solder method

The standard technique. Simple, cheap, accurate to ~0.05 mm.

**Required tools:**

- Soft lead-tin solder wire, 1.5-2.0 mm diameter.
- Ball-peen hammer (light, small).
- Micrometer (0.01 mm resolution).
- Small pick or tweezers.

**Procedure:**

1. Install the piston, rod, crank, cylinder, and head with the
   intended head gasket (see §6). Bolt to correct torque.
2. Remove the sparkplug.
3. Cut two lengths of solder wire, each ~30 mm.
4. Feed one length through the plug hole and lay it across the piston
   crown at the squish band position (parallel to the wrist pin — the
   thrust-side squish band is the tighter one due to rod tilt).
5. Feed the second length across the crown at 90° to the first.
6. Rotate the crank *slowly by hand* through TDC. The piston crown
   pinches the solder against the head's squish band and flattens
   the wire.
7. Continue past TDC. Remove the head. Retrieve the flattened solder
   pieces.
8. Measure the thickness of the flattest portion of each piece with
   the micrometer. This is the squish clearance at that location.
9. Report **four values** (two axes × two ends) if there is any
   asymmetry; the smallest is the safety-critical one.

**Interpretation:**

- If minimum measured clearance > 1.05 mm → head needs machining to
  reduce clearance.
- If minimum measured clearance < 0.9 mm → head needs machining to
  increase clearance, OR a thicker gasket used.
- If minimum measured clearance is 0.9-1.05 mm → within target.

**Repeat** after any head, gasket, or piston change.

## 5. Deck-height budget

Squish clearance = piston-below-deck-at-TDC + head-gasket-crushed-
thickness + head-squish-band-depth.

Measure separately:

- **Piston-below-deck at TDC:** with the cylinder installed on the
  crankcase and the piston at TDC, measure with a depth gauge from
  the cylinder deck to the piston crown. Positive value = piston
  below deck.
- **Head-gasket-crushed thickness:** manufacturer spec or measured
  after a crush test. Typical values: 0.3-0.7 mm depending on
  material.
- **Head-squish-band depth:** 0 mm target (flat head deck), verified
  by placing a straightedge across the head's squish band and
  measuring under it.

Sum these three to get the theoretical squish clearance. Cross-check
against the solder-method measurement in §4.

## 6. Head gasket

- **Type:** solid copper or aluminium sheet, 0.3-0.7 mm. Not a
  composite; two-stroke heat cycles are hard on paper-based gaskets.
- **Crushed thickness:** measure post-torque with the solder method
  or on a scrap installation.
- **Sealant:** copper spray on both faces of the gasket to fill
  small imperfections and improve seal.
- **Torque sequence:** cross-pattern, 25 % / 50 % / 100 % of final
  spec value. Retorque after first thermal cycle.

**Provisional plan:** 0.5 mm copper gasket as starting point; adjust
gasket thickness or head machining to hit the 1.0 mm squish target.

## 7. Compression ratio

Two-stroke compression is quoted two ways:

- **Geometric CR:** displacement + chamber volume / chamber volume,
  measured from TDC to BDC. Not very meaningful because the exhaust
  port is open for a large portion of the stroke.
- **Trapped CR (or delivery-ratio-adjusted CR):** measured from
  exhaust-port closure to TDC. Physically meaningful — this is the
  compression the trapped charge actually sees.

Target trapped CR for this class of engine: **8:1 to 9:1**.

Below 8:1 → weak combustion, low peak torque.
Above 9:1 → detonation risk on pump 95 RON gasoline (Portuguese
standard), especially at high load.

Chamber volume required to hit the target is derived from
displacement, exhaust-close angle (see [port-timing.md](port-timing.md)),
and target trapped CR. Head chamber volume can be measured by burette
method: fill the assembled head-and-piston-at-TDC volume with light
oil from a calibrated burette; the volume delivered is the total
above-piston volume at TDC.

## 8. Verification

- **Squish clearance** verified by solder method after final assembly.
- **Trapped CR** verified by burette method after final assembly.
- Both values recorded in the build log for the engine configuration.

## 9. Open questions

- **Source of the actual head** — Eurocilindro-matched original,
  reworked period head, or custom-machined billet. Deferred to
  physical inspection.
- **Exhaust-port closure angle on the Eurocilindro** — required for
  the trapped-CR calculation. Measured per
  [port-timing.md](port-timing.md).
- **Piston-below-deck at TDC** — depends on the rod and crank
  installed. Measured during the phase-1 mechanical build.

## 10. Related

- [Port timing](port-timing.md) — feeds trapped-CR calculation
- [Constraints](../project/constraints.md) — no porting modification
- [Staged plan phase 1](../project/staged-plan.md) — head/squish is
  set during phase 1 build
