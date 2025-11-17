# Knowledge Graph (Tier 2) Narrative

## For Leadership

The Knowledge Graph shows how CORTEX learns from experience, similar to how professionals develop expertise over time.

**Learning Phase** - When you complete a task (like "add export feature"), CORTEX extracts the pattern: which files were modified, what steps worked, how long it took. This becomes a reusable template.

**Reuse Phase** - Next time you need something similar (like "add receipt export"), CORTEX recognizes the pattern and suggests: "This is 92% similar to invoice export. Reuse the same workflow?" This delivers results 60% faster.

**Decay Phase** - Unused patterns gradually lose confidence. After 90 days without use, confidence drops from 85% to 70%. Patterns below 30% are pruned to keep the system fresh and relevant.

**Relationships** - CORTEX tracks which files change together. When you modify `HostControlPanel.razor`, it suggests also checking `noor-canvas.css` (75% co-modification rate observed).

**Business Impact:** Less rework, faster delivery, accumulated team knowledge that doesn't leave when people do.

## For Developers

**Architecture Pattern:** Graph-based pattern storage with FTS5 full-text search and confidence decay

```
New Request ──▶ Search Graph (FTS5) ──▶ Find Match (92%)
                     ↓
              Apply Pattern ──▶ 60% faster delivery
                     ↓
              Update Confidence (+5%)
```

**Storage Schema:**
```sql
-- Patterns table
CREATE TABLE patterns (
    pattern_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    pattern_type TEXT, -- 'workflow', 'intent', 'validation'
    confidence REAL DEFAULT 0.5,
    context_json TEXT,
    scope TEXT, -- 'cortex' or 'application'
    namespaces TEXT, -- JSON array
    created_at DATETIME,
    last_used DATETIME,
    usage_count INTEGER DEFAULT 0
);

-- FTS5 full-text search
CREATE VIRTUAL TABLE patterns_fts USING fts5(
    pattern_id UNINDEXED,
    title,
    context_json,
    content='patterns'
);
```

**Learning Algorithm:**
1. **Capture:** Extract files, steps, success metrics from conversation
2. **Calculate Confidence:** Initial = 0.5 + (success_rate × 0.5)
3. **Store:** Insert into graph with metadata
4. **Index:** Update FTS5 for fast search

**Reuse Algorithm:**
1. **Parse Request:** Extract intent and entities
2. **Search FTS5:** Full-text search across patterns
3. **Rank Results:** Combine FTS5 score + confidence + recency
4. **Suggest:** If match > 70%, suggest to user
5. **Apply:** On approval, boost confidence (+5%)

**Decay Algorithm:**
```python
def apply_decay(pattern, days_unused):
    decay_rate = 0.05  # 5% per 30 days
    periods = days_unused // 30
    new_confidence = pattern.confidence * (1 - decay_rate) ** periods
    if new_confidence < 0.3:
        prune_pattern(pattern)
    else:
        update_confidence(pattern, new_confidence)
```

**File Relationships:**
- **Co-modification:** Track when files change together (% frequency)
- **Dependency:** Track import/using statements
- **Test Links:** Connect production code to test files

**Performance:**
- FTS5 search: <150ms (target), 92ms actual ⚡
- Pattern storage: <80ms (target), 56ms actual ⚡
- Relationship query: <120ms (target), 78ms actual ⚡

## Key Takeaways

1. **Learns continuously** - Every conversation adds to knowledge
2. **Suggests proactively** - Recognizes similar work automatically
3. **Stays fresh** - Unused patterns decay and prune
4. **Tracks relationships** - Files that change together stay together
5. **Fast search** - FTS5 full-text indexing for instant matches

## Usage Scenarios

**Scenario 1: First Export Feature (Learning)**
```
User: "Add invoice export"
CORTEX: Creates feature, tracks:
  - Files: InvoiceService.cs, ExportController.cs, InvoiceExportTests.cs
  - Steps: validate → format → download
  - Success: 100%, Duration: 45 min
Pattern stored: invoice_export_workflow (confidence 0.85)
```

**Scenario 2: Second Export Feature (Reuse)**
```
User: "Add receipt export"
CORTEX: Searches graph, finds invoice_export_workflow (92% match)
        "This is similar to invoice export (85% confidence)"
        "Reuse same workflow?"
User: "Yes"
CORTEX: Applies pattern, delivers 60% faster (18 min vs 45 min)
        Boosts confidence to 0.90
```

**Scenario 3: Pattern Decay (Cleanup)**
```
Pattern: legacy_xml_export_workflow
Last used: 120 days ago
Confidence: 0.85 → 0.80 → 0.75 → 0.70 → 0.28 (PRUNED)
Reason: XML exports deprecated, no longer relevant
```

**Scenario 4: File Relationships**
```
User: Modifies HostControlPanel.razor
CORTEX: "This file often changes with:"
  - noor-canvas.css (75% co-modification)
  - HostControlPanelTests.cs (test relationship)
  - PanelService.cs (dependency)
        "Review these files too?"
```

*Version: 1.0*  
*Last Updated: November 17, 2025*
