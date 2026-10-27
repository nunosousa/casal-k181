# Implementation plan and task backlog

The [staged plan](staged-plan.md) owns milestone order. This backlog owns
bounded closure tasks; it is not evidence of completion. Dependencies are
explicit, and optional research does not block the earlier baseline.

All tasks below are initially open. Update status and evidence links as work
is completed; a requirement is not verified by closing an implementation task.

| ID | Work and definition of done | Dependencies | Requirement / experiment links | Status |
|---|---|---|---|---|
| TASK-01 | Review concept/scope and initial requirement allocation; define appearance and environmental criteria (PAR-01/05); record the reviewed baseline and remaining gaps. | None | SYS-001/002/009/010 | Open |
| TASK-02 | Review hazard controls, modes, stop path and fault classification; define PAR-06/08 including active-pulse cancellation and re-arm; update SAD/ICD and VER-009 assertions. | None | SYS-012; SW-001/002/011; HAZ-01/02/03/05 | Open |
| TASK-03 | Complete four-node harness/termination and per-instrument connector contracts; review YAML-v2 diagnostic/update routing and receive timestamps; define freshness/invalid-data, local gauge stale indication, brightness fallback and blink contracts (PAR-09/13), then review interface baseline. | TASK-02 | SYS-010/011; SW-003/004/005/010/013/014/016; IF-01 through IF-08 | Open |
| TASK-04 | Measure selected stator/kick energy and loads; validate energy-storage ratings, battery isolation and protection; close PAR-02/04 for the carburetted build, reserving explicit injection revalidation. | TASK-02 | SYS-004/005/007/008; IF-01/02/05 | Open |
| TASK-05 | Confirm full-roadmap ECU MCU and each instrument MCU candidate, package/enclosure fit, Ada runtime and pins/timers/ADC/DMA; define timing statistic, operating envelope, WCET/jitter and watchdog criteria (PAR-03/12); update proposed ADR-0003 and SAD for review. | TASK-02, TASK-03 | SYS-006/010; SW-009/013; IF-03/09 | Open |
| TASK-06 | Define per-node sector-aligned image/calibration layout, target-checked update recovery, speedometer odometer reconciliation/persistence and log contracts (PAR-10/11); demonstrate boot/runtime/toolchain and storage primitives; update SAD and procedures. | TASK-05 | SW-006/007/008/014/015; IF-07/08/09 | Open |
| TASK-07 | Build and execute phase-2 ECU/PDM and three-instrument HIL checks, including independent reset/update/failure and shared-bus faults; link results and close applicable baseline safety/timing/power assertions before first engine start. | TASK-01, TASK-03, TASK-04, TASK-06 | SYS-004/006/011/012; SW-001 through SW-016 as applicable | Open |
| TASK-08 | Complete mechanical first-start checklist, phase-3 fixed-timing baseline and phase-4/5/6 comparisons; retain accepted sessions and calibration identities under the measurement plan. | TASK-07 | SYS-001/003/007/009/013; OBJ-02/05 | Open |
| TASK-09 | Define crank-dynamics usefulness criteria/reference data and bounded adaptive-control evaluation; execute phase 7, and phase 8 only if justified; record negative results too. | TASK-08 | EXP-01/02; SW-009 | Open |
| TASK-10 | Define injection feasibility and PAR-07; allocate fuel hardware/interfaces, update shutdown/calibration/log contracts, revalidate power/kick-start, execute bench then engine checks and phase-9 comparison. Retain carburettor if adoption is unjustified. | TASK-08 | EXP-03; SYS-005/008/014; SW-002/009/011/012; IF-10 | Open |

TASK-10 does not depend on TASK-09: successful crank-dynamics estimation or
adaptive ignition is not a prerequisite for injection. TASK-05 reviews the
recent H743-class recommendation; no MCU change is accepted by this backlog.

## Working rule

Select ready work by dependencies, not row order. For each implementation
change identify requirements and interfaces affected, update the relevant
hazard/ADR when necessary, and run the smallest adequate verification.
Keep experiment plans distinct from requirements closure.
