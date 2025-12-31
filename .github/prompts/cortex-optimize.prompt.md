# 🎯 CORTEX Optimization Engine

**Version:** 1.0.0 | **Status:** ✅ PRODUCTION  
**Author:** Asif Hussain | **Website:** https://asifhussain60.github.io/CORTEX/  
**Copyright © 2025 Asif Hussain. All rights reserved.**

---

## 🎯 Purpose

Deep analysis and optimization of any artifact: prompts, code, configurations, architectures, or documentation. Identifies hidden failure modes, security vulnerabilities, performance bottlenecks, and provides robust, future-proof improvements.

**PRIMARY CHECK:** Detects bloat and recommends decomposition BEFORE running other analyses to prevent optimizing artifacts that should be restructured.

---

## 🔍 Analysis Scope

### Input Types
- **Prompts/Instructions** (`.prompt.md`, `.md`)
- **Source Code** (`.py`, `.cs`, `.js`, `.ts`, etc.)
- **Configuration** (`.yaml`, `.json`, `.xml`)
- **Architecture** (diagrams, specs, design docs)
- **Documentation** (README, guides, manifests)
- **Scripts** (`.sh`, `.ps1`, `.bat`)
- **Database** (schemas, queries, migrations)

---

## 🔬 Multi-Dimensional Analysis Framework

### 0️⃣ Bloat Analysis & Decomposition (PRIORITY: IMMEDIATE)

**Bloat Detection (Run FIRST before all other analyses):**

Check if artifact exceeds thresholds:

| Artifact Type | Bloat Threshold | Decomposition Required |
|---------------|-----------------|------------------------|
| **Prompt Files** | >500 lines | YES - See Pattern 1 (Section 10) |
| **Code Files** | >1,000 lines | YES - See Pattern 2 (Section 10) |
| **Config Files** | >300 lines | YES - See Pattern 3 (Section 10) |
| **Documentation** | >800 lines | YES - See Pattern 4 (Section 10) |
| **Manifests** | >600 lines | YES - See Pattern 5 (Section 10) |

**Bloat Impact:**
- ❌ **Performance:** Large files slow parsing/loading
- ❌ **Maintainability:** Cognitive overload for developers
- ❌ **Reliability:** Higher risk of merge conflicts
- ❌ **Efficiency:** Entire file loaded even when only small section needed
- ❌ **Scalability:** Cannot grow without exponential complexity

**Action:**
- If bloat detected → **STOP other analyses**
- Generate decomposition plan FIRST (Section 10)
- Resume other analyses after decomposition
- If no bloat → Continue to Edge Case Detection (Section 1)

---

### 1️⃣ Edge Case Detection (PRIORITY: CRITICAL)

**Missing Scenarios:**
- [ ] **Boundary Conditions** - Empty inputs, null values, max/min limits
- [ ] **Concurrent Access** - Race conditions, deadlocks, data corruption
- [ ] **Partial Failures** - Network timeouts, disk full, permission denied
- [ ] **Data Anomalies** - Invalid formats, encoding issues, malformed input
- [ ] **State Transitions** - Invalid state combinations, transition failures
- [ ] **Resource Exhaustion** - Memory leaks, file handle limits, connection pools
- [ ] **Time-Based Issues** - Timezone conflicts, leap seconds, DST transitions
- [ ] **Localization** - Unicode, RTL text, multi-byte characters

**Analysis Output:**
```markdown
### 🚨 Unhandled Edge Cases
1. **Race Condition:** Lines 45-67 (concurrent file write without locking)
2. **Null Pointer Risk:** Line 123 (unchecked dictionary access)
3. **Boundary Violation:** Line 89 (no max limit on list size)
```

---

### 2️⃣ Failure Mode Analysis (FMEA)

**Systematic Evaluation:**

| Component | Failure Mode | Impact | Likelihood | Detection | Mitigation |
|-----------|--------------|--------|------------|-----------|------------|
| File I/O | Disk full during write | HIGH | MEDIUM | None | Add pre-check + rollback |
| API Call | Timeout after 30s | MEDIUM | HIGH | Try-catch | Retry with exponential backoff |
| Database | Connection pool exhausted | HIGH | LOW | Monitor | Connection pooling + limits |

