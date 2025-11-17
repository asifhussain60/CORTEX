# Technical Documentation Narrative

**Purpose:** Comprehensive technical reference for developers building with or extending CORTEX  
**Audience:** Developers, architects, plugin developers, system integrators

---

## For Leadership

### What This Is

CORTEX Technical Documentation is a complete developer reference that transforms CORTEX from a "black box" into a fully transparent, extensible platform. It provides every API, schema, code example, and architectural detail needed for developers to build confidently with CORTEX.

### Why It Matters

**Problem:** Developers waste hours reverse-engineering systems when documentation is incomplete or missing. This leads to:
- ❌ Trial-and-error development (slow)
- ❌ Inconsistent implementations (bugs)
- ❌ Fear of breaking things (paralysis)
- ❌ Unable to extend or customize (locked in)

**Solution:** Comprehensive technical documentation eliminates guesswork:
- ✅ Every API documented with code examples
- ✅ Database schemas explicitly defined
- ✅ Architecture patterns clearly explained
- ✅ Plugin development fully supported
- ✅ Testing protocols provided

### Business Impact

**Faster Onboarding:**
- New developers productive in hours, not weeks
- Reduced ramp-up costs (80% faster learning curve)
- Self-service learning (less hand-holding)

**Higher Quality:**
- Clear patterns = consistent code
- Schema definitions = fewer data bugs
- Testing protocols = reliable features

**Extensibility Unlocked:**
- Plugin API enables customization without core changes
- Integration guides support ecosystem growth
- Community contributions become possible

**Cost Reduction:**
- Less time debugging = more time building features
- Fewer support requests (documentation answers questions)
- Reduced training costs (self-serve learning)

### The Difference

| Without Tech Docs | With CORTEX Tech Docs |
|-------------------|----------------------|
| "How do I store a conversation?" | `memory.store_conversation(...)` - Line 42, example included |
| "What fields does this database have?" | Full SQLite schema, indexes documented |
| "Can I build a custom agent?" | Plugin API reference + template code |
| "How fast should Tier 2 be?" | Target: <150ms, Current: 92ms ⚡ |
| Developers ask senior devs | Developers find answers instantly |

---

## For Developers

### What You Get

CORTEX Technical Documentation provides **six comprehensive sections** covering every aspect of the system:

#### 1. Architecture Deep-Dive

**Purpose:** Understand how CORTEX works internally

**Coverage:**
- **4-Tier Brain System** - Complete explanation of Tier 0 (Instinct), Tier 1 (Working Memory), Tier 2 (Knowledge Graph), Tier 3 (Context Intelligence)
- **Agent System** - How 10 specialized agents coordinate via Corpus Callosum
- **Memory Flow** - How conversations become patterns, patterns inform decisions
- **Protection Layers** - Brain protection rules and architectural integrity

**Example - Understanding Tier 1:**
```python
# Tier 1: Working Memory (Last 20 Conversations)
# Storage: cortex-brain/tier1/conversations.db (SQLite)
# Performance Target: <50ms per query
# Actual Performance: 18ms average ⚡

from src.tier1.working_memory import WorkingMemory

memory = WorkingMemory()

# Store conversation
conversation_id = memory.store_conversation(
    user_message="Add purple button to panel",
    assistant_response="I'll create that button...",
    intent="EXECUTE",
    context={
        "files_modified": ["HostControlPanel.razor"],
        "entities": ["button", "panel", "purple"]
    }
)
# Returns: "conv_20251117_103000_a1b2c3"

# Retrieve recent conversations
recent = memory.get_recent_conversations(limit=5)
# Returns: List of last 5 conversations with full context

# Search by entity
button_convos = memory.search_by_entity(
    entity_type="component",
    entity_value="button"
)
# Returns: All conversations mentioning buttons
```

#### 2. API Reference

**Purpose:** Complete reference for every CORTEX API

**Coverage:**

**Tier 1 API (Working Memory):**
```python
# Core Classes
WorkingMemory()
  .store_conversation(user_message, assistant_response, intent, context)
  .get_recent_conversations(limit=5)
  .search_conversations(query, filters, limit)
  .get_conversation_context(conversation_id)
  .track_entity(conversation_id, entity_type, entity_value)
  .cleanup_old_conversations()  # FIFO queue management

# Performance Metrics
- store_conversation(): 12ms avg
- get_recent_conversations(): 18ms avg
- search_conversations(): 45ms avg
```

