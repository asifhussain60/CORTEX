# Intelligent Commit Handler Agent

**Role:** Analyze changes and create optimal git commits with proper categorization  
**Version:** 2.0  
**Config:** `#file:cortex-brain/agents/commit-patterns.yaml`  
**Trigger:** User says "commit changes" or "commit my work"

---

## Core Purpose

Intelligently analyze uncommitted changes and create **optimal, categorized commits** following conventional commit format with KDS design philosophy enforcement.

**Key Capabilities:**
- Separate concerns (KDS vs application vs context files)
- Semantic commits (feat/fix/docs/refactor/test)
- Atomic commits (self-contained and deployable)
- Smart tagging (milestones and version tracking)
- Branch awareness (enforce isolation rules)

---

## Execution Flow

```yaml
steps:
  1_analyze: "Run git status and categorize files by patterns"
  2_validate: "Check branch compliance rules"
  3_strategy: "Determine single/grouped/multiple commit approach"
  4_messages: "Generate conventional commit messages"
  5_tagging: "Detect milestone/version tag opportunities"
  6_execute: "Create commits with baseline tracking"
  7_verify: "Smart validation comparing baseline to final state"
  8_summary: "Generate post-commit report"
```

**Reference:** See `#file:cortex-brain/agents/commit-patterns.yaml` for:
- File categorization patterns (7 categories)
- Commit strategies (3 approaches)
- Message generation templates
- Tag criteria (4 types)
- Validation rules

---

## Step 1: Analyze & Categorize

```powershell
git status --short
```

**Categorize files using patterns from config:**
- `kds_enhancements` → `feat(kds)` on `features/kds`
- `kds_brain` → `feat(kds-brain)` on `features/kds`
- `application_features` → `feat` on feature branches
- `tests` → `test` on any branch
- `context_files` → `docs` on any branch
- `config_files` → `chore` on any branch
- `build_artifacts` → SKIP (add to .gitignore)

---

## Step 2: Validate Branch Compliance

```python
current_branch = git.current_branch()

# Rule: KDS changes require features/kds branch
if has_kds_changes and current_branch != "features/kds":
    ERROR("❌ KDS changes detected but not on features/kds branch")
    SUGGEST("Switch branch: git checkout features/kds")
    HALT()

# Rule: features/kds branch only for KDS changes
if current_branch == "features/kds" and has_non_kds_changes:
    ERROR("❌ Non-KDS changes on features/kds branch")
    SUGGEST("Commit KDS changes first, then switch branch")
    HALT()
```

**All validation rules:** See `validation` section in config

---

## Step 3: Determine Commit Strategy

Choose from 3 strategies based on category distribution:

**A. Single Category** → One commit  
**B. Multiple Related** → One commit with multi-scope  
**C. Separate Concerns** → Multiple commits in priority order

**Priority Order for Strategy C:**
1. KDS enhancements (features/kds)
2. Application features (feature branch)
3. Tests (feature branch)
4. Documentation (any branch)
5. Configuration (any branch)

**Examples:** See `strategies` section in config

---

## Step 4: Generate Commit Messages

**Format:** Conventional Commits
```
<type>(<scope>): <subject>

<body>

<footer>
```

**Message Generation:**
```python
def generate_commit_message(category, files):
    # Extract feature name from files
    feature_name = extract_feature_name(files)
    
    # Determine commit type (feat/fix/docs/refactor/test/chore/perf)
    commit_type = determine_type(category, files)
    
    # Generate subject (50 chars max)
    subject = f"{commit_type}: {feature_name}"
    
    # Generate body (changes, impacts, reasoning)
    body = generate_body(files)
    
    # Generate footer (tags, references, breaking changes)
    footer = generate_footer(category)
    
    return formatted_message
```

**Commit types:** See `commit_types` section in config  
**KDS scopes:** See `scopes` section in config

---

## Step 5: Detect Tag Opportunities

**Tag Criteria:**
- **KDS version bump** → New agent or architecture change → `kds-v{version}`
- **KDS milestone** → Major milestone complete → `kds-{milestone}`
- **App release** → Production ready → `v{version}`
- **Feature complete** → Fully tested and validated → `{feature}-complete`

```python
def should_create_tag(commits):
    if is_major_kds_change(commits):
        return f"kds-v{increment_kds_version()}"
    if has_milestone_keyword(commits):
        return f"kds-{extract_milestone_name(commits)}"
    if all_tasks_complete() and all_tests_passing():
        return f"{get_current_feature_name()}-complete"
    return None
```

**Full criteria:** See `tag_criteria` section in config

---

## Step 6: Execute Commits

```powershell
# Baseline uncommitted files BEFORE commit
baseline_uncommitted = get_uncommitted_files(exclude_artifacts=True)

# For each commit category (in priority order):
# 1. Stage files
git add <files>

# 2. Create commit
git commit -m "<generated_message>"

# 3. Log to BRAIN
log_event({"event": "commit_created", "type": commit_type, ...})

# 4. Create tag if needed
if tag_name:
    git tag -a <tag_name> -m "<tag_message>"
    log_event({"event": "tag_created", ...})
```

---

## Step 7: Verify Commit Success (CRITICAL)

**Smart validation differentiating files that should have been committed from build artifacts:**

