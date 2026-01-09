# 🧠 Intelligent Planning Orchestrator - Executive Design Summary

**Version:** 6.0.0 | **Date:** 2026-01-09  
**Purpose:** Most efficient autonomous planning with intelligent domain learning  
**Author:** Asif Hussain

---

## 🎯 Design Philosophy

**GOAL:** Create a self-learning planning orchestrator that:
- **Learns incrementally** from codebase structure via AST scanning
- **Builds domain knowledge graph** during plan creation (not separate scan)
- **Enriches context intelligently** using accumulated domain understanding
- **Generates optimal folder structures** for autonomous execution
- **Shows concise visual progress** (executive summaries, not code)
- **Eliminates duplication** between epic/feature/phase structures

---

## 📊 Analysis of Existing Variations

### **Variation 1: Planning Orchestrator v5 (Current)**
**Location:** `src/orchestrators/planning/planning_orchestrator_v5.py`

**Strengths:**
- ✅ Pure autonomous execution (zero manual intervention)
- ✅ Database state tracking (`PlanningStateDB`)
- ✅ AST scanning integration (`ASTScanner`)
- ✅ Knowledge graph queries (`KnowledgeGraphQuery`)
- ✅ Governance integration (`GovernanceIntegrator`)
- ✅ Duplicate detection (`PlanningDuplicateDetector`)
- ✅ Orphan detection (`PlanningOrphanDetector`)
- ✅ Acceptance criteria validation (`AcceptanceCriteriaValidator`)
- ✅ TODO Manager integration (task tracking)

**Weaknesses:**
- ❌ AST scanning separate from knowledge building (2-pass system)
- ❌ Knowledge graph not updated during planning
- ❌ No incremental domain learning
- ❌ Verbose progress output (not executive-friendly)
- ❌ Folder structure creates duplication (epic → features → phases)

---

### **Variation 2: CORTEX 6.0 Source-of-Truth Structure**
**Location:** `.asif/AI-Learning/cortex6/source-of-truth/`

**Strengths:**
- ✅ **Flattened epic structure** - features/ folder without nested duplication
- ✅ **feature.yaml per feature** - YAML-based phase/task/dependency tracking
- ✅ **Audit-driven build policy** - every operation logged
- ✅ **Phase-level checkpoints** - validation triggers
- ✅ **Incremental execution** - max 500 lines per increment
- ✅ **Handoff-aware** - Copilot → CORTEX TODO Manager transition

**Weaknesses:**
- ❌ Manually crafted (not orchestrator-generated)
- ❌ No AST-based knowledge capture during creation
- ❌ Static templates (not adaptive to domain)

---

### **Variation 3: Archived Planning v5 (Enhanced)**
**Location:** `cortex-brain/archives/planning/.../planning_orchestrator_v5.py`

**Strengths:**
- ✅ MCP tool integration concepts
- ✅ Continuous knowledge learning mentioned in docs
- ✅ Planning pattern queries

**Weaknesses:**
- ❌ Never fully implemented
- ❌ Concepts scattered, not cohesive

---

## 🏗️ OPTIMAL DESIGN: Intelligent Planning Orchestrator v6

### **Core Innovation: Just-In-Time Domain Learning**

```
Traditional (2-Pass):
1. Scan codebase → Build knowledge graph
2. Query knowledge graph → Generate plan

Intelligent (Single-Pass):
1. Parse user request → Identify domain entities
2. Incremental AST scan → Learn as you go
3. Enrich context continuously → Adaptive planning
4. Generate plan with accumulated knowledge
```

---

## 📁 Optimal Folder Structure (Flattened Epic Model)

### **FOR EPIC PLANS:**

