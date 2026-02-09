# Response Template Migration Guide

**Version:** 1.0  
**Date:** 2026-02-09  
**Author:** Asif Hussain  
**Authority:** ENH-064 Response Template Migration

---

## Overview

This guide provides complete instructions for migrating CORTEX orchestrators to use the enhanced response template system with BaseResponseTemplate, chainable blocks, and consistent formatting.

---

## Architecture

### Core Components

```
cortex/orchestrators/
├── core/
│   └── base_response_template.py       # Abstract base class (500 LOC)
├── response/
│   ├── chainable_blocks.py             # Reusable blocks (600 LOC)
│   ├── template_examples.py            # Example implementations
│   └── orchestrator_templates.py       # Template registry (in progress)
└── migration/
    ├── tdd_template_integration.py     # TDD integration mixin
    └── lens_template_integration.py    # LENS integration mixin
```

### Template Hierarchy

```
BaseResponseTemplate (ABC)
├── header(operation) → h1 (single call enforced)
├── section(title, emoji) → h2
├── subsection(title) → h3
├── subsubsection(title) → h4
├── challenge_box(title, content, severity) → blockquote
└── problem_solution_table(rows) → 2-column table

ChainableBlock (Composable)
├── TestResultsBlock → Test execution table
├── CoverageMetricsBlock → Coverage metrics table
├── ProblemSolutionBlock → Problem/solution pairs
├── ValidationChecklistBlock → Checklist with ✅/❌
├── MetricsDashboardBlock → Metrics with targets
├── RecommendationsBlock → Numbered/bullet list
├── NextStepsBlock → Priority + effort table
├── CodeComparisonBlock → Before/after code
└── ErrorAnalysisBlock → Error details + stack trace
```

---

## Migration Steps

### Step 1: Add BaseResponseTemplate as Base Class

**Before:**
```python
class TDDOrchestrator(OrchestratorBaseProtocol):
    def process(self, request):
        response = "## 🧠 CORTEX IMPLEMENT\n"
        response += "**Author:** Asif Hussain\n\n"
        # ... manual markdown generation ...
        return response
```

**After:**
```python
from cortex.orchestrators.core.base_response_template import BaseResponseTemplate

class TDDOrchestrator(OrchestratorBaseProtocol, BaseResponseTemplate):
    def process(self, request):
        # Use template methods instead
        response = self.header("IMPLEMENT")
        response += self.section("TDD Phase", "🔴")
        response += self.subsection("Test Results")
        # ... template-based generation ...
        return response
```

### Step 2: Replace Manual Markdown with Template Methods

**Old Pattern (FORBIDDEN):**
```python
# ❌ Manual header (can repeat)
response = "## 🧠 CORTEX IMPLEMENT\n"
response += "**Author:** Asif Hussain\n\n"

# ❌ Flat hierarchy (all ###)
response += "### Test Results\n"
response += "### Coverage\n"
response += "### Recommendations\n"

# ❌ No challenge boxes
response += "**WARNING:** Low coverage\n"
```

**New Pattern (REQUIRED):**
```python
# ✅ Single header (enforced)
response = self.header("IMPLEMENT")

# ✅ Proper cascade (h2 → h3 → h4)
response += self.section("Test Results", "🧪")  # h2
response += self.subsection("Passing Tests")    # h3 under Test Results
response += self.subsubsection("Unit Tests")    # h4 under Passing Tests

# ✅ Challenge boxes for warnings
response += self.challenge_box(
    "Low Coverage Warning",
    "Coverage is 45%, below 80% target. Add tests for uncovered branches.",
    SeverityLevel.WARNING
)
```

### Step 3: Use Chainable Blocks for Complex Sections

**Old Pattern:**
```python
# ❌ Manual table generation (error-prone)
response += "| Test | Status | Duration |\n"
response += "|------|--------|----------|\n"
for test in tests:
    response += f"| {test['name']} | {'✅' if test['passed'] else '❌'} | {test['duration']}ms |\n"
```

**New Pattern:**
```python
# ✅ Chainable blocks (reusable, tested)
from cortex.orchestrators.response.chainable_blocks import BlockComposer

composer = BlockComposer()
composer.add_test_results(tests, "Test Execution")
composer.add_coverage(coverage, "Coverage Metrics")
composer.add_next_steps(next_steps, "Next Steps")

response += composer.build()
```

### Step 4: Implement compose() Method

