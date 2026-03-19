from __future__ import annotations

import argparse
import io
import json
import os
import re
import tokenize
from dataclasses import asdict, dataclass, field
from pathlib import Path

RULE_VERSION = "2026-03-18-audit-v2"
IGNORED_DIR_NAMES = {
    "__pycache__",
    ".git",
    ".venv",
    "venv",
    "site-packages",
    "build",
    "dist",
    ".mypy_cache",
    ".pytest_cache",
}


@dataclass(frozen=True)
class Rule:
    """Represents one auditable scanning rule."""

    category: str
    severity: str
    pattern: str
    why_it_matters: str
    preferred_wps_replacement: str
    official_basis: str
    compiled_pattern: re.Pattern[str] = field(init=False, repr=False, compare=False)

    def __post_init__(self) -> None:
        object.__setattr__(self, "compiled_pattern", re.compile(self.pattern))


@dataclass
class Finding:
    """Represents one risky or informative code pattern found in a Python project."""

    file_path: str
    line_number: int
    category: str
    severity: str
    pattern: str
    line_text: str
    why_it_matters: str
    preferred_wps_replacement: str
    official_basis: str


@dataclass
class EncodingIssue:
    """Represents one file skipped or downgraded because UTF-8 decoding failed."""

    file_path: str
    error_type: str
    message: str
    action: str


@dataclass
class IgnoredDirectoryHit:
    """Represents one ignored directory encountered during repository walk."""

    directory_path: str
    reason: str


@dataclass
class ScanFileResult:
    """Represents the result of scanning a single file."""

    findings: list[Finding]
    encoding_issues: list[EncodingIssue]


@dataclass
class ScanReport:
    """Represents the full repository scan payload."""

    scanned_path: str
    python_file_count: int
    finding_count: int
    summary_by_category: dict[str, int]
    summary_by_severity: dict[str, int]
    encoding_issues: list[EncodingIssue]
    ignored_directory_hits: list[IgnoredDirectoryHit]
    findings: list[Finding]
    rule_version: str


