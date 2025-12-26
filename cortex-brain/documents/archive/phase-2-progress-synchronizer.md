# Phase 2: Progress Synchronizer Utility

**Phase ID:** CORTEX-ORCH-AST-P2  
**Parent Plan:** MASTER-CORTEX-ORCHESTRATION-AST-ENHANCEMENT-PLAN.md  
**Duration:** Week 2 (3 days)  
**Owner:** Orchestration Team  
**Status:** ⏳ NOT STARTED

---

## 📊 Phase Progress Tracker

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                      PHASE 2: PROGRESS SYNCHRONIZER
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Step 1: Markdown Parser Design       [          ]   0%  ⏳ Not Started
Step 2: Tracker Update Engine        [          ]   0%  ⏳ Not Started
Step 3: ASCII Art Generator          [          ]   0%  ⏳ Not Started
Step 4: Phase Summary Builder        [          ]   0%  ⏳ Not Started
Step 5: Multi-Plan Sync              [          ]   0%  ⏳ Not Started
Step 6: Integration & Testing        [          ]   0%  ⏳ Not Started

PHASE PROGRESS: ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ 0/6 Steps (0%)

START DATE: TBD
TARGET COMPLETION: TBD (+3 days)
ELAPSED TIME: 0d 0h 0m
```

**Legend:** ⏳ Not Started | 🚧 In Progress | ✅ Complete | ⚠️ Blocked

---

## 🎯 Phase Objectives

### Primary Goal
Create standalone utility that automatically updates master plans and sub-plans after phase completion, maintaining accurate visual progress trackers, next steps, and elapsed time counters without manual intervention.

### Success Criteria

| Metric | Target | Measurement Method |
|--------|--------|-------------------|
| Update Accuracy | 100% | Visual tracker matches actual progress |
| Update Speed | < 1 second | Performance benchmark |
| Multi-Plan Sync | 100% | Master + all sub-plans synchronized |
| Breaking Changes | 0 | Markdown structure preserved |
| Test Coverage | > 90% | pytest coverage report |

### Key Deliverables

1. **Progress Synchronizer** (`src/utils/progress_synchronizer.py`, ~300 lines)
2. **Markdown Parser** (section extraction, safe updates)
3. **ASCII Progress Bar Generator** (visual tracker rendering)
4. **Phase Summary Builder** (completion summaries with metrics)
5. **Integration API** (callable from any orchestrator)

---

## 🔍 Problem Statement

### Real-World Evidence: PrevalidationWS Manual Updates

**Before Synchronizer:**
- User manually updated master plan after each phase
- 11 phases × 5 minutes = 55 minutes spent on updates
- Risk of missed updates or inaccurate percentages
- Visual tracker often out of sync with actual progress

**After Synchronizer (Target State):**
- Orchestrator calls `progress_sync.update_phase(phase_id, status="complete")`
- All plans updated in < 1 second
- Zero manual intervention
- 100% accuracy guaranteed

### Current State Issues

**Problem 1: Manual Progress Tracking**
- Orchestrators complete phases but don't update plans
- User must manually edit markdown files
- Error-prone (typos, wrong percentages, missed updates)

**Problem 2: Inconsistent Visual Trackers**
- Different ASCII art styles across plans
- Percentages calculated incorrectly
- Next steps not updated after phase completion

**Problem 3: No Multi-Plan Synchronization**
- Master plan shows 50% complete
- Sub-plan still shows 0% complete
- Inconsistency confuses stakeholders

### Target State Benefits

**Benefit 1: Automated Accuracy**
- Zero human error in progress updates
- Real-time synchronization across all plans
- Visual trackers always match actual state

**Benefit 2: Orchestrator Integration**
- Every orchestrator can update progress
- Standard API: `progress_sync.update_phase(...)`
- Automatic elapsed time calculation

**Benefit 3: Stakeholder Clarity**
- Always up-to-date progress reports
- Consistent visual tracking across all artifacts
- Clear next steps after every phase

---

## 🏗️ Architecture Design

### Component Overview

```
Orchestrator (any)
    ↓
ProgressSynchronizer.update_phase()
    ↓
MarkdownParser
    ├─ Extract progress tracker section
    ├─ Parse current phase statuses
    └─ Identify update target
    ↓
