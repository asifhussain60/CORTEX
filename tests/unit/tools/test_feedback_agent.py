"""
Tests for Feedback Agent
AC-IDs tested: AC-AGENT-002

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from cortex.tools.feedback_agent import (
    FeedbackAgent,
    FeedbackType,
    Priority,
    ModuleStatus,
    ModuleHealth,
    ErrorInfo,
    ExecutionMetrics,
    Feedback,
    collect_feedback,
)


class TestFeedbackAgent:
    """Tests for FeedbackAgent."""
    
    @pytest.fixture
    def agent(self) -> FeedbackAgent:
        """Create test instance."""
        return FeedbackAgent()
    
    def test_agent_initialization(self, agent: FeedbackAgent) -> None:
        """Test AC-ID: AC-AGENT-002-01 - Agent initializes correctly."""
        assert agent is not None
        assert agent.session_id is not None
        assert len(agent.session_id) == 8
    
    def test_agent_custom_session_id(self) -> None:
        """Test AC-ID: AC-AGENT-002-02 - Agent accepts custom session ID."""
        agent = FeedbackAgent(session_id="test1234")
        assert agent.session_id == "test1234"
    
    def test_collect_general_feedback(self, agent: FeedbackAgent) -> None:
        """Test AC-ID: AC-AGENT-002-03 - Collect general feedback."""
        feedback = agent.collect(FeedbackType.GENERAL)
        
        assert isinstance(feedback, Feedback)
        assert feedback.feedback_type == FeedbackType.GENERAL
        assert feedback.session_id == agent.session_id
    
    def test_collect_error_feedback(self, agent: FeedbackAgent) -> None:
        """Test AC-ID: AC-AGENT-002-04 - Collect error feedback."""
        feedback = agent.collect(FeedbackType.ERROR)
        
        assert isinstance(feedback, Feedback)
        assert feedback.feedback_type == FeedbackType.ERROR
    
    def test_collect_performance_feedback(self, agent: FeedbackAgent) -> None:
        """Test AC-ID: AC-AGENT-002-05 - Collect performance feedback."""
        feedback = agent.collect(FeedbackType.PERFORMANCE)
        
        assert isinstance(feedback, Feedback)
        assert feedback.feedback_type == FeedbackType.PERFORMANCE
    
    def test_collect_governance_feedback(self, agent: FeedbackAgent) -> None:
        """Test AC-ID: AC-AGENT-002-06 - Collect governance feedback."""
        feedback = agent.collect(FeedbackType.GOVERNANCE)
        
        assert isinstance(feedback, Feedback)
        assert feedback.feedback_type == FeedbackType.GOVERNANCE
    
    def test_feedback_has_metadata(self, agent: FeedbackAgent) -> None:
        """Test AC-ID: AC-AGENT-002-07 - Feedback includes metadata."""
        feedback = agent.collect(FeedbackType.GENERAL)
        
        assert feedback.generated_at is not None
        assert feedback.session_id is not None
        assert feedback.machine in ["mac", "win", "linux"]
        assert feedback.cortex_version == "3.9"
    
    def test_feedback_has_module_health(self, agent: FeedbackAgent) -> None:
        """Test AC-ID: AC-AGENT-002-08 - Feedback includes module health."""
        feedback = agent.collect(FeedbackType.GENERAL, scope="all")
        
        assert len(feedback.module_health) >= 1
        for health in feedback.module_health:
            assert isinstance(health, ModuleHealth)
            assert health.name is not None
            assert health.status is not None
    
    def test_feedback_has_recommendations(self, agent: FeedbackAgent) -> None:
        """Test AC-ID: AC-AGENT-002-09 - Feedback includes recommendations."""
        feedback = agent.collect(FeedbackType.GENERAL, include_recommendations=True)
        
        assert isinstance(feedback.recommended_actions_immediate, list)
        assert isinstance(feedback.recommended_actions_short_term, list)
        assert isinstance(feedback.investigation_required, list)
    
    def test_feedback_has_github_labels(self, agent: FeedbackAgent) -> None:
        """Test AC-ID: AC-AGENT-002-10 - Feedback includes GitHub labels."""
        feedback = agent.collect(FeedbackType.ERROR)
        
        assert len(feedback.github_labels) >= 1
        assert any("bug" in label or "error" in label.lower() for label in feedback.github_labels)
    
    def test_feedback_to_yaml(self, agent: FeedbackAgent) -> None:
        """Test AC-ID: AC-AGENT-002-11 - Feedback converts to YAML."""
        feedback = agent.collect(FeedbackType.GENERAL)
        yaml_output = feedback.to_yaml()
        
        assert isinstance(yaml_output, str)
        assert "metadata:" in yaml_output
        assert "summary:" in yaml_output
        assert "execution_metrics:" in yaml_output
        assert "module_health:" in yaml_output
    
    def test_feedback_to_github_issue_markdown(self, agent: FeedbackAgent) -> None:
        """Test AC-ID: AC-AGENT-002-12 - Feedback converts to GitHub Issue markdown."""
        feedback = agent.collect(FeedbackType.GENERAL)
        markdown = feedback.to_github_issue_markdown()
        
        assert isinstance(markdown, str)
        assert "## 🧠 CORTEX Operational Feedback" in markdown
        assert "### Summary" in markdown
        assert "### Impact" in markdown
        assert "```yaml" in markdown
    
    def test_record_error(self, agent: FeedbackAgent) -> None:
        """Test AC-ID: AC-AGENT-002-13 - Record and collect errors."""
        error = ErrorInfo(
            error_id="ERR-001",
            timestamp="2026-01-21T12:00:00Z",
            component="test_component",
            error_type="ValueError",
            message="Test error message",
        )
        agent.record_error(error)
        
        feedback = agent.collect(FeedbackType.ERROR)
        assert len(feedback.errors) >= 1
        assert feedback.errors[0].error_id == "ERR-001"
    
    def test_priority_determination_critical(self, agent: FeedbackAgent) -> None:
        """Test AC-ID: AC-AGENT-002-14 - Critical priority for failed modules."""
        # Record a critical error
        error = ErrorInfo(
            error_id="CRIT-001",
            timestamp="2026-01-21T12:00:00Z",
            component="critical_component",
            error_type="CriticalError",
            message="Critical failure",
        )
        agent.record_error(error)
        
        feedback = agent.collect(FeedbackType.ERROR)
        # Priority should be elevated due to critical error
        assert feedback.priority in [Priority.P0_CRITICAL, Priority.P1_HIGH]


class TestConvenienceFunction:
    """Tests for the collect_feedback convenience function."""
    
    def test_collect_feedback_yaml(self) -> None:
        """Test AC-ID: AC-AGENT-002-15 - Convenience function returns YAML."""
        output = collect_feedback("general", output_format="yaml")
        
        assert isinstance(output, str)
        assert "metadata:" in output
    
    def test_collect_feedback_markdown(self) -> None:
        """Test AC-ID: AC-AGENT-002-16 - Convenience function returns markdown."""
        output = collect_feedback("general", output_format="markdown")
        
        assert isinstance(output, str)
        assert "## 🧠 CORTEX" in output


class TestFeedbackType:
    """Tests for FeedbackType enum."""
    
    def test_all_types_defined(self) -> None:
        """Test AC-ID: AC-AGENT-002-17 - All required types exist."""
        expected_types = ["error", "performance", "enhancement", "governance", "general"]
        
        for fb_type in expected_types:
            assert FeedbackType(fb_type) is not None


class TestPriority:
    """Tests for Priority enum."""
    
    def test_all_priorities_defined(self) -> None:
        """Test AC-ID: AC-AGENT-002-18 - All priorities exist."""
        expected_priorities = ["P0-CRITICAL", "P1-HIGH", "P2-MEDIUM", "P3-LOW"]
        
        for priority in expected_priorities:
            assert Priority(priority) is not None


class TestModuleStatus:
    """Tests for ModuleStatus enum."""
    
    def test_all_statuses_defined(self) -> None:
        """Test AC-ID: AC-AGENT-002-19 - All statuses exist."""
        expected_statuses = ["operational", "degraded", "failed"]
        
        for status in expected_statuses:
            assert ModuleStatus(status) is not None


class TestExecutionMetrics:
    """Tests for ExecutionMetrics dataclass."""
    
    def test_default_values(self) -> None:
        """Test AC-ID: AC-AGENT-002-20 - Default values are set."""
        metrics = ExecutionMetrics()
        
        assert metrics.duration_ms == 0
        assert metrics.token_input == 0
        assert metrics.token_output == 0
        assert metrics.token_percentage == 0.0
        assert metrics.state_transitions == 0
        assert metrics.audit_entries == 0
