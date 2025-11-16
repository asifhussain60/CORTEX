# Request Validator & Enhancer - Code Examples

**Purpose:** Practical code examples for implementing the Request Validator & Enhancer  
**Status:** Implementation Reference  
**Date:** 2025-11-07

---

## 🔧 Core Implementation

### 1. Main Validator Class

```python
"""
src/entry_point/request_validator.py
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum
import time
import uuid
from datetime import datetime

from ..tier1.tier1_api import Tier1API
from ..tier2.knowledge_graph import KnowledgeGraph
from ..tier3.context_intelligence import ContextIntelligence
from ..cortex_agents.base_agent import AgentRequest


class ValidationDecision(Enum):
    APPROVE = "approve"
    CHALLENGE = "challenge"
    ENHANCE = "enhance"
    ADVISE = "advise"


@dataclass
class ValidationResult:
    """Result of validation analysis."""
    decision: ValidationDecision
    confidence: float
    
    viability_score: float
    viability_issues: List[Dict[str, Any]]
    
    similar_patterns: List[Dict[str, Any]]
    success_rate: Optional[float]
    
    enhancements: List[Dict[str, Any]]
    estimated_value: float
    
    message: str
    alternatives: List[str]
    requires_user_input: bool
    
    analysis_time_ms: float
    validation_id: str
    timestamp: str


class RequestValidator:
    """Main validator orchestrator."""
    
    def __init__(
        self,
        tier1_api: Tier1API,
        tier2_kg: KnowledgeGraph,
        tier3_context: ContextIntelligence
    ):
        self.tier1 = tier1_api
        self.tier2 = tier2_kg
        self.tier3 = tier3_context
        
        # Initialize sub-analyzers
        self.viability = ViabilityAnalyzer(tier2_kg, tier3_context)
        self.historical = HistoricalAnalyzer(tier1_api, tier2_kg)
        self.enhancement = EnhancementAnalyzer(tier2_kg)
    
    def validate_and_enhance(
        self,
        request: AgentRequest,
        conversation_id: str,
        skip_checks: Optional[List[str]] = None
    ) -> ValidationResult:
        """Validate request and suggest enhancements."""
        start_time = time.perf_counter()
        skip_checks = skip_checks or []
        
        validation_id = str(uuid.uuid4())
        
        # Run viability analysis first (fail fast on critical issues)
        viability_result = None
        if "viability" not in skip_checks:
            viability_result = self.viability.analyze(request)
            
            # Fail fast on critical issues
            if viability_result.get('has_critical_issues'):
                return self._create_blocking_challenge(
                    validation_id,
                    viability_result,
                    time.perf_counter() - start_time
                )
        
        # Run historical and enhancement analyses
        historical_result = None
        enhancement_result = None
        
        if "historical" not in skip_checks:
            historical_result = self.historical.analyze(
                request,
                conversation_id
            )
        
        if "enhancement" not in skip_checks:
            enhancement_result = self.enhancement.analyze(request)
        
        # Synthesize results
        validation_result = self._synthesize(
            validation_id,
            request,
            viability_result,
            historical_result,
            enhancement_result,
            time.perf_counter() - start_time
        )
        
        # Track for learning
        self._track_validation(validation_result, request, conversation_id)
        
        return validation_result
    
    def _synthesize(
        self,
        validation_id: str,
        request: AgentRequest,
        viability,
        historical,
        enhancement,
        analysis_time: float
    ) -> ValidationResult:
        """Synthesize analysis results into recommendation."""
        
        # Priority 1: Critical viability issues (BLOCK)
        if viability and viability.get('has_critical_issues'):
            return ValidationResult(
                decision=ValidationDecision.CHALLENGE,
                confidence=viability['confidence'],
                viability_score=viability['confidence'],
                viability_issues=viability['issues'],
                similar_patterns=[],
                success_rate=None,
                enhancements=[],
                estimated_value=0.0,
                message=self._format_critical_message(viability),
                alternatives=viability['alternatives'],
                requires_user_input=True,
                analysis_time_ms=analysis_time * 1000,
                validation_id=validation_id,
                timestamp=datetime.now().isoformat()
            )
        
        # Priority 2: High viability issues with good alternatives (ADVISE)
        if viability and viability.get('issues'):
            high_issues = [i for i in viability['issues'] if i['severity'] == 'HIGH']
            if high_issues and historical and historical.get('recommended_workflow'):
                return ValidationResult(
                    decision=ValidationDecision.ADVISE,
                    confidence=0.85,
                    viability_score=viability['confidence'],
                    viability_issues=high_issues,
                    similar_patterns=historical.get('similar_patterns', []),
                    success_rate=historical.get('success_rate'),
                    enhancements=[],
                    estimated_value=0.0,
                    message=self._format_advisory_message(viability, historical),
                    alternatives=[historical['recommended_workflow']],
                    requires_user_input=True,
                    analysis_time_ms=analysis_time * 1000,
                    validation_id=validation_id,
                    timestamp=datetime.now().isoformat()
                )
        
        # Priority 3: Historical success pattern or enhancements available (ENHANCE)
        enhancements = []
        if historical and historical.get('reusable_components'):
            enhancements.append({
                'type': 'historical_pattern',
                'title': f"Reuse proven pattern: {historical['recommended_workflow']}",
                'value': 0.8,
                'time_saved_min': 10
            })
        
        if enhancement and enhancement.get('enhancements'):
            enhancements.extend(enhancement['enhancements'])
        
        if enhancements:
            return ValidationResult(
                decision=ValidationDecision.ENHANCE,
                confidence=0.9,
                viability_score=1.0,
                viability_issues=[],
                similar_patterns=historical.get('similar_patterns', []) if historical else [],
                success_rate=historical.get('success_rate') if historical else None,
                enhancements=enhancements,
                estimated_value=sum(e.get('value', 0) for e in enhancements),
                message=self._format_enhancement_message(historical, enhancement),
                alternatives=[],
                requires_user_input=True,
                analysis_time_ms=analysis_time * 1000,
                validation_id=validation_id,
                timestamp=datetime.now().isoformat()
            )
        
        # Priority 4: No issues, approve (APPROVE)
        return ValidationResult(
            decision=ValidationDecision.APPROVE,
            confidence=0.95,
            viability_score=1.0,
            viability_issues=[],
            similar_patterns=[],
            success_rate=None,
            enhancements=[],
            estimated_value=0.0,
            message="Request looks good! Ready to proceed.",
            alternatives=[],
            requires_user_input=False,
            analysis_time_ms=analysis_time * 1000,
            validation_id=validation_id,
            timestamp=datetime.now().isoformat()
        )
    
    def _create_blocking_challenge(
        self,
        validation_id: str,
        viability_result,
        analysis_time: float
    ) -> ValidationResult:
        """Create blocking challenge for critical issues."""
        return ValidationResult(
            decision=ValidationDecision.CHALLENGE,
            confidence=viability_result['confidence'],
            viability_score=viability_result['confidence'],
            viability_issues=viability_result['issues'],
            similar_patterns=[],
            success_rate=None,
            enhancements=[],
            estimated_value=0.0,
            message=self._format_critical_message(viability_result),
            alternatives=viability_result['alternatives'],
            requires_user_input=True,
            analysis_time_ms=analysis_time * 1000,
            validation_id=validation_id,
            timestamp=datetime.now().isoformat()
        )
    
    def _format_critical_message(self, viability) -> str:
        """Format message for critical issues."""
        issues_text = "\n".join([
            f"  - {issue['description']}" 
            for issue in viability['issues']
        ])
        return f"CRITICAL ISSUES DETECTED:\n{issues_text}"
    
    def _format_advisory_message(self, viability, historical) -> str:
        """Format message for advisory."""
        return f"Request viable but risks detected. Recommended workflow: {historical.get('recommended_workflow', 'N/A')}"
    
    def _format_enhancement_message(self, historical, enhancement) -> str:
        """Format message for enhancements."""
        return "Your request is viable. Enhancements available to improve quality."
    
    def _track_validation(
        self,
        result: ValidationResult,
        request: AgentRequest,
        conversation_id: str
    ):
        """Track validation decision for learning."""
        # Log to Tier 1 for later analysis
        # This will be used by learning loop to improve validation
        pass
```

