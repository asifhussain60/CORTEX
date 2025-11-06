# CORTEX Strategic Refinements - Nov 6, 2025

**Date:** 2025-11-06  
**Status:** 🎯 STRATEGIC PLANNING  
**Context:** User review identified 3 key gaps in current plan  
**Purpose:** Address cleanup instincts, negative testing, and report file strategy

---

## 🚨 User Questions Identified

### 1. Report Files in `docs/reports/` - Are They Needed?

**Question:**
> "Does CORTEX need to dump these report files in docs/reports? If they're not needed, can they be pushed to git with a git commit referenced in a single index file for retrieval?"

**Current State:**
```
docs/reports/
├── WEEK1-CRAWLERS-COMPLETION-REPORT.md
├── WEEK1-MULTI-THREADED-CRAWLERS-STATUS.md
├── KDS-V6-WEEK1-COMPLETE.md
├── BRAIN-INTELLIGENCE-WEEK1-COMPLETE.md
├── test-run-20251103-200000.md
└── [40+ other report files]
```

**Analysis:**

**Purpose of Report Files:**
- ✅ Historical record of milestones (Week 1, Phase completion)
- ✅ Test run results for regression analysis
- ✅ Implementation summaries for future reference
- ❌ NOT actively used during runtime
- ❌ NOT queried by BRAIN for decision-making
- ❌ Growing accumulation (40+ files, will increase)

**Storage Options:**

**Option A: Keep in `docs/reports/` (Current)**
- ✅ Easy to browse
- ✅ Markdown readable in VS Code
- ❌ Clutters workspace
- ❌ No automatic cleanup
- ❌ Hard to search across reports

**Option B: Git-Based Archive with Index**
- ✅ Full history preserved
- ✅ Single index file for discovery
- ✅ Automatic cleanup (git commit = archival)
- ✅ Searchable via git log/grep
- ❌ Requires discipline (commit after each milestone)
- ❌ Not directly browsable without checkout

**Option C: Database Storage in CORTEX**
- ✅ Queryable (SQL search)
- ✅ Structured data
- ✅ No file clutter
- ❌ Requires migration from existing files
- ❌ Not human-readable without dashboard

**RECOMMENDATION: Hybrid Approach**

```yaml
Strategy: Git-Based Archive with SQLite Index

Implementation:
  1. Move completed reports to git:
     - Commit milestone reports immediately
     - Message: "docs: Archive [Phase/Week] completion report"
     - Tag: "milestone-week1", "milestone-phase0"
  
  2. Create index file:
     - File: docs/reports/INDEX.md
     - Lists all archived reports with:
       * Report name
       * Git commit SHA
       * Date
       * Summary (1-2 sentences)
       * Tags (phase, week, feature)
  
  3. Store metadata in CORTEX Tier 3:
     - Table: milestone_reports
     - Columns:
       * report_name (TEXT)
       * commit_sha (TEXT)
       * date (TEXT)
       * phase (TEXT)
       * summary (TEXT)
       * tags (TEXT)
     - Purpose: Queryable index for BRAIN
  
  4. Cleanup rule:
     - After milestone commit → Delete local file
     - INDEX.md updated automatically
     - CORTEX Tier 3 updated with metadata

Benefits:
  ✅ Zero file clutter (only INDEX.md remains)
  ✅ Full history preserved (git)
  ✅ Queryable (CORTEX Tier 3)
  ✅ Human-readable (INDEX.md)
  ✅ Automatic (git hooks trigger cleanup)
```

**Implementation in CORTEX:**

```python
# CORTEX/src/tier5/cleanup_manager.py

class CleanupManager:
    """Tier 5: Housekeeping - Automatic report archival"""
    
    def archive_milestone_report(self, report_path: str):
        """
        Archive milestone report to git and update index.
        
        Steps:
          1. Extract metadata (phase, date, summary)
          2. Git commit with semantic message
          3. Update INDEX.md
          4. Update Tier 3 milestone_reports table
          5. Delete local file
        """
        pass
    
    def query_archived_reports(self, phase: str = None, tags: list = None):
        """
        Query archived reports from Tier 3.
        
        Returns: List of reports with commit SHAs for retrieval
        """
        pass
    
    def retrieve_archived_report(self, commit_sha: str):
        """
        Retrieve archived report from git history.
        
        Uses: git show <commit_sha>:path/to/report.md
        """
        pass
```