RULES: list[Rule] = [
    Rule(
        category="local_file_io",
        severity="high",
        pattern=r"\bPath\s*\(",
        why_it_matters="Local path construction often signals filesystem coupling that WPS runtime cannot preserve directly.",
        preferred_wps_replacement="Replace local file outputs and caches with worksheet tabs or data-table storage.",
        official_basis="WPS worksheet and data-table APIs are the repository-safe persistence surface.",
    ),
    Rule(
        category="local_file_io",
        severity="high",
        pattern=r"\bopen\s*\(",
        why_it_matters="Direct local file reads or writes do not map cleanly to WPS cloud execution.",
        preferred_wps_replacement="Move file-backed inputs and outputs to worksheet tabs, config sheets, or external services.",
        official_basis="Repository migration guidance treats local filesystem persistence as incompatible by default.",
    ),
    Rule(
        category="local_file_io",
        severity="high",
        pattern=r"\.to_csv\s*\(",
        why_it_matters="CSV output usually represents a local cache or report artifact that should be sheet-native in WPS.",
        preferred_wps_replacement="Write report outputs to `write_xl()` or map record data to data tables when CRUD semantics are required.",
        official_basis="Repository defaults prefer worksheet outputs over local report files.",
    ),
    Rule(
        category="local_file_io",
        severity="high",
        pattern=r"\.to_excel\s*\(",
        why_it_matters="Excel output usually represents a local workbook dependency that WPS should replace with worksheet writes.",
        preferred_wps_replacement="Use `write_xl()` for worksheet-style output instead of local workbook files.",
        official_basis="Dedicated worksheet API pages document `write_xl()` as the primary output surface.",
    ),
    Rule(
        category="local_file_io",
        severity="high",
        pattern=r"\bExcelWriter\s*\(",
        why_it_matters="Workbook writer objects usually anchor local Excel persistence and formatting flows.",
        preferred_wps_replacement="Prefer tabular worksheet outputs and only keep richer workbook behavior if the runtime explicitly supports it.",
        official_basis="Repository migration guidance treats local-only workbook flows as a rewrite trigger.",
    ),
    Rule(
        category="local_input_cache",
        severity="medium",
        pattern=r"\bread_csv\s*\(",
        why_it_matters="CSV reads signal local cache or input dependencies that should be surfaced during migration planning.",
        preferred_wps_replacement="Move stable inputs into worksheet tabs, config sheets, or supported external systems.",
        official_basis="The repository scanner should identify local cache and input dependencies before migration.",
    ),
    Rule(
        category="local_input_cache",
        severity="medium",
        pattern=r"\bread_excel\s*\(",
        why_it_matters="Excel reads indicate local workbook dependencies that may not exist inside WPS runtime.",
        preferred_wps_replacement="Use worksheet reads through `xl()` when the source data belongs in KDocs.",
        official_basis="Dedicated worksheet API pages document `xl()` for sheet-native input.",
    ),
    Rule(
        category="local_input_cache",
        severity="medium",
        pattern=r"\bExcelFile\s*\(",
        why_it_matters="Workbook file readers are usually part of local cache or import pipelines.",
        preferred_wps_replacement="Model the source as worksheet ET or external ingestion instead of local workbook reads.",
        official_basis="Repository migration guidance treats local workbook access as a risky construct.",
    ),
    Rule(
        category="local_input_cache",
        severity="medium",
        pattern=r"json\.load\s*\(",
        why_it_matters="JSON file reads often indicate local config or cache files that need a cloud-safe replacement.",
        preferred_wps_replacement="Prefer `config` worksheet rows, supported APIs, or worksheet-backed caches.",
        official_basis="Repository experience rules prefer workbook-driven config via a `config` sheet.",
    ),
    Rule(
        category="local_input_cache",
        severity="medium",
        pattern=r"json\.dump\s*\(",
        why_it_matters="JSON file writes are a local persistence pattern that should be captured during migration.",
        preferred_wps_replacement="Write audit outputs to sheets or supported external systems instead of local JSON files.",
        official_basis="Repository defaults avoid local filesystem persistence in WPS migrations.",
    ),
    Rule(
        category="local_input_cache",
        severity="medium",
        pattern=r"csv\.(reader|writer)\s*\(",
        why_it_matters="CSV reader and writer flows commonly indicate local caches or inter-process handoff files.",
        preferred_wps_replacement="Use worksheet tabs or structured external interfaces instead of local CSV files.",
        official_basis="Repository migration guidance treats local cache files as rewrite candidates.",
    ),
    Rule(
        category="openpyxl_local_workbook",
        severity="high",
        pattern=r"\bopenpyxl\b",
        why_it_matters="Direct openpyxl usage usually implies local workbook or formatting logic that does not carry over as-is.",
        preferred_wps_replacement="Prefer worksheet writes and simplify formatting-heavy flows unless runtime support is explicitly verified.",
        official_basis="The repository uses worksheet APIs as the default stable output surface.",
    ),
    Rule(
        category="workbook_formatting_risk",
        severity="medium",
        pattern=r"\b(CellRichText|InlineFont|PatternFill|Font|Alignment|Border|NamedStyle)\b",
        why_it_matters="Workbook formatting and rich-text features often depend on local Excel semantics rather than WPS sheet writes.",
        preferred_wps_replacement="Reduce outputs to tabular data or verify each richer presentation feature explicitly.",
        official_basis="Repository guidance treats local-only workbook formatting as a migration risk.",
    ),
    Rule(
        category="workbook_formatting_risk",
        severity="medium",
        pattern=r"\bmerge_cells\s*\(",
        why_it_matters="Merged-cell layout logic usually indicates presentation-heavy workbook coupling.",
        preferred_wps_replacement="Prefer flat tabular outputs unless a richer presentation requirement is explicitly confirmed.",
        official_basis="Repository defaults favor tabular outputs over local-only workbook formatting flows.",
    ),
    Rule(
        category="workbook_formatting_risk",
        severity="medium",
        pattern=r"\bconditional_formatting\b",
        why_it_matters="Conditional formatting flows are often workbook-specific and require explicit runtime confirmation.",
        preferred_wps_replacement="Keep the data output and document presentation assumptions separately.",
        official_basis="Repository migration guidance separates official guarantees from richer runtime-dependent behavior.",
    ),
    Rule(
        category="html_parsing_dependency",
        severity="medium",
        pattern=r"\blxml\b",
        why_it_matters="`lxml` support is not part of the repository-safe verified surface and usually needs replacement.",
        preferred_wps_replacement="Prefer `BeautifulSoup` when HTML parsing is still required.",
        official_basis="Repository guidance explicitly recommends replacing `lxml` unless support is confirmed.",
    ),
    Rule(
        category="timezone_risk",
        severity="medium",
        pattern=r"Timestamp\.now\s*\(.*tz\s*=",
        why_it_matters="Timezone-aware pandas calls may behave differently in constrained runtimes.",
        preferred_wps_replacement="Use WPS-safe arithmetic offsets or deterministic naive datetime handling when required.",
        official_basis="Repository experience rules mark timezone conversion as a runtime-sensitive area.",
    ),
    Rule(
        category="timezone_risk",
        severity="medium",
        pattern=r"\.tz_convert\s*\(",
        why_it_matters="Timezone conversion often needs runtime-specific handling in WPS migrations.",
        preferred_wps_replacement="Prefer arithmetic offset or simplified datetime handling when the runtime is unreliable.",
        official_basis="Repository experience rules mark `tz_convert` as a risky construct.",
    ),
    Rule(
        category="timezone_risk",
        severity="medium",
        pattern=r"\.tz_localize\s*\(",
        why_it_matters="Timezone localization often needs runtime-specific handling in WPS migrations.",
        preferred_wps_replacement="Prefer arithmetic offset or simplified datetime handling when the runtime is unreliable.",
        official_basis="Repository experience rules mark `tz_localize` as a risky construct.",
    ),
    Rule(
        category="timezone_risk",
        severity="medium",
        pattern=r"\bzoneinfo\b",
        why_it_matters="Runtime timezone database support may not match local Python behavior.",
        preferred_wps_replacement="Prefer deterministic offsets or carefully scoped timezone handling.",
        official_basis="Repository experience rules treat timezone logic as assumption-heavy.",
    ),
    Rule(
        category="timezone_risk",
        severity="medium",
        pattern=r"\bpytz\b",
        why_it_matters="Third-party timezone libraries often signal logic that needs migration review.",
        preferred_wps_replacement="Prefer deterministic offsets or explicitly tested timezone handling.",
        official_basis="Repository scanner should identify timezone-sensitive code paths.",
    ),
    Rule(
        category="timezone_risk",
        severity="medium",
        pattern=r"\.astimezone\s*\(",
        why_it_matters="Timezone conversion calls may produce runtime-specific behavior differences.",
        preferred_wps_replacement="Prefer deterministic offsets or explicitly tested timezone handling.",
        official_basis="Repository scanner should identify timezone-sensitive code paths.",
    ),
    Rule(
        category="timezone_risk",
        severity="medium",
        pattern=r"datetime\.now\s*\([^)]*timezone",
        why_it_matters="Timezone-aware `datetime.now(...)` usage may require runtime-specific validation.",
        preferred_wps_replacement="Use deterministic offsets when timezone features are not guaranteed.",
        official_basis="Repository scanner should identify timezone-sensitive code paths.",
    ),
    Rule(
        category="wps_sheet_io_present",
        severity="info",
        pattern=r"\bwrite_xl\s*\(",
        why_it_matters="This code already references WPS worksheet write APIs and may already be partially migrated.",
        preferred_wps_replacement="Review whether the surrounding logic still depends on local filesystem assumptions.",
        official_basis="Dedicated worksheet API pages document `write_xl()` as the worksheet output surface.",
    ),
    Rule(
        category="wps_sheet_io_present",
        severity="info",
        pattern=r"\bxl\s*\(",
        why_it_matters="This code already references WPS worksheet read APIs and may already be partially migrated.",
        preferred_wps_replacement="Review whether the surrounding logic still mixes local and WPS-native data access.",
        official_basis="Dedicated worksheet API pages document `xl()` as the worksheet input surface.",
    ),
    Rule(
        category="wps_sheet_io_present",
        severity="info",
        pattern=r"\bdelete_xl\s*\(",
        why_it_matters="This code already references worksheet cleanup APIs and may already be partially migrated.",
        preferred_wps_replacement="Prefer `delete_xl()` over runtime-dependent object-model cleanup when possible.",
        official_basis="Dedicated worksheet API pages document `delete_xl()` as the worksheet deletion surface.",
    ),
    Rule(
        category="data_table_api_present",
        severity="info",
        pattern=r"\bdbt\s*\(",
        why_it_matters="This code already references WPS data-table reads and should be classified as data-table aware.",
        preferred_wps_replacement="Verify that the workflow truly needs record-level CRUD instead of worksheet ET.",
        official_basis="Dedicated data-table API pages document `dbt()` as the read surface.",
    ),
    Rule(
        category="data_table_api_present",
        severity="info",
        pattern=r"\binsert_dbt\s*\(",
        why_it_matters="This code already references WPS data-table inserts and should preserve record semantics.",
        preferred_wps_replacement="Keep record ids and compatible field types explicit when planning writeback.",
        official_basis="Dedicated data-table API pages document `insert_dbt()` as the insert surface.",
    ),
    Rule(
        category="data_table_api_present",
        severity="info",
        pattern=r"\bupdate_dbt\s*\(",
        why_it_matters="This code already references WPS data-table updates and likely depends on record ids.",
        preferred_wps_replacement="Preserve `DataFrame.index` or `_rid` semantics for update paths.",
        official_basis="Dedicated data-table API pages document `update_dbt()` as the update surface.",
    ),
    Rule(
        category="data_table_api_present",
        severity="info",
        pattern=r"\bdelete_dbt\s*\(",
        why_it_matters="This code references a data-table deletion path that the repository does not currently verify.",
        preferred_wps_replacement="Treat the call as unverified and re-check live docs before relying on it.",
        official_basis="The manifest keeps `delete_dbt()` under `unverified_or_snapshot_only`.",
    ),
    Rule(
        category="cross_document_or_object_model",
        severity="medium",
        pattern=r"\bbook_url\s*=",
        why_it_matters="Cross-document sheet access affects migration scope and document boundaries.",
        preferred_wps_replacement="Prefer official `book_url` flows before object-model-only alternatives.",
        official_basis="The manifest verifies `book_url` through dedicated API pages.",
    ),
    Rule(
        category="cross_document_or_object_model",
        severity="medium",
        pattern=r"Application\.Worksheets\.Item\s*\(",
        why_it_matters="Object-model worksheet access may be more runtime-dependent than dedicated worksheet helpers.",
        preferred_wps_replacement="Prefer `xl()`, `write_xl()`, and `delete_xl()` first.",
        official_basis="Repository experience rules prefer worksheet helpers over object-model fallbacks.",
    ),
    Rule(
        category="cross_document_or_object_model",
        severity="medium",
        pattern=r"Workbooks\.Open\s*\(",
        why_it_matters="Cross-document object-model flows have a lighter verification level than dedicated API pages.",
        preferred_wps_replacement="Treat `Workbooks.Open(fileID, type)` as summary-example verified and keep stronger worksheet/data-table APIs as the default.",
        official_basis="The manifest classifies `Workbooks.Open(fileID, type)` as `summary_example_verified`.",
    ),
    Rule(
        category="external_access_or_allowlist",
        severity="medium",
        pattern=r"\brequests\b",
        why_it_matters="Outbound HTTP calls may require WPS allowlisting or runtime assumptions.",
        preferred_wps_replacement="Document external access assumptions and prefer `requests.Session` with retry support.",
        official_basis="Repository guidance requires identifying external HTTP dependencies during migration planning.",
    ),
    Rule(
        category="external_access_or_allowlist",
        severity="medium",
        pattern=r"\bSession\s*\(",
        why_it_matters="Session-based HTTP flows indicate stateful outbound access that should be reviewed for allowlisting and retries.",
        preferred_wps_replacement="Document external access assumptions and keep retries explicit.",
        official_basis="Repository experience rules recommend `requests.Session` with retry support.",
    ),
    Rule(
        category="external_access_or_allowlist",
        severity="medium",
        pattern=r"\bpymysql\b",
        why_it_matters="Database access may depend on network reachability and WPS runtime egress assumptions.",
        preferred_wps_replacement="Record allowlist and connectivity assumptions alongside migration output.",
        official_basis="The repository requires identifying external database dependencies before migration.",
    ),
    Rule(
        category="external_access_or_allowlist",
        severity="medium",
        pattern=r"\bsqlalchemy\b",
        why_it_matters="Database access may depend on network reachability and WPS runtime egress assumptions.",
        preferred_wps_replacement="Record allowlist and connectivity assumptions alongside migration output.",
        official_basis="The repository requires identifying external database dependencies before migration.",
    ),
    Rule(
        category="external_access_or_allowlist",
        severity="medium",
        pattern=r"\bpsycopg2\b",
        why_it_matters="Database access may depend on network reachability and WPS runtime egress assumptions.",
        preferred_wps_replacement="Record allowlist and connectivity assumptions alongside migration output.",
        official_basis="The repository requires identifying external database dependencies before migration.",
    ),
    Rule(
        category="external_access_or_allowlist",
        severity="medium",
        pattern=r"\bredis\b",
        why_it_matters="Cache or message-broker connectivity may not be available without explicit runtime assumptions.",
        preferred_wps_replacement="Document the dependency and confirm network assumptions before migration.",
        official_basis="The repository requires identifying external service dependencies before migration.",
    ),
]


