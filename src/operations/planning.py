"""
Planning CLI Wrapper

Command-line interface for planning utility.
Provides formatted output for feature planning operations.

Usage:
    python3 -m src.operations.planning create <feature_name> [--description DESC] [--complexity LEVEL]
    python3 -m src.operations.planning validate <plan_file>
    python3 -m src.operations.planning approve <plan_file>
    python3 -m src.operations.planning complete <plan_file>
    python3 -m src.operations.planning view <plan_file> [--markdown]

Version: 3.0.0
Author: Asif Hussain
"""

import sys
from pathlib import Path

# Add CORTEX root to path for imports
cortex_root = Path(__file__).resolve().parents[2]
if str(cortex_root) not in sys.path:
    sys.path.insert(0, str(cortex_root))

from src.operations.modules.planning.planning_utility import (
    create_plan,
    load_plan,
    save_plan,
    validate_plan,
    generate_markdown,
    approve_plan,
    complete_plan
)


def run_planning(**kwargs) -> dict:
    """
    Wrapper for planning utility - follows CORTEX operations pattern.
    
    Args:
        **kwargs: Arguments passed to planning utility functions
        
    Returns:
        Result dictionary from utility
    """
    action = kwargs.get("action")
    
    if action == "create":
        result = create_plan(
            feature_name=kwargs.get("feature_name"),
            description=kwargs.get("description", ""),
            author=kwargs.get("author", "CORTEX"),
            complexity=kwargs.get("complexity", "medium")
        )
    elif action == "validate":
        load_result = load_plan(Path(kwargs.get("plan_file")))
        if not load_result.success:
            return {
                "success": False,
                "message": load_result.message,
                "errors": load_result.errors
            }
        result = validate_plan(load_result.plan_data)
        return {
            "success": result.valid,
            "message": "Validation passed" if result.valid else "Validation failed",
            "errors": result.errors,
            "warnings": result.warnings
        }
    elif action == "approve":
        result = approve_plan(kwargs.get("plan_file"))
    elif action == "complete":
        result = complete_plan(kwargs.get("plan_file"))
    elif action == "view":
        load_result = load_plan(Path(kwargs.get("plan_file")))
        if not load_result.success:
            return {
                "success": False,
                "message": load_result.message,
                "errors": load_result.errors
            }
        if kwargs.get("markdown"):
            markdown = generate_markdown(load_result.plan_data)
            return {
                "success": True,
                "message": "Markdown generated",
                "content": markdown
            }
        else:
            return {
                "success": True,
                "message": "Plan loaded",
                "plan_data": load_result.plan_data
            }
    else:
        return {
            "success": False,
            "message": f"Unknown action: {action}"
        }
    
    return {
        "success": result.success,
        "message": result.message,
        "plan_path": str(result.plan_path) if result.plan_path else None,
        "errors": result.errors if hasattr(result, 'errors') else [],
        "details": result.details if hasattr(result, 'details') else None
    }


def main():
    """CLI entry point with formatted output."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CORTEX Planning Utility - Feature Planning Management",
        epilog="Create, validate, approve, and manage feature plans"
    )
    
    subparsers = parser.add_subparsers(dest="action", help="Action to perform")
    
    # Create command
    create_parser = subparsers.add_parser("create", help="Create new plan")
    create_parser.add_argument("feature_name", help="Name of feature")
    create_parser.add_argument("--description", "-d", help="Feature description")
    create_parser.add_argument("--author", "-a", default="CORTEX", help="Plan author")
    create_parser.add_argument("--complexity", "-c", choices=["low", "medium", "high", "critical"],
                                default="medium", help="Complexity level")
    
    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate plan")
    validate_parser.add_argument("plan_file", help="Plan filename")
    
    # Approve command
    approve_parser = subparsers.add_parser("approve", help="Approve plan (moves to active)")
    approve_parser.add_argument("plan_file", help="Plan filename")
    
    # Complete command
    complete_parser = subparsers.add_parser("complete", help="Complete plan (moves to completed)")
    complete_parser.add_argument("plan_file", help="Plan filename")
    
    # View command
    view_parser = subparsers.add_parser("view", help="View plan")
    view_parser.add_argument("plan_file", help="Plan filename")
    view_parser.add_argument("--markdown", "-m", action="store_true", help="Show as Markdown")
    
    args = parser.parse_args()
    
    if not args.action:
        parser.print_help()
        sys.exit(1)
    
    print("=" * 60)
    print(f"📋 CORTEX Planning - {args.action.upper()}")
    print("=" * 60)
    
    # Build kwargs for utility
    kwargs = {"action": args.action}
    
    if args.action == "create":
        kwargs.update({
            "feature_name": args.feature_name,
            "description": args.description or "",
            "author": args.author,
            "complexity": args.complexity
        })
    elif args.action in ["validate", "approve", "complete", "view"]:
        kwargs["plan_file"] = args.plan_file
        if args.action == "view" and hasattr(args, "markdown"):
            kwargs["markdown"] = args.markdown
    
    # Execute utility
    result = run_planning(**kwargs)
    
    # Display results
    print(f"\nStatus: {'✅ SUCCESS' if result['success'] else '❌ FAILED'}")
    print(f"Message: {result['message']}")
    
    if result.get("plan_path"):
        print(f"Plan Path: {result['plan_path']}")
    
    if result.get("errors"):
        print(f"\n❌ Errors ({len(result['errors'])}):")
        for error in result["errors"]:
            print(f"  - {error}")
    
    if result.get("warnings"):
        print(f"\n⚠️  Warnings ({len(result['warnings'])}):")
        for warning in result["warnings"]:
            print(f"  - {warning}")
    
    if result.get("details"):
        print(f"\nDetails:\n{result['details']}")
    
    if result.get("content"):
        print(f"\n{'='*60}")
        print(result["content"])
        print("=" * 60)
    
    if result.get("plan_data") and not result.get("content"):
        import json
        print(f"\n{'='*60}")
        print("Plan Data (JSON):")
        print(json.dumps(result["plan_data"], indent=2, default=str))
        print("=" * 60)
    
    print("\n" + "=" * 60)
    
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
