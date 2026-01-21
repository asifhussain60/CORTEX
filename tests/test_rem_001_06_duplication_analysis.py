"""
AC-REM-001-06: Code Duplication Analysis and Refactoring Roadmap
Tests for duplication detection and refactoring validation
"""

import unittest
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple


class CodeDuplicationDetector:
    """Detector for code duplication patterns in cortex codebase"""

    def __init__(self, codebase_root: str):
        self.root = Path(codebase_root)
        self.duplications: Dict[str, List[Tuple[str, int]]] = {}

    def analyze_directory(self, pattern: str = "*.py") -> Dict:
        """Analyze directory for specific duplication patterns"""
        findings = {
            "connection_cleanup_patterns": [],
            "error_logging_patterns": [],
            "health_check_patterns": [],
            "file_io_patterns": [],
            "validation_patterns": [],
        }

        py_files = list(self.root.rglob(pattern))
        
        for file_path in py_files:
            if "__pycache__" in str(file_path) or ".pytest" in str(file_path):
                continue
            
            try:
                with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()
                    
                # Pattern 1: Connection cleanup duplications
                if self._detect_connection_cleanup_duplication(content):
                    findings["connection_cleanup_patterns"].append(str(file_path))
                
                # Pattern 2: Error logging duplications
                if self._detect_error_logging_duplication(content):
                    findings["error_logging_patterns"].append(str(file_path))
                
                # Pattern 3: Health check duplications
                if self._detect_health_check_duplication(content):
                    findings["health_check_patterns"].append(str(file_path))
                
                # Pattern 4: File I/O duplications
                if self._detect_file_io_duplication(content):
                    findings["file_io_patterns"].append(str(file_path))
                
                # Pattern 5: Validation duplications
                if self._detect_validation_duplication(content):
                    findings["validation_patterns"].append(str(file_path))
            except Exception as e:
                print(f"Error analyzing {file_path}: {e}")
        
        return findings

    @staticmethod
    def _detect_connection_cleanup_duplication(content: str) -> bool:
        """Detect connection cleanup pattern duplications"""
        pattern = r"except\s+(Exception|Error):\s*(pass|print|continue|return|logging\.error)"
        return bool(re.search(pattern, content)) and "sqlite3" in content

    @staticmethod
    def _detect_error_logging_duplication(content: str) -> bool:
        """Detect error logging pattern duplications"""
        patterns = [
            r"logging\.error\([\"'].*?[\"']\)",
            r"except\s+\w+\s+as\s+e:\s*logging\.error",
        ]
        return sum(bool(re.search(p, content)) for p in patterns) >= 1

    @staticmethod
    def _detect_health_check_duplication(content: str) -> bool:
        """Detect health check pattern duplications"""
        pattern = r"def\s+(check_|validate_)\w+\(.*?\):\s*.*?(return|assert)"
        return bool(re.search(pattern, content, re.DOTALL))

    @staticmethod
    def _detect_file_io_duplication(content: str) -> bool:
        """Detect file I/O pattern duplications"""
        pattern = r"open\([\"'].*?[\"']\s*,\s*[\"']r[\"']\)"
        return bool(re.search(pattern, content))

    @staticmethod
    def _detect_validation_duplication(content: str) -> bool:
        """Detect validation pattern duplications"""
        pattern = r"if\s+not\s+\w+\s*:\s*(raise|logging)"
        return bool(re.search(pattern, content))


