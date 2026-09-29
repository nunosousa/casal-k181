# Power Distribution Module (PDM) subsystem architecture

Passive hardware unit that concentrates all vehicle power distribution,
protection, and switching. Owned and controlled by the ECU MCU via a
short inter-module cable. Not a CAN node.

Introduced by
[ADR-0008](../project/decisions/0008-separate-power-distribution-module.md).
Follows automotive convention: sealed enclosure with a serviceable
cover exposing blade fuses in ATO holders and ISO 7588 relays in
sockets.

## 1. Purpose and scope

Owns:

- DC bus input from the R/R output.
- Main fuse and reverse-polarity protection.
- Supercap bank (kick-start bus buffer per
  [ADR-0004](../project/decisions/0004-kick-start-flat-battery.md)).
- Battery charging-controller MOSFETs.
- Battery voltage sense divider.
- Per-lamp blade fuses.
- Automotive relays (headlight low, high, horn) in sockets.
- Lamp-drive MOSFETs (front indicators L/R, rear indicators L/R,
  tail, brake).
- **Coil driver IGBT + gate driver + primary current sense** (per
  [ADR-0009](../project/decisions/0009-coil-driver-in-pdm.md)),
  driven by a logic-level trigger from the ECU MCU. If a smart coil
  with integrated driver is selected, this stage reduces to
  logic-level trigger routing only.
- TVS protection on each output.
- Clean DC bus feed to the ECU.
- Switched-rail feed to the handlebar controller.

Does not own:

- Any MCU, firmware, or communication interface. Passive hardware
  only.
- Sensor front-ends — remain in the ECU.
- The ignition coil itself — external component. The PDM provides
  the primary drive; the coil primary wire runs from the PDM's
  vehicle-harness connector to the coil.

## 2. Block diagram

    +-------------------------------------------------------+
    |                        PDM                            |
    |                                                       |
    |  R/R AC in (2 or 3 phase)                             |
    |     |                                                 |
    |     v                                                 |
    |  [Diode-bridge stage — part of shunt R/R]             |
    |     |                                                 |
    |     v                                                 |
    |  DC bus                                               |
    |     |                                                 |
    |     +--- Main fuse (15 A blade, ATO holder) --> bus   |
    |     |                                                 |
    |     +--- Reverse-polarity P-FET ideal-diode           |
    |     |                                                 |
    |     +--- TVS (24 V clamp)                             |
    |     |                                                 |
    |     +--- Supercap bank (~1 F, 15 V rated)             |
    |     |                                                 |
    |     +--- Battery charge FETs <----+                   |
    |     |          |                  |                   |
    |     |          v                  |                   |
    |     |     Battery +               | Charge-drive lines
    |     |     (via reverse-polarity   | from ECU MCU
    |     |      protected feed)       |                    |
    |     |                            |                    |
    |     +--- Clean 12 V out ---------+---> ECU (short cable)|
    |     |                                                 |
    |     +--- Dedicated 12 V for coil driver -----> ECU    |
    |     |                                                 |
    |     +--- Ignition-switched rail out ---> handlebar    |
    |     |                                                 |
    |     +--- Lamp fuse bank (blade holders):              |
    |            HL-low, HL-high, tail+brake,               |
    |            indicators, horn                           |
    |               |                                       |
    |               v                                       |
    |            Lamp drive PCB:                            |
    |              - ISO 7588 relays in sockets             |
    |                (headlight low, high, horn)            |
    |              - N-MOSFETs (indicators, tail, brake)    |
    |              - TVS on each drain / relay contact      |
    |              - Free-wheel diodes on relay coils       |
    |               |                                       |
    |               v                                       |
    |            Vehicle harness connector                  |
    |            (to lamps and horn)                        |
    +-------------------------------------------------------+
                         ^
                         | Control cable (~19 wires) from ECU:
                         | 7 × MOSFET gate drives
                         | 3 × relay coil drives
                         | 2 × charge FET drives
                         | 3 × sense returns
                         | + spare

## 3. Physical layout and connectors

### 3.1 Enclosure

- Aluminium enclosure, ~120 × 80 × 40 mm (approximate, sized during
  hardware design phase).
- **Serviceable cover** — slide-off or hinged, giving access to fuse
  holders and relay sockets without opening the sealed compartment.
- Sealed inner compartment for the lamp-drive PCB and control-signal
  I/O.
- IP54 or better overall. Cover-seal grade lower than main enclosure
  is acceptable because the cover isn't opened in normal riding
  conditions.
- Mounted on the same frame bracket as the ECU where possible.

### 3.2 Connectors

Three connectors on the enclosure:

