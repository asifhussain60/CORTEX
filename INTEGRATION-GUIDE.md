# CORTEX 2.0 Integration Guide for Application Repositories

**Version:** 2.0.0  
**Release Date:** November 13, 2025  
**Status:** ✅ Production Ready

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file for terms

---

## 🎯 Quick Start

### Step 1: Add CORTEX to Your Application

**Option A: Git Submodule (Recommended)**

```bash
# In your application repository
cd /path/to/your-application

# Add CORTEX as submodule
git submodule add https://github.com/asifhussain60/CORTEX.git CORTEX

# Initialize and update
git submodule init
git submodule update

# Lock to v2.0.0 production release
cd CORTEX
git checkout v2.0.0
cd ..

# Commit the submodule
git add .gitmodules CORTEX
git commit -m "Add CORTEX 2.0 as submodule"
```

**Option B: Direct Copy**

```bash
# Clone CORTEX
git clone https://github.com/asifhussain60/CORTEX.git

# Checkout production version
cd CORTEX
git checkout v2.0.0

# Copy to your application
cp -r CORTEX /path/to/your-application/CORTEX
```

---

## 📂 Application Repository Structure

```
your-application/
├── src/
│   └── your_app.py              # Your application code
├── CORTEX/                       # CORTEX framework (git submodule or copy)
│   ├── src/
│   │   ├── tier0/                # SKULL governance
│   │   ├── tier1/                # Conversation memory
│   │   ├── tier2/                # Knowledge graph
│   │   ├── tier3/                # Context intelligence
│   │   ├── cortex_agents/        # 10 specialist agents
│   │   └── plugins/              # Plugin system
│   ├── cortex-brain/             # Brain data (Tier 0-3 storage)
│   ├── prompts/                  # Entry points and documentation
│   ├── tests/                    # CORTEX test suite
│   └── requirements.txt          # CORTEX dependencies
├── requirements.txt              # Your app dependencies
└── README.md
```

---

## 🔧 Integration Patterns

### Pattern 1: Basic Import and Use

```python
# your-application/src/your_app.py

import sys
import os

# Add CORTEX to Python path
cortex_path = os.path.join(os.path.dirname(__file__), '..', 'CORTEX')
sys.path.insert(0, cortex_path)

# Import CORTEX components
from src.cortex_agents import get_agent
from src.tier1.conversation_tracker import ConversationTracker
from src.tier2.knowledge_graph import KnowledgeGraph

# Use CORTEX agents
def process_with_cortex(user_request: str):
    """Process user request using CORTEX agents."""
    
    # Get executor agent
    executor = get_agent('executor')
    
    # Track conversation in Tier 1
    tracker = ConversationTracker()
    conversation_id = tracker.start_conversation(
        intent='EXECUTE',
        user_message=user_request
    )
    
    # Execute with agent
    result = executor.execute(user_request)
    
    # Save to conversation memory
    tracker.add_message(
        conversation_id=conversation_id,
        role='assistant',
        content=result
    )
    
    return result

# Example usage
if __name__ == '__main__':
    result = process_with_cortex("Implement user authentication")
    print(result)
```

### Pattern 2: Agent Coordination

```python
# Use multiple CORTEX agents together

from src.cortex_agents import get_agent

def plan_and_execute_feature(feature_description: str):
    """Plan a feature using Interactive Planner, then execute."""
    
    # Step 1: Plan with Interactive Planner (RIGHT brain)
    planner = get_agent('interactive_planner')
    plan = planner.create_plan(feature_description)
    
    # Step 2: Execute with Executor (LEFT brain)
    executor = get_agent('executor')
    implementation = executor.execute(plan)
    
    # Step 3: Test with Tester (LEFT brain)
    tester = get_agent('tester')
    test_results = tester.generate_tests(implementation)
    
    # Step 4: Validate with Validator (LEFT brain)
    validator = get_agent('validator')
    validation = validator.validate(implementation, test_results)
    
    return {
        'plan': plan,
        'implementation': implementation,
        'tests': test_results,
        'validation': validation
    }
```

### Pattern 3: Knowledge Graph Learning

```python
# Learn from interactions and retrieve patterns

from src.tier2.knowledge_graph import KnowledgeGraph

def learn_from_interaction(interaction_data: dict):
    """Store learned patterns in CORTEX knowledge graph."""
    
    kg = KnowledgeGraph()
    
    # Add lesson to knowledge graph
    lesson_id = kg.add_lesson(
        title=f"Lesson: {interaction_data['topic']}",
        description=interaction_data['what_learned'],
        confidence=interaction_data['confidence'],
        tags=interaction_data['tags']
    )
    
    return lesson_id

def retrieve_similar_patterns(topic: str):
    """Retrieve similar patterns from knowledge graph."""
    
    kg = KnowledgeGraph()
    similar_lessons = kg.search_lessons(query=topic, limit=5)
    
    return similar_lessons
```

