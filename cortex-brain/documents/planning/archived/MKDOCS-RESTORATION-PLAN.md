# MkDocs Restoration Plan
**Date:** 2025-11-18  
**Author:** Asif Hussain  
**Status:** 🟢 IN PROGRESS  
**Goal:** Restore original MkDocs functionality from commit d4be9c6

---

## 📋 Executive Summary

The original MkDocs site (commit d4be9c6) had comprehensive documentation structure with:
- **Sacred Rules Home Page** - Visual display of all CORTEX governance rules
- **7-Section Navigation** - Home | Story | Getting Started | Architecture | Guides | Operations | Reference
- **Complete Story Chapters** - 10 individual chapter files with full narratives
- **Technical Documentation** - Architecture diagrams, API reference, integration guides
- **Custom Styling** - Three CSS files (custom.css, story.css, technical.css) with fantasy-themed typography

**Current State:** Basic MkDocs site with minimal navigation, no rules display, story in single file

**Target State:** Restored navigation structure + rules home page + integration with enterprise document generator

---

## 🎯 Objectives

### Primary Goals
1. ✅ Restore original MkDocs navigation structure (7 sections)
2. ✅ Restore Sacred Rules home page with visual styling
3. ✅ Integrate with enterprise document generator (`generate_all_docs.py`)
4. ✅ Create MkDocs configuration module for EPM
5. ✅ Add test harness to enforce navigation rules

### Secondary Goals
6. ✅ Restore custom CSS files (story.css, technical.css)
7. ✅ Create architecture documentation files
8. ✅ Create getting started guides
9. ✅ Create operations documentation
10. ✅ Create reference documentation

---

## 📊 Gap Analysis

### What Was Lost in Migration

| Feature | Original (d4be9c6) | Current | Status |
|---------|-------------------|---------|--------|
| **Home Page** | Sacred Rules display with fantasy styling | Generic welcome page | ❌ LOST |
| **Navigation** | 7 sections, 50+ pages | 3 sections, 7 pages | ❌ DEGRADED |
| **Story Structure** | 10 chapter files | 1 monolithic file | ❌ DEGRADED |
| **Custom CSS** | 3 files (custom, story, technical) | None | ❌ LOST |
| **Architecture Docs** | Overview, Tier System, Agents, Brain Protection | Executive summary only | ❌ LOST |
| **Getting Started** | Quick Start, Installation, Configuration | None | ❌ LOST |
| **Guides** | Developer, Admin, Best Practices, Troubleshooting | None | ❌ LOST |
| **Operations** | Overview, Entry Points, Workflows, Health Monitoring | None | ❌ LOST |
| **Reference** | API, Configuration, Templates, Integration | None | ❌ LOST |
| **MkDocs Theme** | Material with custom palette, fonts, features | Material with basic config | ❌ DEGRADED |

### What Was Preserved

| Feature | Status |
|---------|--------|
| **Diagram Generation** | ✅ Working (17+ Mermaid diagrams) |
| **Story Content** | ✅ Working (active narrative voice) |
| **Enterprise Pipeline** | ✅ Working (generate_all_docs.py) |
| **Validation Engine** | ✅ Working (file validation) |

---

## 🏗️ Implementation Phases

### ☐ Phase 1: Foundation (60 minutes)
**Goal:** Restore MkDocs configuration and home page

**Tasks:**
1. ☐ Restore original `mkdocs.yml` with full navigation structure
2. ☐ Create new `docs/index.md` with Sacred Rules display
3. ☐ Restore custom CSS files:
   - `docs/stylesheets/custom.css`
   - `docs/stylesheets/story.css`
   - `docs/stylesheets/technical.css`
4. ☐ Test MkDocs build: `mkdocs build`
5. ☐ Test MkDocs serve: `mkdocs serve`

**Success Criteria:**
- ✅ MkDocs builds without errors
- ✅ Home page displays Sacred Rules with styling
- ✅ Navigation structure matches original (7 sections)

---

### ☐ Phase 2: Architecture Documentation (90 minutes)
**Goal:** Create architecture section content

**Tasks:**
1. ☐ Create `docs/architecture/overview.md`
   - 4-tier system explanation
   - Agent system overview
   - Brain protection overview
2. ☐ Create `docs/architecture/tier-system.md`
   - Tier 0: Instinct (Governance)
   - Tier 1: Working Memory (Conversations)
   - Tier 2: Knowledge Graph (Patterns)
   - Tier 3: Context Intelligence (Analytics)
3. ☐ Create `docs/architecture/agents.md`
   - Left Brain: Tactical agents (Executor, Tester, Validator)
   - Right Brain: Strategic agents (Planner, Architect, Documenter)
   - Corpus Callosum: Coordination
4. ☐ Create `docs/architecture/brain-protection.md`
   - SKULL rules explanation
   - Layer-based protection
   - Examples and best practices
5. ☐ Link existing diagrams to architecture section
   - Module structure
   - Brain protection
   - EPM doc generator
   - Agent coordination
   - Information flow
   - Tier architecture

**Success Criteria:**
- ✅ Architecture section fully navigable
- ✅ All 4 architecture pages created with content
- ✅ Diagrams linked correctly

---

### ☐ Phase 3: Getting Started & Guides (60 minutes)
**Goal:** Create user-facing documentation

**Tasks:**
1. ☐ Create `docs/getting-started/quick-start.md`
   - 5-minute quickstart guide
   - Natural language command examples
   - First conversation walkthrough
2. ☐ Create `docs/getting-started/installation.md`
   - Cross-platform installation
   - Environment setup
   - Verification steps
3. ☐ Create `docs/getting-started/configuration.md`
   - cortex.config.json reference
   - Machine-specific settings
   - Multi-machine setup
4. ☐ Create `docs/guides/developer-guide.md`
   - Plugin development
   - Module creation
   - Testing guidelines
5. ☐ Create `docs/guides/admin-guide.md`
   - System administration
   - Backup and restore
   - Performance tuning
6. ☐ Create `docs/guides/best-practices.md`
   - TDD workflow
   - SOLID principles
   - Pattern learning
7. ☐ Create `docs/guides/troubleshooting.md`
   - Common issues
   - Debug procedures
   - FAQ

**Success Criteria:**
- ✅ Getting Started section complete (3 pages)
- ✅ Guides section complete (4 pages)
- ✅ All content validated for accuracy

---

### ☐ Phase 4: Operations & Reference (60 minutes)
**Goal:** Create operations and reference documentation

**Tasks:**
1. ☐ Create `docs/operations/overview.md`
   - Operations concept
   - Natural language interface
   - Entry point modules
2. ☐ Create `docs/operations/entry-point-modules.md`
   - setup, demo, status operations
   - cleanup, optimize operations
   - refresh, sync operations
3. ☐ Create `docs/operations/workflows.md`
   - Feature planning workflow
   - Code implementation workflow
   - Testing workflow
   - Documentation workflow
4. ☐ Create `docs/operations/health-monitoring.md`
   - System health metrics
   - Performance monitoring
   - Brain protection validation
5. ☐ Create `docs/reference/api.md`
   - Tier 0 API
   - Tier 1 API
   - Tier 2 API
   - Tier 3 API
6. ☐ Create `docs/reference/configuration.md`
   - Complete config reference
   - Environment variables
   - Path configuration
7. ☐ Create `docs/reference/response-templates.md`
   - Template system overview
   - Template format
   - Custom template creation
8. ☐ Link existing integration diagrams
   - Git integration
   - MkDocs integration
   - VSCode integration

**Success Criteria:**
- ✅ Operations section complete (4 pages)
- ✅ Reference section complete (3 pages)
- ✅ Integration diagrams linked

---

### ☐ Phase 5: EPM Integration (90 minutes)
**Goal:** Create MkDocs configurator module for enterprise generator

**Tasks:**
1. ☐ Create `src/epm/modules/mkdocs_configurator.py`
   - Read current mkdocs.yml
   - Discover generated documentation files
   - Build navigation tree dynamically
   - Write updated mkdocs.yml
   - Preserve custom configuration
2. ☐ Update `generate_all_docs.py` to use MkDocsConfigurator
   - Import module
   - Call configurator in mkdocs stage
   - Validate navigation structure
3. ☐ Add configuration to `cortex-brain/mkdocs-refresh-config.yaml`
   - Navigation structure rules
   - Section ordering
   - File discovery patterns
   - Excluded paths
4. ☐ Test full generation pipeline
   - `python generate_all_docs.py`
   - Verify all stages work
   - Verify mkdocs.yml updated correctly

**Success Criteria:**
- ✅ MkDocsConfigurator module implemented
- ✅ Enterprise generator uses configurator
- ✅ Navigation auto-updates on generation
- ✅ Manual edits preserved

---

### ☐ Phase 6: Test Harness (60 minutes)
**Goal:** Create automated tests to enforce navigation rules

**Tasks:**
1. ☐ Create `tests/documentation/test_mkdocs_navigation.py`
   - Test navigation structure (7 sections required)
   - Test home page exists and contains rules
   - Test all navigation links resolve
   - Test no broken internal links
   - Test section ordering matches spec
2. ☐ Create `tests/documentation/test_sacred_rules_display.py`
   - Test Sacred Rules section exists in home page
   - Test all 22 rules present
   - Test rule formatting correct
   - Test CSS classes applied
3. ☐ Create `tests/documentation/test_documentation_completeness.py`
   - Test all architecture pages exist
   - Test all getting started pages exist
   - Test all guides pages exist
   - Test all operations pages exist
   - Test all reference pages exist
4. ☐ Create `tests/documentation/test_mkdocs_build.py`
   - Test mkdocs builds without errors
   - Test mkdocs serves without errors
   - Test generated site structure
5. ☐ Add tests to CI/CD pipeline
   - Run on every PR
   - Block merge if tests fail

**Success Criteria:**
- ✅ 4 test modules created
- ✅ 20+ test cases implemented
- ✅ All tests passing
- ✅ CI/CD integration complete

---

## 📋 Sacred Rules to Display

### Layer I: Instinct Immutability
1. TDD_ENFORCEMENT
2. DEFINITION_OF_DONE
3. DEFINITION_OF_READY
4. BRAIN_PROTECTION_TESTS_MANDATORY
5. MACHINE_READABLE_FORMATS
6. CORTEX_PROMPT_FILE_PROTECTION

### Layer II: Tier Boundary Protection
7. TIER0_APPLICATION_DATA
8. TIER2_CONVERSATION_DATA

### Layer III: SOLID Compliance
9. SINGLE_RESPONSIBILITY
10. DEPENDENCY_INVERSION
11. OPEN_CLOSED
12. CODE_STYLE_CONSISTENCY

### Layer IV: Hemisphere Specialization
13. LEFT_BRAIN_TACTICAL
14. RIGHT_BRAIN_STRATEGIC

### Layer V: SKULL Protection
15. SKULL-001: Test Before Claim
16. SKULL-002: Integration Verification
17. SKULL-003: Visual Regression
18. SKULL-004: Retry Without Learning
19. SKULL-005: Transformation Verification
20. SKULL-006: Privacy Protection

### Layer VI: Namespace Isolation
21. NAMESPACE_WRITE_PROTECTION
22. NAMESPACE_PRIORITY_BOOSTING

---

## 🎨 CSS Restoration

### custom.css
- General site styling
- Navigation enhancements
- Layout improvements

### story.css
- Fantasy-themed typography
- Cinzel font for headers
- IM Fell English for body text
- Ancient scroll styling
- Chapter formatting

### technical.css
- Code block styling
- API documentation formatting
- Diagram container styling
- Reference section layout

---

## 📈 Success Metrics

### Completion Criteria
- ✅ MkDocs builds successfully
- ✅ All 7 navigation sections present
- ✅ Home page displays all 22 Sacred Rules
- ✅ 50+ documentation pages created
- ✅ Custom CSS applied correctly
- ✅ Enterprise generator integrated
- ✅ 20+ tests passing
- ✅ CI/CD validation enforced

### Quality Gates
- Zero MkDocs build warnings
- Zero broken internal links
- 100% test pass rate
- Visual regression tests pass
- Documentation coverage >90%

---

## 🚀 Execution Timeline

**Total Estimated Time:** 6-7 hours

| Phase | Duration | Dependencies | Priority |
|-------|----------|--------------|----------|
| Phase 1: Foundation | 60 min | None | 🔴 CRITICAL |
| Phase 2: Architecture | 90 min | Phase 1 | 🔴 CRITICAL |
| Phase 3: Getting Started | 60 min | Phase 1 | 🟡 HIGH |
| Phase 4: Operations | 60 min | Phase 1 | 🟡 HIGH |
| Phase 5: EPM Integration | 90 min | Phases 1-4 | 🔴 CRITICAL |
| Phase 6: Test Harness | 60 min | Phases 1-5 | 🔴 CRITICAL |

**Parallel Opportunities:**
- Phases 2, 3, 4 can be done in parallel (content creation)
- CSS restoration can be done alongside Phase 1
- Tests can be written alongside each phase

---

## 📝 Notes

### Migration Decisions
- **Preserve current story.md** - Already has active narrative voice
- **Keep enterprise generator** - Integration > replacement
- **Enhance, don't replace** - Build on current foundation
- **Test-driven restoration** - Write tests first for critical paths

### Risk Mitigation
- **Backup current mkdocs.yml** before modification
- **Incremental testing** after each phase
- **Git commits** after each working phase
- **Rollback plan** if build breaks

---

## 🔗 References

**Original Commit:** d4be9c6  
**Original Files:**
- `mkdocs.yml` (navigation structure)
- `docs/index.md` (Sacred Rules home page)
- `docs/stylesheets/custom.css`
- `docs/stylesheets/story.css`
- `docs/stylesheets/technical.css`

**Current Files:**
- `generate_all_docs.py` (enterprise generator)
- `src/epm/modules/` (EPM modules)
- `cortex-brain/mkdocs-refresh-config.yaml` (config)

**Documentation:**
- CORTEX 2.1 Technical Reference
- MkDocs Material Theme Documentation
- Python Markdown Extensions

---

**Status:** 🟢 Ready to begin Phase 1  
**Next Action:** Restore mkdocs.yml and create Sacred Rules home page  
**Approval:** Pending user confirmation

---

*Plan created by CORTEX Documentation Restoration System*  
*Author: Asif Hussain*  
*Copyright: © 2024-2025 Asif Hussain. All rights reserved.*
