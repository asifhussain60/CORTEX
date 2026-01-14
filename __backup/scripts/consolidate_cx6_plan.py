#!/usr/bin/env python3
"""
CORTEX 6.0 Plan Consolidation Script
Moves all CX6-related files into cortex-brain/cx6-plan/ with proper organization
Includes plan-viewer files and validation documents

Author: GitHub Copilot following CORTEX governance
Version: 1.0.0
Date: 2026-01-11
"""

import shutil
import re
from pathlib import Path
from typing import List, Tuple

# Workspace root
WORKSPACE_ROOT = Path(__file__).parent.parent
CORTEX_BRAIN = WORKSPACE_ROOT / "cortex-brain"
CX6_PLAN = CORTEX_BRAIN / "cx6-plan"

# Target folder structure
TARGET_STRUCTURE = {
    "viewer": CX6_PLAN / "viewer",           # Plan viewer HTML files
    "validation": CX6_PLAN / "validation",   # Validation reports
    "phases": CX6_PLAN / "phases",           # Phase breakdown documents
    "architecture": CX6_PLAN / "architecture",  # Architecture docs
    "reports": CX6_PLAN / "reports",         # Completion reports
    "archive": CX6_PLAN / "archive",         # Legacy/historical files
}

# File relocations mapping
FILE_RELOCATIONS = [
    # Plan Viewer Files → viewer/
    ("templates/plan-viewer/cortex-plan-viewer.html", "viewer/cortex-plan-viewer.html"),
    ("templates/plan-viewer/phase-detail-viewer.html", "viewer/phase-detail-viewer.html"),
    ("templates/plan-viewer/cortex-plan-viewer-v2.html", "viewer/cortex-plan-viewer-v2.html"),
    ("templates/plan-viewer/README.md", "viewer/README.md"),
    ("templates/plan-viewer/README-QUICKSTART.md", "viewer/README-QUICKSTART.md"),
    
    # Validation Documents → validation/
    ("cortex-brain/documents/validation/cx6-requirements-gap-analysis.md", "validation/cx6-requirements-gap-analysis.md"),
    ("cortex-brain/documents/validation/cx6-reorganization-completion-report.md", "validation/cx6-reorganization-completion-report.md"),
    ("cortex-brain/documents/validation/option-a-sts-implementation-summary.md", "validation/option-a-sts-implementation-summary.md"),
    ("cortex-brain/documents/validation/phase1-verification-report.yaml", "validation/phase1-verification-report.yaml"),
    ("cortex-brain/documents/validation/cortex6-holistic-implementation-report.md", "validation/cortex6-holistic-implementation-report.md"),
    ("cortex-brain/documents/validation/holistic-verification-2026-01-10.md", "validation/holistic-verification-2026-01-10.md"),
    ("cortex-brain/documents/validation/holistic-verification-summary.md", "validation/holistic-verification-summary.md"),
    
    # Completion Reports → reports/
    ("cortex-brain/documents/reports/CORTEX-6.0-COMPLETION-REPORT.md", "reports/cortex-6.0-completion-report.md"),
    
    # Dashboard data (if exists) → viewer/
    ("cortex-brain/dashboards/plan-data.json", "viewer/plan-data.json"),
    
    # Plan viewer related validation docs → viewer/docs/
    ("cortex-brain/documents/validation/plan-viewer-update-summary.md", "viewer/docs/plan-viewer-update-summary.md"),
    ("cortex-brain/documents/validation/plan-viewer-redesign-summary.md", "viewer/docs/plan-viewer-redesign-summary.md"),
    ("cortex-brain/documents/validation/plan-viewer-equal-height-003.md", "viewer/docs/plan-viewer-equal-height-003.md"),
    ("cortex-brain/documents/validation/plan-viewer-equal-height-004.md", "viewer/docs/plan-viewer-equal-height-004.md"),
    ("cortex-brain/documents/validation/plan-viewer-enhancement-002.md", "viewer/docs/plan-viewer-enhancement-002.md"),
]


