# CORTEX Implants System - Design Document

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Date:** December 15, 2025  
**Status:** ✅ APPROVED FOR IMPLEMENTATION

---

## 🎯 Executive Summary

This design introduces **CORTEX Implants**, a per-repository governance layer that allows organizations to enforce their own coding standards, architectural patterns, and business rules alongside CORTEX's built-in governance. This creates a dual-tier system:

- **CORTEX Tier 0**: Universal governance (TDD, SOLID, file organization)
- **CORTEX Implants**: External governance (coding standards, architectural patterns, business rules)

Each repository in a multi-repo workspace maintains its own `.cortex-implants/` folder with complete isolation from other repositories.

---

## 🏗️ Architecture

### Repository Structure (Per Repo)

```
my-company-repo/
├── .cortex-implants/                  # External governance root
│   ├── governance.yaml                # Repository-specific rules
│   ├── coding-standards.yaml          # Style guides, naming conventions
│   ├── architecture-patterns.yaml     # Required patterns, anti-patterns
│   ├── business-rules.yaml            # Domain-specific validations
│   ├── tech-stack.yaml                # Approved libraries, frameworks
│   ├── security-policy.yaml           # Security requirements
│   ├── README.md                      # Governance documentation
│   └── .cortex-company-version        # Version tracking
├── .github/
│   └── copilot-instructions.md        # Auto-generated (includes company rules)
└── src/
    └── ... (application code)
```

### Multi-Repo Workspace Structure

```
vscode-workspace/
├── cortex-repo/                       # CORTEX itself (has cortex-brain/)
│   └── cortex-brain/                  # CORTEX governance only
├── frontend-repo/                     # User repo #1
│   └── .cortex-implants/              # Frontend-specific rules
├── backend-api-repo/                  # User repo #2
│   └── .cortex-implants/              # API-specific rules
├── mobile-app-repo/                   # User repo #3
│   └── .cortex-implants/              # Mobile-specific rules
├── shared-library-repo/               # User repo #4
│   └── .cortex-implants/              # Library-specific rules
└── ... (6 more repos)
```

**Forbidden Boundary Rule**: Each repo's `.cortex-implants/` folder is invisible to other repos. CORTEX enforces strict repo isolation.

---

## 📁 CORTEX Implants Schema

### 1. `governance.yaml` (Main Configuration)

```yaml
version: '1.0'
company:
  name: "Acme Corporation"
  division: "Engineering"
  contact: "dev-standards@acme.com"

repository:
  name: "frontend-app"
  type: "web-application"  # web-application, api-service, mobile-app, library, microservice
  language: "TypeScript"
  framework: "React"

enforcement:
  level: "STRICT"  # STRICT, MODERATE, ADVISORY
  block_on_violation: true
  require_approval_override: true

rules_enabled:
  - CODING_STANDARDS
  - ARCHITECTURE_PATTERNS
  - BUSINESS_RULES
  - TECH_STACK_VALIDATION
  - SECURITY_POLICY

integration:
  copilot_instructions: true  # Auto-generate copilot-instructions.md
  planning_system: true        # Inject into Planning System
  tdd_workflow: true           # Extend TDD with company tests
  code_review: true            # Pre-commit validation

priority: "HIGH"  # HIGH = company rules override CORTEX when conflict
```

### 2. `coding-standards.yaml`

```yaml
version: '1.0'

naming_conventions:
  components:
    pattern: "PascalCase"
    prefix: ""
    suffix: ""
    example: "UserProfile"
  
  hooks:
    pattern: "camelCase"
    prefix: "use"
    example: "useAuthentication"
  
  functions:
    pattern: "camelCase"
    max_length: 30
    verb_required: true
    example: "getUserById"
  
  constants:
    pattern: "SCREAMING_SNAKE_CASE"
    example: "API_BASE_URL"

file_organization:
  components:
    location: "src/components/"
    structure: "feature-based"  # feature-based, type-based
    max_file_lines: 300
  
  tests:
    location: "src/__tests__/"
    naming: "*.test.ts"
    colocate_with_source: false

code_style:
  max_function_length: 50
  max_params: 4
  max_nesting_depth: 3
  prefer_arrow_functions: true
  require_explicit_return_types: true

imports:
  organize_by: "source"  # source, alphabetical
  max_import_statements: 15
  prefer_absolute_imports: true
  path_alias: "@"

documentation:
  require_jsdoc: true
  require_inline_comments: true
  max_lines_without_comment: 20
```

