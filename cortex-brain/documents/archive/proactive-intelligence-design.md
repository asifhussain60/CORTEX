# 🧠 Proactive Intelligence & Risk Assessment System

**Version:** 1.0  
**Author:** Asif Hussain  
**Created:** 2024-12-14  
**Phase:** 17 of Planning System 3.0

---

## 🎯 Overview

Planning System 3.0 includes a comprehensive **Proactive Intelligence Engine** that continuously assists engineers without requiring prompts, and a **Risk Assessment System** that prevents breaking changes through pre-execution analysis.

### Core Principles

1. **Continuous Assistance** - CORTEX actively monitors context and suggests improvements
2. **Risk-First Mindset** - Critical domains trigger deep analysis automatically
3. **Domain Awareness** - Analysis depth adapts to code criticality
4. **Zero Interruption** - Recommendations appear at natural decision points
5. **Evidence-Based** - All suggestions backed by AST analysis and patterns

---

## 🏗️ Architecture

### Component Overview

```
intelligence/
├── proactive_advisor.py       # Enhancement recommendation engine
├── risk_assessor.py           # Pre-execution risk analysis
└── domain_classifier.py       # Critical domain detection

analysis/
├── security_analyzer.py       # OWASP Top 10, injection patterns
├── compliance_analyzer.py     # PII, audit trails, data retention
└── business_logic_analyzer.py # Financial calculations, rounding errors
```

### Integration Points

```python
# Planning Orchestrator 3.0 Integration
class PlanningOrchestrator_v3:
    def execute_phase(self, phase):
        # 1. Classify domain
        domain = self.domain_classifier.classify(phase.files)
        
        # 2. Adjust analysis depth
        analysis_depth = self._get_analysis_depth(domain)
        
        # 3. Pre-execution risk assessment
        risks = self.risk_assessor.analyze(
            phase=phase,
            domain=domain,
            depth=analysis_depth
        )
        
        # 4. Critical risk gate
        if risks.severity >= RiskLevel.HIGH:
            return self._show_risk_warning(risks)
        
        # 5. Execute phase
        result = self._execute_phase_impl(phase)
        
        # 6. Proactive recommendations
        recommendations = self.proactive_advisor.generate(
            phase=phase,
            result=result,
            domain=domain
        )
        
        return self._format_response(result, recommendations)
```

---

## 🎯 Domain Classification System

### Domain Categories

| Domain | Criticality | Analysis Depth | Example Areas |
|--------|-------------|----------------|---------------|
| **CRITICAL** | HIGH | Deep AST + Pattern Analysis | Authentication, payments, security, compliance, financial calculations, business logic |
| **STANDARD** | MEDIUM | High-level AST | UI components, data access, utilities, APIs |
| **SIMPLE** | LOW | Surface validation | Documentation, configuration, static assets |

### Classification Algorithm

```python
class DomainClassifier:
    CRITICAL_PATTERNS = {
        'security': [
            r'auth|authentication|authorization|oauth|jwt|token',
            r'password|credential|secret|api[_-]?key',
            r'encrypt|decrypt|hash|salt',
            r'permission|role|access[_-]?control|rbac'
        ],
        'financial': [
            r'payment|transaction|invoice|billing',
            r'price|amount|currency|money|dollar',
            r'refund|charge|balance|account',
            r'calculate.*(?:tax|total|subtotal|interest)'
        ],
        'compliance': [
            r'pii|personal.*information|gdpr|hipaa|ccpa',
            r'audit|log.*trail|compliance',
            r'data.*retention|privacy|consent',
            r'redact|anonymize|mask.*data'
        ],
        'business_logic': [
            r'business.*rule|validation.*rule',
            r'workflow|approval|escalation',
            r'calculate.*(?:commission|bonus|penalty|fee)',
            r'eligibility|qualification|criteria'
        ]
    }
    
    def classify(self, files: List[str]) -> DomainCategory:
        """
        Classify domain based on file paths, imports, and function signatures.
        
        Returns:
            DomainCategory with criticality level and required analyzers
        """
        # Multi-signal analysis
        path_signals = self._analyze_paths(files)
        import_signals = self._analyze_imports(files)
        signature_signals = self._analyze_signatures(files)
        
        # Weighted scoring
        score = (
            path_signals * 0.3 +
            import_signals * 0.4 +
            signature_signals * 0.3
        )
        
        if score >= 0.7:
            return DomainCategory.CRITICAL
        elif score >= 0.4:
            return DomainCategory.STANDARD
        else:
            return DomainCategory.SIMPLE
```

