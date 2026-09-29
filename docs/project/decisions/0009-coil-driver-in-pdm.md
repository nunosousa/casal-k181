# ADR-0009: Move coil driver from ECU to PDM

**Status:** Accepted
**Date:** 2026-09-29

## Context

[ADR-0008](0008-separate-power-distribution-module.md) introduced
the PDM to hold all high-current switching hardware — with one
explicit carve-out for the coil driver, which was kept in the ECU
under the claim that "coil timing benefits from MCU proximity."

That claim doesn't survive scrutiny. The STM32H7's output compare
timer commands the IGBT gate at exact microsecond timing regardless
of whether the wire from the timer pin to the gate is 30 mm of PCB
trace or 30 cm of shielded cable. Propagation delay difference is a
few nanoseconds; timer resolution is microseconds. Timing precision
is unaffected by IGBT physical location.

Meanwhile, coil driver on the ECU PCB has real costs:

- 5-10 A pulsed primary current on the ECU PCB generates EMI that
  couples into Hall inputs, thermocouple front-ends, IMU and ADCs.
- Coil primary wire from ECU to external coil is a long high-di/dt
  run in the harness — an unnecessary EMI antenna.
- IGBT is a wear/failure item. On the ECU PCB it is not
  field-replaceable; in the PDM's replaceable-PCB envelope it is.

OEM automotive practice is either **coil-on-plug with integrated
IGBT** (IGBT inside the coil, ECU sends logic-level trigger) or a
**separate ignition module** near the coil. Coil driver on the main
control-module PCB is an aftermarket compromise, not standard.

## Decision

Move the coil driver from the ECU to the PDM.

Specifically:

- **IGBT + gate driver** relocate from the ECU PCB to the PDM PCB,
  alongside the lamp drive stage and charge FETs.
- **Primary current sense** (shunt + shunt monitor IC) relocates to
  the PDM; the sensed differential signal travels back to the ECU
  via the inter-module cable for MCU ADC capture.
- **Drain voltage sense** (for post-spark fault detection)
  relocates similarly.
- **Coil primary wire** exits the PDM's vehicle harness connector,
  not the ECU's — runs from PDM to the external ignition coil.

Add 4 signals to the ECU ↔ PDM interface cable:

- Gate-drive command (logic level, from MCU TIM8 output compare).
- Primary current sense return (differential pair, twisted).
- Drain voltage sense return (single-ended).
- One spare.

Total ECU ↔ PDM cable is now ~23 lines (was 19 in ADR-0008).

### Smart-coil option

If a modern ignition coil with integrated IGBT driver is selected
(coil-on-plug style, or a VAPE-supplied unit with integrated
electronics), the driver hardware moves into the coil itself and the
PDM only routes a logic-level trigger + return sense. Decision
deferred to the ECU schematic / coil-selection phase; either coil
type fits this ADR because the ECU sees only logic-level signals in
both cases.

## Consequences

Positive:

- **ECU is now a clean small-signal environment** — no >100 mA
  switching on-board. Hall, thermocouple, IMU and ADC measurements
  benefit.
- **Coil-driver IGBT is field-replaceable** in the PDM's
  replaceable-PCB envelope.
- **All high-current stuff physically co-located** in the PDM,
  consistent with ADR-0008.
- **Smart-coil option remains open** with no re-architecture cost.

Negative:

- 4 additional signal lines in the ECU ↔ PDM interface cable.
  Modest.
- **Primary current sense signal traverses a cable.** Noise pickup
  risk mitigated by differential sensing at the PDM (INA240-class
  shunt monitor) and twisted-pair signal return.
- The coil primary wire from PDM to coil still exists and still
  carries high di/dt; just doesn't originate at the ECU. Route as a
  short, direct run — the PDM is deliberately located near the
  battery, and the coil is near the engine, so the wire length is
  comparable to the ECU-to-coil run it replaces.

## Alternatives considered

- **Keep driver in ECU** (ADR-0008's original carve-out). Rejected
  as detailed in Context. Timing-proximity argument doesn't hold.
- **Smart coil (integrated IGBT) only.** Reserved as complementary,
  not exclusive. If a smart coil is sourced, the PDM's coil-driver
  stage becomes minimal (just logic-level trigger routing).
- **Standalone ignition module in a fourth enclosure near the
  coil.** Rejected — introduces a fourth vehicle-level enclosure
  for one small function; the PDM is close enough and already
  services other high-current loads.

## Relation to prior ADRs

- **[ADR-0008](0008-separate-power-distribution-module.md)** — the
  coil-driver carve-out in ADR-0008 is superseded by this ADR.
- **[ADR-0002](0002-skip-mechanical-points.md)** unchanged — the
  ECU still owns ignition control; only the physical IGBT moved.
- **[ADR-0004](0004-kick-start-flat-battery.md)** unchanged — cold-
  boot budget is unaffected.

## Related

- [ADR-0008: Separate Power Distribution Module](0008-separate-power-distribution-module.md)
- [PDM subsystem](../../architecture/pdm.md) — updated with coil-
  driver section
- [ECU subsystem](../../architecture/ecu.md) — coil-driver section
  reduced
