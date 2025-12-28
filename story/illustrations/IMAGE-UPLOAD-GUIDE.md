# Story Page Image Integration Guide

**Created:** December 10, 2025  
**Purpose:** Instructions for uploading comic illustrations to complete story page

---

## 📸 Image Upload Instructions

### Image Locations

**Comic Illustrations (12 images):**
- **Upload to:** `docs/gh-pages/story/illustrations/images/`
- **Naming convention:** Match the prompt filenames (see below)

### Required Images (12 total)

Upload these PNG files generated from DALL-E 3 prompts:

1. `00-character-sheet.png` - Character design reference
2. `01-prologue.png` - Basement laboratory scene
3. `02-chapter-1.png` - The Goldfish Theory moment
4. `03-chapter-2.png` - Brain Protector SKULL rules
5. `04-chapter-3.png` - SQLite intervention
6. `05-chapter-4.png` - Agent uprising coordination chaos
7. `06-chapter-5.png` - Knowledge graph incident
8. `07-chapter-6.png` - Token crisis optimization
9. `08-chapter-7.png` - Hebb's Law revelation
10. `09-chapter-8.png` - Response template evolution
11. `10-chapter-9.png` - Cross-platform challenge
12. `11-chapter-10.png` - The Awakening moment

### Image Specifications

- **Format:** PNG (generated from DALL-E 3)
- **Style:** Black & white newspaper cartoon aesthetic
- **Dimensions:** 
  - Standard: 1200×800px (landscape)
  - Timeline: 1600×600px (extra wide)
  - Character sheet: 800×1200px (portrait)
- **Characters:** Einstein professor, ethereal muse, friendly robot (see prompts for details)

### Placeholder System

**Current state:** Story page uses placeholder images
- **Placeholder file:** `docs/gh-pages/assets/images/placeholder-comic.svg`
- **Fallback behavior:** `onerror="this.src='../assets/images/placeholder-comic.png'"`

**After upload:**
- Images automatically replace placeholders
- No code changes needed
- Story page will render comic illustrations at chapter tops

### Testing After Upload

1. **Local preview:**
   ```bash
   cd docs/gh-pages
   python3 -m http.server 8000
   open http://localhost:8000/story/index.html
   ```

2. **Check images load:**
   - Open browser DevTools Console
   - Look for "Image loaded successfully" messages
   - Verify no 404 errors for illustration files

3. **Verify fallback:**
   - Temporarily rename an image to test fallback
   - Should show placeholder instead of broken image

### Image Optimization (Optional)

After uploading PNGs, consider converting to WebP for better performance:

```bash
cd docs/gh-pages/story/illustrations/images
for file in *.png; do
  cwebp -q 80 "$file" -o "${file%.png}.webp"
done
```

Then update HTML `<img>` tags to use WebP with PNG fallback:
```html
<picture>
  <source srcset="illustrations/images/01-prologue.webp" type="image/webp">
  <img src="illustrations/images/01-prologue.png" alt="...">
</picture>
```

---

## 🎨 Dual Image System Architecture

### System 1: Technical Diagrams (EXISTING)
- **Location:** `cortex-brain/documents/analysis/dalle-prompts/cortex-brain/`
- **Purpose:** Education (architecture/feature documentation)
- **Usage:** GitHub Pages feature/architecture pages
- **Style:** Professional presentation format
- **Count:** 10 images

### System 2: Comic Illustrations (NEW - THIS FOLDER)
- **Location:** `docs/gh-pages/story/illustrations/`
- **Purpose:** Entertainment (story humor/character moments)
- **Usage:** Story page ONLY (`docs/gh-pages/story/index.html`)
- **Style:** Black & white newspaper cartoons
- **Count:** 12 images

**IMPORTANT:** These two image systems are SEPARATE and serve different purposes:
- **Technical diagrams** = Educational callouts within story text
- **Comic illustrations** = Entertainment at chapter tops

---

## 📝 Story Page Status

**HTML:** ✅ Complete with image placeholders  
**CSS:** ✅ Complete with glassmorphism design  
**JavaScript:** ✅ Complete with reading progress, chapter navigation  
**Images:** ⏳ Awaiting upload (placeholders active)

**Next steps:**
1. Generate 12 images with DALL-E 3 (use prompts in `prompts/` folder)
2. Upload to `images/` folder (this location)
3. Test story page locally
4. Verify images display correctly
5. (Optional) Optimize with WebP conversion

---

## 🔍 Verification Checklist

After uploading images:

- [ ] All 12 images uploaded to `docs/gh-pages/story/illustrations/images/`
- [ ] Filenames match expected names (00-character-sheet.png, etc.)
- [ ] Images display on story page (no placeholder SVG)
- [ ] Character consistency maintained across all images
- [ ] Black & white cartoon style matches specification
- [ ] No broken images or 404 errors in console
- [ ] Reading progress bar works
- [ ] Chapter navigation highlights active chapter
- [ ] Table of contents links scroll to correct sections
- [ ] Mobile responsive (test at 768px width)

---

## 📞 Support

If images don't display after upload:
1. Check filename spelling (case-sensitive)
2. Clear browser cache (Cmd+Shift+R / Ctrl+Shift+R)
3. Verify file permissions (readable)
4. Check browser console for errors
5. Test in different browser

**Status:** Ready for image upload. Story page will automatically render images once uploaded.
