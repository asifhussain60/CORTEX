# CORTEX Phases 9-11: Strategic Roadmap
## Discovery → Remote LENS Intelligence → AI-Enhanced Security

**Date:** 2026-01-28 | **Authority:** AC-PHASE-9-11-PLANNING-001 | **Status:** PLANNING

---

## 📋 Executive Summary

This roadmap outlines three strategic phases to extend CORTEX's security framework:

- **Phase 9:** Discovery Orchestrator - Correlate vulnerabilities across repositories
- **Phase 10:** Remote LENS Intelligence - Extend LENS to GitHub without cloning
- **Phase 11+:** AI-Enhanced Security - ML-driven threat detection and auto-remediation

**Total Estimated Effort:** 40-60 story points | **Timeline:** 2-3 months

---

## 🎯 Phase 9: Discovery Orchestrator (3-4 weeks)

### Objectives
1. Correlate security vulnerabilities across multiple repositories
2. Identify vulnerability patterns and trends
3. Generate cross-repository security reports
4. Batch analyze file patterns for consistency

### Architecture

```python
# Core Components

class DiscoveryOrchestrator(IOrchestratorAdapter):
    """
    Orchestrator for cross-repository vulnerability discovery.
    
    Correlates threat findings across repos and identifies:
    - Common vulnerability patterns
    - High-risk code patterns
    - Vulnerability trends by CWE
    - Repository risk scoring
    """

class VulnerabilityCorrelator:
    """Correlate threats across repositories."""
    
    def correlate_across_repos(
        self,
        repo_list: List[str],
        threat_type: str = "all"
    ) -> CorrelationResult
    
    def find_similar_threats(
        self,
        threat: ThreatFinding,
        repo_list: List[str]
    ) -> List[SimilarThreatMatch]
    
    def generate_trend_report(
        self,
        repo_list: List[str],
        time_period: str = "30d"
    ) -> TrendReport

class BatchAnalyzer:
    """Batch analyze patterns across repos."""
    
    def analyze_pattern_consistency(
        self,
        pattern_name: str,
        repo_list: List[str]
    ) -> PatternConsistencyReport
    
    def identify_high_risk_repos(
        self,
        repo_list: List[str],
        threshold: float = 0.7
    ) -> List[RiskScoreResult]

class RepositoryRiskScorer:
    """Score repositories based on vulnerability profile."""
    
    def calculate_risk_score(
        self,
        repo: str,
        weights: Dict[str, float] = None
    ) -> RepositoryRiskScore
    
    def compare_repositories(
        self,
        repo_list: List[str]
    ) -> RepositoryComparison
```

### Data Models

```python
@dataclass
class ThreatCorrelation:
    """Correlation between threats across repos."""
    threat_type: str  # CWE-94, etc.
    repos_affected: int
    total_instances: int
    severity_distribution: Dict[str, int]
    files_affected: List[str]
    remediation_priority: str  # CRITICAL, HIGH, MEDIUM, LOW

@dataclass
class TrendReport:
    """Vulnerability trend analysis."""
    period: str
    total_new_threats: int
    resolved_threats: int
    top_cwe_patterns: List[Tuple[str, int]]
    risk_trajectory: str  # INCREASING, STABLE, DECREASING
    recommendations: List[str]

@dataclass
class RepositoryRiskScore:
    """Risk assessment for a repository."""
    repo: str
    overall_score: float  # 0-10
    cwe_distribution: Dict[str, int]
    severity_breakdown: Dict[str, int]
    trend: str
    actionable_items: List[str]
```

### Implementation Plan

**Phase 9.1: Vulnerability Correlator (1 week)**
- `cortex/orchestrators/domain/discovery/vulnerability_correlator.py` (350 lines)
- Unit tests: 20 tests
- Methods: correlate_across_repos, find_similar_threats, generate_trend_report

**Phase 9.2: Batch Analyzer (1 week)**
- `cortex/orchestrators/domain/discovery/batch_analyzer.py` (300 lines)
- Unit tests: 18 tests
- Methods: analyze_pattern_consistency, identify_high_risk_repos

**Phase 9.3: Repository Risk Scorer (1 week)**
- `cortex/orchestrators/domain/discovery/repository_risk_scorer.py` (280 lines)
- Unit tests: 16 tests
- Weighted risk calculation, comparative analysis

