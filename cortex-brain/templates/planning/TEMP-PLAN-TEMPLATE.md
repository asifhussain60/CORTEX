# 🎯 CORTEX Temp Plan: {FEATURE_NAME}

**Session ID:** {SESSION_ID}  
**Created:** {CREATED_TIMESTAMP}  
**Status:** 🔄 {STATUS}  
**Iteration:** {ITERATION_COUNT}  
**Complexity Tier:** {COMPLEXITY_TIER}

---

## 📋 User Request History

### Original Request (Iteration 1)
**Timestamp:** {ITERATION_1_TIMESTAMP}  
**Request:** {ORIGINAL_USER_REQUEST}

{ADDITIONAL_ITERATIONS}

### Latest Request (Iteration {CURRENT_ITERATION})
**Timestamp:** {LATEST_TIMESTAMP}  
**Request:** {LATEST_USER_REQUEST}

---

## 🎯 Proposed Approach

{APPROACH_SUMMARY}

### High-Level Strategy
{STRATEGY_DESCRIPTION}

### Key Technologies/Patterns
{TECHNOLOGIES_LIST}

### Integration Points
{INTEGRATION_POINTS}

---

## 📊 Complexity Analysis

| Metric | Value | Threshold | Status |
|--------|-------|-----------|--------|
| **Estimated Phases** | {PHASE_COUNT} | ≥3 = Master/Sub | {PHASE_STATUS} |
| **Estimated Tasks** | {TASK_COUNT} | ≥10 = Master/Sub | {TASK_STATUS} |
| **Estimated Hours** | {HOURS_ESTIMATE}h | ≥16h = Master/Sub | {HOURS_STATUS} |
| **Affected Modules** | {MODULE_COUNT} | ≥4 = Master/Sub | {MODULE_STATUS} |
| **Recommended Format** | {RECOMMENDED_FORMAT} | - | - |

**Complexity Tier:** {COMPLEXITY_TIER} (1=Trivial, 2=Simple, 3=Moderate, 4=Complex)

---

## 🔍 Context Analysis

### Code Structure (AST Analysis)
{AST_SUMMARY}

**Context Graph:** `context/ast-analysis-iter-{ITERATION}.json`

### Dependencies (Cortex Lens)
{LENS_SUMMARY}

**Context Graph:** `context/lens-dependencies-iter-{ITERATION}.json`

### Existing Patterns
{PATTERNS_SUMMARY}

**Context Graph:** `context/code-patterns-iter-{ITERATION}.json`

---

## 🤔 CORTEX Recommendation

**CRITICAL:** CORTEX challenges this request by balancing accuracy with efficiency against current architecture.

### Viability Assessment

**Overall Viability:** {VIABILITY_SCORE}/100 ({VIABILITY_LEVEL})

**Accuracy vs Efficiency Analysis:**
- **Accuracy Impact:** {ACCURACY_IMPACT} - {ACCURACY_DESCRIPTION}
- **Efficiency Impact:** {EFFICIENCY_IMPACT} - {EFFICIENCY_DESCRIPTION}
- **Performance Tradeoff:** {PERFORMANCE_TRADEOFF}

### Architectural Alignment

**Current Architecture Compatibility:**
{ARCHITECTURE_COMPATIBILITY_ANALYSIS}

**Design Pattern Match:**
{DESIGN_PATTERN_ANALYSIS}

**Technical Debt Impact:**
{TECH_DEBT_ASSESSMENT}

### CORTEX Position

{RECOMMENDATION_STANCE}

**Reasons:**
{RECOMMENDATION_REASONS}

### Alternative Solutions

#### Alternative 1: {ALT_1_NAME}
**Pros:** {ALT_1_PROS}
**Cons:** {ALT_1_CONS}
**Effort:** {ALT_1_EFFORT}

#### Alternative 2: {ALT_2_NAME}
**Pros:** {ALT_2_PROS}
**Cons:** {ALT_2_CONS}
**Effort:** {ALT_2_EFFORT}

#### Alternative 3: {ALT_3_NAME}
**Pros:** {ALT_3_PROS}
**Cons:** {ALT_3_CONS}
**Effort:** {ALT_3_EFFORT}

### Decision Framework

| Approach | Accuracy | Efficiency | Alignment | Risk | Recommended |
|----------|----------|------------|-----------|------|-------------|
| **User Request** | {USER_ACCURACY} | {USER_EFFICIENCY} | {USER_ALIGNMENT} | {USER_RISK} | {USER_RECOMMENDED} |
| **Alternative 1** | {ALT1_ACCURACY} | {ALT1_EFFICIENCY} | {ALT1_ALIGNMENT} | {ALT1_RISK} | {ALT1_RECOMMENDED} |
| **Alternative 2** | {ALT2_ACCURACY} | {ALT2_EFFICIENCY} | {ALT2_ALIGNMENT} | {ALT2_RISK} | {ALT2_RECOMMENDED} |
| **Alternative 3** | {ALT3_ACCURACY} | {ALT3_EFFICIENCY} | {ALT3_ALIGNMENT} | {ALT3_RISK} | {ALT3_RECOMMENDED} |

**CORTEX Recommended Approach:** {CORTEX_RECOMMENDATION}

---

## 📋 Proposed Plan Structure

