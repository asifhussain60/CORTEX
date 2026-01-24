# CORTEX Vacuum Agent Specifications
**Version:** 1.0 | **Updated:** 2026-01-24 | **Authority:** VacuumOrchestrator

---

## 🎯 Overview: 5-Agent Vacuum Framework

The CORTEX Vacuum system operates with 5 specialized agents working in pipeline:

```
FileAnalyzer → PolicyMatcher → SafetyValidator → OperationExecutor → AuditLogger
     ↓              ↓                  ↓                  ↓                ↓
  Scan All      Classify &         Verify             Execute        Record &
  Files        Recommend          Safety             Changes         Report
```

Each agent is stateless and can be tested independently. Data flows through structured outputs.

---

## 🔍 Agent 1: FileAnalyzer

### Identity
```yaml
name: "FileAnalyzer"
role: "Repository Scanner & Classifier"
icon: "🔍"
primary_goal: "Discover and classify every file in CORTEX repository"
depends_on: null  # Entry point agent
```

### Input
```yaml
params:
  repo_root: "/Users/asifhussain/PROJECTS/CORTEX"
  scan_path: "." # Start from root
  exclude_patterns:
    - ".git/"
    - ".venv/"
    - "__pycache__/"
    - "*.pyc"
    - ".DS_Store"
  follow_symlinks: false
```

### Processing Logic

```python
def analyze():
  """
  Phase 1: Traverse file system
  Phase 2: Extract metadata
  Phase 3: Classify by tier
  Phase 4: Calculate metrics
  """
  
  files = []
  
  # Phase 1: Recursive traversal
  for root, dirs, filenames in os.walk(repo_root):
    # Exclude certain directories
    dirs[:] = [d for d in dirs if d not in excluded]
    
    for filename in filenames:
      filepath = os.path.join(root, filename)
      
      # Phase 2: Extract metadata
      metadata = {
        'path': filepath,
        'relative_path': os.path.relpath(filepath, repo_root),
        'name': filename,
        'extension': os.path.splitext(filename)[1],
        'size_bytes': os.path.getsize(filepath),
        'modified_time': os.path.getmtime(filepath),
        'created_time': os.path.getctime(filepath),
        'is_dir': os.path.isdir(filepath),
        'is_symlink': os.path.islink(filepath),
      }
      
      # Phase 3: Classify
      tier = classify_file(filepath, metadata)
      metadata['tier'] = tier
      metadata['age_days'] = calculate_age(metadata['modified_time'])
      
      # Phase 4: Flag for attention
      metadata['needs_review'] = should_review(metadata)
      
      files.append(metadata)
  
  return files
```

### Classification Algorithm

```python
def classify_file(filepath, metadata):
  """
  Returns: "TIER1"|"TIER2"|"TIER3"|"TIER4"|"UNCLASSIFIED"
  """
  
  # Check TIER 1 patterns (IMMUTABLE)
  if matches_keeper_pattern(filepath):
    return "TIER1"
  
  # Check critical system files
  if is_critical_file(filepath):
    return "TIER1"
  
  # Check TIER 2 patterns (DOCUMENTATION)
  if is_in_docs_folder(filepath) and is_curated_doc(filepath):
    return "TIER2"
  
  # Check TIER 3 patterns (EPHEMERAL)
  if matches_ephemeral_pattern(filepath):
    return "TIER3"
  
  # Check TIER 4 patterns (SPECIAL HANDLING)
  if is_special_case(filepath):
    return "TIER4"
  
  # Fallback
  return "UNCLASSIFIED"

def matches_keeper_pattern(filepath):
  """Check against TIER1 patterns from manifest"""
  patterns = [
    ".github/prompts/*.prompt.md",
    ".github/prompts/*-agents.md",
    "cortex*.yaml",
    "cortex_brain/tier*/**/*.yaml",
    "pyrightconfig.json",
  ]
  return any(fnmatch(filepath, p) for p in patterns)

def matches_ephemeral_pattern(filepath):
  """Check against TIER3 patterns from manifest"""
  ephemeral_keywords = [
    "SESSION-",
    "COMPLETION-",
    "DRY-RUN-",
    "-COMPLETION-",
    "-COMPLETE.md",
    "-REPORT.md",
    "-INDEX.md",
    "-SUMMARY.md",
  ]
  return any(kw in filepath for kw in ephemeral_keywords)
```

