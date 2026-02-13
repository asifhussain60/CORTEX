# Development Setup

> Auto-generated from cortex-impl-map.yaml on 2026-01-21

**Last Updated:** 2026-01-21  
**Audience:** Contributors, Developers

## Prerequisites

| Requirement | Version | Notes |
|-------------|---------|-------|
| Python | 3.11+ | 3.12 recommended |
| Git | 2.40+ | For history analysis |
| VS Code | Latest | Recommended IDE |

## Quick Setup

```powershell
# 1. Clone repository
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX

# 2. Create virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1  # Windows
# source .venv/bin/activate   # Linux/macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Verify installation
pytest tests/ -v --co -q | Select-Object -First 20
```

## Project Structure

```
CORTEX/
├── cortex/                 # Main application package (413 files)
│   ├── api/               # API layer
│   ├── core/              # Core business logic
│   ├── mcp/               # MCP server and tools
│   └── orchestrators/     # Domain orchestrators
├── cortex_brain/          # State and governance (41 files)
│   ├── tier0/             # Core rules (immutable)
│   ├── tier1/             # Domain rules
│   ├── tier2/             # Context rules
│   └── state/             # governance.db
├── tests/                 # Test suite (409 files)
├── docs/                  # Documentation
└── _workspaces/roadmap/   # Implementation tracking
```

## IDE Configuration

### VS Code Extensions

Install recommended extensions:

```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.vscode-pylance",
    "charliermarsh.ruff",
    "tamasfe.even-better-toml"
  ]
}
```

### settings.json

```json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
  "python.analysis.typeCheckingMode": "basic",
  "editor.formatOnSave": true,
  "[python]": {
    "editor.defaultFormatter": "charliermarsh.ruff"
  }
}
```

## Running Tests

```powershell
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_ac_ar_010_01_design.py -v

# Run with coverage
pytest tests/ --cov=cortex --cov-report=html

# Run only unit tests
pytest tests/unit/ -v

# Run with specific marker
pytest tests/ -m "not slow" -v
```

## Database Setup

CORTEX uses SQLite for governance state:

```powershell
# Location: cortex_brain/state/governance.db
# Created automatically on first run

# Verify database
python -c "import sqlite3; conn = sqlite3.connect('cortex_brain/state/governance.db'); print(conn.execute('SELECT name FROM sqlite_master WHERE type=\"table\"').fetchall())"
```

## MCP Server

Run the MCP server for AI integration:

```powershell
# Start MCP server (stdio transport)
python -m cortex.mcp.server

# Test with echo
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | python -m cortex.mcp.server
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CORTEX_ENV` | `development` | Environment mode |
| `CORTEX_LOG_LEVEL` | `INFO` | Logging verbosity |
| `CORTEX_DB_PATH` | `cortex_brain/state/governance.db` | Database location |

## Troubleshooting

### Import Errors

```powershell
# Ensure PYTHONPATH includes project root
$env:PYTHONPATH = "$(Get-Location)"
```

### Test Collection Errors

```powershell
# Check for syntax errors
python -m py_compile cortex/core/__init__.py

# Validate imports
python scripts/validate_imports.py
```

### Database Locked

```powershell
# Close other connections
Get-Process python | Stop-Process -Force

# Reset database
Remove-Item cortex_brain/state/governance.db
pytest tests/ -v  # Recreates DB
```

## Related

- [Testing Strategy](3-testing-strategy.md)
- [Code Style Guide](4-code-style-guide.md)
- [Contributing Guidelines](1-contributing-guidelines.md)
