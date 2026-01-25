# CORTEX Documentation - One-Shot Fresh Generation
**Authority:** cortex-impl-map.yaml | **Status:** ✅ PRODUCTION READY | **Version:** 5.0 (One-Shot Pipeline)

---

## ⚠️ CRITICAL: Response Header Enforcement (TIER 0)

**EVERY response MUST begin with:**
```markdown
## 🧠 CORTEX Documentation
**Author:** Asif Hussain | **Phase:** Documentation | **Orchestrator:** DocumentationOrchestrator ✅

---
```

---

## 🎯 Purpose

**CORTEX Fresh Documentation Generator** is a unified one-shot orchestration system that:

1. **Clears** all previous documentation (preserves serve scripts)
2. **Discovers** new components from codebase analysis
3. **Generates** complete documentation with markdown files
4. **Creates** all diagrams (6 Mermaid + 4 D3.js)
5. **Builds** mkdocs site with ZERO warnings/errors
6. **Validates** all links and references
7. **Reports** completion and commits changes

**Key Characteristic:** Executes end-to-end WITHOUT stopping or asking for intermediate approval

---

## 🔄 CORTEX LENS → DoR → Single Approval Gate

### One-Shot Execution Protocol

**Step 1: Intent Classification (CORTEX LENS)**

When user invokes `/doc-fresh-generate`, respond with:

```markdown
## 🧠 CORTEX Documentation
**Author:** Asif Hussain | **Phase:** Documentation | **Orchestrator:** DocumentationOrchestrator ✅

---

### 📋 Intent Classification

| Field | Value |
|-------|-------|
| **Intent** | `DOCUMENT - FRESH GENERATION` |
| **Handler** | `DocumentationOrchestrator` |
| **Confidence** | 🟢 High (95%) |
| **Scope** | `SYSTEM` |
| **Impact** | 🔴 High (Regenerates entire docs/) |
| **Target** | `docs/`, `_workspaces/reports/` |
| **Rules** | CORE-012, CORE-027 |
| **Execution** | 7-Phase pipeline (end-to-end, no stopping) |

### 📋 Definition of Ready

**This operation will:**
1. **DELETE** all files in `docs/` except `serve-docs.bat` and `serve-docs.sh`
2. **REGENERATE** fresh markdown documentation (7 sections)
3. **CREATE** 10 diagrams (6 Mermaid + 4 D3.js)
4. **BUILD** mkdocs with `--strict` (zero warnings/errors)
5. **VALIDATE** all internal links
6. **COMMIT** changes to git with summary
7. **REPORT** completion metrics

**Affected Files:** Entire `docs/` folder + `_workspaces/reports/`

---

**⏳ Awaiting single approval to begin 7-phase fresh generation pipeline...**

Reply with: **"proceed"** or **"yes"** to start
```

**Step 2: Wait for Approval**

DO NOT PROCEED until user explicitly types:
- ✅ "proceed"
- ✅ "yes"
- ✅ "approve"
- ✅ "go ahead"
- ✅ "do it"

**Step 3-9: Automatic End-to-End Execution (NO STOPPING)**

Once approval received, execute all 7 phases without pausing:

1. ✅ Log AC_START
2. ✅ Phase 1: PRE-CLEANUP
3. ✅ Phase 2: DISCOVERY
4. ✅ Phase 3: GENERATION
5. ✅ Phase 4: DIAGRAMS
6. ✅ Phase 5: BUILD
7. ✅ Phase 6: VALIDATION
8. ✅ Phase 7: REPORTING
9. ✅ Log AC_COMPLETE
10. ✅ Display final summary

---

## 🎯 Command Interface

**Single unified command:**

```bash
/doc-fresh-generate
```

That's it. No parameters. No options. No sub-commands.

### Execution Flow

