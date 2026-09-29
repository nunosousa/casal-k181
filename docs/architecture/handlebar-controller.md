# Handlebar controller subsystem architecture

The handlebar-mounted intelligent node. Drives the three passive
dashboard enclosures, handles handlebar switchgear, drives all vehicle
lamps, hosts the GPS module, hosts the TPS sensor, and participates on
CAN as consumer of engine state and producer of user-input and GPS
state.

Constrained by:

- [ADR-0001: Two-node CAN topology](../project/decisions/0001-two-node-can-topology.md)
- [ADR-0003: MCU family selection](../project/decisions/0003-mcu-family-selection.md)
- [System architecture](system.md)
- [Power architecture](power.md)
- [CAN bus](can-bus.md)

Also referred to as the *body-control module* in some places, but the
handlebar controller name is preferred since "BCM" carries automotive
connotations that overspecify what this thing is.

## 1. Purpose and scope

Owns:

- Speedometer and tachometer needle drive (two stepper motors in
  passive dashboard enclosures).
- Warning-lamp cluster drive (LEDs).
- Dashboard illumination.
- Front indicator, rear indicator, rear brake, rear tail, horn, and
  headlight (low/high) drive.
- Handlebar switchgear inputs (indicator, hazard, horn, headlight,
  kill switch, mode buttons, brake switches).
- Turn-signal and hazard timing.
- Twistgrip TPS sensor (AS5600 I2C).
- GPS module (u-blox class, UART).
- Odometer persistence.
- CAN participation as documented in [`messages.yaml`](../../protocol/messages.yaml).

Does not own:

- Engine management — ECU.
- Rider-observed speed (measurement) — ECU (from front wheel Hall);
  handlebar receives the value on CAN and drives the needle.
- Data logging — ECU. The handlebar has no bulk log storage, only a
  small config/odometer/fault store.

## 2. Block diagram

    +----------------------------------------------------------+
    |                Handlebar controller                       |
    |                                                           |
    |  +--------+    +-----------+                             |
    |  | 12V in |--->| Reverse-  |                             |
    |  |        |    | polarity, |                             |
    |  |        |    | TVS, EMI  |                             |
    |  +--------+    +-----+-----+                             |
    |                      |                                    |
    |               +------v------+  +--------+                |
    |               |  5 V buck   |->| 3.3 V  |                |
    |               |             |  |  LDO   |                |
    |               +------+------+  +---+----+                |
    |                      |             |                     |
    |               +------v-------------v-----+               |
    |               |     STM32G474RE          |               |
    |               |     Cortex-M4 @ 170 MHz  |               |
    |               |                          |               |
    |               |  FDCAN1 -> transceiver ->|--> CAN bus    |
    |               |  I2C1  <-> AS5600 TPS    |   (short cable) |
    |               |        <-> BME280 ??     |   (dropped, ecu owns)
    |               |  USART1 <-> GPS module   |   (short cable) |
    |               |  SPI1  <-> W25Q16 flash  |               |
    |               |        <-> tach driver   |               |
    |               |        <-> speedo driver |               |
    |               |  TIM1  -> stepper phases |               |
    |               |  TIM8  -> stepper phases |               |
    |               |  TIM3  -> LED PWMs       |               |
    |               |  GPIO  -> lamp MOSFETs   |               |
    |               |        <- switch inputs  |               |
    |               |  ADC1  <- Vbat divider   |               |
    |               |        <- ALS ADC        |               |
    |               |  SWD (internal only)     |               |
    |               +----+----+----+-----+-----+               |
    |                    |    |    |     |                     |
    |                    v    v    v     v                     |
    |             stepper1 stepper2 LEDs  MOSFET lamp banks    |
    |                                                           |
    +----------------------------------------------------------+
           |                                    |
    Local (short) wiring to dashboard    Long wiring to rear
    enclosures and headlight-area        lamps (via harness)
    switchgear

## 3. MCU peripheral allocation

**STM32G474RE** (LQFP-64, 170 MHz Cortex-M4 with SP FPU, 512 KB flash,
128 KB RAM, FDCAN, no USB required for this node).

Peripheral assignment (working plan — exact pin choices at schematic
phase):