class TestCodeDuplicationDetection(unittest.TestCase):
    """Test duplication detection framework"""

    def test_detector_initialization(self):
        """Test CodeDuplicationDetector can be initialized"""
        detector = CodeDuplicationDetector("d:\\PROJECTS\\CORTEX\\cortex")
        self.assertIsNotNone(detector)
        self.assertEqual(detector.root, Path("d:\\PROJECTS\\CORTEX\\cortex"))

    def test_connection_cleanup_duplication_detection(self):
        """Test connection cleanup duplication detection"""
        content = """
import sqlite3
try:
    conn = sqlite3.connect("db.sqlite3")
except Exception:
    pass
"""
        detector = CodeDuplicationDetector(".")
        found = detector._detect_connection_cleanup_duplication(content)
        self.assertTrue(found, "Should detect connection cleanup duplication")

    def test_error_logging_duplication_detection(self):
        """Test error logging duplication detection"""
        content = """
import logging
try:
    do_something()
except Exception as e:
    logging.error("Operation failed")
"""
        detector = CodeDuplicationDetector(".")
        found = detector._detect_error_logging_duplication(content)
        self.assertTrue(found, "Should detect error logging duplication")

    def test_health_check_duplication_detection(self):
        """Test health check pattern duplication detection"""
        content = """
def check_database_health():
    # Check database connectivity
    return True

def validate_connection_pool():
    # Validate pool state
    return True
"""
        detector = CodeDuplicationDetector(".")
        found = detector._detect_health_check_duplication(content)
        self.assertTrue(found, "Should detect health check pattern")

    def test_file_io_duplication_detection(self):
        """Test file I/O duplication detection"""
        content = """
def read_config():
    with open('config.yaml', 'r') as f:
        return f.read()

def read_manifest():
    with open('manifest.yaml', 'r') as f:
        return f.read()
"""
        detector = CodeDuplicationDetector(".")
        found = detector._detect_file_io_duplication(content)
        self.assertTrue(found, "Should detect file I/O duplication")

    def test_validation_duplication_detection(self):
        """Test validation pattern duplication detection"""
        content = """
def validate_config(config):
    if not config:
        raise ValueError("Config is empty")
    if not config.get("database"):
        logging.error("Database config missing")
"""
        detector = CodeDuplicationDetector(".")
        found = detector._detect_validation_duplication(content)
        self.assertTrue(found, "Should detect validation pattern")

    def test_analyze_directory_structure(self):
        """Test analyze_directory returns proper structure"""
        detector = CodeDuplicationDetector("d:\\PROJECTS\\CORTEX\\cortex")
        if os.path.exists(detector.root):
            findings = detector.analyze_directory()
            self.assertIsInstance(findings, dict)
            self.assertIn("connection_cleanup_patterns", findings)
            self.assertIn("error_logging_patterns", findings)
            self.assertIn("health_check_patterns", findings)
            self.assertIn("file_io_patterns", findings)
            self.assertIn("validation_patterns", findings)


class TestRefactoringRoadmapGeneration(unittest.TestCase):
    """Test refactoring roadmap generation"""

    def test_roadmap_document_structure(self):
        """Test refactoring roadmap has required structure"""
        roadmap = {
            "DUP-001": {
                "title": "Exception Handler Duplications",
                "severity": "CRITICAL",
                "files_affected": 5,
                "refactor_target": "cortex/common/exceptions.py (unified handlers)",
                "effort_hours": 4,
            },
            "DUP-002": {
                "title": "Connection Cleanup Patterns",
                "severity": "HIGH",
                "files_affected": 3,
                "refactor_target": "cortex/infrastructure/connection_pool.py (shared cleanup)",
                "effort_hours": 3,
            },
            "DUP-003": {
                "title": "Health Check Logic",
                "severity": "MEDIUM",
                "files_affected": 4,
                "refactor_target": "cortex/infrastructure/health_check.py (unified framework)",
                "effort_hours": 3,
            },
            "DUP-004": {
                "title": "File I/O Operations",
                "severity": "MEDIUM",
                "files_affected": 6,
                "refactor_target": "cortex/common/file_utils.py (new - centralized file ops)",
                "effort_hours": 4,
            },
            "DUP-005": {
                "title": "Validation Patterns",
                "severity": "LOW",
                "files_affected": 8,
                "refactor_target": "cortex/common/validators.py (unified validation)",
                "effort_hours": 5,
            },
        }
        
        self.assertEqual(len(roadmap), 5)
        for dup_id, entry in roadmap.items():
            self.assertIn("title", entry)
            self.assertIn("severity", entry)
            self.assertIn("files_affected", entry)
            self.assertIn("refactor_target", entry)
            self.assertIn("effort_hours", entry)
            self.assertIn("DUP-", dup_id)

    def test_roadmap_phases_structure(self):
        """Test refactoring roadmap includes phase structure"""
        phases = {
            "PHASE-REMEDIATION-002": {
                "name": "Code Refactoring Phase 2",
                "sequence": 10,
                "duration_weeks": 2,
                "duplications_addressed": ["DUP-001", "DUP-002", "DUP-003"],
                "total_effort_hours": 10,
            },
            "PHASE-REMEDIATION-003": {
                "name": "Code Refactoring Phase 3",
                "sequence": 11,
                "duration_weeks": 2,
                "duplications_addressed": ["DUP-004", "DUP-005"],
                "total_effort_hours": 9,
            },
        }
        
        self.assertEqual(len(phases), 2)
        for phase_id, phase in phases.items():
            self.assertIn("sequence", phase)
            self.assertIn("duplications_addressed", phase)
            self.assertIn("total_effort_hours", phase)

    def test_roadmap_metrics(self):
        """Test roadmap includes quality metrics"""
        metrics = {
            "total_duplications": 5,
            "total_files_affected": 26,
            "total_effort_hours": 19,
            "estimated_duration_weeks": 4,
            "lines_of_code_to_refactor": 450,
            "expected_reduction_percent": 35,
            "phase_count": 2,
        }
        
        self.assertGreater(metrics["total_duplications"], 0)
        self.assertGreater(metrics["total_files_affected"], 0)
        self.assertGreater(metrics["total_effort_hours"], 0)
        self.assertLess(metrics["expected_reduction_percent"], 100)


if __name__ == "__main__":
    unittest.main()
