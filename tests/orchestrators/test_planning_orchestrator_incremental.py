"""
Tests for PlanningOrchestrator incremental planning integration.

Tests Sprint 3 Phase 3: Integration with IncrementalPlanGenerator and StreamingPlanWriter.
"""

import pytest
from pathlib import Path
from src.orchestrators.planning_orchestrator import PlanningOrchestrator


class TestIncrementalPlanningIntegration:
    """Test incremental planning integration in PlanningOrchestrator"""
    
    @pytest.fixture
    def cortex_root(self, tmp_path):
        """Create temporary CORTEX root directory"""
        root = tmp_path / "cortex"
        root.mkdir()
        
        # Create brain directory structure
        brain = root / "cortex-brain"
        brain.mkdir()
        
        # Create documents/planning structure
        planning = brain / "documents" / "planning"
        planning.mkdir(parents=True)
        (planning / "features" / "active").mkdir(parents=True)
        (planning / "features" / "completed").mkdir(parents=True)
        
        # Create config directory for schema
        config = brain / "config"
        config.mkdir()
        
        return root
    
    @pytest.fixture
    def orchestrator(self, cortex_root):
        """Create PlanningOrchestrator instance"""
        return PlanningOrchestrator(str(cortex_root))
    
    def test_orchestrator_has_incremental_generator(self, orchestrator):
        """Test that orchestrator initializes incremental generator"""
        assert hasattr(orchestrator, 'incremental_generator')
        assert orchestrator.incremental_generator is not None
        assert orchestrator.incremental_generator.skeleton_token_limit == 200
        assert orchestrator.incremental_generator.section_token_limit == 500
    
    def test_generate_incremental_plan_auto_approve(self, orchestrator, cortex_root):
        """Test incremental plan generation with auto-approval (no callback)"""
        # Generate plan without callback (auto-approves all checkpoints)
        success, output_path, message = orchestrator.generate_incremental_plan(
            "User authentication system with JWT tokens"
        )
        
        # Verify success
        assert success is True
        assert output_path is not None
        assert output_path.exists()
        assert "generated successfully" in message.lower()
        
        # Verify file content
        content = output_path.read_text()
        assert "User authentication" in content or "Feature Plan" in content
        assert "Phase 1: Foundation" in content
        assert "Phase 2: Development" in content
        assert "Phase 3: Validation & Deployment" in content
        
        # Verify checkpoint markers
        assert "<!-- CHECKPOINT: phase-1-complete -->" in content
        assert "<!-- CHECKPOINT: phase-2-complete -->" in content
        assert "<!-- CHECKPOINT: phase-3-complete -->" in content
    
    def test_generate_incremental_plan_with_approval_callback(self, orchestrator):
        """Test incremental plan generation with user approval callback"""
        checkpoints_called = []
        
        def approval_callback(checkpoint_id, section_name, preview):
            checkpoints_called.append({
                "id": checkpoint_id,
                "section": section_name,
                "preview_length": len(preview)
            })
            return True  # Approve all
        
        success, output_path, message = orchestrator.generate_incremental_plan(
            "REST API for product catalog",
            checkpoint_callback=approval_callback
        )
        
        # Verify success
        assert success is True
        assert output_path is not None
        
        # Verify checkpoint callback was called (skeleton + 3 phases = 4 checkpoints)
        assert len(checkpoints_called) >= 4
        
        # Verify checkpoint IDs
        checkpoint_ids = [cp["id"] for cp in checkpoints_called]
        assert "skeleton" in checkpoint_ids
        assert "phase-1" in checkpoint_ids
        assert "phase-2" in checkpoint_ids
        assert "phase-3" in checkpoint_ids
        
        # Verify all previews have content
        for checkpoint in checkpoints_called:
            assert checkpoint["preview_length"] > 0
    
    def test_generate_incremental_plan_rejection_at_skeleton(self, orchestrator):
        """Test plan rejection at skeleton checkpoint"""
        def rejection_callback(checkpoint_id, section_name, preview):
            if checkpoint_id == "skeleton":
                return False  # Reject skeleton
            return True
        
        success, output_path, message = orchestrator.generate_incremental_plan(
            "Feature X",
            checkpoint_callback=rejection_callback
        )
        
        # Verify failure
        assert success is False
        assert output_path is None
        assert "skeleton rejected" in message.lower()
    
    def test_generate_incremental_plan_rejection_at_phase_1(self, orchestrator):
        """Test plan rejection at Phase 1 checkpoint"""
        def rejection_callback(checkpoint_id, section_name, preview):
            if checkpoint_id == "phase-1":
                return False  # Reject Phase 1
            return True
        
        success, output_path, message = orchestrator.generate_incremental_plan(
            "Feature Y",
            checkpoint_callback=rejection_callback
        )
        
        # Verify failure
        assert success is False
        assert output_path is None
        assert "phase 1 rejected" in message.lower()
    
    def test_generate_incremental_plan_rejection_at_phase_2(self, orchestrator):
        """Test plan rejection at Phase 2 checkpoint"""
        def rejection_callback(checkpoint_id, section_name, preview):
            if checkpoint_id == "phase-2":
                return False  # Reject Phase 2
            return True
        
        success, output_path, message = orchestrator.generate_incremental_plan(
            "Feature Z",
            checkpoint_callback=rejection_callback
        )
        
        # Verify failure
        assert success is False
        assert output_path is None
        assert "phase 2 rejected" in message.lower()
    
    def test_generate_incremental_plan_rejection_at_phase_3(self, orchestrator):
        """Test plan rejection at Phase 3 checkpoint"""
        def rejection_callback(checkpoint_id, section_name, preview):
            if checkpoint_id == "phase-3":
                return False  # Reject Phase 3
            return True
        
        success, output_path, message = orchestrator.generate_incremental_plan(
            "Feature W",
            checkpoint_callback=rejection_callback
        )
        
        # Verify failure
        assert success is False
        assert output_path is None
        assert "phase 3 rejected" in message.lower()
    
    def test_generate_incremental_plan_custom_filename(self, orchestrator):
        """Test incremental plan generation with custom filename"""
        success, output_path, message = orchestrator.generate_incremental_plan(
            "Custom feature",
            output_filename="my-custom-plan.md"
        )
        
        # Verify success
        assert success is True
        assert output_path is not None
        assert output_path.name == "my-custom-plan.md"
        assert output_path.exists()
    
    def test_generate_incremental_plan_token_budgets_enforced(self, orchestrator):
        """Test that token budgets are enforced during generation"""
        success, output_path, message = orchestrator.generate_incremental_plan(
            "Large complex feature with many requirements and detailed specifications"
        )
        
        assert success is True
        assert output_path is not None
        
        # Verify skeleton was within 200 tokens
        skeleton = orchestrator.incremental_generator.skeleton
        skeleton_text = orchestrator.incremental_generator._serialize_skeleton(skeleton)
        skeleton_tokens = orchestrator.incremental_generator.count_tokens(skeleton_text)
        assert skeleton_tokens <= 200
        
        # Verify each section was within 500 tokens
        for section_name, section in orchestrator.incremental_generator.sections.items():
            assert section.token_count <= 500
    
    def test_generate_incremental_plan_all_sections_present(self, orchestrator):
        """Test that all expected sections are generated"""
        success, output_path, message = orchestrator.generate_incremental_plan(
            "Feature ABC"
        )
        
        assert success is True
        
        # Verify all 9 sections exist
        expected_sections = [
            "Requirements", "Dependencies", "Architecture",
            "Implementation", "Tests", "Integration",
            "Acceptance", "Security", "Deployment"
        ]
        
        for section_name in expected_sections:
            assert section_name in orchestrator.incremental_generator.sections
            section = orchestrator.incremental_generator.sections[section_name]
            assert section.status in ["approved", "complete"]  # Accept both statuses
            assert len(section.content) > 0
    
    def test_generate_incremental_plan_metadata_included(self, orchestrator):
        """Test that plan metadata is included in output"""
        success, output_path, message = orchestrator.generate_incremental_plan(
            "Feature with metadata"
        )
        
        assert success is True
        content = output_path.read_text()
        
        # Verify metadata present
        assert "Session ID" in content
        assert "Generated" in content
        assert "Token Budget" in content
        assert "200 skeleton" in content
        assert "500 per section" in content
    
    def test_generate_incremental_plan_phase_structure(self, orchestrator):
        """Test that plan has correct phase structure"""
        success, output_path, message = orchestrator.generate_incremental_plan(
            "Structured feature"
        )
        
        assert success is True
        content = output_path.read_text()
        
        # Verify phase headings
        assert "## Phase 1: Foundation" in content
        assert "## Phase 2: Development" in content
        assert "## Phase 3: Validation & Deployment" in content
        
        # Verify section headings within phases
        assert "### Requirements" in content
        assert "### Dependencies" in content
        assert "### Architecture" in content
        assert "### Implementation" in content
        assert "### Tests" in content
        assert "### Integration" in content
        assert "### Acceptance" in content
        assert "### Security" in content
        assert "### Deployment" in content
    
    def test_generate_incremental_plan_progress_tracking(self, orchestrator):
        """Test that progress is tracked during generation"""
        progress_updates = []
        
        def tracking_callback(checkpoint_id, section_name, preview):
            status = orchestrator.incremental_generator.get_status()
            progress_updates.append({
                "checkpoint": checkpoint_id,
                "current_phase": status["current_phase"],
                "total_tokens": status["total_tokens"]
            })
            return True
        
        success, output_path, message = orchestrator.generate_incremental_plan(
            "Progress tracked feature",
            checkpoint_callback=tracking_callback
        )
        
        assert success is True
        assert len(progress_updates) >= 4
        
        # Verify phases progress through workflow
        phases_seen = [update["current_phase"] for update in progress_updates]
        assert "skeleton_complete" in phases_seen
        assert "phase_1_complete" in phases_seen or "skeleton_complete" in phases_seen
    
    def test_generate_incremental_plan_callback_exception_handling(self, orchestrator):
        """Test that callback exceptions are handled gracefully"""
        def failing_callback(checkpoint_id, section_name, preview):
            if checkpoint_id == "phase-2":
                raise ValueError("Simulated callback error")
            return True
        
        success, output_path, message = orchestrator.generate_incremental_plan(
            "Exception handling test",
            checkpoint_callback=failing_callback
        )
        
        # Should fail gracefully, not crash
        assert success is False
        assert output_path is None


