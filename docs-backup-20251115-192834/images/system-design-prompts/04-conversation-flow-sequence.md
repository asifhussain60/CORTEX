# ChatGPT Image Prompt: CORTEX Conversation Flow

**Diagram Type:** Sequence Flow Diagram  
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
- COLOR SCHEME: Use CORTEX standard palette (Red/Teal/Blue/Green/Gold) consistently

Create a professional sequence diagram showing "CORTEX End-to-End Conversation Flow" with the following specifications:

**Print Specifications:**
- Size: 17" x 11" landscape (tabloid size)
- Resolution: 300 DPI (5100 x 3300 pixels)
- **MARGINS: 0.5" (150px @ 300 DPI) on all sides - CRITICAL for print**
- Format: Technical sequence diagram suitable for printing
- Style: Clean UML-style sequence diagram with swimlanes
- **WHITE background (solid white #ffffff, NOT transparent)**

**Title Section:**
- Title: "CORTEX Conversation Flow"
- Subtitle: "End-to-End Request Lifecycle"
- Copyright: "© 2024-2025 Asif Hussain"

**Participants (Show as swimlanes from top to bottom):**

1. **👤 User**
   - Icon: Person silhouette
   - Color: Light gray

2. **🚪 Entry Point**
   - Icon: Door/gateway
   - Color: Light teal (#a8e6cf)
   - Label: "CORTEX.prompt.md"

3. **🧭 Intent Router**
   - Icon: Compass
   - Color: Gold (#ffd93d)

4. **🧠 4-Tier Brain**
   - Split into 4 sub-lanes:
     * T0 (Red): Instinct
     * T1 (Teal): Memory
     * T2 (Blue): Knowledge
     * T3 (Green): Context

5. **🤖 Specialist Agents**
   - Icon: Robot/agent
   - Color: Mixed (teal/green)

6. **💾 Storage**
   - Icon: Database
   - Color: Dark gray

**Sequence Flow (Left to Right):**

**PHASE 1: REQUEST INTAKE** (Light background)
1. User → Entry Point: "Add authentication" (arrow with label)
2. Entry Point → Entry Point: Parse request (self-arrow)
3. Entry Point → Intent Router: Route to intent detection

**PHASE 2: VALIDATION & CONTEXT LOADING** (Slightly darker background)
4. Intent Router → T0 (Brain): Check protection rules
5. T0 → Intent Router: ✅ Allowed (SKULL validation passed)
6. Intent Router → T1 (Brain): Load recent conversations
7. T1 → Intent Router: Last 5 relevant conversations (data annotation)
8. Intent Router → T2 (Brain): Search for patterns
9. T2 → Intent Router: 3 similar patterns found (data annotation)
10. Intent Router → T3 (Brain): Get current context
11. T3 → Intent Router: Git status, test coverage, file state (data annotation)

**PHASE 3: EXECUTION** (Medium background)
12. Intent Router → Specialist Agents: Execute with full context
13. Specialist Agents → Specialist Agents: Multi-step loop:
    - Plan
    - Execute
    - Test
    - Validate
    (Show as a loop box within the agent swimlane)
14. Specialist Agents → Storage: Save code changes

**PHASE 4: LEARNING & RESPONSE** (Slightly lighter background)
15. Specialist Agents → T1 (Brain): Store conversation
16. Specialist Agents → T2 (Brain): Update patterns (if learned)
17. Specialist Agents → User: Response with results ✅

**Timing Annotations (on bottom):**
- Phase 1: <300ms
- Phase 2: <500ms
- Phase 3: 2-10s (variable)
- Phase 4: <200ms
- Total: 3-11s typical

**Visual Elements:**

**Arrows:**
- Solid arrows: Synchronous calls
- Dashed arrows: Return values/responses
- Thick arrows: Data transfer
- Color code arrows by phase

**Boxes:**
- Activation boxes: Show when participant is active
- Loop box: For multi-step execution
- Note boxes: For important annotations

**Annotations:**
- Add small note boxes for key data transfers
- Show example data in quotes
- Include performance metrics

**Background Phases:**
- Use subtle horizontal bands to show different phases
- Gradient from light to slightly darker as flow progresses

**Visual Style:**
- Clean UML sequence diagram aesthetic
- **CORTEX color scheme:** Use tier colors for brain lanes (Red/Teal/Blue/Green), Gold for coordination
- Professional technical documentation quality
- Clear, readable arrows with labels
- Proper swimlane separation
- **0.5" margins on all sides** (prevents content from being cut off when printed)
- Sufficient horizontal spacing between steps
- Sans-serif typography
- Print-ready clarity
- **WHITE background (solid white #ffffff, NOT transparent)**

**Legend Box (Bottom Right):**
→ Synchronous call
⇢ Asynchronous call
- - → Return value
⟲ Loop
✅ Success
❌ Failure

**Key Insights Box (Bottom Left):**
- Memory Integration: All 4 tiers consulted
- Pattern Matching: Reuses proven solutions
- Learning: Every session updates knowledge
- Speed: <1s for simple, ~5s for complex

Make this diagram clear enough that a developer could understand the complete request flow from a single glance. Professional quality suitable for technical architecture reviews or documentation.
```

---

## 🎨 Color Scheme

| Phase | Background | Accent |
|-------|-----------|--------|
| Phase 1: Intake | #f8f9fa | #a8e6cf |
| Phase 2: Validation | #f1f3f5 | #ffd93d |
| Phase 3: Execution | #e9ecef | #4ecdc4 |
| Phase 4: Learning | #f1f3f5 | #55efc4 |

---

## 📐 Layout Structure

**Landscape (5100 x 3300 pixels):**
```
┌─────────────────────────────────────────────────┐
│  TITLE & SUBTITLE                         (400px)│
├─────────────────────────────────────────────────┤
│  User │Entry│Intent│ Brain │Agents│Storage      │
│       │Point│Router│ (4T)  │      │             │
│  Participant Headers                      (300px)│
├─────────────────────────────────────────────────┤
│  ←────── Flow progresses left to right ────────→│
│  PHASE 1 → PHASE 2 → PHASE 3 → PHASE 4          │
│  (Request → Validation → Execute → Learn)        │
│                                           (2000px)│
├─────────────────────────────────────────────────┤
│  Legend (Bottom Left) │ Insights (Bottom Right)  │
│                                            (600px)│
└─────────────────────────────────────────────────┘
```

---

## 📝 Usage Instructions

1. Copy AI prompt
2. Use any AI platform with image generation (ChatGPT-4 with DALL-E, Claude, Gemini, etc.)
3. Generate image
4. Download high-resolution PNG
5. Save to: `docs/images/print-ready/04-conversation-flow.png`

---

*Created: 2025-11-13 | Complete request lifecycle visualization*
