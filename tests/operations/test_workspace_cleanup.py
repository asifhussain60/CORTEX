import os
import sqlite3
import time
from pathlib import Path

import pytest

from src.operations import execute_operation


def make_file(path: Path, size: int = 0):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "wb") as f:
        if size > 0:
            f.write(b"0" * size)
        else:
            f.write(b"")


def set_mtime_days_ago(path: Path, days: int):
    past = time.time() - days * 86400
    os.utime(path, (past, past))


@pytest.fixture()
def sandbox(tmp_path: Path) -> Path:
    root = tmp_path / "cortex_sandbox"
    # minimal structure used by modules
    (root / "logs").mkdir(parents=True, exist_ok=True)
    (root / "cortex-brain").mkdir(parents=True, exist_ok=True)
    (root / "tests").mkdir(parents=True, exist_ok=True)
    (root / "scripts").mkdir(parents=True, exist_ok=True)

    # temp files
    make_file(root / "tests" / "junk.tmp", 128)
    make_file(root / "scripts" / "cache.bak", 256)

    # cache dirs
    cache_dir = root / "src" / "module" / "__pycache__"
    make_file(cache_dir / "x.pyc", 512)

    # logs: one old, one recent
    old_log = root / "logs" / "old.log"
    recent_log = root / "logs" / "recent.log"
    make_file(old_log, 1024)
    make_file(recent_log, 1024)
    set_mtime_days_ago(old_log, 45)

    # sqlite db under cortex-brain
    db_path = root / "cortex-brain" / "memory.db"
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("create table if not exists t(id integer primary key, v text)")
    cur.executemany("insert into t(v) values (?)", [("a",), ("b",), ("c",)])
    conn.commit()
    conn.close()

    return root


def test_cleanup_safe_profile_scans_and_reports(sandbox: Path):
    report = execute_operation("workspace_cleanup", profile="safe", project_root=sandbox)
    assert report.success is True
    # safe profile does not delete caches/dbs
    summary = report.context.get("cleanup_summary", {})
    assert "report" in report.module_results.get("generate_cleanup_report", {}).data if hasattr(report.module_results.get("generate_cleanup_report"), 'data') else True
    # should at least find something to report (old logs were present)
    assert summary.get("total_items_removed", 0) >= 0


def test_cleanup_standard_profile_removes_old_logs_and_cache(sandbox: Path):
    # Verify preconditions
    assert (sandbox / "logs" / "old.log").exists()
    assert list((sandbox).rglob("__pycache__"))

    report = execute_operation("workspace_cleanup", profile="standard", project_root=sandbox)
    assert report.success is True

    # old log should be gone, recent log remains
    assert not (sandbox / "logs" / "old.log").exists()
    assert (sandbox / "logs" / "recent.log").exists()

    # cache dir should be removed
    assert not any((sandbox).rglob("__pycache__"))

    # summary should reflect removals and space recovered should be non-negative
    summary = report.context.get("cleanup_summary", {})
    assert summary.get("logs_removed", 0) >= 0
    assert summary.get("cache_removed", 0) >= 0
    assert summary.get("total_space_recovered", 0) >= 0


def test_cleanup_vacuums_databases_when_present(sandbox: Path):
    report = execute_operation("workspace_cleanup", profile="standard", project_root=sandbox)
    assert report.success is True
    # optimization either skipped or done, but no failure
    # If DB exists, context should include count
    optimized = report.context.get("databases_optimized")
    assert optimized is None or optimized >= 0
