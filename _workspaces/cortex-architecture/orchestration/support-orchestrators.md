# Support Orchestrators

**Purpose:** Documentation of unified support orchestrators — the consolidated association areas of CORTEX  
**Audience:** Developers, Operations  
**Last Updated:** 2026-02-13 | **Wave 7 Track 4:** CONSOLIDATION COMPLETE

---

## Table of Contents

- [Overview](#overview)
- [UnifiedOnboardingOrchestrator](#unifiedonboardingorchestrator)
- [UnifiedAnalysisOrchestrator](#unifiedanalysisorchestrator)
- [UnifiedQualityAssuranceOrchestrator](#unifiedqualityassuranceorchestrator)
- [UnifiedDiscoveryOrchestrator](#unifieddiscoveryorchestrator)
- [Deprecated Predecessors](#deprecated-predecessors)
- [Related Documents](#related-documents)

---

## Overview

### Neural Pruning: From 12 Regions to 4 Association Areas

In a developing brain, **synaptic pruning** eliminates redundant neural connections to create faster, more efficient pathways. A child's brain has twice as many synapses as an adult's — it's the pruning that creates expertise.

CORTEX underwent the same maturation. During **Wave 7 Track 4**, 12 overlapping support orchestrators were consolidated into **4 unified orchestrators** — a 37% reduction that created faster routing, lower memory overhead, and clearer cognitive boundaries.

Each unified orchestrator is like a mature **association area** in the brain — a region that integrates input from multiple simpler areas into a single, more capable processing center. The temporal-parietal junction combines auditory, visual, and spatial information. Similarly, the UnifiedQualityAssuranceOrchestrator combines challenge generation, code review, recommendation gating, meta-audit, and security review into one coherent quality judgment center.

### The 4 Unified Support Orchestrators

| Orchestrator | Priority | Absorbed | System Analogy |
|--------------|----------|----------|----------------|
| **UnifiedOnboardingOrchestrator** | 105 | 3 predecessors | Memory initialization — encoding new repositories |
| **UnifiedAnalysisOrchestrator** | 115 | 2 predecessors | Unified analysis — comprehensive perception |
| **UnifiedQualityAssuranceOrchestrator** | 125 | 5 predecessors | Quality control — error & quality assessment |
| **UnifiedDiscoveryOrchestrator** | 135 | 2 predecessors | Discovery engine — exploration & learning |

---

## UnifiedOnboardingOrchestrator

### System Analogy: Memory Initialization

When you set up a new system, it needs to learn the environment — scanning configurations, detecting capabilities, and mapping resources. The UnifiedOnboardingOrchestrator does the same for new repositories — scanning, mapping, and encoding everything CORTEX needs to know about a codebase.

### Absorbed Capabilities

| Predecessor | What It Did | Now Handled By |
|------------|-------------|----------------|
| **OnboardingOrchestrator** | Basic repository onboarding | `onboard()` method |
| **RepositoryOnboardingOrchestrator** | Security scanning + profiling | `profile_and_scan()` method |
| **SetupOrchestrator** | Environment initialization | `setup_environment()` method |

### Capabilities

- **Project Analysis** — Detect project type, frameworks, languages
- **Security Scan** — Initial vulnerability assessment (OWASP, dependency CVEs)
- **Configuration** — Generate `.cortex/` config, MCP setup
- **Knowledge Extraction** — Extract domain terminology, API patterns, conventions
- **Environment Setup** — Git hooks, virtual environment, dependency installation

### Onboarding Flow

```
1. SCAN: Project structure analysis
   ├── Language detection   ├── Framework identification
   └── Dependency analysis
           ↓
2. SECURITY: Vulnerability assessment
   ├── Dependency CVEs     ├── Secrets detection
   └── OWASP compliance
           ↓
3. CONFIGURE: CORTEX setup
   ├── Generate .cortex/   ├── Setup MCP integration
   └── Configure git hooks
           ↓
4. EXTRACT: Knowledge extraction
   ├── API patterns        ├── Domain terminology
   └── Coding conventions
           ↓
5. REPORT: Onboarding summary with health score
```

### MCP Tool

```python
cortex_onboard_repository(
    path="./my-project",
    scan_security=True,
    extract_knowledge=True
)
```

---

## UnifiedAnalysisOrchestrator

### Brain Analogy: Visual Association Cortex

The **visual association cortex** doesn't just see raw pixels — it recognizes patterns, objects, and meaning in visual input. It integrates low-level visual features into high-level understanding. The UnifiedAnalysisOrchestrator does the same for code: it combines LENS analysis, AST parsing, tool discovery, and dependency analysis into a unified perception of your codebase.

### Absorbed Capabilities

| Predecessor | What It Did | Now Handled By |
|------------|-------------|----------------|
| **LENSOrchestrator** | Coordinated LENS analyzers | `analyze_with_lens()` method |
| **ToolDiscoveryOrchestrator** | Tool catalog and search | `discover_tools()` method |

### Capabilities

- **Code Analysis** — Full LENS pipeline (10 analyzers in parallel)
- **LENS Coordination** — Orchestrate Git, AST, Comment, Pattern, Config, DB, API, Security analyzers
- **Tool Discovery** — Search and catalog MCP tools by capability
- **Dependency Analysis** — Map code dependencies and detect drift

### Analysis Pipeline

```python
async def analyze(self, target: str, depth: str = "full") -> AnalysisResult:
    """
    Unified analysis combining LENS + tool discovery + dependencies.
    
    Like the visual association cortex processing multiple visual streams
    simultaneously and integrating them into a coherent perception.
    """
    # Parallel perception (like visual processing streams)
    lens_result, tool_result, dep_result = await asyncio.gather(
        self.analyze_with_lens(target, depth),
        self.discover_relevant_tools(target),
        self.analyze_dependencies(target)
    )
    
    # Synthesize into unified understanding
    return self.synthesize(lens_result, tool_result, dep_result)
```

---

## UnifiedQualityAssuranceOrchestrator

### Brain Analogy: Anterior Cingulate Cortex

The **anterior cingulate cortex (ACC)** is the brain's error detection and quality control center. It monitors for conflicts between what you intended and what actually happened, flagging mistakes before they become problems. It's why you feel that "something's wrong" sensation when you make a typo — the ACC caught the error before your conscious mind did.

The UnifiedQualityAssuranceOrchestrator is CORTEX's ACC — continuously monitoring code quality, detecting errors, generating challenges for risky decisions, and ensuring every output meets production standards.

### Absorbed Capabilities

| Predecessor | What It Did | Now Handled By |
|------------|-------------|----------------|
| **RecommendationGate** | Filtered unsafe recommendations | `gate_recommendation()` method |
| **ChallengeEngine** | Generated decision challenges | `generate_challenges()` method |
| **MetaAuditOrchestrator** | Audited the audit system itself | `meta_audit()` method |
| **CodeReviewOrchestrator** | Automated code review | `review_code()` method |
| **SecurityReviewEngine** | Security-focused review | `review_security()` method |

### Capabilities

- **Quality Assurance** — Comprehensive code quality validation
- **Challenge Generation** — Generate alternatives for risky decisions
- **Recommendation Gating** — Block unsafe suggestions (REJ-history check)
- **Meta-Audit** — Audit the audit system for completeness
- **Code Review** — Automated review against CORE rules and best practices
- **Security Review** — OWASP compliance, secrets detection, injection prevention

### Challenge Flow

```
DETECT: Identify challengeable decision
  └── Confidence < 0.7? Conflicting signals? High-impact operation?
          ↓
GENERATE: Create challenge with alternatives
  └── Formulate question, provide evidence, present options
          ↓
PRESENT: Display to user for decision
          ↓
RESOLVE: Handle user's choice
          ↓
LEARN: Record outcome for future accuracy improvement
```

---

## UnifiedDiscoveryOrchestrator

### System Analogy: The Discovery Engine

Modern systems include discovery mechanisms — search engines that help you find what you need, recommendation engines that suggest relevant content, and exploratory interfaces that reveal hidden features. When you encounter something unfamiliar, these systems help you investigate and learn.

The UnifiedDiscoveryOrchestrator is CORTEX's discovery engine — it drives exploration of new tools, generates learning paths, translates business language into technical terms, and helps users discover capabilities they didn't know existed.

### Absorbed Capabilities

| Predecessor | What It Did | Now Handled By |
|------------|-------------|----------------|
| **EducationalOrchestrator** | Learning paths and tutorials | `generate_learning_path()` method |
| **BusinessLanguageOrchestrator** | Business ↔ tech translation | `translate_business_terms()` method |

### Capabilities

- **Feature Discovery** — Surface relevant CORTEX capabilities
- **Learning Paths** — Generate personalized learning sequences
- **Business Language** — Translate domain terminology to technical concepts
- **Educational Content** — Explain complex CORTEX concepts accessibly
- **Tool Discovery** — Find and explain available MCP tools

---

## Deprecated Predecessors

The following orchestrators are **deprecated** and scheduled for removal on **2026-03-31**. They still function but are superseded by unified orchestrators:

| Predecessor | Priority | Replaced By | Status |
|------------|----------|-------------|--------|
| OnboardingOrchestrator | 110 | UnifiedOnboardingOrchestrator | ⚠️ Deprecated |
| ToolDiscoveryOrchestrator | 120 | UnifiedAnalysisOrchestrator | ⚠️ Deprecated |
| UpgradeOrchestrator | 130 | UnifiedOnboardingOrchestrator | ⚠️ Deprecated |
| RollbackOrchestrator | 140 | WorkflowOrchestrator | ⚠️ Deprecated |
| SetupOrchestrator | 150 | UnifiedOnboardingOrchestrator | ⚠️ Deprecated |
| ComposedOrchestrator | 160 | MasterOrchestrator | ⚠️ Deprecated |
| WrappedTDDOrchestrator | 170 | TDDOrchestrator | ⚠️ Deprecated |

> **Migration:** If you depend on any deprecated orchestrator, migrate to the unified replacement before the sunset date. The unified orchestrators expose the same capabilities through consolidated interfaces.

---

## Related Documents

- [Orchestration Overview](overview.md) — Complete orchestrator atlas
- [Domain Orchestrators](domain-orchestrators.md) — Specialized brain lobes
- [Infrastructure Overview](../infrastructure/overview.md) — Brain life support systems

---

*Part of CORTEX Architecture Documentation*
