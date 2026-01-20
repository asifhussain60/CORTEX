# CORTEX GitHub Pages Archive

This directory contains archived documentation from previous versions of the CORTEX project that were hosted at https://asifhussain60.github.io/CORTEX/

## Contents

### docs-cortex-4.0
Comprehensive documentation from CORTEX v4.0 branch, including:
- Architecture documentation (ARCHITECTURE-MAP.md, DEPLOYMENT-ARCHITECTURE-*.md)
- Phase implementation reports (PHASE-*.md, PHASE-*-COMPLETION-REPORT.md)
- Technical specifications and guides
- Executive summaries and status reports
- Governance and policy documentation
- MCP tool catalogs and integration guides
- Comprehensive index files (_archive/subdirectories with organized reports)

**Date**: 2026-01-19
**Source Branch**: `remotes/origin/archive/CORTEX-4.0`
**File Count**: 229+ documentation files

### docs-cortex-5.0
Documentation snapshot from CORTEX v5.0 branch
- Similar structure to v4.0 with incremental updates
- Additional phase completions and reports
- Refined governance implementations

**Date**: 2026-01-19
**Source Branch**: `remotes/origin/archive/CORTEX-5.0`

### docs-cortex-5.5
Final documentation snapshot from CORTEX v5.5 branch
- Most recent archived state of the hosted documentation
- Complete phase implementations
- Final governance and deployment strategies

**Date**: 2026-01-19
**Source Branch**: `remotes/origin/archive/CORTEX-5.5`

## Key Documentation Structure

Each version contains:

```
docs/
├── 00-README-START-HERE-*.md           # Entry point
├── CORTEX-*.md                          # Overview and architecture docs
├── PHASE-*.md                           # Phase-specific documentation
├── DEPLOYMENT-*.md                      # Deployment guides and specs
├── AC-*.md / AC-*.yaml                 # Acceptance criteria documentation
├── *-COMPLETION-REPORT.md              # Phase completion reports
├── _archive/
│   ├── ac-reports/                     # Organized AC completion reports
│   ├── analyses/                       # Deep-dive analysis documents
│   ├── phases/                         # Phase-specific archived docs
│   ├── summaries/                      # Executive summaries
│   └── _archived_reports/              # Historical reports
└── reports/reports/                    # Detailed reports with sub-organization
```

## Usage

### Accessing Specific Documentation
1. Browse directly in the filesystem to find documents
2. Most files are markdown (.md) or YAML (.yaml) format
3. Key entry points: `00-README-START-HERE-*.md` files in each version

### Viewing as Static HTML
These archives were previously served as static HTML. To view:
- Check the `gh-pages` branch for the original hosted version
- These markdown files can be viewed in any markdown viewer
- For full HTML rendering, refer to the original GitHub Pages deployment

### Historical Reference
Use these archives to:
- Track documentation evolution across versions
- Reference past implementation decisions
- Review completed phase documentation
- Understand governance policies from v4.0-5.5

## Branch Information

These documents were extracted from:
- `archive/CORTEX-4.0`: Historical branch preserving v4.0 state
- `archive/CORTEX-5.0`: Historical branch preserving v5.0 state
- `archive/CORTEX-5.5`: Historical branch preserving v5.5 state
- `archive/gh-pages`: Original GitHub Pages hosting branch

## Restoration Notes

These archives were created on **2026-01-20** by:
1. Extracting `docs/` folders from archive branches using git archive
2. Organizing into version-specific directories
3. Preserving complete documentation structure and hierarchy

To access the original branch content:
```bash
git checkout remotes/origin/archive/CORTEX-4.0
git checkout remotes/origin/archive/CORTEX-5.0
git checkout remotes/origin/archive/CORTEX-5.5
```

## Future Work

- Consider creating static HTML sites from these markdown archives
- Implement search indexing for archived documentation
- Set up redirects from hosted site to archive versions
- Create version comparison tools to track documentation changes

---

**Created**: 2026-01-20  
**Last Updated**: 2026-01-20  
**Archive Type**: Documentation preservation from GitHub Pages hosting
