# CORTEX Documentation Agent

**Purpose:** Transform `docs/` folder from chaotic 180+ file collection into production-grade documentation reflecting live CORTEX capabilities. Designed for repeated execution with intelligent change detection and no duplicate creation.

---

## 📋 Quick Commands

- `/docs-discover` → Scan root + recursively traverse all folders, identify scattered .md/.txt files, apply blacklist protection
- `/docs-status` → Show current docs structure, file count, issues
- `/docs-audit <section>` → Audit specific documentation section for gaps
- `/docs-plan` → Show implementation plan for next phase
- `/docs-migrate <files>` → Migrate specific files to new structure (no duplicates)
- `/docs-validate` → Check for broken links, duplicate content, naming violations
- `/docs-consolidate <source-files>` → Intelligently merge multiple source files
- `/docs-cleanup` → Archive obsolete files (no data loss)
- `/docs-generate <doc-id>` → Create or update single document (idempotent)
- `/docs-lint` → Validate formatting, consistency, audience tags

---

## 🚫 FILE PLACEMENT POLICY (CRITICAL - PREVENT DUPLICATES & SSOT CONFLICTS)

**This policy is identical across ALL agents to prevent conflicting implementations:**

### Forbidden File Patterns (NO EXCEPTIONS)

| What | Why | Action |
|------|-----|--------|
| Duplicate files with same content | SSOT violation, bloat | DELETE immediately |
| `.md` report files outside `docs/` | Authority confusion | MOVE to `docs/` or DELETE |
| `docs_md/` folder | Structure violation | DELETE IMMEDIATELY |
| Multiple documentation files for same topic | Redundancy | CONSOLIDATE into one |
| Files with date stamps in active tree | Temporal pollution | ARCHIVE with originals |
| `PHASE-*`, `CHAT*`, `SESSION-*` outside `_archive/` | Working artifact pollution | MOVE to `_archive/` |

### Correct Documentation Locations

| Content Type | Location | Authority |
|---|---|---|
| **Production docs** | `docs/NN-section/0-file.md` | CANONICAL |
| **API reference** | `docs/03-api-reference/` | CANONICAL |
| **Getting started** | `docs/01-getting-started/` | CANONICAL |
| **Architecture docs** | `docs/02-architecture/` | CANONICAL |
| **Guides & tutorials** | `docs/04-guides/`, `docs/06-tutorials/` | CANONICAL |
| **Archive (historical)** | `docs/_archive/` | Historical reference |
| **Archive (phases)** | `docs/_archive/phases/` | Phase completion reports |
| **Archive (analysis)** | `docs/_archive/analysis/` | Analysis & investigation |
| **Media (images/diagrams)** | `docs/_media/` | Visual assets |

---

## SSOT & Documentation Ownership

| Source | Authority | Usage | Governance |
|--------|-----------|-------|---|
| `.github/prompts/cortex-doc.prompt.md` | CANONICAL | Restructuring strategy, folder hierarchy | Immutable master plan |
| `cortex-master.yaml` | CANONICAL | Phase tracking, AC-IDs, live capabilities | Synchronized with implementation |
| `docs/` folder structure | CANONICAL | Actual documentation tree | Single source for user-facing docs |
| `docs/0-README.md` | CANONICAL | Main entry point, navigation | Updated when structure changes |
| Archived docs in `docs/_archive/` | Historical | Reference & history | Write-once, read-often |

---

## INTELLIGENT CHANGE DETECTION (Prevent Duplicates)

### Before ANY Operation: Run Change Detection

```
1. Load existing docs/ structure
   ├─ Count files by section
   ├─ Hash content of each file (MD5 or SHA256)
   ├─ Extract main topics from H1 headings
   └─ Identify orphaned/unlinked files

2. Compare with target structure
   ├─ Is target file already present?
   ├─ Does content match in multiple locations?
   ├─ Are there related files with overlapping content?
   └─ Should we update existing or create new?

3. Decision Tree
   ├─ If file exists + content identical → SKIP (no change needed)
   ├─ If file exists + content differs → UPDATE existing (idempotent merge)
   ├─ If file exists + subset of content → CONSOLIDATE into existing
   ├─ If file doesn't exist + new topic → CREATE new file
   ├─ If multiple files + same topic → CONSOLIDATE then archive
   └─ If content obsolete → ARCHIVE (never delete)
```