### 2. Viability Analyzer

```python
"""
Viability Analyzer - Checks if request is feasible and safe
"""

class ViabilityAnalyzer:
    """Analyzes request viability."""
    
    def __init__(self, tier2: KnowledgeGraph, tier3: ContextIntelligence):
        self.tier2 = tier2
        self.tier3 = tier3
    
    def analyze(self, request: AgentRequest) -> Dict[str, Any]:
        """
        Analyze request viability.
        
        Returns:
            {
                'viable': bool,
                'confidence': float,
                'has_critical_issues': bool,
                'issues': List[Dict],
                'risks': List[str],
                'alternatives': List[str]
            }
        """
        issues = []
        risks = []
        alternatives = []
        
        # Check 1: Scope analysis
        scope_issue = self._check_scope(request)
        if scope_issue:
            issues.append(scope_issue)
            if scope_issue['severity'] == 'CRITICAL':
                alternatives.extend(scope_issue.get('alternatives', []))
        
        # Check 2: Tier 0 rule violations
        rule_violations = self._check_tier0_rules(request)
        if rule_violations:
            issues.extend(rule_violations)
            for violation in rule_violations:
                if violation['severity'] == 'CRITICAL':
                    alternatives.extend(violation.get('alternatives', []))
        
        # Check 3: Technical viability (query Tier 3)
        if request.context.get('files'):
            tech_issues = self._check_technical_viability(
                request.context['files']
            )
            issues.extend(tech_issues)
            risks.extend([i['risk'] for i in tech_issues])
        
        # Check 4: Definition of Ready
        dor_issue = self._check_definition_of_ready(request)
        if dor_issue:
            issues.append(dor_issue)
        
        has_critical = any(i['severity'] == 'CRITICAL' for i in issues)
        
        return {
            'viable': not has_critical,
            'confidence': self._calculate_confidence(issues),
            'has_critical_issues': has_critical,
            'issues': issues,
            'risks': risks,
            'alternatives': alternatives
        }
    
    def _check_scope(self, request: AgentRequest) -> Optional[Dict]:
        """Check if scope is reasonable."""
        message = request.user_message.lower()
        
        # Detect multi-feature requests
        feature_indicators = ['and', 'also', 'plus', 'as well as']
        feature_keywords = ['feature', 'add', 'implement', 'create', 'build']
        
        # Count potential features
        feature_count = sum(1 for keyword in feature_keywords if keyword in message)
        has_connectors = any(ind in message for ind in feature_indicators)
        
        if feature_count >= 3 and has_connectors:
            return {
                'severity': 'CRITICAL',
                'category': 'scope',
                'description': f"Request appears to contain {feature_count} features (multi-feature request)",
                'evidence': request.user_message[:100],
                'alternatives': [
                    "Break into separate requests (one feature per request)",
                    "Prioritize: Implement highest-value feature first"
                ]
            }
        
        # Detect vague requirements
        vague_words = ['maybe', 'probably', 'might', 'could', 'possibly']
        if any(word in message for word in vague_words):
            return {
                'severity': 'HIGH',
                'category': 'clarity',
                'description': "Requirements contain uncertainty",
                'evidence': [word for word in vague_words if word in message],
                'alternatives': [
                    "Clarify requirements (remove 'maybe', 'probably')",
                    "Define clear acceptance criteria"
                ]
            }
        
        return None
    
    def _check_tier0_rules(self, request: AgentRequest) -> List[Dict]:
        """Check for Tier 0 rule violations."""
        violations = []
        message = request.user_message.lower()
        
        # Check for TDD skip attempt
        skip_patterns = [
            'skip test',
            'no test',
            'without test',
            'skip tdd',
            'just implement',
            'implement quickly',
            'fast implementation'
        ]
        
        if any(pattern in message for pattern in skip_patterns):
            violations.append({
                'severity': 'CRITICAL',
                'category': 'tier0_violation',
                'rule': 'TDD_ENFORCEMENT',
                'description': "Request proposes skipping TDD workflow (Rule #4)",
                'evidence': message[:100],
                'alternatives': [
                    "Minimal test-first approach (3-5 core tests, ~15 min)",
                    "Spike branch for exploration, then re-implement with tests"
                ],
                'historical_data': {
                    'test_first_success_rate': 0.94,
                    'test_skip_success_rate': 0.67,
                    'time_penalty': 2.3  # 2.3x slower
                }
            })
        
        # Check for DoD bypass
        dod_bypass = ['skip validation', 'skip checks', 'ignore warnings', 'ignore errors']
        if any(pattern in message for pattern in dod_bypass):
            violations.append({
                'severity': 'CRITICAL',
                'category': 'tier0_violation',
                'rule': 'DEFINITION_OF_DONE',
                'description': "Request proposes bypassing Definition of Done (Rule #6)",
                'evidence': message[:100],
                'alternatives': [
                    "Fix errors/warnings before completion",
                    "Run health checks to identify issues"
                ]
            })
        
        return violations
    
    def _check_technical_viability(self, files: List[str]) -> List[Dict]:
        """Check technical constraints via Tier 3."""
        issues = []
        
        # Query Tier 3 for file stability
        for file_path in files:
            try:
                file_health = self.tier3.get_file_health(file_path)
                
                # Check churn rate
                if file_health.get('churn_rate', 0) > 0.25:
                    issues.append({
                        'severity': 'HIGH',
                        'category': 'file_stability',
                        'description': f"File {file_path} is a hotspot (high churn)",
                        'risk': f"Unstable file - {file_health['churn_rate']:.0%} churn rate",
                        'evidence': {
                            'churn_rate': file_health['churn_rate'],
                            'recent_changes': file_health.get('recent_changes', 0)
                        },
                        'recommendation': "Make small, focused changes. Extra validation recommended."
                    })
            except Exception as e:
                # File not found or other error - note but don't block
                pass
        
        return issues
    
    def _check_definition_of_ready(self, request: AgentRequest) -> Optional[Dict]:
        """Verify request meets Definition of Ready criteria."""
        message = request.user_message
        
        # Check for clear requirements
        if len(message) < 20:
            return {
                'severity': 'MEDIUM',
                'category': 'definition_of_ready',
                'description': "Request is very brief - may lack clear requirements",
                'evidence': f"Message length: {len(message)} characters",
                'alternatives': [
                    "Provide more context (what, why, acceptance criteria)",
                    "Define testable outcomes"
                ]
            }
        
        # Check for testable outcomes
        testable_indicators = ['test', 'verify', 'should', 'must', 'when', 'then']
        has_testable = any(indicator in message.lower() for indicator in testable_indicators)
        
        if not has_testable:
            return {
                'severity': 'MEDIUM',
                'category': 'definition_of_ready',
                'description': "Request lacks testable outcomes",
                'evidence': "No 'should', 'must', 'when', 'then' indicators found",
                'alternatives': [
                    "Add acceptance criteria (Given/When/Then format)",
                    "Define expected behavior"
                ]
            }
        
        return None
    
    def _calculate_confidence(self, issues: List[Dict]) -> float:
        """Calculate confidence score based on issues."""
        if not issues:
            return 1.0
        
        # Weight by severity
        severity_weights = {
            'CRITICAL': 0.4,  # Each critical issue reduces confidence by 40%
            'HIGH': 0.2,
            'MEDIUM': 0.1,
            'LOW': 0.05
        }
        
        total_deduction = sum(
            severity_weights.get(issue['severity'], 0.1)
            for issue in issues
        )
        
        return max(0.0, 1.0 - total_deduction)
```

