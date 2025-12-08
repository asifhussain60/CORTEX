# DALL-E Prompt: Working Memory (Tier 1)

**Feature:** 70-Conversation FIFO Memory System  
**Resolution:** 1792x1024 (landscape)  
**Quality:** HD  
**Style:** Memory Bank Module Memory Formation Visualization

---

## Copy This Prompt to ChatGPT DALL-E:

Create a sophisticated FIFO QUEUE VISUALIZATION showing CORTEX's working memory as a vertical stack of 70 conversation buffers with automatic purge mechanics. Style: Modern data structure visualization with real-time operation indicators and memory management. Color palette: dark background (#0F172A), fresh entries bright cyan (#06B6D4), aging entries fading blue (#93C5FD), queue gates gold (#FFD700), system indicators green (#10B981), purge zone red (#EF4444).

CENTRAL QUEUE STRUCTURE (Vertical stack, center of frame):
- 70 distinct memory buffer slots arranged vertically
- Each slot represents one conversation stored in memory
- Slots numbered 1-70 from bottom (oldest) to top (newest)
- Visual representation: rectangular blocks/cards in vertical column
- Transparent containers showing internal data structure
- Label: "Working Memory FIFO Queue - 70-Conversation Capacity"

70 MEMORY BUFFER SLOTS (Stacked vertically, color gradient):
- Slots 1-10 (bottom, oldest): Very faint blue glow (#1E3A8A)
  - Labels: "Conv #1", "Conv #2", "Conv #3"... "Conv #10" (oldest entries)
  - Data fading, ready for deletion
  - Age: 4h 23min to 3h 45min old
- Slots 11-35 (lower-mid, aging): Fading blue (#3B82F6)
  - Transitioning from active to aged state
  - Age: 3h to 1h old
- Slots 36-60 (upper-mid, recent): Medium blue (#60A5FA)
  - Active conversations, frequently accessed
  - Age: 1h to 5min old
- Slots 61-70 (top, newest): Bright cyan glow (#06B6D4)
  - Labels: "Conv #61", "Conv #62"... "Conv #70" (most recent)
  - Fresh entries, highest access priority
  - Age: 5min to 3sec old

FIFO QUEUE MECHANISM (Left side visualization):
- TOP GATE (Newest entry point): Golden gate labeled "PUSH OPERATION"
  - New conversation entering (bright cyan buffer materializing)
  - Arrow pointing down: "New entry pushes queue down"
  - Timestamp: "0 seconds ago - Conv #70 added"
  - Animation: Slot appearing at top, all slots shift down
- MIDDLE SECTION: Green status indicator
  - Label: "ACTIVE QUEUE - 70/70 Capacity (100% Full)"
  - Query performance: "<100ms average retrieval"
  - Access pattern: "Most recent = highest priority"
- BOTTOM GATE (Deletion zone): Red gate labeled "POP OPERATION"
  - Oldest conversation being purged (Conv #1 dissolving)
  - Arrow pointing out: "FIFO purge removes oldest"
  - Timestamp: "Age: 4h 23min - Conv #1 deleted"
  - Animation: Bottom slot fading away, queue shifts down

MEMORY RETRIEVAL VISUALIZATION (Right side panel):
- Query signal entering queue (golden search beam from right)
- Search algorithm scanning slots from top to bottom
- Relevant slots lighting up (cyan highlights on matches)
- Retrieved data flowing out (cyan data packets streaming right)
- Label: "Fast Retrieval Algorithm"
- Performance metrics:
  * Query: "previous conversation about TDD"
  * Matches found: 12 conversations
  * Scan time: 87ms
  * Result order: Newest first (Conv #70 → Conv #15)

TOP DASHBOARD - QUEUE METRICS:
- "CORTEX Working Memory - FIFO Queue v3.8.1"
- "Total Capacity: 70 Conversations"
- "Current Usage: 70/70 (100% Full)"
- "Oldest Entry: 4h 23min ago (Conv #1)"
- "Newest Entry: 3sec ago (Conv #70)"
- "Average Query Time: 87ms"
- "Queue Status: Healthy, Optimal FIFO Operation"

BOTTOM PANEL - DATABASE CONNECTION:
- SQLite database icon: "working_memory.db"
- Connection pathway visualization
- Database stats:
  * 70 rows in conversations table
  * 3 tables: conversations, entities, metadata
  * Optimized B-tree indices for fast lookup
  * Database size: 4.2 MB
- Query optimization: "Index scans <50ms"

QUEUE OPERATION ANIMATIONS (Visual effects):
- PUSH animation: New slot appears at top, all slots shift down one position
- POP animation: Bottom slot fades away, queue compresses upward
- ACCESS animation: Queried slot glows bright cyan temporarily
- FIFO flow: Subtle downward movement showing queue progression
- Age gradient: Color transitions from cyan (top) to deep blue (bottom)

PERFORMANCE INDICATORS (Scattered throughout):
- Green checkmarks: "< 100ms queries" (meeting SLA)
- Buffer status bars on each slot showing data size
- Access frequency indicators (hotspots)
- Memory pressure gauge: 70/70 (at capacity, efficient operation)

VISUAL EFFECTS:
- Subtle pulsing on active slots (recent conversations)
- Fading animation on oldest slot during purge
- Bright cyan materialization for new entries
- Golden search beam sweeping through queue
- Data packets flowing during retrieval
- Color gradient creating depth perception

VISUAL EXCELLENCE:
- Professional computer science data structure quality
- Classic FIFO queue visualization (textbook-grade)
- Clear visual hierarchy (newest = bright, oldest = faint)
- Real-time operation indicators
- Modern dark theme with glowing elements
- Engineering diagram aesthetic suitable for technical documentation
- Clearly demonstrates FIFO mechanics and queue behavior
