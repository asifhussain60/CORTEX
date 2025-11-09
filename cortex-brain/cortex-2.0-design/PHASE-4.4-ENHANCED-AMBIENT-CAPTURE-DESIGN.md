# CORTEX 2.0 - Phase 4.4: Enhanced Ambient Capture

**Date:** November 9, 2025  
**Author:** Asif Hussain  
**Status:** 🔄 IN PROGRESS  
**Estimated Effort:** 8-12 hours  
**Priority:** HIGH

---

## 📋 Executive Summary

Phase 4.4 enhances the ambient capture daemon with intelligent filtering, pattern detection, activity scoring, and auto-summarization. These improvements dramatically increase the quality of background context capture, improving "continue" command success rates from 85% to 90%+.

**Key Enhancements:**
1. 🎯 **Smart File Filtering** - Ignore noise, focus on meaningful changes
2. 🔍 **Change Pattern Detection** - Identify refactors vs features vs fixes
3. 📊 **Activity Scoring** - Prioritize important changes
4. 📝 **Auto-Summarization** - Generate natural language context

---

## 🎯 Success Criteria

| Metric | Target | Measurement |
|--------|--------|-------------|
| **Noise Reduction** | 70%+ | Irrelevant events filtered |
| **Pattern Accuracy** | 85%+ | Correct change type classification |
| **Scoring Precision** | 80%+ | High-priority changes identified correctly |
| **Summary Quality** | 4/5+ | Human readability score |
| **Continue Success** | 90%+ | "Continue" command success rate |
| **Performance** | <150ms | Processing time per event batch |
| **Test Coverage** | 80%+ | Code coverage |

---

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   Ambient Capture Daemon                     │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  File Change Event                                           │
│         ↓                                                    │
│  ┌────────────────────┐                                     │
│  │  Smart Filter      │ → Ignore noise (build artifacts,    │
│  │  (NEW)             │   temp files, etc.)                 │
│  └────────────────────┘                                     │
│         ↓                                                    │
│  ┌────────────────────┐                                     │
│  │  Pattern Detector  │ → Classify: refactor, feature,     │
│  │  (NEW)             │   bug fix, documentation           │
│  └────────────────────┘                                     │
│         ↓                                                    │
│  ┌────────────────────┐                                     │
│  │  Activity Scorer   │ → Assign priority score (0-100)    │
│  │  (NEW)             │                                     │
│  └────────────────────┘                                     │
│         ↓                                                    │
│  ┌────────────────────┐                                     │
│  │  Debouncer         │ → Batch related events              │
│  │  (EXISTING)        │                                     │
│  └────────────────────┘                                     │
│         ↓                                                    │
│  ┌────────────────────┐                                     │
│  │  Auto-Summarizer   │ → Generate natural language         │
│  │  (NEW)             │   summary of changes               │
│  └────────────────────┘                                     │
│         ↓                                                    │
│  ┌────────────────────┐                                     │
│  │  Tier 1 Storage    │ → Store enriched context           │
│  │  (EXISTING)        │                                     │
│  └────────────────────┘                                     │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

---

## 🎯 Component 1: Smart File Filtering

### Purpose
Eliminate noise by intelligently filtering out irrelevant file changes.

### Design

**Filter Categories:**

1. **Build Artifacts**
   - `**/*.pyc`, `**/__pycache__/**`
   - `**/bin/**`, `**/obj/**`, `**/build/**`, `**/dist/**`
   - `**/node_modules/**`, `**/package-lock.json`
   - `**/.next/**`, `**/.nuxt/**`

2. **Temporary Files**
   - `**/*.tmp`, `**/*.temp`, `**/*.swp`, `**/*~`
   - `**/.DS_Store`, `**/Thumbs.db`
   - `**/*.log` (unless in `logs/` directory)

3. **Auto-Generated Files**
   - Files with `@generated` marker in header
   - Files in `generated/` directories
   - `**/*.generated.*`

