# Story Navigation Testing Guide

**Date:** December 10, 2025  
**Feature:** Chapter Navigation Buttons (Previous/Next)  
**Status:** Ready for Testing

---

## 🧪 Quick Test Instructions

### Prerequisites
- Local HTTP server running
- Modern browser (Chrome, Firefox, Safari, Edge)
- JavaScript enabled

### Start Local Server

```bash
cd /Users/asifhussain/PROJECTS/CORTEX/docs/gh-pages
python3 -m http.server 8000
```

Then open: **http://localhost:8000/story/index.html**

---

## ✅ Test Cases

### Test 1: Prologue Navigation (First Chapter)
**Steps:**
1. Scroll to bottom of Prologue
2. Verify navigation buttons container appears
3. Verify ONLY "Next" button is visible
4. Check button shows "Chapter 1: The Goldfish Theory"

**Expected Result:**
- ✅ Container with glassmorphism background
- ✅ Only "Next Chapter" button (right-aligned)
- ✅ Button has → arrow
- ✅ Hover shows cyan glow effect

**Click Test:**
5. Click "Next" button
6. Page should smooth scroll to Chapter 1

**Expected Result:**
- ✅ Smooth scroll animation (not instant jump)
- ✅ Chapter 1 appears at top of viewport (with ~100px offset)

---

### Test 2: Middle Chapter Navigation (Chapter 4)
**Steps:**
1. Scroll to bottom of Chapter 4
2. Verify navigation buttons container appears
3. Verify BOTH "Previous" and "Next" buttons visible

**Expected Result:**
- ✅ "Previous" button on left with ← arrow
- ✅ "Next" button on right with → arrow
- ✅ Previous shows "Chapter 3: The SQLite Intervention"
- ✅ Next shows "Chapter 5: The Knowledge Graph Incident"

**Click Test:**
4. Click "Previous" button → should scroll to Chapter 3
5. Scroll back to Chapter 4
6. Click "Next" button → should scroll to Chapter 5

**Expected Result:**
- ✅ Both directions work correctly
- ✅ Smooth scroll in both directions

---

### Test 3: Epilogue Navigation (Last Chapter)
**Steps:**
1. Scroll to bottom of Epilogue
2. Verify navigation buttons container appears
3. Verify ONLY "Previous" button is visible
4. Check button shows "Chapter 11: The 3.0 Revolution"

**Expected Result:**
- ✅ Container with glassmorphism background
- ✅ Only "Previous Chapter" button (left-aligned)
- ✅ Button has ← arrow
- ✅ Hover shows cyan glow effect

**Click Test:**
5. Click "Previous" button
6. Page should smooth scroll to Chapter 11

---

### Test 4: Hover Effects
**Steps:**
1. Navigate to any chapter's navigation buttons
2. Hover mouse over "Previous" button
3. Hover mouse over "Next" button

**Expected Result:**
- ✅ Button background brightens (cyan gradient intensifies)
- ✅ Button border becomes more visible
- ✅ Button lifts 2px (translateY effect)
- ✅ Cyan glow shadow appears
- ✅ Transition is smooth (0.3s)

---

### Test 5: Mobile Responsive (< 768px)
**Steps:**
1. Open browser DevTools (F12)
2. Toggle device emulation
3. Set viewport to iPhone 14 (390px width)
4. Scroll to any chapter's navigation buttons

**Expected Result:**
- ✅ Navigation container stacks vertically
- ✅ Buttons are full-width
- ✅ Text is centered in buttons
- ✅ Both buttons visible (if middle chapter)
- ✅ Proper spacing between buttons

---

### Test 6: TOC Integration
**Steps:**
1. Use TOC sidebar to jump to Chapter 7
2. Scroll to bottom of Chapter 7
3. Click "Next" button to go to Chapter 8
4. Verify TOC sidebar updates to highlight Chapter 8

**Expected Result:**
- ✅ TOC active highlight updates correctly
- ✅ Reading progress bar updates
- ✅ Navigation works seamlessly with TOC

---

### Test 7: Print View
**Steps:**
1. Open story page
2. Open Print Preview (Ctrl/Cmd + P)

