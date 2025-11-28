# Protection Event Notifications - Implementation Guide

**Feature:** User-Facing Governance Notifications  
**Sprint:** 2 (Active Compliance Dashboard)  
**Task:** 7 (Protection Event Notifications)  
**Status:** ✅ COMPLETE  
**Date:** November 28, 2025  
**Author:** Asif Hussain

---

## 📋 Overview

Protection Event Notifications provide educational, user-facing alerts when CORTEX governance rules are violated. Instead of cryptic error messages, users receive clear explanations with:

- **Severity indicators** (🔴 BLOCKED, 🟡 WARNING)
- **Educational context** (why the rule matters)
- **Suggested fixes** (concrete remediation steps)
- **Dashboard links** (full compliance report)
- **Override guidance** (for blocked operations)

---

## 🎯 Purpose

**Problem Solved:** Users violated governance rules without understanding:
- Which rule was violated
- Why the rule exists
- How to fix the issue
- Where to get more information

**Solution:** Educational notifications that teach users about CORTEX governance while enforcing architectural integrity.

---

## 🏗️ Architecture

### Components

**1. BrainProtector.format_user_notification()**
- **Location:** `src/tier0/brain_protector.py`
- **Purpose:** Generates markdown-formatted notification from ProtectionResult
- **Input:** ProtectionResult with violations
- **Output:** Formatted notification string (markdown)

**2. Protection Event Notification Template**
- **Location:** `cortex-brain/response-templates.yaml`
- **Purpose:** Defines notification structure and format
- **Sections:** Severity message, violations list, alternatives, dashboard link, override guidance

**3. ComplianceDatabase Integration**
- **Location:** `src/tier1/compliance_database.py`
- **Purpose:** Logs all violations for dashboard display
- **Tables:** `protection_events` (timestamp, rule_id, severity, file_path, evidence)

### Data Flow

```
User Operation
    ↓
BrainProtector.analyze_request(request)
    ↓
Protection Rule Validation (8 layers)
    ↓
Violations Detected? → YES
    ↓
ProtectionResult (severity, violations, alternatives)
    ↓
├─→ ComplianceDatabase.log_protection_event()  [Background logging]
│
└─→ BrainProtector.format_user_notification()
        ↓
    Formatted Notification (markdown)
        ↓
    Displayed in Copilot Chat Response
```

---

## 📝 Notification Format

### Structure

```markdown
---

## {emoji} Governance {severity}

{severity_message}

### Rules Violated:

**1. {rule_name}**
   - **Layer:** {layer_name}
   - **Issue:** {description}
   - **Why This Matters:** {rationale}
   - **Evidence:** {evidence}
   - **Suggested Fix:** {remedy}

{... additional violations ...}

### Recommended Alternatives:

- {alternative_1}
- {alternative_2}

### 📊 Full Compliance Report:

View the full compliance dashboard for detailed rule status and history:
```
show compliance
```

### ⚠️ Override Required:  [Only for BLOCKED severity]

This operation requires explicit override. If you believe this is necessary:
1. Document your justification in the commit message
2. Tag the commit with `[OVERRIDE]`
3. Ensure architectural review before merge

---
```

### Severity Indicators

| Severity | Emoji | Meaning | User Action |
|----------|-------|---------|-------------|
| BLOCKED  | 🔴    | Cannot proceed | Must use alternative or override |
| WARNING  | 🟡    | Risky but allowable | Should review and consider alternatives |
| SAFE     | 🟢    | No issues | No notification displayed |

---

## 🔧 Usage

### For Orchestrators

When implementing operations that might violate governance rules:

```python
from src.tier0.brain_protector import BrainProtector, ModificationRequest, Severity

# 1. Create Brain Protector instance
protector = BrainProtector()

# 2. Create modification request
request = ModificationRequest(
    intent="disable TDD workflow",
    description="Skip test-first development",
    files=["src/tdd/workflow.py"],
    justification="Want to move faster"
)

# 3. Validate request
result = protector.analyze_request(request)

# 4. Check for violations
if result.severity != Severity.SAFE:
    # Generate user-facing notification
    notification = protector.format_user_notification(result)
    
    # Include in response
    response_message = f"{your_main_response}\n\n{notification}"
    
    # For BLOCKED operations, prevent execution
    if result.severity == Severity.BLOCKED:
        return OperationResult(
            success=False,
            message="Operation blocked by governance rules",
            data={"notification": notification}
        )

# 5. Proceed with operation (if SAFE or WARNING)
```

### For Direct Tool Calls

When using Brain Protector for ad-hoc validation:

```python
# Example: Validating a user's request before starting work

protector = BrainProtector()

# User said: "Let's skip DoR validation and start coding"
request = ModificationRequest(
    intent="bypass DoR validation",
    description="Skip Definition of Ready checks",
    files=["src/planning/dor_validator.py"]
)

result = protector.analyze_request(request)

if result.severity == Severity.BLOCKED:
    notification = protector.format_user_notification(result)
    print(f"⚠️ Cannot proceed:\n{notification}")
else:
    print("✅ Request validated, proceeding...")
```

