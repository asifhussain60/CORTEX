/CORTEX /cortex-architect

Follow all rules defined in:

- CORTEX.prompt.md
- cortex-doc.prompt.md
- cortex-doc agents
- cortex-registry governance

All agent rules MUST apply automatically.

Your task is to design and implement a **CORTEX Learning System** that transforms knowledge stored in `cortex-registry` YAML files into a **high-quality interactive learning platform**.

The system must follow **modern software engineering education best practices** and **must be manually designed**, not auto-generated.

Each learning path must have **custom UI, custom diagrams, and curated explanations optimized for learning the specific topic**.

---

# CRITICAL DESIGN RULE

Do NOT create generic pages.

Each learning path must be **manually crafted** with:

- tailored layout
- tailored diagrams
- tailored learning flow
- tailored visuals

The system must feel like a **carefully designed educational platform**, not a documentation generator.

---

# CHALLENGE-FIRST PROTOCOL

Before implementing anything:

Perform a **microscopic audit of CORTEX capabilities**.

Analyze:

• cortex-registry knowledge YAMLs  
• cortex-doc documentation engine  
• D3 visualization capability  
• diagram pipelines  
• workflow composer  
• orchestrator architecture  
• LENS intelligence  
• registry indexing  
• documentation synthesis  
• MCP tool exposure  

Determine:

| Category | Description |
|--------|-------------|
| Existing Capabilities | What already exists |
| Partial Capabilities | What needs extension |
| Missing Capabilities | What must be built |

Assume the user has **no knowledge of CORTEX architecture**.

Explain architecture simply.

Evaluate every design decision using CORTEX pillars:

| Pillar | Requirement |
|------|------|
Extensibility | Add new learning paths without redesign |
Scalability | Support thousands of knowledge nodes |
Accuracy | YAML remains the source of truth |
Collaboration | Teams can contribute knowledge |
Maintainability | Prevent duplication and drift |

Ensure:

• MCP-first exposure  
• Orchestrator integrity  
• Registry-driven architecture  
• Zero regression risk  

---

# LEARNING SYSTEM OBJECTIVE

Build an interactive learning environment called:

**CORTEX University**

The system teaches:

• architecture patterns  
• AI orchestration  
• workflow automation  
• enterprise planning  
• response engineering  
• infrastructure architecture  

The platform should feel like **exploring a system map**, not reading documentation.

---

# PEDAGOGICAL BEST PRACTICES

Follow research-backed learning principles.

### Active Learning

Interactive examples dramatically improve comprehension in engineering education.

### Visual Knowledge Mapping

Concept maps help learners understand relationships between ideas.

### Multi-Diagram Teaching

Different diagrams explain different aspects of systems.

Common architecture diagrams include:

• class diagrams  
• sequence diagrams  
• activity diagrams  
• component diagrams  
• deployment diagrams  

### Progressive Disclosure

Users learn best when information is revealed gradually.

---

# THREE LEVEL LEARNING STRUCTURE

The system must have **three levels only**.

The knowledge graph must be embedded inside levels 2 and 3.

---

# LEVEL 1 — LEARNING PATH PORTAL

Purpose:

Help users choose **what they want to learn**.

UI:

Large animated cards.

Each card contains:

• icon  
• concept preview  
• difficulty level  
• number of topics  
• estimated learning time  
• mini concept diagram  

Example learning paths:

Architecture Patterns  
AI Orchestration  
Workflow Automation  
Enterprise Planning  
Response Engineering  
Infrastructure Architecture  
Enterprise AI Systems  

Card preview diagrams should include **concept maps** showing relationships between major topics.

Concept maps visualize how ideas connect.

---

# LEVEL 2 — CONCEPT EXPLORER

This level introduces **concept exploration with a knowledge graph**.

Instead of a static list of topics, display an **interactive concept map**.

Concepts appear as nodes.

Relationships appear as edges.

Example node relationships:

Pattern → used by → Orchestrator  
Pattern → implemented in → Code  
Pattern → referenced by → Workflow  

Graph type:

**Force-Directed Graph**

This graph type allows interactive exploration of relationships.

Users can:

• zoom  
• drag nodes  
• click nodes to open Level 3  

---

## ARCHITECTURE PATTERNS EXPLORER