```
cortex-brain/documents/planning/active/{epic-id}/
├── 00-{EPIC-ID}-MASTER.yaml               # Epic metadata, features list, dependencies
├── epic.yaml                              # Epic config (handoff, constraints, progress)
├── continuation-prompt.md                 # Session resumption context
├── plan-viewer.html                       # Interactive visual dashboard
├── features/                              # ✅ ALL FEATURES HERE (flattened)
│   ├── feat01-{name}/
│   │   ├── feature.yaml                   # Phases, tasks, dependencies, outputs
│   │   ├── requirements.yaml              # Detailed requirements
│   │   ├── context/                       # Feature-specific docs
│   │   │   └── {name}-overview.md
│   │   └── tracking/                      # Optional per-feature progress
│   │       └── progress-tracker.json
│   ├── feat02-{name}/
│   │   └── [same structure]
│   └── feat##-{name}/
│       └── [same structure]
├── analysis/                              # Epic-level analysis
│   ├── domain-knowledge.json              # 🧠 ACCUMULATED KNOWLEDGE GRAPH
│   ├── ast-insights.yaml                  # Code structure insights
│   └── dependencies-graph.mermaid
├── artifacts/                             # Epic-level deliverables
│   └── architecture-diagrams.md
├── tracking/                              # Epic-level tracking
│   ├── progress-tracker.json              # Overall epic progress
│   ├── effort-log.md                      # Time tracking
│   └── audit-log.jsonl                    # Audit trail
└── reports/                               # Epic-level reports
    └── status-reports/
```

**KEY INSIGHT:** No nested phase folders inside features. Phases defined in `feature.yaml`.

---

### **FOR FEATURE PLANS:**

```
cortex-brain/documents/planning/active/{feature-id}/
├── 00-{FEATURE-ID}-MASTER.yaml
├── feature.yaml                           # Phases, tasks, dependencies
├── requirements.yaml                      # Requirements breakdown
├── continuation-prompt.md
├── plan-viewer.html
├── context/                               # Feature context
│   └── overview.md
├── analysis/                              # Feature analysis
│   ├── domain-knowledge.json              # 🧠 LEARNED DURING PLANNING
│   └── ast-insights.yaml
├── artifacts/                             # Feature deliverables
├── tracking/                              # Feature tracking
│   └── progress-tracker.json
└── reports/                               # Feature reports
```

**NO features/ subfolder** for feature plans. Phases in YAML, not folders.

---

### **FOR PHASE PLANS (Rare - Usually in Feature YAML):**

```
cortex-brain/documents/planning/active/{phase-id}/
├── 00-{PHASE-ID}-MASTER.yaml
├── phase.yaml                             # Tasks, validation criteria
├── continuation-prompt.md
├── context/
├── analysis/
│   └── domain-knowledge.json              # 🧠 PHASE-SPECIFIC KNOWLEDGE
├── artifacts/
├── tracking/
└── reports/
```

---

## 🧠 Intelligent Domain Learning System

### **Component 1: Incremental AST Scanner**

**Purpose:** Learn codebase structure **during** plan creation, not before.

**Features:**
- **Lazy loading** - scan only when needed (not entire codebase upfront)
- **Caching** - remember scanned files (avoid re-scanning)
- **Incremental updates** - update knowledge graph as new files discovered
- **Domain entity extraction** - classes, functions, patterns, dependencies

**Knowledge Captured:**
```yaml
domain_knowledge:
  entities:
    - name: "StateManager"
      type: "class"
      location: "src/database/state_manager.py"
      methods: ["initialize", "get_state", "update_state"]
      dependencies: ["SQLite", "WAL mode"]
      
  patterns:
    - pattern: "orchestrator_pattern"
      files: ["src/orchestrators/*.py"]
      base_class: "BaseOrchestratorV4_1"
      common_methods: ["execute", "validate"]
      
  dependencies:
    - from: "PlanningOrchestrator"
      to: "StateManager"
      type: "uses"
      strength: "critical"
```

---

### **Component 2: Knowledge Graph Builder**

**Purpose:** Build domain graph incrementally as AST scans progress.

