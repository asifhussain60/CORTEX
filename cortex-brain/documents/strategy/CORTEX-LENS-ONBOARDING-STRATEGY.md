# CORTEX LENS & Onboarding Orchestrator Strategy

**Version:** 6.0.0  
**Date:** 2026-01-12  
**Author:** Asif Hussain + GitHub Copilot  
**Status:** ARCHITECTURAL DEFINITION  
**Phase Placement:** Phase 1.5 Enhancement (Between Phase 1 & Phase 2)

---

## 🎯 Vision (CORRECTED)

**CORTEX LENS is NOT a dashboard visualization tool.**

**CORTEX LENS is a universal, intelligent code analysis and reverse-engineering system that:**

1. **AST Scans** - Comprehensive Abstract Syntax Tree analysis across all supported languages
2. **Code Intelligence** - Extracts functions, classes, imports, dependencies, architecture patterns
3. **Knowledge Discovery** - Reverse-engineers codebase intent from:
   - User comments and docstrings
   - Git history and commit patterns  
   - Code structure and naming conventions
   - Architecture patterns and dependencies
4. **Domain Learning** - Captures company and domain-specific knowledge for future work
5. **Feeds the Brain** - Stores discovered knowledge in Tier 1 & 3 for reuse
6. **Universal Tool** - Exposes analyzers and crawlers via MCP for all orchestrators
7. **Foundation for Onboarding** - Used by Onboarding Orchestrator at project setup

**The Onboarding Orchestrator USES CORTEX LENS** to:
- Discover project structure and technology stack on first run
- Analyze git history and team patterns
- Build knowledge graphs for informed decisions
- Create initial CORTEX configuration
- Guide teams through interactive setup

---

## 🏗️ Architecture Overview

### Three-Tier Discovery Stack

```
┌─────────────────────────────────────────────────────────┐
│ LAYER 3: Onboarding Orchestrator (User-Facing)         │
│ - Interactive guided setup                             │
│ - Knowledge discovery flow                             │
│ - Configuration wizard                                 │
│ - Dashboard generation                                 │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ LAYER 2: CORTEX LENS (Intelligence Core)               │
│ - AST scanning (multi-language)                        │
│ - Code crawler framework                               │
│ - Reverse engineering engine                           │
│ - Knowledge extraction                                 │
│ - Pattern detection                                    │
│ - Dependency analysis                                  │
│ - Comment & commit analysis                            │
└─────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────┐
│ LAYER 1: MCP Tool Exposure (Framework Integration)     │
│ - AST Analyzer tools                                   │
│ - Crawler tools                                        │
│ - Comment Analyzer tool                                │
│ - Git History tool                                     │
│ - Knowledge Graph tool                                 │
│ - Domain Learner tool                                  │
└─────────────────────────────────────────────────────────┘
```

### Information Flow

```
User Project
     ↓
┌─ CORTEX LENS AST Crawlers ─┐
│ - Python analyzer           │
│ - JavaScript/TypeScript     │
│ - C# / Java analyzer        │
│ - SQL analyzer              │
│ - Comment extractor         │
└─────────────────────────────┘
     ↓↓↓↓↓↓
┌─ Code Analysis Results ────┐
│ - Architecture graph        │
│ - Dependency matrix         │
│ - Complexity metrics        │
│ - Hotspot detection         │
│ - Pattern library           │
└─────────────────────────────┘
     ↓
┌─ Knowledge Extraction ─────┐
│ + Git history analysis      │
│ + Team/ownership patterns   │
│ + Domain terminology        │
│ + Company practices found   │
└─────────────────────────────┘
     ↓
┌─ Store in CORTEX Brain ────┐
│ Tier 1: Company knowledge   │
│ Tier 3: Domain patterns     │
│ Audit trail: Full discovery │
└─────────────────────────────┘
     ↓
┌─ Onboarding Uses Results ──┐
│ - Generates dashboards      │
│ - Recommends practices      │
│ - Guides team setup         │
│ - Plans improvements        │
└─────────────────────────────┘
```

---

## 📊 CORTEX LENS Components (Detailed)