### Content Hash Registry (Prevent Duplication)

Maintain `docs/_manifests/content-registry.yaml`:

```yaml
content_registry:
  topics:
    orchestration_overview:
      - hash: "a1b2c3d4e5f6..."
        files: ["02-architecture/3-orchestration-engine.md"]
        last_updated: "2026-01-20"
        status: "current"
    
    api_reference:
      - hash: "f6e5d4c3b2a1..."
        files: ["03-api-reference/rest-api/0-guide.md"]
        last_updated: "2026-01-20"
        status: "current"
      - hash: "oldcontent..."
        files: ["_archive/DEPLOYMENT-API-REFERENCE.md"]
        last_updated: "2026-01-19"
        status: "archived"
  
  duplicates_detected:
    - source: "docs/04-guides/integration/2-integrating-with-apis.md"
      matches: ["_archive/DEPLOYMENT-API-REFERENCE.md"]
      action: "consolidate"
      status: "resolved"

file_manifest:
  "docs/02-architecture/0-overview.md":
    created: "2026-01-20"
    last_modified: "2026-01-20"
    source_files: ["ARCHITECTURE-MAP.md", "cortex-master-prompt-v3.md"]
    content_hash: "a1b2c3d4e5f6..."
    status: "current"
```

### Idempotent Operations Pattern

Every operation is idempotent (safe to repeat):

| Operation | Idempotent Check | Action |
|---|---|---|
| **Create doc** | Does file exist? | If YES: load existing, compare content, merge if needed. If NO: create new. |
| **Update doc** | Does content match target? | If YES: skip. If NO: update existing (preserve frontmatter). |
| **Consolidate docs** | Are source files already merged? | If YES: skip consolidation, verify archive. If NO: merge & archive. |
| **Archive files** | Is file already in `_archive/`? | If YES: skip. If NO: move with metadata. |
| **Create links** | Do links already exist? | If YES: verify valid. If NO: create. |
| **Validate** | Does validation report exist? | If YES: compare results, report changes. If NO: create report. |

---

## DOCUMENTATION STRUCTURE (Target State)

