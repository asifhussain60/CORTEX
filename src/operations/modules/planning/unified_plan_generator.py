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
    
    def standardize_hours(self, hours_value: str) -> str:
        """
        Standardize hour format: show hours with days in parentheses if >8h.
        
        Examples:
            "4h" → "4h"
            "16h" → "16h (2d)"
            "2d" → "16h (2d)"
            "24h" → "24h (3d)"
            "1h 30m" → "1.5h"
        
        Args:
            hours_value: Time value in various formats
            
        Returns:
            Standardized format: "Xh (Yd)" or "Xh"
        """
        if not hours_value or hours_value == "-":
            return "-"
        
        # Parse the value
        hours = 0.0
        
        # Handle complex formats like "3d 4h"
        if "d" in hours_value.lower() and "h" in hours_value.lower():
            parts = hours_value.lower().split()
            for part in parts:
                if "d" in part:
                    days = float(part.replace("d", "").strip())
                    hours += days * 8
                elif "h" in part:
                    h = float(part.replace("h", "").strip())
                    hours += h
        elif "d" in hours_value.lower():
            # Extract days (e.g., "2d" → 16h)
            days = float(hours_value.lower().replace("d", "").strip())
            hours = days * 8
        elif "h" in hours_value.lower():
            # Extract hours and minutes
            parts = hours_value.lower().replace("h", "").split()
            hours = float(parts[0])
            if len(parts) > 1 and "m" in parts[1]:
                minutes = float(parts[1].replace("m", ""))
                hours += minutes / 60
        else:
            return hours_value  # Return as-is if format unknown
        
        # Format output
        if hours <= 8:
            # Show days in parentheses if input was in days
            if "d" in hours_value.lower() and not "h" in hours_value.lower():
                days = hours / 8
                return f"{int(hours)}h ({days:.0f}d)" if days == int(days) else f"{int(hours)}h ({days:.1f}d)"
            return f"{hours:.0f}h" if hours == int(hours) else f"{hours:.2f}h"
        else:
            days = hours / 8
            return f"{int(hours)}h ({days:.0f}d)" if days == int(days) else f"{int(hours)}h ({days:.2f}d)"
    
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
            # Calculate efficiency metrics
            total_est_hours, total_est_days = self._calculate_total_estimated(phases)
            total_actual_hours = self._calculate_total_actual(phases)
            total_elapsed_hours = self._calculate_total_elapsed(phases)
            efficiency_percentage = self._calculate_efficiency(total_est_hours, total_actual_hours)
            time_saved_hours = total_est_hours - total_actual_hours if total_actual_hours > 0 else 0
            
            # Calculate average velocity (phases per week)
            avg_velocity = self._calculate_velocity(phases)
            estimated_weeks = total_est_days / 5 if total_est_days > 0 else 1
            estimated_velocity = total / estimated_weeks if estimated_weeks > 0 else 0
            
            # Compact 3-column table format with business value summary
            tracker = f"""## 📊 Visual Progress Tracker

**Overall Progress:** [{bar}] {percentage:.0f}% ({completed}/{total} Phases Complete)  
**Token Reduction:** {percentage_reduction}% ({self.token_tracker.format_tokens(tokens_saved, include_label=True)})  
*Baseline: {self.token_tracker.format_tokens(baseline_tokens)} tokens across {total_files:,} files*

**Legend:** 📅 Plan = Est. effort (1 sr eng, 8h/d) \\| ⚙️ Work = Actual time \\| ⏱️ Wall = Elapsed (incl. reviews)

| 📋 Initial Estimates | ✅ Actual Performance (CORTEX) | 🎯 Efficiency Gains |
|---------------------|-------------------------------|---------------------|
| **Estimate Basis:** 1 Sr Eng \\| 8h/day \\| 40h/wk | **Time Worked:** {self._format_work_hours(total_actual_hours)} | **Time Saved:** {time_saved_hours:.1f}h ({time_saved_hours/8:.1f}d) 🚀 |
| **Total Estimated:** {total_est_hours:.1f}h ({total_est_days:.1f}d) ≈ {estimated_weeks:.1f} wks | **Elapsed Time:** {self._format_elapsed_hours(total_elapsed_hours)} | **Efficiency:** {efficiency_percentage:.1f}% faster |
| **Est. Velocity:** {estimated_velocity:.1f} phases/week | **Actual Velocity:** {avg_velocity:.1f} phases/week | **Cost Savings:** ${time_saved_hours * 75:.0f} (@$75/hr) |
| | **Phases Done:** {completed}/{total} ({percentage:.0f}%) | **Multiplier:** {total_est_hours/total_actual_hours if total_actual_hours > 0 else 1:.2f}x |

---

## 💼 Business Value Summary

| 👤 **Traditional Approach** | ⚡ **CORTEX-Powered Delivery** |
|----------------------------|-------------------------------|
| **Estimated Effort:** {total_est_hours:.1f}h ({total_est_days:.1f} days) | **Actual Effort:** {self._format_work_hours(total_actual_hours)} |
| **Timeline:** {estimated_weeks:.1f} weeks @ 1 senior engineer | **Timeline:** {total_elapsed_hours/40:.1f} weeks with AI acceleration |
| **Labor Cost:** ${total_est_hours * 75:,.0f} (@$75/hr) | **Labor Cost:** ${total_actual_hours * 75:,.0f} (@$75/hr) |
| **Velocity:** {estimated_velocity:.1f} phases/week | **Velocity:** {avg_velocity:.1f} phases/week ({avg_velocity/estimated_velocity if estimated_velocity > 0 else 1:.1f}x faster) |
| | |
| **ROI Impact:** Baseline | **ROI Impact:** ${time_saved_hours * 75:,.0f} saved \\| {efficiency_percentage:.0f}% faster \\| {total_est_hours/total_actual_hours if total_actual_hours > 0 else 1:.1f}x productivity |"""
        
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
        
        return f"""Continue `{plan_id}`. {progress_percentage}% | Phase {next_phase_number}{manifest_ref}. Update Plan/Work/Wall/Tokens columns + Overall Progress totals."""
    
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
        headers = "| Phase | Name | Status | Plan | Work | Wall |"
        separator = "|-------|------|--------|------|------|------|"
        
        if include_tokens:
            headers += " Tokens Saved |"
            separator += "--------------|"
        
        # Compressed mode: shorter headers
        if compressed:
            headers = "| # | Name | S | Est | Time | Δ |"
            separator = "|---|------|---|-----|------|---|"
            if include_tokens:
                headers = "| # | Name | S | Est | Time | Δ |"
                separator = "|---|------|---|-----|------|---|"
        
        rows = [headers, separator]
        
        for phase in phases:
            phase_num = phase.get("id", phase.get("phase_number", "?"))
            name = phase.get("name", "Unknown")
            status = phase.get("status", "pending")
            estimated = phase.get("estimated", "-")
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
            
            row = f"| {phase_num} | {name} | {status_display} | {estimated} | {actual} | {elapsed} |"
            
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
    
    def _sum_estimated_time(self, phases: List[Dict]) -> str:
        """Sum estimated time from all phases."""
        total_hours, total_days = self._calculate_total_estimated(phases)
        if total_hours == 0:
            return "TBD"
        return f"{total_hours:.1f}h ({total_days:.1f}d)"
    
    def _sum_actual_time(self, phases: List[Dict]) -> str:
        """Sum actual time from completed phases."""
        total_hours = self._calculate_total_actual(phases)
        if total_hours == 0:
            return "0h"
        return f"{total_hours:.1f}h"
    
    def _sum_elapsed_time(self, phases: List[Dict]) -> str:
        """Sum elapsed time from completed phases."""
        total_hours = self._calculate_total_elapsed(phases)
        if total_hours == 0:
            return "0h"
        return f"{total_hours:.1f}h"
    
    def _calculate_total_estimated(self, phases: List[Dict]) -> tuple[float, float]:
        """
        Calculate total estimated hours and days from all phases.
        
        Returns:
            Tuple of (total_hours, total_days)
        """
        total_hours = 0.0
        
        for phase in phases:
            estimated = phase.get("estimated", "")
            if not estimated or estimated == "-":
                continue
            
            # Parse various formats: "4h", "16h (2d)", "2d", "1h 30m"
            hours = self._parse_time_to_hours(estimated)
            total_hours += hours
        
        total_days = total_hours / 8
        return total_hours, total_days
    
    def _calculate_total_actual(self, phases: List[Dict]) -> float:
        """Calculate total actual hours from completed phases."""
        total_hours = 0.0
        
        for phase in phases:
            if phase.get("status") != "complete":
                continue
            
            actual = phase.get("actual", "")
            if not actual or actual == "-":
                continue
            
            hours = self._parse_time_to_hours(actual)
            total_hours += hours
        
        return total_hours
    
    def _calculate_total_elapsed(self, phases: List[Dict]) -> float:
        """Calculate total elapsed hours from completed phases."""
        total_hours = 0.0
        
        for phase in phases:
            if phase.get("status") != "complete":
                continue
            
            elapsed = phase.get("elapsed", "")
            if not elapsed or elapsed == "-":
                continue
            
            hours = self._parse_time_to_hours(elapsed)
            total_hours += hours
        
        return total_hours
    
    def _parse_time_to_hours(self, time_str: str) -> float:
        """
        Parse time string to hours.
        
        Supports formats:
        - "4h" → 4.0
        - "16h (2d)" → 16.0
        - "2d" → 16.0
        - "1h 30m" → 1.5
        - "2h 15m" → 2.25
        
        Args:
            time_str: Time string to parse
            
        Returns:
            Hours as float
        """
        if not time_str or time_str == "-":
            return 0.0
        
        time_str = time_str.lower().strip()
        hours = 0.0
        
        # Handle "16h (2d)" format - extract hours before parentheses
        if "(" in time_str:
            time_str = time_str.split("(")[0].strip()
        
        # Handle complex formats like "3d 4h"
        if "d" in time_str and "h" in time_str:
            parts = time_str.split()
            for part in parts:
                if "d" in part:
                    days = float(part.replace("d", "").strip())
                    hours += days * 8
                elif "h" in part:
                    h = float(part.replace("h", "").strip())
                    hours += h
        elif "d" in time_str:
            # Days only: "2d" → 16h
            days = float(time_str.replace("d", "").strip())
            hours = days * 8
        elif "h" in time_str and "m" in time_str:
            # Hours and minutes: "1h 30m" → 1.5h
            parts = time_str.split()
            for part in parts:
                if "h" in part:
                    hours += float(part.replace("h", "").strip())
                elif "m" in part:
                    minutes = float(part.replace("m", "").strip())
                    hours += minutes / 60
        elif "h" in time_str:
            # Hours only: "4h" → 4.0
            hours = float(time_str.replace("h", "").strip())
        
        return hours
    
    def _calculate_efficiency(self, estimated_hours: float, actual_hours: float) -> float:
        """
        Calculate efficiency percentage (how much faster than estimated).
        
        Args:
            estimated_hours: Total estimated hours
            actual_hours: Total actual hours worked
            
        Returns:
            Efficiency percentage (positive means faster than estimated)
        """
        if estimated_hours == 0 or actual_hours == 0:
            return 0.0
        
        time_saved = estimated_hours - actual_hours
        efficiency = (time_saved / estimated_hours) * 100
        return efficiency
    
    def _calculate_velocity(self, phases: List[Dict]) -> float:
        """
        Calculate average velocity (phases per week) based on completed phases.
        
        Args:
            phases: List of phase dictionaries
            
        Returns:
            Phases per week
        """
        completed_phases = [p for p in phases if p.get("status") == "complete"]
        if not completed_phases:
            return 0.0
        
        # Calculate total elapsed time in weeks
        total_elapsed_hours = self._calculate_total_elapsed(phases)
        if total_elapsed_hours == 0:
            return 0.0
        
        total_weeks = total_elapsed_hours / 40  # 40 hours per week
        velocity = len(completed_phases) / total_weeks if total_weeks > 0 else 0.0
        
        return velocity
    
    def _format_work_hours(self, hours: float) -> str:
        """
        Format work hours consistently:
        - Show days only if >= 36h (4.5 days)
        - Use H:MM format for hours < 36h (e.g., "1:25h" instead of "1h 25m")
        
        Args:
            hours: Hours to format
            
        Returns:
            Formatted string
        """
        if hours <= 0:
            return "-"
        
        if hours >= 36:
            # Show in days format
            days = hours / 8
            return f"{hours:.1f}h ({days:.1f}d)"
        else:
            # Show in H:MM format
            whole_hours = int(hours)
            minutes = int((hours - whole_hours) * 60)
            if minutes > 0:
                return f"{whole_hours}:{minutes:02d}h"
            else:
                return f"{whole_hours}h"
    
    def _format_elapsed_hours(self, hours: float) -> str:
        """
        Format elapsed hours in H:MM format with days if >= 36h.
        
        Args:
            hours: Hours to format
            
        Returns:
            Formatted string
        """
        if hours <= 0:
            return "-"
        
        if hours >= 36:
            days = hours / 8
            whole_hours = int(hours)
            minutes = int((hours - whole_hours) * 60)
            if minutes > 0:
                return f"{whole_hours}:{minutes:02d}h ({days:.1f}d)"
            else:
                return f"{whole_hours}h ({days:.1f}d)"
        else:
            whole_hours = int(hours)
            minutes = int((hours - whole_hours) * 60)
            if minutes > 0:
                return f"{whole_hours}:{minutes:02d}h"
            else:
                return f"{whole_hours}h"

