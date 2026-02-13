# CORTEX Deployment Architecture - ADRs

**AC-DEPLOY-ENHANCED-005-01: Comprehensive Deployment Documentation**

## Architecture Decision Records (ADRs)

Record of key architectural decisions made during CORTEX deployment system design.

---

## ADR-001: Hub-Spoke Multi-Repository Model

**Status**: Accepted  
**Date**: January 2026  
**Authors**: CORTEX Team

### Context
Multiple independent repositories need to share governance rules while maintaining autonomy. Options:
1. Centralized authority (hub-spoke model)
2. Distributed peer-to-peer
3. Hybrid with eventual consistency

### Decision
Implement **hub-spoke model** with central CORTEX hub as governance authority.

### Rationale
- **Consistency**: Single source of truth for governance rules
- **Auditability**: Centralized audit trail for compliance
- **Scalability**: Hub scales horizontally independently of repos
- **Operational**: Easier to manage single hub vs peer network
- **Offline support**: Repos can operate offline with cached rules

### Consequences
- **Pro**: Centralized control, clear accountability
- **Pro**: Simpler compliance auditing
- **Con**: Hub becomes critical dependency (mitigated by offline mode)
- **Con**: Network latency on validation (mitigated by caching)

### Related Files
- `cortex/api/server.py` - MCP server implementation
- `cortex/mcp/models/session.py` - Session management
- `cortex_brain/tier0/repo-registry.yaml` - Registry

---

## ADR-002: Repository Isolation via Hard Boundaries

**Status**: Accepted  
**Date**: January 2026

### Context
Repositories must prevent accidental or intentional cross-repo access. Options:
1. Soft boundaries (warnings only)
2. Hard boundaries (blocked with audit)
3. Whitelist-based access

### Decision
Implement **hard boundaries by default** with optional whitelisting per governance rule.

### Rationale
- **Security**: Prevents data leakage between repos
- **Isolation**: Clear separation of concerns
- **Auditability**: Every violation is logged
- **Flexibility**: Whitelist allows legitimate cross-repo access when needed

### Consequences
- **Pro**: Strong isolation guarantees
- **Pro**: Clear audit trail of boundary violations
- **Con**: May require initial whitelisting during setup
- **Mitigation**: Governance rules can whitelist legitimate access

### Related Files
- `cortex/core/security/isolation.py` - Isolation enforcement
- `cortex_brain/tier0/governance-rules.yaml` - Whitelist configuration

---

## ADR-003: Session-Based Context Injection

**Status**: Accepted  
**Date**: January 2026

### Context
Orchestrators need to know which repository they're running in for proper isolation. Options:
1. Global context variables
2. Parameter passing
3. Session-based context injection
4. Thread-local storage

### Decision
Implement **session-based context injection** via MCPSession objects.

### Rationale
- **Thread-safety**: Each session has isolated context
- **Traceability**: Session ID enables full audit trails
- **Flexibility**: Context can be extended for new fields
- **Testability**: Sessions can be mocked/isolated for testing

### Consequences
- **Pro**: Thread-safe concurrent operations
- **Pro**: Complete session audit trail
- **Pro**: Easy context extension
- **Con**: Requires passing session through call stacks
- **Mitigation**: Use context managers for automatic session handling

### Related Files
- `cortex/mcp/models/session.py` - Session dataclass
- `cortex/mcp/session_manager.py` - Session lifecycle

---

## ADR-004: Semantic Versioning for Governance Prompts

**Status**: Accepted  
**Date**: January 2026

### Context
Governance prompts evolve over time. Repos may be at different versions. Options:
1. Always use latest version
2. Semantic versioning with compatibility matrix
3. Feature flags
4. Gradual rollout

### Decision
Implement **semantic versioning with compatibility matrix**.

### Rationale
- **Compatibility**: Repos can stay on stable versions
- **Flexibility**: Gradual adoption of new rules
- **Safety**: Backward compatibility guarantees
- **Auditability**: Clear version history

