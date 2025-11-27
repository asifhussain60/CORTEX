"""Debug the actual integration scoring logic."""
import sys
from pathlib import Path

cortex_root = Path(__file__).parent
sys.path.insert(0, str(cortex_root / "src"))

from operations.modules.admin.system_alignment_orchestrator import SystemAlignmentOrchestrator

project_root = cortex_root
orchestrator = SystemAlignmentOrchestrator(context={"project_root": project_root})

critical = [
    ("HolisticCleanupOrchestrator", "orchestrator"),
    ("SetupEPMOrchestrator", "orchestrator"),
    ("ADOWorkItemOrchestrator", "orchestrator"),
    ("DemoOrchestrator", "orchestrator"),
    ("UnifiedEntryPointOrchestrator", "orchestrator")
]

for name, feature_type in critical:
    print(f"\n{'='*60}")
    print(f"{name}")
    print('='*60)
    
    # Call the actual validation method used by alignment orchestrator
    score = orchestrator._calculate_integration_score(name, feature_type, {})
    
    print(f"✓ Discovered: {score.discovered}")
    print(f"✓ Imported: {score.imported}")
    print(f"✓ Instantiated: {score.instantiated}")
    print(f"✓ Documented: {score.documented}")
    print(f"✓ Tested: {score.tested}")
    print(f"✓ Wired: {score.wired}")
    print(f"✓ Optimized: {score.optimized}")
    print(f"\n🎯 Total Score: {score.get_score()}%")
