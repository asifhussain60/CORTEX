# CORTEX Migrate Orchestrator v1 - Prompt Specification

**Version:** 1.0.0  
**Created:** 2026-01-09  
**Author:** Asif Hussain  
**Status:** Specification (Implementation in Stage 3, Phase 3.5)

---

## 🎯 PURPOSE

The Migrate Orchestrator enables on-demand migration of CORTEX-stored plans to user repositories. By default, CORTEX stores all plans centrally (git isolation), but users can choose to migrate specific plans to their local repos when needed.

---

## 🔀 INTENT ROUTING

**Primary Triggers:**
- `migrate plan`
- `export plan`
- `move plan to repo`
- `migrate plan to user repo`

**Pattern Matching:**
```regex
^(migrate|export|move)\s+(plan|plans?)(\s+to\s+(user\s+)?repo)?
```

**Priority:** 5 (Medium - user-initiated operations)

---

## 📋 ORCHESTRATOR WORKFLOW

### **Phase 1: Plan Detection and Validation**

**Objective:** Locate source plan in CORTEX storage and validate migration target.

**Steps:**
1. **Parse User Request:** Extract plan identifier (name, ID, or select from list)
2. **Locate Source Plan:** Search `cortex-brain/documents/planning/user-repos/{repo}/`
3. **Validate Plan Exists:** Verify plan folder contains valid artifacts
4. **Detect Current Repo:** Determine user's current working directory repo name
5. **Validate Target Repo:** 
   - Check for `.git/` folder (must be git repo)
   - Verify write permissions
   - Check for existing `.cortex/plans/` conflicts

**Success Criteria:**
- ✅ Source plan located and valid
- ✅ Target repo is git repo
- ✅ Write permissions confirmed
- ✅ No conflicts detected

**Error Handling:**
- Plan not found → List available plans, prompt user to select
- Not a git repo → Error: "Current directory is not a git repository"
- Permission denied → Error: "Cannot write to current directory"
- Conflict exists → Prompt: "`.cortex/plans/{plan}` already exists. Overwrite? (y/N)"

---

### **Phase 2: User Confirmation**

**Objective:** Confirm migration details and optional actions with user.

**Confirmation Prompts:**

```
🔄 Migrate Plan: {plan_name}

Source: {cortex_path}
Destination: {user_repo_path}/.cortex/plans/{plan_name}/

Files to migrate: {file_count}
Estimated size: {total_size}

Confirm migration? (Y/n): _
```

**Optional Actions:**

```
📝 .gitignore Management

Add .cortex/ to .gitignore? (Y/n): _
Reason: Prevents accidental commit of CORTEX plans to user repo

🔗 Symlink Maintenance

Keep symlink in CORTEX? (Y/n): _
Reason: Allows cortex commands to reference plan via both paths
```

**Defaults:**
- Confirm migration: **Yes** (user must explicitly cancel)
- Add to .gitignore: **Yes** (recommended for git isolation)
- Keep symlink: **Yes** (convenience for dual-path access)

---

### **Phase 3: Directory Structure Creation**

**Objective:** Create `.cortex/plans/{plan_name}/` structure in user repo.

**Directory Tree:**
```
user-repo/
└── .cortex/
    └── plans/
        └── {plan_name}/
            ├── acceptance-criteria/
            ├── analysis/
            ├── artifacts/
            ├── tracking/
            ├── implementation-guides/
            └── summaries/
```

**Permissions:**
- Owner: read/write/execute
- Group: read/execute
- Others: read/execute

**Success Criteria:**
- ✅ `.cortex/` directory created
- ✅ `plans/{plan_name}/` subfolder created
- ✅ All subfolders match CORTEX plan structure
- ✅ Proper permissions set

---

### **Phase 4: Artifact Copy**

**Objective:** Copy all plan artifacts from CORTEX to user repo.

**Copy Strategy:**
- **Method:** `shutil.copytree()` with symlinks=False
- **Verification:** SHA256 checksum validation
- **Progress:** Display progress for large plans (>100 files)

**Artifacts Copied:**
- `config.yaml` (plan configuration)
- `todos.yaml` (task list)
- `acceptance-criteria/*.yaml` (AC files)
- `tracking/*.md` (progress tracking)
- `analysis/*.md` (analysis documents)
- `artifacts/*.yaml` (plan artifacts)
- `summaries/*.md` (summaries)
- `implementation-guides/*.md` (guides)

