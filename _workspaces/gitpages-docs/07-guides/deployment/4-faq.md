# CORTEX Deployment FAQ

**AC-DEPLOY-ENHANCED-005-01: Comprehensive Deployment Documentation**

## Frequently Asked Questions

### General Questions

#### Q: What is CORTEX?
**A**: CORTEX is a multi-repository governance system that enforces consistent rules and policies across interconnected code repositories. It consists of:
- **Central Hub**: Governance authority running MCP server
- **Connected Repos**: Register via `cortex-config.yaml`
- **IDE Extensions**: VS Code and Visual Studio integration
- **Audit Trail**: Complete logging of all governance operations

---

#### Q: Do I need the CORTEX hub to develop locally?
**A**: No. Repositories can work in offline mode using cached rules. When the hub is unavailable, repos continue with locally cached governance rules and queue operations for syncing when reconnected.

---

#### Q: Can CORTEX work with non-Git repositories?
**A**: Currently designed for Git. The registration script uses Git hooks and creates Git-specific structures. However, the underlying governance principles could be adapted to other VCS systems.

---

#### Q: Is CORTEX open source?
**A**: CORTEX is designed as an enterprise governance system. This implementation is available for internal use.

---

### Setup & Configuration

#### Q: How long does the initial setup take?
**A**: Typically 10-15 minutes for:
1. Hub initialization (2 min)
2. Registering 3-5 repositories (2 min each)
3. Installing IDE extensions (2 min)

---

#### Q: Can I set up the hub on a remote machine?
**A**: Yes. Set `mcp_endpoint` in each `cortex-config.yaml` to point to the remote hub:
```yaml
mcp_endpoint: "http://hub.internal.company.com:8000"
```

Ensure network connectivity and firewall rules allow connections on the hub port.

---

#### Q: What Python version is required?
**A**: Python 3.9 or higher. Check with:
```bash
python3 --version
```

---

#### Q: Can I change the hub port?
**A**: Yes. Start the hub with custom port:
```bash
python -m cortex.api.server --port 9000

# Then update cortex-config.yaml in each repo:
mcp_endpoint: "http://127.0.0.1:9000"
```

---

#### Q: Do I need to modify my repository structure?
**A**: Minimally. The registration script creates:
- `cortex-config.yaml` (root)
- `.github/prompts/` (governance prompts)
- `.github/tier0/` (local governance stub)

These can be committed to Git or added to `.gitignore` depending on your policy.

---

### Usage & Operations

#### Q: How often should I refresh governance rules?
**A**: Automatically! Repos check hub health every 30 seconds (configurable in `cortex-config.yaml`).

---

#### Q: What happens if the hub goes down?
**A**: Repositories enter offline mode:
1. Continue using cached governance rules
2. Queue operations in local offline queue
3. Automatically sync when hub comes back online

---

#### Q: Can I update governance rules without restarting the hub?
**A**: Yes. Rules are loaded from YAML files. Updates take effect after 30 seconds (cache TTL). For immediate effect:
```bash
# Restart the hub
pkill -f "cortex.api.server"
sleep 2
python -m cortex.api.server --port 8000
```

---

#### Q: How do I add a new developer to use CORTEX?
**A**: Each developer needs:
1. Access to hub machine or network address
2. IDE extension installed (VS Code/VS)
3. Repository registration (automatic via `register-repo.sh`)

No additional user accounts needed - hub has no authentication by default.

---

#### Q: How do I remove a repository from governance?
**A**: In the repository:
```bash
git rm cortex-config.yaml .github/
git commit -m "chore: Remove CORTEX governance"

# Optional: Remove from hub registry
# Edit cortex_brain/tier0/repo-registry.yaml
```

---

### Isolation & Access Control

#### Q: What does "isolation mode: strict" mean?
**A**: Repositories cannot access files/resources in other repositories unless explicitly whitelisted in governance rules.

---

#### Q: How do I allow cross-repository access?
**A**: Create a whitelist rule in hub governance:
```yaml
rules:
  - rule_id: "ALLOW_SHARED_RESOURCES"
    source_repo: "frontend"
    target_repo: "shared-resources"
    resource_pattern: "**/*"
    enforcement: "allow"
```

