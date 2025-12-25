# YAML-to-Database Bridge

**Version:** 1.0.0  
**Status:** ✅ Complete  
**Date:** December 25, 2025

## Overview

The YAML-to-Database Bridge automatically loads knowledge files from `cortex-brain/knowledge/` into Tier 2's SQLite database on-demand, making 32,000+ lines of curated best practices immediately available to all CORTEX operations.

## Features

### Lazy Loading
- Knowledge files loaded on first query (no startup overhead)
- Can be disabled with `auto_load_knowledge=False`
- Subsequent queries use cached patterns (no re-parsing)

### Version Tracking
- Tracks file modification times and content hashes
- Only reloads files that have changed
- Prevents duplicate pattern insertion

### Multi-Schema Support
- Design Patterns (GoF + Modern)
- SOLID Principles
- TDD Best Practices
- Security (OWASP Top 10)
- DevOps, Performance, DDD
- Generic fallback for new schemas

### Incremental Loading
- Load all categories: `load_all_knowledge_files()`
- Load specific category: `load_knowledge_category('engineering')`
- Load single file: `load_knowledge_file(path)`

## Usage

### Automatic (Recommended)

```python
from src.tier2.knowledge_graph.knowledge_graph import KnowledgeGraph

# Auto-load enabled by default
kg = KnowledgeGraph()

# First query triggers lazy load
results = kg.search_patterns("Singleton pattern")
# ✅ Knowledge files loaded automatically
```

### Manual Control

```python
# Disable auto-load
kg = KnowledgeGraph(auto_load_knowledge=False)

# Explicitly load when ready
kg.load_knowledge_category('engineering')
kg.load_knowledge_category('testing')

# Or load all at once
kg.yaml_loader.load_all_knowledge_files()
```

### Force Reload

```python
# Reload all knowledge files (ignores cache)
stats = kg.reload_all_knowledge()
print(f"Loaded {sum(stats.values())} patterns")

# Reload specific category
count = kg.load_knowledge_category('security', force_reload=True)
```

### Load Statistics

```python
stats = kg.get_knowledge_load_stats()
print(f"Files loaded: {stats['files_loaded']}")
print(f"Patterns from knowledge: {stats['patterns_from_knowledge']}")
print(f"Last load: {stats['last_load']}")
```

## Architecture

### Components

**YAMLKnowledgeLoader** (`src/tier2/knowledge_graph/loaders/yaml_loader.py`)
- Parses YAML files into pattern dictionaries
- Handles 6 different YAML schemas
- Tracks file hashes for change detection

**KnowledgeGraph** (`src/tier2/knowledge_graph/knowledge_graph.py`)
- Lazy loading via `_ensure_knowledge_loaded()`
- Public API: `load_knowledge_category()`, `reload_all_knowledge()`
- Integrated into `search_patterns()` for transparency

**File Tracking** (SQLite `file_loads` table)
- Stores file path, content hash, load timestamp
- Prevents redundant reloads
- Supports incremental updates

### Pattern Extraction Strategies

**Strategy 1: Pattern Selection Guide** (`design-patterns.yaml`)
```yaml
pattern_selection_guide:
  object_creation:
    - problem: "Need single instance"
      pattern: "Singleton"
      category: "creational"
```

**Strategy 2: GoF Patterns** (`design-patterns.yaml`)
```yaml
creational_patterns:
  - name: "Factory Method"
    intent: "Define interface for creating objects"
    problem: "Need flexibility in object creation"
```

**Strategy 3: SOLID Principles** (`solid-principles.yaml`)
```yaml
single_responsibility_principle:
  name: "Single Responsibility Principle"
  definition: "A class should have one reason to change"
```

**Strategy 4: TDD Practices** (`tdd-best-practices.yaml`)
```yaml
three_laws:
  law_1:
    statement: "Write test before production code"
    explanation: "Ensures test actually tests something"
```

**Strategy 5: Security Practices** (`owasp-top-10.yaml`)
```yaml
owasp_top_10:
  injection:
    name: "Injection"
    risk: "Critical"
    mitigation: "Use parameterized queries"
```

**Strategy 6: Generic Extraction** (Fallback)
- Extracts top-level sections as patterns
- Lower confidence (0.8 vs 1.0)
- Ensures no knowledge is lost

## Integration Points

### TDD Orchestrator v4.0
```python
# Auto-loads testing knowledge on first pattern query
tech_engine = TechnologyDiscoveryEngine(brain, kg)
patterns = kg.search_patterns("pytest fixture best practices")
```

### Planning System 2.0
```python
# Auto-loads design patterns for architectural suggestions
planner = PlanningOrchestrator(kg)
suggestions = kg.suggest_patterns_for_feature("authentication")
```

### Code Review Agents
```python
# Auto-loads SOLID principles for compliance checking
reviewer = CodeReviewAgent(kg)
violations = kg.search_patterns("Single Responsibility violation")
```

## Performance

### Lazy Load Overhead
- First query: ~500ms (32 files, ~300 patterns)
- Subsequent queries: <5ms (SQLite + FTS5)
- Startup: 0ms (no loading until first query)

### Memory Usage
- YAML files: Not kept in memory
- Loaded patterns: ~2MB in SQLite
- File tracking: <1KB per file

### Disk I/O
- File hash calculation: ~10ms per file
- SQLite inserts: Batched in transactions
- No redundant reads (hash-based caching)

## Testing

Run loader tests:
```bash
pytest tests/tier2/test_yaml_knowledge_loader.py -v
```

Run integration demo:
```bash
python examples/yaml_knowledge_bridge_demo.py
```

## Troubleshooting

### Knowledge not loading
```python
# Check if auto-load is enabled
kg = KnowledgeGraph(auto_load_knowledge=True)

# Manually trigger load
kg.load_knowledge_category('engineering', force_reload=True)
```

### Patterns not found
```python
# Verify files are loaded
stats = kg.get_knowledge_load_stats()
print(f"Patterns loaded: {stats['patterns_from_knowledge']}")

# Check search query
results = kg.search_patterns("Singleton", limit=10)
for r in results:
    print(f"{r['title']} - {r['source']}")
```

### Outdated patterns
```python
# Force reload to pick up file changes
kg.reload_all_knowledge()
```

## Future Enhancements

### Phase 11: Feedback Loop (Proposed)
- Track pattern usage in orchestrators
- Adjust confidence scores based on success rates
- Flag low-performing patterns for review

### Phase 12: Custom Knowledge (Proposed)
- User-defined knowledge files in workspace
- Organization-specific patterns
- Team conventions and standards

### Phase 13: Knowledge Versioning (Proposed)
- Track knowledge file versions
- Migration strategies for breaking changes
- Rollback to previous knowledge versions

## References

- **Implementation:** `src/tier2/knowledge_graph/loaders/yaml_loader.py`
- **Tests:** `tests/tier2/test_yaml_knowledge_loader.py`
- **Demo:** `examples/yaml_knowledge_bridge_demo.py`
- **Knowledge Files:** `cortex-brain/knowledge/` (32 files, 7 categories)

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
