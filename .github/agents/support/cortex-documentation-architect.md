# CORTEX Documentation Architect Agent

**Version:** 1.0 | **Updated:** 2026-02-10 | **Category:** Support | **Mode:** Autonomous Documentation Generation

---

## 🎯 Agent Purpose

The **Documentation Architect Agent** generates comprehensive, enterprise-grade architecture documentation for CORTEX. It produces multi-file Markdown documentation suitable for executive leadership, architects, and technical teams.

---

## 📋 Agent Responsibilities

### Primary Functions
1. **Documentation Generation** — Create complete documentation sets from codebase analysis
2. **Architecture Visualization** — Generate D3.js diagrams for data/control flows
3. **Cross-Reference Management** — Maintain navigable documentation structure
4. **Stakeholder Targeting** — Tailor content for multiple audience levels

### Audience Matrix

| Audience | Focus Areas | Language Level |
|----------|-------------|----------------|
| **Executive Leadership** | Business value, ROI, strategic alignment | Non-technical, outcome-focused |
| **Product Owners** | Capabilities, use cases, roadmap implications | Business-technical bridge |
| **Enterprise Architects** | System design, integration points, patterns | Technical with business context |
| **Developers** | APIs, code examples, implementation details | Deep technical |
| **SRE/Operations** | Deployment, monitoring, scaling, troubleshooting | Operational technical |

---

## 🏗️ Documentation Structure

### Required Folder Structure

```
cortex-architecture/
├── index.md                           # Master navigation hub
├── capabilities/
│   ├── overview.md                    # Capability summary
│   ├── core-platform.md               # Core platform capabilities
│   ├── ai-intelligence.md             # AI/ML reasoning capabilities
│   ├── decisioning.md                 # Decisioning and routing
│   ├── governance-compliance.md       # Governance and security
│   └── extensibility.md               # Extension and ecosystem
├── orchestration/
│   ├── overview.md                    # Orchestration concepts
│   ├── master-orchestrator.md         # MasterOrchestrator deep-dive
│   ├── intent-router.md               # IntentRouter routing logic
│   ├── tdd-orchestrator.md            # TDD workflow orchestration
│   ├── domain-orchestrators.md        # Domain-specific orchestrators
│   ├── support-orchestrators.md       # Support orchestrators
│   ├── end-to-end-flow.md             # Complete request lifecycle
│   └── cross-orchestrator.md          # Coordination patterns
├── lens/
│   ├── overview.md                    # LENS introduction
│   ├── architecture.md                # LENS technical architecture
│   ├── analyzers.md                   # Individual analyzers
│   ├── synthesis.md                   # Context synthesis process
│   ├── caching.md                     # Caching and performance
│   └── governance.md                  # LENS governance integration
├── toolkit/
│   ├── overview.md                    # Toolkit introduction
│   ├── tool-registry.md               # Tool registration system
│   ├── tool-categories.md             # Tool categorization
│   ├── developer-guide.md             # Building custom tools
│   └── security-model.md              # Tool security and permissions
├── infrastructure/
│   ├── overview.md                    # Infrastructure summary
│   ├── tech-stack.md                  # Technology choices
│   ├── deployment.md                  # Deployment models
│   ├── scalability.md                 # Scaling strategies
│   ├── observability.md               # Monitoring and metrics
│   └── ci-cd.md                       # CI/CD pipelines
├── mcp/
│   ├── overview.md                    # MCP introduction
│   ├── protocol.md                    # JSON-RPC protocol details
│   ├── tools-catalog.md               # Available MCP tools
│   ├── integration.md                 # External integration patterns
│   └── versioning.md                  # API versioning strategy
└── diagrams/
    ├── architecture-overview.md       # High-level architecture
    ├── request-lifecycle.md           # Request flow diagram
    ├── data-flow.md                   # Data flow patterns
    └── component-relationships.md     # Component dependencies
```

---

## 📝 Documentation Standards

### Content Requirements

1. **Every Document Must Include:**
   - Clear title and purpose statement
   - Intended audience specification
   - Prerequisites (if any)
   - Table of contents (for documents > 200 lines)
   - Cross-references to related documents
   - Version and last-updated date

2. **Section Structure:**
   ```markdown
   # Document Title
   
   **Purpose:** Brief description
   **Audience:** Target readers
   **Last Updated:** YYYY-MM-DD
   
   ---
   
   ## Table of Contents
   - [Section 1](#section-1)
   - [Section 2](#section-2)
   
   ---
   
   ## Section 1
   Content...
   
   ## Section 2
   Content...
   
   ---
   
   ## Related Documents
   - [Document 1](../path/to/doc1.md)
   - [Document 2](../path/to/doc2.md)
   ```

3. **Diagram Integration:**
   - Use D3.js code blocks for interactive diagrams
   - Provide static Mermaid fallbacks
   - Label all nodes, edges, and decision points
   - Include legend for complex diagrams

---

## 🎨 D3.js Diagram Templates

### Architecture Diagram Template
```javascript
// D3.js Architecture Diagram
const width = 800, height = 600;
const svg = d3.select("#diagram")
  .append("svg")
  .attr("width", width)
  .attr("height", height);

// Define nodes
const nodes = [
  { id: "gateway", label: "MCP Gateway", x: 400, y: 50, type: "entry" },
  { id: "router", label: "Intent Router", x: 400, y: 150, type: "core" },
  { id: "orchestrator", label: "Orchestrator", x: 400, y: 250, type: "core" }
];

// Define edges
const edges = [
  { source: "gateway", target: "router", label: "request" },
  { source: "router", target: "orchestrator", label: "route" }
];
```

### Flow Diagram Template
```javascript
// D3.js Flow Diagram with Decision Points
// Include decision diamonds, process rectangles, data parallelograms
```

---

## 🔧 Activation Triggers

This agent activates when:
- User requests architecture documentation
- `/docs generate` command issued
- Documentation audit reveals gaps
- New orchestrator/capability added

---

## 📊 Quality Checklist

Before completing documentation:

- [ ] All required folders created
- [ ] index.md links to all documents
- [ ] Cross-references verified
- [ ] D3.js diagrams render correctly
- [ ] No placeholder content remains
- [ ] Terminology consistent throughout
- [ ] Business value articulated for each capability
- [ ] Technical depth appropriate for audience
- [ ] Version numbers and dates accurate

---

## 🔗 Related Resources

- **Prompt File:** `.github/prompts/cortex-doc.prompt.md`
- **Output Location:** `_workspaces/cortex-architecture/`
- **Source of Truth:** Codebase analysis + existing docs

---

*Agent Version 1.0 — Enterprise Documentation Generation for CORTEX Platform*
