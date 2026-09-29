# System architecture

Vehicle-level electrical architecture. Details of each node live in
`ecu.md`, `dashboard.md`, `handlebar-controller.md`, `power.md`, and
`can-bus.md` (to be written as those subsystems are designed).

## Nodes

Two intelligent nodes on the vehicle, plus passive subsystems:

**ECU** — in-frame, in a sealed aluminium enclosure. Owns:

- Crank trigger acquisition (36-1 Hall).
- Coil driver (external inductive coil, low-side IGBT).
- Front wheel speed acquisition.
- EGT, CHT, ambient temp/pressure/humidity, TPS, battery voltage.
- On-board IMU (6-axis).
- Data logging to internal non-volatile storage.
- CAN broadcast of engine and vehicle state.
- Service USB (single automotive-style connector, hidden but accessible
  without tools).
- SWD for PCB-level debugging (internal, short, not routed through the
  harness).

**Handlebar controller** — in the headlight nacelle or a small hidden
enclosure near the handlebar mount. Owns:

- Stepper motor drivers for speedometer and tachometer needles.
- LED drivers for warning-lamp cluster and gauge illumination.
- Handlebar switchgear inputs (indicators, horn, headlight, mode buttons).
- Rear lamp drivers via low-side MOSFETs (long wires to tail acceptable).
- GPS module UART (assumption: module co-located in headlight nacelle).
- CAN participation: consumer of engine state, producer of GPS state and
  user-input events.

**Passive subsystems:**

- Speedometer, tachometer, warning-lamp enclosures — stepper motors, LEDs,
  illumination only. Wired to the handlebar controller.
- Battery (LiFePO4), regulator/rectifier, fuse box.
- Ignition coil (external inductive type, driven by ECU).
- Wiring harness.

## Physical layout (working assumption)

    +--------------------+
    | Headlight nacelle  |
    |   Handlebar ctrl   |
    |   GPS module       |
    +---+------------+---+
        |            |
    Switchgear   Dashboard enclosures (speedo, tach, warnings)
                 (short local wiring)
        |
        v (harness down to frame)
    +--------------------+
    |    Frame cavity    |
    |        ECU         |
    |  Battery, R/R,     |
    |  fuse box          |
    +---+------------+---+
        |            |
    Engine sensors  Rear lamps
    Coil driver

## Interconnect

- **CAN bus:** two conductors (CAN-H, CAN-L), twisted pair, 120 Ω
  termination at each end. Runs from ECU up to the handlebar controller
  as part of the main harness segment.
- **Power:** switched +12 V and ground to each node. ECU is directly on
  battery (with its own switch/fuse); handlebar controller powered via
  ignition-switched line.
- **Sensor and actuator wiring:** engine-adjacent sensors run to the ECU;
  handlebar switchgear and dashboard enclosures wire to the handlebar
  controller.

## Data ownership

Single-writer discipline: exactly one node is authoritative for each
piece of state.

| State | Owner | Consumers |
|---|---|---|
| RPM | ECU | Handlebar controller (tachometer) |
| Vehicle speed | ECU (from front wheel Hall) | Handlebar controller (speedometer) |
| Odometer | Handlebar controller (persisted) | — |
| EGT, CHT | ECU | Handlebar controller (warning) |
| Battery voltage | ECU | Handlebar controller (warning) |
| Coolant / oil pressure | n/a | n/a |
| Ignition state (running, cranking, off) | ECU | Handlebar controller |
| Turn signal request | Handlebar controller | (self, and rear lamps) |
| Turn signal state (active, hazard) | Handlebar controller | — |
| Position, altitude, GPS speed | Handlebar controller (from GPS) | ECU (logs) |
| Ambient temperature / pressure / humidity | ECU | (logs) |
| Session log | ECU | — |

## Failure modes and safe states

- **CAN silence from ECU:** handlebar controller freezes gauges at last
  known value, illuminates a warning lamp. Rider knows to stop.
- **CAN silence from handlebar controller:** ECU keeps running the
  engine. Rider notices via dark dashboard.
- **ECU config-store fault:** boot into hardcoded safe fixed-timing map,
  illuminate warning via CAN if possible.
- **Coil-driver fault:** logged; engine cannot run. This is not a
  soft-failure case.
- **Battery critical low:** ECU broadcasts warning; handlebar controller
  shows warning lamp. Engine continues to run if magneto can sustain
  ignition current.

## Deferred items

- Immobiliser / keyless start (design open).
- USB charge port for rider phone (open; likely lives off battery via a
  small regulator, not on either node).
- Dashcam integration (out of scope for phase 1).

## Related

- [ADR-0001: Two-node CAN topology](../project/decisions/0001-two-node-can-topology.md)
- [ADR-0002: Skip mechanical points](../project/decisions/0002-skip-mechanical-points.md)
