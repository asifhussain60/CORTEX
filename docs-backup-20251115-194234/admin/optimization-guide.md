# CORTEX Optimization Guide

**Audience:** CORTEX administrators and maintainers  
**Purpose:** Comprehensive guide to analyzing and optimizing the CORTEX codebase  
**Tools:** Standard Python tools (radon, pylint, vulture) + CORTEX-specific optimizer  
**Status:** Production Ready

---

## Table of Contents

1. [Overview](#overview)
2. [Tool Ecosystem](#tool-ecosystem)
3. [Standard Tools Usage](#standard-tools-usage)
4. [CORTEX Optimizer](#cortex-optimizer)
5. [Pre-Commit Integration](#pre-commit-integration)
6. [Interpreting Results](#interpreting-results)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)

---

## Overview

CORTEX uses a **dual-layer optimization approach**:

1. **Standard Python Tools** - Generic code quality metrics (complexity, style, dead code)
2. **CORTEX Optimizer** - Domain-specific analysis (tokens, YAML, plugins, DB)

**Why both?**
- Standard tools handle universal Python best practices
- Custom tool handles CORTEX-specific architecture concerns (token usage, brain file validation, plugin health)

**Location:** `scripts/admin/` (NOT packaged for deployment)

---

## Tool Ecosystem

### Standard Tools (Generic Python)

| Tool | Purpose | When to Use |
|------|---------|-------------|
| **radon** | Complexity metrics (cyclomatic, maintainability) | Before refactoring, code reviews |
| **pylint** | Comprehensive code quality analysis | Pre-commit, CI/CD pipeline |
| **vulture** | Dead code detection (unused functions, imports) | Quarterly cleanup, before releases |
| **black** | Code formatting (consistent style) | Pre-commit (automatic) |
| **mypy** | Static type checking | Development, pre-commit |

### CORTEX Optimizer (Domain-Specific)

| Analyzer | Purpose | What It Checks |
|----------|---------|----------------|
| **TokenAnalyzer** | Prompt efficiency | Prompt file sizes, YAML token usage, modular doc efficiency |
| **YAMLValidator** | Brain file integrity | Schema compliance, required fields, parse errors |
| **PluginHealthChecker** | Plugin system health | Metadata completeness, registration, BasePlugin inheritance |
| **ConversationDBOptimizer** | SQLite performance | Indexes, fragmentation, size, query optimization |

---

## Standard Tools Usage

### Installation

Already installed via `requirements.txt`:

```bash
pip install -r requirements.txt
```

### Radon - Complexity Metrics

**Purpose:** Identify overly complex functions that need refactoring.

```bash
# Check complexity of entire codebase
radon cc src/ -a -s

# Focus on specific module
radon cc src/tier1/ --min B

# Maintainability index
radon mi src/ -s
```

**Interpreting Radon Output:**

```
A - Simple (1-5)       ✅ Good
B - Moderate (6-10)    ⚠️ Watch
C - Complex (11-20)    ⚠️ Consider refactoring
D - Very complex (21-30) ❌ Refactor soon
E/F - Extremely complex  ❌ Refactor immediately
```

**Example Output:**

```
src/tier1/conversation_manager.py
    M 145:4 ConversationManager.add_conversation - B (8)
    M 201:4 ConversationManager.search - C (12)  ⚠️ NEEDS REFACTORING
```

### Pylint - Code Quality

**Purpose:** Comprehensive code analysis (style, errors, best practices).

```bash
# Analyze entire codebase
pylint src/

# Focus on specific file
pylint src/plugins/cleanup_plugin.py

# Generate JSON report
pylint src/ --output-format=json > pylint-report.json
```

**Key Pylint Conventions:**

- `C` - Convention (naming, formatting)
- `R` - Refactor (duplicate code, too many arguments)
- `W` - Warning (potential issues)
- `E` - Error (probable bugs)
- `F` - Fatal (cannot parse)

**Score Interpretation:**

- 9-10: Excellent ✅
- 7-8.9: Good ⚠️ Minor cleanup
- 5-6.9: Fair ⚠️ Needs attention
- <5: Poor ❌ Significant issues

### Vulture - Dead Code Detection

**Purpose:** Find unused code (functions, classes, imports, variables).

```bash
# Find dead code (high confidence only)
vulture src/ --min-confidence 80

# Include all potential dead code
vulture src/ --min-confidence 60

# Generate report
vulture src/ --min-confidence 80 > vulture-report.txt
```

**Interpreting Vulture Output:**

```
src/tier2/pattern_matcher.py:45: unused function 'old_search' (90% confidence)
src/plugins/vision_plugin.py:12: unused import 'requests' (100% confidence)
```

**Confidence Levels:**
- 100%: Definitely unused ✅ Safe to remove
- 80-99%: Very likely unused ⚠️ Verify before removing
- 60-79%: Possibly unused ⚠️ Manual review required

---

## CORTEX Optimizer

### Running Analysis

```bash
# Run full optimization analysis (text output)
python scripts/admin/cortex_optimizer.py analyze

# Generate JSON report
python scripts/admin/cortex_optimizer.py analyze --report json
```

### Sample Output

```
🔍 CORTEX Codebase Optimization Analysis
============================================================

✅ Token Usage: 87/100
   Issues (2):
      • Large prompt file: cortex.md (6247 tokens)
      • Large prompt file: technical-reference.md (5892 tokens)
   Recommendations:
      → Split large prompt files into modular components

✅ YAML Validation: 95/100
   Issues (1):
      • Empty YAML file: temp-analysis.yaml
   Recommendations:
      → Fix YAML validation errors before deployment

⚠️ Plugin Health: 75/100
   Issues (3):
      • Missing register() in old_plugin.py
      • Missing PluginMetadata in experimental_plugin.py
      • Not inheriting from BasePlugin: legacy_plugin.py
   Recommendations:
      → Add register() function to incomplete plugins
      → Add PluginMetadata to plugins for discoverability

✅ Database Optimization: 92/100
   Issues (1):
      • Database fragmentation: 12.3%
   Recommendations:
      → Run VACUUM to defragment database

============================================================
🎯 Overall Optimization Score: 87/100

📋 Priority Recommendations:
   1. Split large prompt files into modular components
   2. Fix YAML validation errors before deployment
   3. Add register() function to incomplete plugins
   4. Run VACUUM to defragment database
   5. Add PluginMetadata to plugins for discoverability
```

### Individual Analyzers

Each analyzer returns:
- **Score:** 0-100 (higher is better)
- **Issues:** Specific problems detected
- **Recommendations:** Actionable fixes
- **Metrics:** Quantitative data

#### TokenAnalyzer Metrics

```json
{
  "total_prompt_tokens": 28445,
  "total_yaml_tokens": 8920,
  "avg_prompt_size": 3556,
  "prompt_file_count": 8,
  "large_files": [
    ["cortex.md", 6247],
    ["technical-reference.md", 5892]
  ]
}
```

**What to optimize:**
- Prompt files >5000 tokens → Split into modules
- YAML files >10000 tokens → Compress or archive old data

#### YAMLValidator Metrics

```json
{
  "total_yaml_files": 15,
  "valid_files": 14,
  "invalid_files": ["temp-analysis.yaml"],
  "validation_rate": "93%"
}
```

**What to fix:**
- Invalid files → Fix YAML syntax or add required fields
- Validation rate <80% → Add schema tests

#### PluginHealthChecker Metrics

```json
{
  "total_plugins": 8,
  "registered_plugins": 6,
  "missing_metadata": ["experimental_plugin.py"],
  "missing_register": ["old_plugin.py"],
  "health_score": "75%"
}
```

**What to fix:**
- Missing `register()` → Add plugin registration function
- Missing `PluginMetadata` → Add metadata for discoverability
- Health score <90% → Review plugin architecture compliance

#### ConversationDBOptimizer Metrics

```json
{
  "table_count": 3,
  "index_count": 4,
  "row_counts": {
    "conversations": 1247,
    "events": 8932,
    "metadata": 156
  },
  "size_mb": 12.4,
  "fragmentation_pct": 8.2
}
```

**What to optimize:**
- Fragmentation >10% → Run `VACUUM`
- Size >100MB → Archive old conversations
- Index count <2 → Add indexes on timestamp/event_type

### Future Commands (Coming Soon)

```bash
# Automated refactoring suggestions
python scripts/admin/cortex_optimizer.py refactor --dry-run

# Performance profiling
python scripts/admin/cortex_optimizer.py profile --module tier1

# Interactive dead code cleanup
python scripts/admin/cortex_optimizer.py cleanup --interactive
```

---

## Pre-Commit Integration

### Installation

```bash
# Install pre-commit framework
pip install pre-commit

# Install hooks to .git/hooks/
pre-commit install
```

### Automatic Checks (On Every Commit)

The following run automatically on `git commit`:

1. **black** - Auto-format code
2. **isort** - Sort imports
3. **flake8** - Style violations
4. **mypy** - Type checking
5. **check-yaml** - YAML syntax
6. **pylint** - Code quality
7. **radon** - Complexity warnings
8. **vulture** - Dead code detection

### Manual Checks

```bash
# Run all hooks on all files
pre-commit run --all-files

# Run specific hook
pre-commit run radon-complexity --all-files

# Run CORTEX optimizer manually
pre-commit run cortex-optimizer --all-files
```

**Why CORTEX optimizer is manual:**
- Comprehensive analysis takes longer
- Run before releases or quarterly reviews
- Avoid slowing down every commit

### Skipping Hooks (Emergency Only)

```bash
# Skip pre-commit checks (NOT recommended)
git commit --no-verify -m "Emergency fix"
```

---

## Interpreting Results

### Overall Health Score

| Score | Status | Action Required |
|-------|--------|-----------------|
| 90-100 | Excellent ✅ | Maintain standards |
| 80-89 | Good ⚠️ | Minor cleanup recommended |
| 70-79 | Fair ⚠️ | Schedule refactoring |
| 60-69 | Poor ❌ | Immediate attention needed |
| <60 | Critical ❌ | Stop feature work, fix issues |

### Priority Matrix

Prioritize fixes based on **Impact × Effort**:

| Issue | Impact | Effort | Priority |
|-------|--------|--------|----------|
| YAML parse errors | HIGH | LOW | 🔥 CRITICAL |
| Missing plugin metadata | HIGH | LOW | ⚠️ HIGH |
| Dead code | MEDIUM | LOW | ⚠️ HIGH |
| Large prompt files | MEDIUM | MEDIUM | 📋 MEDIUM |
| Complexity C rating | MEDIUM | HIGH | 📋 MEDIUM |
| Database fragmentation | LOW | LOW | ✅ LOW |

### Red Flags (Fix Immediately)

- ❌ Any YAML file that won't parse
- ❌ Plugins missing `register()` function
- ❌ Complexity rating E or F
- ❌ Pylint score <5
- ❌ Database errors

---

## Best Practices

### Weekly Routine

```bash
# Monday: Quick health check
python scripts/admin/cortex_optimizer.py analyze

# Review any issues with score <80
# Fix critical issues before continuing
```

### Pre-Release Checklist

```bash
# 1. Run full optimization analysis
python scripts/admin/cortex_optimizer.py analyze --report json > optimization-report.json

# 2. Check complexity of new code
radon cc src/ --min B

# 3. Find dead code
vulture src/ --min-confidence 80

# 4. Run all pre-commit checks
pre-commit run --all-files

# 5. Verify no critical issues
# Requirement: Overall score >85
```

### Quarterly Cleanup

```bash
# 1. Full code analysis
pylint src/ --output-format=json > pylint-quarterly.json

# 2. Dead code sweep (lower confidence threshold)
vulture src/ --min-confidence 60 > vulture-quarterly.txt

# 3. Database maintenance
# Run VACUUM on conversation DB if fragmentation >10%

# 4. Archive old conversations
# Move conversations >6 months to archive DB
```

### Continuous Improvement

- **Green builds:** Keep overall score >85
- **Zero tolerance:** No YAML parse errors, no missing plugin metadata
- **Complexity budget:** No new functions with complexity >B
- **Test coverage:** Run coverage with optimizations (`pytest --cov`)

---

## Troubleshooting

### "Module not found" Errors

**Problem:** Optimizer can't import CORTEX modules

**Solution:**
```bash
# Ensure running from CORTEX root
cd d:\PROJECTS\CORTEX

# Or set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:d:/PROJECTS/CORTEX"
```

### Pre-Commit Hooks Not Running

**Problem:** Hooks skipped on commit

**Solution:**
```bash
# Reinstall hooks
pre-commit uninstall
pre-commit install

# Verify installation
pre-commit run --all-files
```

### Radon Shows No Output

**Problem:** Radon doesn't find complex code

**Solution:**
```bash
# Lower threshold to see all complexity
radon cc src/ -a -s --min A

# Check specific file
radon cc src/tier1/conversation_manager.py -s
```

### Vulture False Positives

**Problem:** Reports used code as dead

**Solution:**
Create `vulture-whitelist.py`:
```python
# Whitelist for Vulture false positives
# These are used but Vulture can't detect usage

# Plugin system (dynamically loaded)
def register():
    pass

# CLI entry points
def main():
    pass
```

Run with whitelist:
```bash
vulture src/ vulture-whitelist.py --min-confidence 80
```

### CORTEX Optimizer Database Errors

**Problem:** Can't access conversation DB

**Solution:**
```bash
# Check DB exists
ls cortex-brain/conversation-history.db

# Check permissions (Windows)
icacls cortex-brain/conversation-history.db

# Rebuild DB if corrupted
python scripts/rebuild_conversation_db.py
```

---

## Advanced Usage

### Custom Radon Thresholds

```bash
# Strict mode (complexity A only)
radon cc src/ --min A --max-average A

# Custom JSON output for CI/CD
radon cc src/ --json --output-file=radon-report.json
```

### Pylint Custom Configuration

Create `.pylintrc`:
```ini
[MASTER]
ignore=tests,fixtures

[MESSAGES CONTROL]
disable=C0111,C0103,R0903

[FORMAT]
max-line-length=100

[DESIGN]
max-args=7
max-locals=15
```

Run with config:
```bash
pylint --rcfile=.pylintrc src/
```

### CORTEX Optimizer Programmatic Usage

```python
from scripts.admin.cortex_optimizer import CortexOptimizer

optimizer = CortexOptimizer()
results = optimizer.analyze(report_format="json")

# Filter critical issues
critical = [r for r in results["results"] if r["score"] < 70]
if critical:
    print(f"⚠️ {len(critical)} critical issues found!")
```

---

## Summary

**Quick Reference:**

```bash
# Daily: Pre-commit hooks (automatic)
git commit -m "Feature X"

# Weekly: CORTEX health check
python scripts/admin/cortex_optimizer.py analyze

# Pre-release: Full validation
pre-commit run --all-files
python scripts/admin/cortex_optimizer.py analyze --report json

# Quarterly: Deep cleanup
vulture src/ --min-confidence 60
radon cc src/ --min B
```

**Key Metrics to Track:**
- Overall optimization score: >85
- Plugin health: 100%
- YAML validation: 100%
- Complexity: No E/F ratings
- Pylint score: >8

---

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary  
**Last Updated:** 2025-11-13
