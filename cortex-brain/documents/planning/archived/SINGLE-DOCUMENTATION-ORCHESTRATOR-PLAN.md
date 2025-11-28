# CORTEX Single Documentation Orchestrator - Comprehensive Plan

**Author:** Asif Hussain  
**Date:** 2025-11-19  
**Status:** 📋 PLANNING  
**Priority:** 🔴 CRITICAL

---

## 🎯 Executive Summary

**GOAL:** Create ONE SINGLE documentation orchestrator (`enterprise_documentation_orchestrator.py`) that generates ALL CORTEX documentation fresh on every run, discovering new functionality from Git history and current codebase state.

**Current State:** Multiple scattered documentation generators with duplicate folder structures  
**Target State:** Single entry point that generates:
- **10+ Prompts** (AI diagram generation prompts)
- **14+ Mermaid Diagrams** (architecture, flows, systems)
- **Multiple Narratives** (The CORTEX Story + technical narratives)
- **Executive Summary** (ALL CORTEX features discovered dynamically)
- **MkDocs Site** (comprehensive documentation website)

---

## 📊 Current Documentation Landscape Analysis

### ✅ Documentation Folders Found

```
ROOT: D:\PROJECTS\CORTEX

DOCUMENTATION FOLDERS:
├── .github\prompts\                    # CORTEX prompt templates
├── cortex-brain\admin\documentation\   # Admin documentation generators
├── cortex-brain\documents\             # Organized CORTEX brain documents
├── cortex-brain\templates\doc-templates\      # Jinja2 templates
├── cortex-brain\templates\documentation\      # Documentation templates
├── docs\                               # ✅ PRIMARY OUTPUT (MkDocs root)
│   ├── diagrams\
│   │   ├── mermaid\                    # 13 .mmd files (architecture diagrams)
│   │   ├── prompts\                    # AI image generation prompts
│   │   ├── narratives\                 # 1 file (technical explanations)
│   │   └── story\                      # THE-CORTEX-STORY.md
│   ├── narratives\                     # "The Intern with Amnesia" story
│   ├── EXECUTIVE-SUMMARY.md            # High-level overview
│   ├── FEATURES.md                     # Feature list
│   └── MODULES-REFERENCE.md            # Module documentation
├── prompts\                            # Legacy prompts folder
├── scripts\document_migration\         # Migration scripts
├── src\epmo\documentation\             # EPMO documentation generator
└── tests\docs\                         # Documentation tests
```

### 🔧 Documentation Generators Found

| Generator | Location | Purpose | Status |
|-----------|----------|---------|--------|
| **Enterprise Documentation Orchestrator** | `src/operations/enterprise_documentation_orchestrator.py` | Main orchestrator | ✅ Active |
| **EPMO Documentation Generator** | `src/operations/modules/epmo/documentation_generator.py` | Backend generator | ✅ Active |
| **Story Generator Plugin** | `src/plugins/story_generator_plugin.py` | "The CORTEX Story" | ✅ Active |
| **Narrative Intelligence** | `src/tier1/narrative_intelligence.py` | Narrative analysis | ✅ Active |
| **Diagrams Generator** | `cortex-brain/admin/documentation/generators/diagrams_generator.py` | Diagram generation | ✅ Active |
| **Narrative Generator** | `cortex-brain/admin/documentation/generators/narrative_generator.py` | Narrative text | ✅ Active |

### 📂 Output Targets (What Gets Generated)

#### 1. **Prompts Folder** (`docs/diagrams/prompts/`) - DALL-E Optimized
**Target:** 10+ AI image generation prompts designed for ChatGPT's DALL-E capabilities
**Current:** Unknown count (need to verify)
**Format:** Markdown files with sophisticated DALL-E prompts

**Design Philosophy:**
- **Leverage DALL-E's Strengths:** Architectural diagrams, system flows, conceptual illustrations
- **Sophisticated Visual Language:** Use terms like "isometric view", "blueprint style", "minimalist tech aesthetic"
- **Technical Accuracy:** Precise component placement, relationship arrows, color-coded systems
- **Narrative Parity:** Each prompt corresponds to a narrative that explains what the image shows

**Prompt Structure:**
```markdown
# Diagram Title: [Name]

## Visual Style
- Style: [Technical blueprint / Isometric / Flowchart / etc.]
- Color Palette: [CORTEX brand colors or technical theme]
- Complexity: [Simple/Moderate/Detailed]

## DALL-E Prompt
Create a [style] technical diagram showing [system/concept]. 
The diagram should include:
- [Component 1] positioned at [location]
- [Component 2] with [characteristics]
- Arrows showing [data flow/relationship]
- Labels for [key elements]

Style: Clean, professional, minimalist tech aesthetic with CORTEX branding.
Perspective: [Isometric/Top-down/Side view]
Colors: [Specific color scheme]

## Corresponding Narrative
File: docs/diagrams/narratives/[matching-narrative].md
Purpose: Explains what this diagram illustrates and why it matters
```

**Examples:**
- `01-tier-architecture-prompt.md` → DALL-E generates 4-tier brain system visualization
- `02-agent-coordination-prompt.md` → DALL-E generates left/right brain agent collaboration
- `03-information-flow-prompt.md` → DALL-E generates data flow between tiers
- `04-conversation-memory-prompt.md` → DALL-E generates FIFO queue visualization
- `05-pattern-learning-prompt.md` → DALL-E generates knowledge graph structure

#### 2. **Mermaid Diagrams** (`docs/diagrams/mermaid/`)
**Target:** 14+ Mermaid diagram files
**Current:** 13 files found
**Format:** `.mmd` files (Mermaid syntax)
**Examples:**
- `01-tier-architecture.mmd`
- `02-agent-coordination-system.mmd`
- `03-information-flow.mmd`
- `04-vision-api-integration.mmd`
- `05-cortex-one-pager.mmd`
- (and 8 more...)

#### 3. **Narratives** - High-Level Image Explanations
**Target:** 14+ narrative documents (one per diagram/prompt pair)
**Current:** 
- `docs/narratives/THE-CORTEX-STORY.md` (main story)
- `docs/narratives/the-intern-with-amnesia/` (chapter-based story)
- `docs/diagrams/narratives/01-tier-architecture-enhanced.md`

**Design Philosophy - Narrative-to-Prompt Parity:**
- **One-to-One Mapping:** Each DALL-E prompt has corresponding narrative
- **High-Level Explanations:** Narratives explain WHAT the image shows, not implementation details
- **Educational Focus:** Help readers understand the concept the image illustrates
- **Reference Architecture:** Link to technical docs for deep dives

**Narrative Structure:**
```markdown
# [Diagram Title] - Explained

## What This Diagram Shows
[High-level overview of the visual concept]

## Key Components
- **Component 1:** [What it represents and its role]
- **Component 2:** [What it represents and its role]
- **Relationships:** [How components interact]

## Why This Matters
[Real-world significance and use cases]

## Visual Guide
- **Color Coding:** [What each color represents]
- **Arrows:** [What different arrow types mean]
- **Layout:** [Why components are positioned this way]

## Related Concepts
[Links to technical documentation for deeper understanding]

---
**Corresponding Image Prompt:** docs/diagrams/prompts/[matching-prompt].md
**Generated Image:** [Will be created by DALL-E from prompt]
```