### Output

```yaml
output:
  format: "JSON"
  structure:
    metadata:
      scan_timestamp: "2026-01-24T10:30:00Z"
      repo_root: "/Users/asifhussain/PROJECTS/CORTEX"
      scan_duration_seconds: 12.5
    
    summary:
      total_files: 1247
      by_tier:
        TIER1: 123
        TIER2: 445
        TIER3: 634
        TIER4: 45
        UNCLASSIFIED: 0
      
      age_distribution:
        "< 7 days": 123
        "7-30 days": 234
        "30-90 days": 345
        "90-365 days": 456
        "> 365 days": 89
    
    files: [
      {
        path: "_workspaces/SESSION-SUMMARY-2026-01-24.md",
        relative_path: "_workspaces/SESSION-SUMMARY-2026-01-24.md",
        name: "SESSION-SUMMARY-2026-01-24.md",
        extension: ".md",
        size_bytes: 45678,
        modified_date: "2026-01-24T08:15:00Z",
        age_days: 0,
        tier: "TIER3",
        ephemeral_category: "session_reports",
        needs_review: false,
      },
      # ... more files
    ]
    
    anomalies: [
      {
        file: "weird-location/README.md",
        issue: "File in unexpected location",
        tier: "UNCLASSIFIED",
        action: "MANUAL_REVIEW",
      }
    ]
```

### Error Handling

```python
errors_that_stop_analysis = [
  "Permission denied accessing directory",
  "Symlink loop detected",
  "Disk read error",
]

errors_that_skip_file = [
  "Cannot read file metadata",
  "File locked by another process",
]

# Log all errors to audit trail
# Report errors to user with recovery options
```

---

## 📋 Agent 2: PolicyMatcher

### Identity
```yaml
name: "PolicyMatcher"
role: "Policy Recommendation Engine"
icon: "📋"
primary_goal: "Match files to policies and recommend actions"
depends_on: "FileAnalyzer"
```

### Input
```yaml
params:
  files_analysis: "Output from FileAnalyzer"
  manifest: "cortex-vacuum-manifest.yaml"
  today_date: "2026-01-24"
```

### Processing Logic

