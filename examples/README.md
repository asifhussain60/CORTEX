# CORTEX Examples

Interactive demonstrations and examples showcasing CORTEX capabilities.

## Available Demos

### 1. DoD/DoR Workflow Integration Demo

**File:** `demo_dod_dor_workflow.py`

**Purpose:** Demonstrates how CORTEX processes user-provided Definition of Done (DoD), Definition of Ready (DoR), and Acceptance Criteria through the multi-agent workflow.

**What It Shows:**
- ✅ DoR Validation (Rule #21) by RIGHT BRAIN Work Planner
- ✅ Planning Enhancement - Structuring implementation from AC
- ✅ AC-to-Test Mapping - Converting scenarios to test methods
- ✅ DoD Enforcement (Rule #20) by LEFT BRAIN Health Validator

**How to Run:**

```powershell
# From CORTEX root directory
python examples/demo_dod_dor_workflow.py
```

**Demo Flow:**
1. **Step 1:** User provides DoD, DoR, and acceptance criteria
2. **Step 2:** Work Planner validates DoR completeness
3. **Step 3:** Work Planner analyzes AC for implementation phases
4. **Step 4:** Structured work package generated
5. **Step 5:** AC converted to TDD test methods
6. **Step 6:** DoD enforcement at pre-commit validation
7. **Step 7:** Summary of benefits and next steps

**Duration:** ~2 minutes (automated with pauses)

**Integration:** This demo is included in the "developer" profile of the main CORTEX tutorial:

```yaml
# In cortex-operations.yaml
cortex_tutorial:
  profiles:
    developer:
      description: Development workflow deep-dive (8-10 minutes)
      modules:
        - demo_introduction
        - demo_help_system
        - demo_dod_dor_workflow  # ← This demo
        - demo_story_refresh
        - demo_cleanup
        - demo_conversation
        - demo_completion
```

**Related Files:**
- `src/tier0/governance.yaml` - Rules #20 (DoD) and #21 (DoR)
- `src/tier0/governance_engine.py` - Validation methods
- `src/workflows/stages/dod_dor_clarifier.py` - Workflow stage implementation
- `cortex-brain/protection-layers/layer-instinct-immutability.yaml` - Enforcement rules

---

### 2. Feature 5.3 Demo

**File:** `feature_5_3_demo.py`

Demonstrates CORTEX 5.3 features including interactive planning and work planner integration.

---

### 3. Smart Hints Integration

**File:** `smart_hints_integration.py`

Shows how CORTEX provides contextual learning opportunities during conversations.

---

## Creating New Demos

When creating new demonstration files:

1. **Naming Convention:** `demo_<feature_name>.py`
2. **Location:** Place in `examples/` directory
3. **Structure:** Include clear steps with pauses for readability
4. **Documentation:** Add entry to this README
5. **Integration:** Add to `cortex-operations.yaml` if part of main tutorial

**Template Structure:**
```python
"""
CORTEX Demo: <Feature Name>
===========================

Brief description of what this demo showcases.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

class FeatureDemo:
    def run_demo(self) -> None:
        """Execute the complete demonstration."""
        self._step_1_introduction()
        self._step_2_main_feature()
        self._step_3_summary()
    
    def _pause_for_demo(self, delay: float = 2.0) -> None:
        """Pause briefly for demo effect."""
        import time
        time.sleep(delay)

if __name__ == "__main__":
    demo = FeatureDemo()
    demo.run_demo()
```

---

## Demo Best Practices

✅ **Clear Introduction:** Explain what will be demonstrated
✅ **Step-by-Step:** Break into logical, numbered steps
✅ **Visual Separators:** Use borders for section clarity
✅ **Realistic Examples:** Use practical, real-world scenarios
✅ **Timed Pauses:** Allow time to read each section
✅ **Summary:** Recap key takeaways and next steps
✅ **Error Handling:** Gracefully handle interruptions (Ctrl+C)

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file for terms
