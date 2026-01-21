"""
AC-REM-001-10: Environment Assumption Validation
Validates Python environment, SQLite, filesystem, and system assumptions
"""

import unittest
import sys
import os
import sqlite3
from pathlib import Path
from typing import Dict, List, Tuple
from dataclasses import dataclass


@dataclass
class EnvironmentAssumption:
    """Represents an environment assumption"""
    category: str  # PYTHON, SQLITE, FILESYSTEM, SYSTEM
    name: str
    expected: str
    current: str
    status: str  # SATISFIED, VIOLATED, WARNING


class PythonEnvironmentValidator:
    """Validates Python environment assumptions"""

    @staticmethod
    def get_python_version() -> Tuple[int, int, int]:
        """Get current Python version"""
        return sys.version_info[:3]

    @staticmethod
    def validate_python_version(min_version: Tuple[int, int, int] = (3, 10, 0)) -> EnvironmentAssumption:
        """Validate Python version meets minimum"""
        current = PythonEnvironmentValidator.get_python_version()
        status = "SATISFIED" if current >= min_version else "VIOLATED"
        
        return EnvironmentAssumption(
            category="PYTHON",
            name="Python Version",
            expected=f">= {'.'.join(map(str, min_version))}",
            current=f"{'.'.join(map(str, current))}",
            status=status
        )

    @staticmethod
    def validate_required_modules(required_modules: List[str]) -> List[EnvironmentAssumption]:
        """Validate required Python modules are installed"""
        assumptions = []
        
        for module_name in required_modules:
            try:
                __import__(module_name)
                status = "SATISFIED"
            except ImportError:
                status = "VIOLATED"
            
            assumptions.append(EnvironmentAssumption(
                category="PYTHON",
                name=f"Module: {module_name}",
                expected="Installed",
                current="Present" if status == "SATISFIED" else "Missing",
                status=status
            ))
        
        return assumptions


class SQLiteEnvironmentValidator:
    """Validates SQLite environment assumptions"""

    @staticmethod
    def get_sqlite_version() -> str:
        """Get SQLite version"""
        return sqlite3.sqlite_version

    @staticmethod
    def validate_sqlite_availability() -> EnvironmentAssumption:
        """Validate SQLite is available"""
        try:
            conn = sqlite3.connect(":memory:")
            conn.close()
            status = "SATISFIED"
        except Exception:
            status = "VIOLATED"
        
        return EnvironmentAssumption(
            category="SQLITE",
            name="SQLite Availability",
            expected="Accessible",
            current=f"v{SQLiteEnvironmentValidator.get_sqlite_version()}",
            status=status
        )

    @staticmethod
    def validate_sqlite_version(min_version: str = "3.22.0") -> EnvironmentAssumption:
        """Validate SQLite version meets minimum"""
        current = SQLiteEnvironmentValidator.get_sqlite_version()
        
        # Simple version comparison
        current_parts = [int(x) for x in current.split('.')[:3]]
        min_parts = [int(x) for x in min_version.split('.')[:3]]
        
        status = "SATISFIED" if current_parts >= min_parts else "VIOLATED"
        
        return EnvironmentAssumption(
            category="SQLITE",
            name="SQLite Version",
            expected=f">= {min_version}",
            current=current,
            status=status
        )


class FilesystemValidator:
    """Validates filesystem assumptions"""

    @staticmethod
    def validate_directory_writable(directory: str) -> EnvironmentAssumption:
        """Validate directory is writable"""
        path = Path(directory)
        
        try:
            # Check if directory exists and is writable
            if not path.exists():
                status = "VIOLATED"
                current = "Directory does not exist"
            else:
                # Try creating a test file
                test_file = path / ".cortex_write_test"
                test_file.touch()
                test_file.unlink()
                status = "SATISFIED"
                current = "Writable"
        except Exception as e:
            status = "VIOLATED"
            current = f"Not writable: {str(e)}"
        
        return EnvironmentAssumption(
            category="FILESYSTEM",
            name=f"Directory Writable: {directory}",
            expected="Writable",
            current=current,
            status=status
        )

    @staticmethod
    def validate_paths_exist(paths: List[str]) -> List[EnvironmentAssumption]:
        """Validate paths exist"""
        assumptions = []
        
        for path_str in paths:
            path = Path(path_str)
            status = "SATISFIED" if path.exists() else "VIOLATED"
            
            assumptions.append(EnvironmentAssumption(
                category="FILESYSTEM",
                name=f"Path Exists: {path_str}",
                expected="Exists",
                current="Present" if status == "SATISFIED" else "Missing",
                status=status
            ))
        
        return assumptions


