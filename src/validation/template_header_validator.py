"""
Template Header Validator - Response Template Compliance Checker

Validates that all response templates include:
1. CORTEX title header with 🧠 emoji
2. Author attribution (Asif Hussain)
3. GitHub repository link
4. Professional section icons (🎯 ⚠️ 💬 📝 🔍)
5. NO old format markers ('✓ Accept', '⚡ Challenge')

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 3.2 (Icon Enhancement + Old Format Detection)
Status: PRODUCTION
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
    violation_type: str  # 'missing_header', 'outdated_copyright', 'missing_author', 'missing_repo_link', 'old_format', 'missing_icon'
    current_value: Optional[str]
    expected_value: str
    severity: str  # 'critical', 'warning'


class TemplateHeaderValidator:
    """
    Validates response template headers for legal compliance and attribution.
    
    Required header format (v3.2):
    ```
    # 🧠 CORTEX [Title]
    **Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
    
    ---
    
    ## 🎯 My Understanding Of Your Request
    ## ⚠️ Challenge
    ## 💬 Response
    ## 📝 Your Request
    ## 🔍 Next Steps
    ```
    
    FORBIDDEN (Old Format):
    - ✓ Accept
    - ⚡ Challenge
    - Missing section icons
    - Missing brain emoji (🧠)
    """
    
    # Header component patterns (v3.2)
    TITLE_PATTERN = r'^#\s+🧠\s+CORTEX\s+.+'
    AUTHOR_PATTERN = r'\*\*Author:\*\*\s*Asif\s+Hussain'
    GITHUB_PATTERN = r'\*\*GitHub:\*\*\s*github\.com/asifhussain60/CORTEX'
    SEPARATOR_PATTERN = r'---'
    
    # Section icon patterns (v3.2)
    UNDERSTANDING_ICON = r'##\s+🎯\s+My\s+Understanding'
    CHALLENGE_ICON = r'##\s+⚠️\s+Challenge'
    RESPONSE_ICON = r'##\s+💬\s+Response'
    REQUEST_ICON = r'##\s+📝\s+Your\s+Request'
    NEXT_STEPS_ICON = r'##\s+🔍\s+Next\s+Steps'
    
    # Old format detection patterns (FORBIDDEN - only in headers/labels)
    OLD_CHALLENGE_ACCEPT = r'##\s+Challenge\s+✓\s+\*\*Accept'
    OLD_CHALLENGE_EMOJI = r'##\s+Challenge\s+⚡\s+\*\*Challenge'
    
    # Expected header template (v3.2)
    EXPECTED_HEADER = (
        "# 🧠 CORTEX [Title]\n"
        "**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX\n\n"
        "---"
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
        """Validate individual template header compliance (v3.2 format)."""
        if not template_content:
            return
            
        # Check for CORTEX title header with brain emoji (# 🧠 CORTEX [Title])
        if not re.search(self.TITLE_PATTERN, template_content, re.MULTILINE):
            self.violations.append(HeaderViolation(
                template_name=template_name,
                violation_type='missing_header',
                current_value=None,
                expected_value='# 🧠 CORTEX [Title]',
                severity='critical'
            ))
        
        # Check for author attribution
        if not re.search(self.AUTHOR_PATTERN, template_content):
            self.violations.append(HeaderViolation(
                template_name=template_name,
                violation_type='missing_author',
                current_value=None,
                expected_value='**Author:** Asif Hussain',
                severity='critical'
            ))
        
        # Check for GitHub link
        if not re.search(self.GITHUB_PATTERN, template_content):
            self.violations.append(HeaderViolation(
                template_name=template_name,
                violation_type='missing_github_link',
                current_value=None,
                expected_value='**GitHub:** github.com/asifhussain60/CORTEX',
                severity='critical'
            ))
        
        # Check for horizontal rule separator
        if not re.search(self.SEPARATOR_PATTERN, template_content):
            self.violations.append(HeaderViolation(
                template_name=template_name,
                violation_type='missing_separator',
                current_value=None,
                expected_value='---',
                severity='warning'
            ))
        
        # v3.2: Check for OLD FORMAT markers (FORBIDDEN)
        if re.search(self.OLD_CHALLENGE_ACCEPT, template_content):
            self.violations.append(HeaderViolation(
                template_name=template_name,
                violation_type='old_format_accept',
                current_value='✓ Accept',
                expected_value='Remove old "✓ Accept" format - use "No Challenge" or state challenge',
                severity='critical'
            ))
        
        if re.search(self.OLD_CHALLENGE_EMOJI, template_content):
            self.violations.append(HeaderViolation(
                template_name=template_name,
                violation_type='old_format_challenge',
                current_value='⚡ Challenge',
                expected_value='Remove old "⚡ Challenge" format - use "No Challenge" or state challenge',
                severity='critical'
            ))
        
        # v3.2: Check for section icons (at least 3 of 5 should be present)
        icon_checks = {
            'understanding': self.UNDERSTANDING_ICON,
            'challenge': self.CHALLENGE_ICON,
            'response': self.RESPONSE_ICON,
            'request': self.REQUEST_ICON,
            'next_steps': self.NEXT_STEPS_ICON
        }
        
        icons_found = 0
        missing_icons = []
        for icon_name, icon_pattern in icon_checks.items():
            if re.search(icon_pattern, template_content, re.IGNORECASE):
                icons_found += 1
            else:
                missing_icons.append(icon_name)
        
        # If less than 3 icons found, flag as missing icons (warning)
        if icons_found < 3:
            self.violations.append(HeaderViolation(
                template_name=template_name,
                violation_type='missing_section_icons',
                current_value=f'{icons_found}/5 icons found',
                expected_value=f'Add section icons: 🎯 Understanding | ⚠️ Challenge | 💬 Response | 📝 Request | 🔍 Next Steps (missing: {", ".join(missing_icons)})',
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
                    if violation.violation_type == 'missing_github_link':
                        updates.append({
                            'component': 'github_link',
                            'new_value': violation.expected_value
                        })
                    elif violation.violation_type == 'missing_author':
                        updates.append({
                            'component': 'author',
                            'new_value': violation.expected_value
                        })
                    elif violation.violation_type == 'missing_separator':
                        updates.append({
                            'component': 'separator',
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
