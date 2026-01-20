# CORTEX Documentation Restructuring Prompt

## Executive Summary

Transform the CORTEX repository from scattered documentation across root and nested folders into a centralized, production-grade documentation suite in `docs/` reflecting live capabilities: an intelligent orchestration platform with multi-tier architecture, REST/MCP/CLI APIs, governance framework, and resilience patterns.

**Key Enhancement:** Phase 0 (File Discovery) recursively traverses root directory and all folders to identify scattered .md/.txt files, consolidate them into `docs/`, and apply blacklist protection to critical system files.

---

## Phase 0: File Discovery & Consolidation (NEW - PREREQUISITE)

### 0.1 Root Directory Scan

**Starting Point:** Scan `/Users/asifhussain/PROJECTS/CORTEX/` root for documentation files

```
Files to discover:
├── *.md files
├── *.txt files  
├── *.yaml files (non-system)
└── *.json files (non-system)
```

**Action:** Create inventory of all files found

### 0.2 Recursive Folder Traversal

**Pattern:** Recursively scan all subdirectories for scattered documentation

```
Traverse:
├── _workspaces/
│   ├── cortex-vision/
│   ├── roadmap/
│   └── sts/
├── cortex/
│   ├── api/
│   ├── brain/
│   ├── core/
│   ├── infrastructure/
│   ├── mcp/
│   ├── orchestrators/
│   ├── scripts/
│   ├── tests/
│   └── tools/
├── cortex_brain/
│   ├── releases/
│   ├── state/
│   ├── tier0/
│   ├── tier1/
│   └── tier2/
├── cortex_toolkit/
│   └── core/
├── .github/
│   ├── agents/      ← Already has docs
│   ├── prompts/     ← Already has prompts
│   └── workflows/
├── extensions/
├── mcp-config/
├── phases/
├── scripts/
├── src/
└── tests/
```

**File Types to Identify:**
- Documentation: `.md`, `.txt`, `.rst`
- Configuration: `.yaml`, `.yml`, `.json` (non-system)
- README files (anywhere)
- CHANGELOG/HISTORY files
- CONTRIBUTING guidelines
- Design documents
- Analysis reports

### 0.3 Blacklist Protection (CRITICAL)

**Protected Files & Folders** - DO NOT MOVE:

```yaml
protected_patterns:
  # Root critical files
  - requirements.txt
  - pytest.ini
  - setup.py
  - pyproject.toml
  - cortex-config.yaml
  - governance.db
  - README.md  # Root project README
  - LICENSE.md
  
  # .github critical files
  - .github/workflows/**/*
  - .github/prompts/*.prompt.md
  - .github/prompts/*.md
  - .github/agents/*
  
  # Source code files (never move)
  - cortex/**/*.py
  - cortex_brain/**/*.py
  - cortex_toolkit/**/*.py
  - src/**/*.py
  
  # System files
  - .git/**
  - .venv/**
  - __pycache__/**
  - *.egg-info/**
  - .pytest_cache/**
  - .DS_Store
  
  # Build/Package files
  - dist/**
  - build/**
  - .tox/**
```

**Special Handling:**

| File | Action | Reason |
|------|--------|--------|
| `requirements.txt` | PROTECT | System dependency file, critical |
| `.github/prompts/*.prompt.md` | PROTECT | Agent prompt definitions |
| `.github/agents/*.md` | PROTECT | Agent system documentation |
| `cortex-config.yaml` | PROTECT | Live configuration, critical |
| `governance.db` | PROTECT | Live database, critical |
| Python source files | PROTECT | Never move code |
| Root `README.md` | PROTECT | Project overview, stays at root |

### 0.4 File Categorization During Traversal

As files are discovered, classify immediately into these categories:

**Classification Categories:**

1. **Root-level documentation** (Candidate for docs/)
   - Pattern: `*.md` files in root
   - Examples: INSTALLATION.md, CONTRIBUTING.md, ARCHITECTURE.md
   - Action: Review for consolidation into docs/07-contributing/ or appropriate section

2. **Scattered subdirectory documentation** (Candidate for docs/)
   - Pattern: `README.md` in subdirectories
   - Examples: cortex/README.md, scripts/README.md, extensions/README.md
   - Action: Review for consolidation by topic into docs/reference/

