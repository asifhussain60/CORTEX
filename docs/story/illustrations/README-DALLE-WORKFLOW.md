# DALL-E Image Generation Workflow

**Purpose:** Guidelines for generating and optimizing images for "The Awakening of CORTEX" story  
**Two Distinct Systems:** Comic Illustrations + Technical Diagrams  
**Last Updated:** December 10, 2025

---

## 🎨 System 1: Comic Illustrations

### Purpose
Black & white cartoons for story humor and character moments (newspaper comic strip aesthetic)

### Location
- **Prompts:** `docs/story/illustrations/prompts/` (14 files)
- **Images:** `docs/story/illustrations/images/` (PNG/WebP)

### Generation Process

**Step 1: Review Prompts**
```bash
cd docs/story/illustrations/prompts/
ls -la
```

Files include:
- `00-character-sheet.md` - Character reference (GENERATE FIRST)
- `00-basement-laboratory.md` - Setting establishment
- `00-coffee-timeline.md` - Visual metaphor guide
- `prologue-deadline.md` through `ch10-personality-emergence.md`

**Step 2: Generate with DALL-E 3**
1. Open each `.md` file
2. Copy prompt text to DALL-E 3 (ChatGPT Plus or API)
3. Use exact prompt text (optimized for consistency)
4. Save as `[filename].png` in `docs/story/illustrations/images/`
5. **CRITICAL:** Generate `00-character-sheet.png` FIRST for consistent character appearance

**Step 3: Quality Check**
- ✅ Black & white aesthetic (newspaper comic strip)
- ✅ Characters match reference sheet (Mr. Codenstein, Miss G, Copilot)
- ✅ Clean lines, good contrast
- ✅ Visible at multiple sizes (800px to 1200px wide)

**Step 4: Optimize for Web**
```bash
# Install tools (if not already installed)
npm install -g sharp-cli

# Convert to WebP (better compression)
sharp -i ch1-goldfish-theory.png -o ch1-goldfish-theory.webp -f webp -q 85

# Resize if needed (max 1200px width)
sharp -i source.png -o optimized.webp --resize 1200 --withoutEnlargement -f webp -q 85
```

**Target Specs:**
- Format: WebP (fallback: PNG)
- Max width: 1200px
- Max filesize: 100KB
- Quality: 85%

---

## 📊 System 2: Technical Diagrams

### Purpose
Professional presentation-style diagrams for educational callouts within story

### Location
- **Prompts:** `cortex-brain/documents/analysis/dalle-prompts/cortex-brain/`
- **Images:** Copy generated images to `docs/story/technical-diagrams/`

### Generation Process

**Step 1: Review Existing Prompts**
```bash
cd cortex-brain/documents/analysis/dalle-prompts/cortex-brain/prompts/
ls -la
```

Files include:
- `01-four-tier-architecture.md`
- `02-skull-protection.md`
- `03-agent-system.md`
- `06-working-memory.md`
- `07-knowledge-graph.md`
- And more...

**Step 2: Generate with DALL-E 3**
1. Open each `.md` file in `prompts/` directory
2. Copy prompt text to DALL-E 3
3. Save as `[number]-[name].png` in matching `narratives/` folder
4. **Style:** Professional presentation diagram (polished, corporate, metrics visible)

**Step 3: Copy to Story Directory**
```bash
# Copy relevant technical diagrams
cp cortex-brain/documents/analysis/dalle-prompts/cortex-brain/narratives/*.png docs/story/technical-diagrams/
```

**Step 4: Optimize for Web**
```bash
# Convert to WebP
sharp -i 06-working-memory.png -o 06-working-memory.webp --resize 1400 -f webp -q 90
```

**Target Specs:**
- Format: WebP (fallback: PNG)
- Max width: 1400px
- Max filesize: 150KB
- Quality: 90% (higher for technical clarity)

---

## 🔗 Integration in Story HTML

### Comic Illustrations (Chapter Openers)
```html
<div class="chapter-image-comic">
    <img src="illustrations/images/ch1-goldfish-theory.webp" 
         alt="Copilot forgetting conversations like a goldfish"
         loading="lazy"
         onerror="this.src='../assets/images/placeholder-comic.png'">
    <p class="image-caption-comic">The amnesia crisis that started everything</p>
</div>
```

### Technical Diagrams (Educational Callouts)
```html
<div class="technical-callout">
    <h3>🧠 Technical Concept: Working Memory</h3>
    <img src="technical-diagrams/06-working-memory.webp"
         alt="CORTEX Working Memory Architecture"
         loading="lazy"
         onerror="this.src='../assets/images/placeholder-technical.png'">
    <p><strong>Teaches:</strong> Persistence over elegance. The 70-conversation FIFO queue 
       that solved Copilot's amnesia crisis. SQLite database instead of in-memory storage 
       ensures nothing is lost.</p>
    <a href="../architecture/working-memory.html">Explore Tier 1 Architecture →</a>
</div>
```

---

## 🎯 Chapter-to-Image Mapping

