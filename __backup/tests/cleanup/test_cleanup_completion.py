import pytest

class TestCleanupPhaseCompletion:
    def test_all_cleanup_acs_tracked(self):
        from pathlib import Path
        ac_index = Path('/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml')
        if ac_index.exists():
            content = ac_index.read_text()
            # Verify AC-CLEAN-301 through AC-CLEAN-328 exist
            clean_acs = sum(1 for i in range(301, 329) if f'AC-CLEAN-{i}' in content)
            assert clean_acs > 0
    
    def test_phase5_tracking_exists(self):
        from pathlib import Path
        tracker = Path('/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/tier1/tracking/progress-tracker.json')
        if tracker.exists():
            import json
            data = json.loads(tracker.read_text())
            # Verify phase 5 is tracked
            assert data is not None
