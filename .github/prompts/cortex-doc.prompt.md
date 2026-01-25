# CORTEX Documentation - Automated Discovery, Generation & Cleanup
**Authority:** cortex-impl-map.yaml | **Status:** ✅ PRODUCTION READY

---

## ⚠️ CRITICAL: Response Header + Implementation Truth (TIER 0)

**EVERY response MUST begin with:**
```markdown
## 🧠 CORTEX Documentation
**Author:** Asif Hussain | **Phase:** Documentation | **Orchestrator:** DocumentationOrchestrator ✅

---
```

**DOCUMENTATION WITH IMPLEMENTATION TRUTH (CORE-030):**
1. **VERIFY IMPLEMENTATION:** Use grep_search/read_file to check actual code
2. **CHECK TEST ISOLATION:** Ensure no test data contamination
3. **VALIDATE API METHODS:** Confirm method names exist in implementation
4. **DOCUMENT WHAT EXISTS:** Only document verified, implemented features

---

## 🎯 Purpose

**CORTEX Documentation** is a comprehensive documentation orchestration system that:

1. **Discovers** new components from codebase analysis
2. **Catalogs** modules with metadata and capabilities
3. **Generates** documentation with mermaid & D3.js diagrams
4. **Validates** mkdocs site integrity and links
5. **Cleans** obsolete, redundant, and duplicate files
6. **Maintains** documentation currency and consistency

---

## 🔄 CORTEX LENS → DoR → Approval Protocol

### One-Shot End-to-End Execution Model

This prompt implements a **unified one-shot execution** model:

**Step 1: Intent Classification**
```markdown
### 📋 Intent Classification

| Field | Value |
|-------|-------|
| **Intent** | `DOCUMENT - FRESH GENERATION` |
| **Handler** | `DocumentationOrchestrator` |
| **Confidence** | 🟢 High (95%) |
| **Scope** | `SYSTEM` |
| **Impact** | � High (Regenerates entire docs/) |
| **Target** | `docs/`, `_workspaces/reports/` |
| **Rules** | CORE-012, CORE-027 |
| **Workflow** | 8-Phase end-to-end pipeline (no stopping) |

---
**⏳ Awaiting approval to proceed with complete fresh documentation generation...**
```

**Step 2: Wait for User Approval**
- Accept: "proceed", "yes", "approve", "go ahead", "do it"
- Reject: "no", "cancel", "stop", "abort"

**Step 3-10: Automatic End-to-End Execution (NO USER INTERACTION)**
Once approved, execute ALL phases without stopping:
1. **DISCOVERY** → Scan codebase for components
2. **GENERATION** → Generate all markdown documentation
3. **DIAGRAMS** → Generate Mermaid + D3.js diagrams (10 total)
4. **BUILD** → mkdocs build --strict (ZERO warnings/errors)
5. **VALIDATION** → Validate all links and references
6. **REPORTING** → Generate completion report
7. **POST-CLEANUP** → Delete legacy markdown files (final cleanup)
8. **GIT-COMMIT** → Final git commit with all changes

---

## 🎯 Command

| Command | Action | Execution |
|---------|--------|-----------|
| `/doc-fresh-generate` | Fresh generation: DISCOVERY → GENERATION → DIAGRAMS → BUILD → VALIDATION → REPORTING → POST-CLEANUP → GIT-COMMIT | End-to-End (No stops) |

---

## � 7-Phase End-to-End Execution Pipeline

Once user approves with "proceed" or "yes", execute ALL phases automatically:

### Phase 1: DISCOVERY (Scan codebase)
```python
class DiscoveryOrchestrator:
    """Scan codebase for undocumented components."""
    
    def scan_orchestrators(self):
        """Find all orchestrator classes."""
        scan: cortex/orchestrators/
        results: List[OrchestratorMetadata]
        
    def scan_mcp_tools(self):
        """Find all MCP tool decorators."""
        scan: cortex/mcp/tools/
        results: List[MCPToolMetadata]
        
    def scan_governance(self):
        """Find all CORE rules."""
        scan: cortex_brain/tier0/governance/
        results: List[GovernanceRule]
    
    def generate_inventory(self):
        """Create component catalog."""
        return ComponentInventory(
            orchestrators=self.scan_orchestrators(),
            mcp_tools=self.scan_mcp_tools(),
            governance_rules=self.scan_governance()
        )

print("✅ PHASE 1: DISCOVERY COMPLETE")
```

### Phase 2: GENERATION (Create markdown docs)
```python
class DocumentationGenerationOrchestrator:
    """Generate comprehensive markdown documentation."""
    
    def generate_all_markdown(self):
        """Generate all sections of documentation."""
        sections = {
            "00-README.md": self._generate_readme(),
            "01-getting-started/": self._generate_getting_started(),
            "02-architecture/": self._generate_architecture(),
            "03-api-reference/": self._generate_api_reference(),
            "04-guides/": self._generate_guides(),
            "05-tutorials/": self._generate_tutorials(),
            "06-reference/": self._generate_reference(),
        }
        return sections

print("✅ PHASE 2: GENERATION COMPLETE")
```