| Chapter | Comic Illustration | Technical Diagram | Teaches |
|---------|-------------------|-------------------|---------|
| Prologue | `01-prologue.png` | None | Setting the scene |
| Chapter 1 | `ch1-goldfish-theory.png` | `06-working-memory.webp` | Memory persistence |
| Chapter 2 | `ch2-skull-moment.png` | `02-skull-protection.webp` + `09-protection-layers.webp` | Safety-first architecture |
| Chapter 3 | `ch3-backup-chaos.png` | `06-working-memory.webp` | Reliability > elegance |
| Chapter 4 | `ch4-agent-chaos.png` | `03-agent-system.webp` | Multi-agent coordination |
| Chapter 5 | `ch5-graph-overload.png` | `07-knowledge-graph.webp` | Relationship modeling |
| Chapter 6 | `ch6-token-mountain.png` | `05-orchestrator-ecosystem.webp` | Optimization strategies |
| Chapter 7 | `ch7-capture-moment.png` | `06-working-memory.webp` | User-centered design |
| Chapter 8 | `ch8-platform-chaos.png` | `08-development-context.webp` | Portable architecture |
| Chapter 9 | `ch9-brute-force.png` | `08-development-context.webp` | Performance optimization |
| Chapter 10 | `ch10-personality-emergence.png` | `10-complete-system.webp` | System integration |

---

##  Naming Conventions

### Comic Illustrations
```
Format: [chapter]-[short-description].webp
Examples:
- ch1-goldfish-theory.webp
- ch2-skull-moment.webp
- ch10-personality-emergence.webp
```

### Technical Diagrams
```
Format: [number]-[component-name].webp
Examples:
- 06-working-memory.webp
- 02-skull-protection.webp
- 10-complete-system.webp
```

### Character References
```
Format: 00-[type].webp
Examples:
- 00-character-sheet.webp
- 00-basement-laboratory.webp
- 00-coffee-timeline.webp
```

---

## 🚀 Bulk Generation Script

```bash
#!/bin/bash
# generate-story-images.sh

# Set directories
COMIC_PROMPTS="docs/story/illustrations/prompts"
COMIC_IMAGES="docs/story/illustrations/images"
TECH_PROMPTS="cortex-brain/documents/analysis/dalle-prompts/cortex-brain/prompts"
TECH_IMAGES="docs/story/technical-diagrams"

# Create output directories
mkdir -p "$COMIC_IMAGES"
mkdir -p "$TECH_IMAGES"

echo "🎨 DALL-E Image Generation Workflow"
echo "===================================="
echo ""
echo "1. Comic Illustrations: $COMIC_PROMPTS"
echo "   → Generate 14 black & white cartoons"
echo "   → Save to $COMIC_IMAGES"
echo ""
echo "2. Technical Diagrams: $TECH_PROMPTS"
echo "   → Generate 10 presentation diagrams"
echo "   → Save to $TECH_IMAGES"
echo ""
echo "⚠️  MANUAL STEP REQUIRED:"
echo "   Copy each prompt to DALL-E 3 (ChatGPT Plus or API)"
echo "   Save generated images with matching filenames"
echo ""
echo "3. Optimization (after generation):"
echo "   → Run: npm install -g sharp-cli"
echo "   → Run: ./optimize-story-images.sh"
```

---

## 🔧 Optimization Script

```bash
#!/bin/bash
# optimize-story-images.sh

# Comic illustrations (max 100KB, 1200px wide)
for file in docs/story/illustrations/images/*.png; do
    filename=$(basename "$file" .png)
    sharp -i "$file" -o "docs/story/illustrations/images/${filename}.webp" \
          --resize 1200 --withoutEnlargement -f webp -q 85
    echo "✅ Optimized: ${filename}.webp"
done

# Technical diagrams (max 150KB, 1400px wide)
for file in docs/story/technical-diagrams/*.png; do
    filename=$(basename "$file" .png)
    sharp -i "$file" -o "docs/story/technical-diagrams/${filename}.webp" \
          --resize 1400 --withoutEnlargement -f webp -q 90
    echo "✅ Optimized: ${filename}.webp"
done

echo "🎉 Optimization complete!"
```

---

## 📋 Quality Checklist

Before marking images as complete, verify:

### Comic Illustrations
- [ ] All 14 prompts generated (00-character-sheet through ch10-personality-emergence)
- [ ] Black & white newspaper comic aesthetic
- [ ] Characters consistent with reference sheet
- [ ] Clean lines, good contrast
- [ ] Optimized to WebP < 100KB
- [ ] Integrated in story HTML with proper alt text

### Technical Diagrams
- [ ] All 10 diagrams generated (01-four-tier through 10-complete-system)
- [ ] Professional presentation style
- [ ] Metrics clearly visible
- [ ] Architecture components labeled
- [ ] Optimized to WebP < 150KB
- [ ] Integrated in technical callouts with educational text

### Integration
- [ ] Comic images appear at chapter tops
- [ ] Technical diagrams appear in callouts within text
- [ ] Lazy loading enabled (`loading="lazy"`)
- [ ] Error fallbacks working (`onerror` handlers)
- [ ] Alt text descriptive and accurate
- [ ] Captions explain what readers are seeing

---

## 🎯 Next Steps

1. **Generate Character Sheet FIRST** (`00-character-sheet.png`)
2. **Generate Foundation Images** (basement lab, coffee timeline)
3. **Generate Chapter Comics** (prologue through ch10)
4. **Generate Technical Diagrams** (from cortex-brain prompts)
5. **Optimize All Images** (WebP conversion, size targets)
6. **Integrate & Test** (verify loading, fallbacks, mobile responsive)

**Estimated Time:** 3-4 hours for complete generation + optimization
