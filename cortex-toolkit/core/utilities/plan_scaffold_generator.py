#!/usr/bin/env python3
"""
CORTEX Plan Scaffold Generator

Automatically creates the standard 4-folder planning structure required by
Planning System 4.0. Eliminates manual directory creation overhead.

Usage:
    python plan_scaffold_generator.py "knowledge-documentation"
    python plan_scaffold_generator.py "feature-name" --description "Feature description"

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class PlanScaffoldGenerator:
    """Generate standard planning folder structure."""
    
    def __init__(self, cortex_root: Optional[Path] = None):
        """
        Initialize generator.
        
        Args:
            cortex_root: Path to CORTEX root (auto-detected if None)
        """
        if cortex_root is None:
            # Auto-detect: Look for cortex-brain/ folder
            current = Path(__file__).resolve()
            for parent in current.parents:
                if (parent / "cortex-brain").exists():
                    cortex_root = parent
                    break
            
            if cortex_root is None:
                raise RuntimeError("Cannot detect CORTEX root directory")
        
        self.cortex_root = Path(cortex_root)
        self.planning_root = self.cortex_root / "cortex-brain" / "documents" / "planning" / "active"
        
        # Validate planning root exists
        if not self.planning_root.exists():
            raise RuntimeError(f"Planning root not found: {self.planning_root}")
    
    def sanitize_name(self, name: str) -> str:
        """
        Sanitize plan name for folder creation.
        
        Rules:
        - Lowercase
        - Replace spaces with hyphens
        - Remove special characters (keep alphanumeric and hyphens)
        - Collapse multiple hyphens
        
        Args:
            name: Raw plan name
            
        Returns:
            Sanitized folder name
            
        Examples:
            >>> gen.sanitize_name("Knowledge Documentation")
            'knowledge-documentation'
            >>> gen.sanitize_name("API v2.0 Migration!")
            'api-v2-0-migration'
        """
        import re
        
        # Lowercase
        sanitized = name.lower()
        
        # Replace spaces and underscores with hyphens
        sanitized = sanitized.replace(' ', '-').replace('_', '-')
        
        # Remove special characters (keep alphanumeric and hyphens)
        sanitized = re.sub(r'[^a-z0-9\-]', '', sanitized)
        
        # Collapse multiple hyphens
        sanitized = re.sub(r'-+', '-', sanitized)
        
        # Remove leading/trailing hyphens
        sanitized = sanitized.strip('-')
        
        return sanitized
    
    def create_scaffold(
        self, 
        plan_name: str, 
        description: Optional[str] = None,
        metadata: Optional[Dict] = None,
        dry_run: bool = False
    ) -> Dict:
        """
        Create standard 4-folder planning structure.
        
        Structure:
            {plan_name}/
            ├── 00-master-plan.md       # Main plan (created separately)
            ├── context/                 # Context artifacts
            ├── reports/                 # Progress reports
            ├── artifacts/               # Supporting files
            └── tracking/                # progress-tracker.json
        
        Args:
            plan_name: Plan name (will be sanitized)
            description: Optional plan description
            metadata: Optional metadata dictionary
            dry_run: If True, don't create folders (just return structure)
            
        Returns:
            Dictionary with created paths and metadata
        """
        # Sanitize name
        folder_name = self.sanitize_name(plan_name)
        
        if not folder_name:
            raise ValueError(f"Invalid plan name: '{plan_name}' sanitizes to empty string")
        
        # Define structure
        plan_dir = self.planning_root / folder_name
        folders = {
            "root": plan_dir,
            "context": plan_dir / "context",
            "reports": plan_dir / "reports",
            "artifacts": plan_dir / "artifacts",
            "tracking": plan_dir / "tracking"
        }
        
        # Check if plan already exists
        if plan_dir.exists() and not dry_run:
            return {
                "status": "exists",
                "message": f"Plan already exists: {folder_name}",
                "plan_dir": str(plan_dir),
                "folders": {k: str(v) for k, v in folders.items()}
            }
        
        # Create folders (unless dry run)
        created_folders = []
        if not dry_run:
            for name, path in folders.items():
                path.mkdir(parents=True, exist_ok=True)
                created_folders.append(str(path))
        
        # Create progress tracker JSON
        tracker_path = folders["tracking"] / "progress-tracker.json"
        tracker_data = {
            "plan_name": plan_name,
            "folder_name": folder_name,
            "created": datetime.now().isoformat(),
            "description": description or f"Implementation plan for {plan_name}",
            "status": "initialized",
            "phases": [],
            "metadata": metadata or {},
            "statistics": {
                "total_phases": 0,
                "completed_phases": 0,
                "progress_percent": 0
            }
        }
        
        if not dry_run:
            with open(tracker_path, 'w', encoding='utf-8') as f:
                json.dump(tracker_data, f, indent=2)
        
        # Return result
        result = {
            "status": "created" if not dry_run else "dry_run",
            "plan_name": plan_name,
            "folder_name": folder_name,
            "plan_dir": str(plan_dir),
            "folders": {k: str(v) for k, v in folders.items()},
            "tracker": str(tracker_path),
            "created_folders": created_folders if not dry_run else []
        }
        
        return result
    
    def list_plans(self) -> list:
        """
        List all existing plans in active folder.
        
        Returns:
            List of plan folder names
        """
        if not self.planning_root.exists():
            return []
        
        plans = []
        for item in self.planning_root.iterdir():
            if item.is_dir() and not item.name.startswith('.'):
                plans.append(item.name)
        
        return sorted(plans)
    
    def validate_structure(self, plan_name: str) -> Dict:
        """
        Validate that a plan has the correct 4-folder structure.
        
        Args:
            plan_name: Plan folder name
            
        Returns:
            Validation result dictionary
        """
        folder_name = self.sanitize_name(plan_name)
        plan_dir = self.planning_root / folder_name
        
        if not plan_dir.exists():
            return {
                "valid": False,
                "message": f"Plan not found: {folder_name}",
                "missing": ["root"]
            }
        
        required_folders = ["context", "reports", "artifacts", "tracking"]
        missing = []
        
        for folder in required_folders:
            if not (plan_dir / folder).exists():
                missing.append(folder)
        
        # Check for progress tracker
        tracker_path = plan_dir / "tracking" / "progress-tracker.json"
        has_tracker = tracker_path.exists()
        
        return {
            "valid": len(missing) == 0 and has_tracker,
            "plan_dir": str(plan_dir),
            "missing_folders": missing,
            "has_tracker": has_tracker,
            "message": "Valid structure" if len(missing) == 0 and has_tracker else f"Missing: {', '.join(missing)}" + ("" if has_tracker else ", progress-tracker.json")
        }


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CORTEX Plan Scaffold Generator - Create standard planning folder structure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create plan scaffold
  python plan_scaffold_generator.py "knowledge-documentation"
  
  # Create with description
  python plan_scaffold_generator.py "api-v2-migration" --description "Migrate API to v2"
  
  # Dry run (don't create folders)
  python plan_scaffold_generator.py "test-plan" --dry-run
  
  # List existing plans
  python plan_scaffold_generator.py --list
  
  # Validate existing plan
  python plan_scaffold_generator.py "knowledge-documentation" --validate
        """
    )
    
    parser.add_argument(
        'plan_name',
        nargs='?',
        help='Plan name (will be sanitized for folder creation)'
    )
    
    parser.add_argument(
        '--description', '-d',
        help='Plan description (added to progress tracker)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be created without creating folders'
    )
    
    parser.add_argument(
        '--list', '-l',
        action='store_true',
        help='List all existing plans'
    )
    
    parser.add_argument(
        '--validate', '-v',
        action='store_true',
        help='Validate existing plan structure'
    )
    
    parser.add_argument(
        '--cortex-root',
        type=Path,
        help='CORTEX root directory (auto-detected if not specified)'
    )
    
    args = parser.parse_args()
    
    try:
        generator = PlanScaffoldGenerator(cortex_root=args.cortex_root)
        
        # List mode
        if args.list:
            plans = generator.list_plans()
            if plans:
                print(f"📋 Found {len(plans)} active plans:")
                for plan in plans:
                    print(f"  • {plan}")
            else:
                print("📋 No active plans found")
            return 0
        
        # Validate mode
        if args.validate:
            if not args.plan_name:
                print("❌ Error: --validate requires plan_name", file=sys.stderr)
                return 1
            
            result = generator.validate_structure(args.plan_name)
            
            if result['valid']:
                print(f"✅ Valid structure: {result['plan_dir']}")
            else:
                print(f"❌ Invalid structure: {result['message']}")
                print(f"   Plan dir: {result.get('plan_dir', 'N/A')}")
            
            return 0 if result['valid'] else 1
        
        # Create mode
        if not args.plan_name:
            parser.print_help()
            return 1
        
        result = generator.create_scaffold(
            plan_name=args.plan_name,
            description=args.description,
            dry_run=args.dry_run
        )
        
        # Print result
        if result['status'] == 'exists':
            print(f"ℹ️  {result['message']}")
            print(f"   Path: {result['plan_dir']}")
        elif result['status'] == 'dry_run':
            print(f"🔍 Dry run - Would create:")
            print(f"   Plan: {result['plan_name']} → {result['folder_name']}")
            print(f"   Root: {result['plan_dir']}")
            print("   Folders:")
            for name, path in result['folders'].items():
                if name != 'root':
                    print(f"     • {name}/")
            print(f"   Tracker: {result['tracker']}")
        else:
            print(f"✅ Created plan scaffold: {result['folder_name']}")
            print(f"   Path: {result['plan_dir']}")
            print(f"   Folders: {len(result['created_folders'])}")
            print(f"   Tracker: {result['tracker']}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
