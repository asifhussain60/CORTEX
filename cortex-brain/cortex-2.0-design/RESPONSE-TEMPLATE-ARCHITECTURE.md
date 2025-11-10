# CORTEX Response Template Architecture
## Holistic Integration Analysis & Implementation Plan

**Created:** 2025-11-10  
**Author:** Asif Hussain  
**Status:** Design Complete → Implementation Ready  
**Impact:** System-wide response standardization

---

## 🎯 Executive Summary

**Problem:** Simple help command required Python execution, encoding fixes, and complex formatting logic. This pattern repeated across agents, operations, and plugins - each implementing custom response formatting.

**Solution:** Unified response template system using YAML-based templates for **instant, zero-execution responses** with consistent formatting across all CORTEX components.

**Benefits:**
- ⚡ **Zero execution overhead** for template-based responses
- 🎯 **Consistent UX** across all commands/agents
- 🔧 **Easy maintenance** - edit YAML, not code
- 📊 **Verbosity control** - concise/detailed/expert modes
- 🌐 **Extensible** - plugins can register templates

---

## 🏗️ Architecture Analysis

### Current State (Fragmented)

**Response formatting is scattered:**

1. **Entry Point Layer** (`src/entry_point/response_formatter.py`)
   - 482 lines of formatting logic
   - Handles text/markdown/JSON formats
   - Verbosity levels (concise/detailed/expert)
   - 30+ test cases

2. **Agent Layer** (each agent in `src/cortex_agents/`)
   - Each agent implements `AgentResponse` dataclass
   - Custom formatting in `execute()` methods
   - Inconsistent error message formats
   - No standardized status reporting

3. **Operations Layer** (`src/operations/`)
   - `OperationExecutionReport` for operation results
   - Custom help formatting in `help_command.py`
   - Inconsistent module output formats

4. **Plugin Layer** (`src/plugins/`)
   - Each plugin returns `PluginMetadata`
   - Custom status/progress reporting
   - No unified error handling

**Issues:**
- ❌ Duplication (formatting logic repeated)
- ❌ Inconsistency (different formats for similar outputs)
- ❌ Complexity (Python execution for simple text)
- ❌ Hard to maintain (change requires code updates)

---

### Proposed State (Unified)

**Single response template system:**

```
cortex-brain/response-templates.yaml
├── Common Templates (help, status, error, success)
├── Agent Templates (per agent type)
├── Operation Templates (per operation)
└── Plugin Templates (registered by plugins)
```

**Template Structure:**
```yaml
templates:
  template_id:
    triggers: [list of phrases]
    response_type: table | list | detailed | narrative | json
    verbosity: concise | detailed | expert
    context_needed: false | true
    content: |
      Pre-formatted response text
      with {{placeholders}} for dynamic values
```

**Integration Points:**

1. **Entry Point** (`CORTEX.prompt.md`)
   - Load templates for instant help/status responses
   - No Python execution needed

2. **ResponseFormatter** (enhanced)
   - Template rendering engine
   - Placeholder substitution
   - Verbosity filtering
   - Format conversion (text → markdown → JSON)

3. **Agents** (standardized)
   - Return structured `AgentResponse`
   - Templates format responses consistently
   - Error templates for common failures

4. **Operations** (templatized)
   - Pre-defined progress templates
   - Status report templates
   - Completion summary templates

5. **Plugins** (extensible)
   - Plugins register custom templates
   - Plugin-specific help templates
   - Consistent plugin output format

---

## 📋 Template Categories

### 1. **System Templates** (Core CORTEX)

**Always available, never require execution:**

```yaml
system_templates:
  help_table:
    triggers: [help, /help, /CORTEX help]
    type: table
    verbosity: concise
    content: "..." # Command table
    
  help_detailed:
    triggers: [help detailed, show all commands]
    type: detailed
    verbosity: detailed
    content: "..." # Categorized commands
    
  status_check:
    triggers: [status, /status, implementation status]
    type: table
    verbosity: concise
    content: "..." # Phase progress
    
  quick_start:
    triggers: [getting started, first time, quick start]
    type: narrative
    verbosity: concise
    content: "..." # Onboarding guide
```

### 2. **Agent Response Templates**

**Standardize agent output formats:**

