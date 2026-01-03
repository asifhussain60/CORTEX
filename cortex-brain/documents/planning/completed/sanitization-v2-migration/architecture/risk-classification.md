# Sanitization v2 - 5-Level Risk Classification System

**Created:** January 3, 2026  
**Phase:** 1 - Design Architecture  
**Version:** 1.0

---

## 🎯 Overview

The risk classification system assigns a risk level (SAFE → CRITICAL) to each domain term transformation based on its potential impact on code functionality, external contracts, and system behavior.

**Purpose:**
- Enable intelligent auto-approval for low-risk changes
- Require human review for high-risk transformations
- Optimize validation strategy (build-only for SAFE, full suite for CRITICAL)
- Support progressive transformation (SAFE first, CRITICAL last)

---

## 📊 Risk Level Taxonomy

### Level 1: SAFE (Auto-Approve ✅)

**Definition:** Changes with zero functional impact, affecting only documentation or non-executable content.

**Examples:**
- Comment text changes
- Docstring updates
- README/markdown documentation
- Code examples in comments
- ASCII art, headers, banners
- Type hints (without runtime impact)

**Validation Strategy:**
- Build verification only
- No test execution required
- Instant approval

**Auto-Approval:** ✅ Yes (if enabled in config)

**Transformation Risk:** Extremely low (0% chance of breakage)

---

### Level 2: LOW_RISK (Auto-Approve ✅)

**Definition:** Changes to internal implementation details with limited scope, isolated to single functions/methods.

**Examples:**
- Local variable renames
- Private method names (`_method_name`)
- Internal helper function names
- Loop variables (`i`, `j`, `k` → generic names)
- Temporary variables
- Lambda parameter names
- List comprehension variables

**Validation Strategy:**
- Build verification
- Smoke test execution (if available)
- Static analysis (type checking)

**Auto-Approval:** ✅ Yes (if enabled in config)

**Transformation Risk:** Very low (1-5% chance of breakage)

**Exclusions:**
- Variables used in:
  - Reflection/metaprogramming (`getattr`, `setattr`)
  - Serialization (JSON keys, pickle)
  - Dynamic imports
  - Logging with variable names

---

### Level 3: MEDIUM (Requires Approval ❌)

**Definition:** Changes to public interfaces within a module, affecting how components interact.

**Examples:**
- Public method names (non-prefixed)
- Public class names
- Module-level function names
- Class attributes (public)
- Enum member names
- Constants (`CONSTANT_NAME`)
- Configuration keys
- Exception class names

**Validation Strategy:**
- Full build verification
- Complete test suite execution
- Integration test validation
- Coverage comparison (must maintain ≥baseline)

**Auto-Approval:** ❌ No (requires user review)

**Transformation Risk:** Moderate (10-20% chance of breakage)

**Review Questions:**
1. Does this method/class have external callers?
2. Is this used in configuration files?
3. Is this part of a documented API?
4. Are there tests that reference this by name?

---

### Level 4: HIGH (Requires Approval ❌ + Extended Validation)

**Definition:** Changes to cross-module interfaces, public APIs, or externally visible contracts.

**Examples:**
- Module names (`src/module_name.py`)
- Package names (`src/package/`)
- CLI command names
- API endpoint names (REST, GraphQL)
- Environment variable names
- Database table/column names (in code)
- File paths (hardcoded)
- Import paths
- Entry point functions (called externally)

**Validation Strategy:**
- Full build verification
- Complete test suite execution
- Integration test validation
- E2E test validation (if available)
- API contract validation
- Backward compatibility check
- Documentation review

**Auto-Approval:** ❌ No (requires user review + extended validation)

**Transformation Risk:** High (20-40% chance of breakage)

**Review Questions:**
1. Is this a public API consumed by external systems?
2. Will existing clients break after this change?
3. Are there deployment dependencies?
4. Does documentation need updates?
5. Do CI/CD pipelines reference this by name?

---

### Level 5: CRITICAL (Requires Approval ❌ + Manual Review)

**Definition:** Changes to system entry points, external contracts, or core infrastructure with catastrophic failure potential.

**Examples:**
- Application entry points (`main()`, `__main__`)
- CLI script names (executable files)
- Configuration file keys (YAML, JSON, TOML)
- External service contracts (webhooks, callbacks)
- Database migrations (schema references)
- Message queue topics/exchanges
- RPC/gRPC service names
- Docker image names
- Deployment script references
- License headers with legal implications

**Validation Strategy:**
- Full build verification
- Complete test suite execution
- Integration test validation
- E2E test validation
- Manual smoke testing
- Deployment simulation (staging)
- Rollback plan validation
- Documentation audit

**Auto-Approval:** ❌ No (requires user review + manual testing)

**Transformation Risk:** Critical (40-60% chance of breakage without review)

**Review Questions:**
1. Will this break production systems?
2. Are there external dependencies (customers, partners)?
3. Is this referenced in deployment infrastructure?
4. Does this require coordinated releases?
5. Are there compliance/legal implications?
6. Is there a rollback plan?

---

## 🧠 Classification Algorithm

### Rule-Based Classification

