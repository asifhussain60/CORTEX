import pytest
from src.tools.archival_executor import archive_master_plan

class TestMasterPlanArchival:
    def test_master_plan_archive_creation(self):
        config = {'source': 'master-plan.yaml', 'destination': 'archive/'}
        result = archive_master_plan(config)
        assert result['success'] is True
    
    def test_master_plan_archive_metadata(self):
        config = {'source': 'master-plan.yaml', 'destination': 'archive/'}
        result = archive_master_plan(config)
        assert 'timestamp' in result
    
    def test_master_plan_archive_path(self):
        config = {'source': 'master-plan.yaml', 'destination': 'archive/'}
        result = archive_master_plan(config)
        assert 'archive_path' in result
    
    def test_master_plan_archive_versioning(self):
        config = {'source': 'master-plan.yaml', 'destination': 'archive/'}
        result = archive_master_plan(config)
        assert 'version' in result
