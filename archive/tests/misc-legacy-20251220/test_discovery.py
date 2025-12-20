"""
CORTEX Test Discovery System

Discovers and categorizes tests for intelligent test execution:
- Discovers tests by tier (tier0, tier1, tier2, tier3)
- Categorizes by plugin
- Identifies integration vs unit tests
- Builds test dependency graph

Part of Test Execution Infrastructure
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Created: 2025-11-11
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Dict, Set, Optional
import re
import subprocess
import sys


class TestCategory(Enum):
    """Test category types."""
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    FUNCTIONAL = "functional"
    PERFORMANCE = "performance"


class TestTier(Enum):
    """CORTEX tier classification."""
    TIER_0 = "tier0"
    TIER_1 = "tier1"
    TIER_2 = "tier2"
    TIER_3 = "tier3"
    PLUGIN = "plugin"
    AGENT = "agent"
    OPERATION = "operation"
    UTILS = "utils"
    EDGE_CASE = "edge_case"
    AMBIENT = "ambient"


@dataclass
class TestNode:
    """A discovered test."""
    node_id: str  # pytest node ID (path::class::method)
    file_path: Path
    test_name: str
    class_name: Optional[str]
    category: TestCategory
    tier: TestTier
    dependencies: Set[str]  # Other test IDs this depends on
    estimated_duration: float = 0.0  # seconds


@dataclass
class TestDiscoveryResult:
    """Result of test discovery."""
    total_tests: int
    tests_by_tier: Dict[TestTier, List[TestNode]]
    tests_by_category: Dict[TestCategory, List[TestNode]]
    all_tests: List[TestNode]
    metadata: Dict[str, any]


class TestDiscovery:
    """
    Discovers and categorizes pytest tests.
    
    Features:
    - Automatic tier detection from file path
    - Category inference from test name/markers
    - Dependency analysis
    - Duration estimation
    """
    
    def __init__(self, test_root: Optional[Path] = None):
        """
        Initialize Test Discovery.
        
        Args:
            test_root: Root directory for tests (default: tests/)
        """
        if test_root is None:
            project_root = Path(__file__).parent.parent.parent
            test_root = project_root / "tests"
        
        self.test_root = Path(test_root)
        
        # Category patterns
        self.category_patterns = {
            TestCategory.INTEGRATION: [
                r".*integration.*",
                r".*e2e.*",
                r".*end_to_end.*"
            ],
            TestCategory.PERFORMANCE: [
                r".*performance.*",
                r".*benchmark.*",
                r".*stress.*"
            ],
            TestCategory.FUNCTIONAL: [
                r".*functional.*",
                r".*acceptance.*"
            ]
        }
        
        # Tier patterns (from file path)
        self.tier_patterns = {
            TestTier.TIER_0: [r".*tests/tier0/.*"],
            TestTier.TIER_1: [r".*tests/tier1/.*"],
            TestTier.TIER_2: [r".*tests/tier2/.*"],
            TestTier.TIER_3: [r".*tests/tier3/.*"],
            TestTier.PLUGIN: [r".*tests/plugins/.*"],
            TestTier.AGENT: [r".*tests/cortex_agents/.*", r".*tests/agents/.*"],
            TestTier.OPERATION: [r".*tests/operations/.*"],
            TestTier.AMBIENT: [r".*tests/ambient/.*"],
            TestTier.EDGE_CASE: [r".*tests/edge_cases/.*"],
            TestTier.UTILS: [r".*tests/utils/.*", r".*tests/test_.*"]
        }
    
    def discover_all(self) -> TestDiscoveryResult:
        """
        Discover all tests in test root.
        
        Returns:
            TestDiscoveryResult with categorized tests
        """
        print(f"[*] Discovering tests in {self.test_root}...")
        
        # Collect test node IDs using pytest
        node_ids = self._collect_test_node_ids()
        
        print(f"[+] Found {len(node_ids)} tests")
        
        # Parse node IDs into TestNode objects
        tests = []
        for node_id in node_ids:
            test_node = self._parse_node_id(node_id)
            if test_node:
                tests.append(test_node)
        
        # Categorize tests
        tests_by_tier = self._categorize_by_tier(tests)
        tests_by_category = self._categorize_by_category(tests)
        
        # Generate metadata
        metadata = {
            "test_root": str(self.test_root),
            "total_tests": len(tests),
            "tiers": {tier.value: len(test_list) for tier, test_list in tests_by_tier.items()},
            "categories": {cat.value: len(test_list) for cat, test_list in tests_by_category.items()}
        }
        
        return TestDiscoveryResult(
            total_tests=len(tests),
            tests_by_tier=tests_by_tier,
            tests_by_category=tests_by_category,
            all_tests=tests,
            metadata=metadata
        )
    
    def _collect_test_node_ids(self) -> List[str]:
        """Collect test node IDs using pytest --collect-only."""
        cmd = [
            sys.executable, "-m", "pytest",
            str(self.test_root),
            "--collect-only", "-q", "--no-header"
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse output for node IDs
            # Format: path/to/test_file.py::TestClass::test_method
            node_ids = []
            for line in result.stdout.split('\n'):
                line = line.strip()
                if '::' in line and not line.startswith('<'):
                    # Remove pytest formatting artifacts
                    line = line.replace('<Function ', '').replace('>', '')
                    line = line.replace('<Method ', '').replace('>', '')
                    node_ids.append(line)
            
            return node_ids
        
        except subprocess.TimeoutExpired:
            print("[X] Test collection timed out")
            return []
        except Exception as e:
            print(f"[X] Test collection failed: {e}")
            return []
    
    def _parse_node_id(self, node_id: str) -> Optional[TestNode]:
        """
        Parse pytest node ID into TestNode.
        
        Args:
            node_id: pytest node ID (e.g., tests/tier0/test_brain.py::TestBrain::test_load)
        
        Returns:
            TestNode or None if parsing fails
        """
        try:
            # Split node ID
            parts = node_id.split('::')
            
            if len(parts) < 2:
                return None
            
            file_path_str = parts[0]
            file_path = Path(file_path_str)
            
            if len(parts) == 2:
                # Format: path::test_function
                class_name = None
                test_name = parts[1]
            elif len(parts) == 3:
                # Format: path::TestClass::test_method
                class_name = parts[1]
                test_name = parts[2]
            else:
                return None
            
            # Determine tier
            tier = self._detect_tier(file_path)
            
            # Determine category
            category = self._detect_category(test_name, file_path)
            
            # Detect dependencies (simplified)
            dependencies = self._detect_dependencies(test_name)
            
            return TestNode(
                node_id=node_id,
                file_path=file_path,
                test_name=test_name,
                class_name=class_name,
                category=category,
                tier=tier,
                dependencies=dependencies
            )
        
        except Exception as e:
            print(f"[!] Failed to parse node ID '{node_id}': {e}")
            return None
    
    def _detect_tier(self, file_path: Path) -> TestTier:
        """Detect tier from file path."""
        file_path_str = str(file_path).replace('\\', '/')
        
        for tier, patterns in self.tier_patterns.items():
            for pattern in patterns:
                if re.match(pattern, file_path_str):
                    return tier
        
        return TestTier.UTILS  # Default
    
    def _detect_category(self, test_name: str, file_path: Path) -> TestCategory:
        """Detect category from test name and file path."""
        combined_str = f"{test_name} {str(file_path)}".lower()
        
        for category, patterns in self.category_patterns.items():
            for pattern in patterns:
                if re.search(pattern, combined_str):
                    return category
        
        return TestCategory.UNIT  # Default
    
    def _detect_dependencies(self, test_name: str) -> Set[str]:
        """Detect test dependencies (simplified heuristic)."""
        dependencies = set()
        
        # Look for common dependency patterns in test names
        # Example: test_after_setup implies dependency on test_setup
        if "after" in test_name.lower():
            # Simplified: no actual analysis yet
            pass
        
        return dependencies
    
    def _categorize_by_tier(self, tests: List[TestNode]) -> Dict[TestTier, List[TestNode]]:
        """Categorize tests by tier."""
        by_tier = {}
        for test in tests:
            if test.tier not in by_tier:
                by_tier[test.tier] = []
            by_tier[test.tier].append(test)
        return by_tier
    
    def _categorize_by_category(self, tests: List[TestNode]) -> Dict[TestCategory, List[TestNode]]:
        """Categorize tests by category."""
        by_category = {}
        for test in tests:
            if test.category not in by_category:
                by_category[test.category] = []
            by_category[test.category].append(test)
        return by_category
    
    def filter_by_tier(self, result: TestDiscoveryResult, tier: TestTier) -> List[str]:
        """
        Get test node IDs for a specific tier.
        
        Args:
            result: Discovery result
            tier: Tier to filter by
        
        Returns:
            List of pytest node IDs
        """
        tests = result.tests_by_tier.get(tier, [])
        return [t.node_id for t in tests]
    
    def filter_by_category(self, result: TestDiscoveryResult, category: TestCategory) -> List[str]:
        """
        Get test node IDs for a specific category.
        
        Args:
            result: Discovery result
            category: Category to filter by
        
        Returns:
            List of pytest node IDs
        """
        tests = result.tests_by_category.get(category, [])
        return [t.node_id for t in tests]
    
    def generate_report(self, result: TestDiscoveryResult) -> str:
        """Generate human-readable discovery report."""
        report = []
        report.append("=" * 70)
        report.append("CORTEX TEST DISCOVERY REPORT")
        report.append("=" * 70)
        report.append(f"Test Root: {result.metadata['test_root']}")
        report.append(f"Total Tests: {result.total_tests}")
        report.append("")
        
        # By tier
        report.append("TESTS BY TIER:")
        report.append("-" * 70)
        for tier, count in sorted(result.metadata['tiers'].items(), key=lambda x: -x[1]):
            percentage = (count / result.total_tests * 100) if result.total_tests > 0 else 0
            bar = "█" * int(percentage / 2)
            report.append(f"  {tier:15s} {count:4d} tests ({percentage:5.1f}%) {bar}")
        report.append("")
        
        # By category
        report.append("TESTS BY CATEGORY:")
        report.append("-" * 70)
        for category, count in sorted(result.metadata['categories'].items(), key=lambda x: -x[1]):
            percentage = (count / result.total_tests * 100) if result.total_tests > 0 else 0
            bar = "█" * int(percentage / 2)
            report.append(f"  {category:15s} {count:4d} tests ({percentage:5.1f}%) {bar}")
        report.append("")
        
        report.append("=" * 70)
        
        return "\n".join(report)


def discover_tests(test_root: Optional[Path] = None) -> TestDiscoveryResult:
    """
    Convenience function to discover tests.
    
    Args:
        test_root: Root directory for tests
    
    Returns:
        TestDiscoveryResult
    """
    discovery = TestDiscovery(test_root)
    result = discovery.discover_all()
    print(discovery.generate_report(result))
    return result


if __name__ == "__main__":
    discover_tests()
