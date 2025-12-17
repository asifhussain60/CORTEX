# 📑 CORTEX 4.0 - Planning Documents Index

**Version:** 1.0.0  
**Status:** 📋 READY FOR REVIEW  
**Last Updated:** December 17, 2025

---

## 🎯 Quick Navigation

### Master Documents

| Document | Purpose | Status |
|----------|---------|--------|
| **[CORTEX-4.0-MASTER-PLAN.md](./orchestrator-migrations/CORTEX-4.0-MASTER-PLAN.md)** | Complete migration & enhancement plan (Orchestrator Migrations) | ✅ Ready |
| **[DEPLOYMENT-STRATEGY.md](./DEPLOYMENT-STRATEGY.md)** | PyPI, Docker, VS Code, GitHub Action | ✅ Ready |
| **[CORTEX-4.0-ARCHITECTURE-DESIGN.md](./CORTEX-4.0-ARCHITECTURE-DESIGN.md)** | Original architecture doc | ✅ Existing |

### Phase Plans (Incremental)

| Phase | Document | Duration | Status |
|-------|----------|----------|--------|
| **Phase 0** | **[phases/phase-0-foundation.md](./phases/phase-0-foundation.md)** | Week 1-2 | ✅ Ready |
| **Phase 1** | **[phases/phase-1-core-orchestrators.md](./phases/phase-1-core-orchestrators.md)** | Week 3-6 | ✅ Ready |
| Phase 2 | phases/phase-2-enhancement-orchestrators.md | Week 7-9 | ⏳ Pending |
| Phase 3 | phases/phase-3-utility-orchestrators.md | Week 10-11 | ⏳ Pending |
| Phase 4 | phases/phase-4-finalization.md | Week 12 | ⏳ Pending |

### Orchestrator Migration Plans (Detailed)

| Orchestrator | Document | Duration | Status |
|--------------|----------|----------|--------|
| **Planning** | **[orchestrator-migrations/02-planning-orchestrator-migration.md](./orchestrator-migrations/02-planning-orchestrator-migration.md)** | 5 days | ✅ Ready |
| **ADO** | **[orchestrator-migrations/03-ado-orchestrator-migration.md](./orchestrator-migrations/03-ado-orchestrator-migration.md)** | 3 days | ✅ Ready |
| **Maintenance** | **[orchestrator-migrations/04-maintenance-orchestrator-migration.md](./orchestrator-migrations/04-maintenance-orchestrator-migration.md)** | 3 days | ✅ Ready |
| TDD | orchestrator-migrations/01-tdd-orchestrator-migration.md | 5 days | ⏳ Pending |
| Sanitization | orchestrator-migrations/05-sanitization-orchestrator-migration.md | 3 days | ⏳ Pending |
| Review | orchestrator-migrations/06-review-orchestrator-migration.md | 3 days | ⏳ Pending |
| Refinement | orchestrator-migrations/07-refinement-orchestrator-migration.md | 2 days | ⏳ Pending |
| Upgrade | orchestrator-migrations/08-upgrade-orchestrator-migration.md | 2 days | ⏳ Pending |

---

## 📖 Document Summaries

### 1. CORTEX-4.0-MASTER-PLAN.md

**The Complete Blueprint**

**Contents:**
- Executive summary & vision
- Version strategy (3.x → 4.0 → 5.0)
- Architecture enhancements
  - MCP-first design
  - Team brain features
  - LLM intent router
  - Sustainable orchestrator framework
- Complete folder structure
- 12-week migration timeline
- Orchestrator consolidation strategy
- Testing strategy (100% coverage)
- Success metrics

### 2. Orchestrator Migration Plans

**Detailed Per-Orchestrator Blueprints**

#### Planning Orchestrator (5 days)
- **Consolidates:** Planning + Incremental + Skeleton (3 systems → 1)
- **Strategy:** Auto-complexity routing (LOW/MEDIUM/HIGH)
- **Target:** 800 LOC, 55 tests, 3 strategies
- **Key Features:** DoR/DoD validation, phase decomposition, MCP tools

#### ADO Orchestrator (3 days)
- **Consolidates:** Story + Feature + Task generators (3 → 1)
- **Strategy:** Extends PlanningOrchestrator with ADO formatting
- **Target:** 600 LOC, 55 tests, 3 work item types
- **Key Features:** Azure DevOps templates, completion summaries, REST API integration

#### Maintenance Orchestrator (3 days)
- **Consolidates:** Healthcheck + Align + Cleanup + Optimize + Vacuum + Refresh (7 → 1)
- **Strategy:** 7-phase autonomous workflow
- **Target:** 800 LOC, 40 tests, 7 phases
- **Key Features:** Health tracking, space recovery, autonomous execution

