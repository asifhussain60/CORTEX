# CORTEX Master Orchestrator System

**Version:** 7.0 (2026-01-20)  
**Status:** Production-Ready  
**Python:** 3.9+ required (3.10+ recommended)

---

## 📋 Quick Links

- **Getting Started:** [`docs/01-getting-started/`](docs/01-getting-started/0-installation.md)
- **Architecture:** [`docs/02-architecture/`](docs/02-architecture/1-system-overview.md)
- **API Reference:** [`docs/03-api-reference/`](docs/03-api-reference/)
- **Guides & Examples:** [`docs/04-guides/`](docs/04-guides/)
- **Reference:** [`docs/05-reference/`](docs/05-reference/)

---

## 🏛️ File Placement Governance (TIER 0 - Immutable)

**CORTEX enforces strict file placement rules to maintain repository clarity and governance compliance. All files must be placed in their designated locations.**

### ✅ Allowed File Locations

| File Type | Location | Purpose | Example |
|-----------|----------|---------|---------|
| **User Documentation** | `docs/0X-*/*.md` | User guides, tutorials, references | `docs/01-getting-started/0-installation.md` |
| **Architecture Decisions** | `docs/02-architecture/adrs/*.md` | ADRs, technical decisions | `docs/02-architecture/adrs/adr-001-*.md` |
| **Implementation Reports** | `docs/_reports/*.md` | Phase reports, audit summaries | `docs/_reports/AUDIT-REPORT-20260120.md` |
| **Python Source Code** | `cortex/` | Main implementation (388 files) | `cortex/mcp/server.py` |
| **Python Tests** | `tests/` | Unit & integration tests | `tests/unit/test_*.py` |
| **Build Scripts** | `scripts/` | Build, setup, utility scripts | `scripts/setup_cortex_hub.py` |
| **Infrastructure** | `deployment/` | Docker, Kubernetes, cloud config | `deployment/prometheus/` |
| **MCP Configuration** | `mcp-config/` | Claude Desktop, VS Code MCP config | `mcp-config/vscode-mcp.json` |
| **Extensions** | `extensions/` | VS Code extensions, IDE plugins | `extensions/vscode-cortex/` |
| **Project Metadata** | Root only | `.gitignore`, `.pre-commit-config.yaml`, `requirements.txt`, `pytest.ini`, `conftest.py` | `requirements.txt` |

### ❌ Prohibited Locations

**NEVER create these at repository root:**

```
❌ .md files at root (docs/ ONLY)
❌ .py files at root (cortex/, src/, tests/, scripts/ ONLY)
   ✅ EXCEPTION: conftest.py (pytest configuration, required at root)
❌ docs_md/ folder (docs/ ONLY)
❌ Random reports in root (_workspaces/roadmap/reports/ or docs/_reports/ ONLY)
❌ Test outputs in root (tests/ ONLY)
❌ Configuration files outside their designated folders
```

### 📂 File Structure Reference

```
CORTEX/
├── README.md                          ← You are here (governance guide)
├── requirements.txt                   ← Production dependencies (PINNED)
├── pytest.ini                         ← Test configuration
├── conftest.py                        ← Pytest fixtures & hooks (ROOT ONLY - required)
├── cortex-config.yaml                 ← CORTEX system config
│
│
├── cortex/                            ← CANONICAL IMPLEMENTATION (388 files)
│   ├── api/                           ← FastAPI endpoints
│   ├── brain/                         ← Brain orchestration (269 files)
│   ├── core/                          ← Core utilities
│   ├── mcp/                           ← MCP server & tools
│   ├── infrastructure/                ← System infrastructure
│   ├── orchestrators/                 ← Orchestration engines
│   └── tools/                         ← Reusable tools
│
├── cortex_brain/                      ← GOVERNANCE STATE (tier0/1/2)
│   ├── tier0/                         ← 28 immutable core rules
│   ├── tier1/                         ← Orchestrator rules
│   ├── tier2/                         ← Domain-specific rules
│   └── state/                         ← Runtime state
│
├── docs/                              ← DOCUMENTATION ONLY
│   ├── 0-README.md                    ← Doc index
│   ├── 01-getting-started/            ← Installation & quickstart
│   ├── 02-architecture/               ← System design & ADRs
│   ├── 03-api-reference/              ← CLI, REST, MCP specs
│   ├── 04-guides/                     ← How-to guides
│   ├── 05-reference/                  ← FAQs, glossary, changelog
│   ├── 07-contributing/               ← Contribution guidelines
│   ├── _reports/                      ← Phase reports (docs/ only!)
│   ├── _manifests/                    ← Deployment manifests
│   └── _archive/                      ← Historical docs
│
├── tests/                             ← TEST SUITE (400+ tests)
│   ├── unit/                          ← Unit tests
│   ├── integration/                   ← Integration tests
│   └── conftest.py                    ← Shared fixtures
│
├── deployment/                        ← INFRASTRUCTURE
│   ├── grafana/                       ← Grafana dashboards
│   └── prometheus/                    ← Prometheus config
│
├── scripts/                           ← BUILD & UTILITIES
│   ├── setup_cortex_hub.py
│   ├── doc-categorization-rules.yaml
│   └── validation/
│
├── extensions/                        ← IDE PLUGINS
│   ├── vscode-cortex/
│   └── cortex-lsp-adapter/
│
├── mcp-config/                        ← MCP CONFIGURATION
│   ├── claude-desktop.json
│   └── vscode-mcp.json
│
├── _workspaces/                       ← PROJECT METADATA
│   └── roadmap/
│       ├── phases/                    ← Implementation phases (12 YAML files)
│       ├── reports/                   ← YAML roadmap reports
│       └── _archives/
│
└── .github/                           ← GIT METADATA
    ├── prompts/                       ← System prompts
    └── .chats/                        ← Chat history
```

