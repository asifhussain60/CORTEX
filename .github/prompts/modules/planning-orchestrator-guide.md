# CORTEX Planning System 2.0

**Version:** 2.0  
**Purpose:** Interactive feature planning with Vision API, file-based workflow, and DoR/DoD enforcement  
**Audience:** Developers using CORTEX for feature planning

---

## 🚀 Key Features

### 1. Vision API Integration for Screenshots
**What:** Attach screenshots during planning → CORTEX auto-extracts requirements, UI elements, error context, ADO fields

**Use Cases:**
- **UI Mockup:** Extract buttons, inputs, labels → Auto-generate acceptance criteria
- **Error Screenshot:** Extract error message, stack trace → Pre-populate bug template
- **ADO Work Item:** Extract ADO#, title, description → Pre-fill ADO form
- **Architecture Diagram:** Extract components, relationships → Add to technical notes

**Example:**
```
User: "let's plan authentication" + [uploads login page mockup]
CORTEX: "✅ Vision API found: Submit button, Email field, Password field, 'Forgot Password' link"
        "✅ Auto-generated 4 acceptance criteria. Review in planning file (opened in VS Code)"
```

**How to Use:** Simply attach screenshot when saying "plan [feature]". CORTEX analyzes automatically.

---

### 2. Unified Planning Core (DRY Principle)
**What:** ADO planning and Feature planning now share 80% of code (phase breakdown, risk analysis, task generation)

**Difference:** Only requirement capture differs:
- **ADO Planning:** Structured form with pre-defined fields
- **Feature Planning:** Interactive chat-based Q&A
- **Vision Planning:** Screenshot-driven extraction

**Benefit:** Consistent planning quality, easier maintenance, faster updates

---

### 3. File-Based Planning Workflow
**What:** Planning outputs to dedicated `.md` files (not chat-only)

**Why:**
- ✅ Persistent artifact (not lost when chat closes)
- ✅ Git-trackable planning history
- ✅ Direct pipeline integration (auto-inject into development context)
- ✅ Resumable (open file anytime)
- ✅ Living documentation

**How It Works:**
```
User: "plan authentication"
    ↓
CORTEX: Creates cortex-brain/documents/planning/features/PLAN-2025-11-17-authentication.md
        Opens file in VS Code
        Writes planning content to file (not chat)
        Sends summaries to chat: "✅ Phase 1 complete (see file)"
    ↓
User: Reviews file, provides feedback in chat
    ↓
CORTEX: Updates file based on feedback
    ↓
User: "approve plan"
    ↓
CORTEX: Moves file to approved/, hooks into development pipeline
```

**Chat Response:** Summarized updates only (full details in file)

---

### 4. CORTEX .gitignore & Brain Preservation
**What:** CORTEX folder automatically excluded from user repo (via `.gitignore`)

**Why:**
- Separate CORTEX data from user application code
- Avoid accidental commits of CORTEX internals
- Preserve brain locally (not dependent on git)

**Brain Preservation Strategy (Hybrid):**
- **Local Backups:** Daily automated backups (full brain, databases included)
- **Cloud Sync (Optional):** Sync documents/templates to OneDrive/Dropbox (not databases)
- **Manual Export:** On-demand export for sharing

**Setup:**
```
User: "setup cortex"
CORTEX: 
  ✅ Created CORTEX/ folder in your repo
  ✅ Added "CORTEX/" to .gitignore (user repo)
  ✅ Configured local backups (daily, 30-day retention)
  ⚠️ Optional: Enable cloud sync for documents? (Y/N)
```

**Backup Status:** "Last backup: 2 hours ago. Next: Today 11:00 PM"

---

## 🎯 How to Use Planning Features

### Scenario 1: Plan with Screenshot (Vision API)
```
User: "plan login feature" + [attach UI mockup screenshot]

CORTEX:
  1. Analyzes screenshot (Vision API)
  2. Extracts UI elements (buttons, inputs, labels)
  3. Creates planning file with pre-populated acceptance criteria
  4. Opens file in VS Code
  5. Chat: "✅ Extracted 8 UI elements. Review AC in planning file."
```

---

### Scenario 2: Plan ADO Feature (Form-Based)
```
User: "plan ado feature"

CORTEX:
  1. Creates ADO form template
  2. Opens in VS Code
  3. User fills: ADO#, Type (Bug/Feature), DoR, DoD, AC, Notes
  4. User: "import ado template"
  5. CORTEX: Parses, validates, stores in database, injects into context
```

---