{PLAN_STRUCTURE_PREVIEW}

---

## 🎯 Definition of Ready (DoR) Status

**DoR is a mutual contract between CORTEX and user - both must agree before execution.**

### CORTEX DoR Checklist (Zero Ambiguity Required)
- [ ] **Application Context:** AST graphs generated, code structure understood
- [ ] **File Impact Analysis:** All affected files identified with exact change types
- [ ] **TDD Workflow:** RED→GREEN→REFACTOR path clear for all components
- [ ] **Integration Points:** APIs, database, external services mapped
- [ ] **Edge Cases:** Error scenarios and boundary conditions documented
- [ ] **Viability Assessment:** Architecture alignment validated (score ≥70)
- [ ] **Alternative Solutions:** 2-3 alternatives evaluated and compared
- [ ] **Confidence Score:** {CONFIDENCE_SCORE}% (target: ≥90%)

**CORTEX Assessment:** {CORTEX_DOR_ASSESSMENT}

### User DoR Checklist (Validation Required)
- [ ] CORTEX interpretation matches my intent
- [ ] Affected files list is complete (no surprises)
- [ ] Proposed approach aligns with application architecture
- [ ] **CORTEX recommendation reviewed and decision made**
- [ ] **Alternative solutions considered (if viability <90)**
- [ ] Acceptance criteria are measurable and achievable
- [ ] Timeline/effort estimate is reasonable

**User Validation Required:** Please confirm DoR is satisfied or request refinement.

---

**DoR Status:** {DOR_STATUS}
- 🔴 **NOT READY** - Ambiguity >10%, missing critical context
- 🟡 **NEEDS REFINEMENT** - Ambiguity 5-10%, clarification needed
- 🟢 **READY** - Ambiguity <5%, mutual agreement achieved

**BLOCKING RULE:** CORTEX will NOT proceed to execution if DoR status is 🔴 or 🟡. User must provide additional refinement or CORTEX will ask specific clarifying questions.

---

## ✅ Acceptance Criteria (Definition of Done)

This feature will be considered complete when:

### Functional Requirements
{FUNCTIONAL_CRITERIA}

### Technical Requirements
{TECHNICAL_CRITERIA}

### Quality Requirements
- [ ] All unit tests passing (100% pass rate)
- [ ] Integration tests passing for affected modules
- [ ] Code coverage ≥85% for new code
- [ ] No critical/high severity issues in code analysis
- [ ] Performance benchmarks met (if applicable)

### Documentation Requirements
- [ ] Code documented with docstrings
- [ ] User-facing documentation updated
- [ ] API documentation generated (if applicable)
- [ ] Knowledge graph updated with learnings

### Compliance Requirements
- [ ] SKULL rules compliance validated
- [ ] Git isolation maintained (CORTEX code separate)
- [ ] TDD workflow followed (RED→GREEN→REFACTOR)
- [ ] Definition of Ready (DoR) criteria met before starting

---

## 🎯 Definition of Ready (DoR)

Before this plan can be promoted to active and executed:

- [ ] **User Approval:** Explicit user approval received
- [ ] **Complexity Confirmed:** Complexity analysis validated
- [ ] **Context Complete:** All AST/Lens graphs generated and stored
- [ ] **Dependencies Identified:** All external dependencies documented
- [ ] **Acceptance Criteria Clear:** DoD criteria unambiguous and measurable
- [ ] **Format Selected:** Single-file vs. master/sub-plan format determined
- [ ] **Risks Assessed:** Known risks documented with mitigations
- [ ] **Estimate Validated:** Time/effort estimate reasonable

---

## ⚠️ Identified Risks

{RISKS_LIST}

---

## 🔗 Dependencies & Prerequisites

{DEPENDENCIES_LIST}

---

## 📊 Iteration History

| Iteration | Timestamp | User Feedback | Changes Made | AST Run | Lens Run |
|-----------|-----------|---------------|--------------|---------|----------|
{ITERATION_HISTORY_TABLE}

---

## 💬 Approval Gateway

### Current Status: {APPROVAL_STATUS}

**Options:**
1. **✅ APPROVE** - Promote to active plan and begin execution
2. **🔄 REFINE** - Request additional changes or clarifications
3. **❌ REJECT** - Cancel this plan

---

### 📝 Provide Your Response

**If APPROVE:** Type "approve" or "approved"

**If REFINE:** Describe what you'd like to change or add. Examples:
- "Add OAuth 2.0 support"
- "Include rate limiting for API calls"
- "Ensure backward compatibility with v2.0"
- "Add detailed error handling strategy"

**If REJECT:** Type "reject" with optional reason

---

## 🎭 Session Metadata

**Session ID:** {SESSION_ID}  
**Temp Plan Folder:** `temp-plans/{FOLDER_NAME}/`  
**Context Folder:** `temp-plans/{FOLDER_NAME}/context/`  
**Created By:** {USER_NAME}  
**Last Updated:** {LAST_UPDATED_TIMESTAMP}  
**Total Context Graphs:** {CONTEXT_GRAPH_COUNT}  
**Orchestrator:** PlanningOrchestrator 4.0  

---

**🔐 SKULL Protection:** This plan CANNOT execute until moved to `active/` folder and registered in manifest.
