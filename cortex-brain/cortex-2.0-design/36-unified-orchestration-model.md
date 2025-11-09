# CORTEX 2.0: Unified Orchestration Model

**Document:** 36-unified-orchestration-model.md  
**Version:** 1.0  
**Created:** 2025-11-09  
**Status:** Design Complete  
**Priority:** CRITICAL  

**Related Documents:**
- 21-workflow-pipeline-system.md (Workflow orchestration)
- 02-plugin-system.md (Plugin architecture)
- 35-unified-architecture-analysis.md (Issue #2 resolution)

---

## 🎯 Purpose

Define clear separation and integration between CORTEX's two orchestration systems:
- **Workflow Pipeline** (Task-level orchestration)
- **Plugin Hooks** (Cross-cutting concerns)

**Problem Solved:** Eliminates confusion about when to use workflows vs hooks, prevents duplicate implementations, establishes clear execution model.

---

## 🏗️ Architectural Decision

### WORKFLOW PIPELINE = Primary Orchestration (Task-Level)

**Purpose:** User-defined task sequences with dependencies

**Scope:**
- Multi-step processes (TDD, threat modeling, cleanup)
- Explicit task ordering and dependencies
- Error recovery and retries
- User-visible workflows

**Mechanism:** DAG-based stages with explicit dependencies

**Example:**
```yaml
# User defines: "I want threat modeling, then DoD/DoR, then TDD"
workflow_id: "secure_feature"
stages:
  - id: "threat_model"
    script: "threat_modeling_plugin"
    depends_on: []
  
  - id: "clarify_dod_dor"
    script: "dod_clarifier_plugin"
    depends_on: ["threat_model"]
  
  - id: "tdd_cycle"
    script: "tdd_workflow_plugin"
    depends_on: ["clarify_dod_dor"]
```

---

### PLUGIN HOOKS = Cross-Cutting Concerns (System-Level)

**Purpose:** Automatic behaviors that apply across all operations

**Scope:**
- Logging and metrics
- Validation and security
- Cleanup and maintenance
- System-level events

**Mechanism:** Event-driven hooks at lifecycle points

**Example:**
```python
# Automatically runs for EVERY task (not user-configured)
@plugin_hook("before_task_start")
def log_task_metrics(context):
    """Log all task starts (cross-cutting concern)"""
    logger.info(f"Task starting: {context['task_id']}")

@plugin_hook("after_task_complete")
def auto_cleanup_temp_files(context):
    """Clean temp files after every task (cross-cutting concern)"""
    cleanup_temp_directory()
```

---

## 🔗 Integration Pattern: Stages Execute Plugins

**Key Principle:** Workflow stages are implemented as plugin executions

```python
# Workflow stage is a thin wrapper around plugin
class WorkflowStage:
    def __init__(self, stage_config):
        # Stage references plugin by ID
        self.plugin_id = stage_config.script
        self.plugin = plugin_manager.get_plugin(self.plugin_id)
        self.config = stage_config
    
    def execute(self, workflow_state):
        # Stage execution = plugin execution with hooks
        context = {
            'stage_id': self.config.id,
            'workflow_id': workflow_state.workflow_id,
            'state': workflow_state.data
        }
        
        # HOOK: before_stage_execute
        plugin_manager.trigger_hook("before_stage_execute", context)
        
        # PLUGIN: Execute the actual work
        result = self.plugin.execute(context)
        
        # HOOK: after_stage_execute  
        plugin_manager.trigger_hook("after_stage_execute", {
            **context,
            'result': result
        })
        
        return result
```

**Benefits:**
- ✅ Stages reuse plugin implementations (no duplication)
- ✅ Hooks apply automatically to all stages (cross-cutting)
- ✅ Clear separation: stages = orchestration, plugins = work
- ✅ Extensible: add plugins, use in workflows

---

## 📊 Execution Model

### Complete Lifecycle

```
User Request: "Run secure feature workflow"
    ↓
Entry Point → HOOK: request_received
    ↓
Workflow Orchestrator Loaded
    ├─ Parse workflow YAML
    ├─ Validate DAG (no cycles)
    └─ Initialize state
    ↓
HOOK: workflow_started
    ↓
For each stage (topological order):
│   ↓
│   HOOK: before_stage_execute
│   ↓
│   Execute Plugin (threat_modeling_plugin)
│   │   ↓
│   │   Plugin logic runs
│   │   ↓
│   │   Return result
│   ↓
│   HOOK: after_stage_execute
│   ↓
│   Update workflow state
│   ↓
│   Check dependencies for next stage
│   ↓
│   (Repeat for next stage)
    ↓
HOOK: workflow_completed
    ↓
Return result to user
```

---

## 📋 When to Use What

### Use Workflow Pipeline When:

**User wants custom sequences:**
- ✅ "Run threat modeling, then DoD/DoR, then TDD"
- ✅ "Run cleanup, then tests, then commit"
- ✅ "Analyze security, then generate code, then test"

**Dependencies between tasks:**
- ✅ Task B requires output from Task A
- ✅ Task C can't run until Task A and B complete
- ✅ Tasks can run in parallel if independent

**Error recovery needed:**
- ✅ Retry failed stages (up to N times)
- ✅ Rollback to checkpoint on failure
- ✅ Skip non-critical stages

**Multi-step processes:**
- ✅ TDD cycle (RED → GREEN → REFACTOR)
- ✅ Feature creation (plan → implement → test → document)
- ✅ Release process (build → test → deploy)

---

### Use Plugin Hooks When:

**Behavior applies to ALL operations:**
- ✅ Log every task start/end
- ✅ Collect metrics on every execution
- ✅ Validate file changes every commit

**Cross-cutting concerns:**
- ✅ Security validation
- ✅ Performance monitoring
- ✅ Error tracking
- ✅ Cleanup operations

**Automatic maintenance:**
- ✅ Archive old conversations (daily)
- ✅ Vacuum databases (weekly)
- ✅ Compress event logs (monthly)

**System-level events:**
- ✅ System startup/shutdown
- ✅ Configuration changes
- ✅ Brain state updates

---

## 🔌 Hook Points Reference

### Workflow Lifecycle Hooks

**Available in Plugin System (src/plugins/base_plugin.py):**

```python
# Workflow-level hooks
@plugin_hook("workflow_started")
def on_workflow_start(context):
    """Called when any workflow starts"""
    # context: {workflow_id, workflow_name, user_request}
    pass

@plugin_hook("workflow_completed")
def on_workflow_complete(context):
    """Called when any workflow completes successfully"""
    # context: {workflow_id, duration_ms, stages_executed}
    pass

@plugin_hook("workflow_failed")
def on_workflow_fail(context):
    """Called when any workflow fails"""
    # context: {workflow_id, failed_stage, error, checkpoint_restored}
    pass

# Stage-level hooks
@plugin_hook("before_stage_execute")
def before_stage(context):
    """Called before each stage executes"""
    # context: {workflow_id, stage_id, plugin_id, state}
    pass

@plugin_hook("after_stage_execute")
def after_stage(context):
    """Called after each stage executes"""
    # context: {workflow_id, stage_id, result, duration_ms}
    pass

@plugin_hook("stage_retry")
def on_stage_retry(context):
    """Called when stage retries after failure"""
    # context: {workflow_id, stage_id, attempt, max_retries, error}
    pass
```

### General System Hooks

```python
# Request lifecycle
@plugin_hook("request_received")
@plugin_hook("request_completed")
@plugin_hook("request_failed")

# Task lifecycle
@plugin_hook("task_started")
@plugin_hook("task_completed")
@plugin_hook("task_failed")

# File operations
@plugin_hook("file_created")
@plugin_hook("file_modified")
@plugin_hook("file_deleted")

# Brain updates
@plugin_hook("brain_updated")
@plugin_hook("rule_violated")
@plugin_hook("checkpoint_created")

# Maintenance
@plugin_hook("daily_maintenance")
@plugin_hook("weekly_maintenance")
@plugin_hook("database_vacuum")
```

---

## 💡 Design Patterns

### Pattern 1: Stage as Plugin Wrapper

**Problem:** Need to execute plugin within workflow orchestration

**Solution:**
```python
class WorkflowStage:
    """Thin wrapper that executes plugin with workflow context"""
    
    def __init__(self, stage_config, workflow_state):
        self.plugin = plugin_manager.get_plugin(stage_config.script)
        self.config = stage_config
        self.workflow_state = workflow_state
    
    def execute(self):
        # Add workflow context to plugin execution
        plugin_context = {
            **self.workflow_state.data,  # Shared state
            'stage_config': self.config,  # Stage-specific config
            'workflow_id': self.workflow_state.workflow_id
        }
        
        return self.plugin.execute(plugin_context)
```

---

### Pattern 2: Conditional Hooks

**Problem:** Hook should only run for specific workflows or stages

**Solution:**
```python
@plugin_hook("before_stage_execute")
def security_validation(context):
    """Only validate security-critical stages"""
    
    # Check if stage requires security validation
    if context['stage_id'] in ['deploy', 'production_release']:
        # Run security checks
        validate_security(context)
    else:
        # Skip for non-critical stages
        pass
```

---

### Pattern 3: State Sharing

**Problem:** Plugins need access to workflow state

**Solution:**
```python
class WorkflowState:
    """Shared state across all stages"""
    
    def __init__(self, workflow_id):
        self.workflow_id = workflow_id
        self.data = {}  # Shared data dictionary
    
    def set(self, key, value):
        self.data[key] = value
    
    def get(self, key, default=None):
        return self.data.get(key, default)

# Stage 1 sets data
def threat_modeling_plugin(context):
    threats = analyze_threats()
    context['state'].set('threats', threats)  # Share with next stage

# Stage 2 uses data
def dod_clarifier_plugin(context):
    threats = context['state'].get('threats')  # Access previous stage data
    generate_dod_from_threats(threats)
```

---

### Pattern 4: Hook Priority

**Problem:** Multiple hooks registered for same event - which runs first?

**Solution:**
```python
@plugin_hook("before_stage_execute", priority=10)
def critical_validation(context):
    """Runs first (priority 10)"""
    validate_critical_conditions()

@plugin_hook("before_stage_execute", priority=50)
def logging(context):
    """Runs second (priority 50)"""
    log_stage_start()

@plugin_hook("before_stage_execute", priority=100)
def metrics(context):
    """Runs last (priority 100)"""
    record_metrics()
```

---

## 🧪 Testing Strategy

### Unit Tests: Workflow Stages

```python
def test_workflow_stage_executes_plugin():
    """Stage should execute plugin with correct context"""
    
    mock_plugin = Mock()
    plugin_manager.register_plugin('test_plugin', mock_plugin)
    
    stage = WorkflowStage({
        'id': 'test_stage',
        'script': 'test_plugin'
    })
    
    state = WorkflowState('test_workflow')
    state.set('input', 'test_data')
    
    result = stage.execute(state)
    
    # Verify plugin executed with workflow context
    mock_plugin.execute.assert_called_once()
    call_context = mock_plugin.execute.call_args[0][0]
    assert call_context['workflow_id'] == 'test_workflow'
    assert call_context['state'].get('input') == 'test_data'
```

### Integration Tests: Hooks + Workflows

```python
def test_hooks_trigger_during_workflow():
    """Hooks should trigger at correct lifecycle points"""
    
    hook_calls = []
    
    @plugin_hook("workflow_started")
    def track_start(context):
        hook_calls.append('workflow_started')
    
    @plugin_hook("before_stage_execute")
    def track_before_stage(context):
        hook_calls.append(f'before_stage:{context["stage_id"]}')
    
    @plugin_hook("after_stage_execute")
    def track_after_stage(context):
        hook_calls.append(f'after_stage:{context["stage_id"]}')
    
    @plugin_hook("workflow_completed")
    def track_complete(context):
        hook_calls.append('workflow_completed')
    
    # Execute workflow with 2 stages
    workflow = WorkflowOrchestrator('test_workflow.yaml')
    workflow.execute()
    
    # Verify hook execution order
    assert hook_calls == [
        'workflow_started',
        'before_stage:stage1',
        'after_stage:stage1',
        'before_stage:stage2',
        'after_stage:stage2',
        'workflow_completed'
    ]
```

---

## 📚 Usage Examples

### Example 1: Secure Feature Creation Workflow

**Workflow Definition (YAML):**
```yaml
workflow_id: "secure_feature_creation"
name: "Secure Feature Creation"

stages:
  - id: "threat_model"
    script: "threat_modeling_plugin"
    required: true
  
  - id: "dod_dor"
    script: "dod_dor_clarifier_plugin"
    depends_on: ["threat_model"]
  
  - id: "tdd_cycle"
    script: "tdd_workflow_plugin"
    depends_on: ["dod_dor"]
  
  - id: "security_review"
    script: "security_review_plugin"
    depends_on: ["tdd_cycle"]
```

**Hook: Automatic Security Logging:**
```python
@plugin_hook("workflow_started")
def log_security_workflow(context):
    """Automatically log security-related workflows"""
    if 'security' in context['workflow_name'].lower():
        security_logger.log({
            'event': 'security_workflow_started',
            'workflow_id': context['workflow_id'],
            'timestamp': time.time(),
            'user': context.get('user_id')
        })
```

**Result:** Workflow orchestrates stages, hook logs automatically (no workflow YAML modification needed).

---

### Example 2: TDD Cycle with Auto-Cleanup

**Workflow Definition:**
```yaml
workflow_id: "tdd_cycle"
name: "Test-Driven Development Cycle"

stages:
  - id: "red_phase"
    script: "write_failing_test_plugin"
  
  - id: "green_phase"
    script: "implement_feature_plugin"
    depends_on: ["red_phase"]
  
  - id: "refactor_phase"
    script: "refactor_code_plugin"
    depends_on: ["green_phase"]
```

**Hook: Auto-Cleanup Temp Files:**
```python
@plugin_hook("after_stage_execute")
def cleanup_temp_files(context):
    """Clean up temporary files after each stage"""
    temp_dir = Path('/tmp/cortex')
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
        temp_dir.mkdir()
```

**Result:** Workflow runs TDD phases, cleanup happens automatically after each phase.

---

## 🎯 Migration Guide

### For Existing Workflow Implementations

**Before (Unclear):**
```python
# Was this a workflow stage or a hook? Unclear!
def threat_modeling(request):
    # Performs threat modeling
    pass
```

**After (Clear):**
```python
# PLUGIN: Implements the work
class ThreatModelingPlugin(BasePlugin):
    def execute(self, context):
        # Performs threat modeling
        return analyze_threats(context['request'])

# WORKFLOW: Orchestrates when it runs
# (defined in YAML - user configures order)

# HOOK: Cross-cutting concern
@plugin_hook("workflow_completed")
def auto_export_threat_model(context):
    """Automatically export threat model after any workflow"""
    if context.get('threats'):
        export_threat_model(context['threats'])
```

---

## ✅ Benefits

**For Developers:**
- ✅ Clear guidance: "Should I use workflow or hook?"
- ✅ No duplicate implementations
- ✅ Easy to test (clear separation)
- ✅ Extensible (add plugins, use in workflows)

**For Users:**
- ✅ Flexible workflows (custom task sequences)
- ✅ Automatic behaviors (hooks "just work")
- ✅ No configuration for cross-cutting concerns
- ✅ Powerful orchestration (DAG dependencies)

**For System:**
- ✅ Single execution model (hooks + stages)
- ✅ Consistent lifecycle (predictable behavior)
- ✅ Scalable (add workflows without touching core)
- ✅ Observable (hooks measure everything)

---

## 🚀 Implementation Checklist

### Phase 1: Core Integration (Week 2)

- [ ] Update `WorkflowStage` to execute plugins
- [ ] Add workflow lifecycle hooks to plugin system
- [ ] Update `PluginManager` to trigger workflow hooks
- [ ] Unit tests for stage-plugin integration
- [ ] Integration tests for hook execution order

### Phase 2: Documentation (Week 2)

- [ ] Update Document 21 (Workflow Pipeline) with plugin integration
- [ ] Update Document 02 (Plugin System) with workflow hooks
- [ ] Add usage examples to both documents
- [ ] Create quick reference guide

### Phase 3: Migration (Week 3)

- [ ] Audit existing workflow implementations
- [ ] Convert workflow stages to plugin executions
- [ ] Identify cross-cutting concerns → convert to hooks
- [ ] Update user-facing workflow YAMLs

---

## 📖 Related Documents

- **02-plugin-system.md** - Plugin architecture and hooks
- **21-workflow-pipeline-system.md** - Workflow orchestration and stages
- **35-unified-architecture-analysis.md** - Issue #2 (this document resolves)
- **00-INDEX.md** - Update with this document

---

**Document Status:** ✅ Complete  
**Next Action:** Update Doc 02 and Doc 21 with cross-references  
**Implementation:** Phase 2 (Plugin Infrastructure)  

**© 2024-2025 Asif Hussain. All rights reserved.**