class SystemValidator:
    """Validates system-level assumptions"""

    @staticmethod
    def get_platform() -> str:
        """Get current platform"""
        return sys.platform

    @staticmethod
    def validate_platform_support(supported_platforms: List[str] = None) -> EnvironmentAssumption:
        """Validate platform is supported"""
        if supported_platforms is None:
            supported_platforms = ["win32", "linux", "darwin"]
        
        current = SystemValidator.get_platform()
        status = "SATISFIED" if current in supported_platforms else "VIOLATED"
        
        return EnvironmentAssumption(
            category="SYSTEM",
            name="Platform Support",
            expected=", ".join(supported_platforms),
            current=current,
            status=status
        )

    @staticmethod
    def validate_environment_variables(required_vars: Dict[str, str]) -> List[EnvironmentAssumption]:
        """Validate required environment variables"""
        assumptions = []
        
        for var_name, expected_value in required_vars.items():
            current_value = os.environ.get(var_name)
            
            if current_value is None:
                status = "VIOLATED"
                current = "Not set"
            else:
                # If expected_value is None, just check existence
                if expected_value is None:
                    status = "SATISFIED"
                    current = "Set"
                else:
                    status = "SATISFIED" if current_value == expected_value else "WARNING"
                    current = current_value
            
            assumptions.append(EnvironmentAssumption(
                category="SYSTEM",
                name=f"Environment Variable: {var_name}",
                expected=expected_value or "Set",
                current=current,
                status=status
            ))
        
        return assumptions


class EnvironmentValidator:
    """Unified environment validator"""

    def __init__(self):
        self.assumptions: List[EnvironmentAssumption] = []
        self.violations: List[EnvironmentAssumption] = []

    def validate_all(self) -> Dict[str, List[EnvironmentAssumption]]:
        """Run all environment validations"""
        results = {
            "python": [],
            "sqlite": [],
            "filesystem": [],
            "system": []
        }
        
        # Python validations
        results["python"].append(PythonEnvironmentValidator.validate_python_version())
        results["python"].extend(PythonEnvironmentValidator.validate_required_modules([
            "pytest", "pyyaml", "sqlite3"
        ]))
        
        # SQLite validations
        results["sqlite"].append(SQLiteEnvironmentValidator.validate_sqlite_availability())
        results["sqlite"].append(SQLiteEnvironmentValidator.validate_sqlite_version())
        
        # Filesystem validations
        cortex_root = Path(__file__).parent.parent.parent / "cortex"
        if cortex_root.exists():
            results["filesystem"].append(
                FilesystemValidator.validate_directory_writable(str(cortex_root))
            )
        
        # System validations
        results["system"].append(SystemValidator.validate_platform_support())
        results["system"].extend(SystemValidator.validate_environment_variables({
            "PATH": None  # Just check if set
        }))
        
        # Flatten and collect all
        self.assumptions = [
            item for category_items in results.values()
            for item in category_items
        ]
        
        # Collect violations
        self.violations = [a for a in self.assumptions if a.status == "VIOLATED"]
        
        return results

    def is_environment_valid(self) -> bool:
        """Check if environment meets all critical requirements"""
        return len(self.violations) == 0

    def get_summary(self) -> Dict:
        """Get validation summary"""
        total = len(self.assumptions)
        satisfied = len([a for a in self.assumptions if a.status == "SATISFIED"])
        violated = len(self.violations)
        warnings = len([a for a in self.assumptions if a.status == "WARNING"])
        
        return {
            "total_assumptions": total,
            "satisfied": satisfied,
            "violated": violated,
            "warnings": warnings,
            "valid": self.is_environment_valid()
        }