Display pattern nodes.

Required diagrams:

### Class Diagram

Shows structural relationships between pattern participants.

### Sequence Diagram

Shows runtime interactions between components.

### Concept Map

Shows relationships between patterns.

Example:

Factory Pattern  
Mediator Pattern  
Template Method  

---

## WORKFLOW AUTOMATION EXPLORER

Best diagrams:

Activity Diagrams

Used to show workflows and processes.

Interaction diagrams

Show nested orchestration flows.

Lifecycle diagrams

Show orchestration lifecycle.

---

## INFRASTRUCTURE EXPLORER

Use:

### C4 Model Diagrams

The C4 model describes systems using four abstraction levels:

Context  
Container  
Component  
Code  

### Deployment Diagrams

Show infrastructure nodes.

### Dependency Graphs

Show API relationships.

Graph nodes:

applications  
apis  
platforms  

---

## PLANNING EXPLORER

Visualize phases using:

Timeline diagrams  
Gantt charts  
Dependency graphs  

These diagrams show phase progression.

---

## RESPONSE ENGINEERING EXPLORER

Display template structures.

Each template node shows:

• sections  
• variables  
• example outputs  

Provide interactive example generator.

---

# LEVEL 3 — DEEP LEARNING PAGE

Each concept gets a **full educational page**.

This page must include:

---

## Concept Explanation

Simple explanation of the concept.

---

## Real-World Analogy

Example:

Factory Pattern

Restaurant kitchen analogy.

---

## CORTEX Implementation

Explain how the concept appears inside CORTEX.

Link to source files.

---

## Interactive Diagrams

Each concept must have specific diagrams.

### Pattern Pages

Class diagram  
Sequence diagram  
Concept map  

### Workflow Pages

Activity diagram  
Lifecycle timeline  

### Infrastructure Pages

C4 architecture diagram  
Deployment diagram  
Dependency graph  

### Planning Pages

Phase timeline  
Dependency graph  

---

# EMBEDDED KNOWLEDGE GRAPH

The learning system must include a **knowledge graph**.

This graph connects:

Concepts  
Patterns  
Workflows  
Infrastructure  
Planning phases  

Graph structure example:

Pattern → used by → Orchestrator  
Pattern → referenced in → Phase  
Workflow → executed by → Orchestrator  
Infrastructure → hosts → Application  

Graph visualization must use:

D3 Force Directed Graph.

Users should be able to explore knowledge visually.

---

# EXTERNAL RESEARCH

Enhance explanations using authoritative sources.

Research references:

Martin Fowler Architecture Catalog  
https://martinfowler.com

Refactoring Guru  
https://refactoring.guru/design-patterns

Microsoft Architecture Center  
https://learn.microsoft.com/azure/architecture

AWS Architecture Center  
https://aws.amazon.com/architecture

Google Cloud Architecture Framework  
https://cloud.google.com/architecture/framework

D3 Visualization Examples  
https://observablehq.com/@d3

Use them to enhance:

• explanations  
• diagrams  
• examples  

Do NOT copy content.

Synthesize ideas.

---

# KNOWLEDGE EXTRACTION

Knowledge must come from:

`cortex-registry` YAML files.

Convert YAML knowledge into:

• explanations  
• diagrams  
• graph nodes  
• relationships  

YAML remains the **single source of truth**.

---

# INTEGRATION WITH CORTEX DOC SYSTEM

All generated pages must be validated through:

`cortex-doc.prompt.md`

Agents must enforce:

• documentation structure  
• diagram rules  
• content synthesis rules  

---

# TECHNOLOGY STACK

Frontend

React  
Tailwind  
FontAwesome  

Visualization

D3.js  
Observable  

Knowledge Engine

YAML parsing  
knowledge graph generator  

---

# DELIVERABLES

Design:

Learning architecture  
Learning paths  
Explorer layouts  
Diagram specifications  
Knowledge graph system  

---

# RESPONSE FORMAT

Return response in CORTEX executive format.

≤ 60 second read time.

Use:

• sections  
• visual hierarchy  
• tables  

All feedback must remain **inline in VSCode Copilot Chat**.

Do NOT generate markdown files.

Do NOT generate reports.

Return response only inside the chat.
