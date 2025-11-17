# Diagram 04: CORTEX Memory Flow (Conversation → Knowledge)

**AI Generation Instructions for ChatGPT DALL-E:**

Create a professional left-to-right flow diagram showing CORTEX's 5-stage memory transformation pipeline. Use modern infographic style with clear progression and data flow visualization suitable for technical presentations.

## Design Requirements

**Style:** Professional process flow infographic, modern flat design, horizontal progression, clean arrows, corporate presentation quality

**Canvas:** 16:9 landscape aspect ratio (3840×2160 pixels equivalent)

## Flow Pipeline (5 Stages, Left to Right)

### Stage 1: User Conversation (Input)
**Position:** Far left (x: 300px from left edge)
**Visual:**
- Icon: 💬 Chat bubble (80×80px, outlined, #3B82F6)
- Box: 500×300px rounded rectangle (16px radius)
- Background: Light blue gradient (#E0F2FE to #BFDBFE)
- Border: 3px solid #3B82F6
- Shadow: 3px offset, 6px blur, 15% opacity

**Content:**
- Title: "User Conversation" (Bold, 20pt, dark gray)
- Sample text (Speech bubble style):
  * "Add authentication to dashboard"
  * "Make the button purple"
  * "Fix null reference error"
- Timestamp: "Real-time" (Regular, 12pt, gray)

**Arrow to Stage 2:**
- 4px solid line, #3B82F6 color
- Length: 200px horizontal
- Label: "Capture" (14pt, gray, above arrow)
- Arrowhead: 20px triangle

### Stage 2: Tier 1 Capture (Working Memory)
**Position:** x: 1100px from left
**Visual:**
- Icon: 🗃️ Database cylinder (80×80px, #3B82F6)
- Box: 500×300px rounded rectangle (16px radius)
- Background: White with #3B82F6 10% tint
- Border: 3px solid #3B82F6
- Shadow: 3px offset, 6px blur, 15% opacity

**Content:**
- Title: "Tier 1 Storage" (Bold, 20pt)
- Description: "Last 20 conversations" (Regular, 14pt)
- Example data (Monospace, 11pt, light gray box):
  ```
  conversation_id: conv_20251116_143000
  user: "Add authentication..."
  entities: [dashboard, authentication]
  timestamp: 2025-11-16 14:30:00
  ```
- Capacity: "18/20 slots used" (12pt, gray)

**Arrow to Stage 3:**
- 4px solid line, gray color
- Length: 200px horizontal
- Label: "Extract" (14pt, gray, above arrow)
- Arrowhead: 20px triangle

### Stage 3: Pattern Extraction (Processing)
**Position:** x: 1900px from left
**Visual:**
- Icon: 🔄 Network graph (80×80px, outlined, gray)
- Box: 500×300px rounded rectangle (16px radius)
- Background: Light gray gradient (#F3F4F6 to #E5E7EB)
- Border: 3px dashed #6B7280
- Shadow: 3px offset, 6px blur, 15% opacity

**Content:**
- Title: "Pattern Extraction" (Bold, 20pt)
- Processing indicators:
  * Intent detection → "EXECUTE"
  * Entity parsing → ["dashboard", "authentication"]
  * File identification → ["Dashboard.tsx"]
  * Relationship mapping → "UI + Auth"
- Processing time: "<50ms" (12pt, green checkmark)

**Arrow to Stage 4:**
- 4px solid line, #10B981 color
- Length: 200px horizontal
- Label: "Store" (14pt, gray, above arrow)
- Arrowhead: 20px triangle

### Stage 4: Tier 2 Storage (Knowledge Graph)
**Position:** x: 2700px from left
**Visual:**
- Icon: 🧩 Connected nodes (80×80px, #10B981)
- Box: 500×300px rounded rectangle (16px radius)
- Background: White with #10B981 10% tint
- Border: 3px solid #10B981
- Shadow: 3px offset, 6px blur, 15% opacity

**Content:**
- Title: "Tier 2 Knowledge" (Bold, 20pt)
- Description: "Patterns + Relationships" (Regular, 14pt)
- Learned patterns (Monospace, 11pt, light gray box):
  ```
  pattern: "feature_implementation"
  confidence: 0.88
  files: [Dashboard.tsx, AuthService.cs]
  success_rate: 0.94
  ```
- Pattern count: "34 patterns learned" (12pt, gray)

**Arrow to Stage 5:**
- 4px solid line, #F59E0B color
- Length: 200px horizontal
- Label: "Analyze" (14pt, gray, above arrow)
- Arrowhead: 20px triangle

### Stage 5: Tier 3 Analytics (Intelligence)
**Position:** x: 3500px from left (far right)
**Visual:**
- Icon: 📊 Bar chart (80×80px, #F59E0B)
- Box: 500×300px rounded rectangle (16px radius)
- Background: White with #F59E0B 10% tint
- Border: 3px solid #F59E0B
- Shadow: 3px offset, 6px blur, 15% opacity

**Content:**
- Title: "Tier 3 Context" (Bold, 20pt)
- Description: "Project Health + Productivity" (Regular, 14pt)
- Analytics (Monospace, 11pt, light gray box):
  ```
  Dashboard.tsx:
    churn_rate: 0.28 (⚠️ unstable)
    changes: 67 (last 30 days)
    recommendation: "Add extra tests"
  ```
- Health score: "87% project health" (12pt, green)

## Visual Flow Indicators

**Overhead Title:**
- Text: "CORTEX Memory Flow Pipeline"
- Position: Top center (y: 100px from top)
- Font: Bold, 42pt, dark gray (#374151)

**Subtitle:**
- Text: "From Conversation to Intelligence in 5 Stages"
- Position: Below title (y: 160px from top)
- Font: Regular, 22pt, medium gray (#6B7280)

**Timeline Bar (Bottom):**
- Position: Bottom of canvas (y: 1950px from top)
- Width: Full width minus 200px margins
- Visual: Horizontal progress bar (10px height)
- Gradient: #3B82F6 → #10B981 → #F59E0B
- Labels: "Input" (left) → "Processing" (center) → "Intelligence" (right)

## Typography

**Stage Titles:** Bold, 20pt, dark gray (#374151)
**Descriptions:** Regular, 14pt, medium gray (#6B7280)
**Example Code:** Monospace (Consolas), 11pt, dark gray
**Arrow Labels:** Regular, 14pt, medium gray
**Timestamps:** Regular, 12pt, light gray (#9CA3AF)

## Visual Polish

**Background:** Clean white or very light gray (#FAFAFA)
**Spacing:** 
- 200px horizontal between stages
- 60px vertical padding inside boxes
- 100px margins from canvas edges

**Shadows:** Subtle, consistent (3px offset, 6px blur, 15% opacity)
**Contrast:** High readability for all text
**Alignment:** Perfect horizontal alignment of stage boxes
**Balance:** Equal visual weight across all 5 stages

**Overall Quality:**
- Professional process flow layout
- Clear left-to-right progression
- Data transformation clearly visualized
- Conference presentation ready
- Print quality (300 DPI equivalent)

## Technical Accuracy

**Data Flow:**
1. User conversation → Tier 1 (captured in real-time)
2. Tier 1 → Pattern extraction (intent, entities, files)
3. Extraction → Tier 2 (stored as learned patterns)
4. Tier 2 → Tier 3 (enriched with git analysis)
5. Tier 3 → Proactive insights (warnings, recommendations)

**Performance:**
- Tier 1 query: <50ms (actual: 18ms avg)
- Pattern search: <150ms (actual: 92ms avg)
- Context analysis: <200ms (actual: 156ms avg)

*Generated: November 17, 2025*