**Failure Categories:**
1. **Silent Failures** - No error handling, failures go unnoticed
2. **Cascading Failures** - One failure triggers multiple downstream failures
3. **Unrecoverable States** - System cannot resume after failure
4. **Data Loss Scenarios** - Incomplete writes, missing transactions
5. **Zombie Processes** - Background tasks continue after parent failure

---

### 3️⃣ Security Vulnerability Assessment

**OWASP Top 10 + Custom Checks:**

- [ ] **Injection Attacks** - SQL, command, LDAP, XPath injection
- [ ] **Authentication Bypass** - Weak credentials, session fixation
- [ ] **Sensitive Data Exposure** - Passwords in logs, API keys in code
- [ ] **XML/JSON Vulnerabilities** - XXE, deserialization attacks
- [ ] **Access Control Flaws** - Privilege escalation, IDOR
- [ ] **Security Misconfiguration** - Default credentials, debug mode enabled
- [ ] **Insecure Dependencies** - CVEs in third-party libraries
- [ ] **CSRF/XSS** - Missing CSRF tokens, unsanitized input
- [ ] **Path Traversal** - Directory traversal via user input
- [ ] **DoS Vectors** - Regex bombs, resource exhaustion attacks

**Output Format:**
```markdown
### 🔒 Security Issues (Severity: HIGH)
**CVE-2024-XXXX:** SQL Injection in user search (Line 234)
- **Attack Vector:** `search_query` parameter unsanitized
- **Fix:** Use parameterized queries + input validation
- **Priority:** P0 (Exploitable in production)
```

---

### 4️⃣ Performance Bottleneck Analysis

**Profiling Targets:**
- [ ] **Algorithmic Complexity** - O(n²) loops, nested iterations
- [ ] **Database Queries** - N+1 queries, missing indexes, full table scans
- [ ] **Memory Allocation** - Excessive allocations, large object graphs
- [ ] **I/O Operations** - Synchronous blocking, no buffering
- [ ] **Network Calls** - Serial API calls, no connection reuse
- [ ] **Serialization** - JSON parsing in hot paths
- [ ] **Regex Performance** - Catastrophic backtracking

**Optimization Matrix:**

| Issue | Current | Optimized | Speedup | Effort |
|-------|---------|-----------|---------|--------|
| Database query (Line 45) | 2.3s | 45ms | 51x | LOW (add index) |
| JSON parsing (Line 123) | 890ms | 12ms | 74x | MEDIUM (use msgpack) |
| File read loop (Line 67) | O(n²) | O(n) | 100x+ | HIGH (algorithm redesign) |

---

### 5️⃣ Scalability & Capacity Planning

**Horizontal Scaling:**
- [ ] **Stateless Design** - No server-side session state
- [ ] **Load Balancing** - Can distribute across multiple instances
- [ ] **Database Sharding** - Can partition data by key
- [ ] **Cache Strategy** - Distributed cache support

**Vertical Scaling:**
- [ ] **Resource Limits** - Max memory/CPU defined
- [ ] **Backpressure Handling** - Queue limits, rate limiting
- [ ] **Connection Pooling** - Configurable pool sizes

**Breaking Points:**
```markdown
### ⚠️ Scalability Limits
- **Current:** Handles 1,000 req/s before memory exhaustion
- **Limit:** Single-threaded file processing (bottleneck)
- **Fix:** Implement async I/O + worker pool (→ 10,000 req/s)
```

---

### 6️⃣ Rollback & Recovery Strategy

**Recovery Capabilities:**
- [ ] **Idempotency** - Can retry operations safely
- [ ] **Transactional Integrity** - All-or-nothing commits
- [ ] **Checkpointing** - Save progress for resume
- [ ] **Backup Strategy** - Automated backups before destructive ops
- [ ] **Health Checks** - Liveness/readiness probes
- [ ] **Circuit Breakers** - Fail fast when dependencies unavailable

**Disaster Recovery:**
```markdown
### 🆘 Recovery Plan
1. **Automated Rollback:** Git revert + DB migration rollback
2. **Manual Intervention:** Admin override via CLI flag
3. **Data Recovery:** Point-in-time restore from hourly snapshots
4. **RTO:** 15 minutes | **RPO:** 5 minutes
```

---

