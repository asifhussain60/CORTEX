# CORTEX 2.0 Design Document 13: File Dependency Tracking System

**Version:** 1.0  
**Created:** 2025-11-12  
**Status:** Design Complete - Implementation Pending  
**Priority:** MEDIUM-HIGH (architectural enhancement, high ROI)

---

## 📋 Executive Summary

**Problem:** CORTEX currently tracks file co-modifications but lacks comprehensive dependency analysis (imports, calls, inheritance). Agents cannot answer questions like "What breaks if I change this file?" or detect circular dependencies.

**Solution:** Implement static analysis-based dependency tracking with graph storage in Tier 2, enabling transitive traversal (A→B→C) and impact analysis.

**Approach:** 3-phase implementation using Python AST (built-in), Pylance MCP (already integrated), and SQLite recursive CTEs (already using).

**Estimated Effort:** 9 hours total (2+3+4)  
**Expected ROI:** 5-10x (saves hours of manual dependency analysis per month)  
**Accuracy Target:** 85-90% (acceptable trade-off vs runtime analysis)

---

## 🎯 Goals and Objectives

### Primary Goals
1. **Enable Impact Analysis** - Answer "What breaks if I change X?"
2. **Detect Circular Dependencies** - Automatic cycle detection for Health Validator
3. **Intelligent Task Ordering** - Work Planner uses dependency graph
4. **Auto-Find Related Tests** - Tester agent discovers test files