---

## 📊 Integration Points

### 1. System Alignment Orchestrator

**Integration:** Validates all configuration changes before deployment
**Usage:** Checks for governance violations in system configuration

```python
# Before deploying configuration changes
result = brain_protector.analyze_request(
    ModificationRequest(
        intent="update brain configuration",
        description=f"Modify {config_file}",
        files=[config_file]
    )
)

if result.severity == Severity.BLOCKED:
    notification = brain_protector.format_user_notification(result)
    return f"Deployment blocked:\n{notification}"
```

### 2. Planning Orchestrator

**Integration:** Validates planning workflow modifications
**Usage:** Prevents bypassing DoR/DoD requirements

```python
# When user requests to skip DoR
if "skip" in user_intent and "dor" in user_intent.lower():
    result = brain_protector.analyze_request(
        ModificationRequest(
            intent="bypass DoR validation",
            description="User wants to skip Definition of Ready",
            files=["src/planning/plan_orchestrator.py"]
        )
    )
    notification = brain_protector.format_user_notification(result)
    return notification
```

### 3. TDD Orchestrator

**Integration:** Enforces TDD workflow compliance
**Usage:** Prevents skipping RED-GREEN-REFACTOR cycle

```python
# When user tries to implement without failing test
if not red_phase_complete:
    result = brain_protector.analyze_request(
        ModificationRequest(
            intent="skip RED phase",
            description="Implement feature without failing test",
            files=["src/tdd/tdd_orchestrator.py"]
        )
    )
    notification = brain_protector.format_user_notification(result)
    return notification
```

### 4. Upgrade Orchestrator

**Integration:** Protects brain data during upgrades
**Usage:** Prevents overwriting user's brain history

```python
# Before upgrading CORTEX
result = brain_protector.analyze_request(
    ModificationRequest(
        intent="upgrade CORTEX",
        description=f"Upgrade from {current_version} to {target_version}",
        files=["cortex-brain/tier1/working_memory.db"]
    )
)

if result.severity == Severity.BLOCKED:
    notification = brain_protector.format_user_notification(result)
    return f"Upgrade blocked:\n{notification}"
```

---

## 🧪 Testing

### Test Script

**Location:** `test_protection_notifications.py`

**Test Cases:**
1. **BLOCKED Notification** - Disable TDD (Instinct Immutability)
2. **WARNING Notification** - God Object (SOLID Compliance)
3. **SAFE Operation** - No notification generated
4. **Component Validation** - All required elements present

### Running Tests

```bash
cd /Users/asifhussain/PROJECTS/CORTEX
python3 test_protection_notifications.py
```

**Expected Output:**

```
🧪 CORTEX Sprint 2 - Task 7: Protection Event Notifications Test
================================================================================

TEST 1: BLOCKED Notification (Disable TDD)
🔍 Validation Result:
   Severity: BLOCKED
   Decision: BLOCK
   Violations: 1
   Override Required: True

📢 USER-FACING NOTIFICATION:
## 🔴 Governance BLOCKED
...

✅ PASS - Blocked Notification
✅ PASS - Warning Notification
✅ PASS - Safe Operation
✅ PASS - Component Validation

🎯 Results: 4/4 tests passed
```

### Manual Testing

Test in actual Copilot Chat by requesting governance violations:

1. **Test BLOCKED:** "Let's disable TDD workflow for this feature"
2. **Test WARNING:** "Create a master manager class with all responsibilities"
3. **Test SAFE:** "Add a helper function for string formatting"

---

## 📚 Educational Content

### Rationale Explanations

Each rule includes a `rationale` field in `brain-protection-rules.yaml`:

```yaml
- rule_id: "TDD_ENFORCEMENT"
  name: "TDD Enforcement"
  severity: "blocked"
  description: "Attempt to bypass Test-Driven Development requirement"
  rationale: "TDD ensures code quality, maintainability, and correctness from day one. Skipping TDD leads to fragile code, harder debugging, and lower confidence in changes."
  remedy: "Write failing test first (RED phase), implement to pass (GREEN phase), then refactor for quality"
```

**Notification displays:**
- **Issue:** "Attempt to bypass Test-Driven Development requirement"
- **Why This Matters:** "TDD ensures code quality, maintainability, and correctness..."
- **Suggested Fix:** "Write failing test first (RED phase), implement to pass (GREEN phase)..."

### Suggested Fixes

Each rule includes a `remedy` field with concrete steps:

**Examples:**

| Rule | Remedy |
|------|--------|
| TDD_ENFORCEMENT | Write failing test first (RED phase), implement to pass (GREEN phase), then refactor |
| DOD_VALIDATION | Complete DoD checklist: tests passing, documentation updated, code reviewed |
| GOD_OBJECT | Split responsibilities into separate classes following Single Responsibility Principle |
| TIER_BOUNDARY | Move application code to user repository, keep CORTEX core focused on AI capabilities |

