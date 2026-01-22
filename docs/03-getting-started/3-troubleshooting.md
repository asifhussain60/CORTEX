# Troubleshooting Setup

**Last Updated:** 2026-01-20  
**Version:** 1.0.0  
**Status:** Production Ready  
**Audience:** Developers, Operators

## Overview

This guide covers common setup and operational issues with CORTEX. Use the diagnostic commands and solutions below to resolve problems quickly.

---

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Installation Issues](#installation-issues)
3. [Configuration Issues](#configuration-issues)
4. [Governance Issues](#governance-issues)
5. [MCP Server Issues](#mcp-server-issues)
6. [API Issues](#api-issues)
7. [Performance Issues](#performance-issues)
8. [Database Issues](#database-issues)
9. [Getting Help](#getting-help)

---

## Quick Diagnostics

### Health Check Command

Run a comprehensive health check:

```bash
cortex health check --verbose

# Expected output:
# ✓ Python environment: OK (3.11.4)
# ✓ Dependencies: OK (all 47 packages installed)
# ✓ Configuration: OK (cortex-config.yaml valid)
# ✓ Database: OK (governance.db accessible)
# ✓ Governance: OK (29 CORE rules loaded)
# ✓ MCP Server: OK (stdio transport ready)
# ✓ API Server: OK (port 8080 available)
```

### Component Status

Check individual components:

```bash
# Check governance
cortex governance status

# Check database
cortex db status

# Check MCP server
cortex mcp status

# Check configuration
cortex config validate
```

### Log Analysis

View recent logs:

```bash
# All logs
cortex logs --tail 50

# Errors only
cortex logs --level ERROR --tail 20

# Specific component
cortex logs --component governance --tail 30
```

---

## Installation Issues

### Python Version Mismatch

**Symptom:**
```
ERROR: This package requires Python >=3.9
```

**Solution:**
```bash
# Check Python version
python --version

# Use pyenv to install correct version
pyenv install 3.11.4
pyenv local 3.11.4

# Or use conda
conda create -n cortex python=3.11
conda activate cortex
```

### Dependency Conflicts

**Symptom:**
```
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed
```

**Solution:**
```bash
# Create fresh virtual environment
python -m venv venv --clear
source venv/bin/activate

# Install with fresh resolver
pip install --upgrade pip
pip install -r requirements.txt --no-cache-dir
```

### Missing System Dependencies

**Symptom (macOS):**
```
ERROR: fatal error: 'sqlite3.h' file not found
```

**Solution:**
```bash
# macOS
xcode-select --install
brew install sqlite3

# Linux (Ubuntu/Debian)
sudo apt-get install libsqlite3-dev python3-dev

# Linux (RHEL/CentOS)
sudo yum install sqlite-devel python3-devel
```

### Permission Errors

**Symptom:**
```
ERROR: Permission denied: '/usr/local/lib/python3.11/site-packages'
```

**Solution:**
```bash
# Never use sudo pip! Use virtual environment instead
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Or use user install
pip install --user -r requirements.txt
```

### Docker Issues

**Symptom:**
```
ERROR: Cannot connect to the Docker daemon
```

**Solution:**
```bash
# macOS/Windows: Start Docker Desktop

# Linux: Start Docker service
sudo systemctl start docker

# Add user to docker group (Linux)
sudo usermod -aG docker $USER
newgrp docker
```

---

## Configuration Issues

### Missing Configuration File

**Symptom:**
```
ERROR: Configuration file not found: cortex-config.yaml
```

**Solution:**
```bash
# Create from template
cp cortex-config.example.yaml cortex-config.yaml

# Or initialize
cortex config init
```

### Invalid YAML Syntax

**Symptom:**
```
ERROR: YAML parse error at line 42: mapping values are not allowed here
```

**Solution:**
```bash
# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('cortex-config.yaml'))"

# Common fixes:
# - Ensure consistent indentation (2 spaces)
# - Quote strings with special characters
# - Check for tabs (use spaces only)
```

### Environment Variable Not Set

**Symptom:**
```
ERROR: Required environment variable CORTEX_DB_PATH not set
```

**Solution:**
```bash
# Set in shell
export CORTEX_DB_PATH=/path/to/governance.db

# Or in .env file
echo "CORTEX_DB_PATH=/path/to/governance.db" >> .env

# Load .env file
source .env
```

### Configuration Schema Validation

**Symptom:**
```
ERROR: Configuration validation failed: 'governance_tier' must be between 0 and 3
```

**Solution:**
```yaml
# cortex-config.yaml - Correct values

governance:
  tier: 0  # Must be 0, 1, 2, or 3
  
orchestrators:
  default:
    max_turns: 10  # Must be positive integer
    timeout: 30.0  # Must be positive float
```

---

## Governance Issues

### Database Not Initialized

**Symptom:**
```
ERROR: Governance database not found or corrupted
```

**Solution:**
```bash
# Initialize database
cortex governance init

# Or with specific path
cortex governance init --db-path ./cortex_brain/state/governance.db

# Verify
cortex governance status
```

### Rules Not Loading

**Symptom:**
```
ERROR: No governance rules found
WARNING: Operating without governance protection
```

**Solution:**
```bash
# Load default rules
cortex governance load-defaults

# Or load from file
cortex governance load --rules-file ./cortex_brain/tier0/skull_rules.yaml

# Verify rules loaded
cortex governance list-rules
```

### Rule Violation Blocking

**Symptom:**
```
ERROR: Governance rule CORE-001 violated: Operation not in safe list
```

**Solution:**
```bash
# Check rule details
cortex governance show-rule CORE-001

# Check what operations are allowed
cortex governance list-safe-operations

# If legitimate, add to safe list (requires Tier 0 access)
cortex governance add-safe-operation "my_operation" --approval-required
```

### Audit Trail Integrity

**Symptom:**
```
ERROR: Audit trail hash chain broken at entry 4523
```

**Solution:**
```bash
# Verify audit trail
cortex audit verify

# If broken, this is a serious issue - investigate before repair
cortex audit show --entry 4523 --context 5

# Create incident report
cortex audit incident --entry 4523 --description "Hash chain investigation"
```

---

## MCP Server Issues

### Server Won't Start

**Symptom:**
```
ERROR: MCP server failed to initialize
```

**Solution:**
```bash
# Check dependencies
pip list | grep mcp

# Verify configuration
cortex mcp validate-config

# Start with debug logging
CORTEX_LOG_LEVEL=DEBUG cortex mcp start
```

### Tool Not Found

**Symptom:**
```
ERROR: Unknown tool: cortex_analyze
```

**Solution:**
```bash
# List available tools
cortex mcp list-tools

# Check tool registration
cortex mcp show-tool cortex_analyze

# Reload tools
cortex mcp reload-tools
```

### JSON-RPC Errors

**Symptom:**
```json
{"jsonrpc": "2.0", "error": {"code": -32600, "message": "Invalid Request"}}
```

**Solution:**
```bash
# Validate request format
# Ensure all required fields present:
# - jsonrpc: "2.0"
# - method: string
# - id: string or number
# - params: object (optional)

# Test with valid request
echo '{"jsonrpc":"2.0","method":"tools/list","id":1}' | cortex mcp --stdio
```

### VS Code Integration Issues

**Symptom:**
```
VS Code cannot connect to CORTEX MCP server
```

**Solution:**
1. Check VS Code MCP configuration:
```json
// .vscode/settings.json
{
    "mcp.servers": {
        "cortex": {
            "command": "cortex",
            "args": ["mcp", "start", "--stdio"],
            "env": {
                "CORTEX_CONFIG": "./cortex-config.yaml"
            }
        }
    }
}
```

2. Restart VS Code
3. Check Output panel > MCP for errors

---

## API Issues

### Server Won't Start

**Symptom:**
```
ERROR: Address already in use: 0.0.0.0:8080
```

**Solution:**
```bash
# Find process using port
lsof -i :8080

# Kill process
kill -9 <PID>

# Or use different port
cortex api start --port 8081
```

### Authentication Failures

**Symptom:**
```
HTTP 401 Unauthorized
```

**Solution:**
```bash
# Check API key is set
echo $CORTEX_API_KEY

# Generate new key
cortex api generate-key

# Test with key
curl -H "Authorization: Bearer $CORTEX_API_KEY" http://localhost:8080/health
```

### CORS Errors

**Symptom:**
```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution:**
```yaml
# cortex-config.yaml
api:
  cors:
    enabled: true
    origins:
      - "http://localhost:3000"
      - "https://your-frontend.com"
    methods:
      - GET
      - POST
      - PUT
      - DELETE
```

### Timeout Errors

**Symptom:**
```
ERROR: Request timeout after 30 seconds
```

**Solution:**
```yaml
# cortex-config.yaml
api:
  timeout:
    read: 60.0  # Increase from default 30
    write: 60.0
    
orchestrators:
  default:
    timeout_seconds: 60.0
```

---

## Performance Issues

### Slow Startup

**Symptom:**
```
CORTEX takes >30 seconds to start
```

**Solution:**
```bash
# Profile startup
cortex --profile start

# Common causes:
# 1. Large governance database - optimize with vacuum
cortex db vacuum

# 2. Many rules loading - use lazy loading
# cortex-config.yaml
governance:
  lazy_load: true

# 3. Network timeouts - check external services
cortex health check --verbose
```

### High Memory Usage

**Symptom:**
```
Memory usage exceeds 2GB
```

**Solution:**
```yaml
# cortex-config.yaml
performance:
  max_memory_mb: 1024
  gc_threshold: 0.8
  
caching:
  max_entries: 1000
  ttl_seconds: 300
```

### Slow Queries

**Symptom:**
```
Governance checks taking >5 seconds
```

**Solution:**
```bash
# Analyze slow queries
cortex db analyze

# Add indexes
cortex db optimize

# Check rule complexity
cortex governance analyze-rules
```

---

## Database Issues

### Database Locked

**Symptom:**
```
ERROR: database is locked
```

**Solution:**
```bash
# Check for other processes
lsof | grep governance.db

# Set busy timeout
# cortex-config.yaml
database:
  busy_timeout_ms: 5000
  
# Or use WAL mode for better concurrency
cortex db enable-wal
```

### Database Corruption

**Symptom:**
```
ERROR: database disk image is malformed
```

**Solution:**
```bash
# Check integrity
cortex db check

# If corrupted, restore from backup
cortex db restore --backup ./backups/governance.db.bak

# If no backup, try recovery
cortex db recover --output ./governance_recovered.db
```

### Migration Issues

**Symptom:**
```
ERROR: Database schema version mismatch
```

**Solution:**
```bash
# Check current version
cortex db version

# Run migrations
cortex db migrate

# Or force specific version
cortex db migrate --target 15
```

---

## Getting Help

### Diagnostic Bundle

Create a diagnostic bundle for support:

```bash
cortex diagnostic bundle --output cortex-diagnostic.zip

# This includes:
# - Configuration (sanitized)
# - Recent logs
# - System information
# - Health check results
```

### Log Levels

Increase logging for debugging:

```bash
# Via environment variable
export CORTEX_LOG_LEVEL=DEBUG

# Via config
# cortex-config.yaml
logging:
  level: DEBUG
  format: detailed
```

### Community Resources

- **Documentation:** [docs/](../0-README.md)
- **Known Issues:** [known-issues.md](../05-reference/known-issues.md)
- **FAQ:** [faq.md](../05-reference/faq.md)

### Reporting Issues

When reporting issues, include:

1. **CORTEX version:** `cortex --version`
2. **Python version:** `python --version`
3. **Operating system:** `uname -a`
4. **Error message:** Full stack trace
5. **Steps to reproduce:** Minimal example
6. **Configuration:** Sanitized config (no secrets)

---

## Common Error Reference

| Error Code | Description | Quick Fix |
|------------|-------------|-----------|
| `CORTEX-001` | Configuration not found | `cortex config init` |
| `CORTEX-002` | Database not initialized | `cortex governance init` |
| `CORTEX-003` | Governance rule violation | Check `cortex audit list` |
| `CORTEX-004` | MCP protocol error | Validate JSON-RPC format |
| `CORTEX-005` | Authentication failed | Check API key |
| `CORTEX-006` | Timeout exceeded | Increase timeout in config |
| `CORTEX-007` | Database locked | Check for other processes |
| `CORTEX-008` | Hash chain broken | Run `cortex audit verify` |
| `CORTEX-009` | Orchestrator not found | Check registry |
| `CORTEX-010` | Dependency missing | `pip install -r requirements.txt` |

---

**Next:** [System Overview](../02-architecture/1-system-overview.md)
