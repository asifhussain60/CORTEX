# Tier 2: Long-Term Knowledge (Knowledge Graph) - Feature Inventory

**Purpose:** Document all pattern learning features from KDS for CORTEX migration  
**Source:** KDS v8 Tier 2 implementation  
**Date:** 2025-11-05

---

## Overview

Tier 2 is the **LONG-TERM MEMORY** layer that learns from every interaction. It transforms deleted conversations (Tier 1) and raw events into reusable patterns and insights.

**Core Functionality:**
- Intent pattern recognition and confidence scoring
- File relationship tracking (co-modification rates)
- Workflow template extraction
- Correction history learning
- Validation insight accumulation
- Pattern generalization and decay

**Current Storage:** YAML file (`knowledge-graph.yaml`, ~50-150 KB)  
**CORTEX Target:** SQLite with FTS5 indexing (~30-100 KB, <100ms queries)

---

## Feature Breakdown

### 1. Intent Patterns

**Purpose:** Learn which phrases trigger which intents with confidence scores

**Current Implementation:**

**File:** `kds-brain/knowledge-graph.yaml`

**Schema:**
```yaml
intent_patterns:
  add_feature:
    pattern: "add|create|implement [component_type]"
    description: "User wants to add a new feature/component"
    triggers:
      - "add a button"
      - "create export feature"
      - "implement invoice PDF"
    routes_to: "work-planner"
    action: "create_multi_phase_plan"
    confidence: 0.95
    successful_routes: 47
    failed_routes: 2
    last_used: "2025-11-05"
    
  continue_work:
    pattern: "continue|next|proceed"
    description: "User wants to continue existing work"
    triggers:
      - "continue"
      - "proceed"
      - "next phase"
      - "keep going"
    routes_to: "code-executor"
    action: "resume_session"
    confidence: 0.98
    successful_routes: 89
    failed_routes: 1
    last_used: "2025-11-05"
    
  make_it_purple:
    pattern: "make [pronoun] [color|style]"
    description: "User referencing previous discussion with implicit subject"
    triggers:
      - "make it purple"
      - "change that to blue"
      - "update the color"
    routes_to: "intent-router"
    action: "resolve_reference_then_execute"
    confidence: 0.92
    requires_context: true
    successful_routes: 23
    failed_routes: 3
    last_used: "2025-11-05"
```

**Features:**

1. ✅ **Pattern Recognition**
   - Regex-based pattern matching
   - Wildcard support: `[component_type]`, `[color]`, `[pronoun]`
   - Multi-trigger variations

2. ✅ **Confidence Scoring**
   ```
   confidence = successful_routes / (successful_routes + failed_routes)
   
   Thresholds:
   - ≥ 0.70: Auto-route (high confidence)
   - 0.50-0.69: Suggest with confirmation
   - < 0.50: Pattern decay or delete
   ```

3. ✅ **Success Tracking**
   - Increment on successful routing
   - Decrement confidence on failure
   - Track last usage date

4. ✅ **Context Requirements**
   - Flag patterns needing Tier 1 context
   - Example: "make it purple" needs conversation history

5. ✅ **Automatic Learning**
   - New successful phrases added from events
   - Failed routes lower confidence
   - Unused patterns decay over time

**CORTEX Changes:**
- SQLite table with indexed patterns
- FTS5 for fuzzy phrase matching
- Probabilistic confidence updates (Bayesian)
- Pattern clustering (similar intents grouped)

---

### 2. File Relationships

**Purpose:** Track which files are commonly modified together

**Current Implementation:**

**Schema:**
```yaml
file_relationships:
  HostControlPanel.razor:
    - related_file: HostControlPanelContent.razor
      relationship_type: parent-child
      co_modification_rate: 0.75
      modification_count: 28
      confidence: 0.87
      last_seen: "2025-11-05"
      
    - related_file: noor-canvas.css
      relationship_type: styling
      co_modification_rate: 0.62
      modification_count: 18
      confidence: 0.78
      last_seen: "2025-11-04"
      
    - related_file: UserRegistrationLink.razor
      relationship_type: component-usage
      co_modification_rate: 0.43
      modification_count: 12
      confidence: 0.65
      last_seen: "2025-11-03"
```

**Features:**

1. ✅ **Co-Modification Tracking**
   ```
   co_mod_rate = times_modified_together / max(file1_mods, file2_mods)
   
   Interpretation:
   - > 0.75: Strong relationship (suggest both)
   - 0.50-0.75: Moderate (mention possibility)
   - < 0.50: Weak (don't suggest unless asked)
   ```

