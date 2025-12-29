# Cortex Implants Setup Guide

**Version:** 1.0.0 | **Updated:** December 15, 2025

---

## 🎯 What Are Cortex Implants?

**Cortex Implants** are per-repository external governance rules that customize CORTEX behavior without modifying CORTEX code.

**Brain Metaphor:** Like neural implants that modify brain behavior externally, cortex-implants inject company/team-specific rules into CORTEX's decision-making process.

**Use Cases:**
- **Companies:** Enforce corporate coding standards
- **Teams:** Share architectural patterns
- **Individuals:** Personal productivity rules
- **Open Source:** Project-specific conventions

---

## 🚀 Quick Start

### 1. Initialize Implants

```bash
cortex init implants --company "YourCompany" --project "YourProject"
```

This creates `.cortex-implants/` folder with 6 YAML files:
- `governance.yaml` (required)
- `coding-standards.yaml` (optional)
- `architecture-patterns.yaml` (optional)
- `business-rules.yaml` (optional)
- `tech-stack.yaml` (optional)
- `security-policy.yaml` (optional)

### 2. Customize Rules

Edit the YAML files to match your requirements:

```bash
# Open in editor
code .cortex-implants/governance.yaml
```

### 3. Generate Copilot Instructions

```bash
cortex implant update
```

This creates `.github/copilot-instructions.md` combining:
- Your cortex-implants rules
- CORTEX universal governance
- Priority-based ordering (HIGH/MEDIUM/LOW)

### 4. Validate Setup

```bash
cortex implant validate
```

### 5. Check Status

```bash
cortex implant status
```

---

## 📁 Folder Structure

```
your-repo/
├── .cortex-implants/              # Implants folder (per-repo)
│   ├── governance.yaml            # ✅ Required - Basic settings
│   ├── coding-standards.yaml      # Optional - Naming, style, docs
│   ├── architecture-patterns.yaml # Optional - Required/forbidden patterns
│   ├── business-rules.yaml        # Optional - Domain-specific rules
│   ├── tech-stack.yaml            # Optional - Approved/forbidden libraries
│   ├── security-policy.yaml       # Optional - Security requirements
│   └── .cortex-company-version    # Version marker (auto-generated)
├── .github/
│   └── copilot-instructions.md    # Auto-generated (DO NOT EDIT)
└── ...
```

---

## ⚙️ Configuration

### governance.yaml (Required)

```yaml
# Basic Information
company_name: "Your Company"
project_name: "Your Project"
repo_name: "your-repo"
repo_type: "application"  # or: library, service, monorepo
version: "1.0.0"
updated_date: "2025-12-15"

# Description
description: |
  Brief description of your project and its governance requirements.

# Enforcement
enforcement_level: "WARN"  # STRICT, WARN, or ADVISORY
block_on_violation: false  # True = block commits, False = warn only

# Priority (affects copilot-instructions.md order)
priority: "MEDIUM"  # HIGH = override CORTEX, MEDIUM/LOW = merge with CORTEX

# Contact
contact: "team@yourcompany.com"

# Rules to enable (optional sections)
rules_enabled:
  - "CODING_STANDARDS"
  - "ARCHITECTURE_PATTERNS"
  - "TECH_STACK"
  - "BUSINESS_RULES"
  - "SECURITY_POLICY"
```

**Priority Levels:**
- **HIGH:** Company rules override CORTEX rules (appears first in copilot-instructions)
- **MEDIUM:** Balanced mix (CORTEX first, then company)
- **LOW:** CORTEX rules dominant (company rules as suggestions)

**Enforcement Levels:**
- **STRICT:** Block operations on violations
- **WARN:** Log warnings but allow operations
- **ADVISORY:** Informational only

---

### coding-standards.yaml (Optional)

```yaml
naming_conventions:
  classes:
    pattern: "PascalCase"
    example: "UserService"
  functions:
    pattern: "snake_case"
    example: "calculate_total"
  constants:
    pattern: "UPPER_SNAKE_CASE"
    example: "MAX_RETRIES"
  files:
    pattern: "kebab-case"
    example: "user-service.py"

code_style:
  max_line_length: 120
  indent_style: "spaces"
  indent_size: 4
  trailing_whitespace: false
  final_newline: true

documentation_requirements:
  functions_require_docstrings: true
  classes_require_docstrings: true
  modules_require_docstrings: true
  docstring_style: "google"  # or: numpy, sphinx

file_organization:
  max_file_lines: 500
  max_function_lines: 50
  imports_order:
    - "stdlib"
    - "third_party"
    - "local"
```

