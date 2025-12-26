# Phase 13B Capability 7: ADO Operations Validation Plan

**Capability:** ADO Operations - Azure DevOps Work Item Hierarchy Generation  
**Status:** ⏳ READY FOR VALIDATION  
**Date:** December 26, 2025  
**Duration:** 5 hours estimated

---

## 🎯 Validation Objective

Validate ADO Operations' ability to transform architectural flaws into properly structured Azure DevOps work item hierarchies:

1. **Flaw → Work Item Mapping:** Map all 65 STS flaws to ADO work items
2. **Hierarchy Generation:** Create proper Epic → Feature → Story → Task structure
3. **Formatting Compliance:** Generate ADO-compliant markdown with acceptance criteria
4. **Traceability:** Maintain bidirectional traceability (Flaw ID ↔ Work Item ID)
5. **Effort Estimation:** T-shirt sizing (XS/S/M/L/XL) for all work items

**Target:** Transform 65 STS flaws into complete ADO work item hierarchy

---

## 📊 Input: STS Application Flaws (65 Total)

### Flaw Categories

| Category | Count | Examples |
|----------|-------|----------|
| **Security** | 12 | SQL injection, hardcoded secrets, weak auth |
| **SOLID** | 15 | God classes, tight coupling, no abstractions |
| **Code Quality** | 20 | High complexity, duplication, dead code |
| **Performance** | 8 | N+1 queries, memory leaks, no caching |
| **Testing** | 10 | 0% coverage, no edge cases, placeholder tests |
| **Documentation** | 8 | Outdated, contradictory, missing |

**Total:** 65 flaws → Target: 1 Epic, 6 Features, 65 Stories, 180+ Tasks

---

## 🏗️ ADO Work Item Hierarchy Structure

### Level 1: Epic (1)

```markdown
# Epic: Sharpen The Saw - STS Application Transformation

**ID:** EPIC-001  
**Priority:** 1 - Critical  
**Business Value:** Enable CORTEX 4.0 validation through comprehensive codebase transformation

## Objective
Transform STS validation application from F grade (25/100) to A grade (90+/100) by systematically addressing 65 documented flaws across 6 categories.

## Success Criteria
- ✅ Security: 12 vulnerabilities → 0 (OWASP Top 10 compliance)
- ✅ SOLID: 15 violations → 0 (100% principle compliance)
- ✅ Code Quality: 20 smells → 0 (pylint 9.0+, complexity <15)
- ✅ Performance: 8 bottlenecks → 0 (+50% improvement)
- ✅ Testing: 15% → 90%+ coverage
- ✅ Documentation: 8 issues → 0 (100% accuracy)

## Metrics
- **Duration:** 4-5 weeks
- **Effort:** 120-150 hours
- **Features:** 6
- **Stories:** 65
- **Tasks:** 180+

## Dependencies
- CORTEX 4.0 capability validation framework
- STS validation application baseline

## Tags
`cortex-4.0` `validation` `phase-13b` `sharpen-the-saw`
```

---

### Level 2: Features (6)

**Feature Structure:**
```markdown
# Feature: [Category] Resolution

**ID:** FEAT-00X  
**Epic:** EPIC-001  
**Priority:** [1-4]  
**Effort:** [L/XL]

## Objective
[Category-specific objective]

## Success Criteria
- ✅ [Criterion 1]
- ✅ [Criterion 2]
- ✅ [Criterion 3]

## Stories
- [Story list with IDs]

## Acceptance Criteria
**GIVEN** [context]  
**WHEN** [action]  
**THEN** [expected outcome]

## Tags
`[category]` `cortex-4.0` `phase-13b`
```

