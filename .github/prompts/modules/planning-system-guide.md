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