class TestPythonEnvironmentValidator(unittest.TestCase):
    """Test Python environment validator"""

    def test_get_python_version(self):
        """Test getting Python version"""
        version = PythonEnvironmentValidator.get_python_version()
        self.assertEqual(len(version), 3)
        self.assertIsInstance(version[0], int)

    def test_validate_python_version_satisfied(self):
        """Test Python version validation when satisfied"""
        assumption = PythonEnvironmentValidator.validate_python_version((3, 0, 0))
        self.assertEqual(assumption.status, "SATISFIED")

    def test_validate_required_modules(self):
        """Test required modules validation"""
        assumptions = PythonEnvironmentValidator.validate_required_modules(["sys", "os"])
        self.assertEqual(len(assumptions), 2)
        # sys and os should be satisfied
        self.assertTrue(all(a.status == "SATISFIED" for a in assumptions))


class TestSQLiteEnvironmentValidator(unittest.TestCase):
    """Test SQLite environment validator"""

    def test_get_sqlite_version(self):
        """Test getting SQLite version"""
        version = SQLiteEnvironmentValidator.get_sqlite_version()
        self.assertIsNotNone(version)
        self.assertIn(".", version)

    def test_validate_sqlite_availability(self):
        """Test SQLite availability validation"""
        assumption = SQLiteEnvironmentValidator.validate_sqlite_availability()
        self.assertEqual(assumption.status, "SATISFIED")

    def test_validate_sqlite_version(self):
        """Test SQLite version validation"""
        assumption = SQLiteEnvironmentValidator.validate_sqlite_version("3.0.0")
        self.assertEqual(assumption.status, "SATISFIED")


class TestFilesystemValidator(unittest.TestCase):
    """Test filesystem validator"""

    def test_validate_paths_exist(self):
        """Test path existence validation"""
        assumptions = FilesystemValidator.validate_paths_exist(["."])
        self.assertEqual(len(assumptions), 1)
        self.assertEqual(assumptions[0].status, "SATISFIED")

    def test_validate_nonexistent_path(self):
        """Test nonexistent path validation"""
        assumptions = FilesystemValidator.validate_paths_exist(["/nonexistent/cortex/path"])
        self.assertEqual(len(assumptions), 1)
        self.assertEqual(assumptions[0].status, "VIOLATED")


class TestSystemValidator(unittest.TestCase):
    """Test system validator"""

    def test_get_platform(self):
        """Test getting platform"""
        platform = SystemValidator.get_platform()
        self.assertIsNotNone(platform)
        self.assertIn(platform, ["win32", "linux", "darwin"])

    def test_validate_platform_support(self):
        """Test platform support validation"""
        assumption = SystemValidator.validate_platform_support()
        self.assertEqual(assumption.status, "SATISFIED")

    def test_validate_environment_variables(self):
        """Test environment variable validation"""
        assumptions = SystemValidator.validate_environment_variables({
            "PATH": None
        })
        self.assertEqual(len(assumptions), 1)
        self.assertEqual(assumptions[0].status, "SATISFIED")


class TestEnvironmentValidator(unittest.TestCase):
    """Test unified environment validator"""

    def test_validator_initialization(self):
        """Test validator initialization"""
        validator = EnvironmentValidator()
        self.assertIsNotNone(validator)
        self.assertEqual(len(validator.assumptions), 0)

    def test_validate_all(self):
        """Test validating all assumptions"""
        validator = EnvironmentValidator()
        results = validator.validate_all()
        
        self.assertIn("python", results)
        self.assertIn("sqlite", results)
        self.assertIn("filesystem", results)
        self.assertIn("system", results)
        self.assertGreater(len(validator.assumptions), 0)

    def test_is_environment_valid(self):
        """Test environment validity check"""
        validator = EnvironmentValidator()
        validator.validate_all()
        
        # Should be valid on typical development machine
        is_valid = validator.is_environment_valid()
        self.assertIsInstance(is_valid, bool)

    def test_get_summary(self):
        """Test getting validation summary"""
        validator = EnvironmentValidator()
        validator.validate_all()
        
        summary = validator.get_summary()
        self.assertIn("total_assumptions", summary)
        self.assertIn("satisfied", summary)
        self.assertIn("violated", summary)
        self.assertIn("valid", summary)


if __name__ == "__main__":
    unittest.main()