**Expected Result:**
- ✅ Navigation buttons are hidden in print view
- ✅ Chapter content flows cleanly without nav buttons
- ✅ Print layout is clean

---

### Test 8: Accessibility
**Steps:**
1. Navigate to story page
2. Press Tab key repeatedly to cycle through elements
3. Tab until you reach a navigation button
4. Press Enter while button is focused

**Expected Result:**
- ✅ Buttons are keyboard-navigable
- ✅ Focus indicator visible (hover state)
- ✅ Enter key triggers navigation
- ✅ Screen reader announces button text correctly

---

### Test 9: All Chapters Coverage
**Steps:**
1. Start at Prologue
2. Click "Next" button 13 times (through all chapters to Epilogue)
3. Click "Previous" button 13 times (back to Prologue)

**Expected Result:**
- ✅ All 13 chapters have navigation buttons
- ✅ Prologue has only "Next"
- ✅ Chapters 1-11 have both buttons
- ✅ Epilogue has only "Previous"
- ✅ All chapter titles display correctly
- ✅ No broken links or missing buttons

---

### Test 10: JavaScript Console
**Steps:**
1. Open browser DevTools (F12)
2. Go to Console tab
3. Reload story page
4. Check for errors

**Expected Result:**
- ✅ "Story page initialized successfully" message appears
- ✅ No JavaScript errors
- ✅ No 404 errors for missing files

---

## 🐛 Known Issues Checklist

Run through these common problems:

- [ ] Buttons not appearing → Check JavaScript console for errors
- [ ] Hover effects not working → Check CSS loaded correctly
- [ ] Smooth scroll jumpy → Check `scroll-behavior` CSS property
- [ ] Mobile layout broken → Check viewport meta tag
- [ ] TOC not updating → Check `updateActiveChapter()` function
- [ ] Print shows nav buttons → Check print media query

---

## 📊 Performance Check

**Metrics to Verify:**
- [ ] Page load time < 2 seconds (with placeholders)
- [ ] Smooth scroll animation 60fps
- [ ] No layout shift when navigation buttons appear
- [ ] Hover effects smooth (no lag)
- [ ] Mobile scroll performance good

---

## 🎨 Visual Inspection

**Design Consistency:**
- [ ] Glassmorphism matches site theme
- [ ] Cyan color matches other interactive elements
- [ ] Typography matches story content
- [ ] Button sizing appropriate (not too large/small)
- [ ] Spacing consistent with story layout
- [ ] Mobile buttons comfortable to tap (min 44px height)

---

## ✅ Acceptance Criteria Summary

**Must Pass:**
1. ✅ Navigation buttons appear at end of every chapter
2. ✅ Contextual display (Prologue: Next only, Epilogue: Previous only)
3. ✅ Smooth scroll works with correct offset
4. ✅ Hover effects display correctly
5. ✅ Mobile responsive layout works
6. ✅ Print view hides buttons
7. ✅ Keyboard accessible
8. ✅ No JavaScript errors
9. ✅ TOC integration seamless
10. ✅ All chapter titles correct

**Nice to Have:**
- [ ] Animation timing feels natural
- [ ] Button sizing optimal for usability
- [ ] Color contrast sufficient for accessibility
- [ ] Performance on slower devices acceptable

---

## 🚀 Sign-Off

**Tester Name:** _________________  
**Date:** _________________  
**Browser(s) Tested:** _________________  
**Device(s) Tested:** _________________  

**Overall Assessment:**
- [ ] ✅ PASS - Ready for production
- [ ] ⚠️ PASS WITH NOTES - Minor issues (document below)
- [ ] ❌ FAIL - Needs fixes (document below)

**Notes:**
_____________________________________________
_____________________________________________
_____________________________________________

---

## 📝 Bug Report Template

If issues found, use this format:

**Issue #:** ___  
**Severity:** Critical / High / Medium / Low  
**Browser:** ___  
**Device:** ___  
**Steps to Reproduce:**
1. 
2. 
3. 

**Expected Result:** ___  
**Actual Result:** ___  
**Screenshot:** (if applicable)  
**Console Errors:** (if any)

---

**Testing Status:** Ready for QA  
**Estimated Test Time:** 15-20 minutes