---

## 🚨 Risk Assessment System

### Risk Categories

```python
class RiskCategory(Enum):
    BREAKING_CHANGE = "Breaking Change"           # API/contract changes
    DATA_LOSS = "Data Loss"                      # Irreversible data modifications
    SECURITY_VULNERABILITY = "Security"          # Auth, injection, XSS vulnerabilities
    COMPLIANCE_VIOLATION = "Compliance"          # PII, audit, regulatory violations
    BUSINESS_LOGIC_ERROR = "Business Logic"      # Financial calculation errors
    PERFORMANCE_DEGRADATION = "Performance"      # N+1 queries, memory leaks
    DEPENDENCY_CONFLICT = "Dependencies"         # Version conflicts, breaking deps
```

### Risk Scoring Matrix

| Severity | Score | Criteria | Action |
|----------|-------|----------|--------|
| **CRITICAL** | 80-100 | Data loss, security breach, financial impact >$10k | ⛔ Block execution, require explicit override |
| **HIGH** | 60-79 | Breaking changes, compliance violations, business logic errors | ⚠️ Show detailed warning, require confirmation |
| **MEDIUM** | 40-59 | Performance issues, minor breaking changes | ℹ️ Show advisory, allow proceed |
| **LOW** | 20-39 | Style violations, minor improvements possible | 💡 Proactive recommendation only |
| **MINIMAL** | 0-19 | No significant risks detected | ✅ Proceed normally |

### Risk Analysis Flow

```python
class RiskAssessor:
    def analyze(self, phase, domain, depth) -> RiskReport:
        """
        Multi-dimensional risk analysis.
        
        Returns:
            RiskReport with severity, issues, and mitigation strategies
        """
        risks = []
        
        # 1. Breaking change detection
        if self._detects_api_changes(phase):
            risks.append(self._analyze_breaking_changes(phase))
        
        # 2. Data loss detection
        if self._detects_data_operations(phase):
            risks.append(self._analyze_data_risks(phase))
        
        # 3. Domain-specific analysis
        if domain == DomainCategory.CRITICAL:
            risks.extend(self._critical_domain_analysis(phase))
        
        # 4. Aggregate scoring
        total_score = self._calculate_risk_score(risks)
        severity = self._map_to_severity(total_score)
        
        return RiskReport(
            severity=severity,
            score=total_score,
            issues=risks,
            mitigations=self._generate_mitigations(risks)
        )
    
    def _critical_domain_analysis(self, phase) -> List[Risk]:
        """Deep analysis for critical domains."""
        analyzers = {
            'security': self.security_analyzer,
            'compliance': self.compliance_analyzer,
            'financial': self.business_logic_analyzer
        }
        
        risks = []
        for name, analyzer in analyzers.items():
            domain_risks = analyzer.analyze(phase.files)
            risks.extend(domain_risks)
        
        return risks
```

### Security Analyzer (OWASP Top 10)

