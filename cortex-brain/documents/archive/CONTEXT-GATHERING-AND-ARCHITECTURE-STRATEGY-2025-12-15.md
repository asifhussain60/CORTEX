# Context Gathering & Architecture Strategy: CORTEX 3.0 → 4.0

**Executive Summary:** Analysis of plan execution orchestrator's context gathering capabilities and comprehensive strategy for CORTEX 3.0 enhancement + 4.0 vision.

**Author:** GitHub Copilot (CORTEX 3.0)  
**Date:** December 15, 2025  
**Status:** Strategic Planning Document  
**Context:** Extension of PLANNING-ORCHESTRATOR-HOLISTIC-REVIEW-2025-12-15.md

---

## 🎯 Purpose

Evaluate plan execution orchestrator's context gathering during plan development and define:
1. **Current State:** What context gathering exists today
2. **CORTEX 3.0 Strategy:** Near-term enhancements (Q1 2026)
3. **CORTEX 4.0 Vision:** Long-term architecture (Q2-Q3 2026)
4. **Implementation Roadmap:** Phased delivery plan

---

## 📊 Current State Analysis

### Plan Execution Orchestrator (v2.0)

**File:** `src/orchestrators/plan_execution_orchestrator.py` (1404 lines)

**Context Gathering Capabilities:**

#### ✅ Implemented
1. **AST Analysis** (Lines 820-850)
   - Python file parsing via `ast.parse()`
   - Function signature extraction
   - Duplicate code detection
   - Limitation: Python-only, no multi-language support

2. **File System Scanning** (Lines 762-800)
   - Gathers files from `files_affected` in plan phases
   - File organization rules (test_, orchestrator, collector patterns)
   - Limitation: Static list from plan, not dynamic discovery

3. **Basic Deprecation Detection** (Lines 780-800)
   - Searches for `@deprecated` and `# deprecated` markers
   - Limitation: Text search only, no semantic analysis

#### ❌ Missing Critical Capabilities
1. **Git History Analysis:** NO integration
   - No commit history context
   - No author/contributor identification
   - No change frequency analysis
   - No related file discovery via co-commits
   - No security pattern identification from past fixes

2. **Comment Extraction:** NO integration
   - AST Narrative Orchestrator exists (`src/orchestrators/ast_narrative_orchestrator.py`)
   - CommentCollector exists (`src/cortex_lens/collectors/comment_collector.py`)
   - NOT integrated into plan execution workflow
   - Business rules, TODOs, regulatory keywords not captured

3. **Historical Context Storage:** NO persistence
   - Analysis results not saved for reuse
   - No context accumulation across phases
   - Each phase starts from scratch

4. **Code Graph Analysis:** Minimal
   - RelationshipManager exists (`src/tier2/knowledge_graph/knowledge_graph.py`)
   - DependencyGraphGenerator exists (`src/operations/modules/visualization/dependency_graph_generator.py`)
   - NOT integrated into plan execution

---

## 🏗️ Architecture Gap Analysis

### Existing Infrastructure

#### ✅ Available Components (Not Integrated)

| Component | Location | Capability | Status |
|-----------|----------|------------|--------|
| GitAnalyzerCrawler | `src/operations/crawlers/git_analyzer.py` | Commit history, hot files, contributors | ✅ Complete |
| GitAnalyzer | `src/agents/implementation_discovery_engine.py` | Recent changes, line diffs, co-authors | ✅ Complete |
| CommentCollector | `src/cortex_lens/collectors/comment_collector.py` | Docstrings, TODOs, regulatory keywords | ✅ Complete |
| AST Narrative Orchestrator | `src/orchestrators/ast_narrative_orchestrator.py` | Comment categorization, narrative synthesis | ✅ Complete |
| KnowledgeGraph | `src/tier2/knowledge_graph/knowledge_graph.py` | Pattern storage, relationships, graph traversal | ✅ Complete |
| DependencyGraphGenerator | `src/operations/modules/visualization/dependency_graph_generator.py` | Import analysis, dependency visualization | ✅ Complete |

**Problem:** All infrastructure exists but operates in silos. Plan execution orchestrator doesn't orchestrate them.

