# IDE Documentation Auto-Generation Specification

**Version:** 1.0  
**Author:** Asif Hussain  
**Created:** December 18, 2025  
**Status:** 🟢 APPROVED - Part of CORTEX 4.0 MASTER-PLAN  
**Related:** MASTER-PLAN.md Section 1.5 (Cross-IDE Compatibility), Phase 1.5, Phase 6

---

## 📋 Executive Summary

This specification defines how CORTEX 4.0's Documentation Orchestrator automatically generates comprehensive IDE setup documentation for VSCode and Visual Studio, ensuring zero-config onboarding for developers using either IDE.

**Key Features:**
- Auto-generate 9 IDE-specific documentation files
- Extract from code, configuration files, and MASTER-PLAN
- Generate interactive diagrams (class diagrams, configuration inheritance)
- Support VSCode + Visual Studio simultaneously
- Update documentation on code/config changes

**Deliverables:**
- 4 Setup Guides (VSCode, Visual Studio, Switching, Troubleshooting)
- 3 Configuration References (VSCode, Visual Studio, CORTEX Brain)
- 2 Architecture Documents (IDE Compatibility, IDE Detection System)

---

## 🎯 Documentation Structure

### Output Directory Structure

```
docs/
├── setup/                                  # IDE-specific setup guides
│   ├── vscode-setup.md                     # ✅ AUTO-GENERATED
│   ├── visualstudio-setup.md               # ✅ AUTO-GENERATED
│   ├── ide-switching.md                    # ✅ AUTO-GENERATED
│   └── ide-detection-troubleshooting.md    # ✅ AUTO-GENERATED
├── configuration/                          # Configuration references
│   ├── vscode-config-reference.md          # ✅ AUTO-GENERATED
│   ├── visualstudio-config-reference.md    # ✅ AUTO-GENERATED
│   └── cortex-brain-config.md              # ✅ AUTO-GENERATED
└── architecture/                           # Architecture documentation
    ├── ide-compatibility.md                # ✅ AUTO-GENERATED
    └── ide-detection-system.md             # ✅ AUTO-GENERATED
```

---

## 📄 Document Specifications

### 1. VSCode Setup Guide (`docs/setup/vscode-setup.md`)

**Purpose:** Complete guide for setting up CORTEX 4.0 in VSCode

**Auto-Generated From:**
- `src/core/ide_detector.py` (IDEDetector class)
- `cortex-brain/config/vscode.config.json` (CORTEX VSCode settings)
- MASTER-PLAN.md Section 1.5 Use Case 1 (Pure Python Project)
- `.vscode/` template examples

**Content Structure:**

```markdown
# CORTEX 4.0 VSCode Setup Guide

## Overview
{extracted from MASTER-PLAN Section 1.5}

## Prerequisites
- VSCode version 1.80+
- Python 3.8+
- Git 2.30+

## Installation Steps

### 1. Clone Repository
{step-by-step instructions}

### 2. Install Extensions
{auto-generated from extensions.json recommendations}

### 3. Configure VSCode Settings
{auto-generated from vscode.config.json with explanations}

### 4. Set Up CORTEX Brain
{brain initialization steps}

## Configuration Files

### `.vscode/settings.json`
{auto-generated example with inline comments}

### `.vscode/tasks.json`
{auto-generated CORTEX tasks}

### `.vscode/launch.json`
{debug configurations}

### `.vscode/extensions.json`
{recommended extensions}

## CORTEX-Specific Configuration

### `cortex-brain/config/vscode.config.json`
{auto-generated from schema with all settings explained}

## Verification
{checklist to verify setup}

## Troubleshooting
{common issues with resolutions}

## Next Steps
{links to relevant documentation}
```

**Auto-Generation Logic:**

