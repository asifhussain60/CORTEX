# CORTEX 2.0 Design Document Update Plan

**Date:** 2025-11-10  
**Purpose:** Actionable plan to align design documents with current implementation  
**Status:** 🎯 READY TO EXECUTE

---

## 📋 Overview

This document provides step-by-step instructions to update CORTEX 2.0 design documents based on the gap analysis findings. All improvements are prioritized and time-estimated.

**Total Effort:** 58-70 hours (spread across remaining phases)  
**This Session:** 6-7 hours (HIGH priority items)

---

## 🎯 Session 1: Core Document Updates (6-7 hours)

### Task 1: Update cortex-operations.yaml (1 hour)

**Goal:** Add status tracking for all 70 modules

**Script to Run:**
```python
# scripts/update_operations_status.py
import yaml

STATUS_MAP = {
    # Implemented modules (10 total)
    "platform_detection": {"status": "implemented", "tests": 15, "date": "2025-11-09"},
    "vision_api": {"status": "implemented", "tests": 12, "date": "2025-11-09"},
    "python_dependencies": {"status": "implemented", "tests": 8, "date": "2025-11-09"},
    "brain_initialization": {"status": "implemented", "tests": 10, "date": "2025-11-09"},
    "load_story_template": {"status": "implemented", "tests": 5, "date": "2025-11-09"},
    "apply_narrator_voice": {"status": "implemented", "tests": 8, "date": "2025-11-09"},
    "validate_story_structure": {"status": "implemented", "tests": 6, "date": "2025-11-09"},
    "save_story_markdown": {"status": "implemented", "tests": 5, "date": "2025-11-09"},
    "update_mkdocs_index": {"status": "implemented", "tests": 4, "date": "2025-11-09"},
    "build_story_preview": {"status": "implemented", "tests": 3, "date": "2025-11-09"},
    
    # Pending modules with estimates (60 remaining)
    "project_validation": {"status": "pending", "estimated_hours": 1.5},
    "git_sync": {"status": "pending", "estimated_hours": 2.0},
    "virtual_environment": {"status": "pending", "estimated_hours": 2.5},
    "conversation_tracking": {"status": "pending", "estimated_hours": 3.0},
    "brain_tests": {"status": "pending", "estimated_hours": 2.0},
    "tooling_verification": {"status": "pending", "estimated_hours": 1.5},
    "setup_completion": {"status": "pending", "estimated_hours": 1.0},
    # ... add all 60 remaining modules
}

# Load YAML
with open("cortex-operations.yaml", "r") as f:
    data = yaml.safe_load(f)

# Update modules
for module_id, info in data["modules"].items():
    if module_id in STATUS_MAP:
        data["modules"][module_id].update(STATUS_MAP[module_id])

# Save updated YAML
with open("cortex-operations.yaml", "w") as f:
    yaml.dump(data, f, default_flow_style=False, sort_keys=False)

print("✅ Updated cortex-operations.yaml with status fields")
```

**Run command:**
```bash
python scripts/update_operations_status.py
```

**Validation:**
```bash
# Check that status field appears in all modules
grep -c "status:" cortex-operations.yaml  # Should be 70
```

**Expected Outcome:**
- All 70 modules have `status: "implemented" | "pending"`
- Implemented modules have `tests: N` and `implemented_date`
- Pending modules have `estimated_hours: N`

---

### Task 2: Convert Priority Docs to YAML (3-4 hours)

**Goal:** Convert 10-12 verbose MD docs to structured YAML

**Priority Order:**

#### A. Operation Configurations (1.5 hours)

**Create:** `cortex-brain/operations-config.yaml`

```yaml
# Consolidates operation-specific configurations
# Replaces: Sections from CORTEX-2.0-IMPLEMENTATION-STATUS.md

operations_config:
  environment_setup:
    enabled: true
    default_profile: "standard"
    timeout_minutes: 15
    retry_on_failure: true
    max_retries: 3
    
    profiles:
      minimal:
        enabled_modules: ["platform_detection", "virtual_environment", "python_dependencies", "brain_initialization", "setup_completion"]
        estimated_duration_minutes: 5
        
      standard:
        enabled_modules: ["platform_detection", "git_sync", "virtual_environment", "python_dependencies", "vision_api", "brain_initialization", "brain_tests", "setup_completion"]
        estimated_duration_minutes: 10
        
      full:
        enabled_modules: ["all"]
        estimated_duration_minutes: 15
        
  refresh_cortex_story:
    enabled: true
    default_profile: "standard"
    timeout_minutes: 5
    source_file: "prompts/shared/story.md"
    output_file: "docs/story/CORTEX-STORY/Technical-CORTEX.md"
    
  workspace_cleanup:
    enabled: false  # Not implemented yet
    default_profile: "safe"
    timeout_minutes: 3
    
  # ... all operations
```

