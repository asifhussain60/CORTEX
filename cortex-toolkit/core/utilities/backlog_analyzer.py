#!/usr/bin/env python3
"""
CORTEX Backlog Analyzer

Holistic analysis and TDD evaluation tool for backlog items.
Ensures autonomous execution readiness before implementation.

Usage:
    python backlog_analyzer.py --file ".asif/backlog/15-docgen-prompt.md" --mode holistic
    python backlog_analyzer.py --file ".asif/backlog/15-docgen-prompt.md" --evaluate-tdd
    python backlog_analyzer.py --file ".asif/backlog/15-docgen-prompt.md" --full

Author: Asif Hussain
Version: 1.0.0
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any


# TDD High-Value Indicators (regex patterns)
TDD_HIGH_VALUE_PATTERNS = {
    "core_logic": [
        r"algorithm", r"calculation", r"business.*rule", r"logic",
        r"compute", r"process.*data", r"transform"
    ],
    "data_transformation": [
        r"pars(e|ing)", r"format", r"convert", r"serialize",
        r"deserialize", r"encode", r"decode", r"extract"
    ],
    "api_contract": [
        r"api", r"endpoint", r"request", r"response",
        r"input.*output", r"schema", r"validate.*input"
    ],
    "complex_conditionals": [
        r"if.*else", r"switch", r"case", r"condition",
        r"branch", r"decision.*tree", r"state.*machine"
    ],
    "regression_prone": [
        r"refactor", r"rewrite", r"migrate", r"upgrade",
        r"breaking.*change", r"critical.*path"
    ]
}

# TDD Low-Value Indicators
TDD_LOW_VALUE_PATTERNS = {
    "documentation": [
        r"readme", r"markdown", r"document", r"\.md\b",
        r"comment", r"docstring", r"jsdoc"
    ],
    "configuration": [
        r"config", r"yaml", r"json", r"setting",
        r"environment", r"\.env\b", r"parameter"
    ],
    "styling": [
        r"css", r"style", r"theme", r"color",
        r"font", r"layout", r"ui.*design"
    ],
    "file_operations": [
        r"move.*file", r"rename", r"delete.*file", r"copy.*file",
        r"mkdir", r"rm\s+-", r"reorganize"
    ]
}

# Autonomy Gap Patterns
AUTONOMY_GAP_PATTERNS = {
    "vague_reference": [
        r"\bthe file\b", r"\bthe config\b", r"\bthe script\b",
        r"\bthe module\b", r"\bthe component\b", r"\bthat file\b"
    ],
    "placeholder": [
        r"\{[a-z_]+\}", r"<[A-Z_]+>", r"\[TODO\]",
        r"XXX", r"FIXME"
    ],
    "human_judgment": [
        r"if appropriate", r"as needed", r"when necessary",
        r"if required", r"optionally", r"you may"
    ],
    "ambiguous_verb": [
        r"\bupdate\b(?!\s+`)", r"\bfix\b(?!\s+`)", r"\bimprove\b",
        r"\bmodify\b(?!\s+`)", r"\bchange\b(?!\s+`)"
    ],
    "missing_path": [
        r"edit the .* file", r"open the .* file",
        r"in the .* directory"
    ]
}


def load_backlog_file(file_path: str) -> str:
    """Load backlog file content."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Backlog file not found: {file_path}")
    return path.read_text(encoding="utf-8")


def evaluate_tdd_value(content: str) -> dict[str, Any]:
    """
    Evaluate if TDD adds HIGH value to this backlog item.
    
    Returns:
        dict with tdd_value (HIGH/LOW), indicators, recommendation
    """
    content_lower = content.lower()
    
    high_indicators = []
    low_indicators = []
    
    # Check high-value patterns
    for category, patterns in TDD_HIGH_VALUE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, content_lower):
                high_indicators.append(category)
                break  # One match per category is enough
    
    # Check low-value patterns
    for category, patterns in TDD_LOW_VALUE_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, content_lower):
                low_indicators.append(category)
                break
    
    # Decision logic
    high_count = len(set(high_indicators))
    low_count = len(set(low_indicators))
    
    # HIGH if 2+ high-value indicators OR core_logic/api_contract present
    if high_count >= 2 or "core_logic" in high_indicators or "api_contract" in high_indicators:
        tdd_value = "HIGH"
        recommendation = "Add TDD section with RED→GREEN→REFACTOR phases"
    elif high_count >= 1 and low_count == 0:
        tdd_value = "HIGH"
        recommendation = "TDD recommended - single high-value indicator detected"
    elif low_count >= 2 and high_count == 0:
        tdd_value = "LOW"
        recommendation = "Manual verification sufficient - documentation/config work"
    else:
        tdd_value = "LOW"
        recommendation = "TDD optional - mixed indicators, lean toward manual verification"
    
    # Generate test file suggestion
    match = re.search(r"#\s*[🔧📚🚀⚡]\s*(.+)", content)
    if match:
        feature_name = match.group(1).lower()
        feature_name = re.sub(r"[^a-z0-9]+", "_", feature_name)[:30]
        test_file = f"tests/test_{feature_name}.py"
    else:
        test_file = "tests/test_feature.py"
    
    return {
        "tdd_value": tdd_value,
        "high_indicators": list(set(high_indicators)),
        "low_indicators": list(set(low_indicators)),
        "recommendation": recommendation,
        "test_file_suggestion": test_file,
        "confidence": "HIGH" if (high_count >= 2 or low_count >= 2) else "MEDIUM"
    }