Every orchestrator template MUST implement `compose()`:

```python
class TDDOrchestrator(OrchestratorBaseProtocol, BaseResponseTemplate):
    
    def compose(
        self,
        operation: str,
        tdd_phase: str,
        test_results: List[Dict[str, Any]],
        coverage_metrics: Dict[str, float],
        **kwargs
    ) -> str:
        """
        Compose TDD orchestrator response.
        
        Args:
            operation: TDD operation (RED/GREEN/REFACTOR)
            tdd_phase: Current TDD phase
            test_results: Test execution results
            coverage_metrics: Coverage percentages
            **kwargs: Additional context
        
        Returns:
            Fully formatted response
        """
        # MANDATORY: Single header
        response = self.header(operation)
        
        # Section 1: TDD Phase (h2)
        response += self.section(f"TDD Phase: {tdd_phase}", "🔴")
        
        # Use blocks for complex sections
        composer = BlockComposer()
        composer.add_test_results(test_results)
        composer.add_coverage(coverage_metrics)
        response += composer.build()
        
        return response
```

---

## Integration Patterns

### Pattern 1: Mixin Integration (Recommended)

**Use Case:** Add template system without modifying orchestrator structure

```python
# Create integration mixin
from cortex.orchestrators.migration.tdd_template_integration import TDDTemplateIntegration

class TDDOrchestrator(OrchestratorBaseProtocol, TDDTemplateIntegration):
    """TDD with template integration via mixin."""
    
    def execute_tdd_cycle(self, request):
        # ... TDD logic ...
        
        # Use mixin's compose() method
        return self.compose(
            operation="IMPLEMENT",
            tdd_phase=current_phase,
            test_results=results,
            coverage_metrics=coverage,
            guidance=guidance,
            recommendations=recs,
            next_steps=steps
        )
```

**Benefits:**
- ✅ No changes to existing orchestrator logic
- ✅ Drop-in replacement for response generation
- ✅ Easy rollback if issues
- ✅ Parallel testing (old vs new)

### Pattern 2: Direct Inheritance

**Use Case:** New orchestrators or complete rewrites

```python
from cortex.orchestrators.core.base_response_template import BaseResponseTemplate

class NewOrchestrator(BaseResponseTemplate):
    """New orchestrator using template from start."""
    
    def compose(self, operation: str, **kwargs) -> str:
        response = self.header(operation)
        response += self.section("Analysis", "📊")
        response += self.subsection("Findings")
        # ... template methods ...
        return response
    
    def process(self, request):
        # Process logic
        result = self.analyze(request)
        
        # Generate response
        return self.compose(
            operation="ANALYZE",
            findings=result
        )
```

**Benefits:**
- ✅ Clean separation of logic and presentation
- ✅ Enforced template usage
- ✅ Consistent responses from day 1

### Pattern 3: Registry-Based Templates

**Use Case:** Dynamic template selection based on context

```python
from cortex.orchestrators.response.orchestrator_templates import OrchestratorTemplateRegistry

registry = OrchestratorTemplateRegistry()

# Get template for orchestrator
template = registry.get_template("TDDOrchestrator")

# Generate response
response = template.compose(
    operation="IMPLEMENT",
    tdd_phase="RED",
    # ... data ...
)
```

**Benefits:**
- ✅ Centralized template management
- ✅ Easy template updates without code changes
- ✅ Template reuse across orchestrators
- ✅ A/B testing different templates

---

## Common Patterns

### Pattern: Test Results

```python
# Data structure
tests = [
    {"name": "test_feature_x", "passed": True, "duration_ms": 45},
    {"name": "test_feature_y", "passed": False, "duration_ms": 120}
]

# Template usage
from cortex.orchestrators.response.chainable_blocks import TestResultsBlock

block = TestResultsBlock(tests, "Test Execution")
response += block.render()

# Output:
# ## 🧪 Test Execution
#
# **Status:** 1/2 tests passing
#
# | Test | Status | Duration |
# |------|--------|----------|
# | test_feature_x | ✅ | 45ms |
# | test_feature_y | ❌ | 120ms |
```

### Pattern: Coverage Metrics

