# 📚 CORTEX Phase 9 Quick Reference Card
## Discovery Orchestrator Implementation Guide | Ready for Development

---

## 🎯 Phase 9 at a Glance

| Aspect | Details |
|--------|---------|
| **Phase Name** | Discovery Orchestrator |
| **Objective** | Cross-repository vulnerability correlation |
| **Duration** | 3-4 weeks |
| **Team Size** | 2 engineers |
| **Tests Required** | 79 unit tests |
| **Production Code** | 1,330 lines |
| **Difficulty** | Medium-High |
| **Dependencies** | Phase 8.5+ complete ✅ |

---

## 📂 File Structure

```
cortex/
├── orchestrators/
│   └── domain/
│       ├── discovery_orchestrator.py          [NEW - 400 lines]
│       └── __init__.py
├── brain/
│   └── analysis/
│       ├── vulnerability_correlator.py        [NEW - 350 lines]
│       ├── batch_analyzer.py                  [NEW - 300 lines]
│       ├── repository_risk_scorer.py          [NEW - 280 lines]
│       └── __init__.py
├── mcp/
│   └── adapters/
│       └── discovery_adapter.py               [NEW - 350 lines]
└── wiring/
    └── specifications/
        └── wiring.yaml                        [MODIFY - add registry]

tests/
├── unit/
│   ├── orchestrators/
│   │   └── domain/
│   │       └── test_discovery_orchestrator.py [NEW - 200 lines, 25 tests]
│   ├── brain/
│   │   └── analysis/
│   │       ├── test_vulnerability_correlator.py [NEW - 180 lines, 20 tests]
│   │       ├── test_batch_analyzer.py         [NEW - 140 lines, 18 tests]
│   │       └── test_repository_risk_scorer.py [NEW - 140 lines, 16 tests]
│   └── mcp/
│       └── adapters/
│           └── test_discovery_adapter.py      [NEW - 180 lines, 5 tests]
└── integration/
    └── test_discovery_integration.py          [NEW - 150 lines, 5 tests]

docs/
└── guides/
    └── phase-9-discovery-guide.md             [NEW - developer guide]
```

---

## 🔑 Core Classes

### 1. VulnerabilityCorrelator
**Location:** `cortex/brain/analysis/vulnerability_correlator.py`  
**Purpose:** Find and correlate similar vulnerabilities across repositories

```python
class VulnerabilityCorrelator:
    """Correlate vulnerabilities across repositories."""
    
    def correlate_across_repos(
        self, 
        threat: SecurityThreat,
        repo_list: List[RepositoryInfo]
    ) -> List[ThreatCorrelation]:
        """Find repositories with similar threats."""
    
    def find_similar_threats(
        self,
        threat: SecurityThreat,
        similarity_threshold: float = 0.8
    ) -> List[ThreatCorrelation]:
        """Find threats with similar patterns."""
    
    def generate_trend_report(
        self,
        threats: List[SecurityThreat]
    ) -> TrendReport:
        """Generate trend analysis from threats."""
```

**Key Methods:** 20+ methods total  
**Tests:** 20 unit tests  
**Dependencies:** SecurityThreatAnalyzer, RemoteSecurityThreatAnalyzer  

### 2. BatchAnalyzer
**Location:** `cortex/brain/analysis/batch_analyzer.py`  
**Purpose:** Analyze patterns consistently across batches of repositories

```python
class BatchAnalyzer:
    """Analyze vulnerability patterns in batch processing."""
    
    def analyze_pattern_consistency(
        self,
        threat_patterns: List[ThreatPattern],
        batch_size: int = 100
    ) -> PatternConsistency:
        """Analyze pattern consistency across batch."""
    
    def identify_high_risk_repos(
        self,
        repos: List[RepositoryInfo],
        risk_threshold: float = 0.7
    ) -> List[RepositoryRiskInfo]:
        """Identify repositories with high risk patterns."""
```

**Key Methods:** 15+ methods  
**Tests:** 18 unit tests  
**Dependencies:** RepositoryRiskScorer, RemoteSecurityThreatAnalyzer

### 3. RepositoryRiskScorer
**Location:** `cortex/brain/analysis/repository_risk_scorer.py`  
**Purpose:** Calculate risk scores for individual and comparative analysis

```python
class RepositoryRiskScorer:
    """Calculate repository-level risk scores."""
    
    def calculate_risk_score(
        self,
        repo: RepositoryInfo,
        threats: List[SecurityThreat]
    ) -> RepositoryRiskScore:
        """Calculate risk score for single repository."""
    
    def compare_repositories(
        self,
        repos: List[RepositoryInfo]
    ) -> RepositoryComparison:
        """Compare risk levels across repositories."""
```

**Key Methods:** 12+ methods  
**Tests:** 16 unit tests  
**Dependencies:** SecurityThreatAnalyzer  

