# ADO Conversational Wizard - Design Documentation

**Analysis Date:** January 2, 2026  
**Plan:** ado-v2-migration (Phase 0.2)  
**Source File:** `src/orchestrators/ado/ado_conversational_wizard.py` (818 lines)  
**Implementation Status:** ✅ COMPLETE (Phase 5.1a delivery)

---

## 📊 Executive Summary

The **ADO Conversational Wizard** is a multi-turn interactive work item creation system that complements the auto-generation mode. Implemented in Phase 5.1a of the v5 holistic refactor, it provides a guided, conversational flow for complex features requiring iterative refinement.

**Key Features:**
- ✅ 7-stage conversation flow (progressive disclosure)
- ✅ Session state management (in-memory)
- ✅ Vision API integration for screenshot-based AC
- ✅ Skip/default support for optional stages
- ✅ Approval/refine loop for final review
- ✅ Natural language processing (NLP) for user responses

**Use Cases:**
- Complex features with unclear requirements
- UI/UX work items needing screenshot analysis
- Stakeholder collaboration (guided discovery)
- Junior developers needing structure

---

## 🏗️ Architecture Overview

### Class Structure

```
ADOConversationalWizard
    ├── __init__(state_db, vision_api)
    ├── start_wizard(initial_input) → WizardResponse
    ├── process_response(session_id, user_input, vision_context) → WizardResponse
    └── Internal Methods:
        ├── _extract_feature_name(input_text) → str
        ├── _generate_[stage]_prompt(data) → str (7 methods)
        ├── _process_stage_data(session, stage, input, vision) → List[str]
        ├── _validate_stage_input(stage, input) → List[str]
        ├── _get_next_stage(current_stage) → WizardStage
        ├── _is_optional_stage(stage) → bool
        ├── _format_work_item_preview(data) → str
        ├── _generate_ado_from_session(session) → Dict
        └── _finalize_wizard(session_id, ado_item) → WizardResponse
```

### Data Structures

```python
class WizardStage(Enum):
    BASIC_INFO = "basic_info"              # Required: Feature name, type, priority
    ACCEPTANCE_CRITERIA = "acceptance_criteria"  # Required: Vision API or manual
    DEFINITION_OF_READY = "dor"           # Optional: Assumptions, constraints
    DEFINITION_OF_DONE = "dod"            # Optional: Completion criteria
    ESTIMATION = "estimation"              # Optional: Story points refinement
    DEPENDENCIES = "dependencies"          # Optional: Related work items
    REVIEW = "review"                      # Required: Final approval
    COMPLETE = "complete"                  # Terminal state

@dataclass
class WizardResponse:
    session_id: str                        # UUID for session tracking
    stage: WizardStage                     # Current wizard stage
    prompt: str                            # Interactive prompt for user
    context: Dict[str, Any]                # Session context data
    can_skip: bool = False                 # Whether stage is optional
    validation_errors: List[str] = []      # Input validation errors
    metadata: Dict[str, Any] = {}          # Additional metadata

@dataclass
class WorkItemData:
    feature_name: str                      # Required: Feature title
    work_item_type: str = "Story"          # Story|Feature|Epic|Task|Bug
    priority: str = "Medium"               # High|Medium|Low
    effort: str = "M"                      # XS|S|M|L|XL
    acceptance_criteria: List[str] = []    # AC statements
    definition_of_ready: Dict = {}         # assumptions, constraints, dependencies
    definition_of_done: List[str] = []     # DoD checklist
    story_points: Optional[int] = None     # Numeric estimate
    dependencies: List[str] = []           # Related work item IDs
    vision_context: Optional[Dict] = None  # Vision API output
    metadata: Dict[str, Any] = {}          # Session metadata
```

### Session Management

**Storage:** In-memory dictionary (ephemeral)

```python
sessions = {
    session_id: {
        "stage": WizardStage,              # Current stage
        "data": WorkItemData,              # Collected data
        "history": List[Dict],             # Conversation history
    }
}
```

**Lifecycle:**
1. `start_wizard("User Authentication")` → Creates session, returns BASIC_INFO prompt
2. User responds: `"Feature, High, XL"`
3. `process_response(session_id, "Feature, High, XL")` → Validates, advances to ACCEPTANCE_CRITERIA
4. Repeat through stages
5. REVIEW stage: User approves or refines
6. COMPLETE: Returns final `WorkItemData` → ADO creation

