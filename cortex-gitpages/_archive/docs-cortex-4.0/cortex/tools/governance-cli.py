#!/usr/bin/env python3
"""
Governance CLI Tool - Query and validate governance rules.

This CLI provides developers with direct access to governance rules,
supporting both querying rule details and validating code/projects
against governance standards.

Supported commands:
  cortex-governance query <rule-id|--domain domain|--phase phase>
  cortex-governance validate <path> [--phase PHASE-XX] [--ac-id AC-XXX-XX] [--strict] [--fix]
"""

import argparse
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    yaml = None

# Import from local module
import os
sys.path.insert(0, os.path.dirname(__file__))
from cortex_brain_integration import GovernanceRuleLoader, ValidationEngine


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser for governance CLI."""
    parser = argparse.ArgumentParser(
        prog="cortex-governance",
        description="CORTEX Governance Rules CLI - Query and validate governance compliance",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Query a specific rule
  cortex-governance query CORE-008
  
  # Query all rules by domain
  cortex-governance query --domain tdd
  cortex-governance query --domain orchestration_lifecycle
  
  # Query all rules for a phase
  cortex-governance query --phase PHASE-01
  
  # Validate a directory or file
  cortex-governance validate src/
  cortex-governance validate src/core/intent/recommendation_engine.py
  
  # Validate with phase context
  cortex-governance validate src/ --phase PHASE-09
  
  # Validate specific AC-ID compliance
  cortex-governance validate src/ --ac-id GV-001-01
  
  # Strict validation with auto-fix suggestions
  cortex-governance validate src/ --strict --fix
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Governance command")

    # Query subcommand
    query_parser = subparsers.add_parser(
        "query", help="Query governance rules"
    )
    query_group = query_parser.add_mutually_exclusive_group()
    query_group.add_argument(
        "rule_id",
        nargs="?",
        default=None,
        help="Rule ID to query (e.g., CORE-008, FR-001-01)",
    )
    query_group.add_argument(
        "--domain",
        type=str,
        help="Query all rules in a domain (e.g., tdd, orchestration_lifecycle)",
    )
    query_group.add_argument(
        "--phase",
        type=str,
        help="Query all rules enforced in a phase (e.g., PHASE-01)",
    )
    query_parser.add_argument(
        "--tier",
        type=int,
        choices=[0, 1, 2, 3],
        help="Filter by governance tier (0=immutable, 1=project, 2=engineering, 3=knowledge)",
    )
    query_parser.add_argument(
        "--format",
        choices=["text", "json", "yaml"],
        default="text",
        help="Output format (default: text)",
    )
    query_parser.add_argument(
        "--severity",
        choices=["blocked", "warning", "info"],
        help="Filter by severity level",
    )

    # Validate subcommand
    validate_parser = subparsers.add_parser(
        "validate", help="Validate code or project against governance rules"
    )
    validate_parser.add_argument(
        "path",
        type=str,
        help="Path to validate (file or directory)",
    )
    validate_parser.add_argument(
        "--phase",
        type=str,
        help="Phase context for validation (e.g., PHASE-09)",
    )
    validate_parser.add_argument(
        "--ac-id",
        type=str,
        help="Specific AC-ID to validate against (e.g., GV-001-01)",
    )
    validate_parser.add_argument(
        "--strict",
        action="store_true",
        help="Enable strict validation (fail on warnings)",
    )
    validate_parser.add_argument(
        "--fix",
        action="store_true",
        help="Suggest auto-fixable violations",
    )
    validate_parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    return parser


def format_rule_text(rule: Dict[str, Any]) -> str:
    """Format a single rule for text output."""
    rule_id = rule.get("rule_id", "UNKNOWN")
    name = rule.get("name", "")
    category = rule.get("category", "")
    severity = rule.get("severity", "")
    description = rule.get("description", "").strip()

    lines = [
        f"Rule ID:    {rule_id}",
        f"Name:       {name}",
        f"Category:   {category}",
        f"Severity:   {severity}",
        f"Description:\n  {description.replace(chr(10), chr(10) + '  ')}",
    ]

    if "validation" in rule:
        lines.append(f"Validation:")
        for item in rule["validation"]:
            lines.append(f"  • {item}")

    return "\n".join(lines)


def handle_query(args: argparse.Namespace) -> int:
    """Handle 'query' subcommand."""
    try:
        start_time = time.time()
        loader = GovernanceRuleLoader()

        rules: List[Dict[str, Any]] = []

        if args.rule_id:
            # Query specific rule
            rule = loader.get_rule_by_id(args.rule_id)
            if rule is None:
                print(
                    f"ERROR: Rule '{args.rule_id}' not found",
                    file=sys.stderr,
                )
                return 1
            rules = [rule]
        elif args.domain:
            # Query by domain
            rules = loader.get_rules_by_domain(args.domain)
            if not rules:
                print(
                    f"ERROR: No rules found in domain '{args.domain}'",
                    file=sys.stderr,
                )
                return 1
        elif args.phase:
            # Query by phase
            rules = loader.get_rules_for_phase(args.phase)
            if not rules:
                print(
                    f"ERROR: No rules found for phase '{args.phase}'",
                    file=sys.stderr,
                )
                return 1
        else:
            # No filter specified
            print(
                "ERROR: Must specify --rule_id, --domain, or --phase",
                file=sys.stderr,
            )
            return 1

        # Apply additional filters
        if args.tier is not None:
            rules = [
                r for r in rules
                if r.get("governance_tier") == args.tier
            ]

        if args.severity:
            rules = [
                r for r in rules
                if r.get("severity") == args.severity
            ]

        elapsed = time.time() - start_time

        # Output
        if args.format == "json":
            print(json.dumps(rules, indent=2))
        elif args.format == "yaml":
            if yaml is None:
                print(
                    "ERROR: YAML format requires PyYAML to be installed",
                    file=sys.stderr,
                )
                return 1
            print(yaml.dump(rules, default_flow_style=False))
        else:
            # Text format
            for i, rule in enumerate(rules):
                if i > 0:
                    print("\n" + "=" * 70)
                print(format_rule_text(rule))

        print(f"\n✓ Found {len(rules)} rule(s) in {elapsed:.2f}ms",
              file=sys.stderr)
        return 0

    except Exception as e:
        print(f"ERROR: Query failed - {e}", file=sys.stderr)
        return 1


def handle_validate(args: argparse.Namespace) -> int:
    """Handle 'validate' subcommand."""
    try:
        start_time = time.time()
        path = Path(args.path)

        if not path.exists():
            print(f"ERROR: Path '{args.path}' does not exist",
                  file=sys.stderr)
            return 1

        engine = ValidationEngine(
            phase=args.phase,
            ac_id=args.ac_id,
            strict=args.strict,
        )

        violations = engine.validate_path(path)

        elapsed = time.time() - start_time

        # Output
        if args.format == "json":
            print(json.dumps({
                "path": str(path),
                "violations_count": len(violations),
                "violations": violations,
                "elapsed_ms": f"{elapsed * 1000:.2f}",
            }, indent=2))
        else:
            # Text format
            if violations:
                print(f"\n🚫 Found {len(violations)} violation(s) in {elapsed*1000:.2f}ms:")
                for i, violation in enumerate(violations, 1):
                    print(
                        f"\n  {i}. {violation.get('rule_id', 'UNKNOWN')}: "
                        f"{violation.get('message', '')}"
                    )
                    if violation.get("file"):
                        print(f"     File: {violation['file']}")
                    if violation.get("line"):
                        print(f"     Line: {violation['line']}")
                    if args.fix and violation.get("fix_suggestion"):
                        print(f"     Fix: {violation['fix_suggestion']}")
            else:
                print(
                    f"✓ No violations found in {elapsed*1000:.2f}ms"
                )

        exit_code = 1 if violations else 0
        return exit_code

    except Exception as e:
        print(f"ERROR: Validation failed - {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main entry point for governance CLI."""
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    if args.command == "query":
        return handle_query(args)
    elif args.command == "validate":
        return handle_validate(args)
    else:
        print(f"ERROR: Unknown command '{args.command}'",
              file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
