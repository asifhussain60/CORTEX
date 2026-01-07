# Config-Only Manifest Specification

**Version:** 5.0  
**Date:** January 2, 2026  
**Purpose:** Define machine-readable configuration format for AUTONOMOUS orchestrators

---

## 🎯 Design Principles

1. **Zero Natural Language** - No imperative instructions or commands
2. **Pure Data Structures** - Only YAML/JSON configuration
3. **Schema-Validated** - All configs must pass validation before execution
4. **Template-Driven** - Output generation uses Jinja2 templates
5. **Python Reads Config** - Orchestrator code interprets configuration

---

## 📋 Manifest Structure

### Top-Level Schema

```yaml
orchestrator:
  name: string              # e.g., "planning_system"
  version: string           # e.g., "5.0"
  type: string              # "autonomous" | "guided"
  description: string       # Human-readable description
  entry_point: string       # Python class name
  
metadata:
  author: string
  created: date
  updated: date
  complexity_tier: integer  # 1-5
  estimated_duration_days: integer
  
phases:
  - id: string
    name: string
    order: integer
    estimated_hours: float
    dependencies: [string]  # phase_ids
    tasks: [Task]
    validations: [Validation]
    templates: [Template]
    search_patterns: [SearchPattern]
    output_artifacts: [OutputArtifact]
    
folder_structure:
  root: string              # Path template with {variables}
  subfolders: [string]
  
output_formats:
  [artifact_type]: string   # Path to Jinja2 template
  
validation_schemas:
  [check_type]: object      # JSON schema for validation
  
config:
  [key]: value              # Orchestrator-specific settings
```

---

## 🏗️ Phase Configuration

### Phase Definition

```yaml
phases:
  - id: "discovery"
    name: "Context Discovery & Architecture Analysis"
    order: 1
    estimated_hours: 2.0
    dependencies: []
    
    # Tasks within phase (metadata only)
    tasks:
      - id: "search_workspace"
        description: "Search workspace for relevant patterns"
        estimated_minutes: 20
        
      - id: "analyze_structure"
        description: "Analyze code architecture"
        estimated_minutes: 30
        
      - id: "extract_dependencies"
        description: "Extract dependency graph"
        estimated_minutes: 25
    
    # Search patterns for context discovery
    search_patterns:
      - name: "controllers"
        pattern: "class.*Controller"
        file_types: ["*.py"]
        scope: "src/"
        max_results: 100
        
      - name: "tests"
        pattern: "def test_"
        file_types: ["*.py"]
        scope: "tests/"
        max_results: 200
    
    # Output artifacts generated
    output_artifacts:
      - type: "context_summary"
        template: "discovery-context.jinja2"
        output_path: "context/discovery-summary.md"
        
      - type: "architecture_diagram"
        template: "architecture-mermaid.jinja2"
        output_path: "artifacts/architecture.md"
    
    # Validation checks
    validations:
      - check_name: "context_files_found"
        check_type: "file_count"
        expected:
          min: 5
          max: 1000
        error_message: "Insufficient context files discovered"
        
      - check_name: "architecture_valid"
        check_type: "schema"
        schema_ref: "architecture_schema"
        error_message: "Architecture analysis failed validation"
```

### Python Orchestrator Reads Config

```python
def execute_phase(phase_config: dict):
    # Read search patterns from config
    for pattern in phase_config['search_patterns']:
        results = workspace_search(
            pattern=pattern['pattern'],
            file_types=pattern['file_types'],
            scope=pattern['scope'],
            max_results=pattern['max_results']
        )
        context[pattern['name']] = results
    
    # Generate outputs using templates
    for artifact in phase_config['output_artifacts']:
        template = load_template(artifact['template'])
        output = template.render(context=context)
        write_file(artifact['output_path'], output)
    
    # Run validations
    for validation in phase_config['validations']:
        result = validate(validation, context)
        if not result.passed:
            raise ValidationError(validation['error_message'])
```

---

## 🔍 Search Pattern Configuration

### Pattern Types

```yaml
search_patterns:
  # 1. Code Pattern (regex)
  - name: "api_endpoints"
    pattern: "@app\\.route\\("
    file_types: ["*.py"]
    scope: "src/api/"
    case_sensitive: false
    
  # 2. File Pattern (glob)
  - name: "config_files"
    file_pattern: "*.config.{json,yaml}"
    scope: "**/"
    recursive: true
    
  # 3. Semantic Search
  - name: "authentication_code"
    semantic_query: "user authentication and authorization logic"
    file_types: ["*.py", "*.js"]
    scope: "src/"
    max_results: 50
    
  # 4. AST Query (Python-specific)
  - name: "class_definitions"
    ast_query:
      node_type: "ClassDef"
      decorators: ["dataclass", "attrs"]
    scope: "src/models/"
```

