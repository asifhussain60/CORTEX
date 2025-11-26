"""
Tests for IncrementalPlanGenerator

Purpose: Validate token-budgeted planning generation
Coverage: Skeleton generation, section filling, checkpoint system, token limits

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from src.workflows.incremental_plan_generator import (
    IncrementalPlanGenerator,
    PlanSection,
    PlanCheckpoint
)


@pytest.fixture
def brain_path(tmp_path):
    """Create temporary brain directory for testing"""
    brain = tmp_path / "cortex-brain"
    brain.mkdir()
    return brain


@pytest.fixture
def generator(brain_path):
    """Create IncrementalPlanGenerator instance"""
    return IncrementalPlanGenerator(
        brain_path=brain_path,
        skeleton_token_limit=200,
        section_token_limit=500
    )


@pytest.fixture
def sample_requirements():
    """Sample feature requirements for testing"""
    return {
        'feature_name': 'User Authentication',
        'description': 'Implement secure user login and session management',
        'priority': 'high',
        'dependencies': ['Database', 'Encryption Library']
    }


class TestIncrementalPlanGenerator:
    """Test suite for IncrementalPlanGenerator"""
    
    def test_initialization(self, generator, brain_path):
        """Test generator initializes with correct configuration"""
        assert generator.brain_path == brain_path
        assert generator.session_id.startswith('plan-')
        assert generator.skeleton_token_limit == 200
        assert generator.section_token_limit == 500
        assert generator.current_phase == 'not_started'
        assert generator.skeleton is None
        assert len(generator.sections) == 0
        assert len(generator.checkpoints) == 0
    
    def test_custom_token_limits(self, brain_path):
        """Test generator accepts custom token limits"""
        generator = IncrementalPlanGenerator(
            brain_path=brain_path,
            skeleton_token_limit=300,
            section_token_limit=600
        )
        
        assert generator.skeleton_token_limit == 300
        assert generator.section_token_limit == 600
    
    def test_count_tokens(self, generator):
        """Test token counting approximation"""
        # 1 token ≈ 4 characters
        text_16_chars = "This is 16 chars"
        assert generator.count_tokens(text_16_chars) == 4
        
        text_100_chars = "x" * 100
        assert generator.count_tokens(text_100_chars) == 25
    
    def test_generate_skeleton(self, generator, sample_requirements):
        """Test skeleton generation within token limit"""
        skeleton, token_count = generator.generate_skeleton(sample_requirements)
        
        # Verify skeleton structure
        assert skeleton['feature_name'] == 'User Authentication'
        assert len(skeleton['phases']) == 3
        assert skeleton['checkpoint_count'] == 4
        
        # Verify phases
        phase_names = [p['name'] for p in skeleton['phases']]
        assert 'Phase 1: Foundation' in phase_names
        assert 'Phase 2: Core Implementation' in phase_names
        assert 'Phase 3: Validation' in phase_names
        
        # Verify token limit respected
        assert token_count <= generator.skeleton_token_limit
        
        # Verify state updated
        assert generator.skeleton == skeleton
        assert generator.current_phase == 'skeleton_complete'
    
    def test_generate_skeleton_without_feature_name(self, generator):
        """Test skeleton generation with missing feature name"""
        skeleton, token_count = generator.generate_skeleton({})
        
        assert skeleton['feature_name'] == 'Unnamed Feature'
        assert token_count <= generator.skeleton_token_limit
    
    def test_fill_section(self, generator, sample_requirements):
        """Test section filling within token limit"""
        context = {
            'description': 'Define user authentication requirements',
            'feature_name': 'User Authentication'
        }
        
        section, needs_checkpoint = generator.fill_section(
            section_name='Requirements',
            context=context
        )
        
        # Verify section structure
        assert section.name == 'Requirements'
        assert section.status == 'complete'
        assert section.token_count > 0
        assert section.token_count <= generator.section_token_limit
        
        # Verify section stored
        assert 'Requirements' in generator.sections
        assert generator.sections['Requirements'] == section
    
    def test_fill_section_triggers_checkpoint(self, generator):
        """Test section filling triggers checkpoint at phase boundaries"""
        context = {'description': 'Architecture design'}
        
        # 'Architecture' is a phase-ending section
        section, needs_checkpoint = generator.fill_section(
            section_name='Architecture',
            context=context
        )
        
        assert needs_checkpoint is True
    
    def test_fill_section_no_checkpoint(self, generator):
        """Test section filling without checkpoint trigger"""
        context = {'description': 'Requirements documentation'}
        
        # 'Requirements' is not a phase-ending section
        section, needs_checkpoint = generator.fill_section(
            section_name='Requirements',
            context=context
        )
        
        assert needs_checkpoint is False
    
    def test_fill_section_custom_token_limit(self, generator):
        """Test section filling with custom token limit"""
        context = {'description': 'Test content'}
        
        section, _ = generator.fill_section(
            section_name='Test Section',
            context=context,
            max_tokens=100
        )
        
        # Should respect custom limit
        assert section.token_count <= 100
    
    def test_create_checkpoint(self, generator, sample_requirements):
        """Test checkpoint creation"""
        # Fill some sections first
        generator.fill_section('Requirements', {'description': 'Test'})
        generator.fill_section('Dependencies', {'description': 'Test'})
        
        checkpoint = generator.create_checkpoint(
            section_name='Dependencies',
            content_preview='This is a preview of the dependencies section content...'
        )
        
        # Verify checkpoint structure
        assert checkpoint.checkpoint_id == 'cp-1'
        assert checkpoint.section_name == 'Dependencies'
        assert checkpoint.status == 'pending_approval'
        assert len(checkpoint.content_preview) <= 200
        assert checkpoint.token_count > 0
        
        # Verify checkpoint stored
        assert len(generator.checkpoints) == 1
        assert generator.checkpoints[0] == checkpoint
    
    def test_multiple_checkpoints(self, generator):
        """Test creating multiple checkpoints"""
        generator.fill_section('Section 1', {'description': 'Test'})
        cp1 = generator.create_checkpoint('Section 1', 'Preview 1')
        
        generator.fill_section('Section 2', {'description': 'Test'})
        cp2 = generator.create_checkpoint('Section 2', 'Preview 2')
        
        assert len(generator.checkpoints) == 2
        assert cp1.checkpoint_id == 'cp-1'
        assert cp2.checkpoint_id == 'cp-2'
        assert cp2.token_count > cp1.token_count  # Cumulative tokens
    
    def test_approve_checkpoint(self, generator):
        """Test checkpoint approval"""
        generator.fill_section('Test Section', {'description': 'Test'})
        checkpoint = generator.create_checkpoint('Test Section', 'Preview')
        
        result = generator.approve_checkpoint('cp-1', feedback='Looks good')
        
        assert result is True
        assert checkpoint.status == 'approved'
        assert checkpoint.feedback == 'Looks good'
    
    def test_approve_nonexistent_checkpoint(self, generator):
        """Test approving checkpoint that doesn't exist"""
        result = generator.approve_checkpoint('cp-999')
        
        assert result is False
    
    def test_reject_checkpoint(self, generator):
        """Test checkpoint rejection"""
        generator.fill_section('Test Section', {'description': 'Test'})
        checkpoint = generator.create_checkpoint('Test Section', 'Preview')
        
        result = generator.reject_checkpoint('cp-1', reason='Needs more detail')
        
        assert result is True
        assert checkpoint.status == 'rejected'
        assert checkpoint.feedback == 'Needs more detail'
    
    def test_reject_nonexistent_checkpoint(self, generator):
        """Test rejecting checkpoint that doesn't exist"""
        result = generator.reject_checkpoint('cp-999', reason='Does not exist')
        
        assert result is False
    
    def test_get_status(self, generator, sample_requirements):
        """Test status reporting"""
        # Initial status
        status = generator.get_status()
        assert status['current_phase'] == 'not_started'
        assert status['total_tokens'] == 0
        assert status['completed_sections'] == 0
        assert status['checkpoints'] == 0
        
        # After skeleton
        generator.generate_skeleton(sample_requirements)
        status = generator.get_status()
        assert status['current_phase'] == 'skeleton_complete'
        assert status['total_sections'] == 9  # 3 phases × 3 sections
        
        # After filling sections
        generator.fill_section('Requirements', {'description': 'Test'})
        generator.fill_section('Dependencies', {'description': 'Test'})
        
        status = generator.get_status()
        assert status['completed_sections'] == 2
        assert status['total_tokens'] > 0
        
        # After checkpoint
        generator.create_checkpoint('Dependencies', 'Preview')
        status = generator.get_status()
        assert status['checkpoints'] == 1
        assert status['pending_approvals'] == 1
        
        # After approval
        generator.approve_checkpoint('cp-1')
        status = generator.get_status()
        assert status['pending_approvals'] == 0
    
    def test_session_id_generation(self, brain_path):
        """Test unique session ID generation"""
        gen1 = IncrementalPlanGenerator(brain_path)
        gen2 = IncrementalPlanGenerator(brain_path)
        
        assert gen1.session_id != gen2.session_id
        assert gen1.session_id.startswith('plan-')
        assert gen2.session_id.startswith('plan-')
    
    def test_custom_session_id(self, brain_path):
        """Test generator accepts custom session ID"""
        generator = IncrementalPlanGenerator(
            brain_path=brain_path,
            session_id='custom-session-123'
        )
        
        assert generator.session_id == 'custom-session-123'
    
    def test_skeleton_serialization(self, generator, sample_requirements):
        """Test skeleton serialization for token counting"""
        skeleton, _ = generator.generate_skeleton(sample_requirements)
        serialized = generator._serialize_skeleton(skeleton)
        
        # Verify format
        assert 'User Authentication' in serialized
        assert 'Phase 1: Foundation' in serialized
        assert 'Requirements' in serialized
        assert 'Dependencies' in serialized
        
        # Verify can be counted
        token_count = generator.count_tokens(serialized)
        assert token_count > 0


