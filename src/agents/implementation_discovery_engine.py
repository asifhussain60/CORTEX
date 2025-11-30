#!/usr/bin/env python3
"""
Implementation Discovery Engine

Scans codebase for actual implementation changes to understand what was built
during feature development. Provides concrete implementation intelligence for
documentation updates and system analysis.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import ast
import os
import re
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)

@dataclass
class CodeElement:
    """Represents a code element (class, function, etc.) discovered in scanning"""
    name: str
    element_type: str  # 'class', 'function', 'method', 'variable'
    file_path: str
    line_number: int
    signature: Optional[str] = None
    docstring: Optional[str] = None
    decorators: List[str] = field(default_factory=list)
    is_public: bool = True
    complexity: int = 0

@dataclass 
class FileChange:
    """Represents changes to a file"""
    file_path: str
    change_type: str  # 'added', 'modified', 'deleted'
    lines_added: int
    lines_deleted: int
    commit_hash: str
    timestamp: datetime
    author: str

@dataclass
class APIEndpoint:
    """Represents an API endpoint discovered in code"""
    path: str
    method: str  # GET, POST, PUT, DELETE
    handler_function: str
    file_path: str
    line_number: int
    parameters: List[str] = field(default_factory=list)
    return_type: Optional[str] = None
    authentication_required: bool = False

@dataclass
class TestCase:
    """Represents a test case discovered in test files"""
    name: str
    test_type: str  # 'unit', 'integration', 'e2e'
    file_path: str
    line_number: int
    target_code: Optional[str] = None  # What code this test targets
    assertions_count: int = 0
    is_passing: bool = True

@dataclass
class ImplementationData:
    """Complete implementation intelligence for a feature"""
    feature_name: str
    discovery_timestamp: datetime
    
    # Code changes
    files_changed: List[FileChange] = field(default_factory=list)
    new_classes: List[CodeElement] = field(default_factory=list)
    new_functions: List[CodeElement] = field(default_factory=list)
    modified_elements: List[CodeElement] = field(default_factory=list)
    
    # API endpoints
    new_endpoints: List[APIEndpoint] = field(default_factory=list)
    modified_endpoints: List[APIEndpoint] = field(default_factory=list)
    
    # Test coverage
    new_tests: List[TestCase] = field(default_factory=list)
    test_coverage_percentage: float = 0.0
    
    # Dependencies
    new_dependencies: List[str] = field(default_factory=list)
    updated_dependencies: List[str] = field(default_factory=list)
    
    # Metrics
    total_lines_added: int = 0
    total_lines_deleted: int = 0
    complexity_score: int = 0
    
    # Quality indicators
    has_documentation: bool = False
    has_tests: bool = False
    follows_conventions: bool = True


class CodeScanner:
    """Scans source code files to extract structural information"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        
    def scan_python_files(self, file_paths: List[str]) -> List[CodeElement]:
        """Scan Python files and extract classes, functions, methods"""
        elements = []
        
        for file_path in file_paths:
            if not file_path.endswith('.py'):
                continue
                
            try:
                elements.extend(self._parse_python_file(file_path))
            except Exception as e:
                logger.warning(f"Failed to parse Python file {file_path}: {e}")
                
        return elements
    
    def _parse_python_file(self, file_path: str) -> List[CodeElement]:
        """Parse a single Python file using AST"""
        elements = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                source = f.read()
                
            tree = ast.parse(source)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    element = CodeElement(
                        name=node.name,
                        element_type='class',
                        file_path=file_path,
                        line_number=node.lineno,
                        signature=f"class {node.name}",
                        docstring=ast.get_docstring(node),
                        decorators=[d.id if hasattr(d, 'id') else str(d) for d in node.decorator_list],
                        is_public=not node.name.startswith('_')
                    )
                    elements.append(element)
                    
                elif isinstance(node, ast.FunctionDef):
                    # Determine if this is a method (inside a class) or standalone function
                    element_type = 'function'
                    for parent in ast.walk(tree):
                        if isinstance(parent, ast.ClassDef):
                            for child in parent.body:
                                if child == node:
                                    element_type = 'method'
                                    break
                    
                    # Build signature
                    args = [arg.arg for arg in node.args.args]
                    signature = f"def {node.name}({', '.join(args)})"
                    
                    element = CodeElement(
                        name=node.name,
                        element_type=element_type,
                        file_path=file_path,
                        line_number=node.lineno,
                        signature=signature,
                        docstring=ast.get_docstring(node),
                        decorators=[d.id if hasattr(d, 'id') else str(d) for d in node.decorator_list],
                        is_public=not node.name.startswith('_'),
                        complexity=self._calculate_complexity(node)
                    )
                    elements.append(element)
                    
        except Exception as e:
            logger.error(f"Error parsing {file_path}: {e}")
            
        return elements
    
    def _calculate_complexity(self, node: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Decision points increase complexity
            if isinstance(child, (ast.If, ast.While, ast.For, ast.Try, ast.With)):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                complexity += len(child.values) - 1
                
        return complexity
    
    def scan_csharp_files(self, file_paths: List[str]) -> List[CodeElement]:
        """Scan C# files for classes and methods"""
        elements = []
        
        for file_path in file_paths:
            if not file_path.endswith('.cs'):
                continue
                
            try:
                elements.extend(self._parse_csharp_file(file_path))
            except Exception as e:
                logger.warning(f"Failed to parse C# file {file_path}: {e}")
                
        return elements
    
    def _parse_csharp_file(self, file_path: str) -> List[CodeElement]:
        """Parse C# file using regex patterns (simple approach)"""
        elements = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Class pattern
            class_pattern = r'(?:public|private|internal|protected)?\s*class\s+(\w+)'
            for match in re.finditer(class_pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                element = CodeElement(
                    name=match.group(1),
                    element_type='class',
                    file_path=file_path,
                    line_number=line_num,
                    signature=match.group(0),
                    is_public=not match.group(0).startswith('private')
                )
                elements.append(element)
                
            # Method pattern  
            method_pattern = r'(?:public|private|internal|protected)\s+(?:static\s+)?(?:async\s+)?\w+\s+(\w+)\s*\([^)]*\)'
            for match in re.finditer(method_pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                element = CodeElement(
                    name=match.group(1),
                    element_type='method',
                    file_path=file_path,
                    line_number=line_num,
                    signature=match.group(0),
                    is_public=match.group(0).startswith('public')
                )
                elements.append(element)
                
        except Exception as e:
            logger.error(f"Error parsing C# file {file_path}: {e}")
            
        return elements


class GitAnalyzer:
    """Analyzes Git history to understand recent changes"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        
    def get_recent_changes(self, days_back: int = 7) -> List[FileChange]:
        """Get file changes from the last N days"""
        since_date = datetime.now() - timedelta(days=days_back)
        since_str = since_date.strftime("%Y-%m-%d")
        
        try:
            # Get commits from the last N days
            cmd = [
                'git', 'log',
                f'--since="{since_str}"',
                '--pretty=format:%H|%an|%ad|%s',
                '--date=iso',
                '--name-status'
            ]
            
            result = subprocess.run(cmd, cwd=self.workspace_path, capture_output=True, text=True)
            
            if result.returncode != 0:
                logger.error(f"Git log failed: {result.stderr}")
                return []
                
            return self._parse_git_log_output(result.stdout)
            
        except Exception as e:
            logger.error(f"Failed to analyze git history: {e}")
            return []
    
    def _parse_git_log_output(self, output: str) -> List[FileChange]:
        """Parse git log output into FileChange objects"""
        changes = []
        lines = output.strip().split('\n')
        
        current_commit = None
        current_author = None
        current_date = None
        
        for line in lines:
            if '|' in line and len(line.split('|')) == 4:
                # Commit info line
                parts = line.split('|')
                current_commit = parts[0]
                current_author = parts[1]
                current_date = datetime.fromisoformat(parts[2].replace(' ', 'T', 1))
                
            elif line.startswith(('A\t', 'M\t', 'D\t')):
                # File change line
                status = line[0]
                file_path = line[2:]
                
                change_type = {'A': 'added', 'M': 'modified', 'D': 'deleted'}[status]
                
                # Get line count changes for this file
                lines_added, lines_deleted = self._get_line_changes(current_commit, file_path)
                
                change = FileChange(
                    file_path=file_path,
                    change_type=change_type,
                    lines_added=lines_added,
                    lines_deleted=lines_deleted,
                    commit_hash=current_commit,
                    timestamp=current_date,
                    author=current_author
                )
                changes.append(change)
                
        return changes
    
    def _get_line_changes(self, commit_hash: str, file_path: str) -> Tuple[int, int]:
        """Get lines added/deleted for a specific file in a commit"""
        try:
            cmd = ['git', 'show', '--numstat', commit_hash, '--', file_path]
            result = subprocess.run(cmd, cwd=self.workspace_path, capture_output=True, text=True)
            
            if result.returncode == 0 and result.stdout.strip():
                parts = result.stdout.strip().split('\t')
                if len(parts) >= 2:
                    added = int(parts[0]) if parts[0] != '-' else 0
                    deleted = int(parts[1]) if parts[1] != '-' else 0
                    return added, deleted
                    
        except Exception as e:
            logger.warning(f"Failed to get line changes for {file_path}: {e}")
            
        return 0, 0
    
    def get_files_changed_recently(self, days_back: int = 7) -> List[str]:
        """Get list of files that changed recently"""
        changes = self.get_recent_changes(days_back)
        return [change.file_path for change in changes if change.change_type != 'deleted']


class TestAnalyzer:
    """Analyzes test files and test coverage"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        
    def discover_test_files(self) -> List[str]:
        """Find all test files in the workspace"""
        test_files = []
        
        # Common test file patterns
        patterns = ['*test*.py', '*_test.py', 'test_*.py', '*Test.cs', '*Tests.cs']
        
        for pattern in patterns:
            test_files.extend(self.workspace_path.rglob(pattern))
            
        return [str(f) for f in test_files]
    
    def analyze_test_files(self, test_files: List[str]) -> List[TestCase]:
        """Analyze test files to extract test cases"""
        test_cases = []
        
        for test_file in test_files:
            if test_file.endswith('.py'):
                test_cases.extend(self._analyze_python_tests(test_file))
            elif test_file.endswith('.cs'):
                test_cases.extend(self._analyze_csharp_tests(test_file))
                
        return test_cases
    
    def _analyze_python_tests(self, test_file: str) -> List[TestCase]:
        """Analyze Python test files"""
        test_cases = []
        
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            tree = ast.parse(content)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef) and node.name.startswith('test_'):
                    # Count assertions
                    assertion_count = 0
                    for child in ast.walk(node):
                        if isinstance(child, ast.Assert):
                            assertion_count += 1
                        elif isinstance(child, ast.Call) and hasattr(child.func, 'attr'):
                            if child.func.attr.startswith('assert'):
                                assertion_count += 1
                    
                    test_case = TestCase(
                        name=node.name,
                        test_type=self._determine_test_type(test_file, node.name),
                        file_path=test_file,
                        line_number=node.lineno,
                        assertions_count=assertion_count
                    )
                    test_cases.append(test_case)
                    
        except Exception as e:
            logger.warning(f"Failed to analyze Python test file {test_file}: {e}")
            
        return test_cases
    
    def _analyze_csharp_tests(self, test_file: str) -> List[TestCase]:
        """Analyze C# test files"""
        test_cases = []
        
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Find test methods with [Test] or [Fact] attributes
            test_pattern = r'\[(?:Test|Fact)\]\s*(?:public\s+)?(?:async\s+)?(?:void|Task)\s+(\w+)\s*\('
            
            for match in re.finditer(test_pattern, content):
                line_num = content[:match.start()].count('\n') + 1
                
                # Count assertions in the method
                method_start = match.end()
                brace_count = 0
                method_end = method_start
                
                for i, char in enumerate(content[method_start:]):
                    if char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            method_end = method_start + i
                            break
                
                method_content = content[method_start:method_end]
                assertion_count = len(re.findall(r'Assert\.', method_content))
                
                test_case = TestCase(
                    name=match.group(1),
                    test_type=self._determine_test_type(test_file, match.group(1)),
                    file_path=test_file,
                    line_number=line_num,
                    assertions_count=assertion_count
                )
                test_cases.append(test_case)
                
        except Exception as e:
            logger.warning(f"Failed to analyze C# test file {test_file}: {e}")
            
        return test_cases
    
    def _determine_test_type(self, file_path: str, test_name: str) -> str:
        """Determine if test is unit, integration, or e2e"""
        file_path_lower = file_path.lower()
        test_name_lower = test_name.lower()
        
        if 'integration' in file_path_lower or 'integration' in test_name_lower:
            return 'integration'
        elif 'e2e' in file_path_lower or 'end2end' in file_path_lower or 'e2e' in test_name_lower:
            return 'e2e'
        else:
            return 'unit'


class APIDiscoverer:
    """Discovers API endpoints in web application code"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        
    def discover_endpoints(self, source_files: List[str]) -> List[APIEndpoint]:
        """Discover API endpoints from source files"""
        endpoints = []
        
        for file_path in source_files:
            if file_path.endswith('.py'):
                endpoints.extend(self._discover_flask_fastapi_endpoints(file_path))
            elif file_path.endswith('.cs'):
                endpoints.extend(self._discover_aspnet_endpoints(file_path))
            elif file_path.endswith('.js') or file_path.endswith('.ts'):
                endpoints.extend(self._discover_express_endpoints(file_path))
                
        return endpoints
    
    def _discover_flask_fastapi_endpoints(self, file_path: str) -> List[APIEndpoint]:
        """Discover Flask/FastAPI endpoints"""
        endpoints = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Flask route pattern
            flask_pattern = r'@app\.route\([\'"]([^\'"]+)[\'"](?:,\s*methods\s*=\s*\[([^\]]+)\])?\)\s*def\s+(\w+)'
            
            for match in re.finditer(flask_pattern, content):
                path = match.group(1)
                methods = match.group(2)
                function_name = match.group(3)
                line_num = content[:match.start()].count('\n') + 1
                
                if methods:
                    # Parse methods list
                    method_list = [m.strip().strip('\'"') for m in methods.split(',')]
                else:
                    method_list = ['GET']
                
                for method in method_list:
                    endpoint = APIEndpoint(
                        path=path,
                        method=method,
                        handler_function=function_name,
                        file_path=file_path,
                        line_number=line_num
                    )
                    endpoints.append(endpoint)
                    
        except Exception as e:
            logger.warning(f"Failed to discover Flask endpoints in {file_path}: {e}")
            
        return endpoints
    
    def _discover_aspnet_endpoints(self, file_path: str) -> List[APIEndpoint]:
        """Discover ASP.NET endpoints"""
        endpoints = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # ASP.NET attribute routing pattern
            route_pattern = r'\[(?:Http(Get|Post|Put|Delete))\(?[\'"]?([^\'"]*)[\'"]?\)?\]\s*(?:public\s+)?(?:async\s+)?[\w<>]+\s+(\w+)\s*\('
            
            for match in re.finditer(route_pattern, content):
                method = match.group(1).upper()
                path = match.group(2) or "/"
                function_name = match.group(3)
                line_num = content[:match.start()].count('\n') + 1
                
                endpoint = APIEndpoint(
                    path=path,
                    method=method,
                    handler_function=function_name,
                    file_path=file_path,
                    line_number=line_num
                )
                endpoints.append(endpoint)
                
        except Exception as e:
            logger.warning(f"Failed to discover ASP.NET endpoints in {file_path}: {e}")
            
        return endpoints
    
    def _discover_express_endpoints(self, file_path: str) -> List[APIEndpoint]:
        """Discover Express.js endpoints"""
        endpoints = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Express route pattern
            express_pattern = r'app\.(get|post|put|delete|patch)\s*\(\s*[\'"]([^\'"]+)[\'"]'
            
            for match in re.finditer(express_pattern, content):
                method = match.group(1).upper()
                path = match.group(2)
                line_num = content[:match.start()].count('\n') + 1
                
                endpoint = APIEndpoint(
                    path=path,
                    method=method,
                    handler_function="anonymous",  # Express often uses inline functions
                    file_path=file_path,
                    line_number=line_num
                )
                endpoints.append(endpoint)
                
        except Exception as e:
            logger.warning(f"Failed to discover Express endpoints in {file_path}: {e}")
            
        return endpoints


class ImplementationDiscoveryEngine:
    """
    Main engine that coordinates all discovery components to build complete
    implementation intelligence for a completed feature.
    """
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.code_scanner = CodeScanner(workspace_path)
        self.git_analyzer = GitAnalyzer(workspace_path)
        self.test_analyzer = TestAnalyzer(workspace_path)
        self.api_discoverer = APIDiscoverer(workspace_path)
        
    async def discover_implementation(self, feature_name: str) -> ImplementationData:
        """
        Main orchestration method that discovers all implementation details
        for a completed feature.
        """
        logger.info(f"Starting implementation discovery for feature: {feature_name}")
        
        # Get recent changes (last 7 days by default)
        file_changes = self.git_analyzer.get_recent_changes(days_back=7)
        changed_files = [change.file_path for change in file_changes 
                        if change.change_type != 'deleted']
        
        # Scan code structure in changed files
        new_elements = self.code_scanner.scan_python_files(changed_files)
        new_elements.extend(self.code_scanner.scan_csharp_files(changed_files))
        
        # Categorize elements
        new_classes = [e for e in new_elements if e.element_type == 'class']
        new_functions = [e for e in new_elements if e.element_type in ['function', 'method']]
        
        # Discover API endpoints
        api_endpoints = self.api_discoverer.discover_endpoints(changed_files)
        
        # Analyze test coverage
        test_files = self.test_analyzer.discover_test_files()
        test_cases = self.test_analyzer.analyze_test_files(test_files)
        
        # Calculate metrics
        total_lines_added = sum(change.lines_added for change in file_changes)
        total_lines_deleted = sum(change.lines_deleted for change in file_changes)
        complexity_score = sum(e.complexity for e in new_elements)
        
        # Determine quality indicators
        has_tests = len(test_cases) > 0
        has_documentation = any(e.docstring for e in new_elements)
        
        # Build implementation data
        implementation_data = ImplementationData(
            feature_name=feature_name,
            discovery_timestamp=datetime.now(),
            files_changed=file_changes,
            new_classes=new_classes,
            new_functions=new_functions,
            new_endpoints=api_endpoints,
            new_tests=test_cases,
            total_lines_added=total_lines_added,
            total_lines_deleted=total_lines_deleted,
            complexity_score=complexity_score,
            has_documentation=has_documentation,
            has_tests=has_tests,
            test_coverage_percentage=self._calculate_test_coverage(new_elements, test_cases)
        )
        
        logger.info(f"Implementation discovery complete for {feature_name}: "
                   f"{len(new_classes)} classes, {len(new_functions)} functions, "
                   f"{len(api_endpoints)} endpoints, {len(test_cases)} tests")
        
        return implementation_data
    
    def _calculate_test_coverage(self, code_elements: List[CodeElement], 
                                test_cases: List[TestCase]) -> float:
        """Calculate approximate test coverage percentage"""
        if not code_elements:
            return 0.0
            
        # Simple heuristic: count test cases vs code elements
        # More sophisticated analysis would require actual coverage tools
        public_elements = [e for e in code_elements if e.is_public and e.element_type != 'class']
        
        if not public_elements:
            return 0.0
            
        # Rough estimate: each test case covers 1-2 functions on average
        estimated_covered = min(len(test_cases) * 1.5, len(public_elements))
        coverage = (estimated_covered / len(public_elements)) * 100
        
        return min(coverage, 100.0)


if __name__ == "__main__":
    # Test implementation discovery
    import asyncio
    
    async def test_discovery():
        engine = ImplementationDiscoveryEngine("/Users/asifhussain/PROJECTS/CORTEX")
        data = await engine.discover_implementation("test_feature")
        
        print(f"Discovery Results for {data.feature_name}:")
        print(f"- Files changed: {len(data.files_changed)}")
        print(f"- New classes: {len(data.new_classes)}")
        print(f"- New functions: {len(data.new_functions)}")
        print(f"- API endpoints: {len(data.new_endpoints)}")
        print(f"- Test cases: {len(data.new_tests)}")
        print(f"- Test coverage: {data.test_coverage_percentage:.1f}%")
        print(f"- Lines added: {data.total_lines_added}")
        print(f"- Complexity score: {data.complexity_score}")
    
    asyncio.run(test_discovery())