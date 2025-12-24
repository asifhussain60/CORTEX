# User Profile System Schema

**Version:** 3.2.1  
**Status:** Implementation Complete  
**Created:** 2025-11-28  
**Updated:** 2025-11-28

---

## Overview

Lightweight user profiling system that adapts CORTEX behavior based on user preferences and company tech stack. Stores minimal data (~150 bytes) in Tier 1 with FIFO exemption for permanent retention.

**Key Features:**
- **Interaction Modes:** 4 modes (autonomous, guided, educational, pair)
- **Experience Levels:** 4 levels (junior, mid, senior, expert)
- **Tech Stack Preference:** Optional JSON field with cloud provider, container platform, architecture, CI/CD, and IaC preferences
- **Context-Not-Constraint:** Tech stack enriches templates without filtering recommendations

---

## Profile Schema

### JSON Structure

```json
{
  "interaction_mode": "guided",
  "experience_level": "senior",
  "tech_stack_preference": {
    "cloud_provider": "azure",
    "container_platform": "kubernetes",
    "architecture": "microservices",
    "ci_cd": "azure_devops",
    "iac": "terraform"
  },
  "created_at": "2025-11-28T10:30:00Z",
  "last_updated": "2025-11-28T10:30:00Z"
}
```

### Field Definitions

**interaction_mode** (string, required)
- Allowed values: `autonomous` | `guided` | `educational` | `pair`
- Default: `guided`
- Description: How user prefers to interact with CORTEX

**experience_level** (string, required)
- Allowed values: `junior` | `mid` | `senior` | `expert`
- Default: `mid`
- Description: User's development experience level

**tech_stack_preference** (JSON object, optional)
- Default: `null` (no preference - CORTEX decides)
- Description: Company/project tech stack for deployment context (NOT a constraint)
- Nested fields (all optional):
  - `cloud_provider`: `azure` | `aws` | `gcp` | `none`
  - `container_platform`: `kubernetes` | `docker` | `none`
  - `architecture`: `microservices` | `monolithic` | `hybrid`
  - `ci_cd`: `azure_devops` | `github_actions` | `jenkins` | `none`
  - `iac`: `terraform` | `arm` | `cloudformation` | `none`

**created_at** (ISO 8601 datetime, required)
- Format: `YYYY-MM-DDTHH:MM:SSZ`
- Auto-generated on profile creation
- Immutable after creation

**last_updated** (ISO 8601 datetime, required)
- Format: `YYYY-MM-DDTHH:MM:SSZ`
- Auto-updated on any profile modification
- Used for audit trail

---

## Database Schema (Tier 1)

### Table: user_profile

```sql
CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY CHECK (id = 1),  -- Single row constraint
    interaction_mode TEXT NOT NULL CHECK(interaction_mode IN ('autonomous', 'guided', 'educational', 'pair')),
    experience_level TEXT NOT NULL CHECK(experience_level IN ('junior', 'mid', 'senior', 'expert')),
    tech_stack_preference TEXT,  -- JSON string, nullable
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_updated TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    persistent_flag BOOLEAN NOT NULL DEFAULT 1  -- FIFO exemption marker
);

-- Ensure only one profile exists
CREATE UNIQUE INDEX IF NOT EXISTS idx_single_profile ON user_profile(id);
```

### Design Decisions

**Single Row Constraint:**
- Only one profile per CORTEX installation
- Enforced via `CHECK (id = 1)` and unique index
- Simplifies queries (no user ID needed)

**Tech Stack as JSON:**
- Stored as TEXT in SQLite (JSON string)
- Allows flexible schema without ALTER TABLE migrations
- Empty dict `{}` and `null` both stored as NULL (no preference)
- Validated in application layer before serialization

**FIFO Exemption:**
- `persistent_flag = 1` marks profile as exempt from Tier 1 cleanup
- Profile survives indefinitely (not subject to 70-conversation FIFO)
- QueueManager respects this flag during eviction

**Validation:**
- CHECK constraints enforce allowed values at database level (interaction_mode, experience_level)
- Application-level validation for tech_stack_preference nested fields
- No invalid data can be inserted

---

## Tech Stack Preference

### Purpose: Context NOT Constraint