2. ✅ **Relationship Types**
   - `parent-child`: Component hierarchy
   - `styling`: CSS for component
   - `component-usage`: Component imports another
   - `test-coverage`: Test file for source
   - `service-controller`: API layers
   - `config-implementation`: Config affects code

3. ✅ **Confidence Calculation**
   ```
   confidence = co_mod_rate × (modification_count / 100)
   
   Max confidence: 1.0
   Higher modification count → Higher confidence
   ```

4. ✅ **Proactive Suggestions**
   - When modifying `HostControlPanel.razor`:
     ```
     ⚠️ File often modified with:
       - HostControlPanelContent.razor (75% co-modification)
       - noor-canvas.css (62% co-modification)
     
     Should I check those files too?
     ```

5. ✅ **Churn Detection**
   ```yaml
   file_hotspots:
     HostControlPanel.razor:
       churn_rate: 0.28  # 28% of all commits touch this file
       total_modifications: 89
       is_hotspot: true
       recommendation: "Extra testing, smaller changes"
   ```

**CORTEX Changes:**
- Graph database structure (nodes = files, edges = relationships)
- Weighted edges (co-modification strength)
- Temporal decay (old relationships fade)
- Multi-hop suggestions (A→B→C chains)

---

### 3. Workflow Patterns

**Purpose:** Learn successful task sequences and reuse them

**Current Implementation:**

**Schema:**
```yaml
workflow_patterns:
  button_addition_test_first:
    pattern: "add_ui_button_with_tdd"
    description: "Add button to component using TDD workflow"
    steps:
      - "Phase 0: Prepare element ID mapping"
      - "Phase 1: RED - Create failing Playwright test"
      - "Phase 2: GREEN - Implement button with ID"
      - "Phase 3: REFACTOR - Validate and commit"
    success_rate: 0.97
    average_duration_minutes: 18
    times_used: 12
    confidence: 0.92
    last_used: "2025-11-05"
    
  export_feature_workflow:
    pattern: "pdf_export_creation"
    description: "Create PDF export feature (service → API → UI)"
    steps:
      - "Phase 1: Service layer with tests"
      - "Phase 2: API controller with tests"
      - "Phase 3: UI component with tests"
      - "Phase 4: Integration validation"
    success_rate: 0.89
    average_duration_days: 5.5
    times_used: 4
    confidence: 0.85
    last_used: "2025-10-28"
    
  wpf_application_tdd:
    pattern: "test_first_for_wpf_ui"
    description: "WPF applications MUST use TDD - build success ≠ runtime success"
    steps:
      - "Phase 0: Create test infrastructure (IconTests, SmokeTests)"
      - "Phase 1: RED - Write failing tests for icons, ViewModels"
      - "Phase 2: GREEN - Implement XAML with validated icons"
      - "Phase 3: REFACTOR - Expand features, keep tests green"
    rationale: "XAML validation happens at runtime, not compile time"
    success_rate: 1.0
    failure_rate_without_tdd: 1.0
    time_saved_minutes: 30
    confidence: 0.95
    last_used: "2025-11-05"
```

**Features:**

1. ✅ **Pattern Extraction**
   - Analyze completed sessions
   - Identify common phase sequences
   - Abstract to reusable templates

2. ✅ **Success Rate Tracking**
   ```
   success_rate = successful_completions / total_attempts
   
   Thresholds:
   - ≥ 0.90: Highly reliable pattern
   - 0.70-0.89: Proven pattern
   - < 0.70: Review and improve
   ```

3. ✅ **Duration Estimation**
   - Track average time per pattern
   - Used for planning estimates
   - Warn if current session exceeds average

4. ✅ **Pattern Reuse**
   - When similar request detected:
     ```
     ✅ Pattern Found: "button_addition_test_first"
     
     This is similar to 12 previous button additions.
     Estimated time: 18 minutes
     Success rate: 97%
     
     Use this workflow? (Y/n)
     ```

5. ✅ **Anti-Pattern Detection**
   ```yaml
   anti_patterns:
     skip_tdd_wpf:
       description: "Skipping TDD for WPF/UI components"
       detection: "WPF component created without test file"
       consequence: "Runtime crashes, silent failures"
       prevention: "Brain Protector challenges (Rule #22)"
       occurrences: 1
       last_seen: "2025-11-05"
   ```

