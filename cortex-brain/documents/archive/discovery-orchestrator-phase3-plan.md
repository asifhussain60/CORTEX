# Discovery Orchestrator - Phase 3 Planning

**Phase:** Phase 3 - AST Analysis & Code Intelligence  
**Status:** 📋 PLANNING  
**Dependencies:** Phase 1 ✅, Phase 2 ✅  
**Start Date:** December 16, 2025  

---

## 🎯 Phase 3 Objectives

**Primary Goal:** Implement Abstract Syntax Tree (AST) analysis for code intelligence

**Key Deliverables:**
1. Multi-language AST parser (Python, C#, JavaScript)
2. Code element extraction (classes, functions, methods, variables)
3. Dependency graph construction
4. Complexity metrics calculation
5. Comprehensive test suite (TDD RED→GREEN→REFACTOR)

---

## 🏗️ Architecture Design

### Components to Implement

#### 1. `ASTParser` (Base Class)
```python
class ASTParser:
    """Base class for language-specific AST parsing"""
    
    def parse(self, file_info: FileInfo) -> ASTNode:
        """Parse file into AST"""
        
    def extract_elements(self, ast: ASTNode) -> List[CodeElement]:
        """Extract code elements from AST"""
        
    def calculate_complexity(self, ast: ASTNode) -> ComplexityMetrics:
        """Calculate complexity metrics"""
```

#### 2. `PythonASTParser` (Python Implementation)
```python
class PythonASTParser(ASTParser):
    """Python AST parser using ast module"""
    
    # Uses Python's built-in ast module
    # Extracts: classes, functions, methods, variables, imports
```

#### 3. `CSharpASTParser` (C# Implementation)
```python
class CSharpASTParser(ASTParser):
    """C# AST parser using tree-sitter-csharp"""
    
    # Uses tree-sitter for C# parsing
    # Extracts: classes, methods, properties, fields, namespaces
```

#### 4. `JavaScriptASTParser` (JavaScript/TypeScript Implementation)
```python
class JavaScriptASTParser(ASTParser):
    """JavaScript/TypeScript parser using tree-sitter-javascript"""
    
    # Uses tree-sitter for JS/TS parsing
    # Extracts: functions, classes, variables, imports, exports
```

#### 5. `DependencyGraphBuilder`
```python
class DependencyGraphBuilder:
    """Build dependency graph from code elements"""
    
    def build_graph(self, elements: List[CodeElement]) -> DependencyGraph:
        """Construct dependency graph"""
        
    def find_dependencies(self, element: CodeElement) -> List[str]:
        """Find dependencies for element"""
        
    def detect_cycles(self) -> List[List[str]]:
        """Detect circular dependencies"""
```

#### 6. `ComplexityAnalyzer`
```python
class ComplexityAnalyzer:
    """Calculate complexity metrics"""
    
    def calculate_cyclomatic_complexity(self, ast: ASTNode) -> int:
        """Calculate cyclomatic complexity"""
        
    def calculate_cognitive_complexity(self, ast: ASTNode) -> int:
        """Calculate cognitive complexity"""
        
    def calculate_maintainability_index(self, metrics: Dict) -> float:
        """Calculate maintainability index"""
```

---

## 📦 Data Models

### `ASTNode`
```python
@dataclass
class ASTNode:
    """Represents an AST node"""
    node_type: str
    name: str
    start_line: int
    end_line: int
    children: List['ASTNode']
    attributes: Dict[str, Any]
```

### `CodeElement`
```python
@dataclass
class CodeElement:
    """Represents a code element (class, function, method)"""
    element_type: str  # 'class', 'function', 'method', 'variable'
    name: str
    file_path: Path
    start_line: int
    end_line: int
    signature: str
    dependencies: List[str]
    complexity: ComplexityMetrics
```

### `ComplexityMetrics`
```python
@dataclass
class ComplexityMetrics:
    """Complexity metrics for code element"""
    cyclomatic_complexity: int
    cognitive_complexity: int
    lines_of_code: int
    number_of_parameters: int
    nesting_depth: int
    maintainability_index: float
```

### `DependencyGraph`
```python
@dataclass
class DependencyGraph:
    """Dependency graph representation"""
    nodes: Dict[str, CodeElement]
    edges: List[Tuple[str, str]]
    cycles: List[List[str]]
```

---

## 🧪 Test Strategy (TDD)

### RED Phase Tests (15-20 tests)

**AST Parsing (6 tests):**
1. ✅ Parse Python file with class
2. ✅ Parse Python file with function
3. ✅ Parse C# file with class
4. ✅ Parse C# file with method
5. ✅ Parse JavaScript file with function
6. ✅ Parse JavaScript file with class

**Element Extraction (6 tests):**
7. ✅ Extract Python classes
8. ✅ Extract Python functions
9. ✅ Extract C# methods
10. ✅ Extract C# properties
11. ✅ Extract JavaScript functions
12. ✅ Extract JavaScript exports

**Dependency Analysis (4 tests):**
13. ✅ Build simple dependency graph
14. ✅ Detect circular dependencies
15. ✅ Find element dependencies
16. ✅ Handle missing dependencies

**Complexity Metrics (4 tests):**
17. ✅ Calculate cyclomatic complexity
18. ✅ Calculate cognitive complexity
19. ✅ Calculate maintainability index
20. ✅ Handle complex nested structures

---

## 🔧 Implementation Strategy

### Step 1: Dependencies (External Libraries)
```bash
pip install tree-sitter
pip install tree-sitter-python
pip install tree-sitter-csharp
pip install tree-sitter-javascript
```

### Step 2: RED Phase (Skeleton + Tests)
1. Create `ast_parser.py` with base class
2. Create language-specific parsers (skeleton)
3. Create `dependency_graph_builder.py` (skeleton)
4. Create `complexity_analyzer.py` (skeleton)
5. Write 20 comprehensive tests (expecting `NotImplementedError`)
6. Validate RED phase (all tests pass with proper failures)

### Step 3: GREEN Phase (Implementation)
1. Implement `PythonASTParser` (uses Python's ast module)
2. Implement `CSharpASTParser` (uses tree-sitter)
3. Implement `JavaScriptASTParser` (uses tree-sitter)
4. Implement `DependencyGraphBuilder`
5. Implement `ComplexityAnalyzer`
6. Update tests to expect real behavior
7. Validate GREEN phase (all tests pass)

### Step 4: REFACTOR Phase
- Deferred to Phase 7 (per autonomous execution plan)

---

## 🔗 Integration Points

### Phase 2 Integration (Input)
- Consumes `FileInventory` from Phase 2
- Uses `FileInfo.language` to select parser
- Processes files discovered by `FileDiscoveryEngine`

### Phase 4 Dependencies (Output)
- Produces `CodeElement` list for semantic indexing
- Provides `DependencyGraph` for impact analysis
- Supplies `ComplexityMetrics` for quality scoring

---

## 📊 Success Criteria

| Criterion | Target | Validation |
|-----------|--------|------------|
| TDD RED phase | 20 tests with NotImplementedError | pytest passing |
| TDD GREEN phase | 20/20 tests passing | pytest passing |
| Python AST parsing | Classes, functions, imports extracted | Test assertions |
| C# AST parsing | Classes, methods, properties extracted | Test assertions |
| JavaScript parsing | Functions, classes, exports extracted | Test assertions |
| Dependency graph | Nodes and edges constructed | Test assertions |
| Complexity metrics | Cyclomatic, cognitive, maintainability | Test assertions |
| No regressions | All 50 Phase 1+2+3 tests passing | Full test suite |

---

## ⚠️ Technical Challenges

### Challenge 1: Tree-Sitter Setup
- **Issue:** Tree-sitter requires compiled language grammars
- **Solution:** Use pre-built bindings (tree-sitter-python, etc.)
- **Fallback:** Manual grammar compilation if needed

### Challenge 2: Multi-Language Support
- **Issue:** Different languages have different AST structures
- **Solution:** Abstract base class with language-specific implementations
- **Benefit:** Easy to add new languages later

### Challenge 3: Complexity Calculation
- **Issue:** Different complexity metrics have different algorithms
- **Solution:** Implement cyclomatic first (simpler), then cognitive
- **Reference:** Use established algorithms (McCabe, Sonar)

### Challenge 4: Dependency Resolution
- **Issue:** Resolving imports/references across files
- **Solution:** Build symbol table during extraction phase
- **Limitation:** May not resolve dynamic imports initially

---

## 📈 Estimated Effort

**Code Volume:**
- `ast_parser.py`: ~100 lines
- `python_ast_parser.py`: ~150 lines
- `csharp_ast_parser.py`: ~150 lines
- `javascript_ast_parser.py`: ~150 lines
- `dependency_graph_builder.py`: ~120 lines
- `complexity_analyzer.py`: ~100 lines
- **Total Production Code:** ~770 lines

**Test Volume:**
- `test_ast_parsing.py`: ~300 lines
- **Total Test Code:** ~300 lines

**Total Phase 3:** ~1,070 lines

**Time Estimate:** 2-3 hours (with TDD workflow)

---

## 🎯 Phase 3 Deliverables

**Code Artifacts:**
- ✅ `src/operations/modules/discovery/ast_parser.py`
- ✅ `src/operations/modules/discovery/python_ast_parser.py`
- ✅ `src/operations/modules/discovery/csharp_ast_parser.py`
- ✅ `src/operations/modules/discovery/javascript_ast_parser.py`
- ✅ `src/operations/modules/discovery/dependency_graph_builder.py`
- ✅ `src/operations/modules/discovery/complexity_analyzer.py`
- ✅ `tests/operations/test_ast_parsing.py`

**Documentation:**
- ✅ Phase 3 completion report
- ✅ AST parsing guide
- ✅ Complexity metrics reference

---

## 🚀 Next Actions

### Immediate Tasks
1. ⏳ Install tree-sitter dependencies
2. ⏳ Create RED phase skeletons
3. ⏳ Write 20 comprehensive tests
4. ⏳ Validate RED phase (all tests fail properly)
5. ⏳ Begin GREEN phase implementation

### User Approval Required
- None (autonomous execution approved)

---

**Phase 3 Status:** 📋 **READY TO BEGIN**

*Awaiting autonomous execution initiation*
