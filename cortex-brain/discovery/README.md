# CORTEX Discovery System

**Purpose:** Auto-generated living documentation system  
**Version:** 1.0  
**Status:** In Development  
**Last Updated:** Auto-generated on every discovery run

---

## 🎯 What is This?

The **Discovery System** is CORTEX's self-awareness engine. It automatically:

1. **Discovers** all CORTEX operations, orchestrators, agents, and utilities
2. **Analyzes** capabilities, integration points, and dependencies
3. **Generates** documentation for multiple audiences (leadership, engineers, product)
4. **Updates** response templates, deployment manifests, and feature catalogs
5. **Validates** that documentation stays in sync with code

**Key Principle:** Documentation is code-generated, not hand-written. This folder contains **living documents** that auto-update when CORTEX changes.

---

## 📂 Folder Structure

```
discovery/
├── README.md                       # This file
├── features/                       # 🎯 Living feature documentation
│   ├── FEATURE-CATALOG.md          # Complete CORTEX feature list (MAIN DOC)
│   ├── FEATURE-MATRIX.md           # Feature comparison matrix
│   ├── CHANGELOG.md                # Auto-generated from git
│   └── audiences/
│       ├── leadership-view.md      # Executive summary (business value)
│       ├── engineering-view.md     # Technical deep-dive (APIs, architecture)
│       └── product-view.md         # Product features & use cases
├── operations/                     # Operation discovery results
│   ├── operations-catalog.json     # Raw discovery data
│   ├── operations-summary.md       # Human-readable summary
│   └── operation-tree.txt          # Hierarchical view
├── orchestrators/                  # Orchestrator analysis
│   ├── orchestrator-map.json       # All orchestrators with metadata
│   ├── integration-graph.dot       # Integration visualization
│   └── capability-matrix.md        # Orchestrator capabilities
├── utilities/                      # Utility module discovery
│   ├── utility-catalog.json        # All utilities with functions
│   └── utility-summary.md          # Grouped by category
├── templates/                      # Template analysis
│   ├── template-coverage.json      # Operations → Templates mapping
│   └── missing-templates.md        # Templates to create
├── deployment/                     # Deployment readiness
│   ├── production-features.json    # Features passing gates
│   ├── feature-gates.md            # Gate validation results
│   └── deployment-report.md        # Ready-to-deploy summary
└── reports/                        # Discovery run reports
    └── {timestamp}-discovery-report.md
```

---

## 🚀 Quick Start

### For Stakeholders (Non-Technical)

**Want to see what CORTEX can do?**

👉 Start here: **[features/FEATURE-CATALOG.md](./features/FEATURE-CATALOG.md)**

This document lists every CORTEX capability in plain English with examples.

**Choose your view:**
- **Leadership:** [audiences/leadership-view.md](./features/audiences/leadership-view.md) - Business value, ROI, strategic fit
- **Product:** [audiences/product-view.md](./features/audiences/product-view.md) - Features, use cases, user stories
- **Engineering:** [audiences/engineering-view.md](./features/audiences/engineering-view.md) - APIs, architecture, integration

### For Developers

**Want to understand CORTEX internals?**

1. **Operations:** `operations/operations-summary.md` - All commands and triggers
2. **Orchestrators:** `orchestrators/capability-matrix.md` - Workflow engines
3. **Utilities:** `utilities/utility-summary.md` - Reusable modules
4. **Deployment:** `deployment/deployment-report.md` - Production readiness

### For Administrators

**Want to run discovery?**

```bash
# Manual discovery run
python -m src.operations.modules.orchestration.discovery_orchestrator

# Full discovery with updates
cortex discover --update-all

# Deployment validation
cortex discover --deployment-check
```

---

## 📊 What Gets Discovered?

### Operations (from `cortex-operations.yaml`)

- Operation names and descriptions
- Execution methods (cli_wrapper, copilot_chat, internal)
- Natural language triggers
- Module mappings
- Implementation status
- Examples

**Output:** `operations/operations-catalog.json`

### Orchestrators (from `src/operations/modules/orchestration/`)

- Orchestrator classes and purposes
- Phase structures
- Integration points
- Capabilities
- Metrics

**Output:** `orchestrators/orchestrator-map.json`

### Agents (from `src/cortex_agents/`)

- Agent types (LEFT_BRAIN, RIGHT_BRAIN)
- Purposes and capabilities
- Integration patterns

**Output:** `orchestrators/orchestrator-map.json` (agents section)

### Utilities (from `src/operations/modules/`)

- Utility modules and functions
- Capability summaries
- Category groupings

**Output:** `utilities/utility-catalog.json`

### Templates (from `cortex-brain/response-templates-v4.yaml`)

- Template names and intents
- Operations → Templates mapping
- Missing templates

**Output:** `templates/template-coverage.json`

### Deployment Features (from codebase scan)

- Production-ready modules
- Feature gate status (tests, docs, coverage)
- Deployment readiness

**Output:** `deployment/production-features.json`

---

## 🔄 Auto-Update Triggers

Discovery runs automatically on:

1. **Git Commits** - When orchestrators/operations change (opt-in via hook)
2. **CI/CD Pipeline** - On every pull request
3. **Daily Schedule** - Catch drift over time
4. **Manual Trigger** - `cortex discover`
5. **Pre-Deployment** - Validate before deploying

Each run:
- Updates feature catalog
- Syncs response templates
- Updates deployment manifest
- Generates change report
- Validates no drift

---

## 📋 Document Types

### Living Documents (Auto-Generated)

These files are **100% code-generated** and update automatically:

- ✅ `features/FEATURE-CATALOG.md`
- ✅ `features/CHANGELOG.md`
- ✅ `features/audiences/*.md`
- ✅ `operations/operations-catalog.json`
- ✅ `orchestrators/orchestrator-map.json`
- ✅ `utilities/utility-catalog.json`
- ✅ `templates/template-coverage.json`
- ✅ `deployment/production-features.json`

**DO NOT EDIT** - Changes will be overwritten on next discovery run.

### Reports (Timestamped Snapshots)

Discovery runs generate timestamped reports:

- `reports/2024-12-16-0830-discovery-report.md`
- `reports/2024-12-16-1545-discovery-report.md`

These are **historical records** and never modified.

---

## 🎯 Audience-Specific Views

### Leadership View

**Purpose:** Show business value, ROI, strategic alignment

**Contains:**
- Executive summary (what CORTEX does)
- Key capabilities (business language)
- Success metrics (productivity gains, cost savings)
- Strategic fit (how it supports business goals)
- ROI analysis

**Target Audience:** C-suite, VPs, Directors

**File:** `features/audiences/leadership-view.md`

### Engineering View

**Purpose:** Technical deep-dive for developers

**Contains:**
- Architecture overview
- API documentation
- Integration points
- Code examples
- Performance metrics
- Security considerations

**Target Audience:** Software engineers, architects, DevOps

**File:** `features/audiences/engineering-view.md`

### Product View

**Purpose:** Features and use cases for product managers

**Contains:**
- Feature list with descriptions
- Use cases and scenarios
- User stories
- Competitive advantages
- Roadmap

**Target Audience:** Product managers, UX designers, analysts

**File:** `features/audiences/product-view.md`

---

## ✅ Validation & Quality

Every discovery run validates:

- [ ] **Template Coverage** - Every operation has response template
- [ ] **Manifest Accuracy** - Deployment manifest matches codebase
- [ ] **Documentation Sync** - Docs reflect current code
- [ ] **Feature Gates** - Production features pass quality gates
- [ ] **Link Integrity** - No broken links in generated docs
- [ ] **Readability** - Passes Flesch-Kincaid reading level

Validation failures block deployment.

---

## 🚨 Important Notes

### Do NOT Manually Edit

**These files are code-generated:**
- `features/FEATURE-CATALOG.md`
- `features/CHANGELOG.md`
- All `.json` files in subfolders

Manual edits will be **overwritten** on next discovery run.

### Preserve Manual Edits

If you need to add content to auto-generated files, use comment markers:

```markdown
<!-- MANUAL_EDIT_START -->
This content is preserved across discovery runs.
<!-- MANUAL_EDIT_END -->
```

The discovery system will preserve content between these markers.

### Git Ignoring

Large auto-generated JSON files are git-ignored by default:

```
cortex-brain/discovery/**/*.json
cortex-brain/discovery/reports/*
```

Only human-readable Markdown files are committed.

---

## 📚 Related Documentation

- **Discovery Orchestrator Plan:** `cortex-brain/documents/planning/temp-plans/discovery-orchestrator-v1/`
- **Phase 7 Details:** `phases/phase-7-cortex-self-discovery.md`
- **Operations YAML:** `cortex-operations.yaml`
- **Response Templates:** `cortex-brain/response-templates-v4.yaml`
- **Deployment Manifest:** `deployment-manifest.yaml`

---

## 🆘 Troubleshooting

### Discovery Run Fails

```bash
# Check discovery logs
tail -f logs/discovery-orchestrator.log

# Validate YAML files
cortex validate-config

# Run in debug mode
cortex discover --debug
```

### Documents Out of Sync

```bash
# Force full rediscovery
cortex discover --force --update-all

# Validate sync status
cortex discover --validate-only
```

### Missing Templates

```bash
# List missing templates
cortex discover --check-templates

# Generate missing templates
cortex discover --create-missing-templates
```

---

## 📈 Metrics

Discovery system tracks:

- **Discovery Runs:** Total runs, frequency
- **Operations Discovered:** Count, new additions
- **Template Coverage:** Percentage with templates
- **Manifest Accuracy:** Percentage up-to-date
- **Documentation Freshness:** Hours since last update
- **Drift Detected:** Mismatches found

View metrics: `cortex discover --stats`

---

## 🎉 Success Criteria

The discovery system is working well when:

- ✅ Feature catalog updated within 24 hours of code changes
- ✅ 100% template coverage (no missing templates)
- ✅ 100% manifest accuracy (no drift)
- ✅ All 3 audience views current
- ✅ Stakeholders rate docs 9/10 or higher
- ✅ Zero manual doc updates needed

---

**Questions?** Contact: Asif Hussain  
**Last Discovery Run:** Check `reports/` folder for latest timestamp