**Decision Required:**
- [ ] Approve hybrid git + SQLite approach
- [ ] Approve automatic cleanup after milestone commits
- [ ] Approve INDEX.md as single reference file

---

### 2. Crawlers - Have They Been Designed and Implemented?

**Question:**
> "Have crawlers been designed and implemented yet?"

**Current State:**

**YES - Crawlers Implemented in KDS v6.0 ✅**

**Location:** `KDS/scripts/crawlers/`

**Implemented Crawlers (4 Total):**
```powershell
# 1. UI Crawler
scripts/crawlers/ui-crawler.ps1
  - Scans: .razor, .cshtml, .vue, .tsx, .jsx files
  - Extracts: Component IDs, CSS classes, event handlers
  - Feeds: kds-brain/long-term/ui-relationships.yaml
  - Status: ✅ WORKING (completed Week 1)

# 2. API Crawler
scripts/crawlers/api-crawler.ps1
  - Scans: Controllers, API endpoints
  - Extracts: Routes, HTTP methods, parameters
  - Feeds: kds-brain/long-term/api-relationships.yaml
  - Status: ✅ WORKING (completed Week 1)

# 3. Service Crawler
scripts/crawlers/service-crawler.ps1
  - Scans: Service layer classes
  - Extracts: Methods, dependencies, DI patterns
  - Feeds: kds-brain/long-term/service-relationships.yaml
  - Status: ✅ WORKING (completed Week 1)

# 4. Test Crawler
scripts/crawlers/test-crawler.ps1
  - Scans: .spec.ts, .test.ts, *Tests.cs files
  - Extracts: Test names, assertions, coverage
  - Feeds: kds-brain/long-term/test-relationships.yaml
  - Status: ✅ WORKING (completed Week 1)

# Orchestrator
scripts/crawlers/orchestrator.ps1
  - Runs all 4 crawlers in parallel
  - Aggregates results
  - Performance: 3 seconds (vs 5-minute target)
  - Status: ✅ WORKING (completed Week 1)

# BRAIN Feeder
scripts/crawlers/feed-brain.ps1
  - Processes crawler results
  - Updates knowledge graph
  - Discovers patterns automatically
  - Status: ✅ WORKING (completed Week 1)
```

**Report:** `docs/reports/WEEK1-CRAWLERS-COMPLETION-REPORT.md`

**Performance:**
- ✅ Target: <5 minutes
- ✅ Actual: 3 seconds (99% faster)
- ✅ Parallel execution working
- ✅ BRAIN feeding functional

**CORTEX Migration:**

Crawlers will be migrated to CORTEX with enhancements:

```yaml
CORTEX Crawler Architecture:

Tier: Tier 5 (Housekeeping - Automated Maintenance)

Enhancements from KDS:
  1. SQLite storage (instead of YAML files)
  2. Incremental crawling (only changed files)
  3. Real-time file watching (trigger on save)
  4. Pattern validation (ensure discoveries are actionable)
  5. Cleanup integration (archive old crawler results)

Crawlers in CORTEX:
  - Component crawler (UI elements)
  - API crawler (endpoints)
  - Service crawler (DI patterns)
  - Test crawler (coverage)
  - Documentation crawler (README, comments) ← NEW
  - Configuration crawler (settings) ← NEW
```

**Cleanup Integration (NEW):**

Crawlers should include cleanup as **instinct** (Tier 0 principle):

```python
# CORTEX/src/tier5/crawlers/base_crawler.py

class BaseCrawler:
    """Base class for all CORTEX crawlers with cleanup instinct"""
    
    def __init__(self):
        self.cleanup_enabled = True  # Tier 0 instinct
    
    def crawl(self, workspace_root: str):
        """
        Crawl workspace and automatically cleanup.
        
        Cleanup instincts:
          - Archive old crawler results (>30 days)
          - Remove duplicate discoveries
          - Consolidate similar patterns
          - Flag stale data (files no longer exist)
        """
        results = self._discover_patterns(workspace_root)
        
        if self.cleanup_enabled:
            self._cleanup_old_results()
            self._consolidate_patterns()
            self._remove_stale_data()
        
        return results
    
    def _cleanup_old_results(self):
        """Archive crawler results older than 30 days"""
        pass
    
    def _consolidate_patterns(self):
        """Merge similar patterns to reduce noise"""
        pass
    
    def _remove_stale_data(self):
        """Remove references to deleted files"""
        pass
```