**Examples:**
- `01-tier-architecture-narrative.md` → Explains 4-tier brain visualization (what each tier does)
- `02-agent-coordination-narrative.md` → Explains how left/right brain agents work together
- `03-information-flow-narrative.md` → Explains how data moves through CORTEX

**What's Needed:**
- The Awakening of CORTEX (hilarious technical story of Asif "Codenstein" and Copilot with wife woven in)
- 14+ technical narratives explaining each diagram (high-level, educational)
- User journey narratives (how users interact with CORTEX)

#### 4. **Executive Summary** (`docs/EXECUTIVE-SUMMARY.md`)
**Target:** Comprehensive list of ALL CORTEX features
**Current:** Exists but needs dynamic generation
**Should Include:**
- All capabilities from `cortex-brain/capabilities.yaml`
- All operations from `cortex-operations.yaml`
- All modules from `module-definitions.yaml`
- Git history analysis (features added in last 2 days)
- Feature completion status

#### 5. **Feature Documentation**
**Files:**
- `FEATURES.md` - User-facing features
- `MODULES-REFERENCE.md` - Technical modules
- `CAPABILITIES-MATRIX.md` - Feature matrix
- `OPERATIONS-REFERENCE.md` - Operations guide

---

## 🎯 Git History Analysis (Last 2 Days)

Based on Git log analysis, recent work includes:

### Recent Documentation Work (Last 2 Days)
1. ✅ **Streamlined documentation with direct import** (commit: 8933088)
2. ✅ **EPM cleanup remnants** (commit: 8933088)
3. ✅ **MkDocs restoration and story generator enhancements** (commit: bd1bf7b)
4. ✅ **Story generator with token optimization, DoD/DoR, semantic commits** (commit: b7dea7f)
5. ✅ **Enterprise documentation system with Mermaid diagrams** (commit: 9c69bdf)
6. ✅ **Documentation consolidation and admin structure migration** (commit: 50b29d8)

### Key Functionality Added Recently
- **Token optimization** (97.2% input token reduction)
- **DoD/DoR framework** (Definition of Done/Ready)
- **Semantic commit system**
- **Performance metrics**
- **Material Design 3 token system** (MD3 tokens)
- **Direct file import mode** to conversation capture
- **Automatic .gitignore configuration**
- **Brain protection caching**

---

## 🚀 The Plan: Single Documentation Orchestrator

### Phase 0: Cleanup Operations 🗑️ (FIRST - Start Clean)

**Goal:** Remove all wrong folder structures and duplicate files BEFORE building new orchestrator

**Rationale:** Starting with a clean slate ensures:
- No conflicts with old structure
- Clear understanding of what exists
- No accidentally referencing deprecated files
- Fresh mental model for implementation

#### Cleanup Script

```powershell
# Cleanup Script for CORTEX Documentation Consolidation

$ErrorActionPreference = "Stop"

Write-Host "🧹 CORTEX Documentation Cleanup - Phase 0" -ForegroundColor Cyan
Write-Host "========================================="" -ForegroundColor Cyan
Write-Host ""

# 1. Delete duplicate prompts folder
Write-Host "1. Deleting duplicate prompts folder..." -ForegroundColor Yellow
if (Test-Path "d:\PROJECTS\CORTEX\prompts") {
    Remove-Item -Path "d:\PROJECTS\CORTEX\prompts" -Recurse -Force
    Write-Host "   ✅ Deleted: prompts\" -ForegroundColor Green
}

# 2. Delete document_migration scripts (migration complete)
Write-Host "2. Deleting migration scripts..." -ForegroundColor Yellow
if (Test-Path "d:\PROJECTS\CORTEX\scripts\document_migration") {
    Remove-Item -Path "d:\PROJECTS\CORTEX\scripts\document_migration" -Recurse -Force
    Write-Host "   ✅ Deleted: scripts\document_migration\" -ForegroundColor Green
}

# 3. Consolidate story folders
Write-Host "3. Consolidating story folders..." -ForegroundColor Yellow
if (Test-Path "d:\PROJECTS\CORTEX\docs\diagrams\story") {
    # Move content to docs\narratives\
    $storyFiles = Get-ChildItem -Path "d:\PROJECTS\CORTEX\docs\diagrams\story" -File
    foreach ($file in $storyFiles) {
        Move-Item -Path $file.FullName -Destination "d:\PROJECTS\CORTEX\docs\narratives\" -Force
    }
    Remove-Item -Path "d:\PROJECTS\CORTEX\docs\diagrams\story" -Recurse -Force
    Write-Host "   ✅ Consolidated: docs\diagrams\story\ → docs\narratives\" -ForegroundColor Green
}

# 4. Merge template folders
Write-Host "4. Merging template folders..." -ForegroundColor Yellow
if (Test-Path "d:\PROJECTS\CORTEX\cortex-brain\templates\doc-templates") {
    $docTemplates = Get-ChildItem -Path "d:\PROJECTS\CORTEX\cortex-brain\templates\doc-templates" -File
    foreach ($file in $docTemplates) {
        Copy-Item -Path $file.FullName -Destination "d:\PROJECTS\CORTEX\cortex-brain\templates\documentation\" -Force
    }
    Remove-Item -Path "d:\PROJECTS\CORTEX\cortex-brain\templates\doc-templates" -Recurse -Force
    Write-Host "   ✅ Merged: templates\doc-templates\ → templates\documentation\" -ForegroundColor Green
}

# 5. Delete all previous MkDocs folder structures (NEW)
Write-Host "5. Deleting previous MkDocs structures..." -ForegroundColor Yellow

# Search for any existing MkDocs-related folders
$mkdocsFolders = @(
    "d:\PROJECTS\CORTEX\mkdocs",
    "d:\PROJECTS\CORTEX\docs\site",
    "d:\PROJECTS\CORTEX\docs\mkdocs",
    "d:\PROJECTS\CORTEX\site"
)

$deletedCount = 0
foreach ($folder in $mkdocsFolders) {
    if (Test-Path $folder) {
        Remove-Item -Path $folder -Recurse -Force
        Write-Host "   ✅ Deleted: $($folder.Replace('d:\PROJECTS\CORTEX\', ''))" -ForegroundColor Green
        $deletedCount++
    }
}

# Search recursively for any mkdocs.yml files outside docs/diagrams/
$mkdocsConfigs = Get-ChildItem -Path "d:\PROJECTS\CORTEX" -Filter "mkdocs.yml" -Recurse -ErrorAction SilentlyContinue |
    Where-Object { $_.FullName -notlike "*\docs\diagrams\*" }

foreach ($config in $mkdocsConfigs) {
    Remove-Item -Path $config.FullName -Force
    Write-Host "   ✅ Deleted orphan: $($config.FullName.Replace('d:\PROJECTS\CORTEX\', ''))" -ForegroundColor Green
    $deletedCount++
}

if ($deletedCount -eq 0) {
    Write-Host "   ℹ️ No previous MkDocs structures found (clean slate)" -ForegroundColor Cyan
}

# 6. Verify tests\docs\ is still needed
Write-Host "6. Checking tests\docs\ folder..." -ForegroundColor Yellow
if (Test-Path "d:\PROJECTS\CORTEX\tests\docs") {
    $testFiles = Get-ChildItem -Path "d:\PROJECTS\CORTEX\tests\docs" -File -Recurse
    if ($testFiles.Count -eq 0) {
        Remove-Item -Path "d:\PROJECTS\CORTEX\tests\docs" -Recurse -Force
        Write-Host "   ✅ Deleted: tests\docs\ (empty)" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️ Keeping: tests\docs\ (has $($testFiles.Count) files)" -ForegroundColor Yellow
    }
}

Write-Host ""
Write-Host "🎉 Cleanup Complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "1. Proceed to Phase 1 (Design Consolidation)" -ForegroundColor White
Write-Host "2. Implement consolidated orchestrator in Phase 2" -ForegroundColor White
```

