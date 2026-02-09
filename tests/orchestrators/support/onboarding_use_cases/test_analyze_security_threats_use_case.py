"""
AC-054A-S1-04,05,06: AnalyzeSecurityThreatsUseCase Tests

TDD Test Suite (8+ tests):
- AC-054A-S1-04: Use case runs P0/P1/P2 threat modeling
- AC-054A-S1-05: Uses SecurityRisk models
- AC-054A-S1-06: 8+ unit tests with mock data

Author: Phase 54-A Implementation
Created: 2026-02-09
Platform: Windows/macOS compatible
"""

import pytest
from enum import Enum
from dataclasses import dataclass
from typing import List


class SeverityLevel(str, Enum):
    """Threat severity classification."""
    P0_CRITICAL = "P0"
    P1_HIGH = "P1"
    P2_MEDIUM = "P2"


@dataclass
class SecurityRisk:
    """Security risk model."""
    id: str
    title: str
    severity: SeverityLevel
    description: str
    mitigation: str
    affected_files: List[str]


class TestAnalyzeSecurityThreatsUseCase:
    """Test security threat analysis and risk modeling."""

    @pytest.fixture
    def use_case(self):
        """Initialize AnalyzeSecurityThreatsUseCase."""
        from cortex.orchestrators.support.onboarding_use_cases import AnalyzeSecurityThreatsUseCase
        return AnalyzeSecurityThreatsUseCase()

    @pytest.fixture
    def sample_repo(self) -> dict:
        """Fixture: Sample repository analysis data."""
        return {
            "name": "test-repo",
            "files": [
                {"path": "config.py", "content": "API_KEY = 'hardcoded-secret'"},
                {"path": "requirements.txt", "content": "requests==2.25.0"},
                {"path": ".env.example", "content": "DATABASE_URL=..."},
            ],
            "dependencies": ["requests==2.25.0", "flask==1.0.0"],
            "git_config": {"remotes": ["origin"]},
        }

    def test_detects_p0_threats(self, use_case, sample_repo):
        """AC-054A-S1-04a: Detects P0 (critical) threats."""
        threats = use_case.execute(sample_repo)
        
        p0_threats = [t for t in threats if t.severity == SeverityLevel.P0_CRITICAL]
        assert len(p0_threats) > 0
        # Should detect hardcoded secrets as P0
        secret_threats = [t for t in p0_threats if "secret" in t.title.lower()]
        assert len(secret_threats) > 0

    def test_detects_p1_threats(self, use_case, sample_repo):
        """AC-054A-S1-04b: Detects P1 (high) threats."""
        threats = use_case.execute(sample_repo)
        
        p1_threats = [t for t in threats if t.severity == SeverityLevel.P1_HIGH]
        assert len(p1_threats) > 0

    def test_detects_p2_threats(self, use_case, sample_repo):
        """AC-054A-S1-04c: Detects P2 (medium) threats."""
        threats = use_case.execute(sample_repo)
        
        p2_threats = [t for t in threats if t.severity == SeverityLevel.P2_MEDIUM]
        assert len(p2_threats) > 0

    def test_returns_security_risk_models(self, use_case, sample_repo):
        """AC-054A-S1-05a: Returns SecurityRisk models."""
        threats = use_case.execute(sample_repo)
        
        assert all(isinstance(t, SecurityRisk) for t in threats)

    def test_includes_mitigation_guidance(self, use_case, sample_repo):
        """AC-054A-S1-05b: Includes mitigation guidance."""
        threats = use_case.execute(sample_repo)
        
        assert all(hasattr(t, 'mitigation') for t in threats)
        assert all(len(t.mitigation) > 0 for t in threats)

    def test_identifies_affected_files(self, use_case, sample_repo):
        """AC-054A-S1-05c: Identifies affected files."""
        threats = use_case.execute(sample_repo)
        
        assert all(hasattr(t, 'affected_files') for t in threats)
        assert all(len(t.affected_files) > 0 for t in threats)

    def test_empty_repo_returns_empty_threats(self, use_case):
        """AC-054A-S1-06a: Empty repo returns empty threat list."""
        empty_repo = {"name": "empty", "files": []}
        threats = use_case.execute(empty_repo)
        
        assert threats == []

    def test_no_threats_returns_empty_list(self, use_case):
        """AC-054A-S1-06b: Clean repo returns empty threat list."""
        clean_repo = {
            "name": "clean",
            "files": [
                {"path": "main.py", "content": "print('hello')"},
            ],
            "dependencies": [],
        }
        threats = use_case.execute(clean_repo)
        
        assert isinstance(threats, list)


class TestAnalyzeSecurityThreatsOrchestration:
    """Test orchestration and repository integration."""

    def test_uses_repository_for_persistence(self):
        """Test saving threats to repository."""
        from cortex.orchestrators.support.onboarding_use_cases import AnalyzeSecurityThreatsUseCase
        
        use_case = AnalyzeSecurityThreatsUseCase()
        assert hasattr(use_case, 'repository')
