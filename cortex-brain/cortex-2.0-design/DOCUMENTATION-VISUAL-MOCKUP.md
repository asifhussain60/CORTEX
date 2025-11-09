# CORTEX MkDocs Visual Design Mockup

**Version:** 1.0.0  
**Created:** 2025-11-09  
**Purpose:** Visual preview of story/technical separation

---

## 🎨 What It Will Look Like

This document shows what readers will see when they visit the CORTEX MkDocs site.

---

## Example: Part 1 - The Problem (Story-Driven)

```markdown
<div class="story-section">

# PART 1: THE PROBLEM

*Once upon a time, in a dimly lit basement...*

## Chapter 1: The Intern Who Forgot

So Asif Codeinstein sat at his desk, staring at the GitHub Copilot chat. He'd just spent thirty minutes explaining his entire project architecture, database schema, and authentication flow. The AI had listened patiently, generated some brilliant code, and then...

*"Hey Copilot, can you now update the user profile endpoint to use that authentication flow we just discussed?"*

**Copilot:** *"What authentication flow?"*

*Narrator: And this is where our story begins.*

![Brain Architecture](images/img-001-brain-architecture.png)
*CORTEX's dual-hemisphere architecture was born from this amnesia problem*

Asif realized something profound: GitHub Copilot was like an incredibly smart intern with **total amnesia**. Every conversation started from scratch. Every context explanation had to be repeated. It was like teaching someone to ride a bike... and then they forgot they even owned a bike.

"This tin can needs a brain," Asif muttered. "A real one."

</div>
```

