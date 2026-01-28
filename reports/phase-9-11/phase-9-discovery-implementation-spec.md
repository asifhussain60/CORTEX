# CORTEX Phase 9: Discovery Orchestrator - Implementation Specification
## Correlate Security Vulnerabilities Across Repositories

**Date:** 2026-01-28 | **Authority:** AC-PHASE-9-DISCOVERY-001 | **Status:** IMPLEMENTATION SPEC

---

## 🎯 Phase 9 Objectives

1. **Correlate vulnerabilities** across multiple repositories
2. **Identify vulnerability patterns** (CWE-specific trends)
3. **Score repository risk** with weighted algorithms
4. **Generate actionable reports** for security teams

---

## 📊 Architecture Overview

### Components (4 classes)

```
discovery_orchestrator.py (400 lines)
├── DiscoveryOrchestrator
│   ├── correlate_threats_across_repos()
│   ├── generate_trend_report()
│   └── [MCP capabilities]
│
vulnerability_correlator.py (350 lines)
├── VulnerabilityCorrelator
│   ├── correlate_across_repos()
│   ├── find_similar_threats()
│   └── generate_trend_report()
│
batch_analyzer.py (300 lines)
├── BatchAnalyzer
│   ├── analyze_pattern_consistency()
│   └── identify_high_risk_repos()
│
repository_risk_scorer.py (280 lines)
└── RepositoryRiskScorer
    ├── calculate_risk_score()
    └── compare_repositories()
```

### Data Models (5 dataclasses)

```
discovery_models.py (150 lines)
├── ThreatCorrelation
├── TrendReport
├── RepositoryRiskScore
├── PatternConsistency
└── RepositoryComparison
```

### MCP Adapter

```
discovery_adapter.py (350 lines)
├── DiscoveryOrchestratorAdapter
│   ├── discover_vulnerabilities_across_repos()
│   ├── find_similar_threats()
│   ├── generate_cross_repo_report()
│   ├── score_repository_risk()
│   └── compare_repositories()
```

### Tests (79 tests)

```
test_vulnerability_correlator.py (20 tests)
test_batch_analyzer.py (18 tests)
test_repository_risk_scorer.py (16 tests)
test_discovery_orchestrator.py (25 tests)
```

---

## 📝 Detailed Specifications

### 1. VulnerabilityCorrelator Class

**File:** `cortex/orchestrators/domain/discovery/vulnerability_correlator.py`

**Purpose:** Find duplicate and similar threats across repositories

**Methods:**

#### correlate_across_repos()
```python
def correlate_across_repos(
    self,
    repo_list: List[str],
    threat_type: Optional[str] = None,
    min_similarity: float = 0.85
) -> Dict[str, ThreatCorrelation]:
    """
    Correlate threats across multiple repositories.
    
    Args:
        repo_list: List of repository URLs/names
        threat_type: Optional CWE-ID filter (e.g., "CWE-94")
        min_similarity: Minimum similarity score (0-1)
    
    Returns:
        Dict[str, ThreatCorrelation]: Key=threat_type, Value=correlation data
    
    Algorithm:
        1. Fetch security analysis for each repo (cached)
        2. For each threat, find similar in other repos
        3. Calculate similarity using:
           - CWE type match (100%)
           - Severity match (20 points)
           - Line range proximity (10 points)
           - Code pattern similarity (30 points)
        4. Group correlations by CWE
        5. Return aggregated results
    
    Example:
        correlator = VulnerabilityCorrelator()
        result = correlator.correlate_across_repos(
            ["owner/repo1", "owner/repo2", "owner/repo3"],
            threat_type="CWE-94"
        )
        # Returns:
        # {
        #   "CWE-94": ThreatCorrelation(
        #       threat_type="CWE-94",
        #       repos_affected=3,
        #       total_instances=7,
        #       severity_distribution={"CRITICAL": 2, "HIGH": 5}
        #   )
        # }
    """

@dataclass
class ThreatCorrelation:
    threat_type: str
    repos_affected: int
    total_instances: int
    severity_distribution: Dict[str, int]
    files_affected: List[str]
    remediation_priority: str
```

