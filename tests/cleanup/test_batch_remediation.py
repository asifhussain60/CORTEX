import pytest
from src.tools.remediation_executor import apply_batch_remediation

class TestBatchRemediation:
    def test_apply_batch_remediation(self):
        remediations = [{'type': 'state_fix'}, {'type': 'audit_fix'}]
        result = apply_batch_remediation(remediations)
        assert isinstance(result, dict)
    
    def test_batch_remediation_tracking(self):
        remediations = [{'type': 'state_fix'}]
        result = apply_batch_remediation(remediations)
        assert 'success' in result or 'applied' in result