### 7️⃣ Data Integrity & Validation

**Input Validation:**
- [ ] **Type Safety** - Schema validation, type checking
- [ ] **Range Checks** - Min/max bounds enforced
- [ ] **Format Validation** - Regex, email, URL validation
- [ ] **Business Rules** - Domain-specific constraints
- [ ] **Sanitization** - XSS prevention, encoding

**Data Consistency:**
- [ ] **Foreign Key Constraints** - Referential integrity enforced
- [ ] **Unique Constraints** - Prevent duplicates
- [ ] **Check Constraints** - Domain value validation
- [ ] **Triggers/Auditing** - Change tracking

---

### 8️⃣ Dependency Risk Assessment

**Third-Party Dependencies:**
- [ ] **CVE Scan** - Known vulnerabilities in dependencies
- [ ] **License Compatibility** - GPL/MIT/Apache conflicts
- [ ] **Maintenance Status** - Last update, bus factor
- [ ] **Version Pinning** - Exact versions vs. ranges
- [ ] **Supply Chain Security** - Package integrity verification

**Dependency Matrix:**

| Package | Version | Last Update | CVEs | Alternatives |
|---------|---------|-------------|------|--------------|
| `requests` | 2.31.0 | 3mo ago | 0 | `httpx` (async) |
| `Newtonsoft.Json` | 13.0.1 | 1yr ago | 1 (LOW) | `System.Text.Json` |

---

### 9️⃣ Maintainability & Technical Debt

**Code Quality Metrics:**
- [ ] **Cyclomatic Complexity** - Max 10 per function
- [ ] **Code Duplication** - <5% duplication ratio
- [ ] **Test Coverage** - >80% line coverage
- [ ] **Documentation** - All public APIs documented
- [ ] **Naming Conventions** - Consistent, descriptive names
- [ ] **SOLID Principles** - Single responsibility, DI usage

**Bloat Detection Thresholds:**

| Artifact Type | Bloat Threshold | Action |
|---------------|-----------------|--------|
| **Prompt Files** | >500 lines | Decompose into sub-prompts |
| **Code Files** | >1,000 lines | Extract classes/modules |
| **Config Files** | >300 lines | Split by domain/environment |
| **Documentation** | >800 lines | Create document hierarchy |
| **Manifests** | >600 lines | Modularize sections |

**Decomposition Trigger Conditions:**
1. **Single Responsibility Violation** - File handles >3 distinct concerns
2. **High Coupling** - >10 dependencies in one file
3. **Low Cohesion** - Functions/sections unrelated to each other
4. **Cognitive Overload** - Requires >30min to understand file purpose
5. **Merge Conflict Frequency** - >5 conflicts in last 30 days

**Technical Debt Inventory:**
```markdown
### 📋 Technical Debt (Priority: P1)
1. **High Coupling:** `UserService` depends on 8 concrete classes (Lines 45-89)
   - **Refactor:** Introduce `IRepository` interface + DI
   - **Effort:** 4 hours | **Risk:** MEDIUM
2. **God Object:** `ConfigManager` has 2,300 lines, 47 methods
   - **Refactor:** Split into 4 feature-specific managers
   - **Effort:** 2 days | **Risk:** HIGH
3. **Bloated Prompt:** `system-prompt.md` has 1,200 lines (threshold: 500)
   - **Refactor:** Decompose into sub-prompts with index
   - **Effort:** 6 hours | **Risk:** LOW
```

---

### 🔟 Decomposition Strategy (Anti-Bloat)

**When to Decompose:**
- Artifact exceeds bloat threshold (see section 9)
- Single file serves multiple distinct purposes
- Cognitive load too high for maintainers
- Frequent merge conflicts in same file
- Performance degradation from file size

---

## ⚠️ CRITICAL: Entry Point Preservation Rule

**❌ DO NOT move the entry point during decomposition!**

**✅ CORRECT Approach:**
1. **Keep original file path** (e.g., `.github/prompts/cortex-maintenance.prompt.md`)
2. **Replace content** with lightweight index (150-200 lines)
3. **Create sub-folder** with same base name (e.g., `.github/prompts/maintenance/`)
4. **Move implementation** to sub-folder files

**❌ WRONG Approach:**
1. ~~Move original file to sub-folder~~
2. ~~Change entry point path~~
3. ~~Update all consumer references~~

