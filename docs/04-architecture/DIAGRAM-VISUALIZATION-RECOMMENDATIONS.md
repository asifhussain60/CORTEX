# Diagram & Visualization Recommendations

**Authority:** cortex-doc.prompt.md | **Status:** 📋 RECOMMENDATIONS READY

---

## Executive Summary

This document provides a comprehensive analysis of additional diagrams and visualizations that would significantly enhance technical understanding of CORTEX's architecture and inner workings. The recommendations combine **Mermaid diagrams** (for documentation maintainability) and **D3.js visualizations** (for interactive exploration and deep-dive analysis).

### Current State
- ✅ 8 existing Mermaid diagrams (flowcharts, state machines, sequence diagrams)
- ✅ Basic system overview and orchestration flow diagrams
- ❌ Missing: Interactive data flow visualizations
- ❌ Missing: Governance tier precedence visualization
- ❌ Missing: TDD workflow cycle diagrams
- ❌ Missing: Request lifecycle diagrams
- ❌ Missing: Resilience pattern flowcharts
- ❌ Missing: Knowledge ingestion flowcharts

---

## 📊 Recommended Diagram Categories

### Category 1: Governance & Decision Making (4 Diagrams)

#### 1.1 **Tier 0-3 Governance Pyramid** (D3.js Interactive)
**Purpose:** Help users understand the immutable hierarchy and rule precedence

**Type:** D3.js Hierarchical Sunburst Chart

**What It Shows:**
- TIER 0 (innermost): 29 CORE rules - color-coded by category
  - Orchestration Lifecycle (4 rules)
  - Quality Standards (5 rules)
  - Development Workflow (4 rules)
  - Safety & Boundaries (4 rules)
  - Audit & Compliance (4 rules)
  - Infrastructure (4 rules)
- TIER 1 (ring 2): Architectural constraints - admin-modifiable
- TIER 2 (ring 3): 80+ templates - user-extendable
- TIER 3 (ring 4): Domain knowledge - context-driven

**Interactivity:**
- Hover: Show rule details, enforcement points
- Click: Navigate to specific rule documentation
- Color code: Red (critical), Yellow (important), Blue (standard)

**Benefits:**
- Visual hierarchy makes immutability obvious
- Shows rule categories and relationships
- Aids decision-making for rule placement

---

#### 1.2 **Complexity-Aware Confirmation Gate Decision Tree** (Mermaid)
**Purpose:** Clarify approval matrix logic for operations

**Type:** Mermaid flowchart with decision nodes

**What It Shows:**
```
User Request
    ↓
LENS Protocol (measure confidence)
    ↓
Complexity Scoring
├─ LENS Confidence (25%)
├─ Files Affected (35%)
├─ Dependency Depth (25%)
└─ Operation Scope (15%)
    ↓
Compare Score to Thresholds
├─ ≤ 0.15 (TRIVIAL) → Auto-approve, no interaction
├─ 0.15-0.35 (SIMPLE) → Auto-approve + summary
├─ 0.35-0.60 (MODERATE) → Request confirmation
├─ 0.60-0.85 (COMPLEX) → Confirm + alternatives
└─ ≥ 0.85 (CRITICAL) → Escalate + executive summary
    ↓
Execute or Block
```

**Interactivity:** Interactive Mermaid with decision paths highlighted

**Benefits:**
- Makes approval logic transparent
- Helps users understand why certain approvals are needed
- Facilitates tuning of thresholds

---

#### 1.3 **Governance Enforcement Points Timeline** (D3.js)
**Purpose:** Show where governance rules are checked during execution

**Type:** D3.js Timeline with enforcement points marked

**What It Shows:**
- Request received → Phase -2 Setup (CORE-006)
- LENS Protocol execution → Intent classification
- Governance Validation (Tier 0) → AC_START logged
- Complexity Assessment (Stage 2.5)
- Orchestrator selection → Domain Brain query
- Execution phase → AC_EXECUTE logged
- Response composition → AC_COMPLETE logged
- Each point shows:
  - Which rules apply
  - Audit entry created
  - Possible rejection triggers

