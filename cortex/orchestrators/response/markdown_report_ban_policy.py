"""Markdown Report Ban Policy - Prevent Report/Summary File Generation

Enforces aggressive prevention of markdown report artifacts:
- Blocks: *-summary.md, *-completion.md, *-report.md, *-progress.md, etc.
- All reporting output is INLINE CHAT ONLY
- Internal persistence: Use JSON + existing audit logs, never markdown

Authority: CORE-002 (copilot-instructions.md) + chat02.txt (Change Request)
Author: CORTEX Framework
Date: 2026-02-06
Version: 1.0.0
"""

import re
from pathlib import Path
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from abc import ABC, abstractmethod


class ArtifactType(str, Enum):
    """Types of artifacts that might be generated"""
    
    # Report artifacts (BLOCKED)
    SUMMARY_REPORT = "summary_report"
    COMPLETION_REPORT = "completion_report"
    PROGRESS_REPORT = "progress_report"
    EXECUTION_REPORT = "execution_report"
    STATUS_DOC = "status_doc"
    RUN_LOG = "run_log"
    
    # Allowed artifact types
    CONFIGURATION = "configuration"  # configs are allowed
    DOCUMENTATION = "documentation"  # docs allowed when product-required
    DATA = "data"  # JSON data allowed
    TEST_RESULTS = "test_results"  # Test results in JSON/YAML


class BlockReason(str, Enum):
    """Reason for blocking file write"""
    
    REPORT_INTENT = "Inline chat output only. Do not create markdown report files."
    SUMMARY_PATTERN = "Markdown summaries blocked by CORE-002"
    COMPLETION_PATTERN = "Completion reports blocked by CORE-002"
    PROGRESS_PATTERN = "Progress logs blocked by CORE-002"
    GENERIC_REPORT = "Report-intent markdown generation blocked"


@dataclass
class BlockedFileWrite:
    """Represents a blocked file write attempt"""
    
    file_path: Path
    artifact_type: ArtifactType
    reason: BlockReason
    context: Optional[str] = None
    suggested_alternative: Optional[str] = None


class MarkdownReportBanPolicy:
    """Enforces prohibition on report-intent markdown file generation"""
    
    # Patterns that trigger REPORT intent (blocked)
    REPORT_PATTERNS = {
        # Summary patterns
        r".*-summary\.md$": ArtifactType.SUMMARY_REPORT,
        r".*[Ss]ummary.*\.md$": ArtifactType.SUMMARY_REPORT,
        r".*/summary/.*\.md$": ArtifactType.SUMMARY_REPORT,
        
        # Completion patterns
        r".*-completion\.md$": ArtifactType.COMPLETION_REPORT,
        r".*-completion-.*\.md$": ArtifactType.COMPLETION_REPORT,
        r".*[Cc]ompletion.*\.md$": ArtifactType.COMPLETION_REPORT,
        r".*/completion/.*\.md$": ArtifactType.COMPLETION_REPORT,
        r".*-COMPLETION.*\.md$": ArtifactType.COMPLETION_REPORT,
        
        # Progress patterns
        r".*-progress\.md$": ArtifactType.PROGRESS_REPORT,
        r".*[Pp]rogress.*\.md$": ArtifactType.PROGRESS_REPORT,
        r".*/progress/.*\.md$": ArtifactType.PROGRESS_REPORT,
        
        # Status patterns
        r".*-status\.md$": ArtifactType.STATUS_DOC,
        r".*[Ss]tatus.*\.md$": ArtifactType.STATUS_DOC,
        r".*/status/.*\.md$": ArtifactType.STATUS_DOC,
        
        # Execution patterns
        r".*-run\.md$": ArtifactType.RUN_LOG,
        r".*[Ee]xecution.*\.md$": ArtifactType.EXECUTION_REPORT,
        r".*/execution/.*\.md$": ArtifactType.EXECUTION_REPORT,
        
        # Report patterns
        r".*-report\.md$": ArtifactType.EXECUTION_REPORT,
        r".*[Rr]eport.*\.md$": ArtifactType.EXECUTION_REPORT,
        r".*/report[s]?/.*\.md$": ArtifactType.EXECUTION_REPORT,
    }
    
    # Allowed patterns (whitelisted locations)
    ALLOWED_PATTERNS = {
        # Documentation that may be modified for product correctness
        r"^docs/.*\.md$",
        r"^\.?github/.*\.md$",
        r"^README\.md$",
        
        # Configuration documentation
        r"^[Cc]onfig.*\.md$",
    }
    
    def __init__(self, workspace_root: Optional[Path] = None):
        """Initialize policy"""
        self.workspace_root = workspace_root or Path.cwd()
        self.blocked_writes: List[BlockedFileWrite] = []
    
    def can_write_file(
        self,
        file_path: Path,
        intent: Optional[str] = None,
        is_report: bool = False
    ) -> Tuple[bool, Optional[str]]:
        """
        Check if file can be written
        
        Args:
            file_path: Path to file to write
            intent: User intent (e.g., "REPORT", "SUMMARY", "COMPLETION")
            is_report: Explicit flag that this is report-intent
        
        Returns:
            (can_write, reason_if_blocked)
        """
        # Normalize path
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        # Make relative to workspace if possible
        try:
            rel_path = file_path.relative_to(self.workspace_root)
        except ValueError:
            rel_path = file_path
        
        path_str = str(rel_path).replace("\\", "/")
        
        # Check report patterns (always blocked)
        for pattern, artifact_type in self.REPORT_PATTERNS.items():
            if re.match(pattern, path_str, re.IGNORECASE):
                reason = f"Markdown report artifact blocked: {artifact_type.value}"
                self.blocked_writes.append(BlockedFileWrite(
                    file_path=file_path,
                    artifact_type=artifact_type,
                    reason=BlockReason.REPORT_INTENT,
                    context=intent
                ))
                return False, reason
        
        # Explicit report intent flag
        if is_report or (intent and "report" in intent.lower()):
            return False, BlockReason.REPORT_INTENT.value
        
        # Check if in allowed list
        for allowed_pattern in self.ALLOWED_PATTERNS:
            if re.match(allowed_pattern, path_str):
                return True, None
        
        # Markdown files outside allowed locations require scrutiny
        if path_str.endswith(".md"):
            # Check if it looks like a run artifact (in _workspaces/)
            if "_workspaces" in path_str and ".chats" not in path_str:
                return False, "Markdown files in _workspaces/ must be for chat sessions only"
        
        return True, None
    
    def block_write_attempt(
        self,
        file_path: Path,
        reason: str,
        context: Optional[str] = None
    ) -> None:
        """Record a blocked write attempt for audit"""
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        self.blocked_writes.append(BlockedFileWrite(
            file_path=file_path,
            artifact_type=ArtifactType.EXECUTION_REPORT,
            reason=BlockReason.GENERIC_REPORT,
            context=context
        ))
    
    def get_audit_trail(self) -> List[Dict[str, Any]]:
        """Get audit trail of blocked writes"""
        return [
            {
                "file_path": str(bw.file_path),
                "artifact_type": bw.artifact_type.value,
                "reason": bw.reason.value,
                "context": bw.context
            }
            for bw in self.blocked_writes
        ]
    
    def suggest_alternative(
        self,
        blocked_file: Path,
        content: str,
        intent: str = "report"
    ) -> Optional[str]:
        """
        Suggest alternative to markdown report
        
        Args:
            blocked_file: Blocked file path
            content: Content that would have been written
            intent: What was user trying to do
        
        Returns:
            Suggestion for how to persist data appropriately
        """
        suggestions = []
        
        if intent.lower() in ["summary", "report", "completion"]:
            suggestions.append(
                "💡 Use inline chat output instead: "
                "Provide findings directly in Copilot Chat (3 sections: Asked, Recommended, Next Steps)"
            )
        
        if intent.lower() == "progress":
            suggestions.append(
                "💡 Track progress via governance.db (audit logs) instead of markdown files"
            )
        
        if len(content) > 100:
            suggestions.append(
                "💡 For large outputs: Use JSON in existing storage (cortex_brain/state/) "
                "rather than markdown reports"
            )
        
        return " | ".join(suggestions) if suggestions else None


