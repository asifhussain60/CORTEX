# CORTEX Brain Transfer - Quick Start Guide

**Feature:** Export and import brain patterns between CORTEX instances  
**Version:** 1.0  
**Author:** Asif Hussain  
**Date:** 2025-11-18

---

## 🎯 What Is Brain Transfer?

Brain transfer allows you to share learned knowledge between CORTEX instances without git merge conflicts. Each CORTEX learns from your work (patterns, workflows, validation insights), and you can explicitly export/import this knowledge.

**Use Cases:**
- 💻 Multiple machines (work PC + laptop)
- 👥 Team collaboration (share best practices)
- 🔄 Git branches (merge knowledge separately from code)
- 📚 Knowledge backup (preserve learnings before reinstall)

---

## 🚀 Quick Start

### Export Brain (Share Your Knowledge)

**Natural Language:**
```
export brain
```

**What It Does:**
- Exports workspace patterns from Tier 2 knowledge graph
- Creates `cortex-brain/exports/brain-export-YYYYMMDD-HHMMSS.yaml`
- Includes confidence scores, usage counts, namespaces
- Human-readable YAML format

**Options:**
```
export brain                    # Workspace patterns only (default)
export cortex patterns          # CORTEX framework patterns only
export all learned knowledge    # Everything (workspace + cortex)
```

**CLI Alternative:**
```bash
python -m src.brain_transfer.cli export workspace
python -m src.brain_transfer.cli export cortex 0.7  # Min confidence 0.7
```

---

### Import Brain (Learn from Others)

**Natural Language:**
```
import brain from brain-export-20251117-143000.yaml
```

**What It Does:**
- Loads patterns from YAML file
- Auto-detects conflicts (same pattern, different confidence)
- Applies intelligent merge strategies:
  - **Similar (>80%):** Weighted confidence averaging
  - **Identical:** Keeps higher confidence
  - **Unique:** Adds as new pattern
- Preserves namespace boundaries (cortex.* vs workspace.*)
- Creates audit trail of all decisions

**Auto-Import Latest:**
```
import brain
```
Automatically finds most recent export in `cortex-brain/exports/`

**CLI Alternative:**
```bash
python -m src.brain_transfer.cli import brain-export-20251117-143000.yaml
```

---

## 📋 YAML Export Format

```yaml
# CORTEX Brain Export
# Generated: 2025-11-17T14:30:00Z
# Source Machine: DESKTOP-PRIMARY-12345
# CORTEX Version: 3.0.1

version: "1.0"
export_date: "2025-11-17T14:30:00Z"
source_machine_id: "DESKTOP-PRIMARY-12345"
cortex_version: "3.0.1"
total_patterns: 54
scope: "workspace"

statistics:
  patterns_exported: 54
  confidence_range: [0.50, 0.95]
  namespaces: ["workspace.ksessions", "workspace.authentication"]
  avg_access_count: 12.5
  total_size_bytes: 45678

patterns:
  - pattern_id: "auth_workflow_001"
    pattern_type: "workflow"
    title: "JWT Authentication Implementation"
    confidence: 0.85
    namespace: "workspace.authentication"
    access_count: 23
    last_accessed: "2025-11-17T12:00:00Z"
    context:
      files: ["AuthService.cs", "LoginController.cs", "AuthTests.cs"]
      steps: ["validate_credentials", "generate_token", "set_session"]
      success_rate: 0.94
```

---

## 🧠 Intelligent Merge Strategies

### Strategy 1: Identical Patterns
**Scenario:** Same pattern_id, same title, same structure  
**Action:** Keep higher confidence  
**Example:**
```
Local:    auth_workflow_001 (confidence: 0.80)
Imported: auth_workflow_001 (confidence: 0.85)
Result:   Keep imported (0.85)
```

### Strategy 2: Similar Patterns (>80% match)
**Scenario:** Different pattern_id, similar content  
**Action:** Weighted merge based on confidence  
**Formula:** `merged_confidence = (local * local_weight) + (imported * imported_weight)`  
**Example:**
```
Local:    jwt_auth (confidence: 0.85, access_count: 20)
Imported: jwt_authentication (confidence: 0.90, access_count: 15)
Similarity: 85%
Result:   Merged pattern (confidence: 0.87)
```

### Strategy 3: Unique Patterns
**Scenario:** No local match found  
**Action:** Add as new pattern  
**Example:**
```
Imported: oauth2_workflow (confidence: 0.88)
Result:   Added as new pattern
```

