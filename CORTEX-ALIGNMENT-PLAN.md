# CORTEX Alignment Plan - Comprehensive Implementation

**Date Created:** November 6, 2025  
**Status:** 📋 READY FOR EXECUTION  
**Estimated Duration:** 28-36 hours (3.5-4.5 days)  
**Priority:** CRITICAL - Establishes impenetrable knowledge boundaries

---

## 🎯 Executive Summary

**Objective:** Implement complete knowledge isolation between CORTEX core intelligence and application-specific knowledge (KSESSIONS, NOOR, etc.) through namespace/scope boundaries, complete pending features, and establish automated protection.

**Current State:**
- ✅ Groups 1-4B complete (409/409 tests passing)
- ✅ Tier 0-3 data storage operational
- ✅ 10 specialist agents functional
- ❌ NO knowledge boundary enforcement (contamination risk active)
- ❌ Brain Protector designed but not integrated
- ❌ Cleanup/housekeeping not implemented
- ❌ KSESSIONS simulation data exists but isolated (safe)

**Target State:**
- ✅ Impenetrable boundary: `scope='generic'` (CORTEX) vs `scope='application'` (KSESSIONS/NOOR)
- ✅ Namespace tagging: Multi-app support with automatic classification
- ✅ Brain Protector: Automated architectural deviation prevention
- ✅ Cleanup automation: Pattern decay, consolidation, anomaly removal
- ✅ Enhanced amnesia: Surgical deletion by scope, preserves CORTEX intelligence
- ✅ 100% test coverage on all new boundary enforcement features

---

## 📊 Phases Overview

| Phase | Name | Duration | Priority | Dependencies |
|-------|------|----------|----------|--------------|
| **Phase 1** | Namespace/Scope Schema Migration | 3-4 hrs | CRITICAL | None |
| **Phase 2** | Boundary Enforcement Implementation | 4-5 hrs | CRITICAL | Phase 1 |
| **Phase 3** | Brain Protector Integration | 4-6 hrs | HIGH | Phase 2 |
| **Phase 4** | Cleanup/Housekeeping Automation | 6-8 hrs | HIGH | Phase 2 |
| **Phase 5** | Enhanced BRAIN Amnesia | 2-3 hrs | MEDIUM | Phase 1, 2 |
| **Phase 6** | Alignment Testing & Validation | 4-5 hrs | CRITICAL | All |
| **Phase 7** | Documentation & User Guide | 3-4 hrs | MEDIUM | All |
| **Phase 8** | Minor Fixes & Stragglers | 2-3 hrs | LOW | None |

**Total:** 28-38 hours

---

## 🔍 Phase 1: Namespace/Scope Schema Migration (3-4 hours)

### Objectives
- Add `scope` and `namespaces` columns to Tier 2 patterns table
- Classify existing patterns (generic vs application-specific)
- Ensure backward compatibility with existing data

### Tasks

#### Task 1.1: Schema Migration Script (1.5 hrs)
**File:** `CORTEX/src/tier2/migrate_add_boundaries.py`

**Requirements:**
1. Create migration script with:
   - `ALTER TABLE patterns ADD COLUMN scope TEXT DEFAULT 'generic' CHECK (scope IN ('generic', 'application'))`
   - `ALTER TABLE patterns ADD COLUMN namespaces TEXT DEFAULT '["CORTEX-core"]'`
   - `CREATE INDEX idx_scope ON patterns(scope)`
   - `CREATE INDEX idx_namespaces ON patterns(namespaces)`

2. Pattern classification logic:
   ```python
   def classify_pattern(pattern_id: str, title: str, content: str, source: str) -> tuple[str, List[str]]:
       """
       Classify pattern as generic or application-specific.
       
       Rules:
       - Contains file paths like "SPA/", "KSESSIONS/", "NOOR/" → application
       - Source from simulations/ksessions/ → application, namespace=[KSESSIONS]
       - Generic workflow names (test_first, SOLID) → generic, namespace=[CORTEX-core]
       - Protection/governance patterns → generic, namespace=[CORTEX-core]
       """
   ```

3. Rollback capability (save backup before migration)

**Deliverables:**
- `migrate_add_boundaries.py` (200 lines)
- Backup creation before ALTER TABLE
- Classification statistics report

#### Task 1.2: Update KnowledgeGraph Class (1 hr)
**File:** `CORTEX/src/tier2/knowledge_graph.py`

**Changes:**
```python
def add_pattern(
    self,
    pattern_id: str,
    title: str,
    content: str,
    pattern_type: PatternType,
    confidence: float = 1.0,
    scope: str = "generic",  # NEW: Boundary enforcement
    namespaces: Optional[List[str]] = None,  # NEW: Multi-app support
    tags: Optional[List[str]] = None,
    source: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Pattern:
    """Add pattern with namespace isolation."""
    if namespaces is None:
        namespaces = ["CORTEX-core"]
    
    # Validate scope
    if scope not in ["generic", "application"]:
        raise ValueError(f"Invalid scope: {scope}")
    
    # Store namespaces as JSON
    namespaces_json = json.dumps(namespaces)
    
    # ... rest of insertion logic
```

**Deliverables:**
- Updated `add_pattern()` signature with scope/namespaces
- Updated `Pattern` dataclass with new fields
- Validation logic for scope enum

