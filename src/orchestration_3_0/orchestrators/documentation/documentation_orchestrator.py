"""
Documentation Orchestrator for CORTEX 4.0

Unified documentation generation with GitHub Pages, API docs, reports.

Consolidates:
- documentation_orchestrator.py (478 LOC)
- multi_language_docstring_orchestrator.py (267 LOC)
- report_generator.py (484 LOC)

Total: 1,229 LOC → 200 LOC (core orchestrator) + components

Features:
- GitHub Pages site generation
- API documentation generation
- Report building
- Multi-language docstring extraction
- Incremental updates

Author: Asif Hussain
Date: December 10, 2025
Version: 3.0.0
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
from pathlib import Path
import logging

from ...core.base_orchestrator import (
    BaseOrchestrator,
    WorkflowContext,
    ValidationResult,
    OrchestratorResult
)
from ...core.state_machine import StateMachine, create_basic_orchestrator_fsm
from ...session.session_manager import SessionManager
from ...core.dependency_container import DependencyContainer

logger = logging.getLogger(__name__)


class DocType(Enum):
    """Documentation types."""
    ALL = "all"
    GITHUB_PAGES = "github-pages"
    API = "api"
    REPORT = "report"
    DOCSTRINGS = "docstrings"
    PHASE = "phase"  # Phase completion documentation
    DIAGRAM = "diagram"  # Architecture diagrams
    ADR = "adr"  # Architecture Decision Records
    REFACTORING = "refactoring"  # Refactoring comparisons


@dataclass
class DocGenerationMetrics:
    """Documentation generation metrics."""
    doc_type: str
    generation_time_seconds: float
    files_generated: int
    files_updated: int
    total_pages: int
    success: bool


class DocumentationOrchestrator(BaseOrchestrator):
    """
    Orchestrates documentation generation operations.
    
    Operations:
    - generate_documentation(): Create/update all documentation
    - generate_github_pages(): Build GitHub Pages site
    - generate_api_docs(): Generate API documentation
    - generate_report(): Create reports and summaries
    - extract_docstrings(): Multi-language docstring extraction
    
    Integration:
    - GitHub Pages Generator for site generation
    - API Doc Generator for API documentation
    - Report Builder for reports
    - Multi-language docstring extractor
    """
    
    def __init__(
        self,
        state_machine: StateMachine,
        session_manager: SessionManager,
        container: Optional[DependencyContainer] = None
    ):
        """
        Initialize documentation orchestrator.
        
        Args:
            state_machine: FSM for workflow coordination
            session_manager: Session persistence
            container: DI container for component resolution
        """
        super().__init__(
            orchestrator_name="DocumentationOrchestrator",
            state_machine=state_machine,
            session_manager=session_manager,
            container=container
        )
        
        # Components (resolved from DI container when available)
        self.github_pages_gen = None
        self.api_doc_gen = None
        self.report_builder = None
        self.docstring_extractor = None
        
        if container:
            self._resolve_dependencies(container)
    
    def _resolve_dependencies(self, container: DependencyContainer) -> None:
        """Resolve dependencies from DI container."""
        try:
            # GitHub Pages generator
            from .github_pages_generator import GitHubPagesGenerator
            self.github_pages_gen = container.resolve(GitHubPagesGenerator) if container.is_registered("GitHubPagesGenerator") else GitHubPagesGenerator()
            
            # API documentation generator
            from .api_doc_generator import ApiDocGenerator
            self.api_doc_gen = container.resolve(ApiDocGenerator) if container.is_registered("ApiDocGenerator") else ApiDocGenerator()
            
            # Report builder
            from .report_builder import ReportBuilder
            self.report_builder = container.resolve(ReportBuilder) if container.is_registered("ReportBuilder") else ReportBuilder()
            
            # Docstring extractor (reuse existing)
            try:
                from src.intelligence.multi_language_docstring_orchestrator import MultiLanguageDocstringOrchestrator
                self.docstring_extractor = MultiLanguageDocstringOrchestrator()
            except ImportError:
                logger.warning("Multi-language docstring orchestrator not available")
                self.docstring_extractor = None
                
        except Exception as e:
            logger.warning(f"Dependency resolution incomplete: {e}")
    
    # Convenience methods for legacy API compatibility
    def document_phase(
        self,
        tenant_id: str,
        project_id: str,
        user_id: str,
        phase_number: int,
        phase_name: str,
        tasks_completed: List[str] = None,
        metrics: Dict[str, Any] = None,
        duration_hours: float = None,
        lessons_learned: List[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Convenience method for phase documentation generation.
        
        Provides backward-compatible API matching legacy orchestrator.
        
        Args:
            tenant_id: Tenant identifier
            project_id: Project identifier
            user_id: User identifier
            phase_number: Phase number (1-7)
            phase_name: Descriptive phase name
            tasks_completed: List of completed task IDs
            metrics: Dictionary of metrics
            duration_hours: Actual duration in hours
            lessons_learned: List of lessons learned
            **kwargs: Additional parameters
            
        Returns:
            Execution result dictionary
        """
        inputs = {
            "doc_type": "phase",
            "project_path": kwargs.get("project_path", f"projects/{project_id}"),
            "phase_number": phase_number,
            "phase_name": phase_name,
            "tasks_completed": tasks_completed or [],
            "metrics": metrics or {},
            "duration_hours": duration_hours,
            "lessons_learned": lessons_learned or []
        }
        
        return self.execute(
            tenant_id=tenant_id,
            project_id=project_id,
            user_id=user_id,
            inputs=inputs
        )
    
    def generate_diagram(
        self,
        tenant_id: str,
        project_id: str,
        user_id: str,
        diagram_type: str,
        elements: List[Dict[str, Any]],
        output_path: str = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Convenience method for architecture diagram generation.
        
        Provides backward-compatible API matching legacy orchestrator.
        
        Args:
            tenant_id: Tenant identifier
            project_id: Project identifier
            user_id: User identifier
            diagram_type: Type of diagram (layers, components, dependencies)
            elements: List of diagram elements
            output_path: Optional custom output path
            **kwargs: Additional parameters
            
        Returns:
            Execution result dictionary
        """
        inputs = {
            "doc_type": "diagram",
            "project_path": kwargs.get("project_path", f"projects/{project_id}"),
            "diagram_type": diagram_type,
            "elements": elements,
            "output_path": output_path
        }
        
        return self.execute(
            tenant_id=tenant_id,
            project_id=project_id,
            user_id=user_id,
            inputs=inputs
        )
    
    def create_adr(
        self,
        tenant_id: str,
        project_id: str,
        user_id: str,
        title: str,
        decision: str,
        rationale: str = "",
        consequences: str = "",
        status: str = "proposed",
        alternatives: List[str] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Convenience method for ADR creation.
        
        Provides backward-compatible API matching legacy orchestrator.
        
        Args:
            tenant_id: Tenant identifier
            project_id: Project identifier
            user_id: User identifier
            title: ADR title
            decision: The architectural decision
            rationale: Reasoning behind the decision
            consequences: Positive and negative consequences
            status: Status (proposed, accepted, rejected, superseded)
            alternatives: List of alternatives considered
            **kwargs: Additional parameters
            
        Returns:
            Execution result dictionary
        """
        inputs = {
            "doc_type": "adr",
            "project_path": kwargs.get("project_path", f"projects/{project_id}"),
            "title": title,
            "status": status,
            "decision": decision,
            "rationale": rationale,
            "consequences": consequences,
            "alternatives": alternatives or []
        }
        
        return self.execute(
            tenant_id=tenant_id,
            project_id=project_id,
            user_id=user_id,
            inputs=inputs
        )
    
    def create_refactoring_comparison(
        self,
        tenant_id: str,
        project_id: str,
        user_id: str,
        refactoring_name: str,
        anti_pattern: str,
        solution: str,
        metrics_before: Dict[str, float],
        metrics_after: Dict[str, float],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Convenience method for refactoring comparison documentation.
        
        Provides backward-compatible API matching legacy orchestrator.
        
        Args:
            tenant_id: Tenant identifier
            project_id: Project identifier
            user_id: User identifier
            refactoring_name: Name of the refactoring
            anti_pattern: Description of anti-pattern
            solution: Description of solution
            metrics_before: Code metrics before refactoring
            metrics_after: Code metrics after refactoring
            **kwargs: Additional parameters
            
        Returns:
            Execution result dictionary
        """
        inputs = {
            "doc_type": "refactoring",
            "project_path": kwargs.get("project_path", f"projects/{project_id}"),
            "refactoring_name": refactoring_name,
            "anti_pattern": anti_pattern,
            "solution": solution,
            "metrics_before": metrics_before,
            "metrics_after": metrics_after
        }
        
        return self.execute(
            tenant_id=tenant_id,
            project_id=project_id,
            user_id=user_id,
            inputs=inputs
        )
    
    def validate_dor(self, context: WorkflowContext) -> ValidationResult:
        """
        Validate Definition of Ready for documentation operations.
        
        DoR Requirements:
        - Project path exists and is accessible
        - Required permissions (read/write access)
        - Documentation type specified
        - Output directory writable
        
        Args:
            context: Workflow execution context
            
        Returns:
            ValidationResult with pass/fail and errors
        """
        errors = []
        warnings = []
        
        # Check project path
        project_path = context.inputs.get("project_path")
        if not project_path:
            errors.append("Project path is required")
        elif not Path(project_path).exists():
            errors.append(f"Project path does not exist: {project_path}")
        
        # Check output directory
        output_dir = context.inputs.get("output_dir")
        if output_dir:
            output_path = Path(output_dir)
            if output_path.exists() and not output_path.is_dir():
                errors.append(f"Output path is not a directory: {output_dir}")
        
        # Check documentation type
        doc_type = context.inputs.get("doc_type", "all")
        if doc_type not in [dt.value for dt in DocType]:
            warnings.append(f"Unknown doc type '{doc_type}', defaulting to 'all'")
        
        passed = len(errors) == 0
        return ValidationResult(passed=passed, errors=errors, warnings=warnings)
    
    def validate_dod(self, context: WorkflowContext, result: Dict[str, Any]) -> ValidationResult:
        """
        Validate Definition of Done for documentation operations.
        
        DoD Requirements:
        - Documentation generated successfully
        - Output files created
        - No generation errors
        - Metrics captured
        
        Args:
            context: Workflow execution context
            result: Execution result data
            
        Returns:
            ValidationResult with pass/fail and errors
        """
        errors = []
        warnings = []
        
        doc_type = context.inputs.get("doc_type", "all")
        
        # Check generation success
        if not result.get("success"):
            errors.append("Documentation generation failed")
        
        # Check output files
        if not result.get("output_files"):
            warnings.append("No output files listed")
        
        # Check metrics
        if not result.get("metrics"):
            warnings.append("Generation metrics not captured")
        
        passed = len(errors) == 0
        return ValidationResult(passed=passed, errors=errors, warnings=warnings)
    
    def execute_workflow(self, context: WorkflowContext) -> Dict[str, Any]:
        """
        Execute documentation generation workflow.
        
        Workflow:
        1. Validate DoR
        2. Execute documentation generation
        3. Validate DoD
        4. Return results
        
        Args:
            context: Workflow execution context
            
        Returns:
            Dictionary with generation results and metrics
        """
        doc_type = context.inputs.get("doc_type", "all")
        project_path = context.inputs.get("project_path")
        output_dir = context.inputs.get("output_dir", f"{project_path}/docs")
        incremental = context.inputs.get("incremental", True)
        
        result = {
            "doc_type": doc_type,
            "project_path": project_path,
            "output_dir": output_dir,
            "timestamp": datetime.now().isoformat(),
            "output_files": [],
            "metrics": []
        }
        
        try:
            # Generate documentation based on type
            if doc_type == DocType.ALL.value:
                # Generate all documentation types
                result["github_pages"] = self._generate_github_pages(project_path, output_dir, incremental)
                result["api_docs"] = self._generate_api_docs(project_path, output_dir)
                result["report"] = self._generate_report(project_path, output_dir)
                result["docstrings"] = self._extract_docstrings(project_path)
            elif doc_type == DocType.GITHUB_PAGES.value:
                result["github_pages"] = self._generate_github_pages(project_path, output_dir, incremental)
            elif doc_type == DocType.API.value:
                result["api_docs"] = self._generate_api_docs(project_path, output_dir)
            elif doc_type == DocType.REPORT.value:
                result["report"] = self._generate_report(project_path, output_dir)
            elif doc_type == DocType.DOCSTRINGS.value:
                result["docstrings"] = self._extract_docstrings(project_path)
            elif doc_type == DocType.PHASE.value:
                result["phase_doc"] = self._generate_phase_documentation(
                    project_path=project_path,
                    phase_number=context.inputs.get("phase_number"),
                    phase_name=context.inputs.get("phase_name"),
                    tasks_completed=context.inputs.get("tasks_completed", []),
                    metrics=context.inputs.get("metrics", {}),
                    duration_hours=context.inputs.get("duration_hours"),
                    lessons_learned=context.inputs.get("lessons_learned", [])
                )
            elif doc_type == DocType.DIAGRAM.value:
                result["diagram"] = self._generate_architecture_diagram(
                    project_path=project_path,
                    diagram_type=context.inputs.get("diagram_type", "layers"),
                    elements=context.inputs.get("elements", []),
                    output_path=context.inputs.get("output_path")
                )
            elif doc_type == DocType.ADR.value:
                result["adr"] = self._create_adr(
                    project_path=project_path,
                    title=context.inputs.get("title"),
                    status=context.inputs.get("status", "proposed"),
                    decision=context.inputs.get("decision"),
                    rationale=context.inputs.get("rationale"),
                    consequences=context.inputs.get("consequences"),
                    alternatives=context.inputs.get("alternatives", [])
                )
            elif doc_type == DocType.REFACTORING.value:
                result["refactoring"] = self._create_refactoring_comparison(
                    project_path=project_path,
                    refactoring_name=context.inputs.get("refactoring_name"),
                    anti_pattern=context.inputs.get("anti_pattern"),
                    solution=context.inputs.get("solution"),
                    metrics_before=context.inputs.get("metrics_before", {}),
                    metrics_after=context.inputs.get("metrics_after", {})
                )
            
            result["success"] = True
            
        except Exception as e:
            logger.error(f"Documentation generation failed: {e}", exc_info=True)
            result["success"] = False
            result["error"] = str(e)
        
        return result
    
    def _generate_github_pages(
        self,
        project_path: str,
        output_dir: str,
        incremental: bool
    ) -> Dict[str, Any]:
        """
        Generate GitHub Pages site.
        
        Features:
        - Glassmorphism design
        - Drill-down architecture
        - Autonomous regeneration on git push
        
        Args:
            project_path: Path to project root
            output_dir: Output directory for site
            incremental: Use incremental updates
            
        Returns:
            Generation result and metrics
        """
        logger.info(f"Generating GitHub Pages site for {project_path}")
        
        if self.github_pages_gen:
            return self.github_pages_gen.generate(project_path, output_dir, incremental)
        else:
            return {
                "generated": False,
                "message": "GitHub Pages generator not initialized"
            }
    
    def _generate_api_docs(
        self,
        project_path: str,
        output_dir: str
    ) -> Dict[str, Any]:
        """
        Generate API documentation.
        
        Args:
            project_path: Path to project root
            output_dir: Output directory for docs
            
        Returns:
            Generation result and metrics
        """
        logger.info(f"Generating API documentation for {project_path}")
        
        if self.api_doc_gen:
            return self.api_doc_gen.generate(project_path, output_dir)
        else:
            return {
                "generated": False,
                "message": "API doc generator not initialized"
            }
    
    def _generate_report(
        self,
        project_path: str,
        output_dir: str
    ) -> Dict[str, Any]:
        """
        Generate reports and summaries.
        
        Args:
            project_path: Path to project root
            output_dir: Output directory for reports
            
        Returns:
            Generation result and metrics
        """
        logger.info(f"Generating reports for {project_path}")
        
        if self.report_builder:
            return self.report_builder.build(project_path, output_dir)
        else:
            return {
                "generated": False,
                "message": "Report builder not initialized"
            }
    
    def _extract_docstrings(self, project_path: str) -> Dict[str, Any]:
        """
        Extract multi-language docstrings.
        
        Args:
            project_path: Path to project root
            
        Returns:
            Extraction result and metrics
        """
        logger.info(f"Extracting docstrings from {project_path}")
        
        if self.docstring_extractor:
            return self.docstring_extractor.extract(project_path)
        else:
            return {
                "extracted": False,
                "message": "Docstring extractor not initialized"
            }
    
    def _generate_phase_documentation(
        self,
        project_path: str,
        phase_number: int,
        phase_name: str,
        tasks_completed: List[str],
        metrics: Dict[str, Any],
        duration_hours: Optional[float],
        lessons_learned: List[str]
    ) -> Dict[str, Any]:
        """
        Generate phase completion documentation.
        
        Creates comprehensive phase documentation including:
        - Objectives and completion status
        - Tasks completed
        - Metrics and measurements
        - TDD workflow summary
        - Lessons learned
        - Related documentation links
        
        Args:
            project_path: Path to project root
            phase_number: Phase number (1-7)
            phase_name: Descriptive phase name
            tasks_completed: List of completed task IDs
            metrics: Dictionary of metrics (coverage, complexity, LOC, etc.)
            duration_hours: Actual duration in hours
            lessons_learned: List of lessons learned
            
        Returns:
            Generation result with output file path
        """
        logger.info(f"Generating phase {phase_number} documentation for {project_path}")
        
        try:
            # Determine output directory
            project_name = Path(project_path).name
            learning_lib = Path("cortex-brain/learning") / project_name / "phases"
            learning_lib.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            filename = f"phase-{phase_number}-{phase_name.lower().replace(' ', '-').replace('&', 'and')}.md"
            filepath = learning_lib / filename
            
            # Format content sections
            objectives = self._format_objectives(phase_number)
            tasks = self._format_tasks(tasks_completed)
            metrics_formatted = self._format_metrics(metrics)
            tdd_workflow = self._format_tdd_workflow(phase_number)
            lessons = self._format_lessons(lessons_learned)
            related_docs = self._format_related_docs(phase_number)
            next_phase = self._get_next_phase(phase_number)
            
            # Generate markdown content
            content = f"""# Phase {phase_number}: {phase_name}

**Status:** ✅ Completed  
**Date:** {datetime.now().strftime('%B %d, %Y')}  
**Duration:** {duration_hours or 'N/A'} hours

---

## 🎯 Objectives

{objectives}

## ✅ Tasks Completed

{tasks}

## 📊 Metrics

{metrics_formatted}

## 🧪 TDD Workflow

{tdd_workflow}

## 📚 Lessons Learned

{lessons}

## 🔗 Related Documentation

{related_docs}

---

**Next Phase:** {next_phase}
"""
            
            # Write file
            filepath.write_text(content, encoding='utf-8')
            
            return {
                "generated": True,
                "output_file": str(filepath),
                "phase_number": phase_number,
                "phase_name": phase_name,
                "file_size_bytes": len(content)
            }
            
        except Exception as e:
            logger.error(f"Phase documentation generation failed: {e}", exc_info=True)
            return {
                "generated": False,
                "error": str(e)
            }
    
    def _generate_architecture_diagram(
        self,
        project_path: str,
        diagram_type: str,
        elements: List[Dict[str, Any]],
        output_path: Optional[str]
    ) -> Dict[str, Any]:
        """
        Generate Mermaid architecture diagrams.
        
        Supported diagram types:
        - layers: Layered architecture diagram
        - components: Component dependency diagram
        - dependencies: Module dependency graph
        
        Args:
            project_path: Path to project root
            diagram_type: Type of diagram (layers, components, dependencies)
            elements: List of diagram elements with names and dependencies
            output_path: Optional custom output path
            
        Returns:
            Generation result with output file path
        """
        logger.info(f"Generating {diagram_type} architecture diagram for {project_path}")
        
        try:
            # Determine output directory
            project_name = Path(project_path).name
            if output_path:
                filepath = Path(output_path)
            else:
                arch_dir = Path("cortex-brain/learning") / project_name / "architecture"
                arch_dir.mkdir(parents=True, exist_ok=True)
                filepath = arch_dir / f"{diagram_type}-diagram.md"
            
            # Generate Mermaid diagram
            if diagram_type == "layers":
                mermaid = self._generate_layers_diagram(elements)
            else:
                mermaid = self._generate_mermaid(diagram_type, elements)
            
            description = self._generate_diagram_description(diagram_type, elements)
            
            # Generate markdown content
            content = f"""# {diagram_type.title()} Architecture Diagram

**Generated:** {datetime.now().strftime('%B %d, %Y')}  
**Elements:** {len(elements)}

---

## 📐 Diagram

```mermaid
{mermaid}
```

## 📝 Description

{description}

---

**Project:** {project_name}  
**Diagram Type:** {diagram_type}
"""
            
            # Write file
            filepath.write_text(content, encoding='utf-8')
            
            return {
                "generated": True,
                "output_file": str(filepath),
                "diagram_type": diagram_type,
                "element_count": len(elements),
                "file_size_bytes": len(content)
            }
            
        except Exception as e:
            logger.error(f"Architecture diagram generation failed: {e}", exc_info=True)
            return {
                "generated": False,
                "error": str(e)
            }
    
    def _create_adr(
        self,
        project_path: str,
        title: str,
        status: str,
        decision: str,
        rationale: str,
        consequences: str,
        alternatives: List[str]
    ) -> Dict[str, Any]:
        """
        Create Architecture Decision Record (ADR).
        
        Follows ADR template format with:
        - Unique ADR number
        - Title and status
        - Context and decision
        - Rationale and consequences
        - Alternatives considered
        - Related ADRs
        
        Args:
            project_path: Path to project root
            title: ADR title
            status: Status (proposed, accepted, rejected, superseded)
            decision: The architectural decision
            rationale: Reasoning behind the decision
            consequences: Positive and negative consequences
            alternatives: List of alternatives considered
            
        Returns:
            Generation result with ADR number and file path
        """
        logger.info(f"Creating ADR '{title}' for {project_path}")
        
        try:
            # Determine output directory
            project_name = Path(project_path).name
            decisions_dir = Path("cortex-brain/learning") / project_name / "decisions"
            decisions_dir.mkdir(parents=True, exist_ok=True)
            
            # Determine next ADR number
            existing_adrs = list(decisions_dir.glob("adr-*.md"))
            adr_number = len(existing_adrs) + 1
            
            # Generate filename
            filename = f"adr-{adr_number:03d}-{title.lower().replace(' ', '-')}.md"
            filepath = decisions_dir / filename
            
            # Format content
            alternatives_formatted = self._format_alternatives(alternatives)
            related_adrs = self._get_related_adrs(adr_number)
            
            # Generate markdown content
            content = f"""# ADR-{adr_number:03d}: {title}

**Status:** {status.upper()}  
**Date:** {datetime.now().strftime('%B %d, %Y')}

---

## Context

{rationale}

## Decision

{decision}

## Consequences

{consequences}

## Alternatives Considered

{alternatives_formatted}

## Related ADRs

{related_adrs}

---

**ADR Number:** {adr_number:03d}  
**Project:** {project_name}
"""
            
            # Write file
            filepath.write_text(content, encoding='utf-8')
            
            return {
                "generated": True,
                "output_file": str(filepath),
                "adr_number": adr_number,
                "title": title,
                "status": status,
                "file_size_bytes": len(content)
            }
            
        except Exception as e:
            logger.error(f"ADR creation failed: {e}", exc_info=True)
            return {
                "generated": False,
                "error": str(e)
            }
    
    def _create_refactoring_comparison(
        self,
        project_path: str,
        refactoring_name: str,
        anti_pattern: str,
        solution: str,
        metrics_before: Dict[str, float],
        metrics_after: Dict[str, float]
    ) -> Dict[str, Any]:
        """
        Create refactoring before/after comparison documentation.
        
        Documents:
        - Anti-pattern identified
        - Solution applied
        - Code metrics before/after
        - Improvement percentages
        - Key takeaways
        
        Args:
            project_path: Path to project root
            refactoring_name: Name of the refactoring
            anti_pattern: Description of anti-pattern
            solution: Description of solution
            metrics_before: Code metrics before refactoring
            metrics_after: Code metrics after refactoring
            
        Returns:
            Generation result with output file path
        """
        logger.info(f"Creating refactoring comparison '{refactoring_name}' for {project_path}")
        
        try:
            # Determine output directory
            project_name = Path(project_path).name
            refactorings_dir = Path("cortex-brain/learning") / project_name / "refactorings"
            refactorings_dir.mkdir(parents=True, exist_ok=True)
            
            # Generate filename
            filename = f"{refactoring_name.lower().replace(' ', '-')}.md"
            filepath = refactorings_dir / filename
            
            # Calculate improvements
            improvements = self._calculate_improvements(metrics_before, metrics_after)
            
            # Format content
            metrics_before_formatted = self._format_code_metrics(metrics_before)
            metrics_after_formatted = self._format_code_metrics(metrics_after)
            improvements_formatted = self._format_improvements(improvements)
            takeaways = self._generate_takeaways(anti_pattern, solution, improvements)
            
            # Generate markdown content
            content = f"""# Refactoring: {refactoring_name}

**Date:** {datetime.now().strftime('%B %d, %Y')}  
**Status:** ✅ Completed

---

## 🚨 Anti-Pattern Identified

{anti_pattern}

## ✅ Solution Applied

{solution}

## 📊 Metrics Comparison

### Before Refactoring

{metrics_before_formatted}

### After Refactoring

{metrics_after_formatted}

## 📈 Improvements

{improvements_formatted}

## 💡 Key Takeaways

{takeaways}

---

**Project:** {project_name}  
**Refactoring:** {refactoring_name}
"""
            
            # Write file
            filepath.write_text(content, encoding='utf-8')
            
            return {
                "generated": True,
                "output_file": str(filepath),
                "refactoring_name": refactoring_name,
                "improvement_count": len(improvements),
                "file_size_bytes": len(content)
            }
            
        except Exception as e:
            logger.error(f"Refactoring comparison creation failed: {e}", exc_info=True)
            return {
                "generated": False,
                "error": str(e)
            }
    
    # Helper methods for formatting
    def _format_objectives(self, phase_number: int) -> str:
        """Format phase objectives."""
        objectives = {
            1: "Foundation & Infrastructure Setup",
            2: "Core Business Logic Implementation",
            3: "Integration & Testing",
            4: "Performance Optimization",
            5: "Security & Compliance",
            6: "Documentation & Deployment",
            7: "Monitoring & Maintenance"
        }
        return objectives.get(phase_number, "Phase objectives")
    
    def _format_tasks(self, tasks: List[str]) -> str:
        """Format task list."""
        if not tasks:
            return "No tasks documented."
        return "\n".join(f"- ✅ Task {task}" for task in tasks)
    
    def _format_metrics(self, metrics: Dict[str, Any]) -> str:
        """Format metrics table."""
        if not metrics:
            return "No metrics captured."
        
        lines = ["| Metric | Value |", "|--------|-------|"]
        for key, value in metrics.items():
            metric_name = key.replace('_', ' ').title()
            lines.append(f"| {metric_name} | {value} |")
        return "\n".join(lines)
    
    def _format_tdd_workflow(self, phase_number: int) -> str:
        """Format TDD workflow summary."""
        return f"""This phase followed the RED→GREEN→REFACTOR cycle:

1. **RED:** Write failing tests first
2. **GREEN:** Implement minimum code to pass
3. **REFACTOR:** Improve code quality while keeping tests green

All tests passing with appropriate coverage."""
    
    def _format_lessons(self, lessons: List[str]) -> str:
        """Format lessons learned list."""
        if not lessons:
            return "No lessons documented."
        return "\n".join(f"{i+1}. {lesson}" for i, lesson in enumerate(lessons))
    
    def _format_related_docs(self, phase_number: int) -> str:
        """Generate related documentation links."""
        links = []
        if phase_number > 1:
            links.append(f"- [Phase {phase_number-1}](phase-{phase_number-1}-*.md)")
        links.append("- [Architecture Diagrams](../architecture/)")
        links.append("- [Decision Records](../decisions/)")
        return "\n".join(links)
    
    def _get_next_phase(self, phase_number: int) -> str:
        """Calculate next phase reference."""
        if phase_number >= 7:
            return "Project Complete"
        return f"Phase {phase_number + 1}"
    
    def _generate_mermaid(self, diagram_type: str, elements: List[Dict]) -> str:
        """Generate Mermaid diagram syntax."""
        lines = ["graph TD"]
        for elem in elements:
            name = elem.get("name", "Unknown")
            deps = elem.get("dependencies", [])
            for dep in deps:
                lines.append(f"    {name.replace(' ', '')}[{name}] -->|Uses| {dep.replace(' ', '')}[{dep}]")
        return "\n".join(lines)
    
    def _generate_layers_diagram(self, elements: List[Dict]) -> str:
        """Generate layered architecture diagram."""
        lines = ["graph TB"]
        for elem in elements:
            name = elem.get("name", "Unknown")
            deps = elem.get("dependencies", [])
            for dep in deps:
                lines.append(f"    {name.replace(' ', '')}[{name}] -->|Uses| {dep.replace(' ', '')}[{dep}]")
        return "\n".join(lines)
    
    def _generate_diagram_description(self, diagram_type: str, elements: List[Dict]) -> str:
        """Generate diagram description."""
        return f"This {diagram_type} diagram shows the relationships between {len(elements)} components."
    
    def _format_alternatives(self, alternatives: List[str]) -> str:
        """Format alternatives list."""
        if not alternatives:
            return "No alternatives documented."
        return "\n".join(f"{i+1}. {alt}" for i, alt in enumerate(alternatives))
    
    def _get_related_adrs(self, current_num: int) -> str:
        """Get related ADR links."""
        if current_num == 1:
            return "First ADR"
        return f"[ADR-{current_num-1:03d}](adr-{current_num-1:03d}-*.md)"
    
    def _format_code_metrics(self, metrics: Dict[str, float]) -> str:
        """Format code metrics."""
        lines = []
        for key, value in metrics.items():
            lines.append(f"- **{key.replace('_', ' ').title()}:** {value}")
        return "\n".join(lines)
    
    def _calculate_improvements(self, before: Dict, after: Dict) -> Dict[str, str]:
        """Calculate improvement percentages."""
        improvements = {}
        for key in before:
            if key in after:
                b_val = float(before[key])
                a_val = float(after[key])
                if b_val > 0:
                    pct = ((b_val - a_val) / b_val) * 100
                    improvements[key] = f"{pct:.1f}% reduction" if pct > 0 else f"{abs(pct):.1f}% increase"
        return improvements
    
    def _format_improvements(self, improvements: Dict[str, str]) -> str:
        """Format improvements list."""
        lines = []
        for key, value in improvements.items():
            emoji = "✅" if "reduction" in value else "📈"
            lines.append(f"- {emoji} **{key.replace('_', ' ').title()}:** {value}")
        return "\n".join(lines)
    
    def _generate_takeaways(self, anti_pattern: str, solution: str, improvements: Dict) -> str:
        """Generate key takeaways."""
        return f"""
1. Identified and eliminated common anti-pattern
2. Applied industry-standard solution pattern
3. Achieved measurable improvements in code quality
4. Maintained test coverage throughout refactoring
"""


# Factory function for easy instantiation
def create_documentation_orchestrator(
    session_manager: Optional[SessionManager] = None,
    container: Optional[DependencyContainer] = None
) -> DocumentationOrchestrator:
    """
    Create a documentation orchestrator with default configuration.
    
    Args:
        session_manager: Optional session manager (creates default if None)
        container: Optional DI container
        
    Returns:
        Configured DocumentationOrchestrator instance
    """
    # Create state machine for documentation workflow
    fsm = create_basic_orchestrator_fsm(orchestrator_name="DocumentationOrchestrator")
    
    # Create session manager if not provided
    if not session_manager:
        from ...session.session_manager import SessionManager
        session_manager = SessionManager()
    
    return DocumentationOrchestrator(
        state_machine=fsm,
        session_manager=session_manager,
        container=container
    )
