# ECU subsystem architecture

The engine control unit. Sole node responsible for engine management,
sensor acquisition, data logging, and vehicle-state broadcast.

This document is a subsystem architecture — block level, component
selection, and interface allocation. Schematic-level detail (part
numbers to the pin, exact passive values, layout guidance) lives with
the hardware design when it happens.

Design is constrained by:

- [ADR-0001: Two-node CAN topology](../project/decisions/0001-two-node-can-topology.md)
- [ADR-0002: Skip mechanical points](../project/decisions/0002-skip-mechanical-points.md)
- [ADR-0003: MCU family selection](../project/decisions/0003-mcu-family-selection.md)
- [ADR-0004: Kick-start with flat battery](../project/decisions/0004-kick-start-flat-battery.md)
- [Power architecture](power.md)
- [Measurement plan](../measurement-plan.md)

## 1. Purpose and scope

Owns:

- Crank position acquisition (36-1 Hall).
- Coil driver (external inductive coil, low-side IGBT, integrated Zener
  clamp).
- Front wheel speed acquisition.
- EGT, CHT thermocouple acquisition.
- TPS (contactless twistgrip sensor).
- Ambient temperature, pressure, humidity (BME280).
- IMU (6-axis, ICM-42688).
- Battery and DC bus voltage sensing.
- Data logging to internal SPI NAND flash.
- CAN broadcast of engine and vehicle state (500 kbit/s classic CAN
  via FDCAN peripheral).
- Service USB (single automotive-style connector).
- Charge-controller MOSFET drive for the LiFePO4 battery.
- SWD debug (internal, not routed off the PCB).

Does not own:

- Speedometer/tachometer display drive — handlebar controller.
- Dashboard warning lamps — handlebar controller.
- Turn signals, horn, lighting — handlebar controller.
- GPS — handlebar controller (re-broadcast on CAN).

## 2. Block diagram

    +--------------------------------------------------------+
    |                          ECU                           |
    |                                                        |
    |  +-----+  +-------------+  +---------+  +-----------+  |
    |  | Bus |  | Shunt R/R   |  | Supercap|  |  Charge   |  |
    |  | in  |->| passive rec.|->|  bank   |->| control-  |  |
    |  |     |  | + MOSFET sh.|  |  ~1 F   |  |  ler MOSFETS  |
    |  +-----+  +-------------+  +----+----+  +-----+-----+  |
    |                                 |             |        |
    |                                 v             |        |
    |                          +-----+------+       |        |
    |                          | ECU input  |       |        |
    |                          | protection |       |        |
    |                          | (P-FET ID, |       |        |
    |                          |  TVS, EMI) |       |        |
    |                          +-----+------+       |        |
    |                                |              |        |
    |               +----------------+              |        |
    |               |          +-----v-----+        |        |
    |               |          | 5V buck   |        |        |
    |               |          | + 3.3 LDO |        |        |
    |               |          +-----+-----+        |        |
    |               |                |              |        |
    |  +------------v----------------v----+         |        |
    |  |         STM32H723ZG              |         |        |
    |  |  Cortex-M7 @ 550 MHz             |         |        |
    |  |                                  |         |        |
    |  |  FDCAN1 --> transceiver -------->|--->     |        |
    |  |  USB FS --> ESD --> connector -->|--->     |        |
    |  |  TIM1 IC <-- crank Hall --------<|<---     |        |
    |  |  TIM2 IC <-- wheel Hall --------<|<---     |        |
    |  |  TIM8 OC --> IGBT gate driver -->|--->     |        |
    |  |  SPI1 <----> MAX31855 EGT        |         |        |
    |  |         <--> MAX31855 CHT        |         |        |
    |  |         <--> ICM-42688 IMU       |         |        |
    |  |         <--> W25N01GV NAND       |         |        |
    |  |  I2C1 <---> BME280 ambient       |         |        |
    |  |         <-> AS5600 TPS           |         |        |
    |  |  ADC1  <-- Vbat divider          |         |        |
    |  |        <-- Vbus divider          |         |        |
    |  |        <-- coil current sense    |         |        |
    |  |  GPIO --> charge ctrl MOSFETs -->|--->     |        |
    |  |  UART --> service (spare)        |         |        |
    |  |  SWD  (internal test points)     |         |        |
    |  +----------------------------------+         |        |
    |                                                        |
    +--------------------------------------------------------+
                     |                        |
         Vehicle harness connector    Service connector
         (sensors, coil, power,       (USB + CAN + GND,
          CAN, ignition switch)        automotive-sealed)