3. **Phase/workspace documentation** (Candidate for docs/_archive/)
   - Pattern: `*.md` in _workspaces/
   - Examples: _workspaces/roadmap/*.md, _workspaces/sts/*.md
   - Action: Evaluate for archival in docs/_archive/workspaces/

4. **Analysis/reports** (Candidate for docs/_archive/)
   - Pattern: Analysis, findings, reports
   - Examples: *-analysis.md, *-findings.md, *-report.md
   - Action: Evaluate for archival in docs/_archive/analysis/ or docs/_archive/reports/

5. **Configuration examples** (Candidate for docs/)
   - Pattern: Config files (.yaml, .json examples)
   - Examples: config-example.yaml, settings.json
   - Action: Review for consolidation into docs/04-guides/deployment/ or docs/reference/ (rename to *-example.*)

6. **Protected files** (DO NOT MOVE)
   - Pattern: Files matching blacklist patterns (see 0.3)
   - Action: Skip and note as protected

---

## Phase 0 Execution (AUTONOMOUS)

This phase is now executed autonomously by the doc-restructuring agent without user input.

### Autonomous Execution

The agent performs all discovery automatically:

```python
# Phase 0 Implementation
orchestrator = AutonomousOrchestrator(root_path)

# Phase 0: Scan
discovered = scanner.scan()  # Root + recursive scan, blacklist filtering
# Outputs: 1) File list with paths and categories
#          2) scan-results.json

# Phase 1: Analyze  
analyzer.analyze()  # Auto-categorization based on rules
# Outputs: analysis-results.json with categories, actions, target dirs

# Phase 2: Execute (NO USER INPUT NEEDED)
orchestrator._execute_restructuring(discovered)  # Move/archive files
# Outputs: Moved files to correct locations

# Phase 3: Report
orchestrator._generate_report()  # Comprehensive report
# Outputs: doc-restructuring-report.json + git commit
```

**No chat interaction required** - all decisions are data-driven based on rules defined in ProtectionFilter, DocumentationScanner, and FileCategory enum.

### Execution Triggers

The agent runs autonomously via:

1. **Scheduled**: Weekly Sunday 2 AM UTC (configurable)
2. **Event-based**: Detects new .md files outside docs/ folder
3. **Manual**: `python .github/agents/doc-restructuring-agent.py --run-now`
4. **CI/CD**: Integrated into GitHub Actions workflow

### Monitoring

Review execution automatically:

```bash
# View log
tail -f .github/agents/doc-restructuring.log

# View report
cat .github/agents/doc-restructuring-report.json | jq

# Check git commits
git log --oneline | head -5
```

---

## Intent Reflection & Autonomous Implementation Plan

### Execution Model: Autonomous (No User Interaction at Each Step)

**CHANGED FROM**: Interactive workflow requiring user confirmation at Phases 2-5  
**CHANGED TO**: Fully autonomous execution with predefined categorization rules

The documentation restructuring now runs as a **background agent** without waiting for user input:

1. **Autonomous Discovery** → Agent scans entire repository automatically
2. **Autonomous Categorization** → Files categorized by rules (location, name patterns)
3. **Autonomous Execution** → Files moved/archived per categorization (NO APPROVAL GATE)
4. **Autonomous Reporting** → Results logged and committed to git

### Current State Analysis (Same as Before)

| Dimension | Current Status | Issues |
|-----------|---|---|
| **File Count** | 180+ files | Unmanageable volume |
| **File Types** | Mixed reports, sessions, analysis, code docs | No clear purpose categorization |
| **Naming Convention** | Date-stamped, phase-based, chat logs | Non-production (e.g., `SESSION-SUMMARY-20260118.md`) |
| **Organization** | Flat structure with minimal hierarchy | Difficult navigation, unclear relationships |
| **Content Quality** | Mix of working notes, duplicate findings, completed reports | Obsolete content mixed with current documentation |
| **Audience** | Unclear (developers? operators? architects?) | No documentation strategy |

### Live Application Capabilities (Same as Before)

| Component | Capability | Documentation Need |
|-----------|---|---|
| **Core Architecture** | Governance layer, multi-tier execution engine, state management | Architecture fundamentals, design patterns |
| **Orchestration** | Business process automation, task coordination, domain-specific orchestrators | Orchestrator registry, capability matrix, lifecycle |
| **APIs** | REST endpoints, MCP protocol, CLI interface, configuration | API reference, integration guides, examples |
| **Resilience** | Circuit breakers, partial functionality mode, graceful degradation, rollback | Resilience strategies, failure scenarios, recovery |
| **Security** | GDPR/HIPAA/SOC2 compliance, encryption, audit trails | Governance framework, compliance mapping, audit procedures |
| **Domain Brain** | Business knowledge ingestion, document parsing, conflict resolution | BKIO patterns, knowledge management, integration |
| **Deployment** | Multi-environment support, feature flags, metrics collection | Deployment guides, environment setup, monitoring |

### Restructuring Strategy: Autonomous + Rules-Based

**Goal**: Create a hierarchical, audience-segmented documentation suite that updates automatically when new files are detected.

**Key Difference From Before**:
- Old: User reviews findings, confirms decisions, approves file movements
- New: Agent categorizes files automatically per predefined rules, executes immediately, no approval gate

---

## Phase 1-2: Autonomous Analysis & Categorization

**AUTOMATED** - No user interaction required. Agent performs all analysis automatically.

### 1.1 File Categorization (Automatic)

The agent automatically classifies files into these categories based on location and naming patterns:

| Category | Auto-Detection Logic | Action |
|----------|-----|--------|
| **ROOT_DOCS** | `*.md` in root dir OR named `README.md`, `CHANGELOG.md`, `CONTRIBUTING.md` | Review/Move to docs/02-architecture |
| **SUBDIRECTORY_DOCS** | Named `README.md` in any subdirectory (except `.git`, `__pycache__`, etc.) | Move to docs/05-reference |
| **PHASE_DOCS** | Located in `_workspaces/*/` OR `phases/*/` | Archive to docs/_archive/workspaces |
| **ANALYSIS_REPORTS** | Contains keywords: analysis, report, findings, summary in path or name | Archive to docs/_archive/reports |
| **CONFIG_EXAMPLES** | `.yaml`, `.yml`, `.json` files with "example" in name | Move to docs/04-guides |
| **PROTECTED** | Matches blacklist patterns (`.github/workflows/**`, `src/**/*.py`, `requirements.txt`, etc.) | Skip - never moved |

**No user decisions needed** - categorization is 100% rules-based.

### 1.2 Action Assignment (Automatic)

Based on category, agent automatically assigns action:

| Category | Auto-Assigned Action | Target Directory |
|----------|-----|--------|
| ROOT_DOCS | move | docs/02-architecture |
| SUBDIRECTORY_DOCS | move | docs/05-reference |
| PHASE_DOCS | archive | docs/_archive/workspaces |
| ANALYSIS_REPORTS | archive | docs/_archive/reports |
| CONFIG_EXAMPLES | move | docs/04-guides |
| PROTECTED | protect | (none - preserved) |

**No approval gate** - actions execute immediately after categorization.

### 1.3 Execution (Automatic)

The agent executes all actions autonomously:

```python
# Pseudo-code showing autonomous flow
for file in discovered_files:
    category = auto_categorize(file)  # Automatic - no user input
    action = get_action(category)      # Automatic - predefined
    target = get_target_dir(category)  # Automatic - predetermined
    
    if action == 'move':
        move_file(file, target)        # Execute immediately
    elif action == 'archive':
        archive_file(file, target)     # Execute immediately
    elif action == 'protect':
        skip_file(file)                # Leave in place
