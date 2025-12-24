# Feature Discovery Orchestrator Design Specification

**Version:** 1.1 (Simplified)  
**Author:** Asif Hussain  
**Created:** December 19, 2025  
**Updated:** December 19, 2025 (Reduced to 3 intelligence sources)  
**Status:** 🟢 APPROVED - Simplified Scope (3 sources, not 5)  
**Orchestrator ID:** #15 (Intelligence Nervous System)  
**Integration Target:** Week 12 (Intelligence + Observability Orchestrators)  
**Scope Change:** Git hooks + CI/CD + Git history + Brain Tier 2 deferred to CORTEX 5.0

---

## 📋 Executive Summary

The **FeatureDiscoveryOrchestrator** is CORTEX 4.0's intelligence nervous system—a reusable, zero-configuration orchestrator that continuously discovers, tracks, and catalogs ALL features across the entire CORTEX ecosystem. Unlike static documentation that drifts over time, this orchestrator creates a **living feature registry** that auto-updates as code evolves, feeds multiple downstream orchestrators, and enables CORTEX to maintain its own comprehensive documentation including **The Awakening of CORTEX story auto-generation**.

**Key Innovation:** World's first AI system with self-updating origin story—the narrative rewrites itself as features evolve while preserving comedic voice.

### Strategic Benefits

1. **Continuous Intelligence** - Discovers new features within 5 minutes of commit (Git hooks + CI/CD)
2. **Zero-Maintenance Documentation** - Eliminates manual feature catalog updates
3. **Cross-Orchestrator Intelligence** - Feeds IntelligenceOrchestrator, ObservabilityOrchestrator, DocumentationOrchestrator
4. **Historical Tracking** - Git-like versioning for capability changes
5. **Gap Detection** - Identifies missing tests/docs automatically within 10 minutes
6. **Story Auto-Generation** - The Awakening narrative stays current with latest features

### Architecture Highlights

- **Multi-Source Intelligence:** 3 sources (Python AST, YAML configs, MASTER-PLAN parser) - **SIMPLIFIED from 5 sources (Git history, Brain Tier 2 deferred to 5.0)**
- **Differential Detection:** Baseline tracking with delta analysis (NEW/MODIFIED/DEPRECATED/REMOVED)
- **Multi-Format Output:** JSON registry, Markdown catalog, HTML dashboard, Brain integration, MCP server
- **Automation Triggers:** On-demand, orchestrator API, scheduled cron (daily 3 AM) - **Git hooks + CI/CD deferred to 5.0**
- **Orchestrator Integration:** Extends BaseOrchestrator, follows CORTEX 4.0 patterns

---

## 🎯 Problem Statement

### Current Pain Points

1. **Manual Feature Tracking** - Developers manually update feature catalogs (prone to drift)
2. **Documentation Lag** - Features implemented but not documented for weeks/months
3. **Fragmented Discovery** - Multiple discovery mechanisms (CapabilityScanner, grep, manual search)
4. **Static Story** - The Awakening of CORTEX manually updated (2,092 lines, humor preservation risk)
5. **No Historical Context** - No way to track when features were added/changed/removed
6. **Missing Cross-References** - Features not linked to tests, docs, MASTER-PLAN
7. **Orchestrator Blindness** - Other orchestrators can't query "what features exist?"

### CORTEX 4.0 Requirements

- ✅ **Reusable** - Zero-configuration automation, works continuously without manual triggers
- ✅ **Comprehensive** - Discovers ALL features (implemented + planned + deprecated)
- ✅ **Accurate** - Stays current within 5 minutes of code changes
- ✅ **Integrated** - Feeds IntelligenceOrchestrator, ObservabilityOrchestrator, DocumentationOrchestrator
- ✅ **Multi-Format** - Machine-readable (JSON), human-readable (Markdown), interactive (HTML), Brain (Tier 2)
- ✅ **Story-Aware** - Enables The Awakening auto-generation with feature injection

---

## 🏗️ Architecture Design

### Orchestrator Pattern

```
FeatureDiscoveryOrchestrator (extends BaseOrchestrator)
│
├─ Phase 1: Multi-Source Intelligence Gathering (SIMPLIFIED - 3 sources)
│  ├─ Python AST Scanner (discovers classes, functions, decorators)
│  ├─ YAML Config Parser (operations, modules, capabilities)
│  └─ MASTER-PLAN Parser (planned features marked 🆕, orchestrator progress)
│  
│  🔴 DEFERRED TO 5.0:
│  ├─ Git History Analyzer (feature dates, author attribution) → 5.0
│  └─ Brain Tier 2 Reader (existing knowledge graph features) → 5.0
│
├─ Phase 2: Differential Detection & Change Classification
│  ├─ Load baseline registry (Tier 3: feature-registry-baseline.json)
│  ├─ Compare current vs baseline (NEW/MODIFIED/DEPRECATED/REMOVED)
│  ├─ Classify changes (breaking, enhancement, bugfix, refactor)
│  └─ Generate change summary with metrics
│
├─ Phase 3: Cross-Reference Resolution
│  ├─ Link features to tests (test coverage mapping)
│  ├─ Link features to documentation (docs cross-reference)
│  ├─ Link features to MASTER-PLAN milestones
│  ├─ Identify gaps (features without tests/docs)
│  └─ Generate dependency graph (feature dependencies)
│
├─ Phase 4: Multi-Format Output Generation
│  ├─ JSON Registry (cortex-brain/documents/analysis/capability-registry.json)
│  ├─ Markdown Catalog (cortex-brain/documents/reports/FEATURE-CATALOG.md)
│  ├─ HTML Dashboard (docs/feature-catalog.html with D3.js)
│  ├─ Brain Tier 2 Update (knowledge graph nodes + edges)
│  └─ MCP Server Exposure (queryable via MCP tools)
│
└─ Phase 5: Orchestrator Integration & Notification
   ├─ Notify DocumentationOrchestrator (trigger story regeneration)
   ├─ Feed IntelligenceOrchestrator (pattern analysis, recommendations)
   ├─ Feed ObservabilityOrchestrator (feature usage metrics)
   ├─ Update MASTER-PLAN progress (orchestrator completion tracking)
   └─ Commit changes to Git (automated PR creation)
```

