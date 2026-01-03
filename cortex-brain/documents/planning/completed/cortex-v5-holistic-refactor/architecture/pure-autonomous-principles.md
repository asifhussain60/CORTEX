# Pure Autonomous Architecture Principles

**Document Type:** Architecture Reference  
**Plan:** CORTEX v5.0 Holistic Refactor  
**Created:** January 2, 2026

---

## 🎯 Core Principles

### 1. Zero Natural Language Instructions

**Manifests contain only data structures, not commands.**

❌ **WRONG (Hybrid):**
```yaml
phases:
  - name: "Discovery"
    instructions: "Search the workspace for relevant files..."
    steps:
      - "Use grep_search to find controllers"
```

✅ **CORRECT (Pure Config):**
```yaml
phases:
  - id: "discovery"
    search_patterns:
      - pattern: "class.*Controller"
        scope: "src/**/*.py"
    output_artifacts:
      - type: "context_summary"
        template: "discovery-summary.jinja2"
```

### 2. Python Owns Execution

**All logic, all decisions, all output generation in orchestrator code.**

- ✅ Python reads config data
- ✅ Python executes phases
- ✅ Python generates all outputs (markdown, JSON, reports)
- ✅ Python validates checkpoints
- ❌ CORTEX never interprets manifest instructions

### 3. Database State Management

**SQLite with ACID transactions for atomic phases.**

**Benefits:**
- Atomic phase execution (commit/rollback)
- Recovery from failures at any point
- Complete audit trail
- Progress queries without parsing files
- Single source of truth

**Schema:**
```sql
plans (plan_id, feature_name, status, created, completed)
phases (phase_id, plan_id, name, status, order, started, completed)
tasks (task_id, phase_id, description, status, estimated_hours)
artifacts (artifact_id, plan_id, path, type, generated)
validations (validation_id, phase_id, check_name, passed, details)
state_snapshots (snapshot_id, plan_id, phase_id, timestamp, data)
```

### 4. Config-Driven Behavior

**YAML defines folder templates, validation schemas, output formats.**

- Orchestrator behavior changes via config edits
- No code changes required for structure modifications
- Testable via config validation
- Version-controlled configuration

### 5. CORTEX as Thin Client

**Route intent → Invoke tool → Display summary → Done.**

```
┌──────────────────────────────────────────────┐
│       USER INTENT DETECTION                  │
│   (CORTEX.prompt.md + LLMIntentClassifier)   │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│    MCP TOOL: invoke_orchestrator()           │
│  Parameters: orchestrator_name, user_request │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│   PYTHON ORCHESTRATOR (Owns Everything)      │
│ • Load YAML config                           │
│ • Execute atomic phases with DB transactions │
│ • Generate all outputs                       │
│ • Return execution summary                   │
└──────────────────────────────────────────────┘
                    ↓
┌──────────────────────────────────────────────┐
│    CORTEX DISPLAYS RESULTS (Thin Client)     │
│  Uses template: autonomous_execution_progress│
└──────────────────────────────────────────────┘
```

---

## 🛡️ Hand-Off Protocol

**When 🛡️ AUTONOMOUS orchestrators are engaged:**

### CORTEX MUST:
1. ✅ Detect intent via LLMIntentClassifier
2. ✅ Load manifest reference ONLY
3. ✅ Invoke MCP tool with parameters
4. ✅ Display header with 🛡️ emoji
5. ✅ STOP immediately (no execution)

### CORTEX MUST NOT:
1. ❌ Read manifest and execute instructions
2. ❌ Provide guidance based on manifest content
3. ❌ Implement features after detecting planning intent
4. ❌ Continue after loading orchestrator
5. ❌ Summarize what orchestrator will do

### Python Orchestrator MUST:
1. ✅ Load config from manifest
2. ✅ Execute all phases autonomously
3. ✅ Generate all outputs
4. ✅ Return execution summary to CORTEX
5. ✅ Handle all errors internally

---

## 📐 Manifest Structure

### Config-Only Manifest Template

