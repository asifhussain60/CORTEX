# DALL-E Story Illustration Generation Guide

**Version:** 1.0  
**Created:** December 10, 2025  
**Purpose:** Step-by-step guide for generating consistent character illustrations

---

## 🎯 Overview

This guide ensures all 12 story illustrations maintain visual character consistency using the canonical character reference system.

**Key Principle:** Generate character sheet FIRST, then use it as visual reference for all subsequent images.

---

## 📋 Prerequisites

- ✅ ChatGPT Plus subscription (DALL-E 3 access)
- ✅ All 12 updated prompt files in `docs/gh-pages/story/illustrations/prompts/`
- ✅ Ability to upload images to ChatGPT for reference

---

## 🚀 Generation Workflow

### Step 1: Generate Character Sheet (BASELINE)

**File:** `00-character-sheet.md`

1. Open `00-character-sheet.md`
2. Copy the entire DALL-E Prompt section
3. Go to ChatGPT Plus (https://chat.openai.com/)
4. Paste prompt with prefix:

```
Generate an image using DALL-E 3:

[paste entire prompt here]
```

5. Review generated image:
   - ✅ Mr. Codenstein has wild WHITE hair, thick glasses, lab coat
   - ✅ Miss G is 70% translucent with flowing hair, ethereal
   - ✅ Copilot has rounded body, screen face, friendly design

6. If satisfied, download image:
   - Right-click → Save Image As
   - Save to: `docs/gh-pages/story/illustrations/images/00-character-sheet.png`

7. If not satisfied, regenerate with adjustments until perfect

**CRITICAL:** This establishes the visual baseline for all other images.

---

### Step 2: Generate Remaining 11 Images

**Order:** Generate in story sequence for narrative flow.

#### For Each Chapter Image:

1. **Open prompt file** (e.g., `ch1-goldfish-theory.md`)

2. **Copy DALL-E prompt section**

3. **In ChatGPT, create new request with three parts:**

```
Generate an image using DALL-E 3. Maintain character consistency with the character sheet I'm uploading.

[Upload 00-character-sheet.png here]

Here's the scene prompt:

[paste chapter prompt here]

IMPORTANT: Use the exact same character designs from the character sheet above, especially:
- Mr. Codenstein's wild WHITE hair, thick round glasses, lab coat
- Miss G's translucent ethereal form with flowing hair
- Copilot's rounded robot body with screen face
```

4. **Review generated image for consistency:**
   - ✅ Characters look like same people as character sheet
   - ✅ Hair, glasses, clothing match baseline
   - ✅ Only expressions/poses vary (as intended)

5. **If inconsistent:** Regenerate with explicit notes:
   ```
   The character's face looks different. Please regenerate using 
   the EXACT hair style and facial features from the character sheet.
   ```

6. **Download and save:**
   - File naming: `ch1-goldfish-theory.png`, `ch2-skull-moment.png`, etc.
   - Location: `docs/gh-pages/story/illustrations/images/`

---

### Step 3: Visual QA (Quality Assurance)

After generating all 12 images:

1. **Open all images side-by-side** (use image viewer or browser)

2. **Check character consistency:**
   ```
   ☐ Mr. Codenstein's hair looks same across all images
   ☐ His glasses style is consistent
   ☐ Lab coat appearance matches
   ☐ Miss G's translucent effect is similar
   ☐ Her hair style is consistent
   ☐ Copilot's body design matches
   ```

3. **Identify outliers:**
   - Any image where characters look noticeably different
   - Note specific differences (e.g., "Ch4: hair is curly instead of spiky")

4. **Regenerate outliers** using character sheet + explicit corrections

5. **Repeat QA until all 12 pass consistency check**

---

## 🎨 Generation Order (Recommended)

### Batch 1: Foundation (Generate First)
1. `00-character-sheet.md` - **BASELINE**
2. `00-basement-laboratory.md` - Setting reference
3. `00-coffee-timeline.md` - Visual metaphor

### Batch 2: Story Opening
4. `prologue-deadline.md` - Story opener
5. `ch1-goldfish-theory.md` - Chapter 1
6. `ch2-skull-moment.md` - Chapter 2

### Batch 3: Mid-Story
7. `ch3-backup-chaos.md` - Chapter 3
8. `ch4-agent-chaos.md` - Chapter 4
9. `ch5-graph-overload.md` - Chapter 5
10. `ch6-token-mountain.md` - Chapter 6

### Batch 4: Story Resolution
11. `ch7-capture-moment.md` - Chapter 7
12. `ch8-platform-chaos.md` - Chapter 8
13. `ch9-brute-force.md` - Chapter 9
14. `ch10-personality-emergence.md` - **FINALE**

**Why this order?**
- Character sheet first = baseline established
- Sequential story order = narrative flow
- Finale last = emotional payoff

---

## 🛠️ Troubleshooting

### Problem: Characters look different in each image

**Solution:**
1. Always upload character sheet image when generating
2. Add explicit character description reminder in prompt
3. Reference specific features: "Same spiky white hair as character sheet"

### Problem: DALL-E refuses to generate

**Reason:** Content policy filter triggered

**Solution:**
- Remove any potentially sensitive terms
- Replace "crazy" with "enthusiastic" if needed
- Simplify complex scene descriptions

### Problem: Image quality is poor

**Solution:**
- Add "high resolution, 4K quality, professional illustration" to prompt
- Request "clean line art" and "high contrast"
- Specify "newspaper comic strip aesthetic" for consistent style

### Problem: Wrong aspect ratio

**Solution:**
- Specify dimensions in prompt: "1200x800px landscape format"
- Or: "800x1200px portrait format" for vertical layouts
- DALL-E will approximate these ratios

---

## 📊 Post-Generation Checklist

After all 12 images generated:

```
☐ All 12 PNG files saved to images/ directory
☐ File names match prompt file names
☐ Visual QA passed (characters consistent)
☐ Images optimized (<150KB each)
☐ Alt text written for each image
☐ Images integrated into story page HTML
☐ Story page tested in browser
☐ Mobile responsive check completed
```

---

## 🎯 Quality Standards

### Character Consistency
- Hair style identical across all images
- Facial features recognizable
- Clothing style matches
- Body proportions consistent

### Visual Style
- Black and white cartoon aesthetic
- Clean line art
- High contrast
- Newspaper comic strip feel

### Technical Quality
- Minimum 1200px width
- Sharp, not blurry
- Text (if any) readable
- File size <150KB (after optimization)

---

## 📁 File Organization

```
docs/gh-pages/story/illustrations/
├── prompts/                      # DALL-E prompt files (source)
│   ├── 00-character-sheet.md     # CANONICAL REFERENCE
│   ├── 00-basement-laboratory.md
│   ├── 00-coffee-timeline.md
│   ├── prologue-deadline.md
│   └── ch1-goldfish-theory.md ... ch10-personality-emergence.md
│
└── images/                       # Generated PNG files (output)
    ├── 00-character-sheet.png    # BASELINE
    ├── 00-basement-laboratory.png
    ├── 00-coffee-timeline.png
    ├── prologue-deadline.png
    └── ch1-goldfish-theory.png ... ch10-personality-emergence.png
```

---

## 🚨 Critical Reminders

1. **ALWAYS generate character sheet first** - It's your baseline
2. **ALWAYS upload character sheet when generating subsequent images** - Visual reference
3. **ALWAYS perform visual QA** - Side-by-side comparison catches issues
4. **NEVER accept inconsistent images** - Regenerate until characters match
5. **SAVE all generated images** - Even rejected ones (for comparison)

---

## 📞 Support

**Issues?** Document problems in:
- `cortex-brain/documents/investigations/dalle-generation-issues.md`

**Questions?** Reference:
- Bug fix report: `DALLE-CHARACTER-CONSISTENCY-FIX-2025-12-10.md`
- Enhancement plan: `enterprise-documentation-enhancement-plan.md`

---

**Guide Version:** 1.0  
**Author:** Asif Hussain  
**Last Updated:** December 10, 2025  
**Status:** ✅ Ready for use
