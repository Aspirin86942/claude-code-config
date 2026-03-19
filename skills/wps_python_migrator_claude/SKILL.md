# WPS Python Migrator

Convert local Python scripts or repositories into WPS online Python code that runs inside KDocs smart sheets and data tables.

## Workflow

Follow this sequence:

1. **Inspect** - Use Explore subagent for multi-file projects (>3 `.py` files)
2. **Classify** - Identify target surface: worksheet ET, data-table DB, or hybrid
3. **Verify** - Use Context7 MCP for unverified APIs or third-party libraries
4. **Plan** - Use Planner subagent for complex migrations
5. **Rewrite** - Apply WPS-native patterns and replacements
6. **Review** - Activate specialized reviewers (security, database, python, etc.)
7. **Validate** - Final checklist before delivery

## Inspect the project first

Treat the task as a repository-level migration unless the user explicitly limits scope.

- Scan every relevant `.py` file before editing.
- Identify entrypoints, shared utilities, config modules, and persistence layers.
- Identify whether each output is report-like worksheet data or record-like data-table data.
- Identify external HTTP or database calls that may require WPS allowlisting.
- Run `scripts/scan_incompatible_patterns.py <path>` when a project contains multiple files or when the incompatibilities are not obvious.
- Summarize findings as reusable migration rules before rewriting code.

## Use subagents for efficiency

For projects with more than 3 `.py` files or unclear structure, leverage specialized subagents:

1. **Explore subagent** - Launch to map the codebase:
   > "Explore this Python project to identify: (1) entry scripts and main functions, (2) shared utilities and helpers, (3) config files and external dependencies (HTTP/DB), (4) local file I/O patterns, (5) output targets (worksheets vs data-tables). Return a structured summary with file paths and their roles."

2. **Planner subagent** - For complex migrations or hybrid (worksheet + data-table) targets:
   > "Design a migration plan for this WPS migration. Output: (1) Goal/Non-Goals, (2) API Contract (worksheet vs data-table), (3) Commit Plan (independent, reversible steps)"

3. **Context7 MCP** - For unverified APIs (`delete_dbt`, `polars`, `dbt(..., condition=...)`) or third-party libraries not in the verified subset:
   - Call `resolve-library-id` then `query-docs` to verify current WPS support
   - Mark verification level in final output:
     - `dedicated_api_doc_verified` - Official API docs exist
     - `summary_example_verified` - Shown in summary only
     - `unverified_or_snapshot_only` - Needs manual confirmation

4. **Specialized Reviewers** - Activate after migration (see Review section below)

Single-file migrations may skip subagents and proceed directly.

## Apply official WPS rules first

Use the live WPS Python docs at
`https://airsheet.wps.cn/pydocs/introduction/summary.html` as the source of
truth. Treat `references/official_capabilities.yml` as the repository's single
machine-readable capability manifest and `wps参考手册.md` as a local snapshot
that can drift away from the online docs. The manifest is the only place that
stores `last_verified_against_official_docs`.

Then use `references/wps-compatibility.md` and
`references/transformation-checklist.md` to apply repository-specific migration
guidance.

Choose APIs by data model:

- Use worksheet APIs such as `xl()`, `write_xl()`, and `delete_xl()` for
  report outputs, cache tabs, matrix-style data, or range-based rewrites.
- Default to worksheet outputs unless the workflow truly needs record-level
  CRUD semantics.
- Use data-table APIs such as `dbt()`, `insert_dbt()`, and `update_dbt()` only
  when the workflow is really record CRUD and the target fields are compatible
  with the currently documented write limitations.
- Use `book_url` when the workflow reads or writes another KDocs document.
- Preserve `_rid` or DataFrame index semantics when updating data-table rows.
  The official `dbt()` contract documents record ids in `DataFrame.index`.
- Treat `Workbooks.Open(fileID, type)` as `summary_example_verified`: it
  appears in the official summary page, but it is not a substitute for the
  dedicated worksheet and data-table API pages used by this repository.