## 3. MCU peripheral allocation

**STM32H723ZG** (LQFP-100, 550 MHz Cortex-M7, 1 MB flash, 564 KB RAM,
FDCAN, USB FS, extensive TIMx, I2C, SPI, UART, ADC).

Peripheral assignment (working plan — exact pin choices at schematic
phase):

| Peripheral | Function | Notes |
|---|---|---|
| FDCAN1 | Vehicle CAN, classic 500 kbit/s | Requires external transceiver (TCAN1042 or SN65HVD230) |
| USB OTG FS | Service USB (device mode) | 12 Mbit/s adequate: 128 MB log downloads in ~85 s |
| TIM1 (input capture) | Crank Hall — 36-1 tooth timing | Advanced timer, high-resolution input capture |
| TIM2 (input capture, 32-bit) | Wheel speed Hall | 32-bit prevents rollover ambiguity at low speeds |
| TIM8 (output compare) | Coil driver IGBT gate signal | Advanced timer, complementary output not needed but has BRK |
| TIM3 or TIM4 | Miscellaneous PWM (fan, aux) | Reserved |
| SPI1 | External flash + IMU + MAX31855 ×2 | Separate CS lines, DMA-driven for logging throughput |
| I2C1 | BME280 + AS5600 TPS | 400 kHz fast mode |
| USART1 | Debug UART (SWD-adjacent) | Not routed off-PCB in normal build |
| USART2 | Reserved (future: GPS backup, second CAN) | |
| ADC1 | Vbat, Vbus, coil current sense, MCU internal temp | 12-bit with hardware oversampling to 16-bit |
| GPIO | Battery charge controller MOSFET gates | 2-3 gate lines, boot-safe defaults |
| DMA | SPI TX/RX for flash, ADC scan | Both required for continuous logging |
| SWD | Internal test points only | See §9 |

Peripheral headroom retained: FDCAN2, USB HS, SPI2/3, USART3+, several
TIMx. Sufficient for phase 5+ additions (wideband lambda controller,
extra ADCs) without a board respin.

## 4. Power input and internal rails

Refer to [power.md](power.md) for the vehicle-level architecture. Inside
the ECU enclosure:

- **DC bus input** from the shunt R/R output, buffered by the supercap
  bank. Nominal 8-16 V during operation, absolute max 24 V transient.
- **Input protection stage:** P-channel MOSFET ideal-diode for reverse
  polarity (zero forward drop), TVS clamp above 24 V, common-mode EMI
  filter (ferrite + Cs).
- **5 V rail** via synchronous buck (TPS54xx-class, 8-16 V input, 2 A
  output). Powers Hall sensors, thermocouple front-ends, coil driver
  gate-driver logic side, IMU VDDIO.
- **3.3 V rail** via LDO from 5 V. Powers MCU, BME280, AS5600, SPI NAND,
  CAN transceiver logic side.
- **Charge controller drive:** discrete high-side and low-side MOSFETs
  isolating the battery from the bus, gate-driven by the MCU via level-
  shifting drivers. Firmware arbitrates charge/discharge policy.

Rail sequencing at cold boot (from ADR-0004):

    t = 0:      Bus rises past ~8 V (kick starts stator producing DC)
    t + 5 ms:   Buck starts producing 5 V
    t + 6 ms:   LDO produces 3.3 V
    t + 8 ms:   MCU exits POR
    t + 20 ms:  Bootloader complete, application entry
    t + 50 ms:  Application peripheral init done
    t + 80 ms:  Crank Hall armed, coil driver armed
    t + 100 ms: First spark possible on next crank sync event

