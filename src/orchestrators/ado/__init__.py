"""
ADO Orchestrator Package

Azure DevOps work item management orchestrator with Planning System parity.

Components:
- ADOOrchestrator: Main orchestrator (5-phase workflow)
- ADOWorkflowPhases: Phase implementations
- ADOValidators: DoR/DoD validators
- ADOGenerators: Work item generators
- ADOFormatters: ADO-specific formatters

Version: 1.0.0
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from src.orchestrators.ado.ado_orchestrator import ADOOrchestrator, ADOPhase

__all__ = ["ADOOrchestrator", "ADOPhase"]
__version__ = "1.0.0"
