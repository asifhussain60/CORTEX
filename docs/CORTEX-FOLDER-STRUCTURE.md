# CORTEX Folder Structure Design

**Version:** 1.0  
**Date:** 2025-11-06  
**Status:** 🎯 DESIGN APPROVED - Ready to Implement  

---

## Design Principles

### 1. **No Root Clutter**
- Every file has a designated folder home
- Root contains ONLY: README.md, LICENSE, .gitignore, core config files
- No orphaned scripts, docs, or data files in root

### 2. **Clear Hierarchy**
- Maximum 3 levels deep (except node_modules, .git)
- Self-documenting folder names
- Consistent naming conventions

### 3. **Separation of Concerns**
- Source code separate from documentation
- Tests mirror source structure
- Configuration centralized
- Data/artifacts isolated

---

## Proposed Structure

```
CORTEX/                                    # Root (clean!)
│
├── README.md                              # Project overview
├── LICENSE                                # MIT license
├── .gitignore                             # Git exclusions
├── cortex.config.json                     # Core configuration
│
├── brain/                                 # CORTEX BRAIN (4-tier system)
│   ├── cortex-brain.db                    # Tier 1 + 2 (SQLite)
│   ├── cortex-metrics.json                # Tier 3 (Git metrics cache)
│   ├── governance.py                      # Tier 0 (Governance Engine)
│   ├── working_memory.py                  # Tier 1 (Working Memory Manager)
│   ├── knowledge.py                       # Tier 2 (Long-Term Knowledge)
│   ├── context.py                         # Tier 3 (Context Intelligence)
│   └── agents/                            # Agent implementations
│       ├── __init__.py
│       ├── hemisphere_left.py             # Analytical agents
│       ├── hemisphere_right.py            # Creative agents
│       └── shared/                        # Shared utilities
│
├── dashboard/                             # CORTEX Dashboard
│   ├── public/                            # Static assets
│   │   ├── index.html
│   │   └── sql-wasm.wasm                  # Custom sql.js build
│   ├── src/
│   │   ├── components/                    # React components
│   │   │   ├── ConversationList.tsx
│   │   │   ├── PatternGraph.tsx
│   │   │   └── MetricsPanel.tsx
│   │   ├── hooks/                         # Custom React hooks
│   │   ├── lib/                           # Utilities
│   │   │   └── db.ts                      # sql.js wrapper
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── config/                                # Configuration files
│   ├── governance/                        # Tier 0 rules
│   │   ├── core-rules.yaml
│   │   ├── agent-contracts.yaml
│   │   └── quality-gates.yaml
│   └── schema/                            # Database schemas
│       ├── tier1-working-memory.sql
│       ├── tier2-knowledge.sql
│       └── migrations/
│
├── docs/                                  # Documentation
│   ├── design/                            # Design documents
│   │   ├── ARCHITECTURE.md
│   │   ├── CORTEX-DNA.md
│   │   ├── DECISIONS.md                   # 🆕 Decision log!
│   │   └── WHY-CORTEX.md
│   ├── guides/                            # User guides
│   │   ├── QUICK-START.md
│   │   ├── DASHBOARD-GUIDE.md
│   │   └── MIGRATION-GUIDE.md
│   ├── api/                               # API documentation
│   │   ├── agents.md
│   │   ├── brain.md
│   │   └── storage.md
│   └── decisions/                         # 🆕 Decision history
│       ├── 2025-11-06-fts5-custom-build.md
│       ├── 2025-11-06-folder-structure.md
│       └── README.md
│
├── tests/                                 # All tests
│   ├── unit/                              # Unit tests (mirror brain/)
│   │   ├── test_governance.py
│   │   ├── test_working_memory.py
│   │   ├── test_knowledge.py
│   │   └── agents/
│   ├── integration/                       # Integration tests
│   │   ├── test_brain_integration.py
│   │   └── test_dashboard_integration.py
│   ├── performance/                       # Performance benchmarks
│   │   ├── benchmark-sql-js.spec.ts
│   │   ├── generate-test-data.py
│   │   └── test-cortex-brain.db
│   └── fixtures/                          # Test data
│       ├── sample-conversations.json
│       └── sample-patterns.json
│
├── scripts/                               # Utility scripts
│   ├── migration/                         # KDS → CORTEX migration
│   │   ├── migrate-tier1.py
│   │   ├── migrate-tier2.py
│   │   └── validate-migration.py
│   ├── build/                             # Build scripts
│   │   ├── build-sql-js.sh
│   │   └── build-dashboard.sh
│   └── dev/                               # Development utilities
│       ├── reset-brain.py
│       └── seed-test-data.py
│
├── prompts/                               # CORTEX prompts (entry point)
│   ├── cortex.md                          # Universal entry point
│   ├── user/                              # User-facing prompts
│   │   └── quick-reference.md
│   └── system/                            # System prompts
│       └── agent-personas.md
│
├── .github/                               # GitHub configuration
│   ├── workflows/                         # CI/CD
│   │   ├── cortex-ci.yml
│   │   └── cortex-tests.yml
│   └── ISSUE_TEMPLATE/
│
└── archives/                              # Historical data
    ├── kds-v8/                            # 🆕 Archived KDS files
    │   ├── README.md                      # What's archived and why
    │   └── [KDS files moved here]
    └── decisions/                         # Old decision logs (if needed)

```

