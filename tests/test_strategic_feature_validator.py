import pytest

from src.operations.modules.healthcheck.strategic_feature_validator import StrategicFeatureValidator


def test_all_validators_return_standard_format():
    v = StrategicFeatureValidator()
    results = {
        'architecture_intelligence': v.validate_architecture_intelligence(),
        'rollback_system': v.validate_rollback_system(),
        'swagger_dor': v.validate_swagger_dor(),
        'ux_enhancement': v.validate_ux_enhancement(),
        'ado_agent': v.validate_ado_agent(),
    }
    for name, res in results.items():
        assert isinstance(res, dict), f"{name} should return a dict"
        assert 'status' in res and 'details' in res and 'issues' in res, f"{name} format incorrect"
        assert res['status'] in {'healthy', 'warning', 'critical', 'error'}
        assert isinstance(res['issues'], list)
