# Power and electrical architecture

Vehicle-level power system. Covers charging source, battery, distribution,
regulation, protection, load budget, and battery-independent kick-start
capability.

Some decisions here are provisional pending measurements on the actual
K181 stator, which must be characterised on the bench before the
regulator/rectifier is designed.

## The original K181 power situation

The Casal M151 has an integrated flywheel magneto. A rotating magnet on
the flywheel induces AC in one or more stator coils. In the original
vehicle:

- Ignition coil generates HT for the sparkplug via mechanical points.
- A separate lighting coil directly powers the headlight (AC).
- No rectifier, no battery, no regulation. Voltage varies with RPM.
- System voltage is nominally low (likely 6 V-class, to be confirmed by
  measurement).

The modernised system diverges from all of the above.

## Design objectives

- 12 V DC modernised electrical system.
- ECU can be kick-started with a flat main battery
  (see [ADR-0004](../project/decisions/0004-kick-start-flat-battery.md)).
- Battery is present and functional in normal use, but not required to
  boot the ECU during starting.
- Sunday-rideable in real weather; sealed enclosures, IP-rated
  connectors.

## Modernised system — architecture

Nominal system voltage: **12 V DC**. Modernised because 12 V is where
LED lighting, ECU components, GPS modules and MOSFET drivers are cheap
and well-supported.

Block-level:

    +----------------------+
    | Flywheel magneto     |
    |  (stator coils, AC)  |
    +----------+-----------+
               |
               v (AC, RPM-dependent)
    +----------+-----------+
    | Shunt-type R/R       |  Passive rectifier + MOSFET shunt.
    |  AC -> DC bus        |  Rectifier stage works even with MOSFET
    |  Regulated to 14.4 V |  control unpowered.
    +----------+-----------+
               |
               v (DC bus)
    +----------+-----------+
    | Supercap bank (~1 F, |  Buffers DC bus. Sized so a handful of
    |  15 V rated)         |  kicks bring bus above ECU brownout.
    +----------+-----------+
               |
               +--> Main fuse (~10 A) --> DC bus (distribution point)
                        |
                        +--> ECU (via own fuse, ideal-diode input)
                        |
                        +--> Battery charging controller
                        |         |
                        |         v
                        |     LiFePO4 3-4 Ah battery
                        |     (back-feeds bus through controlled path
                        |      when bus < Vbat, else charges from bus)
                        |
                        +--> Ignition switch
                                 |
                                 v
                          +--------------------+
                          | Switched 12V rail  |
                          +---+------------+---+
                              |            |
                              v            v
                        Handlebar    Rear lamps
                        controller

Key architectural points, expanded below:

- The DC bus is the main rail. It is fed by the R/R output and buffered
  by the supercap.
- The battery is *not* directly on the bus. A charging controller
  arbitrates: charge current bus→battery when bus is above the
  charging setpoint; back-feed battery→bus when bus droops below Vbat.
- All loads run off the bus, either directly (ECU) or via the ignition
  switch (everything else).
- With a flat battery, kicking spins the stator, the passive rectifier
  charges the supercap, the ECU boots off the supercap and fires spark.

## Charging source

**Working plan: keep the original stator.** Rebuild with new insulation
if needed; do not replace with an aftermarket PMA unless bench
measurements show the original cannot sustain the running load budget.

Rationale:

- The stator is integral to the flywheel magneto. Replacing it with a
  PMA implies replacing the flywheel and rebuilding the entire ignition
  mechanical arrangement.
- Character-preservation constraint favours retaining the original
  stator.
- Load budget suggests the original stator is marginal but likely
  adequate with LED-only lighting.

**Bench measurements required before finalising R/R selection:**

- Stator open-circuit AC voltage vs. RPM, from idle down to kick speeds
  (~400-800 RPM).
- Stator short-circuit AC current vs. RPM, over the same range.
- Compute deliverable DC power at 14.4 V (running) and at 9 V (worst-
  case cold-start bus voltage) across the RPM range.

The low-RPM measurement is critical for the ADR-0004 kick-start
requirement — supercap sizing is driven by how much energy per kick the
stator can deliver into the passive rectifier.

## Regulator/rectifier

**Shunt-type MOSFET R/R.** Specifically: passive diode bridge on the
input, with MOSFETs shunting excess AC to ground when the DC output
exceeds the setpoint.

Rejected: series-type MOSFET regulators (MOSFETs act as controlled
rectifiers). Series topologies fail closed — no output if the
controller is unpowered. Incompatible with the ADR-0004 goal of
bootstrapping the ECU from a dead-vehicle state.

