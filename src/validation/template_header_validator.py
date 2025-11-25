"""
Template Header Validator - Response Template Compliance Checker

Validates that all response templates include:
1. CORTEX title header with 🧠 emoji
2. Author attribution (Asif Hussain)
3. Copyright notice (© 2024-2025)
4. GitHub repository link

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
Status: IMPLEMENTATION
"""

import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import yaml

logger = logging.getLogger(__name__)


@dataclass
class HeaderViolation:
    """Represents a template header compliance violation."""
    template_name: str
    violation_type: str  # 'missing_header', 'outdated_copyright', 'missing_author', 'missing_repo_link'
    current_value: Optional[str]
    expected_value: str
    severity: str  # 'critical', 'warning'


class TemplateHeaderValidator:
    """
    Validates response template headers for legal compliance and attribution.
    
    Required header format:
    ```
    🧠 **CORTEX [Operation Type]**
    Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX
    ```
    """
    
    # Header component patterns
    TITLE_PATTERN = r'🧠\s*\*\*CORTEX\s+\[.*?\]\*\*'
    AUTHOR_PATTERN = r'Author:\s*Asif\s+Hussain'
    COPYRIGHT_PATTERN = r'©\s*2024-2025'
    REPO_PATTERN = r'github\.com/asifhussain60/CORTEX'
    
    # Expected header template
    EXPECTED_HEADER = (
        "🧠 **CORTEX [Operation Type]**\n"
        "Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX"
    )
    
    def __init__(self, templates_path: Path):
        self.templates_path = templates_path
        self.templates: Dict[str, str] = {}
        self.violations: List[HeaderViolation] = []
        
    def validate(self) -> Dict[str, Any]:
        """
        Run all template header validations.
        
        Returns:
            Dict with validation results and violations
        """
        self.violations = []
        
        # Load templates from YAML
        self._load_templates()
        
        # Validate each template
        for template_name, template_content in self.templates.items():
            self._validate_template_header(template_name, template_content)
        
        # Calculate scores
        total_templates = len(self.templates)
        if total_templates == 0:
            return {
                'score': 0,
                'status': 'fail',
                'violations': [],
                'critical_count': 0,
                'warning_count': 0,
                'compliant_templates': 0,
                'total_templates': 0
            }
        
        critical_violations = len([v for v in self.violations if v.severity == 'critical'])
        compliant_templates = total_templates - len(set(v.template_name for v in self.violations))
        score = (compliant_templates / total_templates) * 100
        
        return {
            'score': score,
            'status': 'pass' if score >= 80 else 'fail',
            'violations': self.violations,
            'critical_count': critical_violations,
            'warning_count': len(self.violations) - critical_violations,
            'compliant_templates': compliant_templates,
            'total_templates': total_templates
        }
    
    def _load_templates(self):
        """Load templates from response-templates.yaml."""
        if not self.templates_path.exists():
            logger.warning(f"Templates file not found: {self.templates_path}")
            return
            
        try:
            with open(self.templates_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                
            if not data or 'templates' not in data:
                logger.warning("No templates section found in YAML")
                return
                
            # Extract template content
            for template_name, template_data in data['templates'].items():
                if isinstance(template_data, dict) and 'content' in template_data:
                    self.templates[template_name] = template_data['content']
                    
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse templates YAML: {e}")
        except Exception as e:
            logger.error(f"Failed to load templates: {e}")
    
    def _validate_template_header(self, template_name: str, template_content: str):
        """Validate individual template header compliance."""
        if not template_content:
            return
            
        # Check for CORTEX title header
        if not re.search(self.TITLE_PATTERN, template_content):
            self.violations.append(HeaderViolation(
                template_name=template_name,
                violation_type='missing_header',
                current_value=None,
                expected_value='🧠 **CORTEX [Operation Type]**',
                severity='critical'
            ))
        
        # Check for author attribution
        if not re.search(self.AUTHOR_PATTERN, template_content):
            self.violations.append(HeaderViolation(
                template_name=template_name,
                violation_type='missing_author',
                current_value=None,
                expected_value='Author: Asif Hussain',
                severity='critical'
            ))
        
        # Check for copyright notice with current year
        if not re.search(self.COPYRIGHT_PATTERN, template_content):
            # Check if there's an outdated copyright
            old_copyright_match = re.search(r'©\s*\d{4}(?:-\d{4})?', template_content)
            current_value = old_copyright_match.group(0) if old_copyright_match else None
            
            self.violations.append(HeaderViolation(
                template_name=template_name,
                violation_type='outdated_copyright',
                current_value=current_value,
                expected_value='© 2024-2025',
                severity='warning'
            ))
        
        # Check for GitHub repository link
        if not re.search(self.REPO_PATTERN, template_content):
            self.violations.append(HeaderViolation(
                template_name=template_name,
                violation_type='missing_repo_link',
                current_value=None,
                expected_value='github.com/asifhussain60/CORTEX',
                severity='warning'
            ))
    
    def generate_remediation_templates(self) -> List[Dict[str, Any]]:
        """
        Generate compliant headers for non-compliant templates.
        
        Returns:
            List of remediation templates with corrected headers
        """
        templates = []
        
        # Group violations by template
        template_violations: Dict[str, List[HeaderViolation]] = {}
        for violation in self.violations:
            if violation.template_name not in template_violations:
                template_violations[violation.template_name] = []
            template_violations[violation.template_name].append(violation)
        
        # Generate remediation for each template
        for template_name, violations in template_violations.items():
            violation_types = {v.violation_type for v in violations}
            
            # Determine remediation strategy
            if 'missing_header' in violation_types:
                # Need to add complete header
                templates.append({
                    'type': 'header_addition',
                    'template_name': template_name,
                    'header_content': self.EXPECTED_HEADER,
                    'description': f'Add compliant header to {template_name} template',
                    'action': 'prepend',
                    'violations': [v.violation_type for v in violations]
                })
            else:
                # Need to update existing header components
                updates = []
                for violation in violations:
                    if violation.violation_type == 'outdated_copyright':
                        updates.append({
                            'component': 'copyright',
                            'old_value': violation.current_value,
                            'new_value': violation.expected_value
                        })
                    elif violation.violation_type == 'missing_author':
                        updates.append({
                            'component': 'author',
                            'new_value': violation.expected_value
                        })
                    elif violation.violation_type == 'missing_repo_link':
                        updates.append({
                            'component': 'repo_link',
                            'new_value': violation.expected_value
                        })
                
                templates.append({
                    'type': 'header_update',
                    'template_name': template_name,
                    'updates': updates,
                    'description': f'Update header components in {template_name} template',
                    'violations': [v.violation_type for v in violations]
                })
        
        return templates
    
    def generate_compliance_report(self) -> str:
        """
        Generate human-readable compliance report.
        
        Returns:
            Markdown report with violations and remediation steps
        """
        results = self.validate()
        
        report = [
            "# Template Header Compliance Report",
            "",
            f"**Status:** {'✅ PASS' if results['status'] == 'pass' else '❌ FAIL'}",
            f"**Score:** {results['score']:.1f}%",
            f"**Compliant Templates:** {results['compliant_templates']}/{results['total_templates']}",
            "",
            "## Violations",
            ""
        ]
        
        if not self.violations:
            report.append("✅ All templates are compliant!")
        else:
            # Group by template
            template_violations: Dict[str, List[HeaderViolation]] = {}
            for violation in self.violations:
                if violation.template_name not in template_violations:
                    template_violations[violation.template_name] = []
                template_violations[violation.template_name].append(violation)
            
            for template_name, violations in sorted(template_violations.items()):
                severity_emoji = '🔴' if any(v.severity == 'critical' for v in violations) else '🟡'
                report.append(f"### {severity_emoji} {template_name}")
                report.append("")
                
                for violation in violations:
                    severity_label = violation.severity.upper()
                    report.append(f"- **[{severity_label}]** {violation.violation_type}")
                    if violation.current_value:
                        report.append(f"  - Current: `{violation.current_value}`")
                    report.append(f"  - Expected: `{violation.expected_value}`")
                    report.append("")
        
        report.extend([
            "## Expected Header Format",
            "",
            "```",
            self.EXPECTED_HEADER,
            "```"
        ])
        
        return "\n".join(report)
