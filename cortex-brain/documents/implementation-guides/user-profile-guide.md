# User Profile System - User Guide

**Version:** 3.2.1  
**Status:** Production Ready  
**Author:** Asif Hussain  
**Created:** 2025-11-28

---

## Quick Start

### First Time Setup (Onboarding)

When you first interact with CORTEX, you'll go through a quick 3-question onboarding:

**Question 1: Experience Level**
```
What's your development experience?

1. Junior (0-2 years)
2. Mid (2-5 years)
3. Senior (5-10 years)
4. Expert (10+ years)
```

**Question 2: Interaction Mode**
```
How do you prefer to work with CORTEX?

1. Autonomous - Just do it, show me results
2. Guided - Explain then execute (recommended)
3. Educational - Teach me as we go
4. Pair Programming - Collaborate on everything
```

**Question 3: Tech Stack**
```
What's your company/project tech stack?

1. No preference - CORTEX decides based on best practice
2. Azure stack (Azure DevOps, AKS, ARM/Terraform)
3. AWS stack (ECS/EKS, CodePipeline, CloudFormation/Terraform)
4. GCP stack (GKE, Cloud Build, Terraform)
5. Custom (I'll configure later with 'update profile')
```

**IMPORTANT:** Tech stack is context for deployment, NOT a constraint.  
CORTEX will always recommend the best solution first.

---

## Updating Your Profile

### Update Command Keywords

Say any of these phrases to update your profile:
- "update profile"
- "update my profile"
- "change profile"
- "change my profile"
- "modify profile"
- "modify my profile"
- "update preference"
- "update my preference"
- "change preference"
- "change my preference"
- "modify preference"
- "modify my preference"
- "update tech stack"
- "change tech stack"
- "modify tech stack"
- "update my tech stack"

### Update Menu

After triggering an update, you'll see:

```
## 🧠 CORTEX Profile Update

**Current Profile:**
- Experience: Senior
- Mode: Guided
- Tech Stack: Azure stack

**What would you like to update?**

1. Experience level
2. Interaction mode
3. Tech stack preference
4. Cancel
```

### Example: Updating Experience Level

**You:** "update profile"  
**CORTEX:** (shows menu)  
**You:** "1" (or "experience level")  
**CORTEX:** Shows experience options (1-4)  
**You:** "4" (Expert)  
**CORTEX:** "✅ Experience level updated to: Expert"

### Example: Updating Tech Stack

**You:** "change tech stack"  
**CORTEX:** 
```
## 🧠 CORTEX Tech Stack Update

**Current Tech Stack:** Azure stack

**IMPORTANT:** Tech stack is context for deployment, NOT a constraint.  
CORTEX will always recommend the best solution first.

**What's your company/project tech stack?**

1. No preference - CORTEX decides based on best practice
2. Azure stack (Azure DevOps, AKS, ARM/Terraform)
3. AWS stack (ECS/EKS, CodePipeline, CloudFormation/Terraform)
4. GCP stack (GKE, Cloud Build, Terraform)
5. Custom (I'll configure later with 'update profile')

**Your choice (1-5):**
```

---

## Interaction Modes Explained

### 1. Autonomous Mode
**Best For:** Experienced developers who want quick results  
**Response Style:** Compact, action-first  

**Format Changes:**
- Skips "Understanding" section
- Minimal explanation
- Results and next steps only

**Example Response:**
```markdown
# 🧠 CORTEX Code Update

✅ Fixed validation bug in UserService.cs (line 47)

## 🔍 Next Steps
1. Run tests: `dotnet test`
2. Commit: `git commit -m "Fix user validation"`
```

### 2. Guided Mode (Default)
**Best For:** Most developers, balanced approach  
**Response Style:** Standard format with explanations  

**Format Changes:**
- Full 5-part response structure
- Clear understanding statement
- Challenge identification
- Detailed explanation

**Example Response:**
```markdown
# 🧠 CORTEX Code Update

## 🎯 My Understanding Of Your Request
You need to fix the validation logic that's allowing empty usernames.

## ⚠️ Challenge
Current validator checks null but not empty strings.

## 💬 Response
I've updated the validation to check both null and empty strings...

## 📝 Your Request
Fix user validation to reject empty usernames

## 🔍 Next Steps
1. Run tests: `dotnet test`
2. Commit changes
```

