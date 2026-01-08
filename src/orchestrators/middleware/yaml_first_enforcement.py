"""
YAML-First Enforcement Middleware
==================================
Enforces that all plans must be created as YAML files before implementation.
Part of the intelligence layer to prevent premature implementation.

Author: GitHub Copilot (for CORTEX)
Created: 2026-01-08
Feature: feat04-core-orchestration
Task: 1.3
TDD Phase: GREEN
"""

import re
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from datetime import datetime

from ..audit_logger import get_audit_logger, AuditCategory, AuditLevel


# =============================================================================
# Data Classes
# =============================================================================

@dataclass
class EnforcementResult:
    """Result of YAML-first enforcement check"""
    violation_detected: bool
    violation_type: Optional[str] = None
    message: str = ""
    guidance: Optional[str] = None
    allowed: bool = True
    audit_logged: bool = False
    correlation_id: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def valid(self) -> bool:
        """Alias for allowed"""
        return self.allowed


class YAMLFirstViolation(Exception):
    """Raised when YAML-first rule is violated"""
    
    def __init__(
        self,
        message: str,
        guidance: Optional[str] = None,
        request: Optional[str] = None,
        suggested_plan_path: Optional[Path] = None
    ):
        super().__init__(message)
        self.message = message
        self.guidance = guidance
        self.request = request
        self.suggested_plan_path = suggested_plan_path


# =============================================================================
# YAML-First Enforcer
# =============================================================================