### Consequences
- **Pro**: Supports heterogeneous repo versions
- **Pro**: Safe upgrades with compatibility checking
- **Con**: Requires maintaining version manifests
- **Mitigation**: Automated version negotiation handles complexity

### Related Files
- `src/versioning/prompt_version_manager.py` - Version negotiation
- `cortex_brain/tier0/prompt-versions.yaml` - Version registry

---

## ADR-005: MCP (Model Context Protocol) as Integration Point

**Status**: Accepted  
**Date**: January 2026

### Context
Need standard way for IDEs and tools to integrate with governance hub. Options:
1. Custom HTTP REST API
2. gRPC
3. MCP (Model Context Protocol)
4. GraphQL

### Decision
Implement **MCP (Model Context Protocol)** as the integration interface.

### Rationale
- **Standards-based**: MCP is emerging standard for AI tool integration
- **IDE-friendly**: Designed for IDE/tool integration
- **Extensible**: MCP resources/tools/prompts support governance model
- **AI-first**: Natural fit for prompt-based governance

### Consequences
- **Pro**: Future-proof for AI-driven governance
- **Pro**: IDE extensions can use standard MCP clients
- **Con**: Requires learning MCP protocol
- **Con**: Smaller ecosystem than REST/gRPC (growing)

### Related Files
- `cortex/api/mcp_server.py` - MCP server
- `cortex/api/server.py` - HTTP-MCP bridge

---

## ADR-006: Offline-First Design with Sync-on-Connect

**Status**: Accepted  
**Date**: January 2026

### Context
Repositories should work even if hub is temporarily unreachable. Options:
1. Fail immediately (strict online-only)
2. Offline mode with local rules only
3. Offline-first with sync queue

### Decision
Implement **offline-first with sync-on-reconnect**.

### Rationale
- **Resilience**: Developers can work during hub downtime
- **Productivity**: No false failures when network fluctuates
- **Consistency**: Sync queue ensures no lost events
- **Flexibility**: Rules come from cache when offline

### Consequences
- **Pro**: Improved availability and resilience
- **Pro**: Better user experience
- **Con**: Requires offline rule caching
- **Con**: Sync queue can grow large
- **Mitigation**: Configurable queue limits, local cleanup

### Related Files
- `cortex/mcp/models/session.py` - Offline mode state
- `cortex_brain/state/offline_queue.db` - Sync queue

---

## ADR-007: IDE Integration via Extensions

**Status**: Accepted  
**Date**: January 2026

### Context
Need way for developers to see governance violations in their IDEs. Options:
1. Command-line tool only
2. IDE extensions (VS Code, VS)
3. IDE plugin framework (JetBrains, etc.)
4. Language server protocol (LSP)

### Decision
Implement **both VS Code Extension + VS LSP Adapter**.

### Rationale
- **Developer experience**: Inline diagnostics in IDE
- **Coverage**: VS Code (most popular) + VS (enterprise)
- **Standards**: VS uses LSP (extensible to other IDEs)
- **Quick-fixes**: IDE-native code actions for remediation

### Consequences
- **Pro**: Best-in-class developer experience
- **Pro**: IDE-native UI/UX
- **Con**: Need to maintain multiple integrations
- **Mitigation**: Shared MCP client library, common patterns

### Related Files
- `extensions/vscode-cortex/` - VS Code extension
- `extensions/cortex-lsp-adapter/` - VS LSP adapter

---

## ADR-008: Governance Rules as YAML Manifests

**Status**: Accepted  
**Date**: January 2026

### Context
Need to store and version governance rules. Options:
1. Database-native (SQL)
2. YAML/JSON files in git
3. DSL language
4. Configuration management tool

### Decision
Implement **YAML manifests stored in git** with database cache.

### Rationale
- **Version control**: Rules tracked in git with full history
- **Code review**: Governance changes can be reviewed like code
- **Auditability**: Who changed what and when
- **Flexibility**: YAML is human-readable and extensible
- **Caching**: Database for fast runtime access

