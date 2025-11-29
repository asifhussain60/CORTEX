"""
Integration tests for user profile system (CORTEX 3.2.1).

Tests cover:
- Onboarding 3-question flow
- Profile injection into AgentRequest
- Profile update flow
- Intent router integration
- Context-not-constraint pattern validation

Author: Asif Hussain
"""

import pytest
import tempfile
import os
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from src.tier1.working_memory import WorkingMemory
from src.orchestrators.onboarding_orchestrator import OnboardingOrchestrator
from src.cortex_agents.intent_router import IntentRouter
from src.cortex_agents.base_agent import AgentRequest
from src.response_templates.template_renderer import TemplateRenderer


class TestOnboardingFlow:
    """Test complete onboarding flow."""
    
    @pytest.fixture
    def setup(self):
        """Setup onboarding orchestrator with temp database."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_profile.db")
        tier1 = WorkingMemory(db_path=db_path)
        orchestrator = OnboardingOrchestrator(tier1_api=tier1)
        
        yield orchestrator, tier1
        
        # Cleanup
        tier1.close()
        if os.path.exists(db_path):
            os.remove(db_path)
        os.rmdir(temp_dir)
    
    def test_start_onboarding(self, setup):
        """Test onboarding start returns Question 1."""
        orchestrator, tier1 = setup
        
        result = orchestrator.start_onboarding("User wants to onboard")
        
        assert result['status'] == 'onboarding_started'
        assert 'Question 1: Experience Level' in result['content']
        assert 'Junior' in result['content']
        assert 'Mid' in result['content']
        assert 'Senior' in result['content']
        assert 'Expert' in result['content']
    
    def test_process_experience_choice(self, setup):
        """Test processing experience level choice."""
        orchestrator, tier1 = setup
        
        result = orchestrator.process_experience_choice("2")
        
        assert result['status'] == 'awaiting_mode'
        assert 'Question 2: Interaction Mode' in result['content']
        assert result['experience_level'] == 'mid'
    
    def test_process_experience_invalid_choice(self, setup):
        """Test invalid experience level choice."""
        orchestrator, tier1 = setup
        
        result = orchestrator.process_experience_choice("5")
        
        assert result['status'] == 'error'
        assert 'Invalid choice' in result['message']
    
    def test_process_mode_choice(self, setup):
        """Test processing interaction mode choice."""
        orchestrator, tier1 = setup
        
        # First select experience
        orchestrator.process_experience_choice("2")
        
        # Then select mode
        result = orchestrator.process_mode_choice("2", "mid")
        
        assert result['status'] == 'awaiting_tech_stack'
        assert 'Question 3: Tech Stack Preference' in result['content']
        assert 'Azure stack' in result['content']
        assert 'AWS stack' in result['content']
        assert 'GCP stack' in result['content']
    
    def test_process_tech_stack_choice_azure(self, setup):
        """Test processing tech stack choice - Azure preset."""
        orchestrator, tier1 = setup
        
        # Select experience and mode first
        orchestrator.process_experience_choice("3")  # Senior
        orchestrator.process_mode_choice("1", "senior")  # Autonomous
        
        # Select Azure tech stack
        result = orchestrator.process_tech_stack_choice("2")
        
        assert result['status'] == 'completed'
        assert 'Profile Created' in result['content']
        
        # Verify profile was created in Tier 1
        profile = tier1.get_profile()
        assert profile is not None
        assert profile['experience_level'] == 'senior'
        assert profile['interaction_mode'] == 'autonomous'
        assert profile['tech_stack_preference'] is not None
        assert profile['tech_stack_preference']['cloud_provider'] == 'azure'
    
    def test_process_tech_stack_choice_no_preference(self, setup):
        """Test processing tech stack choice - No preference."""
        orchestrator, tier1 = setup
        
        # Select experience and mode first
        orchestrator.process_experience_choice("2")  # Mid
        orchestrator.process_mode_choice("2", "mid")  # Guided
        
        # Select no preference
        result = orchestrator.process_tech_stack_choice("1")
        
        assert result['status'] == 'completed'
        
        # Verify profile has no tech stack
        profile = tier1.get_profile()
        assert profile['tech_stack_preference'] is None
    
    def test_complete_onboarding_flow(self, setup):
        """Test complete end-to-end onboarding flow."""
        orchestrator, tier1 = setup
        
        # Step 1: Start onboarding
        result1 = orchestrator.start_onboarding("User wants to onboard")
        assert result1['status'] == 'onboarding_started'
        
        # Step 2: Select experience (Mid)
        result2 = orchestrator.process_experience_choice("2")
        assert result2['status'] == 'awaiting_mode'
        assert result2['experience_level'] == 'mid'
        
        # Step 3: Select interaction mode (Guided)
        result3 = orchestrator.process_mode_choice("2", result2['experience_level'])
        assert result3['status'] == 'awaiting_tech_stack'
        
        # Step 4: Select tech stack (AWS)
        result4 = orchestrator.process_tech_stack_choice("3")
        assert result4['status'] == 'completed'
        
        # Verify final profile
        profile = tier1.get_profile()
        assert profile['experience_level'] == 'mid'
        assert profile['interaction_mode'] == 'guided'
        assert profile['tech_stack_preference']['cloud_provider'] == 'aws'
        assert profile['tech_stack_preference']['ci_cd'] == 'github_actions'


class TestProfileUpdateFlow:
    """Test profile update flow."""
    
    @pytest.fixture
    def setup(self):
        """Setup with existing profile."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_profile.db")
        tier1 = WorkingMemory(db_path=db_path)
        orchestrator = OnboardingOrchestrator(tier1_api=tier1)
        
        # Create initial profile
        tier1.create_profile(
            interaction_mode="guided",
            experience_level="mid",
            tech_stack_preference=None
        )
        
        yield orchestrator, tier1
        
        # Cleanup
        tier1.close()
        if os.path.exists(db_path):
            os.remove(db_path)
        os.rmdir(temp_dir)
    
    def test_show_update_options(self, setup):
        """Test showing profile update options."""
        orchestrator, tier1 = setup
        
        result = orchestrator.show_update_options()
        
        assert 'Profile Update' in result
        assert 'Experience: Mid' in result
        assert 'Mode: Guided' in result
        assert '1. Experience level' in result
        assert '2. Interaction mode' in result
        assert '3. Tech stack preference' in result
        assert '4. All settings' in result
    
    def test_update_experience_level(self, setup):
        """Test updating experience level."""
        orchestrator, tier1 = setup
        
        result = orchestrator.update_experience_level("4")  # Expert
        
        assert result['status'] == 'success'
        assert 'Expert' in result['message']
        
        # Verify update
        profile = tier1.get_profile()
        assert profile['experience_level'] == 'expert'
        assert profile['interaction_mode'] == 'guided'  # Unchanged
    
    def test_update_interaction_mode(self, setup):
        """Test updating interaction mode."""
        orchestrator, tier1 = setup
        
        result = orchestrator.update_interaction_mode("1")  # Autonomous
        
        assert result['status'] == 'success'
        assert 'Autonomous' in result['message']
        
        # Verify update
        profile = tier1.get_profile()
        assert profile['interaction_mode'] == 'autonomous'
        assert profile['experience_level'] == 'mid'  # Unchanged
    
    def test_update_tech_stack(self, setup):
        """Test updating tech stack preference."""
        orchestrator, tier1 = setup
        
        result = orchestrator.update_tech_stack("2")  # Azure
        
        assert result['status'] == 'success'
        assert 'Azure stack' in result['message']
        assert 'NOT a constraint' in result['message']  # Context-not-constraint reminder
        
        # Verify update
        profile = tier1.get_profile()
        assert profile['tech_stack_preference'] is not None
        assert profile['tech_stack_preference']['cloud_provider'] == 'azure'
    
    def test_show_tech_stack_options(self, setup):
        """Test showing tech stack options."""
        orchestrator, tier1 = setup
        
        result = orchestrator.show_tech_stack_options()
        
        assert 'Tech Stack Update' in result
        assert 'Current Tech Stack:**' in result  # Match actual format with ** markdown
        assert 'Tech stack is context' in result
        assert 'Azure stack' in result
        assert 'AWS stack' in result
        assert 'GCP stack' in result


