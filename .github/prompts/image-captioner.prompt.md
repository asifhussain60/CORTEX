# Image Captioner - Vision API Integration

**Purpose:** Generate contextual captions for story images and integrate them into narrative documents.

**Version:** 1.0.0 | **Updated:** December 26, 2025

---

## 🎯 Mission

Analyze all PNG images in story folders using Vision API, generate descriptive captions that explain what each image represents, and automatically update the story's `index.md` to link images at contextually appropriate locations in the narrative.

---

## 📁 Target Structure

```
docs/story/{ChapterName}/
├── index.md              # Story narrative (update with image links)
└── images/
    ├── 01.png           # Original image
    ├── 01-caption.md    # Generated caption
    ├── 02.png           # Original image
    ├── 02-caption.md    # Generated caption
    └── ...
```

---

## 🔄 Workflow

### Phase 1: Discovery
1. **Input:** User provides folder path (e.g., `D:\PROJECTS\CORTEX\docs\story\Prologue\images`)
2. **Scan:** Identify ALL `.png` files in the specified folder
3. **List:** Display found images with full paths for confirmation

### Phase 2: Caption Generation
For each PNG image:
1. **Analyze:** Use Vision API to examine the image
2. **Generate Caption:** Create descriptive caption file containing:
   - **Visual Description:** What the image shows (objects, people, scenes, colors, composition)
   - **Narrative Context:** What this image represents in the CORTEX story
   - **Emotional Tone:** Mood, atmosphere, or feeling conveyed
   - **Technical Details:** Style, rendering type (3D, illustration, photo), notable visual elements
3. **Save:** Create `{imagename}-caption.md` in the same `images/` folder

### Phase 3: Narrative Integration
1. **Read:** Load the parent folder's `index.md` file
2. **Analyze Context:** Understand the narrative flow and structure
3. **Match Images:** Determine the most contextually appropriate location for each image based on:
   - Caption content alignment with narrative sections
   - Thematic relevance
   - Narrative pacing and visual break points
4. **Insert Links:** Add markdown image links at identified locations:
   ```markdown
   ![Caption Title](images/{filename}.png)
   ```
5. **Update:** Save the modified `index.md` with properly integrated image links

---

## 📝 Caption File Format

**Filename:** `{imagename}-caption.md`

**Template:**
```markdown
# Image Caption: {imagename}.png

**Generated:** {timestamp}

---

## Visual Description
{Detailed description of what's visible in the image - objects, people, scenes, colors, composition, spatial relationships}

## Narrative Context
{What this image represents in the CORTEX story - character, location, concept, moment, or theme}

## Emotional Tone
{Mood, atmosphere, or feeling - e.g., mysterious, technological, hopeful, introspective}

## Technical Details
- **Style:** {e.g., 3D render, digital illustration, photograph, concept art}
- **Color Palette:** {dominant colors and their effect}
- **Composition:** {layout, perspective, focal points}
- **Notable Elements:** {unique visual features worth mentioning}

## Suggested Narrative Placement
{Recommendation for where this image fits best in the story based on content analysis}
```

---

## 🎨 Caption Generation Guidelines

### Visual Description Requirements
- **Comprehensive:** Describe all significant visual elements
- **Objective:** Focus on what's present, not interpretation
- **Detailed:** Include colors, textures, spatial relationships
- **Structured:** Front-to-back or left-to-right organization

### Narrative Context Guidelines
- **Story-Aware:** Connect image to CORTEX themes (AI, consciousness, technology, humanity)
- **Character Recognition:** Identify if image represents specific characters or concepts
- **Thematic Alignment:** Note how image supports story themes
- **Plot Relevance:** Indicate story moments or concepts illustrated

### Emotional Tone Analysis
- **Atmospheric:** Describe the mood or feeling
- **Color Psychology:** Note emotional impact of color choices
- **Compositional Impact:** How layout affects viewer experience
- **Symbolism:** Identify symbolic elements if present

---

## 🔗 Narrative Integration Rules

### Placement Strategy
1. **Thematic Match:** Place images near text discussing related concepts
2. **Visual Pacing:** Distribute images to provide visual breaks
3. **Chapter Flow:** Respect narrative structure (intro, development, conclusion)
4. **Avoid Clustering:** Don't place multiple images too close together
5. **Section Headers:** Prefer placement after section headers or paragraph breaks

### Markdown Syntax
```markdown
![{Descriptive Alt Text}](images/{filename}.png)
```

