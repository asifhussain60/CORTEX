# Intelligence Testing Blind Spots Analysis
# Wave: Intelligence Consolidation (WAVE-IC-001) - Enhanced with Phase 65 + ENH-092
# Created: 2026-02-14
# Updated: 2026-02-14 (Intelligence fixes integrated)
# Authority: Test Architecture Review

## Executive Summary

Original test plan: 44 tests
Enhanced test plan: 88 tests (+44 tests, +100% increase)
Intelligence fixes integrated: Phase 65 S4/S5 + ENH-092 Phase 53.3

Coverage improvement: 75% → 95% (all new code)

## Blind Spots Discovered & Addressed

### Category 1: Meta-Failures (Intelligence About Intelligence)

**Problem:** Original tests assumed audit logger always works

**Blind Spots:**
1. **Audit logger crash mid-operation**
   - Scenario: Logger throws exception while writing AC_COMPLETE
   - Impact: Operation succeeds but no audit trail (compliance violation)
   - Solution: Transaction-based logging with rollback + memory buffer fallback

2. **Disk full during log write**
   - Scenario: Audit log file at 99.9% disk capacity
   - Impact: Log write fails silently, no error propagated
   - Solution: Pre-flight disk check + fallback to memory + alert threshold

3. **Log corruption detection**
   - Scenario: Filesystem corruption damages audit log
   - Impact: Undetected data loss, invalid compliance evidence
   - Solution: Checksum verification on read + periodic integrity checks

4. **Time drift (NTP failure)**
   - Scenario: System clock drifts -5 hours during operation
   - Impact: Out-of-order audit entries, compliance timeline invalid
   - Solution: Monotonic clock for ordering + timestamp correction on read

### Category 2: Cascade Failures (Sequential Intelligence Source Failures)

**Problem:** Original tests only tested single-source failures

**Blind Spots:**
5. **LENS → KG → Profile cascade**
   - Scenario: LENS times out (>10s) → KG unavailable → Profile missing
   - Impact: Zero intelligence returned, should fallback to CORTEX rules
   - Solution: Graceful degradation tiers (LENS fail → KG only → CORTEX only)

6. **Partial failure handling**
   - Scenario: LENS succeeds, KG fails, Profile succeeds
   - Impact: Incomplete intelligence context, unclear which source failed
   - Solution: Source availability bitmap + partial result metadata

7. **Transient vs permanent failures**
   - Scenario: KG returns 503 (retry-able) vs 404 (not retry-able)
   - Impact: Wasted retries on permanent failures, missed retries on transient
   - Solution: Failure classification + retry policy per error type

### Category 3: Concurrency Issues (Race Conditions & Thread Safety)

**Problem:** Original tests single-threaded only

**Blind Spots:**
8. **Session metrics race condition**
   - Scenario: 10 parallel requests updating same session_metrics dict
   - Impact: Lost updates, incorrect cumulative counts
   - Solution: Thread-safe Counter + atomic operations

9. **Policy hot-swap mid-evaluation**
   - Scenario: Policy changed while LENS trigger decision in progress
   - Impact: Decision uses mix of old + new policy (undefined behavior)
   - Solution: Policy versioning + decision uses snapshot

10. **Cache invalidation race**
    - Scenario: Policy change triggers cache clear during cache read
    - Impact: Reader gets partial cache (some entries cleared, some not)
    - Solution: Read-write lock + atomic cache swap

### Category 4: Resource Exhaustion (Memory Leaks & Accumulation)

**Problem:** Original tests short-lived sessions only

**Blind Spots:**
11. **Long-running session memory leak**
    - Scenario: Session with >1000 operations over 8 hours
    - Impact: Session metrics dict grows unbounded, OOM crash
    - Solution: Rolling window (keep last 1000 ops) + auto-archive

12. **Cycle metrics accumulation**
    - Scenario: Multi-cycle RGR runs 100 cycles (max_cycles=100)
    - Impact: cycle_metrics list grows to 100 items, high memory usage
    - Solution: Streaming metrics (write to disk per cycle) + summary only in memory

13. **Log rotation failure**
    - Scenario: Audit log reaches 10MB but rotation script fails
    - Impact: Log continues growing, fills disk, system crash
    - Solution: Hard limit (15MB = stop logging + alert) + emergency truncation

### Category 5: Boundary Conditions (Edge Values & Limits)

**Problem:** Original tests typical values only

**Blind Spots:**
14. **Empty/null inputs**
    - Scenario: session_id=None, file_path="", intent=""
    - Impact: Crashes or undefined behavior
    - Solution: Input validation + default generation (UUID for session_id)