---

## 📝 Documentation Folder Structure

### Top-Level Categories (01-XX)

**Naming Convention:** `XX-category-name/` where XX is sequence number

- **01-getting-started/** - Installation, quickstart, first steps
- **02-architecture/** - System design, ADRs, design decisions
- **03-api-reference/** - API specifications (REST, CLI, MCP)
- **04-guides/** - How-to guides, tutorials, advanced usage
- **05-reference/** - FAQ, glossary, changelog, known issues
- **07-contributing/** - Contribution guidelines, development setup

### File Naming Convention

```
# Within each category:
0-overview.md              ← Category overview/index
1-topic-name.md            ← First topic
2-another-topic.md         ← Second topic
N-descriptive-title.md     ← Sequential numbering

# Architecture Decision Records:
adrs/adr-NNN-slug-title.md ← Architecture Decision Records

# Special folders:
_reports/                  ← Phase & audit reports (YAML or MD)
_manifests/                ← Deployment manifests
_archive/                  ← Historical documentation
```

### Example Structure: `04-guides/deployment/`

```
04-guides/deployment/
├── 0-overview.md                    ← Deployment guide overview
├── 1-local-development.md           ← Local dev setup
├── 2-docker-deployment.md           ← Docker deployment
├── 3-cloud-deployment.md            ← Cloud (AWS/Azure) deployment
└── 4-faq.md                         ← Deployment FAQs
```

---

## 📋 Plain Reports (docs/_reports/)

**All informational/analysis reports go to `docs/_reports/`**

### Report Types & Naming

| Report Type | Naming Pattern | Example |
|-------------|----------------|---------|
| Audit Report | `AUDIT-{TOPIC}-{DATE}.md` | `AUDIT-IMPORT-STRUCTURE-20260120.md` |
| Phase Report | `PHASE-{NUMBER}-{TITLE}-{DATE}.yaml` | `PHASE-23-MCP-COMPLIANCE-20260120.yaml` |
| Analysis | `ANALYSIS-{TOPIC}-{DATE}.md` | `ANALYSIS-ARCHITECTURAL-GAP-20260120.md` |
| Completion | `COMPLETION-{PHASE}-{DATE}.md` | `COMPLETION-PHASE-22-20260120.md` |

### Rationale

- **Why docs/_reports/?** Centralized, discoverable location for all analysis/reporting
- **Why not root?** TIER 0 rule: `*.md` files ONLY in `docs/` folder
- **Why not _workspaces/?** User docs should be in primary `docs/` folder; roadmap tracking in `_workspaces/roadmap/`

---

## 🔒 Governance Enforcement (TIER 0)

### Rules Enforced

| Rule | Enforcement | Status |
|------|-------------|--------|
| **MD-001** | All `.md` files in `docs/` or `docs/_reports/` ONLY | 🔴 BLOCKED at root |
| **MD-002** | No `docs_md/`, `documentation/`, or alternate structures | 🔴 BLOCKED |
| **PY-001** | No `.py` files in root (except pytest configs) | ✅ Enforced |
| **PY-001-EXCEPTION** | `conftest.py` required at root (pytest fixture discovery) | ✅ Allowed |
| **PY-002** | Source: `cortex/` | ✅ Enforced |
| **PY-003** | Tests: `tests/` | ✅ Enforced |
| **PY-004** | Scripts: `scripts/` | ✅ Enforced |
| **CONFIG-001** | Configuration files at root only (`.yaml`, `.txt`, `.ini`, `.json`) | ✅ Enforced |

### Pre-Commit Hook

```bash
# Pre-commit check prevents commits with violations:
find . -path ./docs -prune -o -name '*.md' -type f -print
# ^ Must return ONLY: ./docs/...
# Any files outside docs/ trigger: ❌ COMMIT BLOCKED

find . -name '*.py' -maxdepth 1 -type f
# ^ Must return EMPTY
# Any root .py files trigger: ❌ COMMIT BLOCKED
```

---

## 🚀 Getting Started

### Installation

```bash
# Clone repository
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # macOS/Linux
# or
.venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest -v
```

See [`docs/01-getting-started/0-installation.md`](docs/01-getting-started/0-installation.md) for detailed setup.

### First Steps

1. **Read Architecture:** [`docs/02-architecture/1-system-overview.md`](docs/02-architecture/1-system-overview.md)
2. **Run Quickstart:** [`docs/01-getting-started/1-quickstart.md`](docs/01-getting-started/1-quickstart.md)
3. **Explore API:** [`docs/03-api-reference/`](docs/03-api-reference/)
4. **Try Guides:** [`docs/04-guides/`](docs/04-guides/)

---

## 📦 Project Information

| Aspect | Details |
|--------|---------|
| **Language** | Python 3.9+ |
| **Framework** | FastAPI + Async |
| **MCP Implementation** | Custom JSON-RPC 2.0 (cortex/mcp/) |
| **Testing** | Pytest (400+ tests) |
| **Code Quality** | Black, MyPy, Pylint, Flake8 |
| **Main Package** | `cortex/` (388 files, canonical) |
| **Governance** | TIER 0 rules, cortex_brain/ state |

---

## 📖 Documentation Index

| Topic | Location |
|-------|----------|
| Installation & Setup | `docs/01-getting-started/0-installation.md` |
| System Architecture | `docs/02-architecture/1-system-overview.md` |
| MCP Protocol | `docs/03-api-reference/mcp-protocol/0-specification.md` |
| REST API | `docs/03-api-reference/rest-api/0-guide.md` |
| Deployment Guides | `docs/04-guides/deployment/` |
| FAQ & Troubleshooting | `docs/05-reference/faq.md` |
| Contributing | `docs/07-contributing/1-contributing-guidelines.md` |
| Changelog | `docs/05-reference/changelog.md` |
| Known Issues | `docs/05-reference/known-issues.md` |

---

## 🔍 Important Notes

### cortex_toolkit/ Status

❌ **DELETED** (2026-01-20)  
✅ **Reason:** Empty placeholder; `cortex/` is canonical package (ARCH-DECISION-RECORD)  
✅ **Decision:** All MCP tools in `cortex/mcp/` (confirmed 23+ tools)

See: [`docs/02-architecture/adrs/adr-001-cortex-canonical-package.md`](docs/02-architecture/adrs/) (if available)

### src/ Folder Status

⚠️ **Under Consolidation**  
- Tests still import from `src.*` (~20 active imports)
- Separate consolidation phase required
- See: `_workspaces/roadmap/reports/` for details

---

## 📄 License

See [`LICENSE.md`](docs/LICENSE.md) for license information.

---

## 🤝 Contributing

**Before contributing, read:** [`docs/07-contributing/1-contributing-guidelines.md`](docs/07-contributing/1-contributing-guidelines.md)

**Key rules:**
1. Follow file placement governance above
2. All `.md` files → `docs/` folder
3. All `.py` files → appropriate subfolder (`cortex/`, `tests/`, `scripts/`)
4. No markdown at repository root
5. Reports → `docs/_reports/` with proper naming

---

## 🆘 Support & Documentation

- **Issues:** File on GitHub
- **FAQ:** [`docs/05-reference/faq.md`](docs/05-reference/faq.md)
- **Troubleshooting:** [`docs/01-getting-started/3-troubleshooting.md`](docs/01-getting-started/3-troubleshooting.md)
- **Deployment:** [`docs/04-guides/deployment/0-overview.md`](docs/04-guides/deployment/0-overview.md)

---

**Last Updated:** 2026-01-20  
**Maintained By:** CORTEX Development Team  
**Status:** ✅ Production Ready (TIER 0 Governance Active)
