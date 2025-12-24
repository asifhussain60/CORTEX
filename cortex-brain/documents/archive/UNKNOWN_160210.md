    URT v3.0 token budgets are carefully optimized:
    - CONCISE: 400 tokens (simple help/status queries)
    - SUMMARIZED: 600 tokens (implementation summaries)
    - DETAILED: 800 tokens (complex planning/analysis)
    - VISUAL: 500 tokens (metrics/diagrams)

    Changes must be validated with performance metrics.

- rule_id: "CHALLENGE_MODE_ROUTING_INTEGRITY"
  name: "Challenge Mode Routing Logic"
  severity: "blocked"
  description: "Challenge mode routing (SKIP/ACCEPT_ONLY/CHALLENGE_ONLY/MIXED/INTELLIGENT) must remain valid"

  detection:
    path_patterns:
      - "src/core/template_renderer.py"
    combined_keywords:
      challenge_logic:
        - "ChallengeMode"
        - "_determine_challenge_mode"
      bypass_pattern:
        - "return ChallengeMode.SKIP"
        - "# Bypass all validation"
    scope: ["code"]
    logic: "AND"

  alternatives:
    - "Preserve intelligent routing based on context analysis"
    - "SKIP mode only for simple info requests (help, status)"
    - "INTELLIGENT mode for complex planning/validation"
    - "Document any routing logic changes with test cases"

  evidence_template: "Challenge routing bypass detected: '{code_snippet}'"

  rationale: |
    Challenge mode routing is core to URT v3.0:
    - Eliminates forced challenge display when unnecessary
    - Intelligent validation for complex requests
    - User feedback: "No more forced challenge when nothing to validate"

- rule_id: "TEMPLATE_SCHEMA_VALIDATION"
  name: "Template Orchestration Metadata Schema"
  severity: "warning"
  description: "Templates must include orchestration metadata: relevance_keywords, priority, composability"

  detection:
    path_patterns:
      - "cortex-brain/response-templates/*.yaml"
    keywords:
      - "new template"
      - "template_id:"
    without_keywords:
      - "orchestration:"
      - "relevance_keywords:"
    scope: ["code"]

  alternatives:
    - "Add orchestration metadata block with relevance_keywords, priority, category"
    - "Include composability rules: compatible_with, conflicts_with"
    - "See cortex-brain/response-templates/base-template-v2.yaml for schema"

  evidence_template: "Template missing orchestration metadata: '{template_id}'"
