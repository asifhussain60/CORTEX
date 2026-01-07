#!/usr/bin/env python3
"""
CORTEX Toolkit: Template Validator

Validates YAML syntax and structure for response templates and orchestrator manifests.
Part of Orchestrator Composable Template System.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import yaml
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class TemplateValidator:
    """Validates response templates and orchestrator manifests."""
    
    def __init__(self, cortex_root: Path = None):
        """Initialize validator with CORTEX root directory."""
        self.cortex_root = cortex_root or Path(__file__).parent.parent
        self.templates_file = self.cortex_root / "cortex-brain" / "response-templates-v4.yaml"
        self.manifests_dir = self.cortex_root / "cortex-brain" / "manifests" / "orchestrators"
        
    def validate_yaml_syntax(self, file_path: Path) -> Tuple[bool, str]:
        """
        Validate YAML syntax for a file.
        
        Returns:
            (success, error_message)
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                yaml.safe_load(f)
            return True, f"✅ {file_path.name}"
        except yaml.YAMLError as e:
            return False, f"❌ {file_path.name}: {str(e)}"
        except Exception as e:
            return False, f"❌ {file_path.name}: {str(e)}"
    
    def validate_template_structure(self, templates_data: Dict) -> List[str]:
        """
        Validate response-templates-v4.yaml structure.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check for required sections
        required_sections = [
            "template_selection_algorithm",
            "composable_blocks",
            "routing",
            "sections",
            "named_templates"
        ]
        
        for section in required_sections:
            if section not in templates_data:
                errors.append(f"Missing required section: {section}")
        
        # Validate algorithm structure
        if "template_selection_algorithm" in templates_data:
            algo = templates_data["template_selection_algorithm"]
            
            if "context_signals" not in algo:
                errors.append("template_selection_algorithm missing context_signals")
            
            if "block_categories" not in algo:
                errors.append("template_selection_algorithm missing block_categories")
            
            if "composition_rules" not in algo:
                errors.append("template_selection_algorithm missing composition_rules")
            
            if "progress_bar_standard" not in algo:
                errors.append("template_selection_algorithm missing progress_bar_standard")
            
            # Validate progress bar config
            if "progress_bar_standard" in algo:
                pb = algo["progress_bar_standard"]
                if pb.get("width") != 10:
                    errors.append(f"progress_bar_standard width must be 10, got {pb.get('width')}")
                if pb.get("filled_char") != "█":
                    errors.append(f"progress_bar_standard filled_char must be '█'")
                if pb.get("empty_char") != "░":
                    errors.append(f"progress_bar_standard empty_char must be '░'")
        
        # Validate composable_blocks structure
        if "composable_blocks" in templates_data:
            blocks = templates_data["composable_blocks"]
            
            required_block_types = [
                "standard_blocks",
                "planning_blocks",
                "ado_blocks",
                "tdd_blocks",
                "debug_blocks",
                "lens_blocks",
                "refinement_blocks",
                "sanitization_blocks",
                "documentation_blocks"
            ]
            
            for block_type in required_block_types:
                if block_type not in blocks:
                    errors.append(f"composable_blocks missing {block_type}")
        
        return errors
    
    def validate_manifest_structure(self, manifest_data: Dict, manifest_name: str) -> List[str]:
        """
        Validate orchestrator manifest structure.
        
        Returns:
            List of validation errors (empty if valid)
        """
        errors = []
        
        # Check for response_templates section
        if "response_templates" not in manifest_data:
            errors.append(f"{manifest_name}: Missing response_templates section")
            return errors
        
        rt = manifest_data["response_templates"]
        
        # Validate response_templates structure
        if "use_algorithm" not in rt:
            errors.append(f"{manifest_name}: response_templates missing use_algorithm flag")
        
        if rt.get("use_algorithm") and "algorithm_version" not in rt:
            errors.append(f"{manifest_name}: response_templates missing algorithm_version")
        
        if "operations" not in rt:
            errors.append(f"{manifest_name}: response_templates missing operations")
            return errors
        
        # Validate each operation
        for op_name, op_data in rt["operations"].items():
            if "context_signals" not in op_data:
                errors.append(f"{manifest_name}::{op_name}: Missing context_signals")
            
            if "blocks" not in op_data:
                errors.append(f"{manifest_name}::{op_name}: Missing blocks")
            else:
                blocks = op_data["blocks"]
                if "mandatory" not in blocks:
                    errors.append(f"{manifest_name}::{op_name}: Missing mandatory blocks")
        
        return errors
    
    def validate_all(self) -> Dict:
        """
        Run all validations.
        
        Returns:
            Dict with validation results
        """
        results = {
            "templates_yaml_valid": False,
            "templates_structure_valid": False,
            "manifests_yaml_valid": {},
            "manifests_structure_valid": {},
            "templates_errors": [],
            "manifests_errors": {},
            "summary": {}
        }
        
        # Validate templates YAML syntax
        success, msg = self.validate_yaml_syntax(self.templates_file)
        results["templates_yaml_valid"] = success
        if not success:
            results["templates_errors"].append(msg)
            print(msg)
            return results
        else:
            print(msg)
        
        # Validate templates structure
        with open(self.templates_file, 'r', encoding='utf-8') as f:
            templates_data = yaml.safe_load(f)
        
        structure_errors = self.validate_template_structure(templates_data)
        results["templates_structure_valid"] = len(structure_errors) == 0
        results["templates_errors"].extend(structure_errors)
        
        if structure_errors:
            print(f"❌ response-templates-v4.yaml structure errors:")
            for error in structure_errors:
                print(f"   - {error}")
        else:
            print(f"✅ response-templates-v4.yaml structure valid")
        
        # Validate orchestrator manifests
        manifest_files = list(self.manifests_dir.glob("*-manifest.yaml"))
        target_manifests = [
            "planning-system-4.0-manifest.yaml",
            "tdd-orchestrator-v4-manifest.yaml",
            "debug-orchestrator-manifest.yaml",
            "cortex-lens-v3-manifest.yaml",
            "refinement-orchestrator-manifest.yaml",
            "code-sanitization-manifest.yaml",
            "technical-documentation-orchestrator-manifest.yaml",
            "ado-planning-manifest.yaml"
        ]
        
        for manifest_file in manifest_files:
            if manifest_file.name not in target_manifests:
                continue
            
            # YAML syntax validation
            success, msg = self.validate_yaml_syntax(manifest_file)
            results["manifests_yaml_valid"][manifest_file.name] = success
            
            if not success:
                results["manifests_errors"][manifest_file.name] = [msg]
                print(msg)
                continue
            else:
                print(msg)
            
            # Structure validation
            with open(manifest_file, 'r', encoding='utf-8') as f:
                manifest_data = yaml.safe_load(f)
            
            structure_errors = self.validate_manifest_structure(manifest_data, manifest_file.name)
            results["manifests_structure_valid"][manifest_file.name] = len(structure_errors) == 0
            
            if structure_errors:
                results["manifests_errors"][manifest_file.name] = structure_errors
                print(f"❌ {manifest_file.name} structure errors:")
                for error in structure_errors:
                    print(f"   - {error}")
            else:
                print(f"✅ {manifest_file.name} structure valid")
        
        # Generate summary
        total_manifests = len(target_manifests)
        valid_yaml = sum(1 for v in results["manifests_yaml_valid"].values() if v)
        valid_structure = sum(1 for v in results["manifests_structure_valid"].values() if v)
        
        results["summary"] = {
            "templates_valid": results["templates_yaml_valid"] and results["templates_structure_valid"],
            "manifests_yaml_valid": f"{valid_yaml}/{total_manifests}",
            "manifests_structure_valid": f"{valid_structure}/{total_manifests}",
            "all_valid": (
                results["templates_yaml_valid"] and 
                results["templates_structure_valid"] and
                valid_yaml == total_manifests and
                valid_structure == total_manifests
            )
        }
        
        return results
    
    def print_summary(self, results: Dict):
        """Print validation summary."""
        print("\n" + "="*60)
        print("VALIDATION SUMMARY")
        print("="*60)
        
        summary = results["summary"]
        
        print(f"\nTemplates Valid: {'✅ YES' if summary['templates_valid'] else '❌ NO'}")
        print(f"Manifests YAML Valid: {summary['manifests_yaml_valid']}")
        print(f"Manifests Structure Valid: {summary['manifests_structure_valid']}")
        print(f"\nOverall Status: {'✅ ALL VALID' if summary['all_valid'] else '❌ VALIDATION FAILED'}")
        
        if not summary["all_valid"]:
            print("\nErrors found. See output above for details.")
            return 1
        
        return 0


def main():
    """Main entry point."""
    print("CORTEX Template Validator")
    print("="*60)
    
    validator = TemplateValidator()
    results = validator.validate_all()
    exit_code = validator.print_summary(results)
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