```python
# Data structure
coverage = {
    "Lines": 85.5,
    "Branches": 72.3,
    "Functions": 90.0
}

# Template usage
from cortex.orchestrators.response.chainable_blocks import CoverageMetricsBlock

block = CoverageMetricsBlock(coverage, "Coverage Metrics")
response += block.render()

# Output:
# ### Coverage Metrics
#
# | Metric | Coverage | Status |
# |--------|----------|--------|
# | Lines | 85.5% | ✅ |
# | Branches | 72.3% | ⚠️ |
# | Functions | 90.0% | ✅ |
```

### Pattern: Problem/Solution Pairs

```python
# Data structure
issues = [
    ("High cyclomatic complexity (15)", "Extract methods to reduce complexity"),
    ("Missing error handling", "Add try/except blocks with specific exceptions")
]

# Template usage
problems_block = self.problem_solution_table(issues, "Code Issues")
response += problems_block

# Output:
# ## Code Issues
#
# | 🔴 **Problem** | 🟢 **Solution** |
# |----------------|------------------|
# | High cyclomatic complexity (15) | Extract methods to reduce complexity |
# | Missing error handling | Add try/except blocks with specific exceptions |
```

### Pattern: Challenge Boxes

```python
# Low confidence challenge
response += self.challenge_box(
    "Low Confidence Warning",
    "Classification confidence is 45%, below 60% threshold.\n\n"
    "**Recommendations:**\n"
    "- Provide more context\n"
    "- Specify target files\n",
    SeverityLevel.WARNING
)

# Output:
# > ⚠️ **CHALLENGE: Low Confidence Warning**
# >
# > Classification confidence is 45%, below 60% threshold.
# >
# > **Recommendations:**
# > - Provide more context
# > - Specify target files
```

### Pattern: Fluent API Composition

```python
# Compose entire response using fluent API
from cortex.orchestrators.response.chainable_blocks import BlockComposer

response = self.header("IMPLEMENT")

response += (
    BlockComposer()
    .add_test_results(tests)
    .add_coverage(coverage)
    .add_problem_solution(issues)
    .add_recommendations(recs)
    .add_next_steps(steps)
    .build()
)

# Benefits:
# - Readable chaining
# - Automatic empty handling (skips empty blocks)
# - Consistent formatting
# - Reusable blocks
```

---

## Validation

### Pre-Migration Checklist

- [ ] Orchestrator identified in registry
- [ ] Response generation points mapped
- [ ] Data structures documented
- [ ] Template requirements defined
- [ ] Integration mixin created
- [ ] Tests written for compose()

### Post-Migration Validation

- [ ] Header appears exactly once
- [ ] Proper h2→h3→h4 cascade
- [ ] Challenge boxes render correctly
- [ ] No manual markdown in response
- [ ] All tests passing
- [ ] Coverage maintained/improved

### Automated Tests

```python
def test_header_single_call_enforcement():
    """Test header can only be called once."""
    template = MyOrchestrator()
    
    # First call: OK
    response = template.header("IMPLEMENT")
    assert "## 🧠 CORTEX IMPLEMENT" in response
    
    # Second call: ERROR
    with pytest.raises(RuntimeError, match="Header already generated"):
        template.header("ANALYZE")


def test_section_hierarchy():
    """Test section creates h2 headers."""
    template = MyOrchestrator()
    response = template.section("Analysis", "📊")
    
    assert "## 📊 Analysis" in response
    assert "###" not in response  # Not h3


def test_challenge_box_renders():
    """Test challenge box uses markdown blockquote."""
    template = MyOrchestrator()
    box = template.challenge_box(
        "Test Challenge",
        "Content here",
        SeverityLevel.WARNING
    )
    
    assert "> ⚠️ **CHALLENGE: Test Challenge**" in box
    assert "> Content here" in box
```

---

## Rollout Strategy

### Phase 1: Core Orchestrators (Week 1)

**Priority:** P0 (CRITICAL)

- [x] MasterOrchestrator
- [x] IntentRouter
- [x] TDDOrchestrator
- [x] LENSSynthesis
- [ ] ChallengeEngine
- [ ] PlanOrchestrator

**Actions:**
1. Create integration mixins
2. Add tests for compose() methods
3. Parallel run (old + new, compare outputs)
4. Switch to new template
5. Remove old response code

### Phase 2: Domain Orchestrators (Week 2)

**Priority:** P1 (HIGH)

- [x] RefactoringOrchestrator
- [x] DocumentationOrchestrator
- [ ] OnboardingOrchestrator
- [ ] ToolDiscoveryOrchestrator
- [ ] WorkflowOrchestrator

