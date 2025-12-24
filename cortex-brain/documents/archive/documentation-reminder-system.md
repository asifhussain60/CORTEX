# Documentation Reminder System

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Created:** December 6, 2025  
**Status:** ✅ Implemented

---

## Overview

The Documentation Reminder System automatically prompts CORTEX to document completed work in the learning library using the docsify documentation framework. This ensures knowledge capture and cross-machine accessibility.

### Key Features

- **Automatic Reminders:** Triggered at workflow completion points
- **Contextual Information:** Includes location, work item details, and access instructions
- **Cross-Machine Compatible:** All documentation stored in `cortex-brain/documents/learning/`
- **Docsify Integration:** Documents accessible via learning dashboard
- **Organized Structure:** Proper nested folder structure by category

---

## Integration Points

### 1. Planning Orchestrator

**File:** `src/orchestrators/planning_orchestrator.py`

#### Plan Approval
- **Trigger:** When `approve_plan()` completes successfully
- **Location:** `cortex-brain/documents/learning/planning_strategies/`
- **Captures:** Requirements, scope, approach, key decisions
- **Return Field:** `documentation_reminder` in result dictionary

#### Plan Completion
- **Trigger:** When `complete_plan()` completes successfully
- **Location:** `cortex-brain/documents/learning/milestones/`
- **Captures:** Key learnings, decisions, outcomes
- **Return Field:** `documentation_reminder` in result dictionary

### 2. ADO Work Item Utility

**File:** `src/operations/modules/ado/ado_utility.py`

#### Work Item Completion
- **Trigger:** When `update_work_item()` changes status to COMPLETED
- **Location:** `cortex-brain/documents/learning/ado_workflows/`
- **Captures:** Implementation details, technical decisions, outcomes
- **Logging:** Reminder logged at INFO level for visibility

---

## Reminder Format

All reminders follow this consistent format:

```
📚 DOCUMENTATION REMINDER:
[Context-specific message]
Location: cortex-brain/documents/learning/[category]/
[Work Item Details]
Capture: [What to document]
Access via: load dashboard
Cross-machine compatible: All docs are in cortex-brain/documents/learning/
```

### Example: Plan Completion

```
📚 DOCUMENTATION REMINDER:
Please document this work in the learning library using docsify.
Location: cortex-brain/documents/learning/milestones/
Plan: feature-xyz-plan.yaml
Generate markdown documentation capturing key learnings, decisions, and outcomes.
The documentation will be accessible via the learning dashboard (load dashboard).
Cross-machine compatible: All docs are in cortex-brain/documents/learning/
```

---

## Documentation Structure

### Learning Library Organization

```
cortex-brain/documents/learning/
├── planning_strategies/      # Plan creation, approval, strategy decisions
├── milestones/               # Completed phases, major achievements
├── ado_workflows/            # ADO work items, stories, features
├── workflow_context/         # Operational workflows
├── intent_routing/           # Command routing patterns
├── architectural_patterns/   # Design patterns, architecture decisions
├── code_quality/             # Refactoring, optimization learnings
├── design_decisions/         # Technical decision records
├── debugging_patterns/       # Problem-solving approaches
├── productivity_patterns/    # Efficiency improvements
├── operational_learnings/    # System operations, deployment
├── user_onboarding/          # Setup, configuration guides
├── deployment_strategies/    # Release processes
├── performance_tuning/       # Optimization strategies
└── security_practices/       # Security implementations
```

### Document Naming Convention

**Format:** `{event_type}_{timestamp}.md`

**Examples:**
- `plan_created_20251206_105458.md`
- `plan_approved_20251206_110230.md`
- `phase_completed_20251206_112045.md`
- `ado_story_created_20251206_143022.md`

---

## Usage

### For Developers

When you see a documentation reminder:

1. **Create Markdown File:**
   ```bash
   # Navigate to suggested location
   cd cortex-brain/documents/learning/[category]/
   
   # Create new document
   touch my_feature_learning_20251206.md
   ```

2. **Document Key Points:**
   - What was the challenge?
   - What approach was taken?
   - What decisions were made?
   - What were the outcomes?
   - What was learned?

3. **Access Documentation:**
   ```bash
   # Launch learning dashboard
   load dashboard
   
   # Or from Python
   python src/operations/modules/dashboard/learning_dashboard_launcher.py
   ```

### For CORTEX AI

When processing a reminder:

1. **Extract Context:**
   - Work item ID/plan name
   - Location path
   - What to capture

2. **Generate Documentation:**
   - Create markdown file in specified location
   - Follow template structure (if available)
   - Include context, decisions, outcomes

3. **Confirm Creation:**
   - Log file creation
   - Verify location
   - Remind about dashboard access

---

## Implementation Details

### Helper Function: `_generate_documentation_reminder()`

**Location:** `PlanningOrchestrator` class  
**Purpose:** Generate contextual reminders for planning workflows

**Signature:**
```python
def _generate_documentation_reminder(self, context: str, **kwargs) -> str:
    """
    Generate documentation reminder for learning library.
    
    Args:
        context: Context type (plan_completion, plan_approval, ado_completion)
        **kwargs: Context-specific parameters (plan_name, work_item_id, title)
    
    Returns:
        Formatted documentation reminder string
    """
```

