# CORTEX Deployment Troubleshooting Guide

**AC-DEPLOY-ENHANCED-005-01: Comprehensive Deployment Documentation**

## Common Issues and Solutions

### Connection Issues

#### Problem: "Connection refused" when connecting to hub

```
Error: Failed to connect to http://127.0.0.1:8000
```

**Diagnosis**:
```bash
# Check if hub process is running
ps aux | grep "cortex.api.server"

# Try health check
curl http://127.0.0.1:8000/health
```

**Solutions**:

1. **Hub not started**:
```bash
# Start hub in foreground to see errors
cd /Users/asifhussain/PROJECTS/CORTEX
python -m cortex.api.server --port 8000 --debug
```

2. **Hub on wrong port**:
```bash
# Check cortex-config.yaml for correct endpoint
cat cortex-config.yaml | grep mcp_endpoint

# Verify hub is on that port
netstat -an | grep 8000  # or lsof -i :8000
```

3. **Firewall blocking**:
```bash
# On macOS, allow Python in firewall
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --setglobalstate on
```

4. **Hub crashed**:
```bash
# Check hub logs
tail -50 cortex_brain/state/cortex.log

# Restart hub
python -m cortex.api.server --port 8000
```

---

#### Problem: Timeout connecting to hub

```
Error: Connection timeout after 10s
```

**Diagnosis**:
```bash
# Check network connectivity
ping 127.0.0.1

# Check hub response time
time curl -w "@curl-format.txt" -o /dev/null -s http://127.0.0.1:8000/health
```

**Solutions**:

1. **Increase timeout** in `cortex-config.yaml`:
```yaml
mcp_timeout_seconds: 30  # Increased from 10
```

2. **Hub overloaded**:
```bash
# Check hub CPU/memory
top  # Or Activity Monitor on macOS

# Increase hub workers
python -m cortex.api.server --port 8000 --workers 8
```

3. **Network latency**:
```bash
# If hub on remote machine, check routing
traceroute <hub-ip>

# Reduce health check frequency to reduce load
mcp_health_check_interval_seconds: 60
```

---

### Repository Registration Issues

#### Problem: "cortex-config.yaml already exists, skipping"

```
⚠ cortex-config.yaml already exists, skipping creation
```

**Diagnosis**:
```bash
cat cortex-config.yaml
```

**Solutions**:

1. **Update existing config**:
```bash
# Edit file directly
vim cortex-config.yaml

# Or delete and re-run registration
rm cortex-config.yaml
bash /path/to/scripts/register-repo.sh $(pwd)
```

2. **Idempotent registration** (expected behavior):
```bash
# Second run should be safe
bash /path/to/scripts/register-repo.sh $(pwd)
# Should complete successfully with minimal changes
```

---

#### Problem: ".github/prompts directory already exists"

**Diagnosis**:
```bash
ls -la .github/prompts/
```

**Solutions**:

1. **Verify symlinks** (macOS/Linux):
```bash
# Check if files are symlinks
ls -la .github/prompts/
# Output should show: lrwxr-xr-x ... -> /path/to/hub/...
```

2. **Verify copies** (Windows):
```bash
# Check if files are copies
dir .github\prompts\
# Files should be regular files, not shortcuts
```

3. **Clean and re-register**:
```bash
rm -rf .github/
bash /path/to/scripts/register-repo.sh $(pwd)
```

---

#### Problem: Repo not showing in hub registry

```
curl http://127.0.0.1:8000/registry/repos
# Response: []  (empty)
```

**Diagnosis**:
```bash
# Check repo_id in local config
grep repo_id cortex-config.yaml

# Check if registered in hub
grep -r "repo_id" /path/to/hub/cortex_brain/tier0/repo-registry.yaml
```

**Solutions**:

1. **Registration incomplete**:
```bash
# Re-run registration with verbose output
bash -x /path/to/scripts/register-repo.sh $(pwd)

# Check for errors in output
```

