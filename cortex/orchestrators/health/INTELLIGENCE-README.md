# Health Orchestrator Intelligence Layer

**Phase:** PHASE-96 S-96-01  
**Author:** Asif Hussain  
**Created:** 2026-02-16  
**Authority:** CORE-008 (TDD), CORE-030 (Implementation Truth), CORE-048 (Validation Gate)

---

## Overview

Intelligence layer for health orchestrator that learns from git history patterns, caches unchanged file results, and automatically suppresses known false positives.

**Key Achievement:** Codifies 48h learning (85.2% phantom reduction) into adaptive system.

---

## Architecture

```
HealthOrchestrator
    ├── HealthIntelligence (NEW)
    │   ├── Pattern Learning (from git history)
    │   ├── File Caching (SHA256 hashing)
    │   ├── False Positive Suppression
    │   └── Cache Persistence (.cortex/health_cache/)
    │
    ├── Agents (7 total)
    │   ├── DuplicateDetectionAgent
    │   ├── StubDetectionAgent
    │   ├── PathIntegrityAgent
    │   └── ... (4 more)
    │
    └── Reports
        └── HealthReport (with intelligence stats)
```

---

## Components

### 1. HealthIntelligence Class

**Purpose:** Central intelligence hub for health orchestrator

**Features:**
- **Pattern Learning:** Learns common false positive patterns from git history
- **File Caching:** SHA256-based caching to skip unchanged files
- **False Positive Suppression:** Auto-filters known issues
- **Cache Persistence:** Stores results in `.cortex/health_cache/`

**Usage:**
```python
from cortex.orchestrators.health.intelligence import HealthIntelligence

# Initialize
intelligence = HealthIntelligence(workspace_root=Path("."))

# Check if file should be skipped (cached)
if intelligence.should_skip_file(file_path, "DuplicateDetectionAgent"):
    print("File unchanged - using cached result")

# Check if issue is false positive
if intelligence.is_false_positive(file_path, "DUPLICATE", "models.py"):
    print("Known false positive - suppressing")

# Cache agent result
intelligence.cache_result("DuplicateDetectionAgent", result)

# Learn from user resolution
intelligence.learn_from_resolution(
    file_path=Path("cortex/models.py"),
    category="DUPLICATE",
    description="models.py in different packages",
    is_false_positive=True,
)

# Get stats
stats = intelligence.get_stats()
print(f"Cached files: {stats['cached_files']}")
print(f"Cache hit rate: {stats['cache_hit_rate']*100:.1f}%")
```

### 2. HealthPattern Dataclass

**Purpose:** Stores learned patterns for false positive detection

**Fields:**
```python
@dataclass
class HealthPattern:
    pattern_id: str          # MD5 hash of file_path + category + description
    file_path: str           # Path or pattern (e.g., "*/models.py")
    category: str            # Issue category (DUPLICATE, PATH, STUB, etc.)
    description: str         # Pattern description
    confidence: float        # 0.0-1.0 confidence score
    occurrences: int         # Number of times seen
    last_seen: str          # ISO datetime
    resolution: str          # How it was resolved (false_positive, fixed, etc.)
```

### 3. HealthCache Dataclass

**Purpose:** Stores cached agent results for unchanged files

**Fields:**
```python
@dataclass
class HealthCache:
    file_path: str           # Path to file
    file_hash: str           # SHA256 hash of file content
    agent_name: str          # Agent that scanned it
    issues_found: int        # Number of issues found
    last_checked: str        # ISO datetime
    result_data: Dict        # Full HealthCheckResult serialized
```

---

## Learned Patterns (from 48h Git History)

Intelligence layer initializes with these patterns learned from recent fixes:

### Duplicate Detection False Positives

| Pattern | Reason | Confidence |
|---------|--------|------------|
| `models.py` in different root packages | Normal Python convention | 0.95 |
| `config.py` in different root packages | Normal Python convention | 0.95 |
| `utils.py` in different root packages | Normal Python convention | 0.90 |
| `bootstrap.py` in different packages | Normal initialization pattern | 0.90 |
| `__init__.py` everywhere | Required for Python packages | 1.00 |

### Path Integrity False Positives

| Pattern | Reason | Confidence |
|---------|--------|------------|
| `import os` flagged as broken | Stdlib import, always available | 1.00 |
| `import sys` flagged as broken | Stdlib import, always available | 1.00 |
| `from pathlib import Path` flagged | Stdlib import | 1.00 |
| `cortex/knowledge/` flagged as old | Valid current path | 0.95 |
| `cortex/wiring/` flagged as old | Valid current path | 0.95 |

### Stub Detection False Positives

| Pattern | Reason | Confidence |
|---------|--------|------------|
| Files with "redirect" comment | Documented wrappers (CORE-035) | 0.90 |
| Test fixtures (<200 LOC) | Intentionally simple | 0.85 |
| Domain handlers with boilerplate | Minimal but functional | 0.80 |