**Example - Feature 1:**
```markdown
# Feature: Security Vulnerability Resolution

**ID:** FEAT-001  
**Epic:** EPIC-001  
**Priority:** 1 - Critical  
**Effort:** XL (30-40 hours)

## Objective
Eliminate all 12 security vulnerabilities mapped to OWASP Top 10:2021, achieving zero-vulnerability status and security audit compliance.

## Success Criteria
- ✅ 0 CRITICAL vulnerabilities (SQL injection, hardcoded secrets)
- ✅ 0 HIGH vulnerabilities (debug mode, weak crypto)
- ✅ 0 MEDIUM vulnerabilities (rate limiting, CORS)
- ✅ OWASP Top 10:2021 compliance (12/12 categories)
- ✅ Security audit passes with 100% score

## Stories (12)
- STORY-001: Fix SQL injection in auth.py
- STORY-002: Fix SQL injection in products.py
- STORY-003: Remove hardcoded JWT secret
- STORY-004: Implement password hashing
- STORY-005: Disable debug mode in production
- STORY-006: Upgrade to stronger crypto (HS512)
- STORY-007: Add rate limiting (DoS protection)
- STORY-008: Remove .env from version control
- STORY-009: Upgrade vulnerable dependencies
- STORY-010: Fix OS command injection
- STORY-011: Replace insecure deserialization
- STORY-012: Restrict CORS policy

## Acceptance Criteria
**GIVEN** the STS application with 12 security vulnerabilities  
**WHEN** all 12 stories are completed and security audit is run  
**THEN** 0 vulnerabilities remain and OWASP Top 10 compliance is achieved

## Dependencies
- Security scanning tools (Bandit, Safety)
- OWASP Top 10:2021 checklist

## Tags
`security` `owasp-top-10` `critical` `cortex-4.0`
```

---

### Level 3: Stories (65)

**Story Structure:**
```markdown
# Story: [Brief Title]

**ID:** STORY-XXX  
**Feature:** FEAT-00X  
**Priority:** [1-4]  
**Effort:** [XS/S/M/L/XL]  
**Flaw ID:** [SEC-XX, SOL-XX, CQ-XX, etc.]

## Description
[Detailed problem description with context]

## Acceptance Criteria
**GIVEN** [preconditions]  
**WHEN** [action taken]  
**THEN** [expected result]

**AND** [additional criteria]

## Technical Details
- **Location:** [file:line]
- **Severity:** [CRITICAL/HIGH/MEDIUM/LOW]
- **Impact:** [users affected, systems impacted]
- **Root Cause:** [technical explanation]

## Solution Approach
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Tasks
- [ ] TASK-XXX: [Task description]
- [ ] TASK-XXX: [Task description]
- [ ] TASK-XXX: [Task description]

## Test Plan
- [ ] Unit tests: [description]
- [ ] Integration tests: [description]
- [ ] Security tests: [description]

## Definition of Done
- [ ] Code implemented and reviewed
- [ ] Tests passing (100%)
- [ ] Security scan passes
- [ ] Documentation updated
- [ ] No regressions

## Tags
`[category]` `[severity]` `[owasp-category]`
```

**Example - Story 1:**
```markdown
# Story: Fix SQL Injection in Authentication Module

**ID:** STORY-001  
**Feature:** FEAT-001 (Security Vulnerability Resolution)  
**Priority:** 1 - Critical  
**Effort:** M (4-6 hours)  
**Flaw ID:** SEC-03

## Description
The `database.py` module uses f-strings for SQL query construction (line 28), making it vulnerable to SQL injection attacks (CWE-89, OWASP A03:2021 Injection).

Current vulnerable code:
```python
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
cursor.execute(query)
```

Attackers can bypass authentication using inputs like:
- Username: `admin' OR '1'='1`
- Password: `anything`

## Acceptance Criteria
**GIVEN** the authentication module with SQL injection vulnerability  
**WHEN** parameterized queries are implemented using `?` placeholders  
**THEN** SQL injection attacks are prevented and authentication works securely

**AND** all existing authentication tests pass  
**AND** new security tests validate injection protection  
**AND** Bandit security scan reports 0 SQL injection vulnerabilities

## Technical Details
- **Location:** `src/data/database.py:28`
- **Severity:** CRITICAL
- **OWASP:** A03:2021 - Injection
- **CWE:** CWE-89 - SQL Injection
- **Impact:** Complete authentication bypass, unauthorized access
- **Root Cause:** String interpolation in SQL queries (f-strings)

## Solution Approach
1. Replace f-string query with parameterized query using `?` placeholders
2. Pass parameters as tuple to `cursor.execute()`
3. Add input validation for username/password format
4. Implement SQL injection security tests
5. Run Bandit scan to verify fix

**Before:**
```python
query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
cursor.execute(query)
```

**After:**
```python
query = "SELECT * FROM users WHERE username = ? AND password = ?"
cursor.execute(query, (username, password))
```

## Tasks
- [ ] TASK-001: Replace f-string with parameterized query (1h)
- [ ] TASK-002: Add input validation for credentials (1h)
- [ ] TASK-003: Create SQL injection security tests (2h)
- [ ] TASK-004: Run Bandit scan and verify 0 issues (0.5h)
- [ ] TASK-005: Update security documentation (0.5h)

## Test Plan
- [ ] Unit tests: Verify authentication with valid credentials
- [ ] Security tests: Attempt SQL injection attacks (5 payloads)
- [ ] Integration tests: End-to-end login flow
- [ ] Performance tests: Query execution time unchanged

**Security Test Cases:**
1. `admin' OR '1'='1` → Rejected
2. `'; DROP TABLE users; --` → Rejected
3. `admin' UNION SELECT * FROM passwords --` → Rejected
4. `\\' OR 1=1 --` → Rejected
5. `admin' AND '1'='1` → Rejected