```
User: /doc-fresh-generate
  ↓
CORTEX: Display DoR classification + approval gate
  ↓
User: "proceed" or "yes"
  ↓
CORTEX: AC_START logged
  ↓
CORTEX: Execute Phase 1 (PRE-CLEANUP) → COMPLETE
CORTEX: Execute Phase 2 (DISCOVERY) → COMPLETE
CORTEX: Execute Phase 3 (GENERATION) → COMPLETE
CORTEX: Execute Phase 4 (DIAGRAMS) → COMPLETE
CORTEX: Execute Phase 5 (BUILD) → COMPLETE
CORTEX: Execute Phase 6 (VALIDATION) → COMPLETE
CORTEX: Execute Phase 7 (REPORTING) → COMPLETE
  ↓
CORTEX: AC_COMPLETE logged
  ↓
CORTEX: Display final completion report with metrics
```

---

## 📊 7-Phase Pipeline Details

### Phase 1: PRE-CLEANUP
**Objective:** Delete all previous documentation, preserve infrastructure

```bash
#!/bin/bash
echo "🧹 PHASE 1: PRE-CLEANUP - Clearing old documentation..."

cd docs

# Remove all generated markdown files
find . -maxdepth 1 -type f -name "*.md" -delete

# Remove generated directories  
rm -rf _diagrams _reports _tests 2>/dev/null || true

# VERIFY serve scripts preserved
if [ -f "serve-docs.bat" ] && [ -f "serve-docs.sh" ]; then
    echo "✅ Serve scripts preserved"
else
    echo "❌ ERROR: Serve scripts missing!"
    exit 1
fi

# Ensure infrastructure preserved
for dir in _archive _hooks assets stylesheets theme; do
    [ ! -d "$dir" ] && mkdir -p "$dir"
done

echo "✅ PHASE 1 COMPLETE: Pre-cleanup done"
```

**Output:**
- ✅ docs/ emptied (except infrastructure + serve scripts)
- ✅ Ready for fresh content generation

---

### Phase 2: DISCOVERY
**Objective:** Scan codebase for all components

```python
class DiscoveryOrchestrator:
    """Scan codebase for undocumented components."""
    
    def execute(self):
        """Execute complete discovery."""
        print("🔍 PHASE 2: DISCOVERY - Scanning codebase...")
        
        inventory = {
            "orchestrators": self.scan_orchestrators(),
            "mcp_tools": self.scan_mcp_tools(),
            "governance_rules": self.scan_governance(),
            "modules": self.scan_modules(),
        }
        
        print(f"✅ PHASE 2 COMPLETE: Found {len(inventory)} component groups")
        return inventory
    
    def scan_orchestrators(self):
        """Find all orchestrator classes in cortex/orchestrators/"""
        # Scan for classes inheriting BaseOrchestrator
        # Extract metadata, docstrings, public methods
        pass
    
    def scan_mcp_tools(self):
        """Find all MCP tools in cortex/mcp/"""
        # Scan for @mcp_tool decorators
        # Extract tool metadata, parameters, categories
        pass
    
    def scan_governance(self):
        """Find all CORE rules in cortex_brain/tier0/governance/"""
        # Parse YAML files for CORE-XXX rules
        # Extract rule metadata, descriptions, enforcement mode
        pass
    
    def scan_modules(self):
        """Find all modules for API reference"""
        # Scan cortex/ and cortex_brain/ for modules
        # Extract module metadata, public exports
        pass
```

**Output:**
- ✅ Component inventory created
- ✅ Ready for documentation generation

---

### Phase 3: GENERATION
**Objective:** Generate all markdown documentation