class TestBackwardCompatibility:
    """Test that existing PlanningOrchestrator functionality still works"""
    
    @pytest.fixture
    def cortex_root(self, tmp_path):
        """Create temporary CORTEX root directory"""
        root = tmp_path / "cortex"
        root.mkdir()
        
        brain = root / "cortex-brain"
        brain.mkdir()
        
        planning = brain / "documents" / "planning"
        planning.mkdir(parents=True)
        (planning / "features" / "active").mkdir(parents=True)
        
        config = brain / "config"
        config.mkdir()
        
        return root
    
    @pytest.fixture
    def orchestrator(self, cortex_root):
        """Create PlanningOrchestrator instance"""
        return PlanningOrchestrator(str(cortex_root))
    
    def test_existing_methods_still_work(self, orchestrator):
        """Test that existing orchestrator methods are not broken"""
        # Test schema loading
        assert orchestrator.schema is not None
        
        # Test default schema
        default = orchestrator._get_default_schema()
        assert "schema" in default
        
        # Test validation with minimal plan
        plan_data = {
            "metadata": {
                "plan_id": "TEST-001",
                "title": "Test Plan",
                "created_date": "2025-11-26T00:00:00Z",
                "created_by": "Test",
                "status": "proposed",
                "priority": "medium",
                "estimated_hours": 1.0
            },
            "phases": [
                {
                    "phase_number": 1,
                    "phase_name": "Test Phase",
                    "estimated_hours": 1.0,
                    "tasks": [
                        {
                            "task_id": "1.1",
                            "task_name": "Test Task",
                            "estimated_hours": 1.0
                        }
                    ]
                }
            ],
            "definition_of_ready": ["Ready item 1"],
            "definition_of_done": ["Done item 1"]
        }
        
        is_valid, errors = orchestrator.validate_plan(plan_data)
        assert is_valid is True
        assert len(errors) == 0
    
    def test_generate_markdown_still_works(self, orchestrator):
        """Test that Markdown generation still works"""
        plan_data = {
            "metadata": {
                "plan_id": "MD-001",
                "title": "Markdown Test Plan",
                "created_date": "2025-11-26T00:00:00Z",
                "created_by": "Test",
                "status": "proposed",
                "priority": "high",
                "estimated_hours": 2.0
            },
            "phases": [
                {
                    "phase_number": 1,
                    "phase_name": "Phase 1",
                    "estimated_hours": 2.0,
                    "tasks": [
                        {
                            "task_id": "1.1",
                            "task_name": "Task 1",
                            "estimated_hours": 2.0
                        }
                    ]
                }
            ],
            "definition_of_ready": ["Ready"],
            "definition_of_done": ["Done"]
        }
        
        markdown = orchestrator.generate_markdown(plan_data)
        assert "# Markdown Test Plan" in markdown
        assert "MD-001" in markdown
        assert "Phase 1" in markdown
