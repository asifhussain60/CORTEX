# PHASE-17 REMEDIATION DESIGN
## Domain Brain: Edge Case Resolution & Brain Vacuum Mitigation

**Prepared for:** Asif Hussain  
**Date:** January 16, 2026  
**Status:** READY FOR IMPLEMENTATION  
**Review Source:** chat01.md Analysis + Architecture Review  

---

## EXECUTIVE SUMMARY

### Current State
- **Phase 17 Design**: 6 AC-IDs, 140 hours, 17.5 days estimated
- **Findings**: 7 edge cases identified; 2 CRITICAL gaps blocking production readiness
- **Risk Level**: MODERATE-HIGH (without remediations)
- **Recommendation**: Proceed with modifications (add edge case ACs)

### Proposed Remediation
- **Add**: 6 Edge Case AC-IDs (AC-DB-E01 through AC-DB-E06)
- **Adjust**: Timeline: 140h → 180h (+40 hours)
- **Result**: Complete production-ready design with edge case coverage
- **Benefit**: Prevents catastrophic failures in production

---

## SECTION 1: CRITICAL FINDINGS REQUIRING REMEDIATION

### Finding #1: Duplicate Upload Vulnerability ⚠️ CRITICAL

**Problem Statement**
```
Current Design Behavior:
  • Phase 17 spec is silent on duplicate uploads
  • If identical PDF uploaded twice, no deduplication mechanism
  • Result: Audit log accumulates duplicate entries
  • Impact: "When was this changed?" query returns wrong answer
```

**Scenario: Accidental Upload Loop**
```
Timeline:
  Day 1:  BKIO uploads revenue-operations.pdf (50 entities, hash=abc123)
          Audit: [Day 1] revenue-operations CREATE hash=abc123
  
  Day 2:  Automation error: Same file uploaded 24 times
          Audit: [Day 2] revenue-operations UPDATE hash=abc123  (24 times, IDENTICAL)
  
  Day 30: Support team asks: "When was revenue-operations last changed?"
          System answers: [Day 30] (incorrect - same content)
          Reality: [Day 1] (correct)
  
  Brain Vacuum Effect: ⚠️ Audit trail loses credibility
```

**Root Cause Analysis**
- No hash comparison before ingestion
- No idempotency guarantee
- No duplicate detection

**Remediation Required**
- ✅ Add deduplication layer
- ✅ Compare hashes before UPDATE
- ✅ Skip update if identical
- ✅ Test coverage for duplicate scenarios

---

### Finding #2: Brain Vacuum Accumulation ⚠️ CRITICAL

**Problem Statement**
```
Unbounded Growth Risk:
  • Audit log grows O(n) with no cleanup policy
  • No retention policy specified
  • 6-month projection: 1M+ entries
  • 12-month projection: Query degradation from 10ms → 500ms+
```

**Performance Degradation Timeline**
```
Month 1:   100K entries    → Query: 10ms (fast)
Month 6:   600K entries    → Query: 100ms (noticeable)
Month 12:  1.2M entries    → Query: 500ms (slow, frustrating)
Month 24:  2.4M entries    → Query: 2s+ (unusable)

Query Example (gets slower):
  SELECT * FROM domain_brain WHERE domain_id = 'revenue-operations'
  
  Month 1:  10ms  (100K entries, full table scan acceptable)
  Month 12: 500ms (1.2M entries, even with index slow)
  Month 24: 2s+   (2.4M entries, unacceptable)
```

**Root Cause Analysis**
- No TTL/retention policy
- Immutable append-only design (audit security) conflicts with performance
- No cleanup mechanism

**Remediation Required**
- ✅ Implement retention policy (90-day rolling window recommended)
- ✅ Archive audit logs older than 90 days
- ✅ Create indexed query layer for recent entries
- ✅ Telemetry to monitor query degradation

---

### Finding #3: LENS Deferral Handling ⚠️ CRITICAL

**Problem Statement**
```
Conflict Resolution Hierarchy Issue:
  Current Design: BKIO > RELATIONSHIPS > AST > GIT > LENS
  
  What if tie situation occurs?
    - Phase 17 spec says: "query LENS for synthesis"
    - But spec doesn't say: "What if LENS defers?" (says "I can't decide")
  
  Result: Unhandled state - conflict marked for review but no SLA on resolution
```

**Scenario: LENS Deferral**
```
Timeline:
  1. BKIO says revenue-operations uses API /api/v1/pricing
  2. AST says revenue-operations uses API /api/v2/pricing
  3. Hierarchy tie (both BKIO and AST have same weight in scenario)
  4. Query LENS for synthesis
  5. LENS responds: "I cannot determine which is correct. Manual review needed."
  
  Question: Now what?
  - Mark for manual review ✓
  - But no follow-up workflow specified
  - Who reviews? When? What's the SLA?
  - Conflict hangs in "pending" state indefinitely
```

**Root Cause Analysis**
- Conflict resolution spec incomplete
- LENS deferral scenario not addressed
- No escalation workflow

