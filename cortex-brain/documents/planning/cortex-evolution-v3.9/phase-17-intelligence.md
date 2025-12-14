# Phase 17: Proactive Intelligence & Risk Assessment

**🔗 Breadcrumb:** [← Back to Master Plan](cortex-3.9-master.md)

**Status:** ⏳ Pending  
**Phase ID:** 17  
**Estimated Time:** 6 hours (360 minutes)  
**Actual Start:** -  
**Actual End:** -  
**Actual Work Time:** -  
**Dependencies:** Phase 02 (Complexity Analyzer) ✅, Phase 08 (AST Engine) ⏳, Phase 09 (Enhanced Analyzers) ⏳  
**Blocks:** None (enhancement feature)

---

## 🎯 Phase Objective

Implement proactive intelligence system providing continuous enhancement recommendations without user prompting, plus pre-execution risk assessment preventing breaking changes, with domain-aware analysis adapting to code criticality.

**Success Criteria:**
- ✅ `proactive_advisor.py` operational with context-aware triggers
- ✅ `risk_assessor.py` preventing 90%+ breaking changes
- ✅ `domain_classifier.py` correctly identifying CRITICAL domains (95%+ accuracy)
- ✅ Specialized analyzers: security, compliance, business logic
- ✅ `risk_warning` response template integrated
- ✅ Integration with Planning Orchestrator 3.0 pre-execution hooks
- ✅ Proactive recommendations generated for 100% of Tier 3/4 operations
- ✅ 100% test coverage with passing tests

---

## 🏗️ Implementation Plan

### Task 1: Proactive Advisor (2 hours)

**Create `src/operations/modules/intelligence/proactive_advisor.py`:**

