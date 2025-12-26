# Discovery Orchestrator v1 - Master Plan

**Plan ID:** discovery-orchestrator-v1  
**Created:** 2024-12-16  
**Status:** Planning  
**Tier:** 4 (Complex)  
**Author:** Asif Hussain  

---

## 🎯 Executive Summary

The **Discovery Orchestrator** is a powerful new CORTEX orchestrator that provides comprehensive codebase exploration, analysis, and knowledge extraction capabilities. It addresses the critical need for intelligent code discovery before any modifications, enforcing SKULL's HOLISTIC_CODE_DISCOVERY_ENFORCEMENT rule while providing developers with deep insights into project structure, dependencies, patterns, and technical debt.

### Key Capabilities

1. **Multi-Layer Discovery** - File system, AST analysis, semantic search, git history
2. **Intelligent Analysis** - Pattern detection, dependency mapping, complexity assessment
3. **Knowledge Extraction** - Automatic documentation, insight generation, recommendation engine
4. **Integration Ready** - Works with Planning System, TDD Orchestrator, and all CORTEX agents
5. **Interactive & Autonomous** - Supports both guided exploration and automated discovery workflows

### Why This Matters

- **Prevents Duplication** - Finds existing implementations before creating new ones
- **Reduces Tech Debt** - Identifies opportunities for consolidation and refactoring
- **Accelerates Onboarding** - New developers understand the codebase faster
- **Improves Quality** - Discovers anti-patterns, unused code, and architectural issues
- **Enables Better Planning** - Provides comprehensive context for feature planning

---

## 📊 Complexity Analysis

**Total Score:** 78/100 (HIGH Complexity)

| Dimension | Score | Reasoning |
|-----------|-------|-----------|
| Technical | 18/25 | AST parsing, graph algorithms, FTS5 integration |
| Integration | 16/20 | Integrates with 5+ CORTEX systems |
| Scope | 15/20 | Multi-phase workflow with 6 major phases |
| Risk | 14/20 | Performance optimization critical, large codebase handling |
| Dependencies | 15/15 | Depends on Tier 2, Planning System, git integration |

**Tier Classification:** Tier 4 (COMPLEX)  
**Estimated Duration:** 2-3 weeks  
**Requires:** Architecture review, incremental implementation, comprehensive testing

---

## 🏗️ Architecture Overview

### System Components

```
DiscoveryOrchestrator (BaseOperationModule)
├── Phase 1: Scope Definition
│   ├── PathResolver - Determine discovery scope
│   ├── ExclusionEngine - Apply .gitignore/.cortexignore
│   └── ScopeValidator - Validate input parameters
├── Phase 2: File Discovery
│   ├── FileSystemScanner - Recursive file enumeration
│   ├── LanguageDetector - Identify file types
│   └── MetricsCollector - Size, line count, file count
├── Phase 3: Code Analysis
│   ├── ASTParser - Parse Python/C#/JS/TS files
│   ├── DependencyMapper - Build import/reference graph
│   ├── ComplexityAnalyzer - Cyclomatic complexity, maintainability
│   └── PatternDetector - Identify design patterns
├── Phase 4: Semantic Discovery
│   ├── SemanticIndexer - Build search index
│   ├── SimilarityEngine - Find duplicate/similar code
│   └── KnowledgeGraphIntegration - Link to Tier 2
├── Phase 5: Historical Context
│   ├── GitHistoryAnalyzer - Commit history, blame, churn
│   ├── AuthorshipMapper - Identify code owners
│   └── EvolutionTracker - Track code evolution
└── Phase 6: Reporting & Recommendations
    ├── ReportGenerator - Generate comprehensive reports
    ├── InsightEngine - Extract actionable insights
    └── RecommendationSystem - Suggest next steps
```

### Integration Points

- **Planning System** - Pre-planning discovery phase
- **TDD Orchestrator** - Test coverage discovery
- **Maintenance Orchestrator** - Health checks, cleanup targets
- **Sanitization Orchestrator** - Discover sanitization candidates
- **Tier 2 Knowledge Graph** - Pattern storage and retrieval
- **Tier 3 Dev Context** - Git metrics, project health

---

