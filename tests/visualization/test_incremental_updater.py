"""Test Incremental Updates (STATIC-VIZ-007)."""
from cortex.visualization.incremental_updater import IncrementalUpdater

def test_delta():
    updater = IncrementalUpdater()
    changed = updater.detect_changes([{"repo": "A", "ts": 100}], [{"repo": "A", "ts": 200}])
    assert len(changed) == 1 and changed[0]["repo"] == "A"

def test_no_change():
    updater = IncrementalUpdater()
    changed = updater.detect_changes([{"repo": "A", "ts": 100}], [{"repo": "A", "ts": 100}])
    assert len(changed) == 0
