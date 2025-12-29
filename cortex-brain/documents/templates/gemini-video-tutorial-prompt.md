# 🎬 Gemini Video Generation Prompt: CORTEX Setup Tutorial

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Created:** December 29, 2025  
**Target Platform:** Google Gemini Video Generation API  
**Duration:** 8-10 minutes  
**Format:** Tutorial/Screencast with narration

---

## 🎯 Video Generation Prompt

### Core Instruction

```
Create a professional tutorial video demonstrating the complete setup and first-use workflow 
for CORTEX - an AI assistant enhancement system for GitHub Copilot. The video should be 
engaging, concise, and suitable for developers who are new to CORTEX but familiar with 
VS Code and GitHub Copilot.
```

---

## 📋 Video Structure & Scenes

### Scene 1: Opening & Introduction (30 seconds)

**Visual Elements:**
- Animated CORTEX logo with brain hemisphere visual (left/right brain concept)
- Fade to VS Code with GitHub Copilot Chat open
- Text overlay: "CORTEX 4.0 - Setup Tutorial"
- Subtitle: "Transform GitHub Copilot from forgetful intern to expert team member"

**Narration Script:**
```
"Welcome to CORTEX - the cognitive enhancement system that gives GitHub Copilot 
long-term memory, strategic planning capabilities, and quality protection. 
In this 10-minute tutorial, we'll install CORTEX, configure it, and complete 
your first AI-assisted development workflow. Let's get started."
```