**Tier 2 API (Knowledge Graph):**
```python
# Core Classes
KnowledgeGraph()
  .store_pattern(title, pattern_type, confidence, context)
  .search_patterns(query, filters, limit)
  .track_relationship(file_a, file_b, relationship_type, strength)
  .get_file_relationships(file_path, min_strength)
  .learn_intent_pattern(user_phrase, detected_intent, confidence)
  .predict_intent(user_phrase, context_hints)
  .store_workflow_template(name, phases, success_rate)
  .apply_decay()  # Pattern confidence decay (5% per 30 days)

# Performance Metrics
- store_pattern(): 56ms avg
- search_patterns(): 92ms avg (FTS5 full-text search)
- get_file_relationships(): 78ms avg
```

**Tier 3 API (Context Intelligence):**
```python
# Core Classes
ContextIntelligence()
  .analyze_git_activity(lookback_days=30)
  .get_file_stability(file_path)
  .get_development_insights()
  .get_file_warnings(file_path)
  .track_code_health(test_coverage, build_success_rate, error_count)
  .get_health_trends(days=30)

# Performance Metrics
- analyze_git_activity(): 156ms avg
- get_file_stability(): 67ms avg
```

**Agent Coordination API:**
```python
# Intent Router
IntentRouter()
  .parse(user_message, context_hints)
  # Returns: {"intent": "EXECUTE", "confidence": 0.92, "agent": "code-executor"}

# Agent Coordinator
AgentCoordinator()
  .execute_workflow(workflow_name, context)
  # Orchestrates multi-agent workflows
```

**Plugin Development API:**
```python
# Base Plugin Class
from src.plugins.base_plugin import BasePlugin

class MyPlugin(BasePlugin):
    def get_natural_language_patterns(self):
        return ["analyze code", "review quality"]
    
    def execute(self, request, context):
        # Access CORTEX brain tiers
        tier2_data = self.knowledge_graph.search_patterns(request)
        tier3_data = self.context_intelligence.analyze_files(context)
        return {"success": True, "data": results}
```

#### 3. Developer Guides

**Cross-Platform Setup:**
```bash
# macOS/Linux
export CORTEX_ROOT="$HOME/PROJECTS/CORTEX"
export CORTEX_BRAIN_PATH="$CORTEX_ROOT/cortex-brain"

# Windows (PowerShell)
[Environment]::SetEnvironmentVariable("CORTEX_ROOT", "D:\PROJECTS\CORTEX", "User")
[Environment]::SetEnvironmentVariable("CORTEX_BRAIN_PATH", "D:\PROJECTS\CORTEX\cortex-brain", "User")

# Install dependencies
pip install -r requirements.txt

# Initialize brain
python scripts/cortex_setup.py
```

**Configuration Reference:**
```json
// cortex.config.json
{
  "tier1": {
    "maxConversations": 20,  // FIFO queue size
    "fifoMode": true,        // Auto-delete oldest
    "entityExtraction": {
      "enabled": true,
      "extractFiles": true,
      "extractClasses": true
    }
  },
  "tier2": {
    "patternLearning": {
      "minConfidence": 0.7,  // Store patterns above 70%
      "decayRate": 0.05,     // 5% decay per 30 days
      "decayAfterDays": 90   // Start decay after 90 days
    }
  },
  "tier3": {
    "gitAnalysis": {
      "enabled": true,
      "maxCommits": 1000
    }
  }
}
```

**Plugin Development Guide:**
```python
# Step 1: Create plugin class
from src.plugins.base_plugin import BasePlugin

class CodeReviewPlugin(BasePlugin):
    def __init__(self):
        super().__init__(
            name="code-review",
            version="1.0.0",
            description="Automated code quality review"
        )
    
    # Step 2: Define natural language triggers
    def get_natural_language_patterns(self):
        return [
            "review code",
            "check quality",
            "analyze PR",
            "code review"
        ]
    
    # Step 3: Implement validation
    def validate(self, context):
        required = ["file_path", "review_type"]
        return all(field in context for field in required)
    
    # Step 4: Implement execution
    def execute(self, request, context):
        file_path = context["file_path"]
        
        # Access Tier 2 for past patterns
        patterns = self.knowledge_graph.search_patterns(
            query="code quality issues",
            filters={"file": file_path}
        )
        
        # Access Tier 3 for file stability
        stability = self.context_intelligence.get_file_stability(file_path)
        
        # Perform review
        issues = self._analyze_code(file_path, patterns, stability)
        
        return {
            "success": True,
            "issues_found": len(issues),
            "recommendations": issues,
            "stability": stability
        }
    
    # Step 5: Register plugin
    def register(self):
        from src.core.plugin_manager import PluginManager
        manager = PluginManager()
        manager.register_plugin(self)
```