```yaml
agent_templates:
  executor_success:
    agent: executor
    result: success
    verbosity: concise
    content: |
      ✅ **Feature Implemented**
      
      Files Modified: {{files_count}}
      {{#files}}
      - {{path}}
      {{/files}}
      
      Next: {{next_action}}
  
  executor_error:
    agent: executor
    result: error
    verbosity: concise
    content: |
      ❌ **Implementation Failed**
      
      Error: {{error_message}}
      
      Suggestions:
      {{#suggestions}}
      - {{text}}
      {{/suggestions}}
  
  tester_coverage:
    agent: tester
    result: success
    verbosity: detailed
    content: |
      ✅ **Tests Generated**
      
      Coverage: {{coverage_percent}}%
      Test Files: {{test_files_count}}
      
      {{#test_files}}
      - {{name}}: {{tests_count}} tests
      {{/test_files}}
      
      Command: pytest {{test_paths}}
```

### 3. **Operation Status Templates**

**Progress reporting for operations:**

```yaml
operation_templates:
  operation_started:
    verbosity: concise
    content: |
      🚀 **{{operation_name}}** - Started
      Profile: {{profile}}
      Modules: {{modules_count}}
  
  operation_progress:
    verbosity: concise
    content: |
      ⏳ **{{operation_name}}** - {{percent}}%
      
      ✅ Completed: {{completed_modules}}
      🔄 Running: {{current_module}}
      ⏸️ Pending: {{pending_modules}}
  
  operation_complete:
    verbosity: detailed
    content: |
      ✅ **{{operation_name}}** - Complete
      
      Duration: {{duration_seconds}}s
      Modules: {{succeeded}}/{{total}} succeeded
      
      {{#failures}}
      ❌ {{module_name}}: {{error}}
      {{/failures}}
      
      Next: {{recommendation}}
```

### 4. **Error Templates**

**Consistent error reporting:**

```yaml
error_templates:
  missing_dependency:
    severity: error
    verbosity: detailed
    content: |
      ❌ **Missing Dependency**
      
      Package: {{package_name}}
      Required by: {{required_by}}
      
      Fix: pip install {{package_name}}
  
  permission_denied:
    severity: error
    verbosity: concise
    content: |
      🔒 **Permission Denied**
      
      {{error_message}}
      
      Try: Run with appropriate permissions
  
  validation_failed:
    severity: warning
    verbosity: detailed
    content: |
      ⚠️ **Validation Failed**
      
      {{#errors}}
      - {{field}}: {{message}}
      {{/errors}}
      
      Fix these issues and retry.
```

### 5. **Plugin Templates**

**Plugins register custom templates:**

```yaml
plugin_templates:
  platform_switch_detected:
    plugin: platform_switch
    verbosity: concise
    content: |
      🔄 **Platform Change Detected**
      
      From: {{old_platform}}
      To: {{new_platform}}
      
      Auto-configuring...
  
  cleanup_report:
    plugin: cleanup
    verbosity: detailed
    content: |
      🧹 **Cleanup Complete**
      
      Files Removed: {{files_count}} ({{size_mb}}MB)
      Logs Rotated: {{logs_count}}
      DB Optimized: {{db_savings_mb}}MB saved
      
      Total Space Freed: {{total_mb}}MB
```

---

## 🔧 Implementation Plan

### Phase 1: Core Template Engine (2-3 hours)

**Goal:** Build template rendering infrastructure

**Deliverables:**

1. **Template Loader** (`src/response_templates/template_loader.py`)
   ```python
   class TemplateLoader:
       def __init__(self, template_file: Path)
       def load_template(self, template_id: str) -> Template
       def find_by_trigger(self, trigger: str) -> Template
       def list_templates(self, category: str = None) -> List[Template]
   ```

2. **Template Renderer** (`src/response_templates/template_renderer.py`)
   ```python
   class TemplateRenderer:
       def render(self, template: Template, context: Dict) -> str
       def render_with_placeholders(self, template: Template, **kwargs) -> str
       def apply_verbosity(self, content: str, verbosity: str) -> str
       def convert_format(self, content: str, format: str) -> str
   ```

3. **Template Registry** (`src/response_templates/template_registry.py`)
   ```python
   class TemplateRegistry:
       def register_template(self, template: Template)
       def register_plugin_templates(self, plugin_id: str, templates: List[Template])
       def get_template(self, template_id: str) -> Template
       def search_templates(self, query: str) -> List[Template]
   ```

### Phase 2: Integration with Existing Systems (3-4 hours)

**Goal:** Connect templates to agents, operations, plugins

**Deliverables:**