```

**All execution is fully automated** - no user confirmation needed between steps.

---

## Phase 3: Production Documentation Structure

**Input:** Consolidation decisions from Phase 2 (discussed in chat)  
**Purpose:** Define target directory hierarchy per industry best practices  
**Output:** Folder structure plan & file placement strategy (discussed in chat, reviewed before execution)

### 3.1 Folder Hierarchy (Industry Best Practices)

```
docs/
├── 0-README.md                           # Main entry point
├── 01-getting-started/                   # Onboarding path
│   ├── 0-installation.md                 # Prerequisites, environment setup
│   ├── 1-quickstart.md                   # 15-min hands-on tutorial
│   ├── 2-first-orchestrator.md           # Create first orchestrator
│   └── 3-troubleshooting.md              # Common setup issues
│
├── 02-architecture/                      # Design foundation
│   ├── 0-overview.md                     # System architecture, components
│   ├── 1-design-principles.md            # CORTEX design philosophy
│   ├── 2-multi-tier-architecture.md      # Tier 0-3 governance & execution
│   ├── 3-orchestration-engine.md         # Core orchestration lifecycle
│   ├── 4-orchestrator-registry.md        # Orchestrator discovery & lifecycle
│   ├── 5-resilience-patterns.md          # Failure handling, circuit breakers
│   ├── 6-security-governance.md          # Audit, compliance, encryption
│   ├── 7-domain-brain.md                 # Knowledge ingestion & management
│   ├── 8-state-management.md             # State persistence & recovery
│   └── adrs/                             # Architecture Decision Records
│       ├── adr-001-orchestration-pattern.md
│       ├── adr-002-tier-architecture.md
│       └── ...
│
├── 03-api-reference/                     # Complete API documentation
│   ├── 0-overview.md                     # API philosophy, authentication
│   ├── rest-api/
│   │   ├── 0-guide.md                    # REST endpoint structure
│   │   ├── orchestrators.md              # Orchestrator endpoints
│   │   ├── domains.md                    # Domain endpoints
│   │   ├── configuration.md              # Configuration endpoints
│   │   └── governance.md                 # Audit & governance endpoints
│   ├── mcp-protocol/
│   │   ├── 0-specification.md            # MCP protocol details
│   │   ├── tools.md                      # Available MCP tools
│   │   └── capabilities.md               # Tool capabilities
│   ├── cli/
│   │   ├── 0-guide.md                    # CLI command reference
│   │   ├── orchestrator-commands.md      # Orchestrator CLI
│   │   ├── configuration-commands.md     # Configuration CLI
│   │   └── governance-commands.md        # Governance CLI
│   └── schemas/
│       ├── orchestration-context.md      # Context schema
│       ├── configuration.md              # Configuration schema
│       └── audit-record.md               # Audit record schema
│
├── 04-guides/                            # How-to documentation
│   ├── 0-index.md                        # Guide catalog
│   ├── integration/
│   │   ├── 0-overview.md                 # Integration patterns
│   │   ├── 1-developing-custom-orchestrators.md
│   │   ├── 2-integrating-with-apis.md
│   │   ├── 3-domain-knowledge-integration.md
│   │   ├── 4-monitoring-observability.md
│   │   └── 5-compliance-audit.md
│   ├── deployment/
│   │   ├── 0-overview.md                 # Deployment philosophy
│   │   ├── 1-local-development.md        # Local setup
│   │   ├── 2-staging-deployment.md       # Staging environment
│   │   ├── 3-production-deployment.md    # Production setup
│   │   ├── 4-azure-deployment.md         # Azure specific
│   │   ├── 5-configuration-management.md # Environment variables, secrets
│   │   ├── 6-feature-flags.md            # Feature management
│   │   └── 7-blue-green-deployment.md    # Zero-downtime deployment
│   ├── operations/
│   │   ├── 0-overview.md                 # Operations framework
│   │   ├── 1-monitoring.md               # Application Insights setup
│   │   ├── 2-alerting.md                 # Alert configuration
│   │   ├── 3-logging.md                  # Log aggregation & analysis
│   │   ├── 4-troubleshooting.md          # Common issues & resolution
│   │   ├── 5-performance-tuning.md       # Optimization strategies
│   │   ├── 6-disaster-recovery.md        # Backup & recovery
│   │   └── 7-audit-compliance.md         # Audit procedures
│   └── advanced/
│       ├── 0-overview.md
│       ├── 1-resilience-configuration.md
│       ├── 2-custom-conflict-resolution.md
│       ├── 3-knowledge-graph-optimization.md
│       └── 4-multi-tenant-setup.md
│
├── 05-reference/                         # Lookup & reference
│   ├── glossary.md                       # Term definitions
│   ├── faq.md                            # Frequently asked questions
│   ├── known-issues.md                   # Known issues & workarounds
│   ├── changelog.md                      # Version history
│   ├── migration-guides/
│   │   ├── v0-to-v1.md
│   │   └── legacy-integration.md
│   ├── compliance-mappings.md            # Regulatory compliance (GDPR/HIPAA/SOC2)
│   └── performance-baselines.md          # Benchmark data
│
├── 06-tutorials/                         # Hands-on learning
│   ├── 0-index.md                        # Tutorial catalog
│   ├── orchestrator-tutorials/
│   │   ├── 1-hello-world.md              # Basic orchestrator
│   │   ├── 2-multi-step-workflow.md      # Sequential orchestration
│   │   ├── 3-error-handling.md           # Resilience patterns
│   │   ├── 4-knowledge-integration.md    # Domain brain usage
│   │   └── 5-complex-domain.md           # Advanced patterns
│   ├── api-integration/
│   │   ├── 1-rest-client.md
│   │   ├── 2-mcp-integration.md
│   │   └── 3-batch-operations.md
│   └── operations/
│       ├── 1-local-setup.md
│       ├── 2-monitoring-dashboard.md
│       ├── 3-incident-response.md
│       └── 4-performance-analysis.md
│
├── 07-contributing/                      # Developer guide
│   ├── 0-code-of-conduct.md
│   ├── 1-contributing-guidelines.md
│   ├── 2-development-setup.md
│   ├── 3-testing-strategy.md
│   ├── 4-documentation-style.md
│   ├── 5-pull-request-process.md
│   └── 6-release-process.md
│
├── _archive/                             # Historical & working docs
│   ├── sessions/                         # Session logs
│   ├── phases/                           # Phase completion reports
│   ├── analysis/                         # Analysis & investigation docs
│   ├── implementation-plans/             # Superseded plans
│   └── reviews/                          # Review artifacts
│
└── _media/                               # Diagrams, images
    ├── architecture/
    ├── workflows/
    └── screenshots/