4. **Version Control**
   - `**/.git/**`, `**/.svn/**`, `**/.hg/**`
   - Git lock files, pack files

5. **IDE/Editor Files**
   - `**/.vscode/**` (except settings)
   - `**/.idea/**`
   - `**/*.suo`, `**/*.user`

**Smart Heuristics:**

```python
def is_noise_file(file_path: Path) -> bool:
    """Determine if file is noise using smart heuristics."""
    
    # Check extension whitelist
    if file_path.suffix not in ALLOWED_EXTENSIONS:
        return True
        
    # Check for auto-generated marker
    if has_generated_marker(file_path):
        return True
        
    # Check file size (> 1MB likely binary/generated)
    if file_path.stat().st_size > 1024 * 1024:
        return True
        
    # Check path patterns
    path_str = str(file_path).lower()
    if any(pattern in path_str for pattern in NOISE_PATTERNS):
        return True
        
    return False
```

### Implementation Plan

1. Create `SmartFileFilter` class in `auto_capture_daemon.py`
2. Add `is_noise_file()` method with heuristics
3. Add `has_generated_marker()` helper
4. Update `FileSystemWatcher._on_file_changed()` to call filter
5. Add configuration for filter rules (extensible)

### Testing

- Unit tests for each filter category
- False positive/negative rate tests
- Performance benchmarks (< 5ms per file)

---

## 🔍 Component 2: Change Pattern Detection

### Purpose
Classify file changes to understand developer intent.

### Design

**Change Patterns:**

1. **Refactoring** (REFACTOR)
   - File renames/moves
   - Function/class renames
   - Code restructuring without logic changes
   - Import reorganization

2. **New Feature** (FEATURE)
   - New files created
   - New functions/classes added
   - Significant LOC additions (>50 lines)
   - New dependencies added

3. **Bug Fix** (BUGFIX)
   - Small targeted changes (<20 lines)
   - Changes in error handling
   - Test file modifications
   - Commit message contains "fix", "bug", "issue"

4. **Documentation** (DOCS)
   - Markdown file changes
   - Comment additions
   - README updates
   - Docstring changes

5. **Configuration** (CONFIG)
   - JSON/YAML config files
   - Environment files (.env)
   - Build configuration

**Detection Algorithm:**

```python
class ChangePatternDetector:
    """Detect change patterns in file modifications."""
    
    def detect_pattern(self, event: Dict[str, Any]) -> str:
        """Classify change pattern."""
        
        file_path = Path(event['file'])
        event_type = event['event']
        
        # File extension analysis
        if file_path.suffix == '.md':
            return 'DOCS'
        
        if file_path.suffix in {'.json', '.yaml', '.yml', '.env'}:
            return 'CONFIG'
        
        # Event type analysis
        if event_type == 'created':
            return 'FEATURE'
        
        if event_type == 'deleted':
            return 'REFACTOR'
        
        # Modified files require deeper analysis
        if event_type == 'modified':
            return self._analyze_modification(file_path)
        
        return 'UNKNOWN'
    
    def _analyze_modification(self, file_path: Path) -> str:
        """Analyze modified file for pattern."""
        
        # Get git diff if available
        diff_lines = self._get_git_diff(file_path)
        
        if not diff_lines:
            return 'UNKNOWN'
        
        # Count additions/deletions
        additions = sum(1 for line in diff_lines if line.startswith('+'))
        deletions = sum(1 for line in diff_lines if line.startswith('-'))
        
        # Refactoring: Similar adds/deletes
        if abs(additions - deletions) < 5:
            return 'REFACTOR'
        
        # Feature: More additions
        if additions > deletions * 2 and additions > 50:
            return 'FEATURE'
        
        # Bug fix: Small targeted change
        if additions + deletions < 20:
            return 'BUGFIX'
        
        return 'UNKNOWN'
```

### Implementation Plan