def iter_python_files(root: Path) -> tuple[list[Path], list[IgnoredDirectoryHit]]:
    """Return Python files under the provided root path and ignored directory hits."""
    if root.is_file():
        if root.suffix != ".py":
            return [], []
        if any(part in IGNORED_DIR_NAMES for part in root.parts):
            return [], [IgnoredDirectoryHit(directory_path=str(root.parent), reason="ignored_dir_name")]
        return [root], []

    python_files: list[Path] = []
    ignored_hits: list[IgnoredDirectoryHit] = []

    for current_dir, dir_names, file_names in os.walk(root):
        dir_names.sort()
        skipped_dir_names = sorted(name for name in dir_names if name in IGNORED_DIR_NAMES)
        for dir_name in skipped_dir_names:
            ignored_hits.append(
                IgnoredDirectoryHit(
                    directory_path=str(Path(current_dir) / dir_name),
                    reason="ignored_dir_name",
                )
            )
        dir_names[:] = [name for name in dir_names if name not in IGNORED_DIR_NAMES]

        for file_name in sorted(file_names):
            if file_name.endswith(".py"):
                python_files.append(Path(current_dir) / file_name)

    python_files.sort()
    return python_files, ignored_hits


def strip_strings_and_comments(text: str) -> str:
    """Return source text with string literals and comments blanked out."""
    lines = [list(line) for line in text.splitlines(keepends=True)]
    reader = io.StringIO(text).readline

    try:
        tokens = tokenize.generate_tokens(reader)
    except (IndentationError, tokenize.TokenError):
        return text

    # 保留原始行列布局，只擦除字符串和注释，避免把示例文本误判成真实依赖。
    for token_info in tokens:
        if token_info.type not in {tokenize.STRING, tokenize.COMMENT}:
            continue

        start_row, start_col = token_info.start
        end_row, end_col = token_info.end
        for row_index in range(start_row - 1, end_row):
            line = lines[row_index]
            replace_start = start_col if row_index == start_row - 1 else 0
            replace_end = end_col if row_index == end_row - 1 else len(line)
            for column_index in range(replace_start, min(replace_end, len(line))):
                if line[column_index] != "\n":
                    line[column_index] = " "

    return "".join("".join(line) for line in lines)


