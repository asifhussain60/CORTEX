# CORTEX Toolkit Architecture Plan

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX  
**Created:** December 16, 2025  
**Status:** Planning Phase  
**Version:** 1.0

---

## 🎯 Executive Summary

This plan consolidates 300+ scattered Python scripts, PowerShell scripts, and shell scripts across the CORTEX repository into a well-architected, cross-repository toolkit. The toolkit will be portable, discoverable, and reusable across all workspace repositories (CORTEX, KSESSIONS, NOOR CANVAS, KASHKOLE).

---

## 📊 Current State Analysis

### Script Inventory

**CORTEX Repository:**
- **Python Scripts:** 3,252 files
  - Core: 150+ in `scripts/`
  - CLI Wrappers: 10 in `scripts/cli_wrappers/`
  - Utilities: 25+ in `scripts/utilities/`
  - Operations: 6 in `scripts/operations/`
  - Tests: 3,000+ in `tests/`
  
- **PowerShell Scripts:** 491 files
  - Legacy (archived): 400+ in `scripts/_archive/kds-legacy/`
  - Active: ~90 scripts
  - Dashboard launcher: `launch_dashboard_server.ps1`
  - Auto-resume: `scripts/auto-resume-prompt.ps1`

- **Shell Scripts:** 13 files (Linux/macOS support)
  - Launchers: `scripts/launchers/run-cortex.sh`
  - Setup: `scripts/install-shell-integration.sh`
  - Auto-resume: `scripts/auto-resume-prompt.sh`

**Other Repositories:**
- **KSESSIONS:** 25+ PowerShell scripts in `Workspaces/Scripts-Tools/GLOBAL/`
- **NOOR CANVAS:** 100+ PowerShell scripts in `Scripts/`
- **KASHKOLE:** Minimal scripts (mostly archived)

### Problems Identified

1. **Discoverability Crisis:**
   - Scripts scattered across 10+ directories
   - No unified catalog or registry
   - Duplicate functionality across repos
   - No cross-repository access

2. **Maintenance Burden:**
   - Similar scripts duplicated per-repo
   - Inconsistent naming conventions
   - No version management
   - Legacy code mixed with production code

3. **Integration Gaps:**
   - Scripts can't be called from other repos
   - No unified CLI interface
   - Manual path management required
   - No dependency resolution

4. **Documentation Issues:**
   - README.md outdated (mentions only 6 scripts)
   - No usage examples
   - No parameter documentation
   - No cross-references

---

## 🏗️ Proposed Architecture

### Toolkit Structure

