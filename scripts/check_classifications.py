from src.discovery.orchestrator_scanner import OrchestratorScanner
from src.discovery.agent_scanner import AgentScanner
from pathlib import Path

# Discover all features
orch_scanner = OrchestratorScanner(Path('.'))
orchestrators = orch_scanner.discover()

agent_scanner = AgentScanner(Path('.'))
agents = agent_scanner.discover()

print("=== ORCHESTRATOR CLASSIFICATIONS ===")
for name in sorted(orchestrators.keys()):
    classification = orchestrators[name].get('classification', 'unknown')
    print(f"{name}: {classification}")

print("\n=== AGENT CLASSIFICATIONS ===")
for name in sorted(agents.keys()):
    classification = agents[name].get('classification', 'unknown')
    print(f"{name}: {classification}")

# Count by classification
all_features = {**orchestrators, **agents}
production = [n for n, m in all_features.items() if m.get('classification') == 'production']
admin = [n for n, m in all_features.items() if m.get('classification') == 'admin']
internal = [n for n, m in all_features.items() if m.get('classification') == 'internal']

print(f"\n=== SUMMARY ===")
print(f"Production: {len(production)}")
print(f"Admin: {len(admin)}")
print(f"Internal: {len(internal)}")
print(f"Total: {len(all_features)}")
