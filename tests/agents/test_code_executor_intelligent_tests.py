"""
Tests for CodeExecutor intelligent test determination (Phase 2)

Validates that CodeExecutor intelligently determines when tests are needed
based on change analysis rather than blindly requiring TDD for all changes.
"""

import pytest
from src.cortex_agents.tactical.code_executor import CodeExecutor
from src.cortex_agents.base_agent import AgentRequest


class TestIntelligentTestDetermination:
    """Test intelligent test determination logic"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.executor = CodeExecutor()
    
    def test_trivial_changes_skip_tests(self):
        """Test that trivial changes (typos, comments) don't require tests"""
        trivial_tasks = [
            "Fix typo in user authentication module",
            "Update comment in database connection",
            "Fix spelling error in README",
            "Add documentation to payment service",
            "Fix whitespace in config file",
            "Rename variable from userId to user_id"
        ]
        
        for task in trivial_tasks:
            request = AgentRequest(
                intent="CODE",
                user_message=task,
                context={
                    'rule_context': {
                        'intelligent_test_determination': True
                    }
                }
            )
            
            response = self.executor.execute(request)
            
            assert response.success
            assert response.result['requires_tests'] is False
            assert 'Direct implementation' in response.result['tdd_cycle']
            assert 'Implement change directly' in response.next_actions[0]
    
    def test_significant_changes_require_tests(self):
        """Test that significant changes require TDD"""
        significant_tasks = [
            "Add feature for user authentication",
            "Implement payment processing algorithm",
            "Create API endpoint for order management",
            "Add business logic for inventory calculation",
            "Implement database migration for users table",
            "Create integration with external payment gateway"
        ]
        
        for task in significant_tasks:
            request = AgentRequest(
                intent="CODE",
                user_message=task,
                context={
                    'rule_context': {
                        'intelligent_test_determination': True
                    }
                }
            )
            
            response = self.executor.execute(request)
            
            assert response.success
            assert response.result['requires_tests'] is True
            assert 'RED → GREEN → REFACTOR enforced' in response.result['tdd_cycle']
            assert 'Generate failing tests (RED)' in response.next_actions[0]
    
    def test_unclear_changes_default_to_requiring_tests(self):
        """Test that unclear changes default to requiring tests (safety)"""
        unclear_tasks = [
            "Update the main module",
            "Modify configuration settings",
            "Change the way we handle requests"
        ]
        
        for task in unclear_tasks:
            request = AgentRequest(
                intent="CODE",
                user_message=task,
                context={
                    'rule_context': {
                        'intelligent_test_determination': True
                    }
                }
            )
            
            response = self.executor.execute(request)
            
            assert response.success
            assert response.result['requires_tests'] is True
    
    def test_disabled_intelligent_determination_always_requires_tests(self):
        """Test that disabling intelligent determination always requires tests"""
        request = AgentRequest(
            intent="CODE",
            user_message="Fix typo in comment",  # Would normally skip tests
            context={
                'rule_context': {
                    'intelligent_test_determination': False  # Disabled
                }
            }
        )
        
        response = self.executor.execute(request)
        
        assert response.success
        assert response.result['requires_tests'] is True


class TestSummaryGenerationControl:
    """Test summary generation control (Phase 3)"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.executor = CodeExecutor()
    
    def test_execution_intents_skip_summary(self):
        """Test that execution-focused intents suppress summary generation"""
        request = AgentRequest(
            intent="CODE",
            user_message="Implement user authentication",
            context={
                'rule_context': {
                    'skip_summary_generation': True,
                    'intelligent_test_determination': True
                }
            }
        )
        
        response = self.executor.execute(request)
        
        assert response.success
        assert response.result['skip_summary'] is True
        assert 'summary_note' in response.result
        assert 'suppressed' in response.result['summary_note'].lower()
    
    def test_investigation_intents_allow_summary(self):
        """Test that investigation intents allow summary generation"""
        request = AgentRequest(
            intent="ARCHITECTURE",
            user_message="Analyze system architecture",
            context={
                'rule_context': {
                    'skip_summary_generation': False,
                    'enable_crawlers': True
                }
            }
        )
        
        response = self.executor.execute(request)
        
        assert response.success
        assert response.result['skip_summary'] is False
        assert 'summary_note' not in response.result  # No suppression note


class TestRuleContextIntegration:
    """Test integration with IntentRouter rule context"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.executor = CodeExecutor()
    
    def test_rule_context_passed_through(self):
        """Test that rule context from IntentRouter is properly used"""
        # Simulate IntentRouter passing rule context
        request = AgentRequest(
            intent="CODE",
            user_message="Add new feature",
            context={
                'rule_context': {
                    'rules_to_consider': ['TDD_ENFORCEMENT', 'DEFINITION_OF_DONE'],
                    'intelligent_test_determination': True,
                    'skip_summary_generation': True,
                    'requires_dod_validation': True
                }
            }
        )
        
        response = self.executor.execute(request)
        
        assert response.success
        assert 'requires_tests' in response.result
        assert 'skip_summary' in response.result
        assert isinstance(response.result['requires_tests'], bool)
        assert isinstance(response.result['skip_summary'], bool)
    
    def test_missing_rule_context_uses_defaults(self):
        """Test that missing rule context uses safe defaults"""
        request = AgentRequest(
            intent="CODE",
            user_message="Implement feature",
            context={}  # No rule_context
        )
        
        response = self.executor.execute(request)
        
        assert response.success
        # Should default to requiring tests and not skipping summary
        assert response.result['requires_tests'] is True
        assert response.result['skip_summary'] is False


class TestChangeAnalysisEdgeCases:
    """Test edge cases in change analysis"""
    
    def setup_method(self):
        """Setup test fixtures"""
        self.executor = CodeExecutor()
    
    def test_mixed_indicators_prioritizes_significant(self):
        """Test that mixed indicators prioritize significant changes"""
        request = AgentRequest(
            intent="CODE",
            user_message="Fix typo and add business logic validation",  # Mixed
            context={
                'rule_context': {
                    'intelligent_test_determination': True
                }
            }
        )
        
        response = self.executor.execute(request)
        
        assert response.success
        # Should require tests because "business logic" detected
        assert response.result['requires_tests'] is True
    
    def test_case_insensitive_matching(self):
        """Test that change analysis is case-insensitive"""
        request = AgentRequest(
            intent="CODE",
            user_message="FIX TYPO IN COMMENT",  # Uppercase
            context={
                'rule_context': {
                    'intelligent_test_determination': True
                }
            }
        )
        
        response = self.executor.execute(request)
        
        assert response.success
        assert response.result['requires_tests'] is False
    
    def test_empty_task_description_defaults_to_tests(self):
        """Test that empty task description defaults to requiring tests"""
        request = AgentRequest(
            intent="CODE",
            user_message="",  # Empty
            context={
                'rule_context': {
                    'intelligent_test_determination': True
                }
            }
        )
        
        response = self.executor.execute(request)
        
        assert response.success
        assert response.result['requires_tests'] is True


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
