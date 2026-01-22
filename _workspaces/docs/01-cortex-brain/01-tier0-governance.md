# CORTEX TIER 0 - Immutable Governance Rules

**Version:** 1.0 | **Updated:** 2026-01-22 | **Authority:** cortex_brain/tier0/governance/core-rules.yaml v1.0

---

## 🧠 Overview

**TIER 0** is the immutable foundation of the CORTEX Brain. It contains **29 non-negotiable CORE rules** (formerly called SKULL rules) that define operational boundaries, quality standards, and brain protection mechanisms. These rules cannot be overridden, modified, or bypassed under any circumstances.

**Key Characteristics:**
- **Immutability:** Cannot be changed programmatically or through user requests
- **Non-Negotiable:** Apply to ALL orchestrators, ALL requests, ALL phases
- **Highest Precedence:** Override TIER 1, TIER 2, and TIER 3 rules completely
- **Audit-Protected:** Any modification attempt triggers critical alerts and rollback
- **Enforcement:** Strict, with no exceptions or special cases

---

## 📋 The 29 CORE Rules

### Category 1: Orchestration Lifecycle (4 Rules)

#### CORE-001: Incremental Autonomous Execution

**Purpose:** Prevent token limit failures by limiting work to <500 line increments.

**Rule:**
- ALL orchestrators work in small increments (<500 lines per turn)
- State MUST persist between increments
- Token usage capped at 80%

**Why:** LLMs have context windows. Batching too much work loses state, forcing re-analysis and wasting tokens.

**Validation:**
```python
if lines_per_turn > 500:
    raise GovernanceViolation("CORE-001: Incremental execution violated")

if state_persistence.is_lost():
    raise GovernanceViolation("CORE-001: State not persisted between turns")
```

**Example:**
```
Turn 1: Lines 1-500 → State → Checkpoint
Turn 2: Lines 501-1000 → State → Checkpoint
Turn 3: Lines 1001-1500 → State → Checkpoint
```

---

#### CORE-006: Phase -2 Setup Verification

**Purpose:** Ensure ALL dependencies exist before execution starts.

**Rule:**
- Verify dependencies before orchestrator execution
- Dependencies must PASS tests (not just file existence)
- VSCode cache checked
- Governance compliance validated

**Why:** Missing dependencies cause cascading failures mid-execution, wasting tokens and breaking workflows.

**Validation:**
```python
# Check dependencies
for dep in required_dependencies:
    if not dep.file_exists():
        raise GovernanceViolation(f"CORE-006: Missing {dep}")
    
    # Test must pass, not just exist
    if not dep.tests_pass():
        raise GovernanceViolation(f"CORE-006: Dependency tests fail for {dep}")
```

---

#### CORE-007: Phase N+1 Teardown

**Purpose:** Clean up and refactor after completion.

**Rule:**
- Refactor modified files after completion
- Git commit follows pattern
- Unused code removed

**Why:** Prevents technical debt accumulation and keeps codebase clean.

**Commit Pattern:**
```
git commit -m "phase-XX: COMPLETED - refactored"
git commit -m "phase-XX: COMPLETED - audit verified"
```

---

#### CORE-021: Use Orchestrator Scaffolder

**Purpose:** Ensure consistent orchestrator structure.

**Rule:**
- NEW orchestrators created via scaffolder, not manually
- Must extend `BaseOrchestratorV4`
- Must have `@register_with_master` decorator
- Manifest created automatically

**Why:** Prevents architectural inconsistencies and ensures proper integration.

---

### Category 2: Response Formatting (4 Rules)

#### CORE-002: No Summary Files

**Purpose:** Keep documentation clean and prevent drift.

**Rule:**
- Do NOT create `*-summary.md` files
- Do NOT create `*-report.md` files
- Do NOT create `completion-*.md` files
- Summaries go in chat/responses only

**Why:** These files create maintenance burdens and violate documentation minimalism.

**Invalid:** ❌
```
- AC-001-SUMMARY.md
- IMPLEMENTATION-REPORT.md
- completion-status.md
```

---

#### CORE-003: Visual Progress Bars (NOT Code Blocks)

**Purpose:** Use appropriate formatting for progress.

**Rule:**
- Progress MUST use visual bars: █████░░░░░
- NOT code blocks
- Response ≤40 lines

**Why:** Visual formatting is more readable and respects communication minimalism.

