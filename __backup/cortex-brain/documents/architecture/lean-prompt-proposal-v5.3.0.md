# Architecture Proposal: Lean CORTEX.prompt.md with Logic in Master Orchestrator

**Date:** January 5, 2026  
**Version:** 5.3.0  
**Status:** PROPOSED  
**Author:** CORTEX Planning System v5

---

## 🎯 Problem Statement

**Current Architecture (v5.2.0):**
- CORTEX.prompt.md contains 250+ lines with:
  - Routing patterns (duplicates master-orchestrator.yaml)
  - Transformation rules (should be in Python)
  - Execution protocols (should be in Python)
  - Examples (should be in docs)
- copilot-instructions.md contains 150+ lines with:
  - Intent routing table (duplicates patterns)
  - Hand-off protocols (duplicates prompt)
  - Template references (should be in Python)

**Issues:**
1. **Duplication** - Routing patterns in 3 places (prompt, instructions, master-orchestrator.yaml)
2. **Brittleness** - Changing routing requires updating 3 files
3. **Bloat** - Prompt files grow with every orchestrator addition
4. **LLM Load** - GitHub Copilot loads 400+ lines on every request
5. **Logic Drift** - Transformation rules drift between prompt and Python

---

## ✅ Proposed Architecture (v5.3.0)

### Philosophy: "Prompt Focuses on Intent, Python Handles Logic"

```
┌─────────────────────────────────────────────────────────────┐
│  CORTEX.prompt.md (LEAN - 50 lines)                         │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│  1. Strip meta-directives                                    │
│  2. Invoke: python3 -m src.main "{user_request}"            │
│  3. Display output                                           │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Master Orchestrator (Python - ALL LOGIC)                   │
│  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━│
│  1. Parse user request                                       │
│  2. Pattern matching (master-orchestrator.yaml)             │
│  3. Request transformation (add context)                     │
│  4. Route to orchestrator                                    │
│  5. Execute and return results                               │
└─────────────────────────────────────────────────────────────┘
```

---

## 📋 What Moves Where

### From CORTEX.prompt.md → Master Orchestrator (Python)

| Component | Current Location | New Location | Why |
|-----------|------------------|--------------|-----|
| **Routing Patterns** | CORTEX.prompt.md lines 45-60 | master-orchestrator.yaml | Already exists there |
| **Transformation Rules** | CORTEX.prompt.md lines 90-105 | src/orchestrators/request_transformer.py | Logic belongs in Python |
| **Examples** | CORTEX.prompt.md lines 160-200 | docs/orchestrators/request-examples.md | Documentation, not routing |
| **Execution Protocol** | CORTEX.prompt.md lines 115-145 | src/orchestrators/execution_engine.py | Already exists |

### From copilot-instructions.md → Master Orchestrator

| Component | Current Location | New Location | Why |
|-----------|------------------|--------------|-----|
| **Intent Routing Table** | copilot-instructions.md lines 25-50 | master-orchestrator.yaml | Duplication |
| **Hand-Off Protocol** | copilot-instructions.md lines 70-110 | N/A | Remove (no hand-off in v5.2.0) |
| **Template References** | copilot-instructions.md lines 120-140 | src/orchestrators/response_renderer.py | Already exists |

---

## 📐 New File Structure

### 1. CORTEX.prompt.md (v5.3.0 - 50 lines)