```
D:\PROJECTS\CORTEX\
├── cortex-toolkit/                     # NEW: Unified toolkit root
│   ├── README.md                       # Comprehensive toolkit documentation
│   ├── toolkit-manifest.yaml           # Tool registry and metadata
│   ├── VERSION                         # Toolkit version
│   │
│   ├── core/                           # Core CORTEX tools (cross-repo)
│   │   ├── brain/                      # Brain operations
│   │   │   ├── align.py
│   │   │   ├── healthcheck.py
│   │   │   ├── optimize.py
│   │   │   └── vacuum.py
│   │   ├── operations/                 # System operations
│   │   │   ├── deploy.py
│   │   │   ├── review.py
│   │   │   ├── cleanup.py
│   │   │   └── regenerate_prompts.py
│   │   ├── planning/                   # Planning tools
│   │   │   ├── plan_generator.py
│   │   │   ├── ado_manager.py
│   │   │   └── planning_file_manager.py
│   │   └── utilities/                  # General utilities
│   │       ├── token_calculator.py
│   │       ├── path_resolver.py
│   │       └── config_manager.py
│   │
│   ├── cli/                            # Command-line interfaces
│   │   ├── cortex-cli.py              # Unified CLI entry point
│   │   ├── wrappers/                   # CLI wrappers
│   │   │   ├── base_wrapper.py
│   │   │   ├── align_wrapper.py
│   │   │   ├── healthcheck_wrapper.py
│   │   │   └── ... (10 wrappers)
│   │   └── launchers/                  # Platform launchers
│   │       ├── run-cortex.ps1         # Windows
│   │       ├── run-cortex.sh          # Linux/macOS
│   │       └── launch_dashboard.ps1    # Dashboard
│   │
│   ├── analytics/                      # Analysis & reporting tools
│   │   ├── profiling/
│   │   │   ├── profile_performance.py
│   │   │   ├── profile_startup.py
│   │   │   └── benchmark_parallel_execution.py
│   │   ├── metrics/
│   │   │   ├── collect_dashboard_data.py
│   │   │   ├── generate_metrics_report.py
│   │   │   └── monitor_brain_health.py
│   │   └── visualization/
│   │       ├── generate_uml.py
│   │       ├── dependency_graph_generator.py
│   │       └── architecture_visualizer.py
│   │
│   ├── migration/                      # Database & schema migration
│   │   ├── schema_migrator.py
│   │   ├── migrate_conversations.py
│   │   ├── migrate_templates.py
│   │   └── version_detector.py
│   │
│   ├── documentation/                  # Documentation generation
│   │   ├── generate_docs_from_code.py
│   │   ├── regenerate_prompts.py
│   │   ├── generate_quick_reference.py
│   │   └── doc_sync_hooks.py
│   │
│   ├── testing/                        # Testing utilities
│   │   ├── generate_performance_tests.py
│   │   ├── validate_deployment.py
│   │   ├── run_validation_suite.py
│   │   └── verify_no_mocks.py
│   │
│   ├── maintenance/                    # Maintenance tools
│   │   ├── cleanup_temp_files.py
│   │   ├── cleanup_obsolete_tests.py
│   │   ├── detect_duplicates.py
│   │   └── master_cleanup.py
│   │
│   ├── shared/                         # Shared libraries
│   │   ├── config.py                   # Configuration loader
│   │   ├── logging_config.py           # Logging setup
│   │   ├── path_resolver.py            # Cross-repo path resolution
│   │   └── toolkit_registry.py         # Tool discovery & registration
│   │
│   └── install/                        # Installation & setup
│       ├── install-toolkit.ps1         # Windows installer
│       ├── install-toolkit.sh          # Linux/macOS installer
│       ├── setup-global-commands.ps1   # Global command setup
│       └── verify-installation.py      # Installation verification
│
├── scripts/                            # DEPRECATED: Legacy location (symlinks)
│   └── README.md                       # Migration notice → cortex-toolkit/
│
└── ... (rest of CORTEX repo)
```

### Cross-Repository Access

**Global Configuration:**
```yaml
# D:\PROJECTS\global-workspace-config.yaml
cortex_toolkit_root: D:\PROJECTS\CORTEX\cortex-toolkit
workspace_roots:
  - D:\PROJECTS\CORTEX
  - D:\PROJECTS\KSESSIONS
  - D:\PROJECTS\NOOR CANVAS
  - D:\PROJECTS\KASHKOLE

path_aliases:
  - alias: cortex
    path: D:\PROJECTS\CORTEX\cortex-toolkit
  - alias: ksessions
    path: D:\PROJECTS\KSESSIONS
  - alias: noorcanvas
    path: D:\PROJECTS\NOOR CANVAS
```

**PowerShell Profile Integration:**
```powershell
# Microsoft.PowerShell_profile.ps1
$env:CORTEX_TOOLKIT_ROOT = "D:\PROJECTS\CORTEX\cortex-toolkit"
$env:PATH += ";$env:CORTEX_TOOLKIT_ROOT\cli"

# Load global commands
. "$env:CORTEX_TOOLKIT_ROOT\install\setup-global-commands.ps1"

# Available commands:
# cortex-align, cortex-health, cortex-optimize, cortex-plan, etc.
```

**Bash Profile Integration:**
```bash
# ~/.bashrc or ~/.zshrc
export CORTEX_TOOLKIT_ROOT="$HOME/PROJECTS/CORTEX/cortex-toolkit"
export PATH="$CORTEX_TOOLKIT_ROOT/cli:$PATH"

# Load global commands
source "$CORTEX_TOOLKIT_ROOT/install/setup-global-commands.sh"
```

