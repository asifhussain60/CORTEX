# Onboarding Orchestrator - Quick Reference Card

**Version:** 3.8.1 | **Type:** CORTEX Learning Resource  
**Purpose:** Fast lookup for onboarding orchestrator operations

---

## 🚀 Quick Start

### Basic Usage

```python
from pathlib import Path
from src.operations.onboarding_orchestrator import OnboardingOrchestrator

# Initialize
orchestrator = OnboardingOrchestrator(
    project_root=Path.cwd(),
    test_mode=False  # Production mode
)

# Onboard application
result = orchestrator.onboard_application(
    project_path=Path("/path/to/app"),
    project_name="MyApp"
)

# Check results
if result.success:
    print(f"Dashboard: {result.dashboard_url}")
```

### CLI Usage

```bash
python src/operations/onboarding_orchestrator.py /path/to/app --name "MyApp"
```

---

## 📋 10 Phases (30-60 seconds total)

| Phase | Name | Time | Output |
|-------|------|------|--------|
| 1 | Project Metadata | ~1-2s | Files, lines, languages |
| 2 | Code Quality | ~3-10s | Issues list, quality score |
| 3 | Security Scan | ~5-15s | Vulnerabilities list |
| 4 | Performance Metrics | <1s | Execution metrics |
| 5 | Architecture Graph | ~5-20s | Dependency graph |
| 6 | Tech Stack | ~2-5s | Languages, frameworks |
| 7 | Recommendations | ~1-3s | Improvement suggestions |
| 8 | UML Diagrams | ~5-15s | Class diagrams (SVG) |
| 9 | **Parallel Collection** | ~8-20s | **6 JSON files** |
| 10 | Validation | ~2-5s | Validation report |

---

## 🎯 Two Operation Modes

### Production Mode (`test_mode=False`)
- **Context:** CORTEX embedded in user repo
- **Output Path:** `{user-repo}/cortex-brain/dashboards/{project}/`
- **Use Case:** Standard application onboarding

### Test Mode (`test_mode=True`)
- **Context:** Standalone CORTEX testing external repos
- **Output Path:** `{cortex-root}/cortex-brain/documents/onboarded-apps/{project}/`
- **Use Case:** Testing, demonstrations, multi-repo analysis

---

## 📊 Output Files (7 total)

| File | Content | Collector |
|------|---------|-----------|
| `health-data.json` | Overall health metrics | Aggregator |
| `tech-stack.json` | Languages, frameworks | TechStackCollector |
| `security.json` | Vulnerabilities, score | SecurityCollector |
| `architecture.json` | Components, patterns | ArchitectureCollector |
| `code-organization.json` | Files, lines, hotspots | CodeOrganizationCollector |
| `vendors.json` | External vendors | VendorCollector |
| `metadata.json` | Scan info, timestamp | Metadata Generator |

---

## 🔧 Key Methods

### Initialization
```python
__init__(project_root: Path, test_mode: bool = False)
```
- Sets operation mode
- Finds CORTEX installation
- Initializes logging

### Main Entry Point
```python
onboard_application(
    project_path: Path,
    project_name: Optional[str] = None
) -> OnboardingResult
```
- Executes all 10 phases
- Returns comprehensive result object

### File Filtering
```python
_should_scan_file(file_path: Path) -> bool
```
- Excludes hidden dirs (`.git`, `.venv`)
- Excludes build artifacts (`__pycache__`, `node_modules`)
- Excludes binaries (`.pyc`, `.dll`)
- Includes source files (`.py`, `.js`, `.cs`)

### Health Calculation
```python
_calculate_health_metrics(collected_data: Dict) -> Dict
```
- Security: 35% weight
- Code Quality: 25% weight
- Architecture: 25% weight
- Tech Stack: 15% weight
- Returns: 0-100 score + status

---

## 🎨 Health Score Formula

```python
security_score = security["score"] × 0.35
code_score = (100 - hotspots × 5) × 0.25
arch_score = (100 - components / 10) × 0.25
tech_score = (languages × 20) × 0.15

overall_score = security_score + code_score + arch_score + tech_score

# Status
if overall_score >= 80: status = "healthy"
elif overall_score >= 60: status = "warning"
else: status = "critical"
```

---

## ⚡ Parallel Collection Architecture

**Phase 9** uses `ParallelCollectorOrchestrator`:

```python
# 6 collectors run simultaneously in thread pool
collectors = [
    TechStackCollector,      # Thread 1
    SecurityCollector,       # Thread 2
    ArchitectureCollector,   # Thread 3
    CodeOrganizationCollector, # Thread 4
    VendorCollector,         # Thread 5
    TeamMetricsCollector     # Thread 6 (optional)
]

# Execution
with ThreadPoolExecutor(max_workers=6) as executor:
    futures = [executor.submit(c.collect) for c in collectors]
    results = [f.result() for f in futures]
```

**Performance Gain:** 3-5x faster than sequential execution

---

## 🚨 Common Issues & Solutions

### Issue: ImportError
```python
# Solution: Add CORTEX root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
```

### Issue: Slow Performance (>2 minutes)
```python
# Solution 1: Check file filtering
if len(all_files) > 10000:
    logger.warning("Large project - consider exclusions")

# Solution 2: Limit UML generation
if len(python_files) > 100:
    python_files = python_files[:50]  # Reduce limit
```

### Issue: Validation Failures
```python
# Check validation report
report_path = output_path / 'dashboard_validation_report.json'
with open(report_path) as f:
    report = json.load(f)

for test in report['tests']:
    if not test['passed']:
        print(f"Failed: {test['name']} - {test['error']}")
```

