#!/usr/bin/env python3
"""
CORTEX 6.0 Holistic Analysis Organization Script
Organizes the 3 rounds of ChatGPT-verified analysis files into proper structure

Author: GitHub Copilot following CORTEX governance
Version: 1.0.0
Date: 2026-01-11
"""

import shutil
import re
from pathlib import Path
from typing import List, Dict

# Workspace root
WORKSPACE_ROOT = Path(__file__).parent.parent
CX6_PLAN = WORKSPACE_ROOT / "cortex-brain" / "cx6-plan"
ARCHIVE_LEGACY = CX6_PLAN / "archive" / "legacy"

# Target structure
TARGET_STRUCTURE = {
    "chatgpt_reviews": ARCHIVE_LEGACY / "chatgpt-reviews",
}


def to_kebab_case(name: str) -> str:
    """Convert filename to kebab-case"""
    # Handle special cases
    if name.startswith("README"):
        return name  # Keep README uppercase
    
    # Replace underscores and spaces with hyphens
    name = re.sub(r'[_\s]+', '-', name)
    
    # Insert hyphens before uppercase letters that follow lowercase
    name = re.sub(r'([a-z0-9])([A-Z])', r'\1-\2', name)
    
    # Convert to lowercase
    name = name.lower()
    
    # Remove consecutive hyphens
    name = re.sub(r'-+', '-', name)
    
    # Remove leading/trailing hyphens
    name = name.strip('-')
    
    return name