```python
# cortex-toolkit/documentation/generators/ide_setup_generator.py

def generate_vscode_setup_guide() -> str:
    """Generate VSCode setup guide from multiple sources."""
    
    # 1. Extract overview from MASTER-PLAN
    overview = extract_section(
        file="cortex-brain/documents/planning/active/CORTEX-3.0-4.0/MASTER-PLAN.md",
        section="1.5. Cross-IDE Compatibility (VSCode + Visual Studio)"
    )
    
    # 2. Parse VSCode configuration schema
    vscode_config = parse_json_schema("cortex-brain/config/vscode.config.json")
    
    # 3. Generate configuration examples
    settings_example = generate_vscode_settings(vscode_config)
    tasks_example = generate_vscode_tasks()
    launch_example = generate_vscode_launch()
    extensions_example = generate_vscode_extensions()
    
    # 4. Extract troubleshooting from error logs
    troubleshooting = extract_common_errors(
        source="logs/ide-detection-errors.log",
        ide="vscode"
    )
    
    # 5. Render template
    return render_template(
        "ide_setup_template.md.j2",
        ide="vscode",
        overview=overview,
        config=vscode_config,
        settings=settings_example,
        tasks=tasks_example,
        launch=launch_example,
        extensions=extensions_example,
        troubleshooting=troubleshooting
    )
```

**Update Triggers:**
- `cortex-brain/config/vscode.config.json` modified → regenerate
- `src/core/ide_detector.py` modified → regenerate
- MASTER-PLAN.md Section 1.5 modified → regenerate

---

### 2. Visual Studio Setup Guide (`docs/setup/visualstudio-setup.md`)

**Purpose:** Complete guide for setting up CORTEX 4.0 in Visual Studio

