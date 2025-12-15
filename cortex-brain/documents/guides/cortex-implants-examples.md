# Cortex Implants Examples Gallery

**Version:** 1.0.0 | **Updated:** December 15, 2025

---

## 🎯 Real-World Examples

This gallery shows complete cortex-implants configurations for different scenarios.

---

## Example 1: Enterprise Web Application

**Scenario:** Large company with strict coding standards and security requirements.

### Directory Structure

```
ecommerce-portal/
├── .cortex-implants/
│   ├── governance.yaml
│   ├── coding-standards.yaml
│   ├── architecture-patterns.yaml
│   ├── tech-stack.yaml
│   └── security-policy.yaml
└── src/
```

### governance.yaml

```yaml
company_name: "TechCorp International"
project_name: "E-Commerce Portal"
repo_name: "ecommerce-portal"
repo_type: "application"
version: "2.1.0"
updated_date: "2025-12-15"

description: |
  Customer-facing e-commerce platform with PCI DSS compliance.
  Handles sensitive payment and customer data.

enforcement_level: "STRICT"
block_on_violation: true
priority: "HIGH"
contact: "platform-team@techcorp.com"

rules_enabled:
  - "CODING_STANDARDS"
  - "ARCHITECTURE_PATTERNS"
  - "TECH_STACK"
  - "SECURITY_POLICY"
```

### tech-stack.yaml

```yaml
approved_libraries:
  python:
    - "django>=4.2,<5.0"
    - "djangorestframework>=3.14"
    - "celery>=5.3"
    - "redis>=5.0"
    - "psycopg2-binary>=2.9"
    - "stripe>=7.0"

forbidden_libraries:
  - library: "eval()"
    reason: "Security vulnerability"
  - library: "pickle"
    reason: "Use JSON for serialization"
  - library: "flask"
    reason: "Django is company standard"

version_constraints:
  python: "==3.11"
  node: ">=18.0.0"

upgrade_policy:
  frequency: "quarterly"
  security_patches: "immediate"
  major_versions: "requires_approval"
```

### security-policy.yaml

```yaml
authentication_required: true
authorization_required: true

data_classification:
  - level: "PUBLIC"
    handling: "No restrictions"
  
  - level: "CONFIDENTIAL"
    handling: "Encryption at rest and in transit, audit logging"
    examples: ["customer_email", "shipping_address"]
  
  - level: "SENSITIVE"
    handling: "PCI DSS Level 1 compliance required"
    examples: ["credit_card", "payment_info"]

encryption_requirements:
  passwords: "Argon2"
  api_keys: "AWS Secrets Manager"
  payment_data: "Stripe-managed encryption"

compliance_frameworks:
  - "PCI DSS Level 1"
  - "GDPR"
  - "SOC2 Type 2"

audit_logging:
  required_events:
    - "User authentication"
    - "Payment processing"
    - "Data access (customer PII)"
    - "Admin operations"
  retention_period: "7_years"
```

---

## Example 2: Microservice API

**Scenario:** Cloud-native microservice with event-driven architecture.

### governance.yaml

```yaml
company_name: "CloudServices Inc"
project_name: "Payment Processing Service"
repo_name: "payment-service"
repo_type: "service"
version: "1.0.0"
updated_date: "2025-12-15"

description: |
  Payment processing microservice using event sourcing.
  Part of larger microservices ecosystem.

enforcement_level: "WARN"
block_on_violation: false
priority: "MEDIUM"
contact: "platform@cloudservices.com"

rules_enabled:
  - "ARCHITECTURE_PATTERNS"
  - "TECH_STACK"
```

### architecture-patterns.yaml

```yaml
required_patterns:
  - pattern: "API Gateway"
    description: "All external requests via API Gateway"
    example_path: "src/gateway/"
  
  - pattern: "Circuit Breaker"
    description: "Prevent cascade failures"
    implementation: "Use Hystrix or similar"
  
  - pattern: "Event Sourcing"
    description: "All state changes as events"
    example_path: "src/events/"
  
  - pattern: "CQRS"
    description: "Separate read/write models"

forbidden_patterns:
  - pattern: "Shared Database"
    description: "Each service owns its data"
    reason: "Violates microservice independence"

design_principles:
  - "12-Factor App methodology"
  - "Stateless services"
  - "Idempotent operations"
  - "Fail-fast with circuit breakers"
```

---

## Example 3: Python Library

**Scenario:** Open-source Python library with community contributions.

### governance.yaml

```yaml
company_name: "Open Source Community"
project_name: "DataViz Pro"
repo_name: "dataviz-pro"
repo_type: "library"
version: "1.0.0"
updated_date: "2025-12-15"

description: |
  Professional data visualization library for Python.
  Community-driven with maintainer oversight.

enforcement_level: "ADVISORY"
block_on_violation: false
priority: "LOW"
contact: "maintainers@dataviz.io"

rules_enabled:
  - "CODING_STANDARDS"
  - "TECH_STACK"
```

### coding-standards.yaml

```yaml
naming_conventions:
  functions:
    pattern: "snake_case"
    example: "plot_scatter"
  classes:
    pattern: "PascalCase"
    example: "ChartRenderer"

code_style:
  max_line_length: 88  # Black default
  indent_size: 4

documentation_requirements:
  functions_require_docstrings: true
  classes_require_docstrings: true
  modules_require_docstrings: true
  docstring_style: "numpy"
  examples_required: true

file_organization:
  max_file_lines: 300
  test_coverage_min: 80
```

### tech-stack.yaml

