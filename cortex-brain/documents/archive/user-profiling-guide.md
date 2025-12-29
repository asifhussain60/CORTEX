# User Profiling System Guide

**CORTEX 3.6.0** - Personalized AI assistance through adaptive user profiles

---

## 🎯 Overview

CORTEX User Profiling System adapts responses based on your experience level, work domain, and communication preferences. Profiles are stored in `cortex.config.json` and automatically influence template selection and response formatting.

**Benefits:**
- 🎨 **Personalized responses** matched to your experience level
- ⚡ **Faster workflows** with domain-specific templates
- 🌍 **Multi-language support** for international teams
- 🔄 **Profile sharing** across multiple projects

---

## 📋 Profile Schema

### UserProfile Data Model

```python
from pydantic import BaseModel
from typing import Literal

class UserProfile(BaseModel):
    """User profile with validated fields."""
    
    name: str  # Your name
    preference: Literal["concise", "verbose", "balanced"]  # Response style
    role: Literal["beginner", "intermediate", "expert"]  # Experience level
    work_area: Literal[
        "backend", "frontend", "fullstack",
        "web_dev", "data_science", "ai_ml",
        "devops", "mobile", "general"
    ]  # Primary work domain
    language: str = "en"  # Preferred language (ISO 639-1 code)
```

### Field Descriptions

| Field | Type | Options | Impact |
|-------|------|---------|--------|
| **name** | string | Any name | Used in personalized greetings |
| **preference** | Literal | concise, verbose, balanced | Response length and detail level |
| **role** | Literal | beginner, intermediate, expert | Technical depth and explanation style |
| **work_area** | Literal | 9 domains | Template selection and code examples |
| **language** | string | en, es, fr, de, etc. | Response language |

---

## 🎨 Profile Impact on Responses

### Response Style (preference)

**Concise:**
```markdown
# 🧠 CORTEX Response

Created `user_service.py` with 3 methods. Tests passing (10/10).

**Next:** Deploy to staging.
```

**Verbose:**
```markdown
# 🧠 CORTEX Response

I've successfully created the user service module at `src/services/user_service.py`.
The module includes three core methods:

1. `create_user(data)` - Validates and creates new user records
2. `get_user(id)` - Retrieves user by ID with caching
3. `update_user(id, data)` - Updates user with validation

All 10 unit tests are passing, including:
- Input validation tests (4 tests)
- Database interaction tests (3 tests)  
- Error handling tests (3 tests)

**Next Steps:**
1. Review the implementation in `src/services/user_service.py`
2. Run integration tests with `pytest tests/integration/`
3. Deploy to staging environment once approved
```

**Balanced:** (default)
```markdown
# 🧠 CORTEX Response

Created `user_service.py` with 3 methods (create, get, update).
Tests passing: 10/10 (validation, DB, errors).

**Files Modified:**
- `src/services/user_service.py` (new)
- `tests/test_user_service.py` (new)

**Next:** Review implementation, run integration tests, deploy to staging.
```

### Technical Depth (role)

**Beginner:**
- Step-by-step explanations
- Code comments included
- Links to documentation
- Safety warnings for risky operations

**Intermediate:** (default)
- Assumes basic knowledge
- Focuses on implementation details
- Minimal comments
- References to best practices

**Expert:**
- Concise technical language
- Advanced patterns assumed
- Performance optimizations
- Architecture discussions

### Domain Focus (work_area)

**Backend:**
- Server-side code examples
- Database patterns
- API design
- Authentication/authorization

**Frontend:**
- Component patterns
- State management
- Styling approaches
- Browser APIs

**Data Science:**
- DataFrame operations
- Statistical methods
- Visualization code
- Model training patterns

**AI/ML:**
- Neural network architectures
- Training workflows
- Hyperparameter tuning
- Model evaluation

---

## 🚀 Creating Your Profile

### Interactive Setup

```bash
# Run setup wizard
python3 src/setup/setup_wizard.py

# Wizard prompts:
# 1. What's your name? → Your Name
# 2. Response style? (concise/verbose/balanced) → balanced
# 3. Experience level? (beginner/intermediate/expert) → intermediate
# 4. Primary work area? (backend/frontend/etc.) → backend
# 5. Preferred language? (en/es/fr/etc.) → en
```

### Programmatic Creation

```python
from src.setup.models.user_profile import UserProfile
from src.setup.modules.user_profile_storage import UserProfileStorage

# Create profile
profile = UserProfile(
    name="Jane Developer",
    preference="balanced",
    role="expert",
    work_area="backend",
    language="en"
)

# Save to config
storage = UserProfileStorage("cortex.config.json")
storage.save_profile(profile)
```

