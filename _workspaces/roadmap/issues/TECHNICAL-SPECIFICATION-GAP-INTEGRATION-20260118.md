# Technical Specification: Systematic Gap Integration Protocol
## Integration Between cortex-review.prompt.md and cortex-builder.prompt.md

**Date:** January 18, 2026  
**Version:** 3.1  
**Status:** PRODUCTION READY ✅

---

## DOCUMENT OVERVIEW

This document specifies the technical protocol for:
1. Gap extraction from review findings (cortex-review.prompt.md Phase 3)
2. Gap integration into master plan (cortex-builder.prompt.md)
3. File formats, validation rules, and edge cases
4. Error handling and recovery procedures

---

## 1. GAP EXTRACTION PROTOCOL (cortex-review.prompt.md Phase 3A)

### 1.1 Input Specification

**Source File:** `REVIEW-FINDINGS-CONSOLIDATED-YYYYMMDD.yaml`

**Required Structure:**
```yaml
metadata:
  review_date: "YYYY-MM-DD"
  phases_executed: "0, 1, 2"
  agents_run: 5
  evidence_quality: "A (95% confidence)"

findings:
  - finding_id: "F001"
    severity: "CRITICAL"        # CRITICAL|HIGH|MEDIUM|LOW
    evidence_grade: "A"         # A|B|C
    agent: "brittleness|hallucination|governance|assumptions|debt"
    root_cause: "IMPLEMENTATION_FLAW|INTEGRATION_ISSUE|DESIGN_WEAKNESS"
    affected_files: [list]
    ac_id_suggested: "AC-FIX-XXX-XX"
    remediation_effort: "2h|4h|1d|1w"
    description: "Clear description"
```

### 1.2 Gap Extraction Algorithm

```python
def extract_gaps(findings_file):
    gaps = []
    gap_counter = {}
    
    for finding in findings:
        # Filter: Only extract MEDIUM and above
        if finding.severity < MEDIUM:
            continue
        
        # Filter: Evidence must be A or B
        if finding.evidence_grade not in ["A", "B"]:
            if finding.severity == CRITICAL:
                # Reject: CRITICAL must be A or B
                raise ValidationError(f"CRITICAL finding {finding.id} has {finding.evidence_grade} evidence")
            continue
        
        # Extract domain from root_cause or ac_id_suggested
        domain = extract_domain(finding)
        
        # Generate gap_id
        if domain not in gap_counter:
            gap_counter[domain] = 0
        gap_counter[domain] += 1
        gap_id = f"GAP-{domain.upper()}-{gap_counter[domain]:03d}"
        
        # Map to remedy AC
        remedy_ac_id = generate_remedy_ac_id(domain, finding)
        remedy_effort = estimate_effort(finding.remediation_effort)
        remedy_priority = map_severity_to_priority(finding.severity)
        
        # Create gap entry
        gap = {
            "gap_id": gap_id,
            "severity": finding.severity,
            "evidence_grade": finding.evidence_grade,
            "description": finding.description,
            "root_cause": finding.root_cause,
            "affected_ac_ids": finding.affected_acs or [],
            "remedy_ac_id": remedy_ac_id,
            "remedy_effort": remedy_effort,
            "remedy_priority": remedy_priority,
            "blocking_for": identify_blocked_tests(finding),
            "depends_on": identify_dependencies(finding),
            "related_skull_rules": map_rules(finding),
            "issue_id": finding.issue_id,
            "investigation_report": finding.investigation_report
        }
        
        gaps.append(gap)
    
    return gaps

def extract_domain(finding):
    # Extract from ac_id_suggested or root_cause keyword
    if "HASH" in finding.root_cause:
        return "HASH-CHAIN"
    elif "EXCEPTION" in finding.root_cause or "ERROR" in finding.root_cause:
        return "ERROR-HANDLING"
    elif "DUPLICATE" in finding.root_cause:
        return "CODE-DUPLICATION"
    # ... other mappings
    else:
        return "GENERIC"
```

### 1.3 Output Specification

**Output File:** `REVIEW-GAPS-EXTRACTED-YYYYMMDD.yaml`

