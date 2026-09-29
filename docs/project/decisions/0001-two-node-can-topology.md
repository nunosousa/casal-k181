# ADR-0001: Two-node CAN topology (ECU + handlebar controller)

**Status:** Accepted (lamp-drive ownership refined by [ADR-0007](0007-lamp-drive-moves-to-ecu.md))
**Date:** 2026-09-28

## Context

The project modernises the entire vehicle electrical system, not only the
engine management. Beyond the ECU, the vehicle has:

- A dashboard consisting of three separate physical enclosures on the
  handlebars: speedometer/odometer, tachometer, and warning-lamp cluster.
- Handlebar switchgear (indicators, horn, light switch, mode buttons).
- Modernised front and rear lighting.
- A GPS module for position, altitude and backup speed reference.

Two architectural questions had to be answered:

1. How many intelligent nodes on the vehicle?
2. Does GPS warrant its own node?

Earlier project discussion had tentatively planned a single-ECU
architecture with CAN deferred as over-engineering. The scope expansion to
whole-vehicle modernisation revised that premise.

## Decision

**Two CAN nodes on the vehicle:**

- **ECU** (in-frame): engine management, sensor acquisition, logging,
  service USB. Authoritative source of RPM, wheel speed, engine state.
- **Handlebar controller** (headlight nacelle or small hidden enclosure
  near the handlebar mount): drives the three dashboard enclosures via
  short local wiring, handles handlebar switchgear, drives rear lamps via
  low-side MOSFETs, hosts the GPS module and re-broadcasts GPS data on
  CAN.

The three dashboard enclosures are electrically passive: stepper motors
for speedo/tach needles, LEDs for warning lamps, illumination. All local
wiring to the handlebar controller with automotive-grade multi-pin
connectors.

**CAN parameters:** CAN 2.0B, 500 kbit/s, 120 Ω termination at each end.
Periodic frames at 100 Hz for high-rate telemetry; event frames on state
change. Single canonical message definition in `protocol/messages.yaml`,
generated headers for both firmware images.

**GPS:** module physically located under a plastic-panelled area with
sky view (working assumption: headlight nacelle). UART-wired to the
handlebar controller. Handlebar controller re-broadcasts position, speed
and altitude on CAN at 5–10 Hz. GPS is not a separate node.

## Consequences

Positive:

- ECU is real-time isolated from display refresh, button debouncing, and
  turn-signal timing.
- ECU is authoritative for engine state. Dashboard shows what the ECU
  logs; no divergence.
- Only two bootloaders, two flash images, two config stores. Complexity
  is proportional to the function.
- Dashboard enclosures are mechanically and electrically simple; a
  cracked speedometer housing is a stepper motor replacement, not a
  firmware event.
- Harness up to the handlebars carries CAN + power + a few switch
  returns; simpler than analog gauge cables + independent sensor wiring.

Negative:

- Two transceivers, two MCUs, two firmware images. Cost is real but
  small.
- Protocol drift risk between nodes. Mitigated by generating both nodes'
  code from a single canonical message definition.
- If the handlebar controller fails, the vehicle is unrideable (no
  speedo, no warning lamps, no indicators). Failure mode must be
  addressed: safe fallback to hard-wired indicator/horn/lights path, or
  simply "the vehicle does not run without a working handlebar
  controller" as an accepted risk given occasional Sunday use.

## Alternatives considered

- **Three CAN nodes (one per dashboard enclosure).** Rejected: three MCUs
  for three trivial functions is complexity disproportionate to the
  problem. Only compelling for the distributed-systems experience per
  se, which is not the project's aim.
- **Single big controller doing ECU + dashboard + BCM.** Rejected: ECU
  has hard real-time deadlines that should be isolated from soft-RT UI
  and lighting work. Also, physical location differs — ECU wants to be
  in the frame, dashboard on the handlebars.
- **GPS as a third node.** Rejected: GPS modules are UART-out devices,
  not compute-heavy. Wiring UART to whichever node is physically nearest
  is sufficient.
- **No CAN, analog gauge cables + independent dashboard sensors.**
  Rejected: divergent state, harness noise contamination, sensor
  duplication.