### Scenario 3: Plan Generic Feature (Interactive)
```
User: "plan user dashboard"

CORTEX:
  1. Creates planning file
  2. Asks clarifying questions in chat
  3. Writes answers to planning file
  4. Generates phases, risks, tasks
  5. User: "approve plan"
  6. CORTEX: Hooks into development pipeline
```

---

### Scenario 4: Resume Existing Plan
```
User: "resume plan authentication"

CORTEX:
  1. Searches planning database
  2. Finds PLAN-2025-11-17-authentication.md
  3. Opens file + related files (code edited for this plan)
  4. Injects into Tier 1 context
  5. Chat: "✅ Resumed authentication plan (60% complete). Continue?"
```

---

## 📋 Planning Commands (Natural Language)

| Command | Description | Example |
|---------|-------------|---------|
| `plan [feature]` | Start new feature planning | "plan authentication" |
| `plan ado` | Start ADO work item planning | "plan ado feature" |
| `plan [feature] + [screenshot]` | Vision-enabled planning | Attach mockup/error/diagram |
| `approve plan` | Finalize plan → hook into pipeline | After reviewing planning file |
| `resume plan [name]` | Continue existing plan | "resume plan authentication" |
| `planning status` | Show all active plans | Dashboard view |
| `import ado template` | Parse filled ADO template | After filling out ADO form |

**No slash commands needed.** Just natural language.

---

## 🗂️ Planning File Structure

```
cortex-brain/documents/planning/
├── features/
│   ├── active/
│   │   ├── PLAN-2025-11-17-authentication-planning.md
│   │   └── PLAN-2025-11-17-user-dashboard-planning.md
│   └── approved/
│       └── APPROVED-2025-11-16-payment-integration.md
├── ado/
│   ├── active/
│   │   ├── ADO-12345-in-progress-user-authentication.md
│   │   └── ADO-12346-planning-api-refactor.md
│   ├── completed/
│   └── blocked/
├── bugs/
│   └── active/
└── rfcs/
    └── active/
```

**Status-Based Directories:** `active/`, `approved/`, `completed/`, `blocked/`

---

## 🔒 .gitignore Configuration

**User Repo (Auto-Created):**
```gitignore
# CORTEX AI Assistant (local only, not committed)
CORTEX/
```

**CORTEX Internal (.gitignore):**
```gitignore
# Exclude from sync/backup
*.db
*.db-shm
*.db-wal
crawler-temp/
sweeper-logs/
logs/

# Include in sync/backup
!documents/
!response-templates.yaml
!capabilities.yaml
```

---

## 💾 Backup & Sync Strategy

**Local Backups (Automatic):**
- Frequency: Daily (configurable)
- Location: User-specified (e.g., `D:/Backups/CORTEX`)
- Retention: 30 days (configurable)
- Size: ~10-50MB per backup (compressed)

**Cloud Sync (Optional):**
- Providers: OneDrive, Dropbox, Google Drive
- What syncs: Documents, templates, configs
- What doesn't sync: Databases (use local backup)
- Privacy: User controls what syncs

**Commands:**
- `cortex backup now` - Manual backup
- `cortex restore [backup-file]` - Restore from backup
- `cortex sync status` - Show sync configuration

---

## ⚡ Incremental Planning (Token-Efficient)

**Version:** 3.2.0  
**Purpose:** Generate large feature plans without context overflow using skeleton-first approach with user checkpoints  
**Status:** ✅ PRODUCTION (Sprint 3 complete)

### What Is Incremental Planning?

Incremental planning generates feature plans in small, token-efficient chunks with user approval checkpoints. This prevents context overflow on large plans while giving you control at each phase.

**Key Features:**
- **Skeleton-First:** 200-token structure generated first, user approves before continuing
- **Chunked Sections:** Each section limited to 500 tokens (prevents context overflow)
- **4 Approval Checkpoints:** Review skeleton, Phase 1, Phase 2, Phase 3 before finalizing
- **Memory Efficient:** Streams to disk as generated (never holds full plan in memory)
- **Auto-Organize:** Completed plans automatically filed to `cortex-brain/documents/planning/`

### Token Budget

| Component | Token Limit | Content |
|-----------|-------------|---------|
| **Skeleton** | 200 tokens | 3-phase structure, section placeholders |
| **Each Section** | 500 tokens | Detailed content per section |
| **Total Plan** | ~4,700 tokens | 200 skeleton + 9 sections × 500 |

**Approximation:** 1 token ≈ 4 characters (English text)

### Workflow