**Graph Structure:**
```
Nodes: Classes, Functions, Modules, Patterns, Concepts
Edges: Depends-on, Implements, Uses, References, Part-of

Example:
PlanningOrchestrator -[depends-on]-> StateManager
PlanningOrchestrator -[implements]-> BaseOrchestrator
StateManager -[uses]-> SQLite
```

**Update Strategy:**
- **On-demand** - add nodes/edges as discovered
- **Confidence scoring** - track how often entities seen (weight)
- **Relationship inference** - detect implicit dependencies

---

### **Component 3: Context Enricher**

**Purpose:** Use accumulated knowledge to enrich plan context intelligently.

**Enrichment Rules:**
1. **User mentions "database"** → Inject knowledge about existing DB classes
2. **User mentions "orchestrator"** → Inject base orchestrator patterns
3. **User mentions "testing"** → Inject test infrastructure knowledge
4. **User vague request** → Infer from similar patterns in graph

**Example:**
```
User: "plan user authentication"

Context Enricher:
- Scans graph for "auth" patterns
- Finds: OAuth2Provider, JWTHandler, SessionManager
- Injects: "Consider integrating with existing OAuth2Provider"
- Detects: Database patterns (users table likely needed)
- Suggests: "StateManager for session persistence"
```

---

### **Component 4: Template Adapter**

**Purpose:** Adapt templates based on domain knowledge.

**Adaptive Templates:**
- **Feature plan** → Include existing orchestrator patterns if relevant
- **Epic plan** → Suggest features based on discovered gaps
- **Phase plan** → Auto-generate tasks based on codebase conventions

---

## 🎨 Concise Visual Progress (Executive-Friendly)

### **During Execution - Show This:**

```
## 🧠 Planning Orchestrator v6 - Autonomous Execution

📊 **Progress:** Phase 2/5 - Architecture Analysis

🔍 **Learning:**
  ├─ Scanned: 12 files
  ├─ Entities: 45 classes, 187 functions
  └─ Patterns: 3 orchestrator patterns, 1 database pattern

✅ **Completed:**
  └─ Phase 1: Context Discovery (3 workspace files found)

⚙️ **Current:**
  └─ Phase 2: AST analysis in progress...

📁 **Plan Location:**
  └─ cortex-brain/documents/planning/active/feat-user-auth/

⏱️ **Duration:** 12s
```

---

### **NOT This (Too Verbose):**

```
[INFO] Scanning file: src/orchestrators/planning_orchestrator_v5.py
[DEBUG] Found class: PlanningOrchestratorV5
[DEBUG] Found method: execute (line 234)
[DEBUG] Found import: BaseOrchestratorV4_1
[DEBUG] Extracting dependencies...
[DEBUG] Building AST tree...
[INFO] Processing node: ClassDef
[DEBUG] Method signature: execute(self, context: Dict[str, Any])
...
```

---

## ⚡ Execution Flow (Single-Pass Knowledge Building)

```
User Request → Parse Intent → Initialize Plan

Phase 1: Context Discovery
  ├─ Search workspace for similar features
  ├─ Build initial knowledge graph (seed)
  └─ Enrich context with discoveries

Phase 2: Architecture Analysis
  ├─ AST scan relevant files (on-demand)
  ├─ Update knowledge graph (incremental)
  ├─ Detect patterns and conventions
  └─ Enrich context continuously

Phase 3: Plan Generation
  ├─ Query knowledge graph for insights
  ├─ Adapt templates based on domain
  ├─ Generate feature.yaml with phases/tasks
  └─ Include learned patterns in plan

Phase 4: Folder Creation
  ├─ Create flattened structure (epic → features/)
  ├─ Generate plan-viewer.html
  ├─ Write domain-knowledge.json to analysis/
  └─ Create continuation-prompt.md

Phase 5: Validation
  ├─ Validate folder structure
  ├─ Validate YAML syntax
  ├─ Check governance compliance
  └─ Write audit log

Result: Plan ready + Domain knowledge captured
```

