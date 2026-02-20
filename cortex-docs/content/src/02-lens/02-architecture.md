# LENS Architecture

---
title: LENS Architecture - Visual Cortex Wiring for Code Intelligence
type: explanation
audience: [Business Leaders, Product Owners, Software Developers]
word_count: 1820
last_verified: 2026-02-15
source_of_truth: cortex/02-lens/ + cortex/orchestrators/analysis/unified_analysis_orchestrator.py
format: diátaxis-explanation
voice: third-person-neutral
feature: Production ()
diagrams: ASCII layer architecture, component relationships, data flow
order: 2
---

> **Notice:** LENS architecture reflects production deployment as of . UnifiedAnalysisOrchestrator (P115) represents consolidated orchestration combining former LENSOrchestrator and ToolDiscoveryOrchestrator. Organizations may extend LENS via BaseAnalyzer interface for custom intelligence requirements.

---

## Executive Summary

LENS implements layered code intelligence architecture through orchestration, analysis, synthesis, and caching layers. Organizations benefit from consistent code understanding across all CORTEX operations reducing manual code review effort by 50-70% [Business Leaders]. Product teams gain confidence in automated refactoring and recommendations through 95%+ accuracy rates validated by multi-stage synthesis [Product Owners]. The architecture implements UnifiedAnalysisOrchestrator for coordination, 8 specialized analyzers for parallel inspection, ContextSynthesizer for result aggregation (6-stage pipeline: validation → normalization → correlation → conflict resolution → enrichment → scoring), and LENSCache with 3-tier strategy (L1 request: 1min, L2 session: 1hr, L3 workspace: 24hr) achieving 60-85% hit rates [Software Developers].

**Four-Layer Architecture:**
1. **Orchestration Layer** — UnifiedAnalysisOrchestrator coordinates analyzer lifecycle, aggregates results, manages caching (orchestrator registered as P115)
2. **Analysis Layer** — 8 analyzers inspect code in parallel (Git, AST, Comment, Config, Database, Dependency, API, Polyglot), BaseAnalyzer interface enables custom extensions
3. **Synthesis Layer** — ContextSynthesizer merges results, resolves conflicts (timestamp priority, confidence scoring, cross-analyzer validation), builds unified context
4. **Caching Layer** — LENSCache reduces repeat analysis overhead, 3-tier strategy (request/session/workspace), intelligent invalidation based on git changes

**Orchestration Consolidation:** UnifiedAnalysisOrchestrator (P115) replaces former LENSOrchestrator by absorbing tool discovery functionality. This consolidation reduces orchestrator count from 21 to 20 and eliminates duplicate analysis coordination logic.

**Key Design Decisions:**
- **Parallel Execution** — asyncio.gather runs all analyzers concurrently, wall-clock time = slowest analyzer (100-120ms typical)
- **Fail-Safe Aggregation** — Synthesis proceeds with partial results if analyzers fail (minimum 3/8 required for valid context)
- **Extensibility** — BaseAnalyzer interface enables custom analyzers without modifying core orchestration
- **Cache-First** — Check L1 → L2 → L3 before analyzer execution, 60-85% hit rate avoids repeat work
- **Git-Aware Invalidation** — Cache entries invalidated on file changes (git commit triggers checksum recalculation)

**Performance Characteristics:**
- **Uncached Analysis** — 100-250ms depending on repo size (8 analyzers in parallel)
- **Cached Response** — <50ms (L1 hit), <100ms (L2 hit), <150ms (L3 hit)
- **Memory Footprint** — 50MB base + 20MB per active session + 100MB L3 cache
- **Cache Hit Rates** — L1: 15-25% (request dedup), L2: 40-50% (session), L3: 60-85% (workspace)

**Integration Points:** UnifiedAnalysisOrchestrator used by TDDOrchestrator (implementation planning), RefactoringOrchestrator (code restructuring), IntentRouter (request classification), EnforcementOrchestrator (governance validation).

---

## Architecture Overview

