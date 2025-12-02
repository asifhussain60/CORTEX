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

## 🔖 Git Checkpoint Integration

**Version:** 3.3.0  
**Purpose:** Automatic git checkpoints during plan generation, approval, and completion for instant rollback capability  
**Status:** ✅ PRODUCTION (100% tested - 12/12 tests passing)

### What Is Git Checkpoint Integration?

The Planning Orchestrator automatically creates git checkpoints (tags) at key workflow stages, enabling instant rollback to any previous state without losing work.

**Key Benefits:**
- **Instant Rollback:** Return to any planning state in seconds
- **Safe Experimentation:** Try bold changes without fear of data loss
- **Clear History:** Track exactly what changed and when
- **Zero Data Loss:** Never lose planning work due to mistakes
- **Non-Blocking:** Planning succeeds even if checkpoints fail

### Automatic Checkpoint Creation

Git checkpoints are automatically created at three critical workflow stages:

**1. Before Plan Generation (operation="plan"):**
```
User: "plan user authentication feature"

CORTEX:
  🔍 Checking git status...
  ✅ Clean working tree
  📸 Creating checkpoint: plan-20251130-143022
  
  [... generates plan ...]
  
  ✅ Plan generated: PLAN-20251130-authentication.md
  📍 Rollback available: plan-20251130-143022
```

**2. After Plan Approval (operation="approve"):**
```
User: "approve plan authentication"

CORTEX:
  📸 Creating checkpoint: approve-20251130-143856
  ✅ Plan approved: PLAN-20251130-authentication.md
  📂 Moved to: approved/APPROVED-20251130-authentication.md
```

**3. After Plan Completion (operation="complete"):**
```
User: "complete plan authentication"

CORTEX:
  📸 Creating checkpoint: complete-20251130-144512
  ✅ Plan completed: PLAN-20251130-authentication.md
  📂 Moved to: completed/COMPLETED-20251130-authentication.md
```

### Checkpoint Triggers

Three new triggers enable planning checkpoints (configured in `cortex-brain/git-checkpoint-rules.yaml`):

```yaml
triggers:
  before_plan_generation:
    enabled: true
    operations: ["plan"]
    
  after_plan_approval:
    enabled: true
    operations: ["approve"]
    
  after_plan_completion:
    enabled: true
    operations: ["complete"]
```

**Trigger Timing:**
- **before_plan_generation:** Creates checkpoint BEFORE planning workflow starts (pre-work safety point)
- **after_plan_approval:** Creates checkpoint AFTER plan moves to approved status (approval milestone)
- **after_plan_completion:** Creates checkpoint AFTER plan moves to completed status (completion milestone)

### Checkpoint Naming Convention

All planning checkpoints follow the format: `{operation}-{YYYYMMDD}-{HHMMSS}`

**Examples:**
- `plan-20251130-143022` - Plan generation checkpoint (Nov 30, 2025 at 2:30:22 PM)
- `approve-20251130-143856` - Plan approval checkpoint (Nov 30, 2025 at 2:38:56 PM)
- `complete-20251130-144512` - Plan completion checkpoint (Nov 30, 2025 at 2:45:12 PM)

### Viewing Checkpoints

**Recommended: Use CORTEX Commands:**
```
User: "show checkpoints"

CORTEX:
  📋 Git Checkpoints (Last 30 Days):
  
  Recent Planning Checkpoints:
  1. complete-20251130-144512 (completion) - 2 hours ago
  2. approve-20251130-143856 (approval) - 3 hours ago
  3. plan-20251130-143022 (generation) - 3 hours ago
  
  💡 Tip: Use 'rollback to <checkpoint>' to restore any checkpoint
```

**Alternative: Direct Git Commands (Advanced):**

<details>
<summary>Click to expand git command reference</summary>

```bash
# Show all checkpoints from today
git tag -l '*-20251130-*' --sort=-creatordate

# Show only plan generation checkpoints
git tag -l 'plan-*'

# Show only approval checkpoints
git tag -l 'approve-*'

# Show only completion checkpoints
git tag -l 'complete-*'

# Show commit info for checkpoint
git show plan-20251130-143022

# Show commit message
git log -1 plan-20251130-143022

# Show files changed at checkpoint
git show plan-20251130-143022 --stat

# Show changes since checkpoint
git diff plan-20251130-143022

# Show only file names changed
git diff plan-20251130-143022 --name-only

# Show summary of changes
git diff plan-20251130-143022 --stat
```