TrackerUpdateEngine
    ├─ Calculate new percentages
    ├─ Update phase status (⏳ → 🚧 → ✅)
    ├─ Recalculate elapsed time
    └─ Update completion timestamps
    ↓
ASCIIArtGenerator
    ├─ Render progress bars [████░░░░]
    ├─ Generate visual tracker
    └─ Format status emojis
    ↓
PhaseSummaryBuilder
    ├─ Generate completion summary
    ├─ Extract metrics (LOC, tests, time)
    └─ Format next steps
    ↓
FileWriter
    ├─ Preserve markdown structure
    ├─ Update only target sections
    └─ Write atomically (temp file → rename)
    ↓
Multi-Plan Sync (if master plan)
    ├─ Update all referenced sub-plans
    └─ Propagate status changes
```

### Progress Tracker Format

**Standard Format:**
```markdown
## 📊 Master Progress Tracker

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
                    CORTEX ORCHESTRATION + AST ENHANCEMENT
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PHASE 0: Foundation & Intent Routing     [██████████]  100%  ✅ Complete
PHASE 1: Pre-Flight Orchestrator         [████░░░░░░]   40%  🚧 In Progress
PHASE 2: Progress Synchronizer           [          ]    0%  ⏳ Not Started
...

OVERALL PROGRESS: ████░░░░░░░░░░░░░░░░░░░░░░░░░░ 2/10 Phases (20%)
                  
ESTIMATED DURATION: 8-10 weeks
START DATE: 2025-12-13
TARGET COMPLETION: 2026-02-28
TOTAL ELAPSED TIME: 5d 12h 30m
```
```

### Update Operations

**Operation 1: Start Phase**
```python
progress_sync.update_phase(
    plan_path="MASTER-PLAN.md",
    phase_id="PHASE_1",
    status="in_progress",
    start_time=datetime.now()
)
```
- Updates status: ⏳ → 🚧
- Records start timestamp
- Updates "Not Started" → "In Progress"

**Operation 2: Complete Phase**
```python
progress_sync.update_phase(
    plan_path="MASTER-PLAN.md",
    phase_id="PHASE_1",
    status="complete",
    end_time=datetime.now(),
    metrics={"loc": 450, "tests": 30, "test_coverage": 92}
)
```
- Updates status: 🚧 → ✅
- Records end timestamp
- Calculates elapsed time
- Updates percentage (40% → 50%)
- Generates phase summary
- Updates overall progress

**Operation 3: Block Phase**
```python
progress_sync.update_phase(
    plan_path="MASTER-PLAN.md",
    phase_id="PHASE_1",
    status="blocked",
    blocker="Missing .NET SDK"
)
```
- Updates status: 🚧 → ⚠️
- Records blocker reason
- Does NOT update percentage
- Alerts stakeholders

---

## 📋 Implementation Steps

### Step 1: Markdown Parser Design (Day 1)
**Duration:** 6 hours  
**Owner:** Senior Engineer

**Tasks:**
- [ ] Create markdown parser module
- [ ] Implement section extractor (find progress tracker)
- [ ] Implement phase line parser (extract status, percentage, emoji)
- [ ] Implement safe update mechanism (preserve structure)
- [ ] Add validation (ensure no corruption)