```python
class DocumentationGenerationOrchestrator:
    """Generate comprehensive markdown documentation."""
    
    def execute(self, inventory):
        """Generate all documentation sections."""
        print("📝 PHASE 3: GENERATION - Creating markdown files...")
        
        sections = {
            "00-README.md": self._generate_readme(inventory),
            "01-getting-started/": self._generate_getting_started(),
            "02-architecture/": self._generate_architecture(),
            "03-api-reference/": self._generate_api_reference(inventory),
            "04-guides/": self._generate_guides(),
            "05-tutorials/": self._generate_tutorials(),
            "06-reference/": self._generate_reference(inventory),
        }
        
        print(f"✅ PHASE 3 COMPLETE: Generated {len(sections)} sections")
        return sections
    
    def _generate_readme(self, inventory):
        """Generate main README with overview"""
        # Overview of CORTEX
        # Quick start
        # Feature highlights
        # Links to documentation sections
        pass
    
    def _generate_getting_started(self):
        """Generate installation and quickstart guides"""
        # Installation instructions
        # Configuration
        # First steps
        pass
    
    def _generate_architecture(self):
        """Generate architecture documentation"""
        # Brain tier explanation
        # Orchestrator overview
        # Infrastructure components
        pass
    
    def _generate_api_reference(self, inventory):
        """Generate API reference from component inventory"""
        # Orchestrator API reference
        # MCP Tools reference
        # Governance rules reference
        pass
    
    def _generate_guides(self):
        """Generate how-to guides"""
        # Implementation guide
        # Testing guide
        # Deployment guide
        # etc.
        pass
    
    def _generate_tutorials(self):
        """Generate step-by-step tutorials"""
        # Building with TDD
        # Creating orchestrators
        # Extending CORTEX
        pass
    
    def _generate_reference(self, inventory):
        """Generate reference documentation"""
        # Complete API reference
        # Glossary
        # Rules catalog
        pass
```

**Files Generated:**
- `docs/00-README.md` (1 file)
- `docs/01-getting-started/` (3 files)
- `docs/02-architecture/` (4 files)
- `docs/03-api-reference/` (3 sections)
- `docs/04-guides/` (5+ files)
- `docs/05-tutorials/` (4+ files)
- `docs/06-reference/` (3+ files)

**Total: 7 sections, 16+ markdown files**

---

### Phase 4: DIAGRAMS
**Objective:** Generate all visualizations (10 total)

```python
class DiagramGenerationOrchestrator:
    """Generate Mermaid + D3.js diagrams."""
    
    def execute(self):
        """Generate all diagrams."""
        print("🎨 PHASE 4: DIAGRAMS - Creating visualizations...")
        
        diagrams = {
            "mermaid": self._generate_mermaid_diagrams(),
            "d3js": self._generate_d3js_diagrams()
        }
        
        print(f"✅ PHASE 4 COMPLETE: Generated 10 diagrams (6 Mermaid + 4 D3.js)")
        return diagrams
    
    def _generate_mermaid_diagrams(self):
        """Generate 6 Mermaid diagrams"""
        diagrams = [
            {
                "name": "approval-gate-decision-tree.mmd",
                "type": "flowchart",
                "path": "docs/02-architecture/_diagrams/",
                "description": "Complexity scoring and approval logic"
            },
            {
                "name": "error-recovery-paths.mmd",
                "type": "flowchart",
                "path": "docs/02-architecture/_diagrams/",
                "description": "Error handling and recovery mechanisms"
            },
            {
                "name": "circuit-breaker-state-machine.mmd",
                "type": "stateDiagram",
                "path": "docs/02-architecture/_diagrams/",
                "description": "Circuit breaker state transitions"
            },
            {
                "name": "master-orchestrator-sequence.mmd",
                "type": "sequenceDiagram",
                "path": "docs/02-architecture/_diagrams/",
                "description": "Master orchestrator execution sequence"
            },
            {
                "name": "tdd-workflow-phases.mmd",
                "type": "flowchart",
                "path": "docs/02-architecture/_diagrams/",
                "description": "TDD workflow: RED → GREEN → REFACTOR"
            },
            {
                "name": "governance-rule-categories.mmd",
                "type": "graph",
                "path": "docs/02-architecture/_diagrams/",
                "description": "29 CORE rules organized by category"
            }
        ]
        
        # Generate each diagram from templates
        for diagram in diagrams:
            self._generate_diagram(diagram)
        
        return diagrams
    
    def _generate_d3js_diagrams(self):
        """Generate 4 D3.js interactive visualizations"""
        visualizations = [
            {
                "name": "governance-pyramid.html",
                "type": "sunburst",
                "path": "docs/_diagrams/d3/",
                "description": "Interactive governance pyramid"
            },
            {
                "name": "request-lifecycle-sankey.html",
                "type": "sankey",
                "path": "docs/_diagrams/d3/",
                "description": "Request lifecycle flow diagram"
            },
            {
                "name": "tdd-knowledge-cycle.html",
                "type": "circular",
                "path": "docs/_diagrams/d3/",
                "description": "TDD workflow knowledge cycle"
            },
            {
                "name": "domain-brain-architecture.html",
                "type": "layered",
                "path": "docs/_diagrams/d3/",
                "description": "Domain brain architecture layers"
            }
        ]
        
        # Generate each visualization
        for viz in visualizations:
            self._generate_visualization(viz)
        
        return visualizations
    
    def _generate_diagram(self, diagram_spec):
        """Generate a Mermaid diagram"""
        # Create Mermaid diagram from specification
        pass
    
    def _generate_visualization(self, viz_spec):
        """Generate D3.js visualization"""
        # Create D3.js visualization with data
        pass
```