**Key Decisions:**
- CORTEX 4.0 = Clean rebuild (not incremental on 3.0)
- CORTEX 5.0 = Future advanced features (was 4.0)
- MCP server for all operations
- LLM replaces keyword matching
- Team-level brain sharing
- No more orchestrator rewiring

**Who Should Read:** Everyone involved in CORTEX 4.0

---

### 2. phases/phase-0-foundation.md

**Week 1-2: Infrastructure Setup**

**Contents:**
- Branch setup (`CORTEX-4.0`)
- Brain engine implementation (unified 4-tier API)
- Event bus & service container (dependency injection)
- MCP server scaffolding
- LLM intent router (local model)
- Testing infrastructure (pytest, CI/CD)
- Deployment scaffolding (setup.py, Dockerfile)

**Deliverables:**
- 2000 LOC
- 100% test coverage
- CI/CD pipeline green
- All foundation services operational

**Validation:**
- Brain engine working (all 4 tiers)
- Event bus functional (pub/sub)
- MCP server starts
- LLM classifies intents
- CI pipeline passes

**Who Should Read:** Infrastructure developers, Phase 0 implementers

---

### 3. phases/phase-1-core-orchestrators.md

**Week 3-6: Critical Orchestrators**

**Contents:**

**Week 3: TDD Orchestrator**
- Analysis & planning (Day 1)
- Core logic migration (Day 2-3)
- Utility extraction (Day 3)
- Testing (Day 4-5: unit, integration, E2E)
- MCP integration (Day 5)

**Week 4: Planning Orchestrator**
- Consolidation (Planning System 2.0)
- Port to 4.0 architecture
- Extract AST utilities
- Write comprehensive tests
- Validate DoR/DoD compliance

**Week 5: ADO Orchestrator**
- Port to 4.0
- Inherit Planning System 2.0
- ADO-specific formatting
- Story/Feature/Task generation

**Week 6: Maintenance Orchestrator**
- Consolidate 7-phase workflow
- Port phase modules
- Tiered routing (Planning System 3.0)
- Success template integration

**Deliverables:**
- 4 orchestrators (2500 LOC)
- 57 tests (100% coverage)
- 15 MCP tools
- Brain integration validated

**Who Should Read:** Orchestrator developers, Week 3-6 implementers

---

### 4. DEPLOYMENT-STRATEGY.md

**PyPI, Docker, VS Code, GitHub Action**

**Contents:**

**1. PyPI Package**
- setup.py configuration
- pyproject.toml (modern packaging)
- MANIFEST.in (include files)
- CLI entry points
- Publishing workflow
- Automated CI/CD

**2. Docker Distribution**
- Multi-stage Dockerfile
- docker-compose.yml
- Volume management
- Health checks
- Docker Hub publishing

**3. VS Code Extension**
- package.json configuration
- MCP integration
- Commands & settings
- Marketplace publishing

**4. GitHub Action**
- action.yml definition
- Workflow examples
- Marketplace publishing

**Validation Checklist:**
- Installation time < 2 minutes
- Zero manual configuration
- Cross-platform support
- Offline capability

**Who Should Read:** DevOps, deployment engineers, release managers

---

### 5. CORTEX-4.0-ARCHITECTURE-DESIGN.md

**Original Architecture Document (Existing)**

**Contents:**
- MCP server architecture
- Folder structure (original)
- Migration phases (original plan)
- Testing strategy
- Deployment artifacts

**Note:** This is the original planning document. The **MASTER-PLAN.md** supersedes this with enhanced features (team brain, LLM intent, etc.)

**Who Should Read:** Reference only, superseded by MASTER-PLAN.md

---

## 🔄 Document Relationships

```
CORTEX-4.0-MASTER-PLAN.md
├── Phase 0: phase-0-foundation.md
│   ├── Brain engine
│   ├── Event bus
│   ├── MCP server
│   └── LLM intent router
├── Phase 1: phase-1-core-orchestrators.md
│   ├── Week 3: TDD
│   ├── Week 4: Planning
│   ├── Week 5: ADO
│   └── Week 6: Maintenance
├── Phase 2: phase-2-enhancement-orchestrators.md (TODO)
│   ├── Week 7: Sanitization
│   ├── Week 8: Review
│   └── Week 9: Refinement
├── Phase 3: phase-3-utility-orchestrators.md (TODO)
│   └── Week 10-11: Remaining orchestrators
└── Phase 4: phase-4-finalization.md (TODO)
    └── Week 12: Documentation, deployment, archive

DEPLOYMENT-STRATEGY.md
├── PyPI (pip install cortex-ai)
├── Docker (docker run cortex-ai:4.0)
├── VS Code Extension (marketplace)
└── GitHub Action (workflow automation)
```