### 3. `architecture-patterns.yaml`

```yaml
version: '1.0'

required_patterns:
  - name: "Repository Pattern"
    description: "All data access through repository abstraction"
    enforcement: "STRICT"
    validation: "Check for direct DB calls outside repositories/"
  
  - name: "Dependency Injection"
    description: "Use DI container for all service instantiation"
    enforcement: "STRICT"
    validation: "No 'new' keyword for services"
  
  - name: "Feature Modules"
    description: "Features encapsulated in modules with barrel exports"
    enforcement: "MODERATE"
    validation: "Check for index.ts in feature folders"

anti_patterns:
  - name: "God Object"
    description: "Classes with >500 lines or >20 methods"
    severity: "HIGH"
    action: "BLOCK"
  
  - name: "Circular Dependencies"
    description: "Import cycles between modules"
    severity: "CRITICAL"
    action: "BLOCK"
  
  - name: "Magic Numbers"
    description: "Hardcoded numbers without constants"
    severity: "MEDIUM"
    action: "WARN"

layer_boundaries:
  - layer: "presentation"
    allowed_dependencies: ["application", "domain"]
    forbidden_dependencies: ["infrastructure"]
  
  - layer: "application"
    allowed_dependencies: ["domain"]
    forbidden_dependencies: ["presentation", "infrastructure"]
  
  - layer: "domain"
    allowed_dependencies: []
    forbidden_dependencies: ["*"]
  
  - layer: "infrastructure"
    allowed_dependencies: ["domain"]
    forbidden_dependencies: ["presentation", "application"]
```

### 4. `business-rules.yaml`

```yaml
version: '1.0'

domain_validations:
  - rule_id: "USER_EMAIL_VALIDATION"
    description: "All user emails must be corporate domain"
    severity: "HIGH"
    validation_regex: "^[a-zA-Z0-9._%+-]+@acme\\.com$"
    error_message: "Only @acme.com emails allowed"
  
  - rule_id: "CURRENCY_PRECISION"
    description: "All currency fields must use Decimal with 2 places"
    severity: "CRITICAL"
    validation: "Check for float/double in currency fields"
    required_type: "Decimal"

workflow_rules:
  - rule_id: "APPROVAL_WORKFLOW"
    description: "Orders >$10k require manager approval"
    severity: "CRITICAL"
    validation: "Check approval logic in order processing"
  
  - rule_id: "AUDIT_LOGGING"
    description: "All state changes must be audited"
    severity: "HIGH"
    validation: "Check for audit calls after mutations"

compliance:
  - regulation: "GDPR"
    requirements:
      - "User consent before data collection"
      - "Right to be forgotten implementation"
      - "Data export functionality"
    validation: "Check for consent checks, delete endpoints, export APIs"
  
  - regulation: "SOX"
    requirements:
      - "Audit trail for financial transactions"
      - "Segregation of duties"
    validation: "Check audit logs, role-based access"
```

### 5. `tech-stack.yaml`

```yaml
version: '1.0'

approved_libraries:
  frontend:
    - name: "react"
      version: "^18.0.0"
      purpose: "UI framework"
      alternatives_forbidden: ["vue", "angular"]
    
    - name: "axios"
      version: "^1.0.0"
      purpose: "HTTP client"
      alternatives_forbidden: ["fetch", "superagent"]
  
  backend:
    - name: "express"
      version: "^4.18.0"
      purpose: "Web framework"
      alternatives_forbidden: ["koa", "fastify"]

forbidden_libraries:
  - name: "lodash"
    reason: "Use native ES6+ methods instead"
    replacement: "Native Array/Object methods"
  
  - name: "moment"
    reason: "Deprecated, use date-fns"
    replacement: "date-fns"

language_features:
  typescript:
    min_version: "5.0.0"
    strict_mode: true
    no_any: true
    no_explicit_any: true
  
  ecmascript:
    target: "ES2022"
    features_forbidden: ["with", "eval"]
```

### 6. `security-policy.yaml`