### Issue: Missing Graphviz
```bash
# Install graphviz for UML generation
pip install graphviz

# Or skip UML (optional feature)
# Orchestrator auto-skips if unavailable
```

---

## 📁 File Exclusion Patterns

### Directories (Always Excluded)
```
/.git/
/.venv/, /venv/, /.env/
/__pycache__/, /.pytest_cache/
/node_modules/, /.tox/
/dist/, /build/, /.egg-info/
/.mypy_cache/, /.coverage, /htmlcov/
/.idea/, /.vscode/, /.vs/
/bin/, /obj/
```

### Binary Extensions (Always Excluded)
```
.pyc, .pyo, .pyd
.so, .dll, .exe, .bin
.pack, .idx, .rev
.db, .sqlite, .sqlite3
```

### Source Extensions (Always Included)
```
.py, .js, .ts, .jsx, .tsx
.cs, .java, .go, .rb, .php
.cpp, .c, .h, .hpp
.rs, .swift, .kt, .scala
.sql, .yaml, .yml, .json, .xml
.md, .txt, .sh, .ps1, .bat
```

---

## 🔍 OnboardingResult Attributes

```python
@dataclass
class OnboardingResult:
    success: bool               # Overall success status
    project_name: str           # Application name
    analysis_timestamp: str     # ISO 8601 timestamp
    quality_score: float        # 0-100 (higher = better)
    security_issues: int        # Number of vulnerabilities
    performance_metrics: int    # Performance observations
    dashboard_url: str          # Relative path to dashboard
    errors: List[str]           # Error messages (if any)
    output_path: Optional[Path] # Path to output directory
```

---

## 📊 Dashboard Structure

```
cortex-brain/dashboards/{project-slug}/
├── health-data.json          # Overall metrics
├── tech-stack.json           # Technologies
├── security.json             # Security scan
├── architecture.json         # Components
├── code-organization.json    # File structure
├── vendors.json              # External APIs
└── metadata.json             # Scan metadata
```

**Access Dashboard:**
```
cortex-brain/dashboards/ui/index.html?source={project-slug}
```

---

## 🧪 Testing & Validation

### Enable Debug Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Profile Performance
```python
import time

start = time.time()
result = orchestrator.onboard_application(...)
elapsed = time.time() - start

print(f"Total time: {elapsed:.2f}s")
```

### Validate Output
```python
# Check all files exist
required_files = [
    'health-data.json',
    'tech-stack.json',
    'security.json',
    'architecture.json',
    'code-organization.json',
    'vendors.json',
    'metadata.json'
]

for filename in required_files:
    file_path = output_path / filename
    assert file_path.exists(), f"Missing: {filename}"
```

---

## 🔗 Integration Examples

### With Planning Orchestrator
```python
# After onboarding, launch planning
from src.orchestrators.planning_orchestrator import PlanningOrchestrator

result = onboarding_orchestrator.onboard_application(...)
if result.success:
    planner = PlanningOrchestrator()
    planner.create_improvement_plan(
        quality_score=result.quality_score,
        security_issues=result.security_issues
    )
```

### With Dashboard Launcher
```python
# After onboarding, auto-launch dashboard
from src.orchestrators.dashboard_launcher import DashboardLauncher

result = onboarding_orchestrator.onboard_application(...)
if result.success:
    launcher = DashboardLauncher()
    launcher.launch(project_slug=result.project_name.lower())
```

---

## 📚 Related Documentation

- **Full Guide:** `cortex-brain/learning/onboarding-orchestrator-guide.md`
- **Flowcharts:** `cortex-brain/learning/onboarding-orchestrator-flowcharts.md`
- **CORTEX Prompt:** `.github/prompts/CORTEX.prompt.md`
- **Source Code:** `src/operations/onboarding_orchestrator.py`

---

## 💡 Tips & Best Practices

### Performance Optimization
- Use SSD for large projects (>5000 files)
- Exclude test fixtures and sample data
- Limit UML generation to critical classes

### Error Handling
- Always check `result.success` before accessing data
- Log errors for troubleshooting: `logger.error(result.errors)`
- Use validation report for dashboard issues

### Quality Improvements
- Address "critical" issues first (highest impact)
- Review security scan for OWASP vulnerabilities
- Monitor hotspots in code organization

### Dashboard Usage
- Share dashboard URL with stakeholders
- Re-run onboarding after major changes
- Export JSON for custom reporting

---

## 🎓 Learning Path

1. **Start Here:** Read overview section of full guide
2. **Understand Flow:** Review flowcharts (sequence diagram)
3. **Try It:** Run on sample application
4. **Debug:** Enable logging and profile performance
5. **Extend:** Add custom collectors or analyzers

---

**Quick Reference Version:** 1.0  
**Last Updated:** December 7, 2025  
**Maintainer:** Asif Hussain

---

## Cheat Sheet Summary

```
┌─────────────────────────────────────────────────────────┐
│ ONBOARDING ORCHESTRATOR - AT A GLANCE                  │
├─────────────────────────────────────────────────────────┤
│ • 10 phases: Metadata → Quality → Security → ... →     │
│              Validation                                  │
│ • Time: 30-60 seconds typical                           │
│ • Output: 7 JSON files + HTML dashboard                │
│ • Modes: Production (embedded) | Test (standalone)     │
│ • Parallel: Phase 9 uses 6 threads                     │
│ • Health Score: Security 35% + Code 25% + Arch 25% +   │
│                Tech 15%                                 │
│ • Files Excluded: Hidden dirs, build artifacts,        │
│                   binaries                             │
│ • Files Included: Source code (.py, .js, .cs, etc.)   │
└─────────────────────────────────────────────────────────┘
```