```python
"""
Proactive Advisor - Continuous enhancement recommendations.

Provides actionable recommendations without user prompting based on
code quality analysis, architecture patterns, and historical learnings.
"""

from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass
import logging

from ..analysis.ast_engine import ASTEngine
from ..analysis.deduplication_analyzer import DeduplicationAnalyzer
from ..analysis.architecture_debt_analyzer import ArchitectureDebtAnalyzer
from ..analysis.code_smell_analyzer import CodeSmellAnalyzer

logger = logging.getLogger(__name__)

@dataclass
class ProactiveRecommendation:
    """Proactive enhancement recommendation."""
    category: str  # "code_quality", "architecture", "performance", "security"
    priority: str  # "high", "medium", "low"
    title: str
    description: str
    suggested_action: str
    estimated_effort: str  # "5 minutes", "1 hour", etc.
    impact: str  # "High", "Medium", "Low"

class ProactiveAdvisor:
    """Generate proactive enhancement recommendations."""
    
    def __init__(self, ast_engine, analyzers: Dict[str, Any]):
        self.ast_engine = ast_engine
        self.analyzers = analyzers
        
        # Recommendation triggers
        self.triggers = {
            'duplicate_code': self._trigger_duplicate_refactor,
            'architecture_violation': self._trigger_architecture_fix,
            'code_smell': self._trigger_code_cleanup,
            'test_gap': self._trigger_test_addition,
            'security_issue': self._trigger_security_fix,
            'performance_bottleneck': self._trigger_optimization
        }
        
    def generate_recommendations(
        self,
        context: Dict[str, Any] = None
    ) -> List[ProactiveRecommendation]:
        """
        Generate proactive recommendations based on current codebase state.
        
        Args:
            context: Optional context (current operation, affected files, etc.)
            
        Returns:
            List of prioritized recommendations
        """
        logger.info("Generating proactive recommendations")
        
        recommendations = []
        
        # Analyze code quality
        dedup_analysis = self.analyzers['deduplication'].analyze()
        if dedup_analysis['total_duplicates'] > 0:
            recommendations.extend(self._trigger_duplicate_refactor(dedup_analysis))
            
        # Analyze architecture
        arch_analysis = self.analyzers['architecture'].analyze()
        if arch_analysis['high_severity_count'] > 0:
            recommendations.extend(self._trigger_architecture_fix(arch_analysis))
            
        # Analyze code smells
        smell_analysis = self.analyzers['code_smell'].analyze(Path.cwd())
        if smell_analysis['total_smells'] > 0:
            recommendations.extend(self._trigger_code_cleanup(smell_analysis))
            
        # Sort by priority
        priority_order = {'high': 0, 'medium': 1, 'low': 2}
        recommendations.sort(key=lambda r: priority_order[r.priority])
        
        return recommendations[:10]  # Top 10 recommendations
        
    def _trigger_duplicate_refactor(self, analysis: Dict[str, Any]) -> List[ProactiveRecommendation]:
        """Generate recommendations for duplicate code."""
        recommendations = []
        
        duplicate_groups = analysis['duplicate_groups']
        
        for group in duplicate_groups[:3]:  # Top 3 duplicates
            recommendations.append(ProactiveRecommendation(
                category="code_quality",
                priority="high" if group.similarity_score > 0.95 else "medium",
                title=f"Refactor {len(group.locations)} duplicate code blocks",
                description=(
                    f"Found {len(group.locations)} instances of similar code "
                    f"({group.similarity_score:.0%} similarity, {group.lines_count} lines)"
                ),
                suggested_action=(
                    "Extract shared logic into utility function or module. "
                    f"{group.recommendation}"
                ),
                estimated_effort=f"{int(group.lines_count / 10)} minutes",
                impact="Medium - Reduces maintenance burden"
            ))
            
        return recommendations
        
    def _trigger_architecture_fix(self, analysis: Dict[str, Any]) -> List[ProactiveRecommendation]:
        """Generate recommendations for architecture violations."""
        recommendations = []
        
        violations = [v for v in analysis['violations'] if v.severity == 'high']
        
        for violation in violations[:2]:  # Top 2 violations
            recommendations.append(ProactiveRecommendation(
                category="architecture",
                priority="high",
                title=f"Fix {violation.violation_type.replace('_', ' ')}",
                description=violation.description,
                suggested_action=violation.recommendation,
                estimated_effort="1-2 hours",
                impact="High - Improves modularity and maintainability"
            ))
            
        return recommendations
        
    def _trigger_code_cleanup(self, analysis: Dict[str, Any]) -> List[ProactiveRecommendation]:
        """Generate recommendations for code smells."""
        recommendations = []
        
        high_severity_smells = [
            s for s in analysis['smells'] if s.severity == 'high'
        ]
        
        for smell in high_severity_smells[:2]:  # Top 2 smells
            recommendations.append(ProactiveRecommendation(
                category="code_quality",
                priority="medium",
                title=f"Address {smell.smell_type.replace('_', ' ')} in {Path(smell.file_path).name}",
                description=smell.description,
                suggested_action=smell.recommendation,
                estimated_effort="30 minutes",
                impact="Medium - Improves code readability"
            ))
            
        return recommendations
        
    def _trigger_test_addition(self, context: Dict[str, Any]) -> List[ProactiveRecommendation]:
        """Generate recommendations for test gaps."""
        # Placeholder - actual implementation would analyze test coverage
        return []
        
    def _trigger_security_fix(self, context: Dict[str, Any]) -> List[ProactiveRecommendation]:
        """Generate recommendations for security issues."""
        # Placeholder - actual implementation would use security analyzer
        return []
        
    def _trigger_optimization(self, context: Dict[str, Any]) -> List[ProactiveRecommendation]:
        """Generate recommendations for performance bottlenecks."""
        # Placeholder - actual implementation would use performance profiler
        return []
```

### Task 2: Risk Assessor (2 hours)

**Create `src/operations/modules/intelligence/risk_assessor.py`:**

