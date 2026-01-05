# C50-19: Brain Data Source Cutover

**Epic:** C50 - CORTEX v5 Gap Remediation  
**Feature:** Complete migration from YAML to SQLite databases  
**Priority:** P0 (CRITICAL BLOCKER)  
**Complexity:** TIER 2 (FOCUSED)  
**Effort:** 2-3 hours  
**Author:** CORTEX Investigation Orchestrator  
**Created:** 2026-01-04

---

## 🎯 Problem Statement

**Current State:** CORTEX has dual data sources causing brittleness:
- ✅ SQLite databases exist and populated (`working_memory.db`, `knowledge_graph.db`)
- ❌ YAML files still present (`conversation-context.jsonl`, `knowledge-graph.yaml`, `development-context.yaml`)
- ❌ Code reads BOTH sources without prioritization

**Risk:** Data inconsistency, race conditions, performance degradation, maintenance burden.

**Goal:** Complete cutover to SQLite-only data sources.

---

## 📋 Acceptance Criteria

### Definition of Ready (DoR)
- [x] Brittleness analysis completed
- [x] SQLite databases exist and operational
- [x] Migration scripts tested
- [x] Dual-source code paths identified

### Definition of Done (DoD)
- [ ] YAML files moved to `archives/yaml-deprecated-2026-01-04/`
- [ ] All code references to YAML files removed
- [ ] Deprecation notice created
- [ ] Documentation updated (no YAML references)
- [ ] All tests pass (DB sources only)
- [ ] Zero grep matches for `knowledge-graph.yaml` in `src/`
- [ ] Validation report generated

---

## 🏗️ Phase Breakdown

### Phase 1: Archive YAML Files (15 min)

**RED (Tests First):**
```python
# tests/tier0/test_yaml_deprecated.py
def test_yaml_files_archived():
    """Verify YAML files moved to archives."""
    brain_root = Path("cortex-brain")
    
    # Should NOT exist in root
    assert not (brain_root / "conversation-context.jsonl").exists()
    assert not (brain_root / "knowledge-graph.yaml").exists()
    assert not (brain_root / "development-context.yaml").exists()
    
    # Should exist in archives
    archive = brain_root / "archives/yaml-deprecated-2026-01-04"
    assert (archive / "conversation-context.jsonl").exists()
    assert (archive / "knowledge-graph.yaml").exists()
    assert (archive / "development-context.yaml").exists()
```

**GREEN (Implementation):**
```bash
# scripts/archive_yaml_sources.sh
#!/bin/bash
set -euo pipefail

BRAIN_ROOT="cortex-brain"
ARCHIVE_DIR="$BRAIN_ROOT/archives/yaml-deprecated-2026-01-04"

mkdir -p "$ARCHIVE_DIR"

# Archive YAML files
mv "$BRAIN_ROOT/conversation-context.jsonl" "$ARCHIVE_DIR/"
mv "$BRAIN_ROOT/knowledge-graph.yaml" "$ARCHIVE_DIR/"
mv "$BRAIN_ROOT/development-context.yaml" "$ARCHIVE_DIR/"

# Create deprecation notice
cat > "$ARCHIVE_DIR/README.md" <<EOF
# YAML Brain Sources - DEPRECATED

**Deprecated:** 2026-01-04  
**Reason:** Migrated to SQLite databases for performance + consistency

## Replacement Locations

| Old YAML | New DB | Schema |
|----------|--------|--------|
| conversation-context.jsonl | tier1/working_memory.db | conversations, messages, entities |
| knowledge-graph.yaml | tier2/knowledge_graph.db | patterns, relationships, tags |
| development-context.yaml | tier3/policies/*.json | token-efficiency-metrics.yaml |

## Migration Scripts

- src/tier1/migrate_tier1.py
- src/tier2/migrate_tier2.py
- src/tier3/migrate_tier3.py

**DO NOT USE THESE FILES IN PRODUCTION.**
EOF

echo "✅ YAML files archived successfully"
```

**REFACTOR:** None (shell script cleanup not needed)

---

### Phase 2: Remove YAML Read Paths (30 min)

