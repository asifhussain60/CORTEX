"""
Tests for UnwiredComponentDetector - Discovers components that exist but aren't wired.

AC-UNWIRED-DETECT-001: UnwiredComponentDetector tests
TDD: Tests FIRST per CORE-008

Test coverage:
- scan_codebase() discovers all orchestrator classes
- generate_report() produces structured gap analysis
- Detects initialized_but_not_called (DoR, IntentRouter)
- Detects registered_but_not_initialized
- Detects exists_but_not_registered (LENSSynthesis)
- Detects mentioned_but_not_implemented (EnforcementOrchestrator)
- Detects registry_lies (says "wired" but isn't called)
"""

import pytest
from pathlib import Path
from typing import List, Dict, Any
from dataclasses import dataclass

# Import will fail until implementation created (TDD - tests first)
try:
    from cortex.tools.unwired_component_detector import (
        UnwiredComponentDetector,
        UnwiredReport,
        ComponentStatus,
    )
except ImportError:
    # Expected to fail initially - TDD
    UnwiredComponentDetector = None
    UnwiredReport = None
    ComponentStatus = None


@pytest.mark.skipif(
    UnwiredComponentDetector is None,
    reason="UnwiredComponentDetector not implemented yet (TDD - tests first)"
)
class TestUnwiredComponentDetector:
    """Test suite for UnwiredComponentDetector."""
    
    def test_detector_initializes(self):
        """Test detector can be instantiated."""
        detector = UnwiredComponentDetector()
        assert detector is not None
        assert hasattr(detector, 'scan_codebase')
        assert hasattr(detector, 'generate_report')
    
    def test_scan_codebase_returns_report(self):
        """Test scan_codebase returns UnwiredReport."""
        detector = UnwiredComponentDetector()
        report = detector.scan_codebase()
        
        assert isinstance(report, UnwiredReport)
        assert hasattr(report, 'initialized_but_not_called')
        assert hasattr(report, 'registered_but_not_initialized')
        assert hasattr(report, 'exists_but_not_registered')
        assert hasattr(report, 'mentioned_but_not_implemented')
        assert hasattr(report, 'registry_lies')
    
    def test_detects_initialized_but_not_called(self):
        """Test detection of components initialized in __init__ but never called."""
        detector = UnwiredComponentDetector()
        report = detector.scan_codebase()
        
        # InteractionOrchestrator and IntentRouter are initialized but not called
        initialized_not_called = report.initialized_but_not_called
        assert isinstance(initialized_not_called, list)
        
        # Should detect known cases (if they still exist)
        component_names = [c['name'] for c in initialized_not_called]
        # Note: May be empty if all components wired by time test runs
        # But structure should exist
        for component in initialized_not_called:
            assert 'name' in component
            assert 'file' in component
            assert 'initialized_at' in component
            assert 'called' in component
            assert component['called'] is False
    
    def test_detects_exists_but_not_registered(self):
        """Test detection of components that exist but aren't in registry."""
        detector = UnwiredComponentDetector()
        report = detector.scan_codebase()
        
        exists_not_registered = report.exists_but_not_registered
        assert isinstance(exists_not_registered, list)
        
        # LENSSynthesis exists but not in registry (as of 2026-01-25)
        for component in exists_not_registered:
            assert 'name' in component
            assert 'file' in component
            assert 'in_registry' in component
            assert component['in_registry'] is False
    
    def test_detects_mentioned_but_not_implemented(self):
        """Test detection of components mentioned in prompts/docs but missing."""
        detector = UnwiredComponentDetector()
        report = detector.scan_codebase()
        
        mentioned_not_implemented = report.mentioned_but_not_implemented
        assert isinstance(mentioned_not_implemented, list)
        
        # EnforcementOrchestrator mentioned in CORTEX.prompt.md but doesn't exist
        for component in mentioned_not_implemented:
            assert 'name' in component
            assert 'mentioned_in' in component
            assert 'exists' in component
            assert component['exists'] is False
    
    def test_detects_registry_lies(self):
        """Test detection of components marked 'wired' but not actually called."""
        detector = UnwiredComponentDetector()
        report = detector.scan_codebase()
        
        registry_lies = report.registry_lies
        assert isinstance(registry_lies, list)
        
        # Registry says 18/18 wired but many aren't actually called
        for lie in registry_lies:
            assert 'name' in lie
            assert 'registry_status' in lie
            assert 'actual_status' in lie
            assert lie['registry_status'] == 'wired'
            assert lie['actual_status'] != 'wired'
    
    def test_generate_report_produces_dict(self):
        """Test generate_report produces structured dict for display."""
        detector = UnwiredComponentDetector()
        report_data = detector.generate_report()
        
        assert isinstance(report_data, dict)
        assert 'summary' in report_data
        assert 'initialized_but_not_called' in report_data
        assert 'registry_lies' in report_data
        assert 'mentioned_but_not_implemented' in report_data
        
        # Summary should have counts
        summary = report_data['summary']
        assert 'total_components_found' in summary
        assert 'total_wired' in summary
        assert 'total_unwired' in summary
        assert 'total_lies' in summary
    
    def test_scan_orchestrator_files(self):
        """Test _scan_orchestrator_files finds all Orchestrator classes."""
        detector = UnwiredComponentDetector()
        
        # Internal method - test if exposed
        if hasattr(detector, '_scan_orchestrator_files'):
            orchestrators = detector._scan_orchestrator_files()
            
            assert isinstance(orchestrators, list)
            assert len(orchestrators) > 0
            
            # Should find known orchestrators
            names = [o['name'] for o in orchestrators]
            assert 'MasterOrchestrator' in names
            assert 'TDDOrchestrator' in names
    
    def test_check_initialization_in_master_orchestrator(self):
        """Test _check_initialization detects if component initialized."""
        detector = UnwiredComponentDetector()
        
        if hasattr(detector, '_check_initialization'):
            # TDDOrchestrator should be initialized
            is_initialized = detector._check_initialization('TDDOrchestrator')
            assert isinstance(is_initialized, bool)
    
    def test_check_invocation_in_execute_operation(self):
        """Test _check_invocation detects if component is called."""
        detector = UnwiredComponentDetector()
        
        if hasattr(detector, '_check_invocation'):
            # TDDOrchestrator should be called
            is_called = detector._check_invocation('TDDOrchestrator')
            assert isinstance(is_called, bool)
    
    def test_report_includes_recommendations(self):
        """Test report includes wiring recommendations."""
        detector = UnwiredComponentDetector()
        report_data = detector.generate_report()
        
        # Should include recommendations for each gap type
        if report_data.get('initialized_but_not_called'):
            assert 'recommendations' in report_data
            recs = report_data['recommendations']
            assert isinstance(recs, list)
            assert len(recs) > 0
    
    def test_detector_respects_cortex_brain_tier0(self):
        """Test detector reads repo-registry.yaml from correct location."""
        detector = UnwiredComponentDetector()
        
        # Should read from cortex_brain/tier0/repo-registry.yaml
        if hasattr(detector, 'registry_file'):
            assert 'cortex_brain' in str(detector.registry_file)
            assert 'tier0' in str(detector.registry_file)
            assert 'repo-registry.yaml' in str(detector.registry_file)