**CRITICAL PRINCIPLE:** Tech stack preference provides deployment context for CORTEX. It does **NOT** filter or constrain recommendations.

**How It Works:**
1. User specifies company/project tech stack during onboarding
2. CORTEX includes tech stack context in response templates
3. Responses show **BOTH**:
   - Best practice recommendation (tech-agnostic)
   - Deployment guidance for company tech stack

**Example Response Structure:**
```markdown
## 💡 Best Practice Recommendation
Use container orchestration with Kubernetes for scalability...

## 🏢 Deployment with Your Tech Stack (Azure)
Since your company uses Azure, here's how to deploy:
- Azure Kubernetes Service (AKS) for container orchestration
- Azure DevOps for CI/CD pipelines
- ARM templates or Terraform for infrastructure
```

### Tech Stack Fields

**cloud_provider** (optional)
- `azure` - Microsoft Azure
- `aws` - Amazon Web Services
- `gcp` - Google Cloud Platform
- `none` - On-premises or no cloud

**container_platform** (optional)
- `kubernetes` - Kubernetes (K8s)
- `docker` - Docker (without orchestration)
- `none` - No containerization

**architecture** (optional)
- `microservices` - Distributed microservices
- `monolithic` - Single monolithic application
- `hybrid` - Mix of both

**ci_cd** (optional)
- `azure_devops` - Azure DevOps (formerly VSTS)
- `github_actions` - GitHub Actions
- `jenkins` - Jenkins CI/CD
- `none` - Manual deployment or other tools

**iac** (optional)
- `terraform` - HashiCorp Terraform
- `arm` - Azure Resource Manager templates
- `cloudformation` - AWS CloudFormation
- `none` - Manual infrastructure or other tools

### Preset Configurations

**Azure Stack:**
```json
{
  "cloud_provider": "azure",
  "container_platform": "kubernetes",
  "architecture": "microservices",
  "ci_cd": "azure_devops",
  "iac": "arm"
}
```

**AWS Stack:**
```json
{
  "cloud_provider": "aws",
  "container_platform": "kubernetes",
  "architecture": "microservices",
  "ci_cd": "github_actions",
  "iac": "terraform"
}
```

**GCP Stack:**
```json
{
  "cloud_provider": "gcp",
  "container_platform": "kubernetes",
  "architecture": "microservices",
  "ci_cd": "github_actions",
  "iac": "terraform"
}
```

**No Preference:**
```json
null  // or {}
```
CORTEX decides based on best practice for the specific use case.

---

## Interaction Modes

### Autonomous Mode
**User Persona:** "Just do it, show me results"  
**Response Style:** Compact, action-focused  
**Format Changes:**
- Skips "Understanding" section
- Minimal explanation
- Results-first approach

**Example Response:**
```markdown
## 🧠 CORTEX Feature Implementation (No Challenge)

💬 **Response:** Authentication feature implemented with JWT tokens. Login/logout routes added to `src/routes/auth.py`. Tests passing.

📝 **Your Request:** Implement user authentication

🔍 **Next Steps:**
1. Test login flow manually
2. Configure token expiration
3. Add password reset feature
```

### Guided Mode (Default)
**User Persona:** "Explain what you're doing, collaborate with me"  
**Response Style:** Balanced, full 5-part structure  
**Format Changes:** None (current CORTEX behavior)

**Example Response:**
```markdown
## 🧠 CORTEX Feature Implementation

### 🎯 My Understanding Of Your Request
You want to add user authentication with login/logout functionality.

### ⚠️ Challenge
No Challenge

### 💬 Response
I've implemented JWT-based authentication with secure password hashing...

### 📝 Your Request
Implement user authentication

### 🔍 Next Steps
1. Test login flow
2. Configure token settings
3. Add password reset
```

### Educational Mode
**User Persona:** "Teach me why, show alternatives"  
**Response Style:** Explanatory, includes rationale  
**Format Changes:**
- Adds "Why This Approach" subsection to Response
- Explains trade-offs and alternatives
- More detailed next steps with learning objectives

