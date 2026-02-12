# LENS Architecture

**Purpose:** Technical architecture of the LENS intelligence layer  
**Audience:** Architects, Senior Developers  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [Architecture Overview](#architecture-overview)
- [Component Design](#component-design)
- [Data Flow](#data-flow)
- [Extension Points](#extension-points)
- [Performance Architecture](#performance-architecture)
- [Related Documents](#related-documents)

---

## Architecture Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      LENS ARCHITECTURE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    LENSOrchestrator                       │  │
│  │  • Analyzer coordination                                  │  │
│  │  • Result aggregation                                     │  │
│  │  • Cache management                                       │  │
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
| **Orchestration** | Coordination, aggregation | LENSOrchestrator |
| **Analysis** | Code inspection | GitHistoryAnalyzer, ASTAnalyzer, etc. |
| **Synthesis** | Result merging | ContextSynthesizer |
| **Caching** | Performance | LENSCache, CacheStrategy |

---

## Component Design

### LENSOrchestrator

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
        self.vision_analyzer = VisionAnalyzer()
        self.config_analyzer = ConfigAnalyzer()
        self.database_analyzer = DatabaseAnalyzer()
        self.api_analyzer = APIAnalyzer()
        self.pattern_analyzer = PatternAnalyzer()
        
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
