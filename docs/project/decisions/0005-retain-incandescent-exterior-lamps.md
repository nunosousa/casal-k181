# ADR-0005: Retain incandescent exterior lamps for road-legal compliance

**Status:** Accepted
**Date:** 2026-09-29

## Context

Earlier project scoping assumed LED lamps for all vehicle exterior
lighting (headlight, tail, brake, indicators) to reduce electrical load
and simplify drive electronics. The user has since identified that this
is not road-legal in Portugal: retrofitting LED emitters into stock
K181 headlight and lamp housings disturbs the photometric certification
of those housings (reflector geometry, filament position, beam pattern)
and consequently fails road-legal type-approval.

The retained-original-technology principle applies: incandescent bulbs
of appropriate form factor must be used in the stock housings.

## Decision

**Vehicle exterior lamps are incandescent** for the road-going
configuration:

- **Headlight** (low and high beam): incandescent, 12 V, form factor
  and wattage matched to the stock housing and Portuguese daytime-lamp
  requirement. Working assumption: 25/25 W or 35/35 W dual-filament
  bulb.
- **Tail lamp:** incandescent, 12 V, ~5 W.
- **Brake lamp:** incandescent, 12 V, ~21 W. Combined-filament bulb
  with tail if a dual-filament original is used.
- **Front and rear indicators:** incandescent, 12 V, ~10 W each.
- **Horn:** original mechanical horn.

**System voltage remains 12 V DC** (per [power.md](../../architecture/power.md)).
Bulbs are 12 V-rated incandescent equivalents of the original 6 V-era
bulbs, in the same physical form factor. The concern behind the
regulation is emitter type and housing geometry, not system voltage.

**Interior lighting stays LED:**

- Dashboard illumination behind dial faces (inside the passive dashboard
  enclosures — not visible-from-outside signal lamps).
- Warning-lamp cluster LEDs.

## Consequences

Positive:

- Fully road-legal. No compromise on Portuguese certification.
- Preserves character — original lamp look and glow.
- Original horn retained; no compatibility drama.

Negative:

- **Running load roughly doubles** compared to the LED plan. Cruise
  load with headlight on rises from ~1.5-2.5 A to ~4.2-5.0 A. See
  [power.md](../../architecture/power.md) revised load budget.
- **Original stator spec may be inadequate.** Its adequacy under the
  new load must be bench-measured before the R/R is finalised;
  provisional plan is to expect a stator rewind rather than treat it
  as the fallback path.
- **MOSFET low-side switches** in the handlebar controller must handle
  higher steady-state current (up to ~3 A per channel for headlight)
  and cold-filament inrush (~5-10× steady for a few ms). Automotive
  relays used for headlight and horn instead of MOSFETs.
- **Harness wire gauge increases** on lamp channels (from ~22 AWG for
  LED signalling to 18-20 AWG for incandescent).
- **PWM frequency for lamp dimming** must be ≥ 1 kHz to avoid filament
  thermal cycling shortening life. (Dimming itself is not a phase-1
  feature.)
- **Load-shedding scope is bounded** because Portuguese law requires
  daytime headlight — the headlight cannot be shed. Only indicators,
  brake (transient anyway), and interior illumination can be reduced
  under low battery.

## Alternatives considered

- **LED retrofit in stock housings.** Rejected on road-legal grounds
  (this ADR exists to record that decision).
- **Replace lamp housings with LED-optimised aftermarket units.**
  Rejected on character-preservation grounds (visible from outside,
  changes vehicle appearance).
- **Keep 6 V system voltage and reuse original 6 V bulbs verbatim.**
  Rejected on modernisation grounds (6 V ECU components, GPS module,
  MCU rails all much harder to source than 12 V equivalents). The
  regulation targets emitter type, not system voltage.

## Related

- [Constraints](../constraints.md)
- [Power architecture](../../architecture/power.md) — load budget and
  stator sizing revised as a consequence of this ADR
- [Handlebar controller](../../architecture/handlebar-controller.md) —
  lamp drive stage revised
- [ADR-0001: Two-node CAN topology](0001-two-node-can-topology.md) —
  unaffected; handlebar still owns lamp control