def detect_autonomy_gaps(content: str) -> dict[str, Any]:
    """
    Detect autonomy gaps that would prevent autonomous execution.
    
    Returns:
        dict with gaps categorized by type
    """
    gaps = {}
    total_gaps = 0
    
    for gap_type, patterns in AUTONOMY_GAP_PATTERNS.items():
        matches = []
        for pattern in patterns:
            found = re.findall(pattern, content, re.IGNORECASE)
            matches.extend(found)
        
        if matches:
            gaps[gap_type] = {
                "count": len(matches),
                "examples": list(set(matches))[:5]  # Limit examples
            }
            total_gaps += len(matches)
    
    # Calculate autonomy score
    lines = content.split("\n")
    code_blocks = len(re.findall(r"```", content)) // 2
    verification_commands = len(re.findall(r"verify:|expected:|✅", content, re.IGNORECASE))
    
    # Higher score = more autonomous
    base_score = 100
    penalty = total_gaps * 5  # Each gap costs 5 points
    bonus = verification_commands * 3  # Each verification adds 3 points
    bonus += code_blocks * 2  # Code blocks add 2 points
    
    autonomy_score = max(0, min(100, base_score - penalty + bonus))
    
    return {
        "autonomy_score": autonomy_score,
        "total_gaps": total_gaps,
        "gaps_by_type": gaps,
        "ready_for_execution": autonomy_score >= 80 and total_gaps <= 3,
        "verification_commands_found": verification_commands,
        "code_blocks_found": code_blocks
    }


def analyze_structure(content: str) -> dict[str, Any]:
    """
    Analyze backlog item structure compliance.
    """
    checks = {
        "has_header": bool(re.search(r"^#\s+[🔧📚🚀⚡💡🎯]", content, re.MULTILINE)),
        "has_metadata": bool(re.search(r"\*\*Priority:\*\*.*\*\*Effort:\*\*", content)),
        "has_objective": bool(re.search(r"##\s*🎯\s*Objective", content)),
        "has_steps": bool(re.search(r"##\s*📋\s*Execution Steps", content)),
        "has_success_criteria": bool(re.search(r"##\s*✅\s*Success Criteria", content)),
        "has_auto_delete": bool(re.search(r"AUTO-DELETE|rm\s+-f", content)),
        "has_checkpoints": bool(re.search(r"Checkpoint|CHECKPOINT", content)),
    }
    
    compliance_score = sum(checks.values()) / len(checks) * 100
    
    return {
        "structure_checks": checks,
        "compliance_score": compliance_score,
        "missing_sections": [k for k, v in checks.items() if not v]
    }


def full_analysis(file_path: str) -> dict[str, Any]:
    """
    Perform full holistic analysis including TDD evaluation.
    """
    content = load_backlog_file(file_path)
    
    return {
        "file": file_path,
        "structure": analyze_structure(content),
        "autonomy": detect_autonomy_gaps(content),
        "tdd_evaluation": evaluate_tdd_value(content),
        "summary": {
            "ready_for_execution": False,  # Will be set below
            "refinements_needed": 0,
            "recommendation": ""
        }
    }


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CORTEX Backlog Analyzer - Holistic analysis and TDD evaluation"
    )
    parser.add_argument(
        "--file", "-f",
        required=True,
        help="Path to backlog file to analyze"
    )
    parser.add_argument(
        "--mode", "-m",
        choices=["holistic", "structure", "autonomy"],
        default="holistic",
        help="Analysis mode (default: holistic)"
    )
    parser.add_argument(
        "--evaluate-tdd",
        action="store_true",
        help="Only evaluate TDD value"
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Full analysis including all checks"
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON"
    )
    
    args = parser.parse_args()
    
    try:
        content = load_backlog_file(args.file)
        
        if args.evaluate_tdd:
            result = evaluate_tdd_value(content)
        elif args.full:
            result = full_analysis(args.file)
        elif args.mode == "structure":
            result = analyze_structure(content)
        elif args.mode == "autonomy":
            result = detect_autonomy_gaps(content)
        else:  # holistic
            result = {
                "structure": analyze_structure(content),
                "autonomy": detect_autonomy_gaps(content),
                "tdd_evaluation": evaluate_tdd_value(content)
            }
        
        if args.json:
            print(json.dumps(result, indent=2))
        else:
            # Pretty print
            print(f"\n{'='*60}")
            print(f"📊 CORTEX Backlog Analysis: {args.file}")
            print(f"{'='*60}\n")
            
            if args.evaluate_tdd:
                print(f"🧪 TDD Value: {result['tdd_value']}")
                print(f"   High Indicators: {', '.join(result['high_indicators']) or 'None'}")
                print(f"   Low Indicators: {', '.join(result['low_indicators']) or 'None'}")
                print(f"   Recommendation: {result['recommendation']}")
                print(f"   Test File: {result['test_file_suggestion']}")
            else:
                if "structure" in result:
                    print(f"📋 Structure Compliance: {result['structure']['compliance_score']:.0f}%")
                    if result['structure']['missing_sections']:
                        print(f"   Missing: {', '.join(result['structure']['missing_sections'])}")
                
                if "autonomy" in result:
                    print(f"\n🔍 Autonomy Score: {result['autonomy']['autonomy_score']}%")
                    print(f"   Total Gaps: {result['autonomy']['total_gaps']}")
                    print(f"   Ready: {'✅ YES' if result['autonomy']['ready_for_execution'] else '❌ NO'}")
                
                if "tdd_evaluation" in result:
                    tdd = result['tdd_evaluation']
                    print(f"\n🧪 TDD Value: {tdd['tdd_value']}")
                    print(f"   Recommendation: {tdd['recommendation']}")
            
            print(f"\n{'='*60}\n")
        
    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