def scan_file(file_path: Path, replace_invalid_utf8: bool = False) -> ScanFileResult:
    """Scan one Python file for known incompatibility patterns."""
    try:
        text = file_path.read_text(encoding="utf-8")
        encoding_issues: list[EncodingIssue] = []
    except UnicodeDecodeError as exc:
        action = (
            "replaced_invalid_utf8_then_scanned"
            if replace_invalid_utf8
            else "skipped_non_utf8_file"
        )
        encoding_issues = [
            EncodingIssue(
                file_path=str(file_path),
                error_type=type(exc).__name__,
                message=str(exc),
                action=action,
            )
        ]
        if not replace_invalid_utf8:
            return ScanFileResult(findings=[], encoding_issues=encoding_issues)
        text = file_path.read_text(encoding="utf-8", errors="replace")

    cleaned_text = strip_strings_and_comments(text)
    findings: list[Finding] = []
    original_lines = text.splitlines()
    cleaned_lines = cleaned_text.splitlines()

    for line_number, (original_line, cleaned_line) in enumerate(
        zip(original_lines, cleaned_lines),
        start=1,
    ):
        matched_categories: set[str] = set()
        for rule in RULES:
            if rule.category in matched_categories:
                continue
            if rule.compiled_pattern.search(cleaned_line):
                findings.append(
                    Finding(
                        file_path=str(file_path),
                        line_number=line_number,
                        category=rule.category,
                        severity=rule.severity,
                        pattern=rule.pattern,
                        line_text=original_line.strip(),
                        why_it_matters=rule.why_it_matters,
                        preferred_wps_replacement=rule.preferred_wps_replacement,
                        official_basis=rule.official_basis,
                    )
                )
                matched_categories.add(rule.category)

    return ScanFileResult(findings=findings, encoding_issues=encoding_issues)


