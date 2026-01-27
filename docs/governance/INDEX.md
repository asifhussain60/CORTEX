# 📚 CORTEX Global File Naming Standards - Complete Index

**Status:** ✅ Deployed & Active | **Date:** 2026-01-27 | **Tag:** `global-file-naming-standards-20260127`

---

## 🎯 Quick Navigation

### 🚀 **Just Getting Started?**
→ Read: `docs/governance/file-naming-quick-start.md` (5 min)

### 💼 **For Developers**
→ Read: `docs/governance/file-naming-quick-start.md` (5 min)
→ Reference: `cortex_brain/tier0/governance/file-naming-standards.md` (20 min)

### 🔧 **For Tool Integration**
→ Review: `cortex/tools/file_naming_factory.py` (docstrings)
→ Copy pattern: See examples below

### 📖 **For Complete Understanding**
→ Read: `docs/governance/global-file-naming-standards-deployment.md` (15 min)
→ Study: `cortex_brain/tier0/governance/file-naming-standards.md` (30 min)
→ Review: `docs/governance/STANDARDS-DEPLOYMENT-COMPLETE.md` (10 min)

### 🔨 **To Change Standards**
→ Edit: `.cortex/standards/file-naming-config.yaml` (SINGLE file)
→ Also update: `cortex_brain/tier0/governance/file-naming-standards.md` (keep docs in sync)

---

## 📁 Complete File Listing

### Core Components

| File | Purpose | Size | Read Time |
|------|---------|------|-----------|
| `.cortex/standards/file-naming-config.yaml` | Configuration (SSOT) | 224 lines | 5 min |
| `cortex_brain/tier0/governance/file-naming-standards.md` | Governance document | 600+ lines | 30 min |
| `cortex/tools/file_naming_factory.py` | Python implementation | 536 lines | 15 min |

### Documentation

| File | Purpose | Size | Audience |
|------|---------|------|----------|
| `docs/governance/file-naming-quick-start.md` | Quick reference | 200 lines | All developers |
| `docs/governance/global-file-naming-standards-deployment.md` | Deployment guide | 320 lines | Architects, tech leads |
| `docs/governance/STANDARDS-DEPLOYMENT-COMPLETE.md` | Completion summary | 520 lines | Project managers |

---

## 🎯 Use Cases & Solutions

### Use Case 1: Generate Documentation Filename
```python
from cortex.tools.file_naming_factory import documentation

filename = documentation("guide", "deployment")
# Returns: "deployment-guide.md"
```
**Result:** `deployment-guide.md`

### Use Case 2: Generate Configuration Filename
```python
from cortex.tools.file_naming_factory import configuration

filename = configuration("prometheus", "production", "yml")
# Returns: "prometheus-production-config.yml"
```
**Result:** `prometheus-production-config.yml`

### Use Case 3: Generate Script Filename
```python
from cortex.tools.file_naming_factory import script

filename = script("deploy", "kubernetes")
# Returns: "deploy-kubernetes.sh"
```
**Result:** `deploy-kubernetes.sh`

### Use Case 4: Generate Python Module Filename
```python
from cortex.tools.file_naming_factory import python_module

filename = python_module("orchestrator", "migration")
# Returns: "migration_orchestrator.py"
```
**Result:** `migration_orchestrator.py` (snake_case, PEP 8)

### Use Case 5: Generate Test Filename
```python
from cortex.tools.file_naming_factory import test

filename = test("orchestrator", "integration")
# Returns: "test_integration_orchestrator.py"
```
**Result:** `test_integration_orchestrator.py`

### Use Case 6: Generate Plan Filename
```python
from cortex.tools.file_naming_factory import plan

filename = plan("migration", "phases")
# Returns: "migration-phases-plan.yaml"
```
**Result:** `migration-phases-plan.yaml`

### Use Case 7: Validate Existing Filename
```python
from cortex.tools.file_naming_factory import validate

result = validate("new-docker-guide.md")

print(result["is_valid"])        # False
print(result["issues"])          # ["Contains prohibited adjective: new"]
print(result["suggestions"])     # ["Remove 'new' or use more descriptive term"]
```

---

## 📋 Standards at a Glance

### Naming Patterns

```
Documentation:  {context}-{purpose}.md
Config:         {service}-config.yaml
Scripts:        {verb}-{noun}.sh
Python:         {noun}_{verb}.py (snake_case)
Tests:          test_{context}_{noun}.py
Plans:          {purpose}-{topic}-plan.yaml
```

