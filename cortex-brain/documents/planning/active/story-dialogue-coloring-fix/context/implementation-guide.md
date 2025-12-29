# 🛠️ Implementation Guide - Dialogue Coloring Fix

**Author:** Asif Hussain  
**Date:** December 29, 2025  
**Target:** story-viewer.js enhancement

---

## 🎯 Overview

This guide details how to fix the dialogue coloring issue by enhancing the `processCharacterDialog()` function in `story-viewer.js`.

**Current State:** 44.5% attribution rate  
**Target State:** 100% attribution rate

---

## 📋 Required Changes

### Change 1: Add Conversation Flow Tracking

**Location:** story-viewer.js, before `processCharacterDialog()` function

**Add Global Variable:**
```javascript
// Track last speaker for conversation flow
let lastSpeaker = null;
```

**Purpose:** Enable alternating speaker detection for back-and-forth dialogue

---

### Change 2: Enhance `processCharacterDialog()` Function

**Location:** story-viewer.js, line ~615

**Current Signature:**
```javascript
function processCharacterDialog(text) {
```

**Enhanced Signature:**
```javascript
function processCharacterDialog(text, resetSpeaker = false) {
```

**Purpose:** Allow resetting speaker tracking between paragraphs

---

### Change 3: Add First-Person Narrator Detection

**Location:** Inside `processCharacterDialog()`, before character loop

**Add Detection Block:**
```javascript
// First-person narrator detection (Asif)
const firstPersonPatterns = [
    /\bI\s+(?:said|asked|responded|replied|muttered|whispered|thought|wondered|froze|looked|turned|spun|gestured|pointed|ran|spun back)/i,
    /\bMy\s+(?:voice|thoughts|mind|hand|eyes|face)/i,
    /\bI\s+(?:let|tried|managed|failed|continued|stopped|started)/i
];

for (const pattern of firstPersonPatterns) {
    if (pattern.test(contextBefore)) {
        lastSpeaker = 'Asif';
        return `<span style="color: ${characterColors['Asif']}; font-weight: 500; text-shadow: 0 0 20px ${characterColors['Asif']}40; font-size: 0.9em;">"${dialog}"</span>`;
    }
}
```

**Purpose:** Detect when Asif is speaking based on first-person narrative

---

### Change 4: Add Conversation Flow Logic

**Location:** Inside `processCharacterDialog()`, after character detection

**Add Flow Detection:**
```javascript
// If no speaker detected but we have conversation flow
if (!detectedSpeaker && lastSpeaker) {
    // Alternate speaker for consecutive short dialogues
    if (dialog.length < 50) {
        // Simple alternation: if last was Asif, try Miss G; if Miss G, try Asif
        const alternativeSpeaker = lastSpeaker === 'Asif' ? 'Miss G' : 'Asif';
        
        // Verify alternative speaker makes sense in context
        const contextText = contextBefore + ' ' + contextAfter;
        const hasConflictingAttribution = /\b(Asif|Miss G|Copilot|CORTEX)\s+(?:asked|said|replied)/i.test(contextText);
        
        if (!hasConflictingAttribution) {
            detectedSpeaker = alternativeSpeaker;
            const color = characterColors[alternativeSpeaker];
            lastSpeaker = alternativeSpeaker;
            return `<span style="color: ${color}; font-weight: 500; text-shadow: 0 0 20px ${color}40; font-size: 0.9em;">"${dialog}"</span>`;
        }
    }
}
```

**Purpose:** Handle alternating dialogue in conversations

---

### Change 5: Update Context Detection

**Location:** Inside `processCharacterDialog()`, where character patterns are checked

**Extend Context Window:**
```javascript
// Get context before the quote (up to 300 chars for better detection)
const contextBefore = text.substring(Math.max(0, offset - 300), offset);

// Get context after the quote (up to 150 chars for "said" attribution)
const contextAfter = text.substring(offset + match.length, Math.min(text.length, offset + match.length + 150));
```

**Purpose:** Capture more context for better attribution

---

### Change 6: Add Miss G Voice Patterns

**Location:** Inside character detection loop