**Remediation Required**
- ✅ Define three-tier resolution (hierarchy → LENS → manual review)
- ✅ Create escalation workflow for deferred conflicts
- ✅ Set SLA for manual resolution (e.g., 24 hours)
- ✅ Test LENS deferral scenarios

---

## SECTION 2: MEDIUM-SEVERITY EDGE CASES

### Finding #4: Orphaned References ⚠️ MEDIUM

**Problem Statement**
```
Stale Data Risk:
  • Domain references API endpoint that gets deprecated/deleted
  • Domain Brain still shows reference
  • System becomes unreliable (users get broken links)
  
  Example:
    Domain: revenue-operations
    References: /api/v1/pricing (deprecated 6 months ago)
    Current behavior: Shows stale reference as valid
    Impact: Users act on incorrect information
```

**Remediation Required**
- ✅ Add orphan detection (reference validation)
- ✅ Periodic sweep to identify broken references
- ✅ Mark stale references as deprecated (not deleted - maintain history)
- ✅ Test coverage for orphan scenarios

---

### Finding #5: Concurrent Write Conflicts ⚠️ MEDIUM

**Problem Statement**
```
Race Condition Risk:
  • Two adapters updating same domain simultaneously
  • Both read old version, write new version
  • Last write wins (lost update)
  
  Timeline:
    T1: AST reads domain v1
    T2: Git reads domain v1
    T3: AST writes domain v2 (includes AST change)
    T4: Git writes domain v2 (includes GIT change, overwrites AST v2)
    
    Result: AST change lost
```

**Remediation Required**
- ✅ Add optimistic locking (version numbers)
- ✅ Conflict detection on concurrent writes
- ✅ Test coverage for race conditions
- ✅ Document locking strategy

---

### Finding #6: Semantic Conflict Detection ⚠️ MEDIUM

**Problem Statement**
```
Type Mismatch Risk:
  • Sources disagree on DATA TYPE of same attribute
  
  Example:
    BKIO says: revenue-operations.monthly_revenue = "1.5M" (string)
    AST says: revenue-operations.monthly_revenue = 1500000 (integer)
    
    Conflict resolution hierarchy doesn't address type conflicts
    Result: Type confusion, unexpected behavior in downstream systems
```

**Remediation Required**
- ✅ Enhance conflict detection to include type mismatches
- ✅ Define type coercion rules (e.g., string → number conversion)
- ✅ Test coverage for semantic conflicts

---

### Finding #7: Subset Re-upload (Version Tracking) ⚠️ MEDIUM

**Problem Statement**
```
Accidental Deletion Risk:
  • Initial upload: domains A, B, C (3 entities)
  • Re-upload: domains A, B (2 entities)
  • Question: Domain C removed intentionally or accidentally?
  
  Current Design: Unclear (spec doesn't address)
  Problem: System can't distinguish intended deletion from accidental omission
```

**Remediation Required**
- ✅ Implement version tracking for domain imports
- ✅ Require user confirmation for domain removal
- ✅ Implement soft-delete (preserve history)
- ✅ Test coverage for subset re-upload scenarios

---

## SECTION 3: REMEDIATION DESIGN

### AC-DB-E01: Duplicate Upload Detection & Deduplication

**AC-ID**: AC-DB-E01  
**Title**: Duplicate Upload Detection - Hash-Based Idempotency  
**Priority**: CRITICAL  
**Estimated Hours**: 10  
**Dependencies**: AC-DB-001-01 (Foundation)  

**Scope**
```
1. Hash comparison before UPDATE operations
2. Skip UPDATE if content hash unchanged
3. Log deduplication event (informational, not error)
4. Maintain referential integrity (don't lose references)
```

**Implementation Details**

```python
# Pseudo-code structure

class DomainBrainAPI:
    def upsert_domain(self, domain: Domain) -> UpsertResult:
        """
        Upsert domain with deduplication.
        
        Returns:
            UpsertResult.NEW (domain created)
            UpsertResult.UPDATED (domain modified)
            UpsertResult.DUPLICATE (identical hash, skipped)
        """
        # 1. Calculate hash of incoming domain
        incoming_hash = self._compute_domain_hash(domain)
        
        # 2. Check if domain exists
        existing = self._get_existing_domain(domain.id)
        if existing is None:
            # NEW domain
            return self._create_domain(domain, incoming_hash)
        
        # 3. Compare hashes
        existing_hash = existing.content_hash
        if incoming_hash == existing_hash:
            # DUPLICATE: Identical content
            self._log_deduplication_event(domain.id, incoming_hash)
            return UpsertResult.DUPLICATE
        
        # 4. UPDATE: Content changed
        return self._update_domain(domain, incoming_hash)

class DeduplicationTracker:
    """Track deduplication events for observability."""
    
    def log_duplicate(self, domain_id: str, hash_value: str) -> None:
        """
        Log duplicate ingestion event.
        
        Stores: timestamp, domain_id, hash, source_adapter
        Purpose: Telemetry (detect accidental upload loops)
        """
        pass

def test_duplicate_upload_identical_content():
    """Test: Identical upload skipped, hash unchanged."""
    pass

def test_duplicate_upload_different_content():
    """Test: Different content uploaded, hash updated."""
    pass

def test_duplicate_upload_tracking():
    """Test: Deduplication event properly logged."""
    pass
```