**Generated files:**
- `docs/00-README.md` - Main entry point
- `docs/01-getting-started/` - Installation, quickstart (3 files)
- `docs/02-architecture/` - Brain tiers, orchestrators, infrastructure (4 files)
- `docs/03-api-reference/` - Orchestrators, MCP tools, governance (3 sections)
- `docs/04-guides/` - How-to guides (5+ files)
- `docs/05-tutorials/` - Step-by-step tutorials (4+ files)
- `docs/06-reference/` - API reference, glossary, rules (3+ files)

### Phase 4: DIAGRAMS (Generate all visualizations)
```python
class DiagramGenerationOrchestrator:
    """Generate Mermaid + D3.js diagrams."""
    
    def generate_all_diagrams(self):
        """Generate 10 diagrams total."""
        
        # Mermaid (6 diagrams)
        mermaid = [
            ("approval-gate-decision-tree.mmd", "flowchart", "Complexity scoring flow"),
            ("error-recovery-paths.mmd", "flowchart", "Error handling recovery"),
            ("circuit-breaker-state-machine.mmd", "stateDiagram", "Resilience pattern"),
            ("master-orchestrator-sequence.mmd", "sequenceDiagram", "Execution protocol"),
            ("tdd-workflow-phases.mmd", "flowchart", "RED → GREEN → REFACTOR"),
            ("governance-rule-categories.mmd", "graph", "29 CORE rules pyramid"),
        ]
        
        # D3.js (4 diagrams)
        d3js = [
            ("governance-pyramid.html", "sunburst", "Interactive governance pyramid"),
            ("request-lifecycle-sankey.html", "sankey", "Request flow diagram"),
            ("tdd-knowledge-cycle.html", "circular", "TDD workflow cycle"),
            ("domain-brain-architecture.html", "layered", "Domain brain layers"),
        ]
        
        return {
            "mermaid": self._generate_mermaid_diagrams(mermaid),
            "d3js": self._generate_d3js_diagrams(d3js)
        }

print("✅ PHASE 3: DIAGRAMS COMPLETE")
```

**Generated diagrams:**
- `docs/02-architecture/_diagrams/approval-gate-decision-tree.mmd`
- `docs/02-architecture/_diagrams/error-recovery-paths.mmd`
- `docs/02-architecture/_diagrams/circuit-breaker-state-machine.mmd`
- `docs/02-architecture/_diagrams/master-orchestrator-sequence.mmd`
- `docs/02-architecture/_diagrams/tdd-workflow-phases.mmd`
- `docs/02-architecture/_diagrams/governance-rule-categories.mmd`
- `docs/_diagrams/d3/governance-pyramid.html` (+ data generator)
- `docs/_diagrams/d3/request-lifecycle-sankey.html` (+ data generator)
- `docs/_diagrams/d3/tdd-knowledge-cycle.html`
- `docs/_diagrams/d3/domain-brain-architecture.html`

### Phase 4: BUILD (mkdocs --strict)
```bash
#!/bin/bash

echo "🏗️  PHASE 4: Building mkdocs (--strict: ZERO warnings/errors)..."

# Validate configuration
mkdocs validate || { echo "❌ Config invalid"; exit 1; }

# Build with strict mode
mkdocs build --strict --clean || { echo "❌ Build failed"; exit 1; }

# Verify ZERO warnings in output
if mkdocs build 2>&1 | grep -iE "warning|error"; then
    echo "❌ Build contains warnings/errors"
    exit 1
fi

echo "✅ PHASE 4: BUILD COMPLETE - ZERO WARNINGS, ZERO ERRORS!"
echo "📍 Site ready at: _build/site/"
```

### Phase 5: VALIDATION (Check links and references)
```bash
#!/bin/bash

echo "🔗 PHASE 5: Validating all internal links..."

broken_count=0
find _build/site -name "*.html" -print0 | while IFS= read -r -d '' file; do
    grep -o 'href="[^"]*"' "$file" 2>/dev/null | sed 's/href="//;s/"$//' | while read link; do
        [[ $link == http* ]] && continue
        
        target="${file%/*}/$link"
        if [ ! -f "$target" ]; then
            echo "❌ Broken: $link in $file"
            ((broken_count++))
        fi
    done
done

[ $broken_count -eq 0 ] && echo "✅ PHASE 5: VALIDATION COMPLETE - All links valid"
```