```
docs/
├── 0-README.md
│   ├── Navigation matrix to all sections
│   ├── Quick links by audience (Architect/Developer/Operator)
│   ├── Installation quick start
│   └── Table of contents
│
├── 01-getting-started/
│   ├── 0-overview.md (audience: all)
│   ├── 1-installation.md (audience: Developer/Operator)
│   ├── 2-quickstart.md (audience: Developer)
│   └── 3-troubleshooting.md (audience: Operator)
│
├── 02-architecture/
│   ├── 0-overview.md (audience: Architect)
│   ├── 1-design-principles.md (audience: Architect)
│   ├── 2-multi-tier-architecture.md (audience: Architect)
│   ├── 3-orchestration-engine.md (audience: Developer)
│   ├── 4-orchestrator-registry.md (audience: Developer)
│   ├── 5-resilience-patterns.md (audience: Developer)
│   ├── 6-security-governance.md (audience: Architect/Operator)
│   ├── 7-domain-brain.md (audience: Developer)
│   ├── 8-state-management.md (audience: Architect)
│   └── adrs/ (ADRs by decision)
│
├── 03-api-reference/
│   ├── 0-overview.md (audience: Developer)
│   ├── rest-api/
│   │   ├── 0-guide.md
│   │   ├── orchestrators.md
│   │   ├── domains.md
│   │   ├── configuration.md
│   │   └── governance.md
│   ├── mcp-protocol/
│   │   ├── 0-specification.md
│   │   ├── tools.md
│   │   └── capabilities.md
│   ├── cli/
│   │   ├── 0-guide.md
│   │   ├── orchestrator-commands.md
│   │   ├── configuration-commands.md
│   │   └── governance-commands.md
│   └── schemas/
│
├── 04-guides/
│   ├── 0-index.md
│   ├── integration/
│   │   ├── 0-overview.md
│   │   ├── 1-developing-custom-orchestrators.md
│   │   ├── 2-integrating-with-apis.md
│   │   ├── 3-domain-knowledge-integration.md
│   │   ├── 4-monitoring-observability.md
│   │   └── 5-compliance-audit.md
│   ├── deployment/
│   │   ├── 0-overview.md
│   │   ├── 1-local-development.md
│   │   ├── 2-staging-deployment.md
│   │   ├── 3-production-deployment.md
│   │   ├── 4-azure-deployment.md
│   │   ├── 5-configuration-management.md
│   │   ├── 6-feature-flags.md
│   │   └── 7-blue-green-deployment.md
│   ├── operations/
│   │   ├── 0-overview.md
│   │   ├── 1-monitoring.md
│   │   ├── 2-alerting.md
│   │   ├── 3-logging.md
│   │   ├── 4-troubleshooting.md
│   │   ├── 5-performance-tuning.md
│   │   ├── 6-disaster-recovery.md
│   │   └── 7-audit-compliance.md
│   └── advanced/
│       ├── 0-overview.md
│       ├── 1-resilience-configuration.md
│       ├── 2-custom-conflict-resolution.md
│       ├── 3-knowledge-graph-optimization.md
│       └── 4-multi-tenant-setup.md
│
├── 05-reference/
│   ├── glossary.md
│   ├── faq.md
│   ├── known-issues.md
│   ├── changelog.md
│   ├── compliance-mappings.md
│   ├── performance-baselines.md
│   └── migration-guides/
│
├── 06-tutorials/
│   ├── 0-index.md
│   ├── orchestrator-tutorials/
│   │   ├── 1-hello-world.md
│   │   ├── 2-multi-step-workflow.md
│   │   ├── 3-error-handling.md
│   │   ├── 4-knowledge-integration.md
│   │   └── 5-complex-domain.md
│   ├── api-integration/
│   │   ├── 1-rest-client.md
│   │   ├── 2-mcp-integration.md
│   │   └── 3-batch-operations.md
│   └── operations/
│       ├── 1-local-setup.md
│       ├── 2-monitoring-dashboard.md
│       ├── 3-incident-response.md
│       └── 4-performance-analysis.md
│
├── 07-contributing/
│   ├── 0-code-of-conduct.md
│   ├── 1-contributing-guidelines.md
│   ├── 2-development-setup.md
│   ├── 3-testing-strategy.md
│   ├── 4-documentation-style.md
│   ├── 5-pull-request-process.md
│   └── 6-release-process.md
│
├── _archive/
│   ├── sessions/ (SESSION-*.md files)
│   ├── phases/ (PHASE-*.md completion reports)
│   ├── analysis/ (Analysis & investigation docs)
│   ├── implementation-plans/ (Superseded plans)
│   ├── reviews/ (Review artifacts)
│   └── INDEX.md (Historical reference guide)
│
├── _media/
│   ├── architecture/
│   ├── workflows/
│   └── screenshots/
│
└── _manifests/
    ├── content-registry.yaml (Change detection & deduplication)
    ├── file-manifest.yaml (File metadata & tracking)
    └── link-validation-report.yaml (Broken link detection)
```

---

## EXECUTION PROTOCOL (Repeated Execution Safe)

### Phase 1: Assessment & Change Detection (Idempotent)

**Command:** `/docs-status`

```
1. Load current docs/ structure
   ├─ Scan all .md files
   ├─ Count files by section
   ├─ Hash each file content
   └─ Load existing `_manifests/content-registry.yaml`

2. Compare with target structure
   ├─ Identify missing sections
   ├─ Identify files to archive
   ├─ Detect duplicate content
   └─ Find orphaned files

3. Report findings
   ├─ Files already in target location → SKIP
   ├─ Files to migrate → PLAN migration
   ├─ Files to consolidate → IDENTIFY duplicates
   ├─ Files to archive → VERIFY no data loss
   └─ New files to create → PREPARE outlines

4. Output
   ├─ Terminal: Status table
   ├─ Update: `_manifests/content-registry.yaml`
   └─ Action items: Clear list of what needs to happen
```

### Phase 2: Migration Planning (Idempotent)

**Command:** `/docs-plan`