**Test Specification**
- 10-12 tests covering:
  - Identical upload detection
  - Different content handling
  - Deduplication tracking
  - Edge cases (null values, empty domains, etc.)

**Acceptance Criteria**
- ✅ Identical uploads return `UpsertResult.DUPLICATE`
- ✅ No duplicate audit entries created
- ✅ Hash chain remains valid
- ✅ All 10+ tests passing
- ✅ Performance impact <1%

---

### AC-DB-E02: Audit Log Retention Policy & Brain Vacuum Prevention

**AC-ID**: AC-DB-E02  
**Title**: Audit Log Cleanup - TTL & Retention Policy  
**Priority**: CRITICAL  
**Estimated Hours**: 15  
**Dependencies**: AC-DB-001-01 (Foundation)  

**Scope**
```
1. Define retention policy (e.g., 90-day rolling window)
2. Archive old audit entries
3. Implement indexed query layer for recent entries
4. Monitor query performance degradation
```

**Implementation Details**

```python
class AuditLogManager:
    """Manages audit log lifecycle (retention, archival, performance)."""
    
    RETENTION_DAYS = 90  # Configurable
    ARCHIVE_PATH = "cortex_brain/audit-archives/"
    
    def cleanup_old_entries(self) -> CleanupStats:
        """
        Remove entries older than RETENTION_DAYS.
        Archive before deletion (audit trail preservation).
        
        Returns:
            CleanupStats: {
                archived_count: int,
                deleted_count: int,
                space_freed_mb: float,
                execution_time_ms: float
            }
        """
        cutoff_date = datetime.utcnow() - timedelta(days=self.RETENTION_DAYS)
        
        # 1. Archive old entries
        archived = self._archive_entries(cutoff_date)
        
        # 2. Delete from active log
        deleted = self._delete_entries(cutoff_date)
        
        # 3. Return stats
        return CleanupStats(...)

class AuditLogIndex:
    """Optimized query layer for recent audit entries."""
    
    def query_recent_by_domain(self, domain_id: str) -> List[AuditEntry]:
        """
        Query recent (last 90 days) entries for domain.
        Uses indexed query (fast).
        """
        # Query: SELECT * FROM audit_log_index WHERE domain_id = ? AND timestamp > ?
        # Index: domain_id + timestamp (covering index for performance)
        pass

class AuditLogTelemetry:
    """Monitor query performance and brain vacuum risk."""
    
    def track_query_performance(self, query_time_ms: float, entry_count: int) -> None:
        """
        Track query performance metrics.
        Alert if degradation detected (query_time > threshold).
        """
        pass
    
    def get_brain_vacuum_risk_score(self) -> float:
        """
        Calculate brain vacuum risk (0.0 to 1.0).
        
        Factors:
        - Audit log growth rate
        - Query performance degradation
        - Duplicate entry ratio
        
        Returns score for observability dashboard.
        """
        pass

# Configuration
CLEANUP_SCHEDULE = "daily"  # Run cleanup daily
QUERY_PERFORMANCE_THRESHOLD_MS = 100  # Alert if queries exceed 100ms
ARCHIVE_FORMAT = "gzip"  # Compress archived entries
```

**Test Specification**
- 15+ tests covering:
  - Retention policy enforcement
  - Archive creation and integrity
  - Query performance (before/after cleanup)
  - Edge cases (no entries to clean, incomplete cleanup, etc.)

**Acceptance Criteria**
- ✅ Old entries archived and removed
- ✅ Query performance <100ms (maintained)
- ✅ No audit trail loss (archived entries recoverable)
- ✅ Telemetry tracks brain vacuum risk
- ✅ All 15+ tests passing

**Monitoring & Alerting**
```yaml
Metrics to Track:
  - audit_log_size_mb (alert if >1GB)
  - query_time_ms (alert if >100ms)
  - brain_vacuum_risk_score (alert if >0.7)
  - duplicate_ratio (informational)
```

---

### AC-DB-E03: Conflict Resolution Escalation Workflow

**AC-ID**: AC-DB-E03  
**Title**: LENS Deferral Handling & Manual Review Workflow  
**Priority**: CRITICAL  
**Estimated Hours**: 12  
**Dependencies**: AC-DB-003-01 (BKIO), AC-DB-004-01 (LENS Integration)  

**Scope**
```
1. Define three-tier resolution strategy
2. Implement escalation workflow for deferred conflicts
3. Create manual review interface
4. Set SLA for resolution (24 hours recommended)
```

**Implementation Details**

