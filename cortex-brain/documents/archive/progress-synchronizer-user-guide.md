# Progress Synchronizer User Guide

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Date:** December 13, 2025  
**Status:** ✅ PRODUCTION

---

## 🎯 Overview

The **Progress Synchronizer** is a utility that automatically updates visual progress trackers in markdown plan files. Designed for **GitHub Copilot Chat** integration, it ensures progress tracking stays synchronized across master plans, sub-plans, and response templates.

### Key Features

- **Markdown Parsing:** Extracts progress tracker sections from markdown files
- **ASCII Art Generation:** Creates visual progress bars (`[██████████]`) for Copilot Chat
- **Phase Status Updates:** Transitions phases through NOT_STARTED → IN_PROGRESS → COMPLETE
- **Atomic File I/O:** Prevents corruption with temp-file-then-rename pattern
- **Overall Progress Calculation:** Auto-calculates completion percentages
- **Multi-Phase Synchronization:** Updates master and sub-plans simultaneously

---

## 🚀 Quick Start

### Basic Usage

```python
from pathlib import Path
from src.operations.utilities.progress_synchronizer import (
    ProgressSynchronizer,
    PhaseStatus
)

# Load plan file
plan_path = Path("cortex-brain/documents/planning/features/active/master-plan.md")
sync = ProgressSynchronizer(plan_path)
sync.load()

# Update phase to IN_PROGRESS
sync.update_phase(
    phase_number=2,
    status=PhaseStatus.IN_PROGRESS
)

# Mark phase complete with metrics
sync.update_phase(
    phase_number=2,
    status=PhaseStatus.COMPLETE,
    metrics={
        'duration': '3.5 hours',
        'tests_created': 37,
        'test_pass_rate': '100%'
    }
)
```

### Convenience Functions

```python
from src.operations.utilities.progress_synchronizer import (
    update_master_plan_phase,
    update_sub_plan_phase
)

# Update master plan (defaults to CORTEX master plan location)
update_master_plan_phase(
    phase_number=2,
    status=PhaseStatus.COMPLETE
)

# Update sub-plan
update_sub_plan_phase(
    sub_plan_name="phase-2-progress-synchronizer.md",
    phase_number=1,
    status=PhaseStatus.IN_PROGRESS
)
```

---

## 📋 Progress Tracker Format

### Markdown Structure

Progress trackers must be in this format:

```markdown
## Progress Tracker

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    CORTEX ORCHESTRATION + AST ENHANCEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 0: Foundation & Intent Routing     [██████████] 100%  ✅ Complete
PHASE 1: Pre-Flight Orchestrator         [██████████] 100%  ✅ Complete
PHASE 2: Progress Synchronizer           [████░░░░░░]  40%  🚧 In Progress
PHASE 3: Test Failure Analyzer           [          ]   0%  ⏳ Not Started

OVERALL PROGRESS: ████████░░░░░░░░░░░░░░░░░░░░ 2/4 Phases (50%)
```
```

### Key Elements

1. **Code Block:** Enclosed in triple backticks
2. **Separator Lines:** Using `━` characters (flexible - also accepts `═`, `─`, `=`)
3. **Title Line:** Center-aligned project title
4. **Phase Lines:** Format: `PHASE N: Name [progress_bar] percent% emoji status`
5. **Overall Progress:** Summary line with total progress bar

### Flexible Parsing

The parser handles variations:
- Different separator characters: `━`, `═`, `─`, `=`
- Empty progress bars (spaces): `[          ]` for 0%
- Various spacing patterns
- Different title formats

---

## 🎨 ASCII Art Components

### Progress Bars

```python
from src.operations.utilities.progress_synchronizer import ASCIIArtGenerator

# Generate phase progress bar (10 chars)
bar = ASCIIArtGenerator.generate_progress_bar(75)
# Output: [███████░░░]

# Generate overall progress bar (30 chars)
overall = ASCIIArtGenerator.generate_overall_progress_bar(60)
# Output: ██████████████████░░░░░░░░░░░░
```

### Status Emojis

| Status | Emoji | Description |
|--------|-------|-------------|
| NOT_STARTED | ⏳ | Phase not yet begun |
| IN_PROGRESS | 🚧 | Currently working |
| COMPLETE | ✅ | Finished successfully |
| BLOCKED | ⚠️ | Blocked by dependency |

```python
# Format status with emoji
status_text = ASCIIArtGenerator.format_status_emoji(PhaseStatus.IN_PROGRESS)
# Output: "🚧"
```

---

## 🔧 Core Components

### 1. MarkdownParser

Extracts and parses progress tracker sections from markdown files.

```python
from src.operations.utilities.progress_synchronizer import MarkdownParser

