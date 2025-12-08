"""
Multi-Language Test Discovery Engine

Detects test frameworks and extracts test cases across:
- Python: pytest, unittest
- C#: xUnit, NUnit, MSTest
- JavaScript/TypeScript: Jest, Mocha, Jasmine
- ColdFusion: TestBox, MXUnit
- Ruby: RSpec, Minitest

Author: Asif Hussain
Created: 2025-12-08
Phase: Dashboard Code Intelligence - Phase 2.5.1 (GREEN)
"""

import re
import ast
import json
from pathlib import Path
from typing import List, Dict, Set, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict


class TestFramework(Enum):
    """Supported test frameworks across languages."""
    # Python
    PYTEST = "pytest"
    UNITTEST = "unittest"
    
    # C#
    XUNIT = "xUnit"
    NUNIT = "NUnit"
    MSTEST = "MSTest"
    
    # JavaScript/TypeScript
    JEST = "Jest"
    MOCHA = "Mocha"
    JASMINE = "Jasmine"
    
    # ColdFusion
    TESTBOX = "TestBox"
    MXUNIT = "MXUnit"
    
    # Ruby
    RSPEC = "RSpec"
    MINITEST = "Minitest"


@dataclass
class TestCase:
    """Represents a single test case."""
    name: str
    file_path: Path
    line_number: int
    framework: TestFramework
    class_name: Optional[str] = None
    description: Optional[str] = None
    tags: List[str] = field(default_factory=list)


@dataclass
class TestSuite:
    """Represents a collection of related test cases."""
    name: str
    file_path: Path
    framework: TestFramework
    test_cases: List[TestCase] = field(default_factory=list)
    
    @property
    def total_tests(self) -> int:
        return len(self.test_cases)


@dataclass
class TestMapping:
    """Maps test files to production code."""
    test_file: Path
    source_file: Path
    confidence: str  # 'high', 'medium', 'low'
    test_cases: List[TestCase] = field(default_factory=list)


