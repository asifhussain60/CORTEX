"""
Debug Marker System

Provides utilities for inserting, tracking, and removing debug markers during development.
Part of Phase 0 Deliverable 0.1 - Foundation: Code Quality & Debugging

Debug markers help developers track execution flow and identify issues during development,
but must never reach production code. This system enforces automatic removal via git hooks
and SKULL protection rules.

Marker Types:
- MARKER: General execution point marker
- DEBUG: Debug-specific code that needs removal
- FIXME: Temporary fixes requiring proper implementation
- TODO: Incomplete implementations
- BREAKPOINT: Execution pause points for debugging

Usage:
    from src.utils.debug_markers import insert_marker, log_marker_hit
    
    # Insert a marker (automatically logged when reached)
    insert_marker("user_validation", "Checking user permissions")
    
    # Log when a marker is hit during execution
    log_marker_hit("user_validation", {"user_id": 123, "role": "admin"})

Author: Asif Hussain
License: Source-Available (Use Allowed, No Contributions)
"""

import re
import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging

# Configure logging
logger = logging.getLogger(__name__)


class MarkerType:
    """Enumeration of debug marker types."""
    MARKER = "MARKER"
    DEBUG = "DEBUG"
    FIXME = "FIXME"
    TODO = "TODO"
    BREAKPOINT = "BREAKPOINT"
    
    @classmethod
    def all_types(cls) -> List[str]:
        """Return all marker types."""
        return [cls.MARKER, cls.DEBUG, cls.FIXME, cls.TODO, cls.BREAKPOINT]