### Root Cause: No Unified Context Builder

**Current Flow (Broken):**
```
Plan Execution Orchestrator
  → Load plan YAML
  → Execute phases (TDD, scaffolding, etc.)
  → Gather files_affected (static list)
  → Basic AST analysis (Python only)
  → NO git history
  → NO comment extraction
  → NO context persistence
```

**Required Flow (Unified):**
```
Plan Execution Orchestrator
  → Load plan YAML
  → 🆕 Initialize Context Builder
  → 🆕 Build Rich Context (git + AST + comments + graph)
  → 🆕 Store in plan folder (YAML + JSON artifacts)
  → Execute phases WITH historical context
  → 🆕 Update context as execution progresses
  → 🆕 Persist learnings to Tier 2 knowledge graph
```

---

## 🎯 CORTEX 3.0 Enhancement Strategy

**Timeline:** Q1 2026 (January-March)  
**Goal:** Add unified context builder to existing orchestrators

### Phase 1: Unified Context Builder Module

**File:** `src/operations/modules/context/unified_context_builder.py`

**Responsibilities:**
1. Orchestrate all context gathering components
2. Build rich context during planning back-and-forth
3. Store context artifacts in plan folder
4. Provide efficient context retrieval API

**Key Features:**

#### 1.1 Git History Context (Priority: CRITICAL)

**Brain Protection Rule:** `GIT_HISTORY_CONTEXT_REQUIRED` (Lines 3363-3368 in brain-protection-rules.yaml)

**Implementation:**
```python
class GitHistoryContextBuilder:
    """
    Builds git history context for files in plan scope.
    
    Outputs:
    - plan-folder/context/git-history.yaml
    - plan-folder/context/contributors.yaml
    - plan-folder/context/security-patterns.yaml
    """
    
    def build_context(self, files: List[Path], days_back: int = 90) -> Dict:
        """
        Build comprehensive git context.
        
        Returns:
            {
                'file_histories': {
                    'path/to/file.py': {
                        'total_commits': 42,
                        'recent_commits': 12,
                        'primary_authors': ['alice', 'bob'],
                        'change_frequency': 'high',
                        'last_modified': '2025-12-10',
                        'security_fixes': [
                            {'commit': 'abc123', 'issue': 'SQL injection', 'date': '2025-11-15'},
                        ],
                        'related_files': ['related1.py', 'related2.py'],
                        'hot_spots': ['function_foo', 'class_Bar'],
                    }
                },
                'risk_assessment': {
                    'high_risk_files': ['Login.cs', 'AuthHandler.py'],
                    'rationale': 'Multiple security fixes in past 90 days'
                },
                'expert_recommendations': {
                    'Login.cs': 'Contact alice (5 commits, security focus)',
                }
            }
        """
        
        # Use existing GitAnalyzerCrawler + GitAnalyzer
        git_crawler = GitAnalyzerCrawler(self.project_root)
        git_analyzer = GitAnalyzer(self.project_root)
        
        # Gather history for each file
        file_histories = {}
        for file in files:
            history = git_analyzer.get_recent_changes(days_back)
            file_histories[str(file)] = self._analyze_file_history(file, history)
        
        # Identify security patterns
        security_patterns = self._extract_security_patterns(file_histories)
        
        # Risk assessment
        risk_assessment = self._assess_risk(file_histories, security_patterns)
        
        # Expert recommendations
        experts = self._identify_experts(file_histories)
        
        return {
            'file_histories': file_histories,
            'security_patterns': security_patterns,
            'risk_assessment': risk_assessment,
            'expert_recommendations': experts,
        }
```

**Storage Format (YAML):**
```yaml
# plan-folder/context/git-history.yaml
file_histories:
  src/auth/login.py:
    total_commits: 42
    recent_commits: 12
    primary_authors:
      - name: alice
        commits: 25
        focus: security
      - name: bob
        commits: 17
        focus: performance
    change_frequency: high
    last_modified: "2025-12-10"
    security_fixes:
      - commit: abc123
        issue: SQL injection
        date: "2025-11-15"
        solution: Parameterized queries
      - commit: def456
        issue: XSS vulnerability
        date: "2025-10-20"
        solution: Output encoding
    related_files:
      - src/auth/session.py
      - src/db/user_repository.py
    hot_spots:
      - function: authenticate_user
        commits: 8
        lines_changed: 156

risk_assessment:
  high_risk_files:
    - src/auth/login.py
    - src/auth/session.py
  rationale: "Multiple security fixes (2) in past 90 days indicate systemic validation issues"

expert_recommendations:
  src/auth/login.py: "Contact alice (25 commits, security focus) for architectural review"
```