```python
def match_policies(files_analysis):
  """
  For each file, determine recommended action based on:
  1. File classification tier
  2. Age vs. policy threshold
  3. Category membership
  4. Safety considerations
  """
  
  policies = load_manifest()
  recommendations = []
  
  for file_metadata in files_analysis['files']:
    
    # Tier 1: Always keep
    if file_metadata['tier'] == "TIER1":
      rec = {
        'file': file_metadata['path'],
        'action': 'ALWAYS_KEEP',
        'reason': 'System file (TIER1)',
        'confidence': 1.0,
        'requires_approval': False,
      }
      recommendations.append(rec)
      continue
    
    # Tier 2: Evaluate for evolution
    if file_metadata['tier'] == "TIER2":
      rec = evaluate_tier2(file_metadata, policies)
      recommendations.append(rec)
      continue
    
    # Tier 3: Evaluate for archival
    if file_metadata['tier'] == "TIER3":
      rec = evaluate_tier3(file_metadata, policies)
      recommendations.append(rec)
      continue
    
    # Tier 4: Special handling
    if file_metadata['tier'] == "TIER4":
      rec = evaluate_tier4(file_metadata, policies)
      recommendations.append(rec)
      continue
    
    # Unclassified: Flag for review
    rec = {
      'file': file_metadata['path'],
      'action': 'MANUAL_REVIEW',
      'reason': 'File does not match known patterns',
      'confidence': 0.0,
      'requires_approval': True,
    }
    recommendations.append(rec)
  
  return group_recommendations_by_action(recommendations)

def evaluate_tier3(file_metadata, policies):
  """
  Tier 3: Ephemeral files
  Decision: ARCHIVE if older than max_age_days, else KEEP
  """
  
  category = find_ephemeral_category(file_metadata['path'])
  
  if not category:
    return {
      'file': file_metadata['path'],
      'action': 'MANUAL_REVIEW',
      'reason': 'Ephemeral file but category unknown',
      'confidence': 0.5,
      'requires_approval': True,
    }
  
  policy = policies['ephemeral_patterns'][category]
  max_age = policy['max_age_days']
  archive_to = policy['archive_to']
  
  if file_metadata['age_days'] > max_age:
    return {
      'file': file_metadata['path'],
      'action': 'ARCHIVE',
      'category': category,
      'reason': f"Older than {max_age} days",
      'destination': archive_to,
      'age_days': file_metadata['age_days'],
      'confidence': 0.95,
      'requires_approval': False,
    }
  else:
    return {
      'file': file_metadata['path'],
      'action': 'KEEP',
      'reason': f"Younger than {max_age} day threshold",
      'age_days': file_metadata['age_days'],
      'confidence': 0.95,
      'requires_approval': False,
    }

def evaluate_tier2(file_metadata, policies):
  """
  Tier 2: Curated documentation
  Decision: KEEP if within category limits, else ARCHIVE older versions
  """
  
  category = find_curated_doc_category(file_metadata['path'])
  
  if not category:
    return {
      'file': file_metadata['path'],
      'action': 'KEEP',
      'reason': 'Curated documentation (no age limit)',
      'confidence': 0.8,
      'requires_approval': False,
    }
  
  policy = policies['curated_docs'][category]
  max_age = policy.get('max_age_days', 365)
  keep_count = policy.get('keep_count', 1)
  
  # Count similar files in category
  similar_files = find_similar_files(file_metadata, category)
  similar_files_sorted = sort_by_date_desc(similar_files)
  
  # Check if this file is in keep_count most recent
  if similar_files_sorted.index(file_metadata) < keep_count:
    return {
      'file': file_metadata['path'],
      'action': 'KEEP',
      'reason': f"In top {keep_count} for category",
      'confidence': 0.95,
      'requires_approval': False,
    }
  
  # Check age
  if file_metadata['age_days'] > max_age:
    return {
      'file': file_metadata['path'],
      'action': 'ARCHIVE',
      'category': category,
      'reason': f"Older than {max_age} days and outside keep_count",
      'destination': "_workspaces/_archive/docs/",
      'age_days': file_metadata['age_days'],
      'confidence': 0.85,
      'requires_approval': False,
    }
  else:
    return {
      'file': file_metadata['path'],
      'action': 'KEEP',
      'reason': f"Within {max_age} day limit",
      'confidence': 0.95,
      'requires_approval': False,
    }
```

### Output

```yaml
output:
  format: "JSON"
  structure:
    recommendations_summary:
      ALWAYS_KEEP: 123
      KEEP: 456
      ARCHIVE: 28
      MIGRATE: 15
      DELETE: 0
      MANUAL_REVIEW: 3
    
    requires_approval_count: 3
    
    grouped_by_action:
      ALWAYS_KEEP:
        - file: ".github/prompts/CORTEX.prompt.md"
          reason: "System file (TIER1)"
      
      ARCHIVE:
        - file: "_workspaces/SESSION-SUMMARY-2026-01-20.md"
          reason: "Older than 30 days"
          category: "session_reports"
          destination: "_workspaces/_archive/sessions/"
          age_days: 4
        # ... more files
      
      MANUAL_REVIEW:
        - file: "strange-file.md"
          reason: "Does not match known patterns"
          confidence: 0.0
```

### Safety Checks

- ✅ No archival of files younger than threshold
- ✅ No deletion of unique files
- ✅ Confidence scores for all recommendations
- ✅ Flagging of edge cases

---

## 🛡️ Agent 3: SafetyValidator

### Identity
```yaml
name: "SafetyValidator"
role: "Safety & Risk Assessment"
icon: "🛡️"
primary_goal: "Validate proposed actions against safety thresholds"
depends_on: "PolicyMatcher"
```

### Input
```yaml
params:
  recommendations: "Output from PolicyMatcher"
  manifest: "cortex-vacuum-manifest.yaml"
  repo_state: "Current git state"
```

### Processing Logic

