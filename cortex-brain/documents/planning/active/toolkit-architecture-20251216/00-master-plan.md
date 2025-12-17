# CORTEX Toolkit Architecture Plan

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Date:** December 16, 2025  
**Status:** Planning Phase

---

## Executive Summary

Analysis of CORTEX repository revealed **200+ scattered Python scripts** and **100+ PowerShell scripts** across multiple directories with inconsistent organization, duplication, and no standardized reuse mechanism. This plan proposes a **well-architected CORTEX Toolkit** - a centralized, reusable library that can be leveraged across all workspace repositories (CORTEX, KASHKOLE, KSESSIONS, NOOR CANVAS).

**Key Findings:**
- **3251 Python files** identified (including source + tests)
- **170+ utility/script files** in `scripts/` directory alone
- **10+ subdirectories** with overlapping functionality
- **No standardized import/usage pattern** (ad-hoc `sys.path` manipulation)
- **Duplication:** Similar functionality reimplemented across scripts
- **Boundary issues:** CORTEX scripts not easily accessible from other repos

**Proposed Solution:**
Create `cortex-toolkit/` as a **first-class Python package** with proper module structure, cross-repo accessibility, and standardized utilities for common development operations.

---

## 1. Current State Analysis

### 1.1 Script Inventory by Category

#### **Category A: CLI Wrappers & System Operations** (10 scripts)
**Location:** `scripts/cli_wrappers/`

| Script | Purpose | Status | Cross-Repo |
|--------|---------|--------|------------|
| `align_wrapper.py` | System alignment operation | Production | ❌ |
| `cleanup_wrapper.py` | Cleanup operations | Production | ❌ |
| `deploy_wrapper.py` | Deployment operations | Production | ❌ |
| `healthcheck_wrapper.py` | Health diagnostics | Production | ❌ |
| `optimize_wrapper.py` | System optimization | Production | ❌ |
| `review_wrapper.py` | Code review interface | Production | ❌ |
| `sanitize_wrapper.py` | Code sanitization | Production | ✅ Needed |
| `regenerate_prompts_wrapper.py` | Prompt regeneration | Production | ❌ |
| `base_wrapper.py` | Base wrapper infrastructure | Library | ✅ Core |

**Analysis:**
- Well-organized with base class pattern
- Not accessible from other repos
- Should be part of toolkit core

#### **Category B: Utilities & Helpers** (25+ scripts)
**Location:** `scripts/utilities/`

| Script | Purpose | Cross-Repo Need |
|--------|---------|-----------------|
| `migrate_entities_table.py` | Database migrations | ✅ High |
| `validate_phase*.py` | Phase validation | ✅ Medium |
| `analyze_*.py` | Various analyzers | ✅ High |
| `benchmark_*.py` | Performance benchmarks | ✅ Medium |
| `debug_*.py` | Debug utilities | ✅ High |
| `profile_*.py` | Profiling tools | ✅ Medium |

**Analysis:**
- Mix of CORTEX-specific and generic utilities
- Many could be useful for KSESSIONS/NOOR CANVAS
- Need categorization: generic vs CORTEX-specific

#### **Category C: Migrations & Schema Management** (15+ scripts)
**Location:** `scripts/` (root)

| Script Pattern | Count | Cross-Repo Need |
|----------------|-------|-----------------|
| `migrate_*.py` | 12 | ✅ Generic pattern |
| `fix_*.py` | 8 | ⚠️ One-time fixes |
| `execute_phase*.py` | 3 | ✅ Workflow pattern |

**Analysis:**
- Migration pattern reusable across repos
- Fix scripts are historical (should archive)
- Phase execution pattern valuable

#### **Category D: Validation & Testing** (20+ scripts)
**Location:** `scripts/validation/`

| Script | Purpose | Cross-Repo |
|--------|---------|------------|
| `post_setup_validator.py` | Setup validation | ✅ High |
| `publish_manifest_validator.py` | Package validation | ✅ High |
| `validate_issue3_*.py` | Issue-specific | ❌ CORTEX only |
| `validate_upgrade_system.py` | Upgrade checks | ✅ Medium |

**Analysis:**
- Validation patterns highly reusable
- Should extract generic validation framework
- Issue-specific validators should remain in CORTEX

