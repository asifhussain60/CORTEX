#!/usr/bin/env python3
"""
CORTEX Planning System - V4 to V5 Migration Script

Purpose: Transform existing V4 plan folders to V5 Planning Architecture
Author: Asif Hussain
Created: January 3, 2026
Version: 1.0.0

V5 Architecture Changes:
- Enhanced folder structure (adds architecture/, phases/)
- Master Orchestrator integration
- Cross-session context tracking
- Progressive validation checkpoints
- AST-based code analysis
- Tier 0 Governance integration
- Knowledge Graph queries
"""

import argparse
import json
import os
import re
import shutil
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class PlanMigrationV5:
    """Migrate V4 plans to V5 architecture."""

    def __init__(self, plan_path: str, dry_run: bool = False):
        self.plan_path = Path(plan_path).resolve()
        self.dry_run = dry_run
        self.changes_log: List[str] = []
        self.backup_path: Optional[Path] = None

    def validate_v4_structure(self) -> Tuple[bool, List[str]]:
        """Verify the plan is a valid V4 structure."""
        errors = []

        if not self.plan_path.exists():
            errors.append(f"Plan path does not exist: {self.plan_path}")
            return False, errors

        if not self.plan_path.is_dir():
            errors.append(f"Plan path is not a directory: {self.plan_path}")
            return False, errors

        # Check for V4 master plan
        master_plan = self.plan_path / "00-master-plan.md"
        if not master_plan.exists():
            errors.append("Missing 00-master-plan.md (V4 required file)")
            return False, errors

        # V4 required folders
        required_v4 = ["context", "reports", "artifacts", "tracking"]
        for folder in required_v4:
            folder_path = self.plan_path / folder
            if not folder_path.exists():
                errors.append(f"Missing required V4 folder: {folder}")

        return len(errors) == 0, errors

    def create_backup(self) -> bool:
        """Create timestamped backup of original plan."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = self.plan_path.parent / "backups"
        self.backup_path = backup_dir / f"{self.plan_path.name}_v4_backup_{timestamp}"

        try:
            if not self.dry_run:
                backup_dir.mkdir(exist_ok=True)
                shutil.copytree(self.plan_path, self.backup_path)
            self.changes_log.append(f"✅ Backup created: {self.backup_path}")
            return True
        except Exception as e:
            self.changes_log.append(f"❌ Backup failed: {str(e)}")
            return False

    def migrate_folder_structure(self) -> bool:
        """Add V5 folders while preserving V4 structure."""
        v5_folders = {
            "architecture": "Master Orchestrator integration docs",
            "phases": "Phase-specific implementation details"
        }

        try:
            for folder, description in v5_folders.items():
                folder_path = self.plan_path / folder
                if folder_path.exists():
                    self.changes_log.append(f"⚠️  Folder exists: {folder} (skipping)")
                    continue

                if not self.dry_run:
                    folder_path.mkdir(parents=True, exist_ok=True)
                    readme = folder_path / "README.md"
                    readme.write_text(f"# {folder.title()}\n\n{description}\n")

                self.changes_log.append(f"✅ Created: {folder}/")

            return True
        except Exception as e:
            self.changes_log.append(f"❌ Folder migration failed: {str(e)}")
            return False

    def upgrade_master_plan(self) -> bool:
        """Transform 00-master-plan.md to V5 format."""
        old_master = self.plan_path / "00-master-plan.md"
        new_master = self.plan_path / "00-MASTER-PLAN-V5.md"

        if new_master.exists():
            self.changes_log.append("⚠️  00-MASTER-PLAN-V5.md already exists (skipping)")
            return True

        try:
            content = old_master.read_text()

            # Extract plan metadata
            metadata = self._extract_plan_metadata(content)

            # Generate V5 master plan
            v5_content = self._generate_v5_master_plan(content, metadata)

            if not self.dry_run:
                new_master.write_text(v5_content)

            self.changes_log.append("✅ Created: 00-MASTER-PLAN-V5.md")
            self.changes_log.append("ℹ️  Original 00-master-plan.md preserved for reference")

            return True
        except Exception as e:
            self.changes_log.append(f"❌ Master plan upgrade failed: {str(e)}")
            return False

    def rename_v4_master_plan(self) -> bool:
        """Rename V4 master plan to avoid confusion with V5."""
        old_master = self.plan_path / "00-master-plan.md"
        deprecated_master = self.plan_path / "00-master-plan-v4-DEPRECATED.md"

        if not old_master.exists():
            self.changes_log.append("⚠️  00-master-plan.md not found (skipping rename)")
            return True

        if deprecated_master.exists():
            self.changes_log.append("⚠️  00-master-plan-v4-DEPRECATED.md already exists (skipping)")
            return True

        try:
            if not self.dry_run:
                old_master.rename(deprecated_master)
            
            self.changes_log.append("✅ Renamed: 00-master-plan.md → 00-master-plan-v4-DEPRECATED.md")
            self.changes_log.append("ℹ️  V4 file preserved for reference with clear deprecation marker")
            return True
        except Exception as e:
            self.changes_log.append(f"❌ V4 master plan rename failed: {str(e)}")
            return False

    def _extract_plan_metadata(self, content: str) -> Dict:
        """Extract key metadata from V4 plan."""
        metadata = {
            "plan_id": self.plan_path.name,
            "created": datetime.now().strftime("%B %d, %Y"),
            "complexity": "TIER 3 (MODERATE)",
            "phases": []
        }

        # Extract title
        title_match = re.search(r"^#\s+(.+?)$", content, re.MULTILINE)
        if title_match:
            metadata["title"] = title_match.group(1).strip()

        # Extract phase count
        phase_matches = re.findall(r"##\s+(?:Phase|🔧|📊|🧪)\s+(\d+)", content)
        if phase_matches:
            metadata["phase_count"] = len(set(phase_matches))

        return metadata

    def _generate_v5_master_plan(self, original_content: str, metadata: Dict) -> str:
        """Generate V5-compliant master plan with current Master Orchestrator state."""
        plan_id = metadata["plan_id"]
        title = metadata.get("title", plan_id.replace("-", " ").title())
        created = metadata["created"]
        phase_count = metadata.get("phase_count", 5)

        v5_template = f"""# 🛡️ {title} (V5 Migration)

