# Company Workflow Template Overrides

This directory holds **company-specific** workflow template overrides.

## Override Precedence

Templates placed here **take priority** over templates in
`cortex-registry/workflows/templates/`:

```
company/workflows/  (priority 1 — highest)
cortex-registry/workflows/templates/  (priority 2 — default)
```

## Usage

To override a CORTEX template, create a YAML file with the **same `id`** as the
template you want to override. For example, to customize the TDD workflow:

```yaml
# company/workflows/tdd-custom.yaml
workflow:
  id: "tdd/feature-implementation"
  name: "Company TDD Workflow"
  category: "tdd"
  steps:
    - step_id: "red_phase"
      name: "RED Phase"
      # ... company-specific TDD steps
```

## Structure

Organize templates by category:

```
company/workflows/
  tdd/           # TDD workflow overrides
  security/      # Security workflow overrides
  quality/       # Code quality overrides
  lifecycle/     # Project lifecycle overrides
```

## Discovery

Templates in this directory are automatically discovered by
`WorkflowTemplateMixin.discover_company_templates()` and registered
with override precedence in the `WorkflowTemplateRegistry`.
