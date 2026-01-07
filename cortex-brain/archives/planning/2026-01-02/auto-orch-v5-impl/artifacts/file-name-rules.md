# Filename Validation Rules

**Version:** 1.0  
**Created:** January 2, 2026  
**Enforcement:** Mandatory across all CORTEX operations

---

## 🎯 Core Requirements

### Maximum Length
- **Limit:** 20 characters (excluding file extension)
- **Master Plan Exception:** 25 characters (excluding extension) with `mst-` prefix
- **Rationale:** Improved readability, consistent formatting, easier navigation
- **Scope:** All files created by CORTEX orchestrators

### Naming Convention
- **Format:** `kebab-case` (lowercase with hyphens)
- **Pattern:** `^[a-z0-9]+(-[a-z0-9]+)*$`
- **Master Plan Pattern:** `^mst-[a-z0-9]+(-[a-z0-9]+)*$` (must start with `mst-`)
- **Examples:**
  - ✅ `mst-pure-autonomous.md` (master plan, 20 chars)
  - ✅ `test-coverage.json`
  - ✅ `db-schema.sql`
  - ❌ `Master_Plan.md` (not kebab-case)
  - ❌ `test--coverage.json` (consecutive hyphens)
  - ❌ `-test.json` (starts with hyphen)
  - ❌ `00-master-plan.md` (master plan missing `mst-` prefix)

