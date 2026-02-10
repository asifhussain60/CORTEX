# CORTEX Architecture Truth Document - Section 14

## 14. Brittleness, Wiring Integrity, and Permanent Deployment Readiness

**Authority:** This section provides explicit failure mode analysis with file references.  
**Status:** MANDATORY for production deployment approval.

---

## 14.1 Wiring Integrity Proof (Static)

### 14.1.1 Source of Truth for Orchestrator Wiring

**Canonical File:** `cortex/wiring/specifications/wiring.yaml`

This YAML file is the **SINGLE SOURCE OF TRUTH** for:
- All orchestrator definitions
- Module paths and class names
- Dependencies between orchestrators
- Tier assignments (1=core, 2=domain, 3=support)
- Priority ordering
- Health check methods
- MCP adapter mappings

**No other file defines orchestrator wiring.** Runtime registration is forbidden.

### 14.1.2 Reachability Guarantee (No Orphan Modules)

**Mechanism:** `cortex/wiring/registry/git_backed_registry.py`

```python
def load(self) -> None:
    # Load orchestrators from all categories
    for category in ['core', 'domain', 'support']:
        if category not in self._spec['orchestrators']:
            logger.warning(f"No {category} orchestrators defined")
            continue
        
        for orch_spec in self._spec['orchestrators'][category]:
            self._register_orchestrator(orch_spec, category)
```

**Guarantee:** Every orchestrator in wiring.yaml is registered. No orphans possible because:
1. wiring.yaml is the only input source
2. Loop iterates ALL entries in each category
3. Missing categories logged as warnings

**NOT GUARANTEED:** Orchestrator implementations exist. See section 14.1.3.

### 14.1.3 Detection of Missing Wiring, Invalid References, Version Drift

**Validation File:** `cortex/wiring/registry/wiring_validator.py`

**Checks Performed:**

| Check | Method | Failure Mode |
|-------|--------|--------------|
| Circular dependencies | `_check_circular_dependencies()` | Returns list of cycles detected |
| Missing dependencies | `_check_missing_dependencies()` | Returns list of non-existent dependency names |
| Duplicate names | `_check_duplicate_names()` | Returns list of duplicate orchestrator names |
| Required fields | `_check_required_structure()` | Returns missing fields: name, module, class, tier, priority, dependencies, capabilities, health_check |
| Tier ordering | `_check_tier_ordering()` | Warning if lower tier depends on higher tier |
| Module path validity | `_check_module_paths()` | Warning if module cannot be imported (NOT BLOCKING) |
| Health check presence | `_check_health_checks()` | Warning if health_check method missing |

**VERSION DRIFT DETECTION:**

The `get_wiring_hash()` method computes SHA256 of wiring.yaml:
```python
def get_wiring_hash(self) -> str:
    with open(self.wiring_file, 'rb') as f:
        content = f.read()
        return hashlib.sha256(content).hexdigest()[:16]
```

**Gap:** No automatic comparison against last-deployed hash. Drift detection is **MANUAL**.

### 14.1.4 Route Validation Between Orchestrators

**Pre-Runtime Validation:** `cortex/wiring/specifications/intent-routing.yaml`

```yaml
IMPLEMENT:
  primary_orchestrator: "TDDOrchestrator"
  fallback_orchestrators:
    - name: "CodePlannerOrchestrator"
      confidence_penalty: 0.1
```

**Validation Mechanism:** IntentRouter validates at route time:
```python
target_orch = self._orchestrators.get(decision.target_handler)
if target_orch is None:
    return Err(f"Orchestrator not found: {decision.target_handler}")
```

**Gap:** No pre-deployment validation that all route targets exist. Validation is **RUNTIME ONLY**.

### 14.1.5 Schema Validation for Wiring/Config Files

**Current State:** Partial Pydantic validation in `orchestrator_factory.py`:

```python
class WiringSpecification(BaseModel):
    version: str
    orchestrators: Dict[str, Any]
    analyzers: Optional[Dict[str, Any]] = None
    config: Optional[Dict[str, Any]] = None
```

**Gap:** No strict JSON Schema or Pydantic model for orchestrator entries. The `Dict[str, Any]` type erases structure.

**Required but NOT IMPLEMENTED:**
```yaml
# Desired: Strict orchestrator schema
orchestrator_schema:
  type: object
  required: [name, module, class, tier, priority, dependencies, capabilities, health_check]
  properties:
    name: {type: string, pattern: "^[A-Z][a-zA-Z]+Orchestrator$"}
    module: {type: string, pattern: "^cortex\\.[a-z_.]+$"}
    tier: {type: integer, enum: [1, 2, 3]}
```

---

### 14.1.6 Wiring Truth Table

