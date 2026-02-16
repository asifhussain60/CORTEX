# CORTEX Workflow Template Library

**Version:** 5.0 | **Status:** Production Ready | **Mode:** Knowledge-Parameterized + Convergence-Gated  
**Authority:** Phase 100 — Convergence-Gated Workflow Template Library  
**Created:** 2026-02-16

---

## Overview

The CORTEX Workflow Template Library provides **knowledge-parameterized, convergence-gated workflow templates** that adapt to repository context automatically. The same template resolves differently for CORTEX internal development (ARCHITECT mode) versus user production repositories (PRODUCTION mode).

### Key Innovations

1. **Knowledge Parameterization**: Templates contain placeholders (`{test_framework}`, `{auth_pattern}`, etc.) that resolve differently based on context
2. **Convergence-Gated Execution**: Every workflow step can loop until success criteria met (max_cycles safety limit)
3. **Two-Context Design**: Same template, different knowledge injection, correct output
4. **Auto-Injected Epilogues**: Post-phase deduplication reviews and holistic refactoring sweeps run automatically

---

## How Knowledge Parameterization Works

### Resolution Chain (Priority Order)

```
1. company/domains/*.yaml (HIGHEST PRECEDENCE)
   └─ Company-specific overrides (API design, security, compliance)

2. cortex_brain/onboarded_repos/{repo}_enhanced.json
   └─ Onboarded repo profile (tech stack, patterns, capabilities)

3. cortex-registry/_cortex-master/knowledge/ (45+ YAMLs)
   └─ CORTEX best practices (fills gaps not covered by company)
```

### Mode Detection

**ARCHITECT Mode** (CORTEX internal development):
- **Triggers**: `.cortex/` directory OR `cortex-registry/` directory OR `cortex/__init__.py` exists
- **Knowledge**: CORTEX-internal specs (registry, wiring, phases)
- **Output**: CORTEX architecture patterns (pytest, FastAPI, orchestrators)