class TestPlanSection:
    """Test suite for PlanSection dataclass"""
    
    def test_plan_section_creation(self):
        """Test PlanSection initialization"""
        section = PlanSection(
            name='Test Section',
            content='Test content',
            token_count=100,
            status='complete'
        )
        
        assert section.name == 'Test Section'
        assert section.content == 'Test content'
        assert section.token_count == 100
        assert section.status == 'complete'
        assert section.subsections == []
    
    def test_plan_section_with_subsections(self):
        """Test PlanSection with nested subsections"""
        subsection = PlanSection(
            name='Subsection',
            content='Sub content',
            token_count=50,
            status='complete'
        )
        
        section = PlanSection(
            name='Main Section',
            content='Main content',
            token_count=150,
            status='complete',
            subsections=[subsection]
        )
        
        assert len(section.subsections) == 1
        assert section.subsections[0].name == 'Subsection'


class TestPlanCheckpoint:
    """Test suite for PlanCheckpoint dataclass"""
    
    def test_checkpoint_creation(self):
        """Test PlanCheckpoint initialization"""
        checkpoint = PlanCheckpoint(
            checkpoint_id='cp-1',
            section_name='Test Section',
            content_preview='This is a preview...',
            token_count=250,
            status='pending_approval'
        )
        
        assert checkpoint.checkpoint_id == 'cp-1'
        assert checkpoint.section_name == 'Test Section'
        assert checkpoint.content_preview == 'This is a preview...'
        assert checkpoint.token_count == 250
        assert checkpoint.status == 'pending_approval'
        assert checkpoint.feedback is None
    
    def test_checkpoint_with_feedback(self):
        """Test PlanCheckpoint with feedback"""
        checkpoint = PlanCheckpoint(
            checkpoint_id='cp-1',
            section_name='Test Section',
            content_preview='Preview',
            token_count=100,
            status='approved',
            feedback='Looks great!'
        )
        
        assert checkpoint.feedback == 'Looks great!'