```yaml
orchestrator:
  name: "planning_system"
  version: "5.0"
  type: "autonomous"  # vs "guided"
  
metadata:
  description: "Pure autonomous planning orchestrator"
  author: "CORTEX v5.0"
  response_template: "autonomous_execution_progress"

folder_structure:
  root: "cortex-brain/documents/planning/active/{plan_name}/"
  subfolders:
    - name: "context"
      description: "Discovery artifacts"
    - name: "artifacts"
      description: "Generated code/config"
    - name: "reports"
      description: "Progress reports"
    - name: "tracking"
      description: "State database snapshots"
    - name: "phases"
      description: "Phase-specific details"
    - name: "architecture"
      description: "Architecture decisions"
    - name: "future-structure"
      description: "Implementation code"

phases:
  - id: "discovery"
    order: 1
    search_patterns:
      - pattern: "class.*Controller"
        scope: "src/**/*.py"
        output_file: "context/controllers.md"
      - pattern: "def test_"
        scope: "tests/**/*.py"
        output_file: "context/tests.md"
    validations:
      - name: "context_complete"
        check: "file_exists"
        path: "context/controllers.md"
    output_artifacts:
      - type: "context_summary"
        template: "templates/discovery-summary.jinja2"
        output_path: "context/discovery-summary.md"

  - id: "architecture_analysis"
    order: 2
    analysis_targets:
      - type: "ast_parse"
        files: "src/**/*.py"
        output_file: "architecture/structure.json"
    validations:
      - name: "ast_valid"
        check: "json_schema"
        schema: "schemas/ast-structure.json"

  - id: "plan_generation"
    order: 3
    templates:
      - name: "master_plan"
        template: "templates/master-plan-v5.jinja2"
        output_path: "00-MASTER-PLAN-V5.md"
        context_sources:
          - "context/discovery-summary.md"
          - "architecture/structure.json"
    validations:
      - name: "plan_complete"
        check: "markdown_headers"
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

## 🔄 Execution Flow

### 1. Intent Detection
```python
# In CORTEX.prompt.md routing logic
if matches_planning_pattern(user_request):
    intent = "planning_system"
    orchestrator = "planning_orchestrator_v5"
```

### 2. MCP Tool Invocation
```python
# CORTEX invokes MCP tool
result = invoke_orchestrator(
    orchestrator_name="planning_orchestrator_v5",
    user_request="create authentication system"
)
```

### 3. Python Execution
```python
# In planning_orchestrator_v5.py
class PlanningOrchestratorV5(BaseOrchestratorV41):
    def execute(self, user_request: str):
        # Load config
        config = self.load_config()
        
        # Execute phases with DB transactions
        for phase in config['phases']:
            with db.transaction():
                self.execute_phase(phase)
                self.validate_phase(phase)
        
        # Generate outputs
        outputs = self.generate_outputs(config['templates'])
        
        # Return summary
        return {
            "status": "success",
            "plan_path": outputs['master_plan'],
            "artifacts": outputs['artifacts']
        }
```

### 4. Result Display
```python
# CORTEX displays result using template
display_result(
    template="autonomous_execution_progress",
    data=result
)
```

---

## ✅ Migration Checklist

For each orchestrator being migrated to v5 architecture:

- [ ] Strip natural language instructions from manifest
- [ ] Convert manifest to pure config (YAML data only)
- [ ] Implement Python execution logic in orchestrator class
- [ ] Add database state management (transactions)
- [ ] Create Jinja2 templates for all outputs
- [ ] Add validation checkpoints after each phase
- [ ] Write unit tests for each phase
- [ ] Update CORTEX.prompt.md intent routing
- [ ] Update response template references
- [ ] Archive old manifest to `cortex-brain/archives/manifests-v4/`
- [ ] Document migration in `reports/migration-report.md`

---

## 📚 References

**Source Documents:**
- `cortex-brain/documents/planning/active/autonomous-orchestrator-v5/00-MASTER-PLAN-V5.md`
- `CORTEX.prompt.md` - Hand-off protocol
- `brain-protection-rules.yaml` - HAND_OFF_PROTOCOL rule
- `response-templates-v4.yaml` - autonomous_execution_progress template

**Implementation Examples:**
- `future-structure/src/orchestrators/planning_orchestrator_v5.py`
- `future-structure/cortex-brain/manifests/orchestrators/planning-system-5.0-manifest.yaml`
