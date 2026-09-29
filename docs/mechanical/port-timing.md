# Eurocilindro port-timing measurement

Procedure for measuring exhaust and transfer port opening/closing
angles on the Eurocilindro 44 mm cylinder before final assembly.
Port timing sets the effective compression ratio (via exhaust close
angle), determines the pipe tuning target, and characterises the
kit's intended performance envelope.

**Constraint:** [ADR-adjacent constraint from constraints.md](../project/constraints.md) —
no porting modifications. We are *measuring* what the kit ships with,
not modifying it. But knowing the numbers is essential for the rest
of the system to be designed intelligently.

## 1. What is measured

For a Casal M151-based piston-port two-stroke, the relevant events per
crank revolution are:

- **Exhaust open (EO):** crank angle after TDC at which the piston
  crown uncovers the top of the exhaust port on the downstroke.
- **Transfer open (TO):** angle after TDC at which the transfer ports
  begin to open on the downstroke.
- **BDC:** 180° after TDC. Reference point.
- **Transfer close (TC):** angle after BDC at which the piston covers
  the transfers on the upstroke.
- **Exhaust close (EC):** angle after BDC at which the piston covers
  the exhaust port on the upstroke.
- **Intake open (IO) / Intake close (IC):** for piston-port intake,
  measured by the piston skirt uncovering/covering the intake port.
  IO occurs on the upstroke; IC on the downstroke.

Derived quantities:

- **Exhaust duration:** EC + (360 − EO) − 180 = EC − EO + 180. In
  practice reported as `2 × (180 − EO)` if symmetric (EO = EC around
  BDC). Actual engines are ~symmetric to within 1°.
- **Transfer duration:** likewise, `2 × (180 − TO)`.
- **Blowdown angle:** the angle from EO to TO — the crank interval
  during which exhaust flows before the transfers open. Longer
  blowdown = higher trapping efficiency at high RPM but rougher low-
  end.

## 2. Bench setup

**Required:**

- The Eurocilindro cylinder, cleaned and free of assembly grease.
- A piston + rings + wrist pin (the intended piston).
- A rod (any rod that fits the wrist pin will do for this measurement).
- A crank stand or bench fixture that holds the crank horizontally and
  allows a degree wheel to be mounted on its end.
- Degree wheel ≥ 150 mm diameter.
- Fixed pointer aligned to the degree wheel.
- Dial indicator with 0.01 mm resolution and a magnetic base (used for
  TDC determination on the piston crown).
- Depth micrometer or vernier caliper.
- Bright work light.

**Assembly:**

1. Install the piston with rings on the rod; install rod on the crank.
2. Mount the crank in the bench fixture.
3. Slide the cylinder over the piston, careful with the rings.
4. Do not bolt the cylinder to a crankcase — the measurement is on
   the crank + piston + cylinder alone.
5. Fix the cylinder position vertically with a bracket clamped to
   the bench fixture, or with the cylinder resting on the crankcase
   mounting studs of the fixture. The cylinder must be at the same
   height it would be on the engine (i.e. the cylinder-base gasket
   thickness accounted for).
6. Fit the degree wheel and pointer.

## 3. Finding TDC on the degree wheel

Use the piston-stop method — same as
[trigger-wheel §7](trigger-wheel.md#7-sync-offset-calibration-procedure):

1. Rotate crank so piston is well below TDC.
2. Fit piston-stop tool (a bolt through the sparkplug hole or a
   temporary equivalent).
3. Rotate crank in normal running direction until piston contacts
   stop. Read degree wheel: α₁.
4. Rotate in reverse until piston contacts stop. Read: α₂.
5. True TDC = (α₁ + α₂) / 2.
6. Adjust the degree wheel or pointer so the pointer reads 0° at true
   TDC.

Verify with a dial indicator on the piston crown through the plug
hole: at the calculated TDC, the dial should read peak height (piston
motion ~0 for small crank movements).

## 4. Measuring port events

For each port event, the same technique:

1. Rotate crank slowly, watching the port through the exhaust or
   transfer opening from the cylinder outside.
2. As the piston crown edge just aligns with the top edge of the
   port, stop.
3. Read the degree wheel.

The piston-crown-to-port-edge alignment is done by eye; illuminate
from behind if visibility is poor. Repeatability is ~0.5° with care.

**Sequence (one revolution starting at TDC):**

- Rotate downstroke slowly.
  - Note EO when exhaust top edge just uncovers.
  - Note TO when transfer top edges just uncover.
- Continue to BDC (180°).
- Rotate upstroke slowly.
  - Note TC when transfers just cover.
  - Note EC when exhaust top edge just covers.
- Continue toward TDC.
  - Note IC when intake port just covers.
- Past TDC on the downstroke of the next cycle:
  - Note IO when intake port just uncovers.

Each event measured **three times** in succession; report mean and
standard deviation.

## 5. Cross-checking with port heights

For each port, measure with a depth gauge:

- **Port height from cylinder deck to top of port:** `h_top`.
- **Port height from cylinder deck to bottom of port:** `h_bot`.

Given crank throw `r` (half of stroke), rod length `L`, and bore, the
piston crown height above the crank axis at any crank angle θ is:

    y(θ) = r·cos(θ) + √(L² − r²·sin²(θ))

Solve for θ when the crown edge is at `deck_height − h_top` — that's
the port-opening angle. Compare against the measured value from §4.

Agreement to within 1° is expected. Discrepancies indicate either
measurement error or a non-obvious geometry issue (e.g., the piston
crown is not flat, or the rod length wasn't what was assumed).

## 6. Recording

Record all values into a per-cylinder-kit measurement sheet under
`docs/experiments/mechanical/eurocilindro-port-timing.md`:

- Kit identifier and any batch markings.
- Piston type and part number.
- Stroke measured, rod length used.
- Each port event: 3 individual readings + mean + SD.
- Derived durations and blowdown angle.
- Photographs of the port geometry (annotated) and of the assembly.

This measurement is done **once per cylinder kit** and is invariant
unless the piston or crank is changed.

## 7. Implications for the rest of the design

From the measured port timing:

- **Trapped CR calculation** uses EC in the formula
  `trapped_CR = (V_swept_between_EC_and_TDC + V_chamber) / V_chamber`.
  See [head-and-squish §7](head-and-squish.md#7-compression-ratio).
- **Pipe tuning target** uses the exhaust duration:
  optimum RPM for a resonant pipe roughly corresponds to a wave
  return time equal to the exhaust duration in crankshaft time.
  Detailed pipe design deferred to a later doc.
- **Ignition timing curve shape** (phase 4+ mapped timing) is
  informed by port timing: retarded timing at low RPM when short-
  circuit losses through the still-open exhaust matter more; advanced
  at high RPM when combustion phasing dominates.

## 8. Open questions

- The Eurocilindro batch varies between production runs. If a
  second cylinder is ever obtained, re-measure — the number may
  differ by a couple of degrees.
- No modification of port geometry is planned, per constraints. If
  a future ADR reversed this, the measurement procedure here would
  serve as the baseline reference.

## 9. Related

- [Constraints](../project/constraints.md) — no porting modifications
- [Head and squish](head-and-squish.md) — trapped CR depends on EC
- [Staged plan phase 1](../project/staged-plan.md) — measured during
  phase 1 bench work, before assembly