1. **Enhanced ResponseFormatter**
   ```python
   class ResponseFormatter:
       def __init__(self, template_loader: TemplateLoader):
           self.template_loader = template_loader
           self.renderer = TemplateRenderer()
       
       def format_from_template(
           self, 
           template_id: str, 
           context: Dict,
           verbosity: str = "concise"
       ) -> str:
           """Format using template instead of code logic"""
           template = self.template_loader.load_template(template_id)
           return self.renderer.render(template, context, verbosity)
   ```

2. **Agent Template Integration**
   ```python
   # In BaseAgent
   def execute(self, request: AgentRequest) -> AgentResponse:
       result = self._do_work(request)
       
       # Use template for formatting
       template_id = f"{self.agent_type.value}_success" if result.success else f"{self.agent_type.value}_error"
       formatted_response = self.template_formatter.format_from_template(
           template_id,
           {
               "agent_name": self.metadata.name,
               "result": result,
               **request.context
           }
       )
       
       return AgentResponse(
           success=result.success,
           result=result.data,
           message=formatted_response,
           agent_name=self.metadata.name
       )
   ```

3. **Operation Template Integration**
   ```python
   # In OperationsOrchestrator
   def execute_operation(self, context: Dict) -> OperationExecutionReport:
       # Start template
       self._show_progress("operation_started", {
           "operation_name": self.operation.name,
           "profile": context.get("profile"),
           "modules_count": len(self.modules)
       })
       
       # Progress template (during execution)
       for i, module in enumerate(self.modules):
           self._show_progress("operation_progress", {
               "operation_name": self.operation.name,
               "percent": (i / len(self.modules)) * 100,
               "current_module": module.metadata.name
           })
           
       # Completion template
       self._show_progress("operation_complete", {
           "operation_name": self.operation.name,
           "duration_seconds": total_duration,
           "succeeded": len(succeeded),
           "total": len(self.modules),
           "failures": failures
       })
   ```

### Phase 3: Template Content Creation (4-5 hours)

**Goal:** Create comprehensive template library

**Deliverables:**

1. **System Templates** (15 templates)
   - help, status, quick_start, commands
   - error (common errors)
   - success (common successes)

2. **Agent Templates** (20 templates, 2 per agent)
   - executor, tester, validator, work_planner, documenter
   - intent_detector, architect, health_validator, pattern_matcher, learner

3. **Operation Templates** (30 templates)
   - environment_setup, refresh_story, cleanup, update_docs
   - brain_protection_check, self_review, run_tests
   - Progress/completion variants

4. **Error Templates** (15 templates)
   - missing_dependency, permission_denied, validation_failed
   - file_not_found, network_error, timeout
   - configuration_error, syntax_error, etc.

5. **Plugin Templates** (10 templates)
   - platform_switch, cleanup, doc_refresh
   - Common plugin patterns

### Phase 4: Testing & Validation (2-3 hours)

**Goal:** Comprehensive test coverage

**Deliverables:**

1. **Template Engine Tests** (`tests/response_templates/test_template_loader.py`)
   - Template loading
   - Trigger matching
   - Template search

2. **Renderer Tests** (`tests/response_templates/test_template_renderer.py`)
   - Placeholder substitution
   - Verbosity filtering
   - Format conversion

3. **Integration Tests** (`tests/response_templates/test_integration.py`)
   - Agent response formatting
   - Operation progress reporting
   - Plugin template registration

4. **Performance Tests**
   - Template loading speed (<10ms)
   - Rendering speed (<5ms)
   - Memory usage (minimal)

### Phase 5: Documentation & Migration (2-3 hours)

**Goal:** Update docs, migrate existing code

**Deliverables:**

1. **Documentation**
   - Template authoring guide
   - Placeholder syntax reference
   - Plugin template registration guide
   - Migration guide for existing code

2. **Migration**
   - Update help_command.py to use templates
   - Migrate agent responses gradually
   - Update operation progress reporting
   - Plugin template registration examples

---

## 📊 Integration Points Matrix

| Component | Current State | Template Integration | Priority | Effort |
|-----------|--------------|---------------------|----------|--------|
| **Entry Point** | Hardcoded help text | Load templates directly | 🔴 Critical | 1h |
| **ResponseFormatter** | Code-based formatting | Template rendering engine | 🔴 Critical | 2h |
| **Help Command** | Python execution | Template lookup | 🔴 Critical | 1h |
| **Agents (10x)** | Custom response formatting | Agent templates | 🟡 High | 3h |
| **Operations** | Custom progress messages | Operation templates | 🟡 High | 2h |
| **Plugins** | Inconsistent outputs | Plugin template registry | 🟢 Medium | 2h |
| **Error Handling** | Scattered error messages | Error templates | 🟢 Medium | 2h |
| **Status Reporting** | Custom status formats | Status templates | 🟢 Medium | 1h |

