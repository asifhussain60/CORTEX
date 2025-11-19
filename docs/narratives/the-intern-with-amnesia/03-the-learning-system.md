# Chapter 03: The Learning System

*Part of The Intern with Amnesia - The CORTEX Story*  
*Author: Asif Hussain | © 2024-2025*  
*Generated: November 19, 2025*

---

## Overview

**Concept:** Extracting patterns from experiences  
**Technical Mapping:** Tier 2 Knowledge Graph (entity tracking, relationship mapping)

---

## The Story

Like your brain's long-term memory that accumulates wisdom over time, Tier 2 is **CORTEX's learning system**. It gets smarter with every project you work on together.

**What Gets Learned:**
- **Intent Patterns** - "add a button" → PLAN intent, "continue" → EXECUTE intent, "test this" → TEST intent
- **File Relationships** - `HostControlPanel.razor` often modified together with `noor-canvas.css` (75% co-modification rate observed)
- **Workflow Templates** - Proven patterns: export_feature_workflow, ui_component_creation, service_api_coordination
- **Validation Insights** - Common mistakes developers make, files that often get confused, architectural guidance
- **Correction History** - Tracks when Copilot worked on wrong files, learns to prevent similar errors

**How It Learns:**
```
Day 1: You ask to "add invoice export feature"
→ Right brain creates strategic plan
→ Left brain executes with TDD
→ Pattern saved: invoice_export_workflow
   - Files: InvoiceService.cs, ExportController.cs, InvoiceExportTests.cs
   - Steps: validate → format → download
   - Success rate: 100%
   - Confidence: 0.85

Day 30: You ask to "add receipt export feature"
→ Right brain queries Tier 2
→ Finds invoice_export_workflow pattern
→ Suggests: "This is similar to invoice export. Reuse same workflow?"
→ You approve
→ 60% faster delivery by reusing proven pattern ⚡
→ Pattern confidence increases to 0.92
```

**Pattern Decay:**
- Unused patterns decay over time (5% confidence drop per 30 days)
- Patterns below 30% confidence are pruned
- Keeps knowledge graph fresh and relevant

**Storage:** `cortex-brain/tier2/knowledge-graph.db` (SQLite), `cortex-brain/tier2/knowledge-graph.yaml`  
**Performance:** <150ms pattern search (target), 92ms actual ⚡

---

---

## Technical Deep Dive

### Tier 2 Knowledge Graph (entity tracking, relationship mapping)


**Tier 2 Architecture:**
- Knowledge graph database: `cortex-brain/tier2/knowledge-graph.db`
- Pattern storage: `cortex-brain/tier2/knowledge-graph.yaml`
- Intent patterns, file relationships, workflow templates
- Performance: <150ms pattern search target, 92ms actual

**Learning Process:**
1. Extract patterns from Tier 1 conversations
2. Store validated patterns in knowledge graph
3. Track confidence scores (0.0-1.0)
4. Decay unused patterns (5% per 30 days)
5. Prune low-confidence patterns (<30%)


---

## Key Takeaways

- Tier 2 learns patterns from accumulated experience
- Knowledge graph stores intent patterns and workflows
- Confidence scoring enables intelligent pattern selection
- Pattern decay keeps knowledge relevant


---

## Next Chapter

**[Chapter 04: Context Intelligence](./04-context-intelligence.md)**

*Understanding project structure and development patterns*
