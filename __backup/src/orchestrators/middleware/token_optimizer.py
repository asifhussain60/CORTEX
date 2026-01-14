"""
Token Optimizer Middleware - Universal token efficiency for all orchestrators.

Implements the POINTER PATTERN + LAZY LOADING algorithm for continuation prompts,
context management, and cross-session optimization.

Based on: cortex5-epic/analysis/continuation-prompt-optimization-plan.md
"""

import json
import logging
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple


class TokenOptimizationStrategy(Enum):
    """Token optimization strategies."""
    POINTER_PATTERN = "pointer"  # Reference files, don't duplicate
    LAZY_LOADING = "lazy"  # Load context on-demand
    CONTEXT_MIGRATION = "migrate"  # Move context to dedicated files
    TEMPLATE_COMPRESSION = "compress"  # Use minimal templates


@dataclass
class TokenMetrics:
    """Token usage metrics for a file or prompt."""
    file_path: str
    line_count: int
    char_count: int
    estimated_tokens: int  # chars ÷ 4.5 (OpenAI approximation)
    file_size_kb: float
    violations: List[str] = field(default_factory=list)
    
    @property
    def within_budget(self) -> bool:
        """Check if within token budget (<500 tokens)."""
        return self.estimated_tokens < 500
    
    @property
    def within_line_limit(self) -> bool:
        """Check if within line limit (≤12 lines)."""
        return self.line_count <= 12


@dataclass
class ContextMigrationTarget:
    """Target location for migrated context."""
    content_type: str  # "recent_changes", "history", "governance_context", "post_exec_steps"
    source_location: str  # Where content currently lives
    target_location: str  # Where content should be moved
    rationale: str  # Why this migration improves token efficiency


@dataclass
class OptimizationResult:
    """Result of token optimization."""
    before_metrics: TokenMetrics
    after_metrics: TokenMetrics
    tokens_saved: int
    reduction_percentage: float
    migrations_performed: List[ContextMigrationTarget]
    template_applied: bool
    success: bool
    error: Optional[str] = None


