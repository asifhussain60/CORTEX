# CORTEX Admin Help - Developer Reference

**Version:** 2.1  
**Last Updated:** 2025-11-22  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Deployment Tier:** Admin Only

---

## ⚠️ Admin Operations

**WARNING:** These operations are for CORTEX developers and administrators. Regular users should use the standard help: `"help"` or `"cortex help"`

---

## 🔧 Admin Operations Reference

| Operation | Natural Language | Purpose | Status |
|-----------|------------------|---------|--------|
| **Publish CORTEX** | "publish cortex", "deploy cortex to github" | Package and deploy CORTEX to GitHub repository | ✅ Ready |
| **Design Sync** | "sync design", "update design docs" | Synchronize design documents with implementation | ✅ Ready |
| **Regenerate Diagrams** | "regenerate diagrams", "update architecture diagrams" | Rebuild Mermaid diagrams from YAML definitions | ✅ Ready |
| **Enterprise Docs** | "generate documentation", "generate enterprise docs" | Build comprehensive enterprise documentation | ✅ Ready |
| **Brain Export** | "export brain", "share brain patterns" | Export learned patterns for team sharing | ✅ Ready |
| **Brain Import** | "import brain", "load patterns from export" | Import shared brain patterns from team | ✅ Ready |
| **Admin Help** | "admin help", "cortex admin help" | Show this admin reference | ✅ Ready |

---

## 📦 Publish CORTEX Operation

**Purpose:** Package and deploy CORTEX to GitHub repository

**Usage:**
```
"publish cortex"
"deploy cortex to github"
"publish cortex to repository"
```

**What It Does:**
1. ✅ Validates all CORTEX files
2. ✅ Packages entry points (.github/prompts/)
3. ✅ Creates SETUP-FOR-COPILOT.md
4. ✅ Generates README with latest capabilities
5. ✅ Commits to CORTEX-3.0 branch
6. ✅ Optional: Pushes to GitHub

**Output Location:** `publish/CORTEX/`

**Files Generated:**
```
publish/CORTEX/
  .github/
    prompts/
      CORTEX.prompt.md           # Main entry point
      copilot-instructions.md    # GitHub Copilot loader
      shared/                    # Shared modules
  SETUP-FOR-COPILOT.md          # User setup guide
  README.md                      # Overview
```

**Safety:**
- Creates local commit before push
- Validates files before packaging
- Backup created automatically

---

## 📐 Design Sync Operation

**Purpose:** Synchronize design documents with implementation

**Usage:**
```
"sync design"
"update design docs"
"synchronize design with code"
```

**What It Does:**
1. ✅ Scans implementation files for module status
2. ✅ Updates module-definitions.yaml with completion percentages
3. ✅ Refreshes architecture diagrams
4. ✅ Generates design-implementation alignment report

**Output:**
- Updated: `cortex-brain/module-definitions.yaml`
- Report: `cortex-brain/documents/analysis/design-sync-report.md`

**Checks:**
- Module implementation status (implemented/pending)
- Test coverage for completed modules
- Documentation completeness
- Dependency resolution

---

## 🖼️ Regenerate Diagrams Operation

**Purpose:** Rebuild Mermaid diagrams from YAML definitions

**Profiles:**
- **Quick** - Architecture diagrams only
- **Standard** - Architecture + workflow diagrams (DEFAULT)
- **Comprehensive** - All diagrams + validation

**Usage:**
```
"regenerate diagrams"                   # Standard profile
"update architecture diagrams"          # Standard profile
"comprehensive diagram regeneration"    # Full rebuild
```

**What It Does:**
1. ✅ Reads centralized diagram definitions:
   - `cortex-brain/documents/diagrams/architecture-diagrams.yaml`
   - `cortex-brain/documents/diagrams/workflow-diagrams.yaml`
2. ✅ Generates Mermaid `.mmd` files
3. ✅ Validates Mermaid syntax
4. ✅ Updates MkDocs references
5. ✅ Generates preview images (if Mermaid CLI installed)

**Output Location:** `docs/diagrams/`

**Diagrams Generated:**
- System architecture
- Module dependencies
- Operation workflows
- Brain tier structure
- EPM orchestration flows

---

## 📚 Enterprise Documentation Generation

**Purpose:** Build comprehensive enterprise-grade documentation