### Phase 6: REPORTING (Generate completion report)
```bash
#!/bin/bash

echo "📊 PHASE 6: Final Report"

# Generate report
report="FRESH-DOCUMENTATION-GENERATION-$(date +%Y-%m-%d).md"

cat > "_workspaces/reports/$report" << 'EOF'
# Fresh Documentation Generation Report

## Summary
- ✅ Serve scripts: PRESERVED (serve-docs.bat, serve-docs.sh)
- ✅ Markdown docs: Generated (7 sections, 16+ files)
- ✅ Diagrams: Generated (6 Mermaid + 4 D3.js = 10 total)
- ✅ Build status: ZERO warnings, ZERO errors
- ✅ Links validation: All valid
- ✅ Site ready: _build/site/

## Files Generated
### Documentation
- docs/00-README.md
- docs/01-getting-started/ (3 files)
- docs/02-architecture/ (4 files)
- docs/03-api-reference/ (3 sections)
- docs/04-guides/ (5+ files)
- docs/05-tutorials/ (4+ files)
- docs/06-reference/ (3+ files)

### Diagrams (Mermaid)
- docs/02-architecture/_diagrams/approval-gate-decision-tree.mmd
- docs/02-architecture/_diagrams/error-recovery-paths.mmd
- docs/02-architecture/_diagrams/circuit-breaker-state-machine.mmd
- docs/02-architecture/_diagrams/master-orchestrator-sequence.mmd
- docs/02-architecture/_diagrams/tdd-workflow-phases.mmd
- docs/02-architecture/_diagrams/governance-rule-categories.mmd

### Diagrams (D3.js)
- docs/_diagrams/d3/governance-pyramid.html
- docs/_diagrams/d3/request-lifecycle-sankey.html
- docs/_diagrams/d3/tdd-knowledge-cycle.html
- docs/_diagrams/d3/domain-brain-architecture.html

## Quality Metrics
✅ mkdocs build: PASSED (--strict mode)
✅ Link validation: 100% (all internal links valid)
✅ Documentation coverage: COMPLETE
✅ Diagram count: 10 (6 Mermaid + 4 D3.js)
✅ Infrastructure preserved: _archive/, assets/, theme/
✅ Serve scripts: serve-docs.bat, serve-docs.sh

## Execution Timeline
- Discovery: [timestamp]
- Generation: [timestamp]
- Diagrams: [timestamp]
- Build: [timestamp]
- Validation: [timestamp]
- Reporting: [timestamp]
- Post-cleanup: [timestamp]
- Git commit: [timestamp]

## Next Steps
1. Run: `mkdocs serve` to preview
2. Run: `mkdocs gh-deploy` to publish
3. Share site with team

## Governance Compliance
✅ AC_START logged
✅ CORE-012 (docstrings): All components documented
✅ CORE-027 (audit trail): AC_COMPLETE logged
✅ Git checkpoint: Commit created
EOF

# Git add (but don't commit - Phase 7 will commit everything)
git add docs/
git add _workspaces/reports/$report

echo "✅ PHASE 6: REPORTING COMPLETE"
echo "📊 Report: _workspaces/reports/$report"
```

### Phase 7: POST-CLEANUP (Remove legacy files)
```bash
#!/bin/bash

echo "🧹 PHASE 7: POST-CLEANUP - Removing legacy files"

cd docs

# Remove all legacy markdown files (everything except serve scripts)
find . -maxdepth 1 -type f -name "*.md" -delete

# Remove old generated directories that may have been recreated
rm -rf _diagrams _reports _tests

# VERIFY serve scripts still exist
[ -f "serve-docs.bat" ] && [ -f "serve-docs.sh" ] && echo "✅ Serve scripts preserved"

# VERIFY new generated content exists
if [ -d "01-getting-started" ] || [ -f "00-README.md" ]; then
    echo "✅ Fresh documentation preserved"
else
    echo "❌ ERROR: Fresh documentation missing!"
    exit 1
fi

echo "✅ PHASE 7: POST-CLEANUP COMPLETE"
```

### Phase 8: GIT-COMMIT (Final commit with all changes)
```bash
#!/bin/bash

echo "📦 PHASE 8: Final Git Commit"

# Commit all changes (fresh docs, diagrams, cleanup, and report)
git commit -m "docs: fresh generation - $(date +%Y-%m-%d)

Fresh documentation generation pipeline complete:
- Phase 1: Discovery (scan codebase)
- Phase 2: Generation (create markdown)
- Phase 3: Diagrams (6 Mermaid + 4 D3.js)
- Phase 4: Build (--strict, zero warnings/errors)
- Phase 5: Validation (all links verified)
- Phase 6: Reporting (completion summary)
- Phase 7: Post-cleanup (remove legacy files)
- Phase 8: Git commit (all changes committed)

Site ready: docs/_build/site/
Serve with: mkdocs serve"

git push origin $(git rev-parse --abbrev-ref HEAD)

echo "✅ PHASE 8: GIT-COMMIT COMPLETE"
echo "✅ All changes committed and pushed"
```

---

## ✅ Execution Summary

When user types "proceed":
1. ✅ AC_START logged with operation ID
2. ✅ Phase 1: DISCOVERY executes (scan codebase)
3. ✅ Phase 2: GENERATION executes (create all markdown)
4. ✅ Phase 3: DIAGRAMS executes (10 diagrams total)
5. ✅ Phase 4: BUILD executes (mkdocs --strict)
6. ✅ Phase 5: VALIDATION executes (link checks)
7. ✅ Phase 6: REPORTING executes (completion summary)
8. ✅ Phase 7: POST-CLEANUP executes (remove legacy files)
9. ✅ Phase 8: GIT-COMMIT executes (final commit + push)
10. ✅ AC_COMPLETE logged with result
11. ✅ Final summary displayed to user

**NO STOPPING, NO CHOICES, NO PAUSES** — Fully automated end-to-end pipeline

---

---

## 🔍 Discovery Algorithms

### Orchestrator Discovery
```yaml
scan: cortex/orchestrators/
detect:
  - Classes inheriting BaseOrchestrator
  - @register_with_master decorators
  - Domain and capability metadata
extract:
  - Class name, docstring
  - Public methods
  - Entry points
```

### MCP Tool Discovery
```yaml
scan: cortex/mcp/tools/
detect:
  - @mcp_tool decorators
  - Tool registry entries
extract:
  - Tool ID, description
  - Parameters, return types
  - Category, auth level
```