### Pattern 4: SKULL Protection in Your App

```python
# Use CORTEX SKULL rules to protect your application

from src.tier0.brain_protector import BrainProtector

def safe_deployment(code_changes: list):
    """Use SKULL protection before deploying."""
    
    protector = BrainProtector()
    
    # Check SKULL-001: Test Before Claim
    test_results = run_tests()  # Your test runner
    if not protector.validate_test_coverage(test_results):
        raise Exception("SKULL-001 violation: Tests must pass before deployment")
    
    # Check SKULL-002: Integration Verification
    integration_tests = run_integration_tests()
    if not protector.validate_integration(integration_tests):
        raise Exception("SKULL-002 violation: Integration tests required")
    
    # Safe to deploy
    deploy(code_changes)
```

---

## 📊 Feature Usage Examples

### Token Optimization

```python
# Use CORTEX token optimization in your responses

from src.tier2.token_optimizer import TokenOptimizer

def generate_response(prompt: str):
    """Generate token-optimized response."""
    
    optimizer = TokenOptimizer()
    
    # Optimize prompt before sending to LLM
    optimized_prompt = optimizer.compress(prompt)
    
    # Your LLM call here
    response = your_llm_call(optimized_prompt)
    
    # Track token savings
    savings = optimizer.calculate_savings(prompt, optimized_prompt)
    print(f"Token savings: {savings['percentage']}%")
    
    return response
```

### Conversation Tracking

```python
# Track multi-turn conversations with CORTEX Tier 1

from src.tier1.conversation_tracker import ConversationTracker

class ChatBot:
    def __init__(self):
        self.tracker = ConversationTracker()
        self.conversation_id = None
    
    def start_conversation(self, user_message: str):
        """Start new conversation."""
        self.conversation_id = self.tracker.start_conversation(
            intent='CHAT',
            user_message=user_message
        )
    
    def continue_conversation(self, user_message: str):
        """Continue existing conversation."""
        
        # Get conversation context (last 20 messages)
        context = self.tracker.get_conversation_context(
            self.conversation_id
        )
        
        # Use context to generate response
        response = self.generate_response(user_message, context)
        
        # Save exchange to memory
        self.tracker.add_message(
            conversation_id=self.conversation_id,
            role='user',
            content=user_message
        )
        self.tracker.add_message(
            conversation_id=self.conversation_id,
            role='assistant',
            content=response
        )
        
        return response
```

---

## 🔌 Plugin System Integration

### Load and Use CORTEX Plugins

```python
# Use CORTEX plugins in your application

from src.plugins.plugin_registry import PluginRegistry

def setup_cortex_plugins():
    """Initialize CORTEX plugins."""
    
    registry = PluginRegistry()
    
    # Auto-discover all plugins
    plugins = registry.discover_plugins()
    
    # Initialize each plugin
    for plugin in plugins:
        plugin.initialize()
    
    return registry

def use_platform_detection():
    """Example: Use platform detection plugin."""
    
    registry = setup_cortex_plugins()
    platform_plugin = registry.get_plugin('platform_switch')
    
    # Detect current platform
    platform_info = platform_plugin.detect_platform()
    
    print(f"Running on: {platform_info['os']}")
    print(f"Shell: {platform_info['shell']}")
    
    # Get platform-specific commands
    commands = platform_plugin.get_platform_commands()
    return commands
```

---

## 📦 Dependencies

### Install CORTEX Dependencies

```bash
# Option 1: Install CORTEX dependencies separately
pip install -r CORTEX/requirements.txt

# Option 2: Merge with your app requirements
cat CORTEX/requirements.txt >> requirements.txt
pip install -r requirements.txt
```

### CORTEX Requirements

```txt
# Core dependencies (from CORTEX/requirements.txt)
pyyaml>=6.0
pytest>=7.0.0
pytest-cov>=4.0.0
pytest-mock>=3.10.0
pytest-xdist>=3.0.0
```

---

## 🎯 Common Use Cases

### Use Case 1: AI-Powered Code Assistant

```python
# Build code assistant using CORTEX agents

from src.cortex_agents import get_agent

class CodeAssistant:
    def __init__(self):
        self.executor = get_agent('executor')
        self.tester = get_agent('tester')
        self.architect = get_agent('architect')
    
    def implement_feature(self, description: str):
        """Implement feature with tests."""
        code = self.executor.execute(description)
        tests = self.tester.generate_tests(code)
        return {'code': code, 'tests': tests}
    
    def review_architecture(self, design: str):
        """Review system architecture."""
        return self.architect.review(design)
```

