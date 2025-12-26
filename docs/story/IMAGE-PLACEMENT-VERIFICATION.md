# Image Placement Verification Guide

**Purpose:** Verify contextual image placement across all 13 chapters

**Algorithm:** Section-aware distribution with minimum 2-section gap between images

---

## ✅ Verification Checklist

### Core Requirements
- [ ] **No side-by-side images** - Minimum 2 sections between any two images
- [ ] **Contextual placement** - Images appear AFTER section heading + 1-2 paragraphs
- [ ] **Even distribution** - Images spread throughout chapter narrative
- [ ] **Text wrapping** - Images float left/right with proper text flow

---

## 📋 Chapter-by-Chapter Testing

### Prologue (2 images)
- **Expected:** Images at sections 2 and 4 (of ~6 total sections)
- **Placement:** Image 1 right-float, Image 2 left-float
- **Context:** Each image should appear within relevant narrative section
- [ ] No side-by-side images
- [ ] Images appear contextually within sections
- [ ] Text wraps around images properly

### Chapter 1 (3 images)
- **Expected:** Images distributed with 2+ section gaps
- **Placement:** Image 1 left, Image 2 right, Image 3 left
- **Context:** Each image within narrative discussing that visual concept
- [ ] Minimum 2 sections between images
- [ ] All 3 images visible and contextual
- [ ] Alternating float positions working

### Chapter 2 (2 images)
- **Expected:** Images at sections ~2 and ~5 (of ~7 sections)
- **Placement:** Image 1 right, Image 2 left
- [ ] No side-by-side images
- [ ] Images contextually relevant to surrounding text

### Chapter 3 (1 image)
- **Expected:** Single image near middle section
- **Placement:** Left-float
- [ ] Image appears in contextually relevant section
- [ ] Text wraps properly around single image

### Chapter 4 (0 images)
- **Expected:** No images
- [ ] Confirmed no images in chapter

### Chapter 5 (1 image)
- **Expected:** Single image near middle section
- **Placement:** Right-float
- [ ] Image contextually placed
- [ ] Text wrapping works

### Chapter 6 (1 image)
- **Expected:** Single image near middle section
- **Placement:** Left-float
- [ ] Image contextually placed

### Chapter 7 (2 images)
- **Expected:** Images distributed with 2+ section gaps
- **Placement:** Image 1 right, Image 2 left
- [ ] No side-by-side images
- [ ] Contextual placement

### Chapter 8 (2 images)
- **Expected:** Images distributed with 2+ section gaps
- **Placement:** Image 1 left, Image 2 right
- [ ] No side-by-side images
- [ ] Contextual placement

### Chapter 9 (1 image)
- **Expected:** Single image near middle section
- **Placement:** Right-float
- [ ] Image contextually placed

### Chapter 10 (2 images)
- **Expected:** Images distributed with 2+ section gaps
- **Placement:** Image 1 left, Image 2 right
- [ ] No side-by-side images
- [ ] Contextual placement

### Chapter 11 (2 images)
- **Expected:** Images distributed with 2+ section gaps
- **Placement:** Image 1 right, Image 2 left
- [ ] No side-by-side images
- [ ] Contextual placement

### Chapter 12 (1 image)
- **Expected:** Single image near middle section
- **Placement:** Left-float
- [ ] Image contextually placed

---

## 🔍 Algorithm Details

**Section-Aware Distribution:**
```javascript
// Calculate placement points
function calculateImagePlacement(totalSections, imageCount) {
    // Single image → middle section
    if (imageCount === 1) return [Math.floor(totalSections / 2)];
    
    // Multiple images → even distribution with minGap = 2
    const step = Math.max(3, Math.floor(totalSections / (imageCount + 1)));
    
    // Returns array of section indices where images should appear
}
```

**Placement Logic:**
1. First pass: Count sections and paragraphs
2. Calculate optimal section indices (minimum 2-section gap)
3. Second pass: Render HTML, insert images after 2nd paragraph in designated sections
4. Result: Contextual placement with proper spacing

---

## 🧪 Testing Commands

```bash
# Start server
./scripts/launch_docs.sh

# Test URL
http://localhost:8000/story/viewer.html

# Verify paths
python3 docs/story/tests/test_paths.py
```

---

## 📊 Success Criteria

✅ **All 19 images load successfully**
✅ **No two images appear side-by-side in any chapter**
✅ **Images appear contextually within relevant narrative sections**
✅ **Text wraps properly around all floating images**
✅ **Responsive: Images stack properly on mobile (<768px)**

---

**Last Updated:** December 26, 2025  
**Author:** Asif Hussain
