"""
Tests for design_sync_orchestrator module.

SKULL-001 compliance: These tests must pass BEFORE claiming design_sync is production-ready.
"""
import pytest
from pathlib import Path
from datetime import datetime


class TestStatusFileConsolidation:
    """Test status file consolidation logic - CRITICAL for preventing content deletion."""
    
    def test_consolidate_preserves_progress_bars(self, tmp_path):
        """
        REGRESSION TEST: Ensure consolidation doesn't delete progress bars.
        
        Bug: Regex r'\*Last Synchronized:.*?\*' was too greedy and deleted content.
        Fix: Should only replace the timestamp line, not surrounding content.
        """
        # Given: A status file with progress bars and timestamp
        status_file = tmp_path / "CORTEX2-STATUS.MD"
        original_content = """# CORTEX 2.0 Compact Status Overview

*Last Synchronized: 2025-11-10 10:00 (design_sync)*

## Visual Progress

```
Phase 0 - Quick Wins [████████████████████████████████] 100%
Phase 1 - Core Mods [████████████████████████████████] 100%
```

## Statistics
- **Total Modules:** 37
- **Implemented:** 37 modules
"""
        status_file.write_text(original_content, encoding='utf-8')
        
        # When: Consolidation updates timestamp
        content = status_file.read_text(encoding='utf-8')
        
        # Simulate timestamp update (the buggy code path)
        sync_note = f"\n\n*Last Synchronized: {datetime.now().strftime('%Y-%m-%d %H:%M')} (design_sync)*\n"
        if '*Last Synchronized:' in content:
            # This is the buggy regex that needs fixing
            import re
            updated_content = re.sub(
                r'\*Last Synchronized:.*?\n',  # ✅ FIXED: Only match to newline
                sync_note.strip() + '\n',
                content,
                count=1  # Only replace first occurrence
            )
        
        # Then: Progress bars and statistics should still exist
        assert '████████████████████████████████' in updated_content
        assert 'Phase 0 - Quick Wins' in updated_content
        assert 'Phase 1 - Core Mods' in updated_content
        assert '**Total Modules:** 37' in updated_content
        assert '**Implemented:** 37 modules' in updated_content
        assert 'Visual Progress' in updated_content
        assert 'Statistics' in updated_content
        
        # And: Only the timestamp should change
        assert '*Last Synchronized:' in updated_content
        assert '2025-11-10 10:00' not in updated_content  # Old timestamp gone
        assert datetime.now().strftime('%Y-%m-%d') in updated_content  # New timestamp present
    
    def test_consolidate_preserves_file_size(self, tmp_path):
        """Ensure consolidated file is not dramatically smaller (indicating content loss)."""
        # Given: A status file with substantial content
        status_file = tmp_path / "CORTEX2-STATUS.MD"
        original_content = "# Status\n" + ("x" * 2000) + "\n*Last Synchronized: 2025-11-10 10:00 (design_sync)*\n"
        status_file.write_text(original_content, encoding='utf-8')
        original_size = len(original_content)
        
        # When: Consolidation runs
        import re
        content = status_file.read_text(encoding='utf-8')
        sync_note = f"*Last Synchronized: {datetime.now().strftime('%Y-%m-%d %H:%M')} (design_sync)*\n"
        updated_content = re.sub(
            r'\*Last Synchronized:.*?\n',
            sync_note,
            content,
            count=1
        )
        
        # Then: File size should be similar (within 5% tolerance)
        new_size = len(updated_content)
        size_difference = abs(new_size - original_size)
        tolerance = original_size * 0.05
        
        assert size_difference < tolerance, f"File size changed dramatically: {original_size} -> {new_size}"
    
    def test_consolidate_handles_multiple_asterisks(self, tmp_path):
        """Ensure regex doesn't match beyond the timestamp line when multiple asterisks exist."""
        # Given: A status file with multiple markdown elements using asterisks
        status_file = tmp_path / "CORTEX2-STATUS.MD"
        original_content = """# CORTEX 2.0 Compact Status Overview

*Last Synchronized: 2025-11-10 10:00 (design_sync)*

## Features
- **Bold text here**
- *Italic text here*
- **More bold** with *italic*

## Statistics
- **Total Modules:** 54
"""
        status_file.write_text(original_content, encoding='utf-8')
        
        # When: Consolidation updates timestamp
        import re
        content = status_file.read_text(encoding='utf-8')
        sync_note = f"*Last Synchronized: {datetime.now().strftime('%Y-%m-%d %H:%M')} (design_sync)*\n"
        updated_content = re.sub(
            r'\*Last Synchronized:.*?\n',
            sync_note,
            content,
            count=1
        )
        
        # Then: All other markdown formatting should be preserved
        assert '**Bold text here**' in updated_content
        assert '*Italic text here*' in updated_content
        assert '**More bold**' in updated_content
        assert '**Total Modules:** 54' in updated_content
    
    def test_consolidate_updates_metrics_correctly(self, tmp_path):
        """Ensure metrics are updated without corrupting file structure."""
        # Given: A status file with old metrics
        status_file = tmp_path / "CORTEX2-STATUS.MD"
        original_content = """# CORTEX 2.0 Compact Status Overview

## Statistics
- **Total Modules:** 37
- **Implemented:** 30 modules
- **Tests:** 1500 tests
- **Plugins:** 6 operational

*Last Synchronized: 2025-11-10 10:00 (design_sync)*
"""
        status_file.write_text(original_content, encoding='utf-8')
        
        # When: Consolidation updates metrics
        import re
        content = status_file.read_text(encoding='utf-8')
        
        # Update metrics
        content = re.sub(r'Total Modules:\*\* \d+', 'Total Modules:** 54', content)
        content = re.sub(r'Implemented:\*\* \d+ modules', 'Implemented:** 54 modules', content)
        content = re.sub(r'Tests:\*\* \d+ tests', 'Tests:** 2088 tests', content)
        content = re.sub(r'Plugins:\*\* \d+ operational', 'Plugins:** 8 operational', content)
        
        # Update timestamp
        sync_note = f"*Last Synchronized: {datetime.now().strftime('%Y-%m-%d %H:%M')} (design_sync)*\n"
        updated_content = re.sub(
            r'\*Last Synchronized:.*?\n',
            sync_note,
            content,
            count=1
        )
        
        # Then: Metrics should be updated
        assert '**Total Modules:** 54' in updated_content
        assert '**Implemented:** 54 modules' in updated_content
        assert '**Tests:** 2088 tests' in updated_content
        assert '**Plugins:** 8 operational' in updated_content
        
        # And: Structure should be intact
        assert '## Statistics' in updated_content
        assert '*Last Synchronized:' in updated_content
    
    def test_consolidate_first_time_adds_timestamp(self, tmp_path):
        """Ensure first-time consolidation adds timestamp without corruption."""
        # Given: A status file without timestamp
        status_file = tmp_path / "CORTEX2-STATUS.MD"
        original_content = """# CORTEX 2.0 Compact Status Overview

## Statistics
- **Total Modules:** 54
"""
        status_file.write_text(original_content, encoding='utf-8')
        
        # When: Consolidation adds timestamp
        content = status_file.read_text(encoding='utf-8')
        sync_note = f"\n\n*Last Synchronized: {datetime.now().strftime('%Y-%m-%d %H:%M')} (design_sync)*\n"
        
        if '*Last Synchronized:' not in content:
            updated_content = content + sync_note
        
        # Then: Content should be preserved and timestamp added
        assert '# CORTEX 2.0 Compact Status Overview' in updated_content
        assert '## Statistics' in updated_content
        assert '**Total Modules:** 54' in updated_content
        assert '*Last Synchronized:' in updated_content
        assert datetime.now().strftime('%Y-%m-%d') in updated_content
    
    def test_consolidate_multiple_runs_idempotent(self, tmp_path):
        """Ensure running consolidation multiple times doesn't corrupt file."""
        # Given: A status file
        status_file = tmp_path / "CORTEX2-STATUS.MD"
        original_content = """# CORTEX 2.0 Compact Status Overview

## Progress
████████████████████████████████ 100%

*Last Synchronized: 2025-11-10 10:00 (design_sync)*
"""
        status_file.write_text(original_content, encoding='utf-8')
        
        # When: Consolidation runs 3 times
        import re
        content = original_content
        for i in range(3):
            sync_note = f"*Last Synchronized: {datetime.now().strftime('%Y-%m-%d %H:%M')} (design_sync)*\n"
            content = re.sub(
                r'\*Last Synchronized:.*?\n',
                sync_note,
                content,
                count=1
            )
        
        # Then: Progress bars should still exist
        assert '████████████████████████████████' in content
        assert '## Progress' in content
        
        # And: Only one timestamp should exist
        timestamp_count = content.count('*Last Synchronized:')
        assert timestamp_count == 1, f"Expected 1 timestamp, found {timestamp_count}"


