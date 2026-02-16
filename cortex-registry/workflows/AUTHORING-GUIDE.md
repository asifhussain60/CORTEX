# CORTEX Workflow Template Authoring Guide

**Version:** 1.0 | **Authority:** Phase 100 Stage 6  
**Audience:** Template Authors | **Complexity:** Intermediate

---

## Table of Contents

1. [Introduction](#introduction)
2. [Template Anatomy](#template-anatomy)
3. [Knowledge Placeholders](#knowledge-placeholders)
4. [Convergence Gates](#convergence-gates)
5. [Step-by-Step Creation](#step-by-step-creation)
6. [Testing Your Template](#testing-your-template)
7. [Best Practices](#best-practices)
8. [Common Pitfalls](#common-pitfalls)
9. [Examples](#examples)

---

## Introduction

This guide teaches you how to create **knowledge-parameterized, convergence-gated workflow templates** for CORTEX. Templates you create will automatically adapt to:

- **ARCHITECT mode**: CORTEX internal development
- **PRODUCTION mode**: User's production repositories

The same template resolves differently based on context, thanks to knowledge injection.

---

## Template Anatomy

Every template consists of 3 required files:

```
cortex-registry/workflows/{category}/{template-name}/
├── metadata.yaml              # REQUIRED: Governance + knowledge + convergence
├── workflow.yaml              # REQUIRED: Steps with placeholders
└── README.md                  # REQUIRED: Documentation
```

### Recommended File Sizes

| File | Typical Size | Maximum Size |
|------|--------------|--------------|
| `metadata.yaml` | 50-100 lines | 200 lines |
| `workflow.yaml` | 100-300 lines | 500 lines |
| `README.md` | 200-400 lines | No limit |

---

## Knowledge Placeholders

### What Are Placeholders?

Placeholders are special tokens in your workflow that get replaced with context-specific values:

```yaml
parameters:
  test_framework: "{test_framework}"  # Placeholder
  auth_pattern: "{auth_pattern}"      # Placeholder
```

### Available Placeholders

| Placeholder | Description | ARCHITECT Value | PRODUCTION Value |
|-------------|-------------|-----------------|------------------|
| `{test_framework}` | Test runner | `pytest` | From onboarded profile (Jest/NUnit/etc) |
| `{component_library}` | UI framework | `CORTEX patterns` | React/Angular/Vue |
| `{auth_pattern}` | Authentication | `MCP auth` | OAuth2/SAML/etc |
| `{api_style}` | API design | `FastAPI + MCP` | REST/GraphQL/gRPC |
| `{compliance_standards}` | Compliance | `CORTEX CORE rules` | PCI-DSS/HIPAA/SOX |
| `{deployment_target}` | Deployment | `CORTEX pipeline` | Docker/K8s/Serverless |
| `{database_type}` | Database | `SQLite` | PostgreSQL/MySQL/MongoDB |
| `{logging_framework}` | Logging | `Python logging` | Log4j/Serilog/Winston |

### Creating Custom Placeholders

You can create custom placeholders for your specific template:

```yaml
knowledge_resolution:
  required_placeholders:
    - "{your_custom_placeholder}"
  
  architect_resolution:
    your_custom_placeholder: "CORTEX-specific value"
  
  production_resolution:
    your_custom_placeholder: "From company/domains/your-domain.yaml"
```

**Rules for Custom Placeholders**:
1. Use kebab-case inside braces: `{my-placeholder}`
2. Document in metadata.yaml
3. Provide fallback values
4. Must resolve from knowledge sources (no hardcoding)

### Resolution Sources

Placeholders resolve from these sources (in priority order):

```
1. company/domains/*.yaml (HIGHEST)
   ↓
2. cortex_brain/onboarded_repos/{repo}_enhanced.json
   ↓
3. cortex-registry/_cortex-master/knowledge/ (FALLBACK)
```

### Example: Placeholder Resolution

**Template Definition**:
```yaml
parameters:
  test_framework: "{test_framework}"
```

**ARCHITECT Mode** (`.cortex/` exists):
```yaml
# Resolves from cortex-registry/_cortex-master/knowledge/tdd-best-practices.yaml
test_framework: "pytest"
```

**PRODUCTION Mode** (onboarded repo):
```yaml
# Resolves from cortex_brain/onboarded_repos/user_repo_enhanced.json
# tech_stack.test_framework: "Jest"
test_framework: "Jest"
```

---

## Convergence Gates

### What Are Convergence Gates?

Convergence gates enable **"loop till resolved"** semantics. Steps can retry until success criteria met or max cycles exceeded.

### When to Use Convergence Gates

✅ **Use for**:
- Cleanup operations (deduplication, dead code removal)
- Quality uplift (improve metrics to threshold)
- Security remediation (fix all critical issues)
- Migration (incremental modernization)

❌ **Don't use for**:
- Simple one-shot operations
- File creation (create once, no retry needed)
- Read-only analysis
- User input collection

### Convergence Gate Configuration

```yaml
convergence_gate:
  max_cycles: 10              # REQUIRED: Maximum retry iterations (default: 5)
  
  success_criteria:           # REQUIRED: All must be true to converge
    all_tests_pass: true
    no_regressions: true
    quality_improvement: ">10%"
  
  convergence_predicate: >    # REQUIRED: Python expression evaluated against output
    all_tests_pass and 
    no_regressions and 
    quality_delta > 0.10
  
  scan_function: >            # REQUIRED: What to measure
    run_tests_and_measure_quality
  
  backoff_strategy: "none"    # OPTIONAL: none | linear | exponential
```

### Step State Machine

Steps with convergence gates follow this lifecycle:

```
PENDING
  ↓ (start)
RUNNING
  ↓ (check)
CHECKING ←──────────┐
  ↓                 │
  ├─ PASSED (converged=true, done!)
  │
  ├─ RETRYING (converged=false, cycle < max_cycles)
  │    ↓ (re_execute)
  │    └────────────┘
  │
  └─ FAILED (cycle >= max_cycles)
```

### Example: Deduplication with Convergence

```yaml
- step_id: "remove_duplicates"
  name: "Remove Code Duplication"
  orchestrator: "LENSSynthesis"
  
  convergence_gate:
    max_cycles: 5
    
    success_criteria:
      new_duplicates_count: 0      # Must be EXACTLY zero
    
    convergence_predicate: "new_duplicates_count == 0"
    
    scan_function: "lens_duplicate_scan_delta"
    
    backoff_strategy: "none"       # No delay between retries
```

**What happens**:
1. RUNNING: LENS scans for duplicates, finds 3
2. CHECKING: `new_duplicates_count == 3` → NOT converged
3. RETRYING: Extract shared code (cycle 1)
4. RUNNING: LENS rescans, finds 1 remaining
5. CHECKING: `new_duplicates_count == 1` → NOT converged
6. RETRYING: Extract remaining duplicate (cycle 2)
7. RUNNING: LENS rescans, finds 0
8. CHECKING: `new_duplicates_count == 0` → **PASSED** ✅

### Backoff Strategies

| Strategy | Delay Between Retries | Use When |
|----------|----------------------|----------|
| `none` | 0 seconds | Fast operations (tests, scans) |
| `linear` | `cycle * 2` seconds | Medium operations (builds) |
| `exponential` | `2^cycle` seconds | Expensive operations (deployment) |

---

## Step-by-Step Creation

### Step 1: Choose Template Type and Category

**Decision Tree**:

```
Does your workflow improve code quality?
  YES → Category: quality/
  NO  → Does it implement new features?
          YES → Category: tdd/
          NO  → Does it fix security issues?
                  YES → Category: security/
                  NO  → Does it modernize legacy code?
                          YES → Category: migration/
                          NO  → Does it clean up code?
                                  YES → Category: cleanup/
                                  NO  → Category: review/ or refactor/
```

### Step 2: Create Directory Structure

```bash
# Navigate to workflows directory
cd cortex-registry/workflows

# Create template directory
mkdir -p {category}/{template-name}
cd {category}/{template-name}

# Create required files
touch metadata.yaml workflow.yaml README.md
```

### Step 3: Define metadata.yaml

```yaml
# Basic Information
template_id: "{category}/{template-name}"
name: "Human-Readable Template Name"
version: "1.0"
category: "{category}"
description: |
  Single-sentence description of what this template does.
  Focus on the outcome, not the implementation.

# Knowledge Resolution
knowledge_resolution:
  required_placeholders:
    - "{placeholder1}"
    - "{placeholder2}"
  
  architect_resolution:
    placeholder1: "Value for CORTEX internal dev"
    placeholder2: "Value for CORTEX internal dev"
  
  production_resolution:
    placeholder1: "From company/domains/domain-name.yaml"
    placeholder2: "From cortex_brain/onboarded_repos/{repo}_enhanced.json"

# Convergence Configuration (if using convergence gates)
convergence_config:
  steps_with_gates:
    - step_id: "step_id_from_workflow"
      max_cycles: 5
      success_criteria:
        criterion1: true
      convergence_predicate: "criterion1"
      scan_function: "your_scan_function"

# Governance
governance:
  core_rules:
    - CORE-008  # TDD mandatory (always include)
    - CORE-027  # Audit trail (always include)
    # Add more as needed
  
  approval_required: true      # Require user approval before execution
  auto_checkpoint: true        # Create git checkpoint at stage boundaries
  
  tags:
    - "tdd"
    - "your-tag"
```

### Step 4: Define workflow.yaml

```yaml
workflow_id: "{category}/{template-name}"

stages:
  - stage_id: "S1"
    name: "Stage 1 Name"
    description: "What this stage does"
    
    steps:
      - step_id: "step1"
        name: "Step 1 Name"
        description: "What this step does"
        orchestrator: "TDDOrchestrator"  # Or other orchestrator
        
        parameters:
          param1: "{placeholder1}"
          param2: "static-value"
        
        # Optional: Add convergence gate if step should loop
        convergence_gate:
          max_cycles: 5
          success_criteria:
            tests_pass: true
          convergence_predicate: "tests_pass"
          scan_function: "run_tests"
        
        # Optional: Dependencies on other steps
        dependencies:
          - "other_step_id"
      
      - step_id: "step2"
        name: "Step 2 Name"
        orchestrator: "AnotherOrchestrator"
        parameters:
          param1: "value"
  
  - stage_id: "S2"
    name: "Stage 2 Name"
    description: "What this stage does"
    
    steps:
      - step_id: "step3"
        name: "Step 3 Name"
        orchestrator: "YetAnotherOrchestrator"
        parameters:
          param1: "{placeholder2}"
```

### Step 5: Write README.md

Your template README should include:

```markdown
# {Template Name}

**Category:** {category}  
**Version:** 1.0  
**Status:** Production Ready

## Purpose

What problem does this template solve?

## When to Use

Scenarios where this template is appropriate.

## Knowledge Placeholders

| Placeholder | Description | Resolution Source |
|-------------|-------------|-------------------|
| {placeholder1} | What it controls | Where it comes from |

## Workflow Stages

### Stage 1: {Name}
Description of what happens in this stage.

### Stage 2: {Name}
Description of what happens in this stage.

## Success Criteria

- ✅ Criterion 1
- ✅ Criterion 2

## Example Usage

```bash
# Via MCP tool
cortex_workflow execute --template {category}/{template-name}
```

## Convergence Gates

If using convergence gates, explain:
- Which steps loop
- What success criteria mean
- Typical number of iterations

## Testing

How to test this template (both ARCHITECT and PRODUCTION modes).

## Related Templates

Links to related templates.
```

### Step 6: Validate Template

```bash
# Auto-discovery validation
python -m cortex.orchestrators.workflow.template_registry validate {category}/{template-name}

# Expected output:
# ✅ Template discovered
# ✅ metadata.yaml valid
# ✅ workflow.yaml valid
# ✅ All placeholders declared
# ✅ Convergence gates valid
```

### Step 7: Write Tests

Create test file in `tests/integration/workflows/`:

```python
"""
Tests for {category}/{template-name} template.
"""

import pytest
from cortex.orchestrators.workflow.template_registry import WorkflowTemplateRegistry


class TestYourTemplate:
    """Tests for your template in both contexts."""
    
    def test_architect_mode_resolution(self):
        """Test template resolves correctly in ARCHITECT mode."""
        registry = WorkflowTemplateRegistry()
        template = registry.resolve_template(
            "{category}/{template-name}",
            context={"mode": "architect"}
        )
        
        assert template.parameters["placeholder1"] == "Expected ARCHITECT value"
    
    def test_production_mode_resolution(self):
        """Test template resolves correctly in PRODUCTION mode."""
        registry = WorkflowTemplateRegistry()
        template = registry.resolve_template(
            "{category}/{template-name}",
            context={
                "mode": "production",
                "company_knowledge": mock_company_knowledge,
                "onboarded_profile": mock_onboarded_profile
            }
        )
        
        assert template.parameters["placeholder1"] == "Expected PRODUCTION value"
    
    def test_convergence_gate_success(self):
        """Test convergence gate passes when criteria met."""
        # Test convergence logic
        pass
    
    def test_convergence_gate_max_cycles(self):
        """Test convergence gate fails after max_cycles."""
        # Test max cycles safety limit
        pass
```

### Step 8: Register in Manifest (Optional)

The registry auto-discovers templates, but you can manually regenerate:

```bash
python -m cortex.orchestrators.workflow.template_registry generate-manifest
```

---

## Testing Your Template

### Two-Context Testing Strategy

Every template MUST be tested in both contexts:

#### ARCHITECT Mode Test
```python
def test_architect_mode(self):
    """Verify CORTEX-compliant output."""
    context = {
        "mode": "architect",
        "workspace": "/path/to/CORTEX"
    }
    
    result = execute_template(template_id, context)
    
    # Assert CORTEX patterns used
    assert "pytest" in result.test_framework
    assert "FastAPI" in result.api_style
```

#### PRODUCTION Mode Test
```python
def test_production_mode(self):
    """Verify domain-compliant output."""
    context = {
        "mode": "production",
        "company_knowledge": load_mock_company_knowledge(),
        "onboarded_profile": load_mock_profile("modern_nodejs_api")
    }
    
    result = execute_template(template_id, context)
    
    # Assert user patterns used
    assert "Jest" in result.test_framework
    assert "Express" in result.api_style
```

### Generic Production Profiles

Use these pre-built profiles for testing:

| Profile | Tech Stack | Test Framework |
|---------|-----------|----------------|
| `legacy_dotnet_spa` | ASP.NET + SPA | NUnit + Playwright |
| `modern_nodejs_api` | Node.js + React | Jest + Cypress |
| `python_data_pipeline` | Python + FastAPI | pytest |

```python
def test_generic_profile():
    """Test with generic production profile."""
    context = {
        "mode": "production",
        "onboarded_profile": GENERIC_PROFILES["modern_nodejs_api"]
    }
    
    result = execute_template(template_id, context)
    
    assert result.test_framework == "Jest"
```

---

## Best Practices

### DO ✅

1. **Use Knowledge Placeholders**
   ```yaml
   # Good: Placeholder resolves dynamically
   test_framework: "{test_framework}"
   ```

2. **Declare All Placeholders in metadata.yaml**
   ```yaml
   knowledge_resolution:
     required_placeholders:
       - "{test_framework}"
   ```

3. **Provide Fallback Values**
   ```yaml
   production_resolution:
     test_framework: "From onboarded profile, fallback: pytest"
   ```

4. **Use Convergence Gates for Quality Operations**
   ```yaml
   convergence_gate:
     max_cycles: 5
     success_criteria:
       quality_score: ">80"
   ```

5. **Document Resolution Sources**
   ```yaml
   # metadata.yaml
   production_resolution:
     api_style: "From company/domains/api-design-standards.yaml"
   ```

6. **Test Both Contexts**
   - ARCHITECT mode test
   - PRODUCTION mode test
   - Fallback scenario test

7. **Keep Stages Focused**
   - One stage = one cohesive unit of work
   - 3-7 steps per stage
   - Clear stage boundaries

8. **Use Descriptive Names**
   ```yaml
   # Good
   - step_id: "implement_auth_endpoint"
     name: "Implement Authentication Endpoint"
   
   # Bad
   - step_id: "step1"
     name: "Step 1"
   ```

### DON'T ❌

1. **Hardcode Framework-Specific Values**
   ```yaml
   # Bad: Hardcoded
   test_framework: "pytest"
   
   # Good: Placeholder
   test_framework: "{test_framework}"
   ```

2. **Use Convergence Gates for One-Shot Operations**
   ```yaml
   # Bad: File creation doesn't need convergence
   - step_id: "create_file"
     convergence_gate:
       max_cycles: 5  # Unnecessary!
   ```

3. **Forget Fallback Values**
   ```yaml
   # Bad: No fallback
   production_resolution:
     custom_value: "From company/domains/"  # What if missing?
   
   # Good: With fallback
   production_resolution:
     custom_value: "From company/domains/, fallback: sensible-default"
   ```

4. **Create CORTEX-Specific Production Templates**
   ```yaml
   # Bad: CORTEX patterns in PRODUCTION mode
   production_resolution:
     component_library: "CORTEX orchestrators"  # User doesn't have these!
   
   # Good: Generic patterns
   production_resolution:
     component_library: "From onboarded profile (React/Angular/Vue)"
   ```

5. **Exceed max_cycles Safety Limits**
   ```yaml
   # Bad: Too high
   max_cycles: 100  # Infinite loop risk!
   
   # Good: Reasonable limit
   max_cycles: 10   # Will fail after 10 retries
   ```

6. **Mix Concerns in Single Step**
   ```yaml
   # Bad: Too much in one step
   - step_id: "implement_and_deploy_and_test"
   
   # Good: Separate steps
   - step_id: "implement"
   - step_id: "test"
   - step_id: "deploy"
   ```

---

## Common Pitfalls

### Pitfall 1: Placeholder Not Resolving

**Problem**:
```yaml
# Template uses placeholder
test_framework: "{test_framework}"

# But metadata.yaml doesn't declare it
knowledge_resolution:
  required_placeholders: []  # Missing!
```

**Solution**:
```yaml
knowledge_resolution:
  required_placeholders:
    - "{test_framework}"
```

### Pitfall 2: Convergence Gate Never Converges

**Problem**:
```yaml
convergence_gate:
  success_criteria:
    quality_score: ">95"  # Too aggressive!
  convergence_predicate: "quality_score > 95"
```

**Solution**:
```yaml
convergence_gate:
  max_cycles: 10          # Safety limit
  success_criteria:
    quality_score: ">80"  # Realistic threshold
  convergence_predicate: "quality_score > 80"
```

### Pitfall 3: CORTEX Patterns Leak into PRODUCTION Mode

**Problem**:
```yaml
# Bad: Hardcoded CORTEX pattern
orchestrator: "CORTEXSpecificOrchestrator"
```

**Solution**:
```yaml
# Good: Generic orchestrator
orchestrator: "TDDOrchestrator"  # Available in both modes
```

### Pitfall 4: No Fallback for Missing Knowledge

**Problem**:
```yaml
production_resolution:
  custom_metric: "From company/domains/metrics.yaml"
  # What if file doesn't exist?
```

**Solution**:
```yaml
production_resolution:
  custom_metric: "From company/domains/metrics.yaml, fallback: 80"
```

### Pitfall 5: Convergence Predicate Syntax Error

**Problem**:
```yaml
convergence_predicate: "quality > 80 && tests_pass"  # Wrong syntax!
```

**Solution**:
```yaml
convergence_predicate: "quality > 80 and tests_pass"  # Python syntax
```

---

## Examples

### Example 1: Simple TDD Workflow (No Convergence)

**metadata.yaml**:
```yaml
template_id: "tdd/simple-feature"
name: "Simple Feature TDD"
version: "1.0"
category: "tdd"
description: "Basic RED→GREEN→REFACTOR cycle for new features"

knowledge_resolution:
  required_placeholders:
    - "{test_framework}"
  
  architect_resolution:
    test_framework: "pytest"
  
  production_resolution:
    test_framework: "From onboarded profile, fallback: pytest"

governance:
  core_rules:
    - CORE-008
    - CORE-027
  approval_required: true
```

**workflow.yaml**:
```yaml
workflow_id: "tdd/simple-feature"

stages:
  - stage_id: "S1"
    name: "RED: Write Failing Test"
    steps:
      - step_id: "write_test"
        name: "Write Failing Test"
        orchestrator: "TDDOrchestrator"
        parameters:
          test_framework: "{test_framework}"
          phase: "RED"
  
  - stage_id: "S2"
    name: "GREEN: Make Test Pass"
    steps:
      - step_id: "implement"
        name: "Implement Feature"
        orchestrator: "TDDOrchestrator"
        parameters:
          test_framework: "{test_framework}"
          phase: "GREEN"
        dependencies:
          - "write_test"
  
  - stage_id: "S3"
    name: "REFACTOR: Improve Code"
    steps:
      - step_id: "refactor"
        name: "Refactor Code"
        orchestrator: "RefactoringOrchestrator"
        dependencies:
          - "implement"
```

### Example 2: Quality Uplift with Convergence

**metadata.yaml**:
```yaml
template_id: "quality/code-uplift"
name: "Code Quality Uplift"
version: "1.0"
category: "quality"
description: "Improve code quality metrics with convergence loop"

knowledge_resolution:
  required_placeholders:
    - "{quality_threshold}"
  
  architect_resolution:
    quality_threshold: "85"
  
  production_resolution:
    quality_threshold: "From company/domains/quality-standards.yaml, fallback: 80"

convergence_config:
  steps_with_gates:
    - step_id: "improve_quality"
      max_cycles: 10
      success_criteria:
        quality_score: ">={quality_threshold}"
        all_tests_pass: true
      convergence_predicate: "quality_score >= quality_threshold and all_tests_pass"
      scan_function: "measure_code_quality"

governance:
  core_rules:
    - CORE-008
    - CORE-027
    - CORE-035
  approval_required: true
```

**workflow.yaml**:
```yaml
workflow_id: "quality/code-uplift"

stages:
  - stage_id: "S1"
    name: "Quality Uplift with Convergence"
    steps:
      - step_id: "improve_quality"
        name: "Improve Code Quality"
        orchestrator: "RefactoringOrchestrator"
        parameters:
          quality_threshold: "{quality_threshold}"
        
        convergence_gate:
          max_cycles: 10
          success_criteria:
            quality_score: ">={quality_threshold}"
            all_tests_pass: true
          convergence_predicate: "quality_score >= quality_threshold and all_tests_pass"
          scan_function: "measure_code_quality"
          backoff_strategy: "linear"
```

### Example 3: Multi-Stage Migration

**metadata.yaml**:
```yaml
template_id: "migration/legacy-modernize"
name: "Legacy Code Modernization"
version: "1.0"
category: "migration"
description: "Incrementally modernize legacy code with convergence gates"

knowledge_resolution:
  required_placeholders:
    - "{source_patterns}"
    - "{target_patterns}"
    - "{test_framework}"
  
  architect_resolution:
    source_patterns: "Legacy CORTEX patterns"
    target_patterns: "Modern CORTEX patterns"
    test_framework: "pytest"
  
  production_resolution:
    source_patterns: "From onboarded profile.legacy_patterns"
    target_patterns: "From company/domains/architecture-standards.yaml"
    test_framework: "From onboarded profile, fallback: pytest"

convergence_config:
  steps_with_gates:
    - step_id: "modernize_code"
      max_cycles: 20
      success_criteria:
        legacy_patterns_remaining: 0
        all_tests_pass: true
      convergence_predicate: "legacy_patterns_remaining == 0 and all_tests_pass"
      scan_function: "scan_legacy_patterns"

governance:
  core_rules:
    - CORE-008
    - CORE-027
    - CORE-035
  approval_required: true
```

**workflow.yaml**:
```yaml
workflow_id: "migration/legacy-modernize"

stages:
  - stage_id: "S1"
    name: "Baseline Analysis"
    steps:
      - step_id: "analyze_legacy"
        name: "Analyze Legacy Code"
        orchestrator: "LENSSynthesis"
        parameters:
          source_patterns: "{source_patterns}"
  
  - stage_id: "S2"
    name: "Incremental Modernization"
    steps:
      - step_id: "modernize_code"
        name: "Modernize Code (Convergence Loop)"
        orchestrator: "RefactoringOrchestrator"
        parameters:
          source_patterns: "{source_patterns}"
          target_patterns: "{target_patterns}"
        
        convergence_gate:
          max_cycles: 20
          success_criteria:
            legacy_patterns_remaining: 0
            all_tests_pass: true
          convergence_predicate: "legacy_patterns_remaining == 0 and all_tests_pass"
          scan_function: "scan_legacy_patterns"
          backoff_strategy: "linear"
        
        dependencies:
          - "analyze_legacy"
  
  - stage_id: "S3"
    name: "Validation"
    steps:
      - step_id: "validate_modern"
        name: "Validate Modernized Code"
        orchestrator: "LENSSynthesis"
        parameters:
          target_patterns: "{target_patterns}"
          test_framework: "{test_framework}"
        dependencies:
          - "modernize_code"
```

---

## Conclusion

You now know how to create knowledge-parameterized, convergence-gated workflow templates for CORTEX. Key takeaways:

1. **Use placeholders** for context-specific values
2. **Add convergence gates** for operations that should loop till resolved
3. **Test both contexts** (ARCHITECT and PRODUCTION)
4. **Provide fallbacks** for missing knowledge
5. **Document thoroughly** in README.md

For questions, see:
- Main README: `cortex-registry/workflows/README.md`
- Phase 100 Spec: `cortex-registry/_cortex-master/phases/planned/phase-100-workflow-template-library.yaml`
- MCP Tool: `cortex_total_recall(feature="workflow templates")`

---

**Author**: Asif Hussain  
**License**: Proprietary  
**Copyright**: © 2026 CORTEX Project