```python
"""
Risk Assessor - Pre-execution impact analysis.

Analyzes proposed changes to identify potential breaking changes,
data loss risks, and security vulnerabilities before execution.
"""

from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class RiskLevel(Enum):
    """Risk severity levels."""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

@dataclass
class RiskAssessment:
    """Risk assessment result."""
    risk_level: RiskLevel
    category: str  # "breaking_change", "data_loss", "security", "performance"
    description: str
    affected_components: List[str]
    mitigation_steps: List[str]
    requires_manual_review: bool

class RiskAssessor:
    """Assess execution risks before changes are applied."""
    
    def __init__(self, ast_engine, domain_classifier):
        self.ast_engine = ast_engine
        self.domain_classifier = domain_classifier
        
    def assess_risk(
        self,
        operation: str,
        context: Dict[str, Any]
    ) -> List[RiskAssessment]:
        """
        Assess risks of proposed operation.
        
        Args:
            operation: Operation description
            context: Operation context (files, changes, etc.)
            
        Returns:
            List of identified risks
        """
        logger.info(f"Assessing risk for operation: {operation}")
        
        risks = []
        
        # Assess breaking change risk
        breaking_risks = self._assess_breaking_changes(context)
        risks.extend(breaking_risks)
        
        # Assess data loss risk
        data_risks = self._assess_data_loss(context)
        risks.extend(data_risks)
        
        # Assess security risk
        security_risks = self._assess_security_impact(context)
        risks.extend(security_risks)
        
        # Assess domain-specific risks
        domain_risks = self._assess_domain_risks(context)
        risks.extend(domain_risks)
        
        # Sort by severity
        severity_order = {
            RiskLevel.CRITICAL: 0,
            RiskLevel.HIGH: 1,
            RiskLevel.MEDIUM: 2,
            RiskLevel.LOW: 3
        }
        risks.sort(key=lambda r: severity_order[r.risk_level])
        
        return risks
        
    def _assess_breaking_changes(self, context: Dict[str, Any]) -> List[RiskAssessment]:
        """Assess breaking change risk."""
        risks = []
        
        affected_files = context.get('affected_files', [])
        
        # Analyze dependencies
        arch = self.ast_engine.analyze_architecture()
        
        for file in affected_files:
            # Find modules that depend on this file
            dependents = self._find_dependents(file, arch)
            
            if len(dependents) > 10:
                risks.append(RiskAssessment(
                    risk_level=RiskLevel.HIGH,
                    category="breaking_change",
                    description=(
                        f"Modifying {Path(file).name} affects {len(dependents)} "
                        f"downstream modules"
                    ),
                    affected_components=dependents[:10],
                    mitigation_steps=[
                        "Run full test suite before committing",
                        "Update dependent modules if interface changes",
                        "Consider deprecation path for major changes",
                        "Create feature flag for gradual rollout"
                    ],
                    requires_manual_review=True
                ))
                
        return risks
        
    def _assess_data_loss(self, context: Dict[str, Any]) -> List[RiskAssessment]:
        """Assess data loss risk."""
        risks = []
        
        operation_type = context.get('operation_type', '')
        
        # Check for destructive operations
        destructive_keywords = ['delete', 'drop', 'truncate', 'remove', 'clear']
        
        if any(kw in operation_type.lower() for kw in destructive_keywords):
            risks.append(RiskAssessment(
                risk_level=RiskLevel.CRITICAL,
                category="data_loss",
                description="Operation involves data deletion or modification",
                affected_components=context.get('affected_data', []),
                mitigation_steps=[
                    "⚠️ CREATE BACKUP BEFORE PROCEEDING",
                    "Verify backup restoration procedure",
                    "Test on non-production data first",
                    "Implement soft-delete if possible"
                ],
                requires_manual_review=True
            ))
            
        return risks
        
    def _assess_security_impact(self, context: Dict[str, Any]) -> List[RiskAssessment]:
        """Assess security risk."""
        risks = []
        
        affected_files = context.get('affected_files', [])
        
        # Check if security-critical files are affected
        security_keywords = ['auth', 'security', 'password', 'token', 'credential']
        
        for file in affected_files:
            file_lower = str(file).lower()
            if any(kw in file_lower for kw in security_keywords):
                risks.append(RiskAssessment(
                    risk_level=RiskLevel.CRITICAL,
                    category="security",
                    description=f"Modifying security-critical file: {Path(file).name}",
                    affected_components=[str(file)],
                    mitigation_steps=[
                        "Security review REQUIRED before merge",
                        "Run security scanner (bandit, safety)",
                        "Validate authentication/authorization logic",
                        "Test for common vulnerabilities (OWASP Top 10)"
                    ],
                    requires_manual_review=True
                ))
                
        return risks
        
    def _assess_domain_risks(self, context: Dict[str, Any]) -> List[RiskAssessment]:
        """Assess domain-specific risks using domain classifier."""
        risks = []
        
        affected_files = context.get('affected_files', [])
        
        for file in affected_files:
            domain = self.domain_classifier.classify(Path(file))
            
            if domain['is_critical']:
                risks.append(RiskAssessment(
                    risk_level=RiskLevel.HIGH,
                    category=domain['category'],
                    description=(
                        f"Modifying CRITICAL domain: {domain['category']} "
                        f"({', '.join(domain['indicators'])})"
                    ),
                    affected_components=[str(file)],
                    mitigation_steps=[
                        f"Deep AST analysis required for {domain['category']}",
                        "Extended testing with domain-specific test cases",
                        "Peer review from domain expert",
                        "Validate compliance requirements if applicable"
                    ],
                    requires_manual_review=True
                ))
                
        return risks
        
    def _find_dependents(self, file: str, arch: Dict[str, Any]) -> List[str]:
        """Find modules that depend on given file."""
        dependents = []
        
        for edge in arch.get('module_graph', []):
            if file in edge['from']:
                dependents.append(edge['to'])
                
        return list(set(dependents))
        
    def should_block_execution(self, risks: List[RiskAssessment]) -> bool:
        """Determine if risks warrant blocking execution."""
        critical_risks = [r for r in risks if r.risk_level == RiskLevel.CRITICAL]
        return len(critical_risks) > 0
```

