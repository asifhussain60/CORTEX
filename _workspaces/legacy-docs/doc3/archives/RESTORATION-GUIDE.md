# Archive Restoration Guide

**Archive Date:** 2026-01-03  
**Reason:** Documentation cleanup - orphaned files removal  
**Location:** `docs/archives/`

---

## 📦 Archived Content

### **Orphaned Knowledge Files** (`orphaned-knowledge-20260103-102230/`)

The following knowledge base files were archived because they were not linked from any navigation:

- `service-design.html` - Microservices service design patterns
- `integration-testing.html` - Integration testing strategies
- `orm-best-practices.html` - ORM best practices guide
- `query-optimization.html` - Database query optimization
- `data-protection.html` - Security data protection guide
- `test-tabs.html` - Lens diagnostics prototype test file

**Restoration Process:**
```powershell
# To restore a specific file
Move-Item "docs/archives/orphaned-knowledge-20260103-102230/service-design.html" "docs/knowledge/microservices/" -Force

# Then link it in docs/knowledge/index.html under appropriate section
```

---

### **Orphaned Best Practices** (`orphaned-best-practices-20260103-102230/`)

The following files were incorrectly nested in `best-practices/best-practices/`:

- `collaboration-patterns.html` - Team collaboration patterns
- `planning-guidelines.html` - Project planning guidelines
- `coding-standards.html` - Coding standards and conventions

**Restoration Process:**
```powershell
# To restore to correct location
Move-Item "docs/archives/orphaned-best-practices-20260103-102230/coding-standards.html" "docs/best-practices/" -Force

# Then link in docs/best-practices/index.html
```

---

### **Prototypes** (`prototypes-20260103-101816/`)

All prototype files moved to archive on 2026-01-03 10:18:16.

**Categories:**
- Orchestrators (11 files)
- Security (13 files)
- Toolkit Manager (1 file)
- Token Optimization (1 file)
- Knowledge Hub (1 file)
- STS (1 file)
- Lens (1 file)

**Restoration Process:**
```powershell
# To restore specific prototype
Move-Item "docs/archives/prototypes-20260103-101816/prototypes/orchestrators/tdd-orchestrator.html" "docs/prototypes/orchestrators/" -Force

# Ensure docs/prototypes/ directory structure exists
```

---

### **Validation Stubs** (`validation-stubs-20260103-101816/`)

Placeholder validation pages:
- `capabilities.html`
- `metrics.html`

**Restoration Process:**
```powershell
# Restore if validation section is re-implemented
Move-Item "docs/archives/validation-stubs-20260103-101816/validation/" "docs/" -Recurse -Force
```

---

## 🔗 Re-Linking Guidelines

After restoring a file, add navigation links in appropriate index files:

### For Knowledge Base Files
Edit `docs/knowledge/index.html`:
```html
<a href="microservices/service-design.html" class="knowledge-link">
    <h3>Service Design Patterns</h3>
    <p>Comprehensive guide to microservices service design</p>
</a>
```

### For Best Practices Files
Edit `docs/best-practices/index.html`:
```html
<a href="coding-standards.html" class="practice-link">
    <h3>Coding Standards</h3>
    <p>Team coding standards and conventions</p>
</a>
```

### For Prototypes
Edit `docs/sitemap.html` or create `docs/prototypes/index.html`:
```html
<a href="prototypes/orchestrators/tdd-orchestrator.html">
    TDD Orchestrator Prototype
</a>
```

---

## 📊 Cleanup Statistics

| Archive | Files | Reason |
|---------|-------|--------|
| Orphaned Knowledge | 6 | Not linked from navigation |
| Orphaned Best Practices | 3 | Incorrectly nested directory |
| Prototypes | 32 | Completed prototypes archived |
| Validation Stubs | 2 | Placeholder pages |
| **Total** | **43** | — |

---

## ⚠️ Important Notes

1. **30-Day Hold:** Archives will be retained for minimum 30 days before deletion consideration
2. **Git History:** All files remain in Git history even if deleted
3. **Link Validation:** After restoration, run `python scripts/doc_cleanup_scanner.py` to verify links
4. **Path Corrections:** Ensure CSS/asset paths are correct for restored location

---

**Generated:** 2026-01-03 10:22:30  
**Orchestrator:** cortex-doc-cleanup v1.0.0  
**Author:** Asif Hussain
