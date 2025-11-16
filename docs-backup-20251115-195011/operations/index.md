# CORTEX Operations Reference

Complete guide to all CORTEX operations, organized by category.

## Quick Links

- [Onboarding](#onboarding) - Getting started operations
- [Environment](#environment) - Setup and configuration
- [Documentation](#documentation) - Story and doc operations
- [Maintenance](#maintenance) - Cleanup and health checks
- [Development](#development) - Testing and validation
- [Planning](#planning) - Architecture and refactoring

---

## Onboarding

### [CORTEX Interactive Demo](./cortex-tutorial.md)
**Operation:** `cortex_tutorial` | **Status:** ✅ Ready

Hands-on walkthrough of CORTEX capabilities with live execution.

**Natural Language:** "demo", "show me what cortex can do", "tutorial"

**Profiles:**
- Quick (2 min): Essential commands only
- Standard (3-4 min): Core capabilities ⭐ Recommended
- Comprehensive (5-6 min): Full walkthrough

---

## Environment

### [Environment Setup](./environment-setup.md)
**Operation:** `environment_setup` | **Status:** ✅ Ready

Configure CORTEX development environment on Mac/Windows/Linux.

**Natural Language:** "setup", "configure", "initialize environment"

**Profiles:**
- Minimal: Core functionality (~2-3 min)
- Standard: Recommended for most users (~4-5 min) ⭐
- Full: Everything enabled (~6-8 min)

**Modules:** project_validation, platform_detection, git_sync, virtual_environment, python_dependencies, vision_api, conversation_tracking, brain_initialization, brain_tests, tooling_verification, setup_completion

---

### Platform Detection
**Operation:** `platform_detection` | **Status:** ✅ Ready

Auto-detect operating system and architecture.

**Natural Language:** "detect platform", "what platform am I on"

**Output:** OS (macOS/Windows/Linux), architecture (x86_64/arm64), shell type

---

## Documentation

### [Refresh CORTEX Story](./refresh-cortex-story.md)
**Operation:** `refresh_cortex_story` | **Status:** ✅ Ready

Update CORTEX story documentation with narrator voice transformation.

**Natural Language:** "refresh story", "update cortex story", "transform story"

**Profiles:**
- Quick: Narrator voice only (~30s)
- Standard: Voice + validation (~45s) ⭐
- Full: Everything + preview (~60s)

**Features:**
- Active narrator voice (passive → first-person dialogue)
- Progressive recaps for multi-part story
- Read time enforcement (60-75 minute target)
- Automatic backup before modification

---

### [Update Documentation](./update-documentation.md)
**Operation:** `update_documentation` | **Status:** 🔄 Partial

Refresh all 6 synchronized documentation files.

**Natural Language:** "update documentation", "refresh docs"

**Files Updated:**
- Technical-CORTEX.md (technical guide)
- Awakening Of CORTEX.md (story)
- Image-Prompts.md (system diagrams)
- History.md (timeline)
- Ancient-Rules.md (governance rules)
- CORTEX-FEATURES.md (feature list)

---

## Maintenance

### Workspace Cleanup
**Operation:** `workspace_cleanup` | **Status:** ✅ Ready

Scan and remove temporary files, old logs, Python cache, orphaned files.

**Natural Language:** "cleanup", "clean workspace", "remove temp files"

**Modules:** scan_temporary_files, remove_old_logs, clear_python_cache, vacuum_sqlite_databases, remove_orphaned_files, generate_cleanup_report

---

### Brain Health Check
**Operation:** `brain_health_check` | **Status:** ✅ Ready

Validate brain system integrity across all 4 tiers.

**Natural Language:** "brain health check", "check brain status"

**Checks:**
- Tier 0: Governance rules integrity
- Tier 1: Conversation memory database
- Tier 2: Knowledge graph validation
- Tier 3: Development context freshness

---

### Brain Protection Check
**Operation:** `brain_protection_check` | **Status:** ✅ Ready

Load and validate brain protection rules (SKULL layer + 6 protection layers).

**Natural Language:** "check brain protection", "validate protection rules"

**Validates:**
- brain-protection-rules.yaml structure
- All 7 protection layers (SKULL + 6 core)
- Rule priorities and enforcement levels

---

## Development

### [Help Command](./help-command.md)
**Operation:** `command_help` | **Status:** ✅ Ready

Display available operations with search, filtering, and multiple output formats.

**Natural Language:** "help", "what can cortex do", "show commands"

**Formats:**
- List: Simple list of operations
- Table: Formatted table with categories ⭐
- Detailed: Full documentation for each operation

---

### Run Tests
**Operation:** `run_tests` | **Status:** ✅ Ready

Execute test suite with pytest.

**Natural Language:** "run tests", "test cortex"

**Modules:** discover_tests, run_unit_tests, run_integration_tests, generate_coverage_report, validate_test_quality

**Test Categories:**
- Unit tests (fast, isolated)
- Integration tests (cross-module)
- Brain tests (protection layer validation)
- Edge cases (boundary conditions)
- Performance (regression benchmarks)

---

### Comprehensive Self Review
**Operation:** `comprehensive_self_review` | **Status:** 🔄 Partial

Multi-agent system review with architecture validation, code quality checks, test coverage analysis.

**Natural Language:** "review system", "self review", "validate architecture"

**Agents:** Architect Agent, Health Validator Agent, Pattern Matcher Agent, Learner Agent

---

## Planning

### Interactive Planning
**Operation:** `interactive_planning` | **Status:** ✅ Ready

Collaborative planning session with Work Planner agent.

**Natural Language:** "plan", "create task plan", "interactive planning"

**Features:**
- Task breakdown and sequencing
- Dependency identification
- Time estimation
- Risk assessment

---

### Architecture Planning
**Operation:** `architecture_planning` | **Status:** 🔄 Partial

High-level architecture design and validation.

**Natural Language:** "architecture planning", "design system"

---

### Refactoring Planning
**Operation:** `refactoring_planning` | **Status:** 🔄 Partial

Plan large-scale refactoring with impact analysis.

**Natural Language:** "refactoring plan", "plan refactor"

---

## Advanced Operations

### Command Search
**Operation:** `command_search` | **Status:** ✅ Ready

Search operations by name, category, or natural language.

**Natural Language:** "search commands", "find operation"

**Example:** "search commands related to testing"

---

### Project Validation
**Operation:** `project_validation` | **Status:** ✅ Ready

Validate CORTEX project structure and dependencies.

**Natural Language:** "validate project", "check project structure"

---

### Git Sync
**Operation:** `git_sync` | **Status:** ✅ Ready

Sync with git repository, check branch status.

**Natural Language:** "git sync", "sync repository"

---

### Virtual Environment
**Operation:** `virtual_environment` | **Status:** ✅ Ready

Create and activate Python virtual environment.

**Natural Language:** "create venv", "setup virtual environment"

---

### Python Dependencies  
**Operation:** `python_dependencies` | **Status:** ✅ Ready

Install Python packages from requirements.txt.

**Natural Language:** "install dependencies", "install requirements"

---

### Vision API
**Operation:** `vision_api` | **Status:** ✅ Ready

Configure vision capabilities (OpenAI GPT-4 Vision integration).

**Natural Language:** "setup vision", "configure vision api"

---

### Conversation Tracking
**Operation:** `conversation_tracking` | **Status:** ✅ Ready

Enable conversation memory and tracking.

**Natural Language:** "enable conversation tracking", "setup conversation memory"

---

### Brain Initialization
**Operation:** `brain_initialization` | **Status:** ✅ Ready

Initialize 4-tier brain system.

**Natural Language:** "initialize brain", "setup brain system"

---

### Brain Tests
**Operation:** `brain_tests` | **Status:** ✅ Ready

Run brain protection test suite (22 tests).

**Natural Language:** "test brain", "run brain tests"

---

## Operation Status Legend

- ✅ **Ready:** Fully implemented and tested
- 🔄 **Partial:** Implemented but incomplete or needs updates
- 🚧 **In Progress:** Currently being implemented
- 📋 **Planned:** Designed but not implemented

---

## Usage Patterns

### Entry Point Syntax

```bash
# Via /CORTEX entry point
/CORTEX <operation_name>
/CORTEX <operation_name> <profile>

# Examples
/CORTEX demo
/CORTEX setup standard
/CORTEX refresh story quick
```

### Natural Language

```bash
# Ask Copilot naturally
"show me what cortex can do"
"setup cortex environment"
"refresh the story"
"run comprehensive tests"
```

### Python API

```python
from src.cortex_entry import CortexEntry

# Initialize entry point
entry = CortexEntry()

# Execute operation
result = entry.execute("cortex_tutorial", profile="standard")

# Check result
if result["success"]:
    print(f"Operation completed: {result['message']}")
```

---

## Operation Development

To add a new operation:

1. **Define in cortex-operations.yaml:**
   ```yaml
   operations:
     my_operation:
       name: My Operation
       description: What it does
       natural_language:
         - "my command"
         - "do the thing"
       category: development
       modules: [module1, module2]
   ```

2. **Implement modules** in appropriate plugin

3. **Add documentation** in docs/operations/

4. **Write tests** in tests/operations/

5. **Update this index**

---

## Related Documentation

- [Plugin System Guide](../guides/plugin-system.md)
- [Module Development](../architecture/modules.md)
- [Natural Language Routing](../architecture/intent-detection.md)
- [Testing Operations](../testing/operation-testing.md)

---

*This reference covers all 50+ operations defined in cortex-operations.yaml. For detailed documentation on each operation, click the operation name.*

*Last Updated: 2025-11-10 | CORTEX 2.0 Documentation Initiative*