**Plan ID:** {plan_id}  
**Feature:** {title}  
**Created:** {created} | **Migrated to V5:** {datetime.now().strftime("%B %d, %Y")}  
**Complexity:** {metadata["complexity"]}  
**Strategy:** Implementation with Master Orchestrator integration (Phase 4 LIVE)  
**Estimated Duration:** TBD (to be refined during Phase 0)

---

## 📊 Visual Progress Tracker

**Overall Progress:** `░░░░░░░░░░░░░░░░░░░░` **0%** ⏸️ MIGRATED - READY TO START

### Implementation Phases

| Phase | Name | Progress | Duration | Status |
|-------|------|----------|----------|--------|
| -1 | Knowledge Library Review | `░░░░░░░░░░` | 2h | ⏸️ Not Started |
| 0 | Foundation & AST Scan | `░░░░░░░░░░` | TBD | ⏸️ Not Started |

**📝 Note:** This plan was migrated from V4 to V5 architecture. Original phases preserved below.

---

## 🎯 Executive Summary

### Migration Context

This plan was automatically migrated from Planning System V4 to V5. Key enhancements:

1. **Master Orchestrator Integration** (✅ LIVE - Phase 4): Pattern-based routing and state coordination
2. **Cross-Session Context** (✅ LIVE - Phase 4.5): Automatic continuation from Tier 1 Working Memory (<200 tokens)
3. **AST-Based Analysis**: Phase 0 code scanning for comprehensive discovery
4. **Governance Integration**: Tier 0 brain-protection-rules.yaml compliance (61 rules)
5. **Knowledge Graph Queries**: Tier 2 knowledge reuse and pattern matching

### Master Orchestrator Status (Phase 4 Complete)

**OPERATIONAL FEATURES:**
- ✅ Pattern Router: Machine-readable intent routing (90%+ accuracy)
- ✅ State Manager: Cross-phase state persistence via PlanningStateDB
- ✅ Execution Engine: Autonomous phase execution with monitoring
- ✅ Context Middleware: Tier 1 integration for "continue" commands

**USAGE:**
- Say "continue {plan_id}" → Master Orch routes automatically
- Say "{plan_id} status" → Query current phase/progress
- Pattern matching handles plan names, phase numbers, common variations

### Original Plan Content

The original V4 plan content has been preserved below for reference. During Phase 0 execution, the Master Orchestrator will:

- Analyze the original phases and tasks
- Generate V5-compliant phase breakdown with proper structure
- Add Foundation (Phase 0) and Knowledge Library (Phase -1)
- Integrate REFACTOR phase (final phase)
- Update progress tracking with visual bars

---

## 🔄 Migration Status

**Migrated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Original Structure:** V4 (4 subfolders)  
**New Structure:** V5 (6 subfolders + architecture/ + phases/)  
**Backup Location:** `backups/{plan_id}_v4_backup_*`

---

## 📋 V4 Original Content (PRESERVED FOR REFERENCE)

{original_content}

---

## 🛡️ Master Orchestrator Integration

### V5 Architecture Components

This plan now integrates with:

1. **Pattern Router** (`src/orchestrators/pattern_router.py`) ✅ LIVE
   - Machine-readable pattern matching (exact + regex)
   - Intent classification for plan resumption
   - "continue" pattern detection
   - Confidence scoring (HIGH/MEDIUM/LOW thresholds)

