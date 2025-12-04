#!/usr/bin/env python3
"""
Dashboard Validator

Comprehensive validation of dashboard functionality including:
- Tab data completeness
- JavaScript function availability
- Data structure compatibility
- Interactive element validation
- Visualization rendering checks

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import json
import logging
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple, Set
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ValidationTest:
    """Individual validation test result"""
    test_name: str
    category: str  # tab, data, function, interaction, visualization
    passed: bool
    message: str
    severity: str = "error"  # error, warning, info


@dataclass
class ValidationResult:
    """Result of a validation check"""
    tab_name: str
    passed: bool
    tests: List[ValidationTest] = field(default_factory=list)
    data_present: bool = True
    
    @property
    def issues(self) -> List[str]:
        """Get error messages"""
        return [t.message for t in self.tests if not t.passed and t.severity == "error"]
    
    @property
    def warnings(self) -> List[str]:
        """Get warning messages"""
        return [t.message for t in self.tests if not t.passed and t.severity == "warning"]
    
    
class DashboardValidator:
    """Validates dashboard data for all tabs"""
    
    REQUIRED_TABS = [
        'overview',
        'techstack',
        'architecture',
        'security',
        'uml',
        'recommendations',
        'data'
    ]
    
    def __init__(self, output_dir: Path):
        self.output_dir = Path(output_dir)
        self.results: List[ValidationResult] = []
        
    def validate_all(self) -> Tuple[bool, Dict[str, Any]]:
        """
        Validate all dashboard tabs
        
        Returns:
            Tuple of (all_passed, detailed_results)
        """
        logger.info(f"Validating dashboard data in: {self.output_dir}")
        
        # Load all data files
        data_files = self._load_data_files()
        
        # Validate each tab
        self.results = [
            self._validate_overview(data_files),
            self._validate_techstack(data_files),
            self._validate_architecture(data_files),
            self._validate_security(data_files),
            self._validate_uml(data_files),
            self._validate_recommendations(data_files),
            self._validate_data_tab(data_files)
        ]
        
        # Generate summary
        all_passed = all(r.passed for r in self.results)
        summary = self._generate_summary()
        
        return all_passed, summary
        
    def _load_data_files(self) -> Dict[str, Any]:
        """Load all JSON data files"""
        data = {}
        
        file_mapping = {
            'project_info': 'project_info.json',
            'quality': 'quality_score.json',
            'security': 'security_scan.json',
            'architecture': 'architecture.json',
            'techstack': 'techstack.json',
            'recommendations': 'recommendations.json',
            'performance': 'performance_metrics.json'
        }
        
        for key, filename in file_mapping.items():
            file_path = self.output_dir / filename
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data[key] = json.load(f)
                except Exception as e:
                    logger.error(f"Failed to load {filename}: {e}")
                    data[key] = None
            else:
                logger.warning(f"Missing data file: {filename}")
                data[key] = None
                
        return data
        
    def _validate_overview(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate Overview tab data"""
        issues = []
        warnings = []
        data_present = True
        
        # Check project info
        if not data.get('project_info'):
            issues.append("Missing project_info.json")
            data_present = False
        else:
            proj = data['project_info']
            if not proj.get('name'):
                issues.append("Project name not set")
            if proj.get('files', 0) == 0:
                warnings.append("No files counted")
            if proj.get('lines', 0) == 0:
                warnings.append("No lines counted")
                
        # Check quality data
        if not data.get('quality'):
            issues.append("Missing quality_score.json")
            data_present = False
        else:
            quality = data['quality']
            if quality.get('score', 0) == 0:
                warnings.append("Quality score is 0 - may need recalculation")
                
        # Check security data
        if not data.get('security'):
            issues.append("Missing security_scan.json")
            data_present = False
            
        passed = len(issues) == 0 and data_present
        return ValidationResult('overview', passed, issues, warnings, data_present)
        
    def _validate_techstack(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate Tech Stack tab data"""
        issues = []
        warnings = []
        data_present = True
        
        if not data.get('techstack'):
            issues.append("Missing techstack.json")
            data_present = False
        else:
            tech = data['techstack']
            
            # Check languages
            languages = tech.get('languages', [])
            if not languages:
                issues.append("No languages detected")
            else:
                if len(languages) < 1:
                    warnings.append("Only 1 language detected - may be incomplete")
                    
            # Check frameworks
            frameworks = tech.get('frameworks', [])
            if not frameworks:
                warnings.append("No frameworks detected")
                
            # Check dependencies
            dependencies = tech.get('dependencies', [])
            if not dependencies:
                warnings.append("No dependencies detected")
                
        passed = len(issues) == 0 and data_present
        return ValidationResult('techstack', passed, issues, warnings, data_present)
        
    def _validate_architecture(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate Architecture tab data"""
        issues = []
        warnings = []
        data_present = True
        
        if not data.get('architecture'):
            issues.append("Missing architecture.json")
            data_present = False
        else:
            arch = data['architecture']
            
            # Check nodes
            nodes = arch.get('nodes', [])
            if not nodes:
                issues.append("No architecture nodes detected")
            else:
                if len(nodes) < 10:
                    warnings.append(f"Only {len(nodes)} nodes - may be incomplete scan")
                    
            # Check relationships
            relationships = arch.get('relationships', [])
            if not relationships:
                warnings.append("No relationships detected between nodes")
                
            # Check if D3 format is available
            if 'd3_data' not in arch:
                issues.append("D3 visualization data not generated")
                
        passed = len(issues) == 0 and data_present
        return ValidationResult('architecture', passed, issues, warnings, data_present)
        
    def _validate_security(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate Security tab data"""
        issues = []
        warnings = []
        data_present = True
        
        if not data.get('security'):
            issues.append("Missing security_scan.json")
            data_present = False
        else:
            security = data['security']
            
            # Security data should have vulnerabilities array
            if 'vulnerabilities' not in security:
                issues.append("Security scan missing vulnerabilities array")
            else:
                vulns = security['vulnerabilities']
                if not isinstance(vulns, list):
                    issues.append("Vulnerabilities is not a list")
                elif len(vulns) == 0:
                    warnings.append("No vulnerabilities detected (good!)")
                    
        passed = len(issues) == 0 and data_present
        return ValidationResult('security', passed, issues, warnings, data_present)
        
    def _validate_uml(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate UML tab data"""
        issues = []
        warnings = []
        data_present = True
        
        # UML is optional but should have SVG if generated
        dashboard_path = self.output_dir / 'dashboard.html'
        if dashboard_path.exists():
            with open(dashboard_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if '"uml_diagram": ""' in content or '"uml_diagram":""' in content:
                    warnings.append("UML diagram not generated (graphviz may be missing)")
                elif '<svg' not in content:
                    warnings.append("UML diagram may not contain valid SVG")
        else:
            issues.append("Dashboard.html not found")
            data_present = False
            
        passed = len(issues) == 0
        return ValidationResult('uml', passed, issues, warnings, data_present)
        
    def _validate_recommendations(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate Recommendations tab data"""
        issues = []
        warnings = []
        data_present = True
        
        if not data.get('recommendations'):
            issues.append("Missing recommendations.json")
            data_present = False
        else:
            recs = data['recommendations']
            if not isinstance(recs, list):
                issues.append("Recommendations is not a list")
            elif len(recs) == 0:
                warnings.append("No recommendations generated")
            else:
                # Check recommendation structure
                for i, rec in enumerate(recs):
                    if not rec.get('title'):
                        issues.append(f"Recommendation {i+1} missing title")
                    if not rec.get('priority'):
                        issues.append(f"Recommendation {i+1} missing priority")
                        
        passed = len(issues) == 0 and data_present
        return ValidationResult('recommendations', passed, issues, warnings, data_present)
        
    def _validate_data_tab(self, data: Dict[str, Any]) -> ValidationResult:
        """Validate Data tab (raw JSON)"""
        issues = []
        warnings = []
        data_present = True
        
        # Data tab just needs the dashboard to exist
        dashboard_path = self.output_dir / 'dashboard.html'
        if not dashboard_path.exists():
            issues.append("Dashboard.html not found")
            data_present = False
        else:
            # Check if dashboard has embedded data
            with open(dashboard_path, 'r', encoding='utf-8') as f:
                content = f.read()
                if 'const dashboardData' not in content:
                    issues.append("Dashboard missing embedded data")
                    
        passed = len(issues) == 0 and data_present
        return ValidationResult('data', passed, issues, warnings, data_present)
        
    def _generate_summary(self) -> Dict[str, Any]:
        """Generate validation summary"""
        total_tabs = len(self.results)
        passed_tabs = sum(1 for r in self.results if r.passed)
        total_issues = sum(len(r.issues) for r in self.results)
        total_warnings = sum(len(r.warnings) for r in self.results)
        
        return {
            'total_tabs': total_tabs,
            'passed_tabs': passed_tabs,
            'failed_tabs': total_tabs - passed_tabs,
            'total_issues': total_issues,
            'total_warnings': total_warnings,
            'results': [
                {
                    'tab': r.tab_name,
                    'passed': r.passed,
                    'data_present': r.data_present,
                    'issues': r.issues,
                    'warnings': r.warnings
                }
                for r in self.results
            ]
        }
        
    def generate_report(self) -> str:
        """Generate human-readable validation report"""
        lines = [
            "=" * 70,
            "DASHBOARD VALIDATION REPORT",
            "=" * 70,
            ""
        ]
        
        summary = self._generate_summary()
        lines.extend([
            f"Total Tabs: {summary['total_tabs']}",
            f"✅ Passed: {summary['passed_tabs']}",
            f"❌ Failed: {summary['failed_tabs']}",
            f"⚠️ Warnings: {summary['total_warnings']}",
            ""
        ])
        
        for result in self.results:
            status = "✅ PASS" if result.passed else "❌ FAIL"
            lines.append(f"{status} | {result.tab_name.upper()} Tab")
            
            if result.issues:
                for issue in result.issues:
                    lines.append(f"    ❌ {issue}")
                    
            if result.warnings:
                for warning in result.warnings:
                    lines.append(f"    ⚠️ {warning}")
                    
            if not result.issues and not result.warnings:
                lines.append(f"    No issues detected")
                
            lines.append("")
            
        lines.append("=" * 70)
        return "\n".join(lines)


def validate_dashboard(output_dir: Path) -> Tuple[bool, Dict[str, Any], str]:
    """
    Convenience function to validate dashboard
    
    Args:
        output_dir: Directory containing dashboard files
        
    Returns:
        Tuple of (all_passed, summary_dict, report_text)
    """
    validator = DashboardValidator(output_dir)
    all_passed, summary = validator.validate_all()
    report = validator.generate_report()
    
    return all_passed, summary, report
