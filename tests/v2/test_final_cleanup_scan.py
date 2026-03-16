"""Phase M12 tests for final cleanup report and parity reconciliation ledger."""

from __future__ import annotations

from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load(path: str) -> dict:
    data = yaml.safe_load((REPO_ROOT / path).read_text(encoding="utf-8"))
    assert isinstance(data, dict)
    return data


def test_m12_cleanup_report_closes_chat_digest_ledger_items() -> None:
    """Cleanup report closes all chat-digest deletion ledger entries."""
    report = _load(
        "cortex-registry/planning/phases/v2/artifacts/phase-m12/final-cleanup-report.yaml"
    )
    assert report["legacy_module_scan"]["unresolved_count"] == 0

    statuses = {entry["id"]: entry["status"] for entry in report["chat_digest_cleanup_ledger"]}
    for item_id in ["CHAT01-DEL-01", "CHAT01-DEL-02", "CHAT01-DEL-03", "CHAT01-DEL-04", "CHAT01-DEL-05"]:
        assert statuses[item_id] == "CLOSED"


def test_m12_capability_parity_ledger_has_required_categories() -> None:
    """Capability parity ledger tracks preserved, strategic, and intentional removals."""
    ledger = _load(
        "cortex-registry/planning/phases/v2/artifacts/phase-m12/capability-parity-ledger.yaml"
    )
    categories = ledger["categories"]
    assert categories["preserved"]
    assert categories["strategic_replacement"]
    assert categories["intentional_removal"]