#### 1.2 AST + Comment Extraction

**Implementation:**
```python
class ASTCommentContextBuilder:
    """
    Combines AST parsing with comment extraction.
    
    Outputs:
    - plan-folder/context/ast-analysis.yaml
    - plan-folder/context/code-graph.json
    - plan-folder/context/comments.yaml
    """
    
    def build_context(self, files: List[Path]) -> Dict:
        """
        Build AST + comment context.
        
        Returns:
            {
                'code_structure': {
                    'classes': [...],
                    'functions': [...],
                    'imports': [...],
                },
                'comments': {
                    'docstrings': [...],
                    'todos': [...],
                    'business_rules': [...],
                    'regulatory': {...},
                },
                'code_graph': {
                    'nodes': [...],
                    'edges': [...],
                },
            }
        """
        
        # Use existing CommentCollector
        comment_collector = CommentCollector(self.project_root)
        comment_data = comment_collector.collect(self.project_root, classification={})
        
        # Use existing AST Narrative Orchestrator for multi-language support
        ast_orchestrator = ASTNarrativeOrchestrator(self.project_root)
        ast_data = ast_orchestrator.analyze_files(files)
        
        # Build code graph via DependencyGraphGenerator
        graph_generator = DependencyGraphGenerator(self.project_root)
        code_graph = graph_generator.generate_graph(files)
        
        return {
            'code_structure': ast_data,
            'comments': comment_data,
            'code_graph': code_graph,
        }
```

**Storage Format (YAML):**
```yaml
# plan-folder/context/comments.yaml
business_rules:
  - file: src/billing/invoice.py
    line: 45
    rule: "Invoices must be sent within 24 hours of order completion (regulatory requirement)"
    type: validation
    priority: critical

todos:
  - file: src/auth/session.py
    line: 120
    text: "TODO: Add session timeout configuration"
    author: alice
    date: "2025-12-01"

regulatory_keywords:
  gdpr:
    - file: src/user/profile.py
      line: 78
      context: "User data export for GDPR compliance"
  pci:
    - file: src/payment/processor.py
      line: 156
      context: "PCI-DSS compliant card tokenization"
```

```json
// plan-folder/context/code-graph.json
{
  "nodes": [
    {
      "id": "src/auth/login.py::authenticate_user",
      "type": "function",
      "language": "python",
      "complexity": 8,
      "lines": 45
    }
  ],
  "edges": [
    {
      "source": "src/auth/login.py::authenticate_user",
      "target": "src/db/user_repository.py::get_user_by_email",
      "type": "calls"
    }
  ],
  "metrics": {
    "total_nodes": 127,
    "total_edges": 234,
    "avg_complexity": 4.2
  }
}
```

#### 1.3 Context Storage & Retrieval

**Storage Strategy:**

```
cortex-brain/documents/planning/active/{feature-name-v1}/
├── context/                              # 🆕 Context storage
│   ├── git-history.yaml                 # Git analysis results
│   ├── contributors.yaml                # Expert identification
│   ├── security-patterns.yaml           # Historical security fixes
│   ├── ast-analysis.yaml                # Code structure
│   ├── code-graph.json                  # Dependency graph
│   ├── comments.yaml                    # Extracted comments
│   └── context-index.yaml               # Context inventory
├── 00-master-plan.md                    # Master plan
├── 01-subplan-phase1.md                 # Sub-plans
├── artifacts/
│   └── execution-context-{phase}.json   # Per-phase snapshots
└── reports/
    └── context-analysis-report.md       # Human-readable summary
```

