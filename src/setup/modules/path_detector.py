"""
Path Detection Utility

Scans repository for existing test directories and suggests optimal paths.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import os
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class PathDetector:
    """
    Detects existing project structure and suggests path configurations.
    
    Example:
        detector = PathDetector("/path/to/repo")
        test_dirs = detector.find_test_directories()
        suggestion = detector.suggest_test_directory()
    """
    
    # Common test directory patterns
    TEST_DIR_PATTERNS = [
        "tests",
        "test",
        "__tests__",
        "Tests",
        "Test",
        "spec",
        "testing"
    ]
    
    # Test file patterns to confirm it's actually a test directory
    TEST_FILE_PATTERNS = [
        "test_*.py",
        "*_test.py",
        "*.test.ts",
        "*.test.js",
        "*.spec.ts",
        "*.spec.js",
        "*Test.cs",
        "*Tests.cs"
    ]
    
    def __init__(self, workspace_root: str):
        """
        Initialize path detector.
        
        Args:
            workspace_root: Repository root directory
        """
        self.workspace_root = Path(workspace_root).resolve()
        
    def find_test_directories(self, max_depth: int = 3) -> List[Dict[str, Any]]:
        """
        Find all test directories in the repository.
        
        Args:
            max_depth: Maximum directory depth to search
        
        Returns:
            List of dictionaries with test directory information:
            [
                {
                    "path": "tests",
                    "absolute_path": "/full/path/to/tests",
                    "test_count": 45,
                    "framework": "pytest",
                    "confidence": 0.95
                }
            ]
        """
        test_dirs = []
        
        for root, dirs, files in os.walk(self.workspace_root):
            # Calculate depth
            depth = len(Path(root).relative_to(self.workspace_root).parts)
            if depth > max_depth:
                continue
            
            # Skip hidden directories and common exclusions
            dirs[:] = [d for d in dirs if not d.startswith('.') and d not in ['node_modules', 'venv', '.venv', 'env', '__pycache__', 'dist', 'build']]
            
            # Check if directory name matches test patterns
            dir_name = Path(root).name
            if dir_name in self.TEST_DIR_PATTERNS or any(pattern in dir_name.lower() for pattern in ['test', 'spec']):
                test_count = self._count_test_files(root)
                
                if test_count > 0:
                    framework = self._detect_framework(root)
                    confidence = self._calculate_confidence(root, test_count)
                    
                    test_dirs.append({
                        "path": str(Path(root).relative_to(self.workspace_root)),
                        "absolute_path": str(root),
                        "test_count": test_count,
                        "framework": framework,
                        "confidence": confidence
                    })
        
        # Sort by confidence (highest first)
        test_dirs.sort(key=lambda x: x["confidence"], reverse=True)
        
        return test_dirs
    
    def _count_test_files(self, directory: str) -> int:
        """Count test files in directory."""
        count = 0
        for pattern in self.TEST_FILE_PATTERNS:
            count += len(list(Path(directory).rglob(pattern)))
        return count
    
    def _detect_framework(self, directory: str) -> str:
        """Detect test framework from directory contents."""
        dir_path = Path(directory)
        
        # Check for pytest
        if (dir_path / "conftest.py").exists():
            return "pytest"
        if (self.workspace_root / "pytest.ini").exists():
            return "pytest"
        
        # Check for Jest
        if (self.workspace_root / "jest.config.js").exists() or (self.workspace_root / "jest.config.ts").exists():
            return "jest"
        
        # Check for xUnit (C#)
        for csproj in self.workspace_root.rglob("*.csproj"):
            content = csproj.read_text(errors='ignore')
            if 'xunit' in content.lower():
                return "xunit"
        
        # Check for unittest (Python)
        for test_file in dir_path.rglob("*.py"):
            content = test_file.read_text(errors='ignore')
            if 'import unittest' in content or 'from unittest' in content:
                return "unittest"
        
        return "unknown"
    
    def _calculate_confidence(self, directory: str, test_count: int) -> float:
        """
        Calculate confidence score for test directory (0.0 to 1.0).
        
        Factors:
        - Number of test files (more = higher confidence)
        - Presence of test framework config files
        - Directory name match
        """
        confidence = 0.0
        dir_path = Path(directory)
        dir_name = dir_path.name
        
        # Base confidence from directory name
        if dir_name in ["tests", "test", "Tests", "Test"]:
            confidence += 0.4
        elif dir_name in ["__tests__", "spec"]:
            confidence += 0.3
        else:
            confidence += 0.1
        
        # Test count contribution
        if test_count >= 20:
            confidence += 0.3
        elif test_count >= 10:
            confidence += 0.2
        elif test_count >= 5:
            confidence += 0.1
        
        # Framework config presence
        if (dir_path / "conftest.py").exists():
            confidence += 0.2
        if (self.workspace_root / "pytest.ini").exists():
            confidence += 0.1
        
        return min(confidence, 1.0)
    
    def suggest_test_directory(self) -> str:
        """
        Suggest the best test directory based on analysis.
        
        Returns:
            Relative path to suggested test directory
        """
        test_dirs = self.find_test_directories()
        
        if not test_dirs:
            # No existing tests found, suggest conventional location
            return self._suggest_default_test_directory()
        
        # Return highest confidence directory
        return test_dirs[0]["path"]
    
    def _suggest_default_test_directory(self) -> str:
        """Suggest default test directory based on project type."""
        # Check for Python project
        if (self.workspace_root / "requirements.txt").exists() or (self.workspace_root / "setup.py").exists():
            return "tests"
        
        # Check for JavaScript/TypeScript project
        if (self.workspace_root / "package.json").exists():
            return "__tests__"
        
        # Check for C# project
        if list(self.workspace_root.glob("*.sln")) or list(self.workspace_root.glob("*.csproj")):
            return "Tests"
        
        # Default fallback
        return "tests"
    
    def find_documents_directories(self) -> Dict[str, Optional[str]]:
        """
        Find existing CORTEX document directories.
        
        Returns:
            Dictionary mapping category to path
        """
        brain_path = self.workspace_root / "cortex-brain"
        docs_path = brain_path / "documents"
        
        categories = {
            "reports": None,
            "analysis": None,
            "summaries": None,
            "planning": None,
            "investigations": None
        }
        
        if not docs_path.exists():
            return categories
        
        for category in categories.keys():
            category_path = docs_path / category
            if category_path.exists():
                categories[category] = str(category_path.relative_to(self.workspace_root))
        
        return categories
    
    def scan_repository(self) -> Dict[str, Any]:
        """
        Comprehensive repository scan.
        
        Returns:
            Complete scan results with suggestions
        """
        test_dirs = self.find_test_directories()
        suggested_test_dir = self.suggest_test_directory()
        doc_dirs = self.find_documents_directories()
        
        return {
            "workspace_root": str(self.workspace_root),
            "test_directories": test_dirs,
            "suggested_test_directory": suggested_test_dir,
            "document_directories": doc_dirs,
            "recommendations": self._generate_recommendations(test_dirs, suggested_test_dir)
        }
    
    def _generate_recommendations(self, test_dirs: List[Dict], suggested: str) -> List[str]:
        """Generate human-readable recommendations."""
        recommendations = []
        
        if not test_dirs:
            recommendations.append(f"No existing test directories found. Suggested: '{suggested}'")
        elif len(test_dirs) == 1:
            recommendations.append(f"Single test directory found: '{test_dirs[0]['path']}' with {test_dirs[0]['test_count']} tests")
        else:
            recommendations.append(f"Multiple test directories found ({len(test_dirs)}). Highest confidence: '{test_dirs[0]['path']}'")
            recommendations.append("Consider consolidating tests into a single directory for consistency")
        
        return recommendations