### Manual Configuration

Edit `cortex.config.json` directly:

```json
{
  "user": {
    "name": "Jane Developer",
    "preference": "balanced",
    "role": "expert",
    "work_area": "backend",
    "language": "en"
  }
}
```

---

## 🔄 Profile Management

### View Current Profile

```bash
# CLI command
cortex profile show

# Output:
# 📋 User Profile
# Name: Jane Developer
# Preference: balanced
# Role: expert
# Work Area: backend
# Language: en
```

### Update Profile

```bash
# Update specific field
cortex profile set preference verbose
cortex profile set role intermediate
cortex profile set work_area fullstack

# Or edit config directly
nano cortex.config.json
```

### Profile Validation

```bash
# Validate profile matches schema
cortex profile validate

# Output:
# ✅ Profile valid
# ✅ All fields present
# ✅ Values within allowed options
```

---

## 🌍 Multi-Language Support

### Supported Languages

| Code | Language | Status |
|------|----------|--------|
| `en` | English | ✅ Full support |
| `es` | Spanish | ⏳ Planned |
| `fr` | French | ⏳ Planned |
| `de` | German | ⏳ Planned |
| `ja` | Japanese | ⏳ Planned |
| `zh` | Chinese | ⏳ Planned |

### Setting Language

```python
profile = UserProfile(
    name="María García",
    preference="verbose",
    role="intermediate",
    work_area="web_dev",
    language="es"  # Spanish responses
)
```

**Note:** Full multi-language support coming in CORTEX 3.7

---

## 🔗 Template Integration

### How Profiles Affect Template Selection

```python
from src.utils.template_selector import TemplateSelector

selector = TemplateSelector()

# Profile influences template selection
template = selector.select_template(
    intent="code_generation",
    user_profile=profile  # Automatically loaded from config
)

# Backend expert with concise preference:
# → Uses backend-specific template
# → Applies concise formatting
# → Includes advanced patterns
```

### Template Priority

1. **Intent match** (code_generation, debug, planning, etc.)
2. **work_area match** (backend templates for backend profile)
3. **role adaptation** (complexity level)
4. **preference formatting** (response length)

---

## 🛡️ Privacy & Security

### Data Storage

- **Location:** `cortex.config.json` (local only)
- **No cloud sync** unless explicitly configured
- **Git-ignored** by default (`.gitignore` includes config)
- **No PII** beyond name (optional)

### Sharing Profiles

```bash
# Export profile (anonymized)
cortex profile export --anonymize > my-profile.json

# Import profile
cortex profile import my-profile.json

# Team profile template
cortex profile export --template > team-template.json
```

---

## 📊 Profile Analytics

### Usage Tracking

CORTEX tracks profile effectiveness (opt-in):

```json
{
  "user": {
    "name": "Jane Developer",
    "preference": "balanced",
    "role": "expert",
    "work_area": "backend",
    "language": "en",
    "analytics": {
      "enabled": true,  # Opt-in
      "responses_generated": 1247,
      "preferred_style_success_rate": 0.94,
      "last_updated": "2025-01-29"
    }
  }
}
```

### Insights

```bash
# View profile effectiveness
cortex profile insights

# Output:
# 📊 Profile Insights (Last 30 days)
# - Responses generated: 1,247
# - Style match rate: 94%
# - Most used templates: code_generation (42%), debug (28%)
# - Recommendation: Consider "concise" for faster workflows
```

---

## 🔄 Migration & Backward Compatibility

### Upgrading from 3.5

```bash
# Automatic migration during upgrade
cortex upgrade

# Creates default profile if missing:
{
  "user": {
    "name": "CORTEX User",
    "preference": "balanced",
    "role": "intermediate",
    "work_area": "general",
    "language": "en"
  }
}
```

### No Profile Behavior

If no profile exists, CORTEX uses safe defaults:
- **preference:** balanced
- **role:** intermediate  
- **work_area:** general
- **language:** en

---

## 📚 Related Documentation

- **Shared Environment Setup:** `shared-environment-setup.md`
- **Plan Management Guide:** `plan-management-guide.md`
- **Response Template System:** `cortex-brain/response-templates.yaml`
- **Template Selector:** `src/utils/template_selector.py`

---

**Version:** 3.6.0  
**Last Updated:** 2025-01-29  
**Author:** Asif Hussain