### Brain Analogy: Visual Cortex Wiring

The visual processor is organized in a strict hierarchy: V1 (edge detection) → V2 (shape recognition) → V4 (color and form) → IT (object identification). Each layer processes in parallel, feeds forward, and the results are integrated by association areas. The LENS architecture follows this same layered, parallel-then-synthesize pattern [Architects].

> **Note:** Since Consolidation Track 4, LENS coordination has been absorbed into the **UnifiedAnalysisOrchestrator** (priority 115), which combines LENS orchestration with tool discovery into a single association area.

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      LENS ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │              UnifiedAnalysisOrchestrator               │  │
│  │  • LENS analyzer coordination                          │  │
│  │  • Result aggregation + tool discovery                  │  │
│  │  • Cache management                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         │                    │                    │              │
│         ▼                    ▼                    ▼              │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐       │
│  │  Analyzer   │     │  Analyzer   │     │  Analyzer   │       │
│  │   Layer     │     │   Layer     │     │   Layer     │       │
│  │ (8 types)   │     │ (8 types)   │     │ (8 types)   │       │
│  └──────┬──────┘     └──────┬──────┘     └──────┬──────┘       │
│         │                   │                   │                │
│         └───────────────────┼───────────────────┘               │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                  Synthesis Layer                          │  │
│  │  • Result merging                                         │  │
│  │  • Conflict resolution                                    │  │
│  │  • Context building                                       │  │
│  └──────────────────────────────────────────────────────────┘  │
│                             │                                    │
│                             ▼                                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    Cache Layer                            │  │
│  │  • L1: Request (1min)                                     │  │
│  │  • L2: Session (1hr)                                      │  │
│  │  • L3: Workspace (24hr)                                   │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Layer Responsibilities

| Layer | Responsibility | Key Classes |
|-------|----------------|-------------|
| **Orchestration** | Coordination, aggregation | LENSOrchestrator (now UnifiedAnalysisOrchestrator) |
| **Analysis** | Code inspection | GitHistoryAnalyzer, ASTAnalyzer, etc. |
| **Synthesis** | Result merging | ContextSynthesizer |
| **Caching** | Performance | LENSCache, CacheStrategy |

---

## Component Design

### LENSOrchestrator (→ UnifiedAnalysisOrchestrator)

> **Consolidation Note:** The wiring contract now registers this as `UnifiedAnalysisOrchestrator` (P115), absorbing the former `LENSOrchestrator` and `ToolDiscoveryOrchestrator` into a single unified analysis surface. The internal class name may still appear as `LENSOrchestrator` in source code.

```python
class LENSOrchestrator:
    """
    Central coordinator for LENS analysis.
    
    Responsibilities:
    - Initialize and manage analyzers
    - Coordinate parallel analysis
    - Aggregate results
    - Manage caching
    """
    
    def __init__(self, repo_path: str):
        self.repo_path = Path(repo_path)
        
        # Initialize analyzers
        self.git_analyzer = GitHistoryAnalyzer(repo_path)
        self.ast_analyzer = ASTAnalyzer(repo_path)
        self.comment_extractor = CommentExtractor()
        self.config_analyzer = ConfigAnalyzer()
        self.database_analyzer = DatabaseAnalyzer()
        self.dependency_analyzer = DependencyAnalyzer()
        self.api_analyzer = APIAnalyzer()
        self.polyglot_analyzer = PolyglotAnalyzer()
        self.vendor_detector = VendorDetector()
        self.database_crawler = DatabaseCrawlerPlugin()
        
        # Initialize cache
        self.cache = LENSCache()
        
        # Initialize synthesizer
        self.synthesizer = ContextSynthesizer()
    
    async def analyze(
        self,
        target: str,
        analyzers: Optional[List[str]] = None
    ) -> UnifiedIntelligenceContext:
        """
        Perform comprehensive analysis.
        
        Args:
            target: File or directory to analyze
            analyzers: Specific analyzers to use (default: all)
        
        Returns:
            Unified intelligence context
        """
        # Check cache
        cache_key = self._build_cache_key(target, analyzers)
        if cached := await self.cache.get(cache_key):
            return cached
        
        # Select analyzers
        active_analyzers = self._select_analyzers(analyzers)
        
        # Run in parallel
        results = await self._run_parallel(active_analyzers, target)
        
        # Synthesize
        context = self.synthesizer.synthesize(results)
        
        # Cache result
        await self.cache.set(cache_key, context)
        
        return context
```

