import pytest
from src.tools.remediation_executor import get_available_remediations

class TestRemediationRegistry:
    def test_get_available_remediations(self):
        remediations = get_available_remediations()
        assert isinstance(remediations, list)
    
    def test_remediations_not_empty(self):
        remediations = get_available_remediations()
        assert len(remediations) > 0
