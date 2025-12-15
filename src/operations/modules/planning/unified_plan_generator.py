"""
Unified Plan Generator for CORTEX

Shared plan generation logic for all planning orchestrators.
Eliminates duplication across PlanningOrchestrator, TempPlanManager, ADOPlanning.

Author: Asif Hussain
Version: 1.0.0
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import re

from .token_reduction_tracker import TokenReductionTracker

logger = logging.getLogger(__name__)


# Phase name abbreviations for token compression
PHASE_NAME_ABBREVIATIONS = {
    'Integration': 'Integ',
    'Implementation': 'Impl',
    'Enhancement': 'Enhnc',
    'Enhancements': 'Enhnc',
    'Orchestrator': 'Orch',
    'Architecture': 'Arch',
    'Organization': 'Org',
    'Management': 'Mgmt',
    'Migration': 'Migr',
    'Optimization': 'Optim',
    'Configuration': 'Config',
    'Authentication': 'Auth',
    'Authorization': 'Authz',
    'Documentation': 'Docs',
    'Development': 'Dev',
    'Environment': 'Env',
    'Deployment': 'Deploy',
    'Preparation': 'Prep',
    'Consolidation': 'Consol',
    'Transformation': 'Transform',
    'Modernization': 'Modern',
    'Refactoring': 'Refactor',
    'Infrastructure': 'Infra',
    'Application': 'App',
    'Database': 'DB',
    'Repository': 'Repo',
    'Connection': 'Conn',
    'Framework': 'FW',
    'Component': 'Comp',
    'Service': 'Svc',
    'Interface': 'Iface',
    'Validation': 'Valid',
    'Verification': 'Verify',
    'Performance': 'Perf',
    'Monitoring': 'Monitor',
    'Maintenance': 'Maint',
    'Security': 'Sec',
    'Testing': 'Test',
    'Quality': 'Qual',
    'Assurance': 'Assur',
    'Analysis': 'Anal',
    'Cleanup': 'Clean',
    'Realignment': 'Realign',
    'Unification': 'Unif',
    'System': 'Sys',
    'Extension': 'Ext',
    'Advanced': 'Adv'
}


class UnifiedPlanGenerator:
    """
    Shared plan generation logic for all planning orchestrators.
    
    Eliminates duplication across:
    - PlanningOrchestrator
    - TempPlanManagerOrchestrator
    - ADOPlanningOrchestrator (future: if it needs master plans)
    """
    
    def __init__(self):
        """Initialize unified plan generator."""
        self.token_tracker = TokenReductionTracker()
        logger.info("✅ UnifiedPlanGenerator initialized")
    
    def compress_phase_name(self, phase_name: str, compressed: bool = False) -> str:
        """Compress phase name using abbreviations.
        
        Args:
            phase_name: Original phase name
            compressed: Whether to apply compression
            
        Returns:
            Compressed or original phase name
        """
        if not compressed:
            return phase_name
        
        result = phase_name
        for full, abbrev in PHASE_NAME_ABBREVIATIONS.items():
            result = result.replace(full, abbrev)
        
        return result
    
    def generate_master_plan(
        self,
        plan_id: str,
        phases: List[Dict],
        metadata: Dict,
        include_token_tracking: bool = True,
        include_visual_tracker: bool = True,
        include_continuation_prompt: bool = True,
        compressed: bool = False,
        manifest_path: Optional[str] = None
    ) -> str:
        """
        Generate master plan with consistent structure.
        
        Args:
            plan_id: Plan identifier
            phases: List of phase dictionaries
            metadata: Plan metadata (date, complexity, etc.)
            include_token_tracking: Include token reduction metrics
            include_visual_tracker: Include ASCII progress bar
            include_continuation_prompt: Include continuation prompt
            compressed: Use compressed format for token optimization
            manifest_path: Path to orchestrator manifest YAML (for continuation prompt context)
        
        Returns:
            Master plan markdown content
        """
        sections = []
        
        # Store compression mode for use in helper methods
        self._compressed = compressed
        
        # Header
        sections.append(self._generate_header(plan_id, metadata, compressed))
        
        # Executive Summary
        if "summary" in metadata:
            sections.append(self._generate_executive_summary(metadata["summary"]))
        
        # Continuation Prompt (skip if plan is 100% complete or empty)
        completed_count = sum(1 for p in phases if p.get("status") == "complete")
        total_phases = len(phases)
        # Skip if: no phases (empty) OR all phases complete
        is_plan_complete_or_empty = (total_phases == 0) or (completed_count == total_phases and total_phases > 0)
        
        if include_continuation_prompt and not is_plan_complete_or_empty:
            sections.append(self._generate_continuation_prompt_section(
                plan_id=plan_id,
                completed_phases=completed_count,
                total_phases=len(phases),
                next_phase_number=self._find_next_phase(phases),
                next_phase_name=self._find_next_phase_name(phases),
                progress_percentage=self._calculate_progress(phases),
                compressed=compressed,
                manifest_path=manifest_path
            ))
        
        # Visual Progress Tracker
        if include_visual_tracker:
            baseline_tokens = metadata.get("baseline_tokens", 0)
            current_tokens = metadata.get("current_tokens", baseline_tokens)
            sections.append(self.generate_progress_tracker(
                phases=phases,
                baseline_tokens=baseline_tokens,
                current_tokens=current_tokens,
                total_files=metadata.get("total_files", 0),
                compressed=compressed
            ))
        
        # Phases Table
        sections.append(self._generate_phases_table(phases, include_token_tracking, compressed))
        
        # Footer
        sections.append(self._generate_footer(compressed))
        
        return "\n\n".join(sections)
    
    def generate_progress_tracker(
        self,
        phases: List[Dict],
        baseline_tokens: int,
        current_tokens: int,
        total_files: int,
        compressed: bool = False
    ) -> str:
        """
        Generate visual progress tracker with token metrics.
        
        Args:
            phases: List of phase dictionaries
            baseline_tokens: Baseline token count
            current_tokens: Current token count
            total_files: Total file count
            compressed: Use compressed format
        
        Returns:
            Progress tracker markdown
        """
        completed = sum(1 for p in phases if p.get("status") == "complete")
        total = len(phases)
        percentage = (completed / total * 100) if total > 0 else 0
        
        # ASCII progress bar
        bar_length = 20
        filled = int(bar_length * completed / total) if total > 0 else 0
        bar = "█" * filled + "░" * (bar_length - filled)
        
        # Token metrics
        tokens_saved = baseline_tokens - current_tokens
        percentage_reduction = self.token_tracker.calculate_percentage(baseline_tokens, current_tokens)
        
        if compressed:
            # Compressed format (target: 70 tokens)
            tracker = f"""## 📊 Progress