## Definition of Done
- [x] Parameterized queries implemented
- [x] Input validation added
- [x] All tests passing (100%)
- [x] Bandit scan: 0 SQL injection issues
- [x] Security documentation updated
- [x] Code reviewed and approved
- [x] No authentication regressions

## References
- OWASP Top 10:2021 - A03:2021 Injection
- CWE-89: SQL Injection
- Bandit Rule: B608 (hardcoded_sql_expressions)

## Tags
`security` `critical` `sql-injection` `owasp-a03` `cwe-89`
```

---

### Level 4: Tasks (180+)

**Task Structure:**
```markdown
# Task: [Action-oriented title]

**ID:** TASK-XXX  
**Story:** STORY-XXX  
**Effort:** [1-8 hours]  
**Assignee:** [Developer/Tester/Reviewer]

## Description
[Specific, actionable task description]

## Steps
1. [Step 1]
2. [Step 2]
3. [Step 3]

## Acceptance Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]

## Tags
`[task-type]` `[skill-required]`
```

**Example - Task 1:**
```markdown
# Task: Replace f-string with Parameterized Query

**ID:** TASK-001  
**Story:** STORY-001  
**Effort:** 1 hour  
**Assignee:** Backend Developer

## Description
Replace the SQL query f-string in `database.py:28` with a parameterized query using `?` placeholders to prevent SQL injection.

## Steps
1. Open `src/data/database.py`
2. Locate line 28: `query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"`
3. Replace with: `query = "SELECT * FROM users WHERE username = ? AND password = ?"`
4. Update `cursor.execute(query)` to `cursor.execute(query, (username, password))`
5. Verify syntax is correct
6. Run existing tests to ensure no regressions

## Acceptance Criteria
- [x] F-string removed from SQL query
- [x] Parameterized query using `?` placeholders
- [x] Parameters passed as tuple
- [x] Existing authentication tests pass
- [x] Code follows PEP 8 style guide