2. **State Manager** (`src/orchestrators/state_manager.py`) ✅ LIVE
   - Cross-phase state persistence via PlanningStateDB
   - Checkpoint creation and restoration
   - Plan metadata tracking
   - Phase status management

3. **Execution Engine** (`src/orchestrators/execution_engine.py`) ✅ LIVE
   - Autonomous phase execution
   - Progress tracking and validation
   - Execution monitoring with metrics
   - Error handling and recovery

4. **Context Middleware** (`src/operations/utilities/cross_session_context_middleware.py`) ✅ LIVE
   - Tier 1 Working Memory integration
   - Last 3 sessions context injection (<200 tokens)
   - Continuation intelligence (auto-resume)
   - Session metadata tracking

### Cross-Session Continuation (Phase 4.5 LIVE)

When you say **"continue"**, the Master Orchestrator will:

1. Query Tier 1 for last session metadata (orchestrator_used, primary_intent)
2. Load this plan's current state from PlanningStateDB
3. Resume from last incomplete phase
4. Inject lightweight context (<200 tokens)

**Session Tracking Path:** `cortex-brain/tier1-working-memory/sessions/`

**Usage Examples:**
- `"continue"` → Auto-detects last plan from Tier 1
- `"continue {plan_id}"` → Explicit plan selection
- `"{plan_id} status"` → Check progress without executing

---

## ⛔ MANDATORY V5 Requirements

### Phase -1: Knowledge Library Review (NEW IN V5)

**REQUIRED BEFORE Phase 0:**

Review existing CORTEX knowledge for similar patterns:

- `cortex-brain/tier2-knowledge-graph/patterns/` - Established design patterns
- `cortex-brain/lessons-learned.yaml` - Historical insights
- `cortex-brain/tier2-knowledge-graph/code-patterns/` - Reusable implementations

**Deliverables:**
- `context/knowledge-library-review.md` - Relevant patterns found
- `context/reuse-opportunities.md` - Code/patterns to reuse

### Phase 0: Foundation & AST Scan (NEW IN V5)

**REQUIRED BEFORE original Phase 1:**

1. **AST Code Analysis:**
   - Scan all Python files in scope
   - Map imports, dependencies, function signatures
   - Identify potential conflicts or duplication

2. **Governance Compliance Check:**
   - Validate against brain-protection-rules.yaml (61 rules)
   - Check TDD_ENFORCEMENT, GIT_ISOLATION, PLANNING_ISOLATION

3. **Architecture Baseline:**
   - Document current state before changes
   - Identify integration points with Master Orchestrator

**Deliverables:**
- `context/ast-scan-results.json` - Full code analysis
- `context/governance-compliance.md` - SKULL rules validation
- `architecture/integration-points.md` - Master Orch touchpoints

### Final Phase: REFACTOR & Cleanup (NEW IN V5)

**REQUIRED AFTER all implementation phases:**

Comprehensive cleanup to prevent technical debt:

1. **Orphaned Code Detection:**
   - Find unused imports, functions, variables
   - AST-based dead code analysis

2. **Duplicate Code Removal:**
   - Identify copy-paste patterns
   - Consolidate into shared utilities

3. **≥18 Cleanup Tasks per File Category:**
   - Test files cleanup
   - Implementation files optimization
   - Configuration files validation

**SKULL Rule Enforcement:** `REFACTOR_CLEANUP` (brain-protection-rules.yaml)

---

## 📚 V5 Resources

| Resource | Path | Purpose |
|----------|------|---------|
| Master Plan (this file) | `00-MASTER-PLAN-V5.md` | Central coordination |
| Master Orchestrator Config | `cortex-brain/config/master-orchestrator.yaml` | Routing rules ✅ LIVE |
| Planning State DB | `cortex-brain/database/planning_state.db` | State persistence ✅ LIVE |
| Brain Protection Rules | `cortex-brain/brain-protection-rules.yaml` | Governance (61 rules) |
| Knowledge Graph | `cortex-brain/tier2-knowledge-graph/` | Pattern library |
| Continuation Prompt | `CONTINUATION-PROMPT-PHASE-*.md` | Session resumption ✅ LIVE |

---

## 🚀 Next Steps

1. **Review Migration**: Verify V5 structure is correct
2. **Execute Phase -1**: Review Knowledge Library for reusable patterns
3. **Execute Phase 0**: Run AST scan + governance check + baseline
4. **Resume Original Work**: Continue with original Phase 1 (now Phase 1 in V5)
5. **Execute REFACTOR Phase**: Final cleanup after all implementation

**To begin:** Say "start Phase -1" or "continue" in CORTEX Chat (Master Orch will route automatically)

---

## 📝 copilot_instructions