**Benefits:**
- Single source of truth for operation settings
- Machine-readable
- Easy to validate
- ~40% token reduction vs MD

---

#### B. Module Definitions (1 hour)

**Create:** `cortex-brain/module-definitions.yaml`

```yaml
# Consolidates module implementation details
# Replaces: Sections from CORTEX-2.0-IMPLEMENTATION-STATUS.md

module_definitions:
  platform_detection:
    status: implemented
    implementation_file: "src/operations/modules/platform_detection_module.py"
    lines_of_code: 156
    tests: 15
    test_file: "tests/operations/test_platform_detection.py"
    dependencies: []
    outputs:
      - platform_name  # "darwin", "windows", "linux"
      - architecture  # "x64", "arm64"
      - shell_type  # "bash", "zsh", "pwsh"
    
  load_story_template:
    status: implemented
    implementation_file: "src/operations/modules/load_story_template_module.py"
    lines_of_code: 89
    tests: 5
    test_file: "tests/operations/test_load_story_template.py"
    dependencies: []
    outputs:
      - story_content  # Raw Markdown string
      - chapter_count  # Number of chapters
      
  # ... all 70 modules
```

**Benefits:**
- Quick reference for module status
- Easy to generate reports
- CI/CD integration
- ~35% token reduction vs MD

---

#### C. Command Discovery Configuration (1 hour)

**Create:** `cortex-brain/command-discovery-config.yaml`

```yaml
# CORTEX 2.1 Command Discovery System Configuration
# Replaces: Sections from CORTEX-COMMAND-DISCOVERY-SYSTEM.md

command_discovery:
  enabled: false  # CORTEX 2.1 feature
  implementation_status: "designed_not_implemented"
  target_release: "Week 21-22"
  
  layers:
    1_natural_language:
      enabled: true
      confidence_threshold: 0.75
      fallback_to_help: true
      
    2_slash_commands:
      enabled: true
      require_exact_match: false
      fuzzy_threshold: 0.8
      
    3_contextual_suggestions:
      enabled: false  # Pending implementation
      max_suggestions: 3
      relevance_threshold: 0.7
      
    4_visual_aids:
      enabled: false  # Pending implementation
      show_examples: true
      show_categories: true
      
    5_progressive_disclosure:
      enabled: false  # Pending implementation
      user_level: "auto_detect"  # beginner, intermediate, expert
      
  help_command:
    formats:
      - quick  # 5-7 most relevant commands
      - standard  # All commands with categories
      - detailed  # Full documentation per command
    default_format: "standard"
    
  search_command:
    enabled: true
    fuzzy_matching: true
    synonym_expansion: true
    max_results: 10
```

**Benefits:**
- Clear CORTEX 2.1 roadmap
- Feature flags for gradual rollout
- Machine-readable settings
- ~50% token reduction vs MD

---

#### D. Slash Commands Guide (30 min)

**Create:** `cortex-brain/slash-commands-guide.yaml`

```yaml
# Slash Commands vs Natural Language Guide
# Addresses Issue #5 from gap analysis

slash_commands:
  philosophy: "Optional shortcuts - natural language preferred"
  
  when_to_use_natural_language:
    - "First-time users (more intuitive)"
    - "Complex multi-part requests"
    - "When unsure of exact command"
    - "Exploratory work sessions"
    
  when_to_use_slash_commands:
    - "Frequent repeated operations"
    - "Power users (faster typing)"
    - "Scripting/automation"
    - "Clear single-intent actions"
  
  all_commands:
    setup:
      slash: "/setup"
      aliases: ["/env", "/environment", "/configure"]
      natural_language:
        - "setup environment"
        - "configure cortex"
        - "initialize environment"
        - "get started"
      when_to_use: "First-time setup or platform reconfiguration"
      example: "/setup full  # Use full profile"
      
    help:
      slash: "/help"
      natural_language:
        - "help"
        - "show commands"
        - "what can you do"
      when_to_use: "Discovering available commands"
      example: "/help search cleanup  # Find cleanup commands"
      
    resume:
      slash: "/resume"
      natural_language:
        - "continue work"
        - "resume where I left off"
        - "continue previous session"
      when_to_use: "Continuing previous work session"
      example: "/resume  # Load last conversation"
      
    # ... all commands from operations.yaml
    
  best_practices:
    - name: "Start with natural language"
      reason: "More flexible, better for exploration"
      
    - name: "Learn slash commands gradually"
      reason: "Pick up shortcuts for frequent tasks"
      
    - name: "Both work equally well"
      reason: "No technical difference, just preference"
      
    - name: "Mix and match"
      reason: "Use what feels natural in the moment"
```

**Benefits:**
- Clear guidance for users
- Reduces confusion about when to use what
- Machine-readable for /help integration
- ~45% token reduction vs MD guide

---