- **R/R input:** 2-pin (single-phase) or 3-pin (three-phase)
  automotive-sealed connector. Wire gauge 14-16 AWG.
- **ECU control cable:** ~19-pin sealed connector, mini-harness or
  short direct board-to-board coupling if enclosures abut. Wire
  gauge mixed: 20 AWG for the power lines to the ECU, 24 AWG for
  the control and sense lines.
- **Vehicle harness:** ~20-pin sealed connector carrying lamp
  outputs to headlight, front indicators, horn, and rear-going
  lines to tail/brake/rear indicators. Wire gauges 18-20 AWG for
  lamp outputs; ground return may be chassis (short local
  connection).

Battery connections direct to the PDM via ring lugs or a fused
battery link, not through the main harness connector.

## 4. Interconnect signals

### 4.1 Power to ECU

- **Clean 12 V** (fused, reverse-polarity protected, TVS-clamped):
  supplies the ECU MCU rails.
- **Dedicated coil-driver 12 V**: separate line from the DC bus
  (fused separately in the PDM at ~15 A), feeds the ECU's on-board
  coil driver IGBT. Kept out of the MCU rail's return path to
  minimise di/dt coupling.
- **Ground return**: heavy conductor tied to a star point in the
  PDM near the bus-neg reference.

### 4.2 Control lines from ECU

- 7 × N-MOSFET gate drives (front indicator L/R, rear indicator L/R,
  tail, brake, horn if not relay).
- 3 × relay coil drives (headlight low, headlight high, horn if
  relay).
- 2 × charge-controller FET drives (charge FET on, discharge FET on).
- **1 × coil-driver gate command** (logic level, from ECU TIM8
  output compare) — per
  [ADR-0009](../project/decisions/0009-coil-driver-in-pdm.md).

Gate driver ICs live on the PDM PCB, driven by 5 V logic-level
signals from the ECU MCU through the cable.

### 4.3 Sense returns to ECU

- Vbat (battery-side voltage, downstream of charge FETs).
- Vbus (DC bus voltage, upstream of everything).
- Ibat (charge current sense, differential across a small
  shunt).
- **Coil primary current sense** (differential, from shunt monitor
  at the coil driver — see §5.6).
- **Coil primary drain voltage sense** (for post-spark fault
  detection).

Additional optional per-lamp current-sense returns for open-lamp /
short-lamp detection can be added in a later phase.

## 5. Component selection notes

### 5.1 Fuse holders

- ATO/ATM (mini) blade-fuse holders through-hole soldered to the
  PDM PCB, arranged in a row behind the serviceable cover.
- Colour-coded blade fuses per ISO 8820: 5 A (tan), 7.5 A (brown),
  10 A (red), 15 A (blue).

### 5.2 Relays

- ISO 7588 mini-relays (Bosch 0332209150-class or equivalent).
- Sockets on the PDM PCB with barbed retention.
- Three relay positions: headlight low, headlight high, horn.
- Spare socket position for future use.

### 5.3 MOSFETs

- N-channel, logic-level, 10 A / 60 V (IRLZ44N, STP80NF12 or
  automotive-grade equivalent).
- TO-220 or D²PAK package, thermal pad to enclosure or copper pour.

### 5.4 Supercap bank

- Working target: ~1 F effective at 15 V. Realised as two 2.7 V / 3 F
  cells in series with active balancing (LTC3625 or similar), or a
  purpose-built module.
- Physically the largest energy-storage component in the PDM.
  Position central on the PCB for thermal budget spread.

### 5.5 Charge FETs

- Back-to-back N-MOSFETs (or a dedicated H-bridge FET pair) sized
  for ~5 A continuous charge current.
- Gate drive from PDM-local driver IC, controlled by ECU via the
  control cable.

### 5.6 Coil driver

Per [ADR-0009](../project/decisions/0009-coil-driver-in-pdm.md).

- **IGBT:** Bosch BIP373 or STMicroelectronics VB525SP class
  automotive smart-IGBT with integrated Zener clamp at ~380 V.
  Coil primary current ~5-10 A peak, dwell ~2-4 ms.
- **Gate driver:** dedicated non-isolated gate driver IC (TC4420
  or on-IGBT integrated), driven by a 5 V logic signal from the
  ECU (TIM8 output compare).
- **Primary current sense:** ~10-50 mΩ non-inductive shunt in the
  low side of the coil primary path, amplified by an INA240-class
  high-CMRR current monitor. Differential output routed back to
  the ECU via twisted-pair sense return.
- **Drain voltage sense:** attenuated (divider) drain-node voltage
  routed back to the ECU for post-spark fault detection.