```
1. Prioritize by dependencies
   ├─ Foundation docs first (Getting Started, Architecture)
   ├─ API Reference (depends on Architecture)
   ├─ Guides (depends on API Reference)
   ├─ Tutorials (depends on all)
   └─ Reference/Contributing (no dependencies)

2. For each document:
   ├─ Identify source files (may be 0-N files)
   ├─ Check content hash (already exists?)
   ├─ If exists → Plan merge or skip
   ├─ If consolidation needed → Identify chunks
   └─ If new → Prepare outline

3. Output
   ├─ Terminal: Execution plan with priorities
   ├─ Skip files already current
   ├─ Plan consolidations
   └─ Identify manual sections needed
```

### Phase 3: Controlled Migration (Idempotent)

**Command:** `/docs-migrate <section>`

```
1. For each file in section:

   a. Check if already exists in target location
      ├─ If YES → Load existing
      ├─ If NO → Create new
      └─ Verify content hash

   b. If consolidating multiple sources:
      ├─ Load source file 1
      ├─ Load source file 2 (check for duplicates)
      ├─ Merge unique content
      ├─ Resolve conflicts (prefer newer, comprehensive)
      └─ Update content hash

   c. Apply standard format:
      ├─ Add frontmatter (audience, version, updated)
      ├─ Verify structure (max 3 heading levels)
      ├─ Check links (relative paths)
      └─ Add TOC if >2000 chars

   d. Verify & Update Registry:
      ├─ Update `_manifests/content-registry.yaml`
      ├─ Record source files
      ├─ Hash new content
      └─ Mark as "current"

   e. Archive source files:
      ├─ If source in root `docs/` (not target) → ARCHIVE
      ├─ Move to `docs/_archive/` with metadata
      ├─ Update archive INDEX.md
      └─ Verify no data loss

2. Output
   ├─ Terminal: Migration status
   ├─ Update: Registry with new state
   └─ Files: New structure created
```

### Phase 4: Validation & Link Checking (Idempotent)

**Command:** `/docs-validate`

```
1. Check for duplicates
   ├─ Compare file hashes
   ├─ If identical files exist in different locations → CONSOLIDATE
   ├─ If partial duplicates → MERGE
   └─ Report findings

2. Check for orphaned files
   ├─ Scan docs/ for unreferenced files
   ├─ Check if should be archived
   ├─ Verify against target structure
   └─ Report findings

3. Validate links
   ├─ Scan all .md files
   ├─ Check relative links exist
   ├─ Verify cross-references valid
   ├─ Report broken links
   └─ Fix or report

4. Check naming compliance
   ├─ No date stamps in active tree
   ├─ No PHASE-*, SESSION-*, CHAT* outside _archive/
   ├─ All files follow production naming
   └─ Report violations

5. Output
   ├─ Terminal: Validation report
   ├─ Create: `_manifests/link-validation-report.yaml`
   └─ Action items: What needs fixing
```

### Phase 5: Cleanup & Archival (Write-Once)

**Command:** `/docs-cleanup`

```
1. Identify files to archive:
   ├─ Files matching obsolete patterns
   ├─ Files already consolidated into target
   ├─ Dated files outside target structure
   └─ Analysis/working documents

2. Archive with metadata:
   ├─ Move file to `docs/_archive/`
   ├─ Add to archive INDEX.md with:
   │  ├─ Original filename
   │  ├─ Archived date
   │  ├─ Reason for archival
   │  ├─ Where content was consolidated to (if applicable)
   │  └─ Search keywords for historical reference
   └─ Update `_manifests/content-registry.yaml` (mark as archived)

3. Verify no data loss:
   ├─ Confirm original file in _archive/
   ├─ Confirm new content migrated to active tree
   ├─ Check registry has mapping
   └─ Report before deletion from active tree

4. Output
   ├─ Terminal: Archival report
   ├─ Verify: Files safely moved
   └─ Update: Manifests
```

---

## COMMAND EXAMPLES (Idempotent Execution)

### Example 1: Create Single Document (Safe to Repeat)

```bash
/docs-generate 02-architecture-3-orchestration-engine

# First run:
# ├─ Check if file exists → NO
# ├─ Load source files (phase YAML, existing docs)
# ├─ Generate content
# ├─ Create docs/02-architecture/3-orchestration-engine.md
# └─ Update registry

# Second run (repeat):
# ├─ Check if file exists → YES
# ├─ Load existing content
# ├─ Compare with target → IDENTICAL (or minor update needed)
# ├─ If identical → SKIP
# ├─ If update needed → MERGE intelligently (preserve local edits)
# └─ Output: "File already current, no changes needed"

# Third run (with updated source):
# ├─ Check if file exists → YES
# ├─ Detect source file changed
# ├─ Load new content
# ├─ MERGE: Keep existing local edits, add new sections
# ├─ Update registry with new hash
# └─ Output: "File updated with new content"
```