#### Task 1.3: Migrate Existing Patterns (30 min)
**Execution:** Run migration script on live databases

**Steps:**
1. Backup `cortex-brain/tier2/knowledge_graph.db`
2. Run `python CORTEX/src/tier2/migrate_add_boundaries.py`
3. Verify classification results
4. Check pattern counts (generic vs application)

**Expected Results:**
- All patterns classified
- KSESSIONS simulation patterns tagged with `scope='application', namespaces=['KSESSIONS']`
- CORTEX core patterns tagged with `scope='generic', namespaces=['CORTEX-core']`

#### Task 1.4: Testing (1 hr)
**File:** `CORTEX/tests/tier2/test_namespace_boundaries.py`

**Test Cases:**
```python
def test_add_pattern_with_scope():
    """Verify scope and namespaces stored correctly."""

def test_scope_validation():
    """Reject invalid scope values."""

def test_namespace_json_storage():
    """Verify namespaces stored as JSON array."""

def test_default_values():
    """Verify defaults: scope='generic', namespaces=['CORTEX-core']."""

def test_migration_classification():
    """Verify existing patterns classified correctly."""
```

**Target:** 12 tests, 100% coverage on new functionality

---

## 🛡️ Phase 2: Boundary Enforcement Implementation (4-5 hours)

### Objectives
- Enforce namespace tagging at all knowledge entry points
- Implement namespace-aware search queries
- Validate boundary integrity

### Tasks

#### Task 2.1: Update Brain Updater (2 hrs)
**File:** `prompts/internal/brain-updater.md`

**Requirements:**
Add automatic scope detection when processing events:

```markdown
### Event Processing with Namespace Tagging

**Rule 1: CORTEX Modifications**
When event indicates CORTEX system modification:
- `scope = "generic"`
- `namespaces = ["CORTEX-core"]`

**Triggers:**
- File paths: `CORTEX/src/*`, `prompts/internal/*`, `governance/*`
- Event types: `tier_migration`, `governance_update`, `agent_modification`

**Rule 2: Application Work**
When event indicates application-specific work:
- `scope = "application"`
- `namespaces = [detected_application]`

**Detection:**
- File paths containing `KSESSIONS/`, `NOOR/`, `SPA/`
- Simulation data from `cortex-brain/simulations/{app}/`
- Event source: `crawler-ksessions`, `crawler-noor`

**Rule 3: Ambiguous Patterns**
When generic pattern discovered during application work:
- Examples: "test_first_workflow", "SOLID_refactor", "semantic_commit"
- `scope = "generic"`
- `namespaces = ["CORTEX-core", "{current_application}"]` (multi-namespace)
```

**Deliverables:**
- Updated brain-updater.md with scope detection rules
- Automatic namespace classification logic
- Examples for each classification type

#### Task 2.2: Namespace-Aware Search (1.5 hrs)
**File:** `CORTEX/src/tier2/knowledge_graph.py`

**New Methods:**
```python
def search_patterns(
    self,
    query: str,
    limit: int = 10,
    current_namespace: Optional[str] = None,
    include_generic: bool = True
) -> List[Pattern]:
    """
    Search patterns with namespace boosting.
    
    Priority:
    1. Current namespace patterns (weight 2.0)
    2. Generic patterns (weight 1.5)
    3. Other namespace patterns (weight 0.5)
    """
    
def get_patterns_by_namespace(self, namespace: str) -> List[Pattern]:
    """Get all patterns for specific namespace."""
    
def get_generic_patterns(self) -> List[Pattern]:
    """Get all scope='generic' patterns."""
```

**Deliverables:**
- Namespace-aware FTS5 search with boosting
- Filter methods for namespace isolation
- Performance: maintain <150ms search time

#### Task 2.3: Context Injector Updates (30 min)
**File:** `CORTEX/src/context_injector.py`

**Changes:**
- Detect current working application from file paths
- Pass namespace context to search queries
- Prioritize relevant patterns

**Example:**
```python
def inject_tier2_context(self, request: AgentRequest) -> str:
    """Inject Tier 2 knowledge graph patterns."""
    # Detect namespace from request context
    current_app = self._detect_application(request.file_path)
    namespace = "CORTEX-core" if current_app is None else current_app
    
    # Search with namespace priority
    patterns = self.tier2.search_patterns(
        query=request.prompt,
        current_namespace=namespace,
        include_generic=True
    )
```

**Deliverables:**
- Automatic namespace detection
- Context-aware pattern retrieval

#### Task 2.4: Testing (1 hr)
**File:** `CORTEX/tests/tier2/test_namespace_search.py`

**Test Cases:**
```python
def test_search_with_namespace_boosting():
    """Verify current namespace patterns ranked higher."""

def test_generic_patterns_always_included():
    """Verify generic patterns available across namespaces."""

def test_cross_namespace_isolation():
    """Verify KSESSIONS patterns don't contaminate NOOR searches."""

def test_multi_namespace_patterns():
    """Verify patterns shared across namespaces."""
```

**Target:** 15 tests, 100% coverage

---

## 🧠 Phase 3: Brain Protector Integration (4-6 hours)

### Objectives
- Wire brain-protector.md into agent orchestration pipeline
- Intercept CORTEX modification requests
- Implement automated challenge protocol

### Tasks

#### Task 3.1: Intent Router Integration (2 hrs)
**File:** `prompts/internal/intent-router.md`

**Requirements:**
Add Brain Protector invocation for CORTEX modifications:

```markdown
### Brain Protector Invocation (NEW)

**Trigger:** Any request that modifies CORTEX system files

**Detection Patterns:**
- File modifications in: `CORTEX/src/*`, `prompts/internal/*`, `governance/rules/*`
- Keywords: "modify tier", "change governance", "bypass TDD", "skip tests"
- Event types: `governance_rule_change`, `tier_boundary_violation`, `protection_override`

**Workflow:**
1. Detect CORTEX modification intent
2. Route to: `#file:prompts/internal/brain-protector.md`
3. Brain Protector analyzes request against 6 protection layers
4. If SAFE → Allow modification
5. If RISKY → Present challenge with alternatives
6. If BLOCKED → Require explicit override + justification

**Protection Layers Checked:**
1. Instinct Immutability (Tier 0 governance rules)
2. Tier Boundary Integrity
3. SOLID Compliance
4. Hemisphere Specialization
5. Knowledge Quality
6. Commit Integrity
```

**Deliverables:**
- Updated intent-router.md with Brain Protector routing
- Modification detection logic
- Challenge/allow/block decision tree

#### Task 3.2: Brain Protector Automation (2-3 hrs)
**File:** `CORTEX/src/tier0/brain_protector.py` (NEW)

**Requirements:**
Create Python implementation of protection algorithms:

```python
class BrainProtector:
    """
    Automates architectural protection challenges.
    
    Implements 6 protection layers from brain-protector.md:
    1. Instinct Immutability
    2. Tier Boundary Protection
    3. SOLID Compliance
    4. Hemisphere Specialization
    5. Knowledge Quality
    6. Commit Integrity
    """
    
    def analyze_request(self, request: ModificationRequest) -> ProtectionResult:
        """
        Analyze modification request against all protection layers.
        
        Returns:
            ProtectionResult with severity (SAFE, WARNING, BLOCKED)
        """
        
    def generate_challenge(self, violations: List[Violation]) -> Challenge:
        """
        Generate challenge with:
        - Threat description
        - Risk assessment
        - Safe alternatives
        - Override requirements
        """
```

**Deliverables:**
- `brain_protector.py` (300 lines)
- 6 protection layer implementations
- Challenge generation logic
- Integration with governance engine

#### Task 3.3: Corpus Callosum Logging (1 hr)
**File:** `cortex-brain/corpus-callosum/protection-events.jsonl`

**Requirements:**
Log all Brain Protector challenges and decisions:

```json
{
  "timestamp": "2025-11-06T14:30:00Z",
  "event": "brain_protector_challenge",
  "request": {
    "intent": "bypass_tdd",
    "file": "CORTEX/src/tier2/knowledge_graph.py",
    "justification": "Quick fix for production bug"
  },
  "violations": [
    {
      "layer": "instinct_immutability",
      "rule": "TDD_ENFORCEMENT",
      "severity": "BLOCKED"
    }
  ],
  "decision": "BLOCKED",
  "alternative_suggested": "Write test first, then fix",
  "user_override": false
}
```

**Deliverables:**
- Structured logging to corpus-callosum
- Challenge audit trail
- Override tracking

#### Task 3.4: Testing (1 hr)
**File:** `CORTEX/tests/tier0/test_brain_protector.py`

**Test Cases:**
```python
def test_detects_tdd_bypass_attempt():
    """Verify BLOCKS code without tests."""

def test_detects_tier_boundary_violation():
    """Verify BLOCKS conversations in Tier 0."""

def test_detects_solid_violation():
    """Verify WARNS on 500+ line God Object."""

def test_generates_challenge_with_alternatives():
    """Verify challenge includes safe alternatives."""

def test_allows_safe_modifications():
    """Verify allows compliant changes."""
```

**Target:** 18 tests, 100% coverage on protection logic

---

## 🧹 Phase 4: Cleanup/Housekeeping Automation (6-8 hours)

### Objectives
- Complete cleanup_hook.py implementation
- Automate pattern decay and consolidation
- Implement automatic triggers

### Tasks

#### Task 4.1: Complete cleanup_hook.py (3-4 hrs)
**File:** `CORTEX/src/tier0/cleanup_hook.py`

**Current State:** Skeleton with placeholders  
**Target State:** Fully operational automation

**Requirements:**

```python
class CleanupHook:
    """Smart cleanup automation for CORTEX BRAIN health."""
    
    def analyze_file(self, file_path: Path) -> ArchiveDecision:
        """
        Analyze file for archival eligibility.
        
        Rules:
        - Age > 90 days AND no recent access → SAFE_AUTO
        - Phase-plan artifacts → SAFE_AUTO
        - Active development files → KEEP
        - System files (governance, agents) → REQUIRE_APPROVAL
        """
        
    def archive_file(self, file_path: Path) -> None:
        """
        Archive file with Git-aware reference updates.
        
        Steps:
        1. Check Git status (abort if uncommitted)
        2. Create archive with timestamp
        3. Update ARCHIVE-INDEX.md with metadata
        4. Run reference_updater to fix broken links
        5. Commit archive action
        """
        
    def execute_pattern_decay(self) -> DecayReport:
        """
        Remove stale patterns from knowledge graph.
        
        Rules:
        - confidence < 0.30 → DELETE
        - access_count = 0 AND age > 90 days → DELETE
        - is_pinned = true → KEEP (never decay)
        """
        
    def consolidate_patterns(self) -> ConsolidationReport:
        """
        Merge similar patterns to reduce redundancy.
        
        Algorithm:
        1. Find patterns with 60-84% similarity (FTS5 search)
        2. If same pattern_type and similar confidence:
           - Merge content (keep highest confidence version)
           - Combine namespaces
           - Update access_count (sum)
           - Delete duplicate
        3. Log consolidation event
        """
```

**Deliverables:**
- Complete `analyze_file()` implementation (100 lines)
- Complete `archive_file()` with Git awareness (150 lines)
- Complete `execute_pattern_decay()` (80 lines)
- Complete `consolidate_patterns()` with similarity detection (120 lines)

#### Task 4.2: Automatic Triggers (1 hr)
**File:** `CORTEX/src/tier0/cleanup_scheduler.py` (NEW)

**Requirements:**
```python
class CleanupScheduler:
    """Triggers cleanup automation based on thresholds."""
    
    def check_should_run(self) -> bool:
        """
        Determine if cleanup should run.
        
        Triggers:
        - Event count > 50 since last cleanup
        - 24 hours since last cleanup
        - Manual invocation via cortex.md command
        """
        
    def run_cleanup_cycle(self) -> CleanupReport:
        """
        Execute full cleanup cycle:
        1. Pattern decay
        2. Pattern consolidation
        3. File archival (phase-plans, old artifacts)
        4. Generate report
        """
```

**Deliverables:**
- Automatic trigger logic
- Scheduled cleanup execution
- Integration with Tier 2 APIs

#### Task 4.3: Anomaly Detection (1-2 hrs)
**File:** `CORTEX/src/tier2/anomaly_detector.py` (NEW)

**Requirements:**
```python
class AnomalyDetector:
    """Detects suspicious patterns in knowledge graph."""
    
    def detect_confidence_anomalies(self) -> List[Anomaly]:
        """
        Find patterns with anomalous confidence.
        
        Rules:
        - Single event confidence > 0.90 (suspicious)
        - Confidence increased by >0.30 in single update
        - Occurrences < 3 but confidence > 0.85
        """
        
    def detect_relationship_anomalies(self) -> List[Anomaly]:
        """
        Find suspicious pattern relationships.
        
        Rules:
        - Contradicts relationship with high strength (data conflict)
        - Circular relationships (A extends B extends C extends A)
        - Orphaned patterns (no relationships, low confidence)
        """
```

**Deliverables:**
- Anomaly detection algorithms (200 lines)
- Automatic flagging of suspicious patterns
- Integration with cleanup automation

#### Task 4.4: Testing (1 hr)
**File:** `CORTEX/tests/tier0/test_cleanup_automation.py`

**Test Cases:**
```python
def test_pattern_decay_removes_low_confidence():
    """Verify patterns <0.30 confidence deleted."""

def test_pattern_decay_preserves_pinned():
    """Verify is_pinned=true patterns never decay."""

def test_consolidates_similar_patterns():
    """Verify 70% similar patterns merged."""

def test_archives_old_phase_plans():
    """Verify >90 day phase-plans archived."""

def test_automatic_triggers():
    """Verify cleanup runs after 50 events."""
```

**Target:** 20 tests, 100% coverage

---

## 🔄 Phase 5: Enhanced BRAIN Amnesia (2-3 hours)

### Objectives
- Replace heuristic-based amnesia with scope-based surgical deletion
- Preserve all CORTEX core intelligence
- Implement namespace-aware reset

### Tasks

#### Task 5.1: Update brain-amnesia.md (1 hr)
**File:** `prompts/internal/brain-amnesia.md`

**Changes:**
Replace guesswork classification with database-driven approach:

```markdown
### Step 2: Execute Surgical Amnesia (NEW APPROACH)

**Tier 2 Knowledge Graph - Scope-Based Deletion:**

```sql
-- Remove ONLY application-specific patterns
DELETE FROM patterns WHERE scope = 'application';

-- CORTEX core intelligence PRESERVED:
-- - All scope='generic' patterns remain
-- - Protection config intact
-- - Governance patterns intact
-- - Test patterns intact
```

**Benefits:**
- ✅ NO GUESSWORK - Database enforces boundary
- ✅ 100% CORTEX intelligence preserved
- ✅ Surgical precision - only app data removed
- ✅ Rollback safe - generic patterns never touched

**Namespace-Aware Amnesia (Advanced):**

```sql
-- Remove specific application namespace only
DELETE FROM patterns 
WHERE namespaces LIKE '%"KSESSIONS"%' 
  AND scope = 'application';

-- Keeps:
-- - CORTEX-core patterns
-- - Other application patterns (NOOR)
-- - Multi-namespace generic patterns
```
```

**Deliverables:**
- Updated amnesia algorithm using scope column
- Namespace-specific amnesia option
- Pre/post statistics reporting

#### Task 5.2: Update Amnesia Script (1 hr)
**File:** `scripts/brain-amnesia.ps1`

**Changes:**
```powershell
# OLD: Heuristic-based pattern matching
$appWorkflows = $kg.workflow_patterns | Where-Object { 
    $_.description -like "*NoorCanvas*" -or 
    $_.id -like "*blazor*" 
}

# NEW: Database-driven scope filtering
$conn = New-Object System.Data.SQLite.SQLiteConnection
$conn.ConnectionString = "Data Source=$kgPath"
$conn.Open()

$cmd = $conn.CreateCommand()
$cmd.CommandText = "DELETE FROM patterns WHERE scope = 'application'"
$deletedCount = $cmd.ExecuteNonQuery()

Write-Host "Removed $deletedCount application-specific patterns"
Write-Host "CORTEX core intelligence preserved (scope='generic')"
```

**Deliverables:**
- Updated PowerShell script with SQLite operations
- Namespace-specific amnesia parameter: `-Namespace "KSESSIONS"`
- Enhanced reporting (scope breakdown)

#### Task 5.3: Testing (30 min)
**File:** `CORTEX/tests/tier2/test_amnesia.py` (NEW)

**Test Cases:**
```python
def test_amnesia_removes_only_application_scope():
    """Verify scope='application' deleted, scope='generic' preserved."""

def test_namespace_specific_amnesia():
    """Verify can remove KSESSIONS while keeping NOOR."""

def test_amnesia_preserves_protection_config():
    """Verify protection settings never deleted."""

def test_amnesia_statistics_accurate():
    """Verify before/after counts match actual deletions."""
```

**Target:** 8 tests, 100% coverage

---

## ✅ Phase 6: Alignment Testing & Validation (4-5 hours)

### Objectives
- Validate boundary enforcement across all tiers
- Ensure 100% test coverage on new features
- Performance regression testing

### Tasks

#### Task 6.1: Integration Tests (2 hrs)
**File:** `CORTEX/tests/integration/test_knowledge_boundaries.py` (NEW)

**Test Scenarios:**
```python
class TestKnowledgeBoundaryIntegration:
    """End-to-end boundary enforcement validation."""
    
    def test_e2e_cortex_modification_protection(self):
        """
        Scenario: User tries to bypass TDD
        Expected: Brain Protector BLOCKS, suggests test-first alternative
        """
        
    def test_e2e_ksessions_knowledge_isolation(self):
        """
        Scenario: CORTEX learns from KSESSIONS work
        Expected: Patterns tagged scope='application', namespace=['KSESSIONS']
        """
        
    def test_e2e_amnesia_preserves_cortex_intelligence(self):
        """
        Scenario: Run amnesia after KSESSIONS work
        Expected: All KSESSIONS patterns deleted, CORTEX patterns intact
        """
        
    def test_e2e_namespace_search_priority(self):
        """
        Scenario: Search for "test workflow" in KSESSIONS context
        Expected: KSESSIONS patterns ranked first, generic second
        """
        
    def test_e2e_cleanup_automation_executes(self):
        """
        Scenario: 50 events accumulated
        Expected: Automatic cleanup runs, stale patterns removed
        """
```

**Target:** 12 integration tests

#### Task 6.2: Performance Regression Tests (1 hr)
**File:** `CORTEX/tests/performance/test_boundary_overhead.py` (NEW)

**Benchmarks:**
```python
def test_namespace_search_within_150ms():
    """Verify namespace-aware search maintains <150ms target."""
    
def test_scope_filtering_adds_minimal_overhead():
    """Verify scope column adds <5ms to queries."""
    
def test_pattern_decay_execution_time():
    """Verify decay on 1000 patterns completes <500ms."""
```

**Target:** Ensure no performance degradation

#### Task 6.3: Coverage Report (30 min)
**Execution:**
```bash
pytest CORTEX/tests/ --cov=CORTEX/src --cov-report=html
```

**Requirements:**
- Overall coverage: ≥95%
- New boundary modules: 100% coverage
- Brain Protector: 100% coverage
- Cleanup automation: 100% coverage

#### Task 6.4: Manual Validation (1 hr)
**Scenarios:**

1. **Boundary Enforcement:**
   - Add pattern without scope → Should default to 'generic'
   - Add pattern with invalid scope → Should raise ValueError
   - Search from KSESSIONS context → Should boost KSESSIONS patterns

2. **Brain Protector:**
   - Try to modify governance rule → Should challenge
   - Try to add code without test → Should block
   - Try to violate tier boundary → Should block

3. **Cleanup Automation:**
   - Set pattern confidence to 0.20 → Should be deleted on next cleanup
   - Pin pattern and set confidence to 0.10 → Should NOT be deleted

4. **Amnesia:**
   - Run amnesia → Verify KSESSIONS patterns deleted
   - Check knowledge graph → Verify CORTEX patterns intact
   - Check statistics → Verify counts accurate

**Deliverables:**
- Manual test checklist (completed)
- Screenshots/logs of validation
- Sign-off on alignment readiness

---

## 📚 Phase 7: Documentation & User Guide (3-4 hours)

### Objectives
- Document boundary system for developers and users
- Update cortex.md with namespace usage
- Create alignment implementation summary

### Tasks

#### Task 7.1: Update cortex.md (1 hr)
**File:** `prompts/user/cortex.md`

**Additions:**
```markdown
### Knowledge Boundary Management

CORTEX enforces impenetrable boundaries between core intelligence and application knowledge.

**Namespaces:**
- `CORTEX-core`: Generic patterns usable across all projects
- `KSESSIONS`: Application-specific patterns for KSESSIONS
- `NOOR`: Application-specific patterns for NOOR-CANVAS
- Multi-namespace: Patterns shared across applications

**Automatic Classification:**
When CORTEX learns from your work:
- CORTEX modifications → `scope='generic'`, `namespace=['CORTEX-core']`
- Application work → `scope='application'`, `namespace=['YourApp']`

**Amnesia Command (Enhanced):**
```markdown
#file:prompts/user/cortex.md

Reset BRAIN for new application
```

**What Gets Removed:**
- All `scope='application'` patterns
- Application-specific conversations
- Project-specific context

**What Gets Preserved:**
- All `scope='generic'` CORTEX intelligence
- Test-first workflows
- SOLID principles
- Protection rules
- Governance patterns

**Namespace-Specific Amnesia:**
```markdown
#file:prompts/user/cortex.md

Remove KSESSIONS knowledge only
```
```

**Deliverables:**
- Updated cortex.md with boundary documentation
- Usage examples for namespace management
- Amnesia command documentation

#### Task 7.2: Create ALIGNMENT-IMPLEMENTATION.md (1.5 hrs)
**File:** `CORTEX-ALIGNMENT-IMPLEMENTATION.md`

**Content:**
```markdown
# CORTEX Alignment Implementation Summary

## Overview
Complete implementation of knowledge boundary system enforcing impenetrable separation between CORTEX core intelligence and application-specific knowledge.

## Architecture

### Boundary System
- **Scope Column:** `generic` (CORTEX) vs `application` (apps)
- **Namespaces Column:** JSON array supporting multi-app patterns
- **Automatic Classification:** Event-driven scope detection
- **Isolation Guarantee:** Database-enforced separation

### Components
1. Schema Migration (Tier 2)
2. Boundary Enforcement (brain-updater.md)
3. Brain Protector (architectural protection)
4. Cleanup Automation (pattern health)
5. Enhanced Amnesia (surgical deletion)

## Usage Guide

### For Developers
[Schema details, API changes, testing]

### For Users
[Namespace commands, amnesia workflow, protection override]

## Performance Impact
- Search queries: <150ms (no degradation)
- Scope filtering: +3ms overhead
- Namespace JSON storage: +1KB per 100 patterns

## Test Coverage
- Boundary enforcement: 100%
- Brain Protector: 100%
- Cleanup automation: 100%
- Overall: 95%+

## Migration Notes
- Existing patterns auto-classified
- Backward compatible (defaults provided)
- Rollback available via backup

## Lessons Learned
[Insights from implementation]
```

**Deliverables:**
- Complete implementation summary
- Architecture diagrams
- Usage guide for developers and users

#### Task 7.3: Update Tier 2 README (30 min)
**File:** `CORTEX/src/tier2/README.md`

**Additions:**
- Namespace/scope system explanation
- API examples with scope parameter
- Search query examples with namespace boosting

#### Task 7.4: Create Quick Reference (1 hr)
**File:** `CORTEX-BOUNDARY-QUICK-REFERENCE.md`

**Content:**
```markdown
# CORTEX Boundary System - Quick Reference

## Adding Patterns

**Generic (CORTEX core):**
```python
kg.add_pattern(
    pattern_id="test_first_workflow",
    scope="generic",
    namespaces=["CORTEX-core"]
)
```

**Application-specific:**
```python
kg.add_pattern(
    pattern_id="ksessions_host_panel",
    scope="application",
    namespaces=["KSESSIONS"]
)
```

## Searching Patterns

**From KSESSIONS context:**
```python
patterns = kg.search_patterns(
    query="test workflow",
    current_namespace="KSESSIONS",
    include_generic=True  # Always include CORTEX patterns
)
```

## Running Amnesia

**Full application reset:**
```sql
DELETE FROM patterns WHERE scope = 'application';
```

**Namespace-specific:**
```sql
DELETE FROM patterns 
WHERE namespaces LIKE '%"KSESSIONS"%' 
  AND scope = 'application';
```

## Protection Override

When Brain Protector challenges your request:
```markdown
I understand the risk. Override protection because: [justification]
```
```

**Deliverables:**
- Quick reference for common operations
- Code snippets for each boundary operation
- Troubleshooting tips

---

## 🔧 Phase 8: Minor Fixes & Stragglers (2-3 hours)

### Objectives
- Fix database schema category constraints
- Update test expectations (23→27 rules)
- Address any pending minor issues

### Tasks

#### Task 8.1: Fix Governance Schema (30 min)
**File:** `CORTEX/src/tier0/governance_engine.py`

**Issue:** Category constraint mismatch (YAML lowercase vs DB uppercase)

**Fix:**
```python
# Change CHECK constraint to match YAML
cursor.execute("""
    CREATE TABLE IF NOT EXISTS rules (
        ...
        category TEXT NOT NULL CHECK (
            category IN ('quality', 'protection', 'architecture', 
                        'data', 'automation', 'monitoring', 'limits',
                        'file_organization', 'governance')
        ),
        ...
    )
""")
```

**Deliverables:**
- Updated schema with lowercase categories
- Migration script for existing database
- Test validation

#### Task 8.2: Update Test Expectations (30 min)
**File:** `CORTEX/tests/tier0/test_governance.py`

**Changes:**
```python
def test_loads_expected_rule_count():
    """Verify all 27 governance rules loaded."""
    engine = GovernanceEngine()
    rules = engine.get_all_rules()
    assert len(rules) == 27  # Updated from 23

def test_gets_all_rules():
    """Test retrieval of all rules."""
    engine = GovernanceEngine()
    rules = engine.get_all_rules()
    assert len(rules) == 27  # Updated from 23
```

**Deliverables:**
- Updated test assertions
- Verified 27/27 tests passing

#### Task 8.3: KSESSIONS Cleanup Verification (1 hr)
**Execution:**

1. **Audit KSESSIONS Data:**
   ```bash
   grep -r "ksessions\|KSESSIONS" cortex-brain/tier1/
   grep -r "ksessions\|KSESSIONS" cortex-brain/tier2/
   grep -r "ksessions\|KSESSIONS" cortex-brain/tier3/
   ```

2. **Expected Findings:**
   - `cortex-brain/simulations/ksessions/` → SAFE (isolated simulation data)
   - Tier 1/2/3 databases → Should be CLEAN (empty or CORTEX-only)

3. **If Contamination Found:**
   - Run classification script
   - Tag contaminated patterns with `scope='application'`, `namespaces=['KSESSIONS']`
   - Document cleanup in ALIGNMENT-IMPLEMENTATION.md

**Deliverables:**
- KSESSIONS audit report
- Cleanup actions (if needed)
- Verification that live BRAIN is clean

#### Task 8.4: Dashboard Stub (OPTIONAL - 1 hr)
**Note:** Dashboard is Sub-Group 4C (10-12 hours) - this is just a placeholder

**File:** `CORTEX/dashboard/index.html` (minimal)

**Content:**
```html
<!DOCTYPE html>
<html>
<head>
    <title>CORTEX Dashboard</title>
</head>
<body>
    <h1>CORTEX Dashboard (Coming Soon)</h1>
    <p>Boundary metrics, knowledge graph stats, protection events</p>
    <p>See Sub-Group 4C for full implementation</p>
</body>
</html>
```

**Deliverables:**
- Placeholder dashboard
- Note in IMPLEMENTATION-PROGRESS.md that dashboard is pending

---

## 📊 Success Criteria

### Phase 1 Success
- ✅ `scope` and `namespaces` columns exist in patterns table
- ✅ All existing patterns classified (generic vs application)
- ✅ Indexes created for performance
- ✅ 12/12 tests passing

### Phase 2 Success
- ✅ Brain updater automatically tags new patterns with scope/namespace
- ✅ Search queries boost current namespace patterns
- ✅ Context injector detects application from file paths
- ✅ 15/15 tests passing

### Phase 3 Success
- ✅ Intent router routes CORTEX modifications to Brain Protector
- ✅ Brain Protector challenges TDD bypass, tier violations, SOLID breaches
- ✅ All challenges logged to corpus-callosum
- ✅ 18/18 tests passing

### Phase 4 Success
- ✅ Cleanup automation removes patterns <0.30 confidence
- ✅ Pattern consolidation merges 60-84% similar patterns
- ✅ Automatic triggers after 50 events OR 24 hours
- ✅ 20/20 tests passing

### Phase 5 Success
- ✅ Amnesia uses `DELETE WHERE scope='application'`
- ✅ CORTEX intelligence (scope='generic') preserved
- ✅ Namespace-specific amnesia available
- ✅ 8/8 tests passing

### Phase 6 Success
- ✅ 12/12 integration tests passing
- ✅ Performance benchmarks met (<150ms search, <5ms scope overhead)
- ✅ Overall coverage ≥95%
- ✅ Manual validation checklist completed

### Phase 7 Success
- ✅ cortex.md updated with boundary documentation
- ✅ ALIGNMENT-IMPLEMENTATION.md complete
- ✅ Quick reference guide created
- ✅ All tier READMEs updated

### Phase 8 Success
- ✅ Governance schema category constraints fixed
- ✅ All 27/27 governance tests passing
- ✅ KSESSIONS audit complete, contamination addressed
- ✅ No pending stragglers

---

## 🚀 Execution Strategy

### Recommended Approach: Sequential by Phase
Execute phases in order 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8

**Rationale:**
- Phase 2 depends on Phase 1 schema
- Phase 3/4/5 depend on Phase 2 enforcement
- Phase 6 validates all previous phases
- Phase 7 documents completed work
- Phase 8 cleans up minor issues

### Parallel Opportunities
- Phase 3 (Brain Protector) and Phase 4 (Cleanup) can run in parallel after Phase 2
- Phase 7 documentation can start after Phase 6 testing begins
- Phase 8 minor fixes independent of other phases

### Milestones

**Milestone 1:** Boundary System Operational (Phases 1-2, ~8 hours)
- ✅ Schema migrated
- ✅ Automatic tagging active
- ✅ Namespace-aware search working

**Milestone 2:** Protection Layers Active (Phases 3-4, ~12 hours)
- ✅ Brain Protector challenging violations
- ✅ Cleanup automation running
- ✅ Full boundary enforcement

**Milestone 3:** Alignment Complete (Phases 5-8, ~13 hours)
- ✅ Enhanced amnesia operational
- ✅ All tests passing (100% coverage)
- ✅ Documentation complete
- ✅ Production-ready

---

## 📈 Metrics & Validation

### Code Metrics
- **Lines Added:** ~2,800 (implementation + tests)
- **Files Created:** 12 new files
- **Files Modified:** 18 existing files
- **Tests Added:** 105 tests (12+15+18+20+8+12+20)
- **Test Coverage:** 95%+ overall, 100% on new features

### Performance Metrics
- **Search Query Time:** <150ms (with namespace boosting)
- **Scope Filter Overhead:** <5ms per query
- **Pattern Decay Execution:** <500ms for 1000 patterns
- **Consolidation Time:** <2s for 500 pattern comparisons

### Knowledge Boundary Metrics
- **Generic Patterns:** All `scope='generic'` patterns
- **Application Patterns:** All `scope='application'` patterns
- **Isolation Guarantee:** 100% (database-enforced)
- **Amnesia Precision:** 100% (scope-based deletion)

### Protection Metrics
- **Challenge Rate:** % of CORTEX modifications challenged
- **Block Rate:** % of violations blocked
- **Override Rate:** % of challenges overridden
- **False Positive Rate:** Target <5%

---

## 🎯 Next Steps After Alignment

### Immediate (After Completion)
1. Run full test suite: `pytest CORTEX/tests/ -v`
2. Generate coverage report: `pytest --cov=CORTEX/src --cov-report=html`
3. Commit alignment implementation: `git commit -m "feat(cortex): Implement knowledge boundary system with namespace isolation"`
4. Update IMPLEMENTATION-PROGRESS.md with completion status

### Short-Term (Next Sprint)
1. **Sub-Group 4C:** Dashboard implementation (10-12 hours)
   - Visualize boundary metrics
   - Show namespace distribution
   - Display protection events
   - Knowledge graph statistics

2. **GROUP 5:** Migration & Validation (5-7 hours)
   - Final YAML→SQLite migration
   - Legacy data cleanup
   - End-to-end validation

3. **GROUP 6:** Finalization (4-6 hours)
   - Performance optimization
   - Production hardening
   - Release preparation

### Long-Term
1. Monitor boundary enforcement effectiveness
2. Tune namespace detection heuristics
3. Expand to additional applications (NOOR, etc.)
4. Evaluate cross-namespace pattern sharing benefits

---

## 📝 Appendix

### A. Files Created/Modified

**Created (12 files):**
1. `CORTEX/src/tier2/migrate_add_boundaries.py`
2. `CORTEX/src/tier0/brain_protector.py`
3. `CORTEX/src/tier0/cleanup_scheduler.py`
4. `CORTEX/src/tier2/anomaly_detector.py`
5. `CORTEX/tests/tier2/test_namespace_boundaries.py`
6. `CORTEX/tests/tier2/test_namespace_search.py`
7. `CORTEX/tests/tier0/test_brain_protector.py`
8. `CORTEX/tests/tier0/test_cleanup_automation.py`
9. `CORTEX/tests/tier2/test_amnesia.py`
10. `CORTEX/tests/integration/test_knowledge_boundaries.py`
11. `CORTEX-ALIGNMENT-IMPLEMENTATION.md`
12. `CORTEX-BOUNDARY-QUICK-REFERENCE.md`

**Modified (18 files):**
1. `CORTEX/src/tier2/knowledge_graph.py`
2. `prompts/internal/brain-updater.md`
3. `prompts/internal/intent-router.md`
4. `prompts/internal/brain-amnesia.md`
5. `prompts/user/cortex.md`
6. `scripts/brain-amnesia.ps1`
7. `CORTEX/src/tier0/cleanup_hook.py`
8. `CORTEX/src/tier0/governance_engine.py`
9. `CORTEX/tests/tier0/test_governance.py`
10. `CORTEX/src/context_injector.py`
11. `CORTEX/src/tier2/README.md`
12. `IMPLEMENTATION-PROGRESS.md`
13. (+ 6 test files with minor updates)

### B. Dependency Requirements

**Python Packages:**
- sqlite3 (built-in)
- json (built-in)
- dataclasses (built-in)
- typing (built-in)
- datetime (built-in)
- pathlib (built-in)

**No new dependencies required** - all using Python standard library

### C. Rollback Plan

**If alignment implementation fails:**

1. **Database Rollback:**
   ```bash
   # Restore pre-migration backup
   cp cortex-brain/tier2/knowledge_graph.db.backup \
      cortex-brain/tier2/knowledge_graph.db
   ```

2. **Code Rollback:**
   ```bash
   git revert <alignment-commit-hash>
   git push origin cortex-migration
   ```

3. **Verify Rollback:**
   ```bash
   pytest CORTEX/tests/tier0/ CORTEX/tests/tier1/ CORTEX/tests/tier2/ -v
   ```

4. **Post-Rollback:**
   - Document failure reason
   - Adjust plan based on lessons learned
   - Re-attempt with fixes

### D. Communication Plan

**Stakeholder Updates:**
- Daily: Update IMPLEMENTATION-PROGRESS.md with phase completion
- Milestone: Create summary report after Milestones 1, 2, 3
- Completion: Create final alignment summary with metrics

**Team Communication:**
- Phase completion: Slack/Teams notification
- Blockers: Immediate escalation
- Success: Celebrate milestones

---

**Document Version:** 1.0  
**Last Updated:** November 6, 2025  
**Status:** READY FOR EXECUTION  
**Approval:** Pending stakeholder review

**To Begin Execution:**
```markdown
#file:prompts/user/cortex.md

Execute CORTEX-ALIGNMENT-PLAN.md - Phase 1: Namespace/Scope Schema Migration
```
