/CORTEX /cortex-architect

Follow the rules defined in:
- CORTEX.prompt.md
- cortex-doc.prompt.md
- cortex-doc agents
- cortex-registry governance

All agent rules MUST be applied automatically.

This task designs and implements a **CORTEX Learning System** built from the knowledge contained in `cortex-registry`.

This learning system must transform CORTEX knowledge YAMLs into a **three-level interactive learning application designed for human learning**.

The system must be **manually designed**, not generated from templates.

Each learning path must have **custom designed UI and diagrams optimized for teaching the subject matter**.

---

# Challenge-First Protocol

Before proposing the implementation:

1. Perform a **full audit of existing CORTEX capabilities** including:

- cortex-registry knowledge YAMLs
- cortex-doc documentation engine
- diagram generation systems
- D3 visualization pipelines
- workflow composer
- orchestrator architecture
- LENS intelligence
- registry indexing
- documentation generation

2. Identify:

| Category | Requirement |
|--------|--------|
Existing Capabilities | What CORTEX already supports |
Partial Capabilities | Systems that exist but must be extended |
New Capabilities | What must be created |

3. Assume the user has **no knowledge of CORTEX architecture**.

Explain the architecture simply.

4. Evaluate every recommendation using CORTEX design pillars:

| Pillar | Evaluation Criteria |
|------|------|
Extensibility | Can new learning paths be added easily |
Scalability | Can system support thousands of knowledge objects |
Accuracy | YAML knowledge remains authoritative |
Collaboration | Teams can extend knowledge |
Maintainability | Prevent duplication and drift |

Ensure:

- MCP-first exposure
- Orchestrator integrity
- Registry-driven knowledge
- Zero regression risk

---

# Learning System Objective

Create an **interactive educational platform** built from CORTEX knowledge.

The system should feel like:

"CORTEX University"

It must teach:

- architecture
- patterns
- workflows
- infrastructure
- enterprise planning
- AI orchestration

---

# Pedagogical Design Requirements

Use **modern educational best practices**.

Key learning principles:

### 1 Active Learning

Students learn better when interacting with examples and diagrams.

Example-based learning improves comprehension and engagement in software engineering education. :contentReference[oaicite:0]{index=0}

### 2 Visual Knowledge Mapping

Concept maps help learners understand relationships between concepts. :contentReference[oaicite:1]{index=1}

### 3 Multi-Diagram Teaching

Different diagrams explain different aspects of systems.

Common software architecture diagrams include:

- class diagrams
- sequence diagrams
- activity diagrams
- component diagrams
- deployment diagrams :contentReference[oaicite:2]{index=2}

### 4 Interactive Visualization

Interactive visualizations improve comprehension compared to static diagrams. :contentReference[oaicite:3]{index=3}

---

# Learning Architecture

The learning system must have **three levels**.

---

# LEVEL 1 — Learning Paths (Portal)

Purpose:

Help users choose **what they want to learn**.

Design:

Large interactive learning cards.

Each card contains:

- icon
- concept summary
- visual preview
- difficulty level
- number of topics
- estimated learning time

Example learning paths:

Architecture Patterns  
AI Orchestration Architecture  
Workflow Automation  
Enterprise Planning Systems  
Response Engineering  
Infrastructure Architecture  
Enterprise AI Systems  

### UI Design

Grid layout with:

Tailwind  
FontAwesome icons  
animated hover previews  

Each card must include **visual micro-diagram previews**.

Example preview diagrams:

Architecture Patterns

Concept Map diagram

Boxes connected by arrows showing relationships between patterns.

Concept maps visually represent relationships between ideas. :contentReference[oaicite:4]{index=4}

Infrastructure

Mini system topology graph.

---

# LEVEL 2 — Concept Explorer

Purpose:

Explore concepts within a learning path.

Each learning path must have **custom visual layout**.

---

## Architecture Patterns Explorer

Display pattern cards.

Each card includes:

- pattern type
- short explanation
- micro diagram
- when to use
- anti-pattern warning

