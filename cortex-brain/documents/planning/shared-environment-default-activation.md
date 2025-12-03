---
plan_id: CORTEX-SETUP-001
title: Shared Environment + User Profiling + Planning + File Naming
status: proposed
priority: high
created_date: 2025-12-03T00:00:00Z
updated_date: 2025-12-03T00:00:00Z
created_by: Asif Hussain
estimated_hours: 160
actual_hours: 0
completion_percentage: 0
tags: [setup, shared-environment, user-profiling, planning-infrastructure, ux-enhancement, file-naming, governance, realignment, multilingual, i18n, code-language-enforcement]
dependencies: []
blocked_by: []
related_plans: []
---

# Feature Plan: Shared Environment Default Activation + User Profiling

**Feature ID:** CORTEX-SETUP-001  
**Version:** 1.5  
**Status:** Planning Complete  
**Created:** 2025-12-03  
**Updated:** 2025-12-03 (Added code language enforcement: Task 3.6 + unified pre-commit hook in Task 8.7)  
**Author:** Asif Hussain  
**Planning System:** CORTEX Planning System 2.0  
**Current Filename:** `shared-environment-default-activation.md` (41 chars)  
**Target Filename:** `PLAN-001-shared-env-setup.md` (27 chars, -34%)  
**Location:** `cortex-brain/documents/planning/` → Will move to `features/active/` in Phase 6

---

## 📋 Executive Summary

Transform CORTEX setup to use shared environment (`~/.cortex/venv/`) as default, add interactive user profiling during setup, wire response templates based on preferences, and validate all enhancements with alignment orchestrator.

**Current State:** Dormant shared environment code, manual flags required, intelligent single-project venv as default, no user profiling

**Target State:** Auto-shared environment setup, sub-5-second project linking, personalized responses, complete setup validation

**Impact:** 83% setup time reduction (270 seconds saved per project), personalized UX, zero documentation mismatch

---

## ✅ Definition of Ready (DoR) - VALIDATED

### 1. Feature Objectives

| Component | What | Why | Success Criteria |
|-----------|------|-----|-----------------|
| **Shared Environment** | Make `~/.cortex/venv/` default setup | Reduce 10x installations to 1x + linking | First-time: 30s, subsequent: <5s |
| **User Profiling** | Interactive session: name, preference, role, work area, language (5 questions) | Personalized responses in user's native language | Profile stored, templates selected |
| **Response Wiring** | Auto-select templates based on profile + language (72 variants) | Match response style and language to user needs | Correct language/style applied |
| **Multilingual Support** | 12 languages with translated section headers, English technical content | Global accessibility, inclusive UX | All languages working, fallbacks functional |
| **Alignment Validation** | Final orchestrator run validating all features | Zero setup issues, production-ready | All checks pass, no manual fixes needed |
| **Planning Infrastructure** | Lightweight plan registry, status tracking, lookup API | Organized plan management, easy retrieval | Plans indexed, searchable, status-tracked |
| **File Naming Governance** | Tier 0 rules for optimal filename lengths (10-45 chars) | Maintainable codebase, better VS Code UX | All files within limits, no tab overflow |

### 2. Technical Requirements (DoR Answers)

**Q1: Migration Strategy** → **A (Auto-migrate)**
- Detect existing `.venv` during setup
- Create shared environment
- Link project automatically
- Remove old `.venv` after validation

**Q2: Dependency Isolation** → **Keep `.project-site-packages/` pattern**
- Project-specific deps remain isolated
- No cross-project contamination
- Shared tooling (pytest, PyYAML) in `~/.cortex/venv/`

**Q3: Python Version Support** → **C (Auto-detect with version-specific shared venvs)**
- **Rationale:** Most efficient and optimal
- Pattern: `~/.cortex/venv-3.11/`, `~/.cortex/venv-3.12/`
- Auto-detect Python version, create/reuse appropriate shared venv
- Supports multi-version development workflows

**Q4: Rollback Strategy** → **A (Fall back to single-project `.venv`)**
- If shared env creation fails → create `.venv` in project
- Log warning, continue setup
- Graceful degradation, never block user

**Q5: Integration Architecture** → **B (Enhance existing `PythonEnvironmentModule`)**
- **Rationale:** Most efficient and optimal
- Add shared environment detection to existing module
- Reuse dependency checking, conflict resolution logic
- Minimal code duplication, leverages proven patterns

### 3. User Profile Design

**Interactive Session Questions:**

```
Welcome to CORTEX Setup! Let's personalize your experience.

1. What's your name?
   → [Free text input]

2. Response preference?
   V) Verbose - Detailed explanations with examples
   C) Concise - Brief, action-focused responses
   → [V/C]

3. What's your role?
   J) Junior Engineer (0-2 years)
   I) Mid-Level Engineer (3-5 years)
   S) Senior Engineer (6-10 years)
   P) Principal/Staff Engineer (10+ years)
   M) Engineering Manager/Lead
   → [J/I/S/P/M]

4. Primary work area?
   B) Backend Development
   F) Frontend Development
   D) DevOps/Infrastructure
   A) Full-Stack/All Areas
   → [B/F/D/A]

5. Preferred response language?
   EN) English
   ES) Español (Spanish)
   FR) Français (French)
   DE) Deutsch (German)
   PT) Português (Portuguese)
   ZH) 中文 (Chinese - Simplified)
   JA) 日本語 (Japanese)
   KO) 한국어 (Korean)
   HI) हिन्दी (Hindi)
   AR) العربية (Arabic)
   RU) Русский (Russian)
   IT) Italiano (Italian)
   → [EN/ES/FR/DE/PT/ZH/JA/KO/HI/AR/RU/IT]
   
   Note: All technical terms, code, and file paths remain in English.
   Only explanations, instructions, and commentary will be translated.
```

**Profile Storage:**
```json
{
  "user_profile": {
    "name": "John Doe",
    "response_preference": "concise",
    "role": "senior",
    "experience_level": "6-10 years",
    "work_area": "backend",
    "language": "en",
    "language_name": "English",
    "profile_version": "2.0",
    "created_at": "2025-12-03T10:30:00Z",
    "updated_at": "2025-12-03T14:00:00Z"
  }
}
```

**Storage Location:** `cortex.config.json` (machine-specific, not committed)

### 4. Response Template Wiring

**Template Selection Matrix (Per Language):**

| Preference | Role | Template | Characteristics |
|------------|------|----------|-----------------|
| Verbose | Junior | `standard_5_part_detailed_{lang}` | Full explanations, code examples, conceptual background |
| Verbose | Mid/Senior | `standard_5_part_technical_{lang}` | Architecture focus, trade-offs, best practices |
| Verbose | Principal/Manager | `standard_5_part_strategic_{lang}` | System impact, team implications, business value |
| Concise | Junior | `compact_format_guided_{lang}` | Essential steps, key concepts, clear next actions |
| Concise | Mid/Senior | `compact_format_pro_{lang}` | Technical bullets, minimal context, direct solutions |
| Concise | Principal/Manager | `compact_format_executive_{lang}` | Decisions, risks, outcomes, delegation points |

**Total Templates:** 6 variants × 12 languages = **72 templates**

**Language Coverage:**
- EN (English) - Default, fully supported
- ES (Spanish) - Full support
- FR (French) - Full support
- DE (German) - Full support
- PT (Portuguese) - Full support
- ZH (Chinese Simplified) - Full support
- JA (Japanese) - Full support
- KO (Korean) - Full support
- HI (Hindi) - Full support
- AR (Arabic) - Full support (RTL formatting)
- RU (Russian) - Full support
- IT (Italian) - Full support

**Localization Strategy:**

1. **What Gets Translated:**
   - Section headers (🎯 My Understanding, ⚠️ Challenge, 💬 Response, etc.)
   - Explanations and instructions
   - User-facing messages
   - Error messages and warnings
   - Success messages

2. **What Stays in English:**
   - Code snippets and syntax
   - File paths and filenames
   - Command-line commands
   - Technical terms (API, JSON, YAML, etc.)
   - Variable names and function names
   - Git commands
   - Tool names (pytest, pip, VS Code, etc.)