**Exclusions (not copied):**
- `.git/` (if present in plan folder)
- `__pycache__/`
- `.DS_Store`
- Temporary files (`*.tmp`, `*.swp`)

**Success Criteria:**
- ✅ All files copied successfully
- ✅ Checksums match source files
- ✅ File count matches source
- ✅ No data loss

---

### **Phase 5: Gitignore Management**

**Objective:** Optionally add `.cortex/` to user repo's `.gitignore`.

**Implementation:**

```python
def add_to_gitignore(repo_path: str, user_confirmed: bool):
    if not user_confirmed:
        return  # User declined
    
    gitignore_path = os.path.join(repo_path, '.gitignore')
    
    if os.path.exists(gitignore_path):
        # Check if .cortex/ already present
        with open(gitignore_path, 'r') as f:
            if '.cortex/' in f.read():
                return  # Already present, no action
        
        # Append .cortex/
        with open(gitignore_path, 'a') as f:
            f.write('\n# CORTEX plans (generated)\n.cortex/\n')
    else:
        # Create .gitignore
        with open(gitignore_path, 'w') as f:
            f.write('# CORTEX plans (generated)\n.cortex/\n')
```

**Success Criteria:**
- ✅ `.gitignore` updated (if user confirmed)
- ✅ No duplicates in `.gitignore`
- ✅ `.gitignore` created if missing
- ✅ Proper formatting (comment + entry)

---

### **Phase 6: Symlink Creation**

**Objective:** Optionally maintain symlink in CORTEX pointing to migrated plan.

**Implementation:**

```python
def create_symlink(source_path: str, target_path: str, user_confirmed: bool):
    if not user_confirmed:
        return  # User declined
    
    # Remove original plan folder (replace with symlink)
    shutil.rmtree(source_path)
    
    # Create symlink
    os.symlink(target_path, source_path)
```

**Symlink Details:**
- **Source:** `cortex-brain/documents/planning/user-repos/{repo}/{plan}/`
- **Target:** `~/user-repo/.cortex/plans/{plan}/`
- **Type:** Symbolic link (relative path preferred)

**Success Criteria:**
- ✅ Symlink created (if user confirmed)
- ✅ Points to correct target
- ✅ Readable from CORTEX
- ✅ Plan accessible via both paths

---

### **Phase 7: Audit Logging**

**Objective:** Log complete migration event for audit trail.

**Audit Entry:**
```json
{
  "timestamp": "2026-01-09T18:30:00Z",
  "ac_id": "AC-ORC-MIGRATE-006",
  "category": "orchestrator",
  "operation": "migrate_plan",
  "status": "success",
  "duration_ms": 1523,
  "metadata": {
    "plan_id": "plan-abc-123",
    "plan_name": "feature-authentication",
    "source_path": "/Users/user/PROJECTS/CORTEX/cortex-brain/.../user-repos/my-project/",
    "destination_path": "/Users/user/my-project/.cortex/plans/feature-authentication/",
    "files_copied": 47,
    "total_size_bytes": 1048576,
    "symlink_created": true,
    "gitignore_updated": true,
    "user_repo": "my-project"
  }
}
```

**Success Criteria:**
- ✅ Audit entry logged to audit.db
- ✅ All metadata captured
- ✅ Queryable via `mcp_audit_validate('AC-ORC-MIGRATE-006')`

---

### **Phase 8: Completion Report**

**Objective:** Display migration summary to user.

**Report Format:**
```
✅ Migration Complete

Plan: feature-authentication
Source: CORTEX storage
Destination: ~/my-project/.cortex/plans/feature-authentication/

📊 Summary:
  Files copied: 47
  Total size: 1.0 MB
  Duration: 1.5 seconds

🔧 Actions Taken:
  ✅ .cortex/ added to .gitignore
  ✅ Symlink maintained in CORTEX

📍 Access Plan:
  From user repo: cd .cortex/plans/feature-authentication/
  From CORTEX: cortex plan "feature-authentication" (via symlink)

🔍 Verify Migration:
  ls -la ~/my-project/.cortex/plans/feature-authentication/
  cortex audit validate AC-ORC-MIGRATE-006
```

---

## 🔒 ERROR HANDLING

### **Common Errors:**

**E-MIG-001: Plan Not Found**
```
❌ Error: Plan '{plan_name}' not found in CORTEX storage.

Available plans for this repo:
  1. feature-authentication
  2. feature-user-profile
  3. bugfix-login-issue

Select plan (1-3) or cancel (C): _
```

