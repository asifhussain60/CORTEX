# Knowledge Synthesis & Governance Integration (Synthesis Layer)

## Overview

The Synthesis Layer aggregates signals from Language, Examination, and Navigation layers, applies governance rules, and integrates business domain context to produce final routing decisions with confidence scores.

## Synthesis Architecture

```mermaid
graph TB
    LangSignals["Language Signals<br/>Intent list<br/>+ confidence"]
    
    ExamSignals["Examination Signals<br/>AST metadata<br/>+ code quality"]
    
    NavSignals["Navigation Signals<br/>History patterns<br/>+ hotspots"]
    
    subgraph SynthesisLayer["Synthesis Layer"]
        Agg["Signal Aggregator<br/>Collect signals"]
        Weight["Weighted Combiner<br/>Apply weights"]
        Gov["Governance Enforcer<br/>TIER 0-3 rules"]
        Domain["Domain Enricher<br/>Business context"]
        Score["Confidence Calculator<br/>Final score"]
    end
    
    LangSignals --> Agg
    ExamSignals --> Agg
    NavSignals --> Agg
    
    Agg --> Weight
    Weight --> Gov
    Gov --> Domain
    Domain --> Score
    
    Score --> Decision{"Score<br/>≥ 0.7?"}
    
    Decision -->|YES| Route["Route to<br/>Orchestrator"]
    Decision -->|NO| Disamb["Request<br/>Clarification"]
    
    style SynthesisLayer fill:#f9e6ff,stroke:#9B59B6,stroke-width:2px
    style Route fill:#e6ffe6,stroke:#27AE60,stroke-width:2px
    style Disamb fill:#ffe6e6,stroke:#E74C3C,stroke-width:2px
```

## Signal Aggregation

```mermaid
graph LR
    L["Language<br/>Intent score<br/>0.92"]
    E["Examination<br/>Code quality<br/>0.78"]
    N["Navigation<br/>File stability<br/>0.85"]
    
    Agg["Aggregator<br/>Combines signals"]
    
    L --> Agg
    E --> Agg
    N --> Agg
    
    Agg -->|Normalized| NL["L: 0.92"]
    Agg -->|Normalized| NE["E: 0.78"]
    Agg -->|Normalized| NN["N: 0.85"]
    
    NL --> Weight["Weighted Sum<br/>= 0.92*w_L<br/>  + 0.78*w_E<br/>  + 0.85*w_N"]
    NE --> Weight
    NN --> Weight
    
    Weight --> Result["Pre-weighted<br/>Score: 0.85"]
    
    style Agg fill:#d4e6ff,stroke:#2E5C8A,stroke-width:2px
```

## Governance Rule Application (TIER 0-3)

```mermaid
graph TB
    Signals["Aggregated<br/>Signals"]
    
    subgraph GovernanceRules["Governance Tiers"]
        TIER0["TIER 0: SKULL Rules<br/>Immutable core rules<br/>CORE-001 through CORE-029"]
        TIER1["TIER 1: Domain Rules<br/>Domain-specific customizations<br/>DOMAIN-001 through DOMAIN-020"]
        TIER2["TIER 2: Context Rules<br/>Engineering standards<br/>CONTEXT-001 through CONTEXT-030"]
        TIER3["TIER3: Knowledge Rules<br/>Best practices & guidance<br/>KNOWLEDGE-001 through KNOWLEDGE-050"]
    end
    
    Signals --> TIER0
    TIER0 -->|Must comply| Check0["Check: All<br/>TIER 0 rules<br/>satisfied?"]
    Check0 -->|FAIL| Reject["REJECT<br/>Operation"]
    Check0 -->|PASS| TIER1
    
    TIER1 -->|Apply| Check1["Evaluate<br/>TIER 1 rules"]
    Check1 --> TIER2
    
    TIER2 -->|Apply| Check2["Evaluate<br/>TIER 2 rules"]
    Check2 --> TIER3
    
    TIER3 -->|Suggest| Check3["Evaluate<br/>TIER 3 guidance"]
    Check3 --> Result["Governance-Adjusted<br/>Score"]
    
    style TIER0 fill:#8B0000,color:#fff,stroke-width:2px
    style TIER1 fill:#1E90FF,color:#fff
    style TIER2 fill:#228B22,color:#fff
    style TIER3 fill:#FFB6C1,color:#000
    style Reject fill:#E74C3C,color:#fff,stroke-width:2px
```