class YAMLFirstEnforcer:
    """Enforces YAML-first planning approach"""
    
    # Implementation keywords that trigger enforcement
    IMPLEMENTATION_KEYWORDS = [
        r'\bimplement\b',
        r'\bbuild\b',
        r'\bcreate\s+(?:the\s+)?(?:class|function|module|component)',
        r'\bwrite\s+(?:the\s+)?(?:code|function|class)',
        r'\bcode\s+(?:the|a)\b',
        r'\bdevelop\b',
        r'\bconstruct\b'
    ]
    
    # Planning keywords that indicate plan creation (allowed)
    PLANNING_KEYWORDS = [
        r'\bcreate\s+(?:a\s+)?plan\b',
        r'\bmake\s+(?:a\s+)?plan\b',
        r'\bplan\s+for\b',
        r'\bdesign\s+(?:a\s+)?plan\b',
        r'\bgenerate\s+(?:a\s+)?plan\b'
    ]
    
    # Required YAML plan structure fields
    REQUIRED_PLAN_FIELDS = [
        'feature',
        'phases'
    ]
    
    def __init__(self, planning_root: Optional[Path] = None):
        """
        Initialize enforcer
        
        Args:
            planning_root: Root directory for plan files
        """
        self.planning_root = planning_root or Path.cwd() / "cortex-brain" / "documents" / "planning"
        self.logger = get_audit_logger()
        
        # Compile regex patterns
        self.implementation_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.IMPLEMENTATION_KEYWORDS
        ]
        self.planning_patterns = [
            re.compile(pattern, re.IGNORECASE)
            for pattern in self.PLANNING_KEYWORDS
        ]
    
    def check_request(
        self,
        request: str,
        plan_file: Optional[Path] = None
    ) -> EnforcementResult:
        """
        Check if request violates YAML-first rule
        
        Args:
            request: User request to check
            plan_file: Optional path to YAML plan file
            
        Returns:
            EnforcementResult with violation status
        """
        correlation_id = f"YAML-FIRST-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        
        # Check if this is a planning request (always allowed)
        if self._is_planning_request(request):
            self.logger.info(
                category=AuditCategory.VALIDATION,
                component='yaml_first_enforcement',
                operation='check_request',
                message='Planning request detected - allowed',
                context={'request': request[:100]},
                correlation_id=correlation_id
            )
            return EnforcementResult(
                violation_detected=False,
                message="Planning request allowed",
                allowed=True,
                audit_logged=True,
                correlation_id=correlation_id
            )
        
        # Check if this is an implementation request
        is_implementation = self._is_implementation_request(request)
        
        if not is_implementation:
            # Not an implementation request, allow
            return EnforcementResult(
                violation_detected=False,
                message="Not an implementation request",
                allowed=True
            )
        
        # Implementation request detected - check for YAML
        if plan_file and plan_file.exists():
            # YAML exists, validate it
            validation = self.validate_yaml_structure(plan_file)
            
            if validation.valid:
                self.logger.info(
                    category=AuditCategory.VALIDATION,
                    component='yaml_first_enforcement',
                    operation='check_request',
                    message='Implementation allowed - valid YAML plan exists',
                    context={
                        'request': request[:100],
                        'plan_file': str(plan_file)
                    },
                    correlation_id=correlation_id
                )
                return EnforcementResult(
                    violation_detected=False,
                    message="Valid YAML plan exists",
                    allowed=True,
                    audit_logged=True,
                    correlation_id=correlation_id
                )
            else:
                # YAML exists but invalid
                self.logger.warning(
                    category=AuditCategory.VALIDATION,
                    component='yaml_first_enforcement',
                    operation='check_request',
                    message='YAML plan exists but invalid',
                    context={
                        'request': request[:100],
                        'plan_file': str(plan_file),
                        'validation_error': validation.message
                    },
                    correlation_id=correlation_id
                )
                return EnforcementResult(
                    violation_detected=True,
                    violation_type="invalid_yaml",
                    message=f"YAML plan invalid: {validation.message}",
                    guidance=self.get_yaml_guidance(),
                    allowed=False,
                    audit_logged=True,
                    correlation_id=correlation_id
                )
        
        # No YAML plan found - violation
        guidance = self.get_yaml_guidance()
        
        self.logger.warning(
            category=AuditCategory.VALIDATION,
            component='yaml_first_enforcement',
            operation='check_request',
            message='YAML-first violation: Implementation without YAML plan',
            context={'request': request[:100]},
            correlation_id=correlation_id
        )
        
        return EnforcementResult(
            violation_detected=True,
            violation_type="missing_yaml",
            message="YAML plan required before implementation",
            guidance=guidance,
            allowed=False,
            audit_logged=True,
            correlation_id=correlation_id
        )
    
    def enforce(
        self,
        request: str,
        plan_file: Optional[Path] = None
    ) -> EnforcementResult:
        """
        Enforce YAML-first rule, raising exception on violation
        
        Args:
            request: User request
            plan_file: Optional path to YAML plan
            
        Returns:
            EnforcementResult if allowed
            
        Raises:
            YAMLFirstViolation: If rule violated
        """
        result = self.check_request(request, plan_file)
        
        if result.violation_detected:
            raise YAMLFirstViolation(
                message=result.message,
                guidance=result.guidance,
                request=request,
                suggested_plan_path=self._suggest_plan_path(request)
            )
        
        return result
    
    def validate_yaml_exists(self, plan_file: Path) -> EnforcementResult:
        """
        Validate YAML file exists
        
        Args:
            plan_file: Path to YAML file
            
        Returns:
            EnforcementResult with validation status
        """
        if not plan_file.exists():
            return EnforcementResult(
                violation_detected=True,
                violation_type="file_not_found",
                message=f"YAML plan not found: {plan_file}",
                allowed=False
            )
        
        return EnforcementResult(
            violation_detected=False,
            message="YAML file exists",
            allowed=True
        )
    
    def validate_yaml_format(self, plan_file: Path) -> EnforcementResult:
        """
        Validate YAML is properly formatted
        
        Args:
            plan_file: Path to YAML file
            
        Returns:
            EnforcementResult with validation status
        """
        try:
            with open(plan_file, 'r') as f:
                yaml.safe_load(f)
            
            return EnforcementResult(
                violation_detected=False,
                message="YAML format valid",
                allowed=True
            )
        except yaml.YAMLError as e:
            return EnforcementResult(
                violation_detected=True,
                violation_type="invalid_format",
                message=f"Invalid YAML format: {str(e)}",
                allowed=False
            )
    
    def validate_yaml_structure(self, plan_file: Path) -> EnforcementResult:
        """
        Validate YAML has required plan structure
        
        Args:
            plan_file: Path to YAML file
            
        Returns:
            EnforcementResult with validation status
        """
        # First check format
        format_result = self.validate_yaml_format(plan_file)
        if not format_result.valid:
            return format_result
        
        # Load and check structure
        try:
            with open(plan_file, 'r') as f:
                data = yaml.safe_load(f)
            
            if not isinstance(data, dict):
                return EnforcementResult(
                    violation_detected=True,
                    violation_type="invalid_structure",
                    message="YAML must be a dictionary",
                    allowed=False
                )
            
            # Check for required fields (support both flat and nested structure)
            missing_fields = []
            
            # Check for 'feature' field
            if 'feature' not in data:
                missing_fields.append('feature')
            
            # Check for 'phases' - can be top-level or nested under 'feature'
            has_phases = False
            if 'phases' in data:
                has_phases = True
            elif 'feature' in data and isinstance(data['feature'], dict):
                if 'phases' in data['feature']:
                    has_phases = True
            
            if not has_phases:
                missing_fields.append('phases')
            
            if missing_fields:
                return EnforcementResult(
                    violation_detected=True,
                    violation_type="missing_required_fields",
                    message=f"YAML missing required fields: {', '.join(missing_fields)}",
                    allowed=False
                )
            
            return EnforcementResult(
                violation_detected=False,
                message="YAML structure valid",
                allowed=True
            )
            
        except Exception as e:
            return EnforcementResult(
                violation_detected=True,
                violation_type="validation_error",
                message=f"YAML validation error: {str(e)}",
                allowed=False
            )
    
    def get_yaml_guidance(self) -> str:
        """
        Get guidance on creating YAML plans
        
        Returns:
            Guidance text with example structure
        """
        return """
YAML Plan Required
==================

Before implementing, create a YAML plan using:

    cortex plan "create a plan for [feature]"

Or manually create a YAML file with this structure:

```yaml
feature:
  id: feature-name
  name: Feature Name
  description: |
    Feature description
    
  phases:
    - id: 1
      name: Phase 1 Name
      estimated_hours: 10
      
      tasks:
        - id: 1.1
          name: Task 1
          description: Task description
          estimated_minutes: 60
          dependencies: []
          
        - id: 1.2
          name: Task 2
          dependencies: ["1.1"]
```

This ensures:
- Clear requirements before coding
- Proper task sequencing
- Dependency management
- Progress tracking
- Audit trail
"""
    
    def _is_planning_request(self, request: str) -> bool:
        """Check if request is for creating a plan"""
        return any(
            pattern.search(request)
            for pattern in self.planning_patterns
        )
    
    def _is_implementation_request(self, request: str) -> bool:
        """Check if request is for implementation"""
        return any(
            pattern.search(request)
            for pattern in self.implementation_patterns
        )
    
    def _suggest_plan_path(self, request: str) -> Path:
        """Suggest a plan file path based on request"""
        # Extract feature name from request
        feature_name = re.sub(r'[^a-z0-9]+', '-', request.lower())[:50]
        feature_name = feature_name.strip('-')
        
        return self.planning_root / "active" / f"{feature_name}-plan.yaml"