### Strategy 4: Conflicts (<80% similarity, contradictory)
**Scenario:** Same domain, contradictory advice  
**Action:** Keep local (prefer existing knowledge)  
**Example:**
```
Local:    "authentication uses JWT" (confidence: 0.85)
Imported: "authentication uses OAuth2" (confidence: 0.90)
Similarity: 60%
Result:   Keep local (preserves existing workflow)
```

---

## 🛡️ Namespace Protection

Brain transfer respects namespace boundaries:

**Namespaces:**
- `cortex.*` - CORTEX framework patterns (rarely exported)
- `workspace.*` - Your application patterns (primary export)

**Rules:**
1. ✅ Can import `workspace.*` patterns (safe)
2. ⚠️ Importing `cortex.*` patterns requires confirmation (rare)
3. ❌ Cannot mix namespaces in same pattern (enforced)
4. ✅ Cross-namespace imports create separate patterns

**Example:**
```yaml
# Safe: Workspace pattern
namespace: "workspace.authentication"

# Requires confirmation: CORTEX framework pattern
namespace: "cortex.intent_routing"
```

---

## 📊 Audit Trail

Every import creates an audit trail:

**Location:** `cortex-brain/exports/import-audit-YYYYMMDD-HHMMSS.yaml`

**Contents:**
```yaml
import_date: "2025-11-17T14:35:00Z"
source_file: "brain-export-20251117-143000.yaml"
total_patterns_processed: 54
merge_decisions:
  - pattern_id: "auth_workflow_001"
    strategy: "weighted_merge"
    reason: "Similar patterns (85% match)"
    confidence_before: 0.80
    confidence_after: 0.87
    timestamp: "2025-11-17T14:35:12Z"
  
  - pattern_id: "new_feature_template"
    strategy: "new"
    reason: "Unique pattern not in local brain"
    confidence_before: null
    confidence_after: 0.75
    timestamp: "2025-11-17T14:35:13Z"
```

---

## 🔧 Advanced Usage

### Export High-Confidence Only
```python
from src.brain_transfer import BrainExporter

exporter = BrainExporter()
exporter.export_brain(
    scope="workspace",
    min_confidence=0.7  # Only patterns with 70%+ confidence
)
```

### Custom Import Logic
```python
from src.brain_transfer import BrainImporter

importer = BrainImporter()
result = importer.import_brain(
    import_path=Path("brain-export-20251117.yaml"),
    auto_resolve_conflicts=True  # Auto-resolve without prompts
)

print(f"Imported {result['patterns_imported']} patterns")
print(f"Resolved {result['conflicts_resolved']} conflicts")
```

### Programmatic Access
```python
from src.brain_transfer import execute_brain_export, execute_brain_import

# Export
export_result = execute_brain_export(
    scope="all",
    min_confidence=0.5
)
print(export_result["message"])

# Import
import_result = execute_brain_import(
    import_path="brain-export-20251117.yaml",
    auto_resolve=True
)
print(import_result["message"])
```

---

## ❓ FAQ

### Q: Will importing overwrite my local patterns?
**A:** No. Intelligent merge strategies preserve your local knowledge:
- Identical patterns: Keeps higher confidence
- Similar patterns: Weighted merge
- Conflicts: Keeps local (prefers existing)
- Unique: Adds as new

### Q: Can I review before importing?
**A:** Currently auto-resolves. Future version will add:
```
import brain with review
```

### Q: What if namespaces conflict?
**A:** Import creates separate patterns per namespace:
```
Local:    workspace.authentication.jwt_auth
Imported: workspace.authentication.oauth_auth
Result:   Both patterns coexist
```

### Q: How do I share with teammates?
**A:**
1. Export: `export brain`
2. Share YAML file (email, Slack, git)
3. Teammate: `import brain from your-export.yaml`

### Q: Can I undo an import?
**A:** Not yet. Backup before importing:
```
export brain  # Creates backup first
import brain from teammate-export.yaml
```

---

## 🎓 Best Practices

1. **Export regularly** - Weekly backup of learned knowledge
2. **Use descriptive exports** - Rename files: `brain-export-authentication-feature.yaml`
3. **Review audit trails** - Check `import-audit-*.yaml` after imports
4. **Start with workspace scope** - Rarely need to export `cortex.*` patterns
5. **Test imports** - Import to test machine first before production
6. **Track in git** - YAML files are human-readable, track separately from brain databases

---

## 📚 Related Documentation

- **Architecture:** `cortex-brain/documents/planning/BRAIN-IMPLANT-ARCHITECTURE.md`
- **Tier 2 API:** `prompts/shared/technical-reference.md` (Knowledge Graph section)
- **Git Strategy:** See CC01 conversation history (git merge discussion)

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Version:** 1.0.0  
**Status:** ✅ Production Ready
