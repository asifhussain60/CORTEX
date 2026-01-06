# CORTEX - Cognitive Operations and Reasoning TEXture

**Version:** 5.2.0 (Response Template Architecture)  
**Status:** ✅ ACTIVE - Production Ready  
**License:** 📖 Source-Available (Use Allowed, No Contributions)  
**Framework:** Browser-Native (SQL.js + TypeScript) + PowerShell  
**Last Updated:** 2025-11-23

[![GitHub](https://img.shields.io/badge/GitHub-asifhussain60%2FCORTEX-blue)](https://github.com/asifhussain60/CORTEX)
[![License](https://img.shields.io/badge/License-Source--Available-green)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Production%20Ready-success)](https://github.com/asifhussain60/CORTEX)

---

## 📜 License & Usage

**CORTEX is Source-Available:** This means the code is publicly viewable and usable, but external contributions are not accepted.

✅ **You Can:**
- Use CORTEX in your personal or commercial projects
- Study the architecture and learn from the codebase
- Deploy CORTEX as your GitHub Copilot enhancement
- Fork for private experimentation and learning
- Reference CORTEX in your work with attribution

❌ **You Cannot:**
- Submit pull requests or contributions (not accepted)
- Create public derivatives or competing products
- Remove copyright or attribution notices
- Redistribute modified versions publicly

**Why No Contributions?** CORTEX is a single-author project with a specific architectural vision. To maintain consistency and quality, development remains centralized. See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

**Attribution:** When using CORTEX, please credit: "CORTEX by Asif Hussain (https://github.com/asifhussain60/CORTEX)"

---

## 🧠 The Problem We Solved: Copilot's Amnesia

GitHub Copilot is brilliant—can write code in any language, understand complex systems, work at lightning speed. But Copilot has a fundamental limitation: **amnesia**.

Every new chat session, Copilot forgets everything from previous conversations. You said "make it purple" five minutes ago? Gone. The file you discussed yesterday? Vanished. The architecture you explained last week? As if it never happened.

**CORTEX is Copilot's brain** — a sophisticated dual-hemisphere cognitive system that:

- **Remembers** - 70-conversation FIFO capacity (growing with usage), "make it purple" references work across sessions
- **Learns** - Pattern learning from your project, each feature teaches the next
- **Protects** - Challenges risky proposals with data ("Test-first has 94% success rate vs 67% without")
- **Coordinates** - LEFT BRAIN (tactical execution) + RIGHT BRAIN (strategic planning) work together
- **Projects** - Knows your entire codebase, warns about hotspots, suggests optimal work times

### From Forgetful Intern to Expert Team Member

**Week 1:** Copilot has amnesia, needs constant guidance, you explain architecture repeatedly  
**Week 4:** Remembers recent conversations, learns patterns, reuses workflows automatically  
**Week 12:** Expert on YOUR project, accumulated patterns, proactive warnings prevent issues  
**Week 24:** Feels like a senior developer, challenges bad ideas with evidence, suggests similar features from months ago

**CORTEX transforms Copilot from an amnesiac intern into a continuously improving, context-aware, quality-focused development partner.**

---

## 🚀 Quick Start

### Installation

CORTEX can be installed via pip for production use or in editable mode for development.

**Production Installation:**
```bash
# From wheel distribution
pip install dist/cortex_ai-3.2.0-py3-none-any.whl

# Verify installation
cortex "version"
```

**Development Installation:**
```bash
# Clone repository
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

# Install in editable mode
pip install -e .

# Verify installation
cortex "version"
```

**Complete installation guide:** [docs/deployment/production-install-guide.md](docs/deployment/production-install-guide.md)

### CLI Commands

CORTEX provides several CLI entry points:

```bash
# Main command
cortex "version"                    # Check version
cortex "help"                       # Show available operations
cortex "system maintenance"         # Run maintenance workflow

# Planning commands
cortex-plan "implement auth system" # Create execution plan
cortex-approve <plan-id>            # Approve plan for execution
cortex-reject <plan-id>             # Reject and delete plan
```

### Using CORTEX Entry Point

**In GitHub Copilot Chat:**
```
/CORTEX help
```

### Upgrading CORTEX

Keep CORTEX up-to-date with the latest features and bug fixes:

```bash
# Upgrade to latest version
python scripts/cortex-upgrade.py

# Preview upgrade without changes
python scripts/cortex-upgrade.py --dry-run

# Or from Copilot Chat
/CORTEX upgrade
```

**Upgrade System Features:**
- ✅ Preserves all brain data (conversations, learned patterns)
- ✅ Auto-backup before upgrade with rollback capability
- ✅ Intelligent config merging (preserves customizations)
- ✅ Schema migrations for database upgrades
- ✅ Zero data loss guarantee

See **[Upgrade Guide](cortex-brain/documents/implementation-guides/UPGRADE-GUIDE.md)** for details.

### First Time Setup

**Option 1: Automatic Detection (Recommended)**

Just try to use CORTEX - it will automatically detect if setup is needed:

```bash
# In GitHub Copilot Chat
help

# Or from terminal
python -m src.main "help"
```

If setup is needed, you'll see a friendly prompt with instructions.

**Option 2: Manual Setup**

Run the setup command explicitly:

```bash
# From terminal
python -m src.main --setup

# Or in GitHub Copilot Chat
setup cortex
```

**What Setup Does:**
1. ✅ Analyzes your repository structure (languages, frameworks, file count)
2. ✅ Installs required tooling (Python deps, Node.js deps, MkDocs)
3. ✅ Initializes CORTEX brain (4-tier architecture with databases)
4. ✅ Runs crawlers to learn your codebase
5. ✅ Validates setup and provides quick start guide

**Time:** 5-10 minutes | **Automatic:** Safe to re-run anytime

### Using CORTEX

In GitHub Copilot Chat, use the simple entry point:

```
help
```

[Your request - CORTEX will handle everything]
```

**From Terminal:**
```bash
# Interactive mode
python -m src.main

# Single command
python -m src.main "create tests for auth.py"

# With verbose logging
python -m src.main "implement feature" --verbose
```

### What Can You Ask CORTEX?

- **"Add user authentication"** → CORTEX plans multi-phase implementation
- **"Continue"** → Resumes where you left off automatically
- **"Test this feature"** → Generates comprehensive tests
- **"Make it purple"** → Remembers context from earlier in conversation
- **"What should I work on?"** → Analyzes your patterns and suggests tasks

---

## 📋 Overview

CORTEX (formerly KDS - Key Data Streams) is a sophisticated AI assistant enhancement system designed to give GitHub Copilot long-term memory, context awareness, and strategic planning capabilities. It provides:

1. **4-Tier Brain Architecture** - Instinct, Working Memory, Knowledge Graph, Development Context
2. **10 Specialist Agents** - Intent routing, planning, execution, testing, validation, governance
3. **Dual-Hemisphere Processing** - LEFT BRAIN (tactical) + RIGHT BRAIN (strategic)
4. **Context Continuity** - "Make it purple" works across sessions (70-conversation FIFO capacity)
5. **Pattern Learning** - Accumulates wisdom from every interaction
6. **Quality Protection** - Challenges risky changes with evidence-based recommendations
7. **Real-Time Performance Analytics** - Track metrics, health scores, and trends across projects
8. **Community Feedback Loop** - Share insights via GitHub Gists, aggregate cross-project data

---

## 🏗️ How CORTEX Works

### Integration Model

CORTEX enhances GitHub Copilot through **AI-augmented instructions**, not traditional CLI dispatch. It works seamlessly through two interfaces:

**Primary Interface: GitHub Copilot Chat**
```
User: "plan authentication feature"
  ↓
Copilot reads .github/copilot-instructions.md
  ↓
Copilot follows structured CORTEX instructions
  ↓
User gets guided planning workflow with context
```

**Secondary Interface: Python CLI**
```bash
python -m src.main "plan authentication"
  ↓
CortexEntry.process() → IntentRouter → PlanningOrchestrator
  ↓
Generates plan with DoR/DoD validation
```

### Entry Point Architecture

```
User Command
  ↓
src/main.py (CLI entry)
  ↓
CortexEntry.process() (main dispatcher)
  ↓
IntentRouter.execute() (routing logic from cortex-operations.yaml)
  ↓
AgentExecutor.execute_routing_decision()
  ↓
[Orchestrators: Planning, TDD, System Maintenance, ADO, etc.]
  ↓
[Agents: Coding Agent, Planning Agent]
```

**Key Components:**

1. **CortexEntry** (`src/entry_point/cortex_entry.py`) - Main request processor and dispatcher
2. **IntentRouter** (`src/intent_router.py`) - Routes commands to appropriate orchestrators
3. **Operations Config** (`cortex-operations.yaml`) - Defines command→orchestrator mappings
4. **Orchestrators** (`src/orchestrators/`) - Implement complex multi-step workflows
5. **Agents** (`src/cortex_agents/`) - Execute specific tasks (coding, planning)

---

## 🗂️ Directory Structure

```
CORTEX/
├── README.md                           # This file - system overview
├── .github/
│   ├── copilot-instructions.md         # Auto-loaded baseline context
│   └── prompts/CORTEX.prompt.md        # 🎯 UNIVERSAL ENTRY POINT - Use /CORTEX
├── scripts/
│   ├── launchers/run-cortex.sh         # Quick launcher for CORTEX entry point
│   └── maintenance/                    # Maintenance utilities
├── cortex-brain/                       # The cognitive storage system
│   ├── tier0/                          # Instinct (immutable rules)
│   ├── tier1/                          # Working memory (last 20 conversations)
│   ├── tier2/                          # Knowledge graph (patterns learned)
│   └── tier3/                          # Development context (git, tests, metrics)
├── scripts/                            # Automation and maintenance scripts
├── cortex-design/                      # Implementation plans and architecture
└── docs/                               # Comprehensive documentation
│
├── docs/                               # 📚 ALL DOCUMENTATION
│   ├── architecture/                   # System design & patterns
│   │   ├── KDS-DESIGN-PLAN.md         # Complete design documentation
│   │   ├── KDS-V3-IMPLEMENTATION-PLAN.md # Detailed implementation plan
│   │   ├── system-overview.md
│   │   ├── prompt-architecture.md
│   │   └── workflow-diagrams.md
│   │
│   ├── database/                       # Database documentation
│   │   ├── schema-reference.md
│   │   ├── session-212-data.md        # Canonical test data
│   │   └── stored-procedures.md
│   │
│   ├── api/                            # API documentation
│   │   ├── endpoints-reference.md
│   │   ├── contracts.md
│   │   └── signalr-hubs.md
│   │
│   ├── testing/                        # Testing documentation
│   │   ├── playwright-guide.md
│   │   ├── test-patterns.md
│   │   └── orchestration-guide.md
│   │
│   └── guides/                         # User guides
│       ├── QUICK-REFERENCE.md         # Fast lookup reference
│       ├── PHASE-0-COMPLETE.md        # Phase 0 completion summary
│       ├── quick-start.md
│       ├── creating-prompts.md
│       ├── customizing-templates.md
│       └── troubleshooting.md
│
├── governance/                         # 🛡️ RULES & COMPLIANCE
│   ├── kds-rulebook.md                # 12 core rules (CANONICAL)
│   ├── prompt-standards.md            # Prompt development standards
│   └── validation-requirements.md     # Schema validation rules
│
├── prompts/                            # 🤖 AGENT PROMPTS (6 total)
│   ├── route.prompt.md                # Entry point - intent detection
│   ├── plan.prompt.md                 # Planning orchestrator
│   ├── execute.prompt.md              # Execution engine
│   ├── test.prompt.md                 # Test generation & orchestration
│   ├── validate.prompt.md             # Health checks & validation
│   ├── govern.prompt.md               # Governance gatekeeper
│   │
│   └── core/                           # Shared prompt modules
│       ├── validation.md              # Shared validation logic
│       ├── handoff.md                 # Handoff workflow
│       ├── test-first.md              # TDD workflow
│       └── output-formatter.md        # Template rendering
│
├── schemas/                            # 📐 JSON/XML SCHEMAS
│   ├── handoffs/                       # Handoff JSON schemas
│   │   ├── handoff-schema.json        # Main handoff schema
│   │   ├── plan-handoff.json
│   │   ├── execute-handoff.json
│   │   └── test-handoff.json
│   │
│   └── outputs/                        # Output XML schemas
│       ├── plan-output.xsd
│       ├── task-output.xsd
│       ├── test-output.xsd
│       └── validation-result.xsd
│
├── templates/                          # 📝 MUSTACHE TEMPLATES
│   ├── user-output/                    # User-facing responses
│   │   ├── plan-complete.mustache
│   │   ├── phase-complete.mustache
│   │   ├── task-complete.mustache
│   │   ├── test-ready.mustache
│   │   ├── validation-report.mustache
│   │   └── error.mustache
│   │
│   └── handoffs/                       # Handoff JSON templates
│       ├── plan-to-execute.json
│       ├── execute-to-test.json
│       └── test-to-validate.json
│
├── services/                           # 🔧 C# SERVICES
│   ├── TemplateEngine.cs              # Mustache rendering service
│   ├── SchemaValidator.cs             # JSON/XML validation service
│   ├── PromptMonitoringService.cs     # Performance tracking
│   └── PromptCacheService.cs          # Response caching
│
├── keys/                               # 🗄️ WORK STREAM DATA
│   └── {key-name}/                     # Per-key workspace
│       ├── plan.md                     # Current plan
│       ├── work-log.md                 # Activity log (append-only)
│       └── handoffs/                   # Active handoff JSONs
│           ├── phase-1-task-1.json
│           └── phase-1-task-2.json
│
├── tests/                              # 🧪 PROMPT TESTS
│   ├── patterns/                       # Reusable test patterns
│   │   ├── auth-pattern.json
│   │   ├── crud-pattern.json
│   │   └── ui-pattern.json
│   │
│   ├── specs/                          # Test specifications
│   │   ├── schema-validation.spec.ts
│   │   ├── template-rendering.spec.ts
│   │   ├── performance.spec.ts
│   │   └── integration.spec.ts
│   │
│   ├── promptfoo-config.yaml          # Prompt testing config
│   └── index.json                      # Global test registry
│
├── scripts/                            # 🔨 UTILITY SCRIPTS
│   ├── migrate-to-v3.ps1              # Migration script
│   ├── validate-prompts.ps1           # Prompt validation
│   └── rebuild-test-index.ps1         # Test registry rebuild
│
└── hooks/                              # 🪝 GIT HOOKS
    ├── pre-commit                      # Validation before commit
    └── post-test-creation.ps1         # After test generation
```

---

## 🚀 Quick Start

### 1. Create New Feature

```bash
@workspace /route request="Add user dashboard with authentication"
```

**System will:**
- Detect multi-task request
- Route to `plan.prompt.md`
- Generate phases/tasks
- Create handoff JSONs
- Output next command

### 2. Execute Plan

```bash
@workspace /execute #file:KDS/keys/user-dashboard/handoffs/phase-1-task-1.json
```

**System will:**
- Load handoff JSON
- Validate against schema
- Implement code changes
- Run build + tests
- Update work-log.md
- Auto-chain to next task (if enabled)

### 3. Run Tests

```bash
@workspace /test key=user-dashboard task=1a
```

**System will:**
- Check test registry for patterns
- Generate Playwright test
- Create orchestration script
- Run test
- Update registry if passed

---

## 📚 Documentation

### Core Documentation (Read First)

1. **[Quick Start Guide](docs/guides/quick-start.md)** - Get started in 5 minutes
2. **[KDS Design Plan](docs/architecture/KDS-DESIGN-PLAN.md)** - Complete system design
3. **[KDS Rulebook](governance/kds-rulebook.md)** - 13 core governance rules
4. **[Quick Reference](docs/guides/QUICK-REFERENCE.md)** - Fast lookup for common operations

### By Topic

**Architecture & Design:**
- [KDS Design Plan](docs/architecture/KDS-DESIGN-PLAN.md) - Complete v3.0 design
- [KDS Implementation Plan](docs/architecture/KDS-V3-IMPLEMENTATION-PLAN.md) - Detailed implementation
- [System Overview](docs/architecture/system-overview.md)
- [Prompt Architecture](docs/architecture/prompt-architecture.md)
- [Workflow Diagrams](docs/architecture/workflow-diagrams.md)

**Database:**
- [Schema Reference](docs/database/schema-reference.md)
- [Session 212 Data](docs/database/session-212-data.md) - Canonical test data
- [Stored Procedures](docs/database/stored-procedures.md)

**API:**
- [Endpoints Reference](docs/api/endpoints-reference.md)
- [Contracts](docs/api/contracts.md)
- [SignalR Hubs](docs/api/signalr-hubs.md)

**Testing:**
- [Playwright Guide](docs/testing/playwright-guide.md)
- [Test Patterns](docs/testing/test-patterns.md)
- [Orchestration Guide](docs/testing/orchestration-guide.md)

**Guides:**
- [Quick Reference](docs/guides/QUICK-REFERENCE.md) - Fast lookup
- [Phase 0 Complete](docs/guides/PHASE-0-COMPLETE.md) - Infrastructure setup summary
- [Quick Start](docs/guides/quick-start.md)
- [Creating Prompts](docs/guides/creating-prompts.md)
- [Customizing Templates](docs/guides/customizing-templates.md)
- [Troubleshooting](docs/guides/troubleshooting.md)

---

## 🎯 Health Dashboard

### Quick Access

**🚀 ONE COMMAND (Recommended):**
```bash
# All-in-one: Start API server + Open dashboard
Ctrl+Shift+P → Tasks: Run Task → "kds: launch dashboard (all-in-one)"
```

**Alternative Methods:**
```bash
# Method 1: PowerShell (all-in-one)
.\KDS\scripts\launch-dashboard.ps1

# Method 2: Separate control
Ctrl+Shift+P → "kds: start api server"  # Terminal 1
Ctrl+Shift+P → "kds: health dashboard"  # Browser opens

# Method 3: Dashboard only (demo mode)
Double-click: KDS\kds-dashboard.html
```

**Features:**
- 📊 **Overview Tab** - System status at a glance
- ❤️ **Health Checks** - 7 categories, 39+ checks (expandable drill-down)
- 🧠 **BRAIN Metrics** - Event stream, knowledge graph stats
- 📝 **Activity Log** - Recent system events
- 🔄 **Auto-Refresh** - Configurable interval (30s default)
- 📤 **Export Reports** - JSON format for analysis
- 🔗 **Live Mode** - Real health checks via API server
- 🎮 **Demo Mode** - Simulated checks (fallback)

**Architecture:**
- ✅ Single HTML file (~60KB)
- ✅ Zero external dependencies
- ✅ Beautiful dark theme
- ✅ Real-time status animations
- ✅ 100% portable

See [Dashboard Documentation](dashboard/README.md) for full details.

---

## 🛠️ Configuration

### Customize User Output Templates

All user-facing responses use Mustache templates. Edit without touching prompts:

```bash
# Edit template
code KDS/templates/user-output/plan-complete.mustache

# Changes apply immediately (no prompt modifications needed)
```

**Template Variables:**
- `{{key}}` - KDS key identifier
- `{{phases}}` - Array of phase objects
- `{{tasks}}` - Array of task objects
- `{{timestamp}}` - ISO 8601 timestamp
- `{{nextCommand}}` - Next invocation command

### Adjust Performance Settings

```json
// appsettings.json
{
  "KDS": {
    "CacheDurationMinutes": 30,
    "MaxTokensPerPrompt": 4000,
    "EnablePerformanceMonitoring": true,
    "TemplateEngine": "Mustache"
  }
}
```

---

## 🧪 Testing

### Run All Tests

```bash
# Test all prompts (regression testing)
npm run test:prompts

# Test JSON/XML schemas
npm run test:schemas

# Test template rendering
npm run test:templates

# Performance benchmarks
npm run test:performance

# Full test suite
npm run test:all
```

### Validate Prompts

```bash
# Lint all prompts
npm run lint:prompts

# Validate handoff JSONs
npm run validate:handoffs

# Check for hardcoded strings
npm run check:templates
```

---

## 📐 Schemas

### Handoff JSON Schema

All handoff files validated against `KDS/schemas/handoffs/handoff-schema.json`:

```json
{
  "key": "string (required)",
  "action": "plan | execute | test | validate | govern",
  "phase": "integer (optional)",
  "task": "string (optional, format: '1a')",
  "data": {
    "description": "string (required)",
    "files": ["array of file paths"],
    "tests": ["array of test paths"],
    "acceptance": ["array of criteria (required)"],
    "next": "string (next handoff file or 'complete')"
  }
}
```

### Output XML Schemas

All prompt outputs validated against XML schemas in `KDS/schemas/outputs/`:

- `plan-output.xsd` - Plan generation output
- `task-output.xsd` - Task execution output
- `test-output.xsd` - Test generation output
- `validation-result.xsd` - Validation reports

---

## 🏗️ Architecture

### 6 Specialized Prompts

| Prompt | Responsibility | Input | Output |
|--------|---------------|-------|--------|
| **route.prompt.md** | Intent detection & routing | User request | Routing decision + handoff |
| **plan.prompt.md** | Phase/task breakdown | Feature request | Plan + handoff JSONs |
| **execute.prompt.md** | Code implementation | Handoff JSON | Updated files + validation |
| **test.prompt.md** | Test generation/execution | Test request | Playwright test + report |
| **validate.prompt.md** | System health checks | Validation request | Health report |
| **govern.prompt.md** | Governance compliance | KDS change | Approval/rejection |

### Core Modules (Zero Duplication)

Shared logic extracted to `/prompts/core/`:

- `validation.md` - Pre/post-execution validation
- `handoff.md` - Handoff workflow patterns
- `test-first.md` - TDD workflow
- `output-formatter.md` - Template rendering

**Usage in prompts:**
```markdown
## Step 3: Validate Environment

<!-- INCLUDE: core/validation.md#Pre-Execution-Validation -->
```

---

## 📊 Performance Monitoring

### Tracked Metrics

- **Execution Time** - Milliseconds per prompt
- **Token Usage** - Estimated tokens consumed
- **Memory Usage** - Memory delta during execution
- **Cache Hit Rate** - Percentage of cached responses
- **Schema Validation** - Success/failure rate

### View Metrics

```bash
# View performance logs
cat SPA/NoorCanvas/logs/prompt-metrics.log

# Generate performance report
dotnet run --project Tools/PromptMetrics -- report --last 7d
```

---

## 🔄 Version History

| Version | Date | Changes |
|---------|------|---------|
| **3.0.0** | 2025-11-02 | Complete redesign - 6 prompts, template-driven, schema validation |
| **2.1.0** | 2025-11-01 | Added Rule #20 (KDTR), test registry system |
| **2.0.0** | 2025-10-31 | Major governance overhaul, centralized Step -1 |
| **1.0.0** | 2025-09-01 | Initial KDS system release |

---

## ⚠️ Known Limitations

1. **GitHub Copilot Integration**: Primary interface is GitHub Copilot Chat, which requires a GitHub Copilot license ($10-$20/month)
2. **Test Collection**: Some legacy test files are scripts rather than proper pytest tests - being migrated to pytest format
3. **Integration Tests**: End-to-end workflow tests are being expanded (planning E2E, TDD E2E, brain persistence tests in progress)
4. **Orchestrator Cleanup**: Some duplicate orchestrators exist from iterative development - consolidation planned
5. **Python 3.8+**: Requires Python 3.8 or higher for async features and type annotations
6. **Windows Primary**: Developed and tested primarily on Windows with PowerShell; Linux/Mac support available but less tested

**Roadmap:**
- ✅ Phase 1: Fix test collection (v5.2.1)
- 🚧 Phase 2: Complete E2E integration tests (v5.3.0)
- 📋 Phase 3: Orchestrator consolidation (v5.4.0)
- 📋 Phase 4: Cross-platform testing expansion (v5.5.0)

---

## 🆘 Support

### Common Issues

**Build Errors:**
- See [Troubleshooting Guide](docs/guides/troubleshooting.md#build-errors)

**Schema Validation Failures:**
- Check [Validation Requirements](governance/validation-requirements.md)

**Template Rendering Issues:**
- Review [Customizing Templates](docs/guides/customizing-templates.md)

### Getting Help

1. Check [Quick Start Guide](docs/guides/quick-start.md)
2. Review [Troubleshooting Guide](docs/guides/troubleshooting.md)
3. Search [KDS Rulebook](governance/kds-rulebook.md)
4. Check existing work logs in `KDS/keys/{key}/work-log.md`

---

## 📝 File Naming Conventions

### Prompts
- Format: `{name}.prompt.md`
- Examples: `route.prompt.md`, `plan.prompt.md`

### Schemas
- JSON: `{type}-schema.json`
- XML: `{type}-output.xsd`
- Examples: `handoff-schema.json`, `plan-output.xsd`

### Templates
- Format: `{name}.mustache`
- Examples: `plan-complete.mustache`, `task-complete.mustache`

### Documentation
- Format: `{topic}-{type}.md`
- Examples: `system-overview.md`, `quick-start.md`

### Keys
- Format: `{feature-name}` (lowercase, hyphen-separated)
- Examples: `user-dashboard`, `auth-flow`, `debug-panel`

### Handoffs
- Format: `phase-{N}-task-{M}.json`
- Examples: `phase-1-task-1.json`, `phase-2-task-3.json`

---

## 🎯 Implementation Status

### Phase 0: Infrastructure ✅ COMPLETE
- [x] Clean directory structure created
- [x] README documentation
- [x] Folder hierarchy established
- [x] Naming conventions defined

### Phase 1: Schemas & Templates ⏳ PENDING
- [ ] Create JSON schemas (4 files)
- [ ] Create XML schemas (3 files)
- [ ] Create Mustache templates (6 files)
- [ ] Create validation services

### Phase 2: Core Modules ⏳ PENDING
- [ ] Create validation.md
- [ ] Create handoff.md
- [ ] Create test-first.md
- [ ] Create output-formatter.md

### Phase 3: Governance ⏳ PENDING
- [ ] Create kds-rulebook.md (12 rules)
- [ ] Create prompt-standards.md
- [ ] Create validation-requirements.md

### Phase 4: Prompts ⏳ PENDING
- [ ] Create route.prompt.md
- [ ] Create plan.prompt.md
- [ ] Create execute.prompt.md
- [ ] Create test.prompt.md
- [ ] Create validate.prompt.md
- [ ] Create govern.prompt.md

### Phase 5: Testing ⏳ PENDING
- [ ] Create promptfoo tests
- [ ] Create schema tests
- [ ] Create template tests
- [ ] Create performance tests

### Phase 6: Documentation ⏳ PENDING
- [ ] Create all architecture docs
- [ ] Create all database docs
- [ ] Create all API docs
- [ ] Create all testing docs
- [ ] Create all guides

---

**System Status:** Infrastructure Ready - Awaiting Phase 1 Implementation  
**Next Command:** Begin Phase 1 (Schemas & Templates)  
**Estimated Completion:** 6.5 hours total
