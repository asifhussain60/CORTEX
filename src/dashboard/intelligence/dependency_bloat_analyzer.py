"""
Phase 9.3: Dependency Bloat Analyzer

Analyzes dependency counts across projects using statistical methods to identify
projects with excessive dependencies (bloat).
"""

import math
from typing import Dict, List, Any


class DependencyBloatAnalyzer:
    """
    Analyzes dependency bloat using statistical methods.
    
    Features:
    - Statistical calculations (mean, median, standard deviation)
    - Bloat score calculation using z-score formula
    - Outlier detection with configurable threshold
    - Recommendations based on bloat severity
    - Histogram generation for distribution visualization
    """
    
    def __init__(self):
        """Initialize bloat analyzer."""
        pass
    
    def calculate_mean(self, values: List[float]) -> float:
        """
        Calculate arithmetic mean.
        
        Args:
            values: List of numeric values
            
        Returns:
            Mean value
        """
        if not values:
            return 0.0
        return sum(values) / len(values)
    
    def calculate_median(self, values: List[float]) -> float:
        """
        Calculate median value.
        
        Args:
            values: List of numeric values
            
        Returns:
            Median value
        """
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        n = len(sorted_values)
        
        if n % 2 == 0:
            # Even count: average of two middle values
            return (sorted_values[n // 2 - 1] + sorted_values[n // 2]) / 2.0
        else:
            # Odd count: middle value
            return float(sorted_values[n // 2])
    
    def calculate_stddev(self, values: List[float]) -> float:
        """
        Calculate population standard deviation.
        
        Args:
            values: List of numeric values
            
        Returns:
            Standard deviation
        """
        if not values or len(values) == 1:
            return 0.0
        
        mean = self.calculate_mean(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)
    
    def calculate_statistics(self, values: List[float]) -> Dict[str, float]:
        """
        Calculate all statistics together.
        
        Args:
            values: List of numeric values
            
        Returns:
            Dictionary with mean, median, and stddev
        """
        return {
            "mean": self.calculate_mean(values),
            "median": self.calculate_median(values),
            "stddev": self.calculate_stddev(values)
        }
    
    def calculate_bloat_score(
        self,
        package_count: int,
        mean: float,
        stddev: float
    ) -> float:
        """
        Calculate bloat score using z-score formula.
        
        Formula: (package_count - mean) / stddev
        - Score > 2.0: Significant bloat (>2 standard deviations above mean)
        - Score 1.0-2.0: Moderate bloat
        - Score -1.0 to 1.0: Normal
        - Score < -1.0: Minimal dependencies
        
        Args:
            package_count: Number of packages in project
            mean: Mean package count across all projects
            stddev: Standard deviation of package counts
            
        Returns:
            Bloat score (z-score)
        """
        if stddev == 0:
            return 0.0
        
        return (package_count - mean) / stddev
    
    def generate_recommendation(self, bloat_score: float) -> str:
        """
        Generate recommendation based on bloat score.
        
        Args:
            bloat_score: Bloat score (z-score)
            
        Returns:
            Recommendation string
        """
        if bloat_score > 2.5:
            return "Critical: Review dependencies immediately. Consider removing unused packages and consolidating similar functionality."
        elif bloat_score > 2.0:
            return "High: Review dependencies for optimization opportunities. Look for unused or redundant packages."
        elif bloat_score > 1.5:
            return "Moderate: Dependencies are above average. Consider periodic review to prevent further bloat."
        elif bloat_score > 1.0:
            return "Slightly elevated: Dependency count is acceptable but monitor for growth."
        else:
            return "Healthy: Dependency count is within acceptable range."
    
    def identify_outliers(
        self,
        projects: List[Dict[str, Any]],
        threshold: float = 1.0
    ) -> List[Dict[str, Any]]:
        """
        Identify projects with excessive dependencies.
        
        Args:
            projects: List of project dictionaries with package_count
            threshold: Bloat score threshold for outliers (default: 1.0)
            
        Returns:
            List of outlier projects with bloat scores
        """
        if not projects:
            return []
        
        # Extract package counts
        package_counts = [p.get("package_count", 0) for p in projects]
        
        # Calculate statistics
        mean = self.calculate_mean(package_counts)
        stddev = self.calculate_stddev(package_counts)
        
        # Identify outliers
        outliers = []
        for project in projects:
            package_count = project.get("package_count", 0)
            bloat_score = self.calculate_bloat_score(package_count, mean, stddev)
            
            if bloat_score > threshold:
                outliers.append({
                    **project,
                    "bloat_score": round(bloat_score, 2)
                })
        
        return outliers
    
    def generate_histogram(
        self,
        values: List[float],
        bins: int = 10
    ) -> Dict[str, List]:
        """
        Generate histogram for package count distribution.
        
        Args:
            values: List of package counts
            bins: Number of histogram bins
            
        Returns:
            Dictionary with bins and counts
        """
        if not values:
            return {"bins": [], "counts": []}
        
        min_val = min(values)
        max_val = max(values)
        
        if min_val == max_val:
            # All values the same
            return {
                "bins": [min_val],
                "counts": [len(values)]
            }
        
        # Calculate bin width
        bin_width = (max_val - min_val) / bins
        
        # Count values in each bin
        counts = [0] * bins
        for value in values:
            # Find which bin this value belongs to
            bin_idx = min(int((value - min_val) / bin_width), bins - 1)
            counts[bin_idx] += 1
        
        # Return bin start positions
        bin_positions = [min_val + i * bin_width for i in range(bins)]
        
        return {
            "bins": bin_positions,
            "counts": counts
        }
    
    def _count_packages(self, project: Dict[str, Any]) -> int:
        """
        Count total packages in project.
        
        Args:
            project: Project dictionary with dependencies
            
        Returns:
            Total package count
        """
        # Handle string projects (tech stack format inconsistency)
        if isinstance(project, str):
            return 0
            
        dependencies = project.get("dependencies", {})
        total = 0
        
        for category, packages in dependencies.items():
            if isinstance(packages, list):
                total += len(packages)
            elif isinstance(packages, dict):
                total += len(packages)
        
        return total
    
    def analyze(self, projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze dependency bloat across all projects.
        
        Args:
            projects: List of project dictionaries with dependencies
            
        Returns:
            Analysis dictionary with statistics, outliers, histogram, and summary
        """
        if not projects:
            return {
                "statistics": {"mean": 0, "median": 0, "stddev": 0},
                "outliers": [],
                "histogram": {"bins": [], "counts": []},
                "summary": {
                    "total_projects": 0,
                    "bloated_projects": 0,
                    "average_packages": 0
                }
            }
        
        # Count packages for each project
        projects_with_counts = []
        package_counts = []
        
        for project in projects:
            # Skip string entries (format inconsistency)
            if isinstance(project, str):
                continue
                
            package_count = self._count_packages(project)
            projects_with_counts.append({
                **project,
                "package_count": package_count
            })
            package_counts.append(package_count)
        
        # Calculate statistics
        statistics = self.calculate_statistics(package_counts)
        
        # Identify outliers
        outliers = self.identify_outliers(projects_with_counts, threshold=1.0)
        
        # Add recommendations to outliers
        for outlier in outliers:
            outlier["recommendation"] = self.generate_recommendation(
                outlier["bloat_score"]
            )
        
        # Generate histogram
        histogram = self.generate_histogram(package_counts, bins=10)
        
        # Build summary
        summary = {
            "total_projects": len(projects),
            "bloated_projects": len(outliers),
            "average_packages": round(statistics["mean"], 2)
        }
        
        return {
            "statistics": statistics,
            "outliers": outliers,
            "histogram": histogram,
            "summary": summary
        }
