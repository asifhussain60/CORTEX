"""
CORTEX Brain Transfer System

Export and import brain patterns (Tier 2 knowledge graph) across machines
with intelligent conflict resolution.

Features:
- Export brain to YAML (human-readable, git-trackable)
- Import brain with intelligent conflict resolution
- Namespace-aware merging (cortex.* vs workspace.*)
- Weighted confidence averaging for similar patterns
- Audit trail of all merge decisions

Usage:
    # Python API
    from src.brain_transfer import BrainExporter, BrainImporter
    exporter = BrainExporter()
    exporter.export_brain(scope="workspace")
    
    # Natural language (via CORTEX)
    "export brain"
    "import brain from brain-export-20251117.yaml"
    
    # CLI
    python -m src.brain_transfer.cli export workspace
    python -m src.brain_transfer.cli import brain-export-20251117.yaml

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from .brain_exporter import BrainExporter
from .brain_importer import BrainImporter
from .cli import (
    execute_brain_export,
    execute_brain_import,
    handle_export_brain_request,
    handle_import_brain_request
)
from .plugin import BrainTransferPlugin, register_plugin

__all__ = [
    "BrainExporter",
    "BrainImporter",
    "execute_brain_export",
    "execute_brain_import",
    "handle_export_brain_request",
    "handle_import_brain_request",
    "BrainTransferPlugin",
    "register_plugin"
]
__version__ = "1.0.0"
