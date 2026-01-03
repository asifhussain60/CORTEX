# Decision Matrix: AUTONOMOUS vs GUIDED Orchestrators

**Version:** 1.0  
**Created:** January 3, 2026  
**Purpose:** Objective framework for determining optimal orchestrator implementation approach

---

## 📊 Decision Criteria & Weighting

| Criterion | Weight | Rationale |
|-----------|--------|-----------|
| **Operation Complexity** | 30% | High complexity (AST manipulation, multi-phase workflows) benefits from Python's rich ecosystem |
| **State Management** | 25% | Multi-phase workflows with rollback requirements need transactional database state |
| **User Interaction** | 20% | High interactivity may favor GUIDED's tool call sequences |
| **Maintenance Cost** | 15% | Python code is easier to maintain/debug than manifest YAML |
| **Code Reusability** | 10% | Shared utilities and libraries favor AUTONOMOUS implementation |

**Decision Threshold:** Score ≥7.0 → AUTONOMOUS | Score <7.0 → GUIDED

---

## 🎯 Scoring Rubric

### 1. Operation Complexity (Weight: 30%)

| Score | Description | AUTONOMOUS Fit | GUIDED Fit |
|-------|-------------|----------------|------------|
| 10 | Very High: AST parsing, multi-file refactoring, complex algorithms | ✅ Excellent | ❌ Poor |
| 7-9 | High: Multi-phase workflows, regex patterns, validation logic | ✅ Good | 🟡 Acceptable |
| 4-6 | Medium: File operations, simple transformations | 🟡 Acceptable | ✅ Good |
| 1-3 | Low: Linear workflows, simple file reads/writes | ❌ Overkill | ✅ Excellent |

**AUTONOMOUS Score Calculation:**
- AST manipulation: +3 points
- Multi-phase workflow (≥3 phases): +2 points
- Complex algorithms (regex, graph analysis): +2 points
- Multi-file analysis: +2 points
- Simple operations: +1 point

### 2. State Management (Weight: 25%)

| Score | Description | AUTONOMOUS Fit | GUIDED Fit |
|-------|-------------|----------------|------------|
| 10 | Critical: Multi-phase with rollback, transaction boundaries | ✅ Excellent | ❌ Poor |
| 7-9 | Important: Progress tracking across phases | ✅ Good | 🟡 Acceptable |
| 4-6 | Moderate: Simple state tracking | 🟡 Acceptable | ✅ Good |
| 1-3 | Minimal: Stateless operations | ❌ Overkill | ✅ Excellent |

**AUTONOMOUS Score Calculation:**
- Requires rollback: +4 points
- Multi-phase state (≥3 phases): +3 points
- Progress persistence needed: +2 points
- Simple state tracking: +1 point
- Stateless: 0 points

### 3. User Interaction (Weight: 20%)

| Score | Description | AUTONOMOUS Fit | GUIDED Fit |
|-------|-------------|----------------|------------|
| 10 | Fully Automated: No user input needed | ✅ Excellent | 🟡 Acceptable |
| 7-9 | Minimal Interaction: 1-2 approval gates | ✅ Good | ✅ Good |
| 4-6 | Moderate Interaction: Iterative refinement | 🟡 Acceptable | ✅ Good |
| 1-3 | High Interaction: Conversational, exploratory | ❌ Poor | ✅ Excellent |

**AUTONOMOUS Score Calculation:**
- Fully automated: +10 points
- 1-2 approval gates: +8 points
- 3-5 approval gates: +6 points
- Iterative/conversational: +3 points

### 4. Maintenance Cost (Weight: 15%)

| Score | Description | AUTONOMOUS Fit | GUIDED Fit |
|-------|-------------|----------------|------------|
| 10 | Complex Logic: Benefits from IDE support, debugging, unit tests | ✅ Excellent | ❌ Poor |
| 7-9 | Moderate Logic: Some complexity, regular updates | ✅ Good | 🟡 Acceptable |
| 4-6 | Simple Logic: Straightforward workflows | 🟡 Acceptable | ✅ Good |
| 1-3 | Minimal Logic: Rarely changes | ❌ Overkill | ✅ Excellent |

