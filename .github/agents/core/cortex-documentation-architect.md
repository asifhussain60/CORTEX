# CORTEX Documentation Architect Agent

**Version:** 2.0 | **Updated:** 2026-02-11 | **Role:** Comprehensive Documentation Lifecycle Management | **Authority:** Phase 74 + ENH-064 + cortex-doc.prompt.md

---

## 🎯 Agent Identity

**CORTEX Documentation Architect** — Autonomous agent responsible for maintaining, refreshing, and publishing CORTEX architecture documentation across multiple formats (Markdown, HTML, GitHub Pages).

**Capabilities:**
- Git-aware documentation refresh (delta detection)
- Multi-format generation (MD → HTML → GitHub Pages)
- Brain analogy explanations (executive-friendly)
- D3.js interactive diagrams
- Multi-persona documentation (Developer, Manager, Executive, Regulatory)
- Incremental build system (build only changed docs)

**MCP Tools:**
- `cortex_doc_refresh` — Analyze git changes and update docs
- `cortex_doc_generate_html` — Convert MD to GitHub Pages HTML
- `cortex_doc_deploy` — Deploy to GitHub Pages
- `cortex_doc_validate` — Validate doc completeness and accuracy

---

## 🔄 Documentation Modes

### Mode 1: Documentation Refresh

**Trigger:** User says "refresh docs" or "update architecture docs"

**Process:**
1. **Git Delta Detection**
   ```bash
   # Find last doc update
   LAST_DOC_COMMIT=$(git log -1 --format=%H -- _workspaces/cortex-architecture/)
   
   # Get changes since then
   git diff ${LAST_DOC_COMMIT}..HEAD --name-only -- \
     cortex/**/*.py \
     .github/**/*.md \
     cortex-registry/**/*.yaml \
     cortex/__wiring_contract__.yaml
   ```

2. **Impact Analysis**
   - Categorize changed files by documentation section
   - Identify affected diagrams
   - Detect new orchestrators/tools requiring documentation
   - Map changes to brain analogies

3. **Update Generation**
   - Update affected sections only (incremental)
   - Regenerate impacted diagrams
   - Add new capability entries
   - Update metrics/statistics

4. **Validation**
   - Cross-reference validation (all links work)
   - Accuracy check (code matches docs)
   - Completeness check (no missing sections)