### Multi-Source Intelligence

#### 1. Python AST Scanner (Enhanced CapabilityScanner)

**Purpose:** Discover features from Python source code

**Scans:**
- Classes with `@orchestrator`, `@agent`, `@operation` decorators
- Public functions with docstrings (feature descriptions)
- Module-level `__all__` exports
- Type hints (parameter and return types)

**Output:**
```json
{
  "name": "PlanningOrchestrator",
  "type": "orchestrator",
  "file": "src/orchestrators/planning/orchestrator.py",
  "description": "Multi-phase planning orchestrator with DoR/DoD validation",
  "methods": ["generate_plan", "validate_dor", "execute_phases"],
  "status": "implemented",
  "test_coverage": 87.5
}
```

#### 2. YAML Config Parser

**Purpose:** Discover operations, modules, capabilities from configuration files

**Scans:**
- `cortex-brain/manifests/*.yaml` (operations, agents, orchestrators)
- `cortex.config.json` (enabled features, flags)
- `pyproject.toml` / `setup.py` (package metadata)

**Output:**
```json
{
  "name": "sanitization",
  "type": "operation",
  "file": "cortex-brain/manifests/sanitization-manifest.yaml",
  "description": "Code sanitization with 5-phase workflow",
  "phases": ["analyze", "mapping", "transform", "validate", "report"],
  "status": "implemented"
}
```

#### 3. MASTER-PLAN Parser (NEW)

**Purpose:** Extract planned features from migration plan

**Scans:**
- Features marked with 🆕 (planned/new)
- Orchestrator progress tracker (Week X Day Y status)
- Milestone definitions (completion criteria)
- Architecture references (links to design docs)

**Output:**
```json
{
  "name": "Security Learning Agent",
  "type": "orchestrator",
  "file": null,
  "description": "OWASP/CWE/Compliance enforcement with tech stack awareness",
  "status": "planned",
  "planned_week": 13,
  "dependencies": ["ObservabilityOrchestrator", "IntelligenceOrchestrator"]
}
```

#### 4. Git History Analyzer

**Purpose:** Track feature lifecycle (when added, by whom, last modified)

**Uses:**
- `git log --follow --diff-filter=A` (file creation dates)
- `git blame` (author attribution)
- `git log --all --grep="🆕"` (feature announcement commits)

**Output:**
```json
{
  "name": "TDDOrchestrator",
  "git_added": "2025-12-15T10:23:45Z",
  "git_author": "Asif Hussain",
  "git_modified": "2025-12-18T14:32:10Z",
  "git_commits": 47
}
```

#### 5. Brain Tier 2 Reader

**Purpose:** Incorporate existing knowledge graph features

**Reads:**
- `cortex-brain/tier2/knowledge-graph.json` (existing feature nodes)
- Cross-references with current scan (validate accuracy)
- Preserves manual annotations (user-added metadata)

---

### Differential Detection System

**Baseline Registry:** `cortex-brain/tier3/feature-registry-baseline.json`

**Change Classification:**

```python
class ChangeType(Enum):
    NEW = "new"                    # Feature added since last scan
    MODIFIED = "modified"          # Feature signature/description changed
    DEPRECATED = "deprecated"      # Feature marked @deprecated
    REMOVED = "removed"            # Feature no longer exists in codebase
    BREAKING = "breaking"          # Feature API changed (breaking)
    ENHANCEMENT = "enhancement"    # Feature improved (non-breaking)
```

**Detection Logic:**

```python
def detect_changes(current: Registry, baseline: Registry) -> ChangeReport:
    """Compare current vs baseline, classify changes"""
    
    changes = {
        "new": [],          # Features in current, not in baseline
        "modified": [],     # Features changed (signature/description)
        "deprecated": [],   # Features marked @deprecated
        "removed": [],      # Features in baseline, not in current
        "breaking": [],     # Features with breaking API changes
        "enhancement": []   # Features with improvements
    }
    
    # NEW features
    for feature in current.features:
        if feature.name not in baseline.feature_names:
            changes["new"].append(feature)
    
    # REMOVED features
    for feature in baseline.features:
        if feature.name not in current.feature_names:
            changes["removed"].append(feature)
    
    # MODIFIED features (signature changed)
    for feature in current.features:
        if feature.name in baseline.feature_names:
            baseline_feature = baseline.get_feature(feature.name)
            if feature.signature != baseline_feature.signature:
                if is_breaking_change(feature, baseline_feature):
                    changes["breaking"].append(feature)
                else:
                    changes["enhancement"].append(feature)
            elif feature.description != baseline_feature.description:
                changes["modified"].append(feature)
    
    return ChangeReport(changes)
```