```python
def validate_safety(recommendations, manifest, repo_state):
  """
  Check all safety rules before allowing execution
  Returns: (is_safe: bool, violations: list, warnings: list)
  """
  
  violations = []  # Blocking issues
  warnings = []    # Non-blocking warnings
  
  # Rule 1: Category minimum threshold
  violations.extend(check_minimum_category_threshold(recommendations, manifest))
  
  # Rule 2: Backup capability
  violations.extend(check_backup_capability(recommendations))
  
  # Rule 3: Git state clean
  warnings.extend(check_git_state(repo_state))
  
  # Rule 4: Archive space available
  violations.extend(check_archive_space(recommendations))
  
  # Rule 5: Mixed operation check
  violations.extend(check_operation_mixing(recommendations))
  
  # Rule 6: Critical file protection
  violations.extend(check_critical_files(recommendations))
  
  # Rule 7: Duplicate/integrity checks
  warnings.extend(check_integrity(recommendations))
  
  is_safe = len(violations) == 0
  
  return {
    'is_safe': is_safe,
    'violations': violations,
    'warnings': warnings,
    'recommendation': 'PROCEED' if is_safe else 'ABORT_AND_FIX',
  }

def check_minimum_category_threshold(recommendations, manifest):
  """
  Ensure no category would be reduced below minimum_docs_per_category
  """
  violations = []
  min_threshold = manifest['safety_rules']['minimum_docs_per_category']
  
  categories = {}
  for rec in recommendations:
    if rec['action'] in ['ARCHIVE', 'DELETE', 'MIGRATE']:
      category = rec.get('category', 'unknown')
      categories[category] = categories.get(category, 0) + 1
  
  for category, removal_count in categories.items():
    # Count existing files in category
    existing_count = count_files_in_category(category)
    remaining = existing_count - removal_count
    
    if remaining < min_threshold:
      violations.append({
        'rule': 'minimum_category_threshold',
        'category': category,
        'existing_count': existing_count,
        'would_remove': removal_count,
        'remaining': remaining,
        'threshold': min_threshold,
        'severity': 'BLOCKING',
        'message': f"Would reduce {category} below threshold. Aborting.",
      })
  
  return violations

def check_backup_capability(recommendations):
  """
  Ensure backup storage exists and has space
  """
  violations = []
  backup_location = "_workspaces/_archive/.backup/"
  
  # Check directory exists
  if not os.path.exists(backup_location):
    violations.append({
      'rule': 'backup_capability',
      'issue': 'Backup directory does not exist',
      'location': backup_location,
      'severity': 'BLOCKING',
      'resolution': 'Create backup directory or specify alternative',
    })
  
  # Check space available
  delete_count = sum(1 for r in recommendations if r['action'] == 'DELETE')
  if delete_count > 0:
    needed_space = calculate_space_for_backups(recommendations)
    available_space = get_available_disk_space(backup_location)
    
    if needed_space > available_space:
      violations.append({
        'rule': 'backup_space',
        'issue': 'Insufficient space for backups',
        'needed_mb': needed_space / (1024*1024),
        'available_mb': available_space / (1024*1024),
        'severity': 'BLOCKING',
      })
  
  return violations

def check_git_state(repo_state):
  """
  Warn if git working directory is not clean
  """
  warnings = []
  
  if repo_state['has_uncommitted_changes']:
    warnings.append({
      'rule': 'git_state',
      'issue': 'Uncommitted changes in working directory',
      'severity': 'WARNING',
      'recommendation': 'Commit or stash changes before vacuum',
    })
  
  if repo_state['current_branch'].startswith('detached'):
    warnings.append({
      'rule': 'git_state',
      'issue': 'Repository in detached HEAD state',
      'severity': 'WARNING',
      'recommendation': 'Checkout a branch before vacuum',
    })
  
  return warnings

def check_critical_files(recommendations):
  """
  Extra protection for system files
  """
  violations = []
  critical_patterns = [
    ".github/prompts/",
    "cortex_brain/tier0/",
    "cortex*.yaml",
  ]
  
  for rec in recommendations:
    if rec['action'] in ['DELETE', 'ARCHIVE']:
      if any(fnmatch(rec['file'], p) for p in critical_patterns):
        violations.append({
          'rule': 'critical_file_protection',
          'file': rec['file'],
          'issue': 'Attempt to remove critical system file',
          'severity': 'BLOCKING',
          'message': 'Critical system files cannot be removed via vacuum',
        })
  
  return violations
```

### Output

```yaml
output:
  format: "JSON"
  structure:
    is_safe: true
    recommendation: "PROCEED"
    
    violations: []  # Blocking issues
    
    warnings:
      - rule: "git_state"
        issue: "Uncommitted changes in working directory"
        severity: "WARNING"
        recommendation: "Commit changes before executing"
    
    checks_performed:
      - "minimum_category_threshold"
      - "backup_capability"
      - "git_state"
      - "archive_space"
      - "operation_mixing"
      - "critical_files"
      - "integrity"
    
    checks_passed: 7
    checks_failed: 0
    checks_warned: 1
```