class TestDiscoveryEngine:
    """
    Multi-language test discovery engine.
    
    Detects test frameworks, extracts test cases, and maps tests to production code.
    """
    
    # File patterns for test detection
    TEST_FILE_PATTERNS = {
        TestFramework.PYTEST: [r'test_.*\.py$', r'.*_test\.py$'],
        TestFramework.UNITTEST: [r'test.*\.py$'],
        TestFramework.XUNIT: [r'.*Tests\.cs$', r'.*Test\.cs$'],
        TestFramework.NUNIT: [r'.*Tests\.cs$', r'.*Test\.cs$'],
        TestFramework.JEST: [r'.*\.test\.(js|ts|jsx|tsx)$', r'.*\.spec\.(js|ts|jsx|tsx)$'],
        TestFramework.MOCHA: [r'.*\.test\.(js|ts)$', r'test/.*\.js$'],
        TestFramework.TESTBOX: [r'.*Test\.cfc$', r'.*Spec\.cfc$'],
        TestFramework.RSPEC: [r'.*_spec\.rb$'],
    }
    
    # Framework indicators (files that indicate framework presence)
    FRAMEWORK_INDICATORS = {
        TestFramework.PYTEST: ['pytest.ini', 'setup.cfg', 'tox.ini', 'pyproject.toml'],
        TestFramework.XUNIT: ['xunit', 'xUnit'],
        TestFramework.NUNIT: ['nunit', 'NUnit'],
        TestFramework.JEST: ['jest.config.js', 'jest.config.ts', 'package.json'],
        TestFramework.MOCHA: ['.mocharc.json', '.mocharc.js', 'package.json'],
        TestFramework.TESTBOX: ['testbox.xml', 'box.json'],
        TestFramework.RSPEC: ['.rspec', 'spec/spec_helper.rb', 'Gemfile'],
    }
    
    def __init__(self, project_path: Path):
        """Initialize test discovery engine."""
        self.project_path = Path(project_path)
        self.detected_frameworks: Dict[TestFramework, Dict] = {}
        self.test_suites: List[TestSuite] = []
    
    def detect_frameworks(self) -> Dict[TestFramework, Dict]:
        """
        Detect which test frameworks are present in the project.
        
        Returns:
            Dict mapping TestFramework to metadata (confidence, indicators)
        """
        frameworks = {}
        
        # Check for framework indicators
        for framework, indicators in self.FRAMEWORK_INDICATORS.items():
            found_indicators = []
            
            for indicator in indicators:
                # Check root directory
                indicator_path = self.project_path / indicator
                if indicator_path.exists():
                    found_indicators.append(indicator)
                
                # Check package.json content for npm packages
                if indicator == 'package.json':
                    package_json = self.project_path / 'package.json'
                    if package_json.exists():
                        try:
                            content = package_json.read_text(encoding='utf-8')
                            data = json.loads(content)
                            dev_deps = data.get('devDependencies', {})
                            deps = data.get('dependencies', {})
                            
                            if framework == TestFramework.JEST and ('jest' in dev_deps or 'jest' in deps):
                                found_indicators.append('jest package')
                            elif framework == TestFramework.MOCHA and ('mocha' in dev_deps or 'mocha' in deps):
                                found_indicators.append('mocha package')
                        except:
                            pass
                
                # Check for .csproj files with xunit/nunit references
                if framework in [TestFramework.XUNIT, TestFramework.NUNIT]:
                    for csproj_file in self.project_path.rglob('*.csproj'):
                        try:
                            content = csproj_file.read_text(encoding='utf-8')
                            if indicator.lower() in content.lower():
                                found_indicators.append(str(csproj_file.relative_to(self.project_path)))
                        except:
                            pass
                
                # Check Gemfile for rspec
                if framework == TestFramework.RSPEC and indicator == 'Gemfile':
                    gemfile = self.project_path / 'Gemfile'
                    if gemfile.exists():
                        try:
                            content = gemfile.read_text(encoding='utf-8')
                            if 'rspec' in content.lower():
                                found_indicators.append('Gemfile')
                        except:
                            pass
            
            # Also check for test file patterns
            test_files = self._find_test_files(framework)
            
            if found_indicators or test_files:
                confidence = 'high' if found_indicators else 'medium'
                frameworks[framework] = {
                    'confidence': confidence,
                    'indicators': found_indicators,
                    'test_files_count': len(test_files)
                }
        
        self.detected_frameworks = frameworks
        return frameworks
    
    def _find_test_files(self, framework: TestFramework) -> List[Path]:
        """Find test files matching framework patterns."""
        test_files = []
        patterns = self.TEST_FILE_PATTERNS.get(framework, [])
        
        for pattern in patterns:
            regex = re.compile(pattern)
            for file_path in self.project_path.rglob('*'):
                if file_path.is_file() and regex.search(str(file_path.name)):
                    test_files.append(file_path)
        
        return test_files
    
    def extract_test_cases(self, file_path: Path, framework: TestFramework) -> List[TestCase]:
        """
        Extract test cases from a test file.
        
        Args:
            file_path: Path to test file
            framework: Test framework being used
        
        Returns:
            List of TestCase objects
        """
        try:
            content = file_path.read_text(encoding='utf-8')
        except:
            return []
        
        if framework in [TestFramework.PYTEST, TestFramework.UNITTEST]:
            return self._extract_python_tests(file_path, content, framework)
        elif framework in [TestFramework.XUNIT, TestFramework.NUNIT]:
            return self._extract_csharp_tests(file_path, content, framework)
        elif framework in [TestFramework.JEST, TestFramework.MOCHA]:
            return self._extract_javascript_tests(file_path, content, framework)
        elif framework == TestFramework.TESTBOX:
            return self._extract_coldfusion_tests(file_path, content)
        elif framework == TestFramework.RSPEC:
            return self._extract_ruby_tests(file_path, content)
        
        return []
    
    def _extract_python_tests(self, file_path: Path, content: str, framework: TestFramework) -> List[TestCase]:
        """Extract test cases from Python test files."""
        test_cases = []
        
        try:
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                # Test functions (def test_xxx)
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    test_cases.append(TestCase(
                        name=node.name,
                        file_path=file_path,
                        line_number=node.lineno,
                        framework=framework
                    ))
                
                # Test classes
                elif isinstance(node, ast.ClassDef):
                    class_name = node.name
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef) and item.name.startswith('test_'):
                            test_cases.append(TestCase(
                                name=f"{class_name}.{item.name}",
                                file_path=file_path,
                                line_number=item.lineno,
                                framework=framework,
                                class_name=class_name
                            ))
        except:
            # Fallback to regex if AST parsing fails
            test_func_pattern = r'^def (test_\w+)\('
            for i, line in enumerate(content.split('\n'), 1):
                match = re.search(test_func_pattern, line)
                if match:
                    test_cases.append(TestCase(
                        name=match.group(1),
                        file_path=file_path,
                        line_number=i,
                        framework=framework
                    ))
        
        return test_cases
    
    def _extract_csharp_tests(self, file_path: Path, content: str, framework: TestFramework) -> List[TestCase]:
        """Extract test cases from C# test files."""
        test_cases = []
        
        # Patterns for xUnit/NUnit test methods
        if framework == TestFramework.XUNIT:
            patterns = [
                r'\[Fact\]\s+public\s+(?:async\s+)?(?:Task\s+)?(\w+)\s*\(',
                r'\[Theory\].*?public\s+(?:async\s+)?(?:Task\s+)?(\w+)\s*\('
            ]
        else:  # NUnit
            patterns = [
                r'\[Test\]\s+public\s+(?:async\s+)?(?:Task\s+)?(\w+)\s*\(',
                r'\[TestCase.*?\]\s+public\s+(?:async\s+)?(?:Task\s+)?(\w+)\s*\('
            ]
        
        for pattern in patterns:
            for i, line in enumerate(content.split('\n'), 1):
                match = re.search(pattern, line, re.DOTALL)
                if match:
                    test_cases.append(TestCase(
                        name=match.group(1),
                        file_path=file_path,
                        line_number=i,
                        framework=framework
                    ))
        
        return test_cases
    
    def _extract_javascript_tests(self, file_path: Path, content: str, framework: TestFramework) -> List[TestCase]:
        """Extract test cases from JavaScript/TypeScript test files."""
        test_cases = []
        
        # Patterns for Jest/Mocha test cases
        patterns = [
            r"test\s*\(\s*['\"]([^'\"]+)['\"]",  # test('name', ...)
            r"it\s*\(\s*['\"]([^'\"]+)['\"]",     # it('name', ...)
        ]
        
        for pattern in patterns:
            for i, line in enumerate(content.split('\n'), 1):
                match = re.search(pattern, line)
                if match:
                    test_cases.append(TestCase(
                        name=match.group(1),
                        file_path=file_path,
                        line_number=i,
                        framework=framework,
                        description=match.group(1)
                    ))
        
        return test_cases
    
    def _extract_coldfusion_tests(self, file_path: Path, content: str) -> List[TestCase]:
        """Extract test cases from ColdFusion TestBox files."""
        test_cases = []
        
        # TestBox uses it('test name', function() { })
        pattern = r"it\s*\(\s*['\"]([^'\"]+)['\"]"
        
        for i, line in enumerate(content.split('\n'), 1):
            match = re.search(pattern, line)
            if match:
                test_cases.append(TestCase(
                    name=match.group(1),
                    file_path=file_path,
                    line_number=i,
                    framework=TestFramework.TESTBOX,
                    description=match.group(1)
                ))
        
        return test_cases
    
    def _extract_ruby_tests(self, file_path: Path, content: str) -> List[TestCase]:
        """Extract test cases from Ruby RSpec files."""
        test_cases = []
        
        # RSpec uses it 'test name' do ... end
        pattern = r"it\s+['\"]([^'\"]+)['\"]"
        
        for i, line in enumerate(content.split('\n'), 1):
            match = re.search(pattern, line)
            if match:
                test_cases.append(TestCase(
                    name=match.group(1),
                    file_path=file_path,
                    line_number=i,
                    framework=TestFramework.RSPEC,
                    description=match.group(1)
                ))
        
        return test_cases
    
    def map_tests_to_code(self) -> List[TestMapping]:
        """
        Map test files to corresponding source code files.
        
        Uses naming conventions and import analysis.
        
        Returns:
            List of TestMapping objects
        """
        mappings = []
        
        # Ensure frameworks are detected
        if not self.detected_frameworks:
            self.detect_frameworks()
        
        for framework in self.detected_frameworks:
            test_files = self._find_test_files(framework)
            
            for test_file in test_files:
                # Infer source file from test file name
                source_file = self._infer_source_file(test_file, framework)
                
                if source_file and source_file.exists():
                    test_cases = self.extract_test_cases(test_file, framework)
                    mappings.append(TestMapping(
                        test_file=test_file,
                        source_file=source_file,
                        confidence='high',
                        test_cases=test_cases
                    ))
        
        return mappings
    
    def _infer_source_file(self, test_file: Path, framework: TestFramework) -> Optional[Path]:
        """Infer source file from test file name."""
        test_name = test_file.stem
        
        # Python: test_calculator.py -> calculator.py
        if framework in [TestFramework.PYTEST, TestFramework.UNITTEST]:
            if test_name.startswith('test_'):
                source_name = test_name[5:] + '.py'
            elif test_name.endswith('_test'):
                source_name = test_name[:-5] + '.py'
            else:
                return None
            
            # Look in src/ directory
            source_path = self.project_path / 'src' / source_name
            return source_path if source_path.exists() else None
        
        # C#: CalculatorTests.cs -> Calculator.cs
        elif framework in [TestFramework.XUNIT, TestFramework.NUNIT]:
            if test_name.endswith('Tests'):
                source_name = test_name[:-5] + '.cs'
            elif test_name.endswith('Test'):
                source_name = test_name[:-4] + '.cs'
            else:
                return None
            
            source_path = self.project_path / 'src' / source_name
            return source_path if source_path.exists() else None
        
        # JavaScript: calculator.test.js -> calculator.js
        elif framework in [TestFramework.JEST, TestFramework.MOCHA]:
            source_name = test_name.replace('.test', '').replace('.spec', '') + test_file.suffix
            source_path = self.project_path / 'src' / source_name
            return source_path if source_path.exists() else None
        
        return None
    
    def discover_test_suites(self) -> List[TestSuite]:
        """
        Discover all test suites in the project.
        
        Returns:
            List of TestSuite objects with aggregated test cases
        """
        suites = []
        
        # Ensure frameworks are detected
        if not self.detected_frameworks:
            self.detect_frameworks()
        
        for framework in self.detected_frameworks:
            test_files = self._find_test_files(framework)
            
            for test_file in test_files:
                test_cases = self.extract_test_cases(test_file, framework)
                
                if test_cases:
                    suite = TestSuite(
                        name=test_file.stem,
                        file_path=test_file,
                        framework=framework,
                        test_cases=test_cases
                    )
                    suites.append(suite)
        
        self.test_suites = suites
        return suites


# Convenience function for quick discovery
def discover_tests(project_path: Path) -> Dict:
    """
    Quick test discovery for a project.
    
    Returns:
        Dict with frameworks, test suites, and mappings
    """
    engine = TestDiscoveryEngine(project_path)
    
    return {
        'frameworks': engine.detect_frameworks(),
        'test_suites': engine.discover_test_suites(),
        'mappings': engine.map_tests_to_code(),
        'total_tests': sum(suite.total_tests for suite in engine.test_suites)
    }