**Code Structure:**
```python
# src/utils/markdown_parser.py

import re
from pathlib import Path
from typing import Dict, Optional, List

class MarkdownParser:
    """Parse and update markdown plan files."""
    
    TRACKER_SECTION_PATTERN = r"## 📊 (?:Master )?Progress Tracker\n\n```\n(.*?)```"
    PHASE_LINE_PATTERN = r"^(PHASE \d+:.*?)\[(.*?)\]\s+(\d+)%\s+(⏳|🚧|✅|⚠️)\s+(.*)$"
    
    def __init__(self, plan_path: Path):
        self.plan_path = plan_path
        self.content = self._read_file()
        self.tracker_section = self._extract_tracker_section()
        self.phases = self._parse_phases()
    
    def _read_file(self) -> str:
        """Read plan file content."""
        return self.plan_path.read_text(encoding='utf-8')
    
    def _extract_tracker_section(self) -> Optional[str]:
        """Extract progress tracker section."""
        match = re.search(
            self.TRACKER_SECTION_PATTERN,
            self.content,
            re.MULTILINE | re.DOTALL
        )
        return match.group(1) if match else None
    
    def _parse_phases(self) -> Dict[str, PhaseInfo]:
        """Parse phase lines from tracker."""
        if not self.tracker_section:
            return {}
        
        phases = {}
        for line in self.tracker_section.split('\n'):
            match = re.match(self.PHASE_LINE_PATTERN, line)
            if match:
                name, bar, percentage, emoji, status = match.groups()
                phase_id = name.split(':')[0].strip()
                
                phases[phase_id] = PhaseInfo(
                    name=name,
                    progress_bar=bar,
                    percentage=int(percentage),
                    emoji=emoji,
                    status=status.strip(),
                    line=line
                )
        
        return phases
    
    def update_phase(
        self,
        phase_id: str,
        status: str,
        percentage: Optional[int] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None
    ) -> str:
        """Update phase status and return new content."""
        
        if phase_id not in self.phases:
            raise ValueError(f"Phase {phase_id} not found in plan")
        
        phase = self.phases[phase_id]
        
        # Update status emoji
        emoji_map = {
            "not_started": "⏳",
            "in_progress": "🚧",
            "complete": "✅",
            "blocked": "⚠️"
        }
        new_emoji = emoji_map.get(status, phase.emoji)
        
        # Update percentage (if provided)
        if percentage is not None:
            new_percentage = percentage
            new_bar = self._generate_progress_bar(percentage)
        else:
            new_percentage = phase.percentage
            new_bar = phase.progress_bar
        
        # Update status text
        status_map = {
            "not_started": "Not Started",
            "in_progress": "In Progress",
            "complete": "Complete",
            "blocked": "Blocked"
        }
        new_status = status_map.get(status, phase.status)
        
        # Build new phase line
        new_line = f"{phase.name}[{new_bar}] {new_percentage:3d}%  {new_emoji} {new_status}"
        
        # Replace in content
        new_content = self.content.replace(phase.line, new_line)
        
        # Update overall progress
        new_content = self._update_overall_progress(new_content)
        
        # Update elapsed time
        if end_time:
            new_content = self._update_elapsed_time(new_content, end_time)
        
        return new_content
    
    def _generate_progress_bar(self, percentage: int, width: int = 10) -> str:
        """Generate ASCII progress bar."""
        filled = int(width * percentage / 100)
        empty = width - filled
        return '█' * filled + '░' * empty
    
    def _update_overall_progress(self, content: str) -> str:
        """Update overall progress line."""
        completed = sum(1 for p in self.phases.values() if p.emoji == "✅")
        total = len(self.phases)
        percentage = int(completed / total * 100)
        
        # Find and replace overall progress line
        overall_pattern = r"OVERALL PROGRESS: (.*?) (\d+)/(\d+) Phases \((\d+)%\)"
        
        def replace_overall(match):
            bar = self._generate_progress_bar(percentage, width=30)
            return f"OVERALL PROGRESS: {bar} {completed}/{total} Phases ({percentage}%)"
        
        return re.sub(overall_pattern, replace_overall, content)
    
    def _update_elapsed_time(self, content: str, current_time: datetime) -> str:
        """Update total elapsed time."""
        # Extract start date
        start_match = re.search(r"START DATE: (\d{4}-\d{2}-\d{2})", content)
        if not start_match:
            return content
        
        start_date = datetime.strptime(start_match.group(1), "%Y-%m-%d")
        elapsed = current_time - start_date
        
        days = elapsed.days
        hours = elapsed.seconds // 3600
        minutes = (elapsed.seconds % 3600) // 60
        
        elapsed_str = f"{days}d {hours}h {minutes}m"
        
        # Replace elapsed time
        return re.sub(
            r"TOTAL ELAPSED TIME: .*",
            f"TOTAL ELAPSED TIME: {elapsed_str}",
            content
        )
```

**Deliverables:**
- Markdown parser module (200 lines)
- Section extraction logic
- Phase line parsing
- Unit tests (20 test cases)

**Acceptance Criteria:**
- [ ] Extracts tracker section correctly
- [ ] Parses all phase lines
- [ ] Preserves markdown structure
- [ ] Test coverage > 90%

---

### Step 2: Tracker Update Engine (Day 1-2)
**Duration:** 6 hours  
**Owner:** Senior Engineer