```

### 3.2 File Naming Convention (Production Standard)

| Purpose | Format | Example |
|---------|--------|---------|
| Main pages | `0-name.md` | `0-overview.md`, `0-getting-started.md` |
| Sequential docs | `N-name.md` | `1-installation.md`, `2-quickstart.md` |
| Reference | `name.md` | `glossary.md`, `faq.md`, `changelog.md` |
| Sub-sections | No prefix | `orchestrators.md`, `domains.md` |
| Architecture decisions | `adr-NNN-title.md` | `adr-001-orchestration-pattern.md` |
| Tutorials | `N-title.md` | `1-hello-world.md`, `3-error-handling.md` |
| Archive items | Original names | Preserved for reference |

**Rationale**: Numeric prefixes enable natural sorting and clear sequential relationships without dates.

---

## Phase 4: Content Consolidation & Formatting (In-Chat Planning)

**Input:** Files identified for consolidation from Phase 2 (discussed in chat)  
**Purpose:** Plan content consolidation, identify redundancy, design consistent formatting  
**Output:** Consolidation strategy (discussed in chat, confirmed before implementation)

### 4.1 Consolidation Mapping Discussion

During chat, analyze and map these consolidation opportunities:

| Source Files | Consolidated Document | Rationale |
|---|---|---|
| `README.md`, `00-README-START-HERE-*.md`, `INDEX.md` | `0-README.md` + navigation structure | Single entry point |
| `ARCHITECTURE-MAP.md`, `cortex-impl-map-overview.md`, `CORTEX-TECHNICAL-VERIFICATION-*.md` | `02-architecture/0-overview.md` | Unified architecture view |
| `DEPLOYMENT-*.md` (multiple) + `DEPLOYMENT-SETUP-GUIDE.md` | `04-guides/deployment/*` (split by environment) | Environment-specific deployment |
| `DEPLOYMENT-API-REFERENCE.md` + `DEPLOYMENT-TROUBLESHOOTING.md` | `04-guides/integration/2-integrating-with-apis.md` | API integration patterns |
| `PHASE-21-*.md`, `PHASE-24-*.md` (20+ files) | `02-architecture/7-state-management.md` + `04-guides/advanced/*` | Extract technical content |
| `AC-*-SPECIFICATION.md`, `AC-*-IMPLEMENTATION-PLAN.yaml` | `03-api-reference/*` + `04-guides/integration/*` | Distribute by topic |
| `*-QUICKSTART.md`, `PHASE-*-QUICK-*` | `04-guides/` + `06-tutorials/` | Quick-start examples |
| `*FINDINGS-*.md`, `*-GAP-*.md`, `*-ANALYSIS*.md` | Summarize → `02-architecture/` + archive originals | Extract insights, archive working docs |
| `COMPLIANCE-*.md`, `GOVERNANCE-*.md` (if any) | `04-guides/operations/7-audit-compliance.md` | Compliance documentation |
| `INTEGRATION-TEST-*.md`, `*-VERIFICATION-*.md` | `04-guides/operations/2-monitoring.md` + archive | Monitoring setup |

**Chat Task:** Review each mapping and discuss which source files contain critical content to preserve.

### 4.2 Content Consolidation Format Strategy

During chat, discuss these formatting standards for consolidated documents:

**Standardized Structure for Each Document**:

- **Overview**: 1-2 sentence summary, audience level, prerequisites/dependencies
- **Key Concepts**: Bulleted technical foundation (no code snippets, high-level)
- **Architecture/Design**: Comparison tables, decision rationale, trade-offs
- **Implementation Details**: Numbered steps, configuration examples in tables, integration patterns
- **Related Documentation**: Internal links to related docs, dependencies, next steps
- **Troubleshooting**: Common issues in Q&A format, resolution steps, escalation guidance

**Chat Task:** Confirm this structure works for all major document types.

### 4.3 Consistency Standards

Reference these standards during chat discussions about document formatting:

| Aspect | Standard |
|--------|----------|
| **Headings** | H1 for title, H2 for sections, H3 for subsections (max 3 levels) |
| **Lists** | Bulleted for unordered, numbered for sequential steps |
| **Tables** | Use for comparisons, matrices, reference data |
| **Terminology** | Define on first use, reference glossary.md for all terms |
| **Links** | Relative paths: `../02-architecture/0-overview.md` |
| **Code** | YAML/JSON configurations in fenced blocks, conceptual pseudocode only |
| **Examples** | Link to working examples in source code, not inline |
| **Audience** | Explicit callouts: `For Architects:`, `For Operators:` |
| **Versioning** | Document version alongside CORTEX version (e.g., v1.0.0) |
| **Update Frequency** | Last updated date in frontmatter |

**Chat Task:** Confirm these standards or propose modifications.

---

## Phase 5: Production-Ready File Planning & Finalization Strategy

**Input:** Formatted content plans from Phase 4 (discussed in chat)  
**Purpose:** Plan final naming conventions, cross-references, metadata  
**Output:** Implementation checklist (discussed in chat, ready for execution)

### 5.1 Naming Checklist (To Discuss in Chat)

For each file, apply these naming principles during chat planning:

- [ ] Remove all date stamps (`-20260118`, `-20260119`, etc.)
- [ ] Remove all phase designations (`PHASE-*`, `AC-*`, `ISSUE-*`)
- [ ] Replace abbreviated session names (`SESSION-`, `CHAT-`, `CONSOLIDATION-`) with descriptive names
- [ ] Use consistent prefixing (sequential for ordering, descriptive for reference)
- [ ] Ensure filename reflects document purpose, not creation method
- [ ] Match filename to H1 heading

**Chat Task:** Review discovered files and propose new names following these principles.

### 5.2 File Finalization Planning (In-Chat)

During chat, plan these finalization steps for each consolidated document:

| Step | Action | Chat Verification |
|------|--------|---|
| 1 | Identify source files to consolidate | At least 2 sources per doc |
| 2 | Extract core technical content | All major topics represented |
| 3 | Plan unified outline | No redundancy, consistent terminology |
| 4 | Plan metadata (audience, version, date) | Frontmatter structure confirmed |
| 5 | Plan cross-links to related docs | All cross-refs use relative paths |
| 6 | Plan table of contents | Navigation structure confirmed |
| 7 | Verify no broken links | Link structure validated in chat |
| 8 | Identify technical review requirements | 2+ reviewers for critical docs |
| 9 | Plan folder placement | File placement strategy confirmed |
| 10 | Plan archival of source files | Original files will be archived |

**Chat Output:** Implementation plan with specific files, targets, and review requirements.

---

## Execution Strategy: In-Chat Collaboration

All work is performed through GitHub Copilot Chat conversation with real-time discussion and confirmation. No separate reporting files are created.

### Pre-Implementation Discussion in Chat

1. **File Inventory Discussion**
   - List all discovered documentation files
   - Categorize by type and location
   - Discuss protected vs. movable files
   - Confirm total file count and distribution

2. **Consolidation Strategy Confirmation**
   - Review proposed consolidation mappings
   - Discuss which content to merge vs. archive
   - Identify dependencies between documents
   - Confirm target structure

3. **Architecture Review**
   - Validate folder hierarchy matches CORTEX capabilities
   - Confirm audience segmentation (Architects/Developers/Operators)
   - Review naming conventions for consistency
   - Confirm link structure strategy

4. **Stakeholder Alignment**
   - Discuss documentation audience and use cases
   - Confirm what content is "live" vs. "historical"
   - Agree on which files to archive vs. preserve
   - Identify any special content requirements

### Implementation Execution (Sequential in Chat)

1. **Phase 0: File Discovery** (Discuss in chat)
   - Run discovery commands in terminal
   - Present results in chat
   - Categorize findings
   - Confirm decisions before proceeding

2. **Phase 1-2: Analysis & Planning** (Discuss in chat)
   - Present categorization results
   - Discuss consolidation opportunities
   - Identify content to archive
   - Confirm strategy and dependencies

3. **Phase 3: Structure Planning** (Discuss in chat)
   - Review target folder hierarchy
   - Confirm file placement strategy
   - Validate naming conventions
   - Get approval before folder creation

4. **Phase 4-5: Content & Metadata Planning** (Discuss in chat)
   - Review consolidation mappings
   - Discuss formatting standards
   - Plan cross-references
   - Confirm implementation checklist

### Success Validation (In-Chat Discussion)

After each phase, present results in chat for confirmation:

| Phase | Chat Deliverable | Confirmation Required |
|-------|---|---|
| **Phase 0** | File inventory with categorization | Verify file counts, blacklist correctness |
| **Phase 1-2** | Consolidation analysis & decisions | Approve strategy, archive targets |
| **Phase 3** | Folder structure plan & file mapping | Confirm hierarchy, naming, placement |
| **Phase 4-5** | Content consolidation & metadata plan | Review format, cross-links, metadata |

---

## Previous Execution Checklist (DEPRECATED - Replaced by In-Chat Approach)

---

## Phase 6: Documentation Enhancement Discovery (POST-ORGANIZATION)

**Purpose:** After files have been organized (Phases 0-5), identify all new features and capabilities that need documentation enhancement.

**Trigger:** Run this phase after the docs/ folder is fully organized and structured.

### 6.1 Feature Discovery from Roadmap

Scan `_workspaces/roadmap/cortex-impl-map.yaml` to identify implemented features:

**Discovery Checklist:**
```yaml
discovery_sources:
  - _workspaces/roadmap/cortex-impl-map.yaml (phases_implementation_status section)
  - _workspaces/roadmap/phases/*.yaml (individual phase specs)
  - src/**/*.py (implementation patterns)
  - cortex/**/*.py (core modules)
  - tests/**/*.py (test coverage reveals features)