**CORTEX Changes:**
- Workflow graph (DAG of phases)
- Conditional branching (if X then Y else Z)
- Success probability per phase
- Time distribution (not just average)

---

### 4. Correction History

**Purpose:** Learn from mistakes to prevent repetition

**Current Implementation:**

**Schema:**
```yaml
correction_history:
  file_confusion:
    type: "wrong_file_edited"
    description: "Copilot modified wrong file due to similar names"
    common_mistakes:
      - incorrect: "HostControlPanel.razor"
        correct: "HostControlPanelContent.razor"
        frequency: 6
        confidence: 0.94
        
      - incorrect: "UserRegistration.razor"
        correct: "UserRegistrationLink.razor"
        frequency: 3
        confidence: 0.87
    
    total_occurrences: 9
    prevention: "Check filename in conversation context before editing"
    last_seen: "2025-11-04"
    
  hallucinated_method:
    type: "method_doesnt_exist"
    description: "Copilot referenced non-existent method/property"
    common_mistakes:
      - claimed_method: "GetInvoiceById()"
        actual_method: "GetInvoiceByIdAsync()"
        frequency: 4
        
      - claimed_property: "User.FullName"
        actual_property: "User.DisplayName"
        frequency: 2
    
    total_occurrences: 6
    prevention: "Verify method signatures before suggesting code"
    last_seen: "2025-11-03"
    
  path_doubling:
    type: "incorrect_path_construction"
    description: "Hardcoded KDS prefix causes path doubling"
    incorrect_pattern: "$path = \"$WorkspaceRoot\\KDS\\kds-brain\""
    correct_pattern: "if ($WorkspaceRoot -match '\\\\KDS$') { $path = \"$WorkspaceRoot\\kds-brain\" }"
    frequency: 6
    confidence: 0.98
    last_seen: "2025-11-04"
```

**Features:**

1. ✅ **Mistake Cataloging**
   - Track incorrect vs correct patterns
   - Frequency counting (higher = more important to prevent)
   - Confidence scoring

2. ✅ **Proactive Prevention**
   - Before editing file:
     ```
     ⚠️ WARNING: Similar filenames detected
     
     Correction history shows 6 previous mistakes:
       HostControlPanel.razor (WRONG) vs HostControlPanelContent.razor (CORRECT)
     
     Conversation context shows: "HostControlPanelContent.razor"
     
     Verifying correct file before proceeding...
     ```

3. ✅ **Pattern Recognition**
   - File confusion patterns (similar names)
   - Method hallucination patterns (async missing)
   - Path construction errors

4. ✅ **Learning Rate**
   ```
   After 3+ occurrences → High-priority prevention
   After 6+ occurrences → Automatic correction
   After 10+ occurrences → Challenge user if override attempted
   ```

5. ✅ **Error Corrector Integration**
   - `error-corrector.md` agent queries correction history
   - Suggests fixes based on past patterns
   - Reduces debugging time by 68%

**CORTEX Changes:**
- Machine learning classifier (predict mistakes before they happen)
- Similarity scoring (detect variants of known mistakes)
- Automated fix suggestions (high-confidence corrections)

---

### 5. Validation Insights

**Purpose:** Learn common validation failures and prevention strategies

**Current Implementation:**

**Schema:**
```yaml
validation_insights:
  wpf_icon_validation:
    issue: "WPF Material Design icons fail at runtime if invalid"
    symptom: "XamlParseException: 'Lightning is not a valid value for PackIconKind'"
    incorrect_approach: "Assume icon names, test by running app"
    correct_approach: "Validate with Enum.TryParse<PackIconKind> in tests BEFORE XAML"
    test_pattern: "MaterialDesignIconTests.cs with Theory tests"
    frequency: 1
    confidence: 0.95
    impact: critical
    last_seen: "2025-11-05"
    lesson: "WPF UI components REQUIRE test-first - build success ≠ runtime success"
    
  wpf_silent_failures:
    issue: "WPF applications fail silently with no error dialog"
    symptom: "User clicks .exe, nothing happens"
    cause: "XAML parsing errors before UI appears"
    detection: "Use 'dotnet run' (shows errors) vs Start-Process (silent)"
    prevention: "ApplicationStartupTests with InitializeComponent tests"
    frequency: 1
    confidence: 0.92
    impact: high
    last_seen: "2025-11-05"
    
  powershell_regex_escaping:
    issue: "Backtick escaping for quotes in regex fails to parse"
    incorrect_pattern: "[`'\\\"\\\"](.*)[`'\\\"\\\"']"
    correct_pattern: "[\\x27\\x22](.*)[ \\x27\\x22]"
    explanation: "Use hex escape sequences (\\x27=', \\x22=\")"
    frequency: 5
    confidence: 0.95
    impact: high
    last_seen: "2025-11-04"
    
  tdd_violation_wpf:
    issue: "WPF implementation proceeded without TDD"
    impact: "Runtime crash, 30 min debugging, unclear failure mode"
    should_have: "Created icon validation tests FIRST, then XAML"
    lesson: "UI components are HIGH RISK - TDD is MANDATORY"
    time_cost: "30 min debugging vs 5 min writing tests"
    frequency: 1
    confidence: 1.0
    severity: high
    resolution: "Retroactive TDD - created 53-test suite"
    commitment: "Enforce TDD for ALL WPF/UI implementations"