### Use Case 2: Intelligent Documentation Generator

```python
# Auto-generate documentation using CORTEX

from src.cortex_agents import get_agent

class DocGenerator:
    def __init__(self):
        self.documenter = get_agent('documenter')
    
    def generate_docs(self, codebase_path: str):
        """Generate documentation from codebase."""
        return self.documenter.document_codebase(codebase_path)
```

### Use Case 3: Project Health Monitor

```python
# Monitor project health using CORTEX Tier 3

from src.tier3.context.brain_metrics_collector import BrainMetricsCollector

class ProjectMonitor:
    def __init__(self):
        self.metrics = BrainMetricsCollector()
    
    def check_health(self, project_path: str):
        """Check project health metrics."""
        
        health_report = self.metrics.collect_project_health(
            project_path
        )
        
        return {
            'test_coverage': health_report['test_coverage'],
            'code_quality': health_report['code_quality'],
            'technical_debt': health_report['technical_debt'],
            'recommendations': health_report['recommendations']
        }
```

---

## 🚀 Production Deployment

### Pre-Deployment Checklist

```python
# Use CORTEX validation before production deployment

from src.tier0.brain_protector import BrainProtector

def pre_deployment_check():
    """Run CORTEX pre-deployment validation."""
    
    protector = BrainProtector()
    
    checks = [
        ('SKULL-001', 'Test coverage >= 80%'),
        ('SKULL-002', 'Integration tests pass'),
        ('SKULL-003', 'No visual regressions'),
        ('SKULL-007', '100% critical tests pass')
    ]
    
    for rule, description in checks:
        if not protector.validate_rule(rule):
            raise Exception(f"{rule} failed: {description}")
    
    print("✅ All CORTEX pre-deployment checks passed")
```

---

## 📖 Documentation Reference

| Resource | Location in CORTEX |
|----------|-------------------|
| **Entry Point** | `CORTEX/.github/prompts/CORTEX.prompt.md` |
| **Story** | `CORTEX/prompts/shared/story.md` |
| **Setup Guide** | `CORTEX/prompts/shared/setup-guide.md` |
| **Technical Docs** | `CORTEX/prompts/shared/technical-reference.md` |
| **Agents Guide** | `CORTEX/prompts/shared/agents-guide.md` |
| **Plugin System** | `CORTEX/prompts/shared/plugin-system.md` |
| **Operations** | `CORTEX/prompts/shared/operations-reference.md` |

---

## 🎓 Support and Troubleshooting

### Common Issues

**Issue: CORTEX modules not found**

```python
# Solution: Ensure CORTEX in Python path
import sys
import os
cortex_path = os.path.abspath('CORTEX')
sys.path.insert(0, cortex_path)
```

**Issue: SQLite database errors**

```python
# Solution: Initialize Tier 1 database
from src.tier1.conversation_tracker import ConversationTracker
tracker = ConversationTracker()
tracker.initialize_database()  # Creates conversations.db
```

**Issue: Plugin discovery fails**

```python
# Solution: Set CORTEX_ROOT environment variable
import os
os.environ['CORTEX_ROOT'] = os.path.abspath('CORTEX')
```

---

## ✅ Validation

**Before using CORTEX in production, validate:**

- [ ] CORTEX imported successfully
- [ ] Tier 1 database created (`CORTEX/cortex-brain/conversations.db`)
- [ ] At least one agent executes successfully
- [ ] SKULL protection rules load from YAML
- [ ] Knowledge graph accessible
- [ ] Plugins discover and initialize

**Test command:**

```bash
cd CORTEX
pytest tests/tier0/test_brain_protector.py tests/cortex_agents/ -v
# Should see: 43 passed
```

---

## 🎯 Next Steps

1. **Integrate CORTEX into your application** (use patterns above)
2. **Test integration** (validate core features work)
3. **Deploy to development environment** (test in real conditions)
4. **Monitor and iterate** (use CORTEX learning to improve)

---

**Integration Support:** See `CORTEX/cortex-brain/CORTEX-2.0-PRODUCTION-READINESS-REPORT.md`  
**Version:** CORTEX 2.0.0 (Production Release)  
**Tags:** v2.0.0, CORTEX-2.0-STABLE, CORTEX-2.0-FINAL

---

*"CORTEX 2.0: 4-Tier Brain, 10 Agents, 97.2% Token Optimization. Production Ready."*
