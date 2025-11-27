# Demo Orchestrator Guide

**Version:** 1.0  
**Status:** Production  
**Module:** src/operations/modules/demo/demo_orchestrator.py

---

## Overview

The Demo Orchestrator provides interactive demonstrations of CORTEX capabilities through guided tours of planning, TDD, testing, and brain features with hands-on examples.

## Key Features

- **Interactive Demos** - Guided tours with Q&A
- **Multiple Modules** - Planning, TDD, Brain, Integration
- **Hands-on Examples** - Real exercises with actual code
- **Session Tracking** - Progress saved across restarts
- **Full Tour Option** - 25-minute complete walkthrough

## Commands

```
demo
cortex demo
show demo
run demo
demo cortex
live demo
```

## Demo Modules Available

### 1. Planning Demo (5 min)
- Feature planning workflow
- DoR/DoD validation
- Incremental planning with checkpoints
- Vision API (screenshot → requirements)

### 2. TDD Demo (7 min)
- RED→GREEN→REFACTOR automation
- Auto-debug on test failures
- Performance-based refactoring
- Test location isolation

### 3. Brain Demo (5 min)
- Conversation capture
- Context injection
- Pattern learning
- Knowledge graph

### 4. Integration Demo (8 min)
- View discovery
- Code review
- ADO work items
- Complete workflow

### 5. Full Tour (25 min)
- All modules in sequence
- Hands-on exercises
- Q&A after each module

## Workflow

1. **Choose Demo Module** - Select from 5 options
2. **Interactive Presentation** - Step-by-step guided tour
3. **Hands-on Exercises** - Try features with examples
4. **Q&A Session** - Ask questions after each section
5. **Progress Tracking** - Resume where you left off

## Demo Session Structure

```python
class DemoSession:
    session_id: str
    module_name: str
    start_time: datetime
    exercises_completed: List[str]
    questions_asked: List[str]
    completion_status: str
```

## Integration

- Response-templates.yaml for triggers
- Brain memory for session tracking
- Tier 1 for demo progress storage
- Interactive CLI interface

## Use Cases

- **New Users** - Learn CORTEX through practical examples
- **Feature Discovery** - Explore capabilities interactively
- **Training** - Onboard team members
- **Validation** - Verify installation and setup
- **Marketing** - Showcase CORTEX to stakeholders

## Performance

- Module load time: <1 second
- Exercise execution: 1-3 seconds each
- Session tracking: <0.5 seconds
- Total demo time: 5-25 minutes (user-paced)

## Session Persistence

- Demo progress saved to Tier 1
- Resume capability across restarts
- Exercise completion tracked
- Q&A history preserved

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)
