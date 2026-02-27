# LENS Analyzers

---
title: LENS Analyzers — 15 Specialized Code Intelligence Components
type: reference
audience: [Software Developers]
last_verified: 2026-02-27
source_of_truth: cortex/lens/analyzers/
order: 3
---

## Analyzer Details

### 1. AST Analyzer
**What it does:** Parses source code into Abstract Syntax Trees. Extracts classes, functions, decorators, imports, type annotations, and structural patterns.

**Output:** Symbol table, class hierarchy, function signatures, decorator usage.

**Use case:** Understanding code structure before refactoring. Identifying functions missing type hints (CORE-011).

### 2. Git History Analyzer
**What it does:** Analyzes git log for change patterns — which files change most, who changes them, when, and in what combinations.

**Output:** Change heatmap, author attribution, co-change patterns, recent modification list.

**Use case:** Identifying hot spots before a refactor. Detecting areas of high churn that need attention.

### 3. Comment Analyzer
**What it does:** Evaluates documentation quality — docstring coverage, TODO/FIXME density, comment-to-code ratio.

**Output:** Documentation score, gap list, TODO inventory.

**Use case:** Ensuring CORE-012 compliance (docstrings on all public APIs).

### 4. Import Analyzer
**What it does:** Maps the dependency graph — circular imports, stale imports, import depth, external dependencies.

**Output:** Dependency graph, circular chain list, stale import list.

**Use case:** Detecting circular dependencies before they cause runtime issues. Import quarantine.

### 5. Security Analyzer
**What it does:** Scans for known vulnerability patterns — SQL injection, XSS, credential exposure, hardcoded secrets.

**Output:** Finding list with severity (Critical/High/Medium/Low), line numbers, remediation suggestions.

**Use case:** Pre-commit security gate. Ensuring CORE-013 compliance.

### 6. Pattern Analyzer
**What it does:** Matches source code against known architecture patterns — framework signatures, design pattern usage, enterprise patterns.

**Output:** Pattern match list with confidence scores. Maps to 9 enterprise patterns in `cortex-registry/patterns/`.

**Use case:** Feeding the Perception tier. Understanding architecture style for strategy selection.

### 7. Metrics Analyzer
**What it does:** Computes code quality metrics — cyclomatic complexity, coupling, lines of code, maintainability index.

**Output:** Metric dashboard with per-function and per-module scores.

**Use case:** Identifying refactoring candidates. Setting quality thresholds.

### 8. Domain Analyzer
**What it does:** Detects business domain context — industry (finance, healthcare, ecommerce), regulatory requirements, domain-specific patterns.

**Output:** Domain classification with confidence. Regulatory context flags.

**Use case:** Routing to the correct domain orchestrator (Financial, Healthcare, Ecommerce).

---

*Verified against `cortex/lens/analyzers/`*
