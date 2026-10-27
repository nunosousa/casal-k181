# Verification and validation plan

Initial plan; no verification evidence exists in this register yet.
Requirements, hazards and procedures must be reviewed before execution.
Use the [HIL architecture](../architecture/hil.md) for bench design and
the [measurement plan](../measurement-plan.md) for experimental methodology.
Their existing test names are procedure candidates, not executed results.

## Verification versus validation

Verification demonstrates an identified requirement against a defined
criterion by inspection, analysis, test or demonstration. Validation asks
whether the resulting vehicle meets its intended Sunday-riding and
experimental use. An experiment that finds no performance benefit can
still satisfy its data-preservation and safety requirements.

`Planned` means not executed; `Blocked` means acceptance/setup decisions
are unresolved. `Pass` requires linked evidence meeting every applicable
criterion for the stated configuration; `Fail` requires recorded evidence
and follow-up. Neither a test ID nor traceability coverage proves compliance.

## Verification register

Requirements reference these IDs. One procedure can cover several
requirements, but its result must distinguish each assertion. Split records
if configurations or outcomes differ; a shared aggregate Pass must not hide
an open assertion. No Pass is permitted while a covered parameter is open.

| ID | Method | Procedure / acceptance basis | State | Evidence |
|---|---|---|---|---|
| VER-001 | Inspection | Build/packaging review: check committed mechanical configuration, exactly four CAN controllers with one inside each of the three instrument enclosures, no central handlebar controller, passive PDM and PAR-01 appearance checklist; record photographs and hardware identities. | Blocked | - |
| VER-002 | Inspection + demonstration | First-start configuration review and controlled run: carburettor installed, points absent, fixed advance selected and no RPM/load map enabled. | Planned | - |
| VER-003 | Test | Scope stable-power application to an observable ignition-ready marker across 8-16 V on supported riding-mode cold-boot paths with valid images/calibration; every measured readiness interval <=100 ms. Establish rail stability and marker definitions before execution. Service and invalid-image behaviour are checked separately. | Planned | - |
| VER-004 | Analysis + test | Characterise stator/DC power versus RPM and load; replay measured kick profiles with flat and isolated battery, then demonstrate starting. Close PAR-02/04 and repeat with injection loads before adoption. | Blocked | - |
| VER-005 | Test | HIL sweep 200-8000 RPM, missing-tooth acquisition, speed ramps, voltage and dwell checks against independent optical/scope reference; resolve PAR-03 and its uncertainty model first. | Blocked | - |
| VER-006 | Inspection + test | Inspect incandescent lamp installation; exercise low-battery shedding, rider intent and independent exterior/repeater blink generation against PAR-13. | Blocked | - |
| VER-007 | Inspection + test | Installation and environmental exposure checks against PAR-05, with before/after functional results and explicit exclusions. | Blocked | - |
| VER-008 | Analysis + test | Check four-node physical CAN, exactly two end terminations and all YAML-v2 messages/owners against recorded frames; test unique node IDs, diagnostic/ISO-TP routing, load, invalid values, freshness and timing tolerances after PAR-09/interface closure. | Blocked | - |
| VER-009 | Test | HIL actuator/stop fault matrix: reset, service, missing/implausible crank, in-progress dwell/injection, stalled engine and CAN/input faults. Measure physical output shutdown/re-arm against PAR-06/08, not just software flags. | Blocked | - |
| VER-010 | Inspection + test | Replay worst-case acquisition/log load, verify recorded channels, timestamps and overflow indication against PAR-10; audit paired experiment records against the measurement plan. | Blocked | - |
| VER-011 | Inspection + test | Bench stage: verify plumbing compatibility, pressure/leaks, lubrication provision, injector controllability and prime/shutdown against PAR-07/08 before injected engine tests. Engine stage: progressively verify calibrated starting/warm-up/transient behaviour before riding. Record each stage separately. | Blocked | - |
| VER-012 | Test | Corrupt or remove calibration and fault each control input; verify warning, validated applicable fallback or fuel inhibition. Include supported version mismatch and injected-operation cases after PAR-07 closure. | Blocked | - |
| VER-013 | Test | Drop each node's heartbeat/data independently; observe local stale indication on each gauge, cluster timeout warning, engine/other-instrument continuation, cluster-loss TPS/switch and brightness fallback under PAR-09. Distinguish isolated reset/disconnect from shared bus/rail faults. | Blocked | - |
| VER-014 | Test | Corrupt active/alternate images and interrupt each update write/commit boundary for every node; verify alternate boot or safe service recovery, inhibited recovery outputs, target-role rejection and compatible retained calibration/odometer under PAR-11. Updating one instrument must not reset or update peers. | Blocked | - |
| VER-015 | Analysis + test | Measure worst-case capture/scheduling latency and jitter under concurrent CAN, logging, sensor and enabled analysis/injection load; verify PAR-12 and watchdog fault response. | Blocked | - |
| VER-016 | Inspection + test | Verify function allocation, each local gauge/illumination and cluster-owned switchgear/TPS/GPS/ALS. Exercise odometer ECU reset/counter wrap/power-cut/update cases under PAR-10/11 and shared brightness/cluster-loss fallback under PAR-09. | Blocked | - |