#### **Category E: Documentation & Generation** (15+ scripts)
**Location:** `scripts/`

| Script | Purpose | Cross-Repo |
|--------|---------|------------|
| `generate_docs_*.py` | Doc generation | ✅ High |
| `regenerate_*.py` | Regeneration tools | ⚠️ CORTEX-specific |
| `template_analysis.py` | Template tools | ✅ Medium |
| `dependency_graph_generator.py` | Dependency graphs | ✅ High |

**Analysis:**
- Documentation generation needed for all repos
- Template analysis useful for NOOR CANVAS
- Dependency graphs valuable for KSESSIONS

#### **Category F: Deployment & Release** (10 scripts)
**Location:** `scripts/`

| Script | Purpose | Cross-Repo |
|--------|---------|------------|
| `deploy_cortex*.py` | CORTEX deployment | ❌ |
| `build_package.py` | Package building | ✅ High |
| `verify_deployment_package.py` | Package verification | ✅ High |
| `create_deploy_package.sh` | Shell deployment | ✅ Medium |

**Analysis:**
- Package building/verification is generic
- Deployment specifics are per-repo
- Extract generic packaging toolkit

#### **Category G: Monitoring & Analytics** (10+ scripts)
**Location:** `scripts/`

| Script | Purpose | Cross-Repo |
|--------|---------|------------|
| `monitor_brain_health.py` | CORTEX monitoring | ❌ |
| `visualize_brain_health.py` | CORTEX visualization | ❌ |
| `collect_dashboard_data*.py` | Data collection | ✅ Pattern |
| `token_pricing_calculator.py` | Token analysis | ✅ High |

**Analysis:**
- Monitoring patterns reusable
- CORTEX-specific metrics stay internal
- Token analysis useful for all AI-integrated repos

#### **Category H: Archive & Legacy** (100+ scripts)
**Location:** `scripts/_archive/`

| Subdirectory | Count | Status |
|--------------|-------|--------|
| `kds-legacy/` | 80+ | ⚠️ Historical |
| `cortex-brain/` | 10+ | ⚠️ Superseded |
| Other archives | 20+ | ⚠️ Reference only |

**Analysis:**
- Should remain archived
- Not candidates for toolkit
- Keep for historical reference

### 1.2 Problems with Current Structure

#### **Problem 1: Ad-hoc Import Patterns**
```python
# Found in 50+ test files
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
```

**Impact:**
- Brittle path manipulation
- No standardized import
- Breaks when file moves
- Not cross-repo compatible

#### **Problem 2: Scattered Utilities**
```
scripts/
├── some_util.py              # Root level
├── utilities/another_util.py # In utilities/
├── admin/third_util.py       # In admin/
└── operations/fourth_util.py # In operations/
```

**Impact:**
- Unclear where to find utilities
- Duplication across directories
- No clear ownership

#### **Problem 3: No Package Structure**
**Current:** Scripts are just files  
**Needed:** Proper Python package with `__init__.py`, imports, metadata

**Impact:**
- Can't `pip install cortex-toolkit`
- Can't use standard imports
- Not distributable

#### **Problem 4: Cross-Repo Inaccessibility**
**Current:** KSESSIONS/NOOR CANVAS can't easily use CORTEX scripts

**Example Need:**
```python
# From NOOR CANVAS - IMPOSSIBLE TODAY
from cortex_toolkit.validation import validate_setup
from cortex_toolkit.testing import run_tests_with_coverage
from cortex_toolkit.docs import generate_api_docs
```

**Impact:**
- Code duplication across repos
- CORTEX functionality not leveraged
- Each repo reinvents wheel

#### **Problem 5: Workspace Context Issues**
**Current:** Scripts assume single repo context (see chat context above)

**Impact:**
- Path resolution failures
- Wrong repo targeted
- No workspace awareness

---

## 2. Proposed Architecture: CORTEX Toolkit

### 2.1 High-Level Design

