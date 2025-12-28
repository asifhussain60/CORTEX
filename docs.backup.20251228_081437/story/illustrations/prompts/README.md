# CORTEX Story Illustration Prompts - Organization Guide

**Last Updated:** December 11, 2025  
**Total Prompts:** 19 (12 Essential + 7 Valuable)

---

## 📁 Directory Structure

```
prompts/
├── essential/              # Priority 1: Generate these first (12 prompts)
├── valuable/               # Priority 2: Optional enhancements (7 prompts)
├── metadata/               # Reserved for JSON exports
├── ILLUSTRATION-CATALOG.md # Complete reference
└── README.md              # This file
```

---

## 🎯 Image Placement Strategy

**CRITICAL:** All generated images go to the same location regardless of prompt tier:

```
docs/story/illustrations/images/
```

### Why Single Location?

✅ **Consistent References:** Story content uses one path format
```markdown
![Title](illustrations/images/cortex-awakening-ch01-01.png)
```

✅ **No Conditional Logic:** Module 9B validator checks one location

✅ **Easy Expansion:** Add "valuable" images later without refactoring references

✅ **Clean Git History:** No "moved images" commits

---

## 📋 Essential Tier (12 Prompts)

**Generate These First** - Core story + all MAJOR features

### Coverage:
- **Prologue:** 2 prompts (basement lab, G appears)
- **Chapter 1:** 2 prompts (coffee timeline, goldfish theory)
- **Chapter 2:** 2 prompts (almost-disaster, SKULL rules)
- **Chapter 3:** 1 prompt (laptop crash)
- **Chapter 7:** 1 prompt (TDD cycle - MAJOR feature)
- **Chapter 8:** 1 prompt (cross-platform chaos)
- **Chapter 9:** 1 prompt (maintenance orchestrator - MAJOR feature)
- **Chapter 10:** 1 prompt (personality emergence)
- **Epilogue:** 1 prompt (resolution)

### File List:
```
essential/
├── cortex-awakening-prologue-01.txt
├── cortex-awakening-prologue-02.txt
├── cortex-awakening-ch01-01.txt
├── cortex-awakening-ch01-03.txt
├── cortex-awakening-ch02-01.txt
├── cortex-awakening-ch02-02.txt
├── cortex-awakening-ch03-01.txt
├── cortex-awakening-ch07-01.txt
├── cortex-awakening-ch08-01.txt
├── cortex-awakening-ch09-01.txt
├── cortex-awakening-ch10-01.txt
└── cortex-awakening-epilogue-01.txt
```

### Estimated Cost:
- **DALL-E 3:** ~$18-24 (12 images)
- **Time:** ~3 hours (15 min/image avg)

---

## 📦 Valuable Tier (7 Prompts)

**Generate If Budget Allows** - Enhanced depth + additional moments

### Coverage:
- **Chapter 1:** 1 prompt (Copilot amnesia - reinforces problem)
- **Chapter 5:** 1 prompt (knowledge graph epiphany)
- **Chapter 6:** 1 prompt (token mountain)
- **Chapter 7:** 1 prompt (test coverage validation)
- **Chapter 9:** 1 prompt (auto-fix success)
- **Chapter 11:** 2 prompts (documentation + Planning System 2.0)

### File List:
```
valuable/
├── cortex-awakening-ch01-02.txt
├── cortex-awakening-ch05-01.txt
├── cortex-awakening-ch06-01.txt
├── cortex-awakening-ch07-02.txt
├── cortex-awakening-ch09-02.txt
├── cortex-awakening-ch11-01.txt
└── cortex-awakening-ch11-02.txt
```

### Estimated Cost:
- **DALL-E 3:** ~$10-14 (7 images)
- **Time:** ~2 hours (15 min/image avg)

---

## 🚀 Generation Workflow

### Phase 1: Essential Tier
1. Open prompt file from `essential/`
2. Copy "DALL-E 3 PROMPT" section
3. Paste into DALL-E 3 interface
4. Generate (may need 2-3 attempts for quality)
5. Save as **exact filename** from prompt
6. Place in `docs/story/illustrations/images/`
7. Repeat for all 12 essential prompts

### Phase 2: Valuable Tier (Optional)
1. Review story with essential images
2. Identify which valuable prompts add most value
3. Follow same workflow from `valuable/` folder
4. Images go to same location: `docs/story/illustrations/images/`

---

## 📊 Quality Standards

All prompts (both tiers) include:

✅ **Narrative Anchor:** Exact text phrase for injection point  
✅ **Visual Elements:** 5-8 specific components  
✅ **Mood Guidance:** Artistic direction  
✅ **Placement Type:** chapter_opening, key_moment, technical_diagram, etc.  
✅ **Style Guide:** Unified tech comedy aesthetic  
✅ **Technical Notes:** 1024x1024, 1:1 aspect ratio, RGB color

---

## 🎨 Filename Convention

**Format:** `cortex-awakening-{chapter}-{sequence}.png`

**Examples:**
- `cortex-awakening-prologue-01.png`
- `cortex-awakening-ch01-01.png`
- `cortex-awakening-ch07-01.png`
- `cortex-awakening-epilogue-01.png`

**Rules:**
- Chapter format: `prologue`, `ch01`-`ch11`, `epilogue`
- Sequence: `01`, `02`, `03` (within chapter)
- Always lowercase
- Always `.png` extension

---

## 🔍 Next Steps

### Immediate:
- [ ] Review all essential prompts for quality
- [ ] Generate 12 essential images via DALL-E 3
- [ ] Place images in `docs/story/illustrations/images/`
- [ ] Run Module 9B to validate image references

### Optional:
- [ ] Decide which valuable prompts to generate
- [ ] Generate valuable images (same location)
- [ ] Re-run Module 9B validation

### Phase 2:
- [ ] Module 3 Content Generator references known filenames
- [ ] Story updates with image markdown at narrative anchors
- [ ] Deploy complete visual story

---

## 💡 Tips

**Cost Optimization:**
- Start with essential tier only
- Gather reader feedback
- Add valuable images based on demand

**Quality Control:**
- Generate 2-3 variations per prompt
- Select best quality/style match
- Keep consistent naming

**Time Management:**
- Batch process prompts by type (diagrams together, scenes together)
- Take breaks between batches for fresh perspective
- Review all images together for consistency

---

**Questions?** Check `ILLUSTRATION-CATALOG.md` for complete filename reference.

**Author:** Asif Hussain  
**Copyright © 2025 Asif Hussain. All rights reserved.**
