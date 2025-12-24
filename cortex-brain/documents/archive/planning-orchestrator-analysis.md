# Planning Orchestrator Analysis
**Date:** December 2, 2025  
**Analyst:** GitHub Copilot  
**Purpose:** Sprint 2 Task 4 - Planning Utility Migration Investigation

---

## Size Analysis

- **File Size:** 110KB
- **Line Count:** 2,693 lines
- **Method Count:** 50+ public/private methods
- **Comparison:** ~3.5x larger than all Sprint 1 utilities combined

---

## Structural Breakdown

### Core Dependencies
```python
from src.workflows.document_organizer import DocumentOrganizer
from src.workflows.incremental_plan_generator import IncrementalPlanGenerator
from src.workflows.streaming_plan_writer import CheckpointedPlanWriter
from src.orchestrators.git_checkpoint_orchestrator import GitCheckpointOrchestrator
from src.agents.security.threat_modeler_agent import ThreatModelerAgent
from src.utils.file_structure_optimizer import FileStructureOptimizer
```

**Issue:** Heavy coupling to workflows, agents, and other orchestrators

### Method Categories

#### 1. Schema & Validation (8 methods)
- `_load_schema()` - Load plan schema
- `_get_default_schema()` - Default schema fallback
- `validate_plan()` - Main validation entry
- `_validate_metadata()` - Metadata validation
- `_validate_phases()` - Phases validation
- `_validate_tasks()` - Tasks validation
- `_validate_risks()` - Risks validation
- `_is_valid_iso8601()` - Date validation

#### 2. Plan CRUD Operations (6 methods)
- `create_empty_plan()` - Create new plan
- `save_plan()` - Save plan to YAML
- `load_plan()` - Load plan from YAML
- `generate_markdown()` - Convert to Markdown
- `generate_markdown_view()` - Generate Markdown file
- `migrate_markdown_plan()` - MD to YAML migration

#### 3. Incremental Planning (10 methods)
- `generate_plan_incremental()` - Main incremental generation
- `add_phase_to_plan()` - Add phase incrementally
- `get_last_phase_number()` - Get last phase
- `_get_max_phase_id()` - Get max phase ID
- `track_progress()` - Progress tracking
- `cancel_planning()` - Cancel planning session
- `_handle_checkpoint()` - Checkpoint handling
- `_handle_phase_checkpoint()` - Phase checkpoint
- `_write_incremental_plan()` - Write incremental
- `_get_section_content()` - Get section content

#### 4. Duplicate Detection (4 methods)
- `check_for_duplicate_plans()` - Check duplicates
- `_simple_duplicate_detection()` - Simple detection
- `_extract_simple_title()` - Extract title
- `_extract_simple_keywords()` - Extract keywords
- `_calculate_simple_similarity()` - Calculate similarity
- `generate_duplicate_handling_prompt()` - Prompt generation

#### 5. Plan Lifecycle (3 methods)
- `approve_plan()` - Approve plan
- `complete_plan()` - Complete plan
- `_update_status_in_content()` - Update status
- `_add_completion_timestamp()` - Add timestamp

#### 6. Scope & Estimation (5 methods)
- `infer_scope_from_dor()` - Infer scope from DoR
- `process_clarification_response()` - Process clarifications
- `estimate_feature_scope()` - Estimate scope
- `estimate_timeframe()` - Estimate timeframe
- `_generate_scope_clarification_prompt()` - Generate prompt
- `resume_estimation_with_approved_scope()` - Resume estimation

#### 7. Security Integration (2 methods)
- `analyze_threats()` - Analyze threats via ThreatModelerAgent
- `integrate_threats_into_plan()` - Integrate threats

#### 8. Internal Helpers (8+ methods)
- `_validate_single_phase()` - Single phase validation
- `_validate_dor_for_phase()` - DoR validation
- `_validate_dod_for_phase()` - DoD validation
- `_parse_markdown_plan()` - Parse MD plan
- `_hand_off_to_planner_for_approval()` - Hand-off logic
- `_store_swagger_context()` - Store Swagger context

---

## Code Duplication Analysis

### Problem Areas

1. **Validation Code Duplication**
   - Similar validation patterns repeated across `_validate_metadata`, `_validate_phases`, `_validate_tasks`, `_validate_risks`
   - Each does: check type → check required fields → validate format
   - **Refactoring Opportunity:** Generic validator with field schemas

2. **File I/O Duplication**
   - `save_plan()`, `load_plan()`, `_write_incremental_plan()` all do similar YAML operations
   - Multiple file path construction patterns
   - **Refactoring Opportunity:** Single file manager utility

