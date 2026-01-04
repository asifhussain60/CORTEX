# ADO Orchestrator v1 - Architecture Analysis

**Analysis Date:** January 2, 2026  
**Plan:** ado-v2-migration (Phase 0.1)  
**Source Files:**
- `src/orchestrators/ado/ado_orchestrator.py` (2,105 lines)
- `src/orchestrators/ado/ado_conversational_wizard.py` (818 lines)

---

## 📊 Executive Summary

**ADO v1** is a Planning System-compliant orchestrator implementing a 6-phase workflow for Azure DevOps work item generation. It inherits from `BaseOrchestrator` and provides feature parity with Planning System including DoR workflows, approval gates, and visual progress tracking.

**Key Strengths:**
- ✅ Complete 6-phase workflow (DISCOVERY → VALIDATION → GENERATION → APPROVAL → EXECUTION → COMPLETION)
- ✅ Conversational wizard for complex features (Phase 5.1a addition)
- ✅ BaseOrchestrator inheritance with lifecycle management
- ✅ Comprehensive DoR (Definition of Ready) workflow
- ✅ Complexity classification (HIGH/MEDIUM/LOW)
- ✅ Graceful degradation (review orchestrator, duplicate detection)

**Migration Drivers:**
- ❌ Not Master Orchestrator integrated (manual routing)
- ❌ No database state tracking (ephemeral state)
- ❌ Limited template-driven outputs
- ❌ Mixed execution logic (some phases are placeholders)
- ❌ No atomic transactions or rollback capability

---

## 🏗️ Architecture Overview

### Class Hierarchy

```
BaseOrchestrator (base class)
    ↓
ADOOrchestrator (v1 - 2,105 lines)
    ├── ADOPhase (Enum - 6 phases)
    ├── ADOResult (Dataclass - execution result)
    └── Methods:
        ├── execute(**kwargs) → ADOResult (main entry)
        ├── _classify_complexity(feature_name) → str
        ├── _run_review_orchestrator(feature_name) → Dict
        ├── _detect_duplicates(feature_name) → List[Dict]
        ├── _generate_dor_prompts(feature_name) → Dict
        ├── _calculate_dor_completeness(...) → Dict
        └── _transition_phase(from_phase, to_phase, logs)

ADOConversationalWizard (Phase 5.1a - 818 lines)
    ├── WizardStage (Enum - 7 stages)
    ├── WizardResponse (Dataclass - wizard responses)
    ├── WorkItemData (Dataclass - collected data)
    └── Methods:
        ├── start_wizard(feature_name) → WizardResponse
        ├── process_response(session_id, user_input) → WizardResponse
        ├── _validate_stage_input(stage, input) → List[str]
        └── _generate_work_item(data) → Dict
```

### 6-Phase Workflow Breakdown

| Phase | Name | Duration | Current State | Purpose |
|-------|------|----------|---------------|---------|
| 1 | DISCOVERY | 25% | **IMPLEMENTED** | Context gathering, complexity classification, review orchestrator integration, duplicate detection |
| 2 | VALIDATION | 30% | **IMPLEMENTED** | DoR workflow (acceptance criteria, assumptions, constraints), completeness calculation |
| 3 | GENERATION | 15% | **PLACEHOLDER** | Work item hierarchy generation, story point conversion, TDD injection |
| 4 | APPROVAL | 10% | **PLACEHOLDER** | User preview, approval gate, modification loop |
| 5 | EXECUTION | 15% | **PLACEHOLDER** | ADO API calls, batch creation, linking, checkpointing |
| 6 | COMPLETION | 5% | **PLACEHOLDER** | Link generation, progress visualization, success response |

**Implementation Status:**
- **Phase 1-2:** ~500 lines fully implemented
- **Phase 3-6:** Placeholder logging statements only

---

## 🔍 Phase 1: DISCOVERY Implementation

**Location:** Lines 356-391 (ado_orchestrator.py)

### Features

1. **Complexity Classification**
   ```python
   complexity = self._classify_complexity(feature_name)
   # Returns: "HIGH" | "MEDIUM" | "LOW"
   # Based on: keyword matching + length thresholds
   ```

2. **Review Orchestrator Integration**
   - Calls external review orchestrator for context
   - Graceful degradation if unavailable
   - Stores result in `discovery_data["review_context"]`

