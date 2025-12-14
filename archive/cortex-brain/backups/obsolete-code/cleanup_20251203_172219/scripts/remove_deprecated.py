#!/usr/bin/env python3
"""
Deprecated Code Removal Script
Phase 0.4 - Remove @deprecated functions, classes, and update manifest

Usage:
    python scripts/remove_deprecated.py [--directory DIR] [--dry-run] [--no-backup]
"""

import ast
import re
import sys
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional, Set
from datetime import datetime
import argparse
import shutil


class DeprecatedItem:
    """Represents a deprecated code item"""
    
    def __init__(self, file_path: str, item_type: str, name: str, 
                 line_number: int, end_line: int = None):
        self.file = file_path
        self.type = item_type
        self.name = name
        self.line = line_number
        self.end_line = end_line or line_number
    
    def to_dict(self) -> Dict:
        return {
            'file': self.file,
            'type': self.type,
            'name': self.name,
            'line': self.line,
            'end_line': self.end_line
        }
    
    def __repr__(self):
        return f"{self.type} '{self.name}' at {self.file}:{self.line}"


class DeprecatedDetector(ast.NodeVisitor):
    """AST visitor to detect @deprecated decorators"""
    
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.deprecated_items: List[DeprecatedItem] = []
        self.deprecated_names: Set[str] = set()
    
    def _has_deprecated_decorator(self, node) -> bool:
        """Check if node has @deprecated decorator"""
        if not hasattr(node, 'decorator_list'):
            return False
        
        for decorator in node.decorator_list:
            # Handle both @deprecated and @deprecated("reason")
            if isinstance(decorator, ast.Name) and decorator.id == 'deprecated':
                return True
            elif isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name) and decorator.func.id == 'deprecated':
                    return True
        
        return False
    
    def visit_FunctionDef(self, node: ast.FunctionDef):
        """Visit function definitions"""
        if self._has_deprecated_decorator(node):
            # Calculate end line (function body end)
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno
            
            item = DeprecatedItem(
                self.file_path,
                'function',
                node.name,
                node.lineno,
                end_line
            )
            self.deprecated_items.append(item)
            self.deprecated_names.add(node.name)
        
        self.generic_visit(node)
    
    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef):
        """Visit async function definitions"""
        if self._has_deprecated_decorator(node):
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno
            
            item = DeprecatedItem(
                self.file_path,
                'async_function',
                node.name,
                node.lineno,
                end_line
            )
            self.deprecated_items.append(item)
            self.deprecated_names.add(node.name)
        
        self.generic_visit(node)
    
    def visit_ClassDef(self, node: ast.ClassDef):
        """Visit class definitions"""
        if self._has_deprecated_decorator(node):
            end_line = node.end_lineno if hasattr(node, 'end_lineno') else node.lineno
            
            item = DeprecatedItem(
                self.file_path,
                'class',
                node.name,
                node.lineno,
                end_line
            )
            self.deprecated_items.append(item)
            self.deprecated_names.add(node.name)
        
        self.generic_visit(node)


def detect_deprecated_code(code: str, file_path: str = "unknown") -> List[Dict]:
    """
    Detect @deprecated decorators in code.
    
    Args:
        code: Python source code
        file_path: Path to file (for reporting)
    
    Returns:
        List of deprecated item dictionaries
    """
    try:
        tree = ast.parse(code)
        detector = DeprecatedDetector(file_path)
        detector.visit(tree)
        return [item.to_dict() for item in detector.deprecated_items]
    except SyntaxError:
        return []


def detect_todo_references(code: str) -> List[Dict]:
    """
    Detect TODO comments that reference deprecated code.
    
    Args:
        code: Python source code
    
    Returns:
        List of TODO references
    """
    violations = []
    lines = code.split('\n')
    
    # First find deprecated function/class names
    deprecated_names = set()
    try:
        tree = ast.parse(code)
        detector = DeprecatedDetector("temp")
        detector.visit(tree)
        deprecated_names = detector.deprecated_names
    except:
        pass
    
    # Find TODOs that mention deprecated items
    for i, line in enumerate(lines, 1):
        if 'TODO' in line and any(name in line for name in deprecated_names):
            violations.append({
                'line': i,
                'message': 'TODO references deprecated code',
                'comment': line.strip()
            })
    
    return violations