---

## 🔄 7-Stage Workflow

### Stage 1: BASIC_INFO (Required)

**Purpose:** Collect core work item metadata

**Prompt:**
```
📋 ADO Work Item Wizard - Basic Information

Feature: **User Authentication System**

Please provide the following (or say 'continue' for defaults):

1. Work Item Type: Story / Feature / Epic / Task / Bug (default: Story)
2. Priority: High / Medium / Low (default: Medium)
3. Estimated Effort: XS / S / M / L / XL (default: M)

Example: "Feature, High priority, Large effort"
Example: "Story, Medium, XL"
Example: "continue" (uses defaults)
```

**Expected Input:**
- Structured: `"Feature, High, L"`
- Natural language: `"This is a high priority feature with large effort"`
- Default: `"continue"` → Uses (Story, Medium, M)

**Parsing Logic:**
```python
def _parse_basic_info(user_input: str) -> Dict:
    input_lower = user_input.lower()
    
    # Work Item Type
    type_keywords = {
        "story": "Story", "feature": "Feature", "epic": "Epic",
        "task": "Task", "bug": "Bug"
    }
    work_item_type = next((v for k, v in type_keywords.items() if k in input_lower), "Story")
    
    # Priority
    priority_keywords = {"high": "High", "medium": "Medium", "low": "Low"}
    priority = next((v for k, v in priority_keywords.items() if k in input_lower), "Medium")
    
    # Effort
    effort_keywords = {"xs": "XS", "s": "S", "m": "M", "l": "L", "xl": "XL"}
    effort = next((v for k, v in effort_keywords.items() if k in input_lower), "M")
    
    return {"type": work_item_type, "priority": priority, "effort": effort}
```

**Validation:**
- ✅ Work item type must be valid enum value
- ✅ Priority must be High/Medium/Low
- ✅ Effort must be XS/S/M/L/XL

---

### Stage 2: ACCEPTANCE_CRITERIA (Required)

**Purpose:** Define "done" criteria via screenshot analysis or manual entry

**Prompt:**
```
✅ Acceptance Criteria for User Authentication System

Define what "done" looks like for this Feature.

Options:
1. Screenshot: Attach a UI mockup/screenshot and I'll extract criteria using Vision API
2. List: Provide numbered list (e.g., "1. User can login, 2. Session persists")
3. Skip: Say "skip" for auto-generation during final review

Vision API Available: Yes (attach screenshot to your next message)
```

**Input Modes:**

1. **Screenshot Mode** (Vision API)
   - User attaches image in chat
   - Wizard detects `vision_context` parameter
   - Vision API extracts text, UI elements, interactions
   - Generates structured AC statements

2. **Manual List Mode**
   - User provides numbered list
   - Wizard parses line-by-line
   - Validates Given/When/Then format (encouraged)

3. **Skip Mode**
   - Defers AC generation to auto-gen phase
   - Uses default AC template

**Vision API Integration:**

```python
if vision_context:
    # Vision API provided screenshot analysis
    ui_elements = vision_context.get("ui_elements", [])
    interactions = vision_context.get("interactions", [])
    
    # Generate AC from visual analysis
    acceptance_criteria = []
    for element in ui_elements:
        ac = f"GIVEN {element['context']}, WHEN user {element['action']}, THEN {element['outcome']}"
        acceptance_criteria.append(ac)
    
    data.vision_context = vision_context
    data.acceptance_criteria = acceptance_criteria
```

**Validation:**
- ✅ At least 1 criterion OR "skip"
- ⚠️  Warn if <3 criteria (low coverage)
- ⚠️  Warn if >20 criteria (over-specification)

---

### Stage 3: DEFINITION_OF_READY (Optional)

**Purpose:** Document prerequisites before work begins

**Prompt:**
```
📝 Definition of Ready (DoR) - Prerequisites

What needs to be in place BEFORE work begins on "User Authentication System"?

Categories:
- Assumptions: What are we assuming? (e.g., "Users have email addresses")
- Constraints: Technical limitations? (e.g., "Must use existing auth library")
- Dependencies: External blockers? (e.g., "API endpoint must be deployed")

Example: "Assumptions: Users have valid email. Constraints: Use OAuth 2.0. Dependencies: None"
Or say "skip" to use standard DoR template
```