**Benefits:**
- Shows when audit trail events are created
- Clarifies AC (Acceptance Criteria) checkpoint timing
- Helps understand failure points

---

#### 1.4 **Rule Categories & Cross-References** (D3.js Network Graph)
**Purpose:** Show relationships between CORE rules

**Type:** D3.js Force-Directed Graph

**What It Shows:**
- Nodes: Each CORE rule (size = importance)
- Edges: "depends-on", "enforced-at", "conflicts-with"
- Color: By category (Orchestration, Quality, Workflow, Safety, Audit, Infrastructure)
- Node details on hover:
  - Rule ID, description
  - Enforcement points
  - Related rules
  - Test coverage count

**Benefits:**
- Shows interdependencies between rules
- Helps identify when changing one rule affects others
- Reveals rule clustering by function

---

### Category 2: Request Lifecycle & Orchestration Flow (3 Diagrams)

#### 2.1 **Master Orchestrator ConversationProtocol** (Mermaid Sequence Diagram)
**Purpose:** Detail turn-by-turn execution and state management

**Type:** Mermaid sequence diagram

**What It Shows:**
- User ↔ Master Orchestrator ↔ Domain Orchestrators
- Each turn:
  - Stage 1: Context Building (HolisticContextBuilder)
  - Stage 2: Intent Routing (LENS Protocol)
  - Stage 2.5: Complexity Gate (ComplexityAssessment)
  - Stage 3: Execution (Domain-specific logic)
  - Stage 4: Response Composition (6 modes, 5 tones, 5 formats)
- ContinuationDecision returns:
  - COMPLETION
  - USER_REJECTION
  - TOKEN_LIMIT
  - GOVERNANCE_HALT
  - MAX_ROUNDS_REACHED
  - ERROR_UNRECOVERABLE
  - INTERACTION_REQUIRED
  - CONFIRMATION_REQUESTED

**Annotations:**
- AC_START, AC_EXECUTE, AC_COMPLETE logging points
- State persistence between turns
- Token budget tracking

**Benefits:**
- Makes explicit turn-by-turn logic clear
- Shows how state is maintained
- Clarifies continuation decision criteria

---

#### 2.2 **Request Lifecycle: From Entry to Exit** (D3.js Flow Diagram)
**Purpose:** Track how a request flows through the entire system

**Type:** D3.js Sankey Diagram or Flow Chart

**What It Shows:**
```
Entry Points (3 parallel):
├─ REST API (FastAPI)
├─ MCP Server (JSON-RPC)
└─ CLI (cortex-*)
    ↓
Authentication & Authorization
    ↓
LENS Protocol (4 phases):
├─ Language (tokenize, intent classification)
├─ Examination (context analysis)
├─ Navigation (domain exploration)
└─ Synthesis (orchestrator selection)
    ↓
Governance Validation (TIER 0)
    ↓
Complexity Assessment
    ↓
Orchestrator Routing:
├─ Planning Domain
├─ Analysis Domain
└─ Integration Domain
    ↓
Domain Brain Query (if needed)
    ↓
Business Logic Execution
    ↓
Response Composition (6 modes)
    ↓
Audit Trail Logging
    ↓
Exit Points (3 parallel):
├─ REST Response
├─ MCP Response
└─ CLI Output
```

**Flow annotations:**
- Show success vs. error paths
- Show rollback paths
- Show partial failure modes

**Benefits:**
- Complete end-to-end visibility
- Shows all decision points
- Helps understand error handling

---

#### 2.3 **Orchestrator Routing Decision Matrix** (D3.js Heat Map)
**Purpose:** Show how intents are routed to different orchestrators

**Type:** D3.js Interactive Heat Map

**Axes:**
- X-axis: Intent types (IMPLEMENT, FIX, REFACTOR, ANALYZE, DOCUMENT, TEST, DEPLOY, GOVERNANCE)
- Y-axis: Orchestrators (Master, TDD, Intent Router, Refactoring, Planning, Analysis, etc.)

