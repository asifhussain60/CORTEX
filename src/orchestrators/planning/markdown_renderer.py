"""
CORTEX 4.0 Markdown Renderer - Plan Markdown Export

Purpose: Render feature plans as human-readable Markdown documents
Version: 4.0.0
Author: CORTEX Development Team
Migrated: 2025-12-19 (from legacy planning_orchestrator.py)

Key Features (Week 8 MVP):
- Markdown generation from plan data
- Metadata table rendering
- Phase and task rendering
- DoR/DoD checklist rendering
- Risk table rendering
- YAML plan export

Deferred to Week 9:
- Template integration (customizable templates)
- Enhanced formatting options

Architecture:
- Standalone renderer module
- Callable from PlanningOrchestrator
- Returns rendered markdown string and file paths
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml

# Phase 10: Systematic YAML Modularization
from src.utils.file_structure_optimizer import FileStructureOptimizer

logger = logging.getLogger(__name__)


# ============================================================================
# Rendering Result Models
# ============================================================================

@dataclass
class RenderingResult:
    """Result of markdown rendering."""
    success: bool
    markdown_content: Optional[str]
    markdown_path: Optional[Path]
    yaml_path: Optional[Path]
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.now)


# ============================================================================
# Markdown Renderer
# ============================================================================

class MarkdownRenderer:
    """
    CORTEX 4.0 Markdown Renderer.
    
    Renders feature plans as Markdown documents with:
    - Title and metadata table
    - Definition of Ready (DoR) checklist
    - Implementation phases with tasks
    - Definition of Done (DoD) checklist
    - Risk table (if present)
    - TDD requirements (if present)
    
    Week 8 MVP: Basic rendering with comprehensive formatting
    Week 9: Template integration for customizable rendering
    """
    
    def __init__(self, output_dir: Optional[Path] = None, modularization_threshold: int = 20480):
        """
        Initialize markdown renderer.
        
        Args:
            output_dir: Optional output directory (default: current directory)
            modularization_threshold: Size threshold for YAML modularization (default: 20KB)
        """
        self.output_dir = Path(output_dir) if output_dir else Path.cwd()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Phase 10: Initialize YAML modularization optimizer
        self.file_optimizer = FileStructureOptimizer(
            threshold_bytes=modularization_threshold,
            module_key='phases'
        )
        
        logger.info(f"✅ Markdown Renderer initialized (output_dir={self.output_dir}, modularization_threshold={modularization_threshold}B)")
    
    def render(
        self,
        plan_data: Dict[str, Any],
        output_filename: Optional[str] = None,
        save_yaml: bool = True
    ) -> RenderingResult:
        """
        Render plan as markdown.
        
        Args:
            plan_data: Plan data dictionary to render
            output_filename: Optional custom filename (without extension)
            save_yaml: Whether to also save YAML file
        
        Returns:
            RenderingResult with markdown content and file paths
        """
        try:
            # Generate markdown content
            markdown_content = self._generate_markdown(plan_data)
            
            # Determine output filename
            if not output_filename:
                metadata = plan_data.get("metadata", {})
                plan_id = metadata.get("plan_id", "unknown-plan")
                output_filename = plan_id.lower()
            
            # Save markdown file
            markdown_path = self.output_dir / f"{output_filename}.md"
            with open(markdown_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"✅ Markdown saved: {markdown_path.name}")
            
            # Optionally save YAML file
            yaml_path = None
            if save_yaml:
                yaml_path = self.output_dir / f"{output_filename}.yaml"
                
                # Phase 10: Check if we should modularize the YAML
                # First, estimate the size by dumping to string
                yaml_str = yaml.dump(plan_data, default_flow_style=False, sort_keys=False, allow_unicode=True)
                estimated_size = len(yaml_str.encode('utf-8'))
                
                if estimated_size > self.file_optimizer.threshold:
                    logger.info(f"📦 Plan size ({estimated_size}B) exceeds threshold ({self.file_optimizer.threshold}B), modularizing...")
                    
                    # Create modular structure
                    plan_dir = self.output_dir / output_filename
                    plan_dir.mkdir(parents=True, exist_ok=True)
                    
                    # Split into modules
                    yaml_path = self.file_optimizer.split_into_modules(
                        yaml_data=plan_data,
                        output_dir=plan_dir
                    )
                    
                    logger.info(f"✅ Modular YAML saved: {yaml_path.name} + phases/ directory")
                else:
                    # Save monolithic YAML (existing behavior)
                    with open(yaml_path, 'w', encoding='utf-8') as f:
                        f.write(yaml_str)
                    logger.info(f"✅ YAML saved: {yaml_path.name}")
            
            return RenderingResult(
                success=True,
                markdown_content=markdown_content,
                markdown_path=markdown_path,
                yaml_path=yaml_path
            )
        
        except Exception as e:
            logger.error(f"Markdown rendering failed: {e}", exc_info=True)
            return RenderingResult(
                success=False,
                markdown_content=None,
                markdown_path=None,
                yaml_path=None,
                errors=[str(e)]
            )
    
    def _generate_markdown(self, plan_data: Dict[str, Any]) -> str:
        """
        Generate markdown content from plan data.
        
        Args:
            plan_data: Plan data dictionary
        
        Returns:
            Markdown-formatted string
        """
        md = []
        
        # Title (H1)
        metadata = plan_data.get("metadata", {})
        title = metadata.get("title", "Untitled Plan")
        md.append(f"# {title}\n")
        
        # Description
        description = metadata.get("description", "")
        if description:
            md.append(f"{description}\n")
        
        # Metadata table
        md.append(self._render_metadata_table(metadata))
        
        # Definition of Ready
        dor = plan_data.get("definition_of_ready", [])
        if dor:
            md.append(self._render_dor(dor))
        
        # Implementation Phases
        phases = plan_data.get("phases", [])
        if phases:
            md.append(self._render_phases(phases))
        
        # Definition of Done
        dod = plan_data.get("definition_of_done", [])
        if dod:
            md.append(self._render_dod(dod))
        
        # TDD Requirements
        tdd_req = plan_data.get("tdd_requirements", {})
        if tdd_req:
            md.append(self._render_tdd_requirements(tdd_req))
        
        # Risks & Mitigation
        risks = plan_data.get("risks", [])
        if risks:
            md.append(self._render_risks(risks))
        
        # Acceptance Criteria (plan-level)
        acceptance_criteria = plan_data.get("acceptance_criteria", [])
        if acceptance_criteria:
            md.append(self._render_acceptance_criteria(acceptance_criteria))
        
        # Notes
        notes = metadata.get("notes", "")
        if notes:
            md.append(self._render_notes(notes))
        
        return "\n".join(md)
    
    def _render_metadata_table(self, metadata: Dict[str, Any]) -> str:
        """Render metadata as table."""
        md = ["## Plan Metadata\n"]
        md.append("| Field | Value |")
        md.append("|-------|-------|")
        
        # Plan ID
        plan_id = metadata.get("plan_id", "N/A")
        md.append(f"| **Plan ID** | `{plan_id}` |")
        
        # Status
        status = metadata.get("status", "N/A").title()
        md.append(f"| **Status** | {status} |")
        
        # Priority
        priority = metadata.get("priority", "N/A").title()
        md.append(f"| **Priority** | {priority} |")
        
        # Complexity
        complexity = metadata.get("complexity", "N/A")
        complexity_map = {1: "Low", 2: "Medium", 3: "High", 4: "Critical"}
        complexity_str = complexity_map.get(complexity, str(complexity))
        md.append(f"| **Complexity** | {complexity_str} |")
        
        # Plan Type
        plan_type = metadata.get("plan_type", "N/A").title()
        md.append(f"| **Plan Type** | {plan_type} |")
        
        # Created
        created_date = metadata.get("created_date", "N/A")
        created_by = metadata.get("created_by", "Unknown")
        md.append(f"| **Created** | {created_date} by {created_by} |")
        
        # Last Updated
        if "last_updated" in metadata:
            md.append(f"| **Last Updated** | {metadata['last_updated']} |")
        
        # Estimated Hours
        estimated_hours = metadata.get("estimated_hours", 0)
        md.append(f"| **Estimated Hours** | {estimated_hours} |")
        
        # Author
        author = metadata.get("author", "N/A")
        md.append(f"| **Author** | {author} |")
        
        # Version
        version = metadata.get("version", "N/A")
        md.append(f"| **Version** | {version} |")
        
        # Tags
        if "tags" in metadata and metadata["tags"]:
            tags_str = ", ".join([f"`{tag}`" for tag in metadata["tags"]])
            md.append(f"| **Tags** | {tags_str} |")
        
        md.append("")
        return "\n".join(md)
    
    def _render_dor(self, dor: List[str]) -> str:
        """Render Definition of Ready."""
        md = ["## Definition of Ready\n"]
        for item in dor:
            md.append(f"- [ ] {item}")
        md.append("")
        return "\n".join(md)
    
    def _render_overall_progress(self, phases: List[Dict[str, Any]]) -> str:
        """Render overall progress bar from phases."""
        if not phases:
            return ""
        
        # Calculate overall progress
        total_phases = len(phases)
        completed_phases = sum(1 for phase in phases if phase.get("status", "").lower() in ["complete", "completed", "done"])
        progress_percent = int((completed_phases / total_phases) * 100) if total_phases > 0 else 0
        
        # Create progress bar (width 20 for overall)
        filled = int((progress_percent / 100) * 20)
        empty = 20 - filled
        progress_bar = f"[{'█' * filled}{'░' * empty}]"
        
        md = []
        md.append(f"**Overall Progress:** {progress_bar} {progress_percent}% ({completed_phases}/{total_phases} phases complete)\n")
        md.append("")
        return "\n".join(md)
    
    def _render_phases(self, phases: List[Dict[str, Any]]) -> str:
        """Render implementation phases."""
        md = ["## 📈 Phase Progress Overview\n"]
        
        # Add overall progress bar as first item
        overall_progress = self._render_overall_progress(phases)
        if overall_progress:
            md.append(overall_progress)
        
        md.append("## Implementation Phases\n")
        
        for phase in phases:
            # Phase header
            phase_num = phase.get("phase_number", "?")
            phase_name = phase.get("phase_name", "Unnamed Phase")
            estimated = phase.get("estimated_hours", "?")
            
            md.append(f"### Phase {phase_num}: {phase_name}\n")
            md.append(f"**Estimated Hours:** {estimated}\n")
            
            # Phase description
            if "description" in phase:
                md.append(f"{phase['description']}\n")
            
            # Tasks
            tasks = phase.get("tasks", [])
            if tasks:
                md.append("#### Tasks\n")
                for task in tasks:
                    task_id = task.get("task_id", "?")
                    task_name = task.get("task_name", "Unnamed Task")
                    task_hours = task.get("estimated_hours", "?")
                    
                    md.append(f"**{task_id}** - {task_name} ({task_hours}h)")
                    
                    # Task description
                    if "description" in task:
                        md.append(f"  {task['description']}")
                    
                    # Task acceptance criteria
                    if "acceptance_criteria" in task and task["acceptance_criteria"]:
                        md.append("  - **Acceptance Criteria:**")
                        for criterion in task["acceptance_criteria"]:
                            md.append(f"    - {criterion}")
                    
                    md.append("")
            
            # Phase acceptance criteria
            if "acceptance_criteria" in phase and phase["acceptance_criteria"]:
                md.append("#### Phase Acceptance Criteria\n")
                for criterion in phase["acceptance_criteria"]:
                    md.append(f"- [ ] {criterion}")
                md.append("")
            
            # Phase dependencies
            if "dependencies" in phase and phase["dependencies"]:
                md.append("#### Dependencies\n")
                for dep in phase["dependencies"]:
                    md.append(f"- {dep}")
                md.append("")
        
        return "\n".join(md)
    
    def _render_dod(self, dod: List[str]) -> str:
        """Render Definition of Done."""
        md = ["## Definition of Done\n"]
        for item in dod:
            md.append(f"- [ ] {item}")
        md.append("")
        return "\n".join(md)
    
    def _render_tdd_requirements(self, tdd_req: Dict[str, Any]) -> str:
        """Render TDD requirements."""
        md = ["## TDD Requirements\n"]
        
        # TDD DoR
        if "dor" in tdd_req:
            md.append("### TDD Definition of Ready\n")
            for item in tdd_req["dor"]:
                md.append(f"- [ ] {item}")
            md.append("")
        
        # TDD DoD
        if "dod" in tdd_req:
            md.append("### TDD Definition of Done\n")
            for item in tdd_req["dod"]:
                md.append(f"- [ ] {item}")
            md.append("")
        
        return "\n".join(md)
    
    def _render_risks(self, risks: List[Dict[str, Any]]) -> str:
        """Render risks table."""
        md = ["## Risks & Mitigation\n"]
        md.append("| ID | Risk | Likelihood | Impact | Mitigation |")
        md.append("|----|------|------------|--------|------------|")
        
        for risk in risks:
            risk_id = risk.get("risk_id", "?")
            description = risk.get("description", "")
            likelihood = risk.get("likelihood", "?")
            impact = risk.get("impact", "?")
            mitigation = risk.get("mitigation", "")
            md.append(f"| {risk_id} | {description} | {likelihood} | {impact} | {mitigation} |")
        
        md.append("")
        return "\n".join(md)
    
    def _render_acceptance_criteria(self, criteria: List[str]) -> str:
        """Render plan-level acceptance criteria."""
        md = ["## Acceptance Criteria\n"]
        for criterion in criteria:
            md.append(f"- [ ] {criterion}")
        md.append("")
        return "\n".join(md)
    
    def _render_notes(self, notes: str) -> str:
        """Render notes section."""
        md = ["## Notes\n"]
        md.append(notes)
        md.append("")
        return "\n".join(md)


# ============================================================================
# Convenience Functions
# ============================================================================

def render_plan(
    plan_data: Dict[str, Any],
    output_dir: Optional[Path] = None,
    output_filename: Optional[str] = None,
    save_yaml: bool = True
) -> RenderingResult:
    """
    Convenience function to render a plan.
    
    Args:
        plan_data: Plan data dictionary to render
        output_dir: Optional output directory
        output_filename: Optional custom filename
        save_yaml: Whether to also save YAML file
    
    Returns:
        RenderingResult with markdown content and paths
    """
    renderer = MarkdownRenderer(output_dir=output_dir)
    return renderer.render(plan_data, output_filename, save_yaml)


def render_plan_from_file(
    plan_path: Path,
    output_dir: Optional[Path] = None,
    output_filename: Optional[str] = None
) -> RenderingResult:
    """
    Convenience function to render a plan from YAML file.
    
    Args:
        plan_path: Path to plan YAML file
        output_dir: Optional output directory
        output_filename: Optional custom filename
    
    Returns:
        RenderingResult with markdown content and paths
    """
    try:
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan_data = yaml.safe_load(f)
        
        return render_plan(plan_data, output_dir, output_filename, save_yaml=False)
    
    except Exception as e:
        return RenderingResult(
            success=False,
            markdown_content=None,
            markdown_path=None,
            yaml_path=None,
            errors=[f"Failed to load plan file: {e}"]
        )
