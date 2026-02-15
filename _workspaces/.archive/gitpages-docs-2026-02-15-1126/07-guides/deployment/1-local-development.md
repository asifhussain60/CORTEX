# CORTEX Deployment Setup Guide

**AC-DEPLOY-ENHANCED-005-01: Comprehensive Deployment Documentation**

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start (3-Repository Example)](#quick-start-3-repository-example)
4. [Step-by-Step Setup](#step-by-step-setup)
5. [Configuration Reference](#configuration-reference)
6. [Troubleshooting](#troubleshooting)
7. [FAQ](#faq)
8. [Multi-Repository Example](#multi-repository-example)

---

## Architecture Overview

CORTEX is a multi-repository governance system with three core components:

### 1. **Central Hub** (`CORTEX` repository)
- **Purpose**: Central governance authority and rule management
- **Location**: `/Users/asifhussain/PROJECTS/CORTEX`
- **Components**:
  - MCP (Model Context Protocol) server on port 8000
  - Governance database (`cortex_brain/state/governance.db`)
  - Prompt version registry (`cortex_brain/tier0/prompt-versions.yaml`)
  - Repository registry (`cortex_brain/tier0/repo-registry.yaml`)
  - Release manifests (`cortex_brain/releases/v*.*.*/`)

### 2. **Repository Local** (Each connected repo)
- **Purpose**: Local governance configuration and prompts
- **Created**: `.github/prompts/` - governance prompts
- **Created**: `.github/tier0/` - local governance stub
- **Created**: `cortex-config.yaml` - hub connection and repo metadata

### 3. **IDE Integrations**
- **VS Code Extension**: Inline violation display, quick fixes, audit trail
- **Visual Studio LSP Adapter**: LSP server for VS integration, Python environment validation

---

## Prerequisites

### System Requirements
- **Python**: 3.9 or higher (for hub)
- **.NET Core**: 6.0 or higher (for LSP adapter, if using VS)
- **Node.js**: 14+ (for VS Code extension, if building)
- **Git**: 2.20+
- **Network**: HTTP connectivity between repositories and hub (default: localhost:8000)

### Initial Setup
```bash
# 1. Clone or navigate to CORTEX hub
cd /Users/asifhussain/PROJECTS/CORTEX

# 2. Verify Python environment
python3 --version  # Should be 3.9+

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize hub (one-time)
python scripts/setup_cortex_hub.py

# 5. Start MCP server
python -m cortex.api.server --port 8000
```

---

## Quick Start (3-Repository Example)

This example shows registering 3 repositories with CORTEX governance.

### Step 1: Start the Hub

```bash
# Terminal 1: Start CORTEX hub
cd /Users/asifhussain/PROJECTS/CORTEX
python -m cortex.api.server --port 8000

# Verify health
curl http://127.0.0.1:8000/health
# Response: {"status": "healthy", "timestamp": "2026-01-19T..."}
```

### Step 2: Register Repository #1 (Frontend)

```bash
# Terminal 2: Register frontend repo
cd ~/projects/frontend

# Run registration script
bash /Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh $(pwd)

# Verify setup
cat cortex-config.yaml
# Should show repo_id, mcp_endpoint, version

# Commit
git add cortex-config.yaml .github/
git commit -m "chore: Initial CORTEX registration"
```

### Step 3: Register Repository #2 (Backend)

```bash
# Terminal 3: Register backend repo
cd ~/projects/backend

bash /Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh $(pwd)
git add cortex-config.yaml .github/
git commit -m "chore: Initial CORTEX registration"
```

### Step 4: Register Repository #3 (Infrastructure)

```bash
# Terminal 4: Register infrastructure repo
cd ~/projects/infrastructure

bash /Users/asifhussain/PROJECTS/CORTEX/scripts/register-repo.sh $(pwd)
git add cortex-config.yaml .github/
git commit -m "chore: Initial CORTEX registration"
```

### Step 5: Verify Integration

```bash
# Check hub sees all repositories
curl http://127.0.0.1:8000/registry/repos
# Response: Lists frontend, backend, infrastructure

# Check audit trail
curl http://127.0.0.1:8000/audit/trail?limit=10
# Should show registration events for all 3 repos

# Test governance validation
curl -X POST http://127.0.0.1:8000/governance/validate \
  -H "Content-Type: application/json" \
  -d '{"repo_id": "frontend", "file": "src/main.ts"}'
```

### Step 6: Install IDE Extensions

**For VS Code:**
```bash
# Install CORTEX extension
code --install-extension cortex-dev.cortex-governance

# Reload VS Code
# Open each repository and verify:
# - Status bar shows "Connected to CORTEX"
# - Any governance violations appear as squiggly lines
# - Audit trail panel shows recent changes
```

**For Visual Studio:**
```bash
# LSP adapter runs automatically via LSP configuration
# Verify in VS Output window: "CORTEX LSP Adapter: Connected"
```

---

## Step-by-Step Setup

### 1. Initialize Hub Environment

```bash
cd /Users/asifhussain/PROJECTS/CORTEX

# Create Python venv if not exists
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install requirements
pip install -r requirements.txt

# Initialize hub (creates databases, directories, manifests)
python scripts/setup_cortex_hub.py
```

**Expected output:**
```
✓ Python version validated (3.9.x)
✓ Database initialized (4 tables created)
✓ Release directories created (v1.0.0)
✓ Prompt manifest generated
✓ Registry template created
✓ Health check configured
```

### 2. Configure MCP Server

**File**: `cortex/api/config.yaml`
```yaml
server:
  host: "127.0.0.1"
  port: 8000
  workers: 4
  timeout: 30

database:
  path: "cortex_brain/state/governance.db"
  
registry:
  path: "cortex_brain/tier0/repo-registry.yaml"

governance:
  rules_path: "cortex_brain/tier0/"
  cache_ttl_seconds: 300
  
logging:
  level: "INFO"
  format: "json"
```

### 3. Register Each Repository

**Command**: 
```bash
bash /path/to/CORTEX/scripts/register-repo.sh /path/to/repo
```

**What it does:**
- Creates `cortex-config.yaml` with repo metadata
- Sets up `.github/prompts/` with governance prompts
- Creates `.github/tier0/` governance stub
- Validates MCP connectivity
- Creates git commit with audit entry

**Verification**:
```bash
# Check config created
cat cortex-config.yaml

# Verify repo registered in hub
curl http://127.0.0.1:8000/registry/repos

# Check audit entry
curl http://127.0.0.1:8000/audit/trail?repo_id=<your-repo-id>
```

### 4. Enable IDE Integration

#### VS Code

1. **Install Extension**:
   - Open VS Code Extensions (Ctrl+Shift+X)
   - Search for "cortex-governance"
   - Click Install

2. **Configuration**:
   - Extension auto-detects `cortex-config.yaml`
   - Settings available in VS Code settings (search "cortex")

3. **Verify**:
   - Open repository in VS Code
   - Check status bar (bottom): should show "✓ Connected to CORTEX"
   - Open any file and look for governance violations (squiggly lines)

#### Visual Studio

1. **Install LSP Adapter**:
   ```bash
   # LSP adapter executable
   /Users/asifhussain/PROJECTS/CORTEX/extensions/cortex-lsp-adapter/bin/Release/cortex-lsp-adapter.exe
   ```

2. **Configure in VS**:
   - Tools → Options → Text Editor → C# → Advanced
   - Set "Language Server" to enabled
   - LSP Adapter connects automatically

3. **Verify**:
   - Open Output window (View → Output)
   - Look for "CORTEX LSP Adapter" tab
   - Should show: "✓ Connected to MCP hub"

---

## Configuration Reference

### `cortex-config.yaml` Fields

```yaml
# Repository Metadata
repo_id: "frontend"          # Unique ID, used in governance rules
repo_name: "Frontend"        # Human-readable name
repo_type: "source"          # Type: source, orchestrator, tool, knowledge

# CORTEX Hub Configuration
mcp_endpoint: "http://127.0.0.1:8000"  # Hub URL
mcp_health_check_interval_seconds: 30  # Health check frequency
mcp_timeout_seconds: 10                 # Request timeout

# Version Management
version: "1.0.0"             # Repo governance version
min_hub_version: "1.0.0"     # Minimum hub version required

# Governance Configuration
governance_enabled: true     # Enable governance checks
audit_trail_enabled: true    # Log all operations
isolation_mode: "strict"     # strict, moderate, permissive

# Offline Mode
offline_mode_enabled: false  # Fallback if hub unreachable
offline_queue_max_items: 1000

# Feature Flags
enable_version_negotiation: true   # Use version negotiation
enable_cross_repo_access: false    # Block cross-repo access
```

### `.github/tier0/` Contents

```
.github/tier0/
├── README.md                 # Local governance reference
├── GOVERNANCE-LOCAL.yaml     # (optional) Local rule overrides
└── VERSION-COMPAT.yaml       # (optional) Version compatibility
```

### Hub Database Schema

**4 Tables in `governance.db`:**

1. **governance_rules**: Stores active governance rules
2. **audit_trail**: Complete audit log of all operations
3. **version_tracking**: Prompt/config version history
4. **sessions**: Active repository sessions

---

## Troubleshooting

### Issue: "Connection refused" when registering repo

**Cause**: Hub not running

**Solution**:
```bash
# In Terminal 1, verify hub is running
curl http://127.0.0.1:8000/health

# If not running, start it:
cd /Users/asifhussain/PROJECTS/CORTEX
python -m cortex.api.server --port 8000
```

### Issue: "cortex-config.yaml not found" in IDE

**Cause**: File not created or in wrong location

**Solution**:
```bash
# Re-run registration script
bash /path/to/CORTEX/scripts/register-repo.sh $(pwd)

# Verify file exists
ls -la cortex-config.yaml

# Check content
cat cortex-config.yaml
```

### Issue: VS Code extension not connecting

**Cause**: Hub endpoint misconfigured

**Solution**:
1. Check `cortex-config.yaml` has correct `mcp_endpoint`
2. Verify hub is running: `curl http://127.0.0.1:8000/health`
3. Reload VS Code: `Ctrl+Shift+P → Developer: Reload Window`
4. Check status bar (bottom-right) for connection status

### Issue: LSP adapter crashes on startup

**Cause**: Python environment validation failed

**Solution**:
```bash
# Check Python version
python3 --version  # Should be 3.9+

# Check required packages
python3 -c "import yaml; import requests"

# Verify .NET version
dotnet --version  # Should be 6.0+
```

### Issue: Governance violations not showing

**Cause**: Rules not loaded or file not validated

**Solution**:
```bash
# Manually validate file
curl -X POST http://127.0.0.1:8000/governance/validate \
  -H "Content-Type: application/json" \
  -d '{"repo_id": "your-repo-id", "file": "src/main.ts"}'

# Should return violations if any exist
# If empty, check rules are registered in hub
```

### Issue: Isolation violation blocking legitimate access

**Cause**: Strict isolation mode blocking cross-repo reference

**Solution**:
```bash
# Option 1: Switch to moderate isolation
# Edit cortex-config.yaml:
isolation_mode: "moderate"

# Option 2: Whitelist the cross-repo access
# Contact hub administrator to update governance rules

# Option 3: Use repository bridge pattern
# Create dedicated bridge repository for shared resources
```

---

## FAQ

### Q: Do I need to restart the hub to register new repositories?
**A**: No. Repositories can be registered dynamically. The hub discovers them via the registry file.

### Q: Can repositories be in offline mode?
**A**: Yes. If `mcp_endpoint` is unreachable, repos enter offline mode using cached rules. They sync when reconnected.

### Q: What happens if two repositories try to access the same file?
**A**: Governed by `isolation_mode`. In strict mode (default), access is blocked with audit log entry. In moderate mode, access is logged but allowed.

### Q: Can I use CORTEX with repositories on different machines?
**A**: Yes. Set `mcp_endpoint` to the hub's network address (e.g., `http://hub.example.com:8000`). Hub must be accessible over network.

### Q: How do I backup governance data?
**A**: Backup these directories:
```bash
cortex_brain/state/              # Database
cortex_brain/tier0/              # Rules and registry
cortex_brain/releases/           # Version manifests
```

### Q: Can I migrate between CORTEX versions?
**A**: Yes. Version negotiation handles compatibility. Hub negotiates with each repo's `version` field and `min_hub_version` requirement.

### Q: What's the performance impact on repositories?
**A**: Minimal (<50ms per file validation). Rules are cached. Health checks run every 30s (configurable).

### Q: How do I remove a repository from governance?
**A**: 
```bash
# In the repository:
git rm cortex-config.yaml .github/tier0 .github/prompts
git commit -m "chore: Remove CORTEX governance"

# In hub, remove from registry:
# Edit cortex_brain/tier0/repo-registry.yaml
# Remove the repository entry
```

---

## Multi-Repository Example

**Setup**: 5 repositories across 3 teams

```
hub (CORTEX)
│
├── frontend (Team A)
│   ├── repo_id: "frontend"
│   └── isolation_mode: "strict"
│
├── backend (Team A)
│   ├── repo_id: "backend"
│   └── isolation_mode: "strict"
│
├── mobile (Team B)
│   ├── repo_id: "mobile"
│   └── isolation_mode: "moderate"
│
├── infrastructure (Team C)
│   ├── repo_id: "infrastructure"
│   └── isolation_mode: "moderate"
│
└── data-platform (Team C)
    ├── repo_id: "data-platform"
    └── isolation_mode: "strict"
```

### Governance Rules

**Rule 1**: Data team accesses only data-platform
```yaml
rule_id: "DATA_ACCESS_001"
repo_id_source: "data-platform"
repo_id_target: "infrastructure"  # Can access infra
isolation_enforcement: "warn"
```

**Rule 2**: Frontend cannot directly access backend database
```yaml
rule_id: "ARCH_BOUNDARY_001"
repo_id_source: "frontend"
resource_pattern: "backend/database/*"
enforcement: "block"
```

### Audit Trail Example

```bash
curl http://127.0.0.1:8000/audit/trail?limit=20

[
  {
    "timestamp": "2026-01-19T14:32:15Z",
    "operation": "repo_registered",
    "actor": "developer@company.com",
    "repo_id": "frontend",
    "status": "success"
  },
  {
    "timestamp": "2026-01-19T14:33:22Z",
    "operation": "file_validated",
    "actor": "vs-code-extension",
    "repo_id": "frontend",
    "file": "src/main.ts",
    "violations": 2
  },
  {
    "timestamp": "2026-01-19T14:34:10Z",
    "operation": "isolation_violation_blocked",
    "actor": "lsp-adapter",
    "repo_id": "frontend",
    "target_repo": "backend",
    "operation": "file_read",
    "status": "blocked"
  }
]
```

---

## Next Steps

1. **Start Hub**: Run `python -m cortex.api.server --port 8000`
2. **Register Repos**: Use `scripts/register-repo.sh` for each repository
3. **Install Extensions**: VS Code extension, VS LSP adapter
4. **Configure Rules**: Set governance rules in hub
5. **Monitor**: Check audit trail and health status

## Support

For issues or questions:
- Check [Troubleshooting](#troubleshooting) section
- Review [FAQ](#faq) for common questions
- Check hub logs: `cortex_brain/state/cortex.log`
- Examine audit trail: `curl http://127.0.0.1:8000/audit/trail`

---

**Last Updated**: January 19, 2026  
**Version**: 1.0.0  
**Status**: Production Ready
