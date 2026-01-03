# CORTEX.prompt.md Structure Analysis

**Date:** 2026-01-03  
**Analyzer:** CORTEX Planning System v5  
**Purpose:** Map current 508-line prompt for lean transformation  
**Target:** Reduce to <200 lines while maintaining functionality

---

## 📊 Current State Summary

**Total Lines:** 508 lines  
**Target Lines:** <200 lines (~150 ideal)  
**Reduction Goal:** 61% smaller  
**Current Token Count:** ~8,500 tokens  
**Target Token Count:** ~2,500 tokens (70% reduction)

---

## 📋 Content Categorization

### 1. **Routing Logic** (KEEP IN PROMPT - Machine Readable)
**Lines:** 176-330 (~154 lines)  
**Content:**
- Intent Router table (13 orchestrators)
- Pattern matching rules (regex patterns)
- Confidence thresholds
- LLM fallback configuration
- Continuation detection logic
- Vision API auto-engagement rules

**Status:** ✅ **KEEP** - Core routing table (reduce to ~80 lines)
**Action:** Compress table, remove verbose descriptions, keep patterns only

---

### 2. **Protocol Specifications** (KEEP IN PROMPT - Critical)
**Lines:** 26-74, 95-150 (~103 lines)  
**Content:**
- Parse User Request FIRST rules
- Planning detection (HIGHEST PRIORITY)
- Hand-Off Protocol (FORBIDDEN/REQUIRED behaviors)
- Orchestrator Autonomy Matrix
- Brain Protection (SKULL) rules summary

**Status:** ✅ **KEEP** - Protocol enforcement (reduce to ~40 lines)
**Action:** Keep rules, remove examples, compress tables

---

### 3. **Orchestrator Documentation** (EXTERNALIZE)
**Lines:** 151-175, 405-475 (~95 lines)  
**Content:**
- Orchestrator behavior descriptions
- Output format examples
- Progress bar rendering instructions (60+ lines)
- Template references
- Helper method documentation

**Status:** ❌ **EXTERNALIZE** → `cortex-brain/documents/orchestrators-quick-ref.md`
**Action:** Move all orchestrator docs to external reference

---

### 4. **Response Format Guidelines** (EXTERNALIZE)
**Lines:** 476-495 (~20 lines)  
**Content:**
- Header format rules
- Body adaptive tiers (INSTANT/FOCUSED/STRUCTURED/COMPREHENSIVE)
- Next Steps format
- Completion format

**Status:** ❌ **EXTERNALIZE** → `cortex-brain/response-templates-v4.yaml` (already exists)
**Action:** Reference template file only

---

### 5. **Examples & Illustrations** (REMOVE)
**Lines:** Scattered throughout (~40 lines)  
**Content:**
- Planning detection examples
- Routing examples
- Progress bar examples
- User interaction examples

**Status:** ❌ **REMOVE** - Verbose, not needed for machine reading
**Action:** Delete examples, keep rules only

---

### 6. **Context & Metadata** (COMPRESS)
**Lines:** 1-25 (~25 lines)  
**Content:**
- Version info
- Author details
- Copyright
- Anti-bloat warning

**Status:** ⚠️ **COMPRESS** - Keep minimal metadata (reduce to ~5 lines)
**Action:** Version + reference to external docs

---

### 7. **Fallback Behavior** (KEEP - COMPRESS)
**Lines:** 467-475 (~9 lines)  
**Content:**
- LLM classification failure handling
- Orchestrator execution failure
- Missing orchestrator handling
- Ambiguous intent handling

**Status:** ✅ **KEEP** - Critical error handling (reduce to ~5 lines)
**Action:** Bullet list only, remove descriptions

---

### 8. **Architecture & Quick Reference** (EXTERNALIZE)
**Lines:** 496-508 (~13 lines)  
**Content:**
- Architecture diagram
- Quick reference table
- Resource links

**Status:** ❌ **EXTERNALIZE** → `cortex-brain/documents/cortex-architecture-quick-ref.md`
**Action:** Move to external reference

---

## 🎯 Externalization Map

### Files to Create (NEW)

1. **`cortex-brain/documents/orchestrators-quick-ref.md`**
   - **Size:** ~300 lines
   - **Content:**
     - All 10 orchestrator descriptions
     - Behavior patterns
     - Output formats
     - Progress bar rendering
     - Template references
   - **Referenced by:** Lean CORTEX.prompt.md line ~15

2. **`cortex-brain/documents/cortex-architecture-quick-ref.md`**
   - **Size:** ~50 lines
   - **Content:**
     - Architecture diagram
     - Brain tier structure
     - Command quick reference
   - **Referenced by:** Lean CORTEX.prompt.md line ~145

3. **`cortex-brain/documents/cortex-protocol-examples.md`**
   - **Size:** ~100 lines
   - **Content:**
     - Planning detection examples
     - Routing examples
     - Hand-off protocol examples
   - **Referenced by:** External learning material (NOT in prompt)

### Files to Enhance (EXISTING)

4. **`cortex-brain/response-templates-v4.yaml`** ✅ Already exists
   - **Enhancement:** Add response format tier definitions
   - **Current:** Template content only
   - **Add:** INSTANT/FOCUSED/STRUCTURED/COMPREHENSIVE specs

