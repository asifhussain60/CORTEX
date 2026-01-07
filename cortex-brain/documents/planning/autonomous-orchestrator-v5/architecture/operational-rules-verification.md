# Operational Rules Verification Report

**Purpose:** Verify 4 user-requested operational rules are captured in planning orchestrator  
**Date:** 2025-01-19  
**Status:** ✅ ALL RULES EXIST (but not in v5 plan)

---

## 🔍 Summary

All 4 user-requested operational rules **ALREADY EXIST** in CORTEX brain protection rules but are **NOT explicitly referenced** in the autonomous-orchestrator-v5 plan.

**Finding:** Rules are scattered across:
- `cortex-brain/brain-protection-rules.yaml` (SKULL rules)
- `cortex-brain/token-optimization-rules.yaml`
- `cortex-brain/manifests/orchestrators/planning-system-4.0-manifest.yaml`

**Recommendation:** Consolidate references in v5 plan to ensure orchestrator implementation enforces these rules.

---

## ✅ Rule 1: Vision API Image Processing

### User Requirement
> "Instructions should be added to vision api any images attached to the prompt to process the image and ast the view to understand how to identify elements for easy future selction. Every turn should update context yaml files appending to the knowledge graph."

### ✅ FOUND: VISION_API_INTEGRATION_ENFORCEMENT

**Location:** `cortex-brain/brain-protection-rules.yaml` (lines 6700+)

**Rule Details:**
- **Rule ID:** `VISION_API_INTEGRATION_ENFORCEMENT`
- **Severity:** `blocked`
- **Visual Indicator:** 📷 icon in response header
- **Automatic Engagement:** Detects image attachments (PNG/JPG/JPEG/WEBP/GIF)

**Capabilities:**
- Comprehensive UI element extraction (buttons, inputs, text, icons)
- CSS selector generation for automation
- Test scenario generation (Given/When/Then)
- Layout structure mapping (DOM inference)
- Accessibility audit (WCAG compliance)
- Security considerations detection

**Integration Points:**
- TDD Orchestrator: Generate test automation selectors
- Planning System: Extract feature requirements from mockups
- ADO Operations: Enhance work items with visual context
- Debug Orchestrator: Extract error details from screenshots

**Context YAML Updates:**
```yaml
vision_analysis_requirements:
  comprehensive_extraction:
    ui_elements: "All visible components, text, icons, layout"
    selector_strategy: "data-testid, aria-label, id, class (priority order)"
  output_format:
    structured_json: true
    sections:
      - image_metadata
      - ui_inventory
      - layout_map
      - selector_strategy
      - implementation_guide
      - test_scenarios
      - accessibility_audit
```

**Status in V5 Plan:** ❌ NOT REFERENCED

---

## ✅ Rule 2: CSS-First Styling Approach

### User Requirement
> "When working with html styling, the class rules should be added to the css file first before applying the class attribute to the elements"

### ✅ FOUND: INLINE_CSS_PROHIBITION

**Location:** `cortex-brain/brain-protection-rules.yaml` (lines 1613-1810)

**Rule Details:**
- **Rule ID:** `INLINE_CSS_PROHIBITION`
- **Severity:** `blocked`
- **Description:** "Inline CSS prohibited - all styles must be centralized to CSS files. REFACTOR phase must migrate inline styles."

**Detection Patterns:**
- HTML/JSX inline styles: `style="..."`
- Embedded `<style>` tags
- JavaScript style manipulation: `.style.property`, `.css()`, `cssText`
- jQuery CSS methods

**Alternatives (CSS-First Workflow):**
1. Extract inline styles to external CSS file
2. Use CSS classes instead of inline styles
3. Create component-specific CSS modules (`.module.css`)
4. CSS rules defined BEFORE HTML class application
5. Replace JS style manipulation with CSS class toggling

**REFACTOR Phase Integration:**
```yaml
refactor_validations:
  - inline_css_migration  # Enforced in REFACTOR phase
  - css_file_exists_before_html_classes
```

**Example Workflow:**
```css
/* Step 1: Define CSS rules FIRST (styles.css) */
.content-box {
  color: blue;
  margin: 10px;
}

/* Step 2: THEN apply class in HTML */
<div class="content-box">Content</div>
```