parser = MarkdownParser(plan_path)
parser.load()

# Extract tracker info
tracker_info = parser.extract_progress_tracker()

# Access parsed data
for phase in tracker_info.phases:
    print(f"{phase.phase_name}: {phase.progress_percent}%")
```

**Methods:**
- `load()` - Load markdown file
- `extract_progress_tracker()` - Parse tracker section, return `ProgressTrackerInfo`

**Regex Patterns:**
- `PHASE_LINE_PATTERN` - Matches individual phase lines
- `OVERALL_PROGRESS_PATTERN` - Matches overall progress line

### 2. ASCIIArtGenerator

Creates visual progress indicators for Copilot Chat.

```python
from src.operations.utilities.progress_synchronizer import ASCIIArtGenerator

# Progress bars
phase_bar = ASCIIArtGenerator.generate_progress_bar(50, width=10)
overall_bar = ASCIIArtGenerator.generate_overall_progress_bar(75, width=30)

# Status formatting
emoji = ASCIIArtGenerator.format_status_emoji(PhaseStatus.COMPLETE)
```

**Methods:**
- `generate_progress_bar(percent, width=10)` - Phase-level bars
- `generate_overall_progress_bar(percent, width=30)` - Project-level bars
- `format_status_emoji(status)` - Status emoji rendering

### 3. TrackerUpdateEngine

Manages phase status transitions and progress calculations.

```python
from src.operations.utilities.progress_synchronizer import TrackerUpdateEngine

engine = TrackerUpdateEngine(tracker_info)

# Update phase status
engine.update_phase_status(
    phase_number=2,
    new_status=PhaseStatus.COMPLETE,
    completion_date=datetime.now()
)

# Get next phase to work on
next_phase = engine.get_next_phase()
```

**Methods:**
- `update_phase_status()` - Change phase status, update timestamps
- `get_next_phase()` - Find next NOT_STARTED phase
- `_recalculate_overall_progress()` - Auto-calculate completion %

### 4. PhaseSummaryBuilder

Generates completion summaries with metrics.

```python
from src.operations.utilities.progress_synchronizer import PhaseSummaryBuilder

summary = PhaseSummaryBuilder.build_summary(
    phase=phase_info,
    metrics={
        'duration': '3.5 hours',
        'tests_created': 37,
        'test_pass_rate': '100%',
        'lines_of_code': 550
    }
)
print(summary)
```

**Output Format:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ PHASE 2 COMPLETE: Progress Synchronizer
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Status: ✅ Complete
Progress: [██████████] 100%
Duration: 3.5 hours
Start: 2025-12-13 14:00:00
Completion: 2025-12-13 17:30:00

📊 Metrics:
  • tests_created: 37
  • test_pass_rate: 100%
  • lines_of_code: 550
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### 5. ProgressSynchronizer

Main orchestrator - coordinates all components.

```python
from src.operations.utilities.progress_synchronizer import ProgressSynchronizer

sync = ProgressSynchronizer(plan_path)

# Load plan
if not sync.load():
    print("Failed to load plan")
    return

# Update phase
sync.update_phase(
    phase_number=2,
    status=PhaseStatus.COMPLETE,
    metrics={'tests': 37}
)

# Get current status
current = sync.get_current_status()
print(f"Overall: {current['overall_percent']}%")
```

**Methods:**
- `load()` - Initialize from plan file
- `update_phase()` - Update phase status and sync file
- `get_current_status()` - Get current progress snapshot
- `get_next_phase()` - Find next phase to execute

---

## 🔄 Integration with Copilot Chat

### Response Template Integration

Use Progress Synchronizer to generate progress sections for Copilot Chat responses:

```python
from src.operations.utilities.progress_synchronizer import ProgressSynchronizer
from pathlib import Path

def generate_progress_section(plan_name: str) -> str:
    """Generate progress section for Copilot Chat response"""
    plan_path = Path(f"cortex-brain/documents/planning/features/active/{plan_name}")
    
    sync = ProgressSynchronizer(plan_path)
    if not sync.load():
        return "❌ Progress tracker not available"
    
    status = sync.get_current_status()
    
    # Format for Copilot Chat
    return f"""
### 📊 Progress Update

**Overall:** {status['overall_percent']}% ({status['completed']}/{status['total']} phases)

**Current Phase:** {status['current_phase']['name'] if status['current_phase'] else 'All Complete'}

**Status:** {status['current_phase']['status'] if status['current_phase'] else '✅ Complete'}
"""
```

### Orchestrator Integration

Example integration with Planning System 2.0:

```python
from src.operations.utilities.progress_synchronizer import (
    update_master_plan_phase,
    PhaseStatus
)
from datetime import datetime

