# Post-Installation Workflow Integration

**Author:** Asif Hussain  
**Created:** 2025-11-26  
**Version:** 1.0.0

---

## 🎯 Overview

After successful CORTEX setup, users are presented with three options:
1. **Demo** - See CORTEX capabilities demonstration
2. **Analyze** - Onboard and analyze current repository
3. **Skip** - Start working immediately

This document describes the integration between setup completion and the demo/onboarding orchestrators.

---

## 🏗️ Architecture

### Flow Diagram

```
Setup Orchestrator
       ↓
Setup Completion Module (generates prompt)
       ↓
User Input (via Copilot Chat)
       ↓
Post-Installation Handler (detects choice)
       ↓
       ├─→ Demo Orchestrator (if demo)
       ├─→ Onboarding Module (if analyze)
       └─→ General Help (if skip)
```

---

## 📋 Components

### 1. Setup Completion Module
**Location:** `src/operations/modules/setup_completion_module.py`

**Responsibilities:**
- Generate setup summary report
- Display post-installation prompt
- Set `awaiting_user_choice` flag in context

**Key Changes:**
```python
def _generate_post_installation_prompt(self, context: Dict[str, Any]) -> str:
    """Generate interactive prompt with 3 options"""
    # Returns formatted prompt with:
    # 1. Demo option
    # 2. Analyze option
    # 3. Skip/help option
```

### 2. Post-Installation Handler
**Location:** `src/setup/post_installation_handler.py`

**Responsibilities:**
- Detect user choice from natural language input
- Route to appropriate orchestrator
- Pass context forward

**API:**
```python
from src.setup import handle_post_installation_choice

# Process user's response
result = handle_post_installation_choice(setup_context, user_input)

# Returns routing dict:
{
    'action': 'demo' | 'analyze' | 'skip',
    'orchestrator': 'demo' | 'onboarding' | None,
    'template_id': 'introduction_discovery' | 'general_help',
    'context': {...}  # Forwarded context
}
```

### 3. Demo Orchestrator
**Location:** `src/operations/modules/demo/demo_orchestrator.py`

**Responsibilities:**
- Show CORTEX capabilities overview
- Provide feature demonstrations
- Route to specific demo types

**Integration:**
```python
from src.operations.modules.demo import DemoOrchestrator

orchestrator = DemoOrchestrator()
response = orchestrator.handle_discovery(
    user_request="show me CORTEX capabilities",
    context={'post_installation': True}
)
```

### 4. Onboarding Module
**Location:** `src/setup/modules/onboarding_module.py`

**Responsibilities:**
- Analyze user's codebase
- Generate improvement recommendations
- Store analysis in CORTEX brain

**Integration:**
```python
from src.setup.modules.onboarding_module import OnboardingModule

module = OnboardingModule()
result = module.execute(context={
    'user_project_root': '/path/to/user/repo',
    'project_root': '/path/to/cortex',
    'brain_initialized': True,
    'post_installation': True
})
```

---

## 🔄 User Interaction Flow

### Step 1: Setup Completion
```
CORTEX Setup Complete!

Modules Processed: 5
  ✓ Successful:    5
  ⚠ Warnings:      0
  ✗ Failures:      0
  ⊘ Skipped:       0

============================================================
🎉 CORTEX INSTALLATION COMPLETE!
============================================================

What would you like to do next?

1. 📚 **See a demo** - Interactive demo of CORTEX capabilities
   Say: 'show me a demo' or 'demo cortex'

2. 🔍 **Analyze current repository** - Get insights and recommendations
   Say: 'analyze this repo' or 'onboard application'

3. 🚀 **Start working** - Jump right in with CORTEX
   Say: 'help' to see all available commands

============================================================
```

### Step 2: User Response Examples

**Option 1 - Demo:**
```
User: "show me a demo"
     OR "demo cortex"
     OR "what can you do"

Handler detects: 'demo'
Routes to: DemoOrchestrator
```

**Option 2 - Analyze:**
```
User: "analyze this repo"
     OR "onboard application"
     OR "scan my code"

Handler detects: 'analyze'
Routes to: OnboardingModule
```

**Option 3 - Skip:**
```
User: "skip"
     OR "help"
     OR "start working"

Handler detects: 'skip'
Routes to: General Help Template
```

---