**Status in V5 Plan:** ❌ NOT REFERENCED

---

## ✅ Rule 3: Work Decomposition (Response Length Limits)

### User Requirement
> "The planning orchestrator should decompose the work in such a way that copilot works on small increments autonomously rather than trying to do too much at a time"

### ✅ FOUND: INCREMENTAL_PLAN_GENERATION

**Location:** `cortex-brain/brain-protection-rules.yaml` (lines ~107)

**Rule Details:**
- **Rule ID:** `INCREMENTAL_PLAN_GENERATION`
- **Severity:** `blocked`
- **Description:** "When generating YAML planning documents, create file first then add phases incrementally to avoid response length limits"

**Detection Keywords:**
- "create plan", "generate plan", "planning document"
- "comprehensive", "complete", "detailed phases"
- Combined with YAML format indicators

**Incremental Workflow:**
1. **STEP 1:** Create planning YAML file with metadata and structure only
2. **STEP 2:** Add Phase 1 details to file
3. **STEP 3:** Add Phase 2 details to file (separate response)
4. **STEP 4:** Add Phase 3 details to file (separate response)
5. **STEP 5:** Add remaining phases incrementally

**Key Principle:**
> "Each step writes to file, NOT to chat response (avoid length limit)"

**Rationale:**
```yaml
rationale:
  - Response length limits hit when generating comprehensive plans
  - Incremental file updates prevent hitting limits
  - Copilot works autonomously on small increments
  - File-based persistence (not chat-based)
```

**Status in V5 Plan:** ⚠️ MENTIONED GENERICALLY (not explicitly enforced)

---

## ✅ Rule 4: Token Optimization During Implementation

### User Requirement
> "Token optimizations should be done during implementations"

### ✅ FOUND: TOKEN_OPTIMIZATION_RULES

**Location:** `cortex-brain/token-optimization-rules.yaml`

**Framework Details:**
- **Version:** 1.0 (PRODUCTION)
- **Status:** Active enforcement
- **Impact:** 40-80% token reduction across operations

**5 Core Principles:**

1. **BATCH_PARALLEL_READS** (40-60% reduction)
   - Read large context windows in single call
   - Avoid sequential small reads
   ```yaml
   before: read_file(1-50), read_file(51-100), ... # Multiple calls
   after: read_file(1-500)  # Single large read (40-60% reduction)
   ```

2. **LARGE_CONTEXT_WINDOWS** (50-70% reduction)
   - Use 100-500 line ranges per read
   - Minimize round trips
   ```yaml
   before: 10 reads × 50 lines = 500 lines total + 10× overhead
   after: 1 read × 500 lines = 500 lines total + 1× overhead
   ```

3. **CONSOLIDATED_SEARCHES** (60-80% reduction)
   - Use regex alternation: `pattern1|pattern2|pattern3`
   - Single search with multiple keywords
   ```yaml
   before: grep_search("pattern1"), grep_search("pattern2"), ...
   after: grep_search("pattern1|pattern2|pattern3", isRegexp=true)
   ```

4. **ELIMINATE_REDUNDANT_SUMMARIES** (100% reduction)
   - Provide full context instead of summaries
   - User can filter what they need
   ```yaml
   before: "Here's a summary... [25 files omitted]"
   after: [Full list of all files, user filters]
   ```

5. **PATH_CACHING** (90% reduction)
   - Cache frequently accessed paths
   - Avoid repeated path resolution
   ```yaml
   before: Resolve path on every file operation
   after: Resolve once, cache for session
   ```

**Integration with Planning System:**
```yaml
planning_phases:
  - phase: implementation
    token_optimization: required
    validation:
      - check_batch_operations
      - verify_large_reads
      - consolidate_searches
```

**Status in V5 Plan:** ❌ NOT REFERENCED

---

## 📋 Integration Requirements

### V5 Plan Updates Needed

