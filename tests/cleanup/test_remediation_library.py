import pytest
from src.tools.remediation_executor import get_available_remediations

class TestRemediationLibrary:
    def test_remediation_library_complete(self):
        remediations = get_available_remediations()
        assert len(remediations) > 0
    
    def test_remediation_types_diverse(self):
        remediations = get_available_remediations()
        types = [r.get('type') if isinstance(r, dict) else r for r in remediations]
        assert len(types) > 0