### 3. Educational Mode
**Best For:** Junior developers or learning new technologies  
**Response Style:** Teaching-focused with explanations  

**Format Changes:**
- Extended "Understanding" with context
- "Why This Matters" section added
- Step-by-step breakdowns
- Related concepts linked

**Example Response:**
```markdown
# 🧠 CORTEX Code Update

## 🎯 My Understanding Of Your Request
You need to fix validation logic. Let me explain what validation is...

## 📚 Why This Matters
Input validation is a critical security practice. Here's why:
- Prevents SQL injection attacks
- Ensures data integrity
- Improves user experience with clear error messages

## 💬 Response
I've updated the validation using C#'s string.IsNullOrWhiteSpace()...

**What this code does:**
1. Checks if username is null (not provided)
2. Checks if username is empty string ("")
3. Checks if username is only whitespace ("   ")

## 🔍 Next Steps
1. Run tests to verify the fix
2. Learn more about validation: [link]
```

### 4. Pair Programming Mode
**Best For:** Complex problems requiring collaboration  
**Response Style:** Conversational, seeks feedback  

**Format Changes:**
- Questions and confirmation requests
- Multiple approach options presented
- Seeks approval before executing
- Collaborative tone

**Example Response:**
```markdown
# 🧠 CORTEX Collaboration

## 🎯 My Understanding
You want to fix validation. I see a few approaches:

**Option 1: Quick Fix**
Add IsNullOrWhiteSpace check (5 min)

**Option 2: Comprehensive**
Refactor entire validation layer with FluentValidation (30 min)

**Which approach works better for you?**

## 💡 My Recommendation
Option 1 for now, since you have a production bug. We can refactor later.

**Shall I proceed with Option 1?**
```

---

## Tech Stack Preference

### Understanding "Context NOT Constraint"

**The Principle:**
Tech stack preference tells CORTEX what your company uses for deployment. It does **NOT** limit or filter recommendations.

**How CORTEX Uses It:**

1. **Best Practice First:** CORTEX always recommends the objectively best solution
2. **Company Context Second:** Then shows how to implement using your tech stack

### Example: Architecture Recommendation

**Scenario:** You ask "How should I design this new feature?"

**With Tech Stack = Azure:**
```markdown
## 💡 Best Practice Recommendation

For this feature, I recommend event-driven microservices architecture:
- Better scalability
- Independent deployment
- Fault isolation

## 🏢 Deployment with Your Tech Stack (Azure)

Since your company uses Azure, here's how to implement:

**Infrastructure:**
- Azure Kubernetes Service (AKS) for container orchestration
- Azure Service Bus for event messaging
- Azure API Management for API gateway

**CI/CD:**
- Azure DevOps pipelines for automated deployment
- Azure Container Registry for Docker images

**Infrastructure as Code:**
- ARM templates or Terraform for resource provisioning
```

**Key Points:**
✅ You see the best practice recommendation (event-driven microservices)  
✅ You see Azure-specific guidance for deployment  
✅ Recommendation not filtered or changed based on tech stack  
✅ Both sections shown, you choose which to follow

### When Tech Stack IS Relevant

Tech stack preference is considered for:
- **Deployment guidance** - Cloud-specific instructions
- **Tool recommendations** - Compatible CI/CD tools
- **Code examples** - Platform-specific SDKs
- **Best practices** - Cloud provider patterns

Tech stack preference is **NOT** considered for:
- **Architecture decisions** - Best practice wins
- **Design patterns** - Language-agnostic
- **Algorithm choices** - Tech-independent
- **Security recommendations** - Universal principles

---

## Preset Configurations

### Azure Stack

**Components:**
- **Cloud:** Microsoft Azure
- **Containers:** Azure Kubernetes Service (AKS)
- **Architecture:** Microservices
- **CI/CD:** Azure DevOps
- **IaC:** ARM templates (Azure Resource Manager)

**When to Choose:**
- Company standardized on Microsoft ecosystem
- Using Azure Active Directory for SSO
- Strong .NET development team
- Enterprise support requirements

**What You Get:**
- Azure-specific deployment guidance
- ARM template examples
- Azure DevOps pipeline samples
- AKS configuration recommendations

---

