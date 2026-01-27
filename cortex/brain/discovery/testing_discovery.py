"""
Testing Framework Discovery

Discovers testing frameworks, configurations, fixtures, coverage tools,
and mock/stub usage in repositories.

Supports:
- pytest (Python)
- Jest (JavaScript/TypeScript)
- Mocha (JavaScript)
- Coverage.py (Python)
- Istanbul/NYC (JavaScript)
- unittest.mock, jest.mock

Task: DISC-006
Authority: PHASE-9-DISCOVERY-ORCHESTRATOR.yaml
Governance: CORE-008, CORE-011, CORE-012, CORE-030
"""

import json
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional

from cortex.brain.discovery import DiscoveryPlugin


logger = logging.getLogger(__name__)


class TestFramework(Enum):
    """
    Test framework types.
    
    Attributes:
        PYTEST: pytest framework
        JEST: Jest framework
        MOCHA: Mocha framework
        UNITTEST: Python unittest
        JASMINE: Jasmine framework
    """
    PYTEST = "pytest"
    JEST = "jest"
    MOCHA = "mocha"
    UNITTEST = "unittest"
    JASMINE = "jasmine"


@dataclass
class TestFileInfo:
    """
    Test file information.
    
    Attributes:
        path: File path
        framework: Test framework used
        test_count: Number of tests
        fixtures: Fixture names used
    """
    path: str
    framework: str
    test_count: int = 0
    fixtures: List[str] = field(default_factory=list)


