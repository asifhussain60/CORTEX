"""
Tests for ADO Planning Orchestrator v3.0

Validates tiered routing, ADO formatting, DoR/DoD compliance,
version management, and completion status signaling.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from src.operations.modules.orchestration.ado_planning_orchestrator import (
    ADOPlanningOrchestrator, ADOPlanningContext, ADO_TIER_PATTERNS
)
from src.operations.modules.routing.tiered_router import OperationTier, RoutingDecision
from src.operations.modules.routing.complexity_analyzer import ComplexityScore, ComplexityTier
from src.operations.modules.ado.ado_utility import (
    WorkItemType, WorkItemStatus, WorkItemMetadata, WorkItemResult
)
from src.operations.base_operation_module import OperationStatus


class TestADOPlanningOrchestratorInit:
    """Test orchestrator initialization."""
    
    def test_initialization_success(self, tmp_path):
        """Test successful initialization with version management."""
        orchestrator = ADOPlanningOrchestrator(project_root=tmp_path)
        
        assert orchestrator.version == "3.0"
        assert orchestrator.project_root == tmp_path
        assert orchestrator.router is not None
        assert orchestrator.complexity_analyzer is not None
        assert orchestrator.metrics['work_items_created'] == 0
    
    def test_ado_directories_created(self, tmp_path):
        """Test that ADO document directories are created."""
        orchestrator = ADOPlanningOrchestrator(project_root=tmp_path)
        
        assert (tmp_path / "cortex-brain" / "documents" / "planning" / "ado" / "active").exists()
        assert (tmp_path / "cortex-brain" / "documents" / "planning" / "ado" / "completed").exists()
        assert (tmp_path / "cortex-brain" / "documents" / "planning" / "ado" / "blocked").exists()
    
    def test_metadata_correct(self, tmp_path):
        """Test orchestrator metadata."""
        orchestrator = ADOPlanningOrchestrator(project_root=tmp_path)
        metadata = orchestrator.get_metadata()
        
        assert metadata.module_id == "ado_planning_orchestrator"
        assert metadata.version == "3.0"
        assert "Azure DevOps" in metadata.description


class TestWorkItemTypeDetection:
    """Test work item type detection from operation text."""
    
    def test_detect_epic(self, tmp_path):
        """Test epic detection."""
        orchestrator = ADOPlanningOrchestrator(project_root=tmp_path)
        
        work_item_type = orchestrator._detect_work_item_type("plan epic for Q1 2025")
        assert work_item_type == WorkItemType.EPIC
    
    def test_detect_feature(self, tmp_path):
        """Test feature detection."""
        orchestrator = ADOPlanningOrchestrator(project_root=tmp_path)
        
        work_item_type = orchestrator._detect_work_item_type("create feature for user authentication")
        assert work_item_type == WorkItemType.FEATURE
    
    def test_detect_bug(self, tmp_path):
        """Test bug detection."""
        orchestrator = ADOPlanningOrchestrator(project_root=tmp_path)
        
        work_item_type = orchestrator._detect_work_item_type("fix bug in login page")
        assert work_item_type == WorkItemType.BUG
    
    def test_detect_task(self, tmp_path):
        """Test task detection."""
        orchestrator = ADOPlanningOrchestrator(project_root=tmp_path)
        
        work_item_type = orchestrator._detect_work_item_type("create task for code review")
        assert work_item_type == WorkItemType.TASK
    
    def test_default_to_story(self, tmp_path):
        """Test default to story when type unclear."""
        orchestrator = ADOPlanningOrchestrator(project_root=tmp_path)
        
        work_item_type = orchestrator._detect_work_item_type("implement user profile")
        assert work_item_type == WorkItemType.STORY


class TestTierClassification:
    """Test tier classification for ADO operations."""
    
    @patch('src.operations.modules.orchestration.ado_planning_orchestrator.TieredRouter')
    def test_tier1_classification(self, mock_router_class, tmp_path):
        """Test Tier 1 classification for quick updates."""
        mock_router = Mock()
        mock_router.classify_operation.return_value = RoutingDecision(
            tier=1,
            confidence=0.95,
            reasoning="Quick status update",
            execution_method="direct_execution",
            estimated_time="<2s",
            requires_planning=False
        )
        mock_router_class.return_value = mock_router
        
        orchestrator = ADOPlanningOrchestrator(project_root=tmp_path)
        orchestrator.router = mock_router
        
        context = orchestrator._classify_and_analyze("update story status to completed")
        
        assert context.tier == 1
        assert orchestrator.metrics['tier_1_operations'] == 1
    
    @patch('src.operations.modules.orchestration.ado_planning_orchestrator.TieredRouter')
    def test_tier2_classification(self, mock_router_class, tmp_path):
        """Test Tier 2 classification for single work item."""
        mock_router = Mock()
        mock_router.classify_operation.return_value = RoutingDecision(
            tier=2,
            confidence=0.90,
            reasoning="Single story creation",
            execution_method="inline_validation",
            estimated_time="<10s",
            requires_planning=False
        )
        mock_router_class.return_value = mock_router
        
        orchestrator = ADOPlanningOrchestrator(project_root=tmp_path)
        orchestrator.router = mock_router
        
        context = orchestrator._classify_and_analyze("create story for user login")
        
        assert context.tier == 2
        assert orchestrator.metrics['tier_2_operations'] == 1
    
    @patch('src.operations.modules.orchestration.ado_planning_orchestrator.TieredRouter')
    def test_tier3_classification(self, mock_router_class, tmp_path):
        """Test Tier 3 classification for feature planning."""
        mock_router = Mock()
        mock_router.classify_operation.return_value = RoutingDecision(
            tier=3,
            confidence=0.92,
            reasoning="Feature with acceptance criteria",
            execution_method="documented_planning",
            estimated_time="10-60min",
            requires_planning=True
        )
        mock_router_class.return_value = mock_router
        
        orchestrator = ADOPlanningOrchestrator(project_root=tmp_path)
        orchestrator.router = mock_router
        
        context = orchestrator._classify_and_analyze("plan feature with multiple stories")
        
        assert context.tier == 3
        assert orchestrator.metrics['tier_3_operations'] == 1
    
    @patch('src.operations.modules.orchestration.ado_planning_orchestrator.TieredRouter')
    def test_tier4_classification(self, mock_router_class, tmp_path):
        """Test Tier 4 classification for epic planning."""
        mock_router = Mock()
        mock_router.classify_operation.return_value = RoutingDecision(
            tier=4,
            confidence=0.88,
            reasoning="Multi-feature epic",
            execution_method="nested_planning",
            estimated_time=">1h",
            requires_planning=True
        )
        mock_router_class.return_value = mock_router
        
        orchestrator = ADOPlanningOrchestrator(project_root=tmp_path)
        orchestrator.router = mock_router
        
        context = orchestrator._classify_and_analyze("plan epic with multiple features")
        
        assert context.tier == 4
        assert orchestrator.metrics['tier_4_operations'] == 1


class TestTier1Execution:
    """Test Tier 1 instant operations."""
    
    @patch('src.operations.modules.orchestration.ado_planning_orchestrator.load_work_item')
    @patch('src.operations.modules.orchestration.ado_planning_orchestrator.update_work_item')
    def test_tier1_status_update(self, mock_update, mock_load, tmp_path):
        """Test Tier 1 status update."""
        # Mock load result
        mock_load.return_value = WorkItemResult(
            success=True,
            message="Work item loaded",
            work_item_id="WI-001"
        )
        
        # Mock update result
        mock_update.return_value = WorkItemResult(
            success=True,
            message="Work item updated"
        )
        
        orchestrator = ADOPlanningOrchestrator(project_root=tmp_path)
        
        context = ADOPlanningContext(
            operation="update story status",
            work_item_type=WorkItemType.STORY,
            tier=1,
            complexity_score=ComplexityScore(
                total_score=10,
                tier=ComplexityTier.TRIVIAL,
                dimensions={'scope_magnitude': 3, 'dependencies': 2, 'risk_level': 3, 'uncertainty': 2},
                rationale=["Simple update"],
                recommendation="Direct execution",
                triggers=[]
            ),
            routing_decision=RoutingDecision(
                tier=1,
                confidence=0.95,
                reasoning="Quick update",
                execution_method="direct",
                estimated_time="<2s",
                requires_planning=False
            )
        )
        
        user_context = {
            'work_item_id': 'WI-001',
            'status': 'completed'
        }
        
        result = orchestrator._execute_tier1_instant(context, user_context)
        
        assert result['success'] is True
        assert result['tier'] == 1
        assert result['work_item_id'] == 'WI-001'


class TestTier2Execution:
    """Test Tier 2 lightweight operations."""
    
    @patch('src.operations.modules.orchestration.ado_planning_orchestrator.create_work_item')
    def test_tier2_story_creation(self, mock_create, tmp_path):
        """Test Tier 2 story creation."""
        mock_create.return_value = WorkItemResult(
            success=True,
            message="Story created",
            work_item_id="WI-002"
        )
        
        orchestrator = ADOPlanningOrchestrator(project_root=tmp_path)
        
        context = ADOPlanningContext(
            operation="create story for user login",
            work_item_type=WorkItemType.STORY,
            tier=2,
            complexity_score=ComplexityScore(
                total_score=35,
                tier=ComplexityTier.LOW,
                dimensions={'scope_magnitude': 10, 'dependencies': 8, 'risk_level': 10, 'uncertainty': 7},
                rationale=["Single story"],
                recommendation="Lightweight planning",
                triggers=[]
            ),
            routing_decision=RoutingDecision(
                tier=2,
                confidence=0.90,
                reasoning="Single story",
                execution_method="inline",
                estimated_time="<10s",
                requires_planning=False
            ),
            title="User Login",
            description="Implement user login functionality"
        )
        
        user_context = {
            'title': 'User Login',
            'description': 'Implement user login functionality',
            'priority': 1
        }
        
        result = orchestrator._execute_tier2_lightweight(context, user_context)
        
        assert result['success'] is True
        assert result['tier'] == 2
        assert result['work_item_id'] == 'WI-002'
        assert orchestrator.metrics['work_items_created'] == 1


class TestTier3Execution:
    """Test Tier 3 documented feature planning."""
    
    @patch('src.operations.modules.orchestration.ado_planning_orchestrator.create_work_item')
    @patch('src.operations.modules.orchestration.ado_planning_orchestrator.validate_dor')
    def test_tier3_feature_planning(self, mock_dor, mock_create, tmp_path):
        """Test Tier 3 feature planning with documentation."""
        mock_dor.return_value = Mock(
            passed=True,
            score=85.0,
            warnings=[]
        )
        
        mock_create.return_value = WorkItemResult(
            success=True,
            message="Feature created",
            work_item_id="WI-003"
        )
        
        orchestrator = ADOPlanningOrchestrator(project_root=tmp_path)
        
        context = ADOPlanningContext(
            operation="plan feature for authentication",
            work_item_type=WorkItemType.FEATURE,
            tier=3,
            complexity_score=ComplexityScore(
                total_score=55,
                tier=ComplexityTier.MEDIUM,
                dimensions={'scope_magnitude': 15, 'dependencies': 12, 'risk_level': 18, 'uncertainty': 10},
                rationale=["Feature planning"],
                recommendation="Documented planning",
                triggers=[]
            ),
            routing_decision=RoutingDecision(
                tier=3,
                confidence=0.92,
                reasoning="Feature planning",
                execution_method="documented",
                estimated_time="10-60min",
                requires_planning=True
            ),
            title="User Authentication",
            description="Complete authentication system",
            acceptance_criteria=["Users can log in", "Users can log out"]
        )
        
        user_context = {
            'title': 'User Authentication',
            'description': 'Complete authentication system',
            'acceptance_criteria': ['Users can log in', 'Users can log out']
        }
        
        result = orchestrator._execute_tier3_documented(context, user_context)
        
        assert result['success'] is True
        assert result['tier'] == 3
        assert result['work_item_id'] == 'WI-003'
        assert 'document_path' in result
        assert 'dor_validation' in result
        assert orchestrator.metrics['work_items_created'] == 1
        assert orchestrator.metrics['dor_validations'] == 1


class TestTier4Execution:
    """Test Tier 4 complex epic planning."""
    
    @patch('src.operations.modules.orchestration.ado_planning_orchestrator.create_work_item')
    def test_tier4_epic_with_children(self, mock_create, tmp_path):
        """Test Tier 4 epic creation with child items."""
        # Mock epic creation
        mock_create.side_effect = [
            WorkItemResult(
                success=True,
                message="Epic created",
                work_item_id="WI-EPIC-001"
            ),
            WorkItemResult(
                success=True,
                message="Feature 1 created",
                work_item_id="WI-004"
            ),
            WorkItemResult(
                success=True,
                message="Feature 2 created",
                work_item_id="WI-005"
            )
        ]
        
        orchestrator = ADOPlanningOrchestrator(project_root=tmp_path)
        
        context = ADOPlanningContext(
            operation="plan epic for platform modernization",
            work_item_type=WorkItemType.EPIC,
            tier=4,
            complexity_score=ComplexityScore(
                total_score=85,
                tier=ComplexityTier.HIGH,
                dimensions={'scope_magnitude': 22, 'dependencies': 20, 'risk_level': 25, 'uncertainty': 18},
                rationale=["Complex epic"],
                recommendation="Nested planning",
                triggers=[]
            ),
            routing_decision=RoutingDecision(
                tier=4,
                confidence=0.88,
                reasoning="Complex epic",
                execution_method="nested",
                estimated_time=">1h",
                requires_planning=True
            ),
            title="Platform Modernization",
            description="Modernize entire platform"
        )
        
        user_context = {
            'title': 'Platform Modernization',
            'description': 'Modernize entire platform',
            'child_items': [
                {'title': 'Frontend Upgrade', 'description': 'Upgrade React version'},
                {'title': 'Backend Migration', 'description': 'Migrate to microservices'}
            ]
        }
        
        result = orchestrator._execute_tier4_complex(context, user_context)
        
        assert result['success'] is True
        assert result['tier'] == 4
        assert result['epic']['work_item_id'] == 'WI-EPIC-001'
        assert len(result['child_items']) == 2
        assert 'document_path' in result
        assert orchestrator.metrics['work_items_created'] == 3


class TestCompletionStatus:
    """Test completion status signaling for template selection."""
    
    @patch('src.operations.modules.orchestration.ado_planning_orchestrator.create_work_item')
    @patch('src.operations.modules.orchestration.ado_planning_orchestrator.load_work_item')
    @patch('src.operations.modules.orchestration.ado_planning_orchestrator.validate_dod')
    @patch('src.operations.modules.orchestration.ado_planning_orchestrator.TieredRouter')
    @patch('src.operations.modules.orchestration.ado_planning_orchestrator.ComplexityAnalyzer')
    def test_completion_status_success(
        self, 
        mock_analyzer_class,
        mock_router_class,
        mock_dod,
        mock_load,
        mock_create,
        tmp_path
    ):
        """Test is_complete flag when all work succeeds."""
        # Setup mocks
        mock_router = Mock()
        mock_router.classify_operation.return_value = RoutingDecision(
            tier=2,
            confidence=0.90,
            reasoning="Single story",
            execution_method="inline",
            estimated_time="<10s",
            requires_planning=False
        )
        mock_router_class.return_value = mock_router
        
        mock_analyzer = Mock()
        mock_analyzer.analyze.return_value = ComplexityScore(
            total_score=35,
            tier=ComplexityTier.LOW,
            dimensions={'scope_magnitude': 10, 'dependencies': 8, 'risk_level': 10, 'uncertainty': 7},
            rationale=["Single story"],
            recommendation="Lightweight",
            triggers=[]
        )
        mock_analyzer_class.return_value = mock_analyzer
        
        mock_create.return_value = WorkItemResult(
            success=True,
            message="Story created",
            work_item_id="WI-TEST-001"
        )
        
        mock_load.return_value = WorkItemResult(
            success=True,
            message="Loaded",
            work_item_id="WI-TEST-001",
            metadata=Mock()
        )
        
        mock_dod.return_value = Mock(passed=True, score=90.0)
        
        orchestrator = ADOPlanningOrchestrator(project_root=tmp_path)
        orchestrator.router = mock_router
        orchestrator.complexity_analyzer = mock_analyzer
        
        context = {
            'operation': 'create story for user profile',
            'title': 'User Profile',
            'description': 'Implement user profile page'
        }
        
        result = orchestrator.execute(context)
        
        assert result.success is True
        assert result.data['is_complete'] is True
        assert len(orchestrator.metrics['errors']) == 0
    
    @patch('src.operations.modules.orchestration.ado_planning_orchestrator.TieredRouter')
    @patch('src.operations.modules.orchestration.ado_planning_orchestrator.ComplexityAnalyzer')
    def test_completion_status_with_errors(
        self,
        mock_analyzer_class,
        mock_router_class,
        tmp_path
    ):
        """Test is_complete flag when errors occur."""
        mock_router = Mock()
        mock_router.classify_operation.side_effect = Exception("Classification failed")
        mock_router_class.return_value = mock_router
        
        orchestrator = ADOPlanningOrchestrator(project_root=tmp_path)
        orchestrator.router = mock_router
        
        context = {
            'operation': 'create story'
        }
        
        result = orchestrator.execute(context)
        
        assert result.success is False
        assert result.data['is_complete'] is False
        assert len(orchestrator.metrics['errors']) > 0


class TestVersionManagement:
    """Test version management integration."""
    
    def test_version_registration(self, tmp_path):
        """Test that orchestrator version is registered."""
        orchestrator = ADOPlanningOrchestrator(project_root=tmp_path)
        
        # Version should be registered with VersionManager
        assert orchestrator.version == "3.0"
    
    def test_version_in_metadata(self, tmp_path):
        """Test version appears in metadata."""
        orchestrator = ADOPlanningOrchestrator(project_root=tmp_path)
        metadata = orchestrator.metadata
        
        assert metadata.version == "3.0"


class TestADOFormatting:
    """Test ADO-specific formatting preservation."""
    
    def test_planning_document_format(self, tmp_path):
        """Test planning document contains ADO fields."""
        orchestrator = ADOPlanningOrchestrator(project_root=tmp_path)
        
        metadata = WorkItemMetadata(
            work_item_type=WorkItemType.STORY,
            title="Test Story",
            description="Test description",
            acceptance_criteria=["Criterion 1", "Criterion 2"],
            area_path="Team/Product",
            iteration="Sprint 1",
            priority=1,
            tags=["backend", "api"]
        )
        
        dor_result = Mock(
            passed=True,
            score=90.0,
            warnings=[]
        )
        
        context = ADOPlanningContext(
            operation="test",
            work_item_type=WorkItemType.STORY,
            tier=3,
            complexity_score=ComplexityScore(
                total_score=45,
                tier=ComplexityTier.MEDIUM,
                dimensions={'scope_magnitude': 12, 'dependencies': 10, 'risk_level': 15, 'uncertainty': 8},
                rationale=["Test context"],
                recommendation="Documented planning",
                triggers=[]
            ),
            routing_decision=RoutingDecision(
                tier=3,
                confidence=0.90,
                reasoning="Test",
                execution_method="documented",
                estimated_time="10-60min",
                requires_planning=True
            )
        )
        
        doc_path = orchestrator._create_planning_document(
            work_item_id="WI-TEST",
            metadata=metadata,
            dor_result=dor_result,
            context=context
        )
        
        content = doc_path.read_text()
        
        # Verify ADO fields present
        assert "Work Item ID:" in content
        assert "WI-TEST" in content
        assert "Test Story" in content
        assert "Area Path:" in content
        assert "Iteration:" in content
        assert "Priority:" in content
        assert "Definition of Ready (DoR)" in content
        assert "Definition of Done (DoD)" in content
        assert "Acceptance Criteria" in content


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