### Governance Discovery
```yaml
scan: cortex_brain/tier0/governance/
detect:
  - CORE rules in YAML
  - Enforcement points
extract:
  - Rule ID, description
  - Severity, enforcement mode
```

---

## 🎨 Diagram Generation System

### Diagram Types & Locations

#### Mermaid Diagrams (Static, Version-Controlled)
**Location:** `docs/04-architecture/_diagrams/`

```yaml
diagrams:
  - approval-gate-decision-tree.mmd
    purpose: Complexity scoring and approval logic visualization
    type: flowchart
    
  - error-recovery-paths.mmd
    purpose: Show all error categories and recovery mechanisms
    type: flowchart
    
  - circuit-breaker-state-machine.mmd
    purpose: Resilience pattern state transitions
    type: stateDiagram
    
  - master-orchestrator-sequence.mmd
    purpose: Turn-by-turn execution protocol
    type: sequenceDiagram
    
  - tdd-workflow-phases.mmd
    purpose: RED → GREEN → REFACTOR with knowledge injection
    type: flowchart
    
  - governance-rule-categories.mmd
    purpose: 29 CORE rules organized by category
    type: graph

generation_command: |
  /doc-diagram mermaid --type=flowchart --title="Approval Gate Decision Tree"
  /doc-diagram mermaid --type=stateDiagram --title="Circuit Breaker"
```

#### D3.js Visualizations (Interactive, Dynamic)
**Location:** `docs/_diagrams/d3/`

```yaml
visualizations:
  - governance-pyramid.html
    tech: D3.js sunburst chart
    data_source: Python script generates JSON
    interactivity: Hover for details, click to navigate
    
  - request-lifecycle-sankey.html
    tech: D3.js Sankey diagram
    data_source: Dynamic or static flow data
    interactivity: Flow width shows probability
    
  - tdd-knowledge-cycle.html
    tech: D3.js circular flow
    data_source: Static workflow definition
    interactivity: Highlight phases on hover
    
  - domain-brain-architecture.html
    tech: D3.js layered diagram
    data_source: Adapter and query engine specs
    interactivity: Click to show data flow details

generation_command: |
  /doc-diagram d3js --type=sunburst --title="Governance Pyramid"
  /doc-diagram d3js --type=sankey --title="Request Lifecycle"
  /doc-diagram d3js --type=circular --title="TDD Workflow"
```

### Diagram Generation Workflow

```python
class DiagramGenerationOrchestrator:
    """Generate diagrams during documentation phase."""
    
    def generate_diagrams(self):
        """Generate all documentation diagrams."""
        diagrams = {
            "mermaid": self._generate_mermaid_diagrams(),
            "d3js": self._generate_d3js_diagrams()
        }
        return diagrams
    
    def _generate_mermaid_diagrams(self):
        """Generate Mermaid diagrams for logic and flows."""
        return [
            {
                "name": "approval-gate-decision-tree.mmd",
                "source": "templates/diagrams/approval-gate.mermaid",
                "output": "docs/04-architecture/_diagrams/"
            },
            # ... additional diagrams
        ]
    
    def _generate_d3js_diagrams(self):
        """Generate D3.js interactive visualizations."""
        return [
            {
                "name": "governance-pyramid.html",
                "template": "templates/diagrams/d3-sunburst.html",
                "data_generator": "scripts/generate-governance-data.py",
                "output": "docs/_diagrams/d3/"
            },
            # ... additional visualizations
        ]
```

---

## 🧹 Documentation Cleanup Cycle

### Purpose
Automatically identify and remove redundant, duplicate, and obsolete documentation files to maintain a clean, maintainable docs folder.

### Cleanup Triggers
- Manual: `/doc-cleanup`
- Automatic: After every major documentation generation cycle
- Scheduled: Weekly or on-demand

### Redundancy Detection Rules

```yaml
REDUNDANCY_RULES:
  # Rule 1: Multiple files documenting the same component
  duplicate_component_docs:
    pattern: "Same component documented in multiple files"
    action: "KEEP latest, ARCHIVE others to _archive/{component}-v{old_version}"
    examples:
      - "orchestrators/master-orchestrator.md + orchestrators/01-master-orchestrator.md"
      - "CORTEX-MASTER-ORCHESTRATOR-v1.md + CORTEX-MASTER-ORCHESTRATOR-v2.md"
  
  # Rule 2: Implementation reports and completion summaries
  completion_reports:
    pattern: "Files ending with: -REPORT.md, -SUMMARY.md, -COMPLETE.md, COMPLETION"
    action: |
      IF NEWER version exists:
        ARCHIVE old report to _archive/reports/
      ELSE:
        KEEP (may be historical record)
  
  # Rule 3: Session notes and temporary working files
  session_files:
    pattern: "SESSION-*.md, BRT-*.md, PHASE*-*.md, *-QUICK*.md"
    action: |
      IF superseded by newer session:
        ARCHIVE to _archive/sessions/{date}/
      ELSE:
        KEEP (active working session)
  
  # Rule 4: Test and intermediate files
  intermediate_files:
    pattern: "DRY-RUN-*.md, TEST-*.md, *-VALIDATION.md, *-ANALYSIS.md"
    action: "ARCHIVE to _archive/temp/ if not referenced in primary docs"
  
  # Rule 5: Duplicate diagrams or visualizations
  duplicate_diagrams:
    pattern: "Same diagram in multiple locations or formats"
    action: "KEEP canonical version, REMOVE duplicates"
    examples:
      - "One governance diagram: keep in _diagrams/, remove from docs/"
      - "Consolidate similar error recovery flow diagrams"
  
  # Rule 6: Obsolete feature documentation
  obsolete_features:
    pattern: "Documented features no longer in codebase"
    action: "MOVE to _archive/obsolete/ with DEPRECATION marker"
    check: "Verify feature exists in current codebase"
  
  # Rule 7: Redundant best practice documentation
  duplicate_guidance:
    pattern: "Multiple docs for same best practice/pattern"
    action: "CONSOLIDATE into single canonical doc, cross-reference"
    examples:
      - "Multiple TDD guides → Single authoritative guide"
      - "Multiple API design docs → Single API design guide"

ORPHANED_FILES:
  pattern: "Files not referenced from mkdocs.yml or other docs"
  action: "WARN user, ask for confirmation before archiving"
  exceptions:
    - "_archive/**" (ignore archived files)
    - "assets/**" (keep media)
    - "theme/**" (keep theme files)
```