---

## 🔧 Toolkit Registry System

### Manifest Structure (`toolkit-manifest.yaml`)

```yaml
version: 1.0.0
last_updated: 2025-12-16T00:00:00Z
toolkit_root: D:\PROJECTS\CORTEX\cortex-toolkit

categories:
  brain_operations:
    description: CORTEX brain tier operations
    tools:
      - name: align
        command: cortex-align
        script: core/brain/align.py
        wrapper: cli/wrappers/align_wrapper.py
        description: System alignment and consistency checks
        platforms: [windows, linux, macos]
        requires_admin: false
        execution_method: cli_wrapper
        
      - name: healthcheck
        command: cortex-health
        script: core/brain/healthcheck.py
        wrapper: cli/wrappers/healthcheck_wrapper.py
        description: Comprehensive system health diagnostics
        platforms: [windows, linux, macos]
        requires_admin: false
        execution_method: cli_wrapper

  operations:
    description: System operations and orchestration
    tools:
      - name: review
        command: cortex-review
        script: core/operations/review.py
        wrapper: cli/wrappers/review_wrapper.py
        description: Code review orchestration
        platforms: [windows, linux, macos]
        requires_admin: false
        execution_method: cli_wrapper
        
      - name: deploy
        command: cortex-deploy
        script: core/operations/deploy.py
        wrapper: cli/wrappers/deploy_wrapper.py
        description: Deployment to publish directory
        platforms: [windows, linux, macos]
        requires_admin: true
        execution_method: cli_wrapper

  planning:
    description: Planning and ADO management
    tools:
      - name: plan
        command: cortex-plan
        script: core/planning/plan_generator.py
        description: Generate feature implementation plans
        platforms: [windows, linux, macos]
        requires_admin: false
        execution_method: copilot_chat
        
      - name: ado
        command: cortex-ado
        script: core/planning/ado_manager.py
        description: Azure DevOps work item management
        platforms: [windows, linux, macos]
        requires_admin: false
        execution_method: copilot_chat

  analytics:
    description: Analysis and reporting
    tools:
      - name: profile
        command: cortex-profile
        script: analytics/profiling/profile_performance.py
        description: Performance profiling and analysis
        platforms: [windows, linux, macos]
        requires_admin: false
        execution_method: cli
        
      - name: metrics
        command: cortex-metrics
        script: analytics/metrics/collect_dashboard_data.py
        description: Collect and display system metrics
        platforms: [windows, linux, macos]
        requires_admin: false
        execution_method: cli

  documentation:
    description: Documentation generation
    tools:
      - name: docs-generate
        command: cortex-docs-gen
        script: documentation/generate_docs_from_code.py
        description: Generate documentation from source code
        platforms: [windows, linux, macos]
        requires_admin: false
        execution_method: cli
        
      - name: prompts-regenerate
        command: cortex-prompts-regen
        script: documentation/regenerate_prompts.py
        wrapper: cli/wrappers/regenerate_prompts_wrapper.py
        description: Regenerate AI prompt files
        platforms: [windows, linux, macos]
        requires_admin: true
        execution_method: cli_wrapper

  testing:
    description: Testing utilities
    tools:
      - name: validate
        command: cortex-validate
        script: testing/validate_deployment.py
        description: Validate deployment integrity
        platforms: [windows, linux, macos]
        requires_admin: false
        execution_method: cli
```

### Tool Discovery API

