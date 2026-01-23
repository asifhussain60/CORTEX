# ⚡ CORTEX Production Deployment Quick Commands

**Status:** ✅ READY FOR DEPLOYMENT  
**Date:** 2026-01-23 | **Authority:** cortex-impl-map.yaml v3.9

---

## 🚀 Immediate Deployment (Copy-Paste Ready)

### Step 1: Verify Production Readiness
```bash
cd /Users/asifhussain/PROJECTS/CORTEX

# Run all production readiness tests (should show 88 PASSING)
python3 -m pytest tests/unit/orchestrators/test_orchestrator_discovery.py \
                   tests/unit/orchestrators/test_module_dependencies.py \
                   tests/unit/orchestrators/test_production_readiness.py -v

# Expected: "88 passed in 0.34s"
```

### Step 2: Verify Core Components Initialized
```bash
python3 << 'EOF'
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.brain.core.governance_registry import GovernanceRegistry
from cortex.orchestrators.tools.todo_manager import TodoManager

master = MasterOrchestrator.instance()
governance = GovernanceRegistry.instance()
todo_manager = TodoManager()

print("✅ CORTEX Production System Ready")
print("   - MasterOrchestrator: ✓")
print("   - GovernanceRegistry: ✓")
print("   - TodoManager: ✓")
EOF
```

### Step 3: Start MCP Server
```bash
# Start the MCP server (background process recommended)
python3 -m cortex.mcp.server --host 0.0.0.0 --port 5000

# Or with nohup for persistent background execution:
nohup python3 -m cortex.mcp.server --host 0.0.0.0 --port 5000 > mcp-server.log 2>&1 &
```

### Step 4: Test Multi-Turn Conversation
```bash
python3 << 'EOF'
from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
from cortex.core.orchestrator.conversation_protocol import ConversationProtocol

master = MasterOrchestrator.instance()
conversation = ConversationProtocol(master, max_turns=10, token_limit=20000)

# Execute a turn
result = conversation.execute_turn(
    user_input="Analyze the CORTEX system status",
    round_number=1,
    previous_context={}
)

print(f"Turn 1 Result: {result.decision}")
print(f"Continue: {result.should_continue}")
EOF
```

---

## 🔧 Operational Commands

### Governance Validation
```bash
# Validate all governance rules are loaded
python3 -m cortex.brain.core.governance_registry --validate

# Expected output shows Tier 0-3 rules operational
```

### Health Checks
```bash
# Check system health
python3 << 'EOF'
from cortex.api.health_endpoints import HealthEndpoints

health = HealthEndpoints()
status = health.get_health_status()

print(f"Liveness: {status.liveness}")
print(f"Readiness: {status.readiness}")
print(f"Components: {len(status.components)} healthy")
EOF
```

### View Audit Trail
```bash
# View recent audit log entries
python3 << 'EOF'
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger

logger = EnhancedAuditLogger.instance()
recent_entries = logger.get_recent_entries(limit=10)

for entry in recent_entries:
    print(f"{entry['timestamp']}: {entry['operation']} - {entry['status']}")
EOF
```

### Run Specific Test Suite
```bash
# Module discovery only (37 tests)
pytest tests/unit/orchestrators/test_orchestrator_discovery.py -v

# Module dependencies only (21 tests)
pytest tests/unit/orchestrators/test_module_dependencies.py -v

# Production readiness only (30 tests)
pytest tests/unit/orchestrators/test_production_readiness.py -v
```

---

## 📊 Monitoring Commands

### Check System Metrics
```bash
# View Prometheus metrics
curl http://localhost:9090/metrics | grep cortex

# Or via Python:
python3 << 'EOF'
from cortex.infrastructure.prometheus_metrics import PrometheusMetrics

metrics = PrometheusMetrics()
print(f"Operations/sec: {metrics.get_throughput()}")
print(f"p95 latency: {metrics.get_latency_percentile(95)}")
EOF
```

### Monitor Governance Compliance
```bash
# Get governance compliance report
python3 << 'EOF'
from cortex.brain.core.governance_registry import GovernanceRegistry

governance = GovernanceRegistry.instance()
report = governance.get_compliance_report()

print(f"Rules Evaluated: {report.rules_evaluated}")
print(f"Violations: {report.violations}")
print(f"Compliance Score: {report.compliance_score}%")
EOF
```

### Check MCP Tools Status
```bash
# List all registered tools
python3 << 'EOF'
from cortex.mcp.registry import get_mcp_tool_registry

registry = get_mcp_tool_registry()
tools = registry.get_all_tools()

print(f"Total MCP Tools: {len(tools)}")
for tool in tools:
    print(f"  - {tool['name']}: {tool['category']}")
EOF
```

---

## 🧠 Brain Tier Operations

### Load Domain Knowledge
```bash
# Load healthcare domain with CORTEX governance overlay
python3 << 'EOF'
from cortex.brain.core.knowledge_composer import KnowledgeComposer

composer = KnowledgeComposer()

composed = composer.load_domain(
    domain="healthcare",
    profile="healthcare-v1.0",
    tiers=[0, 1, 2, 3]
)

print(f"Domain Profile: {composed.domain}")
print(f"Governance Rules: {len(composed.governance_rules)}")
print(f"Knowledge Files: {len(composed.knowledge_files)}")
EOF
```

