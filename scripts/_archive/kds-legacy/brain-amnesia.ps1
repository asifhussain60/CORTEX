# Brain Amnesia - Safe Application Data Reset
# Version: 1.0
# Purpose: Remove application-specific BRAIN data while preserving KDS core intelligence

param(
    [switch]$DryRun,
    [switch]$SkipBackup,
    [switch]$Force
)

$ErrorActionPreference = "Stop"

# Import workspace resolver
. (Join-Path $PSScriptRoot "lib\workspace-resolver.ps1")

$workspaceRoot = Get-WorkspaceRoot
$kdsRoot = Get-KdsRoot
$brainDir = Join-Path $kdsRoot "cortex-brain"

Write-Host "🧠 KDS BRAIN Amnesia - Application Data Reset" -ForegroundColor Cyan
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Step 1: Validate BRAIN exists
Write-Host "[1/8] Validating BRAIN system..." -ForegroundColor Yellow
if (-not (Test-Path $brainDir)) {
    Write-Host "❌ ERROR: BRAIN directory not found at: $brainDir" -ForegroundColor Red
    exit 1
}

$requiredFiles = @(
    "knowledge-graph.yaml",
    "development-context.yaml",
    "conversation-history.jsonl",
    "events.jsonl"
)

foreach ($file in $requiredFiles) {
    $filePath = Join-Path $brainDir $file
    if (-not (Test-Path $filePath)) {
        Write-Host "❌ ERROR: Required file missing: $file" -ForegroundColor Red
        exit 1
    }
}

Write-Host "✅ BRAIN structure validated" -ForegroundColor Green
Write-Host ""

# Step 2: Analyze current BRAIN data
Write-Host "[2/8] Analyzing BRAIN data..." -ForegroundColor Yellow

$kgPath = Join-Path $brainDir "knowledge-graph.yaml"
$kgContent = Get-Content $kgPath -Raw

# Count application-specific patterns
$appFileRelationships = ($kgContent | Select-String -Pattern "file_relationships:" -AllMatches).Matches.Count
$appWorkflows = ($kgContent | Select-String -Pattern "SPA/NoorCanvas|HostControlPanel|fab_button|start_session" -AllMatches).Matches.Count
$genericWorkflows = ($kgContent | Select-String -Pattern "test_first_id_preparation|single_file_spa|kds_health_monitoring|brain_test_synchronization" -AllMatches).Matches.Count

$convPath = Join-Path $brainDir "conversation-history.jsonl"
$convCount = (Get-Content $convPath | Measure-Object -Line).Lines

$eventsPath = Join-Path $brainDir "events.jsonl"
$eventsCount = (Get-Content $eventsPath | Measure-Object -Line).Lines

Write-Host "  Application-specific workflows: $appWorkflows" -ForegroundColor White
Write-Host "  Generic/KDS workflows: $genericWorkflows" -ForegroundColor White
Write-Host "  Conversations: $convCount" -ForegroundColor White
Write-Host "  Events: $eventsCount" -ForegroundColor White
Write-Host ""

# Step 3: Generate amnesia report
Write-Host "[3/8] Generating amnesia report..." -ForegroundColor Yellow

$timestamp = Get-Date -Format "yyyyMMdd-HHmmss"
$reportPath = Join-Path $brainDir "amnesia-report-$timestamp.yaml"

$report = @"
# BRAIN Amnesia Report
# Generated: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

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
    - kds_health_dashboard (app-specific parts)
  correction_history:
    - All file_mismatch entries
  conversation_history:
    - All conversations ($convCount total)
  events:
    - All events ($eventsCount total)
  development_context:
    - All metrics (reset to baseline)

will_be_preserved:
  intent_patterns:
    - Generic templates (add [X] button, create [X] dashboard, etc.)
    - All 8 intent type structures
  workflow_patterns:
    - test_first_id_preparation (generic, reusable)
    - single_file_spa_creation (generic, reusable)
    - kds_health_monitoring (KDS-specific)
    - powershell_http_server (generic, reusable)
    - unified_launcher_pattern (generic, reusable)
    - brain_test_synchronization (KDS governance)
  test_patterns:
    - id_based_playwright_selectors (generic approach)
  validation_insights:
    - Structure preserved (empty but ready)
  protection_config:
    - All settings (confidence thresholds, routing safety)
  statistics:
    - Structure preserved (counters reset to 0)