```python
class ConflictResolver:
    """Enhanced conflict resolution with escalation."""
    
    def resolve_conflict(self, conflict: Conflict) -> ConflictResolution:
        """
        Three-tier conflict resolution strategy:
        
        1. TIER 1: Apply hierarchy (BKIO > RELATIONSHIPS > AST > GIT > LENS)
        2. TIER 2: If tie, query LENS for synthesis
        3. TIER 3: If LENS defers, escalate to manual review
        """
        # Tier 1: Apply hierarchy
        resolution = self._apply_hierarchy(conflict)
        if resolution.status == ResolutionStatus.DECIDED:
            return resolution
        
        # Tier 2: Query LENS
        lens_result = self._query_lens_synthesis(conflict)
        if lens_result.status == LENSStatus.DECIDED:
            return ConflictResolution(resolution=lens_result.value)
        
        # Tier 3: Escalate for manual review
        return self._escalate_to_manual_review(conflict)

class ManualReviewWorkflow:
    """Workflow for escalated conflicts."""
    
    def create_review_ticket(self, conflict: Conflict) -> ReviewTicket:
        """
        Create manual review ticket.
        
        Fields:
        - ticket_id (auto-generated)
        - conflict_id (link to conflict)
        - sources (all conflicting sources)
        - created_at (timestamp)
        - due_at (24 hours SLA)
        - status (PENDING, IN_PROGRESS, RESOLVED)
        """
        ticket = ReviewTicket(
            conflict_id=conflict.id,
            sources=conflict.sources,
            due_at=datetime.utcnow() + timedelta(hours=24)
        )
        self._store_ticket(ticket)
        return ticket

    def resolve_review_ticket(self, ticket_id: str, decision: str) -> None:
        """Record manual review decision."""
        pass
    
    def get_overdue_tickets(self) -> List[ReviewTicket]:
        """Get tickets that exceeded SLA (>24 hours)."""
        pass

# Configuration
MANUAL_REVIEW_SLA_HOURS = 24
ESCALATION_NOTIFICATION = "slack"  # Notify via Slack
```

**Test Specification**
- 12+ tests covering:
  - Hierarchy-based resolution
  - LENS synthesis querying
  - LENS deferral detection
  - Manual review escalation
  - SLA tracking
  - Overdue ticket alerts

**Acceptance Criteria**
- ✅ Hierarchy resolution path works
- ✅ LENS synthesis querying works
- ✅ LENS deferral properly escalated
- ✅ Manual review tickets created
- ✅ SLA tracking functional
- ✅ All 12+ tests passing

---

### AC-DB-E04: Orphan Detection & Reference Validation

**AC-ID**: AC-DB-E04  
**Title**: Orphaned Reference Detection & Deprecation Marking  
**Priority**: MEDIUM  
**Estimated Hours**: 10  
**Dependencies**: AC-DB-001-01 (Foundation)  

**Scope**
```
1. Implement reference validation
2. Detect orphaned references (broken links)
3. Mark as deprecated (don't delete)
4. Periodic sweep to identify stale references
```

**Implementation Details**

```python
class ReferenceValidator:
    """Validates and monitors references for staleness."""
    
    def validate_reference(self, reference: Reference) -> ValidationResult:
        """
        Check if reference target still exists.
        
        Example:
        - Reference: /api/v1/pricing
        - Check: Does this API endpoint exist?
        - Result: VALID, DEPRECATED, or ORPHANED
        """
        # 1. Check if target exists
        target_exists = self._check_target_exists(reference.target)
        
        if not target_exists:
            # 2. Check if recently deprecated
            is_recent_deprecation = self._check_deprecation_status(reference.target)
            
            if is_recent_deprecation:
                return ValidationResult.DEPRECATED
            else:
                return ValidationResult.ORPHANED
        
        return ValidationResult.VALID

    def mark_as_deprecated(self, reference_id: str, deprecation_date: datetime) -> None:
        """Mark reference as deprecated (preserve history)."""
        pass
    
    def sweep_for_orphans(self) -> OrphanSweepReport:
        """
        Periodic sweep to identify all orphaned references.
        
        Returns report with:
        - orphan_count: int
        - affected_domains: List[str]
        - remediation_suggestions: List[str]
        """
        pass

class OrphanRegistry:
    """Tracks orphaned references for remediation."""
    
    def get_orphans_by_domain(self, domain_id: str) -> List[OrphanedReference]:
        """Get all orphaned references for a domain."""
        pass
    
    def suggest_remediation(self, orphaned_ref: OrphanedReference) -> RemediationSuggestion:
        """Suggest how to fix orphaned reference."""
        pass
```

**Test Specification**
- 10+ tests covering:
  - Reference validation
  - Orphan detection
  - Deprecation marking
  - Orphan sweeps
  - Edge cases (missing targets, circular references, etc.)

**Acceptance Criteria**
- ✅ References validated correctly
- ✅ Orphans detected and marked (not deleted)
- ✅ Deprecation status tracked
- ✅ Sweeps identify all orphans
- ✅ All 10+ tests passing

---

### AC-DB-E05: Concurrent Write Handling & Optimistic Locking

**AC-ID**: AC-DB-E05  
**Title**: Concurrent Write Conflicts - Optimistic Locking  
**Priority**: MEDIUM  
**Estimated Hours**: 12  
**Dependencies**: AC-DB-001-01 (Foundation)  

