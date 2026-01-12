#!/usr/bin/env python3
"""
Import Pattern Validator - Prevent Design Brittleness

Validates that imports follow consistent patterns:
1. Cross-package imports use absolute paths (from src.X import Y)
2. No infrastructure imports use relative paths
3. No ".infrastructure" pattern (use "src.infrastructure")
4. Relative imports only within same package

Author: GitHub Copilot (for CORTEX)
Created: 2026-01-12
AC-ID: AC-CODE-QUALITY-001
"""

import sys
from pathlib import Path
from typing import List, Tuple
import re


class ImportValidator:
    """Validates import patterns for brittleness"""
    
    # Design rules
    RULES = {
        'infrastructure_absolute': {
            'pattern': r'from (\.+)(infrastructure|src\.infrastructure)',
            'error': 'infrastructure imports must use absolute path (from src.infrastructure.*)',
            'severity': 'ERROR',
        },
        'cross_package_absolute': {
            'pattern': r'from \.{3,}',
            'error': '3+ dot imports indicate crossing packages - use absolute imports',
            'severity': 'WARNING',
        },
        'mixed_patterns_in_file': {
            'check': 'mixed_absolute_relative',
            'error': 'File mixes absolute and relative imports - standardize to absolute',
            'severity': 'WARNING',
        },
    }
    
    def __init__(self, src_root: Path = None):
        """Initialize validator"""
        self.src_root = src_root or Path('src')
        self.errors = []
        self.warnings = []
    
    def validate_file(self, file_path: Path) -> bool:
        """Validate single file for import brittleness"""
        try:
            content = file_path.read_text()
        except Exception as e:
            self.errors.append((file_path, 0, f"Cannot read file: {e}"))
            return False
        
        lines = content.split('\n')
        has_absolute = False
        has_relative = False
        
        for line_num, line in enumerate(lines, 1):
            line_stripped = line.strip()
            
            if not line_stripped.startswith('from ') or 'import' not in line_stripped:
                continue
            
            # Skip stdlib and third-party imports (no dots after 'from ')
            if line_stripped.startswith('from ') and not line_stripped.startswith('from .') and not line_stripped.startswith('from src.'):
                continue
            
            # Track pattern types
            if line_stripped.startswith('from src.'):
                has_absolute = True
            elif line_stripped.startswith('from .'):
                has_relative = True
            
            # Rule 1: infrastructure must be absolute
            if 'infrastructure' in line_stripped and line_stripped.startswith('from .'):
                self.errors.append((
                    file_path, line_num,
                    f"❌ Infrastructure import must be absolute: {line_stripped[:70]}"
                ))
                return False
            
            # Rule 2: 3+ dots are brittle (crossing packages)
            if line_stripped.startswith('from .'):
                dots = len(line_stripped.split()[1]) - len(line_stripped.split()[1].lstrip('.'))
                if dots >= 3:
                    self.warnings.append((
                        file_path, line_num,
                        f"⚠️  {dots}-dot import (crosses packages): {line_stripped[:70]}"
                    ))
        
        # Rule 3: mixed patterns - only warn if crossing packages
        if has_absolute and has_relative:
            # Check if relative imports are local to same package (acceptable pattern)
            relative_imports = [l for l in lines if l.strip().startswith('from .')]
            absolute_imports = [l for l in lines if l.strip().startswith('from src.')]
            
            # Pattern: Local relative + cross-package absolute is OK
            # e.g., "from .local_module" + "from src.other_package"
            
            # Only flag as error if relative imports are trying to cross packages
            has_cross_package_relative = any(l.count('.') > 1 for l in relative_imports)
            
            if has_absolute and has_cross_package_relative:
                self.warnings.append((
                    file_path, 0,
                    f"⚠️  File mixes local and cross-package imports - consider standardizing"
                ))
        
        return len([e for e in self.errors if e[0] == file_path]) == 0
    
    def validate_directory(self, directory: Path = None) -> bool:
        """Validate all Python files in directory"""
        directory = directory or self.src_root
        
        py_files = list(directory.rglob('*.py'))
        
        print(f"Validating {len(py_files)} Python files...")
        
        for py_file in sorted(py_files):
            if '__pycache__' in str(py_file):
                continue
            self.validate_file(py_file)
        
        return len(self.errors) == 0
    
    def report(self) -> str:
        """Generate validation report"""
        report_lines = []
        
        if self.errors:
            report_lines.append("\n❌ ERRORS (Import Brittleness)")
            report_lines.append("=" * 70)
            for file_path, line_num, msg in self.errors:
                report_lines.append(f"{file_path}:{line_num}: {msg}")
        
        if self.warnings:
            report_lines.append("\n⚠️  WARNINGS (Design Improvements)")
            report_lines.append("=" * 70)
            for file_path, line_num, msg in self.warnings:
                if line_num > 0:
                    report_lines.append(f"{file_path}:{line_num}: {msg}")
                else:
                    report_lines.append(f"{file_path}: {msg}")
        
        if not self.errors and not self.warnings:
            report_lines.append("\n✓ All imports follow design patterns")
        
        return '\n'.join(report_lines)
    
    def exit_code(self) -> int:
        """Return appropriate exit code"""
        if self.errors:
            return 1  # Critical brittleness
        if self.warnings:
            return 0  # Warnings only (allow commit)
        return 0


def main():
    """CLI entry point"""
    validator = ImportValidator()
    
    # Validate src/orchestrators/core first (critical path)
    print("🔍 Validating critical path: src/orchestrators/core/")
    core_path = Path('src/orchestrators/core')
    if core_path.exists():
        for py_file in sorted(core_path.glob('*.py')):
            if py_file.name == '__init__.py':
                continue
            validator.validate_file(py_file)
    
    # Then validate all of src/
    print("🔍 Validating full src/ directory...")
    validator.validate_directory()
    
    # Report
    print(validator.report())
    
    # Exit with appropriate code
    sys.exit(validator.exit_code())


if __name__ == '__main__':
    main()
