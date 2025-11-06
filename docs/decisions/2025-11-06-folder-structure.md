# Decision: Clean Folder Structure & Decision Tracking

**Date:** 2025-11-06  
**Status:** ✅ Accepted  
**Deciders:** Project team  
**Tags:** #organization #structure #governance #decision-tracking

---

## Context

During CORTEX development, we observed:

1. **Root folder clutter** - Files scattered in project root without clear organization
2. **KDS pollution** - KDS v8 files mixed with CORTEX redesign files
3. **No decision history** - Architecture decisions made but not formally recorded
4. **Future scalability** - Need structure that scales from 100 to 10,000 files

**User requirements:**
> "In the final design, I want a very clean and organized folder structure for CORTEX. Each file should have a folder home and they should not be cluttered in the root. Each file should be created in the proper place. This should be a permanent rule for how CORTEX operates."

> "I want all these variations recorded somehow (files, git). I want to be able to recall the evolution of our decisions at any time."

---

## Decision

**Implement a hierarchical folder structure with strict placement rules and comprehensive decision tracking.**

### Core Principles

1. **No Root Clutter** - Only README, LICENSE, .gitignore, and core config files in root
2. **Every File Has a Home** - Clear rules for where each file type belongs
3. **Decision Tracking** - All significant decisions documented in `docs/decisions/`
4. **Separation of Concerns** - Code, docs, tests, config, scripts in separate folders
5. **3-Level Max Depth** - Maximum 3 folder levels (except node_modules, .git)

### Implementation

1. **Archive KDS files** to `archives/kds-v8/`
2. **Reorganize CORTEX files** to proper folder homes
3. **Rename project** from `D:\PROJECTS\KDS` to `D:\PROJECTS\CORTEX`
4. **Create decision log system** in `docs/decisions/`
5. **Enforce with pre-commit hooks** - Reject root clutter

---

## Folder Structure

```
CORTEX/                                    # Root (clean!)
│
├── README.md                              # Project overview only
├── LICENSE                                # MIT license
├── .gitignore                             # Git exclusions
├── cortex.config.json                     # Core configuration
│
├── brain/                                 # CORTEX BRAIN source
│   ├── cortex-brain.db                    # SQLite database
│   ├── governance.py                      # Tier 0
│   ├── working_memory.py                  # Tier 1
│   ├── knowledge.py                       # Tier 2
│   ├── context.py                         # Tier 3
│   └── agents/                            # Agent implementations
│
├── dashboard/                             # React dashboard
│   ├── public/
│   ├── src/
│   └── package.json
│
├── config/                                # Configuration
│   ├── governance/
│   └── schema/
│
├── docs/                                  # Documentation
│   ├── design/                            # Design docs
│   ├── guides/                            # User guides
│   ├── api/                               # API docs
│   └── decisions/                         # 🆕 Decision history
│
├── tests/                                 # All tests
│   ├── unit/
│   ├── integration/
│   ├── performance/
│   └── fixtures/
│
├── scripts/                               # Utility scripts
│   ├── migration/
│   ├── build/
│   └── dev/
│
├── prompts/                               # CORTEX prompts
│   ├── cortex.md
│   ├── user/
│   └── system/
│
└── archives/                              # Historical data
    └── kds-v8/                            # Archived KDS files
```

See: `docs/CORTEX-FOLDER-STRUCTURE.md` for complete specification.

---

## Decision Tracking System

### Structure

```
docs/decisions/
├── README.md                              # Decision index
├── template.md                            # Decision template
├── 2025-11-06-fts5-custom-build.md       # FTS5 decision
├── 2025-11-06-folder-structure.md        # This decision
└── [future decisions...]
```

### Template

Each decision document includes:
- **Context** - Problem being solved
- **Decision** - What we decided
- **Alternatives** - Options considered and why not chosen
- **Consequences** - Positive/negative outcomes
- **Implementation** - How it's being implemented
- **Evolution** - Updates over time

### Git Integration

- Decision documents version controlled
- Link commits to decisions via commit messages
- Tag major architectural decisions
- Monthly review of decision evolution

---

## Alternatives Considered

### Option 1: Hierarchical Structure with Decision Tracking ⭐ CHOSEN