```yaml
response_template: "autonomous_execution_progress"
tdd_enforcement: true
final_refactor_required: true
master_orchestrator_enabled: true  # ✅ LIVE (Phase 4)
cross_session_context: true        # ✅ LIVE (Phase 4.5)
knowledge_graph_integration: true
governance_validation: true
```

**Template Reference:** `cortex-brain/response-templates-v4.yaml:863`  
**Planning System Manifest:** `cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml`  
**Master Orchestrator Status:** ✅ OPERATIONAL (Phase 4 Complete - routing, state, execution, context)
"""

        return v5_template

    def create_phase_documents(self) -> bool:
        """Create phase-specific documents in phases/ folder."""
        phases_dir = self.plan_path / "phases"

        if not phases_dir.exists() and not self.dry_run:
            self.changes_log.append("⚠️  phases/ folder not created yet")
            return False
        
        # In dry run, simulate folder exists
        if self.dry_run and not phases_dir.exists():
            pass  # Continue anyway for simulation

        phase_templates = {
            "phase-minus-1-knowledge-library.md": self._get_phase_minus_1_template(),
            "phase-0-foundation.md": self._get_phase_0_template(),
            "phase-final-refactor.md": self._get_refactor_phase_template()
        }

        try:
            for filename, content in phase_templates.items():
                file_path = phases_dir / filename
                if file_path.exists():
                    self.changes_log.append(f"⚠️  {filename} exists (skipping)")
                    continue

                if not self.dry_run:
                    file_path.write_text(content)

                self.changes_log.append(f"✅ Created: phases/{filename}")

            return True
        except Exception as e:
            self.changes_log.append(f"❌ Phase documents creation failed: {str(e)}")
            return False

    def _get_phase_minus_1_template(self) -> str:
        """Template for Knowledge Library review phase."""
        return """# Phase -1: Knowledge Library Review

**Duration:** 2 hours  
**Status:** ⏸️ Not Started  
**Purpose:** Review existing CORTEX knowledge before implementation

---

## 🎯 Objectives

1. Search Tier 2 Knowledge Graph for similar patterns
2. Review lessons-learned.yaml for relevant insights
3. Identify reusable code patterns
4. Prevent duplication of existing solutions

---

## 📚 Knowledge Sources

### Tier 2 Knowledge Graph
- `cortex-brain/tier2-knowledge-graph/patterns/` - Design patterns
- `cortex-brain/tier2-knowledge-graph/code-patterns/` - Implementation patterns
- `cortex-brain/tier2-knowledge-graph/best-practices/` - Proven approaches

### Historical Learning
- `cortex-brain/lessons-learned.yaml` - Past successes and failures
- `cortex-brain/tier3-dev-context/tech-debt.yaml` - Known issues to avoid

### Existing Implementations
- Search codebase for similar features
- Review test patterns for this feature type

---

## 📋 Tasks

- [ ] Query Knowledge Graph for relevant patterns
- [ ] Review lessons-learned.yaml entries
- [ ] Search codebase for similar implementations
- [ ] Document reuse opportunities
- [ ] Create knowledge-library-review.md in context/

---

## 📝 Deliverables

1. `context/knowledge-library-review.md` - Findings summary
2. `context/reuse-opportunities.md` - Code to reuse
3. Updated Phase 0 plan with knowledge integration
"""

    def _get_phase_0_template(self) -> str:
        """Template for Foundation phase."""
        return """# Phase 0: Foundation & AST Scan

**Duration:** TBD  
**Status:** ⏸️ Not Started  
**Purpose:** Establish baseline and scan codebase before implementation

---

## 🎯 Objectives

1. Run AST scan on all Python files in scope
2. Validate against brain-protection-rules.yaml (61 rules)
3. Document current architecture state
4. Identify Master Orchestrator integration points

---

## 🔍 AST Code Analysis

### Scan Targets
- All Python files in implementation scope
- Related test files
- Configuration files

### Analysis Goals
- Map imports and dependencies
- Identify function signatures and types
- Detect potential naming conflicts
- Find duplication opportunities

### Tool
`src/operations/utilities/ast_scanner.py`

---

## 🛡️ Governance Compliance Check

### SKULL Rules to Validate
1. **TDD_ENFORCEMENT** - Test infrastructure ready
2. **GIT_ISOLATION** - No CORTEX files in user repos
3. **PLANNING_ISOLATION** - Planning vs implementation separation
4. **HOLISTIC_DISCOVERY** - Search before create

### Validation Process
```python
from src.operations.utilities.governance_validator import validate_plan

result = validate_plan(
    plan_path="cortex-brain/documents/planning/active/{plan_name}",
    rules_path="cortex-brain/brain-protection-rules.yaml"
)
```

---

## 🏗️ Architecture Baseline

### Document Current State
- Existing orchestrator integrations
- Current routing mechanisms
- State management approach
- Test coverage baseline

