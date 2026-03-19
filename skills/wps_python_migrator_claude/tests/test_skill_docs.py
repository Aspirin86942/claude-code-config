from __future__ import annotations

import unittest
from pathlib import Path as RepoPath

import yaml

ROOT = RepoPath(__file__).resolve().parents[1]


def read_text(*parts: str) -> str:
    return (ROOT.joinpath(*parts)).read_text(encoding="utf-8")


def load_yaml(*parts: str) -> dict:
    return yaml.safe_load(read_text(*parts))


class SkillDocsTest(unittest.TestCase):
    def setUp(self) -> None:
        self.manifest = load_yaml("references", "official_capabilities.yml")
        self.readme_text = read_text("README.md")
        self.skill_text = read_text("SKILL.md")
        self.compatibility_text = read_text("references", "wps-compatibility.md")
        self.checklist_text = read_text("references", "transformation-checklist.md")

    def test_manifest_structure_and_verification_levels(self) -> None:
        self.assertEqual(
            self.manifest["verification_levels"],
            [
                "dedicated_api_doc_verified",
                "summary_example_verified",
                "unverified_or_snapshot_only",
            ],
        )
        self.assertEqual(
            self.manifest["cross_document"]["summary_example_verified"],
            ["Workbooks.Open(fileID, type)"],
        )
        self.assertIn(
            "dbt() stores record ids in DataFrame.index for update_dbt() workflows",
            self.manifest["data_table"]["verified_behaviors"],
        )
        self.assertIn(
            "xl(sheet_name=None) returns dict[str, DataFrame]",
            self.manifest["worksheet"]["verified_behaviors"],
        )
        self.assertIn(
            "start_row", self.manifest["worksheet"]["verified_parameters"]["xl"]
        )
        self.assertIn(
            "xl_shift_to_left",
            self.manifest["worksheet"]["verified_parameters"]["delete_xl"],
        )
        self.assertEqual(
            self.manifest["official_supported_libraries_reference"],
            self.manifest["official_docs"]["third_party_libraries"],
        )

    def test_last_verified_date_lives_only_in_manifest(self) -> None:
        verified_date = self.manifest["last_verified_against_official_docs"]

        self.assertIn(verified_date, read_text("references", "official_capabilities.yml"))
        self.assertNotIn(verified_date, self.readme_text)
        self.assertNotIn(verified_date, self.skill_text)
        self.assertNotIn(verified_date, self.compatibility_text)
        self.assertNotIn(verified_date, self.checklist_text)

    def test_readme_uses_manifest_as_source_of_truth(self) -> None:
        self.assertIn("Single source of truth", self.readme_text)
        self.assertIn("references/official_capabilities.yml", self.readme_text)
        self.assertIn("summary_example_verified", self.readme_text)
        self.assertIn("unverified_or_snapshot_only", self.readme_text)
        self.assertIn("Workbooks.Open(fileID, type)", self.readme_text)
        self.assertIn("dbt(..., condition=...)", self.readme_text)
        self.assertIn("Prefer worksheet outputs by default.", self.readme_text)

    def test_skill_separates_official_and_experience_rules(self) -> None:
        self.assertIn("single", self.skill_text)
        self.assertIn("machine-readable capability manifest", self.skill_text)
        self.assertIn("last_verified_against_official_docs", self.skill_text)
        self.assertIn("summary_example_verified", self.skill_text)
        self.assertIn("unverified_or_snapshot_only", self.skill_text)
        self.assertIn("Experience-based notes", self.skill_text)
        self.assertIn("repository experience rules", self.skill_text)
        self.assertIn("assert_wps_runtime()", self.skill_text)
        self.assertIn("write_sheet_df()", self.skill_text)
        self.assertIn("`config` worksheet", self.skill_text)
        self.assertIn("`run_id`", self.skill_text)
        self.assertIn("`run_summary`", self.skill_text)
        self.assertIn("`retryable`", self.skill_text)
        self.assertIn("_cache_*", self.skill_text)

    def test_compatibility_guide_tracks_manifest_levels(self) -> None:
        self.assertIn("## dedicated_api_doc_verified", self.compatibility_text)
        self.assertIn("## summary_example_verified", self.compatibility_text)
        self.assertIn("## experience_based", self.compatibility_text)
        self.assertIn("## unverified_or_snapshot_only", self.compatibility_text)

        for api_name in self.manifest["worksheet"]["verified_apis"]:
            self.assertIn(f"`{api_name}()`", self.compatibility_text)
        for library_name in self.manifest["preferred_verified_subset"]:
            self.assertIn(f"`{library_name}`", self.compatibility_text)
        for item in self.manifest["data_table"]["unverified_or_snapshot_only"]:
            self.assertIn(item, self.compatibility_text)
        self.assertIn("Workbooks.Open(fileID, type)", self.compatibility_text)
        self.assertIn("Application.Worksheets.Item(...)", self.compatibility_text)
        self.assertIn("HTTPAdapter", self.compatibility_text)
        self.assertIn("Retry", self.compatibility_text)

    def test_checklist_focuses_on_actions_not_capability_sections(self) -> None:
        self.assertNotIn("## officially_documented", self.checklist_text)
        self.assertNotIn("## dedicated_api_doc_verified", self.checklist_text)
        self.assertIn("read_sheet_df()", self.checklist_text)
        self.assertIn("write_sheet_df()", self.checklist_text)
        self.assertIn("`config` sheet", self.checklist_text)
        self.assertIn("`run_summary`", self.checklist_text)
        self.assertIn("`delete_xl()`", self.checklist_text)
        self.assertIn("Workbooks.Open(...)", self.checklist_text)
        self.assertIn("json.load(...)", self.checklist_text)
        self.assertIn("requests.Session", self.checklist_text)

    def test_environment_baseline_declares_pytest_and_pyyaml(self) -> None:
        environment = load_yaml("environment.yml")

        self.assertEqual(environment["name"], "test")
        self.assertIn("pytest", environment["dependencies"])
        self.assertIn("pyyaml", environment["dependencies"])


if __name__ == "__main__":
    unittest.main()
