"""
Enhanced Planning Orchestrator - Comprehensive Test Suite

Tests for the EnhancedPlanningOrchestrator that:
- Loads phase templates from YAML
- Implements LENS classification
- Manages phase state machine
- Provides topological sorting
- Tracks progress and audit trail

Authority: AC-DOMAIN-PLAN-001-012
Author: GitHub Copilot (TDD Orchestrator)
Date: 2026-01-29
"""

import threading
import pytest
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import MagicMock, Mock, patch


class TestPlanningOrchestratorInitialization:
    """Tests for orchestrator initialization."""
    
    def test_singleton_initialization(self):
        """Test singleton pattern initialization."""
        from cortex.orchestrators.domain.enhanced_planning_orchestrator import (
            EnhancedPlanningOrchestrator,
        )
        
        # Get instance
        instance1 = EnhancedPlanningOrchestrator.instance()
        assert instance1 is not None
        
        # Second instantiation should return same instance
        instance2 = EnhancedPlanningOrchestrator.instance()
        assert instance1 is instance2
    
    def test_initialization_sets_defaults(self):
        """Test that initialization sets default values."""
        from cortex.orchestrators.domain.enhanced_planning_orchestrator import (
            EnhancedPlanningOrchestrator,
        )
        
        orchestrator = EnhancedPlanningOrchestrator.instance()
        
        assert orchestrator._version == "3.0.0"
        assert orchestrator._name == "EnhancedPlanningOrchestrator"
        assert isinstance(orchestrator._phase_templates, dict)
        assert isinstance(orchestrator._audit_trail, list)
    
    def test_initialization_creates_registry_loader(self):
        """Test that initialization creates phase templates."""
        from cortex.orchestrators.domain.enhanced_planning_orchestrator import (
            EnhancedPlanningOrchestrator,
        )
        
        orchestrator = EnhancedPlanningOrchestrator.instance()
        
        # Should have phase_templates dict
        assert hasattr(orchestrator, '_phase_templates')
        assert isinstance(orchestrator._phase_templates, dict)
    
    def test_thread_safety_singleton(self):
        """Test singleton thread safety."""
        from cortex.orchestrators.domain.enhanced_planning_orchestrator import (
            EnhancedPlanningOrchestrator,
        )
        
        instances = []
        
        def get_instance():
            instances.append(EnhancedPlanningOrchestrator.instance())
        
        threads = [threading.Thread(target=get_instance) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        # All instances should be the same object
        assert all(inst is instances[0] for inst in instances)


class TestPhaseStateManagement:
    """Tests for phase state machine (AC-DOMAIN-PLAN-006)."""
    
    def test_phase_states_initialized(self):
        """Test that phase states dict is initialized."""
        from cortex.orchestrators.domain.enhanced_planning_orchestrator import (
            EnhancedPlanningOrchestrator,
        )
        
        orchestrator = EnhancedPlanningOrchestrator.instance()
        
        assert hasattr(orchestrator, '_phase_states')
        assert isinstance(orchestrator._phase_states, dict)
    
    def test_phase_state_enum_exists(self):
        """Test PhaseState enum exists with required values."""
        from cortex.orchestrators.domain.enhanced_planning_orchestrator import (
            PhaseState,
        )
        
        # Verify all 10+ states exist
        assert PhaseState.DRAFT is not None
        assert PhaseState.PENDING_APPROVAL is not None
        assert PhaseState.APPROVED is not None
        assert PhaseState.EXECUTING is not None
        assert PhaseState.COMPLETED is not None
        assert PhaseState.FAILED is not None


class TestProgressTracking:
    """Tests for progress tracking (AC-DOMAIN-PLAN-008)."""
    
    def test_progress_tracking_initialized(self):
        """Test that progress tracking is initialized."""
        from cortex.orchestrators.domain.enhanced_planning_orchestrator import (
            EnhancedPlanningOrchestrator,
        )
        
        orchestrator = EnhancedPlanningOrchestrator.instance()
        
        assert hasattr(orchestrator, '_phase_progress')
        assert isinstance(orchestrator._phase_progress, dict)
    
    def test_audit_trail_initialized(self):
        """Test that audit trail is initialized."""
        from cortex.orchestrators.domain.enhanced_planning_orchestrator import (
            EnhancedPlanningOrchestrator,
        )
        
        orchestrator = EnhancedPlanningOrchestrator.instance()
        
        assert hasattr(orchestrator, '_audit_trail')
        assert isinstance(orchestrator._audit_trail, list)


class TestResourceConstraints:
    """Tests for resource constraint modeling (AC-DOMAIN-PLAN-011)."""
    
    def test_resource_constraints_initialized(self):
        """Test that resource constraints are initialized."""
        from cortex.orchestrators.domain.enhanced_planning_orchestrator import (
            EnhancedPlanningOrchestrator,
        )
        
        orchestrator = EnhancedPlanningOrchestrator.instance()
        
        assert hasattr(orchestrator, '_resource_constraints')
        assert isinstance(orchestrator._resource_constraints, dict)
    
    def test_resource_type_enum_exists(self):
        """Test ResourceType enum exists."""
        from cortex.orchestrators.domain.enhanced_planning_orchestrator import (
            ResourceType,
        )
        
        assert ResourceType.CPU is not None
        assert ResourceType.MEMORY is not None
        assert ResourceType.DISK is not None


class TestRiskAssessment:
    """Tests for risk assessment matrix (AC-DOMAIN-PLAN-012)."""
    
    def test_risk_assessments_initialized(self):
        """Test that risk assessments are initialized."""
        from cortex.orchestrators.domain.enhanced_planning_orchestrator import (
            EnhancedPlanningOrchestrator,
        )
        
        orchestrator = EnhancedPlanningOrchestrator.instance()
        
        assert hasattr(orchestrator, '_risk_assessments')
        assert isinstance(orchestrator._risk_assessments, dict)
    
    def test_risk_level_enum_exists(self):
        """Test RiskLevel enum exists."""
        from cortex.orchestrators.domain.enhanced_planning_orchestrator import (
            RiskLevel,
        )
        
        assert RiskLevel.LOW is not None
        assert RiskLevel.MEDIUM is not None
        assert RiskLevel.HIGH is not None
        assert RiskLevel.CRITICAL is not None


class TestParallelExecution:
    """Tests for parallel execution (AC-DOMAIN-PLAN-010)."""
    
    def test_executor_initialized(self):
        """Test that ThreadPoolExecutor is initialized."""
        from cortex.orchestrators.domain.enhanced_planning_orchestrator import (
            EnhancedPlanningOrchestrator,
        )
        
        orchestrator = EnhancedPlanningOrchestrator.instance()
        
        assert hasattr(orchestrator, '_executor')
        assert orchestrator._executor is not None


class TestOrchestratorInterface:
    """Tests for IOrchestrator interface implementation."""
    
    def test_implements_i_orchestrator(self):
        """Test that EnhancedPlanningOrchestrator implements IOrchestrator."""
        from cortex.orchestrators.domain.enhanced_planning_orchestrator import (
            EnhancedPlanningOrchestrator,
        )
        from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator
        
        orchestrator = EnhancedPlanningOrchestrator.instance()
        
        assert isinstance(orchestrator, IOrchestrator)
    
    def test_has_name_property(self):
        """Test that orchestrator has name property."""
        from cortex.orchestrators.domain.enhanced_planning_orchestrator import (
            EnhancedPlanningOrchestrator,
        )
        
        orchestrator = EnhancedPlanningOrchestrator.instance()
        
        assert orchestrator._name == "EnhancedPlanningOrchestrator"
    
    def test_has_version_property(self):
        """Test that orchestrator has version property."""
        from cortex.orchestrators.domain.enhanced_planning_orchestrator import (
            EnhancedPlanningOrchestrator,
        )
        
        orchestrator = EnhancedPlanningOrchestrator.instance()
        
        assert orchestrator._version == "3.0.0"