```yaml
approved_libraries:
  python:
    - "numpy>=1.24"
    - "pandas>=2.0"
    - "matplotlib>=3.7"
    - "pytest>=7.4"
    - "black>=23.0"
    - "mypy>=1.5"

version_constraints:
  python: ">=3.8"

upgrade_policy:
  frequency: "as_needed"
  backward_compatibility: "required"
```

---

## Example 4: Startup MVP

**Scenario:** Fast-moving startup with flexible standards.

### governance.yaml

```yaml
company_name: "TechStartup"
project_name: "MVP Platform"
repo_name: "mvp-app"
repo_type: "application"
version: "0.1.0"
updated_date: "2025-12-15"

description: |
  Early-stage MVP with rapid iteration.
  Focus on speed while maintaining code quality.

enforcement_level: "WARN"
block_on_violation: false
priority: "MEDIUM"
contact: "dev@techstartup.com"

rules_enabled:
  - "CODING_STANDARDS"
  - "TECH_STACK"
```

### coding-standards.yaml

```yaml
# Minimal standards for speed
code_style:
  max_line_length: 120
  indent_size: 4

documentation_requirements:
  functions_require_docstrings: false  # Optional for MVP
  classes_require_docstrings: true     # Classes must document
```

### tech-stack.yaml

```yaml
approved_libraries:
  python:
    - "fastapi"
    - "sqlalchemy"
    - "pydantic"
    - "pytest"

# No forbidden libraries - allow experimentation
forbidden_libraries: []

upgrade_policy:
  frequency: "continuous"
  philosophy: "Use latest stable versions"
```

---

## Example 5: Data Science Project

**Scenario:** ML/AI project with Jupyter notebooks and experiments.

### governance.yaml

```yaml
company_name: "DataLabs"
project_name: "Customer Churn Prediction"
repo_name: "churn-model"
repo_type: "application"
version: "1.0.0"
updated_date: "2025-12-15"

description: |
  Machine learning project for customer churn prediction.
  Combines notebooks for exploration and production code.

enforcement_level: "WARN"
block_on_violation: false
priority: "MEDIUM"
contact: "ml-team@datalabs.com"

rules_enabled:
  - "CODING_STANDARDS"
  - "TECH_STACK"
  - "BUSINESS_RULES"
```

### tech-stack.yaml

```yaml
approved_libraries:
  python:
    - "pandas>=2.0"
    - "numpy>=1.24"
    - "scikit-learn>=1.3"
    - "tensorflow>=2.13"
    - "jupyter>=1.0"
    - "mlflow>=2.7"
    - "pytest>=7.4"

version_constraints:
  python: ">=3.10"

upgrade_policy:
  frequency: "monthly"
  ml_frameworks: "test_before_upgrade"
```

### business-rules.yaml

```yaml
validation_rules:
  - rule_id: "ML001"
    description: "Model accuracy must exceed 85%"
    validation: "accuracy >= 0.85"
    test_required: true
  
  - rule_id: "ML002"
    description: "Train/test split must be 80/20"
    validation: "test_size == 0.20"
    test_required: true

data_constraints:
  - field: "training_data"
    min_samples: 10000
    max_missing_percent: 5
```

---

## Example 6: Legacy Modernization

**Scenario:** Gradual migration from legacy codebase.

### governance.yaml

```yaml
company_name: "Enterprise Corp"
project_name: "Legacy Modernization"
repo_name: "modernized-app"
repo_type: "monorepo"
version: "2.0.0"
updated_date: "2025-12-15"

description: |
  Modernization of legacy application.
  New code must follow modern standards.

enforcement_level: "WARN"
block_on_violation: false
priority: "HIGH"
contact: "modernization@enterprise.com"

rules_enabled:
  - "CODING_STANDARDS"
  - "ARCHITECTURE_PATTERNS"
  - "TECH_STACK"
```

### architecture-patterns.yaml

```yaml
required_patterns:
  - pattern: "Strangler Fig"
    description: "Gradual migration pattern"
    example_path: "src/modern/"
  
  - pattern: "Anti-Corruption Layer"
    description: "Isolate legacy code"
    example_path: "src/adapters/"

forbidden_patterns:
  - pattern: "Direct Legacy Calls"
    description: "Always use adapters"
    reason: "Prevents modern code contamination"

layer_architecture:
  layers:
    - name: "Modern"
      path: "src/modern/"
      dependencies: ["Adapters"]
    
    - name: "Adapters"
      path: "src/adapters/"
      dependencies: ["Legacy"]
    
    - name: "Legacy"
      path: "src/legacy/"
      dependencies: []
      notes: "Do not modify - replace gradually"
```

---

## 🎯 Choosing Your Configuration

| Scenario | Priority | Enforcement | Focus Areas |
|----------|----------|-------------|-------------|
| **Enterprise** | HIGH | STRICT | Security, Compliance, Standards |
| **Microservice** | MEDIUM | WARN | Architecture, Patterns |
| **Open Source** | LOW | ADVISORY | Documentation, Style |
| **Startup MVP** | MEDIUM | WARN | Speed, Flexibility |
| **Data Science** | MEDIUM | WARN | Model Quality, Reproducibility |
| **Legacy Migration** | HIGH | WARN | Architecture, Isolation |

---

## 🔗 Related Documentation

- [Setup Guide](./cortex-implants-setup-guide.md)
- [Integration Guide](./cortex-implants-integration-guide.md)
- [System Design](../implementation-guides/cortex-implants-system-design.md)

---

**Questions?** See [Setup Guide](./cortex-implants-setup-guide.md) for detailed configuration options.