```yaml
version: '1.0'

authentication:
  method: "OAuth2 + JWT"
  token_expiry: 3600
  refresh_token_required: true
  mfa_required: true

authorization:
  model: "RBAC"  # RBAC, ABAC, ACL
  default_deny: true
  require_explicit_grants: true

data_protection:
  encryption_at_rest: true
  encryption_in_transit: true
  pii_fields:
    - "email"
    - "phone"
    - "ssn"
    - "credit_card"
  pii_encryption: "AES-256"
  pii_masking_in_logs: true

input_validation:
  sanitize_all_inputs: true
  max_request_size: "10MB"
  rate_limiting: true
  sql_injection_prevention: "parameterized_queries"
  xss_prevention: "content_security_policy"

secrets_management:
  use_vault: true
  no_hardcoded_secrets: true
  rotate_secrets_days: 90
  validation: "Check for credentials in code"
```

---

## 🔄 Integration Points

### 1. Copilot Instructions Auto-Generation

**File**: `src/tier0/cortex_implants_loader.py`

```python
def generate_copilot_instructions(repo_path: Path) -> str:
    """
    Generate .github/copilot-instructions.md from .cortex-implants/.
    
    Combines:
    - CORTEX universal governance
    - Repository-specific rules
    - Repo-specific context
    """
    implants = load_cortex_implants(repo_path)
    cortex_rules = load_cortex_tier0()
    
    return template.render(
        implants=implants,
        cortex=cortex_rules,
        priority=implants.get('priority', 'HIGH')
    )
```

**Generated Output** (`.github/copilot-instructions.md`):

```markdown
# GitHub Copilot Instructions

## 🏢 Company Governance (Priority: HIGH)

### Coding Standards
- Components: PascalCase (e.g., UserProfile)
- Hooks: camelCase with 'use' prefix (e.g., useAuthentication)
- Functions: max 50 lines, max 4 params
- Require explicit return types

### Architecture Patterns
✅ REQUIRED: Repository Pattern, Dependency Injection
❌ FORBIDDEN: God Objects, Circular Dependencies

### Tech Stack
✅ APPROVED: react ^18.0.0, axios ^1.0.0
❌ FORBIDDEN: lodash (use native), moment (use date-fns)

---

## 🧠 CORTEX Universal Governance

### TDD Enforcement
- RED → GREEN → REFACTOR mandatory
- Tests must fail before implementation
...
```

### 2. Planning System Integration

**File**: `src/orchestration_3_0/orchestrators/planning/planning_orchestrator.py`

Add company rules validation to planning workflow:

```python
class PlanningOrchestrator:
    def validate_plan_against_company_rules(self, plan: FeaturePlan) -> ValidationResult:
        """
        Validate feature plan against company tier 0 rules.
        
        Checks:
        - Tech stack compliance
        - Architecture pattern adherence
        - Security policy requirements
        """
        repo_path = self._get_current_repo()
        implants = load_cortex_implants(repo_path)
        
        violations = []
        
        # Check tech stack
        for lib in plan.dependencies:
            if not self._is_approved_library(lib, implants):
                violations.append(f"Forbidden library: {lib}")
        
        # Check architecture patterns
        if not self._follows_required_patterns(plan, implants):
            violations.append("Missing required architecture patterns")
        
        return ValidationResult(
            valid=len(violations) == 0,
            violations=violations
        )
```

### 3. TDD Workflow Extension

**File**: `src/operations/modules/execution/tdd_executor.py`

Extend TDD with company-specific tests:

```python
class TDDExecutor:
    def generate_test_suite(self, feature: str) -> List[TestCase]:
        """
        Generate tests including company business rules.
        """
        cortex_tests = self._generate_cortex_tests(feature)
        
        # Add company-specific tests
        implants = load_cortex_implants()
        company_tests = []
        
        for rule in implants.business_rules:
            company_tests.append(
                self._generate_business_rule_test(rule)
            )
        
        return cortex_tests + company_tests
```

### 4. Repo Boundary Enforcement

**File**: `src/tier0/repo_boundary_enforcer.py`

New module to enforce strict repo isolation:

```python
class RepoBoundaryEnforcer:
    """
    Enforces forbidden boundaries between repositories.
    
    Rules:
    - No cross-repo imports
    - No shared state between repos
    - Each repo's cortex-implants is invisible to others
    """
    
    def validate_operation(self, source_repo: Path, target_path: Path) -> bool:
        """
        Check if operation crosses repo boundary.
        """
        source_root = self._find_repo_root(source_repo)
        target_root = self._find_repo_root(target_path)
        
        if source_root != target_root:
            raise RepoBoundaryViolation(
                f"Cannot access {target_path} from {source_repo}. "
                f"Repos must remain isolated."
            )
        
        return True
```

