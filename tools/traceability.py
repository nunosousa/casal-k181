"""Generate requirement traceability from the canonical Markdown registers."""

import re
import sys
from pathlib import Path


def read_rows(text, prefixes, pattern, column_count):
    rows = {}
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if not cells[0].startswith(prefixes):
            continue
        identifier = cells[0]
        if not re.fullmatch(pattern, identifier):
            raise ValueError(f"Invalid identifier: {identifier}")
        if len(cells) != column_count or not all(cells):
            raise ValueError(f"{identifier}: expected {column_count} nonempty columns")
        if identifier in rows:
            raise ValueError(f"Duplicate identifier: {identifier}")
        rows[identifier] = cells
    if not rows:
        raise ValueError(f"No records found for {prefixes}")
    return rows


def build_matrix(concept_text, requirements_text, verification_text):
    objectives = read_rows(concept_text, ("OBJ-",), r"OBJ-\d{2}", 2)
    requirements = read_rows(
        requirements_text, ("SYS-", "SW-"), r"(?:SYS|SW)-\d{3}", 6
    )
    verifications = read_rows(verification_text, ("VER-",), r"VER-\d{3}", 5)
    for identifier, _, _, state, evidence in verifications.values():
        if state not in {"Planned", "Blocked", "Pass", "Fail"}:
            raise ValueError(f"{identifier}: invalid verification state {state}")
        if state in {"Pass", "Fail"} and evidence == "-":
            raise ValueError(f"{identifier}: {state} requires evidence")

    report = [
        "# Requirements traceability matrix",
        "",
        "Generated from the concept, requirements and verification registers.",
        "Maturity and verification state are independent; links are not proof.",
        "",
        "| Objective | Requirement | Allocation | Maturity | Verification | State | Evidence |",
        "|---|---|---|---|---|---|---|",
    ]
    for identifier, parent, allocation, _, verification_ids, maturity in requirements.values():
        if parent not in objectives:
            raise ValueError(f"{identifier}: unknown objective {parent}")
        if maturity not in {"Open", "Draft", "Baselined"}:
            raise ValueError(f"{identifier}: invalid maturity {maturity}")
        references = [reference.strip() for reference in verification_ids.split(",")]
        if len(references) != len(set(references)):
            raise ValueError(f"{identifier}: duplicate verification link")
        for reference in references:
            if reference not in verifications:
                raise ValueError(f"{identifier}: unknown verification {reference}")
            _, _, _, state, evidence = verifications[reference]
            if maturity == "Open" and state == "Pass":
                raise ValueError(f"{identifier}: open acceptance criteria cannot pass")
            report.append(
                f"| {parent} | {identifier} | {allocation} | {maturity} | "
                f"{reference} | {state} | {evidence} |"
            )
    return "\n".join(report) + "\n"


def main():
    project = Path(__file__).resolve().parents[1] / "docs" / "project"
    try:
        report = build_matrix(
            (project / "system-concept.md").read_text(encoding="utf-8"),
            (project / "requirements.md").read_text(encoding="utf-8"),
            (project / "verification-plan.md").read_text(encoding="utf-8"),
        )
    except (OSError, ValueError) as error:
        print(f"Traceability error: {error}", file=sys.stderr)
        return 1
    print(report, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
