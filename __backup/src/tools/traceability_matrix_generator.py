#!/usr/bin/env python3
"""
Traceability Matrix Generator

Creates a comprehensive matrix linking:
- Requirements (requirements.yaml) → Implementation (source files) → Tests (test files)

This enables:
- Coverage analysis (which requirements lack tests)
- Impact analysis (which tests break when implementation changes)
- Compliance verification (audit trail from requirement to validation)

Created: 2026-01-08 | Phase P1-T11
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Set
import re
from datetime import datetime


class TraceabilityMatrixGenerator:
    """Generate traceability matrix from requirements, code, and tests."""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.features_path = workspace_root / '.asif/AI-Learning/cortex6/source-of-truth/features'
        self.src_path = workspace_root / 'src'
        self.tests_path = workspace_root / 'tests'
        
        self.traceability_data = []
        self.coverage_stats = {
            'total_requirements': 0,
            'with_implementation': 0,
            'with_tests': 0,
            'fully_traced': 0
        }
    
    def load_all_requirements(self) -> List[Dict]:
        """Load all requirements from all features."""
        all_requirements = []
        
        print("📖 Loading requirements from all features...")
        
        for feature_dir in sorted(self.features_path.glob('feat*')):
            if not feature_dir.is_dir():
                continue
            
            req_file = feature_dir / 'requirements.yaml'
            if not req_file.exists():
                continue
            
            try:
                with open(req_file, 'r') as f:
                    data = yaml.safe_load(f)
                
                feature_id = data.get('feature_id', '')
                feature_name = data.get('feature_name', '')
                requirements = data.get('requirements', [])
                
                for req in requirements:
                    req['feature_id'] = feature_id
                    req['feature_name'] = feature_name
                    all_requirements.append(req)
                
                print(f"  ✅ {feature_id}: {len(requirements)} requirements")
                
            except Exception as e:
                print(f"  ⚠️  {feature_dir.name}: {e}")
        
        print(f"\n📊 Total requirements loaded: {len(all_requirements)}")
        return all_requirements
    
    def find_implementation_files(self, requirement: Dict) -> List[str]:
        """
        Find source files that implement a requirement.
        
        Strategy:
        1. Check requirement['implementation']['files'] if exists
        2. Search for feature_id in file comments
        3. Search for requirement_id in file comments
        """
        impl_files = []
        
        # Strategy 1: Explicit implementation mapping
        if 'implementation' in requirement and 'files' in requirement['implementation']:
            explicit_files = requirement['implementation']['files']
            for file_path in explicit_files:
                full_path = self.workspace_root / file_path
                if full_path.exists():
                    impl_files.append(str(file_path))
        
        # Strategy 2: Search for feature_id and requirement_id in source code
        feature_id = requirement.get('feature_id', '')
        req_id = requirement.get('requirement_id', '')
        
        if not impl_files and feature_id:
            # Search src/ directory for references
            for src_file in self.src_path.rglob('*.py'):
                try:
                    content = src_file.read_text()
                    
                    # Look for feature_id or req_id in comments
                    if f"{feature_id}" in content or f"{req_id}" in content:
                        rel_path = src_file.relative_to(self.workspace_root)
                        if str(rel_path) not in impl_files:
                            impl_files.append(str(rel_path))
                            
                except Exception:
                    pass
        
        return impl_files
    
    def find_test_files(self, requirement: Dict, impl_files: List[str]) -> List[str]:
        """
        Find test files that validate a requirement.
        
        Strategy:
        1. Check requirement['implementation']['tests'] if exists
        2. For each impl file, find corresponding test file
        3. Search for requirement_id in test files
        """
        test_files = []
        
        # Strategy 1: Explicit test mapping
        if 'implementation' in requirement and 'tests' in requirement['implementation']:
            explicit_tests = requirement['implementation']['tests']
            for test_path in explicit_tests:
                full_path = self.workspace_root / test_path
                if full_path.exists():
                    test_files.append(str(test_path))
        
        # Strategy 2: Find tests for implementation files
        for impl_file in impl_files:
            impl_path = Path(impl_file)
            
            # Convert src/ path to tests/ path
            # src/orchestrators/state_manager.py → tests/unit/test_state_manager.py
            if impl_path.parts[0] == 'src':
                test_name = f"test_{impl_path.stem}.py"
                
                # Check both unit and integration
                unit_test = self.tests_path / 'unit' / test_name
                integration_test = self.tests_path / 'integration' / test_name
                
                if unit_test.exists():
                    test_files.append(str(unit_test.relative_to(self.workspace_root)))
                if integration_test.exists():
                    test_files.append(str(integration_test.relative_to(self.workspace_root)))
        
        # Strategy 3: Search for requirement_id in test files
        req_id = requirement.get('requirement_id', '')
        feature_id = requirement.get('feature_id', '')
        
        if req_id or feature_id:
            for test_file in self.tests_path.rglob('test_*.py'):
                try:
                    content = test_file.read_text()
                    
                    if f"{req_id}" in content or f"{feature_id}" in content:
                        rel_path = test_file.relative_to(self.workspace_root)
                        if str(rel_path) not in test_files:
                            test_files.append(str(rel_path))
                            
                except Exception:
                    pass
        
        return list(set(test_files))  # Remove duplicates
    
    def generate_trace_entry(self, requirement: Dict) -> Dict:
        """Generate traceability entry for a requirement."""
        req_id = requirement.get('requirement_id', '')
        feature_id = requirement.get('feature_id', '')
        
        # Find implementation and tests
        impl_files = self.find_implementation_files(requirement)
        test_files = self.find_test_files(requirement, impl_files)
        
        # Determine coverage status
        has_impl = len(impl_files) > 0
        has_tests = len(test_files) > 0
        status = requirement.get('status', 'NOT_STARTED')
        
        trace_entry = {
            'requirement_id': req_id,
            'feature_id': feature_id,
            'feature_name': requirement.get('feature_name', ''),
            'description': requirement.get('description', ''),
            'priority': requirement.get('priority', ''),
            'status': status,
            'implementation': {
                'files': impl_files,
                'count': len(impl_files),
                'exists': has_impl
            },
            'tests': {
                'files': test_files,
                'count': len(test_files),
                'exists': has_tests
            },
            'coverage': {
                'has_implementation': has_impl,
                'has_tests': has_tests,
                'fully_traced': has_impl and has_tests,
                'coverage_level': self._calculate_coverage_level(has_impl, has_tests, status)
            }
        }
        
        return trace_entry
    
    def _calculate_coverage_level(self, has_impl: bool, has_tests: bool, status: str) -> str:
        """Calculate coverage level for a requirement."""
        if status in ['NOT_STARTED', 'BLOCKED']:
            return 'NOT_APPLICABLE'
        
        if has_impl and has_tests:
            return 'FULL'
        elif has_impl and not has_tests:
            return 'PARTIAL_NO_TESTS'
        elif not has_impl and has_tests:
            return 'PARTIAL_NO_IMPL'
        else:
            return 'NONE'
    
    def generate_matrix(self) -> Dict[str, Any]:
        """Generate complete traceability matrix."""
        print("\n🛡️🧠 CORTEX Traceability Matrix Generation")
        print("=" * 70)
        print()
        
        # Load all requirements
        requirements = self.load_all_requirements()
        self.coverage_stats['total_requirements'] = len(requirements)
        
        print("\n🔍 Analyzing traceability...")
        print()
        
        # Generate trace entries
        for req in requirements:
            trace_entry = self.generate_trace_entry(req)
            self.traceability_data.append(trace_entry)
            
            # Update stats
            if trace_entry['coverage']['has_implementation']:
                self.coverage_stats['with_implementation'] += 1
            if trace_entry['coverage']['has_tests']:
                self.coverage_stats['with_tests'] += 1
            if trace_entry['coverage']['fully_traced']:
                self.coverage_stats['fully_traced'] += 1
            
            # Progress indicator
            status_icon = "✅" if trace_entry['coverage']['fully_traced'] else "⚠️" if trace_entry['coverage']['has_implementation'] else "❌"
            print(f"{status_icon} {trace_entry['requirement_id']}: {trace_entry['implementation']['count']} impl, {trace_entry['tests']['count']} tests")
        
        # Calculate percentages
        total = self.coverage_stats['total_requirements']
        pct_impl = (self.coverage_stats['with_implementation'] / total * 100) if total > 0 else 0
        pct_tests = (self.coverage_stats['with_tests'] / total * 100) if total > 0 else 0
        pct_full = (self.coverage_stats['fully_traced'] / total * 100) if total > 0 else 0
        
        matrix = {
            'metadata': {
                'generated_at': datetime.now().isoformat(),
                'workspace_root': str(self.workspace_root),
                'total_requirements': total
            },
            'coverage_summary': {
                'total_requirements': total,
                'with_implementation': self.coverage_stats['with_implementation'],
                'with_tests': self.coverage_stats['with_tests'],
                'fully_traced': self.coverage_stats['fully_traced'],
                'percentages': {
                    'implementation_coverage': f"{pct_impl:.1f}%",
                    'test_coverage': f"{pct_tests:.1f}%",
                    'full_traceability': f"{pct_full:.1f}%"
                }
            },
            'traceability': self.traceability_data
        }
        
        print()
        print("=" * 70)
        print("📊 TRACEABILITY SUMMARY")
        print("=" * 70)
        print(f"Total Requirements:       {total}")
        print(f"With Implementation:      {self.coverage_stats['with_implementation']} ({pct_impl:.1f}%)")
        print(f"With Tests:               {self.coverage_stats['with_tests']} ({pct_tests:.1f}%)")
        print(f"Fully Traced:             {self.coverage_stats['fully_traced']} ({pct_full:.1f}%)")
        print("=" * 70)
        print()
        
        return matrix
    
    def export_yaml(self, output_path: Path):
        """Export traceability matrix as YAML."""
        matrix = self.generate_matrix()
        
        with open(output_path, 'w') as f:
            yaml.dump(matrix, f, default_flow_style=False, sort_keys=False)
        
        print(f"📄 YAML report saved to: {output_path}")
    
    def export_json(self, output_path: Path):
        """Export traceability matrix as JSON."""
        matrix = self.generate_matrix()
        
        with open(output_path, 'w') as f:
            json.dump(matrix, f, indent=2)
        
        print(f"📄 JSON report saved to: {output_path}")
    
    def export_markdown(self, output_path: Path):
        """Export traceability matrix as Markdown report."""
        matrix = self.generate_matrix()
        
        md_lines = [
            "# 🔗 CORTEX Traceability Matrix",
            "",
            f"**Generated:** {matrix['metadata']['generated_at']}",
            f"**Total Requirements:** {matrix['coverage_summary']['total_requirements']}",
            "",
            "---",
            "",
            "## 📊 Coverage Summary",
            "",
            f"- **Implementation Coverage:** {matrix['coverage_summary']['percentages']['implementation_coverage']}",
            f"- **Test Coverage:** {matrix['coverage_summary']['percentages']['test_coverage']}",
            f"- **Full Traceability:** {matrix['coverage_summary']['percentages']['full_traceability']}",
            "",
            "---",
            "",
            "## 📋 Detailed Traceability",
            "",
            "| Req ID | Feature | Description | Impl Files | Test Files | Coverage |",
            "|--------|---------|-------------|------------|------------|----------|"
        ]
        
        for trace in matrix['traceability']:
            req_id = trace['requirement_id']
            feature = trace['feature_id']
            desc = trace['description'][:50] + "..." if len(trace['description']) > 50 else trace['description']
            impl_count = trace['implementation']['count']
            test_count = trace['tests']['count']
            coverage = "✅ Full" if trace['coverage']['fully_traced'] else "⚠️ Partial" if trace['coverage']['has_implementation'] else "❌ None"
            
            md_lines.append(f"| {req_id} | {feature} | {desc} | {impl_count} | {test_count} | {coverage} |")
        
        md_lines.extend([
            "",
            "---",
            "",
            "**Legend:**",
            "- ✅ Full: Has both implementation and tests",
            "- ⚠️ Partial: Has implementation but missing tests",
            "- ❌ None: No implementation found",
            ""
        ])
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(md_lines))
        
        print(f"📄 Markdown report saved to: {output_path}")


def main():
    """CLI entry point."""
    workspace_root = Path.cwd()
    generator = TraceabilityMatrixGenerator(workspace_root)
    
    # Generate all formats
    reports_dir = workspace_root / '.asif/AI-Learning/cortex6-fixes/reports'
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    yaml_output = reports_dir / 'traceability-matrix.yaml'
    json_output = reports_dir / 'traceability-matrix.json'
    md_output = reports_dir / 'traceability-matrix.md'
    
    # Generate matrix once, export to all formats
    matrix = generator.generate_matrix()
    
    # Export YAML
    with open(yaml_output, 'w') as f:
        yaml.dump(matrix, f, default_flow_style=False, sort_keys=False)
    print(f"📄 YAML saved to: {yaml_output}")
    
    # Export JSON
    with open(json_output, 'w') as f:
        json.dump(matrix, f, indent=2)
    print(f"📄 JSON saved to: {json_output}")
    
    # Export Markdown
    generator.export_markdown(md_output)


if __name__ == '__main__':
    main()