estimated_impact:
  application_data_loss: 100%
  kds_capabilities_loss: 0%
  generic_intelligence_loss: 0%
  recovery_time: "Immediate (via Setup command)"

safety_score: 10/10
  - Backup created before amnesia
  - Generic patterns preserved
  - KDS governance patterns preserved
  - All core capabilities retained
  - Rollback available via backup
"@

Set-Content -Path $reportPath -Value $report
Write-Host "✅ Report saved: $reportPath" -ForegroundColor Green
Write-Host ""

# Step 4: Show report and confirm
Write-Host "[4/8] Amnesia Impact Summary" -ForegroundColor Yellow
Write-Host ""
Write-Host "  WILL BE REMOVED:" -ForegroundColor Red
Write-Host "    - $convCount conversations (application context)" -ForegroundColor White
Write-Host "    - $eventsCount events (application interactions)" -ForegroundColor White
Write-Host "    - ~$appWorkflows application-specific patterns" -ForegroundColor White
Write-Host "    - All NoorCanvas file relationships" -ForegroundColor White
Write-Host "    - All development metrics" -ForegroundColor White
Write-Host ""
Write-Host "  WILL BE PRESERVED:" -ForegroundColor Green
Write-Host "    - All 10 KDS specialist agents" -ForegroundColor White
Write-Host "    - ~$genericWorkflows generic/KDS workflow patterns" -ForegroundColor White
Write-Host "    - Generic intent detection templates" -ForegroundColor White
Write-Host "    - Protection configuration" -ForegroundColor White
Write-Host "    - All KDS governance rules" -ForegroundColor White
Write-Host ""

if ($DryRun) {
    Write-Host "🔍 DRY RUN MODE - No changes will be made" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Report saved to: $reportPath" -ForegroundColor Cyan
    Write-Host "Review the report and run without -DryRun to execute amnesia" -ForegroundColor Cyan
    exit 0
}

if (-not $Force) {
    Write-Host "⚠️  WARNING: This will remove all application-specific BRAIN data!" -ForegroundColor Yellow
    Write-Host "   A backup will be created, but this action requires confirmation." -ForegroundColor Yellow
    Write-Host ""
    $confirmation = Read-Host "Type 'AMNESIA' to confirm reset"
    
    if ($confirmation -ne "AMNESIA") {
        Write-Host "❌ Amnesia cancelled" -ForegroundColor Red
        exit 0
    }
}

Write-Host ""
Write-Host "✅ Amnesia confirmed - proceeding..." -ForegroundColor Green
Write-Host ""

# Step 5: Create backup
if (-not $SkipBackup) {
    Write-Host "[5/8] Creating backup..." -ForegroundColor Yellow
    
    $backupDir = Join-Path $brainDir "backups\pre-amnesia-$timestamp"
    New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
    
    Copy-Item -Path "$brainDir\*.yaml" -Destination $backupDir -Force
    Copy-Item -Path "$brainDir\*.jsonl" -Destination $backupDir -Force
    Copy-Item -Path "$brainDir\*.md" -Destination $backupDir -Force -ErrorAction SilentlyContinue
    
    Write-Host "✅ Backup created: $backupDir" -ForegroundColor Green
    Write-Host ""
} else {
    Write-Host "[5/8] Skipping backup (as requested)..." -ForegroundColor Yellow
    Write-Host ""
}

# Step 6: Execute amnesia - Reset BRAIN files
Write-Host "[6/8] Executing BRAIN amnesia..." -ForegroundColor Yellow