**Context Index (Metadata):**
```yaml
# context-index.yaml
context_version: "3.0"
generated_at: "2025-12-15T10:30:00Z"
files_analyzed: 42
context_sources:
  git_history:
    status: complete
    files_analyzed: 42
    days_back: 90
    security_patterns_found: 5
  ast_analysis:
    status: complete
    languages: [python, csharp, javascript]
    total_functions: 234
    total_classes: 67
  comment_extraction:
    status: complete
    docstrings: 156
    todos: 23
    business_rules: 12
    regulatory_mentions: 8
  code_graph:
    status: complete
    nodes: 127
    edges: 234
    complexity_avg: 4.2

risk_summary:
  high_risk_files: 3
  security_debt: "Multiple SQL injection fixes in auth module (systemic issue)"
  recommended_actions:
    - "Comprehensive input validation strategy"
    - "Security audit of auth module"
    - "Consult alice (security expert, 25 commits in auth)"
```

**Context Retrieval API:**
```python
class ContextRetriever:
    """
    Efficient context retrieval for execution phases.
    """
    
    def load_context(self, plan_folder: Path) -> PlanContext:
        """
        Load all context from plan folder.
        
        Returns unified PlanContext object with:
        - git_history: Dict
        - ast_analysis: Dict
        - comments: Dict
        - code_graph: Dict
        - risk_assessment: Dict
        """
        context_dir = plan_folder / "context"
        
        return PlanContext(
            git_history=self._load_yaml(context_dir / "git-history.yaml"),
            ast_analysis=self._load_yaml(context_dir / "ast-analysis.yaml"),
            comments=self._load_yaml(context_dir / "comments.yaml"),
            code_graph=self._load_json(context_dir / "code-graph.json"),
            risk_assessment=self._extract_risk_summary(context_dir / "context-index.yaml"),
        )
    
    def get_file_context(self, plan_folder: Path, file_path: str) -> FileContext:
        """
        Get context for specific file (optimized for per-file queries).
        """
        context = self.load_context(plan_folder)
        
        return FileContext(
            git_history=context.git_history['file_histories'].get(file_path, {}),
            ast_structure=self._extract_file_ast(context.ast_analysis, file_path),
            comments=self._extract_file_comments(context.comments, file_path),
            dependencies=self._extract_file_dependencies(context.code_graph, file_path),
        )
```

### Phase 2: Integration with Planning Orchestrator

**Update:** `src/operations/modules/orchestration/planning_orchestrator.py`

**Integration Points:**

#### 2.1 Planning Phase: Context Building

```python
class PlanningOrchestrator:
    def __init__(self, ...):
        # ... existing code ...
        
        # 🆕 Initialize context builder
        self.context_builder = UnifiedContextBuilder(self.project_root)
    
    async def _planning_phase(self, planning_context: PlanningContext) -> Dict[str, Any]:
        """
        Enhanced planning phase with context gathering.
        """
        
        # Step 1: Initial planning conversation (existing)
        plan_structure = await self._generate_plan_structure(planning_context)
        
        # Step 2: 🆕 Build rich context for files in scope
        files_in_scope = self._extract_files_from_plan(plan_structure)
        
        logger.info(f"🔍 Building context for {len(files_in_scope)} files...")
        
        context_result = await self.context_builder.build_comprehensive_context(
            files=files_in_scope,
            days_back=90,  # Configurable via manifest
            include_git_history=True,
            include_ast_analysis=True,
            include_comments=True,
            include_code_graph=True,
        )
        
        # Step 3: 🆕 Store context in plan folder
        plan_folder = self._get_plan_folder(planning_context)
        context_dir = plan_folder / "context"
        context_dir.mkdir(exist_ok=True)
        
        self.context_builder.save_context(context_result, context_dir)
        
        logger.info(f"✅ Context saved: {context_dir}")
        
        # Step 4: 🆕 Generate context analysis report (human-readable)
        report_path = plan_folder / "reports" / "context-analysis-report.md"
        self._generate_context_report(context_result, report_path)
        
        # Step 5: Use context to enhance plan (existing flow continues)
        enhanced_plan = self._enhance_plan_with_context(plan_structure, context_result)
        
        return enhanced_plan
```

#### 2.2 Execution Phase: Context Utilization