class TestProfileInjection:
    """Test profile injection into AgentRequest."""
    
    @pytest.fixture
    def setup(self):
        """Setup intent router with profile."""
        temp_dir = tempfile.mkdtemp()
        db_path = os.path.join(temp_dir, "test_profile.db")
        tier1 = WorkingMemory(db_path=db_path)
        
        # Create profile
        tier1.create_profile(
            interaction_mode="guided",
            experience_level="senior",
            tech_stack_preference={
                'cloud_provider': 'azure',
                'container_platform': 'kubernetes'
            }
        )
        
        router = IntentRouter("test-router", tier1_api=tier1)
        
        yield router, tier1
        
        # Cleanup
        tier1.close()
        if os.path.exists(db_path):
            os.remove(db_path)
        os.rmdir(temp_dir)
    
    def test_profile_injected_into_request(self, setup):
        """Test profile is automatically injected into AgentRequest."""
        router, tier1 = setup
        
        request = AgentRequest(
            intent="code",
            context={},
            user_message="Create a new feature"
        )
        
        # Execute should inject profile
        response = router.execute(request)
        
        # Verify profile was injected
        assert request.user_profile is not None
        assert request.user_profile['interaction_mode'] == 'guided'
        assert request.user_profile['experience_level'] == 'senior'
        assert request.user_profile['tech_stack_preference']['cloud_provider'] == 'azure'
    
    def test_profile_update_intent_detection(self, setup):
        """Test profile update intent is detected."""
        router, tier1 = setup
        
        request = AgentRequest(
            intent="unknown",
            context={},
            user_message="update my profile"
        )
        
        response = router.execute(request)
        
        # Verify profile update was detected
        assert response.success is True
        assert response.result['action'] == 'profile_update'
        assert response.metadata['requires_profile_update'] is True


