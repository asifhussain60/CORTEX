# Layer 8: Test Location Isolation Rule

**Version:** 1.0  
**Created:** 2025-11-24  
**Author:** Asif Hussain  
**Type:** Brain Protection Rule (Tier 0 Instinct)  
**Status:** ✅ IMPLEMENTED

---

## 🎯 Purpose

Enforce strict separation between application tests and CORTEX tests while enabling brain learning from user patterns.

---

## 📜 The Rule

**TEST_LOCATION_SEPARATION (Tier 0 Instinct)**

When CORTEX is running in development environments:
- **Application tests** → ALWAYS created in user repository
- **CORTEX tests** → ALWAYS stay in CORTEX folder
- **Brain learning** → Enabled from both, storing patterns (not code)

---

## 🏗️ Architecture

### Test Location Detection Flow

```
Source File Analyzed
    ↓
Is file within CORTEX folder?
    ↓ YES → Tests go to CORTEX/tests/
    ↓ NO  → Tests go to user_repo/tests/
    ↓
Detect user's test framework
    ↓
Follow user's conventions
    ↓
Generate tests in correct location
    ↓
Capture patterns → Brain (Tier 2)
```

### Brain Learning Without Code Pollution

**What Gets Stored:**
- ✅ Framework choice (pytest, jest, xunit, etc.)
- ✅ Naming conventions (test_*.py, *_test.js, etc.)
- ✅ Common patterns (fixtures, mocks, parametrization)
- ✅ Failure insights (DB seeding, API mocking, etc.)
- ✅ Performance patterns (slow tests, bottlenecks)

**What Does NOT Get Stored:**
- ❌ Actual test code
- ❌ Business logic
- ❌ Application-specific details
- ❌ User's intellectual property

---

## 🔧 Implementation

### 1. Brain Protection Rules (`cortex-brain/brain-protection-rules.yaml`)

**Added:**
- Tier 0 instinct: `TEST_LOCATION_SEPARATION`
- Layer 8: Test Location Isolation
- Detection patterns for wrong test locations
- Alternatives for proper test placement
- Evidence template for violations

**Key Changes:**
```yaml
rules:
  total_count: 39  # +1 test location rule
  layers: 15  # +Layer 8

tier0_instincts:
  - "TEST_LOCATION_SEPARATION"  # NEW

protection_layers:
  - layer_id: "test_location_isolation"
    name: "Test Location Isolation"
    priority: 8
```

### 2. TDD Workflow Orchestrator (`src/workflows/tdd_workflow_orchestrator.py`)

**Added Configuration:**
```python
@dataclass
class TDDWorkflowConfig:
    # Layer 8: Test Location Isolation
    user_repo_root: Optional[str] = None
    is_cortex_test: bool = False
    auto_detect_test_location: bool = True
    enable_brain_learning: bool = True
```

**Added Methods:**
1. `_detect_test_location(source_file: str) -> Path`
   - Detects if source is CORTEX or user code
   - Returns appropriate test directory
   - Auto-detects user repo root

2. `_find_user_repo_root(source_path: Path) -> Path`
   - Finds repository root by markers
   - Looks for .git, package.json, requirements.txt, etc.
   - Falls back to source file's parent

3. `_capture_test_patterns_to_brain(test_file, framework, patterns)`
   - Captures generalized patterns from user tests
   - Stores in Tier 2 knowledge graph
   - Flags as user code (not CORTEX)

### 3. CORTEX Prompt (``.github/prompts/CORTEX.prompt.md`)

**Added:**
- Feature bullet in TDD Mastery section
- Configuration options for Layer 8
- Dedicated "Test Location Isolation" section with:
  - Rule explanation
  - Auto-detection workflow
  - Example scenarios
  - Brain learning details
  - Benefits

---

## 📊 Detection Patterns

### Trigger Conditions

**Combined Keywords:**
```yaml
test_generation:
  - "generate test"
  - "create test"
  - "write test"
  - "tdd workflow"

application_code:
  - "user application"
  - "user code"
  - "application feature"
  - "business logic"

wrong_location:
  - "tests/fixtures"
  - "CORTEX/tests"
  - "cortex-brain/tests"
```

**Detection Logic:** AND (all three groups must match)

---

## ✅ Validation

### Example Scenarios

#### Scenario 1: User Application Test ✅
```
Source: /Users/user/myapp/src/payment.py
Test:   /Users/user/myapp/tests/test_payment.py
Framework: pytest (detected from requirements.txt)
Brain: "User prefers mock stripe API" → Tier 2
```

#### Scenario 2: CORTEX Infrastructure Test ✅
```
Source: /CORTEX/src/tier0/brain_protector.py
Test:   /CORTEX/tests/test_brain_protector.py
Framework: pytest (CORTEX standard)
Brain: "Brain protection rule validation" → Tier 2
```

