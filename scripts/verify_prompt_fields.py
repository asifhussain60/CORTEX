#!/usr/bin/env python3
"""
Verify Prompt Fields Pre-Commit Hook

Ensures that fields documented in prompt files (CORTEX.prompt.md, copilot-instructions.md)
are actually implemented in the corresponding code files.

This prevents documentation-code drift (AC-PERMANENT-FIX-010 pattern).

Usage:
    python scripts/verify_prompt_fields.py [--fix]

Exit Codes:
    0: All fields verified
    1: Missing fields detected
    2: Script error

AC-ID: REM-001 (Prevention Measure)
Phase: 16 (Remediation Framework)
Author: Asif Hussain
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple, Set
from dataclasses import dataclass


@dataclass
class FieldSpec:
    """Field specification from prompt documentation."""
    field_name: str
    context: str  # Where it was found
    line_number: int


@dataclass
class ValidationResult:
    """Result of field validation."""
    field_name: str
    exists_in_code: bool
    rendered_in_output: bool
    code_location: str = ""
    render_location: str = ""


class PromptFieldVerifier:
    """Verifies prompt-documented fields exist in code."""
    
    def __init__(self, cortex_root: Path):
        """
        Initialize verifier.
        
        Args:
            cortex_root: Root directory of CORTEX project
        """
        self.cortex_root = cortex_root
        self.prompt_file = cortex_root / ".github/prompts/CORTEX.prompt.md"
        self.instructions_file = cortex_root / ".github/copilot-instructions.md"
        self.dor_gate_file = cortex_root / "cortex/orchestrators/core/dor_approval_gate.py"
    
    def extract_dor_fields_from_prompts(self) -> List[FieldSpec]:
        """
        Extract DoR field specifications from prompt files.
        
        Returns:
            List of field specifications
        """
        fields: List[FieldSpec] = []
        
        # Map display names in prompts to actual field names in IntentReflection
        field_name_mapping = {
            "intent": "intent_type",
            "handler": "target_handler",
            "dor confidence": "dor_confidence",
            "scope": "scope",
            "impact": "estimated_impact",
            "entities": "key_entities",
            "business principles": "business_principles",
            "rules": "governance_rules",
        }
        
        # Pattern for DoR table rows: | **Field** | value |
        field_pattern = re.compile(r'\|\s*\*\*([A-Z][a-zA-Z\s]+)\*\*\s*\|')
        
        for prompt_file in [self.prompt_file, self.instructions_file]:
            if not prompt_file.exists():
                continue
            
            with open(prompt_file) as f:
                in_dor_section = False
                for line_num, line in enumerate(f, 1):
                    # Detect DoR section
                    if "Intent Classification" in line or "DoR" in line:
                        in_dor_section = True
                    elif line.startswith("##") or line.startswith("---"):
                        in_dor_section = False
                    
                    if not in_dor_section:
                        continue
                    
                    match = field_pattern.search(line)
                    if match:
                        field_name = match.group(1).strip().lower()
                        
                        # Map display name to actual field name
                        actual_field = field_name_mapping.get(field_name)
                        
                        if actual_field:
                            fields.append(FieldSpec(
                                field_name=actual_field,
                                context=f"{prompt_file.name}:{line_num}",
                                line_number=line_num
                            ))
        
        return fields
    
    def check_field_in_dataclass(self, field_name: str) -> Tuple[bool, str]:
        """
        Check if field exists in IntentReflection dataclass.
        
        Args:
            field_name: Field name in snake_case
            
        Returns:
            (exists, location) tuple
        """
        if not self.dor_gate_file.exists():
            return False, "File not found"
        
        with open(self.dor_gate_file) as f:
            content = f.read()
        
        # Pattern: field_name: Type = ...
        field_pattern = re.compile(
            rf'^\s*{re.escape(field_name)}\s*:\s*[A-Za-z\[\]_,\s]+',
            re.MULTILINE
        )
        
        match = field_pattern.search(content)
        if match:
            # Find line number
            lines_before = content[:match.start()].count('\n')
            return True, f"{self.dor_gate_file.name}:{lines_before + 1}"
        
        return False, ""
    
    def check_field_rendered(self, field_name: str) -> Tuple[bool, str]:
        """
        Check if field is rendered in to_markdown() method.
        
        Args:
            field_name: Field name in snake_case
            
        Returns:
            (rendered, location) tuple
        """
        if not self.dor_gate_file.exists():
            return False, "File not found"
        
        with open(self.dor_gate_file) as f:
            content = f.read()
        
        # Pattern: self.field_name or f"...{self.field_name}..."
        render_pattern = re.compile(
            rf'self\.{re.escape(field_name)}',
            re.IGNORECASE
        )
        
        # Find to_markdown method
        method_pattern = re.compile(r'def to_markdown\(self\).*?(?=\n    def |\nclass |\Z)', re.DOTALL)
        method_match = method_pattern.search(content)
        
        if not method_match:
            return False, "to_markdown() not found"
        
        method_content = method_match.group(0)
        
        if render_pattern.search(method_content):
            # Find line number
            lines_before = content[:method_match.start()].count('\n')
            return True, f"{self.dor_gate_file.name}:to_markdown():{lines_before + 1}"
        
        return False, ""
    
    def validate_all_fields(self) -> List[ValidationResult]:
        """
        Validate all DoR fields from prompts.
        
        Returns:
            List of validation results
        """
        field_specs = self.extract_dor_fields_from_prompts()
        
        # Deduplicate by field name
        unique_fields: Set[str] = set()
        for spec in field_specs:
            unique_fields.add(spec.field_name)
        
        results: List[ValidationResult] = []
        
        for field_name in sorted(unique_fields):
            exists, code_loc = self.check_field_in_dataclass(field_name)
            rendered, render_loc = self.check_field_rendered(field_name)
            
            results.append(ValidationResult(
                field_name=field_name,
                exists_in_code=exists,
                rendered_in_output=rendered,
                code_location=code_loc,
                render_location=render_loc
            ))
        
        return results
    
    def print_report(self, results: List[ValidationResult]) -> int:
        """
        Print validation report.
        
        Args:
            results: Validation results
            
        Returns:
            Exit code (0 if all pass, 1 if failures)
        """
        print("=" * 80)
        print("🔍 PROMPT FIELD VERIFICATION (REM-001)")
        print("=" * 80)
        print()
        
        passed = 0
        failed = 0
        
        for result in results:
            field_display = result.field_name.replace("_", " ").title()
            
            if result.exists_in_code and result.rendered_in_output:
                print(f"✅ {field_display}")
                print(f"   Defined: {result.code_location}")
                print(f"   Rendered: {result.render_location}")
                passed += 1
            else:
                print(f"❌ {field_display}")
                if not result.exists_in_code:
                    print(f"   MISSING: Field not found in IntentReflection dataclass")
                if not result.rendered_in_output:
                    print(f"   MISSING: Field not rendered in to_markdown()")
                failed += 1
            print()
        
        print("=" * 80)
        print(f"📊 Results: {passed} passed, {failed} failed")
        print("=" * 80)
        
        return 0 if failed == 0 else 1


def main() -> int:
    """Main entry point."""
    cortex_root = Path.cwd()
    
    # Verify we're in CORTEX root
    if not (cortex_root / "cortex").exists():
        print("❌ Error: Run this script from CORTEX root directory")
        return 2
    
    verifier = PromptFieldVerifier(cortex_root)
    results = verifier.validate_all_fields()
    
    return verifier.print_report(results)


if __name__ == "__main__":
    sys.exit(main())
