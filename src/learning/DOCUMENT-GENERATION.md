# Learning System - Document Generation (Phase 2)

**Status:** ✅ COMPLETE | **Version:** 2.0.0 | **Date:** December 6, 2025

---

## Overview

Phase 2 extends the learning system with document generation capabilities that transform captured events into structured markdown documentation. Documents are organized into 15 learning categories with resource linking support.

### Key Features

- **Template-Based Generation:** 15 category-specific document templates
- **Resource Integration:** External resource database with categorized links
- **High Performance:** <10ms per document (target was <100ms)
- **Batch Processing:** Efficient multi-document generation
- **Persistence:** Automatic file path generation and storage
- **Error Handling:** Graceful degradation with skip-on-error support

---

## Architecture

```
src/learning/
├── event_collector.py       # Phase 1: Event capture
├── event_taxonomy.py         # Phase 1: Event definitions
├── document_generator.py     # Phase 2: Markdown generation ✨
└── resource_database.py      # Phase 2: Resource management ✨
```

### Document Generation Flow

```
Event Captured → Category Mapping → Template Selection → 
Metadata Extraction → Resource Injection → Markdown Formatting → 
Document Persistence
```

---

## Quick Start

### Basic Document Generation

```python
from src.learning import (
    LearningEvent,
    EventType,
    DocumentGenerator,
    get_global_collector
)

# Setup
collector = get_global_collector()
generator = DocumentGenerator()

# Capture event (Phase 1)
event = LearningEvent(
    EventType.PLAN_APPROVED,
    "PlanningOrchestrator",
    {"plan_filename": "feature-x.md", "task_count": 5}
)
collector.capture_event(event)

# Generate document (Phase 2)
doc = generator.generate_document(event)
print(doc)
```

### With Resource Integration

```python
from src.learning import ResourceDatabase

# Setup resources
db = ResourceDatabase()
db.add_resource(
    category='planning_strategies',
    title='Planning Best Practices',
    url='https://cortex.dev/planning',
    description='Guide to effective planning'
)

# Link to generator
generator = DocumentGenerator(resource_db=db)

# Generated documents now include resources
doc = generator.generate_document(event)
# Resources section automatically appended
```

### Batch Generation

```python
# Generate documents from all captured events
events = collector.get_milestone_events()
docs = generator.generate_documents(events)

# Save all documents
for i, doc in enumerate(docs):
    path = generator.save_document(doc, events[i])
    print(f"Saved: {path}")
```

---

## 15 Learning Categories

| Category | Events | Purpose |
|----------|--------|---------|
| `concepts` | General learning | Core concepts and principles |
| `patterns` | Code patterns | Design and implementation patterns |
| `milestones` | Completion events | Significant achievements |
| `resources` | External links | Documentation and guides |
| `ado_workflows` | ADO events | Azure DevOps workflows |
| `planning_strategies` | Planning events | Plan creation and approval |
| `workflow_context` | Workflow events | Operational workflows |
| `architectural_patterns` | Architecture | System design patterns |
| `code_quality` | Quality events | Code quality learnings |
| `design_decisions` | Design | Architectural decisions |
| `debugging_patterns` | Debug events | Problem-solving patterns |
| `productivity_patterns` | Productivity | Efficiency improvements |
| `operational_learnings` | Operations | Operational insights |
| `user_onboarding` | Onboarding | User guidance |
| `intent_routing` | Routing | Intent classification |

---

## Event-to-Category Mapping

### Must-Have Events (19)

**Planning & Execution (6)**
- `PLAN_CREATED` → planning_strategies
- `PLAN_APPROVED` → planning_strategies  
- `PLAN_ABANDONED` → planning_strategies
- `PHASE_STARTED` → workflow_context
- `PHASE_COMPLETED` → milestones
- `CHECKPOINT_COMMITTED` → milestones

