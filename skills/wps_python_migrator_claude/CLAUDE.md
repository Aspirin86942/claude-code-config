# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

WPS Python Migrator - A Codex skill package for migrating local Python backends, ETL jobs, and report scripts to the WPS online Python runtime (KDocs smart sheets and data tables).

**Official Docs**: https://airsheet.wps.cn/pydocs/introduction/summary.html

## Commands

```bash
# Run incompatibility pattern scanner on a project
python scripts/scan_incompatible_patterns.py <path>

# Run tests
python -m pytest -q

# Syntax check scripts
python -m compileall scripts
```

## Architecture

**Single Source of Truth**: `references/official_capabilities.yml` - machine-readable capability manifest with verification levels:
- `dedicated_api_doc_verified` - APIs with dedicated WPS docs (xl, write_xl, delete_xl, dbt, insert_dbt, update_dbt)
- `summary_example_verified` - Shown in official summary (Workbooks.Open)
- `unverified_or_snapshot_only` - Need re-checking (delete_dbt, polars)

**Core Files**:
- `SKILL.md` - Skill entry point and migration workflow
- `scripts/scan_incompatible_patterns.py` - Scans for incompatible patterns (local file I/O, timezone risks, unverified libs)
- `tests/` - Unit tests for scanner and skill docs validation
- `references/wps-compatibility.md` - Platform constraints and replacements
- `references/transformation-checklist.md` - Migration checklist
- `example/wps 版本脚本.py` - Runnable WPS-native example with reusable patterns

**Environment**: Conda `test` env with Python 3.10, pytest, pyyaml (`environment.yml`)

## WPS API Surface

**Worksheet APIs** (report outputs, cache tabs, matrix data):
- `xl()` - read sheets, `write_xl()` - write sheets, `delete_xl()` - cleanup

**Data-table APIs** (record-level CRUD only):
- `dbt()` - read, `insert_dbt()` - insert, `update_dbt()` - update (preserves `_rid`/DataFrame.index)

**Preferred verified libraries**: pandas, numpy, requests, bs4, pymysql, pyecharts, akshare, tushare, baostock

**Key migration rules**:
- Replace local file I/O with worksheet tabs by default
- Replace `lxml` with `BeautifulSoup`
- Treat timezone logic (`zoneinfo`, `tz_convert`, `tz_localize`) as runtime-sensitive
- Use `requests.Session` with `Retry` for HTTP calls

## Coding Standards

- Python 3.10+, explicit UTF-8 encoding, type hints on public functions
- `snake_case` for code, `UPPER_CASE` for constants
- No silent failures (`except: pass`), preserve data integrity checks and `error_log` outputs
- Chinese comments for business logic explaining "why"

## Testing

Run `test_scan_incompatible_patterns.py` when modifying scanner rules. Tests cover:
- Pattern detection (structured categories, severities)
- String/comment filtering (no false positives)
- UTF-8 encoding handling
- CLI JSON output schema