```

**Features:**

1. ✅ **Issue Classification**
   - Symptom (what user sees)
   - Cause (root technical issue)
   - Detection (how to find it)
   - Prevention (how to avoid it)

2. ✅ **Impact Scoring**
   ```
   Impact Levels:
   - critical: System crash, data loss, silent failures
   - high: Broken functionality, long debugging time
   - medium: Sub-optimal code, technical debt
   - low: Minor inefficiency, cosmetic issues
   ```

3. ✅ **Lesson Extraction**
   - Key takeaway from each insight
   - Applied to future similar situations
   - Prevents repeat mistakes

4. ✅ **Time Cost Analysis**
   ```
   Example: TDD Violation WPF
   - Time to write tests first: 5 minutes
   - Time debugging without tests: 30 minutes
   - Savings: 25 minutes (5x ROI)
   
   → TDD is faster, not slower
   ```

5. ✅ **Brain Protector Integration**
   - Brain Protector queries validation insights
   - Challenges risky proposals with evidence
   - Example: "Skipping TDD for WPF costs 30 min (last occurrence)"

**CORTEX Changes:**
- Severity-weighted retrieval (critical issues surfaced first)
- Time-decay (recent insights prioritized)
- Clustering (similar issues grouped)

---

### 6. Feature Components

**Purpose:** Map features to their constituent files

**Current Implementation:**

**Schema:**
```yaml
feature_components:
  invoice_export:
    description: "PDF export for invoices"
    files:
      - InvoiceService.cs
      - InvoiceController.cs
      - InvoiceExportButton.razor
      - invoice-export.css
    tests:
      - InvoiceServiceTests.cs
      - InvoiceControllerTests.cs
      - Tests/UI/invoice-export.spec.ts
    completion_date: "2025-10-28"
    duration_days: 5.5
    success: true
    learnings:
      - "Service-first approach worked well"
      - "Test coverage prevented 3 bugs"
      
  fab_pulse_animation:
    description: "Pulse animation for FAB button"
    files:
      - HostControlPanelContent.razor
      - noor-canvas.css
    tests:
      - Tests/UI/fab-button.spec.ts
    completion_date: "2025-11-05"
    duration_minutes: 84
    success: true
    learnings:
      - "TDD reduced delivery time to 84 seconds"
      - "Element ID pattern worked perfectly"
```

**Features:**

1. ✅ **Component Mapping**
   - All files for a feature
   - All tests for a feature
   - Completion metadata

2. ✅ **Pattern Reuse**
   - "This is similar to invoice_export feature"
   - Suggest reusing file structure
   - Estimate based on similar duration

3. ✅ **Learning Capture**
   - What worked well
   - What to avoid next time
   - Best practices discovered

**CORTEX Changes:**
- Feature taxonomy (categorize by type)
- Similarity scoring (feature A is 85% similar to B)
- Template generation (auto-suggest file structure)

---

### 7. Architectural Patterns

**Purpose:** Learn application architecture conventions

**Current Implementation:**

**Schema:**
```yaml
architectural_patterns:
  service_naming: "I{Name} interface"
  service_di_registration: "Program.cs"
  service_layering: "service-only"
  
  api_routing: "attribute-based"
  api_versioning: "url-path"
  api_auth: "none"
  
  ui_component_structure: "feature-based"
  ui_naming: "PascalCase"
  ui_di_pattern: "none"
  
  test_framework: "Playwright"
  test_selector_strategy: "id"
  test_types:
    - unit
    - integration
    - e2e
