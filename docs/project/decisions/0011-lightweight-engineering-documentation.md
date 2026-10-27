# ADR-0011: Adopt lightweight requirements and verification documentation

**Status:** Accepted
**Date:** 2026-10-27

## Context

The growing engine-control roadmap needs explicit requirements, interface
contracts and verification evidence. Existing architecture, HIL and
measurement documents provide substantial design detail but mix commitments,
proposals and experiments. The project remains a hobby restoration, not a
certification programme.

## Decision

Adopt the [engineering framework](../engineering.md): an operational concept,
one identified system/software requirement register, an ICD, the existing
SAD and CAN protocol specification, V&V plan, generated traceability,
preliminary hazard register, ADRs and dependency-linked backlog.

Evolve existing documents rather than rewrite them. Separate experimental
hypotheses from committed behaviour. Mark unresolved acceptance criteria and
interface conflicts as blockers to the applicable release/test gate.
Baseline requirements through a recorded review; do not claim approval or
verification merely because a document or test ID exists.

## Consequences

- Consequential changes are assessed across requirements, architecture,
  interfaces, hazards and tests; evidence remains tied to configuration.
- Initial requirements remain draft/open until reviewed. Legacy interface
  contradictions must be closed before affected hardware release.
- No certification coverage target, assurance level, formal independence,
  function-by-function trace or heavyweight change board is introduced.
- System and software requirements share a document until size justifies
  separation. The trace matrix is generated, not independently maintained.