def remove_deprecated_code(code: str, remove_todos: bool = True) -> str:
    """
    Remove deprecated code from source.
    
    Args:
        code: Python source code
        remove_todos: Also remove TODO comments about deprecated code
    
    Returns:
        Cleaned code
    """
    lines = code.split('\n')
    
    # Detect deprecated items
    deprecated_items = detect_deprecated_code(code)
    
    # Mark lines to remove
    lines_to_remove = set()
    for item in deprecated_items:
        # Remove from decorator line to end of definition
        start_line = item['line'] - 1  # Convert to 0-based
        end_line = item['end_line']
        
        # Find the decorator line (look backwards for @deprecated)
        decorator_line = start_line
        for i in range(start_line - 1, max(0, start_line - 10), -1):
            if lines[i].strip().startswith('@deprecated'):
                decorator_line = i
                break
        
        # Mark all lines in range for removal
        for line_num in range(decorator_line, end_line):
            lines_to_remove.add(line_num)
    
    # Remove TODO references if requested
    if remove_todos:
        todo_refs = detect_todo_references(code)
        for ref in todo_refs:
            lines_to_remove.add(ref['line'] - 1)
    
    # Build cleaned code
    cleaned_lines = []
    for i, line in enumerate(lines):
        if i not in lines_to_remove:
            cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def detect_broken_references(code: str, deprecated_names: List[str]) -> List[Dict]:
    """
    Detect references to removed functions/classes.
    
    Args:
        code: Code after removal
        deprecated_names: Names of removed items
    
    Returns:
        List of broken references
    """
    violations = []
    lines = code.split('\n')
    
    for i, line in enumerate(lines, 1):
        # Skip comments and docstrings
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('"""') or stripped.startswith("'''"):
            continue
        
        # Check for references to deprecated names
        for name in deprecated_names:
            # Look for function calls or class instantiation
            if f"{name}(" in line or f" {name}." in line:
                violations.append({
                    'line': i,
                    'message': f'Reference to removed item: {name}',
                    'code': line.strip()
                })
    
    return violations


