# Phase 10: Narrative Intelligence

**🔗 Breadcrumb:** [← Back to Master Plan](cortex-3.9-master.md)

**Status:** ⏳ Pending  
**Phase ID:** 10  
**Estimated Time:** 3 hours (180 minutes)  
**Actual Start:** -  
**Actual End:** -  
**Actual Work Time:** -  
**Dependencies:** Phase 08 (AST Engine Wrapper) ⏳, Phase 09 (Enhanced Analyzers) ⏳  
**Blocks:** Phase 17 (Proactive Intelligence)

---

## 🎯 Phase Objective

Develop context-aware code explanation system that generates human-friendly narratives for architecture changes, code explanations, and impact analysis using AST insights.

**Success Criteria:**
- ✅ Context-aware code explanation generator
- ✅ Architecture change storytelling with impact narratives
- ✅ Change impact analysis with downstream effects
- ✅ Integration with AST Engine and analyzers
- ✅ Narrative templates for common scenarios
- ✅ 100% test coverage with passing tests

---

## 🏗️ Implementation Plan

### Task 1: Narrative Generator Core (1.5 hours)

**Create `src/operations/modules/intelligence/narrative_generator.py`:**

```python
"""
Narrative Intelligence - Context-aware code explanations and storytelling.

Transforms technical AST analysis into human-friendly narratives that
explain code architecture, changes, and impacts.
"""

from pathlib import Path
from typing import Dict, Any, List
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
        self.ast_engine = ast_engine
        self.analyzers = analyzers  # deduplication, architecture, code_smell
        
        # Narrative templates for common scenarios
        self.templates = {
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
            narrative_type: Type of narrative to generate
            context: Context data (file paths, changes, etc.)
            depth: Narrative depth level
            
        Returns:
            CodeNarrative with human-friendly explanation
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
        
        # Analyze architecture before/after
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
                *[f"  - {c['file']}: {c['type']}" for c in changes]
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
        original = context.get('original_file', '')
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
            f"**Original Complexity:** {self._calculate_complexity(original)}",
            f"**Duplicates Removed:** {len(duplicates['duplicate_groups'])}",
            f"**Code Smells Fixed:** {len(smells['smells'])}"
        ]
        
        if depth == "deep-dive":
            details.extend([
                "**New Structure:**",
                *[f"  - {file}" for file in new_structure]
            ])
            
        impact = (
            f"Reduces maintenance burden by eliminating {len(duplicates['duplicate_groups'])} "
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
        file_path = Path(context['file'])
        function = context.get('function', '')
        
        # Use AST for code structure analysis
        arch = self.ast_engine.analyze_architecture()
        
        summary = f"Explains the purpose and behavior of {function} in {file_path.name}"
        
        details = [
            f"**Function:** {function}",
            f"**Module:** {file_path.stem}",
            f"**Dependencies:** {len(arch['module_graph'])} modules"
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
        arch = self.ast_engine.analyze_architecture()
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
        
    def _find_dependent_modules(
        self, 
        changed_files: List[str],
        arch: Dict[str, Any]
    ) -> List[str]:
        """Find modules that depend on changed files."""
        dependents = set()
        
        for edge in arch['module_graph']:
            if any(changed in edge['from'] for changed in changed_files):
                dependents.add(edge['to'])
                
        return sorted(list(dependents))
        
    def _calculate_risk_level(self, change_type: str, affected_count: int) -> str:
        """Calculate risk level of change."""
        if change_type == 'breaking_change':
            return f"🔴 HIGH RISK: Breaking change affecting {affected_count} modules"
        elif affected_count > 10:
            return f"🟡 MEDIUM RISK: Non-breaking change with wide impact ({affected_count} modules)"
        else:
            return f"🟢 LOW RISK: Localized change affecting {affected_count} modules"
```

### Task 2: Narrative Templates (1 hour)

**Template Library:**

```python
# Standard narrative templates for common scenarios

TEMPLATES = {
    'new_feature': """
    ## New Feature: {feature_name}
    
    **Overview:** {summary}
    
    **Implementation Approach:**
    {approach_details}
    
    **Integration Points:**
    {integration_points}
    
    **Testing Strategy:**
    {testing_approach}
    """,
    
    'bug_fix': """
    ## Bug Fix: {bug_description}
    
    **Root Cause:** {root_cause}
    
    **Solution:** {solution_description}
    
    **Affected Components:** {affected_components}
    
    **Validation:** {validation_steps}
    """,
    
    'performance_optimization': """
    ## Performance Optimization: {optimization_target}
    
    **Baseline Performance:** {baseline_metrics}
    
    **Optimization Strategy:** {strategy}
    
    **Expected Improvement:** {improvement_estimate}
    
    **Trade-offs:** {tradeoffs}
    """
}
```

### Task 3: Integration with Orchestrators (30 min)

**Usage in Planning Orchestrator:**

```python
# In planning_orchestrator.py

def generate_plan_narrative(self, request: str, plan_data: Dict[str, Any]):
    """Generate human-friendly plan explanation."""
    narrative_gen = NarrativeGenerator(self.ast_engine, self.analyzers)
    
    narrative = narrative_gen.generate_narrative(
        narrative_type='architecture_change',
        context=plan_data,
        depth='detailed'
    )
    
    return narrative
```

---

## 📦 Expected Deliverables

### Code Deliverables
- ✅ `src/operations/modules/intelligence/narrative_generator.py`
- ✅ Narrative template library
- ✅ Integration with orchestrators
- ✅ Markdown formatting utilities

### Test Deliverables
- ✅ `tests/test_narrative_generator.py`
- ✅ Template rendering tests
- ✅ Context analysis tests
- ✅ Integration tests with real scenarios

### Documentation Deliverables
- ✅ Narrative generation guide
- ✅ Template customization guide
- ✅ Usage examples for each narrative type
- ✅ Best practices for narrative depth selection

---

## 🔄 Next Steps

1. **Phase 08-09 Completion:** AST Engine and analyzers must be operational
2. **Template Library:** Expand templates for additional scenarios
3. **User Feedback:** Collect feedback on narrative quality and usefulness
4. **Integration:** Connect to Phase 17 (Proactive Intelligence)

---

## 🔗 Integration Points

### Upstream Dependencies
- **AST Engine (Phase 08):** Architecture and dependency analysis
- **Enhanced Analyzers (Phase 09):** Code quality insights

### Downstream Consumers
- **Proactive Intelligence (Phase 17):** Uses narratives for recommendations
- **Planning Orchestrator (Phase 03):** Plan explanation generation
- **Documentation (Phase 18):** Automatic documentation narratives

---

## 🚨 Risk Mitigation

### Risk 1: Narrative Quality Variability
**Mitigation:**
- Standard templates for common scenarios
- User feedback loop for template refinement
- Depth levels for different use cases

### Risk 2: Performance Overhead
**Mitigation:**
- Generate narratives asynchronously
- Cache narrative components (5-minute TTL)
- Limit depth for interactive workflows

---

## 📊 Success Metrics

- ✅ Narratives generated in <500ms for detailed depth
- ✅ User satisfaction ≥4.0/5.0 (survey after 100 narratives)
- ✅ 100% of common scenarios covered by templates
- ✅ Narrative accuracy ≥95% (matches manual explanations)
- ✅ Integration with all major orchestrators

---

**Phase Owner:** Asif Hussain  
**Phase Status:** ⏳ Awaiting Phase 08-09 completion  
**Last Updated:** 2024-12-14
