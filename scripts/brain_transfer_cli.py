#!/usr/bin/env python3
"""
CORTEX Brain Transfer CLI

Natural language interface for brain export/import operations.

Usage:
    cortex export brain [--scope=workspace|cortex|all] [--min-confidence=0.5] [--output=path]
    cortex import brain <file> [--strategy=auto|replace|skip] [--dry-run]

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import argparse
from pathlib import Path
from typing import List, Optional

# Add src to path if needed
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.brain_transfer import BrainExporter, BrainImporter
from src.brain_transfer.git_operations import GitOperations


def export_brain_command(args: argparse.Namespace) -> int:
    """Execute brain export command."""
    try:
        exporter = BrainExporter()
        git_ops = GitOperations()
        
        print(f"🧠 CORTEX Brain Export")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"Scope: {args.scope}")
        print(f"Min Confidence: {args.min_confidence}")
        print(f"Git Integration: {'No (--local-only)' if args.local_only else 'Yes (default)'}")
        print(f"")
        
        output_path = exporter.export_brain(
            scope=args.scope,
            min_confidence=args.min_confidence,
            output_path=Path(args.output) if args.output else None
        )
        
        file_size_kb = output_path.stat().st_size / 1024
        
        print(f"✅ Brain exported successfully!")
        print(f"")
        print(f"📁 Location: {output_path}")
        print(f"💾 Size: {file_size_kb:.1f} KB")
        
        # Git integration (default behavior)
        if not args.local_only:
            if git_ops.is_git_repo():
                try:
                    print(f"")
                    print(f"� Git Integration:")
                    
                    # Stage the file
                    git_ops.git_add(output_path)
                    print(f"   ✅ Staged: {output_path.name}")
                    
                    # Generate smart commit message
                    commit_msg = git_ops.generate_commit_message(output_path)
                    git_ops.git_commit(commit_msg)
                    print(f"   ✅ Committed: {commit_msg}")
                    
                    # Push to remote
                    branch = git_ops.get_current_branch()
                    git_ops.git_push(branch)
                    print(f"   ✅ Pushed to: origin/{branch}")
                    
                    print(f"")
                    print(f"🌐 Brain shared successfully!")
                    print(f"   Teammates can now run: cortex import brain")
                    
                except RuntimeError as e:
                    print(f"")
                    print(f"⚠️  Git operation failed: {e}")
                    print(f"   Brain exported locally: {output_path}")
                    print(f"   You can push manually: git push")
            else:
                print(f"")
                print(f"⚠️  Not in git repository")
                print(f"   Brain exported locally: {output_path}")
                print(f"   Tip: Initialize git repo or use with --local-only")
        else:
            print(f"")
            print(f"📋 To share manually:")
            print(f"   git add {output_path}")
            print(f"   git commit -m 'brain: Share patterns'")
            print(f"   git push")
        
        return 0
        
    except Exception as e:
        print(f"❌ Export failed: {e}", file=sys.stderr)
        return 1


def import_brain_command(args: argparse.Namespace) -> int:
    """Execute brain import command."""
    try:
        importer = BrainImporter()
        git_ops = GitOperations()
        
        # Git integration: Pull first (unless --local-only)
        if not args.local_only:
            if git_ops.is_git_repo():
                try:
                    print(f"🧠 CORTEX Brain Import")
                    print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
                    print(f"🔄 Pulling from remote...")
                    
                    branch = git_ops.get_current_branch()
                    git_ops.git_pull(branch)
                    print(f"   ✅ Pulled from: origin/{branch}")
                    print(f"")
                    
                except RuntimeError as e:
                    print(f"⚠️  Git pull failed: {e}")
                    print(f"   Continuing with local import...")
                    print(f"")
        
        # Auto-detect mode: Scan for unprocessed exports
        if not hasattr(args, 'file') or args.file is None:
            exports_dir = Path("cortex-brain/exports")
            history_file = exports_dir / ".import-history"
            
            unprocessed = git_ops.scan_unprocessed_exports(exports_dir, history_file)
            
            if not unprocessed:
                print(f"✅ All caught up!")
                print(f"   No new brain exports found.")
                return 0
            
            print(f"📥 Found {len(unprocessed)} unprocessed export(s)")
            print(f"")
            
            total_new = 0
            total_merged = 0
            
            for export_file in unprocessed:
                print(f"   Importing: {export_file.name}")
                
                result = importer.import_brain(
                    yaml_path=export_file,
                    dry_run=False,
                    strategy=args.strategy
                )
                
                if result.get("success"):
                    stats = result["statistics"]
                    total_new += stats.get('new_patterns', 0)
                    total_merged += stats.get('merged_patterns', 0)
                    
                    # Mark as processed
                    git_ops.mark_as_processed(export_file, history_file)
                    print(f"      ✅ {stats['new_patterns']} new, {stats['merged_patterns']} merged")
            
            print(f"")
            print(f"✅ Import completed!")
            print(f"   Total patterns imported: {total_new}")
            print(f"   Total patterns merged: {total_merged}")
            
            return 0
        
        # Single file import mode
        yaml_path = Path(args.file)
        if not yaml_path.exists():
            print(f"❌ File not found: {yaml_path}", file=sys.stderr)
            return 1
        
        print(f"🧠 CORTEX Brain Import")
        print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print(f"File: {yaml_path.name}")
        print(f"Strategy: {args.strategy}")
        print(f"Dry Run: {args.dry_run}")
        print(f"")
        
        result = importer.import_brain(
            yaml_path=yaml_path,
            dry_run=args.dry_run,
            strategy=args.strategy
        )
        
        if result.get("dry_run"):
            print(f"🔍 DRY RUN PREVIEW")
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"Total patterns: {result['total_patterns']}")
            print(f"New patterns: {result['new_patterns']}")
            print(f"Conflicts: {result['conflicts']}")
            
            if result['conflicts'] > 0:
                print(f"")
                print(f"Conflict Resolutions:")
                for detail in result["conflict_details"][:10]:  # Show first 10
                    print(f"  {detail['pattern_id']}:")
                    print(f"    Existing confidence: {detail['existing_confidence']:.2f}")
                    print(f"    Imported confidence: {detail['imported_confidence']:.2f}")
                    print(f"    Strategy: {detail['recommendation']}")
                
                if len(result["conflict_details"]) > 10:
                    remaining = len(result["conflict_details"]) - 10
                    print(f"  ... and {remaining} more conflicts")
            
            print(f"")
            print(f"💡 To apply these changes:")
            print(f"   cortex import brain {yaml_path.name} --strategy={args.strategy}")
            
            return 0
            
        elif result.get("success"):
            stats = result["statistics"]
            
            print(f"✅ Import completed successfully!")
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"")
            print(f"📊 Statistics:")
            print(f"   Total patterns: {stats['total_patterns']}")
            print(f"   New patterns: {stats['new_patterns']} (imported)")
            print(f"   Merged patterns: {stats['merged_patterns']} (intelligent merge)")
            print(f"   Replaced patterns: {stats['replaced_patterns']} (overwritten)")
            print(f"   Skipped patterns: {stats['skipped_patterns']} (kept local)")
            
            # Show interesting merge decisions
            merge_decisions = result.get("merge_decisions", [])
            interesting = [d for d in merge_decisions if d["strategy"] == "weighted_merge"]
            
            if interesting:
                print(f"")
                print(f"🧠 Intelligent Merges Applied:")
                for decision in interesting[:5]:  # Show first 5
                    print(f"   {decision['pattern_id']}:")
                    print(f"     {decision['confidence_before']:.2f} → {decision['confidence_after']:.2f}")
                    print(f"     Reason: {decision['reason']}")
            
            return 0
            
        else:
            print(f"❌ Import failed!")
            print(f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print(f"")
            print(f"Errors:")
            for error in result.get("errors", []):
                print(f"  - {error}")
            
            return 1
            
    except Exception as e:
        print(f"❌ Import failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


def main(argv: Optional[List[str]] = None) -> int:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="cortex",
        description="CORTEX Brain Transfer - Export and import knowledge patterns"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Export command
    export_parser = subparsers.add_parser(
        "export",
        help="Export brain patterns to YAML"
    )
    export_subparsers = export_parser.add_subparsers(dest="subcommand")
    
    export_brain_parser = export_subparsers.add_parser(
        "brain",
        help="Export brain patterns"
    )
    export_brain_parser.add_argument(
        "--scope",
        choices=["workspace", "cortex", "all"],
        default="workspace",
        help="Pattern scope to export (default: workspace)"
    )
    export_brain_parser.add_argument(
        "--min-confidence",
        type=float,
        default=0.5,
        help="Minimum confidence threshold (default: 0.5)"
    )
    export_brain_parser.add_argument(
        "--output",
        type=str,
        help="Output file path (auto-generated if not specified)"
    )
    export_brain_parser.add_argument(
        "--local-only",
        action="store_true",
        help="Export without git operations (local only)"
    )
    
    # Import command
    import_parser = subparsers.add_parser(
        "import",
        help="Import brain patterns from YAML"
    )
    import_subparsers = import_parser.add_subparsers(dest="subcommand")
    
    import_brain_parser = import_subparsers.add_parser(
        "brain",
        help="Import brain patterns"
    )
    import_brain_parser.add_argument(
        "file",
        type=str,
        nargs='?',  # Make file optional for auto-detect mode
        help="YAML export file to import (optional - auto-detects if omitted)"
    )
    import_brain_parser.add_argument(
        "--strategy",
        choices=["auto", "replace", "skip"],
        default="auto",
        help="Merge strategy (default: auto - intelligent sniffing)"
    )
    import_brain_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview conflicts without applying changes"
    )
    import_brain_parser.add_argument(
        "--local-only",
        action="store_true",
        help="Import without git operations (local only)"
    )
    
    args = parser.parse_args(argv)
    
    if args.command == "export" and args.subcommand == "brain":
        return export_brain_command(args)
    elif args.command == "import" and args.subcommand == "brain":
        return import_brain_command(args)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