### Verify Tier Composition
```bash
# Verify Tier 0-3 governance is properly composed
python3 << 'EOF'
from cortex.brain.core.tier_composer import TierComposer

composer = TierComposer()

# Compose rules for production healthcare operation
rules = composer.compose_rules(
    tier0_rules=True,
    tier1_domains=["security", "compliance"],
    tier2_contexts=["production", "sensitive-data"],
    tier3_profiles=["healthcare-v1.0"]
)

print(f"Tier 0 (Core): {len(rules.tier0)} rules")
print(f"Tier 1 (Domain): {len(rules.tier1)} rules")
print(f"Tier 2 (Context): {len(rules.tier2)} rules")
print(f"Tier 3 (Profile): {len(rules.tier3)} rules")
EOF
```

---

## 📋 Todo Manager Operations

### Create Multi-Phase Task
```bash
python3 << 'EOF'
from cortex.orchestrators.tools.todo_manager import TodoManager

todo = TodoManager()

task = todo.create_task(
    task_id="IMPL-FEATURE-001",
    description="Implement new feature",
    phases=[
        {"id": 1, "title": "Design", "dependencies": []},
        {"id": 2, "title": "Implementation", "dependencies": [1]},
        {"id": 3, "title": "Testing", "dependencies": [2]},
        {"id": 4, "title": "Deployment", "dependencies": [3]}
    ]
)

print(f"Task Created: {task.task_id}")
print(f"Phases: {task.phase_count}")
EOF
```

### Track Phase Progress
```bash
python3 << 'EOF'
from cortex.orchestrators.tools.todo_manager import TodoManager

todo = TodoManager()

# Mark phase as in-progress
todo.mark_phase("IMPL-FEATURE-001", 1, "in-progress")

# Get status
status = todo.get_task_status("IMPL-FEATURE-001")
print(f"Current Phase: {status.current_phase}")
print(f"Progress: {status.completed_phases}/{status.total_phases}")
EOF
```

---

## 🛡️ Safety & Rollback

### Emergency Rollback
```bash
# If deployment needs to be rolled back
git reset --hard HEAD~1
git push origin HEAD --force

# Verify rollback
git log -1 --oneline
```

### Restore from Backup
```bash
# If domain knowledge YAMLs were lost (they're protected but here's recovery)
BACKUP_DIR="_backups/pre-sync-latest"

# Restore all tier knowledge
cp -r "$BACKUP_DIR/tier1-profiles/"* cortex_brain/tier1/profiles/
cp -r "$BACKUP_DIR/tier2-governance/"* cortex_brain/tier2/governance/
cp -r "$BACKUP_DIR/tier3-knowledge/"* cortex_brain/tier3/knowledge/

# Verify integrity
find cortex_brain/tier{1,2,3} -name "*.yaml" | wc -l
```

---

## 🔍 Troubleshooting

### Module Not Found
```bash
# Verify Python path
python3 -c "import sys; print('\n'.join(sys.path))"

# Verify cortex package is discoverable
python3 -c "from cortex import __version__; print('✓ cortex package found')"
```

### Governance Violations
```bash
# Check what governance rules are blocking
python3 << 'EOF'
from cortex.brain.core.governance_registry import GovernanceRegistry

governance = GovernanceRegistry.instance()
violations = governance.get_violations()

for violation in violations:
    print(f"Rule: {violation.rule_id}")
    print(f"Severity: {violation.severity}")
    print(f"Message: {violation.message}")
EOF
```

### Test Failures
```bash
# Run tests with verbose output
pytest tests/unit/orchestrators/ -v -s

# Run with coverage
pytest tests/ --cov=cortex --cov-report=html

# Run specific test
pytest tests/unit/orchestrators/test_production_readiness.py::TestCORTEXSystemReady::test_system_components_initialized -v
```

---

## ✅ Deployment Verification Checklist

Before declaring deployment successful:

```bash
# 1. All tests passing
pytest tests/unit/orchestrators/test_*.py -v 2>&1 | tail -5
# Expected: "88 passed"

# 2. Core components initialized
python3 -c "from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator; MasterOrchestrator.instance()" && echo "✓"

# 3. MCP server running
curl -s http://localhost:5000/health | grep -q "ok" && echo "✓" || echo "MCP server not responding"

# 4. Governance enforced
python3 -m cortex.brain.core.governance_registry --validate && echo "✓"

# 5. No data loss
find cortex_brain/tier{1,2,3} -name "*.yaml" | wc -l
# Expected: 61+ files
```

---

## 📞 Support References

| Component | Status Command | Log Location |
|-----------|---|---|
| MasterOrchestrator | `python3 -c "from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator; MasterOrchestrator.instance()"` | `/var/log/cortex/orchestrator.log` |
| GovernanceRegistry | `python3 -m cortex.brain.core.governance_registry --validate` | `/var/log/cortex/governance.log` |
| TodoManager | `python3 -c "from cortex.orchestrators.tools.todo_manager import TodoManager; TodoManager()"` | `/var/log/cortex/todo.log` |
| MCP Server | `curl http://localhost:5000/health` | `./mcp-server.log` |

---

**Quick Deploy Summary:**
```bash
# All-in-one deployment check
cd /Users/asifhussain/PROJECTS/CORTEX && \
python3 -m pytest tests/unit/orchestrators/test_*.py -q && \
echo "✅ Production ready - start with: python3 -m cortex.mcp.server"
```

**Status:** ✅ READY FOR PRODUCTION DEPLOYMENT