### 3. Historical Analyzer

```python
"""
Historical Analyzer - Learns from past patterns
"""

class HistoricalAnalyzer:
    """Analyzes historical context."""
    
    def __init__(self, tier1: Tier1API, tier2: KnowledgeGraph):
        self.tier1 = tier1
        self.tier2 = tier2
    
    def analyze(
        self,
        request: AgentRequest,
        conversation_id: str
    ) -> Dict[str, Any]:
        """
        Analyze historical context.
        
        Returns:
            {
                'similar_patterns': List[Dict],
                'success_rate': float,
                'recommended_workflow': str,
                'reusable_components': List[str],
                'anti_patterns': List[Dict]
            }
        """
        # Search Tier 2 for similar patterns
        similar = self.tier2.search_patterns(
            query=request.user_message,
            pattern_type="workflow",
            limit=5
        )
        
        # Calculate success rate from historical data
        success_rate = self._calculate_success_rate(similar)
        
        # Find recommended workflow
        recommended = self._select_best_workflow(similar, success_rate)
        
        # Identify reusable components
        reusable = self._find_reusable_components(request, similar)
        
        # Check for anti-patterns
        anti_patterns = self.tier2.search_patterns(
            query=request.user_message,
            pattern_type="anti_pattern",
            limit=3
        )
        
        return {
            'similar_patterns': similar,
            'success_rate': success_rate,
            'recommended_workflow': recommended,
            'reusable_components': reusable,
            'anti_patterns': anti_patterns
        }
    
    def _calculate_success_rate(self, patterns: List) -> Optional[float]:
        """Calculate success rate from patterns."""
        if not patterns:
            return None
        
        # Extract success metrics from pattern metadata
        success_counts = []
        for pattern in patterns:
            metadata = pattern.get('metadata', {})
            if 'success_count' in metadata and 'total_count' in metadata:
                success_counts.append(
                    metadata['success_count'] / metadata['total_count']
                )
        
        if success_counts:
            return sum(success_counts) / len(success_counts)
        
        return None
    
    def _select_best_workflow(self, patterns: List, success_rate: Optional[float]) -> Optional[str]:
        """Select best workflow from patterns."""
        if not patterns:
            return None
        
        # Sort by confidence and success rate
        best = max(
            patterns,
            key=lambda p: (
                p.get('confidence', 0) *
                (p.get('metadata', {}).get('success_rate', 0.5))
            )
        )
        
        return best.get('title')
    
    def _find_reusable_components(self, request: AgentRequest, patterns: List) -> List[str]:
        """Find reusable components from patterns."""
        components = []
        
        for pattern in patterns:
            metadata = pattern.get('metadata', {})
            if 'components' in metadata:
                components.extend(metadata['components'])
        
        return list(set(components))  # Deduplicate
```