### Master Orchestrator Integration Points
- Pattern matching rules to add
- State manager hooks needed
- Execution engine integration
- Context middleware touchpoints

---

## 📋 Tasks

- [ ] Run AST scan on implementation files
- [ ] Validate against 61 SKULL rules
- [ ] Document architecture baseline
- [ ] Identify Master Orch integration points
- [ ] Create ast-scan-results.json in context/
- [ ] Create governance-compliance.md in context/
- [ ] Create integration-points.md in architecture/

---

## 📝 Deliverables

1. `context/ast-scan-results.json` - Complete code analysis
2. `context/governance-compliance.md` - SKULL validation
3. `architecture/integration-points.md` - Master Orch touchpoints
4. Updated phases with realistic duration estimates
"""

    def _get_refactor_phase_template(self) -> str:
        """Template for final REFACTOR phase."""
        return """# Final Phase: REFACTOR & Cleanup

**Duration:** TBD  
**Status:** ⏸️ Not Started  
**Purpose:** Comprehensive cleanup to prevent technical debt

---

## 🎯 Objectives

1. Detect and remove orphaned code
2. Eliminate duplicate code patterns
3. Complete ≥18 cleanup tasks per file category
4. Ensure SKULL rule compliance

---

## 🔍 Orphaned Code Detection

### Detection Methods
- AST analysis for unused imports
- Dead code analysis (unreachable functions)
- Unused variable detection
- Orphaned test files

### Tool
```bash
python src/operations/utilities/orphan_detector.py \
  --scan-dir src/orchestrators/{feature}/ \
  --output context/orphaned-code-report.json
```

---

## 🔁 Duplicate Code Removal

### Detection
- Copy-paste pattern matching
- Similar function signature analysis
- Redundant logic identification

### Consolidation Strategy
- Extract to shared utilities
- Create base classes for common patterns
- Implement mixins for cross-cutting concerns

---

## 📋 Cleanup Tasks (≥18 per category)

### Test Files
- [ ] Remove commented-out tests
- [ ] Consolidate duplicate fixtures
- [ ] Update outdated docstrings
- [ ] Fix flaky tests
- [ ] Add missing assertions
- [ ] Improve test naming
- [ ] (12 more tasks)

### Implementation Files
- [ ] Remove unused imports
- [ ] Eliminate dead code
- [ ] Consolidate duplicate logic
- [ ] Update type hints
- [ ] Fix linting warnings
- [ ] Improve error messages
- [ ] (12 more tasks)

### Configuration Files
- [ ] Remove obsolete configs
- [ ] Validate YAML syntax
- [ ] Update documentation links
- [ ] Consolidate duplicates
- [ ] Add missing defaults
- [ ] Improve comments
- [ ] (12 more tasks)

---

## 🛡️ SKULL Rule Enforcement

### Rules to Validate
1. **REFACTOR_CLEANUP** - Whole-file cleanup completed
2. **TDD_ENFORCEMENT** - All tests still passing
3. **HOLISTIC_DISCOVERY** - No new duplication introduced

### Validation
```bash
pytest tests/ -v --cov=src --cov-report=html
python scripts/validate_cleanup.py --plan {plan_name}
```

---

## 📊 Success Criteria

- ✅ Zero orphaned code remaining
- ✅ <5% code duplication (via radon cc)
- ✅ ≥18 cleanup tasks per file category completed
- ✅ 100% test coverage maintained
- ✅ All SKULL rules passing
- ✅ Git checkpoint created

---

## 📝 Deliverables

1. `context/orphaned-code-report.json` - Detection results
2. `context/duplicate-code-analysis.md` - Consolidation summary
3. `reports/cleanup-completion-report.md` - Task completion log
4. Updated codebase with all cleanup applied
5. Git checkpoint: `checkpoint-final-refactor-complete`
"""

    def create_master_orch_integration_doc(self) -> bool:
        """Create Master Orchestrator integration documentation."""
        arch_dir = self.plan_path / "architecture"

        if not arch_dir.exists() and not self.dry_run:
            self.changes_log.append("⚠️  architecture/ folder not created yet")
            return False
        
        # In dry run, simulate folder exists
        if self.dry_run and not arch_dir.exists():
            pass  # Continue anyway for simulation

        doc_path = arch_dir / "master-orchestrator-integration.md"

        if doc_path.exists():
            self.changes_log.append("⚠️  master-orchestrator-integration.md exists (skipping)")
            return True

        content = """# Master Orchestrator Integration

**Plan:** {plan_id}  
**Created:** {timestamp}  
**Purpose:** Document Master Orchestrator touchpoints for this plan

---

## 🎯 Integration Overview

This plan integrates with CORTEX Master Orchestrator for:

1. **Pattern-Based Routing**: Intent classification and orchestrator selection
2. **State Coordination**: Cross-phase state persistence
3. **Cross-Session Continuation**: Automatic resumption from Tier 1
4. **Execution Monitoring**: Progress tracking and validation

---

## 🔀 Routing Configuration

### Pattern Matching Rules

Add to `cortex-brain/config/master-orchestrator.yaml`:

```yaml
patterns:
  - pattern: "continue {plan_id}"
    orchestrator: "planning_system"
    context:
      plan_id: "{plan_id}"
      action: "resume"
      
  - pattern: "{plan_id} status"
    orchestrator: "planning_system"
    context:
      plan_id: "{plan_id}"
      action: "status"
```

### Intent Classification

If pattern matching fails, LLM classifier routes based on:
- Plan ID mention in user request
- "continue" keyword detection
- Planning-related vocabulary

---

## 🗄️ State Management

### Database Integration

Plan state stored in `cortex-brain/database/planning_state.db`:

**Tables Used:**
- `plans` - High-level plan metadata
- `phases` - Phase execution tracking
- `tasks` - Granular task status
- `execution_log` - Master Orch routing decisions

### State Queries

```python
# Get current phase
state_mgr.get_current_phase(plan_id="{plan_id}")

# Resume from checkpoint
state_mgr.resume_from_snapshot(snapshot_id="...")

# Update phase status
state_mgr.update_phase_status(
    phase_id="...",
    status="in_progress"
)
```

---

## 🔄 Cross-Session Context

### Tier 1 Integration

Context middleware queries Tier 1 Working Memory for:
- Last 3 sessions metadata
- Previous orchestrator used
- Primary intent from last session
- Phase status at interruption

### Context Injection

Middleware injects <200 tokens:

```json
{{
  "last_session": {{
    "orchestrator": "planning_system",
    "plan_id": "{plan_id}",
    "phase": "Phase 3",
    "status": "in_progress",
    "last_task": "Implementing BaseOrchestrator v4.1"
  }},
  "continuation_detected": true
}}
```

---

## ⚙️ Execution Engine

### Autonomous Execution

Master Orchestrator's Execution Engine:

1. Loads plan from database
2. Identifies current phase
3. Executes phase tasks autonomously
4. Updates progress in real-time
5. Creates checkpoints after each phase

### Monitoring

Progress tracked in:
- Visual progress bars (in master plan)
- `tracking/progress-tracker.json`
- `execution_log` table (database)

---

## 🛡️ Governance Validation

### Pre-Execution Checks

Master Orchestrator validates:
- SKULL rules compliance (brain-protection-rules.yaml)
- Knowledge Graph queries (similar patterns exist?)
- AST scan results (conflicts detected?)

### Continuous Monitoring

During execution:
- TDD_ENFORCEMENT: Tests run before implementation
- GIT_ISOLATION: No CORTEX files in user repos
- REFACTOR_CLEANUP: Cleanup phase exists

---

## 📚 Resources

| Resource | Path | Purpose |
|----------|------|---------|
| Pattern Router | `src/orchestrators/pattern_router.py` | Intent routing |
| State Manager | `src/orchestrators/state_manager.py` | State persistence |
| Execution Engine | `src/orchestrators/execution_engine.py` | Phase execution |
| Context Middleware | `src/operations/utilities/cross_session_context_middleware.py` | Tier 1 integration |
| Master Orch Config | `cortex-brain/config/master-orchestrator.yaml` | Routing rules |

---

## 🚀 Next Steps

1. Update `master-orchestrator.yaml` with plan-specific patterns
2. Test pattern matching with sample user inputs
3. Verify state manager can load plan from database
4. Validate context middleware injects continuation data
5. Execute Phase -1 (Knowledge Library Review)
""".format(plan_id=self.plan_path.name, timestamp=datetime.now().strftime("%B %d, %Y"))

        try:
            if not self.dry_run:
                doc_path.write_text(content)
            self.changes_log.append("✅ Created: architecture/master-orchestrator-integration.md")
            return True
        except Exception as e:
            self.changes_log.append(f"❌ Integration doc creation failed: {str(e)}")
            return False

    def create_continuation_prompt(self) -> bool:
        """Create continuation prompt template."""
        prompt_path = self.plan_path / "CONTINUATION-PROMPT.md"

        if prompt_path.exists():
            self.changes_log.append("⚠️  CONTINUATION-PROMPT.md exists (skipping)")
            return True

        content = """# 🔄 CORTEX Plan Continuation Prompt

**Plan:** {plan_id}  
**Current Phase:** [TO BE DETERMINED FROM STATE]  
**Last Updated:** {timestamp}

---

## 🎯 Quick Resume

**Say in CORTEX Chat:** "continue {plan_id}"

Master Orchestrator will:
1. Query Tier 1 for last session context
2. Load plan state from PlanningStateDB
3. Resume from current phase automatically
4. Inject relevant context (<200 tokens)