## 📋 Phase Breakdown

### Phase 1: Architecture & Foundation (Week 1)

**Objective:** Design architecture, create base orchestrator, implement scope resolution

**Tasks:**
1. Design orchestrator architecture (follow BaseOperationModule pattern)
2. Create `discovery_orchestrator.py` skeleton
3. Implement scope definition system
4. Add exclusion engine (.gitignore support)
5. Create discovery context model
6. Write initial tests (RED phase)

**Deliverables:**
- `src/operations/modules/orchestration/discovery_orchestrator.py`
- `src/operations/modules/discovery/scope_resolver.py`
- `src/operations/modules/discovery/exclusion_engine.py`
- `tests/operations/modules/orchestration/test_discovery_orchestrator.py`

**Acceptance Criteria:**
- [ ] Orchestrator inherits from BaseOperationModule
- [ ] Scope resolution works for files, folders, and entire projects
- [ ] Exclusion patterns from .gitignore are respected
- [ ] Tests pass (TDD cycle complete)

**Status:** Not Started

---

### Phase 2: File Discovery Engine (Week 1)

**Objective:** Implement high-performance file system scanning with metadata collection

**Tasks:**
1. Create FileSystemScanner with async I/O
2. Implement LanguageDetector (extension-based + content-based)
3. Build MetricsCollector (LOC, file size, modification dates)
4. Add progress tracking for large codebases
5. Optimize for performance (<2s for 10k files)
6. Write comprehensive tests

**Deliverables:**
- `src/operations/modules/discovery/file_scanner.py`
- `src/operations/modules/discovery/language_detector.py`
- `src/operations/modules/discovery/metrics_collector.py`

**Acceptance Criteria:**
- [ ] Scans 10k+ files in <2 seconds
- [ ] Detects 20+ programming languages
- [ ] Collects accurate metrics (LOC, size)
- [ ] Progress callback works
- [ ] Tests achieve 90%+ coverage

**Status:** Not Started

---

### Phase 3: AST Analysis & Code Intelligence (Week 2)

**Objective:** Parse source files, extract structural information, build dependency graphs