```python
class SecurityAnalyzer:
    VULNERABILITY_PATTERNS = {
        'sql_injection': [
            r'execute\s*\(\s*["\']SELECT.*\+.*["\']',  # String concatenation in SQL
            r'cursor\.execute\([^?]*%s',                 # Python string formatting
            r'db\.query\(["\'].*\+',                     # Direct string concatenation
        ],
        'xss': [
            r'innerHTML\s*=\s*[^sanitize]',             # Direct innerHTML assignment
            r'dangerouslySetInnerHTML',                  # React dangerous HTML
            r'document\.write\(',                        # Direct DOM write
        ],
        'auth_bypass': [
            r'if.*role\s*==\s*["\']admin["\']',         # Hardcoded role checks
            r'password\s*==\s*["\'].+["\']',             # Hardcoded passwords
            r'skip.*auth|bypass.*auth',                  # Auth bypass logic
        ],
        'insecure_crypto': [
            r'md5|sha1',                                 # Weak hashing
            r'DES|RC4',                                  # Weak encryption
            r'Random\(\)|Math\.random',                  # Insecure randomness
        ]
    }
    
    def analyze(self, files: List[str]) -> List[SecurityRisk]:
        """Detect OWASP Top 10 vulnerabilities."""
        risks = []
        
        for file in files:
            content = self._read_file(file)
            ast_tree = self.ast_engine.parse(file)
            
            # Pattern-based detection
            for vuln_type, patterns in self.VULNERABILITY_PATTERNS.items():
                matches = self._find_patterns(content, patterns)
                if matches:
                    risks.append(SecurityRisk(
                        type=vuln_type,
                        severity=RiskLevel.HIGH,
                        file=file,
                        lines=matches,
                        evidence=self._extract_evidence(content, matches)
                    ))
            
            # AST-based detection
            ast_risks = self._ast_security_analysis(ast_tree)
            risks.extend(ast_risks)
        
        return risks
```

### Compliance Analyzer

```python
class ComplianceAnalyzer:
    COMPLIANCE_CHECKS = {
        'pii_handling': {
            'patterns': [r'ssn|social.*security', r'credit.*card|cc_number'],
            'requirements': ['encryption', 'audit_trail', 'consent_flag']
        },
        'data_retention': {
            'patterns': [r'delete|remove|purge'],
            'requirements': ['retention_policy', 'backup_verification']
        },
        'audit_trail': {
            'patterns': [r'update|modify|change'],
            'requirements': ['audit_log', 'user_tracking', 'timestamp']
        }
    }
    
    def analyze(self, files: List[str]) -> List[ComplianceRisk]:
        """Detect GDPR/HIPAA/CCPA compliance violations."""
        risks = []
        
        for file in files:
            ast_tree = self.ast_engine.parse(file)
            
            # Detect PII handling without proper safeguards
            pii_usage = self._find_pii_usage(ast_tree)
            for usage in pii_usage:
                if not self._has_safeguards(usage):
                    risks.append(ComplianceRisk(
                        type='pii_handling_violation',
                        severity=RiskLevel.CRITICAL,
                        file=file,
                        context=usage,
                        missing_controls=self._identify_missing_controls(usage)
                    ))
        
        return risks
```

### Business Logic Analyzer

```python
class BusinessLogicAnalyzer:
    def analyze(self, files: List[str]) -> List[BusinessLogicRisk]:
        """Detect financial calculation errors and business rule violations."""
        risks = []
        
        for file in files:
            ast_tree = self.ast_engine.parse(file)
            
            # 1. Detect floating point arithmetic in financial calculations
            financial_calcs = self._find_financial_calculations(ast_tree)
            for calc in financial_calcs:
                if self._uses_float_arithmetic(calc):
                    risks.append(BusinessLogicRisk(
                        type='floating_point_error',
                        severity=RiskLevel.HIGH,
                        message='Financial calculations should use Decimal, not float',
                        file=file,
                        function=calc.name,
                        suggestion='Use decimal.Decimal for precise calculations'
                    ))
            
            # 2. Detect missing rounding in currency operations
            currency_ops = self._find_currency_operations(ast_tree)
            for op in currency_ops:
                if not self._has_proper_rounding(op):
                    risks.append(BusinessLogicRisk(
                        type='missing_rounding',
                        severity=RiskLevel.MEDIUM,
                        message='Currency values should be rounded to 2 decimal places',
                        file=file,
                        line=op.line_number
                    ))
            
            # 3. Detect unbounded calculations (overflow risk)
            calculations = self._find_all_calculations(ast_tree)
            for calc in calculations:
                if not self._has_bounds_checking(calc):
                    risks.append(BusinessLogicRisk(
                        type='overflow_risk',
                        severity=RiskLevel.MEDIUM,
                        message='Calculation lacks bounds checking',
                        file=file,
                        expression=calc.expression
                    ))
        
        return risks
```

