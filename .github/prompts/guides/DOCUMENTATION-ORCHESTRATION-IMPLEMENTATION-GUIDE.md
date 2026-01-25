# CORTEX Documentation Orchestration - Implementation Guide

**Authority:** cortex-doc.prompt.md | **Status:** Implementation Guide

---

## 🎯 Overview

This guide provides implementation details for the refactored `cortex-doc.prompt.md` which now includes:
1. **Diagram Generation System** - Automated Mermaid & D3.js diagram creation
2. **Documentation Cleanup Cycle** - Automated redundancy detection and removal
3. **Full Maintenance Orchestration** - Complete doc lifecycle automation

---

## Part 1: Diagram Generation System

### Directory Structure

```
docs/
├── 04-architecture/
│   ├── _diagrams/
│   │   ├── approval-gate-decision-tree.mmd
│   │   ├── error-recovery-paths.mmd
│   │   ├── circuit-breaker-state-machine.mmd
│   │   ├── tdd-workflow-phases.mmd
│   │   └── governance-rule-categories.mmd
│   ├── DIAGRAM-VISUALIZATION-RECOMMENDATIONS.md
│   └── DIAGRAM-EXAMPLES-IMPLEMENTATION-GUIDE.md
│
├── 02-orchestrators/
│   └── diagrams/
│       └── master-orchestrator-sequence.mmd
│
└── _diagrams/
    └── d3/
        ├── governance-pyramid.html
        ├── governance-pyramid-data.json
        ├── request-lifecycle-sankey.html
        ├── request-lifecycle-data.json
        ├── tdd-knowledge-cycle.html
        ├── domain-brain-architecture.html
        ├── styles.css
        └── data-generators/
            ├── generate-governance-data.py
            ├── generate-lifecycle-data.py
            └── generate-tdd-data.py
```

### Mermaid Diagram Generation

The refactored prompt defines 6 core Mermaid diagrams:

#### 1. Approval Gate Decision Tree
**File:** `docs/04-architecture/_diagrams/approval-gate-decision-tree.mmd`
**Purpose:** Visualize complexity scoring and approval logic
**Already Available:** Yes (in DIAGRAM-EXAMPLES-IMPLEMENTATION-GUIDE.md)

#### 2. Error Recovery Paths
**File:** `docs/04-architecture/_diagrams/error-recovery-paths.mmd`
**Purpose:** Show transient/persistent/partial/critical error handling
**Already Available:** Yes (in DIAGRAM-EXAMPLES-IMPLEMENTATION-GUIDE.md)

#### 3. Circuit Breaker State Machine
**File:** `docs/04-architecture/_diagrams/circuit-breaker-state-machine.mmd`
**Purpose:** Visualize CLOSED → OPEN → HALF_OPEN transitions
**Template:** Use Mermaid `stateDiagram-v2`

#### 4. Master Orchestrator Sequence
**File:** `docs/02-orchestrators/diagrams/master-orchestrator-sequence.mmd`
**Purpose:** Show turn-by-turn execution protocol
**Already Available:** Yes (in DIAGRAM-EXAMPLES-IMPLEMENTATION-GUIDE.md)

#### 5. TDD Workflow Phases
**File:** `docs/04-architecture/_diagrams/tdd-workflow-phases.mmd`
**Purpose:** Show RED → GREEN → REFACTOR with knowledge injection
**Type:** Flowchart with circular flow

#### 6. Governance Rule Categories
**File:** `docs/04-architecture/_diagrams/governance-rule-categories.mmd`
**Purpose:** Organize 29 CORE rules by category
**Type:** Graph/mindmap

### D3.js Visualization Generation

#### Data Generation Workflow