---

## File Placement Rules

### When creating ANY new file, ask:

1. **Is it source code?** → `brain/` or `dashboard/src/`
2. **Is it a test?** → `tests/` (mirror source structure)
3. **Is it configuration?** → `config/`
4. **Is it documentation?** → `docs/`
5. **Is it a script?** → `scripts/`
6. **Is it a prompt?** → `prompts/`
7. **Is it data/artifacts?** → Appropriate data folder or `.gitignore`

### NEVER:
- ❌ Create files in project root (except core configs)
- ❌ Create ad-hoc folders without design
- ❌ Mix concerns (code + docs in same folder)
- ❌ Nest more than 3 levels (except node_modules, .git)

---

## Decision Tracking System

### docs/decisions/ Structure

Every significant decision gets its own file:

```
docs/decisions/
├── README.md                              # Index of all decisions
├── 2025-11-06-fts5-custom-build.md       # Why we built custom sql.js
├── 2025-11-06-folder-structure.md        # This structure decision
├── 2025-11-04-sqlite-over-yaml.md        # Why SQLite vs YAML
├── 2025-11-04-4-tier-brain.md            # Why 4 tiers not 6
└── template.md                            # Template for new decisions
```

### Decision Document Template

```markdown
# Decision: [Title]

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Rejected | Superseded
**Deciders:** [Who made this decision]
**Tags:** #architecture #performance #tooling

## Context

What is the issue we're trying to solve? What constraints exist?

## Decision

What did we decide to do?

## Alternatives Considered

### Option 1: [Name]
- Pros: ...
- Cons: ...
- Why not chosen: ...

### Option 2: [Name]
- Pros: ...
- Cons: ...
- Why not chosen: ...

## Consequences

What are the results of this decision?

### Positive
- ...

### Negative
- ...

### Risks
- ...

## Implementation

How will this be implemented? Timeline?

## References

- Related decisions: ...
- Issues: ...
- PRs: ...

## Evolution

### 2025-11-10: Updated because...
### 2025-11-15: Revisited, still valid
```

---

## Migration Plan

### Phase 1: Archive KDS Files (30 min)

```bash
# Create archive structure
mkdir -p archives/kds-v8

# Move KDS-specific files
mv kds-brain/ archives/kds-v8/
mv kds-dashboard.html archives/kds-v8/
mv update-kds-story.ps1 archives/kds-v8/
mv dashboard/ archives/kds-v8/
mv dashboard-wpf/ archives/kds-v8/

# Create archive README
cat > archives/kds-v8/README.md << EOF
# KDS v8 Archive

Archived on: 2025-11-06
Reason: Superseded by CORTEX redesign

## What's Here
- Original KDS v8 implementation
- Dashboard prototypes (HTML + WPF)
- Migration scripts

## Why Archived
CORTEX is a clean-slate redesign with:
- SQLite storage (10-100x faster)
- 4-tier BRAIN architecture
- 95%+ test coverage
- React dashboard

## Migration
See: docs/guides/MIGRATION-GUIDE.md
EOF
```

### Phase 2: Reorganize CORTEX Files (1 hour)