**Total Estimated Effort:** 14-16 hours

---

## 🎯 Benefits Analysis

### Developer Experience

**Before:**
```python
# Custom formatting logic in every agent
def execute(self, request):
    result = do_work()
    if result.success:
        return f"✅ Success! Modified {len(result.files)} files:\n" + \
               "\n".join(f"  - {f}" for f in result.files) + \
               f"\nNext: {result.next_action}"
    else:
        return f"❌ Failed: {result.error}\n" + \
               "Try: " + "\n".join(f"  - {s}" for s in result.suggestions)
```

**After:**
```python
# Template-based formatting
def execute(self, request):
    result = do_work()
    template_id = f"{self.agent_type}_success" if result.success else f"{self.agent_type}_error"
    return self.format_from_template(template_id, {"result": result})
```

### User Experience

**Consistent Output:**
- All agents use same format
- Status symbols consistent (✅ ❌ ⏳ ⚠️)
- Error messages follow same structure
- Help commands look identical

**Verbosity Control:**
- User preference persists
- Templates adapt automatically
- No code changes needed

### Maintenance

**Before:** Change help format → Edit 5 files, test 10 places  
**After:** Change help format → Edit 1 YAML template

**Before:** Add new agent → Implement custom formatting  
**After:** Add new agent → Reference existing templates

---

## 🚀 Rollout Strategy

### Week 1: Foundation (Phase 1)
- Build template engine
- Basic tests passing
- Load system templates

### Week 2: Integration (Phase 2-3)
- Integrate with ResponseFormatter
- Create template library
- Migrate help command

### Week 3: Expansion (Phase 3-4)
- Agent template integration
- Operation templates
- Comprehensive testing

### Week 4: Polish (Phase 5)
- Documentation
- Migration guides
- Plugin examples

---

## 📈 Success Metrics

**Performance:**
- Template load time: <10ms
- Rendering time: <5ms
- Memory overhead: <1MB

**Quality:**
- 100% test pass rate
- Zero execution for help/status
- Consistent UX across all commands

**Adoption:**
- All system commands use templates (Week 2)
- All agents use templates (Week 3)
- Plugins can register templates (Week 4)

---

## 🔮 Future Enhancements

### Phase 2.1: Advanced Features

1. **Template Inheritance**
   ```yaml
   base_success_template:
     content: "✅ Success..."
   
   executor_success:
     extends: base_success_template
     additional_content: "Files: {{files}}"
   ```

2. **Conditional Rendering**
   ```yaml
   content: |
     ✅ Success
     {{#if files}}
     Files Modified: {{files_count}}
     {{/if}}
     {{#if warnings}}
     ⚠️ Warnings: {{warnings}}
     {{/if}}
   ```

3. **Localization Support**
   ```yaml
   help_table:
     en: "CORTEX COMMANDS..."
     es: "COMANDOS DE CORTEX..."
     fr: "COMMANDES CORTEX..."
   ```

4. **Theme Support**
   ```yaml
   themes:
     default:
       success: "✅"
       error: "❌"
     minimal:
       success: "[OK]"
       error: "[ERR]"
   ```

---

## 📝 Decision Log

**Date:** 2025-11-10  
**Decision:** Implement unified response template architecture  
**Rationale:**
- Solves immediate problem (help command complexity)
- Addresses system-wide inconsistency
- Reduces maintenance burden
- Improves user experience
- Aligns with CORTEX 2.0 modular architecture

**Alternatives Considered:**
1. ❌ Keep current code-based formatting (maintenance burden)
2. ❌ Hardcode templates in prompt files (bloat, inflexible)
3. ❌ Database-backed templates (overkill, overhead)
4. ✅ **YAML-based template system (sweet spot)**

**Risk Assessment:**
- 🟢 **LOW:** Template system is simple, well-tested pattern
- 🟢 **LOW:** Rollout can be gradual (no big-bang migration)
- 🟢 **LOW:** Rollback easy (keep old code during transition)

**Approval:** PROCEED with implementation

---

*End of Design Document*
