# CORTEX LENS - Unified Code Intelligence Package

**Version:** 2.0.0  
**Consolidated:** 2026-02-02  
**Authority:** CORE-035 (Single Canonical Implementation)

---

## 📦 Package Structure

```
cortex/lens/
├── __init__.py                    # Top-level imports
├── orchestrator.py                # LENSOrchestrator (unified analysis)
├── analyzers/                     # Code analysis components
│   ├── __init__.py
│   ├── ast_analyzer.py           # Python AST parsing
│   ├── git_history_analyzer.py   # Git commit history
│   ├── comment_extractor.py      # Comments, TODOs, docs
│   ├── config_analyzer.py        # Config security analysis
│   ├── database_analyzer.py      # DB schema/migration analysis
│   ├── api_analyzer.py           # API endpoint analysis
│   └── dependency_analyzer.py    # Dependency vulnerabilities
└── discovery/                     # Discovery plugins
    ├── __init__.py
    ├── config_discovery.py       # Config file discovery
    └── database_discovery.py     # Database topology discovery
```

---

## 🚀 Usage

### Quick Start

```python
from cortex.lens import LENSOrchestrator, ASTAnalyzer

# Unified analysis via orchestrator
orchestrator = LENSOrchestrator(repo_path=Path("/workspace/my-repo"))
result = orchestrator.analyze_repository_holistic()

# Direct analyzer usage
analyzer = ASTAnalyzer()
ast_result = analyzer.analyze_file(Path("my_module.py"))
```

### Import Patterns

**Recommended (Top-level):**
```python
from cortex.lens import LENSOrchestrator
from cortex.lens.analyzers import ASTAnalyzer, GitHistoryAnalyzer
from cortex.lens.discovery import ConfigurationDiscovery
```

**Also Valid:**
```python
from cortex.lens.orchestrator import LENSOrchestrator, LENSContext
from cortex.lens.analyzers.ast_analyzer import ASTAnalyzer
```

---

## 🔌 MCP Exposure

All LENS functionality exposed via MCP tools in `cortex/mcp/tools/lens_tools.py`:

- `cortex_lens_analyze` - Unified file analysis
- `cortex_git_history` - Git history (24h context)
- `cortex_ast_analyze` - AST structure analysis
- `cortex_extract_comments` - Comment/TODO extraction
- `cortex_detect_duplicates` - CORE-035 duplicate detection
- `cortex_tools_catalog` - Tool discovery

MCP tools are thin wrappers importing from `cortex.lens.*`

---

## 📊 Analyzers

### ASTAnalyzer
Parses Python AST for:
- Functions (name, parameters, line numbers, async/sync)
- Classes (name, methods, bases, line numbers)
- Imports (standard library, third-party, local)
- Complexity metrics (cyclomatic complexity)

### GitHistoryAnalyzer
Analyzes git history for:
- Recent commits (24h default, configurable)
- File-specific history and blame
- Contributor patterns
- Commit message analysis

### CommentExtractor
Extracts documentation:
- TODOs, FIXMEs, HACKs
- Docstrings (function, class, module)
- Inline comments
- Comment quality metrics

### ConfigAnalyzer
Security analysis for configs:
- Secret detection (API keys, passwords, tokens)
- Insecure defaults (debug=true, weak encryption)
- Missing required fields
- Schema validation

### DatabaseAnalyzer
Database intelligence:
- Schema extraction (tables, columns, relationships)
- Migration analysis (Alembic, Flyway, EF Core, Django)
- ER diagram generation (Mermaid format)
- Index optimization recommendations

### APIAnalyzer
API endpoint analysis:
- OpenAPI/Swagger parsing
- Endpoint security (auth, CORS, rate limiting)
- OWASP API Security Top 10 compliance
- Route documentation

### DependencyAnalyzer
Dependency scanning:
- Package vulnerability detection (CVE checks)
- Outdated dependencies
- License compliance
- Dependency graph analysis

---

## 🔍 Discovery Plugins

### ConfigurationDiscovery
Discovers configuration files:
- JSON (appsettings.json, package.json)
- YAML (docker-compose.yml, .gitlab-ci.yml)
- ENV (.env, .env.local, .env.production)
- XML (web.config, app.config)
- Connection string extraction (masked)

