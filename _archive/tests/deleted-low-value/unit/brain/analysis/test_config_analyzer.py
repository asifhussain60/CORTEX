"""
Unit tests for ConfigAnalyzer (LENS v2.0).

Tests configuration analysis, secret detection, and security assessment.

AC-ID: AC-LENS-V2-CONFIG-001
Authority: CORE-008 (TDD), CORE-011, CORE-012
"""

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from cortex.lens.analyzers.config_analyzer import (
    ConfigAnalyzer,
    ConfigFinding,
    ConfigSeverity,
    ConfigCategory,
    ConfigAnalysisResult,
    get_config_analyzer,
)


class TestConfigAnalyzer(unittest.TestCase):
    """Test suite for ConfigAnalyzer."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.analyzer = ConfigAnalyzer()
        self.temp_dir = TemporaryDirectory()
        self.test_path = Path(self.temp_dir.name)
    
    def tearDown(self):
        """Clean up test fixtures."""
        self.temp_dir.cleanup()
    
    def test_detects_aws_access_key(self):
        """P0: Should detect hardcoded AWS access key."""
        config_content = """
        aws:
          access_key_id: AKIAIOSFODNN7EXAMPLE
          region: us-west-2
        """
        
        config_file = self.test_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = self.analyzer.analyze_file(config_file)
        
        self.assertTrue(result.success)
        p0_findings = [f for f in result.findings if f.severity == ConfigSeverity.P0]
        self.assertGreater(len(p0_findings), 0)
        self.assertIn("AWS", p0_findings[0].description)
    
    def test_detects_aws_secret_key(self):
        """P0: Should detect hardcoded AWS secret key."""
        config_content = """
        aws:
          secret_access_key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
        """
        
        config_file = self.test_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = self.analyzer.analyze_file(config_file)
        
        p0_findings = [f for f in result.findings if f.severity == ConfigSeverity.P0]
        self.assertGreater(len(p0_findings), 0)
    
    def test_detects_api_key(self):
        """P0: Should detect hardcoded API key."""
        config_content = """
        api:
          api_key: test_key_1234567890abcdefghijklmnop
        """
        
        config_file = self.test_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = self.analyzer.analyze_file(config_file)
        
        p0_findings = [f for f in result.findings if f.severity == ConfigSeverity.P0]
        self.assertGreater(len(p0_findings), 0)
        self.assertEqual(p0_findings[0].category, ConfigCategory.SECRET_EXPOSURE)
    
    def test_detects_password(self):
        """P0: Should detect hardcoded password."""
        config_content = """
        database:
          password: MySecretPassword123!
        """
        
        config_file = self.test_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = self.analyzer.analyze_file(config_file)
        
        p0_findings = [f for f in result.findings if f.severity == ConfigSeverity.P0]
        self.assertGreater(len(p0_findings), 0)
    
    def test_detects_private_key(self):
        """P0: Should detect embedded private key."""
        config_content = """
        ssh:
          key: |
            -----BEGIN RSA PRIVATE KEY-----
            MIIEpAIBAAKCAQEA...
            -----END RSA PRIVATE KEY-----
        """
        
        config_file = self.test_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = self.analyzer.analyze_file(config_file)
        
        p0_findings = [f for f in result.findings if f.severity == ConfigSeverity.P0]
        self.assertGreater(len(p0_findings), 0)
    
    def test_detects_jwt_secret(self):
        """P0: Should detect hardcoded JWT secret."""
        config_content = """
        jwt:
          secret_key: my-super-secret-jwt-key-123
        """
        
        config_file = self.test_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = self.analyzer.analyze_file(config_file)
        
        p0_findings = [f for f in result.findings if f.severity == ConfigSeverity.P0]
        self.assertGreater(len(p0_findings), 0)
    
    def test_detects_debug_enabled(self):
        """P1: Should detect debug mode enabled."""
        config_content = """
        app:
          debug: true
        """
        
        config_file = self.test_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = self.analyzer.analyze_file(config_file)
        
        p1_findings = [f for f in result.findings if f.severity == ConfigSeverity.P1]
        self.assertGreater(len(p1_findings), 0)
        self.assertEqual(p1_findings[0].category, ConfigCategory.INSECURE_DEFAULT)
    
    def test_detects_ssl_disabled(self):
        """P1: Should detect SSL verification disabled."""
        config_content = """
        http:
          ssl_verify: false
        """
        
        config_file = self.test_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = self.analyzer.analyze_file(config_file)
        
        p1_findings = [f for f in result.findings if f.severity == ConfigSeverity.P1]
        self.assertGreater(len(p1_findings), 0)
    
    def test_detects_weak_encryption(self):
        """P1: Should detect weak encryption algorithms."""
        config_content = """
        encryption:
          algorithm: md5
        """
        
        config_file = self.test_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = self.analyzer.analyze_file(config_file)
        
        p1_findings = [f for f in result.findings if f.severity == ConfigSeverity.P1]
        self.assertGreater(len(p1_findings), 0)
    
    def test_detects_insecure_cors(self):
        """P1: Should detect CORS allowing all origins."""
        config_content = """
        cors:
          allowed_origins: "*"
        """
        
        config_file = self.test_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = self.analyzer.analyze_file(config_file)
        
        p1_findings = [f for f in result.findings if f.severity == ConfigSeverity.P1]
        self.assertGreater(len(p1_findings), 0)
    
    def test_detects_no_auth(self):
        """P1: Should detect authentication disabled."""
        config_content = """
        api:
          authentication: false
        """
        
        config_file = self.test_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = self.analyzer.analyze_file(config_file)
        
        p1_findings = [f for f in result.findings if f.severity == ConfigSeverity.P1]
        self.assertGreater(len(p1_findings), 0)
    
    def test_analyze_repository(self):
        """Should analyze all config files in repository."""
        # Create multiple config files
        (self.test_path / "config.yaml").write_text("api_key: test123456789012345")
        (self.test_path / "settings.json").write_text('{"password": "secret123"}')
        (self.test_path / "test").mkdir()
        (self.test_path / "test" / "config.yaml").write_text("debug: true")
        
        result = self.analyzer.analyze_repository(self.test_path)
        
        self.assertGreater(result["analyzed_files"], 0)
        self.assertGreater(result["total_findings"], 0)
        self.assertIn("p0_findings", result)
        self.assertIn("p1_findings", result)
    
    def test_skips_test_files(self):
        """Should skip test files when analyzing repository."""
        (self.test_path / "test_config.yaml").write_text("api_key: test123456789012345")
        
        result = self.analyzer.analyze_repository(self.test_path)
        
        # Should skip test files
        self.assertEqual(result["analyzed_files"], 0)
    
    def test_skips_node_modules(self):
        """Should skip node_modules directory."""
        node_modules = self.test_path / "node_modules"
        node_modules.mkdir()
        (node_modules / "config.yaml").write_text("api_key: test123456789012345")
        
        result = self.analyzer.analyze_repository(self.test_path)
        
        # Should skip node_modules
        self.assertEqual(result["analyzed_files"], 0)
    
    def test_clean_config_passes(self):
        """Should not flag clean configuration."""
        config_content = """
        app:
          name: my-app
          port: 8000
        """
        
        config_file = self.test_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = self.analyzer.analyze_file(config_file)
        
        self.assertTrue(result.success)
        self.assertEqual(len(result.findings), 0)
    
    def test_detects_config_type(self):
        """Should correctly detect config file type."""
        yaml_file = self.test_path / "config.yaml"
        yaml_file.write_text("key: value")
        
        json_file = self.test_path / "config.json"
        json_file.write_text('{"key": "value"}')
        
        yaml_result = self.analyzer.analyze_file(yaml_file)
        json_result = self.analyzer.analyze_file(json_file)
        
        self.assertEqual(yaml_result.config_type, "yaml")
        self.assertEqual(json_result.config_type, "json")
    
    def test_file_not_found_error(self):
        """Should handle file not found gracefully."""
        result = self.analyzer.analyze_file(Path("/nonexistent/file.yaml"))
        
        self.assertFalse(result.success)
        self.assertIn("not found", result.error.lower())
    
    def test_line_number_tracking(self):
        """Should track line numbers for findings."""
        config_content = """line 1
