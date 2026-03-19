from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import textwrap
import unittest
from pathlib import Path as RepoPath

ROOT = RepoPath(__file__).resolve().parents[1]
SCRIPTS_DIR = ROOT / "scripts"
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))

import scan_incompatible_patterns as scanner


class ScanIncompatiblePatternsTest(unittest.TestCase):
    def write_source(self, source: str, file_name: str = "sample.py") -> RepoPath:
        temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(temp_dir.cleanup)
        file_path = RepoPath(temp_dir.name) / file_name
        file_path.write_text(textwrap.dedent(source), encoding="utf-8")
        return file_path

    def test_scan_file_ignores_string_and_comment_matches(self) -> None:
        file_path = self.write_source(
            '''
            """lxml openpyxl Path("fake.xlsx") tz_convert("Asia/Shanghai")"""
            pattern = r"write_xl(df)"
            # open("demo.txt")
            note = "zoneinfo and to_excel are mentioned here only"
            '''
        )

        result = scanner.scan_file(file_path)

        self.assertEqual(result.findings, [])
        self.assertEqual(result.encoding_issues, [])

    def test_scan_file_detects_structured_categories_and_severities(self) -> None:
        file_path = self.write_source(
            """
            import openpyxl
            import requests
            from lxml import etree
            from pathlib import Path

            output = Path("result.xlsx")
            handle = open("result.csv", "w", encoding="utf-8")
            raw = pd.read_csv("cache.csv")
            df.to_excel("result.xlsx")
            series = series.tz_convert("Asia/Shanghai")
            rows = dbt(sheet_name="records")
            write_xl(df, sheet_name="result")
            book = Workbooks.Open("fileID", "et")
            requests.get("https://example.com")
            """
        )

        result = scanner.scan_file(file_path)
        category_summary = scanner.build_summary(result.findings)
        severity_summary = scanner.build_severity_summary(result.findings)

        self.assertEqual(category_summary["local_file_io"], 3)
        self.assertEqual(category_summary["local_input_cache"], 1)
        self.assertEqual(category_summary["openpyxl_local_workbook"], 1)
        self.assertEqual(category_summary["html_parsing_dependency"], 1)
        self.assertEqual(category_summary["timezone_risk"], 1)
        self.assertEqual(category_summary["data_table_api_present"], 1)
        self.assertEqual(category_summary["wps_sheet_io_present"], 1)
        self.assertEqual(category_summary["cross_document_or_object_model"], 1)
        self.assertEqual(category_summary["external_access_or_allowlist"], 2)
        self.assertGreaterEqual(severity_summary["high"], 4)
        self.assertGreaterEqual(severity_summary["info"], 2)

    def test_iter_python_files_skips_ignored_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = RepoPath(temp_dir)
            (root / "__pycache__").mkdir()
            (root / ".venv").mkdir()
            keep_file = root / "keep.py"
            ignored_file = root / "__pycache__" / "ignored.py"
            hidden_env_file = root / ".venv" / "ignored_env.py"
            keep_file.write_text("print('keep')\n", encoding="utf-8")
            ignored_file.write_text("print('ignore')\n", encoding="utf-8")
            hidden_env_file.write_text("print('ignore_env')\n", encoding="utf-8")

            files, ignored_hits = scanner.iter_python_files(root)

        self.assertEqual(files, [keep_file])
        self.assertEqual(len(ignored_hits), 2)
        self.assertTrue(any(hit.directory_path.endswith("__pycache__") for hit in ignored_hits))
        self.assertTrue(any(hit.directory_path.endswith(".venv") for hit in ignored_hits))

    def test_scan_file_records_encoding_issue_without_silent_replace(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = RepoPath(temp_dir) / "bad.py"
            file_path.write_bytes(b"print('\xff')\n")

            result = scanner.scan_file(file_path)

        self.assertEqual(result.findings, [])
        self.assertEqual(len(result.encoding_issues), 1)
        self.assertEqual(result.encoding_issues[0].action, "skipped_non_utf8_file")

    def test_scan_file_can_replace_invalid_utf8_when_explicitly_requested(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            file_path = RepoPath(temp_dir) / "bad.py"
            file_path.write_bytes(b'cache = Path("cache.csv")\nprint("\xff")\n')

            result = scanner.scan_file(file_path, replace_invalid_utf8=True)

        self.assertEqual(len(result.encoding_issues), 1)
        self.assertEqual(
            result.encoding_issues[0].action, "replaced_invalid_utf8_then_scanned"
        )
        self.assertEqual(scanner.build_summary(result.findings)["local_file_io"], 1)

    def test_scan_path_supports_single_file_and_empty_directory(self) -> None:
        file_path = self.write_source("write_xl(df, sheet_name='result')\n", "one.py")
        single_file_report = scanner.scan_path(file_path)

        self.assertEqual(single_file_report.python_file_count, 1)
        self.assertEqual(single_file_report.finding_count, 1)

        with tempfile.TemporaryDirectory() as temp_dir:
            empty_report = scanner.scan_path(RepoPath(temp_dir))

        self.assertEqual(empty_report.python_file_count, 0)
        self.assertEqual(empty_report.finding_count, 0)
        self.assertEqual(empty_report.summary_by_category, {})

    def test_same_line_multi_pattern_only_counts_one_per_category(self) -> None:
        file_path = self.write_source(
            """
            cache = pd.read_csv("a.csv"); backup = pd.read_excel("b.xlsx")
            """
        )

        result = scanner.scan_file(file_path)

        self.assertEqual(scanner.build_summary(result.findings)["local_input_cache"], 1)

    def test_cli_outputs_extended_json_schema(self) -> None:
        file_path = self.write_source("write_xl(df, sheet_name='result')\n", "cli.py")
        completed = subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "scan_incompatible_patterns.py"),
                str(file_path),
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        payload = json.loads(completed.stdout)

        self.assertEqual(payload["rule_version"], scanner.RULE_VERSION)
        self.assertIn("summary_by_severity", payload)
        self.assertIn("encoding_issues", payload)
        self.assertIn("ignored_directory_hits", payload)
        self.assertEqual(payload["summary_by_category"]["wps_sheet_io_present"], 1)


if __name__ == "__main__":
    unittest.main()
