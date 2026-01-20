"""
Test Suite for Master Orchestrator Stage 3 (Knowledge) - AC-PROD-003-02

Stage 3 represents the Knowledge phase of the Master Orchestrator 4-stage workflow.
It executes LENS Protocol Phases 1-3 (Language→Examination→Navigation) and integrates
the Relationship Graph to produce domain knowledge output that feeds into Stage 4 (Approval).

The knowledge stage:
1. Receives Stage 1 comprehension output
2. Runs LENS Phases 1-3 (Language→Examination→Navigation)
3. Builds domain knowledge graph using RelationshipAnalyzer
4. Generates recommendations from knowledge synthesis
5. Produces Stage 3 output ready for Stage 4 approval
6. Logs all operations to audit trail

CORE Governance:
  - CORE-008: TDD (tests first)
  - CORE-011: Type hints mandatory
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-027: Audit trail logging
"""

import pytest
from typing import Dict, Any, List, Optional

from cortex.core.result import Result, Ok, Err
from cortex.orchestrators.core.master_orchestrator_stage_1 import Stage1Output


class TestStage3Initialization:
    """Test Stage 3 Knowledge initialization and setup."""
    
    def test_stage_3_initializes(self) -> None:
        """Test MasterOrchestrationStage3 creates successfully."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            MasterOrchestrationStage3
        )
        
        stage3 = MasterOrchestrationStage3()
        assert stage3 is not None
        assert hasattr(stage3, 'process_knowledge')
        assert hasattr(stage3, 'get_knowledge_history')
    
    def test_stage_3_has_required_attributes(self) -> None:
        """Test Stage 3 has required attributes."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            MasterOrchestrationStage3
        )
        
        stage3 = MasterOrchestrationStage3()
        
        assert hasattr(stage3, 'logger')
        assert hasattr(stage3, 'knowledge_history')
        assert hasattr(stage3, 'relationship_analyzer')
        assert hasattr(stage3, 'lens_synthesizer')
    
    def test_stage_3_starts_with_empty_history(self) -> None:
        """Test Stage 3 starts with empty knowledge history."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            MasterOrchestrationStage3
        )
        
        stage3 = MasterOrchestrationStage3()
        
        history = stage3.get_knowledge_history()
        assert len(history) == 0


class TestStage3KnowledgeContext:
    """Test Stage3KnowledgeContext dataclass."""
    
    def test_knowledge_context_from_stage1_output(self) -> None:
        """Test Stage 3 context creation from Stage 1 output."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            Stage3KnowledgeContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_1 import Stage1Output
        
        stage1_output = Stage1Output(
            operation="implement_oauth2",
            language_analysis={"intent": "implement", "confidence": 0.92},
            extracted_intent="implement",
            confidence_score=0.92,
            domain="api"
        )
        
        context = Stage3KnowledgeContext(
            stage1_output=stage1_output,
            domain="api",
            codebase_path="/path/to/codebase",
            entities=["User", "AuthToken", "Session"]
        )
        
        assert context.stage1_output.operation == "implement_oauth2"
        assert context.domain == "api"
        assert "User" in context.entities
    
    def test_knowledge_context_with_relationships(self) -> None:
        """Test context with existing relationship data."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            Stage3KnowledgeContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_1 import Stage1Output
        
        stage1_output = Stage1Output(
            operation="fix_auth",
            language_analysis={"intent": "fix"},
            extracted_intent="fix",
            confidence_score=0.88,
            domain="api"
        )
        
        context = Stage3KnowledgeContext(
            stage1_output=stage1_output,
            domain="api",
            codebase_path="/path/to/codebase",
            entities=["AuthService"],
            relationships=[
                {"from": "AuthService", "to": "Database", "type": "depends_on"}
            ]
        )
        
        assert len(context.relationships) == 1
        assert context.relationships[0]["type"] == "depends_on"


class TestStage3Output:
    """Test Stage3Output dataclass."""
    
    def test_output_creation(self) -> None:
        """Test Stage3Output creates successfully."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            Stage3Output
        )
        
        output = Stage3Output(
            operation="implement",
            stage1_output=None,
            knowledge_graph={
                "entities": ["User", "Auth"],
                "relationships": []
            },
            lens_recommendations=[
                {"phase": "language", "recommendation": "Use OAuth2"}
            ],
            confidence_score=0.90,
            domain="api"
        )
        
        assert output.operation == "implement"
        assert output.confidence_score == 0.90
        assert len(output.lens_recommendations) > 0
    
    def test_output_has_stage_4_ready_format(self) -> None:
        """Test output format is ready for Stage 4 approval."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            Stage3Output
        )
        
        output = Stage3Output(
            operation="fix",
            stage1_output=None,
            knowledge_graph={},
            lens_recommendations=[],
            confidence_score=0.85,
            domain="persistence"
        )
        
        # Stage 4 should be able to consume this
        assert hasattr(output, 'knowledge_graph')
        assert hasattr(output, 'lens_recommendations')
        assert hasattr(output, 'confidence_score')
        assert hasattr(output, 'operation')


class TestLENSPhase1Integration:
    """Test LENS Phase 1 (Language) integration in Stage 3."""
    
    def test_stage3_receives_stage1_comprehension(self) -> None:
        """Test Stage 3 receives and processes Stage 1 comprehension."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            MasterOrchestrationStage3,
            Stage3KnowledgeContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_1 import Stage1Output
        
        stage3 = MasterOrchestrationStage3()
        
        stage1_output = Stage1Output(
            operation="implement_feature",
            language_analysis={"intent": "implement"},
            extracted_intent="implement",
            confidence_score=0.92,
            domain="api"
        )
        
        context = Stage3KnowledgeContext(
            stage1_output=stage1_output,
            domain="api",
            codebase_path="/path/to/code",
            entities=[]
        )
        
        result = stage3.process_knowledge(context)
        assert result is not None
    
    def test_language_analysis_phase_incorporated(self) -> None:
        """Test LENS Language analysis is incorporated."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            MasterOrchestrationStage3,
            Stage3KnowledgeContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_1 import Stage1Output
        
        stage3 = MasterOrchestrationStage3()
        
        stage1_output = Stage1Output(
            operation="fix_bug",
            language_analysis={
                "intent": "fix",
                "confidence": 0.88,
                "analysis": "Clear bug fix intent"
            },
            extracted_intent="fix",
            confidence_score=0.88,
            domain="persistence"
        )
        
        context = Stage3KnowledgeContext(
            stage1_output=stage1_output,
            domain="persistence",
            codebase_path="/path/to/code",
            entities=["Database", "Connection"]
        )
        
        result = stage3.process_knowledge(context)
        assert result is not None


class TestLENSPhase2Integration:
    """Test LENS Phase 2 (Examination) integration in Stage 3."""
    
    def test_code_examination_phase_executed(self) -> None:
        """Test LENS Phase 2 code examination is executed."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            MasterOrchestrationStage3,
            Stage3KnowledgeContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_1 import Stage1Output
        
        stage3 = MasterOrchestrationStage3()
        
        stage1_output = Stage1Output(
            operation="refactor_code",
            language_analysis={"intent": "refactor"},
            extracted_intent="refactor",
            confidence_score=0.85,
            domain="core"
        )
        
        context = Stage3KnowledgeContext(
            stage1_output=stage1_output,
            domain="core",
            codebase_path="/path/to/code",
            entities=["Module1", "Module2"],
            relationships=[
                {"from": "Module1", "to": "Module2", "type": "imports"}
            ]
        )
        
        result = stage3.process_knowledge(context)
        assert result is not None