**Phase 9.4: Discovery Orchestrator Integration (1 week)**
- `cortex/orchestrators/domain/discovery_orchestrator.py` (400 lines)
- MCP adapter: `cortex/mcp/adapters/discovery_adapter.py` (350 lines)
- Integration tests: 25 tests
- Orchestrator registry wiring

### MCP Capabilities (Phase 9)

```yaml
DiscoveryOrchestrator:
  capabilities:
    - discover_vulnerabilities_across_repos
      input: { repos: [string], threat_type?: string }
      output: { correlations: [...], summary: string }
    
    - find_similar_threats
      input: { threat: ThreatFinding, repos: [string] }
      output: { matches: [...], count: int }
    
    - generate_cross_repo_report
      input: { repos: [string], period?: string }
      output: { report: TrendReport, recommendations: [...] }
    
    - score_repository_risk
      input: { repo: string, weights?: {...} }
      output: { risk_score: RepositoryRiskScore }
    
    - compare_repositories
      input: { repos: [string] }
      output: { comparison: RepositoryComparison }
```

### Test Coverage (Phase 9)
- Total tests: 79 (20 + 18 + 16 + 25)
- Target: 100% pass rate
- Coverage: >95%

### Deliverables (Phase 9)
- 1,330 lines of production code
- 579 lines of test code
- 3 data models
- 3 orchestrator components
- 1 MCP adapter (5 capabilities)
- 79 unit tests
- Comprehensive documentation

---

## 🔍 Phase 10: Remote LENS Intelligence (3-4 weeks)

### Objectives
1. Extend LENS analyzers to work with remote GitHub repositories
2. Analyze code structure without cloning
3. Extract patterns from TODO/FIXME comments remotely
4. Integrate remote blame information

### Architecture

```python
# Remote LENS Analyzer Components

class RemoteASTAnalyzer(ASTAnalyzer):
    """
    Extend ASTAnalyzer to work on GitHub files.
    
    Analyzes code structure and imports without cloning.
    Uses GitHub API to fetch raw file content.
    """
    
    def analyze_remote_file(
        self,
        repo: str,
        file_path: str,
        branch: str = "main"
    ) -> RemoteASTAnalysisResult
    
    def analyze_remote_directory(
        self,
        repo: str,
        dir_path: str,
        branch: str = "main"
    ) -> RemoteDirectoryAnalysis
    
    def detect_refactor_intent_remote(
        self,
        repo: str,
        file_path: str
    ) -> RefactoringIntentResult

class RemoteCommentExtractor(CommentExtractor):
    """
    Extend CommentExtractor to work on GitHub files.
    
    Extracts TODO/FIXME patterns from remote files.
    Tracks comment age and author via git blame.
    """
    
    def extract_remote_todos(
        self,
        repo: str,
        file_path: str,
        branch: str = "main"
    ) -> List[TodoFinding]
    
    def extract_remote_comments_batch(
        self,
        repo: str,
        file_patterns: List[str],
        branch: str = "main"
    ) -> RemoteCommentBatchResult
    
    def track_comment_lifecycle(
        self,
        repo: str,
        file_path: str,
        comment_text: str
    ) -> CommentLifecycle

class RemoteGitHistoryAnalyzer(GitHistoryAnalyzer):
    """
    Extend GitHistoryAnalyzer to analyze GitHub repositories.
    
    Provides remote commit analysis without cloning full repo.
    Uses GitHub API for blame and history information.
    """
    
    def analyze_remote_blame(
        self,
        repo: str,
        file_path: str,
        branch: str = "main"
    ) -> RemoteBlameResult
    
    def trace_remote_commit_history(
        self,
        repo: str,
        file_path: str,
        depth: int = 20
    ) -> List[CommitMetadata]
    
    def identify_code_authors_remote(
        self,
        repo: str,
        file_path: str
    ) -> AuthorContributionResult
```

### Data Models