```

**Features:**

1. ✅ **Convention Detection**
   - Scan codebase for patterns
   - Learn naming conventions
   - Detect DI patterns

2. ✅ **Consistency Enforcement**
   - New services follow naming pattern
   - New components follow structure
   - New tests use correct selectors

3. ✅ **Architecture Awareness**
   - "This app uses service layer, not repository pattern"
   - "DI registration happens in Program.cs"
   - "Tests use ID selectors, not text"

**CORTEX Changes:**
- Auto-detection (scan on first run)
- Confidence scoring (multiple examples → higher confidence)
- Override warnings (diverging from pattern)

---

### 8. Test Patterns

**Purpose:** Learn testing strategies and element ID mappings

**Current Implementation:**

**Schema:**
```yaml
test_patterns:
  selector_strategy: "id"
  
  element_ids:
    - component: "HostControlPanelSidebar.razor"
      id: "sidebar-start-session-btn"
      purpose: "Start session button"
      confidence: 0.98
      
    - component: "UserRegistrationLink.razor"
      id: "reg-transcript-canvas-btn"
      purpose: "Transcript canvas mode selector"
      confidence: 0.95
      
    - component: "UserRegistrationLink.razor"
      id: "reg-asset-canvas-btn"
      purpose: "Asset canvas mode selector"
      confidence: 0.95
```

**Features:**

1. ✅ **Element ID Registry**
   - All known element IDs
   - Purpose documentation
   - Component mapping

2. ✅ **Test Selector Enforcement**
   - Always use ID selectors (not text)
   - Warn if text selector attempted
   - Suggest ID from registry

3. ✅ **Pattern Detection**
   - ID naming convention: `{scope}-{purpose}-{type}`
   - Example: `sidebar-start-session-btn`

**CORTEX Changes:**
- Full element ID crawler (automatic discovery)
- Selector validation (before test creation)
- ID suggestion (auto-generate from pattern)

---

## Pattern Lifecycle

### 1. Pattern Creation

**Trigger:** New successful workflow detected

**Process:**
```
Event stream:
  task_completed → workflow_completed → all_tests_pass
    ↓
Brain Updater analyzes:
  - Phase sequence
  - Duration per phase
  - Success indicators
    ↓
Extract pattern:
  - Name: "button_addition_test_first"
  - Steps: [Phase 0, Phase 1, Phase 2, Phase 3]
  - Initial confidence: 0.70
    ↓
Store in knowledge-graph.yaml
```

### 2. Pattern Reinforcement

**Trigger:** Pattern used successfully again

**Process:**
```
Pattern matched → Successfully executed
    ↓
Update metrics:
  - times_used: +1
  - successful_routes: +1
  - confidence: recalculate
    ↓
New confidence = successful / (successful + failed)
    ↓
Pattern strengthened (confidence ↑)
```

### 3. Pattern Decay

**Trigger:** Pattern unused for extended period

**Decay Schedule:**
```
Unused for 60 days:
  confidence × 0.90 (reduce by 10%)

Unused for 90 days:
  confidence × 0.75 (reduce by 25%)

Unused for 120 days:
  if confidence < 0.50:
    Mark for deletion
  else:
    confidence × 0.60

Unused for 180 days:
  Delete pattern (no longer relevant)
```

**Exceptions:**
- Tier 0 rules (never decay)
- Explicitly pinned patterns
- Critical architectural patterns

### 4. Pattern Consolidation

**Trigger:** Similar patterns detected

**Process:**
```
Pattern A: "add_button_test_first" (confidence: 0.85, uses: 8)
Pattern B: "create_button_tdd" (confidence: 0.78, uses: 4)

Similarity: 84% (same steps, same intent)
    ↓
Consolidate:
  - Keep higher confidence pattern (A)
  - Merge triggers from both
  - Sum usage counts (8 + 4 = 12)
  - Recalculate confidence
    ↓
Result: Single stronger pattern
```

**Threshold:** 80%+ similarity triggers consolidation

---

## Protection System (Tier 2)

### 1. Data Validation

**Before updating knowledge graph:**

**Checks:**
```powershell
# 1. YAML structure valid
$yaml = ConvertFrom-Yaml -Yaml (Get-Content knowledge-graph.yaml)
if (-not $yaml) { throw "Invalid YAML structure" }

# 2. Required sections present
$required = @('intent_patterns', 'file_relationships', 'workflow_patterns')
foreach ($section in $required) {
  if (-not $yaml.$section) { throw "Missing section: $section" }
}

