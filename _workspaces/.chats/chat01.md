User: Follow instructions in [cortex-architect.prompt.md](file:///d%3A/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md).
review CORTEX REPO holisticaly espeically workflow tempaltes and orchestrators. How do we enhance TDD orchestrator to use an html builder that is built specificatlly to create high quality html pages. Similar for all other stacks that use knowledge yamls, and best practices to work with their respective stack.

Enhance my vision. Analyze my request using CORTEX's challenge-first protocol: audit existing capabilities, identify architectural fit within current patterns, then deliver your SINGLE BEST recommendation (no alternatives) that addresses the ask vs. challenge tension inline. Evaluate through CORTEX's core design pillars: extensibility, scalability, accuracy, team collaboration, and long-term maintainability. Ensure MCP-first exposure, orchestrator integrity, and zero regression risk. Present findings in executive-ready format: ≤60 seconds read time, comparison tables, clear sections with visual hierarchy optimized for VS Code Copilot Chat rendering.

GitHub Copilot: 

 

Created 6 todos

Deep CORTEX architecture audit

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/core/tdd_orchestrator.py#1-1), lines 1 to 150

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/strategies)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/knowledge)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/knowledge-base)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/core/orchestrator_protocol_mixin.py#1-1), lines 1 to 150

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/mcp/tools)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/domain)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/templates)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/intelligence)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/lens)

Searched for regex `Builder|builder|StackBuilder|HtmlBuilder|stack_builder` (`**/cortex/**/*.py`), 20 results

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/core/tdd_orchestrator.py#150-150), lines 150 to 400

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/core/tdd_orchestrator.py#400-400), lines 400 to 700

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/core/tdd_orchestrator.py#700-700), lines 700 to 1000

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/core/tdd_orchestrator.py#1000-1000), lines 1000 to 1300

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/core/tdd_orchestrator.py#1300-1300), lines 1300 to 1600

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/core/tdd_orchestrator.py#1600-1600), lines 1600 to 2000

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/core/orchestrator_protocol_mixin.py#150-150), lines 150 to 360

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/strategies/stage_execution_strategy.py)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/domain/strategy_base.py#1-1), lines 1 to 100

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/templates/template_builder.py#1-1), lines 1 to 100

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/templates/template_builder.py#100-100), lines 100 to 215

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/knowledge/backend-python)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/knowledge/architecture)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/knowledge/security)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/knowledge/testing-validation)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/knowledge-base/architecture)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/knowledge-base/governance)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/tdd)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/primitives)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/governance)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/audit)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/domain/domain_orchestrator.py#1-1), lines 1 to 100

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/domain/refactoring_orchestrator.py#1-1), lines 1 to 100

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/knowledge/backend-python/clean-code.yaml)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/knowledge/architecture/engineering-design-patterns.yaml)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/knowledge/testing-validation/tdd-best-practices.yaml)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/tdd/tdd-feature-implementation.yaml)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/tdd/tdd-api-service.yaml#1-1), lines 1 to 100

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/audit/audit-fix-pipeline.yaml#1-1), lines 1 to 100

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/mcp/tools/__init__.py#1-1), lines 1 to 80

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/mcp/tools/core.py#1-1), lines 1 to 80

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/mcp/tools/governance.py#1-1), lines 1 to 100

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/domain/domain_orchestrator.py#100-100), lines 100 to 200

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/knowledge-base/architecture/architecture-best-practices.yaml#1-1), lines 1 to 100

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/knowledge-base/governance/compliance-rules.yaml)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/mcp/mcp_tool_base.py#1-1), lines 1 to 100

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/core/pipeline_stage_strategy.py)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/domain/domain_orchestrator.py#200-200), lines 200 to 349

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/domain/strategy_base.py#100-100), lines 100 to 149

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/core/knowledge_guidance_engine.py#1-1), lines 1 to 100

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/core/interfaces/i_orchestrator.py#1-1), lines 1 to 100

