# System and allocated software requirements specification

Initial draft; not yet a reviewed baseline or a claim of completeness.
`SYS` requirements describe system behaviour; `SW` requirements allocate
behaviour to software without creating a separate document. All rows use
the same traceability scheme from the [engineering framework](engineering.md).

Parents are objectives in the [system concept](system-concept.md). Each
statement includes its acceptance criterion or an explicit unresolved
parameter. Verification IDs refer to the [V&V plan](verification-plan.md).
`Open` rows cannot be baselined until their parameters are resolved.

## Requirements register

| ID | Parent | Allocation | Requirement / acceptance criterion | Verification | Maturity |
|---|---|---|---|---|---|
| SYS-001 | OBJ-01 | Mechanical | The vehicle shall retain the M151-derived two-stroke, piston-port induction, unmodified Eurocilindro cylinder port geometry and NOS five-speed gearbox. | VER-001 | Draft |
| SYS-002 | OBJ-01 | Vehicle packaging | Installed electronics, instrumentation and service wiring shall preserve the recognisable K181 appearance against the photographs and packaging checklist defined by PAR-01. | VER-001 | Open |
| SYS-003 | OBJ-02 | Engine / ECU | First running characterisation shall use a carburettor and ECU-controlled fixed ignition advance, without mechanical points, RPM mapping or load compensation. | VER-002 | Draft |
| SYS-004 | OBJ-03 | ECU / PDM | On a riding-mode boot with a valid application and calibration and a stable input between 8 V and 16 V, the ECU shall become ready to schedule ignition within 100 ms of stable power application; this measures readiness, not time to the first physical spark. | VER-003 | Draft |
| SYS-005 | OBJ-03 | Power / engine | The system shall support kick-starting with the main battery flat or BMS-isolated under the kick profile, temperature, attempt count and fuel configuration defined by PAR-02. | VER-004 | Open |
| SYS-006 | OBJ-02 | Ignition chain | The ignition chain shall acquire and maintain 36-1 synchronisation over 200-8000 RPM and deliver commanded advance within the timing-error definition and dwell limits resolved by PAR-03. | VER-005 | Open |
| SYS-007 | OBJ-04 | Lamps / PDM | The vehicle shall use incandescent exterior lamps in the stock housings and shall not shed legally required exterior lighting as a low-battery load-reduction action. | VER-006 | Draft |
| SYS-008 | OBJ-04 | Power | The charging system shall support the operating loads, charge reserve and voltage limits in the measured power envelope defined by PAR-04, including injection loads before injection adoption. | VER-004 | Open |
| SYS-009 | OBJ-03 | Enclosures / harness | The installed system shall tolerate the rain, vibration, temperature and storage exposures and retain the functions defined by PAR-05. | VER-007 | Open |
| SYS-010 | OBJ-04 | ECU / three instruments | The vehicle shall have exactly four intelligent CAN nodes: ECU, speedometer/odometer, tachometer and warning cluster. Each instrument controller shall be inside its respective stock-style enclosure; no central handlebar controller shall be used. The PDM shall contain no MCU or CAN node. | VER-001 | Draft |
| SYS-011 | OBJ-04 | CAN physical layer | Vehicle CAN shall use classic CAN at 500000 bit/s with 11-bit identifiers and a nominal 120 ohm termination at each end. | VER-008 | Draft |
| SYS-012 | OBJ-03 | Engine controls | The rider shall be able to stop engine actuation under the CAN, reset and input faults, response limits and independence policy defined by PAR-06. | VER-009 | Open |
| SYS-013 | OBJ-05 | Experiment process | Each characterised subsystem change shall preserve its baseline dataset, hardware/software/calibration identities, session conditions and comparison results under the measurement plan. | VER-010 | Draft |
| SYS-014 | OBJ-06 | Fuel system | Before injected engine operation, the fuel system shall meet the pressure, leakage, injector operating range, material compatibility and lubrication acceptance limits defined by PAR-07. | VER-011 | Open |
| SW-001 | OBJ-03 | ECU riding app | Reset, service mode and invalid crank synchronisation shall inhibit coil charging; detection, cancellation and re-arm timing shall meet PAR-08, including a dwell already in progress. | VER-009 | Open |
| SW-002 | OBJ-03 | ECU riding app | An unreadable or corrupt ignition calibration shall select the validated compiled fixed-timing fallback and report the fault; an injected configuration shall continue only with a separately validated applicable fuel fallback, otherwise inhibit fuel. | VER-012 | Draft |
| SW-003 | OBJ-03 | ECU riding app | Loss of an instrument's communication shall not by itself stop engine control; stale warning-cluster throttle and switch inputs shall use the fallback and age limits defined by PAR-09 rather than being treated as fresh data. | VER-013 | Open |
| SW-004 | OBJ-04 | All instrument apps | After three consecutive missing 1 Hz ECU heartbeats, each gauge shall retain its last-known needle position and indicate stale data through its own illumination, while the warning cluster shall independently illuminate a timeout warning; recovery and local indication criteria shall meet PAR-09. | VER-013 | Open |
| SW-005 | OBJ-04 | Both CAN stacks | Transmitted messages shall conform to the reviewed CAN YAML version's identifiers, producers, bit encodings, scales and periods; reception shall enforce the invalid-data rules defined by PAR-09. | VER-008 | Open |
| SW-006 | OBJ-05 | ECU logging | Session records shall retain timestamps, configuration identity and the required measurement channels; loss/overflow shall be observable under the buffering and retention limits in PAR-10. | VER-010 | Open |
| SW-007 | OBJ-07 | Boot / service | The ECU shall reject a corrupt selected riding image, attempt the valid alternate slot and enter service recovery if neither is valid, without enabling engine outputs in recovery. | VER-014 | Draft |
| SW-008 | OBJ-07 | Both service paths | Software/calibration update shall recover after power interruption at every write/commit boundary according to the recoverable states and flash layout defined by PAR-11. | VER-014 | Open |
| SW-009 | OBJ-02 | ECU scheduler | Crank acquisition, ignition scheduling and enabled injection scheduling shall meet the worst-case deadlines and jitter in PAR-12 while CAN, logging, sensor acquisition and permitted analysis execute concurrently. | VER-015 | Open |
| SW-010 | OBJ-04 | ECU / warning-cluster apps | Exterior indicator blink phase shall be generated by the ECU from steady rider intent; dashboard repeaters shall be timed locally by the warning cluster, within the frequency and duty limits in PAR-13. | VER-006 | Open |
| SW-011 | OBJ-06 | ECU fuel control | In an injected configuration, engine stop, invalid crank synchronisation, reset and service mode shall cancel injector drive and control pump shutdown within PAR-08; any priming exception shall be explicitly bounded by PAR-07. | VER-009, VER-011 | Open |
| SW-012 | OBJ-06 | ECU fuel control | Injected operation shall use a versioned fuel calibration and validated sensor inputs for load, temperature and supply compensation; starting, warm-up, transient behaviour and injector dead-time accuracy shall meet PAR-07. | VER-011, VER-012 | Open |
| SW-013 | OBJ-04 | All instrument apps | The speedometer shall own speed display, local illumination and persistent odometer; the tachometer shall own RPM display and local illumination; the warning cluster shall own warning LEDs and remaining dashboard/handlebar functions, including switchgear, twistgrip TPS, GPS, ambient-light sensing and shared brightness command. | VER-016 | Draft |
| SW-014 | OBJ-03 | All four CAN stacks | Each instrument shall have an independent heartbeat, fault-event identity and diagnostic/update endpoint; an isolated reset, service/update or software loss of one instrument shall not stop the ECU or another instrument's normal functions, except for explicitly handled missing inputs. | VER-013, VER-014 | Draft |
| SW-015 | OBJ-04 | Speedometer app | Odometer reconciliation and persistence shall preserve travelled distance across ECU restart, counter wrap, instrument update and power interruption within the loss/error limits in PAR-10/11. | VER-016 | Open |
| SW-016 | OBJ-04 | Gauge apps / warning cluster | Each gauge shall apply shared brightness requests using local calibration and shall retain usable local illumination after loss or invalidity of the warning-cluster command, within the limits defined by PAR-09. | VER-013, VER-016 | Open |