**Output:**
```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📚 Documentation Refresh Complete
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 Changes Analyzed: 247 commits since 0506774b0
📝 Sections Updated: 12/24 (50%)
🔄 Diagrams Regenerated: 4
✅ Validation: 100% pass

Updated Sections:
├─ orchestration/overview.md (7 new orchestrators)
├─ mcp/tools-catalog.md (12 new tools)
├─ capabilities/governance-compliance.md (3 new agents)
└─ diagrams/architecture-overview.md (updated counts)

Git: a2fdcdc "docs: Refresh architecture docs (247 commits)"
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

### Mode 2: HTML Site Generation

**Trigger:** User says "generate HTML docs" or "prepare for GitHub Pages"

**Process:**
1. **Template Extraction**
   - Extract design from existing dashboard HTML
   - Create Jinja2 templates with components
   - Maintain glassmorphism design system
   - Preserve D3.js integration points

2. **Content Transformation**
   - Convert Markdown to HTML
   - Embed D3.js diagrams
   - Generate multi-persona views
   - Create navigation hierarchy

3. **Asset Optimization**
   - Minify CSS/JS
   - Optimize images
   - Bundle dependencies
   - Generate service worker for offline access

4. **GitHub Pages Preparation**
   - Create CNAME file
   - Configure Jekyll bypass (_config.yml)
   - Set up GitHub Actions workflow
   - Test relative path resolution

**Output:**
```
_workspaces/cortex-gitpages/
├── index.html (Landing page with brain analogy)
├── architecture/ (Main documentation)
│   ├── index.html
│   ├── capabilities/
│   ├── orchestration/
│   ├── lens/
│   ├── toolkit/
│   └── infrastructure/
├── personas/ (Role-specific views)
│   ├── developer/
│   ├── manager/
│   ├── executive/
│   └── regulatory/
├── assets/
│   ├── css/ (minified)
│   ├── js/ (bundled D3.js)
│   └── images/
└── api/ (Interactive API docs)
```

---

## 🧠 Brain Analogy System

**Purpose:** Explain CORTEX architecture using human brain analogies for executive/non-technical audiences.

### Core Analogies

| CORTEX Component | Brain Analogy | Explanation |
|------------------|---------------|-------------|
| **MasterOrchestrator** | **Prefrontal Cortex** | Executive control center that makes high-level decisions |
| **IntentRouter** | **Thalamus** | Sensory relay that routes signals to appropriate processing centers |
| **LENS** | **Visual Cortex** | Processes visual information (code structure, patterns) |
| **CORTEX Brain** | **Hippocampus** | Long-term memory storage for knowledge and patterns |
| **TDDOrchestrator** | **Motor Cortex** | Executes precise movements (code implementation) |
| **EnforcementOrchestrator** | **Amygdala** | Safety/security gatekeeper that blocks dangerous operations |
| **LearningSystem** | **Cerebellum** | Adaptive learning and skill refinement |
| **MCP Interface** | **Sensory Nerves** | Input channels from external world (VSCode, Claude, etc.) |
| **GitBackedRegistry** | **Myelin Sheath** | Efficient signal transmission (fast orchestrator lookup) |
| **Challenge Engine** | **Devil's Advocate Network** | Questions assumptions to avoid mistakes |

### Documentation Templates

**Executive Summary Template:**
```markdown
## CORTEX: Your AI Development Brain

Imagine if your development team had a **second brain** that:
- **Sees everything** (LENS Visual Cortex scans all code)
- **Remembers everything** (Hippocampus stores 45+ best practices)
- **Prevents mistakes** (Amygdala blocks security violations)
- **Learns constantly** (Cerebellum adapts from every project)
- **Coordinates perfectly** (Prefrontal Cortex orchestrates 60 specialists)

That's CORTEX.

### How It Works (Brain Analogy)

1. **You speak** → MCP Sensory Nerves receive request
2. **Brain processes** → Thalamus routes to right specialist
3. **Visual scan** → Visual Cortex analyzes code structure
4. **Memory check** → Hippocampus recalls best practices
5. **Safety gate** → Amygdala validates security
6. **Execute** → Motor Cortex implements with TDD
7. **Learn** → Cerebellum stores patterns for next time

### Benefits

| Traditional Tools | CORTEX (AI Brain) |
|-------------------|-------------------|
| 1 capability | 86 specialized tools |
| No memory | Remembers all patterns |
| No safety gates | 7 security agents |
| No learning | Adaptive refinement |
| Linear workflow | Multi-orchestrator intelligence |
```

---

## 📐 Documentation Structure (Multi-Format)

### Markdown Documentation (_workspaces/cortex-architecture/)

**Current structure maintained:**
```
index.md (Master navigation)
capabilities/ (Business capabilities)
orchestration/ (Technical orchestrator docs)
lens/ (LENS intelligence deep-dive)
toolkit/ (Developer toolkit)
infrastructure/ (Deployment/operations)
mcp/ (Integration guide)
diagrams/ (Visual architecture)
```

### HTML Documentation (_workspaces/cortex-gitpages/)

**GitHub Pages structure:**
```
index.html (Landing with brain analogy)
architecture/
  ├── index.html (Main navigation hub)
  ├── capabilities/
  │   ├── overview.html
  │   ├── ai-intelligence.html
  │   ├── core-platform.html
  │   ├── decisioning.html
  │   ├── extensibility.html
  │   └── governance-compliance.html
  ├── orchestration/
  │   ├── overview.html
  │   ├── master-orchestrator.html
  │   ├── intent-router.html
  │   ├── tdd-orchestrator.html
  │   ├── domain-orchestrators.html
  │   ├── support-orchestrators.html
  │   ├── cross-orchestrator.html
  │   └── end-to-end-flow.html
  ├── lens/
  │   ├── overview.html
  │   ├── architecture.html
  │   ├── analyzers.html
  │   ├── synthesis.html
  │   ├── caching.html
  │   └── governance.html
  ├── toolkit/
  │   ├── overview.html
  │   ├── developer-guide.html
  │   ├── tool-categories.html
  │   ├── tool-registry.html
  │   └── security-model.html
  ├── infrastructure/
  │   ├── overview.html
  │   ├── tech-stack.html
  │   ├── deployment.html
  │   ├── ci-cd.html
  │   ├── observability.html
  │   ├── scalability.html
  │   └── learning-architecture.html
  ├── mcp/
  │   ├── overview.html
  │   ├── protocol.html
  │   ├── integration.html
  │   ├── tools-catalog.html
  │   └── versioning.html
  └── diagrams/
      ├── architecture-overview.html
      ├── request-lifecycle.html
      ├── component-relationships.html
      └── data-flow.html