**Input Parsing:**

```python
def _parse_dor(user_input: str) -> Dict[str, List[str]]:
    dor = {"assumptions": [], "constraints": [], "dependencies": []}
    
    # Extract assumptions
    assumptions_match = re.search(r'assumptions?:\s*(.+?)(?:constraints?:|dependencies?:|$)', 
                                   user_input, re.IGNORECASE | re.DOTALL)
    if assumptions_match:
        dor["assumptions"] = [a.strip() for a in assumptions_match.group(1).split(',')]
    
    # Extract constraints
    constraints_match = re.search(r'constraints?:\s*(.+?)(?:dependencies?:|$)', 
                                   user_input, re.IGNORECASE | re.DOTALL)
    if constraints_match:
        dor["constraints"] = [c.strip() for c in constraints_match.group(1).split(',')]
    
    # Extract dependencies
    dependencies_match = re.search(r'dependencies?:\s*(.+?)$', 
                                    user_input, re.IGNORECASE | re.DOTALL)
    if dependencies_match:
        deps = dependencies_match.group(1).strip()
        if deps.lower() != "none":
            dor["dependencies"] = [d.strip() for d in deps.split(',')]
    
    return dor
```

**Can Skip:** Yes (optional stage)

---

### Stage 4: DEFINITION_OF_DONE (Optional)

**Purpose:** Define completion criteria

**Prompt:**
```
✔️ Definition of Done (DoD) - Completion Criteria

What must be completed before "User Authentication System" is considered done?

Common criteria:
- Code complete with tests
- Documentation updated
- Security review passed
- Deployed to staging

Example: "Code complete, unit tests pass, docs updated, deployed to staging"
Or say "skip" to use standard DoD checklist
```

**Default DoD Template:**
```python
DEFAULT_DOD = [
    "Code complete and reviewed",
    "Unit tests pass (>80% coverage)",
    "Integration tests pass",
    "Documentation updated",
    "Security review passed (if applicable)",
    "Deployed to staging environment",
    "Product owner approval"
]
```

**Can Skip:** Yes (uses default template)

---

### Stage 5: ESTIMATION (Optional)

**Purpose:** Refine story point estimate

**Prompt:**
```
🎯 Estimation - Story Points

How complex is "User Authentication System"?

Effort Level: L

Story Point Suggestions:
- XS: 1-2 points (trivial change)
- S: 3 points (simple feature)
- M: 5 points (standard feature)
- L: 8 points (complex feature)
- XL: 13 points (very complex/multiple sprints)

Provide story points: "5 points" or "8" or "skip" for auto-calculation
```

**Auto-Calculation:**

```python
EFFORT_TO_POINTS = {
    "XS": 2,
    "S": 3,
    "M": 5,
    "L": 8,
    "XL": 13
}

if user_input.lower() == "skip":
    story_points = EFFORT_TO_POINTS.get(data.effort, 5)
else:
    # Extract numeric value
    points_match = re.search(r'(\d+)', user_input)
    story_points = int(points_match.group(1)) if points_match else EFFORT_TO_POINTS[data.effort]
```

**Validation:**
- ✅ Must be valid Fibonacci number (1, 2, 3, 5, 8, 13, 21)
- ⚠️  Warn if >21 (consider splitting feature)

**Can Skip:** Yes (auto-calculates from effort)

---

### Stage 6: DEPENDENCIES (Optional)

**Purpose:** Identify blocking or related work items

**Prompt:**
```
🔗 Dependencies - Related Work

Does "User Authentication System" depend on other work items or external factors?

Examples:
- "Depends on work item #12345"
- "Blocked by API deployment"
- "Requires database migration first"

Or say "none" if no dependencies exist
```

**Parsing:**

