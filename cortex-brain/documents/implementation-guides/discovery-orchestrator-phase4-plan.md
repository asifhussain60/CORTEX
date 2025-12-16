# Discovery Orchestrator - Phase 4 Planning

**Phase:** Phase 4 - Semantic Indexing & Search  
**Status:** 📋 PLANNING  
**Dependencies:** Phase 1 ✅, Phase 2 ✅, Phase 3 ✅  
**Start Date:** December 16, 2025  

---

## 🎯 Phase 4 Objectives

**Primary Goal:** Implement FTS5 semantic search index for rapid code discovery

**Key Deliverables:**
1. SQLite FTS5 index builder
2. Semantic search engine with ranking
3. Code snippet extraction and context
4. Symbol lookup and cross-references
5. Comprehensive test suite (TDD RED→GREEN→REFACTOR)

---

## 🏗️ Architecture Design

### Components to Implement

#### 1. `SemanticIndexBuilder`
```python
class SemanticIndexBuilder:
    """Build FTS5 semantic index from code elements"""
    
    def build_index(self, elements: List[CodeElement], db_path: Path) -> SemanticIndex
    def index_element(self, element: CodeElement) -> None
    def update_element(self, element: CodeElement) -> None
    def remove_element(self, element_id: str) -> None
```

#### 2. `SemanticSearchEngine`
```python
class SemanticSearchEngine:
    """Search semantic index with ranking"""
    
    def search(self, query: str, limit: int = 10) -> List[SearchResult]
    def search_by_type(self, query: str, element_type: str) -> List[SearchResult]
    def find_symbol(self, symbol_name: str) -> Optional[CodeElement]
    def find_references(self, symbol_name: str) -> List[CodeElement]
```

#### 3. `SnippetExtractor`
```python
class SnippetExtractor:
    """Extract code snippets with context"""
    
    def extract_snippet(self, element: CodeElement, context_lines: int = 3) -> CodeSnippet
    def highlight_matches(self, snippet: str, query: str) -> str
    def get_surrounding_context(self, file_path: Path, line: int) -> str
```

---

## 📦 Data Models

### `SemanticIndex`
```python
@dataclass
class SemanticIndex:
    """Semantic search index metadata"""
    db_path: Path
    indexed_files: int
    indexed_elements: int
    index_size_mb: float
    created_at: datetime
    last_updated: datetime
```

### `SearchResult`
```python
@dataclass
class SearchResult:
    """Search result with ranking"""
    element: CodeElement
    score: float
    snippet: CodeSnippet
    matches: List[str]
    rank: int
```

### `CodeSnippet`
```python
@dataclass
class CodeSnippet:
    """Code snippet with context"""
    code: str
    start_line: int
    end_line: int
    context_before: str
    context_after: str
    highlighted: str
```

---

## 🧪 Test Strategy (TDD)

### RED Phase Tests (15 tests)

**Index Building (4 tests):**
1. ✅ Build index from empty list
2. ✅ Build index from code elements
3. ✅ Update existing index
4. ✅ Remove element from index

**Search Operations (5 tests):**
5. ✅ Search returns ranked results
6. ✅ Search by element type
7. ✅ Find symbol by exact name
8. ✅ Find references to symbol
9. ✅ Handle empty search results

**Snippet Extraction (4 tests):**
10. ✅ Extract snippet with context
11. ✅ Highlight search matches
12. ✅ Get surrounding context
13. ✅ Handle edge cases (file boundaries)

**Integration (2 tests):**
14. ✅ End-to-end index and search
15. ✅ Index persistence across sessions

---

## 🔧 Implementation Strategy

### Step 1: Dependencies
```bash
# SQLite FTS5 is built into Python 3.x
# No additional dependencies needed
```

### Step 2: RED Phase
1. Create `semantic_index_builder.py` (skeleton)
2. Create `semantic_search_engine.py` (skeleton)
3. Create `snippet_extractor.py` (skeleton)
4. Write 15 comprehensive tests
5. Validate RED phase (all tests expecting NotImplementedError)