```python
class PlanExecutionOrchestrator:
    def _execute_phase(self, phase: Dict, plan_folder: Path) -> Dict[str, Any]:
        """
        Enhanced phase execution with historical context.
        """
        
        # 🆕 Load context for this phase
        context = self.context_retriever.load_context(plan_folder)
        
        # 🆕 Get files for this phase
        phase_files = phase.get('files_affected', [])
        
        # 🆕 Provide context to execution agents
        for file in phase_files:
            file_context = context.get_file_context(file)
            
            # Show security warnings
            if file_context.git_history.get('security_fixes'):
                logger.warning(f"⚠️  {file} has security fix history:")
                for fix in file_context.git_history['security_fixes']:
                    logger.warning(f"   - {fix['issue']} fixed on {fix['date']}")
            
            # Show business rules
            if file_context.comments.get('business_rules'):
                logger.info(f"📋 {file} has business rules:")
                for rule in file_context.comments['business_rules']:
                    logger.info(f"   - {rule['rule']}")
        
        # Execute phase with context-aware agents
        result = self._delegate_to_agent(phase, context)
        
        # 🆕 Update context after phase completion
        self.context_builder.update_context(plan_folder, phase_result=result)
        
        return result
```

### Phase 3: Persistence to Tier 2 Knowledge Graph

**Integration:** `src/tier2/knowledge_graph/knowledge_graph.py`

**Post-Execution Learning:**
```python
class KnowledgeGraphIntegration:
    """
    Persists plan execution learnings to Tier 2 knowledge graph.
    """
    
    def persist_plan_learnings(self, plan_folder: Path, execution_result: Dict):
        """
        After plan execution, extract patterns and store in knowledge graph.
        
        Patterns to capture:
        - Security patterns (from git history + execution)
        - Code quality patterns (from AST analysis)
        - Business rule patterns (from comments)
        - Workflow patterns (from phase execution)
        """
        
        kg = KnowledgeGraph()
        
        # 1. Security patterns
        context = ContextRetriever().load_context(plan_folder)
        for file, history in context.git_history['file_histories'].items():
            if history.get('security_fixes'):
                for fix in history['security_fixes']:
                    kg.learn_pattern(
                        pattern={
                            'title': f"Security Pattern: {fix['issue']}",
                            'content': f"File: {file}, Solution: {fix['solution']}",
                            'pattern_type': 'security',
                            'confidence': 0.9,
                            'metadata': {
                                'file': file,
                                'commit': fix['commit'],
                                'date': fix['date'],
                            }
                        },
                        namespace='workspace.security',
                        is_cortex_internal=False,
                    )
        
        # 2. Business rule patterns
        for rule in context.comments.get('business_rules', []):
            kg.learn_pattern(
                pattern={
                    'title': f"Business Rule: {rule['rule'][:50]}",
                    'content': rule['rule'],
                    'pattern_type': 'business_rule',
                    'confidence': 0.8,
                    'metadata': {
                        'file': rule['file'],
                        'line': rule['line'],
                        'priority': rule.get('priority', 'medium'),
                    }
                },
                namespace='workspace.business',
                is_cortex_internal=False,
            )
        
        # 3. Workflow patterns (from execution)
        if execution_result.get('success'):
            kg.learn_pattern(
                pattern={
                    'title': f"Successful Workflow: {plan_folder.name}",
                    'content': f"Phases completed: {len(execution_result['phases'])}",
                    'pattern_type': 'workflow',
                    'confidence': 1.0,
                    'metadata': {
                        'plan_folder': str(plan_folder),
                        'phases': execution_result['phases'],
                        'duration_seconds': execution_result.get('duration', 0),
                    }
                },
                namespace='workspace.workflow',
                is_cortex_internal=False,
            )
        
        logger.info(f"✅ Plan learnings persisted to knowledge graph")
```

---

## 🚀 CORTEX 3.0 Implementation Roadmap

### Sprint 1: Unified Context Builder Foundation (2 weeks)

**Deliverables:**
1. `src/operations/modules/context/unified_context_builder.py`
   - GitHistoryContextBuilder
   - ASTCommentContextBuilder
   - ContextRetriever
   - Storage utilities (YAML/JSON writers)