**Cell Contents:**
- Color intensity: Routing probability
- Hover: Show confidence score, why this route, fallback routes
- Click: Navigate to orchestrator documentation

**Benefits:**
- Shows which orchestrators handle which intents
- Reveals intent distribution patterns
- Helps debug routing issues

---

### Category 3: Data Flow & Knowledge Integration (4 Diagrams)

#### 3.1 **LENS Protocol (Intent Comprehension)** (Mermaid + D3.js)
**Purpose:** Detailed breakdown of how LENS analyzes intent

**Mermaid Diagram:** 4-phase flowchart showing:
1. **Language Phase**
   - Input: Raw user text
   - Operations: Tokenization, stemming, entity extraction
   - Output: Tokens, entities, keywords

2. **Examination Phase**
   - Input: Tokens + entities
   - Operations: Context analysis, scope detection
   - Output: Scope, affected modules, dependencies

3. **Navigation Phase**
   - Input: Scope + dependencies
   - Operations: Domain Brain query, knowledge lookup
   - Output: Related components, patterns, best practices

4. **Synthesis Phase**
   - Input: All previous outputs
   - Operations: Orchestrator selection, confidence scoring
   - Output: Selected orchestrator, confidence, parameters

**D3.js Companion:** Interactive pipeline showing:
- Example request flowing through each phase
- Transformations at each stage
- Confidence metrics by phase
- Decision points

**Benefits:**
- Makes "intelligent comprehension" concrete
- Shows information enrichment at each stage
- Clarifies confidence scoring

---

#### 3.2 **Domain Brain Architecture & Adapters** (D3.js)
**Purpose:** Show how domain brain ingests and queries knowledge

**Type:** D3.js Layered Architecture

**Layers:**
1. **Data Sources**
   - Codebase (AST parsing)
   - Git history
   - Code comments
   - Test files
   - ADO/Jira work items

2. **Adapters (Data Collectors)**
   - ASTAdapter
   - GitAdapter
   - CommentsAdapter
   - RelationshipsAdapter
   - WorkItemAdapter

3. **Knowledge Graph**
   - Entities (classes, functions, modules)
   - Relationships (dependencies, calls, extends)
   - Metadata (coverage, complexity, age)

4. **Query Engine**
   - Pattern matching
   - Relationship traversal
   - Similarity search
   - Recommendation engine

5. **Output (to Orchestrators)**
   - Suggested patterns
   - Refactoring recommendations
   - Coverage gaps
   - Complexity analysis

**Benefits:**
- Shows data flow through domain brain
- Clarifies adapter roles
- Illustrates query capabilities

---

#### 3.3 **Knowledge Ingestion Pipeline** (Mermaid)
**Purpose:** Show how YAML-based knowledge enters and is applied

**Type:** Mermaid flowchart

**Stages:**
1. **Discovery**
   - Scan cortex_brain/tier3/knowledge/
   - Detect YAML files by domain

2. **Validation**
   - Schema validation
   - Circular reference detection
   - Conflict resolution

3. **Loading**
   - Parse YAML into domain objects
   - Build indices for fast lookup
   - Register with knowledge repository

4. **Integration**
   - Wire to TDD Orchestrator
   - Wire to Refactoring Orchestrator
   - Register best practices
   - Attach to templates

5. **Application**
   - Guidance at RED phase
   - Best practice injection at REFACTOR phase
   - Pattern recommendation at synthesis

6. **Auditing**
   - Log which knowledge was applied
   - Track effectiveness
   - Version control

**Benefits:**
- Shows path from YAML to operational effect
- Clarifies when knowledge is applied
- Aids debugging of knowledge issues

---

#### 3.4 **TDD Workflow with Knowledge Injection** (D3.js)
**Purpose:** Show complete TDD cycle with knowledge applied at each stage

**Type:** D3.js Circular Flow Diagram

**Stages:**
1. **RED Phase**
   - Load Tier 1 requirements (AC-IDs)
   - Generate failing test
   - Knowledge: Test pattern templates
   - Git: Create feature branch

2. **GREEN Phase**
   - Minimal implementation
   - Make test pass
   - Knowledge: None (pure functionality)
   - Metrics: Track implementation time