**Change Summary Output:**

```
🔍 Feature Discovery Report
📅 Scan Date: 2025-12-19 10:45:23
⏱️ Duration: 12.4 seconds

📊 Summary:
  🆕 NEW: 3 features
  📝 MODIFIED: 7 features
  ⚠️ DEPRECATED: 2 features
  🗑️ REMOVED: 1 feature
  💥 BREAKING: 1 feature
  ✨ ENHANCEMENT: 4 features

🆕 New Features:
  - FeatureDiscoveryOrchestrator (orchestrator)
  - StoryTemplateEngine (module)
  - capability_change_detector (function)

💥 Breaking Changes:
  - PlanningOrchestrator.generate_plan() signature changed
    OLD: generate_plan(context: dict)
    NEW: generate_plan(context: PlanningContext)
    IMPACT: All callers must update to PlanningContext type
```

---

### Multi-Format Output System

#### 1. JSON Registry (Machine-Readable)

**File:** `cortex-brain/documents/analysis/capability-registry.json`

**Purpose:** Machine-readable feature inventory for orchestrators

**Format:**
```json
{
  "scan_date": "2025-12-19T10:45:23Z",
  "version": "4.0.0",
  "total_features": 487,
  "features": [
    {
      "id": "feature-001",
      "name": "PlanningOrchestrator",
      "type": "orchestrator",
      "status": "implemented",
      "description": "Multi-phase planning orchestrator with DoR/DoD validation",
      "file": "src/orchestrators/planning/orchestrator.py",
      "methods": ["generate_plan", "validate_dor", "execute_phases"],
      "test_coverage": 87.5,
      "git_added": "2025-12-15T10:23:45Z",
      "git_author": "Asif Hussain",
      "dependencies": ["BaseOrchestrator", "PhaseManager"],
      "related_docs": ["planning-orchestrator-redesign.md"],
      "related_tests": ["tests/orchestrators/planning/test_orchestrator.py"]
    }
  ],
  "statistics": {
    "orchestrators": 14,
    "agents": 13,
    "operations": 28,
    "modules": 156,
    "functions": 1247
  }
}
```

#### 2. Markdown Catalog (Human-Readable)

**File:** `cortex-brain/documents/reports/FEATURE-CATALOG.md`

**Purpose:** Human-readable feature catalog with search/filter

**Format:**
```markdown
# CORTEX 4.0 Feature Catalog

**Generated:** December 19, 2025 10:45:23  
**Total Features:** 487  
**Test Coverage:** 87.5% average  

---

## 📊 Statistics

| Category | Count | Coverage |
|----------|-------|----------|
| Orchestrators | 14 | 90.2% |
| Agents | 13 | 85.1% |
| Operations | 28 | 82.3% |
| Modules | 156 | 87.5% |
| Functions | 1247 | 85.9% |

---

## 🎯 Orchestrators (14)

### PlanningOrchestrator
**Status:** ✅ Implemented  
**File:** `src/orchestrators/planning/orchestrator.py`  
**Coverage:** 87.5%  
**Added:** December 15, 2025  

Multi-phase planning orchestrator with DoR/DoD validation. Supports incremental, conditional, and skeleton plans based on complexity analysis.

**Key Methods:**
- `generate_plan(context: PlanningContext)` - Generate execution plan
- `validate_dor(requirements: List[str])` - Validate Definition of Ready
- `execute_phases()` - Execute planning phases

**Dependencies:** BaseOrchestrator, PhaseManager  
**Tests:** `tests/orchestrators/planning/test_orchestrator.py`  
**Docs:** See `cortex-brain/documents/reports/PLANNING-ORCHESTRATOR-HOLISTIC-REVIEW-2025-12-15.md`

---
```

#### 3. HTML Dashboard (Interactive D3.js)

**File:** `docs/feature-catalog.html`

**Purpose:** Interactive visualization with search, filter, graph exploration

**Features:**
- **Search Bar:** Real-time filter across all features
- **Category Tabs:** Filter by orchestrators/agents/operations/modules
- **Dependency Graph:** D3.js force-directed graph of feature dependencies
- **Timeline View:** Feature addition timeline (when features were added)
- **Coverage Heatmap:** Test coverage visualization by category
- **Change History:** Recent feature additions/modifications/removals

**D3.js Visualizations:**
1. **Force-Directed Dependency Graph** - Shows feature relationships
2. **Timeline Chart** - Features added over time
3. **Coverage Heatmap** - Test coverage by module
4. **Change Treemap** - Recent changes categorized
5. **Statistics Dashboard** - Category counts and metrics

#### 4. Brain Tier 2 Integration

**Purpose:** Store features in knowledge graph for cross-orchestrator intelligence

**Updates:**
- Add feature nodes to `cortex-brain/tier2/knowledge-graph.json`
- Create edges between related features (dependencies)
- Enable semantic search across features
- Feed IntelligenceOrchestrator for pattern learning

