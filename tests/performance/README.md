# Performance Tests

This directory contains performance regression tests to ensure CORTEX maintains optimal speed as the system evolves.

## Test Coverage

**35 Performance Tests** covering:

### Tier 1 (Working Memory) - 5 tests
- `test_tier1_get_recent_conversations_performance` - Baseline: 0.46ms, Target: ≤50ms
- `test_tier1_get_conversation_by_id_performance` - Baseline: 0.64ms, Target: ≤50ms
- `test_tier1_get_messages_performance` - Baseline: 0.40ms, Target: ≤50ms
- `test_tier1_get_active_conversation_performance` - Baseline: 0.41ms, Target: ≤50ms
- `test_tier1_average_performance` - Baseline avg: 0.48ms, Target: ≤50ms

### Tier 2 (Knowledge Graph) - 4 tests
- `test_tier2_get_patterns_by_type_performance` - Baseline: 0.45ms, Target: ≤150ms
- `test_tier2_search_patterns_fts_performance` - Baseline: 1.01ms, Target: ≤150ms
- `test_tier2_find_patterns_by_tag_performance` - Baseline: 0.69ms, Target: ≤150ms
- `test_tier2_average_performance` - Baseline avg: 0.72ms, Target: ≤150ms

### Tier 3 (Context Intelligence) - 6 tests
- `test_tier3_get_git_metrics_performance` - Baseline: 0.40ms, Target: ≤500ms
- `test_tier3_analyze_file_hotspots_performance` - **HOTSPOT**: Baseline: 258ms, Target: ≤300ms
- `test_tier3_get_unstable_files_performance` - Baseline: 0.85ms, Target: ≤500ms
- `test_tier3_calculate_commit_velocity_performance` - Baseline: 0.51ms, Target: ≤500ms
- `test_tier3_get_context_summary_performance` - Baseline: 2.13ms, Target: ≤500ms
- `test_tier3_average_performance` - Baseline avg: 52.51ms, Target: ≤500ms

### Operations (End-to-End) - 6 tests
- `test_operation_help_command_performance` - Baseline: 462ms, Target: <1000ms
- `test_operation_story_refresh_performance` - Baseline: 9.45ms, Target: <5000ms
- `test_operation_cleanup_performance` - Baseline: 1452ms, Target: <5000ms
- `test_operation_demo_performance` - Baseline: 1473ms, Target: <5000ms
- `test_operation_environment_setup_performance` - Baseline: 3758ms, Target: <5000ms
- `test_operation_average_under_5s` - Baseline avg: 1431ms, Target: <5000ms

### Aggregate Tests - 4 tests
- `test_all_tiers_meet_targets` - Critical test: all tiers must pass
- `test_tier1_stays_under_budget` - Maintains 100× faster performance
- `test_tier2_stays_under_budget` - Maintains 208× faster performance

**Total: 25 tests** (matches baseline metrics from Phase 6.1)

## Running Tests

### Run all performance tests:
```bash
pytest tests/performance/ -v -m performance
```

### Run only fast tests (exclude slow operations):
```bash
pytest tests/performance/ -v -m "performance and not slow"
```

### Run specific tier tests:
```bash
pytest tests/performance/ -v -k "tier1"
pytest tests/performance/ -v -k "tier2"
pytest tests/performance/ -v -k "tier3"
```

### Run operation tests only:
```bash
pytest tests/performance/ -v -k "operation"
```

### Generate detailed report:
```bash
pytest tests/performance/ -v -m performance --tb=short --color=yes
```

## Test Markers

- `@pytest.mark.performance` - All performance tests
- `@pytest.mark.slow` - Tests that take >1s (operations, environment setup)

## Baseline Reference

All thresholds based on **Phase 6.1 Performance Baseline** established on 2025-11-10.

**Baseline Report:** `cortex-brain/cortex-2.0-design/PHASE-6.1-PERFORMANCE-BASELINE.md`

## CI Integration

These tests run automatically in CI pipeline to prevent performance regressions:

```yaml
# .github/workflows/performance.yml
- name: Run performance tests
  run: pytest tests/performance/ -v -m performance
```

**Build fails if any test exceeds threshold.**

## Hotspots

Known performance hotspots with stricter thresholds:

1. **Tier 3: `analyze_file_hotspots(30d)`** - 258ms (50% of Tier 3 time)
   - Cause: Git subprocess calls analyzing file churn
   - Target: ≤300ms (stricter than general 500ms)
   - Optimization: Add git log caching (Phase 6.2)

2. **Operation: `environment_setup`** - 3758ms (94% subprocess time)
   - Cause: Git operations (pull, status)
   - Target: <5000ms
   - Optimization: Add git status caching (Phase 6.2)

## Adding New Tests

When adding new operations or tier methods:

1. Run profiler to establish baseline:
   ```bash
   python scripts/profile_performance.py
   ```

2. Add test to `test_performance_regression.py`:
   ```python
   @pytest.mark.performance
   def test_new_operation_performance():
       """Baseline: Xms, Target: Yms"""
       @benchmark
       def operation():
           return your_operation()
       
       result, duration = operation()
       
       assert duration < THRESHOLD_MS, \
           f"Regression: {duration:.2f}ms (baseline: Xms, target: Yms)"
   ```

3. Update this README with new test details

## Performance Budget

Current performance exceeds targets by significant margins:

- **Tier 1:** 100× faster than target (0.48ms vs 50ms)
- **Tier 2:** 208× faster than target (0.72ms vs 150ms)
- **Tier 3:** 10× faster than target (52.51ms vs 500ms)
- **Operations:** 3.5× faster than target (1431ms vs 5000ms)

**Budget tests** ensure we maintain this exceptional performance.

## Troubleshooting

### Test failures due to empty database:
```
pytest.skip("No conversations in database")
```
**Solution:** Run CORTEX operations to populate test data, or use fixtures.

### Test timeouts:
**Solution:** Mark as slow: `@pytest.mark.slow`

### Flaky performance tests:
**Solution:** Run multiple iterations and use average:
```python
durations = [operation() for _ in range(5)]
avg_duration = sum(durations) / len(durations)
```

---

**Last Updated:** 2025-11-10  
**Phase:** 6.1 - Performance Profiling & Regression Tests  
**Status:** ✅ COMPLETE
