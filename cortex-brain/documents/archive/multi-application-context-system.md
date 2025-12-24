# Multi-Application Context System

**User Guide for CORTEX Multi-Application Workspace Intelligence**

Version: 1.0  
Date: 2025-11-25  
Author: Asif Hussain

---

## 📋 Overview

The Multi-Application Context System enables CORTEX to intelligently build context for large workspaces containing multiple applications (like ColdFusion multi-app environments) without choking on volume.

### Key Features

- **Fast Topology Detection** - Discover 14+ applications in <5 seconds
- **Progressive Loading** - Load top 2-3 apps immediately, rest on-demand
- **Intelligent Caching** - Survives VS Code restarts, 7-day TTL, LRU eviction
- **Database Schema Inference** - Extract DB schema from code (no database access needed)
- **Shared Context** - Learn from all apps to build comprehensive database knowledge

---

## 🚀 Quick Start

### Basic Usage

```python
from pathlib import Path
from src.crawlers import MultiApplicationOrchestrator
from src.tier2.knowledge_graph import KnowledgeGraph

# Initialize knowledge graph
kg = KnowledgeGraph()

# Create orchestrator
orchestrator = MultiApplicationOrchestrator(
    workspace_path=Path('/path/to/ColdFusion/workspace'),
    knowledge_graph=kg,
    cortex_brain_path=Path('/path/to/cortex-brain')
)

# Run progressive analysis (15-20 seconds)
result = orchestrator.run_progressive()

print(f"Loaded {result.completed} applications in {result.duration_seconds:.1f}s")
print(f"Discovered {result.total_items_discovered} items")
```

### On-Demand Loading

```python
# User wants to analyze specific application
result = orchestrator.load_application_on_demand(
    app_name='AdjustmentManager',
    depth='deep'  # 'shallow' or 'deep'
)

print(f"Analyzed {result.items_discovered} items")
```

---

## 🏗️ Architecture

### Component Stack

```
┌──────────────────────────────────────────────────────────┐
│              MultiApplicationOrchestrator                │
│  (Progressive loading, prioritization, coordination)     │
├──────────────────────────────────────────────────────────┤
│                                                          │
│  ┌─────────────────────┐  ┌────────────────────────┐   │
│  │ WorkspaceTopology   │  │ ApplicationScoped      │   │
│  │ Crawler             │  │ Crawler                │   │
│  │ (5s, multi-app      │  │ (10s shallow,          │   │
│  │  detection)         │  │  60s deep)             │   │
│  └─────────────────────┘  └────────────────────────┘   │
│                                                          │
│  ┌─────────────────────┐  ┌────────────────────────┐   │
│  │ DatabaseSchema      │  │ PersistentApplication  │   │
│  │ InferenceEngine     │  │ Cache                  │   │
│  │ (code-based         │  │ (SQLite index,         │   │
│  │  extraction)        │  │  LRU eviction)         │   │
│  └─────────────────────┘  └────────────────────────┘   │
│                                                          │
│  ┌─────────────────────────────────────────────────┐   │
│  │ SharedDatabaseContextManager                    │   │
│  │ (cross-app schema knowledge)                    │   │
│  └─────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
```

### Execution Flow

```
Phase 1: Workspace Topology (5s)
  ├─ Scan workspace root
  ├─ Detect application markers
  ├─ Identify shared code
  └─ Estimate sizes

Phase 2: Prioritization (<1s)
  ├─ Analyze VS Code activity
  ├─ Check git recent changes
  ├─ Score by relevance
  └─ Sort applications

Phase 3: Load Top 2 Apps (15-20s)
  ├─ App 1: Shallow crawl + DB inference
  ├─ App 2: Shallow crawl + DB inference
  ├─ Merge into shared DB context
  └─ Cache results

Phase 4: Background Pre-warm (optional)
  └─ App 3: Background shallow crawl

Phase 5: Lazy Queue
  └─ Store remaining apps for on-demand loading
```

---

## 📊 Performance Benchmarks

### Target Performance

| Operation | Target | Notes |
|-----------|--------|-------|
| Workspace topology | <5s | 100+ folders |
| Shallow app crawl | <10s | Entry points + structure |
| Deep app crawl | <60s | Full file inventory |
| Cache retrieval | <0.1s | Hit on valid fingerprint |
| Total initial load (2 apps) | 15-20s | Including DB inference |

### Memory Usage

| Component | Usage | Notes |
|-----------|-------|-------|
| Topology crawler | ~10 MB | Temporary |
| Application crawler | ~20 MB | Per app |
| Cache index (SQLite) | ~5 MB | Persistent |
| Shared DB schema | ~10 MB | Persistent |
| **Total (2 apps)** | **~80-150 MB** | Well within limits |