**PRODUCTION Mode** (User's production repository):
- **Triggers**: None of the above markers present
- **Knowledge**: Onboarded repo profile + `company/domains/*.yaml`
- **Output**: User's framework, test runner, standards

### Template Placeholders

| Placeholder | ARCHITECT Value | PRODUCTION Value | Fallback |
|-------------|-----------------|------------------|----------|
| `{test_framework}` | `pytest` | From onboarded repo profile | `pytest` |
| `{component_library}` | `CORTEX orchestrator patterns` | From onboarded profile (React/Angular/Vue) | `vanilla HTML/CSS/JS` |
| `{auth_pattern}` | `MCP authentication` | From `company/domains/security-standards.yaml` | `OAuth2 with PKCE` |
| `{api_style}` | `FastAPI + MCP endpoints` | From `company/domains/api-design-standards.yaml` | `RESTful with OpenAPI` |
| `{compliance_standards}` | `CORTEX CORE rules` | From `company/domains/` (PCI-DSS, HIPAA, SOX) | `OWASP Top 10` |
| `{deployment_target}` | `CORTEX deployment pipeline` | From onboarded repo infrastructure detection | `Docker + CI/CD` |

---

## Convergence-Gated Execution

### Step State Machine (Using `transitions` FSM)

Every workflow step follows this lifecycle:

```
PENDING → RUNNING → CHECKING → PASSED
                       ↓
                    RETRYING (if not converged)
                       ↓
                    RUNNING (cycle++)
                       ↓
                    CHECKING
                       ↓
                    FAILED (max_cycles exceeded)
```

### Convergence Gate Configuration

Each step declares its success criteria:

```yaml
convergence_gate:
  max_cycles: 10              # Maximum retry iterations
  success_criteria:
    all_tests_pass: true
    no_regressions: true
    quality_improvement: ">10%"
  convergence_predicate: "all_tests_pass and no_regressions and quality_delta > 0.10"
  scan_function: "run_tests_and_measure_quality"
  backoff_strategy: "none"    # none | linear | exponential
```

### Auto-Injected Epilogues

**PostPhaseDeduplicationReview** (after each phase):
- LENS scans for code duplication introduced by completed phase
- Loops until no new duplicates found or max_cycles exceeded
- Uses CORE-035 (single canonical implementation) as standard

**HolisticRefactoringSweep** (after ALL phases):
- RefactoringOrchestrator runs across ALL files modified during workflow
- Ensures holistic coherence — no local optima from individual phase work
- Loops until LENS score meets baseline

---

## Template Categories

### TDD Templates
- **feature-implementation/**: Generic feature TDD workflow (RED→GREEN→REFACTOR)
- **frontend-visual/**: Visual TDD with screenshot comparison (migrated from Phase 99)
- **api-service/**: API service TDD with contract validation

### Security Templates
- **compliance-audit/**: Security compliance audit with zero-findings gate

### Quality Templates
- **code-uplift/**: Code quality uplift with metric improvement gate

### Migration Templates
- **modernize/**: Legacy modernization with incremental gate

### Cleanup Templates
- **deduplication/**: LENS-based deduplication with convergence loop

### Onboarding Templates
- **repo-setup/**: Repository onboarding with profile completeness check

### Review Templates
- **post-phase-dedup/**: Cross-phase deduplication check (auto-injected)

### Refactor Templates
- **holistic-sweep/**: Multi-file coherence sweep (auto-injected epilogue)

---

## Template Structure

Each template consists of:

```
cortex-registry/workflows/{category}/{template-name}/
├── metadata.yaml              # Governance + knowledge resolution + convergence config
├── workflow.yaml              # Workflow steps with knowledge placeholders
└── README.md                  # Template-specific documentation
```

### metadata.yaml Schema

```yaml
template_id: "{category}/{template-name}"
name: "Template Display Name"
version: "1.0"
category: "tdd|security|quality|migration|cleanup|onboarding|review|refactor"
description: "What this template does"

knowledge_resolution:
  required_placeholders:
    - "{test_framework}"
    - "{auth_pattern}"
  
  architect_resolution:
    test_framework: "pytest"
    auth_pattern: "MCP authentication"
  
  production_resolution:
    test_framework: "From onboarded repo profile"
    auth_pattern: "From company/domains/security-standards.yaml"

convergence_config:
  steps_with_gates:
    - step_id: "fix_critical"
      max_cycles: 10
      success_criteria:
        all_tests_pass: true
        no_regressions: true
      convergence_predicate: "all_tests_pass and no_regressions"
      scan_function: "run_tests_and_measure"

governance:
  core_rules:
    - CORE-008  # TDD mandatory
    - CORE-027  # Audit trail
  
  approval_required: true
  auto_checkpoint: true
```

### workflow.yaml Schema

```yaml
workflow_id: "{template_id}"
stages:
  - stage_id: "S1"
    name: "Stage Name"
    steps:
      - step_id: "step1"
        name: "Step Name"
        orchestrator: "TDDOrchestrator"
        parameters:
          test_framework: "{test_framework}"  # Knowledge placeholder
          auth_pattern: "{auth_pattern}"      # Knowledge placeholder
        
        convergence_gate:
          max_cycles: 5
          success_criteria:
            tests_pass: true
          convergence_predicate: "tests_pass"
          scan_function: "run_tests"
```

---

## How to Create a New Template

### Step 1: Choose Category and Name

Choose an existing category or create a new one:
- `tdd/` — Test-driven development workflows
- `security/` — Security and compliance workflows
- `quality/` — Code quality improvement workflows
- `migration/` — Legacy modernization workflows
- `cleanup/` — Deduplication and refactoring workflows
- `onboarding/` — Repository setup workflows
- `review/` — Code review and analysis workflows
- `refactor/` — Refactoring workflows

### Step 2: Create Directory Structure

```bash
mkdir -p cortex-registry/workflows/{category}/{template-name}
cd cortex-registry/workflows/{category}/{template-name}
```

### Step 3: Create metadata.yaml

```yaml
template_id: "{category}/{template-name}"
name: "Your Template Name"
version: "1.0"
category: "{category}"
description: "What your template does"

knowledge_resolution:
  required_placeholders:
    - "{your_placeholder}"
  
  architect_resolution:
    your_placeholder: "CORTEX value"
  
  production_resolution:
    your_placeholder: "From company/domains/ or onboarded profile"

convergence_config:
  steps_with_gates:
    - step_id: "your_step"
      max_cycles: 5
      success_criteria:
        criterion_name: true
      convergence_predicate: "criterion_name"
      scan_function: "your_scan_function"

governance:
  core_rules:
    - CORE-008
    - CORE-027
  approval_required: true
```

### Step 4: Create workflow.yaml

```yaml
workflow_id: "{category}/{template-name}"
stages:
  - stage_id: "S1"
    name: "Your Stage"
    steps:
      - step_id: "step1"
        name: "Your Step"
        orchestrator: "YourOrchestrator"
        parameters:
          param1: "{your_placeholder}"
        
        convergence_gate:
          max_cycles: 5
          success_criteria:
            tests_pass: true
          convergence_predicate: "tests_pass"
          scan_function: "run_tests"
```

### Step 5: Create README.md

Document:
- What the template does
- When to use it
- Knowledge placeholders used
- Success criteria
- Example usage

### Step 6: Register in Master Manifest

The WorkflowTemplateRegistry auto-discovers templates, but you can manually verify:

```bash
# Regenerate manifest
python -m cortex.orchestrators.workflow.template_registry generate-manifest
```

---

## Knowledge Injection Flow

```
User Request + Context
      ↓
MasterOrchestrator.coordinate_operation()
      ↓
Stage 2: IntentRouter classifies → selects template
      ↓
Stage 3: KnowledgeSynthesisEngine.synthesize_unified_context()
      ├─ ARCHITECT mode:
      │   - cortex-registry/_cortex-master/knowledge/ (45+ YAMLs)
      │   - CORTEX architecture patterns
      │   - pytest + FastAPI + Playwright
      └─ PRODUCTION mode:
          - company/domains/*.yaml (api-design, security, payment)
          - cortex_brain/onboarded_repos/{repo}_enhanced.json
          - User's tech stack (detected during onboarding)
      ↓
Stage 4: WorkflowComposer executes template WITH resolved knowledge
      ├─ test_framework: {resolved from onboarded profile}
      ├─ component_patterns: {resolved from company domains}
      ├─ security_standards: {resolved from compliance YAMLs}
      └─ deployment_target: {resolved from infrastructure detection}
```

---

## Example: ARCHITECT vs PRODUCTION Resolution

### Template Definition

```yaml
workflow_id: "tdd/api-service"
stages:
  - stage_id: "S1"
    name: "API Implementation"
    steps:
      - step_id: "implement_api"
        name: "Implement API Endpoint"
        orchestrator: "TDDOrchestrator"
        parameters:
          test_framework: "{test_framework}"
          api_style: "{api_style}"
          auth_pattern: "{auth_pattern}"
```

### ARCHITECT Mode Resolution

**Context**: `.cortex/` directory exists

**Knowledge Sources**:
- `cortex-registry/_cortex-master/knowledge/api-design.yaml`
- `cortex-registry/_cortex-master/knowledge/tdd-best-practices.yaml`

**Resolved Parameters**:
```yaml
test_framework: "pytest"
api_style: "FastAPI + MCP endpoints"
auth_pattern: "MCP authentication"
```

**Generated Code**:
```python
# tests/test_api.py
import pytest
from cortex.mcp.client import MCPClient

@pytest.mark.asyncio
async def test_api_endpoint():
    client = MCPClient()
    response = await client.call("endpoint_name")
    assert response.status == 200
```

### PRODUCTION Mode Resolution

**Context**: No `.cortex/` directory, onboarded repo profile exists

**Knowledge Sources**:
- `company/domains/api-design-standards.yaml`
- `company/domains/security-standards.yaml`
- `cortex_brain/onboarded_repos/user_repo_enhanced.json`

**Resolved Parameters**:
```yaml
test_framework: "Jest"  # From onboarded profile
api_style: "RESTful with pagination"  # From company API design standards
auth_pattern: "OAuth2 with PKCE"  # From company security standards
```

**Generated Code**:
```javascript
// tests/api.test.js
import { apiClient } from './client';

describe('API Endpoint', () => {
  it('should return 200 with valid OAuth2 token', async () => {
    const response = await apiClient.get('/endpoint', {
      headers: { Authorization: `Bearer ${token}` }
    });
    expect(response.status).toBe(200);
  });
});
```

---

## MCP Tool Integration

### cortex_workflow Tool

All template operations route through the `cortex_workflow` MCP tool:

```python
# Usage via MCP
result = await mcp_client.call_tool(
    "cortex_workflow",
    {
        "operation": "execute",
        "template_id": "tdd/api-service",
        "context": {
            "feature": "user authentication",
            "files": ["src/auth/"]
        }
    }
)
```

### Monitoring Operation

```python
# Monitor workflow progress
status = await mcp_client.call_tool(
    "cortex_workflow",
    {
        "operation": "monitor",
        "workflow_id": "wf-12345"
    }
)
```

---

## Governance Requirements

### CORE Rules Applied

- **CORE-008**: TDD mandatory — tests written before implementation
- **CORE-011**: Type hints on all functions
- **CORE-012**: Google-style docstrings
- **CORE-027**: Audit trail (AC_START → AC_COMPLETE markers)
- **CORE-028**: kebab-case filenames, no SCREAMING_CASE
- **CORE-035**: Single canonical implementation (no duplication)
- **CORE-049**: Silent autonomous execution (no mid-execution prompts)

### Enforcement

- EnforcementOrchestrator validates all template executions
- 7-agent pre-execution gate (Phase 48)
- Convergence gates ensure quality criteria met
- Post-phase deduplication reviews prevent CORE-035 violations

---

## Testing Strategy

### Two-Context Golden Tests

Every template has both:

1. **ARCHITECT Mode Tests**: Verify CORTEX-compliant output
2. **PRODUCTION Mode Tests**: Verify domain-compliant output (with mock company knowledge)

### Generic Production Profiles

Tests use generic profiles (no repo-specific names):
- `legacy_dotnet_spa`: ASP.NET + SPA + NUnit
- `modern_nodejs_api`: Node.js + React + Jest
- `python_data_pipeline`: Python + FastAPI + pytest

---

## Autonomous Execution

### CORE-049 Compliance

When user approves a workflow:
- ✅ Execute silently with visual progress bars only
- ✅ No mid-execution prompts
- ✅ ProgressTracker dashboard updates in real-time
- ✅ Checkpoint at 75% token budget
- ✅ Auto-inject epilogues (dedup review + holistic sweep)
- ✅ Report only on completion or error

---

## Related Documentation

- **Phase 100 Specification**: `cortex-registry/_cortex-master/phases/planned/phase-100-workflow-template-library.yaml`
- **Knowledge Synthesis Engine**: `cortex/brain/knowledge/knowledge_synthesis_engine.py`
- **Workflow Composer**: `cortex/orchestrators/workflow/workflow_composer.py`
- **Convergence Neuron**: `cortex/orchestrators/core/convergence_neuron.py`
- **Company Knowledge**: `company/domains/README.md`

---

## Support

For questions or issues:
- **Issue Tracker**: GitHub Issues
- **MCP Tool**: `cortex_total_recall(feature="workflow templates")`
- **Documentation**: `cortex-docs/workflows/`

---

**Author**: Asif Hussain  
**License**: Proprietary  
**Copyright**: © 2026 CORTEX Project