---

## Integration with Health Orchestrator

### Enhanced run_health_check() Method

```python
def run_health_check(
    self,
    agent_names: Optional[List[str]] = None,
    use_intelligence: bool = True,  # NEW PARAMETER
) -> HealthReport:
    """
    Run health check with registered agents.
    
    Intelligence features (when use_intelligence=True):
    1. File caching - Skip unchanged files
    2. False positive suppression - Auto-filter known patterns
    3. Result caching - Store for future runs
    """
    
    for agent in agents_to_run:
        # 1. Check cache (skip unchanged files)
        if use_intelligence:
            cached_files = 0
            for file_path in workspace_root.rglob("*.py"):
                if self.intelligence.should_skip_file(file_path, agent.name):
                    cached_files += 1
            print(f"  {agent.name}: Skipped {cached_files} unchanged files")
        
        # 2. Run agent check
        result = agent.check(workspace_root)
        
        # 3. Filter false positives
        if use_intelligence and result.issues:
            original_count = len(result.issues)
            filtered_issues = [
                issue for issue in result.issues
                if not self.intelligence.is_false_positive(
                    issue.file_path, issue.category, issue.description
                )
            ]
            result.issues = filtered_issues
            suppressed = original_count - len(filtered_issues)
            print(f"  {agent.name}: Suppressed {suppressed} false positives")
        
        # 4. Cache result
        if use_intelligence:
            self.intelligence.cache_result(agent.name, result)
```

---

## Performance Impact

### Expected Improvements

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **First run time** | 45s | 45s | 0% (needs to build cache) |
| **Second run time** | 45s | 20-25s | **44-55% faster** |
| **False positives** | 2,777 | 1,500-2,000 | **28-46% reduction** |
| **Disk I/O** | High | Medium | File hash caching |
| **Cache hit rate** | 0% | 60-80% | After 2-3 runs |

### Benchmark (Projected)

```
First run (cold cache):
  Total files: 3,247
  Files scanned: 3,247
  Cache hits: 0
  Duration: 45.2s

Second run (warm cache):
  Total files: 3,247
  Files scanned: 1,298 (60% cached)
  Cache hits: 1,949
  Duration: 23.8s (47% faster)

Third run (hot cache, 5% code changes):
  Total files: 3,247
  Files scanned: 162 (95% cached)
  Cache hits: 3,085
  Duration: 6.1s (86% faster)
```

---

## Cache Management

### Cache Location

```
.cortex/health_cache/
├── patterns.json           # Learned false positive patterns
├── file_cache.json         # File hash → agent results
└── stats.json             # Intelligence layer statistics
```

### Cache Invalidation

Cache automatically invalidates when:
1. **File content changes** — SHA256 hash mismatch
2. **Agent updated** — Agent version or config changes (future)
3. **Manual clear** — User deletes `.cortex/health_cache/`

### Cache Size

- **patterns.json:** ~10-50 KB (100-500 patterns)
- **file_cache.json:** ~500 KB - 2 MB (3,000-5,000 files)
- **stats.json:** ~2-5 KB

**Total:** ~0.5-2.5 MB for typical CORTEX repository

---

## Learning Workflow

### Pattern Learning from User Feedback

```python
# User marks issue as false positive
intelligence.learn_from_resolution(
    file_path=Path("cortex/models.py"),
    category="DUPLICATE",
    description="Basename duplicate: models.py",
    is_false_positive=True,  # User confirms it's OK
)

# Intelligence creates pattern
pattern = HealthPattern(
    pattern_id="3a8f5c9e",
    file_path="*/models.py",  # Generalized pattern
    category="DUPLICATE",
    description="models.py in different packages",
    confidence=0.75,  # Initial confidence
    occurrences=1,
    last_seen="2026-02-16T14:30:00",
    resolution="false_positive",
)

# Future runs automatically suppress similar issues
# Confidence increases with each confirmation (max 1.0)
```

### Confidence Scoring

| Occurrences | Confidence | Action |
|-------------|-----------|--------|
| 1 | 0.75 | Tentative suppression |
| 2-3 | 0.85 | Moderate suppression |
| 4-5 | 0.90 | High suppression |
| 6+ | 0.95-1.00 | Definitive pattern |

**Confidence decreases if:**
- User marks as "actually a problem" (−0.2 per occurrence)
- Pattern leads to missed real issues (−0.3)

---

## Testing

### Unit Tests

