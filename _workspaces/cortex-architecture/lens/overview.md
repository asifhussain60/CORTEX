# LENS Overview

**Purpose:** Introduction to the LENS intelligence layer  
**Audience:** All Technical Stakeholders  
**Last Updated:** 2026-02-10

---

## Table of Contents

- [What is LENS?](#what-is-lens)
- [The LENS Acronym](#the-lens-acronym)
- [Core Value Proposition](#core-value-proposition)
- [Key Capabilities](#key-capabilities)
- [Integration Points](#integration-points)
- [Related Documents](#related-documents)

---

## What is LENS?

**LENS** is CORTEX's unified code intelligence layer that provides deep understanding of codebases through multi-dimensional analysis. It combines static analysis, runtime correlation, and knowledge synthesis to provide contextual intelligence for all CORTEX operations.

```
┌─────────────────────────────────────────────────────────────────┐
│                         LENS                                     │
│        Language → Examination → Navigation → Synthesis           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│    ┌─────────────┐  ┌─────────────┐  ┌─────────────┐           │
│    │   Static    │  │   Runtime   │  │  Knowledge  │           │
│    │  Analysis   │  │ Correlation │  │  Synthesis  │           │
│    └──────┬──────┘  └──────┬──────┘  └──────┬──────┘           │
│           │                │                │                    │
│           └────────────────┼────────────────┘                   │
│                            ▼                                     │
│                   ┌─────────────────┐                           │
│                   │   Unified       │                           │
│                   │   Intelligence  │                           │
│                   │   Context       │                           │
│                   └─────────────────┘                           │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## The LENS Acronym

### L - Language

Understanding code structure and semantics across multiple programming languages.

| Capability | Description |
|------------|-------------|
| **Syntax Analysis** | Parse code into AST |
| **Semantic Understanding** | Understand meaning |
| **Multi-Language** | Python, TypeScript, Java, etc. |
| **Pattern Recognition** | Identify idioms |

### E - Examination

Deep inspection of code quality, patterns, and potential issues.

| Capability | Description |
|------------|-------------|
| **Code Smell Detection** | Anti-pattern identification |
| **Vulnerability Scanning** | Security issue detection |
| **Duplication Detection** | CORE-035 compliance |
| **Quality Metrics** | Cyclomatic complexity, etc. |

### N - Navigation

Understanding code relationships and navigation paths.

| Capability | Description |
|------------|-------------|
| **Call Graph** | Function relationships |
| **Dependency Graph** | Module dependencies |
| **Import Analysis** | Import chains |
| **Reference Tracking** | Symbol usage |

### S - Synthesis

Combining insights into actionable intelligence.

| Capability | Description |
|------------|-------------|
| **Context Building** | Unified context |
| **Insight Generation** | Actionable recommendations |
| **Knowledge Integration** | Domain knowledge merge |
| **Caching** | Performance optimization |

---

## Core Value Proposition

### Before LENS

```
Developer Request: "Fix the authentication bug"
                         ↓
        ┌────────────────────────────────────┐
        │  AI Model receives raw request     │
        │  No context about:                 │
        │  • Authentication implementation   │
        │  • Recent changes                  │
        │  • Related components              │
        │  • Team conventions                │
        └────────────────────────────────────┘
                         ↓
        Result: Generic, possibly incorrect fix
```

### With LENS

```
Developer Request: "Fix the authentication bug"
                         ↓
        ┌────────────────────────────────────┐
        │           LENS Analysis            │
        │  ✓ Auth code in auth/service.py   │
        │  ✓ Recent commit: "Add JWT"       │
        │  ✓ Related: middleware, tests     │
        │  ✓ Convention: async handlers     │
        └────────────────────────────────────┘
                         ↓
        Result: Precise, contextual fix
```

---

## Key Capabilities

### 1. Multi-Analyzer Architecture

LENS employs 8 specialized analyzers:

| Analyzer | Purpose | Output |
|----------|---------|--------|
| **GitHistoryAnalyzer** | Recent changes (24h) | Commits, diffs, blame |
| **ASTAnalyzer** | Code structure | Classes, functions, types |
| **CommentExtractor** | Documentation | TODOs, docstrings |
| **VisionAnalyzer** | UI/diagram analysis | Visual patterns |
| **ConfigAnalyzer** | Configuration | Settings, env vars |
| **DatabaseAnalyzer** | Schema analysis | Tables, relationships |
| **APIAnalyzer** | API endpoints | Routes, contracts |
| **PatternAnalyzer** | Design patterns | Architectural patterns |

### 2. Unified Intelligence Context

All analyzer outputs merge into a single context object:

```python
@dataclass
class UnifiedIntelligenceContext:
    """Complete intelligence context for operations."""
    
    # Code Analysis
    file_context: FileAnalysisResult
    ast_analysis: ASTAnalysisResult
    
    # Git Intelligence
    git_insights: GitInsights
    recent_commits: List[CommitInfo]
    
    # Documentation
    comment_analysis: CommentAnalysis
    docstring_coverage: float
    
    # Patterns
    detected_patterns: List[DesignPattern]
    anti_patterns: List[AntiPattern]
    
    # Relationships
    call_graph: CallGraph
    dependency_graph: DependencyGraph
    
    # Routing
    routing_decision: RoutingDecision
```

### 3. Intelligent Caching

LENS caches analysis results for performance:

| Cache Layer | TTL | Hit Rate Target |
|-------------|-----|-----------------|
| L1: Request | 1min | 95% |
| L2: Session | 1hr | 80% |
| L3: Workspace | 24hr | 70% |

### 4. Polyglot Support

LENS supports multiple languages through unified abstractions:

```
┌─────────────────────────────────────────────────────────────────┐
│                    POLYGLOT ANALYSIS                             │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────┐  ┌──────────┐  ┌──────┐  ┌──────┐  ┌──────┐      │
│  │ Python  │  │TypeScript│  │ Java │  │  C#  │  │  Go  │      │
│  └────┬────┘  └────┬─────┘  └──┬───┘  └──┬───┘  └──┬───┘      │
│       │            │           │         │         │            │
│       └────────────┴───────────┴─────────┴─────────┘            │
│                            │                                     │
│                            ▼                                     │
│              ┌─────────────────────────┐                        │
│              │   Unified AST Model     │                        │
│              └─────────────────────────┘                        │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Integration Points

### With Orchestrators

```python
# MasterOrchestrator integration
async def enrich_request(self, request: Request) -> EnrichedRequest:
    lens = LENSOrchestrator()
    context = await lens.analyze(request.target_files)
    return EnrichedRequest(request=request, context=context)
```

### With Governance

```python
# Governance validation with LENS
async def validate_with_context(
    self,
    request: Request,
    lens_context: UnifiedIntelligenceContext
) -> ValidationResult:
    # Use LENS context for smarter validation
    if lens_context.anti_patterns:
        return ValidationResult(
            passed=False,
            reason="Anti-patterns detected"
        )
```

### With MCP Tools

```python
# MCP tool exposure
LENS_MCP_TOOLS = [
    "cortex_lens_analyze",      # Full analysis
    "cortex_ast_analyze",       # AST only
    "cortex_git_history",       # Git only
    "cortex_detect_duplicates", # Duplication
]
```

---

## Performance Characteristics

| Metric | Target | Typical |
|--------|--------|---------|
| **Full Analysis** | < 500ms | 300ms |
| **Cached Analysis** | < 50ms | 30ms |
| **Single Analyzer** | < 100ms | 60ms |
| **Memory Usage** | < 200MB | 150MB |

---

## Related Documents

- [LENS Architecture](architecture.md) — Technical design
- [Analyzers Deep-Dive](analyzers.md) — Analyzer details
- [AI Intelligence Capabilities](../capabilities/ai-intelligence.md) — AI overview

---

*Part of CORTEX Architecture Documentation*
