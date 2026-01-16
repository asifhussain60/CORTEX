# FIXES NEEDED - Exact Changes Required

## Status: 63% Complete

The CORTEX architecture is **87% infrastructure ready** but **0% documented in prompts** and **0% populated with templates**.

---

## FIX #1: Update CORTEX.prompt.md

**File:** `.github/prompts/CORTEX.prompt.md`

**What:** Add new section explaining response headers  
**Where:** After "Governance Integration" section (around line 650)  
**Size:** ~150 lines

### Add This Section:

```markdown

---

## Response Header Integration

### Overview

All responses generated must comply with CORTEX response header standards defined in Tier 0.
This ensures consistent branding, copyright attribution, and professional appearance.

### Header Configuration

CORTEX headers are configured in a single source of truth:
```yaml
# cortex-brain/tier0/response-headers.yaml
header:
  template: "## 🧠 CORTEX {operation}"
  
copyright_section:
  template: "**{notice}**"
  
footer:
  template: "**Reference:** {repository} | **License:** {license}"
```

### Response Structure

Every response must follow this structure:

```
[HEADER]
## 🧠 CORTEX {operation}
**Author:** {author} | **Phase:** {phase} | **Orchestrator:** {orchestrator}

[SEPARATOR]
---

[COPYRIGHT]
**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

[SEPARATOR]
---

[CONTENT]
Your actual response content goes here.
This is where you put analysis, recommendations, code, etc.

[SEPARATOR]
---

[FOOTER - Optional]
**Reference:** https://github.com/asifhussain60/CORTEX | **License:** Source-Available
```

### Variables

When rendering headers, you MUST substitute these variables:

| Variable | Example | Source |
|----------|---------|--------|
| {operation} | "Planning Orchestration" | Current operation |
| {author} | "Asif Hussain" | Config: author.name |
| {phase} | "PHASE-13" | Current phase from cortex-master.yaml |
| {orchestrator} | "PlanningOrchestrator" | Active orchestrator |
| {notice} | "Copyright © 2025-2026 Asif Hussain. All rights reserved." | Config: copyright.notice |
| {repository} | "https://github.com/asifhussain60/CORTEX" | Config: author.repository |
| {license} | "Source-Available" | Config: copyright.license |

### Implementation Pattern

When generating responses, follow this pattern:

1. **Load configuration**
   ```
   Source: cortex-brain/tier0/response-headers.yaml
   Loader: HeaderConfigurationManager
   ```

2. **Create injector**
   ```
   Use: ResponseHeaderInjector (composition pattern)
   Wrap: Your template engine or response generator
   ```

3. **Render response**
   ```
   Input: Content + context variables
   Process: Render template with substitutions
   Output: Content wrapped with headers
   ```

4. **Return to user**
   ```
   Result: Complete response with headers and copyright
   ```

### Code Example (Python)

```python
from src.core.response_header_injector import ResponseHeaderInjector
from src.core.response_header_config import HeaderConfigurationManager

# Load configuration
config_manager = HeaderConfigurationManager.get_instance()
config_manager.load_configuration('cortex-brain/tier0/response-headers.yaml')

# Create injector (wrap your response generator)
injector = ResponseHeaderInjector(
    template_engine=your_template_engine,
    config_manager=config_manager
)

# Render with headers
response = injector.render(
    domain_id="planning",
    template_name="recommendations",
    context={
        "operation": "Planning Analysis",
        "phase": "PHASE-13",
        "orchestrator": "PlanningOrchestrator",
        "author": "Asif Hussain",
    }
)

# Response now has headers and copyright
print(response)
```

### Example Output

Here's what a response with headers looks like:

```
## 🧠 CORTEX Planning Analysis
**Author:** Asif Hussain | **Phase:** PHASE-13 | **Orchestrator:** PlanningOrchestrator ✅

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

Based on the holistic context gathered, here are the planning recommendations:

### Recommendation 1: Implementation Strategy
...

### Recommendation 2: Risk Mitigation
...

### Recommendation 3: Documentation
...

---

**Reference:** https://github.com/asifhussain60/CORTEX | **License:** Source-Available
```

### Tier 2 Response Templates

Domain-specific response templates are available in:
```
cortex-brain/tier2/response-templates/
├── governance/        # Governance evaluation responses
├── planning/          # Planning recommendations
├── analysis/          # Analysis reports
└── custom/            # Custom orchestrator responses
```

When rendering domain responses, load templates from these directories.

### Enforcement

**This is a governance requirement (Tier 0):**
- ✅ All responses MUST include header
- ✅ All responses MUST include copyright notice  
- ✅ All responses SHOULD include footer
- ✅ Headers must use correct variables
- ✅ Format must match tier0/response-headers.yaml

**Violation consequences:**
- Brand inconsistency across responses
- Missing attribution for Asif Hussain's work
- Non-compliant with governance requirements

---
```

---

## FIX #2: Update copilot-instruction.md