**Tasks:**
- [ ] Create update engine module
- [ ] Implement percentage calculator
- [ ] Implement status transition logic
- [ ] Add timestamp tracking
- [ ] Add validation (prevent invalid transitions)

**Code Structure:**
```python
# src/utils/tracker_update_engine.py

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

@dataclass
class PhaseUpdate:
    """Phase update request."""
    phase_id: str
    status: str
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    metrics: Optional[Dict] = None
    blocker: Optional[str] = None

class TrackerUpdateEngine:
    """Engine for updating progress trackers."""
    
    VALID_TRANSITIONS = {
        "not_started": ["in_progress"],
        "in_progress": ["complete", "blocked"],
        "blocked": ["in_progress"],
        "complete": []  # Terminal state
    }
    
    def __init__(self, parser: MarkdownParser):
        self.parser = parser
        self.phase_timestamps = {}
    
    def update(self, update: PhaseUpdate) -> str:
        """Apply phase update and return new content."""
        
        # Validate transition
        current_phase = self.parser.phases.get(update.phase_id)
        if not current_phase:
            raise ValueError(f"Phase {update.phase_id} not found")
        
        current_status = self._emoji_to_status(current_phase.emoji)
        
        if not self._is_valid_transition(current_status, update.status):
            raise ValueError(
                f"Invalid transition: {current_status} → {update.status}"
            )
        
        # Calculate new percentage
        new_percentage = self._calculate_percentage(update)
        
        # Update parser
        new_content = self.parser.update_phase(
            phase_id=update.phase_id,
            status=update.status,
            percentage=new_percentage,
            start_time=update.start_time,
            end_time=update.end_time
        )
        
        # Track timestamps
        if update.start_time:
            self.phase_timestamps[update.phase_id] = {
                "start": update.start_time
            }
        
        if update.end_time:
            self.phase_timestamps[update.phase_id]["end"] = update.end_time
            self.phase_timestamps[update.phase_id]["elapsed"] = (
                update.end_time - self.phase_timestamps[update.phase_id]["start"]
            )
        
        return new_content
    
    def _is_valid_transition(self, from_status: str, to_status: str) -> bool:
        """Check if status transition is valid."""
        return to_status in self.VALID_TRANSITIONS.get(from_status, [])
    
    def _calculate_percentage(self, update: PhaseUpdate) -> int:
        """Calculate new phase percentage."""
        if update.status == "complete":
            return 100
        elif update.status == "in_progress":
            # Calculate based on step completion if available
            return self._estimate_progress(update)
        else:
            return 0
    
    def _estimate_progress(self, update: PhaseUpdate) -> int:
        """Estimate progress for in-progress phases."""
        # If metrics provided, use them
        if update.metrics and "steps_completed" in update.metrics:
            completed = update.metrics["steps_completed"]
            total = update.metrics["total_steps"]
            return int(completed / total * 100)
        
        # Default: 50% for in-progress
        return 50
```

**Deliverables:**
- Update engine module (150 lines)
- Status transition validation
- Percentage calculator
- Unit tests (15 test cases)

**Acceptance Criteria:**
- [ ] Valid transitions enforced
- [ ] Percentages calculated correctly
- [ ] Timestamps tracked
- [ ] Test coverage > 90%

---

### Step 3: ASCII Art Generator (Day 2)
**Duration:** 4 hours  
**Owner:** Engineer

**Tasks:**
- [ ] Create ASCII art generator
- [ ] Implement progress bar rendering ([████░░░░])
- [ ] Implement emoji mapping (⏳ 🚧 ✅ ⚠️)
- [ ] Add configurable bar widths
- [ ] Support multiple styles