### Scope Prefixes
```
docker-*        Docker/containers
wiring-*        Orchestration/wiring
migration-*     Migration
health-*        Health/monitoring
validate-*      Validation/testing
deploy-*        Deployment
config-*        Configuration
api-*           APIs
mcp-*           Model Context Protocol
```

### Rules Summary
```
✅ Kebab-case (except Python: snake_case)
✅ 16-32 chars optimal, 8-55 max
✅ Purpose-first naming
✅ Scope context included
❌ No adjectives (new, enhanced, improved, etc.)
❌ No versions (v1.0, 2.2)
❌ No dates (2026-01-27)
❌ No authors (asif-config.yaml)
❌ No status (-draft, -final)
```

---

## 🔄 Workflow Examples

### Workflow 1: Add a New Documentation File

```bash
# 1. Determine filename
python3 << 'EOF'
from cortex.tools.file_naming_factory import documentation
filename = documentation("troubleshooting", "docker")
print(filename)  # → docker-troubleshooting.md
EOF

# 2. Create file with that name
touch docs/docker-troubleshooting.md

# 3. Write content
# ...

# 4. Commit
git add docs/docker-troubleshooting.md
git commit -m "docs: Add Docker troubleshooting guide"
```

### Workflow 2: Add a New Configuration File

```bash
# 1. Determine filename
python3 << 'EOF'
from cortex.tools.file_naming_factory import configuration
filename = configuration("nginx", "staging")
print(filename)  # → nginx-staging-config.yaml
EOF

# 2. Create file with that name
touch config/nginx-staging-config.yaml

# 3. Write content (YAML)
# ...

# 4. Commit
git add config/nginx-staging-config.yaml
git commit -m "config: Add Nginx staging configuration"
```

### Workflow 3: Add a New Script

```bash
# 1. Determine filename
python3 << 'EOF'
from cortex.tools.file_naming_factory import script
filename = script("migrate", "database")
print(filename)  # → migrate-database.sh
EOF

# 2. Create file with that name
touch scripts/migrate-database.sh

# 3. Write script content (bash)
# #!/bin/bash
# ...

# 4. Make executable
chmod +x scripts/migrate-database.sh

# 5. Commit
git add scripts/migrate-database.sh
git commit -m "scripts: Add database migration script"
```

### Workflow 4: Add a New Python Module

```bash
# 1. Determine filename
python3 << 'EOF'
from cortex.tools.file_naming_factory import python_module
filename = python_module("orchestrator", "kubernetes")
print(filename)  # → kubernetes_orchestrator.py
EOF

# 2. Create file with that name
touch cortex/kubernetes_orchestrator.py

# 3. Write Python code
# """Module docstring."""
# ...

# 4. Commit
git add cortex/kubernetes_orchestrator.py
git commit -m "feat: Add Kubernetes orchestrator module"
```

---

## 🔧 Configuration Change Workflow

If you need to change file naming standards:

```bash
# 1. Update configuration
nano .cortex/standards/file-naming-config.yaml

# 2. Update governance docs (keep docs in sync)
nano cortex_brain/tier0/governance/file-naming-standards.md

# 3. If adding new file type, update factory
nano cortex/tools/file_naming_factory.py

# 4. Test changes
python3 -m cortex.tools.file_naming_factory

# 5. Commit all changes
git add .cortex/standards/file-naming-config.yaml
git add cortex_brain/tier0/governance/file-naming-standards.md
git add cortex/tools/file_naming_factory.py
git commit -m "standards: [description of changes]"

# 6. Tag for checkpoint
git tag -a "file-naming-standards-update-$(date +%Y%m%d)" \
  -m "Updated file naming standards: [description]"

# ✅ Done! All future files use new standards
```

---

## 📞 Common Questions

### Q: How do I know if my filename is compliant?
```python
from cortex.tools.file_naming_factory import validate

result = validate("my-file.md")
if result["is_valid"]:
    print("✅ Valid!")
else:
    print("Issues:", result["issues"])
    print("Suggestions:", result["suggestions"])
```

### Q: Can I use CamelCase?
No, except for Python files where snake_case is required by PEP 8.

### Q: Can I include version numbers?
No. Use git history for version tracking, not filenames.

### Q: Can I use dates in filenames?
No. Use git commit dates instead.

### Q: Can I use adjectives like "new" or "improved"?
No. They're weak and become outdated immediately. Use descriptive nouns instead.