```python
#!/usr/bin/env python3
"""Generate data for D3.js visualizations."""

import json
import sys
from pathlib import Path

class DocumentationDataGenerator:
    """Generate data for D3.js visualizations from codebase."""
    
    def generate_governance_pyramid_data(self) -> dict:
        """Generate 29 CORE rules organized by tier."""
        return {
            "tiers": [
                {
                    "tier": 0,
                    "name": "CORE Rules",
                    "categories": [
                        {
                            "name": "Orchestration",
                            "rules": ["CORE-001", "CORE-006", "CORE-007", "CORE-010"]
                        },
                        # ... more categories
                    ]
                }
            ]
        }
    
    def generate_request_lifecycle_data(self) -> dict:
        """Generate request flow data for Sankey diagram."""
        return {
            "stages": [
                {"id": "entry", "name": "Entry Point"},
                {"id": "auth", "name": "Authentication"},
                # ... more stages
            ],
            "flows": [
                {"source": "entry", "target": "auth", "value": 100},
                # ... more flows
            ]
        }
    
    def generate_tdd_workflow_data(self) -> dict:
        """Generate TDD workflow with knowledge injection."""
        return {
            "phases": [
                {
                    "name": "RED",
                    "knowledge_applied": ["test-patterns", "ac-ids"],
                    "duration": "30 minutes"
                },
                {
                    "name": "GREEN",
                    "knowledge_applied": [],
                    "duration": "45 minutes"
                },
                {
                    "name": "REFACTOR",
                    "knowledge_applied": ["best-practices", "solid-principles"],
                    "duration": "30 minutes"
                }
            ]
        }

def main():
    generator = DocumentationDataGenerator()
    
    # Generate all data files
    data_files = {
        "governance-pyramid-data.json": generator.generate_governance_pyramid_data(),
        "request-lifecycle-data.json": generator.generate_request_lifecycle_data(),
        "tdd-knowledge-cycle-data.json": generator.generate_tdd_workflow_data(),
    }
    
    output_dir = Path("docs/_diagrams/d3")
    for filename, data in data_files.items():
        filepath = output_dir / filename
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)
        print(f"✅ Generated {filename}")

if __name__ == "__main__":
    main()
```

#### Integration with mkdocs.yml

```yaml
# mkdocs.yml
plugins:
  - search
  - mermaid2:
      arguments:
        theme: default
        flowchart:
          curve: linear

nav:
  - Architecture:
      - Diagrams & Visualizations:
          - Overview: 04-architecture/DIAGRAM-VISUALIZATION-RECOMMENDATIONS.md
          - Governance Pyramid: _diagrams/d3/governance-pyramid.html
          - Request Lifecycle: _diagrams/d3/request-lifecycle-sankey.html
          - TDD Workflow: _diagrams/d3/tdd-knowledge-cycle.html
          - Domain Brain: _diagrams/d3/domain-brain-architecture.html
          - Implementation Guide: 04-architecture/DIAGRAM-EXAMPLES-IMPLEMENTATION-GUIDE.md
```

---

## Part 2: Documentation Cleanup Cycle

### Cleanup Detection Rules

The prompt defines comprehensive rules for identifying files to clean up:

#### 1. Duplicate Component Documentation
```yaml
Pattern: Same component in multiple files
Examples:
  - "orchestrators/master-orchestrator.md + 02-orchestrators/01-master-orchestrator.md"
  - "CORTEX-MASTER-ORCHESTRATOR-v1.md + CORTEX-MASTER-ORCHESTRATOR-v2.md"
Action: CONSOLIDATE - keep canonical, archive others
```

#### 2. Completion Reports
```yaml
Pattern: "*-REPORT.md, *-SUMMARY.md, *-COMPLETE.md"
Examples:
  - "PHASE2-COMPLETION-REPORT.md"
  - "BRT-017-COMPLETION-REPORT.md"
  - "SESSION-SUMMARY-2026-01-24.md"
Action: ARCHIVE older versions to _archive/reports/
Keep: Latest version only
```

#### 3. Session Notes
```yaml
Pattern: "SESSION-*.md, BRT-*.md, PHASE*-*.md"
Examples:
  - "SESSION-SUMMARY-2026-01-24-PHASE-2-COMPLETE.md"
  - "BRT-017-COMPLETION-REPORT.md"
Action: ARCHIVE to _archive/sessions/{date}/ after one month
Keep: Current session only
```

#### 4. Intermediate Files
```yaml
Pattern: "DRY-RUN-*.md, TEST-*.md, *-VALIDATION.md"
Examples:
  - "VACUUM-DRY-RUN-COMPLETE.md"
  - "DRY-RUN-VALIDATION-REPORT.md"
Action: REMOVE if not referenced in primary docs
```

#### 5. Duplicate Diagrams
```yaml
Pattern: Same diagram in multiple locations
Action: Keep canonical location, remove duplicates
Examples:
  - Keep in _diagrams/, remove from individual doc folders
  - Consolidate similar error flow diagrams
```

#### 6. Obsolete Features
```yaml
Pattern: Documented features no longer in codebase
Action: ARCHIVE to _archive/obsolete/
Check: Scan for Python imports in cortex/ - if not found, likely obsolete
```

#### 7. Redundant Guidance
```yaml
Pattern: Multiple docs for same best practice
Examples:
  - Multiple TDD guides → Single authoritative guide
  - Multiple API design docs → Single API design guide
Action: CONSOLIDATE into single canonical doc
```

### Cleanup Execution

