# Custom Response Templates Architecture

**Date:** 2026-01-14  
**Version:** 1.0.0 - DESIGN SPECIFICATION  
**Status:** Ready for Implementation  
**Purpose:** Enable optional custom response templates per orchestrator with automatic fallback to standard template

---

## Executive Summary

CORTEX 7.0 supports **optional custom response templates** for each orchestrator and child orchestrator while maintaining **automatic fallback** to the standard CORTEX 4.0 response template format. This enables:

- ✅ Orchestrators to define custom response formats for domain-specific operations
- ✅ Child orchestrators to override parent templates for specialized output
- ✅ Automatic fallback to standard template if custom template not provided
- ✅ Template inheritance: Child inherits parent's template unless explicitly overridden
- ✅ Responsive to CORTEX 4.0 established patterns (mandatory headers, executive summary format)
- ✅ Clean nested folder structure for all components

---

## Part 1: Response Template System Design

### 1.1 Template Hierarchy

```
BaseResponseTemplate
├─ Standard CORTEX Template (fallback - always available)
│  └─ Used if orchestrator has no custom_template_path
│
├─ Orchestrator Custom Template (optional)
│  └─ If defined: orchestrator.custom_template_path = "path/to/template.yaml"
│  └─ Loaded at orchestrator initialization
│  └─ Must conform to CORTEX 4.0 schema (mandatory_header, executive_summary, etc.)
│
└─ Child Orchestrator Custom Template (optional override)
   └─ Child inherits parent's template by default
   └─ If child.custom_template_path defined: uses own template instead
   └─ Falls back to parent template if child template missing/invalid
   └─ Falls back to standard template if parent has no custom template
```

### 1.2 Template Resolution Algorithm

```
FUNCTION resolve_response_template(orchestrator):
  
  # Step 1: Check if orchestrator has custom template defined
  IF orchestrator.custom_template_path DEFINED:
    template = load_template(orchestrator.custom_template_path)
    IF template VALID:
      RETURN template
    ELSE:
      LOG WARNING("Invalid custom template, falling back to parent")
  
  # Step 2: Check if child orchestrator - try parent template
  IF orchestrator.parent_orchestrator EXISTS:
    parent_template = resolve_response_template(orchestrator.parent)
    IF parent_template != standard_template:
      RETURN parent_template
  
  # Step 3: Use standard CORTEX template (fallback)
  RETURN load_standard_template()
```

### 1.3 Orchestrator Template Metadata

**BaseOrchestrator extended with template support:**

```yaml
metadata:
  name: "TDD Master"
  version: "1.0.0"
  category: "core"
  
  # NEW: Optional custom response template
  custom_template:
    enabled: false  # Set to true to use custom template
    path: "cortex-brain/tier2/response-templates/tdd-master.yaml"
    schema_version: "4.6.0"  # Must match standard schema
    fallback_on_error: true  # Use standard template if custom fails
```

---

## Part 2: Standard CORTEX 4.0 Response Template Schema

### 2.1 Template Structure (From CORTEX 4.0)

All response templates (custom or standard) must conform to:

```yaml
schema_version: '4.6.0'
description: "Response template"

# MANDATORY SECTION 1: Header
mandatory_header:
  enabled: true
  template: |
    ## 🧠 CORTEX {operation_type}
    **Author:** Asif Hussain | **Phase:** {phase} | **Orchestrator:** {orchestrator} ✅
    
    ---
    **Copyright © 2025-2026 Asif Hussain. All rights reserved.**
    
    ---

# MANDATORY SECTION 2: Executive Summary Format
executive_summary:
  enabled: true
  position: 'after_header'
  
  format_rules:
    mandatory:
      - "Start with 3-5 sentence executive summary"
      - "Use bullet points for all lists (max 5 per section)"
      - "Each bullet MUST be on separate line"
      - "NO code snippets unless explicitly requested"
      - "NO narrative prose - declarative statements only"
    
    sections:
      - name: "Outcomes"
        marker: "✅"
        max_bullets: 5
        required: true
      
      - name: "In Progress"
        marker: "⚙️"
        max_bullets: 3
        required: false
      
      - name: "Risks"
        marker: "⚠️"
        max_bullets: 3
        required: false
      
      - name: "Impact"
        marker: "🎯"
        max_bullets: 3
        required: false
      
      - name: "Next Steps"
        marker: "📋"
        max_bullets: 5
        required: true

# OPTIONAL SECTION 3: Domain-Specific Sections
# Custom templates can add additional sections here
custom_sections:
  enabled: true
  examples:
    - name: "Governance Violations"
      marker: "🔴"
      used_by: "GovernanceOrchestrator"
    
    - name: "Test Coverage"
      marker: "📊"
      used_by: "TddMasterOrchestrator"
    
    - name: "Performance Metrics"
      marker: "⚡"
      used_by: "OptimizationOrchestrator"
```