**Decision Required:**
- [ ] Approve crawler migration to CORTEX Tier 5
- [ ] Approve cleanup instincts as mandatory
- [ ] Approve real-time file watching enhancement

---

### 3. Cleanup as Instinct Layer Forethought

**Question:**
> "I want organized cleanup to be part of the instinct layer as a forethought when designing features."

**Analysis:**

**Current State:**
- ✅ Tier 5 exists: Housekeeping (Auto-maintenance)
- ❌ Cleanup is NOT in Tier 0 (Instinct)
- ❌ Cleanup is reactive (manual scripts)
- ❌ No cleanup forethought when designing features

**Problem:**
Features are designed without considering:
- Data accumulation (events, conversations, reports)
- Storage bloat (database size, file count)
- Archival strategy (when to delete, when to preserve)
- Cleanup automation (triggers, schedules)

**Solution: Cleanup Principles in Tier 0 (Instinct)**

```yaml
# CORTEX/src/tier0/governance.yaml

cleanup_instincts:
  rule_id: "CLEANUP_FORETHOUGHT"
  severity: "CRITICAL"
  category: "housekeeping"
  description: "All features MUST include cleanup strategy before implementation"
  
  requirements:
    before_implementation:
      - "Define data lifecycle (how long to keep)"
      - "Specify archival trigger (time, size, event count)"
      - "Document cleanup automation (manual vs automatic)"
      - "Estimate storage impact (growth rate, max size)"
    
    enforcement:
      - "Work planner MUST ask: 'What's the cleanup strategy?'"
      - "Brain protector CHALLENGES if no cleanup plan"
      - "Code reviewer BLOCKS PR if cleanup missing"
    
    examples:
      event_stream:
        lifecycle: "Keep 30 days, archive older"
        trigger: "Daily at 2am OR >10,000 events"
        automation: "Automatic (cron job)"
        storage: "~500 KB/day, max 15 MB (30 days)"
      
      conversations:
        lifecycle: "Keep last 20, FIFO deletion"
        trigger: "On conversation #21 start"
        automation: "Automatic (FIFO queue)"
        storage: "~200 KB total (predictable)"
      
      milestone_reports:
        lifecycle: "Keep indefinitely (git)"
        trigger: "On milestone commit"
        automation: "Automatic (git hook)"
        storage: "~50 KB/report, git history (infinite)"
      
      test_results:
        lifecycle: "Keep last 100 runs, archive older"
        trigger: "After 100th test run"
        automation: "Automatic (result count threshold)"
        storage: "~10 KB/run, max 1 MB (100 runs)"
      
      crawler_results:
        lifecycle: "Keep last 7 days, consolidate older"
        trigger: "Weekly OR >1,000 patterns"
        automation: "Automatic (weekly cron)"
        storage: "~200 KB/crawl, max 1.4 MB (7 days)"

  validation:
    pre_implementation:
      - "Feature proposal includes cleanup section"
      - "Work plan includes cleanup task"
      - "Tests include cleanup verification"
    
    post_implementation:
      - "Cleanup automation tested"
      - "Storage limits enforced"
      - "Archival triggers working"
```

**Implementation in Work Planner:**

