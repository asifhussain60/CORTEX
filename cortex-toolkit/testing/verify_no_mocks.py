#!/usr/bin/env python3
"""
Mock Detection Pipeline
Phase 0.2 - Verifies no unittest.mock usage in production code (src/)

Usage:
    python scripts/verify_no_mocks.py [--directory DIR]
    
Exit Codes:
    0 - No violations found
    1 - Mock usage detected in production code
    2 - Configuration or runtime error
"""

import ast
import sys
from pathlib import Path
from typing import List, Dict, Any
import argparse


# Exception list - files that can legitimately use mocks
EXCEPTION_LIST = [
    "src/test_utils/mock_factory.py",
    "src/test_utils/test_helpers.py",
    "src/agents/feature_completion_orchestrator.py",  # Async test orchestrator
    "src/caching/cache_warmer.py",  # Cache testing utility
    "src/application/behaviors/validation_behavior_old_backup.py",  # Backup file
]

# File patterns to skip (backup files, etc.)
SKIP_PATTERNS = [
    "_old_backup",
    "_backup",
    ".bak",
    "_deprecated",
]

# Directories to check
CHECK_DIRECTORIES = ["src"]

# Directories to skip
SKIP_DIRECTORIES = ["tests", "test", ".git", "__pycache__", "venv", ".venv"]


class MockViolation:
    """Represents a mock usage violation"""
    
    def __init__(self, file_path: str, line_number: int, message: str):
        self.file = file_path
        self.line = line_number
        self.message = message
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'file': self.file,
            'line': self.line,
            'message': self.message
        }
    
    def __repr__(self):
        return f"{self.file}:{self.line} - {self.message}"


class MockDetector(ast.NodeVisitor):
    """AST visitor to detect unittest.mock usage"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.violations: List[MockViolation] = []
    
    def visit_Import(self, node: ast.Import):
        """Detect 'import unittest.mock' or 'import mock'"""
        for alias in node.names:
            if 'mock' in alias.name.lower():
                violation = MockViolation(
                    self.file_path,
                    node.lineno,
                    f"Mock import detected: {alias.name}"
                )
                self.violations.append(violation)
        self.generic_visit(node)
    
    def visit_ImportFrom(self, node: ast.ImportFrom):
        """Detect 'from unittest.mock import ...' or 'from mock import ...'"""
        if node.module and 'mock' in node.module.lower():
            names = [alias.name for alias in node.names]
            violation = MockViolation(
                self.file_path,
                node.lineno,
                f"Mock import detected: from {node.module} import {', '.join(names)}"
            )
            self.violations.append(violation)
        self.generic_visit(node)


def should_check_file(file_path: Path) -> bool:
    """
    Determine if file should be checked for mocks.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if file should be checked, False otherwise
    """
    # Convert to string for comparison
    file_str = str(file_path).replace('\\', '/')
    
    # Check if in exception list
    for exception in EXCEPTION_LIST:
        if exception in file_str:
            return False
    
    # Check skip patterns (backup files, etc.)
    for pattern in SKIP_PATTERNS:
        if pattern in file_str:
            return False
    
    # Check if in skip directories
    for part in file_path.parts:
        if part in SKIP_DIRECTORIES:
            return False
    
    # Only check Python files
    if file_path.suffix != '.py':
        return False
    
    # Check if in a directory we should check
    for check_dir in CHECK_DIRECTORIES:
        if check_dir in file_path.parts:
            return True
    
    return False


def detect_mocks_in_file(code: str, file_path: str) -> List[Dict[str, Any]]:
    """
    Detect mock usage in Python code using AST.
    
    Args:
        code: Python source code string
        file_path: Path to the file (for error messages)
        
    Returns:
        List of violation dictionaries
    """
    violations = []
    
    try:
        tree = ast.parse(code)
        detector = MockDetector(file_path)
        detector.visit(tree)
        violations = [v.to_dict() for v in detector.violations]
    except SyntaxError as e:
        # Handle syntax errors gracefully
        violations.append({
            'file': file_path,
            'line': e.lineno or 0,
            'message': f"Syntax error: {e.msg}"
        })
    except Exception as e:
        # Handle other parsing errors
        violations.append({
            'file': file_path,
            'line': 0,
            'message': f"Parse error: {str(e)}"
        })
    
    return violations


def scan_directory(directory: Path) -> List[Dict[str, Any]]:
    """
    Scan directory recursively for mock usage.
    
    Args:
        directory: Root directory to scan
        
    Returns:
        List of violation dictionaries
    """
    all_violations = []
    
    # Handle missing directory
    if not directory.exists():
        return all_violations
    
    # Find all Python files
    for py_file in directory.rglob("*.py"):
        if should_check_file(py_file):
            try:
                code = py_file.read_text(encoding='utf-8')
                violations = detect_mocks_in_file(code, str(py_file))
                all_violations.extend(violations)
            except Exception as e:
                # Handle file read errors
                all_violations.append({
                    'file': str(py_file),
                    'line': 0,
                    'message': f"Read error: {str(e)}"
                })
    
    return all_violations


def main():
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(description="Verify no mock objects in production code")
    parser.add_argument(
        '--directory',
        type=str,
        default='.',
        help='Root directory to scan (default: current directory)'
    )
    
    args = parser.parse_args()
    root_dir = Path(args.directory)
    
    print(f"🔍 Scanning for mock usage in production code...")
    print(f"   Root: {root_dir.absolute()}")
    print(f"   Checking: {', '.join(CHECK_DIRECTORIES)}")
    print(f"   Skipping: {', '.join(SKIP_DIRECTORIES)}")
    print()
    
    # Scan all check directories
    all_violations = []
    for check_dir in CHECK_DIRECTORIES:
        scan_path = root_dir / check_dir
        if scan_path.exists():
            violations = scan_directory(scan_path)
            all_violations.extend(violations)
    
    # Report results
    if all_violations:
        print(f"❌ Found {len(all_violations)} mock violation(s):")
        print()
        for violation in all_violations:
            print(f"  {violation['file']}:{violation['line']}")
            print(f"    {violation['message']}")
            print()
        sys.exit(1)
    else:
        print("✅ No mock usage detected in production code")
        sys.exit(0)


if __name__ == "__main__":
    main()