**Required Structure:**
```yaml
metadata:
  review_date: "2026-01-18"
  consolidated_findings_source: "REVIEW-FINDINGS-CONSOLIDATED-20260118.yaml"
  total_findings: 15
  gaps_extracted: 8
  critical_gaps: 2
  high_gaps: 4
  medium_gaps: 2
  extraction_timestamp: "2026-01-18T10:30:00Z"
  extraction_version: "3.1"

gap_summary:
  total_affected_acs: 12
  total_new_acs_needed: 8
  combined_effort: "8.5 hours"
  blocking_status: "CRITICAL (2 gaps block test suite)"
  ready_for_integration: true

gaps_addressed:
  - gap_id: "GAP-HASH-CHAIN-001"
    severity: "CRITICAL"
    evidence_grade: "A"
    description: "Hash chain integrity - previous_hash hardcoded to empty string"
    root_cause: "IMPLEMENTATION_FLAW"
    affected_ac_ids: ["AC-FIX-001-01"]
    
    remedy:
      ac_id: "AC-FIX-001-02"
      title: "Fix Hash Chain Calculation"
      effort: "1 hour"
      priority: "P0 - CRITICAL"
      blocking_for: ["AC-FIX-001-03", "test_hash_chain_integrity"]
      depends_on: ["AC-FIX-001-01"]
      related_skull_rules: ["CORE-008", "CORE-011", "CORE-012", "CORE-025", "CORE-027"]
      issue_id: "ISSUE-005B"
    
    holistic_context: {}  # Added in Phase 3B
```

---

## 2. HOLISTIC ANALYSIS PROTOCOL (cortex-review.prompt.md Phase 3B)

### 2.1 Input Specification

**Source File:** `REVIEW-GAPS-EXTRACTED-YYYYMMDD.yaml` (from Phase 3A)

### 2.2 Analysis Engine

**Six-Layer Analysis:**

```python
def holistic_analysis(gaps_file):
    """
    Performs 6-layer analysis on extracted gaps before AC creation
    """
    
    # Layer 1: Root Cause Clustering
    clusters = cluster_by_root_cause(gaps)
    for cluster in clusters:
        if len(cluster) > 1:
            # Multiple gaps from single root cause
            cluster['recommendation'] = 'CONSOLIDATE'
            cluster['combined_effort'] = sum([g.effort for g in cluster])
            cluster['benefit'] = f"Fixes {len(cluster)} gaps with unified approach"
    
    # Layer 2: Pattern Recognition
    patterns = detect_patterns(gaps)
    for pattern in patterns:
        if pattern['occurrences'] >= 3:
            # Same issue in 3+ places
            pattern['recommendation'] = 'CREATE_REFACTORING_AC'
            pattern['single_ac_consolidates'] = pattern['occurrences']
    
    # Layer 3: Dependency Optimization
    dependency_graph = build_dependency_graph(gaps)
    for node in dependency_graph:
        node['can_parallelize_with'] = find_independent_nodes(node, dependency_graph)
        if len(node['can_parallelize_with']) > 0:
            node['optimization'] = 'PARALLELIZE'
    
    # Layer 4: Evidence Grading Summary
    evidence_dist = {
        'a': len([g for g in gaps if g.evidence_grade == 'A']),
        'b': len([g for g in gaps if g.evidence_grade == 'B']),
        'c': len([g for g in gaps if g.evidence_grade == 'C'])
    }
    
    by_severity = {}
    for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
        by_severity[severity] = {
            'a': count_with_severity_and_grade(gaps, severity, 'A'),
            'b': count_with_severity_and_grade(gaps, severity, 'B'),
            'c': count_with_severity_and_grade(gaps, severity, 'C')
        }
    
    # Validation: CRITICAL must not have Grade C
    for gap in gaps:
        if gap.severity == 'CRITICAL' and gap.evidence_grade == 'C':
            raise ValidationError(f"Gap {gap.id}: CRITICAL findings cannot have C-grade evidence")
    
    # Layer 5: AC Deduplication
    dedup_analysis = analyze_deduplication(gaps)
    
    # Layer 6: Governance Coverage
    gov_coverage = check_governance_coverage(gaps)
    
    return {
        'root_cause_clusters': clusters,
        'patterns': patterns,
        'dependency_optimization': dependency_graph,
        'evidence_distribution': evidence_dist,
        'deduplication_analysis': dedup_analysis,
        'governance_coverage': gov_coverage,
        'timestamp': now()
    }
```

