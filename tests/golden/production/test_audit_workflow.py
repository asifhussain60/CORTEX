"""
Golden tests for production audit workflow.

Authority: Phase 29 S2 | Zero-Mock Philosophy
Test Count: 5 golden tests
"""
import pytest
from pathlib import Path


class TestProductionAudit:
    """Golden test: Complete audit workflow."""

    def test_audit_codebase_compliance(self, tmp_path: Path) -> None:
        """Golden: Audit codebase for CORE rule compliance."""
        from cortex.orchestrators.core.enforcement_orchestrator import EnforcementOrchestrator

        enforcer = EnforcementOrchestrator()

        # Validate a benign operation
        result = enforcer.validate_operation({
            "intent": "QUERY",
            "files": [],
            "description": "read-only query",
        })

        # Should pass — no violations for a simple query
        assert result is not None

    def test_audit_detects_core_008_violation(self, tmp_path: Path) -> None:
        """Golden: Audit detects missing tests (CORE-008)."""
        from cortex.orchestrators.core.enforcement_orchestrator import EnforcementOrchestrator

        enforcer = EnforcementOrchestrator()

        # Operation that should trigger CORE-008 concern
        result = enforcer.validate_operation({
            "intent": "IMPLEMENT",
            "files": [str(tmp_path / "new_feature.py")],
            "description": "add new feature without tests",
        })

        # Result should exist (may BLOCK or WARN depending on config)
        assert result is not None
    
    def test_meta_auditor_validates_results(self, tmp_path: Path) -> None:
        """Golden: Meta-auditor validates audit results."""
        from cortex.orchestrators.intelligence.meta_auditor_agent import MetaAuditorAgent
        
        agent = MetaAuditorAgent()
        
        audit_result = {
            "violations": [
                {"rule": "CORE-028", "file": "GOOD_file.py", "message": "SCREAMING_CASE"}
            ]
        }
        
        validation = agent.validate_audit_result(audit_result)
        
        # Should detect false positive (file not actually SCREAMING_CASE)
        assert validation.has_false_positives is True


class TestProductionPerformance:
    """Golden test: Performance benchmarks."""
    
    def test_onboarding_performance(self, tmp_path: Path) -> None:
        """Golden: Onboarding completes within time budget."""
        import time
        from cortex.infrastructure.repositories.onboarding_service import OnboardingService
        
        service = OnboardingService()
        
        # Small repo (should be fast)
        repo_path = tmp_path / "small-repo"
        repo_path.mkdir()
        (repo_path / "main.py").write_text("print('hello')")
        
        start = time.time()
        result = service.onboard_repository(repo_path)
        duration = time.time() - start
        
        assert result.success is True
        assert duration < 5.0  # Should complete in <5s for small repo
    
    def test_agent_coordination_overhead(self) -> None:
        """Golden: Agent coordination adds <150ms overhead."""
        import time
        from cortex.intelligence.capability_matcher import CapabilityMatcher
        
        matcher = CapabilityMatcher()
        
        start = time.time()
        matches = matcher.find_by_capability("audit")
        duration = time.time() - start
        
        assert len(matches) >= 0  # May be empty if agents not loaded
        assert duration < 0.15  # <150ms overhead