### Task 3: Update Technical Documentation (2 hours)

**Goal:** Fix tier class names throughout technical docs

#### A. Update `prompts/shared/technical-reference.md` (45 min)

**Find and replace:**
```markdown
OLD:
from tier1.working_memory_engine import WorkingMemoryEngine
from tier2.knowledge_graph_engine import KnowledgeGraphEngine
from tier3.dev_context_engine import DevContextEngine

NEW:
from src.tier1.working_memory import WorkingMemory
from src.tier2.knowledge_graph.knowledge_graph import KnowledgeGraph
from src.tier3.context_intelligence import ContextIntelligence
```

**Update API reference section:**
```markdown
## Tier 1: Working Memory API

```python
from src.tier1.working_memory import WorkingMemory

wm = WorkingMemory("cortex-brain.db")

# Add message
wm.add_message(
    conversation_id="conv_123",
    role="user",
    content="Add authentication"
)

# Get recent messages
messages = wm.get_recent_messages(conversation_id="conv_123", limit=20)
\`\`\`

## Tier 2: Knowledge Graph API

\`\`\`python
from src.tier2.knowledge_graph.knowledge_graph import KnowledgeGraph

kg = KnowledgeGraph()

# Add pattern
kg.add_pattern(
    pattern_id="auth_pattern",
    description="Authentication implementation pattern",
    context={"framework": "Django"}
)

# Search patterns
patterns = kg.search_patterns(query="authentication", limit=5)
\`\`\`
```

---

#### B. Update `prompts/shared/agents-guide.md` (30 min)

**Update tier usage examples:**
```markdown
## How Agents Use Tiers

### Executor Agent
Uses Tier 1 (Working Memory) to recall previous implementations:

```python
from src.tier1.working_memory import WorkingMemory

class Executor:
    def execute(self, task):
        wm = WorkingMemory()
        # Check if we've done similar work before
        prev_tasks = wm.search_similar_tasks(task.description)
\`\`\`
```

---

#### C. Update `CORTEX-2.0-2.1-INTEGRATION-ANALYSIS.md` (45 min)

**Update dependency section:**
```markdown
## Dependencies

**CORTEX 2.1 Requires:**
- ✅ Plugin System (2.0 Phase 2) - Complete
- ✅ Tier 1 Memory (2.0 Phase 1) - Complete
  - Class: `WorkingMemory` (NOT `WorkingMemoryEngine`)
  - Module: `src.tier1.working_memory`
- ✅ Tier 2 Knowledge (2.0 Phase 1) - Complete
  - Class: `KnowledgeGraph` (NOT `KnowledgeGraphEngine`)
  - Module: `src.tier2.knowledge_graph.knowledge_graph`
- ✅ Tier 3 Context (2.0 Phase 1) - Complete
  - Class: `ContextIntelligence` (NOT `DevContextEngine`)
  - Module: `src.tier3.context_intelligence`
```

---

## 📊 Session 1 Completion Checklist

### Must Complete (6-7 hours)
- [ ] Update cortex-operations.yaml with status fields (1h)
  - Script: `scripts/update_operations_status.py`
  - Validation: `grep -c "status:" cortex-operations.yaml` = 70
  
- [ ] Create `operations-config.yaml` (1.5h)
  - Location: `cortex-brain/operations-config.yaml`
  - Lines: ~300 (estimated)
  
- [ ] Create `module-definitions.yaml` (1h)
  - Location: `cortex-brain/module-definitions.yaml`
  - Lines: ~500 (estimated)
  
- [ ] Create `command-discovery-config.yaml` (1h)
  - Location: `cortex-brain/command-discovery-config.yaml`
  - Lines: ~200 (estimated)
  
- [ ] Create `slash-commands-guide.yaml` (30min)
  - Location: `cortex-brain/slash-commands-guide.yaml`
  - Lines: ~150 (estimated)
  
- [ ] Update technical-reference.md (45min)
  - Fix tier imports (3 places)
  - Update API examples
  
- [ ] Update agents-guide.md (30min)
  - Fix tier usage examples
  
- [ ] Update CORTEX-2.0-2.1-INTEGRATION-ANALYSIS.md (45min)
  - Fix dependency section

### Optional (Nice to Have)
- [ ] Run tests after changes: `pytest tests/ -v`
- [ ] Update CORTEX.prompt.md to reference new YAML files
- [ ] Commit changes with descriptive message

---

## 🎯 Session 2: Architecture Documentation (4-6 hours)

### Task 4: Create Unified Architecture Document

**Goal:** Single source of truth for CORTEX architecture

**Create:** `CORTEX-UNIFIED-ARCHITECTURE.yaml`

