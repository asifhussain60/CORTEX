# 🎨 Refinement Orchestrator

**Version:** 1.0.0  
**Author:** Asif Hussain  
**Created:** January 3, 2026

## Overview

The Refinement Orchestrator is a comprehensive 7-phase code quality improvement system for CORTEX. It analyzes Python code for quality issues, duplicates, performance bottlenecks, and security vulnerabilities, then generates actionable refactoring plans.

## Features

### 7-Phase Workflow

1. **Code Quality Assessment** - Linting, complexity analysis, code smell detection
2. **Duplicate Detection** - AST-based duplicate code identification
3. **Performance Analysis** - Hotspot identification and optimization suggestions
4. **Security Audit** - Vulnerability scanning and remediation planning
5. **Refactoring Plan** - Prioritized task generation
6. **Apply Refactorings** - Automated and manual refactoring execution
7. **Validation & Metrics** - Before/after comparison and improvement tracking

### Key Capabilities

- **AST-Based Analysis** - Deep code structure understanding
- **Multi-Format Reports** - JSON, HTML, and Markdown outputs
- **Automated Refactoring** - Safe, automated code improvements
- **Comprehensive Metrics** - Quality, performance, and security scoring
- **Flexible Execution** - Run all phases or specific phases
- **Git Integration** - Automatic checkpointing before changes

## Quick Start

```python
from pathlib import Path
from src.orchestrators.refinement import RefinementOrchestrator

# Create orchestrator
target = Path("src/my_module.py")
orchestrator = RefinementOrchestrator(target)

# Execute all phases
results = orchestrator.execute()

# Get summary
summary = orchestrator.get_summary()
print(f"Quality Score: {summary['improvements']['quality_score_improvement']}")
```

## Installation

### Prerequisites

```bash
# Core dependencies
pip install pylint flake8 mypy black isort

# Optional for enhanced analysis
pip install radon  # Complexity metrics
pip install bandit # Security scanning
```

### CORTEX Integration

The Refinement Orchestrator is included in CORTEX:

```python
from src.orchestrators.refinement import RefinementOrchestrator
```

## Usage

### Basic Usage

```python
from pathlib import Path
from src.orchestrators.refinement import RefinementOrchestrator

# Single file
orchestrator = RefinementOrchestrator(
    target_path=Path("src/module.py"),
    output_dir=Path("reports/refinement")
)

results = orchestrator.execute()
```

### Advanced Usage

```python
# Execute specific phases
results = orchestrator.execute(phases=[1, 2, 3])

# Auto-apply safe refactorings
results = orchestrator.execute(auto_apply=True)

# Get detailed summary
summary = orchestrator.get_summary()
print(f"Session: {summary['session_id']}")
print(f"Status: {summary['status']}")
print(f"Improvements: {summary['improvements']}")
```

### Analyzing Directories

```python
# Analyze entire directory
orchestrator = RefinementOrchestrator(
    target_path=Path("src/my_package"),
    output_dir=Path("refinement-output")
)

results = orchestrator.execute()
```

## Output

### Reports Generated

For each session, the orchestrator generates:

1. **JSON Report** - Machine-readable complete results
2. **HTML Report** - Visual dashboard with metrics and recommendations
3. **Markdown Summary** - Human-readable executive summary

### Report Location

```
refinement-output/
├── refinement-report-{session_id}.json
├── refinement-report-{session_id}.html
└── refinement-summary-{session_id}.md
```

### Example Output Structure

```json
{
  "session_id": "20260103_120000",
  "status": "completed",
  "phases_completed": 7,
  "results": {
    "QualityAssessment": {
      "quality_score": 85,
      "issues": [...],
      "metrics": {...}
    },
    "DuplicateDetection": {
      "duplicates_found": 3,
      "duplicate_groups": [...],
      "consolidation_suggestions": [...]
    },
    ...
  }
}
```

## Architecture

### Phase Structure

Each phase is a self-contained module implementing:

```python
class Phase:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def execute(self) -> Dict[str, Any]:
        # Phase logic
        return results
```

### Directory Structure

