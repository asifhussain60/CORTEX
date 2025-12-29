# Story Viewer Testing Checklist

**Before Git Pages Publication**

## Local Testing

### Desktop (Chrome/Safari/Firefox)
- [ ] Open `docs/story/viewer.html` locally
- [ ] Verify CORTEX logo (200x200px) displays in sidebar
- [ ] Verify Prologue loads by default
- [ ] Verify Prologue is highlighted in sidebar
- [ ] Click each chapter link (1-12) and verify:
  - [ ] Chapter content loads
  - [ ] Active state updates in sidebar
  - [ ] URL hash updates (#chapter-01, etc.)
  - [ ] Images display inline with text
  - [ ] Images alternate left/right positioning
  - [ ] Text wraps around images correctly
- [ ] Test Previous/Next navigation:
  - [ ] Previous disabled on Prologue
  - [ ] Next disabled on Chapter 12
  - [ ] Navigation updates URL hash
  - [ ] Smooth scroll to top on navigation
- [ ] Test browser back/forward buttons
- [ ] Verify glassmorphism styling (translucent cards, blur effects)

### Mobile/Tablet (iOS/Android)
- [ ] Sidebar displays at top on mobile
- [ ] Images become full-width (no float)
- [ ] Chapter navigation is touch-friendly
- [ ] Text remains readable
- [ ] All interactive elements work with touch

## Image Verification

### Prologue
- [ ] cortex-awakening-prologue-01.jpeg (right)
- [ ] cortex-awakening-prologue-02.jpeg (left)

### Chapter 1
- [ ] cortex-awakening-ch01-01.jpeg (left)
- [ ] cortex-awakening-ch01-02.jpeg (right)
- [ ] cortex-awakening-ch01-03.jpeg (left)

### Chapters 2-12
Verify each chapter's images display:
- [ ] Chapter 2: 2 images (essentials)
- [ ] Chapter 3: 1 image (essentials)
- [ ] Chapter 4: No images
- [ ] Chapter 5: 1 image (valuable)
- [ ] Chapter 6: 1 image (valuable)
- [ ] Chapter 7: 2 images (essentials + valuable)
- [ ] Chapter 8: 1 image (essentials)
- [ ] Chapter 9: 2 images (essentials + valuable)
- [ ] Chapter 10: 1 image (essentials)
- [ ] Chapter 11: 2 images (valuable)
- [ ] Chapter 12: 1 image (essentials/epilogue)

## Content Verification

- [ ] All chapter titles match sidebar navigation
- [ ] Meta badges display correctly (word count, type)
- [ ] Markdown parsing works:
  - [ ] H2 headings render
  - [ ] H3 headings render
  - [ ] Bold text (**text**)
  - [ ] Italic text (*text*)
  - [ ] Horizontal rules (---)
  - [ ] Paragraphs with proper spacing

## Error Handling

- [ ] Test invalid chapter hash (#invalid)
- [ ] Test missing chapter file (if any)
- [ ] Verify error message displays with "Return to Prologue" button
- [ ] Check browser console for errors

## Git Pages Compatibility

- [ ] All paths are relative (no absolute URLs)
- [ ] Images use correct path: `illustrations/images/`
- [ ] Assets use correct path: `../assets/`
- [ ] No Jekyll processing conflicts (`.nojekyll` present)
- [ ] File names compatible (no spaces, special chars)

## Performance

- [ ] Chapter loads in < 1 second
- [ ] Images load progressively
- [ ] No layout shift on image load
- [ ] Smooth scrolling animations
- [ ] No console warnings/errors

## Accessibility

- [ ] Alt text on all images
- [ ] Keyboard navigation works
- [ ] Focus states visible
- [ ] Readable color contrast
- [ ] Semantic HTML structure

## Cross-Browser Testing

- [ ] Chrome/Edge (Chromium)
- [ ] Safari (WebKit)
- [ ] Firefox (Gecko)
- [ ] Mobile Safari (iOS)
- [ ] Chrome Mobile (Android)

## Sign-Off

Once all items checked:
- [ ] Ready for Git Pages publication
- [ ] Documentation complete
- [ ] No critical bugs

**Tester:** _____________  
**Date:** _____________  
**Branch:** CORTEX-4.0
