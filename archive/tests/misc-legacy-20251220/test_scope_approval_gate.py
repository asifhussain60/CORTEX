"""
Unit Tests for CORTEX 3.2.1: Scope Approval Gate

Tests the scope approval workflow that blocks time estimates until
user approves inferred scope boundaries.

Test Coverage:
- ScopeBoundary approval tracking (approve_scope, is_approval_required)
- Tier 1 SWAGGER context storage (store, retrieve, update)
- Estimation blocking when scope unapproved
- Planner handoff workflow
- Resume estimation after approval

Author: GitHub Copilot (CORTEX 3.2.1)
Created: 2025-11-29
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime
import json

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from src.agents.estimation.scope_inference_engine import ScopeBoundary, ScopeEntities
from src.tier1.working_memory import WorkingMemory
from src.orchestrators.planning_orchestrator import PlanningOrchestrator


class TestScopeBoundaryApproval:
    """Test ScopeBoundary approval tracking"""
    
    def test_scope_boundary_default_not_approved(self):
        """Test that ScopeBoundary defaults to not approved"""
        scope = ScopeBoundary(
            table_count=3,
            file_count=5,
            service_count=2,
            dependency_depth=1,
            estimated_complexity=75.0,
            confidence=0.85,
            gaps=[]
        )
        
        assert scope.user_approved == False
        assert scope.approval_timestamp is None
        assert scope.approval_method is None
        assert scope.swagger_context_id is None
    
    def test_approve_scope_sets_fields(self):
        """Test that approve_scope() sets approval fields correctly"""
        scope = ScopeBoundary(
            table_count=3,
            file_count=5,
            service_count=2,
            dependency_depth=1,
            estimated_complexity=75.0,
            confidence=0.85,
            gaps=[]
        )
        
        # Approve with default method
        scope.approve_scope()
        
        assert scope.user_approved == True
        assert scope.approval_timestamp is not None
        assert scope.approval_method == 'interactive'
        
        # Verify timestamp is ISO format
        datetime.fromisoformat(scope.approval_timestamp)
    
    def test_approve_scope_with_custom_method(self):
        """Test approve_scope() with custom approval method"""
        scope = ScopeBoundary(
            table_count=3,
            file_count=5,
            service_count=2,
            dependency_depth=1,
            estimated_complexity=75.0,
            confidence=0.85,
            gaps=[]
        )
        
        scope.approve_scope(method='plan')
        
        assert scope.user_approved == True
        assert scope.approval_method == 'plan'
    
    def test_is_approval_required_low_confidence(self):
        """Test is_approval_required() returns True for low confidence (<80%)"""
        scope = ScopeBoundary(
            table_count=3,
            file_count=5,
            service_count=2,
            dependency_depth=1,
            estimated_complexity=75.0,
            confidence=0.70,  # Below 80% threshold
            gaps=[],
            user_approved=True  # Even if approved, low confidence requires revalidation
        )
        
        assert scope.is_approval_required() == True
    
    def test_is_approval_required_with_gaps(self):
        """Test is_approval_required() returns True when gaps exist"""
        scope = ScopeBoundary(
            table_count=3,
            file_count=5,
            service_count=2,
            dependency_depth=1,
            estimated_complexity=75.0,
            confidence=0.95,  # High confidence
            gaps=["ambiguous reference: auth system"],  # But has gaps
            user_approved=True
        )
        
        assert scope.is_approval_required() == True
    
    def test_is_approval_required_not_approved(self):
        """Test is_approval_required() returns True when not user-approved"""
        scope = ScopeBoundary(
            table_count=3,
            file_count=5,
            service_count=2,
            dependency_depth=1,
            estimated_complexity=75.0,
            confidence=0.95,  # High confidence
            gaps=[],  # No gaps
            user_approved=False  # But not approved
        )
        
        assert scope.is_approval_required() == True
    
    def test_is_approval_required_all_conditions_met(self):
        """Test is_approval_required() returns False when all conditions met"""
        scope = ScopeBoundary(
            table_count=3,
            file_count=5,
            service_count=2,
            dependency_depth=1,
            estimated_complexity=75.0,
            confidence=0.95,  # High confidence (>= 80%)
            gaps=[],  # No gaps
            user_approved=True  # User approved
        )
        
        assert scope.is_approval_required() == False


class TestSwaggerContextStorage:
    """Test Tier 1 SWAGGER context storage"""
    
    @pytest.fixture
    def temp_working_memory(self, tmp_path):
        """Create temporary WorkingMemory for testing"""
        db_path = tmp_path / "test_working_memory.db"
        wm = WorkingMemory(db_path=db_path)
        yield wm
        # Cleanup handled by tmp_path fixture
    
    def test_store_swagger_context_success(self, temp_working_memory):
        """Test storing SWAGGER context"""
        context_id = "swagger-20251129-120000"
        context_data = {
            'context_id': context_id,
            'complexity': 85.0,
            'scope_boundary': {
                'table_count': 3,
                'file_count': 5,
                'service_count': 2,
                'dependency_depth': 1,
                'estimated_complexity': 85.0,
                'confidence': 0.75,
                'gaps': [],
                'user_approved': False,
                'entities': {
                    'tables': ['users', 'roles', 'permissions'],
                    'files': ['auth.py', 'login.py'],
                    'services': ['AuthService'],
                    'dependencies': ['bcrypt', 'JWT']
                }
            },
            'team_size': 1,
            'velocity': None,
            'created_at': datetime.now().isoformat(),
            'status': 'awaiting_approval'
        }
        
        result = temp_working_memory.store_swagger_context(context_id, context_data)
        
        assert result == True
    
    def test_retrieve_swagger_context_success(self, temp_working_memory):
        """Test retrieving stored SWAGGER context"""
        context_id = "swagger-20251129-120001"
        context_data = {
            'context_id': context_id,
            'complexity': 85.0,
            'scope_boundary': {
                'table_count': 3,
                'confidence': 0.75,
                'entities': {'tables': ['users']}
            },
            'team_size': 1,
            'velocity': None,
            'created_at': datetime.now().isoformat(),
            'status': 'awaiting_approval'
        }
        
        # Store context
        temp_working_memory.store_swagger_context(context_id, context_data)
        
        # Retrieve context
        retrieved = temp_working_memory.retrieve_swagger_context(context_id)
        
        assert retrieved is not None
        assert retrieved['context_id'] == context_id
        assert retrieved['complexity'] == 85.0
        assert retrieved['team_size'] == 1
        assert retrieved['status'] == 'awaiting_approval'
        
        # Verify scope_boundary is deserialized correctly
        scope_boundary = retrieved['scope_boundary']
        assert scope_boundary['table_count'] == 3
        assert scope_boundary['confidence'] == 0.75
    
    def test_retrieve_swagger_context_not_found(self, temp_working_memory):
        """Test retrieving non-existent SWAGGER context returns None"""
        result = temp_working_memory.retrieve_swagger_context("nonexistent-id")
        
        assert result is None
    
    def test_update_swagger_context_status_success(self, temp_working_memory):
        """Test updating SWAGGER context status"""
        context_id = "swagger-20251129-120002"
        context_data = {
            'context_id': context_id,
            'complexity': 85.0,
            'scope_boundary': {'table_count': 3},
            'team_size': 1,
            'velocity': None,
            'created_at': datetime.now().isoformat(),
            'status': 'awaiting_approval'
        }
        
        # Store context
        temp_working_memory.store_swagger_context(context_id, context_data)
        
        # Update status
        result = temp_working_memory.update_swagger_context_status(context_id, 'approved')
        
        assert result == True
        
        # Verify status updated
        retrieved = temp_working_memory.retrieve_swagger_context(context_id)
        assert retrieved['status'] == 'approved'
    
    def test_update_swagger_context_status_not_found(self, temp_working_memory):
        """Test updating non-existent context returns True (no error)"""
        # SQLite UPDATE with no matching rows returns success
        result = temp_working_memory.update_swagger_context_status("nonexistent-id", "approved")
        
        assert result == True  # No error, just no rows affected


class TestEstimationApprovalGate:
    """Test estimation blocking when scope unapproved"""
    
    @pytest.fixture
    def temp_orchestrator(self, tmp_path):
        """Create temporary PlanningOrchestrator for testing"""
        cortex_root = tmp_path / "CORTEX"
        cortex_root.mkdir()
        
        # Create required directories
        brain_path = cortex_root / "cortex-brain"
        brain_path.mkdir()
        (brain_path / "config").mkdir()
        (brain_path / "documents" / "planning" / "features" / "active").mkdir(parents=True)
        
        orchestrator = PlanningOrchestrator(cortex_root=str(cortex_root))
        yield orchestrator
    
    def test_estimate_timeframe_blocks_without_approval(self, temp_orchestrator):
        """Test estimate_timeframe() blocks when scope not approved"""
        scope_boundary = ScopeBoundary(
            table_count=3,
            file_count=5,
            service_count=2,
            dependency_depth=1,
            estimated_complexity=75.0,
            confidence=0.70,  # Below threshold
            gaps=[],
            user_approved=False  # NOT APPROVED
        )
        
        scope_boundary.entities = ScopeEntities(
            tables=['users', 'roles', 'permissions'],
            files=['auth.py', 'login.py'],
            services=['AuthService'],
            dependencies=['bcrypt']
        )
        
        result = temp_orchestrator.estimate_timeframe(
            complexity=75.0,
            scope=None,
            team_size=1,
            velocity=None,
            scope_boundary=scope_boundary
        )
        
        # Should return handoff response, NOT estimate
        assert result['status'] == 'scope_approval_required'
        assert 'swagger_context_id' in result
        assert result['next_action'] == 'plan'
        assert 'message' in result
        assert 'clarification_prompt' in result
        
        # Should NOT contain estimate fields
        assert 'story_points' not in result
        assert 'hours_single' not in result
    
    def test_estimate_timeframe_proceeds_with_approval(self, temp_orchestrator):
        """Test estimate_timeframe() proceeds when scope approved"""
        scope_boundary = ScopeBoundary(
            table_count=3,
            file_count=5,
            service_count=2,
            dependency_depth=1,
            estimated_complexity=75.0,
            confidence=0.95,  # High confidence
            gaps=[],
            user_approved=True  # APPROVED
        )
        
        scope_boundary.entities = ScopeEntities(
            tables=['users', 'roles', 'permissions'],
            files=['auth.py', 'login.py'],
            services=['AuthService'],
            dependencies=['bcrypt']
        )
        
        result = temp_orchestrator.estimate_timeframe(
            complexity=75.0,
            scope=None,
            team_size=1,
            velocity=None,
            scope_boundary=scope_boundary
        )
        
        # Should return estimate, NOT handoff
        assert 'status' not in result  # No blocking status
        assert 'story_points' in result
        assert 'hours_single' in result
        assert 'hours_team' in result
        assert 'days_single' in result
        assert 'sprints' in result
        assert 'report' in result
    
    def test_estimate_timeframe_legacy_call_without_scope_boundary(self, temp_orchestrator):
        """Test legacy call without scope_boundary creates unapproved boundary"""
        # Legacy call (no scope_boundary parameter)
        result = temp_orchestrator.estimate_timeframe(
            complexity=75.0,
            scope={'tables': ['users'], 'files': ['auth.py']},
            team_size=1
        )
        
        # Should block - legacy calls treated as unapproved
        assert result['status'] == 'scope_approval_required'
        assert 'swagger_context_id' in result


class TestPlannerHandoffWorkflow:
    """Test planner handoff and context preservation"""
    
    @pytest.fixture
    def temp_orchestrator_with_storage(self, tmp_path):
        """Create orchestrator with working memory"""
        cortex_root = tmp_path / "CORTEX"
        cortex_root.mkdir()
        
        # Create required directories
        brain_path = cortex_root / "cortex-brain"
        brain_path.mkdir()
        (brain_path / "config").mkdir()
        (brain_path / "documents" / "planning" / "features" / "active").mkdir(parents=True)
        (brain_path / "tier1").mkdir()
        
        orchestrator = PlanningOrchestrator(cortex_root=str(cortex_root))
        yield orchestrator
    
    def test_handoff_stores_swagger_context(self, temp_orchestrator_with_storage):
        """Test _hand_off_to_planner_for_approval() stores context"""
        scope_boundary = ScopeBoundary(
            table_count=3,
            file_count=5,
            service_count=2,
            dependency_depth=1,
            estimated_complexity=75.0,
            confidence=0.70,
            gaps=[],
            user_approved=False
        )
        
        scope_boundary.entities = ScopeEntities(
            tables=['users'],
            files=['auth.py'],
            services=['AuthService'],
            dependencies=['bcrypt']
        )
        
        result = temp_orchestrator_with_storage._hand_off_to_planner_for_approval(
            complexity=75.0,
            scope_boundary=scope_boundary,
            scope=None,
            team_size=1,
            velocity=None
        )
        
        # Verify handoff response
        assert result['status'] == 'scope_approval_required'
        assert 'swagger_context_id' in result
        context_id = result['swagger_context_id']
        
        # Verify context was stored
        from src.tier1.working_memory import WorkingMemory
        wm = WorkingMemory()
        stored_context = wm.retrieve_swagger_context(context_id)
        
        assert stored_context is not None
        assert stored_context['complexity'] == 75.0
        assert stored_context['team_size'] == 1
        assert stored_context['status'] == 'awaiting_approval'
    
    def test_resume_estimation_retrieves_context(self, temp_orchestrator_with_storage):
        """Test resume_estimation_with_approved_scope() retrieves stored context"""
        # Step 1: Block estimation and store context
        scope_boundary = ScopeBoundary(
            table_count=3,
            file_count=5,
            service_count=2,
            dependency_depth=1,
            estimated_complexity=75.0,
            confidence=0.70,
            gaps=[],
            user_approved=False
        )
        
        scope_boundary.entities = ScopeEntities(
            tables=['users'],
            files=['auth.py'],
            services=['AuthService'],
            dependencies=['bcrypt']
        )
        
        handoff_result = temp_orchestrator_with_storage._hand_off_to_planner_for_approval(
            complexity=75.0,
            scope_boundary=scope_boundary,
            scope=None,
            team_size=1,
            velocity=None
        )
        
        context_id = handoff_result['swagger_context_id']
        
        # Step 2: Resume estimation with approved scope
        resume_result = temp_orchestrator_with_storage.resume_estimation_with_approved_scope(
            swagger_context_id=context_id,
            approved_scope=None  # Use existing scope
        )
        
        # Should now return estimate (scope was approved in resume method)
        assert 'story_points' in resume_result
        assert 'hours_single' in resume_result
        assert 'report' in resume_result
    
    def test_resume_estimation_with_nonexistent_context(self, temp_orchestrator_with_storage):
        """Test resume_estimation_with_approved_scope() handles missing context"""
        result = temp_orchestrator_with_storage.resume_estimation_with_approved_scope(
            swagger_context_id="nonexistent-context-id"
        )
        
        assert result['success'] == False
        assert 'error' in result
        assert 'not found' in result['error'].lower()


class TestClarificationPromptGeneration:
    """Test scope clarification prompt generation"""
    
    @pytest.fixture
    def temp_orchestrator(self, tmp_path):
        """Create temporary orchestrator"""
        cortex_root = tmp_path / "CORTEX"
        cortex_root.mkdir()
        
        brain_path = cortex_root / "cortex-brain"
        brain_path.mkdir()
        (brain_path / "config").mkdir()
        (brain_path / "documents" / "planning" / "features" / "active").mkdir(parents=True)
        
        orchestrator = PlanningOrchestrator(cortex_root=str(cortex_root))
        yield orchestrator
    
    def test_clarification_prompt_with_entities(self, temp_orchestrator):
        """Test _generate_scope_clarification_prompt() with full entities"""
        scope_boundary = ScopeBoundary(
            table_count=3,
            file_count=5,
            service_count=2,
            dependency_depth=1,
            estimated_complexity=75.0,
            confidence=0.85,
            gaps=[]
        )
        
        scope_boundary.entities = ScopeEntities(
            tables=['users', 'roles', 'permissions'],
            files=['auth.py', 'login.py', 'session.py'],
            services=['AuthService', 'SessionManager'],
            dependencies=['bcrypt', 'JWT']
        )
        
        prompt = temp_orchestrator._generate_scope_clarification_prompt(
            scope_boundary=scope_boundary,
            scope=None,
            confidence=0.85
        )
        
        assert "Inferred Scope (Confidence: 85%)" in prompt
        assert "users, roles, permissions" in prompt
        assert "auth.py, login.py, session.py" in prompt
        assert "AuthService, SessionManager" in prompt
        assert "bcrypt, JWT" in prompt
        assert "Does this scope accurately represent" in prompt
    
    def test_clarification_prompt_with_gaps(self, temp_orchestrator):
        """Test _generate_scope_clarification_prompt() with ambiguous gaps"""
        scope_boundary = ScopeBoundary(
            table_count=3,
            file_count=5,
            service_count=2,
            dependency_depth=1,
            estimated_complexity=75.0,
            confidence=0.65,
            gaps=["ambiguous: auth system", "unclear: session management"]
        )
        
        scope_boundary.entities = ScopeEntities(
            tables=['users'],
            files=['auth.py'],
            services=[],
            dependencies=[]
        )
        
        prompt = temp_orchestrator._generate_scope_clarification_prompt(
            scope_boundary=scope_boundary,
            scope=None,
            confidence=0.65
        )
        
        assert "Ambiguous References" in prompt
        assert "ambiguous: auth system" in prompt
        assert "unclear: session management" in prompt
        assert "Questions:" in prompt


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