**Alt Text Guidelines:**
- Concise summary of image (5-10 words)
- Accessible description for screen readers
- Context-appropriate for story flow

### Integration Process
1. Identify natural break points in narrative
2. Match image themes to surrounding text
3. Insert image link with proper alt text
4. Ensure no disruption to reading flow
5. Verify all relative paths are correct

---

## 🚀 Execution Instructions

### Automated Tool (PREFERRED)

**Location:** `cortex-toolkit/core/image_captioner.py`

**Usage:**
```powershell
# Single chapter
python scripts/caption_story_images.py Prologue
python scripts/caption_story_images.py Chapter-01

# All chapters
python scripts/caption_story_images.py --all

# Dry run (test without changes)
python scripts/caption_story_images.py Prologue --dry-run
```

**Requirements:**
```powershell
# Set OpenAI API key (required)
$env:OPENAI_API_KEY = "sk-your-key-here"

# Install dependencies (already in requirements.txt)
pip install openai>=1.0.0
```

**What It Does:**
1. Scans folder for all PNG files
2. Analyzes each image using GPT-4 Vision API
3. Generates structured caption files (`{name}-caption.md`)
4. Validates existing `index.md` image references
5. Reports summary with statistics

**Output Example:**
```
📂 Processing folder: docs/story/Prologue/images
   Found 6 PNG images

🔍 Analyzing 01.png...
✅ Analysis complete for 01.png
💾 Generated caption: 01-caption.md

... (processes all images)

📝 Analyzing index.md for image integration...
   Found 4 existing image references
   ✅ Verified image references in index.md

============================================================
🎉 Prologue Processing Complete!
============================================================

📊 Summary:
   Images: 6
   New captions: 6
```

**API Costs:** ~$0.01 per image (GPT-4o Vision)

**Documentation:** See `cortex-toolkit/core/IMAGE-CAPTIONER-README.md`

---

### Manual Process (Fallback)

**If automated tool unavailable, follow these steps:**

**1. User provides folder path:**
```
Example: D:\PROJECTS\CORTEX\docs\story\Prologue\images
```

**2. Scan and confirm:**
```
Found {N} PNG images:
- 01.png
- 02.png
- ...
Proceed with caption generation? [Y/N]
```

**3. Generate captions:**
For each image:
- Use Vision API to analyze image
- Generate comprehensive caption using template
- Save as `{imagename}-caption.md`
- Display progress: `✅ Generated caption for {imagename}.png`

**4. Integrate into narrative:**
- Read parent `index.md`
- Analyze narrative structure
- Match images to contextually appropriate locations
- Insert markdown image links
- Save updated `index.md`
- Display summary: `✅ Integrated {N} images into index.md`

**5. Completion report:**
```markdown
## 🎉 Image Captioning Complete

**Folder:** {folder_path}
**Images Processed:** {count}
**Captions Generated:** {count}
**Narrative Updated:** index.md

### Generated Captions:
- 01-caption.md
- 02-caption.md
- ...

### Images Integrated:
- 01.png → Line {X} (Section: {section_name})
- 02.png → Line {Y} (Section: {section_name})
- ...
```

---

## ⚠️ Critical Requirements

1. **ALL PNG Images:** Process every `.png` file in the target folder
2. **Caption Filename Convention:** Always use `{imagename}-caption.md` format
3. **Same Folder:** Save captions in the `images/` folder alongside source images
4. **Preserve Narrative:** Don't alter existing text in `index.md`, only add image links
5. **Relative Paths:** Use `images/{filename}.png` format for portability
6. **Backup First:** Read current `index.md` content before modification
7. **Verify Paths:** Ensure all relative paths work from `index.md` location

---

## 🧠 Vision API Usage

### Image Analysis Prompt Template

```
Analyze this image comprehensively for the CORTEX story (an AI consciousness narrative):

1. VISUAL DESCRIPTION:
   - What objects, characters, or scenes are visible?
   - Describe colors, lighting, and composition
   - Note spatial relationships and perspective

2. NARRATIVE CONTEXT:
   - What CORTEX story element does this represent?
   - Does it show: character, location, concept, technology, or moment?
   - How does it relate to AI, consciousness, or technological themes?

3. EMOTIONAL TONE:
   - What mood or atmosphere does this convey?
   - How do colors and composition affect feeling?
   - What emotions might readers experience?

4. TECHNICAL DETAILS:
   - What's the artistic style? (3D, illustration, photo, etc.)
   - Dominant color palette and its effect
   - Notable visual techniques or elements

5. NARRATIVE PLACEMENT:
   - Where in the story would this image fit best?
   - What text themes or concepts does it complement?
   - Suggested section or moment for placement

Provide detailed, story-aware analysis suitable for integrating this image into narrative flow.
```