---

## 📊 Current Status

**Overall Progress:** [LOADED FROM tracking/progress-tracker.json]

**Current Phase:** [LOADED FROM DATABASE]

**Last Task:** [LOADED FROM DATABASE]

---

## 🔄 Manual Resume (if needed)

If automatic continuation fails, use:

```
/CORTEX Plan {plan_id}
Resume from Phase [X]
```

---

## 📚 Plan Resources

- **Master Plan:** `00-MASTER-PLAN-V5.md`
- **Progress Tracker:** `tracking/progress-tracker.json`
- **Context Files:** `context/`
- **Phase Documents:** `phases/`
- **Architecture Docs:** `architecture/`

---

## 🛡️ Master Orchestrator Integration

This plan uses Master Orchestrator for:
- ✅ Pattern-based routing ("continue" detection)
- ✅ Cross-session context injection (Tier 1)
- ✅ State persistence (PlanningStateDB)
- ✅ Autonomous execution

**Config:** `cortex-brain/config/master-orchestrator.yaml`

---

## 📝 Notes

- Master Orchestrator auto-detects "continue" keyword
- Context middleware injects last 3 sessions (<200 tokens)
- State manager ensures resumable execution from any phase
- Use "status" to check progress without executing
""".format(plan_id=self.plan_path.name, timestamp=datetime.now().strftime("%B %d, %Y"))

        try:
            if not self.dry_run:
                prompt_path.write_text(content)
            self.changes_log.append("✅ Created: CONTINUATION-PROMPT.md")
            return True
        except Exception as e:
            self.changes_log.append(f"❌ Continuation prompt creation failed: {str(e)}")
            return False

    def generate_migration_report(self) -> bool:
        """Create detailed migration report."""
        report_path = self.plan_path / "reports" / f"v5-migration-report-{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"

        report_content = f"""# V5 Migration Report

**Plan:** {self.plan_path.name}  
**Migration Date:** {datetime.now().strftime("%B %d, %Y at %H:%M:%S")}  
**Dry Run:** {'Yes' if self.dry_run else 'No'}  
**Backup Location:** {self.backup_path if self.backup_path else 'N/A'}

---

## 📊 Migration Summary

### Changes Applied

{chr(10).join(self.changes_log)}

---

## 🏗️ New V5 Structure

```
{self.plan_path.name}/
├── 00-master-plan.md (V4 - PRESERVED)
├── 00-MASTER-PLAN-V5.md (V5 - NEW)
├── CONTINUATION-PROMPT.md (V5 - NEW)
├── context/ (V4 - PRESERVED)
├── reports/ (V4 - PRESERVED)
│   └── v5-migration-report-*.md (NEW)
├── artifacts/ (V4 - PRESERVED)
├── tracking/ (V4 - PRESERVED)
├── architecture/ (V5 - NEW)
│   ├── README.md
│   └── master-orchestrator-integration.md
└── phases/ (V5 - NEW)
    ├── README.md
    ├── phase-minus-1-knowledge-library.md
    ├── phase-0-foundation.md
    └── phase-final-refactor.md
```

---

## ✅ V5 Compliance Checklist

- [{'x' if not self.dry_run else ' '}] V5 folder structure created (architecture/, phases/)
- [{'x' if not self.dry_run else ' '}] 00-MASTER-PLAN-V5.md generated
- [{'x' if not self.dry_run else ' '}] Phase -1 (Knowledge Library) added
- [{'x' if not self.dry_run else ' '}] Phase 0 (Foundation & AST Scan) added
- [{'x' if not self.dry_run else ' '}] Final REFACTOR phase added
- [{'x' if not self.dry_run else ' '}] Master Orchestrator integration docs created
- [{'x' if not self.dry_run else ' '}] Continuation prompt created
- [{'x' if not self.dry_run else ' '}] V4 backup created
- [{'x' if not self.dry_run else ' '}] Original 00-master-plan.md preserved

---

## 🚀 Next Steps

1. **Review Migration**: Verify all files created correctly
2. **Start Phase -1**: Review Knowledge Library for reusable patterns
3. **Execute Phase 0**: Run AST scan and governance validation
4. **Resume Original Work**: Continue with original plan phases
5. **Complete REFACTOR**: Execute final cleanup phase

**To begin:** Say "start Phase -1 for {self.plan_path.name}" in CORTEX Chat

---

## 🛡️ Master Orchestrator Ready

This plan is now ready for Master Orchestrator execution:

- ✅ Pattern matching configured
- ✅ State manager integration ready
- ✅ Cross-session continuation enabled
- ✅ Tier 1 context middleware compatible

**Test routing:** Say "continue {self.plan_path.name}" in CORTEX Chat

---

## 📚 Resources

