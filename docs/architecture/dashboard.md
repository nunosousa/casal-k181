# Distributed dashboard controllers

Three independent CAN controllers inside the three separate stock-style
instrument enclosures, per
[ADR-0012](../project/decisions/0012-distributed-dashboard-can-nodes.md).
There is no central handlebar controller and no passive remote instrument
driven from another enclosure.

## 1. Ownership

| Node | Local outputs / state | Inputs and shared functions |
|---|---|---|
| Speedometer (`speedometer`, address 0x03) | Speed needle, local illumination, odometer/persistence, calibration and health | ECU wheel-derived speed/distance; warning-cluster brightness command |
| Tachometer (`tachometer`, address 0x04) | RPM needle, local illumination, calibration and health | ECU RPM; warning-cluster brightness command |
| Warning cluster (`warning_cluster`, address 0x02) | Warning LEDs, local indicator repeaters, dimming, calibration and health | Switchgear, twistgrip TPS, GPS, ambient-light sensor, ECU status and both gauge heartbeats |

The ECU remains authoritative for measured speed, RPM, thermal/power state
and logged sessions. The speedometer owns the persistent lifetime odometer;
its counter must survive ECU replacement. Other dashboard/handlebar
functions not belonging to the speedometer or tachometer go to the warning
cluster. This rule does not move engine control or power switching off ECU/PDM.

## 2. Common hardware and packaging

Each enclosure contains its own MCU, classic-CAN transceiver, protected
switched-12 V input, local rails and output driver. Each has its own SWD
test points, configuration store and CAN service/update endpoint. Common
PCB/firmware designs may be reused, but the node role and target identity
must be unambiguous. No new visible display or external controller box.

STM32G4-class devices remain candidates, not final per-node selections.
Verify exact package, Ada runtime, flash layout and fit inside each enclosure
before hardware release; the warning cluster has the greatest peripheral
load. Connector pins, protection ratings, board dimensions and current
budgets remain ICD/power-design work, not assumed from the former controller.

Only the two physical ends of the CAN trunk carry 120-ohm termination.
Instrument drops are short; instrument count does not determine termination
count. All three units receive switched power through protected branches
from the PDM. Assess branch faults and shared-bus failures separately from
isolated node resets.

## 3. Gauge drive

Speedometer and tachometer each drive one X27.168-class gauge stepper locally
through a suitable dual H-bridge/automotive gauge driver. Each homes against
its mechanical stop at boot, retains its own zero/full-scale calibration
and smooths its CAN setpoint with a bounded needle-motion profile.
Motor/driver electrical compatibility and actual step geometry need bench
validation; no stepper phase wiring runs between enclosures.

Speedometer consumes `vehicle_state_fast`; tachometer consumes
`engine_state_fast`, both at 100 Hz. The speedometer reconciles ECU
distance-since-boot and resets/wraps without inventing travelled distance.
Define integration, persistence interval and tolerated power-loss error
under PAR-10/11 before odometer acceptance. Redundant wear-managed SPI NOR
is a candidate for the speedometer; it is not required on all three nodes.
The physical odometer indication/drive must also fit the retained speedometer
enclosure; its mechanism and interface remain part of hardware/packaging review.

Each gauge has local backlighting and applies `dashboard_brightness`.
If that command expires, retain a usable calibrated local default under
PAR-09; loss of warning-cluster dimming must not blank the gauges.

## 4. Warning lamps and switchgear

Provisional LEDs: left/right indicator repeater, high beam, neutral if a
gearbox signal is available, general engine fault, charge, thermal and GPS
fix. Local GPIO/LED drivers provide current limiting and PWM dimming.

The cluster acquires/debounces indicator, hazard, horn, headlight, kill,
mode and brake-switch inputs and publishes `handlebar_switches` at 100 Hz.
These are steady rider-intent bits; ECU generates exterior blink phase
and PDM switches exterior loads. Cluster repeaters blink locally at the
nominal matching cadence; small phase drift remains acceptable.

No exterior lamp, horn or ignition high-current switching belongs in any
instrument enclosure. Rider-stop independence under cluster/CAN failure,
input freshness and switch fail states remain PAR-06/08/09 closure work.

## 5. Twistgrip TPS

AS5600 contactless angle sensor on a small twistgrip satellite board,
connected locally to the warning cluster, not over the full ECU harness.
Calibrate idle/full-open positions in the cluster configuration; publish
filtered percentage, raw angle and validity in `user_input_fast` at 100 Hz.
Detect sensor timeout and magnet faults and do not silently publish stale
data as valid.

Measure cable capacitance, EMC behaviour and bus rise time before accepting
the I2C wiring; a nominal cable length alone does not establish reliability.
The ECU consumes and logs TPS over CAN. Injection must independently assess
actual throttle-body position rather than assume twistgrip angle suffices.

## 6. GPS and brightness

GPS UART/PPS terminates at the warning cluster. A u-blox NEO-M9N-class
receiver/antenna may be installed under a suitable non-metallic area with
sky view; do not assume reception inside a metal instrument housing.
No separate GPS CAN node is added. Publish position/speed at 5 Hz and fix
metadata/UTC at 1 Hz. Report missing/invalid GPS explicitly.

The cluster owns ambient-light acquisition and emits a shared brightness
request at 10 Hz. Each gauge applies its own calibrated intensity curve;
warning LEDs retain their own visibility requirements. The cluster can
use a local default when ALS fails and reports the fault. The twilight
curve, allowed range and command-expiry behaviour require PAR-09 review.

## 7. Service, health and failure isolation

Every node emits its own 1 Hz heartbeat and node-specific fault events.
Diagnostics and CAN updates address each unit separately; each image carries
a target identity. Shared source does not imply one firmware identity.
No instrument requires ECU USB hardware; an external CAN tool or ECU service
bridge can address it.

- Missing ECU heartbeat: speedometer/tachometer hold their own last-known
  needles and use local backlighting to indicate stale data; the cluster
  illuminates a warning independently. Visual cadence/recovery is PAR-09.
- Missing gauge heartbeat: cluster warns for that gauge. Other nodes and
  engine continue; do not represent the missing gauge as healthy.
- Missing warning-cluster heartbeat: gauges retain ECU-driven operation
  and usable local illumination; ECU handles stale TPS/switch inputs under
  an explicitly validated policy.
- A bus short/power short is not an isolated node failure; test it as a
  shared infrastructure fault.

All timeouts, last-value age limits, stale indications and recovery guards
must be verified using [V&V procedures](../project/verification-plan.md).

## Related

- [System](system.md), [ICD](interfaces.md), [CAN specification](can-bus.md)
- [Firmware](firmware.md), [power](power.md), [HIL](hil.md)
- [Sensor installation](../mechanical/sensor-installation.md)
