import sys
sys.path.insert(0, 'src')

from pathlib import Path
from operations.modules.admin.system_alignment_orchestrator import SystemAlignmentOrchestrator

orchestrator = SystemAlignmentOrchestrator({'project_root': Path('.')})

features = [
    ('DiagramRegenerationOrchestrator', 'orchestrator'),
    ('CommitOrchestrator', 'orchestrator'),
    ('OnboardingOrchestrator', 'orchestrator')
]

for name, ftype in features:
    print(f"\n=== {name} ===")
    has_guide = orchestrator._check_guide_file_exists(name, ftype)
    print(f"Has guide file: {has_guide}")