### AWS Stack

**Components:**
- **Cloud:** Amazon Web Services
- **Containers:** Amazon EKS (Elastic Kubernetes Service)
- **Architecture:** Microservices
- **CI/CD:** GitHub Actions
- **IaC:** Terraform

**When to Choose:**
- Company standardized on AWS
- Using AWS managed services (RDS, S3, etc.)
- Multi-cloud strategy with AWS primary
- Cost optimization with AWS pricing

**What You Get:**
- AWS-specific deployment guidance
- CloudFormation or Terraform examples
- EKS setup recommendations
- GitHub Actions workflows for AWS

---

### GCP Stack

**Components:**
- **Cloud:** Google Cloud Platform
- **Containers:** Google Kubernetes Engine (GKE)
- **Architecture:** Microservices
- **CI/CD:** GitHub Actions or Cloud Build
- **IaC:** Terraform

**When to Choose:**
- Company standardized on GCP
- Using Google services (BigQuery, Pub/Sub)
- Data analytics/ML workloads
- Kubernetes-native development

**What You Get:**
- GCP-specific deployment guidance
- Terraform examples for GCP
- GKE configuration recommendations
- Cloud Build pipeline samples

---

### No Preference (Recommended for Learning)

**Components:**
- All fields set to `null` or empty

**When to Choose:**
- Learning new technologies
- Want best practice without platform bias
- Evaluating multiple cloud providers
- Personal projects without constraints

**What You Get:**
- Pure best practice recommendations
- Tech-agnostic architecture guidance
- No platform-specific bias
- Freedom to choose later

---

### Custom Configuration

**Components:**
- Mix and match any values

**Example Custom Stack:**
```json
{
  "cloud_provider": "aws",
  "container_platform": "docker",
  "architecture": "monolithic",
  "ci_cd": "jenkins",
  "iac": "none"
}
```

**When to Choose:**
- Unique company requirements
- Legacy system constraints
- Specific tool mandates
- Hybrid environments

---

## API Reference (For Developers)

### WorkingMemory CRUD Operations

#### create_profile()

```python
def create_profile(
    interaction_mode: str,
    experience_level: str,
    tech_stack_preference: Optional[Dict[str, str]] = None
) -> bool
```

**Parameters:**
- `interaction_mode` - One of: autonomous, guided, educational, pair
- `experience_level` - One of: junior, mid, senior, expert
- `tech_stack_preference` - Optional dict with keys: cloud_provider, container_platform, architecture, ci_cd, iac

**Returns:** `True` if successful, raises `ValueError` on validation failure

**Example:**
```python
from src.tier1.working_memory import WorkingMemory

wm = WorkingMemory()
success = wm.create_profile(
    interaction_mode="guided",
    experience_level="senior",
    tech_stack_preference={
        "cloud_provider": "azure",
        "container_platform": "kubernetes"
    }
)
```

---

#### get_profile()

```python
def get_profile() -> Optional[Dict[str, Any]]
```

**Returns:** Profile dict or `None` if no profile exists

**Example:**
```python
profile = wm.get_profile()
if profile:
    print(f"Mode: {profile['interaction_mode']}")
    print(f"Experience: {profile['experience_level']}")
    print(f"Tech Stack: {profile['tech_stack_preference']}")
```

---

#### update_profile()

```python
def update_profile(
    interaction_mode: Optional[str] = None,
    experience_level: Optional[str] = None,
    tech_stack_preference: Optional[Dict[str, str]] = ...
) -> bool
```

**Parameters:**
- `interaction_mode` - New mode (optional, keeps current if omitted)
- `experience_level` - New experience level (optional)
- `tech_stack_preference` - New tech stack (use `None` to clear, omit with `...` to keep current)

**Sentinel Value:** `...` (Ellipsis) means "don't update this field"

**Returns:** `True` if successful, `False` if nothing to update

**Examples:**
```python
# Update only experience level
wm.update_profile(experience_level="expert")

# Update tech stack
wm.update_profile(tech_stack_preference={"cloud_provider": "aws"})

# Clear tech stack (set to None)
wm.update_profile(tech_stack_preference=None)

# Update multiple fields
wm.update_profile(
    interaction_mode="autonomous",
    experience_level="expert",
    tech_stack_preference={"cloud_provider": "gcp"}
)
```

