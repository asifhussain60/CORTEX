#!/usr/bin/env python3
"""
VS Code Cache Cleaner Utility
Purpose: Safely clear VS Code cache without affecting user settings
Author: Asif Hussain
Date: 2026-01-13
Copyright © 2025-2026 Asif Hussain. All rights reserved.

Compliance:
- CORE-005: Path portability (uses pathlib.Path, cross-platform)
- CORE-002: No summary files (reports to stdout only)

Platform Support:
- 🟢 CROSS-PLATFORM: Works identically on MAC, WIN, Linux
"""

import os
import platform
import shutil
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime


class VSCodeCacheCleaner:
    """
    Cross-platform VS Code cache cleaner.
    
    Clears:
    - Extension cache (CachedExtensions, CachedExtensionVSIXs)
    - Workspace cache (workspaceStorage)
    - GPT/Copilot cache (GitHub.copilot)
    - Code cache (Code Cache, GPUCache)
    - Temporary files (logs, crash reports)
    
    Preserves:
    - User settings (settings.json, keybindings.json)
    - Installed extensions (extensions folder structure)
    - Workspace configurations (.vscode folders)
    """
    
    def __init__(self):
        self.system = platform.system()
        self.vscode_base = self._get_vscode_base_path()
        self.cleaned_paths: List[Path] = []
        self.preserved_paths: List[Path] = []
        self.errors: List[Tuple[Path, str]] = []
        self.total_size_freed = 0
    
    def _get_vscode_base_path(self) -> Path:
        """
        Get VS Code user data directory (cross-platform).
        
        Returns:
            Path to VS Code user data directory
        
        Platform paths:
        - macOS: ~/Library/Application Support/Code
        - Windows: %APPDATA%/Code
        - Linux: ~/.config/Code
        """
        home = Path.home()
        
        if self.system == 'Darwin':  # macOS
            return home / "Library/Application Support/Code"
        elif self.system == 'Windows':
            appdata = Path(os.environ.get('APPDATA', home / 'AppData/Roaming'))
            return appdata / "Code"
        else:  # Linux
            return home / ".config/Code"
    
    def _get_cache_directories(self) -> List[Dict[str, any]]:
        """
        Get list of cache directories to clean.
        
        Returns:
            List of dicts with 'path', 'name', 'description' keys
        """
        base = self.vscode_base
        
        cache_dirs = [
            {
                'path': base / "Cache",
                'name': "Main Cache",
                'description': "HTTP cache, image cache"
            },
            {
                'path': base / "CachedData",
                'name': "Cached Data",
                'description': "VS Code update cache"
            },
            {
                'path': base / "CachedExtensions",
                'name': "Cached Extensions",
                'description': "Extension download cache"
            },
            {
                'path': base / "CachedExtensionVSIXs",
                'name': "Cached Extension VSIXs",
                'description': "Extension package cache"
            },
            {
                'path': base / "Code Cache",
                'name': "Code Cache",
                'description': "JavaScript V8 cache"
            },
            {
                'path': base / "GPUCache",
                'name': "GPU Cache",
                'description': "Graphics cache"
            },
            {
                'path': base / "logs",
                'name': "Logs",
                'description': "Application logs"
            },
            {
                'path': base / "crashDumps",
                'name': "Crash Dumps",
                'description': "Crash report files"
            },
            {
                'path': base / "User/workspaceStorage",
                'name': "Workspace Storage",
                'description': "Workspace cache (safe to clear)"
            },
            {
                'path': base / "User/globalStorage/github.copilot",
                'name': "GitHub Copilot Cache",
                'description': "Copilot extension cache"
            }
        ]
        
        return cache_dirs
    
    def _get_preserved_paths(self) -> List[Dict[str, any]]:
        """
        Get list of paths that should be preserved.
        
        Returns:
            List of dicts with 'path', 'name', 'description' keys
        """
        base = self.vscode_base
        
        preserved = [
            {
                'path': base / "User/settings.json",
                'name': "User Settings",
                'description': "User preferences"
            },
            {
                'path': base / "User/keybindings.json",
                'name': "Keybindings",
                'description': "Keyboard shortcuts"
            },
            {
                'path': base / "User/snippets",
                'name': "Snippets",
                'description': "User code snippets"
            },
            {
                'path': base / "extensions",
                'name': "Extensions",
                'description': "Installed extensions"
            },
            {
                'path': base / "User/profiles",
                'name': "Profiles",
                'description': "User profiles"
            }
        ]
        
        return preserved
    
    def _get_directory_size(self, path: Path) -> int:
        """
        Calculate total size of directory in bytes.
        
        Args:
            path: Directory path
        
        Returns:
            Size in bytes
        """
        total = 0
        try:
            if path.is_file():
                total = path.stat().st_size
            elif path.is_dir():
                for item in path.rglob('*'):
                    if item.is_file():
                        try:
                            total += item.stat().st_size
                        except (OSError, PermissionError):
                            pass
        except (OSError, PermissionError):
            pass
        
        return total
    
    def _format_size(self, size_bytes: int) -> str:
        """
        Format bytes to human-readable size.
        
        Args:
            size_bytes: Size in bytes
        
        Returns:
            Formatted string (e.g., "1.5 MB")
        """
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    def dry_run(self) -> Dict[str, any]:
        """
        Simulate cache cleaning (show what would be cleaned).
        
        Returns:
            Dict with 'to_clean', 'to_preserve', 'total_size' keys
        """
        cache_dirs = self._get_cache_directories()
        preserved = self._get_preserved_paths()
        
        to_clean = []
        total_size = 0
        
        for cache_info in cache_dirs:
            path = cache_info['path']
            if path.exists():
                size = self._get_directory_size(path)
                total_size += size
                to_clean.append({
                    **cache_info,
                    'exists': True,
                    'size': size,
                    'size_formatted': self._format_size(size)
                })
            else:
                to_clean.append({
                    **cache_info,
                    'exists': False,
                    'size': 0,
                    'size_formatted': '0 B'
                })
        
        to_preserve = []
        for preserve_info in preserved:
            path = preserve_info['path']
            to_preserve.append({
                **preserve_info,
                'exists': path.exists()
            })
        
        return {
            'to_clean': to_clean,
            'to_preserve': to_preserve,
            'total_size': total_size,
            'total_size_formatted': self._format_size(total_size)
        }
    
    def clean(self, dry_run: bool = False) -> Dict[str, any]:
        """
        Clean VS Code cache.
        
        Args:
            dry_run: If True, only simulate (don't delete)
        
        Returns:
            Dict with 'cleaned', 'errors', 'size_freed' keys
        """
        if dry_run:
            return self.dry_run()
        
        cache_dirs = self._get_cache_directories()
        self.cleaned_paths = []
        self.errors = []
        self.total_size_freed = 0
        
        for cache_info in cache_dirs:
            path = cache_info['path']
            
            if not path.exists():
                continue
            
            try:
                size = self._get_directory_size(path)
                
                if path.is_dir():
                    shutil.rmtree(path)
                elif path.is_file():
                    path.unlink()
                
                self.cleaned_paths.append(path)
                self.total_size_freed += size
                
            except (OSError, PermissionError) as e:
                self.errors.append((path, str(e)))
        
        return {
            'cleaned': [
                {
                    'path': str(p),
                    'name': p.name
                }
                for p in self.cleaned_paths
            ],
            'errors': [
                {
                    'path': str(p),
                    'error': err
                }
                for p, err in self.errors
            ],
            'size_freed': self.total_size_freed,
            'size_freed_formatted': self._format_size(self.total_size_freed),
            'success': len(self.errors) == 0
        }
    
    def report(self, dry_run: bool = False) -> str:
        """
        Generate human-readable report.
        
        Args:
            dry_run: If True, generate dry-run report
        
        Returns:
            Formatted report string
        """
        if dry_run:
            data = self.dry_run()
            
            report = []
            report.append("=" * 60)
            report.append("VS CODE CACHE CLEANER - DRY RUN")
            report.append("=" * 60)
            report.append("")
            report.append(f"System: {self.system}")
            report.append(f"VS Code Path: {self.vscode_base}")
            report.append("")
            
            report.append("📦 TO BE CLEANED:")
            for item in data['to_clean']:
                if item['exists']:
                    report.append(f"  ✓ {item['name']}: {item['size_formatted']}")
                    report.append(f"    {item['description']}")
                else:
                    report.append(f"  ⊘ {item['name']}: Not found")
            
            report.append("")
            report.append("🛡️ TO BE PRESERVED:")
            for item in data['to_preserve']:
                status = "✓" if item['exists'] else "⊘"
                report.append(f"  {status} {item['name']}")
            
            report.append("")
            report.append(f"💾 Total size to free: {data['total_size_formatted']}")
            report.append("")
            report.append("Run without --dry-run to execute cleaning")
            report.append("=" * 60)
            
            return "\n".join(report)
        
        else:
            data = self.clean(dry_run=False)
            
            report = []
            report.append("=" * 60)
            report.append("VS CODE CACHE CLEANER - EXECUTION REPORT")
            report.append("=" * 60)
            report.append("")
            report.append(f"System: {self.system}")
            report.append(f"VS Code Path: {self.vscode_base}")
            report.append(f"Timestamp: {datetime.now().isoformat()}")
            report.append("")
            
            if data['cleaned']:
                report.append(f"✅ CLEANED ({len(data['cleaned'])} items):")
                for item in data['cleaned']:
                    report.append(f"  • {item['name']}")
            else:
                report.append("⚠️ No cache found to clean")
            
            if data['errors']:
                report.append("")
                report.append(f"❌ ERRORS ({len(data['errors'])} items):")
                for item in data['errors']:
                    report.append(f"  • {item['path']}")
                    report.append(f"    Error: {item['error']}")
            
            report.append("")
            report.append(f"💾 Size freed: {data['size_freed_formatted']}")
            report.append("")
            
            if data['success']:
                report.append("✅ Cache cleaning completed successfully")
            else:
                report.append("⚠️ Cache cleaning completed with errors")
            
            report.append("=" * 60)
            
            return "\n".join(report)


def main():
    """CLI entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="VS Code Cache Cleaner - Safely clear VS Code cache"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help="Show what would be cleaned without actually deleting"
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help="Output results as JSON"
    )
    
    args = parser.parse_args()
    
    cleaner = VSCodeCacheCleaner()
    
    if args.json:
        import json
        if args.dry_run:
            result = cleaner.dry_run()
        else:
            result = cleaner.clean()
        print(json.dumps(result, indent=2))
    else:
        report = cleaner.report(dry_run=args.dry_run)
        print(report)


if __name__ == "__main__":
    main()
