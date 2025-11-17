# Image Prompt: CORTEX Conversation Memory (Tier 1)

**For:** ChatGPT Image Generator (DALL-E 3)

## Prompt

Create a professional flowchart diagram with generous margins (10% on all sides) showing how CORTEX's Tier 1 conversation memory works with FIFO queue management. The diagram should be centered with clear spacing.

**Visual Style:**
- Modern tech aesthetic with gradient background (dark blue to navy)
- Three sections: Capture, Storage, FIFO Management
- Use blue for primary operations, green for processing, orange for FIFO
- Professional typography with perfect spelling
- Database and queue icons

**Flow Layout (Top to Bottom, Three Columns):**

**Column 1: Capture (Blue #3B82F6):**
- Large heading: "CAPTURE" (bold, with microphone icon)
- Three methods vertically:
  1. "PowerShell Capture" | "capture-copilot-chat.ps1" (with script icon)
  2. "Python CLI" | "cortex remember" (with terminal icon)
  3. "Ambient Daemon" | "Auto-detect (30s idle)" (with robot icon)
- Arrow down: "Conversation Text"

**Column 2: Storage & Processing (Green #10B981):**
- Large heading: "STORAGE & PROCESSING" (bold, with database icon)
- Process flow:
  1. "Parse Conversation" | "Extract messages"
  2. "Entity Extraction" | "Files, Classes, Methods"
  3. "Intent Detection" | "PLAN, EXECUTE, TEST..."
  4. "Store in SQLite" | "conversations.db" (with cylinder icon)
- Arrow down: "Indexed & Searchable"

**Column 3: FIFO Queue Management (Orange #F59E0B):**
- Large heading: "FIFO QUEUE" (bold, with recycle icon)
- Queue visualization showing 20 boxes:
  - Top 19 boxes: Conversations 1-19 (blue)
  - Bottom box: Conversation 20 (green, highlighted "Active")
- Decision diamond: "Queue Full? (>20)"
  - YES → "Delete Oldest" | "Archive first"
  - NO → "Store New"
- Stats box: "Current: 18/20" | "Oldest: 15 days"

**Data Flow:**
- Capture → Storage: Large arrow "Raw Text"
- Storage → FIFO: Large arrow "Structured Data"
- FIFO → User: Arrow "Query Results"

**Example Query Box (Bottom Center):**
- User query: "What did we discuss about authentication?"
- Results: "Found 2 conversations (Nov 8, Nov 7)"
- Quick preview: "• Nov 8: Implemented login • Nov 7: Fixed null bug"

**Typography Requirements:**
- All text perfectly spelled
- Section headings: 24pt, bold
- Component names: 16pt, bold
- Descriptions: 14pt, regular
- Stats: 12pt, monospace

**Color Palette:**
- Capture: Blue (#3B82F6) with border (#1E3A8A)
- Storage: Green (#10B981) with border (#065F46)
- FIFO: Orange (#F59E0B) with border (#92400E)
- Active conversation: Bright green (#22C55E)
- Background: Gradient from #0F172A to #1E293B
- Text: White (#FFFFFF)

**Margin Requirements:**
- Top margin: 10% of canvas height
- Bottom margin: 10% of canvas height
- Left margin: 10% of canvas width
- Right margin: 10% of canvas width

**Additional Elements:**
- "CORTEX Tier 1: Conversation Memory" title at top
- "Last 20 Conversations • FIFO Queue • <50ms Query" subtitle
- "Performance: 18ms avg" badge (top right, green)
- "© 2024-2025" copyright bottom right

Make it look like a professional memory management system with perfect spelling and clear data flow.