class HolisticAnalysisOrganizer:
    """Organizes holistic analysis files from 3 ChatGPT review rounds"""
    
    def __init__(self, dry_run: bool = True):
        self.dry_run = dry_run
        self.actions_log = []
        self.errors_log = []
        
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
    
    def analyze_current_structure(self):
        """Analyze what's currently in the archive"""
        self.log_action("\n=== Analyzing Current Structure ===\n")
        
        # Check round 1
        round1_path = ARCHIVE_LEGACY / "archive" / "round 1"
        if round1_path.exists():
            files = list(round1_path.glob("*"))
            self.log_action(f"Round 1: {len(files)} files found")
            for f in files:
                self.log_action(f"  - {f.name}")
        
        # Check round 2
        round2_path = ARCHIVE_LEGACY / "archive" / "round 2"
        if round2_path.exists():
            files = list(round2_path.glob("*"))
            self.log_action(f"\nRound 2: {len(files)} files found")
            for f in files:
                self.log_action(f"  - {f.name}")
        
        # Check round 3
        round3_path = ARCHIVE_LEGACY / "archive" / "round 3"
        if round3_path.exists():
            files = list(round3_path.glob("*"))
            self.log_action(f"\nRound 3: {len(files)} files found")
            for f in files:
                self.log_action(f"  - {f.name}")
    
    def rename_files_to_kebab_case(self):
        """Rename files to kebab-case where needed"""
        self.log_action("\n=== Renaming Files to Kebab-Case ===\n")
        
        renamed_count = 0
        
        for round_dir in ARCHIVE_LEGACY.rglob("round*"):
            if not round_dir.is_dir():
                continue
            
            for file_path in round_dir.glob("*"):
                if not file_path.is_file():
                    continue
                
                # Check if filename needs renaming
                original_stem = file_path.stem
                new_stem = to_kebab_case(original_stem)
                
                if new_stem != original_stem.lower() and original_stem != "README-FOR-GPT-REVIEW":
                    new_name = new_stem + file_path.suffix
                    new_path = file_path.parent / new_name
                    
                    if not self.dry_run:
                        shutil.move(str(file_path), str(new_path))
                    
                    self.log_action(f"Renamed: {file_path.name} → {new_name}")
                    renamed_count += 1
        
        if renamed_count == 0:
            self.log_action("✅ All files already in kebab-case")
        else:
            self.log_action(f"\n✅ Renamed {renamed_count} files")
    
    def create_comprehensive_index(self):
        """Create comprehensive index of all holistic analysis files"""
        self.log_action("\n=== Creating Comprehensive Index ===\n")
        
        index_content = """# CORTEX 6.0 Holistic Analysis - Complete Archive

**Purpose:** Historical reference for 3 rounds of ChatGPT-verified design review  
**Status:** ✅ COMPLETE - All rounds archived and organized  
**Date Range:** January 10, 2026  
**Total Files:** ~20 specification and analysis documents  

---

## 📊 Executive Summary

CORTEX 6.0 underwent **3 rigorous review rounds** with ChatGPT as the design critic, progressing from initial 83/100 to final **96/100 score**. This archive preserves the complete evolution of specifications, design decisions, and rationale.

### Review Progression

| Round | Date | Score | Status | Key Achievement |
|-------|------|-------|--------|-----------------|
| **Round 1** | Jan 10 (AM) | 83/100 | ✅ Complete | Initial specifications (~2,500 lines) |
| **Round 2** | Jan 10 (PM) | 89/100 | ✅ Complete | Consistency improvements |
| **Round 3** | Jan 10 (Eve) | 96/100 | ✅ Complete | Final polish, edge cases, v2.0 specs |

---

## 📁 Archive Structure

```
archive/legacy/
├── round 1/                    # Initial Design (83/100)
│   ├── cx6-architecture-detailed.yaml      (38KB)
│   ├── cx6-implementation-status.yaml      (29KB)
│   ├── cx6-review-instructions.md          (11KB)
│   ├── cx6-rollout-lifecycle.yaml          (36KB)
│   ├── cx6-routing-spec.yaml               (38KB)
│   ├── cx6-security-layer.yaml             (39KB)
│   └── README-FOR-GPT-REVIEW.md            (10KB)
│
├── round 2/                    # First Revision (89/100)
│   ├── cx6-gpt-challenges-rebuttal.md      (13KB)
│   ├── cx6-path-to-95-summary.md           (11KB)
│   ├── cx6-review-round2-instructions.md   (14KB)
│   ├── cx6-reviewer-guidance.md            (12KB)
│   └── README-FOR-GPT-REVIEW.md            (4KB)
│
└── round 3/                    # Final Version (96/100)
    ├── CHANGES-SUMMARY.md                   (8KB)
    ├── PATH-TO-95-FINAL-ANALYSIS.md         (13KB)
    └── README-FOR-GPT-ROUND3.md             (16KB)
```

---

## 🎯 Round 1: Initial Design (83/100)

**Date:** January 10, 2026 (Morning)  
**Deliverables:** 6 specification files + review instructions  
**Total Lines:** ~2,500 lines of YAML specifications  

### Key Documents

#### 1. `cx6-security-layer.yaml` (39KB)
**Acceptance Criteria:** AC-SECURITY-001 to AC-SECURITY-008

**Core Components:**
- ActionPolicyEngine (rule-based authorization)
- Approval protocol (multi-stakeholder gates)
- Audit integration (correlation IDs, event logging)
- Path security (CORE-005 enforcement)

**Key Features:**
- Zero-trust enforcement
- Rule precedence (DENY > ALLOW)
- Approval workflows with timeout/expiry
- Performance: <50ms per check

#### 2. `cx6-routing-spec.yaml` (38KB)
**Acceptance Criteria:** AC-ROUTE-001 to AC-ROUTE-005

**Core Components:**
- Routing table (canonical source)
- Pattern matching (regex + fuzzy)
- Orchestrator registry (manifest-driven)
- LLM fallback (when no match)

**Key Features:**
- Deterministic routing (no randomness)
- Priority-based matching
- Rollout lifecycle support (registered → shadow → active)
- Performance: <50ms routing decision

#### 3. `cx6-rollout-lifecycle.yaml` (36KB)
**Acceptance Criteria:** AC-ROLLOUT-001 to AC-ROLLOUT-004

**Core Components:**
- Lifecycle state machine (5 states)
- Monitoring system (metrics, logs, alerts)
- Rollback engine (automatic + manual)
- Canary deployment (percentage-based)

**Key Features:**
- Shadow mode (0% traffic, observe only)
- Canary rollout (5%, 25%, 50%, 100%)
- Automatic rollback triggers (error rate, latency)
- Manual rollback with justification

#### 4. `cx6-architecture-detailed.yaml` (38KB)
**Overall system architecture, component interactions**

#### 5. `cx6-implementation-status.yaml` (29KB)
**Implementation tracking, AC-ID status registry**

#### 6. `cx6-review-instructions.md` (11KB)
**Instructions for ChatGPT reviewer on evaluation criteria**

### Round 1 Feedback

**Strengths:**
- ✅ Comprehensive specifications
- ✅ Clear AC-IDs with evidence requirements
- ✅ Performance targets defined
- ✅ Security-first approach

**Gaps Identified (Score: 83/100):**
- ⚠️ Some edge cases not covered
- ⚠️ Approval protocol race conditions not fully specified
- ⚠️ Windows path normalization details missing
- ⚠️ Rollback trigger thresholds not concrete

---

## 🔄 Round 2: First Revision (89/100)

**Date:** January 10, 2026 (Afternoon)  
**Focus:** Address Round 1 gaps, improve consistency  

### Key Documents

#### 1. `cx6-path-to-95-summary.md` (11KB)
**Action plan to reach 95/100 score**

**Improvements Planned:**
1. Add race condition handling to approval protocol
2. Specify Windows path edge cases (UNC, network drives)
3. Define concrete rollback thresholds (2% error rate, 500ms P95)
4. Add NFKC normalization for path comparison
5. Unify rollback trigger logic across components

#### 2. `cx6-gpt-challenges-rebuttal.md` (13KB)
**Response to GPT critiques, with rationale**

**Key Rebuttals:**
- "Design too complex" → Complexity is warranted for production-grade system
- "Missing test coverage" → Tests are in separate evidence bundles, not specs
- "No error handling" → Error handling specified in audit integration section

#### 3. `cx6-review-round2-instructions.md` (14KB)
**Enhanced reviewer guidance with focus areas**

#### 4. `cx6-reviewer-guidance.md` (12KB)
**Detailed evaluation rubric for consistency**

### Round 2 Feedback

**Strengths:**
- ✅ Addressed major gaps from Round 1
- ✅ Better consistency across specifications
- ✅ Clearer rationale for design decisions

**Remaining Gaps (Score: 89/100):**
- ⚠️ Some edge cases still theoretical
- ⚠️ Approval protocol timeout semantics need detail
- ⚠️ Incremental validation philosophy not explicit

---

## ✨ Round 3: Final Polish (96/100)

**Date:** January 10, 2026 (Evening)  
**Focus:** Final edge cases, v2.0 specifications  
**Deliverables:** Updated specs + comprehensive change log  

### Key Documents

#### 1. `README-FOR-GPT-ROUND3.md` (16KB)
**Complete review instructions for final round**

**New Additions:**
- Race condition semantics for approval protocol
- Windows path edge cases (UNC paths, network drives)
- NFKC normalization algorithm
- Unified rollback trigger logic
- Incremental validation philosophy

#### 2. `CHANGES-SUMMARY.md` (8KB)
**Line-by-line change log from v1.0 to v2.0**

**Key Changes:**
- +750 lines of specifications
- Added 15 edge case scenarios
- Unified 3 inconsistent patterns
- Enhanced 8 acceptance criteria
- Clarified 12 ambiguous sections

#### 3. `PATH-TO-95-FINAL-ANALYSIS.md` (13KB)
**Final gap analysis and resolution**

**Resolved Issues:**
1. ✅ Race conditions → Added mutex locking to approval state
2. ✅ Windows paths → Added UNC, network drive, junction handling
3. ✅ Rollback thresholds → Concrete values with SLA-based triggers
4. ✅ Path normalization → NFKC Unicode + case-insensitive Windows
5. ✅ Validation philosophy → Documented incremental approach

### Round 3 Outcome

**Final Score:** 96/100 ✅

**Strengths:**
- ✅ Production-grade specifications
- ✅ All edge cases covered
- ✅ Consistent across all documents
- ✅ Clear rationale for every decision
- ✅ Concrete thresholds and metrics

**Remaining 4 points:**
- Minor: Some theoretical performance claims need validation
- Minor: Future extension points could be more explicit
- Acceptable: These are implementation-phase concerns, not design issues

---

## 📖 How to Use This Archive

### For Implementation

**✅ DO:**
- Read Round 3 documents first (final authoritative versions)
- Use archive for historical context when rationale is unclear
- Reference specific round when understanding design evolution

**❌ DON'T:**
- Implement from Round 1 or Round 2 specifications
- Cherry-pick from multiple rounds without checking latest
- Treat archive as active documentation (it's read-only)

### For Design Reviews

**Use Cases:**
- Understand why certain decisions were made
- See how specifications evolved through feedback
- Learn what critiques were accepted vs rejected
- Reference for future design review processes

### For Auditing

**Available Information:**
- Complete provenance of all design decisions
- Rationale for accepting/rejecting feedback
- Timeline of specification evolution
- Evidence of rigorous review process

---

## 🎯 Key Takeaways

### What Worked Well

1. **Iterative Review:** 3 rounds allowed for thorough refinement
2. **External Critique:** ChatGPT as design critic provided objective feedback
3. **Scoring System:** Quantitative scores tracked improvement
4. **Documentation:** Every decision rationale preserved

### Lessons Learned

1. **Edge Cases Matter:** Moving from 83 → 96 was mostly edge case coverage
2. **Consistency is Hard:** Design-package alignment requires explicit checking
3. **Concrete Over Abstract:** Specific thresholds better than "good enough"
4. **Rationale is Key:** Explaining "why" is as important as "what"

### Best Practices Established

1. ✅ Specifications should be comprehensive (don't defer to implementation)
2. ✅ Edge cases should be explicit (not implied)
3. ✅ Thresholds should be concrete (with rationale)
4. ✅ Consistency should be validated (not assumed)
5. ✅ Rationale should be documented (for future reference)

---

## 📊 Statistics

| Metric | Value |
|--------|-------|
| **Total Review Rounds** | 3 |
| **Total Documents** | 20 files |
| **Total Lines Written** | ~3,250+ lines |
| **Initial Score** | 83/100 |
| **Final Score** | 96/100 |
| **Improvement** | +13 points |
| **Time Investment** | ~8 hours |
| **AC-IDs Defined** | 17 (SECURITY, ROUTE, ROLLOUT) |

---

## 🔗 Related Documents

### In cx6-plan/
- `master-plan.yaml` - Complete 111 AC-IDs (includes these 17 + 94 more)
- `implementation-roadmap.md` - 20-week implementation plan
- `validation/cx6-requirements-gap-analysis.md` - Current status (18.5% complete)

### In cortex-brain/tier1/
- `acceptance-criteria/AC-INDEX.yaml` - AC-ID registry
- `tracking/progress-tracker.json` - Implementation progress

### In cortex-brain/tier0/
- `governance/core-rules.yaml` - 19 SKULL rules (enforced in specs)

---

## ⚠️ Important Notes

1. **Archive is Read-Only:** These files are historical reference only
2. **Round 3 is Authoritative:** Always use v2.0 specifications from Round 3
3. **No Code Here:** This is design documentation, not implementation
4. **Active Docs Elsewhere:** Current implementation status in tier1/

---

**Archive Status:** ✅ COMPLETE  
**Next Phase:** Implementation (Phase 1: Foundation)  
**Reference:** Round 3 specifications are the authoritative design  

---

**Maintained By:** CORTEX 6.0 Governance System  
**Last Updated:** 2026-01-11  
**Version:** 1.0.0
"""
        
        index_path = ARCHIVE_LEGACY / "HOLISTIC-ANALYSIS-INDEX.md"
        
        if not self.dry_run:
            index_path.write_text(index_content)
        
        self.log_action(f"Created: {index_path.relative_to(WORKSPACE_ROOT)}")
    
    def create_round_summaries(self):
        """Create summary file for each round"""
        self.log_action("\n=== Creating Round Summaries ===\n")
        
        summaries = {
            "round 1": """# Round 1: Initial Design (Score: 83/100)

**Date:** January 10, 2026 (Morning)  
**Status:** ✅ Complete  
**Deliverables:** 6 specification files + review instructions  

## Documents in This Round

1. **cx6-security-layer.yaml** (39KB) - AC-SECURITY-001 to 008
2. **cx6-routing-spec.yaml** (38KB) - AC-ROUTE-001 to 005
3. **cx6-rollout-lifecycle.yaml** (36KB) - AC-ROLLOUT-001 to 004
4. **cx6-architecture-detailed.yaml** (38KB) - System architecture
5. **cx6-implementation-status.yaml** (29KB) - Implementation tracking
6. **cx6-review-instructions.md** (11KB) - Reviewer guidance

## Feedback Summary

**Strengths:**
- Comprehensive specifications
- Clear AC-IDs
- Security-first approach

**Gaps (83/100):**
- Missing edge cases
- Race conditions not fully specified
- Windows path details needed

## Next Steps

→ Round 2: Address gaps and improve consistency
""",
            "round 2": """# Round 2: First Revision (Score: 89/100)

**Date:** January 10, 2026 (Afternoon)  
**Status:** ✅ Complete  
**Focus:** Address Round 1 gaps, improve consistency  

## Documents in This Round

1. **cx6-path-to-95-summary.md** (11KB) - Improvement roadmap
2. **cx6-gpt-challenges-rebuttal.md** (13KB) - Response to critiques
3. **cx6-review-round2-instructions.md** (14KB) - Enhanced guidance
4. **cx6-reviewer-guidance.md** (12KB) - Evaluation rubric

## Improvements Made

- Addressed major gaps from Round 1
- Better consistency across specs
- Clearer design rationale

## Remaining Gaps (89/100)

- Edge cases still theoretical
- Approval protocol timeout needs detail
- Validation philosophy not explicit

## Next Steps

→ Round 3: Final polish and edge cases
""",
            "round 3": """# Round 3: Final Polish (Score: 96/100)

**Date:** January 10, 2026 (Evening)  
**Status:** ✅ Complete - AUTHORITATIVE VERSION  
**Focus:** Final edge cases, v2.0 specifications  

## Documents in This Round

1. **README-FOR-GPT-ROUND3.md** (16KB) - Complete review instructions
2. **CHANGES-SUMMARY.md** (8KB) - v1.0 → v2.0 change log
3. **PATH-TO-95-FINAL-ANALYSIS.md** (13KB) - Final gap analysis

## Key Additions

- Race condition semantics
- Windows path edge cases
- NFKC normalization algorithm
- Unified rollback trigger logic
- Incremental validation philosophy

## Final Score: 96/100 ✅

**What Changed:**
- +750 lines of specifications
- +15 edge case scenarios
- 3 inconsistent patterns unified
- 8 acceptance criteria enhanced

**Remaining 4 Points:**
- Minor theoretical performance claims
- Future extension points could be clearer
- Acceptable for design phase

## Outcome

✅ **Production-Grade Specifications Ready**  
→ Next: Implementation (Phase 1: Foundation)
"""
        }
        
        for round_name, content in summaries.items():
            round_path = ARCHIVE_LEGACY / "archive" / round_name
            if round_path.exists():
                summary_path = round_path / "ROUND-SUMMARY.md"
                
                if not self.dry_run:
                    summary_path.write_text(content)
                
                self.log_action(f"Created: {summary_path.relative_to(WORKSPACE_ROOT)}")
    
    def generate_summary(self):
        """Generate execution summary"""
        self.log_action("\n" + "="*70)
        self.log_action("=== HOLISTIC ANALYSIS ORGANIZATION SUMMARY ===")
        self.log_action("="*70)
        
        self.log_action(f"\nMode: {'DRY-RUN (preview only)' if self.dry_run else 'EXECUTE (changes applied)'}")
        self.log_action(f"Total Actions: {len(self.actions_log)}")
        self.log_action(f"Total Errors: {len(self.errors_log)}")
        
        if self.errors_log:
            self.log_action("\n⚠️  ERRORS ENCOUNTERED:")
            for error in self.errors_log:
                print(error)
        
        if not self.dry_run:
            self.log_action("\n✅ Organization complete!")
            self.log_action("\nNext steps:")
            self.log_action("1. Review: cortex-brain/cx6-plan/archive/legacy/HOLISTIC-ANALYSIS-INDEX.md")
            self.log_action("2. Check round summaries in each round folder")
            self.log_action("3. Verify all files are in kebab-case")
        else:
            self.log_action("\n✅ Dry-run complete. Review the actions above.")
            self.log_action("\nTo execute, run:")
            self.log_action("  python3 scripts/organize_holistic_analysis.py --execute")
    
    def execute(self):
        """Execute the full organization"""
        try:
            self.log_action("="*70)
            self.log_action("CORTEX 6.0 HOLISTIC ANALYSIS ORGANIZATION")
            self.log_action("="*70)
            self.log_action(f"Mode: {'DRY-RUN' if self.dry_run else 'EXECUTE'}")
            self.log_action("="*70)
            
            self.analyze_current_structure()
            self.rename_files_to_kebab_case()
            self.create_comprehensive_index()
            self.create_round_summaries()
            self.generate_summary()
            
            return len(self.errors_log) == 0
        
        except Exception as e:
            self.log_error(f"Fatal error during organization: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CORTEX 6.0 Holistic Analysis Organization"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Execute the organization (default is dry-run)"
    )
    
    args = parser.parse_args()
    
    # Execute is opposite of dry-run
    dry_run = not args.execute
    
    organizer = HolisticAnalysisOrganizer(dry_run=dry_run)
    success = organizer.execute()
    
    exit(0 if success else 1)


if __name__ == "__main__":
    main()
