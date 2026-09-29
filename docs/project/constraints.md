# Project constraints

The following are hard boundaries within which the project operates. They
are architectural in nature — accepting or violating any of them changes
what the project *is*.

## Engine architecture

- **Carburettor-based induction.** No fuel injection at any phase.
- **No reed-valve conversion.** Piston-port induction retained.
- **No cylinder porting modifications.** Port geometry as delivered by the
  Eurocilindro kit is accepted as-is. Head, squish geometry, ignition,
  exhaust, gearing and instrumentation are open for optimisation.
- **Original two-stroke architecture.** The engine remains recognisably a
  Casal M151-derived two-stroke, not a fundamentally different racing
  engine.

## Character preservation

- The finished vehicle must remain visually and mechanically recognisable as
  a Casal K181.
- Instrumentation and modernised electronics must not be visually obtrusive.
  No probes hanging out of the exhaust, no zip-tied harnesses, no visible
  aftermarket displays. Service access hidden under panels.
- Original dial faces (or credible reproductions) preferred on dashboard
  gauges, driven by modern electronics behind the panel.

## Committed hardware

- **Eurocilindro NOS 44 mm bore kit** — ~60 cc, adopted as the top-end.
- **NOS 5-speed gearbox** — adopted as the transmission.
- **Original carburettor and points-derived ignition components retained**
  only until the ECU is ready. First engine run is with ECU-controlled
  fixed-timing ignition (see [staged plan](staged-plan.md)).

## Intended use

- Occasional Sunday riding. Not a race vehicle, not a pure test rig.
- Must survive rain, vibration, seasonal thermal cycling, and being ignored
  for months. This drives IP-rated enclosures, sealed connectors, conformal
  coating, and non-consumer-grade internal storage.
- Must never leave the rider stranded due to a soft failure in the ECU.
  Boot into a safe fixed-timing map on any config-store or map fault.

## Process

- Hobby project. No certified-automotive or aerospace process burden.
- One variable at a time, wherever possible. Every subsystem change is
  characterised against a preserved baseline dataset.
- All architectural decisions of consequence recorded as ADRs under
  `docs/project/decisions/`.
