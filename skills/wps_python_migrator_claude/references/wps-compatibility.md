# WPS online python compatibility guide

The live docs at `https://airsheet.wps.cn/pydocs/introduction/summary.html`
are the source of truth. Treat `references/official_capabilities.yml` as the
repository's single machine-readable contract and `wps参考手册.md` only as a
local snapshot that may drift.

## dedicated_api_doc_verified

Use these capabilities as the repository-safe official baseline.

### 1. Worksheet ET APIs

- `xl()`, `write_xl()`, and `delete_xl()` are the default stable worksheet
  surface
- `xl()` verified parameters include `headers`, `sheet_name`, `book_url`,
  `start_row`, `start_column`, `end_row`, `end_column`, and `formula`
- `write_xl()` verified parameters include `new_sheet`, `sheet_name`,
  `overfill`, `book_url`, `start_row`, `start_column`, and `write_df_index`
- `delete_xl()` verified parameters include `entire_row`, `entire_column`,
  `xl_shift_to_left`, `book_url`, `start_row`, `start_column`, and
  `drop_sheet`
- `xl(sheet_name=None)` and `xl(sheet_name=list[str])` are verified behaviors
  for multi-sheet reads

### 2. Data-table DB APIs

- `dbt()`, `insert_dbt()`, and `update_dbt()` are the repository-safe
  data-table surface
- `dbt()` verified parameters are `field`, `sheet_name`, and `book_url`
- `insert_dbt()` verified parameters include `new_sheet`
- `dbt()` keeps record ids in `DataFrame.index`, which is the official basis
  for `update_dbt()`-style update flows
- official docs explicitly warn that data-table write support is incomplete
- official docs explicitly warn that complex or object-like fields can be
  ignored, simplified, or otherwise degraded on writeback

### 3. Preferred verified library subset

The manifest keeps a repository-curated subset, not the complete official
catalog.

- `pandas`
- `numpy`
- `requests`
- `bs4`
- `pymysql`
- `pyecharts`
- `akshare`
- `tushare`
- `baostock`

## summary_example_verified

These items appear in the official summary page, but the repository keeps them
at a lighter contract level than dedicated API pages.

- `Workbooks.Open(fileID, type)` is official summary-example coverage, not an
  equivalent replacement for worksheet/data-table APIs

## experience_based

These are repository recommendations built on top of the official APIs and the
runnable example. They are useful defaults, but they are not official API
guarantees.

- prefer worksheet outputs by default; move to data tables only when the job
  really needs record-level CRUD and the field types are compatible with
  documented write limits
- map local file reports to worksheet tabs such as `result`, `error_log`,
  `integrity_report`, `run_summary`, and `_cache_*`
- prefer `delete_xl()` for documented worksheet cleanup before falling back to
  object-model-only calls such as `Application.Worksheets.Item(...)`
- use an `assert_wps_runtime()` style guard so the script fails fast outside the
  WPS editor when `xl`, `write_xl`, or `Application` are missing
- keep worksheet IO behind helper functions such as `read_sheet_df()` and
  `write_sheet_df()` so the business logic does not manage retry details
- prefer this write strategy for report sheets: clear old contents, try normal
  `write_xl(...)`, retry with `new_sheet=True`, then fall back to normal write
  again if the runtime reports a duplicated sheet name
- normalize workbook-driven runtime settings through a `config` sheet with
  `key` / `value` columns; parse known fields explicitly, fall back to defaults
  deterministically, and write config issues into `error_log` plus
  `integrity_report`
- prefer a structured `error_log` schema with `run_id`, `source`, `severity`,
  `error_code`, `error_type`, `message`, `retryable`, locator fields, and
  `action`
- when data-table records contain complex objects, attachments, or unsupported
  field types, prefer worksheet outputs or explicit text serialization
- for outbound HTTP, prefer `requests.Session` with `Retry` and `HTTPAdapter`
  rather than bare repeated `requests.get(...)` calls
- when time conversion is needed, prefer arithmetic offset or
  `datetime.utcnow() + timedelta(...)` over `tz_convert` / `tz_localize` if the
  runtime makes timezone support unreliable
- treat `WARN` and `ERROR` as different severities; blocking `ERROR` items
  should cause the run to fail after outputs are written

## unverified_or_snapshot_only

These items are still outside the repository-safe official baseline.

- `delete_dbt()` is not treated as verified in the current repository contract
- `dbt(..., condition=...)` is not treated as a verified live-doc signature
- `polars` appears outside the repository's current verified library subset