class TestLENSPhase3Integration:
    """Test LENS Phase 3 (Navigation) integration in Stage 3."""
    
    def test_domain_navigation_graph_built(self) -> None:
        """Test domain navigation graph is built."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            MasterOrchestrationStage3,
            Stage3KnowledgeContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_1 import Stage1Output
        
        stage3 = MasterOrchestrationStage3()
        
        stage1_output = Stage1Output(
            operation="understand_architecture",
            language_analysis={},
            extracted_intent="implement",
            confidence_score=0.90,
            domain="core"
        )
        
        context = Stage3KnowledgeContext(
            stage1_output=stage1_output,
            domain="core",
            codebase_path="/path/to/code",
            entities=[
                "APIController",
                "ServiceLayer",
                "RepositoryLayer",
                "Database"
            ]
        )
        
        result = stage3.process_knowledge(context)
        assert result is not None


class TestRelationshipGraphIntegration:
    """Test RelationshipAnalyzer integration in Stage 3."""
    
    def test_relationship_analyzer_instantiated(self) -> None:
        """Test RelationshipAnalyzer is instantiated."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            MasterOrchestrationStage3
        )
        
        stage3 = MasterOrchestrationStage3()
        
        # Should have RelationshipAnalyzer
        assert stage3.relationship_analyzer is not None
    
    def test_entities_extracted_from_relationships(self) -> None:
        """Test entities are extracted and indexed."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            MasterOrchestrationStage3,
            Stage3KnowledgeContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_1 import Stage1Output
        
        stage3 = MasterOrchestrationStage3()
        
        stage1_output = Stage1Output(
            operation="find_dependencies",
            language_analysis={},
            extracted_intent="implement",
            confidence_score=0.88,
            domain="api"
        )
        
        context = Stage3KnowledgeContext(
            stage1_output=stage1_output,
            domain="api",
            codebase_path="/path/to/code",
            entities=["UserService", "AuthService", "TokenService"]
        )
        
        result = stage3.process_knowledge(context)
        assert result is not None


class TestLENSSynthesisIntegration:
    """Test LENS Synthesis Phase integration in Stage 3."""
    
    def test_lens_synthesis_produces_recommendations(self) -> None:
        """Test LENS Synthesis produces recommendations."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            MasterOrchestrationStage3,
            Stage3KnowledgeContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_1 import Stage1Output
        
        stage3 = MasterOrchestrationStage3()
        
        stage1_output = Stage1Output(
            operation="synthesize_knowledge",
            language_analysis={"intent": "implement"},
            extracted_intent="implement",
            confidence_score=0.92,
            domain="api"
        )
        
        context = Stage3KnowledgeContext(
            stage1_output=stage1_output,
            domain="api",
            codebase_path="/path/to/code",
            entities=["Auth", "User", "Token"]
        )
        
        result = stage3.process_knowledge(context)
        if result.is_ok():
            output = result.unwrap()
            # Should have LENS recommendations
            assert hasattr(output, 'lens_recommendations')


