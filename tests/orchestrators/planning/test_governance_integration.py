"""
Tests for Phase -1 Knowledge Library - Governance Integration.

Comprehensive test suite validating governance consultation, knowledge graph
queries, and Phase -1 execution before Phase 0.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.orchestrators.planning.phases.phase_minus_one import (
    PhaseMinusOne,
    GovernanceConsultationResult,
    execute_phase_minus_one
)
from src.orchestrators.planning.governance_integrator import (
    GovernanceIntegrator,
    GovernanceValidation
)
from src.orchestrators.planning.knowledge_graph_query import (
    KnowledgeGraphQuery,
    KnowledgeContext
)


@pytest.fixture
def temp_output_dir(tmp_path):
    """Create temporary output directory for reports."""
    output_dir = tmp_path / "governance-consultations"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def mock_governance_integrator():
    """Mock GovernanceIntegrator."""
    mock_gov = MagicMock(spec=GovernanceIntegrator)
    mock_gov.validate_feature_request.return_value = GovernanceValidation(
        is_valid=True,
        violations=[],
        warnings=[],
        applied_rules=['TDD_ENFORCEMENT', 'HOLISTIC_DISCOVERY'],
        governance_context={'validated': True}
    )
    return mock_gov


@pytest.fixture
def mock_knowledge_query():
    """Mock KnowledgeGraphQuery."""
    mock_kg = MagicMock(spec=KnowledgeGraphQuery)
    mock_kg.get_feature_context.return_value = KnowledgeContext(
        related_features=['planning_v4', 'cleanup_v2'],
        dependencies=['base_orchestrator'],
        patterns=['TDD Pattern', 'Orchestrator Pattern'],
        risks=['Integration complexity'],
        recommendations=['Test before implement', 'Use established patterns']
    )
    return mock_kg


@pytest.fixture
def phase_minus_one(mock_governance_integrator, mock_knowledge_query, temp_output_dir):
    """Create PhaseMinusOne instance."""
    return PhaseMinusOne(
        governance_integrator=mock_governance_integrator,
        knowledge_query=mock_knowledge_query,
        output_dir=temp_output_dir
    )


class TestPhaseMinusOneExecution:
    """Test Phase -1 execution and integration."""
    
    def test_phase_minus_one_executes_successfully(self, phase_minus_one):
        """Test that Phase -1 executes without errors."""
        result = phase_minus_one.execute(
            feature_name='test-feature',
            user_request='plan test feature'
        )
        
        assert isinstance(result, GovernanceConsultationResult)
        assert result.success is True
        assert result.execution_time_seconds >= 0
    
    def test_phase_minus_one_executes_before_phase_zero(
        self, mock_governance_integrator, mock_knowledge_query, temp_output_dir
    ):
        """Test that Phase -1 is designed to execute before Phase 0."""
        # This tests the architectural constraint
        phase = PhaseMinusOne(
            governance_integrator=mock_governance_integrator,
            knowledge_query=mock_knowledge_query,
            output_dir=temp_output_dir
        )
        
        # Phase -1 should be callable independently
        result = phase.execute(
            feature_name='test-feature',
            user_request='plan test feature'
        )
        
        # Result should be available for Phase 0 to consume
        assert result is not None
        assert hasattr(result, 'success')
        assert hasattr(result, 'governance_validation')
        assert hasattr(result, 'knowledge_context')
    
    def test_governance_consultation_with_violations(
        self, mock_governance_integrator, mock_knowledge_query, temp_output_dir
    ):
        """Test Phase -1 handling of governance violations."""
        # Configure mock to return violations
        mock_governance_integrator.validate_feature_request.return_value = GovernanceValidation(
            is_valid=False,
            violations=[
                {'severity': 'blocked', 'message': 'TDD_ENFORCEMENT violation'},
                {'severity': 'warning', 'message': 'GIT_ISOLATION warning'}
            ],
            warnings=['Consider adding tests'],
            applied_rules=['TDD_ENFORCEMENT', 'GIT_ISOLATION'],
            governance_context={'validated': False}
        )
        
        phase = PhaseMinusOne(
            governance_integrator=mock_governance_integrator,
            knowledge_query=mock_knowledge_query,
            output_dir=temp_output_dir
        )
        
        result = phase.execute(
            feature_name='test-feature',
            user_request='plan test feature'
        )
        
        # Should fail due to blocking violation
        assert result.success is False
        assert len(result.violations) > 0
        assert any('TDD_ENFORCEMENT' in str(v) for v in result.violations)
    
    def test_knowledge_library_consultation_documented(
        self, phase_minus_one, temp_output_dir
    ):
        """Test that knowledge library consultation is documented."""
        result = phase_minus_one.execute(
            feature_name='test-feature',
            user_request='plan test feature'
        )
        
        # Consultation report should be generated
        assert result.consultation_report_path is not None
        report_path = Path(result.consultation_report_path)
        assert report_path.exists()
        assert report_path.suffix == '.md'
        
        # Report should contain key sections
        content = report_path.read_text()
        assert '# 🛡️ Phase -1 Governance Consultation Report' in content
        assert 'Tier 0: Brain Protection Rules' in content
        assert 'Tier 2: Knowledge Graph Insights' in content
        assert 'Recommendations' in content


class TestGovernanceIntegration:
    """Test governance integration with brain-protection-rules.yaml."""
    
    def test_brain_protection_rules_queried(
        self, phase_minus_one, mock_governance_integrator
    ):
        """Test that brain-protection-rules.yaml is queried."""
        result = phase_minus_one.execute(
            feature_name='test-feature',
            user_request='plan test feature'
        )
        
        # Governance integrator should be called
        mock_governance_integrator.validate_feature_request.assert_called_once()
        
        # Result should include governance validation
        assert result.governance_validation is not None
        assert hasattr(result.governance_validation, 'is_valid')
        assert hasattr(result.governance_validation, 'applied_rules')
    
    def test_skull_rules_validation(
        self, mock_governance_integrator, mock_knowledge_query, temp_output_dir
    ):
        """Test that SKULL rules are validated."""
        # Configure governance to return SKULL rule violations
        mock_governance_integrator.validate_feature_request.return_value = GovernanceValidation(
            is_valid=False,
            violations=[
                {'severity': 'blocked', 'message': 'SKULL:TDD_ENFORCEMENT - Tests required'}
            ],
            warnings=[],
            applied_rules=['TDD_ENFORCEMENT'],
            governance_context={'skull_validated': True}
        )
        
        phase = PhaseMinusOne(
            governance_integrator=mock_governance_integrator,
            knowledge_query=mock_knowledge_query,
            output_dir=temp_output_dir
        )
        
        result = phase.execute(
            feature_name='test-feature',
            user_request='plan test feature'
        )
        
        # Should detect SKULL violation
        assert result.success is False
        assert any('SKULL' in str(v) or 'TDD_ENFORCEMENT' in str(v) for v in result.violations)


class TestKnowledgeGraphIntegration:
    """Test knowledge graph integration with knowledge-graph.yaml."""
    
    def test_knowledge_graph_queries_run(
        self, phase_minus_one, mock_knowledge_query
    ):
        """Test that knowledge-graph.yaml is queried."""
        result = phase_minus_one.execute(
            feature_name='test-feature',
            user_request='plan test feature'
        )
        
        # Knowledge graph should be queried
        mock_knowledge_query.get_feature_context.assert_called_once()
        
        # Result should include knowledge context
        assert result.knowledge_context is not None
        assert hasattr(result.knowledge_context, 'patterns')
        assert hasattr(result.knowledge_context, 'related_features')
    
    def test_knowledge_patterns_integrated(
        self, phase_minus_one
    ):
        """Test that knowledge patterns are integrated into recommendations."""
        result = phase_minus_one.execute(
            feature_name='test-feature',
            user_request='plan test feature'
        )
        
        # Recommendations should reference patterns
        assert len(result.recommendations) > 0
        # Should recommend applying patterns or reviewing recommendations
        has_pattern_rec = any(
            'pattern' in rec.lower() or 'recommend' in rec.lower()
            for rec in result.recommendations
        )
        assert has_pattern_rec


class TestArtifactGeneration:
    """Test governance artifact generation."""
    
    def test_governance_artifacts_created(
        self, phase_minus_one, temp_output_dir
    ):
        """Test that governance consultation artifacts are created."""
        result = phase_minus_one.execute(
            feature_name='test-feature',
            user_request='plan test feature'
        )
        
        # Report should be created
        assert result.consultation_report_path is not None
        report_path = Path(result.consultation_report_path)
        assert report_path.exists()
        assert report_path.parent == temp_output_dir
    
    def test_consultation_report_format(
        self, phase_minus_one
    ):
        """Test consultation report format and content."""
        result = phase_minus_one.execute(
            feature_name='test-feature',
            user_request='plan test feature'
        )
        
        report_path = Path(result.consultation_report_path)
        content = report_path.read_text()
        
        # Check required sections
        assert '## 1️⃣ Tier 0: Brain Protection Rules' in content
        assert '## 2️⃣ Tier 2: Knowledge Graph Insights' in content
        assert '## 3️⃣ Recommendations' in content
        
        # Check metadata
        assert '**Feature:** test-feature' in content
        assert '**Consultation Date:**' in content
        assert 'CORTEX Planning System v5.0' in content
    
    def test_consultation_report_includes_violations(
        self, mock_governance_integrator, mock_knowledge_query, temp_output_dir
    ):
        """Test that violations are included in report."""
        # Configure violations
        mock_governance_integrator.validate_feature_request.return_value = GovernanceValidation(
            is_valid=False,
            violations=[
                {'severity': 'blocked', 'message': 'Test violation'}
            ],
            warnings=['Test warning'],
            applied_rules=['TEST_RULE'],
            governance_context={}
        )
        
        phase = PhaseMinusOne(
            governance_integrator=mock_governance_integrator,
            knowledge_query=mock_knowledge_query,
            output_dir=temp_output_dir
        )
        
        result = phase.execute(
            feature_name='test-feature',
            user_request='plan test feature'
        )
        
        report_path = Path(result.consultation_report_path)
        content = report_path.read_text()
        
        # Violations should be in report
        assert '### 🚨 Violations' in content
        assert 'Test violation' in content
        assert '### ⚠️ Warnings' in content
        assert 'Test warning' in content


class TestConvenienceFunction:
    """Test convenience function for direct execution."""
    
    def test_execute_phase_minus_one_function(
        self, mock_governance_integrator, mock_knowledge_query, temp_output_dir
    ):
        """Test execute_phase_minus_one convenience function."""
        # Patch the PhaseMinusOne constructor to use mocks
        with patch('src.orchestrators.planning.phases.phase_minus_one.GovernanceIntegrator', return_value=mock_governance_integrator):
            with patch('src.orchestrators.planning.phases.phase_minus_one.KnowledgeGraphQuery', return_value=mock_knowledge_query):
                result = execute_phase_minus_one(
                    feature_name='test-feature',
                    user_request='plan test feature',
                    output_dir=temp_output_dir
                )
        
        assert isinstance(result, GovernanceConsultationResult)
        assert result.success in [True, False]  # Can be either
        assert result.consultation_report_path is not None


class TestErrorHandling:
    """Test error handling in Phase -1."""
    
    def test_graceful_failure_on_governance_error(
        self, mock_knowledge_query, temp_output_dir
    ):
        """Test graceful handling of governance query errors."""
        mock_gov = MagicMock(spec=GovernanceIntegrator)
        mock_gov.validate_feature_request.side_effect = Exception("Governance error")
        
        phase = PhaseMinusOne(
            governance_integrator=mock_gov,
            knowledge_query=mock_knowledge_query,
            output_dir=temp_output_dir
        )
        
        result = phase.execute(
            feature_name='test-feature',
            user_request='plan test feature'
        )
        
        # Should handle error gracefully but continue with knowledge graph
        assert result is not None
        assert result.governance_validation is None  # Failed to load
        assert result.knowledge_context is not None  # But knowledge still works
    
    def test_graceful_failure_on_knowledge_graph_error(
        self, mock_governance_integrator, temp_output_dir
    ):
        """Test graceful handling of knowledge graph errors."""
        mock_kg = MagicMock(spec=KnowledgeGraphQuery)
        mock_kg.get_feature_context.side_effect = Exception("Knowledge graph error")
        
        phase = PhaseMinusOne(
            governance_integrator=mock_governance_integrator,
            knowledge_query=mock_kg,
            output_dir=temp_output_dir
        )
        
        result = phase.execute(
            feature_name='test-feature',
            user_request='plan test feature'
        )
        
        # Should continue with reduced functionality
        # (governance still works, just no knowledge context)
        assert result is not None