3. **Duplicate Detection**
   - Searches existing ADO work items
   - Graceful degradation if unavailable
   - Warns user if potential duplicates found

### Data Structure

```python
discovery_data = {
    "complexity": str,              # "HIGH" | "MEDIUM" | "LOW"
    "review_context": Optional[Dict],  # From review orchestrator
    "duplicates": List[Dict]        # Existing work items
}
```

### Complexity Algorithm

**HIGH Complexity Triggers:**
- Keywords: "authentication", "security", "api", "database", "integration", "migration", "payment", "infrastructure"
- Length: >150 characters

**MEDIUM Complexity Triggers:**
- Keywords: "ui", "form", "validation", "report", "dashboard", "notification", "search"
- Length: 50-150 characters

**LOW Complexity:**
- Default for short, simple descriptions

---

## 🔍 Phase 2: VALIDATION Implementation

**Location:** Lines 393-452 (ado_orchestrator.py)

### DoR (Definition of Ready) Workflow

**Purpose:** Ensure feature is ready for development via structured refinement

**Data Collection:**

1. **Acceptance Criteria** (Required)
   - Format: Given/When/Then encouraged
   - Source: `kwargs.get("acceptance_criteria", [])`
   - Validation: Warns if empty

2. **Assumptions** (Optional)
   - Assumptions taken for granted
   - Source: `kwargs.get("assumptions", [])`
   - Validation: Warns if >5 (high uncertainty)

3. **Constraints** (Optional)
   - Limitations/boundaries
   - Source: `kwargs.get("constraints", [])`

### DoR Completeness Calculation

**Algorithm:**
```python
def _calculate_dor_completeness(ac, assumptions, constraints) -> Dict:
    score = 0
    if ac: score += 60  # 60% weight
    if assumptions: score += 20  # 20% weight
    if constraints: score += 20  # 20% weight
    return {
        "is_complete": score >= 60,
        "percentage": score
    }
```

**Threshold:** 60% minimum (requires at least acceptance criteria)

### Data Structure

```python
dor_data = {
    "prompts": Dict[str, str],           # Generated guidance prompts
    "acceptance_criteria": List[str],    # User-provided AC
    "assumptions": List[str],            # User-provided assumptions
    "constraints": List[str],            # User-provided constraints
    "is_complete": bool,                 # >= 60% threshold
    "completeness_percentage": int       # 0-100 score
}
```

---

## 🔍 Phases 3-6: PLACEHOLDER Analysis

**Current Implementation:** Minimal logging statements only

### Phase 3: GENERATION (Expected Implementation)

**Missing Features:**
- Work item hierarchy generation (Epic → Feature → Story → Task)
- Story point conversion from effort estimates
- TDD requirement injection
- Template rendering for work item descriptions

**Estimated Complexity:** HIGH (core business logic)

### Phase 4: APPROVAL (Expected Implementation)

**Missing Features:**
- Formatted work item preview (markdown/table)
- Interactive approval gate (user input)
- Modification loop (refine → regenerate)
- Auto-approve flag handling

**Estimated Complexity:** MEDIUM (user interaction)

### Phase 5: EXECUTION (Expected Implementation)

**Missing Features:**
- ADO API authentication
- Batch work item creation
- Parent-child linking
- Git checkpoint integration
- Error handling and rollback

**Estimated Complexity:** HIGH (external API integration)

### Phase 6: COMPLETION (Expected Implementation)

**Missing Features:**
- ADO URL generation for created items
- Visual progress summary
- Success response formatting
- Metrics collection

**Estimated Complexity:** LOW (reporting)

---

## 🧙 Conversational Wizard Architecture

**File:** `src/orchestrators/ado/ado_conversational_wizard.py` (818 lines)

### 7-Stage Flow

| Stage | Purpose | Can Skip? | Implementation |
|-------|---------|-----------|----------------|
| 1. BASIC_INFO | Feature name, type, priority, effort | No | ✅ Complete |
| 2. ACCEPTANCE_CRITERIA | Vision API or manual AC entry | No | ✅ Complete |
| 3. DEFINITION_OF_READY | Assumptions, constraints | Yes | ✅ Complete |
| 4. DEFINITION_OF_DONE | Completion criteria | Yes | ✅ Complete |
| 5. ESTIMATION | Story points, effort refinement | Yes | ✅ Complete |
| 6. DEPENDENCIES | Related work items | Yes | ✅ Complete |
| 7. REVIEW | Final approval, refinement loop | No | ✅ Complete |

