"""SOLIDOrchestrator tests."""
import pytest
from pathlib import Path
from cortex.orchestrators.validation.solid_orchestrator import SOLIDOrchestrator


class TestSOLIDOrchestrator:
    """Test unified SOLID analysis."""
    
    @pytest.fixture
    def orch(self, tmp_path: Path) -> SOLIDOrchestrator:
        return SOLIDOrchestrator(audit_db_path=tmp_path / "audit.db")
    
    def test_analyze_srp(self, orch: SOLIDOrchestrator, tmp_path: Path) -> None:
        """Analyze SRP violations."""
        code = '''
class GodClass:
    def method1(self): pass
    def method2(self): pass
'''
        test_file = tmp_path / "test.py"
        test_file.write_text(code)
        
        violations = orch.analyze_srp(test_file)
        assert isinstance(violations, list)
    
    def test_analyze_all(self, orch: SOLIDOrchestrator, tmp_path: Path) -> None:
        """Analyze all SOLID principles."""
        code = "class Test: pass"
        test_file = tmp_path / "test.py"
        test_file.write_text(code)
        
        result = orch.analyze_all(test_file)
        assert "srp" in result
        assert "ocp" in result
        assert "isp" in result
        assert "dip" in result
        assert "dry" in result
    
    def test_get_summary(self, orch: SOLIDOrchestrator, tmp_path: Path) -> None:
        """Get analysis summary."""
        code = "def foo(): pass"
        test_file = tmp_path / "test.py"
        test_file.write_text(code)
        
        orch.analyze_all(test_file)
        summary = orch.get_summary()
        
        assert "total_violations" in summary
        assert "by_type" in summary


# AC_COMPLETE: AC-MEGA-B-S2-004-SOLID ✅ 3/3