| Orchestrator | Entrypoint | Dependencies | Expected Inputs | Expected Outputs | Validation | Failure Mode if Missing |
|--------------|------------|--------------|-----------------|------------------|------------|------------------------|
| InteractionOrchestrator | `cortex.orchestrators.core.interaction_orchestrator:InteractionOrchestrator` | None | `{request, context}` | `{response, challenges}` | `execute_turn()` health check | LENS protocol broken, no comprehension |
| IntentRouter | `cortex.orchestrators.core.intent_router:IntentRouter` | InteractionOrchestrator | `{operation, description}` | `RoutingDecision` | `classify_intent()` health check | All routing fails, requests unclassified |
| TDDOrchestrator | `cortex.orchestrators.core.tdd_orchestrator:TDDOrchestrator` | InteractionOrchestrator, IntentRouter | `{target, test_file, lens_context}` | `{tests, implementation}` | `generate_tests()` health check | IMPLEMENT/FIX blocked, no TDD |
| EnforcementOrchestrator | `cortex.orchestrators.core.enforcement_orchestrator:EnforcementOrchestrator` | LENSSynthesis | `{operation, code_sample}` | `EnforcementResult` | `validate_operation()` health check | Governance bypassed, violations allowed |
| MasterOrchestrator | `cortex.orchestrators.core.master_orchestrator:MasterOrchestrator` | InteractionOrchestrator, IntentRouter, LENSSynthesis, TDDOrchestrator | `{operation_name, parameters}` | `Result[Dict, Error]` | `coordinate_operation()` health check | System inoperable, no coordination |
| LENSSynthesis | `cortex.orchestrators.core.lens_synthesis:LENSSynthesis` | IntentRouter, ComplexityClassifier | `{operation, analysis}` | `{recommendations}` | `synthesize()` health check | No DoR generation, no context synthesis |
| RefactoringOrchestrator | `cortex.orchestrators.domain.enhanced_refactoring_orchestrator:EnhancedRefactoringOrchestrator` | MasterOrchestrator | `{target, refactoring_type}` | `{changes}` | `analyze_refactoring()` health check | REFACTOR intent fails |
| PlanOrchestrator | `cortex.orchestrators.support.plan_orchestrator:PlanOrchestrator` | None | `{phase_id, operation}` | `{result}` | `setup_phase()` health check | PLAN MODE broken |
| HolisticValidationOrchestrator | `cortex.orchestrators.holistic.holistic_validation_orchestrator:HolisticValidationOrchestrator` | None | `{target, operation}` | `ValidationResult` | `validate()` health check | Pre-implementation validation skipped |

---

## 14.2 Runtime Wiring & Deployability

### 14.2.1 Wiring Behavior Outside Dev Environment

**Current Behavior:**
1. `GitBackedRegistry` looks for wiring.yaml relative to CWD
2. Falls back to `cortex/wiring/specifications/wiring.yaml`
3. `path_resolver.py` uses `CORTEX_ROOT` env var or Git root detection

**Container Behavior:**
```dockerfile
# Dockerfile copies these directories
COPY cortex /app/cortex
COPY cortex_brain /app/cortex_brain
WORKDIR /app
```

**In container:** CWD is `/app`, so relative paths resolve correctly.

### 14.2.2 Assumptions CORTEX Makes

| Assumption | File Reference | Failure if False |
|------------|---------------|------------------|
| `wiring.yaml` exists at `cortex/wiring/specifications/wiring.yaml` | `git_backed_registry.py:42` | `FileNotFoundError` at startup |
| `cortex_brain/` directory exists | Multiple tier references | `FileNotFoundError` on rule loading |
| `.git/` directory exists (for Git root detection) | `path_resolver.py:49` | Falls back to CWD (may be wrong) |
| Python 3.9+ | `wiring_validator.py` uses dict ordering | Nondeterministic wiring order |
| `CORTEX_ROOT` or Git repo available | `path_resolver.py:35` | Path resolution fails |
| Write access to logs directory | `audit_logger.py` | Audit logging fails silently |
| Read access to all YAML files | Multiple | Governance rules not loaded |

### 14.2.3 Deployment Environment Compatibility

| Environment | Status | Issues | Mitigations |
|-------------|--------|--------|-------------|
| **Container (Docker)** | ✅ SUPPORTED | None (Dockerfile tested) | Use provided Dockerfile |
| **CI/CD Runner** | ⚠️ PARTIAL | No `.git/` directory in shallow clone | Set `CORTEX_ROOT` explicitly |
| **Enterprise (restricted FS)** | ⚠️ PARTIAL | May lack write access for logs | Use tmpfs for logs, or disable audit |
| **Multi-repo/Monorepo** | ⚠️ PARTIAL | Path resolution assumes single repo | Set `CORTEX_ROOT` per workspace |
| **Offline** | ✅ SUPPORTED | No external dependencies | All YAMLs bundled |
| **VS Code Extension Host** | ✅ SUPPORTED | Primary use case | Uses MCP server |

### 14.2.4 Deployment Assumptions Checklist

**MUST BE TRUE for successful deployment:**