```markdown
# 🎯 CORTEX Universal Entry Point

**Version:** 5.3.0 | **Type:** Terminal Execution Bridge

---

## 🚀 How It Works

**Your job is simple:**
1. Strip meta-directives (`Follow instructions in...`, `Use *.prompt.md...`)
2. Invoke Python: `python3 -m src.main "{user_request}" --format markdown`
3. Display output

**That's it.** Python handles everything else.

---

## 🛠️ Examples

**User:** "plan OAuth2 system"  
**You:** `python3 -m src.main "plan OAuth2 system" --format markdown`

**User:** "tdd validate email"  
**You:** `python3 -m src.main "tdd validate email" --format markdown`

**User:** "continue C150 plan"  
**You:** `python3 -m src.main "continue C150 plan" --format markdown`

---

## 📚 References

- **Routing:** `cortex-brain/config/master-orchestrator.yaml`
- **Orchestrators:** `cortex-brain/documents/orchestrators-quick-ref.md`
- **Architecture:** `cortex-brain/documents/cortex-architecture-quick-ref.md`

---

**Version History:**
- v5.0.0: Initial Master Orchestrator integration
- v5.1.0: AUTONOMOUS-ONLY architecture
- v5.2.0: Terminal Execution Bridge
- v5.3.0: **Lean Prompt** - Logic moved to Master Orchestrator
```

**Result:** 50 lines (was 250) - 80% reduction

---

### 2. Master Orchestrator Configuration (Enhanced)

**File:** `cortex-brain/config/master-orchestrator.yaml`

**New Sections:**

```yaml
# Request Transformation Rules (NEW - v5.3.0)
# Applied before orchestrator invocation
transformation_rules:
  # Domain Context Injection
  authentication:
    triggers: ["auth", "login", "oauth", "jwt"]
    inject: "OAuth2, JWT tokens, session management, MFA"
  
  database:
    triggers: ["database", "db", "schema", "table"]
    inject: "Schema design, migrations, indexes, relationships"
  
  api:
    triggers: ["api", "endpoint", "rest", "graphql"]
    inject: "REST/GraphQL design, versioning, rate limiting"
  
  testing:
    triggers: ["test", "tdd", "unittest"]
    inject: "Unit tests, integration tests, E2E tests, coverage"
  
  security:
    triggers: ["security", "secure", "encrypt", "sanitize"]
    inject: "Security best practices, OWASP, encryption, sanitization"

# Implicit Requirements Extraction (NEW - v5.3.0)
implicit_requirements:
  user_auth:
    - "OAuth2 provider integration"
    - "Session management"
    - "Password hashing (bcrypt/argon2)"
    - "MFA/2FA support"
    - "Role-based access control (RBAC)"
  
  api_endpoint:
    - "Input validation"
    - "Error handling"
    - "Rate limiting"
    - "Authentication middleware"
    - "Logging/monitoring"

# Expected Artifacts (NEW - v5.3.0)
artifact_templates:
  planning:
    folders: ["context/", "artifacts/", "reports/", "tracking/"]
    files: ["00-{plan-name}.md", "progress-tracker.json"]
  
  tdd:
    folders: ["tests/"]
    files: ["test_{module}.py", "{module}.py"]
  
  ado:
    folders: ["ado-work-items/"]
    files: ["epic.json", "feature.json", "story-*.json", "task-*.json"]

# Cross-Cutting Concerns (NEW - v5.3.0)
cross_cutting_concerns:
  - concern: "logging"
    applies_to: ["all"]
    requirements: ["Structured logging", "Log levels", "Log rotation"]
  
  - concern: "error_handling"
    applies_to: ["all"]
    requirements: ["Try-catch blocks", "Error messages", "Rollback capability"]
  
  - concern: "validation"
    applies_to: ["api", "database"]
    requirements: ["Input validation", "Schema validation", "Type checking"]
```

---

### 3. Request Transformer (New Python Module)

**File:** `src/orchestrators/request_transformer.py`

