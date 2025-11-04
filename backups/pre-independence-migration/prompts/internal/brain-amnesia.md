# Brain Amnesia - Application Data Reset

**Version:** 1.0  
**Purpose:** Remove application-specific learned data while preserving KDS core intelligence  
**Status:** 🧠 SAFE RESET - Only affects application context, not KDS capabilities  

---

## What This Does

**REMOVES (Application-Specific):**
- ✅ File relationships (e.g., SPA/NoorCanvas/... paths)
- ✅ Application-specific workflow patterns (e.g., "start_session_flow")
- ✅ Application-specific feature components (e.g., "fab_button")
- ✅ Conversation history (application discussions)
- ✅ Events log (application interactions)
- ✅ Development context metrics (git stats, velocity)
- ✅ Correction history with application file paths

**PRESERVES (KDS Core Intelligence):**
- ✅ Generic intent patterns (e.g., "add [X] button" → plan)
- ✅ Generic workflow patterns (e.g., "test_first_id_preparation")
- ✅ Generic test patterns (e.g., "id_based_playwright_selectors")
- ✅ KDS-specific patterns (e.g., "brain_test_synchronization", "kds_health_monitoring")
- ✅ Protection configuration (confidence thresholds, routing safety)
- ✅ Validation insights structure
- ✅ All KDS prompts and agents

---

## Safety Mechanisms

### Pattern Classification

**Generic Pattern Indicators:**
- Contains `[X]` or `[Y]` placeholders (generic template)
- No specific file paths in examples
- Workflow applies to any project type
- Pattern name includes: "generic", "reusable", "pattern", "approach"
- Scope is "kds_internal_governance" or undefined (not application)

**Application-Specific Indicators:**
- Contains hardcoded file paths (e.g., "SPA/NoorCanvas/...")
- References specific features (e.g., "fab_button", "host_control_panel")
- Workflow tied to specific architecture (e.g., "Blazor + SignalR")
- Pattern name includes application name or feature name
- Scope is NOT "kds_internal_governance"

### Pre-Reset Validation

Before amnesia:
1. ✅ Create backup of current BRAIN state (`kds-brain/backups/pre-amnesia-{timestamp}.zip`)
2. ✅ Generate amnesia report (what will be removed vs preserved)
3. ✅ Require user confirmation (show report first)
4. ✅ Validate BRAIN files writeable
5. ✅ Ensure no active sessions (warn if exists)

### Post-Reset Validation

After amnesia:
1. ✅ Verify BRAIN structure intact (all files exist)
2. ✅ Verify generic patterns preserved (count check)
3. ✅ Verify KDS patterns preserved (health monitoring, etc.)
4. ✅ Verify protection config intact
5. ✅ Run BRAIN integrity tests
6. ✅ Generate amnesia completion report

---

## Implementation

### Step 1: Pre-Reset Backup

**Create Backup:**
```powershell
$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$backupDir = "KDS/kds-brain/backups/pre-amnesia-$timestamp"
New-Item -ItemType Directory -Force -Path $backupDir
Copy-Item -Path "KDS/kds-brain/*.yaml" -Destination $backupDir
Copy-Item -Path "KDS/kds-brain/*.jsonl" -Destination $backupDir
```