- Treat `delete_dbt()` and `dbt(..., condition=...)` as
  `unverified_or_snapshot_only` unless they are re-checked against the live
  docs for the current migration.

Prefer keeping officially documented libraries when they already solve the job:

- `pandas`
- `numpy`
- `requests`
- `bs4`
- `pymysql`
- `pyecharts`
- `akshare`
- `tushare`
- `baostock`

Treat `polars` as `unverified_or_snapshot_only` until it is re-confirmed
against the live third-party library page. The manifest keeps a preferred
verified subset, not a mirror of the full official third-party catalog.

Then apply migration replacements:

- Replace local file outputs with worksheet tabs by default.
- Replace local CSV or Excel cache files with sheet-native caches.
- Only map outputs to data tables when the job needs true record CRUD and the
  write path can stay within compatible scalar-like field types.
- When data-table records contain complex objects, attachments, or unsupported
  field types, prefer worksheet outputs or explicit text serialization over
  optimistic direct writes.
- Replace `lxml` parsing with `BeautifulSoup` unless the runtime support is
  explicitly confirmed.
- Replace local-only workbook formatting flows with tabular outputs unless the
  user explicitly requires a richer alternative supported by WPS.

Preserve these properties unless the user requests otherwise:

- keep `pandas`-based transformations when they are already sound
- keep data integrity checks
- keep explicit `error_log` outputs
- keep non-silent failures
- keep deterministic merge keys, `_rid`, and normalization logic

## Decide the output shape

Choose the output form that matches the user request:

- **single file migration**: return one WPS-compatible script
- **multi-file project migration**: return an adapted project structure or a consolidated WPS entry script plus helper modules
- **skill-authoring task**: extract reusable migration rules and improve the skill documentation or create related knowledge assets

Use worksheet tabs for report-style outputs such as `result`, `error_log`,
`integrity_report`, and cache sheets. Use data tables only when the local
workflow truly models records that need insert or update semantics and the
field types remain compatible with documented write limits.

## Experience-based notes

These are repository experience rules, not official API guarantees. Mark them
as assumptions in the final migration when they matter.

- Timezone logic that depends on `zoneinfo`, `tz_convert`, or `tz_localize`
  often needs WPS-safe arithmetic or naive datetime handling.
- Worksheet existence checks may need retry logic between existing-sheet and
  `new_sheet=True` writes if runtime behavior is inconsistent.

## Reusable runtime patterns from the runnable example

The repository also includes a runnable WPS-native example in
`example/wps版本脚本.py`. Treat it as a source of reusable runtime patterns, not
as an official contract and not as a business-specific template.

Prefer these implementation shapes when they fit the user request:

- start WPS-native entry scripts with an `assert_wps_runtime()` style check for
  `xl`, `write_xl`, and `Application`
- prefer official worksheet helpers first: use `delete_xl()` for documented
  range, row, column, or sheet cleanup before falling back to object-model-only
  calls such as `Application.Worksheets.Item(...)`
- keep worksheet access behind helpers such as `get_worksheet()`,
  `read_sheet_df()`, and `write_sheet_df()` instead of scattering raw `xl()`
  and `write_xl()` calls throughout business logic
- when overwriting result sheets, prefer this sequence:
  clear existing contents if possible, try normal `write_xl(...)`, fall back to
  `new_sheet=True`, and retry normal write if the runtime reports duplicated
  sheet names
- when runtime parameters belong in the workbook, prefer a `config` worksheet
  normalized to `key` / `value` pairs; parse known fields explicitly, fall back
  to defaults deterministically, and record config issues in `error_log` plus
  `integrity_report`
- prefer a structured `error_log` shape with fields such as `run_id`,
  `source`, `severity`, `error_code`, `error_type`, `message`, `retryable`,
  locator columns, and `action` so multi-step pipelines can merge reviewable
  warnings and blocking errors
