# Story Title Cover Integration
**Date:** December 26, 2025  
**Author:** Asif Hussain  
**Component:** CORTEX Story Viewer

---

## 🎯 Objective

Display the title cover image (`TitleCover.png`) when users first click "The Awakening of CORTEX" on the home page, before any chapter is selected.

---

## ✅ Implementation

### Changes Made

**1. Modified `story-viewer.js` - `init()` function:**
- Changed initialization logic to check for empty hash
- Shows title cover when no hash present (instead of defaulting to prologue)
- Added hashchange handler to return to title when hash is cleared

**2. Added `showTitleCover()` function:**
```javascript
function showTitleCover() {
    // Clears all active chapter states
    // Displays TitleCover.png centered with fade-in animation
    // Adds hover effects and error handling
    // Includes cyan glow shadow for visual impact
}
```

**3. Updated `viewer.html` - Story Header:**
- Made story title and logo clickable
- Links clear the hash to return to title cover
- Added hover effects for visual feedback

---

## 🎨 User Experience

**Flow:**
1. User clicks "The Awakening of CORTEX" → Title cover displays (no chapter selected)
2. User clicks any chapter → Chapter loads with content
3. User clicks story title/logo → Returns to title cover
4. Browser back button → Returns to previous view

**Visual Features:**
- Centered title image with fade-in animation
- Cyan glow shadow matching CORTEX theme
- Responsive sizing (max 85vh, maintains aspect ratio)
- Hover scale effect on logo (1.05x)
- No sidebar selection when on title view

---

## 📁 Files Modified

1. `docs/story/story-viewer.js` (lines 187-207, 220-270)
2. `docs/story/viewer.html` (lines 338-344)

**Image Location:**
- `docs/story/illustrations/images/TitleCover.png` (2.2MB)

---

## 🧪 Testing

**Manual Test Cases:**
- ✅ Load viewer.html directly → Shows title cover
- ✅ Load viewer.html#prologue → Shows prologue chapter
- ✅ Click chapter from title view → Loads chapter correctly
- ✅ Click story title from chapter → Returns to title cover
- ✅ Browser back/forward → Navigation works correctly
- ✅ No chapter selected in sidebar when showing title

---

## 🔄 Integration Notes

**URL Hash Behavior:**
- No hash (`#`) = Title cover view
- `#prologue`, `#chapter-01`, etc. = Chapter view

**Sidebar State:**
- Title view: All chapters inactive (no selection)
- Chapter view: Active chapter highlighted

**Future Enhancements:**
- Could add subtitle/description below title image
- Could add "Begin Reading" button linking to prologue
- Could add story metadata (author, date, chapter count)

---

**Status:** ✅ Complete and tested