**Generate Amnesia Report:**
```yaml
# KDS/kds-brain/amnesia-report-{timestamp}.yaml

will_be_removed:
  file_relationships:
    - host_control_panel
    - start_session_flow
    - playwright_test_preparation
    - kds_dashboard (contains NoorCanvas paths)
  workflow_patterns:
    - service_layer_ui_injection
    - blazor_component_api_flow
    - two_phase_button_injection
  feature_components:
    - fab_button
    - kds_health_dashboard (if contains app-specific paths)
  correction_history:
    - file_mismatch entries with NoorCanvas paths
  conversation_history:
    - All conversations (application context)
  events:
    - All events (application interactions)
  development_context:
    - All metrics (reset to baseline)

will_be_preserved:
  intent_patterns:
    - plan.phrases (generic templates)
    - execute.phrases (generic templates)
    - All other intent types (structure)
  workflow_patterns:
    - test_first_id_preparation (generic, reusable)
    - single_file_spa_creation (generic, reusable)
    - kds_health_monitoring (KDS-specific)
    - powershell_http_server (generic, reusable)
    - unified_launcher_pattern (generic, reusable)
    - brain_test_synchronization (KDS governance)
  test_patterns:
    - id_based_playwright_selectors (generic)
    - dashboard_refresh_automation (if made generic)
  validation_insights:
    - Structure (empty but ready)
  protection_config:
    - All settings (confidence thresholds, routing safety)
  statistics:
    - Structure (reset counters to 0)

confidence_scores:
  generic_patterns_preserved: 100%
  application_data_removed: 100%
  kds_capabilities_retained: 100%
```

### Step 2: Execute Amnesia

**Reset Tier 1: Conversation History**
```yaml
# conversation-history.jsonl → Reset to bootstrap only
{"conversation_id":"conv-bootstrap","title":"KDS System Initialization","started":"{timestamp}","ended":"{timestamp}","message_count":1,"active":false,"messages":[{"id":"msg-bootstrap-001","timestamp":"{timestamp}","user":"Bootstrap","intent":"SYSTEM","entities":["conversation tracking"],"context_ref":null}],"entities_discussed":["conversation tracking"],"files_modified":[],"outcome":"initialized","note":"BRAIN reset - ready for new application"}
```