**Code Structure:**
```python
# src/utils/ascii_art_generator.py

class ASCIIArtGenerator:
    """Generate ASCII art for progress tracking."""
    
    FILLED_CHAR = '█'
    EMPTY_CHAR = '░'
    
    EMOJI_MAP = {
        "not_started": "⏳",
        "in_progress": "🚧",
        "complete": "✅",
        "blocked": "⚠️"
    }
    
    def generate_progress_bar(
        self,
        percentage: int,
        width: int = 10,
        style: str = "block"
    ) -> str:
        """Generate progress bar string."""
        
        if style == "block":
            filled = int(width * percentage / 100)
            empty = width - filled
            return self.FILLED_CHAR * filled + self.EMPTY_CHAR * empty
        
        elif style == "dots":
            filled = int(width * percentage / 100)
            empty = width - filled
            return '●' * filled + '○' * empty
        
        elif style == "equals":
            filled = int(width * percentage / 100)
            empty = width - filled
            return '=' * filled + '-' * empty
    
    def generate_status_emoji(self, status: str) -> str:
        """Get emoji for status."""
        return self.EMOJI_MAP.get(status, "❓")
    
    def generate_full_tracker(
        self,
        phases: List[Dict],
        title: str = "PROGRESS TRACKER"
    ) -> str:
        """Generate full progress tracker with borders."""
        
        border = "━" * 78
        
        lines = [
            border,
            f"{title.center(78)}",
            border
        ]
        
        for phase in phases:
            bar = self.generate_progress_bar(phase["percentage"])
            emoji = self.generate_status_emoji(phase["status"])
            
            line = (
                f"{phase['name']:<40} "
                f"[{bar}] "
                f"{phase['percentage']:3d}%  "
                f"{emoji} "
                f"{phase['status_text']}"
            )
            lines.append(line)
        
        # Overall progress
        completed = sum(1 for p in phases if p["status"] == "complete")
        total = len(phases)
        overall_pct = int(completed / total * 100)
        overall_bar = self.generate_progress_bar(overall_pct, width=30)
        
        lines.append("")
        lines.append(
            f"OVERALL PROGRESS: {overall_bar} "
            f"{completed}/{total} Phases ({overall_pct}%)"
        )
        
        return "\n".join(lines)
```

**Deliverables:**
- ASCII art generator (100 lines)
- Multiple bar styles
- Full tracker generation
- Unit tests (10 test cases)

**Acceptance Criteria:**
- [ ] Progress bars render correctly
- [ ] Emoji mapping works
- [ ] Multiple styles supported
- [ ] Test coverage > 85%

---

### Step 4: Phase Summary Builder (Day 2)
**Duration:** 4 hours  
**Owner:** Engineer

**Tasks:**
- [ ] Create summary builder
- [ ] Extract phase metrics (LOC, tests, time)
- [ ] Generate completion summaries
- [ ] Format next steps
- [ ] Add to plan automatically

**Code Structure:**
```python
# src/utils/phase_summary_builder.py

class PhaseSummaryBuilder:
    """Build phase completion summaries."""
    
    def build_summary(
        self,
        phase_id: str,
        phase_name: str,
        metrics: Dict,
        elapsed_time: timedelta
    ) -> str:
        """Generate phase completion summary."""
        
        summary = f"""
### ✅ {phase_id} Complete

**Completed:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Elapsed Time:** {self._format_timedelta(elapsed_time)}

**Deliverables:**
{self._format_deliverables(metrics)}

**Metrics:**
{self._format_metrics(metrics)}

**Next Steps:**
{self._format_next_steps(phase_id)}
"""
        return summary.strip()
    
    def _format_deliverables(self, metrics: Dict) -> str:
        """Format deliverables list."""
        deliverables = metrics.get("deliverables", [])
        if not deliverables:
            return "- No deliverables recorded"
        
        return "\n".join(f"- {d}" for d in deliverables)
    
    def _format_metrics(self, metrics: Dict) -> str:
        """Format metrics table."""
        lines = []
        
        if "loc" in metrics:
            lines.append(f"- Lines of Code: {metrics['loc']}")
        
        if "tests" in metrics:
            lines.append(f"- Tests Created: {metrics['tests']}")
        
        if "test_coverage" in metrics:
            lines.append(f"- Test Coverage: {metrics['test_coverage']}%")
        
        if "files_created" in metrics:
            lines.append(f"- Files Created: {metrics['files_created']}")
        
        if "files_modified" in metrics:
            lines.append(f"- Files Modified: {metrics['files_modified']}")
        
        return "\n".join(lines) if lines else "- No metrics available"
    
    def _format_next_steps(self, phase_id: str) -> str:
        """Generate next steps based on phase."""
        # Extract phase number
        phase_num = int(phase_id.split()[1].rstrip(':'))
        next_phase = f"PHASE {phase_num + 1}"
        
        return f"- Proceed to {next_phase}"
    
    def _format_timedelta(self, td: timedelta) -> str:
        """Format timedelta as readable string."""
        hours = td.seconds // 3600
        minutes = (td.seconds % 3600) // 60
        
        if td.days > 0:
            return f"{td.days}d {hours}h {minutes}m"
        elif hours > 0:
            return f"{hours}h {minutes}m"
        else:
            return f"{minutes}m"
```