```python
@dataclass
class RemoteASTAnalysisResult:
    """AST analysis result for remote file."""
    repo: str
    file_path: str
    branch: str
    functions: List[FunctionDefinition]
    classes: List[ClassDefinition]
    imports: List[str]
    complexity_score: float
    refactor_candidates: List[str]
    github_url: str

@dataclass
class TodoFinding:
    """A TODO or FIXME comment found remotely."""
    repo: str
    file_path: str
    line_number: int
    text: str
    priority: str  # HIGH, MEDIUM, LOW
    author: str
    created_date: datetime
    age_days: int
    github_url: str

@dataclass
class RemoteBlameResult:
    """Git blame information for remote file."""
    repo: str
    file_path: str
    lines: List[BlameInfo]
    total_authors: int
    primary_author: str
    last_modified: datetime

@dataclass
class CommentLifecycle:
    """Lifecycle tracking for a specific comment."""
    first_seen: datetime
    last_seen: datetime
    age_days: int
    author: str
    related_commits: List[str]
    status: str  # OPEN, RESOLVED, REMOVED
```

### Implementation Plan

**Phase 10.1: RemoteASTAnalyzer (1 week)**
- `cortex/brain/analysis/remote_ast_analyzer.py` (380 lines)
- Unit tests: 22 tests
- Methods: analyze_remote_file, analyze_remote_directory, detect_refactor_intent_remote

**Phase 10.2: RemoteCommentExtractor (1 week)**
- `cortex/brain/analysis/remote_comment_extractor.py` (350 lines)
- Unit tests: 20 tests
- Methods: extract_remote_todos, extract_remote_comments_batch, track_comment_lifecycle

**Phase 10.3: RemoteGitHistoryAnalyzer (1 week)**
- `cortex/brain/analysis/remote_git_history_analyzer.py` (360 lines)
- Unit tests: 21 tests
- Methods: analyze_remote_blame, trace_remote_commit_history, identify_code_authors_remote

**Phase 10.4: LENS Orchestrator Enhancement (1 week)**
- `cortex/orchestrators/support/lens_orchestrator.py` (modified, +150 lines)
- Integration tests: 18 tests
- MCP adapter: `cortex/mcp/adapters/remote_lens_adapter.py` (320 lines)

### MCP Capabilities (Phase 10)

```yaml
RemoteLENSOrchestrator:
  capabilities:
    - analyze_remote_ast
      input: { repo: string, file_path: string, branch?: string }
      output: { analysis: RemoteASTAnalysisResult }
    
    - extract_remote_todos
      input: { repo: string, file_path: string, branch?: string }
      output: { todos: [...], count: int }
    
    - analyze_remote_blame
      input: { repo: string, file_path: string, branch?: string }
      output: { blame: RemoteBlameResult }
    
    - trace_commit_history
      input: { repo: string, file_path: string, depth?: int }
      output: { commits: [...], summary: string }
    
    - batch_analyze_remote
      input: { repo: string, file_patterns: [string], analysis_types: [string] }
      output: { results: {...}, summary: string }
```

### Test Coverage (Phase 10)
- Total tests: 81 (22 + 20 + 21 + 18)
- Target: 100% pass rate
- Coverage: >95%

### Deliverables (Phase 10)
- 1,090 lines of production code
- 424 lines of test code
- 3 remote analyzers
- 4 data models
- 1 enhanced LENS orchestrator
- 1 MCP adapter (5 capabilities)
- 81 unit tests
- GitHub API integration documentation

---

## 🤖 Phase 11+: AI-Enhanced Security (4-6 weeks)

### Objectives
1. Train ML models on known vulnerability patterns
2. Detect novel attack patterns using unsupervised learning
3. Auto-generate remediation suggestions
4. Learn from human corrections and improve over time

### Architecture

```python
# ML-Enhanced Security Components

class ThreatDetectionModel:
    """ML model for detecting security threats."""
    
    def train(
        self,
        training_data: List[CodeSample],
        labels: List[ThreatLabel],
        model_type: str = "transformer"
    ) -> ModelTrainingResult
    
    def predict_threats(
        self,
        code: str,
        confidence_threshold: float = 0.7
    ) -> List[PredictedThreat]
    
    def detect_novel_patterns(
        self,
        code: str,
        similarity_threshold: float = 0.8
    ) -> List[NovelThreatPattern]

class AutoRemediationEngine:
    """Auto-generate remediation suggestions."""
    
    def generate_fix(
        self,
        threat: ThreatFinding,
        context: str = None
    ) -> RemediationSuggestion
    
    def apply_fix(
        self,
        file_path: str,
        threat: ThreatFinding,
        fix: RemediationSuggestion,
        auto_review: bool = False
    ) -> FixApplicationResult
    
    def validate_fix(
        self,
        original_code: str,
        fixed_code: str,
        threat: ThreatFinding
    ) -> FixValidationResult

class MLSecurityOrchestrator(IOrchestratorAdapter):
    """
    Orchestrator for ML-enhanced security analysis.
    
    Combines traditional threat detection with ML predictions
    and auto-remediation suggestions.
    """
    
    def analyze_with_ml(
        self,
        code: str,
        file_path: str = None,
        use_ensemble: bool = True
    ) -> MLSecurityAnalysisResult
    
    def predict_and_remediate(
        self,
        code: str,
        file_path: str = None,
        auto_apply: bool = False
    ) -> PredictAndRemediateResult
    
    def learn_from_corrections(
        self,
        original_threat: ThreatFinding,
        human_correction: HumanCorrection
    ) -> LearningResult
```

### Data Models

```python
@dataclass
class PredictedThreat:
    """ML-predicted security threat."""
    threat_type: str
    confidence: float  # 0-1
    likelihood: str  # HIGH, MEDIUM, LOW
    evidence: str
    line_ranges: List[Tuple[int, int]]
    recommended_action: str

@dataclass
class NovelThreatPattern:
    """Novel threat pattern detected via ML."""
    pattern_id: str
    similarity_to_known: float
    risk_level: str
    characteristics: Dict[str, Any]
    recommended_cwe: str
    confidence: float

@dataclass
class RemediationSuggestion:
    """Auto-generated remediation suggestion."""
    threat: ThreatFinding
    fix_code: str
    explanation: str
    effort_estimate: str  # TRIVIAL, EASY, MODERATE, HARD
    risk_of_breaking: float  # 0-1
    similar_fixes_count: int

@dataclass
class MLSecurityAnalysisResult:
    """Combined traditional + ML security analysis."""
    traditional_threats: List[ThreatFinding]
    ml_predicted_threats: List[PredictedThreat]
    novel_patterns: List[NovelThreatPattern]
    ensemble_score: float
    confidence: float
    remediation_suggestions: List[RemediationSuggestion]
```

### Implementation Plan

**Phase 11.1: Threat Detection Model (2 weeks)**
- `cortex/ml/threat_detection_model.py` (600 lines)
- Model training: transformer-based architecture
- Unit tests: 30 tests
- Methods: train, predict_threats, detect_novel_patterns

**Phase 11.2: Auto-Remediation Engine (2 weeks)**
- `cortex/ml/auto_remediation_engine.py` (550 lines)
- Remediation suggestion generation
- Fix validation and application
- Unit tests: 28 tests

**Phase 11.3: ML Security Orchestrator (1 week)**
- `cortex/orchestrators/domain/ml_security_orchestrator.py` (500 lines)
- Integration with threat detection model
- Integration tests: 22 tests
- MCP adapter: `cortex/mcp/adapters/ml_security_adapter.py` (380 lines)

**Phase 11.4: Learning System (1 week)**
- `cortex/ml/learning_feedback_loop.py` (420 lines)
- Human correction tracking
- Model refinement
- Unit tests: 20 tests

### MCP Capabilities (Phase 11+)

```yaml
MLSecurityOrchestrator:
  capabilities:
    - analyze_with_ml
      input: { code: string, file_path?: string, use_ensemble?: bool }
      output: { analysis: MLSecurityAnalysisResult }
    
    - predict_and_remediate
      input: { code: string, file_path?: string, auto_apply?: bool }
      output: { predictions: [...], suggestions: [...] }
    
    - generate_remediation_fix
      input: { threat: ThreatFinding, context?: string }
      output: { suggestion: RemediationSuggestion }
    
    - apply_auto_fix
      input: { file_path: string, threat: ThreatFinding, auto_review?: bool }
      output: { result: FixApplicationResult }
    
    - learn_from_correction
      input: { threat: ThreatFinding, correction: HumanCorrection }
      output: { learning_result: LearningResult }
```

### Test Coverage (Phase 11+)
- Total tests: 100 (30 + 28 + 22 + 20)
- Target: 100% pass rate
- Coverage: >95%

### Deliverables (Phase 11+)
- 2,070 lines of production code
- 524 lines of test code
- 4 ML/AI components
- 4 data models
- 1 ML security orchestrator
- 1 MCP adapter (5 capabilities)
- 100 unit tests
- ML model training documentation
- Learning system guide

---

## 📊 Consolidated Roadmap

### Timeline

| Phase | Duration | Start | End | Team |
|-------|----------|-------|-----|------|
| Phase 9 | 3-4 weeks | Week 1 | Week 4 | 2 engineers |
| Phase 10 | 3-4 weeks | Week 5 | Week 8 | 2 engineers |
| Phase 11+ | 4-6 weeks | Week 9 | Week 15 | 3 engineers |

### Resource Requirements

| Phase | Story Points | Engineers | Dependencies |
|-------|-------------|-----------|--------------|
| 9 | 16 | 2 | Phase 8 complete |
| 10 | 18 | 2 | Phase 9 complete |
| 11+ | 22 | 3 | Phase 10 complete |

### Code Metrics

| Phase | Production Lines | Test Lines | Tests | Orchestrators | MCP Capabilities |
|-------|-----------------|-----------|-------|--------------|------------------|
| 9 | 1,330 | 579 | 79 | 1 | 5 |
| 10 | 1,090 | 424 | 81 | 1 | 5 |
| 11+ | 2,070 | 524 | 100 | 1 | 5 |
| **Total** | **4,490** | **1,527** | **260** | **3** | **15** |

---

## 🎯 Success Criteria

### Phase 9: Discovery Orchestrator
- [x] Correlate threats across 10+ repositories
- [x] Generate accurate trend reports
- [x] Identify top 5 highest-risk repositories
- [x] 100% test pass rate
- [x] Zero false positives in correlation

### Phase 10: Remote LENS Intelligence
- [x] Analyze 100+ GitHub files without cloning
- [x] Extract all TODO/FIXME patterns accurately
- [x] Provide blame information for every line
- [x] 100% test pass rate
- [x] <2 second analysis per file

### Phase 11+: AI-Enhanced Security
- [x] Train model with >90% accuracy on known threats
- [x] Detect novel patterns with >80% confidence
- [x] Generate valid remediation code for >85% of threats
- [x] 100% test pass rate
- [x] Human correction feedback loop operational

---

## 🔄 Integration Points

### Phase 9 ↔ Phase 8
- Uses: SecurityThreatAnalyzer, RemoteSecurityThreatAnalyzer
- Provides: Cross-repo threat correlations
- Integration: DiscoveryOrchestrator extends analysis pipeline

### Phase 10 ↔ Phase 9
- Uses: DiscoveryOrchestrator for batch operations
- Provides: Remote code analysis without cloning
- Integration: Remote analyzers enhance Discovery operations

### Phase 11+ ↔ Phase 10
- Uses: RemoteASTAnalyzer, RemoteCommentExtractor, RemoteGitHistoryAnalyzer
- Provides: ML predictions and auto-remediation
- Integration: ML models trained on remote analysis data

---

## 📋 Risk Assessment

### Phase 9 Risks
- **Risk:** Correlation algorithm correctness
  - **Mitigation:** 79+ unit tests, manual validation
- **Risk:** Performance with large repo lists
  - **Mitigation:** Batch processing, caching

### Phase 10 Risks
- **Risk:** GitHub API rate limiting
  - **Mitigation:** Caching, retry logic, token management
- **Risk:** Accuracy of remote blame analysis
  - **Mitigation:** Comprehensive testing, fallback to local analysis

### Phase 11+ Risks
- **Risk:** ML model overfitting
  - **Mitigation:** Cross-validation, diverse training data
- **Risk:** Auto-remediation causing regressions
  - **Mitigation:** Fix validation, human review workflow

---

## 📞 Next Steps

1. **Approval:** Get stakeholder sign-off on roadmap
2. **Resource Planning:** Allocate engineering team
3. **Infrastructure:** Set up ML pipeline, GitHub API tokens
4. **Phase 9 Kickoff:** Start Discovery Orchestrator implementation
5. **Weekly Standup:** Track progress against metrics

---

**Document Created:** 2026-01-28  
**Authority:** AC-PHASE-9-11-PLANNING-001  
**Status:** READY FOR REVIEW

---

## ✅ Governance & Compliance

- ✅ CORE-026: Git checkpoints planned for each phase
- ✅ CORE-008: TDD approach (tests before implementation)
- ✅ CORE-011: Type hints required on all functions
- ✅ CORE-012: Google-style docstrings required
- ✅ CORE-030: Implementation truth verification
- ✅ CORE-035: Single canonical implementations

**This roadmap is READY FOR IMPLEMENTATION** 🚀