**Pros:**
- ✅ Clear organization (every file has a home)
- ✅ Scalable (works for any project size)
- ✅ Enforceable (pre-commit hooks)
- ✅ Complete decision history
- ✅ Searchable/traceable evolution

**Cons:**
- ⚠️ Upfront migration effort (2-3 hours)
- ⚠️ Requires discipline to maintain

**Why chosen:**
- Meets user requirements exactly
- Prevents future clutter
- Best long-term solution
- Industry best practice

---

### Option 2: Flat Structure (Status Quo)

**Pros:**
- ✅ No migration effort
- ✅ Simple (everything in root)

**Cons:**
- ❌ Doesn't meet user requirements
- ❌ Doesn't scale
- ❌ Cluttered and confusing
- ❌ Hard to maintain
- ❌ No decision history

**Why not chosen:**
- Explicitly rejected by user
- Poor long-term scalability
- No professional standard

---

### Option 3: Monorepo Style (nx/turborepo)

**Pros:**
- ✅ Scales to very large projects
- ✅ Built-in tooling

**Cons:**
- ❌ Overkill for current size
- ❌ Complex setup
- ❌ Heavy tooling dependency

**Why not chosen:**
- Too complex for current needs
- Can migrate later if needed

---

## Consequences

### Positive Consequences

✅ **Developer experience**
- Fast navigation (know where everything is)
- Easy to find/create files
- Clear ownership per folder

✅ **Maintainability**
- Clean git history
- Easy refactoring
- Scalable structure

✅ **Decision transparency**
- Complete history of why decisions were made
- Searchable decision archive
- Traceable evolution over time

✅ **Onboarding**
- New developers understand structure immediately
- Self-documenting organization
- Clear patterns to follow

✅ **Quality**
- Pre-commit hooks enforce structure
- Prevents root clutter
- Governance built-in

### Negative Consequences

⚠️ **Migration effort**
- 2-3 hours to reorganize existing files
- Update all path references
- Test after migration

⚠️ **Discipline required**
- Team must follow placement rules
- Decision documentation overhead
- Pre-commit hook maintenance

### Risks & Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Breaking imports** | High | Test after each move, update incrementally |
| **Git history loss** | Medium | Use `git mv` for file moves |
| **Team resistance** | Low | Document benefits, enforce with hooks |
| **Decision doc overhead** | Low | Only for significant decisions, use template |

---

## Implementation

### Phase 1: Create Decision System (1 hour)

```bash
# Create structure
mkdir -p docs/decisions

# Create template
cat > docs/decisions/template.md << 'EOF'
# Decision: [Title]

**Date:** YYYY-MM-DD
**Status:** Proposed | Accepted | Rejected | Superseded
**Deciders:** [Who]
**Tags:** #tag1 #tag2

## Context
[What problem are we solving?]

## Decision
[What did we decide?]

## Alternatives Considered
[What else did we consider?]

## Consequences
[What are the results?]

## Implementation
[How are we implementing this?]

## Evolution
[Updates over time]
EOF

# Create decision index
cat > docs/decisions/README.md << 'EOF'
# Decision Log

All significant CORTEX architectural decisions.

## Active Decisions
- [2025-11-06: Custom sql.js with FTS5](2025-11-06-fts5-custom-build.md)
- [2025-11-06: Folder Structure & Decision Tracking](2025-11-06-folder-structure.md)

## How to Add a Decision
1. Copy `template.md`
2. Name: `YYYY-MM-DD-short-title.md`
3. Fill in all sections
4. Link from this README
5. Commit with tag: `decision/short-title`
EOF

# Create initial decisions
# (fts5-custom-build.md and folder-structure.md)
```

### Phase 2: Archive KDS Files (30 min)

```bash
# Create archive
mkdir -p archives/kds-v8

# Move KDS-specific files
mv kds-brain/ archives/kds-v8/
mv dashboard/ archives/kds-v8/
mv dashboard-wpf/ archives/kds-v8/
mv kds-dashboard.html archives/kds-v8/
mv update-kds-story.ps1 archives/kds-v8/

# Create archive README
cat > archives/kds-v8/README.md << 'EOF'
# KDS v8 Archive

**Archived:** 2025-11-06
**Reason:** Superseded by CORTEX redesign

## What's Here
Original KDS v8 implementation and prototypes

## Why Archived
CORTEX is a clean-slate redesign with better performance and architecture.

See: docs/design/WHY-CORTEX-IS-BETTER.md
EOF
```