```python
class DocumentationCleanupOrchestrator:
    """Execute cleanup with safety guarantees."""
    
    def execute_cleanup_cycle(self, dry_run=True) -> CleanupReport:
        """Run cleanup cycle with full audit trail."""
        
        # Phase 1: Analysis
        redundancies = self._find_redundancies()
        orphans = self._find_orphaned_files()
        obsolete = self._find_obsolete_content()
        
        # Phase 2: Generate recommendations
        recommendations = self._generate_cleanup_plan(
            redundancies, orphans, obsolete
        )
        
        # Phase 3: Show to user
        report = self._generate_report(recommendations)
        print(report.to_markdown())
        
        if dry_run:
            print("\n⏸️  DRY RUN MODE - No changes made")
            print("Run with --confirm to execute cleanup")
            return report
        
        # Phase 4: Ask for confirmation
        if not self._get_user_confirmation(recommendations):
            print("❌ Cleanup cancelled by user")
            return report
        
        # Phase 5: Execute cleanup
        cleanup_results = self._execute_cleanup_plan(recommendations)
        
        # Phase 6: Validate
        validation = self._validate_cleanup(cleanup_results)
        
        # Phase 7: Commit & report
        self._git_commit(cleanup_results)
        
        return report
    
    def _find_redundancies(self) -> List[Redundancy]:
        """Identify duplicate and redundant files."""
        # Scan docs/ directory
        # Group by component
        # Find duplicates using similarity metrics
        # Return list of redundancies
        pass
    
    def _find_orphaned_files(self) -> List[str]:
        """Find files not referenced in mkdocs.yml or other docs."""
        referenced = self._extract_all_references()
        all_files = self._scan_all_doc_files()
        
        orphans = []
        for file in all_files:
            if not self._is_referenced(file, referenced):
                if not self._is_exception(file):
                    orphans.append(file)
        
        return orphans
    
    def _find_obsolete_content(self) -> List[ObsoleteItem]:
        """Find documentation for features no longer in codebase."""
        documented = self._extract_documented_components()
        existing = self._scan_codebase_components()
        
        obsolete = []
        for component in documented:
            if component not in existing:
                obsolete.append(
                    ObsoleteItem(
                        component=component,
                        files=self._find_docs_for(component),
                        reason="Not found in current codebase"
                    )
                )
        
        return obsolete
```

### Cleanup Report Structure

```markdown
# Documentation Cleanup Report - 2026-01-25

## Summary
| Metric | Count |
|--------|-------|
| **Redundancies Found** | 12 |
| **Orphaned Files** | 8 |
| **Obsolete Content** | 3 |
| **Space to Save** | 2.4 MB |
| **Files Affected** | 23 |

## Details by Category

### Redundancies (12 found)
1. **Orchestrator Documentation**
   - Files: `docs/orchestrators/master-orchestrator.md` + `docs/02-orchestrators/01-master-orchestrator.md`
   - Action: CONSOLIDATE
   - Space Saved: 45 KB

2. **TDD Documentation** (3 files)
   - Action: CONSOLIDATE to single authoritative guide
   - Space Saved: 128 KB

### Orphaned Files (8 found)
1. `docs/old-design-docs.md` - Not in mkdocs.yml
   - Action: ARCHIVE
   
2. `docs/temp-notes.md` - Not referenced
   - Action: REMOVE

### Obsolete Content (3 found)
1. `docs/deprecated-orchestrator.md`
   - Status: Feature removed from codebase
   - Action: ARCHIVE

## Recommendations
### HIGH PRIORITY
- [ ] Consolidate TDD documentation (saves 128 KB)
- [ ] Remove obsolete orchestrator docs (saves 32 KB)

### MEDIUM PRIORITY
- [ ] Archive session notes (saves 256 KB)
- [ ] Reorganize completion reports (saves 512 KB)

### LOW PRIORITY
- [ ] Archive old implementation notes (saves 128 KB)

## Commands to Execute
```bash
# Review cleanup plan
/doc-cleanup --analyze --report cleanup-report.md

# Execute cleanup (after confirmation)
/doc-cleanup --execute --plan cleanup-plan.yaml

# Verify build succeeds
mkdocs build

# Commit changes
git commit -m "docs: cleanup cycle - 2.4 MB freed"
```
```

---

## Part 3: Full Maintenance Orchestration

### Maintenance Cycle Workflow

The `/doc-maintenance` command runs a complete 5-phase cycle:

