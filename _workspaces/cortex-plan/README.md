# CORTEX cortex-plan

**Purpose:** Live planning and specification repository for CORTEX development phases  
**Updated:** 2026-02-02  
**Status:** 🎉 PRODUCTION READY + ACTIVE DEVELOPMENT

---

## 🎯 Quick Start

**Current Focus:** Phase 18 (Enterprise Dashboard) + Phase 19 (LENS Unified Intelligence)

| Document | Purpose |
|----------|---------|
| **[LIVE-STATUS.md](./LIVE-STATUS.md)** | Current implementation state + next actions |
| **[PHASE-19-QUICK-REFERENCE.md](./PHASE-19-QUICK-REFERENCE.md)** | Next phase implementation guide |
| **[cortex-plan-index.md](./cortex-plan-index.md)** | Master index of all phases |

---

## 📁 Folder Structure

```
cortex-plan/
├── LIVE-STATUS.md                          ⭐ Current state
├── cortex-plan-index.md                    📋 Master index
├── PHASE-19-LENS-UNIFIED-INTELLIGENCE.yaml 📋 Next phase (PLANNED)
├── PHASE-19-QUICK-REFERENCE.md             📖 Quick guide
├── PHASE-18-ENTERPRISE-DASHBOARD-SYSTEM.yaml 🚧 Active work
├── PHASE-15-STATIC-REPO-VISUALIZATION.yaml ✅ Complete
├── PHASE-10-LENS-REMOTE-INTELLIGENCE.yaml  ✅ Complete
├── wiring-schema.yaml                       🔧 Orchestrator specs
├── deployment-guide.md                      🚀 Production guide
├── observability-runbook.md                 📊 Operations
└── .archive/                                🗄️ Historical content
```

---

## 🎯 Active Phases

### Phase 18: Enterprise Dashboard System (IN PROGRESS)
- **Status:** 🚧 Hardcoded dashboard complete, enhancements planned
- **Location:** `company/dashboards/kashkole/dashboard.html`
- **Next:** Add Domain, Database, Vendors, Patterns tabs
- **Spec:** [PHASE-18-ENTERPRISE-DASHBOARD-SYSTEM.yaml](./PHASE-18-ENTERPRISE-DASHBOARD-SYSTEM.yaml)

### Phase 19: LENS Unified Intelligence (PLANNED)
- **Status:** 📋 Specification complete, ready for implementation
- **Duration:** 4 weeks (160+ tests, 6 major components)
- **Critical:** Fixes snowball effect, adds vendor detection, database crawling
- **Spec:** [PHASE-19-LENS-UNIFIED-INTELLIGENCE.yaml](./PHASE-19-LENS-UNIFIED-INTELLIGENCE.yaml)
- **Quick Ref:** [PHASE-19-QUICK-REFERENCE.md](./PHASE-19-QUICK-REFERENCE.md)

---

## ✅ Completed Phases (Archived)

All phases 0-15 are **COMPLETE** and operational in production:
- **Phases 0-6:** Core infrastructure, Docker migration, MCP server
- **Phases 7-9:** LENS formalization, discovery, governance
- **Phase 10:** Remote git repository analysis
- **Phase 15:** Static repository visualization system

Detailed execution reports moved to `.archive/` for historical reference.

---

## 🚀 Getting Started with Phase 19

### Prerequisites
- Read [PHASE-19-QUICK-REFERENCE.md](./PHASE-19-QUICK-REFERENCE.md)
- Review chat02.txt (_workspaces/.chats/chat02.txt) for architectural decisions
- Understand Phase 18 dashboard requirements

### Implementation Order
1. **Week 1:** DomainKnowledgeMerger + VendorDetector (P0-A)
2. **Week 2:** DatabaseCrawlerPlugin + SQL Server/PostgreSQL (P0-B)
3. **Week 3:** PatternDiscoveryOrchestrator + External Research (P1)
4. **Week 4:** MCP exposure + Integration + Documentation (P1)

---

## 📖 Key Documents

### Specifications (YAML)
- `PHASE-19-LENS-UNIFIED-INTELLIGENCE.yaml` - Full Phase 19 spec
- `PHASE-18-ENTERPRISE-DASHBOARD-SYSTEM.yaml` - Dashboard architecture
- `PHASE-15-STATIC-REPO-VISUALIZATION.yaml` - Visualization foundation

### Guides (Markdown)
- `LIVE-STATUS.md` - Current implementation status
- `PHASE-19-QUICK-REFERENCE.md` - Phase 19 guide
- `deployment-guide.md` - Production deployment
- `observability-runbook.md` - Operations

---

## 📊 Metrics

| Metric | Value |
|--------|-------|
| **Total Phases** | 19 |
| **Phases Complete** | 0-15 ✅ |
| **In Progress** | 18 🚧 |
| **Planned** | 19 📋 |
| **Archived Docs** | 40+ |

---

**Last Updated:** 2026-02-02 - Comprehensive cleanup, Phase 19 specification complete