| Peripheral | Function | Notes |
|---|---|---|
| FDCAN1 | Vehicle CAN, classic 500 kbit/s | External transceiver + 120 Ω termination (this node is the other bus end) |
| I2C1 | AS5600 TPS + ambient light sensor | Short local wiring, 400 kHz |
| USART1 | GPS module UART | 9600 or 38400 baud, u-blox class |
| USART2 | Reserved (debug UART) | Not routed off-PCB |
| SPI1 | W25Q16 config flash + stepper motor drivers (if driver ICs use SPI); if dual-H-bridge ICs are used, SPI is only for flash | |
| TIM1 CH1-CH4 | Speedometer stepper motor drive (2 phases × 2 half-bridges) | Advanced timer, complementary PWM |
| TIM8 CH1-CH4 | Tachometer stepper motor drive | Same |
| TIM3 | Warning-lamp and illumination LED PWM (multi-channel) | Common intensity/dimming |
| TIM4 | Turn-signal / hazard blink timing | Software timer capable as well |
| GPIO (outputs) | Rear brake, rear tail, front-L, front-R, rear-L, rear-R, headlight-low, headlight-high, horn | Each drives an N-MOSFET low-side switch |
| GPIO (inputs) | 10-12 switch inputs with internal pull-up and external RC debounce | ESD-protected |
| ADC1 | Vbat, ambient light (analog), MCU internal temp | 12-bit |
| SWD | Internal PCB test points only | |

Peripheral headroom retained: FDCAN2, USART3+, several TIMx.

## 4. Power input and internal rails

- **Input:** switched 12 V rail from the ignition switch. The handlebar
  does not require always-on power — when the ignition is off, all
  dashboard functions are off.
- **Standby persistence** is handled by writing the odometer counter
  to flash before the switched rail collapses (few ms of buck reserve
  is sufficient; input electrolytic buffers this).
- **Input protection:** reverse-polarity ideal-diode (P-MOSFET), TVS
  clamp, EMI filter. Same pattern as the ECU input stage but simpler
  (no supercap, no charge controller — this is a straightforward 12 V
  input).
- **5 V rail** via synchronous buck. Powers steppers, LEDs, sensor
  rails.
- **3.3 V rail** via LDO. Powers MCU, TPS, GPS, flash, transceiver.

Total draw budget: ~3-5 W (steppers ~1 W transient, LEDs ~1 W, MCU
~0.5 W, GPS ~0.3 W, headroom for illumination).

## 5. Dashboard drive

### 5.1 Speedometer and tachometer needles

Two automotive **X27.168-class stepper motors** (Switec/Juken), one per
gauge. Standard part in modern instrument clusters; small, quiet,
zero-cost per unit at hobby quantities.

Characteristics:

- ~4320 steps per revolution (1/12° per step).
- Bipolar, two phases 90° apart.
- ~30-50 mA per phase at 5 V drive.
- Return-to-zero calibration: driven against the built-in mechanical
  stop at boot to establish zero position.

Drive electronics per motor:

- **Dual H-bridge IC** — DRV8848 or DRV8837 dual-configuration. One IC
  per motor.
- Firmware generates sinusoidal PWM on the two H-bridge inputs at
  ~200 Hz effective phase-current update rate, producing smooth
  microstepped needle movement.
- Position tracked in firmware (open-loop; the mechanical stops give
  the only absolute reference).

Alternative considered: dedicated stepper driver ICs with step/dir
input (AMIS-30623, MLX90410). Better packaging but locks the drive
profile. Rejected in favour of software microstepping for flexibility.

Signal path: `engine_state_fast.rpm` and `vehicle_state_fast.wheel_speed_mps`
consumed at 100 Hz from CAN. Applied to a target-position setpoint;
firmware runs a critically-damped second-order response so the needles
move smoothly rather than jumping.

### 5.2 Warning-lamp cluster

Third dashboard enclosure. Contains an array of LEDs — provisional
list:

- Left indicator repeater
- Right indicator repeater
- High-beam indicator
- Neutral (if applicable — depends on gearbox provision)
- Engine warning (general fault, from ECU heartbeat fault-summary bits)
- Battery / charge warning
- EGT / thermal warning
- GPS fix acquired

LED drive:

- Individual low-side N-channel logic-level MOSFETs (e.g. AO3400 or
  BSS138), one per LED (or per LED group).
- GPIO drives the gate directly.
- PWM for dimming via TIM3 shared across all warning LEDs (single
  common dim level for the cluster).

### 5.3 Illumination

Dial-face backlighting via small LED strip or discrete LEDs behind the
speedometer and tachometer dial faces.

- PWM-dimmed via TIM3 channel (separate from warning-lamp channel).
- Colour: warm white to match a 1970s dashboard aesthetic. Alternative:
  green amber to match period Italian-motorcycle idiom. User
  preference, deferred.