1. **Add Operational Rules Section to 00-MASTER-PLAN-V5.md**
   ```markdown
   ## 🛡️ Operational Rules Enforcement

   The following operational rules MUST be enforced in Python orchestrator:

   1. **Vision API Integration** (VISION_API_INTEGRATION_ENFORCEMENT)
      - Auto-engage on image attachment
      - Update context YAML files
      - Generate test selectors
      - Reference: brain-protection-rules.yaml:6700+

   2. **CSS-First Styling** (INLINE_CSS_PROHIBITION)
      - CSS rules BEFORE HTML classes
      - No inline styles in REFACTOR phase
      - Reference: brain-protection-rules.yaml:1613-1810

   3. **Incremental Work Decomposition** (INCREMENTAL_PLAN_GENERATION)
      - File-based phase generation (not chat-based)
      - Small increments to avoid response length limits
      - Reference: brain-protection-rules.yaml:~107

   4. **Token Optimization** (TOKEN_OPTIMIZATION_RULES)
      - Batch parallel reads (40-60% reduction)
      - Large context windows (50-70% reduction)
      - Consolidated searches (60-80% reduction)
      - Reference: token-optimization-rules.yaml
   ```

2. **Update architecture/config-specification.md**
   ```yaml
   operational_rules:
     vision_api_integration:
       enabled: true
       auto_engage_on_images: true
       context_yaml_updates: true
       selector_generation: true

     css_first_enforcement:
       enabled: true
       inline_css_blocked: true
       refactor_phase_validation: true

     work_decomposition:
       max_response_length: 4000  # Characters
       incremental_file_updates: true
       phases_per_response: 1

     token_optimization:
       enabled: true
       batch_operations: true
       large_context_windows: true
       consolidated_searches: true
       reference_file: "cortex-brain/token-optimization-rules.yaml"
   ```

3. **Update architecture/database-schema.md**
   ```sql
   -- Add operational_rules table for audit trail
   CREATE TABLE operational_rules (
       rule_id TEXT PRIMARY KEY,
       phase_id TEXT,
       enforced BOOLEAN,
       validation_result TEXT,
       timestamp TEXT,
       FOREIGN KEY (phase_id) REFERENCES phases(id)
   );
   ```

---

## 🎯 Recommendations

1. **Create Operational Rules Document**
   - New file: `architecture/operational-rules.md`
   - Consolidate 4 rules with references
   - Include enforcement patterns

2. **Update Master Plan**
   - Add operational rules section
   - Reference in Phase 4 (Planning Orchestrator v5) requirements
   - Add validation checkpoint

3. **Update Config Specification**
   - Add `operational_rules` config block
   - Include toggle flags for each rule
   - Reference source YAML files

4. **Add Validation in Database Schema**
   - `operational_rules` table for tracking
   - Audit trail of rule enforcement
   - Compliance reporting

5. **Python Implementation Requirements**
   - Load rules from brain-protection-rules.yaml
   - Validate enforcement at phase gates
   - Log rule violations
   - Block progression on critical violations

---

## 📊 Current Status Matrix

| Rule | Exists in Brain | Rule ID | Severity | V5 Plan Status |
|------|----------------|---------|----------|----------------|
| Vision API | ✅ Yes | VISION_API_INTEGRATION_ENFORCEMENT | blocked | ❌ Not referenced |
| CSS-First | ✅ Yes | INLINE_CSS_PROHIBITION | blocked | ❌ Not referenced |
| Work Decomposition | ✅ Yes | INCREMENTAL_PLAN_GENERATION | blocked | ⚠️ Mentioned generically |
| Token Optimization | ✅ Yes | TOKEN_OPTIMIZATION_RULES (entire file) | info | ❌ Not referenced |

**Overall:** 4/4 rules exist in CORTEX brain, 0/4 explicitly in v5 plan

---

## 🚀 Next Steps

1. Create `architecture/operational-rules.md` (consolidation document)
2. Update `00-MASTER-PLAN-V5.md` (add operational rules section)
3. Update `architecture/config-specification.md` (add config keys)
4. Update `architecture/database-schema.md` (add operational_rules table)
5. Test Python orchestrator enforcement (Phase 4 implementation)

---

**Conclusion:** All 4 operational rules exist in CORTEX brain protection system but need explicit integration into v5 planning orchestrator documentation and implementation.