**Reset Tier 2: Knowledge Graph**
```yaml
# knowledge-graph.yaml → Preserve generic, remove application-specific

intent_patterns:
  plan:
    phrases:
      - pattern: "add [X] button"
        confidence: 0.95
        routes_to: "work-planner.md"
        examples:
          - "add share button"
          - "add login button"
      - pattern: "create [X] dashboard"
        confidence: 0.95
        routes_to: "work-planner.md"
        examples:
          - "create admin dashboard"
          - "create health dashboard"
      - pattern: "implement [X]"
        confidence: 0.90
        routes_to: "work-planner.md"
        examples:
          - "implement authentication"
          - "implement API integration"
  execute:
    phrases:
      - pattern: "add ids to [component]"
        confidence: 0.95
        routes_to: "direct_execution"
        skip_planning: true
        examples:
          - "add ids to component"
          - "add IDs for tests"
      - pattern: "add [attributes] for [testing]"
        confidence: 0.90
        routes_to: "test_preparation"
        skip_planning: true
        examples:
          - "add data-testid attributes"
  resume: {}
  correct: {}
  test: {}
  validate: {}
  ask: {}
  govern: {}

file_relationships: {}
  # Completely empty - will be learned from new application

workflow_patterns:
  # PRESERVE: Generic, reusable patterns
  test_first_id_preparation:
    description: "Add semantic IDs to components before writing Playwright tests"
    steps:
      - "Analyze component structure"
      - "Add semantic IDs following [component]-[section]-[element] convention"
      - "Document IDs in comprehensive reference"
      - "Provide test examples"
      - "Include Percy visual regression examples"
      - "Mark IDs with [PLAYWRIGHT-IDS] comments"
    success_rate: 1.0
    confidence: 1.0
    reusable: true
  
  single_file_spa_creation:
    description: "Create portable HTML dashboard with inline CSS/JS and zero dependencies"
    steps:
      - "Design UI structure with tabs and cards"
      - "Inline all CSS (no external stylesheets)"
      - "Inline all JavaScript (no external scripts)"
      - "Add PowerShell launcher script"
      - "Create VS Code task integration"
      - "Write comprehensive documentation"
    file_pattern:
      main_file: "KDS/*.html"
      documentation: "KDS/dashboard/*.md"
      launcher: "KDS/scripts/open-*.ps1"
      tasks: ".vscode/tasks.json"
    success_rate: 1.0
    confidence: 0.95
    reusable: true
    benefits:
      - "100% portable (single file)"
      - "Zero external dependencies"
      - "Works offline"
      - "Fast load time"
      - "Easy to share/deploy"
  
  kds_health_monitoring:
    description: "PowerShell-based health checks with browser dashboard and API server"
    architecture: "Client-Server (browser SPA + local API)"
    components:
      dashboard: "Single-file HTML with auto-detection (Live/Demo modes)"
      api_server: "PowerShell HTTP listener on localhost:8765"
      health_checks: "PowerShell script with categorized validations"
      launcher: "All-in-one script (server + client)"
    steps:
      - "Start PowerShell HTTP server (background job)"
      - "Open dashboard in browser"
      - "Dashboard detects API availability"
      - "Execute health checks on demand"
      - "Display results with status circles"
      - "Generate recommendations from failures"
    technologies:
      - "PowerShell (server + health checks)"
      - "HTML5/CSS3/JavaScript (dashboard)"
      - "HTTP REST API (communication)"
      - "VS Code tasks (easy launch)"
    success_rate: 1.0
    confidence: 0.95
    reusable: true
  
  powershell_http_server:
    description: "Simple PowerShell HTTP server for local API endpoints"
    pattern_type: "Local development server"
    implementation:
      - "Create HttpListener on localhost:port"
      - "Set up CORS headers for browser access"
      - "Handle GET/POST requests"
      - "Return JSON responses"
      - "Run as background job"
    use_cases:
      - "Dashboard API integration"
      - "Local testing without IIS/Kestrel"
      - "Lightweight health check endpoints"
    success_rate: 1.0
    confidence: 0.90
    reusable: true
  
  unified_launcher_pattern:
    description: "Single command to start server + open client application"
    pattern_type: "Developer experience"
    steps:
      - "Start background API server (job)"
      - "Wait for server readiness"
      - "Open client application"
      - "Verify connectivity"
      - "Optional: keep server running or auto-cleanup"
    parameters:
      - "-KeepServerRunning (optional)"
      - "-Port (default 8765)"
    success_rate: 1.0
    confidence: 0.95
    reusable: true
    benefits:
      - "Single command UX"
      - "Automatic cleanup"
      - "User-friendly"
      - "Reduces setup friction"
  
  brain_test_synchronization:
    description: "CRITICAL: BRAIN integrity test changes require synchronous updates to health checks and dashboard"
    rule_id: "BRAIN-SYNC-001"
    enforcement: "MANDATORY (change-governor blocks violations)"
    trigger_files:
      - "KDS/tests/test-brain-integrity.ps1"
      - "KDS/tests/test-brain-corruption-scenarios.ps1"
    required_dependencies:
      - path: "KDS/scripts/run-health-checks.ps1"
        section: "Test-BRAINSystem()"
        requirement: "Must map ALL integrity checks from test suite"
      - path: "KDS/kds-dashboard.html"
        section: "renderBRAINMetricsFromAPI()"
        requirement: "Must display ALL integrity checks in BRAIN System tab"
      - path: "KDS/tests/BRAIN-INTEGRITY-TEST.md"
        section: "What Gets Validated"
        requirement: "Must document ALL checks with current count"
    validation_logic:
      - "Detect if test-brain-integrity.ps1 modified"
      - "Verify all 3 dependencies also modified in same commit"
      - "Count checks in test suite (currently 13)"
      - "Verify health script maps all 13 checks"
      - "Verify dashboard displays all 13 checks"
      - "Verify documentation reflects count of 13"
      - "REJECT commit if any dependency missing or count mismatch"
    rationale:
      - "Dashboard must show ALL current BRAIN checks, not subset"
      - "Automated health checks must include every integrity validation"
      - "System components must agree on what 'healthy BRAIN' means"
      - "Users must see accurate, complete BRAIN status"
      - "Silent failures are prevented by enforced synchronization"
    confidence: 1.00
    source: "governance/rules/brain-test-synchronization.md"
    enforced_by: "change-governor.md"
    created: "2025-11-03"
    current_check_count: 13
    success_rate: 1.0
    reusable: false
    scope: "kds_internal_governance"

correction_history:
  # Reset - will learn from new application's corrections
  file_mismatch:
    total_occurrences: 0
    common_mistakes: []
  approach_mismatch:
    total_occurrences: 0
    common_mistakes: []
  scope_mismatch:
    total_occurrences: 0
    common_mistakes: []

validation_insights:
  common_failures: []
  test_patterns:
    # PRESERVE: Generic test pattern intelligence
    id_based_playwright_selectors:
      framework: "playwright"
      description: "Use semantic element IDs for reliable test selectors instead of text-based selectors"
      confidence: 1.0
      reusable: true
      naming_convention: "[component]-[section]-[element]"
      examples:
        - "component-section-element"
        - "feature-area-button"
      benefits:
        - "Resilient to UI text changes"
        - "More maintainable"
        - "Better for visual regression testing"

feature_components: {}
  # Reset - will learn from new application's features

statistics:
  total_events_processed: 0
  last_updated: "{timestamp}"
  knowledge_graph_version: "2.0"
  confidence_threshold: 0.70
  learning_enabled: true
  status: "RESET - Ready for new application"
  recent_sessions: []

protection_config:
  # PRESERVE: All protection settings
  enabled: true
  version: "1.0"
  description: "Phase 1 Protection - Confidence checks and learning quality thresholds"
  
  learning_quality:
    min_confidence_threshold: 0.70
    min_occurrences_for_pattern: 3
    max_single_event_confidence: 0.50
    anomaly_confidence_threshold: 0.95
    description: "Prevents learning from insufficient data and detects anomalies"
  
  routing_safety:
    enabled: true
    fallback_on_low_confidence: true
    ask_user_threshold: 0.70
    auto_route_threshold: 0.85
    description: "Asks user for clarification when confidence is low"
  
  correction_memory:
    enabled: true
    alert_on_repeated_mistake: 3
    prevent_action_threshold: 5
    track_correction_patterns: true
    description: "Prevents repeating the same mistakes"
  
  validation:
    validate_confidence_scores: true
    validate_file_references: true
    detect_stale_relationships: true
    max_relationship_age_days: 90
    description: "Ensures data integrity and removes stale information"
```