### Component 1: Universal AST Framework

**Purpose:** Parse code in all supported languages into unified structure

**Supported Languages:**
- Python (ast module - 90% confidence)
- JavaScript/TypeScript (esprima/babylon - 85% confidence)
- C# (Roslyn/.NET - 80% confidence)
- Java (tree-sitter - 80% confidence)
- Go (tree-sitter - 80% confidence)
- Rust (tree-sitter - 85% confidence)
- SQL (custom parser - 70% confidence)
- HTML/CSS (tree-sitter - 75% confidence)

**Outputs:**
```yaml
file_analysis:
  path: "src/orchestrators/planning.py"
  language: "python"
  lines_of_code: 1245
  complexity: 23
  
  classes:
    - name: "PlanningOrchestratorV5"
      methods: 18
      inherited_from: "BaseOrchestratorV4"
      docstring: "..."
  
  functions:
    - name: "_discover_context"
      parameters: 3
      returns: "List[str]"
      cyclomatic_complexity: 8
  
  imports:
    - module: "pathlib"
      type: "standard_library"
    - module: "cortex.orchestrators.planning"
      type: "internal"
  
  comments_and_docstrings:
    - type: "class_docstring"
      content: "..."
    - type: "function_docstring"
      content: "..."
```

### Component 2: Code Crawler Framework

**Purpose:** Traverse codebase extracting structured information

**Key Crawlers:**

1. **Architecture Crawler**
   - Maps module/package structure
   - Identifies entry points
   - Builds dependency graph
   - Detects circular dependencies
   - Output: `architecture.json`

2. **Comment Crawler**
   - Extracts all comments/docstrings
   - Classifies by category (TODO, FIXME, NOTE, etc.)
   - Analyzes sentiment and importance
   - Output: `comments-analysis.json`

3. **Tech Stack Crawler**
   - Analyzes package.json, requirements.txt, pom.xml, Cargo.toml, etc.
   - Detects frameworks and libraries
   - Identifies build tools and CI/CD
   - Maps database technologies
   - Output: `tech-stack.json`

4. **Complexity Crawler**
   - Calculates cyclomatic complexity per function
   - Identifies hotspots (high complexity files)
   - Measures nesting depth
   - Analyzes code duplication
   - Output: `complexity-metrics.json`

5. **Dependency Crawler**
   - Maps inter-file dependencies
   - Identifies missing modules
   - Detects unused imports
   - Analyzes external vendors
   - Output: `dependency-matrix.json`

### Component 3: Reverse Engineering Engine

**Purpose:** Infer codebase intent from structure, comments, patterns

**Capabilities:**

1. **Intent Inference**
   - Extracts purpose from function/class names
   - Analyzes docstrings and comments
   - Maps responsibilities
   - Identifies business logic

2. **Pattern Detection**
   - Design patterns used (MVC, Factory, Observer, etc.)
   - Architectural patterns (monolith, microservices, etc.)
   - Anti-patterns detected
   - Code style conventions

3. **Dependency Analysis**
   - Maps service-to-service calls
   - Identifies data flow
   - Detects tight coupling
   - Finds potential bottlenecks

4. **Domain Knowledge Extraction**
   - Business terminology from code
   - Domain-specific patterns
   - Company practices embedded in code
   - Implicit conventions

**Output: `reverse-engineering-report.json`**
```json
{
  "inferred_intent": "Multi-tenant project planning orchestrator",
  "architectural_pattern": "distributed_orchestration",
  "primary_responsibility": "coordinate_planning_phase",
  "domain_knowledge": {
    "terminology": ["phase", "checkpoint", "rollback", "evidence_bundle"],
    "patterns": ["checkpoint_pattern", "evidence_based_completion"],
    "company_practices": ["approval_gates", "tdd_enforcement"]
  }
}
```

### Component 4: Knowledge Graph Builder

**Purpose:** Build semantic representation of codebase

**Stores in:** `cortex-brain/tier1/{project-name}/knowledge-graph.yaml`