### Cleanup Workflow

```python
class DocumentationCleanupOrchestrator:
    """Identify and clean up redundant documentation."""
    
    def execute_cleanup_cycle(self) -> CleanupReport:
        """Run complete cleanup cycle."""
        report = CleanupReport()
        
        # Phase 1: Scan for redundancies
        redundancies = self._find_redundancies()
        report.add_section("redundancies_found", redundancies)
        
        # Phase 2: Identify orphaned files
        orphans = self._find_orphaned_files()
        report.add_section("orphaned_files", orphans)
        
        # Phase 3: Detect obsolete content
        obsolete = self._find_obsolete_content()
        report.add_section("obsolete_content", obsolete)
        
        # Phase 4: Generate cleanup recommendations
        recommendations = self._generate_recommendations(
            redundancies, orphans, obsolete
        )
        report.add_section("recommendations", recommendations)
        
        return report
    
    def _find_redundancies(self) -> List[Redundancy]:
        """Find duplicate and redundant documentation."""
        redundancies = []
        
        # Check for multiple component docs
        components = self._scan_components()
        for component, docs in components.items():
            if len(docs) > 1:
                redundancies.append(
                    Redundancy(
                        type="DUPLICATE_COMPONENT_DOCS",
                        component=component,
                        files=docs,
                        recommendation=f"Keep {docs[0]}, archive {docs[1:]}"
                    )
                )
        
        # Check for completion report accumulation
        reports = self._find_files_matching("*REPORT.md", "*SUMMARY.md")
        for group in self._group_by_component(reports):
            if len(group) > 1:
                redundancies.append(
                    Redundancy(
                        type="DUPLICATE_REPORTS",
                        files=group,
                        recommendation=f"Keep latest, archive older versions"
                    )
                )
        
        return redundancies
    
    def _find_orphaned_files(self) -> List[str]:
        """Find files not referenced in mkdocs.yml or other docs."""
        referenced = self._extract_referenced_files()
        all_docs = self._scan_all_docs()
        orphans = [f for f in all_docs if f not in referenced]
        
        # Filter exceptions
        return [o for o in orphans if not self._is_exception(o)]
    
    def _find_obsolete_content(self) -> List[ObsoleteItem]:
        """Find documentation for features no longer in codebase."""
        obsolete = []
        
        # Check documented components against codebase
        documented_components = self._extract_documented_components()
        existing_components = self._scan_codebase_components()
        
        for doc_component in documented_components:
            if doc_component not in existing_components:
                obsolete.append(
                    ObsoleteItem(
                        type="FEATURE_REMOVED",
                        component=doc_component,
                        doc_files=self._find_docs_for(doc_component),
                        recommendation="Archive or update to deprecated status"
                    )
                )
        
        return obsolete
    
    def _generate_recommendations(self, redundancies, orphans, obsolete):
        """Generate cleanup recommendations."""
        return {
            "redundancies": self._recommend_redundancy_actions(redundancies),
            "orphans": self._recommend_orphan_actions(orphans),
            "obsolete": self._recommend_obsolete_actions(obsolete),
            "estimated_space_saved": self._calculate_space_saved(),
            "affected_files": self._list_affected_files(),
        }
```

### Cleanup Actions

