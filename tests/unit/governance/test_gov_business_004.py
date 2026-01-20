"""Test for BDOM-004: Scope Creep Prevention"""
import pytest
from cortex.core.governance.scope_creep import (
    ScopeManager,
    ScopeItem,
    ScopeStatus,
)

class TestScopeCreep:
    def test_define_scope(self):
        manager = ScopeManager()
        items = [ScopeItem("Feature1", 10), ScopeItem("Feature2", 20)]
        manager.define_scope(items)
        assert len(manager.current_scope) == 2
    
    def test_within_scope(self):
        manager = ScopeManager()
        item = ScopeItem("Feature1", 10)
        manager.define_scope([item])
        status = manager.add_item(item)
        assert status == ScopeStatus.WITHIN_SCOPE
    
    def test_scope_creep(self):
        manager = ScopeManager()
        manager.define_scope([ScopeItem("Feature1", 10)])
        status = manager.add_item(ScopeItem("Feature2", 20))
        assert status == ScopeStatus.CREEPING
    
    def test_creep_percentage(self):
        manager = ScopeManager()
        manager.define_scope([ScopeItem("F1", 10)])
        manager.add_item(ScopeItem("F2", 20))
        assert manager.get_creep_percentage() == 100.0