---

## ⚡ Agent 4: OperationExecutor

### Identity
```yaml
name: "OperationExecutor"
role: "Execute Approved Vacuum Operations"
icon: "⚡"
primary_goal: "Safely execute vacuum operations with atomic transactions"
depends_on: "SafetyValidator"
```

### Input
```yaml
params:
  validated_recommendations: "Output from SafetyValidator"
  user_approval: "Explicit user confirmation"
  dry_run_mode: "boolean - if true, simulate only"
```

### Processing Logic

```python
def execute_operations(recommendations, user_approval, dry_run=False):
  """
  Execute approved recommendations with full audit trail
  """
  
  if not user_approval:
    raise OperationAborted("User approval required")
  
  operation_id = generate_operation_id()
  start_time = datetime.now(timezone.utc)
  
  # Phase 0: Checkpoint
  log_ac_start(operation_id, recommendations)
  git_checkpoint(f"vacuum: pre-cleanup checkpoint")
  
  if dry_run:
    return simulate_operations(recommendations, operation_id)
  
  # Phase 1: Backup critical files
  backup_manifest = backup_files_to_remove(recommendations)
  
  # Phase 2: Execute operations in safe order
  operation_log = []
  
  for rec in sorted(recommendations, key=lambda r: r['action']):
    
    try:
      log_ac_execute(operation_id, 'START', rec)
      
      if rec['action'] == 'ARCHIVE':
        result = execute_archive(rec)
      
      elif rec['action'] == 'MIGRATE':
        result = execute_migrate(rec)
      
      elif rec['action'] == 'DELETE':
        result = execute_delete(rec, backup_manifest)
      
      else:
        result = {'status': 'SKIPPED', 'reason': 'No action needed'}
      
      operation_log.append({
        'file': rec['file'],
        'action': rec['action'],
        'result': result,
        'timestamp': datetime.now(timezone.utc).isoformat(),
      })
      
      log_ac_execute(operation_id, 'COMPLETE', rec, result)
      
    except Exception as e:
      operation_log.append({
        'file': rec['file'],
        'action': rec['action'],
        'error': str(e),
        'timestamp': datetime.now(timezone.utc).isoformat(),
      })
      # Log error but continue
      log_error(operation_id, rec, e)
  
  # Phase 3: Git commit
  git_commit(f"vacuum: cleanup operations ({len(recommendations)} files)")
  
  # Phase 4: Finalization
  duration = (datetime.now(timezone.utc) - start_time).total_seconds()
  
  results = {
    'operation_id': operation_id,
    'status': 'COMPLETED',
    'duration_seconds': duration,
    'files_processed': len(recommendations),
    'operations': operation_log,
    'backup_manifest': backup_manifest,
  }
  
  log_ac_complete(operation_id, results)
  
  return results

def execute_archive(rec):
  """
  Move file to archive location
  """
  source = rec['file']
  destination = rec['destination']
  
  # Ensure destination exists
  os.makedirs(destination, exist_ok=True)
  
  # Move file
  target_path = os.path.join(destination, os.path.basename(source))
  shutil.move(source, target_path)
  
  return {
    'status': 'SUCCESS',
    'source': source,
    'destination': target_path,
  }

def execute_migrate(rec):
  """
  Copy to new location and archive original
  """
  source = rec['file']
  destination = rec['destination']
  
  # Copy to destination
  os.makedirs(destination, exist_ok=True)
  target_path = os.path.join(destination, os.path.basename(source))
  shutil.copy2(source, target_path)
  
  # Archive original
  archive_path = execute_archive({
    'file': source,
    'destination': '_workspaces/_archive/migrated/',
  })
  
  return {
    'status': 'SUCCESS',
    'source': source,
    'copied_to': target_path,
    'archived_original': archive_path,
  }

def execute_delete(rec, backup_manifest):
  """
  Delete file (after backup created)
  """
  file_path = rec['file']
  
  if file_path not in backup_manifest:
    raise ValueError(f"File not in backup manifest: {file_path}")
  
  os.remove(file_path)
  
  return {
    'status': 'SUCCESS',
    'file': file_path,
    'backup_location': backup_manifest[file_path],
  }
```

### Output