3. **Hybrid Example (Spanish):**
   ```markdown
   # 🧠 CORTEX Respuesta Técnica
   
   ## 🎯 Mi Comprensión de tu Solicitud
   Deseas actualizar el archivo `src/main.py` para agregar logging.
   
   ## 💬 Respuesta
   Voy a modificar la función `main()` para incluir el módulo `logging`:
   
   ```python
   import logging
   logging.basicConfig(level=logging.INFO)
   ```
   
   Este cambio permite registrar eventos en tiempo de ejecución.
   ```

**Template Loading Logic:**
```python
def select_response_template(user_profile: dict) -> str:
    preference = user_profile.get("response_preference", "verbose")
    role = user_profile.get("role", "mid")
    language = user_profile.get("language", "en")
    
    # Build template key with language suffix
    base_template = f"{preference}_{role}_response"
    template_key = f"{base_template}_{language}"
    
    # Fallback hierarchy: exact match → English variant → default
    if template_key not in templates:
        template_key = f"{base_template}_en"  # Fall back to English
    if template_key not in templates:
        template_key = f"{preference}_default_en"
    if template_key not in templates:
        template_key = "standard_5_part_en"  # Ultimate fallback
    
    return template_key

# Example usage
user_profile = {
    "response_preference": "concise",
    "role": "senior",
    "language": "es"  # Spanish
}
template = select_response_template(user_profile)
# Returns: "concise_senior_response_es"
```

**Translation Implementation:**

```python
# cortex-brain/response-templates.yaml structure
templates:
  standard_5_part_detailed_en:
    sections:
      - header: "# 🧠 CORTEX {operation_type}"
      - understanding: "## 🎯 My Understanding Of Your Request"
      - challenge: "## ⚠️ Challenge"
      - response: "## 💬 Response"
      - request_echo: "## 📝 Your Request"
      - next_steps: "## 🔍 Next Steps"
  
  standard_5_part_detailed_es:
    sections:
      - header: "# 🧠 CORTEX {operation_type}"
      - understanding: "## 🎯 Mi Comprensión de tu Solicitud"
      - challenge: "## ⚠️ Desafío"
      - response: "## 💬 Respuesta"
      - request_echo: "## 📝 Tu Solicitud"
      - next_steps: "## 🔍 Próximos Pasos"
  
  # ... 70 more templates (6 variants × 12 languages)
```

### 5. Alignment Orchestrator Integration

**Final Setup Step in SETUP-CORTEX.MD:**

```markdown
### 9️⃣ Validate Setup (NEW)

Run the alignment orchestrator to ensure everything is wired correctly:

In VS Code Copilot Chat:
```
align setup
```

Or via Python:
```bash
python -m src.orchestrators.alignment_orchestrator --mode setup-validation
```

**What Gets Validated:**
✅ Shared environment created and accessible
✅ Project linked to shared environment correctly
✅ User profile configured and stored
✅ Response templates wired to user preferences
✅ Brain tier databases initialized
✅ Git isolation rules active
✅ All CORTEX modules importable
✅ Configuration file valid and complete

**Output:** Comprehensive validation report with ✅/❌ status for each check
```

**Alignment Orchestrator Features:**

- **User-Facing Design:** Clear, actionable output (no technical jargon overload)
- **Auto-Repair:** Attempts to fix common issues automatically
- **Exit Codes:** 0 = success, 1 = manual intervention needed
- **Report Generation:** Creates `cortex-brain/documents/reports/setup-validation-report.md`
- **Integration Score:** 0-100% indicating setup completeness

---

## 🎨 UX Enhancements (Simple, High-Impact)

### 1. Progress Indicators
**What:** Visual feedback during long-running operations  
**Why:** Reduces user anxiety, shows activity not freeze  
**Implementation:** Reuse existing `@with_progress` decorator  
**Complexity:** NONE (already exists in CORTEX)

```python
@with_progress(operation_name="Creating Shared Environment")
def create_shared_venv():
    yield_progress(1, 3, "Creating directory structure")
    # ... code ...
    yield_progress(2, 3, "Installing Python venv")
    # ... code ...
    yield_progress(3, 3, "Verifying environment")
```

**Impact:** Users see "Creating Shared Environment [2/3] Installing Python venv" vs silent 30-second wait

---

### 2. Smart Defaults with Context
**What:** Pre-populate answers based on detected context  
**Why:** Reduces typing, faster setup, intelligent UX  
**Implementation:** Simple detection logic  
**Complexity:** LOW (basic environment checks)

**Examples:**
- Git user.name detected → Pre-fill profile name
- Existing .vscode/settings.json → Suggest role based on workspace complexity
- GitHub CLI authenticated → Extract name from `gh api user`

```
What's your name? [John Doe] ← detected from git config
Response preference? [V] ← default verbose for first-time
```

**Impact:** 50% less typing, feels personalized

---

### 3. Setup Resume Capability
**What:** If setup interrupted, resume from last checkpoint  
**Why:** Network fails, user cancels, don't start over  
**Implementation:** Checkpoint file `.cortex-setup-state.json`  
**Complexity:** LOW (simple state tracking)

```
⚠️  Previous setup incomplete. Resume? (Y/n)
   ✓ Shared environment created
   ✓ Profile configured
   ⏳ Installing dependencies (interrupted)
```

**Impact:** Frustration elimination, professional feel

---

### 4. Setup Time Estimate
**What:** Show estimated time before each phase  
**Why:** Manage expectations, plan coffee breaks  
**Implementation:** Static estimates from benchmarks  
**Complexity:** NONE (just display text)

```
🚀 Starting CORTEX Setup
   Phase 1: Shared Environment (~30 seconds)
   Phase 2: User Profile (~15 seconds)
   Phase 3: Validation (~10 seconds)
   Total: ~1 minute
```

**Impact:** Reduces perceived wait time

---

### 5. Emoji Status Indicators
**What:** Visual status: 🔄 in-progress, ✅ done, ⚠️ warning, ❌ error  
**Why:** Instant visual comprehension, friendly tone  
**Implementation:** Simple string formatting  
**Complexity:** NONE (already used in CORTEX)

```
🔄 Creating shared environment...
✅ Shared environment created
🔄 Configuring user profile...
✅ Profile saved
⚠️  Git not found - skipping name detection
```

**Impact:** Scanning clarity, emotional connection

---

### 6. Undo Last Setup
**What:** Command to revert most recent setup  
**Why:** Made mistake, want fresh start, easy rollback  
**Implementation:** Backup config before changes  
**Complexity:** LOW (copy config, restore function)

```bash
# User realizes they picked wrong options
cortex setup --undo
✅ Setup reverted to previous state
```

**Impact:** Safety net, encourages experimentation

---

### 7. Setup Summary at End
**What:** Recap what was configured, next actions  
**Why:** Confirmation, learning, reference  
**Implementation:** Template with configured values  
**Complexity:** NONE (just echo config)

```
🎉 CORTEX Setup Complete!

📋 Configuration Summary:
   Name: John Doe
   Preference: Concise responses
   Role: Senior Engineer
   Shared Environment: ~/.cortex/venv-3.11/
   Projects Linked: 1

🔍 Next Steps:
   1. Try: "help" to see available commands
   2. Run: "demo" for interactive tutorial
   3. Say: "plan a feature" to start building

⏱️  Setup completed in 42 seconds
```

**Impact:** Satisfying closure, clear next steps

---

### 8. Profile Preview Before Save
**What:** Show profile summary, confirm before saving  
**Why:** Catch mistakes, transparency  
**Implementation:** Print + Y/N confirmation  
**Complexity:** LOW (one extra prompt)

```
📋 Your Profile:
   Name: John Doe
   Preference: Concise (brief, action-focused)
   Role: Senior Engineer (assumes technical knowledge)
   Work Area: Backend Development

This will customize CORTEX responses to match your needs.
Save profile? (Y/n)
```

**Impact:** Reduces setup regret, builds trust

---

### 9. Keyboard Shortcuts in Prompts
**What:** Show [ENTER] for default, common shortcuts  
**Why:** Faster interaction, power user feel  
**Implementation:** Just display hint text  
**Complexity:** NONE (documentation only)

```
Response preference? (V=Verbose, C=Concise) [V]: _
                                            ↑
                                         Press ENTER for Verbose
```

**Impact:** Reduces cognitive load

---

### 10. Setup Mode Selection
**What:** Quick/Standard/Custom setup modes upfront  
**Why:** Different user needs, time constraints  
**Implementation:** One extra prompt at start  
**Complexity:** LOW (conditional flow)

