"""
Test Manifest Manager for CORTEX Integration Tests.

Manages test_manifest.yaml - tracking discovered components, test coverage,
and integration test metadata.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from .component_discovery import Component, ComponentDiscoveryEngine


class TestManifest:
    """Manages test manifest tracking."""
    
    def __init__(self, project_root: str):
        """Initialize test manifest."""
        self.project_root = Path(project_root)
        self.manifest_path = self.project_root / "tests" / "test_manifest.yaml"
        self.data: Dict[str, Any] = {}
        
        if self.manifest_path.exists():
            self.load()
        else:
            self._initialize_empty()
    
    def _initialize_empty(self):
        """Initialize empty manifest structure."""
        self.data = {
            "version": "1.0",
            "last_discovery": None,
            "total_components": 0,
            "tested_components": 0,
            "untested_components": 0,
            "coverage_percentage": 0.0,
            "categories": {},
            "risk_analysis": {
                "high_risk_untested": 0,
                "critical_paths_uncovered": 0,
                "learning_gaps": 0
            }
        }
    
    def load(self):
        """Load manifest from file."""
        if not self.manifest_path.exists():
            return self.data
        
        with open(self.manifest_path, "r", encoding="utf-8") as f:
            loaded = yaml.safe_load(f)
            if loaded:
                self.data = loaded
        
        return self.data
    
    def save(self):
        """Save manifest to file."""
        self.manifest_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.manifest_path, "w", encoding="utf-8") as f:
            yaml.dump(self.data, f, default_flow_style=False, sort_keys=False)
    
    def update_from_discovery(self, discovery_engine: ComponentDiscoveryEngine):
        """Update manifest from discovery results."""
        components = discovery_engine.discovered_components
        coverage_stats = discovery_engine.calculate_coverage()
        
        # Update header
        self.data["last_discovery"] = datetime.now().isoformat()
        self.data["total_components"] = coverage_stats["total_components"]
        self.data["tested_components"] = coverage_stats["tested_components"]
        self.data["untested_components"] = coverage_stats["untested_components"]
        self.data["coverage_percentage"] = round(coverage_stats["coverage_percentage"], 1)
        
        # Update categories
        self.data["categories"] = {}
        
        for category, stats in coverage_stats["categories"].items():
            category_components = discovery_engine.get_components_by_category(category)
            
            component_list = []
            for comp in category_components:
                component_entry = {
                    "name": comp.name,
                    "path": comp.path,
                    "component_type": comp.component_type,
                    "integration_points": [
                        {
                            "component": ip.component,
                            "type": ip.type,
                            "file": ip.file,
                            "method": ip.method
                        }
                        for ip in comp.integration_points
                    ],
                    "test_file": comp.test_file,
                    "status": comp.test_status,
                    "last_modified": comp.last_modified,
                    "risk_score": comp.risk_score
                }
                component_list.append(component_entry)
            
            self.data["categories"][category] = {
                "discovered": stats["total"],
                "tested": stats["tested"],
                "untested": stats["untested"],
                "coverage": round(stats["coverage"], 1),
                "components": component_list
            }
        
        # Update risk analysis
        high_risk_untested = len([
            c for c in components 
            if c.test_status == "untested" and c.risk_score > 0.7
        ])
        
        learning_untested = len([
            c for c in components
            if c.category == "learning" and c.test_status == "untested"
        ])
        
        self.data["risk_analysis"] = {
            "high_risk_untested": high_risk_untested,
            "critical_paths_uncovered": 0,  # To be enhanced with Tier 2
            "learning_gaps": learning_untested
        }
    
    def update_component(self, component_name: str, test_file: str, test_status: str, risk_score: float = 0.0):
        """Update a component's test information."""
        for category_data in self.data.get("categories", {}).values():
            for component in category_data.get("components", []):
                if component.get("name") == component_name:
                    component["test_file"] = test_file
                    component["status"] = test_status
                    component["risk_score"] = risk_score
                    return
    
    def get_untested_components(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get untested components, optionally filtered by category."""
        untested = []
        
        categories = [category] if category else self.data.get("categories", {}).keys()
        
        for cat in categories:
            category_data = self.data.get("categories", {}).get(cat, {})
            components = category_data.get("components", [])
            
            untested.extend([
                c for c in components
                if c.get("status") == "untested"
            ])
        
        return untested
    
    def get_high_risk_untested(self) -> List[Dict[str, Any]]:
        """Get high-risk untested components."""
        high_risk = []
        
        for category_data in self.data.get("categories", {}).values():
            components = category_data.get("components", [])
            high_risk.extend([
                c for c in components
                if c.get("status") == "untested" and c.get("risk_score", 0) > 0.7
            ])
        
        # Sort by risk score descending
        high_risk.sort(key=lambda c: c.get("risk_score", 0), reverse=True)
        
        return high_risk
    
    def mark_component_tested(
        self, 
        component_name: str, 
        test_file: str, 
        coverage: Optional[float] = None
    ):
        """Mark a component as tested."""
        for category_data in self.data.get("categories", {}).values():
            for component in category_data.get("components", []):
                if component.get("name") == component_name:
                    component["status"] = "tested"
                    component["test_file"] = test_file
                    component["last_test_run"] = datetime.now().isoformat()
                    
                    if coverage is not None:
                        component["coverage"] = coverage
                    
                    break
        
        # Recalculate totals
        self._recalculate_totals()
    
    def _recalculate_totals(self):
        """Recalculate total tested/untested counts."""
        tested_count = 0
        untested_count = 0
        
        for category_data in self.data.get("categories", {}).values():
            for component in category_data.get("components", []):
                if component.get("status") == "tested":
                    tested_count += 1
                else:
                    untested_count += 1
        
        total = tested_count + untested_count
        
        self.data["tested_components"] = tested_count
        self.data["untested_components"] = untested_count
        self.data["total_components"] = total
        self.data["coverage_percentage"] = round(
            (tested_count / total * 100) if total > 0 else 0, 1
        )
    
    def get_category_summary(self) -> str:
        """Get formatted category summary."""
        lines = ["Test Coverage by Category:", ""]
        
        for category, data in self.data.get("categories", {}).items():
            total = data.get("discovered", 0)
            tested = data.get("tested", 0)
            coverage = data.get("coverage", 0)
            
            lines.append(
                f"  {category:20} | Total: {total:3} | Tested: {tested:3} | Coverage: {coverage:5.1f}%"
            )
        
        return "\n".join(lines)
    
    def get_summary(self) -> str:
        """Get formatted manifest summary."""
        lines = [
            "=" * 60,
            "CORTEX Integration Test Manifest Summary",
            "=" * 60,
            "",
            f"Total Components: {self.data.get('total_components', 0)}",
            f"Tested: {self.data.get('tested_components', 0)}",
            f"Untested: {self.data.get('untested_components', 0)}",
            f"Coverage: {self.data.get('coverage_percentage', 0):.1f}%",
            "",
            self.get_category_summary(),
            "",
            "Risk Analysis:",
            f"  High-risk untested: {self.data.get('risk_analysis', {}).get('high_risk_untested', 0)}",
            f"  Learning gaps: {self.data.get('risk_analysis', {}).get('learning_gaps', 0)}",
            "",
            f"Last Discovery: {self.data.get('last_discovery', 'Never')}",
            "=" * 60
        ]
        
        return "\n".join(lines)