class FileWriteInterceptor(ABC):
    """Base class for intercepting file writes"""
    
    @abstractmethod
    def before_write(
        self,
        file_path: Path,
        content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str]]:
        """
        Intercept file write before it happens
        
        Returns:
            (should_proceed, error_message_if_blocked)
        """
        pass
    
    @abstractmethod
    def after_write(
        self,
        file_path: Path,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """Record file write for audit"""
        pass


class ReportBanFileWriteInterceptor(FileWriteInterceptor):
    """File write interceptor that enforces report ban policy"""
    
    def __init__(self, workspace_root: Optional[Path] = None):
        """Initialize interceptor"""
        self.policy = MarkdownReportBanPolicy(workspace_root)
        self.audit_log: List[Dict[str, Any]] = []
    
    def before_write(
        self,
        file_path: Path,
        content: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, Optional[str]]:
        """Check if write is allowed"""
        intent = context.get("intent") if context else None
        is_report = context.get("is_report", False) if context else False
        
        can_write, reason = self.policy.can_write_file(
            file_path,
            intent=intent,
            is_report=is_report
        )
        
        if not can_write:
            # Log attempt
            self.audit_log.append({
                "action": "BLOCKED",
                "file_path": str(file_path),
                "reason": reason,
                "intent": intent
            })
            return False, reason
        
        return True, None
    
    def after_write(
        self,
        file_path: Path,
        success: bool,
        error: Optional[str] = None
    ) -> None:
        """Record write attempt"""
        self.audit_log.append({
            "action": "ALLOWED",
            "file_path": str(file_path),
            "success": success,
            "error": error
        })
    
    def get_blocked_attempts(self) -> List[Dict[str, Any]]:
        """Get list of blocked write attempts"""
        return [
            entry for entry in self.audit_log
            if entry.get("action") == "BLOCKED"
        ]


# Export public API
__all__ = [
    "MarkdownReportBanPolicy",
    "ReportBanFileWriteInterceptor",
    "BlockedFileWrite",
    "ArtifactType",
    "BlockReason",
    "FileWriteInterceptor",
]
