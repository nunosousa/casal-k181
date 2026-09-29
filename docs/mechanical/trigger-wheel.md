# Crank trigger wheel design and installation

Physical design and installation procedure for the 36-1 trigger wheel
that provides crank position to the ECU. Referenced by
[ECU §5.1](../architecture/ecu.md) and
[HIL §3.1](../architecture/hil.md).

## 1. Pattern and geometry

- **Pattern:** 36-1 (35 teeth + one missing at the sync position).
- **Tooth angular pitch:** 10° (36 × 10° = 360°).
- **Angular resolution:** 10° raw between teeth; sub-tooth interpolation
  in firmware to < 1°.
- **Sync marker:** the missing-tooth position corresponds to a specific
  crank angle relative to TDC. The offset from the missing-tooth
  sync marker to TDC is calibrated at installation (see §7) and
  stored in the ECU config store as `sync_offset_deg`.

## 2. Wheel geometry

- **Outer diameter:** 50-60 mm (final value pinned to available K181
  flywheel-face real estate).
- **Wheel thickness:** 3-5 mm.
- **Tooth radial depth:** 5 mm from the OD.
- **Tooth angular width:** ~5° (linear tooth width ~2.5 mm at OD
  50 mm).
- **Gap angular width:** ~5° between teeth.
- **Bore or mounting features:** dictated by the chosen mounting
  method (§4).

## 3. Material and fabrication

**Material:** low-carbon steel (mild steel, 1018, or 4130). Ferrous
target required — the SS411A Hall sensor uses an integrated bias
magnet and senses modulation of that field by a ferrous tooth passing
near it.

Rejected:

- Aluminium — non-ferrous, no Hall signal modulation.
- 3D-printed plastic (as a final part) — non-ferrous, low durability.
  OK as a fit-check prototype only.

Fabrication, in order of preference:

1. **Waterjet cut** from 4 mm plate. Precision ~± 0.05 mm, clean
   edges, no heat-affected zone.
2. **Laser cut** from 3 mm plate. Similar precision, small edge HAZ.
3. **CNC milled** from plate. Best precision, higher cost.
4. **3D printed** in PLA/ABS — bench prototype only, not installed
   on the engine.

Post-processing:

- Deburr all edges.
- Light black-oxide finish for corrosion resistance in the magneto
  environment (mildly humid, oil-misted).

## 4. Tolerances

| Parameter | Tolerance |
|---|---|
| Tooth-to-tooth angular pitch | ± 0.1° |
| Wheel OD concentricity to mounting bore | ± 0.05 mm TIR |
| Axial runout on mounted assembly | ± 0.1 mm |
| Sensor air gap (nominal at install) | 1.0-2.0 mm |
| Sensor air gap (operational range) | 0.5-3.0 mm |

## 5. Mounting

The 36-1 wheel mounts on the outer face of the **new modern rotor**
supplied with the VAPE-class 12 V magneto replacement kit
(see [ADR-0006](../project/decisions/0006-modern-magneto-replacement.md)).
The stock K181 flywheel is not retained.

Two candidate mounting methods; final choice pinned after physical
inspection of the received rotor.

### 5.1 Option A: retaining-compound bonded ring on outer rotor face

- **Adhesive:** Loctite 638 or 620 retaining compound. High-strength,
  oil-tolerant, thermal-stable to > 150 °C.
- **Surface prep:** both mating faces cleaned to bare metal with
  acetone; light cross-hatch abrasion (Scotch-Brite grade A or 240
  grit).
- **Concentricity:** align on a purpose-made mandrel jig that
  registers off the rotor's centre bore; apply light axial pressure
  during cure (24 h cure).
- **Reversibility:** heat to > 200 °C to release. Preserves the rotor
  for future work.

### 5.2 Option B: mechanical fastening via a machined adapter

- **Adapter:** aluminium hub bolted to the rotor through an
  accessible bolt pattern (verify presence at inspection of the
  received rotor).
- **Trigger wheel:** bolted to the adapter with 3 × M4 through
  clearance holes on the wheel and tapped holes in the adapter.
- **Trade-off:** higher precision, serviceable, higher cost.

**Provisional plan:** Option A unless the received rotor offers a
convenient bolt pattern or the VAPE integrated trigger tab
interferes with a bonded ring.

