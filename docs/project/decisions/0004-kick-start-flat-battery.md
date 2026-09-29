# ADR-0004: Kick-start capability preserved with flat battery

**Status:** Accepted
**Date:** 2026-09-29

## Context

[ADR-0002](0002-skip-mechanical-points.md) accepted "battery required for
first start" as a consequence of switching from mechanical points to
ECU-controlled ignition. During subsequent review, the user requested
that kick-starting with a flat main battery remain feasible if the added
design complexity is reasonable.

Motivation is character preservation: the ability to always start a
moped by kicking it — regardless of a flat cell, a tripped BMS, or a
vehicle that has stood for a year — is part of what mopeds *are*.
Removing that ability was an acceptable but reluctant concession in
ADR-0002.

## Decision

The ECU power input stage is designed to bootstrap from the stator
during kick-starting, so that a flat or BMS-tripped battery does not
prevent the engine from starting.

Concrete design commitments:

1. **Shunt-type MOSFET regulator/rectifier**, not series-type. The
   rectifier stage is passive (diode bridge), so DC output rises with
   the stator's AC output whenever the flywheel is spinning, independent
   of the shunt-control MOSFETs being powered.

2. **Supercapacitor bank on the ECU input DC bus**, sized so that a
   handful of kicks charge it to above the ECU brownout threshold. First
   working target: ~1 F, ~15 V-rated (e.g. two 2.7 V/3 F cells in
   series with balancing). Actual sizing pinned by bench measurement of
   the stator's low-RPM output curve.

3. **ECU cold boot ≤ 100 ms** from application of stable input rail to
   "ready to fire spark." At 500 RPM kick speed (8.3 Hz per revolution)
   this comfortably allows the first spark to fire within one engine
   cycle of boot.

4. **ECU input operates from 8 V to 16 V**. Internal buck-LDO chain must
   have dropout margin down to 8 V, so the supercap bank can droop
   during boot and still keep the ECU alive.

5. **Battery on a separate branch behind a charge-management switch.**
   The battery is not directly on the DC bus. A charge controller feeds
   current from the bus to the battery when the bus is at or above
   ~14 V; the battery only back-feeds the bus (via a controlled path)
   when the bus droops below battery voltage. This isolation prevents
   a flat battery from being an unwanted load on the supercap bank
   during boot.

The battery is still expected to be present and functional in normal
use. Kick-starting with a flat battery is an emergency / degraded mode,
not the intended primary starting method.

## Consequences

Positive:

- Vehicle can be kicked to start with a flat or BMS-off battery.
  Character preserved.
- Robustness to battery-related failures: aged cells, single-cell
  BMS-lockout, vibrated-loose battery connection, or vehicle sitting for
  a year all remain kick-recoverable.
- ECU input becomes more tolerant of transients and brownouts as a side
  effect.

Negative:

- BOM increases by ~€30-50 for supercap + balancing + charge controller
  IC + associated protection.
- ECU input schematic is more complex: shunt R/R, cap bank, battery
  isolation switch, ideal-diode ORing of sources.
- Supercap has finite lifetime (~10 years at moderate temperature).
  Long-term maintenance item.
- ECU cold-boot time and startup current draw become hard design
  constraints on both firmware and bootloader. In particular, the
  bootloader cannot afford long integrity-check delays during
  cold-start; heavy checks are deferred to a background task after the
  first sparks have fired.
- Firmware-brick scenarios (corrupt application image, failed OTA) are
  not helped by this ADR. Those remain a bootloader-safe-mode concern.

## Alternatives considered

- **Accept ADR-0002 as-is** (battery required). Rejected on user's
  character-preservation preference.
- **Backup CDI-style ignition** on separate hardware path, activated
  when ECU is unpowered. Rejected: doubles the ignition hardware and
  introduces a second failure surface for marginal benefit.
- **Manual bypass switch** to run a discrete fixed-timing ignition when
  ECU is dead. Rejected on character-preservation (visible extra switch)
  and complexity grounds.
- **Small primary cell (coin) as boot power reservoir.** Rejected:
  primary cells self-discharge and eventually die, requiring service
  intervention that defeats the "just kick it" character goal.
- **Larger supercap bank (e.g. 10 F) as the only energy storage, no
  battery at all.** Rejected: supercap self-discharge over months of
  standing time is significant; a moped that sits for a season would
  arrive at zero charge. Battery-plus-supercap is the correct
  combination.

## Relation to ADR-0002

This ADR refines but does not supersede
[ADR-0002](0002-skip-mechanical-points.md). ADR-0002's core decision
(skip mechanical points, use ECU-controlled ignition) stands. Only the
"battery required for first start" consequence is refined here.

## Related

- [ADR-0002: Skip mechanical points](0002-skip-mechanical-points.md)
- [Power architecture](../../architecture/power.md) *(rewritten to reflect this ADR)*