### 2.2 Custom Template Example (TDD Master)

File: `cortex-brain/tier2/response-templates/tdd-master.yaml`

```yaml
schema_version: '4.6.0'
orchestrator: "TddMasterOrchestrator"
description: "Custom template for TDD Master with test coverage metrics"

mandatory_header:
  enabled: true
  # Inherits standard header format

executive_summary:
  enabled: true
  sections:
    - name: "Outcomes"
      marker: "✅"
      max_bullets: 5
      required: true
    
    - name: "In Progress"
      marker: "⚙️"
      max_bullets: 3
      required: false
    
    - name: "Risks"
      marker: "⚠️"
      max_bullets: 3
      required: false

# NEW: Custom sections for TDD
custom_sections:
  enabled: true
  sections:
    - name: "Test Results"
      marker: "📊"
      required: true
      fields:
        - "Unit Tests: X/Y passed"
        - "Integration Tests: A/B passed"
        - "Coverage: Z%"
      format: |
        📊 TEST RESULTS
        
        • Unit Tests: {unit_passed}/{unit_total} passed
        • Integration Tests: {int_passed}/{int_total} passed
        • Coverage: {coverage}%
    
    - name: "Next Steps"
      marker: "📋"
      required: true
```

---

## Part 3: Folder Structure Design

### 3.1 Clean Nested Organization

```
CORTEX/
├── cortex-brain/
│   ├── tier0/                          # Immutable CORTEX core
│   │   └── governance/
│   │       └── core-rules.yaml
│   │
│   ├── tier1/                          # Active state (mutable)
│   │   ├── tracking/
│   │   │   └── progress-tracker.json
│   │   ├── acceptance-criteria/
│   │   │   └── AC-INDEX.yaml
│   │   └── governance/
│   │       └── business-rules/         (domain-organized)
│   │
│   ├── tier2/                          # Engineering practices & response templates
│   │   ├── response-templates/         ⭐ NEW - Consolidated here
│   │   │   ├── _schema/
│   │   │   │   └── standard-schema.yaml
│   │   │   ├── core/
│   │   │   │   ├── master-orch.yaml
│   │   │   │   ├── tdd-master.yaml
│   │   │   │   ├── planning-orch.yaml
│   │   │   │   └── governance-orch.yaml
│   │   │   ├── domain/
│   │   │   │   ├── ado-orch.yaml
│   │   │   │   ├── vacuum-orch.yaml
│   │   │   │   └── investigation-orch.yaml
│   │   │   └── custom/                 (user-defined orchestrators)
│   │   │       └── .gitkeep
│   │   │
│   │   ├── engineering-standards/
│   │   │   ├── code-quality.yaml
│   │   │   ├── testing.yaml
│   │   │   └── security.yaml
│   │   │
│   │   └── configuration/
│   │       ├── core-config.yaml
│   │       └── environment.yaml
│   │
│   ├── tier3/                          # Knowledge patterns (learned)
│   │   └── knowledge-patterns/
│   │       └── implementation-patterns.yaml
│   │
│   ├── cx6-plan/                       # Planning & roadmap
│   │   └── viewer/
│   │       └── plan-viewer-data.json
│   │
│   ├── documents/                      # Generated documentation
│   │   ├── architecture/
│   │   ├── governance/
│   │   └── roadmap/
│   │
│   └── audit-logs/                     # Operational logs
│
├── src/                                # Source code (clean organization)
│   ├── orchestrators/
│   │   ├── core/                       ⭐ NEW - Organized by tier
│   │   │   ├── base-orchestrator.py
│   │   │   ├── master-orch.py
│   │   │   ├── tdd-master-orch.py
│   │   │   ├── planning-orch.py
│   │   │   ├── governance-orch.py
│   │   │   └── evidence-orch.py
│   │   │
│   │   ├── domain/                     (domain-specific)
│   │   │   ├── ado-orch.py
│   │   │   ├── vacuum-orch.py
│   │   │   ├── investigation-orch.py
│   │   │   └── sanitization-orch.py
│   │   │
│   │   ├── custom/                     (user-defined, isolated)
│   │   │   └── .gitkeep
│   │   │
│   │   ├── middleware/                 (request/response processing)
│   │   │   ├── governance-check.py
│   │   │   ├── execution-guard.py
│   │   │   └── audit-logger.py
│   │   │
│   │   ├── registry/                   ⭐ NEW - Discovery & registration
│   │   │   ├── orchestrator-registry.py
│   │   │   ├── template-registry.py
│   │   │   └── dependency-resolver.py
│   │   │
│   │   └── response/                   ⭐ NEW - Response handling
│   │       ├── response-renderer.py
│   │       ├── template-resolver.py
│   │       └── response-formatter.py
│   │
│   ├── infrastructure/
│   │   ├── audit-logger/               (audit infrastructure)
│   │   │   ├── logger.py
│   │   │   ├── schema.py
│   │   │   └── queries.py
│   │   │
│   │   ├── governance/                 (governance system)
│   │   │   ├── registry.py
│   │   │   ├── evaluator.py
│   │   │   └── middleware.py
│   │   │
│   │   ├── state/                      (state management)
│   │   │   ├── manager.py
│   │   │   ├── persistence.py
│   │   │   └── lifecycle.py
│   │   │
│   │   └── execution/                  (execution types)
│   │       ├── request.py
│   │       ├── result.py
│   │       └── context.py
│   │
│   ├── mcp/                            (Model Context Protocol)
│   │   ├── tools/
│   │   │   ├── governance-tools.py
│   │   │   ├── audit-tools.py
│   │   │   ├── state-tools.py
│   │   │   ├── evidence-tools.py
│   │   │   └── orchestrator-tools.py
│   │   │
│   │   └── server.py
│   │
│   └── utils/                          (shared utilities)
│       ├── pathlib.py                  (cross-platform paths)
│       ├── yaml-loader.py
│       └── validation.py
│
├── tests/                              ⭐ NEW - Test organization by layer
│   ├── unit/
│   │   ├── test_orchestrators.py
│   │   ├── test_templates.py
│   │   ├── test_governance.py
│   │   └── test_infrastructure.py
│   │
│   ├── integration/
│   │   ├── test_orch_integration.py
│   │   ├── test_template_resolution.py
│   │   └── test_governance_enforcement.py
│   │
│   ├── fixtures/
│   │   ├── orchestrator-fixtures.py
│   │   ├── template-fixtures.yaml
│   │   └── context-fixtures.py
│   │
│   └── conftest.py
│
├── scripts/                            ⭐ NEW - Utility scripts organized
│   ├── admin/
│   │   ├── migrate-folder-structure.py
│   │   └── validate-ssot.py
│   │
│   ├── generate/
│   │   ├── gen-template-index.py
│   │   └── gen-orch-registry.py
│   │
│   └── tools/
│       └── get-ac-title.sh
│
└── SSOT/
    ├── roadmap/                        ⭐ ALL CONSOLIDATION HERE
    │   ├── 00-consolidation-summary.md
    │   ├── consolidated-requirements.md
    │   ├── framework-arch-spec.md
    │   ├── implementation-roadmap.md
    │   ├── prod-readiness-analysis.md
    │   ├── custom-response-templates.md ⭐ NEW
    │   ├── folder-structure-design.md ⭐ NEW
    │   └── README.md
    │
    ├── quick-reference.md              (REFERENCE ONLY - not consolidated yet)
    ├── README.md                       (REFERENCE ONLY)
    └── DOCUMENT-INDEX.md               (REFERENCE ONLY)
```

