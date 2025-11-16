# CORTEX DoD/DoR Workflow Demo - Quick Reference

## What This Demo Shows

Demonstrates how CORTEX integrates user-provided **Definition of Done (DoD)**, **Definition of Ready (DoR)**, and **Acceptance Criteria** into its multi-agent development workflow.

## Key Concepts Demonstrated

### 1. Definition of Ready (DoR) - Rule #21
**Entry Gate (RIGHT BRAIN)**
- Validates user-provided DoR completeness
- Skips interactive wizard when criteria complete
- Creates work package from user criteria

### 2. Work Planner Enhancement
**Strategic Planning**
- Maps acceptance criteria to implementation phases
- Breaks work into manageable tasks
- Estimates effort automatically

### 3. Test Generation
**TDD Integration**
- Converts AC scenarios to test methods
- Creates failing tests (RED phase)
- Ensures requirements are testable

### 4. Definition of Done (DoD) - Rule #20
**Exit Gate (LEFT BRAIN)**
- Enforces user's specific quality criteria
- Blocks commits if DoD not met
- Reports validation against user requirements

## Running the Demo

### Standalone Execution

```powershell
# From CORTEX root directory
cd d:\PROJECTS\CORTEX
python examples\demo_dod_dor_workflow.py
```

### As Part of CORTEX Tutorial

```
# In GitHub Copilot Chat or natural language
"run cortex demo developer profile"
```

Or via operations API:
```python
from src.operations.orchestrator import Orchestrator

orchestrator = Orchestrator()
result = orchestrator.execute_operation(
    operation_name="cortex_tutorial",
    profile="developer"  # Includes DoD/DoR demo
)
```

## Demo Profiles

| Profile | Duration | Includes DoD/DoR Demo |
|---------|----------|-----------------------|
| **quick** | 2 min | ❌ No |
| **standard** | 3-4 min | ❌ No |
| **comprehensive** | 5-6 min | ❌ No |
| **developer** | 8-10 min | ✅ **Yes** |

## Example Scenario Used in Demo

**User Request:**
> "Add invoice PDF export feature"

**User Provides:**

**DoR:**
- User Story: "As an admin, I want to export invoices as PDF"
- Acceptance Criteria:
  - AC1: User clicks export → PDF generates with logo
  - AC2: Export handles invalid invoice ID gracefully
  - AC3: Bulk export supports up to 100 invoices
- Dependencies: iTextSharp library
- Estimate: 6 hours

**DoD:**
- All 3 AC tests pass
- Code coverage ≥85%
- PDF validates against PDF/A standard
- Documentation updated

**CORTEX Processing:**

1. **DoR Validation** → ✅ Complete (all criteria met)
2. **Phase Planning** → 3 phases generated (2h each)
3. **Test Generation** → 3 test methods created
4. **DoD Enforcement** → 4 quality gates enforced

## Demo Output Preview

```
═══════════════════════════════════════════════════════════
🧠 CORTEX Demo: DoD/DoR Workflow Integration
═══════════════════════════════════════════════════════════

📝 STEP 1: User Provides Quality Criteria
   User Request: "Add invoice PDF export feature"
   DoR: ✓ Complete (3 AC scenarios, dependencies, estimate)
   DoD: ✓ Defined (4 quality gates)

🧠 STEP 2: RIGHT BRAIN - DoR Validation (Rule #21)
   Status: ✅ COMPLETE
   Decision: Skip wizard, create work package

🎯 STEP 3: Work Planner Analyzes AC
   AC1 → Phase 1: Core PDF Generation (2h)
   AC2 → Phase 2: Error Handling (2h)
   AC3 → Phase 3: Bulk Export (2h)

[... continues through 7 steps ...]

🎉 STEP 7: Demo Summary
   Key Takeaways: DoR validation, AC mapping, DoD enforcement
   Benefits: Faster execution, consistent quality, pattern learning
```

## Integration Points

**Related CORTEX Components:**

| Component | File | Purpose |
|-----------|------|---------|
| **Governance Rules** | `src/tier0/governance.yaml` | DoD/DoR rule definitions |
| **Validation Engine** | `src/tier0/governance_engine.py` | DoD/DoR validation methods |
| **Workflow Stage** | `src/workflows/stages/dod_dor_clarifier.py` | Interactive clarification |
| **Protection Layers** | `cortex-brain/protection-layers/*.yaml` | Enforcement rules |
| **Work Planner Agent** | `cortex-brain/agents/work-planner.md` | RIGHT BRAIN strategic planning |
| **Health Validator** | `cortex-brain/agents/health-validator.md` | LEFT BRAIN quality validation |

## Learning Resources

After running the demo, explore:

1. **Rule #21 (DoR):** `src/tier0/governance.yaml` lines 115-145
2. **Rule #20 (DoD):** `src/tier0/governance.yaml` lines 86-114
3. **DoD/DoR Clarifier:** `src/workflows/stages/dod_dor_clarifier.py`
4. **Governance Engine:** `src/tier0/governance_engine.py`
   - `validate_definition_of_ready()` method
   - `validate_definition_of_done()` method

## Next Steps After Demo

1. Try providing DoD/DoR/AC with your next feature request
2. Review governance rules in detail
3. Explore workflow stage implementation
4. Test with your own acceptance criteria
5. Customize DoD criteria for your team standards

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Created:** November 16, 2025  
**Demo Duration:** ~2 minutes  
**Demo Type:** Interactive, Automated
