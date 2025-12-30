#!/usr/bin/env python3
"""
CORTEX Cache Cleaner - Clear VS Code and Python caches

Clears all cache directories for a fresh workspace state:
- VS Code caches (Cache, CachedData, CachedExtensions)
- Python __pycache__ directories
- pytest and mypy caches
- Workspace-specific caches

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import os
import sys
import shutil
import platform
from pathlib import Path
from typing import List, Tuple
import argparse


def get_vscode_cache_paths() -> List[Path]:
    """Get VS Code cache directory paths based on OS."""
    system = platform.system()
    paths = []
    
    if system == "Darwin":  # macOS
        base = Path.home() / "Library" / "Application Support" / "Code"
        paths = [
            base / "Cache",
            base / "CachedData",
            base / "CachedExtensions",
            base / "CachedExtensionVSIXs",
            base / "logs",
        ]
    elif system == "Windows":
        appdata = Path(os.environ.get("APPDATA", ""))
        paths = [
            appdata / "Code" / "Cache",
            appdata / "Code" / "CachedData",
            appdata / "Code" / "CachedExtensions",
            appdata / "Code" / "CachedExtensionVSIXs",
            appdata / "Code" / "logs",
        ]
    elif system == "Linux":
        config = Path.home() / ".config" / "Code"
        paths = [
            config / "Cache",
            config / "CachedData",
            config / "CachedExtensions",
            config / "CachedExtensionVSIXs",
            config / "logs",
        ]
    
    return [p for p in paths if p.exists()]


def get_workspace_cache_paths(workspace_root: Path) -> List[Path]:
    """Get workspace-specific cache paths."""
    paths = []
    
    # VS Code workspace caches
    vscode_dir = workspace_root / ".vscode"
    if vscode_dir.exists():
        paths.extend([
            vscode_dir / ".history",
            vscode_dir / ".cache",
        ])
    
    return [p for p in paths if p.exists()]


def find_python_caches(workspace_root: Path) -> List[Path]:
    """Find all Python cache directories."""
    caches = []
    
    cache_patterns = [
        "__pycache__",
        ".pytest_cache",
        ".mypy_cache",
        ".ruff_cache",
        "*.egg-info",
    ]
    
    for pattern in cache_patterns:
        if "*" in pattern:
            caches.extend(workspace_root.rglob(pattern))
        else:
            caches.extend(workspace_root.rglob(pattern))
    
    # Also find .pyc files
    caches.extend(workspace_root.rglob("*.pyc"))
    
    return caches


def get_directory_size(path: Path) -> int:
    """Calculate total size of directory in bytes."""
    if path.is_file():
        return path.stat().st_size
    
    total = 0
    try:
        for entry in path.rglob("*"):
            if entry.is_file():
                try:
                    total += entry.stat().st_size
                except (OSError, PermissionError):
                    pass
    except (OSError, PermissionError):
        pass
    return total


def format_size(size_bytes: int) -> str:
    """Format size in human-readable format."""
    for unit in ["B", "KB", "MB", "GB"]:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} TB"


def clear_caches(
    workspace_root: Path,
    dry_run: bool = True,
    include_vscode: bool = True,
    include_python: bool = True,
    include_workspace: bool = True,
    verbose: bool = False
) -> Tuple[int, int, List[str]]:
    """
    Clear cache directories.
    
    Returns:
        Tuple of (items_cleared, bytes_freed, error_messages)
    """
    items_cleared = 0
    bytes_freed = 0
    errors = []
    
    targets = []
    
    if include_vscode:
        targets.extend(get_vscode_cache_paths())
    
    if include_workspace:
        targets.extend(get_workspace_cache_paths(workspace_root))
    
    if include_python:
        targets.extend(find_python_caches(workspace_root))
    
    print(f"\n{'=' * 60}")
    print("🧹 CORTEX Cache Cleaner")
    print(f"{'=' * 60}")
    print(f"\n📂 Workspace: {workspace_root}")
    print(f"🔍 Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print(f"\n📋 Found {len(targets)} cache target(s):")
    
    for target in targets:
        size = get_directory_size(target)
        bytes_freed += size
        
        rel_path = target
        try:
            rel_path = target.relative_to(workspace_root)
        except ValueError:
            pass  # Not relative to workspace
        
        if verbose or not dry_run:
            print(f"   {'📁' if target.is_dir() else '📄'} {rel_path} ({format_size(size)})")
        
        if not dry_run:
            try:
                if target.is_dir():
                    shutil.rmtree(target)
                else:
                    target.unlink()
                items_cleared += 1
            except (OSError, PermissionError) as e:
                errors.append(f"Failed to delete {target}: {e}")
    
    print(f"\n{'=' * 60}")
    if dry_run:
        print(f"📊 Would clear: {len(targets)} items ({format_size(bytes_freed)})")
        print("💡 Run with --execute to actually delete")
    else:
        print(f"✅ Cleared: {items_cleared}/{len(targets)} items ({format_size(bytes_freed)})")
        if errors:
            print(f"⚠️  Errors: {len(errors)}")
            for err in errors:
                print(f"   - {err}")
    print(f"{'=' * 60}\n")
    
    return items_cleared, bytes_freed, errors


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CORTEX Cache Cleaner - Clear VS Code and Python caches"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually delete files (default is dry-run)"
    )
    parser.add_argument(
        "--workspace",
        type=str,
        default=".",
        help="Workspace root directory (default: current)"
    )
    parser.add_argument(
        "--no-vscode",
        action="store_true",
        help="Skip VS Code cache clearing"
    )
    parser.add_argument(
        "--no-python",
        action="store_true",
        help="Skip Python cache clearing"
    )
    parser.add_argument(
        "--no-workspace",
        action="store_true",
        help="Skip workspace-specific cache clearing"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    workspace = Path(args.workspace).resolve()
    
    if not workspace.exists():
        print(f"❌ Workspace not found: {workspace}")
        sys.exit(1)
    
    items, size, errors = clear_caches(
        workspace_root=workspace,
        dry_run=not args.execute,
        include_vscode=not args.no_vscode,
        include_python=not args.no_python,
        include_workspace=not args.no_workspace,
        verbose=args.verbose
    )
    
    sys.exit(0 if not errors else 1)


if __name__ == "__main__":
    main()
