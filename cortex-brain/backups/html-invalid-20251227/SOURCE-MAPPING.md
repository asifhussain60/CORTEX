# HTML Source Mapping Document
**Date:** December 27, 2025  
**Purpose:** Map 32 invalid HTML files to their source documents for regeneration

---

## 📊 Summary

- **Total Files to Regenerate:** 32
- **Backup Location:** `cortex-brain/backups/html-invalid-20251227/`
- **Method:** DELETE → CREATE (no partial updates)

---

## 🗺️ Source Mappings

### Critical Structure Files (4 files)

#### 1. faq.html
**Errors:** 4 structural errors  
**Source Documents:**
- Current content from `cortex-brain/backups/html-invalid-20251227/faq.html`
- FAQ categories from CORTEX4-STATUS.md
- Technical references from `cortex-brain/documents/`
- Common questions from GitHub Issues (if available)

**Template Requirements:**
- 8 FAQ categories with accordion UI
- `.faq-container` wrappers for proper nesting
- Search functionality
- Cross-references to documentation

---

#### 2. tdd-orchestrator.html
**Errors:** 17 errors (mostly </br> tags)  
**Source Documents:**
- `src/orchestrators/tdd/tdd_orchestrator.py`
- `cortex-brain/documents/archive/TDD-V4-ORCHESTRATOR-ARCHITECTURE.md`
- `cortex-operations.yaml` (TDD operation definition)

**Template Requirements:**
- Feature benefit panel: "Writing tests first sounds great..." efficiency statement
- RED-GREEN-REFACTOR cycle explanation
- Phase-by-phase breakdown
- D3.js TDD cycle diagram
- NO </br> tags, use <br> or <br/>

---

#### 3. tutorial.html
**Errors:** 2 errors (code tag mismatch)  
**Source Documents:**
- `cortex-brain/documents/learning-paths/` (if exists)
- Current content from backup
- Getting-started workflow from CORTEX4-STATUS.md

**Template Requirements:**
- Interactive walkthrough
- Step-by-step with code examples
- Cross-references to learning-paths/
- Fix code tag mismatch (lines 229-243)

---

#### 4. architecture/index.html (architecture-index.html in backup)
**Errors:** 2 errors (</img>, </script> mismatches)  
**Source Documents:**
- `cortex-brain/documents/archive/CORTEX-UPGRADE-ARCHITECTURE.md`
- `cortex-brain/architecture/` overview documents
- Four-tier brain structure from tier0-tier3 docs

**Template Requirements:**
- Architecture overview with D3.js visualization
- 4-Tier Brain introduction
- Orchestrator ecosystem summary
- Proper semantic HTML5 structure

---

### Orchestrator Pages (13 files)

**Common Sources:**
- Individual Python files in `src/orchestrators/`
- `cortex-operations.yaml` for operation definitions
- Architecture docs in `cortex-brain/documents/archive/*-ORCHESTRATOR-ARCHITECTURE.md`

**Common Template Sections:**
1. Feature Benefit Panel (ALWAYS FIRST)
2. Key Metrics Grid
3. Overview Section
4. Architecture Section
5. Workflow Section (phase-by-phase)
6. Integration Section
7. Configuration Section
8. Usage Examples
9. Testing Section
10. Performance Section
11. Interactive Diagram (D3.js/Mermaid)

#### 1. architectural-review.html
**Sources:**
- `src/orchestrators/system/architectural_review_orchestrator.py` (if exists)
- `cortex-brain/documents/archive/`
**Icon:** 🏛️

#### 2. autonomous-execution.html
**Sources:**
- `src/orchestrators/autonomous_execution_engine.py`
- `cortex-operations.yaml` (autonomous execution definition)
**Icon:** ⚡

#### 3. cleanup-orchestrator.html
**Sources:**
- `src/orchestrators/system/cleanup_orchestrator.py`
- Cleanup rules from `cortex-brain/cleanup-rules.yaml`
**Icon:** 🧹

#### 4. code-sanitization.html
**Sources:**
- `src/orchestrators/sanitization/sanitization_orchestrator.py`
- `cortex-brain/documents/archive/CODE-SANITIZATION-ORCHESTRATOR-ARCHITECTURE.md`
- `cortex-brain/CODE-SANITIZATION-QUICK-REF.md`
**Icon:** 🔒

#### 5. debug-orchestrator.html
**Sources:**
- `src/orchestrators/system/debug_orchestrator.py` (if exists)
- Debug workflow from operations config
**Icon:** 🔍

#### 6. git-checkpoint.html
**Sources:**
- `src/orchestrators/git_checkpoint_orchestrator.py`
- `cortex-brain/git-checkpoint-rules.yaml`
**Icon:** 📦

#### 7. intelligent-dashboard.html
**Sources:**
- `src/orchestrators/dashboard_generator.py`
- Dashboard metrics from CORTEX4-STATUS.md
**Icon:** 📊

#### 8. maintenance-orchestrator.html
**Sources:**
- `src/orchestrators/system/maintenance_orchestrator.py`
- `cortex-brain/documents/archive/SYSTEM-MAINTENANCE-ORCHESTRATOR-ARCHITECTURE.md`
- 7-phase workflow from operations config
**Icon:** 🔧

#### 9. planning-system.html
**Sources:**
- `src/orchestrators/planning/planning_orchestrator.py`
- `cortex-brain/documents/archive/PLANNING-SYSTEM-2.0-ORCHESTRATOR-ARCHITECTURE.md`
- `cortex-brain/manifests/planning-system-manifest.yaml`
**Icon:** 🎯

