#!/usr/bin/env python3
"""
Instruction File Linter
Enforces CORE-047: No markdown links in instruction files

Detects: [text](path.md) patterns in .github/ instruction files
Auto-fix: Converts to backtick references: `path.md`

Usage:
    python cortex/governance_tools/lint_instruction_files.py [--fix]

Exit codes:
    0 - No violations or all fixed
    1 - Violations found (when --fix not used)
    2 - File system error
"""

import re
import sys
from pathlib import Path
from typing import List, Tuple

# CORE-047 Pattern: [text](path.md) but NOT [text](http://...) or [text](#anchor)
MARKDOWN_LINK_PATTERN = re.compile(
    r'\[([^\]]+)\]\(([^)]+\.md)\)',
    re.MULTILINE
)

# Patterns to exclude (valid markdown links)
EXCLUDE_PATTERNS = [
    re.compile(r'\[.*\]\(https?://.*\)'),  # HTTP/HTTPS links
    re.compile(r'\[.*\]\(#.*\)'),  # Anchor links
    re.compile(r'`\[.*\]\(.*\.md\)`'),  # Backtick-wrapped examples (documentation)
    re.compile(r'NO markdown links `\[text\]\(path\.md\)`'),  # Rule documentation
]

INSTRUCTION_FILE_PATHS = [
    ".github/copilot-instructions.md",
    ".github/prompts/*.md",
    ".github/agents/**/*.md",
]


class InstructionFileLinter:
    """Lints instruction files for CORE-047 violations."""
    
    def __init__(self, root_path: Path, auto_fix: bool = False):
        self.root_path = root_path
        self.auto_fix = auto_fix
        self.violations: List[Tuple[Path, List[Tuple[int, str, str]]]] = []
    
    def should_exclude(self, line: str) -> bool:
        """Check if line matches exclusion patterns."""
        return any(pattern.search(line) for pattern in EXCLUDE_PATTERNS)
    
    def scan_file(self, file_path: Path) -> List[Tuple[int, str, str]]:
        """
        Scan a single file for violations.
        
        Returns:
            List of (line_number, violation_text, suggested_fix)
        """
        violations = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, start=1):
                if self.should_exclude(line):
                    continue
                
                matches = MARKDOWN_LINK_PATTERN.findall(line)
                for text, path in matches:
                    violation = f"[{text}]({path})"
                    suggested_fix = f"`{path}` (load explicitly when needed)"
                    violations.append((line_num, violation, suggested_fix))
        
        except Exception as e:
            print(f"❌ Error reading {file_path}: {e}", file=sys.stderr)
            sys.exit(2)
        
        return violations
    
    def fix_file(self, file_path: Path, violations: List[Tuple[int, str, str]]):
        """Apply auto-fixes to a file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Apply fixes (reverse order to maintain line positions)
            for _, violation, fix in reversed(violations):
                content = content.replace(violation, fix, 1)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"✅ Fixed {len(violations)} violation(s) in {file_path.relative_to(self.root_path)}")
        
        except Exception as e:
            print(f"❌ Error fixing {file_path}: {e}", file=sys.stderr)
            sys.exit(2)
    
    def scan_all(self) -> int:
        """
        Scan all instruction files.
        
        Returns:
            Exit code (0 = success, 1 = violations found)
        """
        print("🔍 CORTEX Instruction File Linter (CORE-047)")
        print("=" * 60)
        
        # Collect all files to scan
        files_to_scan = []
        for pattern in INSTRUCTION_FILE_PATHS:
            if '**' in pattern:
                # Recursive glob
                files_to_scan.extend(self.root_path.glob(pattern))
            elif '*' in pattern:
                # Single-level glob
                files_to_scan.extend(self.root_path.glob(pattern))
            else:
                # Direct path
                file_path = self.root_path / pattern
                if file_path.exists():
                    files_to_scan.append(file_path)
        
        total_violations = 0
        
        for file_path in files_to_scan:
            if not file_path.is_file():
                continue
            
            violations = self.scan_file(file_path)
            if violations:
                total_violations += len(violations)
                self.violations.append((file_path, violations))
                
                print(f"\n📄 {file_path.relative_to(self.root_path)}")
                for line_num, violation, fix in violations:
                    print(f"   Line {line_num}: {violation}")
                    print(f"   Suggested fix: {fix}")
                
                if self.auto_fix:
                    self.fix_file(file_path, violations)
        
        print("\n" + "=" * 60)
        
        if total_violations == 0:
            print("✅ No violations found. All instruction files compliant with CORE-047.")
            return 0
        
        if self.auto_fix:
            print(f"✅ Fixed {total_violations} violation(s) across {len(self.violations)} file(s).")
            return 0
        
        print(f"❌ Found {total_violations} violation(s) across {len(self.violations)} file(s).")
        print("\nTo auto-fix, run: python cortex/governance_tools/lint_instruction_files.py --fix")
        return 1


def main():
    """Main entry point."""
    auto_fix = '--fix' in sys.argv
    
    # Find CORTEX root
    root_path = Path(__file__).resolve().parents[2]  # cortex/governance_tools/... -> CORTEX/
    
    linter = InstructionFileLinter(root_path, auto_fix=auto_fix)
    exit_code = linter.scan_all()
    
    sys.exit(exit_code)


if __name__ == '__main__':
    main()