- [ ] `cortex/wiring/specifications/wiring.yaml` is present and readable
- [ ] `cortex_brain/tier0/governance/core-rules.yaml` is present and readable
- [ ] Python 3.9+ is available
- [ ] Either `.git/` exists OR `CORTEX_ROOT` environment variable is set
- [ ] Write access to at least one of: `./logs/`, `$TMPDIR/`, `/tmp/`
- [ ] All orchestrator modules in wiring.yaml are importable (no broken imports)
- [ ] MCP server port (default 8443) is available
- [ ] No firewall blocking localhost connections

**SHOULD BE TRUE for optimal operation:**

- [ ] `CORTEX_LOG_LEVEL` set appropriately (default: INFO)
- [ ] Prometheus endpoint exposed at `/metrics`
- [ ] Health check endpoint at `/health` returns 200

---

## 14.3 Brittleness Hotspots

### 14.3.1 Magic Strings

| Location | Magic String | Risk | Detection | Recommended Fix |
|----------|--------------|------|-----------|-----------------|
| `wiring.yaml` | `"cortex.orchestrators.core.*"` | Typo breaks loading | Bootstrap fails | Add module existence validation |
| `intent_router.py` | `"IMPLEMENT"`, `"FIX"`, etc. | Case-sensitive matching | Wrong routing | Use `IntentType` enum everywhere |
| `enforcement_orchestrator.py` | `"CORE-008"`, `"CORE-011"` | Rule ID typos | Governance bypassed | Validate against rule registry |
| `path_resolver.py` | `"cortex_brain"` | Hardcoded directory name | Path not found | Use config constant |
| `git_backed_registry.py` | `"core"`, `"domain"`, `"support"` | Category typo | Orchestrators missing | Define categories in schema |

### 14.3.2 Implicit Conventions Not Enforced

| Convention | Current State | Risk | Enforcement Needed |
|------------|---------------|------|-------------------|
| Orchestrator naming: `*Orchestrator` | **NOT ENFORCED** | Inconsistent discovery | Add regex validation in wiring.yaml schema |
| Health check method name | **NOT ENFORCED** | Health checks don't run | Validate method exists at bootstrap |
| AC marker format | **NOT ENFORCED** | Audit trail broken | Add regex matcher in audit logger |
| File path portability | **PARTIAL** (CORE-005) | Windows/Unix breaks | More comprehensive path tests |
| Response header format | **ENFORCED** | N/A | ResponseHeaderInjector handles |

### 14.3.3 Silent Fallback Behavior

| Location | Fallback | Risk | Severity |
|----------|----------|------|----------|
| `path_resolver.py:50` | Falls back to CWD if no Git root | Wrong paths used | HIGH |
| `git_backed_registry.py:83` | Logs warning, continues if category missing | Incomplete wiring | MEDIUM |
| `lazy_orchestrator.py` | Returns `None` if instantiation fails | Silent orchestrator absence | HIGH |
| `enforcement_orchestrator.py` | Returns PASS if no rules loaded | Governance bypassed | CRITICAL |
| `lens_orchestrator.py:180` | Returns empty analysis on error | Missing intelligence | MEDIUM |

### 14.3.4 Tight Coupling

| Components | Coupling Type | Impact |
|------------|---------------|--------|
| IntentRouter ↔ intent-routing.yaml | Config coupling | Must stay synchronized |
| TDDOrchestrator ↔ tdd-rules.yaml | Knowledge coupling | Rules drive behavior |
| ResponseTemplate ↔ tier2 templates | Template coupling | Output format breaks if template missing |
| MasterOrchestrator ↔ All core orchestrators | Dependency coupling | MasterOrchestrator is a god object |

### 14.3.5 Undocumented Structure Reliance

| Structure | Documentation | Risk |
|-----------|--------------|------|
| Tier 0/1/2/3 directory layout | **IN LOADING-SEQUENCE.YAML** | Safe |
| wiring.yaml schema | **NOT DOCUMENTED** | Schema changes break parsing |
| AC marker regex | **NOT DOCUMENTED** | Audit parsing fails |
| Response header format | **IN RESPONSE-HEADERS.YAML** | Safe |
| Phase YAML schema | **PARTIAL** | Missing fields cause KeyError |

### 14.3.6 Optional Validations Not Gated

| Validation | Location | Gated? | Impact if Skipped |
|------------|----------|--------|------------------|
| Module path existence | `_check_module_paths()` | **WARNING ONLY** | ImportError at runtime |
| Health check presence | `_check_health_checks()` | **WARNING ONLY** | Health monitoring fails |
| Tier ordering | `_check_tier_ordering()` | **WARNING ONLY** | Confusing dependency graph |
| Docstring presence | `GovernanceEnforcementAgent` | **WARNING ONLY** | Missing documentation |
| Type hints | `GovernanceEnforcementAgent` | **WARNING ONLY** | Type safety compromised |