---

## 🔧 Technical Architecture

### **Class Hierarchy:**

```
BaseOrchestratorV4_1
  └─ IntelligentPlanningOrchestratorV6
       ├─ IncrementalASTScanner        (lazy, cached)
       ├─ KnowledgeGraphBuilder        (incremental updates)
       ├─ ContextEnricher              (query-based)
       ├─ TemplateAdapter              (domain-aware)
       ├─ FolderStructureGenerator     (flattened epic model)
       └─ ProgressRenderer             (concise, executive)
```

---

### **Database Schema (Knowledge Persistence):**

```sql
-- New table: domain_knowledge
CREATE TABLE domain_knowledge (
    id INTEGER PRIMARY KEY,
    plan_id TEXT NOT NULL,
    entity_type TEXT,  -- 'class', 'function', 'pattern'
    entity_name TEXT,
    location TEXT,
    metadata JSON,     -- methods, dependencies, etc.
    confidence REAL,   -- 0.0-1.0 (how often seen)
    created_at TIMESTAMP,
    FOREIGN KEY (plan_id) REFERENCES plans(plan_id)
);

-- New table: knowledge_graph_edges
CREATE TABLE knowledge_graph_edges (
    id INTEGER PRIMARY KEY,
    plan_id TEXT NOT NULL,
    from_entity TEXT,
    to_entity TEXT,
    edge_type TEXT,    -- 'depends-on', 'implements', 'uses'
    weight REAL,       -- edge strength
    created_at TIMESTAMP
);
```

---

## 📈 Performance Optimizations

### **1. Lazy AST Scanning**
- Don't scan entire codebase upfront
- Scan on-demand when user request implies need
- Cache scanned files in memory (session-local)

### **2. Incremental Knowledge Updates**
- Update graph as new entities discovered
- Don't rebuild entire graph each time
- Use delta updates (add/remove nodes/edges)

### **3. Query Optimization**
- Index knowledge graph by entity type
- Use BFS/DFS for pattern matching (not full scan)
- Cache frequent queries (e.g., "all orchestrators")

### **4. Concise Output**
- Aggregate progress updates (not per-file logs)
- Show executive summary every 5 seconds
- Full logs to audit file, not terminal

---

## 🎯 Key Differentiators from v5

| Feature | Planning v5 | Intelligent v6 |
|---------|-------------|----------------|
| **Knowledge Building** | Separate scan phase | Incremental during planning |
| **Context Enrichment** | Manual patterns | Intelligent query-based |
| **Folder Structure** | Nested (epic→features→phases folders) | Flattened (phases in YAML) |
| **Progress Output** | Verbose logs | Concise executive summary |
| **Domain Learning** | Static | Continuous, adaptive |
| **Template System** | Fixed templates | Domain-aware adaptation |
| **Knowledge Persistence** | None (lost after execution) | Saved to analysis/domain-knowledge.json |
| **AST Caching** | Re-scan every time | Cache per session |

---

## 📋 Implementation Phases

### **Phase 1: Core Infrastructure (P0)**
- Flattened folder structure generator
- Incremental AST scanner with caching
- Knowledge graph builder (in-memory)

### **Phase 2: Intelligence Layer (P0)**
- Context enricher with query engine
- Template adapter with domain awareness
- Progress renderer (concise format)

### **Phase 3: Persistence (P1)**
- Knowledge graph database tables
- domain-knowledge.json writer
- Knowledge graph viewer (HTML)

### **Phase 4: Advanced Features (P2)**
- Pattern inference engine
- Confidence scoring
- Cross-plan knowledge sharing

---

## 🚀 User Experience

### **Command:**
```bash
python3 -m src.main "plan user authentication with OAuth2 and JWT"
```