Searched for regex `class.*Builder.*:|StackBuilder|HtmlBuilder|stack_builder|template_builder` (`**/cortex/**/*.py`), 19 results

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/knowledge/INDEX.yaml#1-1), lines 1 to 100

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/domain/refactoring)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/mcp/mcp_tool_base.py#100-100), lines 100 to 200

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/core)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/core/holistic_context_builder.py#1-1), lines 1 to 60

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/primitives/validation)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/domain/refactoring/refactoring_models.py)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/core/workflow_template_mixin.py#1-1), lines 1 to 80

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/mcp/tools/__init__.py#80-80), lines 80 to 295

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/domain/refactoring/adapters)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/primitives/validation/detect-fix-rescan-loop.yaml#1-1), lines 1 to 100

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/governance/master-plan-phase-lifecycle.yaml#1-1), lines 1 to 100

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/lens/lens_orchestrator.py#1-1), lines 1 to 80

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/lens/core.py)

Starting: *Deliver recommendation* (6/6)

Let me grab a few more specific files to ground the recommendation precisely. 

Gather stack strategy details

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/knowledge/index.yaml)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/tdd)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/frontend)

Searched for files matching `**/cortex/orchestrators/domain/refactoring/adapters/*`, 6 matches

Searched for files matching `**/tech_stack_analyzer*`, 1 match

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/templates/content_strategy.py#1-1), lines 1 to 200

Searched for regex `html|HTML` (`**/cortex/**/*.py`), 20 results

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/knowledge/testing-validation)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/tdd/frontend-tdd-workflow.yaml#1-1), lines 1 to 200

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/tdd/tdd-api-service.yaml)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/tdd/tdd-feature-implementation.yaml)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/tdd/tdd-frontend-visual.yaml)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/tdd/test-strategy-matrix.yaml#1-1), lines 1 to 200

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/frontend/css-extraction-workflow.yaml)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/frontend/css-zero-inline-workflow.yaml#1-1), lines 1 to 200

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/frontend/html-refactor-validation.yaml#1-1), lines 1 to 200

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/frontend/typescript-refactor-workflow.yaml#1-1), lines 1 to 200

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/domain/refactoring/adapters/__init__.py)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/orchestrators/domain/refactoring/adapters/adapter_base.py)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/lens/analyzers/tech_stack_analyzer.py#1-1), lines 1 to 300

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/templates/content_strategy.py#200-200), lines 200 to 500

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/knowledge/testing-validation/tdd-best-practices.yaml)

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/tdd/frontend-tdd-workflow.yaml#200-200), lines 200 to 529

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/tdd/test-strategy-matrix.yaml#200-200), lines 200 to 317

