"""
MCP Tool: Reference Updater
============================
Parameterized tool for searching and updating file references across the workspace.

Usage via MCP:
    cortex_update_references(
        old_pattern="cortex-ac",
        new_pattern="cortex-ac",
        file_extensions=[".md", ".yaml", ".py", ".json"],
        exclude_dirs=[".git", "__pycache__", "node_modules"],
        dry_run=True
    )

Author: Asif Hussain
Version: 1.0.0
Created: 2026-01-09
"""

import os
import re
import json
from pathlib import Path
from typing import Optional
from dataclasses import dataclass, field


@dataclass
class ReferenceMatch:
    """Represents a single reference match in a file."""
    file_path: str
    line_number: int
    line_content: str
    match_text: str
    context_before: str = ""
    context_after: str = ""


@dataclass
class UpdateResult:
    """Result of a reference update operation."""
    success: bool
    files_scanned: int = 0
    files_with_matches: int = 0
    total_matches: int = 0
    files_updated: int = 0
    matches: list = field(default_factory=list)
    errors: list = field(default_factory=list)
    dry_run: bool = True


class ReferenceUpdater:
    """
    Searches and updates file references across a workspace.
    
    Designed to be used via MCP for automated reference management.
    """
    
    DEFAULT_EXTENSIONS = [".md", ".yaml", ".yml", ".py", ".json", ".txt", ".prompt.md"]
    DEFAULT_EXCLUDES = [".git", "__pycache__", "node_modules", ".venv", "venv", "htmlcov", ".pytest_cache"]
    
    def __init__(
        self,
        workspace_root: str,
        file_extensions: Optional[list] = None,
        exclude_dirs: Optional[list] = None
    ):
        """
        Initialize the reference updater.
        
        Args:
            workspace_root: Root directory to search
            file_extensions: List of file extensions to search (e.g., [".md", ".yaml"])
            exclude_dirs: List of directories to exclude from search
        """
        self.workspace_root = Path(workspace_root)
        self.file_extensions = file_extensions or self.DEFAULT_EXTENSIONS
        self.exclude_dirs = set(exclude_dirs or self.DEFAULT_EXCLUDES)
    
    def _should_process_file(self, file_path: Path) -> bool:
        """Check if a file should be processed based on extension and exclusions."""
        # Check extension
        if not any(file_path.name.endswith(ext) for ext in self.file_extensions):
            return False
        
        # Check exclusions
        for part in file_path.parts:
            if part in self.exclude_dirs:
                return False
        
        return True
    
    def _get_all_files(self) -> list:
        """Get all files to process."""
        files = []
        for file_path in self.workspace_root.rglob("*"):
            if file_path.is_file() and self._should_process_file(file_path):
                files.append(file_path)
        return files
    
    def search(
        self,
        pattern: str,
        use_regex: bool = False,
        context_lines: int = 1
    ) -> UpdateResult:
        """
        Search for references matching the pattern.
        
        Args:
            pattern: Text pattern or regex to search for
            use_regex: Whether to treat pattern as regex
            context_lines: Number of context lines before/after match
            
        Returns:
            UpdateResult with all matches found
        """
        result = UpdateResult(success=True, dry_run=True)
        
        if use_regex:
            regex = re.compile(pattern, re.IGNORECASE)
        else:
            # Escape special regex characters for literal search
            regex = re.compile(re.escape(pattern), re.IGNORECASE)
        
        files = self._get_all_files()
        result.files_scanned = len(files)
        
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    lines = f.readlines()
                
                file_matches = []
                for i, line in enumerate(lines, 1):
                    for match in regex.finditer(line):
                        # Get context
                        ctx_before = ""
                        ctx_after = ""
                        if context_lines > 0:
                            start = max(0, i - 1 - context_lines)
                            end = min(len(lines), i + context_lines)
                            ctx_before = "".join(lines[start:i-1]).rstrip()
                            ctx_after = "".join(lines[i:end]).rstrip()
                        
                        ref_match = ReferenceMatch(
                            file_path=str(file_path.relative_to(self.workspace_root)),
                            line_number=i,
                            line_content=line.rstrip(),
                            match_text=match.group(),
                            context_before=ctx_before,
                            context_after=ctx_after
                        )
                        file_matches.append(ref_match)
                
                if file_matches:
                    result.files_with_matches += 1
                    result.total_matches += len(file_matches)
                    result.matches.extend(file_matches)
                    
            except Exception as e:
                result.errors.append(f"{file_path}: {str(e)}")
        
        return result
    
    def update(
        self,
        old_pattern: str,
        new_pattern: str,
        use_regex: bool = False,
        dry_run: bool = True,
        backup: bool = True
    ) -> UpdateResult:
        """
        Search and replace references.
        
        Args:
            old_pattern: Pattern to find
            new_pattern: Replacement text
            use_regex: Whether to treat old_pattern as regex
            dry_run: If True, don't actually modify files
            backup: If True, create .bak files before modifying
            
        Returns:
            UpdateResult with operation details
        """
        # First search for matches
        search_result = self.search(old_pattern, use_regex)
        
        result = UpdateResult(
            success=True,
            files_scanned=search_result.files_scanned,
            files_with_matches=search_result.files_with_matches,
            total_matches=search_result.total_matches,
            matches=search_result.matches,
            errors=search_result.errors.copy(),
            dry_run=dry_run
        )
        
        if dry_run:
            return result
        
        # Group matches by file
        files_to_update = {}
        for match in search_result.matches:
            if match.file_path not in files_to_update:
                files_to_update[match.file_path] = []
            files_to_update[match.file_path].append(match)
        
        # Update each file
        if use_regex:
            regex = re.compile(old_pattern, re.IGNORECASE)
        else:
            regex = re.compile(re.escape(old_pattern))
        
        for rel_path in files_to_update:
            file_path = self.workspace_root / rel_path
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create backup if requested
                if backup:
                    backup_path = file_path.with_suffix(file_path.suffix + '.bak')
                    with open(backup_path, 'w', encoding='utf-8') as f:
                        f.write(content)
                
                # Replace all occurrences
                if use_regex:
                    new_content = regex.sub(new_pattern, content)
                else:
                    new_content = content.replace(old_pattern, new_pattern)
                
                # Write updated content
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                
                result.files_updated += 1
                
            except Exception as e:
                result.errors.append(f"Failed to update {rel_path}: {str(e)}")
        
        result.success = len(result.errors) == 0
        return result
    
    def to_dict(self, result: UpdateResult) -> dict:
        """Convert UpdateResult to dictionary for JSON serialization."""
        return {
            "success": result.success,
            "dry_run": result.dry_run,
            "files_scanned": result.files_scanned,
            "files_with_matches": result.files_with_matches,
            "total_matches": result.total_matches,
            "files_updated": result.files_updated,
            "matches": [
                {
                    "file": m.file_path,
                    "line": m.line_number,
                    "content": m.line_content,
                    "match": m.match_text
                }
                for m in result.matches
            ],
            "errors": result.errors
        }


