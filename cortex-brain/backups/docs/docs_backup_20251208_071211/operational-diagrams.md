# ⚙️ Operational Diagrams

Visual representations of CORTEX's workflows and operational processes.

---

## Operation Execution Pipeline

Step-by-step flow of operation execution from intent detection to validation.

<figure>
  <img src="images/diagrams/operational/07-operation-pipeline.png" alt="Operation Execution Pipeline" style="border: 3px solid #f39c12; border-radius: 8px; width: 100%;"/>
  <figcaption><strong>Detection:</strong> Natural language intent classification and operation matching<br/>
  <strong>Preparation:</strong> Context gathering, memory retrieval, validation checks<br/>
  <strong>Execution:</strong> Agent coordination, operation steps, progress tracking<br/>
  <strong>Completion:</strong> Result validation, memory persistence, response formatting</figcaption>
</figure>

**Pipeline Phases:**
- 🎯 **Intent Detection**: Natural language analysis, template matching
- 📋 **Operation Mapping**: Match intent to registered operations
- 🔍 **Context Gathering**: Tier 1 memory search, file analysis
- ✅ **Pre-flight Validation**: Brain protection, dependency checks
- ⚡ **Execution**: Agent-driven implementation
- 🏥 **Health Monitoring**: Real-time validation during execution
- 📊 **Result Validation**: Output verification, test execution
- 💾 **Persistence**: Save to Tier 1, extract patterns for Tier 2

**Related Documentation:**
- [FEATURES.md](FEATURES.md) - Available operations
- [HELP-SYSTEM.md](HELP-SYSTEM.md) - Operation commands

---

## Setup Orchestration (Part A)

Cross-platform environment configuration and initialization workflow.

<figure>
  <img src="images/diagrams/operational/08a-setup-orchestration.png" alt="Setup Orchestration Part A" style="border: 3px solid #f39c12; border-radius: 8px; width: 100%;"/>
  <figcaption><strong>Platform Detection:</strong> Automatic OS detection (Windows, Mac, Linux)<br/>
  <strong>Environment Setup:</strong> Python virtual environment, dependencies, path configuration<br/>
  <strong>Directory Structure:</strong> Create cortex-brain folders, initialize databases</figcaption>
</figure>

**Setup Steps (Part A):**
- 🖥️ **Platform Detection**: Auto-detect Windows/Mac/Linux
- 🐍 **Python Environment**: Virtual environment creation, activation
- 📦 **Dependencies**: Install requirements.txt packages
- 📁 **Directory Structure**: Create cortex-brain hierarchy
- 🗄️ **Database Init**: Initialize Tier 1 (conversations) and Tier 2 (patterns) SQLite databases
- ⚙️ **Configuration**: Generate cortex.config.json from template

**Related Documentation:**
- [HELP-SYSTEM.md](HELP-SYSTEM.md) - Setup commands
- [CAPABILITIES-MATRIX.md](CAPABILITIES-MATRIX.md) - Platform support

---

## Setup Orchestration (Part B)

Plugin discovery, dependency resolution, and health validation.

<figure>
  <img src="images/diagrams/operational/08b-setup-orchestration.png" alt="Setup Orchestration Part B" style="border: 3px solid #f39c12; border-radius: 8px; width: 100%;"/>
  <figcaption><strong>Plugin Discovery:</strong> Scan src/plugins directory, register commands<br/>
  <strong>Dependency Resolution:</strong> Validate plugin dependencies, check external tools<br/>
  <strong>Health Validation:</strong> Run health checks, verify configuration, report status</figcaption>
</figure>

**Setup Steps (Part B):**
- 🔌 **Plugin Discovery**: Automatic plugin scanning
- 📋 **Command Registration**: Map natural language to plugin operations
- 🔍 **Dependency Check**: Validate required libraries, external tools
- 🏥 **Health Validation**: System health checks
- 🧪 **Test Execution**: Run smoke tests
- 📊 **Status Report**: Configuration summary, warnings, next steps

**Related Documentation:**
- [HELP-SYSTEM.md](HELP-SYSTEM.md) - Setup troubleshooting
- [FEATURES.md](FEATURES.md) - Plugin system

---

## Documentation Generation Workflow

Enterprise documentation orchestrator generating comprehensive documentation artifacts.

<figure>
  <img src="images/diagrams/operational/09-documentation-generation.png" alt="Documentation Generation Workflow" style="border: 3px solid #f39c12; border-radius: 8px; width: 100%;"/>
  <figcaption><strong>Generation Phase:</strong> Mermaid diagrams, DALL-E prompts, narratives, executive summary<br/>
  <strong>Integration Phase:</strong> IMAGE-CATALOG.yaml, story chapters, MkDocs configuration<br/>
  <strong>Build Phase:</strong> Static site generation, validation, deployment to GitHub Pages</figcaption>
</figure>

**Generation Components:**
- 📊 **Mermaid Diagrams**: 14 architectural, integration, and workflow diagrams
- 🎨 **DALL-E Prompts**: 14 image generation prompts (500-800 words each)
- 📝 **Narratives**: Technical explanations for each diagram
- 📋 **Executive Summary**: Feature list, metrics, capabilities
- 📖 **Story Chapters**: 13-chapter narrative split from master story
- 🖼️ **Image Integration**: IMAGE-CATALOG.yaml with metadata
- 🏗️ **MkDocs Build**: Generate static site with custom theme

**Related Documentation:**
- [FEATURES.md](FEATURES.md) - Documentation capabilities
- [HELP-SYSTEM.md](HELP-SYSTEM.md) - Generation commands

---

## Navigation

- **[Home](index.md)** - Return to documentation home
- **[Architecture Diagrams](architecture-diagrams.md)** - Core system architecture
- **[Integration Diagrams](integration-diagrams.md)** - Data flows and integrations
- **[Planning Diagrams](planning-diagrams.md)** - Strategic and planning systems

---

**Image Source:** Generated from DALL-E 3 prompts created by Enterprise Documentation Orchestrator  
**Diagram Metadata:** See [IMAGE-CATALOG.yaml](images/diagrams/IMAGE-CATALOG.yaml)  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.
