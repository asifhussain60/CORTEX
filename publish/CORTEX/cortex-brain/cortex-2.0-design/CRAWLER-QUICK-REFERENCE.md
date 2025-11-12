# CORTEX Unified Crawler System - Quick Reference

## What We Built

✅ **Complete crawler architecture** with:
- Base crawler class for extensibility
- Orchestrator with dependency resolution
- Tooling crawler (databases, APIs, tools)
- UI crawler (components, element IDs, routes)
- Ready for database crawler integration

## File Structure

```
src/crawlers/
├── __init__.py                 # Package exports
├── base_crawler.py             # BaseCrawler (345 lines) ✅
├── orchestrator.py             # Orchestrator (427 lines) ✅
├── tooling_crawler.py          # Tooling discovery (733 lines) ✅
├── ui_crawler.py               # UI discovery (490 lines) ✅
└── README.md                   # Documentation (215 lines) ✅

src/tier2/
└── oracle_crawler.py           # Existing (584 lines) - needs adapter

cortex-brain/cortex-2.0-design/
└── CRAWLER-SYSTEM-COMPLETE.md  # Implementation summary
```

## How It Works

```
1. Orchestrator starts
   ↓
2. Tooling Crawler runs (CRITICAL priority)
   - Discovers: Databases, APIs, Build Tools, Frameworks
   - Determines: Which other crawlers to run
   ↓
3. UI Crawler runs (if UI framework detected)
   - Discovers: Components, Element IDs, Routes
   ↓
4. API Crawler runs
   - Discovers: REST endpoints, GraphQL schemas
   ↓
5. Database Crawlers run (conditional)
   - Oracle (if Oracle connections found)
   - SQL Server (if SQL Server connections found)
   - PostgreSQL (if Postgres connections found)
   ↓
6. Results stored in Knowledge Graph (Tier 2)
```

## Usage Example

```python
from pathlib import Path
from src.crawlers.orchestrator import CrawlerOrchestrator
from src.crawlers.tooling_crawler import ToolingCrawler
from src.crawlers.ui_crawler import UICrawler
from src.tier2.knowledge_graph import KnowledgeGraph

# Initialize
kg = KnowledgeGraph()
orchestrator = CrawlerOrchestrator(
    workspace_path=Path.cwd(),
    knowledge_graph=kg,
    parallel=True
)

# Register crawlers
orchestrator.register(ToolingCrawler)
orchestrator.register(UICrawler)
# Add more as they're implemented

# Run all
result = orchestrator.run_all()

print(f"Completed: {result.completed}/{result.total_crawlers}")
print(f"Items discovered: {result.total_items_discovered}")
print(f"Patterns created: {result.total_patterns_created}")
```

## Key Features

### 1. Extensibility
- Add new crawlers by inheriting from `BaseCrawler`
- Implement 4 methods: `get_crawler_info()`, `validate()`, `crawl()`, `store_results()`
- Register with orchestrator

### 2. Smart Execution
- **Dependency Resolution**: Runs crawlers in correct order
- **Conditional Execution**: Skips DB crawlers if no connections
- **Parallel Execution**: Independent crawlers run concurrently
- **Error Handling**: Individual failures don't stop others

### 3. Knowledge Graph Integration
- All results stored as patterns in Tier 2
- FTS5 search enabled
- Namespace boundaries enforced
- Confidence scoring

## What Tooling Crawler Discovers

### Databases
- ✅ Oracle tnsnames.ora
- ✅ Environment variables (ORACLE_CONNECTION_STRING, etc.)
- ✅ Connection strings in code
- ✅ Configuration files (appsettings.json, .env)

### APIs
- ✅ OpenAPI/Swagger specs
- ✅ Environment variables (API_BASE_URL)
- ✅ REST endpoints in code

### Build Tools
- ✅ npm/yarn (package.json)
- ✅ Maven (pom.xml)
- ✅ Gradle (build.gradle)
- ✅ .NET (*.csproj)
- ✅ Python (requirements.txt, Pipfile, pyproject.toml)
- ✅ Go (go.mod)
- ✅ Rust (Cargo.toml)

