# System architecture

Vehicle-level electrical architecture under the [system concept](../project/system-concept.md),
[requirements](../project/requirements.md) and [ICD](interfaces.md).
[ADR-0012](../project/decisions/0012-distributed-dashboard-can-nodes.md)
defines four intelligent CAN nodes. The PDM is not a CAN node.

## Nodes and ownership

**ECU**, in a sealed in-frame enclosure:

- Crank (36-1), front-wheel speed, EGT, CHT, ambient T/P/RH, IMU and power
  sensing. Twistgrip TPS is received from the warning cluster over CAN.
- Ignition, future fuel control, exterior-lamp blink/control and charge
  logic. Physical high-current switching belongs to the PDM, including the
  coil driver per ADR-0009 (or the selected smart coil).
- Internal non-volatile session logging, engine/vehicle CAN broadcasts,
  service USB and internal SWD.

**Speedometer**, inside its own stock-style enclosure:

- One local needle driver and dial illumination.
- ECU wheel-derived speed display, lifetime odometer and persistence.
- Its own CAN, power conversion, calibration, health and update endpoint.

**Tachometer**, inside its separate stock-style enclosure:

- One local needle driver and dial illumination.
- ECU-derived RPM display.
- Its own CAN, power conversion, calibration, health and update endpoint.

**Warning cluster**, inside its separate stock-style enclosure:

- Warning LEDs and locally timed dashboard indicator repeaters.
- All remaining dashboard/handlebar functions: switchgear acquisition,
  twistgrip TPS, GPS UART/PPS and ambient-light sensing.
- Rider-intent/TPS/GPS broadcasts and shared brightness command; its own
  CAN, power conversion, calibration, health and update endpoint.

There is no central handlebar controller. See [dashboard controllers](dashboard.md)
for local hardware and service detail. Peripheral GPS/antenna and sensor
satellite placement must respect sky view, cable integrity and stock appearance.

## Power distribution and passive hardware

The [PDM](pdm.md) is a separate enclosure adjacent to the ECU:

- Main fuse, reverse-polarity and transient protection, supercap bank.
- Battery charge FETs and sensor returns.
- Serviceable lamp fuses/relays, exterior-lamp and horn power switching.
- Coil power driver and sense returns, commanded by ECU timer signals.
- Protected ECU DC feed and protected switched feeds to all three
  instrument controllers.

Battery, modern magneto/R/R, external ignition coil, lamps and wiring remain
external hardware. Instrument enclosures are no longer passive subsystems.

## Interconnect and physical layout

    Frame: stator/RR -- PDM -- protected DC --> ECU
                        |
                        +-- protected switched feeds --> three instruments

    CAN trunk: ECU ==== harness ==== speedometer ==== tachometer ==== warning cluster
                    (short drops / exact physical order to be designed)

The drawing illustrates connectivity, not a released harness route.
Use a linear twisted-pair CAN trunk, 500 kbit/s classic CAN, with exactly
two 120-ohm terminations at physical ends. Do not populate termination on
every instrument or use long star branches. Final instrument ordering and
endpoint locations are ICD/harness decisions.

Engine sensors wire to ECU; ECU control/sense lines wire to PDM.
Switchgear, TPS satellite, GPS and ALS wire to the warning cluster.
Each gauge motor/illumination wires only to its local controller.

## Data ownership

Exactly one node owns each authoritative state:

| State | Owner | Consumers |
|---|---|---|
| RPM / engine state | ECU | Tachometer, warning cluster |
| Wheel-derived speed / distance since boot | ECU | Speedometer, warning cluster |
| Lifetime odometer | Speedometer | Service tools |
| EGT / CHT / power / ambient / IMU | ECU | Warning cluster as defined in protocol; logs |
| Twistgrip TPS / rider intent | Warning cluster | ECU |
| GPS position / speed / UTC / validity | Warning cluster | ECU logs |
| Exterior lamp phase / commands | ECU | PDM physical switching |
| Dashboard repeater phase | Warning cluster | Local LEDs |
| Ambient-light brightness request | Warning cluster | Speedometer, tachometer |
| Gauge setpoint / illumination / calibration | Each gauge | Local actuator |
| Session log | ECU | Service tools |
| Per-node health / firmware identity | Each respective node | ECU/cluster/gauges as defined in protocol |

## Failure modes and safe states

- **Missing ECU:** gauges hold last-known needles and indicate stale data
  via local illumination; cluster independently warns. Exact indication
  and recovery criteria remain PAR-09.
- **Missing speedometer or tachometer:** cluster warns for the affected
  unit; other instruments and engine do not depend on that unit's software.
- **Missing warning cluster:** gauges continue from ECU data, with usable
  local brightness fallback. ECU must handle stale rider/TPS inputs;
  stop-path independence and fallback remain PAR-06/09 release blockers.
- **Shared bus or power fault:** not equivalent to an isolated node reset.
  Analyse and test branch protection and bus-fault propagation.
- **Invalid calibration:** validated applicable ignition/fuel fallback or
  engine-output inhibition, never assume fixed timing alone recovers injection.
- **Coil driver fault:** report fault; hardware failure may prevent running.
- **Low battery/charging deficit:** cluster warns; local instruments may
  reduce interior illumination without blanking required warnings.
  Required exterior lighting is not shed.

## Deferred extensions

- [Phase-9 injection](../project/staged-plan.md): ECU fuel control, hardware
  allocation, power/kick-start revalidation and safe shutdown before adoption.
- Immobiliser/keyless start and rider USB charging remain open.
- Dashcam integration remains outside the first-running baseline.

## Related

- [Dashboard](dashboard.md), [ECU](ecu.md), [power](power.md)
- [CAN specification](can-bus.md), [firmware](firmware.md), [HIL](hil.md)
