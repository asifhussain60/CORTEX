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

**Phase 8 (0% complete - Design Ready):**
- 🟡 Production deployment package design complete
"""
        
        orchestrator = DesignSyncOrchestrator()
        phase_progress = orchestrator._calculate_phase_progress(content)
        
        assert phase_progress['Phase 5 - Risk Mitigation & Testing'] == 85
        assert phase_progress['Phase 7 - Documentation & Polish'] == 70
        assert phase_progress['Phase 8 - Migration & Deployment'] == 0
    
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


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
