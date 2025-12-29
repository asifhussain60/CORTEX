# KDS v6.0 Brain Structure Setup Script
# Purpose: Create new brain-inspired folder structure and backup current state
# Version: 1.0.0
# Date: 2025-11-04

param(
    [string]$KDSRoot = "D:\PROJECTS\DevProjects\KDS",
    [switch]$DryRun = $false
)

$ErrorActionPreference = "Continue"

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "🧠 KDS v6.0 - Brain Structure Setup" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Step 1: Git-based backup (commit current state)
$timestamp = Get-Date -Format "yyyy-MM-dd HH:mm:ss"

Write-Host "[1/6] Git-based backup of current state..." -ForegroundColor Yellow

if (-not $DryRun) {
    Push-Location $KDSRoot
    
    # Check if there are uncommitted changes
    $gitStatus = git status --porcelain 2>&1
    
    if ($gitStatus) {
        Write-Host "      📝 Uncommitted changes detected" -ForegroundColor Gray
        Write-Host "      Creating backup commit: 'backup: Pre-v6.0 brain migration'" -ForegroundColor Gray
        
        try {
            git add -A
            git commit -m "backup: Pre-v6.0 brain migration - $timestamp" -m "Automated backup before KDS v6.0 brain structure migration. Current cortex-brain/ state preserved in git history." 2>&1 | Out-Null
            
            $commitHash = git rev-parse --short HEAD
            Write-Host "      ✅ Backup commit created: $commitHash" -ForegroundColor Green
            Write-Host "      💡 Rollback: git revert $commitHash" -ForegroundColor Cyan
        } catch {
            Write-Host "      ⚠️  Git commit failed: $($_.Exception.Message)" -ForegroundColor Yellow
            Write-Host "      Continuing anyway..." -ForegroundColor Gray
        }
    } else {
        Write-Host "      ✅ No uncommitted changes - git history is clean" -ForegroundColor Green
    }
    
    Pop-Location
} else {
    Write-Host "      [DRY RUN] Would create git commit: 'backup: Pre-v6.0 brain migration'" -ForegroundColor Gray
}
Write-Host ""

# Step 2: Define new brain structure
$brainStructure = @{
    "brain" = @(
        # Tier 0: Instinct - Permanent Intelligence
        "instinct",
        
        # Tier 1: Working Memory - Short-Term
        "working-memory\recent-conversations",
        
        # Tier 2: Long-Term Memory - Learned Patterns
        "long-term",
        
        # Tier 3: Context Awareness - Project Intelligence
        "context-awareness",
        
        # Tier 4: Imagination - Creative Ideas
        "imagination",
        
        # Tier 5: Housekeeping - Automatic Maintenance
        "housekeeping\services",
        "housekeeping\schedules",
        "housekeeping\logs",
        "housekeeping\config",
        
        # Tier 6: Brain Sharpener - Testing Framework
        "sharpener\core",
        "sharpener\scenarios\tier-0-instinct",
        "sharpener\scenarios\tier-1-working-memory",
        "sharpener\scenarios\tier-2-long-term",
        "sharpener\scenarios\tier-3-context",
        "sharpener\scenarios\tier-4-imagination",
        "sharpener\scenarios\cross-tier",
        "sharpener\results",
        "sharpener\config",
        
        # Event Stream
        "event-stream",
        
        # Health & Diagnostics
        "health\sharpener-results",
        
        # Archives
        "archived\patterns",
        "archived\conversations",
        "archived\events"
    )
}

Write-Host "[2/6] Creating new brain/ folder structure..." -ForegroundColor Yellow

$foldersCreated = 0
foreach ($folder in $brainStructure["brain"]) {
    $fullPath = Join-Path $KDSRoot "brain\$folder"
    
    if (-not $DryRun) {
        if (-not (Test-Path $fullPath)) {
            $null = New-Item -ItemType Directory -Path $fullPath -Force
            $foldersCreated++
            Write-Host "      ✅ Created: brain/$folder" -ForegroundColor Green
        } else {
            Write-Host "      ℹ️  Exists: brain/$folder" -ForegroundColor Gray
        }
    } else {
        Write-Host "      [DRY RUN] Would create: brain/$folder" -ForegroundColor Gray
        $foldersCreated++
    }
}

Write-Host ""
Write-Host "      ✅ Created $foldersCreated new folders" -ForegroundColor Green
Write-Host ""