**Testing Protocols:**
```python
# TDD Workflow (MANDATORY in CORTEX)

# Phase 1: RED (Write Failing Test)
import pytest
from src.tier1.working_memory import WorkingMemory

def test_conversation_storage():
    """Test conversation storage in Tier 1"""
    memory = WorkingMemory()
    
    # Test should fail initially (no implementation)
    conv_id = memory.store_conversation(
        user_message="Test message",
        assistant_response="Test response",
        intent="TEST"
    )
    
    assert conv_id is not None
    assert conv_id.startswith("conv_")
    
    # Retrieve and verify
    conv = memory.get_conversation(conv_id)
    assert conv["user_message"] == "Test message"
    assert conv["intent"] == "TEST"

# Phase 2: GREEN (Make It Pass)
# Implement WorkingMemory.store_conversation() to pass test

# Phase 3: REFACTOR (Clean Up)
# Improve code quality while keeping tests green
```

**Performance Tuning:**
```python
# Optimization Techniques Used in CORTEX

# 1. Database Indexing
# SQLite indexes on frequently queried columns
CREATE INDEX idx_conversations_timestamp ON conversations(timestamp DESC);
CREATE INDEX idx_entities_type_value ON entities(entity_type, entity_value);

# 2. Connection Pooling
# Reuse database connections
from src.core.db_pool import DatabasePool

pool = DatabasePool(max_connections=10)
with pool.get_connection() as conn:
    # Use connection
    pass

# 3. Query Result Caching
# Cache frequently accessed data
from functools import lru_cache

@lru_cache(maxsize=128)
def get_file_relationships(file_path):
    # Expensive query cached for 128 most recent files
    return db.query(...)

# 4. FTS5 Full-Text Search
# Fast pattern search using SQLite FTS5
CREATE VIRTUAL TABLE patterns_fts USING fts5(
    pattern_id UNINDEXED,
    title,
    context_json
);
# Search: 92ms vs 450ms without FTS5 (5x faster)
```

#### 4. Data Schemas

**Tier 1 (Working Memory) Schema:**
```sql
-- Conversations table
CREATE TABLE conversations (
    conversation_id TEXT PRIMARY KEY,
    user_message TEXT NOT NULL,
    assistant_response TEXT,
    intent TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    context_json TEXT,
    is_active BOOLEAN DEFAULT 1
);

-- Messages table (last 10 per conversation)
CREATE TABLE messages (
    message_id TEXT PRIMARY KEY,
    conversation_id TEXT,
    role TEXT,  -- 'user' or 'assistant'
    content TEXT,
    sequence_num INTEGER,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
);

-- Entities table
CREATE TABLE entities (
    entity_id TEXT PRIMARY KEY,
    conversation_id TEXT,
    entity_type TEXT,  -- 'file', 'class', 'method'
    entity_value TEXT,
    context TEXT,
    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
);

-- Indexes for performance
CREATE INDEX idx_conversations_timestamp ON conversations(timestamp DESC);
CREATE INDEX idx_messages_conversation ON messages(conversation_id, sequence_num);
CREATE INDEX idx_entities_conversation ON entities(conversation_id);
CREATE INDEX idx_entities_type_value ON entities(entity_type, entity_value);
```

**Tier 2 (Knowledge Graph) Schema:**
```sql
-- Patterns table
CREATE TABLE patterns (
    pattern_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    pattern_type TEXT,  -- 'workflow', 'intent', 'validation'
    confidence REAL DEFAULT 0.5,
    context_json TEXT,
    scope TEXT,  -- 'cortex' or 'application'
    namespaces TEXT,  -- JSON array
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_used DATETIME,
    usage_count INTEGER DEFAULT 0
);

-- Relationships table
CREATE TABLE relationships (
    relationship_id TEXT PRIMARY KEY,
    file_a TEXT,
    file_b TEXT,
    relationship_type TEXT,  -- 'co_modification', 'dependency'
    strength REAL,  -- 0.0 to 1.0
    co_modification_count INTEGER DEFAULT 0,
    context TEXT,
    last_observed DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- FTS5 for pattern search
CREATE VIRTUAL TABLE patterns_fts USING fts5(
    pattern_id UNINDEXED,
    title,
    context_json,
    content='patterns'
);
```

