"""
Unit tests for SecurityThreatAnalyzer (Phase 8.2).

Tests CWE detection, threat severity scoring, and context-aware risk assessment.

AC-ID: AC-SECURITY-FRAMEWORK-001
Authority: CORE-008 (TDD), CORE-011, CORE-012
"""

import unittest
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass

from cortex.brain.analysis.security_threat_analyzer import (
    SecurityThreatAnalyzer,
    ThreatFinding,
    ThreatSeverity,
    SecurityAnalysisResult,
)


class TestSecurityThreatAnalyzer(unittest.TestCase):
    """Test suite for SecurityThreatAnalyzer."""

    def setUp(self) -> None:
        """Initialize analyzer before each test."""
        self.analyzer = SecurityThreatAnalyzer()
        self.test_dir = Path(__file__).parent / "fixtures"
        self.test_dir.mkdir(exist_ok=True)

    def test_detect_code_injection_cwe94(self) -> None:
        """Test detection of Code Injection (CWE-94: exec/eval)."""
        code = """
import pickle

user_data = request.get_json()
result = eval(user_data['expression'])  # CWE-94
"""
        result = self.analyzer.analyze_code(code, "user_handler.py")
        
        self.assertTrue(result.success)
        self.assertGreaterEqual(len(result.threat_findings), 1)
        
        threat = next((t for t in result.threat_findings if "eval" in t.pattern_name), None)
        self.assertIsNotNone(threat)
        self.assertEqual(threat.cwe_id, "CWE-94")
        self.assertEqual(threat.severity, ThreatSeverity.CRITICAL)

    def test_detect_deserialization_cwe95(self) -> None:
        """Test detection of Deserialization (CWE-95: pickle/marshal)."""
        code = """
import pickle

data = request.get_bytes()
obj = pickle.loads(data)  # CWE-95
"""
        result = self.analyzer.analyze_code(code, "deserialization.py")
        
        self.assertTrue(result.success)
        threat = next((t for t in result.threat_findings if t.cwe_id == "CWE-95"), None)
        self.assertIsNotNone(threat)
        self.assertIn(threat.severity, [ThreatSeverity.HIGH, ThreatSeverity.CRITICAL])

    def test_detect_command_injection_cwe78(self) -> None:
        """Test detection of Command Injection (CWE-78: os.system with user input)."""
        code = """
import os

user_input = request.args.get('cmd')
os.system(f"ls {user_input}")  # CWE-78
"""
        result = self.analyzer.analyze_code(code, "command_handler.py")
        
        self.assertTrue(result.success)
        threat = next((t for t in result.threat_findings if t.cwe_id == "CWE-78"), None)
        self.assertIsNotNone(threat)
        self.assertEqual(threat.severity, ThreatSeverity.CRITICAL)

    def test_detect_sql_injection_cwe89(self) -> None:
        """Test detection of SQL Injection (CWE-89: string concatenation in SQL)."""
        code = """
query = f"SELECT * FROM users WHERE id = {user_id}"  # CWE-89
db.execute(query)
"""
        result = self.analyzer.analyze_code(code, "database.py")
        
        self.assertTrue(result.success)
        threat = next((t for t in result.threat_findings if t.cwe_id == "CWE-89"), None)
        self.assertIsNotNone(threat)
        self.assertGreaterEqual(threat.severity, ThreatSeverity.HIGH)

    def test_detect_weak_crypto_cwe327(self) -> None:
        """Test detection of Weak Cryptography (CWE-327: MD5, DES)."""
        code = """
import hashlib

password_hash = hashlib.md5(password.encode()).hexdigest()  # CWE-327
"""
        result = self.analyzer.analyze_code(code, "auth.py")
        
        self.assertTrue(result.success)
        threat = next((t for t in result.threat_findings if t.cwe_id == "CWE-327"), None)
        self.assertIsNotNone(threat)
        self.assertGreaterEqual(threat.severity, ThreatSeverity.MEDIUM)

    def test_detect_path_traversal_cwe22(self) -> None:
        """Test detection of Path Traversal (CWE-22: ../ in file paths)."""
        code = """
filepath = request.args.get('file')
with open(f"/files/{filepath}") as f:  # CWE-22 if filepath contains ../
    return f.read()
"""
        result = self.analyzer.analyze_code(code, "file_handler.py")
        
        self.assertTrue(result.success)
        # Should detect unsafe file operations with user input
        threats = result.threat_findings
        self.assertTrue(any(t.severity >= ThreatSeverity.HIGH for t in threats))

    def test_severity_scoring(self) -> None:
        """Test threat severity scoring."""
        # CRITICAL threat
        critical_code = "eval(user_input)"
        result = self.analyzer.analyze_code(critical_code, "test.py")
        threats = [t for t in result.threat_findings if t.cwe_id == "CWE-94"]
        self.assertTrue(any(t.severity == ThreatSeverity.CRITICAL for t in threats))

    def test_line_number_accuracy(self) -> None:
        """Test that line numbers are accurately reported."""
        code = """
import os

# Line 4
user_input = request.args.get('cmd')
os.system(f"ls {user_input}")  # Line 6 - should report this
"""
        result = self.analyzer.analyze_code(code, "test.py")
        
        threat = next((t for t in result.threat_findings if t.cwe_id == "CWE-78"), None)
        if threat:
            self.assertEqual(threat.line_number, 6)

    def test_multiple_threats_in_single_file(self) -> None:
        """Test detection of multiple different threats."""
        code = """
import os
import pickle

os.system(f"ls {user_input}")  # CWE-78
data = pickle.loads(request.data)  # CWE-95
result = eval(expression)  # CWE-94
"""
        result = self.analyzer.analyze_code(code, "multi_threat.py")
        
        self.assertTrue(result.success)
        cwe_ids = {t.cwe_id for t in result.threat_findings}
        self.assertIn("CWE-78", cwe_ids)
        self.assertIn("CWE-95", cwe_ids)
        self.assertIn("CWE-94", cwe_ids)

    def test_safe_code_no_threats(self) -> None:
        """Test that safe code produces no threats."""
        code = """
def safe_operation(user_id: int) -> dict:
    '''Safe operation using parameterized query.'''
    query = "SELECT * FROM users WHERE id = ?"
    result = db.execute(query, (user_id,))
    return result
"""
        result = self.analyzer.analyze_code(code, "safe.py")
        
        self.assertTrue(result.success)
        # Should have minimal or no threats
        critical_threats = [t for t in result.threat_findings 
                          if t.severity == ThreatSeverity.CRITICAL]
        self.assertEqual(len(critical_threats), 0)

    def test_threat_finding_attributes(self) -> None:
        """Test ThreatFinding dataclass has required attributes."""
        code = "eval(user_input)"
        result = self.analyzer.analyze_code(code, "test.py")
        
        if result.threat_findings:
            threat = result.threat_findings[0]
            self.assertTrue(hasattr(threat, 'cwe_id'))
            self.assertTrue(hasattr(threat, 'severity'))
            self.assertTrue(hasattr(threat, 'line_number'))
            self.assertTrue(hasattr(threat, 'pattern_name'))
            self.assertTrue(hasattr(threat, 'description'))
            self.assertTrue(hasattr(threat, 'recommendation'))

    def test_analyze_result_includes_metadata(self) -> None:
        """Test SecurityAnalysisResult includes analysis metadata."""
        code = "x = 1"
        result = self.analyzer.analyze_code(code, "test.py")
        
        self.assertTrue(result.success)
        self.assertIsNotNone(result.analysis_time_ms)
        self.assertIsNotNone(result.file_path)
        self.assertIsNotNone(result.patterns_checked)
        self.assertGreater(result.patterns_checked, 0)

    def test_empty_code_handling(self) -> None:
        """Test handling of empty code."""
        result = self.analyzer.analyze_code("", "empty.py")
        
        self.assertTrue(result.success)
        self.assertEqual(len(result.threat_findings), 0)

    def test_syntax_error_handling(self) -> None:
        """Test graceful handling of code with syntax errors."""
        invalid_code = "def broken syntax here"
        result = self.analyzer.analyze_code(invalid_code, "broken.py")
        
        # Should not crash, should log error
        self.assertFalse(result.success)
        self.assertIsNotNone(result.error)


class TestThreatFinding(unittest.TestCase):
    """Test ThreatFinding dataclass."""

    def test_threat_finding_creation(self) -> None:
        """Test creating a ThreatFinding."""
        finding = ThreatFinding(
            cwe_id="CWE-94",
            severity=ThreatSeverity.CRITICAL,
            line_number=42,
            pattern_name="eval_usage",
            description="Code injection via eval()",
            recommendation="Use safe_eval or ast.literal_eval",
            file_path="test.py",
            code_snippet="eval(user_input)",
        )
        
        self.assertEqual(finding.cwe_id, "CWE-94")
        self.assertEqual(finding.severity, ThreatSeverity.CRITICAL)
        self.assertEqual(finding.line_number, 42)

    def test_threat_severity_ordering(self) -> None:
        """Test threat severity enum ordering."""
        self.assertGreater(ThreatSeverity.CRITICAL.value, ThreatSeverity.HIGH.value)
        self.assertGreater(ThreatSeverity.HIGH.value, ThreatSeverity.MEDIUM.value)
        self.assertGreater(ThreatSeverity.MEDIUM.value, ThreatSeverity.LOW.value)


if __name__ == "__main__":
    unittest.main()