### 2.3 Output Specification

Adds `holistic_context` to each gap:

```yaml
gaps_addressed:
  - gap_id: "GAP-HASH-CHAIN-001"
    # ... existing fields ...
    
    holistic_context:
      root_cause_cluster: "Hash Chain Architecture"
      cluster_gaps: ["GAP-HASH-CHAIN-001", "GAP-HASH-VALIDATE-001"]
      cluster_root_cause: "Design defect in DatabaseTransactionManager"
      cluster_effort_total: "1.75 hours"
      cluster_priority: "CRITICAL PATH"
      cluster_ac_count: 2
      single_root_cause_benefit: "Fixes 2 gaps with unified approach"
      
      pattern_analysis: null
      
      dependency_optimization:
        depends_on: ["AC-FIX-001-01"]
        blocking_for: ["AC-FIX-001-03"]
        can_parallelize_with: []
        recommendation: "Sequential - no parallelization"
      
      evidence_analysis:
        grade_a_count: 2
        grade_b_count: 0
        compliance: "✅ All CRITICAL gaps have A-grade evidence"
      
      deduplication_analysis:
        consolidated_from_findings: 1
        separate_acs_avoided: 0
      
      governance_coverage:
        covered_rules: ["CORE-025", "CORE-027"]
        total_relevant_rules: 5
        coverage_percentage: 100
```

---

## 3. YAML GENERATION PROTOCOL (cortex-review.prompt.md Phase 3C)

### 3.1 Input Specification

**Source File:** `REVIEW-GAPS-EXTRACTED-YYYYMMDD.yaml` (with holistic_context)

### 3.2 Generation Algorithm

```python
def generate_cortex_master_yaml_updates(gaps_file, master_plan_file):
    """
    Generates cortex_master_yaml_updates section for cortex-builder integration
    """
    
    # Identify affected phases
    affected_phases = set()
    for gap in gaps:
        phase = identify_phase_for_gap(gap)
        affected_phases.add(phase)
    
    if len(affected_phases) > 1:
        raise ValidationError("Gaps affect multiple phases - not yet supported")
    
    phase_id = affected_phases[0]
    phase = load_phase(phase_id)
    
    # Calculate phase updates
    current_ac_count = phase.ac_ids
    new_ac_ids = [g.remedy_ac_id for g in gaps]
    updated_ac_count = current_ac_count + len(new_ac_ids)
    
    # Generate AC specifications
    ac_specs = {}
    for gap in gaps:
        ac_spec = generate_ac_specification(gap)
        ac_id_snake = gap.remedy_ac_id.lower().replace('-', '_')
        ac_specs[ac_id_snake] = ac_spec
    
    # Generate cortex_master_yaml_updates
    updates = {
        'cortex_master_yaml_updates': {
            'affected_phase': phase_id,
            'current_phase_status': phase.status,
            'current_locked': phase.locked,
            
            'phase_changes': {
                'title': f"Add remediation reference",
                'status': 'IN_PROGRESS',  # Changed from COMPLETED
                'locked': False,           # Changed from true
                'ac_ids': f"{current_ac_count} → {updated_ac_count}",
                'completed_ac_ids': f"{current_ac_count} (unchanged)",
                'blocking': True
            },
            
            'gaps_addressed_section': {
                'gaps': gaps  # Include all gap entries with holistic_context
            },
            
            'ac_breakdown': {
                'critical_blockers': calculate_critical_blockers(gaps, phase)
            },
            
            'metadata': {
                'review_investigation_date': datetime.now().isoformat()[:10],
                'review_investigation_report': get_investigation_report_path(),
                'decision_gate': get_decision_gate_path()
            },
            
            'new_ac_specifications': ac_specs,
            
            'integration_validation': {
                'timestamp': now(),
                'status': 'READY_FOR_INTEGRATION',
                'validation_checks': [
                    'Syntax valid',
                    'All remedy ACs mapped',
                    'No circular dependencies',
                    'Governance rules verified'
                ]
            }
        }
    }
    
    return updates
```

