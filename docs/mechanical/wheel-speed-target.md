# Front wheel speed target and sensor

Physical design and installation of the front-wheel speed target ring
and Hall sensor bracket. Referenced by
[ECU §5.2](../architecture/ecu.md) and used for both real-time
display (via CAN to the handlebar's speedometer) and coastdown /
acceleration analysis (see [measurement plan §3](../measurement-plan.md)).

## 1. Design objectives

- **Speed range covered:** 0.5 m/s (walking pace, needed for
  coastdown tail) to 25 m/s (~90 km/h, above operational envelope).
- **Speed resolution:** ≤ 0.1 km/h at the reading, adequate for
  coastdown fits and acceleration analysis.
- **Undriven wheel:** always the front wheel — no slip, no torque
  artefacts, no chain wind-up.
- **Mounting robustness:** survives braking heat, road grime, and
  years of use.

## 2. Tooth count

Trade-off: more teeth → better resolution at low speed but higher
event rate at high speed. Wheel circumference for a typical Casal
K181 front wheel is ~1.5 m.

| Teeth | Low-speed period at 0.5 m/s | High-speed rate at 25 m/s |
|---|---|---|
| 12 | 250 ms | 200 Hz |
| 24 | 125 ms | 400 Hz |
| 32 | 94 ms | 533 Hz |
| 48 | 62 ms | 800 Hz |

- 12 teeth is too few — low-speed period near 250 ms makes velocity
  updates during the coastdown tail noticeably chunky.
- 48 teeth is unnecessary — 800 Hz is well within timer capability
  but the packaging becomes tight.

**Chosen: 24 teeth.** Sweet spot for both speed regimes. Packaging
easy on a drum-brake hub. Low-speed period 125 ms allows ~8
velocity updates per second at walking pace — enough for coastdown.

## 3. Target-ring geometry

- **Outer diameter:** 100-150 mm (final value depends on the K181
  drum-brake outer face geometry — inspected at disassembly).
- **Ring thickness:** 3 mm.
- **Tooth radial depth:** 5 mm.
- **Tooth angular width:** ~7.5° (half the 15° pitch of a 24-tooth
  pattern).
- **Bore:** clearance-fit over the wheel-hub mounting circle, with
  pilot lugs or bolt-through pattern (see §5).

## 4. Material and fabrication

- **Material:** low-carbon steel (mild steel, 1018) or stainless.
  Ferrous target required.
- **Stainless preferred** for corrosion resistance in the road-spray
  environment.
- **Fabrication:** waterjet or laser from 3 mm plate. Same rationale
  as [trigger-wheel §3](trigger-wheel.md).
- **Post-process:** deburr, passivate stainless or black-oxide mild
  steel.

## 5. Mounting

The K181 front wheel almost certainly has a **drum brake** (era-
typical). The target ring bolts or bonds to the drum's outer face.

### 5.1 Preferred: mechanical fastening

- **Small M4 bolts** through the target ring into tapped or drilled-
  and-tapped holes in the drum outer face.
- Bolt count: 3 or 4 evenly spaced.
- **Serviceable, exact concentricity.**
- Requires a small amount of drum machining (drill + tap or
  through-hole + nut on the back side).

### 5.2 Alternative: retaining-compound bonded

- Same Loctite 638 process as [trigger wheel §5.1](trigger-wheel.md).
- Simpler, non-invasive to the drum.
- Concern: brake drums get warm — sustained braking on a downhill
  descent could see 100-150 °C at the drum face. Loctite 638 operates
  to 150 °C but is close to margin. Not the first choice.

**Provisional plan:** mechanical fastening. Machine 4 × M4 tapped
holes at 90° spacing on the drum outer face.

## 6. Tolerances

| Parameter | Tolerance |
|---|---|
| Tooth-to-tooth pitch | ± 0.2° |
| Ring concentricity to wheel axis | ± 0.1 mm TIR |
| Axial runout | ± 0.2 mm |
| Sensor air gap (nominal) | 1.0-2.0 mm |
| Sensor air gap (operational range) | 0.5-3.5 mm |

## 7. Sensor bracket

- **Sensor:** Honeywell SS411A (or Melexis US5881, or equivalent
  Hall with integrated bias magnet).
- **Bracket:** aluminium 4 mm plate, elongated slot for radial
  position adjustment, clamped to the fork lower via a hose-clamp
  or bolted to an existing bracket lug on the fork lower.
- **Sensor position:** aimed radially inward at the target ring's
  OD, air-gap set with feeler gauges at install.
- **Sensor lead:** shielded, twisted-pair, routed along the fork with
  the brake cable, ~50-70 cm to the frame-side harness connector.

## 8. Calibration

- **Circumference measurement:** roll the front wheel through one
  revolution against a taut chalk-line on a level surface. Measure
  the mark-to-mark distance. Repeat 3× and average.
- **Wheel circumference** stored in the ECU config store as
  `front_wheel_circumference_mm`.
- **Vehicle speed** is computed as `circumference * teeth_per_second /
  24` (teeth per second measured directly from the Hall timer capture).
- **Re-calibrate** after any tyre change or pressure change > 0.2 bar
  from the calibrated pressure.

## 9. Verification

- **On the bench:** spin the wheel by hand while watching the ECU's
  live wheel-speed reading. Verify no missed edges, consistent
  reporting.
- **On the road at low speed:** roll at a measured walking pace over
  a known distance; verify the ECU's reported speed and integrated
  distance match.
- **On the road at cruise speed:** cross-check ECU wheel speed
  against GPS speed on a straight run. Agreement to within GPS
  accuracy (~0.1 m/s) required.

## 10. Failure modes and diagnostics

- **Ring loose:** slight vibration produces spurious edges. Detected
  as impossible high-frequency events; logged.
- **Sensor gap opens:** signal amplitude decreases below the Hall's
  switching threshold. Detected as missing edges; if persistent,
  logged as sensor fault.
- **Sensor lead damaged:** intermittent or lost signal. Logged.

The ECU cannot detect ring installation errors (wrong tooth count,
wrong tooth pitch) beyond gross geometry-mismatch checks against the
calibrated circumference. Installation must be visually verified
tooth count.

## 11. Open questions

- **Actual K181 front-wheel geometry** — drum brake vs. disc; drum
  outer-face diameter and mounting-hole feasibility — determined at
  physical inspection.
- **Whether to co-locate with an existing brake-related sensor** —
  irrelevant; the K181 has none in this era.

## 12. Related

- [ECU subsystem §5.2](../architecture/ecu.md)
- [Measurement plan §3.1](../measurement-plan.md) (coastdown depends
  on this)
- [HIL §3.1](../architecture/hil.md) — bench emulation via square-
  wave generator
- [Trigger wheel](trigger-wheel.md) — companion doc; sensor selection
  matches
