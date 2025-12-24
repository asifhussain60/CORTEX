# CORTEX 3.0 → 4.0 Planning Folder Organization Plan

**Purpose:** Organize 30+ root-level files into logical folder structure  
**Version:** 1.0  
**Created:** December 20, 2025

---

## 📋 Current State (DISORGANIZED)

**Problem:** 30+ files in root of `CORTEX-3.0-4.0/` folder

**Files in Root:**
```
00-MASTER-PLAN.md ✅ (stays)
CORTEX4-STATUS.md ✅ (stays)
MASTER-PLAN.md (archive - original)
AGENTIC-ENHANCEMENTS-IMPLEMENTATION-PLAN.md
CORTEX-4.0-ARCHITECTURE-DESIGN.md
CORTEX-LENS-ARCHITECTURE-REDESIGN.md
CORTEX-LENS-PHASE-A-SPECS.md
FEATURE-DISCOVERY-ORCHESTRATOR-DESIGN.md
GIT-COMMIT-POLICY.md
IDE-DETECTION-IMPLEMENTATION-PLAN.md
IDE-DOCUMENTATION-AUTO-GENERATION-SPEC.md
MASTER-PLAN-GAP-RESOLUTION.md
MIGRATION-GUIDE.md ✅ (stays)
NEXT-STEPS-COMPLETION.md
ORCHESTRATOR-IMPACT-ANALYSIS.md ✅ (stays)
PHASE-1-PROGRESS-DAY-2.md
PHASE-1-PROGRESS-DAY-3.md
PHASE-1.5-SCRIPT-CONSOLIDATION.md
PHASE-3-COMPLETION-SUMMARY.md
PHASE-3-MIGRATION-PLAN.md
PHASE-RESEQUENCING-TODO.md
PROGRESS-TRACKING-INTEGRATION-CHECKLIST.md
PROGRESS-TRACKING-STANDARD.md
README.md ✅ (stays)
SECURITY-LEARNING-INTEGRATION-SPEC.md
TDD-ORCHESTRATOR-REDESIGN.md
TDD-ORCHESTRATOR-V4-REFERENCE.md
technical-documentation-orchestrator-design.md
TECHNICAL-DOCUMENTATION-ORCHESTRATOR-INTEGRATION.md
```

**Existing Folders:**
- `archive/` - Completed/old work
- `metadata/` - YAML metadata
- `phases/` - Phase detail files (empty - pending extraction)
- `reports/` - Status reports
- `sub-plans/` - Sub-plan details
- `supporting-docs/` - Supporting documents
- `worker-plans/` - Worker plan details
- `workers/` - Worker detail files

---

## 🎯 Proposed Structure

```
CORTEX-3.0-4.0/
├── 00-MASTER-PLAN.md              # Master hub (overview)
├── CORTEX4-STATUS.md              # Status tracker
├── MIGRATION-GUIDE.md             # Token optimization guide
├── ORCHESTRATOR-IMPACT-ANALYSIS.md # Impact analysis
├── README.md                       # Navigation guide
│
├── metadata/                       # Machine-readable metadata
│   └── plan-metadata.yaml
│
├── phases/                         # Phase detail files
│   ├── README.md
│   └── (phase files to be extracted)
│
├── workers/                        # Worker detail files
│   └── (week-specific files)
│
├── architecture/                   # NEW: Architecture designs
│   ├── CORTEX-4.0-ARCHITECTURE-DESIGN.md
│   ├── CORTEX-LENS-ARCHITECTURE-REDESIGN.md
│   ├── FEATURE-DISCOVERY-ORCHESTRATOR-DESIGN.md
│   ├── TDD-ORCHESTRATOR-REDESIGN.md
│   ├── technical-documentation-orchestrator-design.md
│   └── IDE-DETECTION-IMPLEMENTATION-PLAN.md
│
├── specs/                          # NEW: Specifications
│   ├── CORTEX-LENS-PHASE-A-SPECS.md
│   ├── SECURITY-LEARNING-INTEGRATION-SPEC.md
│   ├── IDE-DOCUMENTATION-AUTO-GENERATION-SPEC.md
│   └── TECHNICAL-DOCUMENTATION-ORCHESTRATOR-INTEGRATION.md
│
├── implementation-plans/           # NEW: Implementation plans
│   ├── AGENTIC-ENHANCEMENTS-IMPLEMENTATION-PLAN.md
│   ├── PHASE-3-MIGRATION-PLAN.md
│   └── PHASE-1.5-SCRIPT-CONSOLIDATION.md
│
├── progress/                       # NEW: Progress tracking
│   ├── PHASE-1-PROGRESS-DAY-2.md
│   ├── PHASE-1-PROGRESS-DAY-3.md
│   ├── PHASE-3-COMPLETION-SUMMARY.md
│   ├── MASTER-PLAN-GAP-RESOLUTION.md
│   └── NEXT-STEPS-COMPLETION.md
│
├── standards/                      # NEW: Standards & policies
│   ├── PROGRESS-TRACKING-STANDARD.md
│   ├── GIT-COMMIT-POLICY.md
│   ├── PROGRESS-TRACKING-INTEGRATION-CHECKLIST.md
│   └── PHASE-RESEQUENCING-TODO.md
│
├── references/                     # NEW: Reference docs
│   └── TDD-ORCHESTRATOR-V4-REFERENCE.md
│
├── archive/                        # Archived/completed work
│   ├── MASTER-PLAN-original-v1.5.md (to be moved)
│   └── old-plans/
│
├── reports/                        # Status reports
│   └── (existing reports)
│
└── supporting-docs/               # Supporting documents
    └── (existing docs)
```