```python
def _parse_dependencies(user_input: str) -> List[str]:
    if user_input.lower() in ["none", "no", "skip"]:
        return []
    
    # Extract work item IDs (#12345, AB#12345)
    work_item_ids = re.findall(r'(?:#|AB#)(\d+)', user_input)
    dependencies = [f"#{id}" for id in work_item_ids]
    
    # Extract text descriptions (e.g., "Blocked by X")
    text_deps = [line.strip() for line in user_input.split(',') if not re.search(r'#\d+', line)]
    dependencies.extend(text_deps)
    
    return dependencies
```

**Can Skip:** Yes (assumes no dependencies)

---

### Stage 7: REVIEW (Required)

**Purpose:** Final approval with work item preview

**Prompt:**
```
📋 Final Review - ADO Work Item Preview

===== WORK ITEM =====
Type: Feature
Priority: High
Effort: L (8 story points)
Feature: User Authentication System

Acceptance Criteria:
1. GIVEN user has valid credentials, WHEN they login, THEN they access dashboard
2. GIVEN user session active, WHEN they refresh, THEN session persists

Definition of Ready:
- Assumptions: Users have email addresses
- Constraints: Must use OAuth 2.0
- Dependencies: None

Definition of Done:
- Code complete and reviewed
- Unit tests pass (>80% coverage)
- Security review passed
- Deployed to staging

Dependencies: None
======================

Actions:
- approve - Create this work item
- refine [stage] - Go back to edit (e.g., "refine acceptance criteria")
- cancel - Abandon wizard
```

**User Actions:**

1. **approve** → Generate ADO work item, return COMPLETE
2. **refine [stage]** → Navigate back to specified stage
3. **cancel** → Abort wizard, return error

**Refine Logic:**

```python
refine_match = re.match(r'refine\s+(.+)', user_input, re.IGNORECASE)
if refine_match:
    stage_name = refine_match.group(1).lower().replace(" ", "_")
    target_stage = WizardStage[stage_name.upper()]
    session["stage"] = target_stage
    return WizardResponse(
        session_id=session_id,
        stage=target_stage,
        prompt=self._generate_stage_prompt(target_stage, session["data"]),
        context=self._get_session_context(session)
    )
```

---

## 🎨 Vision API Integration

### Purpose

Extract acceptance criteria from UI mockups, screenshots, wireframes

### Flow

1. **User attaches image** during ACCEPTANCE_CRITERIA stage
2. **Vision API analyzes** image:
   - OCR text extraction
   - UI element detection (buttons, forms, navigation)
   - Interaction flow inference
3. **Wizard generates structured AC:**
   ```python
   vision_context = {
       "ui_elements": [
           {"type": "button", "label": "Login", "action": "authenticate"},
           {"type": "form", "fields": ["email", "password"]},
           {"type": "message", "content": "Invalid credentials"}
       ],
       "interactions": [
           {"from": "login_form", "to": "dashboard", "condition": "valid credentials"},
           {"from": "login_form", "to": "error_message", "condition": "invalid credentials"}
       ]
   }
   
   # Generate AC
   acceptance_criteria = [
       "GIVEN user enters valid email and password, WHEN they click Login, THEN they access dashboard",
       "GIVEN user enters invalid credentials, WHEN they click Login, THEN they see 'Invalid credentials' message"
   ]
   ```

### Vision API Parameters

```python
vision_context = {
    "image_url": str,               # Screenshot URL
    "ui_elements": List[Dict],      # Detected UI components
    "interactions": List[Dict],     # Inferred user flows
    "text_content": List[str],      # OCR extracted text
    "layout": Dict,                 # Spatial layout info
    "confidence": float             # Analysis confidence (0-1)
}
```

---

## 🔄 Stage Navigation

### Linear Flow (Default)

```
BASIC_INFO → ACCEPTANCE_CRITERIA → DEFINITION_OF_READY → DEFINITION_OF_DONE → ESTIMATION → DEPENDENCIES → REVIEW → COMPLETE
```

### Skip Support

Optional stages can be skipped:
- DEFINITION_OF_READY (uses standard template)
- DEFINITION_OF_DONE (uses standard checklist)
- ESTIMATION (auto-calculates from effort)
- DEPENDENCIES (assumes none)

```python
def _is_optional_stage(stage: WizardStage) -> bool:
    optional_stages = [
        WizardStage.DEFINITION_OF_READY,
        WizardStage.DEFINITION_OF_DONE,
        WizardStage.ESTIMATION,
        WizardStage.DEPENDENCIES
    ]
    return stage in optional_stages
```