class PlanningOrchestrator:
    def complete_phase(self, phase_number: int, metrics: dict):
        """Mark phase complete and sync progress"""
        
        # Update master plan
        update_master_plan_phase(
            phase_number=phase_number,
            status=PhaseStatus.COMPLETE,
            completion_date=datetime.now(),
            metrics=metrics
        )
        
        # Generate completion message for Copilot Chat
        return f"✅ Phase {phase_number} complete - Progress tracker updated"
```

### TDD Workflow Integration

```python
from src.operations.utilities.progress_synchronizer import ProgressSynchronizer

class TDDOrchestrator:
    def on_all_tests_passing(self, phase_number: int):
        """Called when TDD cycle completes"""
        
        # Update progress to COMPLETE
        sync = ProgressSynchronizer(self.plan_path)
        sync.load()
        
        sync.update_phase(
            phase_number=phase_number,
            status=PhaseStatus.COMPLETE,
            metrics={
                'tests_created': self.test_count,
                'coverage': f"{self.coverage_percent}%",
                'duration': self.elapsed_time
            }
        )
```

---

## 🎯 Use Cases

### 1. Master Plan Tracking

Track overall project progress across all phases:

```python
# Update master plan when phase completes
from src.operations.utilities.progress_synchronizer import update_master_plan_phase

update_master_plan_phase(
    phase_number=2,
    status=PhaseStatus.COMPLETE,
    metrics={'duration': '3.5 hours', 'tests': 37}
)
```

### 2. Sub-Plan Tracking

Track detailed progress within individual phases:

```python
# Update sub-plan for phase-specific milestones
from src.operations.utilities.progress_synchronizer import update_sub_plan_phase

update_sub_plan_phase(
    sub_plan_name="phase-2-progress-synchronizer.md",
    phase_number=1,  # Implementation milestone
    status=PhaseStatus.COMPLETE
)
```

### 3. Real-Time Updates

Show live progress during long-running operations:

```python
def execute_phase_with_progress(phase_number: int, tasks: list):
    """Execute phase with real-time progress updates"""
    sync = ProgressSynchronizer(plan_path)
    sync.load()
    
    # Mark as in progress
    sync.update_phase(phase_number, PhaseStatus.IN_PROGRESS)
    
    for i, task in enumerate(tasks):
        task.execute()
        
        # Update progress percentage
        percent = int((i + 1) / len(tasks) * 100)
        sync.tracker_info.phases[phase_number].progress_percent = percent
        sync.update_phase(phase_number, PhaseStatus.IN_PROGRESS)
    
    # Mark complete
    sync.update_phase(phase_number, PhaseStatus.COMPLETE)
```

### 4. Batch Updates

Update multiple phases simultaneously:

```python
def complete_batch(phase_numbers: list):
    """Mark multiple phases complete"""
    sync = ProgressSynchronizer(master_plan_path)
    sync.load()
    
    for phase_num in phase_numbers:
        sync.update_phase(
            phase_number=phase_num,
            status=PhaseStatus.COMPLETE
        )
```

---

## 🔍 Advanced Features

### Custom Metrics

Add custom metrics to phase completion summaries:

```python
sync.update_phase(
    phase_number=2,
    status=PhaseStatus.COMPLETE,
    metrics={
        'duration': '3.5 hours',
        'tests_created': 37,
        'test_pass_rate': '100%',
        'files_created': 2,
        'lines_of_code': 550,
        'complexity': 'Medium',
        'performance': '< 1 second'
    }
)
```

### Error Handling

Robust error handling for production use:

```python
from src.operations.utilities.progress_synchronizer import ProgressSynchronizer
from pathlib import Path

def safe_update_phase(plan_path: Path, phase_number: int, status):
    """Update phase with error handling"""
    try:
        sync = ProgressSynchronizer(plan_path)
        
        if not sync.load():
            logger.error(f"Failed to load plan: {plan_path}")
            return False
        
        if not sync.update_phase(phase_number, status):
            logger.error(f"Failed to update phase {phase_number}")
            return False
        
        return True
        
    except Exception as e:
        logger.error(f"Error updating progress: {e}")
        return False
```

### Atomic Updates

Built-in atomic file updates prevent corruption:

```python
# Internally uses temp file + rename pattern
sync.update_phase(2, PhaseStatus.COMPLETE)

# Process:
# 1. Write to temp file: /tmp/tmpXXXXXX.md
# 2. Verify write successful
# 3. Rename temp → original (atomic operation)
# 4. On error: temp file deleted, original unchanged
```

---

## 📊 Data Models

### PhaseStatus (Enum)

```python
class PhaseStatus(Enum):
    NOT_STARTED = "⏳ Not Started"
    IN_PROGRESS = "🚧 In Progress"
    COMPLETE = "✅ Complete"
    BLOCKED = "⚠️ Blocked"