# MCP Tool Functions
def cortex_search_references(
    workspace_root: str,
    pattern: str,
    file_extensions: Optional[list] = None,
    exclude_dirs: Optional[list] = None,
    use_regex: bool = False
) -> dict:
    """
    MCP Tool: Search for references matching a pattern.
    
    Args:
        workspace_root: Root directory to search
        pattern: Text or regex pattern to find
        file_extensions: File types to search (default: .md, .yaml, .py, .json)
        exclude_dirs: Directories to skip (default: .git, __pycache__, etc.)
        use_regex: Treat pattern as regex
        
    Returns:
        Dictionary with search results
    """
    updater = ReferenceUpdater(
        workspace_root=workspace_root,
        file_extensions=file_extensions,
        exclude_dirs=exclude_dirs
    )
    result = updater.search(pattern, use_regex)
    return updater.to_dict(result)


def cortex_update_references(
    workspace_root: str,
    old_pattern: str,
    new_pattern: str,
    file_extensions: Optional[list] = None,
    exclude_dirs: Optional[list] = None,
    use_regex: bool = False,
    dry_run: bool = True,
    backup: bool = True
) -> dict:
    """
    MCP Tool: Search and replace references across workspace.
    
    Args:
        workspace_root: Root directory to search
        old_pattern: Text or regex pattern to find
        new_pattern: Replacement text
        file_extensions: File types to search (default: .md, .yaml, .py, .json)
        exclude_dirs: Directories to skip (default: .git, __pycache__, etc.)
        use_regex: Treat patterns as regex
        dry_run: If True, show changes without applying (default: True)
        backup: Create .bak files before modifying (default: True)
        
    Returns:
        Dictionary with operation results
    """
    updater = ReferenceUpdater(
        workspace_root=workspace_root,
        file_extensions=file_extensions,
        exclude_dirs=exclude_dirs
    )
    result = updater.update(old_pattern, new_pattern, use_regex, dry_run, backup)
    return updater.to_dict(result)


# CLI interface for direct execution
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Search and update file references")
    parser.add_argument("--workspace", "-w", required=True, help="Workspace root directory")
    parser.add_argument("--search", "-s", help="Pattern to search for")
    parser.add_argument("--replace", "-r", help="Replacement pattern (if updating)")
    parser.add_argument("--regex", action="store_true", help="Treat patterns as regex")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Preview changes without applying")
    parser.add_argument("--apply", action="store_true", help="Apply changes (opposite of dry-run)")
    parser.add_argument("--no-backup", action="store_true", help="Don't create backup files")
    parser.add_argument("--extensions", "-e", nargs="+", help="File extensions to search")
    parser.add_argument("--exclude", "-x", nargs="+", help="Directories to exclude")
    parser.add_argument("--json", action="store_true", help="Output as JSON")
    
    args = parser.parse_args()
    
    if not args.search:
        parser.error("--search pattern is required")
    
    dry_run = not args.apply
    
    if args.replace:
        result = cortex_update_references(
            workspace_root=args.workspace,
            old_pattern=args.search,
            new_pattern=args.replace,
            file_extensions=args.extensions,
            exclude_dirs=args.exclude,
            use_regex=args.regex,
            dry_run=dry_run,
            backup=not args.no_backup
        )
    else:
        result = cortex_search_references(
            workspace_root=args.workspace,
            pattern=args.search,
            file_extensions=args.extensions,
            exclude_dirs=args.exclude,
            use_regex=args.regex
        )
    
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"\n{'='*60}")
        print(f"Reference {'Search' if not args.replace else 'Update'} Results")
        print(f"{'='*60}")
        print(f"Files scanned: {result['files_scanned']}")
        print(f"Files with matches: {result['files_with_matches']}")
        print(f"Total matches: {result['total_matches']}")
        if args.replace:
            print(f"Files updated: {result['files_updated']}")
            print(f"Dry run: {result['dry_run']}")
        print(f"\nMatches:")
        for m in result['matches'][:50]:  # Limit output
            print(f"  {m['file']}:{m['line']} - {m['match']}")
        if len(result['matches']) > 50:
            print(f"  ... and {len(result['matches']) - 50} more")
        if result['errors']:
            print(f"\nErrors:")
            for e in result['errors']:
                print(f"  {e}")
