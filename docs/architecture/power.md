# Power and electrical architecture

Vehicle-level power system. Covers charging source, battery, distribution,
regulation, protection, load budget, and battery-independent kick-start
capability.

Some decisions here are provisional pending measurements on the actual
K181 stator, which must be characterised on the bench before the
regulator/rectifier is designed and before the stator's continued use
(vs. rewind) can be confirmed.

## The original K181 power situation

The Casal M151 originally had an integrated flywheel magneto with:

- Ignition coil generating HT for the sparkplug via mechanical points.
- A separate lighting coil directly powering the headlight (AC).
- No rectifier, no battery, no regulation. Voltage varying with RPM.
- Nominal system voltage ~6 V-class.

The modernised system diverges from all of the above, and — per
[ADR-0006](../project/decisions/0006-modern-magneto-replacement.md) —
also replaces the magneto itself with a purpose-built modern 12 V
kit (VAPE.eu or equivalent). The stock magneto assembly is not
retained.

## Design objectives

- 12 V DC modernised electrical system.
- ECU can be kick-started with a flat main battery
  (see [ADR-0004](../project/decisions/0004-kick-start-flat-battery.md)).
- Battery is present and functional in normal use, but not required to
  boot the ECU during starting.
- **Original-format incandescent exterior lamps** must be supported —
  see [ADR-0005](../project/decisions/0005-retain-incandescent-exterior-lamps.md).
  This sets the running load budget and constrains stator sizing.
- Sunday-rideable in real weather; sealed enclosures, IP-rated
  connectors.

## Modernised system — architecture

Nominal system voltage: **12 V DC**. Bulbs in the stock lamp housings
are 12 V-rated incandescent equivalents of the original-era units.

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
               +--> Main fuse (~15 A) --> DC bus (distribution point)
                        |
                        +--> ECU (via own fuse, ideal-diode input)
                        |
                        +--> Battery charging controller
                        |         |
                        |         v
                        |     LiFePO4 4-5 Ah battery
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
                        Handlebar    Rear lamps (via handlebar
                        controller   controller's MOSFETs and
                                     relays)

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

## Load budget

Running load with incandescent exterior lamps (per ADR-0005), at 12 V
bus voltage:

| Load | Current draw |
|---|---|
| ECU running | ~0.5 A |
| Handlebar controller (MCU + interior LEDs) | ~0.3 A |
| Ignition coil (time-averaged at idle ~3000 RPM, ~50 sparks/s) | ~0.1-0.2 A |
| **Headlight low beam** (25-35 W incandescent) | **~2.1-2.9 A** |
| **Tail lamp** (~5 W incandescent) | **~0.4 A** |
| Front indicator (per side, active) | ~0.8 A |
| Rear indicator (per side, active) | ~0.8 A |
| Brake lamp (~21 W, transient) | ~1.75 A |
| Horn (mechanical, momentary) | ~2-5 A |

**Cruise steady-state (headlight low + tail + ECU + handlebar +
coil):** ~3.5-4.0 A, ~50 W.

**Cruise with hazard (both indicators blinking) + brake pressed:** peak
~7-8 A during the on-cycle of a blink.

**Kick-start (ignition off, no lamps):** dominated by ECU + coil during
starting = ~1 A. This bounds ADR-0004 supercap sizing (unchanged).

Standby (ignition off, no ECU sleep-load): ~5 mA for RTC and log
preservation.

## Charging source

The stock K181 flywheel magneto is being replaced entirely with a
modern 12 V unit sourced as a purpose-built kit — see
[ADR-0006](../project/decisions/0006-modern-magneto-replacement.md).
Preferred supplier: **VAPE.eu** or equivalent offering a Casal M151-
compatible 12 V conversion kit. The kit supplies a new stator, rotor,
and typically a modern HT coil.

The replacement is chosen because:

- Typical VAPE-class kits deliver ~90-100 W at operating RPM,
  comfortably above the ~50 W ADR-0005 running-load budget.
- No stator rewind coordination needed.
- Fresh mechanical parts with known behaviour.

Usage:

- **Stator AC output** → shunt-type MOSFET R/R → DC bus.
- **Kit's own ignition system** (single-tooth Hall trigger + CDI, if
  supplied) is unused. Our custom 36-1 trigger and ECU handle
  ignition per ADR-0002.
- **HT coil** — either the kit-supplied coil or a separate modern
  automotive coil, driven by the ECU IGBT. Choice deferred.

