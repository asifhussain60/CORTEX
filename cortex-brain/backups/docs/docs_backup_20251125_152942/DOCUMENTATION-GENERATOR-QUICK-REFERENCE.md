# CORTEX Documentation Generator - Quick Reference

## 🚀 Quick Start

```bash
# Generate all documentation
python -m src.documentation.cli generate --workspace . --output docs --parallel

# Scan workspace capabilities
python -m src.documentation.cli scan

# Validate documentation
python -m src.documentation.cli validate --docs-dir docs
```

## 📋 CLI Commands

### Generate
```bash
python -m src.documentation.cli generate [options]

Options:
  --workspace PATH    Workspace root directory (default: .)
  --output PATH       Output directory (default: docs)
  --parallel          Enable parallel generation (8 workers)
```

### Scan
```bash
python -m src.documentation.cli scan [options]

Options:
  --workspace PATH    Workspace root directory (default: .)
  --output PATH       Export registry to file (optional)
```

### Validate
```bash
python -m src.documentation.cli validate [options]

Options:
  --docs-dir PATH     Documentation directory (default: docs)
```

### Report
```bash
python -m src.documentation.cli report [options]

Options:
  --report PATH       Report file path (default: docs/generation-report.json)
  --verbose           Show detailed information
```

## 📦 Programmatic API

```python
from src.documentation import (
    DocumentationOrchestrator,
    CapabilityScanner,
    TemplateEngine
)

# Scan capabilities
scanner = CapabilityScanner('.')
capabilities = scanner.scan_all()
print(f"Found {len(capabilities)} capabilities")

# Generate documentation
orchestrator = DocumentationOrchestrator('.', 'docs')
report = orchestrator.generate_all(parallel=True)
print(f"Generated {len(report['results'])} components")

# Use template engine
engine = TemplateEngine()
content = engine.generate_capabilities_doc({
    'version': '3.0',
    'capabilities': capabilities
})
```

## 📊 Generated Components

### Executive/Overview (5)
- `EXECUTIVE-SUMMARY.md` - High-level overview with metrics
- `CORTEX-CAPABILITIES.md` - Detailed capabilities matrix
- `FEATURES.md` - Categorized feature list
- `QUICK-START.md` - Getting started guide
- `README.md` - Enhanced project readme

### Narratives (5)
- `THE-AWAKENING-OF-CORTEX.md` - Complete CORTEX origin story
- User journey documentation
- Evolution story
- Vision and mission
- Case studies

### Visual Assets (28)
- **ChatGPT Image Prompts (12):** architecture, agent_interaction, brain_structure, workflow, memory_system, plugin_ecosystem, knowledge_graph, ui_mockup, integration_points, data_flow, security_layers, performance_metrics
- **Mermaid Diagrams (16):** system-overview, component-relationships, tier-structure, agent-coordination, feature-planning, implementation, testing, conversation-capture, pattern-learning, context-injection, plugin-communication, brain-protection, vscode, git, mkdocs-pipeline, external-apis

### Technical References (34)
- API references
- Operations guides
- Module documentation
- Plugin guides
- Navigation structure
- Metadata reports
- Landing pages

## 🔍 Capability Types

| Type | Count | Description |
|------|-------|-------------|
| Agent | 25 | Specialized AI agents |
| Capability | 11 | Core system capabilities |
| Module | 45 | Functional modules |
| Operation | 23 | User-facing operations |
| Plugin | 25 | Extensibility plugins |
| **Total** | **129** | **Discovered capabilities** |

## ⚡ Performance

| Metric | Value |
|--------|-------|
| Discovery Time | ~3 seconds |
| Generation Time | ~7 seconds |
| Total Time | ~10 seconds |
| Components Generated | 38/72 (53%) |
| Parallel Workers | 8 |
| Throughput | 5.3 components/second |

## 🧪 Testing

```bash
# Run all tests
pytest tests/documentation/test_documentation_system.py -v

# Run specific test category
pytest tests/documentation/test_documentation_system.py::TestCapabilityScanner -v

# Run without slow tests
pytest tests/documentation/test_documentation_system.py -v -k "not slow"
```

## 📁 Directory Structure

```
src/documentation/
├── __init__.py               # Package exports
├── cli.py                    # CLI interface (4 commands)
├── orchestrator.py           # Main orchestrator (72 generators)
├── discovery/
│   ├── __init__.py
│   └── capability_scanner.py # Capability discovery
└── templates/
    ├── __init__.py
    └── template_engine.py    # Template-based generation

tests/documentation/
├── conftest.py               # Test fixtures
└── test_documentation_system.py  # Test suite (20 tests)

docs/
├── EXECUTIVE-SUMMARY.md
├── CORTEX-CAPABILITIES.md
├── THE-AWAKENING-OF-CORTEX.md
├── FEATURES.md
├── QUICK-START.md
├── image-prompts/           # ChatGPT image prompts (12 files)
└── diagrams/
    └── mermaid/             # Mermaid diagrams (16 files)
```

## 🔧 Configuration

No configuration files required! The system discovers everything automatically from:
- `cortex-brain/cortex-operations.yaml` - Operations
- `cortex-brain/module-definitions.yaml` - Modules
- `cortex-brain/capabilities.yaml` - Core capabilities
- `src/**/*.py` - Python source files (agents, plugins)
- `.git/` - Git history for feature tracking

## 🎯 Use Cases

### Daily Development
```bash
# Regenerate docs after code changes
python -m src.documentation.cli generate --parallel
```

### Release Process
```bash
# Scan capabilities for changelog
python -m src.documentation.cli scan --output release-capabilities.json

# Generate fresh documentation
python -m src.documentation.cli generate --output docs/release

# Validate before publish
python -m src.documentation.cli validate --docs-dir docs/release
```

### CI/CD Integration
```bash
# In GitHub Actions workflow
- name: Generate Documentation
  run: |
    python -m src.documentation.cli generate --parallel
    python -m src.documentation.cli validate
```

### Analysis
```bash
# Scan and analyze capabilities
python -m src.documentation.cli scan --output analysis.json

# View detailed report
python -m src.documentation.cli report --report docs/generation-report.json --verbose
```

## 🚨 Troubleshooting

### Import Errors
```bash
# Ensure you're in project root
cd /path/to/CORTEX

# Verify Python path
python -c "import sys; print(sys.path)"
```

### Generation Failures
```bash
# Run without parallel to see detailed errors
python -m src.documentation.cli generate

# Check individual components
python -c "from src.documentation import DocumentationOrchestrator; o = DocumentationOrchestrator('.'); o._generate_executive_summary({}, {})"
```

### Test Failures
```bash
# Run tests with verbose output
pytest tests/documentation/ -vv --tb=short

# Run specific failing test
pytest tests/documentation/test_documentation_system.py::TestClass::test_method -vv
```

## 📚 References

- **Full Documentation:** `cortex-brain/documents/implementation-guides/ENTERPRISE-DOCUMENTATION-SYSTEM-COMPLETE.md`
- **Test Suite:** `tests/documentation/test_documentation_system.py`
- **Source Code:** `src/documentation/`

---

**Quick Help:** Run `python -m src.documentation.cli --help` for full command reference