3. **REFACTOR Phase**
   - Apply best practices (Tier 2 knowledge)
   - Improve code quality
   - SOLID principles, DRY, YAGNI
   - Knowledge: Best practice YAMLs

4. **Validation**
   - All tests still passing
   - Coverage maintained
   - Complexity reduced

5. **Evidence & Audit**
   - Bundle test results
   - Bundle coverage report
   - Bundle git diffs
   - Create audit log entry

6. **Git Checkpoint**
   - Commit with AC-ID reference
   - Tag with version
   - Push to branch

**Cycle repeats** for next requirement

**Benefits:**
- Shows complete workflow
- Illustrates knowledge role at each phase
- Clarifies evidence collection

---

### Category 4: Resilience & Error Handling (3 Diagrams)

#### 4.1 **Circuit Breaker State Machine** (Mermaid + D3.js)
**Purpose:** Visualize resilience pattern that prevents cascading failures

**Mermaid Diagram:** State machine with transitions

**D3.js Interactive:** Animated transitions showing:
- State indicators (CLOSED → OPEN → HALF_OPEN → CLOSED)
- Threshold crossings
- Timeout countdowns
- Success/failure metrics

**Annotations:**
- Failure rates
- Success thresholds
- Timeout durations
- Per-service configuration overrides

**Benefits:**
- Makes circuit breaker logic obvious
- Shows state transitions
- Clarifies configuration impact

---

#### 4.2 **Error Recovery Paths** (Mermaid)
**Purpose:** Show all possible error scenarios and recovery mechanisms

**Type:** Mermaid flowchart with error nodes

**Paths:**
1. **Transient Errors**
   - Initial failure → Retry with exponential backoff
   - Success → Continue
   - Max retries → Circuit breaker
   - Degraded mode available → Switch to partial function

2. **Persistent Errors**
   - Initial failure → Circuit breaker
   - Endpoint marked OPEN
   - HALF_OPEN probe attempts every 30s
   - Success → Close circuit
   - Continued failure → Stay OPEN

3. **Partial Failures**
   - Some components work
   - Non-critical dependency missing
   - Activate degraded mode
   - Log but continue

4. **Critical Failures**
   - Fatal error detected
   - Rollback to previous state
   - Escalate to operator
   - Graceful shutdown if necessary

**Annotations:**
- Logging points
- Audit entries
- User notifications
- Metrics recorded

**Benefits:**
- Makes error handling explicit
- Shows recovery possibilities
- Clarifies failure categories

---

#### 4.3 **Resilience Configuration & Tuning** (D3.js)
**Purpose:** Help operators understand resilience settings and impact

**Type:** D3.js Dashboard with interactive controls

**Sections:**
1. **Global Settings**
   - Token budget cap (%)
   - Max execution rounds
   - Default timeout
   - Retry base delay

2. **Per-Service Circuit Breaker**
   - Failure threshold
   - Failure rate threshold (%)
   - Timeout in OPEN state
   - Success threshold to CLOSE
   - Sliders to tune each

3. **Impact Visualization**
   - Simulated request flow under different settings
   - Expected success rate
   - Expected degradation
   - Recovery time estimates

4. **Best Practices**
   - Recommended settings by service
   - Common failure patterns
   - Tuning checklist

**Benefits:**
- Makes resilience settings understandable
- Shows impact of configuration changes
- Aids operational decision-making

---

### Category 5: System Metrics & Observability (2 Diagrams)

#### 5.1 **Audit Trail & Evidence Trail** (D3.js Timeline)
**Purpose:** Show how every operation is audited and evidence is collected

**Type:** D3.js Interactive Timeline

**Timeline Shows:**
- Request entry (AC_START)
- Each phase with timestamp
- State checkpoints
- Each decision point
- Governance checks and results
- Error recovery attempts
- Response exit (AC_COMPLETE)

**For Each Event:**
- Show what was logged
- Show hash chain entry
- Show evidence collected
- Show compliance validations

**Benefits:**
- Makes audit trail visible
- Shows evidence collection
- Aids compliance demonstrations