# 3. Confidence values in valid range
foreach ($pattern in $yaml.intent_patterns.Values) {
  if ($pattern.confidence -lt 0.0 -or $pattern.confidence -gt 1.0) {
    throw "Invalid confidence: $($pattern.confidence)"
  }
}
```

### 2. Backup Before Update

**Script:** `protect-brain-update.ps1`

**Process:**
```powershell
# 1. Create timestamped backup
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backup = "kds-brain/backups/knowledge-graph-$timestamp.yaml"
Copy-Item knowledge-graph.yaml $backup

# 2. Update knowledge graph
# (update process)

# 3. Validate after update
$valid = Test-KnowledgeGraphIntegrity

# 4. Rollback if validation fails
if (-not $valid) {
  Copy-Item $backup knowledge-graph.yaml
  throw "Update failed, rolled back to backup"
}
```

### 3. Anomaly Detection

**Detect suspicious changes:**

```yaml
anomalies_detected:
  confidence_spike:
    pattern: "button_addition"
    old_confidence: 0.85
    new_confidence: 0.99
    change: +0.14 (suspicious!)
    reason: "Unrealistic jump in single update"
    action: "Flag for review"
    
  pattern_deletion:
    pattern: "invoice_export_workflow"
    times_used: 47
    confidence: 0.92
    deletion_reason: "60-day decay"
    action: "PREVENT (still highly used)"
    
  file_relationship_broken:
    file1: "HostControlPanel.razor"
    file2: "HostControlPanelContent.razor"
    old_co_mod: 0.75
    new_co_mod: 0.12
    change: -0.63 (suspicious!)
    reason: "Relationship suddenly weak"
    action: "Verify event data"
```

**Thresholds:**
- Confidence change > ±0.20 → Flag
- Co-modification drop > 0.50 → Flag
- Pattern deletion with uses > 20 → Prevent

---

## Automatic Learning Triggers

### 1. Event Threshold

**Trigger:** 50+ unprocessed events

**Process:**
```
Event count: 53 events
    ↓
Automatic trigger: brain-updater.md
    ↓
Process all 53 events
    ↓
Update knowledge graph
    ↓
Reset event counter
```

### 2. Time Threshold

**Trigger:** 24 hours since last update + 10+ events

**Process:**
```
Last update: 2025-11-04 10:00:00
Current time: 2025-11-05 10:30:00
Elapsed: 24.5 hours

Event count: 15 events (>10)
    ↓
Automatic trigger: brain-updater.md
    ↓
Process events
    ↓
Update timestamp
```

### 3. Session Complete

**Trigger:** All tasks in session finished + DoD validated

**Process:**
```
Session "fab-button":
  All tasks: ✅ Complete
  DoD validated: ✅ Yes
    ↓
Trigger: brain-updater.md
    ↓
Extract workflow pattern from session
    ↓
Update knowledge graph
```

---

## Performance Metrics

| Metric | KDS (YAML) | CORTEX (SQLite) | Improvement |
|--------|------------|-----------------|-------------|
| **Pattern query** | 300-500ms | <100ms | 3-5x faster |
| **Full-text search** | N/A | <150ms | New capability |
| **Pattern matching** | 400-800ms | <80ms | 5-10x faster |
| **Consolidation** | Manual | Automatic | Instant |
| **Storage size** | 50-150 KB | 30-100 KB | 40% smaller |
| **Backup/restore** | 2-5 sec | <1 sec | 2-5x faster |

---

## SQLite Schema (CORTEX Target)

### Tables

**1. intent_patterns**
```sql
CREATE TABLE intent_patterns (
  pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
  pattern_name TEXT UNIQUE NOT NULL,
  pattern_regex TEXT NOT NULL,
  description TEXT,
  routes_to TEXT, -- Agent to route to
  action TEXT,
  confidence REAL DEFAULT 0.70,
  successful_routes INTEGER DEFAULT 0,
  failed_routes INTEGER DEFAULT 0,
  requires_context BOOLEAN DEFAULT 0,
  last_used DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT confidence_range CHECK (confidence >= 0.0 AND confidence <= 1.0)
);

CREATE INDEX idx_intent_patterns_confidence ON intent_patterns(confidence DESC);
CREATE INDEX idx_intent_patterns_last_used ON intent_patterns(last_used DESC);