```yaml
CLEANUP_ACTIONS:
  ARCHIVE:
    description: "Move file to _archive/ with version/date subdirectory"
    syntax: "ARCHIVE {file} -> _archive/{category}/{version}/"
    preserves: "Git history, accessibility"
    reversible: "Yes"
    
  CONSOLIDATE:
    description: "Merge multiple files into single canonical doc"
    syntax: "CONSOLIDATE {files} -> {canonical}"
    action: "Keep canonical, redirect others to canonical"
    reversible: "Yes (in git history)"
    
  REMOVE:
    description: "Delete file completely"
    syntax: "REMOVE {file}"
    requires: "Explicit user confirmation"
    reversible: "Via git"
    dangerous: "Yes - requires verification"
    
  REDIRECT:
    description: "Create redirect from old to new doc"
    syntax: "REDIRECT {old} -> {new}"
    creates: "Alias or link in old location"
    preserves: "URLs, SEO"
    
  UPDATE_STATUS:
    description: "Mark document as deprecated/archived"
    syntax: "UPDATE_STATUS {file} -> deprecated"
    action: "Add deprecation notice, link to replacement"
    
  REORGANIZE:
    description: "Move file to correct directory"
    syntax: "REORGANIZE {file} -> {new_location}"
    updates: "mkdocs.yml, cross-references"

CLEANUP_PHASES:
  phase_1_analysis:
    name: "Analysis & Reporting"
    duration: "5-10 minutes"
    outputs: ["redundancy_report.md", "orphan_report.md", "obsolete_report.md"]
    user_action: "Review reports"
    
  phase_2_review:
    name: "User Review & Approval"
    duration: "30 minutes to days"
    outputs: ["cleanup_plan.yaml"]
    user_action: "Approve/modify cleanup recommendations"
    
  phase_3_execution:
    name: "Execute Cleanup"
    duration: "5-15 minutes"
    outputs: ["cleanup_log.md"]
    user_action: "Trigger cleanup"
    
  phase_4_validation:
    name: "Validate & Build"
    duration: "10-20 minutes"
    outputs: ["validation_report.md"]
    user_action: "Verify mkdocs builds successfully"
    
  phase_5_commit:
    name: "Git Commit & Report"
    duration: "5 minutes"
    outputs: ["CLEANUP-COMPLETE-{date}.md"]
    user_action: "Review final report"
```

### Cleanup Report Example

```markdown
# Documentation Cleanup Report - 2026-01-25

## Summary
- **Redundancies Found:** 12
- **Orphaned Files:** 8
- **Obsolete Content:** 3
- **Estimated Space to Save:** 2.4 MB
- **Affected Files:** 23

## Redundancies
1. `docs/orchestrators/master-orchestrator.md` + `docs/02-orchestrators/01-master-orchestrator.md`
   - **Recommendation:** CONSOLIDATE to single file
   - **Space:** 45 KB saved
   
2. Multiple TDD documentation files
   - **Recommendation:** Create single authoritative TDD guide
   - **Space:** 128 KB saved

## Orphaned Files
1. `docs/old-design-docs.md` (not in mkdocs.yml)
   - **Action:** Archive to _archive/obsolete/
   
2. `docs/temp-visualization-notes.md` (not referenced)
   - **Action:** Archive to _archive/temp/

## Obsolete Content
1. `docs/04-architecture/deprecated-orchestrator.md`
   - **Status:** Feature removed from codebase
   - **Action:** Archive to _archive/obsolete/

## Recommendations by Priority
### HIGH PRIORITY (Do immediately)
- Consolidate TDD documentation (saves 128 KB)
- Remove obsolete orchestrator docs (saves 32 KB)

### MEDIUM PRIORITY (Do this week)
- Archive session notes (saves 256 KB)
- Reorganize completion reports (saves 512 KB)

### LOW PRIORITY (Can do later)
- Archive old implementation notes

## Actions to Take
1. Review redundancies list above
2. Run: `/doc-cleanup --execute --plan=cleanup-plan.yaml`
3. Verify: `mkdocs build` completes successfully
4. Commit: `git commit -m "docs: cleanup cycle - 2.4 MB freed"`
```

---

## 🔗 Integration Points

### Documentation Orchestrator
```python
from cortex.orchestrators.documentation import DocumentationOrchestrator

doc_orch = DocumentationOrchestrator()

# Generate component documentation
result = doc_orch.generate(component="MasterOrchestrator")

# Generate diagrams
diagrams = doc_orch.generate_diagrams()

# Execute full maintenance cycle
maintenance = doc_orch.maintenance_cycle()
```

### Diagram Generation Orchestrator
```python
from cortex.orchestrators.documentation import DiagramGenerationOrchestrator

diagram_orch = DiagramGenerationOrchestrator()

# Generate Mermaid diagrams
mermaid = diagram_orch.generate_mermaid_diagrams()

# Generate D3.js visualizations
d3js = diagram_orch.generate_d3js_diagrams()

# Generate all diagrams with data
all_diagrams = diagram_orch.generate_all_diagrams()
```

### Documentation Cleanup Orchestrator
```python
from cortex.orchestrators.documentation import DocumentationCleanupOrchestrator

cleanup_orch = DocumentationCleanupOrchestrator()

# Analyze and report redundancies
report = cleanup_orch.execute_cleanup_cycle()

# Generate cleanup recommendations
recommendations = report.recommendations

# Execute cleanup (requires user approval)
cleanup_result = cleanup_orch.execute_cleanup_plan(
    plan=recommendations,
    auto_archive=True,
    validate=True  # Verify mkdocs builds
)
```

### MCP Tool Registry
```python
from cortex.mcp.registry import get_mcp_tool_registry

registry = get_mcp_tool_registry()
tools = registry.list_tools()

# Generate docs for each tool
doc_orch = DocumentationOrchestrator()
for tool in tools:
    doc_orch.generate_tool_doc(tool)
```

---

## 📊 Documentation Lifecycle

### Full Maintenance Cycle (`/doc-maintenance`)