### 3.3 AC Specification Template

```python
def generate_ac_specification(gap):
    """
    Generates full AC specification from gap entry
    """
    return {
        'status': 'NOT_STARTED',
        'priority': gap.remedy_priority,
        'issue_discovered': datetime.now().isoformat()[:10],
        'issue_id': gap.issue_id,
        
        'root_cause': gap.root_cause,
        'evidence_grade': f"{gap.evidence_grade} ({get_confidence(gap.evidence_grade)})",
        
        'task': f"Remedy for {gap.gap_id}",
        'description': gap.description,
        
        'acceptance_criteria': generate_acceptance_criteria(gap),
        'estimated_effort': gap.remedy_effort,
        
        'blocking_for': gap.blocking_for,
        'depends_on': gap.depends_on,
        
        'governance_rules': gap.related_skull_rules,
        
        'holistic_context': gap.holistic_context
    }
```

### 3.4 Output Specification

Generates section in REVIEW-GAPS-EXTRACTED file:

```yaml
cortex_master_yaml_updates:
  affected_phase: "PHASE-REMEDIATION-03"
  current_phase_status: "COMPLETED"
  current_locked: true
  
  phase_changes:
    title: "Add ISSUE-005B remediation reference"
    status: "IN_PROGRESS"
    locked: false
    ac_ids: "8 → 10"
    completed_ac_ids: "8 (unchanged)"
    blocking: true
  
  gaps_addressed_section:
    gaps: [list of all extracted gaps with holistic_context]
  
  ac_breakdown:
    critical_blockers: 4  # Previous: 2, New: +2
  
  metadata:
    review_investigation_date: "2026-01-18"
    review_investigation_report: "_workspaces/roadmap/issues/REVIEW-INVESTIGATION-REPORT-20260118.yaml"
    decision_gate: "_workspaces/roadmap/issues/DECISION-GATE-20260118.yaml"
  
  new_ac_specifications:
    ac_fix_001_02: [full spec]
    ac_fix_001_03: [full spec]
  
  integration_validation:
    timestamp: "2026-01-18T11:00:00Z"
    status: "READY_FOR_INTEGRATION"
    validation_checks: [list]
```

---

## 4. INTEGRATION PROTOCOL (cortex-builder.prompt.md)

### 4.1 Trigger Mechanism

```python
def cortex_builder_startup():
    """
    Called on cortex-builder initialization
    """
    # Check for gap files
    gap_files = find_files("_workspaces/roadmap/issues/REVIEW-GAPS-EXTRACTED-*.yaml")
    
    if gap_files:
        for gap_file in gap_files:
            # Check if already integrated
            if is_integrated(gap_file):
                continue
            
            # Verify cortex-master.yaml is clean
            if has_uncommitted_changes('cortex-master.yaml'):
                stash_changes('cortex-master.yaml', f"pre-gap-integration-{gap_file}")
            
            # Run integration protocol
            integrate_gaps(gap_file)
```

### 4.2 Integration Steps (A-F)

**Step A: Pre-Integration Verification**
```python
def verify_pre_integration(gap_file):
    # 1. Check file exists and is readable
    assert os.path.exists(gap_file)
    gaps = load_yaml(gap_file)
    
    # 2. Verify cortex-master.yaml is current
    git_status('cortex-master.yaml')
    
    # 3. If modified: stash
    if is_modified('cortex-master.yaml'):
        git_stash('cortex-master.yaml')
    
    # 4. Read gap file metadata
    assert 'metadata' in gaps
    assert 'gaps_addressed' in gaps
    assert 'cortex_master_yaml_updates' in gaps
```

**Step B: Gap Extraction & Classification**
```python
def classify_gaps(gap_file):
    gaps = load_yaml(gap_file)
    
    for gap in gaps['gaps_addressed']:
        # Extract fields
        severity = gap['severity']
        evidence_grade = gap['evidence_grade']
        remedy_ac_id = gap['remedy_ac_id']
        
        # Classify for integration priority
        if severity == 'CRITICAL' and evidence_grade in ['A', 'B']:
            priority = 'IMMEDIATE'
        elif severity == 'HIGH' and evidence_grade == 'A':
            priority = 'NEXT_SPRINT'
        else:
            priority = 'BACKLOG'
        
        gap['integration_priority'] = priority
```