### 3.2 File Naming Conventions

**All files follow kebab-case, max 25 characters:**

✅ Good examples:
- `master-orchestrator.py` (20 chars)
- `response-template.yaml` (22 chars)
- `test-tdd-master.py` (18 chars)
- `governance-registry.py` (21 chars)

❌ Bad examples:
- `MasterOrchestrator.py` (PascalCase - NO)
- `master_orchestrator.py` (snake_case - NO, use kebab)
- `base_response_template_renderer_with_cache.py` (too long)

---

## Part 4: Implementation Sequence

### Phase 1: Infrastructure (Week 1)

1. Create base response template infrastructure
   - Standard template loader
   - Template validator
   - Template schema validation

2. Create orchestrator registry
   - Load custom template paths from orchestrator metadata
   - Template resolution logic
   - Fallback mechanism

3. Create response renderer
   - Render responses using resolved template
   - Enforce mandatory sections
   - Format validation

### Phase 2: Integration (Week 2)

1. Integrate custom templates into BaseOrchestrator
   - Add custom_template_path to metadata
   - Update orchestrator initialization
   - Add template resolution to response generation

2. Migrate core orchestrators
   - TDD Master template
   - Planning template
   - Governance template
   - Evidence template

3. MCP tool integration
   - Governance tools use standard template
   - Audit tools use standard template
   - Custom template inspection tools

### Phase 3: Safety & Migration (Week 3)

1. Implement template validation
   - Schema validation on load
   - Custom template testing
   - Fallback testing

2. Implement folder migration
   - Move files to new nested structure
   - Update all imports
   - Validate no files lost

3. Cross-platform testing
   - Test on Windows + macOS
   - Path resolution verification
   - Template loading verification

---

