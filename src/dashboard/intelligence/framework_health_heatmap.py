"""
Phase 9.2: Framework Health Heatmap

Calculates multiple health factors for frameworks and generates heatmap data
for D3.js visualization. Health factors: version currency, EOL proximity, CVE severity.
"""

from typing import Dict, List, Any


class FrameworkHealthHeatmap:
    """
    Generates framework health heatmaps for visualization.
    
    Features:
    - Calculates 3 health factors (version currency, EOL proximity, CVE severity)
    - Normalizes scores to 0-100 scale
    - Flattens data into frameworks × factors matrix for D3.js
    - Generates color scale for visual encoding
    - Identifies critical frameworks requiring attention
    """
    
    def __init__(self):
        """Initialize heatmap generator."""
        self.factor_labels = {
            "version_currency": "Version Currency",
            "eol_proximity": "EOL Proximity",
            "cve_severity": "CVE Severity"
        }
    
    def calculate_version_currency(self, months_since_update: int) -> float:
        """
        Calculate version currency score based on update recency.
        
        Formula: 100 - (months_since_update / 24 × 100)
        - 0 months = 100 (just released)
        - 12 months = 50 (moderate)
        - 24+ months = 0 (very outdated)
        
        Args:
            months_since_update: Months since last version update
            
        Returns:
            Score from 0-100 (higher is better)
        """
        if months_since_update == 0:
            return 100.0
        
        # Linear decay: 0 months = 100, 24+ months = 0
        score = 100 - (months_since_update / 24.0 * 100)
        return max(0.0, min(100.0, score))
    
    def calculate_eol_proximity(self, months_to_eol: int = None) -> float:
        """
        Calculate EOL proximity score based on time to end-of-life.
        
        Formula: months_to_eol / 24 × 100
        - 24+ months = 100 (safe)
        - 12 months = 50 (moderate)
        - 0 months = 0 (critical)
        
        Args:
            months_to_eol: Months until end-of-life (None if no EOL)
            
        Returns:
            Score from 0-100 (higher is better)
        """
        if months_to_eol is None:
            return 50.0  # Neutral score when data unavailable
        
        # Linear scale: 0 months = 0, 24+ months = 100
        score = (months_to_eol / 24.0 * 100)
        return max(0.0, min(100.0, score))
    
    def calculate_cve_severity(self, cve_count: int) -> float:
        """
        Calculate CVE severity score based on vulnerability count.
        
        Formula: 100 - (cve_count / 10 × 100)
        - 0 CVEs = 100 (safe)
        - 5 CVEs = 50 (moderate)
        - 10+ CVEs = 0 (critical)
        
        Args:
            cve_count: Number of known CVEs
            
        Returns:
            Score from 0-100 (higher is better)
        """
        if cve_count < 0:
            cve_count = 0  # Treat negative as 0
        
        if cve_count == 0:
            return 100.0
        
        # Linear decay: 0 CVEs = 100, 10+ CVEs = 0
        score = 100 - (cve_count / 10.0 * 100)
        return max(0.0, min(100.0, score))
    
    def calculate_health(self, framework: Dict[str, Any]) -> Dict[str, float]:
        """
        Calculate all health factors for a framework.
        
        Args:
            framework: Framework dictionary with health data
            
        Returns:
            Dictionary with health factor scores
        """
        months_since_update = framework.get("months_since_update", 12)
        months_to_eol = framework.get("months_to_eol")
        cve_count = framework.get("cve_count", 0)
        
        return {
            "version_currency": self.calculate_version_currency(months_since_update),
            "eol_proximity": self.calculate_eol_proximity(months_to_eol),
            "cve_severity": self.calculate_cve_severity(cve_count)
        }
    
    def normalize_scores(self, scores: List[float]) -> List[float]:
        """
        Normalize scores to 0-100 range.
        
        Args:
            scores: List of scores to normalize
            
        Returns:
            List of normalized scores
        """
        return [max(0.0, min(100.0, score)) for score in scores]
    
    def flatten_to_heatmap(
        self,
        frameworks: List[Dict[str, Any]],
        health_data: Dict[str, Dict[str, float]]
    ) -> List[Dict[str, Any]]:
        """
        Flatten framework health data into 2D heatmap format.
        
        Format: frameworks × factors = rows for D3.js
        
        Args:
            frameworks: List of framework dictionaries
            health_data: Dictionary mapping framework keys to health scores
            
        Returns:
            List of heatmap rows (framework, factor, score)
        """
        heatmap_data = []
        
        for framework in frameworks:
            # Skip if framework is a string
            if isinstance(framework, str):
                continue
                
            name = framework.get("name", "")
            version = framework.get("version", "")
            framework_key = f"{name} {version}".strip() if version else name
            
            health = health_data.get(framework_key, {})
            
            for factor_key, factor_label in self.factor_labels.items():
                score = health.get(factor_key, 50.0)
                
                heatmap_data.append({
                    "framework": framework_key,
                    "factor": factor_label,
                    "score": score
                })
        
        return heatmap_data
    
    def generate_color_scale(self) -> Dict[str, Any]:
        """
        Generate color scale for heatmap visualization.
        
        Returns:
            Dictionary with thresholds and colors
        """
        return {
            "thresholds": [0, 30, 60, 80, 100],
            "colors": [
                "#d73027",  # Critical (0-30): Red
                "#fc8d59",  # Warning (30-60): Orange
                "#fee08b",  # Moderate (60-80): Yellow
                "#91cf60",  # Healthy (80-100): Light green
                "#1a9850"   # Excellent (100): Dark green
            ]
        }
    
    def generate(self, tech_stack: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """
        Generate complete framework health heatmap.
        
        Args:
            tech_stack: Dictionary with technology categories
            
        Returns:
            Heatmap dictionary with data, color_scale, and summary
        """
        # Collect all frameworks
        all_frameworks = []
        for category, technologies in tech_stack.items():
            all_frameworks.extend(technologies)
        
        if not all_frameworks:
            return {
                "data": [],
                "color_scale": self.generate_color_scale(),
                "summary": {
                    "total_frameworks": 0,
                    "average_health_score": 0,
                    "critical_frameworks": 0
                }
            }
        
        # Calculate health for each framework
        health_data = {}
        total_score = 0
        critical_count = 0
        
        for framework in all_frameworks:
            # Skip if framework is a string
            if isinstance(framework, str):
                continue
                
            name = framework.get("name", "")
            version = framework.get("version", "")
            framework_key = f"{name} {version}".strip() if version else name
            
            health = self.calculate_health(framework)
            health_data[framework_key] = health
            
            # Calculate average health score for this framework
            avg_score = sum(health.values()) / len(health)
            total_score += avg_score
            
            # Count critical frameworks (avg score < 40)
            if avg_score < 40:
                critical_count += 1
        
        # Flatten to heatmap format
        heatmap_data = self.flatten_to_heatmap(all_frameworks, health_data)
        
        # Calculate summary statistics
        avg_health = total_score / len(all_frameworks) if all_frameworks else 0
        
        return {
            "data": heatmap_data,
            "color_scale": self.generate_color_scale(),
            "summary": {
                "total_frameworks": len(all_frameworks),
                "average_health_score": round(avg_health, 2),
                "critical_frameworks": critical_count
            }
        }