**Step C: Phase Updates**
```python
def update_phase_tracker(gap_file):
    gaps = load_yaml(gap_file)
    master = load_yaml('cortex-master.yaml')
    updates = gaps['cortex_master_yaml_updates']
    
    phase_id = updates['affected_phase']
    phase = master['phase_tracker'][phase_id]
    
    # Update phase fields
    phase['status'] = updates['phase_changes']['status']
    phase['locked'] = updates['phase_changes']['locked']
    phase['ac_ids'] = calculate_new_ac_count(phase, gaps)
    phase['blocking'] = updates['phase_changes']['blocking']
    
    # Add gaps_addressed
    phase['gaps_addressed'] = updates['gaps_addressed_section']['gaps']
    
    # Update ac_breakdown
    phase['ac_breakdown']['critical_blockers'] = updates['ac_breakdown']['critical_blockers']
    
    # Add metadata
    phase['metadata'] = updates['metadata']
```

**Step D: Add AC Specifications**
```python
def add_ac_specifications(gap_file):
    gaps = load_yaml(gap_file)
    master = load_yaml('cortex-master.yaml')
    updates = gaps['cortex_master_yaml_updates']
    
    phase_id = updates['affected_phase']
    phase = master['phase_tracker'][phase_id]
    
    # Add each new AC specification
    for ac_snake, ac_spec in updates['new_ac_specifications'].items():
        phase[ac_snake] = ac_spec
```

**Step E: Validation**
```python
def validate_integration(gap_file):
    master = load_yaml('cortex-master.yaml')
    
    # 1. Syntax
    try:
        write_yaml(master, 'temp.yaml')
        run_cmd('yamllint temp.yaml')
    except:
        raise ValidationError("YAML syntax invalid")
    
    # 2. Gap-to-AC mapping
    for phase in master['phase_tracker'].values():
        if 'gaps_addressed' in phase:
            for gap in phase['gaps_addressed']:
                ac_id_snake = gap['remedy_ac_id'].lower().replace('-', '_')
                if ac_id_snake not in phase:
                    raise ValidationError(f"AC {gap['remedy_ac_id']} missing spec")
    
    # 3. Cycle detection
    for phase in master['phase_tracker'].values():
        for ac_id in phase.get('ac_ids', []):
            if ac_id in phase:
                depends = phase[ac_id].get('depends_on', [])
                blocking = phase[ac_id].get('blocking_for', [])
                for d in depends:
                    if d in blocking:
                        raise ValidationError(f"Cycle: {ac_id} → {d} → {ac_id}")
    
    # 4. Governance rules
    for rule_id in get_all_referenced_rules(master):
        if not rule_exists(rule_id):
            raise ValidationError(f"Unknown rule {rule_id}")
    
    # 5. Evidence grading
    for phase in master['phase_tracker'].values():
        if 'gaps_addressed' in phase:
            for gap in phase['gaps_addressed']:
                if gap['severity'] == 'CRITICAL':
                    if gap['evidence_grade'] not in ['A', 'B']:
                        raise ValidationError(f"Gap {gap['gap_id']}: CRITICAL must be A/B")
```

**Step F: Git Commit**
```python
def commit_integration(gap_file):
    # Stage cortex-master.yaml
    git_add('cortex-master.yaml')
    
    # Generate commit message
    gaps = load_yaml(gap_file)
    updates = gaps['cortex_master_yaml_updates']
    phase = updates['affected_phase']
    
    message = f"""integrate-review-gaps: {phase} remediation ACs added

{generate_commit_details(gaps)}

Root cause: {describe_root_causes(gaps)}
Evidence grade: {summarize_evidence_grades(gaps)}
Blocking status: {describe_blocking(gaps)}

See: {gaps['metadata']['review_investigation_report']}
See: {gaps['metadata']['decision_gate']}"""
    
    git_commit(message)
```

### 4.3 Error Handling

