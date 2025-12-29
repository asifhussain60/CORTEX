"""
TDD Workflow Integrator - Issue #3 Fix (P0)
Purpose: Integrate ViewDiscoveryAgent into TDD workflow before test generation
Created: 2025-11-23
Author: Asif Hussain

This module updates the TDD workflow to include view discovery phase:
OLD: User Request → Generate Tests (with assumptions) → Tests Fail
NEW: User Request → Discover Views → Generate Tests (with facts) → Tests Pass
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import json

from agents.view_discovery_agent import ViewDiscoveryAgent, discover_views_for_testing


class TDDWorkflowIntegrator:
    """
    Integrates view discovery into TDD workflow.
    
    Workflow Steps:
    1. User requests TDD test for feature
    2. DISCOVERY PHASE (NEW): Crawl target views, extract element IDs
    3. TEST GENERATION PHASE: Generate tests using discovered selectors
    4. VALIDATION PHASE: Cross-reference selectors with discovered data
    """
    
    def __init__(self, project_root: Path, brain_path: Path = None):
        """
        Initialize TDD workflow integrator.
        
        Args:
            project_root: Root directory of the project being tested
            brain_path: Path to CORTEX brain (for element mapping storage)
        """
        self.project_root = project_root
        self.brain_path = brain_path or Path(__file__).parent.parent.parent / "cortex-brain"
        self.discovery_agent = ViewDiscoveryAgent(project_root=project_root)
        
    def run_discovery_phase(
        self,
        target_views: List[Path],
        cache_results: bool = True
    ) -> Dict[str, Any]:
        """
        Run view discovery phase before test generation.
        
        Args:
            target_views: List of Razor/Blazor files to discover
            cache_results: Whether to cache results for future use
            
        Returns:
            Discovery results with element mappings and selector strategies
        """
        # Determine output path for caching
        output_path = None
        if cache_results:
            cache_dir = self.brain_path / "tier2" / "element-mappings-cache"
            cache_dir.mkdir(parents=True, exist_ok=True)
            output_path = cache_dir / f"discovery_{self.project_root.name}.json"
        
        # Run discovery
        results = self.discovery_agent.discover_views(
            view_paths=target_views,
            output_path=output_path
        )
        
        return results
    
    def get_selector_for_element(
        self,
        element_description: str,
        discovery_results: Dict[str, Any]
    ) -> Optional[str]:
        """
        Get recommended selector for an element based on description.
        
        Args:
            element_description: User description like "Generate Token button"
            discovery_results: Results from discovery phase
            
        Returns:
            Recommended selector string or None if not found
        """
        strategies = discovery_results.get("selector_strategies", {})
        
        # Try exact match
        if element_description in strategies:
            return strategies[element_description]
        
        # Try fuzzy match (case-insensitive, partial)
        description_lower = element_description.lower()
        for key, selector in strategies.items():
            if description_lower in key.lower() or key.lower() in description_lower:
                return selector
        
        return None
    
    def validate_test_selectors(
        self,
        test_selectors: List[str],
        discovery_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Validate that test selectors match discovered elements.
        
        Args:
            test_selectors: List of selectors used in test
            discovery_results: Results from discovery phase
            
        Returns:
            Validation report with matches, misses, and suggestions
        """
        discovered_selectors = [
            elem["selector_strategy"] 
            for elem in discovery_results.get("elements_discovered", [])
        ]
        
        validation = {
            "valid_selectors": [],
            "invalid_selectors": [],
            "suggestions": {}
        }
        
        for selector in test_selectors:
            if selector in discovered_selectors:
                validation["valid_selectors"].append(selector)
            else:
                validation["invalid_selectors"].append(selector)
                # Try to suggest alternative
                suggestion = self._find_similar_selector(selector, discovered_selectors)
                if suggestion:
                    validation["suggestions"][selector] = suggestion
        
        return validation
    
    def _find_similar_selector(
        self,
        selector: str,
        available_selectors: List[str]
    ) -> Optional[str]:
        """Find similar selector from available options."""
        # Simple similarity: check if selector type matches
        selector_type = selector[0] if selector else ""
        
        for available in available_selectors:
            if available.startswith(selector_type):
                return available
        
        return None
    
    def generate_discovery_report(
        self,
        discovery_results: Dict[str, Any],
        output_path: Optional[Path] = None
    ) -> str:
        """
        Generate human-readable discovery report.
        
        Args:
            discovery_results: Results from discovery phase
            output_path: Optional path to save markdown report
            
        Returns:
            Markdown formatted report
        """
        report = f"""# View Discovery Report

**Project:** {self.project_root.name}
**Discovery Date:** {discovery_results.get('discovery_timestamp', 'Unknown')}
**Files Processed:** {len(discovery_results.get('files_processed', []))}

---

## 📊 Summary

- **Total Elements Discovered:** {len(discovery_results.get('elements_discovered', []))}
- **Navigation Flows:** {len(discovery_results.get('navigation_flows', []))}
- **Components Without IDs:** {len(discovery_results.get('components_without_ids', []))}
- **Warnings:** {len(discovery_results.get('warnings', []))}

---

## 🎯 Selector Strategies

"""
        
        # Add selector strategies
        strategies = discovery_results.get('selector_strategies', {})
        if strategies:
            report += "| Element Description | Recommended Selector |\n"
            report += "|---------------------|---------------------|\n"
            for desc, selector in sorted(strategies.items())[:20]:  # Top 20
                report += f"| {desc} | `{selector}` |\n"
        else:
            report += "*No selector strategies generated*\n"
        
        report += "\n---\n\n## ⚠️ Components Without IDs\n\n"
        
        # Add components without IDs
        components_without_ids = discovery_results.get('components_without_ids', [])
        if components_without_ids:
            report += "These components should be updated with `id` or `data-testid` attributes:\n\n"
            for comp in components_without_ids[:10]:  # Top 10
                report += f"- **{comp.get('file')}:{comp.get('line')}** - "
                report += f"`<{comp.get('type')}>` \"{comp.get('text', 'N/A')}\"\n"
        else:
            report += "✅ All interactive components have IDs!\n"
        
        # Save to file if requested
        if output_path:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(report)
        
        return report


def integrate_discovery_with_tdd(
    project_root: Path,
    target_feature: str,
    target_views: List[Path]
) -> Dict[str, Any]:
    """
    Convenience function to run full TDD workflow with discovery.
    
    Args:
        project_root: Project root directory
        target_feature: Feature being tested (e.g., "share button injection")
        target_views: Views to discover elements from
        
    Returns:
        Complete workflow results with discovery and recommendations
    """
    integrator = TDDWorkflowIntegrator(project_root=project_root)
    
    # Phase 1: Discovery
    print(f"🔍 Phase 1: Discovering elements in {len(target_views)} views...")
    discovery_results = integrator.run_discovery_phase(
        target_views=target_views,
        cache_results=True
    )
    
    # Generate report
    print(f"📝 Generating discovery report...")
    report_path = project_root / "TestDiscovery" / f"{target_feature.replace(' ', '-')}-discovery.md"
    report = integrator.generate_discovery_report(
        discovery_results=discovery_results,
        output_path=report_path
    )
    
    print(f"✅ Discovery complete! Found {len(discovery_results['elements_discovered'])} elements.")
    print(f"📄 Report saved: {report_path}")
    
    return {
        "discovery_results": discovery_results,
        "report_path": str(report_path),
        "report_content": report,
        "ready_for_test_generation": True
    }