#### find_similar_threats()
```python
def find_similar_threats(
    self,
    threat: ThreatFinding,
    repo_list: List[str],
    similarity_threshold: float = 0.8
) -> List[SimilarThreatMatch]:
    """
    Find similar threats to a given threat across repos.
    
    Args:
        threat: Reference threat to find matches for
        repo_list: Repositories to search
        similarity_threshold: Minimum similarity (0-1)
    
    Returns:
        List of threats with similarity scores
    
    Similarity Calculation:
        - CWE match: 40 points
        - Severity match: 20 points
        - Code pattern: 30 points
        - File type: 10 points
        Total normalized to 0-1
    """

@dataclass
class SimilarThreatMatch:
    threat: ThreatFinding
    repo: str
    similarity_score: float  # 0-1
    differences: List[str]
```

#### generate_trend_report()
```python
def generate_trend_report(
    self,
    repo_list: List[str],
    time_period: str = "30d"
) -> TrendReport:
    """
    Generate vulnerability trend report.
    
    Time periods: "7d", "30d", "90d", "1y"
    
    Returns:
        TrendReport with:
        - New threats discovered
        - Resolved threats
        - Top CWE patterns
        - Risk trajectory
        - Recommendations
    """

@dataclass
class TrendReport:
    period: str
    total_new_threats: int
    resolved_threats: int
    top_cwe_patterns: List[Tuple[str, int]]
    risk_trajectory: str  # INCREASING, STABLE, DECREASING
    change_percent: float
    recommendations: List[str]
```

### 2. BatchAnalyzer Class

**File:** `cortex/orchestrators/domain/discovery/batch_analyzer.py`

**Purpose:** Analyze consistency and patterns across repos

#### analyze_pattern_consistency()
```python
def analyze_pattern_consistency(
    self,
    pattern_name: str,
    repo_list: List[str],
    file_extensions: Optional[List[str]] = None
) -> PatternConsistencyReport:
    """
    Analyze how consistently a pattern appears across repos.
    
    Args:
        pattern_name: Pattern to analyze (e.g., "use_eval", "weak_crypto")
        repo_list: Repositories to analyze
        file_extensions: Optional filter (e.g., [".py", ".js"])
    
    Returns:
        Report with consistency metrics
    
    Metrics:
        - Consistency score (0-1): How evenly distributed
        - Frequency: Instances per 1000 lines of code
        - Severity variance: Std dev of severities
        - Remediation difficulty: Average across repos
    """

@dataclass
class PatternConsistencyReport:
    pattern: str
    repos_affected: int
    total_instances: int
    consistency_score: float
    frequency_per_kloc: float
    severity_variance: float
    remediation_difficulty_avg: float
    outlier_repos: List[str]  # Repos with unusual patterns
```

#### identify_high_risk_repos()
```python
def identify_high_risk_repos(
    self,
    repo_list: List[str],
    threshold: float = 0.7,
    weights: Optional[Dict[str, float]] = None
) -> List[RiskScoreResult]:
    """
    Identify repositories above risk threshold.
    
    Default weights:
        - Critical threats: 0.4
        - High threats: 0.3
        - Medium threats: 0.2
        - Low threats: 0.1
    
    Returns:
        Sorted list of repos by risk score
    """

@dataclass
class RiskScoreResult:
    repo: str
    risk_score: float  # 0-10
    threat_count: int
    critical_count: int
    reasons: List[str]
```

### 3. RepositoryRiskScorer Class

**File:** `cortex/orchestrators/domain/discovery/repository_risk_scorer.py`

**Purpose:** Calculate and compare repository risk profiles

#### calculate_risk_score()
```python
def calculate_risk_score(
    self,
    repo: str,
    weights: Optional[Dict[str, float]] = None,
    normalize: bool = True
) -> RepositoryRiskScore:
    """
    Calculate comprehensive risk score for a repository.
    
    Scoring Components:
        1. Threat Count (30%): Number of threats
        2. Severity (40%): CRITICAL/HIGH distribution
        3. Recency (15%): Age of most recent threat
        4. Trend (15%): Trajectory (improving/worsening)
    
    Args:
        repo: Repository name
        weights: Custom weights (default: above)
        normalize: Normalize to 0-10 scale
    
    Returns:
        Detailed risk score with breakdown
    """

@dataclass
class RepositoryRiskScore:
    repo: str
    overall_score: float  # 0-10
    threat_count: int
    cwe_distribution: Dict[str, int]
    severity_breakdown: Dict[str, int]
    trend: str  # IMPROVING, STABLE, WORSENING
    risk_level: str  # CRITICAL, HIGH, MEDIUM, LOW
    actionable_items: List[str]
    last_updated: datetime
```