class CX6PlanConsolidator:
    """Consolidates all CORTEX 6 plan files into organized structure"""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.actions_log = []
        self.errors_log = []
        self.files_moved = 0
        self.dirs_created = 0
        
    def log_action(self, action: str):
        """Log an action"""
        prefix = "[DRY-RUN] " if self.dry_run else "[EXECUTE] "
        message = f"{prefix}{action}"
        self.actions_log.append(message)
        print(message)
        
    def log_error(self, error: str):
        """Log an error"""
        message = f"[ERROR] {error}"
        self.errors_log.append(message)
        print(message)
    
    def create_directory_structure(self):
        """Create target directory structure"""
        self.log_action("\n=== Creating Directory Structure ===\n")
        
        for folder_name, folder_path in TARGET_STRUCTURE.items():
            if not folder_path.exists():
                if not self.dry_run:
                    folder_path.mkdir(parents=True, exist_ok=True)
                self.log_action(f"Created: {folder_path.relative_to(WORKSPACE_ROOT)}")
                self.dirs_created += 1
            else:
                self.log_action(f"Exists: {folder_path.relative_to(WORKSPACE_ROOT)}")
        
        # Create viewer/docs subdirectory
        viewer_docs = TARGET_STRUCTURE["viewer"] / "docs"
        if not viewer_docs.exists():
            if not self.dry_run:
                viewer_docs.mkdir(parents=True, exist_ok=True)
            self.log_action(f"Created: {viewer_docs.relative_to(WORKSPACE_ROOT)}")
            self.dirs_created += 1
    
    def relocate_files(self):
        """Move files to target locations"""
        self.log_action("\n=== Relocating Files ===\n")
        
        for source_rel, target_rel in FILE_RELOCATIONS:
            source_path = WORKSPACE_ROOT / source_rel
            target_path = CX6_PLAN / target_rel
            
            if not source_path.exists():
                self.log_action(f"⚠️  SKIP (not found): {source_rel}")
                continue
            
            # Create parent directory if needed
            if not self.dry_run:
                target_path.parent.mkdir(parents=True, exist_ok=True)
            
            try:
                if not self.dry_run:
                    shutil.move(str(source_path), str(target_path))
                
                self.log_action(f"Moved: {source_rel}")
                self.log_action(f"    → {target_path.relative_to(WORKSPACE_ROOT)}")
                self.files_moved += 1
                
            except Exception as e:
                self.log_error(f"Failed to move {source_rel}: {e}")
    
    def update_references(self):
        """Update file references after relocation"""
        self.log_action("\n=== Updating File References ===\n")
        
        reference_updates = [
            # CORTEX.prompt.md references
            {
                "file": ".github/prompts/CORTEX.prompt.md",
                "replacements": [
                    (
                        r"templates/plan-viewer/cortex-plan-viewer\.html",
                        "cortex-brain/cx6-plan/viewer/cortex-plan-viewer.html"
                    ),
                    (
                        r"templates/plan-viewer/phase-detail-viewer\.html",
                        "cortex-brain/cx6-plan/viewer/phase-detail-viewer.html"
                    ),
                    (
                        r"\.\./\.\./cortex-brain/documents/validation/option-a-sts-implementation-summary\.md",
                        "../../cortex-brain/cx6-plan/validation/option-a-sts-implementation-summary.md"
                    ),
                    (
                        r"\.\./\.\./cortex-brain/documents/validation/cx6-requirements-gap-analysis\.md",
                        "../../cortex-brain/cx6-plan/validation/cx6-requirements-gap-analysis.md"
                    ),
                ]
            },
            # State synchronizer references
            {
                "file": "src/orchestrators/core/state_synchronizer.py",
                "replacements": [
                    (
                        r'templates/plan-viewer/cortex-plan-viewer\.html',
                        'cortex-brain/cx6-plan/viewer/cortex-plan-viewer.html'
                    ),
                ]
            },
        ]
        
        for ref_update in reference_updates:
            file_path = WORKSPACE_ROOT / ref_update["file"]
            
            if not file_path.exists():
                self.log_action(f"⚠️  SKIP (not found): {ref_update['file']}")
                continue
            
            try:
                content = file_path.read_text()
                updated_content = content
                changes_made = 0
                
                for pattern, replacement in ref_update["replacements"]:
                    if re.search(pattern, updated_content):
                        updated_content = re.sub(pattern, replacement, updated_content)
                        changes_made += 1
                
                if changes_made > 0:
                    if not self.dry_run:
                        file_path.write_text(updated_content)
                    self.log_action(f"Updated {changes_made} references in: {ref_update['file']}")
                else:
                    self.log_action(f"No changes needed in: {ref_update['file']}")
                    
            except Exception as e:
                self.log_error(f"Failed to update {ref_update['file']}: {e}")
    
    def create_index_file(self):
        """Create README index for cx6-plan folder"""
        self.log_action("\n=== Creating Index File ===\n")
        
        index_content = """# CORTEX 6.0 Plan - Complete Breakdown

**Single Source of Truth for CORTEX 6.0 Implementation**

---

## 📁 Folder Structure

### `/viewer/`
**Plan Viewer HTML Files**
- `cortex-plan-viewer.html` - Main plan visualization dashboard
- `phase-detail-viewer.html` - Detailed phase breakdown viewer
- `plan-data.json` - Dashboard data source
- `docs/` - Plan viewer documentation and enhancement history

### `/validation/`
**Validation Reports & Gap Analysis**
- `cx6-requirements-gap-analysis.md` - Comprehensive gap analysis (16.5% actual completion)
- `option-a-sts-implementation-summary.md` - Phase 1.5 STS implementation details
- `phase1-verification-report.yaml` - Phase 1 verification with YAML bug fix
- `cortex6-holistic-implementation-report.md` - Full implementation report
- `holistic-verification-*.md` - Holistic verification reports

### `/phases/`
**Phase Breakdown Documents**
- Detailed breakdown of each phase (1, 1.5, 2, 3, 4)
- AC-ID listings per phase
- Phase dependencies and gates

### `/architecture/`
**Architecture Documents**
- 4-Tier governance architecture
- Component interaction diagrams
- Design decisions and patterns

### `/reports/`
**Completion & Progress Reports**
- `cortex-6.0-completion-report.md` - Overall completion status
- Sprint reports
- Milestone reports

### `/archive/`
**Legacy & Historical Files**
- Previous plan versions
- Round 1/2/3 review documents
- Deprecated architecture files

---

## 📊 Key Documents

### Master Plan
- **`master-plan.yaml`** - 111 AC-IDs, 4 phases, complete structure

### Implementation Roadmap
- **`implementation-roadmap.md`** - 20-week corrected roadmap

### Current Status (as of 2026-01-11)
- **Overall Completion:** 18.5% (18/97 AC-IDs)
- **Current Phase:** Phase 1.5 - STS (System Testing Suite)
- **Next Phase Gate:** Phase 1 → Phase 2 (blocked until Phase 1.5 complete)

---

## 🔗 Quick Links

- [Plan Viewer](viewer/cortex-plan-viewer.html) - Visual dashboard
- [Gap Analysis](validation/cx6-requirements-gap-analysis.md) - Detailed status
- [Implementation Roadmap](implementation-roadmap.md) - 20-week plan
- [Phase 1.5 Status](validation/option-a-sts-implementation-summary.md) - STS implementation

---

## 📝 Usage

**View Plan:**
```bash
# Open plan viewer in browser
open cortex-brain/cx6-plan/viewer/cortex-plan-viewer.html
```

**Check Status:**
```bash
# Read gap analysis
cat cortex-brain/cx6-plan/validation/cx6-requirements-gap-analysis.md

# Load master plan
python3 -c "import yaml; print(yaml.safe_load(open('cortex-brain/cx6-plan/master-plan.yaml')))"
```

**Update Plan:**
```bash
# Regenerate viewer after changes
python3 scripts/update_plan_viewer_progress.py
```

---

**Last Updated:** 2026-01-11  
**Maintained By:** CORTEX 6.0 Governance System
"""
        
        index_path = CX6_PLAN / "README.md"
        
        if not self.dry_run:
            index_path.write_text(index_content)
        
        self.log_action(f"Created: {index_path.relative_to(WORKSPACE_ROOT)}")
    
    def generate_summary(self):
        """Generate summary report"""
        self.log_action("\n" + "="*70)
        self.log_action("=== CX6 PLAN CONSOLIDATION SUMMARY ===")
        self.log_action("="*70)
        
        self.log_action(f"\nMode: {'DRY-RUN (preview only)' if self.dry_run else 'EXECUTE (changes applied)'}")
        self.log_action(f"Directories Created: {self.dirs_created}")
        self.log_action(f"Files Moved: {self.files_moved}")
        self.log_action(f"Total Actions: {len(self.actions_log)}")
        self.log_action(f"Total Errors: {len(self.errors_log)}")
        
        if self.errors_log:
            self.log_action("\n⚠️  ERRORS ENCOUNTERED:")
            for error in self.errors_log:
                print(error)
        
        if not self.dry_run:
            self.log_action("\n✅ Consolidation complete!")
            self.log_action("\nNext steps:")
            self.log_action("1. Verify files in cortex-brain/cx6-plan/")
            self.log_action("2. Open viewer: cortex-brain/cx6-plan/viewer/cortex-plan-viewer.html")
            self.log_action("3. Check README: cortex-brain/cx6-plan/README.md")
            self.log_action("4. Update any additional broken references")
            self.log_action("5. Commit changes")
        else:
            self.log_action("\n✅ Dry-run complete. Review the actions above.")
            self.log_action("\nTo execute, run:")
            self.log_action("  python3 scripts/consolidate_cx6_plan.py --execute")
    
    def execute(self):
        """Execute the full consolidation"""
        try:
            self.log_action("="*70)
            self.log_action("CORTEX 6.0 PLAN CONSOLIDATION")
            self.log_action("="*70)
            self.log_action(f"Mode: {'DRY-RUN' if self.dry_run else 'EXECUTE'}")
            self.log_action("="*70)
            
            self.create_directory_structure()
            self.relocate_files()
            self.update_references()
            self.create_index_file()
            self.generate_summary()
            
            return len(self.errors_log) == 0
        
        except Exception as e:
            self.log_error(f"Fatal error during consolidation: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CORTEX 6.0 Plan Consolidation - Organize all CX6 files into cx6-plan/"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the consolidation (default is dry-run)"
    )
    
    args = parser.parse_args()
    
    # Execute is opposite of dry-run
    dry_run = not args.execute
    
    consolidator = CX6PlanConsolidator(dry_run=dry_run)
    success = consolidator.execute()
    
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
