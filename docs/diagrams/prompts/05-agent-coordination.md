# Diagram 05: CORTEX Agent Coordination (Multi-Agent Workflow)

**AI Generation Instructions for ChatGPT DALL-E:**

Create a professional vertical sequence diagram showing CORTEX's multi-agent collaboration workflow. Use modern UML-style swimlane format with clear temporal progression suitable for technical documentation.

## Design Requirements

**Style:** Professional sequence diagram with swimlanes, UML-inspired, modern flat design, clear temporal flow, corporate presentation quality

**Canvas:** 9:16 portrait aspect ratio (2160×3840 pixels equivalent)

## Swimlane Layout (4 Columns, Left to Right)

### Column 1: User (Width: 400px)
**Background:** Light gray (#F3F4F6)
**Header:** 
- Text: "USER" (Bold, 24pt, dark gray)
- Icon: 👤 User silhouette (40×40px)
- Height: 100px header bar

### Column 2: RIGHT Brain (Width: 600px)
**Background:** Light orange gradient (#FEF3C7 to #FDE68A)
**Header:**
- Text: "RIGHT BRAIN (Strategic)" (Bold, 24pt, white)
- Icon: 🧠 Brain icon (40×40px)
- Subtext: "Planning + Protection" (Regular, 14pt, white 80%)
- Height: 100px header bar
- Border: 3px solid #F59E0B

### Column 3: Corpus Callosum (Width: 300px)
**Background:** Vertical gradient (blue to orange)
**Header:**
- Text: "CORPUS CALLOSUM" (Bold, 20pt, white, rotated 90°)
- Icon: 🌉 Bridge (30×30px)
- Subtext: "Coordination" (Regular, 12pt, white)
- Height: 100px header bar

### Column 4: LEFT Brain (Width: 600px)
**Background:** Light blue gradient (#DBEAFE to #BFDBFE)
**Header:**
- Text: "LEFT BRAIN (Tactical)" (Bold, 24pt, white)
- Icon: ⚙️ Gear icon (40×40px)
- Subtext: "Execution + Testing" (Regular, 14pt, white 80%)
- Height: 100px header bar
- Border: 3px solid #3B82F6

## Workflow Sequence (Example: "Add Authentication")

**Vertical Timeline** (Top to Bottom, numbered steps)

### Step 1: User Request (y: 200px from top)
**User Column:**
- Speech bubble: 300×120px, white with shadow
- Text: "Add authentication to dashboard" (16pt)
- Icon: 💬 Chat bubble
- Timestamp: "14:30:00" (12pt, gray)

**Arrow:** Solid line (4px, blue) → RIGHT Brain (Intent Router)

### Step 2: Intent Detection (y: 400px)
**RIGHT Brain Column:**
- Box: "Intent Router" (500×100px, white, rounded)
- Icon: 🚦 (40×40px)
- Action: "Detects PLAN intent" (14pt)
- Details: "Confidence: 0.88" (12pt, monospace, gray box)

**Arrow:** Solid line (4px, orange) → RIGHT Brain (Work Planner)

### Step 3: Plan Creation (y: 600px)
**RIGHT Brain Column:**
- Box: "Work Planner" (500×100px, white, rounded)
- Icon: 📋 (40×40px)
- Action: "Creates 3-phase plan" (14pt)
- Details: "Phase 1: Tests | Phase 2: Impl | Phase 3: Validate" (11pt)

**Arrow:** Dashed line (4px, gray) → Corpus Callosum
**Label:** "Task Assignment" (12pt, above arrow)

### Step 4: Message Transfer (y: 800px)
**Corpus Callosum Column:**
- Box: "Message Queue" (250×100px, white, rounded)
- Icon: 📨 Envelope (40×40px)
- Text: "Queuing Phase 1 tasks..." (12pt)
- Status: "Ready" (12pt, green checkmark)

**Arrow:** Solid line (4px, blue) → LEFT Brain (Code Executor)

### Step 5: Test Creation (y: 1000px)
**LEFT Brain Column:**
- Box: "Test Generator" (500×100px, white, rounded)
- Icon: ✓ (40×40px)
- Action: "Create failing tests" (14pt)
- Details: "RED phase: 0/8 passing" (11pt, red text)

**Arrow:** Dashed line (4px, blue) → LEFT Brain (Code Executor)

### Step 6: Implementation (y: 1200px)
**LEFT Brain Column:**
- Box: "Code Executor" (500×100px, white, rounded)
- Icon: `</>` (40×40px)
- Action: "Implement AuthService" (14pt)
- Details: "TDD cycle enforced" (11pt)

**Arrow:** Solid line (4px, blue) → LEFT Brain (Code Executor - same agent)
**Label:** "Make tests pass" (12pt)

### Step 7: Tests Passing (y: 1400px)
**LEFT Brain Column:**
- Box: "Code Executor" (500×100px, white, rounded)
- Icon: `</>` (40×40px)
- Status: "GREEN phase: 8/8 passing ✅" (14pt, green)
- Details: "All tests pass" (11pt)

**Arrow:** Solid line (4px, blue) → LEFT Brain (Health Validator)

### Step 8: Validation (y: 1600px)
**LEFT Brain Column:**
- Box: "Health Validator" (500×100px, white, rounded)
- Icon: ❤️ (40×40px)
- Action: "Enforce Definition of Done" (14pt)
- Checks:
  * Tests: ✅ 8/8 passing
  * Errors: ✅ 0 found
  * Warnings: ✅ 0 found
  * Build: ✅ Success

**Arrow:** Dashed line (4px, gray) → Corpus Callosum
**Label:** "Completion Report" (12pt)

### Step 9: Knowledge Update (y: 1800px)
**Corpus Callosum:**
- Box: "Message Queue" (250×100px, white, rounded)
- Icon: 📨 (40×40px)
- Text: "Forwarding results..." (12pt)

**Arrow:** Solid line (4px, orange) → RIGHT Brain (Knowledge Graph)

### Step 10: Learning (y: 2000px)
**RIGHT Brain Column:**
- Box: "Knowledge Graph (Tier 2)" (500×120px, white, rounded)
- Icon: 🧩 (40×40px)
- Action: "Store workflow pattern" (14pt)
- Details:
  ```
  pattern: "authentication_workflow"
  confidence: 0.92
  success: true
  files: [AuthService.cs, AuthTests.cs]
  ```

**Arrow:** Dashed line (4px, orange) → User
**Label:** "Feature Complete" (12pt, green)

### Step 11: Confirmation (y: 2200px)
**User Column:**
- Notification: 300×100px, white with green border
- Icon: ✅ Checkmark (40×40px)
- Text: "Authentication feature ready!" (16pt)
- Subtext: "8 tests passing, 0 errors" (12pt, gray)

## Visual Elements

**Arrow Specifications:**
- Solid arrows: Requests/commands (4px thickness)
- Dashed arrows: Responses/results (4px thickness, 8px dash, 6px gap)
- Arrowheads: 15px triangles
- Colors: Blue (LEFT), Orange (RIGHT), Gray (Corpus)
- Labels: 12pt, centered above arrow

**Agent Boxes:**
- Size: 500×100px (brain agents), 300×100px (user/messages)
- Radius: 12px rounded corners
- Background: White with hemisphere-colored shadow
- Border: 2px solid (hemisphere color)
- Shadow: 2px offset, 4px blur, 15% opacity

**Timeline Indicator (Left Edge):**
- Vertical line: 2px solid gray, full height
- Time markers: Every 200px (T+0s, T+0.5s, T+1s, etc.)
- Labels: 10pt, gray

**Step Numbers (Left of Timeline):**
- Circles: 40×40px, #3B82F6 fill
- Numbers: Bold, 18pt, white
- Vertical spacing: Aligned with each workflow step

## Typography

**Swimlane Headers:** Bold, 24pt, white (or dark gray for User)
**Agent Names:** Bold, 16pt, dark gray (#374151)
**Actions:** Regular, 14pt, dark gray
**Details:** Monospace (Consolas), 11pt, medium gray (#6B7280)
**Timestamps:** Regular, 12pt, light gray (#9CA3AF)
**Arrow Labels:** Regular, 12pt, medium gray

## Visual Polish

**Background:** Clean white or very light gray (#FAFAFA)
**Spacing:**
- 200px vertical between workflow steps
- 40px padding inside agent boxes
- 100px margins from canvas edges

**Shadows:** Subtle, consistent (2px offset, 4px blur, 15% opacity)
**Contrast:** High readability for all text
**Alignment:** Perfect vertical alignment of sequence flow
**Balance:** Even distribution across swimlanes

**Overall Quality:**
- Professional UML sequence diagram style
- Clear temporal progression (top to bottom)
- Agent collaboration clearly visualized
- Conference presentation ready
- Print quality (300 DPI equivalent)

## Technical Accuracy

**Coordination Protocol:**
1. RIGHT Brain detects intent, creates strategy
2. Corpus Callosum delivers tasks via message queue
3. LEFT Brain executes with TDD enforcement
4. LEFT Brain validates quality (DoD)
5. Results flow back to RIGHT Brain for learning

**Performance:**
- Total workflow: <5 seconds (typical feature)
- Message passing: <10ms per transfer
- Validation: <150ms

**Multi-Agent Benefits:**
- Separation of concerns (strategy vs execution)
- Parallel processing where possible
- Quality gates at each stage
- Continuous learning loop

*Generated: November 16, 2025*
