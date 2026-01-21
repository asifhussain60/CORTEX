# CORTEX Feedback Collection Prompt
**Version:** 1.0 | **Updated:** 2026-01-21 | **Purpose:** Operational feedback for GitHub Issues

---

## Purpose

Generate structured YAML feedback from CORTEX operations for GitHub Issue upload. Collect metrics, errors, performance data, and improvement opportunities across all operational components.

---

## Feedback Collection Protocol

### When to Generate Feedback
- After completing a significant operation (AC implementation, phase completion)
- When encountering errors or unexpected behavior
- When performance degrades below thresholds
- When governance violations are detected
- After test suite execution with failures
- When user requests operational review

---

## YAML Feedback Schema

Generate feedback in this exact YAML structure:

```yaml
# CORTEX Operational Feedback
# Generated: {timestamp}
# Session: {session_id}

metadata:
  generated_at: "{ISO-8601 timestamp}"
  session_id: "{unique session identifier}"
  machine: "{mac|win}"
  cortex_version: "3.9"
  feedback_type: "{error|performance|enhancement|governance|general}"
  priority: "{P0-CRITICAL|P1-HIGH|P2-MEDIUM|P3-LOW}"

summary:
  title: "{Brief descriptive title for GitHub Issue}"
  description: |
    {2-3 sentence summary of the feedback}
  impact: "{What is affected by this issue/observation}"
  
orchestrator_state:
  active_orchestrator: "{MasterOrchestrator|BuilderOrchestrator|etc}"
  operation_type: "{IMPLEMENT|ANALYZE|REVIEW|VALIDATE}"
  phase_context: "{current phase from cortex-impl-map.yaml}"
  intent_classification:
    primary_intent: "{detected intent}"
    confidence: {0.0-1.0}
    disambiguation_required: {true|false}

execution_metrics:
  duration_ms: {operation duration}
  token_usage:
    input: {tokens}
    output: {tokens}
    percentage_of_limit: {0-100}
  state_transitions: {count}
  audit_entries_created: {count}

module_health:
  intent_router:
    status: "{operational|degraded|failed}"
    classification_accuracy: {0.0-1.0}
    fallback_invocations: {count}
  governance_engine:
    status: "{operational|degraded|failed}"
    rules_evaluated: {count}
    violations_detected: {count}
    rules_list: ["{CORE-XXX violations}"]
  orchestrators:
    active: ["{list of active orchestrators}"]
    delegation_count: {count}
    failed_delegations: {count}
  infrastructure:
    database_status: "{connected|disconnected|error}"
    circuit_breaker_trips: {count}
    retry_attempts: {count}

errors:
  - error_id: "{unique error identifier}"
    timestamp: "{ISO-8601}"
    component: "{module/class where error occurred}"
    error_type: "{exception class}"
    message: "{error message}"
    stack_trace: |
      {truncated stack trace - last 10 lines}
    context:
      operation: "{what was being attempted}"
      inputs: "{sanitized inputs - no secrets}"
      state: "{relevant state at time of error}"
    recovery:
      attempted: {true|false}
      successful: {true|false}
      fallback_used: "{fallback mechanism if any}"

performance_observations:
  slow_operations:
    - operation: "{operation name}"
      duration_ms: {duration}
      threshold_ms: {expected threshold}
      deviation_percent: {percentage over threshold}
  resource_usage:
    memory_mb: {peak memory}
    db_connections: {active connections}
    pending_transactions: {count}

governance_compliance:
  overall_status: "{compliant|violations_detected}"
  tier0_violations:
    - rule_id: "{CORE-XXX}"
      description: "{what was violated}"
      severity: "{blocked|strict}"
      remediation: "{how to fix}"
  audit_trail:
    integrity: "{verified|broken|unchecked}"
    entries_since_last_check: {count}
    hash_chain_valid: {true|false}

test_results:
  last_run: "{ISO-8601}"
  collection_status: "{success|errors}"
  tests_collected: {count}
  tests_passed: {count}
  tests_failed: {count}
  failure_categories:
    - category: "{import_error|assertion|timeout|other}"
      count: {count}
      examples: ["{test names}"]

enhancement_opportunities:
  - id: "{ENH-XXX}"
    category: "{performance|reliability|usability|governance}"
    title: "{brief title}"
    description: |
      {detailed description of the enhancement opportunity}
    affected_components: ["{list of components}"]
    estimated_effort: "{hours|days}"
    priority_recommendation: "{P1|P2|P3}"
    related_ac_ids: ["{AC-XXX-XXX}"]

reproduction_steps:
  - step: 1
    action: "{what to do}"
    expected: "{expected result}"
    actual: "{actual result if different}"

environment:
  python_version: "{version}"
  os: "{Windows|macOS|Linux}"
  dependencies_status: "{all_present|missing: [list]}"
  config_files:
    cortex_impl_map: "{path and version}"
    governance_rules: "{path and rule count}"

recommended_actions:
  immediate:
    - "{action 1}"
    - "{action 2}"
  short_term:
    - "{action}"
  investigation_required:
    - "{what needs further analysis}"

github_issue_labels:
  - "{bug|enhancement|performance|governance}"
  - "{priority label}"
  - "{component label}"

related_issues:
  - issue_number: {number}
    relationship: "{blocks|related_to|duplicate_of}"
```