### Q: What if my filename is too long?
Reduce it to under 55 chars. Optimal is 16-32 chars.

### Q: Can I add underscores?
Only for Python files (snake_case per PEP 8). Use hyphens for other files.

### Q: What if I have a special file type not covered?
1. Add it to the factory
2. Update configuration
3. Update governance docs
4. Commit + tag
5. All future files use new type

---

## ✅ Governance Compliance

| CORE Rule | Status | Details |
|-----------|--------|---------|
| **CORE-035** | ✅ Implemented | Single Canonical Implementation in config file |
| **CORE-030** | ✅ Verified | Implementation Truth in factory code |
| **CORE-026** | ✅ Complete | Git Checkpoint Safety (tag: global-file-naming-standards-20260127) |
| **CORE-027** | ✅ Tracked | Audit Trail (committed and tagged) |

---

## 🚀 Next Steps

### Immediate (This Week)
- [ ] Read quick start guide
- [ ] Review examples in this index
- [ ] Test factory with sample filenames

### Short Term (This Month)
- [ ] Integrate factory into your generators
- [ ] Add pre-commit validation hook
- [ ] Train team on new standards

### Medium Term (This Quarter)
- [ ] Update CI/CD to enforce standards
- [ ] Migrate legacy files (gradually, on edit)
- [ ] Document team-specific conventions

### Long Term (Ongoing)
- [ ] Annual review (Q1 2027)
- [ ] Gather feedback
- [ ] Continuous improvement

---

## 📖 Reading Guide

**Time Constraints?**

- **5 minutes:** Read `file-naming-quick-start.md`
- **20 minutes:** Add quick start + skim `file-naming-standards.md`
- **1 hour:** Read all documents + run examples
- **2 hours:** Deep dive + integrate into your code

---

## 🎓 Learning Paths

### Path 1: Quick Learner (15 min)
1. Read: `file-naming-quick-start.md`
2. Skim: `file-naming-standards.md` (just the patterns section)
3. Try: Examples in this index

### Path 2: Developer (1 hour)
1. Read: `file-naming-quick-start.md`
2. Read: `file-naming-standards.md` (full)
3. Study: `file_naming_factory.py` docstrings
4. Try: Generate several filenames
5. Review: Any edge cases

### Path 3: Architect (2 hours)
1. Read: All documentation files
2. Study: `file_naming_factory.py` implementation
3. Review: Configuration file
4. Plan: Integration into your systems
5. Implement: Pre-commit hooks, CI/CD

### Path 4: Complete Master (4+ hours)
1. Read: All documentation
2. Study: All implementation code
3. Review: Git history
4. Analyze: Architecture decisions
5. Plan: Future enhancements
6. Extend: For new file types

---

## 📊 Quick Stats

| Metric | Value |
|--------|-------|
| **Files Created** | 5 |
| **Total Lines** | 2,300+ |
| **Python Code** | 536 lines (fully typed) |
| **Documentation** | 1,200+ lines |
| **Configuration** | 224 lines |
| **Examples** | 50+ |
| **File Types Supported** | 7 |
| **Scope Prefixes** | 9 |
| **Git Commits** | 4 |
| **Git Tags** | 1 |
| **CORE Rules Applied** | 4 |

---

## 🎯 Success Criteria

You'll know it's working when:

- ✅ All new files follow consistent naming
- ✅ File purposes are clear from names
- ✅ No debates about naming conventions
- ✅ Standards enforced automatically
- ✅ Changes cascade globally
- ✅ New developers understand file organization
- ✅ Professional, consistent appearance
- ✅ Easy to find files by name
- ✅ Zero legacy naming patterns in new files

---

## 🏆 You Now Have

```
✅ Configurable standards (change in ONE file)
✅ Comprehensive documentation (600+ lines)
✅ Python implementation (fully typed)
✅ Validation & suggestions (helpful feedback)
✅ Full governance compliance (CORE-035, etc.)
✅ Git integration (versioned, reversible)
✅ Easy integration (simple API)
✅ Future-proof design (easy to extend)
✅ Complete examples (50+)
✅ Clear workflows (step-by-step)
```

---

**Status:** ✅ DEPLOYED & ACTIVE  
**Git Tag:** `global-file-naming-standards-20260127`  
**Authority:** CORTEX Master Orchestrator (CORE-035)  
**Review Cycle:** Annual (Q1 2027)  

*Start here for navigation. Jump to any section using the links above.*