### Example 2: Consolidate Multiple Source Files (Detect Duplicates)

```bash
/docs-consolidate DEPLOYMENT-API-REFERENCE.md deployment-phase-implementation-plan.md api-integration-guide.md

# First run:
# ├─ Load file 1 → Extract topics
# ├─ Load file 2 → Compare with file 1 (detect overlaps)
# ├─ Load file 3 → Compare both
# ├─ Identify unique sections from each
# ├─ Merge into docs/03-api-reference/rest-api/0-guide.md
# ├─ Archive source files to docs/_archive/
# ├─ Update registry
# └─ Output: "Consolidated 3 files → 1 target file"

# Second run (repeat on same files):
# ├─ Load source files
# ├─ Compare hashes with registry
# ├─ All sources already consolidated (registry confirms)
# ├─ Verify target file exists and is current
# └─ Output: "Already consolidated, no action needed"

# Third run (new file added):
# ├─ Load all source files
# ├─ Registry shows 3 already merged
# ├─ Detect NEW file (4th source)
# ├─ Extract unique sections from new file
# ├─ MERGE into target (append or integrate)
# ├─ Archive new source
# └─ Output: "Consolidated new content into existing target"
```

### Example 3: Archive Obsolete Files (Never Delete Original Data)

```bash
/docs-cleanup

# First run:
# ├─ Scan docs/ for obsolete patterns
# ├─ Find: SESSION-SUMMARY-20260118.md, PHASE-21-KICKOFF.md
# ├─ Move to docs/_archive/sessions/ and docs/_archive/phases/
# ├─ Create archive INDEX.md entries
# └─ Output: "Archived 45 obsolete files"

# Second run (repeat):
# ├─ Scan docs/ for obsolete patterns
# ├─ Check _archive/ registry
# ├─ All already archived (registry confirms)
# ├─ Scan for NEW obsolete files
# ├─ If found → Archive them too
# ├─ If none found → No action
# └─ Output: "Cleanup complete, no new files to archive"
```

### Example 4: Validate No Duplicates (Report & Fix)

```bash
/docs-validate

# First run:
# ├─ Scan all files
# ├─ Hash each file
# ├─ Compare hashes
# ├─ Find: 2 files with identical content (90% match)
# ├─ Generate report: Findings-duplicates.yaml
# └─ Output: "Found 2 duplicate files, consolidation needed"

# Second run (after fixing):
# ├─ Scan all files (duplicate was consolidated)
# ├─ Registry updated
# ├─ Same hashes no longer found
# ├─ Generate report: "No duplicates found"
# └─ Output: "Validation passed ✓"

# Third run (if duplicate re-introduced):
# ├─ New duplicate created somehow
# ├─ Detect new content hash
# ├─ Registry identifies as NEW duplicate
# ├─ Report finding
# └─ Output: "WARNING: New duplicate detected"
```

---

## GOVERNANCE INTEGRATION (SSOT Compliance)

### Before ANY Documentation Operation

Load governance rules:

1. **File Placement Rules:**
   - Load: `_manifests/file-placement-policy.yaml` (enforced policy)
   - Forbidden patterns: PHASE-*, SESSION-*, docs_md/, root .md files
   - Correct locations: ONLY in `docs/` or `_archive/`

2. **Content Authority:**
   - Load: `cortex-master.yaml` (live capabilities source)
   - Load: `.github/prompts/cortex-doc.prompt.md` (structure authority)
   - Verify documentation reflects actual live features

3. **Duplicate Prevention:**
   - Load: `_manifests/content-registry.yaml` (SSOT for content hashes)
   - Check: Does content already exist elsewhere?
   - Action: If YES → Consolidate. If NO → Create new.

4. **Archive Preservation:**
   - Load: `_manifests/content-registry.yaml` (archive audit trail)
   - Verify: All archived files have metadata entries
   - Confirm: No files deleted (only archived)

---

## OUTPUT DEFAULTS