- use explicit output sheets such as `result`, `error_log`,
  `integrity_report`, `run_summary`, and `_cache_*`; add business-specific
  summary sheets only when they materially help downstream review
- for external HTTP calls, prefer `requests.Session` with `Retry` and
  `HTTPAdapter` rather than ad-hoc request loops
- record non-blocking issues in `error_log` with a severity such as `WARN`, and
  raise a blocking exception at the end if `ERROR` records remain

## Review using specialized subagents

After migration, activate appropriate reviewers based on what the migrated code does:

| Trigger | Activate | Focus Areas |
| :--- | :--- | :--- |
| External HTTP calls, API keys, user input | `security-reviewer` | Secrets, injection, retry logic, SSRF |
| Database/SQL queries, ORM operations | `database-reviewer` | N+1 queries, indexes, RLS, `FOR UPDATE` locks |
| Python code written or modified | `python-reviewer` | Type hints, vectorization, error handling, PEP 8 |
| Go/TypeScript code in scope | `go-reviewer` / `code-reviewer` | Idiomatic patterns, Hook dependencies, type safety |
| Build or type errors | `*-build-resolver` | Minimal diff fixes to get build green |
| Complex refactoring or dead code | `refactor-cleaner` | Unused imports, duplicate logic, consolidation |
| Core business flows need validation | `e2e-runner` | Playwright tests for critical paths |

Conclusion format: `[Must Fix: 上线前必改] / [Nice to Have: 后续优化]`

## Validate before finishing

Before finishing, verify:

- imports are officially documented or have been replaced
- the live online docs were checked first and any mismatch with
  `wps参考手册.md` is treated in favor of the online docs
- the migration keeps official guarantees, `summary_example_verified` items,
  and repository experience rules clearly separated
- no critical path depends on local filesystem persistence unless the user explicitly accepts that risk
- the chosen API surface matches the real data model: worksheet ET vs data-table DB
- worksheet output is the default unless record-level CRUD semantics clearly
  require a data-table surface
- `book_url`, `headers`, `formula`, `overfill`, or `write_df_index` are used when the migration depends on them
- `_rid` is preserved for data-table updates and deletes
- data-table write limits and complex-field downgrade behavior are documented
  when the workflow writes back to data tables
- a WPS-native script uses a runtime assertion or an equivalent guard against accidental local execution
- `delete_xl()` is preferred over undocumented or runtime-dependent object-model
  deletion flows when the job needs worksheet cleanup
- result sheets are cleared or overwritten in a deterministic way so stale rows do not survive reruns
- `config` worksheet assumptions and fallback behavior are documented when
  runtime parameters come from workbook data
- `error_log` and `integrity_report` are present when the workflow performs ETL, crawling, or reconciliation
- `error_log` is normalized enough for audit review and includes run-level
  context such as `run_id` when multiple phases contribute records
- `run_summary` is present when the workflow has multiple stages, cache reuse,
  or handoff review needs
- blocking errors are surfaced at the end rather than silently logged and ignored
- exception handling does not suppress blocking errors
- external systems note any required allowlist or public-IP assumptions

If the migration still contains unverified assumptions, mark them explicitly.

## Use the bundled resources

- Read the live docs at `https://airsheet.wps.cn/pydocs/introduction/summary.html`
  first.
- Read `references/official_capabilities.yml` next for the repository's current
  verified capability manifest and status levels.
- Read `wps参考手册.md` only as a local snapshot that may lag behind the live
  docs.
- Read `example/wps版本脚本.py` for runnable helper patterns around sheet IO,
  retries, cache tabs, and blocking-error escalation.
- Read `references/wps-compatibility.md` for platform-specific constraints and preferred replacements.
- Read `references/transformation-checklist.md` for the migration checklist and output expectations.
- Run `scripts/scan_incompatible_patterns.py <path>` to scan a repo for risky constructs before editing.
