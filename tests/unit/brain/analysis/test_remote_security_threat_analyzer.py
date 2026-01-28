"""
Unit tests for RemoteSecurityThreatAnalyzer (Phase 8.5).

Tests remote GitHub analysis capabilities.

AC-ID: AC-SECURITY-FRAMEWORK-001 (Phase 8.5)
Authority: CORE-008 (TDD), CORE-011, CORE-012
"""

import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from cortex.brain.analysis.remote_security_threat_analyzer import (
    RemoteSecurityThreatAnalyzer,
    RemoteSecurityAnalysisResult,
    get_remote_security_threat_analyzer,
)


class TestRemoteSecurityThreatAnalyzer(unittest.TestCase):
    """Test RemoteSecurityThreatAnalyzer."""

    def setUp(self) -> None:
        """Initialize analyzer before each test."""
        with patch('cortex.brain.analysis.remote_security_threat_analyzer.RemoteGitAdapter'):
            self.analyzer = RemoteSecurityThreatAnalyzer()

    def test_remote_analyzer_initializes(self) -> None:
        """Test RemoteSecurityThreatAnalyzer initialization."""
        self.assertIsNotNone(self.analyzer)
        self.assertIsNotNone(self.analyzer.remote_adapter)

    @patch('cortex.brain.analysis.remote_security_threat_analyzer.RemoteGitAdapter')
    def test_analyze_remote_file_returns_result(self, mock_adapter_class) -> None:
        """Test analyzing a remote file."""
        # Mock the adapter
        mock_adapter = MagicMock()
        mock_adapter_class.return_value = mock_adapter
        
        # Mock remote file
        mock_file = MagicMock()
        mock_file.content = "eval(user_input)"  # Threat code
        mock_file.commit_hash = "abc123def456"
        mock_file.author = "developer@example.com"
        mock_file.last_modified = "2026-01-28"
        
        mock_adapter.get_file.return_value = mock_file
        mock_adapter.get_blame.return_value = {}
        
        # Create analyzer with mocked adapter
        analyzer = RemoteSecurityThreatAnalyzer()
        analyzer.remote_adapter = mock_adapter
        
        # Analyze
        result = analyzer.analyze_remote_file(
            repo="test-org/test-repo",
            file_path="src/handlers.py",
            branch="main"
        )
        
        # Verify
        self.assertIsInstance(result, RemoteSecurityAnalysisResult)
        self.assertEqual(result.github_repo, "test-org/test-repo")
        self.assertEqual(result.github_branch, "main")

    def test_risk_score_calculation(self) -> None:
        """Test risk score calculation."""
        # Create mock threats
        from cortex.brain.analysis.security_threat_analyzer import (
            ThreatFinding,
            ThreatSeverity,
        )
        
        threats = [
            ThreatFinding(
                cwe_id="CWE-94",
                severity=ThreatSeverity.CRITICAL,
                line_number=10,
                pattern_name="eval_usage",
                description="Code injection",
                recommendation="Use ast.literal_eval",
                file_path="test.py",
                code_snippet="eval(user_input)",
            ),
        ]
        
        risk_score = self.analyzer._calculate_risk_score(threats)
        
        # CRITICAL threat should give high risk
        self.assertGreater(risk_score, 8.0)
        self.assertLessEqual(risk_score, 10.0)

    def test_risk_score_empty_threats(self) -> None:
        """Test risk score with no threats."""
        risk_score = self.analyzer._calculate_risk_score([])
        self.assertEqual(risk_score, 0.0)

    def test_remote_file_url_generation(self) -> None:
        """Test GitHub URL generation."""
        with patch('cortex.brain.analysis.remote_security_threat_analyzer.RemoteGitAdapter'):
            analyzer = RemoteSecurityThreatAnalyzer()
            
            # Mock remote file
            mock_file = MagicMock()
            mock_file.content = "x = 1"  # Safe code
            mock_file.commit_hash = "abc123"
            mock_file.author = "dev"
            mock_file.last_modified = "2026-01-28"
            
            analyzer.remote_adapter.get_file.return_value = mock_file
            analyzer.remote_adapter.get_blame.return_value = {}
            
            result = analyzer.analyze_remote_file(
                repo="cortex-ai/cortex",
                file_path="cortex/brain/analysis.py",
                branch="main"
            )
            
            expected_url = "https://github.com/cortex-ai/cortex/blob/main/cortex/brain/analysis.py"
            self.assertEqual(result.remote_file_url, expected_url)


class TestRemoteSecurityAnalysisResult(unittest.TestCase):
    """Test RemoteSecurityAnalysisResult dataclass."""

    def test_result_creation(self) -> None:
        """Test creating a result."""
        result = RemoteSecurityAnalysisResult(
            success=True,
            threat_findings=[],
            github_repo="test/repo",
            github_branch="develop",
            remote_file_url="https://github.com/test/repo/blob/develop/file.py",
            commit_hash="abc123",
            file_author="author@example.com",
            risk_score=7.5,
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.github_repo, "test/repo")
        self.assertEqual(result.risk_score, 7.5)

    def test_result_has_remote_fields(self) -> None:
        """Test that result has remote-specific fields."""
        result = RemoteSecurityAnalysisResult(
            success=True,
            threat_findings=[],
        )
        
        self.assertTrue(hasattr(result, 'github_repo'))
        self.assertTrue(hasattr(result, 'github_branch'))
        self.assertTrue(hasattr(result, 'remote_file_url'))
        self.assertTrue(hasattr(result, 'commit_hash'))
        self.assertTrue(hasattr(result, 'file_author'))
        self.assertTrue(hasattr(result, 'last_modified'))
        self.assertTrue(hasattr(result, 'risk_score'))


class TestRemoteSecurityThreatAnalyzerFactory(unittest.TestCase):
    """Test factory function."""

    @patch('cortex.brain.analysis.remote_security_threat_analyzer.RemoteGitAdapter')
    def test_factory_returns_instance(self, mock_adapter_class) -> None:
        """Test factory returns RemoteSecurityThreatAnalyzer."""
        analyzer = get_remote_security_threat_analyzer()
        
        self.assertIsInstance(analyzer, RemoteSecurityThreatAnalyzer)

    @patch('cortex.brain.analysis.remote_security_threat_analyzer.RemoteGitAdapter')
    def test_factory_with_github_token(self, mock_adapter_class) -> None:
        """Test factory with GitHub token."""
        token = "gh_test_token_123"
        analyzer = get_remote_security_threat_analyzer(github_token=token)
        
        self.assertIsInstance(analyzer, RemoteSecurityThreatAnalyzer)
        # Verify token was passed to adapter
        mock_adapter_class.assert_called_with(github_token=token)


if __name__ == "__main__":
    unittest.main()