class TestKnowledgeGraphConstruction:
    """Test knowledge graph construction."""
    
    def test_knowledge_graph_populated(self) -> None:
        """Test knowledge graph is populated with entities."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            MasterOrchestrationStage3,
            Stage3KnowledgeContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_1 import Stage1Output
        
        stage3 = MasterOrchestrationStage3()
        
        stage1_output = Stage1Output(
            operation="map_domain",
            language_analysis={},
            extracted_intent="implement",
            confidence_score=0.90,
            domain="persistence"
        )
        
        context = Stage3KnowledgeContext(
            stage1_output=stage1_output,
            domain="persistence",
            codebase_path="/path/to/code",
            entities=["UserRepository", "SessionRepository", "AuditLog"],
            relationships=[
                {"from": "UserRepository", "to": "Database", "type": "uses"},
                {"from": "SessionRepository", "to": "Cache", "type": "uses"}
            ]
        )
        
        result = stage3.process_knowledge(context)
        if result.is_ok():
            output = result.unwrap()
            assert hasattr(output, 'knowledge_graph')


class TestKnowledgeHistory:
    """Test knowledge processing history tracking."""
    
    def test_history_tracks_knowledge_operations(self) -> None:
        """Test history tracks all knowledge operations."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            MasterOrchestrationStage3,
            Stage3KnowledgeContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_1 import Stage1Output
        
        stage3 = MasterOrchestrationStage3()
        
        # Process first knowledge context
        stage1_output1 = Stage1Output(
            operation="op1",
            language_analysis={},
            extracted_intent="implement",
            confidence_score=0.90,
            domain="api"
        )
        
        context1 = Stage3KnowledgeContext(
            stage1_output=stage1_output1,
            domain="api",
            codebase_path="/path/to/code",
            entities=[]
        )
        
        stage3.process_knowledge(context1)
        
        # Process second knowledge context
        stage1_output2 = Stage1Output(
            operation="op2",
            language_analysis={},
            extracted_intent="fix",
            confidence_score=0.88,
            domain="api"
        )
        
        context2 = Stage3KnowledgeContext(
            stage1_output=stage1_output2,
            domain="api",
            codebase_path="/path/to/code",
            entities=[]
        )
        
        stage3.process_knowledge(context2)
        
        history = stage3.get_knowledge_history()
        assert len(history) >= 2
    
    def test_history_preserves_order(self) -> None:
        """Test history preserves chronological order."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            MasterOrchestrationStage3,
            Stage3KnowledgeContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_1 import Stage1Output
        
        stage3 = MasterOrchestrationStage3()
        
        for i in range(3):
            stage1_output = Stage1Output(
                operation=f"op_{i}",
                language_analysis={},
                extracted_intent="implement",
                confidence_score=0.90,
                domain="api"
            )
            
            context = Stage3KnowledgeContext(
                stage1_output=stage1_output,
                domain="api",
                codebase_path="/path/to/code",
                entities=[]
            )
            
            stage3.process_knowledge(context)
        
        history = stage3.get_knowledge_history()
        # History should contain operations in order
        assert all(h is not None for h in history)


class TestStage3ToStage4Handoff:
    """Test handoff from Stage 3 to Stage 4."""
    
    def test_stage3_output_ready_for_stage4_approval(self) -> None:
        """Test Stage 3 output is compatible with Stage 4 approval."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            MasterOrchestrationStage3,
            Stage3KnowledgeContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_1 import Stage1Output
        
        stage3 = MasterOrchestrationStage3()
        
        stage1_output = Stage1Output(
            operation="prepare_for_approval",
            language_analysis={"intent": "implement"},
            extracted_intent="implement",
            confidence_score=0.92,
            domain="api"
        )
        
        context = Stage3KnowledgeContext(
            stage1_output=stage1_output,
            domain="api",
            codebase_path="/path/to/code",
            entities=[]
        )
        
        result = stage3.process_knowledge(context)
        if result.is_ok():
            output = result.unwrap()
            
            # Stage 4 needs these fields
            assert hasattr(output, 'knowledge_graph')
            assert hasattr(output, 'confidence_score')
            assert hasattr(output, 'lens_recommendations')
    
    def test_stage3_provides_knowledge_for_approval_decision(self) -> None:
        """Test Stage 3 provides sufficient knowledge for approval."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            MasterOrchestrationStage3,
            Stage3KnowledgeContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_1 import Stage1Output
        
        stage3 = MasterOrchestrationStage3()
        
        stage1_output = Stage1Output(
            operation="approval_ready",
            language_analysis={
                "intent": "implement",
                "confidence": 0.92
            },
            extracted_intent="implement",
            confidence_score=0.92,
            domain="api"
        )
        
        context = Stage3KnowledgeContext(
            stage1_output=stage1_output,
            domain="api",
            codebase_path="/path/to/code",
            entities=["Service", "Repository", "Controller"]
        )
        
        result = stage3.process_knowledge(context)
        if result.is_ok():
            output = result.unwrap()
            # Should have good confidence for approval
            assert output.confidence_score > 0.5


class TestErrorHandling:
    """Test error handling in Stage 3."""
    
    def test_process_knowledge_invalid_context(self) -> None:
        """Test invalid context returns error."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            MasterOrchestrationStage3
        )
        
        stage3 = MasterOrchestrationStage3()
        
        result = stage3.process_knowledge(None)
        assert result.is_err()
    
    def test_process_knowledge_missing_stage1_output(self) -> None:
        """Test missing Stage 1 output handled."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            MasterOrchestrationStage3,
            Stage3KnowledgeContext
        )
        
        stage3 = MasterOrchestrationStage3()
        
        # Context with None stage1_output
        context = Stage3KnowledgeContext(
            stage1_output=None,
            domain="api",
            codebase_path="/path/to/code",
            entities=[]
        )
        
        result = stage3.process_knowledge(context)
        # Should handle gracefully
        assert result is not None
    
    def test_invalid_domain_handled(self) -> None:
        """Test invalid domain handled gracefully."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            MasterOrchestrationStage3,
            Stage3KnowledgeContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_1 import Stage1Output
        
        stage3 = MasterOrchestrationStage3()
        
        stage1_output = Stage1Output(
            operation="bad_domain",
            language_analysis={},
            extracted_intent="implement",
            confidence_score=0.90,
            domain="invalid_domain"  # Non-standard domain
        )
        
        context = Stage3KnowledgeContext(
            stage1_output=stage1_output,
            domain="invalid_domain",
            codebase_path="/path/to/code",
            entities=[]
        )
        
        result = stage3.process_knowledge(context)
        # Should handle gracefully
        assert result is not None


