"""Debug script to see what agents are discovered."""
from src.discovery.agent_scanner import AgentScanner
from pathlib import Path

scanner = AgentScanner(Path.cwd())
agents = scanner.discover()

print("Brain/Ingestion Related Agents:")
for name, meta in agents.items():
    if 'Ingestion' in name or 'Brain' in name:
        print(f"  {name}: {meta['path'].name}")

print(f"\nTotal agents discovered: {len(agents)}")