---

## 📋 Review Checklist

### For User/Stakeholder

**Before starting Phase 0, review and approve:**

- [ ] **MASTER-PLAN.md** - Complete vision and strategy
  - [ ] Version renaming (4.0 vs 5.0)
  - [ ] MCP-first approach
  - [ ] Team brain features
  - [ ] LLM intent router
  - [ ] 12-week timeline
  - [ ] 100% coverage requirement
  
- [ ] **DEPLOYMENT-STRATEGY.md** - Distribution approach
  - [ ] PyPI packaging
  - [ ] Docker containerization
  - [ ] VS Code extension
  - [ ] GitHub Action

- [ ] **phase-0-foundation.md** - First 2 weeks
  - [ ] Infrastructure setup
  - [ ] Foundation services
  - [ ] Testing infrastructure

### Key Questions to Answer

1. **Version Strategy:** Comfortable renaming 4.0 → 5.0, and 4.0 = clean rebuild?
2. **MCP Architecture:** Agree with MCP server approach vs custom CLI?
3. **Team Brain:** Want team-level knowledge sharing features?
4. **LLM Intent:** Replace keyword matching with LLM classification?
5. **Timeline:** 12-14 weeks acceptable for complete migration?
6. **Testing:** Strict 100% coverage requirement acceptable?
7. **Deployment:** PyPI + Docker + VS Code + GitHub Action all needed?

---

## 🎯 Next Steps After Approval

### Immediate (Week 0)

1. **Create CORTEX-4.0 branch**
   ```bash
   git checkout main
   git pull
   git checkout -b CORTEX-4.0
   git push -u origin CORTEX-4.0
   ```

2. **Initialize directory structure**
   - Create all folders from master plan
   - Add .gitignore
   - Create README.md for 4.0

3. **Set up CI/CD**
   - Configure GitHub Actions
   - Set up codecov
   - Add branch protection

### Week 1-2 (Phase 0)

Execute **phase-0-foundation.md**:
- Brain engine
- Event bus & service container
- MCP server
- LLM intent router
- Testing infrastructure
- Deployment scaffolding

**Validation:** All foundation services operational, CI green, 100% coverage

### Week 3+ (Phase 1)

Execute **phase-1-core-orchestrators.md**:
- Week 3: TDD Orchestrator
- Week 4: Planning Orchestrator
- Week 5: ADO Orchestrator
- Week 6: Maintenance Orchestrator

---

## 📞 Questions & Feedback

**Before proceeding, please review:**

1. **CORTEX-4.0-MASTER-PLAN.md** - The complete vision
2. **phases/phase-0-foundation.md** - First 2 weeks of work
3. **DEPLOYMENT-STRATEGY.md** - How users will install CORTEX 4.0

**Provide feedback on:**
- Architecture decisions (MCP, team brain, LLM intent)
- Timeline (12-14 weeks realistic?)
- Deployment targets (PyPI, Docker, VS Code, GitHub Action)
- Testing requirements (100% coverage)
- Resource allocation

---

## 📊 Document Statistics

**Total Documents:** 5 (2 complete, 3 pending)  
**Total Pages:** ~150 pages  
**Total LOC (Planned):** ~10,000 LOC  
**Total Tests (Planned):** ~200 tests  
**Timeline:** 12-14 weeks  
**Orchestrators:** 12 (consolidated from 16)

---

## 🔗 Related Resources

**External:**
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io/)
- [Python Packaging Guide](https://packaging.python.org/)
- [VS Code Extension API](https://code.visualstudio.com/api)
- [GitHub Actions](https://docs.github.com/en/actions)

**Internal:**
- `cortex-brain/documents/planning/PLANNING-SYSTEM-3.0-GAP-REMEDIATION-MASTER-PLAN.md`
- `cortex-brain/documents/planning/UNIFIED-PLANNING-GAP-ANALYSIS-IMPLEMENTATION-PLAN.md`
- `cortex-brain/brain-protection-rules.yaml` (SKULL rules)
- `cortex-operations.yaml` (Current operations)

---

**Ready to begin? Review documents and provide approval to start Phase 0.**

**Author:** Asif Hussain  
**GitHub:** https://github.com/asifhussain60/CORTEX  
**Date:** December 17, 2025

