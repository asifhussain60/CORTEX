# Orchestrator Evaluation Template

**Version:** 1.0  
**Created:** January 3, 2026  
**Purpose:** Standardized template for evaluating GUIDED orchestrators for potential AUTONOMOUS conversion

---

## 📋 Orchestrator Information

**Orchestrator Name:** [NAME]  
**Current Type:** 📋 GUIDED  
**Evaluator:** [NAME]  
**Evaluation Date:** [DATE]

---

## 🔍 Current Implementation Analysis

### 1. Location & Structure

**Manifest File:** `cortex-brain/manifests/orchestrators/[name]-orchestrator-manifest.yaml`  
**Prompt File(s):** `.github/prompts/[name]/[files]`  
**Supporting Files:** [List any related utilities, templates, etc.]

### 2. Current Workflow Description

**Phase Structure:**
```
Phase 0: [Name] - [Description]
Phase 1: [Name] - [Description]
Phase 2: [Name] - [Description]
...
```

**Total Phases:** [Number]  
**Linear vs Branching:** [Linear / Conditional / Complex]

### 3. Current Capabilities

**Primary Functions:**
- [Function 1]
- [Function 2]
- [Function 3]

**Key Operations:**
- [Operation type: file manipulation, AST parsing, etc.]
- [Operation type]
- [Operation type]

### 4. Integration Points

**Dependencies:**
- Master Orchestrator: [Yes/No - routing configured?]
- BaseOrchestrator: [N/A for GUIDED]
- PlanningStateDB: [Yes/No - state tracking?]
- Other Orchestrators: [List any]

**Tool Calls Used:**
- [Tool 1: description]
- [Tool 2: description]
- [Tool 3: description]

---

## 📊 Decision Matrix Scoring

### Criterion 1: Operation Complexity (Weight: 30%)

**Assessment:**
- AST manipulation: [Yes/No]
- Multi-phase workflow: [Yes/No - how many phases?]
- Complex algorithms: [Yes/No - describe]
- Multi-file analysis: [Yes/No]

**Raw Score:** [1-10]  
**Weighted Score:** [Score × 0.30]  
**Rationale:** [Explanation of score]

---

### Criterion 2: State Management (Weight: 25%)

**Assessment:**
- Requires rollback: [Yes/No - describe scenarios]
- Multi-phase state: [Yes/No - how many phases?]
- Progress persistence: [Yes/No - what needs tracking?]
- Transaction boundaries: [Yes/No - where?]

**Raw Score:** [1-10]  
**Weighted Score:** [Score × 0.25]  
**Rationale:** [Explanation of score]

---

### Criterion 3: User Interaction (Weight: 20%)

**Assessment:**
- Automation level: [Fully automated / Minimal gates / Moderate / High interaction]
- Approval gates: [Number and location]
- Conversational elements: [Yes/No - describe]
- Iterative refinement: [Yes/No]

**Raw Score:** [1-10]  
**Weighted Score:** [Score × 0.20]  
**Rationale:** [Explanation of score]

---

### Criterion 4: Maintenance Cost (Weight: 15%)

**Assessment:**
- Logic complexity: [Simple / Moderate / Complex]
- Update frequency: [Rarely / Occasionally / Regularly]
- Debug difficulty: [Easy / Moderate / Hard with manifests]
- Test coverage: [Current coverage if any]

**Raw Score:** [1-10]  
**Weighted Score:** [Score × 0.15]  
**Rationale:** [Explanation of score]

---

### Criterion 5: Code Reusability (Weight: 10%)

**Assessment:**
- Shared utilities: [List any reusable components]
- Used by other orchestrators: [List which ones]
- Potential for reuse: [Describe opportunities]
- Unique vs generic logic: [Ratio]

**Raw Score:** [1-10]  
**Weighted Score:** [Score × 0.10]  
**Rationale:** [Explanation of score]

---

## 🎯 Final Score & Recommendation

| Criterion | Weight | Raw Score | Weighted Score |
|-----------|--------|-----------|----------------|
| Operation Complexity | 30% | [X/10] | [X.XX] |
| State Management | 25% | [X/10] | [X.XX] |
| User Interaction | 20% | [X/10] | [X.XX] |
| Maintenance Cost | 15% | [X/10] | [X.XX] |
| Code Reusability | 10% | [X/10] | [X.XX] |
| **TOTAL** | **100%** | **[XX/50]** | **[X.XX/10]** |