**Reset Tier 3: Development Context**
```yaml
# development-context.yaml → Reset to baseline template
# (Copy structure from current file, but zero all counters and clear application data)
```

**Reset Events Log**
```jsonl
# events.jsonl → Single bootstrap event
{"timestamp":"{timestamp}","type":"brain_reset","source":"brain-amnesia.md","data":{"reason":"Application context reset","previous_app":"NoorCanvas","new_app":"pending_setup","events_archived":68,"conversations_archived":5,"patterns_preserved":8,"patterns_removed":15}}
```

### Step 3: Verify Reset

**BRAIN Integrity Checks:**
1. ✅ File structure intact (all .yaml/.jsonl files exist)
2. ✅ Generic intent patterns present (count >= 5)
3. ✅ KDS workflow patterns present (brain_test_synchronization, kds_health_monitoring)
4. ✅ Protection config unchanged
5. ✅ No application-specific file paths remain
6. ✅ Statistics structure intact (counters at 0)
7. ✅ Backup created successfully

### Step 4: Generate Completion Report

```yaml
# KDS/kds-brain/amnesia-complete-{timestamp}.yaml

amnesia_summary:
  executed: "{timestamp}"
  previous_application: "NoorCanvas"
  backup_location: "KDS/kds-brain/backups/pre-amnesia-{timestamp}"
  
  removed:
    file_relationships: 5
    workflow_patterns: 4
    feature_components: 2
    conversations: 5
    events: 68
    corrections: 1
  
  preserved:
    intent_patterns: 2  # plan, execute with generic templates
    workflow_patterns: 6  # Generic + KDS governance patterns
    test_patterns: 1  # id_based_playwright_selectors
    protection_config: 1
  
  brain_health:
    structure_intact: true
    generic_intelligence_preserved: true
    application_data_removed: true
    ready_for_new_app: true
  
  next_steps:
    - "Update kds.config.json with new application details"
    - "Run Setup command to learn new application architecture"
    - "KDS will automatically learn from new interactions"
    - "BRAIN will rebuild application-specific knowledge over time"

validation_passed:
  - ✅ Backup created
  - ✅ Generic patterns preserved
  - ✅ KDS patterns preserved
  - ✅ Application data removed
  - ✅ Protection config intact
  - ✅ File structure valid
  - ✅ Ready for use
```