## 🧪 Testing

### Unit Tests

**Test post-installation handler:**
```python
# Test in: tests/setup/test_post_installation_handler.py

def test_detect_demo_choice():
    handler = PostInstallationHandler(context)
    assert handler.detect_user_choice("show me a demo") == 'demo'
    assert handler.detect_user_choice("demo cortex") == 'demo'

def test_detect_analyze_choice():
    handler = PostInstallationHandler(context)
    assert handler.detect_user_choice("analyze repo") == 'analyze'
    assert handler.detect_user_choice("onboard") == 'analyze'

def test_detect_skip_choice():
    handler = PostInstallationHandler(context)
    assert handler.detect_user_choice("skip") == 'skip'
    assert handler.detect_user_choice("help") == 'skip'
```

### Integration Tests

**Test full workflow:**
```python
# Test in: tests/integration/test_post_installation_workflow.py

def test_setup_to_demo_flow():
    # 1. Run setup
    report = run_setup(profile='standard')
    assert report.overall_success
    
    # 2. Get context
    context = report.context
    assert context['awaiting_user_choice'] == True
    
    # 3. Process user choice
    result = handle_post_installation_choice(context, "demo")
    assert result['action'] == 'demo'
    assert result['orchestrator'] == 'demo'
```

---

## 📝 Configuration

### Trigger Keywords

**Demo triggers:**
- demo, show me, demonstrate, tour, capabilities
- what can you do, features, show features, see demo

**Analyze triggers:**
- analyze, onboard, analyze repo, analyze repository
- analyze this, scan, review, inspect, check repo

**Skip triggers:**
- skip, no, later, start working, get started
- jump in, begin, help

### Context Flags

```python
context = {
    'setup_complete': True,              # Setup finished successfully
    'awaiting_user_choice': True,        # Expecting post-install choice
    'post_installation': True,           # From post-install flow
    'brain_initialized': bool,           # Brain available for analysis
    'user_project_root': str,           # User's repo path
    'project_root': str                  # CORTEX installation path
}
```

---

## 🔧 Maintenance

### Adding New Post-Installation Options

1. **Update prompt** in `_generate_post_installation_prompt()`
2. **Add trigger keywords** in `detect_user_choice()`
3. **Create handler method** (e.g., `handle_new_choice()`)
4. **Add to handlers dict** in `process_user_choice()`
5. **Update tests** to cover new choice

### Modifying Existing Options

1. Update trigger detection in `PostInstallationHandler`
2. Modify handler method logic
3. Update integration tests
4. Document changes in this file

---

## 🚨 Error Handling

### Missing Context
```python
if not context.get('project_root'):
    logger.warning("project_root not in context, using cwd")
    context['project_root'] = Path.cwd()
```

### Invalid Choice
```python
# Default to demo if choice unclear
choice = detect_user_choice(user_input)
if choice not in ['demo', 'analyze', 'skip']:
    choice = 'demo'
```

### Orchestrator Failure
```python
try:
    orchestrator = DemoOrchestrator()
    response = orchestrator.handle_discovery(...)
except Exception as e:
    logger.error(f"Demo orchestrator failed: {e}")
    return {'action': 'skip', 'template_id': 'general_help'}
```

---

## 📊 Metrics

Track post-installation choices in Tier 3:

```python
# Store user choice
tier3.store_metric('post_install_choice', {
    'choice': choice,
    'timestamp': datetime.now(),
    'setup_profile': context.get('setup_profile')
})
```

**Analysis queries:**
```sql
-- Most popular choice
SELECT choice, COUNT(*) FROM post_install_choices GROUP BY choice;

-- Choice by setup profile
SELECT setup_profile, choice, COUNT(*) 
FROM post_install_choices 
GROUP BY setup_profile, choice;
```

---

## ✅ Success Criteria

- [ ] Setup completion shows post-installation prompt
- [ ] User can choose demo/analyze/skip via natural language
- [ ] Demo choice routes to DemoOrchestrator
- [ ] Analyze choice triggers OnboardingModule
- [ ] Skip choice shows help information
- [ ] All choices logged to Tier 3
- [ ] Context preserved across transitions
- [ ] Error handling prevents crashes

---

**Status:** ✅ Implementation Complete  
**Next Review:** After initial user feedback  
**Owner:** Asif Hussain
