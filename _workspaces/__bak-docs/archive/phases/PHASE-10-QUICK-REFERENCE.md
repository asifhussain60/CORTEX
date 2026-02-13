# Phase 10: LENS Remote Intelligence - Quick Reference

**Created:** 2026-01-27  
**Status:** PLANNED  
**Priority:** P2 Medium  
**Estimated Effort:** 5-7 days  
**Full Spec:** [PHASE-10-LENS-REMOTE-INTELLIGENCE.yaml](./PHASE-10-LENS-REMOTE-INTELLIGENCE.yaml)

---

## 🎯 Overview

**Problem:** Current LENS intelligence (`GitHistoryAnalyzer`, `ASTAnalyzer`, `CommentExtractor`) requires local git repository clones. Cannot analyze remote branches, PRs, or repositories without downloading entire codebase.

**Solution:** Extend LENS system with remote git capabilities using GitHub/GitLab APIs, enabling analysis without local clones.

---

## 🚀 Key Features

### 1. Remote Repository Analysis
```bash
# Analyze file from GitHub without cloning
cortex lens remote analyze https://github.com/user/repo main src/file.py

# Analyze from GitLab with authentication
GITLAB_TOKEN=xyz cortex lens remote analyze https://gitlab.com/user/repo develop file.py
```

### 2. Branch Comparison
```bash
# Compare same file across branches
cortex lens remote compare \
  https://github.com/user/repo main \
  https://github.com/user/repo feature/xyz \
  src/module.py
```

### 3. API Integration
- **GitHub API v3/v4** (GraphQL)
- **GitLab API v4**
- **Generic git protocol** (fallback)
- Authentication via environment variables
- Rate limiting and retry logic

### 4. Intelligent Caching
- File content cache (TTL: 1 hour)
- Commit history cache (TTL: 5 minutes)
- 80%+ cache hit rate target
- Size-limited disk cache (500MB default)
- Manual cache clearing: `cortex lens cache clear`

---

## 📋 Tasks (7 Total)

| ID | Task | Effort | Priority |
|----|------|--------|----------|
| **LENS-010** | Remote Git Adapter Design | 4h | HIGH |
| **LENS-011** | Enhance GitHistoryAnalyzer | 8h | HIGH |
| **LENS-012** | Remote Caching System | 6h | MEDIUM |
| **LENS-013** | LENSOrchestrator Integration | 5h | HIGH |
| **LENS-014** | CLI Commands | 4h | MEDIUM |
| **LENS-015** | Branch Comparison | 6h | LOW |
| **LENS-016** | Documentation | 3h | MEDIUM |

**Total:** 36 hours (~5-7 days)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│            LENSOrchestrator (Enhanced)              │
│  - analyze_remote_file()                            │
│  - analyze_remote_branch()                          │
└────────────────┬────────────────────────────────────┘
                 │
      ┌──────────┼──────────┐
      │          │          │
      ▼          ▼          ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│   Git    │ │   AST    │ │ Comment  │
│ History  │ │ Analyzer │ │Extractor │
│ Analyzer │ │          │ │          │
└────┬─────┘ └──────────┘ └──────────┘
     │
     ▼
┌─────────────────────────────────────┐
│    RemoteGitAdapter (NEW)           │
│  - Provider detection               │
│  - Auth management                  │
│  - Rate limiting                    │
└───┬─────────┬───────────┬───────────┘
    │         │           │
    ▼         ▼           ▼
┌────────┐ ┌────────┐ ┌────────┐
│ GitHub │ │ GitLab │ │Generic │
│Provider│ │Provider│ │  Git   │
└────────┘ └────────┘ └────────┘
```

---

## 🧪 Testing

**Unit Tests:** 60 new tests  
**Integration Tests:** 25 scenarios  
**Target Coverage:** 95%

### Critical Test Scenarios:
- ✅ Public GitHub repo analysis
- ✅ Private repo with token authentication
- ✅ GitLab API integration
- ✅ Branch comparison (same repo)
- ✅ Branch comparison (different repos)
- ✅ Cache hit/miss behavior
- ✅ API rate limit handling
- ✅ Network failure recovery
- ✅ 100% backward compatibility with local analysis

---

## 📦 New Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| PyGithub | >=2.1.0 | GitHub API v3 client |
| python-gitlab | >=4.0.0 | GitLab API v4 client |
| requests | >=2.31.0 | Generic git provider HTTP |
| diskcache | >=5.6.0 | Disk-based caching with TTL |

---

## ✅ Acceptance Criteria

### Functional (5 ACs)
- **AC-LENS-REMOTE-001:** Analyze GitHub file without clone
- **AC-LENS-REMOTE-002:** GitLab with authentication
- **AC-LENS-REMOTE-003:** Cross-repo branch comparison
- **AC-LENS-REMOTE-004:** Cache reduces API calls 80%+
- **AC-LENS-REMOTE-005:** 100% backward compatibility

### Non-Functional (3 ACs)
- **AC-LENS-PERF-001:** Response time < 5s (cached), < 15s (uncached)
- **AC-LENS-SEC-001:** Zero token leaks in logs
- **AC-LENS-RELIABLE-001:** Graceful degradation on API failures

---

## 🎯 Success Metrics

| Metric | Target | Tracking |
|--------|--------|----------|
| Test Coverage | >= 95% | pytest-cov |
| All Tests Passing | 257/257 (172 existing + 85 new) | CI/CD |
| Remote Analysis (Cached) | < 5s | Performance tests |
| Remote Analysis (Uncached) | < 15s | Performance tests |
| Cache Hit Rate | > 70% | Redis metrics |
| API Success Rate | > 95% | Audit logs |
| CLI Usage | > 100 invocations/week | CLI audit logs |

---

## 🚨 Risks & Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| API rate limits exhausted | MEDIUM | Aggressive caching, respect headers, exponential backoff |
| Large repo timeouts | MEDIUM | Timeout config, streaming results |
| Token exposure | HIGH | Never log tokens, secure storage, audit errors |
| Backward compat break | HIGH | 100% test pass rate, extensive integration testing |
| Cache corruption | MEDIUM | Cache validation, configurable TTL, manual clear |

---

## 📅 Timeline

**Milestones:**
- **M1:** Remote Adapter Design (Day 1) — LENS-010
- **M2:** GitHistoryAnalyzer Enhanced (Day 3) — LENS-011
- **M3:** Caching Implemented (Day 4) — LENS-012
- **M4:** LENSOrchestrator Updated (Day 5) — LENS-013
- **M5:** CLI Commands Ready (Day 6) — LENS-014
- **M6:** Branch Comparison Complete (Day 7) — LENS-015
- **M7:** Documentation & Deployment (Day 7) — LENS-016

---

## 🔗 Related Phases

- **Phase 7.1:** LENS Intelligence System (Base) — ✅ COMPLETE
- **Phase 8:** CORE-035 Consolidation — 📋 PLANNED
- **Phase 9:** Discovery Orchestrator — 📋 PLANNED

---

## 🛠️ Python API Examples

### Basic Remote Analysis
```python
from pathlib import Path
from cortex.orchestrators.support.lens_orchestrator import LENSOrchestrator

