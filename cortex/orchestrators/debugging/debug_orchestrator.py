"""
CORTEX Debug Orchestrator
=========================

Main orchestration coordinator for comprehensive debugging workflows.
Coordinates injection, capture, analysis, fix-plan generation, and cleanup.

Author: CORTEX
Version: 1.0.0
Phase: Phase 21.5 - Universal Debugging

MCP Tools Exposed:
- cortex_debug_inject: Inject debug markers into target files
- cortex_debug_capture: Capture logs during execution
- cortex_debug_analyze: Analyze captured logs for issues
- cortex_debug_cleanup: Remove debug markers cleanly
- cortex_debug_full_cycle: Run complete debug workflow
"""

import json
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Unique marker prefix - easily grep-able across all languages


class DebugPhase(Enum):
    """Debug workflow phases."""
    INIT = "INIT"
    INJECT = "INJECT"
    CAPTURE = "CAPTURE"
    ANALYZE = "ANALYZE"
    FIX_PLAN = "FIX_PLAN"
    CLEANUP = "CLEANUP"
    COMPLETE = "COMPLETE"


class DebugSeverity(Enum):
    """Issue severity levels."""
    CRITICAL = "CRITICAL"  # Blocking issues (crashes, data loss)
    HIGH = "HIGH"          # Race conditions, integration failures
    MEDIUM = "MEDIUM"      # Performance issues, timing problems
    LOW = "LOW"            # Warnings, non-blocking issues
    INFO = "INFO"          # Informational traces


class LanguageType(Enum):
    """Supported language types for debugging."""
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    PYTHON = "python"
    HTML = "html"
    CSS = "css"
    YAML = "yaml"
    JSON = "json"
    UNKNOWN = "unknown"