### Python Implementation

```python
def execute_search_pattern(pattern: dict) -> list:
    if 'pattern' in pattern:
        # Regex search
        return grep_search(
            pattern=pattern['pattern'],
            file_types=pattern['file_types'],
            scope=pattern['scope']
        )
    elif 'file_pattern' in pattern:
        # File glob
        return file_search(
            pattern=pattern['file_pattern'],
            recursive=pattern.get('recursive', True)
        )
    elif 'semantic_query' in pattern:
        # Semantic search
        return semantic_search(
            query=pattern['semantic_query'],
            file_types=pattern['file_types']
        )
    elif 'ast_query' in pattern:
        # AST parsing
        return ast_search(
            node_type=pattern['ast_query']['node_type'],
            filters=pattern['ast_query']
        )
```

---

## 📄 Template Configuration

### Output Templates

```yaml
output_formats:
  # Master plan template
  master_plan:
    template: "templates/planning/master-plan.jinja2"
    output_path: "00-MASTER-PLAN.md"
    context_required:
      - "feature_name"
      - "complexity_tier"
      - "phases"
      - "total_tasks"
      
  # Progress tracker
  progress_tracker:
    template: "templates/planning/progress-tracker.json.jinja2"
    output_path: "tracking/progress-tracker.json"
    context_required:
      - "plan_metadata"
      - "phases"
      - "overall_progress"
      
  # Context summary
  context_summary:
    template: "templates/planning/context-summary.jinja2"
    output_path: "context/discovery-summary.md"
    context_required:
      - "discovered_files"
      - "architecture_analysis"
      - "dependencies"
```

### Jinja2 Template Example

```jinja2
# {{ feature_name | title }} - Master Plan

**Created:** {{ created_at }}
**Complexity Tier:** {{ complexity_tier }}
**Estimated Duration:** {{ estimated_days }} days

## Phases

{% for phase in phases %}
### Phase {{ phase.order }}: {{ phase.name }}

**Estimated Hours:** {{ phase.estimated_hours }}

**Tasks:**
{% for task in phase.tasks %}
- [ ] {{ task.description }} ({{ task.estimated_minutes }}m)
{% endfor %}

**Validations:**
{% for validation in phase.validations %}
- ✅ {{ validation.check_name }}: {{ validation.error_message }}
{% endfor %}

{% endfor %}
```

---

## ✅ Validation Configuration

### Validation Types

```yaml
validations:
  # 1. File Existence
  - check_name: "master_plan_created"
    check_type: "file_exists"
    file_path: "00-MASTER-PLAN.md"
    error_message: "Master plan file not generated"
    
  # 2. Folder Structure
  - check_name: "folders_created"
    check_type: "folder_structure"
    expected_folders:
      - "context"
      - "artifacts"
      - "reports"
      - "tracking"
    error_message: "Required folders missing"
    
  # 3. File Count
  - check_name: "sufficient_context"
    check_type: "file_count"
    folder: "context"
    min: 1
    max: 100
    error_message: "Insufficient context files"
    
  # 4. JSON Schema
  - check_name: "progress_tracker_valid"
    check_type: "json_schema"
    file_path: "tracking/progress-tracker.json"
    schema_ref: "progress_tracker_schema"
    error_message: "Progress tracker schema invalid"
    
  # 5. Custom Validation
  - check_name: "phase_consistency"
    check_type: "custom"
    validator: "validate_phase_consistency"
    error_message: "Phase definitions inconsistent"
```

### Python Validation Implementation

```python
def run_validation(validation: dict, context: dict) -> ValidationResult:
    check_type = validation['check_type']
    
    if check_type == 'file_exists':
        passed = os.path.exists(validation['file_path'])
        
    elif check_type == 'folder_structure':
        passed = all(
            os.path.exists(folder)
            for folder in validation['expected_folders']
        )
        
    elif check_type == 'file_count':
        count = len(os.listdir(validation['folder']))
        passed = validation['min'] <= count <= validation['max']
        
    elif check_type == 'json_schema':
        data = load_json(validation['file_path'])
        schema = load_schema(validation['schema_ref'])
        passed = validate_json_schema(data, schema)
        
    elif check_type == 'custom':
        validator_fn = getattr(validators, validation['validator'])
        passed = validator_fn(context)
    
    return ValidationResult(
        passed=passed,
        error_message=validation['error_message'] if not passed else None
    )
```

---

## 📁 Folder Structure Configuration

### Structure Template

