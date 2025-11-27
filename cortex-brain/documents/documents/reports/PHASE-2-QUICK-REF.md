# Phase 2 Quick Reference

## 🎯 What Phase 2 Adds

**Intelligent activity-based prioritization** for multi-app workspaces without editor dependency.

---

## 🚀 Quick Start

```python
from src.crawlers.multi_app_orchestrator import MultiApplicationOrchestrator
from src.tier2.knowledge_graph import KnowledgeGraph

orchestrator = MultiApplicationOrchestrator(
    workspace_path='/path/to/workspace',
    knowledge_graph=KnowledgeGraph(),
    cortex_brain_path='/path/to/cortex-brain'
)

result = orchestrator.run_progressive()
orchestrator.cleanup()
```

That's it! Phase 2 auto-initializes and uses intelligent prioritization.

---

## 📊 Scoring Weights

| Signal | Weight | What It Tracks |
|--------|--------|----------------|
| **Filesystem Activity** | 40% | Recent file modifications, lock files |
| **Git History** | 30% | Commit frequency, file changes |
| **Access Patterns** | 20% | File access times, cross-app navigation |
| **Dependencies** | 10% | Shared database, imports |

---

## 🎚️ Priority Tiers

| Tier | Count | Action | When |
|------|-------|--------|------|
| **immediate** | 2-3 apps | Load full context NOW | Score > 0.7 |
| **queued** | 3-5 apps | Pre-warm metadata | Score 0.4-0.7 |
| **background** | Rest | Lazy load on demand | Score < 0.4 |

---

## 🔧 Optional: Install Watchdog

For real-time filesystem monitoring:

```bash
pip install watchdog
```

Without it: Falls back to periodic checks (still works fine).

---

## 📁 Components

1. **FileSystemActivityMonitor** - Tracks file modifications
2. **GitHistoryAnalyzer** - Parses git commit history
3. **AccessPatternTracker** - Monitors file access times
4. **ApplicationPrioritizationEngine** - Aggregates signals
5. **SmartCacheManager** - Real-time cache management

---

## ✅ Testing

```bash
# Run integration tests
python3 -m pytest tests/integration/test_phase_2_integration.py -v

# Expected: 5/5 PASSING ✅
```

---

## 🎯 Performance Targets

- **Initial analysis:** < 2s
- **Ongoing updates:** < 100ms
- **File change events:** < 10ms

---

## 🔄 Fallback Behavior

If Phase 2 fails → **Automatic fallback to legacy scoring**

No crashes, just reduced intelligence.

---

## 🛠️ Configuration

### Prioritization
```python
config = {
    'immediate_count': 3,   # Top 2-3 apps
    'queued_count': 5       # Next 3-5 apps
}
```

### Cache Manager
```python
config = {
    'check_interval': 60,      # Check every 60s
    'promotion_threshold': 5,  # Promote after 5 changes
    'demotion_threshold': 300  # Demote after 5 min idle
}
```

---

## 📚 Full Docs

See: `cortex-brain/documents/reports/PHASE-2-COMPLETE.md`

---

**Status:** ✅ PRODUCTION READY  
**Tests:** 5/5 passing  
**Dependencies:** None required (watchdog optional)