100 ms budget is comfortable at 500 RPM (~120 ms per revolution).

## 5. Sensor front-ends

### 5.1 Crank Hall (36-1 trigger)

- Sensor: Honeywell SS411A or equivalent chopper-stabilised Hall with
  push-pull digital output.
- Powered from 5 V rail.
- Signal to MCU: series resistor (~1 kΩ) + ESD clamp diodes to 3.3 V
  and GND, input pin used as TIM1 input capture.
- Optional: Schmitt-trigger buffer on the input if bench measurement
  shows Hall output has significant noise or slow edges. Provision the
  footprint even if unpopulated.
- **Firmware sync algorithm:** capture inter-tooth intervals in a
  circular buffer; the missing tooth appears as an interval ~2× the
  running average. Sync flag set on detection; timing map indexed off
  the sync marker plus tooth count.
- Fault detection: no edges for > 500 ms while engine expected running
  → sensor fault, log, retry sync.

### 5.2 Wheel speed Hall (front wheel)

- Same sensor family as crank Hall.
- Target ring: bespoke small toothed wheel bolted to the front brake
  hub. Tooth count to be determined by required speed resolution and
  packaging — likely 12-24 teeth.
- MCU: TIM2 input capture (32-bit counter avoids rollover issues at low
  vehicle speeds).
- Firmware: instantaneous speed from inter-tooth interval; filtered
  speed for display; per-run velocity trace for coastdown analysis.

### 5.3 EGT thermocouple

- K-type thermocouple with weld-in bung, ~50 mm from exhaust port.
  Sensor tip inside the exhaust flow.
- Front-end: **MAX31855KASA** (SPI, integrated cold-junction
  compensation, digital output in ¼ °C).
- Range: 0-1200 °C, adequate for two-stroke EGT (typically 500-800 °C).
- CS driven from MCU GPIO; shares SPI1 bus.
- Sample rate: 5 Hz.

### 5.4 CHT thermocouple

- K-type in a spark-plug washer or head-fin bracket.
- Front-end: **MAX31855KASA** identical to EGT channel.
- Range: 0-1200 °C (huge overkill for CHT), part choice unified for
  BOM simplicity.
- Sample rate: 1 Hz.

**Alternative for CHT:** NTC thermistor in a head-fin bracket. Simpler
(single ADC channel, one resistor), cheaper. Choice deferred to bench
comparison of installation options.

### 5.5 TPS

- Sensor: **AS5600** — 12-bit contactless magnetic rotary encoder,
  I2C output.
- Small diametric magnet on the twistgrip shaft; sensor on a bracket
  fixed to the handlebar.
- I2C address 0x36 (fixed); shares I2C1 with BME280 (address 0x76).
- Sample rate: 100 Hz.
- Fault detection: I2C timeout, magnet-lost bit in AS5600 status
  register.

Note: TPS is *commanded* throttle (twistgrip position), not carburettor
slide position. Cable slack/wear introduces a small offset. Acceptable
for phase 1; revisit if carburettor is later replaced.

### 5.6 Battery and DC bus voltage sensing

- Two independent divider networks:
  - Vbus (measured after supercap, before charge controller)
  - Vbat (measured on battery side of charge controller)
- Each ~1:6 ratio, feeding an ADC1 channel.
- 100 kΩ + 20 kΩ divider gives 6 µA continuous draw — acceptable.
- Sample rate: 10 Hz.
- Also used by firmware to control the charge controller MOSFETs.

### 5.7 Ambient sensor (BME280)

- **BME280** — I2C, temperature/pressure/humidity.
- Sensor location: inside the ECU enclosure but with a vented port to
  the outside airflow. Vent designed to keep water out but allow
  pressure equalisation.
- Sample rate: 1 Hz.

### 5.8 IMU (ICM-42688)

- **ICM-42688-P** — 6-axis (accel + gyro), SPI, low noise, 32 kHz
  internal ODR capable.
- Mounted on ECU PCB. Enclosure orientation on the vehicle recorded in
  configuration; firmware rotates raw axes to vehicle frame.
- Sample rate: 200 Hz (for coastdown-quality acceleration reference).
- Shares SPI1 bus.