### 14.3.7 Config Drift Risks

| Config | Drift Detection | Mitigation |
|--------|-----------------|------------|
| wiring.yaml | Hash comparison via `get_wiring_hash()` | **NOT AUTOMATED** |
| index.yaml (phases) | Manual review | **NOT AUTOMATED** |
| core-rules.yaml | Git diff | **NOT AUTOMATED** |
| response templates | Manual review | **NOT AUTOMATED** |

### 14.3.8 Nondeterminism Sources

| Source | Location | Mitigation |
|--------|----------|------------|
| Dict ordering | Python 3.7+ | ✅ Guaranteed ordered |
| Thread execution order | `enforcement_orchestrator.py:ThreadPoolExecutor` | Results aggregated, order doesn't matter |
| Cache eviction | `lens_cache.py` | TTL-based, deterministic |
| File system enumeration | `glob()` calls | **POTENTIAL ISSUE** - sort results |
| Random usage in wiring | `test_wiring_determinism.py` | ✅ Tested - no random in wiring |

---

## 14.4 Invariants and Guarantees

### 14.4.1 Non-Negotiable Invariants

| Invariant | Enforced By | Tested By | Violation Consequence |
|-----------|-------------|-----------|----------------------|
| wiring.yaml must exist | `git_backed_registry.py` | `test_wiring_determinism.py` | `FileNotFoundError`, system won't start |
| core-rules.yaml must exist | `governance_loading_sequence.yaml` | `test_governance_registry_loading.py` | Governance completely bypassed |
| No circular dependencies | `WiringValidator._check_circular_dependencies()` | Validator test suite | Bootstrap fails |
| Orchestrator names unique | `WiringValidator._check_duplicate_names()` | Validator test suite | Bootstrap fails |
| Health check method exists | **NOT ENFORCED** | Manual testing | Health endpoint returns errors |
| Response header on all outputs | `ResponseHeaderInjector` | `test_response_headers.py` | CORE-029 violation |
| TDD for IMPLEMENT/FIX | `TDDOrchestrator` | TDD orchestrator tests | Tests missing |

### 14.4.2 Required File Structure

```
CORTEX/
├── cortex/
│   ├── wiring/
│   │   └── specifications/
│   │       └── wiring.yaml        # REQUIRED
│   ├── orchestrators/
│   │   └── core/
│   │       └── *.py               # REQUIRED (as referenced in wiring.yaml)
│   └── mcp/
│       └── server.py              # REQUIRED for MCP operation
├── cortex_brain/
│   ├── tier0/
│   │   └── governance/
│   │       └── core-rules.yaml    # REQUIRED
│   └── tier2/
│       └── response-templates-index.yaml  # REQUIRED
└── cortex-registry/
    └── _cortex-master/
        └── index.yaml             # REQUIRED for phase tracking
```

### 14.4.3 Minimum Metadata Requirements

**Orchestrator Entry (wiring.yaml):**
```yaml
# REQUIRED fields
name: string              # Unique identifier
module: string            # Python module path
class: string             # Class name
tier: integer             # 1, 2, or 3
priority: integer         # Execution order
dependencies: list        # May be empty
capabilities: list        # May be empty
health_check: string      # Method name
```

**Phase Entry (index.yaml):**
```yaml
# REQUIRED fields
id: string                # e.g., "phase-48"
name: string              # Human-readable name
file: string              # Path to YAML specification
status: string            # planned | in_progress | completed
priority: string          # P0 | P1 | P2 | P3
```

### 14.4.4 Enforcement and Testing

| Invariant | Enforcement Level | Test Location |
|-----------|-------------------|---------------|
| wiring.yaml exists | **BLOCKING** (FileNotFoundError) | `tests/wiring/` |
| core-rules.yaml exists | **BLOCKING** (FileNotFoundError) | `tests/governance/` |
| No circular deps | **BLOCKING** (validation error) | `tests/wiring/` |
| Unique names | **BLOCKING** (validation error) | `tests/wiring/` |
| Health check | **WARNING** (logged) | Manual |
| Response header | **AUTOMATIC** (injected) | `tests/unit/` |

### 14.4.5 Drift Prevention

**Current State:** Drift prevention is **MANUAL**.

**Recommended Additions:**
1. Pre-commit hook running `WiringValidator.validate()`
2. CI job comparing wiring.yaml hash against deployed version
3. Automated test: `test_all_wired_orchestrators_importable()`
4. Schema validation on all YAML files in CI

---

## 14.5 Failure Mode & Effects Analysis (FMEA)