**Auto-Generated From:**
- `src/core/ide_detector.py` (IDEDetector class)
- `cortex-brain/config/visualstudio.config.json` (CORTEX VS settings)
- MASTER-PLAN.md Section 1.5 Use Case 2 (C# Solution)
- `.vs/` template examples

**Content Structure:**

```markdown
# CORTEX 4.0 Visual Studio Setup Guide

## Overview
{extracted from MASTER-PLAN Section 1.5}

## Prerequisites
- Visual Studio 2022 (17.0+)
- .NET SDK 6.0+
- Python 3.8+ (for CORTEX orchestrators)
- Git 2.30+

## Installation Steps

### 1. Open Solution
{instructions for opening .sln files}

### 2. Configure CORTEX Integration
{.vs/cortex/ directory setup}

### 3. Install Extensions/Packages
{NuGet packages, VS extensions}

### 4. Set Up CORTEX Brain
{brain initialization steps}

## Configuration Files

### `.vs/cortex/settings.json`
{auto-generated example with inline comments}

### `.vs/cortex/tasks.json`
{CORTEX task definitions}

## CORTEX-Specific Configuration

### `cortex-brain/config/visualstudio.config.json`
{auto-generated from schema with all settings explained}

## Verification
{checklist to verify setup}

## Troubleshooting
{common issues with resolutions}

## Next Steps
{links to relevant documentation}
```

**Auto-Generation Logic:**

```python
def generate_visualstudio_setup_guide() -> str:
    """Generate Visual Studio setup guide from multiple sources."""
    
    # 1. Extract overview from MASTER-PLAN
    overview = extract_section(
        file="cortex-brain/documents/planning/active/CORTEX-3.0-4.0/MASTER-PLAN.md",
        section="1.5. Cross-IDE Compatibility (VSCode + Visual Studio)"
    )
    
    # 2. Parse Visual Studio configuration schema
    vs_config = parse_json_schema("cortex-brain/config/visualstudio.config.json")
    
    # 3. Generate configuration examples
    vs_settings_example = generate_vs_settings(vs_config)
    vs_tasks_example = generate_vs_tasks()
    
    # 4. Extract troubleshooting from error logs
    troubleshooting = extract_common_errors(
        source="logs/ide-detection-errors.log",
        ide="visualstudio"
    )
    
    # 5. Render template
    return render_template(
        "ide_setup_template.md.j2",
        ide="visualstudio",
        overview=overview,
        config=vs_config,
        settings=vs_settings_example,
        tasks=vs_tasks_example,
        troubleshooting=troubleshooting
    )
```

**Update Triggers:**
- `cortex-brain/config/visualstudio.config.json` modified → regenerate
- `src/core/ide_detector.py` modified → regenerate
- MASTER-PLAN.md Section 1.5 modified → regenerate

---

### 3. IDE Switching Workflow (`docs/setup/ide-switching.md`)

**Purpose:** Guide for switching IDEs mid-project without data loss

**Auto-Generated From:**
- MASTER-PLAN.md Section 1.5 Use Case 4 (Mid-Project IDE Switch)
- `src/core/ide_detector.py` (detection logic)
- `src/core/config_manager.py` (configuration inheritance)

**Content Structure:**

```markdown
# Switching IDEs Mid-Project

## Overview
{why you might switch, what's preserved, what's not}

## Scenario 1: VSCode → Visual Studio
{step-by-step instructions}

## Scenario 2: Visual Studio → VSCode
{step-by-step instructions}

## What Happens During a Switch

### Preserved
- ✅ CORTEX brain data (conversations, patterns, metrics)
- ✅ Git history
- ✅ Application code
- ✅ Configuration inheritance (shared.config.json)

### IDE-Specific (Not Preserved)
- ❌ `.vscode/` settings (VSCode-specific)
- ❌ `.vs/` settings (Visual Studio-specific)
- ❌ IDE workspace state

## Configuration Inheritance

### Priority Order
1. IDE-specific config (highest priority)
2. Shared config (fallback)
3. Default config (hardcoded)

{auto-generated diagram showing inheritance}

## Verification Checklist
{steps to verify switch was successful}

## Troubleshooting
{common issues during IDE switches}
```

**Auto-Generation Logic:**

```python
def generate_ide_switching_guide() -> str:
    """Generate IDE switching workflow guide."""
    
    # 1. Extract use case from MASTER-PLAN
    use_case = extract_use_case(
        file="cortex-brain/documents/planning/active/CORTEX-3.0-4.0/MASTER-PLAN.md",
        section="1.5",
        use_case=4
    )
    
    # 2. Generate configuration inheritance diagram
    inheritance_diagram = generate_config_inheritance_diagram(
        source="src/core/config_manager.py"
    )
    
    # 3. Extract preserved/not-preserved items from code
    preserved_items = extract_brain_persistence_logic(
        source="src/brain/brain_interface.py"
    )
    
    # 4. Render template
    return render_template(
        "ide_switching_template.md.j2",
        use_case=use_case,
        diagram=inheritance_diagram,
        preserved=preserved_items
    )
```

**Update Triggers:**
- MASTER-PLAN.md Section 1.5 Use Case 4 modified → regenerate
- `src/core/config_manager.py` modified → regenerate

---

### 4. IDE Detection Troubleshooting (`docs/setup/ide-detection-troubleshooting.md`)

**Purpose:** Diagnose and resolve IDE detection issues

**Auto-Generated From:**
- `logs/ide-detection-errors.log` (common error patterns)
- `src/core/ide_detector.py` (detection logic, error messages)
- GitHub issues tagged with `ide-detection`

**Content Structure:**

```markdown
# IDE Detection Troubleshooting

## How IDE Detection Works
{explanation of detection logic from IDEDetector}

## Detection Priority
1. Environment variables
2. Workspace markers (`.vscode/`, `.vs/`)
3. Fallback to UNKNOWN

## Common Issues

### Issue 1: CORTEX detects UNKNOWN IDE
**Symptoms:**
{extracted from error logs}

**Causes:**
{code analysis}

**Solutions:**
{step-by-step resolution}

### Issue 2: Wrong IDE detected
{similar structure}

### Issue 3: Configuration not loading
{similar structure}

## Diagnostic Commands

```bash
# Check IDE detection
cortex-toolkit ide detect

# Validate configuration
cortex-toolkit config validate --ide vscode

# Test configuration inheritance
cortex-toolkit config resolve --show-priority
```

## Manual Override
{how to force IDE detection}

## Report an Issue
{link to GitHub issues with template}
```

**Auto-Generation Logic:**

```python
def generate_ide_troubleshooting_guide() -> str:
    """Generate IDE detection troubleshooting guide."""
    
    # 1. Analyze error logs
    common_errors = analyze_error_patterns(
        source="logs/ide-detection-errors.log",
        min_occurrences=5
    )
    
    # 2. Extract detection logic from code
    detection_flow = extract_detection_logic(
        source="src/core/ide_detector.py",
        method="detect_current_ide"
    )
    
    # 3. Generate diagnostic commands
    diagnostic_commands = generate_diagnostic_commands()
    
    # 4. Extract solutions from resolved GitHub issues
    solutions = extract_github_issue_solutions(
        repo="asifhussain60/CORTEX",
        label="ide-detection",
        state="closed"
    )
    
    # 5. Render template
    return render_template(
        "troubleshooting_template.md.j2",
        errors=common_errors,
        detection_flow=detection_flow,
        commands=diagnostic_commands,
        solutions=solutions
    )
```

**Update Triggers:**
- `logs/ide-detection-errors.log` updated (weekly scan) → regenerate
- `src/core/ide_detector.py` modified → regenerate
- New GitHub issue closed with `ide-detection` label → regenerate

---

### 5. VSCode Configuration Reference (`docs/configuration/vscode-config-reference.md`)

**Purpose:** Complete reference for all VSCode CORTEX settings

**Auto-Generated From:**
- `cortex-brain/config/vscode.config.json` (configuration schema)
- `.vscode/settings.json` (example settings)
- `src/core/config_manager.py` (configuration resolution logic)

**Content Structure:**

```markdown
# VSCode Configuration Reference

## Overview
{explanation of CORTEX VSCode configuration}

## Configuration Files

### `.vscode/settings.json` (VSCode Editor Settings)
{auto-generated table of all settings}

### `cortex-brain/config/vscode.config.json` (CORTEX Settings)
{auto-generated table of all CORTEX settings}

## Configuration Table

| Setting | Type | Default | Description | Example |
|---------|------|---------|-------------|---------|
| `cortex.pythonPath` | string | `${workspaceFolder}/.venv/bin/python` | Path to Python interpreter | `"C:\\Python38\\python.exe"` |
| `cortex.autoSave` | boolean | `true` | Auto-save CORTEX state | `false` |
| ... | ... | ... | ... | ... |

## Path Resolution

### VSCode Variables
{auto-generated table of VSCode path variables}

### CORTEX Variable Expansion
{explanation of how CORTEX resolves ${workspaceFolder}}

## Examples

### Minimal Configuration
{auto-generated minimal example}

### Full Configuration
{auto-generated full example with all options}

### Multi-Repo Configuration
{example for multiple projects}

## Troubleshooting
{configuration-related issues}
```

**Auto-Generation Logic:**

```python
def generate_vscode_config_reference() -> str:
    """Generate VSCode configuration reference."""
    
    # 1. Parse configuration schema
    config_schema = parse_json_schema("cortex-brain/config/vscode.config.json")
    
    # 2. Extract default values
    defaults = extract_default_values(config_schema)
    
    # 3. Generate configuration table
    config_table = generate_config_table(
        schema=config_schema,
        defaults=defaults,
        include_examples=True
    )
    
    # 4. Extract path resolution logic
    path_resolution = extract_path_resolution_logic(
        source="src/core/config_manager.py",
        method="_resolve_paths",
        ide="vscode"
    )
    
    # 5. Generate examples
    minimal_example = generate_minimal_config("vscode")
    full_example = generate_full_config("vscode")
    
    # 6. Render template
    return render_template(
        "configuration_reference_template.md.j2",
        ide="vscode",
        schema=config_schema,
        table=config_table,
        path_resolution=path_resolution,
        minimal=minimal_example,
        full=full_example
    )
```

**Update Triggers:**
- `cortex-brain/config/vscode.config.json` modified → regenerate
- `src/core/config_manager.py` modified → regenerate

---

### 6. Visual Studio Configuration Reference (`docs/configuration/visualstudio-config-reference.md`)

**Purpose:** Complete reference for all Visual Studio CORTEX settings

**Auto-Generated From:**
- `cortex-brain/config/visualstudio.config.json` (configuration schema)
- `.vs/cortex/settings.json` (example settings)
- `src/core/config_manager.py` (configuration resolution logic)

**Content Structure:**

```markdown
# Visual Studio Configuration Reference

## Overview
{explanation of CORTEX Visual Studio configuration}

## Configuration Files

### `.vs/cortex/settings.json` (CORTEX Integration Settings)
{auto-generated table of all settings}

### `cortex-brain/config/visualstudio.config.json` (CORTEX Settings)
{auto-generated table of all CORTEX settings}

## Configuration Table

| Setting | Type | Default | Description | Example |
|---------|------|---------|-------------|---------|
| `CortexPythonPath` | string | `$(SolutionDir).venv\\Scripts\\python.exe` | Path to Python interpreter | `"C:\\Python38\\python.exe"` |
| `CortexAutoSave` | boolean | `true` | Auto-save CORTEX state | `false` |
| ... | ... | ... | ... | ... |

## Path Resolution

### Visual Studio Variables
{auto-generated table of VS path variables}

### CORTEX Variable Expansion
{explanation of how CORTEX resolves $(SolutionDir)}

## Examples

### Minimal Configuration
{auto-generated minimal example}

### Full Configuration
{auto-generated full example with all options}

### Multi-Solution Configuration
{example for multiple solutions}

## Troubleshooting
{configuration-related issues}
```

**Auto-Generation Logic:**

```python
def generate_visualstudio_config_reference() -> str:
    """Generate Visual Studio configuration reference."""
    
    # 1. Parse configuration schema
    config_schema = parse_json_schema("cortex-brain/config/visualstudio.config.json")
    
    # 2. Extract default values
    defaults = extract_default_values(config_schema)
    
    # 3. Generate configuration table
    config_table = generate_config_table(
        schema=config_schema,
        defaults=defaults,
        include_examples=True
    )
    
    # 4. Extract path resolution logic
    path_resolution = extract_path_resolution_logic(
        source="src/core/config_manager.py",
        method="_resolve_paths",
        ide="visualstudio"
    )
    
    # 5. Generate examples
    minimal_example = generate_minimal_config("visualstudio")
    full_example = generate_full_config("visualstudio")
    
    # 6. Render template
    return render_template(
        "configuration_reference_template.md.j2",
        ide="visualstudio",
        schema=config_schema,
        table=config_table,
        path_resolution=path_resolution,
        minimal=minimal_example,
        full=full_example
    )
```

**Update Triggers:**
- `cortex-brain/config/visualstudio.config.json` modified → regenerate
- `src/core/config_manager.py` modified → regenerate

---

### 7. CORTEX Brain Configuration (`docs/configuration/cortex-brain-config.md`)

**Purpose:** Complete reference for CORTEX brain configuration system

**Auto-Generated From:**
- `cortex-brain/config/shared.config.json` (shared configuration)
- `src/core/config_manager.py` (ConfigManager class)
- All IDE-specific configuration files

**Content Structure:**

```markdown
# CORTEX Brain Configuration

## Overview
{explanation of CORTEX configuration system}

## Configuration Hierarchy

### Priority Order
1. IDE-specific config (highest)
2. Shared config (fallback)
3. Default config (hardcoded)

{auto-generated diagram showing inheritance}

## Configuration Files

### `cortex-brain/config/shared.config.json`
{IDE-agnostic settings, used as fallback}

### `cortex-brain/config/vscode.config.json`
{VSCode-specific overrides}

### `cortex-brain/config/visualstudio.config.json`
{Visual Studio-specific overrides}

## Configuration Schema

### Brain Settings
{auto-generated table}

### Path Settings
{auto-generated table}

### Feature Flags
{auto-generated table}

## Configuration Inheritance Examples

### Example 1: Python Path Resolution
{step-by-step example showing inheritance}

### Example 2: IDE-Specific Override
{example showing override behavior}

## Programmatic Access

```python
from src.core.config_manager import ConfigManager

config = ConfigManager(workspace_root=Path.cwd())
python_path = config.get("pythonPath")
```

## Troubleshooting
{configuration-related issues}
```

**Auto-Generation Logic:**

```python
def generate_cortex_brain_config_reference() -> str:
    """Generate CORTEX brain configuration reference."""
    
    # 1. Parse all configuration schemas
    shared_config = parse_json_schema("cortex-brain/config/shared.config.json")
    vscode_config = parse_json_schema("cortex-brain/config/vscode.config.json")
    vs_config = parse_json_schema("cortex-brain/config/visualstudio.config.json")
    
    # 2. Generate inheritance diagram
    inheritance_diagram = generate_config_inheritance_diagram(
        source="src/core/config_manager.py",
        method="_load_config"
    )
    
    # 3. Extract configuration resolution examples
    examples = extract_config_resolution_examples(
        source="src/core/config_manager.py"
    )
    
    # 4. Generate configuration tables
    brain_settings = generate_config_table(shared_config, category="brain")
    path_settings = generate_config_table(shared_config, category="paths")
    feature_flags = generate_config_table(shared_config, category="features")
    
    # 5. Render template
    return render_template(
        "brain_config_template.md.j2",
        shared=shared_config,
        vscode=vscode_config,
        visualstudio=vs_config,
        inheritance=inheritance_diagram,
        examples=examples,
        brain_settings=brain_settings,
        path_settings=path_settings,
        feature_flags=feature_flags
    )
```

**Update Triggers:**
- Any `cortex-brain/config/*.json` file modified → regenerate
- `src/core/config_manager.py` modified → regenerate

---

### 8. IDE Compatibility Architecture (`docs/architecture/ide-compatibility.md`)

**Purpose:** Architectural overview of CORTEX IDE compatibility system

**Auto-Generated From:**
- MASTER-PLAN.md Section 1.5 (entire section)
- `src/core/ide_detector.py` (class documentation)
- `src/core/config_manager.py` (class documentation)

**Content Structure:**

```markdown
# IDE Compatibility Architecture

## Overview
{extracted from MASTER-PLAN Section 1.5}

## Design Philosophy
{5 principles from MASTER-PLAN}

## Architecture Diagram
{auto-generated D3.js diagram showing components}

## File Structure
{intelligent file separation diagram}

## Core Components

### IDEDetector
{class documentation from ide_detector.py}

### ConfigManager
{class documentation from config_manager.py}

## Use Cases

### Use Case 1: Pure Python Project (VSCode)
{extracted from MASTER-PLAN}

### Use Case 2: C# Solution (Visual Studio)
{extracted from MASTER-PLAN}

### Use Case 3: Full-Stack (VSCode + Visual Studio)
{extracted from MASTER-PLAN}

### Use Case 4: Mid-Project IDE Switch
{extracted from MASTER-PLAN}

## Benefits
{extracted from MASTER-PLAN}

## Implementation Status
{extracted from checklist}

## Performance Impact
{<0.01s startup overhead}
```

**Auto-Generation Logic:**

```python
def generate_ide_compatibility_architecture() -> str:
    """Generate IDE compatibility architecture documentation."""
    
    # 1. Extract entire Section 1.5 from MASTER-PLAN
    section = extract_section(
        file="cortex-brain/documents/planning/active/CORTEX-3.0-4.0/MASTER-PLAN.md",
        section="1.5"
    )
    
    # 2. Parse class documentation
    ide_detector_docs = extract_class_documentation(
        source="src/core/ide_detector.py",
        class_name="IDEDetector"
    )
    config_manager_docs = extract_class_documentation(
        source="src/core/config_manager.py",
        class_name="ConfigManager"
    )
    
    # 3. Generate architecture diagram
    architecture_diagram = generate_architecture_diagram(
        components=["IDEDetector", "ConfigManager", "Brain", ".vscode/", ".vs/"],
        relationships="auto"
    )
    
    # 4. Extract use cases
    use_cases = extract_use_cases(section)
    
    # 5. Render template
    return render_template(
        "architecture_template.md.j2",
        overview=section["overview"],
        philosophy=section["philosophy"],
        diagram=architecture_diagram,
        ide_detector=ide_detector_docs,
        config_manager=config_manager_docs,
        use_cases=use_cases,
        benefits=section["benefits"]
    )
```

**Update Triggers:**
- MASTER-PLAN.md Section 1.5 modified → regenerate
- `src/core/ide_detector.py` modified → regenerate
- `src/core/config_manager.py` modified → regenerate

---

### 9. IDE Detection System (`docs/architecture/ide-detection-system.md`)

**Purpose:** Technical documentation for IDEDetector class

**Auto-Generated From:**
- `src/core/ide_detector.py` (complete class documentation)
- Code annotations and docstrings

**Content Structure:**

```markdown
# IDE Detection System

## Overview
{class-level docstring}

## Class Diagram
{auto-generated D3.js class diagram}

## Detection Flow
{auto-generated flowchart from detect_current_ide method}

## API Reference

### IDEType Enum
{auto-generated from enum}

### Methods

#### `detect_current_ide() -> IDEType`
{method documentation}

#### `get_config_path(base_path: Path, ide: IDEType) -> Path`
{method documentation}

#### `get_settings_template(ide: IDEType) -> dict`
{method documentation}

## Environment Variables

### VSCode Detection
{table of environment variables}

### Visual Studio Detection
{table of environment variables}

## Workspace Markers

### VSCode Markers
{.vscode/ directory structure}

### Visual Studio Markers
{.sln files, .vs/ directory}

## Examples

### Example 1: Detect IDE in current workspace
```python
from src.core.ide_detector import IDEDetector

ide = IDEDetector.detect_current_ide()
print(f"Detected IDE: {ide.value}")
```

### Example 2: Get configuration path
{code example}

## Testing
{links to test files}

## Performance
{detection time benchmarks}
```

**Auto-Generation Logic:**

```python
def generate_ide_detection_system_docs() -> str:
    """Generate IDE detection system documentation."""
    
    # 1. Parse IDEDetector class
    class_docs = parse_class(
        source="src/core/ide_detector.py",
        class_name="IDEDetector"
    )
    
    # 2. Generate class diagram
    class_diagram = generate_class_diagram(
        source="src/core/ide_detector.py",
        diagram_type="d3-hierarchy"
    )
    
    # 3. Generate detection flowchart
    detection_flow = generate_flowchart_from_method(
        source="src/core/ide_detector.py",
        method="detect_current_ide"
    )
    
    # 4. Extract method documentation
    methods = extract_method_documentation(class_docs)
    
    # 5. Extract environment variables from code
    env_vars = extract_environment_variables(
        source="src/core/ide_detector.py"
    )
    
    # 6. Generate code examples
    examples = generate_code_examples(class_docs)
    
    # 7. Render template
    return render_template(
        "class_documentation_template.md.j2",
        class_docs=class_docs,
        class_diagram=class_diagram,
        detection_flow=detection_flow,
        methods=methods,
        env_vars=env_vars,
        examples=examples
    )
```

**Update Triggers:**
- `src/core/ide_detector.py` modified → regenerate
- Test files updated → update testing section

---

## 🔧 Implementation Details

### Phase 1.5 Integration (Week 3)

**File:** `cortex-toolkit/documentation/generators/ide_documentation_generator.py`

```python
"""IDE-specific documentation generator.

Generates comprehensive IDE setup and configuration documentation
for VSCode and Visual Studio from code, configuration files, and
MASTER-PLAN specifications.
"""

from pathlib import Path
from typing import Dict, List
from .base_generator import BaseDocumentationGenerator

class IDEDocumentationGenerator(BaseDocumentationGenerator):
    """Generate IDE-specific documentation."""
    
    def __init__(self, cortex_root: Path):
        super().__init__(cortex_root)
        self.master_plan = cortex_root / "cortex-brain/documents/planning/active/CORTEX-3.0-4.0/MASTER-PLAN.md"
        self.ide_detector = cortex_root / "src/core/ide_detector.py"
        self.config_manager = cortex_root / "src/core/config_manager.py"
    
    def generate_all(self) -> Dict[str, str]:
        """Generate all IDE documentation."""
        return {
            "setup/vscode-setup.md": self.generate_vscode_setup_guide(),
            "setup/visualstudio-setup.md": self.generate_visualstudio_setup_guide(),
            "setup/ide-switching.md": self.generate_ide_switching_guide(),
            "setup/ide-detection-troubleshooting.md": self.generate_ide_troubleshooting_guide(),
            "configuration/vscode-config-reference.md": self.generate_vscode_config_reference(),
            "configuration/visualstudio-config-reference.md": self.generate_visualstudio_config_reference(),
            "configuration/cortex-brain-config.md": self.generate_cortex_brain_config_reference(),
            "architecture/ide-compatibility.md": self.generate_ide_compatibility_architecture(),
            "architecture/ide-detection-system.md": self.generate_ide_detection_system_docs()
        }
    
    # ... implementation of each generate_* method
```

### CLI Integration

```bash
# Generate all IDE documentation
cortex-toolkit docs generate --category ide

# Generate specific IDE documentation
cortex-toolkit docs generate --document setup/vscode-setup.md

# Validate generated documentation
cortex-toolkit docs validate --category ide

# Watch for changes and auto-regenerate
cortex-toolkit docs watch --category ide
```

### CI/CD Integration

```yaml
# .github/workflows/documentation.yml

name: Documentation

on:
  push:
    paths:
      - 'src/core/ide_detector.py'
      - 'src/core/config_manager.py'
      - 'cortex-brain/config/*.json'
      - 'cortex-brain/documents/planning/active/CORTEX-3.0-4.0/MASTER-PLAN.md'

jobs:
  regenerate-docs:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Regenerate IDE documentation
        run: cortex-toolkit docs generate --category ide --validate
      - name: Commit changes
        run: |
          git config --global user.name 'CORTEX Documentation Bot'
          git config --global user.email 'bot@cortex.ai'
          git add docs/
          git commit -m "docs: Auto-regenerate IDE documentation [skip ci]"
          git push
```

---

## 📊 Quality Assurance

### Validation Checks

1. **Link Validation:**
   - All internal links resolve correctly
   - All external links return 200 status
   - No broken references to code files

2. **Code Example Validation:**
   - All Python examples compile
   - All configuration examples validate against schema
   - All CLI commands execute successfully

3. **Diagram Validation:**
   - All D3.js diagrams render correctly
   - All diagrams have alt text for accessibility
   - All diagrams export to PDF correctly

4. **Completeness:**
   - All 9 documents generated
   - All sections populated (no TODO markers)
   - All configuration options documented

### Testing Strategy

```python
# tests/documentation/test_ide_documentation_generator.py

def test_generate_all_ide_docs():
    """Test generation of all IDE documentation."""
    generator = IDEDocumentationGenerator(cortex_root=Path("/path/to/cortex"))
    docs = generator.generate_all()
    
    assert len(docs) == 9
    assert "setup/vscode-setup.md" in docs
    assert "architecture/ide-detection-system.md" in docs

def test_vscode_setup_guide_completeness():
    """Test VSCode setup guide has all required sections."""
    doc = generator.generate_vscode_setup_guide()
    
    assert "## Prerequisites" in doc
    assert "## Installation Steps" in doc
    assert "## Configuration Files" in doc
    assert "## Verification" in doc
    assert "## Troubleshooting" in doc

def test_config_reference_tables():
    """Test configuration reference tables are properly formatted."""
    doc = generator.generate_vscode_config_reference()
    
    assert "| Setting | Type | Default | Description | Example |" in doc
    assert "`cortex.pythonPath`" in doc
    assert "`cortex.autoSave`" in doc
```

---

## 📅 Timeline

**Phase 1.5 (Week 3):**
- Days 1-2: Implement IDEDocumentationGenerator class
- Day 3: Implement generation methods (9 documents)
- Day 4: Add CLI integration and validation
- Day 5: Testing and documentation

**Phase 6 (Week 18):**
- Day 2: Generate all IDE documentation
- Day 4: Include IDE docs in supporting documentation
- Day 5: Validate IDE documentation in final review

---

## ✅ Success Criteria

- ✅ All 9 IDE documentation files auto-generate correctly
- ✅ Documentation updates automatically when source changes
- ✅ All code examples validate successfully
- ✅ All configuration tables complete with defaults and descriptions
- ✅ All diagrams render correctly (D3.js + PDF export)
- ✅ Zero broken links
- ✅ CI/CD pipeline auto-regenerates on changes
- ✅ Documentation accessible from CORTEX 4.0 documentation site

---

**Status:** 🟢 READY FOR IMPLEMENTATION  
**Next Step:** Implement in Phase 1.5 (Week 3)

