# CORTEX 2.0 Knowledge Boundary System

**Document:** 05-knowledge-boundaries.md  
**Version:** 2.0.0-alpha  
**Date:** 2025-11-07

---

## 🎯 Purpose

Enforce strict separation between core CORTEX knowledge and project-specific knowledge to:
- Prevent core intelligence contamination
- Enable surgical knowledge deletion
- Maintain CORTEX portability across projects
- Ensure knowledge quality and relevance
- Protect core patterns from project-specific bloat

---

## ❌ Current Pain Points (CORTEX 1.0)

### Problem 1: Knowledge Contamination
```yaml
# ❌ Tier 2 knowledge_graph.yaml (mixed knowledge)
patterns:
  - title: "TDD: Test-first service creation"
    scope: "generic"  # ✅ Core CORTEX pattern
    
  - title: "KSESSIONS: Invoice export workflow"
    scope: "application"  # ⚠️ Project-specific in core brain
    
  - title: "NOOR: Purple button animation"
    scope: "application"  # ⚠️ Another project contaminating brain
```

**Issue:** Application patterns stored alongside core patterns, making CORTEX brain project-dependent.

### Problem 2: No Surgical Deletion
```
Question: "Delete all KSESSIONS knowledge"
Current approach:
  ❌ Must manually find and remove KSESSIONS entries
  ❌ Risk deleting core patterns accidentally
  ❌ No guarantee all project data removed
```

### Problem 3: Namespace Confusion
```yaml
# ❌ Pattern without clear namespace
pattern:
  title: "Add export button"
  # Is this:
  # - Generic UI pattern? (CORTEX core)
  # - KSESSIONS-specific? (project)
  # - NOOR-specific? (different project)
  # No way to tell!
```

### Problem 4: Scope Drift
```yaml
# ❌ Application data creeping into Tier 0 (INSTINCT)
file: cortex-brain/tier0/ksessions-patterns.yaml
# Tier 0 is IMMUTABLE core rules
# Application patterns DO NOT belong here!
```

---

## ✅ CORTEX 2.0 Solution

### Architecture Overview

```
┌──────────────────────────────────────────────────────────┐
│          Knowledge Boundary Enforcer (NEW)                │
├──────────────────────────────────────────────────────────┤
│  • Validates scope/namespace on every write              │
│  • Auto-detects violations                               │
│  • Auto-migrates misplaced knowledge                     │
│  • Prevents Tier 0 contamination                         │
│  • Enables surgical deletion by namespace                │
└────────────────────┬─────────────────────────────────────┘
                     │
         ┌───────────┴───────────┐
         │                       │
    ┌────▼─────────┐      ┌─────▼──────────┐
    │ Core Knowledge│      │Project Knowledge│
    ├───────────────┤      ├─────────────────┤
    │ Scope: generic│      │Scope: application│
    │ Namespace:    │      │Namespace:       │
    │  CORTEX-core  │      │  KSESSIONS      │
    │               │      │  NOOR           │
    │ • TDD         │      │  my-app         │
    │ • SOLID       │      │                 │
    │ • Refactoring │      │• Feature flows  │
    │ • Testing     │      │• UI components  │
    │ • Architecture│      │• Business logic │
    └───────────────┘      └─────────────────┘
         │                       │
         └───────────┬───────────┘
                     │
         ┌───────────▼──────────────┐
         │  Tier 2 Database (NEW)   │
         │  + scope column          │
         │  + namespaces column     │
         │  + project_id column     │
         └──────────────────────────┘
```

---

## 🗄️ Enhanced Database Schema

### Updated: patterns table (Tier 2)

```sql
CREATE TABLE patterns (
    pattern_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    pattern_type TEXT NOT NULL,
    
    -- NEW: Knowledge boundary fields
    scope TEXT NOT NULL CHECK(scope IN ('generic', 'application', 'experimental')),
    namespaces TEXT NOT NULL,  -- JSON array: ["CORTEX-core"] or ["KSESSIONS", "NOOR"]
    project_id TEXT,           -- Optional: explicit project ID
    
    -- Pattern data
    pattern_data TEXT NOT NULL,
    confidence REAL DEFAULT 0.5,
    usage_count INTEGER DEFAULT 0,
    
    -- Metadata
    created_at TIMESTAMP NOT NULL,
    last_used TIMESTAMP,
    
    -- Validation
    validated BOOLEAN DEFAULT 0,
    validation_notes TEXT,
    
    -- Constraints
    CONSTRAINT valid_scope CHECK (
        (scope = 'generic' AND namespaces LIKE '%CORTEX-core%') OR
        (scope = 'application' AND namespaces NOT LIKE '%CORTEX-core%') OR
        (scope = 'experimental')
    )
);

-- Indexes for boundary queries
CREATE INDEX idx_patterns_scope ON patterns(scope);
CREATE INDEX idx_patterns_project ON patterns(project_id);
CREATE INDEX idx_patterns_validated ON patterns(validated);
```