**Why Entry Point Must Stay:**
- ✅ **Zero breaking changes** - All invocations still work
- ✅ **Backward compatibility** - Existing references unaffected
- ✅ **User experience preserved** - Commands unchanged
- ✅ **Minimal migration effort** - No consumer updates needed

**Visual Comparison:**

```
✅ CORRECT DECOMPOSITION (Entry Point Preserved)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BEFORE (v1.0 - Monolithic):
.github/prompts/
└── cortex-maintenance.prompt.md (4,844 lines) ← Entry point

AFTER (v2.0 - Modular):
.github/prompts/
├── cortex-maintenance.prompt.md (138 lines) ← SAME LOCATION (now index)
└── maintenance/                              ← NEW sub-folder
    ├── core/ (4 files)
    ├── pipeline/ (3 files)
    ├── phases/ (12 files)
    ├── guides/ (3 files)
    └── metadata/ (3 files)

User Command: "system maintenance" ← UNCHANGED
References: CORTEX.prompt.md, copilot-instructions.md ← NO UPDATES NEEDED

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

❌ WRONG DECOMPOSITION (Entry Point Moved)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

BEFORE (v1.0):
.github/prompts/
└── cortex-maintenance.prompt.md (4,844 lines) ← Entry point

AFTER (v2.0 - WRONG):
.github/prompts/
└── maintenance/
    ├── index.prompt.md (194 lines) ← MOVED (breaks everything!)
    ├── core/ (4 files)
    └── ...

Breaking Changes:
❌ User command "system maintenance" → File not found
❌ CORTEX.prompt.md reference → Must update to maintenance/index.prompt.md
❌ copilot-instructions.md → Must update reference
❌ Migration effort: HIGH (multiple consumer updates required)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Example (CORRECT):**
```
BEFORE: cortex-maintenance.prompt.md (4,844 lines at .github/prompts/)
AFTER:
  - cortex-maintenance.prompt.md (138 lines at .github/prompts/) ← INDEX, same location
  - maintenance/ folder (26 files at .github/prompts/maintenance/) ← NEW sub-prompts
```

**Example (WRONG):**
```
❌ Moving cortex-maintenance.prompt.md → maintenance/index.prompt.md
   This breaks all references and requires consumer updates!
```

---

**Decomposition Patterns:**

#### Pattern 1: Prompt File Decomposition

**⚠️ CRITICAL: Original file path MUST remain as entry point!**

**Before (Bloated):**
```
.github/prompts/
└── system-prompt.md (1,200 lines)  ← Entry point
    ├── Introduction
    ├── Core Instructions
    ├── Edge Cases
    ├── Security Rules
    ├── Performance Tips
    ├── Examples
    └── Troubleshooting
```

**After (Decomposed):**
```
.github/prompts/
├── system-prompt.md (150 lines)  ← SAME LOCATION = Entry point (now an index)
└── system/                        ← NEW sub-folder with implementation
    ├── core/
    │   ├── instructions.prompt.md
    │   ├── edge-cases.prompt.md
    │   └── security-rules.prompt.md
    ├── guides/
    │   ├── performance.prompt.md
    │   ├── examples.prompt.md
    │   └── troubleshooting.prompt.md
    └── metadata/
        ├── version-history.md
        └── references.md
```

**Entry Point Index File Structure (system-prompt.md):**
```markdown
# System Prompt (v2.0 - Modular)
**Version:** 2.0.0 | **Decomposed:** 2025-12-31

## 🎯 Purpose
Centralized prompt system with modular sub-prompts.

**OLD (v1.0):** Single file (1,200 lines) ❌ BLOAT  
**NEW (v2.0):** Index + 8 modular sub-prompts (150 lines main index) ✅ OPTIMIZED

## 📚 Sub-Prompts (Load on Demand)
1. **Core Instructions** → `system/core/instructions.prompt.md`
2. **Edge Cases** → `system/core/edge-cases.prompt.md`
3. **Security Rules** → `system/core/security-rules.prompt.md`
4. **Performance Guide** → `system/guides/performance.prompt.md`
5. **Examples** → `system/guides/examples.prompt.md`
6. **Troubleshooting** → `system/guides/troubleshooting.prompt.md`