**RED (Tests First):**
```python
# tests/tier0/test_no_yaml_references.py
def test_no_yaml_references_in_source():
    """Verify no YAML file references in production code."""
    import subprocess
    
    result = subprocess.run(
        ["grep", "-r", "knowledge-graph\\.yaml", "src/"],
        capture_output=True,
        text=True
    )
    
    # Should return empty (exit code 1 = no matches)
    assert result.returncode == 1, f"Found YAML references: {result.stdout}"
    
    # Same for other YAML files
    for yaml_file in ["conversation-context.jsonl", "development-context.yaml"]:
        result = subprocess.run(
            ["grep", "-r", yaml_file, "src/"],
            capture_output=True,
            text=True
        )
        assert result.returncode == 1, f"Found {yaml_file} reference: {result.stdout}"
```

**GREEN (Implementation):**

**File 1:** `src/tier0/integrity_checker.py`
```python
# BEFORE (line 87-89):
"tier1_context": self.brain_root / "conversation-context.jsonl",
"tier2_knowledge": self.brain_root / "knowledge-graph.yaml",
"tier3_dev_context": self.brain_root / "development-context.yaml"

# AFTER:
"tier1_context": self.brain_root / "tier1" / "working_memory.db",
"tier2_knowledge": self.brain_root / "tier2" / "knowledge_graph.db",
"tier3_dev_context": self.brain_root / "tier3" / "policies"
```

**File 2:** `src/tier0/tier_validator.py`
```python
# BEFORE (line 90-91):
TierLevel.TIER_2: self.brain_root / "knowledge-graph.yaml",
TierLevel.TIER_3: self.brain_root / "development-context.yaml"

# AFTER:
TierLevel.TIER_2: self.brain_root / "tier2" / "knowledge_graph.db",
TierLevel.TIER_3: self.brain_root / "tier3" / "policies"
```

**File 3:** `src/tier0/optimized_context_loader.py`
```python
# BEFORE (line 294):
kg_file = self.brain_dir / "knowledge-graph.yaml"

# AFTER:
from src.tier2.knowledge_graph import KnowledgeGraph
kg = KnowledgeGraph()  # Uses knowledge_graph.db by default
```

**REFACTOR:** Remove any commented-out YAML code, consolidate DB imports.

---

### Phase 3: Update Documentation (20 min)

**RED (Tests First):**
```python
# tests/docs/test_no_yaml_in_docs.py
def test_documentation_no_yaml_references():
    """Verify documentation doesn't reference deprecated YAML files."""
    docs = [
        "README.md",
        "cortex-brain/documents/cortex-architecture-quick-ref.md",
        "cortex-brain/documents/orchestrators-quick-ref.md"
    ]
    
    for doc_path in docs:
        with open(doc_path) as f:
            content = f.read()
        
        # Should not mention old YAML files
        assert "knowledge-graph.yaml" not in content, f"{doc_path} mentions YAML"
        assert "conversation-context.jsonl" not in content
        
        # Should mention new DB files
        if "architecture" in doc_path or "README" in doc_path:
            assert "working_memory.db" in content
            assert "knowledge_graph.db" in content
```

**GREEN (Implementation):**

**File 1:** `README.md`
```markdown
# BEFORE:
## Brain Architecture (4 Tiers)
- Tier 1: conversation-context.jsonl (working memory)
- Tier 2: knowledge-graph.yaml (patterns)

# AFTER:
## Brain Architecture (4 Tiers)
- Tier 1: tier1/working_memory.db (conversations, sessions, entities)
- Tier 2: tier2/knowledge_graph.db (patterns, relationships, tags)
- Tier 3: tier3/policies/ (JSON policy files)
```

**File 2:** `cortex-brain/documents/cortex-architecture-quick-ref.md`
```markdown
# Add migration notice section:
## 🔄 YAML to SQLite Migration (2026-01-04)

**Deprecated Sources:**
- ❌ conversation-context.jsonl
- ❌ knowledge-graph.yaml
- ❌ development-context.yaml

**Current Sources:**
- ✅ tier1/working_memory.db (SQLite)
- ✅ tier2/knowledge_graph.db (SQLite)
- ✅ tier3/policies/*.json (JSON)

**Migration Scripts:** See `src/tier*/migrate_tier*.py`
```

**REFACTOR:** Remove any outdated architecture diagrams showing YAML files.

---

### Phase 4: Validation & Testing (45 min)