| # | Failure Mode | Trigger | Blast Radius | Probability | Detection | Mitigation | Rollback |
|---|-------------|---------|--------------|-------------|-----------|------------|----------|
| 1 | **wiring.yaml missing** | Deleted file, bad deployment | System won't start | LOW | Bootstrap fails with FileNotFoundError | CI validates file exists | Redeploy from Git |
| 2 | **Orchestrator import fails** | Broken module, missing dependency | That orchestrator unavailable | MEDIUM | LazyOrchestrator logs error | Pre-deployment import test | Fix and redeploy |
| 3 | **Circular dependency introduced** | Careless wiring.yaml edit | Bootstrap fails | LOW | WiringValidator catches | Pre-commit validation | Revert wiring.yaml |
| 4 | **core-rules.yaml corrupted** | Bad merge, encoding issue | Governance bypassed | LOW | YAML parse error | YAML lint in CI | Restore from Git |
| 5 | **MCP server port in use** | Port conflict | Server won't start | MEDIUM | Bind error at startup | Configurable port | Change port |
| 6 | **LENS analyzer timeout** | Large repo, slow disk | Analysis incomplete | MEDIUM | Timeout logged | Increase timeout, add cache | Skip analysis |
| 7 | **Health check method missing** | Typo in wiring.yaml | Health endpoint fails | MEDIUM | 500 error on /health | Validate method exists | Fix wiring.yaml |
| 8 | **Intent misclassification** | Edge case input | Wrong orchestrator called | MEDIUM | User reports wrong behavior | Improve routing rules | Manual override |
| 9 | **TDD test generation fails** | Invalid target file | IMPLEMENT blocked | LOW | TDDOrchestrator returns error | Fallback to manual | Manual test creation |
| 10 | **Enforcement rules outdated** | Rules not updated with code | False positives/negatives | MEDIUM | Manual audit | Quarterly rule review | Update rules |
| 11 | **Response template missing** | Template ID typo | Format error in output | LOW | Template resolver logs error | Template existence test | Add missing template |
| 12 | **Registry index desync** | Phase completed but index not updated | Dashboard shows wrong status | HIGH | Manual observation | Automated sync | Manual index update |
| 13 | **Path resolution fails** | No .git, no CORTEX_ROOT | Wrong paths, file not found | MEDIUM | FileNotFoundError | Always set CORTEX_ROOT | Set env var |
| 14 | **Audit logger write fails** | Permissions, disk full | Audit trail lost | LOW | Exception logged | Fallback to stdout | Fix permissions |
| 15 | **Graceful degradation fails** | All fallbacks fail | ComponentFailure exception | LOW | Exception propagates | Add more fallbacks | Manual intervention |

---

## 14.6 Self-Healing and Safe Degradation

### 14.6.1 Orchestrator Failure Behavior

**Implementation:** `cortex_brain/tier2/resilience.py`

```python
class GracefulDegradationFramework:
    def execute_with_degradation(self, component_name: str, primary: Callable, fallbacks: List[FallbackStrategy]) -> DegradedResponse:
        try:
            result = primary()
            return DegradedResponse(data=result, mode="primary")
        except Exception as e:
            for i, fallback in enumerate(fallbacks):
                try:
                    result = fallback.execute()
                    return DegradedResponse(data=result, mode=f"fallback_{i+1}")
                except Exception:
                    continue
            raise ComponentFailure(component_name, "All fallbacks failed")
```

**Behavior:**
1. Primary execution attempted
2. On failure, fallback strategies tried in order
3. If all fail, `ComponentFailure` exception raised
4. Partial results are marked with `DegradedResponse` wrapper

### 14.6.2 Rollback Capability

**Current State:** **LIMITED**.

- `RollbackOrchestrator` exists in wiring but rollback is **MANUAL**
- No automatic checkpoint before operations
- Git is the de facto rollback mechanism

**Recommended:** Add automatic git stash before IMPLEMENT/FIX operations.

### 14.6.3 Partial Output Safety

| Orchestrator | Partial Output Safe? | Reason |
|--------------|---------------------|--------|
| TDDOrchestrator | ✅ YES | Tests generated first, code second |
| RefactoringOrchestrator | ⚠️ PARTIAL | May leave code in intermediate state |
| PlanOrchestrator | ✅ YES | Read-only until commit |
| LENSOrchestrator | ✅ YES | Analysis only, no modifications |
| MasterOrchestrator | Depends on delegate | Inherits from called orchestrator |

### 14.6.4 Gate Failure Behavior

**Question:** Does CORTEX stop generation when gates fail?

**Answer:** **YES, for Tier 0 gates.**

```python
# enforcement_orchestrator.py
if enforcement_result.is_blocked():
    return Err(enforcement_result.violations)
    # Execution STOPS here
```

**Tier 1 gates (warnings):** Execution continues with warnings logged.

### 14.6.5 Incomplete Intelligence Context Safety

**Safeguard:** If LENS analysis fails, orchestrators receive empty context:

```python
# lens_orchestrator.py
def analyze_file(self, file_path: Path) -> Dict[str, Any]:
    try:
        # ... analysis logic
    except Exception as e:
        logger.error(f"LENS analysis failed: {e}")
        return {
            "git_analysis": {},
            "ast_analysis": {},
            "comment_analysis": {},
            "_metadata": {"error": str(e)}
        }
```