```python
def handle_integration_error(error_type, error_msg):
    if error_type == 'SYNTAX_ERROR':
        # Restore from stash and report
        git_stash_pop()
        raise SyntaxError(error_msg)
    
    elif error_type == 'VALIDATION_ERROR':
        # Log error, do not commit
        log_error(error_msg)
        raise ValidationError(error_msg)
    
    elif error_type == 'GIT_CONFLICT':
        # Stash integration, manual resolution needed
        git_stash()
        raise GitConflictError("Manual resolution required")
```

---

## 5. FILE FORMAT SPECIFICATIONS

### 5.1 REVIEW-GAPS-EXTRACTED-YYYYMMDD.yaml

**Full Schema:**

```yaml
metadata:
  review_date: <date-iso>
  consolidated_findings_source: <filename>
  total_findings: <int>
  gaps_extracted: <int>
  critical_gaps: <int>
  high_gaps: <int>
  medium_gaps: <int>
  extraction_timestamp: <datetime-iso>
  extraction_version: <version>

gap_summary:
  total_affected_acs: <int>
  total_new_acs_needed: <int>
  combined_effort: <duration-string>
  blocking_status: <string>
  ready_for_integration: <bool>

gaps_addressed:
  - gap_id: <string>              # GAP-{DOMAIN}-{NNN}
    severity: <enum>              # CRITICAL|HIGH|MEDIUM|LOW
    evidence_grade: <enum>        # A|B|C
    description: <string>
    root_cause: <enum>            # IMPLEMENTATION_FLAW|INTEGRATION_ISSUE|DESIGN_WEAKNESS
    affected_ac_ids: <list>
    affected_tests: <list>
    
    remedy:
      ac_id: <string>             # AC-FIX-*-*
      title: <string>
      description: <string>
      effort: <duration-string>
      priority: <string>          # P0-P3
      blocking_for: <list>
      depends_on: <list>
      related_skull_rules: <list>
      issue_id: <string>
    
    holistic_context:
      root_cause_cluster: <string>
      cluster_gaps: <list>
      cluster_effort_total: <duration-string>
      cluster_priority: <string>
      cluster_ac_count: <int>
      single_root_cause_benefit: <string>
      pattern_analysis: <object>
      dependency_optimization: <object>
      evidence_analysis: <object>
      deduplication_analysis: <object>
      governance_coverage: <object>

cortex_master_yaml_updates:
  affected_phase: <phase-id>
  current_phase_status: <string>
  current_locked: <bool>
  
  phase_changes:
    title: <string>
    status: <string>
    locked: <bool>
    ac_ids: <string>              # e.g., "8 → 10"
    completed_ac_ids: <string>
    blocking: <bool>
  
  gaps_addressed_section:
    gaps: <list>
  
  ac_breakdown:
    critical_blockers: <int>
  
  metadata:
    review_investigation_date: <date>
    review_investigation_report: <filepath>
    decision_gate: <filepath>
  
  new_ac_specifications:
    <ac_id_snake>:
      status: <string>
      priority: <string>
      # ... full AC spec
  
  integration_validation:
    timestamp: <datetime-iso>
    status: <enum>                # READY_FOR_INTEGRATION|NEEDS_REVIEW|INVALID
    validation_checks: <list>
```

---

## 6. VALIDATION RULES

### 6.1 Mandatory Rules

```
RULE V001: Every gap must have evidence_grade in [A, B, C]
RULE V002: CRITICAL findings MUST have evidence_grade in [A, B]
RULE V003: Every gap must map to exactly one remedy AC
RULE V004: All remedy ACs must be unique (no duplicates)
RULE V005: No circular dependencies (A depends_on B and B blocking_for A)
RULE V006: All referenced governance rules must exist
RULE V007: Phase status must change from COMPLETED to IN_PROGRESS
RULE V008: Phase locked must change from true to false
RULE V009: All new ACs must have full specifications
RULE V010: All referenced issue_ids must be valid
```

### 6.2 Optional Rules

```
RULE O001: Holistic context recommended (improves traceability)
RULE O002: Pattern analysis recommended (prevents redundant ACs)
RULE O003: Comments for non-obvious dependencies (readability)
```

---

## 7. EDGE CASES & ERROR HANDLING

### 7.1 Multiple Gaps Affecting Same AC

