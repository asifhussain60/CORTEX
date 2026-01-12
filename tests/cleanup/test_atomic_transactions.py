import pytest
from pathlib import Path
from src.orchestrators.core.state_synchronizer import StateSynchronizer

class TestAtomicTransactions:
    def setup_method(self):
        self.root_path = Path('/Users/asifhussain/PROJECTS/CORTEX')
        
    def test_begin_transaction(self):
        sync = StateSynchronizer(self.root_path)
        result = sync.begin_transaction()
        assert result is not None
    
    def test_commit_transaction(self):
        sync = StateSynchronizer(self.root_path)
        sync.begin_transaction()
        result = sync.commit()
        assert result is not None
    
    def test_rollback_on_error(self):
        sync = StateSynchronizer(self.root_path)
        sync.begin_transaction()
        result = sync.rollback()
        assert result is not None