```python
# cortex-toolkit/shared/toolkit_registry.py
from pathlib import Path
import yaml
from typing import Dict, List, Optional

class ToolkitRegistry:
    """Registry for discovering and invoking toolkit tools."""
    
    def __init__(self, toolkit_root: Optional[Path] = None):
        self.toolkit_root = toolkit_root or self._discover_toolkit_root()
        self.manifest_path = self.toolkit_root / "toolkit-manifest.yaml"
        self.manifest = self._load_manifest()
    
    def _discover_toolkit_root(self) -> Path:
        """Auto-discover toolkit root from environment or config."""
        # Check environment variable
        if env_root := os.getenv("CORTEX_TOOLKIT_ROOT"):
            return Path(env_root)
        
        # Check global config
        global_config = Path.home() / ".cortex" / "config.yaml"
        if global_config.exists():
            config = yaml.safe_load(global_config.read_text())
            return Path(config["cortex_toolkit_root"])
        
        # Fallback: relative to current repo
        return Path(__file__).parent.parent
    
    def _load_manifest(self) -> Dict:
        """Load toolkit manifest."""
        return yaml.safe_load(self.manifest_path.read_text(encoding='utf-8'))
    
    def list_categories(self) -> List[str]:
        """List all tool categories."""
        return list(self.manifest["categories"].keys())
    
    def list_tools(self, category: Optional[str] = None) -> List[Dict]:
        """List all tools or tools in a specific category."""
        if category:
            return self.manifest["categories"][category]["tools"]
        
        all_tools = []
        for cat_data in self.manifest["categories"].values():
            all_tools.extend(cat_data["tools"])
        return all_tools
    
    def get_tool(self, name: str) -> Optional[Dict]:
        """Get tool metadata by name."""
        for tool in self.list_tools():
            if tool["name"] == name:
                return tool
        return None
    
    def resolve_script_path(self, tool_name: str) -> Optional[Path]:
        """Resolve absolute path to tool script."""
        if tool := self.get_tool(tool_name):
            return self.toolkit_root / tool["script"]
        return None
    
    def invoke_tool(self, name: str, args: List[str]) -> int:
        """Invoke a tool with arguments."""
        tool = self.get_tool(name)
        if not tool:
            raise ValueError(f"Tool not found: {name}")
        
        script_path = self.resolve_script_path(name)
        if not script_path.exists():
            raise FileNotFoundError(f"Script not found: {script_path}")
        
        # Execute based on execution_method
        if tool["execution_method"] == "cli_wrapper":
            wrapper_path = self.toolkit_root / tool["wrapper"]
            return self._run_python_script(wrapper_path, args)
        elif tool["execution_method"] == "cli":
            return self._run_python_script(script_path, args)
        else:
            raise ValueError(f"Unsupported execution method: {tool['execution_method']}")
    
    def _run_python_script(self, script_path: Path, args: List[str]) -> int:
        """Execute Python script with arguments."""
        import subprocess
        cmd = ["python", str(script_path)] + args
        return subprocess.run(cmd).returncode
```

---

## 🚀 Migration Plan

### Phase 1: Toolkit Foundation (Days 1-3)

**Tasks:**
1. Create `cortex-toolkit/` directory structure
2. Implement `toolkit-manifest.yaml`
3. Build `ToolkitRegistry` API
4. Create installation scripts
5. Update global configurations

**Deliverables:**
- Toolkit skeleton with all folders
- Working registry system
- Installation scripts tested on Windows/Linux/macOS

### Phase 2: Core Tools Migration (Days 4-7)

**Priority 1 - Brain Operations:**
1. Migrate CLI wrappers (`scripts/cli_wrappers/` → `cortex-toolkit/cli/wrappers/`)
2. Migrate brain operations (`src/operations/` → `cortex-toolkit/core/brain/`)
3. Update imports and paths
4. Test cross-repository invocation

**Priority 2 - System Operations:**
1. Migrate system operation scripts
2. Migrate planning tools
3. Migrate utilities
4. Update `cortex-operations.yaml` references

**Deliverables:**
- 30+ core tools migrated
- All CLI wrappers functional
- Cross-repo access verified

### Phase 3: Analytics & Documentation (Days 8-10)

**Tasks:**
1. Migrate analytics scripts (`scripts/` → `cortex-toolkit/analytics/`)
2. Migrate documentation generators
3. Migrate testing utilities
4. Migrate maintenance tools