1. Create `ChangePatternDetector` class
2. Implement pattern detection logic
3. Add git diff analysis helper
4. Add AST-based analysis for Python files (optional, future)
5. Cache detection results to avoid recomputation

### Testing

- Test each pattern category with real examples
- Measure accuracy against manual classification
- Edge case handling (empty files, binary files)

---

## 📊 Component 3: Activity Scoring System

### Purpose
Prioritize changes by importance to focus context capture.

### Design

**Scoring Factors:**

1. **File Type Weight** (0-40 points)
   - Source code (.py, .ts, .cs): 40 points
   - Configuration (.json, .yaml): 30 points
   - Documentation (.md): 20 points
   - Other: 10 points

2. **Change Magnitude** (0-30 points)
   - Large changes (>100 LOC): 30 points
   - Medium changes (20-100 LOC): 20 points
   - Small changes (<20 LOC): 10 points

3. **Change Pattern** (0-20 points)
   - FEATURE: 20 points
   - BUGFIX: 15 points
   - REFACTOR: 10 points
   - CONFIG: 8 points
   - DOCS: 5 points

4. **File Importance** (0-10 points)
   - Core modules (`src/`, `lib/`): 10 points
   - Tests (`tests/`): 8 points
   - Scripts: 5 points
   - Other: 3 points

**Scoring Algorithm:**

```python
class ActivityScorer:
    """Score file change activity by importance."""
    
    FILE_TYPE_WEIGHTS = {
        '.py': 40, '.ts': 40, '.tsx': 40, '.cs': 40,
        '.json': 30, '.yaml': 30, '.yml': 30,
        '.md': 20,
        'default': 10
    }
    
    PATTERN_WEIGHTS = {
        'FEATURE': 20,
        'BUGFIX': 15,
        'REFACTOR': 10,
        'CONFIG': 8,
        'DOCS': 5,
        'UNKNOWN': 5
    }
    
    def score_activity(self, event: Dict[str, Any], pattern: str) -> int:
        """Calculate activity score (0-100)."""
        
        file_path = Path(event['file'])
        
        # File type weight
        ext = file_path.suffix
        file_type_score = self.FILE_TYPE_WEIGHTS.get(ext, self.FILE_TYPE_WEIGHTS['default'])
        
        # Change magnitude (estimate from event type)
        magnitude_score = self._estimate_magnitude(event)
        
        # Pattern weight
        pattern_score = self.PATTERN_WEIGHTS.get(pattern, 5)
        
        # File importance
        importance_score = self._calculate_importance(file_path)
        
        # Total score (capped at 100)
        total = min(100, file_type_score + magnitude_score + pattern_score + importance_score)
        
        return total
    
    def _calculate_importance(self, file_path: Path) -> int:
        """Calculate file importance based on path."""
        path_str = str(file_path).lower()
        
        if '/src/' in path_str or '/lib/' in path_str:
            return 10
        elif '/tests/' in path_str or '/test/' in path_str:
            return 8
        elif '/scripts/' in path_str:
            return 5
        else:
            return 3
```

### Implementation Plan

1. Create `ActivityScorer` class
2. Implement scoring algorithm
3. Add configuration for weights (tunable)
4. Store scores with events in Tier 1
5. Use scores to prioritize context loading

### Testing

- Test scoring with diverse file types
- Validate score distribution (avoid clustering)
- Benchmark scoring performance (< 2ms per event)

---

## 📝 Component 4: Auto-Summarization

### Purpose
Generate human-readable summaries of workspace activity.

### Design

**Summarization Levels:**

1. **Event Summary** (per file change)
   ```
   "Modified src/tier1/memory.py: Bug fix in query_memory() - added null check"
   ```

2. **Batch Summary** (debounced events)
   ```
   "Refactored 3 modules in src/tier1/: Renamed functions for clarity, 
    updated 5 tests. Score: 75/100"
   ```