### 5.9 Coil primary sense

- Not a sensor per se — the coil driver includes:
  - Gate drive voltage sensed on ADC1 (windowed capture, 100 kHz
    during firing).
  - Primary current via a low-value sense resistor between the coil's
    low side and the IGBT, differential-amplified to a single-ended
    signal on ADC1.
- Feeds spark-energy characterisation and misfire detection in later
  phases.

## 6. Coil driver

### 6.1 Topology

Low-side inductive (Kettering) with an external coil:

    Battery +
       |
       +----[ External ignition coil primary ]----+
                                                  |
                                              Drain of IGBT
                                                  |
                                              +---+---+
                                              |       |
                                          Zener    Gate <- gate driver
                                          clamp        (from TIM8 OC)
                                              |
                                              +
                                              |
                                          Sense R
                                              |
                                           Ground (star)

### 6.2 Part selection

- **IGBT: Bosch BIP373** or **STMicroelectronics VB525SP** or similar
  automotive smart-IGBT with integrated Zener clamp at ~380 V and
  built-in ESD protection. These parts are designed for exactly this
  application and eliminate the discrete snubber network.
- **Gate driver:** dedicated non-isolated gate driver IC (e.g. TC4420
  or on-IGBT integrated driver) rated for the IGBT's gate charge.
- **Sense resistor:** ~10-50 mΩ, non-inductive, sized for ~50-500 mV
  full-scale over the coil primary current range.
- **Differential amp for sense:** INA240 or similar high-CMRR current-
  shunt monitor.

### 6.3 Firmware control

- Dwell time (time IGBT is held on, building coil current) commanded
  by MCU based on a battery-voltage-compensated table.
- Spark event triggered by TIM8 output compare configured against the
  crank sync + timing map.
- Fault flag if primary current fails to reach expected value during
  dwell (open coil, driver fault).
- Fault flag if drain voltage doesn't collapse post-spark (short
  circuit, no spark).

### 6.4 Layout constraints (flagged for schematic phase)

- **Star ground for coil return** — critical, must not share ground
  path with sensor grounds.
- Coil driver on its own supply domain (direct battery/bus feed, not
  through the ECU input protection stage, to handle the 5-10 A pulsed
  current without disturbing the sensor rails).
- Copper pour for heat spreading on the IGBT.

## 7. Storage

### 7.1 Firmware storage (MCU internal flash)

STM32H723 has 1 MB internal flash.

Partitioning:

- **Bootloader**: 64 KB. Immutable after production; verifies
  application signature, selects boot slot, cold-starts fast for the
  ADR-0004 kick-start scenario.
- **Application slot A**: 448 KB.
- **Application slot B**: 448 KB.

A/B slots enable safe firmware update: writer flashes B, marks it
valid, next reboot boots B; if B fails to signal healthy within N
seconds, bootloader falls back to A. Standard pattern.

### 7.2 Configuration store

Dedicated 32 KB region of MCU internal flash, formatted as a small
log-structured store with wear leveling. Holds:

- Ignition timing map(s).
- Crank angle sync offset calibration (measured at installation).
- Sensor calibrations (thermocouple cold-junction offset, TPS zero,
  battery divider ratios).
- Vehicle-frame IMU rotation matrix.
- Odometer counters (though these may live on the handlebar
  controller instead — decision open).
- Fault history (recent).

Reset-to-defaults path in bootloader for recovery.

### 7.3 Log store (external SPI NAND)

- **Winbond W25N01GV** — 1 Gbit (128 MB) SPI NAND. Or a lower-density
  W25N512 (64 MB) if 128 MB proves excessive after phase 3.
- Custom append-only log format, sized for the phase-1 channel set
  (~22 MB/hour continuous). 128 MB gives ~5 hours of continuous
  logging.
- Sequential write pattern aligns with NAND's strengths; wear leveling
  is straightforward for append-only.
- Bad-block management in firmware.
- Circular overwrite when full: newest data preserved, oldest
  overwritten. High-rate windows (§ measurement plan) marked with a
  no-overwrite flag until downloaded.
