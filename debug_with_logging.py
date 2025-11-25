"""
Debug script with logging enabled.
"""
import logging
logging.basicConfig(level=logging.INFO)

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.operations.modules.admin.system_alignment_orchestrator import SystemAlignmentOrchestrator

project_root = Path(__file__).parent
orchestrator = SystemAlignmentOrchestrator({'project_root': project_root})
report = orchestrator.run_full_validation()

print(f"\nTDDWorkflowOrchestrator score: {report.feature_scores['TDDWorkflowOrchestrator'].score}%")
print(f"Documented: {report.feature_scores['TDDWorkflowOrchestrator'].documented}")