15. **Extremely large files**
    - Scenario: LENS trigger on 50MB Python file
    - Impact: LENS analysis times out (>10s), no fallback
    - Solution: File size check before LENS (>10MB = skip LENS, warn)

16. **Impossible criteria**
    - Scenario: SuccessCriteria(coverage=1.0, complexity=0)
    - Impact: Infinite loop (criteria can never be met)
    - Solution: Criteria validation (feasibility check) + warn on impossible

17. **Oscillating metrics**
    - Scenario: Cycle 1: coverage=0.8 → Cycle 2: 0.6 → Cycle 3: 0.9
    - Impact: Loop never stabilizes, runs until max_cycles
    - Solution: Oscillation detection (variance > threshold → stop)

### Category 6: File System Edge Cases (Non-Code Files & Permissions)

**Problem:** Original tests assumed valid Python files

**Blind Spots:**
18. **Binary file LENS trigger**
    - Scenario: LENS trigger on .jpg, .pdf, .exe file
    - Impact: LENS AST analysis fails, no error handling
    - Solution: File type check (magic bytes) before LENS engagement

19. **Permission denied**
    - Scenario: LENS trigger on file_path without read permission
    - Impact: LENS reads fail, crashes or silent failure
    - Solution: Permission check before LENS + graceful skip

20. **Circular symlink**
    - Scenario: file_path points to symlink loop (a → b → a)
    - Impact: LENS follows symlinks infinitely, hangs
    - Solution: Symlink depth limit (3 hops max) + loop detection

21. **Deleted file mid-analysis**
    - Scenario: File deleted between trigger decision and LENS analysis
    - Impact: LENS reads missing file, crashes
    - Solution: File existence check immediately before LENS + retry once

### Category 7: Performance Degradation (Latency & Throughput)

**Problem:** Original tests no performance benchmarks

**Blind Spots:**
22. **High-throughput audit logging**
    - Scenario: 1000 intelligence operations per second sustained
    - Impact: Audit logger becomes bottleneck, slows all operations
    - Solution: Async logging queue + batch writes + backpressure

23. **Policy decision latency**
    - Scenario: Custom policy makes network call (>5s latency)
    - Impact: Every LENS trigger decision waits 5s (unusable)
    - Solution: Policy timeout (5s = fallback to DefaultPolicy) + warn

24. **Cache thrashing**
    - Scenario: 1000 unique intents in 1 minute (no cache hits)
    - Impact: LENS invoked 1000 times, extreme latency
    - Solution: LRU cache eviction + pre-warming + size limit

### Category 8: Integration Failures (Cross-Component Breakage)

**Problem:** Original tests components in isolation

**Blind Spots:**
25. **MCP gate bypass via LENS**
    - Scenario: LENS triggered without MCP gate check
    - Impact: CORE-049 violation (MCP-FIRST bypassed)
    - Solution: LENS trigger respects MCP availability + blocks if unavailable

26. **Mode detection edge cases**
    - Scenario: Repository has .cortex/ but no cortex/__init__.py
    - Impact: Ambiguous mode (ARCHITECT or PRODUCTION?)
    - Solution: Multi-marker voting (2 of 3 markers = high confidence)

27. **Cross-orchestrator intelligence sharing**
    - Scenario: TDDOrchestrator fetches intelligence, RefactoringOrchestrator refetches same
    - Impact: Duplicate LENS calls, wasted resources
    - Solution: Session-scoped intelligence cache (shared across orchestrators)

## Test Enhancement Breakdown

### T1.1: Intelligence Audit Trail + Phase 65 Integration
- **Original:** 8 tests (happy path only)
- **Enhanced:** 24 tests (+16 edge cases, Phase 65 integration)
- **Added scenarios:**
  - Meta-failure (audit logger crash)
  - Cascade failure (all sources fail)
  - Memory leak detection (>1000 ops)
  - Log rotation and archival
  - High-throughput stress test (1000 ops/sec)
  - **Phase 65 S5:** TurnContext integration for turn-over-turn accumulation
  - **Phase 65 S5:** Session profile storage with audit trail
  - **Phase 65 S5:** Thread-safe turn context operations
  - **Phase 65 S5:** Turn-level intelligence queryability

### T1.2: LENS Trigger Extraction + Lifecycle Hook Integration
- **Original:** 12 tests (basic triggers + policies)
- **Enhanced:** 28 tests (+16 edge cases, ENH-092 integration)
- **Added scenarios:**
  - Binary file handling
  - Permission denied
  - Circular symlinks
  - Extremely large files (>10MB)
  - Policy timeout (>5s)
  - Cache invalidation on policy change
  - **ENH-092:** Lifecycle hook logging for LENS decisions
  - **ENH-092:** Automatic cleanup on wave/phase completion
  - **ENH-092:** LENS decision audit trail queryable
  - **ENH-092:** Event-driven LENS trigger auditing

