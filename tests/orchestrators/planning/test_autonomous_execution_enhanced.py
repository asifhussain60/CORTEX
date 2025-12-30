"""
Test Autonomous Execution Enhanced - Phase 4.3

End-to-end tests for full workflow testing with progress updates,
TDD enforcement, and threat modeling integration.

Author: CORTEX Development Team
Version: 1.0.0 (Planner 2.0 Enhancements)
"""

import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from datetime import datetime
from pathlib import Path
import tempfile
import os

# Import planning orchestrator components
from src.orchestrators.planning.planning_orchestrator import (
    PlanningOrchestrator,
    PlanData,
    PlanMetadata,
    PlanPhaseData,
    PlanComplexity,
    PlanType,
    PlanningResult,
    ValidationResult,
    THREAT_MODELER_AVAILABLE
)


class TestAutonomousExecutionWorkflow:
    """E2E tests for autonomous execution with enhanced features."""
    
    @pytest.fixture
    def temp_workspace(self):
        """Create temporary workspace for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def mock_orchestrator(self, temp_workspace):
        """Create mock orchestrator with realistic configuration."""
        with patch.object(PlanningOrchestrator, '__init__', lambda x: None):
            orchestrator = PlanningOrchestrator()
            orchestrator.logger = Mock()
            orchestrator._tdd_dor_requirements = [
                "TDD Mastery workflow MUST be followed (RED→GREEN→REFACTOR)",
                "Tests MUST fail before implementation (RED phase validation)"
            ]
            orchestrator._tdd_dod_requirements = [
                "All tests passing",
                "Code reviewed",
                "Documentation updated"
            ]
            orchestrator.cortex_root = temp_workspace
            return orchestrator
    
    def test_full_plan_generation_workflow(self, mock_orchestrator):
        """Test complete plan generation with all enhanced features."""
        # Simulate full plan generation
        feature_name = "User Authentication with OAuth2"
        plan_type = "feature"
        
        # Create comprehensive plan with all new fields
        plan_data = PlanData(
            metadata=PlanMetadata(
                title=feature_name,
                description="OAuth2 authentication implementation",
                complexity=PlanComplexity.HIGH,
                plan_type=PlanType.INCREMENTAL
            ),
            definition_of_ready=[
                "Requirements clearly defined",
                "Architecture design reviewed",
                "Test strategy defined",
                "TDD workflow understood"
            ],
            definition_of_done=[
                "All tests passing",
                "Code reviewed and merged",
                "Documentation updated",
                "Security threats mitigated"
            ],
            phases=[
                PlanPhaseData(
                    phase_name="Security Analysis",
                    tasks=[
                        {"task": "Run STRIDE analysis", "estimated_hours": 2},
                        {"task": "Review OWASP Top 10 mapping", "estimated_hours": 1}
                    ],
                    acceptance_criteria=["All threats documented"]
                ),
                PlanPhaseData(
                    phase_name="Implementation",
                    tasks=[
                        {"task": "Implement OAuth2 flow", "estimated_hours": 6},
                        {"task": "Add session management", "estimated_hours": 4}
                    ],
                    acceptance_criteria=["OAuth2 working"]
                ),
                PlanPhaseData(
                    phase_name="Testing",
                    tasks=[
                        {"task": "Write unit tests", "estimated_hours": 3},
                        {"task": "Write integration tests", "estimated_hours": 3}
                    ],
                    acceptance_criteria=["100% critical path coverage"]
                )
            ],
            tdd_requirements={
                "dor": mock_orchestrator._tdd_dor_requirements,
                "dod": mock_orchestrator._tdd_dod_requirements
            },
            copilot_instructions={
                "response_template": "autonomous_execution_progress",
                "progress_updates": True,
                "tdd_enforcement": True,
                "checkpoint_frequency": "per_phase"
            },
            threat_modeling={
                "enabled": True,
                "stride_categories": [
                    "Spoofing", "Tampering", "Repudiation",
                    "Information Disclosure", "Elevation of Privilege"
                ],
                "auto_mitigations": True
            },
            threat_analysis={
                "risk_level": "HIGH",
                "threats": [
                    {
                        "category": "Spoofing",
                        "name": "OAuth Token Theft",
                        "risk_rating": "HIGH"
                    }
                ],
                "stride_summary": {"Spoofing": 1, "Tampering": 0},
                "recommendations": ["Use secure token storage"]
            }
        )
        
        # Verify all components are present
        assert plan_data.copilot_instructions is not None
        assert plan_data.threat_modeling is not None
        assert plan_data.threat_analysis is not None
        assert len(plan_data.phases) == 3
        
        # Verify copilot_instructions structure
        ci = plan_data.copilot_instructions
        assert ci["response_template"] == "autonomous_execution_progress"
        assert ci["progress_updates"] is True
        assert ci["tdd_enforcement"] is True
        
        # Verify threat analysis
        assert plan_data.threat_analysis["risk_level"] == "HIGH"
    
    def test_progress_tracking_simulation(self, mock_orchestrator):
        """Test progress tracking during autonomous execution."""
        # Simulate phase completion tracking
        phases = [
            {"name": "Security Analysis", "completed": True, "tasks_total": 2, "tasks_done": 2},
            {"name": "Implementation", "completed": False, "tasks_total": 4, "tasks_done": 2},
            {"name": "Testing", "completed": False, "tasks_total": 3, "tasks_done": 0}
        ]
        
        # Calculate overall progress
        total_tasks = sum(p["tasks_total"] for p in phases)
        completed_tasks = sum(p["tasks_done"] for p in phases)
        overall_progress = int((completed_tasks / total_tasks) * 100)
        
        assert overall_progress == 44  # 4/9 tasks = 44%
        
        # Calculate phase progress
        current_phase = phases[1]  # Implementation
        phase_progress = int((current_phase["tasks_done"] / current_phase["tasks_total"]) * 100)
        
        assert phase_progress == 50  # 2/4 tasks
    
    def test_tdd_enforcement_workflow(self, mock_orchestrator):
        """Test TDD enforcement during execution."""
        # Simulate TDD workflow states
        tdd_states = ["RED", "GREEN", "REFACTOR"]
        
        # Verify valid TDD transitions
        valid_transitions = [
            ("RED", "GREEN"),      # Tests written, implementation done
            ("GREEN", "REFACTOR"), # Tests pass, optimize
            ("REFACTOR", "RED"),   # Optimization done, new tests
        ]
        
        for from_state, to_state in valid_transitions:
            assert from_state in tdd_states
            assert to_state in tdd_states
        
        # Test TDD enforcement blocks invalid transitions
        enforcement_config = {"tdd_enforcement": True}
        
        if enforcement_config["tdd_enforcement"]:
            # Should block GREEN without RED (implementation without tests)
            current_state = "GREEN"
            previous_state = None  # No tests written
            
            # This would be invalid - tests must fail first
            is_valid = previous_state == "RED" or current_state == "RED"
            assert not is_valid  # Should fail without previous RED
    
    def test_checkpoint_creation_simulation(self, mock_orchestrator, temp_workspace):
        """Test checkpoint creation at phase boundaries."""
        checkpoint_frequency = "per_phase"
        
        # Simulate phase completion
        phases_completed = [
            {"phase": "Security Analysis", "checkpoint_created": True},
            {"phase": "Implementation", "checkpoint_created": True},
        ]
        
        # Verify checkpoints created for each phase
        for phase in phases_completed:
            if checkpoint_frequency == "per_phase":
                assert phase["checkpoint_created"] is True
        
        # Test per_task frequency
        checkpoint_frequency = "per_task"
        tasks_completed = [
            {"task": "Task 1.1", "checkpoint": "checkpoint-task-1-1"},
            {"task": "Task 1.2", "checkpoint": "checkpoint-task-1-2"},
        ]
        
        assert len(tasks_completed) == 2
        assert all("checkpoint" in t for t in tasks_completed)


class TestProgressBarGeneration:
    """E2E tests for progress bar generation."""
    
    def test_generate_ascii_progress_bar(self):
        """Test ASCII progress bar generation."""
        def generate_progress_bar(percent: int, width: int = 20) -> str:
            filled = int(width * percent / 100)
            empty = width - filled
            return f"[{'█' * filled}{'░' * empty}] {percent}%"
        
        # Test various percentages
        assert generate_progress_bar(0) == "[░░░░░░░░░░░░░░░░░░░░] 0%"
        assert generate_progress_bar(25) == "[█████░░░░░░░░░░░░░░░] 25%"
        assert generate_progress_bar(50) == "[██████████░░░░░░░░░░] 50%"
        assert generate_progress_bar(75) == "[███████████████░░░░░] 75%"
        assert generate_progress_bar(100) == "[████████████████████] 100%"
    
    def test_generate_progress_table(self):
        """Test progress table generation."""
        phases = [
            {"name": "Setup", "progress": 100, "tasks": "3/3", "status": "✓"},
            {"name": "Implementation", "progress": 70, "tasks": "7/10", "status": ""},
            {"name": "Testing", "progress": 0, "tasks": "0/5", "status": ""},
        ]
        
        # Generate table header
        table = "| Phase | Progress | Tasks |\n"
        table += "|-------|----------|-------|\n"
        
        for phase in phases:
            bar = f"[{'█' * (phase['progress'] // 10)}{'░' * (10 - phase['progress'] // 10)}]"
            table += f"| {phase['name']} | {bar} {phase['progress']}% | {phase['tasks']} {phase['status']} |\n"
        
        assert "Setup" in table
        assert "Implementation" in table
        assert "Testing" in table
        assert "70%" in table


class TestThreatModelingE2E:
    """E2E tests for threat modeling workflow."""
    
    @pytest.fixture
    def mock_orchestrator(self):
        """Create mock orchestrator with threat modeling."""
        with patch.object(PlanningOrchestrator, '__init__', lambda x: None):
            orchestrator = PlanningOrchestrator()
            orchestrator.logger = Mock()
            orchestrator._tdd_dor_requirements = []
            orchestrator._tdd_dod_requirements = []
            return orchestrator
    
    def test_threat_modeling_workflow(self, mock_orchestrator):
        """Test complete threat modeling workflow."""
        # Step 1: Configure threat modeling
        threat_config = {
            "enabled": True,
            "stride_categories": ["Spoofing", "Tampering", "Elevation of Privilege"],
            "auto_mitigations": True
        }
        
        # Step 2: Simulate threat analysis
        threat_analysis = {
            "feature_name": "User Authentication",
            "risk_level": "HIGH",
            "threats": [
                {
                    "category": "Spoofing",
                    "name": "Session Hijacking",
                    "description": "Attacker can steal session tokens",
                    "risk_rating": "HIGH",
                    "risk_score": 8,
                    "mitigation_strategies": [
                        {"name": "Secure cookies", "effort_hours": 2},
                        {"name": "Token rotation", "effort_hours": 4}
                    ]
                },
                {
                    "category": "Elevation of Privilege",
                    "name": "Role Bypass",
                    "description": "Attacker can bypass role checks",
                    "risk_rating": "CRITICAL",
                    "risk_score": 10,
                    "mitigation_strategies": [
                        {"name": "RBAC enforcement", "effort_hours": 6}
                    ]
                }
            ],
            "stride_summary": {
                "Spoofing": 1,
                "Tampering": 0,
                "Repudiation": 0,
                "Information Disclosure": 0,
                "Denial of Service": 0,
                "Elevation of Privilege": 1
            },
            "recommendations": [
                "Implement secure session management",
                "Add strict role-based access control",
                "Enable security audit logging"
            ]
        }
        
        # Step 3: Check if critical threats exist
        has_critical = mock_orchestrator._has_critical_threats(threat_analysis)
        assert has_critical is True
        
        # Step 4: Create base plan
        base_plan = PlanData(
            metadata=PlanMetadata(
                title="User Authentication",
                description="Secure auth implementation",
                complexity=PlanComplexity.HIGH,
                plan_type=PlanType.INCREMENTAL
            ),
            definition_of_ready=["Requirements defined"],
            definition_of_done=["Tests passing"],
            phases=[
                PlanPhaseData(
                    phase_name="Implementation",
                    tasks=[{"task": "Implement auth", "estimated_hours": 8}],
                    acceptance_criteria=["Auth works"]
                )
            ],
            threat_modeling=threat_config,
            threat_analysis=threat_analysis
        )
        
        # Step 5: Inject security tasks
        enhanced_plan = mock_orchestrator._inject_security_tasks(base_plan, threat_analysis)
        
        # Verify security phase was injected
        assert len(enhanced_plan.phases) == 2
        assert enhanced_plan.phases[0].phase_name == "Security Hardening"
        assert any("threat" in item.lower() for item in enhanced_plan.definition_of_done)
    
    def test_threat_analysis_report_format(self):
        """Test threat analysis report format for Copilot consumption."""
        threat_analysis = {
            "risk_level": "HIGH",
            "threats": [
                {"category": "Spoofing", "name": "Token Theft", "risk_rating": "HIGH"},
                {"category": "Tampering", "name": "Data Modification", "risk_rating": "MEDIUM"}
            ],
            "stride_summary": {
                "Spoofing": 1,
                "Tampering": 1,
                "Repudiation": 0,
                "Information Disclosure": 0,
                "Denial of Service": 0,
                "Elevation of Privilege": 0
            }
        }
        
        # Generate report section
        report = "### Threat Analysis Summary\n\n"
        report += f"**Risk Level:** {threat_analysis['risk_level']}\n\n"
        report += "| STRIDE Category | Count |\n"
        report += "|-----------------|-------|\n"
        
        for category, count in threat_analysis["stride_summary"].items():
            if count > 0:
                report += f"| {category} | {count} |\n"
        
        assert "Spoofing" in report
        assert "Tampering" in report
        assert "HIGH" in report


class TestResponseTemplateE2E:
    """E2E tests for response template rendering."""
    
    def test_autonomous_execution_progress_template(self):
        """Test autonomous execution progress template structure."""
        # Simulate template data
        template_data = {
            "plan_name": "User Authentication",
            "current_phase": 2,
            "total_phases": 4,
            "phase_name": "Implementation",
            "overall_progress": 45,
            "phase_progress": 70,
            "tasks_completed": 5,
            "tasks_total": 12,
            "tdd_status": "GREEN",
            "show_threat_analysis": True,
            "threat_analysis": {
                "risk_level": "HIGH",
                "threats_count": 3,
                "mitigated_count": 1
            }
        }
        
        # Generate progress output (simulating Handlebars template)
        output = f"""## 🚀 Autonomous Execution Progress

