# Governance Onboarding System

**Module:** `OnboardingAcknowledgmentOrchestrator`  
**Purpose:** First-time governance acknowledgment with 3-step progressive disclosure  
**Author:** Asif Hussain  
**Status:** ✅ Production Ready

---

## 📋 Overview

The Governance Onboarding System ensures first-time CORTEX users understand and explicitly acknowledge the governance framework before using the system. This creates informed consent and sets proper expectations.

### Why Onboarding Matters

**Without governance acknowledgment:**
- ❌ Users may be surprised by TDD enforcement
- ❌ Git checkpoints happen without context
- ❌ Compliance dashboard appears unexpectedly
- ❌ No explicit consent to governed workflow

**With governance onboarding:**
- ✅ Users understand CORTEX approach upfront
- ✅ Explicit acknowledgment creates accountability
- ✅ Expectations are set properly
- ✅ One-time process (never repeated)

---

## 🏗️ Architecture

### 3-Step Progressive Disclosure

```
Step 1: Welcome & Introduction (30 seconds)
   ↓
Step 2: Rulebook Overview (60 seconds)
   ↓
Step 3: Explicit Acknowledgment (30 seconds)
   ↓
Onboarding Complete (recorded in Tier 1)
```

### Integration Points

1. **UnifiedEntryPointOrchestrator** - Checks if user needs onboarding
2. **UserProfileGovernance** - Stores acknowledgment status
3. **WelcomeBannerAgent** - Shows welcome per session (different from onboarding)
4. **Response Templates** - Pre-formatted content for each step

---

## 🚀 Quick Start

### For Users

**First-time experience:**
```
User: "help" (or any command)
CORTEX: [Shows Step 1 - Welcome & Introduction]

User: "next"
CORTEX: [Shows Step 2 - Rulebook Overview]

User: "I acknowledge"
CORTEX: [Records acknowledgment, shows completion]

User: [Never sees onboarding again]
```

### For Developers

**Check if user needs onboarding:**
```python
from src.orchestrators.onboarding_acknowledgment_orchestrator import OnboardingAcknowledgmentOrchestrator

orchestrator = OnboardingAcknowledgmentOrchestrator()

if orchestrator.needs_onboarding():
    # Show Step 1
    step1 = orchestrator.execute_step_1_welcome()
    # Return step1["content"] to user
```

**Record acknowledgment:**
```python
result = orchestrator.record_acknowledgment()

if result["success"]:
    # Acknowledgment recorded
    # User won't see onboarding again
    print(result["content"])
```

---

## 📊 Step-by-Step Guide

### Step 1: Welcome & Introduction

**Purpose:** Introduce CORTEX governance approach and set expectations

**Key Topics:**
- What makes CORTEX different (governed AI assistant)
- Why governance matters (quality, safety, compliance)
- What happens next (3-step process)

**Duration:** ~30 seconds reading time

**Progression:** User says "next" or "continue" to proceed to Step 2

**Implementation:**
```python
step1 = orchestrator.execute_step_1_welcome()

# Returns:
# {
#     "step": 1,
#     "title": "Welcome & Introduction",
#     "content": "...",  # Markdown content
#     "next_step": "rulebook",
#     "progress": "1/3"
# }
```

---

### Step 2: Rulebook Overview

**Purpose:** Explain the 7 core protection layers and key commands

**7 Protection Layers:**
1. **Definition of Ready (DoR)** - Requirements validation before work
2. **Definition of Done (DoD)** - Completion criteria enforcement
3. **TDD Enforcement** - RED→GREEN→REFACTOR workflow
4. **Git Checkpoint System** - Automatic rollback points
5. **SOLID Principles** - Code design standards
6. **Security Standards (OWASP)** - Security by design
7. **Brain Integrity** - Knowledge validation

**Duration:** ~60 seconds reading time

**Progression:** User says "acknowledge" or "I understand" to proceed to Step 3

**Implementation:**
```python
step2 = orchestrator.execute_step_2_rulebook()

# Returns:
# {
#     "step": 2,
#     "title": "Rulebook Overview",
#     "content": "...",  # Markdown with 7 layers
#     "next_step": "acknowledgment",
#     "progress": "2/3"
# }
```

---

### Step 3: Explicit Acknowledgment

**Purpose:** Request confirmation of understanding and record consent

**User Confirms:**
- ✅ Understands CORTEX operates under governance rules
- ✅ Agrees to follow DoR/DoD workflows
- ✅ Will use compliance dashboard
- ✅ Knows how to access rulebook and help

**Acknowledgment Phrases:**
- "I acknowledge"
- "I understand and agree"
- "acknowledged"
- "confirm"

