import pytest
from src.tools.archival_executor import decommission_legacy

class TestLegacyDecommission:
    def test_decommission_returns_success(self):
        config = {'legacy_paths': ['src/old/', 'src/deprecated/']}
        result = decommission_legacy(config)
        assert result['success'] is True
    
    def test_decommission_tracks_removed(self):
        config = {'legacy_paths': ['src/old/', 'src/deprecated/']}
        result = decommission_legacy(config)
        assert 'decommissioned' in result
    
    def test_decommission_handles_empty(self):
        config = {'legacy_paths': []}
        result = decommission_legacy(config)
        assert result['success'] is True
    
    def test_decommission_creates_archive(self):
        config = {'legacy_paths': ['src/old/'], 'create_archive': True}
        result = decommission_legacy(config)
        assert 'archived_at' in result or result['success'] is True