```
D:\PROJECTS\CORTEX\
├── cortex-toolkit/           # NEW: First-class toolkit package
│   ├── __init__.py
│   ├── setup.py             # Package metadata
│   ├── pyproject.toml       # Modern Python packaging
│   ├── README.md
│   ├── CHANGELOG.md
│   │
│   ├── cortex_toolkit/      # Main package
│   │   ├── __init__.py
│   │   ├── version.py
│   │   │
│   │   ├── cli/             # CLI wrappers & system ops
│   │   │   ├── __init__.py
│   │   │   ├── base.py      # BaseWrapper
│   │   │   ├── align.py
│   │   │   ├── cleanup.py
│   │   │   ├── deploy.py
│   │   │   ├── healthcheck.py
│   │   │   ├── optimize.py
│   │   │   ├── review.py
│   │   │   └── sanitize.py
│   │   │
│   │   ├── validation/      # Generic validation framework
│   │   │   ├── __init__.py
│   │   │   ├── base.py      # BaseValidator
│   │   │   ├── setup.py     # Setup validation
│   │   │   ├── package.py   # Package validation
│   │   │   ├── schema.py    # Schema validation
│   │   │   └── upgrade.py   # Upgrade validation
│   │   │
│   │   ├── testing/         # Testing utilities
│   │   │   ├── __init__.py
│   │   │   ├── coverage.py  # Coverage tools
│   │   │   ├── fixtures.py  # Common fixtures
│   │   │   ├── mocking.py   # Mock helpers
│   │   │   └── runners.py   # Test runners
│   │   │
│   │   ├── documentation/   # Doc generation
│   │   │   ├── __init__.py
│   │   │   ├── api_docs.py
│   │   │   ├── readme.py
│   │   │   ├── changelog.py
│   │   │   └── diagrams.py
│   │   │
│   │   ├── deployment/      # Package & deploy
│   │   │   ├── __init__.py
│   │   │   ├── builder.py
│   │   │   ├── packager.py
│   │   │   ├── verifier.py
│   │   │   └── publisher.py
│   │   │
│   │   ├── migration/       # DB & schema migrations
│   │   │   ├── __init__.py
│   │   │   ├── base.py      # BaseMigration
│   │   │   ├── sqlite.py
│   │   │   ├── schema.py
│   │   │   └── runner.py
│   │   │
│   │   ├── monitoring/      # Monitoring & analytics
│   │   │   ├── __init__.py
│   │   │   ├── metrics.py
│   │   │   ├── logging.py
│   │   │   ├── profiling.py
│   │   │   └── visualization.py
│   │   │
│   │   ├── context/         # Workspace context (from POC)
│   │   │   ├── __init__.py
│   │   │   ├── workspace_context.py
│   │   │   ├── context_resolver.py
│   │   │   └── copilot_integration.py
│   │   │
│   │   ├── utils/           # Generic utilities
│   │   │   ├── __init__.py
│   │   │   ├── filesystem.py
│   │   │   ├── git.py
│   │   │   ├── subprocess.py
│   │   │   ├── config.py
│   │   │   └── formatting.py
│   │   │
│   │   └── core/            # Core CORTEX integration
│   │       ├── __init__.py
│   │       ├── brain.py     # Brain operations
│   │       ├── agents.py    # Agent utilities
│   │       └── operations.py # Operation helpers
│   │
│   └── tests/               # Toolkit tests
│       ├── __init__.py
│       ├── test_cli/
│       ├── test_validation/
│       ├── test_testing/
│       └── ...
│
├── src/                     # Existing CORTEX source
├── scripts/                 # Legacy scripts (gradually migrate)
└── ...
```

### 2.2 Package Installation Approach

#### **Option A: Editable Install (RECOMMENDED)**
```bash
# From CORTEX root
cd cortex-toolkit
pip install -e .

# Now available in ALL repos with same Python environment
```

**Advantages:**
- ✅ Development-friendly (changes immediately available)
- ✅ Single source of truth
- ✅ Works across all workspace repos
- ✅ Standard Python practice

#### **Option B: Path-Based Install**
```python
# In cortex.config.json
{
  "toolkit_path": "D:\\PROJECTS\\CORTEX\\cortex-toolkit"
}

# Auto-added to sys.path on CORTEX operations
```

**Advantages:**
- ✅ No pip install needed
- ✅ Dynamic loading
- ⚠️ Non-standard approach

**Recommendation:** Use Option A (editable install) for standardization

### 2.3 Usage Examples