---

### architecture-patterns.yaml (Optional)

```yaml
required_patterns:
  - pattern: "Repository Pattern"
    description: "Use repository pattern for data access"
    example_path: "src/repositories/"
  
  - pattern: "Dependency Injection"
    description: "Use DI for loose coupling"

forbidden_patterns:
  - pattern: "Singleton (overuse)"
    description: "Avoid singleton except for truly global state"
    reason: "Makes testing difficult"

layer_architecture:
  layers:
    - name: "Presentation"
      path: "src/api/"
      dependencies: ["Application"]
    
    - name: "Application"
      path: "src/services/"
      dependencies: ["Domain", "Infrastructure"]
    
    - name: "Domain"
      path: "src/domain/"
      dependencies: []
    
    - name: "Infrastructure"
      path: "src/infrastructure/"
      dependencies: ["Domain"]

design_principles:
  - "SOLID principles mandatory"
  - "DRY (Don't Repeat Yourself)"
  - "KISS (Keep It Simple)"
  - "Prefer composition over inheritance"
```

---

### tech-stack.yaml (Optional)

```yaml
approved_libraries:
  python:
    - "fastapi>=0.104.0"
    - "pydantic>=2.0.0"
    - "sqlalchemy>=2.0.0"
    - "pytest>=7.4.0"

forbidden_libraries:
  - library: "eval()"
    reason: "Security risk"
  - library: "pickle"
    reason: "Use JSON instead"

version_constraints:
  python: ">=3.11"
  node: ">=18.0.0"

upgrade_policy:
  frequency: "quarterly"
  security_patches: "immediate"
  major_versions: "requires_approval"
```

---

### business-rules.yaml (Optional)

```yaml
validation_rules:
  - rule_id: "BR001"
    description: "Email must be validated before user creation"
    validation: "email_validator.validate(email)"
    test_required: true
  
  - rule_id: "BR002"
    description: "Prices must be non-negative"
    validation: "price >= 0"
    test_required: true

workflow_rules:
  - name: "Order Processing"
    steps:
      - "Validate inventory"
      - "Process payment"
      - "Create shipment"
      - "Send confirmation"

data_constraints:
  - field: "username"
    min_length: 3
    max_length: 30
    pattern: "^[a-zA-Z0-9_]+$"
```

---

### security-policy.yaml (Optional)

```yaml
authentication_required: true
authorization_required: true

data_classification:
  - level: "PUBLIC"
    handling: "No restrictions"
  
  - level: "INTERNAL"
    handling: "Encryption at rest"
  
  - level: "CONFIDENTIAL"
    handling: "Encryption in transit + at rest, audit logging"

encryption_requirements:
  passwords: "bcrypt"
  sensitive_data: "AES-256"
  api_keys: "Environment variables only"

compliance_frameworks:
  - "GDPR"
  - "SOC2"

audit_logging:
  required_events:
    - "User login/logout"
    - "Data access"
    - "Configuration changes"
```

---

## 🔄 Workflow

### Development Workflow

1. **Developer makes changes**
   ```bash
   git checkout -b feature/new-feature
   # Make changes...
   ```

2. **CORTEX validates against implants**
   - Automatically during planning (`plan feature X`)
   - Automatically during execution
   - Shows warnings for violations

3. **Update copilot-instructions if implants changed**
   ```bash
   cortex implant update
   git add .github/copilot-instructions.md
   git commit -m "Update governance"
   ```

### Multi-Repo Workflow

Each repo has its own `.cortex-implants/`:

```
workspace/
├── repo-1/
│   └── .cortex-implants/  # Rules for repo-1
├── repo-2/
│   └── .cortex-implants/  # Rules for repo-2
└── repo-3/
    └── .cortex-implants/  # Rules for repo-3
```

