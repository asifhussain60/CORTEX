# CORTEX 7.0

Production-grade AI assistant framework with 3-tier governance model.

## Quick Start

```bash
# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Unix)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Use toolkit
python -m src.tools.toolkit version
```

## Structure

```
CORTEX/
├── cortex-brain/          # 3-Tier Governance
│   ├── tier0/             # SKULL rules (immutable)
│   ├── tier1/             # Business rules (mutable)
│   ├── tier2/             # Engineering standards
│   └── tier3/             # Domain patterns
├── src/                   # Source code
│   ├── core/              # Shared utilities
│   ├── infrastructure/    # Audit, storage
│   ├── orchestrators/     # Workflow orchestration
│   ├── mcp/               # MCP integration
│   └── tools/             # CLI tools
├── tests/                 # Test suite
│   ├── unit/              # Unit tests
│   └── integration/       # Integration tests
└── .github/roadmap/       # Implementation roadmap
    ├── cortex-master.yaml # Single Source of Truth
    └── phases/            # Phase definitions
```

## Governance Tiers

| Tier | Name | Mutability | Purpose |
|------|------|------------|---------|
| 0 | SKULL | Immutable | Core protection rules |
| 1 | Business | Mutable | Acceptance criteria |
| 2 | Engineering | Mutable | Code standards |
| 3 | Domain | Mutable | Domain patterns |

## Key Principles

1. **Result Pattern** - All functions return `Result[T]` for explicit error handling
2. **Path Portability** - No hardcoded paths, use `get_project_root()`
3. **Audit-First** - All operations logged with hash chain integrity
4. **TDD Required** - Tests before implementation

## Author

Asif Hussain  
Copyright © 2025-2026 Asif Hussain. All rights reserved.
