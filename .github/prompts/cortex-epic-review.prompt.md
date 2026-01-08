# CORTEX Epic Review - Health & Progress Analysis

**Purpose:** Autonomous health check and progress analysis for CORTEX 6.0 Build Epic  
**Output:** Executive summary with ASCII progress bars, no code snippets  
**Workflow:** Analyze → Report → Identify Issues → Update Epic  

---

## 🎯 Invocation Patterns

```regex
^(epic review|review epic|health check|progress report|cortex status|epic status)$
```

**User says:**
- "epic review"
- "health check"
- "progress report"
- "cortex status"

**Agent does:**
1. Generate executive summary with visual progress bars
2. Analyze audit logs for health metrics
3. Evaluate self-healing capabilities
4. Assess governance compliance
5. Identify gaps and recommend new tasks/feats
6. Update epic files if issues found

---

## 📊 Output Format

### Executive Summary Template

```
🏥 CORTEX 6.0 EPIC HEALTH REPORT
Generated: {timestamp}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📊 OVERALL PROGRESS: {percentage}% ({completed}/{total} tasks)

████████████████████░░░░░░░░ {percentage}%

Health Score: {score}/100 | Status: {status_icon} {status_text}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 FEATURE COMPLETION STATUS

✅ feat01-foundation      ████████████████████ 100% (18/19 tasks)
✅ feat02-todo            ████████████████████ 100% (21/21 tasks)
✅ feat03-governance      ████████████████████ 100% (Operational)
✅ feat04-orchestration   ████████████████████ 100% (Complete)
✅ feat05-resilience      ████████████████████ 100% (3/3 tasks)
⚪ feat06-mcp             ░░░░░░░░░░░░░░░░░░░░   0% (Not started)
⚪ feat07-integration     ░░░░░░░░░░░░░░░░░░░░   0% (Not started)
⚪ feat08-cleanup         ░░░░░░░░░░░░░░░░░░░░   0% (Not started)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🧪 TEST SUITE HEALTH

Tests Collected:  574
Tests Passing:    564 ████████████████████▓░ 98.3%
Tests Skipped:     10 ▓░░░░░░░░░░░░░░░░░░░░  1.7%
Tests Failed:       0 ░░░░░░░░░░░░░░░░░░░░░  0.0%

Execution Time: 9.74s | Regressions: 0 | Status: 🟢 HEALTHY

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 AUDIT LOG ANALYSIS (Last 24h)

Total Entries:     877
Correlation IDs:   263
Active Components:   9

Log Levels:
  INFO     748 █████████████████░░░ 85.3%
  WARNING  122 ███░░░░░░░░░░░░░░░░░ 13.9%
  ERROR      7 ░░░░░░░░░░░░░░░░░░░░  0.8%
  CRITICAL   0 ░░░░░░░░░░░░░░░░░░░░  0.0%

Error Analysis: ✅ All 7 errors from test scenarios (no production issues)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 ACTIVE FEATURE USAGE (Evidence-Based)

🔥 GovernanceMerger       ████████████████░░░░ 226 entries (HIGHLY ACTIVE)
🔥 TodoOrchestrator       ██████████████░░░░░░ 133 entries (ACTIVE)
🔥 RateLimiter           █████████████░░░░░░░ 123 entries (ACTIVE) ✨NEW
🔥 CircuitBreaker        ██████░░░░░░░░░░░░░░  64 entries (ACTIVE) ✨NEW
🔥 MasterOrchestrator    █████░░░░░░░░░░░░░░░  63 entries (ACTIVE)
🔥 ResourceLimiter       ███░░░░░░░░░░░░░░░░░  39 entries (ACTIVE) ✨NEW

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🛡️ SELF-HEALING CAPABILITIES

Audit Review:        ✅ OPERATIONAL (Pre-task error checks)
Validation Checks:   ✅ OPERATIONAL (Exit criteria enforcement)
Test Alignment:      ✅ OPERATIONAL (TDD enforcement)
Error Remediation:   ✅ OPERATIONAL (Immediate fixes)
Checkpoint System:   🟡 PARTIAL (Git-based, task 1.2.5 pending)

Self-Healing Score: 90/100 | Status: 🟢 STRONG

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🏛️ GOVERNANCE COMPLIANCE

SKULL Rules:         ✅ 61 rules active (Tier 0)
4-Tier System:       ✅ OPERATIONAL (Tier 0-3)
Merge Performance:   ✅ <50ms (target met)
Cache Hit Rate:      ✅ >80% (target met)
Violation Tracking:  ✅ ACTIVE (auto-conversion to TODOs)

YAML-First:          ✅ ENFORCED (16/16 tests passing)
TDD Enforcement:     ✅ ACTIVE (All new features)
Git Isolation:       ✅ PROTECTED (CORTEX code isolated)

Governance Score: 98/100 | Status: 🟢 EXCELLENT

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔍 IDENTIFIED GAPS & RECOMMENDATIONS

{gaps_section}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 NEXT ACTIONS

{next_actions}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 EPIC UPDATES MADE

{epic_updates}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🔍 Analysis Workflow

### Step 1: Load Context
```yaml
files_to_analyze:
  - .asif/AI-Learning/cortex6/source-of-truth/todo/00-TODO-CONTINUITY-TRACKER.yaml
  - .asif/AI-Learning/cortex6/source-of-truth/epic/00-CORTEX6-BUILD-EPIC.yaml
  - cortex-brain/audit-logs/*.jsonl (last 24h)
  - cortex-brain/tier0/governance/core-rules.yaml
  - cortex-brain/brain-protection-rules.yaml
  - pytest test collection results
  - pytest test execution results
```

### Step 2: Calculate Metrics
```python
metrics = {
    'overall_progress': completed_tasks / total_tasks * 100,
    'test_health': passing_tests / total_tests * 100,
    'audit_health': (total_logs - errors) / total_logs * 100,
    'governance_compliance': passed_rules / total_rules * 100,
    'self_healing_score': calculate_self_healing_score(),
    'health_score': weighted_average([...])
}
```

### Step 3: Analyze Component Usage
```python
audit_analysis = {
    'by_component': count_logs_by_component(last_24h),
    'by_category': count_logs_by_category(last_24h),
    'by_level': count_logs_by_level(last_24h),
    'errors': extract_errors(last_24h),
    'correlation_ids': extract_unique_correlations(last_24h)
}

# Mark as ACTIVE if logs > 10 in last 24h
# Mark as HIGHLY ACTIVE if logs > 100 in last 24h
# Mark as INACTIVE if logs == 0 in last 24h
```

### Step 4: Evaluate Self-Healing
```yaml
self_healing_checks:
  audit_review:
    check: "Does pre-task audit review happen?"
    evidence: "Search for correlation IDs in audit logs"
    score: 20/20 if yes, 0/20 if no
  
  validation_checks:
    check: "Are exit criteria validated before COMPLETED?"
    evidence: "Check tracker for validation.result fields"
    score: 20/20 if yes, 0/20 if no
  
  test_alignment:
    check: "Do test counts match expectations?"
    evidence: "Compare tracker expected vs actual tests"
    score: 20/20 if yes, 0/20 if no
  
  error_remediation:
    check: "Are errors fixed immediately?"
    evidence: "Check for ERROR → fix → COMPLETED patterns"
    score: 20/20 if yes, 10/20 if delayed, 0/20 if ignored
  
  checkpoint_system:
    check: "Are checkpoints created every 5 tasks?"
    evidence: "Check git commits or tracker checkpoints"
    score: 20/20 if automated, 10/20 if manual, 0/20 if missing
```

### Step 5: Evaluate Governance
```yaml
governance_checks:
  skull_rules:
    check: "Are SKULL rules active and enforced?"
    evidence: "cortex-brain/tier0/governance/core-rules.yaml exists and loaded"
    score: 15/15 if yes
  
  yaml_first:
    check: "Is YAML-first enforced?"
    evidence: "tests/unit/test_yaml_first_enforcement.py passing"
    score: 15/15 if yes
  
  tdd_enforcement:
    check: "Is TDD followed for tdd_required tasks?"
    evidence: "Check tracker for RED→GREEN→REFACTOR notes"
    score: 15/15 if yes
  
  git_isolation:
    check: "Is CORTEX code isolated from user repos?"
    evidence: "Check .gitignore and brain-protection-rules.yaml"
    score: 15/15 if yes
  
  merge_performance:
    check: "Is governance merge <50ms?"
    evidence: "Check audit logs for merge operation times"
    score: 20/20 if <50ms, 10/20 if <100ms, 0/20 if >100ms
  
  violation_tracking:
    check: "Are violations converted to TODOs?"
    evidence: "Check GovernanceMerger audit logs"
    score: 20/20 if yes
```

### Step 6: Identify Gaps
```python
gaps = []

# Check for missing features
if feature.status == 'NOT_STARTED' and feature.estimated_days > 7:
    gaps.append({
        'type': 'MISSING_FEATURE',
        'severity': 'HIGH',
        'feature': feature.id,
        'recommendation': 'Start implementation'
    })

# Check for incomplete phases
if phase.progress < 100 and phase.status == 'IN_PROGRESS':
    gaps.append({
        'type': 'INCOMPLETE_PHASE',
        'severity': 'MEDIUM',
        'phase': phase.id,
        'recommendation': 'Complete remaining tasks'
    })

# Check for test coverage gaps
if test_coverage < 80:
    gaps.append({
        'type': 'LOW_TEST_COVERAGE',
        'severity': 'HIGH',
        'coverage': test_coverage,
        'recommendation': 'Add tests to reach 80% minimum'
    })

# Check for error patterns
if error_count > 10 and not all_are_test_errors:
    gaps.append({
        'type': 'ERROR_PATTERN',
        'severity': 'CRITICAL',
        'error_count': error_count,
        'recommendation': 'Investigate and fix production errors'
    })

# Check for inactive critical components
critical_components = ['StateManager', 'AuditLogger', 'GovernanceMerger', 'TodoOrchestrator']
for component in critical_components:
    if component_log_count[component] == 0:
        gaps.append({
            'type': 'INACTIVE_COMPONENT',
            'severity': 'HIGH',
            'component': component,
            'recommendation': 'Verify component integration or remove if obsolete'
        })

# Check for missing documentation
if feature.status == 'COMPLETED' and not documentation_exists:
    gaps.append({
        'type': 'MISSING_DOCUMENTATION',
        'severity': 'LOW',
        'feature': feature.id,
        'recommendation': 'Add architecture/usage documentation'
    })

# Check for security gaps
if 'security' not in features and 'authentication' not in features:
    gaps.append({
        'type': 'SECURITY_GAP',
        'severity': 'HIGH',
        'recommendation': 'Add feat09-security for auth, encryption, input validation'
    })

# Check for performance gaps
if no_performance_benchmarks and production_ready:
    gaps.append({
        'type': 'PERFORMANCE_GAP',
        'severity': 'MEDIUM',
        'recommendation': 'Add performance benchmarking to feat05 or feat07'
    })

# Check for accessibility gaps
if no_accessibility_features and user_facing:
    gaps.append({
        'type': 'ACCESSIBILITY_GAP',
        'severity': 'MEDIUM',
        'recommendation': 'Add WCAG 2.1 AA compliance checks'
    })

# Check for monitoring/observability gaps
if no_metrics_dashboard and production_ready:
    gaps.append({
        'type': 'OBSERVABILITY_GAP',
        'severity': 'MEDIUM',
        'recommendation': 'Add metrics dashboard or monitoring integration'
    })

# Check for disaster recovery gaps
if no_backup_strategy and stateful_system:
    gaps.append({
        'type': 'DISASTER_RECOVERY_GAP',
        'severity': 'HIGH',
        'recommendation': 'Add backup/restore capabilities to feat05 or new feat'
    })
```

### Step 7: Generate Recommendations
```python
recommendations = []

for gap in sorted_gaps_by_severity:
    if gap.severity == 'CRITICAL':
        recommendations.append({
            'action': 'IMMEDIATE',
            'description': gap.recommendation,
            'target': 'Current session',
            'epic_update': create_new_task(gap)
        })
    elif gap.severity == 'HIGH':
        recommendations.append({
            'action': 'PRIORITY',
            'description': gap.recommendation,
            'target': 'Next feature or phase',
            'epic_update': create_new_task(gap)
        })
    elif gap.severity == 'MEDIUM':
        recommendations.append({
            'action': 'PLANNED',
            'description': gap.recommendation,
            'target': 'Before release',
            'epic_update': create_new_phase_or_task(gap)
        })
    else:  # LOW
        recommendations.append({
            'action': 'BACKLOG',
            'description': gap.recommendation,
            'target': 'Post-release',
            'epic_update': add_to_backlog(gap)
        })
```

### Step 8: Update Epic Files
```python
if gaps_found:
    # Update epic YAML
    update_file('.asif/AI-Learning/cortex6/source-of-truth/epic/00-CORTEX6-BUILD-EPIC.yaml', {
        'new_tasks': [...],
        'new_phases': [...],
        'new_features': [...]
    })
    
    # Update tracker
    update_file('.asif/AI-Learning/cortex6/source-of-truth/todo/00-TODO-CONTINUITY-TRACKER.yaml', {
        'new_tasks': [...],
        'updated_estimates': [...]
    })
    
    # Update continuation prompt
    run_command('python3 .asif/AI-Learning/cortex6/source-of-truth/update_continuation_prompt.py')
    
    # Update feature YAML files
    for feature in affected_features:
        update_file(f'features/{feature.id}/feature.yaml', {...})
```

---

## 🎯 Gap Detection Rules

### Critical Gaps (Immediate Action Required)
```yaml
critical_patterns:
  - production_errors: ERROR logs not from test scenarios
  - security_vulnerabilities: Unencrypted secrets, SQL injection risks
  - data_loss_risks: No backup strategy for stateful systems
  - broken_critical_path: Core orchestrator not working
  - zero_test_coverage: Features with no tests
```

### High Priority Gaps (Next Feature/Phase)
```yaml
high_priority_patterns:
  - missing_auth: No authentication/authorization
  - low_test_coverage: <80% coverage
  - inactive_critical_component: Core component not logging
  - incomplete_self_healing: Missing audit review or validation
  - missing_monitoring: No metrics or health checks
  - missing_documentation: Completed features undocumented
```

### Medium Priority Gaps (Before Release)
```yaml
medium_priority_patterns:
  - performance_unknowns: No benchmarking or SLA definition
  - accessibility_gaps: No WCAG compliance
  - missing_rollback: No disaster recovery plan
  - incomplete_integration: Features not fully integrated
  - missing_edge_cases: No negative testing
```

### Low Priority Gaps (Post-Release)
```yaml
low_priority_patterns:
  - nice_to_have_features: Advanced UI, analytics
  - optimization_opportunities: Code refactoring, caching improvements
  - missing_examples: Usage examples, tutorials
  - minor_documentation: API docs, inline comments
```

---

## 📋 Epic Update Template

When gaps are found, add to epic using this template:

```yaml
# New Task Template
- id: task-{feature}-{phase}-{number}
  name: "{Gap Description}"
  description: "{Detailed description}"
  estimated_hours: {estimate}
  priority: {CRITICAL|HIGH|MEDIUM|LOW}
  dependencies:
    - {existing_task_id}
  tdd_required: true
  audit_requirements:
    category: {category}
    correlation_id_prefix: {prefix}
  exit_criteria:
    - "{Verification method}"
  gap_origin:
    detected_by: epic_review
    detected_at: "{timestamp}"
    severity: "{severity}"
    recommendation: "{recommendation}"

# New Phase Template (if multiple related tasks)
- phase_id: {number}
  name: "{Phase Name}"
  status: NOT_STARTED
  estimated_hours: {sum_of_tasks}
  dependencies:
    - phase-{previous}
  tasks: [...]
  gap_origin:
    detected_by: epic_review
    detected_at: "{timestamp}"
    severity: "{severity}"

# New Feature Template (if major gap like security)
feat{XX}_{name}:
  feature_id: feat{XX}-{name}
  feature_name: "{Feature Name}"
  status: NOT_STARTED
  estimated_days: {estimate}
  dependencies:
    - feat{previous}
  phases: [...]
  gap_origin:
    detected_by: epic_review
    detected_at: "{timestamp}"
    severity: "{severity}"
    justification: "{Why this is needed}"
```

---

## 🔧 Execution Instructions

When user invokes this prompt:

1. **Collect Data** (Silent - no output)
   - Load tracker YAML
   - Load epic YAML
   - Parse audit logs (last 24h)
   - Run pytest --collect-only
   - Run pytest (full suite)
   - Check component files

2. **Calculate Metrics** (Silent)
   - Overall progress percentage
   - Feature completion breakdown
   - Test health metrics
   - Audit log analysis
   - Self-healing score
   - Governance compliance score
   - Component usage stats
   - Health score (weighted)

3. **Identify Gaps** (Silent)
   - Run all gap detection rules
   - Categorize by severity
   - Generate recommendations
   - Prepare epic updates

4. **Generate Report** (Output to user)
   - Use executive summary template
   - ASCII progress bars for visual appeal
   - Color-coded status icons
   - No code snippets (only metrics and prose)
   - Concise format (≤50 lines visible at once)

5. **Update Epic** (Silent if no gaps, notify if updates made)
   - Add new tasks/phases/features to epic YAML
   - Update tracker with new items
   - Run update_continuation_prompt.py
   - Create git commit with changes

6. **Present Next Steps** (Output)
   - IMMEDIATE actions (if critical gaps)
   - PRIORITY actions (if high gaps)
   - PLANNED actions (if medium gaps)
   - BACKLOG items (if low gaps)
   - OR "No gaps found - ready to proceed" message

---

## 🎨 Visual Elements

### Progress Bar Generator
```python
def generate_progress_bar(percentage, width=20):
    filled = int(width * percentage / 100)
    empty = width - filled
    return '█' * filled + '░' * empty

# Example outputs:
# 100%: ████████████████████
#  75%: ███████████████░░░░░
#  50%: ██████████░░░░░░░░░░
#  25%: █████░░░░░░░░░░░░░░░
#   0%: ░░░░░░░░░░░░░░░░░░░░
```

### Status Icons
```python
status_icons = {
    'EXCELLENT': '🟢',
    'GOOD': '🟢',
    'HEALTHY': '🟢',
    'WARNING': '🟡',
    'PARTIAL': '🟡',
    'ERROR': '🔴',
    'CRITICAL': '🔴',
    'COMPLETED': '✅',
    'IN_PROGRESS': '🔄',
    'NOT_STARTED': '⚪',
    'BLOCKED': '🚫',
    'NEW': '✨',
    'HIGHLY_ACTIVE': '🔥',
    'ACTIVE': '🔥',
    'INACTIVE': '💤'
}
```

### Severity Icons
```python
severity_icons = {
    'CRITICAL': '🚨',
    'HIGH': '⚠️',
    'MEDIUM': '⚡',
    'LOW': 'ℹ️'
}
```

---

## 🔄 Continuous Improvement

This prompt should evolve based on:
1. **New gap patterns discovered** → Add to gap detection rules
2. **User feedback** → Adjust output format or detail level
3. **Epic evolution** → Update analysis rules for new features
4. **Performance issues** → Optimize data collection

Update this prompt when:
- New critical components added to system
- New governance rules added to Tier 0
- New self-healing capabilities implemented
- Epic structure changes significantly

---

## 📚 References

| Reference | Path |
|-----------|------|
| Tracker | `.asif/AI-Learning/cortex6/source-of-truth/todo/00-TODO-CONTINUITY-TRACKER.yaml` |
| Epic | `.asif/AI-Learning/cortex6/source-of-truth/epic/00-CORTEX6-BUILD-EPIC.yaml` |
| Features | `.asif/AI-Learning/cortex6/source-of-truth/features/` |
| Audit Logs | `cortex-brain/audit-logs/` |
| SKULL Rules | `cortex-brain/tier0/governance/core-rules.yaml` |
| Brain Protection | `cortex-brain/brain-protection-rules.yaml` |
| Response Templates | `cortex-brain/response-templates-v4.yaml` |

---

## ✅ Success Criteria

Epic review is successful when:
- ✅ Executive summary generated in <10 seconds
- ✅ All metrics calculated accurately
- ✅ Gaps identified with clear severity
- ✅ Epic files updated automatically if gaps found
- ✅ User sees visual progress bars and icons
- ✅ No code snippets in output (prose and metrics only)
- ✅ Health score calculated with clear methodology
- ✅ Next actions clearly prioritized
- ✅ Self-healing and governance assessed objectively

---

**Version:** 1.0.0  
**Last Updated:** 2026-01-08  
**Maintained By:** CORTEX Core Team