**Isolation Guarantee:** Each repo's implants are invisible to other repos (enforced by `RepoBoundaryEnforcer`).

---

## 🎛️ Priority System

### HIGH Priority (Override CORTEX)

```yaml
priority: "HIGH"
```

**Behavior:**
- Company rules appear **first** in copilot-instructions.md
- Company rules override CORTEX rules on conflicts
- Strict enforcement recommended

**Use When:**
- Regulatory compliance required
- Security policies non-negotiable
- Corporate standards mandatory

### MEDIUM Priority (Balanced)

```yaml
priority: "MEDIUM"
```

**Behavior:**
- CORTEX rules appear first
- Company rules appear second
- Both sets considered equally

**Use When:**
- Team conventions established
- Best practices encouraged
- Some flexibility needed

### LOW Priority (Suggestions)

```yaml
priority: "LOW"
```

**Behavior:**
- CORTEX rules dominant
- Company rules as suggestions/references
- Informational only

**Use When:**
- Personal preferences
- Experimental projects
- Learning environments

---

## 🧪 Testing

### Validate Implants

```bash
# Full validation
cortex implant validate

# Check specific file
cortex implant validate --file governance.yaml
```

### Dry Run

```bash
# See what would be generated without writing
cortex implant update --dry-run
```

---

## 🚨 Troubleshooting

### Implants Not Loading

**Problem:** `cortex implant status` shows "No cortex-implants found"

**Solutions:**
1. Check folder name: Must be `.cortex-implants` (with leading dot)
2. Check location: Must be in repository root
3. Check governance.yaml: Must exist and be valid YAML

### Validation Errors

**Problem:** `cortex implant validate` fails

**Solutions:**
1. Check YAML syntax: Use YAML validator
2. Check required fields: governance.yaml must have company_name, project_name
3. Check file encoding: Must be UTF-8

### Copilot Instructions Not Generated

**Problem:** `.github/copilot-instructions.md` not created

**Solutions:**
1. Ensure implants valid: Run `cortex implant validate` first
2. Check permissions: .github/ folder must be writable
3. Check logs: Look for error messages in terminal

---

## 📚 Examples

### Example 1: Web Application

```yaml
# governance.yaml
company_name: "TechCorp"
project_name: "CustomerPortal"
repo_type: "application"
priority: "HIGH"
enforcement_level: "WARN"

# tech-stack.yaml
approved_libraries:
  python:
    - "django>=4.2"
    - "djangorestframework>=3.14"
forbidden_libraries:
  - library: "flask"
    reason: "Django is company standard"
```

### Example 2: Microservice

```yaml
# governance.yaml
company_name: "CloudCo"
project_name: "PaymentService"
repo_type: "service"
priority: "MEDIUM"

# architecture-patterns.yaml
required_patterns:
  - pattern: "API Gateway"
  - pattern: "Circuit Breaker"
  - pattern: "Event Sourcing"
```

### Example 3: Open Source Library

```yaml
# governance.yaml
company_name: "OpenSource Community"
project_name: "AwesomeLib"
repo_type: "library"
priority: "LOW"
enforcement_level: "ADVISORY"

# coding-standards.yaml
documentation_requirements:
  functions_require_docstrings: true
  docstring_style: "numpy"
```

---

## 🔗 Related Documentation

- [Integration Guide](./cortex-implants-integration-guide.md) - Integrate with orchestrators
- [Examples Gallery](./cortex-implants-examples.md) - Real-world examples
- [System Design](./cortex-implants-system-design.md) - Technical architecture
- [Migration Plan](../planning/CORTEX-IMPLANTS-MIGRATION-PLAN.md) - Implementation phases

---

## 💡 Best Practices

1. **Start Simple:** Begin with governance.yaml only, add others as needed
2. **Version Control:** Commit .cortex-implants/ to Git
3. **Document Changes:** Update implants when governance changes
4. **Team Review:** Get team consensus on rules
5. **Test First:** Validate implants before enforcing
6. **Gradual Rollout:** Start with ADVISORY, move to WARN, then STRICT
7. **Regular Review:** Quarterly review and update rules

---

**Next Steps:** See [Integration Guide](./cortex-implants-integration-guide.md) for orchestrator integration.