- **Star-ground the coil primary return** at the PDM's bus-negative
  reference. Coil-driver ground is kept out of the sensor-return
  path in the interconnect cable.
- **Layout:** coil-driver zone thermally isolated from sense
  circuitry inside the PDM; copper pour under the IGBT; TVS on the
  drain node.

**Smart-coil option:** if the ignition coil chosen for the vehicle
has an integrated IGBT (COP-style), the PDM's coil driver stage
reduces to a logic-level buffer forwarding the ECU trigger to the
coil. Shunt-based current sense may then be omitted (integrated
coils typically self-diagnose). Choice deferred to the ECU / coil-
selection phase.

## 6. Thermal budget

Dominant contributors at cruise (headlight on, 4 A load):

- MOSFETs (lamp drive, ~6 outputs actively conducting): ~2 W
  aggregate.
- Relay coil dissipation (headlight low held on): ~1.5 W.
- Charge FETs at ~3 A charge current: ~0.5 W.
- Reverse-polarity P-FET at 5 A: ~0.5 W.
- TVS quiescent: negligible.
- **Total ~4.5 W** typical, ~7 W with brake pressed and hazard on.

Aluminium enclosure at ~200 cm² surface, 15-25 °C rise expected.
Comfortable margin.

## 7. Serviceability

Designed to allow routine service without breaking the sealed
compartment:

- **Fuse replacement:** slide/hinge off cover, extract blown fuse
  with automotive fuse-puller, insert replacement, close cover.
- **Relay replacement:** same access; unplug relay from socket,
  replace with new ISO 7588 unit.
- **PCB service (rare):** open sealed compartment via captive
  screws, replace PDM PCB as a unit.

Documentation of the fuse map is affixed to the underside of the
serviceable cover.

## 8. Failure modes

- **Blown per-lamp fuse:** loss of that lamp, otherwise no effect.
  ECU can detect via sense returns (post-phase 1).
- **Blown main fuse:** total vehicle power loss. Highly abnormal —
  investigate before replacing.
- **Failed MOSFET (open):** loss of that lamp. Fault detectable
  via sense return; logged.
- **Failed MOSFET (shorted):** lamp on permanently, drives the
  per-lamp fuse. Rare.
- **Failed relay:** loss of headlight or horn. Detected by absence
  of expected current on sense (if instrumented).
- **Failed charge FET (charge stuck on):** battery over-charged;
  BMS trips off, warned by handlebar via ECU CAN.
- **Failed reverse-polarity P-FET:** silent (worst case). Failure
  mode is protection loss, not immediate malfunction.
- **Supercap failure (open):** kick-start bootstrap fails; running
  vehicle unaffected.
- **Supercap failure (shorted):** dead-short on DC bus at boot,
  blows main fuse.
- **Control-cable disconnect:** ECU loses control of all lamps and
  charging. Handlebar warning based on absent CAN sense-return
  feedback (post-phase 1 detection).

## 9. Interaction with the ECU

- ECU firmware treats the PDM as a set of output pins and a set of
  ADC inputs — no discovery, no configuration protocol, no
  handshake.
- The PDM's presence is confirmed indirectly: if control signals
  don't correlate with sense returns (drive charge FETs on but see
  no charge current), ECU logs a PDM-interface fault.
- No firmware component of the PDM. Bootloader complexity, config
  store, and firmware update are all ECU-side concerns.

## 10. Open questions

- **Enclosure supplier and size** — sized during hardware design
  phase.
- **Exact fuse holder and relay socket parts** — automotive-grade
  parts widely available (Molex, TE, Amphenol); specific selection
  during hardware phase.
- **PDM PCB layer count** — likely 2-layer for cost, possibly 4
  for cleaner ground/power planes. Decide during layout.
- **Whether to include per-lamp current-sense** (open-lamp / short-
  lamp fault detection) in phase 1 or defer.
- **Whether the R/R integrates the diode bridge** or that stage
  lives on the PDM. Depends on which R/R model is chosen.

## 11. Related

- [ADR-0008: Separate Power Distribution Module](../project/decisions/0008-separate-power-distribution-module.md)
- [ADR-0004: Kick-start with flat battery](../project/decisions/0004-kick-start-flat-battery.md)
- [ADR-0005: Retain incandescent exterior lamps](../project/decisions/0005-retain-incandescent-exterior-lamps.md)
- [ADR-0007: Lamp drive logic ownership](../project/decisions/0007-lamp-drive-moves-to-ecu.md)
- [System architecture](system.md)
- [ECU subsystem](ecu.md)
- [Power architecture](power.md)