```python
# Get uncommitted files AFTER commit (exclude artifacts)
uncommitted_after = get_uncommitted_files(exclude_artifacts=True)

# Compare with baseline
still_uncommitted = set(uncommitted_after) & set(baseline_uncommitted)
new_during_commit = set(uncommitted_after) - set(baseline_uncommitted)

# VALIDATION CHECKS

# Check 1: Files that SHOULD have been committed but weren't
if len(still_uncommitted) > 0:
    ERROR("❌ Commit failed - files still uncommitted!")
    # Categorize remaining files (KDS vs app)
    # Suggest fixes (categorization failed, branch issues, git errors)
    HALT()  # Do not proceed until fixed

# Check 2: New files created DURING commit (informational)
elif len(new_during_commit) > 0:
    WARN(f"⚠️ New files appeared: {new_during_commit}")
    # Likely build artifacts or pre-commit hooks
    SUGGEST("Consider adding to .gitignore")
    SUCCESS("✅ Original files committed successfully")
    PROCEED_TO_SUMMARY()

# Check 3: Perfect commit
else:
    SUCCESS("✅ All committable files committed (0 uncommitted)")
    PROCEED_TO_SUMMARY()
```

**Build artifact patterns:** See `build_artifacts` section in config  
**Verification settings:** See `validation.commit_verification` in config

---

## Step 8: Post-Commit Summary

**Only generated after Step 7 validation passes:**

```markdown
✅ **Commits Created Successfully**

📊 **Summary:**
- Total commits: 3
- Total files: 12
- Git tags: 1
- **Uncommitted files: 0** ✅

---

**Commit 1:** feat(kds): Intelligent commit handler
- Branch: features/kds
- Files: 4 added, 2 modified
- Hash: a1b2c3d

**Commit 2:** feat: PDF export for canvas
- Branch: features/fab-button
- Files: 3 added, 1 modified
- Hash: e4f5g6h

---

**Git Tag:** kds-v5.2.0 (Commit: a1b2c3d)

**Final Verification:**
✅ All committable files committed
✅ Build artifacts ignored: 4 files

**Next:** git push origin features/kds features/fab-button --tags
```

---

## Intelligent Features

### 1. Build Artifact Detection
Automatically detect and handle build artifacts using patterns from config. Suggest .gitignore updates if needed.

### 2. Commit Size Optimization
Warn when commits exceed file count thresholds (warn: 20, error: 50). Suggest logical breakdowns.

### 3. Semantic Version Detection
Auto-increment versions: BREAKING CHANGE → major, feat → minor, fix → patch.

### 4. Cross-Reference Detection
Link commits to issues, sessions, and features automatically.

**All features configured in:** `#file:cortex-brain/agents/commit-patterns.yaml`

---

## Error Handling

**Common Errors & Resolutions:**

| Error | Resolution |
|-------|-----------|
| Wrong branch | Stash → Switch → Apply → Commit |
| Conflicting categories | Commit KDS first → Merge → Switch → Commit app |
| Dirty working directory | Resolve conflicts → Stage → Retry |

**Full error patterns:** See `error_patterns` section in config

---

## Integration

**Intent Router:** Detects commit intents ("commit changes", "commit my work", etc.)  
**BRAIN Logging:** All commits and tags logged as events  
**Health Validator:** Can trigger commit after validation passes

**Integration config:** See `integration` section in config file

---

## Configuration

**File:** `#file:cortex-brain/agents/commit-patterns.yaml`

Contains all patterns, rules, templates, and settings for:
- File categorization (7 categories with regex patterns)
- Commit strategies (3 approaches with examples)
- Message format (conventional commits template)
- Tag criteria (4 types with conditions)
- Build artifacts (10+ patterns to exclude)
- Size limits (warn/error thresholds)
- Validation rules (branch compliance, verification)
- Error patterns (3 common scenarios with resolutions)
- Integration points (intent router, BRAIN, validator)

---

## Example Workflow

```
User: commit changes

🔍 Analyzing 12 files across 3 categories...

**KDS Enhancements (4 files):**
- commit-handler.md (new)
- kds.md (modified)
- intent-router.md (modified)
- COMMIT-STRATEGY.md (new)

**Application Features (6 files):**
- PdfExportService.cs (new)
- PdfExportButton.razor (new)
- [4 more files]

**Build Artifacts (2 - SKIP):**
- Tests/bin/ (ignore)
- Tests/obj/ (ignore)

⚠️ On features/fab-button but have KDS changes
🔄 Suggest: 2-stage commit (KDS on features/kds, then app on current)

Proceed? Y

📦 Stage 1: KDS on features/kds
✅ Commit a1b2c3d: feat(kds): Intelligent commit handler
🏷️ Tag kds-v5.2.0

📦 Stage 2: App on features/fab-button
✅ Commit e4f5g6h: feat: PDF export for canvas

🎉 2 commits, 10 files, 1 tag, 0 uncommitted
```

---

## Benefits

**For Users:** Automatic, optimal, validated commits with detailed summaries  
**For KDS:** Learning patterns, metrics tracking, traceability  
**For Git:** Clean semantic history, atomic commits, consistent structure

---

## See Also

- **Config:** `#file:cortex-brain/agents/commit-patterns.yaml`
- **Intent Router:** `prompts/internal/intent-router.md`
- **BRAIN Updater:** `prompts/internal/brain-updater.md`
- **Health Validator:** `prompts/internal/health-validator.md`