2. `src/operations/modules/context/__init__.py`
   - Public API exports

3. Tests
   - `tests/operations/modules/context/test_unified_context_builder.py`
   - Mock git history, AST analysis, comment extraction
   - Test YAML/JSON storage

**Success Criteria:**
- ✅ Unit tests pass (>90% coverage)
- ✅ Context builder can gather git history for 100 files in <10 seconds
- ✅ YAML output validated against schema

### Sprint 2: Planning Orchestrator Integration (2 weeks)

**Deliverables:**
1. Update `src/operations/modules/orchestration/planning_orchestrator.py`
   - Add context builder initialization
   - Integrate context building into planning phase
   - Store context in plan folder

2. Context storage schema
   - `cortex-brain/manifests/orchestrators/context-storage-schema.yaml`
   - Define YAML/JSON formats

3. Tests
   - `tests/orchestrators/test_planning_orchestrator_context.py`
   - Test context building during planning
   - Test context storage

**Success Criteria:**
- ✅ Planning orchestrator builds context for all files in plan scope
- ✅ Context stored in `{plan-folder}/context/` directory
- ✅ Integration tests pass

### Sprint 3: Execution Orchestrator Integration (2 weeks)

**Deliverables:**
1. Update `src/orchestrators/plan_execution_orchestrator.py`
   - Add context retriever initialization
   - Load context during phase execution
   - Provide context to execution agents

2. Context-aware agent integration
   - Update TDD orchestrator to consume context
   - Update scaffolding orchestrator to consume context

3. Tests
   - `tests/orchestrators/test_plan_execution_orchestrator_context.py`
   - Test context loading during execution
   - Test context-aware agent behavior

**Success Criteria:**
- ✅ Execution orchestrator loads context at phase start
- ✅ Security warnings displayed for high-risk files
- ✅ Business rules logged during implementation

### Sprint 4: Knowledge Graph Persistence (1 week)

**Deliverables:**
1. `src/operations/modules/context/knowledge_graph_integration.py`
   - KnowledgeGraphIntegration class
   - Pattern extraction from context
   - Tier 2 persistence

2. Tests
   - `tests/operations/modules/context/test_knowledge_graph_integration.py`
   - Test pattern extraction
   - Test Tier 2 storage

**Success Criteria:**
- ✅ Plan learnings persisted to knowledge graph after execution
- ✅ Security patterns, business rules, workflow patterns captured
- ✅ Patterns retrievable via knowledge graph API

### Sprint 5: Documentation & Polish (1 week)

**Deliverables:**
1. Documentation
   - `cortex-brain/documents/implementation-guides/unified-context-builder-guide.md`
   - Update `.github/prompts/CORTEX.prompt.md`
   - Update orchestrator manifests

2. CLI integration
   - Add `context build` command for manual context generation
   - Add `context view` command for context inspection

3. Validation
   - Add SKULL rule validation for context completeness
   - Update healthcheck to verify context builder

**Success Criteria:**
- ✅ Documentation complete
- ✅ CLI commands functional
- ✅ SKULL validation passes

---

## 🔮 CORTEX 4.0 Vision (Q2-Q3 2026)

**Timeline:** April-September 2026  
**Goal:** AI-powered context synthesis with proactive recommendations

### Strategic Pillars

#### Pillar 1: AI Context Synthesis

**Problem:** Current approach: Manual orchestration of components  
**Solution:** LLM-powered context synthesis

**Features:**
1. **Natural Language Context Queries**
   ```python
   context = ai_context_engine.synthesize(
       query="What are the security risks in the authentication module?",
       files=auth_files,
       days_back=365,
   )
   # Returns: LLM-generated summary with evidence links
   ```

2. **Proactive Risk Identification**
   - LLM analyzes git history + AST + comments
   - Identifies patterns humans might miss
   - Example: "Login.py has 5 SQL injection fixes in past year, but no parameterized query pattern. Recommend architectural refactor."

3. **Expert Identification with Reasoning**
   - Not just "alice has 25 commits"
   - "Contact alice: 25 commits (18 security-focused), fixed similar SQL injection in UserRepository.py on 2025-03-15"