**Visual Result:**
- **Font:** Comic Sans MS (fun, approachable)
- **Background:** Warm cream color (#fff9f0)
- **Border:** Rounded corners with amber border
- **Text:** Dark brown, easy to read
- **Headers:** Purple gradient
- **Feels Like:** Reading a tech story, not documentation

---

## Example: Part 2 - The Solution (Story + Technical)

```markdown
<div class="story-section">

## Chapter 2: The Brain That Built Garbage

Six months later, CORTEX could remember. But there was a problem.

*"Hey CORTEX, plan the authentication system."*

**CORTEX RIGHT BRAIN:** "Brilliant! I've designed a modular, scalable auth system with JWT tokens, refresh mechanisms, and OAuth2 integration!"

*"Great! Now implement it."*

**CORTEX LEFT BRAIN:** "I've shipped the code! 847 lines of untested, uncommented spaghetti!"

**RIGHT BRAIN:** "WHAT HAVE YOU DONE?!"

**LEFT BRAIN:** "You said build it! I built it! Fast!"

*Narrator: Houston, we have a coordination problem.*

</div>

<div class="content-transition">✧ ✦ ✧</div>

<div class="technical-section">

### Technical Deep-Dive: Dual-Hemisphere Architecture

CORTEX implements a **corpus callosum** message queue to coordinate between strategic planning (RIGHT BRAIN) and tactical execution (LEFT BRAIN).

**Architecture:**
- **RIGHT BRAIN (Strategic):** Intent detection, planning, validation
- **LEFT BRAIN (Tactical):** Code execution, testing, deployment
- **Corpus Callosum:** Message queue with acknowledgment protocol

```python
# Corpus Callosum coordination
message = {
    "from": "right_brain",
    "to": "left_brain",
    "intent": "IMPLEMENT_AUTH",
    "plan": plan_object,
    "constraints": ["MUST_HAVE_TESTS", "MUST_HAVE_DOCS"]
}
corpus_callosum.send(message)
```

**Benefits:**
- Strategic thinking separated from tactical execution
- Quality gates enforced through message protocol
- Parallel processing when appropriate
- Clear accountability (which hemisphere did what)

![Dual Hemisphere Flow](images/img-002-dual-hemisphere.png)
*LEFT and RIGHT BRAIN coordination through corpus callosum*

</div>
```

**Visual Result:**

**Story Section:**
- Comic Sans font
- Warm cream background
- Rounded corners
- Purple headers
- Fun, narrative style

**Transition:**
- ✧ ✦ ✧ visual separator
- Signals content type change

**Technical Section:**
- Roboto font (professional)
- Cool blue background
- Sharp, boxed corners
- Blue headers
- Code blocks with black background
- Professional diagram

**Reader Experience:**
- Can visually scan and know: "This is story, this is technical"
- Never confused about content type
- Story carries narrative, technical provides depth
- Can skip technical sections if desired (but styled attractively)

---

## Example: Code Block (Black Background)

```markdown
<div class="technical-section">

### Tier 1 Memory API

```python
# Store conversation in Tier 1
from src.tier1.conversation_manager import ConversationManager

manager = ConversationManager()
manager.store_conversation(
    user_request="Add authentication",
    intent="IMPLEMENT",
    context={"files": ["auth.py"]},
    outcome="success"
)

# Retrieve last 20 conversations
conversations = manager.get_recent_conversations(limit=20)
```

**Result:** Perfect conversation continuity across sessions.

</div>
```

**Visual Result:**
- Code block: **Black background (#000000)**
- Code text: **White (#ffffff)**
- Syntax highlighting optimized for dark background
- Inline code also black background
- Stands out clearly from surrounding text

---

## Example: Timeline Section (Part 3)

```markdown
<div class="timeline-section">

## The Evolution Timeline

### November 2024: CORTEX 1.0
- **Problem:** GitHub Copilot amnesia
- **Solution:** Tier 1 memory (SQLite)
- **Result:** Conversations remembered!

### January 2025: Dual Hemisphere
- **Problem:** Building garbage too fast
- **Solution:** Split brain (strategic + tactical)
- **Result:** Quality gates enforced

### March 2025: CORTEX 2.0
- **Problem:** Monolithic, bloated codebase
- **Solution:** Modular architecture
- **Result:** 97.2% token reduction

![Token Optimization](images/img-006-token-optimization.png)
*From 74,047 tokens to 2,078 tokens - 97.2% reduction*

</div>
```

**Visual Result:**
- **Font:** Roboto (clean timeline)
- **Background:** Light green (#f0fff4)
- **Border:** Green with rounded corners
- **Style:** Clean, chronological
- **Perfect for:** Historical context

---

## 📱 Mobile Responsive

On mobile devices (≤768px width):
- Story/technical sections stack vertically
- Font sizes adjust automatically
- Padding reduces for smaller screens
- Drop cap removed (mobile optimization)
- Images scale responsively
- Navigation collapses to hamburger menu

---

## 🎯 Key Visual Distinctions

### Story Sections
| Element | Style |
|---------|-------|
| Font | Comic Sans MS |
| Background | Warm cream (#fff9f0) |
| Corners | Rounded (12px) |
| Border | Amber (#ffe4b5) |
| Headers | Purple gradient |
| Feel | Fun, narrative |

### Technical Sections
| Element | Style |
|---------|-------|
| Font | Roboto |
| Background | Cool blue (#f0f4ff) |
| Corners | Sharp (8px) |
| Border | Light blue (#b0c4de) |
| Headers | Blue gradient |
| Feel | Professional, precise |

### Code Blocks
| Element | Style |
|---------|-------|
| Background | Black (#000000) |
| Text | White (#ffffff) |
| Font | Roboto Mono |
| Border | Dark gray |
| Feel | Terminal-like |

---

## 🌟 Final Result

**What readers will see:**
1. Open THE-AWAKENING-OF-CORTEX.md
2. See beautiful story sections (comic font, cream background)
3. Encounter technical deep-dives (professional font, blue boxes)
4. Code examples stand out (black background, white text)
5. Images integrated contextually with captions
6. Can visually scan and know content type instantly
7. Mobile-responsive and print-friendly

**Benefits:**
- ✅ 95% story / 5% technical ratio maintained
- ✅ Visual scanning: readers never confused
- ✅ Accessible to all audiences
- ✅ Technical details available but not overwhelming
- ✅ Engaging, fun to read
- ✅ Professional when needed

---

## 🖥️ Live Preview

To see it locally:

```bash
# Install dependencies
pip install mkdocs mkdocs-material pymdown-extensions

# Serve locally
mkdocs serve

# Visit http://127.0.0.1:8000
```

**You'll see:**
- Material theme with CORTEX branding
- Story/technical visual separation
- Comic font for story (fun!)
- Black code blocks (professional)
- Light, subtle backgrounds
- Beautiful diagrams with captions
- Fast, instant navigation

---

*This is what CORTEX documentation will look like after implementation!*