**Components:**
1. **Mermaid Diagrams** - Architecture and workflows
2. **Executive Summary** - High-level project overview
3. **Feature Documentation** - Complete feature list
4. **MkDocs Site** - Static documentation website
5. **GitHub Pages Deployment** - Publish documentation

**Usage:**
```
"generate documentation"                # Full pipeline
"generate enterprise docs"              # Full pipeline
"refresh docs"                          # Regenerate all

# Individual components:
"generate diagrams"                     # Diagrams only
"generate executive summary"            # Summary only
"generate feature list"                 # Features only
"generate mkdocs"                       # MkDocs config only
"publish docs"                          # Build and publish to GitHub Pages
```

**Full Pipeline Process:**
1. **Diagrams** (2 min)
   - Read centralized YAML definitions
   - Generate Mermaid files
   - Validate syntax
   
2. **Executive Summary** (1 min)
   - Extract project metrics
   - Compile capabilities matrix
   - Generate status overview
   
3. **Feature Documentation** (2 min)
   - Extract from cortex-operations.yaml
   - Document module capabilities
   - Cross-reference operations
   
4. **MkDocs Site** (1 min)
   - Generate mkdocs.yml navigation
   - Create index pages
   - Build cross-references
   
5. **GitHub Pages** (Optional, 2 min)
   - Build static site (`mkdocs build`)
   - Commit to gh-pages branch
   - Push to GitHub

**Total Time:** 6-8 minutes for full pipeline

**Output Locations:**
- Diagrams: `docs/diagrams/`
- Executive Summary: `docs/EXECUTIVE-SUMMARY.md`
- Features: `docs/FEATURES.md`
- MkDocs config: `mkdocs.yml`
- Built site: `site/`

---

## 🧠 Brain Export/Import Operations

### Brain Export

**Purpose:** Export learned patterns for team knowledge sharing

**Usage:**
```
"export brain"                          # Export all patterns
"brain export"                          # Export all patterns
"export brain --scope=workspace"        # Current project only
```

**What Gets Exported:**
- ✅ Learned patterns (workflows, tech stacks, solutions)
- ✅ Pattern confidence scores (0.0-1.0)
- ✅ Metadata (source machine, CORTEX version, namespaces)
- ✅ Integrity signature for validation

**What Stays Local:**
- ❌ Conversation history (private)
- ❌ Machine-specific configurations
- ❌ Database connections and credentials

**Output:** `cortex-brain/exports/brain-export-YYYYMMDD_HHMMSS.yaml`

**Workflow:**
1. Run export command
2. Review export file
3. Commit to git: `git add cortex-brain/exports/ && git commit -m "Brain export"`
4. Share via git push or direct file transfer

---

### Brain Import

**Purpose:** Import shared brain patterns from team exports

**Merge Strategies:**
- **Auto** (Recommended) - Intelligent merge (higher confidence wins)
- **Replace** - Import wins (use when importing from expert)
- **Keep Local** - Your patterns win (use when testing)

**Usage:**
```
# Preview import (no changes)
"import brain --file=brain-export-20251122_040727.yaml --dry-run"

# Import with auto-merge
"import brain --file=brain-export-20251122_040727.yaml --strategy=auto"

# Import from senior developer (replace local)
"import brain --file=brain-export-20251122_040727.yaml --strategy=replace"
```

**Workflow:**
1. Obtain export file (git pull or copy to `cortex-brain/exports/`)
2. Run dry-run preview
3. Review conflicts and new patterns
4. Choose merge strategy
5. Execute import
6. Verify patterns in database

**Safety:**
- Dry-run shows changes before applying
- Backup created automatically
- Version compatibility validation
- Integrity signature verification

---

## 🧪 Testing & Validation

### Run Admin Tests
```powershell
# All admin operation tests
pytest tests/admin/ -v

# Specific operation tests
pytest tests/admin/test_publish_operation.py -v
pytest tests/admin/test_design_sync.py -v
pytest tests/admin/test_diagram_generation.py -v
```

### Validate Documentation
```powershell
# Check MkDocs build
mkdocs build --strict

# Validate Mermaid diagrams
mmdc --version  # Ensure mermaid-cli installed
python scripts/validate_diagrams.py
```