**Deliverables:**
- Summary builder (120 lines)
- Metrics formatting
- Next steps generation
- Unit tests (8 test cases)

**Acceptance Criteria:**
- [ ] Summaries generated correctly
- [ ] Metrics formatted
- [ ] Next steps accurate
- [ ] Test coverage > 85%

---

### Step 5: Multi-Plan Synchronization (Day 3)
**Duration:** 6 hours  
**Owner:** Senior Engineer

**Tasks:**
- [ ] Implement multi-plan sync
- [ ] Detect master/sub-plan relationships
- [ ] Propagate updates to all plans
- [ ] Handle circular references
- [ ] Add transaction-like updates (all or nothing)

**Code Structure:**
```python
# src/utils/multi_plan_synchronizer.py

class MultiPlanSynchronizer:
    """Synchronize progress across multiple plans."""
    
    def __init__(self, plans_directory: Path):
        self.plans_dir = plans_directory
        self.plan_graph = self._build_plan_graph()
    
    def _build_plan_graph(self) -> Dict[str, List[str]]:
        """Build dependency graph of plans."""
        graph = {}
        
        for plan_file in self.plans_dir.glob("**/*.md"):
            content = plan_file.read_text(encoding='utf-8')
            
            # Extract parent plan references
            parent_match = re.search(
                r"\*\*Parent Plan:\*\* (.+\.md)",
                content
            )
            
            if parent_match:
                parent = parent_match.group(1)
                if parent not in graph:
                    graph[parent] = []
                graph[parent].append(str(plan_file.name))
        
        return graph
    
    def sync_update(
        self,
        plan_path: Path,
        phase_update: PhaseUpdate
    ) -> List[Path]:
        """Update plan and synchronize with related plans."""
        
        updated_plans = []
        
        # Update primary plan
        self._update_single_plan(plan_path, phase_update)
        updated_plans.append(plan_path)
        
        # If this is a sub-plan, update parent
        parent = self._get_parent_plan(plan_path)
        if parent:
            self._update_parent_from_subplan(parent, plan_path, phase_update)
            updated_plans.append(parent)
        
        # If this is a master plan, update all sub-plans
        sub_plans = self._get_sub_plans(plan_path)
        for sub_plan in sub_plans:
            # Propagate relevant updates
            self._update_subplan_from_master(sub_plan, phase_update)
            updated_plans.append(sub_plan)
        
        return updated_plans
    
    def _update_single_plan(self, plan_path: Path, update: PhaseUpdate):
        """Update single plan file."""
        parser = MarkdownParser(plan_path)
        engine = TrackerUpdateEngine(parser)
        
        new_content = engine.update(update)
        
        # Atomic write
        temp_file = plan_path.with_suffix('.tmp')
        temp_file.write_text(new_content, encoding='utf-8')
        temp_file.replace(plan_path)
```

**Deliverables:**
- Multi-plan sync module (180 lines)
- Plan dependency graph
- Atomic updates
- Unit tests (15 test cases)

**Acceptance Criteria:**
- [ ] Master/sub-plan sync working
- [ ] No circular reference issues
- [ ] Atomic updates (no partial failures)
- [ ] Test coverage > 88%

---

### Step 6: Integration & Testing (Day 3)
**Duration:** 6 hours  
**Owner:** QA + Integration Engineer

**Tasks:**
- [ ] Create public API for orchestrators
- [ ] Write integration tests
- [ ] Test with real plan files
- [ ] Document usage
- [ ] Create examples

