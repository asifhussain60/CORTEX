#!/usr/bin/env python3
"""
Manifest Validation Script
Validates CORTEX 3-Tier Manifest Architecture against JSON schemas

Purpose: Ensure all manifests conform to schema definitions
Author: Asif Hussain
Created: 2025-12-22
Version: 1.0.0
"""

import json
import yaml
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple

try:
    from jsonschema import validate, ValidationError, Draft7Validator
    from jsonschema.exceptions import SchemaError
except ImportError:
    print("❌ jsonschema not installed. Run: pip install jsonschema")
    sys.exit(1)


class ManifestValidator:
    """Validate manifests against JSON schemas"""
    
    def __init__(self, cortex_root: Path):
        self.cortex_root = Path(cortex_root)
        self.manifest_dir = self.cortex_root / "cortex-brain" / "manifests"
        self.schema_dir = self.manifest_dir / "schemas"
        
        self.manifests = {
            "core": "core-manifest.yaml",
            "config": "config-manifest.yaml",
            "integration": "integration-manifest.yaml"
        }
        
        self.schemas = {
            "core": "core-manifest-schema-v2.json",
            "config": "config-manifest-schema-v2.json",
            "integration": "integration-manifest-schema-v2.json"
        }
    
    def load_manifest(self, manifest_type: str) -> Dict[str, Any]:
        """Load YAML manifest"""
        manifest_path = self.manifest_dir / self.manifests[manifest_type]
        
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")
        
        with open(manifest_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def load_schema(self, manifest_type: str) -> Dict[str, Any]:
        """Load JSON schema"""
        schema_path = self.schema_dir / self.schemas[manifest_type]
        
        if not schema_path.exists():
            raise FileNotFoundError(f"Schema not found: {schema_path}")
        
        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def validate_manifest(self, manifest_type: str) -> Tuple[bool, List[str]]:
        """
        Validate manifest against schema.
        
        Returns:
            (success, errors)
        """
        errors = []
        
        try:
            print(f"\n📋 Validating {manifest_type.upper()} Manifest...")
            
            # Load manifest
            manifest = self.load_manifest(manifest_type)
            print(f"   ✅ Loaded manifest: {len(str(manifest))} bytes")
            
            # Load schema
            schema = self.load_schema(manifest_type)
            print(f"   ✅ Loaded schema: {len(str(schema))} bytes")
            
            # Validate
            validator = Draft7Validator(schema)
            validation_errors = list(validator.iter_errors(manifest))
            
            if validation_errors:
                for error in validation_errors:
                    path = ".".join(str(p) for p in error.path)
                    errors.append(f"   ❌ {path or 'root'}: {error.message}")
                return False, errors
            
            print(f"   ✅ Validation passed")
            return True, []
        
        except FileNotFoundError as e:
            errors.append(f"   ❌ File not found: {e}")
            return False, errors
        
        except yaml.YAMLError as e:
            errors.append(f"   ❌ YAML parse error: {e}")
            return False, errors
        
        except json.JSONDecodeError as e:
            errors.append(f"   ❌ JSON parse error: {e}")
            return False, errors
        
        except SchemaError as e:
            errors.append(f"   ❌ Schema error: {e}")
            return False, errors
        
        except Exception as e:
            errors.append(f"   ❌ Unexpected error: {e}")
            return False, errors
    
    def validate_cross_references(self) -> Tuple[bool, List[str]]:
        """Validate cross-references between manifests"""
        errors = []
        
        print("\n🔗 Validating Cross-References...")
        
        try:
            # Load all manifests
            core = self.load_manifest("core")
            config = self.load_manifest("config")
            integration = self.load_manifest("integration")
            
            # Check config references in core
            for orch_id, orch_data in core.get("orchestrators", {}).items():
                if "config_overrides" in orch_data:
                    namespace = orch_data["config_overrides"].get("namespace", "")
                    
                    # Should start with "config://"
                    if not namespace.startswith("config://"):
                        errors.append(f"   ❌ {orch_id}: Invalid config namespace '{namespace}'")
                        continue
                    
                    # Check sections exist in config manifest
                    sections = orch_data["config_overrides"].get("sections", [])
                    for section in sections:
                        category, *subcategory = section.split(".")
                        
                        if category not in config.get("categories", {}):
                            errors.append(f"   ❌ {orch_id}: Config category '{category}' not found")
            
            # Check integration references in core
            for orch_id, orch_data in core.get("orchestrators", {}).items():
                if "integrations" in orch_data:
                    for integration_ref in orch_data["integrations"]:
                        # Should start with "integration://"
                        if not integration_ref.startswith("integration://"):
                            errors.append(f"   ❌ {orch_id}: Invalid integration ref '{integration_ref}'")
                            continue
                        
                        # Extract integration ID
                        integration_id = integration_ref.replace("integration://", "")
                        
                        # Check exists in integration manifest
                        if integration_id not in integration.get("integrations", {}):
                            errors.append(f"   ❌ {orch_id}: Integration '{integration_id}' not found")
            
            if errors:
                return False, errors
            
            print("   ✅ All cross-references valid")
            return True, []
        
        except Exception as e:
            errors.append(f"   ❌ Error validating cross-references: {e}")
            return False, errors
    
    def validate_statistics(self) -> Tuple[bool, List[str]]:
        """Validate manifest statistics"""
        errors = []
        warnings = []
        
        print("\n📊 Validating Statistics...")
        
        try:
            core = self.load_manifest("core")
            config = self.load_manifest("config")
            integration = self.load_manifest("integration")
            
            # Core manifest
            core_meta = core.get("metadata", {})
            total_orchestrators = core_meta.get("total_orchestrators", 0)
            actual_orchestrators = len(core.get("orchestrators", {}))
            
            if total_orchestrators != actual_orchestrators:
                warnings.append(f"   ⚠️  Core: total_orchestrators ({total_orchestrators}) != actual ({actual_orchestrators})")
            
            # Config manifest
            config_meta = config.get("metadata", {})
            total_categories = config_meta.get("total_categories", 0)
            actual_categories = len(config.get("categories", {}))
            
            if total_categories != actual_categories:
                warnings.append(f"   ⚠️  Config: total_categories ({total_categories}) != actual ({actual_categories})")
            
            # Integration manifest
            integration_meta = integration.get("metadata", {})
            total_integrations = integration_meta.get("total_integrations", 0)
            actual_integrations = len(integration.get("integrations", {}))
            
            if total_integrations != actual_integrations:
                warnings.append(f"   ⚠️  Integration: total_integrations ({total_integrations}) != actual ({actual_integrations})")
            
            if warnings:
                for warning in warnings:
                    print(warning)
                return True, warnings  # Warnings don't fail validation
            
            print("   ✅ All statistics accurate")
            return True, []
        
        except Exception as e:
            errors.append(f"   ❌ Error validating statistics: {e}")
            return False, errors
    
    def count_lines(self) -> Dict[str, int]:
        """Count lines in each manifest"""
        line_counts = {}
        
        for manifest_type, filename in self.manifests.items():
            manifest_path = self.manifest_dir / filename
            
            if manifest_path.exists():
                with open(manifest_path, 'r', encoding='utf-8') as f:
                    line_counts[manifest_type] = len(f.readlines())
            else:
                line_counts[manifest_type] = 0
        
        return line_counts
    
    def run_all_validations(self) -> bool:
        """Run all validation checks"""
        print("=" * 80)
        print("CORTEX 3-Tier Manifest Validation")
        print("=" * 80)
        
        all_passed = True
        
        # Validate each manifest
        for manifest_type in ["core", "config", "integration"]:
            success, errors = self.validate_manifest(manifest_type)
            
            if not success:
                all_passed = False
                for error in errors:
                    print(error)
        
        # Validate cross-references
        success, errors = self.validate_cross_references()
        if not success:
            all_passed = False
            for error in errors:
                print(error)
        
        # Validate statistics
        success, warnings = self.validate_statistics()
        if not success:
            all_passed = False
        
        # Count lines
        print("\n📏 Line Counts:")
        line_counts = self.count_lines()
        total_lines = 0
        
        for manifest_type, count in line_counts.items():
            print(f"   {manifest_type.capitalize()}: {count} lines")
            total_lines += count
        
        print(f"   TOTAL: {total_lines} lines")
        
        # Target was 2,500 lines
        target_lines = 2500
        if total_lines <= target_lines:
            print(f"   ✅ Within target ({target_lines} lines)")
        else:
            print(f"   ⚠️  Exceeds target by {total_lines - target_lines} lines")
        
        # Summary
        print("\n" + "=" * 80)
        if all_passed:
            print("✅ ALL VALIDATIONS PASSED")
            print("=" * 80)
            return True
        else:
            print("❌ VALIDATION FAILED")
            print("=" * 80)
            return False


def main():
    """Main entry point"""
    # Determine CORTEX root
    script_dir = Path(__file__).parent
    cortex_root = script_dir.parent
    
    # Allow override via command line
    if len(sys.argv) > 1:
        cortex_root = Path(sys.argv[1])
    
    print(f"CORTEX Root: {cortex_root}\n")
    
    # Validate
    validator = ManifestValidator(cortex_root)
    success = validator.run_all_validations()
    
    # Exit code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