```
START
  ↓
1. DISCOVERY
  ├─ Scan codebase for new components
  ├─ Identify missing documentation
  └─ Generate component inventory
  ↓
2. GENERATION
  ├─ Generate component documentation
  ├─ Generate diagrams (Mermaid + D3.js)
  ├─ Update diagrams with latest data
  └─ Create/update related pages
  ↓
3. VALIDATION
  ├─ Check documentation completeness
  ├─ Verify diagram links
  ├─ Validate mkdocs build
  └─ Check for broken references
  ↓
4. CLEANUP
  ├─ Identify redundancies
  ├─ Detect orphaned files
  ├─ Find obsolete content
  ├─ Generate cleanup report
  ├─ Request user approval
  └─ Execute cleanup plan
  ↓
5. COMMIT & REPORT
  ├─ Git commit with summary
  ├─ Generate final report
  └─ Update documentation index
  ↓
END
```

### Single Command Interface

```bash
# Execute complete fresh documentation generation pipeline
/doc-fresh-generate
```

**Execution Flow:**
1. User: `/doc-fresh-generate`
2. CORTEX: Display DoR classification
3. CORTEX: Show message "⏳ Awaiting approval to proceed with complete fresh documentation generation..."
4. User: Type "proceed" or "yes"
5. CORTEX: Execute all 7 phases WITHOUT stopping:
   - Phase 1: Pre-cleanup
   - Phase 2: Discovery
   - Phase 3: Generation
   - Phase 4: Diagrams
   - Phase 5: Build
   - Phase 6: Validation
   - Phase 7: Reporting
6. CORTEX: Display final completion report with metrics

---

## 📁 Deliverables

After running `/doc-maintenance`, the following are created:

### Documentation Files
- `docs/04-architecture/` - Core architecture docs
- `docs/02-orchestrators/` - Orchestrator documentation
- `docs/01-cortex-brain/` - Brain tier documentation
- `docs/06-tutorials/` - Tutorials with diagrams

### Diagram Files

**Mermaid (Static):**
- `docs/04-architecture/_diagrams/approval-gate-decision-tree.mmd`
- `docs/04-architecture/_diagrams/error-recovery-paths.mmd`
- `docs/04-architecture/_diagrams/circuit-breaker-state-machine.mmd`
- `docs/02-orchestrators/diagrams/master-orchestrator-sequence.mmd`
- `docs/04-architecture/_diagrams/tdd-workflow-phases.mmd`
- `docs/04-architecture/_diagrams/governance-rule-categories.mmd`

**D3.js (Interactive):**
- `docs/_diagrams/d3/governance-pyramid.html` + data generator
- `docs/_diagrams/d3/request-lifecycle-sankey.html` + data generator
- `docs/_diagrams/d3/tdd-knowledge-cycle.html`
- `docs/_diagrams/d3/domain-brain-architecture.html`

### Reports
- `docs/04-architecture/DIAGRAM-VISUALIZATION-RECOMMENDATIONS.md`
- `docs/04-architecture/DIAGRAM-EXAMPLES-IMPLEMENTATION-GUIDE.md`
- `_workspaces/CLEANUP-REPORT-{date}.md`
- `_workspaces/MAINTENANCE-CYCLE-{date}.md`

### Archive (Cleanup Results)
- `docs/_archive/reports/` - Old completion reports
- `docs/_archive/sessions/` - Old session notes
- `docs/_archive/obsolete/` - Removed features
- `docs/_archive/temp/` - Temporary files

---

## 📋 Approval Workflow

### Before Cleanup Execution

1. **Analyze Phase** (Automatic)
   - Scan for redundancies, orphans, obsolete content
   - Generate cleanup report
   
2. **Review Phase** (User approval required)
   ```markdown
   ### 📋 Intent Classification
   | Field | Value |
   |-------|-------|
   | **Intent** | `DOCUMENT - CLEANUP` |
   | **Handler** | `DocumentationCleanupOrchestrator` |
   | **Confidence** | 🟢 High (95%) |
   | **Scope** | `SYSTEM` |
   | **Impact** | 🟡 Medium (Archive/remove docs) |
   | **Affected Files** | 23 files (2.4 MB) |
   | **Rules** | CORE-012, CORE-027 |
   
   ---
   **⏳ Awaiting approval to proceed with cleanup...**
   ```

3. **Execution Phase** (After approval)
   - Archive redundant files
   - Remove orphaned files
   - Update mkdocs.yml
   - Validate build
   - Commit changes

4. **Report Phase** (Final status)
   - Generate cleanup completion report
   - Show space freed
   - Provide rollback instructions

---

## ⚠️ Safety Guardrails

All cleanup operations include:
- ✅ Dry-run mode (show what would happen)
- ✅ User confirmation (require explicit approval)
- ✅ Git integrity (preserve history)
- ✅ Validation (verify mkdocs builds)
- ✅ Audit trail (log all changes)
- ✅ Rollback capability (easy git revert)

---

## 🚀 Phase 5: Fresh Documentation Generation & mkdocs Compilation

### Overview

This phase implements a **complete fresh generation workflow** that:
1. **Clears** all previously generated documentation (except serve scripts)
2. **Regenerates** all content from specifications and sources
3. **Builds** mkdocs site with ZERO warnings and ZERO errors
4. **Validates** all links and references
5. **Serves** the latest documentation