line 2
api_key: secret123456789012345
line 4"""
        
        config_file = self.test_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = self.analyzer.analyze_file(config_file)
        
        self.assertGreater(len(result.findings), 0)
        self.assertEqual(result.findings[0].line_number, 3)
    
    def test_includes_recommendations(self):
        """Should include remediation recommendations."""
        config_content = "password: MyPassword123"
        
        config_file = self.test_path / "config.yaml"
        config_file.write_text(config_content)
        
        result = self.analyzer.analyze_file(config_file)
        
        self.assertGreater(len(result.findings), 0)
        self.assertTrue(len(result.findings[0].recommendation) > 0)
        self.assertIn("secret management", result.findings[0].recommendation.lower())


class TestConfigFinding(unittest.TestCase):
    """Test ConfigFinding dataclass."""
    
    def test_finding_creation(self):
        """Should create ConfigFinding with all attributes."""
        finding = ConfigFinding(
            file_path="/path/to/file.yaml",
            line_number=10,
            severity=ConfigSeverity.P0,
            category=ConfigCategory.SECRET_EXPOSURE,
            description="Test finding",
            recommendation="Fix it",
            pattern_matched="test_pattern",
            context={"key": "value"}
        )
        
        self.assertEqual(finding.file_path, "/path/to/file.yaml")
        self.assertEqual(finding.line_number, 10)
        self.assertEqual(finding.severity, ConfigSeverity.P0)
        self.assertEqual(finding.category, ConfigCategory.SECRET_EXPOSURE)
        self.assertEqual(finding.description, "Test finding")
        self.assertEqual(finding.recommendation, "Fix it")
        self.assertEqual(finding.pattern_matched, "test_pattern")
        self.assertEqual(finding.context["key"], "value")


class TestConfigAnalyzerSingleton(unittest.TestCase):
    """Test get_config_analyzer singleton."""
    
    def test_returns_singleton(self):
        """Should return same instance on multiple calls."""
        analyzer1 = get_config_analyzer()
        analyzer2 = get_config_analyzer()
        
        self.assertIs(analyzer1, analyzer2)
    
    def test_returns_config_analyzer_instance(self):
        """Should return ConfigAnalyzer instance."""
        analyzer = get_config_analyzer()
        
        self.assertIsInstance(analyzer, ConfigAnalyzer)


if __name__ == "__main__":
    unittest.main()
