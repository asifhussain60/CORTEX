# 🧹 Cleanup Enhancements

**Purpose:** Three specialized cleanup operations with surgical precision and zero-break guarantees.

## Operation 1: Surgical Cleanup with Test Harness (Admin Only)

**Commands:**
- `cleanup with tests` - Zero-break guarantee via test harness
- `surgical cleanup` - Category-level cleanup with automatic rollback
- `safe cleanup` - Validated cleanup with baseline comparison

**What It Does:**
1. **Baseline Capture** - Runs all tests, records coverage % (5-10 sec)
2. **Repository Scan** - Finds redundant, deprecated, temp files (~5 sec)
3. **Category-Level Cleanup** - Processes logs → temp → cache → redundant → deprecated
   - Backs up files before deletion
   - Runs tests after each category
   - **Automatic rollback if tests fail**
4. **Validation Report** - Test comparison, coverage changes, space freed

**Performance:** 1-2 minutes total (92% faster than file-by-file validation)

**Safety Guarantees:**
- ✅ Zero-break (tests must pass)
- ✅ Automatic rollback on failures
- ✅ Backup before every deletion
- ✅ Git checkpoint integration

**Example:**
```
You: "cleanup with tests"

CORTEX:
  📊 Baseline: 834/834 tests (89.5% coverage)
  
  📦 Category: logs (45 files)
  ✅ Tests: 834/834 ✓
  
  📦 Category: temp (120 files)
  ❌ Tests: 832/834 (2 failures)
  🔄 Rolling back temp...
  
  Files Deleted: 45 (logs only)
  Space Freed: 17.5 MB
```

**Guide:** `cortex-brain/documents/implementation-guides/cleanup-enhancement-guide.md` (Section: Surgical Cleanup)

---

## Operation 2: Markdown Consolidation (Admin Only)

**Commands:**
- `consolidate markdown` - Intelligent consolidation of 600+ files
- `consolidate documents` - Same as above
- `merge markdown files` - Consolidate with 4 strategies

**What It Does:**
1. **Discovery** - Scans cortex-brain/documents/ (~0.1 sec for 683 files)
2. **Analysis** - Identifies consolidation opportunities with 4 strategies:
   - **Eliminate Duplicates** - SHA256 hash matching
   - **Time-Series Merge** - Multi-phase reports (PHASE-1, PHASE-2 → COMPLETE)
   - **Topic Clustering** - Related content (4+ files on same topic)
   - **README → INDEX** - Standardization
3. **Consolidation** - Archives originals (30-day retention), creates consolidated files
4. **Report** - Files before/after, size savings, rules applied

**Performance:** <2 minutes for 683 files

**Expected Results:**
- **683 files → 242 files** (441 reduction, 64% decrease)
- **Reports:** 302 → ~50 files (83% reduction)
- **Analysis:** 80 → ~30 files (62% reduction)

**Example:**
```
You: "consolidate markdown"

CORTEX:
  ✅ Discovered: 683 files (0.11s)
  ✅ Identified: 35 consolidation rules (0.01s)
  
  Rules:
  • Topic: implementation (129 files → 128 reduction)
  • Topic: documentation (30 files → 29 reduction)
  • Duplicate: PLAN.md (1 file → 1 reduction)
  
  Estimated: 441 files reduced (64.6%)
  
  [DRY RUN] - Review report before approving
```

**Safety:** 30-day archive retention, restore via copy from `.archive/` subdirectory

**Guide:** `cortex-brain/documents/implementation-guides/cleanup-enhancement-guide.md` (Section: Markdown Consolidation)

---

## Operation 3: User Repository Cleanup (User-Facing)

**Commands:**
- `cleanup` (when in user repository)
- `user cleanup` - Conservative cleanup for user projects
- `cleanup repository` - Safe deletion of logs, temp, cache

**What It Does:**
1. **Repository Scan** - Finds safe categories only (~5 sec)
2. **Preview** - Shows files by category, estimates savings
3. **Interactive Confirmation** - Auto-approve logs/temp/cache, requires confirmation for build artifacts
4. **Cleanup** - Deletes approved categories only

**Safe Categories:**
| Category | Patterns | Auto-Delete |
|----------|----------|-------------|
| **Logs** | `*.log`, `logs/` | ✅ Yes |
| **Temp** | `tmp/`, `*.tmp` | ✅ Yes |
| **Cache** | `__pycache__/`, `.cache/` | ✅ Yes |
| **Build Artifacts** | `.next/`, `dist/` | ⚠️ Confirmation |
| **IDE Files** | `.DS_Store`, `*.swp` | ✅ Yes |

**Protected Paths (Never Touch):**
- ❌ Source: `src/`, `lib/`, `app/`
- ❌ Tests: `tests/`, `*.test.*`
- ❌ Configs: `*.config.js`, `.env`
- ❌ Dependencies: `node_modules/`, `venv/`
- ❌ Version control: `.git/`

**Performance:** <1 minute for typical projects

**Expected Savings:**
- **Python projects:** 20-100 MB (`__pycache__/`, logs)
- **Build artifacts:** 50-200 MB (`.next/`, `dist/`, `node_modules/`)

**Example:**
```
You: "cleanup"  # In user project

CORTEX:
  ✅ Found: 245 files (87.3 MB)
  
  • Logs: 45 files (15.2 MB)
  • Temp: 120 files (52.1 MB)
  • Cache: 80 files (20.0 MB)
  
  Total Savings: 87.3 MB
  
  To proceed: "approve cleanup"
```

**Safety:**
- ✅ Protected path validation (hardcoded)
- ✅ Conservative detection (prefers false negatives)
- ✅ Interactive confirmation for non-obvious deletions

**Guide:** `cortex-brain/documents/implementation-guides/cleanup-enhancement-guide.md` (Section: User Repository Cleanup)

---

## Comparison Matrix

| Feature | Surgical Cleanup | Markdown Consolidation | User Cleanup |
|---------|-----------------|----------------------|--------------|
| **Target** | CORTEX repo | CORTEX documents | User repos |
| **Scope** | All file types | Markdown only | Safe categories |
| **Validation** | Test harness | SHA256 + content | Protected paths |
| **Safety** | Zero-break | Archive 30-day | Conservative |
| **Speed** | 1-2 min | <2 min | <1 min |
| **Reduction** | 50-200 MB | 441 files (64%) | 50-200 MB |
| **Rollback** | Automatic | Manual (archive) | None (restore from git) |
| **Admin Only** | ✅ Yes | ✅ Yes | ❌ No |

**Complete Guide:** `cortex-brain/documents/implementation-guides/cleanup-enhancement-guide.md`