## Gates

1. **Hardware release:** review requirements, hazard controls and ICD;
   resolve applicable parameters and interface conflicts; verify MCU/runtime,
   pins, memory and power budgets. Record the baseline commit.
2. **Bench energisation:** review setup-specific hazards, guards, loads,
   isolation, component ratings and instrument ranges. This precedes HIL,
   not the other way round.
3. **First carburetted engine start (phase 3):** close applicable phase-2
   HIL assertions, particularly readiness, timing, stop/inhibition and power.
   No applicable safety-critical open criterion or failed test may be waived
   merely because no firmware fault has been observed. Record mechanical
   readiness, baseline configuration and unresolved non-blocking limitations.
4. **Riding / characterisation:** complete controlled engine checks, relevant
   lighting/display/fault tests, site/safety and road-use applicability review.
   Meet measurement-plan session acceptance; do not treat documentation as
   legal approval.
5. **Injection engine tests / adoption:** resolve PAR-07 and applicable
   shutdown, calibration and power parameters; pass fuel bench checks before
   injected engine tests. Complete controlled engine checks before riding,
   then compare against the carburettor with unchanged ignition/hardware.
   Revalidate flat-battery starting before claiming it for injection.

Later optional-feature blockers do not prevent an earlier carburetted
baseline once its applicable requirements are closed. Document applicability
explicitly; do not mark a future-feature requirement as passed or silently
exclude a fault case.

## Result record and evidence retention

Store a concise result with the build log or experiment record. Include:

- Verification ID and individual requirements/assertions, date and operator.
- Requirement/protocol baseline commit, hardware revision, firmware build,
  calibration identity and applicable feature configuration.
- Setup, instrument identity/calibration, stimulus and expected limits.
- Measured values, uncertainty, raw-data locations and durable checksums.
- Per-assertion pass/fail, anomalies, exclusions and follow-up task.

Large raw data may remain outside Git as in the existing repository layout,
but its location and checksum must be retained. Do not link ephemeral files
as the only evidence. Update register state/evidence when results are reviewed.

## Validation campaigns

Validate OBJ-01/03/04/07 through packaging review, representative cold/hot
starting, stop/degraded/service scenarios, lighting and intended-use checks
under defined conditions. Define environmental claims before asserting
seasonal reliability.

Validate OBJ-02/05/06 through preserved stage comparisons using the measurement
plan. Define EXP-01/02/03 decision criteria before data collection and record
negative/inconclusive results as valid outcomes. Performance improvements
are not inferred from passing HIL.