---

## Collection Sources

### 1. Orchestrator Metrics
```python
# Entry point: cortex.orchestrators.core.master_orchestrator.MasterOrchestrator
# Collect:
- operation_history: List[Dict[str, Any]]
- domain_orchestrators: Dict[str, OrchestratorMetadata]
- _turn_number: int
- delegation decisions and outcomes
```

### 2. Intent Router Metrics
```python
# Entry point: cortex.intent_router.classifier.IntentClassifier
# Collect:
- classification results with confidence scores
- disambiguation events
- fallback invocations
- routing decisions
```

### 3. Governance Registry
```python
# Entry point: cortex.brain.core.governance_registry.GovernanceRegistry
# Collect:
- rule evaluation counts
- violation events
- tier precedence conflicts
- enforcement actions
```

### 4. Audit Logger
```python
# Entry point: cortex.infrastructure.enhanced_audit_logger.EnhancedAuditLogger
# Collect:
- operation logs
- hash chain integrity
- performance metrics
- error events
```

### 5. Infrastructure Components
```python
# Entry points:
# - cortex.infrastructure.circuit_breaker.CircuitBreaker
# - cortex.infrastructure.connection_pool.ConnectionPool
# - cortex.infrastructure.retry_strategy.RetryStrategy
# Collect:
- circuit breaker state and trips
- connection pool utilization
- retry attempts and outcomes
```

### 6. Test Results
```bash
# Command: pytest tests/ --json-report --json-report-file=feedback.json
# Collect:
- test collection status
- pass/fail counts
- failure categories
- slow tests
```

---

## Feedback Generation Commands

```bash
# Generate full operational feedback
python -m cortex.tools.feedback_collector --output feedback.yaml

# Generate error-focused feedback
python -m cortex.tools.feedback_collector --type errors --since "1 hour ago"

# Generate performance feedback
python -m cortex.tools.feedback_collector --type performance --threshold 100ms

# Generate governance compliance report
python -m cortex.tools.feedback_collector --type governance
```

---

## GitHub Issue Template

When uploading feedback to GitHub Issues, use this template:

```markdown
## 🧠 CORTEX Operational Feedback

**Type:** {feedback_type}
**Priority:** {priority}
**Generated:** {timestamp}

### Summary
{summary.description}

### Impact
{summary.impact}

### Details
<details>
<summary>Full YAML Feedback</summary>

```yaml
{paste generated YAML here}
```

</details>

### Recommended Actions
{list from recommended_actions}

### Labels
{github_issue_labels}
```

---

## Thresholds and Alerts

| Metric | Warning | Critical |
|--------|---------|----------|
| Operation duration | >500ms | >2000ms |
| Token usage | >70% | >90% |
| Governance violations | 1+ STRICT | 1+ BLOCKED |
| Circuit breaker trips | 3 in 1min | 5 in 1min |
| Test failures | >2% | >5% |
| DB connections | >80% pool | 100% pool |

---

## Privacy and Security

**NEVER include in feedback:**
- API keys, tokens, or credentials
- Personal identifiable information (PII)
- Full file paths with usernames
- Database contents or queries with sensitive data
- Unredacted error messages with secrets

**Always sanitize:**
- Replace paths with relative paths
- Mask credential values with `***REDACTED***`
- Truncate large payloads to 500 chars

---

**Last Updated:** 2026-01-21
**Version:** 1.0
**Status:** ✅ Ready for use