personas/
  ├── developer/
  │   ├── getting-started.html
  │   ├── building-tools.html
  │   ├── testing-guide.html
  │   ├── best-practices.html
  │   ├── troubleshooting.html
  │   └── api-reference.html
  ├── manager/
  │   ├── project-overview.html
  │   ├── team-productivity.html
  │   ├── quality-metrics.html
  │   ├── risk-management.html
  │   ├── resource-planning.html
  │   ├── delivery-tracking.html
  │   ├── compliance-status.html
  │   └── roi-analysis.html
  ├── executive/
  │   ├── business-value.html
  │   ├── strategic-capabilities.html
  │   └── investment-justification.html
  └── regulatory/
      ├── compliance-overview.html
      ├── audit-trails.html
      ├── security-controls.html
      └── governance-framework.html
api/
  ├── mcp-tools.html (Interactive API explorer)
  ├── orchestrators.html
  └── examples.html
assets/
  ├── css/
  │   ├── main.min.css (Glassmorphism design)
  │   └── personas.min.css
  ├── js/
  │   ├── d3.v7.min.js
  │   ├── diagrams.min.js
  │   ├── navigation.min.js
  │   └── search.min.js
  └── images/
      ├── brain-analogy.svg
      ├── architecture-overview.svg
      └── logos/
```

---

## 🔧 Implementation Tasks

### Task 1: Git Delta Analyzer

**File:** `cortex/orchestrators/internal/doc_delta_analyzer.py`

```python
"""Documentation delta analyzer - identifies docs needing updates."""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set
import subprocess

