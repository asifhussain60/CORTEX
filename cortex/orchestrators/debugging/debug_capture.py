"""
CORTEX Debug Capture
====================

Log capture system for collecting debug output during execution.
Supports browser-based capture (Playwright) and CLI capture (subprocess).

Author: CORTEX
Version: 1.0.0
Phase: Phase 21.5 - Universal Debugging

Capture Modes:
- Browser: Playwright-based for web applications
- CLI: Subprocess-based for scripts and services
- File: Monitor log files for changes
"""

import asyncio
import json
import logging
import re
import subprocess
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

logger = logging.getLogger(__name__)

# Marker prefix constant

# Noise patterns to filter (third-party extensions, etc.)
NOISE_PATTERNS = [
    re.compile(r'grammarly', re.IGNORECASE),
    re.compile(r'wax', re.IGNORECASE),
    re.compile(r'contentisolated', re.IGNORECASE),
    re.compile(r'chrome-extension', re.IGNORECASE),
    re.compile(r'moz-extension', re.IGNORECASE),
    re.compile(r'devtools', re.IGNORECASE),
    re.compile(r'favicon\.ico', re.IGNORECASE),
    re.compile(r'\[HMR\]', re.IGNORECASE),  # Hot Module Replacement
    re.compile(r'\[vite\]', re.IGNORECASE),  # Vite dev server
]


class CaptureMode(Enum):
    """Capture mode types."""
    BROWSER = "browser"
    CLI = "cli"
    FILE = "file"


class LogType(Enum):
    """Log entry types."""
    LOG = "log"
    INFO = "info"
    WARN = "warn"
    ERROR = "error"
    DEBUG = "debug"
    TRACE = "trace"


@dataclass
class LogEntry:
    """Represents a single captured log entry."""

    timestamp: datetime
    log_type: LogType
    message: str
    source: Optional[str] = None
    line_number: Optional[int] = None
    is_cortex_marker: bool = False
    parsed_marker: Optional[Dict[str, Any]] = None

    @classmethod
    def parse_cortex_marker(cls, text: str) -> Optional[Dict[str, Any]]:
        """Parse a CORTEX debug marker from log text."""
        match = re.match(pattern, text)
        if match:
            return {
                "session_id": match.group(1),
                "phase": match.group(2),
                "file": match.group(3),
                "line": int(match.group(4)),
                "message": match.group(5),
            }
        return None

    def is_noise(self) -> bool:
        """Check if this log entry is noise from third-party sources."""
        for pattern in NOISE_PATTERNS:
            if pattern.search(self.message):
                return True
        return False

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "timestamp": self.timestamp.isoformat(),
            "log_type": self.log_type.value,
            "message": self.message,
            "source": self.source,
            "line_number": self.line_number,
            "is_cortex_marker": self.is_cortex_marker,
            "parsed_marker": self.parsed_marker,
        }


@dataclass
class CaptureResult:
    """Result of a capture session."""

    mode: CaptureMode
    start_time: datetime
    end_time: Optional[datetime] = None
    duration_ms: int = 0

    all_logs: List[LogEntry] = field(default_factory=list)
    cortex_markers: List[LogEntry] = field(default_factory=list)
    errors: List[LogEntry] = field(default_factory=list)
    warnings: List[LogEntry] = field(default_factory=list)

    tabs_visited: List[Dict[str, Any]] = field(default_factory=list)
    commands_run: List[str] = field(default_factory=list)

    success: bool = True
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "mode": self.mode.value,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration_ms": self.duration_ms,
            "all_logs": [log.to_dict() for log in self.all_logs],
            "cortex_markers": [log.to_dict() for log in self.cortex_markers],
            "errors": [log.to_dict() for log in self.errors],
            "warnings": [log.to_dict() for log in self.warnings],
            "tabs_visited": self.tabs_visited,
            "commands_run": self.commands_run,
            "success": self.success,
            "error_message": self.error_message,
            "summary": {
                "total_logs": len(self.all_logs),
                "cortex_markers_count": len(self.cortex_markers),
                "errors_count": len(self.errors),
                "warnings_count": len(self.warnings),
            }
        }


