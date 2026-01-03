"""
Response Validator - Single Action Rule Enforcement

Validates orchestrator responses against architectural principles:
- Single Action Rule: One next step only, never multiple options
- Concise Executive Format: Outcome-focused, no unrequested code

Part of Response Architecture v4.0.4 enhancement.

Author: Asif Hussain
Copyright © 2026 Asif Hussain. All rights reserved.
"""

import re
import logging
from dataclasses import dataclass
from typing import Dict, Any, List, Optional
from enum import Enum
from pathlib import Path

import yaml


class ViolationType(Enum):
    """Types of response violations."""
    MULTIPLE_OPTIONS = "multiple_options"
    UNREQUESTED_CODE = "unrequested_code"
    EXCESSIVE_DETAIL = "excessive_detail"


@dataclass
class ValidationViolation:
    """A single validation violation."""
    violation_type: ViolationType
    severity: str  # "error" or "warning"
    message: str
    context: str  # Text excerpt showing violation
    suggested_fix: Optional[str] = None


@dataclass
class ValidationResult:
    """Result of response validation."""
    valid: bool
    violations: List[ValidationViolation]
    response_text: str
    
    @property
    def has_errors(self) -> bool:
        """Check if any violations are errors."""
        return any(v.severity == "error" for v in self.violations)
    
    @property
    def has_warnings(self) -> bool:
        """Check if any violations are warnings."""
        return any(v.severity == "warning" for v in self.violations)