2. **Hub registry stale** (requires hub restart):
```bash
# The hub caches registry on startup
# Restart hub to reload
pkill -f "cortex.api.server"
sleep 1
python -m cortex.api.server --port 8000
```

3. **Git commit not created**:
```bash
git log --oneline | head -5
# Should show "chore: Initial CORTEX registration"

# If missing, verify git user configured
git config user.name
git config user.email
```

---

### Governance Validation Issues

#### Problem: "No violations found" but expect violations

```
curl -X POST http://127.0.0.1:8000/governance/validate \
  -H "Content-Type: application/json" \
  -d '{"repo_id": "frontend", "file": "src/main.ts"}'
# Response: {"violations": []}
```

**Diagnosis**:
```bash
# Check governance rules are loaded
curl http://127.0.0.1:8000/governance/rules

# Check if rules match file
cat /path/to/hub/cortex_brain/tier0/governance-rules.yaml
```

**Solutions**:

1. **No rules defined**:
```bash
# Define governance rules
cat > /path/to/hub/cortex_brain/tier0/governance-rules.yaml << 'EOF'
rules:
  - rule_id: "RULE_001"
    pattern: "*.ts"
    severity: "warning"
    message: "TypeScript file detected"
EOF

# Restart hub to load
pkill -f "cortex.api.server"
sleep 1
python -m cortex.api.server --port 8000
```

2. **File pattern doesn't match**:
```bash
# Check rule patterns
grep pattern /path/to/hub/cortex_brain/tier0/governance-rules.yaml

# Verify file path matches pattern
# Rules use glob patterns: *.ts, **/*.py, etc.
```

3. **Repo not recognized**:
```bash
# Verify repo_id in request matches registered repo_id
grep repo_id cortex-config.yaml
# Use this exact value in request
```

---

#### Problem: "Isolation violation" blocking legitimate access

```
Error: Repository isolation prevents access
Source: frontend
Target: backend/database/schema.sql
Severity: error
```

**Diagnosis**:
```bash
# Check isolation mode
grep isolation_mode cortex-config.yaml

# Check governance whitelist rules
grep -A 5 "cross.repo" /path/to/hub/cortex_brain/tier0/governance-rules.yaml
```

**Solutions**:

1. **Temporarily allow** in cortex-config.yaml:
```yaml
isolation_mode: "moderate"  # Allow with logging
# Then change back to "strict" after work done
```

2. **Whitelist access** in hub:
```yaml
# Add to governance-rules.yaml
- rule_id: "ALLOW_FRONTEND_TO_BACKEND"
  source_repo: "frontend"
  target_repo: "backend"
  resource_pattern: "database/schema.sql"
  enforcement: "allow"
```

3. **Use bridge repository** (recommended):
```bash
# Create shared resource repo
mkdir shared-resources
bash /path/to/scripts/register-repo.sh $(pwd)

# Frontend and backend can access shared-resources
# with whitelist rules
```

---

### IDE Integration Issues

#### Problem: VS Code extension not connecting

```
VS Code status bar shows: ✗ CORTEX Disconnected
```

**Diagnosis**:
```bash
# Open VS Code Output window (View → Output)
# Select "CORTEX" from dropdown
# Look for error messages
```

**Solutions**:

1. **Extension not installed**:
```bash
# Check if extension appears in VS Code Extensions
code --list-extensions | grep cortex

# If missing, install
code --install-extension cortex-dev.cortex-governance
```

2. **cortex-config.yaml not found**:
```bash
# VS Code looks for config in workspace root
ls $(pwd)/cortex-config.yaml

# If missing, run registration
bash /path/to/scripts/register-repo.sh $(pwd)

# Reload VS Code: Cmd+Shift+P → "Developer: Reload Window"
```

