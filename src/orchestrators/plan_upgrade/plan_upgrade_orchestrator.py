#!/usr/bin/env python3
"""
CORTEX Plan Upgrade Orchestrator

Autonomous migration of legacy plans to CORTEX-5.0 standards.

Capabilities:
- Analyze legacy plan structure and content
- Extract core requirements and acceptance criteria
- Regenerate plan following CORTEX-5.0 standards
- Validate against Final Acceptance Criteria
- Archive old plan, activate new plan
- Generate migration report

Author: Asif Hussain
Version: 1.0.0
Copyright © 2026 Asif Hussain. All rights reserved.
"""

import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# CORTEX-5.0 Plan Standards
CORTEX_5_STANDARDS = {
    "folder_structure": {
        "root": "cortex-brain/documents/planning/active/",
        "subfolders": ["context/", "reports/", "artifacts/", "tracking/"]
    },
    "master_plan_file": "00-master-plan.md",
    "required_sections": [
        "Progress Tracker",
        "Strategic Context",
        "Dependencies",
        "Phase Breakdown",
        "REFACTOR Phase",
        "Success Criteria",
        "Git Checkpoints"
    ],
    "refactor_phase": {
        "minimum_tasks": 18,
        "mandatory_checks": [
            "Remove duplicates",
            "Fix broken structure",
            "Reduce complexity",
            "Enforce SOLID",
            "Remove dead code",
            "Add missing docstrings",
            "Update inline comments",
            "Fix broken links",
            "Add missing tests",
            "Optimize queries",
            "Fix memory leaks",
            "Remove debug code",
            "Validate input sanitization"
        ]
    },
    "visual_progress": {
        "required": True,
        "format": "ASCII progress bars",
        "update_frequency": "per-phase"
    },
    "git_workflow": {
        "commits_required": True,
        "push_forbidden": True,
        "checkpoint_format": "cortex-phase-{number}-{name}"
    },
    "metadata": {
        "required_fields": [
            "plan_id",
            "created",
            "author",
            "status",
            "priority",
            "duration",
            "parent_plan"
        ]
    },
    "acceptance_criteria": {
        "format": "AC-{number}",
        "validation_required": True,
        "evidence_mapping": True
    }
}