**Add Miss G-Specific Patterns:**
```javascript
// Special handling for Miss G (inner voice, imaginary girlfriend)
if (character === 'Miss G') {
    const missGPatterns = [
        /Miss G'?s?\s+voice/i,
        /Miss G'?s?\s+(?:voice|thoughts|presence|tone)/i,
        /(?:she|She)\s+(?:used my full name|cut through|observed|noted|said quietly|asked gently)/i,
        /imaginary girlfriend/i,
        /in my (?:thoughts|mind|consciousness|head)/i
    ];
    
    if (missGPatterns.some(p => p.test(contextBefore) || p.test(contextAfter))) {
        lastSpeaker = 'Miss G';
        return `<span style="color: ${characterColors['Miss G']}; font-weight: 500; text-shadow: 0 0 20px ${characterColors['Miss G']}40; font-size: 0.9em;">"${dialog}"</span>`;
    }
}
```

**Purpose:** Better detect Miss G's unique dialogue patterns

---

### Change 7: Reset Speaker Between Sections

**Location:** In `parseMarkdown()` function, where paragraphs are processed

**Add Reset Call:**
```javascript
// Reset speaker tracking at section boundaries
if (line.match(/^#{1,3}\s+/)) {
    lastSpeaker = null;
}
```

**Purpose:** Prevent speaker tracking from bleeding across scene changes

---

## 🧪 Testing Strategy

### Test Case 1: Short Back-and-Forth
**Input:**
```markdown
"What have you done?" Miss G asked.
"Improved it." 
"How?"
"Coffee mug architecture."
```

**Expected:**
- Line 1: Miss G (explicit) ✅
- Line 2: Asif (alternation) ✅
- Line 3: Miss G (alternation) ✅
- Line 4: Asif (alternation) ✅

### Test Case 2: First-Person Narrator
**Input:**
```markdown
I froze mid-keystroke. "Which one?"
```

**Expected:**
- Asif (first-person "I froze") ✅

### Test Case 3: Long-Distance Attribution
**Input:**
```markdown
Miss G pinched the bridge of her nose—a gesture I'd seen 
approximately 847 times since our imaginary relationship began. 
"Tell me this isn't another smart mirror situation."
```

**Expected:**
- Miss G (via "her nose" + "Miss G" in context) ✅

### Test Case 4: Pronoun Resolution
**Input:**
```markdown
She used my full name. Never a good sign. "What have you done to that basement?"
```

**Expected:**
- Miss G (via "She used") ✅

---

## 📊 Validation Checklist

Before deploying:

- [ ] Run local HTTP server: `python -m http.server 8000`
- [ ] Open `http://localhost:8000/story/viewer.html`
- [ ] Test Prologue (104 dialogues)
- [ ] Test Chapter 1 (51 dialogues)
- [ ] Spot-check Chapters 2-13
- [ ] Verify no HTML/CSS/paths colored
- [ ] Verify no regressions (previously colored dialogues still colored)
- [ ] Check mobile responsiveness
- [ ] Verify all character colors correct

---

## 🔄 Rollback Plan

If issues arise:

1. **Backup current version:**
   ```bash
   cp docs/story/story-viewer.js docs/story/story-viewer.js.backup
   ```

2. **Restore from backup:**
   ```bash
   cp docs/story/story-viewer.js.backup docs/story/story-viewer.js
   ```

3. **Git revert if committed:**
   ```bash
   git checkout HEAD~1 -- docs/story/story-viewer.js
   ```

---

## 📈 Success Metrics

| Metric | Baseline | Target | How to Measure |
|--------|----------|--------|----------------|
| Attribution Rate | 44.5% | 100% | Re-run `analyze-story-dialogues.py` |
| Asif Dialogues | 273 | ~650 | Check analysis report |
| Miss G Dialogues | 198 | ~350 | Check analysis report |
| Unattributed | 606 | 0 | Check analysis report |
| False Positives | 0 | 0 | Manual review of HTML/CSS content |

---

## 🐛 Known Edge Cases

### Edge Case 1: Single-Word Responses
```markdown
"Ready?"
"No."
```
**Solution:** Use conversation flow (alternation)

### Edge Case 2: Technical Dialogue
```markdown
"Run git commit -m 'fix: dialogue colors'"
```
**Solution:** Technical terms like "git" should be colored (it's still dialogue)

### Edge Case 3: Multiple Characters Present
```markdown
Asif looked at Mom. "Should I tell her?"
Miss G's voice in his head: "Yes."
```
**Solution:** Explicit attribution overrides alternation

---

## 📝 Post-Implementation Tasks

1. ✅ Update CHARACTER-COLORS.md with new statistics
2. ✅ Run full analysis: `python analyze-story-dialogues.py`
3. ✅ Generate validation report
4. ✅ Update this guide with actual results
5. ✅ Commit changes with descriptive message
6. ✅ Test on GitHub Pages deployment

---

**Next Action:** Apply these changes to `story-viewer.js` systematically