```bash
# Create new structure
mkdir -p brain/agents/shared
mkdir -p dashboard/src/{components,hooks,lib}
mkdir -p config/{governance,schema/migrations}
mkdir -p docs/{design,guides,api,decisions}
mkdir -p tests/{unit,integration,performance,fixtures}
mkdir -p scripts/{migration,build,dev}
mkdir -p prompts/{user,system}

# Move CORTEX files to proper homes
mv CORTEX/cortex-brain.py brain/
mv cortex-design/*.md docs/design/
mv cortex-tests/ tests/
# ... (detailed move script)

# Move root clutter
mv *.md docs/design/  # Except README.md
```

### Phase 3: Rename Root Folder (15 min)

```bash
# Outside project folder:
cd D:/PROJECTS/
mv KDS CORTEX

# Update git remote (if needed)
cd CORTEX
git remote set-url origin https://github.com/asifhussain60/CORTEX.git
```

### Phase 4: Update All References (30 min)

```bash
# Update paths in all files
grep -r "D:\\PROJECTS\\KDS" --files-with-matches | \
  xargs sed -i 's/D:\\PROJECTS\\KDS/D:\\PROJECTS\\CORTEX/g'

# Update documentation
# Update configuration files
# Update scripts
```

### Phase 5: Create Decision Logs (1 hour)

```bash
# Create decision documents from our conversation
docs/decisions/2025-11-06-fts5-custom-build.md
docs/decisions/2025-11-06-folder-structure.md
docs/decisions/2025-11-06-holistic-review.md

# Create decision index
docs/decisions/README.md
```

---

## Enforcement

### Pre-commit Hook Rule

Add to `.git/hooks/pre-commit`:

```bash
# Check for root clutter (files not in allowed list)
ALLOWED_ROOT="README.md LICENSE .gitignore cortex.config.json package.json"

for file in *; do
  if [[ -f "$file" ]] && ! echo "$ALLOWED_ROOT" | grep -q "$file"; then
    echo "❌ ERROR: File '$file' not allowed in root!"
    echo "   Move to appropriate folder (see DIRECTORY-STRUCTURE.md)"
    exit 1
  fi
done
```

### Phase 0 Implementation

- Create folder structure
- Set up pre-commit hook
- Document in DIRECTORY-STRUCTURE.md
- Add to governance rules

---

## Benefits

### For Development
✅ **Fast navigation** - Know exactly where to find/create files
✅ **Clear ownership** - Each folder has a single purpose
✅ **Easy onboarding** - New developers understand structure immediately

### For Maintenance
✅ **Clean git history** - Organized commits
✅ **Easy refactoring** - Move whole folders without breaking imports
✅ **Scalable** - Structure works for 10 or 10,000 files

### For Decision Tracking
✅ **Complete history** - All decisions documented
✅ **Searchable** - grep/search across decision logs
✅ **Traceable** - Link commits to decisions
✅ **Accountability** - Know who decided what and why

---

## Timeline Integration

### Immediate (Today)
- ✅ Design approved (this document)
- Create decision log system
- Document FTS5 decision

### Phase -1 Completion (This Week)
- Archive KDS files
- Reorganize CORTEX files
- Rename root folder

### Phase 0 (Next)
- Enforce structure with pre-commit hook
- Add to governance rules
- Create DIRECTORY-STRUCTURE.md

### Ongoing (Permanent)
- Every new file follows placement rules
- Every significant decision documented
- Monthly decision log review

---

## Open Questions

1. **Should we keep `prompts/user/kds.md`?**
   - Option A: Archive to `archives/kds-v8/prompts/`
   - Option B: Keep as `prompts/user/legacy-kds-reference.md`
   - **Recommendation:** Keep as reference during migration (Phase 6)

2. **Dashboard build output location?**
   - Option A: `dashboard/dist/` (standard)
   - Option B: `brain/static/` (if serving from Python)
   - **Recommendation:** `dashboard/dist/` (browser-only, no server)

3. **Test database location?**
   - Option A: `tests/fixtures/test-cortex-brain.db`
   - Option B: `.gitignore` in `brain/`
   - **Recommendation:** `tests/fixtures/` (checked into git for reproducibility)

---

**Status:** 🎯 READY TO IMPLEMENT  
**Next:** Create decision logs → Archive KDS → Reorganize CORTEX → Build FTS5

