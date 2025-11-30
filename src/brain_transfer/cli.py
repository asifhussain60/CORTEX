#!/usr/bin/env python3
"""
CORTEX Brain Transfer CLI

Command-line interface for brain export/import operations.
Integrates with CORTEX command registry for natural language access.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from .brain_exporter import BrainExporter
from .brain_importer import BrainImporter

logger = logging.getLogger(__name__)


def execute_brain_export(
    scope: str = "workspace",
    min_confidence: float = 0.5,
    output_path: Optional[str] = None
) -> Dict[str, Any]:
    """
    Execute brain export operation.
    
    Args:
        scope: Export scope ("workspace", "cortex", "all")
        min_confidence: Minimum confidence threshold
        output_path: Custom output path (optional)
    
    Returns:
        Result dictionary with status and details
    """
    try:
        exporter = BrainExporter()
        
        result = exporter.export_brain(
            scope=scope,
            min_confidence=min_confidence,
            output_path=Path(output_path) if output_path else None
        )
        
        return {
            "success": True,
            "operation": "export_brain",
            "export_path": str(result["export_path"]),
            "patterns_exported": result["patterns_exported"],
            "total_size_bytes": result["total_size_bytes"],
            "message": f"✅ Exported {result['patterns_exported']} patterns to {result['export_path']}"
        }
        
    except Exception as e:
        logger.error(f"Brain export failed: {e}", exc_info=True)
        return {
            "success": False,
            "operation": "export_brain",
            "error": str(e),
            "message": f"❌ Brain export failed: {e}"
        }


def execute_brain_import(
    import_path: str,
    auto_resolve: bool = True
) -> Dict[str, Any]:
    """
    Execute brain import operation.
    
    Args:
        import_path: Path to YAML file to import
        auto_resolve: Auto-resolve conflicts without manual review
    
    Returns:
        Result dictionary with status and details
    """
    try:
        importer = BrainImporter()
        
        result = importer.import_brain(
            import_path=Path(import_path),
            auto_resolve_conflicts=auto_resolve
        )
        
        return {
            "success": True,
            "operation": "import_brain",
            "patterns_imported": result["patterns_imported"],
            "conflicts_resolved": result["conflicts_resolved"],
            "merge_decisions": result["merge_decisions"],
            "audit_trail_path": str(result["audit_trail_path"]),
            "message": f"✅ Imported {result['patterns_imported']} patterns with {result['conflicts_resolved']} conflicts auto-resolved"
        }
        
    except Exception as e:
        logger.error(f"Brain import failed: {e}", exc_info=True)
        return {
            "success": False,
            "operation": "import_brain",
            "error": str(e),
            "message": f"❌ Brain import failed: {e}"
        }


# Natural language handlers for router integration
def handle_export_brain_request(user_request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Handle natural language export brain requests.
    
    Examples:
        "export brain"
        "export cortex patterns"
        "share my learned knowledge"
    
    Args:
        user_request: User's natural language request
        context: Optional context with parameters
    
    Returns:
        Execution result
    """
    # Extract parameters from request or context
    scope = "workspace"  # Default
    min_confidence = 0.5  # Default
    
    if context:
        scope = context.get("scope", scope)
        min_confidence = context.get("min_confidence", min_confidence)
    
    # Parse scope from natural language
    if "cortex" in user_request.lower() and "all" not in user_request.lower():
        scope = "cortex"
    elif "all" in user_request.lower() or "everything" in user_request.lower():
        scope = "all"
    
    return execute_brain_export(
        scope=scope,
        min_confidence=min_confidence
    )


def handle_import_brain_request(user_request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Handle natural language import brain requests.
    
    Examples:
        "import brain from brain-export-20251117.yaml"
        "load knowledge from teammate"
        "merge patterns"
    
    Args:
        user_request: User's natural language request
        context: Optional context with parameters
    
    Returns:
        Execution result
    """
    # Extract file path from request or context
    import_path = None
    
    if context and "import_path" in context:
        import_path = context["import_path"]
    else:
        # Try to extract .yaml filename from request
        words = user_request.split()
        for word in words:
            if word.endswith(".yaml") or word.endswith(".yml"):
                import_path = word
                break
    
    if not import_path:
        # Check for most recent export in exports directory
        try:
            exporter = BrainExporter()
            exports = sorted(exporter.export_dir.glob("brain-export-*.yaml"), reverse=True)
            if exports:
                import_path = str(exports[0])
        except Exception:
            pass
    
    if not import_path:
        return {
            "success": False,
            "operation": "import_brain",
            "error": "No import file specified",
            "message": "❌ Please specify a YAML file to import (e.g., 'import brain from brain-export-20251117.yaml')"
        }
    
    return execute_brain_import(
        import_path=import_path,
        auto_resolve=True
    )


if __name__ == "__main__":
    # CLI test
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  Export: python -m src.brain_transfer.cli export [scope] [min_confidence]")
        print("  Import: python -m src.brain_transfer.cli import <file.yaml>")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "export":
        scope = sys.argv[2] if len(sys.argv) > 2 else "workspace"
        min_confidence = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
        result = execute_brain_export(scope, min_confidence)
        print(result["message"])
        
    elif command == "import":
        if len(sys.argv) < 3:
            print("Error: Import requires a file path")
            sys.exit(1)
        import_path = sys.argv[2]
        result = execute_brain_import(import_path)
        print(result["message"])
        
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
