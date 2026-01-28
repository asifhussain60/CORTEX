# CORTEX

**CO**gnitive **R**eal-**T**ime **EX**ecution System — AI-powered development orchestrator.

## Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

# 2. Set up Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Configure git hooks (IMPORTANT for team collaboration)
make setup-hooks
# or: ./scripts/setup-hooks.sh
```

## Git Hooks

CORTEX uses automated verification hooks to ensure code quality:

| Hook | Trigger | Checks |
|------|---------|--------|
| `pre-commit` | Before commit | CORE-011 (type hints), CORE-013 (no bare except), CORE-028 (naming), CORE-038 (file placement) |
| `pre-push` | Before push | 12 production readiness checks including prompt-code synchronization |

**After cloning, run:**
```bash
make setup-hooks
```

This configures Git to use version-controlled hooks from `.cortex/hooks/`.

## Development Commands

```bash
make help          # Show all commands
make verify        # Run production readiness verification
make test          # Run wiring tests
make test-all      # Run all tests
```

## Documentation

- [Getting Started](docs/01-getting-started/)
- [Architecture](docs/02-architecture/)
- [API Reference](docs/06-api-reference/)

## License

See LICENSE file.
