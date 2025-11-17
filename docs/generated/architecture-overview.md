# Architecture Overview

**Generated**:   
**Version**: 

CORTEX 3.0 is a cognitive AI architecture designed for intelligent code assistance with long-term memory and self-improving capabilities.

## Core Principles

1. **Cognitive Architecture**: Inspired by human brain structure
2. **Tier-based Intelligence**: 4 layers from instinct to deep context
3. **Dual-Hemisphere Processing**: Strategic (right) and tactical (left) agents
4. **Self-Protection**: Multi-layer brain protection system
5. **Continuous Learning**: Knowledge graph that evolves over time

## System Architecture

![4-Tier Architecture](../images/diagrams/strategic/tier-architecture.md)

### Tier System

CORTEX operates on a 4-tier cognitive architecture, each tier providing different levels of intelligence:

#### Tier 0: Instinct (Protection)

**Purpose**: Immutable governance rules that protect CORTEX architectural integrity

**Responsibilities**:
- Enforce Test-Driven Development (RED → GREEN → REFACTOR)
- Maintain Definition of Ready and Definition of Done
- Protect brain state from unauthorized modifications
- Challenge risky changes via Brain Protector agent

**Storage**:
- **Governance Rules**: `governance/rules.md` - Permanent, immutable core principles
- **Protection Rules**: `cortex-brain/brain-protection-rules.yaml` - 6-layer protection system

---

#### Tier 1: Working Memory

**Purpose**: Short-term conversation memory (last 20 conversations, FIFO queue)

**Responsibilities**:
- Store recent conversation history with full message context
- Track entities (files, classes, methods) mentioned in conversations
- Enable context continuity ("make it purple" knows what "it" refers to)
- Provide FIFO queue management with automatic archival

**Storage**:
- **SQLite Database**: `cortex-brain/tier1/conversations.db` - Indexed conversation storage
- **JSON Lines**: `cortex-brain/tier1/conversation-context.jsonl` - Raw message logs
- **Performance**: <50ms query time (target), 18ms average actual ⚡

---

#### Tier 2: Knowledge Graph

**Purpose**: Long-term pattern learning and workflow templates

**Responsibilities**:
- Learn intent patterns from user interactions
- Track file relationships (co-modification, dependencies)
- Store successful workflow templates for reuse
- Apply pattern decay (confidence decreases over time for unused patterns)

**Storage**:
- **SQLite Database**: `cortex-brain/tier2/knowledge-graph.db` - Pattern storage with FTS5 search
- **YAML Exports**: `cortex-brain/tier2/knowledge-graph.yaml` - Human-readable backups
- **Performance**: <150ms pattern search (target), 92ms average actual ⚡

---

#### Tier 3: Context Intelligence

**Purpose**: Development context analytics and git analysis

**Responsibilities**:
- Analyze git commit history and file hotspots
- Track code health metrics (test coverage, build success rate)
- Monitor session productivity patterns
- Provide proactive warnings for unstable files

**Storage**:
- **SQLite Database**: `cortex-brain/tier3/context-intelligence.db` - Analytics storage
- **JSON Lines**: `cortex-brain/tier3/git-analysis.jsonl` - Git commit logs
- **Performance**: <200ms analysis (target), 156ms average actual ⚡

---

## Agent Architecture

![Agent Coordination](../images/diagrams/strategic/agent-coordination.md)


### Right Brain (Strategic)

Strategic agents handle high-level planning and governance:



### Left Brain (Tactical)

Tactical agents handle execution and validation:



### Corpus Callosum (Coordination)

The coordination layer manages communication between hemispheres:

- **Message Queue**: Asynchronous task routing
- **Context Sharing**: Shared memory access
- **Synchronization**: State coordination


## Information Flow

![Information Flow](../images/diagrams/strategic/information-flow.md)

### Request Processing Flow

1. **User Intent** → Intent Router (Right Brain)
2. **Planning** → Work Planner (Right Brain)
3. **Execution** → Code Executor (Left Brain)
4. **Validation** → Health Validator (Left Brain)
5. **Response** → User

Each stage enriches context from the appropriate tier:

- Tier 0: Governance rules
- Tier 1: Recent conversations
- Tier 2: Pattern knowledge
- Tier 3: Deep code context

## Brain Protection

![Brain Protection](../images/diagrams/architectural/brain-protection.md)

CORTEX implements multi-layer protection for the cortex-brain:

1. **Rule Validation**: Check against brain-protection-rules.yaml
2. **Change Approval**: Require explicit approval for brain changes
3. **Backup Creation**: Automatic backup before modifications
4. **Safe Execution**: Sandboxed execution environment
5. **Verification**: Post-change validation

## Key Components

### Entry Point Modules (EPM)

EPMs are the primary interface for major operations:

- **Documentation Generator**: Regenerate all documentation
- **Health Check**: System diagnostics
- **Cleanup Manager**: Maintenance operations
- **Migration Handler**: Schema and data migrations

### Knowledge Graph

The knowledge graph captures learned patterns:

- File relationships
- Common workflows
- Error patterns
- Best practices

### Context Intelligence

Tier 3 provides deep contextual understanding:

- Git history analysis
- Code metrics tracking
- Health trend analysis
- Performance profiling

## Technology Stack

**Backend**:
- Python 3.8+
- Jinja2 (templating)
- PyYAML (configuration)
- AST (code analysis)

**Frontend**:
- VS Code Extension API
- TypeScript
- Node.js

**Documentation**:
- MkDocs
- Mermaid (diagrams)
- Markdown

**Storage**:
- YAML (configuration and knowledge)
- JSON (structured data)
- JSONL (conversation logs)
- SQLite (future: metrics database)

## Design Decisions

### Why YAML for Brain Storage?

- **Human-readable**: Easy to inspect and debug
- **Git-friendly**: Clean diffs for version control
- **Flexible**: Hierarchical structure without rigid schema
- **Editable**: Can be manually edited when needed

### Why Dual-Hemisphere Design?

- **Separation of concerns**: Strategy vs. execution
- **Parallel processing**: Independent agent operation
- **Fault isolation**: Failures don't cascade
- **Cognitive realism**: Mirrors human brain structure

### Why 4 Tiers?

- **Performance**: Fast access to frequently used data (T0, T1)
- **Intelligence**: Deep context when needed (T2, T3)
- **Scalability**: Each tier can scale independently
- **Clarity**: Clear boundaries for data lifecycle

## Related Documentation

- [Tier System Details](tier-system.md)
- [Agent Architecture](agents.md)
- [Brain Protection](brain-protection.md)
- [Operations Overview](../operations/overview.md)

---

*This page was automatically generated by the CORTEX Documentation Generator.*