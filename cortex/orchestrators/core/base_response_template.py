"""
Base Response Template System for CORTEX Orchestrators.

Provides inheritance-based response templating with:
- Single header per response (no repetition)
- Cascading hierarchy (h2 → h3 → h4)
- Challenge boxes with visual callouts
- Problem/Solution 2-column tables
- Registry-driven customization per orchestrator

Module: cortex.orchestrators.core.base_response_template
Author: Asif Hussain
Created: 2026-02-09
Version: 1.0
Authority: ENH-064 Response Template Migration
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import yaml
from pathlib import Path


# ============================================================================
# ENUMERATIONS
# ============================================================================


class SeverityLevel(str, Enum):
    """Severity level for challenge boxes and alerts."""
    
    CRITICAL = "CRITICAL"
    WARNING = "WARNING"
    INFO = "INFO"
    SUCCESS = "SUCCESS"


class SectionType(str, Enum):
    """Section type for automatic icon selection."""
    
    ANALYSIS = "analysis"
    FINDINGS = "findings"
    RECOMMENDATIONS = "recommendations"
    IMPLEMENTATION = "implementation"
    TESTING = "testing"
    METRICS = "metrics"
    NEXT_STEPS = "next_steps"
    VERDICT = "verdict"


# ============================================================================
# DATA MODELS
# ============================================================================


@dataclass
class TemplateConfig:
    """Configuration for orchestrator-specific templates."""
    
    orchestrator_name: str
    """Name of the orchestrator"""
    
    custom_blocks: List[str] = field(default_factory=list)
    """Custom template blocks available"""
    
    section_icons: Dict[str, str] = field(default_factory=dict)
    """Section name → emoji mapping"""
    
    enable_challenge_box: bool = True
    """Whether to enable challenge boxes"""
    
    enable_problem_solution: bool = True
    """Whether to enable problem/solution tables"""
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    """Additional metadata"""


# ============================================================================
# BASE RESPONSE TEMPLATE
# ============================================================================


class BaseResponseTemplate(ABC):
    """
    Abstract base class for orchestrator response templates.
    
    Provides:
    - Single header generation (prevents repetition)
    - Cascading hierarchy (## → ### → ####)
    - Challenge boxes with visual borders
    - Problem/Solution 2-column tables
    - Registry-driven customization
    
    Usage:
        class MyOrchestrator(BaseOrchestrator, BaseResponseTemplate):
            def __init__(self):
                BaseResponseTemplate.__init__(self, "MyOrchestrator")
                
            def compose(self, **kwargs) -> str:
                response = self.header("ANALYZE")
                response += self.section("Analysis Results", "📊")
                response += self.subsection("Key Findings")
                response += self.challenge_box("Design Question", "Should we...?")
                return response
    """
    
    def __init__(
        self,
        orchestrator_name: str,
        mode: str = "CORTEX",
        author: str = "Asif Hussain",
        config_path: Optional[Path] = None
    ):
        """
        Initialize base response template.
        
        Args:
            orchestrator_name: Name of orchestrator (e.g., "TDDOrchestrator")
            mode: Response mode (default: "CORTEX")
            author: Author name (default: "Asif Hussain")
            config_path: Path to template configuration YAML
        """
        self.orchestrator_name = orchestrator_name
        self.mode = mode
        self.author = author
        self._header_generated = False
        self._section_count = 0
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Section icon mapping
        self._section_icons = {
            SectionType.ANALYSIS: "🔍",
            SectionType.FINDINGS: "📋",
            SectionType.RECOMMENDATIONS: "🚀",
            SectionType.IMPLEMENTATION: "🔨",
            SectionType.TESTING: "🧪",
            SectionType.METRICS: "📊",
            SectionType.NEXT_STEPS: "⏭️",
            SectionType.VERDICT: "✅",
        }
        self._section_icons.update(self.config.section_icons)
        
        # Severity emoji mapping
        self._severity_emoji = {
            SeverityLevel.CRITICAL: "🔴",
            SeverityLevel.WARNING: "⚠️",
            SeverityLevel.INFO: "ℹ️",
            SeverityLevel.SUCCESS: "✅",
        }
    
    def _load_config(self, config_path: Optional[Path]) -> TemplateConfig:
        """
        Load orchestrator-specific configuration from YAML.
        
        Args:
            config_path: Path to config file (optional)
        
        Returns:
            TemplateConfig instance
        """
        if config_path and config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                data = yaml.safe_load(f)
                orchestrator_configs = data.get("orchestrator_templates", {})
                orch_data = orchestrator_configs.get(self.orchestrator_name, {})
                
                return TemplateConfig(
                    orchestrator_name=self.orchestrator_name,
                    custom_blocks=orch_data.get("custom_blocks", []),
                    section_icons=orch_data.get("section_icons", {}),
                    enable_challenge_box=orch_data.get("enable_challenge_box", True),
                    enable_problem_solution=orch_data.get("enable_problem_solution", True),
                    metadata=orch_data.get("metadata", {}),
                )
        
        # Default config
        return TemplateConfig(orchestrator_name=self.orchestrator_name)
    
    # ========================================================================
    # HEADER GENERATION (MANDATORY SINGLE CALL)
    # ========================================================================
    
    def header(self, operation: str) -> str:
        """
        Generate response header.
        
        **CRITICAL:** Call ONCE per response. Prevents header repetition.
        
        Args:
            operation: Operation type (e.g., "ANALYZE", "IMPLEMENT", "FIX")
        
        Returns:
            Formatted header markdown
        
        Raises:
            RuntimeError: If header already generated (prevents repetition)
        
        Example:
            >>> template.header("ANALYZE")
            ## 🧠 CORTEX ANALYZE
            **Author:** Asif Hussain | **Orchestrator:** LENSSynthesis ✅
            
            ---
        """
        if self._header_generated:
            raise RuntimeError(
                f"Header already generated for {self.orchestrator_name}. "
                "Call header() ONCE per response to prevent repetition."
            )
        
        self._header_generated = True
        
        return (
            f"## 🧠 {self.mode} {operation}\n"
            f"**Author:** {self.author} | **Orchestrator:** {self.orchestrator_name} ✅\n"
            "\n---\n"
        )
    
    # ========================================================================
    # SECTION HIERARCHY (CASCADING h2 → h3 → h4)
    # ========================================================================
    
    def section(self, title: str, emoji: str = "", section_type: Optional[SectionType] = None) -> str:
        """
        Generate main section header (h2 level).
        
        Use for top-level sections in response. Automatically increments section count.
        
        Args:
            title: Section title
            emoji: Custom emoji (optional, auto-selected if not provided)
            section_type: Section type for automatic icon selection
        
        Returns:
            Formatted section header
        
        Example:
            >>> template.section("Analysis Results", "📊")
            
            ## 📊 Analysis Results
        """
        self._section_count += 1
        
        # Auto-select emoji based on section type or title
        if not emoji:
            if section_type:
                emoji = self._section_icons.get(section_type, "")
            else:
                emoji = self._infer_section_icon(title)
        
        return f"\n## {emoji + ' ' if emoji else ''}{title}\n"
    
    def subsection(self, title: str) -> str:
        """
        Generate subsection header (h3 level).
        
        Use for subsections under main sections.
        
        Args:
            title: Subsection title
        
        Returns:
            Formatted subsection header
        
        Example:
            >>> template.subsection("Key Findings")
            
            ### Key Findings
        """
        return f"\n### {title}\n"
    
    def subsubsection(self, title: str) -> str:
        """
        Generate nested subsection header (h4 level).
        
        Use for nested content under subsections.
        
        Args:
            title: Nested subsection title
        
        Returns:
            Formatted nested header
        
        Example:
            >>> template.subsubsection("Strengths")
            
            #### Strengths
        """
        return f"\n#### {title}\n"
    
    def _infer_section_icon(self, title: str) -> str:
        """
        Infer section icon from title keywords.
        
        Args:
            title: Section title
        
        Returns:
            Emoji icon or empty string
        """
        title_lower = title.lower()
        
        if any(kw in title_lower for kw in ["analysis", "review", "examination"]):
            return "🔍"
        elif any(kw in title_lower for kw in ["finding", "issue", "problem"]):
            return "📋"
        elif any(kw in title_lower for kw in ["recommend", "solution", "proposal"]):
            return "🚀"
        elif any(kw in title_lower for kw in ["implement", "execution", "action"]):
            return "🔨"
        elif any(kw in title_lower for kw in ["test", "validation", "quality"]):
            return "🧪"
        elif any(kw in title_lower for kw in ["metric", "performance", "stat"]):
            return "📊"
        elif any(kw in title_lower for kw in ["next", "step", "action"]):
            return "⏭️"
        elif any(kw in title_lower for kw in ["verdict", "decision", "conclusion"]):
            return "✅"
        
        return ""
    
    # ========================================================================
    # CHALLENGE BOXES (VISUAL CALLOUTS)
    # ========================================================================
    
    def challenge_box(
        self,
        title: str,
        content: str,
        severity: SeverityLevel = SeverityLevel.WARNING,
        response_prompt: str = "**Response:** [Awaiting user input]"
    ) -> str:
        """
        Generate bordered challenge callout box.
        
        Uses markdown blockquote (>) for visual distinction in Copilot Chat.
        
        Args:
            title: Challenge title
            content: Challenge content/question
            severity: Severity level (CRITICAL, WARNING, INFO, SUCCESS)
            response_prompt: Prompt for user response
        
        Returns:
            Formatted challenge box
        
        Example:
            >>> template.challenge_box(
            ...     "Design Question",
            ...     "Should we use async or sync API?",
            ...     SeverityLevel.WARNING
            ... )
            
            > ⚠️ **CHALLENGE: Design Question**
            > 
            > Should we use async or sync API?
            > 
            > **Response:** [Awaiting user input]
        """
        if not self.config.enable_challenge_box:
            return ""
        
        emoji = self._severity_emoji.get(severity, "⚠️")
        
        return (
            f"\n> {emoji} **CHALLENGE: {title}**\n"
            f"> \n"
            f"> {content}\n"
            f"> \n"
            f"> {response_prompt}\n"
        )
    
    # ========================================================================
    # PROBLEM/SOLUTION TABLES
    # ========================================================================
    
    def problem_solution_table(
        self,
        rows: List[Tuple[str, str]],
        problem_header: str = "🔴 **Problem**",
        solution_header: str = "🟢 **Solution**"
    ) -> str:
        """
        Generate Problem/Solution 2-column table.
        
        Args:
            rows: List of (problem, solution) tuples
            problem_header: Custom problem column header
            solution_header: Custom solution column header
        
        Returns:
            Formatted markdown table
        
        Example:
            >>> template.problem_solution_table([
            ...     ("Static routing", "Dynamic multi-orchestrator routing"),
            ...     ("Stub data", "Real AST analysis")
            ... ])
            
            | 🔴 **Problem** | 🟢 **Solution** |
            |----------------|------------------|
            | Static routing | Dynamic multi-orchestrator routing |
            | Stub data | Real AST analysis |
        """
        if not self.config.enable_problem_solution or not rows:
            return ""
        
        # Build table
        header = f"| {problem_header} | {solution_header} |\n"
        separator = "|----------------|------------------|\n"
        body = "\n".join([f"| {prob} | {sol} |" for prob, sol in rows])
        
        return f"\n{header}{separator}{body}\n"
    
    # ========================================================================
    # UTILITY METHODS
    # ========================================================================
    
    def reset_state(self) -> None:
        """
        Reset template state for new response.
        
        Allows reusing template instance across multiple responses.
        """
        self._header_generated = False
        self._section_count = 0
    
    def get_section_count(self) -> int:
        """Get number of sections generated."""
        return self._section_count
    
    def is_header_generated(self) -> bool:
        """Check if header already generated."""
        return self._header_generated
    
    # ========================================================================
    # ABSTRACT METHOD (ORCHESTRATOR-SPECIFIC)
    # ========================================================================
    
    @abstractmethod
    def compose(self, **kwargs) -> str:
        """
        Compose full response using template methods.
        
        **Must be implemented by each orchestrator.**
        
        Args:
            **kwargs: Orchestrator-specific data
        
        Returns:
            Complete formatted response
        
        Example Implementation:
            def compose(self, analysis: Dict, findings: List) -> str:
                response = self.header("ANALYZE")
                response += self.section("Analysis Results", "📊")
                response += self.subsection("Key Findings")
                response += "\\n".join(f"- {f}" for f in findings)
                response += self.challenge_box("Design Question", "Should we...?")
                return response
        """
        pass


# ============================================================================
# MODULE EXPORTS
# ============================================================================


__all__ = [
    "BaseResponseTemplate",
    "TemplateConfig",
    "SeverityLevel",
    "SectionType",
]