```python
def classify_risk(term: DomainTerm, context: CodeContext) -> RiskLevel:
    """
    Classify transformation risk using rule-based heuristics.
    
    Args:
        term: Domain term to classify
        context: Code context (AST node, scope, usage)
    
    Returns:
        RiskLevel enum (SAFE, LOW_RISK, MEDIUM, HIGH, CRITICAL)
    """
    
    # CRITICAL: Entry points, external contracts
    if is_entry_point(term, context):
        return RiskLevel.CRITICAL
    if is_external_contract(term, context):
        return RiskLevel.CRITICAL
    if is_deployment_reference(term, context):
        return RiskLevel.CRITICAL
    
    # HIGH: Module names, public APIs
    if is_module_name(term):
        return RiskLevel.HIGH
    if is_public_api(term, context):
        return RiskLevel.HIGH
    if is_cli_command(term):
        return RiskLevel.HIGH
    
    # MEDIUM: Public methods/classes
    if is_public_method(term, context):
        return RiskLevel.MEDIUM
    if is_public_class(term, context):
        return RiskLevel.MEDIUM
    if is_configuration_key(term, context):
        return RiskLevel.MEDIUM
    
    # LOW_RISK: Private methods, local variables
    if is_private_method(term, context):
        return RiskLevel.LOW_RISK
    if is_local_variable(term, context):
        return RiskLevel.LOW_RISK
    
    # SAFE: Comments, docstrings
    if is_comment(term, context):
        return RiskLevel.SAFE
    if is_docstring(term, context):
        return RiskLevel.SAFE
    
    # Default: MEDIUM (conservative)
    return RiskLevel.MEDIUM
```

### Context Signals

**Entry Point Detection:**
- `if __name__ == "__main__"`
- Function named `main()` at module level
- CLI decorators (`@click.command`, `@typer.command`)
- WSGI/ASGI application objects

**External Contract Detection:**
- Decorator analysis (`@api_route`, `@endpoint`, `@webhook`)
- Configuration file parsing (YAML keys, env vars)
- Database model inspection (table names, column names)
- Import statements in external documentation

**Public API Detection:**
- Method/class without leading underscore
- Listed in `__all__`
- Documented in public docs
- Imported by external modules

**Scope Analysis:**
- Function-local scope → LOW_RISK
- Class-level scope → MEDIUM
- Module-level scope → HIGH
- Package-level scope → CRITICAL

---

## 📋 Approval Workflow by Risk Level

### Auto-Approval Path (SAFE + LOW_RISK)

```
Transformation Request
  ↓
Risk Classification
  ↓
IF risk_level <= LOW_RISK AND auto_approve_enabled:
  ├─→ Apply transformation
  ├─→ Run lightweight validation (build only)
  └─→ Continue to next transformation
ELSE:
  └─→ Interactive approval workflow
```

### Interactive Approval Path (MEDIUM+)

```
Transformation Request
  ↓
Risk Classification
  ↓
IF risk_level >= MEDIUM:
  ├─→ Present transformation preview
  ├─→ Show risk analysis
  ├─→ Display affected files/functions
  ├─→ Wait for user decision
  │   ├─→ APPROVE: Apply transformation
  │   ├─→ SKIP: Skip this transformation
  │   └─→ ABORT: Cancel entire workflow
  └─→ Continue to next transformation
```

---

## 🎯 Validation Strategies by Risk Level

| Risk Level | Build | Unit Tests | Integration Tests | E2E Tests | Manual Review |
|------------|-------|------------|-------------------|-----------|---------------|
| SAFE | ✅ | ⏭️ Skip | ⏭️ Skip | ⏭️ Skip | ❌ |
| LOW_RISK | ✅ | ✅ Smoke | ⏭️ Skip | ⏭️ Skip | ❌ |
| MEDIUM | ✅ | ✅ Full | ✅ | ⏭️ Skip | ❌ |
| HIGH | ✅ | ✅ Full | ✅ | ✅ | ❌ |
| CRITICAL | ✅ | ✅ Full | ✅ | ✅ | ✅ Required |

---

## 📊 Risk Distribution Analysis

**Typical Project Breakdown:**
- **SAFE:** 20-30% (comments, docs)
- **LOW_RISK:** 40-50% (local vars, private methods)
- **MEDIUM:** 15-25% (public methods, classes)
- **HIGH:** 5-10% (modules, APIs)
- **CRITICAL:** 1-5% (entry points, contracts)

**Impact on Approval Workflow:**
- **Auto-Approved:** 60-80% of transformations (SAFE + LOW_RISK)
- **Interactive Review:** 20-40% of transformations (MEDIUM+)
- **Manual Testing:** 1-5% of transformations (CRITICAL)

---

## 🛡️ Conservative Bias

**When in Doubt, Classify Higher:**
- Ambiguous scope → Assume public (MEDIUM)
- Unknown context → Assume external (HIGH)
- Complex AST patterns → Assume critical (CRITICAL)
- Reflection/metaprogramming → Assume high risk (HIGH)

**Rationale:**
- False positives (over-classification) = extra approval prompts (minor UX impact)
- False negatives (under-classification) = production breakage (catastrophic)
- User can manually downgrade risk during approval

---

## 🧪 Testing Risk Classification

**Unit Tests:**
- Test each classification rule independently
- Verify context signal detection
- Validate conservative bias

**Integration Tests:**
- Test realistic code samples
- Verify distribution (60-80% auto-approved)
- Test edge cases (metaprogramming, decorators)

**Validation:**
- Run on real-world projects
- Compare auto-approved % with expectations
- Measure false positive/negative rates

---

## 📈 Metrics & Monitoring

**Track During Execution:**
- Distribution by risk level
- Auto-approval rate
- User overrides (manual upgrades/downgrades)
- Transformation failures by risk level
- Validation failures by risk level

**Post-Execution Analysis:**
- Identify patterns in false positives
- Tune classification rules
- Update exclusion lists
- Improve context detection

---

## 🎯 Success Criteria

**Classification System Complete When:**
- ✅ 5 risk levels defined with clear criteria
- ✅ Classification algorithm specified
- ✅ Context signals documented
- ✅ Approval workflows mapped
- ✅ Validation strategies defined
- ✅ Conservative bias policy documented
- ✅ Testing approach specified

---

**Next:** Workflow diagram + progressive analysis pipeline design