---

#### 5.2 **Performance & Metrics Dashboard** (D3.js)
**Purpose:** Show system health and performance metrics

**Type:** D3.js Multi-panel Dashboard

**Panels:**
1. **Throughput**
   - Requests/second
   - Orchestrator distribution
   - Trend over time

2. **Latency**
   - P50, P95, P99 latencies
   - By orchestrator
   - By phase

3. **Error Rates**
   - By error type
   - By orchestrator
   - Circuit breaker openings

4. **Resource Usage**
   - Token budget utilization
   - Memory usage
   - Database connections

5. **Governance Compliance**
   - CORE rules violations (count)
   - Rejections by rule
   - Audit trail completeness

6. **Knowledge Effectiveness**
   - Best practices applied (count)
   - Refactoring suggestions accepted
   - Coverage improvement

**Benefits:**
- Provides operational visibility
- Shows system health at a glance
- Aids capacity planning

---

## 📋 Implementation Priorities

### Phase 1: High-Impact, Low-Complexity (Weeks 1-2)

1. **Complexity-Aware Confirmation Gate Decision Tree** (Mermaid)
   - Time: 2 hours
   - Impact: Clarifies approval logic for users
   - Dependency: None

2. **Circuit Breaker State Machine** (Mermaid)
   - Time: 1.5 hours
   - Impact: Makes resilience obvious
   - Dependency: None

3. **Master Orchestrator ConversationProtocol** (Mermaid Sequence)
   - Time: 3 hours
   - Impact: Clarifies turn-based execution
   - Dependency: Existing docs

### Phase 2: Medium-Impact, Medium-Complexity (Weeks 3-4)

4. **Tier 0-3 Governance Pyramid** (D3.js Interactive)
   - Time: 8-10 hours
   - Impact: Visual hierarchy aids understanding
   - Dependency: Governance data available

5. **LENS Protocol Pipeline** (Mermaid + D3.js)
   - Time: 6-8 hours
   - Impact: Demystifies intent comprehension
   - Dependency: LENS phase documentation

6. **Domain Brain Architecture & Adapters** (D3.js)
   - Time: 6-8 hours
   - Impact: Shows knowledge ingestion
   - Dependency: Adapter code review needed

### Phase 3: Strategic, Complex (Weeks 5-8)

7. **Request Lifecycle Flow** (D3.js Sankey)
   - Time: 10-12 hours
   - Impact: Complete end-to-end visibility
   - Dependency: All phases documented

8. **TDD Workflow with Knowledge Injection** (D3.js Circular)
   - Time: 8-10 hours
   - Impact: Shows TDD + knowledge integration
   - Dependency: TDD phase documentation

9. **Governance Enforcement Points Timeline** (D3.js)
   - Time: 8-10 hours
   - Impact: Shows audit trail creation
   - Dependency: Timeline data availability

### Phase 4: Analytics & Monitoring (Weeks 9-12)

10. **Performance & Metrics Dashboard** (D3.js)
    - Time: 12-16 hours
    - Impact: Operational visibility
    - Dependency: Metrics infrastructure

11. **Audit Trail & Evidence Trail** (D3.js Timeline)
    - Time: 8-10 hours
    - Impact: Compliance visibility
    - Dependency: Audit logger implementation

12. **Orchestrator Routing Decision Matrix** (D3.js Heat Map)
    - Time: 6-8 hours
    - Impact: Shows routing logic
    - Dependency: Routing data collection

---

## 🛠️ Technical Implementation Notes

### Mermaid Diagrams
- **Location:** `docs/04-architecture/_diagrams/`
- **Format:** `.mmd` files embedded in markdown
- **Rendering:** Built-in mkdocs-mermaid plugin
- **Version Control:** Auto-tracked with docs
- **No external dependencies:** Self-contained

**Best Practices:**
- Keep diagrams < 100 nodes for performance
- Use subgraphs for modularity
- Color code by theme (governance, flow, data)
- Add styling comments for clarity