## Part 5: Usage Examples

### 5.1 Using Standard Template (Default)

```python
class MyOrchestrator(BaseOrchestrator):
    def get_metadata(self):
        return OrchestratorMetadata(
            name="My Orchestrator",
            version="1.0.0",
            category="custom",
            # custom_template NOT defined → uses standard template
        )
    
    def execute(self, request):
        # ... implementation ...
        result = ExecutionResult(success=True, outcome="Task completed")
        return self.render_response(result)  # Uses standard CORTEX template
```

### 5.2 Using Custom Template

```python
class TddMasterOrchestrator(BaseOrchestrator):
    def get_metadata(self):
        return OrchestratorMetadata(
            name="TDD Master",
            version="1.0.0",
            category="core",
            custom_template=CustomTemplateConfig(
                enabled=True,
                path="cortex-brain/tier2/response-templates/tdd-master.yaml",
                schema_version="4.6.0",
                fallback_on_error=True
            )
        )
    
    def execute(self, request):
        # ... test execution ...
        result = ExecutionResult(
            success=True,
            outcome="Tests passed",
            metadata={
                "unit_passed": 45,
                "unit_total": 50,
                "coverage": "92%"
            }
        )
        return self.render_response(result)  # Uses tdd-master.yaml template
```

### 5.3 Child Orchestrator Inheritance

```python
class StripePaymentOrchestrator(BaseOrchestrator):
    parent: PaymentOrchestrator  # Parent orchestrator reference
    
    def get_metadata(self):
        return OrchestratorMetadata(
            name="Stripe Payment",
            version="1.0.0",
            category="domain",
            # custom_template NOT defined
            # → inherits parent's template
            # → if parent has no custom: uses standard template
        )
```

---

## Part 6: Acceptance Criteria

### AC-TEMPLATE-001: Custom Response Template System
- [ ] BaseOrchestrator supports optional custom_template_path
- [ ] TemplateResolver implements fallback chain correctly
- [ ] Child orchestrators inherit parent templates
- [ ] Standard template always available as fallback
- [ ] Invalid custom templates don't break system (logged, fallback)
- [ ] Custom template schema validates against CORTEX 4.0 schema

### AC-TEMPLATE-002: Response Template Folder Structure
- [ ] All templates in cortex-brain/tier2/response-templates/
- [ ] Sub-folders: _schema, core, domain, custom
- [ ] All files follow kebab-case, max 25 chars
- [ ] Standard schema documented in _schema/standard-schema.yaml
- [ ] Example templates for core orchestrators provided

### AC-FOLDER-001: Nested Folder Reorganization
- [ ] All source code organized in cortex-brain/ + src/
- [ ] No root-level .md files (consolidated into SSOT/roadmap/)
- [ ] orchestrators/core/, orchestrators/domain/, orchestrators/custom/
- [ ] middleware/, registry/, response/ folders created
- [ ] All imports updated to new paths
- [ ] No files lost in migration

### AC-FOLDER-002: Cross-Platform Path Portability
- [ ] All paths use pathlib.Path (no hardcoded /Users/ or C:\\)
- [ ] Tests pass on Windows + macOS + Linux
- [ ] CORTEX-005 enforcement verified

---

## Part 7: Success Criteria

| Criterion | Target | Verification |
|-----------|--------|--------------|
| **Custom templates work** | 5/5 core orchestrators have custom templates | Test: render_response() returns correct template |
| **Fallback works** | 100% of calls without custom template fallback to standard | Test: TemplateResolver returns standard when custom unavailable |
| **No file loss** | All source files present in new structure | Checksum verification, git diff review |
| **Path portability** | Tests pass on Windows + macOS + Linux | CI/CD runs on all 3 platforms |
| **Documentation** | All new components documented | tier2/response-templates/ fully documented |
| **SSOT consolidation** | 18 root files deleted, all content in roadmap/ | File count verification |
| **Code coverage** | ≥95% new code coverage | pytest --cov=src/orchestrators/response/ |

---

## Part 8: Risks & Mitigations

| Risk | Mitigation | Week |
|------|-----------|------|
| Custom template YAML invalid | Schema validation + fallback to standard | Phase 1 |
| Missing custom template file | Fallback to standard immediately | Phase 1 |
| Import path breaks during migration | Comprehensive import update, dry-run first | Phase 3 |
| Cross-platform path issues | Use pathlib.Path everywhere, test on all platforms | Phase 3 |
| Performance regression | Templates cached, <1ms resolution | Phase 2 |
| Orchestrator confusion | Clear documentation + examples | Phase 2 |

---

**Status:** READY FOR IMPLEMENTATION ✅

This design enables optional customization while maintaining CORTEX 4.0 standards and provides clean folder organization for production-grade deployment.