3. **Session Summary** (daily/hourly rollup)
   ```
   "Work session 2025-11-09 14:00-16:30: Implemented smart filtering in 
    ambient capture (Phase 4.4). Added SmartFileFilter class with 5 
    filter categories. Created 8 unit tests. High-priority changes in 
    auto_capture_daemon.py (score: 95/100)."
   ```

**Summarization Algorithm:**

```python
class AutoSummarizer:
    """Generate natural language summaries of changes."""
    
    def summarize_event(self, event: Dict[str, Any], pattern: str, score: int) -> str:
        """Create event-level summary."""
        
        file_path = event['file']
        event_type = event['event']
        
        # Template-based generation
        template = self._get_template(event_type, pattern)
        summary = template.format(
            file=file_path,
            pattern=pattern.lower(),
            score=score
        )
        
        return summary
    
    def summarize_batch(self, events: List[Dict[str, Any]]) -> str:
        """Create batch-level summary."""
        
        # Group by pattern
        by_pattern = self._group_by_pattern(events)
        
        # Count files by type
        file_counts = self._count_by_type(events)
        
        # Calculate average score
        avg_score = sum(e.get('score', 0) for e in events) // len(events)
        
        # Generate summary
        parts = []
        for pattern, pattern_events in by_pattern.items():
            parts.append(f"{len(pattern_events)} {pattern.lower()} changes")
        
        summary = f"Batch: {', '.join(parts)}. "
        summary += f"Files: {file_counts}. "
        summary += f"Avg score: {avg_score}/100"
        
        return summary
    
    def summarize_session(self, start_time: datetime, end_time: datetime, 
                          all_events: List[Dict[str, Any]]) -> str:
        """Create session-level summary."""
        
        duration = (end_time - start_time).total_seconds() / 3600
        
        # Extract high-priority events (score > 70)
        high_priority = [e for e in all_events if e.get('score', 0) > 70]
        
        # Identify most changed files
        file_changes = self._count_changes_per_file(all_events)
        top_files = sorted(file_changes.items(), key=lambda x: x[1], reverse=True)[:3]
        
        # Generate session summary
        summary = f"Work session {start_time.strftime('%Y-%m-%d %H:%M')} - "
        summary += f"{end_time.strftime('%H:%M')} ({duration:.1f}h): "
        
        if high_priority:
            summary += f"{len(high_priority)} high-priority changes. "
        
        summary += f"Most active: {', '.join(f[0] for f in top_files)}. "
        
        return summary
```

### Implementation Plan

1. Create `AutoSummarizer` class
2. Implement event/batch/session summarization
3. Add natural language templates
4. Store summaries in Tier 1 metadata
5. Add CLI command to view summaries

### Testing

- Test summary generation quality (human review)
- Verify summary conciseness (<200 chars)
- Test with various event combinations

---

## 🔄 Integration with Existing System

### Changes to `auto_capture_daemon.py`

```python
class AmbientCaptureDaemon:
    """Enhanced ambient capture daemon with intelligence."""
    
    def __init__(self, workspace_path: str):
        # ... existing code ...
        
        # NEW: Add intelligent components
        self.file_filter = SmartFileFilter()
        self.pattern_detector = ChangePatternDetector(workspace_path)
        self.activity_scorer = ActivityScorer()
        self.auto_summarizer = AutoSummarizer()
```

### Updated Event Flow

```python
def _on_file_changed(self, event):
    """Enhanced file change handler."""
    
    # 1. Smart filtering
    if self.file_filter.is_noise_file(event.src_path):
        return  # Skip noise
    
    # 2. Pattern detection
    pattern = self.pattern_detector.detect_pattern(event)
    
    # 3. Activity scoring
    score = self.activity_scorer.score_activity(event, pattern)
    
    # 4. Create enriched context
    context = {
        "type": "file_change",
        "file": str(relative_path),
        "event": event.event_type,
        "pattern": pattern,
        "score": score,
        "timestamp": datetime.now().isoformat()
    }
    
    # 5. Generate summary
    context["summary"] = self.auto_summarizer.summarize_event(
        context, pattern, score
    )
    
    # 6. Send to debouncer
    self.debouncer.add_event(context)
```

