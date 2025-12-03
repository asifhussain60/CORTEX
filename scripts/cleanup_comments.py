#!/usr/bin/env python3
"""
Comment Cleanup Script
Phase 0.3 - Remove unnecessary comments, update docstrings to Google style

Usage:
    python scripts/cleanup_comments.py [--directory DIR] [--dry-run]
"""

import ast
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Optional
import argparse
import shutil


# Patterns for obvious comments
OBVIOUS_PATTERNS = [
    r"^# (Create|Initialize|Set|Get|Return|Define|Declare) ",
    r"^# (Loop|Iterate|Check|Validate|Calculate|Process) ",
    r"^# Variable",
    r"^# Function",
    r"^# Class",
    r"^# Import",
]

# Patterns for vague TODOs
VAGUE_TODO_PATTERNS = [
    r"TODO:?\s+(fix\s+(this|it)?|this|later|implement)$",
    r"TODO\s*$",
]


class CommentViolation:
    """Represents a comment issue"""
    
    def __init__(self, line_number: int, message: str, comment_text: str = ""):
        self.line = line_number
        self.message = message
        self.comment = comment_text
    
    def to_dict(self) -> Dict:
        return {
            'line': self.line,
            'message': self.message,
            'comment': self.comment
        }
    
    def __repr__(self):
        return f"Line {self.line}: {self.message}"


def detect_obvious_comments(code: str) -> List[Dict]:
    """Detect obvious/redundant comments that can be removed"""
    violations = []
    lines = code.split('\n')
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        # Skip docstrings (lines within triple quotes)
        if '"""' in line or "'''" in line:
            continue
        
        # Check for obvious comment patterns
        if stripped.startswith('#'):
            comment_text = stripped
            
            # Check each pattern
            for pattern in OBVIOUS_PATTERNS:
                if re.match(pattern, comment_text, re.IGNORECASE):
                    # Check if it's actually explaining complex logic
                    # (Complex comments typically have multiple sentences or technical terms)
                    if len(comment_text) > 50 or any(word in comment_text.lower() for word in 
                                                      ['algorithm', 'optimization', 'complexity', 'performance',
                                                       'workaround', 'bug', 'edge case', 'note:']):
                        continue
                    
                    violations.append({
                        'line': i,
                        'message': 'Obvious comment',
                        'comment': comment_text
                    })
                    break
    
    return violations


def detect_commented_code(code: str) -> List[Dict]:
    """Detect commented-out code blocks"""
    violations = []
    lines = code.split('\n')
    
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        # Look for commented code patterns
        if line.startswith('#'):
            # Check if it looks like code (has Python syntax elements)
            code_patterns = [
                r'# *def ',
                r'# *class ',
                r'# *import ',
                r'# *from ',
                r'# *return ',
                r'# *if ',
                r'# *for ',
                r'# *while ',
                r'# *\w+ *= *',  # assignments
            ]
            
            if any(re.match(pattern, line) for pattern in code_patterns):
                # Found start of commented code block
                block_start = i + 1
                block_lines = [line]
                
                # Find extent of block
                j = i + 1
                while j < len(lines):
                    next_line = lines[j].strip()
                    if next_line.startswith('#') or next_line == '':
                        if next_line.startswith('#'):
                            block_lines.append(next_line)
                        j += 1
                    else:
                        break
                
                if len(block_lines) >= 2:  # At least 2 lines of commented code
                    violations.append({
                        'line': block_start,
                        'message': f'Commented-out code block ({len(block_lines)} lines)',
                        'comment': '\n'.join(block_lines[:3]) + '...'
                    })
                
                i = j
                continue
        
        i += 1
    
    return violations


def detect_incomplete_todos(code: str) -> List[Dict]:
    """Detect TODO comments without sufficient context"""
    violations = []
    lines = code.split('\n')
    
    for i, line in enumerate(lines, 1):
        stripped = line.strip()
        
        if 'TODO' in stripped:
            # Check if it's vague
            for pattern in VAGUE_TODO_PATTERNS:
                if re.search(pattern, stripped, re.IGNORECASE):
                    violations.append({
                        'line': i,
                        'message': 'Vague TODO comment (add specific context)',
                        'comment': stripped
                    })
                    break
    
    return violations


def validate_docstrings(code: str) -> List[Dict]:
    """Validate docstring format (should be Google style)"""
    violations = []
    
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return violations
    
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            docstring = ast.get_docstring(node)
            
            # Check for missing docstrings in public functions
            if not node.name.startswith('_') and not docstring:
                violations.append({
                    'line': node.lineno,
                    'message': f'Public function "{node.name}" missing docstring',
                    'comment': ''
                })
                continue
            
            if docstring:
                # Check for non-Google style markers
                if '@param' in docstring or '@return' in docstring or ':param' in docstring:
                    violations.append({
                        'line': node.lineno,
                        'message': f'Function "{node.name}" uses non-Google style docstring',
                        'comment': '@param/@return style detected'
                    })
    
    return violations