### Frameworks
- ✅ React, Angular, Vue (frontend)
- ✅ Flask, Django, FastAPI (Python)
- ✅ Express, Next.js (Node.js)

## What UI Crawler Discovers

### React Components
- ✅ Component names and files
- ✅ Element IDs (`id="..."`)
- ✅ Routes (`<Route path="...">`)
- ✅ Props
- ✅ Dependencies

### Angular Components
- ✅ Component classes
- ✅ Template element IDs
- ✅ Route configurations
- ✅ @Input decorators

### Vue Components
- ✅ Component files
- ✅ Template element IDs
- ✅ Props
- ✅ Routes

## Next Steps

### Phase 1: Complete Core Crawlers
1. ⬜ API crawler (REST, GraphQL)
2. ⬜ Adapt Oracle crawler to BaseCrawler
3. ⬜ SQL Server crawler
4. ⬜ PostgreSQL crawler

### Phase 2: Plugin Integration
5. ⬜ Create crawler plugin
6. ⬜ Add commands (`cortex crawlers:run`, `crawlers:list`, etc.)
7. ⬜ Progress reporting
8. ⬜ Result formatting

### Phase 3: Testing
9. ⬜ Unit tests for all crawlers
10. ⬜ Orchestrator tests
11. ⬜ Integration tests
12. ⬜ Mock database tests

### Phase 4: Documentation
13. ⬜ User guide
14. ⬜ Developer guide
15. ⬜ API documentation

## Adding a New Crawler

```python
from src.crawlers.base_crawler import BaseCrawler, CrawlerPriority

class MyCrawler(BaseCrawler):
    def get_crawler_info(self):
        return {
            'crawler_id': 'my_crawler',
            'name': 'My Custom Crawler',
            'version': '1.0.0',
            'priority': CrawlerPriority.MEDIUM,
            'dependencies': ['tooling_crawler'],  # Optional
            'description': 'Discovers X, Y, Z'
        }
    
    def validate(self):
        # Check if crawler can run
        return True
    
    def crawl(self):
        # Discovery logic
        return {'items': [...]}
    
    def store_results(self, data):
        # Store in knowledge graph
        for item in data['items']:
            self.knowledge_graph.add_pattern(...)
        return len(data['items'])

# Register
orchestrator.register(MyCrawler)
```

## Performance

| Crawler | Expected Time |
|---------|---------------|
| Tooling | ~3 seconds |
| UI | ~7 seconds |
| API | ~5 seconds |
| Oracle | ~15 seconds |
| SQL Server | ~15 seconds |
| **Total (parallel)** | **~20 seconds** |

## Design Principles

1. **Extensible**: Easy to add new crawlers
2. **Conditional**: Smart execution based on detection
3. **Resilient**: Errors don't cascade
4. **Integrated**: Deep knowledge graph integration
5. **Fast**: Parallel execution where possible
6. **User-Friendly**: Simple API and CLI

## Testing the System

When ready, you can test with:

```bash
# After plugin implementation
cortex crawlers:run

# Or manually
python -c "
from pathlib import Path
from src.crawlers.orchestrator import CrawlerOrchestrator
from src.crawlers.tooling_crawler import ToolingCrawler
from src.tier2.knowledge_graph import KnowledgeGraph

kg = KnowledgeGraph()
orch = CrawlerOrchestrator(Path.cwd(), kg)
orch.register(ToolingCrawler)
result = orch.run_all()
print(result.to_dict())
"
```

## Summary

✅ **Architecture Complete**
- Extensible base class with lifecycle
- Orchestrator with dependencies and conditions
- Smart execution flow

✅ **Core Crawlers Implemented**
- Tooling crawler (733 lines) - discovers everything
- UI crawler (490 lines) - finds components and IDs

✅ **Ready for Integration**
- Knowledge graph storage
- Plugin system hooks
- Configuration support

🚧 **Next: Implementation**
- API crawler
- Database adapters
- Plugin integration
- Testing suite

**Total Code**: ~2,236 lines (base + orchestrator + crawlers + docs)

The system is ready to test the crawlers individually and can be extended with additional crawler types as needed!
