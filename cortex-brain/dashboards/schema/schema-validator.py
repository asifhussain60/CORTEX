#!/usr/bin/env python3
"""
Schema Validator for Universal Health Data

Validates health data JSON files against the universal schema.
Can validate single files or entire directories.

Usage:
    python schema-validator.py health-data.json
    python schema-validator.py ../mock/
    python schema-validator.py --all

Author: CORTEX Project
Version: 1.0.0
"""

import json
import sys
from pathlib import Path
from typing import List, Tuple, Optional

try:
    import jsonschema
    from jsonschema import validate, ValidationError, Draft7Validator
except ImportError:
    print("❌ Error: jsonschema package not installed")
    print("Install with: pip install jsonschema")
    sys.exit(1)


class HealthDataValidator:
    """Validator for universal health data schema."""
    
    def __init__(self, schema_path: Path):
        """
        Initialize validator with schema file.
        
        Args:
            schema_path: Path to health-data-schema.json
        """
        self.schema_path = schema_path
        self.schema = self._load_schema()
        self.validator = Draft7Validator(self.schema)
    
    def _load_schema(self) -> dict:
        """Load JSON schema from file."""
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"❌ Schema file not found: {self.schema_path}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON in schema file: {e}")
            sys.exit(1)
    
    def validate_file(self, data_path: Path) -> Tuple[bool, Optional[str]]:
        """
        Validate a single health data JSON file.
        
        Args:
            data_path: Path to health data JSON file
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        try:
            with open(data_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except FileNotFoundError:
            return False, f"File not found: {data_path}"
        except json.JSONDecodeError as e:
            return False, f"Invalid JSON: {e}"
        
        try:
            validate(instance=data, schema=self.schema)
            return True, None
        except ValidationError as e:
            error_path = " -> ".join(str(p) for p in e.absolute_path)
            return False, f"{e.message}\nPath: {error_path if error_path else 'root'}"
    
    def validate_directory(self, dir_path: Path, pattern: str = "*.json") -> List[Tuple[Path, bool, Optional[str]]]:
        """
        Validate all JSON files in a directory.
        
        Args:
            dir_path: Path to directory containing health data files
            pattern: Glob pattern for files (default: *.json)
            
        Returns:
            List of (file_path, is_valid, error_message) tuples
        """
        results = []
        json_files = list(dir_path.glob(pattern))
        
        if not json_files:
            print(f"⚠️  No JSON files found in {dir_path}")
            return results
        
        for file_path in sorted(json_files):
            is_valid, error = self.validate_file(file_path)
            results.append((file_path, is_valid, error))
        
        return results
    
    def print_validation_results(self, results: List[Tuple[Path, bool, Optional[str]]]):
        """Print validation results in formatted output."""
        print("\n" + "="*80)
        print("📋 VALIDATION RESULTS")
        print("="*80 + "\n")
        
        passed = sum(1 for _, is_valid, _ in results if is_valid)
        failed = len(results) - passed
        
        for file_path, is_valid, error in results:
            status = "✅ PASS" if is_valid else "❌ FAIL"
            print(f"{status}  {file_path.name}")
            
            if not is_valid:
                print(f"     Error: {error}")
                print()
        
        print("="*80)
        print(f"Total: {len(results)} files | Passed: {passed} | Failed: {failed}")
        
        if failed == 0:
            print("✅ All files valid!")
        else:
            print(f"❌ {failed} file(s) failed validation")
        
        print("="*80 + "\n")
        
        return failed == 0


def main():
    """Main entry point for validator."""
    # Determine schema and data paths
    script_dir = Path(__file__).parent
    schema_path = script_dir / "health-data-schema.json"
    mock_dir = script_dir.parent / "mock"
    
    # Handle case where script is run from different directory
    if not schema_path.exists():
        # Try relative to current working directory
        schema_path = Path("cortex-brain/dashboards/schema/health-data-schema.json")
        mock_dir = Path("cortex-brain/dashboards/mock")
    
    if not schema_path.exists():
        print(f"❌ Schema file not found: {schema_path}")
        print("Run this script from CORTEX root or schema directory")
        sys.exit(1)
    
    print("🔍 Universal Health Data Schema Validator")
    print(f"Schema: {schema_path}")
    print()
    
    # Initialize validator
    validator = HealthDataValidator(schema_path)
    
    # Determine what to validate
    if len(sys.argv) > 1:
        target = Path(sys.argv[1])
        
        if target == Path("--all"):
            # Validate all mock data
            print(f"Validating all files in: {mock_dir}")
            results = validator.validate_directory(mock_dir)
        elif target.is_file():
            # Validate single file
            print(f"Validating file: {target}")
            is_valid, error = validator.validate_file(target)
            results = [(target, is_valid, error)]
        elif target.is_dir():
            # Validate directory
            print(f"Validating directory: {target}")
            results = validator.validate_directory(target)
        else:
            print(f"❌ Invalid path: {target}")
            sys.exit(1)
    else:
        # Default: validate all mock data
        print(f"Validating all files in: {mock_dir}")
        results = validator.validate_directory(mock_dir)
    
    # Print results
    all_valid = validator.print_validation_results(results)
    
    # Exit with appropriate code
    sys.exit(0 if all_valid else 1)


if __name__ == "__main__":
    main()
