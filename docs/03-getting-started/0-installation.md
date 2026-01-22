# Installation & Setup

**Last Updated:** 2026-01-20  
**Audience:** All Users  
**Prerequisites:** None

## Overview

This guide covers installing CORTEX for local development. CORTEX is a Python-based intelligent orchestration platform requiring Python 3.9+ and SQLite.

## System Requirements

### Minimum Requirements

| Component | Requirement |
|-----------|-------------|
| **Python** | 3.9 or higher (3.11+ recommended) |
| **OS** | macOS, Linux, Windows (WSL recommended) |
| **Memory** | 4GB RAM minimum |
| **Disk** | 500MB free space |
| **Network** | Internet for initial setup |

### Recommended Requirements

| Component | Recommendation |
|-----------|----------------|
| **Python** | 3.11.x |
| **Memory** | 8GB+ RAM |
| **Disk** | 2GB+ free space |
| **Editor** | VS Code with Python extension |

## Installation Steps

### 1. Clone the Repository

```bash
# Clone CORTEX
git clone https://github.com/cortex-ai/cortex.git
cd cortex
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv .venv

# Activate (macOS/Linux)
source .venv/bin/activate

# Activate (Windows)
.venv\Scripts\activate
```

### 3. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt

# Verify installation
python -c "import cortex; print('CORTEX installed successfully')"
```

### 4. Initialize Database

```bash
# Initialize governance database
python scripts/setup_cortex_hub.py

# Verify database
python -c "import sqlite3; conn = sqlite3.connect('governance.db'); print(f'Database ready: {conn.execute(\"SELECT COUNT(*) FROM audit_log\").fetchone()[0]} entries')"
```

### 5. Verify Installation

```bash
# Run health check
python -m cortex.cli system health

# Expected output:
# CORTEX System Health
# ────────────────────
# ✅ Governance DB: connected
# ✅ Domain Brain: operational
# ✅ Orchestrator Registry: ready
# Overall: HEALTHY ✅
```

## Configuration

### Default Configuration

CORTEX uses `cortex-config.yaml` for configuration:

```yaml
# cortex-config.yaml
version: "1.0.0"
environment: "development"

# Governance settings
governance:
  database: "governance.db"
  strict_mode: true
  audit_enabled: true

# Orchestrator settings
orchestrator:
  timeout_seconds: 300
  max_retries: 3
  complexity_gate:
    enabled: true
    trivial_threshold: 0.15
    simple_threshold: 0.35

# MCP Server settings
mcp:
  enabled: true
  transport: "stdio"

# Logging settings
logging:
  level: "INFO"
  format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
```

### Environment Variables

Override configuration via environment variables:

```bash
# Set log level
export CORTEX_LOG_LEVEL=DEBUG

# Set database path
export CORTEX_DB_PATH=/path/to/governance.db

# Set config file
export CORTEX_CONFIG=/path/to/cortex-config.yaml
```

## IDE Setup

### VS Code

1. **Install Extensions:**
   - Python (ms-python.python)
   - Pylance (ms-python.vscode-pylance)
   - GitHub Copilot (GitHub.copilot) - optional

2. **Configure Workspace Settings:**

```json
// .vscode/settings.json
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/bin/python",
  "python.analysis.typeCheckingMode": "basic",
  "python.analysis.extraPaths": ["${workspaceFolder}/src"],
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests/"]
}
```

3. **Configure Launch Settings:**

```json
// .vscode/launch.json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "CORTEX MCP Server",
      "type": "python",
      "request": "launch",
      "module": "src.mcp",
      "console": "integratedTerminal"
    },
    {
      "name": "CORTEX CLI",
      "type": "python",
      "request": "launch",
      "module": "cortex.cli",
      "args": ["system", "health"],
      "console": "integratedTerminal"
    }
  ]
}
```

### PyCharm

1. Open the project folder
2. Configure Python interpreter: `.venv/bin/python`
3. Mark `src/` as Sources Root
4. Configure pytest as test runner

## MCP Client Setup

### Claude Desktop

Add to Claude Desktop configuration:

```json
// ~/Library/Application Support/Claude/claude_desktop_config.json
{
  "mcpServers": {
    "cortex": {
      "command": "python",
      "args": ["-m", "src.mcp"],
      "cwd": "/path/to/cortex"
    }
  }
}
```

### VS Code (MCP Extension)

Add to VS Code settings:

```json
// settings.json
{
  "mcp.servers": {
    "cortex": {
      "command": "python",
      "args": ["-m", "src.mcp"],
      "workingDirectory": "${workspaceFolder}"
    }
  }
}
```

## Verify Complete Setup

Run the verification script:

```bash
# Run all verification checks
python -c "
from pathlib import Path
import sys

checks = []

# Check Python version
checks.append(('Python 3.9+', sys.version_info >= (3, 9)))

# Check virtual environment
checks.append(('Virtual env active', hasattr(sys, 'prefix')))

# Check dependencies
try:
    import yaml
    import sqlite3
    checks.append(('Dependencies installed', True))
except ImportError:
    checks.append(('Dependencies installed', False))

# Check database
db_path = Path('governance.db')
checks.append(('Governance DB exists', db_path.exists()))

# Check config
config_path = Path('cortex-config.yaml')
checks.append(('Config file exists', config_path.exists()))

# Print results
print('CORTEX Installation Verification')
print('=' * 40)
for name, passed in checks:
    status = '✅' if passed else '❌'
    print(f'{status} {name}')

all_passed = all(passed for _, passed in checks)
print('=' * 40)
print(f\"Overall: {'READY' if all_passed else 'ISSUES FOUND'}\")
"
```

## Troubleshooting Installation

### Common Issues

#### Python Version Error

```
Error: Python 3.9+ required
```

**Solution:**
```bash
# Check Python version
python --version

# Install Python 3.11 (macOS with Homebrew)
brew install python@3.11

# Use specific version
python3.11 -m venv .venv
```

#### Missing Dependencies

```
ModuleNotFoundError: No module named 'yaml'
```

**Solution:**
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

#### Database Connection Error

```
Error: Unable to connect to governance.db
```

**Solution:**
```bash
# Reinitialize database
python scripts/setup_cortex_hub.py --force

# Check file permissions
chmod 644 governance.db
```

#### MCP Server Won't Start

```
Error: MCP server failed to initialize
```

**Solution:**
```bash
# Check for port conflicts
lsof -i :8000

# Run with debug logging
CORTEX_LOG_LEVEL=DEBUG python -m src.mcp
```

## Next Steps

After successful installation:

1. **[Quick Start](1-quickstart.md)** - 15-minute hands-on tutorial
2. **[First Orchestrator](2-first-orchestrator.md)** - Create your first orchestrator
3. **[System Overview](../02-architecture/1-system-overview.md)** - Understand the architecture

## Related Documentation

- [Local Development](../04-guides/deployment/1-local-development.md) - Development environment setup
- [Troubleshooting](../04-guides/operations/4-troubleshooting.md) - Common issues
- [FAQ](../05-reference/faq.md) - Frequently asked questions