---

## Usage

**Invoke Amnesia:**
```markdown
#file:KDS/prompts/user/kds.md

Reset BRAIN for new application (amnesia)
```

**Expected Flow:**
1. Router detects "amnesia" or "reset brain" → Routes to brain-amnesia.md
2. Generate amnesia report (what will be removed/preserved)
3. Show report to user, require confirmation
4. Create backup of current BRAIN state
5. Execute amnesia (reset Tier 1, Tier 2, Tier 3)
6. Verify BRAIN integrity
7. Generate completion report
8. User updates kds.config.json
9. User runs Setup to learn new application

---

## Safety Guarantees

### What CANNOT Be Lost

**KDS Core Capabilities:**
- ✅ Intent routing (8 intent types)
- ✅ 10 specialist agents
- ✅ Abstraction layer (session-loader, test-runner, file-accessor, brain-query)
- ✅ Governance rules (17 rules)
- ✅ Protection system (confidence thresholds, anomaly detection)
- ✅ Health dashboard
- ✅ Metrics reporter
- ✅ All KDS prompts

**Generic Intelligence:**
- ✅ "Add [X] button" → plan (generic template)
- ✅ "Test-first ID preparation" workflow
- ✅ "Single-file SPA creation" pattern
- ✅ "ID-based Playwright selectors" approach
- ✅ KDS health monitoring patterns
- ✅ Brain synchronization governance

### What WILL Be Lost (As Intended)

**Application-Specific Data:**
- ✅ NoorCanvas file paths
- ✅ Blazor/SignalR workflow patterns (application-specific)
- ✅ Feature components (fab_button, etc.)
- ✅ Conversation history (application discussions)
- ✅ Git metrics from old repository
- ✅ Correction history (old file paths)

---

## Rollback Procedure

**If amnesia needs to be undone:**
```powershell
# Restore from backup
$backupDir = "KDS/kds-brain/backups/pre-amnesia-{timestamp}"
Copy-Item -Path "$backupDir/*.yaml" -Destination "KDS/kds-brain/" -Force
Copy-Item -Path "$backupDir/*.jsonl" -Destination "KDS/kds-brain/" -Force
```

**Verification:**
```markdown
#file:KDS/prompts/internal/health-validator.md
Validate BRAIN system
```

---

## Testing Amnesia

**Test Scenario:**
1. Backup current BRAIN
2. Run amnesia (dry-run mode first)
3. Verify generic patterns preserved
4. Verify application data removed
5. Restore from backup
6. Verify restoration successful

**Success Criteria:**
- ✅ No KDS capabilities lost
- ✅ Generic patterns intact
- ✅ Application data removed
- ✅ BRAIN ready for new application
- ✅ Backup/restore works

---

**Version:** 1.0  
**Status:** Ready for implementation  
**Safety Level:** MAXIMUM (preserves all KDS intelligence)