---

## 🔧 Configuration

### Cache Configuration

```python
cache_manager = PersistentApplicationCache(
    cache_dir=cortex_brain_path,
    max_cache_size_mb=500,      # Maximum total cache size
    ttl_days=7                  # Time-to-live (days)
)
```

### Orchestrator Configuration

```python
orchestrator = MultiApplicationOrchestrator(
    workspace_path=workspace_path,
    knowledge_graph=kg,
    cortex_brain_path=cortex_brain_path,
    config={
        'max_workers': 3,       # Parallel workers
        'cache_enabled': True,  # Enable caching
        'db_inference': True    # Enable DB inference
    }
)
```

---

## 💾 Cache Management

### Cache Structure

```
cortex-brain/
└── context-cache/
    ├── cache_index.db (SQLite index)
    ├── shared_database_schema.json
    └── applications/
        ├── AdjustmentManager/
        │   ├── shallow_context.json
        │   └── deep_context.json
        ├── CatalogManager/
        │   ├── shallow_context.json
        │   └── deep_context.json
        └── ...
```

### Cache Operations

```python
# Get cache statistics
stats = orchestrator.get_cache_stats()
print(f"Total entries: {stats['total_entries']}")
print(f"Total size: {stats['total_size_mb']:.1f} MB")
print(f"Apps cached: {stats['apps_cached']}")

# Clear cache for specific app
orchestrator.cache_manager.clear_app('AdjustmentManager')

# Clear all cache
orchestrator.cache_manager.clear_all()
```

---

## 🗄️ Database Schema Inference

### How It Works

The `DatabaseSchemaInferenceEngine` extracts database knowledge from application code **without needing database access**:

1. **ColdFusion Queries** - Parses `<cfquery>` tags to extract table names and columns
2. **ORM Models** - Analyzes ColdFusion ORM entity definitions
3. **DAO Files** - Scans data access layer for CRUD patterns
4. **Confidence Scoring** - Assigns confidence based on evidence quality

### Example Output

```python
db_engine = DatabaseSchemaInferenceEngine(app_path)
schema = db_engine.infer_schema()

# Output:
{
    'tables': {
        'users': {
            'columns': ['user_id', 'username', 'email', 'created_at'],
            'primary_key': 'user_id',
            'confidence': 0.95,  # ORM model = high confidence
            'source_apps': ['AdjustmentManager', 'PayrollManager'],
            'operations': ['SELECT', 'INSERT', 'UPDATE']
        },
        'transactions': {
            'columns': ['transaction_id', 'amount', 'date'],
            'primary_key': 'transaction_id',
            'confidence': 0.75,  # Multiple queries = medium-high
            'source_apps': ['PayrollManager'],
            'operations': ['SELECT', 'INSERT']
        }
    },
    'total_tables': 23,
    'high_confidence_tables': 18  # >=0.8 confidence
}
```

### Shared Database Context

Since all applications use the same Oracle database, CORTEX merges schema information across apps:

```python
# Get shared database info
db_info = orchestrator.get_shared_database_info()

print(f"Total tables: {db_info['total_tables']}")
print(f"High confidence: {db_info['high_confidence_tables']}")
print(f"Contributing apps: {db_info['contributing_apps']}")
```

---

## 🎯 Prioritization Algorithm

Applications are scored based on user activity patterns:

| Factor | Points | Notes |
|--------|--------|-------|
| Open files in VS Code | 40 each | Currently editing |
| Recent edits (last 7 days) | 30 each | Active development |
| Application size | 0-20 | Smaller = faster load |
| Has database access | 10 | More context available |

**Example:**
- App with 2 open files, 1 recent edit, 5 MB size, DB access
- Score: (2 × 40) + (1 × 30) + 18 + 10 = **158 points**

---

## 📈 Use Cases

### Scenario 1: Legacy ColdFusion Workspace

**Problem:** 14 ColdFusion applications, 70K+ files total, 2-3 GB codebase

**Solution:**
```python
# Initial load: 15-20 seconds (top 2 apps)
result = orchestrator.run_progressive()

# User focuses on specific app
result = orchestrator.load_application_on_demand('AdjustmentManager', depth='deep')

# Result: 90% faster than full scan (8 min → 45s)
```

### Scenario 2: Microservices Architecture

**Problem:** 20+ microservices, each with own repo structure

**Solution:**
```python
# Topology detection identifies all services
# Progressive load focuses on recently modified services
# Shared DB context builds API contract knowledge

# Result: Context for active services in <30s
```

### Scenario 3: Monorepo with Multiple Packages