---

#### Q: Can I temporarily disable isolation?
**A**: Yes, for testing:
```yaml
# In cortex-config.yaml
isolation_mode: "moderate"  # Allows with logging
# Don't commit! Switch back after testing
isolation_mode: "strict"    # Revert before committing
```

---

#### Q: What audit events are logged?
**A**: Every operation:
- Repository registrations
- File validations
- Governance violations
- Isolation violations
- Rule changes
- Session creation/closure
- All IDE interactions

---

### IDE Integration

#### Q: Which IDEs are supported?
**A**: 
- **VS Code**: Full support via native extension
- **Visual Studio**: Full support via LSP adapter
- **Others**: Can be added via LSP support (JetBrains IntelliJ, Sublime, etc.)

---

#### Q: Can I use CORTEX without an IDE?
**A**: Yes. Use command-line or scripts:
```bash
# Validate file via API
curl -X POST http://127.0.0.1:8000/governance/validate \
  -H "Content-Type: application/json" \
  -d '{"repo_id": "frontend", "file": "src/main.ts"}'
```

---

#### Q: Can I configure IDE diagnostics?
**A**: Yes. In VS Code settings (`.vscode/settings.json`):
```json
{
  "cortex.showDiagnostics": true,
  "cortex.hubEndpoint": "http://127.0.0.1:8000",
  "cortex.healthCheckInterval": 30,
  "cortex.offlineMode": false
}
```

---

#### Q: Why are violations not showing in my IDE?
**A**: Check:
1. Is the hub running? → `curl http://127.0.0.1:8000/health`
2. Is the file covered by rules? → `curl http://127.0.0.1:8000/governance/rules`
3. Is `cortex-config.yaml` in repo root? → `ls cortex-config.yaml`
4. Is the extension connected? → Check status bar (VS Code) or Output window (VS)

---

### Offline Mode

#### Q: How long can I work offline?
**A**: Indefinitely. Repos use cached rules and queue operations locally.

---

#### Q: What happens when I reconnect?
**A**: Automatic sync-on-reconnect:
1. Queue of offline operations syncs with hub
2. Rules are refreshed from hub
3. Any offline violations are validated against latest rules

---

#### Q: Can the offline queue get too large?
**A**: Yes, if hub is down for extended time. Configure limit:
```yaml
offline_queue_max_items: 5000  # Increased from 1000
```

Or force sync when hub is available.

---

#### Q: What happens if hub is unreachable when I reconnect?
**A**: Sync is retried on next health check (default every 30s). You'll see warning in IDE that you're still in offline mode.

---

### Performance & Scalability

#### Q: How many repositories can one hub handle?
**A**: Tested and recommended:
- **Small scale**: 10-20 repos (1 hub instance)
- **Medium scale**: 50-100 repos (scale hub horizontally)
- **Large scale**: 200+ repos (use hub cluster with load balancer)

---

#### Q: How long does file validation take?
**A**: Typical:
- Simple validation: 10-50ms
- Complex rules: 50-200ms
- Cached validation: <5ms

---

#### Q: Does validation slow down my IDE?
**A**: Minimal impact:
- Validations run in background
- Results cached for performance
- IDE remains responsive

---

#### Q: Can I batch validate many files?
**A**: Not directly via IDE, but:
```bash
# Script to batch validate
for file in src/**/*.ts; do
  curl -X POST http://127.0.0.1:8000/governance/validate \
    -d "{\"repo_id\": \"frontend\", \"file\": \"$file\"}"
done
```

---

### Versioning & Upgrades

#### Q: What do version numbers mean?
**A**: Semantic versioning (major.minor.patch):
- **1.0.0**: Initial production release
- **1.0.1**: Patch/bugfix
- **1.1.0**: Minor feature addition
- **2.0.0**: Major breaking changes

---

#### Q: How do I upgrade CORTEX?
**A**: 
1. Backup governance data: `cp -r cortex_brain cortex_brain.backup`
2. Pull latest code
3. Run migrations: `python scripts/migrate.py`
4. Restart hub
5. Verify all repos connect: `curl http://127.0.0.1:8000/health`