**Risk:** Orchestrators may make decisions without full context.  
**Mitigation:** Critical orchestrators (TDD, Enforcement) check for required context fields.

---

## 14.7 Security Brittleness

### 14.7.1 Secrets Exposure Risks

| Risk | Location | Likelihood | Mitigation |
|------|----------|------------|------------|
| Secrets in logs | `audit_logger.py` | LOW | Secrets not logged by design |
| Secrets in templates | `response-templates/` | LOW | Templates don't include secrets |
| API keys in artifacts | User code | MEDIUM | `SecurityThreatAnalyzer` detects |
| GitHub token exposure | `pr_review_engine.py` | MEDIUM | Loaded from env var only |

**Secrets Provider Interface:** `cortex/secrets/__init__.py`

```python
class ISecretsProvider(ABC):
    @abstractmethod
    def get(self, secret_id: str) -> Optional[str]:
        """Never returns secrets in logs."""
```

### 14.7.2 Prompt Injection Surface

| Vector | Risk | Mitigation |
|--------|------|------------|
| User request text | HIGH | IntentRouter validates structure |
| File contents analyzed by LENS | MEDIUM | AST parser, not eval |
| YAML files loaded | LOW | `yaml.safe_load()` only |
| MCP request parameters | MEDIUM | Pydantic validation |

**NOT IMPLEMENTED:** Sanitization of user request text before processing.

### 14.7.3 Dependency Trust

| Dependency | Trust Level | Risk |
|------------|-------------|------|
| Python stdlib | HIGH | Minimal risk |
| PyYAML | HIGH | No known vulns, safe_load used |
| Pydantic | HIGH | Trusted validation library |
| External knowledge sources | **N/A** | No external sources (all bundled) |

### 14.7.4 Permission Boundaries

| Operation | Permission Required | Enforcement |
|-----------|--------------------|--------------| 
| Read source files | Read access | OS-level |
| Write code files | Write access | **MCP-FIRST blocks direct writes for IMPLEMENT** |
| Read YAML configs | Read access | OS-level |
| Write audit logs | Write access | Fallback to stdout |
| Execute tests | Execute access | pytest invocation |

### 14.7.5 Auditability and Provenance

**Audit Trail:**
- AC markers in code: `AC_START`, `AC_COMPLETE`
- Audit logger: `cortex/infrastructure/enhanced_audit_logger.py`
- Git commits: Every operation should result in commit

**Provenance:**
- Orchestrator name logged with each operation
- User request preserved in context
- Timestamps on all operations

### 14.7.6 Threat Model

| Threat | Attack Vector | Impact | Mitigation | Control Status |
|--------|--------------|--------|------------|----------------|
| Malicious prompt injection | User request | Code execution | Input validation | **PARTIAL** |
| Secrets exfiltration | Log scraping | Data breach | No secrets in logs | ✅ IMPLEMENTED |
| Governance bypass | Direct file edit | Quality degradation | MCP-FIRST enforcement | ✅ IMPLEMENTED |
| Denial of service | Large file analysis | System hang | Timeouts on LENS | ✅ IMPLEMENTED |
| Config tampering | wiring.yaml edit | System compromise | Git tracking | ✅ IMPLEMENTED |
| Dependency confusion | Malicious package | Code execution | Requirements pinned | ✅ IMPLEMENTED |

---

## 14.8 Observability and Diagnostic Readiness

### 14.8.1 Telemetry

| Type | Implementation | Location |
|------|---------------|----------|
| Logging | Python `logging` module | Throughout codebase |
| Metrics | Prometheus `/metrics` endpoint | `cortex/mcp/metrics.py` |
| Traces | **NOT IMPLEMENTED** | N/A |
| Health checks | `/health` endpoint | `cortex/mcp/server.py` |

**Log Levels:**
- DEBUG: Detailed diagnostic
- INFO: Normal operation
- WARNING: Recoverable issues
- ERROR: Operation failures

### 14.8.2 Debugging Wiring Failures

**Debug Playbook:**

**Symptom: "Orchestrator not found"**
```bash
# 1. Check wiring.yaml has the orchestrator
grep "name: TDDOrchestrator" cortex/wiring/specifications/wiring.yaml

# 2. Verify module path is correct
python -c "from cortex.orchestrators.core.tdd_orchestrator import TDDOrchestrator"

# 3. Check registry loaded it
python -c "from cortex.wiring import get_registry; r = get_registry(); r.load(); print(r.list_orchestrators())"

# 4. Check for validation errors
python -c "from cortex.wiring.registry import WiringValidator; v = WiringValidator(); print(v.validate())"
```

**Symptom: "Health check failed"**
```bash
# 1. Check health endpoint directly
curl http://localhost:8443/health

# 2. Check specific orchestrator health
python -c "
from cortex.wiring import get_registry
r = get_registry()
r.load()
orch = r.get_orchestrator('TDDOrchestrator')
print(hasattr(orch, 'health_check'))
"

# 3. Run health check executor
python -c "
from cortex.wiring.health_check import HealthCheckExecutor
from cortex.wiring import get_registry
r = get_registry()
r.load()
orch = r.get_orchestrator('TDDOrchestrator')
result = HealthCheckExecutor.execute_health_check(orch)
print(result)
"
```

### 14.8.3 Decision Explanation

**How CORTEX proves routing decisions:**

```python
# IntentRouter returns RoutingDecision with explanation
RoutingDecision(
    intent_type=IntentType.IMPLEMENT,
    confidence_score=0.92,
    reasoning="Keywords matched: implement (100), new (90). Context: test_first signal detected.",
    keyword_matches=["implement", "new"],
    confidence_breakdown={
        "keyword_score": 0.9,
        "context_score": 0.8,
        "domain_score": 0.95
    }
)
```

### 14.8.4 Debug Playbook Summary

| Failure | First Check | Second Check | Third Check |
|---------|------------|--------------|-------------|
| System won't start | `wiring.yaml` exists? | Python version 3.9+? | Validation passes? |
| Orchestrator missing | In wiring.yaml? | Module importable? | Health check method exists? |
| Governance bypassed | core-rules.yaml valid? | EnforcementOrchestrator loaded? | Rules not empty? |
| Wrong routing | Intent classification correct? | Routing rules match? | Confidence threshold met? |
| LENS analysis empty | File exists? | Analyzers loaded? | Timeout not exceeded? |

---

## 14.9 Test Strategy for Brittleness

### 14.9.1 Schema Validation Tests

**Location:** `tests/wiring/`

```python
# test_wiring_schema.py
def test_wiring_yaml_has_required_structure():
    """Every orchestrator entry has required fields."""
    validator = WiringValidator()
    errors, _ = validator.validate()
    assert not errors, f"Schema violations: {errors}"

def test_orchestrator_names_match_pattern():
    """Orchestrator names end with 'Orchestrator'."""
    registry = get_registry()
    registry.load()
    for name in registry.list_orchestrators():
        assert name.endswith("Orchestrator"), f"Invalid name: {name}"
```

### 14.9.2 Registry/Wiring Consistency Tests

**Location:** `tests/wiring/test_production_verification.py`

```python
def test_all_wired_orchestrators_importable():
    """Every orchestrator in wiring.yaml can be imported."""
    registry = get_registry()
    registry.load()
    
    for name in registry.list_orchestrators():
        orch = registry.get_orchestrator(name)
        assert orch is not None, f"Failed to load: {name}"

def test_no_orphan_modules():
    """Every orchestrator module in cortex/orchestrators/ is in wiring.yaml."""
    wired_modules = get_wired_modules()
    all_modules = discover_orchestrator_modules()
    
    orphans = all_modules - wired_modules
    assert not orphans, f"Orphan modules not in wiring: {orphans}"
```

### 14.9.3 Smoke Tests per Orchestrator

```python
# test_orchestrator_smoke.py
@pytest.mark.parametrize("orch_name", [
    "TDDOrchestrator",
    "IntentRouter",
    "EnforcementOrchestrator",
    "MasterOrchestrator",
    "LENSSynthesis",
])
def test_orchestrator_health_check(orch_name):
    """Each orchestrator passes health check."""
    registry = get_registry()
    registry.load()
    orch = registry.get_orchestrator(orch_name)
    
    result = HealthCheckExecutor.execute_health_check(orch)
    assert result.status == HealthStatus.HEALTHY, f"{orch_name}: {result.message}"
```

### 14.9.4 Golden Path Regression Tests

```python
# test_golden_paths.py
def test_implement_intent_routes_to_tdd():
    """IMPLEMENT intent always routes to TDDOrchestrator."""
    router = IntentRouter()
    decision = router.classify_intent({
        "operation": "implement new feature",
        "description": "Add user authentication"
    })
    
    assert decision.intent_type == IntentType.IMPLEMENT
    assert decision.target_handler == "TDDOrchestrator"

def test_tdd_workflow_completes():
    """TDD workflow: RED → GREEN → REFACTOR."""
    tdd = TDDOrchestrator()
    result = tdd.execute({
        "target": "test_module.py",
        "test_file": "test_test_module.py"
    })
    
    assert result.is_ok()
    assert "tests" in result.unwrap()
```

### 14.9.5 Break-the-Wiring Tests

```python
# test_wiring_resilience.py
def test_missing_wiring_file_raises():
    """Missing wiring.yaml raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        GitBackedRegistry(wiring_file=Path("/nonexistent/wiring.yaml")).load()

def test_invalid_yaml_raises():
    """Invalid YAML in wiring.yaml raises error."""
    with tempfile.NamedTemporaryFile(suffix=".yaml") as f:
        f.write(b"invalid: yaml: content: [")
        f.flush()
        
        with pytest.raises(yaml.YAMLError):
            GitBackedRegistry(wiring_file=Path(f.name)).load()

def test_missing_orchestrator_returns_none():
    """Missing orchestrator returns None, not exception."""
    registry = get_registry()
    registry.load()
    
    result = registry.get_orchestrator("NonExistentOrchestrator")
    assert result is None

def test_circular_dependency_detected():
    """Circular dependency in wiring.yaml is detected."""
    # Create wiring with circular dep
    validator = WiringValidator(wiring_file=circular_dep_fixture)
    errors, _ = validator.validate()
    
    assert any("Circular dependency" in e for e in errors)
```

### 14.9.6 Test Integration Points

| Test Category | TDD Orchestrator | Operational Orchestrator | Validation Gates |
|--------------|------------------|--------------------------|------------------|
| Schema validation | ✅ Must pass before TDD | ✅ Must pass before ops | ✅ Part of enforcement |
| Wiring consistency | ✅ Required | ✅ Required | ✅ Pre-execution check |
| Smoke tests | ✅ Health check | ✅ Health check | N/A |
| Golden path | ✅ TDD workflow | ✅ Routing paths | N/A |
| Break-the-wiring | ✅ Error handling | ✅ Graceful degradation | ✅ Gate failure handling |

---

## 14.10 Minimal, High-Impact Fixes

### 14.10.1 Prioritized Fix List

| Priority | Fix | File(s) | LOC | Impact | Acceptance Criteria |
|----------|-----|---------|-----|--------|-------------------|
| **P0** | Add strict Pydantic schema for wiring.yaml entries | `orchestrator_factory.py` | ~50 | Catches config errors at load time | `pytest tests/wiring/test_wiring_schema.py` passes |
| **P0** | Validate all wired modules are importable at bootstrap | `git_backed_registry.py` | ~30 | No runtime ImportError surprises | All orchestrators load in test |
| **P0** | Block WARNING-level validations for production | `wiring_validator.py` | ~20 | No degraded deployments | Warnings become errors in CORTEX_ENV=production |
| **P1** | Add pre-commit hook for wiring validation | `.pre-commit-config.yaml` | ~15 | Catch errors before commit | Pre-commit runs validator |
| **P1** | Add wiring hash comparison in CI | `.github/workflows/` | ~30 | Detect unintentional wiring changes | CI fails on hash mismatch without explicit approval |
| **P1** | Sort glob results for determinism | Multiple files | ~10 | Deterministic file enumeration | `test_wiring_determinism.py` passes |
| **P2** | Add health check method validation | `wiring_validator.py` | ~20 | Health endpoint reliability | All health checks callable |
| **P2** | Document wiring.yaml schema in JSON Schema | `wiring-schema.json` | ~100 | IDE validation support | VS Code validates wiring.yaml |
| **P2** | Add tracing (OpenTelemetry) | `cortex/observability/` | ~200 | Debug complex failures | Traces visible in Jaeger |
| **P3** | Automatic git stash before IMPLEMENT | `tdd_orchestrator.py` | ~30 | Safe rollback | Stash created, can be popped |

### 14.10.2 Specific Files to Change

**P0 Changes:**

1. `cortex/wiring/orchestrator_factory.py`
   - Add `OrchestratorEntry(BaseModel)` with all required fields typed
   - Change `orchestrators: Dict[str, Any]` to `orchestrators: Dict[str, List[OrchestratorEntry]]`

2. `cortex/wiring/registry/git_backed_registry.py`
   - Add in `load()`:
     ```python
     for name, lazy_orch in self._orchestrators.items():
         try:
             lazy_orch.validate_importable()
         except ImportError as e:
             raise ValueError(f"Orchestrator {name} not importable: {e}")
     ```

3. `cortex/wiring/registry/wiring_validator.py`
   - Add `strict_mode` parameter to `validate()`
   - When `strict_mode=True` (or `CORTEX_ENV=production`), warnings become errors

### 14.10.3 Acceptance Criteria for "Deployment-Ready"

**MUST pass all of the following:**

- [ ] `pytest tests/wiring/` - 100% pass rate
- [ ] `python -c "from cortex.wiring import bootstrap_cortex; bootstrap_cortex()"` - No errors
- [ ] `WiringValidator().validate()` returns `([], [])` (no errors, no warnings) in production mode
- [ ] All orchestrators in wiring.yaml successfully instantiate
- [ ] Health endpoint returns 200 with all orchestrators healthy
- [ ] No `WARNING` or `ERROR` logs during bootstrap
- [ ] Wiring hash matches deployed version (or explicit approval for change)
- [ ] Pre-commit hook passes
- [ ] CI pipeline green

---

*Section 14 Complete. All claims reference actual CORTEX files or explicitly state "NOT IMPLEMENTED".*