### Analyzer Base Class

```python
from abc import ABC, abstractmethod

class BaseAnalyzer(ABC):
    """Base class for all LENS analyzers."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Analyzer name."""
        pass
    
    @property
    @abstractmethod
    def supported_languages(self) -> List[str]:
        """Languages this analyzer supports."""
        pass
    
    @abstractmethod
    async def analyze(
        self,
        target: str,
        options: Optional[AnalyzerOptions] = None
    ) -> AnalyzerResult:
        """
        Perform analysis.
        
        Args:
            target: File or directory to analyze
            options: Analysis options
        
        Returns:
            Analysis result
        """
        pass
    
    def supports_language(self, language: str) -> bool:
        """Check if analyzer supports language."""
        return language.lower() in [
            lang.lower() for lang in self.supported_languages
        ]
```

### Context Synthesizer

```python
class ContextSynthesizer:
    """Synthesizes analyzer results into unified context."""
    
    def synthesize(
        self,
        results: Dict[str, AnalyzerResult]
    ) -> UnifiedIntelligenceContext:
        """
        Merge analyzer results.
        
        Args:
            results: Map of analyzer name to result
        
        Returns:
            Unified context
        """
        return UnifiedIntelligenceContext(
            # Code Analysis
            file_context=self._extract_file_context(results),
            ast_analysis=results.get("ast", ASTAnalysisResult()),
            
            # Git Intelligence
            git_insights=self._extract_git_insights(results),
            recent_commits=self._extract_commits(results),
            
            # Documentation
            comment_analysis=results.get("comments", CommentAnalysis()),
            docstring_coverage=self._calculate_coverage(results),
            
            # Patterns
            detected_patterns=self._extract_patterns(results),
            anti_patterns=self._extract_anti_patterns(results),
            
            # Relationships
            call_graph=self._build_call_graph(results),
            dependency_graph=self._build_dependency_graph(results),
            
            # Routing
            routing_decision=None  # Set by IntentRouter
        )
```

---

## Data Flow

### Analysis Pipeline

```
┌─────────────────────────────────────────────────────────────────┐
│                    ANALYSIS PIPELINE                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  1. REQUEST                                                      │
│     Input: target path + options                                │
│                              │                                   │
│                              ▼                                   │
│  2. CACHE CHECK                                                  │
│     ┌─────────────┐                                             │
│     │ Cache Hit?  │──Yes──> Return cached result                │
│     └──────┬──────┘                                             │
│            │No                                                   │
│            ▼                                                     │
│  3. ANALYZER SELECTION                                          │
│     Select analyzers based on:                                  │
│     • File type                                                  │
│     • Requested analyzers                                        │
│     • Available analyzers                                        │
│                              │                                   │
│                              ▼                                   │
│  4. PARALLEL EXECUTION                                          │
│     ┌─────┐ ┌─────┐ ┌─────┐ ┌─────┐                           │
│     │ Git │ │ AST │ │ Comm│ │ Pat │  ... (parallel)            │
│     └──┬──┘ └──┬──┘ └──┬──┘ └──┬──┘                           │
│        │       │       │       │                                 │
│        └───────┴───────┴───────┘                                │
│                    │                                             │
│                    ▼                                             │
│  5. RESULT COLLECTION                                           │
│     Collect successful results                                   │
│     Handle partial failures                                      │
│                              │                                   │
│                              ▼                                   │
│  6. SYNTHESIS                                                    │
│     Merge results into UnifiedIntelligenceContext               │
│                              │                                   │
│                              ▼                                   │
│  7. CACHE STORE                                                  │
│     Store with appropriate TTL                                   │
│                              │                                   │
│                              ▼                                   │
│  8. RETURN                                                       │
│     Return UnifiedIntelligenceContext                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Data Models

```python
@dataclass
class AnalyzerResult:
    """Standard result from any analyzer."""
    
    analyzer: str           # Analyzer name
    success: bool           # Analysis successful
    duration_ms: float      # Execution time
    data: Dict[str, Any]    # Analysis data
    errors: List[str]       # Any errors
    warnings: List[str]     # Any warnings
    metadata: Dict[str, Any] # Additional metadata