```
User: "plan [feature] --incremental"
    ↓
CORTEX: Generates 200-token skeleton (phase breakdown)
    ↓
Checkpoint 1: Review skeleton? (approve/reject)
    ↓ (if approved)
CORTEX: Fills Phase 1 sections (Requirements, Dependencies, Architecture)
    ↓
Checkpoint 2: Review Phase 1? (approve/reject)
    ↓ (if approved)
CORTEX: Fills Phase 2 sections (Implementation, Tests, Integration)
    ↓
Checkpoint 3: Review Phase 2? (approve/reject)
    ↓ (if approved)
CORTEX: Fills Phase 3 sections (Acceptance, Security, Deployment)
    ↓
Checkpoint 4: Review Phase 3? (approve/reject)
    ↓ (if approved)
CORTEX: Streams complete plan to file → Auto-organizes
    ↓
✅ Plan complete: cortex-brain/documents/planning/features/PLAN-[date]-[feature].md
```

### Commands

| Command | Description | Mode |
|---------|-------------|------|
| `plan [feature] --incremental` | Start incremental planning with checkpoints | Interactive |
| `plan [feature] --incremental --auto-approve` | Generate full plan without checkpoints | Automated |
| `continue plan` | Approve current checkpoint and continue | Interactive |
| `reject plan` | Reject current checkpoint (stop generation) | Interactive |

**Natural Language Examples:**
- "Generate incremental plan for user authentication"
- "Create token-efficient plan for REST API"
- "Plan payment integration with checkpoints"

### Usage Examples

**Example 1: Interactive Mode (Default)**

```python
# User: "plan user authentication --incremental"

# CORTEX generates skeleton (200 tokens)
"""
# Feature Plan: User Authentication

## Phase 1: Foundation
- Requirements Analysis
- Dependency Mapping
- Architecture Design

## Phase 2: Implementation
- Implementation Plan
- Test Strategy
- Integration Points

## Phase 3: Deployment
- Acceptance Criteria
- Security Review
- Deployment Strategy
"""

# CORTEX: "✅ Skeleton generated (187 tokens). Review and approve?"

# User: "approve"

# CORTEX fills Phase 1 (3 sections × 500 tokens)
# CORTEX: "✅ Phase 1 complete (1,450 tokens). Review sections?"

# User: "approve"

# (Continues through Phase 2, Phase 3, then writes complete plan)
```

**Example 2: Automated Mode (No Checkpoints)**

```python
# User: "plan REST API for product catalog --incremental --auto-approve"

# CORTEX: Auto-approves all checkpoints, generates full plan
# No user interaction needed (useful for testing, batch processing)

# CORTEX: "✅ Plan complete: PLAN-2025-11-26-product-catalog-api.md"
```

**Example 3: Rejection Handling**

```python
# User: "plan e-commerce checkout flow --incremental"

# CORTEX: "✅ Skeleton generated. Review?"
# User: "reject - missing payment gateway integration"

# CORTEX: "❌ Plan skeleton rejected by user. Reason: missing payment gateway integration"
# CORTEX: "Would you like to regenerate with additional requirements?"
```

### API Reference (PlanningOrchestrator)

```python
def generate_incremental_plan(
    self,
    feature_requirements: str,
    checkpoint_callback: Optional[Callable[[str, str, str], bool]] = None,
    output_filename: Optional[str] = None
) -> Tuple[bool, Optional[Path], str]:
    """
    Generate feature plan incrementally with user checkpoints.
    
    Args:
        feature_requirements: Feature description (converted to structured dict)
        checkpoint_callback: Optional approval handler (checkpoint_id, section_name, preview) -> bool
                           If None, auto-approves all checkpoints
        output_filename: Optional custom filename (default: auto-generated with timestamp)
    
    Returns:
        (success: bool, file_path: Optional[Path], message: str)
        
    Checkpoints:
        1. "skeleton" - After 200-token structure generation
        2. "phase_1" - After Requirements, Dependencies, Architecture (3 sections)
        3. "phase_2" - After Implementation, Tests, Integration (3 sections)
        4. "phase_3" - After Acceptance, Security, Deployment (3 sections)
    
    Example:
        # Auto-approve mode
        success, path, msg = orchestrator.generate_incremental_plan(
            "User authentication with JWT tokens"
        )
        
        # Interactive mode
        def approve(checkpoint_id, section_name, preview):
            print(f'=== {section_name} ===')
            print(preview[:200])
            return input('Approve? (y/n): ').lower() == 'y'
        
        success, path, msg = orchestrator.generate_incremental_plan(
            "REST API for product catalog",
            checkpoint_callback=approve
        )
    """
```

### Benefits

