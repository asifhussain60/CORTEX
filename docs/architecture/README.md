# CORTEX Architecture

**Last Updated:** 2025-11-10

## Overview

CORTEX is an AI enhancement framework that gives GitHub Copilot long-term memory, context awareness, and strategic planning capabilities through a 4-tier brain architecture.

---

## 4-Tier Brain System

### Tier 0: Instinct (Governance)
**Purpose:** Immutable rules that protect CORTEX integrity

**Storage:** `cortex-brain/brain-protection-rules.yaml`

**Key Rules:**
- NEVER create new files if target doesn't exist
- Maintain plugin boundaries
- Enforce documentation sync
- Protect tier separation

**Tests:** `tests/tier0/test_brain_protector.py` (22/22 passing ✅)

---

### Tier 1: Working Memory (Conversations)
**Purpose:** Last 20 conversations preserved across sessions

**Storage:** SQLite database (`cortex-brain/conversation-history.db`)

**Key Features:**
- Conversation tracking
- Message threading
- Context preservation
- "Continue" command support

**API:** `src/tier1/conversation_manager.py`

---

### Tier 2: Knowledge Graph (Learning)
**Purpose:** Accumulated patterns from all interactions

**Storage:** `cortex-brain/knowledge-graph.yaml`

**Categories:**
- Technical patterns
- User preferences
- Code patterns
- Best practices
- Lessons learned

**API:** `src/tier2/knowledge_graph.py`

---

### Tier 3: Development Context (Project Health)
**Purpose:** Real-time project metrics and health monitoring

**Sources:**
- Git history analysis
- Test coverage metrics
- Code quality scores
- Dependency tracking

**API:** `src/tier3/development_context.py`

---

## 10 Specialist Agents

### LEFT BRAIN (Tactical - 5 Agents)

**🏃 Executor Agent**
- Implements features
- Writes code
- Executes tasks

**🧪 Tester Agent**
- Creates comprehensive tests
- Validates coverage
- Ensures quality

**✅ Validator Agent**
- Quality assurance
- Code review
- Standard compliance

**📋 Work Planner Agent**
- Task breakdown
- Dependency analysis
- Execution planning

**📝 Documenter Agent**
- Auto-generates documentation
- Maintains consistency
- Updates references

---

### RIGHT BRAIN (Strategic - 5 Agents)

**🎯 Intent Detector Agent**
- Routes requests
- Detects patterns
- Classifies intents

**🏛️ Architect Agent**
- System design
- Architecture decisions
- Scalability planning

**🏥 Health Validator Agent**
- Project diagnosis
- Issue detection
- Improvement recommendations

**🔍 Pattern Matcher Agent**
- Finds similar problems
- Recommends solutions
- Applies lessons learned

**🧠 Learner Agent**
- Accumulates wisdom
- Updates knowledge graph
- Improves over time

---

## Corpus Callosum (Coordination)

**Purpose:** Coordinates left and right brain hemispheres

**Functions:**
- Intent routing
- Agent orchestration
- Context sharing
- Result synthesis

**Implementation:** `src/cortex_agents/corpus_callosum.py`

---

## Plugin System

**Architecture:** Extensible, event-driven plugin framework

**Base Class:** `src/plugins/base_plugin.py`

**Key Components:**
- Plugin registry
- Command registry
- Hook system
- Lifecycle management

**Current Plugins:**
- Documentation Refresh (v2.1)
- Platform Switch
- Code Review
- System Refactor

**Learn More:** [Plugin System](../plugins/README.md)

---

## Universal Operations

**Architecture:** Modular, YAML-driven operation system

**Configuration:** `cortex-operations.yaml`

**Components:**
1. **Registry** - Operation definitions
2. **Orchestrator** - Execution coordination
3. **Modules** - Reusable building blocks
4. **Factory** - Module instantiation

**Status:**
- ✅ Core architecture complete
- ✅ Setup operation (4/4 modules)
- 🟡 Story refresh (1/6 modules)
- ⏸️ Other operations pending