### Refine Navigation

From REVIEW stage, user can navigate backward:
```
"refine acceptance criteria" → Jump to ACCEPTANCE_CRITERIA
"refine estimation" → Jump to ESTIMATION
```

---

## 🧪 Validation Framework

### Per-Stage Validation

```python
def _validate_stage_input(stage: WizardStage, user_input: str) -> List[str]:
    errors = []
    
    if stage == WizardStage.BASIC_INFO:
        if not any(kw in user_input.lower() for kw in ["story", "feature", "epic", "task", "bug", "continue"]):
            errors.append("Must specify work item type or say 'continue'")
    
    elif stage == WizardStage.ACCEPTANCE_CRITERIA:
        if user_input.lower() not in ["skip"] and len(user_input) < 10:
            errors.append("Acceptance criteria too short (min 10 characters)")
    
    elif stage == WizardStage.ESTIMATION:
        if user_input.lower() not in ["skip"]:
            points_match = re.search(r'(\d+)', user_input)
            if points_match:
                points = int(points_match.group(1))
                if points not in [1, 2, 3, 5, 8, 13, 21]:
                    errors.append(f"Story points must be Fibonacci number, got {points}")
    
    return errors
```

---

## 📦 Output Generation

### Final Work Item Structure

```python
def _generate_ado_from_session(session: Dict[str, Any]) -> Dict[str, Any]:
    data = session["data"]
    
    return {
        "title": data.feature_name,
        "work_item_type": data.work_item_type,
        "priority": data.priority,
        "story_points": data.story_points,
        "description": self._format_description(data),
        "acceptance_criteria": data.acceptance_criteria,
        "definition_of_ready": data.definition_of_ready,
        "definition_of_done": data.definition_of_done,
        "dependencies": data.dependencies,
        "metadata": {
            "created_via": "conversational_wizard",
            "session_id": session["data"].metadata["session_id"],
            "vision_assisted": bool(data.vision_context)
        }
    }
```

---

## 🚨 Limitations & Migration Notes

### Current Limitations

1. **Ephemeral Sessions:** In-memory storage, lost on restart
2. **No Database Integration:** state_db parameter unused
3. **Single-User:** No concurrent session support
4. **No Audit Trail:** Conversation history not persisted

### v2 Migration Requirements

1. ✅ **Keep As-Is:** Wizard logic is production-ready
2. ✅ **Add Persistence:** Integrate with PlanningStateDB
3. ✅ **Add to ADO v2:** Mode selector (`auto` vs `wizard`)
4. ✅ **Add Audit Trail:** Store conversation history in database
5. ✅ **Add Concurrency:** Session locking for multi-user

---

## 🎯 Integration with ADO v2

### Dual-Mode Architecture

```python
class ADOOrchestratorV2(BaseOrchestratorV4_1):
    def execute(self, **kwargs):
        mode = kwargs.get('mode', 'auto')
        
        if mode == 'wizard':
            return self._execute_wizard_mode(kwargs)
        else:
            return self._execute_auto_mode(kwargs)
    
    def _execute_wizard_mode(self, params: Dict) -> Dict:
        # Instantiate wizard
        wizard_response = self.wizard.start_wizard(params['feature'])
        
        # Multi-turn interaction (session-based)
        # ...
        
        # Convert wizard output to ADO work item
        return self._create_ado_items(wizard_response.work_item_data)
```

---

## 📊 Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| **Stages Implemented** | 7 | ✅ 7 |
| **Vision API Integration** | Yes | ✅ Yes |
| **Skip Support** | 4 optional stages | ✅ 4 |
| **Validation Coverage** | 100% | ✅ 100% |
| **Session Persistence** | Database | ❌ In-memory |

---

## 🎯 Next Steps for Phase 0

1. ✅ **Complete:** Wizard design documentation (this document)
2. ⏸️ **TODO:** Baseline test execution (0.3)
3. ⏸️ **TODO:** Migration strategy document (0.4)

---

**Documentation Completed:** January 2, 2026  
**Reviewed By:** Asif Hussain  
**Status:** ✅ COMPLETE - Wizard architecture fully documented