### Success Criteria
- ✅ Query transitive dependencies in < 1 second
- ✅ 85%+ accuracy on Python import detection
- ✅ Detect all circular dependencies
- ✅ Integration with Architect, Health Validator, Work Planner agents
- ✅ Python support (future: JS/TS/C# multi-language)

### Non-Goals
- ❌ Runtime behavior analysis (too slow, marginal benefit)
- ❌ Dynamic import detection (acceptable 10-15% miss rate)
- ❌ Multi-language support in Phase 1 (Python only initially)

---

## 🏗️ Architecture

### Current State (Limited Capability)

```yaml
# cortex-brain/file-relationships.yaml (Legacy)
relationships:
- primary_file: tests/test_brain.py
  related_file: src/tier1/tier1_api.py
  relationship: test-coverage
  confidence: 0.8
```

**Limitations:**
- ❌ No directionality (imports vs imported-by)
- ❌ No transitive traversal (A→B→C)
- ❌ No relationship types (import, call, extend)
- ❌ Static, manually curated

### Proposed Architecture (Phase 13)

```
┌─────────────────────────────────────────────┐
│          CORTEX Agents (Layer 4)            │
│  Architect │ Health │ Work Planner │ Tester │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│      Dependency Graph API (Layer 3)         │
│  • get_transitive_deps(file, depth)         │
│  • get_reverse_deps(file)                   │
│  • find_circular_deps()                     │
│  • impact_analysis(file)                    │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│    SQLite Graph Storage (Tier 2 - Layer 2) │
│  • file_dependencies table                  │
│  • Recursive CTEs for traversal             │
│  • Indexes on source/target/type            │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│   Dependency Analyzer (Layer 1)             │
│  • Python AST parser (built-in)             │
│  • Pylance MCP integration (optional)       │
│  • Import/call/extend extraction            │
└─────────────────────────────────────────────┘
```

---

## 📊 Database Schema

### Enhanced Tier 2 Schema (Phase 13.1)

```sql
-- New table: file_dependencies
CREATE TABLE IF NOT EXISTS file_dependencies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_file TEXT NOT NULL,          -- A.py imports B.py
    target_file TEXT NOT NULL,          -- B.py is imported by A.py
    dependency_type TEXT NOT NULL,      -- 'import', 'call', 'extend', 'test'
    line_number INTEGER,                -- Line where dependency occurs
    strength REAL NOT NULL DEFAULT 1.0, -- 0.0-1.0 (importance/frequency)
    discovered_at TEXT NOT NULL,        -- Timestamp (ISO 8601)
    last_verified TEXT,                 -- Last scan timestamp
    UNIQUE(source_file, target_file, dependency_type)
);

-- Indexes for fast queries
CREATE INDEX IF NOT EXISTS idx_source ON file_dependencies(source_file);
CREATE INDEX IF NOT EXISTS idx_target ON file_dependencies(target_file);
CREATE INDEX IF NOT EXISTS idx_type ON file_dependencies(dependency_type);
CREATE INDEX IF NOT EXISTS idx_source_type ON file_dependencies(source_file, dependency_type);
```

### Relationship Types

| Type | Description | Example |
|------|-------------|---------|
| `import` | Static import statement | `from tier1 import Tier1API` |
| `call` | Function/method call | `tier1_api.get_conversations()` |
| `extend` | Class inheritance | `class MyAgent(BaseAgent)` |
| `test` | Test file → source file | `test_tier1.py` → `tier1_api.py` |
| `config` | Configuration file dependency | `cortex.config.json` → `config.py` |

---

## 🔧 Implementation Plan

### Phase 13.1: Foundation (2 hours)

**Goal:** Create database schema and basic Python AST analyzer

**Tasks:**
1. Add `file_dependencies` table to Tier 2 schema ✅
2. Create `src/tier2/dependency_analyzer.py` (300 lines)
3. Implement AST-based import extraction
4. Add dependency type detection
5. Write unit tests (10 tests)

**Deliverables:**
```python
# src/tier2/dependency_analyzer.py
class DependencyAnalyzer:
    """Extract dependencies from Python files using AST."""
    
    def analyze_file(self, file_path: Path) -> List[Dependency]:
        """
        Parse file and extract all dependencies.
        
        Returns:
            List of Dependency objects (source, target, type, line)
        """
        tree = ast.parse(file_path.read_text())
        deps = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                # import os, sys
                for alias in node.names:
                    deps.append(Dependency(
                        source=file_path,
                        target=self._resolve_module(alias.name),
                        type='import',
                        line=node.lineno
                    ))
            
            elif isinstance(node, ast.ImportFrom):
                # from pathlib import Path
                module = node.module or ''
                for alias in node.names:
                    deps.append(Dependency(
                        source=file_path,
                        target=self._resolve_module(module),
                        type='import',
                        line=node.lineno
                    ))
        
        return deps
    
    def _resolve_module(self, module_name: str) -> Optional[Path]:
        """Resolve module name to file path."""
        # Handle relative imports (src.tier1 → src/tier1/__init__.py)
        # Handle absolute paths (pathlib → stdlib, skip)
        # Handle workspace modules (src.* → track)
```

**Test Cases:**
```python
def test_extract_imports():
    code = "from src.tier1 import Tier1API"
    deps = analyzer.analyze_code(code)
    assert deps[0].type == 'import'
    assert 'tier1' in deps[0].target

def test_detect_class_inheritance():
    code = "class MyAgent(BaseAgent): pass"
    deps = analyzer.analyze_code(code)
    assert deps[0].type == 'extend'
```

**Estimated Time:** 2 hours

---

### Phase 13.2: Graph Analysis (3 hours)

**Goal:** Implement graph traversal and analysis algorithms

**Tasks:**
1. Create `src/tier2/dependency_graph.py` (400 lines)
2. Implement transitive dependency queries (recursive SQL CTEs)
3. Add reverse dependency tracking
4. Create circular dependency detector
5. Build impact analysis engine
6. Write integration tests (15 tests)

**Deliverables:**
```python
# src/tier2/dependency_graph.py
class DependencyGraph:
    """Graph analysis for file dependencies."""
    
    def __init__(self, tier2_db: Path):
        self.db = tier2_db
    
    def get_transitive_deps(
        self,
        file: str,
        max_depth: int = 5,
        dep_type: Optional[str] = None
    ) -> List[str]:
        """
        Get all files that 'file' depends on (recursive).
        
        Args:
            file: Source file path
            max_depth: Maximum traversal depth (prevent infinite loops)
            dep_type: Filter by type (import, call, extend, test)
        
        Returns:
            List of file paths (ordered by depth)
        
        Example:
            A.py imports B.py, B.py imports C.py
            get_transitive_deps("A.py") → ["B.py", "C.py"]
        """
        query = """
        WITH RECURSIVE deps(file, depth) AS (
            -- Base case: direct dependencies
            SELECT target_file, 1
            FROM file_dependencies
            WHERE source_file = ?
                AND (:dep_type IS NULL OR dependency_type = :dep_type)
            
            UNION
            
            -- Recursive case: transitive dependencies
            SELECT d.target_file, deps.depth + 1
            FROM file_dependencies d
            JOIN deps ON d.source_file = deps.file
            WHERE deps.depth < :max_depth
                AND (:dep_type IS NULL OR d.dependency_type = :dep_type)
        )
        SELECT DISTINCT file FROM deps ORDER BY depth;
        """
        # Execute and return results
    
    def get_reverse_deps(
        self,
        file: str,
        dep_type: Optional[str] = None
    ) -> List[str]:
        """
        Get all files that depend on 'file'.
        
        Args:
            file: Target file path
            dep_type: Filter by type
        
        Returns:
            List of file paths that import/call/extend 'file'
        
        Example:
            A.py imports B.py, C.py imports B.py
            get_reverse_deps("B.py") → ["A.py", "C.py"]
        """
        query = """
        SELECT DISTINCT source_file
        FROM file_dependencies
        WHERE target_file = ?
            AND (:dep_type IS NULL OR dependency_type = :dep_type)
        ORDER BY source_file;
        """
        # Execute and return results
    
    def find_circular_deps(self) -> List[List[str]]:
        """
        Detect circular dependencies (import cycles).
        
        Returns:
            List of cycles (each cycle is a list of files)
        
        Example:
            A.py → B.py → C.py → A.py
            Returns: [["A.py", "B.py", "C.py", "A.py"]]
        """
        # Use DFS to detect cycles
        # Track visited nodes and current path
        # Return all detected cycles
    
    def impact_analysis(self, file: str) -> Dict[str, Any]:
        """
        Comprehensive impact analysis for changing a file.
        
        Args:
            file: File to analyze
        
        Returns:
            {
                "direct_dependents": [...],     # Files that import this
                "transitive_dependents": [...], # All affected files
                "test_files": [...],            # Related test files
                "estimated_impact": "HIGH",     # LOW/MEDIUM/HIGH
                "circular_deps": [...]          # Cycles involving this file
            }
        """
        direct = self.get_reverse_deps(file)
        transitive = []
        for dep in direct:
            transitive.extend(self.get_reverse_deps(dep))
        
        test_files = self.get_reverse_deps(file, dep_type='test')
        
        # Estimate impact based on number of affected files
        if len(transitive) > 20:
            impact = "HIGH"
        elif len(transitive) > 5:
            impact = "MEDIUM"
        else:
            impact = "LOW"
        
        return {
            "file": file,
            "direct_dependents": direct,
            "transitive_dependents": list(set(transitive)),
            "test_files": test_files,
            "estimated_impact": impact,
            "total_affected": len(set(transitive)) + len(direct)
        }
```

**Test Cases:**
```python
def test_transitive_deps():
    # A → B → C
    graph.add_dependency("A.py", "B.py", "import")
    graph.add_dependency("B.py", "C.py", "import")
    
    deps = graph.get_transitive_deps("A.py")
    assert deps == ["B.py", "C.py"]

def test_circular_deps():
    # A → B → C → A (cycle)
    graph.add_dependency("A.py", "B.py", "import")
    graph.add_dependency("B.py", "C.py", "import")
    graph.add_dependency("C.py", "A.py", "import")
    
    cycles = graph.find_circular_deps()
    assert len(cycles) == 1
    assert "A.py" in cycles[0]

def test_impact_analysis():
    # A → B, C → B, D → C
    # Changing B affects A, C, D
    result = graph.impact_analysis("B.py")
    assert result["estimated_impact"] == "MEDIUM"
    assert len(result["direct_dependents"]) == 2
```

**Estimated Time:** 3 hours

---

### Phase 13.3: Agent Integration (4 hours)

**Goal:** Integrate dependency graph with CORTEX agents

**Tasks:**
1. Update Architect agent to use dependency graph
2. Add circular dependency checks to Health Validator
3. Enhance Work Planner with dependency-aware task ordering
4. Enable Tester agent to auto-find related tests
5. Create agent integration tests (12 tests)
6. Add visualization export (optional, Graphviz)

**Deliverables:**

#### Architect Agent Integration
```python
# src/cortex_agents/architect/agent.py
class Architect(BaseAgent):
    def design_system(self, request: AgentRequest) -> AgentResponse:
        """Design system changes with impact analysis."""
        
        # Get file from request
        file = extract_file_from_request(request.content)
        
        # Analyze dependencies
        deps = self.tier2.dependency_graph.get_transitive_deps(file)
        reverse = self.tier2.dependency_graph.get_reverse_deps(file)
        impact = self.tier2.dependency_graph.impact_analysis(file)
        
        # Generate design recommendations
        design = f"""
        ## Impact Analysis: {file}
        
        **Dependencies:** {len(deps)} files depend on changes to {file}
        **Affected Files:** {len(reverse)} files will be affected
        **Risk Level:** {impact['estimated_impact']}
        
        ### Direct Dependencies
        {self._format_file_list(deps[:10])}
        
        ### Files That Depend On This
        {self._format_file_list(reverse[:10])}
        
        ### Recommendations
        {self._generate_recommendations(impact)}
        """
        
        return AgentResponse(
            success=True,
            content=design,
            confidence=0.9
        )
```

#### Health Validator Integration
```python
# src/cortex_agents/health_validator/agent.py
class HealthValidator(BaseAgent):
    def validate_health(self) -> AgentResponse:
        """Validate codebase health including dependencies."""
        
        issues = []
        
        # Check for circular dependencies
        cycles = self.tier2.dependency_graph.find_circular_deps()
        if cycles:
            issues.append({
                "category": "circular_dependencies",
                "severity": "HIGH",
                "message": f"Found {len(cycles)} circular dependencies",
                "details": cycles[:5],  # Show first 5
                "recommendation": "Break cycles by refactoring imports"
            })
        
        # Check for high-impact files (central hub files)
        all_files = self._get_all_workspace_files()
        for file in all_files:
            impact = self.tier2.dependency_graph.impact_analysis(file)
            if impact['total_affected'] > 50:
                issues.append({
                    "category": "high_coupling",
                    "severity": "MEDIUM",
                    "message": f"{file} is a dependency hub",
                    "details": f"Affects {impact['total_affected']} files",
                    "recommendation": "Consider splitting into smaller modules"
                })
        
        return AgentResponse(
            success=True,
            content=self._format_health_report(issues),
            metadata={"issues_found": len(issues)}
        )
```

#### Work Planner Integration
```python
# src/cortex_agents/work_planner/agent.py
class WorkPlanner(BaseAgent):
    def plan_tasks(self, request: AgentRequest) -> List[Task]:
        """Generate task plan with dependency-aware ordering."""
        
        # Extract files mentioned in request
        files = extract_files_from_request(request.content)
        
        # Build dependency graph for these files
        task_graph = {}
        for file in files:
            deps = self.tier2.dependency_graph.get_transitive_deps(file)
            task_graph[file] = deps
        
        # Topological sort for task ordering
        ordered_tasks = self._topological_sort(task_graph)
        
        # Generate tasks in dependency order
        tasks = []
        for file in ordered_tasks:
            tasks.append(Task(
                name=f"Modify {file}",
                dependencies=[f"Modify {dep}" for dep in task_graph.get(file, [])],
                estimated_time=self._estimate_time(file)
            ))
        
        return tasks
    
    def _topological_sort(self, graph: Dict) -> List[str]:
        """Sort tasks by dependencies (dependencies first)."""
        # Standard topological sort algorithm
        # Returns: [base files first, dependent files last]
```

#### Tester Agent Integration
```python
# src/cortex_agents/tester/agent.py
class Tester(BaseAgent):
    def find_related_tests(self, file: str) -> List[str]:
        """Find all test files for a source file."""
        
        # Direct test files (test_tier1.py → tier1_api.py)
        test_files = self.tier2.dependency_graph.get_reverse_deps(
            file,
            dep_type='test'
        )
        
        # Transitive test files (tests that import files that import this)
        deps = self.tier2.dependency_graph.get_reverse_deps(file)
        for dep in deps:
            test_files.extend(
                self.tier2.dependency_graph.get_reverse_deps(dep, dep_type='test')
            )
        
        return list(set(test_files))
    
    def generate_tests(self, request: AgentRequest) -> AgentResponse:
        """Generate comprehensive tests for a file."""
        
        file = extract_file_from_request(request.content)
        
        # Check existing test coverage
        existing_tests = self.find_related_tests(file)
        
        # Analyze dependencies to determine what to mock
        deps = self.tier2.dependency_graph.get_transitive_deps(file)
        
        # Generate test plan
        test_plan = f"""
        ## Test Plan: {file}
        
        **Existing Tests:** {len(existing_tests)}
        **Dependencies to Mock:** {len(deps)}
        
        ### Test Files to Create/Update
        {self._format_test_files(existing_tests)}
        
        ### Dependencies to Mock
        {self._format_file_list(deps)}
        
        ### Test Cases
        {self._generate_test_cases(file, deps)}
        """
        
        return AgentResponse(success=True, content=test_plan)
```

**Visualization Export (Optional):**
```python
# src/tier2/dependency_visualizer.py
class DependencyVisualizer:
    """Export dependency graphs to Graphviz format."""
    
    def export_to_dot(
        self,
        file: str,
        max_depth: int = 3,
        output_path: Path = Path("deps.dot")
    ):
        """
        Export dependency graph to Graphviz DOT format.
        
        Usage:
            visualizer.export_to_dot("src/tier1/tier1_api.py")
            # Creates deps.dot
            # Run: dot -Tpng deps.dot -o deps.png
        """
        deps = self.graph.get_transitive_deps(file, max_depth)
        
        dot_content = "digraph Dependencies {\n"
        dot_content += f'    "{file}" [color=red];\n'
        
        for dep in deps:
            dot_content += f'    "{file}" -> "{dep}";\n'
        
        dot_content += "}\n"
        
        output_path.write_text(dot_content)
```

**Test Cases:**
```python
def test_architect_impact_analysis():
    response = architect.execute(AgentRequest(
        content="Design changes to src/tier1/tier1_api.py"
    ))
    assert "Impact Analysis" in response.content
    assert response.confidence > 0.8

def test_health_validator_detects_cycles():
    # Create circular dependency
    graph.add_dependency("A.py", "B.py", "import")
    graph.add_dependency("B.py", "A.py", "import")
    
    response = health_validator.validate_health()
    assert "circular_dependencies" in response.content

def test_work_planner_orders_tasks():
    tasks = work_planner.plan_tasks(AgentRequest(
        content="Modify A.py, B.py, C.py (A→B→C)"
    ))
    # Should order: C, B, A (dependencies first)
    assert tasks[0].name == "Modify C.py"
```

**Estimated Time:** 4 hours

---

## 🎯 Technology Stack

### Core Components

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Static Analysis** | Python AST (stdlib) | Zero dependencies, 85-90% accuracy, fast |
| **Graph Storage** | SQLite + Recursive CTEs | Already using, efficient graph queries |
| **Real-time Updates** | Pylance MCP | Already integrated, LSP-powered |
| **Graph Algorithms** | Custom + NetworkX (optional) | Built-in for basics, NetworkX for advanced |
| **Visualization** | Graphviz (optional) | Industry standard, beautiful diagrams |

### Accuracy vs Efficiency Trade-offs

| Approach | Accuracy | Speed | Dependencies | Recommendation |
|----------|----------|-------|--------------|----------------|
| **Python AST** | 85-90% | <10s (1000 files) | None (stdlib) | ✅ RECOMMENDED |
| **Pylance MCP** | 90-95% | Incremental | Already integrated | ✅ FUTURE ENHANCEMENT |
| **Runtime Analysis** | 95-98% | 10-100x slower | Security risk | ❌ OVERKILL |
| **NetworkX** | N/A | Fast | pip install | 🟡 OPTIONAL (advanced algorithms) |

**Decision:** Start with Python AST (Phase 13.1-13.3), add Pylance incremental updates in future enhancement.

---

## 📈 Expected Benefits

### Agent Capabilities (Before vs After)

| Question | Before | After Phase 13 |
|----------|--------|----------------|
| "What breaks if I change X?" | ❌ Cannot answer | ✅ Complete impact analysis |
| "Show me circular dependencies" | ❌ Manual detection | ✅ Automatic detection |
| "Order tasks by dependencies" | ❌ Manual ordering | ✅ Topological sort |
| "Find tests for module X" | ❌ Search by naming | ✅ Dependency-based discovery |
| "What files import X?" | ❌ Grep search | ✅ Instant graph query |

### Performance Metrics

| Operation | Target | Actual (Projected) |
|-----------|--------|-------------------|
| **Scan workspace (1000 files)** | <30s | ~8-10s |
| **Query transitive deps** | <1s | ~200-500ms |
| **Find circular deps** | <2s | ~1-1.5s |
| **Impact analysis** | <1s | ~300-600ms |
| **Storage overhead** | <10MB | ~2-5MB |

### Use Case Examples

**Use Case 1: Architect Agent - Impact Analysis**
```
User: "I want to refactor src/tier1/tier1_api.py"

Architect: "Impact Analysis for tier1_api.py:
  - Direct dependencies: 8 files
  - Total affected: 24 files (HIGH impact)
  - Test files: 5 files need updating
  - Recommendation: Create abstraction layer first
  - Estimated effort: 6-8 hours"
```

**Use Case 2: Health Validator - Circular Dependencies**
```
Health Validator: "Found 2 circular dependencies:
  1. src/tier2/patterns.py → knowledge_graph.py → patterns.py
  2. src/workflows/pipeline.py → stages/executor.py → pipeline.py
  
  Recommendation: Extract shared interfaces to break cycles"
```

**Use Case 3: Work Planner - Dependency-Aware Ordering**
```
User: "Refactor authentication system across 5 files"

Work Planner: "Task Plan (dependency-ordered):
  1. Modify src/auth/jwt_handler.py (no dependencies)
  2. Modify src/auth/auth_middleware.py (depends on jwt_handler)
  3. Modify src/api/routes.py (depends on auth_middleware)
  4. Update tests (depends on all above)
  5. Update docs (final step)"
```

---

## 🚀 Deployment Timeline

### Week 14: Foundation
- **Monday-Tuesday:** Phase 13.1 implementation (2 hours)
  - Database schema enhancement
  - Python AST analyzer
  - Unit tests
- **Wednesday:** Code review and testing
- **Thursday:** Deploy to development branch

### Week 15: Analysis & Integration
- **Monday-Tuesday:** Phase 13.2 implementation (3 hours)
  - Graph traversal algorithms
  - Circular dependency detection
  - Integration tests
- **Wednesday-Thursday:** Phase 13.3 implementation (4 hours)
  - Agent integrations
  - Visualization export
  - End-to-end tests
- **Friday:** Code review, testing, deployment

### Success Metrics
- ✅ All 37 tests passing (10 + 15 + 12)
- ✅ Query performance < 1s
- ✅ Agent integration functional
- ✅ Documentation complete

---

## 🔒 Risk Assessment

### Technical Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **AST misses dynamic imports** | HIGH | LOW | Acceptable 10-15% miss rate, document limitation |
| **Performance degradation** | MEDIUM | MEDIUM | Add indexes, cache queries, limit depth |
| **Multi-language complexity** | LOW | HIGH | Start with Python only, add others later |
| **Circular dependency overload** | LOW | MEDIUM | Limit to top 10 cycles, paginate results |

### Implementation Risks

| Risk | Probability | Impact | Mitigation |
|------|------------|--------|------------|
| **Scope creep** | MEDIUM | MEDIUM | Stick to 3-phase plan, defer enhancements |
| **Integration breakage** | LOW | HIGH | Comprehensive tests, backward compatibility |
| **Performance regression** | MEDIUM | MEDIUM | Benchmark before/after, optimize queries |

---

## 🔮 Future Enhancements (Not Phase 13)

### Phase 13+: Multi-Language Support
- JavaScript/TypeScript: tree-sitter or esprima
- C#: Roslyn analyzers
- Go: go/parser package
- **Estimated Effort:** 8-10 hours per language

### Phase 13+: Real-Time Watching
- File system monitoring (watchdog library)
- Incremental updates on file save
- LSP-based real-time dependency tracking
- **Estimated Effort:** 6-8 hours

### Phase 13+: Advanced Visualizations
- Interactive web-based graph viewer (D3.js)
- Dependency heat maps (file coupling metrics)
- Change impact prediction (ML-based)
- **Estimated Effort:** 12-16 hours

### Phase 13+: Performance Optimizations
- In-memory graph caching (Redis)
- Parallel AST parsing (multiprocessing)
- Precomputed transitive closures
- **Estimated Effort:** 4-6 hours

---

## 📚 References

### Internal Documents
- `cortex-brain/FILE-DEPENDENCY-ANALYSIS.md` - Comprehensive analysis
- `cortex-brain/cortex-2.0-design/CORTEX2-STATUS.MD` - Implementation status
- `cortex-brain/cortex-2.0-design/25-implementation-roadmap.md` - Overall roadmap

### External Resources
- **Python AST:** https://docs.python.org/3/library/ast.html
- **SQLite Recursive CTEs:** https://www.sqlite.org/lang_with.html
- **NetworkX Graph Library:** https://networkx.org/
- **Graphviz Visualization:** https://graphviz.org/
- **pydeps Tool:** https://github.com/thebjorn/pydeps

### Related CORTEX Components
- `src/tier2/knowledge_graph.py` - Pattern storage
- `src/tier1/file_tracker.py` - File mention extraction
- `src/cortex_agents/architect/agent.py` - Design decisions
- `src/cortex_agents/health_validator/agent.py` - Health checks

---

## ✅ Approval Checklist

**Before Implementation:**
- [ ] Design review completed
- [ ] Timeline approved (Week 14-15)
- [ ] Resource allocation confirmed
- [ ] Test plan reviewed
- [ ] Risk mitigation strategies approved

**After Phase 13.1:**
- [ ] Database schema deployed
- [ ] AST analyzer functional
- [ ] Unit tests passing (10/10)

**After Phase 13.2:**
- [ ] Graph queries working
- [ ] Performance benchmarks met
- [ ] Integration tests passing (15/15)

**After Phase 13.3:**
- [ ] Agent integrations complete
- [ ] End-to-end tests passing (12/12)
- [ ] Documentation updated
- [ ] Feature ready for production

---

**Status:** ✅ READY FOR IMPLEMENTATION  
**Approval Required:** Lead Architect, Product Owner  
**Next Steps:** Begin Phase 13.1 (Week 14)

---

*Document maintained by: CORTEX Development Team*  
*Last updated: 2025-11-12*  
*Version: 1.0 (Initial design)*