#### **Example 1: From NOOR CANVAS**
```python
# In NOOR CANVAS/Scripts/analyze_code.py
from cortex_toolkit.validation import PackageValidator
from cortex_toolkit.testing import CoverageAnalyzer
from cortex_toolkit.documentation import APIDocGenerator
from cortex_toolkit.context import WorkspaceContext, resolve_context

# Get workspace-aware context
context = resolve_context(
    repo_root="D:\\PROJECTS\\NOOR CANVAS",
    cortex_root="D:\\PROJECTS\\CORTEX"
)

# Use toolkit utilities
validator = PackageValidator(context)
if validator.validate_structure():
    analyzer = CoverageAnalyzer(context)
    report = analyzer.generate_report()
    
    doc_gen = APIDocGenerator(context)
    doc_gen.generate(output_dir=context.repo_root / "docs")
```

#### **Example 2: From KSESSIONS**
```python
# In KSESSIONS/Workspaces/SCRIPTS/run_migrations.py
from cortex_toolkit.migration import MigrationRunner, SQLiteMigration
from cortex_toolkit.context import resolve_context

context = resolve_context(
    repo_root="D:\\PROJECTS\\KSESSIONS"
)

runner = MigrationRunner(context)
migrations = [
    SQLiteMigration("add_user_profile_table", "migrations/001_users.sql"),
    SQLiteMigration("add_indexes", "migrations/002_indexes.sql")
]

runner.execute(migrations)
```

#### **Example 3: From CORTEX**
```python
# Existing CORTEX operations just import directly
from cortex_toolkit.cli import AlignWrapper, HealthCheckWrapper
from cortex_toolkit.context import resolve_context

context = resolve_context()  # Auto-detects CORTEX context

align = AlignWrapper(context)
health = HealthCheckWrapper(context)

align.execute()
health.check_and_report()
```

### 2.4 Cross-Repo Compatibility Strategy

#### **Principle 1: Context-Aware by Default**
Every toolkit function accepts `WorkspaceContext`:
```python
def generate_docs(context: WorkspaceContext, output_dir: Path = None):
    """
    Generate documentation for any repo.
    
    Args:
        context: Workspace context (repo_root, cortex_root, etc.)
        output_dir: Optional output directory (defaults to repo_root/docs)
    """
    output_dir = output_dir or (context.repo_root / "docs")
    # Implementation works for any repo
```

#### **Principle 2: Generic-First, CORTEX-Specific Separate**
- **Generic:** `cortex_toolkit.validation`, `cortex_toolkit.testing`, `cortex_toolkit.documentation`
- **CORTEX-specific:** `cortex_toolkit.core.brain`, `cortex_toolkit.core.agents`

#### **Principle 3: Zero External Dependencies (Where Possible)**
- Use stdlib (pathlib, subprocess, sqlite3, etc.)
- Optional dependencies for advanced features
- Clear documentation of requirements

#### **Principle 4: Clear Versioning**
```python
# cortex_toolkit/version.py
__version__ = "1.0.0"
__cortex_version_required__ = ">=3.9.0"

def check_compatibility():
    """Check if toolkit version is compatible with current CORTEX."""
```

---

## 3. Migration Strategy

### 3.1 Phase 1: Foundation (Week 1)

**Tasks:**
1. ✅ Create `cortex-toolkit/` directory structure
2. ✅ Set up `pyproject.toml` with metadata
3. ✅ Implement base modules:
   - `cortex_toolkit/context/` (leverage existing POC)
   - `cortex_toolkit/utils/` (filesystem, git, subprocess)
   - `cortex_toolkit/core/` (CORTEX integration points)
4. ✅ Create editable install process
5. ✅ Write initial documentation

**Deliverables:**
- Installable package (`pip install -e cortex-toolkit`)
- Core utilities functional
- Basic tests passing

### 3.2 Phase 2: CLI Wrappers (Week 2)

**Tasks:**
1. Migrate `scripts/cli_wrappers/` → `cortex_toolkit/cli/`
2. Ensure all wrappers use `WorkspaceContext`
3. Add tests for each wrapper
4. Update CORTEX operations to import from toolkit

**Deliverables:**
- All CLI wrappers in toolkit
- CORTEX operations using toolkit imports
- 100% test coverage

### 3.3 Phase 3: Validation & Testing (Week 3)

**Tasks:**
1. Migrate validation scripts → `cortex_toolkit/validation/`
2. Extract generic testing patterns → `cortex_toolkit/testing/`
3. Create `BaseValidator` and `TestRunner` base classes
4. Add comprehensive tests

