# MkDocs Issues and Fixes - November 7, 2025

**Status:** 🔄 IN PROGRESS  
**Phase:** Post-Hybrid Implementation Refinements

---

## 🐛 Issues Identified

### Issue 1: Images Not Showing in Story ❌
**Problem:** Image paths are broken - using `../../images/` but files aren't accessible  
**Root Cause:** Images in `docs/images/cortex-awakening/` but story files reference `../../images/`  
**Impact:** All story illustrations missing (Figures 2.0-5.3 across all chapters)

**Solution:**
- Move image files from `docs/images/cortex-awakening/` to `docs/story/images/`
- Update all image references in chapter files from `../../images/cortex-awakening/` to `images/`
- Simpler path: `![alt](images/filename.png)` instead of `![alt](../../images/cortex-awakening/filename.png)`

**Files to Update:**
- `chapter-1-the-problem.md` (0 images - no changes needed)
- `chapter-2-the-solution.md` (7 image references)
- `chapter-3-the-memory.md` (6 image references)
- `chapter-4-the-protection.md` (3 image references)
- `chapter-5-the-activation.md` (multiple image references)

**Estimated Time:** 15 minutes

---

### Issue 2: Home Page - Replace Content with CORTEX BIBLE ❌
**Problem:** Home page shows generic "The Problem" section instead of the governance rules  
**Desired:** Display CORTEX BIBLE (governance rules) formatted like a scroll with prominent rules

**Solution:**
- Replace home page hero section with "CORTEX BIBLE" scroll design
- Extract rules from `governance/rules.md` or create comprehensive rule list
- Format as scroll with categories:
  - **🧠 Core Values** (TDD, SOLID, DoR/DoD)
  - **🔄 Workflow Rules** (RED → GREEN → REFACTOR)
  - **🛡️ Protection Rules** (Brain integrity, challenge system)
  - **📚 Learning Rules** (Auto-learning, pattern extraction)
  - **🕷️ Discovery Rules** (Oracle Crawler, UI element mapping)
- Use large, prominent font sizes for each rule
- CSS styling for scroll appearance (parchment color, decorative borders)

**File to Update:**
- `docs/index.md` - Replace hero section and main content

**Estimated Time:** 30 minutes

---

### Issue 3: Broken Links - 404 Errors ❌
**Problem:** "Get Started in 5 Minutes" and "Read The Story" buttons giving 404 errors  
**Root Cause:** Links point to non-existent files

**Current Broken Links:**
- `getting-started/quick-start/` → File doesn't exist yet (Phase 5b not started)
- `story/the-awakening/` → Should be `story/index/` (story landing page)

**Solution:**
- Update `docs/index.md` links:
  - Change `story/the-awakening/` to `story/` (MkDocs auto-resolves to index.md)
  - Change `getting-started/quick-start/` to `story/` temporarily until Phase 5b completed
- Create placeholder files for all referenced documentation (prevents build warnings)

**Files to Update:**
- `docs/index.md` - Fix button links
- Optionally: Create placeholder stubs for missing docs

**Estimated Time:** 10 minutes

---

### Issue 4: Technical Documentation Background Color ❌
**Problem:** Black background for technical sections not desired  
**Desired:** Use standard industry colors for markdown/technical documentation

**Solution:**
- Update `docs/stylesheets/custom.css`
- Change `.technical-section` background from `#F0F4F8` (current light gray) to better option
- Research standard technical doc colors:
  - **Option A:** GitHub-style `#F6F8FA` (very light gray-blue)
  - **Option B:** Documentation-style `#FAFBFC` (near-white with hint of gray)
  - **Option C:** Material-style `#ECEFF1` (light blue-gray)
- Keep code blocks black background (explicitly requested)
- Only change technical prose sections

**File to Update:**
- `docs/stylesheets/custom.css` - `.technical-section` class

**Estimated Time:** 5 minutes

---

### Issue 5: Add Internal Tooling & Tech Stack Section ⭐
**Problem:** No section documenting the tools and technologies used to build CORTEX  
**Desired:** Comprehensive section showing internal tooling and tech stack