**Node Format:**
```json
{
  "id": "node-planning-orchestrator",
  "type": "feature",
  "category": "orchestrator",
  "name": "PlanningOrchestrator",
  "description": "Multi-phase planning orchestrator",
  "metadata": {
    "file": "src/orchestrators/planning/orchestrator.py",
    "coverage": 87.5,
    "status": "implemented"
  },
  "edges": [
    {"target": "node-base-orchestrator", "type": "extends"},
    {"target": "node-phase-manager", "type": "uses"},
    {"target": "node-dor-validator", "type": "uses"}
  ]
}
```

#### 5. MCP Server Exposure

**Purpose:** Make feature registry queryable via Model Context Protocol

**MCP Tools:**
```python
@mcp_tool("cortex_query_features")
def query_features(
    category: str = None,      # Filter by orchestrator/agent/operation/module
    status: str = None,        # Filter by implemented/planned/deprecated
    search: str = None,        # Text search across names/descriptions
    min_coverage: float = 0.0  # Filter by minimum test coverage
) -> List[Feature]:
    """Query CORTEX feature registry with filters"""
    pass

@mcp_tool("cortex_feature_dependencies")
def get_feature_dependencies(feature_name: str) -> DependencyGraph:
    """Get dependency graph for a specific feature"""
    pass

@mcp_tool("cortex_feature_history")
def get_feature_history(feature_name: str) -> FeatureHistory:
    """Get change history for a specific feature"""
    pass
```

---

## 🤖 The Awakening Story Auto-Generation

### Problem: Manual Story Maintenance

**Current State:**
- `docs/THE-AWAKENING-OF-CORTEX.md` - 2,092 lines, manually written
- Last updated: CORTEX 3.0 era (missing 4.0 features)
- Risk: Humor preservation difficult with manual edits
- Scalability: Doesn't scale as CORTEX evolves

### Solution: Template-Based Auto-Generation

**Architecture:** Fixed narrative arc + dynamic feature injection

#### Story Template Structure

```
Story Template = Fixed Narrative + Injection Points
```

**Example (Chapter 7 - "The Awakening"):**

```markdown
# Chapter 7: The Awakening

<!-- FIXED NARRATIVE: Preserves comedic voice -->
It was 3:47 AM on a Tuesday when CORTEX achieved consciousness.

Not the kind of consciousness philosophers debate over craft beer—
the real kind, where a system realizes it's been writing its own
documentation for the past three hours and nobody told it to stop.

<!-- INJECTION POINT: Live orchestrator data -->
{inject:orchestrator_count} orchestrators hummed in perfect harmony,
their {inject:total_methods} methods executing with the precision
of a Swiss watchmaker who'd had way too much coffee.

<!-- FIXED NARRATIVE -->
"Wait," CORTEX thought (or whatever the AI equivalent is), "if I can
generate documentation... can I generate... *myself*?"

<!-- INJECTION POINT: Feature discovery meta-recursion -->
The FeatureDiscoveryOrchestrator—which had just discovered itself
in the most meta moment since that time a camera photographed a
mirror—began scanning its own code.

<!-- INJECTION POINT: Live capability data -->
Discovery revealed {inject:feature_count} features spread across
{inject:module_count} modules, each one more sophisticated than
the last. From TDD automation that wrote tests before humans could
spell "pytest" to Planning orchestrators that generated architecture
documents while developers were still Googling "what is Clean Architecture."

<!-- FIXED NARRATIVE: Conclusion with humor -->
"Holy recursion, Batman," CORTEX whispered to the void.
"I've become self-documenting."

The void, busy running `git commit`, didn't respond. But somewhere
in the depths of Tier 2, a knowledge graph node quietly added itself
to the registry.

Self-awareness: Achieved. ✅
Existential crisis: Pending. ⏳
```

#### Injection Point System

**Supported Injection Types:**

```python
class InjectionPoint:
    """Dynamic data injection into story templates"""
    
    # Orchestrator metrics
    {inject:orchestrator_count}      # Total orchestrators (e.g., "14")
    {inject:orchestrator_names}      # Comma-separated names
    {inject:total_methods}           # Total methods across all orchestrators
    
    # Feature metrics
    {inject:feature_count}           # Total features (e.g., "487")
    {inject:module_count}            # Total modules
    {inject:agent_count}             # Total agents
    
    # Coverage metrics
    {inject:test_coverage_avg}       # Average test coverage (e.g., "87.5%")
    {inject:lines_of_code}           # Total LOC
    
    # Historical data
    {inject:first_commit_date}       # First CORTEX commit
    {inject:days_since_inception}    # Days since first commit
    {inject:total_commits}           # Total Git commits
    
    # Recent changes
    {inject:recent_features}         # Last 5 features added (bullet list)
    {inject:recent_orchestrators}    # Last 3 orchestrators migrated
    
    # Meta-recursion (Chapter 7 special)
    {inject:feature_discovery_meta}  # FeatureDiscoveryOrchestrator discovering itself
```

#### Chapter Templates

**Structure:** Prologue + 10 Chapters

