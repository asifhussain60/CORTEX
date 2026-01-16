#!/usr/bin/env python3
"""
Phase Deliverables Validation Script

AC-DOC-004-01: Validates that phase deliverables actually exist.

This script addresses GAP-6 from ROADMAP-GAP-ANALYSIS.md:
"files_to_create in phase YAML MUST exist before phase lock"

Usage:
    python scripts/validate_phase_deliverables.py --phase DOC-REMEDIATION
    python scripts/validate_phase_deliverables.py --all
    python scripts/validate_phase_deliverables.py --phase DOC-REMEDIATION --strict
"""

import argparse
import sys
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    check_name: str
    passed: bool
    message: str
    severity: str = "ERROR"  # ERROR, WARNING, INFO


class PhaseDeliverableValidator:
    """
    Validates that phase deliverables (files_to_create) actually exist.
    
    Addresses systematic gap where phases are marked complete
    but specified files were never created.
    """
    
    def __init__(self, project_root: Path = None):
        """Initialize validator with project root."""
        self.project_root = project_root or Path(__file__).parent.parent
        self.results: List[ValidationResult] = []
        
    def validate_phase(self, phase_id: str) -> Tuple[bool, List[ValidationResult]]:
        """
        Validate all deliverables for a specific phase.
        
        Args:
            phase_id: Phase identifier (e.g., "DOC-REMEDIATION")
            
        Returns:
            Tuple of (all_passed, results)
        """
        self.results = []
        
        # Load phase YAML
        phase_yaml = self._load_phase_yaml(phase_id)
        if not phase_yaml:
            return False, self.results
            
        # Validate files_to_create
        self._validate_files_to_create(phase_yaml)
        
        # Validate files_to_modify exist (so they CAN be modified)
        self._validate_files_to_modify(phase_yaml)
        
        # Validate prompt sections (for DOC-REMEDIATION specifically)
        if phase_id == "DOC-REMEDIATION":
            self._validate_prompt_sections()
            self._validate_tier2_templates()
        
        # Check if all passed
        all_passed = all(r.passed for r in self.results if r.severity == "ERROR")
        
        return all_passed, self.results
    
    def _load_phase_yaml(self, phase_id: str) -> Dict[str, Any]:
        """Load phase YAML file."""
        # Try different naming patterns
        patterns = [
            f"phase-{phase_id.lower()}.yaml",
            f"phase-{phase_id.lower().replace('_', '-')}.yaml",
        ]
        
        phases_dir = self.project_root / ".github" / "roadmap" / "phases"
        
        for pattern in patterns:
            yaml_path = phases_dir / pattern
            if yaml_path.exists():
                try:
                    with open(yaml_path, 'r') as f:
                        return yaml.safe_load(f)
                except Exception as e:
                    self.results.append(ValidationResult(
                        check_name="Load Phase YAML",
                        passed=False,
                        message=f"Failed to load {yaml_path}: {e}"
                    ))
                    return None
        
        self.results.append(ValidationResult(
            check_name="Load Phase YAML",
            passed=False,
            message=f"Phase YAML not found for {phase_id}. Tried: {patterns}"
        ))
        return None
    
    def _validate_files_to_create(self, phase_yaml: Dict[str, Any]) -> None:
        """Validate all files_to_create actually exist."""
        acs = phase_yaml.get("acceptance_criteria", {})
        
        for ac_id, ac_data in acs.items():
            files_to_create = ac_data.get("files_to_create", [])
            
            for file_spec in files_to_create:
                # Handle both string paths and dict specs
                if isinstance(file_spec, dict):
                    file_path = file_spec.get("path", "")
                else:
                    file_path = file_spec
                
                if not file_path:
                    continue
                    
                full_path = self.project_root / file_path
                exists = full_path.exists()
                
                self.results.append(ValidationResult(
                    check_name=f"File Exists: {file_path}",
                    passed=exists,
                    message=f"{'✅ EXISTS' if exists else '❌ MISSING'}: {file_path}",
                    severity="ERROR"
                ))
    
    def _validate_files_to_modify(self, phase_yaml: Dict[str, Any]) -> None:
        """Validate files_to_modify exist (prerequisite for modification)."""
        acs = phase_yaml.get("acceptance_criteria", {})
        
        for ac_id, ac_data in acs.items():
            files_to_modify = ac_data.get("files_to_modify", [])
            
            for file_spec in files_to_modify:
                # Handle both string paths and dict specs
                if isinstance(file_spec, dict):
                    file_path = file_spec.get("path", "")
                else:
                    file_path = file_spec
                
                if not file_path:
                    continue
                    
                full_path = self.project_root / file_path
                exists = full_path.exists()
                
                self.results.append(ValidationResult(
                    check_name=f"File Can Be Modified: {file_path}",
                    passed=exists,
                    message=f"{'✅ EXISTS' if exists else '❌ MISSING (cannot modify)'}: {file_path}",
                    severity="ERROR"
                ))
    
    def _validate_prompt_sections(self) -> None:
        """Validate that prompts contain required sections."""
        # Check CORTEX.prompt.md
        cortex_prompt = self.project_root / ".github" / "prompts" / "CORTEX.prompt.md"
        if cortex_prompt.exists():
            content = cortex_prompt.read_text()
            
            # Check for Response Header section
            has_response_header = "Response Header" in content
            self.results.append(ValidationResult(
                check_name="CORTEX.prompt.md: Response Header Section",
                passed=has_response_header,
                message=f"{'✅ FOUND' if has_response_header else '❌ MISSING'}: Response Header Integration section",
                severity="ERROR"
            ))
            
            # Check for response-headers.yaml reference
            has_headers_ref = "response-headers.yaml" in content
            self.results.append(ValidationResult(
                check_name="CORTEX.prompt.md: response-headers.yaml Reference",
                passed=has_headers_ref,
                message=f"{'✅ FOUND' if has_headers_ref else '❌ MISSING'}: reference to response-headers.yaml",
                severity="ERROR"
            ))
        else:
            self.results.append(ValidationResult(
                check_name="CORTEX.prompt.md Exists",
                passed=False,
                message="❌ CORTEX.prompt.md not found",
                severity="ERROR"
            ))
        
        # Check copilot-instruction.md
        copilot_instruction = self.project_root / ".github" / "copilot-instruction.md"
        if copilot_instruction.exists():
            content = copilot_instruction.read_text()
            
            # Check for Response Format section
            has_response_format = "Response Format" in content
            self.results.append(ValidationResult(
                check_name="copilot-instruction.md: Response Format Section",
                passed=has_response_format,
                message=f"{'✅ FOUND' if has_response_format else '❌ MISSING'}: Response Format Standards section",
                severity="ERROR"
            ))
            
            # Check for copyright template
            has_copyright = "Copyright" in content and "Asif Hussain" in content
            self.results.append(ValidationResult(
                check_name="copilot-instruction.md: Copyright Template",
                passed=has_copyright,
                message=f"{'✅ FOUND' if has_copyright else '❌ MISSING'}: Copyright template",
                severity="ERROR"
            ))
        else:
            self.results.append(ValidationResult(
                check_name="copilot-instruction.md Exists",
                passed=False,
                message="❌ copilot-instruction.md not found",
                severity="ERROR"
            ))
    
    def _validate_tier2_templates(self) -> None:
        """Validate Tier 2 response templates exist and are not empty."""
        tier2_base = self.project_root / "cortex-brain" / "tier2"
        
        # Check base templates
        base_dir = tier2_base / "base"
        base_yamls = list(base_dir.glob("*.yaml")) if base_dir.exists() else []
        has_base = len(base_yamls) >= 3
        
        self.results.append(ValidationResult(
            check_name="Tier 2 Base Templates",
            passed=has_base,
            message=f"{'✅' if has_base else '❌'} Found {len(base_yamls)}/3 required base templates",
            severity="ERROR"
        ))
        
        # Check domain templates
        domains_dir = tier2_base / "domains"
        if domains_dir.exists():
            domain_yamls = list(domains_dir.rglob("*.yaml"))
            has_domains = len(domain_yamls) >= 6
            
            self.results.append(ValidationResult(
                check_name="Tier 2 Domain Templates",
                passed=has_domains,
                message=f"{'✅' if has_domains else '❌'} Found {len(domain_yamls)}/6 required domain templates",
                severity="ERROR"
            ))
        else:
            self.results.append(ValidationResult(
                check_name="Tier 2 Domain Templates Directory",
                passed=False,
                message="❌ cortex-brain/tier2/domains/ directory not found",
                severity="ERROR"
            ))
        
        # Check index file
        index_file = tier2_base / "response-templates-index.yaml"
        has_index = index_file.exists()
        
        self.results.append(ValidationResult(
            check_name="Tier 2 Templates Index",
            passed=has_index,
            message=f"{'✅ EXISTS' if has_index else '❌ MISSING'}: response-templates-index.yaml",
            severity="ERROR"
        ))
        
        # Check response-templates directory is not just .gitkeep
        templates_dir = tier2_base / "response-templates"
        if templates_dir.exists():
            files = [f for f in templates_dir.iterdir() if f.name != ".gitkeep"]
            not_empty = len(files) > 0
            
            self.results.append(ValidationResult(
                check_name="Tier 2 response-templates Directory",
                passed=not_empty,
                message=f"{'✅' if not_empty else '❌'} Directory has {len(files)} files (excluding .gitkeep)",
                severity="WARNING" if not_empty else "ERROR"
            ))