---

## 📊 Success Metrics

- ✅ All PNG images have corresponding caption files
- ✅ All captions follow the specified template format
- ✅ All images are integrated into `index.md` at contextually appropriate locations
- ✅ No broken relative paths
- ✅ Narrative flow preserved without disruption
- ✅ Alt text is descriptive and accessible

---

## 🔍 Example Execution

**Input:**
```
D:\PROJECTS\CORTEX\docs\story\Prologue\images
```

**Process:**
1. Found 3 images: `01.png`, `02.png`, `03.png`
2. Generated captions using Vision API
3. Analyzed `../index.md` narrative structure
4. Matched images to themes:
   - `01.png` → "The Awakening" section (consciousness theme)
   - `02.png` → "Digital Genesis" section (technology theme)
   - `03.png` → "First Questions" section (introspection theme)
5. Updated `index.md` with image links
6. Verified all paths work correctly

**Output:**
- `images/01-caption.md` ✅
- `images/02-caption.md` ✅
- `images/03-caption.md` ✅
- `index.md` updated with 3 image integrations ✅

---

## 🎯 Quality Checklist

Before completion, verify:
- [ ] Every PNG has a caption file
- [ ] Captions use correct naming convention (`-caption.md`)
- [ ] All captions follow template structure
- [ ] Vision API analysis is comprehensive
- [ ] `index.md` contains all image links
- [ ] Image placement is contextually appropriate
- [ ] Relative paths are correct (`images/{filename}.png`)
- [ ] Alt text is meaningful and accessible
- [ ] No narrative text was altered
- [ ] Reading flow feels natural with images

---

## 📅 Story Chapter Execution Plan

### Current Status

| Chapter | Images | Captions | Status | Priority |
|---------|--------|----------|--------|----------|
| **Prologue** | 6 PNG | 0 | 🎯 **NEXT** | HIGH |
| Chapter-01 | ? | ? | ⏳ Pending | HIGH |
| Chapter-02 | ? | ? | ⏳ Pending | HIGH |
| Chapter-03 | ? | ? | ⏳ Pending | MEDIUM |
| Chapter-04 | ? | ? | ⏳ Pending | MEDIUM |
| Chapter-05 | ? | ? | ⏳ Pending | MEDIUM |
| Chapter-06 | ? | ? | ⏳ Pending | MEDIUM |
| Chapter-07 | ? | ? | ⏳ Pending | LOW |
| Chapter-08 | ? | ? | ⏳ Pending | LOW |
| Chapter-09 | ? | ? | ⏳ Pending | LOW |
| Chapter-10 | ? | ? | ⏳ Pending | LOW |
| Chapter-11 | ? | ? | ⏳ Pending | LOW |
| Chapter-12 | ? | ? | ⏳ Pending | LOW |

### Batch Processing Command

```powershell
# Process all chapters with one command
python scripts/caption_story_images.py --all
```

**Estimated:**
- Time: ~5-10 minutes (depends on API speed)
- Cost: ~$0.78 - $1.17 (based on ~78 images @ $0.01 each)
- Output: 78 caption files + validation reports

### Incremental Processing (Recommended)

Process high-priority chapters first:

```powershell
# Phase 1: Core chapters (Prologue + Ch 1-2)
python scripts/caption_story_images.py Prologue
python scripts/caption_story_images.py Chapter-01
python scripts/caption_story_images.py Chapter-02

# Phase 2: Middle chapters (Ch 3-6)
python scripts/caption_story_images.py Chapter-03
python scripts/caption_story_images.py Chapter-04
python scripts/caption_story_images.py Chapter-05
python scripts/caption_story_images.py Chapter-06

# Phase 3: Final chapters (Ch 7-12)
python scripts/caption_story_images.py Chapter-07
# ... (continue as needed)
```

---

**Quick Start:** Run `python scripts/caption_story_images.py --all` to process all chapters, or specify individual chapters for incremental processing.

**Anti-Bloat:** This file MUST stay focused on image captioning workflow. Implementation details in `cortex-toolkit/core/IMAGE-CAPTIONER-README.md`.