---

## Token Optimization

**Challenge:** Original monolithic prompts consumed excessive tokens

**Solution:** Modular architecture + YAML configuration

**Results:**
- Entry point: 74,047 → 2,078 tokens (97.2% reduction)
- Brain rules: YAML format (75% reduction vs Python)
- Module loading: On-demand vs always-loaded
- Annual savings: $25,920 (at typical usage)

**Details:** See `cortex-brain/CORTEX-TOKEN-OPTIMIZER-COMPARISON.md`

---

## Development Context

### Project Health Metrics

CORTEX tracks:
- Git commit frequency
- Test coverage percentage
- Code quality scores
- Documentation completeness
- Dependency freshness

### Context Sources

**Git Analysis:**
```python
from src.tier3.development_context import DevelopmentContext

context = DevelopmentContext()
health = context.get_project_health()
```

**Test Coverage:**
```bash
pytest --cov=src tests/
```

**Code Quality:**
```bash
pylint src/
mypy src/
```

---

## Data Flow

```
User Request
    ↓
Intent Detection (RIGHT BRAIN)
    ↓
Agent Selection (Corpus Callosum)
    ↓
Execution (LEFT BRAIN)
    ↓
Learning (Tier 2 Update)
    ↓
Result + Context Preservation (Tier 1)
```

---

## Memory Hierarchy

**Access Speed vs Capacity:**

```
Tier 0: Instant access, ~100 rules (YAML)
Tier 1: Fast access, 20 conversations (SQLite)
Tier 2: Medium access, unlimited patterns (YAML)
Tier 3: Real-time, project metrics (Git/Files)
```

---

## Configuration

**Main Config:** `cortex.config.json`

**Machine-Specific Paths:**
```json
{
  "machines": {
    "DESKTOP-HOME": {
      "cortex_root": "D:\\PROJECTS\\CORTEX"
    },
    "macbook-pro": {
      "cortex_root": "/Users/asif/dev/CORTEX"
    }
  }
}
```

**Template:** `cortex.config.template.json`

---

## Testing Architecture

**Layers:**
- Tier 0: Brain protection rules (22 tests)
- Tier 1: Conversation management (45 tests)
- Tier 2: Knowledge graph (38 tests)
- Tier 3: Development context (29 tests)
- Plugins: Individual plugin tests (150+ tests)
- Integration: Cross-tier workflows (25 tests)

**Total:** 309+ tests

**Framework:** pytest 9.0.0

---

## Performance Benchmarks

**Token Usage:**
- Entry point: 2,078 tokens avg (97% reduction)
- Full context: 15,000 tokens avg (with history)
- Per-request: ~$0.06 (GPT-4 pricing)

**Response Times:**
- Intent detection: <100ms
- Agent routing: <50ms
- Simple execution: 1-3s
- Complex planning: 5-15s

**Memory Usage:**
- SQLite DB: ~5MB (20 conversations)
- Knowledge graph: ~500KB (YAML)
- Brain rules: ~50KB (YAML)

---

## Security

**Principles:**
- No credentials in code
- Tier 0 protection rules
- File operation validation
- Path traversal prevention
- Input sanitization

**Audit:** `tests/tier0/test_brain_protector.py`

---

## Scalability

**Current Limits:**
- Tier 1: 20 conversations (configurable)
- Tier 2: No practical limit (YAML)
- Tier 3: Git history depth (configurable)
- Plugins: No limit

**Future Enhancements:**
- Distributed Tier 1 (multi-machine)
- Tier 2 compression
- Tier 3 caching
- Plugin marketplace

---

## Resources

- [Technical Reference](../reference/api-reference.md)
- [Plugin Development](../plugins/README.md)
- [Agent System](../guides/agents-guide.md)
- [Configuration Guide](../reference/configuration.md)

---

*Last Updated: 2025-11-09*  
*CORTEX Architecture v2.1*