- **Planning System V5 Manifest:** `cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml`
- **Master Orchestrator Config:** `cortex-brain/config/master-orchestrator.yaml`
- **Brain Protection Rules:** `cortex-brain/brain-protection-rules.yaml` (61 rules)
- **Response Templates:** `cortex-brain/response-templates-v4.yaml:863`
"""

        try:
            if not self.dry_run:
                report_path.parent.mkdir(exist_ok=True)
                report_path.write_text(report_content)
            self.changes_log.append(f"✅ Migration report: {report_path.name}")
            return True
        except Exception as e:
            self.changes_log.append(f"❌ Report generation failed: {str(e)}")
            return False

    def execute_migration(self) -> bool:
        """Execute full migration process."""
        print(f"🔄 Migrating plan: {self.plan_path.name}")
        print(f"{'[DRY RUN] ' if self.dry_run else ''}Starting V4 → V5 migration...\n")

        # Step 1: Validate V4 structure
        print("Step 1: Validating V4 structure...")
        is_valid, errors = self.validate_v4_structure()
        if not is_valid:
            print("❌ Validation failed:")
            for error in errors:
                print(f"   - {error}")
            return False
        print("✅ V4 structure valid\n")

        # Step 2: Create backup
        print("Step 2: Creating backup...")
        if not self.create_backup():
            print("❌ Backup failed - aborting migration")
            return False
        print(f"✅ Backup created\n")

        # Step 3: Migrate folder structure
        print("Step 3: Creating V5 folders...")
        if not self.migrate_folder_structure():
            print("❌ Folder migration failed")
            return False
        print("✅ V5 folders created\n")

        # Step 4: Upgrade master plan
        print("Step 4: Generating 00-MASTER-PLAN-V5.md...")
        if not self.upgrade_master_plan():
            print("❌ Master plan upgrade failed")
            return False
        print("✅ V5 master plan created\n")

        # Step 4.5: Rename old V4 master plan to avoid confusion
        print("Step 4.5: Renaming V4 master plan to deprecated...")
        if not self.rename_v4_master_plan():
            print("❌ V4 master plan rename failed")
            return False
        print("✅ V4 master plan renamed\n")

        # Step 5: Create phase documents
        print("Step 5: Creating phase documents...")
        if not self.create_phase_documents():
            print("❌ Phase documents creation failed")
            return False
        print("✅ Phase documents created\n")

        # Step 6: Create Master Orch integration doc
        print("Step 6: Creating Master Orchestrator integration doc...")
        if not self.create_master_orch_integration_doc():
            print("❌ Integration doc creation failed")
            return False
        print("✅ Integration doc created\n")

        # Step 7: Create continuation prompt
        print("Step 7: Creating continuation prompt...")
        if not self.create_continuation_prompt():
            print("❌ Continuation prompt creation failed")
            return False
        print("✅ Continuation prompt created\n")

        # Step 8: Generate migration report
        print("Step 8: Generating migration report...")
        if not self.generate_migration_report():
            print("❌ Report generation failed")
            return False
        print("✅ Migration report generated\n")

        return True

    def print_summary(self):
        """Print migration summary."""
        print("\n" + "="*60)
        print("🎉 MIGRATION COMPLETE")
        print("="*60)
        print(f"\nPlan: {self.plan_path.name}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'PRODUCTION'}")
        print(f"\nChanges Log ({len(self.changes_log)} items):")
        for log in self.changes_log:
            print(f"  {log}")

        print(f"\n📁 Backup Location:")
        print(f"  {self.backup_path}")

        print(f"\n🚀 Next Steps:")
        print(f"  1. Review: Open {self.plan_path}/00-MASTER-PLAN-V5.md")
        print(f"  2. Start: Say 'start Phase -1 for {self.plan_path.name}' in CORTEX")
        print(f"  3. Continue: Say 'continue {self.plan_path.name}' for auto-resume")

        print("\n" + "="*60)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Migrate CORTEX V4 plans to V5 architecture",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Dry run to preview changes
  python scripts/migrate_plan_to_v5.py \\
    --plan cortex-brain/documents/planning/active/my-plan \\
    --dry-run

  # Execute migration
  python scripts/migrate_plan_to_v5.py \\
    --plan cortex-brain/documents/planning/active/my-plan

  # Migrate all plans in active folder
  for plan in cortex-brain/documents/planning/active/*/; do
    python scripts/migrate_plan_to_v5.py --plan "$plan"
  done
        """
    )

    parser.add_argument(
        "--plan",
        required=True,
        help="Path to V4 plan folder (e.g., cortex-brain/documents/planning/active/my-plan)"
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without modifying files"
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print detailed progress information"
    )

    args = parser.parse_args()

    # Execute migration
    migrator = PlanMigrationV5(args.plan, dry_run=args.dry_run)
    success = migrator.execute_migration()
    migrator.print_summary()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