-- FTS5 for fuzzy pattern matching
CREATE VIRTUAL TABLE intent_patterns_fts USING fts5(
  pattern_id UNINDEXED,
  pattern_name,
  description,
  content=intent_patterns,
  content_rowid=pattern_id
);
```

**2. pattern_triggers**
```sql
CREATE TABLE pattern_triggers (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pattern_id INTEGER NOT NULL,
  trigger_phrase TEXT NOT NULL,
  
  FOREIGN KEY (pattern_id) REFERENCES intent_patterns(pattern_id) ON DELETE CASCADE
);

CREATE INDEX idx_pattern_triggers_pattern ON pattern_triggers(pattern_id);
CREATE INDEX idx_pattern_triggers_phrase ON pattern_triggers(trigger_phrase);
```

**3. file_relationships**
```sql
CREATE TABLE file_relationships (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  file1 TEXT NOT NULL,
  file2 TEXT NOT NULL,
  relationship_type TEXT, -- parent-child, styling, test-coverage, etc.
  co_modification_rate REAL,
  modification_count INTEGER DEFAULT 0,
  confidence REAL DEFAULT 0.50,
  last_seen DATETIME,
  
  CONSTRAINT unique_relationship UNIQUE (file1, file2),
  CONSTRAINT confidence_range CHECK (confidence >= 0.0 AND confidence <= 1.0)
);

CREATE INDEX idx_file_rel_file1 ON file_relationships(file1);
CREATE INDEX idx_file_rel_file2 ON file_relationships(file2);
CREATE INDEX idx_file_rel_confidence ON file_relationships(confidence DESC);
```

**4. workflow_patterns**
```sql
CREATE TABLE workflow_patterns (
  pattern_id INTEGER PRIMARY KEY AUTOINCREMENT,
  pattern_name TEXT UNIQUE NOT NULL,
  description TEXT,
  success_rate REAL,
  average_duration_minutes INTEGER,
  times_used INTEGER DEFAULT 0,
  confidence REAL DEFAULT 0.70,
  last_used DATETIME,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  
  CONSTRAINT confidence_range CHECK (confidence >= 0.0 AND confidence <= 1.0)
);

CREATE INDEX idx_workflow_patterns_confidence ON workflow_patterns(confidence DESC);
CREATE INDEX idx_workflow_patterns_last_used ON workflow_patterns(last_used DESC);
```

**5. workflow_steps**
```sql
CREATE TABLE workflow_steps (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  pattern_id INTEGER NOT NULL,
  step_order INTEGER NOT NULL,
  step_description TEXT NOT NULL,
  
  FOREIGN KEY (pattern_id) REFERENCES workflow_patterns(pattern_id) ON DELETE CASCADE
);

CREATE INDEX idx_workflow_steps_pattern ON workflow_steps(pattern_id, step_order);
```

**6. correction_history**
```sql
CREATE TABLE correction_history (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  correction_type TEXT NOT NULL,
  description TEXT,
  incorrect_value TEXT,
  correct_value TEXT,
  frequency INTEGER DEFAULT 1,
  confidence REAL DEFAULT 0.70,
  prevention_strategy TEXT,
  last_seen DATETIME,
  
  CONSTRAINT confidence_range CHECK (confidence >= 0.0 AND confidence <= 1.0)
);

CREATE INDEX idx_corrections_type ON correction_history(correction_type);
CREATE INDEX idx_corrections_frequency ON correction_history(frequency DESC);
```

**7. validation_insights**
```sql
CREATE TABLE validation_insights (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  insight_name TEXT UNIQUE NOT NULL,
  issue TEXT,
  symptom TEXT,
  cause TEXT,
  detection TEXT,
  prevention TEXT,
  impact TEXT CHECK(impact IN ('critical', 'high', 'medium', 'low')),
  frequency INTEGER DEFAULT 1,
  confidence REAL DEFAULT 0.70,
  time_cost_minutes INTEGER,
  last_seen DATETIME,
  
  CONSTRAINT confidence_range CHECK (confidence >= 0.0 AND confidence <= 1.0)
);

CREATE INDEX idx_insights_impact ON validation_insights(impact, confidence DESC);
CREATE INDEX idx_insights_frequency ON validation_insights(frequency DESC);

-- FTS5 for searching issues/symptoms
CREATE VIRTUAL TABLE validation_insights_fts USING fts5(
  id UNINDEXED,
  insight_name,
  issue,
  symptom,
  cause,
  content=validation_insights,
  content_rowid=id
);
```

**8. feature_components**
```sql
CREATE TABLE feature_components (
  feature_id INTEGER PRIMARY KEY AUTOINCREMENT,
  feature_name TEXT UNIQUE NOT NULL,
  description TEXT,
  completion_date DATETIME,
  duration_minutes INTEGER,
  success BOOLEAN DEFAULT 1
);