**Deliverables:**
- 50+ tools migrated
- Documentation generators working
- Testing utilities functional

### Phase 4: Cross-Repository Integration (Days 11-13)

**Tasks:**
1. Setup global PowerShell profile integration
2. Setup global Bash profile integration
3. Create repository-specific adapters
4. Test from KSESSIONS, NOOR CANVAS, KASHKOLE

**Deliverables:**
- Global commands available workspace-wide
- Profile integration scripts
- Cross-repo verification tests

### Phase 5: Legacy Cleanup & Documentation (Days 14-15)

**Tasks:**
1. Archive legacy scripts (keep in `scripts/_archive/`)
2. Create symlinks for backward compatibility
3. Generate comprehensive toolkit README
4. Create usage documentation
5. Generate API documentation

**Deliverables:**
- Legacy code archived safely
- Backward compatibility maintained
- Complete documentation
- Migration guide

### Phase 6: Validation & Rollout (Day 16)

**Tasks:**
1. Run full validation suite
2. Performance benchmarking
3. User acceptance testing
4. Final documentation review
5. Announcement and rollout

**Deliverables:**
- 100% validation pass rate
- Performance benchmarks documented
- Toolkit v1.0 released

---

## 📐 Design Patterns & Standards

### Naming Conventions

**Commands:**
- Format: `cortex-{verb}` (e.g., `cortex-align`, `cortex-health`)
- PowerShell functions: `Invoke-CortexAlign`, `Get-CortexHealth`
- Bash functions: `cortex_align`, `cortex_health`

**Scripts:**
- Python: `lowercase_with_underscores.py`
- PowerShell: `Verb-Noun.ps1` (PascalCase)
- Bash: `lowercase-with-hyphens.sh`

**Directories:**
- `lowercase/` (no underscores)

### Configuration Management

**Hierarchical Configuration:**
1. Global workspace config: `D:\PROJECTS\global-workspace-config.yaml`
2. User config: `~/.cortex/config.yaml`
3. Repository config: `{repo}/cortex.config.json`
4. Environment variables: `CORTEX_TOOLKIT_ROOT`, etc.

**Priority:** Environment > User > Repository > Global

### Error Handling

**Standard Error Codes:**
- `0` - Success
- `1` - Generic error
- `2` - Configuration error
- `3` - Permission error
- `4` - Not found error
- `5` - Validation error
- `10` - Tool-specific errors (10-99)

**Logging:**
- Use `cortex-toolkit/shared/logging_config.py`
- Format: `[TIMESTAMP] [LEVEL] [TOOL] Message`
- Levels: DEBUG, INFO, WARNING, ERROR, CRITICAL

---

## 🧪 Testing Strategy

### Unit Tests
- Test each tool in isolation
- Mock external dependencies
- Location: `tests/toolkit/unit/`

### Integration Tests
- Test cross-tool workflows
- Test cross-repository access
- Location: `tests/toolkit/integration/`

### Platform Tests
- Test on Windows, Linux, macOS
- Test PowerShell, Bash, Python
- Location: `tests/toolkit/platform/`

### Performance Tests
- Benchmark tool startup time
- Benchmark registry discovery
- Location: `tests/toolkit/performance/`

---

## 📊 Success Metrics

### Quantitative Metrics
1. **Tool Discoverability:** <2 seconds to list all tools
2. **Cross-Repo Invocation:** <5 seconds overhead
3. **Installation Time:** <3 minutes (Windows/Linux/macOS)
4. **Documentation Coverage:** 100% of public APIs
5. **Test Coverage:** >80% for toolkit code

### Qualitative Metrics
1. **Developer Satisfaction:** Can find tools easily
2. **Cross-Team Adoption:** Used across KSESSIONS, NOOR CANVAS
3. **Maintenance Reduction:** Less duplicate code
4. **Onboarding Speed:** New team members productive in <1 hour

---

## 🔐 Security Considerations

### Access Control
- Admin-only tools require elevation
- Cross-repo access validated via config
- No hardcoded credentials