### Session Management

**Storage:** In-memory dictionary (ephemeral)

```python
sessions = {
    session_id: {
        "stage": WizardStage,
        "data": WorkItemData,
        "created_at": datetime,
        "last_updated": datetime
    }
}
```

**Lifecycle:**
1. `start_wizard(feature_name)` → Creates session, returns BASIC_INFO prompt
2. `process_response(session_id, input)` → Validates, progresses to next stage
3. Repeat until COMPLETE stage
4. Returns final `WorkItemData` for ADO creation

### Vision API Integration

**Purpose:** Extract acceptance criteria from screenshots

**Flow:**
1. User attaches screenshot during ACCEPTANCE_CRITERIA stage
2. Wizard detects image attachment
3. Calls Vision API for OCR + analysis
4. Extracts structured AC (Given/When/Then format)
5. Stores in `WorkItemData.vision_context`

---

## 🔧 State Management

### Current Approach (v1)

**Method:** Instance variables + method parameters

```python
class ADOOrchestrator:
    def __init__(self):
        self.current_phase = ADOPhase.DISCOVERY  # Ephemeral
        self.logger = logging.getLogger(__name__)
        
    def execute(self, **kwargs):
        logs = []                    # Local variable (lost after execution)
        warnings = []                # Local variable
        errors = []                  # Local variable
        discovery_data = {}          # Local variable
        dor_data = {}                # Local variable
        # ...
```

**Limitations:**
- ❌ No persistence (state lost between invocations)
- ❌ No transaction support (cannot rollback)
- ❌ No cross-session continuity
- ❌ No progress tracking outside execution

### Target State (v2)

**Method:** PlanningStateDB integration

```python
class ADOOrchestratorV2(BaseOrchestratorV4_1):
    def execute(self, **kwargs):
        plan_id = self.state_db.create_plan(...)
        
        phase_id = self.state_db.start_phase(plan_id, 0, ...)
        # Execute Phase 0
        self.state_db.complete_phase(phase_id)
        
        # Phases persisted in database → resumable, transactional
```

---

## 🛡️ Error Handling & Graceful Degradation

### Current Implementation

**Strategy:** Try-catch with warning messages

**Examples:**

1. **Review Orchestrator Unavailable:**
   ```python
   try:
       review_context = self._run_review_orchestrator(feature_name)
   except Exception as e:
       warnings.append(f"⚠️  Review orchestrator unavailable: {e}")
       discovery_data["review_context"] = None
   ```

2. **Duplicate Detection Failure:**
   ```python
   try:
       duplicates = self._detect_duplicates(feature_name)
   except Exception as e:
       warnings.append(f"⚠️  Duplicate detection unavailable: {e}")
       discovery_data["duplicates"] = []
   ```

**Strengths:**
- ✅ Non-blocking failures
- ✅ User-visible warnings
- ✅ Continues execution

**Weaknesses:**
- ❌ No rollback on critical failures
- ❌ No transaction boundaries
- ❌ Partial failures leave inconsistent state

---

## 📦 Data Structures

### ADOResult (Execution Output)

```python
@dataclass
class ADOResult:
    status: str                     # "success" | "error" | "cancelled"
    success: bool
    phase: ADOPhase                 # Final phase reached
    message: str                    # Human-readable summary
    items_created: int = 0
    items_planned: int = 0
    work_item_links: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    logs: List[str] = field(default_factory=list)
    data: Dict[str, Any] = field(default_factory=dict)
```

### WorkItemData (Wizard Output)

```python
@dataclass
class WorkItemData:
    feature_name: str
    work_item_type: str = "Story"
    priority: str = "Medium"
    effort: str = "M"
    acceptance_criteria: List[str] = field(default_factory=list)
    definition_of_ready: Dict[str, List[str]] = field(default_factory=dict)
    definition_of_done: List[str] = field(default_factory=list)
    story_points: Optional[int] = None
    dependencies: List[str] = field(default_factory=list)
    vision_context: Optional[Dict[str, Any]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
```

---

## 🔗 External Dependencies