#### Scenario 3: Violation ❌
```
Source: /Users/user/myapp/src/feature.py
Test:   /CORTEX/tests/test_feature.py  ← WRONG!
Blocked: Layer 8 protection triggered
Alternative: Create at /Users/user/myapp/tests/test_feature.py
```

---

## 🧠 Brain Learning Mechanism

### Tier 2 Knowledge Graph Storage

**Pattern Structure:**
```python
{
    "pattern_id": "test_framework_usage_{session_id}",
    "title": "Test Pattern: pytest in user repo",
    "content": "User prefers pytest with patterns: fixtures, parametrize, mocks",
    "pattern_type": "test_framework_usage",
    "confidence": 0.9,
    "metadata": {
        "framework": "pytest",
        "patterns": {
            "fixtures": "User defines conftest.py with db fixture",
            "parametrize": "Used for edge cases in payment tests",
            "mocks": "Mock stripe API with responses library"
        },
        "session_id": "tdd_abc123",
        "timestamp": "2025-11-24T10:00:00",
        "is_user_code": true  # Flag to avoid CORTEX pollution
    },
    "namespaces": ["workspace.tdd.abc123"]
}
```

### Learning Categories

1. **Framework Detection**
   - Which test framework user prefers
   - Version compatibility requirements
   - Plugin usage patterns

2. **Naming Conventions**
   - File naming patterns (test_*.py vs *_test.py)
   - Directory structure preferences
   - Module organization patterns

3. **Test Patterns**
   - Fixture usage (setup/teardown)
   - Parametrization strategies
   - Mock/stub patterns
   - Assertion styles

4. **Failure Insights**
   - Common setup issues
   - Environment dependencies
   - Data seeding requirements
   - API mocking needs

5. **Performance Patterns**
   - Slow test identification
   - Parallelization opportunities
   - Resource cleanup issues

---

## 🎯 Benefits

### For Users
- ✅ Tests stay in their own repository
- ✅ Self-contained project structure
- ✅ No CORTEX pollution in their codebase
- ✅ Framework choice honored
- ✅ Conventions followed automatically

### For CORTEX
- ✅ Clean separation of concerns
- ✅ Brain learns from diverse patterns
- ✅ No intellectual property concerns
- ✅ Focused CORTEX test suite
- ✅ Better pattern generalization

### For Development
- ✅ Reduced confusion about test locations
- ✅ Automatic framework detection
- ✅ Context-aware test generation
- ✅ Progressive learning from usage
- ✅ Improved test quality over time

---

## 🔄 Integration with Existing Systems

### Brain Protection Agent
- Monitors test generation operations
- Validates test file paths
- Triggers Layer 8 challenge when violated
- Suggests correct alternatives

### TDD Workflow Orchestrator
- Calls `_detect_test_location()` before test generation
- Determines user repo vs CORTEX context
- Configures test generator with correct paths
- Triggers brain learning after test creation

### Knowledge Graph (Tier 2)
- Receives pattern captures
- Stores generalized insights
- Flags user code patterns
- Enables future test generation improvements

### Session Manager (Tier 1)
- Tracks test generation sessions
- Links tests to workspace context
- Stores test execution results
- Maintains session continuity

---

## 📝 Future Enhancements

### Phase 2: Advanced Framework Support
- [ ] Multi-framework projects (pytest + jest)
- [ ] Framework-specific pattern capture
- [ ] Version-specific feature detection
- [ ] Plugin ecosystem learning

### Phase 3: Intelligent Recommendations
- [ ] "Your tests suggest adding pytest-cov"
- [ ] "Consider parametrizing these similar tests"
- [ ] "Your fixture pattern matches best practice X"
- [ ] "Common failure: Add DB migration before tests"

### Phase 4: Cross-Project Learning
- [ ] Aggregate patterns across all user projects
- [ ] Industry-standard pattern library
- [ ] Framework comparison insights
- [ ] Best practice evolution tracking

---

## 📚 References

**Modified Files:**
- `cortex-brain/brain-protection-rules.yaml` (Layer 8 added)
- `src/workflows/tdd_workflow_orchestrator.py` (Detection + capture methods)
- `.github/prompts/CORTEX.prompt.md` (Documentation + examples)

**Related Documents:**
- `cortex-brain/documents/implementation-guides/TDD-MASTERY-INTEGRATION-PLAN.md`
- `cortex-brain/documents/reports/TDD-MASTERY-PHASE*.md`
- `cortex-brain/brain-protection-rules.yaml` (Layer 1-7)

**Brain Components:**
- Tier 0: Brain Protection Agent (enforcement)
- Tier 1: Session Manager (tracking)
- Tier 2: Knowledge Graph (learning)

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
