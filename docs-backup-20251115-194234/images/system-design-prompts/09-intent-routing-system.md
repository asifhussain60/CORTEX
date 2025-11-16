# ChatGPT Image Prompt: CORTEX Intent Routing System

**Diagram Type:** Decision Tree & Routing Logic  
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
- COLOR SCHEME: Use CORTEX standard palette with Gold (#ffd93d) for routing/coordination
- Show natural language input transforming into agent routing

Create a professional decision tree diagram showing "CORTEX Intent Routing System" - how natural language becomes agent actions:

**Print Specifications:**
- Size: 17" x 11" landscape (tabloid size)
- Resolution: 300 DPI (5100 x 3300 pixels)
- **MARGINS: 0.5" (150px @ 300 DPI) on all sides - CRITICAL for print**
- Format: Decision tree with routing logic
- Style: Technical flowchart with NLP transformation
- **WHITE background (solid white #ffffff, NOT transparent)**

**Title Section:**
- Title: "CORTEX Intent Routing System"
- Subtitle: "Natural Language → Agent Selection"
- Copyright: "© 2024-2025 Asif Hussain"

**LEFT SIDE: INPUT EXAMPLES (Show 8 natural language requests)**

**Implementation Requests:**
- "Add authentication to the dashboard"
- "Fix the bug in user service"
- "Refactor the payment module"

**Testing Requests:**
- "Test the login feature"
- "Generate tests for API endpoints"

**Planning Requests:**
- "Plan a feature for notifications"
- "Break down the search implementation"

**Analysis Requests:**
- "Check project health"
- "Have we solved authentication before?"

**Documentation Requests:**
- "Document the user service"
- "Update the README"

**Configuration Requests:**
- "Setup my environment"
- "Configure for Windows"

**CENTER: INTENT DETECTOR (Large component - Gold #ffd93d)**

Show as funnel/processor with stages:

**Stage 1: Keyword Analysis**
- Extract action verbs: add, fix, test, plan, check, etc.
- Extract targets: authentication, bug, feature, etc.
- Extract context: dashboard, user service, etc.

**Stage 2: Intent Classification**
Decision logic:
```
Keywords: [add, implement, create, build]
    → Intent: EXECUTE
    
Keywords: [fix, debug, solve, repair]
    → Intent: EXECUTE (bug focus)
    
Keywords: [test, validate, verify, check coverage]
    → Intent: TEST
    
Keywords: [plan, break down, design, architecture]
    → Intent: PLAN
    
Keywords: [health, analyze, review, assess]
    → Intent: VALIDATE
    
Keywords: [document, explain, readme, docs]
    → Intent: DOCUMENT
    
Keywords: [setup, configure, install, environment]
    → Intent: SETUP
    
Keywords: [have we, similar, before, pattern]
    → Intent: SEARCH_PATTERNS
```

**Stage 3: Command Registry Lookup**
- Check registered plugin commands
- Match natural language to command aliases
- Resolve to specific plugin

**Stage 4: Context Enrichment**
- Load Tier 1: Recent conversations
- Query Tier 2: Similar patterns
- Fetch Tier 3: Current project state

**RIGHT SIDE: AGENT ROUTING (Show 10 agents with routing paths)**

**LEFT BRAIN AGENTS (Teal #4ecdc4):**

1. **Executor** ⚙️
   - Routes: EXECUTE intents
   - Examples: "Add X", "Fix Y", "Refactor Z"

2. **Tester** 🧪
   - Routes: TEST intents
   - Examples: "Test X", "Generate tests"

3. **Validator** ✅
   - Routes: VALIDATE intents
   - Examples: "Check health", "Review code"

4. **Work Planner** 📋
   - Routes: PLAN intents
   - Examples: "Plan feature", "Break down task"

5. **Documenter** 📚
   - Routes: DOCUMENT intents
   - Examples: "Document X", "Update README"

**RIGHT BRAIN AGENTS (Green #96ceb4):**

6. **Intent Detector** 🎯
   - Routes: ALL (orchestrator)
   - Examples: Every request goes through here first

7. **Architect** 🏗️
   - Routes: DESIGN, ARCHITECTURE intents
   - Examples: "Design system", "Architecture for X"

8. **Health Validator** 💚
   - Routes: HEALTH, ANALYSIS intents
   - Examples: "Check health", "Analyze codebase"

9. **Pattern Matcher** 🔍
   - Routes: SEARCH_PATTERNS intents
   - Examples: "Have we solved X before?"

10. **Learner** 📖
    - Routes: POST_EXECUTION (automatic)
    - Examples: After every session (background)

**PLUGINS (Show as optional routing destinations):**

- Platform Switch → SETUP intents
- Configuration Wizard → CONFIGURE intents
- Cleanup → CLEANUP intents
- Doc Refresh → STORY, DOCUMENTATION intents

**BOTTOM: ROUTING FLOW EXAMPLE**

Show complete flow for sample request:

**Example: "Add authentication to the dashboard"**

```
Input: "Add authentication to the dashboard"
    ↓
Intent Detector: Keyword Analysis
    - Action: "Add" → EXECUTE
    - Target: "authentication"
    - Context: "dashboard"
    ↓
Classification: EXECUTE intent
    ↓
Context Enrichment:
    - Tier 1: Previous auth discussions
    - Tier 2: JWT pattern (93% success)
    - Tier 3: Current test coverage 67%
    ↓
Agent Selection: Executor
    ↓
Multi-agent Workflow:
    1. Executor: Implement auth
    2. Tester: Generate tests
    3. Validator: Review code
    4. Learner: Update knowledge
    ↓
Response to User ✅
```

**METRICS PANEL (Bottom right):**

**Routing Performance:**
- Intent Detection Accuracy: 99.1%
- Avg Routing Time: <300ms
- Multi-agent Workflows: 73%
- Single-agent Workflows: 27%
- Ambiguity Resolution: 94%

**Visual Style:**
- **CORTEX color scheme:** Gold (#ffd93d) for Intent Detector, Teal (#4ecdc4) for LEFT agents, Green (#96ceb4) for RIGHT agents
- Decision tree: Clear YES/NO branches
- Agent cards: Icons with routing indicators
- Flow arrows: Bold, directional, labeled
- Code/logic examples: Monospace font in boxes
- **0.5" margins on all sides** (prevents content from being cut off when printed)
- Professional NLP/routing aesthetic
- Clear typography with intent labels
- **WHITE background (solid white #ffffff, NOT transparent)**

**Typography:**
- Intent names: Bold, 14-16pt
- Natural language examples: Italic, 11-12pt
- Agent names: Bold, 12-14pt
- Flow labels: Regular, 10-11pt
- Code blocks: Monospace, 9-10pt

**Visual Hierarchy:**
- Intent Detector: Largest, center focus
- Input examples: Left column, grouped by type
- Agent routing: Right column, organized by brain hemisphere
- Flow example: Bottom, step-by-step progression

Make this diagram show how CORTEX "understands" natural language without requiring slash commands or rigid syntax. Show the intelligence of the routing system. Professional quality for technical architecture documentation.
```

---

## 🎨 Color Palette

| Element | Color | Hex | Usage |
|---------|-------|-----|-------|
| Intent Detector | Gold | #ffd93d | Routing engine |
| LEFT Brain Agents | Teal | #4ecdc4 | Tactical execution |
| RIGHT Brain Agents | Green | #96ceb4 | Strategic planning |
| Arrows | Blue | #45b7d1 | Data flow |
| Code Boxes | Light Gray | #f8f9fa | Examples |
| Text Primary | Dark | #2d3436 | Main text |

---

## 📐 Layout

**Landscape (5100 x 3300 pixels):**
```
┌────────────────────────────────────────────────┐
│  TITLE & SUBTITLE                       (400px)│
├────────────────────────────────────────────────┤
│  INPUT      │  INTENT DETECTOR  │  AGENT       │
│  EXAMPLES   │  (Gold)           │  ROUTING     │
│  (1200px)   │  (1800px)         │  (1500px)    │
│             │                   │              │
├────────────────────────────────────────────────┤
│  ROUTING FLOW EXAMPLE & METRICS         (900px)│
└────────────────────────────────────────────────┘
```

---

## 📝 Usage Instructions

1. Copy AI prompt
2. Use any AI platform with image generation (ChatGPT-4 with DALL-E, Claude, Gemini, etc.)
3. Generate image
4. Download PNG
5. Save to: `docs/images/print-ready/09-intent-routing-system.png`

---

## 💡 Key Messages

- **Natural language understanding** - no slash commands needed
- **Intelligent routing** - context-aware agent selection
- **Multi-agent workflows** - complex requests use multiple agents
- **High accuracy** - 99.1% intent detection success
- **Plugin integration** - registered commands auto-discovered

---

*Created: 2025-11-13 | Intent detection and agent routing visualization*