**Deliverables:**
- Generic validation framework
- Reusable testing utilities
- NOOR CANVAS/KSESSIONS can use validation

### 3.4 Phase 4: Documentation & Deployment (Week 4)

**Tasks:**
1. Migrate doc generation → `cortex_toolkit/documentation/`
2. Migrate deployment scripts → `cortex_toolkit/deployment/`
3. Create packaging utilities
4. Add usage examples for each repo

**Deliverables:**
- Doc generation tools available
- Deployment utilities standardized
- Cross-repo usage documented

### 3.5 Phase 5: Monitoring & Analytics (Week 5)

**Tasks:**
1. Extract generic monitoring → `cortex_toolkit/monitoring/`
2. Migrate analytics patterns
3. Create visualization utilities
4. Add profiling tools

**Deliverables:**
- Generic monitoring framework
- Reusable analytics tools
- Performance profiling utilities

### 3.6 Phase 6: Migration Framework (Week 6)

**Tasks:**
1. Create `BaseMigration` class
2. Implement SQLite migration runner
3. Add schema validation
4. Create rollback mechanisms

**Deliverables:**
- Generic migration framework
- KSESSIONS/NOOR CANVAS can use for their DBs
- Automated migration testing

### 3.7 Phase 7: Legacy Cleanup (Week 7)

**Tasks:**
1. Archive unused scripts to `scripts/_archive/`
2. Update all imports across CORTEX
3. Remove duplicated code
4. Document migration status

**Deliverables:**
- Clean `scripts/` directory
- All imports use toolkit
- Migration documentation complete

---

## 4. Directory Organization Plan

### 4.1 New Structure

```
D:\PROJECTS\CORTEX\
├── cortex-toolkit/                  # NEW: Toolkit package
│   ├── pyproject.toml
│   ├── setup.py
│   ├── README.md
│   ├── LICENSE
│   ├── CHANGELOG.md
│   ├── cortex_toolkit/             # Main package
│   │   └── [modules as designed]
│   ├── tests/
│   ├── docs/
│   └── examples/                   # Usage examples per repo
│       ├── noor_canvas_example.py
│       ├── ksessions_example.py
│       └── kashkole_example.py
│
├── src/                            # Existing CORTEX source
│   └── [uses cortex_toolkit imports]
│
├── scripts/                        # Reduced to repo-specific only
│   ├── cortex/                    # CORTEX-specific scripts
│   │   ├── brain_operations.py
│   │   ├── agent_management.py
│   │   └── orchestrator_utils.py
│   ├── admin/                     # Admin-only operations
│   └── _archive/                  # Historical scripts
│
└── ...
```

### 4.2 Cross-Repo Access Pattern

```
D:\PROJECTS\
├── CORTEX\
│   └── cortex-toolkit\            # Source of truth
│
├── KASHKOLE\
│   └── Scripts\
│       └── use_toolkit.py         # Imports cortex_toolkit
│
├── KSESSIONS\
│   └── Workspaces\SCRIPTS\
│       └── use_toolkit.py         # Imports cortex_toolkit
│
└── NOOR CANVAS\
    └── Scripts\
        └── use_toolkit.py         # Imports cortex_toolkit
```

**Key:** All repos use **same Python environment**, toolkit installed once via `pip install -e`

---

## 5. Success Criteria

### 5.1 Functional Goals

- ✅ Toolkit installable with `pip install -e cortex-toolkit`
- ✅ All modules importable from any repo
- ✅ 90%+ test coverage
- ✅ Documentation complete
- ✅ Zero CORTEX-specific assumptions in generic modules
- ✅ Context-aware operations work across repos
- ✅ No more ad-hoc `sys.path` manipulation

### 5.2 Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Test Coverage | ≥90% | pytest --cov |
| Import Success | 100% | All repos can import |
| Context Resolution | <10ms | Performance tests |
| Cross-Repo Usage | 3/3 repos | NOOR CANVAS, KSESSIONS, KASHKOLE |
| Code Duplication | <5% | Static analysis |
| Documentation | 100% | All modules documented |

### 5.3 Usage Validation

**Test in NOOR CANVAS:**
```python
from cortex_toolkit.validation import PackageValidator
from cortex_toolkit.testing import CoverageAnalyzer
from cortex_toolkit.documentation import APIDocGenerator

# Should work without modification
```