def validate_syntax(code: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Python syntax.
    
    Args:
        code: Source code
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"


def update_obsolete_manifest(removed_items: List[Dict], 
                             manifest_path: Path = None) -> Dict:
    """
    Update obsolete-tests-manifest.json with removed items.
    
    Args:
        removed_items: List of removed item dictionaries
        manifest_path: Path to manifest file
    
    Returns:
        Updated manifest dictionary
    """
    if manifest_path is None:
        manifest_path = Path("cortex-brain/obsolete-tests-manifest.json")
    
    # Load existing manifest or create new
    if manifest_path.exists():
        try:
            with open(manifest_path, 'r') as f:
                manifest = json.load(f)
            # Ensure 'removed' key exists
            if 'removed' not in manifest:
                manifest['removed'] = []
        except:
            manifest = {
                'version': '1.0',
                'removed': []
            }
    else:
        manifest = {
            'version': '1.0',
            'removed': []
        }
    
    # Add new removals with timestamp
    for item in removed_items:
        item_copy = item.copy()
        item_copy['timestamp'] = datetime.now().isoformat()
        manifest['removed'].append(item_copy)
    
    # Update metadata
    manifest['timestamp'] = datetime.now().isoformat()
    manifest['total_removed'] = len(manifest['removed'])
    
    return manifest


def generate_changelog_entry(removed_items: List[Dict]) -> str:
    """
    Generate CHANGELOG.md entry for breaking changes.
    
    Args:
        removed_items: List of removed items
    
    Returns:
        Markdown formatted changelog entry
    """
    entry_lines = [
        f"## {datetime.now().strftime('%Y-%m-%d')} - BREAKING CHANGES",
        "",
        "### Removed Deprecated Code",
        ""
    ]
    
    # Group by type
    functions = [item for item in removed_items if item['type'] in ('function', 'async_function')]
    classes = [item for item in removed_items if item['type'] == 'class']
    
    if functions:
        entry_lines.append("**Removed Functions:**")
        for item in functions:
            entry_lines.append(f"- `{item['name']}()` from `{item['file']}`")
        entry_lines.append("")
    
    if classes:
        entry_lines.append("**Removed Classes:**")
        for item in classes:
            entry_lines.append(f"- `{item['name']}` from `{item['file']}`")
        entry_lines.append("")
    
    entry_lines.extend([
        "**Migration Guide:**",
        "These deprecated items have been removed. Please update your code to use the recommended alternatives.",
        ""
    ])
    
    return '\n'.join(entry_lines)


def process_directory(directory: Path, dry_run: bool = True, 
                      create_backup: bool = True,
                      remove_todos: bool = True) -> Dict:
    """
    Process all Python files in directory.
    
    Args:
        directory: Root directory
        dry_run: If True, report changes without modifying
        create_backup: Create .bak files
        remove_todos: Also remove TODO references
    
    Returns:
        Statistics dictionary
    """
    stats = {
        'files_processed': 0,
        'files_modified': 0,
        'items_removed': 0,
        'removed_items': [],
        'errors': []
    }
    
    all_deprecated_names = set()
    
    # First pass: detect all deprecated code
    for py_file in directory.rglob("*.py"):
        if '__pycache__' in str(py_file) or 'test' in str(py_file):
            continue
        
        try:
            code = py_file.read_text(encoding='utf-8')
            deprecated = detect_deprecated_code(code, str(py_file))
            
            if deprecated:
                for item in deprecated:
                    all_deprecated_names.add(item['name'])
                    stats['removed_items'].append(item)
        except Exception as e:
            stats['errors'].append(f"{py_file}: {str(e)}")
    
    # Second pass: remove deprecated code and check references
    for py_file in directory.rglob("*.py"):
        if '__pycache__' in str(py_file) or 'test' in str(py_file):
            continue
        
        try:
            original_code = py_file.read_text(encoding='utf-8')
            cleaned_code = remove_deprecated_code(original_code, remove_todos)
            
            stats['files_processed'] += 1
            
            if cleaned_code != original_code:
                stats['files_modified'] += 1
                
                # Validate syntax
                is_valid, error = validate_syntax(cleaned_code)
                if not is_valid:
                    stats['errors'].append(f"{py_file}: {error}")
                    continue
                
                # Check for broken references
                broken_refs = detect_broken_references(cleaned_code, list(all_deprecated_names))
                if broken_refs:
                    for ref in broken_refs:
                        stats['errors'].append(f"{py_file}:{ref['line']} - {ref['message']}")
                
                if not dry_run:
                    # Create backup
                    if create_backup:
                        backup_path = py_file.with_suffix('.py.bak')
                        shutil.copy2(py_file, backup_path)
                    
                    # Write cleaned code
                    py_file.write_text(cleaned_code, encoding='utf-8')
        
        except Exception as e:
            stats['errors'].append(f"{py_file}: {str(e)}")
    
    stats['items_removed'] = len(stats['removed_items'])
    
    return stats


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Remove deprecated code")
    parser.add_argument('--directory', type=str, default='src',
                        help='Directory to process (default: src)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Report changes without modifying files')
    parser.add_argument('--no-backup', action='store_true',
                        help='Do not create .bak files')
    parser.add_argument('--keep-todos', action='store_true',
                        help='Keep TODO comments about deprecated code')
    parser.add_argument('--update-changelog', action='store_true',
                        help='Generate CHANGELOG.md entry')
    
    args = parser.parse_args()
    
    directory = Path(args.directory)
    
    if not directory.exists():
        print(f"ERROR: Directory not found: {directory}")
        sys.exit(1)
    
    print(f"Removing deprecated code from: {directory}")
    print(f"   Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"   Backup: {'No' if args.no_backup else 'Yes'}")
    print(f"   Remove TODOs: {'No' if args.keep_todos else 'Yes'}")
    print()
    
    stats = process_directory(
        directory,
        dry_run=args.dry_run,
        create_backup=not args.no_backup,
        remove_todos=not args.keep_todos
    )
    
    print(f"OK: Processed {stats['files_processed']} files")
    print(f"   Modified: {stats['files_modified']}")
    print(f"   Items removed: {stats['items_removed']}")
    
    if stats['removed_items']:
        print("\nRemoved items:")
        for item in stats['removed_items']:
            print(f"   - {item['type']} '{item['name']}' from {item['file']}:{item['line']}")
    
    if stats['errors']:
        print(f"\nWARNING: Errors:")
        for error in stats['errors']:
            print(f"   {error}")
        sys.exit(1)
    
    # Update manifest if not dry run
    if not args.dry_run and stats['removed_items']:
        manifest = update_obsolete_manifest(stats['removed_items'])
        manifest_path = Path("cortex-brain/obsolete-tests-manifest.json")
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        print(f"\nUpdated manifest: {manifest_path}")
    
    # Generate changelog entry if requested
    if args.update_changelog and stats['removed_items']:
        entry = generate_changelog_entry(stats['removed_items'])
        print("\nCHANGELOG entry:")
        print(entry)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
