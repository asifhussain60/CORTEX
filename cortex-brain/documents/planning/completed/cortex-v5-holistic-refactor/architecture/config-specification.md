# Config-Only Manifest Specification

**Document Type:** Technical Specification  
**Plan:** CORTEX v5.0 Holistic Refactor  
**Created:** January 2, 2026

---

## 🎯 Purpose

Define the structure of pure configuration manifests that contain ZERO natural language instructions and ONLY machine-readable data structures.

---

## 📐 Core Principles

1. **No Imperative Language** - No "Search the workspace", "Create a file", "Execute command"
2. **Data Only** - YAML/JSON structures describing WHAT, not HOW
3. **Python Interprets** - Orchestrator code reads config and decides execution
4. **Schema Validation** - All manifests validate against JSON Schema
5. **Version Control** - Semantic versioning for manifest format

---

## 📄 Manifest Structure

### Top-Level Schema

```yaml
# Orchestrator metadata
orchestrator:
  name: string                      # Unique identifier (e.g., "planning_system")
  version: string                   # Semantic version (e.g., "5.0.0")
  type: enum[autonomous, guided]    # Execution model
  base_class: string                # Python class (e.g., "BaseOrchestratorV41")

# Human-readable info
metadata:
  description: string               # What this orchestrator does
  author: string                    # Creator/maintainer
  created: date                     # Creation date (ISO 8601)
  updated: date                     # Last update (ISO 8601)
  response_template: string         # Template name from response-templates-v4.yaml
  documentation_url: string         # Link to docs

# Folder structure to create
folder_structure:
  root: string                      # Path with {placeholders}
  subfolders: array[FolderSpec]     # List of folders to create
  file_templates: array[FileSpec]   # Initial files to generate

# Execution phases
phases: array[PhaseSpec]            # Ordered list of phases

# Output generation
templates: object                   # Key-value pairs of template names to paths
validation_schemas: object          # Key-value pairs of schema names to paths

# Database configuration
database:
  connection: string                # Path to SQLite database
  tables: array[string]             # Tables used by this orchestrator
```

---

## 📦 Sub-Schemas

### FolderSpec

```yaml
name: string                        # Folder name
description: string                 # Purpose of folder
required: boolean                   # Must exist for plan to be valid
permissions: string                 # Unix-style permissions (optional)
```

**Example:**
```yaml
folder_structure:
  root: "cortex-brain/documents/planning/active/{plan_name}/"
  subfolders:
    - name: "context"
      description: "Discovery artifacts and workspace analysis"
      required: true
    - name: "artifacts"
      description: "Generated code, config, and implementation files"
      required: true
    - name: "reports"
      description: "Progress reports and status summaries"
      required: false
    - name: "tracking"
      description: "State database snapshots and progress JSON"
      required: true
```

### FileSpec

```yaml
path: string                        # Relative path within plan folder
template: string                    # Template file to use
context_sources: array[string]      # Where to get data for template
required: boolean                   # Must be generated
```

**Example:**
```yaml
file_templates:
  - path: "00-MASTER-PLAN-V5.md"
    template: "templates/master-plan-v5.jinja2"
    context_sources:
      - "context/discovery-summary.md"
      - "architecture/structure.json"
    required: true
  - path: "README.md"
    template: "templates/plan-readme.jinja2"
    required: true
```

### PhaseSpec

```yaml
id: string                          # Unique phase identifier
order: integer                      # Execution order (0-based)
name: string                        # Human-readable name
description: string                 # Purpose of phase
dependencies: array[string]         # Phase IDs that must complete first
estimated_duration_hours: float     # Time estimate

# What to search/analyze
search_patterns: array[SearchPattern]
analysis_targets: array[AnalysisTarget]

# What to generate
output_artifacts: array[OutputArtifact]

# Validation checks
validations: array[ValidationCheck]

# Conditional execution
skip_if: string                     # Condition expression (e.g., "file_exists('output.md')")
```

**Example:**
```yaml
phases:
  - id: "discovery"
    order: 1
    name: "Workspace Discovery"
    description: "Search workspace for relevant code and documentation"
    estimated_duration_hours: 2.0
    
    search_patterns:
      - pattern: "class.*Controller"
        scope: "src/**/*.py"
        output_file: "context/controllers.md"
        format: "markdown_list"
      
      - pattern: "def test_"
        scope: "tests/**/*.py"
        output_file: "context/tests.md"
        format: "markdown_table"
    
    validations:
      - name: "context_complete"
        check: "file_exists"
        path: "context/controllers.md"
      - name: "minimum_findings"
        check: "line_count_gt"
        path: "context/controllers.md"
        threshold: 5
    
    output_artifacts:
      - type: "context_summary"
        template: "templates/discovery-summary.jinja2"
        output_path: "context/discovery-summary.md"
        context_sources:
          - "context/controllers.md"
          - "context/tests.md"
```