**Problem:** Single repo with 10+ packages/modules

**Solution:**
```python
# Detect package boundaries
# Load packages by dependency order
# Cache reduces subsequent loads to <1s

# Result: Smart prioritization based on import patterns
```

---

## 🧪 Testing

### Unit Tests

```bash
# Run all multi-app tests
python -m pytest tests/crawlers/test_multi_app_system.py -v

# Test specific components
python -m pytest tests/crawlers/test_workspace_topology.py -v
python -m pytest tests/crawlers/test_application_scoped.py -v
python -m pytest tests/crawlers/test_persistent_cache.py -v
python -m pytest tests/crawlers/test_database_inference.py -v
```

### Integration Tests

```bash
# Test on real ColdFusion workspace
python tests/integration/test_coldfusion_workspace.py

# Performance benchmarks
python tests/benchmarks/test_multi_app_performance.py
```

---

## 🐛 Troubleshooting

### Cache Issues

**Problem:** Cache not persisting across restarts

**Solution:**
- Check `cortex-brain/context-cache/` exists
- Verify SQLite database is writable
- Check disk space

**Problem:** Cache growing too large

**Solution:**
```python
# Reduce TTL
cache_manager.ttl_days = 3

# Reduce max size
cache_manager.max_cache_size_mb = 250

# Manual cleanup
cache_manager.clear_all()
```

### Performance Issues

**Problem:** Initial load taking >30 seconds

**Solution:**
- Check if VS Code is indexing simultaneously
- Reduce number of immediate apps to 1
- Enable cache for subsequent loads

**Problem:** Database inference slow

**Solution:**
- Limit file scanning depth
- Use shallow mode initially
- Check for large SQL files

---

## 📚 API Reference

### MultiApplicationOrchestrator

```python
class MultiApplicationOrchestrator(CrawlerOrchestrator):
    def __init__(
        workspace_path: Path,
        knowledge_graph: Optional[KnowledgeGraph],
        cortex_brain_path: Optional[Path],
        config: Optional[Dict[str, Any]]
    )
    
    def run_progressive() -> OrchestrationResult
    """Execute progressive multi-application crawling"""
    
    def load_application_on_demand(
        app_name: str,
        depth: str = 'shallow'
    ) -> CrawlerResult
    """Load specific application on-demand"""
    
    def get_cache_stats() -> Dict[str, Any]
    """Get cache statistics"""
    
    def get_shared_database_info() -> Dict[str, Any]
    """Get shared database schema information"""
```

### PersistentApplicationCache

```python
class PersistentApplicationCache:
    def __init__(
        cache_dir: Path,
        max_cache_size_mb: int = 500,
        ttl_days: int = 7
    )
    
    def get(
        app_name: str,
        depth: str,
        fingerprint: str
    ) -> Optional[Dict[str, Any]]
    """Retrieve cached context"""
    
    def put(
        app_name: str,
        depth: str,
        fingerprint: str,
        data: Dict[str, Any]
    ) -> bool
    """Store context in cache"""
    
    def clear_app(app_name: str) -> bool
    """Clear cache for specific application"""
    
    def clear_all() -> bool
    """Clear all cache"""
    
    def get_stats() -> Dict[str, Any]
    """Get cache statistics"""
```

---

## 🔮 Future Enhancements

### Planned Features

1. **Real-time File Watching** - Auto-update context on file changes
2. **VS Code Integration** - Direct integration with VS Code workspace API
3. **Cross-Application Tracing** - Follow execution flow across apps
4. **AI-Powered Prioritization** - ML-based relevance scoring
5. **Distributed Caching** - Share cache across team members

### Experimental Features

- **Incremental Updates** - Delta-based context updates
- **Semantic Search** - Natural language queries across apps
- **Dependency Visualization** - Interactive dependency graphs

---

## 📝 Best Practices

### For Developers

1. **Use shallow mode initially** - Deep dive only when needed
2. **Let cache warm up** - Second load is 90% faster
3. **Clear stale cache periodically** - Use 7-day TTL
4. **Monitor cache size** - Keep under 500 MB

### For Architects

1. **Organize shared code properly** - Use `Common/` folders
2. **Document datasources** - Helps DB inference
3. **Use ORM when possible** - Highest confidence schema
4. **Keep apps modular** - Easier for CORTEX to analyze

---

## 📄 License

Copyright © 2024-2025 Asif Hussain. All rights reserved.

Source-Available License - Use Allowed, No Contributions

---

## 🤝 Support

For issues or questions:
- GitHub Issues: https://github.com/asifhussain60/CORTEX/issues
- Email: [contact information]

**Version:** 1.0  
**Last Updated:** 2025-11-25