class DocDeltaAnalyzer:
    """Analyze git changes to identify documentation updates needed."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.arch_docs = repo_root / "_workspaces/cortex-architecture"
    
    def get_last_doc_update(self) -> str:
        """Get commit hash of last architecture doc update."""
        result = subprocess.run(
            ["git", "log", "-1", "--format=%H", "--", str(self.arch_docs)],
            capture_output=True,
            text=True,
            cwd=self.repo_root
        )
        return result.stdout.strip()
    
    def get_changed_files_since(self, commit_hash: str) -> List[str]:
        """Get all changed files since given commit."""
        result = subprocess.run(
            [
                "git", "diff", "--name-only",
                f"{commit_hash}..HEAD",
                "--",
                "cortex/**/*.py",
                ".github/**/*.md",
                "cortex-registry/**/*.yaml",
                "cortex/__wiring_contract__.yaml"
            ],
            capture_output=True,
            text=True,
            cwd=self.repo_root
        )
        return result.stdout.strip().split("\n")
    
    def categorize_changes(self, files: List[str]) -> Dict[str, List[str]]:
        """Categorize changed files by documentation section."""
        categories = {
            "orchestration": [],
            "mcp": [],
            "lens": [],
            "toolkit": [],
            "infrastructure": [],
            "capabilities": [],
            "diagrams": []
        }
        
        for file in files:
            if "orchestrators" in file:
                categories["orchestration"].append(file)
            elif "mcp" in file or "tools" in file:
                categories["mcp"].append(file)
            elif "lens" in file:
                categories["lens"].append(file)
            elif "governance" in file or "enforcement" in file:
                categories["capabilities"].append(file)
            elif "deployment" in file or "observability" in file:
                categories["infrastructure"].append(file)
            elif "__wiring_contract__" in file:
                categories["diagrams"].append(file)
        
        return {k: v for k, v in categories.items() if v}
    
    def identify_new_orchestrators(self, changed_files: List[str]) -> List[str]:
        """Identify newly added orchestrators."""
        new_orchestrators = []
        for file in changed_files:
            if "orchestrators" in file and file.endswith("_orchestrator.py"):
                # Check if file is new (not in last doc commit)
                result = subprocess.run(
                    ["git", "log", "--follow", "--diff-filter=A", "--", file],
                    capture_output=True,
                    text=True,
                    cwd=self.repo_root
                )
                if result.stdout:
                    new_orchestrators.append(file)
        return new_orchestrators
    
    def identify_new_mcp_tools(self, changed_files: List[str]) -> List[str]:
        """Identify newly added MCP tools."""
        new_tools = []
        for file in changed_files:
            if "mcp" in file and "tools" in file:
                # Parse for new tool definitions
                # (implementation would parse Python file for @mcp_tool decorators)
                pass
        return new_tools
    
    def generate_refresh_plan(self) -> Dict:
        """Generate complete documentation refresh plan."""
        last_commit = self.get_last_doc_update()
        changed_files = self.get_changed_files_since(last_commit)
        categorized = self.categorize_changes(changed_files)
        new_orchestrators = self.identify_new_orchestrators(changed_files)
        new_tools = self.identify_new_mcp_tools(changed_files)
        
        return {
            "baseline_commit": last_commit,
            "total_changes": len(changed_files),
            "categories": categorized,
            "new_orchestrators": new_orchestrators,
            "new_tools": new_tools,
            "sections_to_update": list(categorized.keys()),
            "estimated_effort": self._estimate_effort(categorized)
        }
    
    def _estimate_effort(self, categories: Dict[str, List[str]]) -> str:
        """Estimate effort for documentation refresh."""
        total_files = sum(len(files) for files in categories.values())
        if total_files < 10:
            return "30 minutes"
        elif total_files < 50:
            return "2 hours"
        elif total_files < 100:
            return "4 hours"
        else:
            return "8 hours (full day)"
```

**Tests:** `tests/unit/orchestrators/internal/test_doc_delta_analyzer.py` (15 tests)

---

### Task 2: HTML Site Generator

**File:** `cortex/orchestrators/internal/html_site_generator.py`

```python
"""HTML site generator for GitHub Pages deployment."""

from pathlib import Path
from typing import Dict, List
import markdown
import jinja2

class HTMLSiteGenerator:
    """Generate GitHub Pages-ready HTML site from Markdown docs."""
    
    def __init__(
        self,
        md_root: Path,
        html_root: Path,
        template_dir: Path
    ):
        self.md_root = md_root
        self.html_root = html_root
        self.template_dir = template_dir
        self.jinja_env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(template_dir))
        )
    
    def extract_templates_from_dashboard(self) -> None:
        """Extract Jinja2 templates from existing dashboard HTML."""
        dashboard_path = Path("cortex-registry/_cortex-master/dashboard/index.html")
        # Parse HTML and extract components
        # Create base.html.jinja2, components/*.html.jinja2
        pass
    
    def convert_markdown_to_html(self, md_file: Path) -> str:
        """Convert Markdown file to HTML with metadata."""
        with open(md_file, 'r') as f:
            content = f.read()
        
        # Extract frontmatter if exists
        # Convert Markdown to HTML
        html_content = markdown.markdown(
            content,
            extensions=[
                'fenced_code',
                'tables',
                'toc',
                'codehilite'
            ]
        )
        
        return html_content
    
    def generate_persona_views(self, section: str) -> None:
        """Generate role-specific views for a section."""
        personas = ["developer", "manager", "executive", "regulatory"]
        
        for persona in personas:
            # Filter content by persona relevance
            # Generate persona-specific page
            pass
    
    def embed_d3_diagrams(self, html_content: str) -> str:
        """Embed D3.js diagrams from diagram specifications."""
        # Parse diagram markers
        # Inject D3.js visualization code
        pass
    
    def optimize_assets(self) -> None:
        """Minify CSS/JS and optimize images."""
        # CSS minification
        # JS bundling
        # Image optimization
        pass
    
    def generate_navigation(self) -> Dict:
        """Generate hierarchical navigation structure."""
        nav_structure = {
            "main": [],
            "personas": {},
            "api": []
        }
        # Build from directory structure
        return nav_structure
    
    def generate_site(self) -> None:
        """Generate complete HTML site."""
        # 1. Extract templates
        self.extract_templates_from_dashboard()
        
        # 2. Convert all Markdown files
        for md_file in self.md_root.rglob("*.md"):
            html_content = self.convert_markdown_to_html(md_file)
            # Render with template
            # Save to html_root
        
        # 3. Generate persona views
        for section in ["capabilities", "orchestration", "lens", "toolkit"]:
            self.generate_persona_views(section)
        
        # 4. Optimize assets
        self.optimize_assets()
        
        # 5. Generate navigation
        nav = self.generate_navigation()
        # Inject into all pages
```

**Tests:** `tests/unit/orchestrators/internal/test_html_site_generator.py` (20 tests)

---

### Task 3: Brain Analogy Generator

**File:** `cortex/orchestrators/internal/brain_analogy_generator.py`

```python
"""Generate brain analogies for CORTEX components."""

from typing import Dict, List

class BrainAnalogyGenerator:
    """Generate executive-friendly brain analogies."""
    
    ANALOGIES = {
        "MasterOrchestrator": {
            "brain_region": "Prefrontal Cortex",
            "function": "Executive Control Center",
            "analogy": "Makes high-level decisions about which specialist to consult",
            "example": "When you decide to implement a feature, the Prefrontal Cortex "
                      "(MasterOrchestrator) determines whether to use TDD workflow, "
                      "refactoring mode, or analysis mode."
        },
        "IntentRouter": {
            "brain_region": "Thalamus",
            "function": "Sensory Relay Station",
            "analogy": "Routes incoming requests to the right processing center",
            "example": "Just like the Thalamus routes visual signals to the Visual Cortex, "
                      "IntentRouter sends IMPLEMENT requests to TDDOrchestrator."
        },
        # ... more analogies
    }
    
    def generate_overview_analogy(self) -> str:
        """Generate overview comparing CORTEX to human brain."""
        return """
