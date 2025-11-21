#!/usr/bin/env python3
"""
Temporary script to generate all enterprise documentation
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / 'cortex-brain' / 'admin' / 'scripts' / 'documentation'))
sys.path.insert(0, str(Path(__file__).parent / 'cortex-brain' / 'admin' / 'documentation'))

from enterprise_documentation_orchestrator import EnterpriseDocumentationOrchestrator

print("🚀 Starting comprehensive documentation generation...")
print("")

orchestrator = EnterpriseDocumentationOrchestrator()
result = orchestrator.execute(
    profile="comprehensive",  # Options: 'quick', 'standard', 'comprehensive'
    dry_run=False
)

print("")
print("=== Generation Summary ===")
print(f"Success: {result.success}")
print(f"Status: {result.status}")
print(f"Message: {result.message}")
if result.data:
    print(f"Data: {result.data}")
print(f"Duration: {result.duration_seconds:.1f}s")
print("")

if result.errors:
    print("=== Errors ===")
    for error in result.errors:
        print(f"❌ {error}")
    print("")

print("✅ Documentation generation complete!")