**Context Efficiency:**
- ✅ Never exceeds token budget (each chunk ≤500 tokens)
- ✅ Prevents context overflow on large plans
- ✅ Predictable memory usage

**User Control:**
- ✅ Review structure before generating details (skeleton checkpoint)
- ✅ Approve each phase independently (catch issues early)
- ✅ Reject and regenerate without wasting full plan generation

**Memory Safety:**
- ✅ Streaming architecture (write-as-you-go)
- ✅ Never holds full plan in memory
- ✅ Progress tracking with ETA

**Backward Compatibility:**
- ✅ Existing `generate_plan()` method unchanged
- ✅ Non-incremental planning still available
- ✅ Zero breaking changes

### Implementation Status

**Sprint 3: Incremental Planning - ✅ COMPLETE (Nov 2025)**

| Phase | Status | Tests | Time |
|-------|--------|-------|------|
| Phase 1: IncrementalPlanGenerator | ✅ Complete | 25/25 passing | 2h (50% under budget) |
| Phase 2: StreamingPlanWriter | ✅ Complete | 32/32 passing | 3h (on time) |
| Phase 3: PlanningOrchestrator Integration | ✅ Complete | 16/16 passing | 1.5h (25% under) |
| Phase 4: Testing & Validation | ✅ Complete | 73/73 passing | 0.5h (75% under) |
| Phase 5: Documentation | ✅ Complete | N/A | 1h |

**Total Time:** 8h actual / 12h estimated (67% of budget)  
**Commits:** 3 (28d5900b, b2bd0cbb, 4387b716)  
**Zero Regressions:** All 656 CORTEX tests passing

---

## 📊 Implementation Status

**Phase 1: Vision API Integration** - ⏳ PLANNED (60-90 min)  
**Phase 2: Unified Planning Core** - ⏳ PLANNED (90 min)  
**Phase 3: File-Based Workflow** - ⏳ PLANNED (90 min)  
**Phase 4: .gitignore & Backups** - ⏳ PLANNED (45 min)  
**Phase 5: Integration & Testing** - ⏳ PLANNED (60 min)  
**Phase 6: Documentation** - ⏳ PLANNED (30 min)

**Total Estimated Time:** 6-7 hours

---

## 📖 DoR/DoD Framework

### Definition of Ready (DoR)

**Requirements Checklist:**
- [ ] Requirements documented with zero ambiguity
- [ ] All vague terms replaced with specific metrics
- [ ] Dependencies identified and validated
- [ ] Technical design approach agreed upon
- [ ] Test strategy defined
- [ ] Acceptance criteria are measurable
- [ ] Security review completed (OWASP checklist)
- [ ] User approval on scope and approach

**Ambiguity Detection Examples:**

**❌ VAGUE:**
```
"Improve performance"
"Make it user-friendly"
"Enhance security"
```

**✅ SPECIFIC:**
```
"Reduce API response time from 500ms to 200ms"
"Add inline validation with error messages within 100ms"
"Implement OAuth 2.0 with JWT tokens (15-min expiry)"
```

---

### Definition of Done (DoD)

**Quality Checklist:**
- [ ] Code reviewed and approved by peer
- [ ] Unit tests written (≥80% coverage)
- [ ] Integration tests passing
- [ ] Documentation updated (API docs, README)
- [ ] Security scan passed (no critical vulnerabilities)
- [ ] Performance benchmarks met
- [ ] Deployed to staging environment
- [ ] Acceptance criteria validated
- [ ] User acceptance testing completed
- [ ] Production deployment checklist complete

---

## 🔒 Security Review (OWASP Integration)

**Auto-Detection:** CORTEX identifies feature type (authentication/api/data_storage/file_upload/payment) and applies relevant OWASP Top 10 categories.

**Example Security Checklist (Authentication Feature):**

**A01 - Broken Access Control**
- [ ] Authentication required for protected resources?
- [ ] Authorization checks present for all actions?
- [ ] Role-based access control (RBAC) implemented?
- [ ] Session management secure (timeout, revocation)?

**A02 - Cryptographic Failures**
- [ ] Passwords hashed with strong algorithm (bcrypt, Argon2)?
- [ ] Sensitive data encrypted at rest?
- [ ] TLS/SSL used for data in transit?
- [ ] Keys stored securely (not hardcoded)?

**A07 - Identification and Authentication Failures**
- [ ] Multi-factor authentication available?
- [ ] Account lockout after failed attempts?
- [ ] Password complexity requirements enforced?
- [ ] Session tokens unpredictable and properly rotated?

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary
