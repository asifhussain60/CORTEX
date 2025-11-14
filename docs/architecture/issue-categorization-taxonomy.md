# CORTEX Health Audit - Issue Categorization Taxonomy

**Version:** 1.0  
**Status:** DRAFT  
**Author:** Asif Hussain  
**Date:** 2025-11-14

## 🎯 Overview

Comprehensive categorization system for all types of issues that can be detected in CORTEX implementation, providing structured classification for automated analysis and prioritization.

## 🏷️ Primary Categories

### 1. Tier 0 Issues (Governance & Protection)

**Category:** `TIER0_GOVERNANCE`

| Issue Type | Description | Examples | Severity Range |
|------------|-------------|----------|----------------|
| RULE_VIOLATION | Brain protection rule violations | SKULL rules ignored, immutable files modified | CRITICAL-HIGH |
| PROTECTION_BYPASS | Security/safety mechanisms bypassed | Tests skipped, validation disabled | CRITICAL-HIGH |
| GOVERNANCE_GAP | Missing governance controls | Unprotected operations, missing rules | HIGH-MEDIUM |
| RULE_INCONSISTENCY | Conflicting or unclear rules | Contradictory SKULL rules | MEDIUM |

### 2. Tier 1 Issues (Working Memory)

**Category:** `TIER1_MEMORY`

| Issue Type | Description | Examples | Severity Range |
|------------|-------------|----------|----------------|
| MEMORY_CORRUPTION | Data integrity problems | Invalid JSON, corrupted SQLite | CRITICAL |
| FIFO_VIOLATION | Queue ordering issues | Out-of-order conversations, missing entries | HIGH |
| ENTITY_TRACKING_FAILURE | Lost entity relationships | Missing user tracking, broken links | HIGH-MEDIUM |
| CAPACITY_OVERFLOW | Memory limits exceeded | >20 conversations, database bloat | MEDIUM |
| SYNC_INCONSISTENCY | Memory/storage sync problems | Cache out of date, write failures | MEDIUM-LOW |

### 3. Tier 2 Issues (Knowledge Graph)

**Category:** `TIER2_KNOWLEDGE`

| Issue Type | Description | Examples | Severity Range |
|------------|-------------|----------|----------------|
| PATTERN_DECAY | Knowledge degradation | Outdated patterns, broken references | HIGH |
| GRAPH_CORRUPTION | Structural integrity problems | Broken edges, orphaned nodes | HIGH |
| LEARNING_STAGNATION | No new pattern formation | Learning pipeline broken | MEDIUM |
| RELATIONSHIP_GAPS | Missing critical connections | Isolated knowledge islands | MEDIUM |
| INFERENCE_FAILURE | Can't derive new knowledge | Pattern matching broken | MEDIUM-LOW |

### 4. Tier 3 Issues (Development Context)

**Category:** `TIER3_CONTEXT`

| Issue Type | Description | Examples | Severity Range |
|------------|-------------|----------|----------------|
| GIT_ANALYSIS_FAILURE | Git context extraction broken | Can't read history, missing metrics | HIGH |
| CONTEXT_STALENESS | Development context out of date | Old file info, stale metrics | MEDIUM |
| INTELLIGENCE_GAP | Missing context awareness | No project understanding | MEDIUM |
| METRIC_CORRUPTION | Invalid or misleading metrics | Wrong test coverage, bad stats | LOW |

## 🤖 Agent System Issues

### 5. Agent Communication Issues

**Category:** `AGENT_COMMUNICATION`

| Issue Type | Description | Examples | Severity Range |
|------------|-------------|----------|----------------|
| CORPUS_CALLOSUM_FAILURE | Inter-agent communication broken | Messages lost, protocol errors | CRITICAL |
| WORKFLOW_BREAKDOWN | Agent coordination failures | Stuck workflows, deadlocks | HIGH |
| AGENT_ISOLATION | Agents not cooperating | Solo operations, missing handoffs | MEDIUM |
| MESSAGE_CORRUPTION | Invalid agent messages | Malformed data, protocol violations | MEDIUM |

### 6. Specialist Agent Issues

**Category:** `AGENT_SPECIALIST`

| Issue Type | Description | Examples | Severity Range |
|------------|-------------|----------|----------------|
| AGENT_UNAVAILABLE | Required agent not responding | Executor down, Tester offline | HIGH |
| CAPABILITY_DEGRADATION | Agent functionality reduced | Incomplete implementations | MEDIUM |
| ROLE_CONFUSION | Agents performing wrong tasks | Wrong agent for job | MEDIUM-LOW |
| PERFORMANCE_DEGRADATION | Agents running slowly | Response time issues | LOW |

## 🔌 Plugin System Issues

### 7. Plugin Registration Issues

**Category:** `PLUGIN_REGISTRATION`

| Issue Type | Description | Examples | Severity Range |
|------------|-------------|----------|----------------|
| REGISTRATION_FAILURE | Plugin can't register | Import errors, missing dependencies | HIGH |
| COMMAND_CONFLICT | Duplicate command registrations | Same command from multiple plugins | HIGH |
| METADATA_INVALID | Plugin metadata problems | Wrong version, missing info | MEDIUM |
| DEPENDENCY_MISSING | Required plugin dependencies missing | Broken plugin chains | MEDIUM |

### 8. Plugin Health Issues

**Category:** `PLUGIN_HEALTH`

| Issue Type | Description | Examples | Severity Range |
|------------|-------------|----------|----------------|
| PLUGIN_CRASH | Plugin causing system crashes | Unhandled exceptions | CRITICAL |
| MEMORY_LEAK | Plugin consuming excessive memory | Growing memory usage | HIGH |
| RESOURCE_EXHAUSTION | Plugin overusing resources | Too many files open, CPU spike | HIGH-MEDIUM |
| API_DEPRECATION | Plugin using outdated APIs | Deprecated function calls | LOW |

## 🧪 Testing & Quality Issues

### 9. Test Coverage Issues

**Category:** `TEST_COVERAGE`

| Issue Type | Description | Examples | Severity Range |
|------------|-------------|----------|----------------|
| CRITICAL_PATH_UNTESTED | Core functionality not tested | Main workflows missing tests | CRITICAL |
| LOW_COVERAGE | Insufficient test coverage | <80% coverage in critical modules | HIGH |
| FLAKY_TESTS | Tests with inconsistent results | Random failures, timing issues | MEDIUM |
| OUTDATED_TESTS | Tests not matching current code | Obsolete test cases | MEDIUM-LOW |

### 10. Test Execution Issues

**Category:** `TEST_EXECUTION`

| Issue Type | Description | Examples | Severity Range |
|------------|-------------|----------|----------------|
| TEST_FAILURE | Tests actively failing | Assertion errors, exceptions | HIGH |
| SETUP_FAILURE | Test environment problems | Database setup fails, missing fixtures | HIGH-MEDIUM |
| PERFORMANCE_REGRESSION | Tests running too slowly | Timeout issues, performance degradation | MEDIUM |
| RESOURCE_CLEANUP | Tests leaving behind artifacts | Temp files, open connections | LOW |

## 📚 Documentation Issues

### 11. Documentation Quality Issues

**Category:** `DOCUMENTATION_QUALITY`

| Issue Type | Description | Examples | Severity Range |
|------------|-------------|----------|----------------|
| CRITICAL_DOCS_MISSING | Essential documentation absent | API docs missing, no setup guide | HIGH |
| OUTDATED_INFORMATION | Documentation doesn't match code | Wrong examples, obsolete instructions | MEDIUM |
| BROKEN_LINKS | Links pointing to non-existent content | 404 errors, missing references | MEDIUM-LOW |
| POOR_STRUCTURE | Hard to navigate or understand | No table of contents, unclear organization | LOW |

### 12. Documentation Maintenance Issues

**Category:** `DOCUMENTATION_MAINTENANCE`

| Issue Type | Description | Examples | Severity Range |
|------------|-------------|----------|----------------|
| AUTO_GENERATION_FAILURE | Automated docs not updating | Doc generation scripts broken | MEDIUM |
| VERSION_SYNC_FAILURE | Docs out of sync with versions | Wrong version numbers, old feature lists | MEDIUM-LOW |
| LOCALIZATION_GAPS | Missing translations or outdated | English-only docs, stale translations | LOW |

## ⚙️ Configuration Issues

### 13. Configuration Validity Issues

**Category:** `CONFIGURATION_VALIDITY`

| Issue Type | Description | Examples | Severity Range |
|------------|-------------|----------|----------------|
| INVALID_CONFIG | Configuration values are wrong | Bad JSON, wrong data types | HIGH |
| MISSING_REQUIRED | Required configuration missing | No database config, missing API keys | HIGH |
| CONFLICTING_SETTINGS | Configuration values conflict | Debug + production mode enabled | MEDIUM |
| DEFAULT_OVERRIDES | Important defaults overridden unsafely | Security settings disabled | MEDIUM-LOW |

### 14. Platform Configuration Issues

**Category:** `CONFIGURATION_PLATFORM`

| Issue Type | Description | Examples | Severity Range |
|------------|-------------|----------|----------------|
| PLATFORM_MISMATCH | Config doesn't match platform | Windows paths on Mac, wrong commands | MEDIUM |
| ENVIRONMENT_MISSING | Required environment variables missing | PATH issues, missing env vars | MEDIUM |
| PERMISSION_ISSUES | Insufficient permissions for config | Can't write to config dir | MEDIUM-LOW |
| MULTI_MACHINE_DRIFT | Different configs across machines | Inconsistent settings | LOW |

## 🚀 Operations & Orchestration Issues

### 15. Workflow Issues

**Category:** `WORKFLOW_OPERATIONS`

| Issue Type | Description | Examples | Severity Range |
|------------|-------------|----------|----------------|
| ORCHESTRATION_FAILURE | Workflow coordination broken | Steps out of order, missing dependencies | HIGH |
| TIMEOUT_ISSUES | Operations timing out | Long-running tasks stuck | HIGH-MEDIUM |
| ERROR_HANDLING_GAP | Poor error recovery | Unhandled exceptions, no retries | MEDIUM |
| STATUS_INCONSISTENCY | Workflow status tracking broken | Wrong status reported | MEDIUM-LOW |

### 16. Performance Issues

**Category:** `PERFORMANCE_OPERATIONS`

| Issue Type | Description | Examples | Severity Range |
|------------|-------------|----------|----------------|
| MEMORY_CONSUMPTION | Excessive memory usage | Memory leaks, large object retention | HIGH |
| CPU_UTILIZATION | High CPU usage | Infinite loops, inefficient algorithms | HIGH-MEDIUM |
| IO_BOTTLENECKS | File/network I/O problems | Slow disk access, network timeouts | MEDIUM |
| SCALABILITY_LIMITS | System doesn't scale well | Performance degrades with load | MEDIUM-LOW |

## 🔒 Security Issues

### 17. Security Vulnerabilities

**Category:** `SECURITY_VULNERABILITY`

| Issue Type | Description | Examples | Severity Range |
|------------|-------------|----------|----------------|
| DATA_EXPOSURE | Sensitive data exposed | Passwords in logs, API keys in code | CRITICAL |
| INJECTION_VULNERABILITY | Code/SQL injection possible | Unsanitized inputs | CRITICAL-HIGH |
| ACCESS_CONTROL_BYPASS | Authentication/authorization issues | Privilege escalation | HIGH |
| INSECURE_DEFAULTS | Default settings are insecure | Debug mode in production | MEDIUM |

## 🔧 Maintenance Issues

### 18. Technical Debt

**Category:** `TECHNICAL_DEBT`

| Issue Type | Description | Examples | Severity Range |
|------------|-------------|----------|----------------|
| CODE_DUPLICATION | Repeated code patterns | Copy-paste programming | MEDIUM-LOW |
| COMPLEX_CODE | Overly complex implementations | High cyclomatic complexity | MEDIUM-LOW |
| DEPRECATED_USAGE | Using deprecated features | Old API calls, obsolete patterns | LOW |
| ARCHITECTURAL_VIOLATION | Code violating design principles | Tight coupling, layer violations | LOW |

## 📊 Priority Scoring Matrix

### Scoring Algorithm

```python
def calculate_priority_score(issue: HealthIssue) -> int:
    """Calculate priority score (0-100) based on multiple factors"""
    severity_weights = {
        Severity.CRITICAL: 40,
        Severity.HIGH: 30,
        Severity.MEDIUM: 20,
        Severity.LOW: 10,
        Severity.INFO: 5
    }
    
    category_weights = {
        'TIER0_GOVERNANCE': 1.0,      # Highest priority
        'SECURITY_VULNERABILITY': 1.0,
        'TIER1_MEMORY': 0.9,
        'AGENT_COMMUNICATION': 0.8,
        'TEST_EXECUTION': 0.7,
        'TIER2_KNOWLEDGE': 0.6,
        'PLUGIN_REGISTRATION': 0.5,
        # ... etc
    }
    
    impact_modifier = calculate_impact_modifier(issue)
    urgency_modifier = calculate_urgency_modifier(issue)
    
    base_score = severity_weights[issue.severity]
    category_weight = category_weights.get(issue.category, 0.3)
    
    return min(100, int(base_score * category_weight * impact_modifier * urgency_modifier))
```

### Impact Factors

- **Tier 0 Issues**: Always high impact (affects system integrity)
- **Blocking Issues**: Prevents other work (higher impact)
- **Cascading Issues**: Affects multiple components
- **User-Facing Issues**: Directly impacts user experience
- **Development Velocity**: Slows down development

### Urgency Factors

- **Production Impact**: Affects live systems
- **Security Implications**: Time-sensitive security issues
- **Dependencies**: Other issues depend on fixing this
- **Deadlines**: Time constraints for fixes

## 🏁 Usage Examples

### Example Issue Classification

```python
# Critical governance violation
HealthIssue(
    id="TIER0-001",
    title="SKULL-001 Test Protection Rule Violated",
    description="Code claimed 'Fixed ✅' without running required tests",
    severity=Severity.CRITICAL,
    issue_type=IssueType.VIOLATION,
    category="TIER0_GOVERNANCE",
    file_path="/src/some_module.py",
    line_number=42,
    suggestions=[
        "Run test suite before claiming fixes",
        "Enable SKULL rule enforcement",
        "Add pre-commit hooks for test validation"
    ],
    priority_score=95
)

# Medium knowledge graph issue
HealthIssue(
    id="TIER2-015",
    title="Pattern Learning Stagnation Detected",
    description="No new patterns learned in last 30 days",
    severity=Severity.MEDIUM,
    issue_type=IssueType.PERFORMANCE,
    category="TIER2_KNOWLEDGE",
    suggestions=[
        "Check learning pipeline health",
        "Verify conversation import is working",
        "Review pattern detection algorithms"
    ],
    priority_score=45
)
```

---

**Next Steps:**
1. Review categorization completeness
2. Validate with actual CORTEX codebase
3. Implement detection algorithms for each category
4. Create report template using this taxonomy