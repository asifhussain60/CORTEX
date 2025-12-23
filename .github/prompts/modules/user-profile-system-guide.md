# 👤 User Profile System Guide

**Full Documentation:** `cortex-brain/documents/implementation-guides/user-profile-guide.md`

## Quick Start

### First-Time Setup
- 3-question onboarding: experience level → interaction mode → tech stack
- Takes <2 minutes
- Can be updated anytime

### Updating Profile
- `update profile` - Full profile update
- `change tech stack` - Update tech stack only
- 16 keywords auto-trigger profile updates (e.g., "I'm new to Python", "switch to autonomous mode")

## Interaction Modes

### 1. Autonomous Mode
- **Speed:** Fastest results
- **Explanation:** Minimal, assumes understanding
- **Best For:** Experienced developers, time-sensitive work
- **Output:** Direct solutions with brief context

### 2. Guided Mode (Default)
- **Speed:** Standard
- **Explanation:** Balanced, clear reasoning
- **Best For:** Most developers, production work
- **Output:** Solutions + explanations + next steps

### 3. Educational Mode
- **Speed:** Slower (more detail)
- **Explanation:** Extended teaching focus
- **Best For:** Learning new technologies, junior developers
- **Output:** Solutions + extended context + learning resources

### 4. Pair Programming Mode
- **Speed:** Interactive (back-and-forth)
- **Explanation:** Collaborative, asks for feedback
- **Best For:** Complex decisions, architectural planning
- **Output:** Proposals + questions + refinement loops

## Experience Levels

### Junior (0-2 years)
- More detailed explanations
- Links to learning resources
- Common pitfalls highlighted
- Best practices explained from first principles

### Mid (2-5 years)
- Balanced approach (default)
- Assumes basic knowledge
- Focuses on practical application
- Includes optimization tips

### Senior (5-10 years)
- Advanced patterns emphasized
- Less explanation of basics
- Performance and scalability focus
- Architecture recommendations

### Expert (10+ years)
- Assumes deep technical knowledge
- Cutting-edge approaches
- Tradeoff analysis
- System design focus

## Tech Stack Preferences

### Pre-Configured Stacks

**Azure Stack**
- Azure DevOps for CI/CD
- AKS for container orchestration
- ARM templates or Terraform for IaC

**AWS Stack**
- ECS/EKS for containers
- CodePipeline for CI/CD
- CloudFormation or Terraform for IaC

**GCP Stack**
- GKE for container orchestration
- Cloud Build for CI/CD
- Terraform for IaC

**No Preference** (Recommended for Learning)
- CORTEX decides based on best practice
- Learn optimal solutions first
- Company-specific adaptation second

**Custom**
- Mix and match individual tools
- Specify per-project preferences
- Maximum flexibility

## CRITICAL PRINCIPLE: Context NOT Constraint

**Tech stack is deployment context only - never a filter:**

1. **Best Practice First:** CORTEX always recommends the optimal solution
2. **Dual Responses:** Shows BOTH best practice + company stack deployment
3. **No Filtering:** Recommendations never limited by tech stack
4. **Learning Focus:** Understand WHY before adapting to constraints

### Example
```
User: "How do I implement caching?" (Profile: AWS Stack)

CORTEX Response:
1. Best Practice: Redis with proper eviction policies
2. AWS Deployment: ElastiCache for Redis + CloudWatch monitoring
3. Why: In-memory caching reduces database load by 70-90%
```

## Profile Update Keywords

These trigger automatic profile updates:
- Experience: "I'm new to", "I'm experienced with", "I've been coding for X years"
- Mode: "explain more", "less detail", "teach me", "just give me the code"
- Tech Stack: "we use Azure", "switch to AWS", "prefer GCP"

## API Reference

### Get Current Profile
```python
from src.tier1.user_profile_manager import UserProfileManager
profile = UserProfileManager.get_profile()
```

### Update Profile
```python
profile.update(
    experience_level="senior",
    mode="autonomous",
    tech_stack="azure"
)
```

### Check Profile Completeness
```python
if not profile.is_complete():
    # Trigger onboarding
    profile.run_onboarding()
```

## Integration Points

- **Response Templates:** Automatic mode-based formatting
- **TDD Workflow:** Adapts explanation depth
- **Planning System:** Tailors DoR/DoD validation
- **Code Generation:** Matches tech stack conventions

## Best Practices

1. **Complete Onboarding:** Don't skip - saves time long-term
2. **Update Regularly:** As you grow, update your experience level
3. **Experiment with Modes:** Try different modes for different tasks
4. **Tech Stack Honesty:** Set to actual company constraints
5. **No Preference Default:** Best for maximum learning