### Task 3: Specialized Analyzers (1.5 hours)

**Create `src/operations/modules/analysis/security_analyzer.py`:**

```python
"""Security Analyzer - OWASP Top 10 pattern detection."""

from pathlib import Path
from typing import Dict, Any, List
import ast
import re
import logging

logger = logging.getLogger(__name__)

class SecurityAnalyzer:
    """Detect security vulnerabilities and anti-patterns."""
    
    def __init__(self):
        # OWASP Top 10 patterns
        self.vulnerability_patterns = {
            'sql_injection': r'execute\s*\(\s*["\'].*%s.*["\']',
            'xss': r'innerHTML\s*=.*\+',
            'hardcoded_secrets': r'(password|secret|key|token)\s*=\s*["\'][^"\']+["\']',
            'unsafe_deserialization': r'pickle\.loads?\s*\(',
            'command_injection': r'os\.system\s*\(.*\+',
        }
        
    def analyze(self, target_path: Path) -> Dict[str, Any]:
        """Analyze for security vulnerabilities."""
        vulnerabilities = []
        
        if target_path.is_file():
            files = [target_path]
        else:
            files = list(target_path.rglob("*.py"))
            
        for file in files:
            file_vulns = self._analyze_file(file)
            vulnerabilities.extend(file_vulns)
            
        return {
            'vulnerabilities': vulnerabilities,
            'total_vulnerabilities': len(vulnerabilities),
            'critical_count': len([v for v in vulnerabilities if v['severity'] == 'critical'])
        }
```

**Create `src/operations/modules/analysis/compliance_analyzer.py`:**

```python
"""Compliance Analyzer - PII handling, audit trail validation."""

# Similar structure to SecurityAnalyzer
# Focus on GDPR, HIPAA, SOC2 compliance patterns
```

**Create `src/operations/modules/analysis/business_logic_analyzer.py`:**