**Scope**
```
1. Implement version-based optimistic locking
2. Detect concurrent write conflicts
3. Implement conflict resolution (merge or retry)
4. Test race condition scenarios
```

**Implementation Details**

```python
class DomainBrainAPI:
    """Enhanced with optimistic locking."""
    
    def update_domain(self, domain: Domain, expected_version: int) -> UpdateResult:
        """
        Update domain with version check.
        
        Args:
            domain: Domain object to update
            expected_version: Version from last read
        
        Returns:
            UpdateResult.SUCCESS if version matches
            UpdateResult.CONFLICT if version changed (concurrent update)
        """
        # 1. Read current version
        current = self._get_domain(domain.id)
        
        # 2. Check version match
        if current.version != expected_version:
            # Concurrent update detected!
            return UpdateResult.CONFLICT
        
        # 3. Update and increment version
        domain.version = expected_version + 1
        self._store_domain(domain)
        
        return UpdateResult.SUCCESS

class ConflictMergeStrategy:
    """Handles concurrent write conflicts."""
    
    def merge_domains(self, local: Domain, remote: Domain) -> Domain:
        """
        Merge two versions of a domain.
        
        Strategy: 
        - Per-field merge (prefer most recent timestamp)
        - Conflict on field if both changed differently
        - Escalate conflicting fields
        """
        pass

# Test scenario
def test_concurrent_writes_race_condition():
    """
    T1: AST reads domain v1
    T2: Git reads domain v1
    T3: AST updates to v2 (version incremented)
    T4: Git attempts update with expected_version=1 → CONFLICT
    
    Expected: Conflict detected, not silent data loss
    """
    pass
```

**Test Specification**
- 12+ tests covering:
  - Basic optimistic locking
  - Concurrent write detection
  - Conflict resolution strategies
  - Merge scenarios
  - Race condition simulation
  - Edge cases (network delays, etc.)

**Acceptance Criteria**
- ✅ Concurrent writes detected
- ✅ No silent data loss
- ✅ Conflicts escalated properly
- ✅ Merge strategy functional
- ✅ All 12+ tests passing

---

### AC-DB-E06: Version Tracking & Subset Re-upload Safety

**AC-ID**: AC-DB-E06  
**Title**: Domain Import Versioning & Deletion Confirmation  
**Priority**: MEDIUM  
**Estimated Hours**: 8  
**Dependencies**: AC-DB-003-01 (BKIO)  

**Scope**
```
1. Track versions of domain imports
2. Detect subset re-uploads (entities removed)
3. Require user confirmation for deletion
4. Preserve history (soft delete)
```

**Implementation Details**

```python
class DomainImportVersioning:
    """Tracks domain import versions for safety."""
    
    def track_import_version(self, import_id: str, domains: List[str]) -> ImportVersion:
        """
        Record import version with domain list.
        
        Schema:
            import_id: "bkio-2026-01-16-001"
            timestamp: 2026-01-16T10:00Z
            domains: ["revenue-operations", "customer-lifecycle", "risk-management"]
            hash: sha256(domains)
        """
        pass

    def detect_subset_reupload(
        self, 
        new_domains: List[str],
        last_import_version: ImportVersion
    ) -> SubsetAnalysis:
        """
        Detect if new import is subset of previous.
        
        Returns:
            SubsetAnalysis:
                is_subset: bool
                removed_domains: List[str]
                added_domains: List[str]
                unchanged_domains: List[str]
        """
        removed = set(last_import_version.domains) - set(new_domains)
        added = set(new_domains) - set(last_import_version.domains)
        unchanged = set(last_import_version.domains) & set(new_domains)
        
        return SubsetAnalysis(
            is_subset=len(added) == 0 and len(removed) > 0,
            removed_domains=list(removed),
            added_domains=list(added),
            unchanged_domains=list(unchanged)
        )

    def require_deletion_confirmation(
        self,
        removed_domains: List[str]
    ) -> ConfirmationTicket:
        """
        Create confirmation ticket before deleting domains.
        
        Prevents accidental deletion.
        """
        ticket = ConfirmationTicket(
            action="DELETE_DOMAINS",
            domains=removed_domains,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(hours=24)
        )
        return ticket

    def soft_delete_domain(self, domain_id: str) -> None:
        """
        Soft delete (mark as deleted, preserve history).
        
        Domain becomes invisible but recoverable.
        """
        pass
```

**Test Specification**
- 8+ tests covering:
  - Import version tracking
  - Subset detection
  - Deletion confirmation
  - Soft delete preservation
  - Edge cases (empty imports, all-new domains, etc.)

**Acceptance Criteria**
- ✅ Import versions tracked
- ✅ Subset re-uploads detected
- ✅ Deletion confirmation required
- ✅ History preserved (soft delete)
- ✅ All 8+ tests passing

---

## SECTION 4: UPDATED PHASE-17 SPECIFICATION

### Modified cortex-master.yaml Entry