### T1.3: Refactoring Multi-Cycle RGR
- **Original:** 10 tests (basic cycles + safety)
- **Enhanced:** 22 tests (+12 edge cases)
- **Added scenarios:**
  - Oscillation detection
  - Regression cascade
  - Impossible criteria
  - Conflicting goals
  - Hard timeout (30min)
  - Memory accumulation prevention

## Chaos Testing Strategy

### Purpose
Simulate real-world failures that tests can't predict

### Intelligence Audit Chaos
1. **Kill audit logger mid-write** → Transaction rollback verified
2. **Fill disk to 100%** → Memory buffer fallback verified
3. **Corrupt log file** → Checksum detection verified
4. **Drift system clock** → Monotonic ordering verified

### LENS Trigger Chaos
1. **Policy server unavailable** → Local cache fallback verified
2. **File system lag (>10s)** → Timeout handling verified
3. **Concurrent policy updates** → Version conflict resolution verified
4. **Corrupted policy JSON** → Schema validation verified

### Multi-Cycle RGR Chaos
1. **Test framework crash** → Resume from checkpoint verified
2. **Metric collection failure** → Default values used verified
3. **Criteria file modified** → Reload + warning verified
4. **Process kill mid-refactor** → Atomic rollback verified

## Coverage Improvement

| Component | Original | Enhanced | Improvement |
|-----------|----------|----------|-------------|
| Intelligence Audit | 75% | 95% | +20% |
| LENS Triggers | 70% | 95% | +25% |
| Multi-Cycle RGR | 80% | 95% | +15% |
| Error Paths | 30% | 90% | +60% |
| Concurrency | 0% | 85% | +85% |
| Chaos Scenarios | 0% | 70% | +70% |

## Implementation Priority

### P0 (Critical - Must Have)
- Meta-failure handling (audit logger crash)
- Cascade failure graceful degradation
- Session metrics thread-safety
- File size check before LENS (>10MB)
- Impossible criteria validation

### P1 (Important - Should Have)
- Memory leak prevention (long sessions)
- Log rotation and archival
- Policy timeout handling
- Oscillation detection
- MCP gate integration check

### P2 (Nice to Have - Could Have)
- High-throughput stress tests
- Chaos testing automation
- Performance benchmarking suite
- Cross-orchestrator intelligence sharing
- Cache thrashing prevention

## Verification Checklist

Before wave completion:
- [ ] All 80 tests passing (44 original + 36 new)
- [ ] 95%+ coverage on all new code
- [ ] All P0 blind spots addressed in implementation
- [ ] Chaos testing scenarios documented
- [ ] Performance benchmarks established
- [ ] Memory leak tests verified (>1000 ops)
- [ ] Concurrency tests verified (10 parallel sessions)
- [ ] Integration tests verified (cross-orchestrator)

## Lessons Learned

### For Future Intelligence Tests

1. **Always test meta-failures** (intelligence about intelligence)
2. **Always test cascade failures** (sequential source failures)
3. **Always test long-running sessions** (memory leaks)
4. **Always test concurrency** (race conditions)
5. **Always test file system edge cases** (permissions, symlinks, binary files)
6. **Always test performance** (throughput, latency, caching)
7. **Always test integration** (cross-component breakage)
8. **Always include chaos testing** (unpredictable real-world failures)

### Test Smell Indicators

Red flags that suggest blind spots:
- ❌ All tests pass in <1s (no long-running scenarios)
- ❌ No tests with concurrent requests (missing race conditions)
- ❌ No tests that intentionally crash components (missing failure modes)
- ❌ No tests with extremely large inputs (missing boundary conditions)
- ❌ No tests with filesystem operations (missing permission/symlink issues)
- ❌ No tests that measure memory usage (missing leak detection)
- ❌ No tests that simulate external service failures (missing network issues)
- ❌ No tests with impossible inputs (missing validation checks)

## Next Wave Improvements

For future waves, enhance testing from day 1:
1. Generate edge case tests automatically from implementation
2. Use property-based testing (hypothesis) for input validation
3. Use mutation testing to verify test quality
4. Add continuous chaos testing in CI/CD pipeline
5. Establish performance budgets (max latency, max memory)
6. Track test coverage trends (prevent regression)
7. Create test templates for common patterns (audit, concurrency, chaos)