Read [](file:///d%3A/PROJECTS/CORTEX/cortex-registry/workflows/templates/frontend/typescript-refactor-workflow.yaml#200-200), lines 200 to 289

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/lens/analyzers/tech_stack_analyzer.py#300-300), lines 300 to 463

Read [](file:///d%3A/PROJECTS/CORTEX/cortex/templates/content_strategy.py#500-500), lines 500 to 764

Searched for regex `html|HTML` (`**/cortex/**/*.py`), 100 results

Completed: *Deliver recommendation* (6/6)

---

## 🎨 CORTEX Architect DESIGN
**Author:** Asif Hussain | **Orchestrator:** DesignCoordinator ✅

---

## 📋 Summary — Stack-Aware Builder Infrastructure

You're asking CORTEX to graduate from **stack-agnostic TDD guidance** to **stack-specialized execution** — where an HTML builder knows semantic HTML5, BEM conventions, and accessibility; a Python builder knows pytest fixtures and type-narrowing; a .NET builder knows xUnit traits and Roslyn analyzers. The audit reveals CORTEX already has **80% of the wiring** but lacks the one bridging abstraction: a **StackBuilder protocol** that connects detected tech stacks to domain-specific knowledge and generation strategies.

---

## 🔍 Analysis — Current State vs. Target State

### What CORTEX Already Has (Assets to Leverage)

| Capability | Location | Status |
|---|---|---|
| Tech stack detection (15 languages, 25 configs, 18 imports) | tech_stack_analyzer.py | ✅ Detects stacks, but results are **not consumed downstream** |
| Adapter pattern for multi-language refactoring | adapters | ✅ `RefactoringAdapter` ABC — Rope/Roslyn/TS adapters |
| 30 knowledge YAMLs across 11 domains | knowledge | ⚠️ Organized by **domain** not by **stack** — only `backend-python` is stack-specific |
| 6 HTML generation modules (dashboards, security reports) | dashboards, templates | ⚠️ All are **ad-hoc f-string/Jinja2** — no shared quality contract |
| Workflow templates with `knowledge_context` mode-awareness | tdd | ✅ `architect_mode` vs `production_mode` with `{{template_variables}}` |
| Content strategy with 72 registered templates | content_strategy.py | ✅ Domain-indexed, but no stack dimension |
| `StageExecutionStrategy` ABC for pipeline stages | strategies | ✅ Strategy pattern exists, but only for pipeline stages |
| `TDDKnowledgeLoader` for discipline rules | tdd_orchestrator.py | ⚠️ Loads stack-agnostic rules — same guidance for all languages |

### The Gap — One Missing Abstraction

```
LENS detects "React + TypeScript"  →  ???  →  TDDOrchestrator gives generic guidance
                                      ↑
                             No StackBuilder dispatch
```

The `TechStackAnalyzer` produces rich `StackDetection` results (language, framework, confidence) but **nothing consumes them to differentiate behavior**. The `TDDOrchestrator.determine_phase()` does keyword matching, not stack-aware routing. Knowledge YAMLs have no `stack:` key for filtering. The 6 HTML generation modules each reinvent their own patterns with no shared quality contract.

---

## 💡 Recommendation — StackBuilder Protocol + Stack Knowledge Registry

### Architecture: 3-Layer Stack Intelligence

```
┌─────────────────────────────────────────────────────────────┐
│  Layer 3: Stack Builders (new)                              │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │HTMLBuilder│ │PyBuilder │ │TSBuilder │ │DotNetBuilder │   │
│  │ semantic  │ │ pytest   │ │ vitest   │ │ xunit        │   │
│  │ a11y/BEM  │ │ fixtures │ │ strict   │ │ roslyn       │   │
│  └─────┬─────┘ └─────┬────┘ └────┬─────┘ └──────┬───────┘   │
│        └──────────────┴──────────┴───────────────┘           │
│                       implements                             │
│              ┌────────────────────────┐                      │
│              │  StackBuilder (ABC)    │  ← new protocol      │
│              │  get_stack_id()        │                      │
│              │  get_test_patterns()   │                      │
│              │  get_best_practices()  │                      │
│              │  generate_scaffold()   │                      │
│              │  validate_output()     │                      │
│              └────────────┬───────────┘                      │
├────────────────────────────┼─────────────────────────────────┤
│  Layer 2: Stack Knowledge Registry (new)                     │
│  cortex-registry/knowledge/stacks/                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐   │
│  │html5.yaml│ │python.   │ │typescript│ │dotnet.yaml   │   │
│  │  semantic │ │  yaml    │ │  .yaml   │ │  xunit       │   │
│  │  a11y     │ │  pytest  │ │  vitest  │ │  efcore      │   │
│  │  BEM/CSS  │ │  typing  │ │  strict  │ │  aspnet      │   │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘   │
├─────────────────────────────────────────────────────────────┤
│  Layer 1: Existing CORTEX Infrastructure (unchanged)         │
│  TechStackAnalyzer → StackDetection → confidence scoring     │
│  OrchestratorProtocolMixin → cross-cutting intelligence      │
│  RefactoringAdapter pattern → language-specific tools         │
│  WorkflowTemplate knowledge_context → mode-aware execution   │
└─────────────────────────────────────────────────────────────┘
```

### How It Wires Into Existing Orchestrators

| Orchestrator | Current Behavior | Enhanced Behavior |
|---|---|---|
| **TDDOrchestrator** | `determine_phase()` → generic guidance | `determine_phase()` → `StackBuilderRegistry.get(stack_id).get_test_patterns()` → stack-specific RED/GREEN/REFACTOR |
| **RefactoringOrchestrator** | `RefactoringAdapter` per language | Adapter delegates to `StackBuilder.get_best_practices()` for refactoring suggestions |
| **DomainOrchestrator** | `DomainHandler.execute()` generic | Handler queries `StackBuilder.generate_scaffold()` for stack-aware scaffolding |
| **LENSOrchestrator** | `TechStackAnalyzer` detects but doesn't dispatch | Detection result feeds `StackBuilderRegistry.resolve(detections)` — automatic |

### StackBuilder ABC — Follows Existing RefactoringAdapter Pattern

```python
# cortex/orchestrators/strategies/stack_builder.py
class StackBuilder(ABC):
    """Stack-specific builder following RefactoringAdapter pattern."""

    @abstractmethod
    def get_stack_id(self) -> str: ...              # "html5", "python", "typescript", "dotnet"

    @abstractmethod
    def get_supported_frameworks(self) -> List[str]: ...  # ["react", "vue", "angular"]

    @abstractmethod
    def get_test_patterns(self, phase: TDDPhase) -> StackTestGuidance: ...
        # RED: what test framework, assertion style, fixture patterns
        # GREEN: minimum implementation idioms
        # REFACTOR: stack-specific code smells to eliminate

    @abstractmethod
    def get_best_practices(self) -> StackBestPractices: ...
        # Loaded from cortex-registry/knowledge/stacks/{stack}.yaml

    @abstractmethod
    def generate_scaffold(self, artifact_type: str, context: Dict) -> str: ...
        # "component" → React component + test file
        # "page" → semantic HTML5 + CSS + test
        # "endpoint" → FastAPI route + contract test

    @abstractmethod
    def validate_output(self, content: str) -> StackValidationResult: ...
        # HTML: W3C + a11y + semantic structure
        # Python: type coverage + import hygiene
        # TS: strict mode compliance + no `any`
```

### HTML Builder — Concrete Example (Your Primary Ask)

```python
# cortex/orchestrators/strategies/builders/html_builder.py
class HtmlStackBuilder(StackBuilder):
    """High-quality HTML generation with semantic structure, a11y, BEM."""

    def get_stack_id(self) -> str:
        return "html5"

    def get_test_patterns(self, phase: TDDPhase) -> StackTestGuidance:
        # RED: DOM structure assertions, a11y tree validation, Lighthouse CI
        # GREEN: semantic HTML5 elements, ARIA attributes, BEM class naming
        # REFACTOR: inline style extraction, duplicate section dedup, responsive

    def validate_output(self, content: str) -> StackValidationResult:
        # W3C validation, axe-core a11y audit, zero inline styles (CORE-073)
        # Semantic element coverage (header/main/nav/section/article/footer)
        # BEM naming convention compliance
```

### Stack Knowledge YAML Schema (New)

```yaml
# cortex-registry/knowledge/stacks/html5.yaml
stack:
  id: html5
  display_name: "HTML5 + CSS"
  category: frontend
  version: "1.0"

quality_contract:
  semantic_elements: [header, main, nav, section, article, aside, footer]
  accessibility:
    standard: "WCAG 2.1 AA"
    tooling: [axe-core, lighthouse]
    required_attributes: [alt, aria-label, role, lang]
  css:
    methodology: BEM
    zero_inline_styles: true          # CORE-073
    external_stylesheets: true
  validation:
    w3c_validator: true
    lighthouse_score: 95

tdd_patterns:
  red:
    test_framework: pytest + beautifulsoup4
    assertions: [dom_structure, a11y_tree, semantic_coverage, no_inline_styles]
    golden_tests: [visual_regression, lighthouse_ci]
  green:
    generation_rules:
      - "Use semantic HTML5 elements over generic divs"
      - "Every img has alt, every form input has label"
      - "BEM class naming: block__element--modifier"
      - "External CSS linked in <head>, never inline style"
  refactor:
    smells: [SMELL-13, SMELL-18, SMELL-21]  # duplicate sections, DOM issues, inline styles
    workflows: [css-extraction.yaml, dom-deduplication.yaml]

best_practices:
  performance: [lazy_loading, critical_css, preload_fonts]
  seo: [meta_description, open_graph, canonical_url, structured_data]
  security: [csp_header, sri_hashes, no_inline_scripts]
```

### MCP Exposure — New Tool Operation

```python
# Added to existing cortex_scaffold_files or new cortex_stack tool
cortex_stack:
  operations:
    - list       # Show all registered stack builders
    - guidance   # Get stack-specific TDD guidance for detected stack
    - scaffold   # Generate stack-aware file scaffold
    - validate   # Run stack quality contract against output
```

### Integration Points — Zero Breaking Changes

| Integration | Mechanism | Risk |
|---|---|---|
| `TDDOrchestrator.build_guidance()` | Add `stack_context` parameter from `StackBuilderRegistry` | **None** — additive parameter with default `None` |
| `TechStackAnalyzer` output | Feed `StackDetection` into `StackBuilderRegistry.resolve()` | **None** — consumer addition, no producer change |
| Knowledge loading | New `cortex-registry/knowledge/stacks/` directory alongside existing structure | **None** — new directory, no existing files moved |
| Workflow templates | `knowledge_context.stack_builder` field in templates | **None** — templates are YAML, additive keys are safe |
| MCP tool | New `cortex_stack` tool or new operation on `cortex_scaffold_files` | **None** — additive tool registration |
| `OrchestratorProtocolMixin` | No changes needed — cross-cutting intelligence already wired | **None** |

---

## ⚖️ Benefits & Risks

| Design Pillar | Score | Assessment |
|---|---|---|
| **Extensibility** | 🟢 9/10 | New stacks = 1 YAML + 1 Builder class. Follows `RefactoringAdapter` pattern already proven with 3 languages |
| **Scalability** | 🟢 9/10 | Registry pattern supports unlimited stacks. Knowledge YAMLs are lazy-loaded per detection |
| **Accuracy** | 🟢 9/10 | Stack detection already exists at 0.0–1.0 confidence. Builder dispatch only fires above threshold |
| **Collaboration** | 🟢 8/10 | Each stack is self-contained (1 YAML + 1 class). Teams can own their stack without touching core |
| **Maintainability** | 🟢 9/10 | Follows 3 existing patterns (Adapter ABC, Strategy dispatch, Knowledge YAML). No novel abstractions |
| **Regression Risk** | 🟢 0 | All additions are additive. No existing method signatures change. Default `None` fallbacks everywhere |

---

## 🎯 Next Steps — Phased Implementation

| Phase | Deliverable | Files | Effort |
|---|---|---|---|
| **68-A** | `StackBuilder` ABC + `StackBuilderRegistry` | `cortex/orchestrators/strategies/stack_builder.py`, `cortex/orchestrators/strategies/stack_builder_registry.py` | 1 day |
| **68-B** | `HtmlStackBuilder` (your primary ask) + `html5.yaml` knowledge | `cortex/orchestrators/strategies/builders/html_builder.py`, `cortex-registry/knowledge/stacks/html5.yaml` | 1 day |
| **68-C** | `PythonStackBuilder` + `python.yaml` knowledge | `cortex/orchestrators/strategies/builders/python_builder.py`, `cortex-registry/knowledge/stacks/python.yaml` | 1 day |
| **68-D** | `TDDOrchestrator` integration — wire `StackBuilderRegistry` into `build_guidance()` + `determine_phase()` | Modify `tdd_orchestrator.py` (additive) | 0.5 day |
| **68-E** | `cortex_stack` MCP tool + tests | `cortex/mcp/tools/cortex_stack.py`, `tests/mcp/test_cortex_stack.py` | 0.5 day |
| **68-F** | TypeScript + .NET builders + workflow template updates | `builders/typescript_builder.py`, `builders/dotnet_builder.py`, template YAML updates | 1 day |

### ⚡ If you type `proceed`, CORTEX will:
- Create the Phase 68 dedicated plan file at `cortex-registry/planning/phases/planned/phase-68-stack-builder-infrastructure.yaml` with full gap catalogue, TDD sequences, and acceptance criteria
- Add thin reference entry to `cortex-master.yaml`
- Begin Phase 68-A: write failing tests for `StackBuilder` ABC and `StackBuilderRegistry`, then implement (TDD RED → GREEN → REFACTOR)