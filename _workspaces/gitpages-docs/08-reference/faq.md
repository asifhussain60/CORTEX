# Frequently Asked Questions# Frequently Asked Questions



**Last Updated:** 2026-01-20  Common questions about CORTEX installation, usage, and troubleshooting.

**Version:** 1.0.0  

**Status:** Production Ready## Installation & Setup



Common questions about CORTEX installation, usage, troubleshooting, and best practices. Questions are organized by topic.**Q: What are the system requirements?**  

A: Python 3.9+, Node.js 14+ (for CLI), and Git 2.20+. See [Installation Guide](../01-getting-started/0-installation.md).

---

**Q: How do I set up local development?**  

## Table of ContentsA: Follow the [Local Development Guide](../04-guides/deployment/1-local-development.md).



1. [Installation & Setup](#installation--setup)**Q: Can I run CORTEX on Windows?**  

2. [Getting Started](#getting-started)A: CORTEX is developed on macOS/Linux. Windows users should use WSL2.

3. [Architecture & Design](#architecture--design)

4. [Usage & Integration](#usage--integration)## Usage

5. [Governance & Rules](#governance--rules)

6. [Performance & Scaling](#performance--scaling)**Q: How do I create my first orchestrator?**  

7. [Troubleshooting](#troubleshooting)A: See [First Orchestrator](../01-getting-started/2-first-orchestrator.md) tutorial.

8. [Compliance & Security](#compliance--security)

9. [Development & Contributing](#development--contributing)**Q: What's the difference between REST, MCP, and CLI?**  

A: All three are equal-privilege interfaces to CORTEX:

---- **REST**: HTTP endpoints for web integration

- **MCP**: Model Context Protocol for AI-native apps

## Installation & Setup- **CLI**: Command-line for automation and scripting



### What are the system requirements?**Q: How do I integrate domain knowledge?**  

A: Use Domain Brain BKIO interface. See [Domain Brain Guide](../02-architecture/4-domain-brain.md).

**Minimum:**

- Python 3.9+## Troubleshooting

- 4GB RAM

- 10GB disk space**Q: CORTEX is slow. How do I diagnose?**  

- macOS, Linux, or Windows (WSL2)A: Check the [Troubleshooting Guide](../04-guides/operations/4-troubleshooting.md#performance).



**Recommended:****Q: How do I check audit logs?**  

- Python 3.11+A: Access via REST API: `GET /api/audit/logs?limit=100`

- 8GB RAM

- 50GB disk space**Q: Can I run multiple CORTEX instances?**  

- SSD storageA: Yes, but they require a shared governance database. See [Advanced Configuration](../04-guides/advanced/0-overview.md).



*See: [Installation Guide](../01-getting-started/0-installation.md)*## Compliance & Security



### Can I run CORTEX on Windows?

**Q: Is CORTEX HIPAA-compliant?**  
A: See [Compliance Mappings](compliance-mappings.md) for regulatory requirements.

Yes, but we recommend using **WSL2** (Windows Subsystem for Linux). Native Windows support is experimental.

**Q: How is audit trail secured?**  
A: Audit logs are immutable and encrypted. See [Governance Rules](../02-architecture/governance-rules.md) for security details.

```bash
# Install WSL2
wsl --install -d Ubuntu-22.04---



# Then follow standard Linux installation**Still have questions?** Check the [Troubleshooting Guide](../04-guides/operations/4-troubleshooting.md) or open an issue.

```

### How do I set up local development?

```bash
# Clone and setup
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Initialize
cortex governance init
cortex health check
```

*See: [Quick Start](../01-getting-started/1-quickstart.md)*

### What Python version should I use?

**Python 3.11.4** is the recommended version. CORTEX supports Python 3.9+ but:

- 3.9-3.10: Supported but may have performance limitations
- 3.11+: Recommended (best performance)
- 3.12+: Experimental support

### Do I need Docker?

**No, but it's recommended** for:
- Consistent environments
- Easy deployment
- Isolation from host system

You can run CORTEX directly with Python if preferred.

### How much disk space does CORTEX need?

- **Base installation**: ~500MB
- **Governance database**: ~10-100MB (grows with usage)
- **Domain Brain knowledge**: ~1-10GB (depends on content)
- **Logs and audit trail**: ~1GB per month

**Recommendation**: Allocate 50GB for production deployments.

---

## Getting Started

### How do I create my first orchestrator?

Follow the step-by-step tutorial:

```python
from src.orchestrators.base import OrchestratorBase

class MyFirstOrchestrator(OrchestratorBase):
    async def process(self, intent: str, context: dict) -> Result:
        # Your business logic here
        return Result(status="success", data={"message": "Done!"})
```

*See: [First Orchestrator Tutorial](../01-getting-started/2-first-orchestrator.md)*

### What's the difference between REST, MCP, and CLI?

All three are **equal-privilege interfaces** to CORTEX:

| Interface | Use Case | Example |
|-----------|----------|---------|
| **REST API** | Web apps, microservices | `curl -X POST /api/orchestrate` |
| **MCP Protocol** | AI-native apps, VS Code | JSON-RPC over stdio |
| **CLI** | Automation, scripts, dev | `cortex orchestrator run my-orch` |

They provide the same capabilities—choose based on your integration needs.

### What is the LENS Protocol?

LENS is CORTEX's 4-phase intent comprehension method:

1. **L**anguage: Canonicalize intent, extract keywords
2. **E**xamination: Identify patterns, classify operation
3. **N**avigation: Map to capabilities, select orchestrator
4. **S**ynthesis: Generate execution plan

It runs before every orchestrator execution to understand user intent.

*See: [Orchestration Engine](../02-architecture/3-orchestration-engine.md#lens-protocol)*

### How do I integrate domain knowledge?

Use the Domain Brain BKIO (Business Knowledge Ingestion Organization) system:

```bash
# File-based knowledge
cortex knowledge import --type file --path ./knowledge/

# API-based knowledge
cortex knowledge import --type api --url https://api.example.com/knowledge

# Database knowledge
cortex knowledge import --type database --connection postgres://...
```

*See: [Domain Brain Guide](../02-architecture/4-domain-brain.md)*

### What's a ConversationProtocol?

It's CORTEX's pattern for multi-turn interactions. Each turn produces a `ContinuationDecision`:

```python
turn1 = await orchestrator.converse("Hi")
# Decision: NEEDS_INPUT (too short)

turn2 = await orchestrator.converse("Analyze this code for bugs")
# Decision: NEEDS_APPROVAL (high complexity)

turn3 = await orchestrator.converse("Yes, proceed")
# Decision: COMPLETE (task finished)
```

*See: [ConversationProtocol](../02-architecture/3-orchestration-engine.md#conversationprotocol)*

---

## Architecture & Design

### What are Governance Tiers?

CORTEX uses 4 hierarchical tiers:

| Tier | Name | Mutability | Use Case |
|------|------|------------|----------|
| **0** | SKULL (CORE rules) | Immutable | System safety |
| **1** | Architectural | Admin-only | Structure constraints |
| **2** | Templates | User-extensible | Scaffolding |
| **3** | Knowledge | User-managed | Domain rules |

Higher tiers **cannot override** lower tiers.

*See: [System Overview](../02-architecture/1-system-overview.md#governance-tiers)*

### Why can't I modify Tier 0 rules?

Tier 0 contains the **29 CORE rules** that ensure system safety. They're immutable to:

- Prevent accidental corruption
- Ensure compliance requirements
- Maintain audit trail integrity
- Guarantee governance enforcement

If you need to modify system behavior, use Tier 1 (architectural) rules instead.

### What is the Complexity Gate?

Stage 2.5 in the orchestration pipeline that analyzes operation complexity and decides if user confirmation is needed:

```
Complexity Score 0.0-0.4 → Auto-approve (simple operations)
Complexity Score 0.4-0.7 → Notify user (informational)
Complexity Score 0.7-1.0 → Require confirmation (risky operations)
```

*See: [Orchestration Engine](../02-architecture/3-orchestration-engine.md#complexity-gate)*

### How does the audit trail work?

Every operation creates an audit entry with:

- Operation details
- Governance results
- Timestamp
- Cryptographic hash

Entries form a **hash chain**—each entry links to the previous one, making tampering detectable.

```json
{
  "entry_id": "AUD-00001234",
  "hash": "sha256:a1b2c3...",
  "previous_hash": "sha256:x9y8z7...",
  ...
}
```

*See: [Design Principles - Auditability](../02-architecture/2-design-principles.md#10-safety-through-auditability)*

### What resilience patterns does CORTEX use?

1. **Circuit Breaker**: Fail fast when service is down
2. **Retry with Backoff**: Automatic retry for transient failures
3. **Partial Mode**: Degrade gracefully, don't fail completely
4. **Rollback**: Atomic transaction reversal
5. **Bulkhead**: Resource isolation

*See: [Resilience Patterns](../02-architecture/5-resilience-patterns.md)*

---

## Usage & Integration

### How do I call an orchestrator via REST API?

```bash
curl -X POST http://localhost:8080/api/orchestrators/my-orch/execute \
  -H "Authorization: Bearer $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "intent": "Analyze repository for security issues",
    "context": {"repo_url": "https://github.com/example/repo"}
  }'
```

*See: [REST API Guide](../03-api-reference/rest-api/0-guide.md)*

### How do I use CORTEX with VS Code?

CORTEX implements MCP (Model Context Protocol) for VS Code Copilot integration:

```json
// .vscode/settings.json
{
  "mcp.servers": {
    "cortex": {
      "command": "cortex",
      "args": ["mcp", "start", "--stdio"]
    }
  }
}
```

Then use in Copilot Chat:
```
@cortex analyze this file for security issues
```

*See: [MCP Protocol](../03-api-reference/mcp-protocol/0-specification.md)*

### Can I run multiple orchestrators in parallel?

Yes! CORTEX supports concurrent execution:

```python
import asyncio

results = await asyncio.gather(
    orchestrator1.process(intent1),
    orchestrator2.process(intent2),
    orchestrator3.process(intent3),
)
```

Each orchestrator runs independently with its own governance checks.

### How do I pass context between orchestrator turns?

Context is preserved across turns in a conversation:

```python
# Turn 1
turn1 = await orch.converse("Start analysis", context={"repo": "my-repo"})

# Turn 2 - context automatically preserved
turn2 = await orch.converse("Show me the results")
# Still has access to repo="my-repo"
```

### Can CORTEX integrate with my existing systems?

Yes! Integration options:

1. **REST API**: HTTP-based integration
2. **Python SDK**: Direct Python imports
3. **MCP Protocol**: AI-native integrations
4. **CLI**: Command-line automation
5. **Webhooks**: Event-driven notifications

*See: [Integration Guide](../04-guides/integration/0-overview.md)*

---

## Governance & Rules

### How do I add custom governance rules?

Custom rules go in Tier 1 or Tier 3:

```yaml
# my_rules.yaml
- rule_id: CUSTOM-001
  tier: 3
  name: "Require code review for production"
  description: "All production deployments need review"
  pattern: "deploy.*production"
  action: require_approval
```

Load with:
```bash
cortex governance load --rules my_rules.yaml
```

### What happens when a rule is violated?

1. Operation is **immediately blocked**
2. Violation is **recorded in audit trail**
3. User receives **detailed error message**
4. Admin can review in audit logs

```json
{
  "status": "governance_blocked",
  "violations": [{
    "rule_id": "CORE-001",
    "message": "Operation not in safe list",
    "severity": "critical"
  }]
}
```

### Can I temporarily disable a rule?

**No for Tier 0** (CORE rules are immutable).

**Yes for Tier 1-3** with admin access:

```bash
cortex governance disable-rule CUSTOM-001 --reason "Testing" --expires "2026-01-21"
```

All rule changes are audited.

### How do I check which rules are active?

```bash
# List all rules
cortex governance list-rules

# Show specific rule
cortex governance show-rule CORE-001

# Check rule status
cortex governance status
```

### What are "safe operations"?

Operations explicitly allowed by CORE-001. Examples:

- Read-only file operations
- Query operations (no writes)
- Information retrieval
- Analysis and reporting

Destructive operations (delete, modify production, etc.) require explicit approval.

---

## Performance & Scaling

### CORTEX is slow. How do I diagnose?

```bash
# Check system health
cortex health check --verbose

# Profile operations
cortex diagnostic profile --duration 60s

# Check slow queries
cortex db analyze-slow-queries

# Review metrics
cortex metrics export --format json
```

*See: [Troubleshooting Guide](../01-getting-started/3-troubleshooting.md#performance-issues)*

### How do I optimize knowledge queries?

```bash
# Reindex knowledge base
cortex knowledge reindex --parallel 4

# Vacuum database
cortex db vacuum

# Enable query caching
# In cortex-config.yaml:
domain_brain:
  cache:
    enabled: true
    max_entries: 10000
    ttl_seconds: 3600
```

### Can I run multiple CORTEX instances?

Yes, with shared governance database:

```yaml
# Instance 1 & 2 config
database:
  type: postgresql  # Use PostgreSQL instead of SQLite
  host: db.example.com
  database: cortex_governance
  
# Enable distributed locking
distributed:
  enabled: true
  lock_backend: redis
  redis_url: redis://cache.example.com
```

*See: [Advanced Configuration](../04-guides/advanced/0-overview.md)*

### What's the maximum knowledge base size?

**Tested limits:**
- 100,000 knowledge entries
- 10GB total knowledge size
- Sub-second query times with proper indexing

**Best practices:**
- Use semantic search for large bases
- Enable caching
- Partition by domain
- Regular vacuum/reindex

### How do I monitor CORTEX in production?

```yaml
# Enable Prometheus metrics
telemetry:
  enabled: true
  prometheus:
    port: 9090
    
# Enable health checks
health:
  endpoint: /health
  liveness_interval: 5
  readiness_interval: 10
```

Key metrics:
- `cortex_orchestrator_duration_seconds`
- `cortex_governance_checks_total`
- `cortex_circuit_state`
- `cortex_knowledge_query_duration`

*See: [Operations Guide](../04-guides/operations/0-overview.md)*

---

## Troubleshooting

### CORTEX won't start. What should I check?

```bash
# 1. Check Python version
python --version  # Should be 3.9+

# 2. Check dependencies
pip list | grep -E "(cortex|pydantic|fastapi)"

# 3. Verify configuration
cortex config validate

# 4. Check database
cortex db status

# 5. View logs
cortex logs --tail 50
```

### How do I check audit logs?

```bash
# Recent entries
cortex audit list --limit 100

# Search by orchestrator
cortex audit search --orchestrator master-orchestrator

# Verify integrity
cortex audit verify

# Export for analysis
cortex audit export --format json --output audit.json
```

### Database is locked. How do I fix?

```bash
# 1. Check for other processes
lsof | grep governance.db

# 2. Enable WAL mode
cortex db enable-wal

# 3. Increase busy timeout
# In cortex-config.yaml:
database:
  busy_timeout_ms: 5000
```

*See: [Troubleshooting Guide](../01-getting-started/3-troubleshooting.md#database-issues)*

### Orchestrator times out. How do I increase timeout?

```yaml
# cortex-config.yaml
orchestrators:
  my-orchestrator:
    timeout_seconds: 60  # Increase from default 30
    
resilience:
  timeouts:
    request: 60.0
    orchestrator: 55.0
```

### How do I enable debug logging?

```bash
# Environment variable
export CORTEX_LOG_LEVEL=DEBUG

# Or in config
# cortex-config.yaml
logging:
  level: DEBUG
  format: detailed
  file: /var/log/cortex/debug.log
```

---

## Compliance & Security

### Is CORTEX HIPAA-compliant?

CORTEX provides **technical controls** that support HIPAA compliance:

- ✅ Audit trails (§164.308(a)(1)(ii)(D))
- ✅ Access controls (§164.308(a)(4))
- ✅ Encryption (§164.312(a)(2)(iv))
- ✅ Automatic log-off (§164.312(a)(2)(iii))

You must still:
- Sign BAAs with vendors
- Implement organizational policies
- Conduct risk assessments

*See: [Compliance Mappings](compliance-mappings.md#hipaa)*

### How is audit trail secured?

1. **Hash chain**: Tamper detection via cryptographic linking
2. **Encryption**: Encrypted at rest and in transit
3. **Immutability**: Entries cannot be modified
4. **Access control**: Only admins can query full trail
5. **Backup**: Automatic periodic backups

### Can I export audit logs for compliance?

Yes:

```bash
# Export all logs
cortex audit export --format json --output audit.json

# Export date range
cortex audit export --start 2026-01-01 --end 2026-01-31 --format csv

# Export for specific user
cortex audit export --user john.doe@example.com
```

### How do I handle sensitive data?

```python
from src.core.security import mask_sensitive

# Automatic masking in logs
logger.info(mask_sensitive({
    "username": "john",
    "password": "secret123",  # Will be masked
    "api_key": "key_abc"      # Will be masked
}))
```

### What encryption does CORTEX use?

- **At rest**: AES-256-GCM for database
- **In transit**: TLS 1.3 for API
- **Audit trail**: SHA-256 hashing
- **API keys**: bcrypt with salt

---

## Development & Contributing

### How do I contribute to CORTEX?

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

*See: [Contributing Guidelines](../07-contributing/1-contributing-guidelines.md)*

### What coding standards does CORTEX use?

- **Style**: PEP 8 with 100-char line length
- **Formatting**: black + isort
- **Type hints**: Required for all functions
- **Docstrings**: Google-style
- **Tests**: 80% minimum coverage

### How do I run the test suite?

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html

# Fast tests only
pytest tests/ -v -m "not slow"

# Specific component
pytest tests/unit/test_governance.py -v
```

### Can I extend CORTEX with plugins?

Yes! CORTEX supports:

1. **Custom orchestrators**: Extend `OrchestratorBase`
2. **Knowledge adapters**: Implement adapter interface
3. **Governance rules**: Add Tier 3 rules
4. **MCP tools**: Register custom tools

### Where can I get help?

1. **Documentation**: [docs/](../0-README.md)
2. **GitHub Issues**: Bug reports and questions
3. **GitHub Discussions**: General discussions
4. **Troubleshooting Guide**: [troubleshooting.md](../01-getting-started/3-troubleshooting.md)

---

## Still Have Questions?

- Check [Known Issues](known-issues.md) for common problems
- Search [GitHub Issues](https://github.com/asifhussain60/CORTEX/issues)
- Review [Troubleshooting Guide](../01-getting-started/3-troubleshooting.md)
- Open a new issue with the `question` label

---

**Document Version:** 1.0.0  
**Last Updated:** 2026-01-20  
**Questions Covered:** 75+