## Governance Rule Examples

### TIER 0 Rule: CORE-008 (TDD First)

```
Rule ID: CORE-008
Name: Test-Driven Development
Severity: BLOCKED

Rule:
- Implementation code must have corresponding tests
- Tests must be created BEFORE implementation
- Red → Green → Refactor cycle mandatory

Synthesis Application:
Input: Operation to implement new function
Check: Does test file exist?
- YES → Allow routing
- NO → Request test creation first
```

### TIER 0 Rule: CORE-013 (No Bare Except)

```
Rule ID: CORE-013
Name: Specific Exception Handling
Severity: STRICT

Rule:
- No bare except: clauses
- All exceptions must be specific types
- Fallback exceptions allowed only in specific contexts

Synthesis Application:
Input: Code contains "except:"
Check: Is this a known exception type?
- YES → Allow
- NO → REJECT with guidance
```

### TIER 2 Rule: Context-Aware Execution

```
Rule ID: CONTEXT-AWARE-001
Name: Context-Aware Orchestration
Severity: MODERATE

Rule:
- Operations in PHASE_E must include tests
- Refactoring only in designated code areas
- Deployments require approval

Synthesis Application:
Input: Refactoring operation, PHASE_E execution context
Check: Is refactoring allowed in PHASE_E?
- YES → Require test coverage
- NO → Suggest deferring to next phase
```

## Domain Brain Integration

```mermaid
graph TB
    Synthesis["Synthesis Results<br/>Pre-domain signals"]
    
    subgraph DomainBrain["Domain Brain"]
        Domains["Domain<br/>Catalog"]
        Services["Service<br/>Registry"]
        APIs["API<br/>Definitions"]
        Knowledge["Business<br/>Knowledge"]
    end
    
    Synthesis -->|Query| Domains
    Synthesis -->|Query| Services
    Synthesis -->|Query| APIs
    Synthesis -->|Query| Knowledge
    
    Domains -->|Enrich| Enriched["Enriched Context<br/>- Target domain identified<br/>- Related services mapped<br/>- API compatibility checked<br/>- Business implications noted"]
    Services --> Enriched
    APIs --> Enriched
    Knowledge --> Enriched
    
    Enriched --> AdjustedScore["Adjusted Confidence<br/>Score"]
    
    style DomainBrain fill:#fff9e6,stroke:#F39C12,stroke-width:2px
```

## Confidence Calculation Algorithm

```mermaid
graph TB
    Raw["Raw Signals<br/>L=0.92, E=0.78, N=0.85"]
    
    Normalize["Normalize to [0,1]<br/>Apply min/max scaling"]
    Raw --> Normalize
    
    Normalize --> Weighted["Weighted Sum<br/>score = w_L*L + w_E*E + w_N*N"]
    
    Weighted --> GovAdjust["Governance Adjustment<br/>TIER 0: blocks?<br/>TIER 1-2: reduce 0.1?<br/>TIER 3: hints only"]
    
    GovAdjust --> DomainAdjust["Domain Adjustment<br/>In-scope domain? +0.05<br/>Cross-domain? -0.1<br/>Risky domain? -0.15"]
    
    DomainAdjust --> FinalScore["Final Confidence<br/>Score: 0.82"]
    
    FinalScore --> Threshold{"Threshold<br/>Check"}
    
    Threshold -->|≥ 0.7| Auto["AUTO-ROUTE<br/>High confidence"]
    Threshold -->|0.5-0.7| Review["REVIEW<br/>Moderate confidence"]
    Threshold -->|< 0.5| Reject["REJECT<br/>Low confidence"]
    
    style Auto fill:#e6ffe6,stroke:#27AE60,stroke-width:2px
    style Review fill:#fff9e6,stroke:#F39C12,stroke-width:2px
    style Reject fill:#ffe6e6,stroke:#E74C3C,stroke-width:2px
```

## Configuration: Signal Weights

```yaml
synthesis_engine:
  signal_weights:
    language: 0.35      # Language intent strength
    examination: 0.30   # Code quality signals
    navigation: 0.20    # Historical patterns
    governance: 0.10    # Rule compliance
    domain: 0.05        # Business context
    
  governance_adjustments:
    tier_0_violation: -1.0        # Hard block
    tier_1_violation: -0.15       # Reduce by 15%
    tier_2_violation: -0.10       # Reduce by 10%
    tier_3_suggestion: -0.05      # Reduce by 5%
    
  domain_adjustments:
    in_scope: +0.05
    cross_domain: -0.10
    high_risk: -0.15
    new_domain: -0.20
    
  confidence_thresholds:
    auto_route: 0.70    # Auto-execute
    review: 0.50        # Request clarification
    reject: 0.00        # Too low
```