### 4. Enhancement Analyzer

```python
"""
Enhancement Analyzer - Suggests improvements
"""

class EnhancementAnalyzer:
    """Suggests improvements to requests."""
    
    def __init__(self, tier2: KnowledgeGraph):
        self.tier2 = tier2
    
    def analyze(self, request: AgentRequest) -> Dict[str, Any]:
        """
        Suggest enhancements.
        
        Returns:
            {
                'enhancements': List[Dict],
                'estimated_value': float,
                'priority_order': List[str]
            }
        """
        enhancements = []
        
        # Query Tier 2 for best practice patterns
        best_practices = self.tier2.search_patterns(
            query=request.intent,
            pattern_type="principle",
            limit=5
        )
        
        # Generate enhancement suggestions
        enhancements.extend(self._suggest_completeness(request))
        enhancements.extend(self._suggest_best_practices(request, best_practices))
        enhancements.extend(self._suggest_quality(request))
        
        # Calculate value
        estimated_value = sum(e.get('value', 0) for e in enhancements)
        
        # Priority ordering (highest value first)
        priority_order = sorted(
            enhancements,
            key=lambda e: e.get('value', 0),
            reverse=True
        )
        
        return {
            'enhancements': priority_order,
            'estimated_value': estimated_value,
            'priority_order': [e['id'] for e in priority_order]
        }
    
    def _suggest_completeness(self, request: AgentRequest) -> List[Dict]:
        """Suggest completeness improvements."""
        suggestions = []
        message = request.user_message.lower()
        
        # Check for UI elements without element IDs
        ui_keywords = ['button', 'input', 'form', 'link', 'menu']
        has_ui_element = any(keyword in message for keyword in ui_keywords)
        
        if has_ui_element and 'id' not in message:
            suggestions.append({
                'id': 'element-id',
                'type': 'completeness',
                'title': 'Add element ID for testing',
                'description': 'Enable robust Playwright selectors with unique ID',
                'value': 0.9,  # High value (prevents test fragility)
                'time_estimate_min': 1,
                'priority': 'CRITICAL',
                'rationale': 'ID-based selectors are 96% reliable vs 43% for text selectors'
            })
        
        # Check for confirmation dialogs on destructive actions
        destructive_keywords = ['delete', 'remove', 'destroy', 'clear']
        if any(keyword in message for keyword in destructive_keywords):
            if 'confirm' not in message:
                suggestions.append({
                    'id': 'confirmation-dialog',
                    'type': 'completeness',
                    'title': 'Add confirmation dialog',
                    'description': 'Prevent accidental data loss with user confirmation',
                    'value': 0.8,
                    'time_estimate_min': 5,
                    'priority': 'HIGH',
                    'rationale': 'Industry standard UX pattern for destructive actions'
                })
        
        return suggestions
    
    def _suggest_best_practices(
        self,
        request: AgentRequest,
        best_practices: List
    ) -> List[Dict]:
        """Suggest best practice improvements."""
        suggestions = []
        
        # Check for TDD approach mention
        message = request.user_message.lower()
        if 'test' not in message:
            suggestions.append({
                'id': 'tdd-approach',
                'type': 'best_practice',
                'title': 'Use test-first approach',
                'description': 'Write tests before implementation (TDD)',
                'value': 0.7,
                'time_estimate_min': 10,
                'priority': 'HIGH',
                'rationale': 'Test-first: 94% success rate vs 67% test-after'
            })
        
        return suggestions
    
    def _suggest_quality(self, request: AgentRequest) -> List[Dict]:
        """Suggest quality improvements."""
        suggestions = []
        message = request.user_message.lower()
        
        # Check for accessibility mention
        ui_keywords = ['button', 'input', 'form', 'component']
        has_ui = any(keyword in message for keyword in ui_keywords)
        
        if has_ui and 'accessibility' not in message and 'aria' not in message:
            suggestions.append({
                'id': 'accessibility',
                'type': 'quality',
                'title': 'Add accessibility labels',
                'description': 'ARIA labels for screen reader support',
                'value': 0.6,
                'time_estimate_min': 2,
                'priority': 'MEDIUM',
                'rationale': 'WCAG compliance, legal requirement in many jurisdictions'
            })
        
        return suggestions
```