### **Output (Concise Executive Summary):**
```
## 🧠 Intelligent Planning Orchestrator v6

📊 **Plan Type:** Feature Plan
📁 **Plan ID:** feat-user-authentication
📍 **Location:** cortex-brain/documents/planning/active/feat-user-authentication/

🔍 **Domain Learning:**
  ✅ Discovered 3 similar patterns in codebase
  ✅ Found existing OAuth2Provider class
  ✅ Detected JWT library already installed
  
✨ **Intelligent Insights:**
  • Reuse existing OAuth2Provider (src/auth/oauth2_provider.py)
  • JWT tokens: Use existing JWTHandler class
  • Database: Extend UserManager with authentication fields
  
📋 **Generated Plan:**
  ├─ 4 Phases: Design → Implementation → Testing → Deployment
  ├─ 15 Tasks (8 TDD-required)
  ├─ Dependencies: 3 existing classes
  └─ Estimated: 12 days
  
📂 **Structure Created:**
  ├─ feature.yaml (phases, tasks, dependencies)
  ├─ requirements.yaml (detailed breakdown)
  ├─ context/overview.md
  ├─ analysis/domain-knowledge.json (45 entities learned)
  ├─ tracking/progress-tracker.json
  └─ plan-viewer.html

✅ **Plan Ready** - Execute with: `cortex continue feat-user-authentication`

⏱️ **Duration:** 8.3s | **Knowledge Learned:** 45 entities, 12 patterns
```

---

## 🎯 Success Metrics

- **Planning Speed:** <10s for feature plans, <30s for epic plans
- **Knowledge Capture:** 80%+ entities in relevant domain discovered
- **Context Relevance:** 90%+ suggested patterns applicable
- **User Satisfaction:** Concise output, no code spam
- **Knowledge Reuse:** 50%+ plans benefit from previously learned domain

---

## 🔄 Continuous Improvement

**Knowledge graph grows over time:**
- Each plan execution adds to domain knowledge
- Pattern confidence scores increase with usage
- Cross-plan learning (shared knowledge across epics)
- Automated cleanup of low-confidence entities (pruning)

---

## 📝 Folder Structure Rules (Anti-Duplication)

### **✅ CORRECT (Flattened):**
```
epic-cortex6/
  └─ features/
       ├─ feat01-foundation/
       │    └─ feature.yaml (phases defined in YAML)
       └─ feat02-todo-orchestrator/
            └─ feature.yaml (phases defined in YAML)
```

### **❌ WRONG (Nested Duplication):**
```
epic-cortex6/
  └─ features/
       └─ feat01-foundation/
            └─ phases/
                 ├─ phase1-design/
                 ├─ phase2-implementation/
                 └─ phase3-testing/
```

**Rationale:** Phases are execution units, not folders. YAML tracks progress.

---

## 🎨 Visual Progress Examples

### **Phase Start:**
```
⚙️ Phase 2/5: Architecture Analysis
  └─ AST scanning... 🔍
```

### **Phase Progress:**
```
⚙️ Phase 2/5: Architecture Analysis
  ├─ Scanned: 8/12 files
  └─ Entities discovered: 32 classes, 98 functions
```

### **Phase Complete:**
```
✅ Phase 2/5: Architecture Analysis - COMPLETE
  ├─ Scanned: 12 files
  ├─ Entities: 45 classes, 187 functions
  └─ Duration: 2.1s
```

---

## 🏁 Conclusion

**Intelligent Planning Orchestrator v6** combines:
- ✅ **Efficiency** - Single-pass knowledge building (not 2-pass)
- ✅ **Intelligence** - Learn domain during planning
- ✅ **Clarity** - Concise executive summaries (no code spam)
- ✅ **Simplicity** - Flattened folder structure (no duplication)
- ✅ **Persistence** - Knowledge saved for future plans
- ✅ **Adaptability** - Templates adapt to discovered patterns

**Next Step:** Review this design, approve, and begin Phase 1 implementation (P0 infrastructure).

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
