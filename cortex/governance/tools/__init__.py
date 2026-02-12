"""
Governance tools module.

This module contains standalone command-line tools for governance enforcement.
"""

from cortex.governance.tools.lint_instruction_files import InstructionFileLinter

__all__ = ["InstructionFileLinter"]