### Debouncer Enhancements

```python
def _flush(self):
    """Enhanced flush with batch summarization."""
    
    # Merge events
    merged = self._merge_events(self.buffer)
    
    # Generate batch summary
    batch_summary = self.auto_summarizer.summarize_batch(merged)
    
    # Write to Tier 1 with summary
    self._write_to_tier1(merged, batch_summary)
```

---

## 📊 Performance Considerations

| Operation | Target Time | Strategy |
|-----------|-------------|----------|
| **Smart Filtering** | < 5ms | Regex patterns, file stat caching |
| **Pattern Detection** | < 20ms | Git diff caching, lazy evaluation |
| **Activity Scoring** | < 2ms | Simple arithmetic, no I/O |
| **Summarization** | < 10ms | Template-based, no LLM |
| **Total per Event** | < 50ms | Pipeline optimization |
| **Batch Processing** | < 150ms | Parallel analysis where possible |

**Optimization Strategies:**
- Cache git diff results (5 min TTL)
- Use regex compilation for patterns
- Lazy load file content (only when needed)
- Batch git operations
- Thread pool for parallel analysis

---

## 🧪 Testing Strategy

### Unit Tests

```python
# tests/tier2/test_smart_filter.py
def test_noise_file_detection():
    filter = SmartFileFilter()
    
    # Build artifacts
    assert filter.is_noise_file(Path("__pycache__/module.pyc"))
    assert filter.is_noise_file(Path("dist/bundle.js"))
    
    # Valid files
    assert not filter.is_noise_file(Path("src/main.py"))

# tests/tier2/test_pattern_detector.py
def test_pattern_detection():
    detector = ChangePatternDetector(workspace)
    
    # Feature detection
    event = {"file": "src/new_module.py", "event": "created"}
    assert detector.detect_pattern(event) == "FEATURE"
    
    # Refactor detection
    event = {"file": "src/renamed.py", "event": "deleted"}
    assert detector.detect_pattern(event) == "REFACTOR"

# tests/tier2/test_activity_scorer.py
def test_activity_scoring():
    scorer = ActivityScorer()
    
    event = {"file": "src/core.py", "event": "modified"}
    score = scorer.score_activity(event, "FEATURE")
    
    assert 70 <= score <= 100  # High priority

# tests/tier2/test_auto_summarizer.py
def test_event_summarization():
    summarizer = AutoSummarizer()
    
    event = {"file": "src/main.py", "event": "modified", "score": 85}
    summary = summarizer.summarize_event(event, "BUGFIX", 85)
    
    assert len(summary) < 200
    assert "main.py" in summary
```

### Integration Tests

```python
# tests/tier2/test_ambient_capture_integration.py
def test_end_to_end_capture():
    """Test full capture pipeline with enhancements."""
    
    # Create test file
    test_file = workspace / "src" / "test.py"
    test_file.write_text("def hello(): pass")
    
    # Wait for capture
    time.sleep(6)  # Debouncer delay
    
    # Verify in Tier 1
    wm = WorkingMemory(db_path)
    messages = wm.query_memory("test.py", limit=1)
    
    assert len(messages) > 0
    assert "pattern" in messages[0]
    assert "score" in messages[0]
    assert "summary" in messages[0]
```

### Performance Tests

```python
def test_filtering_performance():
    """Ensure filtering is fast."""
    filter = SmartFileFilter()
    
    start = time.time()
    for _ in range(1000):
        filter.is_noise_file(Path("src/test.py"))
    duration = time.time() - start
    
    assert duration < 5.0  # < 5ms per call
```

---

## 📈 Success Metrics

### Quantitative

- ✅ 70%+ noise reduction (measured by filtered events)
- ✅ 85%+ pattern detection accuracy
- ✅ 80%+ scoring precision
- ✅ <150ms batch processing time
- ✅ 80%+ test coverage