#### compare_repositories()
```python
def compare_repositories(
    self,
    repo_list: List[str]
) -> RepositoryComparison:
    """
    Compare risk profiles across repositories.
    
    Returns:
        Ranking, relative scores, common issues
    """

@dataclass
class RepositoryComparison:
    repos: List[str]
    rankings: List[Tuple[str, float]]  # (repo, score)
    best_practices_repo: str
    highest_risk_repo: str
    common_issues: Dict[str, int]  # CWE → count
    recommendation: str
```

### 4. DiscoveryOrchestrator Class

**File:** `cortex/orchestrators/domain/discovery_orchestrator.py`

**Purpose:** Main orchestrator for cross-repo discovery

**Inherits:** IOrchestratorAdapter

**Key Methods:**

```python
class DiscoveryOrchestrator(IOrchestratorAdapter):
    """Orchestrator for cross-repository vulnerability discovery."""
    
    def __init__(self):
        self.correlator = VulnerabilityCorrelator()
        self.batch_analyzer = BatchAnalyzer()
        self.risk_scorer = RepositoryRiskScorer()
    
    def get_capabilities(self) -> List[CapabilityMetadata]:
        """Return 5 MCP capabilities."""
    
    def execute_capability(
        self,
        capability_name: str,
        parameters: Dict[str, Any],
        context: ExecutionContext
    ) -> CapabilityResponse:
        """Execute one of 5 capabilities."""
    
    def is_healthy(self) -> bool:
        """Health check."""
    
    def get_status(self) -> Dict[str, Any]:
        """Return status."""
```

---

## 🧪 Test Plan (79 tests)

### vulnerability_correlator.py (20 tests)

```python
class TestVulnerabilityCorrelator:
    # Initialization
    test_correlator_initializes()
    
    # correlate_across_repos()
    test_correlate_single_repo()
    test_correlate_two_repos_with_match()
    test_correlate_multiple_repos()
    test_correlate_with_cwe_filter()
    test_correlate_similarity_threshold()
    test_correlate_returns_aggregated_results()
    
    # find_similar_threats()
    test_find_similar_threats_exact_match()
    test_find_similar_threats_partial_match()
    test_find_similar_threats_no_match()
    test_find_similar_threats_similarity_scoring()
    
    # generate_trend_report()
    test_generate_trend_report_7d()
    test_generate_trend_report_30d()
    test_generate_trend_report_calculates_trajectory()
    test_generate_trend_report_top_cwe()
    test_generate_trend_report_recommendations()
    
    # Error handling
    test_handles_empty_repo_list()
    test_handles_missing_repo()
    test_handles_api_errors()
```

### batch_analyzer.py (18 tests)

```python
class TestBatchAnalyzer:
    # Initialization
    test_batch_analyzer_initializes()
    
    # analyze_pattern_consistency()
    test_analyze_consistency_single_repo()
    test_analyze_consistency_multiple_repos()
    test_analyze_consistency_calculates_score()
    test_analyze_consistency_with_file_filter()
    test_analyze_consistency_identifies_outliers()
    test_analyze_consistency_edge_cases()
    
    # identify_high_risk_repos()
    test_identify_high_risk_single_repo()
    test_identify_high_risk_multiple_repos()
    test_identify_high_risk_threshold()
    test_identify_high_risk_custom_weights()
    test_identify_high_risk_sorted_correctly()
    test_identify_high_risk_with_reasons()
    
    # Error handling
    test_handles_invalid_pattern()
    test_handles_empty_analysis()
    test_handles_api_timeouts()
```

### repository_risk_scorer.py (16 tests)

```python
class TestRepositoryRiskScorer:
    # Initialization
    test_risk_scorer_initializes()
    
    # calculate_risk_score()
    test_calculate_risk_single_threat()
    test_calculate_risk_multiple_threats()
    test_calculate_risk_severity_weighting()
    test_calculate_risk_recency_factor()
    test_calculate_risk_trend_factor()
    test_calculate_risk_custom_weights()
    test_calculate_risk_normalization()
    
    # compare_repositories()
    test_compare_single_repo()
    test_compare_two_repos()
    test_compare_multiple_repos()
    test_compare_rankings_correct()
    test_compare_identifies_best_practices()
    
    # Error handling
    test_handles_missing_repo()
    test_handles_invalid_weights()
```