```
src/orchestrators/refinement/
├── __init__.py
├── refinement_orchestrator.py     # Main orchestrator
├── phases/
│   ├── quality_assessment.py      # Phase 1
│   ├── duplicate_detection.py     # Phase 2
│   ├── performance_analysis.py    # Phase 3
│   ├── security_audit.py          # Phase 4
│   ├── refactoring_plan.py        # Phase 5
│   ├── apply_refactorings.py      # Phase 6
│   └── validation_metrics.py      # Phase 7
├── analyzers/
│   ├── code_quality_analyzer.py
│   ├── complexity_calculator.py
│   └── pattern_matcher.py
└── utils/
    ├── ast_utils.py
    └── metrics_reporter.py
```

## API Reference

### RefinementOrchestrator

Main orchestrator class for code refinement workflow.

#### Constructor

```python
RefinementOrchestrator(target_path: Path, output_dir: Optional[Path] = None)
```

**Parameters:**
- `target_path`: File or directory to refine
- `output_dir`: Output directory for reports (default: `./refinement-output`)

#### Methods

##### execute()

```python
def execute(
    phases: Optional[List[int]] = None,
    auto_apply: bool = False
) -> Dict[str, Any]
```

Execute refinement workflow.

**Parameters:**
- `phases`: Specific phases to run (1-7), None for all
- `auto_apply`: Auto-apply safe refactorings

**Returns:** Complete results dictionary

##### get_summary()

```python
def get_summary() -> Dict[str, Any]
```

Get refinement summary.

**Returns:** Summary with session info and improvements

## Configuration

### Custom Thresholds

Modify phase behavior by subclassing:

```python
class CustomQualityPhase(QualityAssessmentPhase):
    def _calculate_quality_score(self, results):
        # Custom scoring logic
        return score
```

### Report Customization

```python
from src.orchestrators.refinement.utils import MetricsReporter

reporter = MetricsReporter(output_dir)
reporter.generate_comprehensive_report(...)
```

## Testing

Run refinement orchestrator tests:

```bash
pytest tests/orchestrators/refinement/ -v
```

### Test Coverage

- ✅ Integration tests (10 tests)
- ✅ Phase-specific tests (18 tests)
- ✅ End-to-end workflow validation
- ✅ Error handling

## Best Practices

### 1. Start with Analysis Phases

Run phases 1-4 first to understand issues before refactoring:

```python
results = orchestrator.execute(phases=[1, 2, 3, 4])
```

### 2. Review Refactoring Plan

Always review the refactoring plan (Phase 5) before applying changes:

```python
plan = results["results"]["RefactoringPlan"]
print(f"Tasks: {len(plan['refactoring_tasks'])}")
print(f"Effort: {plan['estimated_effort_hours']} hours")
```

### 3. Use Git Checkpoints

Enable auto-apply only with version control:

```python
# Ensure in git repo
results = orchestrator.execute(auto_apply=True)
```

### 4. Incremental Refinement

Refine in stages, validating after each:

```python
# Stage 1: Quality
orchestrator.execute(phases=[1, 5, 6, 7])

# Stage 2: Security
orchestrator.execute(phases=[4, 5, 6, 7])
```

## Troubleshooting

### Common Issues

**Issue:** "No Python files found"
- **Solution:** Ensure target path contains `.py` files
- Check exclusion patterns (excludes `__pycache__`, `.venv`, etc.)

**Issue:** "Quality score is 0"
- **Solution:** Target file may not exist or has syntax errors
- Run Phase 1 separately to debug

**Issue:** "Pylint not found"
- **Solution:** Install with `pip install pylint`
- Analysis continues without it (graceful degradation)

## Roadmap

### Upcoming Features

- [ ] JavaScript/TypeScript support
- [ ] Custom analyzer plugins
- [ ] CI/CD integration guides
- [ ] Real-time refactoring preview
- [ ] Team collaboration features

## Support

For issues or questions:

1. Check [Examples](examples/) directory
2. Review [Architecture](architecture.md) documentation
3. Open GitHub issue with reproduction steps

## License

Copyright © 2025-2026 Asif Hussain. All rights reserved.

---

**See Also:**
- [User Guide](user-guide.md) - Detailed usage instructions
- [Architecture](architecture.md) - Technical design
- [Examples](examples/) - Code examples