```python
# CORTEX/src/agents/work_planner.py

class WorkPlanner:
    """RIGHT BRAIN - Strategic planning with cleanup forethought"""
    
    def create_plan(self, feature_request: str):
        """Create plan with mandatory cleanup phase"""
        
        # Phase 0: Architectural Discovery
        # Phase 1-N: Feature implementation
        
        # MANDATORY: Cleanup Phase (Tier 0 requirement)
        cleanup_phase = self._create_cleanup_phase(feature_request)
        
        if cleanup_phase is None:
            # Brain Protector CHALLENGES
            return self._challenge_missing_cleanup(feature_request)
        
        return {
            "phases": [
                # ... feature phases ...
                cleanup_phase  # MANDATORY
            ]
        }
    
    def _create_cleanup_phase(self, feature_request: str):
        """
        Create cleanup phase based on Tier 0 instincts.
        
        Questions to answer:
          - What data does this feature generate?
          - How long should it be kept?
          - What triggers cleanup?
          - Is cleanup automatic or manual?
          - What's the storage impact?
        """
        pass
    
    def _challenge_missing_cleanup(self, feature_request: str):
        """
        Brain Protector CHALLENGES if cleanup strategy missing.
        
        Response:
          ⚠️ BRAIN PROTECTION CHALLENGE
          
          Feature: [feature_request]
          Missing: Cleanup strategy
          
          Required:
            - Data lifecycle definition
            - Archival trigger
            - Automation strategy
            - Storage impact estimate
          
          Please provide cleanup strategy before proceeding.
        """
        pass
```

**Example: Feature with Cleanup Forethought**

```markdown
Feature Request: "Add export history tracking"

Phase 0: Architectural Discovery
  - Task 0.1: Map export service patterns
  - Task 0.2: Define storage schema
  - Task 0.3: **Define cleanup strategy** ← MANDATORY (Tier 0)

Phase 1: Export History Schema
  - Task 1.1: Create export_history table
  - Task 1.2: Add indexes
  - Task 1.3: Write tests

Phase 2: Tracking Implementation
  - Task 2.1: Log exports to database
  - Task 2.2: Query history API
  - Task 2.3: Write tests

Phase 3: Cleanup Automation ← MANDATORY (Tier 0)
  - Task 3.1: Implement archival trigger (>1000 records)
  - Task 3.2: Archive to git (export-history-archive-{date}.json)
  - Task 3.3: Delete archived records
  - Task 3.4: Test cleanup automation
  - Task 3.5: Verify storage limits (max 1000 records = ~500 KB)

Cleanup Strategy (Tier 0 requirement):
  Data lifecycle: Keep last 1000 exports, archive older
  Archival trigger: When 1001st export logged
  Automation: Automatic (database trigger)
  Storage impact: ~500 bytes/export, max 500 KB (1000 records)
  Archival format: JSON files in git (export-history-archive-{date}.json)
  Retention: Infinite (git history)
```

**Decision Required:**
- [ ] Approve CLEANUP_FORETHOUGHT as Tier 0 instinct
- [ ] Approve mandatory cleanup phase in all feature plans
- [ ] Approve Brain Protector challenge for missing cleanup

---

### 4. Negative Testing - System NOT Doing What It's NOT Supposed To Do

**Question:**
> "When writing tests, CORTEX should not just focus on positive tests. Negative tests (system not doing what it's NOT supposed to do) should also be checked."

**Analysis:**

**Current State:**
- ✅ Positive tests designed (features work as expected)
- ❌ Negative tests sparse (not systematic)
- ❌ No Tier 0 requirement for negative testing
- ❌ Test generator doesn't prompt for negative cases

**Problem:**

**Example: Export Feature (Positive Only)**
```python
# Current test (positive only)
def test_export_invoice_success():
    """Test invoice export works"""
    invoice = create_test_invoice()
    result = export_service.export_invoice(invoice.id)
    
    assert result.success == True
    assert result.file_path.endswith('.pdf')
    assert os.path.exists(result.file_path)
```

