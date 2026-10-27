import unittest
from pathlib import Path

from traceability import build_matrix


CONCEPT = "| OBJ-01 | Intended use |"
REQUIREMENTS = "| SYS-001 | OBJ-01 | ECU | Shall meet a limit. | VER-001 | Draft |"
VERIFICATION = "| VER-001 | Test | Measure the limit. | Planned | - |"


class TraceabilityTests(unittest.TestCase):
    def test_generates_join_with_separate_states(self):
        report = build_matrix(CONCEPT, REQUIREMENTS, VERIFICATION)
        self.assertIn(
            "| OBJ-01 | SYS-001 | ECU | Draft | VER-001 | Planned | - |", report
        )

    def test_multiple_verifications(self):
        requirements = REQUIREMENTS.replace("VER-001", "VER-001, VER-002")
        verifications = VERIFICATION + "\n" + VERIFICATION.replace("VER-001", "VER-002")
        report = build_matrix(CONCEPT, requirements, verifications)
        self.assertEqual(report.count("| OBJ-01 | SYS-001 |"), 2)

    def test_rejects_duplicate_records(self):
        for concept, requirements, verifications in (
            (CONCEPT + "\n" + CONCEPT, REQUIREMENTS, VERIFICATION),
            (CONCEPT, REQUIREMENTS + "\n" + REQUIREMENTS, VERIFICATION),
            (CONCEPT, REQUIREMENTS, VERIFICATION + "\n" + VERIFICATION),
        ):
            with self.subTest(requirements=requirements, verifications=verifications):
                with self.assertRaisesRegex(ValueError, "Duplicate identifier"):
                    build_matrix(concept, requirements, verifications)

    def test_rejects_broken_links(self):
        for old, new in (("OBJ-01", "OBJ-99"), ("VER-001", "VER-999")):
            with self.subTest(link=old):
                with self.assertRaisesRegex(ValueError, "unknown"):
                    build_matrix(CONCEPT, REQUIREMENTS.replace(old, new), VERIFICATION)

    def test_rejects_missing_or_malformed_records(self):
        for requirements in (
            "",
            REQUIREMENTS.replace("SYS-001", "SYS-1"),
            REQUIREMENTS.replace("| ECU |", "| |"),
        ):
            with self.subTest(requirements=requirements):
                with self.assertRaises(ValueError):
                    build_matrix(CONCEPT, requirements, VERIFICATION)

    def test_rejects_invalid_states_and_duplicate_links(self):
        for requirements, verifications in (
            (REQUIREMENTS.replace("Draft", "Approved"), VERIFICATION),
            (REQUIREMENTS, VERIFICATION.replace("Planned", "Done")),
            (REQUIREMENTS.replace("VER-001", "VER-001, VER-001"), VERIFICATION),
        ):
            with self.subTest(requirements=requirements, verifications=verifications):
                with self.assertRaises(ValueError):
                    build_matrix(CONCEPT, requirements, verifications)

    def test_results_require_evidence(self):
        for state in ("Pass", "Fail"):
            with self.subTest(state=state):
                with self.assertRaisesRegex(ValueError, "requires evidence"):
                    build_matrix(
                        CONCEPT, REQUIREMENTS, VERIFICATION.replace("Planned", state)
                    )

    def test_open_requirement_cannot_pass(self):
        with self.assertRaisesRegex(ValueError, "open acceptance criteria"):
            build_matrix(
                CONCEPT,
                REQUIREMENTS.replace("Draft", "Open"),
                VERIFICATION.replace("Planned | -", "Pass | [result](result.md)"),
            )

    def test_evidenced_result_is_retained(self):
        report = build_matrix(
            CONCEPT,
            REQUIREMENTS.replace("Draft", "Baselined"),
            VERIFICATION.replace("Planned | -", "Pass | [result](result.md)"),
        )
        self.assertIn("| Baselined | VER-001 | Pass | [result](result.md) |", report)

    def test_repository_registers_generate(self):
        project = Path(__file__).resolve().parents[1] / "docs" / "project"
        report = build_matrix(
            (project / "system-concept.md").read_text(encoding="utf-8"),
            (project / "requirements.md").read_text(encoding="utf-8"),
            (project / "verification-plan.md").read_text(encoding="utf-8"),
        )
        self.assertIn("| SYS-001 |", report)
        self.assertIn("| SW-012 |", report)
        self.assertIn("| SW-016 |", report)
        self.assertTrue(report.startswith("# Requirements traceability matrix\n"))


if __name__ == "__main__":
    unittest.main()