@dataclass
class DebugSession:
    """Represents a debug session with all metadata."""

    session_id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    repo_path: Path = field(default_factory=Path)
    start_time: datetime = field(default_factory=datetime.now)
    end_time: Optional[datetime] = None
    phase: DebugPhase = DebugPhase.INIT

    # Injection metadata
    injected_files: List[str] = field(default_factory=list)
    injection_count: int = 0
    backup_dir: Optional[Path] = None

    # Capture metadata
    captured_logs: List[Dict[str, Any]] = field(default_factory=list)
    cortex_markers: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[Dict[str, Any]] = field(default_factory=list)
    warnings: List[Dict[str, Any]] = field(default_factory=list)

    # Analysis metadata
    detected_issues: List[Dict[str, Any]] = field(default_factory=list)
    race_conditions: List[Dict[str, Any]] = field(default_factory=list)
    integration_breaks: List[Dict[str, Any]] = field(default_factory=list)
    fix_plan: Optional[Dict[str, Any]] = None

    # Cleanup metadata
    cleaned_files: List[str] = field(default_factory=list)
    cleanup_verified: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for serialization."""
        return {
            "session_id": self.session_id,
            "repo_path": str(self.repo_path),
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "phase": self.phase.value,
            "injected_files": self.injected_files,
            "injection_count": self.injection_count,
            "backup_dir": str(self.backup_dir) if self.backup_dir else None,
            "captured_logs_count": len(self.captured_logs),
            "cortex_markers_count": len(self.cortex_markers),
            "errors_count": len(self.errors),
            "warnings_count": len(self.warnings),
            "detected_issues_count": len(self.detected_issues),
            "race_conditions_count": len(self.race_conditions),
            "integration_breaks_count": len(self.integration_breaks),
            "fix_plan": self.fix_plan,
            "cleaned_files": self.cleaned_files,
            "cleanup_verified": self.cleanup_verified,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "DebugSession":
        """Create session from dictionary."""
        session = cls()
        session.session_id = data.get("session_id", session.session_id)
        session.repo_path = Path(data.get("repo_path", "."))
        session.start_time = datetime.fromisoformat(data["start_time"]) if data.get("start_time") else datetime.now()
        session.end_time = datetime.fromisoformat(data["end_time"]) if data.get("end_time") else None
        session.phase = DebugPhase(data.get("phase", "INIT"))
        session.injected_files = data.get("injected_files", [])
        session.injection_count = data.get("injection_count", 0)
        session.backup_dir = Path(data["backup_dir"]) if data.get("backup_dir") else None
        session.fix_plan = data.get("fix_plan")
        session.cleaned_files = data.get("cleaned_files", [])
        session.cleanup_verified = data.get("cleanup_verified", False)
        return session


@dataclass
class DebugMarker:
    """Represents a single debug marker with all context."""

    session_id: str
    phase: str
    file: str
    line: int
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    severity: DebugSeverity = DebugSeverity.INFO
    context: Dict[str, Any] = field(default_factory=dict)

    def to_log_string(self) -> str:
        """Generate the log string for injection."""
        return f'{marker} {self.message}'

    @classmethod
    def parse(cls, log_text: str) -> Optional["DebugMarker"]:
        """Parse a log string back into a DebugMarker."""
        import re
        match = re.match(pattern, log_text)
        if match:
            return cls(
                session_id=match.group(1),
                phase=match.group(2),
                file=match.group(3),
                line=int(match.group(4)),
                message=match.group(5),
            )
        return None


class DebugOrchestrator:
    """
    Main orchestration coordinator for comprehensive debugging.

    Provides a complete debugging workflow:
    1. INJECT: Insert debug markers into target files
    2. CAPTURE: Collect all console output during test execution
    3. ANALYZE: Detect race conditions, integration issues, root causes
    4. FIX_PLAN: Generate comprehensive fix recommendations
    5. CLEANUP: Remove all debug markers cleanly

    Supports multiple languages: JavaScript, TypeScript, Python, HTML
    """

    def __init__(
        self,
        repo_path: Path,
        output_dir: Optional[Path] = None,
        session_id: Optional[str] = None,
    ):
        """
        Initialize the Debug Orchestrator.

        Args:
            repo_path: Path to the repository to debug
            output_dir: Directory for debug artifacts (default: .cortex-debug/)
            session_id: Optional session ID (auto-generated if not provided)
        """
        self.repo_path = Path(repo_path).resolve()
        self.output_dir = output_dir or (self.repo_path / ".cortex-debug")
        self.session = DebugSession(
            session_id=session_id or uuid.uuid4().hex[:8],
            repo_path=self.repo_path,
        )

        # Lazy-loaded components
        self._injector = None
        self._capture = None
        self._analyzer = None
        self._cleanup = None

        logger.info(f"DebugOrchestrator initialized for {self.repo_path}")
        logger.info(f"Session ID: {self.session.session_id}")

    @property
    def injector(self):
        """Lazy-load the debug injector."""
        if self._injector is None:
            from cortex.orchestrators.debugging.debug_injector import DebugInjector
            self._injector = DebugInjector(
                session_id=self.session.session_id,
                repo_path=self.repo_path,
                output_dir=self.output_dir,
            )
        return self._injector

    @property
    def capture(self):
        """Lazy-load the debug capture."""
        if self._capture is None:
            from cortex.orchestrators.debugging.debug_capture import DebugCapture
            self._capture = DebugCapture(
                session_id=self.session.session_id,
                output_dir=self.output_dir,
            )
        return self._capture

    @property
    def analyzer(self):
        """Lazy-load the debug analyzer."""
        if self._analyzer is None:
            from cortex.orchestrators.debugging.debug_analyzer import DebugAnalyzer
            self._analyzer = DebugAnalyzer(
                session_id=self.session.session_id,
                output_dir=self.output_dir,
            )
        return self._analyzer

    @property
    def cleanup_handler(self):
        """Lazy-load the debug cleanup."""
        if self._cleanup is None:
            from cortex.orchestrators.debugging.debug_cleanup import DebugCleanup
            self._cleanup = DebugCleanup(
                session_id=self.session.session_id,
                repo_path=self.repo_path,
                output_dir=self.output_dir,
            )
        return self._cleanup

    def inject(
        self,
        file_patterns: Optional[List[str]] = None,
        languages: Optional[List[LanguageType]] = None,
        exclude_patterns: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Inject debug markers into target files.

        Args:
            file_patterns: Glob patterns for files to inject (default: auto-detect)
            languages: Languages to target (default: all supported)
            exclude_patterns: Patterns to exclude (default: node_modules, .git, etc.)

        Returns:
            Injection result with file list and marker count
        """
        logger.info(f"Starting injection phase for session {self.session.session_id}")
        self.session.phase = DebugPhase.INJECT

        result = self.injector.inject(
            file_patterns=file_patterns,
            languages=languages,
            exclude_patterns=exclude_patterns,
        )

        self.session.injected_files = result.get("injected_files", [])
        self.session.injection_count = result.get("total_markers", 0)
        self.session.backup_dir = Path(result.get("backup_dir", self.output_dir / "backups"))

        self._save_session()

        return result

    def capture_logs(
        self,
        url: Optional[str] = None,
        command: Optional[str] = None,
        timeout: int = 60000,
        headless: bool = True,
    ) -> Dict[str, Any]:
        """
        Capture logs during test execution.

        For web applications: Launches browser and captures console output
        For CLI/scripts: Runs command and captures stdout/stderr

        Args:
            url: URL to load (for web apps)
            command: Command to run (for scripts)
            timeout: Maximum capture time in milliseconds
            headless: Run browser in headless mode

        Returns:
            Capture result with all logs and markers
        """
        logger.info(f"Starting capture phase for session {self.session.session_id}")
        self.session.phase = DebugPhase.CAPTURE

        result = self.capture.capture(
            url=url,
            command=command,
            timeout=timeout,
            headless=headless,
        )

        self.session.captured_logs = result.get("all_logs", [])
        self.session.cortex_markers = result.get("cortex_markers", [])
        self.session.errors = result.get("errors", [])
        self.session.warnings = result.get("warnings", [])

        self._save_session()

        return result

    def analyze(self) -> Dict[str, Any]:
        """
        Analyze captured logs to identify issues.

        Detects:
        - Race conditions (out-of-order execution)
        - Integration breakages (missing dependencies, DOM issues)
        - Timing issues (async operations completing incorrectly)
        - Error patterns and root causes

        Returns:
            Analysis result with detected issues and fix recommendations
        """
        logger.info(f"Starting analysis phase for session {self.session.session_id}")
        self.session.phase = DebugPhase.ANALYZE

        result = self.analyzer.analyze(
            cortex_markers=self.session.cortex_markers,
            errors=self.session.errors,
            warnings=self.session.warnings,
        )

        self.session.detected_issues = result.get("issues", [])
        self.session.race_conditions = result.get("race_conditions", [])
        self.session.integration_breaks = result.get("integration_breaks", [])

        self._save_session()

        return result

    def generate_fix_plan(self) -> Dict[str, Any]:
        """
        Generate a comprehensive fix plan based on analysis.

        Returns:
            Fix plan with prioritized recommendations
        """
        logger.info(f"Generating fix plan for session {self.session.session_id}")
        self.session.phase = DebugPhase.FIX_PLAN

        fix_plan = self.analyzer.generate_fix_plan(
            issues=self.session.detected_issues,
            race_conditions=self.session.race_conditions,
            integration_breaks=self.session.integration_breaks,
        )

        self.session.fix_plan = fix_plan
        self._save_session()

        # Save fix plan as markdown for easy review
        fix_plan_path = self.output_dir / "fix-plan.md"
        self._write_fix_plan_markdown(fix_plan, fix_plan_path)

        return fix_plan

    def cleanup(self, verify: bool = True) -> Dict[str, Any]:
        """
        Remove all debug markers from injected files.

        Args:
            verify: Run verification after cleanup to ensure no markers remain

        Returns:
            Cleanup result with verification status
        """
        logger.info(f"Starting cleanup phase for session {self.session.session_id}")
        self.session.phase = DebugPhase.CLEANUP

        result = self.cleanup_handler.cleanup(
            injected_files=self.session.injected_files,
            verify=verify,
        )

        self.session.cleaned_files = result.get("cleaned_files", [])
        self.session.cleanup_verified = result.get("verified", False)
        self.session.phase = DebugPhase.COMPLETE
        self.session.end_time = datetime.now()

        self._save_session()

        return result

    def run_full_cycle(
        self,
        file_patterns: Optional[List[str]] = None,
        url: Optional[str] = None,
        command: Optional[str] = None,
        auto_cleanup: bool = False,
    ) -> Dict[str, Any]:
        """
        Run the complete debug workflow.

        1. Inject markers
        2. Capture logs
        3. Analyze issues
        4. Generate fix plan
        5. (Optional) Cleanup

        Args:
            file_patterns: Files to inject markers into
            url: URL to test (web apps)
            command: Command to run (scripts)
            auto_cleanup: Automatically cleanup after analysis

        Returns:
            Complete debug report
        """
        logger.info(f"Starting full debug cycle for session {self.session.session_id}")

        results = {
            "session_id": self.session.session_id,
            "phases": {},
        }

        # Phase 1: Inject
        results["phases"]["inject"] = self.inject(file_patterns=file_patterns)

        # Phase 2: Capture
        results["phases"]["capture"] = self.capture_logs(url=url, command=command)

        # Phase 3: Analyze
        results["phases"]["analyze"] = self.analyze()

        # Phase 4: Fix Plan
        results["phases"]["fix_plan"] = self.generate_fix_plan()

        # Phase 5: Cleanup (if requested)
        if auto_cleanup:
            results["phases"]["cleanup"] = self.cleanup()
        else:
            results["cleanup_pending"] = True
            results["cleanup_command"] = f"cortex_debug_cleanup --session {self.session.session_id}"

        results["session"] = self.session.to_dict()

        return results

    def restore_from_backup(self) -> Dict[str, Any]:
        """
        Restore all files from backup (emergency recovery).

        Returns:
            Restoration result
        """
        logger.info(f"Restoring files from backup for session {self.session.session_id}")
        return self.cleanup_handler.restore_from_backup()

    def get_session_status(self) -> Dict[str, Any]:
        """Get current session status."""
        return self.session.to_dict()

    def _save_session(self):
        """Save session state to disk."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        session_path = self.output_dir / "session.json"
        with open(session_path, "w") as f:
            json.dump(self.session.to_dict(), f, indent=2)

    def _write_fix_plan_markdown(self, fix_plan: Dict[str, Any], path: Path):
        """Write fix plan as markdown."""
        md_content = f"""# CORTEX Debug Fix Plan