- USB service session lists sessions, allows selective download.

Log format (working plan):

- Fixed-size superblock at each erase-block boundary with channel
  table, session ID, wall-clock offset.
- Records within a superblock: fixed-rate frames + event frames,
  timestamped in ECU monotonic time.
- Post-download conversion to MCAP or Parquet for analysis.

## 8. Interfaces

### 8.1 CAN

- FDCAN1 in classic mode, 500 kbit/s.
- External transceiver (TCAN1042 or SN65HVD230) with ESD protection.
- 120 Ω termination on the ECU side (this node is one bus end).
- Periodic message plan captured separately in
  `docs/architecture/can-bus.md` and `protocol/messages.yaml`.

### 8.2 USB service

- USB OTG FS in device mode.
- Enumerates as a composite device:
  - CDC-ACM for command/response (calibration, ignition-map upload,
    fault log dump).
  - MSC or vendor-specific for bulk log download.
- Bootloader also enumerates USB (in a distinct configuration) for
  firmware update. Bootloader USB stack must be tiny and self-
  contained.

### 8.3 SWD

- Internal PCB test points, not routed through the vehicle harness or
  the service connector.
- ARM 10-pin or 4-pin Cortex-M compact footprint. Pogo-pin or header,
  populated only for development boards.

## 9. Connectors

Two connectors on the enclosure:

**Vehicle harness connector** — main. Carries:

- DC bus power in (from R/R output side)
- Ground
- CAN H, CAN L
- Ignition switch sense line (voltage from switched rail)
- Sensor lines (crank Hall, wheel Hall, TPS, EGT+, EGT−, CHT+, CHT−)
  — for TPS this is the twistgrip AS5600's I2C running as long-cable;
  see below.
- Coil driver output (IGBT drain to coil primary), coil primary return
- Charge controller drive lines (or the charge controller is on the
  battery pack side; see open questions)
- Reserved future channels: wideband lambda, MAP, second temp

Connector candidate: **TE Superseal 1.0 series** or **Deutsch DT
series** — sealed, IP67, automotive-grade, hand-crimpable.
Pin count roughly 20-30 depending on final channel list.

**Service connector** — separate, smaller:

- USB (5 V, D+, D−, GND)
- CAN H, CAN L, GND (for diagnostic tools that connect via CAN
  independent of USB)

Connector candidate: **Deutsch DT-06-4S** for CAN + **automotive-
grade USB-C receptacle** with sealed cap. Or a purpose-built
combined connector.

**Regarding long-cable I2C for TPS at handlebar**: I2C is not ideal
over a metre-plus cable due to capacitance. Options:

- Terminate TPS I2C at the handlebar controller, which broadcasts TPS
  on CAN back to the ECU. Cleaner architecturally — TPS becomes a
  handlebar-side sensor whose value the ECU consumes over CAN. Decision
  moved to the handlebar controller doc.

Working assumption for this doc: TPS is a handlebar controller
responsibility, ECU receives it over CAN. Update to the sensor-list
above is deferred until the handlebar controller doc formalises it.

## 10. Enclosure and thermal

- **Aluminium extruded enclosure**, IP65-rated. Approximate internal
  volume based on PCB footprint of ~100 × 120 mm and full-height
  components ~40 mm.
- Sealed with silicone gasket; two threaded ports for the two
  connectors, each with its own gasket.
- Wall thickness sufficient to act as a heat spreader for the coil
  driver IGBT (thermal pad + spring clip to inside wall).
- **BME280 ambient port:** small hooded vent with Gore-Tex-style
  membrane, allowing pressure equalisation and humidity sensing
  without admitting liquid water.
- **Mount:** four M5 or M6 bolts to a bracket welded or bolted to the
  frame. Rubber isolators between enclosure and bracket to attenuate
  chassis vibration into the crystal oscillator and IMU.
- Location on vehicle: TBD after frame inspection. Candidate zones:
  behind side cover near airbox, under seat, or in a fabricated
  cavity in the frame's central spine.

Thermal budget:

- MCU under full load: ~2.5 W.
- Coil driver: ~1-2 W average at running RPMs (dominated by IGBT
  switching + conduction losses).
- Buck + LDO: ~0.5 W.
- Sensors, transceivers: ~0.5 W.
- **Total ~5 W** typical, ~10 W worst case.

At 5 W dissipated to a 200 cm² aluminium enclosure with reasonable
airflow, ambient-to-internal rise is 15-25 °C. Acceptable for the
0-40 °C ambient range of Portuguese Sunday-riding.

## 11. Fault diagnostics

Categories of fault the ECU must detect, log, and (where relevant)
signal via CAN:

**Hardware faults:**

- Coil driver open (no primary current during dwell) → log, degrade to
  low-dwell attempt on next cycle.
- Coil driver short (drain doesn't recover post-spark) → cut coil
  drive, log, warn.
- Crank Hall silent → log, engine cannot run.
- Wheel Hall silent while running (with engine RPM up) → log, don't
  suppress engine.
- Thermocouple open (MAX31855 fault bit) → log, exclude from mixture-
  warning logic.
- I2C bus timeout → log, degrade dependent sensor.
- SPI NAND write failure → log, retry, degrade to no-log if repeated.
- MCU overtemperature → log, warn via CAN.

**Firmware faults:**

- Watchdog: window watchdog on STM32H7, refreshed by application
  scheduler.
- Stack overflow (compile-time analysis + runtime sentinel).
- Assertion violation (Ada preconditions where applicable) → log
  cause + PC, restart to safe-timing map.

**Sensor plausibility:**

- Battery voltage out of range → log.
- Ambient values out of range → log, don't correct data.
- IMU calibration divergence → log.

**Fault log:**

- Persistent in the config-store flash region.
- Circular ~200-entry buffer.
- Downloadable via USB service.
- Recent entries broadcast on CAN on request (for handlebar
  controller warning-lamp logic).

## 12. Development sequencing

Recommended bring-up order for the hardware and firmware (phase 2 of
the [staged plan](../project/staged-plan.md)):

1. **Bare PCB power-on:** power the input stage from a bench PSU, verify
   5 V and 3.3 V rails, verify MCU exits POR. No firmware needed.
2. **Bootloader alive:** flash minimal bootloader, blink LED, respond
   over UART.
3. **SPI/I2C bring-up:** enumerate NAND, IMU, thermocouple, BME280 via
   simple probes.
4. **CAN loopback:** two ECU prototype boards, or one ECU + a USB-CAN
   dongle, exchange test frames.
5. **USB enumeration:** service session on a laptop.
6. **Trigger wheel HIL:** small motor spinning a trigger wheel,
   MAX firing a coil into a dummy load, verify timing on scope.
7. **Cold-boot timing:** measure end-to-end cold-boot time against the
   100 ms budget from ADR-0004. Iterate on bootloader and app init
   until met.
8. **First engine start:** phase 3 begins.

## 13. Open questions

- **Charge controller topology** — dedicated BMS IC vs. discrete ECU-
  controlled MOSFETs. Discrete preferred for logging flexibility.
  Decision at ECU schematic phase.
- **CHT sensor type** — MAX31855 K-type vs. NTC thermistor. Bench
  comparison during phase 2.
- **Wheel-speed target tooth count** — driven by packaging on the
  brake hub. Determined during phase 0/1 mechanical work.
- **ECU physical mounting location on the frame** — determined
  during frame inspection in phase 0.
- **External coil model** — deferred; drives the IGBT drive
  parameters.
- **Log format** — self-describing binary custom vs. MCAP-native on
  device. Custom is simpler on device; MCAP-native is friendlier for
  tools. Decision needed before firmware log module is written.
- **Odometer persistence location** — ECU config store vs. handlebar
  controller. Handlebar makes more sense (survives ECU replacement
  during development). Confirm in handlebar controller doc.
- **TPS ownership** — provisionally on handlebar controller
  (§9 note). Confirm.

## Related

- [System architecture](system.md)
- [Power architecture](power.md)
- CAN bus — to be written
- Handlebar controller — to be written
- Firmware architecture — to be written