**ADO Workflows (4)**
- `ADO_STORY_CREATED` → ado_workflows
- `ADO_FEATURE_CREATED` → ado_workflows
- `ADO_WORK_ITEM_COMPLETED` → milestones
- `ADO_ACCEPTANCE_CRITERIA_VALIDATED` → ado_workflows

**Workflow Routing (3)**
- `WORKFLOW_STARTED` → workflow_context
- `OPERATION_ROUTED` → intent_routing
- `WORKFLOW_COMPLETED` → milestones

**Planning Strategy (6)**
- `PLANNING_REQUEST` → planning_strategies
- `PLAN_STRATEGY_SELECTED` → planning_strategies
- `PLAN_VALIDATED` → milestones
- `INTERACTIVE_PLANNING_STARTED` → planning_strategies
- `CLARIFICATION_REQUESTED` → workflow_context
- `REQUIREMENTS_FINALIZED` → milestones

---

## Document Structure

### Generated Document Format

```markdown
# Event Name - Learning Document

**Event:** PLAN_CREATED
**Component:** PlanningOrchestrator
**Timestamp:** 2025-12-06 10:30:45
**Category:** planning_strategies

---

## Overview

This document captures learning from a PLAN_CREATED event 
in the PlanningOrchestrator component.

## Details

**Event Type:** PLAN_CREATED
**Source Component:** PlanningOrchestrator
**Milestone Event:** No

## Event Metadata

- **plan_filename:** feature-x.md
- **task_count:** 5

## Resources

### Planning Best Practices
**Link:** [https://cortex.dev/planning](https://cortex.dev/planning)

Guide to effective planning in CORTEX

---

*Generated: 2025-12-06 10:30:46*
```

---

## API Reference

### DocumentGenerator

**Constructor**
```python
DocumentGenerator(enabled: bool = True, resource_db: ResourceDatabase = None)
```

**Methods**

| Method | Description | Returns |
|--------|-------------|---------|
| `generate_document(event)` | Generate markdown from event | `str` |
| `generate_documents(events, skip_errors)` | Batch generation | `List[str]` |
| `save_document(doc, event)` | Save to filesystem | `str` (path) |
| `get_document_path(event)` | Get output path | `Path` |
| `document_exists(event)` | Check if exists | `bool` |
| `get_template(category)` | Get template | `Dict` |
| `get_template_for_event(event)` | Map event to template | `Dict` |

### ResourceDatabase

**Constructor**
```python
ResourceDatabase()
```

**Methods**

| Method | Description | Returns |
|--------|-------------|---------|
| `add_resource(category, title, url, desc)` | Add resource | `None` |
| `get_resources(category)` | Get by category | `List[Dict]` |
| `search_resources(query)` | Search all | `List[Dict]` |
| `get_all_resources()` | Get all | `Dict` |
| `remove_resource(category, title)` | Remove | `bool` |
| `clear_category(category)` | Clear category | `None` |
| `get_categories()` | List categories | `List[str]` |
| `get_resource_count()` | Count per category | `Dict[str, int]` |

---

## Performance Characteristics

### Benchmarks (December 2025)

| Metric | Target | Actual | Status |
|--------|--------|--------|--------|
| Single Document | <100ms | <10ms | ✅ Exceeded |
| Batch (20 docs) | <2000ms | <150ms | ✅ Exceeded |
| Template Loading | <50ms | <5ms | ✅ Exceeded |
| Resource Injection | <10ms | <2ms | ✅ Exceeded |

### Optimization Techniques

1. **Template Caching:** Templates loaded once, cached for reuse
2. **Lazy Evaluation:** Resources only loaded when needed
3. **String Building:** Efficient list concatenation
4. **Minimal Formatting:** Direct string operations over regex

---

## Integration Patterns

### With Event Collector

```python
# Complete pipeline
collector = get_global_collector()
generator = DocumentGenerator()

# Capture events from orchestrators (Phase 1)
for operation in operations:
    event = LearningEvent(...)
    collector.capture_event(event)

# Generate documents from milestones (Phase 2)
milestones = collector.get_milestone_events()
docs = generator.generate_documents(milestones)
```