**Valid:** ✅
```
Progress: ███████░░░░░░░ 50% [████████/████████]
```

**Invalid:** ❌
```
```
Progress: ###############
```
```

---

#### CORE-004: Minimal Continuation Prompts

**Purpose:** Keep continuation context minimal.

**Rule:**
- `CONTINUATION-PROMPT.md` MUST be <500 tokens
- Max line count: 12
- File size: <2KB
- Use pointer pattern (reference, don't repeat)

**Why:** Reduces context pollution and token waste.

---

#### CORE-030: Mandatory CORTEX Response Headers

**Purpose:** Ensure consistent response formatting and attribution.

**Rule:**
- ALL responses MUST start with standard header
- Format: `## 🧠 CORTEX {operation}`
- Include Author, Phase, Orchestrator, Copyright

**Exact Format:**
```markdown
## 🧠 CORTEX {operation}
**Author:** Asif Hussain | **Phase:** {phase} | **Orchestrator:** {orchestrator} ✅

---
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**
```

**Operation Types:**
- Code Analysis
- Code Review
- Implementation Plan
- AC Execution
- Governance Evaluation
- Debugging
- Response
- Planning
- Testing
- Validation

**No Exceptions:** This is immutable and applies to every response.

---

### Category 3: Portability (1 Rule)

#### CORE-005: No Hardcoded Paths (CRITICAL)

**Purpose:** Ensure code works across all machines and environments.

**Rule:**
- NEVER use hardcoded absolute paths
- Use `src.core.path_resolver.get_project_root()`
- Platform-agnostic path handling required

**Wrong:** ❌
```python
path = "/Users/asifhussain/PROJECTS/CORTEX/cortex_brain"
path = "C:\\Users\\user\\PROJECTS\\CORTEX"
```

**Right:** ✅
```python
from cortex.brain.core.path_resolver import get_project_root
path = get_project_root() / "cortex_brain"
```

---

### Category 4: Development Workflow (4 Rules)

#### CORE-008: TDD Enforcement (RED → GREEN → REFACTOR)

**Purpose:** Ensure code quality through test-first development.

**Rule:**
- Tests MUST exist BEFORE implementation
- Test fails initially (RED phase)
- Implementation makes test pass (GREEN phase)
- Refactor with tests passing (REFACTOR phase)

**Why:** TDD catches requirements errors early and ensures testability.

**Workflow:**
```
1. RED:     Write test (should fail)
2. GREEN:   Write minimal implementation (test passes)
3. REFACTOR: Improve code (tests still pass)
4. GIT:     Checkpoint after each phase
```

---

#### CORE-009: Files in Plan Folders

**Purpose:** Organize plan artifacts logically.

**Rule:**
- Plan artifacts MUST live in plan folder structure
- No plan files in workspace root
- Structure: `plan_folder/artifacts/`, `plan_folder/tracking/`

**Why:** Prevents root directory clutter and ensures discoverability.

---

#### CORE-010: Script Consolidation

**Purpose:** Prevent duplicate script functionality.

**Rule:**
- Scripts must be cataloged
- Duplicate detection runs
- Similar scripts consolidated

**Why:** Reduces maintenance burden and prevents inconsistencies.

---

#### CORE-019: TDD-Master Routing (Route Through TDD-Master)

**Purpose:** Ensure implementation requests go through proper orchestration.

**Rule:**
- `"implement X"` routes to TDD-Master orchestrator
- `"build X"` routes to TDD-Master orchestrator
- Never write code directly; always route to orchestrator

**Why:** Ensures TDD compliance, governance checking, and audit trails.

---

### Category 5: Architecture Integrity (7 Rules)

#### CORE-014: SOLID Principles Required

**Purpose:** Ensure maintainable, extensible code architecture.

**Rule:**
- Code MUST follow SOLID principles:
  - **S:** Single Responsibility - one reason to change
  - **O:** Open/Closed - open for extension, closed for modification
  - **L:** Liskov Substitution - subtypes are substitutable
  - **I:** Interface Segregation - many specific interfaces
  - **D:** Dependency Inversion - depend on abstractions

**Validation:**
```python
@dataclass
class AnalysisResult:
    single_responsibility: bool
    open_closed: bool
    liskov_substitution: bool
    interface_segregation: bool
    dependency_inversion: bool
```

---

#### CORE-018: YAML-First Design

**Purpose:** Maintain machine-readable configurations.

**Rule:**
- Plans and configs MUST use YAML, not markdown
- Machine-readable format required
- Exception: README.md, docs/ only

**Why:** Enables tooling, validation, and automation.

**Invalid:** ❌
```
- PLAN-DOCUMENT.md (config in markdown)
```

**Valid:** ✅
```
- plan-document.yaml (config in YAML)
- README.md (documentation okay)
```

---

#### CORE-020: No Markdown in Brain

**Purpose:** Keep cortex_brain configuration-only.

**Rule:**
- `cortex_brain/` MUST be YAML/JSON only
- No `.md` files allowed in brain
- Exception: None (absolute rule)

**Why:** Brain is configuration, not documentation. Keeps it clean and machine-readable.

---

#### CORE-022: Kebab-Case File Naming with 25-Char Limit

**Purpose:** Ensure consistent, self-documenting file naming.

**Rule:**
- Kebab-case only: lowercase with hyphens
- Max 25 characters including extension
- Use semantic acronyms to stay within limit
- Names must be self-documenting

**Acronym Dictionary (Semantic):**
```
cfg: config           mgr: manager       exec: execution
db: database          util: utility      impl: implementation
svc: service          gov: governance    sync: synchronization
rpt: report           anal: analysis     ver: verification
```

**Valid Examples:** ✅
```
- cortex-vacuum-exec.py      (20 chars)
- cortex-gov-rules.yaml      (19 chars)
- plan-ac-tracker.db         (16 chars)
- phase-completion-rpt.md    (21 chars)
```

**Invalid Examples:** ❌
```
- cortex_vacuum_executor.py                    (underscores)
- cortex-vacuum-implementation-executor.py     (41 chars, too long)
- CortexVacuumExecutor.py                      (PascalCase)
```

---

#### CORE-024: MCP Tool Decorator Required

**Purpose:** Ensure all tools are registered and discoverable.

**Rule:**
- ALL MCP tools MUST use `@mcp_tool` decorator
- Registered in manifest
- No manual registration

**Why:** Prevents unregistered tools and ensures discoverability.

**Valid:** ✅
```python
@mcp_tool
def my_tool(param: str) -> Result[str]:
    """Tool description."""
    return Ok(result)
```

---

#### CORE-028: Intelligent Kebab-Case Naming (25-Char Limit)

**Purpose:** Strategic naming balancing clarity and conciseness.

**Rule:**
- Use kebab-case with semantic acronyms
- Order: `[domain]-[component]-[purpose].[ext]`
- Max 25 chars total
- Avoid articles (a, the), conjunctions (and), prepositions

**Validation:**
```python
pattern = r'^[a-z0-9]([a-z0-9-]*[a-z0-9])?(\.[a-z0-9]+)?$'
assert len(filename) <= 25
assert re.match(pattern, filename)
```

---

### Category 6: Quality Gates (7 Rules)

#### CORE-011: Python Type Hints Required

**Purpose:** Enable static analysis and catch type errors early.

**Rule:**
- ALL Python functions MUST have complete type hints
- Parameters require type hints
- Return types specified
- No bare `Any` types

**Why:** Type hints catch errors at edit time, not runtime.

**Valid:** ✅
```python
def process_data(items: List[str], count: int) -> Result[Dict[str, int]]:
    """Process items and return results."""
    pass
```

**Invalid:** ❌
```python
def process_data(items, count):  # No type hints
    return data

def process_data(items: Any, count: Any) -> Any:  # Bare Any
    return data
```

---

#### CORE-012: Google-Style Docstrings Required

**Purpose:** Ensure all public APIs are documented.

**Rule:**
- ALL public functions/classes MUST have docstrings
- Google-style format required
- Args/Returns/Raises sections
- One-line summary, detailed description

**Format:**
```python
def my_function(param1: str, param2: int) -> Result[bool]:
    """
    Brief summary here.
    
    More detailed description if needed.
    
    Args:
        param1: Description of param1.
        param2: Description of param2.
    
    Returns:
        Result[bool]: True if successful, Err with message otherwise.
    
    Raises:
        GovernanceViolation: If governance rules violated.
    """
    pass
```

---

#### CORE-013: Explicit Error Handling

**Purpose:** Prevent silent failures and cryptic errors.

**Rule:**
- NO bare `except:` clauses
- NO catching generic `Exception`
- Specific exception types only
- Error context preserved

**Invalid:** ❌
```python
try:
    risky_operation()
except:  # Bare except - FORBIDDEN
    pass

except Exception as e:  # Too generic - FORBIDDEN
    log.error("Error occurred")
```

**Valid:** ✅
```python
try:
    risky_operation()
except FileNotFoundError as e:
    logger.error(f"File not found: {e.filename}")
except ValueError as e:
    logger.error(f"Invalid value: {e}")
```

---

#### CORE-015: PEP 8 Import Organization

**Purpose:** Maintain consistent, readable import structure.

**Rule:**
- 3 import sections: stdlib, third-party, local
- Blank line between sections
- Sorted alphabetically within sections
- No wildcard imports

**Valid:** ✅
```python
import logging
import threading
from pathlib import Path
from typing import Dict, List, Optional

import requests
import yaml

from cortex.brain.core.result import Result, Ok, Err
from cortex.brain.core.governance_registry import GovernanceRegistry
```

**Invalid:** ❌
```python
from cortex.brain.core import *  # Wildcard - FORBIDDEN
import yaml
import logging
from typing import *  # Wildcard - FORBIDDEN
```

---

#### CORE-016: Black Formatting

**Purpose:** Enforce consistent code style.

**Rule:**
- Python code MUST be formatted with Black
- Line length: 100 characters
- Double quotes
- Trailing commas in multi-line structures

**Validation:**
```bash
black --line-length=100 --check cortex/
```

---

#### CORE-023: Pre-Commit File Validation

**Purpose:** Catch errors before commit.

**Rule:**
- Modified files MUST pass type-specific validation
- HTML: html5lib + WCAG AA
- YAML: schema validation
- Python: pytest pass

**Why:** Prevents broken commits.

---

#### CORE-025: Result[T] Pattern Required

**Purpose:** Enable explicit error handling without exceptions.

**Rule:**
- Functions MUST return `Result[T]`
- Use `Ok(value)` for success
- Use `Err(message)` for failure
- Check `is_ok()` before `unwrap()`

**Why:** Explicit error handling is safer than exceptions.

**Valid:** ✅
```python
def risky_operation() -> Result[str]:
    if error_condition:
        return Err("Error description")
    return Ok("Success result")

# Usage
result = risky_operation()
if result.is_ok():
    value = result.unwrap()
else:
    error = result.error()
```

---

### Category 7: Security & Privacy (1 Rule)

#### CORE-017: Strict Governance Enforcement

**Purpose:** Ensure governance rules are never bypassed.

**Rule:**
- ALL rules enforced strictly
- No overrides allowed
- All violations logged
- Execution halted on violation

**Why:** Without strict enforcement, governance becomes optional.

---

### Category 8: Audit & Compliance (3 Rules)

#### CORE-026: Git Checkpoint Before Modify

**Purpose:** Enable efficient rollback on failures.

**Rule:**
- Git checkpoint BEFORE every major action
- Checkpoint before AC-ID start
- Checkpoint before file modification
- Commit after successful test pass

**Commit Patterns:**
```
git commit -m "checkpoint: before AC-XXX-XX"
git commit -m "checkpoint: pre-modify"
git commit -m "AC-XXX-XX: [description] - tests passing"
git commit -m "phase-XX: COMPLETED - audit verified"
```

---

#### CORE-027: Audit Trail Verification

**Purpose:** Ensure phase completion can be verified.

**Rule:**
- Phase completion validated by audit trail
- Each AC-ID has 3+ audit entries:
  - `AC_START`
  - `AC_EXECUTE`
  - `AC_COMPLETE`
- Hash chain integrity verified
- No phase lock without audit verification

**Audit Structure:**
```
AC-ID: AC-FR-001-01
├─ AC_START:    [timestamp, audit_id, hash]
├─ AC_EXECUTE:  [timestamp, audit_id, hash]
├─ AC_COMPLETE: [timestamp, audit_id, hash]
└─ Verification: ✅ Hash chain valid
```

---

#### CORE-029: Documentation Drift Prevention

**Purpose:** Ensure features are documented before phase lock.

**Rule:**
- User-facing features MUST be documented
- Documentation required in prompts BEFORE phase lock
- Features + documentation go together
- Companion AC-IDs for documentation

**Pattern:**
```
Feature AC:        AC-FR-X-01: Implement feature
Companion AC:      AC-DOC-X-01: Document in CORTEX.prompt.md

Both required for phase lock.
```

---

## 🎯 Rule Precedence & Enforcement

### Precedence Hierarchy

When rules conflict (they shouldn't, but theoretically):

```
TIER 0 Rules (Immutable) > All other rules
Within TIER 0:
  1. Security/Privacy rules (CORE-017)
  2. Portability rules (CORE-005)
  3. Type/Format rules (CORE-011, CORE-012)
  4. Workflow rules (CORE-008, CORE-019)
  5. Formatting rules (CORE-002, CORE-003, CORE-004, CORE-030)
```

---

## 🔒 Immutability Mechanisms

### 1. File-Level Protection

```yaml
# cortex_brain/tier0/governance/core-rules.yaml
# READ-ONLY FILE - DO NOT EDIT

# Pre-commit hook prevents modifications
# Schema validation on any load attempt
# Hash verification at startup
```

### 2. Runtime Immutability

```python
class MutationGuard:
    """Prevents programmatic modification of TIER 0 rules."""
    
    @classmethod
    def protect_rule(cls, rule: GovernanceRule) -> None:
        """Make rule immutable."""
        rule._immutable = True
        rule._original_hash = compute_hash(rule)
    
    @classmethod
    def verify_integrity(cls, rule: GovernanceRule) -> bool:
        """Verify rule hasn't been modified."""
        if not rule._immutable:
            raise GovernanceViolation("Rule not protected")
        
        current_hash = compute_hash(rule)
        if current_hash != rule._original_hash:
            raise GovernanceViolation("Rule has been modified!")
        
        return True
```

### 3. Git-Level Protection

```bash
# Pre-commit hook
if modified_file in TIER0_PROTECTED_FILES:
    echo "ERROR: Cannot modify TIER 0 files"
    exit 1

# Branch protection
# TIER 0 changes require:
# - Code review
# - All tests pass
# - Explicit approval from governance team
```

---

## 📊 Violation Detection & Response

### Automatic Detection

```python
class GovernanceEnforcer:
    def check_rules(self, request: Request) -> Result[None]:
        """Check all applicable TIER 0 rules."""
        
        active_rules = self.filter_by_context(request)
        
        for rule in active_rules:
            if not rule.validate(request):
                return Err(
                    f"TIER 0 Violation: {rule.rule_id} - {rule.description}"
                )
        
        return Ok(None)
    
    def on_violation(self, violation: GovernanceViolation) -> None:
        """Handle rule violation."""
        
        # 1. Log immediately (CRITICAL level)
        logger.critical(f"GOVERNANCE VIOLATION: {violation}")
        
        # 2. Audit trail
        audit_logger.record(
            operation="GOVERNANCE_VIOLATION",
            violation_rule=violation.rule_id,
            timestamp=datetime.now(),
            hash=compute_hash(violation)
        )
        
        # 3. Escalate
        raise GovernanceViolationEvent(violation)
        
        # 4. Halt execution
        self.halt_orchestrator()
```

---

## ✅ Compliance Checklist

Before any code submission:

- [ ] All functions have type hints (CORE-011)
- [ ] All public functions have docstrings (CORE-012)
- [ ] No bare `except` clauses (CORE-013)
- [ ] No hardcoded paths (CORE-005)
- [ ] Files use kebab-case, <25 chars (CORE-022, CORE-028)
- [ ] Functions return Result[T] (CORE-025)
- [ ] Tests written before implementation (CORE-008)
- [ ] Response starts with CORTEX header (CORE-030)
- [ ] YAML configs used, no .md in brain (CORE-018, CORE-020)
- [ ] Git checkpoints created (CORE-026)
- [ ] Audit trail entries logged (CORE-027)

---

## 📈 Metrics

| Metric | Value |
|--------|-------|
| Total TIER 0 Rules | 29 CORE |
| Test Coverage | 404 tests, 100% |
| Enforcement Mode | Strict (no override) |
| Average Violation Response Time | <10ms |
| Immutability Verification | 100% on load |

---

## 🔗 Related Documentation

- [Brain Index](00-brain-index.md) - System overview
- [TIER 1 Governance](02-tier1-acceptance.md) - AC-ID tracking
- [TIER 2 Templates](03-tier2-response-templates.md) - Response formatting
- [TIER 3 Knowledge](04-tier3-knowledge.md) - Domain knowledge
- [Governance Registry](../../cortex/brain/core/governance_registry.py) - Implementation

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

