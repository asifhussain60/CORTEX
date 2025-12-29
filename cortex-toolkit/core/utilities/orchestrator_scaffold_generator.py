#!/usr/bin/env python3
"""
CORTEX Orchestrator Scaffold Generator

Universal scaffold generator for orchestrators that require standard folder structures.
Supports multiple orchestrator types with configurable templates.

Supported Orchestrators:
- Planning System: 4 folders (context, reports, artifacts, tracking)
- Sanitization: 5 folders (source, mappings, sanitized, reports, backups)
- TDD: 3 folders (tests, implementation, reports)
- ADO: 2 folders (work-items, mappings)

Usage:
    python orchestrator_scaffold_generator.py --type planning "feature-name"
    python orchestrator_scaffold_generator.py --type sanitization "project-name"
    python orchestrator_scaffold_generator.py --type tdd "feature-name"

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional


# Orchestrator templates
TEMPLATES = {
    "planning": {
        "root": "cortex-brain/documents/planning/active",
        "folders": ["context", "reports", "artifacts", "tracking"],
        "tracker_file": "tracking/progress-tracker.json",
        "master_file": "00-master-plan.md",
        "description": "Planning System 4.0 standard structure"
    },
    "sanitization": {
        "root": "cortex-brain/documents/sanitization",
        "folders": ["source-analysis", "mappings", "sanitized-output", "reports", "backups"],
        "tracker_file": "reports/sanitization-tracker.json",
        "master_file": "sanitization-plan.md",
        "description": "Code Sanitization workflow structure"
    },
    "tdd": {
        "root": "cortex-brain/documents/tdd",
        "folders": ["tests", "implementation", "refactoring-reports"],
        "tracker_file": "refactoring-reports/tdd-tracker.json",
        "master_file": "tdd-plan.md",
        "description": "TDD workflow structure (RED-GREEN-REFACTOR)"
    },
    "ado": {
        "root": "cortex-brain/documents/ado",
        "folders": ["work-items", "mappings"],
        "tracker_file": "work-items/ado-tracker.json",
        "master_file": "ado-plan.md",
        "description": "ADO work item generation structure"
    },
    "maintenance": {
        "root": "cortex-brain/health-reports",
        "folders": ["diagnostics", "optimizations", "repairs", "archives"],
        "tracker_file": "diagnostics/maintenance-tracker.json",
        "master_file": "maintenance-report.md",
        "description": "System maintenance workflow structure"
    }
}


class OrchestratorScaffoldGenerator:
    """Generate orchestrator-specific folder structures."""
    
    def __init__(self, cortex_root: Optional[Path] = None):
        """Initialize generator with CORTEX root detection."""
        if cortex_root is None:
            current = Path(__file__).resolve()
            for parent in current.parents:
                if (parent / "cortex-brain").exists():
                    cortex_root = parent
                    break
            
            if cortex_root is None:
                raise RuntimeError("Cannot detect CORTEX root directory")
        
        self.cortex_root = Path(cortex_root)
    
    def sanitize_name(self, name: str) -> str:
        """Sanitize name for folder creation."""
        import re
        sanitized = name.lower()
        sanitized = sanitized.replace(' ', '-').replace('_', '-')
        sanitized = re.sub(r'[^a-z0-9\-]', '', sanitized)
        sanitized = re.sub(r'-+', '-', sanitized)
        return sanitized.strip('-')
    
    def create_scaffold(
        self,
        orchestrator_type: str,
        name: str,
        description: Optional[str] = None,
        dry_run: bool = False
    ) -> Dict:
        """
        Create orchestrator-specific folder structure.
        
        Args:
            orchestrator_type: Type of orchestrator (planning, sanitization, tdd, ado)
            name: Folder name (will be sanitized)
            description: Optional description
            dry_run: If True, don't create folders
            
        Returns:
            Result dictionary with created paths
        """
        if orchestrator_type not in TEMPLATES:
            raise ValueError(
                f"Unknown orchestrator type: {orchestrator_type}. "
                f"Supported: {', '.join(TEMPLATES.keys())}"
            )
        
        template = TEMPLATES[orchestrator_type]
        folder_name = self.sanitize_name(name)
        
        if not folder_name:
            raise ValueError(f"Invalid name: '{name}' sanitizes to empty string")
        
        # Build paths
        root_dir = self.cortex_root / template["root"] / folder_name
        folders = {
            "root": root_dir,
            **{folder: root_dir / folder for folder in template["folders"]}
        }
        
        # Check existence
        if root_dir.exists() and not dry_run:
            return {
                "status": "exists",
                "message": f"{orchestrator_type.title()} scaffold already exists: {folder_name}",
                "root_dir": str(root_dir),
                "folders": {k: str(v) for k, v in folders.items()}
            }
        
        # Create folders
        created_folders = []
        if not dry_run:
            for path in folders.values():
                path.mkdir(parents=True, exist_ok=True)
                created_folders.append(str(path))
        
        # Create tracker file
        tracker_path = root_dir / template["tracker_file"]
        tracker_data = {
            "orchestrator_type": orchestrator_type,
            "name": name,
            "folder_name": folder_name,
            "created": datetime.now().isoformat(),
            "description": description or template["description"],
            "status": "initialized",
            "template_version": "1.0"
        }
        
        if not dry_run:
            tracker_path.parent.mkdir(parents=True, exist_ok=True)
            with open(tracker_path, 'w', encoding='utf-8') as f:
                json.dump(tracker_data, f, indent=2)
        
        # Return result
        return {
            "status": "created" if not dry_run else "dry_run",
            "orchestrator_type": orchestrator_type,
            "name": name,
            "folder_name": folder_name,
            "root_dir": str(root_dir),
            "folders": {k: str(v) for k, v in folders.items()},
            "tracker": str(tracker_path),
            "created_folders": created_folders if not dry_run else []
        }
    
    def list_templates(self) -> Dict[str, str]:
        """List available orchestrator templates."""
        return {k: v["description"] for k, v in TEMPLATES.items()}


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CORTEX Orchestrator Scaffold Generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create planning scaffold
  python orchestrator_scaffold_generator.py --type planning "api-migration"
  
  # Create sanitization scaffold
  python orchestrator_scaffold_generator.py --type sanitization "legacy-codebase"
  
  # Create TDD scaffold
  python orchestrator_scaffold_generator.py --type tdd "user-auth"
  
  # List available templates
  python orchestrator_scaffold_generator.py --list-templates
  
  # Dry run
  python orchestrator_scaffold_generator.py --type planning "test" --dry-run
        """
    )
    
    parser.add_argument(
        '--type', '-t',
        choices=list(TEMPLATES.keys()),
        help='Orchestrator type'
    )
    
    parser.add_argument(
        'name',
        nargs='?',
        help='Folder name (will be sanitized)'
    )
    
    parser.add_argument(
        '--description', '-d',
        help='Description (added to tracker)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be created without creating folders'
    )
    
    parser.add_argument(
        '--list-templates',
        action='store_true',
        help='List available orchestrator templates'
    )
    
    parser.add_argument(
        '--cortex-root',
        type=Path,
        help='CORTEX root directory (auto-detected if not specified)'
    )
    
    args = parser.parse_args()
    
    try:
        generator = OrchestratorScaffoldGenerator(cortex_root=args.cortex_root)
        
        # List templates
        if args.list_templates:
            templates = generator.list_templates()
            print("📋 Available Orchestrator Templates:\n")
            for orch_type, desc in templates.items():
                template = TEMPLATES[orch_type]
                print(f"  {orch_type}:")
                print(f"    Description: {desc}")
                print(f"    Folders: {', '.join(template['folders'])}")
                print(f"    Root: {template['root']}")
                print()
            return 0
        
        # Validate inputs
        if not args.type:
            print("❌ Error: --type required", file=sys.stderr)
            parser.print_help()
            return 1
        
        if not args.name:
            print("❌ Error: name required", file=sys.stderr)
            parser.print_help()
            return 1
        
        # Create scaffold
        result = generator.create_scaffold(
            orchestrator_type=args.type,
            name=args.name,
            description=args.description,
            dry_run=args.dry_run
        )
        
        # Print result
        if result['status'] == 'exists':
            print(f"ℹ️  {result['message']}")
            print(f"   Path: {result['root_dir']}")
        elif result['status'] == 'dry_run':
            print(f"🔍 Dry run - Would create {result['orchestrator_type']} scaffold:")
            print(f"   Name: {result['name']} → {result['folder_name']}")
            print(f"   Root: {result['root_dir']}")
            print("   Folders:")
            for name, path in result['folders'].items():
                if name != 'root':
                    print(f"     • {Path(path).name}/")
            print(f"   Tracker: {result['tracker']}")
        else:
            print(f"✅ Created {result['orchestrator_type']} scaffold: {result['folder_name']}")
            print(f"   Path: {result['root_dir']}")
            print(f"   Folders: {len(result['created_folders'])}")
            print(f"   Tracker: {result['tracker']}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
