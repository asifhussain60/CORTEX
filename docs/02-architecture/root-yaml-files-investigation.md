# Root YAML Files Investigation Report

**Date:** 2026-01-26  
**Status:** Investigation Complete

---

## Summary of Findings

### 1. **mkdocs.yml** - MUST STAY IN ROOT ⭐

**Current Location:** `./mkdocs.yml` (root)

**Usage:**
- MkDocs standard convention - build tool expects it in root
- MkDocs searches for `mkdocs.yml` in project root automatically
- Cannot be moved without breaking documentation build pipeline

**Evidence:**
- Standard MkDocs behavior (de facto standard across all MkDocs projects)
- Documentation tool looks for it in root by default
- Would require changing CI/CD and build scripts

**Verdict:** ✅ **KEEP IN ROOT** - MkDocs convention

---

### 2. **.knowledge-index.yaml** - ACTIVELY USED, CAN BE RELOCATED 🔄

**Current Location:** `/.knowledge-index.yaml` (root)

**Usage:**
- `cortex/brain/knowledge/hybrid_loader.py` actively loads it
- Hardcoded path: `self.repo_root / ".knowledge-index.yaml"`
- Part of AC-HYBRID-KNOWLEDGE-001 system

**Key Finding:**
```python
def __init__(self, repo_root: Optional[Path] = None):
    if repo_root is None:
        repo_root = Path(__file__).parent.parent.parent.parent  # Project root
    
    self.knowledge_index_path = self.repo_root / ".knowledge-index.yaml"
```

**Analysis:**
- The loader resolves `repo_root` as project root
- Path is **NOT** hardcoded to root - it's calculated from file location
- Can be relocated if we update the path construction logic

**Verdict:** ✅ **CAN BE RELOCATED** - Need to update hybrid_loader.py

**Recommended Location:** `cortex_brain/tier3/knowledge/.knowledge-index.yaml`

---

### 3. **.knowledge-synthesis-rules.yaml** - ACTIVELY USED, CAN BE RELOCATED 🔄

**Current Location:** `/.knowledge-synthesis-rules.yaml` (root)

**Usage:**
- `cortex/brain/knowledge/hybrid_loader.py` actively loads it
- Hardcoded path: `self.synthesis_rules_path = self.repo_root / ".knowledge-synthesis-rules.yaml"`
- Part of AC-HYBRID-KNOWLEDGE-002 system

**Analysis:**
- Same situation as .knowledge-index.yaml
- Can be relocated by updating path in hybrid_loader.py

**Verdict:** ✅ **CAN BE RELOCATED** - Need to update hybrid_loader.py

**Recommended Location:** `cortex_brain/tier3/knowledge/.knowledge-synthesis-rules.yaml`

---

## Reorganization Plan

### Option A: MINIMAL (Recommended)
**Keep in root:**
- ✅ `mkdocs.yml` (MkDocs standard)
- ✅ `cortex-config.yaml` (path resolver marker)

**Move to cortex_brain/tier3/knowledge/:**
- 🔄 `.knowledge-index.yaml`
- 🔄 `.knowledge-synthesis-rules.yaml`

**Delete from root:**
- ❌ Already deleted: `cortex-impl-map.yaml`

**Code Changes Required:**
1. Update `cortex/brain/knowledge/hybrid_loader.py`:
   - Change knowledge index path to `cortex_brain/tier3/knowledge/.knowledge-index.yaml`
   - Change synthesis rules path to `cortex_brain/tier3/knowledge/.knowledge-synthesis-rules.yaml`

**Benefits:**
- Root becomes cleaner (only 2 files)
- Knowledge files co-located with knowledge tier 3
- Logical organization
- Minimal code changes

---

### Option B: AGGRESSIVE
Move mkdocs.yml to `_workspaces/config/mkdocs.yml`

**Requires:**
- Update CI/CD pipelines to use `--config-file` flag
- Update documentation build scripts
- More invasive changes

**Not Recommended:** MkDocs convention expects it in root

---

## Recommendation

**Execute Option A:**
1. Move `.knowledge-index.yaml` → `cortex_brain/tier3/knowledge/`
2. Move `.knowledge-synthesis-rules.yaml` → `cortex_brain/tier3/knowledge/`
3. Update `cortex/brain/knowledge/hybrid_loader.py` (3 lines changed)
4. Keep `mkdocs.yml` in root (MkDocs standard)
5. Keep `cortex-config.yaml` in root (path resolver marker)

**Result:**
- ✅ Root directory: 2 essential files
- ✅ Knowledge files: Organized in cortex_brain/tier3/knowledge/
- ✅ No build pipeline changes
- ✅ Follows file placement policy

---

## Files to Process

**DELETE:**
- ~~`cortex-impl-map.yaml`~~ (already deleted)

**MOVE:**
- `.knowledge-index.yaml` → `cortex_brain/tier3/knowledge/.knowledge-index.yaml`
- `.knowledge-synthesis-rules.yaml` → `cortex_brain/tier3/knowledge/.knowledge-synthesis-rules.yaml`

**KEEP:**
- `mkdocs.yml` (MkDocs standard)
- `cortex-config.yaml` (path resolver)

**CODE UPDATES:**
- `cortex/brain/knowledge/hybrid_loader.py` (update 2 path definitions)
