# CORTEX Plan Upgrade Orchestrator

Autonomous migration of legacy plans to CORTEX-5.0 standards.

## Quick Start

```bash
python cortex-upgrade-plan.py path/to/legacy-plan/
```

## Features

- ✅ Analyzes legacy plan structure and content
- ✅ Generates CORTEX-5.0 compliant plan
- ✅ Creates visual progress trackers
- ✅ Adds mandatory REFACTOR phase (18+ tasks)
- ✅ Documents GIT_NO_PUSH_ENFORCEMENT
- ✅ Archives old plan safely
- ✅ Generates comprehensive migration report

## Documentation

- **Quick Start:** [QUICKSTART-plan-upgrade.md](../../docs/orchestrators/QUICKSTART-plan-upgrade.md)
- **Full Documentation:** [plan-upgrade-orchestrator.md](../../docs/orchestrators/plan-upgrade-orchestrator.md)

## Usage

```bash
# Basic upgrade
python cortex-upgrade-plan.py cortex-brain/documents/planning/active/old-plan/

# Auto-archive original
python cortex-upgrade-plan.py old-plan.md --archive

# Custom output
python cortex-upgrade-plan.py old-plan/ --output new-plan-v5/
```

## Python API

```python
from pathlib import Path
from src.orchestrators.plan_upgrade import PlanUpgradeOrchestrator

workspace = Path.cwd()
orchestrator = PlanUpgradeOrchestrator(workspace)

# Analyze
analysis = orchestrator.analyze_legacy_plan(Path("old-plan/"))

# Upgrade
new_plan_dir = orchestrator.generate_upgraded_plan(analysis)

# Archive
orchestrator.archive_legacy_plan(Path("old-plan/"))
```

## CORTEX-5.0 Compliance

All upgraded plans include:

- ✅ Proper folder structure (`context/`, `reports/`, `artifacts/`, `tracking/`)
- ✅ Visual progress tracker (ASCII bars)
- ✅ REFACTOR phase with 18+ mandatory tasks
- ✅ Git checkpoint documentation
- ✅ GIT_NO_PUSH_ENFORCEMENT
- ✅ SKULL rules section
- ✅ Acceptance criteria format
- ✅ Progress tracking JSON

## Output

```
plan-name-v5/
├── 00-master-plan.md          # CORTEX-5.0 compliant
├── context/                    # Copied from legacy plan
├── reports/
│   └── migration-report.md    # Auto-generated
├── artifacts/
└── tracking/
    └── progress-tracker.json  # Auto-generated
```

## Requirements

- Python 3.8+
- CORTEX workspace structure
- Legacy plan (directory or .md file)

## License

Copyright © 2026 Asif Hussain. All rights reserved.
