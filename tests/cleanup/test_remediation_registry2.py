import pytest
from src.tools.remediation_executor import get_remediation_registry

class TestRemediationRegistry:
    def test_get_remediation_registry(self):
        registry = get_remediation_registry()
        assert isinstance(registry, dict)
    
    def test_registry_has_entries(self):
        registry = get_remediation_registry()
        assert len(registry) > 0 or 'remediations' in registry