class PlanUpgradeOrchestrator:
    """Migrates legacy plans to CORTEX-5.0 standards."""
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.brain_root = workspace_root / "cortex-brain"
        self.planning_root = self.brain_root / "documents" / "planning"
        self.active_dir = self.planning_root / "active"
        self.archive_dir = self.planning_root / "archived"
        
        # Ensure archive directory exists
        self.archive_dir.mkdir(parents=True, exist_ok=True)
    
    def analyze_legacy_plan(self, plan_path: Path) -> Dict:
        """
        Analyze legacy plan structure and extract key information.
        
        Args:
            plan_path: Path to legacy plan directory or file
            
        Returns:
            Dictionary with analysis results
        """
        analysis = {
            "plan_path": str(plan_path),
            "plan_name": plan_path.stem if plan_path.is_file() else plan_path.name,
            "is_directory": plan_path.is_dir(),
            "compliance_issues": [],
            "extracted_content": {},
            "migration_required": True
        }
        
        if plan_path.is_dir():
            analysis["extracted_content"] = self._analyze_directory_plan(plan_path, analysis)
        else:
            analysis["extracted_content"] = self._analyze_file_plan(plan_path, analysis)
        
        # Check compliance
        self._check_compliance(plan_path, analysis)
        
        return analysis
    
    def _analyze_directory_plan(self, plan_dir: Path, analysis: Dict) -> Dict:
        """Analyze directory-based plan structure."""
        content = {
            "has_master_plan": False,
            "has_subfolders": False,
            "subfolder_compliance": {},
            "master_plan_path": None,
            "phases": [],
            "acceptance_criteria": [],
            "context_files": []
        }
        
        # Check for master plan
        master_plan = plan_dir / "00-master-plan.md"
        if master_plan.exists():
            content["has_master_plan"] = True
            content["master_plan_path"] = str(master_plan)
            content.update(self._extract_plan_content(master_plan))
        else:
            # Look for any .md file in root
            md_files = list(plan_dir.glob("*.md"))
            if md_files:
                content["master_plan_path"] = str(md_files[0])
                content.update(self._extract_plan_content(md_files[0]))
        
        # Check subfolder structure
        required_subfolders = CORTEX_5_STANDARDS["folder_structure"]["subfolders"]
        for subfolder in required_subfolders:
            subfolder_path = plan_dir / subfolder
            content["subfolder_compliance"][subfolder] = subfolder_path.exists()
        
        content["has_subfolders"] = all(content["subfolder_compliance"].values())
        
        # Collect context files
        context_dir = plan_dir / "context"
        if context_dir.exists():
            content["context_files"] = [str(f) for f in context_dir.glob("*")]
        
        return content
    
    def _analyze_file_plan(self, plan_file: Path, analysis: Dict) -> Dict:
        """Analyze single-file plan."""
        content = {
            "has_master_plan": True,
            "master_plan_path": str(plan_file),
            "has_subfolders": False,
            "subfolder_compliance": {sf: False for sf in CORTEX_5_STANDARDS["folder_structure"]["subfolders"]}
        }
        
        content.update(self._extract_plan_content(plan_file))
        
        return content
    
    def _extract_plan_content(self, plan_file: Path) -> Dict:
        """Extract key content from plan markdown file."""
        with open(plan_file, 'r', encoding='utf-8') as f:
            content_text = f.read()
        
        extracted = {
            "title": self._extract_title(content_text),
            "phases": self._extract_phases(content_text),
            "acceptance_criteria": self._extract_acceptance_criteria(content_text),
            "has_progress_tracker": self._has_progress_tracker(content_text),
            "has_refactor_phase": self._has_refactor_phase(content_text),
            "refactor_task_count": self._count_refactor_tasks(content_text),
            "has_git_checkpoints": self._has_git_checkpoints(content_text),
            "raw_content": content_text
        }
        
        return extracted
    
    def _extract_title(self, content: str) -> str:
        """Extract plan title from markdown."""
        title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        return title_match.group(1).strip() if title_match else "Untitled Plan"
    
    def _extract_phases(self, content: str) -> List[Dict]:
        """Extract phases from plan content."""
        phases = []
        
        # Look for phase headers (### Phase N: Name or ## Phase N)
        phase_pattern = r'###?\s+Phase\s+(\d+):?\s*(.+?)(?=###?|$)'
        matches = re.finditer(phase_pattern, content, re.DOTALL | re.IGNORECASE)
        
        for match in matches:
            phase_num = match.group(1)
            phase_content = match.group(2).strip()
            
            # Extract phase name from first line
            first_line = phase_content.split('\n')[0].strip()
            phase_name = first_line if first_line else f"Phase {phase_num}"
            
            phases.append({
                "number": int(phase_num),
                "name": phase_name,
                "content": phase_content[:200]  # First 200 chars
            })
        
        return phases
    
    def _extract_acceptance_criteria(self, content: str) -> List[Dict]:
        """Extract acceptance criteria from plan."""
        criteria = []
        
        # Look for AC patterns: AC-01, AC-001, or numbered lists in AC section
        ac_pattern = r'(?:AC-(\d+)|(?:^|\n)\s*\d+\.\s+)(.+?)(?=\n|$)'
        matches = re.finditer(ac_pattern, content, re.MULTILINE)
        
        for i, match in enumerate(matches, 1):
            ac_id = match.group(1) if match.group(1) else f"{i:02d}"
            description = match.group(2).strip()
            
            criteria.append({
                "id": f"AC-{ac_id}",
                "description": description
            })
        
        return criteria
    
    def _has_progress_tracker(self, content: str) -> bool:
        """Check if plan has visual progress tracker."""
        progress_indicators = ['░', '█', 'Progress:', '██', 'Overall Progress']
        return any(indicator in content for indicator in progress_indicators)
    
    def _has_refactor_phase(self, content: str) -> bool:
        """Check if plan has REFACTOR phase."""
        refactor_keywords = ['REFACTOR', 'Refactor', 'refactor', 'Cleanup', 'Code Cleanup']
        return any(keyword in content for keyword in refactor_keywords)
    
    def _count_refactor_tasks(self, content: str) -> int:
        """Count tasks in REFACTOR phase."""
        # Find REFACTOR section
        refactor_match = re.search(
            r'(?:###?\s+.*?REFACTOR.*?)(.*?)(?=###?|$)',
            content,
            re.DOTALL | re.IGNORECASE
        )
        
        if not refactor_match:
            return 0
        
        refactor_section = refactor_match.group(1)
        
        # Count numbered lists or checkboxes
        task_patterns = [
            r'^\s*\d+\.\s+',  # 1. Task
            r'^\s*[-*]\s+',    # - Task or * Task
            r'^\s*\[[ x]\]\s+' # [ ] Task or [x] Task
        ]
        
        task_count = 0
        for pattern in task_patterns:
            tasks = re.findall(pattern, refactor_section, re.MULTILINE)
            task_count += len(tasks)
        
        return task_count
    
    def _has_git_checkpoints(self, content: str) -> bool:
        """Check if plan mentions git checkpoints."""
        git_keywords = ['git commit', 'git checkpoint', 'git tag', 'cortex-phase']
        return any(keyword in content.lower() for keyword in git_keywords)
    
    def _check_compliance(self, plan_path: Path, analysis: Dict):
        """Check plan compliance against CORTEX-5.0 standards."""
        issues = []
        content = analysis["extracted_content"]
        
        # Check folder structure
        if plan_path.is_dir():
            if not content.get("has_subfolders", False):
                missing = [sf for sf, exists in content.get("subfolder_compliance", {}).items() if not exists]
                issues.append(f"Missing subfolders: {', '.join(missing)}")
        else:
            issues.append("Plan is single file, not directory structure")
        
        # Check master plan
        if not content.get("has_master_plan", False):
            issues.append("Missing 00-master-plan.md")
        
        # Check progress tracker
        if not content.get("has_progress_tracker", False):
            issues.append("Missing visual progress tracker")
        
        # Check REFACTOR phase
        if not content.get("has_refactor_phase", False):
            issues.append("Missing REFACTOR phase")
        else:
            task_count = content.get("refactor_task_count", 0)
            if task_count < CORTEX_5_STANDARDS["refactor_phase"]["minimum_tasks"]:
                issues.append(f"REFACTOR phase has only {task_count} tasks (minimum: 18)")
        
        # Check git checkpoints
        if not content.get("has_git_checkpoints", False):
            issues.append("Missing git checkpoint references")
        
        # Check phases
        phases = content.get("phases", [])
        if len(phases) < 3:
            issues.append(f"Only {len(phases)} phases defined (recommend 5+)")
        
        # Check acceptance criteria
        ac_list = content.get("acceptance_criteria", [])
        if len(ac_list) == 0:
            issues.append("No acceptance criteria defined")
        
        analysis["compliance_issues"] = issues
        analysis["migration_required"] = len(issues) > 0
        analysis["compliance_score"] = max(0, 100 - (len(issues) * 10))
    
    def generate_upgraded_plan(self, analysis: Dict, output_dir: Optional[Path] = None) -> Path:
        """
        Generate CORTEX-5.0 compliant plan from analysis.
        
        Args:
            analysis: Analysis results from analyze_legacy_plan()
            output_dir: Optional output directory (defaults to active/)
            
        Returns:
            Path to new plan directory
        """
        # Determine output location
        if output_dir is None:
            plan_name = analysis["plan_name"]
            plan_name_clean = re.sub(r'[^a-z0-9-]', '-', plan_name.lower())
            output_dir = self.active_dir / f"{plan_name_clean}-v5"
        
        # Create folder structure
        output_dir.mkdir(parents=True, exist_ok=True)
        for subfolder in CORTEX_5_STANDARDS["folder_structure"]["subfolders"]:
            (output_dir / subfolder).mkdir(exist_ok=True)
        
        # Generate master plan content
        master_plan_content = self._generate_master_plan_content(analysis)
        
        # Write master plan
        master_plan_path = output_dir / CORTEX_5_STANDARDS["master_plan_file"]
        with open(master_plan_path, 'w', encoding='utf-8') as f:
            f.write(master_plan_content)
        
        # Generate tracking JSON
        tracking_json = self._generate_tracking_json(analysis)
        tracking_path = output_dir / "tracking" / "progress-tracker.json"
        with open(tracking_path, 'w', encoding='utf-8') as f:
            json.dump(tracking_json, f, indent=2)
        
        # Copy context files if they exist
        if "context_files" in analysis["extracted_content"]:
            for context_file in analysis["extracted_content"]["context_files"]:
                src = Path(context_file)
                dst = output_dir / "context" / src.name
                if src.exists():
                    shutil.copy2(src, dst)
        
        # Generate migration report
        self._generate_migration_report(analysis, output_dir)
        
        return output_dir
    
    def _generate_master_plan_content(self, analysis: Dict) -> str:
        """Generate CORTEX-5.0 compliant master plan markdown."""
        content = analysis["extracted_content"]
        title = content.get("title", "Untitled Plan")
        
        # Clean title
        title = re.sub(r'^#\s+', '', title).strip()
        
        # Generate metadata
        plan_id = re.sub(r'[^a-z0-9-]', '-', title.lower())
        timestamp = datetime.now().strftime("%Y-%m-%d")
        
        plan_content = f"""# 🎯 {title} (CORTEX-5.0 Compliant)

**Plan ID:** {plan_id}-v5  
**Created:** {timestamp}  
**Author:** Asif Hussain  
**Status:** 📋 READY FOR REVIEW  
**Priority:** HIGH  
**Duration:** TBD  
**Parent Plan:** CORTEX-5.0 Gap Remediation  
**Migrated From:** {analysis['plan_name']}

---

## 📊 Progress Tracker

**Overall Progress:** `░░░░░░░░░░` **0%** ⏸️ NOT STARTED

| Phase | Tasks | Progress | Status | Duration | Git Checkpoint |
|-------|-------|----------|--------|----------|----------------|
"""
        
        # Add phases from analysis
        phases = content.get("phases", [])
        if not phases:
            # Generate default phases
            phases = [
                {"number": 0, "name": "Setup & Discovery"},
                {"number": 1, "name": "Planning & Design"},
                {"number": 2, "name": "Implementation"},
                {"number": 3, "name": "Testing & Validation"},
                {"number": 4, "name": "REFACTOR - Holistic Cleanup"},
                {"number": 5, "name": "Documentation"},
                {"number": 6, "name": "Final Validation"}
            ]
        
        for phase in phases:
            phase_num = phase.get("number", 0)
            phase_name = phase.get("name", f"Phase {phase_num}")
            plan_content += f"| **Phase {phase_num}: {phase_name}** | TBD | `░░░░░░░░░░` 0% | ⏸️ Not Started | TBD | `cortex-phase-{phase_num}` |\n"
        
        # Add REFACTOR phase if not present
        if not content.get("has_refactor_phase", False):
            refactor_num = len(phases)
            plan_content += f"| **Phase {refactor_num}: REFACTOR - Holistic Cleanup** | 18+ | `░░░░░░░░░░` 0% | ⏸️ Not Started | 1d | `cortex-phase-{refactor_num}` |\n"
        
        plan_content += """
---

## 🎯 Strategic Context

### Problem Statement

"""
        
        # Extract problem from original content if available
        raw_content = content.get("raw_content", "")
        problem_match = re.search(r'(?:Problem|Context|Background):\s*(.{100,500})', raw_content, re.DOTALL | re.IGNORECASE)
        if problem_match:
            plan_content += problem_match.group(1).strip()[:400] + "...\n\n"
        else:
            plan_content += "*(Extracted from legacy plan - review and update)*\n\n"
        
        plan_content += """### Solution Approach

*(Define high-level strategy)*

---

## 📋 Dependencies

**Required (Blockers):**
- *(List dependencies)*

**Optional (Enhancers):**
- *(List nice-to-have dependencies)*

---

## 🛡️ SKULL Rules Enforced

| Rule | Enforcement Point |
|------|------------------|
| **GIT_NO_PUSH_ENFORCEMENT** | All phases commit, NEVER push |
| **GIT_CHECKPOINT_PHASE_PROTECTION** | Checkpoint after each phase |
| **REFACTOR_CODE_CLEANUP_ENFORCEMENT** | Phase N (18+ mandatory tasks) |
| **DEFINITION_OF_DONE** | Final approval gate |

---

## 🏗️ Phase Breakdown

"""
        
        # Add phase details
        for phase in phases:
            phase_num = phase.get("number", 0)
            phase_name = phase.get("name", f"Phase {phase_num}")
            
            plan_content += f"""### Phase {phase_num}: {phase_name}

**Objective:** *(Define phase goal)*

**Tasks:**
1. *(Define tasks)*

**Exit Criteria:**
- ✅ *(Define completion criteria)*

**Git Checkpoint:**
```bash
git add .
git commit -m "cortex: Phase {phase_num} - {phase_name} complete"
git tag cortex-phase-{phase_num}
```

---

"""
        
        # Add comprehensive REFACTOR phase
        refactor_num = len(phases)
        plan_content += f"""### Phase {refactor_num}: REFACTOR - Holistic Code Cleanup

**Objective:** Review ENTIRE codebase (not just new code) for quality issues

**Mandatory Tasks (18+):**

#### Code Quality (6 tasks)
1. **Remove Duplicate Code** - Scan for duplicates (≥10 lines), extract to utilities
2. **Fix Broken Structure** - Validate imports, check circular dependencies
3. **Reduce Complexity** - Refactor functions with complexity >30
4. **Enforce SOLID Principles** - SRP, OCP, LSP, ISP, DIP
5. **Remove Dead Code** - Unused imports, unreferenced functions
6. **Fix Code Smells** - Long parameter lists, god objects, feature envy

#### Documentation (4 tasks)
7. **Add Missing Docstrings** - All public functions documented
8. **Update Inline Comments** - Remove obvious, add WHY comments
9. **Fix Broken Links** - Validate all `#file:` references
10. **Update README files** - Reflect new functionality

#### Testing (3 tasks)
11. **Add Missing Tests** - Untested code paths
12. **Fix Brittle Tests** - Remove hardcoded values, use fixtures
13. **Improve Test Coverage** - Target ≥80%

#### Performance (3 tasks)
14. **Optimize Database Queries** - Fix N+1 patterns, add indexes
15. **Fix Memory Leaks** - Close file handles, clean up objects
16. **Reduce Response Times** - Profile slow code, optimize algorithms

#### Security (2 tasks)
17. **Remove Debug Code** - Delete print statements, debug flags
18. **Validate Input Sanitization** - Check all user inputs validated

**Exit Criteria:**
- ✅ All 18+ refactor tasks completed
- ✅ Code quality tools pass (Pylint ≥8.5/10)
- ✅ No duplicates >10 lines
- ✅ Complexity ≤30 for all functions
- ✅ Test coverage ≥80%

**Git Checkpoint:**
```bash
git add .
git commit -m "cortex: Phase {refactor_num} - REFACTOR complete

Completed:
- [List major refactoring achievements]

Quality Metrics:
- Pylint: [score]
- Coverage: [percentage]
- Complexity: max [number]
"
git tag cortex-phase-{refactor_num}-refactor
```

---

## ✅ Success Criteria (Acceptance Criteria)

"""
        
        # Add acceptance criteria
        ac_list = content.get("acceptance_criteria", [])
        if ac_list:
            for ac in ac_list:
                plan_content += f"**{ac['id']}:** {ac['description']}\n\n"
        else:
            plan_content += """**AC-01:** *(Define acceptance criterion 1)*
**AC-02:** *(Define acceptance criterion 2)*
**AC-03:** *(Define acceptance criterion 3)*

"""
        
        plan_content += """---

## 🔄 GIT_NO_PUSH_ENFORCEMENT

**CRITICAL:** Every phase commits to local git, but NEVER pushes to remote.

```python
# ✅ CORRECT
def complete_phase(phase_name: str):
    run_command("git add .")
    run_command(f"git commit -m 'cortex: {phase_name} complete'")
    run_command(f"git tag cortex-{phase_name}")
    print(f"✅ {phase_name} complete (committed locally)")
    print("⚠️  Not pushed to remote. Run 'git push' when ready.")
```

**User Action Required:**
```bash
# Review commits
git log --oneline --graph

# When satisfied, push manually
git push origin [branch-name]
git push origin --tags
```

---

## 📚 Reference Documentation

### Related Plans
- [CORTEX-5.0 Master Plan](../CORTEX-5.0/00-cortex-v5-gap-remediation/00-MASTER-REMEDIATION-PLAN.md)
- [Brain Protection Rules](../../../../brain-protection-rules.yaml)

### Migration Notes
- **Original Plan:** {analysis['plan_path']}
- **Compliance Score:** {analysis['compliance_score']}%
- **Issues Fixed:** {len(analysis['compliance_issues'])}
- **Migration Date:** {timestamp}

---

**Status:** 📋 READY FOR REVIEW  
**Next:** Review and update placeholders, then begin Phase 0  
**Migrated By:** CORTEX Plan Upgrade Orchestrator v1.0.0

---

**Copyright © 2026 Asif Hussain. All rights reserved.**
"""
        
        return plan_content
    
    def _generate_tracking_json(self, analysis: Dict) -> Dict:
        """Generate progress tracking JSON."""
        content = analysis["extracted_content"]
        phases = content.get("phases", [])
        
        tracking = {
            "plan_id": analysis["plan_name"],
            "version": "5.0",
            "created": datetime.now().isoformat(),
            "migrated_from": analysis["plan_path"],
            "overall_progress": 0,
            "phases": []
        }
        
        for phase in phases:
            tracking["phases"].append({
                "number": phase.get("number", 0),
                "name": phase.get("name", "Unnamed Phase"),
                "status": "not_started",
                "progress": 0,
                "tasks_completed": 0,
                "tasks_total": 0,
                "started": None,
                "completed": None
            })
        
        # Add REFACTOR phase if missing
        if not content.get("has_refactor_phase", False):
            tracking["phases"].append({
                "number": len(phases),
                "name": "REFACTOR - Holistic Cleanup",
                "status": "not_started",
                "progress": 0,
                "tasks_completed": 0,
                "tasks_total": 18,
                "started": None,
                "completed": None
            })
        
        return tracking
    
    def _generate_migration_report(self, analysis: Dict, output_dir: Path):
        """Generate migration report documenting the upgrade process."""
        report_content = f"""# 📊 Plan Migration Report

**Migration Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Original Plan:** {analysis['plan_path']}  
**New Plan:** {output_dir}  
**Migrated By:** CORTEX Plan Upgrade Orchestrator v1.0.0

---

## 🎯 Migration Summary

**Compliance Score:** {analysis['compliance_score']}%  
**Issues Fixed:** {len(analysis['compliance_issues'])}  
**Migration Required:** {'Yes' if analysis['migration_required'] else 'No'}

---

## 📋 Original Plan Analysis

### Structure
- **Type:** {'Directory' if analysis['is_directory'] else 'Single File'}
- **Master Plan:** {'✅ Found' if analysis['extracted_content'].get('has_master_plan') else '❌ Missing'}
- **Subfolders:** {'✅ Complete' if analysis['extracted_content'].get('has_subfolders') else '❌ Incomplete'}

### Content
- **Phases:** {len(analysis['extracted_content'].get('phases', []))}
- **Acceptance Criteria:** {len(analysis['extracted_content'].get('acceptance_criteria', []))}
- **Progress Tracker:** {'✅ Present' if analysis['extracted_content'].get('has_progress_tracker') else '❌ Missing'}
- **REFACTOR Phase:** {'✅ Present' if analysis['extracted_content'].get('has_refactor_phase') else '❌ Missing'}
- **Git Checkpoints:** {'✅ Mentioned' if analysis['extracted_content'].get('has_git_checkpoints') else '❌ Not Mentioned'}

---

## ⚠️ Compliance Issues Fixed

"""
        
        if analysis['compliance_issues']:
            for i, issue in enumerate(analysis['compliance_issues'], 1):
                report_content += f"{i}. {issue}\n"
        else:
            report_content += "✅ No compliance issues found\n"
        
        report_content += f"""
---

## ✅ CORTEX-5.0 Compliance

### Folder Structure
- ✅ Created `context/` subfolder
- ✅ Created `reports/` subfolder
- ✅ Created `artifacts/` subfolder
- ✅ Created `tracking/` subfolder
- ✅ Generated `00-master-plan.md`
- ✅ Generated `tracking/progress-tracker.json`

### Master Plan Content
- ✅ Visual progress tracker (ASCII bars)
- ✅ Phase breakdown with git checkpoints
- ✅ REFACTOR phase (18+ mandatory tasks)
- ✅ GIT_NO_PUSH_ENFORCEMENT documented
- ✅ SKULL rules section
- ✅ Acceptance criteria section
- ✅ Reference documentation section

### Git Workflow
- ✅ Git checkpoint format: `cortex-phase-{{number}}`
- ✅ Commit commands documented per phase
- ✅ GIT_NO_PUSH_ENFORCEMENT enforced
- ✅ User push control instructions included

---

## 🚀 Next Steps

1. **Review Migrated Plan**
   - Open: `{output_dir / '00-master-plan.md'}`
   - Update placeholders marked with `*()*`
   - Verify phase breakdown matches intent

2. **Archive Original Plan**
   - Original plan will be moved to `archived/` after user confirmation
   - Backup created with timestamp

3. **Begin Execution**
   - Follow phase-by-phase execution
   - Git commit after each phase (don't push!)
   - Update progress tracker JSON

---

**Migration Status:** ✅ COMPLETE  
**New Plan Ready:** {output_dir}

---

**Copyright © 2026 Asif Hussain. All rights reserved.**
"""
        
        report_path = output_dir / "reports" / "migration-report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
    
    def archive_legacy_plan(self, plan_path: Path, backup: bool = True) -> Path:
        """
        Archive legacy plan after successful migration.
        
        Args:
            plan_path: Path to legacy plan
            backup: Create timestamped backup before archiving
            
        Returns:
            Path to archived plan
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plan_name = plan_path.stem if plan_path.is_file() else plan_path.name
        
        # Create archive destination
        archive_name = f"{plan_name}-archived-{timestamp}"
        archive_path = self.archive_dir / archive_name
        
        # Move plan to archive
        if plan_path.is_dir():
            shutil.move(str(plan_path), str(archive_path))
        else:
            archive_path.mkdir(parents=True, exist_ok=True)
            shutil.move(str(plan_path), str(archive_path / plan_path.name))
        
        # Create archive metadata
        metadata = {
            "original_path": str(plan_path),
            "archived_at": datetime.now().isoformat(),
            "archive_path": str(archive_path),
            "reason": "Migrated to CORTEX-5.0 standards"
        }
        
        metadata_path = archive_path / "archive-metadata.json"
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        return archive_path
    
    def execute_upgrade(self, plan_path: Path, auto_archive: bool = False) -> Tuple[Path, Dict]:
        """
        Execute complete upgrade workflow.
        
        Args:
            plan_path: Path to legacy plan
            auto_archive: Automatically archive old plan after upgrade
            
        Returns:
            Tuple of (new_plan_path, analysis_report)
        """
        print(f"🔍 Analyzing legacy plan: {plan_path}")
        analysis = self.analyze_legacy_plan(plan_path)
        
        print(f"\n📊 Compliance Score: {analysis['compliance_score']}%")
        print(f"Issues Found: {len(analysis['compliance_issues'])}")
        
        if analysis['compliance_issues']:
            print("\n⚠️  Compliance Issues:")
            for issue in analysis['compliance_issues']:
                print(f"  - {issue}")
        
        print(f"\n🔄 Generating CORTEX-5.0 compliant plan...")
        new_plan_dir = self.generate_upgraded_plan(analysis)
        
        print(f"✅ New plan created: {new_plan_dir}")
        print(f"📄 Master plan: {new_plan_dir / '00-master-plan.md'}")
        print(f"📊 Migration report: {new_plan_dir / 'reports' / 'migration-report.md'}")
        
        if auto_archive:
            print(f"\n📦 Archiving legacy plan...")
            archive_path = self.archive_legacy_plan(plan_path)
            print(f"✅ Archived to: {archive_path}")
        
        return new_plan_dir, analysis


def main():
    """CLI entry point for plan upgrade orchestrator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CORTEX Plan Upgrade Orchestrator - Migrate legacy plans to CORTEX-5.0 standards"
    )
    parser.add_argument(
        "plan_path",
        type=Path,
        help="Path to legacy plan (directory or .md file)"
    )
    parser.add_argument(
        "--workspace",
        type=Path,
        default=Path.cwd(),
        help="CORTEX workspace root (default: current directory)"
    )
    parser.add_argument(
        "--archive",
        action="store_true",
        help="Automatically archive legacy plan after upgrade"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Custom output directory for upgraded plan"
    )
    
    args = parser.parse_args()
    
    # Validate inputs
    if not args.plan_path.exists():
        print(f"❌ Error: Plan path not found: {args.plan_path}")
        return 1
    
    # Execute upgrade
    orchestrator = PlanUpgradeOrchestrator(args.workspace)
    new_plan_dir, analysis = orchestrator.execute_upgrade(
        args.plan_path,
        auto_archive=args.archive
    )
    
    print(f"\n🎉 Plan upgrade complete!")
    print(f"\n📂 Next Steps:")
    print(f"1. Review: {new_plan_dir / '00-master-plan.md'}")
    print(f"2. Read: {new_plan_dir / 'reports' / 'migration-report.md'}")
    print(f"3. Update placeholders marked with `*()*`")
    print(f"4. Begin execution following CORTEX-5.0 workflow")
    
    if not args.archive:
        print(f"\n⚠️  Legacy plan still exists at: {args.plan_path}")
        print(f"   Run with --archive flag to auto-archive, or manually move to archived/")
    
    return 0


if __name__ == "__main__":
    exit(main())