---

## 📊 File Categorization

### Keep in Root (5 files)
- `00-MASTER-PLAN.md` - Master hub
- `CORTEX4-STATUS.md` - Status tracker
- `MIGRATION-GUIDE.md` - Token optimization guide
- `ORCHESTRATOR-IMPACT-ANALYSIS.md` - Impact analysis
- `README.md` - Navigation

### Move to architecture/ (6 files)
- `CORTEX-4.0-ARCHITECTURE-DESIGN.md`
- `CORTEX-LENS-ARCHITECTURE-REDESIGN.md`
- `FEATURE-DISCOVERY-ORCHESTRATOR-DESIGN.md`
- `TDD-ORCHESTRATOR-REDESIGN.md`
- `technical-documentation-orchestrator-design.md`
- `IDE-DETECTION-IMPLEMENTATION-PLAN.md`

### Move to specs/ (4 files)
- `CORTEX-LENS-PHASE-A-SPECS.md`
- `SECURITY-LEARNING-INTEGRATION-SPEC.md`
- `IDE-DOCUMENTATION-AUTO-GENERATION-SPEC.md`
- `TECHNICAL-DOCUMENTATION-ORCHESTRATOR-INTEGRATION.md`

### Move to implementation-plans/ (3 files)
- `AGENTIC-ENHANCEMENTS-IMPLEMENTATION-PLAN.md`
- `PHASE-3-MIGRATION-PLAN.md`
- `PHASE-1.5-SCRIPT-CONSOLIDATION.md`

### Move to progress/ (5 files)
- `PHASE-1-PROGRESS-DAY-2.md`
- `PHASE-1-PROGRESS-DAY-3.md`
- `PHASE-3-COMPLETION-SUMMARY.md`
- `MASTER-PLAN-GAP-RESOLUTION.md`
- `NEXT-STEPS-COMPLETION.md`

### Move to standards/ (4 files)
- `PROGRESS-TRACKING-STANDARD.md`
- `GIT-COMMIT-POLICY.md`
- `PROGRESS-TRACKING-INTEGRATION-CHECKLIST.md`
- `PHASE-RESEQUENCING-TODO.md`

### Move to references/ (1 file)
- `TDD-ORCHESTRATOR-V4-REFERENCE.md`

### Move to archive/ (1 file)
- `MASTER-PLAN.md` → `MASTER-PLAN-original-v1.5.md`

---

## 🔧 Implementation Steps

### Phase 1: Create New Folders
```powershell
# Create new category folders
New-Item -ItemType Directory -Path "architecture"
New-Item -ItemType Directory -Path "specs"
New-Item -ItemType Directory -Path "implementation-plans"
New-Item -ItemType Directory -Path "progress"
New-Item -ItemType Directory -Path "standards"
New-Item -ItemType Directory -Path "references"
```

### Phase 2: Move Files
```powershell
# Architecture
Move-Item "CORTEX-4.0-ARCHITECTURE-DESIGN.md" "architecture/"
Move-Item "CORTEX-LENS-ARCHITECTURE-REDESIGN.md" "architecture/"
Move-Item "FEATURE-DISCOVERY-ORCHESTRATOR-DESIGN.md" "architecture/"
Move-Item "TDD-ORCHESTRATOR-REDESIGN.md" "architecture/"
Move-Item "technical-documentation-orchestrator-design.md" "architecture/"
Move-Item "IDE-DETECTION-IMPLEMENTATION-PLAN.md" "architecture/"

# Specs
Move-Item "CORTEX-LENS-PHASE-A-SPECS.md" "specs/"
Move-Item "SECURITY-LEARNING-INTEGRATION-SPEC.md" "specs/"
Move-Item "IDE-DOCUMENTATION-AUTO-GENERATION-SPEC.md" "specs/"
Move-Item "TECHNICAL-DOCUMENTATION-ORCHESTRATOR-INTEGRATION.md" "specs/"

# Implementation Plans
Move-Item "AGENTIC-ENHANCEMENTS-IMPLEMENTATION-PLAN.md" "implementation-plans/"
Move-Item "PHASE-3-MIGRATION-PLAN.md" "implementation-plans/"
Move-Item "PHASE-1.5-SCRIPT-CONSOLIDATION.md" "implementation-plans/"

# Progress
Move-Item "PHASE-1-PROGRESS-DAY-2.md" "progress/"
Move-Item "PHASE-1-PROGRESS-DAY-3.md" "progress/"
Move-Item "PHASE-3-COMPLETION-SUMMARY.md" "progress/"
Move-Item "MASTER-PLAN-GAP-RESOLUTION.md" "progress/"
Move-Item "NEXT-STEPS-COMPLETION.md" "progress/"

# Standards
Move-Item "PROGRESS-TRACKING-STANDARD.md" "standards/"
Move-Item "GIT-COMMIT-POLICY.md" "standards/"
Move-Item "PROGRESS-TRACKING-INTEGRATION-CHECKLIST.md" "standards/"
Move-Item "PHASE-RESEQUENCING-TODO.md" "standards/"

# References
Move-Item "TDD-ORCHESTRATOR-V4-REFERENCE.md" "references/"

# Archive
Move-Item "MASTER-PLAN.md" "archive/MASTER-PLAN-original-v1.5.md"
```