**Solution:**
- Create new documentation page: `docs/reference/tech-stack.md`
- Categories:
  - **💻 Core Languages** (Python 3.11+)
  - **📦 Storage & Data** (SQLite, JSONL, YAML, FTS5)
  - **🧪 Testing** (pytest, Playwright, coverage.py)
  - **📚 Documentation** (MkDocs Material, Mermaid diagrams)
  - **🛠️ Development Tools** (VS Code, Git, pre-commit hooks)
  - **🎨 UI/UX** (Material Design, CSS3, Comics Sans MS for story)
  - **🔧 Build Tools** (PowerShell scripts, Python build system)
  - **🌐 Deployment** (GitHub Pages, GitHub Actions)
  - **🧠 AI Integration** (GitHub Copilot, Google Gemini for image generation)
  - **📊 Metrics & Analysis** (Git metrics, code analysis tools)

**File to Create:**
- `docs/reference/tech-stack.md` - Complete tech stack documentation

**Add to mkdocs.yml nav:**
```yaml
- 📖 Reference:
    - Tech Stack & Tooling: reference/tech-stack.md  # NEW
    - Tier 0 - Governance: reference/tier0-governance.md
    # ... rest of reference docs
```

**Estimated Time:** 45 minutes

---

## 📋 Updated Implementation Plan

### **Phase 6a: Bug Fixes & Content Updates** ⏱️ ~1 hour 15 min

#### Task 1: Fix Image Paths (Issue #1) - 15 min
```powershell
# Move images to story folder
Move-Item "docs\images\cortex-awakening\*" "docs\story\images\" -Force

# Update all chapter files (find/replace ../../images/cortex-awakening/ → images/)
```

**Files to edit:**
- `chapter-2-the-solution.md`
- `chapter-3-the-memory.md`
- `chapter-4-the-protection.md`
- `chapter-5-the-activation.md`

---

#### Task 2: Fix Broken Links (Issue #3) - 10 min
```yaml
# Update docs/index.md
Old: href="getting-started/quick-start/"
New: href="story/"

Old: href="story/the-awakening/"
New: href="story/"
```

**Files to edit:**
- `docs/index.md` (fix CTA button links)

---

#### Task 3: Update Technical Section Colors (Issue #4) - 5 min
```css
/* Change .technical-section background */
.technical-section {
  background: #FAFBFC;  /* Near-white, standard docs color */
  /* or */
  background: #F6F8FA;  /* GitHub-style */
}
```

**Files to edit:**
- `docs/stylesheets/custom.css`

---

#### Task 4: Create CORTEX BIBLE Home Page (Issue #2) - 30 min
```markdown
# New home page structure
1. Hero with brain icon
2. CORTEX BIBLE scroll (large prominent rules)
3. Categories: Core Values, Workflow, Protection, Learning, Discovery
4. Big fonts, decorative scroll styling
5. CTA buttons to story and docs
```

**Files to edit:**
- `docs/index.md` (complete rewrite of main content)

**CSS additions:**
- `.cortex-bible-scroll` - Scroll styling
- `.bible-rule` - Individual rule styling
- `.bible-category` - Category headers

---

#### Task 5: Create Tech Stack Documentation (Issue #5) - 45 min
```markdown
# New file: docs/reference/tech-stack.md
- Complete tooling inventory
- Categorized by purpose
- Version numbers
- Why each tool was chosen
- Links to documentation
```

**Files to create:**
- `docs/reference/tech-stack.md`

**Files to edit:**
- `mkdocs.yml` (add to navigation)

---

### **Phase 6b: Validation & Testing** ⏱️ ~20 min

1. **Build Test:** `mkdocs build --clean` - Verify no errors
2. **Image Verification:** Check all chapter images display
3. **Link Testing:** Test all CTA buttons and navigation links
4. **Visual Review:** Check CORTEX BIBLE scroll appearance
5. **Color Validation:** Ensure technical sections use standard colors
6. **Tech Stack Review:** Verify all tools documented

---

### **Phase 7: Git Commit & Deploy** ⏱️ ~10 min

```powershell
git add docs/ mkdocs.yml
git commit -m "fix(docs): Resolve issues and add CORTEX BIBLE home page

- Move images to story/ folder for correct paths
- Replace home page with CORTEX BIBLE scroll design
- Fix broken CTA button links (404 errors)
- Update technical section background to standard colors
- Add comprehensive tech stack documentation
- All images now displaying correctly
- All links functional"

git push origin cortex-migration
```

---

## 🎯 Total Estimated Time