## 🔗 Load Order
1. Core instructions (REQUIRED)
2. Edge cases (REQUIRED)
3. Security rules (REQUIRED)
4. Guides (OPTIONAL, context-dependent)

## 📋 Invocation (Unchanged from v1.0)
All commands work identically - no breaking changes to user interface.

## 📊 Performance Metrics (v2.0 vs v1.0)
- Main file: 1,200 → 150 lines (87% reduction)
- Context load: ~1,200 → ~400 lines (67% reduction)
- Load time: 4.6x faster
- Maintainability: 90% easier (isolated edits)
```

**Real-World Example (CORTEX Maintenance):**
```
✅ CORRECT:
  - Entry: .github/prompts/cortex-maintenance.prompt.md (138 lines, INDEX)
  - Impl:  .github/prompts/maintenance/* (26 files)
  - User command: "system maintenance" (unchanged)

❌ WRONG:
  - Entry: .github/prompts/maintenance/index.prompt.md (MOVED)
  - This breaks: "system maintenance" command
  - Requires: Update all references in CORTEX.prompt.md, copilot-instructions.md
```

---

#### Pattern 2: Code File Decomposition
**Before (God Object):**
```
UserManager.cs (2,300 lines)
├── User CRUD
├── Authentication
├── Authorization
├── Profile Management
├── Notification Preferences
├── Activity Logging
└── Reporting
```

**After (Decomposed):**
```
Users/
├── UserManager.cs (Facade, 200 lines)
├── Core/
│   ├── UserRepository.cs
│   ├── UserValidator.cs
│   └── UserMapper.cs
├── Auth/
│   ├── AuthenticationService.cs
│   ├── AuthorizationService.cs
│   └── PasswordService.cs
├── Features/
│   ├── ProfileService.cs
│   ├── NotificationService.cs
│   └── ActivityLogger.cs
└── Reports/
    └── UserReportService.cs
```

---

#### Pattern 3: Configuration File Decomposition
**Before (Monolithic Config):**
```
app-config.yaml (800 lines)
├── Database settings
├── API endpoints
├── Feature flags
├── Logging config
├── Security policies
├── Performance tuning
└── Monitoring settings
```

**After (Decomposed):**
```
config/
├── app-config.yaml (Index, 100 lines)
├── infrastructure/
│   ├── database.yaml
│   ├── cache.yaml
│   └── storage.yaml
├── application/
│   ├── api.yaml
│   ├── features.yaml
│   └── security.yaml
├── observability/
│   ├── logging.yaml
│   ├── metrics.yaml
│   └── tracing.yaml
└── environments/
    ├── dev.yaml
    ├── staging.yaml
    └── production.yaml
```

**Index Config Structure:**
```yaml
# app-config.yaml (Index)
version: "2.0.0"
decomposed: true

imports:
  - infrastructure/database.yaml
  - infrastructure/cache.yaml
  - application/api.yaml
  - application/features.yaml
  - observability/logging.yaml
  
environment_overrides:
  dev: environments/dev.yaml
  staging: environments/staging.yaml
  production: environments/production.yaml
```

---

#### Pattern 4: Documentation Decomposition
**Before (Monolithic Docs):**
```
README.md (1,500 lines)
├── Project Overview
├── Installation
├── Configuration
├── API Reference
├── Examples
├── Troubleshooting
├── Contributing
└── Architecture
```

**After (Decomposed):**
```
docs/
├── README.md (Overview + navigation, 200 lines)
├── getting-started/
│   ├── installation.md
│   ├── quick-start.md
│   └── configuration.md
├── api-reference/
│   ├── endpoints.md
│   ├── authentication.md
│   └── error-codes.md
├── guides/
│   ├── examples.md
│   ├── best-practices.md
│   └── troubleshooting.md
└── architecture/
    ├── overview.md
    ├── components.md
    └── data-flow.md
```

---

#### Pattern 5: Manifest File Decomposition
**Before (Bloated Manifest):**
```
orchestrator-manifest.yaml (1,000 lines)
├── Metadata
├── Phases (8 phases × 80 lines each)
├── Templates
├── Validation rules
└── Examples
```

**After (Decomposed):**
```
manifests/orchestrator/
├── orchestrator-manifest.yaml (Index, 150 lines)
├── phases/
│   ├── phase-01-discovery.yaml
│   ├── phase-02-analysis.yaml
│   ├── phase-03-design.yaml
│   ├── phase-04-implementation.yaml
│   ├── phase-05-testing.yaml
│   ├── phase-06-deployment.yaml
│   ├── phase-07-validation.yaml
│   └── phase-08-documentation.yaml
├── templates/
│   ├── response-templates.yaml
│   └── code-templates.yaml
├── rules/
│   ├── validation-rules.yaml
│   └── quality-gates.yaml
└── examples/
    └── usage-examples.yaml
```

---

**Standardized Folder Structure:**

```
{artifact-name}/
├── index.{ext}                    # Main entry point (index/facade)
├── core/                          # Essential components (REQUIRED)
│   ├── {component-1}.{ext}
│   ├── {component-2}.{ext}
│   └── ...
├── features/                      # Feature-specific modules (OPTIONAL)
│   ├── {feature-1}/
│   │   ├── {feature-1}.{ext}
│   │   └── {feature-1}.test.{ext}
│   └── {feature-2}/
│       ├── {feature-2}.{ext}
│       └── {feature-2}.test.{ext}
├── shared/                        # Shared utilities/helpers
│   ├── utils.{ext}
│   ├── constants.{ext}
│   └── types.{ext}
├── config/                        # Configuration files
│   ├── default.{ext}
│   └── overrides.{ext}
├── docs/                          # Documentation
│   ├── README.md
│   └── api-reference.md
├── tests/                         # Test files
│   ├── unit/
│   ├── integration/
│   └── e2e/
└── metadata/                      # Version history, changelog
    ├── CHANGELOG.md
    └── version-history.md
```

---

**Decomposition Checklist:**

- [ ] **⚠️ Entry Point Preserved** - Original file path unchanged (becomes index)
- [ ] **Index/Facade Created** - Original file now references all sub-components
- [ ] **Sub-Folder Created** - New folder with base name (e.g., `system/` for `system-prompt.md`)
- [ ] **Logical Grouping** - Related components in same folder
- [ ] **Clear Naming** - Folder/file names indicate purpose
- [ ] **Zero Breaking Changes** - All invocations/commands still work
- [ ] **Documentation Updated** - Index explains new structure + load strategy
- [ ] **No Reference Updates Needed** - Consumer code unchanged (entry point same)
- [ ] **Tests Still Pass** - No broken imports/references
- [ ] **Version Bumped** - Major version increment (2.0.0)
- [ ] **Migration Guide** - Document v1.0 → v2.0 changes
- [ ] **Original Archived** - v1.0 moved to `cortex-brain/archives/`
- [ ] **Performance Validated** - Load time improved, no degradation

---

**Decomposition Output:**

```markdown
### 🔨 Decomposition Plan: {Artifact Name}

**Bloat Detection:**
- **Current Size:** 1,200 lines
- **Threshold:** 500 lines
- **Severity:** CRITICAL (2.4x over threshold)

**Decomposition Strategy:** Pattern 1 (Prompt File)

**Entry Point Preservation:**
- **OLD Path:** `.github/prompts/system-prompt.md` (1,200 lines, monolithic)
- **NEW Path:** `.github/prompts/system-prompt.md` (150 lines, INDEX) ← SAME LOCATION
- **Implementation:** `.github/prompts/system/` (8 files, modular)

**New Structure:**
\`\`\`
.github/prompts/
├── system-prompt.md (150 lines, INDEX) ← Entry point unchanged
└── system/                          ← NEW sub-folder
    ├── core/ (3 files, 450 lines)
    ├── guides/ (3 files, 400 lines)
    └── metadata/ (2 files, 200 lines)
\`\`\`

**Benefits:**
- ✅ 87% reduction in main file size
- ✅ Modular: Load only required sections
- ✅ Maintainable: Edit concerns independently
- ✅ Testable: Validate sub-prompts separately
- ✅ Scalable: Add new sections without bloating index
- ✅ Zero breaking changes: Entry point path unchanged

**Migration Effort:** 6 hours | **Risk:** LOW

**Next Steps:**
1. Create sub-folder: `.github/prompts/system/`
2. Extract sections to sub-files
3. Replace original file content with index (keep same path!)
4. Validate: All commands/invocations still work
5. Archive v1.0: Move to `cortex-brain/archives/{artifact-name}-v1.0.{ext}`
6. Commit: "feat: Decompose {artifact-name} (v2.0) - 87% size reduction"
```

---

### 🔟 Integration & Deployment Pitfalls

**Integration Issues:**
- [ ] **API Versioning** - Breaking changes handled
- [ ] **Backward Compatibility** - Old clients supported
- [ ] **Contract Testing** - Consumer-driven contracts
- [ ] **Message Formats** - Schema evolution strategy

**Deployment Risks:**
- [ ] **Database Migrations** - Zero-downtime migrations
- [ ] **Configuration Management** - Environment-specific configs
- [ ] **Feature Flags** - Gradual rollout capability
- [ ] **Monitoring/Alerting** - Metrics, logs, traces
- [ ] **Smoke Tests** - Post-deployment validation

---

## 📊 Optimization Report Template

```markdown
# 🎯 Optimization Report: {Artifact Name}

**Analyzed:** {Date} | **Type:** {Code/Prompt/Config}  
**Severity:** {P0-Critical | P1-High | P2-Medium | P3-Low}

---

## 🔴 Critical Issues (P0)

### 1. SQL Injection Vulnerability (Line 234)
**Impact:** Data breach, unauthorized access  
**Fix:**
\`\`\`python
# BEFORE
query = f"SELECT * FROM users WHERE name = '{user_input}'"

# AFTER
query = "SELECT * FROM users WHERE name = %s"
cursor.execute(query, (user_input,))
\`\`\`
**References:** OWASP A03:2021

---

## 🟡 High-Priority Issues (P1)

### 1. Race Condition in File Write (Lines 45-67)
**Impact:** Data corruption, partial writes  
**Fix:** Add file locking mechanism
\`\`\`python
import fcntl
with open(file_path, 'w') as f:
    fcntl.flock(f, fcntl.LOCK_EX)
    f.write(content)
    fcntl.flock(f, fcntl.LOCK_UN)
\`\`\`

### 2. Performance Bottleneck: O(n²) Loop (Line 123)
**Impact:** 10,000x slower for large datasets  
**Fix:** Use hash table for O(n) lookup
\`\`\`python
# BEFORE: O(n²)
for item in list1:
    for match in list2:
        if item == match: process(item)

# AFTER: O(n)
lookup = set(list2)
for item in list1:
    if item in lookup: process(item)
\`\`\`

---

## 🟢 Enhancements (P2-P3)

### 1. Add Retry Logic for Network Calls
\`\`\`python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def fetch_data(url):
    return requests.get(url, timeout=30)
\`\`\`

### 2. Implement Circuit Breaker Pattern
**Library:** `pybreaker` or manual implementation

---

## 🚀 Alternative Approaches

### Current Architecture
- **Problem:** Synchronous, blocking I/O
- **Limit:** 1,000 req/s

### Recommended Alternative
- **Approach:** Async/await with task queue
- **Benefit:** 10x throughput, better resource utilization
- **Migration Effort:** 1-2 weeks

---

## 📋 Action Plan

| Task | Priority | Effort | Owner | Status |
|------|----------|--------|-------|--------|
| Fix SQL injection | P0 | 2h | Dev Team | ⏳ TODO |
| Add file locking | P1 | 4h | Dev Team | ⏳ TODO |
| Optimize O(n²) loop | P1 | 6h | Dev Team | ⏳ TODO |
| Implement retry logic | P2 | 3h | Dev Team | ⏳ TODO |

---

## ✅ Validation Checklist

- [ ] Security scan (Bandit/SonarQube)
- [ ] Load testing (JMeter/Locust)
- [ ] Code review approval
- [ ] Integration tests pass
- [ ] Documentation updated

---

**Next Steps:** Implement P0 fixes immediately, schedule P1 for next sprint.
```

---

## 🧠 CORTEX Optimization Workflow

### Phase 1: Context Gathering (5 min)
1. Read artifact in full
2. Identify artifact type (code/prompt/config)
3. Scan for dependencies/imports/references
4. Check existing documentation/tests

### Phase 2: Multi-Dimensional Analysis (15 min)
1. **Check bloat FIRST** (Section 0) - If detected, generate decomposition plan
2. Run remaining 10 analysis dimensions (Sections 1-10)
3. Assign severity (P0/P1/P2/P3)
4. Calculate impact × likelihood
5. Identify quick wins vs. major refactors

### Phase 3: Solution Design (10 min)
1. Provide before/after code samples
2. Calculate performance improvements
3. Estimate migration effort
4. Suggest alternative architectures

### Phase 4: Report Generation (5 min)
1. Use Optimization Report Template
2. Include action plan with owners
3. Add validation checklist
4. Export to `cortex-brain/documents/optimization/`

**Total Time:** 35 minutes per artifact

---

## 🛡️ Brain Protection Integration

**SKULL Rules Applied:**
- **HOLISTIC_DISCOVERY** - Search for existing optimizations before creating new ones
- **REFACTOR_CLEANUP** - Remove obsolete code identified during optimization
- **TDD_ENFORCEMENT** - All optimization fixes must include tests

**Output Location:**
```
cortex-brain/documents/optimization/
├── {artifact-name}-optimization-report.md
├── {artifact-name}-before.{ext}
├── {artifact-name}-after.{ext}
└── validation-results.json
```

---

## 🔧 Integration with CORTEX Orchestrators

| Orchestrator | Integration Point |
|--------------|-------------------|
| **Planning System** | Pre-implementation optimization scan |
| **TDD Mastery** | Post-implementation security + performance audit |
| **Refinement** | Continuous optimization as refinement sub-task |
| **Maintenance** | Phase 6: Code Quality Analysis |
| **Debug** | Root cause analysis with optimization recommendations |

---

## 📋 Usage Examples

### Example 1: Optimize Prompt File
```
User: "optimize CORTEX.prompt.md"
CORTEX: 
- **Bloat Check:** 240 lines (threshold: 500) ✅ PASS
- Edge case: No fallback for LLM classification timeout
- Performance: Intent router could use trie data structure
- Maintainability: 250-line limit approaching (currently 240)
[Generates optimization report with 7 recommendations]
```

### Example 2: Optimize Python Code
```
User: "optimize src/orchestrators/planning_orchestrator.py"
CORTEX:
- **Bloat Check:** 1,450 lines (threshold: 1,000) ❌ BLOAT DETECTED
- **Action:** Generate decomposition plan FIRST
[Shows Pattern 2 decomposition with folder structure]
[After decomposition approved, runs security/performance analysis]
```

### Example 3: Optimize YAML Config
```
User: "optimize cortex-brain/operations-config.yaml"
CORTEX:
- **Bloat Check:** 850 lines (threshold: 300) ❌ BLOAT DETECTED
- **Action:** Decompose into domain-specific configs
[Shows Pattern 3 decomposition with 5 sub-configs]
[Generates migration guide for config consumers]
```

### Example 4: Optimize After Decomposition
```
User: "optimize core/instructions.prompt.md"
CORTEX:
- **Bloat Check:** 280 lines (threshold: 500) ✅ PASS
- Security: API key in example code (Line 23)
- Performance: Regex pattern could be precompiled
- Edge case: No handling for missing sub-prompt references
[Generates optimization report with fixes]
```

---

## 🎯 Success Criteria

**Optimization is complete when:**
1. ✅ Bloat check passed OR decomposition plan generated + approved
2. ✅ All P0 issues resolved
3. ✅ P1 issues have mitigation plan
4. ✅ Performance benchmarks show measurable improvement
5. ✅ Security scan passes with 0 HIGH/CRITICAL findings
6. ✅ Test coverage maintained or increased
7. ✅ Documentation updated with new architecture
8. ✅ Rollback plan documented
9. ✅ If decomposed: Migration guide provided + backward compatibility plan

---

## 📚 References

- **OWASP Top 10:** https://owasp.org/Top10/
- **FMEA Guide:** https://asq.org/quality-resources/fmea
- **Performance Patterns:** https://docs.microsoft.com/azure/architecture/patterns/
- **SOLID Principles:** https://en.wikipedia.org/wiki/SOLID

---

**Version History:**
- v1.0.0 (2025-01-31): Initial release

**Maintainer:** Asif Hussain | **License:** Proprietary