| Command | Output Format | Location |
|---------|---|---|
| `/docs-status` | Terminal table | STDOUT |
| `/docs-plan` | Terminal execution plan | STDOUT |
| `/docs-migrate` | Terminal migration status | STDOUT |
| `/docs-validate` | Terminal validation report | STDOUT + `_manifests/link-validation-report.yaml` |
| `/docs-cleanup` | Terminal archival report | STDOUT |
| `/docs-generate` | Terminal generation status | STDOUT + new .md file |
| `/docs-consolidate` | Terminal consolidation status | STDOUT + updated .md file |
| `/docs-lint` | Terminal format report | STDOUT + `_manifests/format-validation-report.yaml` |
| `/docs-audit` | Terminal audit findings | STDOUT + section-specific report |

**Critical Rules:**
- ✅ Terminal output: Human-readable, actionable
- ✅ YAML manifests: Machine-readable, registry updates
- ✅ YAML reports: Findings stored in `_manifests/`
- ❌ NO markdown report files outside `docs/`
- ❌ NO working documents in active tree

---

## ANTI-PATTERNS (STRICTLY FORBIDDEN)

| Anti-Pattern | Impact | Prevention |
|---|---|---|
| Creating duplicate files | Bloat, confusion, sync issues | Check registry before creating |
| Markdown reports in root | SSOT conflict | Output to `docs/` or YAML only |
| Updating docs outside `docs/` | Navigation breaks | Centralize all docs in `docs/` |
| Date-stamped files in active tree | Temporal pollution | No dates in production filenames |
| Working session docs in `docs/` | Clutter, obsolescence | Archive working docs to `_archive/` |
| Orphaned content not linked | Invisible documentation | Cross-reference from index |
| Inconsistent naming | Navigation difficulty | All files follow production standard |
| Broken internal links | Navigation failures | Validate all links before finalizing |
| Missing audience tags | Unclear purpose | Tag every doc with audience |
| Duplicate sections across files | Maintenance nightmare | Consolidate duplicates |

---

## SUCCESS METRICS (Idempotent Target State)

| Metric | Target | Validation |
|--------|--------|---|
| **Total Files** | 80 (from 180+) | Inventory check |
| **Duplicate Files** | 0 | Content hash scan |
| **Files with Date Stamps** | 0 | Grep: `-20260[0-9]` |
| **Broken Links** | 0 | Link validator |
| **Docs without Audience Tag** | 0 | Frontmatter audit |
| **Consolidation Conflicts** | 0 | Registry verification |
| **Archived Files** | ~100 (from deleted) | Archive manifest count |
| **Navigation Coverage** | 100% reachable from root | Depth-first traversal |
| **Naming Compliance** | 100% production standard | File listing check |
| **Idempotent Execution** | All commands safe to repeat | Repeat 3x, verify identical result |

---

## /docs-discover COMMAND (File Discovery & Consolidation Planning)

**Purpose**: Scan CORTEX root and recursively traverse all folders to identify scattered .md/.txt files and plan consolidation strategy

**Input**: 
- Root directory: `/Users/asifhussain/PROJECTS/CORTEX`
- Blacklist configuration: `docs/_manifests/file-discovery-blacklist.yaml`

**Output**: 
- Discovery report: `docs/_manifests/discovery-report.yaml`
- Move/archive plan: `docs/_manifests/consolidation-plan.yaml`

### Execution Steps

```bash
# Step 1: Scan root directory
find /Users/asifhussain/PROJECTS/CORTEX -maxdepth 1 -type f \( -name "*.md" -o -name "*.txt" \) | sort

# Step 2: Recursively traverse all folders (excluding protected patterns)
find /Users/asifhussain/PROJECTS/CORTEX -type f \( -name "*.md" -o -name "*.txt" \) \
  -not -path "*/\.git/*" \
  -not -path "*/__pycache__/*" \
  -not -path "*.egg-info/*" \
  -not -path "*/.venv/*" \
  | sort

# Step 3: Apply blacklist filter
# Exclude all patterns defined in file-discovery-blacklist.yaml protected_files

# Step 4: Categorize discovered files
# - Files to move to docs/
# - Files to archive in docs/_archive/
# - Files protected (skip)
# - Files excluded (skip)

# Step 5: Generate discovery report
# Create YAML with categories: files_discovered, files_to_move, files_to_archive, files_protected, summary
```

