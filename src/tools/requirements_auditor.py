#!/usr/bin/env python3
"""
Requirements Audit Script (P1-T1)

Scans CORTEX 6.0 requirements and generates comprehensive audit report.

Part of: CORTEX 6.0 Remediation Plan - Phase P1
Author: GitHub Copilot + Asif Hussain
Created: 2026-01-08
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict
from datetime import datetime


class RequirementsAuditor:
    """Audits CORTEX 6.0 requirements documentation."""
    
    def __init__(self, cortex6_root: Path):
        """Initialize auditor."""
        self.cortex6_root = Path(cortex6_root)
        self.source_of_truth = self.cortex6_root / "source-of-truth" / "features"
        self.results = {
            'files_by_type': defaultdict(list),
            'files_by_feature': defaultdict(list),
            'conversion_needed': [],
            'already_yaml': [],
            'total_files': 0,
            'audit_timestamp': datetime.now().isoformat()
        }
    
    def scan_requirements(self) -> None:
        """Scan all requirements files."""
        # Scan MD files
        for md_file in self.cortex6_root.rglob("*.md"):
            self.results['files_by_type']['markdown'].append(str(md_file.relative_to(self.cortex6_root)))
            
            # Categorize by feature
            feature_id = self._extract_feature_id(md_file)
            if feature_id:
                self.results['files_by_feature'][feature_id].append(str(md_file.relative_to(self.cortex6_root)))
            
            self.results['total_files'] += 1
        
        # Scan YAML files
        for yaml_file in self.cortex6_root.rglob("*.yaml"):
            self.results['files_by_type']['yaml'].append(str(yaml_file.relative_to(self.cortex6_root)))
            
            feature_id = self._extract_feature_id(yaml_file)
            if feature_id:
                self.results['files_by_feature'][feature_id].append(str(yaml_file.relative_to(self.cortex6_root)))
                
                # Check if it's a feature.yaml
                if yaml_file.name in ['feature.yaml', 'requirements.yaml']:
                    self.results['already_yaml'].append({
                        'file': str(yaml_file.relative_to(self.cortex6_root)),
                        'feature': feature_id,
                        'type': yaml_file.name
                    })
            
            self.results['total_files'] += 1
    
    def _extract_feature_id(self, file_path: Path) -> str:
        """Extract feature ID from file path."""
        parts = file_path.parts
        for part in parts:
            if part.startswith('feat'):
                return part
        return None
    
    def identify_conversion_targets(self) -> None:
        """Identify files that need conversion to YAML."""
        # Check each feature directory
        features = ['feat01-foundation', 'feat02-todo-orchestrator', 
                   'feat03-governance', 'feat04-core-orchestration',
                   'feat05-audit-orchestration', 'feat06-modular-design',
                   'feat07-integration-tests', 'feat08-cleanup-vacuum']
        
        for feature_id in features:
            feature_dir = self.source_of_truth / feature_id
            
            # Check if feature.yaml exists
            feature_yaml = feature_dir / "feature.yaml" if feature_dir.exists() else None
            requirements_yaml = feature_dir / "requirements.yaml" if feature_dir.exists() else None
            
            if not (feature_yaml and feature_yaml.exists()):
                self.results['conversion_needed'].append({
                    'feature': feature_id,
                    'missing': 'feature.yaml',
                    'priority': 'HIGH',
                    'estimated_minutes': 90
                })
            
            if not (requirements_yaml and requirements_yaml.exists()):
                self.results['conversion_needed'].append({
                    'feature': feature_id,
                    'missing': 'requirements.yaml',
                    'priority': 'HIGH',
                    'estimated_minutes': 120
                })
    
    def calculate_effort(self) -> Dict[str, Any]:
        """Calculate conversion effort estimates."""
        total_conversions = len(self.results['conversion_needed'])
        total_minutes = sum(item['estimated_minutes'] for item in self.results['conversion_needed'])
        
        return {
            'total_conversions_needed': total_conversions,
            'total_estimated_minutes': total_minutes,
            'total_estimated_hours': round(total_minutes / 60, 1),
            'conversions_by_priority': {
                'HIGH': sum(1 for item in self.results['conversion_needed'] if item['priority'] == 'HIGH'),
                'MEDIUM': sum(1 for item in self.results['conversion_needed'] if item['priority'] == 'MEDIUM'),
                'LOW': sum(1 for item in self.results['conversion_needed'] if item['priority'] == 'LOW')
            }
        }
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate comprehensive audit report."""
        self.scan_requirements()
        self.identify_conversion_targets()
        effort = self.calculate_effort()
        
        report = {
            **self.results,
            'effort_estimate': effort,
            'summary': {
                'total_files_scanned': self.results['total_files'],
                'yaml_files': len(self.results['files_by_type']['yaml']),
                'markdown_files': len(self.results['files_by_type']['markdown']),
                'features_with_yaml': len(self.results['already_yaml']),
                'conversions_needed': len(self.results['conversion_needed'])
            }
        }
        
        return report
    
    def save_report(self, output_path: Path, format: str = 'yaml') -> None:
        """Save audit report to file."""
        report = self.generate_report()
        
        if format == 'yaml':
            with open(output_path, 'w') as f:
                yaml.dump(report, f, default_flow_style=False, sort_keys=False)
        elif format == 'json':
            with open(output_path, 'w') as f:
                json.dump(report, f, indent=2)
        elif format == 'md':
            self._save_markdown_report(output_path, report)
    
    def _save_markdown_report(self, output_path: Path, report: Dict[str, Any]) -> None:
        """Save report as markdown."""
        lines = []
        lines.append("# CORTEX 6.0 Requirements Audit Report")
        lines.append(f"\n**Generated:** {report['audit_timestamp']}")
        lines.append(f"**Total Files Scanned:** {report['summary']['total_files_scanned']}")
        lines.append("")
        
        lines.append("## Summary")
        lines.append(f"- **YAML Files:** {report['summary']['yaml_files']}")
        lines.append(f"- **Markdown Files:** {report['summary']['markdown_files']}")
        lines.append(f"- **Features with YAML:** {report['summary']['features_with_yaml']}")
        lines.append(f"- **Conversions Needed:** {report['summary']['conversions_needed']}")
        lines.append("")
        
        lines.append("## Conversion Effort")
        effort = report['effort_estimate']
        lines.append(f"- **Total Conversions:** {effort['total_conversions_needed']}")
        lines.append(f"- **Estimated Time:** {effort['total_estimated_hours']} hours")
        lines.append("")
        
        lines.append("## Conversions Needed")
        for item in report['conversion_needed']:
            lines.append(f"- **{item['feature']}**: Missing `{item['missing']}` (Priority: {item['priority']}, Est: {item['estimated_minutes']}min)")
        lines.append("")
        
        lines.append("## Existing YAML Files")
        for item in report['already_yaml']:
            lines.append(f"- ✅ {item['feature']}: `{item['type']}`")
        
        with open(output_path, 'w') as f:
            f.write('\n'.join(lines))


