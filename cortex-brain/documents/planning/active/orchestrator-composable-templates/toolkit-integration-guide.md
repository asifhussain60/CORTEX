# CORTEX Toolkit Integration Guide

**Purpose:** Integration instructions for the 3 new template system tools  
**Audience:** CORTEX maintainers and contributors  
**Date:** 2025-12-31

---

## 🎯 Overview

Three new tools added to CORTEX Toolkit for managing the Orchestrator Composable Template System:

1. **validate_templates.py** - YAML validation for templates and manifests
2. **analyze_blocks.py** - Block usage analysis and optimization recommendations
3. **progress_bar.py** - Standardized progress bar generation

All tools use Python standard library only (no external dependencies).

---

## 📦 Installation

Tools are located in `cortex-toolkit/` and ready to use immediately:

```bash
# No installation needed - tools are portable Python scripts
python cortex-toolkit/validate_templates.py
python cortex-toolkit/analyze_blocks.py --save
python cortex-toolkit/progress_bar.py
```

---

## 🔧 CI/CD Integration

### GitHub Actions Workflow

Add validation to `.github/workflows/validate-templates.yml`:

```yaml
name: Validate CORTEX Templates

on:
  push:
    paths:
      - 'cortex-brain/response-templates-v4.yaml'
      - 'cortex-brain/manifests/orchestrators/*.yaml'
  pull_request:
    paths:
      - 'cortex-brain/response-templates-v4.yaml'
      - 'cortex-brain/manifests/orchestrators/*.yaml'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Validate Templates
        run: python cortex-toolkit/validate_templates.py
      
      - name: Generate Block Analysis
        if: github.event_name == 'push' && github.ref == 'refs/heads/main'
        run: |
          python cortex-toolkit/analyze_blocks.py --save --output cortex-brain/documents/analysis/block-analysis-latest.md
          git config user.name "CORTEX Bot"
          git config user.email "cortex@noreply.github.com"
          git add cortex-brain/documents/analysis/block-analysis-latest.md
          git commit -m "📊 Update block analysis report" || echo "No changes"
          git push || echo "Nothing to push"
```

### Pre-commit Hook

Add to `.git/hooks/pre-commit`:

```bash
#!/bin/bash
# Validate templates before commit

echo "🔍 Validating CORTEX templates..."
python cortex-toolkit/validate_templates.py

if [ $? -ne 0 ]; then
    echo "❌ Template validation failed. Commit aborted."
    exit 1
fi

echo "✅ Template validation passed"
exit 0
```

Make executable:
```bash
chmod +x .git/hooks/pre-commit
```

---

## 🔄 Maintenance Workflows

### Weekly Block Analysis

Add to crontab or scheduled task:

```bash
# Weekly Sunday night analysis
0 0 * * 0 cd /path/to/CORTEX && python cortex-toolkit/analyze_blocks.py --save --output cortex-brain/documents/analysis/block-analysis-$(date +\%Y-\%m-\%d).md
```

### Monthly Template Audit

Create `scripts/monthly-template-audit.sh`:

```bash
#!/bin/bash
# Monthly template system audit

echo "=== CORTEX Template System Audit ==="
echo "Date: $(date)"
echo ""

# Validation
echo "1. Running validation..."
python cortex-toolkit/validate_templates.py
VALIDATION_STATUS=$?

# Block analysis
echo ""
echo "2. Generating block analysis..."
python cortex-toolkit/analyze_blocks.py --save --output "cortex-brain/documents/analysis/audit-$(date +%Y-%m).md"

# Summary
echo ""
echo "=== Audit Complete ==="
echo "Validation: $([ $VALIDATION_STATUS -eq 0 ] && echo '✅ PASS' || echo '❌ FAIL')"
echo "Report: cortex-brain/documents/analysis/audit-$(date +%Y-%m).md"

exit $VALIDATION_STATUS
```

---

## 🐍 Python Integration

### Importing in Orchestrators

```python
# In orchestrator implementation files
import sys
from pathlib import Path

# Add toolkit to path
toolkit_path = Path(__file__).parent.parent / "cortex-toolkit"
sys.path.insert(0, str(toolkit_path))

from progress_bar import generate_progress_bar, generate_orchestrator_progress

# Use in orchestrator
class PlanningOrchestrator:
    def execute_phase(self, current_phase: int, total_phases: int):
        progress = generate_progress_bar(
            current=current_phase,
            total=total_phases,
            status="in_progress"
        )
        print(f"**Progress:** {progress}")
```

### Validation in Tests