### Phase 3: Reorganize CORTEX Files (1 hour)

```bash
# Create new structure
mkdir -p brain/agents/shared
mkdir -p dashboard/src/{components,hooks,lib}
mkdir -p dashboard/public
mkdir -p config/{governance,schema/migrations}
mkdir -p docs/{design,guides,api}
mkdir -p tests/{unit,integration,performance,fixtures}
mkdir -p scripts/{migration,build,dev}
mkdir -p prompts/{user,system}

# Move files to proper homes
mv CORTEX/*.py brain/
mv cortex-design/*.md docs/design/
mv cortex-tests/* tests/
mv CORTEX/package.json dashboard/
mv CORTEX/cortex-tests/performance/* tests/performance/

# Move documentation
mv *.md docs/design/  # Except README.md

# Clean up root
# (Only README.md, LICENSE, .gitignore, cortex.config.json remain)
```

### Phase 4: Rename Root Folder (15 min)

```bash
# Exit VS Code, close all terminals

# Rename folder (Windows PowerShell)
cd D:\PROJECTS
Rename-Item -Path "KDS" -NewName "CORTEX"

# Update git remote (if applicable)
cd CORTEX
git remote set-url origin https://github.com/asifhussain60/CORTEX.git

# Reopen in VS Code
code .
```

### Phase 5: Update Path References (30 min)

```bash
# Update all hardcoded paths
Get-ChildItem -Recurse -File | 
  Where-Object { $_.Extension -match '\.(py|ts|tsx|md|json|yaml)$' } |
  ForEach-Object {
    (Get-Content $_.FullName) -replace 'D:\\PROJECTS\\KDS', 'D:\\PROJECTS\\CORTEX' |
    Set-Content $_.FullName
  }

# Update documentation
# Update configuration
# Test all imports
```

### Phase 6: Add Pre-commit Hook (15 min)

```bash
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Prevent root clutter

ALLOWED_ROOT="README.md LICENSE .gitignore cortex.config.json package.json"

for file in *; do
  if [[ -f "$file" ]] && ! echo "$ALLOWED_ROOT" | grep -q "$file"; then
    echo "❌ ERROR: File '$file' not allowed in root!"
    echo "   See: docs/CORTEX-FOLDER-STRUCTURE.md"
    exit 1
  fi
done
EOF

chmod +x .git/hooks/pre-commit
```

---

## Timeline

| Phase | Effort | When |
|-------|--------|------|
| Create decision system | 1 hour | Today (Phase -1) |
| Archive KDS files | 30 min | Today (Phase -1) |
| Reorganize CORTEX files | 1 hour | Today/Tomorrow |
| Rename root folder | 15 min | Tomorrow |
| Update path references | 30 min | Tomorrow |
| Add pre-commit hook | 15 min | Phase 0 |
| **Total** | **3.5 hours** | **This week** |

---

## References

### Related Documents
- Complete structure spec: `docs/CORTEX-FOLDER-STRUCTURE.md`
- FTS5 decision: `docs/decisions/2025-11-06-fts5-custom-build.md`
- Implementation Plan v2.0: `cortex-design/IMPLEMENTATION-PLAN-V2.md`

### External Resources
- Architecture Decision Records: https://adr.github.io/
- Folder structure best practices: https://github.com/kriasoft/Folder-Structure-Conventions

---

## Evolution

### 2025-11-06: Initial Decision
- User requested clean folder structure
- User requested decision tracking
- Designed hierarchical structure with 3-level max depth
- Created decision log system
- Planned KDS archival and folder rename

### Future Reviews
- After Phase 0: Review pre-commit hook effectiveness
- After Phase 3: Review if structure still scales
- Quarterly: Review decision log usefulness

---

**Status:** ✅ Accepted and In Progress  
**Next:** Create decision logs → Archive KDS → Reorganize files → Rename folder