---

#### delete_profile()

```python
def delete_profile() -> bool
```

**Returns:** `True` if profile deleted

**Example:**
```python
wm.delete_profile()  # Removes profile, will trigger onboarding on next interaction
```

---

#### profile_exists()

```python
def profile_exists() -> bool
```

**Returns:** `True` if profile exists

**Example:**
```python
if not wm.profile_exists():
    # Trigger onboarding
    pass
```

---

## Troubleshooting

### Profile Not Persisting

**Symptom:** Profile resets after restarting CORTEX

**Cause:** Database file missing `persistent_flag`

**Fix:**
```python
# Check persistent flag
from src.tier1.working_memory import WorkingMemory
wm = WorkingMemory()
profile = wm.get_profile()
# Profile should have persistent_flag=1 in database
```

### Onboarding Loops

**Symptom:** CORTEX keeps asking onboarding questions

**Cause:** Profile creation failing silently

**Fix:**
```python
# Check for errors
try:
    wm.create_profile("guided", "mid")
except ValueError as e:
    print(f"Validation error: {e}")
```

### Tech Stack Not Applied

**Symptom:** Responses don't include tech stack context

**Cause:** Template rendering not using profile

**Fix:** Check that `IntentRouter` is injecting profile into `AgentRequest`

### Update Commands Not Recognized

**Symptom:** "update profile" doesn't trigger update flow

**Cause:** Intent detection keywords not matching

**Fix:** Use exact phrases listed in "Update Command Keywords" section above

---

## Best Practices

### For Users

1. **Start with "No Preference"** - Learn best practices without bias
2. **Update Profile Gradually** - Change settings as you understand them
3. **Trust the Recommendations** - CORTEX always shows best practice first
4. **Use Educational Mode** - When learning new technologies
5. **Switch to Autonomous** - When time-sensitive and you know the domain

### For Developers

1. **Check Profile Exists** - Before accessing profile fields
2. **Handle None Tech Stack** - Not all users set tech stack
3. **Validate Before Update** - Use WorkingMemory validation, don't bypass
4. **Respect Sentinel Values** - `...` means "don't update", `None` means "clear"
5. **Test Edge Cases** - Empty dict, null, partial tech stack

---

## FAQ

**Q: Can I have multiple profiles?**  
A: No, CORTEX supports one profile per installation (single-user design).

**Q: What happens if I don't set tech stack?**  
A: CORTEX provides best practice recommendations without platform-specific guidance.

**Q: Does tech stack limit what CORTEX can recommend?**  
A: No. Tech stack is context only. CORTEX always recommends the best solution first.

**Q: Can I change tech stack later?**  
A: Yes, use "update tech stack" command anytime.

**Q: What if my company uses tools not in the presets?**  
A: Choose "Custom" and configure individual fields to match your stack.

**Q: Is profile data private?**  
A: Yes, stored locally in Tier 1 database (tier1-working-memory.db), never transmitted.

**Q: Can I export my profile?**  
A: Yes, use `wm.get_profile()` to retrieve as JSON dict.

**Q: Does profile affect test generation?**  
A: No, tests are generated based on code structure, not user profile.

**Q: Can I skip onboarding?**  
A: No, but you can choose "No preference" for all questions to minimize setup time.

**Q: What's the difference between "No preference" and empty profile?**  
A: Same behavior - both mean CORTEX decides based on best practice.

---

## Version History

**3.2.1** (2025-11-28)
- Added tech_stack_preference field
- Implemented context-not-constraint pattern
- Added 5 preset configurations
- Added 16-keyword intent detection
- Comprehensive test coverage (46 tests, 100% passing)

**3.2.0** (2025-11-27)
- Initial profile system (interaction_mode + experience_level)
- 3-question onboarding flow
- Profile CRUD operations

---

## Related Documentation

- **Schema:** `user-profile-schema.md` - Database schema and field definitions
- **Test Results:** `user-profile-test-results.md` - Comprehensive test report
- **CORTEX Prompt:** `.github/prompts/CORTEX.prompt.md` - Main system prompt with profile integration
- **Response Templates:** `cortex-brain/response-templates.yaml` - Template patterns using profile

---

**Questions?** Say "help with profile" in CORTEX chat.