def main():
    """CLI entry point."""
    cortex6_root = Path(__file__).parent.parent.parent / ".asif" / "AI-Learning" / "cortex6"
    reports_dir = Path(__file__).parent.parent.parent / ".asif" / "AI-Learning" / "cortex6-fixes" / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)
    
    print("📋 Starting CORTEX 6.0 Requirements Audit...")
    
    auditor = RequirementsAuditor(cortex6_root)
    
    # Generate reports in multiple formats
    print("   Scanning requirements files...")
    auditor.save_report(reports_dir / "requirements-audit.yaml", format='yaml')
    auditor.save_report(reports_dir / "requirements-audit.json", format='json')
    auditor.save_report(reports_dir / "requirements-audit.md", format='md')
    
    # Print summary
    report = auditor.generate_report()
    print(f"\n✅ Audit Complete!")
    print(f"   Total Files: {report['summary']['total_files_scanned']}")
    print(f"   YAML Files: {report['summary']['yaml_files']}")
    print(f"   Markdown Files: {report['summary']['markdown_files']}")
    print(f"   Conversions Needed: {report['summary']['conversions_needed']}")
    print(f"   Estimated Effort: {report['effort_estimate']['total_estimated_hours']} hours")
    print(f"\n📄 Reports saved to: {reports_dir}")


if __name__ == "__main__":
    main()