## Source rationale

- SYS-001/002/007/009 preserve the [constraints](constraints.md), not a new
  claim of legal approval. Road-use applicability still requires review.
- SYS-003/013 and injection requirements derive from the [staged plan](staged-plan.md)
  and [ADR-0010](decisions/0010-throttle-body-fuel-injection.md).
- SYS-004/005 preserve [ADR-0004](decisions/0004-kick-start-flat-battery.md).
  Its illustrative supercap component values are not a validated design.
- SYS-006 uses the [HIL objectives](../architecture/hil.md) as draft targets.
  The stated 0.7-degree timing figure mixes an end-to-end limit with a
  statistical uncertainty target; PAR-03 must resolve that distinction.
- SYS-008 uses the [power architecture](../architecture/power.md); its
  estimated loads and protection values require measurement.
- SYS-010/011 and SW-003/004/005/010/013/014/015/016 derive from
  [ADR-0012](decisions/0012-distributed-dashboard-can-nodes.md), the accepted
  lamp-control ADRs and the [CAN specification](../architecture/can-bus.md).
- SYS-012 and output-inhibition requirements make [hazard](hazards.md)
  mitigations explicit; they are incomplete until timing and fault coverage
  are defined.
- Other software requirements allocate responsibilities from the
  [firmware architecture](../architecture/firmware.md). They do not endorse
  its provisional MCU, memory layout or peripheral assignments.