### Character Set
- **Allowed:** Lowercase letters (a-z), digits (0-9), hyphens (-)
- **Prohibited:** 
  - Uppercase letters
  - Underscores
  - Spaces
  - Special characters (!@#$%^&*()+=[]{}|\\:;"'<>,.?/)

---

### Rule 1: Length Check
```python
def check_length(filename: str, is_master_plan: bool = False) -> bool:
    """Filename (without extension) must be ≤20 chars (≤25 for master plans)"""
    name_without_ext = os.path.splitext(filename)[0]
    max_len = 25 if is_master_plan else 20
    return len(name_without_ext) <= max_len
```

**Examples:**
- ✅ `mst-pure-autonomous.md` (20 chars, master plan)
- ✅ `config-spec.yaml` (11 chars)
- ✅ `test-report.md` (11 chars)
- ❌ `comprehensive-architecture-analysis.md` (37 chars)
- ❌ `mst-comprehensive-implementation-plan.md` (41 chars, exceeds 25)
- ✅ `00-master-plan.md` (14 chars)
### Rule 2: Format Check
```python
def check_format(filename: str, is_master_plan: bool = False) -> bool:
    """Filename must be kebab-case (master plans must start with mst-)"""
    name_without_ext = os.path.splitext(filename)[0]
    
    if is_master_plan:
        pattern = r'^mst-[a-z0-9]+(-[a-z0-9]+)*$'
    else:
        pattern = r'^[a-z0-9]+(-[a-z0-9]+)*$'
    
    return re.match(pattern, name_without_ext) is not None
```

**Examples:**
- ✅ `mst-pure-autonomous.md` (master plan)
- ✅ `test-report.md`
- ✅ `v5-plan.md`
- ❌ `TestReport.md` (camelCase)
- ❌ `test_report.md` (snake_case)
- ❌ `test--report.md` (consecutive hyphens)
- ❌ `00-master-plan.md` (master plan without mst- prefix)
- ❌ `test_report.md` (snake_case)
- ❌ `test--report.md` (consecutive hyphens)

### Rule 3: Extension Check
```python
def check_extension(filename: str) -> bool:
    """Extension must be valid for file type"""
    valid_extensions = {
        '.md', '.json', '.yaml', '.yml', '.py', 
        '.sql', '.txt', '.log', '.html', '.css'
    }
    ext = os.path.splitext(filename)[1].lower()
    return ext in valid_extensions
```

---

## 🛠️ Auto-Fix Strategies

### Strategy 1: Shorten Long Names
```python
def suggest_filename(long_name: str, max_len: int = 20) -> str:
    """Intelligently shorten while preserving meaning"""
    
    # Remove common words
    stopwords = ['the', 'and', 'or', 'for', 'with', 'from', 'to']
    words = long_name.split('-')
    filtered = [w for w in words if w not in stopwords]
    
    # Try abbreviations
    abbrev_map = {
        'architecture': 'arch',
        'configuration': 'config',
        'database': 'db',
        'documentation': 'docs',
        'implementation': 'impl',
        'orchestrator': 'orch',
        'specification': 'spec',
        'validation': 'valid',
        'migration': 'migrate',
        'analysis': 'analyze'
    }
    
    result = []
    for word in filtered:
        if word in abbrev_map:
            result.append(abbrev_map[word])
        else:
            result.append(word)
    
    shortened = '-'.join(result)
    
    # If still too long, truncate intelligently
    if len(shortened) > max_len:
**Examples:**
- `comprehensive-architecture-analysis` → `arch-analyze` (12 chars)
- `database-migration-script` → `db-migrate-script` (17 chars)
- `implementation-documentation` → `impl-docs` (9 chars)
- `master-plan-autonomous-orchestrator-v5` → `mst-pure-autonomous` (20 chars, master plan)
    return shortened[:max_len]
```

**Examples:**
- `comprehensive-architecture-analysis` → `arch-analyze` (12 chars)
- `database-migration-script` → `db-migrate-script` (17 chars)
- `implementation-documentation` → `impl-docs` (9 chars)

### Strategy 2: Convert Case
```python
def to_kebab_case(filename: str) -> str:
    """Convert any case to kebab-case"""
    
    # Handle camelCase and PascalCase
    name = re.sub('([a-z0-9])([A-Z])', r'\1-\2', filename)
    
    # Handle snake_case
    name = name.replace('_', '-')
    
    # Handle spaces
    name = name.replace(' ', '-')
    
    # Remove consecutive hyphens
    name = re.sub('-+', '-', name)
    
    # Convert to lowercase
    name = name.lower()
    
    # Remove leading/trailing hyphens
    name = name.strip('-')
    
    return name
```

**Examples:**
- `TestReport` → `test-report`
- `test_coverage_report` → `test-coverage-report`
- `My Test File` → `my-test-file`

---

## 🔍 Validation Integration Points

### 1. BaseOrchestrator File Creation
```python
class BaseOrchestrator:
    def create_artifact(self, type: str, content: str, name: str) -> str:
        # Validate before creation
        is_valid, error = validate_filename(name)
        if not is_valid:
            suggested = suggest_filename(name)
            logger.warning(f"Invalid filename '{name}': {error}. Using '{suggested}'")
            name = suggested
        
        # Create file
        path = self.write_file(name, content)
        
        # Track in database
        self.db.create_artifact(self.plan_id, path, type)
        
        return path
```

### 2. Database Constraint
```sql
CREATE TABLE artifacts (
    artifact_id TEXT PRIMARY KEY,
    plan_id TEXT REFERENCES plans(plan_id),
    file_path TEXT NOT NULL,
    artifact_type TEXT,
    generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    size_bytes INTEGER,
    -- Filename validation constraint
    CONSTRAINT file_name_len CHECK(
        length(
            substr(
                file_path, 
                instr(file_path, '/') + 1,
                instr(substr(file_path, instr(file_path, '/') + 1), '.') - 1
            )
        ) <= 20
    ),
    CONSTRAINT file_name_format CHECK(
        substr(file_path, instr(file_path, '/') + 1)
        GLOB '[a-z0-9]*-[a-z0-9]*.[a-z]*'
    )
);
```

### 3. Pre-Commit Hook (Optional)
```bash
#!/bin/bash
# .git/hooks/pre-commit

# Find files violating naming convention
violations=$(find . -type f -name "*" | python3 -c "
import sys
import os
import re

max_len = 20
pattern = r'^[a-z0-9]+(-[a-z0-9]+)*$'

for line in sys.stdin:
    filepath = line.strip()
    filename = os.path.basename(filepath)
    name, ext = os.path.splitext(filename)
    
    if len(name) > max_len or not re.match(pattern, name):
        print(filepath)
")

if [ -n "$violations" ]; then
    echo "ERROR: Files violate naming convention:"
    echo "$violations"
    exit 1
fi
```

---

## 📊 Monitoring & Reporting

### Weekly Compliance Audit
```python
def audit_filename_compliance(root_dir: str) -> dict:
    """Scan all files and check compliance"""
    
    results = {
        'total_files': 0,
        'compliant': 0,
        'violations': []
    }
    
    for root, dirs, files in os.walk(root_dir):
        for filename in files:
            results['total_files'] += 1
            
            is_valid, error = validate_filename(filename)
            if is_valid:
                results['compliant'] += 1
            else:
                suggested = suggest_filename(filename)
                results['violations'].append({
                    'path': os.path.join(root, filename),
                    'error': error,
                    'suggested': suggested
                })
    
    results['compliance_rate'] = (
        results['compliant'] / results['total_files'] * 100
        if results['total_files'] > 0 else 100
    )
    
    return results
```

### Compliance Report Template
```markdown
# Filename Compliance Report

**Date:** {date}  
**Scope:** {directory}

## Summary

- **Total Files:** {total_files}
- **Compliant:** {compliant}
- **Violations:** {violations}
- **Compliance Rate:** {compliance_rate}%

## Violations

{for violation in violations}
- **File:** `{violation.path}`
  - **Issue:** {violation.error}
  - **Suggested Fix:** `{violation.suggested}`
{endfor}

## Recommendations

{if compliance_rate < 100}
Run auto-fix script: `python scripts/fix_filenames.py`
{endif}
```

---

## 🚀 Implementation Checklist

### Phase 0: Foundation
- [ ] Create `src/utils/file_name.py` with validation functions
- [ ] Write unit tests (100% coverage)
- [ ] Document validation rules
- [ ] Create auto-fix utilities

### Phase 1-8: Orchestrator Integration
- [ ] Integrate validation in BaseOrchestrator
- [ ] Add database constraints
- [ ] Update file creation methods
- [ ] Add logging for violations

### Phase 9: Testing
- [ ] Test validation with valid names
- [ ] Test auto-fix with invalid names
- [ ] Test database constraints
- [ ] Run compliance audit

### Phase 10: Documentation
- [ ] Document rules in user guide
- [ ] Add examples to README
- [ ] Create troubleshooting guide
- [ ] Update contribution guidelines

### Phase 11: Enforcement
- [ ] Enable pre-commit hooks (optional)
- [ ] Schedule weekly audits
- [ ] Monitor compliance metrics
- [ ] Fix all existing violations

---

## 📚 Reference Examples
### Valid Filenames
```
mst-pure-autonomous.md  (20 chars) ✅ Master Plan
progress.json           (8 chars) ✅
db-schema.sql           (9 chars) ✅
test-cov.md             (8 chars) ✅
arch.md                 (4 chars) ✅
plan-sys-5.yaml         (11 chars) ✅
```n-sys-5.yaml        (11 chars) ✅
```

### Invalid → Fixed
```
comprehensive-architecture-analysis.md  (37 chars) ❌
→ arch-analyze.md                       (12 chars) ✅

00-master-plan.md                       (14 chars, missing mst- prefix) ❌
→ mst-pure-autonomous.md                (20 chars) ✅

database_migration_script.py            (24 chars, snake_case) ❌
→ db-migrate-script.py                  (17 chars) ✅

TestCoverageReport.json                 (18 chars, PascalCase) ❌
→ test-cov-report.json                  (15 chars) ✅
```

---

## 🎯 Success Criteria

- ✅ 100% of new files comply with rules
- ✅ All orchestrators validate filenames before creation
- ✅ Database constraints prevent invalid names
- ✅ Violations auto-fixed with suggestions
- ✅ Weekly compliance rate ≥99%
- ✅ Zero manual filename corrections needed

---

**Status:** 🟢 ENFORCED  
**Compliance Target:** 100%  
**Review Frequency:** Weekly
