# ADR-0003: MCU family selection — STM32H7 (ECU) and STM32G4 (handlebar controller)

**Status:** Proposed
**Date:** 2026-09-28

## Context

The two-node CAN topology (ADR-0001) implies two independent MCU
selections. The ECU has hard real-time engine-control workload; the
handlebar controller has soft real-time UI and body-control workload.
Different requirements, but strong preference for staying inside a
single vendor family to share tooling and knowledge.

Language preference: **Ada** for the ECU's riding application and
possibly the handlebar controller's application. C is acceptable for
bootloader, USB, and low-level infrastructure. This is a hard constraint
on the MCU ecosystem: Ada's practical embedded targets are limited to
families where GNAT's runtime and BSP work is mature.

Non-goals:

- Squeezing the smallest, cheapest MCU possible.
- Cortex-M0/M0+ minimalism.
- Chasing the latest silicon.

Requirements summary:

**ECU:**
- CAN 2.0B (FDCAN peripheral acceptable, used in classic mode).
- ≥ 4 timer channels with high-resolution input capture (crank trigger).
- ≥ 2 timer channels with output compare (coil driver, PWM).
- ≥ 8-channel 12-bit ADC (thermocouple amps, TPS, battery, sensors).
- USB device (service connector).
- SPI (external NOR flash for logs, IMU).
- I2C (BME280).
- ≥ 2 UARTs (GPS backup, service, debug).
- ≥ 512 KB flash, ≥ 128 KB RAM.
- Headroom for later phases (crank-dynamics FFTs, adaptive control
  algorithms).
- Ada tooling maturity.
- Available in a hand-solderable package (LQFP preferred).
- Long-term availability.

**Handlebar controller:**
- CAN 2.0B or FDCAN.
- Stepper motor drive (either integrated PWM channels driving external
  driver ICs like TMC2209/DRV8825, or dedicated automotive gauge stepper
  drivers).
- LED PWM outputs.
- Button/switch input pins with internal pull-ups.
- UART for GPS.
- Modest flash and RAM (~128 KB flash, 32 KB RAM sufficient).
- Same family as ECU preferred for tooling.

## Decision

**ECU: STM32H723ZG (Cortex-M7 at 550 MHz, 1 MB flash, 564 KB RAM,
LQFP-100).**

**Handlebar controller: STM32G474RE (Cortex-M4 at 170 MHz, 512 KB flash,
128 KB RAM, LQFP-64).**

Both STMicro STM32, both with FDCAN peripherals (used in classic mode
initially), both with well-supported GNAT runtimes via the
Ada Drivers Library and Alire/ada-runtime-crates.

## Rationale

STM32H7 for the ECU:

- Massive headroom: Cortex-M7 with DP FPU, 550 MHz, single-precision
  and double-precision floats fast enough for any signal processing we
  might do at the crank frequency.
- FDCAN peripheral (used as classic CAN at 500 kbit/s).
- USB HS device.
- Extensive high-resolution timers (HRTIM available for coil-driver
  fine control if needed later; standard TIM1/TIM8 more than adequate
  for phase 1).
- 12-bit ADCs with hardware oversampling to 16-bit.
- LQFP-100 is hand-solderable with a hot-air station.
- Very well-supported in GNAT — the Ada Drivers Library targets STM32H7
  directly. Alire has ready toolchain packages.
- Enterprise-scale silicon that is not going obsolete soon.

STM32G4 for the handlebar controller:

- Same vendor family — tooling, header conventions, HAL patterns, and
  debug workflow transfer directly from the ECU work.
- FDCAN peripheral (also classic-mode).
- Cortex-M4 with SP FPU — adequate for gauge kinematics and turn-signal
  timers.
- 170 MHz, plenty of margin for the workload.
- LQFP-64 is very hand-solderable.
- Well-supported in GNAT.
- Cost is a fraction of the H7.

## Consequences

Positive:

- Both firmware images build with GNAT, letting the Ada preference stand
  from day one.
- Shared FDCAN peripheral: shared CAN driver code between nodes.
- Shared vendor HAL/BSP conventions.
- Substantial headroom on both nodes for later phases and mission creep.
- LQFP packages allow prototype boards to be hand-assembled without a
  reflow oven.

Negative:

- STM32H7 is overkill for phase 1. Bill of materials is higher than
  necessary. Acceptable: this is a one-off vehicle, not a mass product.
- Two different chip variants means two different flash programming
  scripts, two different linker files, two different memory maps.
  Mitigated by keeping the bootloader interface and log format
  identical across nodes.
- FDCAN peripheral operated in classic mode is slightly odd — a
  plain bxCAN would have been simpler — but classic-mode FDCAN is a
  well-trodden path and the code differences are minor.

## Alternatives considered

- **NXP S32K family** (automotive, Cortex-M4/M7): mature automotive
  ecosystem, but Ada support is much weaker. Rejected on tooling.
- **Renesas RH850 / RA family**: aggressive automotive positioning,
  minimal community Ada support. Rejected on tooling.
- **Microchip SAM E70/E51**: Cortex-M7 with CAN, some GNAT support.
  Rejected because the STM32 GNAT ecosystem is measurably more mature.
- **Nordic nRF series**: BLE-oriented, poor fit for CAN-based
  vehicle-electronics work. Rejected on requirements.
- **STM32F4 for the ECU** (older, cheaper, Cortex-M4 at 168 MHz):
  adequate for phase 1 but leaves no headroom for later crank-dynamics
  work. Rejected on headroom.
- **STM32F7 for the ECU** (Cortex-M7 at 216 MHz): reasonable middle
  ground. Rejected because STM32H7 is roughly the same board complexity
  and gives 2.5× the compute for a small BOM cost increase.
- **STM32G0 for the handlebar controller**: cheaper than G4, but no
  FDCAN (some variants have bxCAN, others none) and less headroom.
  Rejected to keep the CAN peripheral consistent across both nodes.
- **RP2040 (Raspberry Pi Pico silicon)**: cheap and interesting, but no
  CAN peripheral (needs external MCP2515), and Ada support is
  experimental. Rejected on requirements and ecosystem.

## Toolchain implications

- **GNAT arm-elf** via Alire.
- **Ada Drivers Library** for HAL primitives on both targets.
- **openocd** or **stlink-tools** for flashing via ST-Link V3.
- **GDB** for debugging via ST-Link SWD.
- **CANtools** or **python-can** for CAN bring-up and message inspection.

## Related

- [ADR-0001: Two-node CAN topology](0001-two-node-can-topology.md)
- [ADR-0002: Skip mechanical points](0002-skip-mechanical-points.md)
- [Power architecture](../../architecture/power.md)