### Updated: file_relationships table (Tier 2)

```sql
CREATE TABLE file_relationships (
    relationship_id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path_1 TEXT NOT NULL,
    file_path_2 TEXT NOT NULL,
    relationship_type TEXT NOT NULL,
    
    -- NEW: Knowledge boundary fields
    scope TEXT NOT NULL CHECK(scope IN ('generic', 'application')),
    project_id TEXT,
    
    -- Relationship data
    co_modification_count INTEGER DEFAULT 1,
    confidence REAL DEFAULT 0.5,
    
    -- Timestamps
    first_seen TIMESTAMP NOT NULL,
    last_seen TIMESTAMP NOT NULL,
    
    UNIQUE(file_path_1, file_path_2, relationship_type)
);

CREATE INDEX idx_file_relationships_scope ON file_relationships(scope);
CREATE INDEX idx_file_relationships_project ON file_relationships(project_id);
```

---

## 🏗️ Implementation: Boundary Enforcer

```python
# src/maintenance/knowledge_validator.py

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum
import json
import re

class KnowledgeScope(Enum):
    """Knowledge scope types"""
    GENERIC = "generic"          # Universal CORTEX patterns
    APPLICATION = "application"  # Project-specific patterns
    EXPERIMENTAL = "experimental" # Testing/learning patterns

@dataclass
class BoundaryViolation:
    """Represents a boundary violation"""
    violation_type: str
    severity: str  # critical, warning, info
    item_id: str
    item_type: str  # pattern, file_relationship, etc.
    current_scope: str
    current_namespaces: List[str]
    expected_scope: str
    expected_namespaces: List[str]
    reason: str
    auto_fixable: bool
    
class KnowledgeBoundaryEnforcer:
    """Enforces knowledge boundaries across the brain"""
    
    # Core namespace - the heart of CORTEX
    CORE_NAMESPACE = "CORTEX-core"
    
    # Tier 0 is IMMUTABLE - no application data allowed
    TIER0_ALLOWED_SCOPES = [KnowledgeScope.GENERIC]
    
    def __init__(self, path_resolver, db_connections):
        self.paths = path_resolver
        self.tier2_db = db_connections['tier2']
        self.violations: List[BoundaryViolation] = []
    
    def validate_pattern(self, 
                        pattern: Dict[str, Any],
                        auto_fix: bool = False) -> bool:
        """
        Validate a pattern's scope and namespaces
        
        Args:
            pattern: Pattern dictionary
            auto_fix: If True, attempt to fix violations
        
        Returns:
            True if valid or fixed, False if violation remains
        """
        pattern_id = pattern.get('pattern_id')
        title = pattern.get('title', '')
        scope = pattern.get('scope')
        namespaces = json.loads(pattern.get('namespaces', '[]'))
        
        # Validation 1: Core namespace requires generic scope
        if self.CORE_NAMESPACE in namespaces:
            if scope != KnowledgeScope.GENERIC.value:
                violation = BoundaryViolation(
                    violation_type="core_namespace_non_generic",
                    severity="critical",
                    item_id=pattern_id,
                    item_type="pattern",
                    current_scope=scope,
                    current_namespaces=namespaces,
                    expected_scope=KnowledgeScope.GENERIC.value,
                    expected_namespaces=[self.CORE_NAMESPACE],
                    reason=f"Pattern '{title}' uses CORTEX-core namespace but scope is '{scope}' (must be 'generic')",
                    auto_fixable=True
                )
                self.violations.append(violation)
                
                if auto_fix:
                    return self._fix_scope_mismatch(pattern_id, KnowledgeScope.GENERIC.value)
                return False
        
        # Validation 2: Application scope cannot use core namespace
        if scope == KnowledgeScope.APPLICATION.value:
            if self.CORE_NAMESPACE in namespaces:
                violation = BoundaryViolation(
                    violation_type="application_in_core_namespace",
                    severity="critical",
                    item_id=pattern_id,
                    item_type="pattern",
                    current_scope=scope,
                    current_namespaces=namespaces,
                    expected_scope=KnowledgeScope.APPLICATION.value,
                    expected_namespaces=[ns for ns in namespaces if ns != self.CORE_NAMESPACE],
                    reason=f"Application pattern '{title}' cannot use CORTEX-core namespace",
                    auto_fixable=True
                )
                self.violations.append(violation)
                
                if auto_fix:
                    return self._remove_core_namespace(pattern_id)
                return False
        
        # Validation 3: Detect application-specific content in generic patterns
        if scope == KnowledgeScope.GENERIC.value:
            if self._contains_application_markers(title, pattern.get('description', '')):
                violation = BoundaryViolation(
                    violation_type="application_content_in_generic",
                    severity="warning",
                    item_id=pattern_id,
                    item_type="pattern",
                    current_scope=scope,
                    current_namespaces=namespaces,
                    expected_scope=KnowledgeScope.APPLICATION.value,
                    expected_namespaces=self._detect_project_namespace(title),
                    reason=f"Pattern '{title}' appears to be application-specific but marked as generic",
                    auto_fixable=True
                )
                self.violations.append(violation)
                
                if auto_fix:
                    project_ns = self._detect_project_namespace(title)
                    return self._migrate_to_application_scope(pattern_id, project_ns)
                return False
        
        return True
    
    def validate_tier0_integrity(self) -> List[BoundaryViolation]:
        """
        Validate that Tier 0 contains ONLY core CORTEX patterns
        
        Returns:
            List of violations found
        """
        tier0_violations = []
        tier0_path = self.paths.resolve_brain_path("tier0")
        
        # Scan all YAML files in Tier 0
        for yaml_file in tier0_path.glob("*.yaml"):
            # Check filename for application markers
            filename = yaml_file.stem.lower()
            
            if self._is_application_filename(filename):
                violation = BoundaryViolation(
                    violation_type="application_file_in_tier0",
                    severity="critical",
                    item_id=str(yaml_file),
                    item_type="file",
                    current_scope="tier0",
                    current_namespaces=[],
                    expected_scope="tier2",
                    expected_namespaces=[self._extract_project_from_filename(filename)],
                    reason=f"Application file '{filename}.yaml' found in Tier 0 (IMMUTABLE core)",
                    auto_fixable=True
                )
                tier0_violations.append(violation)
        
        return tier0_violations
    
    def surgical_delete_project(self, project_id: str) -> Dict[str, int]:
        """
        Delete ALL knowledge for a specific project
        
        Args:
            project_id: Project identifier (e.g., "KSESSIONS")
        
        Returns:
            Dictionary with counts of deleted items by type
        """
        deleted = {
            "patterns": 0,
            "file_relationships": 0,
            "workflows": 0,
            "intent_patterns": 0
        }
        
        with self.tier2_db.connection() as conn:
            # Delete patterns
            cursor = conn.execute("""
                DELETE FROM patterns
                WHERE project_id = ? OR namespaces LIKE ?
            """, (project_id, f'%{project_id}%'))
            deleted["patterns"] = cursor.rowcount
            
            # Delete file relationships
            cursor = conn.execute("""
                DELETE FROM file_relationships
                WHERE project_id = ?
            """, (project_id,))
            deleted["file_relationships"] = cursor.rowcount
            
            # Delete workflows
            cursor = conn.execute("""
                DELETE FROM workflow_patterns
                WHERE project_id = ?
            """, (project_id,))
            deleted["workflows"] = cursor.rowcount
            
            # Delete intent patterns
            cursor = conn.execute("""
                DELETE FROM intent_patterns
                WHERE namespaces LIKE ?
            """, (f'%{project_id}%',))
            deleted["intent_patterns"] = cursor.rowcount
            
            conn.commit()
        
        return deleted
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """
        Get all projects in the knowledge base
        
        Returns:
            List of projects with statistics
        """
        projects = []
        
        with self.tier2_db.connection() as conn:
            # Query distinct project IDs
            cursor = conn.execute("""
                SELECT DISTINCT project_id, COUNT(*) as pattern_count
                FROM patterns
                WHERE project_id IS NOT NULL
                GROUP BY project_id
                ORDER BY pattern_count DESC
            """)
            
            for row in cursor:
                project_id = row[0]
                
                # Get additional stats
                stats = self._get_project_stats(conn, project_id)
                
                projects.append({
                    "project_id": project_id,
                    "patterns": stats["patterns"],
                    "file_relationships": stats["file_relationships"],
                    "workflows": stats["workflows"],
                    "total_items": stats["total"],
                    "last_updated": stats["last_updated"]
                })
        
        return projects
    
    def auto_migrate_violations(self) -> Dict[str, int]:
        """
        Automatically fix all auto-fixable violations
        
        Returns:
            Count of fixes by violation type
        """
        # Run full validation
        self.validate_all()
        
        fixes = {}
        
        for violation in self.violations:
            if violation.auto_fixable:
                success = self._apply_fix(violation)
                if success:
                    fixes[violation.violation_type] = fixes.get(violation.violation_type, 0) + 1
        
        return fixes
    
    def validate_all(self) -> List[BoundaryViolation]:
        """
        Run comprehensive boundary validation
        
        Returns:
            List of all violations found
        """
        self.violations = []
        
        # Validate Tier 0 integrity
        self.violations.extend(self.validate_tier0_integrity())
        
        # Validate all patterns
        with self.tier2_db.connection() as conn:
            cursor = conn.execute("SELECT * FROM patterns")
            for row in cursor:
                pattern = dict(row)
                self.validate_pattern(pattern, auto_fix=False)
        
        # Validate file relationships
        # (similar validation for other tables)
        
        return self.violations
    
    def generate_report(self) -> str:
        """Generate human-readable validation report"""
        report = ["=" * 60]
        report.append("KNOWLEDGE BOUNDARY VALIDATION REPORT")
        report.append("=" * 60)
        report.append("")
        
        if not self.violations:
            report.append("✅ No violations found! Knowledge boundaries are clean.")
            return "\n".join(report)
        
        # Group by severity
        critical = [v for v in self.violations if v.severity == "critical"]
        warnings = [v for v in self.violations if v.severity == "warning"]
        
        if critical:
            report.append(f"❌ CRITICAL VIOLATIONS: {len(critical)}")
            report.append("-" * 60)
            for v in critical[:5]:  # Show first 5
                report.append(f"  • {v.reason}")
            if len(critical) > 5:
                report.append(f"  ... and {len(critical) - 5} more")
            report.append("")
        
        if warnings:
            report.append(f"⚠️  WARNINGS: {len(warnings)}")
            report.append("-" * 60)
            for v in warnings[:5]:  # Show first 5
                report.append(f"  • {v.reason}")
            if len(warnings) > 5:
                report.append(f"  ... and {len(warnings) - 5} more")
            report.append("")
        
        # Auto-fix summary
        auto_fixable = [v for v in self.violations if v.auto_fixable]
        report.append(f"🔧 AUTO-FIXABLE: {len(auto_fixable)}/{len(self.violations)}")
        report.append("")
        report.append("Run with --auto-fix to automatically resolve fixable issues.")
        
        return "\n".join(report)
    
    # Helper methods
    
    def _contains_application_markers(self, title: str, description: str) -> bool:
        """Detect if content contains application-specific markers"""
        # Common application-specific markers
        app_markers = [
            r'\bKSESSIONS\b', r'\bNOOR\b', r'\bInvoice\b', r'\bReceipt\b',
            r'\bHost\b.*\bPanel\b', r'\bRegistration\b', r'\bLogin\b',
            r'\bDashboard\b', r'\bAPI\b.*\bEndpoint\b'
        ]
        
        text = f"{title} {description}".lower()
        for pattern in app_markers:
            if re.search(pattern, text, re.IGNORECASE):
                return True
        return False
    
    def _detect_project_namespace(self, title: str) -> List[str]:
        """Attempt to detect project namespace from content"""
        title_upper = title.upper()
        
        if "KSESSIONS" in title_upper:
            return ["KSESSIONS"]
        elif "NOOR" in title_upper:
            return ["NOOR"]
        elif any(word in title_upper for word in ["INVOICE", "RECEIPT", "SESSION"]):
            return ["KSESSIONS"]  # Common KSESSIONS terms
        
        return ["unknown-project"]
    
    def _is_application_filename(self, filename: str) -> bool:
        """Check if filename suggests application-specific content"""
        app_indicators = ["ksessions", "noor", "invoice", "receipt", "login"]
        filename_lower = filename.lower()
        return any(indicator in filename_lower for indicator in app_indicators)
    
    def _extract_project_from_filename(self, filename: str) -> str:
        """Extract project name from filename"""
        filename_upper = filename.upper()
        if "KSESSIONS" in filename_upper:
            return "KSESSIONS"
        elif "NOOR" in filename_upper:
            return "NOOR"
        return "unknown-project"
    
    def _fix_scope_mismatch(self, pattern_id: str, correct_scope: str) -> bool:
        """Fix scope mismatch"""
        with self.tier2_db.connection() as conn:
            conn.execute("""
                UPDATE patterns
                SET scope = ?
                WHERE pattern_id = ?
            """, (correct_scope, pattern_id))
            conn.commit()
        return True
    
    def _remove_core_namespace(self, pattern_id: str) -> bool:
        """Remove CORTEX-core from namespaces"""
        with self.tier2_db.connection() as conn:
            cursor = conn.execute("""
                SELECT namespaces FROM patterns WHERE pattern_id = ?
            """, (pattern_id,))
            row = cursor.fetchone()
            
            if row:
                namespaces = json.loads(row[0])
                namespaces = [ns for ns in namespaces if ns != self.CORE_NAMESPACE]
                
                conn.execute("""
                    UPDATE patterns
                    SET namespaces = ?
                    WHERE pattern_id = ?
                """, (json.dumps(namespaces), pattern_id))
                conn.commit()
                return True
        return False
    
    def _migrate_to_application_scope(self, pattern_id: str, namespaces: List[str]) -> bool:
        """Migrate pattern to application scope"""
        with self.tier2_db.connection() as conn:
            conn.execute("""
                UPDATE patterns
                SET scope = ?,
                    namespaces = ?,
                    project_id = ?
                WHERE pattern_id = ?
            """, (
                KnowledgeScope.APPLICATION.value,
                json.dumps(namespaces),
                namespaces[0] if namespaces else None,
                pattern_id
            ))
            conn.commit()
        return True
    
    def _apply_fix(self, violation: BoundaryViolation) -> bool:
        """Apply fix for a specific violation"""
        if violation.violation_type == "application_file_in_tier0":
            # Move file from Tier 0 to appropriate location
            return self._move_file_out_of_tier0(violation.item_id)
        elif violation.violation_type == "core_namespace_non_generic":
            return self._fix_scope_mismatch(violation.item_id, violation.expected_scope)
        elif violation.violation_type == "application_in_core_namespace":
            return self._remove_core_namespace(violation.item_id)
        elif violation.violation_type == "application_content_in_generic":
            return self._migrate_to_application_scope(
                violation.item_id, 
                violation.expected_namespaces
            )
        return False
    
    def _move_file_out_of_tier0(self, file_path: str) -> bool:
        """Move file from Tier 0 to Tier 2"""
        # Implementation: move file, update references
        # (Details omitted for brevity)
        return True
    
    def _get_project_stats(self, conn, project_id: str) -> Dict[str, Any]:
        """Get statistics for a project"""
        # Implementation: query various tables for project stats
        # (Details omitted for brevity)
        return {
            "patterns": 0,
            "file_relationships": 0,
            "workflows": 0,
            "total": 0,
            "last_updated": None
        }
```