```yaml
output:
  format: "JSON"
  structure:
    operation_id: "vacuum-20260124-001"
    status: "COMPLETED"
    duration_seconds: 125.5
    
    summary:
      files_processed: 28
      successful: 28
      failed: 0
      skipped: 0
    
    by_action:
      ARCHIVE: 23
      MIGRATE: 3
      DELETE: 2
    
    space_reclaimed_mb: 12.5
    
    operations: [
      {
        file: "_workspaces/SESSION-SUMMARY-2026-01-20.md",
        action: "ARCHIVE",
        result:
          status: "SUCCESS"
          destination: "_workspaces/_archive/sessions/SESSION-SUMMARY-2026-01-20.md"
        timestamp: "2026-01-24T10:35:12Z"
      },
      # ... more operations
    ]
    
    git_commits:
      - "vacuum: pre-cleanup checkpoint"
      - "vacuum: cleanup operations (28 files)"
    
    backup_manifest:
      "_workspaces/old-file.md": "_workspaces/_archive/.backup/old-file.md.bak"
      # ... more files
```

---

## 📝 Agent 5: AuditLogger

### Identity
```yaml
name: "AuditLogger"
role: "Operation Auditing & Reporting"
icon: "📝"
primary_goal: "Maintain complete audit trail and enable rollback"
depends_on: "OperationExecutor"
```

### Input
```yaml
params:
  operation_results: "Output from OperationExecutor"
  analysis_results: "Output from FileAnalyzer"
  git_log: "Git commit history"
```

### Processing Logic

```python
def generate_audit_trail(operation_results, analysis_results):
  """
  Create comprehensive audit trail for traceability and rollback
  """
  
  log_entry = {
    'timestamp': datetime.now(timezone.utc).isoformat(),
    'operation_id': operation_results['operation_id'],
    'phase': 'AC_COMPLETE',
    'status': operation_results['status'],
    
    'pre_operation_state': {
      'total_files': analysis_results['summary']['total_files'],
      'by_tier': analysis_results['summary']['by_tier'],
    },
    
    'operation_details': {
      'duration_seconds': operation_results['duration_seconds'],
      'files_processed': operation_results['files_processed'],
      'breakdown': operation_results['by_action'],
      'space_reclaimed_mb': operation_results['space_reclaimed_mb'],
    },
    
    'git_state': {
      'commits': operation_results['git_commits'],
      'branch': get_current_branch(),
      'head_commit': get_head_commit(),
    },
    
    'rollback_info': {
      'backup_manifest': operation_results['backup_manifest'],
      'restore_command': f"cortex-vacuum --rollback {operation_results['operation_id']}",
    },
  }
  
  # Append to log file
  log_file = "_workspaces/.vacuum-operations.log"
  with open(log_file, 'a') as f:
    f.write(json.dumps(log_entry, indent=2) + "\n")
  
  # Create rollback manifest
  create_rollback_manifest(operation_results['operation_id'], log_entry)
  
  return log_entry

def create_rollback_manifest(operation_id, log_entry):
  """
  Create manifest for potential rollback
  """
  manifest = {
    'operation_id': operation_id,
    'timestamp': log_entry['timestamp'],
    'backup_manifest': log_entry['rollback_info']['backup_manifest'],
    'git_commits': log_entry['git_state']['commits'],
    'instructions': [
      "1. Run: git revert {commits}",
      "2. Restore files from: _workspaces/_archive/.backup/",
      "3. Verify: git status",
    ],
  }
  
  manifest_file = f"_workspaces/_archive/.rollback-manifests/{operation_id}.json"
  os.makedirs(os.path.dirname(manifest_file), exist_ok=True)
  
  with open(manifest_file, 'w') as f:
    json.dump(manifest, f, indent=2)

def generate_reports(operation_results):
  """
  Generate human-readable reports
  """
  
  report = f"""
CORTEX Vacuum Operation Report
==============================

Operation ID: {operation_results['operation_id']}
Status: {operation_results['status']}
Duration: {operation_results['duration_seconds']} seconds

Summary:
--------
Files Processed: {operation_results['files_processed']}
Successful: {operation_results['by_action']['ARCHIVE']} archived, ...
Space Reclaimed: {operation_results['space_reclaimed_mb']} MB

Breakdown by Action:
--------------------
Archive: {operation_results['by_action'].get('ARCHIVE', 0)} files
Migrate: {operation_results['by_action'].get('MIGRATE', 0)} files
Delete: {operation_results['by_action'].get('DELETE', 0)} files

Git Commits Created:
-------------------
{chr(10).join(f'- {c}' for c in operation_results['git_commits'])}

To Rollback:
-----------
1. Restore backups: cortex-vacuum --rollback {operation_results['operation_id']}
2. Review changes: git log --oneline -5
3. Reset if needed: git revert {operation_results['git_commits'][-1]}

Audit Trail:
-----------
All operations logged to: _workspaces/.vacuum-operations.log
Rollback manifest: _workspaces/_archive/.rollback-manifests/{operation_results['operation_id']}.json
"""
  
  return report
```