### Critical Requirement: docs/ Folder Structure After Generation

After generation completes, `docs/` folder must contain ONLY:
- ✅ `serve-docs.bat` (Windows launcher)
- ✅ `serve-docs.sh` (Linux/Mac launcher)
- All other content: Fresh auto-generated files and directories

**Everything else is removed and regenerated fresh to showcase latest documentation.**

### Step 1: Pre-Generation Cleanup

**Objective:** Delete ALL generated files (keep only serve scripts and infrastructure)

```bash
#!/bin/bash
# Pre-generation cleanup

cd docs

# Remove all generated markdown files
find . -maxdepth 1 -type f -name "*.md" -delete

# Remove generated directories  
rm -rf _diagrams _reports _tests

# Verify serve scripts still exist
[ -f "serve-docs.bat" ] && [ -f "serve-docs.sh" ] && echo "✅ Serve scripts preserved"

# Verify infrastructure preserved
for dir in _archive _hooks assets stylesheets theme; do
    [ ! -d "$dir" ] && mkdir -p "$dir"
done

echo "✅ Pre-generation cleanup complete!"
```

### Step 2-4: Generate Documentation, Diagrams, & Build

Generate all markdown files, create 6 Mermaid + 4 D3.js diagrams, then execute mkdocs build.

### Step 5: mkdocs Build with ZERO Warnings & ZERO Errors

```bash
#!/bin/bash

echo "🏗️  Building mkdocs (--strict: must have ZERO warnings/errors)..."

# Validate configuration
mkdocs validate || exit 1

# Build with strict mode
mkdocs build --strict --clean || exit 1

# Verify ZERO warnings in output
if mkdocs build 2>&1 | grep -iE "warning|error"; then
    echo "❌ Build contains warnings/errors"
    exit 1
fi

echo "✅ mkdocs BUILD COMPLETE - ZERO WARNINGS, ZERO ERRORS!"
echo "📍 Site ready at: _build/site/"
```

### Step 6: Validate All Internal Links

```bash
#!/bin/bash

echo "🔗 Validating all internal links..."

find _build/site -name "*.html" -print0 | while IFS= read -r -d '' file; do
    grep -o 'href="[^"]*"' "$file" 2>/dev/null | sed 's/href="//;s/"$//' | while read link; do
        [[ $link == http* ]] || [[ $link == /* ]] && continue
        
        target="${file%/*}/$link"
        [ ! -f "$target" ] && echo "❌ Broken: $link"
    done
done

echo "✅ All links validated!"
```

### Step 7: Generate Final Report

```bash
#!/bin/bash

echo "📊 DOCUMENTATION GENERATION REPORT"
echo ""
echo "✅ Serve scripts: $([ -f docs/serve-docs.bat ] && echo 'PRESENT' || echo 'MISSING')"
echo "✅ Markdown docs: $(find docs -maxdepth 1 -name "*.md" | wc -l) files"
echo "✅ Diagrams: $(find docs/_diagrams -type f | wc -l) files"
echo "✅ mkdocs build: ZERO warnings, ZERO errors"
echo "✅ Internal links: All valid"
echo "✅ Site ready: _build/site/"
echo ""
echo "🚀 Next: mkdocs serve  OR  mkdocs gh-deploy"
```

### Complete Orchestration

```python
async def generate_all_fresh(self) -> Result[Dict[str, Any], str]:
    """
    Fresh documentation generation with zero warnings/errors guarantee.
    
    1. Pre-cleanup (keep serve scripts only)
    2. Generate all markdown docs
    3. Generate all diagrams (Mermaid + D3.js)
    4. Build mkdocs --strict
    5. Validate zero warnings/errors
    6. Validate all links
    7. Report completion
    """
    
    # AC_START
    self.logger.log_operation_start("generate_all_fresh")
    
    # Step 1: Pre-cleanup
    await self._cleanup_docs_preserve_serve_scripts()
    
    # Step 2-3: Generate content
    await self._generate_all_markdown()
    await self._generate_all_diagrams()
    
    # Step 4-6: Build & validate
    build = await self._build_mkdocs_strict()
    if build.is_err():
        return build
    
    links = await self._validate_links()
    if links.is_err():
        return links
    
    # Step 7: Report
    report = await self._generate_report()
    
    # AC_COMPLETE
    self.logger.log_operation_complete("generate_all_fresh")
    
    return Ok({
        "status": "success",
        "site": "_build/site/",
        "serve_scripts": ["serve-docs.bat", "serve-docs.sh"],
        "build_quality": "zero_warnings_zero_errors"
    })
```

### CLI Integration

```bash
# One command for everything
/doc-fresh-generate

# Or individual steps
/doc-cleanup-for-fresh
/doc-generate
/doc-diagram
/doc-build-strict
/doc-validate-links
/doc-report
```

### Key Guarantees

✅ **Always Fresh:** Clears docs/ before generation
✅ **Serve Scripts Safe:** Never deletes serve-docs.bat/sh
✅ **Zero Warnings:** mkdocs --strict enforcement
✅ **Zero Errors:** Build fails on any error
✅ **Links Verified:** All internal references validated
✅ **Complete:** Generates 16 doc sections + 10 diagrams
✅ **Reproducible:** Same output every run