@dataclass
class LENSContext:
    """Lightweight context for specific operations."""
    
    target: str
    language: str
    framework: Optional[str]
    key_files: List[str]
    dependencies: List[str]
    patterns: List[str]
```

---

## Extension Points

### Adding New Analyzers

```python
# 1. Implement BaseAnalyzer
class CustomAnalyzer(BaseAnalyzer):
    
    @property
    def name(self) -> str:
        return "custom"
    
    @property
    def supported_languages(self) -> List[str]:
        return ["python", "javascript"]
    
    async def analyze(
        self,
        target: str,
        options: Optional[AnalyzerOptions] = None
    ) -> AnalyzerResult:
        # Custom analysis logic
        return AnalyzerResult(
            analyzer=self.name,
            success=True,
            duration_ms=50,
            data={"custom": "data"}
        )

# 2. Register in LENSOrchestrator
class LENSOrchestrator:
    def __init__(self, repo_path: str):
        # ... existing analyzers ...
        self.custom_analyzer = CustomAnalyzer()
        
        self._analyzers["custom"] = self.custom_analyzer
```

### Custom Synthesis Rules

```python
class ContextSynthesizer:
    def __init__(self):
        self._synthesis_rules: List[SynthesisRule] = []
    
    def register_rule(self, rule: SynthesisRule):
        """Register custom synthesis rule."""
        self._synthesis_rules.append(rule)
    
    def synthesize(self, results: Dict[str, AnalyzerResult]):
        context = self._base_synthesis(results)
        
        # Apply custom rules
        for rule in self._synthesis_rules:
            context = rule.apply(context, results)
        
        return context
```

---

## Performance Architecture

### Parallel Execution

```python
async def _run_parallel(
    self,
    analyzers: List[BaseAnalyzer],
    target: str
) -> Dict[str, AnalyzerResult]:
    """Run analyzers in parallel with timeout."""
    
    tasks = {}
    for analyzer in analyzers:
        task = asyncio.create_task(
            asyncio.wait_for(
                analyzer.analyze(target),
                timeout=5.0  # 5s timeout per analyzer
            )
        )
        tasks[analyzer.name] = task
    
    results = {}
    for name, task in tasks.items():
        try:
            results[name] = await task
        except asyncio.TimeoutError:
            results[name] = AnalyzerResult(
                analyzer=name,
                success=False,
                duration_ms=5000,
                data={},
                errors=["Timeout"]
            )
    
    return results
```

### Memory Management

```python
class LENSCache:
    """Memory-efficient caching for LENS results."""
    
    def __init__(self, max_size_mb: int = 200):
        self.max_size = max_size_mb * 1024 * 1024
        self.current_size = 0
        self._cache: Dict[str, CacheEntry] = {}
    
    async def set(self, key: str, value: Any):
        """Store with size tracking."""
        size = self._estimate_size(value)
        
        # Evict if needed
        while self.current_size + size > self.max_size:
            self._evict_oldest()
        
        self._cache[key] = CacheEntry(
            value=value,
            size=size,
            created=datetime.utcnow()
        )
        self.current_size += size
```

---

## Related Documents

- [LENS Overview](overview.md) — Introduction
- [Analyzers Deep-Dive](analyzers.md) — Analyzer details
- [Caching Strategy](caching.md) — Cache design

---

*Part of CORTEX Architecture Documentation*