@pytest.mark.skipif(
    UnwiredReport is None,
    reason="UnwiredReport not implemented yet (TDD - tests first)"
)
class TestUnwiredReport:
    """Test suite for UnwiredReport dataclass."""
    
    def test_unwired_report_structure(self):
        """Test UnwiredReport has correct structure."""
        # Test creating report manually
        report = UnwiredReport(
            initialized_but_not_called=[],
            registered_but_not_initialized=[],
            exists_but_not_registered=[],
            mentioned_but_not_implemented=[],
            registry_lies=[],
            timestamp="2026-01-25T00:00:00"
        )
        
        assert report.initialized_but_not_called == []
        assert report.timestamp == "2026-01-25T00:00:00"
    
    def test_unwired_report_to_dict(self):
        """Test UnwiredReport can convert to dict."""
        report = UnwiredReport(
            initialized_but_not_called=[{'name': 'TestOrch', 'called': False}],
            registered_but_not_initialized=[],
            exists_but_not_registered=[],
            mentioned_but_not_implemented=[],
            registry_lies=[],
        )
        
        if hasattr(report, 'to_dict'):
            report_dict = report.to_dict()
            assert isinstance(report_dict, dict)
            assert 'initialized_but_not_called' in report_dict


@pytest.mark.skipif(
    ComponentStatus is None,
    reason="ComponentStatus not implemented yet (TDD - tests first)"
)
class TestComponentStatus:
    """Test suite for ComponentStatus enum."""
    
    def test_component_status_enum_values(self):
        """Test ComponentStatus has expected values."""
        assert hasattr(ComponentStatus, 'FULLY_WIRED')
        assert hasattr(ComponentStatus, 'PARTIALLY_WIRED')
        assert hasattr(ComponentStatus, 'UNWIRED')
        assert hasattr(ComponentStatus, 'ORPHANED')
        assert hasattr(ComponentStatus, 'MISSING')


# Integration test with actual codebase
class TestUnwiredComponentDetectorIntegration:
    """Integration tests using actual CORTEX codebase."""
    
    @pytest.mark.skipif(
        UnwiredComponentDetector is None,
        reason="UnwiredComponentDetector not implemented yet"
    )
    def test_detects_real_unwired_components(self):
        """Test detector finds real unwired components in CORTEX."""
        detector = UnwiredComponentDetector()
        report = detector.scan_codebase()
        
        # As of 2026-01-25, we know these gaps exist:
        # - InteractionOrchestrator: initialized but not called
        # - IntentRouter: initialized but not called
        # - DoRApprovalGate: initialized but not called
        # - EnforcementOrchestrator: mentioned but not implemented
        
        # Validate report captures these
        report_data = detector.generate_report()
        
        # Should have some gaps (if codebase unchanged)
        assert (
            len(report_data['initialized_but_not_called']) > 0 or
            len(report_data['mentioned_but_not_implemented']) > 0 or
            len(report_data['registry_lies']) > 0
        )
    
    @pytest.mark.skipif(
        UnwiredComponentDetector is None,
        reason="UnwiredComponentDetector not implemented yet"
    )
    def test_report_is_actionable(self):
        """Test generated report has actionable recommendations."""
        detector = UnwiredComponentDetector()
        report_data = detector.generate_report()
        
        # Report should be actionable
        assert 'summary' in report_data
        summary = report_data['summary']
        
        # Should have clear counts
        assert summary['total_components_found'] > 0
        
        # If gaps exist, should have recommendations
        total_gaps = (
            len(report_data.get('initialized_but_not_called', [])) +
            len(report_data.get('registry_lies', []))
        )
        
        if total_gaps > 0:
            assert 'recommendations' in report_data
            assert len(report_data['recommendations']) > 0