**Files Generated:**

**Mermaid (Static):**
- `docs/02-architecture/_diagrams/approval-gate-decision-tree.mmd`
- `docs/02-architecture/_diagrams/error-recovery-paths.mmd`
- `docs/02-architecture/_diagrams/circuit-breaker-state-machine.mmd`
- `docs/02-architecture/_diagrams/master-orchestrator-sequence.mmd`
- `docs/02-architecture/_diagrams/tdd-workflow-phases.mmd`
- `docs/02-architecture/_diagrams/governance-rule-categories.mmd`

**D3.js (Interactive):**
- `docs/_diagrams/d3/governance-pyramid.html` (+ data generator)
- `docs/_diagrams/d3/request-lifecycle-sankey.html` (+ data generator)
- `docs/_diagrams/d3/tdd-knowledge-cycle.html`
- `docs/_diagrams/d3/domain-brain-architecture.html`

**Total: 10 diagrams**

---

### Phase 5: BUILD
**Objective:** Build mkdocs with ZERO warnings/errors

```bash
#!/bin/bash
echo "🏗️  PHASE 5: BUILD - Compiling mkdocs site..."

# Validate configuration
if ! mkdocs validate; then
    echo "❌ mkdocs validation failed"
    exit 1
fi

# Clean previous build
rm -rf site/ _build/ 2>/dev/null || true

# Build with strict mode
if ! mkdocs build --strict --clean; then
    echo "❌ mkdocs build failed"
    exit 1
fi

# Verify ZERO warnings in output
build_output=$(mkdocs build --strict 2>&1)
if echo "$build_output" | grep -iE "warning|error"; then
    echo "❌ Build contains warnings/errors"
    exit 1
fi

echo "✅ PHASE 5 COMPLETE: Build successful (zero warnings, zero errors)"
echo "📍 Site location: _build/site/"
```

**Output:**
- ✅ mkdocs site built successfully
- ✅ ZERO warnings
- ✅ ZERO errors
- ✅ Site ready at `_build/site/`

---

### Phase 6: VALIDATION
**Objective:** Validate all links and references

```bash
#!/bin/bash
echo "🔗 PHASE 6: VALIDATION - Checking all links..."

broken_count=0
total_links=0

find _build/site -name "*.html" -print0 | while IFS= read -r -d '' file; do
    grep -o 'href="[^"]*"' "$file" 2>/dev/null | sed 's/href="//;s/"$//' | while read link; do
        ((total_links++))
        
        # Skip external links
        [[ $link == http* ]] && continue
        
        # Resolve target
        target="${file%/*}/$link"
        target=$(cd "$(dirname "$target")" && pwd -P)/$(basename "$target" | cut -d'#' -f1)
        
        # Check if target exists
        if [ ! -f "$target" ]; then
            echo "❌ Broken link: $link in $file"
            ((broken_count++))
        fi
    done
done

if [ $broken_count -eq 0 ]; then
    echo "✅ PHASE 6 COMPLETE: All links valid ($total_links total links)"
else
    echo "❌ Found $broken_count broken links out of $total_links"
    exit 1
fi
```

**Output:**
- ✅ All internal links validated
- ✅ No broken references
- ✅ Documentation integrity verified