#### Pillar 2: Temporal Context Tracking

**Problem:** Context is static snapshot  
**Solution:** Time-series context with trend analysis

**Features:**
1. **Context Evolution Tracking**
   ```yaml
   # context/temporal-analysis.yaml
   src/auth/login.py:
     security_trend:
       2025_Q1: 5 security fixes
       2025_Q2: 3 security fixes
       2025_Q3: 1 security fix
       2025_Q4: 0 security fixes
       conclusion: "Improving trend - systemic issues addressed"
   ```

2. **Predictive Risk Scoring**
   - ML model trained on git history + execution outcomes
   - Predicts likelihood of defects based on change patterns
   - Example: "File complexity increased 40% in past 30 days + 3 authors modified concurrently = 78% defect risk"

#### Pillar 3: Cross-Repository Learning

**Problem:** Each repository learns in isolation  
**Solution:** Federated knowledge graph across user's repositories

**Features:**
1. **Organization-Wide Pattern Library**
   - Security patterns learned in Repo A available in Repo B
   - Business rule patterns shared across microservices
   - Compliance patterns reused across projects

2. **Expert Network Graph**
   - "Alice is security expert across 5 repositories"
   - "Bob wrote similar authentication logic in ProjectX - recommend consultation"

3. **Compliance Drift Detection**
   - "ProjectA has GDPR consent pattern, but ProjectB doesn't - compliance risk"
   - "PCI-DSS tokenization pattern in ProjectC can be reused in ProjectD"

#### Pillar 4: Continuous Context Refresh

**Problem:** Context becomes stale as code evolves  
**Solution:** Incremental context updates via file watchers

**Features:**
1. **Real-Time Context Updates**
   - File watcher detects changes
   - Incremental AST update (not full re-parse)
   - Incremental git log update (only new commits)

2. **Context Invalidation Triggers**
   - Major refactor detected → Flag context as stale
   - Security fix committed → Update security patterns
   - Business rule comment changed → Re-extract business rules

3. **Background Context Maintenance**
   - Nightly job: Update git history for all active plans
   - Weekly job: Re-analyze AST for changed files
   - Monthly job: Full context rebuild for archival plans

#### Pillar 5: Visualization & Exploration

**Problem:** YAML/JSON context is not human-friendly  
**Solution:** Interactive context dashboards

**Features:**
1. **CORTEX Lens Integration**
   - Context dashboard showing git history, AST, comments
   - Interactive code graph with security overlays
   - Temporal charts showing evolution

2. **Context Diff Visualization**
   - Compare context between plan versions
   - Show what changed since last execution
   - Highlight new security risks

3. **Expert Heatmaps**
   - Show author contributions overlaid on codebase
   - Identify knowledge silos
   - Recommend pair programming opportunities

---

## 🏗️ CORTEX 4.0 Architecture

### Layered Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Orchestrator Layer                        │
│  (Planning, Execution, TDD, ADO - consume context)          │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│              AI Context Synthesis Engine (New)               │
│  - LLM-powered context synthesis                             │
│  - Natural language queries                                  │
│  - Proactive risk identification                             │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│            Unified Context Builder (CORTEX 3.0)              │
│  - GitHistoryContextBuilder                                  │
│  - ASTCommentContextBuilder                                  │
│  - ContextRetriever                                          │
│  - Temporal tracking                                         │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│              Infrastructure Components                       │
│  - GitAnalyzerCrawler    - CommentCollector                  │
│  - ASTNarrativeOrch      - DependencyGraphGenerator          │
│  - KnowledgeGraph        - FileWatcher (New)                 │
└─────────────────────────────────────────────────────────────┘
                            ▲
                            │
┌─────────────────────────────────────────────────────────────┐
│                  Tier 2: Knowledge Graph                     │
│  - Pattern storage (security, business, workflow)            │
│  - Cross-repository federation (New)                         │
│  - ML model training data (New)                              │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Layer | Component | Responsibility |
|-------|-----------|----------------|
| Orchestrator | Planning/Execution | Consume context, make decisions |
| AI Synthesis | AI Context Engine | LLM-powered analysis, proactive recommendations |
| Context Builder | Unified Context Builder | Orchestrate infrastructure, store/retrieve context |
| Infrastructure | Git/AST/Comments | Raw data collection |
| Tier 2 | Knowledge Graph | Pattern storage, cross-repo learning |