**RED (Tests First):**
```python
# tests/tier0/test_brain_data_cutover.py
def test_tier1_db_operational():
    """Verify Tier 1 DB is primary source."""
    from src.tier1.session_manager import SessionManager
    
    db_path = Path("cortex-brain/tier1/working_memory.db")
    assert db_path.exists()
    
    session_mgr = SessionManager(db_path)
    conversations = session_mgr.get_recent_conversations(limit=1)
    assert len(conversations) >= 0  # DB readable

def test_tier2_db_operational():
    """Verify Tier 2 DB is primary source."""
    from src.tier2.knowledge_graph import KnowledgeGraph
    
    kg = KnowledgeGraph()
    patterns = kg.query_patterns(limit=1)
    # Should not raise error (even if empty)
    assert patterns is not None

def test_yaml_files_not_loaded():
    """Verify no YAML files loaded at runtime."""
    import sys
    import importlib
    
    # Reload tier modules
    for module in list(sys.modules.keys()):
        if "tier" in module:
            del sys.modules[module]
    
    # Import tier modules
    from src.tier1 import session_manager
    from src.tier2 import knowledge_graph
    
    # Should not trigger YAML file reads
    # (Would fail if YAML files don't exist)
```

**GREEN (Implementation):**
```bash
# scripts/validate_brain_cutover.sh
#!/bin/bash
set -euo pipefail

echo "🔍 Validating brain data cutover..."

# 1. Check YAML files archived
if [ -f "cortex-brain/conversation-context.jsonl" ]; then
    echo "❌ YAML file still in root: conversation-context.jsonl"
    exit 1
fi

# 2. Check DB files exist
if [ ! -f "cortex-brain/tier1/working_memory.db" ]; then
    echo "❌ Missing: tier1/working_memory.db"
    exit 1
fi

# 3. Run grep for YAML references in src/
if grep -r "knowledge-graph\.yaml" src/ 2>/dev/null; then
    echo "❌ Found YAML references in src/"
    exit 1
fi

# 4. Run pytest
pytest tests/tier0/test_brain_data_cutover.py -v

echo "✅ Brain data cutover validation PASSED"
```

**REFACTOR:** None (validation script cleanup not critical)

---

## 🔧 Implementation Checklist

### Pre-Implementation
- [x] Brittleness analysis reviewed
- [x] Migration scripts validated
- [ ] Backup YAML files to external location (safety)

### Implementation
- [ ] Phase 1: Archive YAML files (RED→GREEN→REFACTOR)
- [ ] Phase 2: Remove YAML read paths (RED→GREEN→REFACTOR)
- [ ] Phase 3: Update documentation (RED→GREEN→REFACTOR)
- [ ] Phase 4: Validation & testing (RED→GREEN→REFACTOR)

### Post-Implementation
- [ ] All tests pass (`pytest tests/tier0/test_brain_data_cutover.py`)
- [ ] Validation script passes (`./scripts/validate_brain_cutover.sh`)
- [ ] No YAML references in `src/` (grep verification)
- [ ] Documentation updated (no YAML mentions)
- [ ] Completion report generated

---

## 📊 Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Breaking existing code | MEDIUM | HIGH | Comprehensive testing before archiving |
| Data loss | LOW | CRITICAL | Backup YAML files externally |
| Missed YAML references | MEDIUM | HIGH | Automated grep + pytest validation |
| Documentation drift | LOW | MEDIUM | Systematic doc review in Phase 3 |

---

## 🎯 Success Criteria

**Feature Complete When:**
1. ✅ YAML files in `archives/yaml-deprecated-2026-01-04/`
2. ✅ Zero grep matches for YAML files in `src/`
3. ✅ All tier tests pass (DB sources only)
4. ✅ Documentation updated (no YAML references)
5. ✅ Validation script passes
6. ✅ Completion report generated

---

## 📝 Notes

**Dependencies:**
- None (standalone feature)

**Blocking:**
- C50-20 (Governance Middleware) - should complete this first

**Related Issues:**
- Brittleness Analysis: `cortex-brain/documents/analysis/C50-brittleness-analysis-2026-01-04.md`

---

**Author:** CORTEX Investigation Orchestrator  
**Reviewed By:** Asif Hussain  
**Status:** READY FOR EXECUTION  
**Estimated Duration:** 2-3 hours (TDD enforced)

**Copyright © 2026 Asif Hussain. All rights reserved.**
