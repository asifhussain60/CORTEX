# Onboarding Orchestrator Guide

**Module:** `OnboardingOrchestrator`  
**Location:** `src/operations/modules/onboarding/onboarding_orchestrator.py`  
**Purpose:** First-time user onboarding and profile setup  
**Status:** ✅ Production  
**Version:** 3.3.0

---

## Overview

The Onboarding Orchestrator manages the first-time user experience for CORTEX, including user profile creation, initial setup, feature introduction, and learning path recommendations.

**Key Capabilities:**
- 3-question user profile setup
- Interactive feature introduction
- Guided learning path creation
- Initial repository configuration
- Welcome message customization
- Skip/resume onboarding flow

---

## Natural Language Triggers

**Automatic Activation:**
- First-time CORTEX activation (no profile exists)
- `setup profile`
- `onboard me`

**Manual Triggers:**
- `start onboarding`
- `reset profile`
- `onboarding tutorial`

**Context Variations:**
- "Set up my CORTEX profile"
- "Start fresh with CORTEX"
- "Show me how to use CORTEX"

---

## Architecture & Integration

**Dependencies:**
- User Profile System (Tier 3 database)
- Response template system
- Hands-on Tutorial Orchestrator
- Setup EPM Orchestrator

**Integration Points:**
- UnifiedEntryPointOrchestrator (first activation detection)
- UserProfileManager (profile storage)
- DemoOrchestrator (feature introduction)

---

## Onboarding Flow

**Step 1: Welcome & Introduction**
- CORTEX overview
- Key capabilities summary
- Natural language interface explanation
- Privacy and data storage info

**Step 2: User Profile Setup (3 Questions)**

**Question 1: Experience Level**
- Junior (0-2 years)
- Mid (2-5 years)
- Senior (5-10 years)
- Expert (10+ years)

**Question 2: Interaction Mode**
- Autonomous (quick results, minimal explanation)
- Guided (standard, balanced approach) **[Default]**
- Educational (teaching-focused, extended context)
- Pair Programming (collaborative, seeks feedback)

**Question 3: Tech Stack Preference**
- Azure Stack (Azure DevOps, AKS, ARM/Terraform)
- AWS Stack (ECS/EKS, CodePipeline, CloudFormation)
- GCP Stack (GKE, Cloud Build, Terraform)
- No Preference (CORTEX decides - recommended) **[Default]**
- Custom (mix and match)

**Step 3: Repository Setup**
- Detect project type (language, framework)
- Generate `.github/copilot-instructions.md`
- Configure CORTEX/ directory structure
- Add CORTEX/ to `.gitignore`

**Step 4: Feature Introduction**
- Planning System 2.0 demo
- TDD Mastery overview
- Brain system explanation
- Quick command reference

**Step 5: Learning Path Recommendation**
- Beginner path: Tutorial → Planning → TDD
- Intermediate path: TDD → Planning → Advanced features
- Expert path: Architecture review → Optimization → Custom workflows

**Step 6: Completion & Next Steps**
- Profile confirmation
- First operation suggestions
- Help command reminder
- Tutorial availability notice

---

## Usage Examples

### First-Time Activation

```
User: "/CORTEX"
CORTEX: Detects no profile → Starts onboarding → 3 questions → Setup complete
```

### Skip Onboarding

```
User: "skip onboarding"
CORTEX: Creates default profile → Proceeds to main interface
```

### Resume Onboarding

```
User: "continue onboarding"
CORTEX: Resumes from last completed step
```

### Reset Profile

```
User: "reset profile"
CORTEX: Confirms action → Deletes profile → Restarts onboarding
```

---

## Configuration

**Onboarding Settings:**
- Auto-start: Enabled (first activation)
- Skippable: Yes
- Resumable: Yes
- Profile required: Yes
- Tutorial auto-launch: Optional

**Default Values:**
- Experience: Mid
- Interaction Mode: Guided
- Tech Stack: No Preference

---

## Profile Storage

**Location:** `cortex-brain/tier3-development-context.db`