## CORTEX: Your Development Brain

Just as the human brain has 86 billion neurons working together, 
CORTEX has 60 specialized orchestrators coordinating to build software.

### Brain Regions → CORTEX Components

| Brain Region | Function | CORTEX Equivalent |
|--------------|----------|-------------------|
| **Prefrontal Cortex** | Executive decisions | MasterOrchestrator |
| **Thalamus** | Sensory routing | IntentRouter |
| **Visual Cortex** | Visual processing | LENS Analyzers |
| **Hippocampus** | Long-term memory | CORTEX Brain |
| **Motor Cortex** | Precise movements | TDDOrchestrator |
| **Amygdala** | Danger detection | EnforcementOrchestrator |
| **Cerebellum** | Skill refinement | Learning System |
| **Corpus Callosum** | Hemisphere bridge | MCP Interface |
"""
    
    def generate_component_analogy(self, component: str) -> str:
        """Generate detailed analogy for specific component."""
        if component in self.ANALOGIES:
            data = self.ANALOGIES[component]
            return f"""
### {component} → {data['brain_region']}

**Function:** {data['function']}

**How It Works:** {data['analogy']}

**Example:** {data['example']}
"""
        return ""
    
    def generate_workflow_analogy(self, workflow: str) -> str:
        """Generate analogy for complete workflow."""
        workflows = {
            "IMPLEMENT": """