---

## 🎨 Presentation Layer

### Validation Presenter

```python
"""
src/entry_point/validation_presenter.py
"""

from .request_validator import ValidationResult, ValidationDecision


class ValidationPresenter:
    """Formats validation results for display."""
    
    def present(self, result: ValidationResult) -> str:
        """Format validation result for user."""
        if result.decision == ValidationDecision.APPROVE:
            return self._format_approval(result)
        
        elif result.decision == ValidationDecision.CHALLENGE:
            return self._format_challenge(result)
        
        elif result.decision == ValidationDecision.ENHANCE:
            return self._format_enhancement(result)
        
        elif result.decision == ValidationDecision.ADVISE:
            return self._format_advisory(result)
    
    def _format_challenge(self, result: ValidationResult) -> str:
        """Format blocking challenge."""
        issues_text = "\n".join([
            f"  ❌ {issue['description']}"
            for issue in result.viability_issues
        ])
        
        alternatives_text = "\n".join([
            f"  {i+1}. {alt} {'✅ RECOMMENDED' if i == 0 else ''}"
            for i, alt in enumerate(result.alternatives)
        ])
        
        return f"""
═══════════════════════════════════════════════
⚠️  REQUEST VALIDATION CHALLENGE

Request Analysis: {result.confidence:.0%} confidence
Analysis Time: {result.analysis_time_ms:.0f}ms

{result.message}

ISSUES DETECTED:
{issues_text}

SAFE ALTERNATIVES:
{alternatives_text}

RECOMMENDATION: Alternative 1

═══════════════════════════════════════════════

Options:
  1. Accept recommended alternative ← RECOMMENDED
  2. Modify your request
  3. Override (requires justification)
  4. Abort

Your choice [1-4]: """
    
    def _format_enhancement(self, result: ValidationResult) -> str:
        """Format enhancement suggestions."""
        historical_text = ""
        if result.similar_patterns:
            pattern = result.similar_patterns[0]
            historical_text = f"""
HISTORICAL CONTEXT:
  Similar work found: "{pattern.get('title', 'Unknown')}"
  ✅ Success rate: {result.success_rate:.0%}
  ⏱️  Proven workflow available
"""
        
        enhancements_text = "\n".join([
            self._format_single_enhancement(i+1, enh)
            for i, enh in enumerate(result.enhancements)
        ])
        
        return f"""
═══════════════════════════════════════════════
💡 REQUEST ENHANCEMENT SUGGESTIONS

Your request is viable ✅ ({result.confidence:.0%} confidence)
{historical_text}
SUGGESTED ENHANCEMENTS:

{enhancements_text}

Total Enhanced Value: {result.estimated_value:.1f}x quality improvement

═══════════════════════════════════════════════

Options:
  1. Accept all enhancements ← RECOMMENDED
  2. Select specific enhancements
  3. Proceed without enhancements
  
Your choice [1-3]: """
    
    def _format_single_enhancement(self, num: int, enhancement: Dict) -> str:
        """Format single enhancement."""
        stars = "⭐" * min(3, int(enhancement.get('value', 0) * 3))
        
        return f"""
{num}. {enhancement['title']} {stars}
   Why: {enhancement['description']}
   Value: {enhancement.get('value', 0):.1f}x improvement
   Time: +{enhancement.get('time_estimate_min', 0)} minutes
"""
    
    def _format_approval(self, result: ValidationResult) -> str:
        """Format approval."""
        return f"""
✅ Request validation complete!

Your request looks good and ready to proceed.
Confidence: {result.confidence:.0%}
Analysis time: {result.analysis_time_ms:.0f}ms

Proceeding to execution...
"""
    
    def _format_advisory(self, result: ValidationResult) -> str:
        """Format advisory warning."""
        issues_text = "\n".join([
            f"  ⚠️  {issue['description']}"
            for issue in result.viability_issues
        ])
        
        return f"""
═══════════════════════════════════════════════
⚠️  REQUEST ADVISORY

Request Analysis: {result.confidence:.0%} confidence
Analysis Time: {result.analysis_time_ms:.0f}ms

Your request is viable, but risks detected:

RISK ASSESSMENT:
{issues_text}

{result.message}

═══════════════════════════════════════════════

Options:
  1. Proceed (aware of risks) ← RECOMMENDED
  2. Modify request (smaller scope)
  3. Abort

Your choice [1-3]: """
```

