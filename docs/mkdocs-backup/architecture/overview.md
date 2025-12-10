# CORTEX Architecture Overview

**Version:** 3.0  
**Status:** Production Ready  
**Last Updated:** November 2025

## System Architecture

CORTEX implements a sophisticated multi-tier architecture with specialized agents and comprehensive brain protection.

## Core Components

This component provides specific functionality within the CORTEX architecture:

- **Purpose**: Specialized processing and data handling
- **Integration**: Works seamlessly with other components
- **APIs**: Well-defined interfaces for interaction
- **Testing**: Comprehensive test coverage

See [Technical Reference](../reference/api.md) for API documentation.

### Memory System (4 Tiers)

<div class="architecture-section">

#### Tier 0: Instinct (Immutable Governance)
- **Purpose:** Hardwired rules that cannot be bypassed
- **Components:** Brain protection, SKULL rules, TDD enforcement
- **Status:** ✅ Complete

#### Tier 1: Working Memory
- **Purpose:** Recent conversation context (last 20 conversations)
- **Components:** SQLite database, context scoring, auto-injection
- **Status:** ✅ Complete

#### Tier 2: Knowledge Graph
- **Purpose:** Pattern learning and semantic relationships
- **Components:** Entity extraction, pattern matching, confidence scoring
- **Status:** ✅ Complete

#### Tier 3: Context Intelligence
- **Purpose:** Long-term storage and historical analysis
- **Components:** Git analysis, code health metrics, project history
- **Status:** ✅ Complete

</div>

### Agent System (Dual Hemisphere)

<div class="architecture-section">

#### Left Hemisphere (Logical)
- **Code Executor:** Tactical implementation
- **Test Generator:** Automated test creation
- **Validator:** Quality assurance

#### Right Hemisphere (Creative)
- **Work Planner:** Strategic planning
- **Architect:** System design
- **Documenter:** Documentation generation

#### Coordination Layer
- **Corpus Callosum:** Inter-agent communication
- **Intent Router:** Natural language understanding
- **Pattern Matcher:** Context detection

</div>

### Protection System

<div class="architecture-section">

**10 Protection Layers with 27 Automated Rules**

1. **Layer 1:** Instinct Immutability
2. **Layer 2:** Architectural Integrity
3. **Layer 3:** Code Quality Standards
4. **Layer 4:** Test Coverage Requirements
5. **Layer 5:** Documentation Completeness
6. **Layer 6:** Security Validation
7. **Layer 7:** Performance Budgets
8. **Layer 8:** Dependency Management
9. **Layer 9:** Git Commit Standards
10. **Layer 10:** Continuous Monitoring

</div>

## Architecture Diagrams

For detailed visual representations, see:

- [Architecture Diagrams Page](../architecture-diagrams.md)
- [Integration Diagrams](../integration-diagrams.md)
- [Operational Diagrams](../operational-diagrams.md)
- [Planning & Strategic Diagrams](../planning-diagrams.md)

## Design Principles

This section covers architectural aspects of design principles. See the architecture overview for context.

### Separation of Concerns
- Each tier has distinct responsibilities
- Agents specialize in specific domains
- Clear boundaries between components

### Pragmatic MVP Approach
- Working software over perfect architecture
- Incremental progress over all-or-nothing
- Reality-based thresholds over aspirational goals

### Protection First
- Brain protection enforced at Tier 0
- Automated validation before commits
- Continuous health monitoring

## Performance Metrics

- **Token Reduction:** 97.2% (74,047 → 2,078 tokens)
- **Cost Reduction:** 93.4% with GitHub Copilot pricing
- **Response Time:** < 500ms for context injection
- **Memory Efficiency:** 4-tier caching system

## Technology Stack

- **Language:** Python 3.9+
- **Databases:** SQLite (Tier 1), NetworkX (Tier 2)
- **Framework:** Plugin-based architecture
- **Testing:** pytest with 834/897 tests passing
- **Documentation:** MkDocs with custom Tales theme

---

**See Also:**
- [Tier System Details](tier-system.md)
- [Agent Architecture](agents.md)
- [Brain Protection](brain-protection.md)