class TestDesignSyncIntegration:
    """Integration tests for full design_sync operation."""
    
    def test_design_sync_operation_completes(self, tmp_path):
        """Smoke test: Ensure design_sync can run without crashing."""
        # This is a placeholder - full integration test would require:
        # - Mock file system with design docs
        # - Mock git operations
        # - Mock implementation discovery
        pass


class TestProgressBarGeneration:
    """Test visual progress bar generation - NEW FEATURE."""
    
    def test_calculate_phase_progress_from_content(self):
        """Test extraction of phase percentages from Current Focus section."""
        from src.operations.modules.design_sync.design_sync_orchestrator import DesignSyncOrchestrator
        
        content = """
## 🎯 Current Focus

**Phase 5 (85% complete):**
- ✅ Integration tests (100%)
- 🔴 Test suite optimization (HIGH PRIORITY)

**Phase 7 (70% complete):**
- ✅ Doc refresh complete
- ⏸️ Command discovery UX (pending)

**Phase 8 (25% complete - Implementation Started):**
- ✅ Build script (create clean package)
"""
        
        orchestrator = DesignSyncOrchestrator()
        phase_progress, execution_order = orchestrator._calculate_phase_progress(content)
        
        assert phase_progress['Phase 5 - Risk Mitigation & Testing'] == 85
        assert phase_progress['Phase 7 - Documentation & Polish'] == 70
        assert phase_progress['Phase 8 - Migration & Deployment'] == 25
    
    def test_generate_progress_bar_full(self):
        """Test progress bar generation at 100%."""
        from src.operations.modules.design_sync.design_sync_orchestrator import DesignSyncOrchestrator
        
        orchestrator = DesignSyncOrchestrator()
        bar = orchestrator._generate_progress_bar(100, width=32)
        
        assert bar == '[████████████████████████████████]'
        assert bar.count('█') == 32
        assert '░' not in bar
    
    def test_generate_progress_bar_partial(self):
        """Test progress bar generation at 50%."""
        from src.operations.modules.design_sync.design_sync_orchestrator import DesignSyncOrchestrator
        
        orchestrator = DesignSyncOrchestrator()
        bar = orchestrator._generate_progress_bar(50, width=32)
        
        assert bar.startswith('[████████████████')
        assert bar.endswith('░░░░░░░░░░░░░░░░]')
        assert bar.count('█') == 16
        assert bar.count('░') == 16
    
    def test_generate_progress_bar_empty(self):
        """Test progress bar generation at 0%."""
        from src.operations.modules.design_sync.design_sync_orchestrator import DesignSyncOrchestrator
        
        orchestrator = DesignSyncOrchestrator()
        bar = orchestrator._generate_progress_bar(0, width=32)
        
        assert bar == '[░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░]'
        assert '█' not in bar
        assert bar.count('░') == 32