class TestIntegrationScenarios:
    """Integration tests for complete workflows"""
    
    def test_complete_planning_workflow(self, generator, sample_requirements):
        """Test complete planning workflow from skeleton to completion"""
        # Step 1: Generate skeleton
        skeleton, _ = generator.generate_skeleton(sample_requirements)
        assert generator.current_phase == 'skeleton_complete'
        
        # Step 2: Fill Phase 1 sections
        for section_name in ['Requirements', 'Dependencies', 'Architecture']:
            section, needs_checkpoint = generator.fill_section(
                section_name, 
                {'description': f'{section_name} content'}
            )
            
            if needs_checkpoint:
                cp = generator.create_checkpoint(section_name, section.content)
                generator.approve_checkpoint(cp.checkpoint_id)
        
        # Step 3: Fill Phase 2 sections
        for section_name in ['Implementation Plan', 'Test Strategy', 'Integration Points']:
            section, needs_checkpoint = generator.fill_section(
                section_name,
                {'description': f'{section_name} content'}
            )
            
            if needs_checkpoint:
                cp = generator.create_checkpoint(section_name, section.content)
                generator.approve_checkpoint(cp.checkpoint_id)
        
        # Step 4: Fill Phase 3 sections
        for section_name in ['Acceptance Criteria', 'Security Review', 'Deployment Plan']:
            section, needs_checkpoint = generator.fill_section(
                section_name,
                {'description': f'{section_name} content'}
            )
            
            if needs_checkpoint:
                cp = generator.create_checkpoint(section_name, section.content)
                generator.approve_checkpoint(cp.checkpoint_id)
        
        # Verify completion
        status = generator.get_status()
        assert status['completed_sections'] == 9
        assert status['pending_approvals'] == 0
        assert all(cp.status == 'approved' for cp in generator.checkpoints)
    
    def test_checkpoint_rejection_workflow(self, generator, sample_requirements):
        """Test workflow with checkpoint rejection"""
        generator.generate_skeleton(sample_requirements)
        
        # Fill section
        section, _ = generator.fill_section(
            'Requirements',
            {'description': 'Initial requirements'}
        )
        
        # Create checkpoint and reject
        cp = generator.create_checkpoint('Requirements', section.content)
        result = generator.reject_checkpoint(
            cp.checkpoint_id,
            reason='Needs more specific acceptance criteria'
        )
        
        assert result is True
        assert cp.status == 'rejected'
        assert 'acceptance criteria' in cp.feedback
        
        # In real workflow, this would trigger regeneration
        # For now, verify state is correct for retry
        status = generator.get_status()
        assert status['pending_approvals'] == 0  # Rejected, not pending
