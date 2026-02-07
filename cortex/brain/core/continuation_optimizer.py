"""
Continuation Optimizer - Token-efficient continuation prompt generation.

Detects bloated continuation prompts and generates optimized versions that
leverage GitHub Copilot's existing context instead of duplicating information.

Key Features:
- Detects token waste patterns (session replay, file lists, etc.)
- Generates <500 token continuation prompts (vs 60k+ bloated versions)
- Ensures #file: prefix for automatic prompt loading
- Only suggests continuation when token budget >90%

Governance:
- CORE-002: No markdown file generation
- CORE-011: Type hints on all functions
- CORE-012: Google-style docstrings
- ENH-047: Token optimization via EXIT GATE

Author: Asif Hussain
Date: 2026-02-07
"""

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Any, Optional


@dataclass
class TokenWastePattern:
    """Represents a detected token waste pattern."""
    
    pattern: str
    severity: str  # P0, P1, P2
    waste_estimate: int  # Estimated tokens wasted
    fix: str  # How to fix it
    location: Optional[str] = None  # Where in response


@dataclass
class ContinuationAuditResult:
    """Result of continuation prompt audit."""
    
    violations: List[TokenWastePattern] = field(default_factory=list)
    total_token_waste: int = 0
    efficiency_score: float = 0.0
    is_continuation_needed: bool = False
    token_budget_usage: Optional[float] = None