## Tags
`backend` `security-fix` `sql`
```

---

## 🔄 ADO Work Item Generation Algorithm

```python
def generate_ado_hierarchy(flaws):
    """Generate complete ADO work item hierarchy from STS flaws."""
    
    # Level 1: Epic
    epic = create_epic({
        'id': 'EPIC-001',
        'title': 'Sharpen The Saw - STS Application Transformation',
        'flaws_count': len(flaws),
        'categories': get_unique_categories(flaws),
        'duration': '4-5 weeks',
        'effort': '120-150 hours'
    })
    
    # Level 2: Features (group by category)
    features = []
    flaw_categories = group_by_category(flaws)
    
    for idx, (category, category_flaws) in enumerate(flaw_categories.items(), 1):
        feature = create_feature({
            'id': f'FEAT-{idx:03d}',
            'epic_id': epic['id'],
            'title': f'{category} Resolution',
            'priority': get_category_priority(category),
            'effort': calculate_feature_effort(category_flaws),
            'flaws': category_flaws,
            'success_criteria': generate_success_criteria(category, category_flaws)
        })
        features.append(feature)
    
    # Level 3: Stories (one per flaw)
    stories = []
    for flaw in flaws:
        feature = find_feature_by_category(features, flaw['category'])
        
        story = create_story({
            'id': f"STORY-{flaw['id'].split('-')[1]}",
            'feature_id': feature['id'],
            'flaw_id': flaw['id'],
            'title': flaw['description'],
            'priority': map_severity_to_priority(flaw['severity']),
            'effort': estimate_story_effort(flaw),
            'acceptance_criteria': generate_acceptance_criteria(flaw),
            'technical_details': extract_technical_details(flaw),
            'solution_approach': generate_solution_approach(flaw)
        })
        stories.append(story)
    
    # Level 4: Tasks (2-4 per story)
    tasks = []
    for story in stories:
        story_tasks = generate_tasks_for_story(story)
        tasks.extend(story_tasks)
    
    # Build hierarchy
    hierarchy = {
        'epic': epic,
        'features': features,
        'stories': stories,
        'tasks': tasks,
        'metadata': {
            'total_work_items': 1 + len(features) + len(stories) + len(tasks),
            'total_effort_hours': sum(t['effort'] for t in tasks),
            'generation_date': datetime.now().isoformat()
        }
    }
    
    return hierarchy


def generate_tasks_for_story(story):
    """Generate 2-4 tasks per story based on flaw type."""
    
    task_templates = {
        'security': [
            'Implement security fix',
            'Add security tests',
            'Run security scan',
            'Update security documentation'
        ],
        'solid': [
            'Refactor code structure',
            'Add unit tests',
            'Update class diagram',
            'Review SOLID compliance'
        ],
        'code_quality': [
            'Apply refactoring pattern',
            'Reduce complexity',
            'Add tests',
            'Update documentation'
        ],
        'performance': [
            'Implement optimization',
            'Add performance tests',
            'Benchmark improvements',
            'Update performance docs'
        ],
        'testing': [
            'Write test cases',
            'Implement tests',
            'Achieve coverage target',
            'Review test quality'
        ],
        'documentation': [
            'Update documentation',
            'Verify accuracy',
            'Add code examples',
            'Review for completeness'
        ]
    }
    
    category = story['flaw_id'].split('-')[0].lower()
    templates = task_templates.get(category, task_templates['code_quality'])
    
    tasks = []
    for idx, template in enumerate(templates[:3], 1):  # 3 tasks per story
        task = {
            'id': f"{story['id']}-T{idx:02d}",
            'story_id': story['id'],
            'title': f"{template}: {story['title'][:50]}",
            'effort': estimate_task_effort(template, story),
            'assignee': determine_assignee(template),
            'description': generate_task_description(template, story),
            'steps': generate_task_steps(template, story),
            'acceptance_criteria': generate_task_acceptance_criteria(template)
        }
        tasks.append(task)
    
    return tasks


def estimate_story_effort(flaw):
    """Estimate story effort using T-shirt sizing."""
    
    # Base effort by severity
    severity_effort = {
        'CRITICAL': 'L',  # 8-12 hours
        'HIGH': 'M',       # 4-6 hours
        'MEDIUM': 'S',     # 2-3 hours
        'LOW': 'XS'        # 1-2 hours
    }
    
    base_effort = severity_effort[flaw['severity']]
    
    # Adjust for complexity
    if flaw.get('complexity', 0) > 50:
        base_effort = increase_effort(base_effort)  # M → L, L → XL
    
    # Adjust for dependencies
    if len(flaw.get('dependencies', [])) > 3:
        base_effort = increase_effort(base_effort)
    
    return base_effort