def build_summary(findings: list[Finding]) -> dict[str, int]:
    """Aggregate counts by category."""
    summary: dict[str, int] = {}
    for finding in findings:
        summary[finding.category] = summary.get(finding.category, 0) + 1
    return dict(sorted(summary.items(), key=lambda item: item[0]))


def build_severity_summary(findings: list[Finding]) -> dict[str, int]:
    """Aggregate counts by severity."""
    summary: dict[str, int] = {}
    for finding in findings:
        summary[finding.severity] = summary.get(finding.severity, 0) + 1
    return dict(sorted(summary.items(), key=lambda item: item[0]))


def scan_path(root: Path, replace_invalid_utf8: bool = False) -> ScanReport:
    """Scan a project directory or one file and return a structured audit report."""
    if not root.exists():
        raise FileNotFoundError(f"Path not found: {root}")

    files, ignored_directory_hits = iter_python_files(root)
    findings: list[Finding] = []
    encoding_issues: list[EncodingIssue] = []

    for file_path in files:
        file_result = scan_file(file_path, replace_invalid_utf8=replace_invalid_utf8)
        findings.extend(file_result.findings)
        encoding_issues.extend(file_result.encoding_issues)

    return ScanReport(
        scanned_path=str(root),
        python_file_count=len(files),
        finding_count=len(findings),
        summary_by_category=build_summary(findings),
        summary_by_severity=build_severity_summary(findings),
        encoding_issues=encoding_issues,
        ignored_directory_hits=ignored_directory_hits,
        findings=findings,
        rule_version=RULE_VERSION,
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Scan a Python project for patterns that often need changes "
            "in WPS online migrations."
        )
    )
    parser.add_argument(
        "path",
        type=Path,
        help="Project directory or a single Python file to scan.",
    )
    parser.add_argument(
        "--replace-invalid-utf8",
        action="store_true",
        help="Replace invalid UTF-8 bytes and keep scanning instead of skipping the file.",
    )
    args = parser.parse_args()

    report = scan_path(args.path, replace_invalid_utf8=args.replace_invalid_utf8)
    print(json.dumps(asdict(report), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
