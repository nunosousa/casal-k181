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
- Modernised dashboard: speedometer, tachometer, warning-lamp cluster.
- Modernised lighting, switchgear, charging, wiring harness.
- Instrumentation and data logging sufficient to characterise each stage.

## Non-goals

- Maximum peak power at the expense of character.
- Reed-valve conversion.
- Cylinder porting modifications.
- Certified-automotive process rigour.

## Repository layout

    docs/                       project documentation
      project/                  constraints, staged plan, decisions log
      architecture/             system and subsystem architecture
      experiments/              per-experiment protocols and results
      build-log/                mechanical and electrical restoration notes
      measurement-plan.md       primary methodology document
    protocol/                   canonical CAN message definitions
    hardware/                   ECU, handlebar controller, dashboard, harness
    firmware/                   bootloaders, riding app, service app, shared
    tools/                      loader, log analysis, protocol codegen
    data/                       session logs (gitignored)

## Status

Pre-build. Moped disassembled. Project documentation and architecture being
defined. See [staged plan](docs/project/staged-plan.md) for current phase
ordering.