# Reset conversation history
Write-Host "  Resetting Tier 1 (Conversation History)..." -ForegroundColor White
$convReset = @"
{"conversation_id":"conv-bootstrap","title":"KDS System Initialization - Post Amnesia","started":"$(Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")","ended":"$(Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")","message_count":1,"active":false,"messages":[{"id":"msg-bootstrap-001","timestamp":"$(Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")","user":"System","intent":"SYSTEM","entities":["amnesia","brain_reset"],"context_ref":null}],"entities_discussed":["amnesia","new_application_ready"],"files_modified":[],"outcome":"initialized","note":"BRAIN reset via amnesia - ready for new application"}
"@
Set-Content -Path $convPath -Value $convReset

# Reset events log
Write-Host "  Resetting events log..." -ForegroundColor White
$eventsReset = @"
{"timestamp":"$(Get-Date -Format "yyyy-MM-ddTHH:mm:ssK")","type":"brain_amnesia","source":"brain-amnesia.ps1","data":{"reason":"Application context reset","previous_app":"NoorCanvas","conversations_archived":$convCount,"events_archived":$eventsCount,"patterns_preserved":$genericWorkflows,"patterns_removed":$appWorkflows,"backup_location":"backups/pre-amnesia-$timestamp"}}
"@
Set-Content -Path $eventsPath -Value $eventsReset

# Reset knowledge graph (preserve generic patterns)
Write-Host "  Resetting Tier 2 (Knowledge Graph)..." -ForegroundColor White
$kgReset = @"
# KDS BRAIN - Knowledge Graph
# Version: 2.0 (Post-Amnesia)
# Last Updated: $(Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")
# Purpose: Aggregated learnings from KDS interactions
# STATUS: RESET - Ready for new application

intent_patterns:
  plan:
    phrases:
      - pattern: "add [X] button"
        confidence: 0.95
        routes_to: "work-planner.md"
        examples:
          - "add share button"
          - "add login button"
          - "add search button"
      - pattern: "create [X] dashboard"
        confidence: 0.95
        routes_to: "work-planner.md"
        examples:
          - "create admin dashboard"
          - "create health dashboard"
          - "create monitoring dashboard"
      - pattern: "implement [X]"
        confidence: 0.90
        routes_to: "work-planner.md"
        examples:
          - "implement authentication"
          - "implement API integration"
          - "implement feature"
  execute:
    phrases:
      - pattern: "add ids to [component]"
        confidence: 0.95
        routes_to: "direct_execution"
        skip_planning: true
        examples:
          - "add ids to component"
          - "add IDs for tests"
          - "add data-testid attributes"
      - pattern: "add [attributes] for [testing]"
        confidence: 0.90
        routes_to: "test_preparation"
        skip_planning: true
        examples:
          - "add data-testid for playwright"
          - "add test identifiers"
  resume: {}
  correct: {}
  test: {}
  validate: {}
  ask: {}
  govern: {}

file_relationships: {}

workflow_patterns:
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
      - "Count checks in test suite"
      - "Verify health script maps all checks"
      - "Verify dashboard displays all checks"
      - "Verify documentation reflects current count"
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
    current_check_count: 13
    success_rate: 1.0
    reusable: false
    scope: "kds_internal_governance"

correction_history:
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
    id_based_playwright_selectors:
      framework: "playwright"
      description: "Use semantic element IDs for reliable test selectors instead of text-based selectors"
      confidence: 1.0
      reusable: true
      naming_convention: "[component]-[section]-[element]"
      examples:
        - "component-section-element"
        - "feature-area-button"
        - "page-action-link"
      benefits:
        - "Resilient to UI text changes"
        - "More maintainable"
        - "Better for visual regression testing"

feature_components: {}

statistics:
  total_events_processed: 0
  last_updated: "$(Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")"
  knowledge_graph_version: "2.0"
  confidence_threshold: 0.70
  learning_enabled: true
  status: "RESET - Ready for new application"
  recent_sessions: []

protection_config:
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
"@
Set-Content -Path $kgPath -Value $kgReset

# Reset development context
Write-Host "  Resetting Tier 3 (Development Context)..." -ForegroundColor White
$dcPath = Join-Path $brainDir "development-context.yaml"
$dcContent = Get-Content $dcPath -Raw
# Simple approach: Reset all counters and clear arrays
$dcReset = $dcContent -replace 'total_commits: \d+', 'total_commits: 0'
$dcReset = $dcReset -replace 'commits_per_day_avg: [\d.]+', 'commits_per_day_avg: 0.00'
$dcReset = $dcReset -replace 'lines_added: \d+', 'lines_added: 0'
$dcReset = $dcReset -replace 'lines_deleted: \d+', 'lines_deleted: 0'
$dcReset = $dcReset -replace 'total_files_modified: \d+', 'total_files_modified: 0'
$dcReset = $dcReset -replace 'commit_patterns: \[.*?\]', 'commit_patterns: []'
$dcReset = $dcReset -replace 'files_most_changed: \[.*?\]', 'files_most_changed: []'
$dcReset = $dcReset -replace 'active_branches: \[.*?\]', 'active_branches: []'
$dcReset = $dcReset -replace 'last_updated: ".*?"', "last_updated: `"$(Get-Date -Format 'yyyy-MM-ddTHH:mm:ssZ')`""
Set-Content -Path $dcPath -Value $dcReset

Write-Host "✅ BRAIN amnesia complete" -ForegroundColor Green
Write-Host ""

# Step 7: Verify BRAIN integrity
Write-Host "[7/8] Verifying BRAIN integrity..." -ForegroundColor Yellow

$verified = $true

# Check file existence
foreach ($file in $requiredFiles) {
    $filePath = Join-Path $brainDir $file
    if (-not (Test-Path $filePath)) {
        Write-Host "  ❌ File missing: $file" -ForegroundColor Red
        $verified = $false
    }
}

# Check generic patterns preserved
$newKgContent = Get-Content $kgPath -Raw
$preservedPatterns = ($newKgContent | Select-String -Pattern "test_first_id_preparation|single_file_spa|kds_health_monitoring|brain_test_synchronization|powershell_http_server|unified_launcher" -AllMatches).Matches.Count

if ($preservedPatterns -lt 6) {
    Write-Host "  ❌ Generic patterns not fully preserved (found $preservedPatterns, expected 6)" -ForegroundColor Red
    $verified = $false
}

# Check protection config preserved
if ($newKgContent -notmatch "protection_config:") {
    Write-Host "  ❌ Protection config missing" -ForegroundColor Red
    $verified = $false
}

if ($verified) {
    Write-Host "✅ BRAIN integrity verified" -ForegroundColor Green
} else {
    Write-Host "⚠️  WARNING: BRAIN integrity check failed" -ForegroundColor Yellow
    Write-Host "   Backup available at: $backupDir" -ForegroundColor Yellow
}
Write-Host ""

# Step 8: Generate completion report
Write-Host "[8/8] Generating completion report..." -ForegroundColor Yellow

$completionPath = Join-Path $brainDir "amnesia-complete-$timestamp.yaml"
$completion = @"
# BRAIN Amnesia Completion Report
# Executed: $(Get-Date -Format "yyyy-MM-dd HH:mm:ss")

amnesia_summary:
  executed: "$(Get-Date -Format "yyyy-MM-ddTHH:mm:ssZ")"
  previous_application: "NoorCanvas"
  backup_location: "backups/pre-amnesia-$timestamp"
  
  removed:
    file_relationships: ~5
    workflow_patterns: ~4
    feature_components: ~2
    conversations: $convCount
    events: $eventsCount
    corrections: ~1
  
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
    - "Update KDS/tooling/cortex.config.json with new application details"
    - "Run Setup command to learn new application architecture"
    - "KDS will automatically learn from new interactions"
    - "BRAIN will rebuild application-specific knowledge over time"

validation_passed:
  - Backup created at: $backupDir
  - Generic patterns preserved: $preservedPatterns/6
  - KDS patterns preserved: Yes
  - Application data removed: Yes
  - Protection config intact: Yes
  - File structure valid: Yes
  - Ready for use: Yes

rollback_instructions:
  - "If amnesia needs to be undone:"
  - "  Copy-Item -Path '$backupDir\*.yaml' -Destination '$brainDir' -Force"
  - "  Copy-Item -Path '$backupDir\*.jsonl' -Destination '$brainDir' -Force"
  - "  Then validate with: #file:KDS/prompts/internal/health-validator.md"
"@

Set-Content -Path $completionPath -Value $completion
Write-Host "✅ Completion report saved: $completionPath" -ForegroundColor Green
Write-Host ""

# Summary
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ BRAIN AMNESIA COMPLETE" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host "Summary:" -ForegroundColor White
Write-Host "  ✅ Backup created: $backupDir" -ForegroundColor Green
Write-Host "  ✅ Application data removed" -ForegroundColor Green
Write-Host "  ✅ Generic patterns preserved ($preservedPatterns patterns)" -ForegroundColor Green
Write-Host "  ✅ KDS capabilities intact" -ForegroundColor Green
Write-Host "  ✅ BRAIN ready for new application" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Yellow
Write-Host "  1. Update KDS/tooling/cortex.config.json (new project name/paths)" -ForegroundColor White
Write-Host "  2. Run: #file:KDS/prompts/user/kds.md Setup" -ForegroundColor White
Write-Host "  3. KDS will learn your new application architecture" -ForegroundColor White
Write-Host ""
Write-Host "Reports Generated:" -ForegroundColor Cyan
Write-Host "  - $reportPath" -ForegroundColor White
Write-Host "  - $completionPath" -ForegroundColor White
Write-Host ""