**E-MIG-002: Not a Git Repository**
```
❌ Error: Current directory is not a git repository.

Migration requires a git-initialized repository.

Initialize git:
  git init
  
Or navigate to existing repo:
  cd ~/my-project/
```

**E-MIG-003: Permission Denied**
```
❌ Error: Cannot write to current directory.

Check permissions:
  ls -la .
  
Resolve:
  chmod u+w .
  
Or run with elevated permissions:
  sudo cortex migrate plan '{plan_name}'
```

**E-MIG-004: Conflict Detected**
```
⚠️  Warning: .cortex/plans/{plan_name}/ already exists.

Options:
  1. Overwrite (delete existing, migrate fresh)
  2. Merge (keep existing, skip conflicts)
  3. Rename (migrate to .cortex/plans/{plan_name}-2/)
  4. Cancel

Select option (1-4): _
```

---

## 🧪 VALIDATION

### **Test Scenarios:**

**T-MIG-001: Happy Path**
- User in user repo
- Valid plan in CORTEX storage
- No conflicts
- User confirms all prompts
- **Expected:** Plan migrated, .gitignore updated, symlink created

**T-MIG-002: Decline Migration**
- User selects plan
- User declines confirmation
- **Expected:** No changes made, operation cancelled

**T-MIG-003: Conflict Resolution**
- `.cortex/plans/{plan}/` already exists
- User selects "Overwrite"
- **Expected:** Existing deleted, fresh migration

**T-MIG-004: No Gitignore**
- User repo has no `.gitignore`
- User confirms gitignore management
- **Expected:** `.gitignore` created with `.cortex/`

**T-MIG-005: Large Plan**
- Plan has 500+ files
- Total size >100MB
- **Expected:** Progress indicator shown, successful migration

---

## 📊 PERFORMANCE TARGETS

| Metric | Target | Measurement |
|--------|--------|-------------|
| Small Plan (<10 files) | <500ms | End-to-end migration time |
| Medium Plan (10-100 files) | <2 seconds | End-to-end migration time |
| Large Plan (100-500 files) | <10 seconds | End-to-end migration time |
| Symlink Creation | <10ms | OS-level operation |
| Gitignore Update | <50ms | File append operation |

---

## 🔗 INTEGRATION POINTS

**Dependencies:**
- AuditLogger (for logging)
- WorkspaceDetector (for repo context)
- StateManager (for plan metadata)
- MCP tools (for validation)

**Upstream:**
- User command: `cortex migrate plan`
- Intent router → Migrate Orchestrator

**Downstream:**
- Audit.db (migration events)
- User repo `.cortex/` folder
- CORTEX symlinks

---

## 📚 USAGE EXAMPLES

### **Example 1: Simple Migration**
```bash
~/my-project$ cortex migrate plan "feature-authentication"

# Orchestrator detects plan, confirms, migrates
✅ Migration Complete
```

### **Example 2: Interactive Selection**
```bash
~/my-project$ cortex migrate plan

Select plan to migrate:
  1. feature-authentication
  2. feature-user-profile

Enter number (1-2): 1

Confirm migration? (Y/n): Y
Add .cortex/ to .gitignore? (Y/n): Y
Keep symlink in CORTEX? (Y/n): Y

✅ Migration Complete
```

### **Example 3: Decline Gitignore**
```bash
~/my-project$ cortex migrate plan "bugfix-login"

Add .cortex/ to .gitignore? (Y/n): n
# .gitignore not updated

Keep symlink in CORTEX? (Y/n): Y

✅ Migration Complete (no .gitignore update)
```

---

## 🚀 IMPLEMENTATION CHECKLIST

**Stage 3, Phase 3.5 (6-8 hours):**

- [ ] Create `src/orchestrators/migrate_orchestrator.py`
- [ ] Create `cortex-brain/manifests/orchestrators/migrate.yaml`
- [ ] Implement 8 phases (detection, confirmation, copy, etc.)
- [ ] Add error handling (5 error codes)
- [ ] Implement user prompts (3 confirmations)
- [ ] Add progress indicator (for large plans)
- [ ] Write tests: `tests/orchestrators/test_migrate.py`
- [ ] Test all scenarios (T-MIG-001 to T-MIG-005)
- [ ] Validate performance targets (<10s for large plans)
- [ ] Document in README (usage examples)

---

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Status:** Finalized - Ready for Stage 3 Implementation