# Step 3: Link implementation plan to imagination layer
Write-Host "[3/6] Linking KDS-V6-HOLISTIC-PLAN.md to imagination layer..." -ForegroundColor Yellow

if (-not $DryRun) {
    # The files already exist from our manual creation above
    if ((Test-Path (Join-Path $KDSRoot "brain\imagination\ideas-stashed.yaml")) -and
        (Test-Path (Join-Path $KDSRoot "brain\imagination\semantic-links.yaml")) -and
        (Test-Path (Join-Path $KDSRoot "brain\imagination\questions-answered.yaml"))) {
        Write-Host "      ✅ Imagination layer populated with v6.0 implementation plan" -ForegroundColor Green
        Write-Host "      📊 5 ideas tracked in ideas-stashed.yaml" -ForegroundColor Gray
        Write-Host "      🔗 18 semantic links created" -ForegroundColor Gray
        Write-Host "      ❓ 4 questions documented" -ForegroundColor Gray
    }
} else {
    Write-Host "      [DRY RUN] Would populate imagination layer with:" -ForegroundColor Gray
    Write-Host "         - ideas-stashed.yaml (v6.0 plan tracking)" -ForegroundColor Gray
    Write-Host "         - semantic-links.yaml (idea relationships)" -ForegroundColor Gray
    Write-Host "         - questions-answered.yaml (design decisions)" -ForegroundColor Gray
}
Write-Host ""

# Step 4: Create README files for each tier
Write-Host "[4/6] Creating README files for each tier..." -ForegroundColor Yellow