```python
"""
Request Transformer - Enriches user requests with context before routing.

Moves transformation logic from CORTEX.prompt.md to Python.
"""

import re
from typing import Dict, List, Any
from pathlib import Path
import yaml


class RequestTransformer:
    """Transform raw user requests into context-rich orchestrator invocations."""
    
    def __init__(self, config_path: str = "cortex-brain/config/master-orchestrator.yaml"):
        """Initialize with transformation rules from config."""
        with open(config_path) as f:
            config = yaml.safe_load(f)
        
        self.transformation_rules = config.get("transformation_rules", {})
        self.implicit_requirements = config.get("implicit_requirements", {})
        self.cross_cutting_concerns = config.get("cross_cutting_concerns", [])
    
    def transform(self, user_request: str, orchestrator_id: str) -> str:
        """
        Transform user request by adding context, requirements, artifacts.
        
        Args:
            user_request: Raw user input
            orchestrator_id: Target orchestrator
        
        Returns:
            Enriched request with injected context
        """
        enriched = user_request
        
        # 1. Inject domain context
        enriched = self._inject_domain_context(enriched)
        
        # 2. Extract and add implicit requirements
        enriched = self._add_implicit_requirements(enriched)
        
        # 3. Specify expected artifacts
        enriched = self._specify_artifacts(enriched, orchestrator_id)
        
        # 4. Add cross-cutting concerns
        enriched = self._add_cross_cutting_concerns(enriched)
        
        return enriched
    
    def _inject_domain_context(self, request: str) -> str:
        """Inject domain-specific context based on triggers."""
        request_lower = request.lower()
        injections = []
        
        for domain, config in self.transformation_rules.items():
            triggers = config.get("triggers", [])
            if any(trigger in request_lower for trigger in triggers):
                injections.append(config["inject"])
        
        if injections:
            return f"{request} with {', '.join(injections)}"
        return request
    
    def _add_implicit_requirements(self, request: str) -> str:
        """Extract and add implicit requirements."""
        request_lower = request.lower()
        requirements = []
        
        for pattern, reqs in self.implicit_requirements.items():
            # Check if pattern matches request
            if any(word in request_lower for word in pattern.split("_")):
                requirements.extend(reqs)
        
        if requirements:
            return f"{request}, including {', '.join(requirements[:3])}"
        return request
    
    def _specify_artifacts(self, request: str, orchestrator_id: str) -> str:
        """Specify expected artifacts based on orchestrator."""
        # Placeholder - would load from config
        return request
    
    def _add_cross_cutting_concerns(self, request: str) -> str:
        """Add cross-cutting concerns (logging, error handling, validation)."""
        concerns = [c["concern"] for c in self.cross_cutting_concerns if "all" in c["applies_to"]]
        if concerns:
            return f"{request} (ensure {', '.join(concerns)})"
        return request
```

---

### 4. Copilot Instructions (Simplified - 50 lines)

**File:** `.github/copilot-instructions.md`

```markdown
# GitHub Copilot Instructions for CORTEX

**Version:** 5.3.0 | **Author:** Asif Hussain

---

## 🎯 Entry Point

**Load:** `.github/prompts/CORTEX.prompt.md` for routing instructions.

**Context Detection:**
- **CORTEX repo** (has `cortex-brain/admin/`): Admin operations enabled
- **User repos**: User operations only

---

## 🚀 How It Works

**Every request follows 3 steps:**

1. **Strip Meta-Directives**
   - Remove: `Follow instructions in...`, `Use *.prompt.md...`
   - Extract core intent

2. **Invoke Python**
   ```bash
   python3 -m src.main "{user_request}" --format markdown
   ```

3. **Display Output**
   - Show terminal output
   - No additional processing

---

## 📚 References

**Master Orchestrator handles:**
- Pattern matching → `cortex-brain/config/master-orchestrator.yaml`
- Request transformation → `src/orchestrators/request_transformer.py`
- Orchestrator routing → `src/orchestrators/master_orchestrator.py`
- Response rendering → `src/orchestrators/response_renderer.py`

**Documentation:**
- Orchestrators → `cortex-brain/documents/orchestrators-quick-ref.md`
- Architecture → `cortex-brain/documents/cortex-architecture-quick-ref.md`
- Brain Protection → `cortex-brain/brain-protection-rules.yaml`

---

**That's it. Python does everything else.**
```

**Result:** 50 lines (was 150) - 67% reduction

---

## 📊 Benefits

### 1. Maintainability
- ✅ Single source of truth (master-orchestrator.yaml)
- ✅ Changes in one place (Python, not 3 files)
- ✅ Version control on logic (Python modules)