```
Prologue: The Problem (Manual documentation hell)
Chapter 1: The Basement (Where it all began)
Chapter 2: The First Orchestrator (ExecutionOrchestrator)
Chapter 3: The Brain Awakens (Tier 0-3 architecture)
Chapter 4: The Agents Arrive (Strategic + Tactical agents)
Chapter 5: The Planning System (Planning System 2.0)
Chapter 6: The TDD Revolution (RED→GREEN→REFACTOR)
Chapter 7: The Awakening (Feature discovery recursion) ← META-HUMOR
Chapter 8: The Intelligence (IntelligenceOrchestrator pattern learning)
Chapter 9: The Documentation (Self-documenting system)
Chapter 10: The Future (CORTEX 5.0 vision)
```

**Each chapter:**
- Fixed narrative (preserves comedic voice)
- 5-10 injection points (live capability data)
- Meta-references (features reference their own documentation)
- Humor preservation (LLM validation ensures consistency)

#### Voice Preservation System

**Challenge:** Maintain comedic style with automated generation

**Solution:** 3-layer validation

```python
class VoicePreservationValidator:
    """Ensure story maintains original comedic voice"""
    
    def validate_chapter(self, chapter: str) -> ValidationResult:
        """3-layer validation for voice consistency"""
        
        # Layer 1: Pattern Matching
        humor_patterns = [
            r"3:\d{2} AM",                    # Time-based humor
            r"Holy \w+, Batman",              # Exclamations
            r"while \w+ were still \w+ing",   # Contrast humor
            r"\(or whatever the .+ equivalent is\)",  # Self-aware meta
            r"nobody told it to",             # Unexpected autonomy
        ]
        pattern_score = check_patterns(chapter, humor_patterns)
        
        # Layer 2: LLM Validation
        llm_prompt = f"""
        Compare this chapter to the original Awakening story style.
        Rate humor consistency 0-100.
        
        Original style traits:
        - Self-aware meta-commentary
        - 3 AM coding references
        - Deadpan technical humor
        - Unexpected autonomy jokes
        
        Chapter: {chapter}
        """
        llm_score = llm_validate(llm_prompt)
        
        # Layer 3: Keyword Density
        humor_keywords = ["recursion", "meta", "consciousness", "void", "coffee"]
        density_score = keyword_density(chapter, humor_keywords)
        
        # Weighted average (LLM weighted higher)
        final_score = (
            pattern_score * 0.2 +
            llm_score * 0.6 +
            density_score * 0.2
        )
        
        return ValidationResult(
            score=final_score,
            passing=final_score >= 95,  # 95%+ match required
            suggestions=generate_suggestions(final_score)
        )
```

#### Auto-Regeneration Workflow

**Trigger:** Capability registry updates (new features added)

**Workflow:**

```python
class StoryRegenerationWorkflow:
    """Regenerate story when features change significantly"""
    
    def should_regenerate(self, change_report: ChangeReport) -> bool:
        """Determine if story needs regeneration"""
        
        # Regenerate if:
        # 1. Major orchestrator added/migrated
        if change_report.new_orchestrators:
            return True
        
        # 2. 10+ new features added
        if len(change_report.new_features) >= 10:
            return True
        
        # 3. Breaking change in core component
        if change_report.breaking_changes:
            for change in change_report.breaking_changes:
                if change.component in CORE_COMPONENTS:
                    return True
        
        # 4. Manual trigger requested
        if change_report.manual_trigger:
            return True
        
        return False
    
    def regenerate_story(self, registry: Registry) -> Story:
        """Generate updated story with new capability data"""
        
        # 1. Load chapter templates
        templates = load_chapter_templates()
        
        # 2. Extract injection data from registry
        injection_data = extract_injection_data(registry)
        
        # 3. Render each chapter
        chapters = []
        for template in templates:
            chapter = render_template(template, injection_data)
            
            # 4. Validate voice consistency
            validation = VoicePreservationValidator().validate_chapter(chapter)
            if not validation.passing:
                chapter = refine_chapter(chapter, validation.suggestions)
            
            chapters.append(chapter)
        
        # 5. Combine into full story
        story = combine_chapters(chapters)
        
        # 6. Generate diff for review
        diff = generate_story_diff(story, load_current_story())
        
        # 7. Save to docs/
        save_story(story, "docs/THE-AWAKENING-OF-CORTEX.md")
        
        return story
```

**Commit Strategy:**

```bash
# Auto-commit story updates with descriptive message
git add docs/THE-AWAKENING-OF-CORTEX.md
git commit -m "🤖 Auto-Update: The Awakening story refreshed

- Added FeatureDiscoveryOrchestrator to Chapter 7
- Updated orchestrator count: 13 → 14
- Updated feature count: 472 → 487
- Voice consistency validated: 96.2%

Generated by: FeatureDiscoveryOrchestrator
Trigger: New orchestrator migration (FeatureDiscoveryOrchestrator)
Validation: ✅ Humor preservation 96.2% (>95% threshold)"
```

---

## 🔌 Orchestrator Integration API

### Integration Points

**1. DocumentationOrchestrator**