---

## 🔌 Integration with Brain Protector

```python
# src/cortex_agents/brain_protector.py (Enhanced)

class BrainProtector:
    def __init__(self, boundary_enforcer: KnowledgeBoundaryEnforcer):
        self.boundary_enforcer = boundary_enforcer
    
    def challenge_pattern_addition(self, pattern: Dict[str, Any]) -> Optional[str]:
        """Challenge pattern addition if it violates boundaries"""
        
        # Validate boundaries
        is_valid = self.boundary_enforcer.validate_pattern(pattern, auto_fix=False)
        
        if not is_valid:
            violations = [v for v in self.boundary_enforcer.violations 
                         if v.item_id == pattern['pattern_id']]
            
            if violations:
                v = violations[0]
                
                challenge = f"""
═══════════════════════════════════════════════
🧠 BRAIN PROTECTION CHALLENGE

Attempted Action: Add pattern to Tier 2
Pattern: {pattern['title']}

⚠️ BOUNDARY VIOLATION DETECTED:
  Type: {v.violation_type}
  Severity: {v.severity.upper()}
  
  Current: scope={v.current_scope}, namespaces={v.current_namespaces}
  Expected: scope={v.expected_scope}, namespaces={v.expected_namespaces}
  
  Reason: {v.reason}

SAFE ALTERNATIVES:
1. Use scope='{v.expected_scope}' and namespaces={v.expected_namespaces} ✅ RECOMMENDED
2. Mark as experimental for testing
3. Store in project-specific location

RECOMMENDATION: Alternative 1

═══════════════════════════════════════════════
This challenge protects CORTEX brain integrity (Rule #22).

Options:
  1. Accept recommended alternative (SAFE)
  2. Provide different approach (REVIEW)
  3. Type 'OVERRIDE' with justification (RISKY)

Your choice:
"""
                return challenge
        
        return None  # No challenge needed
```

