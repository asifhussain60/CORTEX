# LENS Synthesis

**Purpose:** Documentation of the LENS result synthesis process  
**Audience:** Architects, Senior Developers  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Overview](#overview)
- [Synthesis Pipeline](#synthesis-pipeline)
- [Conflict Resolution](#conflict-resolution)
- [Context Building](#context-building)
- [Quality Scoring](#quality-scoring)
- [Related Documents](#related-documents)

---

## Overview

LENS Synthesis is the process of combining outputs from multiple analyzers into a unified, coherent intelligence context. This ensures that CORTEX operations receive consistent, high-quality context regardless of which analyzers contributed.

```
┌─────────────────────────────────────────────────────────────────┐
│                    SYNTHESIS OVERVIEW                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐              │
│  │   Git   │ │   AST   │ │ Comment │ │ Pattern │  ...         │
│  │ Result  │ │ Result  │ │ Result  │ │ Result  │              │
│  └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘              │
│       │          │          │          │                       │
│       └──────────┴──────────┴──────────┘                       │
│                         │                                       │
│                         ▼                                       │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │                  SYNTHESIS ENGINE                        │  │
│  │                                                          │  │
│  │  1. Validation    → Check result integrity              │  │
│  │  2. Normalization → Standardize formats                 │  │
│  │  3. Correlation   → Link related data                   │  │
│  │  4. Conflict Res  → Resolve disagreements               │  │
│  │  5. Enrichment    → Add derived insights                │  │
│  │  6. Scoring       → Calculate quality metrics           │  │
│  │                                                          │  │
│  └─────────────────────────────────────────────────────────┘  │
│                         │                                       │
│                         ▼                                       │
│              ┌─────────────────────┐                           │
│              │  Unified Context    │                           │
│              └─────────────────────┘                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Synthesis Pipeline

### Stage 1: Validation

```python
class ResultValidator:
    """Validates analyzer results before synthesis."""
    
    def validate(
        self,
        results: Dict[str, AnalyzerResult]
    ) -> ValidationReport:
        """
        Validate all analyzer results.
        
        Checks:
        - Result structure integrity
        - Required fields present
        - Data type correctness
        - No critical errors
        """
        issues = []
        
        for name, result in results.items():
            # Check structure
            if not isinstance(result, AnalyzerResult):
                issues.append(f"{name}: Invalid result type")
                continue
            
            # Check success
            if not result.success and result.errors:
                issues.append(f"{name}: {result.errors}")
            
            # Check required fields
            if not result.data:
                issues.append(f"{name}: Empty data")
        
        return ValidationReport(
            valid=len(issues) == 0,
            issues=issues,
            results_count=len(results),
            valid_count=len(results) - len(issues)
        )
```

### Stage 2: Normalization

```python
class ResultNormalizer:
    """Normalizes analyzer results to standard formats."""
    
    def normalize(
        self,
        results: Dict[str, AnalyzerResult]
    ) -> Dict[str, NormalizedResult]:
        """
        Normalize all results to standard format.
        
        Operations:
        - Standardize file paths
        - Normalize timestamps
        - Convert types to canonical forms
        - Deduplicate entries
        """
        normalized = {}
        
        for name, result in results.items():
            normalized[name] = NormalizedResult(
                analyzer=name,
                data=self._normalize_data(result.data),
                metadata=self._normalize_metadata(result)
            )
        
        return normalized
    
    def _normalize_data(self, data: Dict) -> Dict:
        """Normalize data fields."""
        normalized = {}
        
        for key, value in data.items():
            # Normalize file paths
            if key.endswith("_file") or key.endswith("_path"):
                value = self._normalize_path(value)
            
            # Normalize timestamps
            if key.endswith("_at") or key.endswith("_time"):
                value = self._normalize_timestamp(value)
            
            normalized[key] = value
        
        return normalized
```

### Stage 3: Correlation

```python
class DataCorrelator:
    """Correlates data across analyzer results."""
    
    def correlate(
        self,
        results: Dict[str, NormalizedResult]
    ) -> CorrelatedData:
        """
        Find relationships between analyzer outputs.
        
        Correlations:
        - Git changes ↔ AST changes
        - Comments ↔ Functions
        - Patterns ↔ Classes
        """
        correlations = CorrelatedData()
        
        # Correlate git with AST
        if "git" in results and "ast" in results:
            correlations.git_ast = self._correlate_git_ast(
                results["git"],
                results["ast"]
            )
        
        # Correlate comments with functions
        if "comments" in results and "ast" in results:
            correlations.doc_coverage = self._correlate_docs(
                results["comments"],
                results["ast"]
            )
        
        return correlations
    
    def _correlate_git_ast(
        self,
        git: NormalizedResult,
        ast: NormalizedResult
    ) -> List[Correlation]:
        """Link git changes to AST elements."""
        correlations = []
        
        for change in git.data.get("file_changes", []):
            file_path = change["file"]
            
            # Find AST elements in this file
            elements = [
                e for e in ast.data.get("functions", [])
                if e["file"] == file_path
            ]
            
            if elements:
                correlations.append(Correlation(
                    source="git",
                    target="ast",
                    file=file_path,
                    elements=elements
                ))
        
        return correlations
```

### Stage 4: Conflict Resolution

See [Conflict Resolution](#conflict-resolution) section below.

### Stage 5: Enrichment

```python
class ContextEnricher:
    """Enriches context with derived insights."""
    
    def enrich(
        self,
        correlated: CorrelatedData,
        results: Dict[str, NormalizedResult]
    ) -> EnrichedContext:
        """
        Add derived insights to context.
        
        Enrichments:
        - Hot files (frequently changed)
        - Complexity hotspots
        - Documentation gaps
        - Pattern recommendations
        """
        enriched = EnrichedContext(base=correlated)
        
        # Hot files
        enriched.hot_files = self._identify_hot_files(results)
        
        # Complexity hotspots
        enriched.complexity_hotspots = self._find_complexity_hotspots(
            results
        )
        
        # Documentation gaps
        enriched.doc_gaps = self._find_doc_gaps(results)
        
        # Recommendations
        enriched.recommendations = self._generate_recommendations(
            results,
            correlated
        )
        
        return enriched
```

### Stage 6: Quality Scoring

See [Quality Scoring](#quality-scoring) section below.

---

## Conflict Resolution

### Conflict Types

| Conflict Type | Example | Resolution Strategy |
|---------------|---------|---------------------|
| **Value Conflict** | Different line counts | Trust most recent analyzer |
| **Type Conflict** | Different classifications | Use confidence scoring |
| **Missing Data** | Analyzer didn't run | Use fallback or exclude |
| **Contradictory** | Opposite conclusions | Flag for human review |

### Resolution Strategies

```python
class ConflictResolver:
    """Resolves conflicts between analyzer results."""
    
    STRATEGIES = {
        "value": "most_recent",
        "type": "confidence",
        "missing": "fallback",
        "contradictory": "flag",
    }
    
    def resolve(
        self,
        conflicts: List[Conflict]
    ) -> List[Resolution]:
        """Resolve all detected conflicts."""
        resolutions = []
        
        for conflict in conflicts:
            strategy = self.STRATEGIES.get(
                conflict.type,
                "flag"
            )
            
            resolution = self._apply_strategy(conflict, strategy)
            resolutions.append(resolution)
        
        return resolutions
    
    def _apply_strategy(
        self,
        conflict: Conflict,
        strategy: str
    ) -> Resolution:
        """Apply resolution strategy."""
        if strategy == "most_recent":
            return self._resolve_by_recency(conflict)
        elif strategy == "confidence":
            return self._resolve_by_confidence(conflict)
        elif strategy == "fallback":
            return self._apply_fallback(conflict)
        else:
            return Resolution(
                conflict=conflict,
                resolved=False,
                flagged=True,
                reason="Requires human review"
            )
```

### Confidence-Based Resolution

```python
def _resolve_by_confidence(
    self,
    conflict: Conflict
) -> Resolution:
    """Resolve conflict using confidence scores."""
    # Each analyzer provides confidence
    options = []
    
    for source, value in conflict.values.items():
        confidence = self._get_analyzer_confidence(
            source,
            conflict.field
        )
        options.append((source, value, confidence))
    
    # Select highest confidence
    best = max(options, key=lambda x: x[2])
    
    return Resolution(
        conflict=conflict,
        resolved=True,
        value=best[1],
        source=best[0],
        confidence=best[2],
        reason=f"Highest confidence: {best[2]:.2f}"
    )
```

---

## Context Building

### UnifiedIntelligenceContext Assembly

```python
class ContextBuilder:
    """Builds the final unified context."""
    
    def build(
        self,
        enriched: EnrichedContext,
        resolutions: List[Resolution]
    ) -> UnifiedIntelligenceContext:
        """
        Assemble the final unified context.
        """
        return UnifiedIntelligenceContext(
            # Code Analysis
            file_context=self._build_file_context(enriched),
            ast_analysis=self._build_ast_analysis(enriched),
            
            # Git Intelligence
            git_insights=self._build_git_insights(enriched),
            recent_commits=enriched.base.git_data.get("commits", []),
            
            # Documentation
            comment_analysis=self._build_comment_analysis(enriched),
            docstring_coverage=enriched.doc_coverage,
            
            # Patterns
            detected_patterns=enriched.patterns,
            anti_patterns=enriched.anti_patterns,
            
            # Relationships
            call_graph=self._build_call_graph(enriched),
            dependency_graph=self._build_dependency_graph(enriched),
            
            # Enrichments
            hot_files=enriched.hot_files,
            complexity_hotspots=enriched.complexity_hotspots,
            recommendations=enriched.recommendations,
            
            # Metadata
            synthesis_quality=self._calculate_quality(resolutions),
            conflict_count=len([r for r in resolutions if r.flagged]),
            timestamp=datetime.utcnow()
        )
```

---

## Quality Scoring

### Quality Dimensions

| Dimension | Weight | Measurement |
|-----------|--------|-------------|
| **Completeness** | 0.30 | % of analyzers successful |
| **Consistency** | 0.25 | Conflict resolution rate |
| **Coverage** | 0.20 | % of codebase analyzed |
| **Freshness** | 0.15 | Age of data |
| **Confidence** | 0.10 | Average analyzer confidence |

### Quality Calculator

```python
class QualityCalculator:
    """Calculates synthesis quality score."""
    
    WEIGHTS = {
        "completeness": 0.30,
        "consistency": 0.25,
        "coverage": 0.20,
        "freshness": 0.15,
        "confidence": 0.10,
    }
    
    def calculate(
        self,
        results: Dict[str, AnalyzerResult],
        resolutions: List[Resolution],
        enriched: EnrichedContext
    ) -> QualityScore:
        """Calculate overall quality score."""
        scores = {}
        
        # Completeness
        successful = sum(1 for r in results.values() if r.success)
        scores["completeness"] = successful / len(results)
        
        # Consistency
        resolved = sum(1 for r in resolutions if r.resolved)
        scores["consistency"] = resolved / max(len(resolutions), 1)
        
        # Coverage
        scores["coverage"] = enriched.coverage_ratio
        
        # Freshness
        age_hours = (datetime.utcnow() - enriched.oldest_data).hours
        scores["freshness"] = max(0, 1 - (age_hours / 24))
        
        # Confidence
        confidences = [
            r.confidence for r in results.values()
            if hasattr(r, 'confidence')
        ]
        scores["confidence"] = sum(confidences) / max(len(confidences), 1)
        
        # Weighted total
        total = sum(
            scores[dim] * weight
            for dim, weight in self.WEIGHTS.items()
        )
        
        return QualityScore(
            overall=total,
            breakdown=scores,
            grade=self._score_to_grade(total)
        )
    
    def _score_to_grade(self, score: float) -> str:
        """Convert score to letter grade."""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B"
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"
```

---

## Related Documents

- [LENS Architecture](architecture.md) — Technical design
- [Caching Strategy](caching.md) — Performance optimization
- [Governance Integration](governance.md) — Governance with LENS

---

*Part of CORTEX Architecture Documentation*
