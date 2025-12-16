#!/usr/bin/env python3
"""
Key Files Freshness Checker

Part of Phase 2 Deliverable 2.2 - Key Files Inventory Automation

This module:
1. Reads KEY-FILES-INVENTORY.md for tracked files
2. Checks file modification timestamps
3. Flags files not updated in 30+ days (excluding auto-update files)
4. Generates freshness report for deployment validation

Usage:
    from src.utils.key_files_checker import KeyFilesChecker
    
    checker = KeyFilesChecker()
    stale_files = checker.find_stale_files(days=30)
    report = checker.generate_freshness_report()

Author: Asif Hussain
License: Source-Available (Use Allowed, No Contributions)
"""

import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple
import os


class KeyFilesChecker:
    """Checks freshness of key CORTEX files tracked in inventory."""
    
    def __init__(self, cortex_root: Path = None):
        """
        Initialize key files checker.
        
        Args:
            cortex_root: Root directory of CORTEX project
        """
        if cortex_root is None:
            # Auto-detect: this file is in src/utils/
            cortex_root = Path(__file__).parent.parent.parent
        
        self.cortex_root = cortex_root
        self.inventory_file = (
            cortex_root / "cortex-brain" / "documents" / "planning" / "KEY-FILES-INVENTORY.md"
        )
    
    def parse_inventory(self) -> List[Dict[str, str]]:
        """
        Parse KEY-FILES-INVENTORY.md to extract tracked files.
        
        Returns:
            List of dicts with file info:
            [
                {
                    "file": "docs/ARCHITECTURE.md",
                    "auto_update": "Yes",
                    "update_frequency": "Deploy"
                },
                ...
            ]
        """
        if not self.inventory_file.exists():
            return []
        
        content = self.inventory_file.read_text()
        tracked_files = []
        
        # Find all table rows with file paths
        # Pattern: | `path/to/file.ext` | Purpose | Frequency | Auto | Owner |
        pattern = r'\| `([^`]+)` \| .+ \| .+ \| ([✅❌]) ([YyNn][eoOs]+)'
        
        for match in re.finditer(pattern, content):
            file_path = match.group(1)
            auto_update_marker = match.group(2)
            auto_update = "Yes" if auto_update_marker == "✅" else "No"
            
            tracked_files.append({
                "file": file_path,
                "auto_update": auto_update,
                "path": self.cortex_root / file_path
            })
        
        return tracked_files
    
    def get_file_age_days(self, file_path: Path) -> float:
        """
        Get age of file in days since last modification.
        
        Args:
            file_path: Path to file
            
        Returns:
            Age in days (float)
        """
        if not file_path.exists():
            return float('inf')  # Missing file = infinitely old
        
        mtime = os.path.getmtime(file_path)
        file_modified = datetime.fromtimestamp(mtime)
        age = datetime.now() - file_modified
        
        return age.total_seconds() / 86400  # Convert to days
    
    def find_stale_files(self, days: int = 30) -> List[Dict[str, any]]:
        """
        Find files not updated within specified days.
        
        Only flags manual-update files (auto_update=No).
        Auto-updated files are excluded from staleness check.
        
        Args:
            days: Number of days threshold (default: 30)
            
        Returns:
            List of stale file dicts:
            [
                {
                    "file": "path/to/file",
                    "age_days": 45.2,
                    "last_modified": "2025-10-15",
                    "auto_update": "No"
                },
                ...
            ]
        """
        tracked_files = self.parse_inventory()
        stale_files = []
        
        for file_info in tracked_files:
            # Skip auto-update files
            if file_info["auto_update"] == "Yes":
                continue
            
            file_path = file_info["path"]
            age_days = self.get_file_age_days(file_path)
            
            if age_days > days:
                if file_path.exists():
                    mtime = os.path.getmtime(file_path)
                    last_modified = datetime.fromtimestamp(mtime).strftime("%Y-%m-%d")
                else:
                    last_modified = "MISSING"
                
                stale_files.append({
                    "file": file_info["file"],
                    "age_days": round(age_days, 1),
                    "last_modified": last_modified,
                    "auto_update": file_info["auto_update"],
                    "path": file_path
                })
        
        return stale_files
    
    def generate_freshness_report(self) -> Dict[str, any]:
        """
        Generate comprehensive freshness report for all tracked files.
        
        Returns:
            Report dict:
            {
                "stale_files": [...],
                "fresh_files": [...],
                "missing_files": [...],
                "auto_update_files": [...],
                "stale_count": int,
                "total_tracked": int,
                "staleness_percentage": float,
                "generated_at": "2025-12-01 10:30:00"
            }
        """
        tracked_files = self.parse_inventory()
        stale_files = self.find_stale_files(days=30)
        
        fresh_files = []
        missing_files = []
        auto_update_files = []
        
        for file_info in tracked_files:
            file_path = file_info["path"]
            
            if not file_path.exists():
                missing_files.append(file_info["file"])
                continue
            
            if file_info["auto_update"] == "Yes":
                auto_update_files.append(file_info["file"])
                continue
            
            age_days = self.get_file_age_days(file_path)
            if age_days <= 30:
                fresh_files.append({
                    "file": file_info["file"],
                    "age_days": round(age_days, 1)
                })
        
        total_manual = len([f for f in tracked_files if f["auto_update"] == "No"])
        staleness_pct = (len(stale_files) / total_manual * 100) if total_manual > 0 else 0.0
        
        return {
            "stale_files": stale_files,
            "fresh_files": fresh_files,
            "missing_files": missing_files,
            "auto_update_files": auto_update_files,
            "stale_count": len(stale_files),
            "fresh_count": len(fresh_files),
            "missing_count": len(missing_files),
            "auto_update_count": len(auto_update_files),
            "total_tracked": len(tracked_files),
            "staleness_percentage": round(staleness_pct, 1),
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def print_freshness_report(self) -> None:
        """Print human-readable freshness report to console."""
        report = self.generate_freshness_report()
        
        print("\n" + "="*60)
        print("📋 CORTEX Key Files Freshness Report")
        print("="*60)
        print(f"Generated: {report['generated_at']}")
        print(f"Total Tracked Files: {report['total_tracked']}")
        print()
        
        print(f"✅ Fresh Files (< 30 days): {report['fresh_count']}")
        print(f"⚠️  Stale Files (> 30 days): {report['stale_count']}")
        print(f"❌ Missing Files: {report['missing_count']}")
        print(f"🔄 Auto-Update Files: {report['auto_update_count']}")
        print()
        
        if report['stale_count'] > 0:
            print(f"Staleness Percentage: {report['staleness_percentage']}%")
            print()
            print("⚠️  STALE FILES (Manual Update Required):")
            print("-" * 60)
            for f in report['stale_files']:
                print(f"  • {f['file']}")
                print(f"    Last Modified: {f['last_modified']} ({f['age_days']} days ago)")
            print()
        
        if report['missing_count'] > 0:
            print("❌ MISSING FILES:")
            print("-" * 60)
            for f in report['missing_files']:
                print(f"  • {f}")
            print()
        
        print("="*60 + "\n")


def main():
    """CLI entry point for freshness checking."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Check CORTEX key files freshness")
    parser.add_argument("--days", type=int, default=30, help="Staleness threshold in days")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of text")
    args = parser.parse_args()
    
    checker = KeyFilesChecker()
    
    if args.json:
        import json
        report = checker.generate_freshness_report()
        print(json.dumps(report, indent=2))
    else:
        checker.print_freshness_report()


if __name__ == "__main__":
    main()