---

## 📊 CLI Commands

```bash
# Validate boundaries
python scripts/cortex-boundary-check.py

# Validate with auto-fix
python scripts/cortex-boundary-check.py --auto-fix

# List all projects
python scripts/cortex-boundary-check.py --list-projects

# Delete project knowledge
python scripts/cortex-boundary-check.py --delete-project KSESSIONS

# Generate detailed report
python scripts/cortex-boundary-check.py --report --output report.txt
```

---

## ✅ Benefits

### 1. Clean Core Knowledge
```yaml
# CORTEX-core namespace - pure, portable patterns
- "TDD: Test-first service creation"
- "SOLID: Single Responsibility Principle"
- "Refactoring: Extract method pattern"
- "Architecture: Three-tier separation"

# NO application-specific contamination ✅
```

### 2. Surgical Project Deletion
```bash
# Delete KSESSIONS, keep CORTEX core intact
$ python scripts/cortex-boundary-check.py --delete-project KSESSIONS

Deleted:
  - 47 patterns
  - 89 file relationships
  - 12 workflow templates
  - 23 intent patterns

✅ CORTEX core knowledge unchanged
```

### 3. Project Isolation
```
Working on NOOR project:
  - NOOR patterns boosted 2x
  - CORTEX-core patterns boosted 1.5x
  - KSESSIONS patterns boosted 0.5x (low relevance)

Clear boundaries = better search results
```