## Implementation: Synthesizer

```python
class Synthesizer:
    """
    Aggregates all LENS signals and applies governance rules
    to produce routing decisions.
    """
    
    def synthesize(self, 
                  language_signals: IntentSignals,
                  examination_signals: ExaminationSignals,
                  navigation_signals: NavigationSignals) -> SynthesisResult:
        """
        Synthesize all signals into routing decision.
        
        Args:
            language_signals: Intent classification results
            examination_signals: AST analysis results
            navigation_signals: Git history results
            
        Returns:
            SynthesisResult with confidence score and routing decision
        """
        # 1. Normalize signals
        normalized = self._normalize_signals(
            language_signals,
            examination_signals,
            navigation_signals
        )
        
        # 2. Apply weights
        weighted_score = self._apply_weights(normalized)
        
        # 3. Apply governance rules
        governed_score = self._apply_governance(weighted_score)
        
        # 4. Enrich with domain context
        enriched_score = self._enrich_domain(governed_score)
        
        # 5. Calculate final confidence
        final_score = self._calculate_confidence(enriched_score)
        
        # 6. Make routing decision
        decision = self._make_decision(final_score)
        
        return SynthesisResult(
            score=final_score,
            decision=decision,
            reasoning=self._generate_reasoning(final_score)
        )
    
    def _apply_governance(self, score: float) -> float:
        """
        Apply TIER 0-3 governance rules.
        
        TIER 0: Hard blocks (multiply by 0.0)
        TIER 1-2: Soft penalties (reduce by percentage)
        TIER 3: Guidance only (no scoring change)
        """
        registry = GovernanceRegistry.instance()
        
        # Check TIER 0 (immutable rules)
        violations_tier0 = registry.check_tier0(self.operation)
        if violations_tier0:
            return 0.0  # Hard block
        
        # Check TIER 1-2 (soft constraints)
        violations_tier1 = registry.check_tier1(self.operation)
        violations_tier2 = registry.check_tier2(self.operation)
        
        penalty = 0.0
        penalty += len(violations_tier1) * 0.15
        penalty += len(violations_tier2) * 0.10
        
        return max(0.0, score - penalty)
```

## Routing Decision Logic

```mermaid
graph TB
    FinalScore["Final Confidence<br/>Score: S"]
    
    Check1{"Is S ≥ 0.7?"}
    
    Check1 -->|YES| AutoRoute["AUTO-ROUTE<br/>Decision Type:<br/>CONFIDENT"]
    
    Check1 -->|NO| Check2{"Is S ≥ 0.5?"}
    
    Check2 -->|YES| Review["REVIEW<br/>Decision Type:<br/>MODERATE"]
    
    Check2 -->|NO| Reject["REJECT<br/>Decision Type:<br/>LOW_CONFIDENCE"]
    
    AutoRoute --> ExecAuto["Execute<br/>Immediately"]
    Review --> ExecReview["Present Options<br/>to User"]
    Reject --> ExecReject["Decline<br/>Request"]
    
    style AutoRoute fill:#e6ffe6,stroke:#27AE60,stroke-width:2px
    style Review fill:#fff9e6,stroke:#F39C12,stroke-width:2px
    style Reject fill:#ffe6e6,stroke:#E74C3C,stroke-width:2px
```

## Test Coverage

- **Signal Aggregation**: Combine signals correctly
- **Governance Application**: All TIER 0-3 rules enforced
- **Domain Enrichment**: Business context properly applied
- **Confidence Calculation**: Score bounds [0, 1]
- **Threshold Logic**: Correct routing decisions
- **Edge Cases**: No confidence signals, conflicting rules

## Related Documentation

- [LENS Overview](01-lens-overview.md)
- [Intent Classification](02-intent-classification.md)
- [AST Analysis](03-ast-analysis.md)
- [Git Navigation](04-git-navigation.md)
- [Governance Rules](../04-architecture/governance-rules.md)
- [Domain Brain](../04-architecture/4-domain-brain.md)