**Session:** {self.session.session_id}
**Generated:** {datetime.now().isoformat()}
**Repository:** {self.repo_path}

---

## 📋 Executive Summary

- **Total Issues:** {len(self.session.detected_issues)}
- **Race Conditions:** {len(self.session.race_conditions)}
- **Integration Breaks:** {len(self.session.integration_breaks)}
- **Errors Captured:** {len(self.session.errors)}

---

## 🔴 Critical Issues (P0)

"""
        critical = [i for i in self.session.detected_issues if i.get("severity") == "CRITICAL"]
        for i, issue in enumerate(critical, 1):
            md_content += f"""### {i}. {issue.get('title', 'Unknown Issue')}

**File:** `{issue.get('file', 'unknown')}`
**Line:** {issue.get('line', 'N/A')}
**Type:** {issue.get('type', 'unknown')}

**Description:** {issue.get('description', 'No description')}

**Fix:** {issue.get('fix', 'No fix recommendation')}

---

"""

        md_content += """## 🟡 High Priority Issues (P1)

"""
        high = [i for i in self.session.detected_issues if i.get("severity") == "HIGH"]
        for i, issue in enumerate(high, 1):
            md_content += f"""### {i}. {issue.get('title', 'Unknown Issue')}

**File:** `{issue.get('file', 'unknown')}`
**Description:** {issue.get('description', 'No description')}
**Fix:** {issue.get('fix', 'No fix recommendation')}