### SearchPattern

```yaml
pattern: string                     # Regex or glob pattern
scope: string                       # File glob (e.g., "src/**/*.py")
output_file: string                 # Where to write results
format: enum[json, markdown_list, markdown_table, yaml]
max_results: integer                # Limit results (optional)
exclude_patterns: array[string]     # Patterns to exclude (optional)
```

### AnalysisTarget

```yaml
type: enum[ast_parse, ast_metrics, file_stats, dependency_graph]
files: string                       # File glob pattern
output_file: string                 # Where to write analysis
options: object                     # Type-specific options
```

**Example:**
```yaml
analysis_targets:
  - type: "ast_parse"
    files: "src/**/*.py"
    output_file: "architecture/structure.json"
    options:
      include_docstrings: true
      include_type_hints: true
  
  - type: "dependency_graph"
    files: "src/**/*.py"
    output_file: "architecture/dependencies.dot"
    options:
      format: "graphviz"
```

### OutputArtifact

```yaml
type: enum[context, report, code, config, documentation, test]
template: string                    # Jinja2 template path
output_path: string                 # Where to write output
context_sources: array[string]      # Data sources for template
format: enum[markdown, json, yaml, python, html]
```

### ValidationCheck

```yaml
name: string                        # Check identifier
check: enum[file_exists, json_schema, markdown_headers, test_pass, line_count_gt, custom]
path: string                        # File to check (optional)
schema: string                      # Schema file (for json_schema check)
required_sections: array[string]    # For markdown_headers check
threshold: integer                  # For line_count_gt check
custom_validator: string            # Python function name (for custom check)
```

**Example:**
```yaml
validations:
  - name: "plan_complete"
    check: "markdown_headers"
    path: "00-MASTER-PLAN-V5.md"
    required_sections:
      - "Executive Summary"
      - "Visual Progress Tracker"
      - "Implementation Strategy"
      - "Success Criteria"
  
  - name: "structure_valid"
    check: "json_schema"
    path: "architecture/structure.json"
    schema: "schemas/ast-structure.json"
  
  - name: "tests_present"
    check: "file_exists"
    path: "tests/test_orchestrator.py"
```

---

## 🔧 Python Interpretation

### How Orchestrator Reads Config

```python
class PlanningOrchestratorV5(BaseOrchestratorV41):
    def execute_phase(self, phase_config: dict):
        """Execute a phase based on pure config data"""
        
        # 1. Execute search patterns
        for pattern in phase_config.get('search_patterns', []):
            results = self._execute_search(
                pattern=pattern['pattern'],
                scope=pattern['scope'],
                max_results=pattern.get('max_results')
            )
            self._write_output(
                results, 
                pattern['output_file'], 
                format=pattern['format']
            )
        
        # 2. Execute analysis targets
        for target in phase_config.get('analysis_targets', []):
            if target['type'] == 'ast_parse':
                analysis = self._ast_parse(
                    target['files'], 
                    **target.get('options', {})
                )
            elif target['type'] == 'dependency_graph':
                analysis = self._build_dependency_graph(
                    target['files'],
                    **target.get('options', {})
                )
            self._write_output(analysis, target['output_file'])
        
        # 3. Generate output artifacts
        for artifact in phase_config.get('output_artifacts', []):
            context = self._load_context_sources(artifact['context_sources'])
            output = self._render_template(
                template=artifact['template'],
                context=context
            )
            self._write_file(artifact['output_path'], output)
        
        # 4. Run validations
        for validation in phase_config.get('validations', []):
            result = self._validate(
                check_type=validation['check'],
                **validation
            )
            self._record_validation(validation['name'], result)
```

### No Interpretation of Instructions

❌ **WRONG (Hybrid):**
```python
# Orchestrator reads instructions and interprets them
instructions = phase_config['instructions']
if "search the workspace" in instructions:
    # Try to parse natural language
    self._search_workspace()
```

✅ **CORRECT (Pure Config):**
```python
# Orchestrator reads structured data
for search in phase_config['search_patterns']:
    self._execute_search(
        pattern=search['pattern'],
        scope=search['scope']
    )
```

---

## 📋 Complete Example Manifest