def cleanup_file(code: str, remove_obvious: bool = True, 
                 remove_commented_code: bool = True,
                 remove_vague_todos: bool = True) -> str:
    """
    Clean up comments in code while preserving structure.
    
    Args:
        code: Source code string
        remove_obvious: Remove obvious comments
        remove_commented_code: Remove commented-out code
        remove_vague_todos: Remove vague TODO comments
    
    Returns:
        Cleaned code string
    """
    lines = code.split('\n')
    cleaned_lines = []
    
    # Get violations
    obvious = set(v['line'] for v in detect_obvious_comments(code)) if remove_obvious else set()
    vague_todos = set(v['line'] for v in detect_incomplete_todos(code)) if remove_vague_todos else set()
    
    # Handle commented code separately (it's multi-line)
    commented_blocks = []
    if remove_commented_code:
        violations = detect_commented_code(code)
        for v in violations:
            # Mark range of lines to remove
            start = v['line'] - 1  # Convert to 0-based
            # Find block extent
            for i in range(start, len(lines)):
                line = lines[i].strip()
                if line.startswith('#') or line == '':
                    commented_blocks.append(i)
                else:
                    break
    
    # Process each line
    for i, line in enumerate(lines):
        line_num = i + 1
        
        # Skip if part of commented code block
        if i in commented_blocks:
            continue
        
        # Skip if obvious or vague TODO
        if line_num in obvious or line_num in vague_todos:
            continue
        
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)


def validate_syntax(code: str) -> Tuple[bool, Optional[str]]:
    """
    Validate Python syntax.
    
    Args:
        code: Source code string
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        ast.parse(code)
        return True, None
    except SyntaxError as e:
        return False, f"Syntax error at line {e.lineno}: {e.msg}"


def cleanup_directory(directory: Path, dry_run: bool = True, 
                      create_backup: bool = True) -> Dict:
    """
    Clean up all Python files in directory.
    
    Args:
        directory: Root directory to process
        dry_run: If True, only report what would be changed
        create_backup: If True, create .bak files before modification
    
    Returns:
        Dictionary with statistics
    """
    stats = {
        'files_processed': 0,
        'files_modified': 0,
        'comments_removed': 0,
        'errors': []
    }
    
    for py_file in directory.rglob("*.py"):
        # Skip test files and generated files
        if 'test' in str(py_file) or '__pycache__' in str(py_file):
            continue
        
        try:
            original_code = py_file.read_text(encoding='utf-8')
            cleaned_code = cleanup_file(original_code)
            
            stats['files_processed'] += 1
            
            if cleaned_code != original_code:
                stats['files_modified'] += 1
                
                # Count removed lines
                original_lines = len(original_code.split('\n'))
                cleaned_lines = len(cleaned_code.split('\n'))
                stats['comments_removed'] += (original_lines - cleaned_lines)
                
                # Validate syntax
                is_valid, error = validate_syntax(cleaned_code)
                if not is_valid:
                    stats['errors'].append(f"{py_file}: {error}")
                    continue
                
                if not dry_run:
                    # Create backup
                    if create_backup:
                        backup_path = py_file.with_suffix('.py.bak')
                        shutil.copy2(py_file, backup_path)
                    
                    # Write cleaned code
                    py_file.write_text(cleaned_code, encoding='utf-8')
        
        except Exception as e:
            stats['errors'].append(f"{py_file}: {str(e)}")
    
    return stats


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="Clean up Python comments")
    parser.add_argument('--directory', type=str, default='src',
                        help='Directory to process (default: src)')
    parser.add_argument('--dry-run', action='store_true',
                        help='Report what would be changed without modifying files')
    parser.add_argument('--no-backup', action='store_true',
                        help='Do not create .bak files')
    
    args = parser.parse_args()
    
    directory = Path(args.directory)
    
    if not directory.exists():
        print(f"ERROR: Directory not found: {directory}")
        sys.exit(1)
    
    print(f"Cleaning comments in: {directory}")
    print(f"   Mode: {'DRY RUN' if args.dry_run else 'LIVE'}")
    print(f"   Backup: {'No' if args.no_backup else 'Yes'}")
    print()
    
    stats = cleanup_directory(
        directory,
        dry_run=args.dry_run,
        create_backup=not args.no_backup
    )
    
    print(f"OK: Processed {stats['files_processed']} files")
    print(f"   Modified: {stats['files_modified']}")
    print(f"   Comments removed: {stats['comments_removed']}")
    
    if stats['errors']:
        print(f"\nWARNING: Errors:")
        for error in stats['errors']:
            print(f"   {error}")
        sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