**Nodes:**
- Files (modules)
- Classes (entities)
- Functions (operations)
- Dependencies (relationships)
- Technologies (external)
- Patterns (structural)

**Edges:**
- Inheritance: Class A extends Class B
- Composition: Class A contains Class B
- Dependency: Function A calls Function B
- Uses: Module A imports Module B
- Implements: Class A implements Interface B
- Pattern: Function A uses Factory Pattern

**Enables:**
- Traversal queries (find all callers of a function)
- Impact analysis (what breaks if I change X?)
- Pattern suggestions (similar code elsewhere?)
- Risk assessment (critical path identification)

### Component 5: Domain Learner

**Purpose:** Capture company and domain-specific knowledge

**Learns:**
```yaml
company_knowledge:
  naming_conventions:
    - orchestrators: "*_orchestrator.py"
    - interfaces: "Base*.py"
    - utilities: "*_utils.py"
  
  architectural_patterns:
    - lifecycle_pattern:
        description: "State machine with transitions"
        components: [StateManager, LifecycleError, OrchestratorLifecycle]
    - evidence_pattern:
        description: "Prove completion with test evidence"
        components: [EvidenceBundle, CleanupEvidenceBundle, AuditLog]
  
  domain_terminology:
    - "AC-ID": "Acceptance Criteria Identifier"
    - "Evidence Bundle": "Proof of capability completion"
    - "Phase Gate": "100% completion checkpoint before next phase"
    - "Skull Rule": "Immutable governance constraint"

  team_practices:
    - "TDD enforcement": CORE-019
    - "No root-level plans": CORE-009
    - "Evidence-based status": Always use test results
    - "Audit logging": All operations tracked
```

**Stored in:** `cortex-brain/tier3/{domain}/patterns.yaml`

**Used by:** All future work in this domain

---

## 👥 Onboarding Orchestrator (Detailed)

### Purpose

Guide teams and projects through CORTEX adoption with intelligent discovery:

1. **Analyze** - CORTEX LENS discovers project structure
2. **Recommend** - Suggest practices based on what's found
3. **Configure** - Set up CORTEX with sensible defaults
4. **Learn** - Store discovered knowledge for future use
5. **Guide** - Interactive walkthrough of capabilities

### 10-Phase Execution Flow

| Phase | Name | Tool | Time | Output |
|-------|------|------|------|--------|
| 1 | **Project Metadata** | File Scanner | ~1-2s | File count, LOC, languages |
| 2 | **AST Analysis** | CORTEX LENS AST | ~5-10s | Architecture graph, complexity |
| 3 | **Git History** | Git Analyzer | ~5-15s | Commit patterns, authors, hotspots |
| 4 | **Tech Stack** | Tech Detector | ~2-5s | Frameworks, databases, CI/CD |
| 5 | **Code Quality** | Complexity Crawler | ~3-10s | Hotspots, code duplication |
| 6 | **Architecture** | Dependency Crawler | ~5-20s | Service map, coupling analysis |
| 7 | **Comments** | Comment Crawler | ~2-5s | TODO/FIXME count, domain terms |
| 8 | **Domain Learning** | Domain Learner | ~1-3s | Patterns, practices, terminology |
| 9 | **Parallel Collection** | All crawlers | ~8-20s | 6 JSON files simultaneously |
| 10 | **Dashboard Generate** | Renderer | ~2-5s | Interactive HTML dashboard |

### Two-Mode Operation

#### Production Mode (Embedded in User Project)
```
User's project/
├── cortex-brain/
│   ├── tier1/
│   │   └── {project-name}/
│   │       ├── knowledge-graph.yaml
│   │       ├── tech-stack.json
│   │       └── git-analysis.json
│   └── dashboards/
│       └── {project-name}/
│           └── index.html
```

#### Test/Demo Mode (Standalone CORTEX)
```
CORTEX/
├── cortex-brain/
│   ├── documents/
│   │   └── onboarded-apps/
│   │       └── {project-name}/
│   │           ├── tech-stack.json
│   │           └── analysis-report.html
```

### Output Files (7 Total)

