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
- **Vehicle exterior lamp control logic** (per
  [ADR-0007](../project/decisions/0007-lamp-drive-moves-to-ecu.md)):
  headlight, tail, brake, front and rear indicators, horn. Blink
  timing generated locally from steady-state rider-intent bits
  received over CAN. Physical switching hardware lives in the PDM
  (see below).
- **Charge controller logic** — drives PDM charge FETs.

**Power Distribution Module (PDM)** — separate hardware enclosure
adjacent to the ECU (per
[ADR-0008](../project/decisions/0008-separate-power-distribution-module.md)).
Passive hardware controlled by the ECU MCU via a short inter-module
cable. **Not a CAN node.** Owns:

- Main fuse, reverse-polarity protection, bus TVS.
- Supercap bank (ADR-0004 kick-start bootstrap buffer).
- Battery charging FETs (physical MOSFETs; logic in ECU).
- Per-lamp blade fuses in ATO holders behind a serviceable cover.
- Automotive relays in sockets (headlight low, high, horn).
- Lamp-drive MOSFETs (indicators, tail, brake).
- Clean 12 V feed to ECU and switched rail to handlebar controller.
- Vehicle harness connector for all lamp outputs.

**Handlebar controller** — in the headlight nacelle or a small hidden
enclosure near the handlebar mount. Owns:

- Stepper motor drivers for speedometer and tachometer needles.
- LED drivers for warning-lamp cluster and gauge illumination.
- Handlebar switchgear inputs (indicators, horn, headlight, mode buttons).
- GPS module UART (assumption: module co-located in headlight nacelle).
- CAN participation: consumer of engine state, producer of GPS state and
  user-input events.
- Dashboard indicator-lamp repeater blink (locally timed at ~1.5 Hz;
  small phase drift from ECU-commanded exterior indicators is
  acceptable).

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
| Turn signal request (rider intent) | Handlebar controller | ECU (drives blink) |
| Turn signal exterior lamp state | ECU (locally-generated blink) | — |
| Turn signal dashboard-repeater state | Handlebar controller (locally-generated blink) | — |
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
  shows warning lamp and sheds interior illumination. Exterior lamps
  (headlight, tail, brake, indicators) are legally required and are
  not shed. Engine continues to run as long as ECU rail is stable.
- **Stator under-capacity relative to load** (e.g. rewind not yet done,
  or degraded): battery slowly drains during running. Warned via CAN.
  Not immediate emergency; rider knows to shorten ride or recharge.

## Deferred items

- Immobiliser / keyless start (design open).
- USB charge port for rider phone (open; likely lives off battery via a
  small regulator, not on either node).
- Dashcam integration (out of scope for phase 1).

## Related

- [ADR-0001: Two-node CAN topology](../project/decisions/0001-two-node-can-topology.md)
- [ADR-0002: Skip mechanical points](../project/decisions/0002-skip-mechanical-points.md)
