# 🎯 INTENT CLARIFICATION - QUICK SUMMARY

## Your Question
**"Will cortex clarify my intent and use the interaction orchestrator as the default?"**

## Answer
### ✅ YES - ABSOLUTELY

---

## How It Works

### 1️⃣ You Give Vague Request
```
"Fix the error"
```

### 2️⃣ CORTEX Detects Ambiguity
```
Confidence: 0.62 (< 0.85 threshold)
Status: NEEDS_CLARIFICATION
```

### 3️⃣ CORTEX Asks Questions
```
❓ Which error? (logout, validation, tokens?)
❓ Which module? (auth.py, services, etc?)
❓ Any constraints? (backward compat?)
```

### 4️⃣ You Clarify
```
"Logout endpoint. oauth.py. Must maintain API."
```

### 5️⃣ CORTEX Confirms
```
Confidence: 0.96 (READY)
Status: READY_FOR_APPROVAL
```

### 6️⃣ You Approve
```
✅ YES → Execute
❌ NO → Back to clarification
❓ CLARIFY → Ask more
```

---

## The Default Flow

```
STAGE 1: Intent Comprehension (Interaction Orchestrator)
    ↓
├─ Detect confidence
├─ If confidence < 0.85 → Ask clarification
├─ Run LENS protocol (5-source intelligence)
└─ Generate comprehension YAML
    ↓
APPROVAL GATE
    ↓
├─ User reviews comprehension
├─ User confirms/rejects/clarifies
└─ On approval → Stage 2
    ↓
STAGE 2: Route to Executor
    ↓
STAGE 3: Execute with governance
```

---

## Key Guarantees

✅ Interaction Orchestrator is FIRST STAGE (always)  
✅ Clarification questions WILL BE ASKED  
✅ Low confidence intents CANNOT proceed  
✅ No execution without user approval  
✅ You see reasoning and alternatives  
✅ Ambiguous requests WILL BE CLARIFIED  

---

## The Threshold

**Confidence < 0.85** → Clarification Required  
**Confidence ≥ 0.85** → Comprehension Ready  
**Unclear Routing** → Back to Interaction (DEFAULT)  

---

## What CANNOT Happen

❌ Cannot execute on vague intent  
❌ Cannot skip Interaction stage  
❌ Cannot bypass approval gate  
❌ Cannot execute low-confidence requests  
❌ Cannot skip clarification questions  

---

## Real Example

```
User: "Improve error handling"

CORTEX asks:
Q1: Where? (which file/module?)
Q2: What type? (messages, recovery, etc?)
Q3: Constraints? (breaking changes OK?)

User: "oauth.py, handle more cases, backward compat"

CORTEX generates comprehension:
Intent: REFACTOR
Target: src/auth/oauth.py
Type: Add error handling
Confidence: 0.94 ✅

CORTEX shows:
→ Challenges: API changes, test gaps, impact
→ Recommendations: TDD approach, new tests, docs
→ Requests approval

User: ✅ Approve

CORTEX executes through TDD Orchestrator
```

---

## Technical Details

**Clarification Trigger:**
- Confidence score < 0.85
- Multiple intent candidates
- Vague scope
- Missing constraints

**Clarification Process:**
- Generate specific questions
- Show alternatives
- Wait for user response
- Update confidence score
- Repeat if needed

**Interaction Orchestrator Default:**
- STAGE 1 ALWAYS (before anything)
- Handles all comprehension
- Generates challenges & recommendations
- Manages approval gate
- Fallback for unclear routing

---

## Files That Implement This

- `src/core/intent/intent_reflection_protocol.py` - Main orchestrator
- `src/core/intent/intent_canonicalizer.py` - Clarification logic
- `src/core/intent/comprehension_loop.py` - User approval gate
- `.github/prompts/CORTEX.prompt.md` - System prompt

---

**Bottom Line:**

CORTEX will NOT let you proceed with an unclear intent. It WILL ask clarification questions. The Interaction Orchestrator is the DEFAULT first stage that clarifies everything before execution.

✅ **CONFIRMED & GUARANTEED**
