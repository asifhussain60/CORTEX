    UnifiedContextManager enforces architectural boundaries:
    - Tier isolation (T1/T2/T3 separation)
    - Relevance-based loading prioritization
    - Token budget allocation fairness
    - Context deduplication and merging

- rule_id: "TOKEN_BUDGET_ALLOCATION_FAIRNESS"
  name: "Token Budget Allocation Must Be Proportional"
  severity: "blocked"
  description: "Token budget allocation must be proportional to relevance scores, not fixed percentages"

  detection:
    path_patterns:
      - "src/core/context_management/token_budget_manager.py"
    combined_keywords:
      unfair_allocation:
        - "tier1: total_budget * 0.9"
        - "fixed allocation"
        - "/ len(tier_relevance)"
      not_proportional:
        - "!tier_relevance"
        - "!relevance_score"
    scope: ["code"]
    logic: "AND"

  alternatives:
    - "Allocate budget proportionally to tier relevance scores"
    - "High relevance = more tokens, low relevance = fewer tokens"
    - "Ensure total allocation ≤ total_budget (no overflow)"

  evidence_template: "Unfair token allocation detected: '{code_snippet}'"

  rationale: |
    Token budget allocation algorithm ensures fairness:
    - Proportional to relevance (high relevance → more tokens)
    - Dynamic allocation (not fixed percentages)
    - Sum constraint enforced (total ≤ budget)

- rule_id: "STALENESS_THRESHOLD_ENFORCEMENT"
  name: "Staleness Thresholds Must Be Enforced"
  severity: "blocked"
  description: "Staleness thresholds: T1=24h, T2=90d, T3=7d must be enforced"

  detection:
    path_patterns:
      - "src/core/context_management/context_quality_monitor.py"
    combined_keywords:
      staleness_bypass:
        - "def check_staleness"
        - "return False"
      or_threshold_change:
        - "tier1': 168"
        - "tier2': 180"
        - "tier3': 14"
    scope: ["code"]
    logic: "OR"

  alternatives:
    - "T1 staleness: 24 hours (conversations)"
    - "T2 staleness: 90 days (learned patterns)"
    - "T3 staleness: 7 days (git metrics/insights)"
    - "Document rationale for any threshold changes"

  evidence_template: "Staleness detection compromised: '{code_snippet}'"

  rationale: |
    Staleness thresholds prevent using outdated context:
    - T1: 24h (recent conversations relevant)
    - T2: 90d (patterns valid longer term)
    - T3: 7d (metrics need frequent refresh)

- rule_id: "CROSS_TIER_LINKING_SCHEMA"
  name: "Cross-Tier Linking Schema Integrity"
  severity: "warning"
  description: "Cross-tier linking fields (used_patterns, used_metrics) must be maintained"

  detection:
    path_patterns:
      - "src/core/context_management/migrate_cross_tier_linking.py"
      - "src/tier1/**/*.py"
      - "src/tier2/**/*.py"
    keywords:
      - "used_patterns"
      - "used_metrics"
      - "applied_in_conversations"
    without_keywords:
      - "JSON serialization"
      - "json.dumps"
    scope: ["code"]

  alternatives:
    - "Store linking data as JSON-serialized lists"
    - "Update bidirectionally (T1 → T2 and T2 → T1)"
    - "Include context_quality_score for monitoring"

  evidence_template: "Cross-tier linking schema violation: '{code_snippet}'"