### Discovery Report Format

```yaml
discovery_report:
  metadata:
    timestamp: "2026-01-20T14:00:00Z"
    phase: "Phase 0"
    status: "DISCOVERY_ONLY"  # No files moved, report only
  
  summary:
    files_discovered: 0
    files_to_move: 0
    files_to_archive: 0
    files_protected: 0
    
  files_discovered:
    to_move:
      - source: "path/to/file.md"
        destination: "docs/section/"
        category: "documentation"
        status: "ready_to_move"
    
    to_archive:
      - source: "path/to/report.md"
        destination: "docs/_archive/reports/"
        category: "working_artifact"
    
    protected:
      - file: "requirements.txt"
        reason: "system_critical"
        status: "protected"
```

### Blacklist Enforcement

**Files/Patterns to ALWAYS protect:**
- `requirements.txt` - System critical
- `pytest.ini` - Test configuration
- `.github/prompts/*.prompt.md` - Agent prompts
- `.github/agents/*.md` - Agent system
- `cortex/**/*.py` - Application code
- `.git/**/*` - Git metadata
- `__pycache__/**` - Python cache
- All files matching exclusion patterns in `file-discovery-blacklist.yaml`

### Safety Guarantees

✅ **No files moved** during discovery phase  
✅ **No files deleted** - only categorized  
✅ **Blacklist applied** before any categorization  
✅ **Report generated** for human review  
✅ **Safe to repeat** - same result each time  

### Integration with Phases 1-5

- **Phase 0** (this command): Discover and plan
- **Phase 1** (cortex-doc.prompt.md): Map current to target
- **Phase 2** (cortex-doc.prompt.md): Archive obsolete files
- **Phase 3** (cortex-doc.prompt.md): Create target structure
- **Phase 4** (cortex-doc.prompt.md): Consolidate & format
- **Phase 5** (cortex-doc.prompt.md): Final naming & deployment

---

## REPEATED EXECUTION SAFETY CHECKLIST

Before every run:

- [ ] **Load Registry**: Verify `_manifests/content-registry.yaml` current
- [ ] **Check Duplicates**: Scan for files with identical content hashes
- [ ] **Detect Changes**: Compare source files with documented state
- [ ] **Plan Only**: Show what WOULD change, ask before executing
- [ ] **Atomic Operations**: Each file operation is all-or-nothing
- [ ] **Archive Everything**: Nothing deleted, only archived
- [ ] **Update Registry**: Every operation updates manifests
- [ ] **Verify Links**: No broken references after changes
- [ ] **Preserve Metadata**: Keep frontmatter when updating files
- [ ] **Report Status**: Clear before/after comparison

---

## INTEGRATION WITH OTHER AGENTS

### Interaction with cortex-builder.md

| Agent | Interaction | Governance |
|---|---|---|
| **cortex-doc** | Extracts live capabilities from implemented features | Read-only from `cortex-master.yaml` |
| **cortex-builder** | Implements features, cortex-doc documents them | cortex-builder updates master plan |
| **Coordination** | cortex-doc waits for AC-ID completion before documenting | cortex-builder signals AC-ID completion |

### Interaction with cortex-gap-detection.md

| Agent | Interaction | Governance |
|---|---|---|
| **cortex-doc** | Documents current capabilities | Receives gap findings |
| **cortex-gap-detection** | Finds design-build gaps | Reports missing documentation |
| **Coordination** | cortex-doc creates docs for gap remediation | Gap findings trigger new doc creation |

### Interaction with cortex-review.md

| Agent | Interaction | Governance |
|---|---|---|
| **cortex-doc** | Ensures compliance documentation exists | Receives compliance audit results |
| **cortex-review** | Verifies documentation completeness | Reviews doc quality, coverage |
| **Coordination** | cortex-doc creates missing docs identified in audit | Verification triggers doc creation |

---

## REFERENCES

- **Master Plan**: `.github/prompts/cortex-doc.prompt.md` (structure authority)
- **File Policy**: This document (SSOT for file placement)
- **Registry**: `_manifests/content-registry.yaml` (duplicate prevention)
- **Live Features**: `cortex-master.yaml` (capability source)
- **Archived History**: `docs/_archive/INDEX.md` (historical reference)