```
🚀 CORTEX Setup

How would you like to proceed?
   Q) Quick Setup (~30 seconds, smart defaults)
   S) Standard Setup (~1 minute, guided questions)
   C) Custom Setup (~2 minutes, full control)

Choose setup mode [S]: _
```

**Quick Mode:** Auto-detect everything, skip profile questions  
**Standard Mode:** Current design (4 questions)  
**Custom Mode:** Additional questions (editor preference, timezone, etc.)

**Impact:** Respects user time, flexibility

---

## 🔒 STRIDE Threat Analysis

### Spoofing
- **Threat:** Malicious user profile injection corrupting config
- **Mitigation:** Input validation, sanitize name field, enum validation for selections
- **Severity:** LOW (local machine access required)

### Tampering
- **Threat:** Corrupted shared venv affecting multiple projects
- **Mitigation:** Hash verification of installed packages, integrity checks during linking
- **Severity:** MEDIUM (impacts all linked projects)

### Repudiation
- **Threat:** No audit trail of setup actions
- **Mitigation:** Log all setup operations to `cortex-brain/admin/setup-audit.log`
- **Severity:** LOW (development tool, not business-critical)

### Information Disclosure
- **Threat:** User profile data exposed in logs or reports
- **Mitigation:** Redact PII from logs, profile stored in local config only
- **Severity:** LOW (local storage, user's own data)

### Denial of Service
- **Threat:** Setup failure blocking CORTEX usage
- **Mitigation:** Fallback to single-project venv, graceful degradation
- **Severity:** MEDIUM (mitigated by fallback strategy)

### Elevation of Privilege
- **Threat:** Setup process requiring sudo/admin unnecessarily
- **Mitigation:** Use user home directory (`~/.cortex/`), no system-wide changes
- **Severity:** BLOCKED (design prevents privilege escalation)

**Overall Risk:** LOW (all threats mitigated or blocked)

---

## 📐 Implementation Phases

### Phase 1: Shared Environment Enhancement (3-5 days)

**Goal:** Make shared environment the default, support multi-version

**Tasks:**

☐ **1.1 Enhance PythonEnvironmentModule**
- Add `_detect_shared_environment()` method
- Add `_create_version_specific_shared_venv(python_version)` method
- Add `_auto_migrate_from_single_project()` method
- Update `execute()` to prioritize shared environment
- **Files:** `src/setup/modules/python_environment_module.py`
- **Tests:** `tests/test_python_environment_module.py`
- **TDD:** RED (tests fail without shared env detection) → GREEN (implement detection) → REFACTOR (extract helpers)

☐ **1.2 Version-Specific Shared Environment**
- Detect Python version: `sys.version_info`
- Create path: `~/.cortex/venv-{major}.{minor}/`
- Check existing shared venv for version match
- Reuse if version matches, create new if different
- **Files:** `src/operations/modules/setup/setup_utility.py` (add `create_versioned_shared_venv()`)
- **Tests:** `tests/test_shared_cortex_environment.py` (add version tests)
- **TDD:** RED (version mismatch test fails) → GREEN (version detection) → REFACTOR (path builders)

☐ **1.3 Auto-Migration Logic**
- Detect existing `.venv` in project root
- Prompt user: "Migrate to shared environment? (Y/n)"
- Create shared venv if doesn't exist
- Link project to shared venv
- Optional: Remove old `.venv` after confirmation
- **Files:** `src/setup/modules/python_environment_module.py`
- **Tests:** `tests/test_migration.py` (new file)
- **TDD:** RED (migration test fails) → GREEN (implement migration) → REFACTOR (cleanup logic)

☐ **1.4 Fallback Strategy**
- Wrap shared venv creation in try-except
- On failure, log warning, create `.venv`
- Store failure reason in context for troubleshooting
- **Files:** `src/setup/modules/python_environment_module.py`
- **Tests:** `tests/test_python_environment_module.py` (add failure scenarios)
- **TDD:** RED (failure test passes incorrectly) → GREEN (add fallback) → REFACTOR (error handling)

☐ **1.5 UX Enhancement: Progress Indicators**
- Add `@with_progress` decorator to shared venv creation
- Yield progress for: directory creation, venv install, tooling install
- Reuse existing CORTEX progress system (zero complexity)
- **Files:** `src/setup/modules/python_environment_module.py`
- **Tests:** Tests inherit from progress system tests
- **TDD:** RED (progress not shown) → GREEN (add decorator) → REFACTOR (N/A, decorator handles it)

☐ **1.6 UX Enhancement: Setup Time Estimates**
- Display phase estimates before execution: "Phase 1: ~30 seconds"
- Show total estimated time upfront
- Use static benchmarks from testing
- **Files:** `src/setup/setup_orchestrator.py` (phase metadata)
- **Tests:** `tests/test_setup_orchestrator.py` (estimate display)
- **TDD:** RED (estimates not shown) → GREEN (add display) → REFACTOR (estimate calculator)

**Acceptance Criteria:**
- [ ] First-time setup creates `~/.cortex/venv-3.X/` automatically
- [ ] Subsequent setups link in <5 seconds
- [ ] Existing `.venv` projects auto-migrate with prompt
- [ ] Fallback to `.venv` on shared env failure
- [ ] Progress indicators show during long operations
- [ ] Time estimates displayed before each phase
- [ ] All existing tests pass
- [ ] 10+ new tests for shared environment scenarios

---

### Phase 2: User Profiling System (2-3 days)

**Goal:** Interactive profile session during setup, store preferences, UX enhancements

**Tasks:**

☐ **2.1 Create User Profile Module**
- New module: `src/setup/modules/user_profile_module.py`
- Inherit from `BaseSetupModule`
- Metadata: phase=INITIALIZATION, priority=5 (early)
- Implements interactive questionnaire
- **Files:** `src/setup/modules/user_profile_module.py` (new)
- **Tests:** `tests/test_user_profile_module.py` (new)
- **TDD:** RED (profile creation fails) → GREEN (implement questionnaire) → REFACTOR (extract validators)

☐ **2.2 Interactive Questionnaire Implementation**
- Use `input()` with letter-based selection
- 5 questions: name, preference (V/C), role (J/I/S/P/M), work area (B/F/D/A), language (EN/ES/FR/DE/PT/ZH/JA/KO/HI/AR/RU/IT)
- Validate responses with retry (max 3 attempts)
- Allow skip with defaults (preference=verbose, role=intermediate, language=en)
- Display language options with native script (e.g., "ES) Español", "ZH) 中文")
- **Files:** `src/setup/modules/user_profile_module.py`
- **Tests:** `tests/test_user_profile_module.py` (mock input, test all 12 languages)
- **TDD:** RED (invalid input test fails) → GREEN (validation) → REFACTOR (input handlers)

☐ **2.3 Profile Storage in cortex.config.json**
- Load existing config or create new
- Add `user_profile` section with language field
- Write back with pretty JSON formatting
- Verify file permissions (readable only by user)
- Store language as ISO 639-1 code (en, es, fr, etc.) and full name
- **Files:** `src/setup/modules/user_profile_module.py`
- **Tests:** `tests/test_user_profile_module.py` (config persistence, language storage)
- **TDD:** RED (config write fails) → GREEN (JSON persistence) → REFACTOR (config helpers)

☐ **2.4 Profile Schema Validation**
- Define Pydantic model for UserProfile with language field
- Validate language code against supported list (12 languages)
- Handle schema evolution (version field, profile_version="2.0")
- **Files:** `src/setup/models/user_profile.py` (new)
- **Tests:** `tests/test_user_profile_schema.py` (new, test all language codes)
- **TDD:** RED (schema validation fails) → GREEN (Pydantic model) → REFACTOR (validators)

☐ **2.5 Register Module in Setup Orchestrator**
- Import `UserProfileModule`
- Register in orchestrator initialization
- Ensure execution before response template wiring
- **Files:** `src/setup/setup_orchestrator.py`
- **Tests:** `tests/test_setup_orchestrator.py` (module registration)
- **TDD:** RED (orchestrator doesn't run profile module) → GREEN (registration) → REFACTOR (module discovery)

☐ **2.6 UX Enhancement: Smart Defaults**
- Detect git user.name → pre-fill profile name
- Check workspace complexity → suggest role
- GitHub CLI auth → extract name from `gh api user`
- **Files:** `src/setup/modules/user_profile_module.py` (add detection methods)
- **Tests:** `tests/test_user_profile_module.py` (smart defaults)
- **TDD:** RED (detection not working) → GREEN (implement detectors) → REFACTOR (detector chain)

☐ **2.7 UX Enhancement: Profile Preview + Confirmation**
- Display profile summary before saving
- Show interpretation (e.g., "Concise = brief, action-focused")
- Y/N confirmation prompt
- **Files:** `src/setup/modules/user_profile_module.py` (add preview)
- **Tests:** `tests/test_user_profile_module.py` (confirmation flow)
- **TDD:** RED (preview not shown) → GREEN (implement preview) → REFACTOR (format helpers)

☐ **2.8 UX Enhancement: Setup Mode Selection**
- Add initial prompt: Quick/Standard/Custom
- Quick: Auto-detect all, skip questions
- Standard: 4 questions (current design)
- Custom: Extended questionnaire
- **Files:** `src/setup/modules/user_profile_module.py` (mode selection)
- **Tests:** `tests/test_user_profile_module.py` (mode flows)
- **TDD:** RED (mode not respected) → GREEN (conditional flows) → REFACTOR (mode handlers)

**Acceptance Criteria:**
- [ ] Interactive questionnaire runs during setup
- [ ] Profile stored in `cortex.config.json`
- [ ] Input validation prevents invalid entries
- [ ] Default values provided for skipped questions
- [ ] Profile schema validated with Pydantic
- [ ] Smart defaults pre-fill from git/GitHub when available
- [ ] Profile preview shown before save with confirmation
- [ ] Setup mode selection (Quick/Standard/Custom) working
- [ ] 15+ tests covering all input scenarios

---

### Phase 3: Response Template Wiring (2-3 days)

**Goal:** Auto-select templates based on user profile with multilingual support, personalize responses

**Tasks:**

☐ **3.1 Create Multilingual Response Templates**
- Add 72 template variants to `response-templates.yaml` (6 role/preference combos × 12 languages)
- Base templates: detailed, technical, strategic, guided, pro, executive
- Languages: EN, ES, FR, DE, PT, ZH, JA, KO, HI, AR, RU, IT
- Template naming: `{type}_{role}_{language}` (e.g., `standard_5_part_detailed_es`)
- Translate section headers only (keep code/paths in English)
- **Files:** `cortex-brain/response-templates.yaml`
- **Tests:** `tests/test_response_templates.py` (template loading, all 72 variants)
- **TDD:** RED (template not found) → GREEN (add templates) → REFACTOR (DRY base structures)

☐ **3.2 Translation Strategy Implementation**
- Create language mapping dictionary (en="English", es="Español", etc.)
- Section header translations for all 12 languages:
  - "My Understanding" → "Mi Comprensión" (ES), "Meine Verständnis" (DE), etc.
  - "Challenge" → "Desafío" (ES), "Défi" (FR), etc.
  - "Response" → "Respuesta" (ES), "Antwort" (DE), etc.
  - "Next Steps" → "Próximos Pasos" (ES), "Nächste Schritte" (DE), etc.
- Maintain hybrid format (translated headers, English technical content)
- **Files:** `cortex-brain/response-templates.yaml`, `src/response_templates/translations.py` (new)
- **Tests:** `tests/test_translations.py` (new, verify all 12 languages)
- **TDD:** RED (translation missing) → GREEN (add translation map) → REFACTOR (translation loader)

☐ **3.3 Create Template Selection Engine**
- New module: `src/response_templates/template_selector.py`
- Function: `select_template_for_user(profile: UserProfile) -> str`
- Include language in selection: `{preference}_{role}_{language}`
- Fallback hierarchy: exact language → English → generic → default
- Cache selected template for performance
- **Files:** `src/response_templates/template_selector.py` (new)
- **Tests:** `tests/test_template_selector.py` (new, test all language fallbacks)
- **TDD:** RED (selection logic fails) → GREEN (implement selector) → REFACTOR (fallback chain)

☐ **3.4 Integrate with Response Template Loader**
- Load user profile from `cortex.config.json` at startup (including language preference)
- Pass profile to template selector with language parameter
- Use selected language-specific template for all responses
- Handle missing profile gracefully (default to English)
- **Files:** `src/response_templates/response_template_manager.py`
- **Tests:** `tests/test_response_template_manager.py` (profile integration, multilingual)
- **TDD:** RED (profile not loaded) → GREEN (load on init) → REFACTOR (lazy loading)

☐ **3.5 Response Customization Logic**
- Verbose: Include "Why" sections, code examples, conceptual explanations (in user's language)
- Concise: Skip background, focus on actions, bullet lists (in user's language)
- Junior: Add learning resources, explain fundamentals (translated)
- Senior/Principal: Assume knowledge, focus on architecture/decisions (translated)
- Manager: Emphasize team impact, risks, business value (translated)
- Keep all code, commands, paths in English regardless of language setting
- **Files:** `src/response_templates/template_customizers.py` (new)
- **Tests:** `tests/test_template_customizers.py` (new)
- **TDD:** RED (customization doesn't apply) → GREEN (conditional content) → REFACTOR (customizer classes)

☐ **3.5 Update Response Template Documentation**
- Document new template variants in `cortex-brain/documents/`
- Explain selection logic and customization
- Provide examples for each role/preference combo
- **Files:** `cortex-brain/documents/implementation-guides/response-template-customization.md` (new)
- **Tests:** N/A (documentation)

☐ **3.6 Create Code Language Enforcement Hook**
- **Purpose:** Ensure all code/comments remain in English, regardless of response language setting
- **Scope:** Validate `.py`, `.js`, `.ts`, `.java`, `.cpp`, `.c`, `.go`, `.rs` files
- **Detection Strategy:**
  - Scan comments (inline `#`, block `"""`, JSDoc `/** */`)
  - Use Unicode range detection for non-Latin scripts (CJK, Arabic, Cyrillic, Devanagari)
  - Allow English + technical terms + common abbreviations
  - Ignore strings (they can be multilingual for user-facing content)
- **Hook Type:** Pre-commit (prevents commit if non-English detected)
- **Reporting:**
  - List files with non-English comments
  - Show line numbers and detected language
  - Suggest: "Code and comments must be in English. Use multilingual responses via user profile instead."
- **Exemptions:**
  - `cortex-brain/response-templates.yaml` (contains translations)
  - `src/response_templates/translations.py` (translation dictionary)
  - String literals (user-facing messages)
  - Test files with intentional multilingual test data
- **Files:** 
  - `.git/hooks/pre-commit` (add language check)
  - `src/utils/code_language_validator.py` (new)
  - `scripts/check_code_language.py` (new, standalone checker)
- **Tests:** `tests/test_code_language_validator.py` (new)
- **TDD:** RED (non-English comment passes) → GREEN (detection works) → REFACTOR (Unicode ranges, exemptions)

**Rationale:**
- Codebase maintainability: English is universal developer language
- Code review efficiency: All reviewers can read comments
- Documentation consistency: Prevents mixed-language documentation
- Team scalability: New developers can understand codebase
- Separation of concerns: Multilingual UX (responses) ≠ multilingual code

**Acceptance Criteria:**
- [ ] 72 multilingual template variants added (6 types × 12 languages)
- [ ] Translation map covers all 12 supported languages
- [ ] Section headers translated, technical content in English
- [ ] Template selector chooses correct variant based on profile + language
- [ ] Fallback hierarchy works: specific language → English → default
- [ ] Response customization applies correctly in all languages
- [ ] **Code language validator detects non-English comments in 8 file types**
- [ ] **Pre-commit hook prevents commits with non-English code/comments**
- [ ] **Exemptions work for response-templates.yaml and translations.py**
- [ ] Documentation explains selection logic and translation strategy
- [ ] 35+ tests covering all selection scenarios, languages, and code validation

---

### Phase 4: Alignment Orchestrator (2-3 days)

**Goal:** Final setup validation, user-facing design, auto-repair

**Tasks:**

☐ **4.1 Create Alignment Orchestrator Module**
- New module: `src/orchestrators/alignment_orchestrator.py`
- Mode: `--mode setup-validation` (user-facing)
- Mode: `--mode full-alignment` (admin-only, existing)
- **Files:** `src/orchestrators/alignment_orchestrator.py`
- **Tests:** `tests/test_alignment_orchestrator.py` (new)
- **TDD:** RED (orchestrator doesn't exist) → GREEN (skeleton) → REFACTOR (mode handlers)

☐ **4.2 Setup Validation Checks**
- ✅ Shared environment exists and accessible
- ✅ Project linked to shared environment (config has `shared_cortex_venv`)
- ✅ User profile configured and valid
- ✅ Response templates wired correctly
- ✅ Brain tier databases initialized (tier1, tier2, tier3)
- ✅ Git isolation rules active (`.gitignore` has CORTEX)
- ✅ All CORTEX modules importable
- ✅ Configuration file valid JSON and complete
- **Files:** `src/orchestrators/alignment_orchestrator.py`
- **Tests:** `tests/test_alignment_orchestrator.py` (validation checks)
- **TDD:** RED (checks fail on broken setup) → GREEN (implement checks) → REFACTOR (check classes)

☐ **4.3 Auto-Repair Implementation**
- Shared env missing → Create it
- Profile missing → Prompt for interactive session
- Brain DB missing → Initialize tier databases
- Config invalid → Merge with template, fix structure
- **Files:** `src/orchestrators/alignment_orchestrator.py`
- **Tests:** `tests/test_alignment_orchestrator.py` (repair scenarios)
- **TDD:** RED (repair doesn't fix issue) → GREEN (implement repair) → REFACTOR (repair strategies)

☐ **4.4 User-Facing Report Generation**
- Clear output: "✅ Shared environment active" vs "❌ Profile not configured"
- Actionable messages: "Run 'cortex setup profile' to configure"
- Progress indicators during validation
- Final summary: "Setup 90% complete - 1 issue needs attention"
- **Files:** `src/orchestrators/alignment_orchestrator.py`
- **Tests:** `tests/test_alignment_orchestrator.py` (report format)
- **TDD:** RED (report unclear) → GREEN (format output) → REFACTOR (report builder)

☐ **4.5 Integration Score Calculation**
- Each check: pass=10 points, fail=0 points (8 checks = 80 points max)
- Bonus points: performance metrics, optimization flags (+20 points)
- Score: 0-100%
- Thresholds: <70% = needs attention, 70-89% = good, 90-100% = excellent
- **Files:** `src/orchestrators/alignment_orchestrator.py`
- **Tests:** `tests/test_alignment_orchestrator.py` (scoring logic)
- **TDD:** RED (score calculation wrong) → GREEN (implement scoring) → REFACTOR (weight system)

☐ **4.6 Update SETUP-CORTEX.MD**
- Add "Step 9: Validate Setup" section
- Explain alignment orchestrator purpose
- Show command: `align setup` or Python invocation
- Interpret output: what ✅/❌ means, when to get help
- **Files:** `docs/SETUP-CORTEX.md`
- **Tests:** N/A (documentation)

☐ **4.7 UX Enhancement: Setup Summary**
- Display recap at end: configuration, time taken, next steps
- Show personalized recommendations based on profile
- Include performance metrics (setup time vs benchmark)
- **Files:** `src/orchestrators/alignment_orchestrator.py`
- **Tests:** `tests/test_alignment_orchestrator.py` (summary generation)
- **TDD:** RED (summary missing) → GREEN (generate summary) → REFACTOR (summary template)

☐ **4.8 UX Enhancement: Setup Resume**
- Create checkpoint file `.cortex-setup-state.json`
- Save state after each phase completion
- On next setup, detect incomplete state, offer resume
- **Files:** `src/setup/setup_orchestrator.py` (checkpoint logic)
- **Tests:** `tests/test_setup_orchestrator.py` (resume flow)
- **TDD:** RED (resume not offered) → GREEN (checkpoint + resume) → REFACTOR (state manager)

☐ **4.9 UX Enhancement: Undo Last Setup**
- Backup config before setup changes
- Provide `cortex setup --undo` command
- Restore previous config, remove shared venv link
- **Files:** `src/setup/setup_orchestrator.py` (undo command)
- **Tests:** `tests/test_setup_orchestrator.py` (undo scenarios)
- **TDD:** RED (undo doesn't restore) → GREEN (backup + restore) → REFACTOR (backup manager)

**Acceptance Criteria:**
- [ ] Alignment orchestrator runs in `setup-validation` mode
- [ ] All 8 validation checks implemented
- [ ] Auto-repair fixes common issues
- [ ] User-facing report is clear and actionable
- [ ] Integration score calculated (0-100%)
- [ ] SETUP-CORTEX.MD updated with step 9
- [ ] Setup summary displayed at end with personalization
- [ ] Setup resume works after interruption
- [ ] Undo command restores previous setup state
- [ ] 25+ tests covering validation, repair, scoring

---

### Phase 6: Planning Infrastructure (1-2 days)

**Goal:** Lightweight plan management system for organization, lookup, and status tracking

**Tasks:**

☐ **6.1 Create Plan Metadata System**
- Add metadata header to all plan files
- Fields: plan_id, title, status, priority, created_date, estimated_hours
- Store metadata in YAML frontmatter (Markdown compatible)
- **Files:** `src/workflows/plan_metadata.py` (new)
- **Tests:** `tests/test_plan_metadata.py` (new)
- **TDD:** RED (metadata extraction fails) → GREEN (YAML parser) → REFACTOR (validator)

☐ **6.2 Build Plan Registry**
- SQLite database: `cortex-brain/planning-registry.db`
- Schema: plan_id (PK), title, status, priority, file_path, created_date, updated_date
- Auto-scan `documents/planning/` on startup, index all plans
- **Files:** `src/workflows/plan_registry.py` (new)
- **Tests:** `tests/test_plan_registry.py` (new)
- **TDD:** RED (registry empty) → GREEN (scan + index) → REFACTOR (incremental updates)

☐ **6.3 Implement Plan Lookup API**
- `list_plans(status=None, priority=None)` - Filter by criteria
- `get_plan(plan_id)` - Retrieve plan by ID
- `search_plans(query)` - Full-text search in titles/descriptions
- `update_plan_status(plan_id, new_status)` - Status transitions
- **Files:** `src/workflows/plan_registry.py` (extend)
- **Tests:** `tests/test_plan_registry.py` (lookup scenarios)
- **TDD:** RED (lookup returns wrong results) → GREEN (query logic) → REFACTOR (query builder)

☐ **6.4 Organize Plan Files by Status**
- Create structure: `planning/features/active/`, `planning/features/completed/`
- Move this plan to `planning/features/active/CORTEX-SETUP-001.md`
- Implement auto-move on status change (in-progress → active, completed → completed)
- **Files:** `src/workflows/plan_registry.py` (add file management)
- **Tests:** `tests/test_plan_registry.py` (file movement)
- **TDD:** RED (files not moved) → GREEN (file organizer) → REFACTOR (collision handling)

☐ **6.5 Generate Plan Index**
- Auto-generate `planning/INDEX.md` with all plans
- Table format: ID | Title | Status | Priority | Link
- Group by status: Active Plans, Completed Plans, Proposed Plans
- Update index on any plan change
- **Files:** `src/workflows/plan_index_generator.py` (new)
- **Tests:** `tests/test_plan_index_generator.py` (new)
- **TDD:** RED (index not generated) → GREEN (markdown generator) → REFACTOR (template system)

☐ **6.6 Create Plan CLI Commands**
- `cortex plan list [--status=active]` - List plans
- `cortex plan show <plan_id>` - Display plan details
- `cortex plan search <query>` - Search plans
- `cortex plan update <plan_id> --status=<status>` - Update status
- **Files:** `src/main.py` (add plan commands)
- **Tests:** `tests/test_plan_cli.py` (new)
- **TDD:** RED (command not recognized) → GREEN (CLI handlers) → REFACTOR (command router)

☐ **6.7 Update Current Plan with Metadata**
- Add YAML frontmatter to this plan
- Register in plan registry
- Move to `planning/features/active/`
- Update index to include this plan
- **Files:** This file + registry
- **Tests:** Manual validation
- **TDD:** N/A (manual migration)

**Acceptance Criteria:**
- [ ] Plan metadata system extracts YAML frontmatter
- [ ] Plan registry indexes all plans in `documents/planning/`
- [ ] Lookup API filters by status, priority, searches by query
- [ ] Plans organized into active/completed directories
- [ ] INDEX.md auto-generated with all plans
- [ ] CLI commands work for list/show/search/update
- [ ] This plan registered and moved to active directory
- [ ] 15+ tests covering registry, lookup, index generation

---

### Phase 7: Integration & Testing (2-3 days)

**Goal:** End-to-end testing, documentation, deployment readiness

**Tasks:**

☐ **7.1 End-to-End Setup Flow Test**
- Fresh installation simulation
- Run full setup: shared env + profile + templates + alignment + plan registration
- Verify all components working together
- Time measurement: ensure <60 seconds for first setup
- **Files:** `tests/integration/test_full_setup_flow.py` (new)
- **Tests:** Integration test suite
- **TDD:** RED (E2E fails) → GREEN (fix integration points) → REFACTOR (test helpers)

☐ **7.2 Migration Scenario Testing**
- Existing single-project `.venv` → shared environment
- Existing profile → preserved during upgrade
- Existing config → merged with new fields
- **Files:** `tests/integration/test_migration_scenarios.py` (new)
- **Tests:** Migration test suite
- **TDD:** RED (migration breaks existing setup) → GREEN (safe migration) → REFACTOR (migration strategies)

☐ **7.3 Multi-Project Simulation**
- Create 3 test projects
- Link all to same shared environment
- Verify independence: deps in project A don't affect project B
- **Files:** `tests/integration/test_multi_project.py` (new)
- **Tests:** Multi-project test suite
- **TDD:** RED (cross-project contamination) → GREEN (isolation verified) → REFACTOR (test fixtures)

☐ **7.4 Performance Benchmarking**
- Measure first-time setup time (target: <60 seconds)
- Measure subsequent project linking (target: <5 seconds)
- Compare vs old single-project approach (expect 83% reduction)
- **Files:** `tests/performance/test_setup_performance.py` (new)
- **Tests:** Performance test suite
- **TDD:** RED (performance targets not met) → GREEN (optimize bottlenecks) → REFACTOR (async operations)

☐ **7.5 Plan Registry Integration Testing**
- Test plan registration during feature creation
- Verify plan lookup and search functionality
- Test status transitions (proposed → approved → in-progress → completed)
- Validate index generation and updates
- **Files:** `tests/integration/test_plan_registry_integration.py` (new)
- **Tests:** Plan registry integration suite
- **TDD:** RED (registry not integrated) → GREEN (workflow integration) → REFACTOR (registry hooks)

☐ **7.6 Documentation Updates**
- Update `.github/prompts/CORTEX.prompt.md` with new setup flow
- Update `.github/copilot-instructions.md` with profile system + planning commands
- Create `cortex-brain/documents/implementation-guides/shared-environment-setup.md`
- Create `cortex-brain/documents/implementation-guides/user-profiling-guide.md`
- Create `cortex-brain/documents/implementation-guides/plan-management-guide.md`
- **Files:** Multiple documentation files
- **Tests:** N/A (documentation)

☐ **7.7 Update VERSION and CHANGELOG**
- Bump version to 3.6.0 (minor feature addition)
- Add CHANGELOG entries for all changes
- Note breaking changes: setup flow different (but backward compatible)
- **Files:** `VERSION`, `CHANGELOG.md`
- **Tests:** N/A (versioning)

**Acceptance Criteria:**
- [ ] All E2E tests pass (100% success rate)
- [ ] Migration scenarios tested and validated
- [ ] Multi-project isolation confirmed
- [ ] Performance targets achieved (<60s first, <5s subsequent)
- [ ] Plan registry integrated with planning workflow
- [ ] All documentation updated and reviewed
- [ ] Version bumped, CHANGELOG complete
- [ ] 55+ integration tests covering all flows (was 40+, added plan registry tests)

---

### Phase 8: File Naming Governance (1 day)

**Goal:** Implement Tier 0 file naming conventions to prevent excessively long/short filenames globally

**Problem Analysis:**

**Current Issues:**
- ❌ Filenames up to 84 characters (e.g., `ADO-ENTRY-POINT-ENHANCEMENT-PROPOSAL_20251201_20251201_20251202_20251202_20251202.md`)
- ❌ VS Code tabs consume entire screen real estate  
- ❌ Difficult to scan and find files quickly
- ❌ Redundant timestamps and excessive verbosity
- ❌ No enforced maximum length
- ⚠️ But also avoid overly short names that lack meaning

**Root Causes:**
1. Planning orchestrator generates descriptive names with dates
2. No Tier 0 governance rule for filename length
3. No automated validation during file creation
4. No filename optimization strategy

**Optimal Balance:**

**Filename Length Limits:**
- **Maximum:** 45 characters (excluding extension)
- **Minimum:** 10 characters (excluding extension)
- **Sweet Spot:** 20-35 characters

**Rationale:**
- 45 chars = ~5 tabs visible in VS Code (optimal multitasking)
- 10 chars = Prevents meaningless names like `plan.md`, `doc.md`
- 20-35 chars = Descriptive yet concise

**Tasks:**

☐ **8.1 Add Tier 0 Governance Rules**
- **Rule 1: FILENAME_LENGTH_GOVERNANCE**
  - Add to `brain-protection-rules.yaml`
  - Severity: WARNING (not blocking, but strongly enforced)
  - Applies to: All documents, plans, reports, captures
  - Exceptions: Auto-generated timestamps in specific formats
  
- **Rule 2: CODE_LANGUAGE_ENFORCEMENT** (NEW)
  - Add to `brain-protection-rules.yaml`
  - Severity: BLOCKED (prevents commits with non-English code)
  - Applies to: All code files (.py, .js, .ts, .java, .cpp, .c, .go, .rs)
  - Validation: Comments and docstrings must be in English
  - Exemptions: 
    - `cortex-brain/response-templates.yaml` (contains translations)
    - `src/response_templates/translations.py` (translation data)
    - String literals (user-facing messages can be multilingual)
    - Test data files with intentional multilingual content
  - Detection: Unicode range analysis (CJK, Arabic, Cyrillic, Devanagari, etc.)
  - Rationale: 
    - Maintainability: All developers can read code
    - Code review: Universal understanding
    - Documentation: Consistent technical communication
    - Separation: Multilingual UX responses ≠ multilingual code
    
- **Files:** `cortex-brain/brain-protection-rules.yaml`
- **Tests:** `tests/test_brain_protector.py` (filename + code language validation)
- **TDD:** RED (rules not enforced) → GREEN (warnings/blocking works) → REFACTOR (rule engine)

☐ **8.2 Define Filename Convention Strategy**
- **Pattern:** `{TYPE}-{ID}-{SHORT_TITLE}.{ext}`
- **Type:** PLAN, ADO, REPORT, CAPTURE, ANALYSIS (max 8 chars)
- **ID:** Numeric or short alphanumeric (3-6 chars)
- **Short Title:** Hyphen-separated, 2-4 words max (15-25 chars)
- **Examples:**
  - Good: `PLAN-001-shared-env-setup.md` (28 chars)
  - Good: `ADO-4567-auth-fix.md` (18 chars)
  - Good: `REPORT-2025Q4-setup-metrics.md` (31 chars)
  - Bad: `PLAN-2025-11-17-COMPREHENSIVE-IMPLEMENTATION-STRATEGY-FOR-AUTHENTICATION.md` (76 chars)
  - Bad: `doc.md` (3 chars)
- **Files:** `cortex-brain/documents/naming-conventions.md` (new)
- **Tests:** N/A (documentation)

☐ **8.3 Implement Filename Validator**
- Create utility: `src/utils/filename_validator.py`
- Functions: `validate_filename(name)`, `suggest_shorter_name(name)`, `validate_plan_filename(name)`
- Returns: `(is_valid: bool, message: str, suggestion: Optional[str])`
- Integrates with Brain Protector for automatic checking
- **Files:** `src/utils/filename_validator.py` (new)
- **Tests:** `tests/test_filename_validator.py` (new)
- **TDD:** RED (validator doesn't exist) → GREEN (basic validation) → REFACTOR (smart suggestions)

☐ **8.4 Add Filename Shortening Algorithm**
- Intelligent abbreviation: "authentication" → "auth", "implementation" → "impl"
- Remove redundant words: "comprehensive", "complete", "full"
- Preserve meaning: Use domain-specific abbreviations
- Example transformations:
  - `PLAN-2025-11-17-comprehensive-authentication-implementation.md` (60 chars)
  - → `PLAN-001-auth-impl.md` (21 chars)
- **Files:** `src/utils/filename_optimizer.py` (new)
- **Tests:** `tests/test_filename_optimizer.py` (new)
- **TDD:** RED (no optimization) → GREEN (abbreviation engine) → REFACTOR (domain dictionary)

☐ **8.5 Update Planning Orchestrator**
- Modify plan creation to use short filenames
- Pattern: `PLAN-{auto_id}-{abbreviated_title}.md`
- Auto-ID: 3-digit sequential (001, 002, 003)
- Abbreviated title: 2-3 word summary (15-20 chars max)
- **Files:** `src/orchestrators/planning_orchestrator.py.bak` (when restored)
- **Tests:** `tests/test_planning_orchestrator.py` (filename generation)
- **TDD:** RED (long filenames generated) → GREEN (short filenames) → REFACTOR (abbreviator integration)

☐ **8.6 Create Realignment Script for Existing Files**
- **Purpose:** Rename all existing files to comply with new governance (45 char max)
- **Scope:** All documents in `cortex-brain/documents/` including plans, reports, captures, analyses
- **Script:** `scripts/realign_filenames.py` with comprehensive features:
  
  **Core Functionality:**
  - Scan all `.md` files recursively in `cortex-brain/documents/`
  - Identify files >45 chars or <10 chars (excluding extension)
  - Generate optimized names using `filename_optimizer` abbreviation engine
  - Preserve TYPE-ID pattern when present
  - Auto-assign IDs when missing (sequential by type)
  
  **Dry-Run Mode (Default):**
  - Preview all rename operations without making changes
  - Show before/after comparison with character count
  - Identify cross-reference locations that need updating
  - Generate migration report: `FILENAME-REALIGNMENT-REPORT.md`
  - Exit code 0 (success, no changes made)
  
  **Execution Mode (`--execute` flag):**
  - Create backup: `cortex-brain/backups/filename-realignment-{timestamp}.tar.gz`
  - Rename files with validation (check no overwrites)
  - Update cross-references in all `.md`, `.yaml`, `.json` files
  - Update plan registry (if exists) with new filenames
  - Generate completion report with rollback instructions
  - Exit code 0 (success) or 1 (failure with rollback)
  
  **Safety Features:**
  - Collision detection: prevent overwrites
  - Atomic operations: rollback on any failure
  - Reference validation: verify all links updated
  - Backup verification: ensure backup is complete before rename
  - Git status check: warn if uncommitted changes exist
  
  **Reporting:**
  - Total files scanned
  - Files needing rename (count and percentage)
  - Character savings (before/after average length)
  - Cross-references updated (count)
  - Operation duration
  
  **Example Output (Dry-Run):**
  ```
  🔍 Filename Realignment Analysis
  ================================
  
  Scanning: cortex-brain/documents/
  Total files: 247
  Files needing rename: 42 (17%)
  
  Sample Transformations:
  ❌ shared-environment-default-activation.md (41 chars)
  ✅ PLAN-001-shared-env-setup.md (27 chars) [-34%]
  
  ❌ ADO-ENTRY-POINT-ENHANCEMENT-PROPOSAL_20251201_20251201.md (84 chars)
  ✅ ADO-4567-entry-enhance.md (24 chars) [-71%]
  
  ❌ CONVERSATION-CAPTURE-2025-11-17-DOCUMENT-GENERATION-GAP.md (69 chars)
  ✅ CAPTURE-nov17-doc-gen-gap.md (28 chars) [-59%]
  
  Cross-References Found: 156 locations in 38 files
  
  💾 Estimated Impact:
  - Average filename length: 47.3 → 26.8 chars (-43%)
  - VS Code tabs visible: 2.1 → 5.4 tabs (+157%)
  - Total character savings: 1,974 chars
  
  ⚠️  DRY-RUN MODE - No changes made
  Run with --execute to apply changes
  
  Report saved: FILENAME-REALIGNMENT-REPORT.md
  ```
  
  **Self-Application:**
  - This plan file (`shared-environment-default-activation.md`, 41 chars) will be renamed to:
  - **New name:** `PLAN-001-shared-env-setup.md` (27 chars)
  - Rationale: Follows TYPE-ID-TITLE pattern, removes redundancy, under 45 char limit
  
- **Files:** `scripts/realign_filenames.py` (new), `src/utils/filename_optimizer.py` (dependency)
- **Tests:** `tests/test_realign_filenames.py` (new) - dry-run validation, backup verification, reference updating
- **TDD:** RED (no realignment capability) → GREEN (safe bulk rename with backups) → REFACTOR (cross-reference updater, collision resolver)

☐ **8.7 Unified Pre-Commit Hook (Filename + Code Language)**
- **Purpose:** Single pre-commit hook for dual governance (filename length + code language)
- **Validations:**
  1. **Filename Length:** Warn on files >45 or <10 chars (non-blocking warning)
  2. **Code Language:** Block commits with non-English code/comments (blocking error)
- **Hook Structure:**
  ```bash
  #!/bin/bash
  # CORTEX Pre-Commit Governance Hook
  
  # Check 1: Filename length (warning only)
  python src/utils/filename_validator.py --staged-files
  
  # Check 2: Code language (blocking)
  python src/utils/code_language_validator.py --staged-files
  if [ $? -ne 0 ]; then
    echo "❌ Commit blocked: Non-English code/comments detected"
    echo "Fix issues or use --no-verify to skip (not recommended)"
    exit 1
  fi
  
  echo "✅ Pre-commit checks passed"
  exit 0
  ```
- **Installation:** Auto-install during CORTEX setup via `setup_git_hooks()` function
- **Bypass:** Allow `--no-verify` flag for emergencies (logged as warning)
- **Files:** 
  - `.git/hooks/pre-commit` (generated during setup)
  - `scripts/install_git_hooks.sh` (installer script)
- **Tests:** `tests/test_git_hooks.py` (new) - test hook installation, filename validation, code language detection
- **TDD:** RED (hook doesn't block non-English) → GREEN (blocking works) → REFACTOR (dual validation)

☐ **8.8 Update Documentation**
- Add filename conventions to `CORTEX.prompt.md`
- Add code language policy to `CORTEX.prompt.md` and `.github/copilot-instructions.md`
- Update `.github/copilot-instructions.md` with both governance rules
- Create `cortex-brain/documents/implementation-guides/filename-best-practices.md`
- Create `cortex-brain/documents/implementation-guides/code-language-policy.md` (new)
- Document pre-commit hook in SETUP-CORTEX.MD
- **Files:** Multiple documentation files
- **Tests:** N/A (documentation)

**Acceptance Criteria:**
- [ ] Tier 0 rule `FILENAME_LENGTH_GOVERNANCE` added to brain protection rules
- [ ] Tier 0 rule `CODE_LANGUAGE_ENFORCEMENT` added to brain protection rules (new)
- [ ] Filename validator warns on files >45 chars or <10 chars
- [ ] Code language validator detects non-English in 8 file types (new)
- [ ] Filename optimizer suggests intelligent abbreviations with domain dictionary
- [ ] Planning orchestrator generates short filenames (20-35 chars)
- [ ] Realignment script with dry-run mode identifies 40+ files needing rename
- [ ] Realignment script execution mode safely renames files with atomic rollback
- [ ] Cross-reference updater modifies 150+ references across .md/.yaml/.json files
- [ ] This plan file renamed: `shared-environment-default-activation.md` → `PLAN-001-shared-env-setup.md`
- [ ] Unified pre-commit hook validates filenames (warning) and code language (blocking) (new)
- [ ] Pre-commit hook auto-installs during CORTEX setup (new)
- [ ] Documentation updated with conventions, realignment guide, and code language policy (new)
- [ ] 20+ tests covering validation, optimization, abbreviation, realignment
- [ ] Average filename length reduced from ~47 to ~27 chars (43% reduction)
- [ ] VS Code tabs visible increased from 2 to 5+ tabs (157% improvement)
- [ ] 20+ tests covering validation, optimization, abbreviation

**Filename Abbreviation Dictionary (Domain-Specific):**

| Long Word | Abbreviation | Context |
|-----------|-------------|---------|
| authentication | auth | Security |
| implementation | impl | Development |
| comprehensive | (remove) | Filler word |
| documentation | docs | General |
| orchestrator | orch | Architecture |
| environment | env | Configuration |
| configuration | config | Settings |
| integration | integ | Development |
| validation | valid | Testing |
| optimization | optim | Performance |
| enhancement | enhance | Features |
| application | app | General |
| development | dev | General |
| production | prod | Environment |
| infrastructure | infra | DevOps |
| conversation | conv | CORTEX |
| architecture | arch | Design |

**Governance Integration:**

This becomes a **Tier 0 Instinct**: `FILENAME_LENGTH_GOVERNANCE`

```yaml
- rule_id: "FILENAME_LENGTH_GOVERNANCE"
  name: "Filename Length Governance"
  severity: "warning"
  description: |
    Enforce optimal filename lengths for maintainability and UX.
    
    Limits:
    - Maximum: 45 characters (excluding extension)
    - Minimum: 10 characters (excluding extension)
    - Optimal: 20-35 characters
    
    Rationale:
    - 45 chars = ~5 tabs visible in VS Code
    - 10 chars = Prevents meaningless names
    - Descriptive yet scannable
  
  triggers:
    - File creation in cortex-brain/documents/
    - Plan generation
    - Report generation
    - Document organization
  
  validation:
    - Check filename length (exclude extension)
    - Warn if >45 or <10 characters
    - Suggest optimized name using abbreviation dictionary
  
  alternatives:
    - "Use abbreviations from domain dictionary"
    - "Remove filler words (comprehensive, complete, full)"
    - "Use pattern: {TYPE}-{ID}-{SHORT_TITLE}"
    - "Consult filename_optimizer for suggestions"
  
  evidence_template: |
    Filename too long/short: '{filename}' ({length} chars)
    
    Guideline violation:
    - Maximum: 45 chars (yours: {length})
    - Minimum: 10 chars
    - Optimal: 20-35 chars
    
    Suggested alternative: '{suggested_name}'
    
    Rationale: Maintain readability in VS Code tabs and file explorers
```

---

## ✅ Definition of Done (DoD)

### Code Quality
- [ ] All new code follows SOLID principles
- [ ] TDD workflow: RED → GREEN → REFACTOR for all features
- [ ] Code coverage ≥85% for new modules
- [ ] No linting errors (pylint score ≥9.0/10)
- [ ] Type hints on all public functions
- [ ] Docstrings with examples for all modules

### Testing
- [ ] 100+ new unit tests (all passing)
- [ ] 40+ integration tests (all passing)
- [ ] Performance benchmarks meet targets
- [ ] Edge cases covered (invalid input, failures, migrations)
- [ ] Manual testing on macOS, Windows, Linux

### Security
- [ ] STRIDE threat analysis completed and mitigated
- [ ] Input validation on all user inputs
- [ ] No PII in logs or error messages
- [ ] File permissions validated (user-only for config)
- [ ] No elevation of privilege required

### Documentation
- [ ] SETUP-CORTEX.MD updated with step 9
- [ ] Implementation guides created (2 new guides)
- [ ] CORTEX.prompt.md updated with new flow
- [ ] copilot-instructions.md updated with profiling
- [ ] CHANGELOG.md complete with all changes

### User Experience
- [ ] First-time setup completes in <60 seconds
- [ ] Subsequent project linking in <5 seconds
- [ ] Interactive questionnaire clear and intuitive
- [ ] Response templates personalized correctly
- [ ] Alignment orchestrator output actionable
- [ ] Migration from old setup seamless

### Deployment Readiness
- [ ] All tests pass on CI/CD (if applicable)
- [ ] Version bumped to 3.6.0
- [ ] Brain Protector rules updated (if needed)
- [ ] Rollback procedure documented
- [ ] Upgrade path from 3.5.0 → 3.6.0 tested

---

## 📊 Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| First-time setup time | ~300s (5 min) | <60s (1 min) | Timer in setup script |
| Subsequent setup time | ~30s | <5s | Timer in setup script |
| Setup time reduction | 0% | 83% | (300-60)/300 |
| User profile adoption | 0% | 90% | % of configs with profile |
| Template personalization | 0% | 95% | % of responses using selected template |
| Multilingual adoption | 0% | 25% | % of users selecting non-English |
| Language template coverage | 0 | 72 templates | 6 variants × 12 languages |
| Translation accuracy | N/A | 95%+ | Native speaker review |
| Alignment pass rate | Unknown | 100% | % of setups passing all checks |
| Plans indexed | 0 | 100% | % of plans in registry |
| Plan lookup time | N/A | <100ms | Query performance |
| Average filename length | ~47 chars | ~27 chars | Measured across all docs |
| Filename reduction | 0% | 43% | Character savings |
| VS Code tabs visible | ~2 tabs | 5+ tabs | UI measurement |
| Files needing rename | 42 (17%) | 0 (0%) | Realignment script report |
| Test coverage | ~75% | ≥85% | pytest-cov |
| User satisfaction | N/A | 4.5/5 | Feedback system |

---

## 🚨 Risks & Mitigations

| Risk | Probability | Impact | Mitigation |
|------|-------------|--------|------------|
| Shared env creation fails | MEDIUM | HIGH | Fallback to single-project `.venv` |
| Migration breaks existing setup | LOW | HIGH | Backup config before migration, rollback available |
| User confusion with profile questions | MEDIUM | LOW | Clear instructions, defaults for all questions |
| Performance targets not met | LOW | MEDIUM | Benchmark early, optimize bottlenecks incrementally |
| Template selection logic bugs | MEDIUM | LOW | Extensive testing, fallback to default template |
| Alignment orchestrator false positives | LOW | MEDIUM | Manual override flag, detailed logging |
| Plan registry corruption | LOW | MEDIUM | SQLite ACID guarantees, automatic backup, rebuild from files |

---

## 🔄 Rollback Plan

If critical issues discovered post-deployment:

1. **Revert setup orchestrator** to use single-project venv module
2. **Disable user profiling module** (skip in orchestrator registration)
3. **Use default response template** (ignore profile if present)
4. **Skip alignment orchestrator** in SETUP-CORTEX.MD step 9
5. **Git revert** to commit before feature merge
6. **Notify users** via CHANGELOG and GitHub issue

**Rollback Time:** <30 minutes (code revert + validation)

---

## 📅 Timeline Estimate

| Phase | Duration | Dependencies |
|-------|----------|--------------|
| Phase 1: Shared Environment Enhancement | 3-5 days | None |
| Phase 2: User Profiling System | 2-3 days | Phase 1 (config structure) |
| Phase 3: Response Template Wiring | 2-3 days | Phase 2 (profile available) |
| Phase 4: Alignment Orchestrator | 2-3 days | Phases 1-3 (all features ready) |
| Phase 5: Integration & Testing | 2-3 days | Phases 1-4 (all features complete) |
| Phase 6: Planning Infrastructure | 1-2 days | None (can run parallel with Phase 1-2) |
| Phase 7: Final Integration & Testing | 2-3 days | All phases complete |
| Phase 8: File Naming Governance | 1-2 days | None (can run parallel, realignment at end) |
| **Total** | **16-24 days** | **~3.5-5 weeks** |

**Assumptions:**
- 1 developer working full-time
- No major blockers or scope changes
- Phase 8 realignment script run after Phase 7 completion (safest approach)
- Parallel execution: Phase 6 + Phase 8 tasks 8.1-8.5 during Phase 1-5, then 8.6-8.8 after Phase 7
- TDD workflow followed (may add 20% time but reduces bugs)
- Phase 6 can run partially in parallel with early phases (reduces total time)

---

## 📝 Approval Checklist

Before implementation begins:

- [ ] Product Owner approves feature scope
- [ ] Architecture reviewed and approved
- [ ] STRIDE threat analysis reviewed
- [ ] DoR validation complete
- [ ] DoD criteria agreed upon
- [ ] Timeline and resources allocated
- [ ] Rollback plan reviewed

**Planning Status:** ✅ COMPLETE - Ready for Implementation

**Next Action:** Begin Phase 1 - Shared Environment Enhancement

---

**Document Control:**
- **Version:** 1.0
- **Status:** Approved for Implementation
- **Planning Hours:** 2 hours
- **Review Date:** 2025-12-03
- **Approver:** Asif Hussain