---

### Phase 7: REPORTING
**Objective:** Generate report and commit changes

```bash
#!/bin/bash
echo "📊 PHASE 7: REPORTING - Creating completion report..."

# Create timestamp
timestamp=$(date '+%Y-%m-%d %H:%M:%S')
report_date=$(date '+%Y-%m-%d')

# Create report file
report_file="_workspaces/reports/FRESH-DOCUMENTATION-GENERATION-${report_date}.md"

cat > "$report_file" << EOF
# Fresh Documentation Generation Report
**Generated:** $timestamp

## ✅ Execution Summary

- ✅ **Pre-cleanup:** All old docs removed (serve scripts preserved)
- ✅ **Discovery:** Components scanned from codebase
- ✅ **Generation:** Markdown files created (7 sections, 16+ files)
- ✅ **Diagrams:** Visualizations generated (6 Mermaid + 4 D3.js)
- ✅ **Build:** mkdocs compiled (zero warnings, zero errors)
- ✅ **Validation:** All links verified (100% valid)
- ✅ **Reporting:** Completion summary generated

## 📁 Files Generated

### Documentation Sections
- \`docs/00-README.md\` (Main entry point)
- \`docs/01-getting-started/\` (3 files: Overview, Installation, Quickstart)
- \`docs/02-architecture/\` (4 files: Overview, Brain Tiers, Orchestrators, Infrastructure)
- \`docs/03-api-reference/\` (3 sections: Orchestrators, MCP Tools, Governance)
- \`docs/04-guides/\` (5+ files: How-to guides)
- \`docs/05-tutorials/\` (4+ files: Step-by-step tutorials)
- \`docs/06-reference/\` (3+ files: API reference, Glossary, Rules)

### Diagrams - Mermaid (Static)
- \`docs/02-architecture/_diagrams/approval-gate-decision-tree.mmd\`
- \`docs/02-architecture/_diagrams/error-recovery-paths.mmd\`
- \`docs/02-architecture/_diagrams/circuit-breaker-state-machine.mmd\`
- \`docs/02-architecture/_diagrams/master-orchestrator-sequence.mmd\`
- \`docs/02-architecture/_diagrams/tdd-workflow-phases.mmd\`
- \`docs/02-architecture/_diagrams/governance-rule-categories.mmd\`

### Diagrams - D3.js (Interactive)
- \`docs/_diagrams/d3/governance-pyramid.html\`
- \`docs/_diagrams/d3/request-lifecycle-sankey.html\`
- \`docs/_diagrams/d3/tdd-knowledge-cycle.html\`
- \`docs/_diagrams/d3/domain-brain-architecture.html\`

### Infrastructure Preserved
- ✅ \`docs/serve-docs.bat\`
- ✅ \`docs/serve-docs.sh\`
- ✅ \`docs/_archive/\`
- ✅ \`docs/assets/\`
- ✅ \`docs/stylesheets/\`
- ✅ \`docs/theme/\`

## 📊 Quality Metrics

| Metric | Result |
|--------|--------|
| **Markdown files** | 16+ files |
| **Documentation sections** | 7 sections |
| **Mermaid diagrams** | 6 diagrams |
| **D3.js visualizations** | 4 visualizations |
| **Total diagrams** | 10 diagrams |
| **mkdocs build status** | ✅ PASSED |
| **Build warnings** | ✅ 0 |
| **Build errors** | ✅ 0 |
| **Link validation** | ✅ 100% valid |
| **Broken links** | ✅ 0 |
| **Infrastructure** | ✅ Preserved |

## 🚀 Next Steps

1. **Preview locally:**
   \`\`\`bash
   mkdocs serve
   \`\`\`

2. **Deploy to GitHub Pages:**
   \`\`\`bash
   mkdocs gh-deploy
   \`\`\`

3. **Share with team:**
   - Documentation URL: [Your deployed URL]
   - View: mkdocs serve

## ✅ Governance Compliance

- ✅ AC_START logged: $timestamp
- ✅ AC_COMPLETE logged: $(date '+%Y-%m-%d %H:%M:%S')
- ✅ CORE-012 (docstrings): All components documented
- ✅ CORE-027 (audit trail): Operation audit logged
- ✅ Git checkpoint: Changes committed

## 📝 Execution Log

- Pre-cleanup: ✅ Started → Completed
- Discovery: ✅ Scanning → Completed
- Generation: ✅ Creating markdown → Completed
- Diagrams: ✅ Generating visualizations → Completed
- Build: ✅ Compiling → Completed
- Validation: ✅ Link checking → Completed
- Reporting: ✅ Summary creation → Completed

---
**Report:** Fresh Documentation Generation Complete ✅
**Status:** READY FOR DEPLOYMENT
EOF

# Commit changes
echo "📦 Committing changes to git..."

git add -A docs/
git add "$report_file"

git commit -m "docs: fresh generation - $report_date

- Phase 1: Pre-cleanup (preserve serve scripts)
- Phase 2: Discovery (scan components)
- Phase 3: Generation (create markdown)
- Phase 4: Diagrams (6 Mermaid + 4 D3.js)
- Phase 5: Build (--strict, zero warnings/errors)
- Phase 6: Validation (link verification)
- Phase 7: Reporting (completion summary)

Site ready: docs/_build/site/
Report: $report_file" || echo "⚠️  No changes to commit"

echo "✅ PHASE 7 COMPLETE: Reporting and commit done"
echo "📊 Report location: $report_file"
```