```json
{
  "health-data.json": {
    "overall_score": 72,
    "status": "warning",
    "security_score": 85,
    "code_quality_score": 60,
    "architecture_score": 70,
    "tech_stack_score": 75
  },
  
  "tech-stack.json": {
    "languages": ["Python", "JavaScript", "SQL"],
    "frameworks": ["FastAPI", "React", "SQLAlchemy"],
    "databases": ["PostgreSQL"],
    "build_tools": ["npm", "pip", "docker"],
    "ci_cd": ["GitHub Actions"],
    "package_managers": ["pip", "npm"]
  },
  
  "architecture.json": {
    "modules": 45,
    "entry_points": ["main.py", "app.js"],
    "layers": ["api", "business_logic", "database"],
    "critical_paths": ["/api/users", "/api/planning"],
    "coupling_score": 0.32
  },
  
  "code-organization.json": {
    "total_files": 342,
    "total_lines": 125000,
    "complexity_score": 32,
    "hotspots": ["planning_orchestrator.py", "state_manager.py"],
    "code_duplication_percentage": 8.5
  },
  
  "security.json": {
    "vulnerability_count": 3,
    "critical_issues": 0,
    "warnings": 3,
    "owasp_top_10": ["A03: Injection", "A07: XSS"],
    "recommended_fixes": [...]
  },
  
  "git-analysis.json": {
    "total_commits": 1234,
    "active_contributors": 5,
    "hotspots": ["planning_orchestrator.py"],
    "branch_patterns": "feature-*, bugfix-*",
    "release_cadence": "weekly"
  },
  
  "metadata.json": {
    "scan_timestamp": "2026-01-12T15:30:00Z",
    "scanner_version": "6.0.0",
    "project_name": "CORTEX",
    "project_root": "/path/to/cortex",
    "analysis_time_seconds": 45
  }
}
```

---

## 🔗 Integration Points

### With Planning Orchestrator
```python
# Onboarding discovers tech stack and patterns
result = onboarding.run()

# Planning uses discovered knowledge for context-aware planning
planner = PlanningOrchestrator()
planner.context = {
    "tech_stack": result.tech_stack,
    "architecture": result.architecture,
    "team_patterns": result.git_analysis.patterns,
    "company_practices": result.domain_learning.practices
}
planner.create_plan()
```

### With Other Orchestrators
- **Vacuum/Cleanup:** Use architecture graph to identify unused files
- **Investigation:** Reverse engineering provides initial hypothesis
- **Sanitization:** Code complexity data identifies refactoring candidates
- **ADO:** Tech stack helps classify work items

### MCP Tool Exposure

All CORTEX LENS components exposed as MCP tools:

```python
@mcp_tool(
    name="cortex_lens_ast_analyzer",
    category="analysis",
    description="Analyze codebase AST for functions, classes, imports"
)
def analyze_ast(project_path: str, language: str) -> Dict[str, Any]:
    """Exposed to all orchestrators via MCP"""
    pass

@mcp_tool(
    name="cortex_lens_crawler",
    category="analysis",
    description="Run any registered crawler on codebase"
)
def run_crawler(crawler_name: str, project_path: str) -> Dict[str, Any]:
    """Exposed to all orchestrators via MCP"""
    pass
```

---

## 📋 AC-IDs for Implementation

### Phase 1.5: CORTEX LENS (6 ACs)
- **AC-LENS-001:** Universal AST Framework
- **AC-LENS-002:** Code Crawler Framework
- **AC-LENS-003:** Reverse Engineering Engine
- **AC-LENS-004:** Knowledge Graph Builder
- **AC-LENS-005:** Domain Learner System
- **AC-LENS-006:** MCP Tool Exposure

### Phase 1.5: Onboarding Orchestrator (8 ACs)
- **AC-ONBOARD-001:** Project Metadata Scanner
- **AC-ONBOARD-002:** AST Analysis Phase
- **AC-ONBOARD-003:** Git History Analyzer
- **AC-ONBOARD-004:** Tech Stack Detector
- **AC-ONBOARD-005:** Code Quality Analysis
- **AC-ONBOARD-006:** Dashboard Generator
- **AC-ONBOARD-007:** Interactive Setup Wizard
- **AC-ONBOARD-008:** Knowledge Persistence

