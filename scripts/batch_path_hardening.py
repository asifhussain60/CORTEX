"""
CORTEX Batch Path Hardening Script

Automatically fixes hardcoded development paths across the codebase.
Replaces Path(__file__).parent.parent.parent patterns with resource_resolver.

Usage:
    # Dry run (preview changes)
    python scripts/batch_path_hardening.py --dry-run
    
    # Apply fixes to specific module
    python scripts/batch_path_hardening.py --module tier1
    
    # Apply all fixes
    python scripts/batch_path_hardening.py --apply-all
    
    # Integration with refinement orchestrator
    from scripts.batch_path_hardening import PathHardeningOrchestrator
    orchestrator = PathHardeningOrchestrator()
    results = orchestrator.execute(dry_run=False)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime
import json
import argparse


@dataclass
class PathReplacement:
    """Represents a single path replacement operation."""
    file_path: Path
    line_number: int
    old_pattern: str
    new_pattern: str
    context_before: str
    context_after: str
    reason: str = ""


@dataclass
class BatchResult:
    """Results from batch path hardening operation."""
    total_files: int = 0
    files_processed: int = 0
    replacements_made: int = 0
    errors: List[str] = field(default_factory=list)
    skipped_files: List[str] = field(default_factory=list)
    replacements: List[PathReplacement] = field(default_factory=list)
    dry_run: bool = True
    

class PathHardeningOrchestrator:
    """
    Orchestrates batch path hardening across CORTEX codebase.
    
    Features:
    - Scans for hardcoded paths
    - Generates appropriate replacements
    - Supports dry-run mode
    - Creates backup before changes
    - Validates replacements
    - Generates detailed report
    """
    
    # Patterns to detect and their replacements
    PATTERNS = {
        # Pattern: (detection_regex, replacement_template, import_needed)
        "project_root": (
            r"Path\(__file__\)\.parent\.parent\.parent",
            "get_root_path()",
            "from src.utils.resource_resolver import get_root_path"
        ),
        "brain_dir": (
            r"Path\(__file__\)\.parent\.parent\.parent\s*/\s*[\"']cortex-brain[\"']",
            "get_brain_path()",
            "from src.utils.resource_resolver import get_brain_path"
        ),
        "brain_file": (
            r"Path\(__file__\)\.parent\.parent\.parent\s*/\s*[\"']cortex-brain[\"']\s*/\s*[\"']([^\"']+)[\"']",
            'get_brain_file("{filename}")',
            "from src.utils.resource_resolver import get_brain_file"
        ),
    }
    
    # Files to skip (already using config.py or correct patterns)
    SKIP_PATTERNS = [
        "*/config.py",  # Uses its own resolution
        "*/resource_resolver.py",  # The utility itself
        "*/test_*.py",  # Test files - validate separately
        "*/__pycache__/*",
        "*/archive/*",
    ]
    
    def __init__(self, root_path: Optional[Path] = None):
        """
        Initialize path hardening orchestrator.
        
        Args:
            root_path: CORTEX root directory (auto-detected if None)
        """
        if root_path is None:
            # Auto-detect from this script's location
            root_path = Path(__file__).parent.parent
        
        self.root_path = root_path.resolve()
        self.src_path = self.root_path / "src"
        self.backup_dir = self.root_path / "cortex-brain" / "backups" / "path-hardening"
        
    def scan_files(self, module: Optional[str] = None) -> List[Path]:
        """
        Scan for Python files with hardcoded paths.
        
        Args:
            module: Specific module to scan (e.g., 'tier1', 'operations')
                   If None, scans all of src/
        
        Returns:
            List of files containing hardcoded paths
        """
        if module:
            search_path = self.src_path / module
        else:
            search_path = self.src_path
        
        if not search_path.exists():
            raise ValueError(f"Module path not found: {search_path}")
        
        files_with_issues = []
        
        for py_file in search_path.rglob("*.py"):
            # Skip files matching skip patterns
            if any(py_file.match(pattern) for pattern in self.SKIP_PATTERNS):
                continue
            
            try:
                content = py_file.read_text(encoding="utf-8")
                
                # Check for any hardcoded path pattern
                for pattern_name, (regex, _, _) in self.PATTERNS.items():
                    if re.search(regex, content):
                        files_with_issues.append(py_file)
                        break
            except Exception as e:
                print(f"Warning: Could not read {py_file}: {e}")
        
        return files_with_issues
    
    def analyze_file(self, file_path: Path) -> List[PathReplacement]:
        """
        Analyze a file and generate replacement operations.
        
        Args:
            file_path: Path to Python file
        
        Returns:
            List of PathReplacement objects
        """
        replacements = []
        
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            
            for line_num, line in enumerate(lines, start=1):
                for pattern_name, (regex, replacement, import_stmt) in self.PATTERNS.items():
                    match = re.search(regex, line)
                    if match:
                        # Extract context (3 lines before and after)
                        context_start = max(0, line_num - 4)
                        context_end = min(len(lines), line_num + 3)
                        context_before = "\n".join(lines[context_start:line_num-1])
                        context_after = "\n".join(lines[line_num:context_end])
                        
                        # Generate replacement
                        if "{filename}" in replacement:
                            # Extract filename from match
                            filename = match.group(1) if match.groups() else ""
                            new_pattern = replacement.format(filename=filename)
                        else:
                            new_pattern = replacement
                        
                        replacements.append(PathReplacement(
                            file_path=file_path,
                            line_number=line_num,
                            old_pattern=line.strip(),
                            new_pattern=line.replace(match.group(0), new_pattern),
                            context_before=context_before,
                            context_after=context_after,
                            reason=f"Replace {pattern_name} with resource_resolver"
                        ))
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
        
        return replacements
    
    def apply_replacements(self, replacements: List[PathReplacement], dry_run: bool = True) -> BatchResult:
        """
        Apply path replacements to files.
        
        Args:
            replacements: List of replacements to apply
            dry_run: If True, only preview changes without applying
        
        Returns:
            BatchResult with operation details
        """
        result = BatchResult(dry_run=dry_run)
        result.replacements = replacements
        
        # Group replacements by file
        files_to_process: Dict[Path, List[PathReplacement]] = {}
        for repl in replacements:
            if repl.file_path not in files_to_process:
                files_to_process[repl.file_path] = []
            files_to_process[repl.file_path].append(repl)
        
        result.total_files = len(files_to_process)
        
        # Create backup if not dry run
        if not dry_run:
            self._create_backup(list(files_to_process.keys()))
        
        # Process each file
        for file_path, file_replacements in files_to_process.items():
            try:
                if dry_run:
                    # Just validate
                    result.files_processed += 1
                    result.replacements_made += len(file_replacements)
                else:
                    # Apply changes
                    success = self._apply_file_replacements(file_path, file_replacements)
                    if success:
                        result.files_processed += 1
                        result.replacements_made += len(file_replacements)
                    else:
                        result.errors.append(f"Failed to apply replacements to {file_path}")
            
            except Exception as e:
                result.errors.append(f"Error processing {file_path}: {e}")
        
        return result
    
    def _apply_file_replacements(self, file_path: Path, replacements: List[PathReplacement]) -> bool:
        """
        Apply replacements to a single file.
        
        Args:
            file_path: File to modify
            replacements: Replacements for this file
        
        Returns:
            True if successful
        """
        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            
            # Apply replacements (in reverse order to preserve line numbers)
            for repl in sorted(replacements, key=lambda r: r.line_number, reverse=True):
                if 0 < repl.line_number <= len(lines):
                    lines[repl.line_number - 1] = repl.new_pattern
            
            # Check if import statement is needed
            import_needed = self._get_needed_import(replacements)
            if import_needed:
                lines = self._add_import_if_missing(lines, import_needed)
            
            # Write back
            new_content = "\n".join(lines)
            file_path.write_text(new_content, encoding="utf-8")
            
            return True
        
        except Exception as e:
            print(f"Error applying replacements to {file_path}: {e}")
            return False
    
    def _get_needed_import(self, replacements: List[PathReplacement]) -> Optional[str]:
        """Determine which import statement is needed."""
        for repl in replacements:
            if "get_root_path()" in repl.new_pattern:
                return "from src.utils.resource_resolver import get_root_path"
            elif "get_brain_path()" in repl.new_pattern:
                return "from src.utils.resource_resolver import get_brain_path"
            elif "get_brain_file(" in repl.new_pattern:
                return "from src.utils.resource_resolver import get_brain_file"
        return None
    
    def _add_import_if_missing(self, lines: List[str], import_stmt: str) -> List[str]:
        """Add import statement if not already present."""
        # Check if already imported
        if any(import_stmt in line for line in lines):
            return lines
        
        # Find where to insert (after last import or docstring)
        insert_pos = 0
        in_docstring = False
        
        for i, line in enumerate(lines):
            stripped = line.strip()
            
            # Track docstring
            if '"""' in stripped or "'''" in stripped:
                in_docstring = not in_docstring
            
            # Find last import
            if not in_docstring and (stripped.startswith("import ") or stripped.startswith("from ")):
                insert_pos = i + 1
        
        # Insert import
        lines.insert(insert_pos, import_stmt)
        return lines
    
    def _create_backup(self, files: List[Path]) -> None:
        """Create backup of files before modification."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"backup_{timestamp}"
        backup_path.mkdir(parents=True, exist_ok=True)
        
        for file_path in files:
            relative_path = file_path.relative_to(self.root_path)
            backup_file = backup_path / relative_path
            backup_file.parent.mkdir(parents=True, exist_ok=True)
            backup_file.write_text(file_path.read_text(encoding="utf-8"), encoding="utf-8")
        
        # Create manifest
        manifest = {
            "timestamp": timestamp,
            "files_backed_up": len(files),
            "files": [str(f.relative_to(self.root_path)) for f in files]
        }
        manifest_file = backup_path / "manifest.json"
        manifest_file.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
        
        print(f"✅ Backup created: {backup_path}")
    
    def execute(self, module: Optional[str] = None, dry_run: bool = True) -> BatchResult:
        """
        Execute batch path hardening.
        
        Args:
            module: Specific module to process (None = all)
            dry_run: Preview changes without applying
        
        Returns:
            BatchResult with operation summary
        """
        print(f"🔍 Scanning for hardcoded paths{' (dry run)' if dry_run else ''}...")
        
        # Scan files
        files_with_issues = self.scan_files(module)
        print(f"📁 Found {len(files_with_issues)} files with hardcoded paths")
        
        if not files_with_issues:
            return BatchResult(dry_run=dry_run)
        
        # Analyze files
        all_replacements = []
        for file_path in files_with_issues:
            replacements = self.analyze_file(file_path)
            all_replacements.extend(replacements)
        
        print(f"🔧 Generated {len(all_replacements)} replacements")
        
        # Apply replacements
        result = self.apply_replacements(all_replacements, dry_run=dry_run)
        
        return result
    
    def generate_report(self, result: BatchResult) -> str:
        """
        Generate detailed report of batch operation.
        
        Args:
            result: BatchResult from execution
        
        Returns:
            Formatted report string
        """
        report = []
        report.append("=" * 80)
        report.append("CORTEX Batch Path Hardening Report")
        report.append("=" * 80)
        report.append(f"Mode: {'DRY RUN (preview only)' if result.dry_run else 'APPLIED'}")
        report.append(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        report.append("📊 Summary:")
        report.append(f"  Total files scanned: {result.total_files}")
        report.append(f"  Files processed: {result.files_processed}")
        report.append(f"  Replacements made: {result.replacements_made}")
        report.append(f"  Errors: {len(result.errors)}")
        report.append(f"  Skipped: {len(result.skipped_files)}")
        report.append("")
        
        if result.errors:
            report.append("❌ Errors:")
            for error in result.errors:
                report.append(f"  - {error}")
            report.append("")
        
        if result.replacements:
            report.append("🔧 Replacements:")
            # Group by file
            files_map: Dict[Path, List[PathReplacement]] = {}
            for repl in result.replacements:
                if repl.file_path not in files_map:
                    files_map[repl.file_path] = []
                files_map[repl.file_path].append(repl)
            
            for file_path, repls in files_map.items():
                report.append(f"\n  {file_path.relative_to(self.root_path)}:")
                for repl in repls:
                    report.append(f"    Line {repl.line_number}:")
                    report.append(f"      OLD: {repl.old_pattern[:60]}...")
                    report.append(f"      NEW: {repl.new_pattern[:60]}...")
        
        report.append("")
        report.append("=" * 80)
        
        return "\n".join(report)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CORTEX Batch Path Hardening - Fix hardcoded development paths"
    )
    parser.add_argument(
        "--module",
        help="Specific module to process (e.g., tier1, operations)",
        default=None
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying (default: True)"
    )
    parser.add_argument(
        "--apply-all",
        action="store_true",
        help="Apply all changes (disables dry-run)"
    )
    
    args = parser.parse_args()
    
    # Determine dry-run mode
    dry_run = not args.apply_all
    
    # Execute
    orchestrator = PathHardeningOrchestrator()
    result = orchestrator.execute(module=args.module, dry_run=dry_run)
    
    # Generate and print report
    report = orchestrator.generate_report(result)
    print(report)
    
    # Save report
    report_dir = orchestrator.root_path / "cortex-brain" / "documents" / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_file = report_dir / f"path-hardening-report-{timestamp}.md"
    report_file.write_text(report, encoding="utf-8")
    print(f"\n📄 Report saved: {report_file}")
    
    # Exit code
    sys.exit(0 if not result.errors else 1)


if __name__ == "__main__":
    main()
