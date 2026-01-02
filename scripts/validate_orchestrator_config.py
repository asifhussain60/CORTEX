#!/usr/bin/env python3
"""
Orchestrator Configuration Validator

Validates YAML configuration files against JSON schemas and performs cross-validation
to prevent the brittleness patterns discovered during Vacuum v2 migration:

1. Module Path Mismatch - Ensures module files exist
2. Config File Mismatch - Ensures manifest files exist
3. Orchestrator ID Mismatch - Ensures routing rules reference valid registry entries
4. Method Signature Issues - Validates class structure

Usage:
    python scripts/validate_orchestrator_config.py
    python scripts/validate_orchestrator_config.py --fix  # Auto-fix some issues
    python scripts/validate_orchestrator_config.py --verbose
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import yaml

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install jsonschema")
    sys.exit(1)


class ConfigValidator:
    """Validates orchestrator configuration files."""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.base_path = Path(__file__).parent.parent
        
    def log_verbose(self, message: str):
        """Log verbose message."""
        if self.verbose:
            print(f"  [VERBOSE] {message}")
    
    def validate_all(self) -> bool:
        """
        Run all validation checks.
        
        Returns:
            True if all validations pass, False otherwise
        """
        print("🔍 Validating Orchestrator Configuration...")
        print()
        
        # Phase 1: Schema Validation
        print("Phase 1: Schema Validation")
        print("-" * 50)
        registry_valid = self.validate_registry_schema()
        routing_valid = self.validate_routing_schema()
        print()
        
        # Phase 2: File Existence Validation
        print("Phase 2: File Existence Validation")
        print("-" * 50)
        files_valid = self.validate_file_existence()
        print()
        
        # Phase 3: Cross-Validation
        print("Phase 3: Cross-Validation")
        print("-" * 50)
        cross_valid = self.validate_cross_references()
        print()
        
        # Phase 4: Python Import Validation
        print("Phase 4: Python Import Validation")
        print("-" * 50)
        import_valid = self.validate_python_imports()
        print()
        
        # Summary
        print("=" * 50)
        if self.errors:
            print(f"❌ VALIDATION FAILED: {len(self.errors)} errors")
            print()
            for i, error in enumerate(self.errors, 1):
                print(f"{i}. {error}")
            print()
        else:
            print("✅ ALL VALIDATIONS PASSED")
            print()
        
        if self.warnings:
            print(f"⚠️  {len(self.warnings)} warnings:")
            for i, warning in enumerate(self.warnings, 1):
                print(f"{i}. {warning}")
            print()
        
        return len(self.errors) == 0
    
    def validate_registry_schema(self) -> bool:
        """Validate mcp-server.yaml against schema."""
        schema_path = self.base_path / "cortex-brain/config/schemas/orchestrator-registry-schema.json"
        config_path = self.base_path / "cortex-brain/config/mcp-server.yaml"
        
        if not schema_path.exists():
            self.errors.append(f"Schema not found: {schema_path}")
            return False
        
        if not config_path.exists():
            self.errors.append(f"Config not found: {config_path}")
            return False
        
        try:
            schema = json.loads(schema_path.read_text())
            config = yaml.safe_load(config_path.read_text())
            
            jsonschema.validate(instance=config, schema=schema)
            print(f"  ✅ Registry schema validation passed ({config_path.name})")
            self.log_verbose(f"Validated {len(config.get('orchestrators', {}))} orchestrators")
            return True
            
        except jsonschema.ValidationError as e:
            self.errors.append(f"Registry schema validation failed: {e.message} at {'.'.join(str(p) for p in e.path)}")
            return False
        except Exception as e:
            self.errors.append(f"Registry validation error: {e}")
            return False
    
    def validate_routing_schema(self) -> bool:
        """Validate master-orchestrator.yaml against schema."""
        schema_path = self.base_path / "cortex-brain/config/schemas/routing-config-schema.json"
        config_path = self.base_path / "cortex-brain/config/master-orchestrator.yaml"
        
        if not schema_path.exists():
            self.errors.append(f"Schema not found: {schema_path}")
            return False
        
        if not config_path.exists():
            self.errors.append(f"Config not found: {config_path}")
            return False
        
        try:
            schema = json.loads(schema_path.read_text())
            config = yaml.safe_load(config_path.read_text())
            
            jsonschema.validate(instance=config, schema=schema)
            print(f"  ✅ Routing schema validation passed ({config_path.name})")
            self.log_verbose(f"Validated {len(config.get('routing_rules', []))} routing rules")
            return True
            
        except jsonschema.ValidationError as e:
            self.errors.append(f"Routing schema validation failed: {e.message} at {'.'.join(str(p) for p in e.path)}")
            return False
        except Exception as e:
            self.errors.append(f"Routing validation error: {e}")
            return False
    
    def validate_file_existence(self) -> bool:
        """Validate that all referenced files exist."""
        registry_path = self.base_path / "cortex-brain/config/mcp-server.yaml"
        
        if not registry_path.exists():
            return False
        
        registry_config = yaml.safe_load(registry_path.read_text())
        orchestrators = registry_config.get('orchestrators', {})
        
        all_valid = True
        
        for orch_id, definition in orchestrators.items():
            self.log_verbose(f"Checking orchestrator '{orch_id}'...")
            
            # Check module file
            module_path = definition['module'].replace('.', '/') + '.py'
            module_file = self.base_path / module_path
            
            if not module_file.exists():
                self.errors.append(
                    f"Orchestrator '{orch_id}': Module file not found: {module_path}"
                )
                all_valid = False
            else:
                self.log_verbose(f"  ✓ Module file exists: {module_path}")
            
            # Check config file
            config_file = self.base_path / definition['config']
            
            if not config_file.exists():
                self.errors.append(
                    f"Orchestrator '{orch_id}': Config file not found: {definition['config']}"
                )
                all_valid = False
            else:
                self.log_verbose(f"  ✓ Config file exists: {definition['config']}")
        
        if all_valid:
            print(f"  ✅ All {len(orchestrators)} orchestrator files exist")
        
        return all_valid
    
    def validate_cross_references(self) -> bool:
        """Validate routing rules reference valid registry entries."""
        routing_path = self.base_path / "cortex-brain/config/master-orchestrator.yaml"
        registry_path = self.base_path / "cortex-brain/config/mcp-server.yaml"
        
        if not routing_path.exists() or not registry_path.exists():
            return False
        
        routing_config = yaml.safe_load(routing_path.read_text())
        registry_config = yaml.safe_load(registry_path.read_text())
        
        routing_rules = routing_config.get('routing_rules', [])
        orchestrators = registry_config.get('orchestrators', {})
        
        all_valid = True
        
        for i, rule in enumerate(routing_rules):
            orch_id = rule['orchestrator']
            pattern = rule['pattern']
            
            self.log_verbose(f"Checking routing rule {i+1}: {pattern} → {orch_id}")
            
            if orch_id not in orchestrators:
                self.errors.append(
                    f"Routing rule {i+1} (pattern: '{pattern}'): "
                    f"Orchestrator '{orch_id}' not found in registry"
                )
                all_valid = False
            else:
                self.log_verbose(f"  ✓ Orchestrator '{orch_id}' exists in registry")
        
        # Check for unused orchestrators (warning only)
        routing_orch_ids = {rule['orchestrator'] for rule in routing_rules}
        unused = set(orchestrators.keys()) - routing_orch_ids
        
        if unused:
            self.warnings.append(
                f"Orchestrators in registry but not in routing rules: {', '.join(sorted(unused))}"
            )
        
        if all_valid:
            print(f"  ✅ All {len(routing_rules)} routing rules reference valid orchestrators")
        
        return all_valid
    
    def validate_python_imports(self) -> bool:
        """Validate that Python classes can be imported."""
        registry_path = self.base_path / "cortex-brain/config/mcp-server.yaml"
        
        if not registry_path.exists():
            return False
        
        registry_config = yaml.safe_load(registry_path.read_text())
        orchestrators = registry_config.get('orchestrators', {})
        
        all_valid = True
        
        for orch_id, definition in orchestrators.items():
            module_path = definition['module']
            class_name = definition['class']
            
            self.log_verbose(f"Checking import: {module_path}.{class_name}")
            
            # Check if class exists in module file
            py_file = self.base_path / (module_path.replace('.', '/') + '.py')
            
            if py_file.exists():
                content = py_file.read_text()
                
                # Check for class definition
                class_pattern = rf'class\s+{re.escape(class_name)}\s*\('
                if not re.search(class_pattern, content):
                    self.errors.append(
                        f"Orchestrator '{orch_id}': Class '{class_name}' not found in {module_path}"
                    )
                    all_valid = False
                else:
                    self.log_verbose(f"  ✓ Class '{class_name}' found in module")
                
                # Check for execute method (required for orchestrators)
                execute_pattern = r'def\s+execute\s*\('
                if not re.search(execute_pattern, content):
                    self.warnings.append(
                        f"Orchestrator '{orch_id}': No 'execute()' method found in class '{class_name}'"
                    )
        
        if all_valid:
            print(f"  ✅ All {len(orchestrators)} orchestrator classes found")
        
        return all_valid


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate orchestrator configuration files"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix issues where possible (not yet implemented)"
    )
    
    args = parser.parse_args()
    
    validator = ConfigValidator(verbose=args.verbose)
    
    if args.fix:
        print("⚠️  Auto-fix not yet implemented")
        print()
    
    success = validator.validate_all()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