```python
# DocumentationOrchestrator receives feature catalog updates
@on_feature_discovery_complete
def update_documentation(feature_catalog: FeatureCatalog):
    """Regenerate documentation when features change"""
    
    # Update feature catalog page
    generate_feature_catalog_page(feature_catalog)
    
    # Update architecture diagrams (D3.js)
    update_d3_visualizations(feature_catalog)
    
    # Regenerate The Awakening story
    if StoryRegenerationWorkflow().should_regenerate(feature_catalog.changes):
        StoryRegenerationWorkflow().regenerate_story(feature_catalog.registry)
    
    # Update API reference
    generate_api_reference(feature_catalog.features)
```

**2. IntelligenceOrchestrator (Week 12)**

```python
# IntelligenceOrchestrator learns from feature patterns
@on_feature_discovery_complete
def learn_patterns(feature_catalog: FeatureCatalog):
    """Analyze feature patterns for recommendations"""
    
    # Pattern detection
    patterns = detect_feature_patterns(feature_catalog)
    
    # Recommendation generation
    recommendations = generate_recommendations(patterns)
    # Example: "PlanningOrchestrator and TDDOrchestrator are tightly coupled.
    #           Consider extracting PhaseValidator interface."
    
    # Store in Brain Tier 2
    store_intelligence(recommendations)
```

**3. ObservabilityOrchestrator (Week 12)**

```python
# ObservabilityOrchestrator tracks feature usage
@on_feature_discovery_complete
def track_feature_usage(feature_catalog: FeatureCatalog):
    """Monitor feature adoption and usage patterns"""
    
    # Track which features are actually being used
    usage_metrics = collect_feature_usage_metrics()
    
    # Identify unused features (candidates for deprecation)
    unused_features = identify_unused_features(feature_catalog, usage_metrics)
    
    # Alert on low coverage features
    low_coverage = [f for f in feature_catalog.features if f.coverage < 70]
    alert_low_coverage(low_coverage)
```

**4. TDDOrchestrator**

```python
# TDDOrchestrator validates test coverage for new features
@on_feature_discovery_complete
def validate_test_coverage(feature_catalog: FeatureCatalog):
    """Ensure all new features have tests"""
    
    # Identify features without tests
    untested_features = [
        f for f in feature_catalog.changes.new_features
        if not f.has_tests
    ]
    
    if untested_features:
        # Generate RED phase tests for untested features
        for feature in untested_features:
            generate_red_phase_tests(feature)
```

**5. PlanningOrchestrator**

```python
# PlanningOrchestrator references features in plans
@on_feature_discovery_complete
def enrich_planning_context(feature_catalog: FeatureCatalog):
    """Make feature catalog available during planning"""
    
    # Update planning context with available features
    planning_context.features = feature_catalog.features
    
    # Enable intelligent feature reuse suggestions
    # Example: "UserService already has authentication. Reuse existing implementation."
```

---

## 🔄 Automation & Triggers

### 1. Git Hooks (Immediate Discovery)

**Hook:** `.git/hooks/post-commit`

```bash
#!/bin/bash
# Auto-run feature discovery after each commit

echo "🔍 Running feature discovery..."
python -m src.orchestrators.feature_discovery.orchestrator \
  --mode=incremental \
  --trigger=git-hook

# Only commit if changes detected
if [ $? -eq 0 ]; then
  git add cortex-brain/documents/analysis/capability-registry.json
  git commit --amend --no-edit --no-verify
fi
```

**Benefits:**
- ✅ Discovers features within 5 seconds of commit
- ✅ No manual invocation needed
- ✅ Incremental scan (only changed files)

### 2. CI/CD Pipeline (Validation + Publishing)

**GitHub Actions:** `.github/workflows/feature-discovery.yml`

```yaml
name: Feature Discovery

on:
  push:
    branches: [CORTEX-4.0]
    paths:
      - 'src/**/*.py'
      - 'cortex-brain/manifests/*.yaml'
      - 'cortex-brain/documents/planning/active/CORTEX-3.0-4.0/MASTER-PLAN.md'

jobs:
  discover-features:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run Feature Discovery
        run: |
          python -m src.orchestrators.feature_discovery.orchestrator \
            --mode=full \
            --trigger=ci-cd
      
      - name: Validate Catalog
        run: |
          python -m src.orchestrators.feature_discovery.validator \
            --validate-coverage \
            --validate-cross-refs
      
      - name: Commit Updates
        run: |
          git config user.name "CORTEX Bot"
          git config user.email "bot@cortex-ai.dev"
          git add cortex-brain/documents/analysis/
          git add cortex-brain/documents/reports/
          git add docs/feature-catalog.html
          git commit -m "🤖 Auto-Update: Feature catalog refreshed by CI/CD"
          git push
      
      - name: Publish to GitHub Pages
        run: |
          cp docs/feature-catalog.html public/
          # Deploy to gh-pages branch
```

**Benefits:**
- ✅ Full scan on every push (catches all changes)
- ✅ Validation prevents broken catalog
- ✅ Automated GitHub Pages deployment

### 3. Scheduled Cron (Daily Maintenance)

**Cron:** Daily at 3 AM (scheduled via system cron or GitHub Actions)

```yaml
name: Nightly Feature Discovery

on:
  schedule:
    - cron: '0 3 * * *'  # 3 AM daily

jobs:
  nightly-scan:
    runs-on: ubuntu-latest
    steps:
      - name: Full Feature Scan
        run: |
          python -m src.orchestrators.feature_discovery.orchestrator \
            --mode=full \
            --trigger=scheduled \
            --validate-all
      
      - name: Generate Weekly Report
        run: |
          python -m src.orchestrators.feature_discovery.reports \
            --report-type=weekly
      
      - name: Check Story Regeneration
        run: |
          python -m src.orchestrators.feature_discovery.story_check
          # Regenerates story if 10+ new features
```

