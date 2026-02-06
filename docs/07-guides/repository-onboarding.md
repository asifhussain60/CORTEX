## 📦 Repository Onboarding (Phase 28)

**Status:** ✅ COMPLETE  
**Version:** 1.0  
**Created:** 2026-02-06

---

### 🎯 Overview

Repository onboarding is the **MANDATORY first step** when interacting with external repositories. It creates comprehensive profiles that enable CORTEX to understand and interact with repositories in a loosely-coupled, deletion-safe manner.

### 🚀 Quick Start

```bash
/onboard /path/to/repository
```

Example:
```bash
/onboard /Users/asifhussain/PROJECTS/KSESSIONS
```

---

### 📋 What Gets Profiled

| Category | Details |
|----------|---------|
| **Tech Stack** | Primary language, frameworks, dependencies |
| **Structure** | Company domains, tests, documentation |
| **Security** | Secrets management, auth patterns, vulnerabilities |
| **Standards** | Coding style, test patterns, API patterns |
| **Loose Coupling** | Deletion-safe references, fallback strategies |

---

### 🔧 Profile Schema

```yaml
repository:
  name: "KSESSIONS"
  path: "/Users/asifhussain/PROJECTS/KSESSIONS"
  onboarded_at: "2026-02-06T10:30:00Z"
  last_validated: "2026-02-06T10:30:00Z"
  exists: true

tech_stack:
  primary_language: "Python"
  languages: ["Python", "YAML", "Markdown"]
  frameworks: ["FastAPI", "Pydantic"]
  dependencies:
    - "pyyaml>=6.0"
    - "pydantic>=2.0"

structure:
  has_company_domains: true
  company_domains_path: "company/domains/"
  domains_detected:
    - "security/"
    - "testing/"
    - "api-standards/"
  has_tests: true
  test_framework: "pytest"
  has_docs: true
  doc_format: "markdown"

standards:
  coding_style: "black + mypy + pylint"
  security_baseline: "OWASP Top 10 compliant"
  test_patterns: "TDD with pytest"
  api_patterns: "RESTful + OpenAPI 3.0"

security:
  secrets_management: "environment variables"
  auth_pattern: "JWT + OAuth2"
  vulnerabilities_detected: 0
  last_scan: "2026-02-06T10:30:00Z"

loose_coupling:
  referenced_by_cortex: true
  deletion_safe: true
  fallback_strategy: "use_cached_profile"
```

---

### 🛡️ Onboarding-First Enforcement

CORTEX automatically enforces onboarding before external repository operations via the **OnboardingGate** middleware:

```python
# Unonboarded repository - BLOCKED
request = {'operation': 'analyze', 'repo_path': '/path/to/unonboarded'}
result = gate.check_onboarding(request)
# {'onboarded': False, 'error': "Repository 'unonboarded' is not onboarded..."}

# Onboarded repository - ALLOWED
request = {'operation': 'analyze', 'repo_path': '/path/to/ksessions'}
result = gate.check_onboarding(request)
# {'onboarded': True, 'repo_name': 'KSESSIONS'}
```

**Auto-onboarding:** Set `auto_onboard=True` to automatically onboard new repositories on first access.

---

### 🧩 Loose Coupling Architecture

**Problem:** Hard references to external repositories break CORTEX when repos are deleted.

**Solution:** Profile-based loose coupling:

1. **Profile Storage:** Profiles stored in `cortex_brain/onboarded_repos/`
2. **Path References:** References by path, not hard links
3. **Existence Validation:** Check `exists` flag before operations
4. **Graceful Degradation:** Use cached profile if repo deleted
5. **Fallback Strategy:** `use_cached_profile` for deleted repos

```python
# Repository still usable after deletion
profile = store.load("KSESSIONS")
profile.validate_exists()  # Updates 'exists' flag

if not profile.exists:
    # Use cached profile data
    print(f"Tech stack: {profile.tech_stack.primary_language}")
    # Operation continues with cached information
```

---

### 📊 Test Coverage

**Phase 28 Test Results:** ✅ **37/37 tests passing (100%)**

| Test Category | Tests | Status |
|---------------|-------|--------|
| Profile Schema | 10 | ✅ 100% |
| Profile Store | 9 | ✅ 100% |
| Onboarding Orchestrator | 10 | ✅ 100% |
| Onboarding Gate | 5 | ✅ 100% |
| KSESSIONS Integration | 3 | ✅ 100% |

---

### 🎓 API Usage

#### Python API

```python
from cortex.orchestrators.support.repository_onboarding_orchestrator import (
    get_repository_onboarding_orchestrator
)
from cortex_brain.onboarded_repos import ProfileStore

# Onboard repository
orchestrator = get_repository_onboarding_orchestrator()
profile = orchestrator.onboard_repository_with_profile(
    repo_path=Path("/path/to/repo")
)

# Load profile later
store = ProfileStore()
profile = store.load("REPO_NAME")

# Check if repo still exists
profile.validate_exists()
if not profile.exists:
    print("Repository deleted, using cached profile")
```

#### MCP Tool

```bash
# Via MCP
cortex_onboard_repository --repo_path /path/to/repo

# Returns:
{
  "success": true,
  "repo_name": "REPO_NAME",
  "onboarded_at": "2026-02-06T10:30:00",
  "profile": {...}
}
```

---

### 🔍 Profile Management

```python
from cortex_brain.onboarded_repos import ProfileStore

store = ProfileStore()

# List all profiles
profiles = store.list_all()

# Check existence
if store.exists("KSESSIONS"):
    print("KSESSIONS is onboarded")

# Delete profile
store.delete("OLD_REPO")
```

---

### 🌐 Company Domains Integration (Phase 27)

When `company/domains/` is detected, Phase 27 (Company Domain Integration) uses the profile for standards resolution:

```yaml
structure:
  has_company_domains: true
  company_domains_path: "company/domains/"
  domains_detected:
    - "security/"
    - "testing/"
    - "api-standards/"
```

Phase 27 StandardsResolver reads these domains for:
- Security requirements
- Testing standards
- API patterns
- Gap analysis

---

### ⚠️ Important Notes

1. **NO Stubs:** All implementations are real (CORE-030)
2. **TDD-First:** Tests written before code (CORE-008)
3. **Loose Coupling:** External repos can be safely deleted
4. **Single Source of Truth:** Profiles in `cortex_brain/onboarded_repos/`
5. **Auto-Cleanup:** Profiles persist after repo deletion for reference

---

### 📁 File Locations

| Component | Path |
|-----------|------|
| Profile Schema | `cortex_brain/onboarded_repos/profile_schema.py` |
| Profile Store | `cortex_brain/onboarded_repos/profile_store.py` |
| Onboarding Orchestrator | `cortex/orchestrators/support/repository_onboarding_orchestrator.py` |
| Onboarding Gate | `cortex/mcp/middleware/onboarding_gate.py` |
| MCP Tool | `cortex/mcp/tools/repository_onboarding_tool.py` |
| Profiles Storage | `cortex_brain/onboarded_repos/*.yaml` |

---

### 🎯 Next Steps

- **Phase 27:** Company Domain Integration (uses onboarding profiles)
- **Phase 29:** Multi-repo orchestration (builds on onboarding)

---

**Authority:** `phase-28-repository-onboarding-system.yaml`  
**Completion Date:** 2026-02-06  
**Test Coverage:** 100%