### ADO Agent Integration

**File:** `src/cortex_agents/ado_agent.py` (not analyzed yet)

**Expected Responsibilities:**
- ADO API authentication
- Work item creation/updates
- Link management
- Query operations

**Integration Point:** Phase 5 (EXECUTION)

### BaseOrchestrator Integration

**Inherited Features:**
- Configuration loading
- Template management
- Brain tier integration
- Metrics collection
- Lifecycle hooks

**Usage:**
```python
class ADOOrchestrator(BaseOrchestrator):
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(name="ADOOrchestrator", config=config)
```

---

## 📊 Metrics & Logging

### Logging Strategy

**Format:** Structured logging with phase transitions

```python
logs.append(f"📋 Planning for: {feature_name}")
logs.append(f"🎯 Complexity classified as: {complexity}")
logs.append(f"✅ Collected {len(acceptance_criteria)} acceptance criteria")
```

**Emoji Convention:**
- 📋 Informational
- 🎯 Classification/Decision
- ✅ Success
- ⚠️  Warning
- ❌ Error

### Phase Transition Tracking

```python
def _transition_phase(self, from_phase: ADOPhase, to_phase: ADOPhase, logs: List[str]):
    self.current_phase = to_phase
    self.logger.info(f"🎭 Phase transition: {from_phase.value} → {to_phase.value}")
    logs.append(f"🎭 Phase transition: {from_phase.value} → {to_phase.value}")
```

---

## 🎯 Migration Targets (v1 → v2)

### Preserve

1. ✅ **6-Phase Workflow** - Keep structure, improve execution
2. ✅ **DoR Workflow** - Keep logic, add database persistence
3. ✅ **Complexity Classification** - Keep algorithm, move to config
4. ✅ **Graceful Degradation** - Keep pattern, improve error handling
5. ✅ **Conversational Wizard** - Keep as-is, integrate as mode selector

### Transform

1. ❌→✅ **State Management** - Ephemeral → PlanningStateDB
2. ❌→✅ **Execution Logic** - Placeholders → Full implementation
3. ❌→✅ **Configuration** - Hardcoded → YAML manifest
4. ❌→✅ **Templates** - Inline strings → Jinja2 templates
5. ❌→✅ **Routing** - Manual → Master Orchestrator patterns

### Add

1. 🆕 **BaseOrchestrator v4.1 Compliance**
2. 🆕 **Master Orchestrator Integration**
3. 🆕 **Atomic Transactions**
4. 🆕 **Rollback Capability**
5. 🆕 **Dual-Mode Operation** (auto + wizard)

---

## 🚨 Known Limitations & Risks

### High-Priority Issues

1. **No Phase 3-6 Implementation** - Core generation logic missing
2. **Ephemeral State** - Cannot resume interrupted workflows
3. **No Rollback** - Failures leave inconsistent state
4. **Manual Routing** - Not Master Orchestrator integrated

### Medium-Priority Issues

1. **In-Memory Wizard Sessions** - Lost on restart
2. **Limited Error Context** - Generic exception handling
3. **No Validation Framework** - Manual validation scattered

### Low-Priority Issues

1. **Hardcoded Complexity Thresholds** - Should be config-driven
2. **No Metrics Collection** - Only logging
3. **Limited Test Coverage** - Unknown coverage percentage

---

## 📈 Code Quality Metrics

| Metric | Value | Assessment |
|--------|-------|------------|
| **File Size** | 2,105 lines | Large (consider splitting) |
| **Class Size** | ~2,000 lines | Very Large (refactor recommended) |
| **Cyclomatic Complexity** | Unknown | Requires analysis |
| **Test Coverage** | Unknown | Requires baseline |
| **Documentation** | Excellent | Comprehensive docstrings |
| **Type Hints** | Good | Most functions typed |

---

## 🎯 Next Steps for Phase 0

1. ✅ **Complete:** ADO v1 architecture analysis (this document)
2. ⏸️ **TODO:** Conversational wizard design documentation (0.2)
3. ⏸️ **TODO:** Baseline test execution (0.3)
4. ⏸️ **TODO:** Migration strategy document (0.4)

---

**Analysis Completed:** January 2, 2026  
**Reviewed By:** Asif Hussain  
**Status:** ✅ COMPLETE - Ready for Phase 0.2
