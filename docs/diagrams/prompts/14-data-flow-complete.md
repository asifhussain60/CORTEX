# Image Prompt: CORTEX Complete Data Flow

**For:** ChatGPT Image Generator (DALL-E 3)

## Prompt

Create a professional end-to-end system flow diagram with generous margins (10% on all sides) showing complete data flow through CORTEX from user request to learned pattern. The diagram should be centered with clear spacing.

**Visual Style:**
- Modern tech aesthetic with gradient background (dark navy to deep purple)
- Vertical flow from top to bottom showing complete journey
- Use color coding for different phases: detect (orange), execute (blue), learn (green), validate (purple)
- Professional typography with perfect spelling
- Include timing metrics at each stage

**Flow Layout (Top to Bottom, 8 Stages):**

**Stage 1: User Input (Gray - Top):**
- Icon: Person with speech bubble
- Input: "User: 'Add authentication to login page'"
- Timestamp: "T+0ms"

**Stage 2: Intent Detection (Orange #F59E0B):**
- Component: "INTENT ROUTER"
- Actions:
  • Parse: "add authentication"
  • Extract: "login page"
  • Query Tier 2: Search patterns
  • Detect: "EXECUTE intent (92% confidence)"
- Route to: "Code Executor"
- Timestamp: "T+45ms"

**Stage 3: Work Planning (Orange #F59E0B):**
- Component: "WORK PLANNER"
- Actions:
  • Search similar: "auth patterns (Tier 2)"
  • Found: "login_authentication_workflow (0.88)"
  • Create: "4-phase plan"
  • Phases: "Test → Implement → Validate → Commit"
- Timestamp: "T+187ms"

**Stage 4: Test Creation (Blue #3B82F6):**
- Component: "TEST GENERATOR"
- Actions:
  • Generate: "LoginTests.cs"
  • Tests: "valid_credentials(), invalid_credentials()"
  • Run: "ALL FAIL ✓ (RED phase)"
- Files: "LoginTests.cs (47 lines)"
- Timestamp: "T+1.2s"

**Stage 5: Implementation (Blue #3B82F6):**
- Component: "CODE EXECUTOR"
- Actions:
  • Create: "AuthService.cs"
  • Implement: "Login() method"
  • Integrate: "LoginController.cs"
  • Run tests: "ALL PASS ✓ (GREEN phase)"
- Files: "AuthService.cs (128 lines), LoginController.cs (64 lines)"
- Timestamp: "T+4.5s"

**Stage 6: Validation (Purple #6B46C1):**
- Component: "HEALTH VALIDATOR"
- Actions:
  • Run: "Full test suite (47 tests)"
  • Check: "Zero errors ✓"
  • Check: "Zero warnings ✓"
  • Coverage: "82% (target: 80%)"
  • Status: "DEFINITION OF DONE MET ✓"
- Timestamp: "T+6.8s"

**Stage 7: Commit (Blue #3B82F6):**
- Component: "COMMIT HANDLER"
- Actions:
  • Create: "Semantic commit message"
  • Message: "feat(auth): Add login authentication"
  • Body: "Implements AuthService with JWT validation"
  • Commit: "SHA: a1b2c3d"
- Timestamp: "T+7.1s"

**Stage 8: Learning (Green #10B981):**
- Component: "TIER 2 KNOWLEDGE GRAPH"
- Actions:
  • Extract: "Workflow pattern"
  • Files: "LoginTests.cs, AuthService.cs, LoginController.cs"
  • Success rate: "100%"
  • Store: "auth_implementation_pattern"
  • Update confidence: "0.88 → 0.91"
- Label: "LEARNED FOR FUTURE REUSE"
- Timestamp: "T+7.3s"

**Right Side Panel: Metrics Summary:**
- "TOTAL TIME: 7.3s"
- "FILES CREATED: 3"
- "TESTS WRITTEN: 8"
- "TESTS PASSING: 47/47"
- "CODE QUALITY: ✓ EXCELLENT"
- "PATTERN STORED: ✓ YES"

**Left Side Panel: Tier Access:**
Show which tiers accessed at each stage:
- Stage 2: "Tier 2 (pattern search)"
- Stage 3: "Tier 2 (workflow template)"
- Stage 5: "Tier 1 (conversation context)"
- Stage 6: "Tier 3 (file stability)"
- Stage 8: "Tier 2 (store pattern)"

**Typography Requirements:**
- All text perfectly spelled
- Stage headings: 20pt, bold
- Component names: 18pt, bold
- Actions: 14pt, regular with bullet points
- Timestamps: 12pt, monospace
- Metrics: 16pt, bold

**Color Palette:**
- User Input: Gray (#6B7280)
- Detection/Planning: Orange (#F59E0B) with border (#92400E)
- Execution/Testing: Blue (#3B82F6) with border (#1E3A8A)
- Validation: Purple (#6B46C1) with border (#4C1D95)
- Learning: Green (#10B981) with border (#065F46)
- Background: Gradient from #0F172A to #4C1D95
- Arrows: White with glow
- Text: White (#FFFFFF)

**Margin Requirements:**
- Top margin: 10% of canvas height
- Bottom margin: 10% of canvas height
- Left margin: 10% of canvas width
- Right margin: 10% of canvas width

**Additional Elements:**
- "CORTEX Complete Data Flow" title at top
- "User Request → Execution → Learning • End-to-End Journey" subtitle
- "⚡ 7.3s TOTAL TIME" badge (top right, green)
- "© 2024-2025" copyright bottom right

Make it look like a professional system architecture diagram with perfect spelling and clear data flow progression.