### With Resource Database

```python
# Setup resources
db = ResourceDatabase()

# Populate planning resources
db.add_resource('planning_strategies', 'ADO Guide', 'http://ado.example.com')
db.add_resource('planning_strategies', 'TDD Workflow', 'http://tdd.example.com')

# Auto-inject into documents
generator = DocumentGenerator(resource_db=db)
doc = generator.generate_document(planning_event)  # Includes resources
```

### Error Handling

```python
# Graceful error handling
try:
    docs = generator.generate_documents(events, skip_errors=True)
except Exception as e:
    logger.error(f"Document generation failed: {e}")
    # Generator continues, logs errors, returns successful documents
```

---

## Testing

### Test Suite

**Phase 2 Tests:**
- 24 unit tests (test_document_generator.py)
- 7 integration tests (test_phase2_integration.py)
- **Total:** 31 new tests, all passing

**Full Learning System:**
- 33 Phase 1 tests (event collector)
- 1 Phase 1 integration test
- 31 Phase 2 tests (document generation)
- **Total:** 65 tests, 89% coverage

### Running Tests

```bash
# Phase 2 only
pytest tests/learning/test_document_generator.py -v
pytest tests/learning/test_phase2_integration.py -v

# Full learning system
pytest tests/learning/ -v --cov=src/learning

# Performance validation
pytest tests/learning/ -v -k "performance"
```

---

## File Organization

### Document Output Paths

```
cortex-brain/documents/learning/
├── planning_strategies/
│   ├── PLAN_CREATED_20251206_103045.md
│   └── PLAN_APPROVED_20251206_103046.md
├── milestones/
│   ├── PHASE_COMPLETED_20251206_103047.md
│   └── CHECKPOINT_COMMITTED_20251206_103048.md
├── ado_workflows/
│   └── ADO_STORY_CREATED_20251206_103049.md
└── ... (12 more categories)
```

**Path Pattern:** `cortex-brain/documents/learning/{category}/{event_type}_{timestamp}.md`

---

## Troubleshooting

### Common Issues

**1. Documents Not Generating**
- Check event has valid event_type
- Verify DocumentGenerator initialized
- Confirm event_type has category mapping

**2. Resources Not Appearing**
- Ensure ResourceDatabase linked to generator: `generator.resource_db = db`
- Verify resources added to correct category
- Check category matches event's mapped category

**3. Performance Issues**
- Use batch generation for multiple documents
- Ensure template caching enabled (default)
- Check for large metadata objects

**4. File Permission Errors**
- Verify `cortex-brain/documents/learning/` directory exists
- Check write permissions
- Ensure parent directories created (automatic in save_document)

---

## Future Phases

### Phase 3: Docsify UI Integration
- Learning dashboard launcher (separate from metrics dashboard)
- Docsify 4.13.1 integration
- Full-text search across documents
- Sidebar navigation by category
- Auto-fallback port selection (8080-8089)

### Phase 4: MVP Testing & Polish
- End-to-end validation with real workflows
- Performance tuning
- User documentation
- Production readiness

### Phase 5-7: Should-Have Events
- 15 architectural learning events
- 18 system operations events
- Complete 52-event taxonomy

---

## Success Metrics

**Phase 2 Completion:**
- ✅ 31 tests passing (24 unit + 7 integration)
- ✅ 89% overall coverage (385 statements)
- ✅ <10ms document generation (exceeded <100ms target)
- ✅ All 19 must-have events mapped to categories
- ✅ Resource database operational with 15 categories
- ✅ Document persistence working correctly
- ✅ Batch generation efficient (<150ms for 20 docs)
- ✅ Error handling graceful

---

**Document Version:** 1.0  
**Last Updated:** December 6, 2025  
**Author:** Asif Hussain  
**GitHub:** github.com/asifhussain60/CORTEX