### Step 3: GREEN Phase
1. Implement `SemanticIndexBuilder` with SQLite FTS5
2. Implement `SemanticSearchEngine` with ranking
3. Implement `SnippetExtractor` with context
4. Update tests to expect real behavior
5. Validate GREEN phase (all tests passing)

### Step 4: REFACTOR Phase
- Deferred to Phase 7 (per plan)

---

## 📊 Success Criteria

| Criterion | Target | Validation |
|-----------|--------|------------|
| TDD RED phase | 15 tests with NotImplementedError | pytest passing |
| TDD GREEN phase | 15/15 tests passing | pytest passing |
| FTS5 index creation | SQLite database created | File exists |
| Search ranking | Results sorted by score | Test assertions |
| Snippet extraction | Code + context returned | Test assertions |
| Symbol lookup | Exact matches found | Test assertions |
| Performance | <100ms for 1000 elements | Benchmark test |
| No regressions | All 62 tests passing (1+2+3+4) | Full test suite |

---

## 🚀 FTS5 Schema Design

```sql
CREATE VIRTUAL TABLE code_index USING fts5(
    element_id,
    element_type,
    element_name,
    file_path,
    signature,
    docstring,
    code_content,
    tokenize='porter unicode61'
);

CREATE TABLE element_metadata (
    element_id TEXT PRIMARY KEY,
    element_type TEXT,
    file_path TEXT,
    line_start INTEGER,
    line_end INTEGER,
    complexity_score INTEGER,
    indexed_at TIMESTAMP
);
```

---

## 📈 Estimated Effort

**Code Volume:**
- `semantic_index_builder.py`: ~150 lines
- `semantic_search_engine.py`: ~120 lines
- `snippet_extractor.py`: ~100 lines
- **Total Production Code:** ~370 lines

**Test Volume:**
- `test_semantic_indexing.py`: ~250 lines
- **Total Test Code:** ~250 lines

**Total Phase 4:** ~620 lines

**Time Estimate:** 1-2 hours (with TDD workflow)

---

## 🔗 Integration Points

**Phase 3 Integration (Input):**
- Consumes `CodeElement` list from AST parsers
- Uses complexity metrics for ranking boost
- Leverages file paths for snippet extraction

**Phase 5 Dependencies (Output):**
- Provides fast symbol lookup for change impact
- Enables cross-reference analysis
- Supports refactoring operations

---

## ⚠️ Technical Challenges

### Challenge 1: FTS5 Ranking
- **Issue:** Default BM25 ranking may not suit code search
- **Solution:** Add complexity and type-based ranking boost
- **Fallback:** Use simple match count ranking

### Challenge 2: Large Codebases
- **Issue:** Index size may grow large
- **Solution:** Incremental indexing, partial updates
- **Optimization:** Vacuum database periodically

### Challenge 3: Context Extraction
- **Issue:** Need to read files for snippet context
- **Solution:** Cache file contents during indexing
- **Trade-off:** Memory vs. disk I/O

---

## 🎯 Phase 4 Deliverables

**Code Artifacts:**
- ✅ `src/operations/modules/discovery/semantic_index_builder.py`
- ✅ `src/operations/modules/discovery/semantic_search_engine.py`
- ✅ `src/operations/modules/discovery/snippet_extractor.py`
- ✅ `tests/operations/test_semantic_indexing.py`

**Documentation:**
- ✅ Phase 4 completion report
- ✅ Semantic search guide

---

## 🚀 Next Actions

### Immediate Tasks
1. ⏳ Create RED phase skeletons
2. ⏳ Write 15 comprehensive tests
3. ⏳ Validate RED phase
4. ⏳ Begin GREEN phase implementation

---

**Phase 4 Status:** 📋 **READY TO BEGIN**

*Proceeding with autonomous execution*