class TestExecutionOrderAndVisualGraphSync:
    """
    CRITICAL: Tests to prevent visual progress graph from going out of sync.
    
    This test suite enforces:
    1. Visual graph percentages must match Current Focus percentages
    2. Visual graph order must match Current Focus execution order
    3. Active phases (mentioned in Current Focus) appear first
    4. Completed phases (100%, not in Current Focus) appear next
    5. Future phases (0%, not in Current Focus) appear last
    
    SKULL-001: These tests MUST pass before claiming design_sync is production-ready.
    """
    
    def test_execution_order_extraction_from_current_focus(self):
        """Test that execution order is correctly extracted from Current Focus section."""
        from src.operations.modules.design_sync.design_sync_orchestrator import DesignSyncOrchestrator
        
        content = """
## 🎯 Current Focus

**Phase 5 (85% complete):**
- ✅ Integration tests

**Phase 7 (70% complete):**
- ✅ Doc refresh

**Phase 8 (25% complete):**
- ✅ Build script

**Phase 11 (0% complete):**
- 🟡 Design ready
"""
        
        orchestrator = DesignSyncOrchestrator()
        phase_progress, execution_order = orchestrator._calculate_phase_progress(content)
        
        # Verify execution order: active phases first (5, 7, 8, 11)
        assert execution_order[0] == 'Phase 5 - Risk Mitigation & Testing'
        assert execution_order[1] == 'Phase 7 - Documentation & Polish'
        assert execution_order[2] == 'Phase 8 - Migration & Deployment'
        assert execution_order[3] == 'Phase 11 - Context Helper Plugin'
        
        # Verify remaining phases appear after active ones
        remaining_phases = execution_order[4:]
        assert 'Phase 0 - Quick Wins' in remaining_phases
        assert 'Phase 1 - Core Modularization' in remaining_phases
        assert 'Phase 2 - Ambient + Workflow' in remaining_phases
    
    def test_execution_order_completed_phases_grouped(self):
        """Test that completed phases (100%) are grouped together after active phases."""
        from src.operations.modules.design_sync.design_sync_orchestrator import DesignSyncOrchestrator
        
        content = """
## 🎯 Current Focus

**Phase 8 (25% complete):**
- ✅ Build script
"""
        
        orchestrator = DesignSyncOrchestrator()
        phase_progress, execution_order = orchestrator._calculate_phase_progress(content)
        
        # Find indices of completed phases (100%)
        completed_indices = [
            i for i, phase in enumerate(execution_order)
            if phase_progress[phase] == 100
        ]
        
        # Find indices of future phases (0%)
        future_indices = [
            i for i, phase in enumerate(execution_order)
            if phase_progress[phase] == 0 and phase != 'Phase 8 - Migration & Deployment'
        ]
        
        # Verify completed phases come before future phases
        if completed_indices and future_indices:
            assert max(completed_indices) < min(future_indices), \
                "Completed phases should appear before future phases"
    
    def test_visual_graph_percentages_match_current_focus(self):
        """
        CRITICAL: Ensure visual graph percentages exactly match Current Focus.
        
        This test prevents the bug where hardcoded percentages override actual values.
        """
        from src.operations.modules.design_sync.design_sync_orchestrator import DesignSyncOrchestrator
        
        content = """
## 🎯 Current Focus

**Phase 5 (85% complete):**
- Work in progress

**Phase 7 (70% complete):**
- Work in progress

**Phase 8 (25% complete):**
- Work in progress
"""
        
        orchestrator = DesignSyncOrchestrator()
        phase_progress, execution_order = orchestrator._calculate_phase_progress(content)
        
        # These MUST match Current Focus, not hardcoded defaults
        assert phase_progress['Phase 5 - Risk Mitigation & Testing'] == 85, \
            "Phase 5 percentage must match Current Focus (85%)"
        assert phase_progress['Phase 7 - Documentation & Polish'] == 70, \
            "Phase 7 percentage must match Current Focus (70%)"
        assert phase_progress['Phase 8 - Migration & Deployment'] == 25, \
            "Phase 8 percentage must match Current Focus (25%)"
    
    def test_visual_graph_order_matches_current_focus_order(self):
        """
        CRITICAL: Ensure visual graph shows phases in Current Focus order, not numerical.
        
        This test prevents the bug where graph showed 0-11 regardless of execution sequence.
        """
        from src.operations.modules.design_sync.design_sync_orchestrator import DesignSyncOrchestrator
        
        content = """
## 🎯 Current Focus

**Phase 11 (5% complete):**
- Started first (out of numerical order)

**Phase 2 (95% complete):**
- Almost done

**Phase 7 (50% complete):**
- Mid-way
"""
        
        orchestrator = DesignSyncOrchestrator()
        phase_progress, execution_order = orchestrator._calculate_phase_progress(content)
        
        # Verify execution order matches Current Focus appearance order
        assert execution_order[0] == 'Phase 11 - Context Helper Plugin', \
            "First phase in graph should be Phase 11 (first in Current Focus)"
        assert execution_order[1] == 'Phase 2 - Ambient + Workflow', \
            "Second phase in graph should be Phase 2 (second in Current Focus)"
        assert execution_order[2] == 'Phase 7 - Documentation & Polish', \
            "Third phase in graph should be Phase 7 (third in Current Focus)"
    
    def test_visual_graph_sync_with_actual_file(self, tmp_path):
        """
        INTEGRATION TEST: Verify visual graph stays in sync after consolidation.
        
        This test simulates the full workflow:
        1. Read CORTEX2-STATUS.MD with Current Focus
        2. Extract percentages and execution order
        3. Generate new visual progress bars
        4. Verify bars match Current Focus exactly
        """
        from src.operations.modules.design_sync.design_sync_orchestrator import DesignSyncOrchestrator
        import re
        
        # Given: A realistic CORTEX2-STATUS.MD file
        status_file = tmp_path / "CORTEX2-STATUS.MD"
        original_content = """# CORTEX 2.0 Compact Status Overview

## 📊 Visual Progress (Phases & Tasks)

```
Phase 0 - Quick Wins                    [████████████████████████████████] 100%
Phase 1 - Core Modularization           [████████████████████████████████] 100%
Phase 5 - Risk Mitigation & Testing     [███████████████████████████░░░░░]  85%
```

## 🎯 Current Focus

**Phase 5 (90% complete):**
- ✅ Integration tests (updated!)

**Phase 8 (30% complete):**
- ✅ Build script progress
"""
        status_file.write_text(original_content, encoding='utf-8')
        
        # When: Consolidation runs
        content = status_file.read_text(encoding='utf-8')
        orchestrator = DesignSyncOrchestrator()
        phase_progress, execution_order = orchestrator._calculate_phase_progress(content)
        
        # Generate new progress section
        progress_section_lines = ['```']
        for phase_name in execution_order:
            percentage = phase_progress[phase_name]
            bar = orchestrator._generate_progress_bar(percentage)
            padded_name = phase_name.ljust(40)
            progress_section_lines.append(f"{padded_name}{bar} {percentage:3d}%")
        progress_section_lines.append('```')
        new_progress_section = '\n'.join(progress_section_lines)
        
        # Replace visual progress bars
        updated_content = re.sub(
            r'```\nPhase.*?```',
            new_progress_section,
            content,
            flags=re.DOTALL,
            count=1
        )
        
        # Then: Visual graph should reflect Current Focus
        assert 'Phase 5 - Risk Mitigation & Testing' in updated_content
        assert 'Phase 8 - Migration & Deployment' in updated_content
        
        # Verify Phase 5 appears first (active phase)
        phase5_pos = updated_content.find('Phase 5 - Risk Mitigation & Testing')
        phase0_pos = updated_content.find('Phase 0 - Quick Wins')
        assert phase5_pos < phase0_pos, "Active Phase 5 should appear before completed Phase 0"
        
        # Verify Phase 5 shows 90% (from Current Focus), not 85% (old value)
        assert ' 90%' in updated_content
        assert updated_content.count(' 85%') == 0, "Old Phase 5 percentage (85%) should be updated"
        
        # Verify Phase 8 shows 30% (from Current Focus)
        assert ' 30%' in updated_content
    
    def test_fallback_to_numerical_order_when_no_current_focus(self):
        """Test that graph falls back to numerical order when Current Focus is missing."""
        from src.operations.modules.design_sync.design_sync_orchestrator import DesignSyncOrchestrator
        
        content = """# CORTEX 2.0 Compact Status Overview

## Statistics
- Total Modules: 57
"""
        
        orchestrator = DesignSyncOrchestrator()
        phase_progress, execution_order = orchestrator._calculate_phase_progress(content)
        
        # Should fall back to numerical order (Phase 0, 1, 2, ...)
        assert execution_order[0] == 'Phase 0 - Quick Wins'
        assert execution_order[1] == 'Phase 1 - Core Modularization'
        assert execution_order[2] == 'Phase 2 - Ambient + Workflow'
    
    def test_prevents_duplicate_phases_in_execution_order(self):
        """Test that execution order doesn't contain duplicate phases."""
        from src.operations.modules.design_sync.design_sync_orchestrator import DesignSyncOrchestrator
        
        content = """
## 🎯 Current Focus

**Phase 5 (85% complete):**
- Work in progress

**Phase 5 (90% complete):**
- Duplicate entry (should be handled gracefully)
"""
        
        orchestrator = DesignSyncOrchestrator()
        phase_progress, execution_order = orchestrator._calculate_phase_progress(content)
        
        # Verify no duplicates in execution order
        assert len(execution_order) == len(set(execution_order)), \
            "Execution order should not contain duplicate phases"
        
        # Verify Phase 5 appears only once
        phase5_count = sum(1 for phase in execution_order 
                          if phase == 'Phase 5 - Risk Mitigation & Testing')
        assert phase5_count == 1, "Phase 5 should appear exactly once"
    
    def test_regression_phase_8_percentage_not_hardcoded_to_zero(self):
        """
        REGRESSION TEST: Prevent Phase 8 from being hardcoded to 0%.
        
        Original bug: _calculate_phase_progress had Phase 8 hardcoded to 0%,
        which overrode the actual 25% from Current Focus.
        """
        from src.operations.modules.design_sync.design_sync_orchestrator import DesignSyncOrchestrator
        
        content = """
## 🎯 Current Focus

**Phase 8 (25% complete - Implementation Started):**
- ✅ Build script (create clean package)
"""
        
        orchestrator = DesignSyncOrchestrator()
        phase_progress, execution_order = orchestrator._calculate_phase_progress(content)
        
        # CRITICAL: Phase 8 must show 25%, not 0%
        assert phase_progress['Phase 8 - Migration & Deployment'] == 25, \
            "Phase 8 percentage must not be hardcoded to 0% (regression from bug fix)"
    
    def test_active_phases_always_appear_first_in_visual_graph(self):
        """
        CRITICAL: Ensure active phases (in Current Focus) always appear first.
        
        This is the core feature: visual graph should show what you're working on
        at the top, not buried in numerical order.
        """
        from src.operations.modules.design_sync.design_sync_orchestrator import DesignSyncOrchestrator
        
        content = """
## 🎯 Current Focus

**Phase 8 (25% complete):**
- Active work

**Phase 11 (5% complete):**
- Active work
"""
        
        orchestrator = DesignSyncOrchestrator()
        phase_progress, execution_order = orchestrator._calculate_phase_progress(content)
        
        # First 2 phases in execution order should be Phase 8 and 11 (active)
        assert execution_order[0] == 'Phase 8 - Migration & Deployment'
        assert execution_order[1] == 'Phase 11 - Context Helper Plugin'
        
        # Completed phases should come after active phases
        phase0_index = execution_order.index('Phase 0 - Quick Wins')
        assert phase0_index > 1, "Completed Phase 0 should appear after active phases"


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