**Visual Style:**
- Modern glassmorphism UI elements
- Smooth transitions with subtle brain network animations
- Color scheme: Blues (#2196F3), purples (#9C27B0), with frosted glass effects

---

### Scene 2: The Problem (45 seconds)

**Visual Elements:**
- Split screen showing "Before CORTEX" vs "After CORTEX"
- Animation of chat bubbles fading away (representing amnesia)
- Counter showing: "Session 1 → Session 2 → Memory Lost"
- Transition to CORTEX brain storing memories

**Narration Script:**
```
"GitHub Copilot has one critical limitation: amnesia. Every new chat session, 
everything you've discussed disappears. That architecture you explained? Gone. 
The feature you built yesterday? Forgotten. You're constantly re-explaining context.

CORTEX solves this with a 4-tier cognitive system: Tier 0 enforces best practices, 
Tier 1 stores 70 conversations, Tier 2 learns patterns from your work, and 
Tier 3 tracks your entire codebase. Let's install it."
```

**Visual Cues:**
- Animated tier stack building up (Tier 0 → Tier 1 → Tier 2 → Tier 3)
- Memory capacity counter: "0 → 70 conversations"
- Pattern learning visualization with connecting dots

---

### Scene 3: Prerequisites Check (30 seconds)

**Visual Elements:**
- Checklist appearing with animated checkmarks
- Terminal window showing version commands
- VS Code interface with Copilot extension highlighted

**Narration Script:**
```
"Before we start, verify you have: VS Code installed, GitHub Copilot extension active, 
Python 3.9 or higher, and terminal access. Open your terminal and run these commands 
to verify."
```

**Screen Recording Actions:**
1. Open VS Code
2. Show Extensions panel with GitHub Copilot
3. Open integrated terminal
4. Type: `code --version` (show output)
5. Type: `python --version` (show output: Python 3.11.x)

**Text Overlays:**
```
✅ VS Code: 1.85+
✅ GitHub Copilot: Active
✅ Python: 3.9+
✅ Terminal: Ready
```

---

### Scene 4: Installation (2 minutes)

**Visual Elements:**
- Terminal in focus with typing animation
- Progress bars for installation
- File tree showing CORTEX structure appearing

**Narration Script:**
```
"Installation is simple. We have two options: quick install via pip for immediate use, 
or development install if you want to explore the codebase. Let's do the quick install.

In your VS Code terminal, type: pip install cortex-ai

This downloads and installs CORTEX with all dependencies. The installation creates 
the cortex-brain folder structure with four cognitive tiers, manifest files for 
orchestrators, and response templates."
```

**Screen Recording Actions:**
1. Show terminal prompt
2. Type: `pip install cortex-ai`
3. Show installation progress (truncated for time)
4. Fast-forward animation showing package download
5. Show completion message: "Successfully installed cortex-ai-4.0.0"
6. Split screen: Terminal + File Explorer
7. Navigate to show created structure:
   ```
   cortex-brain/
   ├── tier0/ (Governance)
   ├── tier1/ (Working Memory)
   ├── tier2/ (Knowledge Graph)
   ├── tier3/ (Dev Context)
   └── manifests/orchestrators/
   ```

**Visual Annotations:**
- Highlight tier folders as they appear
- Show file count increasing
- Animated arrows showing data flow between tiers

---

### Scene 5: First Command - Help (1 minute)

**Visual Elements:**
- GitHub Copilot Chat panel opening
- User typing in chat
- Response appearing with formatted command list

**Narration Script:**
```
"Let's verify CORTEX is working. Open GitHub Copilot Chat and type: help

CORTEX responds with all available operations organized by category. 
You'll see System Operations like healthcheck and align, Planning commands 
like 'plan' and 'start tdd', and Advanced Operations for administrators."
```

**Screen Recording Actions:**
1. Click Copilot Chat icon in sidebar
2. Type: `help`
3. Show response rendering with categories:
   - System Operations
   - Planning & Development
   - Advanced Operations
4. Hover over different commands to show tooltips
5. Highlight key commands with animated underlines

**Visual Highlights:**
- Color-code command categories
- Animated table rows appearing sequentially
- Spotlight effect on most-used commands

---

### Scene 6: Health Check (45 seconds)

**Visual Elements:**
- Command being typed: `healthcheck`
- Diagnostic animation running (spinning brain icon)
- Results appearing in formatted table

**Narration Script:**
```
"Run your first diagnostic. Type: healthcheck

CORTEX checks all four cognitive tiers, verifies manifest integrity, validates 
the brain structure, and confirms orchestrator availability. All systems should 
show green checkmarks. If you see any errors, type 'align' to auto-fix."
```

**Screen Recording Actions:**
1. Type in chat: `healthcheck`
2. Show animated progress indicator
3. Display results table:
   ```
   ✅ Tier 0: Governance Rules Active
   ✅ Tier 1: Working Memory (70 slots available)
   ✅ Tier 2: Knowledge Graph Ready
   ✅ Tier 3: Dev Context Tracking
   ✅ Manifests: 8 orchestrators loaded
   ✅ Brain Protection: SKULL rules active
   ```
4. Show summary: "🎉 All systems operational"

**Visual Effects:**
- Checkmarks animating in sequence
- Health meter filling up to 100%
- Subtle celebration animation on success

---

### Scene 7: Creating Your First Plan (2 minutes)

**Visual Elements:**
- User typing plan command
- CORTEX analyzing complexity
- File structure being created in real-time
- Master plan document opening

**Narration Script:**
```
"Now for the exciting part - let's create your first feature plan. 
Type: plan a todo list API with CRUD operations

Watch what happens. CORTEX analyzes the complexity, determines it's a LOW complexity 
task, generates a 5-phase plan with Test-Driven Development built in, and creates 
a complete project folder structure.

Notice the output folder: cortex-brain/documents/planning/active/todo-list-api/
It contains your master plan, context folder for research, reports folder for 
progress tracking, artifacts for supporting files, and a tracking folder with 
progress-tracker.json."
```

**Screen Recording Actions:**
1. Type: `plan a todo list API with CRUD operations`
2. Show CORTEX "thinking" animation
3. Display complexity analysis:
   ```
   🧠 Analyzing request...
   Complexity: LOW
   Phases: 5
   TDD: Enabled
   ```
4. Show folder creation animation in Explorer:
   ```
   cortex-brain/documents/planning/active/todo-list-api/
   ├── 00-master-plan.md
   ├── context/
   ├── reports/
   ├── artifacts/
   └── tracking/
       └── progress-tracker.json
   ```
5. Open `00-master-plan.md` and scroll through sections:
   - Overview
   - Phases (RED → GREEN → REFACTOR → DOCUMENT → VALIDATE)
   - Definition of Ready (DoR)
   - Definition of Done (DoD)
   - Success Criteria

**Visual Highlights:**
- Folder tree expanding with animation
- Phase badges appearing (RED, GREEN, REFACTOR)
- Checklist items with interactive checkboxes

---

### Scene 8: Starting TDD Workflow (1.5 minutes)

**Visual Elements:**
- TDD cycle visualization (RED → GREEN → REFACTOR)
- Code editor split with test file and implementation
- Tests running in terminal

**Narration Script:**
```
"CORTEX enforces Test-Driven Development through its SKULL brain protection system. 
Let's start the TDD workflow. Type: start tdd for todo list API

CORTEX guides you through RED-GREEN-REFACTOR. First, RED phase: write a failing test. 
CORTEX creates a test file and writes your first failing test for creating a todo item.

The test runs and fails - that's correct! Now GREEN phase: write minimal code to pass. 
CORTEX implements just enough code in the API to make the test pass.

Test runs again - it passes! Finally, REFACTOR phase: improve the code quality 
while keeping tests green. CORTEX suggests improvements to error handling and validation."
```

**Screen Recording Actions:**
1. Type: `start tdd for todo list API`
2. **RED Phase:**
   - Show test file creation: `tests/test_todo_api.py`
   - Display failing test code:
     ```python
     def test_create_todo():
         response = api.create_todo("Buy milk")
         assert response.status == 201
         assert response.data.title == "Buy milk"
     ```
   - Run test in terminal: `pytest tests/test_todo_api.py`
   - Show red failure: `FAILED - AssertionError`
3. **GREEN Phase:**
   - Show implementation file: `src/todo_api.py`
   - Display minimal code:
     ```python
     def create_todo(title):
         return Response(status=201, data={"title": title})
     ```
   - Run test again: `pytest tests/test_todo_api.py`
   - Show green success: `PASSED`
4. **REFACTOR Phase:**
   - Show improved code with validation
   - Tests still green
   - Code coverage indicator: 95%

**Visual Effects:**
- Traffic light animation (Red → Green → Green)
- Code diff highlighting changes
- Test output with color coding
- Coverage meter animating to 95%

---

### Scene 9: Advanced Features Preview (1 minute)

**Visual Elements:**
- Quick montage of other capabilities
- Dashboard visualizations
- ADO integration
- Code sanitization

**Narration Script:**
```
"CORTEX offers much more. Plan ADO work items with 'plan ado story'. 
Sanitize code for public sharing with 'sanitize analyze'. 
Run system maintenance with comprehensive health checks. 
Create multi-phase feature plans with strategic planning.

As you use CORTEX, it learns your patterns. Tier 2 builds a knowledge graph 
of your preferences. Tier 3 tracks hotspots in your codebase. After a few weeks, 
CORTEX feels like a senior developer who knows your project intimately."
```

**Screen Recording Actions:**
1. Quick cuts showing:
   - ADO story generation
   - Sanitization phase list
   - Health dashboard with metrics
   - Knowledge graph visualization
2. Show Tier 1 memory counter: "15/70 conversations stored"
3. Show Tier 2 pattern count: "8 patterns learned"
4. Show Tier 3 hotspot map

**Visual Style:**
- Fast-paced montage with 2-second cuts
- Overlay stats animating
- Network graph pulsing with activity

---

### Scene 10: Recap & Next Steps (45 seconds)

**Visual Elements:**
- Checklist of completed steps
- Resource links appearing
- Call-to-action overlay

**Narration Script:**
```
"Congratulations! You've installed CORTEX, verified system health, created your first 
feature plan, and run a TDD workflow. You're now equipped with an AI assistant that 
remembers, learns, and protects code quality.

Next steps: Explore the interactive tutorial with 'onboard', read the documentation 
at github.com/asifhussain60/CORTEX, and join our community for tips and best practices.

Transform your GitHub Copilot from a forgetful intern into an expert team member. 
Happy coding with CORTEX!"
```

**Screen Recording Actions:**
1. Show completion checklist:
   ```
   ✅ Installed CORTEX
   ✅ Verified system health
   ✅ Created first plan
   ✅ Ran TDD workflow
   ✅ Explored features
   ```
2. Display resource links:
   - 📖 Documentation: https://asifhussain60.github.io/CORTEX/
   - 🐙 GitHub: https://github.com/asifhussain60/CORTEX
   - 💬 Community: [Link to discussions]
3. Show final CORTEX logo with tagline

**Closing Visual:**
- Brain logo with pulsing animation
- Text: "CORTEX - Memory for Your AI"
- Fade to black

---

## 🎨 Visual Design Specifications

### Color Palette

```css
Primary: #2196F3 (Blue)
Secondary: #9C27B0 (Purple)
Accent: #00BCD4 (Cyan)
Success: #4CAF50 (Green)
Warning: #FF9800 (Orange)
Error: #F44336 (Red)
Background: #0D1117 (Dark)
Glass: rgba(255, 255, 255, 0.1) with backdrop-blur
```

### Typography

- **Title Font:** Poppins Bold, 48px
- **Subtitle Font:** Roboto Medium, 24px
- **Body Font:** Roboto Regular, 16px
- **Code Font:** Fira Code, 14px (with ligatures)

### Animation Style

- **Transitions:** Smooth easing, 300ms duration
- **Loading:** Pulsing brain icon with rotating neural network
- **Success:** Gentle bounce with checkmark
- **Progress:** Linear fills with percentage counter
- **Text:** Typing effect for narration subtitles

### UI Elements

- **Buttons:** Rounded (8px), glassmorphism with hover lift
- **Cards:** Frosted glass with subtle shadow, 12px border radius
- **Tables:** Zebra striping with alternating row colors
- **Code Blocks:** Dark theme (GitHub Dark Dimmed)
- **Icons:** Material Design with 24px size

---

## 🎙️ Audio Specifications

### Narration Voice

- **Style:** Professional, friendly, conversational
- **Pace:** Moderate (140-160 words per minute)
- **Tone:** Enthusiastic but not overwhelming
- **Accent:** Neutral American or British English

### Background Music

- **Genre:** Electronic ambient, lo-fi tech
- **Volume:** -20dB (subtle, not distracting)
- **Mood:** Focused, productive, modern
- **Key Moments:** Slight volume increase during transitions

### Sound Effects

- **Command execution:** Soft "whoosh" (50ms)
- **Success checkmarks:** Gentle "ding" (100ms)
- **Test pass/fail:** Distinctive tones (pass: C major, fail: F minor)
- **Folder creation:** Soft "pop" (80ms)
- **Transitions:** Ambient swoosh (200ms)

---

## 📊 Technical Production Notes

### Video Settings

```yaml
Resolution: 1920x1080 (Full HD)
Frame Rate: 60fps
Bitrate: 8000 kbps (high quality)
Codec: H.264
Color Space: sRGB
Aspect Ratio: 16:9
```

### Screen Recording Settings

```yaml
Capture Area: Full screen or VS Code window
Cursor: Visible with yellow highlight ring
Keystrokes: Display in bottom-right overlay
Terminal: Use high-contrast color scheme
Font Size: Increase to 16px for readability
```

### Caption/Subtitle Settings

```yaml
Format: SRT (SubRip)
Language: English (en-US)
Font: Roboto Medium, 18px
Background: Semi-transparent black bar
Position: Bottom center, 10% from edge
Display: Word-by-word highlighting during narration
```

---

## 🎬 Scene Timing Breakdown

| Scene | Duration | Cumulative |
|-------|----------|------------|
| 1. Opening & Introduction | 0:30 | 0:30 |
| 2. The Problem | 0:45 | 1:15 |
| 3. Prerequisites Check | 0:30 | 1:45 |
| 4. Installation | 2:00 | 3:45 |
| 5. First Command - Help | 1:00 | 4:45 |
| 6. Health Check | 0:45 | 5:30 |
| 7. Creating First Plan | 2:00 | 7:30 |
| 8. Starting TDD Workflow | 1:30 | 9:00 |
| 9. Advanced Features Preview | 1:00 | 10:00 |
| 10. Recap & Next Steps | 0:45 | 10:45 |

**Total Duration:** 10 minutes 45 seconds

---

## ✅ Quality Checklist

Before finalizing video, verify:

- [ ] All text is legible at 1080p resolution
- [ ] Narration syncs with on-screen actions
- [ ] Code examples are syntax-highlighted correctly
- [ ] Terminal commands execute without errors
- [ ] Transitions are smooth (no jarring cuts)
- [ ] Background music doesn't overpower narration
- [ ] Captions are accurate and timed correctly
- [ ] Brand colors (blue/purple) used consistently
- [ ] CORTEX logo appears in opening and closing
- [ ] All resource links are displayed clearly
- [ ] Video maintains 16:9 aspect ratio throughout
- [ ] Audio levels are balanced (-3dB to -6dB)
- [ ] No dead air longer than 2 seconds
- [ ] Loading/progress animations don't drag
- [ ] Call-to-action is clear and compelling

---

## 🔄 Iteration & Variants

### Short Version (3 minutes)

Focus on: Installation → First Command → TDD Workflow  
Skip: Problem explanation, advanced features, detailed health checks

### Long Version (20 minutes)

Add: Deeper dives into each tier, live coding session, troubleshooting common issues

### Platform-Specific Variants

- **YouTube:** Add end screen with subscribe button, chapter markers
- **Twitter/X:** 1-minute teaser focusing on "the problem" hook
- **LinkedIn:** Professional tone, emphasize productivity gains
- **TikTok/Shorts:** 30-second ultra-fast setup demo

---

## 📝 Gemini API Parameters

```json
{
  "model": "gemini-2.0-flash-video-exp",
  "video_generation": {
    "prompt": "[Use full prompt from above sections]",
    "duration": 645,
    "resolution": "1920x1080",
    "fps": 60,
    "style": "professional_tutorial",
    "narration": {
      "voice": "en-US-Neural2-J",
      "speed": 1.0,
      "pitch": 0.0
    },
    "visual_style": {
      "theme": "dark_mode_glassmorphism",
      "primary_color": "#2196F3",
      "accent_color": "#9C27B0",
      "animation_style": "smooth_modern"
    },
    "screen_elements": {
      "cursor_highlight": true,
      "keystroke_display": true,
      "terminal_font_size": 16,
      "code_syntax_highlighting": "github-dark-dimmed"
    },
    "audio": {
      "background_music": "electronic_ambient",
      "music_volume": 0.2,
      "sound_effects": true,
      "narration_volume": 1.0
    },
    "captions": {
      "enabled": true,
      "language": "en-US",
      "style": "word_by_word_highlight"
    }
  }
}
```

---

## 🎯 Success Metrics

After video publication, track:

- **View Duration:** Target >70% completion rate
- **Engagement:** Likes, shares, comments about setup clarity
- **Conversion:** Users who report successful CORTEX installation
- **Retention:** Viewers who watch related tutorial videos
- **Feedback:** Survey responses about video clarity and pacing

---

## 📖 Related Resources

- **Full Documentation:** https://asifhussain60.github.io/CORTEX/
- **Interactive Tutorial:** `cortex-brain/documents/learning-paths/CORTEX-4.0-INTERACTIVE-TUTORIAL.md`
- **Practice Exercises:** `cortex-brain/documents/learning-paths/CORTEX-4.0-PRACTICE-EXERCISES.md`
- **Quick Start Guide:** `cortex-brain/documents/learning-paths/CORTEX-4.0-QUICK-START.md`

---

**Copyright © 2025 Asif Hussain. All rights reserved.**
