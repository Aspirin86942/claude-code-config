# transformation checklist

Use this checklist before, during, and after a migration.

## 1. classify the target surface first

- decide whether the source workflow is worksheet ET, data-table DB, or hybrid
- default to worksheet outputs unless the workflow truly needs record-level CRUD
- confirm whether `book_url` is enough before reaching for object-model flows

## 2. inspect the repository

- identify entry scripts, shared helpers, config files, and local persistence
- identify external requests or database calls that may need allowlisting
- identify imports that may fail in WPS
- identify whether the script should assert the WPS runtime before doing any work
- identify any complex, object-like, or attachment-style fields before choosing
  a data-table write path

## 3. classify risky constructs

Look for:

- local file paths, `Path(...)`, `open(...)`
- local input or cache reads such as `read_csv(...)`, `read_excel(...)`,
  `ExcelFile(...)`, `json.load(...)`, or `csv.reader(...)`
- local workbook writes such as `to_excel(...)`, `ExcelWriter`, and openpyxl
  formatting features
- WPS-native APIs such as `xl()`, `write_xl()`, `delete_xl()`, `dbt()`,
  `insert_dbt()`, and `update_dbt()`
- cross-document or object-model calls such as `book_url`,
  `Application.Worksheets.Item(...)`, and `Workbooks.Open(...)`
- external access clients such as `requests`, `Session`, `pymysql`, or other
  database drivers
- timezone conversion calls such as `tz_convert`, `tz_localize`, `pytz`, or
  `astimezone(...)`

## 4. design the migration

- read the live docs first, then compare with
  `references/official_capabilities.yml`
- keep official guarantees, summary-example coverage, and experience rules
  separated in the migration notes
- map each local artifact to worksheet tabs, data tables, or a hybrid design
- preserve stable keys, `_rid`, integrity checks, and error logging
- decide whether worksheet IO should be wrapped in helpers such as
  `read_sheet_df()` / `write_sheet_df()`
- decide whether runtime parameters should come from a `config` sheet with
  `key` / `value` rows and explicit default-fallback rules
- decide whether worksheet cleanup should use `delete_xl()` before any
  object-model fallback
- decide whether outbound HTTP should use `requests.Session` with retry support

## 5. rewrite the code

- replace local output layers with worksheet APIs by default
- switch to data-table APIs only for genuine record CRUD with compatible field
  types
- replace unsupported parsing libraries
- replace timezone logic with WPS-safe logic when runtime behavior requires it
- normalize `error_log` into a stable audit schema with fields such as
  `run_id`, `severity`, `error_code`, `message`, `retryable`, raw value, and
  `action`
- add explicit output tabs such as `result`, `error_log`, `integrity_report`,
  `run_summary`, and `_cache_*` when the workflow needs auditability or caching

## 6. validate the result

- confirm the script no longer depends on persistent local files
- confirm the chosen API matches the real data model
- confirm worksheet cleanup prefers `delete_xl()` before runtime-dependent
  object-model fallbacks
- confirm `error_log` and `integrity_report` still exist
- confirm the integrity report includes row-count reconciliation plus at least
  one missing-field, coverage, or uniqueness-style check
- confirm `config` parse failures fall back deterministically and are written to
  `error_log` or `integrity_report`
- confirm `run_summary` exists when the workflow has multiple stages, cache
  reuse, or manual review handoff
- confirm blocking `ERROR` records still fail the run after outputs are written
- confirm any dependency on `delete_dbt()`, `dbt(..., condition=...)`, or
  `polars` is called out explicitly
- confirm multiple files or modules still import cleanly

## output expectation

Unless the user requests a different shape, provide:

1. a short migration summary with the chosen surface: worksheet, data table, or hybrid
2. the migrated WPS-compatible code
3. a list of official assumptions, summary-example assumptions, and unverified runtime assumptions