### Consequences
- **Pro**: Governance rules are reviewable, versioned, auditable
- **Pro**: Easy for teams to understand and modify
- **Con**: Requires git workflow for rule changes
- **Mitigation**: UI tools can automate rule generation

### Related Files
- `cortex_brain/tier0/governance-rules.yaml` - Rules manifest
- `cortex_brain/state/governance.db` - Runtime cache

---

## ADR-009: Layered Compliance (Tier 0-2)

**Status**: Accepted  
**Date**: January 2026

### Context
Different governance strictness needed for different parts of codebase. Options:
1. Single governance layer
2. Two-tier (base + override)
3. Three+ tier with inheritance

### Decision
Implement **three-tier model: Tier 0 (core), Tier 1 (extended), Tier 2 (local)**.

### Rationale
- **Flexibility**: Core + team-specific + repo-specific rules
- **Inheritance**: Rules inherit down layers with override capability
- **Maintenance**: Core rules maintained centrally, teams can customize
- **Compliance**: Different compliance requirements per team

### Consequences
- **Pro**: Balances central control with local flexibility
- **Pro**: Rules can be specialized per context
- **Con**: Complexity of rule inheritance
- **Mitigation**: Clear documentation, conflict resolution rules

### Related Files
- `cortex_brain/tier0/` - Core governance rules
- `cortex_brain/tier1/` - Extended rules
- `cortex_brain/tier2/` - Local/team rules

---

## ADR-010: Minimal Deployment Footprint

**Status**: Accepted  
**Date**: January 2026

### Context
Each repository shouldn't require heavy dependencies. Options:
1. Full CORTEX installation in each repo
2. Lightweight client-only installation
3. Extension-based model (no installation)

### Decision
Implement **extension-based model** with minimal `cortex-config.yaml`.

### Rationale
- **Lightweight**: Just config file in each repo
- **Fast onboarding**: `register-repo.sh` does everything
- **Flexibility**: Use IDE extensions or command-line
- **Scalability**: No per-repo infrastructure needed

### Consequences
- **Pro**: Minimal per-repo overhead
- **Pro**: Easy to add/remove repos
- **Con**: Full validation requires hub connectivity
- **Mitigation**: Offline mode + caching

### Related Files
- `scripts/register-repo.sh` - Registration automation
- `cortex-config.yaml` - Minimal config file

---

## Trade-offs Summary

| Decision | Pro | Con | Mitigation |
|----------|-----|-----|-----------|
| Hub-spoke | Consistency | Single point of failure | Offline mode |
| Hard isolation | Security | Requires whitelisting | Governance rules |
| Session context | Thread-safe | Parameter passing | Context managers |
| Semantic versioning | Flexibility | Complexity | Auto-negotiation |
| MCP protocol | Standards | New ecosystem | Documentation |
| Offline-first | Resilience | Sync complexity | Queue management |
| IDE extensions | UX | Maintenance | Shared libraries |
| YAML manifests | Git-native | File management | UI tooling |
| Tiered governance | Flexibility | Complexity | Clear docs |
| Minimal footprint | Simplicity | Limited local features | IDE extensions |

---

## Future Considerations

### Potential Evolution

1. **Distributed Mode**: P2P governance for fully decentralized teams
2. **ML-based Rules**: AI learns governance violations and suggests improvements
3. **Blockchain Audit Trail**: Immutable governance record (for regulated industries)
4. **Real-time Sync**: WebSocket-based live rule updates
5. **Plugin Ecosystem**: Community governance rule extensions

### Technology Evolution

- **Protocol**: Considering gRPC for performance-critical paths
- **Storage**: Potentially PostgreSQL for large-scale deployments
- **Caching**: Redis for distributed hub setups
- **Observability**: OpenTelemetry for tracing/metrics

---

**Last Updated**: January 19, 2026  
**Version**: 1.0.0  
**Status**: Production Ready