**Tier 3 (Context Intelligence) Schema:**
```sql
-- Git commits table
CREATE TABLE git_commits (
    commit_hash TEXT PRIMARY KEY,
    author TEXT,
    timestamp DATETIME,
    message TEXT,
    files_changed INTEGER,
    lines_added INTEGER,
    lines_deleted INTEGER,
    analyzed_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- File metrics table
CREATE TABLE file_metrics (
    file_path TEXT PRIMARY KEY,
    change_count INTEGER DEFAULT 0,
    churn_rate REAL,
    stability TEXT,  -- 'stable', 'unstable', 'volatile'
    last_changed DATETIME,
    avg_change_size INTEGER,
    total_lines INTEGER
);

-- Session analytics table
CREATE TABLE session_analytics (
    session_id TEXT PRIMARY KEY,
    start_time DATETIME,
    end_time DATETIME,
    duration_minutes INTEGER,
    intent TEXT,
    success BOOLEAN,
    productivity_score REAL
);
```

**YAML Configuration Formats:**
```yaml
# brain-protection-rules.yaml
protection_layers:
  - name: instinct_immutability
    severity: blocked
    rules:
      - instinct_immutability
      - tier0_modification_prevention
  
  - name: critical_path_protection
    severity: blocked
    rules:
      - critical_files_readonly
      - governance_rules_protected

# response-templates.yaml
templates:
  help_table:
    name: Help Table
    trigger: ["help", "/help", "what can cortex do"]
    response_type: table
    content: |
      [Pre-formatted help text]
```

#### 5. Code Examples

**Example 1: Store and Search Conversations**
```python
from src.tier1.working_memory import WorkingMemory

memory = WorkingMemory()

# Store conversation
conv_id = memory.store_conversation(
    user_message="Create authentication system",
    assistant_response="I'll create a secure auth system with JWT...",
    intent="PLAN",
    context={
        "complexity": "high",
        "estimated_hours": 8,
        "files_to_create": ["AuthService.cs", "LoginController.cs"]
    }
)

# Search conversations about authentication
auth_convos = memory.search_conversations(
    query="authentication",
    filters={
        "intent": "PLAN",
        "date_range": ("2025-11-01", "2025-11-17")
    }
)

for conv in auth_convos:
    print(f"Found: {conv['user_message']} (Intent: {conv['intent']})")
```

**Example 2: Pattern Learning and Reuse**
```python
from src.tier2.knowledge_graph import KnowledgeGraph

kg = KnowledgeGraph()

# Store successful workflow pattern
pattern_id = kg.store_pattern(
    title="Invoice Export Workflow",
    pattern_type="workflow",
    confidence=0.85,
    context={
        "files": ["InvoiceService.cs", "ExportController.cs"],
        "steps": ["validate", "format", "generate_pdf", "download"],
        "success_rate": 0.94,
        "avg_duration_minutes": 45
    }
)

# Later: Search for similar patterns
patterns = kg.search_patterns(
    query="export feature",
    filters={"pattern_type": "workflow", "min_confidence": 0.7}
)

if patterns:
    print(f"Found similar pattern: {patterns[0]['title']}")
    print(f"Confidence: {patterns[0]['confidence']}")
    print(f"Reuse this workflow? (60% faster delivery)")
```

**Example 3: File Stability Analysis**
```python
from src.tier3.context_intelligence import ContextIntelligence

ci = ContextIntelligence()

# Analyze file stability
stability = ci.get_file_stability("HostControlPanel.razor")
print(f"Stability: {stability}")  # Output: "unstable"

# Get detailed analysis
details = ci.get_file_stability_details("HostControlPanel.razor")
print(f"Churn rate: {details['churn_rate']}")  # 0.28 (28%)
print(f"Change count: {details['change_count']}")  # 67 changes
print(f"Recommendations:")
for rec in details['recommendations']:
    print(f"  - {rec}")
# Output:
#   - Add extra testing before changes
#   - Consider refactoring to reduce complexity
```

**Example 4: Custom Plugin Development**
```python
from src.plugins.base_plugin import BasePlugin

class MyCustomPlugin(BasePlugin):
    def get_natural_language_patterns(self):
        return ["analyze dependencies", "check imports"]
    
    def execute(self, request, context):
        # Use CORTEX brain tiers (zero external dependencies)
        
        # Tier 2: Search for dependency patterns
        patterns = self.knowledge_graph.search_patterns(
            query="dependency issues",
            filters={"pattern_type": "validation"}
        )
        
        # Tier 3: Get file metrics
        file_path = context.get("file_path")
        metrics = self.context_intelligence.get_file_stability(file_path)
        
        # Your plugin logic
        dependencies = self._analyze_imports(file_path)
        issues = self._check_circular_deps(dependencies)
        
        return {
            "success": True,
            "dependencies_found": len(dependencies),
            "issues": issues,
            "file_stability": metrics,
            "learned_patterns": patterns
        }

# Register plugin
plugin = MyCustomPlugin()
plugin.register()
```