### Audit Trail
- Log all tool invocations
- Record user, timestamp, arguments
- Location: `logs/toolkit-audit.log`

### Sensitive Data
- Never log passwords or tokens
- Sanitize paths in logs
- Use secure config storage

---

## 🛠️ Implementation Guidelines

### For Tool Authors

**Creating a New Tool:**

1. **Define in Manifest:**
```yaml
# cortex-toolkit/toolkit-manifest.yaml
tools:
  - name: my-tool
    command: cortex-mytool
    script: core/utilities/my_tool.py
    description: Does something useful
    platforms: [windows, linux, macos]
    requires_admin: false
    execution_method: cli
```

2. **Implement Script:**
```python
# cortex-toolkit/core/utilities/my_tool.py
import argparse
from pathlib import Path
import sys

# Add toolkit to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "shared"))
from logging_config import setup_logging
from toolkit_registry import ToolkitRegistry

def main():
    parser = argparse.ArgumentParser(description="My useful tool")
    parser.add_argument("--option", help="An option")
    args = parser.parse_args()
    
    logger = setup_logging("my-tool")
    logger.info("Starting my-tool...")
    
    # Your logic here
    
    logger.info("Completed successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())
```

3. **Add Tests:**
```python
# tests/toolkit/unit/test_my_tool.py
import pytest
from cortex_toolkit.core.utilities.my_tool import main

def test_my_tool_success():
    result = main(["--option", "value"])
    assert result == 0
```

4. **Document:**
```markdown
# cortex-toolkit/core/utilities/README.md
## my-tool

**Command:** `cortex-mytool`

**Description:** Does something useful

**Usage:**
```bash
cortex-mytool --option value
```

**Options:**
- `--option VALUE` - An option
```

### For Tool Consumers

**Using Tools:**

**From Command Line:**
```bash
# List all tools
cortex-cli list

# List tools in category
cortex-cli list --category brain_operations

# Invoke tool
cortex-align --check-only

# Get help
cortex-align --help
```

**From Python:**
```python
from cortex_toolkit.shared.toolkit_registry import ToolkitRegistry

registry = ToolkitRegistry()

# List tools
tools = registry.list_tools()

# Get tool info
tool_info = registry.get_tool("align")

# Invoke tool
registry.invoke_tool("align", ["--check-only"])
```

**From PowerShell:**
```powershell
# List tools
Get-CortexTools

# Invoke tool
Invoke-CortexAlign -CheckOnly

# Get help
Get-Help Invoke-CortexAlign
```

---

## 📚 Documentation Requirements

### Required Documentation

**Per Tool:**
1. Command syntax
2. Parameter descriptions
3. Usage examples
4. Return codes
5. Dependencies

**Per Category:**
1. Category overview
2. Common workflows
3. Tool relationships

**Toolkit-Level:**
1. Installation guide
2. Configuration guide
3. Cross-repo setup guide
4. API reference
5. Migration guide (for legacy scripts)

---

## 🔄 Backward Compatibility

### Legacy Script Support

**Strategy:**
1. Keep legacy scripts in `scripts/_archive/`
2. Create symlinks in `scripts/` → `cortex-toolkit/`
3. Add deprecation warnings
4. Maintain for 2 major versions

**Example Deprecation Warning:**
```python
# scripts/align.py (legacy location)
import warnings
warnings.warn(
    "This script location is deprecated. Use 'cortex-align' from cortex-toolkit instead.",
    DeprecationWarning,
    stacklevel=2
)

# Delegate to new location
from cortex_toolkit.core.brain.align import main
if __name__ == "__main__":
    main()
```

---

## 🎯 Next Steps

### Immediate Actions

1. **Review & Approval:** Stakeholder review of this plan
2. **Prototype:** Build Phase 1 toolkit foundation
3. **Pilot Migration:** Migrate 3 critical tools (align, healthcheck, plan)
4. **Validation:** Test cross-repo access from KSESSIONS
5. **Iterate:** Refine based on feedback