## Open acceptance parameters

These are unresolved engineering decisions, not default values. Affected
verification remains blocked until closure. Backlog IDs identify closure work.

| ID | Definition needed | Closure task |
|---|---|---|
| PAR-01 | Appearance reference photos and packaging/visibility checklist. | TASK-01 |
| PAR-02 | Measured kick energy/profile, flat versus isolated battery conditions, temperature, maximum attempts and injection pressure readiness. | TASK-04 |
| PAR-03 | Timing error statistic versus maximum bound, reference uncertainty, operating voltage/acceleration range and dwell error limits. | TASK-05 |
| PAR-04 | RPM/load envelope, regulator/battery limits, charging reserve, brownout and transient acceptance. | TASK-04 |
| PAR-05 | Environmental exposures, durations, installation conditions and post-test acceptance. | TASK-01 |
| PAR-06 | Stop-command path, availability during communication failure, required faults and maximum stop latency. | TASK-02 |
| PAR-07 | Injection fuel/mechanical envelope, sensor and calibration accuracy, priming, temperature, lubrication and functional acceptance. | TASK-10 |
| PAR-08 | Loss-of-sync/stall detection, maximum dwell, actuator shutdown deadlines, safe defaults and re-arm guards. | TASK-02 |
| PAR-09 | Signal freshness/plausibility, stale-input fallbacks, per-node heartbeat recovery, local gauge stale indication, shared brightness limits/fallback and message timing tolerances. | TASK-03 |
| PAR-10 | Required channels/rates, storage throughput, overflow indication, timestamp accuracy, retention policy and odometer reconciliation/error/loss limits. | TASK-06 |
| PAR-11 | Per-node sector-aligned flash partitions, update atomicity, target-role/calibration compatibility, odometer retention and recoverable update states. | TASK-06 |
| PAR-12 | Maximum RPM, capture range, deadlines/jitter, worst-case analysis workload and watchdog supervision criteria. | TASK-05 |
| PAR-13 | Exterior/repeater blink frequency tolerance, duty cycle and switch response limits. | TASK-03 |