</details>

### Rollback Procedures

**Rollback Plan Approval (Return to Active State):**

If you approved a plan prematurely and need to make changes:

**Recommended: Use CORTEX Rollback Command:**
```
User: "rollback to approve-20251130-143856"

CORTEX:
  ⚠️  ROLLBACK WARNING
  
  This will DISCARD all changes after checkpoint 'approve-20251130-143856'
  
  Changes to be lost:
   cortex-brain/documents/planning/approved/APPROVED-20251130-authentication.md
   src/auth/authentication_service.py
   2 files changed, 150 insertions(+)
  
  Type 'yes' to confirm rollback: yes
  
  📸 Creating safety checkpoint: pre-rollback-20251130-150000
  ✅ Rolled back to checkpoint: approve-20251130-143856
  
  Plan restored to: cortex-brain/documents/planning/active/PLAN-20251130-authentication.md
```

**Alternative: Direct Git Commands (Advanced):**
```bash
# 1. List available checkpoints
git tag -l 'approve-*' --sort=-creatordate

# 2. View checkpoint details
git show approve-20251130-143856

# 3. Preview changes to be undone
git diff approve-20251130-143856

# 4. Execute rollback
git reset --hard approve-20251130-143856

# 5. Verify plan restored to active/
ls cortex-brain/documents/planning/active/
```

**Alternative: CORTEX Rollback Command:**
```
User: "rollback to approve-20251130-143856"

CORTEX:
  ⚠️  ROLLBACK WARNING
  
  This will DISCARD all changes after checkpoint 'approve-20251130-143856'
  
  Changes to be lost:
   cortex-brain/documents/planning/approved/APPROVED-20251130-authentication.md
   src/auth/authentication_service.py
   2 files changed, 150 insertions(+)
  
  Type 'yes' to confirm rollback: yes
  
  📸 Creating safety checkpoint: pre-rollback-20251130-150000
  ✅ Rolled back to checkpoint: approve-20251130-143856
  
  Plan restored to: cortex-brain/documents/planning/active/PLAN-20251130-authentication.md
```

**Rollback Plan Generation (Undo Planning Entirely):**

**Recommended: Use CORTEX Rollback Command:**
```
User: "rollback to plan-20251130-143022"

CORTEX:
  ⚠️  ROLLBACK WARNING
  
  This will DISCARD all changes after checkpoint 'plan-20251130-143022'
  (This undoes the entire planning session)
  
  Type 'yes' to confirm rollback: yes
  
  📸 Creating safety checkpoint: pre-rollback-20251130-150000
  ✅ Rolled back to checkpoint: plan-20251130-143022
```

**Alternative: Direct Git Command (Advanced):**
```bash
# Revert to state before planning started
git reset --hard plan-20251130-143022
```

### Error Handling (Non-Blocking Design)

Checkpoints are **non-blocking** - planning operations succeed even if checkpoint creation fails.

**Design Principles:**
- **User Value Priority:** Planning operations deliver immediate value and are prioritized
- **Checkpoint is Enhancement:** Git checkpoints are safety features, not requirements
- **Graceful Degradation:** System remains functional when non-critical features fail
- **User Awareness:** Warnings logged so users know checkpoint didn't save

**Example: Git Not Available**
```
User: "plan feature" (working in non-git directory)

CORTEX:
  ⚠️  Git checkpoint failed: Not a git repository
  Planning will continue without checkpoint
  
  [... generates plan normally ...]
  
  ✅ Plan generated: PLAN-20251130-feature.md
  ⚠️  Note: No rollback checkpoint created (git unavailable)
```

**Example: Permission Error**
```
User: "approve plan feature"

CORTEX:
  ⚠️  Git checkpoint failed: Permission denied (.git/ directory read-only)
  Plan approval completed successfully
  
  ✅ Plan approved: PLAN-20251130-feature.md
  💡 Tip: Fix .git/ permissions to enable checkpoints
```