**What's Missing (Negative Tests):**
```python
# Negative test 1: Invalid invoice ID
def test_export_invalid_invoice_id():
    """System should NOT export non-existent invoice"""
    result = export_service.export_invoice(invoice_id=99999)
    
    assert result.success == False
    assert result.error == "Invoice not found"
    assert result.file_path is None  # Should NOT create file

# Negative test 2: Unauthorized access
def test_export_unauthorized_user():
    """System should NOT allow export by unauthorized user"""
    invoice = create_test_invoice(owner_id=123)
    
    result = export_service.export_invoice(
        invoice_id=invoice.id,
        user_id=456  # Different user
    )
    
    assert result.success == False
    assert result.error == "Unauthorized"
    assert result.file_path is None  # Should NOT export

# Negative test 3: Missing required data
def test_export_incomplete_invoice():
    """System should NOT export invoice with missing data"""
    invoice = create_incomplete_invoice()  # Missing line items
    
    result = export_service.export_invoice(invoice.id)
    
    assert result.success == False
    assert result.error == "Incomplete invoice data"
    assert result.file_path is None  # Should NOT create broken PDF

# Negative test 4: Storage limit exceeded
def test_export_storage_limit_exceeded():
    """System should NOT export if storage quota exceeded"""
    set_storage_quota(0)  # No space left
    
    invoice = create_test_invoice()
    result = export_service.export_invoice(invoice.id)
    
    assert result.success == False
    assert result.error == "Storage quota exceeded"
    assert result.file_path is None  # Should NOT create file

# Negative test 5: Cleanup verification
def test_export_cleans_up_temp_files():
    """System should NOT leave temp files after export"""
    temp_dir_before = os.listdir('/tmp')
    
    invoice = create_test_invoice()
    result = export_service.export_invoice(invoice.id)
    
    temp_dir_after = os.listdir('/tmp')
    
    # Should NOT have new temp files (cleanup worked)
    assert len(temp_dir_after) == len(temp_dir_before)
```

**Solution: Negative Testing as Tier 0 Instinct**

```yaml
# CORTEX/src/tier0/governance.yaml

negative_testing_instinct:
  rule_id: "NEGATIVE_TESTING_REQUIRED"
  severity: "CRITICAL"
  category: "quality"
  description: "All features MUST include negative tests (what NOT to do)"
  
  requirements:
    test_categories:
      positive_tests:
        - "Feature works as expected (happy path)"
        - "Valid inputs produce correct outputs"
        - "Integration with other components"
      
      negative_tests:  # MANDATORY
        - "Invalid inputs rejected gracefully"
        - "Unauthorized access blocked"
        - "Missing data handled (no crashes)"
        - "Resource limits enforced"
        - "Cleanup verified (no leaks)"
        - "Error messages informative"
        - "System state unchanged on failure"
    
    enforcement:
      - "Test generator MUST create negative tests"
      - "Test coverage MUST include negative paths"
      - "Brain Protector CHALLENGES if negative tests missing"
      - "DoD blocks merge if negative coverage <80%"
    
    negative_test_templates:
      invalid_input:
        - "test_{feature}_invalid_id()"
        - "test_{feature}_null_parameter()"
        - "test_{feature}_malformed_data()"
      
      unauthorized_access:
        - "test_{feature}_unauthorized_user()"
        - "test_{feature}_expired_token()"
        - "test_{feature}_insufficient_permissions()"
      
      resource_limits:
        - "test_{feature}_storage_quota_exceeded()"
        - "test_{feature}_rate_limit_enforced()"
        - "test_{feature}_timeout_handled()"
      
      cleanup_verification:
        - "test_{feature}_no_temp_files_leaked()"
        - "test_{feature}_connections_closed()"
        - "test_{feature}_locks_released()"
      
      error_handling:
        - "test_{feature}_error_message_clarity()"
        - "test_{feature}_no_stack_trace_exposed()"
        - "test_{feature}_state_rollback_on_error()"

  ratio:
    target: "2:1 (2 negative tests per 1 positive test)"
    minimum: "1:1 (equal negative and positive)"
    enforcement: "DoD blocks if ratio < 1:1"
```

**Implementation in Test Generator:**

