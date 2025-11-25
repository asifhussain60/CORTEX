"""
CORTEX Template Validator
=========================

Validates response templates against meta-template.yaml structure
and enforces quality standards defined in the meta-template.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import sys
import yaml
import re
from pathlib import Path
from typing import Dict, List, Any, Tuple
from dataclasses import dataclass


@dataclass
class ValidationResult:
    """Result of template validation"""
    template_name: str
    valid: bool
    errors: List[Dict[str, str]]
    warnings: List[Dict[str, str]]
    info: List[Dict[str, str]]


class TemplateValidator:
    """Validates CORTEX response templates against meta-template rules"""
    
    def __init__(self, meta_template_path: str = "cortex-brain/templates/meta-template.yaml"):
        """Initialize validator with meta-template rules"""
        self.meta_template_path = Path(meta_template_path)
        self.meta_template = self._load_meta_template()
        # Extract standard emojis if they exist
        content_rules = self.meta_template.get('validation_rules', {}).get('content', [])
        self.standard_emojis = {}
        for rule in content_rules:
            if isinstance(rule, dict) and 'standard_emojis' in rule:
                self.standard_emojis = rule['standard_emojis']
                break
    
    def _load_meta_template(self) -> Dict:
        """Load meta-template definition with caching"""
        if not self.meta_template_path.exists():
            raise FileNotFoundError(f"Meta-template not found: {self.meta_template_path}")
        
        try:
            # Use universal YAML cache for performance
            from src.utils.yaml_cache import load_yaml_cached
            meta = load_yaml_cached(self.meta_template_path)
        except ImportError:
            # Fallback to direct loading
            with open(self.meta_template_path, 'r', encoding='utf-8') as f:
                meta = yaml.safe_load(f)
        
        # Ensure validation_rules structure exists
        if 'validation_rules' not in meta:
            meta['validation_rules'] = {'content': []}
        return meta
    
    def validate_file(self, template_file: str, template_name: str = None) -> List[ValidationResult]:
        """
        Validate all templates in a file or a specific template.
        
        Args:
            template_file: Path to response-templates.yaml
            template_name: Optional specific template to validate
            
        Returns:
            List of ValidationResult objects
        """
        template_path = Path(template_file)
        if not template_path.exists():
            raise FileNotFoundError(f"Template file not found: {template_path}")
        
        try:
            # Use universal YAML cache for response-templates.yaml
            from src.utils.yaml_cache import load_yaml_cached
            data = load_yaml_cached(template_path)
        except ImportError:
            # Fallback to direct loading
            with open(template_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
        
        templates = data.get('templates', {})
        results = []
        
        if template_name:
            if template_name in templates:
                result = self.validate_template(template_name, templates[template_name])
                results.append(result)
            else:
                result = ValidationResult(
                    template_name=template_name,
                    valid=False,
                    errors=[{"rule": "Template not found", "message": f"Template '{template_name}' not found in file"}],
                    warnings=[],
                    info=[]
                )
                results.append(result)
        else:
            for name, template_data in templates.items():
                result = self.validate_template(name, template_data)
                results.append(result)
        
        return results
    
    def validate_template(self, template_name: str, template_data: Dict) -> ValidationResult:
        """
        Validate a single template against meta-template rules.
        
        Args:
            template_name: Name of the template
            template_data: Template configuration dictionary
            
        Returns:
            ValidationResult with errors, warnings, and info
        """
        errors = []
        warnings = []
        info = []
        
        try:
            # Structural validation
            errors.extend(self._validate_required_fields(template_name, template_data))
            errors.extend(self._validate_5_part_structure(template_name, template_data))
            errors.extend(self._validate_no_separator_lines(template_name, template_data))
            errors.extend(self._validate_request_echo_placement(template_name, template_data))
            
            # Content validation
            warnings.extend(self._validate_no_hardcoded_counts(template_name, template_data))
            warnings.extend(self._validate_placeholder_consistency(template_name, template_data))
            warnings.extend(self._validate_trigger_uniqueness(template_name, template_data))
            
            # Formatting validation
            info.extend(self._validate_emoji_usage(template_name, template_data))
            
        except Exception as e:
            errors.append({
                "rule": "Validation error",
                "message": f"Error validating template '{template_name}': {str(e)}",
                "severity": "ERROR"
            })
        
        valid = len(errors) == 0
        
        return ValidationResult(
            template_name=template_name,
            valid=valid,
            errors=errors,
            warnings=warnings,
            info=info
        )
    
    def _validate_required_fields(self, template_name: str, template_data: Dict) -> List[Dict]:
        """Validate required fields are present"""
        errors = []
        required_fields = ['name', 'trigger', 'response_type', 'content']
        
        for field in required_fields:
            if field not in template_data:
                errors.append({
                    "rule": "Required field missing",
                    "field": field,
                    "message": f"Template '{template_name}' missing required field: {field}",
                    "severity": "ERROR"
                })
        
        return errors
    
    def _validate_5_part_structure(self, template_name: str, template_data: Dict) -> List[Dict]:
        """Validate 5-part mandatory format"""
        errors = []
        content = template_data.get('content', '')
        
        required_sections = [
            (r'🧠.*CORTEX|\\U0001F9E0.*CORTEX', 'Header (🧠 CORTEX)'),
            (r'Author:.*Asif Hussain', 'Author line'),
            (r'🎯.*My Understanding|\\U0001F3AF.*My Understanding', 'Understanding section (🎯)'),
            (r'⚠️.*Challenge|\\u26A0\\uFE0F.*Challenge', 'Challenge section (⚠️)'),
            (r'💬.*Response|\\U0001F4AC.*Response', 'Response section (💬)'),
            (r'📝.*Your Request|\\U0001F4DD.*Your Request', 'Request Echo section (📝)'),
            (r'🔍.*Next Steps|\\U0001F50D.*Next Steps', 'Next Steps section (🔍)')
        ]
        
        for pattern, section_name in required_sections:
            if not re.search(pattern, content):
                errors.append({
                    "rule": "Mandatory 5-part format",
                    "section": section_name,
                    "message": f"Template '{template_name}' missing required section: {section_name}",
                    "severity": "ERROR"
                })
        
        return errors
    
    def _validate_no_separator_lines(self, template_name: str, template_data: Dict) -> List[Dict]:
        """Validate no horizontal separator lines present"""
        errors = []
        content = template_data.get('content', '')
        
        # Check for separator patterns (3+ repeated characters)
        separator_patterns = [
            r'━{3,}',  # U+2501
            r'═{3,}',  # U+2550
            r'─{3,}',  # U+2500
            r'_{3,}',  # Underscore
            r'-{3,}'   # Hyphen
        ]
        
        for pattern in separator_patterns:
            matches = re.findall(pattern, content)
            if matches:
                errors.append({
                    "rule": "No separator lines",
                    "pattern": pattern,
                    "matches": len(matches),
                    "message": f"Template '{template_name}' contains {len(matches)} separator line(s). These break rendering in GitHub Copilot Chat.",
                    "severity": "ERROR",
                    "auto_fix": True
                })
        
        return errors
    
    def _validate_request_echo_placement(self, template_name: str, template_data: Dict) -> List[Dict]:
        """Validate Request Echo appears between Response and Next Steps"""
        errors = []
        content = template_data.get('content', '')
        
        # Find positions of sections
        response_match = re.search(r'💬.*Response|\\U0001F4AC.*Response', content)
        request_match = re.search(r'📝.*Your Request|\\U0001F4DD.*Your Request', content)
        next_match = re.search(r'🔍.*Next Steps|\\U0001F50D.*Next Steps', content)
        
        if response_match and request_match and next_match:
            response_pos = response_match.start()
            request_pos = request_match.start()
            next_pos = next_match.start()
            
            if not (response_pos < request_pos < next_pos):
                errors.append({
                    "rule": "Request echo placement",
                    "message": f"Template '{template_name}' has Request Echo in wrong position. Must be between Response and Next Steps.",
                    "severity": "ERROR",
                    "reason": "Most common quality violation - bridges response to actionable steps"
                })
        
        return errors
    
    def _validate_no_hardcoded_counts(self, template_name: str, template_data: Dict) -> List[Dict]:
        """Validate no hardcoded numbers in content"""
        warnings = []
        content = template_data.get('content', '')
        
        # Find potential hardcoded counts (numbers not in placeholders)
        # Look for numbers followed by count-related words
        count_patterns = [
            r'\b(\d+)\s+(files?|classes?|functions?|tests?|issues?|errors?|warnings?|templates?|modules?)\b',
            r'\b(found|detected|identified)\s+(\d+)',
            r'\b(\d+)\s+(of|out of)\s+\d+'
        ]
        
        for pattern in count_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                # Check if these numbers are in placeholder context
                for match in matches:
                    number = match[0] if isinstance(match, tuple) else match
                    if number.isdigit():
                        warnings.append({
                            "rule": "No hardcoded counts",
                            "number": number,
                            "message": f"Template '{template_name}' may contain hardcoded count: {number}. Use placeholders or qualitative descriptions.",
                            "severity": "WARNING",
                            "suggestion": "Use {{count}} placeholder or terms like 'several', 'many', 'multiple'"
                        })
                        break  # Only report once per template
        
        return warnings
    
    def _validate_placeholder_consistency(self, template_name: str, template_data: Dict) -> List[Dict]:
        """Validate all placeholders are declared"""
        warnings = []
        content = template_data.get('content', '')
        context_template = template_data.get('context_summary_template', '')
        
        # Find all placeholders in content
        content_placeholders = set(re.findall(r'\{\{([a-zA-Z_][a-zA-Z0-9_]*)\}\}', content))
        context_placeholders = set(re.findall(r'\{([a-zA-Z_][a-zA-Z0-9_]*)\}', context_template))
        
        # Placeholders in content should be in context_summary_template if it exists
        if context_template and content_placeholders:
            undeclared = content_placeholders - context_placeholders
            if undeclared:
                warnings.append({
                    "rule": "Placeholder consistency",
                    "undeclared": list(undeclared),
                    "message": f"Template '{template_name}' has undeclared placeholders: {undeclared}",
                    "severity": "WARNING"
                })
        
        return warnings
    
    def _validate_trigger_uniqueness(self, template_name: str, template_data: Dict) -> List[Dict]:
        """Validate trigger phrases are unique (cross-template check)"""
        # This needs access to all templates, so it's a placeholder for now
        # Full implementation would require passing all templates to validator
        warnings = []
        triggers = template_data.get('trigger', [])
        
        if not triggers:
            warnings.append({
                "rule": "Trigger uniqueness",
                "message": f"Template '{template_name}' has no triggers. At least one required.",
                "severity": "WARNING"
            })
        
        return warnings
    
    def _validate_emoji_usage(self, template_name: str, template_data: Dict) -> List[Dict]:
        """Validate consistent emoji usage"""
        info = []
        content = template_data.get('content', '')
        
        # Check if standard emojis are used
        expected_emojis = {
            'header': ('🧠', '\\U0001F9E0'),
            'understanding': ('🎯', '\\U0001F3AF'),
            'response': ('💬', '\\U0001F4AC'),
            'request_echo': ('📝', '\\U0001F4DD'),
            'next_steps': ('🔍', '\\U0001F50D')
        }
        
        emoji_usage = []
        for section, (emoji, unicode_escape) in expected_emojis.items():
            if emoji in content or unicode_escape in content:
                emoji_usage.append(section)
        
        if len(emoji_usage) >= 4:  # Most emojis present
            info.append({
                "rule": "Consistent emoji usage",
                "message": f"Template '{template_name}' uses standard emoji set",
                "severity": "INFO"
            })
        
        return info


def print_validation_results(results: List[ValidationResult], verbose: bool = False):
    """Print validation results in readable format"""
    total = len(results)
    valid = sum(1 for r in results if r.valid)
    invalid = total - valid
    
    print(f"\n{'='*70}")
    print(f"CORTEX Template Validation Report")
    print(f"{'='*70}\n")
    
    print(f"Total Templates: {total}")
    print(f"✅ Valid: {valid}")
    print(f"❌ Invalid: {invalid}")
    print()
    
    # Group results by validity
    if invalid > 0:
        print(f"{'─'*70}")
        print("TEMPLATES WITH ERRORS:")
        print(f"{'─'*70}\n")
        
        for result in results:
            if not result.valid:
                print(f"❌ {result.template_name}")
                
                if result.errors:
                    print(f"   Errors ({len(result.errors)}):")
                    for error in result.errors:
                        print(f"      • [{error.get('rule', 'Unknown')}] {error.get('message', 'No message')}")
                        if error.get('auto_fix'):
                            print(f"        (Auto-fix available)")
                
                if result.warnings and verbose:
                    print(f"   Warnings ({len(result.warnings)}):")
                    for warning in result.warnings:
                        print(f"      • [{warning.get('rule', 'Unknown')}] {warning.get('message', 'No message')}")
                
                print()
    
    if verbose and valid > 0:
        print(f"{'─'*70}")
        print("VALID TEMPLATES:")
        print(f"{'─'*70}\n")
        
        for result in results:
            if result.valid:
                warning_count = len(result.warnings)
                info_count = len(result.info)
                print(f"✅ {result.template_name} ({warning_count} warnings, {info_count} info)")
                
                if result.warnings:
                    for warning in result.warnings:
                        print(f"   ⚠️  {warning.get('message', 'No message')}")
        print()
    
    # Summary
    print(f"{'='*70}")
    if invalid == 0:
        print("✅ All templates passed validation!")
    else:
        print(f"❌ {invalid} template(s) failed validation. Fix errors above.")
    print(f"{'='*70}\n")


def main():
    """Main entry point for CLI"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate CORTEX response templates against meta-template rules"
    )
    parser.add_argument(
        '--file',
        default='cortex-brain/response-templates.yaml',
        help='Path to templates file (default: cortex-brain/response-templates.yaml)'
    )
    parser.add_argument(
        '--template',
        help='Validate specific template only'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Show detailed validation info including warnings'
    )
    parser.add_argument(
        '--meta-template',
        default='cortex-brain/templates/meta-template.yaml',
        help='Path to meta-template file'
    )
    
    args = parser.parse_args()
    
    try:
        validator = TemplateValidator(args.meta_template)
        results = validator.validate_file(args.file, args.template)
        print_validation_results(results, args.verbose)
        
        # Exit with error code if any templates invalid
        invalid_count = sum(1 for r in results if not r.valid)
        sys.exit(1 if invalid_count > 0 else 0)
        
    except Exception as e:
        print(f"❌ Validation failed: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