**AUTONOMOUS Score Calculation:**
- Complex business logic: +10 points
- Regular updates expected: +8 points
- Moderate complexity: +6 points
- Simple, stable logic: +3 points

### 5. Code Reusability (Weight: 10%)

| Score | Description | AUTONOMOUS Fit | GUIDED Fit |
|-------|-------------|----------------|------------|
| 10 | High: Shared utilities, libraries, patterns used by multiple orchestrators | ✅ Excellent | ❌ Poor |
| 7-9 | Moderate: Some reusable components | ✅ Good | 🟡 Acceptable |
| 4-6 | Low: Mostly unique logic | 🟡 Acceptable | ✅ Good |
| 1-3 | None: One-off implementation | ❌ Overkill | ✅ Excellent |

**AUTONOMOUS Score Calculation:**
- Shared by 3+ orchestrators: +10 points
- Shared by 2 orchestrators: +7 points
- Potential for reuse: +5 points
- Unique implementation: +2 points

---

## 📐 Scoring Formula

```
Final Score = (Operation Complexity × 0.30) + 
              (State Management × 0.25) + 
              (User Interaction × 0.20) + 
              (Maintenance Cost × 0.15) + 
              (Code Reusability × 0.10)
```

**Decision Rules:**
- **Score ≥ 8.0:** STRONG AUTONOMOUS recommendation
- **Score 7.0-7.9:** AUTONOMOUS recommendation
- **Score 6.0-6.9:** NEUTRAL (consider other factors)
- **Score 5.0-5.9:** GUIDED recommendation
- **Score < 5.0:** STRONG GUIDED recommendation

---

## 🔍 Additional Considerations (Tiebreakers)

When scores fall in NEUTRAL range (6.0-6.9), consider:

1. **Development Effort:** Autonomous conversion typically requires 2-4 days
2. **Master Orchestrator Integration:** Autonomous orchestrators integrate more naturally
3. **Testing Requirements:** Autonomous code has 100% test coverage requirement
4. **Team Expertise:** Python vs YAML manifest expertise
5. **Strategic Alignment:** Does this orchestrator represent core CORTEX capability?

---

## 📋 Application Examples

### Example 1: TDD Orchestrator (Already Approved)

| Criterion | Raw Score | Weighted Score | Rationale |
|-----------|-----------|----------------|-----------|
| Operation Complexity | 9 | 2.70 | Multi-phase (RED→GREEN→REFACTOR), test framework integration |
| State Management | 10 | 2.50 | Critical rollback needs, transaction boundaries |
| User Interaction | 8 | 1.60 | 1-2 approval gates after GREEN phase |
| Maintenance Cost | 9 | 1.35 | Complex test execution logic, regular updates |
| Code Reusability | 7 | 0.70 | Test runner abstraction reusable by other orchestrators |
| **TOTAL** | **43/50** | **8.85** | **✅ STRONG AUTONOMOUS** |

**Decision:** ✅ APPROVED for AUTONOMOUS conversion (January 2, 2026)

### Example 2: Simple File Copy Orchestrator (Hypothetical)

| Criterion | Raw Score | Weighted Score | Rationale |
|-----------|-----------|----------------|-----------|
| Operation Complexity | 2 | 0.60 | Simple file copy operations |
| State Management | 1 | 0.25 | Stateless operation |
| User Interaction | 9 | 1.80 | Fully automated |
| Maintenance Cost | 3 | 0.45 | Rarely changes |
| Code Reusability | 2 | 0.20 | Unique implementation |
| **TOTAL** | **17/50** | **3.30** | **❌ STRONG GUIDED** |

**Decision:** ❌ Keep GUIDED - simple operations don't justify autonomous complexity

---

## 🎯 Summary

This decision matrix provides:
- **Objective criteria** for AUTONOMOUS vs GUIDED decisions
- **Weighted scoring** reflecting relative importance
- **Clear thresholds** for decision-making
- **Tiebreaker guidance** for edge cases

**Usage:** Apply this matrix to each GUIDED orchestrator (Debug, Sanitization, Refinement) in subsequent assessment phases.