**Total:** [{bar}] {percentage:.0f}% ({completed}/{total})  
**Time:** {self._sum_actual_time(phases)} | **Saved:** -{percentage_reduction}% ({self.token_tracker.format_tokens(tokens_saved, include_label=True)})"""
        else:
            # Verbose format (current: 101 tokens)
            tracker = f"""## 📊 Visual Progress Tracker

**Overall Progress:** [{bar}] {percentage:.0f}% ({completed}/{total} Phases Complete)  
**Total Actual:** {self._sum_actual_time(phases)} | **Total Elapsed:** {self._sum_elapsed_time(phases)}  
**Token Reduction:** {percentage_reduction}% ({self.token_tracker.format_tokens(tokens_saved, include_label=True)})  
*Baseline: {self.token_tracker.format_tokens(baseline_tokens)} tokens across {total_files} files*"""
        
        return tracker
    
    def generate_continuation_prompt(
        self,
        plan_id: str,
        completed_phases: int,
        total_phases: int,
        next_phase_number: Optional[int],
        next_phase_name: Optional[str],
        progress_percentage: int,
        manifest_path: Optional[str] = None
    ) -> str:
        """
        Generate ultra-compact continuation prompt with manifest reference.
        
        Strategy: Link to YAML manifest for full context (phases, DoR/DoD, TDD rules)
        rather than repeating information. AI will load manifest on demand.
        
        Args:
            plan_id: Plan identifier
            completed_phases: Number of completed phases
            total_phases: Total number of phases
            next_phase_number: Next phase number (or None if complete)
            next_phase_name: Next phase name
            progress_percentage: Overall progress percentage
            manifest_path: Path to orchestrator manifest (e.g., planning-system-3.0-manifest.yaml)
        
        Returns:
            Ultra-compact continuation prompt (<30 tokens target)
        """
        # Build manifest reference if provided
        manifest_ref = ""
        if manifest_path:
            manifest_ref = f" | Manifest: `{manifest_path}`"
        
        if next_phase_number is None:
            return f"""Continue `{plan_id}`. {progress_percentage}% complete{manifest_ref}. All phases done."""
        
        return f"""Continue `{plan_id}`. {progress_percentage}% | Phase {next_phase_number}{manifest_ref}."""
    
    def update_phase_status(
        self,
        master_plan_content: str,
        phase_number: int,
        new_status: str,
        actual_time: Optional[str] = None,
        tokens_saved: Optional[int] = None
    ) -> str:
        """
        Update phase status in master plan content.
        
        Args:
            master_plan_content: Current master plan markdown
            phase_number: Phase number to update
            new_status: New status (e.g., "IN PROGRESS", "COMPLETE")
            actual_time: Actual time taken (e.g., "2h 15m")
            tokens_saved: Tokens saved in this phase
        
        Returns:
            Updated master plan content
        """
        # Find phase line in table
        pattern = rf"\| {phase_number} \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|"
        
        def replace_phase(match):
            phase_name = match.group(1).strip()
            old_status = match.group(2).strip()
            old_actual = match.group(3).strip()
            old_tokens = match.group(4).strip()
            
            # Update status with emoji
            status_emoji = {
                "PENDING": "⏸️",
                "IN PROGRESS": "🚀",
                "COMPLETE": "✅",
                "BLOCKED": "🚫"
            }
            new_status_display = f"{status_emoji.get(new_status, '')} {new_status}"
            
            # Update actual time
            actual_display = actual_time if actual_time else old_actual
            
            # Update tokens
            tokens_display = str(tokens_saved) if tokens_saved is not None else old_tokens
            
            return f"| {phase_number} | {phase_name} | {new_status_display} | {actual_display} | {tokens_display} |"
        
        updated_content = re.sub(pattern, replace_phase, master_plan_content)
        return updated_content
    
    # ===== Private Helper Methods =====
    
    def _generate_header(self, plan_id: str, metadata: Dict, compressed: bool = False) -> str:
        """Generate plan header."""
        date = metadata.get("date", datetime.now().strftime("%Y-%m-%d"))
        complexity = metadata.get("complexity_tier", "N/A")
        
        if compressed:
            # Compressed: ultra-minimal (target: < 25 tokens)
            title = metadata.get("title", plan_id.replace('-', ' ').title())
            return f"""🧠 {title}\n**{plan_id}** | {date} | T{complexity}\n\n---"""
        else:
            # Verbose: multi-line (current: 33 tokens)
            return f"""🧠 CORTEX - {plan_id.replace('-', ' ').title()}