---

#### Q: Can repos run different CORTEX versions?
**A**: Yes, via version negotiation. Each repo's `cortex-config.yaml` specifies:
```yaml
version: "1.0.0"           # Current version
min_hub_version: "1.0.0"   # Minimum hub version required
```

Hub negotiates compatibility on each connection.

---

#### Q: What's the upgrade path from 0.9 to 1.0?
**A**: Minor breaking changes - follow migration guide:
```bash
python scripts/upgrade-0.9-to-1.0.py
```

---

### Troubleshooting

#### Q: Where are the logs?
**A**: 
- **Hub logs**: `cortex_brain/state/cortex.log`
- **IDE logs**: 
  - VS Code: Command Palette → "Developer: Toggle Developer Tools"
  - VS: View → Output (CORTEX channel)

---

#### Q: How do I reset everything and start over?
**A**:
```bash
# WARNING: Deletes all governance data!
rm -rf cortex_brain/state/
python scripts/setup_cortex_hub.py

# For repositories:
# Re-run registration script
bash /path/to/scripts/register-repo.sh $(pwd)
```

---

#### Q: What if I accidentally create an isolation violation?
**A**: It's logged but doesn't break anything:
1. Check audit trail to see what happened
2. Either whitelist the access or refactor to avoid it
3. Violations don't prevent work - they're logged for audit

---

#### Q: Can I see what other repositories are accessing?
**A**: Yes, via audit trail:
```bash
curl "http://127.0.0.1:8000/audit/trail?operation=isolation_violation"
```

---

### Best Practices

#### Q: What's the recommended deployment strategy?
**A**:
1. Start with central hub + 2-3 pilot repos
2. Validate governance rules work as expected
3. Gradually onboard more repos
4. Monitor audit trail for issues
5. Document rules and policies

---

#### Q: How should I organize governance rules?
**A**:
- **Tier 0**: Core organizational policies
- **Tier 1**: Team/domain specific rules
- **Tier 2**: Project/repository specific overrides

---

#### Q: Should repos commit `cortex-config.yaml`?
**A**: Recommended yes:
```bash
git add cortex-config.yaml .github/tier0 .github/prompts
git commit -m "chore: Add CORTEX governance configuration"
```

Benefits:
- New developers automatically get CORTEX setup
- Config changes tracked in Git
- Easy to see when repo was registered

---

#### Q: How do I back up governance data?
**A**: 
```bash
# Full backup
cp -r cortex_brain cortex_brain.backup-$(date +%Y%m%d)

# Or automated backup
0 2 * * * tar -czf /backups/cortex-$(date +\%Y\%m\%d).tar.gz /path/to/cortex_brain
```

---

#### Q: How do I handle team onboarding?
**A**:
1. Have them clone repo
2. `cortex-config.yaml` automatically sets up CORTEX
3. Install IDE extension
4. Reload IDE
5. Done!

---

### Support & Resources

#### Q: Where can I get help?
**A**: 
1. Check this FAQ
2. Review troubleshooting guide: `docs/DEPLOYMENT-TROUBLESHOOTING.md`
3. Read setup guide: `docs/DEPLOYMENT-SETUP-GUIDE.md`
4. Check API reference: `docs/DEPLOYMENT-API-REFERENCE.md`

---

#### Q: How do I report a bug?
**A**: 
1. Reproduce the issue
2. Collect logs from `cortex_brain/state/cortex.log`
3. Note the exact error and steps to reproduce
4. File issue with full details

---

#### Q: Is there a community?
**A**: This is an internal enterprise tool. For internal questions, contact CORTEX team.

---

#### Q: What's the roadmap?
**A**: Planned features:
- **Phase 2**: ML-based violation suggestions
- **Phase 3**: Distributed hub support
- **Phase 4**: Blockchain audit trail (regulated industries)
- **Phase 5**: Community governance rule library

---

**Last Updated**: January 19, 2026  
**Version**: 1.0.0  
**Status**: Production Ready
