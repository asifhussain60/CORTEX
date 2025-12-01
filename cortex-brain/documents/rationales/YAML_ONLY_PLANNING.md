YAML_ONLY_PLANNING: Documentation Bloat Prevention

Real incident (2025-11-18):
- CORTEX created: DOCUMENTATION-CONSOLIDATION-COMPREHENSIVE-PLAN.md
- File size: 23KB (extensive markdown document)
- User: "why is CORTEX still generating md plans instead of yaml plans?"
- User: "Add to tier 0 that planning should ALWAYS done using yaml files NEVER MD to prevent documentation bloat"

Problem with Markdown Plans:
- Verbose "comprehensive" documents (10-50 pages typical)
- Heavy token cost to read/process
- Difficult to parse programmatically
- No enforced structure (inconsistent formats)
- Accumulates as "documentation debt"

YAML Planning Benefits:
- Enforced concise structure
- 60-80% token reduction vs Markdown
- Machine-readable for automation
- Consistent schema across all plans
- Easy to validate and query

Implementation:
- CORTEX creates planning YAML schemas
- Validation against JSON Schema
- Brain integration for automated tracking
- Markdown reserved ONLY for user-facing docs (stories, guides)

Related Rules:
- MACHINE_READABLE_FORMATS (Tier 0 instinct)
- NO_ROOT_SUMMARY_DOCUMENTS (Layer 3)

Reference Examples:
- cortex-brain/documents/planning/YAML-PHASE-TRACKER-DESIGN.yaml
- cortex-brain/CORTEX-UNIFIED-ARCHITECTURE.yaml
- cortex-operations.yaml

User Feedback:
"Add to tier 0 of cortex that planning should ALWAYS done using yaml files NEVER MD 
to prevent documentation bloat" - Asif Hussain, 2025-11-18
│
├── investigations/       # Research, architecture investigations
│   ├── AUTH-FEATURE-INVESTIGATION.md
│   └── DATABASE-MIGRATION-INVESTIGATION.md
│
├── planning/             # Roadmaps, implementation plans
│   ├── CORTEX-4.0-PLANNING.md
│   └── features/
│       └── PLAN-2025-11-17-authentication.md
│
├── conversation-captures/ # Strategic conversation captures
│   └── CONVERSATION-CAPTURE-2025-11-14-AUTHENTICATION.md
│
└── implementation-guides/  # How-to guides, integration docs
    └── CORTEX-SETUP-GUIDE.md
```

Benefits of Organized Structure:
- Easy to find related documents
- Clear ownership and purpose
- Searchable by category
- No root-level clutter
- Professional appearance

Root Directory Reserved For:
```
CORTEX/
├── README.md              ✅ Project overview
├── LICENSE                ✅ Legal
├── package.json           ✅ Dependencies
├── requirements.txt       ✅ Python packages
├── cortex.config.json     ✅ Configuration
├── setup.py               ✅ Installation
├── mkdocs.yml             ✅ Docs build config
└── .gitignore             ✅ Git config
```

Example Violations:

❌ BAD:
```
d:\PROJECTS\CORTEX\INVESTIGATION-ANALYSIS-REPORT.md
d:\PROJECTS\CORTEX\CORTEX-3.0-IMPLEMENTATION-COMPLETE.md
d:\PROJECTS\CORTEX\COMPREHENSIVE-CORTEX-ANALYSIS-REPORT.md
```

✅ GOOD:
```
d:\PROJECTS\CORTEX\cortex-brain\documents\analysis\INVESTIGATION-ANALYSIS-REPORT.md
d:\PROJECTS\CORTEX\cortex-brain\documents\reports\CORTEX-3.0-IMPLEMENTATION-COMPLETE.md
d:\PROJECTS\CORTEX\cortex-brain\documents\analysis\COMPREHENSIVE-CORTEX-ANALYSIS-REPORT.md
```

Enforcement:
- Brain Protector challenges root-level document creation
- Suggests appropriate category automatically
- Provides full path template
- References cortex-brain/documents/README.md for guidelines

Override Cases (Rare):
- User explicitly requests root-level placement
- Temporary scaffolding during setup
- Files intended for repository metadata (CHANGELOG.md, CONTRIBUTING.md)

This maintains clean repository structure and ensures documents
are findable, organized, and maintainable long-term.
