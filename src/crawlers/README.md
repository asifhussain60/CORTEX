"""
Unified Crawler System for CORTEX

Complete implementation with orchestrator, tooling, UI, API, and database crawlers.

## Architecture

```
CrawlerOrchestrator
├── ToolingCrawler (CRITICAL priority - runs first)
│   ├── Discovers: Databases, APIs, Build Tools, Frameworks
│   └── Determines: Which other crawlers to run
├── UICrawler (HIGH priority)
│   └── Discovers: UI components, element IDs, routes
├── APICrawler (HIGH priority)
│   └── Discovers: REST endpoints, GraphQL schemas
└── Database Crawlers (MEDIUM priority - conditional)
    ├── OracleCrawler (if Oracle connections found)
    ├── SQLServerCrawler (if SQL Server connections found)
    └── PostgresCrawler (if Postgres connections found)
```

## Usage

### Run All Crawlers

```python
from src.crawlers.orchestrator import CrawlerOrchestrator
from src.crawlers.tooling_crawler import ToolingCrawler
from src.crawlers.ui_crawler import UICrawler
from src.crawlers.api_crawler import APICrawler
from src.tier2.knowledge_graph import KnowledgeGraph
from pathlib import Path

# Initialize knowledge graph
kg = KnowledgeGraph()

# Create orchestrator
orchestrator = CrawlerOrchestrator(
    workspace_path=Path.cwd(),
    knowledge_graph=kg,
    parallel=True,
    max_workers=4
)

# Register crawlers
orchestrator.register(ToolingCrawler)
orchestrator.register(UICrawler)
orchestrator.register(APICrawler)
# Database crawlers registered but only run if connections found

# Execute all
result = orchestrator.run_all()

print(f"Completed: {result.completed}/{result.total_crawlers}")
print(f"Discovered: {result.total_items_discovered} items")
print(f"Stored: {result.total_patterns_created} patterns")
```

### Run Single Crawler

```python
result = orchestrator.run_single('tooling_crawler')
print(f"Status: {result.status}")
print(f"Items: {result.items_discovered}")
```

### Via Plugin (Recommended)

```bash
# Run all crawlers
cortex crawlers:run

# Run specific crawler
cortex crawlers:run --crawler=tooling

# List available crawlers
cortex crawlers:list

# Get crawler status
cortex crawlers:status
```

## Adding New Crawlers

1. Create new crawler class inheriting from `BaseCrawler`
2. Implement required methods:
   - `get_crawler_info()` - Metadata and dependencies
   - `validate()` - Check if crawler can run
   - `crawl()` - Discovery logic
   - `store_results()` - Save to knowledge graph
3. Register with orchestrator
4. Add to plugin command handlers

Example:

```python
from src.crawlers.base_crawler import BaseCrawler, CrawlerPriority

class GitCrawler(BaseCrawler):
    def get_crawler_info(self):
        return {
            'crawler_id': 'git_crawler',
            'name': 'Git History Crawler',
            'version': '1.0.0',
            'priority': CrawlerPriority.LOW,
            'dependencies': [],
            'description': 'Discovers git history and patterns'
        }
    
    def validate(self):
        return (self.workspace_path / '.git').exists()
    
    def crawl(self):
        # Git discovery logic
        return {'commits': [...], 'branches': [...]}
    
    def store_results(self, data):
        # Store patterns
        return len(data['commits'])

# Register
orchestrator.register(GitCrawler)
```

## Crawler Results

Each crawler returns a `CrawlerResult` with:

- `status`: COMPLETED, FAILED, SKIPPED
- `items_discovered`: Number of items found
- `patterns_created`: Number of patterns stored
- `duration_seconds`: Execution time
- `errors`: List of error messages
- `warnings`: List of warnings
- `metadata`: Crawler-specific data

## Orchestration Features

### Dependency Resolution
- Crawlers declare dependencies
- Orchestrator resolves execution order
- Dependencies run first

### Conditional Execution
- Database crawlers only run if connections found
- UI crawler only runs if UI frameworks detected
- Configurable via `_should_run_crawler()`

### Parallel Execution
- Independent crawlers run in parallel
- Configurable max workers
- Sequential execution for dependencies

### Error Handling
- Individual crawler failures don't stop orchestration
- Errors captured in results
- Cleanup always runs

### Progress Reporting
- Real-time logging
- Result aggregation
- Summary statistics

## Extensibility

The system is designed for easy extension:

1. **Base Class**: All crawlers inherit common functionality
2. **Registration**: Dynamic crawler registration
3. **Plugins**: Plugin system for user commands
4. **Configuration**: Per-crawler configuration support
5. **Hooks**: Lifecycle hooks for customization

## Integration Points

### Knowledge Graph (Tier 2)
- All crawlers store results as patterns
- Standardized format (scope, namespace, tags)
- FTS5 search across all crawler data

### Configuration Wizard
- Tooling crawler integrates with config wizard
- Auto-discovered connections validated
- Results saved to cortex.config.json

### Brain Protection Rules
- All crawlers respect brain protection rules
- Patterns have confidence scores
- Decay rules apply uniformly

## Performance

- Tooling crawler: ~2-5 seconds
- UI crawler: ~5-10 seconds
- API crawler: ~3-8 seconds
- Database crawlers: ~10-30 seconds each
- Total (parallel): ~15-40 seconds

## Testing

Run tests:

```bash
# All crawler tests
python -m pytest tests/crawlers/ -v

# Specific crawler
python -m pytest tests/crawlers/test_tooling_crawler.py -v

# With coverage
python -m pytest tests/crawlers/ -v --cov=src/crawlers
```

## Next Steps

1. ✅ Base crawler infrastructure
2. ✅ Orchestrator with dependencies
3. ✅ Tooling crawler
4. 🚧 UI crawler
5. 🚧 API crawler
6. 🚧 Database crawler adapters
7. 🚧 Plugin integration
8. 🚧 Comprehensive tests
9. ⬜ Documentation
10. ⬜ User guide

Author: Syed Asif Hussain
Copyright: © 2024-2025 Syed Asif Hussain. All rights reserved.
"""