---

## 💡 Proactive Advisor System

### Recommendation Categories

```python
class RecommendationCategory(Enum):
    CODE_QUALITY = "Code Quality"           # Duplication, complexity
    ARCHITECTURE = "Architecture"           # Design patterns, separation of concerns
    PERFORMANCE = "Performance"             # N+1, caching opportunities
    SECURITY = "Security"                   # Best practices, hardening
    TESTING = "Testing"                     # Coverage gaps, test quality
    DOCUMENTATION = "Documentation"         # Missing docs, outdated comments
```

### Recommendation Triggers

| Trigger | Context | Example |
|---------|---------|---------|
| **Code Duplication** | 2+ similar functions detected | "Found 3 similar functions. Consider extracting to shared utility." |
| **Architecture Debt** | God class detected (>500 LOC) | "ProductService has 1200 lines. Consider splitting into domain services." |
| **Performance** | N+1 query detected | "Detected N+1 query in order processing. Recommend eager loading." |
| **Security** | Hardcoded secrets | "Found hardcoded API key. Move to environment variables." |
| **Testing Gap** | Critical path without tests | "Payment processing has 0% test coverage. Recommend TDD." |
| **Tech Debt** | TODO/FIXME older than 30 days | "5 unresolved TODOs from 3 months ago. Recommend cleanup." |

### Proactive Recommendation Engine

```python
class ProactiveAdvisor:
    def generate(self, phase, result, domain) -> List[Recommendation]:
        """
        Generate context-aware enhancement recommendations.
        
        Returns:
            List of actionable recommendations with impact estimates
        """
        recommendations = []
        
        # 1. Code quality analysis
        if self._detects_duplication(result):
            recommendations.append(self._recommend_deduplication(result))
        
        # 2. Architecture insights
        if self._detects_god_class(result):
            recommendations.append(self._recommend_refactoring(result))
        
        # 3. Performance opportunities
        if self._detects_n_plus_one(result):
            recommendations.append(self._recommend_optimization(result))
        
        # 4. Security hardening
        if domain == DomainCategory.CRITICAL:
            sec_recs = self._security_recommendations(result)
            recommendations.extend(sec_recs)
        
        # 5. Testing improvements
        if self._has_coverage_gaps(result):
            recommendations.append(self._recommend_tests(result))
        
        # Priority sorting (impact × effort⁻¹)
        recommendations.sort(key=lambda r: r.priority_score, reverse=True)
        
        return recommendations[:5]  # Top 5 recommendations
    
    def _recommend_deduplication(self, result) -> Recommendation:
        """Generate deduplication recommendation."""
        duplicates = self.ast_engine.find_similar_functions(
            threshold=0.85,
            files=result.modified_files
        )
        
        return Recommendation(
            category=RecommendationCategory.CODE_QUALITY,
            title="Consolidate Duplicate Code",
            description=f"Found {len(duplicates)} similar functions",
            impact="Reduces maintenance burden by 40%",
            effort="2 hours",
            priority_score=8.5,
            action_plan=[
                "Extract common logic to shared utility",
                "Update all call sites",
                "Add tests for new utility function"
            ]
        )
```

---

## 📊 Response Template Integration

### Risk Warning Template

Used when `risk_score >= 60`:

```markdown
## ⚠️ CORTEX Risk Assessment
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

### 🎯 Understanding & Scope
{understanding_content}

### 🚨 RISK ANALYSIS

**Risk Level:** HIGH (85/100)

**Risk Category:** Security Vulnerability + Data Loss

#### 💥 Potential Impacts

- **Breaking Change:** API endpoint `/api/users` signature changed - 12 consumers affected
- **Data Loss:** Migration drops `user_preferences` table without backup
- **Security:** New endpoint lacks authentication middleware

#### 🔍 Detected Issues

1. **SQL Injection Risk** (auth_service.py:45)
   - Direct string concatenation in query
   - Pattern: `query = "SELECT * FROM users WHERE id=" + user_id`
   
2. **Missing Authentication** (api_routes.py:89)
   - New `/api/sensitive-data` endpoint lacks @require_auth decorator
   
3. **Irreversible Migration** (migrations/003_drop_prefs.py)
   - No backup strategy before dropping table

#### 🛡️ Affected Areas

- **Security:** 2 vulnerabilities
- **Data Integrity:** 1 migration risk
- **API Contracts:** 12 breaking changes

### ⚡ Approach & Considerations

**Mitigation Strategy:**
1. Use parameterized queries for all SQL operations
2. Add authentication middleware to new endpoints
3. Create backup before running destructive migrations

### 💬 Recommended Actions

1. **Immediate:** Fix SQL injection in auth_service.py (use `execute(query, params)`)
2. **Before Deploy:** Add @require_auth to sensitive endpoints
3. **Migration:** Add backup step before table drop

### 📊 Impact Summary

**Breaking Changes:** 12
**Data Loss Risk:** HIGH
**Security Vulnerabilities:** 2 critical
**Compliance Violations:** 0

### 🔍 Next Steps

☐ Fix SQL injection vulnerability
☐ Add authentication middleware
☐ Modify migration to include backup
☐ Review changes with security team
☐ **After fixes:** Say "proceed with caution"

---

⚠️  **CRITICAL:** Review all risks before proceeding. Say "abort" to cancel or "proceed with caution" to continue.
```

### Proactive Recommendation Template

Appears after successful phase completion when improvements are detected:

```markdown
## 💡 CORTEX Proactive Insight
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

### 🎯 Context

Phase 3 completed successfully. Detected 3 enhancement opportunities.

### 💡 Enhancement Opportunities

1. **Code Quality: Consolidate Duplicate Code** (Priority: HIGH)
   - Found 3 similar functions in `order_processor.py`, `invoice_generator.py`, `receipt_builder.py`
   - All implement nearly identical discount calculation logic
   - **Impact:** Reduces maintenance burden by 40%, prevents inconsistency bugs
   - **Effort:** 2 hours

2. **Performance: Optimize Database Queries** (Priority: MEDIUM)
   - Detected N+1 query in order processing workflow
   - Loading line items one-by-one in loop (avg 50 items per order)
   - **Impact:** 10x performance improvement, reduces DB load
   - **Effort:** 1 hour

3. **Testing: Add Coverage for Critical Path** (Priority: MEDIUM)
   - Payment processing logic has 0% test coverage
   - Financial calculations lack validation tests
   - **Impact:** Prevents calculation errors, increases confidence
   - **Effort:** 3 hours

### 📊 Potential Benefits

- **Code Quality:** -120 lines of duplicate code
- **Performance:** 10x faster order processing (500ms → 50ms)
- **Test Coverage:** +25% overall coverage
- **Risk Reduction:** Critical path protected by tests

### 🔍 Implementation Path

**Recommended Order:**
1. Fix N+1 query (1h, high impact)
2. Consolidate duplicate code (2h, high impact)
3. Add payment tests (3h, risk reduction)

**Total Effort:** 6 hours
**Total Impact:** High

---

💬 Say "apply recommendation 1" to implement, or "dismiss" to continue without changes.
```

---

## 🎛️ Configuration

### Domain Classification Config