---

## 📋 Generated Files Inventory

**Total Files:** 40+ files across 5 categories

### Table: Complete Output Structure

| # | File Path | Type | Category | Description |
|---|-----------|------|----------|-------------|
| **DALL-E PROMPTS (10+ files)** |
| 1 | `docs/diagrams/prompts/01-tier-architecture-prompt.md` | Prompt | Architecture | DALL-E prompt for 4-tier brain system visualization |
| 2 | `docs/diagrams/prompts/02-agent-coordination-prompt.md` | Prompt | Agents | DALL-E prompt for left/right brain agent collaboration |
| 3 | `docs/diagrams/prompts/03-information-flow-prompt.md` | Prompt | Data Flow | DALL-E prompt for tier-to-tier data flow |
| 4 | `docs/diagrams/prompts/04-conversation-memory-prompt.md` | Prompt | Memory | DALL-E prompt for FIFO queue visualization |
| 5 | `docs/diagrams/prompts/05-pattern-learning-prompt.md` | Prompt | Learning | DALL-E prompt for knowledge graph structure |
| 6 | `docs/diagrams/prompts/06-brain-protection-prompt.md` | Prompt | Security | DALL-E prompt for 6-layer protection system |
| 7 | `docs/diagrams/prompts/07-tdd-workflow-prompt.md` | Prompt | Development | DALL-E prompt for RED-GREEN-REFACTOR cycle |
| 8 | `docs/diagrams/prompts/08-user-journey-prompt.md` | Prompt | UX | DALL-E prompt for user interaction flow |
| 9 | `docs/diagrams/prompts/09-context-intelligence-prompt.md` | Prompt | Analytics | DALL-E prompt for git analysis/metrics |
| 10 | `docs/diagrams/prompts/10-corpus-callosum-prompt.md` | Prompt | Communication | DALL-E prompt for hemisphere coordination |
| **MERMAID DIAGRAMS (14 files)** |
| 11 | `docs/diagrams/mermaid/01-tier-architecture.mmd` | Mermaid | Architecture | 4-tier system flowchart |
| 12 | `docs/diagrams/mermaid/02-agent-coordination.mmd` | Mermaid | Agents | Agent communication sequence |
| 13 | `docs/diagrams/mermaid/03-information-flow.mmd` | Mermaid | Data Flow | Data movement flowchart |
| 14 | `docs/diagrams/mermaid/04-conversation-memory.mmd` | Mermaid | Memory | FIFO queue diagram |
| 15 | `docs/diagrams/mermaid/05-pattern-learning.mmd` | Mermaid | Learning | Knowledge graph structure |
| 16 | `docs/diagrams/mermaid/06-brain-protection.mmd` | Mermaid | Security | Protection layers diagram |
| 17 | `docs/diagrams/mermaid/07-tdd-workflow.mmd` | Mermaid | Development | TDD cycle flowchart |
| 18 | `docs/diagrams/mermaid/08-user-journey.mmd` | Mermaid | UX | User journey map |
| 19 | `docs/diagrams/mermaid/09-context-intelligence.mmd` | Mermaid | Analytics | Context analysis flow |
| 20 | `docs/diagrams/mermaid/10-corpus-callosum.mmd` | Mermaid | Communication | Message queue diagram |
| 21 | `docs/diagrams/mermaid/11-plugin-system.mmd` | Mermaid | Extensibility | Plugin architecture |
| 22 | `docs/diagrams/mermaid/12-intent-routing.mmd` | Mermaid | Routing | Intent detection flow |
| 23 | `docs/diagrams/mermaid/13-file-relationships.mmd` | Mermaid | Codebase | File dependency graph |
| 24 | `docs/diagrams/mermaid/14-deployment-architecture.mmd` | Mermaid | Deployment | System deployment diagram |
| **NARRATIVES (14+ files)** |
| 25 | `docs/narratives/01-tier-architecture-narrative.md` | Narrative | Architecture | Explains 4-tier brain (what each tier does) |
| 26 | `docs/narratives/02-agent-coordination-narrative.md` | Narrative | Agents | Explains how agents work together |
| 27 | `docs/narratives/03-information-flow-narrative.md` | Narrative | Data Flow | Explains data movement through CORTEX |
| 28 | `docs/narratives/04-conversation-memory-narrative.md` | Narrative | Memory | Explains FIFO queue and context |
| 29 | `docs/narratives/05-pattern-learning-narrative.md` | Narrative | Learning | Explains knowledge graph learning |
| 30 | `docs/narratives/06-brain-protection-narrative.md` | Narrative | Security | Explains 6 protection layers |
| 31 | `docs/narratives/07-tdd-workflow-narrative.md` | Narrative | Development | Explains RED-GREEN-REFACTOR |
| 32 | `docs/narratives/08-user-journey-narrative.md` | Narrative | UX | Explains user interaction patterns |
| 33 | `docs/narratives/09-context-intelligence-narrative.md` | Narrative | Analytics | Explains git analysis/metrics |
| 34 | `docs/narratives/10-corpus-callosum-narrative.md` | Narrative | Communication | Explains hemisphere coordination |
| 35 | `docs/narratives/11-plugin-system-narrative.md` | Narrative | Extensibility | Explains plugin architecture |
| 36 | `docs/narratives/12-intent-routing-narrative.md` | Narrative | Routing | Explains intent detection |
| 37 | `docs/narratives/13-file-relationships-narrative.md` | Narrative | Codebase | Explains dependency tracking |
| 38 | `docs/narratives/14-deployment-architecture-narrative.md` | Narrative | Deployment | Explains deployment patterns |
| **STORY FILES (2 files)** |
| 39 | `docs/narratives/THE-CORTEX-STORY.md` | Story | Main Story | "The Awakening of CORTEX" - Asif "Codenstein" origin story |
| 40 | `docs/narratives/the-intern-with-amnesia/chapter-01.md` | Story | Chapter | First chapter: The brilliant amnesiac intern |
| **EXECUTIVE & FEATURES (2 files)** |
| 41 | `docs/EXECUTIVE-SUMMARY.md` | Summary | Executive | High-level overview with ALL capabilities |
| 42 | `docs/FEATURES.md` | Documentation | Features | Complete feature list from capabilities.yaml |
| **MKDOCS SITE (3+ files)** |
| 43 | `docs/diagrams/mkdocs.yml` | Config | MkDocs | MkDocs configuration (generated) |
| 44 | `docs/index.md` | Markdown | Home | Site home page with quick links |
| 45 | `docs/diagrams/site/` | Directory | Static Site | Built MkDocs static site (HTML, CSS, JS, search index) |

### File Type Summary

| Type | Count | Purpose |
|------|-------|---------|
| **DALL-E Prompts** | 10+ | Image generation for sophisticated diagrams |
| **Mermaid Diagrams** | 14 | Technical architecture visualizations |
| **Narratives** | 14+ | High-level explanations of diagrams/images |
| **Story Files** | 2+ | "The Awakening" story with chapters |
| **Executive Docs** | 2 | Summary + feature documentation |
| **MkDocs Site** | 1 config + 1 index + 1 site output | Complete static documentation website |
| **TOTAL** | **45+** | Complete documentation suite + deployable website |

### Validation Checklist

After orchestrator runs, verify:
- [ ] All 10+ DALL-E prompts generated (sophisticated, detailed)
- [ ] All 14 Mermaid diagrams created (valid .mmd syntax)
- [ ] All 14+ narratives written (high-level, educational)
- [ ] 1:1 parity: Each prompt has matching narrative
- [ ] Story files complete (main story + chapters)
- [ ] Executive summary includes ALL capabilities
- [ ] FEATURES.md matches capabilities.yaml
- [ ] No broken links between files
- [ ] **MkDocs site builds successfully** ✨
- [ ] **MkDocs config generated (mkdocs.yml)** ✨
- [ ] **Site index page created** ✨
- [ ] **Navigation structure complete** ✨
- [ ] **Search functionality works** ✨
- [ ] **Dark mode toggle works** ✨
- [ ] **Mermaid diagrams render in site** ✨

---

### Phase 1: Design Consolidation ✅ (Current Phase)

**Goal:** Create comprehensive design document for single orchestrator

**Design Principles:**
1. **Single Entry Point:** `enterprise_documentation_orchestrator.py` is THE orchestrator
2. **Fresh Every Time:** Regenerate ALL docs from source (no stale content)
3. **Discovery-Based:** Scan Git history, capabilities.yaml, module-definitions.yaml, operations.yaml
4. **Component-Based:** Modular generators that orchestrator calls
5. **Validation:** Post-generation validation to ensure quality

**Architecture:**
```
enterprise_documentation_orchestrator.py (MAIN)
    ↓
    ├─→ Discovery Engine (scans Git, YAML configs, codebase)
    │   ├─ Git History Analyzer (last N days)
    │   ├─ Capabilities Scanner (capabilities.yaml)
    │   ├─ Operations Scanner (cortex-operations.yaml)
    │   ├─ Module Scanner (module-definitions.yaml)
    │   └─ Codebase Feature Detector
    ↓
    ├─→ Generation Pipeline
    │   ├─ Diagrams Generator (14+ Mermaid + prompts)
    │   ├─ Narrative Generator (stories + technical)
    │   ├─ Executive Summary Generator (ALL features)
    │   ├─ Features Documentation Generator
    │   ├─ MkDocs Site Builder
    │   └─ Story Generator (The Awakening of CORTEX)
    ↓
    └─→ Validation & Report
        ├─ File Count Validation
        ├─ Content Quality Check
        ├─ Link Validation
        └─ Generation Report
```

---

### Phase 2: Identify Wrong/Duplicate Structures 🔍

**Goal:** Map all incorrect folder structures and duplicate files for deletion

**Note:** This was Phase 2 originally. After Phase 0 cleanup, this becomes verification phase.

#### ❌ Wrong Folder Structures to Delete

```
D:\PROJECTS\CORTEX\

DUPLICATES TO DELETE:
├── prompts\                           # ❌ DELETE (use .github\prompts\)
├── scripts\document_migration\        # ❌ DELETE (migration complete)
├── docs\diagrams\story\               # ❌ CONSOLIDATE to docs\narratives\
├── cortex-brain\templates\doc-templates\  # ❌ MERGE to cortex-brain\templates\documentation\

MKDOCS CLEANUP (NEW):
├── mkdocs\                            # ❌ DELETE any old mkdocs folders
├── site\                              # ❌ DELETE any old site output folders
├── docs\site\                         # ❌ DELETE any old site in docs
├── docs\mkdocs\                       # ❌ DELETE any old mkdocs in docs
└── **/mkdocs.yml                      # ❌ DELETE orphan configs (keep only docs/diagrams/mkdocs.yml)

WRONG LOCATIONS TO MOVE:
├── src\epmo\documentation\            # ❌ MOVE to src\operations\modules\epmo\
└── tests\docs\                        # ❌ VERIFY if still needed

ARCHIVES TO CLEAN:
└── cortex-brain\archives\             # ✅ KEEP but verify nothing needed
```

#### 🔍 Recursive Search Strategy

**Step 1:** Find all documentation-related folders
```powershell
Get-ChildItem -Path "d:\PROJECTS\CORTEX" -Directory -Recurse | 
Where-Object { 
    $_.Name -match "doc|prompt|narrative|mermaid|story|diagram" -and 
    $_.FullName -notlike "*node_modules*" -and 
    $_.FullName -notlike "*\.venv*" -and 
    $_.FullName -notlike "*__pycache__*" -and 
    $_.FullName -notlike "*publish*"
} | Select-Object FullName
```

**Step 2:** Find all orphaned documentation files
```powershell
Get-ChildItem -Path "d:\PROJECTS\CORTEX" -File -Recurse | 
Where-Object { 
    ($_.Extension -eq ".md" -or $_.Extension -eq ".mmd") -and 
    $_.Name -match "story|narrative|diagram|prompt" -and
    $_.FullName -notlike "*cortex-brain\documents*" -and
    $_.FullName -notlike "*docs\*"
}
```

**Step 3:** Identify duplicate generators
```python
# Search for classes named *Generator or *Orchestrator related to docs
grep -r "class.*Generator.*:.*doc" src/
grep -r "class.*Orchestrator.*:.*doc" src/
```

---

### Phase 3: Implement Consolidated Orchestrator 🛠️

**Goal:** Enhance `enterprise_documentation_orchestrator.py` to be THE single entry point

**Note:** This was Phase 3 originally, now Phase 3 after Phase 0 cleanup.

#### 3.1 Discovery Engine Implementation

```python
class DocumentationDiscoveryEngine:
    """Discovers all CORTEX features dynamically"""
    
    def discover_features(self, since_days: int = 2) -> Dict[str, Any]:
        """
        Discover all CORTEX features from multiple sources
        
        Returns:
            {
                "git_features": [...],  # From Git history
                "capabilities": [...],  # From capabilities.yaml
                "operations": [...],    # From operations.yaml
                "modules": [...],       # From module-definitions.yaml
                "undocumented": [...]   # Code analysis
            }
        """
        return {
            "git_features": self._scan_git_history(since_days),
            "capabilities": self._scan_capabilities_yaml(),
            "operations": self._scan_operations_yaml(),
            "modules": self._scan_modules_yaml(),
            "undocumented": self._detect_undocumented_features()
        }
    
    def _scan_git_history(self, days: int) -> List[Dict]:
        """Analyze Git commits from last N days"""
        # Parse git log --since="{days} days ago" --oneline
        # Extract feature additions, major changes
        pass
    
    def _scan_capabilities_yaml(self) -> List[Dict]:
        """Load and parse capabilities.yaml"""
        pass
    
    def _scan_operations_yaml(self) -> List[Dict]:
        """Load and parse cortex-operations.yaml"""
        pass
    
    def _scan_modules_yaml(self) -> List[Dict]:
        """Load and parse module-definitions.yaml"""
        pass
    
    def _detect_undocumented_features(self) -> List[Dict]:
        """Scan codebase for features not in YAML"""
        # Search for @operation decorators
        # Search for class definitions
        # Search for natural language patterns
        pass
```

#### 3.2 Generation Pipeline Enhancement

```python
class ConsolidatedDocumentationPipeline:
    """Single pipeline for ALL documentation generation"""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.brain_path = workspace_root / "cortex-brain"
        self.docs_path = workspace_root / "docs"
        
        # Initialize component generators
        self.diagrams_gen = DiagramsGenerator(...)
        self.narrative_gen = NarrativeGenerator(...)
        self.executive_gen = ExecutiveSummaryGenerator(...)
        self.story_gen = StoryGenerator(...)
        self.mkdocs_gen = MkDocsBuilder(...)
    
    def generate_all(self, discovered_features: Dict) -> GenerationReport:
        """Generate ALL documentation"""
        
        results = {}
        
        # 1. Generate 14+ Mermaid diagrams
        results['diagrams'] = self._generate_diagrams(discovered_features)
        
        # 2. Generate 10+ AI prompts
        results['prompts'] = self._generate_prompts(discovered_features)
        
        # 3. Generate narratives
        results['narratives'] = self._generate_narratives(discovered_features)
        
        # 4. Generate "The Awakening of CORTEX" story
        results['story'] = self._generate_story(discovered_features)
        
        # 5. Generate Executive Summary with ALL features
        results['executive'] = self._generate_executive_summary(discovered_features)
        
        # 6. Generate feature documentation
        results['features'] = self._generate_feature_docs(discovered_features)
        
        # 7. Build MkDocs site (co-located with source docs)
        results['mkdocs'] = self._build_mkdocs_site(discovered_features)
        
        return GenerationReport(results)
    
    def _generate_diagrams(self, features: Dict) -> Dict:
        """Generate all Mermaid diagrams and prompts"""
        diagrams = []
        
        # Core architecture diagrams (always generated)
        diagrams.extend([
            self._create_tier_architecture_diagram(),
            self._create_agent_coordination_diagram(),
            self._create_information_flow_diagram(),
            # ... 11 more standard diagrams
        ])
        
        # Feature-specific diagrams (from discovered features)
        for feature in features.get('capabilities', []):
            if feature.get('needs_diagram'):
                diagrams.append(self._create_feature_diagram(feature))
        
        # Save to docs/diagrams/mermaid/
        self._save_diagrams(diagrams)
        
        # Generate corresponding AI prompts
        prompts = [self._create_ai_prompt(d) for d in diagrams]
        self._save_prompts(prompts)  # docs/diagrams/prompts/
        
        return {
            "diagrams_count": len(diagrams),
            "prompts_count": len(prompts),
            "files": [d.filename for d in diagrams]
        }
    
    def _generate_narratives(self, features: Dict) -> Dict:
        """Generate narrative documentation"""
        narratives = []
        
        # Technical narratives (one per diagram)
        for diagram in self._get_diagrams():
            narrative = self._create_technical_narrative(diagram, features)
            narratives.append(narrative)
        
        # Save to docs/diagrams/narratives/
        self._save_narratives(narratives)
        
        return {"count": len(narratives)}
    
    def _generate_story(self, features: Dict) -> Dict:
        """Generate 'The Awakening of CORTEX' story"""
        
        # The hilarious technical story
        story_chapters = [
            self._write_chapter_1_amnesia_problem(),
            self._write_chapter_2_asif_codenstein_appears(),
            self._write_chapter_3_copilot_awakening(),
            self._write_chapter_4_wife_weaved_in(),
            self._write_chapter_5_tier_implementation(),
            self._write_chapter_6_agent_coordination(),
            self._write_chapter_7_real_world_scenarios(),
            self._write_chapter_8_transformation_complete(),
        ]
        
        story_md = self._combine_chapters(story_chapters)
        
        # Save to docs/narratives/THE-AWAKENING-OF-CORTEX.md
        output_path = self.docs_path / "narratives" / "THE-AWAKENING-OF-CORTEX.md"
        output_path.write_text(story_md, encoding='utf-8')
        
        return {
            "chapters": len(story_chapters),
            "file": str(output_path)
        }
    
    def _generate_executive_summary(self, features: Dict) -> Dict:
        """Generate comprehensive executive summary with ALL features"""
        
        # Aggregate all features
        all_features = []
        all_features.extend(features.get('capabilities', []))
        all_features.extend(features.get('operations', []))
        all_features.extend(features.get('modules', []))
        all_features.extend(features.get('git_features', []))
        
        # Deduplicate and categorize
        categorized = self._categorize_features(all_features)
        
        # Generate summary markdown
        summary_md = self._format_executive_summary(categorized)
        
        # Save to docs/EXECUTIVE-SUMMARY.md
        output_path = self.docs_path / "EXECUTIVE-SUMMARY.md"
        output_path.write_text(summary_md, encoding='utf-8')
        
        return {
            "total_features": len(all_features),
            "categories": len(categorized),
            "file": str(output_path)
        }
```

#### 3.4 MkDocs Site Builder Implementation

**"Co-located with source documentation for organizational clarity"**

