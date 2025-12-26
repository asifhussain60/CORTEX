# Discovery Orchestrator - Architecture Document

**Version:** 1.0  
**Date:** 2024-12-16  
**Author:** Asif Hussain  

---

## 🏗️ High-Level Architecture

### System Overview

The Discovery Orchestrator is a Tier 4 (COMPLEX) orchestrator that provides comprehensive codebase exploration capabilities. It follows CORTEX's BaseOperationModule pattern and integrates deeply with existing systems.

```
┌─────────────────────────────────────────────────────────────────┐
│                    Discovery Orchestrator                        │
│                  (BaseOperationModule)                           │
└───────────────────────┬─────────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
┌───────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
│  File Layer  │ │ Code Layer │ │ Git Layer  │
│              │ │            │ │            │
│ - Scanner    │ │ - AST      │ │ - History  │
│ - Detector   │ │ - Deps     │ │ - Blame    │
│ - Metrics    │ │ - Patterns │ │ - Churn    │
└──────────────┘ └────────────┘ └────────────┘
        │               │               │
        └───────────────┼───────────────┘
                        │
        ┌───────────────▼───────────────┐
        │   Semantic & Analysis Layer   │
        │                               │
        │  - Indexer                    │
        │  - Similarity Engine          │
        │  - Duplicate Detector         │
        │  - Knowledge Graph Linker     │
        └───────────────┬───────────────┘
                        │
        ┌───────────────▼───────────────┐
        │    Reporting & Insights       │
        │                               │
        │  - Report Generator           │
        │  - Insight Engine             │
        │  - Recommendation System      │
        └───────────────────────────────┘
```

---

## 🎯 Design Principles

### 1. Single Responsibility (SOLID-SRP)

Each component has ONE clear responsibility:
- **FileScanner** - Enumerate files
- **ASTParser** - Parse code structure
- **DependencyMapper** - Build dependency graphs
- **ReportGenerator** - Generate reports

### 2. Open/Closed Principle

- **Open for extension** - New language parsers can be added
- **Closed for modification** - Core discovery logic remains stable

### 3. Dependency Inversion

Orchestrator depends on abstractions, not concrete implementations:
```python
class ICodeParser(ABC):
    @abstractmethod
    def parse(self, file_path: Path) -> AST: pass

class PythonParser(ICodeParser): ...
class CSharpParser(ICodeParser): ...
```

### 4. Incremental Processing