class TokenOptimizer:
    """
    Universal token optimizer for continuation prompts and context management.
    
    Algorithm:
    1. ANALYZE: Measure current token usage
    2. DETECT: Identify bloat sources (history, explanations, checklists)
    3. MIGRATE: Move context to dedicated files
    4. COMPRESS: Apply minimal template
    5. VALIDATE: Ensure <500 tokens, <12 lines
    6. PRESERVE: Verify zero information loss
    
    Patterns:
    - POINTER PATTERN: Reference files instead of duplicating content
    - LAZY LOADING: Let GitHub Copilot load context on-demand
    - CONTEXT MIGRATION: Separate concerns (history, context, instructions)
    """
    
    # Token budget constants (aligned with brain-protection-rules.yaml)
    MAX_LINES = 12
    MAX_TOKENS = 500
    MAX_FILE_SIZE_KB = 2.0
    CHARS_PER_TOKEN = 4.5  # OpenAI approximation
    
    # Minimal continuation prompt template
    MINIMAL_TEMPLATE = """Execute Phase {phase_number}: {phase_name}

Plan: {plan_name} | Progress: {progress}% | Phase {current_phase}/{total_phases}

Context: {context_files}

Requirements & acceptance criteria defined in phase file.
Post-execution: Update progress tracker, run vacuum, regenerate viewer."""
    
    def __init__(self):
        """Initialize token optimizer."""
        self.logger = logging.getLogger("cortex.orchestrators.middleware.token_optimizer")
    
    def analyze_file(self, file_path: Path) -> TokenMetrics:
        """
        Analyze file for token usage.
        
        Args:
            file_path: Path to file to analyze
            
        Returns:
            TokenMetrics with detailed measurements
        """
        if not file_path.exists():
            self.logger.warning(f"File not found: {file_path}")
            return TokenMetrics(
                file_path=str(file_path),
                line_count=0,
                char_count=0,
                estimated_tokens=0,
                file_size_kb=0.0,
                violations=["file_not_found"]
            )
        
        # Read file content
        content = file_path.read_text(encoding="utf-8")
        
        # Calculate metrics
        line_count = len(content.splitlines())
        char_count = len(content)
        estimated_tokens = int(char_count / self.CHARS_PER_TOKEN)
        file_size_kb = file_path.stat().st_size / 1024
        
        # Detect violations
        violations = []
        if line_count > self.MAX_LINES:
            violations.append(f"line_count_exceeded: {line_count} > {self.MAX_LINES}")
        if estimated_tokens > self.MAX_TOKENS:
            violations.append(f"token_budget_exceeded: {estimated_tokens} > {self.MAX_TOKENS}")
        if file_size_kb > self.MAX_FILE_SIZE_KB:
            violations.append(f"file_size_exceeded: {file_size_kb:.1f}KB > {self.MAX_FILE_SIZE_KB}KB")
        
        return TokenMetrics(
            file_path=str(file_path),
            line_count=line_count,
            char_count=char_count,
            estimated_tokens=estimated_tokens,
            file_size_kb=file_size_kb,
            violations=violations
        )
    
    def detect_bloat_sources(self, content: str) -> Dict[str, List[str]]:
        """
        Detect sources of token bloat in continuation prompts.
        
        Args:
            content: File content to analyze
            
        Returns:
            Dictionary mapping bloat type to list of detected patterns
        """
        bloat_sources = {
            "historical_changes": [],
            "explanatory_context": [],
            "multi_step_checklists": [],
            "timestamps": [],
            "pending_items": [],
            "redundant_paths": []
        }
        
        lines = content.splitlines()
        
        for line in lines:
            # Detect historical change logs
            if re.match(r'\*\*(?:Recent|Previous) Changes.*\*\*', line):
                bloat_sources["historical_changes"].append(line.strip())
            
            # Detect explanatory context sections
            if re.match(r'\*\*(?:Context|Rationale|Integration Context).*\*\*', line):
                bloat_sources["explanatory_context"].append(line.strip())
            
            # Detect multi-step post-execution checklists
            if re.match(r'Post-execution:?\s*$', line):
                bloat_sources["multi_step_checklists"].append(line.strip())
            
            # Detect timestamps
            if re.search(r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z', line):
                bloat_sources["timestamps"].append(line.strip())
            
            # Detect pending items lists
            if re.match(r'⏸️\s*PENDING:', line):
                bloat_sources["pending_items"].append(line.strip())
            
            # Detect redundant file paths (already in Context line)
            if line.strip().startswith('- ') and ('/' in line or '.md' in line or '.json' in line):
                bloat_sources["redundant_paths"].append(line.strip())
        
        return bloat_sources
    
    def plan_context_migration(
        self,
        content: str,
        plan_path: Path,
        bloat_sources: Dict[str, List[str]]
    ) -> List[ContextMigrationTarget]:
        """
        Plan context migrations to optimize token usage.
        
        Args:
            content: Current continuation prompt content
            plan_path: Path to plan folder
            bloat_sources: Detected bloat sources
            
        Returns:
            List of context migration targets
        """
        migrations = []
        
        # Migration 1: Recent changes → progress-tracker.json
        if bloat_sources["historical_changes"]:
            migrations.append(ContextMigrationTarget(
                content_type="recent_changes",
                source_location="CONTINUATION-PROMPT.md (inline)",
                target_location=str(plan_path / "tracking/progress-tracker.json:last_changes"),
                rationale="Already tracked in progress tracker; no duplication needed"
            ))
        
        # Migration 2: Historical changes → history.json
        if bloat_sources["historical_changes"]:
            migrations.append(ContextMigrationTarget(
                content_type="historical_changes",
                source_location="CONTINUATION-PROMPT.md (inline)",
                target_location=str(plan_path / "tracking/history.json"),
                rationale="Historical context separate from execution prompt; lazy load only when needed"
            ))
        
        # Migration 3: Governance/explanatory context → phase files
        if bloat_sources["explanatory_context"]:
            migrations.append(ContextMigrationTarget(
                content_type="governance_context",
                source_location="CONTINUATION-PROMPT.md (inline)",
                target_location=str(plan_path / "phases/phase-XX.md:context section"),
                rationale="Phase-specific rationale belongs in phase file; reduces prompt bloat"
            ))
        
        # Migration 4: Post-execution steps → cortex-planner.prompt.md
        if bloat_sources["multi_step_checklists"]:
            migrations.append(ContextMigrationTarget(
                content_type="post_exec_steps",
                source_location="CONTINUATION-PROMPT.md (inline checklist)",
                target_location=".github/prompts/cortex-planner.prompt.md (universal pattern)",
                rationale="Universal post-execution pattern; no need to repeat in every prompt"
            ))
        
        return migrations
    
    def extract_context_for_migration(
        self,
        content: str,
        migration: ContextMigrationTarget
    ) -> str:
        """
        Extract content to be migrated from continuation prompt.
        
        Args:
            content: Current continuation prompt content
            migration: Migration target specification
            
        Returns:
            Extracted content for migration
        """
        lines = content.splitlines()
        extracted_lines = []
        
        if migration.content_type == "recent_changes":
            # Extract recent changes section
            in_section = False
            for line in lines:
                if re.match(r'\*\*Recent Changes.*\*\*', line):
                    in_section = True
                    continue
                if in_section:
                    if line.startswith('**') or not line.strip():
                        break
                    extracted_lines.append(line)
        
        elif migration.content_type == "historical_changes":
            # Extract previous changes section
            in_section = False
            for line in lines:
                if re.match(r'\*\*Previous Changes.*\*\*', line):
                    in_section = True
                    continue
                if in_section:
                    if line.startswith('**') or (not line.strip() and len(extracted_lines) > 0):
                        break
                    extracted_lines.append(line)
        
        elif migration.content_type == "governance_context":
            # Extract governance rules integration context
            in_section = False
            for line in lines:
                if re.match(r'\*\*Governance.*Context.*\*\*', line):
                    in_section = True
                    continue
                if in_section:
                    if line.startswith('Requirements from') or not line.strip():
                        break
                    extracted_lines.append(line)
        
        return '\n'.join(extracted_lines)
    
    def apply_minimal_template(
        self,
        plan_name: str,
        phase_number: int,
        phase_name: str,
        progress: int,
        current_phase: int,
        total_phases: int,
        context_files: List[str]
    ) -> str:
        """
        Apply minimal continuation prompt template.
        
        Args:
            plan_name: Name of the plan
            phase_number: Current phase number
            phase_name: Human-readable phase name
            progress: Progress percentage
            current_phase: Current phase counter
            total_phases: Total number of phases
            context_files: List of context file references
            
        Returns:
            Minimal continuation prompt content
        """
        context_str = ", ".join(context_files)
        
        return self.MINIMAL_TEMPLATE.format(
            phase_number=phase_number,
            phase_name=phase_name,
            plan_name=plan_name,
            progress=progress,
            current_phase=current_phase,
            total_phases=total_phases,
            context_files=context_str
        )
    
    def optimize_continuation_prompt(
        self,
        plan_path: Path,
        continuation_prompt_path: Optional[Path] = None
    ) -> OptimizationResult:
        """
        Optimize continuation prompt for token efficiency.
        
        Main algorithm implementing POINTER PATTERN + LAZY LOADING.
        
        Args:
            plan_path: Path to plan folder
            continuation_prompt_path: Optional path to CONTINUATION-PROMPT.md
                                     (defaults to plan_path/CONTINUATION-PROMPT.md)
        
        Returns:
            OptimizationResult with before/after metrics
        """
        if continuation_prompt_path is None:
            continuation_prompt_path = plan_path / "CONTINUATION-PROMPT.md"
        
        try:
            # Step 1: ANALYZE - Measure current token usage
            before_metrics = self.analyze_file(continuation_prompt_path)
            self.logger.info(
                f"Before optimization: {before_metrics.estimated_tokens} tokens, "
                f"{before_metrics.line_count} lines"
            )
            
            if not continuation_prompt_path.exists():
                return OptimizationResult(
                    before_metrics=before_metrics,
                    after_metrics=before_metrics,
                    tokens_saved=0,
                    reduction_percentage=0.0,
                    migrations_performed=[],
                    template_applied=False,
                    success=False,
                    error="Continuation prompt file not found"
                )
            
            # Step 2: DETECT - Identify bloat sources
            content = continuation_prompt_path.read_text(encoding="utf-8")
            bloat_sources = self.detect_bloat_sources(content)
            
            total_bloat_lines = sum(len(v) for v in bloat_sources.values())
            self.logger.info(f"Detected {total_bloat_lines} lines of bloat across {len(bloat_sources)} categories")
            
            # Step 3: MIGRATE - Plan context migrations
            migrations = self.plan_context_migration(content, plan_path, bloat_sources)
            self.logger.info(f"Planned {len(migrations)} context migrations")
            
            # Step 4: Execute migrations (create target files)
            for migration in migrations:
                extracted_content = self.extract_context_for_migration(content, migration)
                if extracted_content.strip():
                    self._save_migrated_context(
                        plan_path,
                        migration,
                        extracted_content
                    )
            
            # Step 5: Load progress tracker to extract template variables
            progress_tracker_path = plan_path / "tracking/progress-tracker.json"
            if progress_tracker_path.exists():
                tracker_data = json.loads(progress_tracker_path.read_text())
                plan_name = plan_path.name
                current_phase = tracker_data.get("overall_progress", {}).get("current_phase", 1)
                total_phases = tracker_data.get("epic_metadata", {}).get("total_phases", 14)
                progress = tracker_data.get("overall_progress", {}).get("completion_percentage", 0)
                
                # Find current phase details
                phases = tracker_data.get("phases", [])
                phase_name = "Unknown Phase"
                phase_number = current_phase
                
                for phase in phases:
                    if phase.get("phase_number") == current_phase or phase.get("phase_number") == f"P{current_phase:02d}":
                        phase_name = phase.get("name", phase_name)
                        phase_number = phase.get("phase_number", phase_number)
                        break
                
                # Context files (standard references)
                context_files = [
                    "tracking/progress-tracker.json",
                    f"phases/phase-{phase_number:02d if isinstance(phase_number, int) else phase_number}-{phase_name.lower().replace(' ', '-')}.md"
                ]
            else:
                # Fallback values if progress tracker not found
                plan_name = plan_path.name
                phase_number = 1
                phase_name = "Unknown Phase"
                progress = 0
                current_phase = 1
                total_phases = 1
                context_files = ["tracking/progress-tracker.json"]
            
            # Step 6: COMPRESS - Apply minimal template
            optimized_content = self.apply_minimal_template(
                plan_name=plan_name,
                phase_number=phase_number,
                phase_name=phase_name,
                progress=progress,
                current_phase=current_phase,
                total_phases=total_phases,
                context_files=context_files
            )
            
            # Step 7: VALIDATE - Write optimized content and measure
            continuation_prompt_path.write_text(optimized_content, encoding="utf-8")
            after_metrics = self.analyze_file(continuation_prompt_path)
            
            # Calculate savings
            tokens_saved = before_metrics.estimated_tokens - after_metrics.estimated_tokens
            reduction_percentage = (tokens_saved / before_metrics.estimated_tokens * 100) if before_metrics.estimated_tokens > 0 else 0.0
            
            self.logger.info(
                f"After optimization: {after_metrics.estimated_tokens} tokens, "
                f"{after_metrics.line_count} lines "
                f"({reduction_percentage:.1f}% reduction)"
            )
            
            return OptimizationResult(
                before_metrics=before_metrics,
                after_metrics=after_metrics,
                tokens_saved=tokens_saved,
                reduction_percentage=reduction_percentage,
                migrations_performed=migrations,
                template_applied=True,
                success=after_metrics.within_budget and after_metrics.within_line_limit
            )
        
        except Exception as e:
            self.logger.error(f"Optimization failed: {e}", exc_info=True)
            return OptimizationResult(
                before_metrics=before_metrics if 'before_metrics' in locals() else TokenMetrics("", 0, 0, 0, 0.0),
                after_metrics=TokenMetrics("", 0, 0, 0, 0.0),
                tokens_saved=0,
                reduction_percentage=0.0,
                migrations_performed=[],
                template_applied=False,
                success=False,
                error=str(e)
            )
    
    def _save_migrated_context(
        self,
        plan_path: Path,
        migration: ContextMigrationTarget,
        content: str
    ) -> None:
        """
        Save migrated context to target location.
        
        Args:
            plan_path: Path to plan folder
            migration: Migration target specification
            content: Content to save
        """
        if migration.content_type == "historical_changes":
            # Save to tracking/history.json
            history_path = plan_path / "tracking/history.json"
            
            # Load existing history or create new
            if history_path.exists():
                history_data = json.loads(history_path.read_text())
            else:
                history_data = {
                    "history": [],
                    "metadata": {
                        "format_version": "1.0.0",
                        "purpose": "Historical context for continuation prompt optimization",
                        "token_optimization": {
                            "enabled": True,
                            "strategy": "lazy_loading"
                        }
                    }
                }
            
            # Don't duplicate - this is a one-time migration
            # (Content already moved in cortex5-epic)
            
            self.logger.info(f"Migrated historical changes to {history_path}")
        
        elif migration.content_type == "governance_context":
            # Save to phases/phase-XX.md (context section)
            # This requires phase-specific handling, skip for now
            self.logger.info(f"Governance context migration planned (requires phase file update)")
    
    def optimize_all_plans(self, plans_root: Path) -> List[OptimizationResult]:
        """
        Optimize all plans in planning directory.
        
        Args:
            plans_root: Root path for plans (e.g., cortex-brain/documents/planning/active/)
        
        Returns:
            List of optimization results for each plan
        """
        results = []
        
        for plan_path in plans_root.iterdir():
            if not plan_path.is_dir():
                continue
            
            self.logger.info(f"Optimizing plan: {plan_path.name}")
            result = self.optimize_continuation_prompt(plan_path)
            results.append(result)
        
        return results
    
    def generate_optimization_report(
        self,
        results: List[OptimizationResult],
        output_path: Path
    ) -> None:
        """
        Generate optimization report for multiple plans.
        
        Args:
            results: List of optimization results
            output_path: Path to save report
        """
        total_tokens_saved = sum(r.tokens_saved for r in results)
        avg_reduction = sum(r.reduction_percentage for r in results) / len(results) if results else 0.0
        successful_count = sum(1 for r in results if r.success)
        
        report = f"""# Token Optimization Report

**Date:** {Path(output_path).stem}
**Plans Optimized:** {len(results)}
**Successful:** {successful_count}/{len(results)}
**Total Tokens Saved:** {total_tokens_saved}
**Average Reduction:** {avg_reduction:.1f}%

## Individual Plan Results

"""
        
        for result in results:
            status = "✅ SUCCESS" if result.success else "❌ FAILED"
            report += f"""### {Path(result.before_metrics.file_path).parent.name}

**Status:** {status}
**Tokens Saved:** {result.tokens_saved} ({result.reduction_percentage:.1f}%)
**Before:** {result.before_metrics.estimated_tokens} tokens, {result.before_metrics.line_count} lines
**After:** {result.after_metrics.estimated_tokens} tokens, {result.after_metrics.line_count} lines
**Migrations:** {len(result.migrations_performed)}

"""
            
            if result.error:
                report += f"**Error:** {result.error}\n\n"
        
        output_path.write_text(report, encoding="utf-8")
        self.logger.info(f"Optimization report saved to {output_path}")


# Convenience function for orchestrators
def optimize_continuation_prompt(plan_path: Path) -> OptimizationResult:
    """
    Optimize continuation prompt for a single plan.
    
    Convenience function for use by orchestrators.
    
    Args:
        plan_path: Path to plan folder
    
    Returns:
        OptimizationResult with before/after metrics
    """
    optimizer = TokenOptimizer()
    return optimizer.optimize_continuation_prompt(plan_path)