**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX

---

**Plan ID:** {plan_id}  
**Date:** {date}  
**Complexity Tier:** {complexity}

---"""
    
    def _generate_executive_summary(self, summary: str) -> str:
        """Generate executive summary section."""
        return f"""## 🎯 Executive Summary

{summary}

---"""
    
    def _generate_continuation_prompt_section(
        self,
        plan_id: str,
        completed_phases: int,
        total_phases: int,
        next_phase_number: Optional[int],
        next_phase_name: Optional[str],
        progress_percentage: int,
        compressed: bool = False,
        manifest_path: Optional[str] = None
    ) -> str:
        """Generate continuation prompt section with optional manifest reference."""
        prompt = self.generate_continuation_prompt(
            plan_id=plan_id,
            completed_phases=completed_phases,
            total_phases=total_phases,
            next_phase_number=next_phase_number,
            next_phase_name=next_phase_name,
            progress_percentage=progress_percentage,
            manifest_path=manifest_path
        )
        
        if compressed:
            # Compressed: inline format (target: < 30 tokens with manifest)
            return f"""## 🔄 Continue
{prompt}

---"""
        else:
            # Verbose: with manifest reference for full context
            return f"""## 🔄 Continuation Prompt

**COPY-PASTE THIS TO RESUME WORK:**

