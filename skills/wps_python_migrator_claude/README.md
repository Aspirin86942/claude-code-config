# wps_python_migrator

Official-doc-driven Codex skill for migrating local Python backends, ETL jobs,
and report scripts into the WPS online Python runtime.

## Source of truth

- Single source of truth: `references/official_capabilities.yml`
- Official entrypoint: `https://airsheet.wps.cn/pydocs/introduction/summary.html`
- Local snapshot only: `wps参考手册.md`

## Verification boundary

- `dedicated_api_doc_verified`: repository-safe capabilities with dedicated WPS
  API pages, such as `xl()`, `write_xl()`, `delete_xl()`, `dbt()`,
  `insert_dbt()`, and `update_dbt()`
- `summary_example_verified`: capabilities shown in the official summary page,
  such as `Workbooks.Open(fileID, type)`
- `unverified_or_snapshot_only`: items that still need re-checking before they
  are treated as repository-safe defaults, such as `delete_dbt()`,
  `dbt(..., condition=...)`, and `polars`

## Repository defaults

- Prefer worksheet outputs by default.
- Use data tables only for genuine record-level CRUD flows with compatible
  field types.
- Keep repository experience rules separate from official guarantees.
- Data-table write support is incomplete, and complex or object-like fields may
  degrade on writeback.
- The repository keeps a preferred verified library subset in the manifest; the
  full official library surface stays linked from the official docs.
