# Two-Tier AST Scanning Strategy

**Created:** December 11, 2025  
**Author:** Asif Hussain  
**Purpose:** Document the architectural decision for two-tier code analysis

---

## 🎯 Overview

CORTEX uses a **two-tier AST scanning strategy** to balance speed with depth:

| Tier | Purpose | Trigger | Scope | Time | Method |
|------|---------|---------|-------|------|--------|
| **TIER 1** | AI instruction generation | `setup copilot instructions` | 3-5 files | <3s | Regex + imports |
| **TIER 2** | Deep code analysis | `onboard application` | Full codebase | 30-60s | AST + metrics |

---

## 🚀 TIER 1: Lightweight Setup Scan

### Purpose
Generate **just enough intelligence** for AI instructions (copilot-instructions.md and CORTEX.prompt.md enhancements).

### Implementation
**Module:** `src/operations/modules/setup/code_pattern_detector.py` (561 lines)

**Approach:**
- **Fast regex matching** (not deep AST parsing)
- **Import detection** (framework/library hints from imports)
- **Directory structure heuristics** (repos/, services/ directories)
- **Hard limits:** 3-5 files max, no recursion

**Detected Patterns:**
1. **Framework:** FastAPI, Flask, Django, React, Angular, Spring Boot
2. **Auth hint:** JWT, OAuth (from imports)
3. **API hint:** REST decorators/annotations
4. **ORM hint:** SQLAlchemy, Entity Framework, TypeORM
5. **Architecture hint:** Repository/Service (from directory structure)

**Performance Target:** <3 seconds

### Example Output
```python
DomainPatterns(
    architecture=["Repository Pattern", "Service Layer"],
    auth_method="JWT authentication",
    api_style="REST with FastAPI",
    data_access="SQLAlchemy async ORM",
    testing_patterns=["pytest"],
    framework_specifics={"fastapi": "FastAPI async framework"}
)
```

### Use Case
```bash
> setup copilot instructions

🔍 Analyzing codebase...
   ✓ Detected: Python 3.11 with FastAPI
   ✓ Found: Repository Pattern
   ✓ Found: JWT authentication
   ⏱️  Analysis completed in 2.1 seconds

📝 Generated .github/copilot-instructions.md
   • Domain patterns: 4 detected
   • File size: 342 lines (~1,200 tokens)
```

---

## 🔬 TIER 2: Deep Analysis via Dashboard Collectors

### Purpose
Comprehensive code analysis for **metrics, complexity, dependencies, and code quality**.

### Implementation
**Modules:** (Already exist in CORTEX)
- `src/operations/modules/dashboard/code_metrics_collector.py`
- `src/operations/modules/dashboard/complexity_analyzer.py`
- `src/operations/modules/dashboard/dependency_analyzer.py`
- `src/operations/modules/dashboard/test_coverage_collector.py`

**Approach:**
- **Full AST parsing** of all code files
- **Cyclomatic complexity** analysis
- **Dependency graph** construction
- **Test coverage** mapping
- **Code hotspot** detection
- **Technical debt** calculation

**Detected Metrics:**
1. **Lines of Code:** Total, per file, per module
2. **Complexity:** Cyclomatic complexity, cognitive complexity
3. **Dependencies:** Import graphs, circular dependency detection
4. **Test Coverage:** Line coverage, branch coverage
5. **Code Quality:** Duplication, coupling, cohesion
6. **Hotspots:** Frequently changed files, high-complexity areas

**Performance:** 30-60 seconds (background task with caching)

### Use Case
```bash
> onboard application

🔍 Deep analysis in progress...
   ⏱️  Analyzing 342 files...
   ✓ Code metrics collected
   ✓ Complexity analysis complete
   ✓ Dependency graph built
   ✓ Test coverage mapped
   
📊 Dashboard updated with insights
   • Average complexity: 4.2
   • Test coverage: 87%
   • Technical debt: 12 hours
```

---

## 🔀 Integration Points

### Setup Workflow (TIER 1)
```python
# In master_setup_utility.py:generate_copilot_instructions()

from src.operations.modules.setup.code_pattern_detector import detect_patterns

# Fast scan for AI instructions
patterns = detect_patterns(project_root, language)  # <3 seconds

# Generate copilot-instructions.md with detected patterns
content = render_enhanced_template(project_name, detection, patterns)
```

