# Casal K181 restoration and experimental ECU project

A 1970s Portuguese Casal K181 moped restored as an experimental engineering
platform. The project modernises the entire electrical system — engine
management, dashboard, lighting, switchgear, harness — while preserving the
vehicle's mechanical and visual character.

## Objective

Explore how far the performance, drivability, efficiency, reliability and
refinement of the M151-based two-stroke engine can be pushed within
deliberate architectural constraints (see [constraints](docs/project/constraints.md)).

The guiding principle is experimental: establish baselines, change one
subsystem at a time, measure again, preserve datasets. The finished machine
should be visually and mechanically recognisable as a K181 but perform
noticeably better because its subsystems have been individually optimised.

Professional-grade engineering thinking, hobby-grade process, experimentally
demonstrated results.

## Scope

- Mechanical restoration.
- 60 cc Eurocilindro top end + NOS 5-speed gearbox.
- Custom ECU replacing the mechanical points ignition.
- Explore throttle-body fuel injection: replace the carburettor with a
  throttle body and electronically controlled injector, using sensors and
  ECU calibration to control fuel delivery after carburettor baselines.
- Modernised dashboard: speedometer, tachometer, warning-lamp cluster.
  Each stock-style enclosure contains its own CAN controller; there is no
  central handlebar controller. The warning-cluster unit also owns
  switchgear, twistgrip TPS, GPS and ambient-light sensing.
  See [dashboard architecture](docs/architecture/dashboard.md).
- Modernised lighting, switchgear, charging, wiring harness.
- Instrumentation and data logging sufficient to characterise each stage.

## Non-goals

- Maximum peak power at the expense of character.
- Reed-valve conversion.
- Cylinder porting modifications.
- Certified-automotive process rigour.

## Repository layout

    docs/                       project documentation
      project/                  concept, requirements, V&V, backlog, decisions
      architecture/             system and subsystem architecture
      experiments/              per-experiment protocols and results
      build-log/                mechanical and electrical restoration notes
      measurement-plan.md       primary methodology document
    protocol/                   canonical CAN message definitions
    hardware/                   ECU, three instrument controllers, PDM, harness
    firmware/                   bootloaders, riding app, service app, shared
    tools/                      loader, log analysis, protocol codegen
    data/                       session logs (gitignored)

## Engineering documentation

Start with the [engineering framework](docs/project/engineering.md) for the
document map and lightweight review/change-control rules. The
[system concept](docs/project/system-concept.md) separates intended behaviour
from experimental hypotheses; the
[requirements](docs/project/requirements.md) allocate commitments to hardware
and software. Cross-subsystem contracts live in the
[ICD](docs/architecture/interfaces.md).

The [V&V plan](docs/project/verification-plan.md),
[hazard register](docs/project/hazards.md) and
[backlog](docs/project/backlog.md) track closure work and evidence.
Generate the [traceability matrix](docs/project/traceability.md) with
`python3 tools/traceability.py`. Requirements are initially draft/open,
and no planned verification is claimed as a pass.

## Status

Pre-build. Moped disassembled. Project documentation and architecture being
defined. See [staged plan](docs/project/staged-plan.md) for current phase
ordering.