# Initialize with remote URL
orchestrator = LENSOrchestrator(
    repo_path="https://github.com/user/repo",
    branch="main"
)

# Analyze remote file
lens_context = orchestrator.analyze_remote_file(
    file_path="src/module.py"
)

# Use with IntentRouter
from cortex.orchestrators.core.intent_router import IntentRouter

router = IntentRouter()
decision = router.route({
    "operation": "refactor",
    "keywords": ["refactor"],
    "lens_context": lens_context  # +0.15 confidence boost
})
```

### Branch Comparison
```python
from cortex.brain.analysis.branch_comparator import BranchComparator

comparator = BranchComparator()
diff_report = comparator.compare_branches(
    repo_url="https://github.com/user/repo",
    branch_a="main",
    branch_b="feature/new-feature",
    file_path="src/core.py"
)

print(f"Commits diverged: {diff_report.commit_count}")
print(f"Lines changed: {diff_report.lines_changed}")
```

---

## 📚 Documentation Deliverables

- **docs/LENS-REMOTE-GUIDE.md** — Complete usage guide
- **docs/LENS-ARCHITECTURE.md** (updated) — Architecture diagrams
- **README.md** (updated) — Quick start examples

---

## ✨ Business Value

1. **Security/Compliance:** Analyze code before cloning (audit remote repos)
2. **PR Automation:** Review pull requests without local checkout
3. **Multi-Branch Intelligence:** Compare feature branches across repos
4. **Disk Space:** No need to clone 100s of repos for analysis
5. **Developer Experience:** Faster analysis, no git clone wait times

---

## 🔧 Configuration

**Environment Variables:**
```bash
# GitHub authentication
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"

# GitLab authentication
export GITLAB_TOKEN="glpat_xxxxxxxxxxxx"

# Cache configuration
export LENS_CACHE_PATH="/tmp/cortex-lens-cache"
export LENS_CACHE_SIZE_MB="500"
export LENS_CACHE_TTL_FILE="3600"  # 1 hour
export LENS_CACHE_TTL_COMMIT="300"  # 5 minutes
```

**Configuration File (`cortex/config/lens_config.yaml`):**
```yaml
lens:
  remote:
    providers:
      github:
        enabled: true
        api_version: "v3"
        timeout: 30
      gitlab:
        enabled: true
        api_version: "v4"
        timeout: 30
    
    cache:
      enabled: true
      path: "/tmp/cortex-lens-cache"
      size_mb: 500
      ttl:
        file_content: 3600  # 1 hour
        commit_history: 300  # 5 minutes
        blame_info: 3600    # 1 hour
```

---

## 🎓 Governance Compliance

**Applicable CORE Rules:**
- ✅ CORE-008 (TDD) — 60 new unit tests
- ✅ CORE-011 (Type hints mandatory)
- ✅ CORE-012 (Google-style docstrings)
- ✅ CORE-013 (No bare except)
- ✅ CORE-026 (Git checkpoint before deployment)
- ✅ CORE-027 (Audit trail: AC_START → AC_COMPLETE)
- ✅ CORE-030 (Implementation Truth — verify providers work)
- ✅ CORE-035 (Single Canonical Implementation — no duplicate adapters)
- ✅ CORE-038 (File Placement Policy)
- ✅ CORE-039 (MD Generation Prohibition)
- ✅ CORE-040 (Documentation Lifecycle)

---

**For complete specification, see:** [PHASE-10-LENS-REMOTE-INTELLIGENCE.yaml](./PHASE-10-LENS-REMOTE-INTELLIGENCE.yaml)
