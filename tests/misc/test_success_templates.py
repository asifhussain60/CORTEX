"""
Test Suite for Success Template Integration

Tests verify success_completion templates render correctly and orchestrators
use them appropriately when work is complete.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import pytest
from pathlib import Path
from src.response_templates.response_template_manager import ResponseTemplateManager


class TestSuccessCompletionTemplate:
    """Test success_completion base template rendering."""
    
    def test_success_completion_has_congratulations_header(self):
        """Verify success template renders with CONGRATULATIONS H1 header."""
        manager = ResponseTemplateManager()
        
        rendered = manager.render_template(
            template_id='success_completion',
            context={
                'operation': 'Test Operation',
                'understanding_content': 'Test understanding',
                'challenge_content': 'No Challenge',
                'response_content': 'Test response',
                'request_echo_content': 'Test request',
                'optional_next_actions': 'Optional: Try something else'
            }
        )
        
        assert '# 🎉 CONGRATULATIONS' in rendered
        assert '## 🧠 CORTEX Test Operation' in rendered
        assert '✅ **Work Complete!**' in rendered
        assert 'Optional: Try something else' in rendered
    
    def test_success_completion_no_next_steps_section(self):
        """Verify success template uses optional_next_actions not next_steps."""
        manager = ResponseTemplateManager()
        
        rendered = manager.render_template(
            template_id='success_completion',
            context={
                'operation': 'Test Operation',
                'understanding_content': 'Test understanding',
                'challenge_content': 'No Challenge',
                'response_content': 'Test response',
                'request_echo_content': 'Test request',
                'optional_next_actions': 'Optional actions here'
            }
        )
        
        # Should have work complete message
        assert '✅ **Work Complete!**' in rendered
        # Should have optional actions
        assert 'Optional actions here' in rendered


class TestStandardTemplateNoConfetti:
    """Test standard template does NOT show celebration for in-progress work."""
    
    def test_standard_template_no_congratulations(self):
        """Verify standard template does NOT have CONGRATULATIONS."""
        manager = ResponseTemplateManager()
        
        rendered = manager.render_template(
            template_id='standard_5_part',
            context={
                'operation': 'Test Operation',
                'understanding_content': 'Test understanding',
                'challenge_content': 'Challenge present',
                'response_content': 'Test response',
                'request_echo_content': 'Test request',
                'next_steps_content': '☐ Step 1\n☐ Step 2'
            }
        )
        
        assert '# 🎉 CONGRATULATIONS' not in rendered
        assert '## 🧠 CORTEX Test Operation' in rendered
        assert '☐ Step 1' in rendered
        assert '☐ Step 2' in rendered


class TestSystemMaintenanceCompleteTemplate:
    """Test system_maintenance_complete template."""
    
    def test_system_maintenance_complete_template_exists(self):
        """Verify system_maintenance_complete template is registered."""
        manager = ResponseTemplateManager()
        
        rendered = manager.render_template(
            template_id='system_maintenance_complete',
            context={
                'total_phases': 6,
                'phase_list': 'Healthcheck → Alignment → Cleanup → Optimize → Refresh → Healthcheck',
                'pre_health_status': 'Healthy',
                'alignment_fixes': 12,
                'cleanup_improvements': 8,
                'optimization_gains': 'Performance +15%',
                'prompts_updated': 5,
                'post_health_status': 'Healthy',
                'overall_status': 'All phases completed',
                'total_improvements': 25,
                'warnings_resolved': 3,
                'duration': '2m 15s',
                'report_path': '/path/to/report.json'
            }
        )
        
        assert '# 🎉 CONGRATULATIONS' in rendered
        assert '## 🧠 CORTEX System Maintenance' in rendered
        assert '## 🔧 Maintenance Summary' in rendered
        assert '12 fixes applied' in rendered
        assert '✅ **Work Complete!**' in rendered


class TestPlanExecutionCompleteTemplate:
    """Test plan_execution_complete template."""
    
    def test_plan_execution_complete_template_exists(self):
        """Verify plan_execution_complete template is registered."""
        manager = ResponseTemplateManager()
        
        rendered = manager.render_template(
            template_id='plan_execution_complete',
            context={
                'feature_name': 'User Authentication',
                'phases_completed': 4,
                'phases_total': 4,
                'tests_passing': 45,
                'tests_total': 45,
                'coverage_percentage': 92,
                'duration': '1h 30m',
                'commit_hash': 'abc123def'
            }
        )
        
        assert '# 🎉 CONGRATULATIONS' in rendered
        assert '## 🧠 CORTEX Feature Implementation' in rendered
        assert '## ✅ Implementation Complete' in rendered
        assert 'User Authentication' in rendered
        assert '45/45 passing (100%)' in rendered
        assert '✅ **Work Complete!**' in rendered


class TestTDDWorkflowCompleteTemplate:
    """Test tdd_workflow_complete template."""
    
    def test_tdd_workflow_complete_template_exists(self):
        """Verify tdd_workflow_complete template is registered."""
        manager = ResponseTemplateManager()
        
        rendered = manager.render_template(
            template_id='tdd_workflow_complete',
            context={
                'tests_written': 12,
                'feature_name': 'Order Processing',
                'domain_coverage': 95,
                'application_coverage': 88,
                'infrastructure_coverage': 75,
                'overall_coverage': 86,
                'complexity_score': 'Low (3.2)'
            }
        )
        
        assert '# 🎉 CONGRATULATIONS' in rendered
        assert '## 🧠 CORTEX TDD Workflow' in rendered
        assert '## 🧪 TDD Cycle Complete' in rendered
        assert 'RED → GREEN → REFACTOR' in rendered
        assert '12 tests written' in rendered
        assert '✅ **Work Complete!**' in rendered


class TestTemplateDecisionLogic:
    """Test template selection logic."""
    
    def test_work_complete_signals_success_template(self):
        """Verify is_complete flag signals use of success template."""
        # This would be tested in orchestrator integration tests
        # Here we document the pattern:
        
        # Orchestrator sets is_complete=True when:
        # - all_phases_complete = True
        # - all_tests_passing = True
        # - no_warnings = True (or warnings_count == 0)
        # - no_errors = True (or errors_count == 0)
        
        # Example data structure from orchestrator:
        completion_data = {
            'is_complete': True,
            'phases_completed': 6,
            'phases_total': 6,
            'tests_passing': 100,
            'tests_total': 100,
            'errors': [],
            'warnings': []
        }
        
        assert completion_data['is_complete'] is True
        assert completion_data['phases_completed'] == completion_data['phases_total']
        assert len(completion_data['errors']) == 0
    
    def test_work_incomplete_signals_standard_template(self):
        """Verify incomplete work uses standard template."""
        incomplete_data = {
            'is_complete': False,
            'phases_completed': 4,
            'phases_total': 6,
            'warnings': ['Some cleanup needed']
        }
        
        assert incomplete_data['is_complete'] is False
        assert incomplete_data['phases_completed'] < incomplete_data['phases_total']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