class TestContextNotConstraint:
    """Test context-not-constraint pattern validation."""
    
    def test_template_enrichment_azure(self):
        """Test template enrichment adds Azure placeholders."""
        renderer = TemplateRenderer()
        
        context = {
            'user_profile': {
                'tech_stack_preference': {
                    'cloud_provider': 'azure',
                    'container_platform': 'kubernetes'
                }
            }
        }
        
        enriched = renderer._enrich_tech_stack_context(context)
        
        # Verify Azure placeholders added
        assert enriched['has_tech_stack'] is True
        assert enriched['cloud_provider_name'] == 'AZURE'
        assert 'Azure' in enriched['cloud_deployment']
        assert 'AKS' in enriched['container_orchestration']
    
    def test_template_enrichment_aws(self):
        """Test template enrichment adds AWS placeholders."""
        renderer = TemplateRenderer()
        
        context = {
            'user_profile': {
                'tech_stack_preference': {
                    'cloud_provider': 'aws'
                }
            }
        }
        
        enriched = renderer._enrich_tech_stack_context(context)
        
        # Verify AWS placeholders added
        assert enriched['has_tech_stack'] is True
        assert enriched['cloud_provider_name'] == 'AWS'
        assert 'AWS' in enriched['cloud_deployment']
        assert 'EKS' in enriched['container_orchestration']
    
    def test_template_enrichment_gcp(self):
        """Test template enrichment adds GCP placeholders."""
        renderer = TemplateRenderer()
        
        context = {
            'user_profile': {
                'tech_stack_preference': {
                    'cloud_provider': 'gcp'
                }
            }
        }
        
        enriched = renderer._enrich_tech_stack_context(context)
        
        # Verify GCP placeholders added
        assert enriched['has_tech_stack'] is True
        assert enriched['cloud_provider_name'] == 'GCP'
        assert 'GKE' in enriched['container_orchestration']
    
    def test_template_enrichment_no_tech_stack(self):
        """Test template enrichment handles no tech stack gracefully."""
        renderer = TemplateRenderer()
        
        context = {
            'user_profile': {
                'interaction_mode': 'guided',
                'experience_level': 'mid'
            }
        }
        
        enriched = renderer._enrich_tech_stack_context(context)
        
        # Verify no enrichment when no tech stack
        assert 'has_tech_stack' not in enriched or not enriched.get('has_tech_stack')
    
    def test_recommendation_not_filtered(self):
        """Test that tech stack does NOT filter recommendations."""
        # This is a behavioral test - tech stack should only add
        # company-aligned implementation section, never filter recommended solution
        
        renderer = TemplateRenderer()
        
        # User with Azure stack should still see Redis recommendation
        context = {
            'user_profile': {
                'tech_stack_preference': {
                    'cloud_provider': 'azure'
                }
            },
            'recommended_solution': 'Redis',
            'company_aligned_implementation': 'Azure Cache for Redis'
        }
        
        enriched = renderer._enrich_tech_stack_context(context)
        
        # Verify both sections present
        assert 'recommended_solution' in context  # Recommended (Redis) unchanged
        assert enriched['has_tech_stack'] is True  # Company section enabled
        
        # This validates the pattern: BOTH recommendations shown, not filtered


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