- Stream large files (don't load entirely)
- Process in batches
- Release memory after each phase
- Provide progress callbacks

### 5. Performance First

- Target: <2s for 10k files
- Async I/O for file operations
- Cache AST results
- Lazy evaluation where possible

---

## 📦 Module Structure

```
src/operations/modules/
├── orchestration/
│   └── discovery_orchestrator.py        # Main orchestrator
└── discovery/                           # Discovery modules
    ├── __init__.py
    ├── scope_resolver.py                # Phase 1
    ├── exclusion_engine.py              # Phase 1
    ├── file_scanner.py                  # Phase 2
    ├── language_detector.py             # Phase 2
    ├── metrics_collector.py             # Phase 2
    ├── ast_parser.py                    # Phase 3
    ├── dependency_mapper.py             # Phase 3
    ├── complexity_analyzer.py           # Phase 3
    ├── pattern_detector.py              # Phase 3
    ├── semantic_indexer.py              # Phase 4
    ├── similarity_engine.py             # Phase 4
    ├── duplicate_detector.py            # Phase 4
    ├── git_analyzer.py                  # Phase 5
    ├── churn_detector.py                # Phase 5
    ├── authorship_mapper.py             # Phase 5
    ├── report_generator.py              # Phase 6
    ├── insight_engine.py                # Phase 6
    └── recommendation_system.py         # Phase 6
```

---

## 🔄 Workflow Phases

### Phase 1: Scope Definition

**Input:** User request (file path, folder, or "entire project")  
**Output:** `DiscoveryScope` object with resolved paths and exclusions  

**Process:**
1. Parse user input
2. Resolve to absolute paths
3. Load exclusion patterns (.gitignore, .cortexignore)
4. Validate paths exist
5. Estimate scope size

**Key Classes:**
- `ScopeResolver`
- `ExclusionEngine`
- `ScopeValidator`

---

### Phase 2: File Discovery

**Input:** `DiscoveryScope`  
**Output:** `FileInventory` with metadata for each file  

**Process:**
1. Recursive file enumeration (async)
2. Apply exclusion patterns
3. Detect language for each file
4. Collect metrics (LOC, size, modified date)
5. Generate file inventory

**Key Classes:**
- `FileSystemScanner`
- `LanguageDetector`
- `MetricsCollector`

**Performance Target:** <2s for 10k files

---

### Phase 3: Code Analysis

**Input:** `FileInventory`  
**Output:** `CodeAnalysisResult` with AST, dependencies, complexity  

**Process:**
1. Parse each source file (multi-threaded)
2. Extract classes, functions, imports
3. Build dependency graph
4. Calculate complexity metrics
5. Detect design patterns

**Key Classes:**
- `ASTParser` (multi-language)
- `DependencyMapper`
- `ComplexityAnalyzer`
- `PatternDetector`

**Performance Target:** <5s for 100k LOC

---

### Phase 4: Semantic Discovery

**Input:** `CodeAnalysisResult`  
**Output:** `SemanticIndex` with search capability  

**Process:**
1. Build FTS5 index from code
2. Calculate code embeddings
3. Find similar code blocks
4. Detect duplicates
5. Link to Knowledge Graph

**Key Classes:**
- `SemanticIndexer`
- `SimilarityEngine`
- `DuplicateDetector`

**Performance Target:** <100ms for searches

---

### Phase 5: Historical Context

**Input:** Repository path  
**Output:** `GitHistory` with authorship, churn, evolution  

**Process:**
1. Parse git log
2. Calculate code churn
3. Map authorship (git blame)
4. Track feature evolution
5. Identify hot spots

**Key Classes:**
- `GitHistoryAnalyzer`
- `ChurnDetector`
- `AuthorshipMapper`

**Performance Target:** <5s for 1k commits

---

### Phase 6: Reporting

**Input:** All previous phase outputs  
**Output:** Reports in multiple formats (JSON, Markdown, HTML)  

**Process:**
1. Generate executive summary
2. Extract actionable insights
3. Prioritize recommendations
4. Create visualizations
5. Format reports

**Key Classes:**
- `ReportGenerator`
- `InsightEngine`
- `RecommendationSystem`

**Performance Target:** <2s for report generation

---

## 🔌 Integration Points

### With Planning System

```python
class PlanningOrchestrator:
    def pre_planning_discovery(self, operation: str) -> Dict[str, Any]:
        """Phase 1 - Task 1.1: Run discovery before planning"""
        discovery = DiscoveryOrchestrator(self.project_root)
        
        result = discovery.execute({
            'scope': self._detect_discovery_scope(operation),
            'depth': 'moderate',
            'focus': ['dependencies', 'patterns', 'duplicates']
        })
        
        return {
            'existing_implementations': result.data['similar_code'],
            'dependencies': result.data['dependency_graph'],
            'patterns': result.data['detected_patterns']
        }
```

### With TDD Orchestrator

```python
class TDDOrchestrator:
    def discover_test_coverage(self) -> Dict[str, Any]:
        """Find untested code paths"""
        discovery = DiscoveryOrchestrator(self.project_root)
        
        result = discovery.execute({
            'scope': self.source_files,
            'focus': ['test_coverage', 'complexity']
        })
        
        return result.data['coverage_analysis']
```

### With Maintenance Orchestrator

```python
class MaintenanceOrchestrator:
    def discover_cleanup_targets(self) -> Dict[str, Any]:
        """Find files to cleanup"""
        discovery = DiscoveryOrchestrator(self.project_root)
        
        result = discovery.execute({
            'scope': 'project',
            'focus': ['duplicates', 'dead_code', 'complexity']
        })
        
        return result.data['cleanup_recommendations']
```

### With Knowledge Graph (Tier 2)

```python
# Store discovered patterns
knowledge_graph.store_pattern(
    pattern_type='discovery_result',
    namespace='codebase_analysis',
    data=discovery_result,
    metadata={'timestamp': datetime.now()}
)

# Query historical discoveries
similar_discoveries = knowledge_graph.search(
    query='authentication implementation',
    pattern_type='discovery_result'
)
```

---

## 🗃️ Data Models

### DiscoveryScope

```python
@dataclass
class DiscoveryScope:
    root_path: Path
    include_patterns: List[str]
    exclude_patterns: List[str]
    max_depth: int
    follow_symlinks: bool
    estimated_file_count: int
```

### FileInventory

```python
@dataclass
class FileInfo:
    path: Path
    language: str
    size_bytes: int
    line_count: int
    modified_at: datetime
    hash: str

@dataclass
class FileInventory:
    files: List[FileInfo]
    total_files: int
    total_size: int
    total_lines: int
    languages: Dict[str, int]  # language -> file count
```

### CodeAnalysisResult

```python
@dataclass
class CodeElement:
    type: str  # class, function, method
    name: str
    file_path: Path
    line_start: int
    line_end: int
    complexity: int
    dependencies: List[str]

@dataclass
class CodeAnalysisResult:
    elements: List[CodeElement]
    dependency_graph: Dict[str, List[str]]
    complexity_metrics: Dict[str, float]
    detected_patterns: List[str]
```

### DiscoveryReport

```python
@dataclass
class DiscoveryReport:
    summary: Dict[str, Any]
    file_inventory: FileInventory
    code_analysis: CodeAnalysisResult
    semantic_index: SemanticIndex
    git_history: GitHistory
    insights: List[str]
    recommendations: List[Recommendation]
    generated_at: datetime
```

---

## 🧪 Testing Strategy

### Unit Tests (per module)

```python
# test_file_scanner.py
def test_scanner_respects_exclusions():
    scanner = FileSystemScanner()
    result = scanner.scan(path, exclude_patterns=['.git', '__pycache__'])
    assert '.git' not in [f.path for f in result.files]

def test_scanner_performance():
    """Should scan 10k files in <2s"""
    with timer() as t:
        result = scanner.scan(large_project_path)
    assert t.elapsed < 2.0
```

### Integration Tests

```python
def test_full_discovery_workflow():
    """End-to-end discovery test"""
    orchestrator = DiscoveryOrchestrator(project_root)
    
    result = orchestrator.execute({
        'scope': 'src/',
        'depth': 'full'
    })
    
    assert result.success
    assert result.data['file_count'] > 0
    assert result.data['dependency_graph']
    assert result.data['report']
```

### Performance Tests

```python
@pytest.mark.benchmark
def test_large_codebase_performance():
    """Benchmark with 100k LOC"""
    result = orchestrator.execute({'scope': large_codebase})
    
    assert result.data['elapsed_time'] < 10.0
    assert result.data['memory_usage_mb'] < 500
```

---

## 📊 Metrics & Monitoring

### Performance Metrics

- **Discovery Time** - Total time from start to finish
- **Files Processed** - Number of files analyzed
- **Lines Analyzed** - Total LOC processed
- **Memory Usage** - Peak memory consumption
- **Cache Hit Rate** - Percentage of cached AST results

### Quality Metrics

- **Duplicate Detection Accuracy** - Precision/recall
- **Pattern Detection Rate** - Patterns found vs expected
- **Dependency Accuracy** - Correct dependencies identified
- **Search Relevance** - Search result quality

### Usage Metrics

- **Invocations** - Times discovery ran
- **Integration Usage** - Which orchestrators use it
- **Report Formats** - Most requested formats
- **Common Scopes** - Most common discovery scopes

---

## ⚠️ Known Limitations

### Current Limitations

1. **Language Support** - Initially Python, C#, JS/TS only
2. **Large Files** - Files >10MB may be slow
3. **Binary Files** - No analysis, only metadata
4. **Encrypted Files** - Cannot analyze
5. **Generated Code** - May have false positives

### Future Enhancements

1. Support for Java, Go, Rust
2. Cloud storage support (S3, Azure Blob)
3. Real-time monitoring mode
4. API for external tools
5. Machine learning for pattern detection

---

## 🔐 Security Considerations

### Data Privacy

- Never send code to external services
- All analysis done locally
- Reports sanitized (no secrets exposed)
- Git history anonymization option

### Performance & DoS

- Size limits (max file size, max files)
- Timeout protection (kill long-running operations)
- Memory limits (configurable)
- Rate limiting for API usage

### Access Control

- Respects file system permissions
- No privileged operations
- Sandboxed execution environment
- Audit logging for sensitive operations

---

## 📚 References

- **BaseOperationModule:** `src/operations/base_operation_module.py`
- **Planning System:** `src/operations/modules/orchestration/planning_orchestrator.py`
- **SKULL Rules:** `cortex-brain/brain-protection-rules.yaml`
- **Tree-sitter:** https://tree-sitter.github.io/
- **FTS5 Documentation:** https://www.sqlite.org/fts5.html

---

*Architecture version 1.0 - Subject to refinement during implementation*
