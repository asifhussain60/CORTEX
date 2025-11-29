"""Quick alignment validation after documentation."""
from src.discovery.orchestrator_scanner import OrchestratorScanner
from src.discovery.entry_point_scanner import EntryPointScanner
from pathlib import Path

# Scan orchestrators
project_root = Path(__file__).parent
scanner = OrchestratorScanner(project_root)
orchestrators = scanner.discover()

print(f"\n📊 Orchestrator Status:")
print(f"   Total: {len(orchestrators)}")

# Check for documentation
docs_dir = Path(".github/prompts/modules")
doc_files = {f.stem: f for f in docs_dir.glob("*.md")}

# Improved mappings
doc_mappings = {
    "TDDWorkflowOrchestrator": ["tdd-mastery-guide", "tdd-workflow"],
    "OptimizeCortexOrchestrator": ["optimize-cortex-guide", "optimize"],
    "WorkflowOrchestrator": ["workflow-orchestrator-guide", "workflow"],
    "SystemAlignmentOrchestrator": ["system-alignment-guide", "alignment"],
    "CleanupOrchestrator": ["cleanup-guide", "cleanup"],
    "DesignSyncOrchestrator": ["design-sync-guide", "design"],
    "PublishBranchOrchestrator": ["publish-guide", "publish"]
}

for name in sorted(orchestrators.keys()):
    # Check for corresponding documentation
    has_docs = False
    if name in doc_mappings:
        for pattern in doc_mappings[name]:
            if any(pattern in doc_file.lower() for doc_file in doc_files.keys()):
                has_docs = True
                break
    
    docs = "✅" if has_docs else "❌"
    print(f"   {docs} {name}")

# Check wiring
ep_scanner = EntryPointScanner(project_root)
entry_points = ep_scanner.discover()
orphaned, ghosts = ep_scanner.validate_wiring(orchestrators)

print(f"\n🔌 Wiring Status:")
wired_names = set()
for trigger, metadata in entry_points.items():
    orch_name = metadata['expected_orchestrator']
    if orch_name and orch_name in orchestrators:
        wired_names.add(orch_name)

for name in sorted(orchestrators.keys()):
    status = "✅" if name in wired_names else "❌"
    print(f"   {status} {name}")

print(f"\n📈 Summary:")
documented = sum(1 for name in orchestrators.keys() if name in doc_mappings and any(any(pattern in doc_file.lower() for doc_file in doc_files.keys()) for pattern in doc_mappings[name]))
wired = len(wired_names)
print(f"   Documented: {documented}/{len(orchestrators)} ({documented*100//len(orchestrators) if orchestrators else 0}%)")
print(f"   Wired: {wired}/{len(orchestrators)} ({wired*100//len(orchestrators) if orchestrators else 0}%)")
print(f"   Orphaned triggers: {len(orphaned)}")
print(f"   Ghost features: {len(ghosts)}")
