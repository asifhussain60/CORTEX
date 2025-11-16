# ChatGPT Image Prompt: CORTEX Memory Integration Flow

**Diagram Type:** Data Flow & Integration Diagram  
**Print Specifications:** 17" x 11" @ 300 DPI (5100 x 3300 pixels)  
**Output Format:** PNG with WHITE background (not transparent)  
**Orientation:** Landscape  
**Print Margins:** 0.5" (150px @ 300 DPI) on all sides  
**Color Scheme:** CORTEX Standard Palette (Red/Teal/Blue/Green/Gold)

---

## 📋 AI Prompt

```
⚠️ CRITICAL REQUIREMENTS:
- PRINT MARGINS: Add 0.5" (150px @ 300 DPI) margin on ALL sides to prevent content cutoff
- COLOR SCHEME: Use CORTEX tier colors (Teal/Blue/Green) to show memory integration
- Show data flowing between tiers, not isolated boxes

Create a professional data flow diagram showing "CORTEX Memory Integration Flow" - how the 4-tier brain works together:

**Print Specifications:**
- Size: 17" x 11" landscape (tabloid size)
- Resolution: 300 DPI (5100 x 3300 pixels)
- **MARGINS: 0.5" (150px @ 300 DPI) on all sides - CRITICAL for print**
- Format: Data flow diagram with integration points
- Style: Technical architecture showing memory synchronization
- **WHITE background (solid white #ffffff, NOT transparent)**

**Title Section:**
- Title: "CORTEX Memory Integration Flow"
- Subtitle: "How the 4-Tier Brain Works Together"
- Copyright: "© 2024-2025 Asif Hussain"

**Main Layout: Memory Tiers + Integration (Top to Bottom)**

**TIER 1: WORKING MEMORY (Top - Teal #4ecdc4)**

**Storage:**
- SQLite Database: `conversations.db`
- JSONL Export: `conversation-history.jsonl`
- Capacity: Last 20 conversations

**Data Schema:**
```
{
  conversation_id: UUID,
  timestamp: ISO-8601,
  role: user/assistant/system,
  content: message text,
  metadata: {
    session_id, intent, agent, duration
  }
}
```

**Operations:**
- WRITE: After each conversation turn
- READ: On session start, context queries
- EXPORT: Every 5 conversations (JSONL)
- CLEANUP: Remove conversations older than 20th

**TIER 2: KNOWLEDGE GRAPH (Middle - Blue #45b7d1)**

**Storage:**
- YAML File: `knowledge-graph.yaml`
- Growth: Accumulates continuously

**Knowledge Types:**
```yaml
patterns:
  - problem: "JWT authentication"
    solution: "Use httpOnly cookies"
    success_rate: 93%
    uses: 13

lessons_learned:
  - what_worked: "Test-first approach"
    when: "Feature implementation"
    confidence: 95%

architecture_patterns:
  - pattern: "Plugin system"
    benefits: ["extensibility", "modularity"]
    tradeoffs: ["complexity"]
```

**Operations:**
- WRITE: Learner agent updates after sessions
- READ: Pattern Matcher searches during requests
- MERGE: Consolidate similar patterns
- PRUNE: Remove low-confidence entries (<20%)

**TIER 3: CONTEXT INTELLIGENCE (Bottom - Green #96ceb4)**

**Real-time Sources:**
- Git Metrics: Commits, branches, hotspots
- Test Coverage: pytest results, coverage %
- File Analysis: Dependencies, complexity
- Environment: Python version, packages

**Operations:**
- REFRESH: Every request (always current)
- ENRICH: Add context to Tier 1 conversations
- ANALYZE: Detect project health changes

**CENTER: INTEGRATION FLOWS (Show with arrows)**

**Flow 1: REQUEST PROCESSING**
```
User Request
    ↓
Load Tier 1: Recent conversations (context)
    ↓
Query Tier 2: Similar patterns (wisdom)
    ↓
Enrich with Tier 3: Current state (reality)
    ↓
Execute with full context
```

**Flow 2: LEARNING CYCLE**
```
Conversation Completed
    ↓
Store in Tier 1: Conversation record
    ↓
Extract patterns → Tier 2: Update knowledge
    ↓