Off-the-shelf candidates: Shindengen SH847-class or comparable
aftermarket MOSFET R/Rs marketed as "shunt type" or "MOSFET shunt." Some
motorcycle R/Rs are internally series-type despite MOSFET marketing —
verify topology before purchase.

Setpoint: 14.4 V bus voltage. Overvoltage crowbar at 15.5 V to protect
downstream electronics.

## Battery

**Chemistry: LiFePO4** (LFP). See ADR-0004 rationale for the
battery-plus-supercap arrangement.

LFP characteristics that matter here:

- Nominal ~13.2 V (4S). Maps cleanly to a 12 V-nominal system.
- Charge acceptance from ~13.4 V; float at ~13.6–13.8 V. Sits well
  below the 14.4 V bus setpoint.
- ~2000+ cycles to 80 % capacity.
- Tolerates high pulse discharge (relevant for coil driver in
  battery-powered mode).
- Low self-discharge (~2 % per month), so multi-month standing periods
  don't necessarily flatten it.

Sizing:

- ECU running: ~0.5 A.
- Handlebar controller + illumination + steppers: ~0.3 A.
- Ignition coil at idle (~3000 RPM, ~50 sparks/s, ~30 mJ/spark): ~0.1–
  0.2 A time-average.
- LED headlight low beam: ~0.5–1.0 A.
- LED tail + indicators: intermittent, negligible average.

Running load: ~1.5–2.5 A depending on lights. Standby load (parked but
ignition off): ~5 mA for ECU real-time clock and log preservation.

Battery capacity: **3–4 Ah nominal**. Overkill by a comfortable margin
given the supercap-buffered kick-start capability. Small enough (~250 g)
to fit the original battery box.

**Battery management:** built-in BMS on the LFP pack. Cell-level
balancing, low-voltage cutoff, high-temperature cutoff, short-circuit
protection.

## Supercap bank

**Purpose:** buffer the DC bus so the ECU can boot from stator-only
power during a kick-start with a flat battery.

**First working target:** ~1 F effective at 15 V rating. Realised as
two 2.7 V / 3 F cells in series with active balancing, or a purpose-
built module. Actual sizing pinned by the low-RPM stator measurement.

**Sizing math (order of magnitude):**

- ECU cold-boot current: ~500 mA at bus ~9 V.
- ECU time from stable rail to "ready to fire spark": target ≤ 100 ms.
- Energy needed to boot: ~0.5 A × 9 V × 0.1 s ≈ 0.45 J.
- Energy stored in 1 F between 9 V and 14 V: ½ × 1 × (14² - 9²) =
  57.5 J.
- Comfortable margin. Real driver is how much energy the stator can
  push into the cap during the low-RPM part of a kick.

**Placement:** on the ECU-side of the main fuse, on the DC bus.
Physically inside the ECU enclosure so its state is monitored by the
ECU (voltage, temperature). Supercap failure is a service item.

**Balancing:** active balancing IC (e.g. LTC3625 class) or a
dedicated supercap module with balancing built in.

## Battery charging controller

**Purpose:** decouple battery from bus. Charges battery when bus is
above ~14 V; permits controlled back-feed from battery to bus when bus
droops below Vbat.

Implementation options (choose during ECU schematic phase):

- Dedicated battery-management IC with charge/discharge FETs (e.g.
  BQ25xxx class).
- Discrete: MOSFET switches gated by ECU based on measured bus and
  battery voltages. More flexible, requires firmware.

Discrete is preferred because it lets the ECU log detailed charge/
discharge behaviour and adjust policy in firmware. Cost: more ECU code
to write and verify.

## Distribution and protection

- **Main fuse** in the bus-to-distribution line: ~10 A blade.
- **Per-node fuses:** ECU on its own 5 A fuse from the bus, ideal-diode
  input protection. Handlebar controller on the switched rail via its
  own 5 A fuse. Headlight, tail lamps, indicators — each on the
  switched rail via its own 1–3 A fuse.
- **Reverse polarity protection:** P-channel MOSFET ideal-diode on the
  ECU input. Zero forward drop, protects the ECU if the bus is ever
  reversed during service.
- **Transient protection:** TVS diode at each MCU-bearing node's input,
  clamping above ~24 V.
- **Ignition switch:** cuts the switched rail, not the bus-to-ECU line.
  ECU stays powered momentarily to flush logs then goes to sleep,
  drawing only the ~5 mA standby from the bus.

## ECU internal rails

- **Bus input (8–16 V nominal)** with reverse-polarity ideal-diode, TVS
  clamp, EMI input filter.
- **5 V rail** via a synchronous buck (TPS54xx class). Powers sensors
  (Hall for wheel and crank, TPS, thermocouple amps). Buck must have
  dropout margin down to 8 V input.