```markdown
{prompt}
```

---"""
            return f"""## 🔄 Continuation Prompt

**COPY-PASTE THIS TO RESUME WORK:**

```markdown
{prompt}
```

---"""
    
    def _generate_phases_table(self, phases: List[Dict], include_tokens: bool, compressed: bool = False) -> str:
        """Generate phases table with optional compression."""
        headers = "| Phase | Name | Status | Actual | Elapsed |"
        separator = "|-------|------|--------|--------|---------|"
        
        if include_tokens:
            headers += " Tokens Saved |"
            separator += "--------------|" 
        
        # Compressed mode: shorter headers
        if compressed:
            headers = "| # | Name | S | Time | Δ |"
            separator = "|---|------|---|------|---|"
            if include_tokens:
                headers = "| # | Name | S | Time | Δ |"
                separator = "|---|------|---|------|---|"
        
        rows = [headers, separator]
        
        for phase in phases:
            phase_num = phase.get("id", phase.get("phase_number", "?"))
            name = phase.get("name", "Unknown")
            status = phase.get("status", "pending")
            actual = phase.get("actual", "-")
            elapsed = phase.get("elapsed", "-")
            
            # Compress phase name if needed
            if compressed:
                name = self.compress_phase_name(name, compressed=True)
            
            # Status emoji
            if compressed:
                # Compressed: emoji only
                status_emoji = {
                    "pending": "⏸️",
                    "in-progress": "🚀",
                    "complete": "✅",
                    "blocked": "🚫"
                }
            else:
                # Verbose: emoji + text
                status_emoji = {
                    "pending": "⏸️ PENDING",
                    "in-progress": "🚀 IN PROGRESS",
                    "complete": "✅ COMPLETE",
                    "blocked": "🚫 BLOCKED"
                }
            status_display = status_emoji.get(status.lower(), status)
            
            row = f"| {phase_num} | {name} | {status_display} | {actual} | {elapsed} |"
            
            if include_tokens:
                tokens = phase.get("tokens_saved", phase.get("tokens", "-"))
                row += f" {tokens} |"
            
            rows.append(row)
        
        return "\n".join(rows)
    
    def _generate_footer(self, compressed: bool = False) -> str:
        """Generate plan footer with optional compression."""
        if compressed:
            # Compressed: minimal (target: 10 tokens)
            return f"---\n**Updated:** {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        else:
            # Verbose: detailed
            return f"""---

**Last Updated:** {datetime.now().strftime("%B %d, %Y, %I:%M %p")}  
**Next Update:** After phase completion"""
    
    def _find_next_phase(self, phases: List[Dict]) -> Optional[int]:
        """Find next pending phase number."""
        for phase in phases:
            if phase.get("status", "").lower() == "pending":
                return phase.get("id", phase.get("phase_number"))
        return None
    
    def _find_next_phase_name(self, phases: List[Dict]) -> Optional[str]:
        """Find next pending phase name."""
        for phase in phases:
            if phase.get("status", "").lower() == "pending":
                return phase.get("name", "Unknown")
        return None
    
    def _calculate_progress(self, phases: List[Dict]) -> int:
        """Calculate overall progress percentage."""
        if not phases:
            return 0
        completed = sum(1 for p in phases if p.get("status") == "complete")
        return int((completed / len(phases)) * 100)
    
    def _sum_actual_time(self, phases: List[Dict]) -> str:
        """Sum actual time from completed phases."""
        # Simple implementation - can be enhanced with timedelta parsing
        return "calculated"
    
    def _sum_elapsed_time(self, phases: List[Dict]) -> str:
        """Sum elapsed time from completed phases."""
        # Simple implementation - can be enhanced with timedelta parsing
        return "calculated"
