# CORTEX L2 VIEWS NAVIGATION MAP
**Version:** 1.0 | **Generated:** 2026-01-31  
**Approach:** Option C (Hybrid) | **Total:** 16 L2 Views

---

## 📖 Quick Navigation

### 🚀 Core Views (4)
| # | View | Path | Status |
|---|------|------|--------|
| 01 | Getting Started | `docs/getting-started/index.html` | PENDING |
| 02 | LENS Protocol | `docs/lens/index.html` | PENDING |
| 03 | MCP Tools | `docs/11-mcp-tools/index.html` | PENDING |
| 04 | Architecture | `docs/architecture/index.html` | ✅ REFERENCE |

---

### 🎯 Main Features (6)
| # | View | Path | Status |
|---|------|------|--------|
| 04 | Security (Overview) | `docs/security/index.html` | PENDING |
| 05 | Token Optimization | `docs/token-optimization/index.html` | ✅ COMPLETE |
| 06 | Toolkit Manager | `docs/toolkit-manager/index.html` | ✅ COMPLETE |
| 07 | Knowledge Base | `docs/knowledge/index.html` | ✅ COMPLETE |
| 08 | Sharpen The Saw | `docs/sts/index.html` | ✅ COMPLETE |
| 09 | Learning Paths | `docs/learning-paths/index.html` | ✅ COMPLETE |
| 10 | Story Viewer | `docs/story/viewer.html` | ✅ COMPLETE |

---

### 🛡️ Security Trilogy (3 Sub-Views)
| # | View | Path | Status | Focus |
|---|------|------|--------|-------|
| 11 | Security: Protection | `docs/security/protection/index.html` | ✅ COMPLETE | RBAC, Validation, Secrets, Audit |
| 12 | Security: Assessment | `docs/security/assessment/index.html` | ✅ COMPLETE | STRIDE, CWE, AST |
| 13 | Security: Compliance | `docs/security/compliance/index.html` | ✅ COMPLETE | OWASP, YAMLs, Secure Coding |

---

### 🎼 Orchestrators Trilogy (3 Sub-Views)
| # | View | Path | Status | Count | Focus |
|---|------|------|--------|-------|-------|
| 14 | Orchestrators: Core | `docs/orchestrators/core/index.html` | ✅ COMPLETE | 7 | Foundation orchestrators |
| 15 | Orchestrators: Domain | `docs/orchestrators/domain/index.html` | ✅ COMPLETE | 6 | Specialized orchestrators |
| 16 | Orchestrators: Support | `docs/orchestrators/support/index.html` | ✅ COMPLETE | 11 | Infrastructure orchestrators |

**Total Orchestrators:** 24 (verified against `wiring.yaml`)

---

## 🗺️ Information Architecture

```
CORTEX GitPages
│
├── 🚀 Getting Started
├── 🔍 LENS Protocol
├── 🔌 MCP Tools
│
├── 🛡️ Security (Overview) ◄─┐
│   ├── 🔒 Protection       │ Security Trilogy
│   ├── 🔍 Assessment       │ (3 sub-views)
│   └── ✅ Compliance       ◄─┘
│
├── 💰 Token Optimization
├── 🛠️ Toolkit Manager
├── 📚 Knowledge Base
├── 🔧 Sharpen The Saw
├── 🎓 Learning Paths
├── 📖 Story Viewer
│
└── 🎼 Orchestrators (Overview) ◄─┐
    ├── 🧠 Core (7)                │ Orchestrators Trilogy
    ├── 🎯 Domain (6)              │ (3 sub-views)
    └── 🛠️ Support (11)            ◄─┘
```

---

## 📊 Effort Summary

| Category | Views | Hours | Status |
|----------|-------|-------|--------|
| **Existing** | 4 | 60h | PENDING (01-04) |
| **Main Features** | 6 | 109h | ✅ COMPLETE (05-10) |
| **Security Trilogy** | 3 | 48h | ✅ COMPLETE (11-13) |
| **Orchestrators Trilogy** | 3 | 66h | ✅ COMPLETE (14-16) |
| **TOTAL** | **16** | **283h** | **12/16 Complete** |

---

## 🎨 Visualization Inventory

### D3.js Charts (36 Total)
- **Force Graphs:** 9 (dependencies, networks, emergence)
- **Sankey Diagrams:** 7 (flows, pipelines, routing)
- **Timelines:** 6 (events, journeys, lifecycle)
- **Radars:** 5 (capabilities, skills, coverage)
- **Trees:** 3 (hierarchies, RBAC, skills)
- **Sunbursts:** 3 (standards, brain tiers, compliance)
- **Matrices:** 2 (heatmaps, capabilities, threats)