**Tasks:**
1. Implement multi-language AST parser (Python, C#, JS/TS)
2. Extract classes, functions, imports, exports
3. Build dependency graph (files, modules, classes)
4. Calculate complexity metrics (cyclomatic, cognitive)
5. Detect design patterns (Singleton, Factory, Observer, etc.)
6. Optimize memory usage for large files
7. Write parser tests with edge cases

**Deliverables:**
- `src/operations/modules/discovery/ast_parser.py`
- `src/operations/modules/discovery/dependency_mapper.py`
- `src/operations/modules/discovery/complexity_analyzer.py`
- `src/operations/modules/discovery/pattern_detector.py`

**Acceptance Criteria:**
- [ ] Parses Python, C#, JavaScript/TypeScript correctly
- [ ] Extracts complete dependency graph
- [ ] Complexity metrics match industry standards
- [ ] Detects 10+ common design patterns
- [ ] Handles syntax errors gracefully
- [ ] Memory efficient (<500MB for 100k LOC)

**Status:** Not Started

---

### Phase 4: Semantic Discovery & Similarity (Week 2)

**Objective:** Enable semantic search, detect duplicate/similar code, integrate with Knowledge Graph

**Tasks:**
1. Create semantic indexer (FTS5 integration)
2. Implement similarity detection (token-based + AST-based)
3. Build duplicate code finder (clone detection)
4. Integrate with Tier 2 Knowledge Graph
5. Add cross-reference linking
6. Optimize search performance (<100ms)
7. Write search and similarity tests

**Deliverables:**
- `src/operations/modules/discovery/semantic_indexer.py`
- `src/operations/modules/discovery/similarity_engine.py`
- `src/operations/modules/discovery/duplicate_detector.py`

**Acceptance Criteria:**
- [ ] Semantic search returns relevant results
- [ ] Similarity detection accuracy >85%
- [ ] Finds duplicate code blocks (>10 lines)
- [ ] Knowledge Graph integration works
- [ ] Search performance <100ms
- [ ] Tests cover edge cases

**Status:** Not Started

---

### Phase 5: Git History & Evolution Analysis (Week 2-3)

**Objective:** Analyze git history for code ownership, churn, and evolution patterns

**Tasks:**
1. Create GitHistoryAnalyzer (commits, diffs, blame)
2. Implement code churn detection (frequently changed files)
3. Build authorship mapper (identify owners)
4. Track feature evolution over time
5. Detect hot spots (bugs, complexity + churn)
6. Generate historical insights
7. Write git integration tests

**Deliverables:**
- `src/operations/modules/discovery/git_analyzer.py`
- `src/operations/modules/discovery/churn_detector.py`
- `src/operations/modules/discovery/authorship_mapper.py`

**Acceptance Criteria:**
- [ ] Git history parsing works for large repos
- [ ] Churn detection identifies hot spots
- [ ] Authorship mapping accurate
- [ ] Evolution tracking shows trends
- [ ] Performance acceptable (<5s for 1k commits)
- [ ] Tests mock git commands

**Status:** Not Started

---

### Phase 6: Reporting & Recommendation Engine (Week 3)

**Objective:** Generate comprehensive reports, extract insights, provide actionable recommendations

**Tasks:**
1. Create ReportGenerator (JSON, Markdown, HTML)
2. Implement InsightEngine (extract key findings)
3. Build RecommendationSystem (suggest actions)
4. Add visualization support (dependency graphs, metrics charts)
5. Integrate with response templates
6. Generate executive summaries
7. Write report generation tests

**Deliverables:**
- `src/operations/modules/discovery/report_generator.py`
- `src/operations/modules/discovery/insight_engine.py`
- `src/operations/modules/discovery/recommendation_system.py`
- `templates/discovery_report_template.yaml`

**Acceptance Criteria:**
- [ ] Reports generated in multiple formats
- [ ] Insights are actionable and relevant
- [ ] Recommendations prioritized by impact
- [ ] Visualizations render correctly
- [ ] Response templates integrate
- [ ] Tests validate report structure

**Status:** Not Started

---

## 🔗 Integration Strategy

### With Planning System

```python
# Pre-planning discovery
def pre_planning_discovery(self, operation: str) -> Dict[str, Any]:
    """Phase 1 - Task 1.1: Run discovery before planning"""
    discovery = DiscoveryOrchestrator(self.project_root)
    
    # Intelligent scope detection based on operation
    scope = self._detect_discovery_scope(operation)
    
    # Run targeted discovery
    result = discovery.execute({
        'scope': scope,
        'depth': 'moderate',  # balance speed vs thoroughness
        'focus': ['dependencies', 'patterns', 'duplicates']
    })
    
    # Extract key insights for planning
    return {
        'existing_implementations': result.data['similar_code'],
        'dependencies': result.data['dependency_graph'],
        'patterns': result.data['detected_patterns'],
        'recommendations': result.data['recommendations']
    }
```

### With TDD Orchestrator

```python
# Discover test coverage gaps
def discover_test_coverage(self, source_files: List[Path]) -> Dict[str, Any]:
    """Find untested code paths"""
    discovery = DiscoveryOrchestrator(self.project_root)
    
    result = discovery.execute({
        'scope': source_files,
        'focus': ['test_coverage', 'complexity'],
        'report_format': 'coverage_gaps'
    })
    
    return result.data['coverage_analysis']
```

### With Maintenance Orchestrator

```python
# Discover cleanup targets
def discover_cleanup_targets(self) -> Dict[str, Any]:
    """Find files to cleanup/refactor"""
    discovery = DiscoveryOrchestrator(self.project_root)
    
    result = discovery.execute({
        'scope': 'project',
        'focus': ['duplicates', 'dead_code', 'complexity'],
        'thresholds': {
            'complexity': 15,
            'similarity': 0.85
        }
    })
    
    return result.data['cleanup_recommendations']
```

---

## 🧪 Testing Strategy

### Test Coverage Requirements

- **Unit Tests:** 90%+ coverage for all modules
- **Integration Tests:** End-to-end discovery workflows
- **Performance Tests:** Benchmark for large codebases (100k+ LOC)
- **Edge Case Tests:** Syntax errors, binary files, large files

### Test Structure

```
tests/
├── operations/
│   └── modules/
│       └── orchestration/
│           └── test_discovery_orchestrator.py
└── operations/
    └── modules/
        └── discovery/
            ├── test_file_scanner.py
            ├── test_ast_parser.py
            ├── test_dependency_mapper.py
            ├── test_semantic_indexer.py
            ├── test_similarity_engine.py
            ├── test_git_analyzer.py
            └── test_report_generator.py
```

### TDD Workflow

1. **RED Phase** - Write failing test for each module
2. **GREEN Phase** - Implement minimum code to pass
3. **REFACTOR Phase** - Optimize, clean up, document
4. **Repeat** - For each sub-feature

---

## 📊 Success Metrics

### Functional Metrics

- **Discovery Speed:** <2s for 10k files, <10s for 100k files
- **Accuracy:** >90% precision for duplicate detection
- **Coverage:** Supports Python, C#, JavaScript, TypeScript
- **Integration:** Works with all existing orchestrators

### Quality Metrics

- **Test Coverage:** >90% for all modules
- **Performance:** All operations <5s for typical repos
- **Memory:** <500MB for 100k LOC analysis
- **Reliability:** Zero crashes on production codebases

### Business Metrics

- **Adoption:** Used in 80%+ of planning operations
- **Time Savings:** Reduces discovery time by 70%
- **Quality Impact:** Reduces duplicate code by 40%
- **Developer Satisfaction:** >8/10 rating

---

## ⚠️ Risks & Mitigations

### Risk 1: Performance on Large Codebases

**Impact:** High  
**Likelihood:** Medium  
**Mitigation:**
- Implement async I/O for file scanning
- Use streaming for large file processing
- Add caching for AST results
- Provide progress feedback
- Allow incremental discovery

### Risk 2: AST Parser Complexity

**Impact:** High  
**Likelihood:** Medium  
**Mitigation:**
- Start with Python (most familiar)
- Use existing libraries (ast, tree-sitter)
- Handle syntax errors gracefully
- Provide fallback to simple lexical analysis
- Incremental language support

### Risk 3: Integration Coordination

**Impact:** Medium  
**Likelihood:** Low  
**Mitigation:**
- Define clear interfaces early
- Use BaseOperationModule pattern
- Write integration tests
- Coordinate with Planning System team
- Document integration points

### Risk 4: Memory Usage

**Impact:** Medium  
**Likelihood:** Medium  
**Mitigation:**
- Stream large files (don't load entirely)
- Release AST data after processing
- Implement result pagination
- Add memory profiling
- Set size limits

---

## 📅 Timeline

### Week 1 (Dec 16-22, 2024)
- Phase 1: Architecture & Foundation ✅
- Phase 2: File Discovery Engine ✅

### Week 2 (Dec 23-29, 2024)
- Phase 3: AST Analysis & Code Intelligence
- Phase 4: Semantic Discovery & Similarity

### Week 3 (Dec 30-Jan 5, 2025)
- Phase 5: Git History & Evolution
- Phase 6: Reporting & Recommendations

### Week 4 (Jan 6-12, 2025)
- Phase 7: CORTEX Self-Discovery & Documentation Automation
- Integration testing
- Performance optimization
- Documentation
- Launch

---

## 🔍 Phase 7: CORTEX Self-Discovery & Documentation Automation

**NEW PHASE - Critical Enhancement**

**Objective:** Enable Discovery Orchestrator to analyze CORTEX itself and automatically update all documentation, templates, and manifests for multiple audiences.

### Key Capabilities

1. **CORTEX Operations Discovery**
   - Scans `cortex-operations.yaml` for all operations
   - Extracts execution methods, natural language triggers, modules
   - Discovers orchestrators, agents, utilities

2. **Automatic Template Updates**
   - Updates `cortex-brain/response-templates.yaml`
   - Syncs introduction templates (leadership, engineering, product)
   - Updates help template with complete command list
   - Validates 100% template coverage

3. **Deployment Manifest Sync**
   - Updates `deployment-manifest.yaml` with production features
   - Validates feature gates (tests, docs, coverage)
   - Generates deployment readiness reports

4. **Living Feature Documentation**
   - **Feature Catalog** - Complete CORTEX capability list (always current)
   - **Multi-Audience Views:**
     - Leadership: Business value, ROI, strategic fit
     - Engineering: Technical details, APIs, integration
     - Product: Features, use cases, user stories
   - **Auto-Changelog** - Generated from git commits

5. **Dedicated Folder Structure**
   - `cortex-brain/discovery/` - Clean, organized structure
   - `features/` - Living feature docs
   - `operations/` - Operation catalogs
   - `orchestrators/` - Orchestrator analysis
   - `utilities/` - Utility module discovery
   - `templates/` - Template coverage analysis
   - `deployment/` - Deployment readiness
   - `reports/` - Timestamped discovery runs

6. **Automation & Triggers**
   - Git hooks (pre-commit, opt-in)
   - CI/CD pipeline integration
   - Daily scheduled runs
   - Manual trigger: `cortex discover`
   - Pre-deployment validation

### Why This Matters

- **Zero Documentation Drift** - Docs always match code
- **Multi-Audience Support** - Tailored views for different stakeholders
- **Time Savings** - 95% reduction in manual doc updates
- **Deployment Confidence** - Automated validation before deploy
- **Discoverability** - Easy for new users to find features

### Deliverables

- `src/operations/modules/discovery/cortex_operations_discoverer.py`
- `src/operations/modules/discovery/template_updater.py`
- `src/operations/modules/discovery/manifest_updater.py`
- `src/operations/modules/discovery/feature_doc_generator.py`
- `src/operations/modules/discovery/discovery_scheduler.py`
- `cortex-brain/discovery/` folder structure with:
  - `FEATURE-CATALOG.md` (main document)
  - 3 audience-specific views
  - Auto-generated changelog
  - Operation/orchestrator/utility catalogs

### Success Criteria

- [ ] Discovers 100% of CORTEX operations
- [ ] Updates templates automatically (0 drift)
- [ ] Updates manifest automatically (0 drift)
- [ ] Generates 3 audience views
- [ ] Runs in <5s for full discovery
- [ ] Integrates with Maintenance Orchestrator
- [ ] Tests achieve 90%+ coverage

**Detailed Plan:** See `phases/phase-7-cortex-self-discovery.md`

---

## 🔍 Next Steps

### Immediate Actions

1. ✅ Review and approve this master plan
2. ⏭️ Create Phase 1 sub-plan
3. ⏭️ Set up git branch: `feature/discovery-orchestrator-v1`
4. ⏭️ Create orchestrator skeleton
5. ⏭️ Write first test (RED phase)

### After Phase 1

- Review Phase 1 deliverables
- Demo file discovery capabilities
- Get feedback from team
- Proceed to Phase 2

### Success Criteria for Plan Approval

- [ ] Architecture reviewed by senior developer
- [ ] Integration points validated with other orchestrators
- [ ] Timeline realistic based on team capacity
- [ ] Risks identified and mitigations documented
- [ ] Testing strategy comprehensive

---

## 📚 References

### CORTEX Documentation

- `.github/prompts/CORTEX.prompt.md` - Entry point and standards
- `cortex-brain/brain-protection-rules.yaml` - SKULL rules (HOLISTIC_CODE_DISCOVERY_ENFORCEMENT)
- `src/operations/base_operation_module.py` - Base class for orchestrators
- `src/operations/modules/orchestration/planning_orchestrator.py` - Planning System
- `src/operations/modules/orchestration/maintenance_orchestrator.py` - Example orchestrator

### External Resources

- [Tree-sitter](https://tree-sitter.github.io/) - Multi-language AST parsing
- [Roslyn](https://github.com/dotnet/roslyn) - C# compiler API
- [SQLite FTS5](https://www.sqlite.org/fts5.html) - Full-text search
- [Cyclomatic Complexity](https://en.wikipedia.org/wiki/Cyclomatic_complexity) - Code complexity metrics

---

**Plan Status:** 🟡 AWAITING APPROVAL  
**Next Review:** After Phase 1 completion  
**Plan Owner:** Asif Hussain  

---

*This plan follows CORTEX Planning System standards with incremental phases, TDD enforcement, and comprehensive documentation.*