**Duration:** ~30 seconds

**Implementation:**
```python
step3 = orchestrator.execute_step_3_acknowledgment()

# Show content to user

# When user acknowledges:
result = orchestrator.record_acknowledgment()

# Returns:
# {
#     "success": True,
#     "message": "Onboarding completed successfully",
#     "content": "...",  # Completion message
#     "acknowledged_at": "2025-11-30T04:52:00"
# }
```

---

## 🔧 API Reference

### Class: OnboardingAcknowledgmentOrchestrator

```python
class OnboardingAcknowledgmentOrchestrator:
    """3-step governance acknowledgment orchestrator."""
    
    def __init__(self, db_path: Optional[str] = None)
    def needs_onboarding(self) -> bool
    def get_onboarding_status(self) -> Dict[str, Any]
    def execute_step_1_welcome(self) -> Dict[str, Any]
    def execute_step_2_rulebook(self) -> Dict[str, Any]
    def execute_step_3_acknowledgment(self) -> Dict[str, Any]
    def record_acknowledgment(self) -> Dict[str, Any]
    def get_current_step(self) -> OnboardingStep
    def reset_onboarding(self) -> bool
```

### Method Details

#### `needs_onboarding() -> bool`

Checks if user has acknowledged rulebook.

**Returns:** `True` if user needs onboarding, `False` if already acknowledged

**Example:**
```python
if orchestrator.needs_onboarding():
    # Show onboarding
else:
    # Proceed to command execution
```

---

#### `get_onboarding_status() -> Dict[str, Any]`

Gets detailed acknowledgment status.

**Returns:**
```python
{
    "acknowledged_rulebook": bool,
    "acknowledged_at": Optional[str],  # ISO format timestamp
    "onboarding_completed": bool
}
```

---

#### `execute_step_1_welcome() -> Dict[str, Any]`

Executes Step 1: Welcome & Introduction.

**Returns:**
```python
{
    "step": 1,
    "title": "Welcome & Introduction",
    "content": str,  # Markdown content
    "next_step": "rulebook",
    "progress": "1/3"
}
```

**Side Effect:** Sets `current_step` to `OnboardingStep.RULEBOOK`

---

#### `execute_step_2_rulebook() -> Dict[str, Any]`

Executes Step 2: Rulebook Overview.

**Returns:**
```python
{
    "step": 2,
    "title": "Rulebook Overview",
    "content": str,  # Markdown with 7 layers
    "next_step": "acknowledgment",
    "progress": "2/3"
}
```

**Side Effect:** Sets `current_step` to `OnboardingStep.ACKNOWLEDGMENT`

---

#### `execute_step_3_acknowledgment() -> Dict[str, Any]`

Executes Step 3: Acknowledgment.

**Returns:**
```python
{
    "step": 3,
    "title": "Acknowledgment & Completion",
    "content": str,  # Acknowledgment prompt
    "next_step": "complete",
    "progress": "3/3"
}
```

**Side Effect:** Sets `current_step` to `OnboardingStep.COMPLETE`

---

#### `record_acknowledgment() -> Dict[str, Any]`

Records user's acknowledgment and completes onboarding.

**Returns:**
```python
{
    "success": bool,
    "message": str,
    "content": str,  # Completion message
    "acknowledged_at": str  # ISO timestamp
}
```

**Side Effects:**
- Writes acknowledgment to Tier 1 database
- Sets `acknowledged_rulebook = 1`
- Sets `acknowledged_at = NOW()`
- User won't see onboarding again

---

#### `get_current_step() -> OnboardingStep`

Gets the current onboarding step.

**Returns:** `OnboardingStep` enum value

**Enum Values:**
- `OnboardingStep.WELCOME` - Step 1
- `OnboardingStep.RULEBOOK` - Step 2
- `OnboardingStep.ACKNOWLEDGMENT` - Step 3
- `OnboardingStep.COMPLETE` - All done

---

#### `reset_onboarding() -> bool`

Resets onboarding status (for testing or re-onboarding).

**Returns:** `True` if successful

**Use Cases:**
- Unit testing
- User requests re-onboarding
- Admin reset

---

## 🧪 Testing

### Test Suite

Location: `tests/orchestrators/test_onboarding_acknowledgment_orchestrator.py`

**Coverage:** 95%+ (all critical paths)

### Key Test Cases

1. **Initialization** - Orchestrator initializes correctly
2. **Needs Onboarding** - New users need onboarding, returning users don't
3. **Step Execution** - All 3 steps execute with correct content
4. **Acknowledgment Recording** - Acknowledgment persists
5. **Full Workflow** - Complete end-to-end flow
6. **Content Quality** - All key topics covered
7. **Step Isolation** - Steps can be executed independently
8. **Reset Functionality** - Onboarding can be reset