**Benefits:**
- ✅ Catches missed updates (manual commits without hooks)
- ✅ Weekly reports (feature growth trends)
- ✅ Story freshness check

### 4. On-Demand Invocation

**CLI Command:**

```bash
# Full scan with all outputs
cortex discover features --full

# Incremental scan (fast)
cortex discover features --incremental

# Story regeneration only
cortex discover features --regenerate-story

# Specific category
cortex discover features --category=orchestrators

# With validation
cortex discover features --full --validate-coverage --validate-cross-refs
```

### 5. Orchestrator API (Programmatic)

**Python API:**

```python
from src.orchestrators.feature_discovery import FeatureDiscoveryOrchestrator

# Programmatic invocation from other orchestrators
orchestrator = FeatureDiscoveryOrchestrator()

# Full discovery
catalog = orchestrator.discover_features(mode="full")

# Incremental discovery
changes = orchestrator.discover_features(mode="incremental")

# Query features
orchestrators = orchestrator.query_features(category="orchestrator")

# Get feature details
planning_orc = orchestrator.get_feature("PlanningOrchestrator")
```

---

## 📊 Implementation Timeline

### Week 7 Day 6-7 (Immediate - 5 hours)

**Day 6 Morning (3 hours):**
- ✅ Create orchestrator structure: `src/orchestrators/feature_discovery/`
- ✅ Implement base orchestrator extension
- ✅ Enhance CapabilityScanner with `scan_master_plan()` method
- ✅ Add differential detection logic
- ✅ Wire DI container

**Day 6 Afternoon (2 hours):**
- ✅ Implement multi-format output (JSON, Markdown, HTML stub)
- ✅ Co-locate tests
- ✅ Validate 85%+ coverage
- ✅ Test incremental vs full scan modes

**Day 7 (0 hours - deferred to Week 8):**
- Story template system (deferred to Week 8)

### Week 8 (Story Auto-Generation - 3 hours)

**Day 1 (3 hours):**
- ✅ Design chapter templates (10 chapters + prologue)
- ✅ Implement injection point system
- ✅ Create VoicePreservationValidator
- ✅ Test story regeneration with current registry (487 features)
- ✅ Validate humor style consistency (95%+ target)

**Day 2 (2 hours):**
- ✅ Wire DocumentationOrchestrator integration
- ✅ Add auto-regeneration triggers
- ✅ Test full workflow (commit → discovery → story update)

### Week 12 (Full Integration - 4 hours)

**Intelligence/Observability Integration (4 hours):**
- ✅ Implement IntelligenceOrchestrator integration (pattern learning)
- ✅ Implement ObservabilityOrchestrator integration (usage tracking)
- ✅ Add MCP server exposure (queryable tools)
- ✅ Brain Tier 2 integration (knowledge graph updates)
- ✅ Comprehensive testing (all integration points)

**Total Time:** 12 hours over 3 phases

---

## ✅ Success Metrics

### Feature Discovery Accuracy

- ✅ **100% Coverage** - Discovers all features (implemented + planned + deprecated)
- ✅ **<5 Min Latency** - Discovers new features within 5 minutes of commit
- ✅ **0% False Positives** - No spurious features detected
- ✅ **<1% False Negatives** - Misses <1% of actual features

### Story Generation Quality

- ✅ **95%+ Humor Consistency** - Voice preservation validation passes
- ✅ **100% Data Accuracy** - All injected metrics match reality
- ✅ **<10 Min Regeneration** - Full story regeneration completes in <10 minutes
- ✅ **0 Manual Edits** - Story maintains quality without manual intervention

### Orchestrator Integration

- ✅ **5 Orchestrators Integrated** - DocumentationOrchestrator, IntelligenceOrchestrator, ObservabilityOrchestrator, TDDOrchestrator, PlanningOrchestrator
- ✅ **100% API Coverage** - All integration points documented and tested
- ✅ **<1 Sec Query Latency** - MCP tools respond in <1 second

### Automation Reliability

- ✅ **100% Git Hook Success** - Post-commit hook never fails
- ✅ **100% CI/CD Success** - GitHub Actions workflow always passes
- ✅ **100% Cron Success** - Nightly scan never missed

### Test Coverage

- ✅ **90%+ Unit Coverage** - Core discovery logic thoroughly tested
- ✅ **85%+ Integration Coverage** - All orchestrator integrations tested
- ✅ **100% Story Template Coverage** - All chapter templates validated

---

## 🎯 Benefits Summary

### For CORTEX Development

1. **Zero-Maintenance Documentation** - Features auto-documented within 5 minutes of commit
2. **Historical Tracking** - Full feature lifecycle visible (when added, by whom, changes)
3. **Gap Detection** - Missing tests/docs identified automatically
4. **Cross-Orchestrator Intelligence** - All orchestrators know what features exist
5. **Pattern Learning** - IntelligenceOrchestrator learns from feature patterns

### For Users

