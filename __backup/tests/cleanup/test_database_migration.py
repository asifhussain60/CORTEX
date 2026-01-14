import pytest
from pathlib import Path
from src.database.planning_state_db import PlanningStateDB

class TestDatabaseMigration:
    def setup_method(self):
        self.db_path = '/tmp/test_planning_state.db'
        
    def test_get_migration_status(self):
        db = PlanningStateDB(self.db_path)
        status = db.get_migration_status()
        assert isinstance(status, dict)
    
    def test_query_legacy_phase(self):
        db = PlanningStateDB(self.db_path)
        result = db.query_legacy_phase('phase_1')
        assert isinstance(result, dict)
