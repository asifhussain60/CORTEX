import pytest
from pathlib import Path
from src.infrastructure.atomic_state_manager import AtomicStateManager

class TestStateValidation:
    def setup_method(self):
        self.root_path = Path('/Users/asifhussain/PROJECTS/CORTEX')
        
    def test_validate_state_schema(self):
        manager = AtomicStateManager(self.root_path)
        is_valid = manager.validate_constraints()
        assert is_valid is not None
    
    def test_state_data_integrity(self):
        manager = AtomicStateManager(self.root_path)
        integrity = manager.check_data_integrity()
        assert isinstance(integrity, dict)
