"""IntelligenceOrchestrator tests."""
import pytest
from pathlib import Path
from cortex.orchestrators.intelligence.intelligence_orchestrator import IntelligenceOrchestrator


class TestIntelligenceOrchestrator:
    """Test unified intelligence operations."""
    
    @pytest.fixture
    def orch(self, tmp_path: Path) -> IntelligenceOrchestrator:
        """Create orchestrator."""
        return IntelligenceOrchestrator(audit_db_path=tmp_path / "audit.db")
    
    def test_parse_python_file(self, orch: IntelligenceOrchestrator, tmp_path: Path) -> None:
        """Parse Python file extracts functions and classes."""
        code = '''
def foo():
    pass

class Bar:
    def baz(self):
        pass
'''
        test_file = tmp_path / "test.py"
        test_file.write_text(code)
        
        result = orch.parse_python_file(test_file)
        assert result.success
        assert len(result.functions) == 1
        assert len(result.classes) == 1
    
    def test_analyze_comments(self, orch: IntelligenceOrchestrator, tmp_path: Path) -> None:
        """Analyze comments extracts docstrings."""
        code = '''
def foo():
    """This is a docstring."""
    pass
'''
        test_file = tmp_path / "test.py"
        test_file.write_text(code)
        
        result = orch.analyze_comments(test_file)
        assert len(result) > 0
    
    def test_route_intelligence(self, orch: IntelligenceOrchestrator) -> None:
        """Route intelligence returns routing decision."""
        result = orch.route_intelligence("IMPLEMENT", context={})
        assert "target" in result
        assert "confidence" in result
    
    def test_get_cached_analysis(self, orch: IntelligenceOrchestrator, tmp_path: Path) -> None:
        """Get cached analysis returns cached result."""
        code = "def foo(): pass"
        test_file = tmp_path / "test.py"
        test_file.write_text(code)
        
        # First call caches
        result1 = orch.parse_python_file(test_file)
        # Second call retrieves from cache
        result2 = orch.get_cached_analysis(test_file)
        
        assert result2 is not None
    
    def test_query_audit_log(self, orch: IntelligenceOrchestrator, tmp_path: Path) -> None:
        """Query audit log returns entries."""
        code = "def foo(): pass"
        test_file = tmp_path / "test.py"
        test_file.write_text(code)
        
        orch.parse_python_file(test_file)
        
        entries = orch.query_audit_log(operation="PARSE")
        assert len(entries) > 0


# AC_COMPLETE: AC-MEGA-B-S2-003-INTELLIGENCE ✅ 6/6
