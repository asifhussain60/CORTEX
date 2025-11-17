# CORTEX Brain Simulations

This directory contains simulation data from crawler runs on external repositories.
Simulations are used to test and demonstrate how crawlers feed the brain without polluting production design files.

## Purpose
- Test crawler functionality on real-world repositories
- Demonstrate brain learning capabilities
- Analyze pattern discovery and knowledge graph population
- Verify crawler accuracy and performance

## Structure
```
simulations/
├── README.md              # This file
├── .gitignore            # Prevents simulation data commits
└── {repo-name}/          # One directory per simulated repository
    ├── crawler-results/  # Raw crawler output (JSON)
    ├── brain-snapshot/   # Knowledge graph snapshot after simulation
    └── simulation-report.md  # Analysis and findings
```

## Usage

### Run a Simulation
```powershell
# Clone target repository to temp location
git clone https://github.com/owner/repo C:\Temp\simulation-repo

# Run crawler orchestrator
.\scripts\crawlers\orchestrator.ps1 -WorkspaceRoot "C:\Temp\simulation-repo" -Mode deep

# Results saved to cortex-brain/simulations/{repo-name}/
```

### Analyze Results
See the `simulation-report.md` in each repo directory for:
- What crawlers discovered
- How brain tiers were populated
- Pattern analysis
- Recommendations

## Active Simulations

### KSESSIONS
**Repository:** https://github.com/asifhussain60/KSESSIONS
**Date:** 2025-11-06
**Purpose:** Demonstrate crawler capabilities on session management repository
**Status:** In Progress