### Running Tests

```bash
# Run all onboarding tests
pytest tests/orchestrators/test_onboarding_acknowledgment_orchestrator.py -v

# Run with coverage
pytest tests/orchestrators/test_onboarding_acknowledgment_orchestrator.py --cov=src.orchestrators.onboarding_acknowledgment_orchestrator

# Run specific test
pytest tests/orchestrators/test_onboarding_acknowledgment_orchestrator.py::TestOnboardingAcknowledgmentOrchestrator::test_full_workflow -v
```

---

## 🔗 Integration

### Response Templates

Location: `cortex-brain/response-templates.yaml`

**Templates:**
- `governance_onboarding_step1` - Welcome content
- `governance_onboarding_step2` - Rulebook content
- `governance_onboarding_step3` - Acknowledgment prompt
- `governance_onboarding_complete` - Completion message

**Triggers:**
```yaml
governance_onboarding_step1:
  triggers:
    - start governance onboarding
    - first time setup
  expected_orchestrator: OnboardingAcknowledgmentOrchestrator

governance_onboarding_step3:
  triggers:
    - i acknowledge
    - i understand and agree
    - acknowledged
    - confirm acknowledgment
  expected_orchestrator: OnboardingAcknowledgmentOrchestrator
```

---

### UnifiedEntryPointOrchestrator Integration

**Workflow:**
```python
# UnifiedEntryPointOrchestrator checks on every request
onboarding_orch = OnboardingAcknowledgmentOrchestrator()

if onboarding_orch.needs_onboarding():
    # Show Step 1
    return onboarding_orch.execute_step_1_welcome()

# Otherwise proceed with command execution
```

---

### UserProfileGovernance Integration

**Database:** `cortex-brain/tier1/working_memory.db`

**Table:** `user_profile`

**Fields:**
- `acknowledged_rulebook` (INTEGER) - 0=no, 1=yes
- `acknowledged_at` (TEXT) - ISO timestamp
- `onboarding_completed` (INTEGER) - 0=no, 1=yes

---

## 📈 Metrics & Monitoring

### Success Metrics

1. **Completion Rate** - % of users who complete onboarding
2. **Time to Complete** - Average time from Step 1 to acknowledgment
3. **Skip Rate** - % of users who bypass (should be 0%)
4. **Re-engagement** - Users who return after onboarding

### Logging

```python
logger.info("OnboardingAcknowledgmentOrchestrator initialized")
logger.info(f"User needs onboarding: {needs_onboarding}")
logger.info(f"Step executed: {current_step}")
logger.info(f"Acknowledgment recorded at {acknowledged_at}")
```

---

## 🚨 Troubleshooting

### User skips onboarding

**Problem:** User closes window or ignores steps

**Solution:** Onboarding re-appears on next command until acknowledged

---

### User wants to review rulebook after onboarding

**Problem:** User completed onboarding but wants to see rulebook again

**Solution:** Use `show rules` command (always available)

---

### User regrets acknowledgment

**Problem:** User wants to re-read onboarding

**Solution:** Admin can reset: `orchestrator.reset_onboarding()`

---

### Database write fails

**Problem:** Acknowledgment not persisting

**Solution:**
1. Check database permissions
2. Verify `cortex-brain/tier1/working_memory.db` exists
3. Check disk space
4. Review logs for SQL errors

---

## 🎯 Best Practices

### Content Updates

**When updating onboarding content:**
1. Update orchestrator methods (execute_step_X)
2. Update response templates (response-templates.yaml)
3. Update this guide
4. Update tests
5. Test full workflow

### Localization

**For multi-language support:**
1. Extract content to separate files
2. Use language parameter in execute_step_X methods
3. Update response templates with language variants

### Analytics

**Track user behavior:**
1. Log step completion times
2. Monitor drop-off rates
3. Track acknowledgment phrases used
4. Measure time-to-first-command after onboarding

---

## 📚 Related Documentation

- **Brain Protection Rules:** `cortex-brain/brain-protection-rules.yaml`
- **User Profile System:** `cortex-brain/documents/implementation-guides/user-profile-guide.md`
- **Welcome Banner:** `src/cortex_agents/tactical/welcome_banner_agent.py`
- **Response Templates:** `cortex-brain/response-templates.yaml`

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2025-11-28 | Initial implementation (Sprint 1 Day 3) |
| 1.1.0 | 2025-11-30 | Added routing triggers and test suite |

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available - See LICENSE
