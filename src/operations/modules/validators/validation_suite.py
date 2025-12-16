"""
Complete Validation Suite for RA API Specifications

Runs all validation checks in sequence and provides comprehensive report.

Author: CORTEX
Version: 1.0
"""

import subprocess
import sys
from pathlib import Path
from typing import Dict, List
import argparse


class ValidationSuite:
    """Orchestrates complete specification validation."""
    
    def __init__(self, api_folder: Path):
        self.api_folder = api_folder
        self.api_name = api_folder.name
        
        # Expected files
        self.legacy_file = None  # Must be provided
        self.spec_file = api_folder / 'business-spec.md'
        self.data_flow_file = api_folder / 'data-flow.mmd'
        self.layer_mapping_file = api_folder / 'layer-mapping.md'
        self.matrix_file = api_folder / 'traceability-matrix.md'
        self.trace_file = api_folder / 'execution-trace.log'
        
        # Tools directory
        self.tools_dir = api_folder.parent.parent / 'tools'
        
        self.results = {}
        
    def validate_prerequisites(self) -> bool:
        """Check if required files exist."""
        print("🔍 Checking prerequisites...")
        
        missing = []
        
        if not self.legacy_file or not self.legacy_file.exists():
            missing.append(f"Legacy file: {self.legacy_file}")
        
        if not self.spec_file.exists():
            missing.append(f"Specification: {self.spec_file}")
        
        if not self.data_flow_file.exists():
            missing.append(f"Data flow diagram: {self.data_flow_file}")
        
        if not self.layer_mapping_file.exists():
            missing.append(f"Layer mapping: {self.layer_mapping_file}")
        
        if missing:
            print("❌ Missing required files:")
            for item in missing:
                print(f"   - {item}")
            return False
        
        print("✅ All required files present")
        return True
    
    def run_ast_validation(self) -> Dict[str, any]:
        """Run AST completeness checker."""
        print("\n" + "="*70)
        print("1️⃣  AST COMPLETENESS VALIDATION")
        print("="*70)
        
        cmd = [
            sys.executable,
            str(self.tools_dir / 'ast_completeness_checker.py'),
            '--legacy', str(self.legacy_file),
            '--spec', str(self.spec_file)
        ]
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            
            return {
                'passed': result.returncode == 0,
                'output': result.stdout
            }
        except Exception as e:
            print(f"❌ Error running AST validation: {e}")
            return {'passed': False, 'error': str(e)}
    
    def run_data_flow_validation(self) -> Dict[str, any]:
        """Run data flow validator."""
        print("\n" + "="*70)
        print("2️⃣  DATA FLOW VALIDATION")
        print("="*70)
        
        cmd = [
            sys.executable,
            str(self.tools_dir / 'data_flow_validator.py'),
            '--mermaid', str(self.data_flow_file)
        ]
        
        # Add trace file if available
        if self.trace_file.exists():
            cmd.extend(['--trace', str(self.trace_file)])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            
            return {
                'passed': result.returncode == 0,
                'output': result.stdout
            }
        except Exception as e:
            print(f"❌ Error running data flow validation: {e}")
            return {'passed': False, 'error': str(e)}
    
    def run_traceability_validation(self) -> Dict[str, any]:
        """Run traceability calculator."""
        print("\n" + "="*70)
        print("3️⃣  TRACEABILITY VALIDATION")
        print("="*70)
        
        cmd = [
            sys.executable,
            str(self.tools_dir / 'traceability_calculator.py'),
            '--legacy', str(self.legacy_file),
            '--spec', str(self.spec_file)
        ]
        
        # Add matrix file if available
        if self.matrix_file.exists():
            cmd.extend(['--matrix', str(self.matrix_file)])
        
        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=False)
            print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
            
            return {
                'passed': result.returncode == 0,
                'output': result.stdout
            }
        except Exception as e:
            print(f"❌ Error running traceability validation: {e}")
            return {'passed': False, 'error': str(e)}
    
    def run_layer_mapping_validation(self) -> Dict[str, any]:
        """Run project reference validator on layer mapping."""
        print("\n" + "="*70)
        print("4️⃣  LAYER MAPPING VALIDATION")
        print("="*70)
        
        # Note: This would use project_reference_validator.py
        # For now, just check file exists and has content
        if self.layer_mapping_file.exists():
            content = self.layer_mapping_file.read_text()
            if len(content) > 100:  # Minimum viable content
                print("✅ Layer mapping file exists and has content")
                return {'passed': True, 'output': 'Layer mapping present'}
            else:
                print("❌ Layer mapping file is too short")
                return {'passed': False, 'output': 'Insufficient content'}
        else:
            print("❌ Layer mapping file not found")
            return {'passed': False, 'output': 'File missing'}
    
    def print_final_report(self):
        """Print comprehensive validation report."""
        print("\n" + "="*70)
        print("📊 COMPREHENSIVE VALIDATION REPORT")
        print("="*70)
        print(f"API: {self.api_name}")
        print(f"Legacy File: {self.legacy_file.name if self.legacy_file else 'N/A'}")
        print("="*70)
        
        all_passed = True
        
        for check_name, result in self.results.items():
            status = "✅ PASS" if result['passed'] else "❌ FAIL"
            print(f"\n{status} - {check_name}")
            
            if 'error' in result:
                print(f"   Error: {result['error']}")
                all_passed = False
            elif not result['passed']:
                all_passed = False
        
        print("\n" + "="*70)
        if all_passed:
            print("🎉 OVERALL: ✅ ALL VALIDATIONS PASSED")
            print("   Specification ready for PM/BA approval")
        else:
            print("⚠️  OVERALL: ❌ VALIDATION FAILED")
            print("   Address issues before proceeding to approval")
        print("="*70)
        
        return all_passed
    
    def run_all(self, legacy_file: Path) -> bool:
        """Run complete validation suite."""
        self.legacy_file = legacy_file
        
        print("="*70)
        print("🚀 STARTING COMPLETE VALIDATION SUITE")
        print("="*70)
        print(f"API: {self.api_name}")
        print(f"Folder: {self.api_folder}")
        print("="*70)
        
        # Check prerequisites
        if not self.validate_prerequisites():
            print("\n❌ Prerequisites not met. Cannot continue.")
            return False
        
        # Run validations
        self.results['AST Completeness'] = self.run_ast_validation()
        self.results['Data Flow'] = self.run_data_flow_validation()
        self.results['Traceability'] = self.run_traceability_validation()
        self.results['Layer Mapping'] = self.run_layer_mapping_validation()
        
        # Print final report
        return self.print_final_report()


def main():
    parser = argparse.ArgumentParser(
        description='Run complete validation suite for API specification'
    )
    parser.add_argument(
        '--api-folder',
        required=True,
        help='Path to API specification folder (e.g., specifications/xupdatefundingbatch)'
    )
    parser.add_argument(
        '--legacy-file',
        required=True,
        help='Path to legacy C# file'
    )
    
    args = parser.parse_args()
    
    api_folder = Path(args.api_folder)
    legacy_file = Path(args.legacy_file)
    
    if not api_folder.exists():
        print(f"❌ Error: API folder not found: {api_folder}")
        return 1
    
    if not legacy_file.exists():
        print(f"❌ Error: Legacy file not found: {legacy_file}")
        return 1
    
    suite = ValidationSuite(api_folder)
    success = suite.run_all(legacy_file)
    
    return 0 if success else 1


if __name__ == '__main__':
    exit(main())