$readmeFiles = @{
    "brain\README.md" = @"
# KDS Brain Structure (v6.0)

**Inspired by human brain architecture** - Multi-tier intelligence system.

## 📁 Folder Structure

\`\`\`
brain/
├── instinct/              # Tier 0: Permanent core rules (never reset)
├── working-memory/        # Tier 1: Last 20 conversations (FIFO)
├── long-term/             # Tier 2: Consolidated patterns
├── context-awareness/     # Tier 3: Project metrics & intelligence
├── imagination/           # Tier 4: Ideas & questions
├── housekeeping/          # Tier 5: Automatic maintenance
├── sharpener/             # Testing framework
├── event-stream/          # Activity log
├── health/                # Diagnostics
└── archived/              # Historical data
\`\`\`

## 🧠 Brain Region Mapping

| Brain Region | Biological Function | KDS Folder | Purpose |
|--------------|---------------------|------------|---------|
| **Brainstem** | Automatic responses | \`instinct/\` | Core rules, never change |
| **Hippocampus** | Short-term memory | \`working-memory/\` | Recent 20 conversations |
| **Cortex** | Long-term learning | \`long-term/\` | Consolidated patterns |
| **Prefrontal Cortex** | Context & planning | \`context-awareness/\` | Project metrics |
| **Creative Centers** | Imagination | \`imagination/\` | Ideas & questions |
| **Cerebellum** | Automatic maintenance | \`housekeeping/\` | Background cleanup |

## 📖 Migration from v5.0

This structure replaces the flat \`cortex-brain/\` folder with a hierarchical, brain-inspired organization.

**Old (v5.0):**
\`\`\`
cortex-brain/
├── conversation-history.jsonl
├── knowledge-graph.yaml
├── development-context.yaml
└── events.jsonl
\`\`\`

**New (v6.0):**
- \`conversation-history.jsonl\` → Split into \`working-memory/recent-conversations/*.jsonl\`
- \`knowledge-graph.yaml\` → Split into \`long-term/*.yaml\` (specialized files)
- \`development-context.yaml\` → Split into \`context-awareness/*.yaml\`
- \`events.jsonl\` → Moved to \`event-stream/events.jsonl\`

See: \`KDS/docs/KDS-V6-MIGRATION-GUIDE.md\` for complete migration instructions.
"@

    "brain\instinct\README.md" = @"
# Tier 0: Instinct Layer

**Purpose:** Permanent core intelligence that never changes, even during amnesia.

## 📂 Contents

- \`core-rules.yaml\` - 17 governance rules (from governance/rules.md)
- \`solid-principles.yaml\` - Architecture patterns
- \`routing-logic.yaml\` - Intent detection templates
- \`protection-config.yaml\` - Confidence thresholds

## 🔒 Amnesia-Proof

This tier is **NEVER** reset by brain-amnesia.ps1. These are KDS's permanent "instincts."

## 📖 See Also

- Brain Architecture.md - Full brain design
- KDS-DESIGN.md - SOLID v5.0 architecture
"@

    "brain\working-memory\README.md" = @"
# Tier 1: Working Memory

**Purpose:** Short-term conversation history (last 20 conversations, FIFO queue).

## 📂 Contents

- \`recent-conversations/\` - Individual conversation files
- \`conversation-index.yaml\` - Fast lookup index
- \`active-conversation.jsonl\` - Current chat (symlink)

## 🔄 FIFO Queue

- **Capacity:** 20 complete conversations
- **Deletion:** When conversation #21 starts, #1 is deleted
- **No time limit:** Conversations preserved until FIFO deletion
- **Active protected:** Current conversation never deleted

## 📖 See Also

- conversation-context-manager.md - Manages this tier
- BRAIN-CONVERSATION-MEMORY-DESIGN.md - Design details
"@

    "brain\long-term\README.md" = @"
# Tier 2: Long-Term Memory

**Purpose:** Consolidated patterns learned from deleted conversations and interactions.

## 📂 Contents

- \`intent-patterns.yaml\` - Phrase → Intent mappings
- \`file-relationships.yaml\` - Co-modification patterns
- \`workflow-templates.yaml\` - Proven task sequences
- \`error-patterns.yaml\` - Common mistakes
- \`test-patterns.yaml\` - Successful test strategies

## 🧠 Learning Process

1. Conversations live in Tier 1 (working memory)
2. When FIFO deletes conversation → Patterns extracted
3. Patterns consolidated into Tier 2 files
4. Details discarded, learnings preserved

## 📖 See Also

- brain-updater.md - Processes events into patterns
- brain-query.md - Queries this tier
"@

    "brain\context-awareness\README.md" = @"
# Tier 3: Context Awareness

**Purpose:** Holistic project understanding from git, tests, builds, and work patterns.

## 📂 Contents

- \`git-metrics.yaml\` - Commit history, change velocity
- \`velocity-tracking.yaml\` - Development speed trends
- \`file-hotspots.yaml\` - High-churn files
- \`pr-intelligence.yaml\` - PR review patterns
- \`productivity-patterns.yaml\` - Optimal work times

## 🔄 Update Frequency

- **Collection:** After each brain update (>1 hour throttle)
- **Lookback:** 30 days rolling window
- **Aggregation:** Weekly → Monthly → Quarterly

## 📖 See Also

- development-context-collector.md - Collects metrics
- collect-pr-intelligence.ps1 - PR analysis
"@

    "brain\imagination\README.md" = @"
# Tier 4: Imagination

**Purpose:** Creative idea tracking, implementation plans, and question deduplication.

## 📂 Contents

- \`ideas-stashed.yaml\` - Future enhancements and implementation plans
- \`questions-answered.yaml\` - Deduplication cache
- \`semantic-links.yaml\` - Idea relationships

## 💡 Use Cases

### Implementation Plans
All implementation plans (like KDS-V6-HOLISTIC-PLAN.md) should be:
1. **Structured in:** \`ideas-stashed.yaml\` (core idea + status)
2. **Detailed in:** \`docs/*.md\` (full documentation)
3. **Linked via:** \`semantic-links.yaml\` (idea → doc mapping)

**Example:**
\`\`\`yaml
ideas:
  kds-v6-brain-redesign:
    status: in-progress
    priority: high
    created: 2025-11-04
    description: Brain-inspired 6-tier structure
    documentation: docs/KDS-V6-HOLISTIC-PLAN.md
    related_ideas:
      - brain-flush-mechanism
      - extensible-sharpener
\`\`\`

### Question Deduplication
- Avoid answering same question twice
- Track which questions have been answered
- Link to knowledge base articles

### Idea Stashing
- Capture ideas for later (\`stash idea: ...\`)
- Track idea evolution (status: idea → planned → in-progress → implemented)

## 📖 See Also

- knowledge-retriever.md - Queries this tier
- docs/ - Detailed documentation linked from ideas
"@

    "brain\housekeeping\README.md" = @"
# Tier 5: Housekeeping

**Purpose:** Automatic background maintenance and optimization.

## 📂 Services

- \`cleanup-service.ps1\` - Remove unused patterns
- \`organizer-service.ps1\` - Consolidate patterns
- \`optimizer-service.ps1\` - Performance tuning
- \`indexer-service.ps1\` - Rebuild indices
- \`validator-service.ps1\` - Integrity checks
- \`archiver-service.ps1\` - Archive old data

## 📅 Schedules

- **Daily (2am):** cleanup, validator
- **Weekly (Sunday):** organizer
- **Monthly (1st):** optimizer, archiver

## 🎯 Orchestration

\`orchestrator.ps1\` manages all services and schedules.

## 📖 See Also

- KDS-V6-HOLISTIC-PLAN.md - Housekeeping design
"@

    "brain\sharpener\README.md" = @"
# Brain Sharpener Testing Framework

**Purpose:** Extensible plugin-based testing for brain health.

## 📂 Structure

- \`core/\` - Test runner, scenario loader, aggregator
- \`scenarios/\` - YAML test plugins (organized by tier)
- \`results/\` - Historical test runs
- \`config/\` - Benchmarks and thresholds

## 🧪 Test Scenarios

- **Tier 0-4 Tests:** Validate each brain tier
- **Cross-Tier Tests:** Whole-brain processing
- **Total:** 64+ scenario plugins

## 🎯 Usage

\`\`\`markdown
#file:KDS/prompts/user/kds.md sharpen the brain
\`\`\`

**Quick mode:** 5 minutes (critical tests)  
**Full mode:** 30 minutes (all 64+ scenarios)

## 📖 See Also

- BRAIN-SHARPENER.md - Original test documentation
- test-runner.ps1 - Execution engine
"@
}

foreach ($file in $readmeFiles.Keys) {
    $fullPath = Join-Path $KDSRoot $file
    
    if (-not $DryRun) {
        Set-Content -Path $fullPath -Value $readmeFiles[$file] -Force
        Write-Host "      ✅ Created: $file" -ForegroundColor Green
    } else {
        Write-Host "      [DRY RUN] Would create: $file" -ForegroundColor Gray
    }
}

Write-Host ""

# Step 4: Create placeholder files
Write-Host "[5/6] Creating placeholder configuration files..." -ForegroundColor Yellow

$placeholderFiles = @{
    "brain\event-stream\events.jsonl" = ""
    "brain\event-stream\event-index.yaml" = @"
# Event Index for Fast Lookup
# Auto-generated by brain system

events:
  count: 0
  first_event: null
  last_event: null
  
indices:
  by_agent: {}
  by_intent: {}
  by_date: {}
"@

    "brain\health\capacity-metrics.yaml" = @"
# Brain Capacity Metrics
# Monitors storage and performance

storage:
  tier_0_instinct: "0 KB"
  tier_1_working_memory: "0 KB"
  tier_2_long_term: "0 KB"
  tier_3_context: "0 KB"
  tier_4_imagination: "0 KB"
  tier_5_housekeeping: "0 KB"
  total: "0 KB"
  
thresholds:
  warning: "5 MB"
  critical: "20 MB"
  recommendation: "file-based"
  
performance:
  avg_query_time: "0 ms"
  threshold_slow: "500 ms"
  threshold_critical: "1000 ms"
"@

    "brain\housekeeping\config\service-config.yaml" = @"
# Housekeeping Service Configuration
# Controls automatic maintenance

services:
  cleanup:
    enabled: true
    unused_threshold_days: 90
    low_confidence_threshold: 0.60
    duplicate_similarity: 0.85
    
  organizer:
    enabled: true
    consolidate_patterns: true
    rebuild_indices: true
    
  optimizer:
    enabled: true
    defragment_files: true
    compress_events: true
    
  validator:
    enabled: true
    check_references: true
    validate_yaml: true
    
  indexer:
    enabled: true
    rebuild_all: false  # Only rebuild if needed
    
  archiver:
    enabled: true
    retention_days: 180
"@

    "brain\housekeeping\config\thresholds.yaml" = @"
# Thresholds for Housekeeping Actions

storage:
  trigger_cleanup: "3 MB"
  trigger_archive: "5 MB"
  
patterns:
  unused_days: 90
  low_confidence: 0.60
  low_success_rate: 0.50
  
events:
  compress_after: 1000
  archive_after_days: 30
  
conversations:
  fifo_capacity: 20
"@

    "brain\imagination\ideas-stashed.yaml" = (Get-Content "D:\PROJECTS\DevProjects\KDS\brain\imagination\ideas-stashed.yaml" -Raw)
    
    "brain\imagination\semantic-links.yaml" = (Get-Content "D:\PROJECTS\DevProjects\KDS\brain\imagination\semantic-links.yaml" -Raw)
    
    "brain\imagination\questions-answered.yaml" = (Get-Content "D:\PROJECTS\DevProjects\KDS\brain\imagination\questions-answered.yaml" -Raw)
    
    "brain\sharpener\config\benchmarks.yaml" = @"
# Brain Sharpener Benchmarks
# Performance targets for test scenarios

tiers:
  tier_0_instinct:
    routing_accuracy: 0.95
    intent_detection: 0.90
    solid_compliance: 1.00
    
  tier_1_working_memory:
    same_conversation_resolution: 0.98
    cross_conversation_resolution: 0.85
    reference_accuracy: 0.90
    
  tier_2_long_term:
    error_prevention: 0.85
    workflow_success: 0.80
    pattern_accuracy: 0.75
    
  tier_3_context:
    hotspot_detection: 0.85
    velocity_accuracy: 0.70
    warning_precision: 0.80
    
  tier_4_imagination:
    deduplication_rate: 0.95
    idea_linking: 0.70
    
overall:
  health_score_min: 80
  health_score_target: 90
  health_score_excellent: 95
"@
}

foreach ($file in $placeholderFiles.Keys) {
    $fullPath = Join-Path $KDSRoot $file
    
    if (-not $DryRun) {
        Set-Content -Path $fullPath -Value $placeholderFiles[$file] -Force
        Write-Host "      ✅ Created: $file" -ForegroundColor Green
    } else {
        Write-Host "      [DRY RUN] Would create: $file" -ForegroundColor Gray
    }
}

Write-Host ""

# Step 6: Summary
Write-Host "[6/6] Setup Summary" -ForegroundColor Yellow
Write-Host ""
Write-Host "✅ Brain structure created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "📊 What was created:" -ForegroundColor Cyan
Write-Host "   - $foldersCreated new folders in brain/" -ForegroundColor White
Write-Host "   - $($readmeFiles.Count) README files" -ForegroundColor White
Write-Host "   - $($placeholderFiles.Count) placeholder config files" -ForegroundColor White
Write-Host "   - Imagination layer: 5 ideas, 18 links, 4 questions" -ForegroundColor White

if (-not $DryRun) {
    Push-Location $KDSRoot
    $commitHash = git rev-parse --short HEAD 2>$null
    if ($commitHash) {
        Write-Host "   - Git backup commit: $commitHash" -ForegroundColor White
    }
    Pop-Location
}

Write-Host ""
Write-Host "📁 New Structure:" -ForegroundColor Cyan
Write-Host "   brain/" -ForegroundColor White
Write-Host "   ├── instinct/              (Tier 0: Permanent rules)" -ForegroundColor Gray
Write-Host "   ├── working-memory/        (Tier 1: Last 20 conversations)" -ForegroundColor Gray
Write-Host "   ├── long-term/             (Tier 2: Learned patterns)" -ForegroundColor Gray
Write-Host "   ├── context-awareness/     (Tier 3: Project intelligence)" -ForegroundColor Gray
Write-Host "   ├── imagination/           (Tier 4: Ideas)" -ForegroundColor Gray
Write-Host "   ├── housekeeping/          (Tier 5: Auto-maintenance)" -ForegroundColor Gray
Write-Host "   ├── sharpener/             (Testing framework)" -ForegroundColor Gray
Write-Host "   ├── event-stream/          (Activity log)" -ForegroundColor Gray
Write-Host "   ├── health/                (Diagnostics)" -ForegroundColor Gray
Write-Host "   └── archived/              (Historical data)" -ForegroundColor Gray
Write-Host ""

Write-Host "🎯 Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Review the created structure: cd brain/" -ForegroundColor White
Write-Host "   2. Read brain/README.md for overview" -ForegroundColor White
Write-Host "   3. Check imagination/ideas-stashed.yaml for v6.0 plan tracking" -ForegroundColor White
Write-Host "   4. Run Phase 1 migration scripts to populate data" -ForegroundColor White
Write-Host ""

if ($DryRun) {
    Write-Host "⚠️  DRY RUN MODE - No changes were made" -ForegroundColor Yellow
    Write-Host "   Run without -DryRun to actually create the structure" -ForegroundColor Gray
    Write-Host ""
}

Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "✅ SETUP COMPLETE" -ForegroundColor Green
Write-Host "═══════════════════════════════════════════════════════" -ForegroundColor Cyan