```

### PhaseInfo (Dataclass)

```python
@dataclass
class PhaseInfo:
    phase_id: str              # e.g., "PHASE-2"
    phase_number: int          # e.g., 2
    phase_name: str            # e.g., "PHASE 2: Progress Synchronizer"
    status: PhaseStatus        # Current status
    progress_percent: int      # 0-100
    start_date: Optional[datetime] = None
    completion_date: Optional[datetime] = None
    elapsed_time: Optional[timedelta] = None
```

### ProgressTrackerInfo (Dataclass)

```python
@dataclass
class ProgressTrackerInfo:
    phases: List[PhaseInfo]                    # All phases
    overall_progress_percent: int              # Overall completion %
    total_phases: int                          # Total phase count
    completed_phases: int                      # Completed count
    start_date: Optional[datetime] = None
    target_completion_date: Optional[datetime] = None
    total_elapsed_time: Optional[timedelta] = None
```

---

## 🧪 Testing

The Progress Synchronizer has comprehensive test coverage:

```bash
# Run all tests
pytest tests/unit/operations/utilities/test_progress_synchronizer.py -v

# Run specific test class
pytest tests/unit/operations/utilities/test_progress_synchronizer.py::TestMarkdownParser -v

# Run with coverage
pytest tests/unit/operations/utilities/test_progress_synchronizer.py --cov=src/operations/utilities/progress_synchronizer
```

**Test Coverage:**
- ✅ 37 tests across 8 test classes
- ✅ 100% pass rate
- ✅ Markdown parsing (5 tests)
- ✅ ASCII art generation (8 tests)
- ✅ Tracker updates (6 tests)
- ✅ Phase summaries (2 tests)
- ✅ Integration tests (2 tests)
- ✅ Edge cases (4 tests)
- ✅ Convenience functions (2 tests)

---

## ⚠️ Best Practices

### 1. Always Load Before Update

```python
# ✅ Correct
sync = ProgressSynchronizer(plan_path)
sync.load()  # Load tracker info first
sync.update_phase(2, PhaseStatus.COMPLETE)

# ❌ Wrong
sync = ProgressSynchronizer(plan_path)
sync.update_phase(2, PhaseStatus.COMPLETE)  # Error: No tracker info loaded
```

### 2. Use Convenience Functions for Common Cases

```python
# ✅ Simpler
update_master_plan_phase(2, PhaseStatus.COMPLETE)

# ❌ More verbose
sync = ProgressSynchronizer(Path("cortex-brain/.../master-plan.md"))
sync.load()
sync.update_phase(2, PhaseStatus.COMPLETE)
```

### 3. Include Metrics on Completion

```python
# ✅ Informative
sync.update_phase(
    phase_number=2,
    status=PhaseStatus.COMPLETE,
    metrics={'duration': '3.5h', 'tests': 37}
)

# ❌ Less useful
sync.update_phase(2, PhaseStatus.COMPLETE)
```

### 4. Handle Errors Gracefully

```python
# ✅ Robust
if not sync.load():
    logger.error("Failed to load plan")
    return False

if not sync.update_phase(2, PhaseStatus.COMPLETE):
    logger.error("Failed to update phase")
    return False

# ❌ Fragile
sync.load()
sync.update_phase(2, PhaseStatus.COMPLETE)
```

---

## 🐛 Troubleshooting

### Issue: "No progress tracker found"

**Cause:** Markdown format doesn't match expected pattern

**Solution:** Ensure tracker uses this format:

```markdown
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    TITLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 0: Name     [██████████] 100%  ✅ Complete
```
```

### Issue: Phase not updating

**Cause:** Phase number doesn't exist in tracker

**Solution:** Verify phase numbers match tracker:

```python
status = sync.get_current_status()
print(f"Available phases: {[p['number'] for p in status['phases']]}")
```

### Issue: File corruption

**Cause:** Atomic write failed

**Solution:** Check logs for error details. Original file remains unchanged if atomic write fails.

---

## 📚 References

- **Implementation:** `src/operations/utilities/progress_synchronizer.py`
- **Tests:** `tests/unit/operations/utilities/test_progress_synchronizer.py`
- **Master Plan Template:** `cortex-brain/documents/planning/features/active/MASTER-*.md`
- **Response Templates:** `cortex-brain/response-templates.yaml`

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-12-13 | Initial release - Full implementation with 37 tests |

---

**For questions or issues:** Reference this guide and check test cases for usage examples.