**Example: Disk Space Full**
```
User: "complete plan feature"

CORTEX:
  ⚠️  Git checkpoint failed: No space left on device
  Plan completion succeeded
  
  ✅ Plan completed: PLAN-20251130-feature.md
  💡 Tip: Free up disk space and manually create checkpoint
```

### Troubleshooting

**Checkpoint Not Created:**

*Symptoms:* No checkpoint appears after planning operation

*Causes & Solutions:*
- ❌ **Not a git repository** → Initialize git: `git init`
- ❌ **No write permissions** → Fix permissions: `chmod -R 755 .git/`
- ❌ **Disk space full** → Free up space, then manually create checkpoint
- ❌ **Repository corrupted** → Check git health: `git fsck`

**Planning Continues Despite Error:**

*Symptoms:* Warning about checkpoint failure, but plan generated

*Status:* ✅ **Expected behavior** (non-blocking design)

*Why:* Planning operations prioritized over checkpoints. Checkpoint failures don't block user value delivery.

**Multiple Checkpoints Created:**

*Symptoms:* Many checkpoints accumulating over time

*Status:* ✅ **Expected behavior** (one checkpoint per operation)

*Solution:* Use checkpoint cleanup commands from Git Checkpoint Guide:
```bash
# List old checkpoints (30+ days)
git tag -l '*-2024*' --sort=-creatordate

# Delete specific checkpoint
git tag -d plan-20241015-120000

# Bulk delete old checkpoints
git tag -l 'plan-2024*' | xargs git tag -d
```

### Configuration Options

**Enable/Disable Checkpoints:**

Edit `cortex-brain/git-checkpoint-rules.yaml`:

```yaml
# Disable all planning checkpoints
triggers:
  before_plan_generation:
    enabled: false
  after_plan_approval:
    enabled: false
  after_plan_completion:
    enabled: false

# Or disable specific triggers
triggers:
  before_plan_generation:
    enabled: true    # Keep plan generation checkpoints
  after_plan_approval:
    enabled: false   # Disable approval checkpoints
  after_plan_completion:
    enabled: false   # Disable completion checkpoints
```

**Retention Policy:**

Configure automatic checkpoint cleanup:

```yaml
retention:
  max_age_days: 30           # Delete checkpoints older than 30 days
  max_count: 50              # Keep maximum 50 checkpoints
  preserve_named: true       # Never delete user-named checkpoints
```

### Related Examples

**Comprehensive Documentation:**
- **Basic Usage:** `cortex-brain/documents/examples/planning-with-git-checkpoints.md` (300+ lines)
  - Complete workflow example (generate → approve → complete)
  - Viewing checkpoints with git commands
  - Checkpoint operations reference
  - Benefits and use cases

- **Rollback Scenario:** `cortex-brain/documents/examples/rollback-plan-approval.md` (400+ lines)
  - 9-step detailed rollback procedure
  - Alternative CORTEX rollback command
  - When to rollback (4 scenarios)
  - Best practices and troubleshooting

- **Error Handling:** `cortex-brain/documents/examples/checkpoint-failure-handling.md` (450+ lines)
  - Why non-blocking design matters
  - 3 detailed failure scenarios
  - Error handling implementation
  - 4 checkpoint failure types with recovery

**System Guides:**
- **Git Checkpoint System:** `.github/prompts/modules/git-checkpoint-guide.md`
  - Complete checkpoint system documentation
  - TDD workflow integration
  - Rollback procedures
  - Configuration options

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

## 🛡️ Threat Modeling Integration

**What:** Automated security threat analysis using STRIDE framework integrated into planning workflow

**When:** Threat modeling runs automatically after DoR validation and before plan generation

**Framework:** STRIDE (Spoofing, Tampering, Repudiation, Information Disclosure, Denial of Service, Elevation of Privilege)

### How It Works

```
User: "plan user authentication feature"
    ↓
CORTEX: 
  ✅ DoR validation passed
  🔒 Running threat analysis...
  ✅ Identified 8 threats (2 Critical, 3 High, 3 Medium)
  ✅ Generated mitigation strategies with code examples
  ✅ Mapped to OWASP Top 10 2021
  ✅ Updated DoD with security criteria
    ↓
Plan Output:
  - Phase sections (Requirements, Architecture, Implementation)
  - Security section with threat analysis
  - DoD updated with threat mitigations
  - Standalone threat report generated
```