```python
class MkDocsBuilder:
    """Generates complete MkDocs static documentation site"""
    
    def __init__(self, docs_root: Path):
        self.docs_root = docs_root
        self.site_root = docs_root / "diagrams"  # Co-locate with source
        self.site_output = self.site_root / "site"
        self.mkdocs_config = self.site_root / "mkdocs.yml"
    
    def build_site(self, discovered_features: Dict, generated_files: Dict) -> Dict:
        """
        Generate complete MkDocs site from documentation
        
        Args:
            discovered_features: All features discovered by Discovery Engine
            generated_files: All files generated by pipeline
        
        Returns:
            Build report with site location and metrics
        """
        
        # Step 1: Generate mkdocs.yml configuration
        config = self._generate_mkdocs_config(discovered_features, generated_files)
        self._save_config(config)
        
        # Step 2: Organize documentation structure for MkDocs
        self._organize_docs_for_mkdocs(generated_files)
        
        # Step 3: Generate navigation structure
        nav_structure = self._generate_navigation(discovered_features)
        
        # Step 4: Create index page
        self._create_index_page(discovered_features)
        
        # Step 5: Build site using mkdocs
        build_result = self._execute_mkdocs_build()
        
        # Step 6: Validate build
        validation = self._validate_site()
        
        return {
            "config_file": str(self.mkdocs_config),
            "site_output": str(self.site_output),
            "pages_generated": validation.get('page_count', 0),
            "build_time": build_result.get('duration_seconds', 0),
            "build_status": build_result.get('status', 'unknown'),
            "site_size_mb": validation.get('size_mb', 0),
            "validation": validation
        }
    
    def _generate_mkdocs_config(self, features: Dict, files: Dict) -> Dict:
        """Generate mkdocs.yml configuration"""
        
        config = {
            "site_name": "CORTEX - Documentation & Architecture",
            "site_description": "Comprehensive documentation for CORTEX memory system",
            "site_author": "Asif Hussain",
            "site_url": "https://asifhussain60.github.io/CORTEX",  # GitHub Pages
            
            "repo_name": "asifhussain60/CORTEX",
            "repo_url": "https://github.com/asifhussain60/CORTEX",
            "edit_uri": "edit/CORTEX-3.0/docs/",
            
            "theme": {
                "name": "material",
                "language": "en",
                "palette": [
                    {
                        "media": "(prefers-color-scheme: light)",
                        "scheme": "default",
                        "primary": "indigo",
                        "accent": "indigo",
                        "toggle": {
                            "icon": "material/brightness-7",
                            "name": "Switch to dark mode"
                        }
                    },
                    {
                        "media": "(prefers-color-scheme: dark)",
                        "scheme": "slate",
                        "primary": "indigo",
                        "accent": "indigo",
                        "toggle": {
                            "icon": "material/brightness-4",
                            "name": "Switch to light mode"
                        }
                    }
                ],
                "font": {
                    "text": "Roboto",
                    "code": "Roboto Mono"
                },
                "features": [
                    "navigation.instant",       # Instant loading
                    "navigation.tracking",      # URL tracking
                    "navigation.tabs",          # Top-level tabs
                    "navigation.sections",      # Section navigation
                    "navigation.expand",        # Expand navigation
                    "navigation.top",           # Back to top button
                    "search.suggest",           # Search suggestions
                    "search.highlight",         # Highlight search terms
                    "search.share",             # Share search results
                    "toc.follow",              # TOC follows scroll
                    "toc.integrate",           # Integrate TOC
                    "content.code.copy",       # Copy code button
                    "content.tabs.link",       # Link content tabs
                ]
            },
            
            "plugins": [
                "search",                       # Search functionality
                {
                    "mermaid2": {              # Mermaid diagram support
                        "version": "10.6.1"
                    }
                }
            ],
            
            "markdown_extensions": [
                "pymdownx.highlight",           # Code highlighting
                "pymdownx.superfences",         # Enhanced fences
                "pymdownx.tabbed",             # Tabbed content
                "pymdownx.details",            # Collapsible sections
                "pymdownx.emoji",              # Emoji support
                "pymdownx.tasklist",           # Task lists
                "toc",                         # Table of contents
                "tables",                      # Tables support
                "admonition",                  # Admonitions (callouts)
                {
                    "pymdownx.superfences": {
                        "custom_fences": [
                            {
                                "name": "mermaid",
                                "class": "mermaid",
                                "format": "!!python/name:mermaid2.fence_mermaid"
                            }
                        ]
                    }
                }
            ],
            
            "extra": {
                "social": [
                    {
                        "icon": "fontawesome/brands/github",
                        "link": "https://github.com/asifhussain60/CORTEX"
                    }
                ],
                "version": {
                    "provider": "mike",
                    "default": "latest"
                }
            },
            
            "nav": self._build_navigation_structure(features, files)
        }
        
        return config
    
    def _build_navigation_structure(self, features: Dict, files: Dict) -> List:
        """Build hierarchical navigation from generated files"""
        
        nav = [
            {
                "Home": "index.md"
            },
            {
                "Overview": [
                    "EXECUTIVE-SUMMARY.md",
                    "FEATURES.md",
                    "CAPABILITIES-MATRIX.md"
                ]
            },
            {
                "Architecture": [
                    {
                        "Diagrams": self._get_diagram_nav_items("mermaid")
                    },
                    {
                        "Visual Prompts": self._get_diagram_nav_items("prompts")
                    }
                ]
            },
            {
                "Narratives": [
                    {
                        "Technical Narratives": self._get_narrative_nav_items("technical")
                    },
                    {
                        "The CORTEX Story": self._get_narrative_nav_items("story")
                    }
                ]
            },
            {
                "Technical Reference": [
                    "MODULES-REFERENCE.md",
                    "OPERATIONS-REFERENCE.md",
                    "API-REFERENCE.md"
                ]
            }
        ]
        
        return nav
    
    def _get_diagram_nav_items(self, diagram_type: str) -> List[str]:
        """Get navigation items for diagrams"""
        diagrams_path = self.site_root / diagram_type
        
        if not diagrams_path.exists():
            return []
        
        # Get all diagram files
        if diagram_type == "mermaid":
            pattern = "*.mmd"
        elif diagram_type == "prompts":
            pattern = "*-prompt.md"
        else:
            pattern = "*.md"
        
        files = sorted(diagrams_path.glob(pattern))
        
        # Create navigation items
        nav_items = []
        for file in files:
            # Extract title from filename (e.g., 01-tier-architecture → Tier Architecture)
            title = self._format_nav_title(file.stem)
            relative_path = f"diagrams/{diagram_type}/{file.name}"
            nav_items.append({title: relative_path})
        
        return nav_items
    
    def _get_narrative_nav_items(self, narrative_type: str) -> List[str]:
        """Get navigation items for narratives"""
        if narrative_type == "technical":
            narratives_path = self.site_root / "narratives"
            pattern = "*-narrative.md"
        else:  # story
            narratives_path = self.docs_root / "narratives"
            pattern = "THE-*.md"
        
        if not narratives_path.exists():
            return []
        
        files = sorted(narratives_path.glob(pattern))
        
        nav_items = []
        for file in files:
            title = self._format_nav_title(file.stem)
            
            if narrative_type == "technical":
                relative_path = f"diagrams/narratives/{file.name}"
            else:
                relative_path = f"narratives/{file.name}"
            
            nav_items.append({title: relative_path})
        
        return nav_items
    
    def _format_nav_title(self, filename_stem: str) -> str:
        """Format filename into readable navigation title"""
        # Remove number prefix (01-, 02-, etc.)
        title = re.sub(r'^\d+-', '', filename_stem)
        
        # Remove suffixes
        title = title.replace('-narrative', '').replace('-prompt', '')
        
        # Replace hyphens with spaces and title case
        title = title.replace('-', ' ').title()
        
        return title
    
    def _organize_docs_for_mkdocs(self, generated_files: Dict):
        """Ensure all documentation is properly organized for MkDocs"""
        
        # MkDocs expects docs to be in specific structure
        # Our current structure: docs/diagrams/{mermaid,prompts,narratives}
        # This is already MkDocs-compatible, but we need to verify
        
        # Create docs_src symlinks or copy if needed
        # (MkDocs reads from docs/ by default)
        pass
    
    def _create_index_page(self, features: Dict):
        """Generate the index.md home page"""
        
        index_content = f"""# Welcome to CORTEX Documentation

## 🧠 The Memory System for GitHub Copilot

CORTEX transforms GitHub Copilot from a brilliant but forgetful assistant into an experienced team member with comprehensive memory and context awareness.

### What is CORTEX?

CORTEX is a **four-tier cognitive architecture** that gives GitHub Copilot:
- **Working Memory** (Tier 1): Remember your last 20 conversations
- **Long-Term Memory** (Tier 2): Learn patterns from past work
- **Context Intelligence** (Tier 3): Understand your project holistically
- **Core Principles** (Tier 0): Immutable rules protecting system integrity

### Quick Links

- [Executive Summary](EXECUTIVE-SUMMARY.md) - Complete overview of all capabilities
- [Features List](FEATURES.md) - User-facing features and operations
- [Architecture Diagrams](diagrams/mermaid/) - Technical visualizations
- [The CORTEX Story](narratives/THE-AWAKENING-OF-CORTEX.md) - The origin story

### Recently Discovered Features

{self._format_recent_features(features.get('git_features', []))}

### Documentation Categories

#### 📊 Architecture & Diagrams
Explore visual representations of CORTEX's architecture, data flows, and system components.

[Browse Architecture Diagrams →](diagrams/mermaid/)

#### 📖 Narratives & Stories
Read high-level explanations and the entertaining origin story of CORTEX.

[Read Narratives →](narratives/)

#### 🔧 Technical Reference
Deep dive into modules, operations, and API documentation.

[View Technical Docs →](MODULES-REFERENCE.md)

---

**Version:** {features.get('version', 'Unknown')}  
**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}  
**Author:** Asif Hussain  
**Repository:** [github.com/asifhussain60/CORTEX](https://github.com/asifhussain60/CORTEX)
"""
        
        index_path = self.docs_root / "index.md"
        index_path.write_text(index_content, encoding='utf-8')
    
    def _format_recent_features(self, git_features: List[Dict]) -> str:
        """Format recently added features for index page"""
        if not git_features:
            return "*No recent features tracked.*"
        
        lines = []
        for feature in git_features[:5]:  # Top 5 recent
            lines.append(f"- **{feature.get('title', 'Unknown')}** - {feature.get('description', '')}")
        
        return "\n".join(lines)
    
    def _execute_mkdocs_build(self) -> Dict:
        """Execute mkdocs build command"""
        import subprocess
        import time
        
        start_time = time.time()
        
        try:
            # Run mkdocs build from site root
            result = subprocess.run(
                ["mkdocs", "build", "--config-file", str(self.mkdocs_config), "--site-dir", str(self.site_output)],
                cwd=str(self.site_root),
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            duration = time.time() - start_time
            
            if result.returncode == 0:
                return {
                    "status": "success",
                    "duration_seconds": duration,
                    "stdout": result.stdout
                }
            else:
                return {
                    "status": "failed",
                    "duration_seconds": duration,
                    "error": result.stderr
                }
        
        except subprocess.TimeoutExpired:
            return {
                "status": "timeout",
                "duration_seconds": 300,
                "error": "MkDocs build exceeded 5 minute timeout"
            }
        
        except FileNotFoundError:
            return {
                "status": "mkdocs_not_found",
                "duration_seconds": 0,
                "error": "mkdocs command not found. Install with: pip install mkdocs mkdocs-material mkdocs-mermaid2-plugin"
            }
    
    def _validate_site(self) -> Dict:
        """Validate generated site"""
        
        if not self.site_output.exists():
            return {
                "valid": False,
                "error": "Site output directory not found"
            }
        
        # Count generated pages
        html_files = list(self.site_output.rglob("*.html"))
        
        # Calculate site size
        total_size = sum(f.stat().st_size for f in self.site_output.rglob("*") if f.is_file())
        size_mb = total_size / (1024 * 1024)
        
        # Check for required files
        required_files = [
            "index.html",
            "search/search_index.json",
            "sitemap.xml"
        ]
        
        missing_files = [f for f in required_files if not (self.site_output / f).exists()]
        
        return {
            "valid": len(missing_files) == 0,
            "page_count": len(html_files),
            "size_mb": round(size_mb, 2),
            "missing_files": missing_files,
            "has_search": (self.site_output / "search" / "search_index.json").exists(),
            "has_sitemap": (self.site_output / "sitemap.xml").exists()
        }
    
    def _save_config(self, config: Dict):
        """Save mkdocs.yml configuration"""
        import yaml
        
        with open(self.mkdocs_config, 'w', encoding='utf-8') as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
```