### Long-Term Vision

**Version 2.0 Features:**
- Web-based toolkit browser
- Automated tool dependency resolution
- Cloud-hosted shared tools
- Real-time tool telemetry
- AI-powered tool recommendations

---

## 📝 Appendix

### A. Full Script Inventory

**CORTEX Repository Scripts (Top 100):**
```
scripts/
├── cli_wrappers/
│   ├── align_wrapper.py
│   ├── cleanup_wrapper.py
│   ├── deploy_wrapper.py
│   ├── healthcheck_wrapper.py
│   ├── optimize_wrapper.py
│   ├── regenerate_prompts_wrapper.py
│   ├── review_wrapper.py
│   ├── sanitize_wrapper.py
│   └── base_wrapper.py
├── operations/
│   ├── brain_preserver.py
│   ├── config_merger.py
│   ├── github_fetcher.py
│   ├── schema_migrator.py
│   ├── upgrade_orchestrator.py
│   └── version_detector.py
├── utilities/
│   ├── analyze_duplicates.py
│   ├── benchmark_parallel.py
│   ├── check_schema.py
│   ├── debug_dashboard.py
│   ├── launch_admin_dashboard.py
│   └── ... (20+ more)
├── ado_manager.py
├── aggregate_team_telemetry.py
├── analyze_plan_tokens.py
├── benchmark_tdd_mastery.py
├── brain_transfer_cli.py
├── cleanup_comments.py
├── cleanup_temp_files.py
├── collect_dashboard_data_with_progress.py
├── dependency_graph_generator.py
├── deploy_cortex.py
├── detect_duplicates.py
├── generate_docs_from_code.py
├── generate_missing_docs.py
├── generate_performance_tests.py
├── generate_quick_reference.py
├── generate_uml_standalone.py
├── measure_prompt_tokens.py
├── migrate_existing_plans.py
├── monitor_brain_health.py
├── planning_file_manager.py
├── plan_cli.py
├── profile_performance.py
├── profile_startup.py
├── refresh_tier3_metrics.py
├── regenerate_all_docs.py
├── regenerate_cortex_prompts.py
├── regenerate_diagrams.py
├── remove_deprecated_code.py
├── roadmap_calculator.py
├── run_alignment.py
├── run_cleanup.py
├── run_optimize.py
├── sanitize_ra_domain.py
├── token_pricing_calculator.py
├── validate_cortex_3_0.py
├── validate_deployment.py
├── validate_templates.py
├── verify_deployment_package.py
├── version_manager.py
└── visualize_brain_health.py
```

### B. Cross-Repository Tool Usage Matrix

| Tool Category | CORTEX | KSESSIONS | NOOR CANVAS | KASHKOLE |
|---------------|--------|-----------|-------------|----------|
| Brain Ops | ✅ Primary | ✅ Used | ✅ Used | ❌ |
| Operations | ✅ Primary | ✅ Used | ✅ Used | ❌ |
| Planning | ✅ Primary | ✅ Heavy | ✅ Heavy | ❌ |
| Analytics | ✅ Primary | ✅ Used | ✅ Used | ❌ |
| Documentation | ✅ Primary | ✅ Used | ✅ Used | ❌ |
| Testing | ✅ Primary | ✅ Heavy | ✅ Heavy | ❌ |
| Deployment | ✅ Primary | ✅ Heavy | ✅ Heavy | ❌ |

### C. Platform Support Matrix

| Platform | Python | PowerShell | Bash | Batch |
|----------|--------|------------|------|-------|
| Windows 11 | ✅ 3.8+ | ✅ 5.1+ | ✅ WSL | ✅ |
| macOS | ✅ 3.8+ | ❌ | ✅ zsh | ❌ |
| Linux | ✅ 3.8+ | ❌ | ✅ bash | ❌ |

---

**End of Plan**

**Approval Required From:**
- [ ] CORTEX Maintainers
- [ ] KSESSIONS Team
- [ ] NOOR CANVAS Team

**Next Review Date:** December 20, 2025