### Threat Analysis Output

**Quick Summary:**
- Total threats identified
- Risk distribution (Critical/High/Medium/Low)
- OWASP Top 10 mapping
- Top 3 threats requiring immediate attention
- Quick mitigation recommendations

**Detailed Report Includes:**
- Full STRIDE breakdown
- Each threat with:
  - Category (e.g., Spoofing)
  - Description
  - Risk rating (CRITICAL/HIGH/MEDIUM/LOW)
  - Attack scenario
  - Mitigation strategy
  - Implementation code example (C#)
  - Test recommendations
- OWASP Top 10 2021 mapping
- Context-aware risk scoring

### Feature-Specific Threat Templates

CORTEX uses specialized threat templates based on feature type:

**Authentication Features:**
- Credential stuffing attacks
- Session hijacking
- Weak password policies
- Multi-factor authentication bypass

**API Features:**
- Broken authentication
- Excessive data exposure
- Lack of rate limiting
- Injection attacks

**Data Storage Features:**
- SQL injection
- Insecure data at rest
- Missing encryption
- Sensitive data exposure

**File Upload Features:**
- Malicious file upload
- Path traversal
- Unrestricted file types
- Denial of service via large files

**Payment Processing:**
- PCI-DSS compliance gaps
- Payment data exposure
- Transaction tampering
- Insecure payment gateway integration

### Accessing Threat Reports

**Quick Report (in chat):**
```
User: "show threats"
CORTEX: [Displays quick summary with top threats and mitigations]
```

**Detailed Report (file):**
```
Location: cortex-brain/documents/reports/threat-analysis-[feature-name].md
Auto-opens: Yes (when threat analysis completes)
Format: Markdown with structured sections
```

**Integrated in Plan:**
```
Location: cortex-brain/documents/planning/active/[plan-name].md
Section: ## Security Threat Analysis
Includes: All identified threats, mitigations, DoD updates
```

### Security DoD Checklist

Threat modeling automatically adds security items to Definition of Done:

**Critical/High Threats (Must Complete):**
- [ ] SQL injection prevention implemented and tested
- [ ] Authentication bypass vulnerability mitigated
- [ ] Sensitive data encryption at rest configured

**Medium Threats (Should Complete):**
- [ ] Rate limiting implemented for API endpoints
- [ ] Input validation for all user inputs
- [ ] Error handling doesn't leak sensitive information

**Security Testing:**
- [ ] Unit tests for all security controls
- [ ] Integration tests for authentication/authorization
- [ ] Security-focused code review completed

### Commands

```bash
# Run threat analysis on feature description
"analyze threats for [feature]"

# Show quick threat summary
"show threats"

# Show detailed threat report
"detailed threat report"

# Show security DoD checklist
"security checklist"

# Validate security DoD
"validate security"
```

### Example: Authentication Feature Threat Analysis

```markdown
## 🛡️ Security Threat Analysis

**Feature:** User Authentication System
**Analysis Date:** 2025-12-01
**Total Threats:** 8
**Risk Score:** 72/100 (HIGH)

### Critical Threats (2)

1. **Weak Password Storage (Spoofing)**
   - **Risk:** CRITICAL
   - **OWASP:** A02:2021 - Cryptographic Failures
   - **Attack:** Attacker gains database access and cracks passwords
   - **Mitigation:** Use Argon2id or bcrypt with high cost factor
   ```csharp
   using Microsoft.AspNetCore.Identity;
   var hasher = new PasswordHasher<User>();
   string hashedPassword = hasher.HashPassword(user, password);
   ```

2. **Missing Multi-Factor Authentication (Spoofing)**
   - **Risk:** CRITICAL
   - **OWASP:** A07:2021 - Identification and Authentication Failures
   - **Attack:** Compromised password grants full account access
   - **Mitigation:** Implement TOTP-based MFA
   ```csharp
   // Implementation code provided...
   ```

### High Threats (3)
[Details for each high threat...]

### DoD Integration
- [ ] Argon2id password hashing implemented
- [ ] MFA enabled for all user accounts
- [ ] Session timeout configured (15 minutes)
- [ ] All security tests passing (15/15)
```

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