class DebugCapture:
    """
    Log capture coordinator for debug sessions.

    Supports multiple capture modes:
    - Browser: Uses Playwright for web application debugging
    - CLI: Uses subprocess for script/service debugging
    - File: Monitors log files for changes
    """

    def __init__(
        self,
        session_id: str,
        output_dir: Path,
    ):
        self.session_id = session_id
        self.output_dir = Path(output_dir)

        logger.info(f"DebugCapture initialized for session {session_id}")

    def capture(
        self,
        url: Optional[str] = None,
        command: Optional[str] = None,
        log_file: Optional[Path] = None,
        timeout: int = 60000,
        headless: bool = True,
        click_tabs: bool = True,
        wait_for_ready: bool = True,
    ) -> Dict[str, Any]:
        """
        Capture logs from the specified source.

        Args:
            url: URL to load (browser mode)
            command: Command to run (CLI mode)
            log_file: Log file to monitor (file mode)
            timeout: Maximum capture time in milliseconds
            headless: Run browser in headless mode
            click_tabs: Automatically click through tabs (browser mode)
            wait_for_ready: Wait for application to be ready

        Returns:
            Capture result dictionary
        """
        if url:
            return self._capture_browser(
                url=url,
                timeout=timeout,
                headless=headless,
                click_tabs=click_tabs,
                wait_for_ready=wait_for_ready,
            )
        elif command:
            return self._capture_cli(
                command=command,
                timeout=timeout,
            )
        elif log_file:
            return self._capture_file(
                log_file=log_file,
                timeout=timeout,
            )
        else:
            raise ValueError("Must provide url, command, or log_file")

    def _capture_browser(
        self,
        url: str,
        timeout: int,
        headless: bool,
        click_tabs: bool,
        wait_for_ready: bool,
    ) -> Dict[str, Any]:
        """Capture browser console logs using Playwright."""
        try:
            # Import playwright
            from playwright.sync_api import sync_playwright
        except ImportError:
            logger.warning("Playwright not installed, falling back to subprocess capture")
            return self._capture_browser_fallback(url, timeout)

        result = CaptureResult(
            mode=CaptureMode.BROWSER,
            start_time=datetime.now(),
        )

        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=headless)
                context = browser.new_context(viewport={"width": 1920, "height": 1080})
                page = context.new_page()

                # Set up console message handler
                def handle_console(msg):
                    log_type_map = {
                        "log": LogType.LOG,
                        "info": LogType.INFO,
                        "warning": LogType.WARN,
                        "error": LogType.ERROR,
                        "debug": LogType.DEBUG,
                        "trace": LogType.TRACE,
                    }

                    entry = LogEntry(
                        timestamp=datetime.now(),
                        log_type=log_type_map.get(msg.type, LogType.LOG),
                        message=msg.text,
                        source=msg.location.get("url") if msg.location else None,
                        line_number=msg.location.get("lineNumber") if msg.location else None,
                    )

                    # Check for CORTEX marker
                    parsed = LogEntry.parse_cortex_marker(msg.text)
                    if parsed:
                        entry.is_cortex_marker = True
                        entry.parsed_marker = parsed
                        result.cortex_markers.append(entry)

                    # Filter noise
                    if not entry.is_noise():
                        result.all_logs.append(entry)

                        if entry.log_type == LogType.ERROR:
                            result.errors.append(entry)
                        elif entry.log_type == LogType.WARN:
                            result.warnings.append(entry)

                page.on("console", handle_console)

                # Navigate to URL
                logger.info(f"Navigating to {url}")
                try:
                    page.goto(url, wait_until="networkidle", timeout=timeout)
                except Exception as e:
                    logger.warning(f"Navigation timeout: {e}")

                # Wait for application ready
                if wait_for_ready:
                    try:
                        page.wait_for_function(
                            """() => {
                                return window.cortexDashboard?.initialized ||
                                       document.querySelector('[data-dashboard-ready="true"]') ||
                                       document.querySelector('.metric-card__value:not(:empty)');
                            }""",
                            timeout=10000
                        )
                        logger.info("Application ready detected")
                    except Exception as e:
                        logger.warning(f"Ready check timeout: {e}")

                # Click through tabs if requested
                if click_tabs:
                    try:
                        tabs = page.query_selector_all('.tab-button')
                        logger.info(f"Found {len(tabs)} tabs")

                        for i, tab in enumerate(tabs):
                            try:
                                tab_name = tab.text_content().strip()
                                tab.click()
                                result.tabs_visited.append({
                                    "name": tab_name,
                                    "index": i,
                                    "timestamp": datetime.now().isoformat(),
                                })
                                page.wait_for_timeout(500)

                                # Check for sub-tabs
                                sub_tabs = page.query_selector_all('.sub-tab')
                                for sub_tab in sub_tabs:
                                    sub_name = sub_tab.text_content().strip()
                                    sub_tab.click()
                                    result.tabs_visited.append({
                                        "name": f"{tab_name} > {sub_name}",
                                        "index": i,
                                        "timestamp": datetime.now().isoformat(),
                                    })
                                    page.wait_for_timeout(300)
                            except Exception as e:
                                logger.warning(f"Tab click failed: {e}")
                    except Exception as e:
                        logger.warning(f"Tab navigation failed: {e}")

                # Wait for any delayed renders
                page.wait_for_timeout(2000)

                browser.close()

        except Exception as e:
            result.success = False
            result.error_message = str(e)
            logger.error(f"Browser capture failed: {e}")

        result.end_time = datetime.now()
        result.duration_ms = int((result.end_time - result.start_time).total_seconds() * 1000)

        # Save captured logs
        self._save_capture_result(result)

        return result.to_dict()

    def _capture_browser_fallback(self, url: str, timeout: int) -> Dict[str, Any]:
        """Fallback browser capture using a simple HTTP request."""
        logger.info("Using fallback capture (no Playwright)")

        result = CaptureResult(
            mode=CaptureMode.BROWSER,
            start_time=datetime.now(),
        )

        result.error_message = "Playwright not available - install with: pip install playwright && playwright install"
        result.success = False

        result.end_time = datetime.now()
        result.duration_ms = int((result.end_time - result.start_time).total_seconds() * 1000)

        return result.to_dict()

    def _capture_cli(
        self,
        command: str,
        timeout: int,
    ) -> Dict[str, Any]:
        """Capture CLI output using subprocess."""
        result = CaptureResult(
            mode=CaptureMode.CLI,
            start_time=datetime.now(),
        )
        result.commands_run.append(command)

        try:
            logger.info(f"Running command: {command}")

            # Run command with timeout
            process = subprocess.Popen(
                command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            timeout_seconds = timeout / 1000

            try:
                stdout, stderr = process.communicate(timeout=timeout_seconds)
            except subprocess.TimeoutExpired:
                process.kill()
                stdout, stderr = process.communicate()
                logger.warning(f"Command timed out after {timeout_seconds}s")

            # Parse stdout
            for line in stdout.split('\n'):
                if line.strip():
                    entry = LogEntry(
                        timestamp=datetime.now(),
                        log_type=LogType.LOG,
                        message=line,
                    )

                    parsed = LogEntry.parse_cortex_marker(line)
                    if parsed:
                        entry.is_cortex_marker = True
                        entry.parsed_marker = parsed
                        result.cortex_markers.append(entry)

                    result.all_logs.append(entry)

            # Parse stderr
            for line in stderr.split('\n'):
                if line.strip():
                    entry = LogEntry(
                        timestamp=datetime.now(),
                        log_type=LogType.ERROR,
                        message=line,
                    )
                    result.all_logs.append(entry)
                    result.errors.append(entry)

            if process.returncode != 0:
                result.success = False
                result.error_message = f"Command exited with code {process.returncode}"

        except Exception as e:
            result.success = False
            result.error_message = str(e)
            logger.error(f"CLI capture failed: {e}")

        result.end_time = datetime.now()
        result.duration_ms = int((result.end_time - result.start_time).total_seconds() * 1000)

        # Save captured logs
        self._save_capture_result(result)

        return result.to_dict()

    def _capture_file(
        self,
        log_file: Path,
        timeout: int,
    ) -> Dict[str, Any]:
        """Capture logs from a file (tail -f style)."""
        result = CaptureResult(
            mode=CaptureMode.FILE,
            start_time=datetime.now(),
        )

        log_path = Path(log_file)

        try:
            if not log_path.exists():
                raise FileNotFoundError(f"Log file not found: {log_path}")

            # Read existing content
            with open(log_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line:
                        entry = LogEntry(
                            timestamp=datetime.now(),
                            log_type=LogType.LOG,
                            message=line,
                            source=str(log_path),
                        )

                        parsed = LogEntry.parse_cortex_marker(line)
                        if parsed:
                            entry.is_cortex_marker = True
                            entry.parsed_marker = parsed
                            result.cortex_markers.append(entry)

                        result.all_logs.append(entry)

        except Exception as e:
            result.success = False
            result.error_message = str(e)
            logger.error(f"File capture failed: {e}")

        result.end_time = datetime.now()
        result.duration_ms = int((result.end_time - result.start_time).total_seconds() * 1000)

        # Save captured logs
        self._save_capture_result(result)

        return result.to_dict()

    def _save_capture_result(self, result: CaptureResult):
        """Save capture result to disk."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        capture_path = self.output_dir / "captured-logs.json"
        with open(capture_path, 'w') as f:
            json.dump(result.to_dict(), f, indent=2)

        logger.info(f"Capture saved to {capture_path}")