**Bench measurements required before finalising R/R selection:**

- Stator open-circuit AC voltage vs. RPM, from cranking speed
  (~400 RPM) up through peak operating RPM. This informs the R/R's
  input voltage envelope and the kick-start bootstrap analysis.
- Stator short-circuit AC current vs. RPM.
- Deliverable DC power at 14.4 V and at 9 V across the RPM range.
- Deliverable energy per kick — bounds ADR-0004 supercap sizing.

These measurements are done on the **new** stator once received.
They confirm the supplier's spec and pin the R/R and supercap
selections.

## Regulator/rectifier

**Shunt-type MOSFET R/R** with passive rectifier front-end. Rationale
unchanged from prior version: series-topology fails closed when the
control MOSFETs are unpowered, incompatible with the ADR-0004 bootstrap
requirement.

Setpoint: 14.4 V bus voltage. Overvoltage crowbar at 15.5 V.

Off-the-shelf candidates: Shindengen SH847-class or comparable
aftermarket MOSFET R/Rs marketed as "shunt type." Some motorcycle R/Rs
are internally series-type despite MOSFET marketing — verify topology
before purchase.

Current rating requirement: **≥ 10 A continuous output** to cover
peak lamp + accessory loads with margin.

## Battery

**Chemistry: LiFePO4** (LFP), for the reasons in ADR-0004.

Sizing: bumped up moderately from the original 3-4 Ah plan to **4-5
Ah nominal**. Rationale:

- Running load is now ~4 A rather than ~2 A.
- If the stator is under-sized on any given ride (partially, or before
  a rewind is done), the battery must carry some deficit.
- 5 Ah at 12 V = 60 Wh, giving ~15 minutes of running-load standby if
  the stator produced zero — hard failure boundary, not normal
  operation.
- Physical: still small enough (~400 g LFP) to fit the original battery
  box with a foam adapter.

Standby load (parked, ECU asleep) at 5 mA gives ~40 days on a 5 Ah
pack. Practical for Sunday-rider standing periods.

**Battery management:** built-in BMS on the LFP pack. Cell-level
balancing, low-voltage cutoff, high-temperature cutoff, short-circuit
protection.

## Supercap bank

Unchanged from ADR-0004. Details in that ADR and in the earlier
version of this doc. First working target: ~1 F at 15 V rating,
sized from the low-RPM stator output measurement.

## Battery charging controller

Unchanged in principle. Implementation may be a discrete ECU-controlled
FET pair (preferred, logging-friendly) or a dedicated BMS IC.

Charge current headroom must accommodate the case where the stator is
delivering all it can and the load is minimal — potentially several
amps into the battery. Charge FETs rated for ≥ 5 A continuous.

## Distribution and protection

Revised current ratings:

- **Main fuse** (bus-to-distribution): **~15 A blade** (was 10 A).
  Sized above steady load with headroom for horn transient plus
  simultaneous hazard.
- **Per-node fuses:**
  - ECU: 5 A (unchanged).
  - Handlebar controller (switched-rail feed to the electronics only,
    not to lamps directly): 3 A.
  - Headlight low: 5 A.
  - Headlight high: 5 A.
  - Tail + brake: 5 A.
  - Indicators (combined): 5 A.
  - Horn: 5 A.
- **Reverse polarity protection:** P-channel MOSFET ideal-diode on
  the ECU input. Unchanged.
- **Transient protection:** TVS diode at each MCU-bearing node's
  input.
- **Ignition switch:** cuts the switched rail feeding lamps and
  handlebar controller. ECU stays powered momentarily to flush logs,
  then sleeps at ~5 mA standby.

## ECU internal rails

Unchanged from previous revision — 12 V input, 5 V buck, 3.3 V LDO,
8 V brownout threshold, 100 ms cold-boot budget.

## Coil driver — power notes

Unchanged. Bosch BIP373 or STMicro VB525SP class low-side IGBT with
integrated Zener clamp; star-grounded coil return; primary sense
built into the driver.

## Load shedding and low-battery behaviour

Bounded by regulatory requirements:

- **Headlight is not sheddable** — Portuguese law requires daytime
  headlight for two-wheelers. See
  [ADR-0005](../project/decisions/0005-retain-incandescent-exterior-lamps.md).
