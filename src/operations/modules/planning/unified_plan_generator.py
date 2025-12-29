"""
Unified Plan Generator for CORTEX

Shared plan generation logic for all planning orchestrators.
Eliminates duplication across PlanningOrchestrator, TempPlanManager, ADOPlanning.

Author: Asif Hussain
Version: 2.1.0 - Added TaskInjector integration for standard task auto-injection
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import re
import subprocess

from .token_reduction_tracker import TokenReductionTracker
from .master_plan_template import MasterPlanTemplate, MasterPlanSection, SECTION_TEMPLATES
from .task_injector import TaskInjector

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
        self.task_injector = TaskInjector()
        logger.info("✅ UnifiedPlanGenerator initialized with TaskInjector")
    
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
        Generate master plan by rendering template with all required sections.
        
        Template sections (7 mandatory):
        1. Executive Summary
        2. Continuation Prompt
        3. Visual Progress Tracker
        4. Business Value Summary
        5. Phase Breakdown & Execution Status
        6. Request Context
        7. Definition of Done (DoD)
        
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
            Master plan markdown content with all 7 template sections
        """
        from pathlib import Path
        import datetime
        
        # Load template (navigate from src/ up to project root, then to cortex-brain/)
        # Current file: src/operations/modules/planning/unified_plan_generator.py
        # Need: cortex-brain/templates/planning/MASTER-PLAN-TEMPLATE.md
        template_path = Path(__file__).parent.parent.parent.parent.parent / "cortex-brain" / "templates" / "planning" / "MASTER-PLAN-TEMPLATE.md"
        if not template_path.exists():
            logger.warning(f"Template not found: {template_path}, using programmatic generation")
            return self._generate_master_plan_programmatic(plan_id, phases, metadata, include_token_tracking, include_visual_tracker, include_continuation_prompt, compressed, manifest_path)
        
        template_content = template_path.read_text(encoding='utf-8')
        
        # Calculate metrics
        completed_phases = sum(1 for p in phases if p.get("status") == "complete")
        total_phases = len(phases)
        progress_percentage = int((completed_phases / total_phases * 100) if total_phases > 0 else 0)
        
        # Calculate progress bar
        bar_length = 20
        filled = int(bar_length * completed_phases / total_phases) if total_phases > 0 else 0
        progress_bar = "█" * filled + "░" * (bar_length - filled)
        
        # Calculate token metrics
        baseline_tokens = metadata.get("baseline_tokens", 0)
        current_tokens = metadata.get("current_tokens", baseline_tokens)
        tokens_saved = baseline_tokens - current_tokens
        token_reduction_percentage = self.token_tracker.calculate_percentage(baseline_tokens, current_tokens)
        
        # Calculate time metrics
        total_est_hours, total_est_days = self._calculate_total_estimated(phases)
        total_actual_hours = self._calculate_total_actual(phases)
        total_elapsed_hours = self._calculate_total_elapsed(phases)
        time_saved_hours = total_est_hours - total_actual_hours if total_actual_hours > 0 else 0
        efficiency_percentage = self._calculate_efficiency(total_est_hours, total_actual_hours)
        
        # Generate continuation prompt
        next_phase_num = completed_phases + 1 if completed_phases < total_phases else None
        next_phase_name = phases[completed_phases]['name'] if completed_phases < total_phases else None
        continuation_prompt = self.generate_continuation_prompt(
            plan_id=plan_id,
            completed_phases=completed_phases,
            total_phases=total_phases,
            next_phase_number=next_phase_num,
            next_phase_name=next_phase_name,
            progress_percentage=progress_percentage,
            manifest_path=manifest_path
        )
        
        # Generate phase breakdown table
        phase_tables = self._generate_phases_table(phases, include_token_tracking, compressed)
        
        # Build placeholder replacements
        replacements = {
            "{PLAN_TITLE}": metadata.get("feature_name", plan_id),
            "{PLAN_ID}": plan_id,
            "{CREATION_DATE}": metadata.get("creation_date", datetime.datetime.now().strftime("%Y-%m-%d")),
            "{STATUS}": "IN PROGRESS" if completed_phases < total_phases else "COMPLETE",
            "{COMPLEXITY_TIER}": str(metadata.get("complexity_tier", 4)),
            "{PHASES_COMPLETE}": str(completed_phases),
            "{TOTAL_PHASES}": str(total_phases),
            "{PROGRESS_PERCENTAGE}": str(progress_percentage),
            "{PROGRESS_BAR}": progress_bar,
            "{TOKEN_REDUCTION_PERCENTAGE}": f"{token_reduction_percentage:.1f}",
            "{TOKEN_REDUCTION_AMOUNT}": self.token_tracker.format_tokens(tokens_saved),
            "{BASELINE_TOKENS}": self.token_tracker.format_tokens(baseline_tokens),
            "{BASELINE_FILES}": str(metadata.get("total_files", 0)),
            "{ACTUAL_WORK_TIME}": f"{total_actual_hours:.1f}",
            "{TIME_SAVED}": f"{time_saved_hours:.1f}",
            "{DAYS_SAVED}": f"{time_saved_hours/8:.1f}",
            "{ESTIMATED_HOURS}": f"{total_est_hours:.1f}",
            "{ESTIMATED_DAYS}": f"{total_est_days:.1f}",
            "{ESTIMATED_WEEKS}": f"{total_est_days/5:.1f}",
            "{ESTIMATED_VELOCITY}": f"{total_phases/(total_est_days/5) if total_est_days > 0 else 0:.1f}",
            "{ACTUAL_VELOCITY}": f"{self._calculate_velocity(phases):.1f}",
            "{COST_SAVINGS}": f"{time_saved_hours * 75:,.0f}",
            "{PRODUCTIVITY_MULTIPLIER}": f"{total_est_hours/total_actual_hours if total_actual_hours > 0 else 1:.2f}",
            "{EFFICIENCY_PERCENTAGE}": f"{efficiency_percentage:.1f}",
            "{ELAPSED_TIME}": f"{total_elapsed_hours:.1f}",
            "{ELAPSED_DAYS}": f"{total_elapsed_hours/8:.1f}",
            "{ACTUAL_DAYS}": f"{total_actual_hours/8:.1f}",
            "{ACTUAL_WEEKS}": f"{total_elapsed_hours/40:.1f}",
            "{TRADITIONAL_COST}": f"{total_est_hours * 75:,.0f}",
            "{ACTUAL_COST}": f"{total_actual_hours * 75:,.0f}",
            "{VELOCITY_MULTIPLIER}": f"{self._calculate_velocity(phases)/(total_phases/(total_est_days/5)) if total_est_days > 0 else 1:.1f}",
            "{EXECUTIVE_SUMMARY}": metadata.get("summary", "Feature implementation plan generated by CORTEX Planning System."),
            "{CONTINUATION_PROMPT}": continuation_prompt,
            "{PHASE_TABLES}": phase_tables,
            "{REQUEST_CONTEXT}": metadata.get("request_context", "User requested implementation of this feature."),
            "{NARRATIVE_ENHANCED_SUMMARY}": metadata.get("codebase_summary", "AST analysis pending."),
            "{PATTERN_LIST_WITH_EXPLANATIONS}": metadata.get("patterns", "- Analysis pending"),
            "{AFFECTED_FILES_WITH_REASONS}": metadata.get("affected_files", "- Analysis pending"),
            "{DEPENDENCY_NARRATIVE}": metadata.get("dependencies", "Analysis pending."),
            "{INTEGRATION_POINTS_NARRATIVE}": metadata.get("integration_points", "Analysis pending."),
            "{AST_ANALYSIS_TIMESTAMP}": metadata.get("ast_timestamp", "Pending"),
            "{FILE_COUNT}": str(metadata.get("file_count", 0)),
            "{MODULE_COUNT}": str(metadata.get("module_count", 0)),
            "{DOD_CRITERIA}": metadata.get("dod_criteria", "- All tests passing (100% pass rate)\n- Code review completed\n- Documentation updated"),
            "{APPROVAL_PROCESS}": metadata.get("approval_process", "Requires validation before promotion to active plan."),
            "{RELATED_DOCS}": metadata.get("related_docs", "- Planning System 4.0 Manifest: `planning-system-4.0-manifest.yaml`"),
            "{RISK_ANALYSIS}": metadata.get("risk_analysis", "Risk assessment pending."),
            "{SUCCESS_CRITERIA}": metadata.get("success_criteria", "- Feature implemented per requirements\n- All acceptance criteria met"),
            "{FINAL_STATUS}": "IN PROGRESS" if completed_phases < total_phases else "COMPLETE",
            "{TOTAL_DURATION}": f"{total_elapsed_hours:.1f}h"
        }
        
        # Replace all placeholders
        rendered_content = template_content
        for placeholder, value in replacements.items():
            rendered_content = rendered_content.replace(placeholder, value)
        
        return rendered_content
    
    def _generate_master_plan_programmatic(
        self,
        plan_id: str,
        phases: List[Dict],
        metadata: Dict,
        include_token_tracking: bool,
        include_visual_tracker: bool,
        include_continuation_prompt: bool,
        compressed: bool,
        manifest_path: Optional[str]
    ) -> str:
        """
        Fallback programmatic master plan generation (legacy compatibility).
        Used when template file is not available.
        """
        sections = []
        
        # Store compression mode
        self._compressed = compressed
        
        # Get canonical section order
        complexity_tier = metadata.get("complexity_tier", 4)
        section_order = MasterPlanTemplate.get_section_order(complexity_tier)
        
        # Build sections in canonical order
        for section_type in section_order:
            if section_type == MasterPlanSection.CORTEX_HEADER:
                sections.append(MasterPlanTemplate.get_cortex_header())
            elif section_type == MasterPlanSection.TITLE_METADATA:
                sections.append(self._generate_title_metadata(plan_id, metadata))
            elif section_type == MasterPlanSection.REQUEST_CONTEXT:
                if "request_context" in metadata:
                    sections.append(self._generate_request_context(metadata["request_context"]))
            elif section_type == MasterPlanSection.VISUAL_PROGRESS_TRACKER:
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
            elif section_type == MasterPlanSection.PHASE_STATUS_TABLE:
                sections.append(self._generate_phases_table(phases, include_token_tracking, compressed))
            elif section_type == MasterPlanSection.EXECUTIVE_SUMMARY:
                if "summary" in metadata or "goals" in metadata:
                    sections.append(self._generate_executive_summary_full(metadata))
        
        sections.append(self._generate_footer(compressed))
        return "\n\n".join(sections)
    
    def generate_progress_tracker(
        self,
        phases: List[Dict],
        baseline_tokens: int,
        current_tokens: int,
        total_files: int,
        compressed: bool = False,
        include_detailed_tracker: bool = True
    ) -> str:
        """
        Generate visual progress tracker with token metrics.
        
        Args:
            phases: List of phase dictionaries
            baseline_tokens: Baseline token count
            current_tokens: Current token count
            total_files: Total file count
            compressed: Use compressed format
            include_detailed_tracker: Include detailed ASCII box tracker (cortex-3.9 style)
        
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
        elif include_detailed_tracker:
            # Detailed ASCII box tracker (cortex-3.9 style)
            total_actual_minutes = self._calculate_total_actual_minutes(phases)
            total_elapsed_time = self._format_elapsed_time(phases)
            total_est_hours, total_est_days = self._calculate_total_estimated(phases)
            
            # Calculate senior dev estimate range
            base_hours = total_est_hours
            min_estimate = base_hours * 1.55  # Testing (1.30) × Docs (1.15) × Rework (1.10)
            max_estimate = base_hours * 2.05  # 33% complexity buffer
            min_weeks = min_estimate / 40
            max_weeks = max_estimate / 40
            
            tracker = f"""## Visual Progress Tracker

