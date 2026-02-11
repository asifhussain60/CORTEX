"""RepoDetectionOrchestrator - Intelligent repository type detection.

AC-ID: INQUIRY-001-NEW
Purpose: Auto-detect CORTEX vs user repository questions
Author: Asif Hussain
Date: 2026-01-27

Detection Algorithm (5 steps):
1. Keyword Analysis: Check for CORTEX-specific terms
2. Working Directory: Check if cwd is CORTEX path
3. File Paths: Check evidence files for CORTEX patterns
4. Git Remote: Check git remote URL
5. Confidence Synthesis: Combine signals for final decision

Confidence Thresholds:
- >= 0.85: High confidence CORTEX
- >= 0.50: Medium confidence (prompt user)
- < 0.50: User repository
"""

import re
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from cortex.models.inquiry_models import RepoContext, RepoType


@dataclass
class DetectionSignal:
    """Individual detection signal result.

    Attributes:
        name: Signal name (keyword_match, cwd_match, etc.)
        matched: Whether signal matched
        confidence: Confidence contribution 0.0-1.0
        evidence: Description of what was detected
    """
    name: str
    matched: bool
    confidence: float
    evidence: str


class RepoDetectionOrchestrator:
    """Intelligent repository type detection orchestrator.

    Uses 5-step algorithm to detect CORTEX vs user repositories:
    1. Keyword analysis in question text
    2. Working directory path check
    3. File paths in evidence
    4. Git remote URL check
    5. Confidence synthesis
    """

    # CORTEX-specific keywords for detection
    CORTEX_KEYWORDS = [
        "CORTEX",
        "TDDOrchestrator",
        "MasterOrchestrator",
        "IntentRouter",
        "EnforcementOrchestrator",
        "LENS",
        "DatabaseBackedRegistry",
        "CORE-",  # CORE rules
        "Tier3",
        "cortex-plan",
        "cortex_brain",
    ]

    # CORTEX path patterns
    CORTEX_PATH_PATTERNS = [
        "/CORTEX",
        "/PROJECTS/CORTEX",
        "asifhussain/PROJECTS/CORTEX",
    ]

    # CORTEX file patterns
    CORTEX_FILE_PATTERNS = [
        "cortex/",
        "cortex_brain/",
        "_workspaces/",
        "CORE-",
    ]

    # CORTEX git remote patterns
    CORTEX_GIT_PATTERNS = [
        "asifhussain60/CORTEX",
        "CORTEX.git",
    ]

    def detect_repository(
        self,
        question: str,
        current_directory: Path,
        file_paths: Optional[List[str]] = None,
    ) -> RepoContext:
        """Detect repository type using multi-signal analysis.

        Args:
            question: User's question text
            current_directory: Current working directory
            file_paths: Optional list of file paths in evidence

        Returns:
            RepoContext with detection results
        """
        signals: Dict[str, DetectionSignal] = {}

        # Step 1: Keyword analysis
        keyword_signal = self._check_keyword_match(question)
        signals["keyword_match"] = keyword_signal

        # Step 2: Working directory check
        cwd_signal = self._check_working_directory(current_directory)
        signals["cwd_match"] = cwd_signal

        # Step 3: File paths check
        if file_paths:
            file_signal = self._check_file_paths(file_paths)
            signals["file_path_match"] = file_signal

        # Step 4: Git remote check
        git_signal = self._check_git_remote(current_directory)
        signals["git_remote_match"] = git_signal

        # Step 5: Synthesize confidence and decide
        return self._synthesize_detection(
            signals=signals,
            current_directory=current_directory,
        )

    def _check_keyword_match(self, question: str) -> DetectionSignal:
        """Check for CORTEX keywords in question.

        Args:
            question: Question text

        Returns:
            Detection signal with match result
        """
        matched_keywords = [
            kw for kw in self.CORTEX_KEYWORDS
            if kw.lower() in question.lower()
        ]

        if matched_keywords:
            confidence = min(0.90, 0.75 + (len(matched_keywords) * 0.05))
            return DetectionSignal(
                name="keyword_match",
                matched=True,
                confidence=confidence,
                evidence=f"Found keywords: {', '.join(matched_keywords)}",
            )

        return DetectionSignal(
            name="keyword_match",
            matched=False,
            confidence=0.0,
            evidence="No CORTEX keywords found",
        )

    def _check_working_directory(self, cwd: Path) -> DetectionSignal:
        """Check if working directory is CORTEX path.

        Args:
            cwd: Current working directory

        Returns:
            Detection signal with match result
        """
        cwd_str = str(cwd)

        for pattern in self.CORTEX_PATH_PATTERNS:
            if pattern in cwd_str:
                return DetectionSignal(
                    name="cwd_match",
                    matched=True,
                    confidence=0.95,
                    evidence=f"Working directory: {cwd}",
                )

        return DetectionSignal(
            name="cwd_match",
            matched=False,
            confidence=0.0,
            evidence=f"Working directory: {cwd} (not CORTEX)",
        )

    def _check_file_paths(self, file_paths: List[str]) -> DetectionSignal:
        """Check if file paths contain CORTEX patterns.

        Args:
            file_paths: List of file paths

        Returns:
            Detection signal with match result
        """
        matched_files = []

        for file_path in file_paths:
            for pattern in self.CORTEX_FILE_PATTERNS:
                if pattern in file_path:
                    matched_files.append(file_path)
                    break

        if matched_files:
            confidence = min(0.85, 0.70 + (len(matched_files) * 0.05))
            return DetectionSignal(
                name="file_path_match",
                matched=True,
                confidence=confidence,
                evidence=f"CORTEX files: {', '.join(matched_files[:3])}",
            )

        return DetectionSignal(
            name="file_path_match",
            matched=False,
            confidence=0.0,
            evidence="No CORTEX file patterns found",
        )

    def _check_git_remote(self, cwd: Path) -> DetectionSignal:
        """Check git remote URL for CORTEX patterns.

        Args:
            cwd: Current working directory

        Returns:
            Detection signal with match result
        """
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=2,
            )

            if result.returncode == 0:
                remote_url = result.stdout.strip()

                for pattern in self.CORTEX_GIT_PATTERNS:
                    if pattern in remote_url:
                        return DetectionSignal(
                            name="git_remote_match",
                            matched=True,
                            confidence=0.98,
                            evidence=f"Git remote: {remote_url}",
                        )

        except Exception:
            # Not a git repo or git not available
            pass

        return DetectionSignal(
            name="git_remote_match",
            matched=False,
            confidence=0.0,
            evidence="Git remote not matched or unavailable",
        )

    def _synthesize_detection(
        self,
        signals: Dict[str, DetectionSignal],
        current_directory: Path,
    ) -> RepoContext:
        """Synthesize signals into final detection decision.

        Args:
            signals: Dictionary of detection signals
            current_directory: Current working directory

        Returns:
            RepoContext with final decision
        """
        # Calculate overall confidence
        total_confidence = sum(
            signal.confidence for signal in signals.values()
            if signal.matched
        )

        # Normalize (max 1.0)
        final_confidence = min(1.0, total_confidence)

        # Decision thresholds
        if final_confidence >= 0.85:
            repo_type = RepoType.CORTEX
            repo_name = "CORTEX"
        elif final_confidence >= 0.50:
            # Ambiguous - default to CORTEX if any signal matched
            any_matched = any(s.matched for s in signals.values())
            repo_type = RepoType.CORTEX if any_matched else RepoType.USER_REPO
            repo_name = "CORTEX" if any_matched else current_directory.name
        else:
            repo_type = RepoType.USER_REPO
            repo_name = current_directory.name

        # Build detection signals dict
        detection_signals = {
            name: signal.matched
            for name, signal in signals.items()
        }

        # Get git remote if available
        git_remote = None
        if "git_remote_match" in signals and signals["git_remote_match"].matched:
            git_remote = signals["git_remote_match"].evidence.replace("Git remote: ", "")

        return RepoContext(
            repo_type=repo_type,
            repo_path=current_directory,
            repo_name=repo_name,
            git_remote=git_remote,
            detection_confidence=final_confidence,
            detection_signals=detection_signals,
        )