---

## 🔧 Integration with Entry Point

```python
"""
src/entry_point/cortex_entry.py
(MODIFIED to add validation)
"""

class CortexEntry:
    def __init__(self, brain_path: Optional[str] = None, ...):
        # ... existing init ...
        
        # NEW: Initialize validator
        self.validator = RequestValidator(
            tier1_api=self.tier1,
            tier2_kg=self.tier2,
            tier3_context=self.tier3
        )
        self.validation_presenter = ValidationPresenter()
    
    def process(self, user_message: str, ...):
        try:
            # Step 1: Parse request (EXISTING)
            request = self.parser.parse(user_message, conversation_id)
            
            # Step 2: Validate & Enhance (NEW)
            validation_result = self.validator.validate_and_enhance(
                request=request,
                conversation_id=conversation_id
            )
            
            # Step 3: Present to user if needed (NEW)
            if validation_result.requires_user_input:
                # Format and present
                presentation = self.validation_presenter.present(
                    validation_result
                )
                print(presentation)
                
                # Get user decision (in real implementation, would be interactive)
                # For now, auto-accept enhancements, challenge blocks
                if validation_result.decision == ValidationDecision.CHALLENGE:
                    # In production: wait for user input
                    # For now: accept recommended alternative
                    user_decision = "ACCEPT"
                    
                    if user_decision == "ABORT":
                        return "Request aborted by user."
                    
                    # Apply alternative (would need to re-parse)
                    # ...
                
                elif validation_result.decision == ValidationDecision.ENHANCE:
                    # In production: wait for user input
                    # For now: accept all enhancements
                    user_decision = "ACCEPT_ALL"
                    
                    # Apply enhancements to request
                    request = self._apply_enhancements(
                        request,
                        validation_result.enhancements
                    )
            
            # Step 4: Route to agent (EXISTING - continues as before)
            response = self.router.execute(request)
            
            # ... rest of existing flow ...
```

---

**Status:** Code examples complete  
**Ready for:** Implementation Phase 1  
**Related:** `22-request-validator-enhancer.md`, `REQUEST-VALIDATOR-IMPLEMENTATION-SUMMARY.md`