**Public API:**
```python
# src/utils/progress_synchronizer.py (Public API)

from pathlib import Path
from datetime import datetime
from typing import Optional, Dict

class ProgressSynchronizer:
    """Public API for progress synchronization."""
    
    def __init__(self, plans_directory: Path):
        self.multi_sync = MultiPlanSynchronizer(plans_directory)
    
    def start_phase(
        self,
        plan_path: Path,
        phase_id: str
    ) -> None:
        """Mark phase as started."""
        update = PhaseUpdate(
            phase_id=phase_id,
            status="in_progress",
            start_time=datetime.now()
        )
        self.multi_sync.sync_update(plan_path, update)
    
    def complete_phase(
        self,
        plan_path: Path,
        phase_id: str,
        metrics: Optional[Dict] = None
    ) -> None:
        """Mark phase as complete."""
        update = PhaseUpdate(
            phase_id=phase_id,
            status="complete",
            end_time=datetime.now(),
            metrics=metrics or {}
        )
        self.multi_sync.sync_update(plan_path, update)
    
    def block_phase(
        self,
        plan_path: Path,
        phase_id: str,
        blocker: str
    ) -> None:
        """Mark phase as blocked."""
        update = PhaseUpdate(
            phase_id=phase_id,
            status="blocked",
            blocker=blocker
        )
        self.multi_sync.sync_update(plan_path, update)

# Usage Example
progress_sync = ProgressSynchronizer(Path("cortex-brain/documents/planning"))

# Start Phase 1
progress_sync.start_phase(
    Path("MASTER-PLAN.md"),
    "PHASE 1"
)

# Complete Phase 1
progress_sync.complete_phase(
    Path("MASTER-PLAN.md"),
    "PHASE 1",
    metrics={
        "loc": 450,
        "tests": 30,
        "test_coverage": 92,
        "files_created": 3
    }
)
```

**Deliverables:**
- Public API (100 lines)
- Integration tests (25 test cases)
- Usage documentation
- Example code

**Acceptance Criteria:**
- [ ] API intuitive and simple
- [ ] All integration tests pass
- [ ] Documentation complete
- [ ] Examples working

---

## 🧪 Testing Strategy

### Unit Tests (78+ tests)
- Markdown parser (20 tests)
- Update engine (15 tests)
- ASCII generator (10 tests)
- Summary builder (8 tests)
- Multi-plan sync (15 tests)
- Public API (10 tests)

### Integration Tests (25+ tests)
- Full update workflow
- Multi-plan synchronization
- Error handling
- Edge cases (empty plans, malformed trackers)

### Performance Tests (3 benchmarks)
- Update speed (< 1 second)
- Multi-plan sync (< 2 seconds for 10 plans)
- Memory usage (< 50MB)

---

## 📊 Success Metrics

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Update Accuracy | 100% | TBD | ⏳ |
| Update Speed | < 1s | TBD | ⏳ |
| Multi-Plan Sync | 100% | TBD | ⏳ |
| Test Coverage | > 90% | TBD | ⏳ |
| Breaking Changes | 0 | TBD | ⏳ |

---

## 🚧 Risks & Mitigation

### Risk 1: Markdown Corruption
**Probability:** Medium | **Impact:** High

**Mitigation:**
- Extensive testing on real plan files
- Atomic writes (temp file → rename)
- Backup before update
- Validation after update

### Risk 2: Performance with Large Plans
**Probability:** Low | **Impact:** Medium

**Mitigation:**
- Optimize regex patterns
- Cache parsed content
- Update only changed sections
- Performance benchmarks (< 1s target)

---

## 🔗 Dependencies

### Upstream Dependencies
- None (standalone utility)

### Downstream Dependents
- Phase 4: Autonomous Executor (uses progress sync)
- Phase 6: Completion Reporter (reads progress)
- All orchestrators (should call progress sync)

---

## 📚 References

- Master Plan: `MASTER-CORTEX-ORCHESTRATION-AST-ENHANCEMENT-PLAN.md`
- PrevalidationWS Evidence: Chat02 (manual updates)
- Planning System: Progress tracker format

---

## 🔍 Next Steps

1. **Integrate with Orchestrators** - Add progress sync calls to all orchestrators
2. **Monitor Accuracy** - Track update accuracy in production
3. **Optimize Performance** - Profile and optimize if needed

---

**Phase Status:** 🚀 READY TO START  
**Estimated Completion:** Week 2, Day 3  
**Estimated LOC:** 300 (implementation) + 200 (tests) = 500 total

**Author:** Asif Hussain  
**Created:** December 13, 2025  
**Last Updated:** December 13, 2025