```python
# CORTEX/src/agents/test_generator.py

class TestGenerator:
    """LEFT BRAIN - Test creation with negative test instinct"""
    
    def generate_tests(self, feature_spec: str):
        """Generate positive AND negative tests (Tier 0 requirement)"""
        
        positive_tests = self._generate_positive_tests(feature_spec)
        negative_tests = self._generate_negative_tests(feature_spec)
        
        # Tier 0 enforcement: 2:1 ratio (2 negative per 1 positive)
        if len(negative_tests) < len(positive_tests):
            return self._challenge_insufficient_negative_tests(
                positive_count=len(positive_tests),
                negative_count=len(negative_tests)
            )
        
        return {
            "positive_tests": positive_tests,
            "negative_tests": negative_tests,
            "ratio": f"{len(negative_tests)}:{len(positive_tests)}"
        }
    
    def _generate_negative_tests(self, feature_spec: str):
        """
        Generate negative tests using Tier 0 templates.
        
        Categories:
          - Invalid input
          - Unauthorized access
          - Resource limits
          - Cleanup verification
          - Error handling
        """
        negative_tests = []
        
        # Invalid input tests
        negative_tests.extend(self._generate_invalid_input_tests(feature_spec))
        
        # Unauthorized access tests
        negative_tests.extend(self._generate_unauthorized_tests(feature_spec))
        
        # Resource limit tests
        negative_tests.extend(self._generate_resource_limit_tests(feature_spec))
        
        # Cleanup verification tests
        negative_tests.extend(self._generate_cleanup_tests(feature_spec))
        
        # Error handling tests
        negative_tests.extend(self._generate_error_handling_tests(feature_spec))
        
        return negative_tests
    
    def _challenge_insufficient_negative_tests(self, positive_count: int, negative_count: int):
        """
        Brain Protector CHALLENGES if negative test ratio too low.
        
        Response:
          ⚠️ BRAIN PROTECTION CHALLENGE
          
          Positive tests: {positive_count}
          Negative tests: {negative_count}
          Ratio: {negative_count}:{positive_count}
          
          Required: Minimum 1:1 ratio (equal negative and positive)
          Target: 2:1 ratio (2 negative per 1 positive)
          
          Missing negative test categories:
            - Invalid input tests
            - Unauthorized access tests
            - Resource limit tests
            - Cleanup verification tests
            - Error handling tests
          
          Please add {positive_count - negative_count} more negative tests.
        """
        pass
```

**Example: Feature with Negative Tests**

```markdown
Feature: Export invoice to PDF

Positive Tests (3):
  ✅ test_export_invoice_success() - Valid invoice exports correctly
  ✅ test_export_invoice_with_logo() - Custom logo included
  ✅ test_export_invoice_saves_history() - History tracked

Negative Tests (6 - 2:1 ratio):
  ❌ test_export_invalid_invoice_id() - Rejects non-existent invoice
  ❌ test_export_unauthorized_user() - Blocks unauthorized access
  ❌ test_export_incomplete_invoice() - Rejects incomplete data
  ❌ test_export_storage_quota_exceeded() - Enforces storage limits
  ❌ test_export_cleans_up_temp_files() - No temp file leaks
  ❌ test_export_error_message_clarity() - Error messages informative

Ratio: 6:3 (2:1) ✅ Meets Tier 0 requirement
```

**Decision Required:**
- [ ] Approve NEGATIVE_TESTING_REQUIRED as Tier 0 instinct
- [ ] Approve 2:1 negative:positive test ratio target
- [ ] Approve Brain Protector challenge for insufficient negative tests
- [ ] Approve test generator automatic negative test creation

---

## 📊 Updated Implementation Plan Summary

### New Tier 0 Instincts (3 additions)

| Instinct | Rule ID | Impact |
|----------|---------|--------|
| Cleanup Forethought | CLEANUP_FORETHOUGHT | Every feature includes cleanup strategy |
| Negative Testing | NEGATIVE_TESTING_REQUIRED | 2:1 negative:positive test ratio |
| Report Archival | REPORT_ARCHIVAL_STRATEGY | Git + SQLite index for reports |

### Updated Phase Timeline

```
Phase -1: Architecture Validation        →  6-8 hours
Phase 0: Governance + CI/CD + Instincts  →  7-9 hours (+2 hrs for new instincts)
Phase 0.5: Migration Tools               →  3-4 hours
Phase 1: Working Memory + Cleanup        →  10-12 hours (+1 hr for cleanup)
Phase 2: Long-Term Knowledge + Cleanup   →  12-14 hours (+1 hr for cleanup)
Phase 3: Context Intelligence + Cleanup  →  12-14 hours (+1 hr for cleanup)
Phase 4: Agents + Negative Tests         →  15-19 hours (+2 hrs for negative tests)
Phase 5: Entry Point + Cleanup           →  8-10 hours (+1 hr for cleanup)
Phase 6: Migration Validation            →  5-7 hours
─────────────────────────────────────────────────────────────────
TOTAL: 78-97 hours (10-12 days focused work)
```