#### 10. pre-flight.html
**Sources:**
- `src/orchestrators/system/pre_flight_orchestrator.py` (if exists)
- Pre-flight checks from operations config
**Icon:** ✈️

#### 11. refinement-orchestrator.html
**Sources:**
- `src/orchestrators/system/refinement_orchestrator.py` (if exists)
- Refinement workflow from operations
**Icon:** ✨

#### 12. rollback-orchestrator.html
**Sources:**
- `src/orchestrators/rollback_orchestrator.py`
- `src/orchestrators/rollback_command_parser.py`
**Icon:** ↩️

#### 13. system-integrity.html
**Sources:**
- `src/orchestrators/system/system_integrity_orchestrator.py` (if exists)
- System health checks from operations
**Icon:** 🛡️

---

### Getting Started Pages (4 files)

#### 1. deployment.html
**Sources:**
- `README.md` (installation instructions)
- `requirements.txt` (dependencies)
- Setup workflow from CORTEX4-STATUS.md

#### 2. first-commands.html
**Sources:**
- `cortex-operations.yaml` (essential commands)
- Quick reference from CORTEX.prompt.md

#### 3. index.html (getting-started-index.html in backup)
**Sources:**
- Quick start guide from README.md
- 5-minute setup workflow
- 1:∞ repo support explanation

#### 4. multi-repo-setup.html
**Sources:**
- Phase 11 documentation from CORTEX4-STATUS.md
- Multi-repo configuration from `cortex.config.json`
- `cortex-brain/documents/implementation-guides/` (if exists)

---

### Architecture Pages (4 additional files)

#### 1. agent-system.html
**Sources:**
- `src/cortex_agents/planning_agent.py`
- `src/cortex_agents/strategic_reasoning_agent.py`
- Agent architecture docs

#### 2. four-tier-brain.html
**Sources:**
- `cortex-brain/tier0/`, `tier1/`, `tier2/`, `tier3/` structures
- Brain architecture from CORTEX.prompt.md
- SKULL rules from `cortex-brain/brain-protection-rules.yaml`

#### 3. orchestrator-ecosystem.html
**Sources:**
- `src/orchestrators/base/base_orchestrator.py`
- BaseOrchestrator pattern documentation
- Orchestrator registry and discovery

#### 4. working-memory.html
**Sources:**
- `cortex-brain/tier1/` structure
- 70-conversation FIFO queue implementation
- Working memory architecture docs

---

### Features & Validation Pages (6 files)

#### 1. ado-operations.html
**Sources:**
- `src/orchestrators/ado/ado_orchestrator.py`
- `cortex-brain/documents/archive/ADO-OPERATIONS-ORCHESTRATOR-ARCHITECTURE.md`
- `cortex-brain/manifests/ado-planning-manifest.yaml`

#### 2. index.html (features-index.html in backup)
**Sources:**
- Features overview from CORTEX4-STATUS.md
- Feature summaries from all orchestrators

#### 3. tdd-mastery.html
**Sources:**
- TDD workflow from TDD orchestrator
- Test coverage metrics
- RED-GREEN-REFACTOR cycle

#### 4. index.html (toolkit-index.html in backup)
**Sources:**
- `cortex-toolkit/` directory structure
- Toolkit overview from README files

#### 5. validation-tools.html
**Sources:**
- `cortex-toolkit/documentation/html-tools/` scripts
- Validation workflow documentation

#### 6. capabilities.html
**Sources:**
- `cortex-brain/capabilities.yaml`
- 9 validated capabilities from Phase 13B
- STS baseline validation results

---

## 🎨 Template Patterns from Valid Files

**To be extracted from 26 valid HTML files:**

### Common Structure
```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Page Title | CORTEX 4.0</title>
    <link rel="stylesheet" href="../assets/css/main.css">
</head>
<body>
    <div class="logo-header">
        <a href="../index.html">
            <img src="../assets/images/CORTEX-logo.png" alt="CORTEX Logo" class="page-logo">
        </a>
    </div>

    <nav class="breadcrumb">...</nav>

    <main>
        <!-- Feature Benefit Panel (orchestrators/features only) -->
        <div class="feature-benefit-panel">
            <div class="icon">🎯</div>
            <div class="description">
                Natural language efficiency statement...
            </div>
        </div>

        <!-- Content -->
    </main>

    <footer>
        <p>&copy; 2025 CORTEX. All rights reserved.</p>
    </footer>

    <script src="../assets/js/main.js" defer></script>
</body>
</html>
```

### Glassmorphism Classes
- `.glass-bg` - Glass background effect
- `.feature-benefit-panel` - Efficiency statement panel
- `.section-overview` - Section container
- `.metric-grid` - Key metrics display
- `.phase-card` - Phase breakdown cards
- `.code-block` - Code examples
- `.breadcrumb` - Navigation breadcrumbs
- `.logo-header` - Logo container

### NO INLINE STYLES
- ❌ FORBIDDEN: `style="..."` attributes (except story button)
- ❌ FORBIDDEN: Page-specific `<style>` tags
- ❌ FORBIDDEN: Alternate CSS files

---

## ✅ Next Steps

1. ✅ Backup complete (32 files)
2. ✅ Source mapping documented
3. ⏳ Extract template patterns from 26 valid files
4. ⏳ Begin Phase 2: Delete invalid files (after template extraction)

---

**End of Source Mapping Document**
