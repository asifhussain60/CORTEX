"""
ADO CLI - Azure DevOps Work Item Management

Command-line interface for ADO utility operations.

Commands:
  create        - Create new work item
  load          - Load existing work item
  update        - Update work item fields
  summary       - Generate completion summary
  validate-dor  - Validate Definition of Ready
  validate-dod  - Validate Definition of Done
  list          - List work items by status

Usage:
  python -m src.operations.ado create story "My Story" "Description" --priority 1
  python -m src.operations.ado load <work-item-id>
  python -m src.operations.ado update <work-item-id> --status completed
  python -m src.operations.ado summary <work-item-id> --files-created file1.py file2.py
  python -m src.operations.ado validate-dor <work-item-id>
  python -m src.operations.ado validate-dod <work-item-id>
  python -m src.operations.ado list --status active

Version: 3.0.0 (Utility Migration)
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import argparse
import sys
import json
from pathlib import Path
from typing import List

# Import ADO utility operations
from src.operations.modules.ado.ado_utility import (
    create_work_item,
    load_work_item,
    update_work_item,
    generate_summary,
    validate_dor,
    validate_dod,
    list_work_items,
    WorkItemType,
    WorkItemStatus,
    WorkItemResult,
    ValidationResult
)


def format_work_item_result(result: WorkItemResult, json_output: bool = False) -> str:
    """Format work item result for display."""
    if json_output:
        data = {
            "success": result.success,
            "message": result.message,
            "work_item_id": result.work_item_id,
            "errors": result.errors
        }
        if result.metadata:
            data["metadata"] = {
                "type": result.metadata.work_item_type.value,
                "title": result.metadata.title,
                "status": result.metadata.status.value,
                "priority": result.metadata.priority
            }
        return json.dumps(data, indent=2)
    
    # Text output
    output = []
    
    if result.success:
        output.append(f"✅ {result.message}")
        if result.work_item_id:
            output.append(f"\n📋 Work Item ID: {result.work_item_id}")
        if result.metadata:
            output.append(f"\n📝 Title: {result.metadata.title}")
            output.append(f"Type: {result.metadata.work_item_type.value}")
            output.append(f"Status: {result.metadata.status.value.upper()}")
            output.append(f"Priority: {result.metadata.priority}")
            if result.metadata.tags:
                output.append(f"Tags: {', '.join(result.metadata.tags)}")
    else:
        output.append(f"❌ {result.message}")
        if result.errors:
            output.append("\nErrors:")
            for error in result.errors:
                output.append(f"  - {error}")
    
    if result.file_path:
        output.append(f"\n📁 File: {result.file_path}")
    
    return "\n".join(output)


def format_validation_result(result: ValidationResult, json_output: bool = False) -> str:
    """Format validation result for display."""
    if json_output:
        return json.dumps({
            "passed": result.passed,
            "score": result.score,
            "total_points": result.total_points,
            "earned_points": result.earned_points,
            "passed_checks": result.passed_checks,
            "failed_checks": result.failed_checks,
            "warnings": result.warnings,
            "recommendations": result.recommendations
        }, indent=2)
    
    # Text output
    output = []
    
    # Header
    status_icon = "✅" if result.passed else "❌"
    output.append(f"{status_icon} {result.validation_type} Validation")
    output.append("=" * 60)
    
    # Score
    score_bar = "█" * int(result.score / 5) + "░" * (20 - int(result.score / 5))
    output.append(f"\nScore: {result.score:.1f}% [{score_bar}]")
    output.append(f"Points: {result.earned_points}/{result.total_points}")
    output.append(f"Status: {'PASSED ✅' if result.passed else 'FAILED ❌'}")
    
    # Passed checks
    if result.passed_checks:
        output.append(f"\n✅ Passed Checks ({len(result.passed_checks)}):")
        for check in result.passed_checks:
            output.append(f"  ✓ {check}")
    
    # Failed checks
    if result.failed_checks:
        output.append(f"\n❌ Failed Checks ({len(result.failed_checks)}):")
        for check in result.failed_checks:
            output.append(f"  ✗ {check}")
    
    # Warnings
    if result.warnings:
        output.append(f"\n⚠️  Warnings ({len(result.warnings)}):")
        for warning in result.warnings:
            output.append(f"  ⚠️  {warning}")
    
    # Recommendations
    if result.recommendations:
        output.append(f"\n💡 Recommendations ({len(result.recommendations)}):")
        for rec in result.recommendations:
            output.append(f"  💡 {rec}")
    
    return "\n".join(output)


def cmd_create(args: argparse.Namespace) -> int:
    """Create work item command."""
    # Parse work item type
    type_map = {
        "story": WorkItemType.STORY,
        "feature": WorkItemType.FEATURE,
        "bug": WorkItemType.BUG,
        "task": WorkItemType.TASK,
        "epic": WorkItemType.EPIC
    }
    
    work_item_type = type_map.get(args.type.lower())
    if not work_item_type:
        print(f"❌ Invalid type: {args.type}")
        print(f"Valid types: story, feature, bug, task, epic")
        return 1
    
    # Build kwargs
    kwargs = {}
    if args.priority:
        kwargs["priority"] = args.priority
    if args.tags:
        kwargs["tags"] = args.tags
    if args.acceptance_criteria:
        kwargs["acceptance_criteria"] = args.acceptance_criteria
    if args.assigned_to:
        kwargs["assigned_to"] = args.assigned_to
    if args.iteration:
        kwargs["iteration"] = args.iteration
    
    result = create_work_item(
        work_item_type=work_item_type,
        title=args.title,
        description=args.description,
        **kwargs
    )
    
    print(format_work_item_result(result, args.json))
    return 0 if result.success else 1


def cmd_load(args: argparse.Namespace) -> int:
    """Load work item command."""
    result = load_work_item(args.work_item_id)
    
    print(format_work_item_result(result, args.json))
    
    if result.success and not args.json:
        # Show additional details
        metadata = result.metadata
        print("\n" + "=" * 60)
        print("Work Item Details")
        print("=" * 60)
        if metadata.description:
            print(f"\nDescription:\n{metadata.description[:200]}...")
        if metadata.acceptance_criteria:
            print(f"\nAcceptance Criteria ({len(metadata.acceptance_criteria)}):")
            for i, criterion in enumerate(metadata.acceptance_criteria, 1):
                print(f"  {i}. {criterion}")
        print(f"\nCreated: {metadata.created_date}")
        print(f"Updated: {metadata.updated_date}")
    
    return 0 if result.success else 1


def cmd_update(args: argparse.Namespace) -> int:
    """Update work item command."""
    updates = {}
    
    if args.status:
        updates["status"] = args.status
    if args.priority:
        updates["priority"] = args.priority
    if args.assigned_to:
        updates["assigned_to"] = args.assigned_to
    if args.iteration:
        updates["iteration"] = args.iteration
    if args.tags:
        updates["tags"] = args.tags
    
    if not updates:
        print("❌ No updates specified. Use --status, --priority, --assigned-to, etc.")
        return 1
    
    result = update_work_item(args.work_item_id, **updates)
    
    print(format_work_item_result(result, args.json))
    return 0 if result.success else 1


def cmd_summary(args: argparse.Namespace) -> int:
    """Generate summary command."""
    summary_data = {}
    
    if args.files_created:
        summary_data["files_created"] = args.files_created
    if args.files_modified:
        summary_data["files_modified"] = args.files_modified
    if args.tests_created:
        summary_data["tests_created"] = args.tests_created
    if args.documentation_created:
        summary_data["documentation_created"] = args.documentation_created
    if args.code_changes_count is not None:
        summary_data["code_changes_count"] = args.code_changes_count
    if args.test_coverage is not None:
        summary_data["test_coverage"] = args.test_coverage
    if args.duration_hours is not None:
        summary_data["duration_hours"] = args.duration_hours
    if args.implementation_notes:
        summary_data["implementation_notes"] = args.implementation_notes
    
    result = generate_summary(args.work_item_id, **summary_data)
    
    print(format_work_item_result(result, args.json))
    
    if result.success and result.file_path:
        print(f"\n✅ Summary saved to: {result.file_path}")
    
    return 0 if result.success else 1


def cmd_validate_dor(args: argparse.Namespace) -> int:
    """Validate DoR command."""
    # Load work item
    load_result = load_work_item(args.work_item_id)
    if not load_result.success:
        print(format_work_item_result(load_result, args.json))
        return 1
    
    # Validate
    validation_result = validate_dor(
        load_result.metadata,
        ambiguity_score=args.ambiguity_score
    )
    
    print(format_validation_result(validation_result, args.json))
    return 0 if validation_result.passed else 1


def cmd_validate_dod(args: argparse.Namespace) -> int:
    """Validate DoD command."""
    # This requires a summary file or summary data
    # For now, create a minimal summary from work item
    load_result = load_work_item(args.work_item_id)
    if not load_result.success:
        print(format_work_item_result(load_result, args.json))
        return 1
    
    # Create minimal summary for validation
    from src.operations.modules.ado.ado_utility import WorkItemSummary
    
    summary = WorkItemSummary(
        work_item_id=args.work_item_id,
        work_item_type=load_result.metadata.work_item_type,
        title=load_result.metadata.title,
        code_changes_count=args.code_changes_count or 0,
        test_coverage=args.test_coverage or 0.0,
        tests_created=args.tests_created or [],
        files_created=args.files_created or [],
        acceptance_criteria_met=args.acceptance_criteria_met or []
    )
    
    validation_result = validate_dod(summary)
    
    print(format_validation_result(validation_result, args.json))
    return 0 if validation_result.passed else 1


def cmd_list(args: argparse.Namespace) -> int:
    """List work items command."""
    status = None
    if args.status:
        try:
            status = WorkItemStatus(args.status)
        except ValueError:
            valid_statuses = [s.value for s in WorkItemStatus]
            print(f"❌ Invalid status: {args.status}")
            print(f"Valid statuses: {', '.join(valid_statuses)}")
            return 1
    
    result = list_work_items(status)
    
    if args.json:
        print(format_work_item_result(result, True))
    else:
        print(f"{'=' * 60}")
        print(f"ADO Work Items {f'({status.value.upper()})' if status else '(ALL)'}")
        print(f"{'=' * 60}\n")
        
        if result.success:
            print(f"✅ {result.message}\n")
            
            # Since list_work_items doesn't return all items in result.metadata,
            # we need to call it differently or access internal data
            # For now, just show the message
            if result.errors:
                print("No work items found.")
            else:
                print("Use 'load <work-item-id>' to view details.")
        else:
            print(f"❌ {result.message}")
            if result.errors:
                for error in result.errors:
                    print(f"  - {error}")
    
    return 0 if result.success else 1


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="ADO CLI - Azure DevOps Work Item Management",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="ADO command")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create new work item")
    create_parser.add_argument("type", help="Work item type (story, feature, bug, task, epic)")
    create_parser.add_argument("title", help="Work item title")
    create_parser.add_argument("description", help="Work item description")
    create_parser.add_argument("--priority", type=int, choices=[1,2,3,4], help="Priority (1=High, 4=Very Low)")
    create_parser.add_argument("--tags", nargs="+", help="Tags")
    create_parser.add_argument("--acceptance-criteria", nargs="+", help="Acceptance criteria")
    create_parser.add_argument("--assigned-to", help="Assigned to")
    create_parser.add_argument("--iteration", help="Iteration")
    create_parser.set_defaults(func=cmd_create)
    
    # Load command
    load_parser = subparsers.add_parser("load", help="Load existing work item")
    load_parser.add_argument("work_item_id", help="Work item ID")
    load_parser.set_defaults(func=cmd_load)
    
    # Update command
    update_parser = subparsers.add_parser("update", help="Update work item")
    update_parser.add_argument("work_item_id", help="Work item ID")
    update_parser.add_argument("--status", choices=["active", "completed", "blocked", "cancelled"], help="Status")
    update_parser.add_argument("--priority", type=int, choices=[1,2,3,4], help="Priority")
    update_parser.add_argument("--assigned-to", help="Assigned to")
    update_parser.add_argument("--iteration", help="Iteration")
    update_parser.add_argument("--tags", nargs="+", help="Tags")
    update_parser.set_defaults(func=cmd_update)
    
    # Summary command
    summary_parser = subparsers.add_parser("summary", help="Generate completion summary")
    summary_parser.add_argument("work_item_id", help="Work item ID")
    summary_parser.add_argument("--files-created", nargs="+", help="Files created")
    summary_parser.add_argument("--files-modified", nargs="+", help="Files modified")
    summary_parser.add_argument("--tests-created", nargs="+", help="Tests created")
    summary_parser.add_argument("--documentation-created", nargs="+", help="Documentation created")
    summary_parser.add_argument("--code-changes-count", type=int, help="Number of code changes")
    summary_parser.add_argument("--test-coverage", type=float, help="Test coverage percentage")
    summary_parser.add_argument("--duration-hours", type=float, help="Duration in hours")
    summary_parser.add_argument("--implementation-notes", help="Implementation notes")
    summary_parser.set_defaults(func=cmd_summary)
    
    # Validate DoR command
    validate_dor_parser = subparsers.add_parser("validate-dor", help="Validate Definition of Ready")
    validate_dor_parser.add_argument("work_item_id", help="Work item ID")
    validate_dor_parser.add_argument("--ambiguity-score", type=int, default=0, help="Ambiguity score")
    validate_dor_parser.set_defaults(func=cmd_validate_dor)
    
    # Validate DoD command
    validate_dod_parser = subparsers.add_parser("validate-dod", help="Validate Definition of Done")
    validate_dod_parser.add_argument("work_item_id", help="Work item ID")
    validate_dod_parser.add_argument("--code-changes-count", type=int, help="Number of code changes")
    validate_dod_parser.add_argument("--test-coverage", type=float, help="Test coverage percentage")
    validate_dod_parser.add_argument("--tests-created", nargs="+", help="Tests created")
    validate_dod_parser.add_argument("--files-created", nargs="+", help="Files created")
    validate_dod_parser.add_argument("--acceptance-criteria-met", nargs="+", help="Acceptance criteria met")
    validate_dod_parser.set_defaults(func=cmd_validate_dod)
    
    # List command
    list_parser = subparsers.add_parser("list", help="List work items")
    list_parser.add_argument("--status", choices=["active", "completed", "blocked", "cancelled"], help="Filter by status")
    list_parser.set_defaults(func=cmd_list)
    
    # Parse arguments
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Execute command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