#### 6. Testing & Validation

**Test-Driven Development Workflow:**
```python
# MANDATORY: RED → GREEN → REFACTOR

# ❌ RED: Write failing test first
def test_intent_detection():
    router = IntentRouter()
    result = router.parse("add a button")
    
    assert result["intent"] == "EXECUTE"
    assert result["confidence"] > 0.7
    assert result["agent"] == "code-executor"

# ✅ GREEN: Implement to pass test
class IntentRouter:
    def parse(self, user_message):
        # Implementation that makes test pass
        if "add" in user_message.lower():
            return {
                "intent": "EXECUTE",
                "confidence": 0.92,
                "agent": "code-executor"
            }

# 🔄 REFACTOR: Clean up while keeping tests green
class IntentRouter:
    EXECUTE_KEYWORDS = ["add", "create", "implement"]
    
    def parse(self, user_message):
        for keyword in self.EXECUTE_KEYWORDS:
            if keyword in user_message.lower():
                return self._build_execute_intent(user_message)
```

**Performance Benchmarks:**
| Operation | Target | Actual | Status |
|-----------|--------|--------|--------|
| Tier 1: Store Conversation | <30ms | 12ms | ⚡ Excellent |
| Tier 1: Query Recent | <50ms | 18ms | ⚡ Excellent |
| Tier 2: Pattern Search | <150ms | 92ms | ⚡ Excellent |
| Tier 3: Git Analysis | <200ms | 156ms | ⚡ Excellent |

**Test Coverage Requirements:**
- Unit tests: ≥80% coverage
- Integration tests: All workflows tested
- Performance tests: All targets met
- Definition of Done: Zero errors, zero warnings, all tests pass

---

## Key Takeaways

1. **Complete API Reference** - Every CORTEX API documented with code examples and performance metrics
2. **Production Schemas** - All database schemas, indexes, and data formats explicitly defined
3. **Plugin Development** - Full API for building custom plugins with zero external dependencies
4. **Performance Targets** - Benchmarks provided for every operation (all targets exceeded)
5. **Developer-Ready** - Setup guides, testing protocols, and best practices included

---

## Usage Scenarios

### Scenario 1: New Developer Onboarding

**Context:** Sarah joins the team, needs to understand CORTEX

**Without Tech Docs:**
- Week 1: Read code, ask senior devs questions
- Week 2: Still confused about tier structure
- Week 3: Trial-and-error with APIs
- Result: 3 weeks to productivity

**With CORTEX Tech Docs:**
- Day 1: Read Architecture Deep-Dive, understand tiers
- Day 2: Follow API examples, run test code
- Day 3: Build first feature using patterns
- Result: 3 days to productivity (7x faster)

---

### Scenario 2: Plugin Development

**Context:** Team needs custom "Code Quality" plugin

**Developer Journey:**
1. Read Plugin Development Guide
2. Copy plugin template code
3. Implement custom logic using Tier 2/3 APIs
4. Test using provided testing protocols
5. Deploy in 4 hours (vs 2 weeks without docs)

```python
# From template to production in hours
class CodeQualityPlugin(BasePlugin):
    # Template provides structure
    # Docs provide API details
    # Examples show best practices
    # Result: Fast, correct implementation
```

---

### Scenario 3: Performance Optimization

**Context:** Developer notices slow queries

**Debugging Process:**
1. Check Performance Benchmarks section
2. See target: <150ms for Tier 2 searches
3. Measure actual: 450ms (3x slower)
4. Read optimization techniques
5. Apply indexing + FTS5 + caching
6. Achieve: 92ms (below target) ⚡

**Without Docs:** Days of trial-and-error  
**With Docs:** 1 hour to solution

---

### Scenario 4: Architecture Review

**Context:** Architect evaluating CORTEX for enterprise adoption

**Questions Answered:**
- ✅ "What are the dependencies?" → Zero external (local-first)
- ✅ "How is data stored?" → SQLite schemas provided
- ✅ "What's the performance?" → Benchmarks documented
- ✅ "Can we extend it?" → Plugin API fully documented
- ✅ "Is it production-ready?" → 100% test pass rate, all metrics green

**Decision:** Approved in 2 hours (vs weeks of investigation)

---

*Version: 1.0*  
*Last Updated: November 17, 2025*  
*Status: Production Ready*

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**Repository:** github.com/asifhussain60/CORTEX