**MkDocs Site Structure:**
```
docs/diagrams/  (CO-LOCATED WITH SOURCE)
├── mkdocs.yml          # MkDocs configuration (generated)
├── site/               # Built static site (output)
│   ├── index.html
│   ├── EXECUTIVE-SUMMARY/
│   ├── diagrams/
│   │   ├── mermaid/
│   │   ├── prompts/
│   │   └── narratives/
│   ├── narratives/
│   ├── search/
│   └── assets/
├── mermaid/            # Source diagrams
├── prompts/            # Source prompts
└── narratives/         # Source narratives
```

**MkDocs Features Enabled:**
- **Material Theme:** Professional, responsive design
- **Dark Mode:** Automatic/manual theme switching
- **Search:** Full-text search with suggestions
- **Navigation:** Hierarchical navigation with tabs
- **Mermaid Support:** Render `.mmd` diagrams inline
- **Code Highlighting:** Syntax highlighting for code blocks
- **Mobile Responsive:** Works on all devices
- **GitHub Integration:** Links to repository, edit pages

**Deployment:**
- **Local Preview:** `mkdocs serve` (http://localhost:8000)
- **GitHub Pages:** `mkdocs gh-deploy` (deploys to gh-pages branch)
- **Static Export:** Pre-built site in `docs/diagrams/site/`


#### 3.3 Story Generator Implementation

**"The Awakening of CORTEX"** - The hilarious technical narrative

```python
class StoryGenerator:
    """Generates the hilarious CORTEX awakening story"""
    
    def generate_awakening_story(self, features: Dict) -> str:
        """
        Generate the full story with:
        - Asif "Codenstein" as the mad scientist
        - GitHub Copilot as the brilliant but amnesiac intern
        - Asif's wife as the voice of reason (and humor)
        - Technical accuracy wrapped in humor
        """
        
        chapters = []
        
        # Chapter 1: The Amnesia Problem
        chapters.append(self._chapter_1_amnesia())
        
        # Chapter 2: Asif "Codenstein" Appears
        chapters.append(self._chapter_2_codenstein())
        
        # Chapter 3: "Honey, You're Talking to the Computer Again"
        chapters.append(self._chapter_3_wife_intervention())
        
        # Chapter 4: Building the Brain (Tier System)
        chapters.append(self._chapter_4_brain_building())
        
        # Chapter 5: The Agent Revolution
        chapters.append(self._chapter_5_agents())
        
        # Chapter 6: Real-World Chaos (Funny Bug Stories)
        chapters.append(self._chapter_6_real_world())
        
        # Chapter 7: The Transformation
        chapters.append(self._chapter_7_transformation())
        
        return "\n\n".join(chapters)
    
    def _chapter_1_amnesia(self) -> str:
        return """
# Chapter 1: The Amnesia Problem

*"What was I working on again?"*

It was 3 AM. Asif stared at his screen, GitHub Copilot blinking innocently 
back at him. He'd been implementing authentication for three days straight.

"Copilot, remember that JWT token refresh logic we designed on Monday?"

`I'm GitHub Copilot. I can help you write code!`

"No, no, I KNOW that. I'm asking about MONDAY. The design we spent 4 hours on."

`I don't have access to previous conversations. How can I help you today?`

Asif's eye twitched. This was the 47th time this week. The brilliant AI 
that could write flawless code... had the memory of a goldfish.

"THAT'S IT!" he shouted, startling his wife awake.

"Honey, it's 3 AM. Why are you yelling at your computer?"

"Because my computer has amnesia!" Asif declared, wild-eyed. 
"I'm going to build it a BRAIN!"

His wife rolled over. "Just... don't electrocute yourself like last time."

And thus, CORTEX was born. (Well, conceived. Building would take a LOT of coffee.)
"""
    
    def _chapter_2_codenstein(self) -> str:
        return """
# Chapter 2: Asif "Codenstein" Appears

*"It's alive! IT'S ALIVE!"*

The neighbors were getting concerned. For the fifth day straight, they'd 
heard Asif cackling maniacally at 2 AM, followed by his wife yelling 
"GO TO SLEEP, CODENSTEIN!"

The nickname stuck.

Asif - now officially "Codenstein" to his family - was building something 
revolutionary: a three-tier memory system for GitHub Copilot.

Tier 1: Working Memory (last 20 conversations)
Tier 2: Knowledge Graph (long-term pattern learning)
Tier 3: Context Intelligence (git analysis, file stability)

"It's like a human brain!" he explained to his unimpressed cat. "Tier 1 is 
short-term memory. Tier 2 is long-term. Tier 3 is... uh... the smart part 
that knows what files you haven't touched in months are probably stable."

The cat meowed, which Codenstein interpreted as "Brilliant! Continue!"

His wife interpreted it as "Feed me," which was more accurate.
"""
    
    def _chapter_3_wife_intervention(self) -> str:
        return """
# Chapter 3: "Honey, You're Talking to the Computer Again"

*The moment she realized her husband had lost his mind*

"Honey, can you explain to me why there's a file called 'brain-protection-rules.yaml' 
that says 'DO NOT DELETE OR CORTEX DIES'?"

Asif looked up from his keyboard, eyes blazing with the fire of a thousand 
commit messages.

"Because if someone deletes the brain protection rules, CORTEX forgets 
how to protect its brain! It's like... like..."

"Like that time you deleted the trash folder and lost all your 'definitely 
temporary' files that were actually important?"

"EXACTLY!" Codenstein beamed. "So I created Tier 0: The SKULL. 22 immutable 
rules that protect CORTEX from... well... me."

"You're protecting the AI from yourself."

"I'm protecting FUTURE me from CURRENT me. Future me is terrible at 
remembering what Current me was thinking."

His wife poured another cup of coffee. "At least you're self-aware."

"That's what Tier 1 is for!"

She just walked away.
"""
```

---

### Phase 4: Validation & Testing ✅

**Goal:** Verify all documentation is generated correctly

#### Validation Checklist

```markdown
## Documentation Generation Validation

### File Count Validation
- [ ] docs/diagrams/mermaid/ has 14+ .mmd files
- [ ] docs/diagrams/prompts/ has 10+ prompt files
- [ ] docs/diagrams/narratives/ has 14+ narrative files
- [ ] docs/narratives/THE-AWAKENING-OF-CORTEX.md exists
- [ ] docs/EXECUTIVE-SUMMARY.md exists and lists ALL features
- [ ] docs/FEATURES.md exists
- [ ] docs/MODULES-REFERENCE.md exists

### Content Quality Validation
- [ ] Executive Summary includes Git features from last 2 days
- [ ] All diagrams have corresponding prompts
- [ ] All diagrams have corresponding narratives
- [ ] Story chapters are complete and funny
- [ ] MkDocs site builds without errors

### Link Validation
- [ ] All internal links work
- [ ] All diagram references resolve
- [ ] Navigation structure is correct

### Generation Report
- [ ] Generation completes in < 5 minutes
- [ ] No errors in generation log
- [ ] All components report success
```

---

## 📋 Implementation Checklist

### 🗑️ Phase 0: Cleanup Operations (START CLEAN - FIRST)
- [ ] Run cleanup script
- [ ] Delete duplicate prompts folder
- [ ] Delete document_migration scripts
- [ ] Consolidate story folders
- [ ] Merge template folders
- [ ] Verify deletions
- [ ] Update import paths
- [ ] Update tests

### ✅ Phase 1: Design (CURRENT - COMPLETE)
- [x] Analyze current documentation structure
- [x] Map all generators and outputs
- [x] Analyze Git history for recent work
- [x] Design consolidated orchestrator architecture
- [x] Create comprehensive plan document
- [x] Update plan with DALL-E prompt design emphasis
- [x] Clarify narrative-to-prompt parity

### 🔄 Phase 2: Identify Wrong Structures (Verification)
- [ ] Run recursive search for all doc folders
- [ ] Identify any remaining duplicate generators
- [ ] Verify cleanup was complete
- [ ] Create final cleanup manifest if needed

### 🛠️ Phase 3: Implement Orchestrator
- [ ] Implement Discovery Engine
- [ ] Enhance Generation Pipeline with DALL-E prompt generation
- [ ] Implement Narrative Generator (high-level explanations)
- [ ] Implement Story Generator (The Awakening)
- [ ] Integrate all component generators
- [ ] Add validation layer
- [ ] Ensure prompt-to-narrative parity

### ✅ Phase 4: Validate
- [ ] Run consolidated orchestrator
- [ ] Verify file counts (14+ diagrams, 10+ prompts, 14+ narratives)
- [ ] Check content quality (DALL-E prompts sophisticated, narratives clear)
- [ ] Validate prompt-to-narrative pairing
- [ ] Validate links
- [ ] Test MkDocs build

---

## 🎯 Success Criteria

**The consolidated orchestrator is successful when:**

1. ✅ **Single Entry Point:** One command generates ALL documentation
2. ✅ **Fresh Discovery:** Discovers new features from Git (last 2 days) and YAML configs
3. ✅ **Complete Output:** Generates all required files:
   - 14+ Mermaid diagrams
   - 10+ AI prompts
   - Multiple narratives (technical + story)
   - Executive summary with ALL features
   - Complete MkDocs site
4. ✅ **No Duplicates:** Zero duplicate folder structures
5. ✅ **Quality Content:** Story is funny, technical docs are accurate
6. ✅ **Fast Generation:** Completes in < 5 minutes
7. ✅ **Validated:** All links work, no broken references

---

## 📊 Estimated Effort

| Phase | Tasks | Estimated Time |
|-------|-------|----------------|
| Phase 0: Cleanup | Script execution (START CLEAN) | **30 minutes** |
| Phase 1: Design | Analysis + Planning | ✅ **2 hours (COMPLETE)** |
| Phase 2: Identify | Recursive search + verification | **30 minutes** |
| Phase 3: Implement | Code enhancement + DALL-E prompts | **5-7 hours** |
| Phase 4: Validate | Testing + fixes | **1-2 hours** |
| **TOTAL** | | **9-12 hours** |

---

## 🚀 Next Actions

1. **Review this plan** with user ✅
2. **Get approval** to proceed with Phase 0
3. **Execute Phase 0:** Cleanup operations (START CLEAN - delete duplicates)
4. **Execute Phase 2:** Verify cleanup complete (recursive search)
5. **Execute Phase 3:** Implement consolidated orchestrator with DALL-E prompts
6. **Execute Phase 4:** Validation and testing (verify prompt-narrative parity)

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Repository:** https://github.com/asifhussain60/CORTEX

---

*End of Plan Document*
