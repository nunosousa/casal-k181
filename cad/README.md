# CAD models

This directory contains CAD models that support the Casal K181 restoration and
experimental ECU project, including frame references and packaging for
mechanical and electrical components.

## Contents

| Directory | Purpose |
| --- | --- |
| [`frame-reference/`](frame-reference/) | Reference geometry for the frame and suspension |
| `air-filter-box/` | Air-filter-box design and fit |
| `ecu-mount/` | ECU placement and mounting |
| `intake/` | Carburettor or throttle-body air-path design |

Add or rename directories as the models evolve. Keep related parts together
with their assembly or reference geometry.

## File conventions

- Keep the editable FreeCAD document (`.FCStd`) as the source of truth.
- Add neutral exports such as STEP (`.step` or `.stp`) when they are useful for
  checking fit or sharing a model. Regenerate exports from the source document.
- Use millimetres for dimensions unless a model explicitly documents another
  unit.
- Give files and bodies descriptive names. Include a revision in the filename
  only when multiple revisions need to be retained; otherwise use version
  history.
- Avoid committing temporary files, autosaves, and duplicate exports.

## Measurement and fit notes

For frame and component reference models, record enough information to judge
how reliable the geometry is:

- Measurement source and date
- Measurement method and any known uncertainty
- Datums, origin, and orientation
- Dimensions that are measured versus estimated
- Fit-critical clearances or tolerances, when known

Do not treat reference geometry as manufacturing-ready unless its dimensions
and tolerances have been verified.

## Model index

| Model | File | Purpose / status | Notes |
| --- | --- | --- | --- |
| Frame reference | [`frame-reference/frame.FCStd`](frame-reference/frame.FCStd) | Reference | Add measurement source, datums, and limitations |
| Front suspension bushing | [`frame-reference/front-suspension-bushing.FCStd`](frame-reference/front-suspension-bushing.FCStd) | Reference | Add measurement source and fit notes |

Add an entry when introducing a model that is not self-explanatory from its
directory and filename.