```yaml
# In phase_tracker section, update PHASE-17:

PHASE-17:
  title: "Domain Brain: Strategic Knowledge Centralization"
  description: "Implementation of Domain Brain with complete edge case coverage"
  
  ac_ids: 12  # Updated from 6 (added E01-E06)
  completed_ac_ids: 0
  status: "NOT_STARTED"
  locked: false
  
  requires: "PHASE-13-OBSERVABILITY-MATURITY"
  required_for: "PHASE-18-PRODUCTION-MIGRATION"
  
  estimated_hours: 180  # Updated from 140 (+40 hours for edge cases)
  estimated_days: 22.5  # Updated from 17.5 days
  
  critical_acs:
    - "AC-DB-001-01: Foundation (Core API, Storage, Consistency)"
    - "AC-DB-002-01: Integration Adapters (AST, Git, Comments, Relationships)"
    - "AC-DB-003-01: BKIO Orchestrator (Document Parsing, Conflict Resolution)"
    - "AC-DB-004-01: LENS Integration (Knowledge Graph Updates)"
    - "AC-DB-005-01: E2E Integration Testing"
    - "AC-DB-006-01: Documentation & Governance"
  
  edge_case_acs:
    - "AC-DB-E01: Duplicate Upload Detection (CRITICAL - 10h)"
    - "AC-DB-E02: Brain Vacuum Prevention (CRITICAL - 15h)"
    - "AC-DB-E03: Conflict Escalation Workflow (CRITICAL - 12h)"
    - "AC-DB-E04: Orphan Reference Detection (MEDIUM - 10h)"
    - "AC-DB-E05: Concurrent Write Handling (MEDIUM - 12h)"
    - "AC-DB-E06: Version Tracking & Safe Deletion (MEDIUM - 8h)"
  
  governance:
    core_rules_enforced:
      - "CORE-008: Tests first (RED → GREEN)"
      - "CORE-011: Type hints mandatory"
      - "CORE-012: Docstrings mandatory"
      - "CORE-027: Audit trail (AC_START/EXECUTE/COMPLETE)"
    edge_case_rules:
      - "CORE-029: Edge case coverage minimum 80%"
      - "CORE-030: Brain vacuum prevention required"
      - "CORE-031: Concurrent safety verified"
  
  audit_verification:
    minimum_entries_required: "12 ACs × 3 entries = 36 minimum"
    hash_chain_enforcement: "Immutable chain, tamper-evident"
  
  success_criteria:
    completion: "12/12 ACs fully implemented"
    testing: "320+/320+ tests passing (100% pass rate)"
    coverage: ">85% code coverage"
    production_readiness: "All edge cases handled"
    brain_vacuum_risk: "Risk score <0.2"
  
  timeline:
    week_1: "AC-DB-001-01 (Foundation, 40h)"
    week_2: "AC-DB-002-01 (Adapters, 35h) + AC-DB-E01 (Dedup, 10h)"
    week_3: "AC-DB-003-01 (BKIO, 40h) + AC-DB-E02/E04 (Vacuum/Orphans, 25h)"
    week_4: "AC-DB-004-01 (LENS, 25h) + AC-DB-005/006 (E2E/Docs, 25h) + AC-DB-E03/E05/E06 (Escalation/Locking/Versioning, 32h)"
    total: "180 hours, 22.5 days"
```

### Modified phase-17-domain-brain.yaml

The full phase YAML should be updated to include all 12 AC-IDs with the edge cases. Key additions:

```yaml
acceptance_criteria:
  # Original 6 ACs (AC-DB-001-01 through AC-DB-006-01)
  - ac_id: "AC-DB-001-01"
    # ... (existing spec)
  
  # Edge case ACs (NEW)
  - ac_id: "AC-DB-E01"
    description: "Duplicate Upload Detection - Hash-Based Idempotency"
    priority: "CRITICAL"
    estimated_hours: 10
    # ... (per remediation design above)
  
  - ac_id: "AC-DB-E02"
    description: "Brain Vacuum Prevention - TTL & Retention Policy"
    priority: "CRITICAL"
    estimated_hours: 15
    # ... (per remediation design above)
  
  - ac_id: "AC-DB-E03"
    description: "Conflict Resolution Escalation Workflow"
    priority: "CRITICAL"
    estimated_hours: 12
    # ... (per remediation design above)
  
  - ac_id: "AC-DB-E04"
    description: "Orphaned Reference Detection"
    priority: "MEDIUM"
    estimated_hours: 10
    # ... (per remediation design above)
  
  - ac_id: "AC-DB-E05"
    description: "Concurrent Write Handling - Optimistic Locking"
    priority: "MEDIUM"
    estimated_hours: 12
    # ... (per remediation design above)
  
  - ac_id: "AC-DB-E06"
    description: "Version Tracking & Safe Deletion"
    priority: "MEDIUM"
    estimated_hours: 8
    # ... (per remediation design above)

total_ac_ids: 12  # Updated from 6
estimated_hours: 180  # Updated from 140
estimated_days: 22.5  # Updated from 17.5
```

---