### Phase 3: Update References

**Files that reference moved documents:**
1. `00-MASTER-PLAN.md` - Update all links
2. `CORTEX4-STATUS.md` - Update phase links
3. `README.md` - Update navigation links
4. `MIGRATION-GUIDE.md` - Update file paths
5. `planning-system-4.0-manifest.yaml` - Update linked documents

**Reference Update Patterns:**
```
OLD: ./CORTEX-LENS-ARCHITECTURE-REDESIGN.md
NEW: ./architecture/CORTEX-LENS-ARCHITECTURE-REDESIGN.md

OLD: ./TDD-ORCHESTRATOR-REDESIGN.md
NEW: ./architecture/TDD-ORCHESTRATOR-REDESIGN.md

OLD: ./SECURITY-LEARNING-INTEGRATION-SPEC.md
NEW: ./specs/SECURITY-LEARNING-INTEGRATION-SPEC.md
```

### Phase 4: Update Navigation

Update `README.md` with new structure:
```markdown
## 📁 Folder Structure

- **Root Files:** Status, Master Hub, Migration Guide, Impact Analysis
- **metadata/** - Machine-readable YAML
- **phases/** - Phase detail files
- **workers/** - Week-specific work
- **architecture/** - System architecture designs
- **specs/** - Technical specifications
- **implementation-plans/** - Implementation plans
- **progress/** - Progress tracking documents
- **standards/** - Standards & policies
- **references/** - Reference documentation
- **archive/** - Historical documents
- **reports/** - Status reports
- **supporting-docs/** - Supporting documentation
```

---

## 🔍 Reference Update Scan

**Find all references to moved files:**
```powershell
# Scan for references
Get-ChildItem -Recurse -Include *.md,*.yaml | 
    Select-String -Pattern "CORTEX-LENS-ARCHITECTURE-REDESIGN|TDD-ORCHESTRATOR-REDESIGN|SECURITY-LEARNING-INTEGRATION-SPEC" |
    Select-Object Path, LineNumber, Line
```

---

## ✅ Validation Checklist

**Structure:**
- [ ] 6 new folders created
- [ ] 24 files moved to appropriate folders
- [ ] 5 root files remain
- [ ] Original MASTER-PLAN.md archived

**References:**
- [ ] 00-MASTER-PLAN.md links updated
- [ ] CORTEX4-STATUS.md links updated
- [ ] README.md navigation updated
- [ ] Manifest YAML links updated
- [ ] All cross-references verified

**Navigation:**
- [ ] README.md shows new structure
- [ ] All links tested and working
- [ ] No broken references
- [ ] Folder index files created (optional)

---

## 🚀 Planning Orchestrator Integration

**Current State:** Orchestrator does NOT generate hierarchical structure

**Needed Enhancement (Week 9 Intelligence Layer):**

```python
class PlanningOrchestrator:
    def generate_plan(self, complexity: PlanComplexity) -> PlanResult:
        """Generate plan with token-optimized structure for complex plans."""
        
        if complexity >= PlanComplexity.MEDIUM:
            # Generate hierarchical structure
            return self._generate_hierarchical_plan()
        else:
            # Single file for simple plans
            return self._generate_single_file_plan()
    
    def _generate_hierarchical_plan(self) -> PlanResult:
        """
        Generate token-optimized hierarchical plan structure.
        
        Structure:
        - {PLAN-NAME}-STATUS.md (status tracker)
        - 00-MASTER-PLAN.md (master hub)
        - metadata/plan-metadata.yaml (metadata)
        - phases/phase-{id}.md (phase files)
        - architecture/ (design docs)
        - specs/ (specifications)
        - implementation-plans/ (plans)
        - progress/ (tracking)
        - standards/ (policies)
        """
        plan_folder = self._create_plan_folder_structure()
        
        # Generate status file
        self._generate_status_file(plan_folder)
        
        # Generate master hub
        self._generate_master_hub(plan_folder)
        
        # Generate metadata
        self._generate_metadata_yaml(plan_folder)
        
        # Generate phase files
        for phase in self.plan_data['phases']:
            self._generate_phase_file(plan_folder, phase)
        
        return PlanResult(success=True, plan_folder=plan_folder)
```

**Timeline:** Week 9-10 (Planning System Intelligence Layer)

---

**Last Updated:** December 20, 2025  
**Status:** Organization plan complete, implementation pending  
**Next Steps:** Execute file moves and reference updates