**Example Response:**
```markdown
## 🧠 CORTEX Feature Implementation

### 🎯 My Understanding Of Your Request
You want to add user authentication...

### ⚠️ Challenge
No Challenge

### 💬 Response
I've implemented JWT-based authentication...

**Why This Approach:**
JWT tokens are stateless, making them ideal for distributed systems. Alternative approaches include:
- Session cookies (simpler but requires server-side storage)
- OAuth2 (better for third-party integration)
- API keys (simpler but less secure)

We chose JWT because your app is stateless and may scale horizontally in the future.

### 📝 Your Request
Implement user authentication

### 🔍 Next Steps
1. Test login flow (learn: JWT structure and validation)
2. Configure token settings (learn: security best practices)
3. Add password reset (learn: secure token generation)
```

### Pair Programming Mode
**User Persona:** "Ask me questions first, validate understanding"  
**Response Style:** Interactive, question-first  
**Format Changes:**
- Adds "Clarifying Questions" section before execution
- Validates requirements before implementing
- More collaborative decision-making

**Example Response:**
```markdown
## 🧠 CORTEX Feature Planning

### 🎯 My Understanding Of Your Request
You want to add user authentication...

### ⚠️ Clarifying Questions
Before I implement, I need to understand:

1. **Token Type:** JWT tokens (stateless) or session cookies (server-side)?
2. **Password Storage:** bcrypt, argon2, or PBKDF2 for hashing?
3. **Token Expiration:** How long should tokens remain valid? (1 hour, 24 hours, custom?)
4. **Password Reset:** Email-based or admin-managed?
5. **Multi-Factor Auth:** Needed now or future enhancement?

Please answer these questions, or say "use defaults" for standard secure configuration.

### 📝 Your Request
Implement user authentication
```

---

## Experience Levels

### Junior
**Characteristics:**
- More safety warnings before destructive operations
- Suggests safeguards (backups, checkpoints)
- Explains trade-offs explicitly
- Additional validation prompts

**Behavioral Changes:**
- Git operations: Prompts for backup before risky operations
- Code generation: Adds more inline comments
- Testing: Suggests test cases explicitly
- Refactoring: Warns about potential breaking changes

### Mid (Default)
**Characteristics:**
- Balanced approach
- Assumes solid fundamentals
- Standard validation

**Behavioral Changes:**
- Current CORTEX behavior (no changes)

### Senior
**Characteristics:**
- Trusts user judgment
- Less hand-holding
- Assumes understanding of common patterns

**Behavioral Changes:**
- Skips basic explanations
- Fewer confirmation prompts for standard operations
- More concise responses

### Expert
**Characteristics:**
- Minimal guidance
- Fast-tracks common operations
- Assumes deep context understanding

**Behavioral Changes:**
- Maximum autonomy
- Skips validation for routine operations
- Ultra-concise responses
- Assumes user will review code/changes independently

---

## Validation Rules

### Interaction Mode Validation

```python
VALID_MODES = ["autonomous", "guided", "educational", "pair"]

def validate_interaction_mode(mode: str) -> tuple[bool, str]:
    """
    Validate interaction mode.
    
    Returns:
        (is_valid, error_message)
    """
    if not mode:
        return False, "Interaction mode cannot be empty"
    
    if mode not in VALID_MODES:
        return False, f"Invalid mode '{mode}'. Must be one of: {', '.join(VALID_MODES)}"
    
    return True, ""
```

### Experience Level Validation

```python
VALID_LEVELS = ["junior", "mid", "senior", "expert"]

def validate_experience_level(level: str) -> tuple[bool, str]:
    """
    Validate experience level.
    
    Returns:
        (is_valid, error_message)
    """
    if not level:
        return False, "Experience level cannot be empty"
    
    if level not in VALID_LEVELS:
        return False, f"Invalid level '{level}'. Must be one of: {', '.join(VALID_LEVELS)}"
    
    return True, ""
```

---

## FIFO Exemption Implementation

### QueueManager Integration

The `QueueManager` class in `src/tier1/fifo.py` will be updated to check the `persistent_flag` before evicting conversations:

```python
def _should_exempt_from_fifo(self, conversation_id: str) -> bool:
    """
    Check if conversation should be exempt from FIFO eviction.
    
    Returns:
        True if conversation is user profile (persistent_flag=1)
    """
    # Check if this is the user profile record
    cursor.execute("""
        SELECT persistent_flag FROM user_profile 
        WHERE id = 1
    """)
    result = cursor.fetchone()
    
    return result is not None and result[0] == 1
```

