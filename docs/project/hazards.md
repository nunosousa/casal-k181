# Preliminary hazard register

Qualitative starting point, not a completed safety assessment or an
automotive/avionics assurance claim. No residual risk is accepted by this
document. Review likelihood, severity and mitigation effectiveness before
the relevant test gate; do not infer safety from a planned test.

| ID | Hazardous outcome / initiating conditions | Proposed controls and requirement links | Evidence / closure |
|---|---|---|---|
| HAZ-01 | Unexpected engine actuation during boot, service, reset or loss of synchronisation. | Safe hardware defaults, bounded dwell and cancellation of scheduled outputs; SW-001, SW-011, SYS-012. | VER-009; TASK-02. Open: shutdown limits and stuck-driver coverage. |
| HAZ-02 | Fuel release, fire or uncontrolled fuel delivery after stall, electrical fault or plumbing failure. | Rated compatible fuel components, pressure/leak tests, bounded priming, shutdown and defined power isolation; SYS-014, SW-011. | VER-009/011; TASK-10. Open: limits and independent hardware protection. |
| HAZ-03 | Engine damage or sudden loss of propulsion from unsafe advance, lean fuelling or lost lubrication. | Validated calibration, input plausibility, applicable fallback, controlled thermal tests and preserved lubrication; SW-002/012, SYS-014. | VER-011/012; TASK-02/10. Open: operating/thermal limits and fault classification. |
| HAZ-04 | Loss of required lighting, thermal damage or power collapse from overload, short or incorrect charging/storage design. | Measured power envelope, fuse coordination, rated energy storage, no shedding of required exterior lights; SYS-007/008/009. | VER-004/006/007; TASK-04. Open: hardware ratings and protection response. |
| HAZ-05 | Rider cannot stop the engine, or receives misleading information, after CAN, instrument or warning-cluster failure. | Explicit stop-path policy, signal-age handling, local stale-gauge indication, cluster peer warnings and brightness fallback; SYS-012, SW-003/004/005/014/016. | VER-009/013/016; TASK-02/03. Open: communication-independent stop provision, shared-bus/power propagation and recovery. |
| HAZ-06 | Timing corruption or control failure due to logging contention, missed deadlines or corrupted update/configuration. | Hardware timing, bounded priorities, watchdog policy, image/configuration validation and power-cut recovery; SW-002/006/007/008/009. | VER-010/012/014/015; TASK-05/06. Open: deadlines, partitioning and watchdog coverage. |
| HAZ-07 | Injury during bench, rotating-rig or riding experiments. | Guarded rotating parts, suitable coil loads, fuel/energy isolation, controlled engine checks and suitable authorised test site; SYS-013/014. | VER-005/010/011 and test-specific setup review; TASK-07/08/10. Open: setup-specific controls before energising. |

For each test session record applicable hazards, controls, remaining
limitations and a proceed/stop decision. A fallback is not automatically
safer than shutdown, nor is shutdown automatically safe in every riding
scenario. Resolve that trade-off for each fault class.

The [V&V plan](verification-plan.md) gates escalation from non-running bench
checks to engine and riding tests. The [backlog](backlog.md) owns closure work.
