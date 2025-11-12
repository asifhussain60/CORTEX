# CORTEX Quick Reference - Operation Configurations

**Purpose:** Fast lookup for operation settings, profiles, and modules  
**Last Updated:** 2025-11-10  
**Based On:** `cortex-brain/operations-config.yaml`

---

## 🚀 Quick Commands

| Command | Profile | Duration | What It Does |
|---------|---------|----------|--------------|
| `setup` | standard | ~10 min | Setup development environment |
| `refresh story` | standard | ~3 min | Validate and update story docs |
| `cleanup` | safe | ~1 min | Remove temporary files |
| `update docs` | local | ~5 min | Generate documentation |
| `check brain` | standard | ~3 min | Validate brain integrity |
| `run tests` | standard | ~7 min | Run test suite |
| `demo` | standard | ~5 min | Interactive tutorial |

---

## 📋 Operation Profiles

### Environment Setup

**Command:** `setup`, `setup environment`, `configure`

| Profile | Modules | Duration | Use When |
|---------|---------|----------|----------|
| minimal | 6 | 5 min | Quick testing, CI/CD |
| standard ⭐ | 9 | 10 min | Daily development |
| full | 11 | 15 min | Production deployment |

**Modules:**
- ✅ project_validation
- ✅ platform_detection (auto-detects Mac/Windows/Linux)
- ✅ git_sync (optional)
- ✅ virtual_environment
- ✅ python_dependencies
- ✅ vision_api (optional)
- ✅ conversation_tracking (optional)
- ✅ brain_initialization
- ✅ brain_tests
- ✅ tooling_verification (optional)
- ✅ setup_completion

---

### Story Refresh

**Command:** `refresh story`, `refresh cortex story`, `update story`

| Profile | Modules | Duration | Use When |
|---------|---------|----------|----------|
| quick | 3 | 2 min | Quick validation |
| standard ⭐ | 5 | 3 min | Normal refresh |
| full | 6 | 5 min | With HTML preview |

**Modules:**
- ✅ load_story_template
- 🟡 apply_narrator_voice (validation-only)
- ✅ validate_story_structure (optional)
- ✅ save_story_markdown
- ✅ update_mkdocs_index (optional)
- ✅ build_story_preview (full only)

**Note:** Currently validation-only (SKULL-005). Story already in narrator voice.

---

### Workspace Cleanup

**Command:** `cleanup`, `clean workspace`, `tidy up`

| Profile | Modules | Duration | Use When |
|---------|---------|----------|----------|
| safe ⭐ | 3 | 1 min | Auto-confirm cleanup |
| standard | 5 | 2 min | Regular maintenance |
| aggressive | 6 | 3 min | Remove everything |

**Modules:**
- ✅ scan_temporary_files
- ✅ remove_old_logs
- ✅ clear_python_cache (standard+)
- ✅ vacuum_sqlite_databases (standard+)
- ✅ remove_orphaned_files (aggressive only)
- ✅ generate_cleanup_report

**Cleanup Rules:**
- Temp files: `*.tmp`, `*.temp`, `*.cache` (>7 days)
- Log files: `*.log` (>30 days, keep latest 5)
- Python cache: `__pycache__`, `*.pyc`, `*.pyo`
- Orphaned files: Check Git tracking

---

### Documentation Update

**Command:** `update docs`, `build docs`, `generate documentation`

| Profile | Modules | Duration | Use When |
|---------|---------|----------|----------|
| local ⭐ | 5 | 5 min | Local build only |
| preview | 6 | 7 min | With preview server |
| full | 6 | 10 min | With deployment |

**Modules:**
- ✅ scan_docstrings
- ✅ generate_api_docs
- ✅ refresh_design_docs
- ✅ build_mkdocs_site
- ✅ validate_doc_links
- ✅ deploy_docs_preview (preview/full)

---

### Brain Protection Check

**Command:** `check brain`, `validate brain`, `brain integrity`

| Profile | Modules | Duration | Use When |
|---------|---------|----------|----------|
| quick | 4 | 2 min | Critical checks only |
| standard ⭐ | 6 | 3 min | All tier validation |
| comprehensive | 6 | 5 min | Deep scan |

**Modules:**
- ✅ load_protection_rules
- 🟡 validate_tier0_immutability (pending)
- 🟡 validate_tier1_structure (pending)
- 🟡 validate_tier2_schema (pending)
- 🟡 check_brain_integrity (pending)
- 🟡 generate_protection_report (pending)

**Status:** 1/6 modules implemented, architecture ready

---

### Test Execution

**Command:** `run tests`, `test suite`, `execute tests`

| Profile | Modules | Duration | Use When |
|---------|---------|----------|----------|
| quick | 2 | 3 min | Unit tests only |
| standard ⭐ | 3 | 7 min | Unit + integration |
| full | 5 | 15 min | Everything + coverage |

**Modules:**
- ⏸️ discover_tests (pending)
- ⏸️ run_unit_tests (pending)
- ⏸️ run_integration_tests (pending)
- ⏸️ generate_coverage_report (full only)
- ⏸️ validate_test_quality (full only)

**Status:** 0/5 modules implemented

---

### CORTEX Tutorial (Demo)

**Command:** `demo`, `tutorial`, `show capabilities`

| Profile | Modules | Duration | Use When |
|---------|---------|----------|----------|
| standard | 6 | 5 min | Full walkthrough |

**Modules:**
- ✅ demo_introduction
- ✅ demo_help_system
- ✅ demo_story_refresh
- ✅ demo_conversation
- ✅ demo_cleanup
- ✅ demo_completion

---

## 🎯 Module Status Legend

| Symbol | Meaning | Example |
|--------|---------|---------|
| ✅ | Production ready | environment_setup (11/11) |
| 🟡 | Validation-only | apply_narrator_voice |
| 🟡 | Partial implementation | cleanup (integration testing) |
| ⏸️ | Architecture ready | brain_protection (1/6) |
| ❌ | Not started | - |

---

## 📊 Implementation Summary

| Operation | Modules Implemented | Status | Notes |
|-----------|-------------------|--------|-------|
| environment_setup | 11/11 (100%) | ✅ READY | All platforms supported |
| cortex_tutorial | 6/6 (100%) | ✅ READY | Interactive demo complete |
| refresh_cortex_story | 6/6 (100%) | 🟡 VALIDATION | SKULL-005 compliant |
| workspace_cleanup | 6/6 (100%) | 🟡 INTEGRATION | Testing in progress |
| update_documentation | 6/6 (100%) | 🟡 PARTIAL | Orchestration pending |
| brain_protection_check | 1/6 (17%) | ⏸️ ARCHITECTURE | 5 modules pending |
| run_tests | 0/5 (0%) | ⏸️ PENDING | Design complete |

**Total:** 36/43 modules ready (84% core functionality)

---

## 🔧 Configuration Options

### Platform-Specific Settings

**Windows:**
- Shell: `pwsh`
- Python: `python`
- Path separator: `\`

**macOS (Darwin):**
- Shell: `zsh`
- Python: `python3`
- Path separator: `/`

**Linux:**
- Shell: `bash`
- Python: `python3`
- Path separator: `/`

### Timeouts

| Operation | Default | Adjustable |
|-----------|---------|------------|
| environment_setup | 15 min | Yes |
| refresh_cortex_story | 5 min | No |
| workspace_cleanup | 3 min | No |
| update_documentation | 10 min | Yes |
| brain_protection_check | 5 min | No |
| run_tests | 15 min | No |

### Retry Behavior

| Operation | Retry on Failure |
|-----------|-----------------|
| environment_setup | Yes (max 3) |
| refresh_cortex_story | No |
| workspace_cleanup | No |
| update_documentation | Yes (max 2) |
| brain_protection_check | No |
| run_tests | No |

---

## 🚨 Important Notes

### SKULL-005 Compliance

**Story Refresh Operation:**
- Status: 🟡 VALIDATION-ONLY
- Why: Story already in narrator voice
- Behavior: Validates structure, copies unchanged
- Future: AI-based transformation (Phase 6+)
- See: `cortex-brain/brain-protection-rules.yaml`

### Platform Auto-Detection

**Environment Setup:**
- Automatically detects Mac/Windows/Linux
- Configures platform-specific paths
- No manual configuration needed
- Runs on startup if platform changed

### Confirmation Required

**Workspace Cleanup:**
- Safe profile: Auto-confirm (read-only scan)
- Standard profile: User confirmation required
- Aggressive profile: User confirmation required

---

## 📚 Full Configuration

For complete configuration details, see:
- **Main Config:** `cortex-brain/operations-config.yaml`
- **Module Details:** `docs/operations/story-refresh-modules.md`
- **Integration Report:** `cortex-brain/MODULE-INTEGRATION-REPORT.md`
- **Status Dashboard:** `cortex-brain/cortex-2.0-design/CORTEX2-STATUS.MD`

---

## 🎯 Quick Troubleshooting

### "Operation not found"

**Solution:** Use natural language:
```
# Instead of /refresh_story
refresh story

# Instead of /setup_env
setup environment
```

### "Module not implemented"

**Solution:** Check status in this file. Use alternative profile or wait for implementation.

### "Profile not recognized"

**Valid profiles:** `minimal`, `quick`, `safe`, `standard`, `full`, `comprehensive`, `local`, `preview`

---

*This quick reference is generated from `cortex-brain/operations-config.yaml`. For detailed module documentation, see `docs/operations/`*

*Last Updated: 2025-11-10 | CORTEX 2.0*