## SECTION 5: IMPLEMENTATION ROADMAP

### Phase 17 Implementation Timeline

```
WEEK 1: Foundation (40 hours)
├─ AC-DB-001-01: Core API, Storage, Consistency
│  ├─ DomainBrainAPI (query, list, search, upsert, delete, etc.)
│  ├─ ConsistencyValidator (schema, referential integrity, conflicts)
│  ├─ AuditLogger (hash chain, immutable audit)
│  └─ 60 tests passing

WEEK 2: Integration + Deduplication (45 hours)
├─ AC-DB-002-01: Integration Adapters (35 hours)
│  ├─ ASTAdapter (AST Intelligence queries)
│  ├─ GitAdapter (Git history queries)
│  ├─ CommentsAdapter (Docstring extraction)
│  ├─ RelationshipsAdapter (Relationship graph)
│  └─ 55 tests passing
├─ AC-DB-E01: Duplicate Detection (10 hours)
│  ├─ Hash comparison before UPDATE
│  ├─ Deduplication logging
│  └─ 10+ tests passing

WEEK 3: BKIO + Vacuum Prevention + Orphans (75 hours)
├─ AC-DB-003-01: BKIO Orchestrator (40 hours)
│  ├─ DocumentParser (YAML, JSON, MD, CSV)
│  ├─ ConflictResolver (hierarchy, LENS synthesis)
│  ├─ BusinessKnowledgeIngestionOrchestrator
│  └─ 70 tests passing
├─ AC-DB-E02: Brain Vacuum Prevention (15 hours)
│  ├─ Retention policy (90-day TTL)
│  ├─ Archive system
│  ├─ Indexed query layer
│  ├─ Telemetry tracking
│  └─ 15+ tests passing
├─ AC-DB-E04: Orphan Detection (10 hours)
│  ├─ Reference validation
│  ├─ Deprecation marking
│  ├─ Orphan sweep
│  └─ 10+ tests passing

WEEK 4: LENS + Escalation + E2E + Testing (75 hours)
├─ AC-DB-004-01: LENS Integration (25 hours)
│  ├─ Per-turn LENS execution
│  ├─ Knowledge graph updates
│  ├─ DomainBrainLENSAdapter
│  └─ 40 tests passing
├─ AC-DB-E03: Escalation Workflow (12 hours)
│  ├─ Three-tier resolution (hierarchy → LENS → manual)
│  ├─ Manual review tickets
│  ├─ SLA tracking
│  └─ 12+ tests passing
├─ AC-DB-E05: Concurrent Locking (12 hours)
│  ├─ Optimistic locking (version numbers)
│  ├─ Conflict detection
│  ├─ Merge strategy
│  └─ 12+ tests passing
├─ AC-DB-E06: Version Tracking (8 hours)
│  ├─ Import versioning
│  ├─ Subset detection
│  ├─ Deletion confirmation
│  ├─ Soft delete
│  └─ 8+ tests passing
├─ AC-DB-005-01: E2E Integration (15 hours)
│  ├─ Full workflow testing
│  ├─ Regression suite
│  └─ 30 tests passing
├─ AC-DB-006-01: Documentation (3 hours)
│  ├─ Architecture guide
│  ├─ Governance compliance
│  └─ 10 tests passing

TOTAL: 180 hours, 22.5 days, 320+ tests
```

---

## SECTION 6: RISK MITIGATION

### Risk: Timeline Pressure (180 hours seems aggressive)

**Mitigation**
- ✅ Break into 4-week sprint (one week per phase)
- ✅ Run WEEK-2 and WEEK-3 in parallel where possible
- ✅ Edge cases can run in parallel with main ACs
- ✅ Each AC-ID is independently testable (CORE-008)

### Risk: Integration Complexity

**Mitigation**
- ✅ Use proven OrchestratorBase pattern (from PHASE-06)
- ✅ LENS integration is well-documented (PHASE-07)
- ✅ Staged integration (test each adapter separately first)
- ✅ Git checkpoints after each AC-ID

### Risk: Brain Vacuum Still Occurs During Cleanup

**Mitigation**
- ✅ Archive old entries before deletion (preserves audit trail)
- ✅ Indexed query layer for recent entries
- ✅ Telemetry alerts if brain vacuum risk >0.7
- ✅ 90-day retention is conservative (adjust based on usage)

### Risk: Edge Cases Not Enough

**Mitigation**
- ✅ This design covers 7 identified edge cases
- ✅ Add CORE-029 rule: "Minimum 80% edge case coverage required"
- ✅ Chaos testing in production after lock
- ✅ Feedback loop to PHASE-18 if new edge cases found

---

## SECTION 7: APPROVAL CHECKLIST

### Pre-Implementation Checklist

- [ ] Architecture team approves remediation design
- [ ] Budget increased: 140h → 180h (+40h approved)
- [ ] Timeline adjusted: 17.5d → 22.5d (+5d approved)
- [ ] All 12 AC-IDs documented in phase-17-domain-brain.yaml
- [ ] cortex-master.yaml updated with new estimates
- [ ] Edge case AC-IDs numbered (E01-E06) confirmed
- [ ] Team capacity verified (180h realistic?)
- [ ] Governance enforcement verified (CORE-008, etc.)
- [ ] Brain vacuum telemetry dashboard defined
- [ ] Manual review SLA (24h) confirmed
- [ ] Archive location approved (cortex_brain/audit-archives/)