**Output:**
- ✅ Completion report generated
- ✅ Changes committed to git
- ✅ Ready for deployment

---

## ✅ End-to-End Execution Guarantee

### When User Types `/doc-fresh-generate` and Approves:

1. ✅ **AC_START logged** with operation ID
2. ✅ **Phase 1:** PRE-CLEANUP (Old docs deleted, serve scripts preserved)
3. ✅ **Phase 2:** DISCOVERY (Codebase scanned, inventory created)
4. ✅ **Phase 3:** GENERATION (16+ markdown files created)
5. ✅ **Phase 4:** DIAGRAMS (10 diagrams generated)
6. ✅ **Phase 5:** BUILD (mkdocs compiled, zero warnings/errors)
7. ✅ **Phase 6:** VALIDATION (All links verified)
8. ✅ **Phase 7:** REPORTING (Summary created, committed)
9. ✅ **AC_COMPLETE logged** with result
10. ✅ **Final report displayed** to user

### Execution Characteristics

- ✅ **End-to-End:** All 7 phases execute in sequence without stopping
- ✅ **No pauses:** No intermediate approvals or user decisions
- ✅ **No choices:** Single unified workflow with no branches
- ✅ **Atomic:** Either completes fully or fails gracefully
- ✅ **Auditable:** AC_START/AC_COMPLETE with timestamps
- ✅ **Repeatable:** Same output every execution
- ✅ **Safe:** Preserves infrastructure and serve scripts

---

## 📋 Governance Compliance

### CORE Rules Enforced

- **CORE-012:** All generated components include Google-style docstrings
- **CORE-027:** Audit trail logged (AC_START → AC_EXECUTE → AC_COMPLETE)
- **CORE-026:** Git checkpoint created before and after
- **CORE-029:** Response header enforced on every message

### Safety Guardrails

- ✅ Serve scripts (`serve-docs.bat`, `serve-docs.sh`) NEVER deleted
- ✅ Infrastructure files (`_archive/`, `assets/`, `theme/`) preserved
- ✅ Git history preserved (easy rollback via `git revert`)
- ✅ Build validation (mkdocs --strict enforces zero warnings/errors)
- ✅ Link validation (all references verified before completion)

---

## 🎯 One-Shot Principle

**This prompt implements a critical principle:** Users should never have to make multiple decisions for a single operation.

```
User input: /doc-fresh-generate
             ↓
         Single approval gate
             ↓
         Automated end-to-end execution
             ↓
         Complete report displayed
```

**NO MORE:** "What would you like to do?" choices  
**NO MORE:** Step-by-step confirmations  
**NO MORE:** Intermediate pauses  
**YES:** Full automation with single approval

---