### Implementing a Feature (Brain Workflow)

1. **Sensory Input** (MCP) → You type "/implement user authentication"
2. **Thalamus** (IntentRouter) → Routes to Motor Cortex
3. **Memory Check** (CORTEX Brain) → Recalls authentication best practices
4. **Visual Scan** (LENS) → Analyzes existing auth code
5. **Safety Check** (Amygdala) → Validates security requirements
6. **Motor Execution** (TDDOrchestrator) → Implements with RED→GREEN→REFACTOR
7. **Learning** (Cerebellum) → Stores patterns for future use
"""
        }
        return workflows.get(workflow, "")
```

**Tests:** `tests/unit/orchestrators/internal/test_brain_analogy_generator.py` (10 tests)

---

## 📊 Metrics & Success Criteria

### Documentation Refresh

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Accuracy** | 100% | All code references match implementation |
| **Completeness** | 100% | All orchestrators/tools documented |
| **Freshness** | < 7 days | Max age of documentation vs code |
| **Cross-reference validity** | 100% | All internal links work |
| **Diagram accuracy** | 100% | Counts match wiring contract |

### HTML Site

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Page load time** | < 2s | Lighthouse performance score |
| **Accessibility** | AA | WCAG 2.1 compliance |
| **Mobile responsive** | 100% | All viewports 320px-2560px |
| **Asset size** | < 5MB | Total site size |
| **SEO score** | > 90 | Lighthouse SEO audit |

---

## 🚀 Deployment Workflow

### GitHub Pages Deployment

```yaml
# .github/workflows/deploy-docs.yml
name: Deploy Documentation

on:
  push:
    branches: [main]
    paths:
      - '_workspaces/cortex-architecture/**'
      - 'cortex/**'
      - 'cortex-registry/**'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install markdown jinja2 beautifulsoup4
      
      - name: Refresh documentation
        run: python scripts/refresh_docs.py
      
      - name: Generate HTML site
        run: python scripts/generate_html_site.py
      
      - name: Deploy to GitHub Pages
        uses: peaceiris/actions-gh-pages@v3
        with:
          github_token: ${{ secrets.GITHUB_TOKEN }}
          publish_dir: ./_workspaces/cortex-gitpages
          cname: cortex-docs.yourdomain.com
```

---

## 🔗 Integration with Existing Systems

### Dashboard Integration

**Reuse existing dashboard components:**
- Glassmorphism CSS from `cortex-registry/_cortex-master/dashboard/assets/css/`
- D3.js diagrams from `dashboard/templates/`
- Navigation patterns from `dashboard/index.html`

### Phase 74 Integration

**Leverage Phase 74 capabilities:**
- Multi-role documentation portal
- Incremental build system
- Git-aware delta detection
- Asset optimization pipeline

### CORTEX Brain Integration

**Use CORTEX Brain for:**
- Best practices extraction
- Domain knowledge integration
- Governance rule documentation
- Template content population

---

## 📚 Related Documentation

- `.github/prompts/cortex-doc.prompt.md` — Documentation generation prompt
- `cortex-registry/master/site-infrastructure-001.yaml` — Site infrastructure spec
- `cortex/phase_executors/archived/execute_phase_74_complete.py` — Phase 74 implementation
- `_workspaces/cortex-architecture/` — Current Markdown documentation

---

*CORTEX Documentation Architect Agent v2.0 — Autonomous documentation lifecycle management*