### 2. Testability
- ✅ Unit test transformation rules (Python)
- ✅ Integration test routing (Python)
- ✅ No LLM required for testing

### 3. Performance
- ✅ GitHub Copilot loads 100 lines (was 400)
- ✅ Faster prompt parsing
- ✅ Reduced token usage

### 4. Extensibility
- ✅ Add orchestrators without touching prompts
- ✅ Add transformation rules in YAML
- ✅ Plugin architecture for transformers

### 5. Consistency
- ✅ Transformation logic in one place
- ✅ No drift between prompt and Python
- ✅ Easier debugging

---

## 🔄 Migration Path

### Phase 1: Create New Files (No Breaking Changes)
1. Create `src/orchestrators/request_transformer.py`
2. Add transformation sections to `master-orchestrator.yaml`
3. Create `docs/orchestrators/request-examples.md`

### Phase 2: Update Master Orchestrator
1. Integrate `RequestTransformer` into `MasterOrchestrator.handle_request()`
2. Add transformation call before orchestrator execution
3. Test with POC plan

### Phase 3: Slim Down Prompts
1. Create `CORTEX.prompt.md` v5.3.0 (50 lines)
2. Create `copilot-instructions.md` v5.3.0 (50 lines)
3. Archive old versions

### Phase 4: Validate
1. Run POC plan with new architecture
2. Test all orchestrators
3. Update documentation

---

## 📐 File Size Comparison

| File | v5.2.0 | v5.3.0 | Change |
|------|--------|--------|--------|
| **CORTEX.prompt.md** | 250 lines | 50 lines | -80% |
| **copilot-instructions.md** | 150 lines | 50 lines | -67% |
| **master-orchestrator.yaml** | 418 lines | 550 lines | +32% |
| **request_transformer.py** | 0 lines | 200 lines | NEW |
| **Total (Prompt)** | 400 lines | 100 lines | -75% |
| **Total (Python)** | 418 lines | 750 lines | +79% |

**Net Effect:** Logic moves from LLM context to Python (testable, maintainable)

---

## 🎯 Implementation Plan

**Add to C150 Plan as Phase 26:**

```yaml
- number: 26
  name: "Implement Lean Prompt Architecture (v5.3.0)"
  description: "Move logic from CORTEX.prompt.md to Master Orchestrator"
  estimated_hours: 8.0
  python_executor: "scripts/orchestration/implement_lean_prompt_architecture.py"
  
  changes:
    - "Create src/orchestrators/request_transformer.py (200 lines)"
    - "Add transformation sections to master-orchestrator.yaml (+132 lines)"
    - "Create CORTEX.prompt.md v5.3.0 (50 lines, -200 from v5.2.0)"
    - "Create copilot-instructions.md v5.3.0 (50 lines, -100 from v5.2.0)"
    - "Integrate RequestTransformer into MasterOrchestrator"
    - "Create docs/orchestrators/request-examples.md"
  
  validation:
    - "POC plan executes with v5.3.0"
    - "All orchestrators work with transformation"
    - "Prompt files ≤50 lines each"
    - "Transformation logic in Python (100% coverage)"
  
  outputs:
    - "src/orchestrators/request_transformer.py"
    - ".github/prompts/CORTEX.prompt.md (v5.3.0)"
    - ".github/copilot-instructions.md (v5.3.0)"
    - "cortex-brain/config/master-orchestrator.yaml (enhanced)"
    - "reports/lean-prompt-migration.md"
```

---

## ✅ Success Criteria

1. ✅ CORTEX.prompt.md ≤50 lines
2. ✅ copilot-instructions.md ≤50 lines
3. ✅ Transformation logic 100% in Python
4. ✅ POC plan executes successfully
5. ✅ No duplication between files
6. ✅ All tests pass

---

**Recommendation:** Implement Phase 26 to complete the architecture fix. This makes CORTEX truly maintainable and extensible.