class DebugMarker:
    """Represents a single debug marker found in code."""
    
    def __init__(
        self,
        marker_type: str,
        file_path: str,
        line_number: int,
        content: str,
        context: str = ""
    ):
        """
        Initialize a debug marker.
        
        Args:
            marker_type: Type of marker (MARKER, DEBUG, etc.)
            file_path: Path to file containing marker
            line_number: Line number where marker appears
            content: Full content of the line with marker
            context: Optional context or description
        """
        self.marker_type = marker_type
        self.file_path = file_path
        self.line_number = line_number
        self.content = content.strip()
        self.context = context
        self.detected_at = datetime.now()
    
    def __str__(self) -> str:
        """String representation for display."""
        return f"{self.file_path}:{self.line_number} [{self.marker_type}] {self.content}"
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for reporting."""
        return {
            "marker_type": self.marker_type,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "content": self.content,
            "context": self.context,
            "detected_at": self.detected_at.isoformat()
        }


def insert_marker(
    marker_id: str,
    description: str = "",
    marker_type: str = MarkerType.MARKER
) -> None:
    """
    Insert a debug marker at the current execution point.
    
    This function is for runtime marker insertion during development.
    It logs the marker hit immediately and can be used to trace execution flow.
    
    Args:
        marker_id: Unique identifier for the marker
        description: Optional description of what's being marked
        marker_type: Type of marker (default: MARKER)
    
    Example:
        insert_marker("auth_check", "Validating user credentials")
    """
    frame = sys._getframe(1)
    file_path = frame.f_code.co_filename
    line_number = frame.f_lineno
    
    log_entry = {
        "marker_id": marker_id,
        "marker_type": marker_type,
        "description": description,
        "file": file_path,
        "line": line_number,
        "timestamp": datetime.now().isoformat()
    }
    
    logger.debug(f"[{marker_type}] {marker_id} at {file_path}:{line_number} - {description}")
    
    # In development mode, also print to stdout for visibility
    if os.environ.get("CORTEX_DEBUG_MODE") == "1":
        print(f"🔍 [{marker_type}] {marker_id}: {description} ({file_path}:{line_number})")


def log_marker_hit(marker_id: str, context: Optional[Dict] = None) -> None:
    """
    Log when a previously defined marker is hit during execution.
    
    Args:
        marker_id: Identifier of the marker being hit
        context: Optional context data to log with the marker
    
    Example:
        log_marker_hit("auth_check", {"user_id": 123, "role": "admin"})
    """
    frame = sys._getframe(1)
    file_path = frame.f_code.co_filename
    line_number = frame.f_lineno
    
    log_entry = {
        "marker_id": marker_id,
        "hit_at": datetime.now().isoformat(),
        "file": file_path,
        "line": line_number,
        "context": context or {}
    }
    
    logger.debug(f"Marker hit: {marker_id} at {file_path}:{line_number}")
    
    if os.environ.get("CORTEX_DEBUG_MODE") == "1":
        context_str = f" | {context}" if context else ""
        print(f"✓ Marker '{marker_id}' hit{context_str}")


def scan_for_markers(
    directory: str,
    file_extensions: Optional[List[str]] = None
) -> List[DebugMarker]:
    """
    Scan directory for debug markers in source files.
    
    Args:
        directory: Root directory to scan
        file_extensions: List of file extensions to scan (default: ['.py'])
    
    Returns:
        List of DebugMarker objects found
    
    Example:
        markers = scan_for_markers("src/", [".py"])
        for marker in markers:
            print(f"Found: {marker}")
    """
    if file_extensions is None:
        file_extensions = ['.py']
    
    markers = []
    directory_path = Path(directory)
    
    # Build regex pattern for all marker types
    marker_patterns = [
        rf'#\s*({marker_type}):?\s*(.*)' 
        for marker_type in MarkerType.all_types()
    ]
    combined_pattern = '|'.join(marker_patterns)
    regex = re.compile(combined_pattern, re.IGNORECASE)
    
    # Scan all files with specified extensions
    for ext in file_extensions:
        for file_path in directory_path.rglob(f"*{ext}"):
            # Skip virtual environments and cache directories
            if any(part in file_path.parts for part in ['venv', '__pycache__', '.git', 'node_modules']):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for line_num, line in enumerate(lines, start=1):
                    match = regex.search(line)
                    if match:
                        # Determine which marker type matched
                        marker_type = None
                        context = ""
                        
                        for i, group in enumerate(match.groups()):
                            if group and group.upper() in MarkerType.all_types():
                                marker_type = group.upper()
                                # Context is in the next group
                                if i + 1 < len(match.groups()):
                                    context = match.groups()[i + 1] or ""
                                break
                        
                        if marker_type:
                            marker = DebugMarker(
                                marker_type=marker_type,
                                file_path=str(file_path),
                                line_number=line_num,
                                content=line.strip(),
                                context=context.strip()
                            )
                            markers.append(marker)
            
            except Exception as e:
                logger.warning(f"Error scanning {file_path}: {e}")
                continue
    
    return markers


def remove_markers(
    file_path: str,
    dry_run: bool = False
) -> Tuple[int, List[str]]:
    """
    Remove all debug markers from a specific file.
    
    Args:
        file_path: Path to file to clean
        dry_run: If True, don't modify file, just report what would be removed
    
    Returns:
        Tuple of (number of markers removed, list of removed line contents)
    
    Example:
        count, removed = remove_markers("src/main.py", dry_run=True)
        print(f"Would remove {count} markers: {removed}")
    """
    removed_lines = []
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Build regex for marker detection
        marker_patterns = [
            rf'#\s*({marker_type}):?\s*' 
            for marker_type in MarkerType.all_types()
        ]
        combined_pattern = '|'.join(marker_patterns)
        regex = re.compile(combined_pattern, re.IGNORECASE)
        
        # Filter out lines with markers
        cleaned_lines = []
        for line in lines:
            if regex.search(line):
                removed_lines.append(line.strip())
            else:
                cleaned_lines.append(line)
        
        # Write cleaned content if not dry run
        if not dry_run and removed_lines:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(cleaned_lines)
        
        return len(removed_lines), removed_lines
    
    except Exception as e:
        logger.error(f"Error removing markers from {file_path}: {e}")
        return 0, []


def generate_marker_report(markers: List[DebugMarker]) -> str:
    """
    Generate a formatted report of all markers found.
    
    Args:
        markers: List of DebugMarker objects
    
    Returns:
        Formatted string report
    """
    if not markers:
        return "✓ No debug markers found."
    
    report = [
        f"⚠️  Found {len(markers)} debug marker(s):\n",
        "=" * 80
    ]
    
    # Group by marker type
    by_type = {}
    for marker in markers:
        if marker.marker_type not in by_type:
            by_type[marker.marker_type] = []
        by_type[marker.marker_type].append(marker)
    
    # Generate report by type
    for marker_type, type_markers in sorted(by_type.items()):
        report.append(f"\n{marker_type} markers ({len(type_markers)}):")
        report.append("-" * 80)
        
        for marker in sorted(type_markers, key=lambda m: (m.file_path, m.line_number)):
            report.append(f"  {marker.file_path}:{marker.line_number}")
            report.append(f"    {marker.content}")
            if marker.context:
                report.append(f"    Context: {marker.context}")
            report.append("")
    
    report.append("=" * 80)
    report.append("\n⛔ These markers must be removed before committing.")
    
    return "\n".join(report)


def check_markers_in_files(file_paths: List[str]) -> Tuple[bool, str]:
    """
    Check if any of the provided files contain debug markers.
    
    Used by git pre-commit hook to block commits with markers.
    
    Args:
        file_paths: List of file paths to check
    
    Returns:
        Tuple of (has_markers: bool, report: str)
    """
    all_markers = []
    
    for file_path in file_paths:
        if file_path.endswith('.py'):
            file_markers = scan_for_markers(
                os.path.dirname(file_path) or '.',
                ['.py']
            )
            # Filter to only markers from this specific file
            file_markers = [m for m in file_markers if m.file_path == file_path]
            all_markers.extend(file_markers)
    
    if all_markers:
        report = generate_marker_report(all_markers)
        return True, report
    else:
        return False, "✓ No debug markers found in staged files."


if __name__ == "__main__":
    """CLI interface for debug marker utilities."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Debug Marker System Utilities")
    parser.add_argument(
        "command",
        choices=["scan", "remove", "report"],
        help="Command to execute"
    )
    parser.add_argument(
        "path",
        help="File or directory path"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes"
    )
    
    args = parser.parse_args()
    
    if args.command == "scan":
        markers = scan_for_markers(args.path)
        print(generate_marker_report(markers))
    
    elif args.command == "remove":
        if os.path.isfile(args.path):
            count, removed = remove_markers(args.path, dry_run=args.dry_run)
            if args.dry_run:
                print(f"Would remove {count} markers from {args.path}")
            else:
                print(f"Removed {count} markers from {args.path}")
            for line in removed:
                print(f"  - {line}")
        else:
            print(f"Error: {args.path} is not a file")
    
    elif args.command == "report":
        markers = scan_for_markers(args.path)
        print(generate_marker_report(markers))