### Required Diagrams

Class Diagram

Used to show pattern structure.

Class diagrams show relationships between classes and components. :contentReference[oaicite:5]{index=5}

Sequence Diagram

Used to show runtime interaction.

Sequence diagrams illustrate how components interact over time. :contentReference[oaicite:6]{index=6}

Concept Map

Shows relationship between patterns.

---

## Workflow Automation Explorer

Best diagram types:

Activity Diagrams

Used to show workflows and business processes. :contentReference[oaicite:7]{index=7}

Interaction Overview Diagrams

Used for complex workflows with nested interactions. :contentReference[oaicite:8]{index=8}

Timeline diagrams showing lifecycle.

---

## Infrastructure Explorer

Best diagram types:

Component Diagram

Shows system modules and dependencies.

Deployment Diagram

Shows infrastructure nodes and deployment relationships.

C4 Architecture Diagrams

C4 model decomposes systems into containers and components. :contentReference[oaicite:9]{index=9}

Graph visualizations using D3.

---

## Planning Explorer

Best diagrams:

Timeline diagrams  
Gantt charts  
Dependency graphs  

These visualize phases and deliverables.

---

## Response Engineering Explorer

Display template cards.

Each card shows:

- template structure
- variables
- example outputs
- real use cases

Interactive example editor.

---

# LEVEL 3 — Deep Learning Pages

Each concept gets a **full educational page**.

Every page must contain:

---

## Concept Explanation

Explain the idea in simple language.

---

## Real-World Analogy

Example:

Factory Pattern

Analogy:

Restaurant kitchen preparing meals.

---

## CORTEX Implementation

Explain how CORTEX implements the concept.

Show relevant code references.

---

## Interactive Diagrams

Diagrams must be interactive.

Required diagram types per concept:

### Pattern Pages

Class diagram  
Sequence diagram  
Concept map  

### Workflow Pages

Activity diagram  
Lifecycle timeline  

### Infrastructure Pages

C4 architecture diagrams  
Deployment diagrams  
Dependency graphs  

### Planning Pages

Phase timeline  
Dependency graph  

---

# Diagram Implementation

All diagrams must use:

D3.js

Examples:

Force-directed graph

Used for concept maps.

Sequence diagram

Animated message flow.

Lifecycle diagram

Animated phase transitions.

---

# External Research Requirement

Enhance YAML knowledge using trusted architecture sources.

Required research sources:

Martin Fowler Architecture Catalog  
https://martinfowler.com

Refactoring Guru Pattern Guides  
https://refactoring.guru/design-patterns

Microsoft Architecture Center  
https://learn.microsoft.com/azure/architecture

AWS Architecture Center  
https://aws.amazon.com/architecture

Google Cloud Architecture Framework  
https://cloud.google.com/architecture/framework

D3 Visualization Examples  
https://observablehq.com/@d3

Use them to improve:

- explanations
- analogies
- diagrams
- examples

Do NOT copy content.

Synthesize ideas.

---

# Knowledge Extraction Strategy

Extract information from:

cortex-registry YAMLs

Convert YAML structures into:

- concept definitions
- diagrams
- explanations

The YAML remains the **source of truth**.

---

# Integration with cortex-doc

All generated learning pages must be validated using:

cortex-doc.prompt.md

Agents must enforce:

documentation structure  
diagram rules  
content synthesis rules  

---

# Technical Stack

Frontend

React  
Tailwind  
FontAwesome  

Visualization

D3.js  
Observable patterns  

Content Engine

YAML parsing  
knowledge synthesis  

---

# Deliverables

Design:

Learning architecture  
Learning path definitions  
View specifications  
Diagram specifications  
Knowledge extraction system  

---

# Response Format

Follow CORTEX executive format.

≤ 60 second read time.

Use:

visual hierarchy  
tables  
sections  

All responses must remain **inline in the VSCode Copilot Chat session**.

Never generate external markdown files.

Never generate summary documents.

Never produce reports.

Return only in the GitHub Copilot Chat session.