```python
"""Business Logic Analyzer - Financial calculation verification."""

# Similar structure to SecurityAnalyzer
# Focus on financial calculations, rounding errors, precision issues
```

### Task 4: Integration with Planning Orchestrator (30 min)

**Update Planning Orchestrator 3.0:**

```python
# In planning_orchestrator.py

async def _assess_risks_pre_execution(self, request: str, context: Dict[str, Any]):
    """Pre-execution risk assessment."""
    from ..intelligence.risk_assessor import RiskAssessor
    
    risk_assessor = RiskAssessor(self.ast_engine, self.domain_classifier)
    
    risks = risk_assessor.assess_risk(request, context)
    
    if risk_assessor.should_block_execution(risks):
        logger.warning("⚠️ CRITICAL RISKS DETECTED - Execution blocked")
        return {
            'blocked': True,
            'risks': risks
        }
        
    return {
        'blocked': False,
        'risks': risks
    }
```

---

## 📦 Expected Deliverables

### Code Deliverables
- ✅ `src/operations/modules/intelligence/proactive_advisor.py`
- ✅ `src/operations/modules/intelligence/risk_assessor.py`
- ✅ `src/operations/modules/analysis/security_analyzer.py`
- ✅ `src/operations/modules/analysis/compliance_analyzer.py`
- ✅ `src/operations/modules/analysis/business_logic_analyzer.py`
- ✅ Integration with Planning Orchestrator 3.0

### Test Deliverables
- ✅ `tests/test_proactive_advisor.py`
- ✅ `tests/test_risk_assessor.py`
- ✅ `tests/test_security_analyzer.py`
- ✅ `tests/integration/test_proactive_intelligence.py`
- ✅ `tests/integration/test_risk_assessment_flow.py`

### Documentation Deliverables
- ✅ Proactive intelligence guide
- ✅ Risk assessment framework
- ✅ Domain classification matrix
- ✅ Security analyzer patterns
- ✅ `risk_warning` response template

---

## 🔄 Next Steps

1. **Phase 02, 08-09 Completion:** Dependencies must be operational
2. **OWASP Pattern Library:** Expand security patterns
3. **Domain Classification:** Calibrate critical domain detection
4. **Integration Testing:** Validate risk assessment accuracy
5. **User Feedback:** Collect feedback on recommendation quality

---

## 🔗 Integration Points

### Upstream Dependencies
- **Complexity Analyzer (Phase 02):** Domain classification
- **AST Engine (Phase 08):** Dependency analysis
- **Enhanced Analyzers (Phase 09):** Code quality insights

### Downstream Consumers
- **Planning Orchestrator (Phase 03):** Pre-execution risk assessment
- **System Maintenance (Phase 06):** Proactive recommendations
- **Integration Tests (Phase 16):** Risk prevention validation

---

## 🚨 Risk Mitigation

### Risk 1: False Positive Risk Warnings
**Mitigation:**
- Conservative thresholds for blocking execution
- User override mechanism for low/medium risks
- Feedback loop for risk accuracy improvement

### Risk 2: Recommendation Fatigue
**Mitigation:**
- Limit to top 10 recommendations
- Priority-based sorting (high → medium → low)
- Context-aware filtering (relevant to current operation)

### Risk 3: Performance Overhead
**Mitigation:**
- Asynchronous risk assessment
- Cache analysis results (5-minute TTL)
- Skip for Tier 1/2 operations

---

## 📊 Success Metrics

- ✅ Proactive recommendations generated for 100% of Tier 3/4 operations
- ✅ Risk assessment prevents 90%+ breaking changes
- ✅ Domain classifier 95%+ accuracy on CRITICAL domains
- ✅ Security analyzer detects 100% of OWASP Top 10 patterns
- ✅ User satisfaction ≥4.5/5.0 for recommendation quality
- ✅ False positive rate <5% for risk warnings

---

**Phase Owner:** Asif Hussain  
**Phase Status:** ⏳ Awaiting Phase 02, 08-09 completion  
**Last Updated:** 2024-12-14