```python
# tests/test_templates.py
import pytest
from pathlib import Path
import sys

# Add toolkit to path
toolkit_path = Path(__file__).parent.parent / "cortex-toolkit"
sys.path.insert(0, str(toolkit_path))

from validate_templates import TemplateValidator

def test_templates_valid():
    """Ensure all templates and manifests are valid."""
    validator = TemplateValidator()
    results = validator.validate_all()
    
    assert results["summary"]["all_valid"], "Template validation failed"
    
def test_progress_bar_standard():
    """Verify progress bar meets standard."""
    from progress_bar import PROGRESS_BAR_CONFIG
    
    assert PROGRESS_BAR_CONFIG["width"] == 10
    assert PROGRESS_BAR_CONFIG["filled_char"] == "█"
    assert PROGRESS_BAR_CONFIG["empty_char"] == "░"
```

---

## 📊 Usage Examples

### 1. Validate Before Deploy

```bash
# Before deploying CORTEX changes
python cortex-toolkit/validate_templates.py

# Exit code 0 = success, 1 = failure
if [ $? -eq 0 ]; then
    echo "Safe to deploy"
    # ... deployment commands
else
    echo "Fix validation errors first"
    exit 1
fi
```

### 2. Monthly Health Check

```bash
# Generate comprehensive health report
python cortex-toolkit/analyze_blocks.py --save

# Output saved to:
# cortex-brain/documents/analysis/block-analysis-report.md
```

### 3. Progress Bar in Scripts

```python
from cortex_toolkit.progress_bar import generate_progress_bar

phases = ["Discovery", "Analysis", "Implementation", "Testing", "Documentation"]

for idx, phase in enumerate(phases):
    progress = generate_progress_bar(
        current=idx + 1,
        total=len(phases),
        status="in_progress" if idx < len(phases) - 1 else "completed"
    )
    print(f"{phase}: {progress}")
```

---

## 🛡️ SKULL Compliance

All toolkit tools follow Brain Protection Rules:

### TDD_ENFORCEMENT
- Tools tested with example cases (see `progress_bar.py` demo)
- Validation tools ensure templates pass structure tests

### HOLISTIC_DISCOVERY
- `analyze_blocks.py` searches all manifests before reporting
- `validate_templates.py` checks all files for comprehensive coverage

### GIT_ISOLATION
- Tools are read-only (except report generation)
- No automatic commits without explicit approval

### PLANNING_ISOLATION
- Tools support planning workflows but don't implement changes
- Analysis reports inform decisions, don't make them

### HAND_OFF_PROTOCOL
- Tools can be used by 🛡️ AUTONOMOUS orchestrators
- Clear separation between analysis and action

---

## 📝 Documentation Updates

### README.md Updates
- Added "Template System Tools (NEW)" section
- Listed all 3 tools with usage examples
- Preserved existing toolkit documentation

### TRUTH-SOURCES.yaml
Add to toolkit section:
```yaml
toolkit:
  template_system_tools:
    - validate_templates.py
    - analyze_blocks.py
    - progress_bar.py
  documentation:
    - cortex-toolkit/README.md
    - cortex-brain/documents/planning/active/orchestrator-composable-templates/toolkit-integration-guide.md
```

---

## 🔮 Future Enhancements

Potential additions (not yet implemented):

1. **block_composer.py** - Runtime template composition engine
2. **manifest_updater.py** - Bulk manifest updates CLI
3. **template_linter.py** - Style consistency checker
4. **block_dependency_analyzer.py** - Dependency mapping
5. **template_coverage_reporter.py** - Coverage tracking

---

## 🆘 Troubleshooting

### "No such file or directory" errors
**Cause:** Incorrect path detection  
**Fix:** Tools use `Path(__file__).parent.parent` to find CORTEX root. Verify running from correct directory:
```bash
# Must be in CORTEX root
cd /path/to/CORTEX
python cortex-toolkit/validate_templates.py
```

### "KeyError: 'templates_valid'" in validator
**Cause:** File read failure before summary generation  
**Fix:** Check that response-templates-v4.yaml exists and is readable

### Missing manifests in analysis
**Cause:** Manifests not in expected location  
**Fix:** Verify manifests are in `cortex-brain/manifests/orchestrators/`

---

## ✅ Verification Checklist

After integration, verify:

- [ ] `python cortex-toolkit/validate_templates.py` exits with code 0
- [ ] `python cortex-toolkit/analyze_blocks.py --save` creates report in `cortex-brain/documents/analysis/`
- [ ] `python cortex-toolkit/progress_bar.py` displays demo output
- [ ] CI/CD workflow validates templates on push
- [ ] Pre-commit hook blocks invalid templates
- [ ] Monthly audit runs successfully
- [ ] Progress bars use 10-char width, █░ characters
- [ ] All 8 orchestrator manifests validated

---

**Author:** Asif Hussain  
**Copyright:** © 2025 Asif Hussain. All rights reserved.  
**Version:** 1.0.0  
**Status:** Production Ready  
**Last Updated:** 2025-12-31