### Output

```yaml
output:
  format: "JSON"
  structure:
    audit_log_entry:
      timestamp: "2026-01-24T10:37:30Z"
      operation_id: "vacuum-20260124-001"
      phase: "AC_COMPLETE"
      status: "COMPLETED"
      
      pre_operation_state:
        total_files: 1247
        by_tier:
          TIER1: 123
          TIER2: 445
          TIER3: 634
          TIER4: 45
      
      operation_details:
        duration_seconds: 125.5
        files_processed: 28
        breakdown:
          ARCHIVE: 23
          MIGRATE: 3
          DELETE: 2
        space_reclaimed_mb: 12.5
      
      git_state:
        commits:
          - "vacuum: pre-cleanup checkpoint"
          - "vacuum: cleanup operations (28 files)"
        branch: "vacuum/repo-sanitization-20260124"
        head_commit: "abc123def..."
      
      rollback_info:
        backup_manifest: {...}
        restore_command: "cortex-vacuum --rollback vacuum-20260124-001"
    
    report_file: "_workspaces/reports/vacuum-20260124-001.md"
    
    metrics:
      files_archived: 23
      files_migrated: 3
      files_deleted: 2
      space_freed_mb: 12.5
      duration_seconds: 125.5
```

---

## 🔄 Agent Communication Protocol

```
FileAnalyzer
  ↓ (JSON output)
  ├─ Sends: files[], summary, anomalies
  └─ To: PolicyMatcher (file paths + metadata)

PolicyMatcher
  ↓ (JSON output)
  ├─ Sends: recommendations[], grouped_by_action
  └─ To: SafetyValidator (file paths + proposed actions)

SafetyValidator
  ↓ (JSON output)
  ├─ Sends: is_safe, violations[], warnings[]
  └─ To: User (for approval) + OperationExecutor (if approved)

OperationExecutor
  ↓ (JSON output)
  ├─ Sends: operation_results, backup_manifest, git_commits
  └─ To: AuditLogger (for recording)

AuditLogger
  ↓ (Log file + reports)
  ├─ Writes: _workspaces/.vacuum-operations.log
  ├─ Creates: _workspaces/reports/vacuum-{date}.md
  └─ Maintains: rollback manifests
```

---

## 🧪 Agent Testing Strategy

Each agent can be tested independently:

```python
# Test FileAnalyzer
test_files_analysis = analyze_test_repo()
assert len(test_files_analysis['files']) > 0
assert test_files_analysis['summary']['total_files'] == expected_count

# Test PolicyMatcher
test_recommendations = match_policies(test_files_analysis)
assert len(test_recommendations['ARCHIVE']) > 0
assert test_recommendations['ALWAYS_KEEP'][0]['requires_approval'] == False

# Test SafetyValidator
validation = validate_safety(test_recommendations, manifest)
assert validation['is_safe'] == True

# Test OperationExecutor (dry-run)
results = execute_operations(test_recommendations, True, dry_run=True)
assert results['status'] == 'COMPLETED'
assert len(results['operations']) == len(test_recommendations)

# Test AuditLogger
audit_entry = generate_audit_trail(results, test_files_analysis)
assert audit_entry['operation_id'] is not None
```

---

## 📌 Integration Checklist

- ✅ FileAnalyzer can scan full CORTEX repo
- ✅ PolicyMatcher loads manifest correctly
- ✅ SafetyValidator enforces all rules
- ✅ OperationExecutor creates git commits
- ✅ AuditLogger writes to log file
- ✅ All agents handle errors gracefully
- ✅ Dry-run mode works end-to-end
- ✅ Rollback capability tested