- **3.3 V rail** via LDO from 5 V: MCU, IMU, BME280, SPI flash, CAN
  transceiver.
- **Isolated coil-driver gate drive:** not required unless coil chassis
  is not HV-isolated from vehicle ground (verify with chosen coil).

**Startup sequencing** matters more than in a battery-only design.
When bus rises past ~8 V, the buck must start, the MCU must reset, the
bootloader must run, the application must start, and the coil driver
must be armed — all before the flywheel's kick-momentum decays. Total
budget from stable rail to armed: ≤ 100 ms.

## Coil driver — power notes

Unchanged from a battery-powered design; captured here for
completeness.

- Coil primary current: ~5–10 A peak during dwell, decaying to zero
  post-spark. Duration ~2–4 ms.
- Low-side IGBT rated for ~400 V (fly-back), ~20 A pulsed. Bosch BIP373
  or STMicroelectronics VB525SP-class parts with integrated Zener
  clamps.
- **Star-ground the coil.** High di/dt makes it the noisiest point in
  the whole system. Ground return goes directly to the battery/bus
  negative terminal, not shared with sensor grounds.
- **Sense on the driver:** ECU reads gate-drive voltage and primary
  current (small sense resistor or Hall). Free diagnostic channel for
  later spark-energy characterisation.

## Load shedding and low-battery behaviour

- ECU broadcasts bus voltage and (separately) battery voltage on CAN at
  10 Hz.
- Handlebar controller warns below ~12.5 V on either.
- Below ~12.0 V, illumination reduces, non-essential loads drop.
- ECU continues firing ignition as long as its 3.3 V rail is stable.
  Brownout threshold ~8 V on the bus input.

## Failure modes

- **Flat battery (any cause):** vehicle can still be kick-started via
  supercap bootstrap. Once running, R/R charges bus; charging
  controller arbitrates whether to also charge battery. Rider notified
  via CAN warning that battery is unhealthy.
- **BMS-tripped battery:** same as flat battery — kick-start still
  works.
- **Battery entirely removed:** vehicle can be kick-started. Standing
  time is limited because the supercap has non-zero self-discharge
  (days, not months). Not a supported long-term configuration.
- **Stator open circuit:** supercap depletes rapidly, engine stops.
  Logged.
- **R/R short:** stator sees short circuit, overheats. TCO fuse or
  discrete inline PTC advisable if commonly-available R/Rs don't
  include short protection.
- **R/R runaway (overvoltage):** crowbar clamps at 15.5 V.
  Downstream TVSes back that up. Battery protected by LFP BMS.
- **Supercap failure (open):** battery back-feeds bus during operation
  and engine keeps running, but kick-start with a flat battery no
  longer works. Detected by monitoring bus response during starting.
- **Reverse polarity connection during service:** P-FET ideal-diode
  protects each node. Bus polarity checked during ECU boot.

## Character constraints on the physical implementation

- Battery hidden under seat or in original battery-box location.
- Supercap module inside the ECU enclosure, invisible.
- R/R hidden in the frame cavity or under a side cover with airflow.
- Fuse box small, hidden under a side cover, accessible without tools.
- Wiring in original-style cloth-over-braid loom where visible; modern
  insulation underneath.

## Bench-measurement checklist (before schematic finalisation)

- Stator open-circuit voltage vs. RPM, 0 to peak operating.
- Stator short-circuit current vs. RPM, 0 to peak operating.
- Deliverable DC power at 14.4 V and at 9 V across the RPM range.
- Deliverable energy per kick (integrated stator output during a
  simulated kick profile), used to size the supercap.
- Coil primary inductance and resistance (of the chosen external
  coil).
- Coil dwell time to reach target primary current.
- ECU cold-boot time end-to-end (once first firmware exists).

## Open questions

- Exact original stator specification — measure, don't assume.
- Chosen external ignition coil model — deferred until MCU/ECU design
  freezes the coil driver IC choice.
- Choice of battery charging controller (dedicated IC vs. discrete
  ECU-controlled MOSFETs) — deferred to ECU schematic phase.
- Physical mounting location for R/R (needs airflow) — deferred to
  frame inspection.
- Supercap module selection — deferred until low-RPM stator curve is
  measured.

## Related

- [ADR-0002: Skip mechanical points](../project/decisions/0002-skip-mechanical-points.md)
- [ADR-0004: Kick-start with flat battery](../project/decisions/0004-kick-start-flat-battery.md)
- [ADR-0003: MCU family selection](../project/decisions/0003-mcu-family-selection.md)
- [System architecture](system.md)
