# ADR-0008: Introduce a separate Power Distribution Module (PDM)

**Status:** Accepted (coil-driver location subsequently refined by [ADR-0009](0009-coil-driver-in-pdm.md))
**Date:** 2026-09-29

## Context

[ADR-0007](0007-lamp-drive-moves-to-ecu.md) moved the exterior lamp
drive (MOSFETs, relays, per-lamp fuses) into the ECU enclosure, on
the ECU PCB. The user challenged this on automotive-practice
grounds. The critique stands:

- Blade fuses on a sealed ECU PCB are not serviceable in the way
  automotive fuses are supposed to be.
- ISO 7588 automotive relays are physically bulky (~25 mm cubes)
  and are wear items with sockets and replaceability in real
  vehicles.
- Coil-driver di/dt + relay contact bounce + lamp-switching
  transients on the same PCB as Hall inputs, thermocouple front-
  ends and IMU is not what automotive designers do.
- ECU replacement cost inflates if the same PCB carries the
  lamp-drive stage.
- Real vehicles physically separate ECU from body/power distribution.

## Decision

Introduce a distinct **Power Distribution Module (PDM)** as a
separate physical enclosure, located adjacent to the ECU on the same
frame bracket (or nearby with a short mini-harness).

**PDM is not a CAN node.** It is passive hardware controlled by the
ECU MCU via short low-current control lines. ADR-0001's two-node
CAN topology is unchanged.

### What lives in the PDM

Power distribution and protection:

- Main fuse (~15 A blade) on the DC bus input from the R/R.
- Reverse-polarity protection (P-MOSFET ideal-diode) on the DC bus.
- TVS + EMI filter on the DC bus input.
- Supercap bank (~1 F, 15 V-rated) buffering the DC bus for
  ADR-0004 kick-start bootstrap.

Battery interface:

- Charging-controller MOSFETs (charge and discharge FETs, ECU-driven).
- Battery voltage sense divider.

Lamp drive stage:

- **Per-lamp blade fuses** in accessible ATO/ATM holders behind the
  PDM service cover.
- **ISO 7588 automotive relays in sockets** — headlight low,
  headlight high, horn. Replaceable without soldering.
- **N-MOSFETs** on the lamp-drive PCB — front indicator L/R, rear
  indicator L/R, tail, brake. TVS on each output. Free-wheel diodes
  on relay coils.

Output to vehicle harness:

- Clean DC bus feed to the ECU (short cable).
- Switched-rail feed to the handlebar controller.
- Lamp outputs to headlight, front indicators, horn, rear tail,
  rear brake, rear indicators.

### What lives in the ECU (unchanged from before ADR-0007)

- MCU (STM32H723ZG) and its rails.
- Sensor front-ends (Hall, thermocouple, ADC, I2C, SPI).
- Coil driver IGBT + gate driver + primary sense.
- SPI NAND log storage.
- CAN transceiver + service USB.
- Small TVS on the incoming clean-12 V feed from the PDM (main
  protection is upstream in the PDM).
- Lamp control logic and blink timing (as introduced in ADR-0007):
  logic stays with ECU MCU, physical switching happens in the PDM.
- Charge controller drive logic (as ADR-0004): logic stays with
  ECU MCU, physical FETs live in the PDM.

### Interconnect

Short ECU ↔ PDM cable (~10-30 cm) with roughly 19 conductors:

- 2 × power (clean 12 V + GND to ECU MCU side)
- 1 × dedicated bus feed for coil driver
- 7 × MOSFET gate drives (one per lamp channel)
- 3 × relay coil drives (headlight low, high, horn)
- 2 × charge FET drives (charge, discharge)
- 3 × sense returns (Vbat, Vbus, charge current)
- 1 × spare/reserved

Board-to-board connector option if the two enclosures are bolted
together directly.

## Consequences

Positive:

- **Serviceability.** Fuse and relay replacement without opening
  the ECU. Slide-off PDM cover, blade fuses in ATO holders, relays
  in sockets — standard automotive experience.
- **EMI cleanliness.** Coil-driver + relay bounce + lamp switching
  are all outside the sensor-front-end enclosure. Better analog
  measurements.
- **ECU shrinks and simplifies.** Back to sensor-and-timing focus.
- **PDM replaceable independently.** If a MOSFET or relay fails,
  swap the PDM PCB. Doesn't touch the ECU.
- **Aligns with automotive convention.** Anyone opening the vehicle
  finds a layout that matches expectation.
- **Thermal budget on the ECU drops** back to ~5 W typical from the
  ~7 W ADR-0007 revised figure.

Negative:

- **Two enclosures instead of one** — extra mechanical work, one
  more sealed connector, one more mounting bracket.
- **~19-line inter-module cable** — connector cost, harness
  complexity between the two modules. Mitigated by co-locating them
  on the same frame bracket.
- **PDM is a new dependency for the ECU.** ECU can't get power
  without a functional PDM. This is intrinsic to any junction-box
  architecture and matches real vehicles.
- **HIL rig needs to accommodate PDM as a distinct unit under test.**

## Alternatives considered

- **Lamp drive on the ECU PCB** (previous ADR-0007 as written).
  Rejected on the grounds detailed in the Context section.
- **Two internal compartments inside a shared enclosure.**
  Considered as a middle ground — a single aluminium box with an
  internal bulkhead separating electronics from power switching.
  Rejected as still constraining serviceability (main cover would
  need to open to reach fuses; opening it exposes ECU as well).
- **Split lamp drive between ECU and a rear-mounted PDM.**
  Rejected — one physical distribution point is simpler.
- **Complete integration of all high-current stuff (lamps, coil
  driver, charging) into the PDM.** Rejected for the coil driver
  only — coil timing benefits from MCU proximity. Charge FETs and
  supercap can be in PDM without hurting timing.

## Relation to prior ADRs

- **[ADR-0001](0001-two-node-can-topology.md)** unchanged. Two-node
  CAN topology preserved because the PDM is not a node.
- **[ADR-0004](0004-kick-start-flat-battery.md)** — the supercap
  and charging arrangement relocate into the PDM but the topology
  is unchanged.
- **[ADR-0007](0007-lamp-drive-moves-to-ecu.md)** — the logic
  ownership decision (ECU MCU owns lamp state and blink timing)
  stands. The physical location of the switching hardware is
  refined here.

## Related

- [PDM subsystem](../../architecture/pdm.md) — new
- [System architecture](../../architecture/system.md) — updated
- [ECU subsystem](../../architecture/ecu.md) — reverted to
  pre-ADR-0007 scope for drive components
- [Power architecture](../../architecture/power.md) — updated