### D3.js Visualizations
- **Location:** `docs/_diagrams/d3/` (new directory)
- **Format:** HTML5 + JavaScript (standalone, no build)
- **Framework:** D3.js v7+ (CDN or local)
- **Data Format:** JSON from Python scripts

**Best Practices:**
- Create Python script to generate JSON data
- Implement responsive design (mobile-friendly)
- Add loading indicators for data fetches
- Implement hover tooltips for details
- Support dark/light themes to match mkdocs

### Integration with Documentation
- Embed Mermaid diagrams directly in markdown
- Create D3.js visualization hub page
- Link visualizations from relevant sections
- Provide "View Interactive Version" buttons
- Maintain accessibility (alt-text, descriptions)

---

## 🎨 Design Principles for Visualizations

### Color Coding Scheme
```
Governance (Red/Orange):
  - TIER 0 Rules: #D32F2F (red)
  - Critical violations: #E64A19 (orange-red)

Processing (Blue/Cyan):
  - Data flow: #1976D2 (blue)
  - Queries: #0288D1 (light blue)

Success/Valid (Green):
  - Completed stages: #388E3C (green)
  - Approved decisions: #66BB6A (light green)

Warning/Partial (Yellow):
  - Partial failures: #FBC02D (yellow)
  - Circuit breaker HALF_OPEN: #FFB300 (amber)

Neutral/Info (Gray/Purple):
  - Data sources: #757575 (gray)
  - Metadata: #7B1FA2 (purple)
```

### Typography
- **Headers:** Bold, large (26-32px)
- **Labels:** Medium (14-16px)
- **Annotations:** Small (12-14px)
- **Font:** Consistent with mkdocs theme (System fonts)

### Layout
- **Hierarchy:** Top-down flows, left-to-right reading
- **Whitespace:** 20-40% empty space for clarity
- **Grouping:** Related items visually clustered
- **Density:** 6-8 items per visual grouping

---

## 📈 Success Metrics

After implementing these diagrams, measure:

1. **Documentation Engagement**
   - Time spent on architecture pages
   - Click-through to related docs
   - D3.js interactivity usage

2. **Understanding Quality**
   - Reduced GitHub issues about "how CORTEX works"
   - Increased developer contributions
   - Better onboarding speed

3. **Diagram Maintenance**
   - Diagrams kept current
   - User feedback incorporated
   - Performance monitored

---

## 📝 Next Steps

1. **Review & Prioritize:** Select which diagrams to implement first
2. **Create D3.js Template:** Set up boilerplate for consistency
3. **Build Data Pipeline:** Create Python scripts to generate D3.js data
4. **Implement Phase 1:** Start with high-impact, low-complexity diagrams
5. **User Feedback:** Iterate based on user testing
6. **Maintenance Plan:** Establish process to keep diagrams current

---

## Appendix: Example D3.js Data Structure

```json
{
  "governance_pyramid": {
    "tiers": [
      {
        "tier": 0,
        "name": "CORE Rules",
        "color": "#D32F2F",
        "categories": [
          {
            "id": "orchestration",
            "name": "Orchestration Lifecycle",
            "rules": [
              {
                "id": "CORE-001",
                "name": "Incremental Autonomous Execution",
                "description": "Prevent token limit failures",
                "enforced_at": "Phase 0"
              }
            ]
          }
        ]
      }
    ]
  },
  "request_lifecycle": {
    "stages": [
      {
        "id": 1,
        "name": "Entry",
        "duration_ms": 100,
        "components": ["API Gateway", "Auth"],
        "exit_conditions": ["success", "auth_fail"]
      }
    ]
  }
}
```

---

## 📚 References

- **Documentation:** docs/04-architecture/
- **Governance:** docs/01-cortex-brain/01-tier0-governance.md
- **Design Principles:** docs/04-architecture/2-design-principles.md
- **Orchestration Engine:** docs/04-architecture/3-orchestration-engine.md
- **Resilience Patterns:** docs/04-architecture/5-resilience-patterns.md

---

**Author:** Asif Hussain  
**Status:** 📋 Proposal - Ready for Review  
**Next Review:** After prioritization discussion