3. **Status Update Duplication**
   - `approve_plan()` and `complete_plan()` share 80% of logic
   - Both: load file → validate → update status → save file → move file
   - **Refactoring Opportunity:** Generic status updater

4. **Checkpoint Integration**
   - `_handle_checkpoint()` and `_handle_phase_checkpoint()` duplicate git operations
   - Already depends on `GitCheckpointOrchestrator` (we just migrated this!)
   - **Refactoring Opportunity:** Use checkpoint utility directly

---

## Dependency Issues

### Heavy Dependencies (Should Be Removed)
1. ❌ `GitCheckpointOrchestrator` - Use `git_checkpoint_utility` instead
2. ❌ `DocumentOrganizer` - Workflow dependency, should be separate
3. ❌ `IncrementalPlanGenerator` - Workflow dependency, should be separate
4. ❌ `CheckpointedPlanWriter` - Streaming writer, should be separate
5. ❌ `ThreatModelerAgent` - Agent dependency, should be separate call

### Light Dependencies (OK to Keep)
1. ✅ `FileStructureOptimizer` - Utility, lightweight
2. ✅ Standard library (yaml, json, pathlib, datetime)

---

## Core Functionality for Utility

### Must Have (P0)
1. **Create Plan** - Empty plan with metadata
2. **Validate Plan** - Schema validation (DoR/DoD)
3. **Save Plan** - Write to YAML file
4. **Load Plan** - Read from YAML file
5. **Generate Markdown** - Convert plan to readable format

### Should Have (P1)
6. **Approve Plan** - Move to active, update status
7. **Complete Plan** - Move to completed, add timestamp

### Nice to Have (P2)
8. **Check Duplicates** - Basic similarity detection
9. **Vision API Integration** - Extract requirements from screenshots

### Exclude (Move to Workflows)
- ❌ Incremental generation (belongs in workflow)
- ❌ Phase-by-phase building (belongs in workflow)
- ❌ Progress tracking UI (belongs in workflow)
- ❌ Threat modeling integration (belongs in agent call)
- ❌ Scope estimation (belongs in agent call)
- ❌ Swagger context storage (belongs in separate utility)

---

## Proposed Utility Structure

```python
class PlanningUtility:
    """Lightweight planning utility - core operations only."""
    
    # Core CRUD (300 lines)
    def create_plan(feature_name, metadata) -> PlanResult
    def load_plan(plan_path) -> PlanResult
    def save_plan(plan_data, output_path) -> PlanResult
    def validate_plan(plan_data) -> ValidationResult
    
    # Lifecycle (150 lines)
    def approve_plan(plan_filename) -> PlanResult
    def complete_plan(plan_filename) -> PlanResult
    
    # Conversion (100 lines)
    def generate_markdown(plan_data) -> str
    
    # Optional: Vision API (200 lines if implemented)
    def extract_requirements_from_image(image_path) -> RequirementsResult
    
    # Total: ~750 lines (72% reduction from 2,693)
```

---

## Performance Targets

- **Without Vision API:** <5 seconds
- **With Vision API:** <15 seconds
- **Validation only:** <1 second

---

## Migration Strategy

### Phase 1: Extract Core (This Sprint)
- Create lightweight utility with P0 + P1 features
- Remove workflow dependencies
- Use git_checkpoint_utility (already migrated)
- Target: 750-1000 lines

### Phase 2: Workflow Refactoring (Future Sprint)
- Move incremental generation to dedicated workflow
- Move threat modeling to agent call
- Create separate estimation utility

### Phase 3: Cleanup (Future Sprint)
- Delete planning_orchestrator after workflow migration
- Update all references to use new utility

---

## Recommended Approach

**Do NOT migrate 1:1** - This would perpetuate bloat and defeat the purpose.

**Instead:**
1. Extract core 7-8 operations (create, load, save, validate, approve, complete, markdown)
2. Remove all workflow logic (incremental, progress tracking)
3. Remove all agent integration (threats, estimation)
4. Keep validation logic but consolidate duplication
5. Result: ~800 line utility vs 2,693 line orchestrator (70% reduction)

---

## Risk Assessment

**Risk:** Breaking existing workflows that depend on orchestrator  
**Mitigation:** Keep orchestrator as .bak, test workflows separately

**Risk:** Vision API integration complexity  
**Mitigation:** Make Vision API optional, test without it first

**Risk:** Missing essential features  
**Mitigation:** Start with P0 features, add P1 if tests fail

---

## Next Steps

1. Create `planning_utility.py` with 7 core operations
2. Test create/load/save/validate cycle
3. Add approve/complete if time permits
4. Create CLI wrapper for user-friendly interface
5. Measure performance (target <5s)
6. Deprecate orchestrator to .bak

**Estimated Time:** 8-12 minutes (core utility only, no Vision API)