### 4. DiscoveryOrchestrator
**Location:** `cortex/orchestrators/domain/discovery_orchestrator.py`  
**Purpose:** Main orchestrator implementing IOrchestratorAdapter

```python
class DiscoveryOrchestrator(IOrchestratorAdapter):
    """Orchestrate vulnerability discovery across repositories."""
    
    async def execute(
        self,
        request: OrchestrationRequest
    ) -> OrchestrationResponse:
        """Execute discovery workflow."""
    
    def get_capabilities(self) -> List[CapabilityInfo]:
        """Return 5 MCP capabilities."""
    
    def get_health(self) -> HealthStatus:
        """Return orchestrator health."""
```

**Capabilities (5):**
1. `correlate_vulnerabilities` - Find similar threats
2. `find_similar_issues` - Cross-repo matching
3. `generate_trend_report` - Threat trends
4. `calculate_repository_risk` - Risk scoring
5. `compare_repositories` - Comparative analysis

**Tests:** 25 unit tests  
**Dependencies:** All 3 analyzers above

---

## 📊 Data Models

### ThreatCorrelation
```python
@dataclass
class ThreatCorrelation:
    source_repo: str
    target_repo: str
    threat_id: str
    similarity_score: float  # 0.0-1.0
    cwe_category: str
    severity: str  # "critical", "high", "medium", "low"
    evidence: List[str]
    correlation_method: str
    timestamp: datetime
```

### TrendReport
```python
@dataclass
class TrendReport:
    threat_type: str
    total_occurrences: int
    affected_repos: int
    trend_direction: str  # "increasing", "stable", "decreasing"
    severity_distribution: Dict[str, int]
    timeline: List[Tuple[datetime, int]]
    recommendations: List[str]
```

### RepositoryRiskScore
```python
@dataclass
class RepositoryRiskScore:
    repository: str
    overall_risk: float  # 0.0-10.0
    critical_threats: int
    high_threats: int
    medium_threats: int
    risk_factors: List[str]
    recommendations: List[str]
    last_updated: datetime
```

### PatternConsistency
```python
@dataclass
class PatternConsistency:
    pattern_type: str
    consistency_score: float  # 0.0-1.0
    repositories_affected: int
    consistency_details: Dict[str, Any]
    anomalies: List[str]
    recommendations: List[str]
```

### RepositoryComparison
```python
@dataclass
class RepositoryComparison:
    repositories: List[str]
    risk_rankings: List[Tuple[str, float]]
    common_threats: List[str]
    unique_threats: Dict[str, List[str]]
    recommendations: List[str]
```

---

## ✅ Implementation Checklist

### Week 1: Foundation & Core Analysis

- [ ] **Day 1-2: VulnerabilityCorrelator**
  - [ ] Implement `correlate_across_repos()` (40 lines)
  - [ ] Implement `find_similar_threats()` (45 lines)
  - [ ] Implement `generate_trend_report()` (50 lines)
  - [ ] Create 20 unit tests
  - [ ] Integration tests with SecurityThreatAnalyzer

- [ ] **Day 3: BatchAnalyzer**
  - [ ] Implement `analyze_pattern_consistency()` (40 lines)
  - [ ] Implement `identify_high_risk_repos()` (45 lines)
  - [ ] Create 18 unit tests
  - [ ] Integration tests

- [ ] **Day 4-5: RepositoryRiskScorer**
  - [ ] Implement `calculate_risk_score()` (35 lines)
  - [ ] Implement `compare_repositories()` (50 lines)
  - [ ] Create 16 unit tests
  - [ ] Integration tests

### Week 2: Orchestrator & Integration

- [ ] **Day 1-2: DiscoveryOrchestrator**
  - [ ] Implement core class (100 lines)
  - [ ] Implement `execute()` method (120 lines)
  - [ ] Implement 5 MCP capabilities (100 lines)
  - [ ] Create 25 unit tests
  - [ ] Full integration tests (5 tests)

- [ ] **Day 3: MCP Adapter**
  - [ ] Implement DiscoveryAdapter (350 lines)
  - [ ] Register 5 capabilities
  - [ ] Create 5 unit tests
  - [ ] Health checking

- [ ] **Day 4-5: Registry & Wiring**
  - [ ] Register in wiring.yaml
  - [ ] Integration with InteractionOrchestrator
  - [ ] End-to-end testing
  - [ ] Documentation

### Week 3: Testing & Documentation

- [ ] **Day 1-2: Comprehensive Testing**
  - [ ] All 79 tests passing
  - [ ] 0 regressions
  - [ ] Edge case coverage
  - [ ] Performance benchmarking

- [ ] **Day 3-4: Documentation**
  - [ ] API reference (Google docstrings)
  - [ ] Integration guide
  - [ ] Usage examples
  - [ ] Troubleshooting guide

- [ ] **Day 5: Code Review & Cleanup**
  - [ ] Full code review
  - [ ] CORE rule compliance check
  - [ ] Type hint verification
  - [ ] Final polish