```yaml
folder_structure:
  # Root path with variable substitution
  root: "cortex-brain/documents/planning/active/{plan_name}/"
  
  # Subfolders to create
  subfolders:
    - "context"
    - "artifacts"
    - "reports"
    - "tracking"
    - "architecture"
    
  # File templates to generate
  files:
    - path: "00-MASTER-PLAN.md"
      template: "master-plan.jinja2"
      
    - path: "tracking/progress-tracker.json"
      template: "progress-tracker.json.jinja2"
      
    - path: "README.md"
      template: "plan-readme.jinja2"
```

### Python Implementation

```python
def create_folder_structure(config: dict, variables: dict):
    # Substitute variables in root path
    root = config['root'].format(**variables)
    
    # Create root
    os.makedirs(root, exist_ok=True)
    
    # Create subfolders
    for subfolder in config['subfolders']:
        os.makedirs(os.path.join(root, subfolder), exist_ok=True)
    
    # Generate initial files
    for file_config in config['files']:
        template = load_template(file_config['template'])
        output = template.render(**variables)
        file_path = os.path.join(root, file_config['path'])
        write_file(file_path, output)
```

---

## 🎛️ Orchestrator-Specific Config

### Planning System Config

```yaml
config:
  # Complexity tier settings
  complexity_tiers:
    1: {max_phases: 3, max_tasks_per_phase: 10}
    2: {max_phases: 5, max_tasks_per_phase: 15}
    3: {max_phases: 8, max_tasks_per_phase: 20}
    4: {max_phases: 12, max_tasks_per_phase: 30}
    5: {max_phases: 20, max_tasks_per_phase: 50}
  
  # Context discovery limits
  context_limits:
    max_files_to_analyze: 500
    max_file_size_kb: 100
    excluded_patterns: ["node_modules/", "*.pyc", "__pycache__/"]
  
  # Template defaults
  template_defaults:
    author: "Asif Hussain"
    github_repo: "github.com/asifhussain60/CORTEX"
    
  # Database settings
  database:
    path: "cortex-brain/database/planning_state.db"
    snapshot_interval_minutes: 15
    auto_cleanup_days: 90
```

---

## 🔄 Complete Example: Planning System v5.0

```yaml
orchestrator:
  name: "planning_system"
  version: "5.0"
  type: "autonomous"
  description: "Pure autonomous planning orchestrator with state database"
  entry_point: "PlanningOrchestratorV5"

metadata:
  author: "Asif Hussain"
  created: "2026-01-02"
  complexity_tier: 4
  estimated_duration_days: 27

phases:
  - id: "discovery"
    name: "Context Discovery"
    order: 1
    estimated_hours: 2.0
    search_patterns:
      - name: "source_files"
        pattern: "class|def|function"
        file_types: ["*.py", "*.js"]
        scope: "src/"
    output_artifacts:
      - type: "context_summary"
        template: "discovery-context.jinja2"
        output_path: "context/discovery-summary.md"
    validations:
      - check_name: "files_found"
        check_type: "file_count"
        min: 5

folder_structure:
  root: "cortex-brain/documents/planning/active/{plan_name}/"
  subfolders: ["context", "artifacts", "reports", "tracking"]
  files:
    - path: "00-MASTER-PLAN.md"
      template: "master-plan.jinja2"

output_formats:
  master_plan:
    template: "templates/planning/master-plan.jinja2"
    context_required: ["feature_name", "phases"]

config:
  complexity_tiers:
    4: {max_phases: 12, max_tasks_per_phase: 30}
  database:
    path: "cortex-brain/database/planning_state.db"
```

---

## ✅ Validation Rules

All manifests MUST:
1. Pass JSON schema validation
2. Have all required top-level keys
3. Have unique phase IDs
4. Have valid template references
5. Have consistent validation configurations

**Schema Validator:**
```python
def validate_manifest(manifest: dict) -> ValidationResult:
    schema = load_schema('manifest-schema.json')
    jsonschema.validate(manifest, schema)
    
    # Additional business logic validation
    phase_ids = [p['id'] for p in manifest['phases']]
    if len(phase_ids) != len(set(phase_ids)):
        raise ValueError("Duplicate phase IDs")
    
    # Verify template files exist
    for artifact_type, config in manifest['output_formats'].items():
        if not os.path.exists(config['template']):
            raise ValueError(f"Template not found: {config['template']}")
```

---

## 🚀 Benefits

| Aspect | Hybrid (Old) | Config-Only (New) |
|--------|-------------|-------------------|
| **Ambiguity** | High (who executes?) | Zero (Python owns all) |
| **Maintainability** | Hard (sync code + language) | Easy (edit YAML) |
| **Testability** | Manual interpretation | Schema validation |
| **Extensibility** | Requires code changes | Edit config |
| **Debugging** | Unclear execution path | Traceable config reads |

---

**Specification Version:** 1.0  
**Status:** Ready for implementation  
**Next:** Create manifest templates for all 4 AUTONOMOUS orchestrators
