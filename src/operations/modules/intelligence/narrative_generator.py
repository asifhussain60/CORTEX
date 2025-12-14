"""
Narrative Intelligence - Context-aware code explanations and storytelling.

Transforms technical AST analysis into human-friendly narratives that
explain code architecture, changes, and impacts.
"""

from pathlib import Path
from typing import Dict, Any, List, Callable
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class CodeNarrative:
    """Human-friendly code explanation."""
    title: str
    summary: str
    details: List[str]
    impact_analysis: str
    recommendations: List[str]
    technical_depth: str  # "high-level", "detailed", "deep-dive"


class NarrativeGenerator:
    """Generate context-aware code narratives."""
    
    def __init__(self, ast_engine, analyzers: Dict[str, Any]):
        """
        Initialize narrative generator.
        
        Args:
            ast_engine: AST engine for code structure analysis
            analyzers: Dict of analyzers (deduplication, architecture, code_smell)
        """
        self.ast_engine = ast_engine
        self.analyzers = analyzers
        
        # Narrative templates for common scenarios
        self.templates: Dict[str, Callable] = {
            'architecture_change': self._architecture_change_narrative,
            'refactor_explanation': self._refactor_explanation_narrative,
            'code_explanation': self._code_explanation_narrative,
            'impact_analysis': self._impact_analysis_narrative
        }
        
    def generate_narrative(
        self, 
        narrative_type: str,
        context: Dict[str, Any],
        depth: str = "detailed"
    ) -> CodeNarrative:
        """
        Generate narrative for given context.
        
        Args:
            narrative_type: Type of narrative ('architecture_change', 'refactor_explanation', etc.)
            context: Context data (file paths, changes, affected modules, etc.)
            depth: Narrative depth level ('high-level', 'detailed', 'deep-dive')
            
        Returns:
            CodeNarrative with human-friendly explanation
            
        Raises:
            ValueError: If narrative_type is unknown
        """
        logger.info(f"Generating {narrative_type} narrative (depth: {depth})")
        
        if narrative_type not in self.templates:
            raise ValueError(f"Unknown narrative type: {narrative_type}")
            
        template_func = self.templates[narrative_type]
        return template_func(context, depth)
        
    def _architecture_change_narrative(
        self, 
        context: Dict[str, Any],
        depth: str
    ) -> CodeNarrative:
        """
        Generate narrative explaining architecture changes.
        
        Example context:
        {
            'changes': [{'file': 'module.py', 'type': 'layer_move'}],
            'affected_modules': ['auth', 'user', 'api']
        }
        """
        changes = context.get('changes', [])
        affected = context.get('affected_modules', [])
        
        # Analyze architecture violations
        arch_analysis = self.analyzers['architecture'].analyze()
        violations = arch_analysis['violations']
        
        summary = self._generate_change_summary(changes)
        
        details = []
        if depth in ["detailed", "deep-dive"]:
            details.extend([
                f"**Files Modified:** {len(changes)}",
                f"**Modules Affected:** {', '.join(affected)}",
                f"**Architecture Violations:** {len(violations)} detected"
            ])
            
        if depth == "deep-dive":
            details.extend([
                "**Detailed Changes:**",
                *[f"  - {c.get('file', 'unknown')}: {c.get('type', 'unknown')}" for c in changes]
            ])
            
        impact = self._analyze_downstream_impact(affected)
        
        recommendations = self._generate_architecture_recommendations(
            violations, 
            changes
        )
        
        return CodeNarrative(
            title=f"Architecture Change: {summary}",
            summary=summary,
            details=details,
            impact_analysis=impact,
            recommendations=recommendations,
            technical_depth=depth
        )
        
    def _refactor_explanation_narrative(
        self,
        context: Dict[str, Any],
        depth: str
    ) -> CodeNarrative:
        """
        Generate narrative explaining refactoring decisions.
        
        Example context:
        {
            'refactor_type': 'extract_method',
            'original_file': 'service.py',
            'new_structure': ['service.py', 'helpers.py']
        }
        """
        refactor_type = context.get('refactor_type', 'unknown')
        original = context.get('original_file', 'unknown_file.py')
        new_structure = context.get('new_structure', [])
        
        # Analyze code quality improvements
        duplicates = self.analyzers['deduplication'].analyze()
        smells = self.analyzers['code_smell'].analyze(Path(original))
        
        title = self._refactor_type_to_title(refactor_type)
        summary = (
            f"Refactored {original} to improve code quality and maintainability. "
            f"Extracted shared logic into {len(new_structure)} focused modules."
        )
        
        details = [
            f"**Refactor Type:** {refactor_type}",
            f"**Original File:** {original}",
            f"**Duplicates Removed:** {len(duplicates.get('duplicate_groups', []))}",
            f"**Code Smells Fixed:** {len(smells.get('smells', []))}"
        ]
        
        if depth == "deep-dive":
            details.extend([
                "**New Structure:**",
                *[f"  - {file}" for file in new_structure]
            ])
            
        impact = (
            f"Reduces maintenance burden by eliminating {len(duplicates.get('duplicate_groups', []))} "
            f"duplicate code blocks. Improves testability through focused modules."
        )
        
        recommendations = [
            "Update imports in dependent modules",
            "Add unit tests for extracted logic",
            "Update documentation to reflect new structure"
        ]
        
        return CodeNarrative(
            title=title,
            summary=summary,
            details=details,
            impact_analysis=impact,
            recommendations=recommendations,
            technical_depth=depth
        )
        
    def _code_explanation_narrative(
        self,
        context: Dict[str, Any],
        depth: str
    ) -> CodeNarrative:
        """
        Generate narrative explaining code functionality.
        
        Example context:
        {
            'file': 'orchestrator.py',
            'function': 'execute_plan',
            'line_range': [45, 120]
        }
        """
        file_path = Path(context.get('file', 'unknown.py'))
        function = context.get('function', 'unknown_function')
        
        # Use AST for architecture analysis
        arch = self.ast_engine.get_architecture_insights()
        
        summary = f"Explains the purpose and behavior of {function} in {file_path.name}"
        
        details = [
            f"**Function:** {function}",
            f"**Module:** {file_path.stem}",
            f"**Dependencies:** {len(arch.get('dependencies', []))} modules"
        ]
        
        if depth in ["detailed", "deep-dive"]:
            details.extend([
                "**Key Operations:**",
                "  1. Initialize execution context",
                "  2. Validate input parameters",
                "  3. Execute core logic",
                "  4. Handle errors and return results"
            ])
            
        impact = "Central orchestration function - changes affect all planning workflows"
        
        recommendations = [
            "Maintain backward compatibility",
            "Add integration tests for new behavior",
            "Update API documentation"
        ]
        
        return CodeNarrative(
            title=f"Code Explanation: {function}",
            summary=summary,
            details=details,
            impact_analysis=impact,
            recommendations=recommendations,
            technical_depth=depth
        )
        
    def _impact_analysis_narrative(
        self,
        context: Dict[str, Any],
        depth: str
    ) -> CodeNarrative:
        """
        Generate narrative analyzing change impact.
        
        Example context:
        {
            'changed_files': ['router.py', 'analyzer.py'],
            'change_type': 'breaking_change'
        }
        """
        changed_files = context.get('changed_files', [])
        change_type = context.get('change_type', 'modification')
        
        # Analyze downstream dependencies
        arch = self.ast_engine.get_architecture_insights()
        affected_modules = self._find_dependent_modules(changed_files, arch)
        
        title = f"Impact Analysis: {change_type.replace('_', ' ').title()}"
        summary = (
            f"Analyzing impact of changes to {len(changed_files)} files. "
            f"Affects {len(affected_modules)} downstream modules."
        )
        
        details = [
            f"**Changed Files:** {', '.join(changed_files)}",
            f"**Change Type:** {change_type}",
            f"**Affected Modules:** {len(affected_modules)}"
        ]
        
        if depth in ["detailed", "deep-dive"]:
            details.extend([
                "**Downstream Impact:**",
                *[f"  - {module}" for module in affected_modules[:10]]
            ])
            
        impact = self._calculate_risk_level(change_type, len(affected_modules))
        
        recommendations = [
            f"Test all {len(affected_modules)} affected modules",
            "Consider phased rollout for breaking changes",
            "Update documentation for API changes"
        ]
        
        if change_type == 'breaking_change':
            recommendations.insert(0, "⚠️ BREAKING CHANGE - Requires major version bump")
            
        return CodeNarrative(
            title=title,
            summary=summary,
            details=details,
            impact_analysis=impact,
            recommendations=recommendations,
            technical_depth=depth
        )
        
    # Helper methods
    
    def _generate_change_summary(self, changes: List[Dict[str, Any]]) -> str:
        """Generate concise summary of changes."""
        if not changes:
            return "No changes detected"
        
        change_types = set(c.get('type', 'unknown') for c in changes)
        return f"{len(changes)} files modified ({', '.join(change_types)})"
        
    def _analyze_downstream_impact(self, affected_modules: List[str]) -> str:
        """Analyze impact on downstream modules."""
        count = len(affected_modules)
        if count == 0:
            return "No downstream impact detected"
        elif count <= 3:
            return f"Limited impact: {', '.join(affected_modules)}"
        else:
            return f"Moderate impact: {count} modules affected"
            
    def _generate_architecture_recommendations(
        self,
        violations: List[Any],
        changes: List[Dict[str, Any]]
    ) -> List[str]:
        """Generate recommendations for architecture changes."""
        recommendations = []
        
        if violations:
            recommendations.append(f"Fix {len(violations)} architecture violations before merging")
        
        if len(changes) > 5:
            recommendations.append("Consider breaking changes into smaller PRs")
            
        recommendations.extend([
            "Update architecture documentation",
            "Run integration tests across all layers",
            "Review with team before deployment"
        ])
        
        return recommendations
        
    def _refactor_type_to_title(self, refactor_type: str) -> str:
        """Convert refactor type to human-friendly title."""
        titles = {
            'extract_method': 'Method Extraction Refactor',
            'extract_class': 'Class Extraction Refactor',
            'inline_method': 'Method Inline Refactor',
            'move_method': 'Method Move Refactor',
            'rename': 'Rename Refactor'
        }
        return titles.get(refactor_type, f"Refactor: {refactor_type.replace('_', ' ').title()}")
        
    def _find_dependent_modules(
        self, 
        changed_files: List[str],
        arch: Dict[str, Any]
    ) -> List[str]:
        """Find modules that depend on changed files."""
        dependents = set()
        dependencies = arch.get('dependencies', [])
        
        for dep in dependencies:
            source = dep.get('from', '')
            target = dep.get('to', '')
            if any(changed in source for changed in changed_files):
                dependents.add(target)
                
        return sorted(list(dependents))
        
    def _calculate_risk_level(self, change_type: str, affected_count: int) -> str:
        """Calculate risk level of change."""
        if change_type == 'breaking_change':
            return f"🔴 HIGH RISK: Breaking change affecting {affected_count} modules"
        elif affected_count > 10:
            return f"🟡 MEDIUM RISK: Non-breaking change with wide impact ({affected_count} modules)"
        else:
            return f"🟢 LOW RISK: Localized change affecting {affected_count} modules"
