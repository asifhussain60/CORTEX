"""
CORTEX Policy System

Purpose: Policy document parsing, compliance validation, and enforcement.

Components:
- PolicyAnalyzer: Parse policy documents (PDF/MD/DOCX/TXT)
- ComplianceValidator: Validate code against policies (3-act WOW workflow)
- PolicyTestGenerator: Generate pytest tests from policies
- PolicyStorage: Per-repo policy tracking with change detection (Tier 3)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Repository: https://github.com/asifhussain60/CORTEX
"""

from .policy_analyzer import (
    PolicyAnalyzer,
    PolicyDocument,
    PolicyRule,
    PolicyLevel,
    PolicyCategory
)

from .compliance_validator import (
    ComplianceValidator,
    ComplianceReport,
    PolicyViolation,
    GapAnalysis,
    RemediationAction,
    ViolationSeverity
)

from .policy_test_generator import (
    PolicyTestGenerator
)

from .policy_storage import (
    PolicyStorage
)

__all__ = [
    # Analyzer
    'PolicyAnalyzer',
    'PolicyDocument',
    'PolicyRule',
    'PolicyLevel',
    'PolicyCategory',
    
    # Validator
    'ComplianceValidator',
    'ComplianceReport',
    'PolicyViolation',
    'GapAnalysis',
    'RemediationAction',
    'ViolationSeverity',
    
    # Test Generator
    'PolicyTestGenerator',
    
    # Storage
    'PolicyStorage',
]