### 4. Portability
```
CORTEX moving to new project:
  ✅ Core knowledge transfers perfectly
  ✅ Old project knowledge stays isolated
  ✅ No cleanup needed
```

---

## 🧪 Validation Scenarios

### Scenario 1: Application File in Tier 0
```yaml
# ❌ VIOLATION
File: cortex-brain/tier0/ksessions-patterns.yaml
Severity: CRITICAL
Reason: Application-specific file in IMMUTABLE Tier 0

Auto-fix:
  1. Move file to tier2/applications/ksessions/
  2. Update scope to "application"
  3. Add namespace: ["KSESSIONS"]
```

### Scenario 2: Generic Pattern with App Content
```yaml
# ❌ VIOLATION
Pattern:
  title: "KSESSIONS: Invoice export workflow"
  scope: "generic"  # ← Wrong!
  namespaces: ["CORTEX-core"]  # ← Wrong!

Auto-fix:
  scope: "application"
  namespaces: ["KSESSIONS"]
  project_id: "KSESSIONS"
```

### Scenario 3: Mixed Namespace
```yaml
# ❌ VIOLATION
Pattern:
  scope: "application"
  namespaces: ["CORTEX-core", "KSESSIONS"]  # ← Can't mix!

Auto-fix:
  Remove "CORTEX-core" from namespaces
  Keep: ["KSESSIONS"]
```

---

## 🔄 Migration Process

### Step 1: Initial Validation
```bash
python scripts/cortex-boundary-check.py --report
```

### Step 2: Review Violations
```
Found 23 violations:
  - 5 critical (Tier 0 contamination)
  - 18 warnings (scope mismatches)
  
All 23 are auto-fixable
```

### Step 3: Apply Fixes
```bash
python scripts/cortex-boundary-check.py --auto-fix
```

### Step 4: Verify Clean
```bash
python scripts/cortex-boundary-check.py

✅ No violations found! Knowledge boundaries are clean.
```

---

**Next:** 06-documentation-system.md (Auto-refresh MkDocs with duplicate detection)
