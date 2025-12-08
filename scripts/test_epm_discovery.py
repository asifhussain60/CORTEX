"""Test EPM feature discovery"""
import sys
from pathlib import Path

# Add project root
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.epm_documentation_orchestrator import DocumentationOrchestrator
import json

# Test discovery
orchestrator = DocumentationOrchestrator()
results = orchestrator._discover_new_features()

print(f"Total Discovered: {results['total_discovered']}")
print(f"Total Unregistered: {results['total_unregistered']}")
print(f"\nFirst 5 Unregistered Features:")
print(json.dumps(results['unregistered'][:5], indent=2))

print(f"\n\nSample Orchestrator Info:")
if results['orchestrators']:
    sample_name = list(results['orchestrators'].keys())[0]
    print(json.dumps({
        sample_name: results['orchestrators'][sample_name]
    }, indent=2, default=str))