### 5.3 VAPE integrated trigger

The VAPE rotor typically ships with an integrated trigger feature
(single tooth or magnet) intended for the VAPE ignition CDI. We do
not use that trigger. Two disposition options:

- **Leave in place** if it does not interfere with the 36-1 wheel
  mounting or with the Hall sensor bracket. Simplest.
- **Physically remove** (machine off) if it interferes. Requires care
  not to unbalance the rotor.

Physical inspection of the received rotor determines the choice.

## 6. Sensor bracket

- **Sensor:** Honeywell SS411A (or Melexis US5881, or equivalent
  chopper-stabilised Hall with digital push-pull output and
  integrated bias magnet).
- **Bracket:** 6 mm aluminium plate, machined slot for sensor body,
  bolted to a crankcase boss.
- **Mounting boss:** either an existing tapped hole on the crankcase
  or a drilled-and-tapped M5 hole. Location depends on physical
  clearance between the flywheel outer face and the crankcase.
- **Air-gap adjustment:** shims under the bracket base *or* an
  elongated slot allowing radial position adjustment. Prefer shims —
  more stable long-term.
- **Sensor lead:** shielded, twisted-pair or triaxial, ~30-50 cm to
  ECU harness connector.

## 7. Sync-offset calibration procedure

Every trigger-wheel installation must have its sync offset measured
and stored before the engine is run. This is the single number that
lets the ECU relate "missing tooth passing the Hall" to "crank at
X degrees relative to TDC."

**Required tools:**

- Piston-stop tool (screws into sparkplug hole, contacts piston crown
  before TDC).
- Degree wheel (large — ≥ 150 mm — temporarily mounted on the crank
  end opposite the trigger wheel).
- Fixed pointer aligned to the degree wheel.
- Fine-tip marker.
- Laptop with the ECU service tool showing live crank angle.

**Procedure:**

1. Install piston, rod, crank, flywheel, and trigger wheel.
2. Leave the cylinder head off — the piston must be visible.
3. Rotate the crank so the piston is well below TDC.
4. Screw the piston-stop tool into the sparkplug hole.
5. Rotate the crank *slowly* in the normal running direction until
   the piston contacts the stop. Record the degree-wheel reading as
   α₁.
6. Rotate the crank in the *reverse* direction until the piston
   contacts the stop from the other side. Record the reading as α₂.
7. True TDC on the degree wheel is (α₁ + α₂) / 2.
8. Remove the piston stop.
9. Rotate the crank to the calculated TDC position.
10. In the ECU service session, read the live-data field
    `crank_angle_since_sync_deg`. This is the sync offset — the angle
    between the missing-tooth sync marker and TDC.
11. Write the value to the ECU config store as `sync_offset_deg` via
    the service tool.

**Sanity check:** rotate to BDC (180° from TDC on the degree wheel);
`crank_angle_since_sync_deg` should read `(sync_offset_deg + 180)
mod 360`, within ± 0.5°.

Store to 0.1° precision. Re-calibrate any time the trigger wheel or
its bracket is disturbed.

## 8. Verification on the bench (HIL)

Before final installation, verify the trigger wheel on the HIL bench
per [HIL §6.2](../architecture/hil.md#62-trigger-and-timing). The rig
spins the wheel at a range of RPMs; the scope confirms 36 pulses per
revolution with the missing-tooth pattern visible, and firmware
reports sync acquired.

## 9. Open questions

- **Final mounting method** (bond vs. adapter) — pinned after
  received rotor is physically inspected.
- **Disposition of the VAPE integrated trigger tab** — leave in
  place or machine off; decided at rotor inspection.
- **Whether the VAPE rotor's outer face is amenable to retaining-
  compound bonding.** VAPE rotors are typically machined steel or
  cast — normally fine with Loctite 638 — but verify with the
  supplier or by test on a scrap surface.

## 10. Related

- [ECU subsystem §5.1](../architecture/ecu.md)
- [HIL bench §3.1](../architecture/hil.md)
- [ADR-0002: Skip mechanical points](../project/decisions/0002-skip-mechanical-points.md)
- [ADR-0006: Modern magneto replacement](../project/decisions/0006-modern-magneto-replacement.md)
- [Staged plan phase 1](../project/staged-plan.md)
