"""
Workspace Context Manager for TDD Mastery

Purpose: Integrate with VS Code workspace context (@workspace)
Author: Asif Hussain
Created: 2025-11-24
Version: 1.0

Provides:
- Project structure discovery
- Test/source file mapping
- Test framework detection
- Active file context from editor
"""

from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
import json
import re


class WorkspaceContextManager:
    """
    Workspace context manager for TDD workflow.
    
    Integrates with VS Code @workspace context to provide:
    - Automatic project structure discovery
    - Test/source file mapping
    - Framework detection
    - Active file context
    
    Example:
        workspace = WorkspaceContextManager()
        
        # Discover workspace
        workspace.discover_workspace()
        
        # Get active file from editor
        active_file = workspace.get_active_file_context()
        
        # Map test to source
        source_file = workspace.map_test_to_source("tests/test_login.py")
    """
    
    # Project type indicators
    PROJECT_INDICATORS = {
        'python': [
            'requirements.txt',
            'pyproject.toml',
            'setup.py',
            'Pipfile',
            '*.py'
        ],
        'csharp': [
            '*.csproj',
            '*.sln',
            'Program.cs'
        ],
        'typescript': [
            'package.json',
            'tsconfig.json',
            '*.ts'
        ],
        'javascript': [
            'package.json',
            '*.js'
        ]
    }
    
    # Test framework indicators
    FRAMEWORK_INDICATORS = {
        'pytest': [
            'pytest.ini',
            'pyproject.toml',  # May contain [tool.pytest]
            'setup.cfg',  # May contain [tool:pytest]
            'conftest.py'
        ],
        'unittest': [
            # unittest is built-in, detected by imports
        ],
        'jest': [
            'jest.config.js',
            'jest.config.ts',
            'jest.config.json'
        ],
        'xunit': [
            # Detected by .csproj references
        ]
    }
    
    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize workspace context manager.
        
        Args:
            workspace_root: Explicit workspace root (None = auto-detect)
        """
        self.workspace_root = workspace_root
        self.project_type: Optional[str] = None
        self.test_framework: Optional[str] = None
        self.test_directories: List[Path] = []
        self.source_directories: List[Path] = []
        self.active_file: Optional[Path] = None
        
        # Auto-discover if root provided
        if workspace_root:
            self.discover_workspace()
    
    def discover_workspace(self, provided_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Discover workspace structure.
        
        This method should be called by GitHub Copilot with @workspace context.
        In standalone usage, it analyzes the workspace_root directory.
        
        Args:
            provided_context: Workspace context from GitHub Copilot (@workspace)
            
        Returns:
            Workspace metadata
            {
                'workspace_root': '/path/to/project',
                'project_type': 'python'|'csharp'|'typescript',
                'test_framework': 'pytest'|'jest'|'xunit',
                'test_directories': ['/path/to/tests'],
                'source_directories': ['/path/to/src'],
                'config_files': {
                    'pytest.ini': '/path/to/pytest.ini',
                    'package.json': '/path/to/package.json'
                }
            }
        """
        # Use provided context if available
        if provided_context:
            self.workspace_root = Path(provided_context.get('workspace_root', '.'))
        
        if not self.workspace_root:
            self.workspace_root = Path.cwd()
        
        # Detect project type
        self.project_type = self._detect_project_type()
        
        # Detect test framework
        self.test_framework = self._detect_test_framework()
        
        # Find test and source directories
        self.test_directories = self._find_test_directories()
        self.source_directories = self._find_source_directories()
        
        # Find config files
        config_files = self._find_config_files()
        
        return {
            'workspace_root': str(self.workspace_root),
            'project_type': self.project_type,
            'test_framework': self.test_framework,
            'test_directories': [str(d) for d in self.test_directories],
            'source_directories': [str(d) for d in self.source_directories],
            'config_files': {k: str(v) for k, v in config_files.items()}
        }
    
    def get_active_file_context(self, active_file_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Get context for currently active file in editor.
        
        This method should be called by GitHub Copilot with active file info.
        
        Args:
            active_file_path: Path from GitHub Copilot (@workspace context)
            
        Returns:
            Active file context
            {
                'file_path': '/path/to/file.py',
                'file_type': 'test'|'source',
                'language': 'python'|'csharp'|'typescript',
                'relative_path': 'tests/test_login.py',
                'corresponding_file': '/path/to/src/login.py'  # if test file
            }
        """
        if active_file_path:
            self.active_file = Path(active_file_path)
        
        if not self.active_file:
            return {'error': 'No active file'}
        
        # Determine if test or source file
        is_test = self._is_test_file(self.active_file)
        
        # Get relative path
        try:
            relative_path = self.active_file.relative_to(self.workspace_root)
        except ValueError:
            relative_path = self.active_file
        
        context = {
            'file_path': str(self.active_file),
            'file_type': 'test' if is_test else 'source',
            'language': self.project_type,
            'relative_path': str(relative_path)
        }
        
        # Find corresponding file
        if is_test:
            source_file = self.map_test_to_source(str(self.active_file))
            if source_file:
                context['corresponding_file'] = source_file
        else:
            test_file = self.map_source_to_test(str(self.active_file))
            if test_file:
                context['corresponding_file'] = test_file
        
        return context
    
    def map_test_to_source(self, test_file: str) -> Optional[str]:
        """
        Find source file for test file.
        
        Args:
            test_file: Path to test file
            
        Returns:
            Path to corresponding source file, or None
        """
        test_path = Path(test_file)
        
        # Extract base name (remove test_ prefix and _test suffix)
        base_name = test_path.stem
        base_name = re.sub(r'^test_', '', base_name)
        base_name = re.sub(r'_test$', '', base_name)
        base_name = re.sub(r'\.test$', '', base_name)
        
        # Search in source directories
        for src_dir in self.source_directories:
            # Try same relative structure
            potential_file = src_dir / f"{base_name}{test_path.suffix}"
            if potential_file.exists():
                return str(potential_file)
            
            # Try subdirectories
            for candidate in src_dir.rglob(f"{base_name}{test_path.suffix}"):
                return str(candidate)
        
        return None
    
    def map_source_to_test(self, source_file: str) -> Optional[str]:
        """
        Find test file for source file.
        
        Args:
            source_file: Path to source file
            
        Returns:
            Path to corresponding test file, or None
        """
        source_path = Path(source_file)
        base_name = source_path.stem
        
        # Common test naming patterns
        test_patterns = [
            f"test_{base_name}{source_path.suffix}",
            f"{base_name}_test{source_path.suffix}",
            f"{base_name}.test{source_path.suffix}"
        ]
        
        # Search in test directories
        for test_dir in self.test_directories:
            for pattern in test_patterns:
                # Try same relative structure
                potential_file = test_dir / pattern
                if potential_file.exists():
                    return str(potential_file)
                
                # Try subdirectories
                for candidate in test_dir.rglob(pattern):
                    return str(candidate)
        
        return None
    
    def _detect_project_type(self) -> str:
        """Auto-detect project type from files."""
        scores = {ptype: 0 for ptype in self.PROJECT_INDICATORS}
        
        for ptype, indicators in self.PROJECT_INDICATORS.items():
            for indicator in indicators:
                if '*' in indicator:
                    # Glob pattern
                    if list(self.workspace_root.glob(indicator)):
                        scores[ptype] += 1
                else:
                    # Exact file
                    if (self.workspace_root / indicator).exists():
                        scores[ptype] += 2  # Exact matches score higher
        
        # Return highest scoring type
        if max(scores.values()) == 0:
            return 'unknown'
        
        return max(scores, key=scores.get)
    
    def _detect_test_framework(self) -> str:
        """Auto-detect test framework."""
        if self.project_type == 'python':
            # Check pytest indicators
            for indicator in self.FRAMEWORK_INDICATORS['pytest']:
                if (self.workspace_root / indicator).exists():
                    return 'pytest'
            
            # Check for unittest imports in test files
            test_dirs = self._find_test_directories()
            for test_dir in test_dirs:
                for test_file in test_dir.glob('test_*.py'):
                    content = test_file.read_text()
                    if 'import unittest' in content:
                        return 'unittest'
            
            return 'pytest'  # Default for Python
        
        elif self.project_type in ['typescript', 'javascript']:
            for indicator in self.FRAMEWORK_INDICATORS['jest']:
                if (self.workspace_root / indicator).exists():
                    return 'jest'
            
            # Check package.json
            package_json = self.workspace_root / 'package.json'
            if package_json.exists():
                data = json.loads(package_json.read_text())
                if 'jest' in data.get('devDependencies', {}):
                    return 'jest'
            
            return 'jest'  # Default for JS/TS
        
        elif self.project_type == 'csharp':
            # Check for xunit references in .csproj
            for csproj in self.workspace_root.glob('**/*.csproj'):
                content = csproj.read_text()
                if 'xunit' in content.lower():
                    return 'xunit'
            
            return 'xunit'  # Default for C#
        
        return 'unknown'
    
    def _find_test_directories(self) -> List[Path]:
        """Find directories containing tests."""
        test_dirs = []
        
        # Common test directory names
        test_names = ['tests', 'test', '__tests__', 'spec']
        
        for name in test_names:
            test_dir = self.workspace_root / name
            if test_dir.exists() and test_dir.is_dir():
                test_dirs.append(test_dir)
        
        # Also check for directories with test files
        for path in self.workspace_root.rglob('*'):
            if path.is_dir() and 'test' in path.name.lower():
                if path not in test_dirs:
                    test_dirs.append(path)
        
        return test_dirs
    
    def _find_source_directories(self) -> List[Path]:
        """Find directories containing source code."""
        source_dirs = []
        
        # Common source directory names
        source_names = ['src', 'source', 'lib', 'app']
        
        for name in source_names:
            src_dir = self.workspace_root / name
            if src_dir.exists() and src_dir.is_dir():
                source_dirs.append(src_dir)
        
        # If no explicit src directory, use workspace root
        if not source_dirs:
            source_dirs.append(self.workspace_root)
        
        return source_dirs
    
    def _is_test_file(self, file_path: Path) -> bool:
        """Check if file is a test file."""
        name = file_path.name.lower()
        
        # Common test file patterns
        test_patterns = [
            r'^test_',
            r'_test\.',
            r'\.test\.',
            r'\.spec\.'
        ]
        
        for pattern in test_patterns:
            if re.search(pattern, name):
                return True
        
        # Check if in test directory
        for test_dir in self.test_directories:
            try:
                file_path.relative_to(test_dir)
                return True
            except ValueError:
                continue
        
        return False
    
    def _find_config_files(self) -> Dict[str, Path]:
        """Find configuration files."""
        config_files = {}
        
        # Common config files
        configs = [
            'pytest.ini',
            'pyproject.toml',
            'setup.cfg',
            'jest.config.js',
            'jest.config.ts',
            'package.json',
            'tsconfig.json'
        ]
        
        for config in configs:
            config_path = self.workspace_root / config
            if config_path.exists():
                config_files[config] = config_path
        
        return config_files


# GitHub Copilot Integration Functions

def on_workspace_context_available(workspace_context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Called by GitHub Copilot when @workspace context is available.
    
    Args:
        workspace_context: Workspace context from Copilot
            {
                'workspace_root': '/path/to/project',
                'active_file': '/path/to/current/file.py',
                'open_files': ['/path/to/file1.py', ...]
            }
    
    Returns:
        Discovered workspace metadata
    """
    workspace_root = Path(workspace_context.get('workspace_root', '.'))
    manager = WorkspaceContextManager(workspace_root)
    
    # Set active file if provided
    if 'active_file' in workspace_context:
        manager.active_file = Path(workspace_context['active_file'])
    
    return manager.discover_workspace(workspace_context)