**Schema:**
```sql
CREATE TABLE user_profiles (
  profile_id TEXT PRIMARY KEY,
  experience_level TEXT,
  interaction_mode TEXT,
  tech_stack_preference TEXT,
  onboarding_completed BOOLEAN,
  onboarding_step INTEGER,
  created_at TEXT,
  updated_at TEXT
);
```

---

## Implementation Details

**Class:** `OnboardingOrchestrator`

**Key Methods:**
- `execute(context)` - Main onboarding orchestration
- `_check_profile_exists()` - Detect first-time user
- `_show_welcome()` - Welcome message
- `_collect_profile_data()` - 3-question survey
- `_setup_repository()` - Initial configuration
- `_introduce_features()` - Feature demos
- `_recommend_learning_path()` - Personalized suggestions
- `_complete_onboarding()` - Save profile and finish

---

## Onboarding Metrics

**Tracked Metrics:**
- Completion rate (target: >90%)
- Time to complete (average: 3-5 minutes)
- Skip rate (target: <10%)
- Profile customization rate
- Tutorial launch rate after onboarding

**Analytics:**
- Experience level distribution
- Most common interaction mode
- Tech stack preferences
- Feature adoption after onboarding

---

## Error Handling

**Common Issues:**
1. **Database write failure** → Falls back to in-memory profile
2. **User interrupts onboarding** → Saves progress, allows resume
3. **Invalid profile data** → Uses defaults, logs warning
4. **Repository setup fails** → Continues with profile only, logs issue

---

## Testing

**Test Coverage:** 60% (needs improvement)

**Test Files:**
- `tests/operations/test_onboarding_orchestrator.py` (planned)

**Manual Validation:**
1. Delete existing profile
2. Activate CORTEX
3. Complete onboarding flow
4. Verify profile saved correctly
5. Check repository setup successful
6. Validate welcome message appropriate

---

## Related Modules

- **UserProfileManager** - Profile storage and retrieval
- **SetupEPMOrchestrator** - Repository configuration
- **HandsOnTutorialOrchestrator** - Interactive tutorial
- **DemoOrchestrator** - Feature demonstrations

---

## Troubleshooting

**Issue:** Onboarding starts every time  
**Solution:** Check profile database exists and is readable

**Issue:** Profile questions skipped  
**Solution:** Verify interactive mode enabled, not in batch mode

**Issue:** Repository setup fails  
**Solution:** Check write permissions on project directory

---

## Learning Paths

**Beginner Path (Junior/Mid):**
1. Complete hands-on tutorial (30 min)
2. Try planning a simple feature (15 min)
3. Use TDD workflow for one test (20 min)
4. Explore help commands (10 min)

**Intermediate Path (Senior):**
1. Review TDD Mastery guide (10 min)
2. Plan complex feature with DoR/DoD (20 min)
3. Use architecture review (15 min)
4. Explore advanced commands (15 min)

**Expert Path (Expert):**
1. Architecture intelligence review (20 min)
2. System optimization (15 min)
3. Custom workflow creation (30 min)
4. Contribute to CORTEX enhancements (optional)

---

## Personalization Examples

**Junior Developer (Educational Mode):**
- Detailed explanations for every action
- Links to learning resources
- Step-by-step guidance
- Encouragement and positive reinforcement

**Expert Developer (Autonomous Mode):**
- Minimal explanation
- Direct execution
- Advanced options presented upfront
- Assumes deep knowledge

**Azure Stack Preference:**
- Examples use Azure DevOps, AKS
- ARM templates in code samples
- Azure-specific recommendations
- Deployment examples target Azure

---

## Future Enhancements

**Planned (CORTEX 4.0):**
- Interactive onboarding with real-time validation
- Visual setup wizard with progress indicators
- Team onboarding (shared profiles)
- Custom onboarding flows per organization
- Onboarding analytics dashboard
- A/B testing for onboarding variations

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)  
**Last Updated:** November 28, 2025  
**Guide Version:** 1.0.0