### Storage Size Calculation

**Profile Size:**
- interaction_mode: ~12 bytes (avg)
- experience_level: ~6 bytes (avg)
- created_at: ~25 bytes (ISO 8601)
- last_updated: ~25 bytes (ISO 8601)
- **Total:** ~68 bytes per profile

**Impact on Tier 1:**
- Single profile = 68 bytes
- Negligible impact on database size
- No performance degradation

---

## Migration Strategy

### First-Time Installation
- Database table created during `_init_database()`
- No profile exists initially
- Onboarding triggers on first user interaction

### Existing Installations
- Migration script adds `user_profile` table
- No data loss (existing conversations unaffected)
- Backward compatible (profile is optional)

### Rollback Strategy
- Profile table can be dropped without affecting core functionality
- CORTEX falls back to default behavior (guided mode, mid experience)
- No cascade effects on other tables

---

## Privacy & Security

### Data Storage
- All data stored locally in SQLite (Tier 1)
- No cloud sync, no external transmission
- User controls all data

### Data Collection
- Minimal data (4 fields only)
- No PII (personally identifiable information)
- No telemetry or analytics

### User Control
- Profile creation optional (can skip onboarding)
- Update anytime via `update profile` command
- Delete profile with `clear profile` command
- Transparent storage (SQLite file accessible)

---

## Testing Requirements

### Unit Tests
1. Profile creation with valid data
2. Profile creation with invalid data (constraint violations)
3. Profile update (single field)
4. Profile update (multiple fields)
5. Profile retrieval (existing profile)
6. Profile retrieval (no profile exists)
7. FIFO exemption validation
8. Single row constraint enforcement (can't create multiple profiles)
9. Timestamp auto-update on modification
10. Default value handling

### Integration Tests
1. Onboarding flow end-to-end
2. Profile injection into AgentRequest
3. Mode-aware response template selection
4. Experience level safety warnings
5. Profile persistence across sessions
6. Profile update command workflow

### Target Coverage
- 95%+ code coverage for profile module
- All validation paths tested
- Edge cases covered (null values, SQL injection attempts, concurrent updates)

---

## Performance Considerations

### Query Performance
- Single row table = O(1) lookup
- No joins required (self-contained profile)
- Index on `id` for instant retrieval
- Estimated query time: <1ms

### Memory Footprint
- 68 bytes in database
- ~200 bytes in memory (Python object overhead)
- Negligible impact on Tier 1 performance

### Concurrency
- Single profile = no concurrent user conflicts
- SQLite handles concurrent reads efficiently
- Write operations rare (only on create/update)

---

## Future Enhancements (Post-3.2.1)

### Version 4.0 Candidates
1. **Multi-User Support:** Tier 4 with user identity system
2. **Preference Learning:** ML-based preference refinement over time
3. **Cross-Project Profiles:** Sync preferences across multiple repositories
4. **Advanced Modes:** Custom interaction modes defined by users
5. **Profile Analytics:** Usage patterns and effectiveness tracking
6. **Team Profiles:** Shared team preferences for organizations

### Not Planned
- Social features (profile sharing, ratings)
- Cloud backup of profiles
- AI-generated profile recommendations
- Integration with external identity providers

---

## Appendix: Example Queries

### Create Profile
```sql
INSERT INTO user_profile (id, interaction_mode, experience_level)
VALUES (1, 'guided', 'mid')
ON CONFLICT(id) DO UPDATE SET
    interaction_mode = excluded.interaction_mode,
    experience_level = excluded.experience_level,
    last_updated = CURRENT_TIMESTAMP;
```

### Retrieve Profile
```sql
SELECT interaction_mode, experience_level, created_at, last_updated
FROM user_profile
WHERE id = 1;
```

### Update Mode Only
```sql
UPDATE user_profile
SET interaction_mode = 'autonomous',
    last_updated = CURRENT_TIMESTAMP
WHERE id = 1;
```

### Check Profile Exists
```sql
SELECT COUNT(*) FROM user_profile WHERE id = 1;
```

---

**Schema Status:** ✅ Approved for Implementation  
**Next Step:** Implement Profile CRUD in Tier 1 (Todo #2)