Update Tier 3: Git/test state changed
```

**Flow 3: MEMORY CONSOLIDATION**
```
Tier 1 (20 conversations)
    ↓
    [When conversation #21 arrives]
    ↓
Export oldest to JSONL (archive)
    ↓
Extract patterns → Tier 2
    ↓
Remove from active memory (SQLite)
```

**RIGHT PANEL: INTEGRATION BENEFITS**

**Context Enrichment:**
- Tier 1 → Tier 2: "Have we solved this before?"
- Tier 2 → Tier 1: "Yes, use this pattern (93% success)"
- Tier 3 → All: "But tests are failing now"

**Memory Efficiency:**
- Working Memory: <20 conversations (fast)
- Knowledge Graph: Compressed patterns (compact)
- Context: Real-time only (no storage)

**Performance Metrics:**
- Tier 1 Query: <20ms
- Tier 2 Search: <100ms
- Tier 3 Refresh: <120ms
- Total Context Load: <240ms

**BOTTOM: DATA FLOW DIAGRAM**

Show circular flow:
```
    ┌─────────────────────────────────────┐
    │                                     │
    ↓                                     │
REQUEST → T1 Load → T2 Search → T3 Enrich → EXECUTE
    │                                     ↑
    └─────→ LEARN → T2 Update ───────────┘
```

**Visual Style:**
- **CORTEX color scheme:** Teal (#4ecdc4) for Tier 1, Blue (#45b7d1) for Tier 2, Green (#96ceb4) for Tier 3
- Tier boxes: Horizontal bands across the diagram
- Data flow arrows: Bold, directional, labeled
- Integration points: Clear connection indicators
- Code/data examples: Monospace font in light gray boxes
- **0.5" margins on all sides** (prevents content from being cut off when printed)
- Professional data architecture aesthetic
- Clear typography with tier labels
- **WHITE background (solid white #ffffff, NOT transparent)**

**Typography:**
- Tier names: Bold, 16-18pt
- Operation labels: Regular, 11-12pt
- Data examples: Monospace, 9-10pt
- Metrics: Regular, 10-11pt

**Visual Hierarchy:**
- Tiers: Large horizontal sections
- Integration flows: Bold arrows between tiers
- Code samples: Boxed and indented
- Metrics: Small table format

Make this diagram show how the "brain" isn't just storage - it's an active, integrated memory system where all tiers work together. Professional quality for technical architecture documentation.
```

---

## 🎨 Color Palette

| Element | Color | Hex | Usage |
|---------|-------|-----|-------|
| Tier 1 (Memory) | Teal | #4ecdc4 | Working memory |
| Tier 2 (Knowledge) | Blue | #45b7d1 | Pattern storage |
| Tier 3 (Context) | Green | #96ceb4 | Real-time data |
| Arrows | Gold | #ffd93d | Data flow |
| Code Boxes | Light Gray | #f8f9fa | Examples |
| Text Primary | Dark | #2d3436 | Main text |

---

## 📐 Layout

**Landscape (5100 x 3300 pixels):**
```
┌──────────────────────────────────────────────┐
│  TITLE & SUBTITLE                     (400px)│
├──────────────────────────────────────────────┤
│  TIER 1: Working Memory (Teal)        (600px)│
├──────────────────────────────────────────────┤
│  TIER 2: Knowledge Graph (Blue)       (600px)│
├──────────────────────────────────────────────┤
│  TIER 3: Context Intelligence (Green) (600px)│
├──────────────────────────────────────────────┤
│  INTEGRATION FLOWS & BENEFITS         (800px)│
├──────────────────────────────────────────────┤
│  DATA FLOW DIAGRAM                    (300px)│
└──────────────────────────────────────────────┘
```

---

## 📝 Usage Instructions

1. Copy AI prompt
2. Use any AI platform with image generation (ChatGPT-4 with DALL-E, Claude, Gemini, etc.)
3. Generate image
4. Download PNG
5. Save to: `docs/images/print-ready/08-memory-integration-flow.png`

---

## 💡 Key Messages

- **Integrated memory system** - tiers work together, not isolated
- **Data flows bidirectionally** - read and write across tiers
- **Context enrichment** - each tier adds value
- **Performance optimized** - <240ms total context load
- **Learning cycle** - continuous knowledge accumulation

---

*Created: 2025-11-13 | Memory integration and data flow visualization*
