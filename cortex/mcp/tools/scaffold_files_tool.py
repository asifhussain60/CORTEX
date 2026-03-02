"""cortex_scaffold_files MCP tool — write arbitrary-language source files to disk.

Exposes FileFactory's file-creation capability through the MCP interface so that
repeatable playbooks (PB-STS-001 and successors) can scaffold real source files
without bypassing MCP.

Sharpen-the-Saw: Resolves GAP-007 (no MCP tool could write non-Python files).
Authority: CORE-002 | CORE-008 | CORE-011 | CORE-012 | CORE-028 | CORE-035

AC_START: PB-STS-001-RUN-2-SCAFFOLD-TOOL
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, List, Optional

from cortex.mcp.mcp_tool_base import (
    ConsolidatedTool,
    ToolCategory,
    ToolParameter,
    ToolResult,
)
from cortex.mcp.tools._shared import validate_orchestrator_context


class CortexScaffoldFiles(ConsolidatedTool):
    """Write one or more source files to disk via CORTEX FileFactory.

    Resolves GAP-007: previously no MCP tool could create arbitrary-language
    files (C#, TypeScript, YAML, etc.) during playbook execution, forcing
    bypasses of the MCP-only policy.

    Each entry in ``files`` is a dict with:
        path     (str, required) — relative path under ``root``
        content  (str, required) — full file content to write
        language (str, optional) — hint: csharp | typescript | python | yaml | markdown

    The tool creates parent directories as needed (equivalent to ``mkdir -p``).
    """

    @property
    def name(self) -> str:
        """Return the canonical tool name."""
        return "cortex_scaffold_files"

    @property
    def description(self) -> str:
        """Return the human-readable description."""
        return (
            "Write one or more source files to disk under a given root directory. "
            "Supports any language (C#, TypeScript, Python, YAML, Markdown, etc.). "
            "Creates parent directories automatically. "
            "Used by repeatable playbooks (PB-STS-001+) to scaffold refactored "
            "codebases through MCP without bypassing the MCP-only execution policy. "
            "Resolves GAP-007 from mcp-compatibility-gaps.yaml."
        )

    @property
    def category(self) -> ToolCategory:
        """Return the tool category."""
        return ToolCategory.OPERATIONS

    @property
    def parameters(self) -> List[ToolParameter]:
        """Return the parameter schema."""
        return [
            ToolParameter(
                name="root",
                type="string",
                description=(
                    "Absolute path to the root directory under which all files "
                    "will be written. Must exist or be creatable."
                ),
                required=True,
            ),
            ToolParameter(
                name="files",
                type="array",
                description=(
                    "List of file descriptors. Each item is an object with: "
                    "  path (str, required): relative path from root, "
                    "  content (str, required): full text content to write, "
                    "  language (str, optional): csharp|typescript|python|yaml|markdown."
                ),
                required=True,
            ),
            ToolParameter(
                name="overwrite",
                type="boolean",
                description="If true, overwrite existing files. Default: true.",
                required=False,
            ),
            ToolParameter(
                name="dry_run",
                type="boolean",
                description=(
                    "If true, validate inputs and return what would be written "
                    "without touching the filesystem."
                ),
                required=False,
            ),
            ToolParameter(
                name="session_id",
                type="string",
                description="Optional audit session UUID for trace persistence.",
                required=False,
            ),
        ]

    @property
    def supported_operations(self) -> List[str]:
        """Return the list of supported operations."""
        return ["write"]

    async def execute(self, **params: Any) -> ToolResult:
        """Write files to disk and return a summary result.

        Args:
            **params: Keyword arguments matching the parameter schema.

        Returns:
            ToolResult with data containing files_created, paths, and skipped.
        """
        # Enforce orchestrator routing in production
        _oc = params.get("orchestrator_context")
        if _oc is not None:
            validate_orchestrator_context(_oc)

        root_str: Optional[str] = params.get("root")
        files: List[Any] = params.get("files") or []
        overwrite: bool = params.get("overwrite", True)
        dry_run: bool = params.get("dry_run", False)
        session_id: Optional[str] = params.get("session_id")

        # ── Validate required params ──────────────────────────────────────
        if not root_str:
            return ToolResult(success=False, error="Parameter 'root' is required.")

        # ── Validate each file descriptor up-front ────────────────────────
        for i, fd in enumerate(files):
            if not isinstance(fd, dict):
                return ToolResult(
                    success=False,
                    error=f"files[{i}] must be a dict with 'path' and 'content' keys.",
                )
            if "path" not in fd:
                return ToolResult(
                    success=False,
                    error=f"files[{i}] is missing required key 'path'.",
                )
            if "content" not in fd:
                return ToolResult(
                    success=False,
                    error=f"files[{i}] is missing required key 'content'.",
                )

        if not files:
            return ToolResult(
                success=True,
                data={"files_created": 0, "paths": [], "skipped": [], "dry_run": dry_run},
                metadata={"session_id": session_id, "root": root_str},
            )

        root = Path(root_str)

        # ── Write files ───────────────────────────────────────────────────
        created_paths: List[str] = []
        skipped_paths: List[str] = []
        errors: List[str] = []

        for fd in files:
            rel_path: str = fd["path"]
            content: str = fd["content"]
            abs_path = root / rel_path

            if dry_run:
                created_paths.append(rel_path)
                continue

            try:
                if abs_path.exists() and not overwrite:
                    skipped_paths.append(rel_path)
                    continue

                abs_path.parent.mkdir(parents=True, exist_ok=True)
                abs_path.write_text(content, encoding="utf-8")
                created_paths.append(rel_path)

            except OSError as exc:
                errors.append(f"{rel_path}: {exc}")

        if errors:
            return ToolResult(
                success=False,
                error=f"Failed to write {len(errors)} file(s): {'; '.join(errors)}",
                data={
                    "files_created": len(created_paths),
                    "paths": created_paths,
                    "skipped": skipped_paths,
                    "errors": errors,
                },
                metadata={"session_id": session_id, "root": root_str},
            )

        return ToolResult(
            success=True,
            data={
                "files_created": len(created_paths),
                "paths": created_paths,
                "skipped": skipped_paths,
                "dry_run": dry_run,
            },
            metadata={"session_id": session_id, "root": root_str},
        )