---

## 🎯 Implementation Strategy

### Delivery Timeline

**Phase 1.5 Duration:** 3-4 weeks (inserted between Phase 1 & Phase 2)

**Rationale:**
- Onboarding depends on Phase 1 infrastructure (audit, state, evidence)
- CORTEX LENS MCP tools needed by Phase 2+ orchestrators
- Early deployment enables better context for Planning v5

**Week Breakdown:**
- **Week 1:** CORTEX LENS foundation (AST, crawlers)
- **Week 2:** Reverse engineering + knowledge graph
- **Week 3:** Onboarding orchestrator (10 phases)
- **Week 4:** Integration testing + MCP exposure

### Dependencies
- ✅ Phase 1 Complete (Audit, State, Lifecycle, Evidence)
- ✅ MCP Framework Ready
- ✅ Base Orchestrator class exists

### High-Risk Items
1. **Multi-language AST parsing** - Mitigate: Start with Python, iterate
2. **Git analysis performance** - Mitigate: Lazy-load, cache results
3. **Large codebase handling** - Mitigate: Parallel crawlers, file limits
4. **Knowledge storage schema** - Mitigate: Use existing YAML patterns

---

## 💾 Storage & Persistence

### Tier 1 (Company Knowledge)
```
cortex-brain/tier1/{project-slug}/
├── knowledge-graph.yaml          # Semantic graph
├── tech-stack.json               # Detected technologies
├── architecture.json             # Module structure
├── team-patterns.json            # Git-based patterns
├── domain-terminology.json       # Project vocabulary
└── onboarding-report.json        # Original analysis
```

### Tier 3 (Domain Patterns)
```
cortex-brain/tier3/{domain}/
├── patterns.yaml                 # Reusable patterns
├── anti-patterns.yaml            # Things to avoid
├── naming-conventions.yaml       # Naming rules
├── best-practices.yaml           # Learned practices
└── examples/                      # Code examples
```

### Audit Trail
- All discovery operations logged to `cortex-brain/audit-logs/`
- Full evidence bundles generated
- Searchable by project or date

---

## ✅ Success Metrics

### CORTEX LENS
- ✅ All 6 ACs implemented with ≥80% test coverage
- ✅ Supports ≥6 programming languages
- ✅ <5s AST analysis for files <1000 LOC
- ✅ MCP tools accessible from all orchestrators

### Onboarding Orchestrator
- ✅ 10-phase flow completes in <2 minutes for typical project
- ✅ Generates 7 JSON output files with valid schema
- ✅ Interactive dashboard displays all findings
- ✅ Auto-creates tier1/tier3 knowledge files
- ✅ 100% of projects auto-onboarded during setup

### Integration
- ✅ Planning v5 uses discovered context
- ✅ All orchestrators can query knowledge graph
- ✅ Crawler results visible in audit logs
- ✅ Regression testing: Re-onboard validates consistency

---

## 📚 Related Documentation

- CORTEX-5.5 branch: `cortex-brain/learning/onboarding-orchestrator-quick-ref.md`
- Previous LENS implementations: commits 6d5d3c825, 63de6f396, 04a8e3d8c
- AST integration examples: `src/orchestrators/planning/planning_orchestrator.py`
- Crawler framework: `cortex-brain/manifests/shared/analysis-base-manifest.yaml`

---

## 🎓 Learning Path for Implementation

1. **Study:** Previous onboarding implementation (quick-ref.md)
2. **Understand:** AST parsing patterns in planning_orchestrator.py
3. **Design:** CORTEX LENS component interfaces
4. **Implement:** Start with Python AST analyzer
5. **Test:** TDD cycle for each component
6. **Integrate:** Wire Onboarding to use LENS
7. **Validate:** End-to-end onboarding flow

---

**Next Step:** Break AC-LENS-* and AC-ONBOARD-* into AC-INDEX.yaml with detailed acceptance criteria, then begin Phase 1.5 implementation.