```

**Feature Categories to Extract:**

| Category | Source Location | Documentation Target |
|----------|-----------------|---------------------|
| **Completed Phases** | `phase_tracker.*` with `locked: true` | Architecture, API Reference |
| **MCP Tools** | `src/mcp/*.py`, `cortex/mcp/*.py` | API Reference (MCP Protocol) |
| **Orchestrators** | `src/orchestrators/**/*.py` | Orchestration Engine, Tutorials |
| **Governance Rules** | `cortex_brain/tier0/governance/*.yaml` | Security & Governance |
| **Resilience Patterns** | `src/core/governance/*.py` | Resilience Patterns |
| **Domain Brain** | `src/core/knowledge/*.py` | Domain Brain |
| **Deployment** | `src/deployment/*.py` | Deployment Guides |
| **Response Composition** | `src/orchestrators/response/*.py` | API Reference |
| **Complexity Assessment** | `src/complexity/*.py`, `src/confirmation/*.py` | Architecture |

### 6.2 Documentation Gap Analysis

For each discovered feature, check documentation coverage:

**Gap Detection Matrix:**

| Feature | Has Architecture Doc | Has API Reference | Has Tutorial | Has Guide | Gap Score |
|---------|---------------------|-------------------|--------------|-----------|-----------|
| MCP Protocol Server | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | 0-4 |
| Complexity Assessment | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | 0-4 |
| Response Composition | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | 0-4 |
| Governance Rules | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | 0-4 |
| LENS Protocol | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | 0-4 |
| Domain Brain | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | 0-4 |
| Conversation Protocol | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | 0-4 |
| Telemetry System | ✅/❌ | ✅/❌ | ✅/❌ | ✅/❌ | 0-4 |

**Gap Score Interpretation:**
- 0: Fully documented
- 1-2: Minor gaps (enhance existing)
- 3-4: Major gaps (create new docs)

### 6.3 Documentation Quality Assessment

For each existing documentation file, evaluate:

**Quality Criteria:**

| Criterion | Weight | Check |
|-----------|--------|-------|
| **Accuracy** | 30% | Content matches actual implementation |
| **Completeness** | 25% | All features covered, no missing sections |
| **Currency** | 20% | Reflects latest phase completions |
| **Technical Depth** | 15% | Sufficient detail for target audience |
| **Cross-References** | 10% | Links to related docs work, are current |

**Assessment Actions:**

| Quality Score | Action |
|---------------|--------|
| 90-100% | No action needed |
| 70-89% | Minor enhancement (add missing details) |
| 50-69% | Significant update (rewrite sections) |
| <50% | Major rewrite or deprecate |

### 6.4 Enhancement Execution Strategy

**Step 1: Recursive Documentation Scan**
```bash
find docs/ -name "*.md" -type f | while read file; do
  echo "Analyzing: $file"
  # Extract feature mentions
  # Check against roadmap features
  # Identify gaps
done
```

**Step 2: Feature-to-Doc Mapping**

For each implemented feature (from cortex-impl-map.yaml):
1. Identify which doc(s) should cover it
2. Check if coverage exists
3. If missing → flag for creation
4. If incomplete → flag for enhancement

**Step 3: Prioritized Enhancement Queue**

| Priority | Criteria | Action |
|----------|----------|--------|
| P0 | Core features with no documentation | Create immediately |
| P1 | Major features with outdated docs | Update within session |
| P2 | Features with incomplete coverage | Enhance progressively |
| P3 | Nice-to-have improvements | Backlog for future |

### 6.5 Redundancy & Validity Check

**Redundancy Detection:**
- Identify duplicate content across files
- Flag overlapping topics for consolidation
- Mark superseded content for deletion

**Validity Check:**
- Cross-reference claims against implementation
- Verify code examples match actual APIs
- Confirm feature availability (not just planned)

**Deletion Criteria:**

| Condition | Action |
|-----------|--------|
| Content duplicated elsewhere with better quality | DELETE |
| Feature no longer exists in implementation | DELETE |
| Content contradicts actual behavior | CORRECT or DELETE |
| Working notes not converted to docs | ARCHIVE or DELETE |
| Phase-specific docs for locked phases | ARCHIVE |

---

## Phase 7: Documentation Content Enhancement (EXECUTION)

**Purpose:** Execute enhancements identified in Phase 6.

### 7.1 Enhancement Types

| Type | Description | Approach |
|------|-------------|----------|
| **Technical Enhancement** | Add implementation details, code patterns | Read source code, extract patterns |
| **Business Value Enhancement** | Add use cases, benefits, ROI | Analyze feature purpose, document value |
| **Integration Enhancement** | Add how features work together | Map feature dependencies |
| **Example Enhancement** | Add working examples | Create minimal reproducible examples |
| **Cross-Reference Enhancement** | Add links to related docs | Audit and update internal links |

### 7.2 Enhancement Standards

Every enhanced document MUST include:

```markdown
# Document Title

**Last Updated:** YYYY-MM-DD  
**Audience:** [Architect/Developer/Operator]  
**Prerequisites:** [List or "None"]

## Overview
2-3 sentence executive summary

## Key Concepts
Bulleted list of foundational concepts

## [Main Content Sections]
Detailed technical content

## Configuration
YAML/JSON configuration examples (if applicable)

## Integration Points
How this feature connects to other CORTEX components

## Related Documentation
- [Link 1](path/to/doc1.md)
- [Link 2](path/to/doc2.md)

## Troubleshooting
Common issues and solutions (if applicable)
```

### 7.3 Source-of-Truth Validation

Every documentation claim MUST be validated against:

| Source | Validation Method |
|--------|-------------------|
| `cortex-impl-map.yaml` | Feature exists in `phases_implementation_status` with status indicating completion |
| Source code | Implementation file exists and matches documented behavior |
| Tests | Test coverage exists for documented features |
| Governance rules | Rule exists in `cortex_brain/tier0/governance/` |

**Validation Command:**
```bash
# Verify feature exists in implementation
grep -r "feature_name" src/ cortex/ --include="*.py"

# Verify test coverage
grep -r "test_feature_name" tests/ --include="*.py"

# Verify governance rule
grep -r "RULE-ID" cortex_brain/tier0/governance/ --include="*.yaml"
```

---

## Key Principles (Guiding Standards)

1. **Single Source of Truth**: One doc per topic; cross-reference others rather than duplicate
2. **Audience-First**: Every doc identifies its primary audience in the first paragraph
3. **Discoverability**: Clear hierarchy, descriptive names, comprehensive index
4. **Maintainability**: Production naming removes need for regular updates to file metadata
5. **Liveability**: Docs reflect actual live capabilities, not historical plans
6. **Navigation**: Breadcrumb paths and related-doc links on every page
7. **Executive Summary**: Every document starts with a 2-3 sentence overview
8. **Version Coupling**: Documentation version matches CORTEX release version
9. **No Temporal Artifacts**: Dates/phases removed; structure reflects capability, not timeline
10. **Accessibility**: High-level technical language; code examples in source, not docs
11. **In-Chat Collaboration**: All decisions, plans, and validations happen through chat conversation
12. **Reality-Based**: Documentation ONLY reflects implemented features, never assumptions or plans

---

## Notes for Implementation (In-Chat Context)

- **Real-Time Discussion**: Each phase presents findings in chat and waits for confirmation
- **No Hidden Work**: All analysis, planning, and decision-making is transparent in conversation
- **Interactive Validation**: After each major step, chat confirms results before proceeding
- **Stakeholder Alignment**: Decisions are discussed directly with user in real-time
- **Git Strategy**: All changes will be committed with clear messaging after in-chat approval
- **Traceability**: Full conversation history serves as documentation of decisions and rationale
- **Source Verification**: Every claim validated against implementation before documenting

---

## Expected Outcomes

**Before**: 180+ files, chaos, obsolete content mixed with live docs, temporal naming, unclear ownership

**After**:
- ✅ 80 production-ready files
- ✅ Hierarchical structure following industry standards (DiRT, Vale, etc.)
- ✅ Clear audience segmentation (Architect/Developer/Operator pathways)
- ✅ Consolidated content (no redundancy)
- ✅ Accurate reflection of live CORTEX capabilities
- ✅ Discoverable navigation and comprehensive indexing
- ✅ Production naming (no dates, phases, or session references)
- ✅ Maintainable structure (easy to add new docs, update existing ones)
- ✅ Compliance documentation (GDPR/HIPAA/SOC2 mappings)
- ✅ Operational guides (deployment, monitoring, troubleshooting for all environments)
- ✅ All content validated against implementation (no assumptions)
- ✅ Enhancement discovery process for ongoing maintenance

---

## Prompt Refactoring Summary

**Changes Made (January 20, 2026):**
- Converted from interactive chat-based workflow to autonomous agent-based workflow
- Created `doc-restructuring-agent.py` - Pure Python autonomous agent with zero chat dependencies
- Created `doc-restructuring-scheduler.yaml` - Execution scheduler with weekly + event-based triggers
- Created `README-AUTONOMOUS.md` - Complete guide to autonomous operation
- Phase 0 now describes autonomous scanning (no confirmation needed)
- Phase 1-2 now describes automatic categorization (rules-driven, no decisions)
- Phases 3-5 now describe autonomous execution (immediate, no approval gates)
- Removed all interactive chat discussion requirements
- Agent performs all file operations automatically with git backup
- Full audit logging and comprehensive JSON reports
- Protected file blacklist enforcement
- Zero user interruption during execution

See [Autonomous Agent Documentation](.github/agents/README-AUTONOMOUS.md) for setup and operation.