**Test in KSESSIONS:**
```python
from cortex_toolkit.migration import MigrationRunner
from cortex_toolkit.deployment import PackageBuilder

# Should work without modification
```

**Test in KASHKOLE:**
```python
from cortex_toolkit.monitoring import MetricsCollector
from cortex_toolkit.utils import GitOperations

# Should work without modification
```

---

## 6. Implementation Checklist

### Phase 1: Foundation
- [ ] Create `cortex-toolkit/` directory structure
- [ ] Set up `pyproject.toml` with package metadata
- [ ] Implement `cortex_toolkit/context/` (WorkspaceContext, ContextResolver)
- [ ] Implement `cortex_toolkit/utils/` (filesystem, git, subprocess, config)
- [ ] Implement `cortex_toolkit/core/` (brain, agents, operations)
- [ ] Create editable install process
- [ ] Write README with installation instructions
- [ ] Add initial tests
- [ ] Validate installation in CORTEX

### Phase 2: CLI Wrappers
- [ ] Create `cortex_toolkit/cli/` module
- [ ] Migrate `base_wrapper.py` → `cli/base.py`
- [ ] Migrate all wrapper scripts to toolkit
- [ ] Update CORTEX operations to use toolkit imports
- [ ] Add tests for each wrapper
- [ ] Validate all CLI operations work

### Phase 3: Validation & Testing
- [ ] Create `cortex_toolkit/validation/` module
- [ ] Implement `BaseValidator` class
- [ ] Migrate validation scripts
- [ ] Create `cortex_toolkit/testing/` module
- [ ] Implement test runners and coverage tools
- [ ] Add comprehensive tests
- [ ] Validate in NOOR CANVAS

### Phase 4: Documentation & Deployment
- [ ] Create `cortex_toolkit/documentation/` module
- [ ] Migrate doc generation scripts
- [ ] Create `cortex_toolkit/deployment/` module
- [ ] Migrate deployment scripts
- [ ] Add usage examples for each repo
- [ ] Write comprehensive documentation
- [ ] Validate in KSESSIONS

### Phase 5: Monitoring & Analytics
- [ ] Create `cortex_toolkit/monitoring/` module
- [ ] Extract generic monitoring patterns
- [ ] Migrate analytics tools
- [ ] Add visualization utilities
- [ ] Add profiling tools
- [ ] Validate performance

### Phase 6: Migration Framework
- [ ] Create `cortex_toolkit/migration/` module
- [ ] Implement `BaseMigration` class
- [ ] Create SQLite migration runner
- [ ] Add schema validation
- [ ] Implement rollback mechanisms
- [ ] Test with KSESSIONS database

### Phase 7: Legacy Cleanup
- [ ] Archive unused scripts
- [ ] Update all imports across CORTEX
- [ ] Remove duplicate code
- [ ] Clean `scripts/` directory
- [ ] Update all documentation
- [ ] Create migration completion report

---

## 7. Risk Analysis

### Risk 1: Breaking Changes in CORTEX
**Severity:** High  
**Likelihood:** Medium

**Mitigation:**
- Incremental migration (not big bang)
- Keep old scripts until validated
- Comprehensive testing
- Gradual rollout

### Risk 2: Cross-Repo Import Failures
**Severity:** High  
**Likelihood:** Low

**Mitigation:**
- Use editable install (standard practice)
- Test in all repos early
- Clear error messages
- Fallback to legacy if needed

### Risk 3: Version Incompatibility
**Severity:** Medium  
**Likelihood:** Medium

**Mitigation:**
- Semantic versioning
- Compatibility checks in toolkit
- Clear documentation of requirements
- Version pinning in requirements.txt

### Risk 4: Performance Overhead
**Severity:** Low  
**Likelihood:** Low

**Mitigation:**
- Benchmark context resolution (<10ms target)
- Lazy loading where possible
- Profile toolkit overhead
- Optimize hot paths

---

## 8. Timeline