```yaml
# CORTEX 2.0 + 2.1 Unified Architecture
# Consolidates 47+ scattered design documents

architecture:
  version: "2.0 + 2.1 Integration"
  last_updated: "2025-11-10"
  
  overview:
    name: "CORTEX Cognitive Framework"
    tagline: "Gives GitHub Copilot Long-Term Memory"
    status: "69% Complete (21/34 weeks)"
    
  brain:
    tier0_instinct:
      status: "complete"
      description: "Immutable governance rules (YAML)"
      file: "cortex-brain/brain-protection-rules.yaml"
      tests: 55
      lines: 250
      
    tier1_memory:
      status: "complete"
      description: "Last 20 conversations (SQLite)"
      class: "WorkingMemory"
      module: "src.tier1.working_memory"
      tests: 149
      
    tier2_knowledge:
      status: "complete"
      description: "Learned patterns (YAML)"
      class: "KnowledgeGraph"
      module: "src.tier2.knowledge_graph.knowledge_graph"
      tests: 165
      
    tier3_context:
      status: "complete"
      description: "Development context (Git, tests)"
      class: "ContextIntelligence"
      module: "src.tier3.context_intelligence"
      tests: 49
      
  agents:
    left_brain:
      - name: "Executor"
        status: "complete"
        role: "Implements features"
        
      - name: "Tester"
        status: "complete"
        role: "Creates comprehensive tests"
        
      # ... all 10 agents
      
  operations:
    implemented: 2
    pending: 11
    total_modules: 70
    modules_implemented: 10
    
    list:
      environment_setup:
        status: "partial"
        modules: "4/11"
        
      refresh_cortex_story:
        status: "complete"
        modules: "6/6"
        
      # ... all operations
      
  plugins:
    total: 12
    tested: 12
    coverage: "100%"
    
  data_flows:
    user_request:
      step1: "IntentDetector analyzes request"
      step2: "Router selects operation"
      step3: "Orchestrator executes modules"
      step4: "Agents complete tasks"
      step5: "Response returned to user"
      
  extension_points:
    add_operation: "Define in cortex-operations.yaml"
    add_module: "Implement BaseOperationModule"
    add_plugin: "Implement BasePlugin"
    add_agent: "Implement BaseAgent"
```

**Time:** 4-6 hours (comprehensive)

---

## 📈 Sessions 3-4: Module Implementation (8-10 hours)

### Task 5: Complete Environment Setup Operation

**Goal:** Implement 7 remaining modules

See: `docs/contributing/MODULE-IMPLEMENTATION-GUIDE.md` (to be created)

**Modules to implement:**
1. `project_validation_module.py` (1.5h)
2. `git_sync_module.py` (2h)
3. `virtual_environment_module.py` (2.5h)
4. `conversation_tracking_module.py` (3h)
5. `brain_tests_module.py` (2h)
6. `tooling_verification_module.py` (1.5h)
7. `setup_completion_module.py` (1h)

**Total:** 13.5 hours (can be split across multiple sessions)

---

## 📅 Implementation Timeline

### This Week (Phase 5)
- ✅ Day 1: Session 1 complete (6-7h)
- 📋 Day 2: Session 2 start (2-3h)
- 📋 Day 3: Session 2 complete (2-3h)

### Next Week (Phase 5.5)
- 📋 Day 4-5: Session 3 (complete 4 setup modules, 5-6h)
- 📋 Day 6-7: Session 4 (complete 3 setup modules, 3-4h)

**Total Phase 5 remaining:** ~22-25 hours

---

## ✅ Success Metrics

| Metric | Before | After Session 1 | After All Sessions |
|--------|--------|----------------|-------------------|
| **YAML Docs** | 1/15 (7%) | 5/15 (33%) | 10/15 (67%) |
| **Ops Status Tracking** | No | Yes (70 modules) | Yes + unified doc |
| **Tier Docs Fixed** | No | Yes (3 docs) | Yes (all refs) |
| **Setup Modules** | 4/11 (36%) | 4/11 (36%) | 11/11 (100%) |
| **Architecture Clarity** | 6/10 | 7/10 | 9/10 |

---

## 🚀 Getting Started

**To begin Session 1 right now:**

```bash
# 1. Create the status update script
mkdir -p scripts
touch scripts/update_operations_status.py

# 2. Create YAML files directory (if needed)
mkdir -p cortex-brain

# 3. Open this plan in editor
code cortex-brain/cortex-2.0-design/CORTEX-2.0-DESIGN-UPDATE-PLAN.md

# 4. Start with Task 1 (update_operations_status.py)
```

**First action:** Implement the status update script in Task 1.

---

**Document Status:** ✅ READY TO EXECUTE  
**Next Action:** Begin Session 1, Task 1 (1 hour)  
**Total Plan:** 4 sessions, 58-70 hours

---

*Generated: 2025-11-10*  
*Part of: CORTEX 2.0 Architecture Refinement*  
*Related: CORTEX-2.0-ARCHITECTURE-GAP-ANALYSIS.md*