- Auto-dim: an ambient light sensor (TSL2591 or a simple photoresistor
  ADC input) provides day/night adaptive brightness.

## 6. Rear lamps, indicators, horn, headlight

All vehicle exterior lamps driven from this node via low-side N-MOSFETs.
Long wire runs to rear lamps acceptable — LED current levels are low
(hundreds of mA at most) so voltage drop over 1-2 m of automotive
harness wire is negligible.

Outputs (one MOSFET each):

- Front indicator L
- Front indicator R
- Rear indicator L
- Rear indicator R
- Rear tail
- Rear brake
- Headlight low
- Headlight high
- Horn (via a small relay for higher current if a mechanical horn is
  retained; otherwise direct MOSFET for an electronic horn)

Each MOSFET: N-channel logic-level, ~10 A capable (headroom over LED
loads), TVS on drain for inductive-load protection (relevant to horn).

Timers:

- Turn-signal blink: TIM4 or software timer, ~1.5 Hz on/off.
- Hazard: same, but drives both indicators simultaneously.

## 7. TPS input

**AS5600** contactless magnetic rotary encoder on the twistgrip.

- Small diametric magnet on the twistgrip shaft's end (a small
  adapter piece bonded to the end of the throttle grip).
- AS5600 IC on a small satellite PCB mounted rigidly on the handlebar
  bracket, ~1 mm gap to the magnet.
- Short I2C cable from the handlebar controller board (in the headlight
  nacelle) to the twistgrip satellite: ~30 cm.
- I2C at 400 kHz, well within specification for that cable length.
- Address 0x36 (fixed); shares I2C1 with the ambient light sensor
  (0x29 or similar).
- Firmware maps raw angle to throttle percentage using a calibration
  captured at first setup (idle stop and full-open positions).
- Broadcasts on CAN 0x300 (`user_input_fast`) at 100 Hz.

## 8. GPS

**u-blox NEO-M9N** class, active patch antenna.

- Module physically located inside the headlight nacelle or under an
  adjacent plastic panel (mounted for sky view). See [system
  architecture](system.md) for the constraint that steel bodywork
  blocks GPS.
- 3.3 V logic-level UART, 38400 baud typical (u-blox default 9600;
  reconfigure at first boot).
- PPS output line: connect to a GPIO with input capture. Optional but
  useful — provides a hardware pulse aligned with UTC second boundaries
  for high-accuracy time correlation. Firmware use of PPS is deferred;
  wire it now, decide firmware use later.
- Firmware parses NMEA (or ublox binary protocol UBX for lower CPU).
- CAN broadcasts: `gps_position` (0x400, 5 Hz), `gps_speed_alt` (0x410,
  5 Hz), `gps_fix_state` (0x420, 1 Hz).

## 9. Storage

**W25Q16JV** — 16 Mbit / 2 MB SPI NOR flash. Modest size, appropriate
for the handlebar's needs.

Partitioning:

- **Bootloader**: 64 KB of MCU internal flash (identical pattern to
  ECU).
- **Application slot A**: 224 KB internal flash.
- **Application slot B**: 224 KB internal flash.
- **Configuration** (internal flash): 16 KB.
- **External W25Q16**: odometer + fault log.

Odometer persistence:

- Distance-tracking counter updated in RAM as CAN wheel-speed frames
  arrive.
- Committed to flash on ignition-off (buck reserve carries the ~10 ms
  needed to write) and on periodic 60 s intervals.
- Redundant copy in a second flash sector to guard against half-written
  updates.

The handlebar owns the odometer rather than the ECU because it
survives ECU reflash/replacement during development.

## 10. Interfaces

### 10.1 CAN

- FDCAN1 in classic mode, 500 kbit/s.
- External transceiver + 120 Ω termination (this node is one bus end).
- Message set per [`messages.yaml`](../../protocol/messages.yaml).

### 10.2 Service

No dedicated service USB. Handlebar-specific service (odometer reset,
gauge calibration, warning-lamp test) is performed over CAN via
diagnostic frames 0x702/0x703. A tool connected to the ECU's service
USB, or directly to the CAN bus at the service connector, can address
the handlebar.

### 10.3 SWD

Internal PCB test points, not routed off the PCB. Populated only for
development boards.

## 11. Connectors

Two connectors on the enclosure:

**Main harness connector** — carries:

- Switched 12 V power in, ground.
- CAN H, CAN L.
- Rear lamp drives (indicator L, indicator R, tail, brake) — 4 signals.
- Headlight drives (low, high) — 2 signals.
- Horn drive.
- Reserved (2-4 pins).

Connector candidate: **TE Superseal 1.5** or **Deutsch DT** family,
sealed, ~15-20 pin.

**Dashboard/switchgear connector** — carries:

- 5 V and 3.3 V sensor rails.
- Speedometer stepper drive (4 wires).
- Tachometer stepper drive (4 wires).
- Warning-lamp cluster (~10 GPIO drives plus common cathode).
- Front indicator L/R drives.
- Dashboard illumination LED PWM + common.
- Switch inputs (indicator L/R switch, hazard, horn, headlight, kill,
  mode buttons, brake) — ~10 signals with common ground.
- TPS I2C (SDA, SCL, VCC, GND) — 4 signals.
- Ambient light sensor lines.

Connector candidate: **JST GH** or **Molex Micro-Fit** — 30-40 pin,
compact. This connector stays inside the headlight nacelle and does
not see rain directly, so a non-sealed IP52-class connector is
adequate.

## 12. Enclosure and thermal

- **Small aluminium enclosure**, ~60 × 40 × 20 mm, IP54.
- Mounted inside the headlight nacelle, rubber-isolated.
- No cooling required — total dissipation ~3-5 W spread across a
  substantial enclosure surface.
- The stepper drivers are the hottest components (~0.3 W each). Board
  layout should keep them near the enclosure wall for conduction to
  ambient.

## 13. Fault diagnostics

Detected and logged by the handlebar controller:

- CAN bus-off event.
- Missing ECU heartbeat (see [can-bus §8](can-bus.md)).
- TPS I2C timeout or AS5600 magnet-lost bit.
- GPS UART silence > 5 s (log; not fatal).
- Ambient light sensor timeout (log; falls back to default brightness).
- SPI NOR flash write failure (log; odometer counter switches to
  redundant copy).
- Stepper motor stall — detectable via H-bridge current sense if
  provisioned. Optional in phase 1.
- Switch input stuck (same value > 60 s while ignition on) — log,
  ignore.

Fault-summary bits are placed in the `handlebar_heartbeat.fault_summary`
CAN signal at 1 Hz.

Watchdog: window watchdog on STM32G4, refreshed by application
scheduler.

## 14. Development sequencing

Recommended bring-up (phase 2, in parallel with ECU bring-up):

1. Bare board power-on, verify rails, verify MCU exits POR.
2. Bootloader alive, blink LED, respond over UART.
3. Flash + CAN bring-up. Two-node echo test with the ECU (or with a
   USB-CAN dongle if the ECU isn't ready yet).
4. Stepper motor bring-up: return-to-zero, sweep to full-scale, verify
   motion profile.
5. LED cluster bring-up: individually flash each warning lamp.
6. AS5600 TPS bring-up: read raw angle, calibrate zero/full.
7. GPS bring-up: NMEA parsing, first fix acquisition.
8. Illumination auto-dim: verify light-sensor curve.
9. Integrate with ECU on the vehicle harness.

## 15. Open questions

- **Ambient light sensor** — TSL2591 vs. a simple photoresistor + ADC
  channel. Photoresistor is cheaper and simpler; TSL2591 is more
  precise. Choice deferred.
- **Dashboard illumination colour** — warm white vs. period amber.
  Aesthetic decision, defer to a mock-up.
- **Horn: mechanical or electronic**. Mechanical horns draw ~2-3 A and
  need a relay; electronic horns are lower current. Original K181
  probably had a mechanical horn; character-preservation may favour
  keeping it.
- **Neutral indicator** — depends on whether the 5-speed gearbox
  provides a neutral sensor. Deferred to gearbox inspection.
- **Ambient sensor location** — the [ECU doc](ecu.md) currently places
  BME280 on the ECU. If measurement quality proves poor there, moving
  it to the handlebar (better airflow, further from engine heat) is a
  future refinement. Not implemented in phase 1.
- **Stepper stall detection** — cost/benefit unclear for phase 1.
  Provision the current-sense resistors in the layout; leave the
  sense amplifier optional-populate.
- **Dial-face reproductions vs. originals** — sourcing question. Not a
  firmware or hardware constraint.

## Related

- [System architecture](system.md)
- [ECU subsystem](ecu.md)
- [CAN bus](can-bus.md)
- [`protocol/messages.yaml`](../../protocol/messages.yaml)
- Firmware architecture — to be written