### DatabaseDiscovery
Database topology discovery:
- Connection string parsing (SQL Server, PostgreSQL, MySQL, Oracle)
- ORM detection (Entity Framework, SQLAlchemy, Django)
- Migration framework detection (Alembic, Flyway, EF Migrations)
- Schema inference from models

---

## 🎼 LENSOrchestrator

**Unified analysis orchestrator** coordinating all analyzers:

```python
orchestrator = LENSOrchestrator(repo_path=Path("/repo"))

# Analyze single file
file_result = orchestrator.analyze_file(
    file_path=Path("src/main.py"),
    include_git=True,
    include_ast=True,
    include_comments=True
)

# Holistic repository analysis (all 9 analyzers)
repo_result = orchestrator.analyze_repository_holistic(
    include_vision=False,
    include_security=True
)
```

**9 Analyzers Integrated:**
1. GitHistoryAnalyzer - Commit patterns
2. ASTAnalyzer - Code structure
3. CommentExtractor - Documentation
4. VisionAnalyzer - UI/diagrams (if enabled)
5. ConfigAnalyzer - Config security
6. DatabaseAnalyzer - Schema analysis
7. APIAnalyzer - Endpoint security
8. SecurityAdvisorMixin - Threat modeling
9. DependencyAnalyzer - Vulnerabilities

---

## 📁 Separation of Concerns

**Backend (Python):**
- `cortex/lens/` - Pure Python intelligence package
- `cortex/mcp/tools/lens_tools.py` - MCP tool wrappers

**Frontend (Static Assets):**
- `cortex-lens/` - HTML dashboards, JS, CSS
- Served separately (nginx), consumes MCP API

**Clear boundaries:** Backend and frontend never mixed.

---

## 🔄 Migration from Old Paths

| Old Location | New Location | Status |
|--------------|--------------|--------|
| `cortex.brain.analysis.ast_analyzer` | `cortex.lens.analyzers.ast_analyzer` | ✅ Moved |
| `cortex.brain.analysis.git_history_analyzer` | `cortex.lens.analyzers.git_history_analyzer` | ✅ Moved |
| `cortex.brain.analysis.comment_extractor` | `cortex.lens.analyzers.comment_extractor` | ✅ Moved |
| `cortex.brain.analysis.config_analyzer` | `cortex.lens.analyzers.config_analyzer` | ✅ Moved |
| `cortex.brain.analysis.database_analyzer` | `cortex.lens.analyzers.database_analyzer` | ✅ Moved |
| `cortex.brain.analysis.api_analyzer` | `cortex.lens.analyzers.api_analyzer` | ✅ Moved |
| `cortex.brain.analysis.dependency_analyzer` | `cortex.lens.analyzers.dependency_analyzer` | ✅ Moved |
| `cortex.brain.discovery.config_discovery` | `cortex.lens.discovery.config_discovery` | ✅ Moved |
| `cortex.brain.discovery.database_discovery` | `cortex.lens.discovery.database_discovery` | ✅ Moved |
| `cortex.orchestrators.support.lens_orchestrator` | `cortex.lens.orchestrator` | ✅ Moved |

**Deprecation stubs** in old locations emit warnings, removed next sprint.

---

## 🧪 Testing

Tests follow same structure:

```
tests/unit/lens/
├── analyzers/
│   ├── test_ast_analyzer.py
│   ├── test_git_history_analyzer.py
│   └── ...
├── discovery/
│   ├── test_config_discovery.py
│   └── test_database_discovery.py
└── test_lens_orchestrator.py
```

**Import in tests:**
```python
from cortex.lens import LENSOrchestrator
from cortex.lens.analyzers import ASTAnalyzer
```

---

## 🎯 Design Goals

1. **Single Canonical Location** - All LENS components in one package (CORE-035)
2. **Clear Imports** - `from cortex.lens import X` (discoverable, intuitive)
3. **MCP-First** - All features exposed via MCP tools in `cortex/mcp/tools/`
4. **Separation of Concerns** - Backend Python separate from frontend HTML/JS
5. **No Backward Compatibility** - Clean break, forced migration (ARCH-006)

---

## 📚 Related Documentation

- **MCP Tools:** `cortex/mcp/tools/lens_tools.py`
- **Frontend Dashboards:** `cortex-lens/README.md`
- **Test Suite:** `tests/unit/lens/`
- **Examples:** `examples/lens_v2_usage.py`

---

*LENS v2.0 - Unified, consolidated, MCP-exposed. 2026-02-02.*