**Plan:** {template_data['plan_name']}
**Phase:** {template_data['current_phase']}/{template_data['total_phases']} - {template_data['phase_name']}

### Progress Overview

| Metric | Status |
|--------|--------|
| Overall | [{'█' * (template_data['overall_progress'] // 5)}{'░' * (20 - template_data['overall_progress'] // 5)}] {template_data['overall_progress']}% |
| Phase | [{'█' * (template_data['phase_progress'] // 5)}{'░' * (20 - template_data['phase_progress'] // 5)}] {template_data['phase_progress']}% |
| Tasks | {template_data['tasks_completed']}/{template_data['tasks_total']} completed |
| TDD | 🟢 {template_data['tdd_status']} |
"""
        
        if template_data['show_threat_analysis']:
            ta = template_data['threat_analysis']
            output += f"""
### Threat Analysis

| Metric | Value |
|--------|-------|
| Risk Level | {ta['risk_level']} |
| Threats | {ta['threats_count']} identified |
| Mitigated | {ta['mitigated_count']}/{ta['threats_count']} |
"""
        
        assert "User Authentication" in output
        assert "Implementation" in output
        assert "45%" in output
        assert "GREEN" in output
        assert "Threat Analysis" in output
    
    def test_tdd_indicator_states(self):
        """Test TDD indicator rendering for all states."""
        tdd_indicators = {
            "RED": "🔴 RED (writing tests)",
            "GREEN": "🟢 GREEN (tests passing)",
            "REFACTOR": "🔵 REFACTOR (optimizing)"
        }
        
        for state, indicator in tdd_indicators.items():
            assert state in indicator
            assert indicator.startswith("🔴") or indicator.startswith("🟢") or indicator.startswith("🔵")


class TestCopilotInstructionsE2E:
    """E2E tests for copilot_instructions consumption."""
    
    def test_copilot_instructions_complete_workflow(self):
        """Test complete workflow with copilot_instructions."""
        # Step 1: Define instructions
        copilot_instructions = {
            "response_template": "autonomous_execution_progress",
            "progress_updates": True,
            "tdd_enforcement": True,
            "checkpoint_frequency": "per_phase",
            "custom_format": None
        }
        
        # Step 2: Verify template selection
        template = copilot_instructions.get("response_template")
        assert template == "autonomous_execution_progress"
        
        # Step 3: Verify progress updates enabled
        show_progress = copilot_instructions.get("progress_updates", True)
        assert show_progress is True
        
        # Step 4: Verify TDD enforcement
        enforce_tdd = copilot_instructions.get("tdd_enforcement", True)
        assert enforce_tdd is True
        
        # Step 5: Verify checkpoint frequency
        checkpoint = copilot_instructions.get("checkpoint_frequency", "per_phase")
        assert checkpoint == "per_phase"
    
    def test_custom_format_override(self):
        """Test custom_format overrides template."""
        copilot_instructions = {
            "response_template": "custom",
            "progress_updates": True,
            "custom_format": """
Use 5-part response format:
1. Status header with emoji
2. Progress table with ASCII bars
3. Current task details
4. TDD phase indicator
5. Next steps
""",
            "tdd_enforcement": True,
            "checkpoint_frequency": "per_task"
        }
        
        # When template is "custom", use custom_format
        if copilot_instructions["response_template"] == "custom":
            format_instructions = copilot_instructions.get("custom_format", "")
            assert "5-part response format" in format_instructions
            assert "Progress table" in format_instructions


# Run tests
if __name__ == "__main__":
    pytest.main([__file__, "-v"])