**Timeline Impact:**
- Original v2.0: 74-93 hours
- Updated v2.1: 78-97 hours
- Increase: +4 hours (cleanup instincts + negative testing)
- Net benefit: Prevents 10-20 hours of production issues

---

## ✅ What's Completed

### From Original Plan
- ✅ Crawlers designed and implemented (Week 1)
- ✅ BRAIN feeding functional (6 relationships, 12 patterns)
- ✅ Multi-threaded performance (3 seconds vs 5 minutes)
- ✅ Path handling robust (KDS standalone or embedded)
- ✅ Architecture design complete (7 documents, 6,450 lines)
- ✅ Phase plans complete (6 phases + Phase -1)
- ✅ Test specifications complete (196+ tests)
- ✅ Holistic review complete (risk analysis)

### From This Refinement (NEW)
- ✅ Report archival strategy defined
- ✅ Crawler migration plan defined
- ✅ Cleanup instinct specification
- ✅ Negative testing instinct specification
- ✅ Updated timeline with new instincts

---

## 📋 What's Left

### Design Phase (Remaining)
- [ ] Approve 3 new Tier 0 instincts
- [ ] Update governance.yaml with new rules
- [ ] Update phase plans with cleanup tasks
- [ ] Update test specifications with negative tests

### Implementation Phase (After Approval)
- [ ] Phase -1: Architecture Validation (6-8 hours)
- [ ] Phase 0: Governance + new instincts (7-9 hours)
- [ ] Phase 0.5: Migration Tools (3-4 hours)
- [ ] Phase 1-6: Implementation with cleanup + negative tests (62-77 hours)

**Total Remaining:** ~78-97 hours (10-12 days focused work)

---

## 🎯 Decisions Required

### 1. Report Archival Strategy
- [ ] Approve git-based archival with INDEX.md
- [ ] Approve SQLite index in Tier 3
- [ ] Approve automatic cleanup after milestone commits

### 2. Crawler Migration
- [ ] Approve crawler migration to CORTEX Tier 5
- [ ] Approve cleanup instincts as mandatory
- [ ] Approve real-time file watching enhancement

### 3. Cleanup Instinct (Tier 0)
- [ ] Approve CLEANUP_FORETHOUGHT as Tier 0 rule
- [ ] Approve mandatory cleanup phase in all feature plans
- [ ] Approve Brain Protector challenge for missing cleanup

### 4. Negative Testing Instinct (Tier 0)
- [ ] Approve NEGATIVE_TESTING_REQUIRED as Tier 0 rule
- [ ] Approve 2:1 negative:positive test ratio target
- [ ] Approve Brain Protector challenge for insufficient negative tests
- [ ] Approve test generator automatic negative test creation

### 5. Overall Plan
- [ ] Approve updated timeline (78-97 hours vs 74-93 hours)
- [ ] Approve +4 hour increase for new instincts
- [ ] Approve Implementation Plan v2.1

---

## 🚀 Next Steps (After Approval)

1. **Update governance.yaml** (1 hour)
   - Add CLEANUP_FORETHOUGHT rule
   - Add NEGATIVE_TESTING_REQUIRED rule
   - Add REPORT_ARCHIVAL_STRATEGY rule

2. **Update phase plans** (2 hours)
   - Add cleanup phases to all feature plans
   - Add negative test specifications
   - Update timelines

3. **Begin Phase -1** (6-8 hours)
   - Benchmark sql.js performance
   - Test browser compatibility
   - Validate unified schema
   - Create dashboard prototype

4. **Continue implementation** (Phase 0 → Phase 6)

---

**Status:** 🟡 AWAITING APPROVAL  
**Blockers:** 4 decisions needed (report archival, crawlers, cleanup instinct, negative testing)  
**Confidence:** VERY HIGH (all gaps addressed)  
**ROI:** +4 hrs upfront → Prevents 10-20 hrs production issues (2.5-5x savings)