| Phase | Duration | Status |
|-------|----------|--------|
| Task 1: Fix Images | 15 min | ⏳ TODO |
| Task 2: Fix Links | 10 min | ⏳ TODO |
| Task 3: Update Colors | 5 min | ⏳ TODO |
| Task 4: CORTEX BIBLE | 30 min | ⏳ TODO |
| Task 5: Tech Stack | 45 min | ⏳ TODO |
| Validation | 20 min | ⏳ TODO |
| Git Commit | 10 min | ⏳ TODO |
| **TOTAL** | **~2 hours 15 min** | - |

---

## 📝 CORTEX BIBLE Rules Preview

Here are the key rules to display prominently on the home page:

### 🧠 Core Values (Tier 0 - Immutable)
1. **Test-Driven Development** - Always RED → GREEN → REFACTOR, no exceptions
2. **Definition of READY** - Clear requirements before starting work
3. **Definition of DONE** - Zero errors, zero warnings, all tests passing
4. **SOLID Principles** - Single Responsibility, no mode switches
5. **Challenge Risky Requests** - Even from the user, especially from the user

### 🔄 Workflow Rules
6. **RED Phase** - Write failing tests first
7. **GREEN Phase** - Minimum code to pass tests
8. **REFACTOR Phase** - Clean up with confidence (tests protect you)
9. **One Door Entry** - All requests through `#file:prompts/user/cortex.md`
10. **Hemisphere Routing** - RIGHT plans, LEFT executes

### 🛡️ Protection Rules
11. **Layer 1** - Instinct Immutability (Tier 0 never changes)
12. **Layer 2** - Tier Boundary Protection (data in correct tier)
13. **Layer 3** - SOLID Compliance (single responsibility enforced)
14. **Layer 4** - Hemisphere Specialization (auto-routing)
15. **Layer 5** - Knowledge Quality (pattern decay <0.50 confidence)
16. **Layer 6** - Commit Integrity (brain files never committed)

### 📚 Learning Rules
17. **FIFO Queue** - Last 20 conversations, oldest deleted first
18. **Pattern Extraction** - Before deletion, patterns → Tier 2
19. **Auto-Learning Trigger** - 50+ events OR 24 hours → BRAIN update
20. **Confidence Reinforcement** - Successful patterns gain confidence
21. **Knowledge Decay** - Unused patterns (<90 days) marked for review

### 🕷️ Discovery Rules
22. **Oracle Crawler** - Deep scan during setup (5-10 minutes)
23. **UI Element IDs** - All IDs mapped for robust test selectors
24. **File Relationships** - Co-modification patterns tracked
25. **Architectural Patterns** - Component hierarchies documented
26. **Database Schema** - SQL files discovered FIRST, then connection strings

---

## 🎨 CORTEX BIBLE Scroll Design

**CSS Styling:**
```css
.cortex-bible-scroll {
  background: linear-gradient(135deg, #FEF3E2 0%, #FFEAA7 100%);
  border: 4px solid #D4A373;
  border-radius: 16px;
  padding: 3rem;
  margin: 2rem 0;
  box-shadow: 0 8px 24px rgba(212, 163, 115, 0.3);
  position: relative;
}

.cortex-bible-scroll::before {
  content: "📜";
  font-size: 3rem;
  position: absolute;
  top: -1.5rem;
  left: 50%;
  transform: translateX(-50%);
}

.bible-category {
  font-size: 1.8rem;
  font-weight: bold;
  color: #8B4513;
  margin: 2rem 0 1rem 0;
  text-align: center;
  border-bottom: 3px solid #D4A373;
  padding-bottom: 0.5rem;
}

.bible-rule {
  font-size: 1.3rem;
  font-weight: 600;
  color: #5D4037;
  margin: 1.5rem 0;
  padding: 1rem 1.5rem;
  background: rgba(255, 255, 255, 0.5);
  border-left: 6px solid #FF6B6B;
  border-radius: 8px;
}

.bible-rule strong {
  color: #C0392B;
  font-size: 1.4rem;
}
```

---

## 🚀 Next Steps

**Ready to proceed?** I can start implementing these fixes in order:

1. ✅ **Start with Task 1** (Fix images) - Quick win, visible improvement
2. ✅ **Then Task 2** (Fix links) - Removes 404 errors
3. ✅ **Then Task 3** (Update colors) - Visual polish
4. ✅ **Then Task 4** (CORTEX BIBLE) - Major home page overhaul
5. ✅ **Then Task 5** (Tech Stack) - New documentation section

**Confirm to begin implementation!**