**File:** `.github/copilot-instruction.md`

**What:** Add new section explaining response format  
**Where:** After "Quality Targets" section (around line 200)  
**Size:** ~100 lines

### Add This Section:

```markdown

## Response Format Standards

### CORTEX Response Headers (Mandatory)

All responses generated must include CORTEX headers and copyright notice
as defined in `cortex-brain/tier0/response-headers.yaml`.

### Header Format

Every response MUST include:

1. **Header Line** (Markdown H2)
   ```
   ## 🧠 CORTEX {operation}
   ```

2. **Attribution Line**
   ```
   **Author:** Asif Hussain | **Phase:** {current_phase} | **Orchestrator:** {orchestrator}
   ```

3. **Separator**
   ```
   ---
   ```

4. **Copyright Notice**
   ```
   **Copyright © 2025-2026 Asif Hussain. All rights reserved.**
   ```

5. **Separator**
   ```
   ---
   ```

6. **Response Content**
   (Your actual response here)

7. **Optional Footer**
   ```
   ---
   
   **Reference:** https://github.com/asifhussain60/CORTEX | **License:** Source-Available
   ```

### Full Example

```markdown
## 🧠 CORTEX Implementation Planning
**Author:** Asif Hussain | **Phase:** PHASE-13 | **Orchestrator:** PlanningOrchestrator ✅

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

### Implementation Overview

Based on the acceptance criteria AC-OB-001-01, here's the implementation plan:

1. **Create observability module**
   - File: `src/infrastructure/observability.py`
   - Purpose: Centralized telemetry collection

2. **Add metrics collection**
   - Implement counter metrics for operations
   - Implement timer metrics for performance

3. **Test coverage**
   - Add 8 unit tests in `tests/unit/test_observability.py`
   - Add 3 integration tests in `tests/integration/test_observability_integration.py`

### Timeline
- Development: 4 hours
- Testing: 2 hours
- Documentation: 1 hour
- Total: 7 hours

---

**Reference:** https://github.com/asifhussain60/CORTEX | **License:** Source-Available
```

### Implementation in Code

When writing Python code that generates responses:

```python
from src.core.response_header_injector import ResponseHeaderInjector
from src.core.response_header_config import HeaderConfigurationManager
from src.core.response_template_engine import ResponseTemplateEngine

class MyOrchestrator:
    def __init__(self):
        # Load header configuration
        self.config_manager = HeaderConfigurationManager.get_instance()
        self.config_manager.load_configuration('cortex-brain/tier0/response-headers.yaml')
        
        # Create header injector
        self.header_injector = ResponseHeaderInjector(
            template_engine=None,  # Or your template engine
            config_manager=self.config_manager
        )
    
    def generate_response(self, content: str) -> str:
        """Generate response with CORTEX headers."""
        context = {
            "operation": "My Operation",
            "phase": "PHASE-13",
            "orchestrator": "MyOrchestrator",
            "author": "Asif Hussain",
        }
        
        # Wrap content with headers
        response_with_headers = self._wrap_with_headers(content, context)
        return response_with_headers
    
    def _wrap_with_headers(self, content: str, context: dict) -> str:
        """Wrap content with CORTEX headers."""
        header = f"""## 🧠 CORTEX {context['operation']}
**Author:** {context['author']} | **Phase:** {context['phase']} | **Orchestrator:** {context['orchestrator']} ✅

---

**Copyright © 2025-2026 Asif Hussain. All rights reserved.**

---

{content}

---

**Reference:** https://github.com/asifhussain60/CORTEX | **License:** Source-Available"""
        
        return header
```

### Configuration Source

All header configuration comes from:
- **Location:** `cortex-brain/tier0/response-headers.yaml`
- **Immutability:** Tier 0 (changes require governance approval)
- **Authority:** Single source of truth for all domains
- **Version:** 1.0 (as of 2026-01-15)

### Template Usage

Domain-specific response templates are in:
- `cortex-brain/tier2/response-templates/governance/`
- `cortex-brain/tier2/response-templates/planning/`
- `cortex-brain/tier2/response-templates/analysis/`
- `cortex-brain/tier2/response-templates/custom/`

Use ResponseTemplateEngine to load and render domain templates.

### Compliance Checklist

When generating a response, verify:
- [ ] Header included: "## 🧠 CORTEX {operation}"
- [ ] Author line included: "**Author:** Asif Hussain"
- [ ] Copyright notice included: "**Copyright © 2025-2026..."
- [ ] Separators present (---)
- [ ] Content properly formatted
- [ ] Footer optional but recommended
- [ ] Variables correctly substituted
- [ ] No hardcoded values except copyright year

---
```

---

## FIX #3: Create Tier 2 Response Templates

**Directory:** `cortex-brain/tier2/response-templates/`

**What:** Create template files for domain-specific responses  
**Files to create:** 5+ templates (20+ for full implementation)

### Template Structure

Each template file should follow this format:

```
[Domain]/[Operation].template
├─ Metadata header (author, AC-ID, version)
├─ Variables section (what needs to be substituted)
├─ Template content
└─ Examples
```

### Create These Files

#### 1. governance/evaluation-result.template

```template
# Governance Evaluation Result

**AC-ID:** {ac_id}
**Rule:** {rule_name}
**Result:** {result_status}
**Details:** {result_details}

## Evaluation Criteria
{evaluation_criteria}

## Compliance Status
{compliance_status}

## Recommendations
{recommendations}

## Next Steps
{next_steps}
```

#### 2. planning/recommendations.template

```template
# Planning Recommendations

**Phase:** {phase}
**Orchestrator:** {orchestrator}
**Priority:** {priority}

## Executive Summary
{summary}

## Recommendations
{recommendations}

## Implementation Strategy
{strategy}

## Risk Assessment
{risk_assessment}

## Timeline
{timeline}

## Resource Requirements
{resources}

## Success Criteria
{success_criteria}
```

#### 3. planning/implementation-plan.template

```template
# Implementation Plan

**AC-ID:** {ac_id}
**Phase:** {phase}
**Status:** {status}
**Owner:** {owner}

## Overview
{overview}

## Phases
{phases}

## Task List
{tasks}

## Dependencies
{dependencies}

## Testing Strategy
{testing_strategy}

## Rollout Plan
{rollout}

## Monitoring
{monitoring}

## Rollback Plan
{rollback}
```

#### 4. analysis/report.template

```template
# Analysis Report

**Date:** {date}
**Author:** {author}
**Scope:** {scope}

## Executive Summary
{summary}

## Analysis
{analysis}

## Findings
{findings}

## Metrics
{metrics}

## Recommendations
{recommendations}

## Conclusion
{conclusion}

## Appendix
{appendix}
```

#### 5. shared/error-response.template

```template
# Error Response

**Error Code:** {error_code}
**Severity:** {severity}
**Timestamp:** {timestamp}

## What Happened
{error_description}

## Root Cause
{root_cause}

## Impact
{impact}

## Resolution Steps
{resolution}

## Escalation
{escalation}

## Contact Support
{contact}
```

### How to Create Templates

1. **Create the directory structure**
   ```bash
   mkdir -p cortex-brain/tier2/response-templates/{governance,planning,analysis,custom,shared}
   ```

2. **Create each template file**
   ```bash
   touch cortex-brain/tier2/response-templates/governance/evaluation-result.template
   touch cortex-brain/tier2/response-templates/planning/recommendations.template
   # ... etc
   ```

3. **Add template content**
   - Copy content from sections above
   - Ensure consistent formatting
   - Document all variables with {curly_braces}

4. **Test template rendering**
   ```python
   from src.core.response_template_engine import ResponseTemplateEngine
   
   engine = ResponseTemplateEngine('cortex-brain/tier2/')
   rendered = engine.render_by_id(
       'governance/evaluation-result',
       {'ac_id': 'AC-OB-001-01', ...}
   )
   ```

---

## Summary: What Needs to Change

| File | Change | Size | Effort | Impact |
|------|--------|------|--------|--------|
| CORTEX.prompt.md | Add Response Headers section | ~150 lines | 1 hour | CRITICAL |
| copilot-instruction.md | Add Response Format Standards section | ~100 lines | 45 min | CRITICAL |
| tier2/response-templates/ | Create 5+ template files | ~300 lines total | 2 hours | HIGH |

**Total Effort:** ~4 hours  
**Blocking PHASE-13:** YES  
**Recommended Timeline:** Today (before PHASE-13 starts)

---

## Verification After Changes

### Test CORTEX.prompt.md Update
- [ ] Check that new section appears after Governance Integration
- [ ] Verify all code examples are valid Python
- [ ] Check that links to tier0/response-headers.yaml are correct
- [ ] Test that ResponseHeaderInjector example compiles

### Test copilot-instruction.md Update
- [ ] Check that new section appears after Quality Targets
- [ ] Verify code examples match orchestrator implementation
- [ ] Check compliance checklist is complete
- [ ] Ensure no duplicate content with CORTEX.prompt.md

### Test Tier 2 Templates
- [ ] Directory structure created
- [ ] All template files present
- [ ] Template syntax is valid
- [ ] Variables are correctly {bracketed}
- [ ] Test rendering with ResponseTemplateEngine

### End-to-End Test
- [ ] Load ResponseHeaderInjector
- [ ] Load template engine
- [ ] Render a response using templates
- [ ] Verify header injection
- [ ] Verify copyright notice
- [ ] Verify footer (if enabled)

---

## Next Steps

1. ✅ Apply Fix #1 (CORTEX.prompt.md)
2. ✅ Apply Fix #2 (copilot-instruction.md)  
3. ✅ Apply Fix #3 (Create templates)
4. 🧪 Run verification tests
5. 📋 Update PHASE-13 readiness status
6. 🚀 Begin PHASE-13 with full header support
