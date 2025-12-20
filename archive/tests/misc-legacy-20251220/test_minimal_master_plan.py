"""
Tests for minimized master plan generation (Planning System 3.1)

Verifies:
- Minimal master plan format (CORTEX header, exec summary, visual tracker, continuation prompt)
- ASCII progress bar generation
- Phase links to sub-plans
- Continuation prompt updates after each phase
- Token-conscious formatting (< 100 lines for typical plans)

Author: Asif Hussain
Version: 3.1.0
"""

import pytest
from pathlib import Path
from datetime import datetime
import tempfile
import shutil

from src.operations.modules.orchestration.temporary_plan_manager import (
    TemporaryPlanManager,
    TemporaryPlan
)


class TestMinimalMasterPlanGeneration:
    """Test minimal master plan format."""
    
    @pytest.fixture
    def temp_project_root(self):
        """Create temporary project structure."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def manager(self, temp_project_root):
        """Create TemporaryPlanManager instance."""
        return TemporaryPlanManager(temp_project_root)
    
    def test_minimal_master_plan_has_cortex_header(self, manager):
        """Test master plan has CORTEX branding header."""
        # Create temp plan
        temp_plan = manager.create_temporary_plan(
            user_request="Test Feature Implementation",
            complexity_tier=3,
            estimated_time="30min",
            approach="Implement feature with TDD approach",
            phases=[
                {'name': 'Foundation', 'description': 'Setup', 'tasks': ['Task 1']},
                {'name': 'Implementation', 'description': 'Build', 'tasks': ['Task 2']}
            ]
        )
        
        # Approve and convert
        manager.approve_temporary_plan(temp_plan.plan_id)
        master_plan_path = manager.convert_to_full_plan(temp_plan.plan_id)
        
        # Read master plan
        content = master_plan_path.read_text(encoding='utf-8')
        
        # Verify header
        assert '🧠 CORTEX' in content
        assert '**Author:**' in content
        assert 'Asif Hussain' in content
        assert 'github.com/asifhussain60/CORTEX' in content
        assert temp_plan.plan_id in content
    
    def test_minimal_master_plan_has_exec_summary(self, manager):
        """Test master plan has single-paragraph executive summary."""
        temp_plan = manager.create_temporary_plan(
            user_request="Test Feature",
            complexity_tier=2,
            estimated_time="15min",
            approach="Single paragraph approach description here",
            phases=[{'name': 'Phase 1', 'description': 'Desc', 'tasks': ['T1']}]
        )
        
        manager.approve_temporary_plan(temp_plan.plan_id)
        master_plan_path = manager.convert_to_full_plan(temp_plan.plan_id)
        content = master_plan_path.read_text(encoding='utf-8')
        
        # Verify executive summary section
        assert '## 🎯 Executive Summary' in content
        assert 'Single paragraph approach description here' in content
    
    def test_minimal_master_plan_has_ascii_progress_bar(self, manager):
        """Test master plan includes ASCII progress bar."""
        temp_plan = manager.create_temporary_plan(
            user_request="Test",
            complexity_tier=1,
            estimated_time="5min",
            approach="Approach",
            phases=[
                {'name': 'P1', 'description': 'D1', 'tasks': ['T1']},
                {'name': 'P2', 'description': 'D2', 'tasks': ['T2']}
            ]
        )
        
        manager.approve_temporary_plan(temp_plan.plan_id)
        master_plan_path = manager.convert_to_full_plan(temp_plan.plan_id)
        content = master_plan_path.read_text(encoding='utf-8')
        
        # Verify ASCII progress bar present
        assert '**Overall Progress:**' in content
        assert '░' in content or '▓' in content or '█' in content  # ASCII bar characters
        assert '0% (0/2 Phases Complete)' in content
    
    def test_minimal_master_plan_has_phase_links(self, manager):
        """Test master plan links to sub-plans."""
        temp_plan = manager.create_temporary_plan(
            user_request="Multi-Phase Test",
            complexity_tier=3,
            estimated_time="1h",
            approach="Multi-phase approach",
            phases=[
                {'name': 'Foundation', 'description': 'Setup', 'tasks': ['T1']},
                {'name': 'Implementation', 'description': 'Build', 'tasks': ['T2']},
                {'name': 'Testing', 'description': 'Validate', 'tasks': ['T3']}
            ]
        )
        
        manager.approve_temporary_plan(temp_plan.plan_id)
        master_plan_path = manager.convert_to_full_plan(temp_plan.plan_id)
        content = master_plan_path.read_text(encoding='utf-8')
        
        # Verify phase links
        assert '[Foundation](sub-plans/phase-01-foundation.md)' in content
        assert '[Implementation](sub-plans/phase-02-implementation.md)' in content
        assert '[Testing](sub-plans/phase-03-testing.md)' in content
        
        # Verify visual tracker table with time tracking
        assert '| Phase | Name | Status | Actual | Elapsed |' in content
        assert '⏸️ PENDING' in content
        
        # Verify time tracking summary
        assert 'Total Actual:' in content
        assert 'Total Elapsed:' in content
    
    def test_minimal_master_plan_has_continuation_prompt(self, manager):
        """Test master plan has copy-paste ready continuation prompt."""
        temp_plan = manager.create_temporary_plan(
            user_request="Test Plan",
            complexity_tier=2,
            estimated_time="20min",
            approach="Test approach",
            phases=[{'name': 'Phase 1', 'description': 'D', 'tasks': ['T']}]
        )
        
        manager.approve_temporary_plan(temp_plan.plan_id)
        master_plan_path = manager.convert_to_full_plan(temp_plan.plan_id)
        content = master_plan_path.read_text(encoding='utf-8')
        
        # Verify continuation prompt
        assert '## 🔄 Continuation Prompt' in content
        assert '**COPY-PASTE THIS TO RESUME WORK:**' in content
        assert f'Continue work on plan `{temp_plan.plan_id}`' in content
        assert 'Follow TDD workflow (RED→GREEN→REFACTOR)' in content
        assert '```markdown' in content  # Code block for easy copy-paste
    
    def test_master_plan_is_token_conscious(self, manager):
        """Test master plan is minimal (< 100 lines for typical plans)."""
        temp_plan = manager.create_temporary_plan(
            user_request="Typical Feature",
            complexity_tier=3,
            estimated_time="45min",
            approach="Standard implementation approach",
            phases=[
                {'name': f'Phase {i}', 'description': f'Desc {i}', 'tasks': [f'Task {i}']}
                for i in range(1, 6)  # 5 phases (typical Tier 3 plan)
            ]
        )
        
        manager.approve_temporary_plan(temp_plan.plan_id)
        master_plan_path = manager.convert_to_full_plan(temp_plan.plan_id)
        content = master_plan_path.read_text(encoding='utf-8')
        
        # Count lines
        line_count = len(content.split('\n'))
        
        # Verify minimal (< 100 lines for 5-phase plan)
        assert line_count < 100, f"Master plan too long: {line_count} lines (expected < 100)"
    
    def test_continuation_prompt_updates_after_phase_completion(self, manager):
        """Test continuation prompt updates when phase completes."""
        # Create and approve plan
        temp_plan = manager.create_temporary_plan(
            user_request="Multi-Phase Test",
            complexity_tier=3,
            estimated_time="1h",
            approach="Test approach",
            phases=[
                {'name': 'Foundation', 'description': 'Setup', 'tasks': ['T1']},
                {'name': 'Implementation', 'description': 'Build', 'tasks': ['T2']}
            ]
        )
        
        manager.approve_temporary_plan(temp_plan.plan_id)
        master_plan_path = manager.convert_to_full_plan(temp_plan.plan_id)
        
        # Initial state
        content = master_plan_path.read_text(encoding='utf-8')
        assert 'Current status: 0/2 phases complete' in content
        assert 'Next: Execute Phase 1 (Foundation)' in content
        
        # Complete Phase 1
        manager.mark_phase_in_progress(temp_plan.plan_id, 1)
        manager.mark_phase_complete(temp_plan.plan_id, 1)
        
        # Verify updated prompt
        content = master_plan_path.read_text(encoding='utf-8')
        assert 'Current status: 1/2 phases complete' in content
        assert 'Phase 1 DONE' in content
        assert 'Next: Execute Phase 2 (Implementation)' in content
    
    def test_progress_bar_updates_as_phases_complete(self, manager):
        """Test ASCII progress bar updates with completion."""
        temp_plan = manager.create_temporary_plan(
            user_request="Test",
            complexity_tier=2,
            estimated_time="30min",
            approach="Test",
            phases=[
                {'name': 'P1', 'description': 'D1', 'tasks': ['T1']},
                {'name': 'P2', 'description': 'D2', 'tasks': ['T2']},
                {'name': 'P3', 'description': 'D3', 'tasks': ['T3']},
                {'name': 'P4', 'description': 'D4', 'tasks': ['T4']}
            ]
        )
        
        manager.approve_temporary_plan(temp_plan.plan_id)
        master_plan_path = manager.convert_to_full_plan(temp_plan.plan_id)
        
        # Complete 2 out of 4 phases
        manager.mark_phase_in_progress(temp_plan.plan_id, 1)
        manager.mark_phase_complete(temp_plan.plan_id, 1)
        manager.mark_phase_in_progress(temp_plan.plan_id, 2)
        manager.mark_phase_complete(temp_plan.plan_id, 2)
        
        content = master_plan_path.read_text(encoding='utf-8')
        
        # Verify progress updated (50%)
        assert '50% (2/4 Phases Complete)' in content
        
        # Verify visual tracker updated
        assert '✅ COMPLETE' in content  # At least one phase complete
    
    def test_all_phases_complete_shows_completion_prompt(self, manager):
        """Test completion prompt when all phases done."""
        temp_plan = manager.create_temporary_plan(
            user_request="Simple Test",
            complexity_tier=1,
            estimated_time="10min",
            approach="Quick test",
            phases=[
                {'name': 'Only Phase', 'description': 'Single phase', 'tasks': ['T1']}
            ]
        )
        
        manager.approve_temporary_plan(temp_plan.plan_id)
        master_plan_path = manager.convert_to_full_plan(temp_plan.plan_id)
        
        # Complete the only phase
        manager.mark_phase_in_progress(temp_plan.plan_id, 1)
        manager.mark_phase_complete(temp_plan.plan_id, 1)
        
        content = master_plan_path.read_text(encoding='utf-8')
        
        # Verify completion message
        assert '**WORK COMPLETE**' in content
        assert 'All 1 phases finished' in content
        assert 'Run knowledge extraction' in content


class TestContinuationPromptQuality:
    """Test continuation prompt quality and usability."""
    
    @pytest.fixture
    def temp_project_root(self):
        """Create temporary project structure."""
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def manager(self, temp_project_root):
        """Create TemporaryPlanManager instance."""
        return TemporaryPlanManager(temp_project_root)
    
    def test_continuation_prompt_has_all_required_context(self, manager):
        """Test prompt includes all necessary context for resumption."""
        temp_plan = manager.create_temporary_plan(
            user_request="Feature X",
            complexity_tier=3,
            estimated_time="45min",
            approach="Approach",
            phases=[
                {'name': 'Phase 1', 'description': 'D1', 'tasks': ['T1']},
                {'name': 'Phase 2', 'description': 'D2', 'tasks': ['T2']}
            ]
        )
        
        manager.approve_temporary_plan(temp_plan.plan_id)
        master_plan_path = manager.convert_to_full_plan(temp_plan.plan_id)
        content = master_plan_path.read_text(encoding='utf-8')
        
        # Required context elements
        assert temp_plan.plan_id in content  # Plan ID
        assert 'phases complete' in content  # Progress
        assert 'Execute Phase' in content  # Next action
        assert 'master-plan.md' in content  # File path
        assert 'TDD workflow' in content  # Methodology reminder
        assert 'continuation prompt' in content  # Self-reference
    
    def test_continuation_prompt_is_single_paragraph(self, manager):
        """Test prompt is concise (single paragraph, token-conscious)."""
        temp_plan = manager.create_temporary_plan(
            user_request="Test",
            complexity_tier=2,
            estimated_time="20min",
            approach="Approach",
            phases=[{'name': 'P1', 'description': 'D', 'tasks': ['T']}]
        )
        
        manager.approve_temporary_plan(temp_plan.plan_id)
        master_plan_path = manager.convert_to_full_plan(temp_plan.plan_id)
        content = master_plan_path.read_text(encoding='utf-8')
        
        # Extract prompt content
        import re
        prompt_match = re.search(r'```markdown\n(.*?)\n```', content, re.DOTALL)
        assert prompt_match, "Prompt markdown block not found"
        
        prompt_content = prompt_match.group(1).strip()
        
        # Verify single paragraph (no double line breaks)
        assert '\n\n' not in prompt_content, "Prompt should be single paragraph"
        
        # Verify reasonable length (< 400 chars - enough for full context)
        assert len(prompt_content) < 400, f"Prompt too long: {len(prompt_content)} chars"