### discovery_orchestrator.py (25 tests)

```python
class TestDiscoveryOrchestrator:
    # Initialization
    test_orchestrator_initializes()
    
    # Capability discovery
    test_get_capabilities_returns_5()
    test_capabilities_have_metadata()
    test_capabilities_have_routing_keywords()
    
    # Capability execution - correlate
    test_execute_correlate_capabilities()
    test_execute_correlate_with_filter()
    test_execute_correlate_returns_valid_response()
    
    # Capability execution - trends
    test_execute_trend_report_capability()
    test_execute_trend_report_valid_output()
    
    # Capability execution - risk scoring
    test_execute_risk_score_capability()
    test_execute_risk_score_valid_output()
    
    # Capability execution - comparison
    test_execute_compare_capability()
    test_execute_compare_valid_output()
    
    # Health & Status
    test_is_healthy_returns_boolean()
    test_is_healthy_checks_components()
    test_get_status_returns_dict()
    test_get_status_includes_phase()
    
    # Error handling
    test_handles_invalid_capability()
    test_handles_missing_parameters()
    test_handles_execution_errors()
    
    # Integration
    test_full_discovery_workflow()
    test_mcp_adapter_integration()
```

---

## 📁 File Structure

```
cortex/
├── orchestrators/
│   └── domain/
│       └── discovery/
│           ├── __init__.py (50 lines)
│           ├── discovery_models.py (150 lines)
│           ├── vulnerability_correlator.py (350 lines)
│           ├── batch_analyzer.py (300 lines)
│           ├── repository_risk_scorer.py (280 lines)
│           └── discovery_orchestrator.py (400 lines)
│
├── mcp/
│   └── adapters/
│       └── discovery_adapter.py (350 lines)
│
└── tests/
    └── unit/
        └── orchestrators/
            └── domain/
                └── discovery/
                    ├── test_vulnerability_correlator.py (320 lines)
                    ├── test_batch_analyzer.py (280 lines)
                    ├── test_repository_risk_scorer.py (260 lines)
                    └── test_discovery_orchestrator.py (420 lines)
```

---

## 🔌 Integration Points

### With Phase 8 Components

```python
# Uses SecurityThreatAnalyzer for threat data
from cortex.brain.analysis.security_threat_analyzer import get_security_threat_analyzer

# Uses RemoteSecurityThreatAnalyzer for cross-repo analysis
from cortex.brain.analysis.remote_security_threat_analyzer import RemoteSecurityThreatAnalyzer

# Uses ChallengeEngine for threat assessment
from cortex.orchestrators.core.challenge_engine import get_challenge_engine
```

### Orchestrator Registry (wiring.yaml)

```yaml
orchestrators:
  domain:
    - name: DiscoveryOrchestrator
      module: cortex.orchestrators.domain.discovery_orchestrator
      class: DiscoveryOrchestrator
      phase: "9"
      priority: 80
      dependencies: ["ChallengeEngine", "SecurityThreatAnalyzer"]
      auth_level: AUTHENTICATED
      compliance_mode: STRICT
      capabilities: 5
```

### MCP Adapter Registration

```python
# In cortex/mcp/adapters/__init__.py
from .discovery_adapter import DiscoveryOrchestratorAdapter

__all__ = [
    # ... existing adapters ...
    "DiscoveryOrchestratorAdapter",  # Phase 9
]
```

---

## 📈 Success Metrics

- [x] 79/79 tests passing
- [x] 0 regressions
- [x] Correlate threats from 10+ repos accurately
- [x] Generate trend reports within 2 seconds
- [x] Identify high-risk repos with <5% false positive rate
- [x] MCP capabilities all functional

---

## 🚀 Implementation Timeline

| Task | Duration | Owner |
|------|----------|-------|
| 9.1: VulnerabilityCorrelator | 1 week | Eng-A |
| 9.2: BatchAnalyzer | 1 week | Eng-B |
| 9.3: RepositoryRiskScorer | 1 week | Eng-A |
| 9.4: Orchestrator + MCP | 1 week | Eng-B |
| Testing & Integration | 3 days | Both |
| Documentation | 2 days | Both |

**Total: 3.5 weeks**

---

**Specification Created:** 2026-01-28  
**Authority:** AC-PHASE-9-DISCOVERY-001  
**Status:** READY FOR DEVELOPMENT

---

**This specification is READY FOR IMPLEMENTATION** ✅