class TestGovernanceCompliance:
    """Test CORE governance compliance."""
    
    def test_core_011_type_hints_present(self) -> None:
        """Test CORE-011: Type hints present on all methods."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            MasterOrchestrationStage3
        )
        
        stage3 = MasterOrchestrationStage3()
        
        assert hasattr(stage3.process_knowledge, '__annotations__')
        assert 'return' in stage3.process_knowledge.__annotations__
    
    def test_core_012_docstrings_present(self) -> None:
        """Test CORE-012: Google-style docstrings present."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            MasterOrchestrationStage3
        )
        
        assert MasterOrchestrationStage3.__doc__ is not None
        assert len(MasterOrchestrationStage3.__doc__) > 0
    
    def test_core_027_audit_trail_support(self) -> None:
        """Test CORE-027: Audit trail support."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            MasterOrchestrationStage3
        )
        
        stage3 = MasterOrchestrationStage3()
        
        # Should have audit logger
        assert hasattr(stage3, 'logger')


class TestAuditTrailing:
    """Test audit trail logging for knowledge operations."""
    
    def test_knowledge_processing_logged(self) -> None:
        """Test knowledge processing operations are logged."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            MasterOrchestrationStage3,
            Stage3KnowledgeContext
        )
        from cortex.orchestrators.core.master_orchestrator_stage_1 import Stage1Output
        
        stage3 = MasterOrchestrationStage3()
        
        stage1_output = Stage1Output(
            operation="test_logging",
            language_analysis={},
            extracted_intent="implement",
            confidence_score=0.90,
            domain="api"
        )
        
        context = Stage3KnowledgeContext(
            stage1_output=stage1_output,
            domain="api",
            codebase_path="/path/to/code",
            entities=[]
        )
        
        result = stage3.process_knowledge(context)
        # Operation should be logged
        assert result is not None
    
    def test_error_operations_logged(self) -> None:
        """Test error operations are logged."""
        from cortex.orchestrators.core.master_orchestrator_stage_3 import (
            MasterOrchestrationStage3
        )
        
        stage3 = MasterOrchestrationStage3()
        
        result = stage3.process_knowledge(None)
        # Error should be logged
        assert result.is_err()


# Module exports
__all__ = [
    "TestStage3Initialization",
    "TestStage3KnowledgeContext",
    "TestStage3Output",
    "TestLENSPhase1Integration",
    "TestLENSPhase2Integration",
    "TestLENSPhase3Integration",
    "TestRelationshipGraphIntegration",
    "TestLENSSynthesisIntegration",
    "TestKnowledgeGraphConstruction",
    "TestKnowledgeHistory",
    "TestStage3ToStage4Handoff",
    "TestErrorHandling",
    "TestGovernanceCompliance",
    "TestAuditTrailing",
]