CREATE TABLE feature_files (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  feature_id INTEGER NOT NULL,
  file_path TEXT NOT NULL,
  
  FOREIGN KEY (feature_id) REFERENCES feature_components(feature_id) ON DELETE CASCADE
);

CREATE TABLE feature_learnings (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  feature_id INTEGER NOT NULL,
  learning TEXT NOT NULL,
  
  FOREIGN KEY (feature_id) REFERENCES feature_components(feature_id) ON DELETE CASCADE
);
```

---

## Migration Checklist

**Tier 2 complete when:**

### Core Features
- [ ] SQLite schema created and tested
- [ ] Intent pattern recognition with confidence scoring
- [ ] File relationship tracking (co-modification)
- [ ] Workflow pattern extraction
- [ ] Correction history learning
- [ ] Validation insights accumulation
- [ ] Pattern decay system
- [ ] Pattern consolidation (80%+ similarity)

### Data Migration
- [ ] YAML → SQLite conversion script
- [ ] Zero data loss validation
- [ ] Pattern re-extraction from events
- [ ] Confidence recalculation
- [ ] Integrity checks

### Protection System
- [ ] Pre-update validation
- [ ] Automatic backups
- [ ] Anomaly detection
- [ ] Rollback capability

### Testing
- [ ] 67 unit tests (CRUD per table)
- [ ] 12 integration tests (cross-table queries)
- [ ] Pattern matching tests
- [ ] Decay/consolidation tests
- [ ] Performance benchmarks (<100ms)

### Documentation
- [ ] SQLite schema documentation
- [ ] Pattern lifecycle guide
- [ ] Migration guide (YAML → SQLite)
- [ ] Troubleshooting guide

---

## Test Requirements

**Unit Tests (67 total):**

1. **Intent Patterns** (12 tests)
   - Create/read/update/delete pattern
   - Confidence calculation
   - Trigger phrase matching
   - Context requirement detection

2. **File Relationships** (10 tests)
   - Create relationship
   - Calculate co-modification rate
   - Update confidence
   - Relationship type classification

3. **Workflow Patterns** (10 tests)
   - Extract from events
   - Calculate success rate
   - Duration estimation
   - Step ordering

4. **Correction History** (8 tests)
   - Log correction
   - Increment frequency
   - Prevention strategy retrieval
   - Confidence scoring

5. **Validation Insights** (9 tests)
   - Create insight
   - Impact classification
   - Time cost tracking
   - Full-text search

6. **Pattern Lifecycle** (10 tests)
   - Pattern creation
   - Pattern reinforcement
   - Pattern decay (60/90/120 days)
   - Pattern consolidation (80%+ similarity)

7. **Feature Components** (8 tests)
   - Map feature to files
   - Extract learnings
   - Duration tracking
   - Similarity scoring

**Integration Tests (12 total):**

1. **Cross-pattern queries** (4 tests)
   - Find all patterns for file
   - Find all insights for issue type
   - Find similar workflows

2. **Automatic learning** (4 tests)
   - Event → Intent pattern
   - Event → File relationship
   - Event → Workflow extraction
   - Event → Correction logging

3. **Protection system** (4 tests)
   - Backup before update
   - Rollback on failure
   - Anomaly detection
   - Validation after update

---

## Success Criteria

**Tier 2 migration successful when:**

### Functional Parity
- ✅ All KDS pattern learning works in CORTEX
- ✅ Zero data loss during migration
- ✅ Pattern decay automatic and reliable
- ✅ Consolidation reduces duplicates
- ✅ Intent matching ≥ 92% accuracy
- ✅ File relationship suggestions ≥ 75% helpful

### Performance Gains
- ✅ Pattern query <100ms (3-5x faster)
- ✅ Full-text search <150ms
- ✅ Storage 40% smaller
- ✅ Automatic consolidation

### Quality Improvements
- ✅ 95%+ confidence patterns used for auto-routing
- ✅ Protection system prevents data corruption
- ✅ 67 unit + 12 integration tests passing
- ✅ Anomaly detection active

---

**Status:** Feature inventory complete  
**Next:** Tier 3 (Context Intelligence) feature extraction  
**Estimated Implementation Time:** 3-4 days (Phase 2)