3. **MCP endpoint incorrect**:
```bash
# Check config
cat cortex-config.yaml | grep mcp_endpoint

# Verify hub is accessible
curl $(grep mcp_endpoint cortex-config.yaml | cut -d'"' -f2)/health

# Update config if needed
sed -i 's|http://.*:8000|http://127.0.0.1:8000|' cortex-config.yaml

# Reload extension
code --command "workbench.action.reloadWindow"
```

4. **Hub not running**:
```bash
# Verify hub is running
curl http://127.0.0.1:8000/health

# If not, start it
cd /Users/asifhussain/PROJECTS/CORTEX
python -m cortex.api.server --port 8000
```

---

#### Problem: Diagnostics not appearing in VS Code

```
Open file in VS Code but no squiggly lines shown for violations
```

**Diagnosis**:
```bash
# Check if violations exist
curl -X POST http://127.0.0.1:8000/governance/validate \
  -H "Content-Type: application/json" \
  -d '{"repo_id": "frontend", "file": "src/main.ts"}'

# Check VS Code diagnostics settings
# Command Palette: "Developer: Set Log Level" → Debug
```

**Solutions**:

1. **Violations don't exist**:
```bash
# Governance rules may not match file
# See "No violations found" section above
```

2. **Diagnostics disabled in VS Code settings**:
```bash
# Open VS Code settings (Cmd+,)
# Search for "cortex"
# Check "showDiagnostics" is enabled

# Or edit settings.json:
cat .vscode/settings.json
# Should have: "cortex.showDiagnostics": true
```

3. **File type not validated**:
```bash
# Check governance rules
# Rules may only cover certain file types (*.ts, *.py, etc.)
```

---

#### Problem: VS LSP Adapter not connecting

```
VS Output window shows: CORTEX LSP Adapter: Connection failed
```

**Diagnosis**:
```bash
# Check if .NET is installed
dotnet --version

# Check if LSP adapter executable exists
ls /path/to/cortex-lsp-adapter/bin/Release/cortex-lsp-adapter
```

**Solutions**:

1. **.NET not installed**:
```bash
# Install .NET 6.0+
# Download from https://dotnet.microsoft.com/download

# Verify after install
dotnet --version  # Should be 6.0+
```

2. **LSP adapter not built**:
```bash
# Build LSP adapter
cd /path/to/cortex-lsp-adapter
dotnet build -c Release

# Run manually to test
./bin/Release/cortex-lsp-adapter
```

3. **Python environment invalid**:
```bash
# LSP adapter validates Python
python3 --version  # Should be 3.9+

# Check required packages
python3 -c "import yaml, requests"

# Install if missing
pip install pyyaml requests
```

---

### Offline Mode Issues

#### Problem: "Offline mode enabled" when hub is actually running

```
VS Code: ⚠ CORTEX: Running in offline mode (hub unreachable)
```

**Diagnosis**:
```bash
# Check hub status
curl http://127.0.0.1:8000/health

# Check config endpoint
cat cortex-config.yaml | grep mcp_endpoint
```

**Solutions**:

1. **Hub running but endpoint wrong**:
```bash
# Check what hub is listening on
netstat -an | grep LISTEN  # or lsof -i :8000

# Update cortex-config.yaml with correct endpoint
sed -i 's|mcp_endpoint:.*|mcp_endpoint: "http://127.0.0.1:8000"|' cortex-config.yaml
```

2. **Network connectivity issue**:
```bash
# Check if machine can reach localhost
ping 127.0.0.1

# Check for firewall blocking
# macOS: System Preferences → Security & Privacy → Firewall
```

3. **Hub crashed silently**:
```bash
# Check hub logs
tail -100 /path/to/hub/cortex_brain/state/cortex.log

# Restart hub
pkill -f "cortex.api.server"
sleep 2
python -m cortex.api.server --port 8000
```

---

#### Problem: Offline queue growing too large

```
Offline queue: 1000 items (at maximum)
```

**Diagnosis**:
```bash
# Check queue size
# Queue stored in: cortex_brain/state/offline_queue.db
```

**Solutions**:

1. **Reconnect to hub** (primary solution):
```bash
# Check if hub is reachable
curl http://127.0.0.1:8000/health

# If yes, trigger sync manually (varies by IDE):
# VS Code: Command Palette → "CORTEX: Sync Offline Queue"
# VS: Output window should show sync happening
```

2. **Increase queue limit** in cortex-config.yaml:
```yaml
offline_queue_max_items: 5000  # Increased from 1000
```

3. **Clear queue** (loses unsynced events):
```bash
# WARNING: This loses offline events!
# Only do if hub cannot be reached and queue is critical

# Manual clear (dangerous):
rm cortex_brain/state/offline_queue.db

# Or use CLI command (if available):
cortex-cli offline:clear-queue
```

---

### Performance Issues

#### Problem: Validation taking >1 second

```
File validation slow:
- Expected: <100ms
- Actual: 3-5 seconds
```

**Diagnosis**:
```bash
# Measure hub response time
time curl -X POST http://127.0.0.1:8000/governance/validate \
  -H "Content-Type: application/json" \
  -d '{"repo_id": "test", "file": "test.ts"}'

# Check hub CPU/memory
top
```

**Solutions**:

1. **Hub overloaded**:
```bash
# Increase hub workers
python -m cortex.api.server --port 8000 --workers 8

# Move hub to dedicated machine if needed
# Edit cortex-config.yaml to point to remote hub
mcp_endpoint: "http://hub.internal.company.com:8000"
```

2. **Network latency**:
```bash
# Measure ping to hub
ping -c 5 127.0.0.1

# If remote hub, consider local cache refresh interval
mcp_health_check_interval_seconds: 60  # Less frequent checks
```

3. **Large file being validated**:
```bash
# Check file size
ls -lh <file>

# For very large files, consider batch validation
# Or exclude from validation in governance rules
```

---

### Data Consistency Issues

#### Problem: Audit trail missing events

```
Expected 100 events in audit trail, but only showing 50
```

**Diagnosis**:
```bash
# Check audit trail size
wc -l /path/to/hub/cortex_brain/state/governance.db

# Check for errors in hub logs
grep ERROR /path/to/hub/cortex_brain/state/cortex.log
```

**Solutions**:

1. **Audit trail pruned** (by design):
```bash
# Audit trail may have retention policy
# Check cortex/api/config.yaml for retention settings

# To keep full history:
audit_retention_days: 0  # Never delete
```

2. **Database corruption**:
```bash
# Rebuild database from manifest
python scripts/rebuild_audit_trail.py

# Or restore from backup (if available)
cp cortex_brain/state/governance.db.backup cortex_brain/state/governance.db
```

---

### Debugging Techniques

#### Enable Debug Logging

```bash
# Hub with debug logging
python -m cortex.api.server --port 8000 --debug

# Watch logs in real-time
tail -f /path/to/hub/cortex_brain/state/cortex.log

# IDE extension debug output
# VS Code: Command Palette → "Developer: Toggle Developer Tools"
# VS: View → Output (select CORTEX channel)
```

#### Test Endpoints Manually

```bash
# Health check
curl http://127.0.0.1:8000/health

# List registered repos
curl http://127.0.0.1:8000/registry/repos

# Validate file
curl -X POST http://127.0.0.1:8000/governance/validate \
  -H "Content-Type: application/json" \
  -d '{"repo_id": "test", "file": "test.ts"}'

# Get audit trail
curl http://127.0.0.1:8000/audit/trail?limit=10

# Get governance rules
curl http://127.0.0.1:8000/governance/rules
```

#### Check System Resources

```bash
# Monitor process
ps aux | grep cortex

# Monitor network
netstat -an | grep 8000

# Monitor logs
tail -f /path/to/hub/cortex_brain/state/cortex.log

# Check disk space
df -h
```

---

**Last Updated**: January 19, 2026  
**Version**: 1.0.0  
**Status**: Production Ready