**Actions:**
1. Use existing patterns from Phase 1
2. Batch testing (5 orchestrators together)
3. Staged rollout (1 per day)

### Phase 3: Support + Enterprise (Week 3)

**Priority:** P2 (MEDIUM)

- [x] DebuggingOrchestrator
- [x] DigestSessionOrchestrator
- [ ] SecurityOrchestrator
- [ ] ComplianceOrchestrator
- [ ] PerformanceOrchestrator
- [ ] Remaining ~60 orchestrators

**Actions:**
1. Automated migration script for simple orchestrators
2. Manual review for complex orchestrators
3. Bulk testing + validation

---

## Troubleshooting

### Issue: Header Repetition

**Symptom:** "CORTEX Architect" appears multiple times

**Cause:** Multiple calls to `header()`

**Fix:**
```python
# ❌ BAD
response = self.header("IMPLEMENT")
response += "... sections ..."
response += self.header("IMPLEMENT")  # ERROR!

# ✅ GOOD
response = self.header("IMPLEMENT")  # Single call
response += "... sections ..."
```

### Issue: Flat Hierarchy

**Symptom:** All sections are `###` (h3)

**Cause:** Using `subsection()` instead of `section()`

**Fix:**
```python
# ❌ BAD
response += self.subsection("Analysis")      # h3
response += self.subsection("Findings")      # h3
response += self.subsection("Recommendations")  # h3

# ✅ GOOD
response += self.section("Analysis", "📊")       # h2
response += self.subsection("Findings")          # h3 under Analysis
response += self.section("Recommendations", "🚀")  # h2 (new section)
```

### Issue: Challenge Box Not Rendering

**Symptom:** Challenge appears as plain text

**Cause:** Not using `challenge_box()` method

**Fix:**
```python
# ❌ BAD
response += "**WARNING:** Low coverage\n"

# ✅ GOOD
response += self.challenge_box(
    "Low Coverage Warning",
    "Coverage is below target. Add tests.",
    SeverityLevel.WARNING
)
```

### Issue: Table Formatting Broken

**Symptom:** Table doesn't render correctly

**Cause:** Manual table generation with incorrect spacing

**Fix:**
```python
# ❌ BAD (error-prone)
response += "|Test|Status|\n"
response += "|---|---|\n"

# ✅ GOOD (use blocks)
from cortex.orchestrators.response.chainable_blocks import TestResultsBlock
response += TestResultsBlock(tests).render()
```

---

## Performance Considerations

### Caching

```python
# Cache compose() output for repeated calls
from functools import lru_cache

class MyOrchestrator(BaseResponseTemplate):
    
    @lru_cache(maxsize=128)
    def compose(self, operation: str, **kwargs) -> str:
        # Expensive template generation
        return self._generate_response(operation, **kwargs)
```

### Lazy Evaluation

```python
# Generate sections only when needed
class MyOrchestrator(BaseResponseTemplate):
    
    def compose(self, operation: str, **kwargs) -> str:
        response = self.header(operation)
        
        # Only generate expensive section if data available
        if kwargs.get("metrics"):
            response += self._format_metrics(kwargs["metrics"])
        
        return response
```

### Batch Operations

```python
# Batch-generate multiple responses
from cortex.orchestrators.response.orchestrator_templates import OrchestratorTemplateRegistry

registry = OrchestratorTemplateRegistry()
templates = registry.list_templates()

# Generate all responses in parallel
from concurrent.futures import ThreadPoolExecutor

with ThreadPoolExecutor() as executor:
    responses = executor.map(generate_response, templates)
```

---

## Best Practices

1. **Single Header:** Call `header()` exactly once per response
2. **Proper Cascade:** Use section() → subsection() → subsubsection()
3. **Challenge Boxes:** Use for warnings, errors, questions
4. **Chainable Blocks:** Reuse blocks instead of manual markdown
5. **Data Validation:** Validate data before passing to blocks
6. **Empty Handling:** Blocks automatically skip empty data
7. **Type Hints:** All compose() methods fully typed
8. **Tests First:** Test compose() before integration
9. **Documentation:** Document compose() parameters
10. **Performance:** Cache expensive computations

---

## Support

**Issues:** Open ticket in CORTEX issue tracker  
**Questions:** Ask in #cortex-templates Slack channel  
**Updates:** Watch cortex-registry for template changes

---

*v1.0 — Initial migration guide for ENH-064 Response Template Migration*