def print_results(results: List[ValidationResult], verbose: bool = False) -> None:
    """Print validation results."""
    print("\n" + "=" * 70)
    print("PHASE DELIVERABLES VALIDATION REPORT")
    print("=" * 70 + "\n")
    
    errors = [r for r in results if not r.passed and r.severity == "ERROR"]
    warnings = [r for r in results if not r.passed and r.severity == "WARNING"]
    passed = [r for r in results if r.passed]
    
    # Summary
    print(f"📊 SUMMARY: {len(passed)} passed, {len(errors)} errors, {len(warnings)} warnings\n")
    
    # Errors
    if errors:
        print("❌ ERRORS (must fix before phase lock):")
        for r in errors:
            print(f"   • {r.message}")
        print()
    
    # Warnings
    if warnings:
        print("⚠️  WARNINGS:")
        for r in warnings:
            print(f"   • {r.message}")
        print()
    
    # Passed (verbose only)
    if verbose and passed:
        print("✅ PASSED:")
        for r in passed:
            print(f"   • {r.message}")
        print()
    
    # Final status
    if errors:
        print("❌ VALIDATION FAILED - Fix errors before phase lock")
    elif warnings:
        print("⚠️  VALIDATION PASSED WITH WARNINGS")
    else:
        print("✅ VALIDATION PASSED - All deliverables verified")
    
    print("=" * 70 + "\n")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate phase deliverables exist"
    )
    parser.add_argument(
        "--phase",
        type=str,
        required=True,
        help="Phase ID to validate (e.g., DOC-REMEDIATION)"
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on warnings as well as errors"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show all checks including passed ones"
    )
    
    args = parser.parse_args()
    
    validator = PhaseDeliverableValidator()
    all_passed, results = validator.validate_phase(args.phase)
    
    print_results(results, args.verbose)
    
    # Determine exit code
    if not all_passed:
        sys.exit(1)
    elif args.strict:
        warnings = [r for r in results if not r.passed and r.severity == "WARNING"]
        if warnings:
            sys.exit(1)
    
    sys.exit(0)


if __name__ == "__main__":
    main()
