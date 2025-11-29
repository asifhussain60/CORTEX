"""
Integration Tests for Feature 5 Phase 3: Intelligent Auto-Detection

Tests the complete flow:
1. Quality Monitor detects valuable conversation
2. Smart Hint Generator creates prompt
3. User responds (accept/reject/ignore)
4. Tier 2 Learning adapts threshold

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path
from src.operations.modules.conversations.quality_monitor import QualityMonitor
from src.operations.modules.conversations.smart_hint_generator import SmartHintGenerator
from src.operations.modules.conversations.tier2_learning import Tier2LearningIntegration


class TestPhase3Integration:
    """Integration tests for complete Phase 3 workflow."""
    
    @pytest.fixture
    def temp_storage(self):
        """Create temporary storage for learning data."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)
        yield temp_path
        if temp_path.exists():
            temp_path.unlink()
    
    @pytest.fixture
    def integrated_system(self, temp_storage):
        """Create integrated system with all components."""
        monitor = QualityMonitor(min_turns_before_check=2, quality_threshold="GOOD")
        generator = SmartHintGenerator(quality_threshold="GOOD")
        learner = Tier2LearningIntegration(storage_path=temp_storage, min_samples_for_learning=5)
        
        return {
            'monitor': monitor,
            'generator': generator,
            'learner': learner
        }
    
    def test_end_to_end_high_quality_conversation_accepted(self, integrated_system):
        """Test complete flow with high-quality conversation accepted by user."""
        monitor = integrated_system['monitor']
        generator = integrated_system['generator']
        learner = integrated_system['learner']
        
        # Step 1: User has strategic conversation
        monitor.start_session("session-001")
        
        result1 = monitor.add_turn(
            user_message="Let's plan the authentication feature",
            assistant_response="""
            🎯 Understanding: Implement user authentication
            
            ⚠️ **Challenge:** ✓ **Accept**
            
            💬 **Response:** I'll implement authentication with these phases:
            
            Phase 1: Backend API
            Phase 2: UI Integration
            Phase 3: Testing
            
            Files: `auth_service.py`, `api/routes.py`
            
            🔍 Next Steps:
               1. Design authentication flow
               2. Implement JWT tokens
            """
        )
        
        # Step 2: Quality check triggers after 2 turns
        result2 = monitor.add_turn(
            user_message="Great, let's start with Phase 1",
            assistant_response="Starting backend implementation..."
        )
        
        assert result2['should_check_quality'] is True
        assert result2['quality_level'] in ['GOOD', 'EXCELLENT']
        assert result2['should_show_hint'] is True
        
        # Step 3: Generate Smart Hint
        quality_score = monitor.get_current_quality()
        hint = generator.generate_hint(quality_score, hint_already_shown=False)
        
        assert hint.should_display is True
        assert "💡 CORTEX Learning Opportunity" in hint.content
        assert "/CORTEX Capture this conversation" in hint.content
        
        # Step 4: User accepts hint
        monitor.record_user_response('accepted')
        learner.record_response(
            session_id="session-001",
            response='accepted',
            quality_score=quality_score.total_score,
            quality_level=quality_score.level
        )
        
        # Verify learning recorded
        assert len(learner.responses) == 1
        assert learner.responses[0].response == 'accepted'
    
    def test_end_to_end_low_quality_no_hint(self, integrated_system):
        """Test complete flow with low-quality conversation (no hint shown)."""
        monitor = integrated_system['monitor']
        generator = integrated_system['generator']
        
        # Step 1: Simple low-quality conversation
        monitor.start_session("session-002")
        
        monitor.add_turn(
            user_message="Hi",
            assistant_response="Hello! How can I help you?"
        )
        
        result = monitor.add_turn(
            user_message="Thanks",
            assistant_response="You're welcome!"
        )
        
        # Step 2: Quality check shows LOW quality
        assert result['should_check_quality'] is True
        assert result['quality_level'] in ['LOW', 'FAIR']
        assert result['should_show_hint'] is False
        
        # Step 3: Smart Hint should not be generated
        quality_score = monitor.get_current_quality()
        hint = generator.generate_hint(quality_score, hint_already_shown=False)
        
        assert hint.should_display is False
        assert hint.content == ""
    
    def test_hint_shown_only_once_per_session(self, integrated_system):
        """Test hint shown only once per session even with continued high quality."""
        monitor = integrated_system['monitor']
        generator = integrated_system['generator']
        
        monitor.start_session("session-003")
        
        # First strategic exchange - needs more elements to reach GOOD (10+ points)
        monitor.add_turn(
            user_message="Plan feature X",
            assistant_response="""
            ⚠️ **Challenge:** ✓ **Accept**
            
            Phase 1: Design
            Phase 2: Implementation
            Phase 3: Testing
            
            Files: `feature.py`, `test_feature.py`
            
            🔍 Next Steps:
               1. Task 1
               2. Task 2
            """
        )
        
        result1 = monitor.add_turn(
            user_message="Continue",
            assistant_response="Implementing..."
        )
        
        # Should show hint first time (now has 3 phases=9pts + challenge=3pts + files=2pts + next steps=2pts = 16pts GOOD)
        assert result1['should_show_hint'] is True
        
        quality1 = monitor.get_current_quality()
        hint1 = generator.generate_hint(quality1, hint_already_shown=False)
        assert hint1.should_display is True
        
        # Mark as shown
        monitor.record_user_response('ignored')
        
        # More strategic content
        result2 = monitor.add_turn(
            user_message="Add more features",
            assistant_response="""
            Phase 3: Additional features
            Phase 4: Polish
            """
        )
        
        # Should not show hint again (already shown)
        assert result2['should_show_hint'] is False
        
        quality2 = monitor.get_current_quality()
        hint2 = generator.generate_hint(quality2, hint_already_shown=True)
        assert hint2.should_display is False
    
    def test_threshold_adaptation_high_acceptance(self, integrated_system):
        """Test threshold adapts lower with high acceptance rate."""
        learner = integrated_system['learner']
        
        # Simulate 5 sessions with high acceptance (80%)
        for i in range(5):
            learner.record_response(
                session_id=f"session-{i}",
                response='accepted' if i < 4 else 'rejected',
                quality_score=20,
                quality_level='EXCELLENT'
            )
        
        # Check recommendation
        recommendation = learner.recommend_threshold_adjustment('EXCELLENT')
        
        assert recommendation is not None
        assert recommendation.recommended_threshold == 'GOOD'
        assert 'High acceptance rate' in recommendation.reasoning
    
    def test_threshold_adaptation_low_acceptance(self, integrated_system):
        """Test threshold adapts higher with low acceptance rate."""
        learner = integrated_system['learner']
        
        # Simulate 5 sessions with low acceptance (20%)
        for i in range(5):
            learner.record_response(
                session_id=f"session-{i}",
                response='accepted' if i == 0 else 'rejected',
                quality_score=14,
                quality_level='GOOD'
            )
        
        # Check recommendation
        recommendation = learner.recommend_threshold_adjustment('GOOD')
        
        assert recommendation is not None
        assert recommendation.recommended_threshold == 'EXCELLENT'
        assert 'Low acceptance rate' in recommendation.reasoning
    
    def test_multi_session_learning_convergence(self, integrated_system):
        """Test learning converges over multiple sessions."""
        monitor = integrated_system['monitor']
        generator = integrated_system['generator']
        learner = integrated_system['learner']
        
        # Simulate 10 sessions with varying responses - ensure GOOD quality (10+ points)
        for session_num in range(10):
            monitor.start_session(f"session-{session_num}")
            
            # Strategic conversation with enough elements for GOOD (10+ points)
            monitor.add_turn(
                user_message=f"Plan feature {session_num}",
                assistant_response=f"""
                ⚠️ **Challenge:** ✓ **Accept**
                
                Phase 1: Design feature {session_num}
                Phase 2: Implement feature {session_num}
                Phase 3: Test feature {session_num}
                
                Files: `feature{session_num}.py`, `test_{session_num}.py`
                
                🔍 Next Steps:
                   1. Start implementation
                   2. Write tests
                """
            )
            
            result = monitor.add_turn(
                user_message="Proceed",
                assistant_response="Starting..."
            )
            
            if result['should_show_hint']:
                quality = monitor.get_current_quality()
                hint = generator.generate_hint(quality, hint_already_shown=False)
                
                if hint.should_display:
                    # User accepts 70% of the time
                    response = 'accepted' if session_num % 10 < 7 else 'rejected'
                    
                    monitor.record_user_response(response)
                    learner.record_response(
                        session_id=f"session-{session_num}",
                        response=response,
                        quality_score=quality.total_score,
                        quality_level=quality.level
                    )
            
            monitor.end_session()
        
        # Verify learning occurred
        stats = learner.get_response_stats()
        assert stats['total_responses'] == 10
        
        # With 70% acceptance, threshold should stay at GOOD
        recommendation = learner.recommend_threshold_adjustment('GOOD')
        assert recommendation.recommended_threshold == 'GOOD'
        assert 'balanced' in recommendation.reasoning.lower() or 'High acceptance' in recommendation.reasoning
    
    def test_session_stats_tracking(self, integrated_system):
        """Test session statistics are tracked correctly."""
        monitor = integrated_system['monitor']
        learner = integrated_system['learner']
        
        # Run 3 sessions with different outcomes - ensure GOOD quality (10+ points)
        for i, response in enumerate(['accepted', 'rejected', 'ignored']):
            monitor.start_session(f"session-{i}")
            
            monitor.add_turn(
                user_message="Question",
                assistant_response="""
                ⚠️ **Challenge:** ✓ **Accept**
                
                Phase 1: Analysis
                Phase 2: Implementation
                Phase 3: Testing
                
                Files: `main.py`, `test.py`
                
                🔍 Next Steps:
                   1. Step 1
                   2. Step 2
                """
            )
            
            result = monitor.add_turn(
                user_message="Continue",
                assistant_response="Proceeding..."
            )
            
            if result['should_show_hint']:
                quality = monitor.get_current_quality()
                monitor.record_user_response(response)
                learner.record_response(
                    session_id=f"session-{i}",
                    response=response,
                    quality_score=quality.total_score,
                    quality_level=quality.level
                )
            
            monitor.end_session()
        
        # Check monitor stats
        monitor_stats = monitor.get_session_stats()
        assert monitor_stats['total_sessions'] == 3
        
        # Check learner stats
        learner_stats = learner.get_response_stats()
        assert learner_stats['total_responses'] == 3
        assert learner_stats['accepted'] == 1
        assert learner_stats['rejected'] == 1
        assert learner_stats['ignored'] == 1
    
    def test_persistence_across_restarts(self, temp_storage, integrated_system):
        """Test learning data persists across system restarts."""
        learner1 = integrated_system['learner']
        
        # Record some responses
        learner1.record_response("s1", "accepted", 14, "GOOD")
        learner1.record_response("s2", "rejected", 15, "GOOD")
        
        # Create new learner instance (simulates restart)
        learner2 = Tier2LearningIntegration(storage_path=temp_storage)
        
        # Should have loaded previous data
        assert len(learner2.responses) == 2
        assert learner2.get_acceptance_rate() == 0.5
    
    def test_excellent_quality_conversation_flow(self, integrated_system):
        """Test flow with EXCELLENT quality conversation."""
        monitor = integrated_system['monitor']
        generator = integrated_system['generator']
        
        monitor.start_session("excellent-session")
        
        # Highly strategic conversation
        monitor.add_turn(
            user_message="Design the complete authentication system",
            assistant_response="""
            🎯 Understanding: Complete auth system design
            
            ⚠️ **Challenge:** ✓ **Accept**
            
            💬 **Response:** Multi-phase implementation:
            
            Phase 1: Core Authentication
            Phase 2: Authorization Layer
            Phase 3: Session Management
            Phase 4: Security Hardening
            Phase 5: Audit Logging
            
            Files: `auth_service.py`, `user_model.py`, `session_manager.py`, 
                   `security_config.py`, `audit_logger.py`
            
            Design decisions:
            - JWT vs Session tokens (chose JWT for stateless)
            - bcrypt hashing for passwords
            - Redis for session storage
            
            Architecture: Layered approach with clear separation
            
            🔍 Next Steps:
               1. Set up authentication database schema
               2. Implement core auth service
               3. Add middleware for route protection
               4. Create comprehensive security tests
            """
        )
        
        result = monitor.add_turn(
            user_message="Excellent plan, let's proceed",
            assistant_response="Starting Phase 1..."
        )
        
        # Should be EXCELLENT quality
        assert result['quality_level'] == 'EXCELLENT'
        assert result['should_show_hint'] is True
        
        # Verify high score
        quality = monitor.get_current_quality()
        assert quality.total_score >= 19  # EXCELLENT threshold
        
        # Generate hint
        hint = generator.generate_hint(quality, hint_already_shown=False)
        assert hint.should_display is True
        assert "strategic value" in hint.content.lower()