---

"""

        md_content += """## ⚡ Race Conditions Detected

"""
        for i, race in enumerate(self.session.race_conditions, 1):
            md_content += f"""### {i}. {race.get('description', 'Race condition')}

**Files Involved:** {', '.join(race.get('files', []))}
**Sequence Issue:** {race.get('sequence', 'Unknown')}
**Fix:** {race.get('fix', 'No fix recommendation')}

---

"""

        md_content += """## 🔗 Integration Breakages

"""
        for i, brk in enumerate(self.session.integration_breaks, 1):
            md_content += f"""### {i}. {brk.get('description', 'Integration issue')}

**Component:** {brk.get('component', 'Unknown')}
**Dependency:** {brk.get('dependency', 'Unknown')}
**Fix:** {brk.get('fix', 'No fix recommendation')}

---

"""

        md_content += f"""## 🧹 Cleanup Instructions

After fixing the issues, run cleanup to remove debug markers:

```bash
# Via MCP tool
cortex_debug_cleanup --session {self.session.session_id}

# Or via Python
from cortex.orchestrators.debugging import DebugOrchestrator
orchestrator = DebugOrchestrator("{self.repo_path}")
orchestrator.cleanup()
```

---

*Generated by CORTEX Debug Orchestrator v1.0.0*
"""

        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(md_content)

        logger.info(f"Fix plan written to {path}")


# Health check for wiring system
def health_check() -> bool:
    """Health check for orchestrator wiring."""
    return True