**Contexts:**
- `plan_completion` - Plan finished
- `plan_approval` - Plan approved
- `ado_completion` - Work item completed (legacy, use ADO utility instead)

### Helper Function: `_generate_ado_documentation_reminder()`

**Location:** `ado_utility.py` module  
**Purpose:** Generate reminders for ADO work item completion

**Signature:**
```python
def _generate_ado_documentation_reminder(work_item_id: str, title: str) -> str:
    """
    Generate documentation reminder for ADO work item completion.
    
    Args:
        work_item_id: ADO work item identifier
        title: Work item title
    
    Returns:
        Formatted documentation reminder string
    """
```

---

## Testing

### Manual Testing

1. **Test Plan Approval:**
   ```python
   from src.orchestrators.planning_orchestrator import PlanningOrchestrator
   
   orchestrator = PlanningOrchestrator("d:\\PROJECTS\\CORTEX")
   result = orchestrator.approve_plan("test-plan.yaml")
   
   # Check for reminder
   assert 'documentation_reminder' in result
   print(result['documentation_reminder'])
   ```

2. **Test Plan Completion:**
   ```python
   result = orchestrator.complete_plan("test-plan.yaml")
   
   # Check for reminder
   assert 'documentation_reminder' in result
   print(result['documentation_reminder'])
   ```

3. **Test ADO Completion:**
   ```python
   from src.operations.modules.ado.ado_utility import update_work_item, WorkItemStatus
   
   result = update_work_item(
       work_item_id="ado-test-12345",
       status=WorkItemStatus.COMPLETED
   )
   
   # Reminder logged at INFO level
   # Check logs for documentation reminder
   ```

---

## Cross-Machine Compatibility

### Design Principles

1. **Relative Paths:** All paths relative to `cortex-brain/`
2. **Config-Based Root:** Machine-specific paths in `cortex.config.json`
3. **Git Synchronized:** Documentation committed to repository
4. **No Absolute Paths:** Never use machine-specific absolute paths in reminders

### Machine Configuration

**File:** `cortex.config.json`

```json
{
  "machines": {
    "MACHINE-NAME": {
      "rootPath": "/path/to/CORTEX",
      "brainPath": "/path/to/CORTEX/cortex-brain"
    }
  }
}
```

Each developer adds their machine configuration. Documentation paths remain relative.

---

## Benefits

### Knowledge Capture
- ✅ Automatic prompts prevent documentation gaps
- ✅ Consistent structure across all documentation
- ✅ Context-specific guidance on what to capture

### Accessibility
- ✅ Single source of truth in learning library
- ✅ Full-text search via docsify
- ✅ Category-based navigation
- ✅ Web-based interface (no IDE required)

### Collaboration
- ✅ Cross-machine compatible
- ✅ Git-synchronized
- ✅ Version-controlled documentation
- ✅ Easy sharing and discovery

### Learning
- ✅ Captures decisions and rationale
- ✅ Documents patterns and practices
- ✅ Preserves institutional knowledge
- ✅ Supports onboarding and training

---

## Future Enhancements

### Phase 2: Auto-Generation (Planned)
- Automatic markdown generation from context
- Template-based documentation
- AI-assisted content generation
- Integration with Phase 2 document generation system

### Phase 3: Enhanced Integration (Planned)
- Dashboard deep-linking to specific documents
- Search integration with work item IDs
- Cross-reference detection
- Related document suggestions

### Phase 4: Analytics (Planned)
- Documentation coverage metrics
- Most-documented categories
- Knowledge gap identification
- Documentation quality scoring

---

## Troubleshooting

### Reminder Not Appearing

**Symptom:** No documentation reminder in result

**Causes:**
1. Operation failed before reminder generation
2. Status transition not completed
3. Exception during reminder generation

**Solution:**
- Check operation success: `result['success']`
- Review logs for errors
- Verify status transition occurred

### Wrong Location Suggested

**Symptom:** Reminder suggests incorrect location

**Causes:**
1. Context parameter incorrect
2. Category mapping needs update

**Solution:**
- Verify context parameter passed to `_generate_documentation_reminder()`
- Update category mapping in reminder templates

### Dashboard Not Loading Docs

**Symptom:** Documentation created but not visible in dashboard

**Causes:**
1. Wrong location (not in `cortex-brain/documents/learning/`)
2. File permissions issue
3. Dashboard serving wrong directory

**Solution:**
- Verify file location: `cortex-brain/documents/learning/[category]/`
- Check file permissions (should be readable)
- Restart dashboard: `load dashboard`

---

## References

- **Learning System:** `src/learning/README.md`
- **Dashboard Integration:** `src/learning/DASHBOARD-INTEGRATION.md`
- **Document Generation:** `src/learning/DOCUMENT-GENERATION.md`
- **Planning Orchestrator:** `src/orchestrators/planning_orchestrator.py`
- **ADO Utility:** `src/operations/modules/ado/ado_utility.py`

---

**Version History:**
- **1.0.0** (2025-12-06): Initial implementation
  - Planning orchestrator integration
  - ADO utility integration
  - Documentation reminder system
