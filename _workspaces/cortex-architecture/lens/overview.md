# LENS Intelligence Overview

**L**anguage **E**xamination **N**avigation **S**ynthesis  
**Updated:** 2026-02-11 | **Version:** 2.0.0

---

## What is LENS?

LENS is CORTEX's **sensory and analysis system** — like the visual cortex of a brain, it observes, analyzes, and synthesizes information about codebases.

### Four-Stage Intelligence Pipeline

```
┌────────────────────────────────────────────────────────────┐
│  L - LANGUAGE: Parse & Understand Code Structure          │
│     • AST parsing (Python, JS, TS, Java, C#, etc.)       │
│     • Syntax tree traversal                              │
│     • Token analysis                                     │
└────────────┬───────────────────────────────────────────────┘
             │
┌────────────▼───────────────────────────────────────────────┐
│  E - EXAMINATION: Deep Analysis                           │
│     • Security vulnerabilities (OWASP Top 10)            │
│     • Complexity metrics (cyclomatic, cognitive)         │
│     • Code smells & anti-patterns                        │
│     • Dependency analysis                                │
└────────────┬───────────────────────────────────────────────┘
             │
┌────────────▼───────────────────────────────────────────────┐
│  N - NAVIGATION: Context & History                        │
│     • Git history (24-hour window)                       │
│     • Commit patterns                                    │
│     • Author activity                                    │
│     • File relationships                                 │
└────────────┬───────────────────────────────────────────────┘
             │
┌────────────▼───────────────────────────────────────────────┐
│  S - SYNTHESIS: Intelligent Insights                      │
│     • Risk scoring                                       │
│     • Recommendation generation                          │
│     • Pattern detection                                  │
│     • Holistic assessment                                │
└────────────────────────────────────────────────────────────┘
```

---

## LENS Analyzers

CORTEX includes multiple specialized analyzers for comprehensive code intelligence.

### 1. Security Analyzer

**Purpose:** Identify security vulnerabilities and compliance issues

**Capabilities:**
- OWASP Top 10 Detection (SQL Injection, XSS, CSRF, etc.)
- Secret Detection (hardcoded passwords, API keys)
- Dependency Vulnerabilities (CVEs, outdated libraries)

**MCP Tools:** `cortex_lens_analyze(analysis_type="security")`

### 2. Complexity Analyzer

**Purpose:** Measure code complexity and maintainability

**Metrics:**
- Cyclomatic Complexity (control flow branches)
- Cognitive Complexity (human understanding)
- Halstead Metrics (vocabulary/length)
- Maintainability Index

### 3. Architecture Analyzer

**Purpose:** Understand architectural patterns and structure

**Capabilities:**
- Pattern Detection (MVC, Repository, Factory, etc.)
- Layer Analysis (presentation, business, data)
- Dependency Mapping (import graphs, circular dependencies)

### 4. Git History Analyzer

**Purpose:** Analyze code evolution and commit patterns

**Window:** 24-hour context (configurable)

**Insights:**
- Churn Analysis (frequently changed files)
- Author Patterns (code ownership)
- Commit Quality (message quality, test coverage)
- Risk Assessment (recently modified + complex = high risk)

### 5. Comment & Documentation Analyzer

**Purpose:** Extract and analyze code comments

**Features:**
- TODO/FIXME Detection
- Docstring Extraction (Google, NumPy, Sphinx)
- Comment Quality Assessment
- Documentation Coverage

### 6. Duplicate Code Detector

**Purpose:** Identify code duplication (CORE-035)

**Algorithms:**
- Token-based matching (fast, syntax-aware)
- AST similarity (structural comparison)
- Semantic similarity (ML-powered)

---

## LENS Performance

| Analyzer | Small (<100 LOC) | Medium (100-500) | Large (500+) |
|----------|------------------|------------------|--------------|
| Security | ~50ms | ~150ms | ~400ms |
| Complexity | ~30ms | ~80ms | ~200ms |
| Architecture | ~40ms | ~120ms | ~350ms |
| Git History | ~100ms | ~100ms | ~100ms |
| Comments | ~20ms | ~60ms | ~150ms |
| Duplicates | ~200ms | ~800ms | ~2s |

---

## LENS via MCP

| Tool | Purpose |
|------|---------|
| `cortex_lens_analyze` | Primary analysis entry point |
| `cortex_lens_deep_analyze` | Multi-analyzer scan |
| `cortex_ast_analyze` | AST-specific analysis |
| `cortex_git_history` | Git context analysis |
| `cortex_extract_comments` | Comment extraction |
| `cortex_detect_duplicates` | Duplication detection |

---

**Last Updated:** 2026-02-11 06:41:55  
**LENS Version:** 2.0.0  
**Analyzers:** 6 active