```
+==============================================================================+
  CORTEX Plan Progress Tracker
+==============================================================================+

  Overall Progress:  [{bar}] {percentage:.0f}% ({completed}/{total} phases complete)

  Total Actual Time:    {total_actual_minutes} minutes  |  Total Elapsed Time:  {total_elapsed_time}
  Senior Dev Estimate:  {min_estimate:.0f}-{max_estimate:.0f} hours ({min_weeks:.2f}-{max_weeks:.2f} weeks @ 40h/week baseline)

  Estimation Methodology:
    • Base: {base_hours:.0f} hours pure development
    • Testing overhead: x1.30 (TDD, unit/integration tests)
    • Documentation: x1.15 (inline docs, READMEs, manifests)
    • Rework/refinement: x1.10 (code review, refactoring)
    • Combined multiplier: 1.55x = {min_estimate:.0f} hours minimum
    • Complexity buffer: +33% = {max_estimate:.0f} hours maximum

+==============================================================================+
```"""
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
            tracker = f"""## 📊 Business Value Summary

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

## 💼 ROI Analysis

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
            manifest_path: Path to orchestrator manifest (e.g., planning-system-4.0-manifest.yaml)
        
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
        tokens_saved: Optional[int] = None,
        master_plan_path: Optional[Path] = None,
        auto_commit: bool = True,
        commit_message_prefix: Optional[str] = None
    ) -> str:
        """
        Update phase status in master plan content with optional git commit.
        
        Args:
            master_plan_content: Current master plan markdown
            phase_number: Phase number to update
            new_status: New status (e.g., "IN PROGRESS", "COMPLETE")
            actual_time: Actual time taken (e.g., "2h 15m")
            tokens_saved: Tokens saved in this phase
            master_plan_path: Path to master plan file (required if auto_commit=True)
            auto_commit: Automatically commit changes to git (default: True)
            commit_message_prefix: Optional custom commit message prefix
        
        Returns:
            Updated master plan content
        """
        # Find phase line in table
        pattern = rf"\| {phase_number} \| ([^|]+) \| ([^|]+) \| ([^|]+) \| ([^|]+) \|"
        
        phase_name = ""
        
        def replace_phase(match):
            nonlocal phase_name
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
        
        # Auto-commit if requested and status is COMPLETE
        if auto_commit and new_status == "COMPLETE" and master_plan_path:
            try:
                # Write updated content to file
                with open(master_plan_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)
                
                # Perform git commit
                self._git_commit_phase_completion(
                    phase_number=phase_number,
                    phase_name=phase_name,
                    master_plan_path=master_plan_path,
                    commit_message_prefix=commit_message_prefix
                )
                
                logger.info(f"✅ Auto-committed Phase {phase_number} completion to git")
            except Exception as e:
                logger.warning(f"⚠️ Failed to auto-commit Phase {phase_number}: {e}")
                # Continue anyway - content is updated, just not committed
        
        return updated_content
    
    def _git_commit_phase_completion(
        self,
        phase_number: int,
        phase_name: str,
        master_plan_path: Path,
        commit_message_prefix: Optional[str] = None
    ) -> bool:
        """
        Commit phase completion to git.
        
        Args:
            phase_number: Phase number completed
            phase_name: Phase name
            master_plan_path: Path to master plan file
            commit_message_prefix: Optional custom commit message prefix
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Get repository root (master plan path is relative to repo)
            repo_root = master_plan_path.parent
            while repo_root.parent != repo_root:
                if (repo_root / ".git").exists():
                    break
                repo_root = repo_root.parent
            
            # Build commit message
            if commit_message_prefix:
                commit_msg = f"{commit_message_prefix}: Phase {phase_number} - {phase_name} complete"
            else:
                commit_msg = f"docs: Phase {phase_number} complete - {phase_name}\n\n- Updated master plan with phase completion\n- Status: ✅ COMPLETE"
            
            # Stage master plan file
            subprocess.run(
                ["git", "add", str(master_plan_path)],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True
            )
            
            # Commit changes
            result = subprocess.run(
                ["git", "commit", "-m", commit_msg],
                cwd=repo_root,
                check=True,
                capture_output=True,
                text=True
            )
            
            logger.info(f"📝 Git commit successful: {commit_msg.split(chr(10))[0]}")
            return True
            
        except subprocess.CalledProcessError as e:
            logger.warning(f"⚠️ Git commit failed: {e.stderr}")
            return False
        except Exception as e:
            logger.error(f"❌ Unexpected error during git commit: {e}")
            return False
    
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
    
    def _generate_phases_table(self, phases: List[Dict], include_tokens: bool, compressed: bool = False, detailed_timing: bool = True) -> str:
        """Generate phases table with optional compression and detailed timing.
        
        Args:
            phases: List of phase dictionaries
            include_tokens: Whether to include token savings column
            compressed: Use compressed format
            detailed_timing: Include Start/End/Actual/Elapsed/Sub-Plan columns (cortex-3.9 style)
        
        Returns:
            Markdown table string
        """
        if detailed_timing and not compressed:
            # Detailed timing table (cortex-3.9 style)
            return self._generate_detailed_phases_table(phases)
        
        # Standard table format
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
    
    def _generate_detailed_phases_table(self, phases: List[Dict]) -> str:
        """
        Generate detailed phases table with Start/End/Actual/Elapsed/Sub-Plan columns.
        
        This is the cortex-3.9 style table format.
        
        Args:
            phases: List of phase dictionaries
            
        Returns:
            Markdown table string
        """
        headers = "| Phase | Name | Status | Start | End | Actual | Elapsed | Sub-Plan |"
        separator = "|-------|------|--------|-------|-----|--------|---------|----------|"
        
        rows = [
            "### Phase Status Table",
            "",
            headers,
            separator
        ]
        
        for phase in phases:
            phase_num = phase.get("id", phase.get("phase_number", "?"))
            name = phase.get("name", "Unknown")
            status = phase.get("status", "pending")
            start = phase.get("start_time", "-")
            end = phase.get("end_time", "-")
            actual = phase.get("actual", "-")
            elapsed = phase.get("elapsed", "-")
            sub_plan = phase.get("sub_plan", "")
            
            # Status emoji
            status_emoji = {
                "pending": "⏳ Pending",
                "in-progress": "🟡 In Progress",
                "complete": "✅ Complete",
                "blocked": "⚠️ Blocked"
            }
            status_display = status_emoji.get(status.lower(), status)
            
            # Sub-plan link
            sub_plan_display = f"[{sub_plan}]({sub_plan})" if sub_plan else "-"
            
            row = f"| {phase_num} | {name} | {status_display} | {start} | {end} | {actual} | {elapsed} | {sub_plan_display} |"
            rows.append(row)
        
        # Add legend
        rows.append("")
        rows.append("**Legend:**")
        rows.append("- ⏳ Pending - Not started")
        rows.append("- 🟡 In Progress - Active development")
        rows.append("- ✅ Complete - Finished and validated")
        rows.append("- ⚠️ Blocked - Dependency or issue preventing progress")
        
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
    
    def _calculate_total_actual_minutes(self, phases: List[Dict]) -> int:
        """
        Calculate total actual time in minutes from completed and in-progress phases.
        
        Returns:
            Total minutes as integer
        """
        total_hours = 0.0
        
        for phase in phases:
            status = phase.get("status", "").lower()
            if status not in ["complete", "in-progress"]:
                continue
            
            actual = phase.get("actual", "")
            if not actual or actual == "-":
                continue
            
            hours = self._parse_time_to_hours(actual)
            total_hours += hours
        
        return int(total_hours * 60)
    
    def _format_elapsed_time(self, phases: List[Dict]) -> str:
        """
        Format total elapsed time in H:MM format from completed and in-progress phases.
        
        Args:
            phases: List of phase dictionaries
            
        Returns:
            Formatted elapsed time string (e.g., "4:45")
        """
        total_hours = 0.0
        
        for phase in phases:
            status = phase.get("status", "").lower()
            if status not in ["complete", "in-progress"]:
                continue
            
            elapsed = phase.get("elapsed", "")
            if not elapsed or elapsed == "-":
                continue
            
            hours = self._parse_time_to_hours(elapsed)
            total_hours += hours
        
        if total_hours == 0:
            return "0:00"
        
        whole_hours = int(total_hours)
        minutes = int((total_hours - whole_hours) * 60)
        return f"{whole_hours}:{minutes:02d}"
    
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
        - "10 min" → 0.167
        - "30m" → 0.5
        - "0:45" → 0.75 (H:MM format)
        
        Args:
            time_str: Time string to parse
            
        Returns:
            Hours as float
        """
        if not time_str or time_str == "-":
            return 0.0
        
        time_str = time_str.lower().strip()
        hours = 0.0
        
        # Handle H:MM format (e.g., "0:45" or "1:30")
        if ":" in time_str and not "h" in time_str and not "d" in time_str:
            parts = time_str.split(":")
            if len(parts) == 2:
                try:
                    h = float(parts[0])
                    m = float(parts[1])
                    return h + (m / 60)
                except ValueError:
                    pass
        
        # Handle "16h (2d)" format - extract hours before parentheses
        if "(" in time_str:
            time_str = time_str.split("(")[0].strip()
        
        # Handle "10 min" or "30 min" format
        if "min" in time_str and "h" not in time_str:
            minutes = float(time_str.replace("min", "").strip())
            return minutes / 60
        
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
        elif "m" in time_str:
            # Minutes only: "30m" → 0.5h
            minutes = float(time_str.replace("m", "").strip())
            hours = minutes / 60
        
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
    
    # ===== New Section Generators (Canonical Order) =====
    
    def _generate_title_metadata(self, plan_id: str, metadata: Dict) -> str:
        """Generate title and metadata section (Section 2)."""
        title = metadata.get("title", plan_id.replace('-', ' ').title())
        tier = metadata.get("complexity_tier", "N/A")
        tier_label = "Complex" if tier >= 4 else "Documented" if tier >= 3 else "Lightweight"
        
        return f"""# {title}

**Plan Name:** {title}  
**Type:** Tier {tier} {tier_label} Plan  
**Status:** {metadata.get('status', '⏳ In Progress')}  
**Created:** {metadata.get('created', datetime.now().strftime('%Y-%m-%d %I:%M %p'))}  
**Last Updated:** {metadata.get('last_updated', datetime.now().strftime('%Y-%m-%d %I:%M %p'))}  
**Completed:** {metadata.get('completed', 'TBD')}  
**Version:** {metadata.get('version', '1.0.0')}

---"""
    
    def _generate_request_context(self, context: str) -> str:
        """Generate request context section (Section 3)."""
        return f"""## Request Context

{context}

---"""
    
    def _generate_executive_summary_full(self, metadata: Dict) -> str:
        """Generate full executive summary section (Section 6)."""
        summary = metadata.get("summary", "")
        goals = metadata.get("goals", [])
        outcomes = metadata.get("outcomes", [])
        autonomous = metadata.get("autonomous_execution", "")
        
        sections = [f"## 🎯 Executive Summary", "", summary]
        
        if goals:
            sections.extend(["", "**Primary Goals:**"])
            sections.extend([f"- {goal}" for goal in goals])
        
        if outcomes:
            sections.extend(["", "**Key Outcomes:**"])
            sections.extend([f"- {outcome}" for outcome in outcomes])
        
        if autonomous:
            sections.extend(["", "**Autonomous Execution:**", autonomous])
        
        sections.append("\n---")
        return "\n".join(sections)
    
    def _generate_architectural_changes(self, changes: str) -> str:
        """Generate architectural changes section (Section 7)."""
        return f"""## 🏗️ Architectural Changes

{changes}

---"""
    
    def _generate_governance_framework(self, framework: str) -> str:
        """Generate governance framework section (Section 8)."""
        return f"""## 🛡️ Governance Framework

### New Brain Protection Rules (SKULL System)

{framework}

---"""
    
    def _generate_phase_overview(self, overview: str) -> str:
        """Generate phase overview section (Section 9)."""
        return f"""## 📋 Phase Overview

{overview}

---"""
    
    def _generate_dependency_graph(self, graph: str) -> str:
        """Generate dependency graph section (Section 10)."""
        return f"""## 🔗 Dependency Graph

{graph}

---"""
    
    def _generate_success_criteria(self, criteria: str) -> str:
        """Generate success criteria section (Section 11)."""
        return f"""## ✅ Success Criteria

{criteria}

---"""
    
    def _generate_deliverables(self, deliverables: str) -> str:
        """Generate deliverables section (Section 12)."""
        return f"""## 📁 Deliverables

{deliverables}

---"""
    
    def _generate_risk_analysis(self, risks: str) -> str:
        """Generate risk analysis section (Section 13)."""
        return f"""## 🚨 Risk Analysis

{risks}

---"""
    
    def _generate_related_documentation(self, docs: str) -> str:
        """Generate related documentation section (Section 14)."""
        return f"""## 📖 Related Documentation

{docs}

---"""
    
    def _generate_execution_strategy(self, strategy: str) -> str:
        """Generate execution strategy section (Section 15)."""
        return f"""## 🚀 Execution Strategy

{strategy}

---"""
    
    def _generate_version_history(self, history: List[Dict]) -> str:
        """Generate version history section (Section 16)."""
        rows = []
        for v in history:
            rows.append(f"| {v.get('version', 'N/A')} | {v.get('date', 'N/A')} | {v.get('author', 'N/A')} | {v.get('changes', 'N/A')} |")
        
        return f"""## 🔄 Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
{chr(10).join(rows)}

---"""
    
    def _generate_contact_support(self, contact: str) -> str:
        """Generate contact & support section (Section 17)."""
        return f"""## 📞 Contact & Support

{contact}

---"""
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
            hours_int = int(hours) if hours == int(hours) else hours
            return f"{hours_int}h ({days:.1f}d)"
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
    
    def generate_worker_plan(
        self,
        plan_id: str,
        phase_number: int,
        phase_name: str,
        phase_data: Dict[str, Any],
        inject_standard_tasks: bool = True
    ) -> str:
        """
        Generate worker plan (WP##-Phase-Name.md) with optional task injection.
        
        Args:
            plan_id: Plan identifier
            phase_number: Phase number (1-indexed)
            phase_name: Phase name
            phase_data: Phase data dictionary with tasks, deliverables, DoD
            inject_standard_tasks: Whether to inject standard tasks
            
        Returns:
            Worker plan markdown content
        """
        logger.info(f"📝 Generating worker plan WP{phase_number:02d}-{phase_name}")
        
        # Get phase tasks
        phase_tasks = phase_data.get("tasks", [])
        
        # Inject standard tasks if enabled
        if inject_standard_tasks:
            phase_tasks = self.task_injector.inject_standard_tasks(
                phase_tasks=phase_tasks,
                phase_number=phase_number,
                phase_name=phase_name
            )
            logger.info(f"✅ Standard tasks injected into WP{phase_number:02d}")
        
        # Build worker plan content
        sections = []
        
        # Header
        sections.append(f"# 🎯 Worker Plan {phase_number:02d}: {phase_name}")
        sections.append(f"**Plan ID:** {plan_id}")
        sections.append(f"**Phase:** {phase_number}")
        sections.append(f"**Status:** {phase_data.get('status', 'PENDING')}")
        sections.append("")
        sections.append("---")
        sections.append("")
        
        # Phase Overview
        sections.append("## 📋 Phase Overview")
        sections.append("")
        sections.append(phase_data.get("description", ""))
        sections.append("")
        sections.append("---")
        sections.append("")
        
        # Tasks
        sections.append("## ✅ Tasks")
        sections.append("")
        
        # Group tasks by category (handle tasks as dicts safely)
        git_tasks = [t for t in phase_tasks if isinstance(t, dict) and t.get("category") == "git"]
        analysis_tasks = [t for t in phase_tasks if isinstance(t, dict) and t.get("category") == "analysis"]
        phase_specific_tasks = [t for t in phase_tasks if isinstance(t, dict) and not t.get("standard_task", False)]
        doc_tasks = [t for t in phase_tasks if isinstance(t, dict) and t.get("category") == "documentation"]
        tdd_tasks = [t for t in phase_tasks if isinstance(t, dict) and t.get("category") == "tdd"]
        dod_tasks = [t for t in phase_tasks if isinstance(t, dict) and t.get("category") == "dod"]
        
        # Start checkpoint
        if git_tasks:
            start_checkpoint = [t for t in git_tasks if "start" in t.get("title", "").lower()]
            if start_checkpoint:
                sections.append("### 📌 Phase Start")
                sections.append("")
                for task in start_checkpoint:
                    status = "✅" if task.get("status") == "complete" else "⏸️"
                    sections.append(f"- [{' ' if task.get('status') != 'complete' else 'x'}] {status} **{task['title']}**")
                    sections.append(f"  - {task['description']}")
                    sections.append(f"  - Estimated: {task.get('estimated', '15m')}")
                sections.append("")
        
        # Analysis
        if analysis_tasks:
            sections.append("### 🔍 Analysis & Context")
            sections.append("")
            for task in analysis_tasks:
                status = "✅" if task.get("status") == "complete" else "⏸️"
                sections.append(f"- [{' ' if task.get('status') != 'complete' else 'x'}] {status} **{task['title']}**")
                sections.append(f"  - {task['description']}")
                sections.append(f"  - Estimated: {task.get('estimated', '30m')}")
            sections.append("")
        
        # Phase-specific tasks
        if phase_specific_tasks:
            sections.append("### 🛠️ Phase-Specific Work")
            sections.append("")
            for task in phase_specific_tasks:
                status = "✅" if task.get("status") == "complete" else "⏸️"
                sections.append(f"- [{' ' if task.get('status') != 'complete' else 'x'}] {status} **{task.get('title', 'Task')}**")
                if "description" in task:
                    sections.append(f"  - {task['description']}")
                sections.append(f"  - Estimated: {task.get('estimated', '1h')}")
            sections.append("")
        
        # Documentation
        if doc_tasks:
            sections.append("### 📝 Documentation")
            sections.append("")
            for task in doc_tasks:
                status = "✅" if task.get("status") == "complete" else "⏸️"
                sections.append(f"- [{' ' if task.get('status') != 'complete' else 'x'}] {status} **{task['title']}**")
                sections.append(f"  - {task['description']}")
                sections.append(f"  - Estimated: {task.get('estimated', '30m')}")
            sections.append("")
        
        # TDD Validation
        if tdd_tasks:
            sections.append("### ✅ TDD Validation")
            sections.append("")
            for task in tdd_tasks:
                status = "✅" if task.get("status") == "complete" else "⏸️"
                sections.append(f"- [{' ' if task.get('status') != 'complete' else 'x'}] {status} **{task['title']}**")
                sections.append(f"  - {task['description']}")
                sections.append(f"  - Estimated: {task.get('estimated', '30m')}")
            sections.append("")
        
        # End checkpoint and DoD
        if git_tasks or dod_tasks:
            sections.append("### 🎯 Phase Completion")
            sections.append("")
            
            # End checkpoint
            end_checkpoint = [t for t in git_tasks if "end" in t.get("title", "").lower() or "complete" in t.get("title", "").lower()]
            for task in end_checkpoint:
                status = "✅" if task.get("status") == "complete" else "⏸️"
                sections.append(f"- [{' ' if task.get('status') != 'complete' else 'x'}] {status} **{task['title']}**")
                sections.append(f"  - {task['description']}")
                sections.append(f"  - Estimated: {task.get('estimated', '15m')}")
            
            # DoD validation
            for task in dod_tasks:
                status = "✅" if task.get("status") == "complete" else "⏸️"
                sections.append(f"- [{' ' if task.get('status') != 'complete' else 'x'}] {status} **{task['title']}**")
                sections.append(f"  - {task['description']}")
                sections.append(f"  - Estimated: {task.get('estimated', '30m')}")
            sections.append("")
        
        sections.append("---")
        sections.append("")
        
        # Deliverables
        sections.append("## 📦 Deliverables")
        sections.append("")
        deliverables = phase_data.get("deliverables", [])
        for deliverable in deliverables:
            sections.append(f"- {deliverable}")
        sections.append("")
        sections.append("---")
        sections.append("")
        
        # DoD Checklist
        sections.append("## ✅ Definition of Done (DoD)")
        sections.append("")
        dod_items = phase_data.get("dod", [])
        for item in dod_items:
            sections.append(f"- [ ] {item}")
        sections.append("")
        
        return "\n".join(sections)