---

### Recommendation: [AUTONOMOUS / GUIDED / NEUTRAL]

**Confidence Level:** [High / Medium / Low]

**Primary Rationale:**
[2-3 sentences explaining the key factors driving the recommendation]

**Key Decision Factors:**
1. [Factor 1]
2. [Factor 2]
3. [Factor 3]

---

## 🏗️ Migration Roadmap (If AUTONOMOUS Recommended)

### Effort Estimate

**Total Duration:** [X days]

**Phase Breakdown:**
- **Day 1:** [Core orchestrator implementation]
- **Day 2:** [Additional features]
- **Day 3:** [Testing and integration]
- **Day X:** [Master Orchestrator integration]

### Implementation Strategy

**New Files to Create:**
```
src/orchestrators/[name]/
├── [name]_orchestrator_v2.py       # Main orchestrator (BaseOrchestrator v4.1)
├── [component]_engine.py            # Core logic component
├── [component]_validator.py         # Validation component
└── __init__.py

cortex-brain/manifests/orchestrators/
└── [name]-orchestrator-v2.yaml      # Configuration manifest

cortex-brain/templates/[name]/
├── [template1].jinja2
└── [template2].jinja2

tests/orchestrators/[name]/
├── test_[name]_orchestrator_v2.py
├── test_[component]_engine.py
└── test_[component]_validator.py
```

### Key Components

1. **Core Orchestrator:** [Description]
2. **Component 1:** [Description]
3. **Component 2:** [Description]
4. **State Management:** [Description of database schema]

### Master Orchestrator Integration

**Routing Pattern:**
```yaml
- pattern: "^([pattern]|[pattern]).*$"
  orchestrator: [name]_orchestrator_v2
  confidence: 1.0
  match_type: regex
  priority: [number]
  metadata:
    description: "[Description]"
    autonomous: true
```

### Testing Strategy

**Test Coverage Requirements:**
- Unit tests: 100% coverage
- Integration tests: [X scenarios]
- End-to-end tests: [X workflows]

**Critical Test Cases:**
1. [Test case 1]
2. [Test case 2]
3. [Test case 3]

### SKULL Enforcement

**Applicable Rules:**
- `TDD_ENFORCEMENT`: [How it applies]
- `HOLISTIC_CODE_DISCOVERY_ENFORCEMENT`: [How it applies]
- `REFACTOR_CODE_CLEANUP_ENFORCEMENT`: [How it applies]
- [Other applicable rules]

---

## 🚫 Retention Rationale (If GUIDED Recommended)

### Why Remain GUIDED

**Primary Reasons:**
1. [Reason 1]
2. [Reason 2]
3. [Reason 3]

### Enhancements (If Keeping GUIDED)

**Proposed Improvements:**
1. **Master Orchestrator Routing:** Add pattern to route GUIDED orchestrator
   ```yaml
   - pattern: "^[pattern].*$"
     orchestrator: [name]_orchestrator
     confidence: 1.0
     match_type: regex
     priority: [number]
     metadata:
       description: "[Description]"
       autonomous: false  # GUIDED execution
   ```

2. **Manifest Updates:** [List any improvements to existing manifests]

3. **Documentation:** [Clarify usage, add examples]

---

## 📊 Risk Assessment

### Risks of Converting to AUTONOMOUS

**Technical Risks:**
- [Risk 1: description, mitigation]
- [Risk 2: description, mitigation]

**Resource Risks:**
- Development time: [X days investment]
- Testing complexity: [Description]

**Maintenance Risks:**
- [Risk 1: description, mitigation]

### Risks of Remaining GUIDED

**Technical Risks:**
- [Risk 1: description, mitigation]
- [Risk 2: description, mitigation]

**Operational Risks:**
- [Risk 1: description, mitigation]

---

## 📝 Additional Notes

[Any additional context, considerations, or observations that don't fit above categories]

---

## ✅ Approval

**Evaluator:** [Name]  
**Date:** [Date]  
**Status:** [Pending Review / Approved / Rejected]

**Reviewer:** [Name]  
**Review Date:** [Date]  
**Decision:** [Approved for AUTONOMOUS / Remain GUIDED / Requires Further Analysis]

**Comments:**
[Reviewer feedback]