---

## 🚀 Implementation Plan

### Phase 1: Core Infrastructure (2 days)

**Files to Create:**
1. `src/tier0/cortex_implants_loader.py` - Load implant governance
2. `src/tier0/cortex_implants_validator.py` - Validate against rules
3. `src/tier0/repo_boundary_enforcer.py` - Enforce repo isolation
4. `src/tier0/copilot_instructions_generator.py` - Auto-generate instructions

**Files to Modify:**
1. `src/tier0/governance_engine.py` - Add company tier 0 support
2. `src/tier0/optimized_context_loader.py` - Load company context

### Phase 2: Integration (1 day)

**Files to Modify:**
1. `src/orchestration_3_0/orchestrators/planning/planning_orchestrator.py`
2. `src/operations/modules/execution/tdd_executor.py`
3. `src/operations/modules/validation/planning_rules_validator.py`

### Phase 3: Templates & Documentation (1 day)

**Files to Create:**
1. `cortex-brain/templates/cortex-implants-templates/` - Full template
2. `cortex-brain/documents/guides/cortex-implants-setup-guide.md`
3. `cortex-brain/documents/guides/multi-repo-workspace-guide.md`

### Phase 4: Commands & CLI (1 day)

**Commands to Add:**
- `cortex init implants` - Initialize cortex implants
- `cortex validate company-rules` - Check compliance
- `cortex update copilot-instructions` - Regenerate instructions
- `cortex repo-isolation check` - Verify boundaries

---

## 🎯 Usage Examples

### Example 1: Initialize Company Tier 0

```bash
# In company repo
cd /path/to/my-company-repo
cortex init implants --template web-application

# Creates .company-tier0/ with templates
# Generates .github/copilot-instructions.md
# Updates CORTEX config to recognize repo
```

### Example 2: Validate Code Against Company Rules

```bash
# Run validation
cortex validate company-rules

# Output:
# ✅ Coding standards: PASS
# ✅ Architecture patterns: PASS
# ❌ Tech stack: FAIL
#    - Forbidden library detected: lodash
#    - Recommendation: Use native Array methods
# ✅ Security policy: PASS
# ❌ Business rules: FAIL
#    - Missing audit logging in updateOrder()
```

### Example 3: Multi-Repo Workspace

```bash
# CORTEX detects all repos in workspace
cortex workspace analyze

# Output:
# Repository Inventory:
# 1. cortex-repo (CORTEX core) - cortex-brain/
# 2. frontend-repo (web-app) - .company-tier0/ ✅
# 3. backend-api (api-service) - .company-tier0/ ✅
# 4. mobile-app (mobile-app) - .company-tier0/ ❌ Missing
# 5. shared-lib (library) - .company-tier0/ ✅
# 
# Repo Boundaries: ✅ ENFORCED
# No cross-repo imports detected
```

---

## 🔒 Security Considerations

1. **Immutability**: Company tier 0 rules cannot be bypassed by developers
2. **Version Control**: All changes to `.company-tier0/` require PR approval
3. **Audit Trail**: All rule violations logged to `cortex-brain/metrics/company-violations.jsonl`
4. **Encryption**: Sensitive company rules can be encrypted (future enhancement)

---

## 📊 Success Metrics

- **Adoption**: % of repos with `.company-tier0/`
- **Compliance**: % of code passing company rules
- **Violations**: # of company rule violations per week
- **Developer Satisfaction**: Survey score (1-10)
- **Time Saved**: Hours saved by auto-generated copilot instructions

---

## 🔮 Future Enhancements (v2.0)

1. **Cloud Sync**: Sync company rules from central governance server
2. **Rule Marketplace**: Share/download community company rules
3. **ML-Powered Validation**: AI detects pattern violations
4. **Visual Rule Builder**: GUI for non-technical stakeholders
5. **Multi-Company Support**: Support multiple companies in one workspace

---

## 📚 References

- CORTEX Tier 0: `cortex-brain/brain-protection-rules.yaml`
- Planning System: `cortex-brain/manifests/orchestrators/planning-system-manifest.yaml`
- Truth Sources: `cortex-brain/TRUTH-SOURCES.yaml`

---

**Approval**: Ready for implementation  
**Next Steps**: Create Phase 1 implementation files