### Mermaid Diagrams (36+ Total)
- **Mindmaps:** 12 (concept hierarchies)
- **Flowcharts:** 12 (process flows, decisions)
- **Sequence Diagrams:** 8 (interactions, workflows)
- **Journey Diagrams:** 4 (user paths, progression)

---

## 🎯 Audience Mapping

### Business Leaders
**Primary:** 05 (Token Optimization), 04 (Security)  
**Secondary:** All views (executive summaries)

### Product Owners
**Primary:** 01 (Getting Started), 10 (Story Viewer)  
**Secondary:** 06 (Toolkit), 09 (Learning Paths)

### Software Engineers
**Primary:** 02 (LENS), 03 (MCP Tools), 14-16 (Orchestrators)  
**Secondary:** All technical views

### Security Engineers
**Primary:** 11-13 (Security trilogy)  
**Secondary:** 07 (Knowledge Base - OWASP YAMLs)

### System Architects
**Primary:** 14-16 (Orchestrators trilogy)  
**Secondary:** 02 (LENS), 07 (Knowledge)

### DevOps Engineers
**Primary:** 06 (Toolkit), 03 (MCP Tools)  
**Secondary:** 16 (Support Orchestrators)

### L&D Teams
**Primary:** 08 (STS), 09 (Learning Paths)  
**Secondary:** 07 (Knowledge), 10 (Story)

---

## 🚀 Next Phase: HTML Generation

### Phase 1: Asset Preparation (12h)
- [ ] Generate 36+ D3.js JSON data files
- [ ] Create 36+ Mermaid .mmd source files
- [ ] Copy CORTEX logo to 12 section folders
- [ ] Prepare SVG diagrams

### Phase 2: HTML Generation (96h)
- [ ] Convert 12 YAMLs to HTML via CortexDocsOrchestrator
- [ ] Inject D3.js visualizations with data
- [ ] Render Mermaid diagrams
- [ ] Apply glassmorphism theme
- [ ] Validate responsive behavior

### Phase 3: Validation (8h)
- [ ] Cross-browser testing
- [ ] Mobile responsiveness
- [ ] Performance optimization
- [ ] Accessibility audit (WCAG AA)
- [ ] Link validation

**Total Remaining:** ~116 hours

---

## 📝 File References

### Planning Files
```
_workspaces/docker-plan/gitpages/L2/
├── 00-L2-VIEWS-INDEX.yaml (UPDATED - master index)
├── 00-GENERATION-COMPLETE.md (UPDATED - 16 views)
├── 00-OPTION-C-COMPLETE.md (NEW - hybrid summary)
├── 00-NAVIGATION-MAP.md (THIS FILE)
├── 05-token-optimization.yaml ✅
├── 06-toolkit-manager.yaml ✅
├── 07-knowledge.yaml ✅
├── 08-sts.yaml ✅
├── 09-learning-paths.yaml ✅
├── 10-story-viewer.yaml ✅
├── 11-security-protection.yaml ✅
├── 12-security-assessment.yaml ✅
├── 13-security-compliance.yaml ✅
├── 14-orchestrators-core.yaml ✅
├── 15-orchestrators-domain.yaml ✅
└── 16-orchestrators-support.yaml ✅
```

### Output Structure
```
docs/
├── getting-started/index.html
├── lens/index.html
├── 11-mcp-tools/index.html
├── architecture/index.html (reference)
├── security/
│   ├── index.html (overview)
│   ├── protection/index.html
│   ├── assessment/index.html
│   └── compliance/index.html
├── token-optimization/index.html
├── toolkit-manager/index.html
├── knowledge/index.html
├── sts/index.html
├── learning-paths/index.html
├── story/viewer.html
└── orchestrators/
    ├── index.html (overview - TBD)
    ├── core/index.html
    ├── domain/index.html
    └── support/index.html
```

---

## ✅ Verification Checklist

Planning Phase:
- [x] 16 YAML plans created
- [x] Security trilogy complete (3 views)
- [x] Orchestrators trilogy complete (3 views)
- [x] Master index updated
- [x] Navigation map created
- [x] Effort estimates calculated
- [x] Visualization inventory documented
- [x] Audience mapping complete

Ready for Execution:
- [ ] CortexDocsOrchestrator advisory mode ready
- [ ] Asset generation scripts prepared
- [ ] HTML templates validated
- [ ] D3.js/Mermaid libraries tested
- [ ] Deployment pipeline configured

---

*Navigation map for CORTEX L2 views — Option C hybrid approach complete.*