```
1. DISCOVERY (5-10 min)
   ├─ Scan cortex/ for new/modified components
   ├─ Identify missing documentation
   ├─ Generate inventory of what needs docs
   └─ Output: discovery-report.md

2. GENERATION (15-30 min)
   ├─ Generate component documentation
   ├─ Generate Mermaid diagrams
   ├─ Generate D3.js visualizations (with data)
   ├─ Update existing diagrams with latest data
   └─ Output: generated-docs/, generated-diagrams/

3. VALIDATION (10-20 min)
   ├─ Verify all components documented
   ├─ Check diagram links and rendering
   ├─ Build mkdocs site
   ├─ Validate no broken references
   └─ Output: validation-report.md

4. CLEANUP (30-60 min)
   ├─ Analyze redundancies
   ├─ Identify orphaned files
   ├─ Detect obsolete content
   ├─ Generate cleanup recommendations
   ├─ Present to user for approval
   └─ Output: cleanup-report.md

5. COMMIT & REPORT (5 min)
   ├─ Execute approved cleanup actions
   ├─ Create git commit
   ├─ Generate final summary report
   └─ Output: maintenance-complete-{date}.md
```

### Integration with CI/CD

```yaml
# .github/workflows/docs-maintenance.yml
name: Documentation Maintenance

on:
  schedule:
    - cron: '0 9 * * MON'  # Weekly on Monday mornings
  workflow_dispatch:  # Manual trigger

jobs:
  maintenance:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Run documentation maintenance cycle
        run: |
          # Would call CORTEX Documentation Orchestrator
          # /doc-maintenance --auto-cleanup --commit
          echo "Running full maintenance cycle..."
      
      - name: Upload reports
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: doc-maintenance-reports
          path: _workspaces/maintenance-reports/
      
      - name: Create PR for cleanup
        if: success()
        run: |
          # Create pull request with cleanup changes
          # for human review before merging
          echo "PR created with cleanup changes"
```

---

## Part 4: Usage Examples

### Generate Documentation Only
```bash
# Discover what's new
/doc-discover

# Generate docs for specific component
/doc-generate master-orchestrator --verbose

# Generate all component docs
/doc-generate --all

# Output: docs/02-orchestrators/, docs/04-architecture/, etc.
```

### Generate Diagrams Only
```bash
# Generate Mermaid diagrams
/doc-diagram mermaid --all

# Generate specific diagram
/doc-diagram mermaid --title="Approval Gate Decision Tree"

# Generate D3.js visualizations
/doc-diagram d3js --all

# Output: docs/_diagrams/
```

### Validate Documentation
```bash
# Check documentation completeness
/doc-status

# Validate all links and references
/doc-validate

# Output: validation-report.md
```

### Run Cleanup Cycle
```bash
# Analyze only (dry-run)
/doc-cleanup --analyze

# Show cleanup plan and recommendations
/doc-cleanup --report

# Execute cleanup (after user confirmation)
/doc-cleanup --execute

# Output: _workspaces/CLEANUP-REPORT-{date}.md
```

### Full Maintenance Cycle
```bash
# Run all phases with defaults
/doc-maintenance

# Run with auto-cleanup (skip approval)
/doc-maintenance --auto-cleanup

# Run with git commit
/doc-maintenance --commit

# Run with specific options
/doc-maintenance --discovery --generation --cleanup --commit
```

---

## Part 5: Safety & Validation

### Pre-Cleanup Validation
- ✅ Git working directory must be clean
- ✅ All files to be removed must be in version control
- ✅ mkdocs.yml must be valid
- ✅ At least one backup of each file being archived

### Post-Cleanup Validation
- ✅ mkdocs build succeeds
- ✅ No orphaned references in mkdocs.yml
- ✅ All internal links still valid
- ✅ _archive/ has all archived files

### Rollback Capability
```bash
# If cleanup goes wrong, rollback is simple:
git revert HEAD  # Undo cleanup commit

# All files return to previous state
# Archives stay in git history
```

---

## 📊 Expected Outputs

After running the refactored system, expect:

**Documentation Files:** ✅ (Already created)
- DIAGRAM-VISUALIZATION-RECOMMENDATIONS.md (18 KB)
- DIAGRAM-EXAMPLES-IMPLEMENTATION-GUIDE.md (18 KB)
- Specific component documentation

**Diagram Files:** 🔄 (To be generated)
- Mermaid: 6 diagrams in `_diagrams/`
- D3.js: 4 visualizations with data generators
- Styles and supporting files

**Reports:** 📊 (To be generated)
- Discovery report
- Generation report
- Validation report
- Cleanup report
- Final maintenance report

**Archive:** 📦 (To be populated)
- `_archive/reports/` - Old completion reports
- `_archive/sessions/` - Old session notes
- `_archive/obsolete/` - Removed features
- `_archive/temp/` - Temporary working files

---

**Status:** Implementation Guide for Refactored cortex-doc.prompt.md  
**Next Step:** Execute `/doc-maintenance` to generate diagrams and run cleanup cycle