### Week 4: Final Integration & Sign-Off

- [ ] Production deployment readiness
- [ ] Stakeholder review
- [ ] Performance optimization
- [ ] Final testing & sign-off

---

## 🧪 Test Strategy (79 Tests)

### Unit Tests (74 tests)
```
VulnerabilityCorrelator:     20 tests
  ├─ correlate_across_repos:  6 tests
  ├─ find_similar_threats:    7 tests
  └─ generate_trend_report:   7 tests

BatchAnalyzer:               18 tests
  ├─ analyze_pattern_consistency: 9 tests
  └─ identify_high_risk_repos:    9 tests

RepositoryRiskScorer:        16 tests
  ├─ calculate_risk_score:    8 tests
  └─ compare_repositories:    8 tests

DiscoveryOrchestrator:       25 tests
  ├─ execute():              8 tests
  ├─ get_capabilities():     7 tests
  ├─ get_health():           5 tests
  └─ edge cases:             5 tests

DiscoveryAdapter:            5 tests
  └─ MCP integration:        5 tests
```

### Integration Tests (5 tests)
- End-to-end discovery flow
- Phase 8 integration
- Wiring registry integration
- MCP capability discovery
- Performance validation

---

## 🔗 Dependencies & Integration

### Depends On (Phase 8.5+)
- ✅ SecurityThreatAnalyzer
- ✅ RemoteSecurityThreatAnalyzer
- ✅ RecommendationEngine
- ✅ ChallengeEngine
- ✅ wiring.yaml system

### Integrates With
- InteractionOrchestrator
- MasterOrchestrator
- TotalRecallAgent
- GitBackedRegistry

### Provides To (Phase 10)
- Enhanced LENS intelligence
- Cross-repo context
- Vulnerability patterns
- Risk scoring baselines

---

## 📞 Development Resources

### Documentation
- Phase 9 Implementation Spec: `reports/phase-9-11/phase-9-discovery-implementation-spec.md` (620 lines)
- Full Roadmap: `reports/phase-9-11/roadmap-phases-9-11-planning.md` (550 lines)
- Strategic Vision: `reports/phase-9-11/strategic-vision-final-summary.md` (385 lines)

### Reference Code
- SecurityThreatAnalyzer: `cortex/brain/analysis/security_threat_analyzer.py`
- RemoteSecurityThreatAnalyzer: `cortex/orchestrators/support/remote_security_threat_analyzer.py`
- RecommendationEngineAdapter: `cortex/mcp/adapters/recommendation_adapter.py`

### Test Examples
- Phase 8 Tests: `tests/unit/orchestrators/support/`
- Adapter Tests: `tests/unit/mcp/adapters/`

---

## 🚀 Development Commands

```bash
# Setup development environment
git checkout -b feature/phase-9-discovery-orchestrator

# Create files
mkdir -p cortex/brain/analysis
mkdir -p cortex/orchestrators/domain
mkdir -p cortex/mcp/adapters

# Run tests during development
pytest tests/unit/brain/analysis/ -v
pytest tests/unit/orchestrators/domain/ -v
pytest tests/unit/mcp/adapters/ -v

# Full test suite
pytest tests/ -v --cov=cortex/brain --cov=cortex/orchestrators --cov=cortex/mcp

# Pre-commit validation
git add . && git commit -m "Phase 9 implementation"

# Create commit
git commit -m "AC-PHASE-9-DISCOVERY: Full Discovery Orchestrator implementation (79 tests, 1,330 lines)"
```

---

## ⚠️ Common Pitfalls

1. **Similarity Scoring:** Must handle 0.0-1.0 range correctly
2. **Performance:** Batch processing should be efficient for 1000+ repos
3. **GitHub API Limits:** Cache results to avoid rate limiting
4. **Test Fixtures:** Mock RemoteSecurityThreatAnalyzer appropriately
5. **Type Hints:** Must use proper Union/Optional for complex types

---

## ✅ Success Criteria

- [ ] All 79 tests passing
- [ ] 0 regressions with Phase 8
- [ ] Type hints on 100% of code
- [ ] Google-style docstrings complete
- [ ] MCP capabilities fully functional
- [ ] wiring.yaml registration complete
- [ ] No CORE rule violations
- [ ] Documentation complete
- [ ] Code review approved
- [ ] Production deployment ready

---

## 📞 Support & Questions

**For questions during implementation:**
1. Check `phase-9-discovery-implementation-spec.md` for detailed specs
2. Review test examples in Phase 8 code
3. Reference RecommendationEngineAdapter for MCP patterns
4. Consult CORTEX architecture documentation

---

**Phase 9 is ready for development kickoff!** 🚀

**Git Branch:** `feature/phase-9-discovery-orchestrator`  
**Duration:** 3-4 weeks  
**Team:** 2 engineers  
**Status:** APPROVED FOR IMPLEMENTATION ✅