**Scenario:** Two gaps both suggest remedy in same AC
**Resolution:** Merge gap entries, combine descriptions
**Code:**
```python
if len([g for g in gaps if g.remedy_ac_id == remedy_id]) > 1:
    # Merge gaps
    merged_gap = merge_gaps(gaps_with_same_remedy)
    # Single AC spec addresses all
```

### 7.2 Gap Affecting Non-Existent AC

**Scenario:** Gap suggests remedy AC that doesn't exist in phase
**Resolution:** Create AC specification from gap data
**Code:**
```python
if remedy_ac not in phase:
    ac_spec = generate_ac_specification(gap)
    phase[remedy_ac_snake] = ac_spec
```

### 7.3 Circular Dependencies

**Scenario:** AC-A depends_on AC-B and AC-B blocking_for AC-A
**Resolution:** Reject integration, require manual fix
**Code:**
```python
if creates_cycle(ac_graph):
    raise ValidationError("Circular dependency detected")
```

### 7.4 Evidence Grade Downgrade

**Scenario:** CRITICAL finding has Grade C evidence
**Resolution:** Reject gap extraction
**Code:**
```python
if severity == CRITICAL and evidence_grade == C:
    raise ValidationError("Cannot extract CRITICAL gap with Grade C evidence")
```

---

## 8. PERFORMANCE CONSIDERATIONS

### 8.1 Time Complexity

| Operation | Complexity | Notes |
|-----------|-----------|-------|
| Extract gaps | O(n) | n = findings count |
| Holistic analysis | O(n²) | Pattern recognition is quadratic |
| Generate YAML | O(m) | m = gaps count |
| Validate integration | O(m + k) | k = AC count |
| Git operations | O(1) | Constant, file size < 50KB |

**Total time:** ~20 minutes (for typical review with 15 findings → 8 gaps)

### 8.2 Memory Requirements

- Typical review: <100MB
- Large review (50+ findings): <500MB
- No streaming needed (files <50KB)

---

## 9. RECOVERY PROCEDURES

### 9.1 Failed Integration

**If cortex-builder integration fails:**

```bash
# 1. Restore stashed cortex-master.yaml
git stash pop

# 2. Check gap file for validation errors
yamllint _workspaces/roadmap/issues/REVIEW-GAPS-EXTRACTED-*.yaml

# 3. Fix validation errors in gap file
# (See VALIDATION RULES section above)

# 4. Retry integration
/cortex-builder integrate-gaps --gaps-file <fixed-file>
```

### 9.2 Incomplete Integration

**If cortex-builder crashes mid-integration:**

```bash
# 1. Check if cortex-master.yaml is partially updated
git diff cortex-master.yaml

# 2. If clean state desired: revert
git checkout cortex-master.yaml

# 3. Restart integration from Step A
```

### 9.3 Manual Fix Required

**If systematic integration not possible:**

```bash
# 1. Document reason in gap file comments
# 2. Reference GitHub issue for manual review
# 3. Manually apply cortex_master_yaml_updates section
# 4. Commit with message including reason for manual handling
```

---

## 10. AUDIT TRAIL

### 10.1 Integration Metadata

Every integration adds to cortex-master.yaml:

```yaml
phase:
  metadata:
    review_investigation_date: "2026-01-18"
    review_investigation_report: "_workspaces/roadmap/issues/REVIEW-INVESTIGATION-REPORT-20260118.yaml"
    decision_gate: "_workspaces/roadmap/issues/DECISION-GATE-20260118.yaml"
    gap_extraction_file: "_workspaces/roadmap/issues/REVIEW-GAPS-EXTRACTED-20260118.yaml"
    gap_integration_timestamp: "2026-01-18T11:30:00Z"
    gap_integration_commit: "<commit-sha>"
```

### 10.2 Git Audit Trail

```bash
# View integration history
git log --oneline | grep "integrate-review-gaps"

# View specific integration commit
git show <commit-sha>

# Trace back to review findings
git show <commit-sha>:cortex-master.yaml | grep -A20 "metadata:"
```

---

**Version:** 3.1  
**Last Updated:** 2026-01-18  
**Status:** PRODUCTION READY ✅