5. **`cortex-brain/brain-protection-rules.yaml`** ✅ Already exists
   - **Current:** 61 detailed rules
   - **Usage:** Reference for SKULL rule enforcement

---

## 📐 Lean Prompt Structure (Target ~150 lines)

### Section Breakdown

```markdown
# CORTEX Universal Entry Point
[5 lines: Version, author, copyright]

## Core Protocol
[30 lines: Parse rules, Planning detection, Hand-off protocol]

## Intent Router
[80 lines: Routing table ONLY - orchestrators, patterns, types]

## Fallback Handling
[5 lines: Error handling bullet list]

## Brain Protection (SKULL)
[10 lines: Rule summary with reference link]

## Document Organization
[5 lines: cortex-brain structure rules]

## External References
[15 lines: Links to orchestrators-quick-ref, templates, etc.]

---
Total: ~150 lines (70% reduction)
```

---

## 🔍 Token Optimization Analysis

### Current Token Distribution

| Section | Current Tokens | Target Tokens | Reduction |
|---------|----------------|---------------|-----------|
| Routing logic | 2,500 | 1,200 | 52% |
| Protocol specs | 1,800 | 600 | 67% |
| Orchestrator docs | 1,500 | 100 (reference) | 93% |
| Response formats | 400 | 50 (reference) | 88% |
| Examples | 800 | 0 | 100% |
| Metadata | 300 | 100 | 67% |
| Fallback | 200 | 100 | 50% |
| Architecture | 300 | 150 | 50% |
| **TOTAL** | **~8,500** | **~2,500** | **70%** |

---

## ✅ Validation Criteria

### Content Integrity Check
- [ ] All 10 orchestrators still routable
- [ ] Pattern matching preserved (100% regex patterns intact)
- [ ] Hand-off protocol rules complete
- [ ] SKULL rules enforced
- [ ] Fallback chain functional

### Functional Equivalence Check
- [ ] Introduction command works
- [ ] Planning detection works (MUST NOT IMPLEMENT)
- [ ] All 🛡️ AUTONOMOUS orchestrators route correctly
- [ ] All 📋 GUIDED orchestrators route correctly
- [ ] Continuation detection works
- [ ] Vision API auto-engagement works

### Performance Metrics
- [ ] Token count reduced by ≥65%
- [ ] Line count reduced by ≥60%
- [ ] Loading time <500ms (no noticeable delay)
- [ ] Master Orchestrator can parse table directly

---

## 🚨 Critical Preservation Requirements

### MUST PRESERVE (Zero Tolerance)

1. **Pattern Matching Regex:** All 10 orchestrator patterns exactly as-is
2. **Hand-Off Protocol:** 5 FORBIDDEN + 5 REQUIRED behaviors
3. **Planning Detection:** HIGHEST PRIORITY section (lines 26-74)
4. **Parse User Request:** Meta-directive removal rules
5. **Continuation Detection:** "continue" routing to last orchestrator
6. **Vision API Auto-Engagement:** Image detection configuration

### CAN COMPRESS (Carefully)

1. **Orchestrator descriptions:** Keep name + type (🛡️/📋) only
2. **Response format tiers:** Reference template file
3. **Progress bar rendering:** Reference external doc
4. **Examples:** Remove entirely
5. **Architecture diagram:** Reference external doc

### CAN REMOVE (Safe)

1. **All prose explanations**
2. **All examples**
3. **Verbose table descriptions**
4. **Quick reference sections**
5. **"Why Master Orchestrator?" explanations**

---

## 📊 Transformation Metrics

| Metric | Before | After (Target) | Change |
|--------|--------|----------------|--------|
| **Lines** | 508 | ~150 | -70% |
| **Tokens** | ~8,500 | ~2,500 | -70% |
| **Sections** | 14 | 7 | -50% |
| **Tables** | 6 | 2 | -67% |
| **Examples** | 8 | 0 | -100% |
| **External Refs** | 0 | 3 | +3 |
| **Load Time** | ~2s | <0.5s | -75% |

---

## 🎯 Next Steps (Task 6.4.5.2)

1. **Design lean specification** based on this analysis
2. **Create orchestrators-quick-ref.md** with externalized content
3. **Implement lean CORTEX.prompt.md** with strict <200 line limit
4. **Enhance Master Orchestrator** to parse lean table format
5. **Validate routing** for all 10 orchestrators

---

## 📝 Summary

**Key Findings:**
- 61% of content can be externalized or removed
- Intent Router table is the core (must preserve exactly)
- Progress bar rendering (60 lines) should move to external doc
- Examples and prose add no machine-readable value

**Transformation Strategy:**
1. **KEEP:** Routing table, protocol rules, fallback handling
2. **EXTERNALIZE:** Orchestrator docs, response formats, architecture
3. **REMOVE:** Examples, verbose descriptions, quick references

**Benefits:**
- ✅ 70% token reduction (8,500 → 2,500)
- ✅ Faster loading (<0.5s vs ~2s)
- ✅ Machine-readable format for Master Orchestrator
- ✅ Easier to maintain (changes go to external docs)
- ✅ Zero functional regression (all routing preserved)

**Risk Mitigation:**
- Create backup before transformation (.v4.backup)
- Validate all 10 orchestrators after implementation
- Keep examples in separate learning doc (not in prompt)