---

## 📊 Success Metrics

### CORTEX 3.0 (Q1 2026)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Context build time | <10s for 100 files | Performance benchmark |
| Context accuracy | >95% | Manual validation of git history, AST, comments |
| Context reuse | >80% | Plans that reuse context from previous phases |
| Security pattern detection | >90% | Compare manual review vs automated detection |
| Developer satisfaction | >4.0/5.0 | Survey: "Context helps me understand risks" |

### CORTEX 4.0 (Q3 2026)

| Metric | Target | Measurement |
|--------|--------|-------------|
| AI synthesis quality | >90% | Human eval: "Synthesis is actionable" |
| Proactive risk detection | >85% | Risks identified before implementation |
| Cross-repo pattern reuse | >50% | Patterns from other repos applied |
| Context staleness | <7 days | Average age of context data |
| Developer productivity | +30% | Time to implement features (before/after) |

---

## 🚨 Risk Assessment & Mitigation

### CORTEX 3.0 Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Performance degradation (context building slows planning) | HIGH | MEDIUM | Async context building, caching, incremental updates |
| Storage bloat (context files grow large) | MEDIUM | HIGH | Compression, retention policies, archival |
| Integration complexity (many components to orchestrate) | HIGH | MEDIUM | Phased rollout, extensive testing, rollback plan |
| False positive security warnings | MEDIUM | MEDIUM | Tuning thresholds, user feedback loop |

### CORTEX 4.0 Risks

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| LLM hallucination (AI synthesis generates incorrect conclusions) | HIGH | MEDIUM | Evidence linking, confidence scoring, human review gates |
| Privacy concerns (cross-repo learning exposes sensitive data) | HIGH | LOW | Namespace isolation, opt-in federation, data anonymization |
| Temporal drift (context becomes stale, leads to bad decisions) | HIGH | MEDIUM | Continuous refresh, staleness alerts, auto-invalidation |
| Complexity explosion (too many features, unmaintainable) | HIGH | MEDIUM | Strict modularity, SKULL enforcement, phased deprecation |

---

## 🎯 Recommended Action Plan

### Immediate (This Week)

1. ✅ **Review this document** with team
2. ✅ **Approve CORTEX 3.0 strategy** (Sprints 1-5)
3. ✅ **Create sprint board** with deliverables
4. ✅ **Assign engineers** to Sprint 1 tasks

### Near-Term (Q1 2026)

1. **Execute CORTEX 3.0 roadmap** (Sprints 1-5)
2. **Pilot with 2-3 internal projects**
3. **Gather feedback** and iterate
4. **Document learnings** for CORTEX 4.0

### Long-Term (Q2-Q3 2026)

1. **Prototype AI Context Synthesis Engine**
2. **Evaluate LLM options** (GPT-4, Claude, local models)
3. **Design federated knowledge graph** architecture
4. **Build CORTEX Lens context dashboards**
5. **Launch CORTEX 4.0 beta**

---

## 📚 Related Documents

1. **PLANNING-ORCHESTRATOR-HOLISTIC-REVIEW-2025-12-15.md**
   - Foundation for this analysis
   - Visual tracker restoration plan
   - Semantic folder organization

2. **cortex-brain/brain-protection-rules.yaml**
   - GIT_HISTORY_CONTEXT_REQUIRED (Lines 3363-3368)
   - Critical SKULL rule requiring git history integration

3. **cortex-brain/manifests/orchestrators/manifest-schema.yaml**
   - Manifest structure for orchestrator compliance
   - Context requirements definition

4. **src/tier2/knowledge_graph/knowledge_graph.py**
   - Tier 2 pattern storage implementation
   - Target for context persistence

---

## ✅ Sign-Off

**Document Status:** ✅ Ready for Review  
**Approval Required:** Asif Hussain (Architecture Lead)  
**Implementation Start:** Pending approval  
**Target Completion:** March 31, 2026 (CORTEX 3.0)

---

**End of Document**