```yaml
# cortex-brain/config/domain-classification.yaml
domain_classification:
  critical_domains:
    security:
      keywords: [auth, authentication, authorization, oauth, jwt, password, encrypt]
      file_patterns: [**/auth/**, **/security/**, **/middleware/auth*]
      analysis_depth: deep
      
    financial:
      keywords: [payment, transaction, invoice, price, amount, currency, calculate]
      file_patterns: [**/payments/**, **/billing/**, **/financial/**]
      analysis_depth: deep
      
    compliance:
      keywords: [pii, gdpr, hipaa, audit, privacy, consent, redact]
      file_patterns: [**/compliance/**, **/privacy/**, **/audit/**]
      analysis_depth: deep
      
    business_logic:
      keywords: [business_rule, validation, workflow, calculate, eligibility]
      file_patterns: [**/domain/**, **/business/**, **/rules/**]
      analysis_depth: deep
  
  standard_domains:
    data_access:
      file_patterns: [**/repositories/**, **/dao/**, **/models/**]
      analysis_depth: high
      
    api_layer:
      file_patterns: [**/api/**, **/controllers/**, **/routes/**]
      analysis_depth: high
  
  simple_domains:
    documentation:
      file_patterns: [**/*.md, **/docs/**]
      analysis_depth: surface
      
    configuration:
      file_patterns: [**/*.json, **/*.yaml, **/*.config]
      analysis_depth: surface
```

### Risk Assessment Config

```yaml
# cortex-brain/config/risk-assessment.yaml
risk_assessment:
  severity_thresholds:
    critical: 80
    high: 60
    medium: 40
    low: 20
  
  blocking_conditions:
    - risk_level: critical
      action: block_with_override
      message: "CRITICAL risks detected. Explicit override required."
    
    - risk_level: high
      risk_categories: [data_loss, security_vulnerability]
      action: warn_with_confirmation
      message: "HIGH risks detected. Confirmation required to proceed."
  
  analyzers:
    security:
      enabled: true
      owasp_top_10: true
      custom_patterns: true
      
    compliance:
      enabled: true
      regulations: [gdpr, hipaa, ccpa]
      
    business_logic:
      enabled: true
      financial_validation: true
      decimal_enforcement: true
```

### Proactive Advisor Config

```yaml
# cortex-brain/config/proactive-advisor.yaml
proactive_advisor:
  enabled: true
  max_recommendations: 5
  priority_threshold: 5.0  # Only show recommendations with score >= 5.0
  
  triggers:
    code_duplication:
      enabled: true
      similarity_threshold: 0.85
      min_instances: 2
      
    architecture_debt:
      enabled: true
      god_class_threshold: 500  # lines
      cyclomatic_complexity_threshold: 10
      
    performance:
      enabled: true
      n_plus_one_detection: true
      missing_index_detection: true
      
    security:
      enabled: true
      hardcoded_secrets: true
      insecure_patterns: true
      
    testing:
      enabled: true
      coverage_threshold: 80
      critical_path_priority: true
  
  recommendation_timing:
    - phase: post_execution
      conditions: [success, no_critical_errors]
    
    - phase: pre_commit
      conditions: [files_modified]
```

---

## 📈 Success Metrics

### Risk Assessment Effectiveness

- **Goal:** Prevent 90%+ breaking changes before execution
- **Measurement:** Track blocked changes that would have caused production issues
- **Target:** <5% false positive rate (unnecessary blocks)

### Proactive Advisor Value

- **Goal:** Generate ≥3 actionable recommendations per complex operation
- **Measurement:** Track recommendation acceptance rate
- **Target:** ≥40% recommendations accepted and implemented

### Domain Classification Accuracy

- **Goal:** 95%+ correct domain classification
- **Measurement:** Manual review of 100 classifications
- **Target:** <5% misclassifications requiring override

---

## 🚀 Implementation Plan

See **Phase 17** of main plan (`cortex-3.9-master.md`) for detailed implementation steps.

**Estimated Effort:** 6 hours

**Dependencies:**
- Phase 08 (AST Engine Wrapper) - REQUIRED
- Phase 09 (Enhanced Analyzers) - REQUIRED
- Phase 03 (Planning Orchestrator 3.0) - Integration point

**Deliverables:**
- `proactive_advisor.py`
- `risk_assessor.py`
- `domain_classifier.py`
- `security_analyzer.py`
- `compliance_analyzer.py`
- `business_logic_analyzer.py`
- 2 new response templates (`risk_warning`, `proactive_recommendation`)
- 3 configuration files
- 7 test suites

---

**Last Updated:** 2024-12-14  
**Next Review:** After Phase 08 completion  
**Status:** Design Complete, Implementation Pending