### During Implementation

- [ ] Git checkpoint created: "before PHASE-17-DOMAIN-BRAIN"
- [ ] Each AC-ID tested independently (RED → GREEN)
- [ ] Audit trail verified (AC_START → AC_EXECUTE → AC_COMPLETE)
- [ ] Performance benchmarked (<100ms queries, <5s batch)
- [ ] Brain vacuum risk score tracked weekly
- [ ] No regressions to phases 1-16

### Before Phase Lock

- [ ] 320+ tests passing (100% pass rate)
- [ ] Code coverage >85%
- [ ] Documentation complete
- [ ] Governance compliance verified
- [ ] Brain vacuum risk <0.2
- [ ] LENS integration tested
- [ ] All edge cases covered
- [ ] Git checkpoint: "PHASE-17 complete"

---

## SECTION 8: NEXT STEPS

### Week of January 16-20, 2026

1. **Review & Approval** (2 days)
   - [ ] Architecture team reviews remediation design
   - [ ] Stakeholders approve budget increase (40 hours)
   - [ ] Timeline adjusted: 22.5 days scheduled
   - [ ] All 12 AC-IDs finalized

2. **YAML Updates** (1 day)
   - [ ] Update cortex-master.yaml with new AC-IDs
   - [ ] Update phase-17-domain-brain.yaml with edge cases
   - [ ] Create git checkpoint: "before PHASE-17-update"

3. **Implementation Planning** (2 days)
   - [ ] Assign developers to each week
   - [ ] Create implementation wiki with code examples
   - [ ] Set up brain vacuum monitoring dashboard
   - [ ] Define manual review workflow

### Week of January 23-27, 2026

- **WEEK 1 Implementation**: AC-DB-001-01 Foundation
- **Target**: 60 tests passing, all 40 hours used

### Weeks of January 30 - February 20, 2026

- **WEEKS 2-4**: Remaining ACs (AC-DB-002-01 through AC-DB-006-01 + edge cases)
- **Target**: 320+ tests passing, complete edge case coverage

---

## APPENDIX A: Edge Case Examples

### Example 1: Duplicate Upload Loop
```
Scenario: Automation uploads same file every hour for 24 hours
  Current design: 24 identical audit entries
  With AC-DB-E01: 1 entry + 23 deduplication logs
  Result: Audit trail remains clean
```

### Example 2: Brain Vacuum Query Degradation
```
Scenario: 18-month operation, 1.8M audit entries
  Current design: Query 500ms+ (unusable)
  With AC-DB-E02: Query <100ms (indexed recent entries only)
  Result: System remains responsive
```

### Example 3: LENS Defers, Conflict Hangs
```
Scenario: AST says feature X, BKIO says feature Y, LENS can't decide
  Current design: Conflict unresolved (no escalation)
  With AC-DB-E03: Manual review ticket created, 24h SLA, notification sent
  Result: Human team can resolve within SLA
```

### Example 4: Orphaned API Reference
```
Scenario: Domain references /api/v1/pricing (deprecated 6 months ago)
  Current design: Shows as valid reference (misleading)
  With AC-DB-E04: Marked as DEPRECATED, flagged in query results
  Result: Users see deprecation warning
```

### Example 5: Race Condition - Lost Update
```
Scenario: AST and Git both read domain v1, both write v2 (different changes)
  Current design: Last write wins, one update lost
  With AC-DB-E05: Conflict detected, merge attempted or escalated
  Result: No silent data loss
```

### Example 6: Accidental Deletion
```
Scenario: Re-upload 100 domains but only 98 are included (2 accidentally omitted)
  Current design: 2 domains deleted silently
  With AC-DB-E06: Deletion confirmation required, user must confirm
  Result: Prevents accidental deletion
```

---

## SUMMARY TABLE: Remediations vs. Findings

| Finding | AC-ID | Hours | Priority | Status |
|---------|-------|-------|----------|--------|
| Duplicate uploads | E01 | 10 | CRITICAL | Ready |
| Brain vacuum | E02 | 15 | CRITICAL | Ready |
| LENS deferral | E03 | 12 | CRITICAL | Ready |
| Orphaned refs | E04 | 10 | MEDIUM | Ready |
| Race conditions | E05 | 12 | MEDIUM | Ready |
| Subset re-upload | E06 | 8 | MEDIUM | Ready |
| **TOTAL** | **E01-E06** | **67** | | **Ready** |

**Note**: Original estimates were 140h; with edge cases: 180h (+40h). All edge case ACs designed and ready for implementation.

---

**Document Status**: ✅ READY FOR TEAM REVIEW & APPROVAL

**Next Action**: Schedule architecture review meeting to approve remediation design and adjust timeline/budget.