class ContinuationOptimizer:
    """
    Optimizes continuation prompts for token efficiency.
    
    Detects and eliminates common token waste patterns:
    - Session replay (chat history already available)
    - Detailed stage documentation (files exist in repo)
    - File lists (use semantic_search instead)
    - Implementation steps (use phase YAMLs)
    - Missing #file: prefix (prevents auto-load)
    
    Example:
        >>> optimizer = ContinuationOptimizer()
        >>> result = optimizer.audit_response(response_text)
        >>> if result.total_token_waste > 10000:
        ...     optimized = optimizer.generate_optimal_continuation(
        ...         session_id="Phase 38 Stage 7.2",
        ...         last_checkpoint="exposure_auditor.py ✅",
        ...         next_action="Implement tool_spec_generator.py"
        ...     )
    """
    
    # Token waste patterns (pattern, severity, avg_tokens)
    BLOAT_PATTERNS = {
        "session_replay": (
            r"Completed:.*\n.*Stage [0-9]",
            "P0",
            15000,
            "Remove session replay - GitHub Copilot has chat history"
        ),
        "detailed_stages": (
            r"Stage [0-9]+:.*\([0-9]+ hours, [0-9]+ tests\)",
            "P0",
            20000,
            "Remove stage details - Files exist in repo (use semantic_search)"
        ),
        "file_lists": (
            r"Files to Create/Modify:\n(?:-.*\n){5,}",
            "P1",
            5000,
            "Remove file lists - Use semantic_search or #file: references"
        ),
        "implementation_steps": (
            r"Implementation Order:\n(?:[0-9]+\..*\n){5,}",
            "P1",
            8000,
            "Remove implementation steps - Phase YAMLs have details"
        ),
        "command_history": (
            r"Commands to.*:\n(?:[0-9]+\..*\n){3,}",
            "P1",
            3000,
            "Remove command history - Terminal history available"
        ),
        "extensive_context": (
            r"Session Context:.*\n(?:.*\n){20,}",
            "P0",
            12000,
            "Remove extensive context - Summarize to 3-4 lines max"
        ),
    }
    
    DUPLICATE_PATTERNS = [
        (r"Previously completed:.*\n(?:- .*\n){5,}", "completed_work_list", 3500),
        (r"Files modified:.*\n(?:- .*\n){5,}", "file_modification_list", 4000),
        (r"Test results:.*\n(?:.*\n){10,}", "test_result_replay", 5000),
        (r"Audit trail:.*\n(?:AC-.*\n){3,}", "audit_trail_replay", 2500),
    ]
    
    def __init__(self) -> None:
        """Initialize continuation optimizer."""
        pass
    
    def audit_response(
        self,
        response_text: str,
        token_budget_usage: Optional[float] = None
    ) -> ContinuationAuditResult:
        """
        Audit response for continuation prompt efficiency.
        
        Args:
            response_text: Full response text to audit
            token_budget_usage: Optional token usage percentage (0-100)
            
        Returns:
            ContinuationAuditResult with violations and waste estimate
        """
        violations: List[TokenWastePattern] = []
        total_waste = 0
        
        # Check if this is a continuation prompt
        is_continuation = (
            "continuation" in response_text.lower() or
            "next session" in response_text.lower()
        )
        
        if not is_continuation:
            return ContinuationAuditResult(
                violations=[],
                total_token_waste=0,
                efficiency_score=100.0,
                is_continuation_needed=False,
                token_budget_usage=token_budget_usage
            )
        
        # Pattern 1: Bloat indicators
        for pattern_name, (pattern, severity, waste, fix) in self.BLOAT_PATTERNS.items():
            if re.search(pattern, response_text, re.MULTILINE):
                violations.append(TokenWastePattern(
                    pattern=pattern_name,
                    severity=severity,
                    waste_estimate=waste,
                    fix=fix
                ))
                total_waste += waste
        
        # Pattern 2: Missing #file: prefix
        if "#file:" not in response_text and "cortex-architect" in response_text.lower():
            violations.append(TokenWastePattern(
                pattern="missing_file_prefix",
                severity="P1",
                waste_estimate=2000,
                fix="Add #file:cortex-architect.prompt.md at start"
            ))
            total_waste += 2000
        
        # Pattern 3: Duplicate context
        for pattern, pattern_name, waste in self.DUPLICATE_PATTERNS:
            if re.search(pattern, response_text, re.MULTILINE):
                violations.append(TokenWastePattern(
                    pattern=f"duplicate_{pattern_name}",
                    severity="P1",
                    waste_estimate=waste,
                    fix=f"Remove {pattern_name} - Available in chat history"
                ))
                total_waste += waste
        
        # Pattern 4: Continuation when work is complete
        work_complete = (
            "implementation complete" in response_text.lower() or
            "mission accomplished" in response_text.lower() or
            "✅" in response_text
        )
        
        if is_continuation and work_complete:
            violations.append(TokenWastePattern(
                pattern="unnecessary_continuation",
                severity="P0",
                waste_estimate=200,
                fix='Use "Implementation Complete" instead of continuation'
            ))
            total_waste += 200
        
        # Pattern 5: Premature continuation (<90% token budget)
        if token_budget_usage and token_budget_usage < 90:
            violations.append(TokenWastePattern(
                pattern="premature_continuation",
                severity="P1",
                waste_estimate=0,
                fix="Show continuation only at >90% token usage"
            ))
        
        # Calculate efficiency score
        efficiency = max(0, 100 - (total_waste / 600))  # 60k baseline
        
        return ContinuationAuditResult(
            violations=violations,
            total_token_waste=total_waste,
            efficiency_score=efficiency,
            is_continuation_needed=is_continuation and not work_complete,
            token_budget_usage=token_budget_usage
        )
    
    def generate_optimal_continuation(
        self,
        session_id: str,
        branch: str,
        last_checkpoint: str,
        next_action: str,
        command: Optional[str] = None,
        prompt_file: str = "cortex-architect.prompt.md"
    ) -> str:
        """
        Generate optimal token-efficient continuation prompt.
        
        Args:
            session_id: Phase/stage identifier (e.g., "Phase 38 Stage 7.2")
            branch: Git branch name
            last_checkpoint: Last completed item with status
            next_action: Immediate next action to take
            command: Optional command to resume work
            prompt_file: Prompt file to load (with #file: prefix)
                        Should be the ORIGINAL prompt that started the session:
                        - "cortex-architect.prompt.md" for AUDIT/DESIGN/PLAN modes
                        - "CORTEX.prompt.md" for IMPLEMENT/FIX/REFACTOR modes
            
        Returns:
            Optimized continuation prompt (~200 tokens)
            
        Example:
            >>> optimizer.generate_optimal_continuation(
            ...     session_id="Phase 38 Stage 7.2",
            ...     branch="CORTEX",
            ...     last_checkpoint="exposure_auditor.py ✅",
            ...     next_action="Implement tool_spec_generator.py (46 orchestrators)",
            ...     command="/implement tool_spec_generator",
            ...     prompt_file="cortex-architect.prompt.md"  # Original session prompt
            ... )
        """
        lines = [
            "---",
            "",
            "### 🔄 Continuation Required",
            "",
            "**Token budget:** >90% used — Continue in new session",
            "",
            f"**#file:{prompt_file}**",
            "",
            f"**Session:** {session_id}",
            f"**Branch:** {branch}",
            f"**Context:** {last_checkpoint}",
            "",
            f"**Next:** {next_action}",
        ]
        
        if command:
            lines.extend([
                "",
                f"**Command:** `{command}`"
            ])
        
        return "\n".join(lines)
    
    def should_show_continuation(
        self,
        token_budget_usage: float,
        work_complete: bool
    ) -> bool:
        """
        Determine if continuation prompt should be shown.
        
        Args:
            token_budget_usage: Token usage percentage (0-100)
            work_complete: Whether work is complete
            
        Returns:
            True if continuation prompt should be shown
        """
        return token_budget_usage >= 90 and not work_complete
    
    def scan_chat_sessions(
        self,
        chat_dir: Path = Path("_workspaces/.chats"),
        max_sessions: int = 5
    ) -> Dict[str, ContinuationAuditResult]:
        """
        Scan recent chat sessions for token waste patterns.
        
        Args:
            chat_dir: Directory containing chat session files
            max_sessions: Maximum number of recent sessions to scan
            
        Returns:
            Dict mapping session filename to audit result
        """
        results: Dict[str, ContinuationAuditResult] = {}
        
        if not chat_dir.exists():
            return results
        
        # Get most recent chat files
        chat_files = sorted(
            chat_dir.glob("*.txt"),
            key=lambda p: p.stat().st_mtime,
            reverse=True
        )[:max_sessions]
        
        for chat_file in chat_files:
            try:
                content = chat_file.read_text(encoding="utf-8")
                result = self.audit_response(content)
                results[chat_file.name] = result
            except Exception as e:
                # Skip files that can't be read
                continue
        
        return results
    
    def generate_audit_report(
        self,
        scan_results: Dict[str, ContinuationAuditResult]
    ) -> str:
        """
        Generate markdown audit report from scan results.
        
        Args:
            scan_results: Dict of session -> audit result
            
        Returns:
            Markdown formatted audit report
        """
        lines = [
            "### P7: Token Efficiency & Continuation Prompts",
            "",
            f"**Sessions Scanned:** {len(scan_results)}",
            "",
        ]
        
        # Calculate totals
        total_waste = sum(r.total_token_waste for r in scan_results.values())
        avg_efficiency = sum(r.efficiency_score for r in scan_results.values()) / len(scan_results) if scan_results else 0
        
        lines.extend([
            "#### Summary",
            "",
            f"- **Total Token Waste:** {total_waste:,} tokens",
            f"- **Average Efficiency:** {avg_efficiency:.1f}% (Target: >90%)",
            f"- **Status:** {'✅ PASS' if avg_efficiency >= 90 else '❌ FAIL'}",
            "",
        ])
        
        # Detail violations by session
        if any(r.violations for r in scan_results.values()):
            lines.extend([
                "#### Violations by Session",
                "",
                "| Session | Pattern | Severity | Waste | Fix |",
                "|---------|---------|----------|-------|-----|",
            ])
            
            for session, result in scan_results.items():
                for v in result.violations:
                    severity_icon = "🔴" if v.severity == "P0" else "🟡"
                    lines.append(
                        f"| {session} | {v.pattern} | {severity_icon} {v.severity} | "
                        f"{v.waste_estimate:,} | {v.fix} |"
                    )
            
            lines.append("")
        
        # Recommendations
        lines.extend([
            "#### Recommendations",
            "",
            "**Use optimal continuation format:**",
            "",
            "```markdown",
            "### 🔄 Continuation Required",
            "",
            "**Token budget:** >90% used — Continue in new session",
            "",
            "**#file:cortex-architect.prompt.md**",
            "",
            "**Session:** Phase 38 Stage 7.2",
            "**Branch:** CORTEX",
            "**Context:** exposure_auditor.py ✅",
            "",
            "**Next:** Implement tool_spec_generator.py",
            "",
            "**Command:** `/implement tool_spec_generator`",
            "```",
            "",
            f"**Savings:** ~60,000 → ~200 tokens = **99.67% reduction**",
        ])
        
        return "\n".join(lines)