**Total Duration:** 7 weeks (35 working days)

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| Phase 1: Foundation | Week 1 | Installable package |
| Phase 2: CLI Wrappers | Week 2 | All wrappers migrated |
| Phase 3: Validation & Testing | Week 3 | Generic frameworks |
| Phase 4: Documentation & Deployment | Week 4 | Doc & deploy tools |
| Phase 5: Monitoring & Analytics | Week 5 | Monitoring framework |
| Phase 6: Migration Framework | Week 6 | Migration utilities |
| Phase 7: Legacy Cleanup | Week 7 | Clean architecture |

**Milestone Reviews:**
- **Week 2:** Foundation + CLI wrappers complete
- **Week 4:** Generic utilities available for NOOR CANVAS
- **Week 6:** Full toolkit ready for all repos
- **Week 7:** Legacy cleanup and documentation

---

## 9. Future Enhancements (Post-v1.0)

### v1.1: Advanced Features
- Plugin system for custom utilities
- CLI command-line tool (`cortex-toolkit validate`, `cortex-toolkit deploy`)
- Rich terminal output (progress bars, colored logging)
- Configuration wizard

### v1.2: AI Integration
- AI-powered code analysis utilities
- Automated migration generation
- Intelligent validation suggestions
- Context-aware recommendations

### v1.3: Multi-Repo Operations
- Workspace-level operations (run command across all repos)
- Dependency graph visualization across repos
- Cross-repo impact analysis
- Unified monitoring dashboard

---

## 10. Decision Log

### Decision 1: Editable Install vs Path-Based
**Chosen:** Editable install (`pip install -e`)  
**Rationale:** Standard Python practice, better IDE support, clearer dependency management

### Decision 2: Monolithic vs Multi-Package
**Chosen:** Single monolithic package (`cortex-toolkit`)  
**Rationale:** Simpler to maintain, easier to install, better for versioning

### Decision 3: Generic-First vs CORTEX-First
**Chosen:** Generic-first with CORTEX-specific in `core/`  
**Rationale:** Maximizes reusability, clearer boundaries, supports cross-repo goal

### Decision 4: Context Injection vs Auto-Detection
**Chosen:** Context injection (WorkspaceContext parameter)  
**Rationale:** Explicit, testable, works with CORTEX-first + Copilot graceful degradation (from POC)

---

## 11. References

- **Related Documents:**
  - `CORTEX-3.9.1-CONTEXT-INJECTION-PLAN.md` - Context architecture
  - `CORTEX-3.9.1-POC-REPORT.md` - Context POC validation
  - `CORTEX-4.0-WORKSPACE-ARCHITECTURE-PLAN.md` - Future workspace vision
  - `CORTEX-3.X-WORKSPACE-FAILURE-ANALYSIS.md` - Current issues analysis

- **Implementation Examples:**
  - `src/context/workspace_context.py` - WorkspaceContext dataclass
  - `src/context/context_resolver.py` - 5-layer context resolution
  - `scripts/cli_wrappers/base_wrapper.py` - Base wrapper pattern

---

## Appendix A: Script Categorization Matrix

| Script | Category | Generic? | CORTEX-Specific? | Priority | Target Module |
|--------|----------|----------|------------------|----------|---------------|
| `align_wrapper.py` | CLI | ❌ | ✅ | High | `cli/align.py` |
| `base_wrapper.py` | CLI | ✅ | ❌ | Critical | `cli/base.py` |
| `validate_setup.py` | Validation | ✅ | ❌ | High | `validation/setup.py` |
| `migrate_entities_table.py` | Migration | ✅ | ❌ | High | `migration/sqlite.py` |
| `generate_docs_from_code.py` | Documentation | ✅ | ❌ | Medium | `documentation/api_docs.py` |
| `token_pricing_calculator.py` | Monitoring | ✅ | ❌ | Medium | `monitoring/metrics.py` |
| `dependency_graph_generator.py` | Documentation | ✅ | ❌ | Medium | `documentation/diagrams.py` |
| `build_package.py` | Deployment | ✅ | ❌ | High | `deployment/builder.py` |
| `brain_transfer_cli.py` | Core | ❌ | ✅ | Medium | `core/brain.py` |
| `visualize_brain_health.py` | Core | ❌ | ✅ | Low | `core/brain.py` |

*(Full matrix available as separate artifact)*

---

**End of Plan**

**Next Steps:**
1. Review and approve architecture
2. Validate cross-repo usage requirements
3. Begin Phase 1 implementation
4. Create toolkit package structure