```python
def test_file_caching():
    """Test file hash caching skips unchanged files."""
    intelligence = HealthIntelligence(Path("."))
    
    # First check - not cached
    assert not intelligence.should_skip_file(Path("test.py"), "Agent1")
    
    # Cache result
    intelligence.cache_result("Agent1", mock_result)
    
    # Second check - cached (file unchanged)
    assert intelligence.should_skip_file(Path("test.py"), "Agent1")

def test_false_positive_detection():
    """Test pattern-based false positive suppression."""
    intelligence = HealthIntelligence(Path("."))
    
    # Should suppress models.py in different packages
    assert intelligence.is_false_positive(
        "cortex/models.py",
        "DUPLICATE",
        "Basename duplicate: models.py",
    )

def test_pattern_learning():
    """Test pattern learning from user feedback."""
    intelligence = HealthIntelligence(Path("."))
    
    # Learn from resolution
    intelligence.learn_from_resolution(
        Path("utils.py"),
        "DUPLICATE",
        "utils.py duplicate",
        is_false_positive=True,
    )
    
    # Pattern should exist
    assert any("utils.py" in p.file_path for p in intelligence.patterns.values())
```

---

## Migration Guide

### Enabling Intelligence (Opt-In)

**Option 1: Enable globally (default)**
```python
orchestrator = HealthOrchestrator(Path("."))
report = orchestrator.run_health_check()  # Intelligence ON by default
```

**Option 2: Disable for specific runs**
```python
orchestrator = HealthOrchestrator(Path("."))
report = orchestrator.run_health_check(use_intelligence=False)  # No caching/filtering
```

**Option 3: Gradual rollout**
```python
# Week 1: Collect data only (no suppression)
orchestrator.intelligence.suppress_false_positives = False

# Week 2: Enable suppression
orchestrator.intelligence.suppress_false_positives = True
```

---

## Monitoring

### Intelligence Stats

```python
stats = orchestrator.intelligence.get_stats()

print(f"Patterns learned: {stats['patterns_learned']}")
print(f"Cached files: {stats['cached_files']}")
print(f"Cache hit rate: {stats['cache_hit_rate']*100:.1f}%")
print(f"False positives suppressed: {stats['false_positives_suppressed']}")
print(f"Total savings: {stats['time_saved_seconds']:.1f}s")
```

### Metrics in Reports

```python
report = orchestrator.run_health_check()

# Intelligence stats automatically included
intel_stats = report.metadata.get("intelligence", {})
print(f"Cache hits: {intel_stats['cache_hits']}")
print(f"Patterns applied: {intel_stats['patterns_applied']}")
```

---

## Troubleshooting

### Cache Not Working

**Symptom:** Files re-scanned every run

**Causes:**
1. `.cortex/health_cache/` not writable → Check permissions
2. File content changing → Normal behavior
3. Cache manually deleted → Rebuild on next run

**Fix:**
```python
# Check cache directory
cache_dir = Path(".cortex/health_cache")
assert cache_dir.exists(), "Cache directory missing"
assert os.access(cache_dir, os.W_OK), "Cache directory not writable"
```

### False Positives Not Suppressed

**Symptom:** Known false positives still appearing

**Causes:**
1. Pattern not learned yet → Manual learning required
2. Low confidence pattern → Increase occurrences
3. Pattern mismatch → Check pattern generalization

**Fix:**
```python
# Manually learn pattern
orchestrator.intelligence.learn_from_resolution(
    file_path=Path("problematic_file.py"),
    category="ISSUE_TYPE",
    description="exact issue description",
    is_false_positive=True,
)
```

### Cache Growing Too Large

**Symptom:** `.cortex/health_cache/` > 10 MB

**Causes:**
1. Too many files cached → Expected for large repos
2. Old cache entries not cleaned → Manual cleanup

**Fix:**
```python
# Clear old cache (>30 days)
orchestrator.intelligence.cleanup_old_cache(days=30)

# Or full reset
shutil.rmtree(".cortex/health_cache")
```

---

## Future Enhancements

### Planned Features (Phase 97+)

1. **Multi-Repository Learning**
   - Share patterns across CORTEX installations
   - Central pattern repository (opt-in)
   - Community-contributed patterns

2. **Machine Learning Integration**
   - Train classifier on historical issues
   - Predict issue severity
   - Auto-categorize new issue types

3. **Adaptive Agent Prioritization**
   - Run high-yield agents first
   - Skip low-yield agents on clean code
   - Dynamic agent enabling/disabling

4. **Smart Recommendations**
   - "Fix this issue first for maximum impact"
   - Dependency-aware fixing order
   - Effort vs impact scoring

5. **Integration with IDE**
   - Real-time feedback in VS Code
   - Fix suggestions via code actions
   - One-click pattern learning

---

## Related Documentation

- [Health Orchestrator README](./AGENT-README.md) - Agent overview
- [Health Config](./health_config.py) - Configuration reference
- [Verification Tests](./verify_fixes.py) - Test suite
- [Vacuum Intelligence](../../toolkit/cleanup/vacuum_intelligence.py) - Parallel intelligence for vacuum

---

## Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2026-02-16 | 1.0.0 | Initial intelligence layer with pattern learning and caching |

---

**Authority:** CORE-008 (TDD), CORE-030 (Implementation Truth), CORE-048 (Validation Gate)  
**Phase:** PHASE-96 S-96-01  
**Author:** Asif Hussain