```

---

## 📊 Traceability Matrix

### Flaw → Work Item Mapping

| Flaw ID | Category | Severity | Story ID | Feature ID | Epic ID | Status |
|---------|----------|----------|----------|------------|---------|--------|
| SEC-01 | Security | CRITICAL | STORY-001 | FEAT-001 | EPIC-001 | ⏳ |
| SEC-02 | Security | CRITICAL | STORY-002 | FEAT-001 | EPIC-001 | ⏳ |
| ... | ... | ... | ... | ... | ... | ... |
| DOC-08 | Documentation | MEDIUM | STORY-065 | FEAT-006 | EPIC-001 | ⏳ |

**Traceability Algorithm:**
```python
def generate_traceability_matrix(hierarchy):
    """Generate bidirectional traceability matrix."""
    
    matrix = []
    
    for story in hierarchy['stories']:
        # Get parent feature and epic
        feature = find_by_id(hierarchy['features'], story['feature_id'])
        epic = hierarchy['epic']
        
        # Get child tasks
        tasks = [t for t in hierarchy['tasks'] if t['story_id'] == story['id']]
        
        matrix.append({
            'flaw_id': story['flaw_id'],
            'category': extract_category(story['flaw_id']),
            'severity': story['priority'],
            'story_id': story['id'],
            'story_title': story['title'],
            'feature_id': feature['id'],
            'feature_title': feature['title'],
            'epic_id': epic['id'],
            'task_ids': [t['id'] for t in tasks],
            'task_count': len(tasks),
            'total_effort_hours': sum(t['effort'] for t in tasks),
            'status': '⏳ Pending',
            'completion_percentage': 0
        })
    
    return matrix
```

---

## ✅ Success Criteria

| Criterion | Target | Validation |
|-----------|--------|------------|
| **Work Items Generated** | 252+ | Count check (1 Epic + 6 Features + 65 Stories + 180 Tasks) |
| **Flaw Coverage** | 100% | All 65 flaws mapped to stories |
| **Hierarchy Compliance** | 100% | Epic → Feature → Story → Task structure |
| **Formatting** | 100% | ADO markdown compliant |
| **Acceptance Criteria** | 100% | GIVEN-WHEN-THEN for all stories |
| **Effort Estimation** | 100% | T-shirt sizing for all items |
| **Traceability** | 100% | Bidirectional Flaw ↔ Work Item |

---

## 🎯 Validation Execution

### Phase 1: Work Item Generation (90 minutes)

1. **Parse STS Flaws (15 min):** Load 65 flaws from `sts-baseline.json`
2. **Generate Epic (10 min):** Create top-level epic
3. **Generate Features (20 min):** Create 6 category-based features
4. **Generate Stories (30 min):** Create 65 stories (one per flaw)
5. **Generate Tasks (15 min):** Create 180+ tasks (2-4 per story)

### Phase 2: Validation & Export (60 minutes)

1. **Validate Hierarchy (20 min):** Check parent-child relationships
2. **Validate Formatting (15 min):** ADO markdown compliance
3. **Generate Traceability Matrix (15 min):** Bidirectional mapping
4. **Export to ADO Format (10 min):** JSON/CSV for import

### Phase 3: Quality Checks (90 minutes)

1. **Acceptance Criteria Review (30 min):** Verify GIVEN-WHEN-THEN format
2. **Effort Estimation Review (20 min):** Validate T-shirt sizing
3. **Completeness Check (20 min):** All required fields populated
4. **Test Import (20 min):** Simulate ADO import process

---

## 📝 Validation Report Template

```markdown
# ADO Operations Validation Report

## Executive Summary
- **Flaws Processed:** 65/65 (100%)
- **Work Items Generated:** 252 (1 Epic + 6 Features + 65 Stories + 180 Tasks)
- **Hierarchy Compliance:** 100%
- **Traceability:** 100%
- **Duration:** 5 hours

## Results

### Work Item Generation ✅
- Epic: 1 ✅
- Features: 6 ✅
- Stories: 65 ✅
- Tasks: 180 ✅

### Quality Metrics ✅
- Flaw Coverage: 100% (65/65)
- Acceptance Criteria: 100% (65/65 GIVEN-WHEN-THEN)
- Effort Estimation: 100% (245/245 T-shirt sized)
- Formatting: 100% ADO compliant
- Traceability: 100% bidirectional

## Traceability Matrix
[65 rows showing Flaw → Story → Feature → Epic mapping]

**Verdict:** ✅ **ADO OPERATIONS VALIDATED**
```

---

**Plan Created:** December 26, 2025  
**Status:** ⏳ READY FOR VALIDATION  
**Duration:** 5 hours estimated  
**Target:** 252 work items, 100% traceability, ADO-compliant

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
