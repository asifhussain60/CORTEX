# Onboarding Orchestrator Guide

**Purpose:** User onboarding with 3-question micro-survey for profile creation  
**Version:** 3.2.1  
**Status:** ✅ PRODUCTION

---

## 🎯 Overview

The Onboarding Orchestrator handles first-time user setup through a quick 3-question survey to establish user preferences:

1. **Experience Level** - Junior, Mid, Senior, Expert
2. **Interaction Mode** - Autonomous, Guided, Educational, Pair Programming
3. **Tech Stack Preference** - Azure, AWS, GCP, Custom, or No Preference

Profile is stored in Tier 1 with FIFO exemption for permanent retention.

---

## 🚀 Commands

**Natural Language Triggers:**

- `onboard`
- `onboarding`
- `setup profile`
- `first time`
- `new user`

**When It Runs:**
- Automatically on first CORTEX interaction (if no profile exists)
- When user says "update profile" or "change profile"

---

## 📊 Onboarding Questions

### Question 1: Experience Level

**Prompt:**
```
What's your development experience?

1. Junior (0-2 years) - Learning the ropes, need guidance
2. Mid (2-5 years) - Solid fundamentals, occasional help needed
3. Senior (5-10 years) - Experienced, confident in most areas
4. Expert (10+ years) - Deep expertise, minimal hand-holding

Your choice (1-4):
```

**Impact:**
- **Junior:** More detailed explanations, educational mode default
- **Mid:** Balanced guidance and execution
- **Senior:** Less verbose, assumes knowledge
- **Expert:** Minimal explanation, results-focused

---

### Question 2: Interaction Mode

**Prompt:**
```
How do you prefer to work with CORTEX?

1. Autonomous - Just do it, show me results
2. Guided - Explain what you're doing (recommended)
3. Educational - Teach me why and show alternatives
4. Pair Programming - Ask clarifying questions first

Your choice (1-4):
```

**Mode Behaviors:**

**Autonomous Mode:**
- Executes immediately without explanation
- Shows only results and next steps
- Best for: Experienced users who know what they want

**Guided Mode (Recommended):**
- Explains actions before executing
- Provides context for decisions
- Best for: Most users, balanced approach

**Educational Mode:**
- Teaches concepts as you work
- Shows alternatives and trade-offs
- Best for: Learning new technologies

**Pair Programming Mode:**
- Asks clarifying questions before proceeding
- Collaborative decision-making
- Best for: Complex problems requiring discussion

---

### Question 3: Tech Stack Preference

**Prompt:**
```
What's your company/project tech stack?

1. No preference - CORTEX decides based on best practice
2. Azure stack (Azure DevOps, AKS, ARM/Terraform)
3. AWS stack (ECS/EKS, CodePipeline, CloudFormation/Terraform)
4. GCP stack (GKE, Cloud Build, Terraform)
5. Custom (I'll configure later with 'update profile')

Your choice (1-5):
```

**IMPORTANT:** Tech stack is context for deployment, NOT a constraint.

CORTEX will always recommend the best solution first, then show how to implement using your tech stack.

**Preset Configurations:**

- **Azure Stack:**
  ```json
  {
    "cloud_provider": "azure",
    "container_platform": "kubernetes",
    "ci_cd": "azure_devops",
    "iac": "terraform"
  }
  ```

- **AWS Stack:**
  ```json
  {
    "cloud_provider": "aws",
    "container_platform": "kubernetes",
    "ci_cd": "github_actions",
    "iac": "terraform"
  }
  ```

- **GCP Stack:**
  ```json
  {
    "cloud_provider": "gcp",
    "container_platform": "kubernetes",
    "ci_cd": "github_actions",
    "iac": "terraform"
  }
  ```

---

## ⚙️ Profile Storage

**Location:** Tier 1 SQLite database (`tier1-working-memory.db`)

**Table:** `user_profile`

**Schema:**
```sql
CREATE TABLE user_profile (
    id INTEGER PRIMARY KEY,
    experience_level TEXT NOT NULL,
    interaction_mode TEXT NOT NULL,
    tech_stack_preference TEXT,
    created_at TEXT NOT NULL,
    last_updated TEXT NOT NULL,
    persistent_flag INTEGER DEFAULT 1
);
```

**FIFO Exemption:** Profile is marked as persistent (never auto-deleted by 70-conversation FIFO cleanup).

---

## 🔧 Updating Profile

**Commands:**
- `update profile`
- `change profile`
- `modify profile`
- `update my profile`

**What Can Be Updated:**
- Experience level
- Interaction mode
- Tech stack preference

**Example:**
```
User: "update profile"

CORTEX:
  Current Profile:
  • Experience: Senior
  • Mode: Guided
  • Tech Stack: Azure stack
  
  What would you like to update?
  1. Experience level
  2. Interaction mode
  3. Tech stack preference
  4. Cancel
  
  Your choice (1-4):
```

---

## 📈 Examples

### Example 1: First-Time Onboarding

```
User: [First interaction with CORTEX]

CORTEX:
  Welcome to CORTEX! Let's personalize your experience (~30 seconds).
  
  Question 1 of 3: What's your development experience?
  
  1. Junior (0-2 years)
  2. Mid (2-5 years)
  3. Senior (5-10 years)
  4. Expert (10+ years)
  
  Your choice (1-4): 3
  
  ✅ Experience level set to: Senior
  
  Question 2 of 3: How do you prefer to work with CORTEX?
  
  1. Autonomous
  2. Guided (recommended)
  3. Educational
  4. Pair Programming
  
  Your choice (1-4): 2
  
  ✅ Interaction mode set to: Guided
  
  Question 3 of 3: What's your tech stack?
  
  1. No preference
  2. Azure stack
  3. AWS stack
  4. GCP stack
  5. Custom
  
  Your choice (1-5): 2
  
  ✅ Tech stack preference set to: Azure stack
  
  🎉 Onboarding complete! CORTEX is now personalized for you.
  
  Try these commands:
  • "help" - See all capabilities
  • "plan [feature]" - Start feature planning
  • "start tdd" - Begin test-driven development
```

---

### Example 2: Profile Update

```
User: "change my interaction mode to autonomous"

CORTEX:
  Updating profile...
  
  ✅ Interaction mode changed: Guided → Autonomous
  
  From now on, CORTEX will execute immediately and show results without explanations.
  
  To revert: "update profile" and select Guided mode.
```

---

## 🐛 Troubleshooting

### Issue: "Profile not persisting"

**Cause:** Profile not marked with persistent flag

**Solution:**
```sql
-- Check persistent flag
SELECT persistent_flag FROM user_profile WHERE id = 1;
-- Should return 1

-- If 0, update:
UPDATE user_profile SET persistent_flag = 1 WHERE id = 1;
```

---

### Issue: "Onboarding loops (asks questions repeatedly)"

**Cause:** Profile creation failing silently

**Solution:**
```python
# Check for errors
from src.tier1.working_memory import WorkingMemory
wm = WorkingMemory()
try:
    wm.create_profile("guided", "mid")
except ValueError as e:
    print(f"Validation error: {e}")
```

---

## 📚 Related Documentation

- **User Profile Guide:** `cortex-brain/documents/implementation-guides/user-profile-guide.md`
- **Response Format:** `.github/prompts/modules/response-format.md`
- **Template Guide:** `.github/prompts/modules/template-guide.md`

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