class TestingDiscovery(DiscoveryPlugin):
    """
    Discovers testing frameworks and configurations.
    
    Analyzes test framework configurations, test files, fixtures,
    coverage tools, and mock/stub usage patterns.
    
    Features:
    - Multi-framework support (pytest, Jest, Mocha)
    - Configuration file parsing
    - Test file pattern detection
    - Fixture discovery
    - Coverage tool detection
    - Mock/stub usage analysis
    
    Example:
        ```python
        discovery = TestingDiscovery()
        topology = discovery.discover(Path("/my/repo"))
        
        for framework in topology["frameworks"]:
            print(f"Framework: {framework}")
        ```
    """
    
    def __init__(self) -> None:
        """Initialize testing discovery."""
        self.supported_frameworks = ["pytest", "jest", "mocha", "unittest"]
        logger.info("TestingDiscovery initialized")
    
    def get_supported_frameworks(self) -> List[str]:
        """
        Get list of supported test frameworks.
        
        Returns:
            List of framework names
        """
        return self.supported_frameworks
    
    def discover(self, repo_path: Path) -> Dict[str, Any]:
        """
        Discover testing topology in repository.
        
        Args:
            repo_path: Path to repository to scan
            
        Returns:
            Dictionary containing testing topology
        """
        logger.info(f"Discovering testing topology in {repo_path}")
        
        frameworks: List[str] = []
        test_files: List[Dict[str, Any]] = []
        coverage_config: Optional[Dict[str, Any]] = None
        mock_usage: Dict[str, int] = {}
        
        # Detect pytest
        pytest_info = self.detect_pytest(repo_path)
        if pytest_info:
            frameworks.append("pytest")
        
        # Detect Jest
        jest_info = self.detect_jest(repo_path)
        if jest_info:
            frameworks.append("jest")
        
        # Detect Mocha
        mocha_info = self.detect_mocha(repo_path)
        if mocha_info:
            frameworks.append("mocha")
        
        # Scan test files
        test_files = self.scan_test_files(repo_path)
        
        # Detect coverage configuration
        coverage_config = self.detect_coverage_config(repo_path)
        
        # Detect mock usage
        mock_usage = self.detect_mocks(repo_path)
        
        logger.info(
            f"Discovered {len(frameworks)} frameworks, "
            f"{len(test_files)} test files"
        )
        
        return {
            "frameworks": frameworks,
            "pytest_config": pytest_info,
            "jest_config": jest_info,
            "mocha_config": mocha_info,
            "test_files": [
                {
                    "path": tf["path"],
                    "framework": tf["framework"],
                }
                for tf in test_files
            ],
            "coverage_config": coverage_config,
            "mock_usage": mock_usage,
            "total_test_files": len(test_files),
            "total_frameworks": len(frameworks),
        }
    
    def detect_pytest(self, repo_path: Path) -> Optional[Dict[str, Any]]:
        """
        Detect pytest configuration.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            pytest configuration or None
        """
        config_files = ["pytest.ini", "pyproject.toml", "setup.cfg", "tox.ini"]
        
        for config_file in config_files:
            config_path = repo_path / config_file
            if config_path.exists():
                try:
                    content = config_path.read_text()
                    if "[pytest]" in content or "[tool.pytest" in content:
                        # Parse basic config
                        config = {}
                        if "testpaths" in content:
                            match = re.search(r'testpaths\s*=\s*(.+)', content)
                            if match:
                                config["testpaths"] = match.group(1).strip()
                        
                        logger.debug(f"Detected pytest config: {config_path}")
                        return {
                            "framework": "pytest",
                            "config_file": str(config_path),
                            "config": config,
                        }
                except Exception:
                    pass
        
        return None
    
    def scan_pytest_fixtures(self, repo_path: Path) -> List[Dict[str, Any]]:
        """
        Scan for pytest fixtures.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            List of fixture information
        """
        fixtures = []
        
        for conftest in repo_path.rglob("conftest.py"):
            try:
                content = conftest.read_text()
                # Find @pytest.fixture decorators
                fixture_matches = re.finditer(
                    r'@pytest\.fixture(?:\([^)]*\))?\s+def\s+(\w+)',
                    content
                )
                for match in fixture_matches:
                    fixtures.append({
                        "name": match.group(1),
                        "file": str(conftest),
                    })
            except Exception:
                pass
        
        logger.debug(f"Found {len(fixtures)} pytest fixtures")
        return fixtures
    
    def detect_jest(self, repo_path: Path) -> Optional[Dict[str, Any]]:
        """
        Detect Jest configuration.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Jest configuration or None
        """
        config_files = ["jest.config.js", "jest.config.ts", "jest.config.json"]
        
        for config_file in config_files:
            config_path = repo_path / config_file
            if config_path.exists():
                logger.debug(f"Detected Jest config: {config_path}")
                return {
                    "framework": "jest",
                    "config_file": str(config_path),
                }
        
        # Check package.json
        package_json = repo_path / "package.json"
        if package_json.exists():
            try:
                with open(package_json) as f:
                    pkg = json.load(f)
                    if "jest" in pkg.get("devDependencies", {}) or \
                       "jest" in pkg.get("dependencies", {}):
                        logger.debug(f"Detected Jest in package.json")
                        return {
                            "framework": "jest",
                            "config_file": str(package_json),
                        }
            except Exception:
                pass
        
        return None
    
    def detect_mocha(self, repo_path: Path) -> Optional[Dict[str, Any]]:
        """
        Detect Mocha configuration.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Mocha configuration or None
        """
        config_files = [".mocharc.json", ".mocharc.js", ".mocharc.yaml"]
        
        for config_file in config_files:
            config_path = repo_path / config_file
            if config_path.exists():
                logger.debug(f"Detected Mocha config: {config_path}")
                return {
                    "framework": "mocha",
                    "config_file": str(config_path),
                }
        
        return None
    
    def detect_coverage_config(self, repo_path: Path) -> Optional[Dict[str, Any]]:
        """
        Detect coverage tool configuration.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Coverage configuration or None
        """
        # Check for coverage.py
        coveragerc = repo_path / ".coveragerc"
        if coveragerc.exists():
            try:
                content = coveragerc.read_text()
                config = {}
                if "[run]" in content:
                    source_match = re.search(r'source\s*=\s*(.+)', content)
                    if source_match:
                        config["source"] = source_match.group(1).strip()
                
                logger.debug(f"Detected coverage.py config: {coveragerc}")
                return {
                    "tool": "coverage.py",
                    "config_file": str(coveragerc),
                    "config": config,
                }
            except Exception:
                pass
        
        # Check for Istanbul/NYC
        nyc_config = repo_path / ".nycrc"
        if nyc_config.exists():
            logger.debug(f"Detected Istanbul config: {nyc_config}")
            return {
                "tool": "istanbul",
                "config_file": str(nyc_config),
            }
        
        return None
    
    def scan_test_files(self, repo_path: Path) -> List[Dict[str, Any]]:
        """
        Scan for test files.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            List of test file information
        """
        test_files = []
        
        # Python test files
        for test_file in repo_path.rglob("test_*.py"):
            test_files.append({
                "path": str(test_file),
                "framework": "pytest",
            })
        
        for test_file in repo_path.rglob("*_test.py"):
            test_files.append({
                "path": str(test_file),
                "framework": "pytest",
            })
        
        # JavaScript test files
        for test_file in repo_path.rglob("*.test.js"):
            test_files.append({
                "path": str(test_file),
                "framework": "jest",
            })
        
        for test_file in repo_path.rglob("*.spec.js"):
            test_files.append({
                "path": str(test_file),
                "framework": "jest",
            })
        
        for test_file in repo_path.rglob("*.test.ts"):
            test_files.append({
                "path": str(test_file),
                "framework": "jest",
            })
        
        logger.debug(f"Found {len(test_files)} test files")
        return test_files
    
    def detect_mocks(self, repo_path: Path) -> Dict[str, int]:
        """
        Detect mock/stub usage.
        
        Args:
            repo_path: Path to repository
            
        Returns:
            Dictionary with mock usage counts
        """
        python_mocks = 0
        javascript_mocks = 0
        
        # Scan Python files for unittest.mock
        for py_file in repo_path.rglob("*.py"):
            try:
                content = py_file.read_text()
                if "unittest.mock" in content or "from mock import" in content:
                    python_mocks += 1
            except Exception:
                pass
        
        # Scan JavaScript files for jest.mock
        for js_file in repo_path.rglob("*.js"):
            try:
                content = js_file.read_text()
                if "jest.mock" in content or "jest.fn()" in content:
                    javascript_mocks += 1
            except Exception:
                pass
        
        for ts_file in repo_path.rglob("*.ts"):
            try:
                content = ts_file.read_text()
                if "jest.mock" in content or "jest.fn()" in content:
                    javascript_mocks += 1
            except Exception:
                pass
        
        logger.debug(f"Detected {python_mocks} Python mocks, {javascript_mocks} JS mocks")
        
        return {
            "python_mocks": python_mocks,
            "javascript_mocks": javascript_mocks,
        }