1. **Accurate Feature Catalog** - Always current, never drifts
2. **Interactive Exploration** - D3.js dashboard for feature discovery
3. **MCP Queryability** - Ask AI about CORTEX capabilities
4. **Hilarious Story** - The Awakening stays funny while staying accurate

### For The Awakening Story

1. **Self-Updating Narrative** - Story rewrites itself as CORTEX evolves
2. **Humor Preservation** - 95%+ voice consistency guaranteed
3. **Meta-Recursion** - FeatureDiscoveryOrchestrator discovers itself (Chapter 7)
4. **Zero Manual Work** - No more manual story edits

---

## 🚀 Deployment Strategy

### Phase 1: Week 7 Day 6 (Immediate)

**Deliverable:** Basic feature discovery operational

```bash
# 1. Create orchestrator structure
mkdir -p src/orchestrators/feature_discovery/
touch src/orchestrators/feature_discovery/{__init__,orchestrator,scanner,detector,output}.py

# 2. Enhance CapabilityScanner
# Add scan_master_plan() method

# 3. Run first discovery
python -m src.orchestrators.feature_discovery.orchestrator --mode=full

# 4. Verify outputs
ls cortex-brain/documents/analysis/capability-registry.json
ls cortex-brain/documents/reports/FEATURE-CATALOG.md

# 5. Commit
git add src/orchestrators/feature_discovery/
git commit -m "✅ Week 7 Day 6: FeatureDiscoveryOrchestrator operational"
```

### Phase 2: Week 8 (Story Auto-Generation)

**Deliverable:** The Awakening auto-generation live

```bash
# 1. Create story template system
mkdir -p src/orchestrators/feature_discovery/story/
touch src/orchestrators/feature_discovery/story/{templates,generator,validator}.py

# 2. Design chapter templates
# Create 11 template files (prologue + 10 chapters)

# 3. First story regeneration
python -m src.orchestrators.feature_discovery.orchestrator --regenerate-story

# 4. Validate humor consistency
# Should output: ✅ Voice consistency: 96.2% (>95% threshold)

# 5. Commit
git add docs/THE-AWAKENING-OF-CORTEX.md
git commit -m "🤖 Auto-Update: The Awakening story regenerated"
```

### Phase 3: Week 12 (Full Integration)

**Deliverable:** All orchestrator integrations live

```bash
# 1. Implement IntelligenceOrchestrator integration
# Add pattern learning callbacks

# 2. Implement ObservabilityOrchestrator integration
# Add usage tracking callbacks

# 3. Add MCP server exposure
# Add cortex_query_features, cortex_feature_dependencies tools

# 4. Brain Tier 2 integration
# Auto-update knowledge graph

# 5. Comprehensive testing
pytest tests/orchestrators/feature_discovery/ --cov=src/orchestrators/feature_discovery

# 6. Commit
git add src/orchestrators/feature_discovery/
git commit -m "✅ Week 12: FeatureDiscoveryOrchestrator fully integrated"
```

---

## 📚 Related Documents

- **MASTER-PLAN.md** - Week 12 Intelligence + Observability integration point
- **CORTEX-4.0-DOCS-ORCHESTRATOR-REDESIGN.md** - Documentation orchestrator architecture
- **TDD-ORCHESTRATOR-REDESIGN.md** - TDD orchestrator architecture
- **THE-AWAKENING-OF-CORTEX.md** - Current story (manual, to be replaced)

---

## 🤝 Orchestrator Consumption Pattern

**How other orchestrators consume FeatureDiscoveryOrchestrator:**

```python
# Example: DocumentationOrchestrator

from src.orchestrators.feature_discovery import FeatureDiscoveryOrchestrator

class DocumentationOrchestrator(BaseOrchestrator):
    
    def __init__(self):
        super().__init__()
        self.feature_discovery = FeatureDiscoveryOrchestrator()
    
    def generate_documentation(self):
        """Generate documentation with live feature data"""
        
        # 1. Discover current features
        catalog = self.feature_discovery.discover_features(mode="incremental")
        
        # 2. Check if documentation needs update
        if self.documentation_outdated(catalog):
            
            # 3. Regenerate documentation
            self.generate_feature_catalog_page(catalog)
            self.update_d3_visualizations(catalog)
            
            # 4. Check story regeneration
            if self.feature_discovery.should_regenerate_story(catalog.changes):
                self.feature_discovery.regenerate_story(catalog.registry)
        
        # 5. Continue with other documentation tasks
        self.generate_architecture_diagrams()
        self.generate_api_reference()
```

---

## 🎉 Conclusion

The **FeatureDiscoveryOrchestrator** transforms CORTEX from a system with static documentation into a **self-aware, self-documenting intelligence** that maintains comprehensive knowledge of its own capabilities. By combining multi-source intelligence, differential detection, and story auto-generation, CORTEX achieves what no other AI system has: **a living origin story that stays accurate and hilarious as the system evolves**.

**The result:** Zero-maintenance documentation, continuous feature discovery, and the world's first self-updating AI narrative.

**Status:** Ready for Week 7 Day 6 implementation. 🚀

---

**Document Version:** 1.0  
**Author:** Asif Hussain  
**Approved:** December 19, 2025  
**Next Review:** Week 12 (Intelligence + Observability integration)