```yaml
orchestrator:
  name: "planning_system"
  version: "5.0.0"
  type: "autonomous"
  base_class: "BaseOrchestratorV41"

metadata:
  description: "Pure autonomous planning orchestrator"
  author: "CORTEX v5.0"
  created: "2026-01-02"
  response_template: "autonomous_execution_progress"
  documentation_url: "https://asifhussain60.github.io/CORTEX/orchestrators/planning"

folder_structure:
  root: "cortex-brain/documents/planning/active/{plan_name}/"
  subfolders:
    - name: "context"
      description: "Discovery artifacts"
      required: true
    - name: "artifacts"
      description: "Generated code/config"
      required: true
    - name: "reports"
      description: "Progress reports"
      required: false
    - name: "tracking"
      description: "State snapshots"
      required: true
    - name: "phases"
      description: "Phase-specific details"
      required: false
    - name: "architecture"
      description: "Architecture decisions"
      required: false
    - name: "future-structure"
      description: "Implementation code"
      required: false

phases:
  - id: "discovery"
    order: 1
    name: "Workspace Discovery"
    description: "Search workspace for relevant code"
    estimated_duration_hours: 2.0
    
    search_patterns:
      - pattern: "class.*"
        scope: "src/**/*.py"
        output_file: "context/classes.md"
        format: "markdown_list"
        max_results: 100
    
    validations:
      - name: "context_complete"
        check: "file_exists"
        path: "context/classes.md"
    
    output_artifacts:
      - type: "context_summary"
        template: "templates/discovery-summary.jinja2"
        output_path: "context/discovery-summary.md"
        context_sources:
          - "context/classes.md"

  - id: "architecture_analysis"
    order: 2
    name: "Architecture Analysis"
    description: "Parse code structure"
    dependencies: ["discovery"]
    estimated_duration_hours: 1.5
    
    analysis_targets:
      - type: "ast_parse"
        files: "src/**/*.py"
        output_file: "architecture/structure.json"
        options:
          include_docstrings: true
    
    validations:
      - name: "ast_valid"
        check: "json_schema"
        path: "architecture/structure.json"
        schema: "schemas/ast-structure.json"

  - id: "plan_generation"
    order: 3
    name: "Plan Generation"
    description: "Generate master plan document"
    dependencies: ["discovery", "architecture_analysis"]
    estimated_duration_hours: 1.0
    
    output_artifacts:
      - type: "documentation"
        template: "templates/master-plan-v5.jinja2"
        output_path: "00-MASTER-PLAN-V5.md"
        context_sources:
          - "context/discovery-summary.md"
          - "architecture/structure.json"
        format: "markdown"
    
    validations:
      - name: "plan_complete"
        check: "markdown_headers"
        path: "00-MASTER-PLAN-V5.md"
        required_sections:
          - "Executive Summary"
          - "Visual Progress Tracker"
          - "Implementation Strategy"

templates:
  discovery_summary: "templates/discovery-summary.jinja2"
  master_plan: "templates/master-plan-v5.jinja2"
  progress_report: "templates/progress-report.jinja2"

validation_schemas:
  ast_structure: "schemas/ast-structure.json"
  plan_metadata: "schemas/plan-metadata.json"

database:
  connection: "cortex-brain/database/planning_state.db"
  tables:
    - plans
    - phases
    - tasks
    - artifacts
    - validations
    - state_snapshots
```

---

## ✅ Validation Rules

All manifests MUST:
1. Validate against `schemas/manifest-v5.json`
2. Have semantic version in orchestrator.version
3. Specify response_template in metadata
4. Define at least one phase
5. Include validations for each phase
6. Reference existing templates
7. Not contain natural language instructions
8. Not contain imperative commands

**Validation Script:**
```python
# validate_manifest.py
import yaml
import jsonschema

def validate_manifest(manifest_path: Path):
    with open(manifest_path) as f:
        manifest = yaml.safe_load(f)
    
    # Load schema
    with open("schemas/manifest-v5.json") as f:
        schema = json.load(f)
    
    # Validate structure
    jsonschema.validate(manifest, schema)
    
    # Check for forbidden patterns
    manifest_str = yaml.dump(manifest)
    forbidden = [
        "search the workspace",
        "create a file",
        "execute command",
        "run the following",
        "implement",
        "build",
        "generate"
    ]
    
    for phrase in forbidden:
        if phrase.lower() in manifest_str.lower():
            raise ValueError(f"Manifest contains forbidden imperative: '{phrase}'")
    
    print(f"✅ Manifest valid: {manifest_path}")
```

---

## 📚 References

- JSON Schema specification: https://json-schema.org/
- YAML 1.2 specification: https://yaml.org/spec/1.2/spec.html
- Jinja2 template engine: https://jinja.palletsprojects.com/
- Manifest validation script: `future-structure/scripts/validate_manifest.py`
- Example manifests: `future-structure/cortex-brain/manifests/orchestrators/`
