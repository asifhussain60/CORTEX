"""
Tests for Demo and Tutorial Integration

Tests ADO planning demo and tutorial modules.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
from pathlib import Path
from src.operations.modules.demo.demo_orchestrator import DemoOrchestrator
from src.operations.modules.demo.ado_planning_demo import ADOPlanningDemo
from src.operations.modules.hands_on_tutorial_orchestrator import HandsOnTutorialOrchestrator, TutorialProfile
from src.operations.modules.tutorial_validator import TutorialValidator


@pytest.fixture
def cortex_root():
    """Get CORTEX repository root."""
    return Path.cwd()


@pytest.fixture
def demo_orchestrator(cortex_root):
    """Create demo orchestrator instance."""
    return DemoOrchestrator(cortex_root / "cortex-brain")


@pytest.fixture
def ado_demo(cortex_root):
    """Create ADO planning demo instance."""
    return ADOPlanningDemo(cortex_root)


@pytest.fixture
def tutorial_orchestrator(cortex_root):
    """Create tutorial orchestrator instance."""
    return HandsOnTutorialOrchestrator(cortex_root)


@pytest.fixture
def tutorial_validator(cortex_root):
    """Create tutorial validator instance."""
    return TutorialValidator(cortex_root)


class TestDemoIntegration:
    """Test demo orchestrator integration."""
    
    def test_demo_orchestrator_detects_ado_planning(self, demo_orchestrator):
        """Test that demo orchestrator detects ADO planning requests."""
        test_requests = [
            "demo ado",
            "demo ado planning",
            "show ado planning",
            "ado demo"
        ]
        
        for request in test_requests:
            demo_type = demo_orchestrator._detect_demo_type(request.lower())
            assert demo_type == 'ado_planning', f"Failed to detect ADO demo for request: {request}"
    
    def test_demo_orchestrator_handles_ado_planning(self, demo_orchestrator):
        """Test that demo orchestrator can handle ADO planning demo."""
        result = demo_orchestrator.handle_discovery("demo ado planning")
        
        assert 'template_id' in result
        assert 'context' in result
        assert result['context'].get('demo_type') == 'ado_planning'
        assert 'ADO Work Item Planning Demo' in result['context'].get('demo_content', '')
    
    def test_ado_planning_demo_runs(self, ado_demo):
        """Test that ADO planning demo executes successfully."""
        result = ado_demo.run_demo()
        
        assert result['success'] is True
        assert 'demo_sections' in result
        assert len(result['demo_sections']) == 7  # 7 sections in demo
        
        # Check section titles
        section_titles = [section['title'] for section in result['demo_sections']]
        assert '📋 ADO Work Item Planning Demo' in section_titles
        assert '❌ Before Phase 1 (No Git Integration)' in section_titles
        assert '✅ After Phase 1 (Git Integration Active)' in section_titles
        assert '📊 Quality Scoring Explained' in section_titles
        assert '⚠️ High-Risk File Detection' in section_titles
        assert '💡 SME Identification System' in section_titles
        assert '🚀 Try It Yourself!' in section_titles
    
    def test_demo_shows_before_after_comparison(self, ado_demo):
        """Test that demo includes before/after comparison."""
        result = ado_demo.run_demo()
        
        before_section = result['demo_sections'][1]
        after_section = result['demo_sections'][2]
        
        assert before_section['type'] == 'before_example'
        assert after_section['type'] == 'after_example'
        assert '## Acceptance Criteria' in before_section['content']
        assert '## Git History Context' in after_section['content']
    
    def test_demo_explains_quality_scoring(self, ado_demo):
        """Test that demo explains quality scoring system."""
        result = ado_demo.run_demo()
        
        quality_section = result['demo_sections'][3]
        
        assert 'Quality Scoring Explained' in quality_section['title']
        assert '90-100% (Excellent)' in quality_section['content']
        assert '70-89% (Good)' in quality_section['content']
        assert '50-69% (Adequate)' in quality_section['content']
        assert '< 50% (Weak)' in quality_section['content']
    
    def test_demo_explains_high_risk_detection(self, ado_demo):
        """Test that demo explains high-risk file detection."""
        result = ado_demo.run_demo()
        
        risk_section = result['demo_sections'][4]
        
        assert 'High-Risk File Detection' in risk_section['title']
        assert 'High Churn' in risk_section['content']
        assert 'Hotfix Pattern' in risk_section['content']
        assert 'Recent Security Fix' in risk_section['content']
    
    def test_demo_explains_sme_identification(self, ado_demo):
        """Test that demo explains SME identification."""
        result = ado_demo.run_demo()
        
        sme_section = result['demo_sections'][5]
        
        assert 'SME Identification System' in sme_section['title']
        assert 'git shortlog' in sme_section['content']
        assert 'Contributor Analysis' in sme_section['content']


class TestTutorialIntegration:
    """Test tutorial orchestrator integration."""
    
    def test_tutorial_has_ado_planning_module(self, tutorial_orchestrator):
        """Test that tutorial includes ADO planning module."""
        assert 'ado_planning' in tutorial_orchestrator.modules
        
        ado_module = tutorial_orchestrator.modules['ado_planning']
        assert ado_module.name == 'ADO Work Item Planning'
        assert ado_module.duration_min == 6
        assert len(ado_module.exercises) == 5
    
    def test_ado_module_has_correct_exercises(self, tutorial_orchestrator):
        """Test that ADO module has all required exercises."""
        ado_module = tutorial_orchestrator.modules['ado_planning']
        
        expected_exercises = [
            'create_ado_work_item',
            'review_git_context',
            'understand_quality_scoring',
            'analyze_high_risk_files',
            'review_sme_suggestions'
        ]
        
        assert ado_module.exercises == expected_exercises
    
    def test_ado_module_prerequisites(self, tutorial_orchestrator):
        """Test that ADO module has correct prerequisites."""
        ado_module = tutorial_orchestrator.modules['ado_planning']
        
        assert 'basics' in ado_module.prerequisites
        assert 'planning' in ado_module.prerequisites
    
    def test_tutorial_can_get_ado_exercise_instructions(self, tutorial_orchestrator):
        """Test that tutorial can retrieve ADO exercise instructions."""
        exercise = tutorial_orchestrator._get_exercise_instructions('ado_planning', 'create_ado_work_item')
        
        assert 'Exercise 3.1' in exercise['title']
        assert 'Create ADO Work Item' in exercise['title']
        assert 'plan ado' in exercise['commands']
        assert 'OAuth users cannot log in' in exercise['scenario']
    
    def test_all_ado_exercises_have_instructions(self, tutorial_orchestrator):
        """Test that all ADO exercises have complete instructions."""
        ado_module = tutorial_orchestrator.modules['ado_planning']
        
        for exercise_id in ado_module.exercises:
            exercise = tutorial_orchestrator._get_exercise_instructions('ado_planning', exercise_id)
            
            assert 'title' in exercise
            assert 'task' in exercise
            assert exercise['title'] != 'Exercise Not Found'
    
    def test_tutorial_start_includes_ado_module(self, tutorial_orchestrator):
        """Test that starting tutorial accounts for ADO module duration."""
        result = tutorial_orchestrator.start_tutorial(TutorialProfile.STANDARD)
        
        assert 'session_id' in result
        assert 'duration_min' in result
        # Standard tutorial should be 25 minutes (was updated to include ADO module)
        # But check it's reasonable (20-30 min range)
        assert 20 <= result['duration_min'] <= 30


class TestTutorialValidation:
    """Test tutorial validation functionality."""
    
    def test_validator_can_validate_ado_exercise(self, tutorial_validator):
        """Test that validator can validate ADO planning exercise."""
        # This test would use a real work item file if available
        # For now, test the structure
        result = tutorial_validator.validate_ado_planning_exercise('test-12345')
        
        assert 'work_item_created' in result
        assert 'git_context_present' in result
        assert 'quality_score_calculated' in result
        assert 'high_risk_detected' in result
        assert 'sme_suggested' in result
        assert 'contributors_listed' in result
        assert 'related_commits_listed' in result
        assert 'acceptance_criteria_enhanced' in result
    
    def test_validator_generates_report(self, tutorial_validator):
        """Test that validator can generate validation report."""
        validation_results = {
            'work_item_id': 'Bug-12345',
            'work_item_created': True,
            'git_context_present': True,
            'quality_score_calculated': True,
            'quality_score_value': 85.5,
            'high_risk_detected': True,
            'high_risk_files': ['src/auth/login.py'],
            'sme_suggested': True,
            'sme_name': 'John Doe',
            'contributors_listed': True,
            'related_commits_listed': True,
            'acceptance_criteria_enhanced': True,
            'completion_percentage': 100,
            'all_checks_passed': True
        }
        
        report = tutorial_validator.generate_validation_report(validation_results)
        
        assert '# Tutorial Exercise Validation Report' in report
        assert 'Bug-12345' in report
        assert '✅ PASSED' in report
        assert '85.5%' in report
        assert 'Good' in report  # Quality label for 85.5%
        assert 'John Doe' in report
        assert 'src/auth/login.py' in report
    
    def test_validator_quality_labels(self, tutorial_validator):
        """Test that validator assigns correct quality labels."""
        assert tutorial_validator._get_quality_label(95) == 'Excellent'
        assert tutorial_validator._get_quality_label(85) == 'Good'
        assert tutorial_validator._get_quality_label(60) == 'Adequate'
        assert tutorial_validator._get_quality_label(40) == 'Weak'
    
    def test_validator_can_validate_all_modules(self, tutorial_validator):
        """Test that validator can validate all tutorial modules."""
        result = tutorial_validator.validate_all_exercises('tutorial-20251127-120000')
        
        assert 'session_id' in result
        assert 'basics_complete' in result
        assert 'planning_complete' in result
        assert 'ado_planning_complete' in result
        assert 'tdd_complete' in result
        assert 'testing_complete' in result
        assert 'overall_completion' in result
        assert 'all_modules_complete' in result


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
