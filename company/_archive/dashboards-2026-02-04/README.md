# CORTEX Repository Dashboards# Dashboard Migration Notice



**Status:** PRODUCTION  **Status:** MIGRATED to cortex/visualization/dashboards/

**Structure:** Unified asset sharing with per-repo isolation  

**MCP Exposure:** Full CRUD via `cortex_dashboard_*` toolsThis directory has been migrated as part of Phase 21 (JSON-First Architecture rewrite).



---## New Locations



## 📁 Directory Structure| Component | Old Path | New Path |

|-----------|----------|----------|

```| Landing Page | company/dashboards/index.html | cortex/visualization/dashboards/spa/index.html |

company/dashboards/| Registry | company/dashboards/registry.json | cortex/visualization/dashboards/spa/registry.json |

├── index.html                    # Landing page (hero + tile grid)| SPA Assets | company/dashboards/spa/ | cortex/visualization/dashboards/spa/ |

├── registry.json                 # Master registry of all repos| Dashboard Data | company/dashboards/repos/ | cortex/visualization/dashboards/data/ |

├── README.md                     # This file

│## Why Migration?

├── assets/                       # SHARED assets (single source)

│   ├── css/- **Architectural Alignment:** Dashboard visualization now belongs in `cortex/visualization/` module

│   │   ├── variables.css         # Design tokens- **Clean Slate:** Removed SQLite dependencies for JSON-first approach

│   │   ├── base.css              # Base styles- **Future Extensibility:** New adapter pattern (JSON → SQLite → PostgreSQL) organized under `cortex/visualization/adapters/`

│   │   ├── components.css        # Reusable components

│   │   ├── layout.css            # Layout utilities## References

│   │   └── tabs.css              # Tab navigation

│   ├── js/                       # Shared JavaScript- Phase 21 Spec: `_workspaces/cortex-plan/PHASE-21-JSON-FIRST-REWRITE.yaml`

│   ├── images/- Implementation: `cortex/visualization/dashboards/`

│   │   └── cortex-logo-200.png   # Shared logo- Data Layer: `cortex/visualization/adapters/`

│   └── vendor/

│       ├── fuse.min.js           # Search library---

│       └── gridjs.min.css        # Grid styles

│Last Updated: 2026-02-04

└── repos/                        # Per-repo dashboards
    ├── _template/                # Template for new repos
    │   ├── index.html            # Dashboard template
    │   └── data.json             # Data schema template
    │
    ├── cortex/                   # ← CORTEX (single unified dashboard)
    │   ├── index.html            # Full dashboard with ALL tabs
    │   └── data.json             # ALL data embedded
    │
    ├── ksessions/                # ← KSESSIONS repo
    │   ├── index.html
    │   └── data.json
    │
    └── kashkole/                 # ← Kashkole repo
        ├── index.html
        └── data.json
```

---

## 🔗 URL Structure

| Page | Path | Notes |
|------|------|-------|
| Landing | `index.html` | Entry point with repo tiles |
| CORTEX Dashboard | `repos/cortex/index.html` | Full CORTEX dashboard |
| KSESSIONS Dashboard | `repos/ksessions/index.html` | Session management |
| Kashkole Dashboard | `repos/kashkole/index.html` | Testing framework |

**Asset Reference (from repo dashboard):**
```html
<link rel="stylesheet" href="../../assets/css/variables.css">
```

---

## 🛠️ MCP Tools

| Tool | Purpose |
|------|---------|
| `cortex_generate_dashboard_suite` | Generate complete suite |
| `cortex_generate_repo_dashboard` | Generate single repo dashboard |
| `cortex_generate_landing_page` | Generate landing page |
| `cortex_dashboard_create_repo` | Create new repo folder |
| `cortex_dashboard_update_repo` | Update existing repo data |
| `cortex_dashboard_list_repos` | List all registered repos |

---

## 📊 Adding a New Repository

1. Copy `repos/_template/` to `repos/<new-slug>/`
2. Update `data.json` with repo-specific data
3. Add entry to `registry.json`
4. Dashboard auto-appears on landing page

---

## 🎯 Design Principles

1. **Single Asset Source:** All repos share `assets/` (no duplication)
2. **Per-Repo Isolation:** Each repo in its own folder
3. **Offline-First:** Works with `file://` protocol
4. **MCP-First:** All operations via MCP tools
5. **Scalable:** Designed for 100+ repositories

---

**Last Updated:** 2026-02-04  
**Authority:** CORE-035 (Single Canonical Implementation)
