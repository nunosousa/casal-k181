# Engineering documentation framework

Use avionics-style reasoning and traceability with hobby-scale evidence,
not a certification lifecycle. This framework organises the existing
design; it does not assert that the vehicle is safe, compliant or verified.

## Document map

| Concern | Authoritative location |
|---|---|
| Operational concept, objectives and modes | [System concept](system-concept.md) |
| System and allocated software requirements | [Requirements specification](requirements.md) |
| Architectural boundaries and constraints | [Constraints](constraints.md) and accepted [ADRs](decisions/) |
| System architecture | [System architecture](../architecture/system.md) |
| Distributed instrument controllers | [Dashboard architecture](../architecture/dashboard.md) |
| Software architecture description (SAD) | [Firmware architecture](../architecture/firmware.md) |
| Electrical, mechanical and logical interfaces (ICD) | [Interface control](../architecture/interfaces.md) |
| Protocol specification (PS) | [CAN specification](../architecture/can-bus.md) and [message definitions](../../protocol/messages.yaml) |
| Verification and validation plan | [V&V plan](verification-plan.md) |
| Requirement-to-verification traceability | [Traceability](traceability.md), generated from the requirements and V&V records |
| Hazard analysis | [Hazard register](hazards.md) |
| Milestones and executable work | [Staged plan](staged-plan.md) and [backlog](backlog.md) |
| Experimental methodology | [Measurement plan](../measurement-plan.md) |

## Authority and change control

- The concept explains intended use; requirements state what must hold;
  architecture describes how; ADRs record why consequential choices were
  made. Experiments test hypotheses rather than promise improvements.
- Requirements are normative only after review and a recorded baseline.
  The initial set is a draft extraction, not an exhaustive specification.
  Accepted ADRs remain decisions; proposed ADRs are not commitments.
- The ICD owns cross-subsystem contracts. The CAN YAML owns wire encodings;
  the CAN document owns transport behaviour and subsystem documents own
  application semantics. Conflicts are blockers to resolve, not permission
  to choose whichever source is convenient.
- Keep requirement IDs stable; retire IDs rather than reuse them. Changes
  to baselined behaviour update affected interfaces, architecture, hazards,
  tests and backlog in the same change. Record consequential changes in an
  ADR. A Git commit identifies each reviewed baseline.
- Before hardware release, review the applicable requirements and interfaces
  and record the baseline commit and unresolved items in the build record.
  Before engine or riding tests, apply the V&V gates. No sign-off bureaucracy
  is required, but a dated review and evidence links are.

## Minimum useful records

Requirements contain an ID, parent objective, allocation, acceptance
statement, verification IDs and maturity. Source rationale is recorded in
the specification. Software requirements share the same register initially;
split them only when their size warrants a separate SRS.

Verification records identify procedures and evidence status. Result
records identify the requirement baseline, firmware/calibration/hardware,
setup and instrument calibration, stimulus, measured limits, outcome and
anomalies. Trace to tests and evidence, not every implementation function.

Use `Open` for a requirement with unresolved acceptance criteria, `Draft`
for a reviewable statement and `Baselined` only after a recorded review.
None of these means verified. `Planned`, `Blocked`, `Pass` and `Fail` are
separate verification states; a planned test is not evidence.

Do not silently assign numerical limits to unresolved safety behaviour.
Track them as parameters with a closure task and gate. Start with bench
evidence, then controlled engine tests, then riding tests where appropriate.