### Onboarding Workflow (TIER 2)
```python
# In application_onboarding_orchestrator.py (already exists)

from src.operations.modules.dashboard.code_metrics_collector import collect_metrics
from src.operations.modules.dashboard.complexity_analyzer import analyze_complexity

# Deep analysis for dashboard
metrics = collect_metrics(project_root)  # 30-60 seconds
complexity = analyze_complexity(project_root)

# Update dashboard with detailed insights
dashboard.update(metrics, complexity, dependencies, coverage)
```

---

## 📊 Comparison

| Aspect | TIER 1 (Setup) | TIER 2 (Onboarding) |
|--------|----------------|---------------------|
| **Speed** | <3 seconds | 30-60 seconds |
| **Files scanned** | 3-5 files | All files |
| **Method** | Regex + imports | Full AST parsing |
| **Output** | 4-5 patterns | Comprehensive metrics |
| **Purpose** | AI instructions | Dashboard analytics |
| **Trigger** | `setup copilot instructions` | `onboard application` |
| **Caching** | 1 hour TTL | Persistent with invalidation |

---

## ✅ Benefits

### TIER 1 Benefits
- ✅ **Instant feedback** for setup (<3s)
- ✅ **Just enough intelligence** for AI instructions
- ✅ **Minimal overhead** (no complex AST parsing)
- ✅ **User-friendly** (fast response during setup)

### TIER 2 Benefits
- ✅ **Comprehensive insights** for development
- ✅ **Actionable metrics** for code quality
- ✅ **Background processing** (doesn't block user)
- ✅ **Persistent dashboard** (always available)

### Combined Benefits
- ✅ **No redundancy** (each tier serves distinct purpose)
- ✅ **Optimal performance** (fast when needed, deep when valuable)
- ✅ **Clear separation** (setup vs ongoing development)
- ✅ **Scalable** (TIER 1 stays fast regardless of codebase size)

---

## 🚀 Future Enhancements

### TIER 1 Enhancements
- [ ] Add Go/Rust/PHP language support
- [ ] Detect microservice architecture (docker-compose.yml, K8s)
- [ ] Detect CI/CD patterns (.github/workflows, .gitlab-ci.yml)
- [ ] Pattern confidence scoring

### TIER 2 Enhancements
- [ ] Machine learning for code smell detection
- [ ] Architectural drift detection
- [ ] Performance bottleneck prediction
- [ ] Security vulnerability scanning

---

## 📝 Usage Guidelines

### When to Use TIER 1
- ✅ Initial project setup
- ✅ Generating copilot-instructions.md
- ✅ Quick framework/pattern detection
- ✅ CORTEX.prompt.md enhancements

### When to Use TIER 2
- ✅ Application onboarding (detailed setup)
- ✅ Dashboard metrics updates
- ✅ Code quality analysis
- ✅ Technical debt assessment
- ✅ Refactoring planning

### When to Skip Analysis
- ❌ User explicitly requests generic instructions
- ❌ Project has no code files (pure config repos)
- ❌ Non-supported language with no heuristics

---

## 🔍 Example: Full Workflow

```bash
# Step 1: Fast setup (TIER 1)
> setup copilot instructions
⏱️  2.1 seconds | 4 patterns detected

# Step 2: Deep onboarding (TIER 2) - later, when ready
> onboard application
⏱️  45 seconds | Full metrics collected

# Result: Best of both worlds
# - Fast AI instructions immediately available
# - Deep insights available when needed
```

---

**Key Takeaway:** TIER 1 gives AI agents **just enough** context to be helpful, while TIER 2 provides **comprehensive** insights for development. The two-tier approach optimizes for both **speed** and **depth** without compromise.

---

**Implementation Status:**
- ✅ TIER 1: code_pattern_detector.py (561 lines, <3s performance target)
- ✅ TIER 2: Dashboard collectors (already exist, 30-60s)
- ⏳ Integration: master_setup_utility.py (next step)
- ⏳ Documentation: SETUP-GUIDE.md update (pending)

**Target Release:** CORTEX 3.9.0
