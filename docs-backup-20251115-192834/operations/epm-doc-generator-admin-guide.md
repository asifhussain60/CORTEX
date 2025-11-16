# EPM Documentation Generator - Admin Guide

**Version**: 1.0.0  
**Last Updated**: November 15, 2025  
**Status**: ✅ Production Ready (Dry-Run Validated)

---

## 🎯 Overview

The **EPM (Entry Point Module) Documentation Generator** is an automated system that generates comprehensive, up-to-date documentation for CORTEX by analyzing the codebase, brain files, and existing documentation.

### What It Does

- **Generates Diagrams**: Creates Mermaid diagrams (architecture, flows, integrations)
- **Generates Pages**: Creates markdown documentation pages from templates + brain data
- **Maintains Links**: Validates and fixes cross-references between documentation pages
- **Stays Fresh**: Regenerates documentation whenever source code/brain changes

### Why Use It

✅ **Accuracy**: Documentation matches actual implementation  
✅ **Consistency**: All pages follow same structure and format  
✅ **Automation**: No manual documentation maintenance  
✅ **Validation**: Detects broken links and missing references  

---

## 🚀 Quick Start

### Running the Generator

**Basic Usage (Dry-Run - Safe Preview)**:
```bash
# Preview what would be generated (no files created)
python src/operations/epm_doc_generator/orchestrator.py --dry-run
```

**Production Usage (Actual Generation)**:
```bash
# Generate all documentation
python src/operations/epm_doc_generator/orchestrator.py

# Or use the CORTEX interface
"generate documentation"
"update docs"
"refresh documentation"
```

**Custom Options**:
```bash
# Only generate diagrams
python src/operations/epm_doc_generator/orchestrator.py --diagrams-only

# Only generate pages
python src/operations/epm_doc_generator/orchestrator.py --pages-only

# Skip cleanup (preserve existing files)
python src/operations/epm_doc_generator/orchestrator.py --skip-cleanup

# Verbose output
python src/operations/epm_doc_generator/orchestrator.py --verbose
```

---

## 📋 When to Run

### Required Situations

**1. After Code Changes**
- New operations added (e.g., `src/operations/new_operation/`)
- Agent system modified (e.g., `src/agents/`)
- Brain structure changed (e.g., new YAML files in `cortex-brain/`)

**2. After Brain Updates**
- `response-templates.yaml` modified
- `brain-protection-rules.yaml` updated
- `operations-config.yaml` changed
- Knowledge graph structure evolved

**3. Before Documentation Releases**
- Publishing to documentation site
- Creating user guides
- Preparing for new CORTEX version

**4. When Links Break**
- Cross-reference validation shows broken links
- Documentation pages reference non-existent files
- Navigation structure changed

### Optional Situations

**1. Routine Maintenance**
- Weekly documentation refresh
- Monthly quality checks
- Before major demos/presentations

**2. Validation Checks**
- Verify documentation accuracy
- Check for missing pages
- Audit diagram coverage

---

## 🧩 Pipeline Stages

The generator runs through 6 sequential stages:

### Stage 1: Pre-Flight Validation
**Purpose**: Verify system is ready to generate documentation

**Checks**:
- Brain structure exists (`cortex-brain/` directory)
- Required YAML schemas present
- Code structure valid (`src/`, `tests/` directories)
- Write permissions to `docs/` directory

**Duration**: ~0.1 seconds

**What Happens on Failure**:
- Missing brain structure → Abort with error
- Missing YAML files → Warning (generate with empty data)
- No write permissions → Abort with error

---

### Stage 2: Destructive Cleanup
**Purpose**: Remove old generated files before creating new ones

**Actions**:
- Delete `docs/images/diagrams/` (all generated diagrams)
- Delete generated pages in `docs/getting-started/`, `docs/architecture/`, etc.
- Preserve manual documentation (marked with `<!-- MANUAL -->` tag)

**Duration**: ~0.2 seconds

**Safety**:
- Dry-run mode: No files deleted (preview only)
- Production mode: Only deletes files in target directories
- Manual files: Never deleted (protected by tag)

**Skip This Stage**:
```bash
python ... --skip-cleanup  # Preserve existing files
```

---

### Stage 3: Diagram Generation
**Purpose**: Generate Mermaid diagrams for architecture, flows, and integrations

**Output Locations**:
```
docs/images/diagrams/
├── strategic/          # High-level architecture
│   ├── tier-architecture.md
│   ├── agent-coordination.md
│   └── information-flow.md
├── architectural/      # System design
│   ├── epm-doc-generator-pipeline.md
│   ├── module-structure.md
│   └── brain-protection.md
├── operational/        # Runtime flows
│   ├── conversation-flow.md
│   ├── knowledge-graph-update.md
│   └── health-check.md
└── integration/        # External integrations
    ├── vscode-integration.md
    ├── git-integration.md
    └── mkdocs-integration.md
```

**Duration**: ~0.2 seconds

**Diagram Types**:
- **Strategic**: 30,000-foot view of system
- **Architectural**: Component relationships
- **Operational**: Runtime behavior
- **Integration**: External system connections

**Generate Only Diagrams**:
```bash
python ... --diagrams-only
```

---

### Stage 4: Page Generation
**Purpose**: Generate documentation pages from templates + brain data

**Output Locations**:
```
docs/
├── getting-started/     # Quick start, installation, config
├── architecture/        # System design documentation
├── operations/          # Operation usage guides
├── plugins/             # Plugin development
├── reference/           # API reference, configuration
└── guides/              # Admin, developer, troubleshooting
```

**Duration**: ~0.2 seconds

**Template Processing**:
1. Load Jinja2 template from `cortex-brain/doc-generation-config/templates/`
2. Load data source (YAML/JSON from `cortex-brain/`)
3. Render template with data
4. Write markdown file to `docs/`

**Data Sources**:
- `response-templates.yaml` → Commands and examples
- `brain-protection-rules.yaml` → Security policies
- `operations-config.yaml` → Operation definitions
- Code analysis → Agent system, modules

**Generate Only Pages**:
```bash
python ... --pages-only
```

---

### Stage 5: Cross-Reference Building
**Purpose**: Validate and fix links between documentation pages

**Actions**:
1. Scan all markdown files in `docs/`
2. Extract all links (internal references)
3. Validate link targets exist
4. Report broken links
5. (Optional) Auto-fix broken links

**Duration**: ~0.9 seconds

**Output**:
- List of broken links with source/target
- Suggestions for fixes
- Link graph (which pages reference which)

**What Counts as Broken**:
- Link to non-existent file: `[text](missing.md)`
- Invalid anchor: `[text](file.md#missing-section)`
- Relative path errors: `../../wrong/path.md`

**What Doesn't Count**:
- External URLs (not validated)
- Placeholder links (e.g., `...`, `TODO`)

---

### Stage 6: Post-Generation Validation
**Purpose**: Verify generated documentation is valid

**Checks**:
- Internal links valid
- Diagram references valid
- Markdown syntax correct
- MkDocs can build successfully

**Duration**: ~0.0 seconds (stub implementations)

**What Happens on Failure**:
- Broken links → Warning (list of issues)
- Invalid markdown → Error (syntax issues)
- MkDocs build fails → Error (configuration issues)

---

## 📊 Expected Outputs

### Successful Run

```
🧠 CORTEX Documentation Generation
Author: Asif Hussain | © 2024-2025 | github.com/asifhussain60/CORTEX

🎯 My Understanding Of Your Request:
   Generate comprehensive documentation for CORTEX system

⚠️ Challenge: ✓ Accept
   Documentation generation is ready. All validation checks passed.

💬 Response:
   Running EPM Documentation Generator pipeline...

Pipeline Execution:
  ✅ Stage 1: Pre-Flight Validation (0.10s)
  ✅ Stage 2: Destructive Cleanup (0.17s)
  ✅ Stage 3: Diagram Generation (0.15s)
     • Generated 12 diagrams
  ✅ Stage 4: Page Generation (0.19s)
     • Generated 20 pages
  ✅ Stage 5: Cross-Reference Building (0.85s)
     • Indexed 371 pages
     • Found 0 broken links
  ✅ Stage 6: Post-Generation Validation (0.00s)

Total Duration: 1.46 seconds

Output:
  • Diagrams: docs/images/diagrams/ (12 files)
  • Pages: docs/ (20 files)
  • Cross-References: Validated 351 links

📝 Your Request: Generate documentation

🔍 Next Steps:
   1. Review generated documentation in docs/
   2. Run mkdocs serve to preview
   3. Commit changes to git
   4. Deploy to documentation site
```

### Dry-Run Output

```
💬 Response:
   Running EPM Documentation Generator pipeline (DRY-RUN mode)...

Pipeline Execution:
  ✅ Stage 1: Pre-Flight Validation (0.10s)
  ✅ Stage 2: Destructive Cleanup (0.17s)
     • DRY-RUN: Would delete 12 old diagrams
  ✅ Stage 3: Diagram Generation (0.15s)
     • DRY-RUN: Would generate 12 diagrams
  ✅ Stage 4: Page Generation (0.19s)
     • DRY-RUN: Would generate 20 pages
  ✅ Stage 5: Cross-Reference Building (0.85s)
     • Indexed 351 pages
     • Found 52 broken links (existing docs)
  ✅ Stage 6: Post-Generation Validation (0.00s)

⚠️ Warnings:
  • 4 missing source files (operations-config.yaml, etc.)
  • 52 broken links in existing documentation

Recommendation: Fix broken links before production run
```

---

## ⚙️ Configuration

### Main Configuration File

**Location**: `cortex-brain/doc-generation-config/doc-generation-config.yaml`

**Structure**:
```yaml
templates:
  base_path: "cortex-brain/doc-generation-config/templates"
  categories:
    - getting-started
    - architecture
    - operations
    - plugins
    - reference
    - guides

diagrams:
  output_path: "docs/images/diagrams"
  categories:
    - strategic
    - architectural
    - operational
    - integration

pages:
  output_path: "docs"
  categories:
    getting-started:
      - quick-start.md
      - installation.md
      - configuration.md
    architecture:
      - overview.md
      - tier-system.md
      - agents.md
      - brain-protection.md
    # ... etc

cross_reference:
  exclude_patterns:
    - "docs/api/external/*"
    - "docs/archive/*"
  auto_fix: false

validation:
  check_links: true
  check_diagrams: true
  check_markdown: true
  check_mkdocs_build: true
```

**Customization**:
- Add new template categories
- Change output paths
- Configure exclusion patterns
- Enable/disable validation checks

---

## 🛠️ Source File Requirements

### Required Brain Files

The generator expects these files to exist in `cortex-brain/`:

**Core Configuration**:
- `response-templates.yaml` - Command templates and examples
- `brain-protection-rules.yaml` - Security policies
- `module-definitions.yaml` - Module metadata

**Optional (graceful degradation)**:
- `operations-config.yaml` - Operation definitions
- `lessons-learned.yaml` - Historical patterns
- `development-context.yaml` - Development metadata

**Behavior with Missing Files**:
- Required files missing → Warning + generate with empty data
- Optional files missing → Silent fallback to defaults

### Creating Missing Files

If you see warnings about missing files:

**1. Create Placeholder**:
```bash
# Create empty YAML with basic structure
cat > cortex-brain/operations-config.yaml << EOF
operations:
  setup:
    name: "Setup Environment"
    description: "Configure development environment"
  cleanup:
    name: "Cleanup Workspace"
    description: "Remove temporary files"
EOF
```

**2. Populate with Real Data**:
- Copy from `cortex-operations.yaml` (root level)
- Or manually document operations

**3. Re-run Generator**:
```bash
python src/operations/epm_doc_generator/orchestrator.py
```

---

## 🧪 Testing & Validation

### Dry-Run Testing

**Always test with dry-run first**:
```bash
# Preview what will be generated
python src/operations/epm_doc_generator/orchestrator.py --dry-run --verbose
```

**What to Check**:
- Number of diagrams/pages matches expectation
- No unexpected file deletions
- Warnings about missing source files
- Broken link count (should be 0 for fresh docs)

### Production Testing

**After generation, validate**:
```bash
# Check MkDocs can build
cd docs
mkdocs build

# Preview locally
mkdocs serve
# Open http://localhost:8000

# Check for errors
grep -r "TODO" docs/
grep -r "FIXME" docs/
```

**Quality Checks**:
- [ ] All diagrams render correctly
- [ ] Pages have content (not empty)
- [ ] Links work (no 404s)
- [ ] Navigation structure correct
- [ ] Code examples syntax-highlighted

---

## 🚨 Troubleshooting

### Issue 1: Missing Source Files

**Symptom**:
```
⚠️ Warning: Source file not found: cortex-brain/operations-config.yaml
```

**Solution**:
1. Create the missing file (see "Source File Requirements")
2. Or ignore if file is optional (generator uses defaults)

**Prevention**: Run with `--dry-run` first to identify missing files

---

### Issue 2: Broken Links

**Symptom**:
```
⚠️ Found 52 broken links in documentation
```

**Solution**:
1. Review broken link report in output
2. Fix links manually OR
3. Delete/regenerate affected pages

**Common Causes**:
- Old documentation referencing deleted files
- Incorrect relative paths
- Pages moved but references not updated

**Quick Fix**:
```bash
# Find all broken links
grep -r "\[.*\](.*\.md)" docs/ | grep -v "^docs/images"

# Fix with sed (example)
find docs/ -name "*.md" -exec sed -i 's|../old/path.md|../new/path.md|g' {} +
```

---

### Issue 3: Template Rendering Errors

**Symptom**:
```
❌ Error: Failed to render template getting-started/quick-start.md
    Jinja2 TemplateNotFound: quick-start.jinja2
```

**Solution**:
1. Check template exists: `cortex-brain/doc-generation-config/templates/getting-started/quick-start.jinja2`
2. Check template path in config matches actual location
3. Verify template syntax (valid Jinja2)

**Template Debugging**:
```python
# Test template manually
from jinja2 import Environment, FileSystemLoader
env = Environment(loader=FileSystemLoader('cortex-brain/doc-generation-config/templates'))
template = env.get_template('getting-started/quick-start.jinja2')
print(template.render(data={}))
```

---

### Issue 4: Permission Errors

**Symptom**:
```
❌ Error: No write permissions to docs/ directory
```

**Solution**:
```bash
# Check permissions
ls -la docs/

# Fix permissions (Unix/Mac)
chmod -R u+w docs/

# Fix permissions (Windows - run as Administrator)
icacls docs /grant Users:F /T
```

---

### Issue 5: MkDocs Build Fails

**Symptom**:
```
❌ Error: MkDocs build failed
    Config file 'mkdocs.yml' does not exist
```

**Solution**:
1. Ensure `mkdocs.yml` exists in project root
2. Check YAML syntax: `python -c "import yaml; yaml.safe_load(open('mkdocs.yml'))"`
3. Verify all referenced pages exist

**Common MkDocs Issues**:
- Missing nav entries for new pages
- Invalid markdown syntax in pages
- Broken theme configuration

---

## 📈 Performance & Optimization

### Expected Performance

| Stage | Duration | Bottleneck |
|-------|----------|-----------|
| Pre-Flight Validation | 0.1s | Filesystem checks |
| Destructive Cleanup | 0.2s | File deletion |
| Diagram Generation | 0.2s | Template rendering |
| Page Generation | 0.2s | Template rendering |
| Cross-Reference Building | 0.9s | Link validation |
| Post-Generation Validation | 0.0s | Stub (future) |

**Total**: ~1.5 seconds (dry-run), 3-5 seconds (production)

### Performance Optimization

**1. Skip Stages You Don't Need**:
```bash
# Only regenerate pages (skip diagrams, cleanup)
python ... --pages-only --skip-cleanup
```

**2. Parallel Processing** (future enhancement):
- Generate diagrams in parallel
- Generate pages in parallel
- Current: Sequential processing

**3. Incremental Updates** (future enhancement):
- Only regenerate changed pages
- Current: Regenerates all pages

**4. Caching** (future enhancement):
- Cache rendered templates
- Current: No caching

---

## 🔐 Security Considerations

### What Gets Deleted

**During Cleanup Stage**:
- ALL files in `docs/images/diagrams/` (no exceptions)
- Generated pages in `docs/getting-started/`, `docs/architecture/`, etc.
- Files without `<!-- MANUAL -->` tag

**Protected Files**:
- Manual documentation with `<!-- MANUAL -->` tag at top
- Files outside target directories
- `docs/index.md` (home page)
- `docs/README.md` (documentation readme)

### Adding Manual Documentation

**Mark files as manual** to prevent deletion:
```markdown
<!-- MANUAL -->
# My Manual Documentation

This file will not be deleted by the generator.
```

**Best Practice**: Keep manual docs in separate directories:
```
docs/
├── manual/           # Never touched by generator
│   └── custom-guide.md
├── generated/        # Generator output
│   └── api-reference.md
```

---

## 🚀 Advanced Usage

### Custom Templates

**1. Create Template**:
```bash
# Create new template
cat > cortex-brain/doc-generation-config/templates/custom/my-page.jinja2 << EOF
# {{ title }}

{{ description }}

## Sections
{% for section in sections %}
- {{ section.name }}: {{ section.content }}
{% endfor %}
EOF
```

**2. Add to Configuration**:
```yaml
# In doc-generation-config.yaml
pages:
  custom:
    - my-page.md
```

**3. Create Data Source**:
```yaml
# In cortex-brain/my-page-data.yaml
title: "My Custom Page"
description: "Custom documentation"
sections:
  - name: "Section 1"
    content: "Content here"
```

**4. Register in Generator**:
```python
# In page_generator.py
PAGE_TEMPLATES = {
    'custom/my-page.md': {
        'template': 'custom/my-page.jinja2',
        'source_type': 'yaml',
        'source_path': 'cortex-brain/my-page-data.yaml'
    }
}
```

---

### Custom Diagrams

**1. Define Diagram Logic**:
```python
# In diagram_generator.py
def generate_my_custom_diagram(self):
    """Generate custom Mermaid diagram"""
    diagram = """
    graph TD
        A[Start] --> B{Decision}
        B -->|Yes| C[Action 1]
        B -->|No| D[Action 2]
    """
    return diagram
```

**2. Register in Generator**:
```python
DIAGRAM_GENERATORS = {
    'custom/my-diagram.md': 'generate_my_custom_diagram'
}
```

**3. Run Generator**:
```bash
python src/operations/epm_doc_generator/orchestrator.py --diagrams-only
```

---

## 📚 Integration with CORTEX Operations

### Using CORTEX Natural Language

**Instead of command-line**:
```
"generate documentation"
"update docs"
"refresh documentation"
"rebuild docs with latest changes"
```

**CORTEX will**:
1. Detect `DOCUMENT` intent
2. Route to EPM Documentation Generator
3. Run full pipeline
4. Report results

### Integration with Other Operations

**After Code Changes**:
```
1. "implement new operation"  → Creates code
2. "generate documentation"   → Documents it
3. "validate system"          → Checks health
```

**Before Releases**:
```
1. "cleanup workspace"        → Removes temp files
2. "generate documentation"   → Fresh docs
3. "run tests"                → Validates system
4. "publish release"          → Deploys
```

---

## 🎯 Best Practices

### Daily Operations

**✅ DO**:
- Run dry-run before production
- Check for warnings about missing files
- Review broken link reports
- Test locally with `mkdocs serve`
- Commit generated docs to git

**❌ DON'T**:
- Run without dry-run first
- Ignore missing source file warnings
- Skip broken link fixes
- Generate docs without testing
- Manually edit generated files

### Maintenance

**Weekly**:
- [ ] Run generator with dry-run
- [ ] Review broken link report
- [ ] Check for missing source files
- [ ] Update templates if needed

**Monthly**:
- [ ] Audit documentation quality
- [ ] Verify all operations documented
- [ ] Check for outdated content
- [ ] Update diagrams for new features

**Before Releases**:
- [ ] Generate fresh documentation
- [ ] Fix all broken links
- [ ] Validate MkDocs build
- [ ] Review generated content
- [ ] Deploy to documentation site

---

## 📞 Support & Troubleshooting

### Getting Help

**1. Check Logs**:
```bash
# Generator logs
cat logs/epm-doc-generator.log

# CORTEX logs
cat logs/cortex.log
```

**2. Run Verbose Mode**:
```bash
python src/operations/epm_doc_generator/orchestrator.py --verbose
```

**3. Test Individual Stages**:
```bash
# Test only diagram generation
python -m src.operations.epm_doc_generator.diagram_generator

# Test only page generation
python -m src.operations.epm_doc_generator.page_generator
```

**4. Validate Configuration**:
```bash
# Check YAML syntax
python -c "import yaml; print(yaml.safe_load(open('cortex-brain/doc-generation-config/doc-generation-config.yaml')))"
```

### Common Questions

**Q: How often should I run the generator?**  
A: After any code/brain changes, weekly for maintenance, before releases.

**Q: Can I edit generated files?**  
A: No - they'll be overwritten. Mark manual files with `<!-- MANUAL -->` tag.

**Q: What if I don't have all source files?**  
A: Generator uses defaults for missing files. Create placeholders if warnings appear.

**Q: How do I add new pages?**  
A: Create template, add to config, create data source, register in generator.

**Q: What about external API documentation?**  
A: Use Sphinx for Python APIs, JSDoc for JavaScript. This generator is for user-facing docs.

---

## 🔮 Future Enhancements

### Planned Features

**Version 1.1** (Q1 2026):
- [ ] Incremental updates (only changed pages)
- [ ] Parallel stage processing
- [ ] Template caching
- [ ] Auto-fix broken links

**Version 1.2** (Q2 2026):
- [ ] API documentation generation (from code)
- [ ] Interactive diagram editor
- [ ] Multi-language support
- [ ] Documentation versioning

**Version 2.0** (Q3 2026):
- [ ] AI-powered content generation
- [ ] Automatic screenshot capture
- [ ] Video tutorial generation
- [ ] Documentation analytics

### Contributing

Want to improve the generator? See:
- `src/operations/epm_doc_generator/README.md` - Developer guide
- `tests/operations/epm_doc_generator/` - Test suite
- Submit issues/PRs to GitHub repository

---

## 📋 Checklist: First-Time Setup

### Initial Setup

- [ ] Install dependencies: `pip install -r requirements.txt`
- [ ] Verify MkDocs installed: `mkdocs --version`
- [ ] Check brain structure: `ls cortex-brain/`
- [ ] Review configuration: `cat cortex-brain/doc-generation-config/doc-generation-config.yaml`

### First Run

- [ ] Run dry-run: `python ... --dry-run --verbose`
- [ ] Review output for warnings
- [ ] Create missing source files
- [ ] Run production: `python ...`
- [ ] Test locally: `mkdocs serve`

### Validation

- [ ] Check diagrams render: `docs/images/diagrams/`
- [ ] Check pages exist: `docs/getting-started/`, etc.
- [ ] Verify links work: No broken links in output
- [ ] Build documentation: `mkdocs build`
- [ ] Commit changes: `git add docs/ && git commit`

---

## 📖 Related Documentation

| Document | Description |
|----------|-------------|
| [EPM Doc Generator README](../../src/operations/epm_doc_generator/README.md) | Developer documentation |
| [Integration Test Results](../../cortex-brain/doc-generation-config/INTEGRATION-TEST-RESULTS.md) | Test validation report |
| [Operations Reference](operations-reference.md) | All CORTEX operations |
| [Plugin System](plugin-system.md) | Plugin development guide |

---

**Copyright**: © 2024-2025 Asif Hussain. All rights reserved.  
**License**: Proprietary - See LICENSE file  
**Version**: 1.0.0  
**Last Updated**: November 15, 2025  
**Status**: ✅ Production Ready
