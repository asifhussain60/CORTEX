NO_ROOT_SUMMARY_DOCUMENTS: Repository Organization Standard - STRICT ENFORCEMENT

Real incident (2025-11-25 - dev environment):
- CORTEX created files in repository root instead of CORTEX folder
- User: "Found another issue in CORTEX in dev environment. CORTEX was 
  creating files in the root of the repo instead of the CORTEX folder."
- User: "Add a rule to make this forbidden. No summary, update, reports 
  should be created in the root of the repo."
- Result: Upgraded from "warning" to "blocked" severity

Why Root-Level Documents Are BLOCKED:

1. Repository Clutter (Critical Issue):
   - Root directory becomes unnavigable with accumulated documents
   - Hard to find important files (README, LICENSE, package.json)
   - Git status becomes noisy (dozens of unrelated files)
   - New contributors confused by file soup
   - Professional appearance destroyed

2. Loss of Context:
   - No categorization = documents impossible to find
   - "Which report is the latest?" ← unanswerable
   - "Where's the security analysis?" ← lost in root
   - Search becomes time-consuming guessing game
   - Historical context lost (no folder-based organization)

3. Merge Conflicts:
   - Multiple people creating documents in root simultaneously
   - Filename collisions extremely likely
   - No clear ownership or hierarchy
   - Git conflicts on unrelated files

4. Violates CORTEX Organization Mandate:
   - CORTEX has structured document system (cortex-brain/documents/)
   - Category-based organization already exists and works
   - Ignoring structure creates technical debt
   - Future migration becomes expensive

5. Embedded Installation Chaos:
   - When CORTEX embedded in user repo (e.g., NOOR-CANVAS/CORTEX/)
   - Root-level CORTEX files pollute user's application repository
   - User repo becomes mixed CORTEX + application artifacts
   - Cleanup difficult (which files are CORTEX vs application?)

CORTEX Document Structure (MANDATORY):

```
CORTEX/                           ← CORTEX folder (standalone or embedded)
  cortex-brain/
    documents/
      ├── reports/                # Implementation completion, status reports
      │   ├── CORTEX-3.0-FINAL-REPORT.md
      │   ├── PHASE-0-COMPLETION-REPORT.md
      │   └── ISSUE-67-FIX-REPORT.md
      │
      ├── analysis/               # Deep investigations, performance analysis
      │   ├── ROUTER-PERFORMANCE-ANALYSIS.md
      │   ├── TOKEN-OPTIMIZATION-ANALYSIS.md
      │   └── SECURITY-AUDIT-2025-11-25.md
      │
      ├── summaries/              # Quick overviews, daily progress
      │   ├── TIER3-IMPLEMENTATION-SUMMARY.md
      │   ├── WEEKLY-PROGRESS-SUMMARY.md
      │   └── SPRINT-23-SUMMARY.md
      │
      ├── investigations/         # Research findings, explorations
      │   ├── CORTEX-3.0-INVESTIGATION.md
      │   └── FEATURE-FEASIBILITY-STUDY.md
      │
      ├── planning/               # Roadmaps, implementation plans
      │   ├── CORTEX-4.0-ROADMAP.yaml
      │   └── MIGRATION-PLAN.yaml
      │
      ├── conversation-captures/  # Strategic conversations
      │   └── CONVERSATION-CAPTURE-2025-11-25-ARCHITECTURE.md
      │
      └── implementation-guides/  # How-to guides
          └── CORTEX-INTEGRATION-GUIDE.md
```

Standalone vs Embedded Installations:

**Standalone (CORTEX repository):**
```
d:\PROJECTS\CORTEX\
  ├── README.md                   ✅ Allowed in root
  ├── LICENSE                     ✅ Allowed in root
  ├── cortex-brain/
  │   └── documents/
  │       └── reports/
  │           └── REPORT.md       ✅ Correct location
  └── WRONG-SUMMARY.md            ❌ BLOCKED
```

**Embedded (CORTEX inside user repo):**
```
d:\PROJECTS\NOOR-CANVAS\
  ├── README.md                   ✅ User's file
  ├── CORTEX/
  │   ├── cortex-brain/
  │   │   └── documents/
  │   │       └── reports/
  │   │           └── REPORT.md   ✅ Correct location
  │   └── WRONG-UPDATE.md         ❌ BLOCKED (CORTEX root)
  └── WRONG-SUMMARY.md            ❌ BLOCKED (user repo root)
```

What IS Allowed in Repository Root:
- README.md (project introduction)
- LICENSE (legal requirement)
- Package files (package.json, requirements.txt, setup.py, Cargo.toml)
- Configuration (cortex.config.json, .editorconfig, .gitignore)
- Build scripts (build.py, Makefile, build.sh)
- CI/CD (Jenkinsfile, .github/workflows/)
- Version control (.gitattributes)

What is NEVER Allowed in Repository Root:
- Summaries (SUMMARY-*.md)
- Reports (REPORT-*.md, *-COMPLETE.md)
- Analysis (*-ANALYSIS.md)
- Status updates (STATUS-*.md, UPDATE-*.md)
- Investigation reports (INVESTIGATION-*.md)
- Planning documents (PLAN-*.md, ROADMAP-*.md)
- Notes (NOTES-*.md, TODO-*.md)
- Any documentation files

Enforcement Strategy:
- Severity: "blocked" (hard stop, not warning)
- Detection: File path analysis + intent keywords
- Pre-flight: Validate path before file creation
- Post-flight: Validate no root files after operations

Integration Points:
- BrainProtector: Validates before document creation
- create_file tool: Path validation interceptor
- FileValidator: Post-operation verification
- DocumentationOrchestrator: Enforces structure

This rule BLOCKS operations that violate structure.
No exceptions, no warnings, no bypass mechanism.
