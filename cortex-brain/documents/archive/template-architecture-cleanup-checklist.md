# Template Architecture Cleanup Checklist (Phase 6)

**Purpose:** Comprehensive checklist for Phase 6: Cleanup and Alignment after template architecture refactoring  
**Version:** 1.0  
**Date:** 2025-11-27  
**Estimated Time:** 4-6 hours  
**Risk Level:** LOW (all functionality validated in Phases 1-5)

---

## 📋 Pre-Cleanup Preparation

### Backup & Safety

- [ ] **Create rollback git tag:** `git tag -a template-architecture-v1 -m "Pre-refactoring baseline"`
- [ ] **Push tag to remote:** `git push origin template-architecture-v1`
- [ ] **Backup brain databases:**
  - [ ] `cp cortex-brain/tier1-working-memory.db cortex-brain/tier1-working-memory.db.backup`
  - [ ] `cp cortex-brain/tier2-knowledge-graph.db cortex-brain/tier2-knowledge-graph.db.backup`
  - [ ] `cp cortex-brain/tier3-development-context.db cortex-brain/tier3-development-context.db.backup`
- [ ] **Backup response templates:** `cp cortex-brain/response-templates.yaml cortex-brain/response-templates.yaml.backup`
- [ ] **Document current state:**
  - [ ] Run `git status` and save output
  - [ ] Run `align report` and save results
  - [ ] Run full test suite and save results (baseline)

### Environment Validation

- [ ] **Verify test suite passes:** `pytest tests/ -v` (100% pass required)
- [ ] **Check system alignment:** `align report` (score should be >80%)
- [ ] **Verify no uncommitted changes:** `git status` (clean working tree)
- [ ] **Check disk space:** Ensure >500MB free for archives
- [ ] **Verify Python environment:** `python --version` (3.10+ required)

---

## 🗂️ Section 1: Template File Cleanup (30 min)

### Identify Deprecated Files

- [ ] **List all template YAML files:**
  ```bash
  find cortex-brain -name "*template*.yaml" -o -name "*template*.yml"
  ```
- [ ] **Identify deprecated files:**
  - [ ] `response-templates-enhanced.yaml` (old version)
  - [ ] `response-templates-condensed.yaml` (old version)
  - [ ] Any `response-templates-*.yaml` variants
  - [ ] Temporary migration files (if created)

### Create Archive Directory

- [ ] **Create archive structure:**
  ```bash
  mkdir -p cortex-brain/archives/template-v1/original
  mkdir -p cortex-brain/archives/template-v1/backups
  mkdir -p cortex-brain/archives/template-v1/documentation
  ```
- [ ] **Add README to archive:**
  ```bash
  cat > cortex-brain/archives/template-v1/README.md << 'EOF'
  # Template Architecture v1 Archive
  
  **Archived:** 2025-11-27
  **Reason:** Template architecture refactoring (v1 → v2)
  **Rollback Tag:** template-architecture-v1
  
  ## Contents
  - original/ - Original template files before refactoring
  - backups/ - Database and config backups
  - documentation/ - Old documentation snapshots
  
  ## Restoration
  To restore: `git checkout template-architecture-v1`
  EOF
  ```

### Move Deprecated Files

- [ ] **Move old template files:**
  ```bash
  mv cortex-brain/response-templates-enhanced.yaml cortex-brain/archives/template-v1/original/
  mv cortex-brain/response-templates-condensed.yaml cortex-brain/archives/template-v1/original/
  ```
- [ ] **Move backup file:** `mv cortex-brain/response-templates.yaml.backup cortex-brain/archives/template-v1/backups/`
- [ ] **Verify single source of truth:** Only `cortex-brain/response-templates.yaml` should exist

### Update File References

- [ ] **Search for old file references:**
  ```bash
  grep -r "response-templates-enhanced" . --exclude-dir=archives
  grep -r "response-templates-condensed" . --exclude-dir=archives
  ```
- [ ] **Update all found references** to use `response-templates.yaml`

---

## 📚 Section 2: Documentation Synchronization (45 min)

### Update Template Guide

- [ ] **Open:** `.github/prompts/modules/template-guide.md`
- [ ] **Update sections:**
  - [ ] Add "Template Inheritance" section with YAML anchor examples
  - [ ] Add "Component Library" section with reusable components
  - [ ] Add "Base Template Structure" section
  - [ ] Update examples to show inheritance vs duplication
  - [ ] Add "Creating New Templates" guide using new architecture

### Update Header Format Documentation

- [ ] **Update template-guide.md with new header format:**
  - [ ] Document enhanced header structure with `---` separators
  - [ ] Include rendering examples showing visual horizontal lines
  - [ ] Document Git Pages link usage: `https://asifhussain60.github.io/CORTEX/`
  - [ ] Explain `---` vs `<hr>` rendering (both create visual lines)
  - [ ] Show component-based header reference: `*header_standard`
  - [ ] Add cross-platform rendering compatibility notes
  - [ ] Include "before/after" comparison showing GitHub URL → Git Pages URL change

- [ ] **Update CORTEX.prompt.md with new header:**
  - [ ] Update "MANDATORY RESPONSE FORMAT" section with new header
  - [ ] Update all example responses to show new header format
  - [ ] Remove references to old `**GitHub:**` format
  - [ ] Add Git Pages link in all template examples
  - [ ] Verify horizontal line rendering explanation clear

- [ ] **Update architecture review doc:**
  - [ ] Mark Phase 2 header specifications as "as-built"
  - [ ] Document final rendering decisions (`---` markdown chosen)
  - [ ] Include Git Pages URL discovery process
  - [ ] Add header rendering test results when available

### Update Main Prompt

- [ ] **Open:** `.github/prompts/CORTEX.prompt.md`
- [ ] **Update template system section:**
  - [ ] Add inheritance model explanation
  - [ ] Update example templates to show new structure
  - [ ] Add component composition examples
  - [ ] Update "Template Selection Priority" with new logic

### Update Module Guides

- [ ] **Check all module guides** for template references:
  ```bash
  grep -l "response.*template" .github/prompts/modules/*.md
  ```
- [ ] **Update each guide:**
  - [ ] `planning-orchestrator-guide.md` - Update template examples
  - [ ] `tdd-mastery-guide.md` - Update response format references
  - [ ] `hands-on-tutorial-guide.md` - Update template interaction examples
  - [ ] `response-format.md` - Add inheritance section
  - [ ] `system-alignment-guide.md` - Update template validation rules

### Create Migration Guide

- [ ] **Create:** `.github/prompts/modules/template-architecture-v2-migration.md`
- [ ] **Include:**
  - [ ] Overview of changes (v1 → v2)
  - [ ] Base template inheritance examples
  - [ ] Component library usage guide
  - [ ] How to create new templates with new architecture
  - [ ] Comparison: old vs new template syntax
  - [ ] Troubleshooting common issues

### Add Architecture Diagrams

- [ ] **Create:** `cortex-brain/documents/architecture/template-inheritance-diagram.md`
- [ ] **Include:**
  - [ ] Inheritance hierarchy visualization
  - [ ] Component composition flow
  - [ ] Rendering pipeline diagram
  - [ ] Before/after comparison

---

## 🧪 Section 3: Test Suite Alignment (30 min)

### Update Template Loader Tests

- [ ] **File:** `tests/test_response_template_loader.py` (or equivalent)
- [ ] **Updates needed:**
  - [ ] Add test for inheritance resolution
  - [ ] Add test for component rendering
  - [ ] Add test for YAML anchor expansion
  - [ ] Update existing tests for new template structure
  - [ ] Add backward compatibility tests (if applicable)

### Add Component Library Tests

- [ ] **Create:** `tests/test_template_components.py`
- [ ] **Add tests:**
  - [ ] Test component loading
  - [ ] Test component composition
  - [ ] Test component validation
  - [ ] Test component reuse across templates

### Update Intent Router Tests

- [ ] **File:** `tests/test_intent_router.py` (or equivalent)
- [ ] **Updates needed:**
  - [ ] Update auto-routing tests for new trigger system
  - [ ] Remove tests for deprecated routing section
  - [ ] Add tests for dynamic route building
  - [ ] Verify all 18 templates route correctly

### Update Integration Tests

- [ ] **Update:** End-to-end tests using templates
- [ ] **Verify:**
  - [ ] Help command renders correctly
  - [ ] Planning workflow uses new templates
  - [ ] TDD workflow responses formatted correctly
  - [ ] Admin operations render with inheritance

### Run Full Test Suite

- [ ] **Execute:** `pytest tests/ -v --cov=src`
- [ ] **Verify:**
  - [ ] 100% pass rate (no failures)
  - [ ] Coverage maintained or improved
  - [ ] No performance regressions (<500ms template load)

---

## ⚙️ Section 4: Configuration Alignment (20 min)

### Update CORTEX Config

- [ ] **File:** `cortex.config.json`
- [ ] **Check for:**
  - [ ] Template path references (update if hardcoded)
  - [ ] Template cache settings
  - [ ] Template validation rules
- [ ] **Update:** Any deprecated references

### Update Capabilities

- [ ] **File:** `cortex-brain/capabilities.yaml`
- [ ] **Updates:**
  - [ ] Update template system description
  - [ ] Add inheritance capabilities
  - [ ] Add component library features
  - [ ] Update version references

### Update Operations Config

- [ ] **File:** `cortex-brain/operations-config.yaml`
- [ ] **Updates:**
  - [ ] Remove old routing configuration
  - [ ] Update template references
  - [ ] Add new template features to available operations

### Update MkDocs Config

- [ ] **File:** `mkdocs.yml`
- [ ] **Updates:**
  - [ ] Add new template architecture docs to nav
  - [ ] Update template guide links
  - [ ] Add migration guide to docs
  - [ ] Remove old template file references

### Update Deployment Scripts

- [ ] **Check:** `scripts/deploy*.py` or similar
- [ ] **Update:**
  - [ ] Template file paths
  - [ ] Validation checks for new structure
  - [ ] Deployment verification steps

---

## 💾 Section 5: Database & Storage Cleanup (20 min)

### Archive Old Metrics

- [ ] **Query template usage metrics:**
  ```sql
  SELECT * FROM template_usage WHERE timestamp < '2025-11-27';
  ```
- [ ] **Export to archive:**
  ```bash
  sqlite3 cortex-brain/tier3-development-context.db ".dump template_usage" > cortex-brain/archives/template-v1/backups/template_usage_pre_refactoring.sql
  ```
- [ ] **Optional:** Clear old metrics if not needed

### Update Schema References

- [ ] **Check:** `cortex-brain/schema.sql`
- [ ] **Update:**
  - [ ] Template table structure (if changed)
  - [ ] Add template_inheritance table (if tracking)
  - [ ] Update template_components table (if new)

### Clean Cached Data

- [ ] **Clear template cache:**
  ```bash
  find cortex-brain/cache -name "*template*" -type f -delete
  ```
- [ ] **Verify cache regenerates:** Test template loading

### Update Development Context

- [ ] **File:** `cortex-brain/tier3-development-context.db`
- [ ] **Updates:**
  - [ ] Record new template patterns learned
  - [ ] Update template best practices
  - [ ] Archive old template usage patterns

---

## 💻 Section 6: Code Alignment (45 min)

### Update Orchestrators

- [ ] **Scan for template usage:**
  ```bash
  grep -r "get_template\|load_template\|template_name" src/orchestrators/
  ```
- [ ] **Update each orchestrator:**
  - [ ] Planning orchestrator (template names unchanged?)
  - [ ] TDD orchestrator (response format correct?)
  - [ ] Feedback orchestrator (template references valid?)
  - [ ] Admin orchestrators (admin-specific templates working?)

### Update Response Template Loader

- [ ] **File:** `src/response_templates/template_loader.py` (or equivalent)
- [ ] **Add features:**
  - [ ] YAML anchor resolution
  - [ ] Component composition logic
  - [ ] Inheritance chain resolution
  - [ ] Backward compatibility (if needed)
- [ ] **Add deprecation warnings:**
  ```python
  if old_template_format_detected:
      logger.warning(f"Template '{name}' uses deprecated format. Migrate to v2.")
  ```

### Update Intent Router

- [ ] **File:** `src/cortex_agents/intent_router.py` (or equivalent)
- [ ] **Updates:**
  - [ ] Remove routing section parsing
  - [ ] Add auto-routing builder
  - [ ] Update template selection logic
  - [ ] Add validation for new trigger format

### Update Agents

- [ ] **Scan agent usage:**
  ```bash
  grep -r "template\|response_type" src/cortex_agents/
  ```
- [ ] **Update agents:**
  - [ ] Replace hardcoded template names with constants
  - [ ] Update response formatting calls
  - [ ] Add validation for template compatibility

### Add Constants Module

- [ ] **Create:** `src/response_templates/template_constants.py`
- [ ] **Add:**
  ```python
  # Template names (prevent typos)
  TEMPLATE_HELP_TABLE = "help_table"
  TEMPLATE_WORK_PLANNER = "work_planner_success"
  TEMPLATE_ADO_CREATED = "ado_created"
  # ... all 18 templates
  
  # Base templates
  BASE_STANDARD_5_PART = "standard_5_part"
  BASE_ADMIN_OPERATION = "admin_operation"
  BASE_INTERACTIVE_GUIDE = "interactive_guide"
  ```
- [ ] **Update all code** to use constants

---

## ✅ Section 7: Validation & Verification (60 min)

### Full Test Suite

- [ ] **Run:** `pytest tests/ -v --cov=src --cov-report=html`
- [ ] **Verify:**
  - [ ] 0 failures
  - [ ] 0 errors
  - [ ] 0 skipped (unless intentional)
  - [ ] Coverage >80% (target: 85%+)
- [ ] **Review coverage report:** Open `htmlcov/index.html`
- [ ] **Fix any gaps** in test coverage

### Template Rendering Validation

- [ ] **Test all 18 templates individually:**
  ```python
  for template_name in TEMPLATE_NAMES:
      result = loader.render_template(template_name, context)
      assert result is not None
      assert len(result) > 0
      assert "# 🧠 CORTEX" in result  # Header present
  ```
- [ ] **Compare output:** Old vs new should be identical (or intentionally different)
- [ ] **Verify formatting:** All sections present (Understanding, Challenge, Response, Request, Next Steps)

### Enhanced Header Rendering Validation

- [ ] **Markdown Rendering Tests:**
  - [ ] Verify `---` renders as horizontal line in GitHub markdown
  - [ ] Verify `---` renders as horizontal line in MkDocs output
  - [ ] Verify `---` renders as horizontal line in VS Code preview
  - [ ] Test in web browsers (Chrome, Firefox, Safari, Edge)
  - [ ] Verify `---` does NOT show as visible text (renders as visual line)

- [ ] **Header Structure Tests:**
  - [ ] Verify title uses standard `#` markdown (H1 heading)
  - [ ] Verify brain icon `🧠` renders consistently across platforms
  - [ ] Verify title format: `# 🧠 CORTEX {operation}` (with operation substitution)
  - [ ] Verify author line format: `**Author:** Asif Hussain | **Git Pages:** [link]`
  - [ ] Verify NO `<hr>` HTML tags visible in output
  - [ ] Verify NO old `**GitHub:**` format remaining

- [ ] **Git Pages Link Validation:**
  - [ ] Verify Git Pages link is present in all 18 templates
  - [ ] Verify Git Pages URL is correct: `https://asifhussain60.github.io/CORTEX/`
  - [ ] Test link navigation (click-through to documentation)
  - [ ] Verify link opens in browser successfully
  - [ ] Verify link points to production documentation (not staging/dev)
  - [ ] Test link accessibility (no 404 errors)

- [ ] **Cross-Platform Consistency:**
  - [ ] Visual inspection: Headers look identical across all 18 templates
  - [ ] Visual inspection: Horizontal lines render consistently
  - [ ] Visual inspection: Spacing and alignment correct
  - [ ] Test in email clients (if responses sent via email)
  - [ ] Test in Slack/Teams (if responses posted to chat)
  - [ ] Verify mobile rendering (if applicable)

- [ ] **Automated Header Tests:**
  ```python
  def test_header_format():
      for template_name in TEMPLATE_NAMES:
          result = loader.render_template(template_name, {"operation": "Test"})
          # Verify separator at start
          assert result.startswith("---\n")
          # Verify title format
          assert "# 🧠 CORTEX Test" in result
          # Verify author line with Git Pages
          assert "**Author:** Asif Hussain" in result
          assert "**Git Pages:** https://asifhussain60.github.io/CORTEX/" in result
          # Verify separator after author
          assert "---\n" in result.split("\n")[4]  # Line after author
          # Verify NO old GitHub format
          assert "**GitHub:**" not in result
          assert "github.com/asifhussain60/CORTEX" not in result
  ```
- [ ] **Run automated header tests:** `pytest tests/test_header_format.py -v`
- [ ] **Verify 0 failures:** All header assertions pass

### Entry Point Testing

- [ ] **Test help command:**
  ```bash
  echo "help" | python -m src.main
  ```
- [ ] **Test planning:**
  ```bash
  echo "plan authentication" | python -m src.main
  ```
- [ ] **Test feedback:**
  ```bash
  echo "feedback" | python -m src.main
  ```
- [ ] **Test admin (if in CORTEX repo):**
  ```bash
  echo "admin help" | python -m src.main
  ```

### Performance Testing

- [ ] **Benchmark template loading:**
  ```python
  import time
  start = time.time()
  for _ in range(100):
      loader.load_all_templates()
  elapsed = time.time() - start
  print(f"100 loads: {elapsed:.2f}s (avg: {elapsed*10:.1f}ms)")
  # Target: <500ms per load
  ```
- [ ] **Verify no regression:** Compare with baseline metrics
- [ ] **Check memory usage:** Should not increase significantly

### System Alignment Check

- [ ] **Run:** `python -m src.orchestrators.system_alignment_orchestrator`
- [ ] **Verify score:** >90% required
- [ ] **Check categories:**
  - [ ] Template system: 100% (fully integrated)
  - [ ] Documentation: 100% (all guides updated)
  - [ ] Testing: 100% (all tests passing)
  - [ ] Wiring: 100% (all entry points working)

### Documentation Link Validation

- [ ] **Check all links:**
  ```bash
  find .github/prompts -name "*.md" -exec grep -H "file:" {} \; | grep -v "^#"
  ```
- [ ] **Verify each link:** File exists and path is correct
- [ ] **Update broken links:** Fix any dead references

### User Acceptance Testing

- [ ] **Manual smoke tests:**
  - [ ] Open GitHub Copilot Chat
  - [ ] Say "help" → Should show help table
  - [ ] Say "plan authentication" → Should start planning workflow
  - [ ] Say "tutorial" → Should show tutorial options
  - [ ] Say "admin help" (if CORTEX repo) → Should show admin operations
- [ ] **Verify output quality:**
  - [ ] Formatting correct
  - [ ] No missing sections
  - [ ] Icons display properly
  - [ ] Next steps formatted appropriately

---

## 📦 Section 8: Archive and Finalization (20 min)

### Create Final Archive

- [ ] **Copy documentation to archive:**
  ```bash
  cp .github/prompts/modules/template-guide.md cortex-brain/archives/template-v1/documentation/template-guide-v1.md
  cp cortex-brain/response-templates.yaml cortex-brain/archives/template-v1/original/response-templates-v1.yaml
  ```
- [ ] **Create archive manifest:**
  ```bash
  cat > cortex-brain/archives/template-v1/MANIFEST.md << 'EOF'
  # Template Architecture v1 Archive Manifest
  
  ## Files Archived
  - original/response-templates-v1.yaml (2,278 lines)
  - original/response-templates-enhanced.yaml
  - original/response-templates-condensed.yaml
  - backups/*.db.backup (database backups)
  - documentation/template-guide-v1.md
  
  ## Restoration Instructions
  1. Checkout tag: `git checkout template-architecture-v1`
  2. Restore databases: `cp backups/*.db.backup cortex-brain/`
  3. Run tests: `pytest tests/`
  
  ## Reason for Archive
  Template architecture refactored to v2 with inheritance model.
  EOF
  ```

### Update VERSION File

- [ ] **File:** `VERSION`
- [ ] **Add notes:**
  ```
  3.2.0 - Template Architecture v2
  
  BREAKING CHANGES:
  - Template inheritance model introduced
  - Component library for reusable elements
  - Auto-routing replaces manual routing section
  - Metadata-driven rendering engine
  
  MIGRATION:
  - See .github/prompts/modules/template-architecture-v2-migration.md
  - Backward compatible: Old template names still work
  - Deprecated: response-templates-*.yaml variants
  
  ROLLBACK:
  - Git tag: template-architecture-v1
  - Archive: cortex-brain/archives/template-v1/
  ```

### Create Rollback Plan Document

- [ ] **Create:** `cortex-brain/archives/template-v1/ROLLBACK-PLAN.md`
- [ ] **Include:**
  ```markdown
  # Template Architecture v2 Rollback Plan
  
  ## When to Rollback
  - Critical bug in new template system
  - Performance regression >50%
  - Test failures that cannot be fixed within 2 hours
  
  ## Rollback Steps
  1. **Git revert:** `git reset --hard template-architecture-v1`
  2. **Restore databases:**
     ```bash
     cp cortex-brain/archives/template-v1/backups/*.db.backup cortex-brain/
     ```
  3. **Restore config:**
     ```bash
     git checkout template-architecture-v1 -- cortex.config.json
     ```
  4. **Run tests:** `pytest tests/ -v` (verify 100% pass)
  5. **Clear cache:** `rm -rf cortex-brain/cache/*`
  6. **Restart:** Fresh Python interpreter
  
  ## Post-Rollback
  - Document issue in GitHub Issues
  - Tag commit with issue reference
  - Plan fixes for next attempt
  
  ## Rollback Contact
  - Primary: Asif Hussain
  - Backup: Check cortex-brain/archives/template-v1/README.md
  ```

### Tag Release

- [ ] **Create release tag:**
  ```bash
  git add .
  git commit -m "Template architecture v2: Inheritance model, component library, auto-routing"
  git tag -a template-architecture-v2 -m "Template architecture refactoring complete"
  git push origin CORTEX-3.0
  git push origin template-architecture-v2
  ```

### Update Changelog

- [ ] **File:** `CHANGELOG.md` (or create if missing)
- [ ] **Add entry:**
  ```markdown
  ## [3.2.0] - 2025-11-27
  
  ### Changed - Template Architecture v2
  - **Template Inheritance:** Base templates with YAML anchors (74% code reduction)
  - **Component Library:** Reusable headers, sections, footers
  - **Auto-Routing:** Dynamic route building from triggers (300 lines removed)
  - **Metadata Renderer:** Metadata-driven template rendering
  
  ### Removed
  - Deprecated: response-templates-enhanced.yaml
  - Deprecated: response-templates-condensed.yaml
  - Removed: Manual routing section from YAML
  
  ### Migration
  - See: .github/prompts/modules/template-architecture-v2-migration.md
  - Backward compatible: Old template names still work
  
  ### Rollback
  - Tag: template-architecture-v1
  - Archive: cortex-brain/archives/template-v1/
  ```

---

## 🎉 Final Checklist

### Pre-Deployment

- [ ] **All sections complete** (1-8 above)
- [ ] **100% test pass rate**
- [ ] **System alignment >90%**
- [ ] **No broken documentation links**
- [ ] **Performance maintained** (no >10% regression)
- [ ] **Rollback plan documented**
- [ ] **Archive complete and verified**

### Deployment

- [ ] **Create deployment tag:** `template-architecture-v2-deployed`
- [ ] **Notify team:** Send deployment summary
- [ ] **Monitor:** Check production logs for 24 hours
- [ ] **Celebrate:** Template architecture v2 is live! 🎉

### Post-Deployment

- [ ] **Monitor GitHub Copilot Chat** for template rendering issues
- [ ] **Collect user feedback** on new template system
- [ ] **Track performance metrics** (template load time, memory usage)
- [ ] **Document lessons learned** in `cortex-brain/documents/lessons-learned/template-v2-deployment.md`

---

## 📊 Success Metrics

### Required (Must Pass)

- ✅ **Test Pass Rate:** 100% (0 failures)
- ✅ **System Alignment:** >90%
- ✅ **Documentation Coverage:** 100% (all guides updated)
- ✅ **Performance:** <500ms template load (no >10% regression)
- ✅ **Zero Broken Links:** All file references valid

### Stretch Goals

- 🎯 **Code Reduction:** 74% (2,278 → 600 lines)
- 🎯 **Duplication Reduction:** 85% → 10%
- 🎯 **Maintenance Improvement:** 17x easier (edit 1 place vs 17)
- 🎯 **Test Coverage:** >85%
- 🎯 **Template Load Time:** <200ms

---

## 🆘 Troubleshooting

### Issue: Tests Failing After Cleanup

**Solution:**
1. Check test output for specific failures
2. Verify template files not accidentally deleted
3. Check import paths updated correctly
4. Rollback if >5 failures: `git reset --hard template-architecture-v1`

### Issue: Template Not Rendering

**Solution:**
1. Check template exists in YAML: `grep "template_name" cortex-brain/response-templates.yaml`
2. Verify inheritance chain: Check `extends` references
3. Test template loader: `python -c "from src.response_templates import loader; print(loader.load_template('name'))"`
4. Check logs: `tail -f logs/cortex.log`

### Issue: Performance Regression

**Solution:**
1. Profile template loading: Add timing instrumentation
2. Check for N+1 queries or excessive file I/O
3. Verify caching enabled
4. Compare with baseline metrics from pre-cleanup

### Issue: Broken Documentation Links

**Solution:**
1. Run link checker: `find .github/prompts -name "*.md" -exec grep -H "file:" {} \;`
2. Update file paths systematically
3. Verify with MkDocs: `mkdocs serve` and check all pages

---

**Checklist Version:** 1.0  
**Last Updated:** 2025-11-27  
**Author:** Asif Hussain  
**Status:** Ready for Phase 6 Execution