- **Shed candidates (only if bus voltage drops below thresholds):**
  - Dashboard illumination — reduce PWM duty, then off.
  - Warning-lamp cluster brightness — reduce PWM duty.
  - Indicator repetition rate slightly reduced (still legally on).
- ECU broadcasts bus voltage and battery voltage on CAN at 10 Hz.
- Handlebar warns at ~12.5 V (~30 % SoC on LFP).
- Below ~12.0 V: illumination reduces, non-essential loads drop.
- Below ~11.0 V: rider warning becomes urgent; consider stopping
  before the ECU brown-outs.
- ECU continues firing ignition as long as its 3.3 V rail is stable.
  Brownout threshold ~8 V on the bus input.

Realistic outcome: with a stator rewind, this behaviour is a fallback
for genuine failure modes (broken stator, disconnected R/R). Without
a rewind, low-battery warnings may be routine on long rides — which
is a strong argument for rewinding.

## Failure modes

- **Flat battery (any cause):** vehicle can still be kick-started via
  supercap bootstrap. Once running, R/R charges bus; charging
  controller arbitrates whether to also charge battery. Rider notified
  via CAN warning.
- **BMS-tripped battery:** same as flat battery — kick-start still
  works.
- **Battery entirely removed:** vehicle can be kick-started. Standing
  time is limited because the supercap has non-zero self-discharge.
  Not a supported long-term configuration.
- **Stator open circuit:** supercap depletes rapidly under running
  load; engine stops. Logged.
- **Stator under-capacity:** persistent negative charge current — bus
  cannot maintain 14.4 V during full load; battery slowly drains
  during the ride. Warning at first symptom, informative rather than
  emergency.
- **R/R short:** stator sees short circuit, overheats. TCO fuse or
  discrete inline PTC advisable if commonly-available R/Rs don't
  include short protection.
- **R/R runaway (overvoltage):** crowbar clamps at 15.5 V. Downstream
  TVSes back that up. Battery protected by LFP BMS.
- **Supercap failure (open):** battery back-feeds bus during
  operation and engine keeps running, but kick-start with a flat
  battery no longer works. Detected by monitoring bus response during
  starting.
- **Lamp bulb short:** blows the appropriate per-node fuse. Rider
  loses that lamp but vehicle remains rideable.
- **Reverse polarity connection during service:** P-FET ideal-diode
  protects each node.

## Character constraints on the physical implementation

- Battery hidden under seat or in original battery-box location.
- Supercap module inside the ECU enclosure, invisible.
- R/R hidden in the frame cavity or under a side cover with airflow.
- Fuse box small, hidden under a side cover, accessible without
  tools.
- Wiring in original-style cloth-over-braid loom where visible;
  modern insulation underneath.
- Lamp bulbs are the original type in the original housings — no
  visible change to the vehicle's exterior lighting.

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
- **Actual bulb cold-inrush characteristic** — measured on the chosen
  bulb model, informs MOSFET/relay sizing on the handlebar controller.

## Open questions

- **VAPE (or equivalent) kit selection** — specific M151-compatible
  part, availability, delivered content list. Confirmed before
  ordering downstream components.
- **New stator's measured spec** — bench-measured after receipt,
  informs R/R input range and supercap sizing.
- **Bulb wattage selected for headlight** — 25/25 W or 35/35 W;
  determined by chosen housing and legal minimum.
- **HT coil model** — VAPE-supplied vs. separate modern automotive
  coil. Deferred until MCU/ECU design freezes the coil driver IC
  choice.
- **Choice of battery charging controller** (dedicated IC vs. discrete
  ECU-controlled MOSFETs) — deferred to ECU schematic phase.
- **Physical mounting location for R/R** (needs airflow) — deferred
  to frame inspection.
- **Supercap module selection** — deferred until low-RPM new-stator
  curve is measured.

## Related

- [ADR-0002: Skip mechanical points](../project/decisions/0002-skip-mechanical-points.md)
- [ADR-0004: Kick-start with flat battery](../project/decisions/0004-kick-start-flat-battery.md)
- [ADR-0005: Retain incandescent exterior lamps](../project/decisions/0005-retain-incandescent-exterior-lamps.md)
- [ADR-0006: Modern magneto replacement](../project/decisions/0006-modern-magneto-replacement.md)
- [ADR-0003: MCU family selection](../project/decisions/0003-mcu-family-selection.md)
- [System architecture](system.md)
- [Handlebar controller](handlebar-controller.md) — lamp drive stage