### Qualitative

- ✅ Summaries are human-readable (manual review)
- ✅ "Continue" command feels more intelligent
- ✅ No performance degradation in daemon
- ✅ Easy to configure and extend

### User Impact

- ✅ 90%+ "continue" command success rate (up from 85%)
- ✅ More relevant context in conversations
- ✅ Better understanding of recent work
- ✅ Reduced frustration with AI memory

---

## 🚀 Implementation Checklist

### Phase 1: Smart Filtering (2-3 hours)
- [ ] Create `SmartFileFilter` class
- [ ] Implement filter categories
- [ ] Add smart heuristics
- [ ] Write 10+ unit tests
- [ ] Integrate with FileSystemWatcher
- [ ] Measure noise reduction

### Phase 2: Pattern Detection (3-4 hours)
- [ ] Create `ChangePatternDetector` class
- [ ] Implement pattern classification
- [ ] Add git diff analysis
- [ ] Write 15+ unit tests
- [ ] Test accuracy on real examples
- [ ] Document patterns

### Phase 3: Activity Scoring (2 hours)
- [ ] Create `ActivityScorer` class
- [ ] Implement scoring algorithm
- [ ] Add configuration for weights
- [ ] Write 10+ unit tests
- [ ] Validate score distribution
- [ ] Benchmark performance

### Phase 4: Auto-Summarization (2-3 hours)
- [ ] Create `AutoSummarizer` class
- [ ] Implement event/batch/session summaries
- [ ] Add natural language templates
- [ ] Write 10+ unit tests
- [ ] Review summary quality
- [ ] Add CLI commands

### Phase 5: Integration & Testing (2 hours)
- [ ] Update `auto_capture_daemon.py`
- [ ] Integrate all components
- [ ] Write integration tests
- [ ] Run full test suite
- [ ] Performance benchmarks
- [ ] Documentation updates

### Phase 6: Documentation (1 hour)
- [ ] Create completion document
- [ ] Update STATUS.md
- [ ] Document configuration options
- [ ] Add usage examples
- [ ] Update user guides

---

## 📝 Configuration

**New config section in `cortex.config.json`:**

```json
{
  "ambient_capture": {
    "smart_filtering": {
      "enabled": true,
      "custom_ignore_patterns": [],
      "max_file_size_kb": 1024
    },
    "pattern_detection": {
      "enabled": true,
      "use_git_diff": true,
      "refactor_threshold_lines": 5
    },
    "activity_scoring": {
      "enabled": true,
      "file_type_weights": {
        ".py": 40,
        ".ts": 40,
        ".json": 30
      }
    },
    "auto_summarization": {
      "enabled": true,
      "max_summary_length": 200,
      "session_rollup_interval_hours": 2
    }
  }
}
```

---

## 🎯 Expected Outcomes

### Immediate Benefits
- ✅ 70% reduction in noise events
- ✅ Better context quality for "continue"
- ✅ Faster daemon processing (less noise)
- ✅ More intelligent event classification

### Long-term Benefits
- ✅ 90%+ "continue" success rate
- ✅ Foundation for ML-based improvements
- ✅ Better analytics on developer activity
- ✅ Enhanced context for all CORTEX operations

### Technical Debt Reduction
- ✅ Cleaner event logs
- ✅ More structured context data
- ✅ Better separation of concerns
- ✅ Easier to extend and maintain

---

## 🔗 Related Documents

- **Phase 4.1:** Quick Capture Workflows (COMPLETE)
- **Phase 4.2:** Shell Integration (COMPLETE)
- **Phase 4.3:** Context Optimization (COMPLETE)
- **Phase 2.1:** Ambient Capture (Foundation)
- **Phase 5.5:** YAML Conversion (Upcoming)

---

**Next Steps:** Begin implementation with Smart Filtering (Phase 1)

**Status:** Ready to implement 🚀