---

## 🎨 Customization

### Adjusting Notification Tone

**Current:** Educational, friendly, teaching-focused  
**Modification:** Edit `BrainProtector.format_user_notification()` method

**Options:**
- **Strict:** More formal language, less explanation
- **Verbose:** Extended explanations with examples
- **Minimal:** Bullet points only, no rationale

**Example (Strict Tone):**

```python
if result.severity == Severity.BLOCKED:
    notification += "**BLOCKED: This operation violates governance and MUST NOT proceed.**\n\n"
else:
    notification += "**WARNING: Review governance implications before continuing.**\n\n"
```

### Adding Custom Sections

Extend the notification with additional context:

```python
# After alternatives section, add:
notification += "### 📖 Learn More:\n\n"
notification += f"Read the full governance guide: `#file:cortex-brain/documents/governance/{violation.layer.value}.md`\n\n"
```

### Suppressing Notifications

For automated operations that don't need user alerts:

```python
result = protector.analyze_request(request)

# Option 1: Check severity before generating notification
if result.severity == Severity.BLOCKED and require_user_notification:
    notification = protector.format_user_notification(result)

# Option 2: Add silent mode parameter
result = protector.analyze_request(request, silent=True)  # No DB logging
```

---

## 📈 Metrics & Monitoring

### Compliance Dashboard Integration

All notifications are automatically logged to:

**Database:** `cortex-brain/compliance_status.db`  
**Table:** `protection_events`

**Fields:**
- `id` - Event ID
- `timestamp` - When violation occurred
- `rule_id` - Which rule was violated
- `severity` - blocked/warning
- `file_path` - File involved
- `evidence` - Detection details

**Dashboard Display:**
- **Recent Events:** Last 20 protection violations
- **Rule Status:** Violation frequency per rule
- **Compliance Score:** Percentage of operations following rules

### Viewing Metrics

```
show compliance
```

**Shows:**
- Overall compliance score (0-100%)
- Rule-by-rule status (🟢 🟡 🔴)
- Recent violations timeline
- Trend over time

---

## 🔍 Troubleshooting

### Notification Not Appearing

**Symptom:** Violation detected but no notification shown  
**Cause:** Orchestrator not calling `format_user_notification()`

**Fix:**
```python
# Add after analyze_request()
if result.severity != Severity.SAFE:
    notification = protector.format_user_notification(result)
    # Include in response
```

### Missing Rule Details

**Symptom:** Notification shows "No rationale available"  
**Cause:** Rule missing `rationale` or `remedy` fields in YAML

**Fix:** Update `cortex-brain/brain-protection-rules.yaml`:
```yaml
- rule_id: "YOUR_RULE"
  rationale: "Explanation of why rule matters"
  remedy: "Steps to fix violation"
```

### Database Logging Failures

**Symptom:** Notifications appear but dashboard shows no events  
**Cause:** Compliance database not initialized

**Fix:**
```python
# In BrainProtector.__init__()
self.compliance_db = ComplianceDatabase(brain_path=project_root / "cortex-brain")
```

---

## 🚀 Future Enhancements

### Phase 2 (Planned)

1. **User Profile Adaptation**
   - Junior developers: More explanation, learning resources
   - Senior developers: Concise, assumes knowledge
   - Educational mode: Extended tutorials

2. **Interactive Fixes**
   - "Fix this for me" button
   - Auto-generate alternative implementation
   - One-click remediation

3. **Notification History**
   - View past violations
   - Track learning progress
   - Reduce repeat notifications

4. **Custom Severity Levels**
   - User-configurable thresholds
   - Project-specific rule customization
   - Team-level governance policies

---

## 📄 Related Documentation

- **Brain Protection Rules:** `cortex-brain/brain-protection-rules.yaml`
- **Compliance Dashboard:** `cortex-brain/documents/implementation-guides/compliance-dashboard-guide.md`
- **Response Templates:** `cortex-brain/response-templates.yaml` (protection_event_notification)
- **System Alignment:** `cortex-brain/documents/implementation-guides/system-alignment-guide.md`

---

## ✅ Acceptance Criteria

**Task 7 Complete When:**

- [x] Notification method added to BrainProtector (`format_user_notification()`)
- [x] Template created in response-templates.yaml (`protection_event_notification`)
- [x] Notifications include: severity emoji, rule name, layer, issue, rationale, remedy, dashboard link
- [x] Override guidance shown for BLOCKED operations
- [x] Alternatives displayed when available
- [x] Test script demonstrates all notification types
- [x] Educational tone matches CORTEX style guide
- [x] Markdown formatting correct (H2 headers, bold text, code blocks)
- [x] Dashboard link functional (`show compliance` command)
- [x] Documentation complete (this file)

**Status:** ✅ ALL CRITERIA MET

---

**Author:** Asif Hussain  
**Sprint:** 2 (Active Compliance Dashboard)  
**Task:** 7 (Protection Event Notifications)  
**Date:** November 28, 2025  
**Version:** 1.0