class ResponseValidator:
    """
    Validates orchestrator responses against Single Action Rule.
    
    Enforcement Levels:
    1. ERROR: Multiple options detected → response rejected
    2. WARNING: Unrequested code/details → flagged for revision
    
    Usage:
        validator = ResponseValidator(cortex_root='/path/to/CORTEX')
        result = validator.validate_response(response_text)
        
        if not result.valid:
            print(f"Validation failed: {result.violations}")
    """
    
    def __init__(self, cortex_root: str = None):
        """
        Initialize response validator.
        
        Args:
            cortex_root: CORTEX root directory (defaults to current workspace)
        """
        self.cortex_root = Path(cortex_root) if cortex_root else Path.cwd()
        self.logger = logging.getLogger("cortex.response_validator")
        
        # Load validation patterns from response-templates-v4.yaml
        self.patterns = self._load_validation_patterns()
        
        self.logger.info("ResponseValidator initialized with Single Action Rule enforcement")
    
    def _load_validation_patterns(self) -> Dict[str, Any]:
        """
        Load validation patterns from response-templates-v4.yaml.
        
        Returns:
            Dict with validation patterns from architectural_principles section
        """
        templates_path = (
            self.cortex_root / "cortex-brain" / "response-templates-v4.yaml"
        )
        
        if not templates_path.exists():
            self.logger.warning(
                f"response-templates-v4.yaml not found at {templates_path}"
            )
            return self._get_default_patterns()
        
        try:
            with open(templates_path, 'r', encoding='utf-8') as f:
                templates_data = yaml.safe_load(f)
            
            # Extract architectural_principles.single_action_rule patterns
            arch_principles = templates_data.get('architectural_principles', {})
            single_action_rule = arch_principles.get('single_action_rule', {})
            
            return {
                'multiple_options_pattern': single_action_rule.get(
                    'validation', {}
                ).get('pattern', r'\b(or|either|option|choose)\b.*\b(or|either|option)\b'),
                'valid_single_action_pattern': r'^\*\*Next:\*\*.*\(.*\)|^Say [\'\"]|^✅',
                'code_block_pattern': r'```[a-z]+\n.*?\n```',
                'forbidden_phrases': [
                    'to continue:',
                    'you can either',
                    'option 1:',
                    'option 2:',
                    'choose',
                    'or say',
                    'alternatively'
                ]
            }
            
        except Exception as e:
            self.logger.error(
                f"Failed to load validation patterns: {e}",
                exc_info=True
            )
            return self._get_default_patterns()
    
    def _get_default_patterns(self) -> Dict[str, Any]:
        """Get default validation patterns if loading fails."""
        return {
            'multiple_options_pattern': r'\b(or|either|option|choose)\b.*\b(or|either|option)\b',
            'valid_single_action_pattern': r'^\*\*Next:\*\*.*\(.*\)|^Say [\'\"]|^✅',
            'code_block_pattern': r'```[a-z]+\n.*?\n```',
            'forbidden_phrases': [
                'to continue:',
                'you can either',
                'option 1:',
                'option 2:',
                'choose',
                'or say',
                'alternatively'
            ]
        }
    
    def validate_response(
        self,
        response_text: str,
        user_request: Optional[str] = None
    ) -> ValidationResult:
        """
        Validate response against Single Action Rule.
        
        Args:
            response_text: Orchestrator response text
            user_request: Optional user request for context analysis
        
        Returns:
            ValidationResult with violations (if any)
        """
        violations = []
        
        # Extract next steps section
        next_steps = self._extract_next_steps(response_text)
        
        if next_steps:
            # Check for multiple options (ERROR level)
            multiple_options_violations = self._check_multiple_options(next_steps)
            violations.extend(multiple_options_violations)
        
        # Check for unrequested code (WARNING level)
        if user_request and not self._user_requested_code(user_request):
            code_violations = self._check_unrequested_code(response_text)
            violations.extend(code_violations)
        
        # Valid if no ERROR-level violations
        valid = not any(v.severity == "error" for v in violations)
        
        return ValidationResult(
            valid=valid,
            violations=violations,
            response_text=response_text
        )
    
    def _extract_next_steps(self, response_text: str) -> Optional[str]:
        """
        Extract next steps section from response.
        
        Args:
            response_text: Full response text
        
        Returns:
            Next steps section text or None
        """
        # Look for common next steps markers
        patterns = [
            r'\*\*Next:\*\*.*',
            r'## Next Steps.*?(?=##|\Z)',
            r'### Next Steps.*?(?=##|\Z)',
            r'To continue:.*?(?=\n\n|\Z)',
            r'Say [\'\"].*?[\'\"].*?(?=\n|\Z)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, response_text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(0)
        
        return None
    
    def _check_multiple_options(self, next_steps: str) -> List[ValidationViolation]:
        """
        Check for multiple option violations (SINGLE ACTION RULE).
        
        Args:
            next_steps: Next steps section text
        
        Returns:
            List of violations (ERROR level)
        """
        violations = []
        
        # Check forbidden phrases
        next_steps_lower = next_steps.lower()
        for phrase in self.patterns['forbidden_phrases']:
            if phrase in next_steps_lower:
                violations.append(ValidationViolation(
                    violation_type=ViolationType.MULTIPLE_OPTIONS,
                    severity="error",
                    message=f"SINGLE ACTION RULE violation: Forbidden phrase '{phrase}' detected",
                    context=self._extract_context(next_steps, phrase, 100),
                    suggested_fix=(
                        "Select ONE optimal next step and format as: "
                        "**Next:** [action] ([value/benefit])"
                    )
                ))
        
        # Check regex pattern for multiple options
        pattern = self.patterns['multiple_options_pattern']
        matches = re.finditer(pattern, next_steps, re.IGNORECASE)
        
        for match in matches:
            # Avoid false positives (e.g., "orchestrator" contains "or")
            matched_text = match.group(0)
            if self._is_genuine_multiple_options(matched_text):
                violations.append(ValidationViolation(
                    violation_type=ViolationType.MULTIPLE_OPTIONS,
                    severity="error",
                    message="SINGLE ACTION RULE violation: Multiple options detected in next steps",
                    context=self._extract_context(next_steps, matched_text, 100),
                    suggested_fix=(
                        "Provide EXACTLY ONE next step with justification. "
                        "Remove all alternative options."
                    )
                ))
        
        return violations
    
    def _is_genuine_multiple_options(self, text: str) -> bool:
        """
        Check if matched text is genuine multiple options (not false positive).
        
        Args:
            text: Matched text snippet
        
        Returns:
            True if genuine multiple options pattern
        """
        # False positive filters
        false_positives = [
            'orchestrator',
            'coordinator',
            'operator',
            'author',
            'collaborator'
        ]
        
        text_lower = text.lower()
        for fp in false_positives:
            if fp in text_lower:
                return False
        
        # Genuine if contains choice indicators
        choice_indicators = ['option', 'either', 'choose', 'select']
        return any(indicator in text_lower for indicator in choice_indicators)
    
    def _check_unrequested_code(self, response_text: str) -> List[ValidationViolation]:
        """
        Check for unrequested code blocks (CONCISE EXECUTIVE FORMAT).
        
        Args:
            response_text: Full response text
        
        Returns:
            List of violations (WARNING level)
        """
        violations = []
        
        # Find code blocks
        pattern = self.patterns['code_block_pattern']
        matches = list(re.finditer(pattern, response_text, re.DOTALL))
        
        if matches:
            violations.append(ValidationViolation(
                violation_type=ViolationType.UNREQUESTED_CODE,
                severity="warning",
                message=(
                    f"CONCISE EXECUTIVE FORMAT: {len(matches)} code block(s) found "
                    f"without user requesting code"
                ),
                context=f"Found {len(matches)} code blocks (```...```)",
                suggested_fix=(
                    "Remove code blocks or replace with high-level summary. "
                    "Users will request code if needed."
                )
            ))
        
        return violations
    
    def _user_requested_code(self, user_request: str) -> bool:
        """
        Check if user explicitly requested code.
        
        Args:
            user_request: User's request text
        
        Returns:
            True if user requested code/implementation details
        """
        code_request_patterns = [
            r'show\s+(me\s+)?(the\s+)?code',
            r'write\s+(the\s+)?code',
            r'implement',
            r'code\s+for',
            r'example\s+code',
            r'code\s+snippet',
            r'how\s+to\s+code'
        ]
        
        user_request_lower = user_request.lower()
        return any(
            re.search(pattern, user_request_lower)
            for pattern in code_request_patterns
        )
    
    def _extract_context(
        self,
        text: str,
        target: str,
        context_length: int = 100
    ) -> str:
        """
        Extract context around target text.
        
        Args:
            text: Full text
            target: Target substring
            context_length: Characters before/after target
        
        Returns:
            Context excerpt
        """
        try:
            idx = text.lower().find(target.lower())
            if idx == -1:
                return text[:context_length]
            
            start = max(0, idx - context_length // 2)
            end = min(len(text), idx + len(target) + context_length // 2)
            
            excerpt = text[start:end]
            if start > 0:
                excerpt = "..." + excerpt
            if end < len(text):
                excerpt = excerpt + "..."
            
            return excerpt
            
        except Exception:
            return text[:context_length]
    
    def format_violation_report(self, result: ValidationResult) -> str:
        """
        Format validation result as human-readable report.
        
        Args:
            result: ValidationResult to format
        
        Returns:
            Formatted report string
        """
        if result.valid:
            return "✅ Response validation passed"
        
        report_lines = [
            "❌ Response Validation Failed",
            "=" * 50,
            ""
        ]
        
        # Group by severity
        errors = [v for v in result.violations if v.severity == "error"]
        warnings = [v for v in result.violations if v.severity == "warning"]
        
        if errors:
            report_lines.append(f"ERRORS ({len(errors)}):")
            for i, violation in enumerate(errors, 1):
                report_lines.extend([
                    f"\n{i}. {violation.message}",
                    f"   Type: {violation.violation_type.value}",
                    f"   Context: {violation.context}",
                    f"   Fix: {violation.suggested_fix}"
                ])
        
        if warnings:
            report_lines.append(f"\nWARNINGS ({len(warnings)}):")
            for i, violation in enumerate(warnings, 1):
                report_lines.extend([
                    f"\n{i}. {violation.message}",
                    f"   Context: {violation.context}",
                    f"   Fix: {violation.suggested_fix}"
                ])
        
        return "\n".join(report_lines)


# CLI Interface for Testing
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python response_validator.py <response_file>")
        sys.exit(1)
    
    response_file = Path(sys.argv[1])
    if not response_file.exists():
        print(f"Error: File not found: {response_file}")
        sys.exit(1)
    
    response_text = response_file.read_text(encoding='utf-8')
    
    validator = ResponseValidator()
    result = validator.validate_response(response_text)
    
    print(validator.format_violation_report(result))
    
    sys.exit(0 if result.valid else 1)