### Health Check
```powershell
# Admin health check
pytest tests/admin/test_admin_health.py -v

# Full system health
python scripts/health_check.py --admin
```

---

## 📊 Admin Metrics

### Performance Targets
| Component | Target | Current |
|-----------|--------|---------|
| Publish Time | <5 min | 3.2 min |
| Design Sync | <2 min | 1.5 min |
| Diagram Generation | <3 min | 2.1 min |
| Enterprise Docs | <8 min | 6.4 min |
| Brain Export | <1 min | 0.3 min |
| Brain Import | <2 min | 1.1 min |

### Success Rates
| Operation | Success Rate | Target |
|-----------|--------------|--------|
| Publish | 100% | >99% |
| Design Sync | 100% | >95% |
| Diagram Generation | 98% | >95% |
| Enterprise Docs | 96% | >90% |
| Brain Export/Import | 100% | >99% |

---

## 🔍 Troubleshooting

### Publish Fails
```powershell
# Check git status
git status

# Validate files
python scripts/validate_cortex_files.py

# Manual publish
python src/operations/publish_cortex_operation.py
```

### Diagram Generation Fails
```powershell
# Validate YAML definitions
yamllint cortex-brain/documents/diagrams/*.yaml

# Check Mermaid syntax
mmdc -i docs/diagrams/architecture.mmd -o /dev/null

# Manual regeneration
python scripts/generate_diagrams.py
```

### Brain Export/Import Issues
```powershell
# Check Tier 2 database
sqlite3 cortex-brain/tier2-knowledge-graph.db "SELECT COUNT(*) FROM patterns;"

# Validate export file
python scripts/validate_brain_export.py brain-export-*.yaml

# Check import conflicts
python scripts/brain_transfer_cli.py import brain --file=export.yaml --dry-run
```

---

## 🎓 Admin Best Practices

### Publishing
1. ✅ Run full test suite before publish: `pytest`
2. ✅ Validate documentation: `mkdocs build --strict`
3. ✅ Review changelog: Update `CHANGELOG.md`
4. ✅ Commit before publish: Create checkpoint
5. ✅ Tag releases: `git tag v2.1.0`

### Design Sync
1. ✅ Run after major implementation changes
2. ✅ Validate module status accuracy
3. ✅ Update diagrams if architecture changed
4. ✅ Review alignment report

### Documentation Generation
1. ✅ Use full pipeline for releases
2. ✅ Validate all diagrams render correctly
3. ✅ Test GitHub Pages deployment locally
4. ✅ Review cross-references for accuracy

### Brain Export/Import
1. ✅ Export regularly for backup (weekly)
2. ✅ Use meaningful export names: `brain-export-feature-x-complete.yaml`
3. ✅ Document export content in README
4. ✅ Always dry-run imports before applying
5. ✅ Use auto-merge strategy for team collaboration

---

## 📚 Additional Admin Resources

**Configuration Files:**
- `cortex-operations.yaml` - Operations registry (2278 lines)
- `cortex-brain/module-definitions.yaml` - Module inventory (75 modules)
- `cortex-brain/capabilities.yaml` - Capability assessment matrix
- `cortex-brain/response-templates.yaml` - Response template system
- `cortex-brain/brain-protection-rules.yaml` - SKULL governance rules

**Admin Scripts:**
- `scripts/publish_cortex.py` - Manual publish
- `scripts/generate_diagrams.py` - Manual diagram generation
- `scripts/brain_transfer_cli.py` - Brain export/import CLI
- `scripts/health_check.py` - System diagnostics
- `scripts/validate_cortex_files.py` - File validation

**Admin Documentation:**
- `cortex-brain/documents/admin/` - Admin guides
- `cortex-brain/documents/implementation-guides/` - Implementation references
- `cortex-brain/documents/analysis/` - System analysis reports

---

## 🔐 Security Considerations

### Access Control
- Admin operations require direct file system access
- GitHub push requires repository permissions
- Brain exports may contain proprietary patterns
- Review export content before sharing externally

### Data Protection
- Brain exports include learned patterns (may contain sensitive info)
- Validate import sources (check integrity signature)
- Use encrypted channels for brain transfer
- Audit imported patterns before merging

---

**Version:** 2.1  
**Last Updated:** 2025-11-22  
**Deployment Tier:** Admin Only
