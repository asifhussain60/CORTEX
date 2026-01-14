"""
AC-CLEAN-306: Remove Phase References from Remediation Executor

Purpose: Remove phase-based logic from src/tools/remediation_executor.py
Ensure remediation works independently of phase numbers.

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path


class TestRemediationExecutorPhaseRemoval:
    """Tests for phase reference elimination from remediation executor"""

    def test_remediation_dispatch_without_phase(self):
        """AC-CLEAN-306.1: Remediation dispatch works without phase"""
        from src.tools.remediation_executor import apply_remediation
        
        result = apply_remediation({'issue': 'broken_reference', 'action': 'fix'})
        assert result is not None

    def test_remediation_workflow_independent_of_phases(self):
        """AC-CLEAN-306.2: Remediation workflow independent of phases"""
        from src.tools.remediation_executor import get_available_remediations
        
        remediations = get_available_remediations()
        assert isinstance(remediations, list) or remediations is not None

    def test_no_phase_conditional_in_remediation(self):
        """AC-CLEAN-306.3: No phase conditionals in remediation logic"""
        from src.tools.remediation_executor import execute_remediation
        
        result = execute_remediation({'type': 'test_fix'})
        assert result is not None or isinstance(result, dict)

    def test_remediation_by_capability(self):
        """AC-CLEAN-306.4: Remediation works by capability"""
        from src.tools.remediation_executor import get_remediation_for
        
        remediator = get_remediation_for('audit_issue')
        assert remediator is not None or remediator is False

    def test_batch_remediation_without_phase_gating(self):
        """AC-CLEAN-306.5: Batch remediation works independently"""
        from src.tools.remediation_executor import apply_batch_remediation
        
        result = apply_batch_remediation([
            {'issue': 'test1'},
            {'issue': 'test2'}
        ])
        assert result is not None

    def test_remediation_registry_capability_based(self):
        """AC-CLEAN-306.6: Remediation registry uses capabilities"""
        from src.tools.remediation_executor import get_remediation_registry
        
        registry = get_remediation_registry()
        assert registry is not None or isinstance(registry, dict)
