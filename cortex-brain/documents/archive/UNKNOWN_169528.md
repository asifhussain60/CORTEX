    Relevance weight modification detected: '{code_snippet}'

    Weights are validated through extensive testing.
    Changes require performance analysis.

  rationale: |
    Relevance scoring weights are empirically validated:
    - keyword=0.4 (strongest signal)
    - trigger=0.3 (explicit phrases)
    - context=0.2 (metadata match)
    - category=0.1 (general relevance)

- rule_id: "CONFLICT_RESOLUTION_PRIORITY"
  name: "Conflict Resolution Priority Map"
  severity: "blocked"
  description: "Priority map: error=100, security=90, planning=80, execution=70, validation=60, help=50, status=40, general=30"

  detection:
    path_patterns:
      - "src/response_templates/multi_template_orchestrator.py"
    combined_keywords:
      priority_change:
        - "PRIORITY_MAP"
        - "'error':"
      invalid_priority:
        - "'error': 50"
        - "'general': 100"
    scope: ["code"]
    logic: "AND"

  alternatives:
    - "error=100 (highest priority - user blocked)"
    - "security=90 (critical security issues)"
    - "planning=80 (important strategic work)"
    - "Preserve priority hierarchy for conflict resolution"

  evidence_template: "Priority map violation detected: '{code_snippet}'"

  rationale: |
    Priority map ensures critical templates win conflicts:
    - Errors block users → highest priority
    - Security issues → second highest
    - General info → lowest priority

- rule_id: "MAX_TEMPLATES_LIMIT"
  name: "Max Templates Composition Limit"
  severity: "warning"
  description: "max_templates=3 limit enforced (composition complexity management)"

  detection:
    path_patterns:
      - "src/response_templates/multi_template_orchestrator.py"
      - "cortex-brain/response-templates/*.yaml"
    combined_keywords:
      limit_increase:
        - "max_templates"
        - "= 5"
        - "= 10"
    scope: ["code"]
    logic: "AND"

  alternatives:
    - "max_templates=3 (validated composition complexity limit)"
    - "Performance target: < 500ms composition time"
    - "Changes require composition time benchmarking"

  evidence_template: "Max templates limit increase detected: '{code_snippet}'"

  rationale: |
    max_templates=3 limit prevents:
    - Excessive composition complexity
    - Response token bloat
    - Performance degradation (target: < 500ms)

- rule_id: "TEMPLATE_COMPATIBILITY_MATRIX"
  name: "Template Compatibility Matrix Integrity"
  severity: "warning"
  description: "Template compatibility declarations must be reciprocal and conflict-free"

  detection:
    path_patterns:
      - "cortex-brain/response-templates-enhanced.yaml"
    combined_keywords:
      compatibility_violation:
        - "compatible_with"
        - "conflicts_with"
      circular_logic:
        - "compatible_with: [template_b]"
        - "conflicts_with: [template_b]"
    scope: ["code"]
    logic: "AND"

  alternatives:
    - "Ensure compatible_with declarations are reciprocal"
    - "Prevent circular conflicts (A compatible with B, A conflicts with B)"
    - "Validate compatibility matrix with automated tests"

  evidence_template: "Template compatibility violation: '{code_snippet}'"
