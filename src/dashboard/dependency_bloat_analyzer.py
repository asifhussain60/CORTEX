"""
Dependency Bloat Analyzer

Analyzes package count distribution across solutions to identify bloated projects.
Provides statistical analysis (histogram, box plot, quartiles) and bloat scoring.

Author: Asif Hussain
Date: December 6, 2025
"""

import json
import statistics
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Any, Tuple, Optional


@dataclass
class SolutionPackageStats:
    """Statistics for a single solution's package usage."""
    solution_name: str
    package_count: int
    bloat_score: float
    is_outlier: bool
    category: str  # 'critical', 'warning', 'normal'


@dataclass
class BloatAnalysis:
    """Complete bloat analysis results."""
    solutions: List[SolutionPackageStats]
    mean: float
    median: float
    q1: float
    q3: float
    iqr: float
    outlier_threshold: float
    histogram_bins: List[Dict[str, Any]]
    box_plot_data: Dict[str, Any]
    recommendations: List[str]


class DependencyBloatAnalyzer:
    """Analyzes dependency bloat across solutions."""
    
    # Histogram bin ranges (package counts)
    HISTOGRAM_BINS = [
        (0, 50, "0-50"),
        (51, 100, "51-100"),
        (101, 150, "101-150"),
        (151, 200, "151-200"),
        (201, float('inf'), "200+")
    ]
    
    # Bloat score thresholds
    BLOAT_CRITICAL = 2.0  # >2 standard deviations above mean
    BLOAT_WARNING = 1.0   # 1-2 standard deviations above mean
    
    def __init__(self, tech_stack_path: Optional[str] = None):
        """
        Initialize analyzer.
        
        Args:
            tech_stack_path: Path to tech-stack.json file
        """
        self.tech_stack_path = tech_stack_path
        self.data: Optional[Dict[str, Any]] = None
    
    def load_data(self, path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load tech stack data from JSON file.
        
        Args:
            path: Optional path override
            
        Returns:
            Parsed JSON data
            
        Raises:
            FileNotFoundError: If file doesn't exist
            json.JSONDecodeError: If invalid JSON
        """
        file_path = path or self.tech_stack_path
        if not file_path:
            raise ValueError("No tech stack path provided")
        
        path_obj = Path(file_path)
        if not path_obj.exists():
            raise FileNotFoundError(f"Tech stack file not found: {file_path}")
        
        with open(path_obj, 'r', encoding='utf-8') as f:
            self.data = json.load(f)
        
        return self.data
    
    def extract_package_counts(self, data: Optional[Dict[str, Any]] = None) -> List[Tuple[str, int]]:
        """
        Extract package counts for each solution.
        
        Args:
            data: Optional data override
            
        Returns:
            List of (solution_name, package_count) tuples
        """
        if data is None:
            data = self.data
        
        if not data:
            return []
        
        solutions = data.get('solutions', [])
        counts = []
        
        for solution in solutions:
            name = solution.get('name', 'Unknown')
            packages = solution.get('packages', [])
            counts.append((name, len(packages)))
        
        return counts
    
    def calculate_statistics(self, counts: List[int]) -> Dict[str, float]:
        """
        Calculate statistical measures.
        
        Args:
            counts: List of package counts
            
        Returns:
            Dictionary with mean, median, Q1, Q3, IQR, outlier_threshold
        """
        if not counts:
            return {
                'mean': 0.0,
                'median': 0.0,
                'q1': 0.0,
                'q3': 0.0,
                'iqr': 0.0,
                'outlier_threshold': 0.0
            }
        
        sorted_counts = sorted(counts)
        n = len(sorted_counts)
        
        mean = statistics.mean(sorted_counts)
        median = statistics.median(sorted_counts)
        
        # Calculate quartiles
        q1 = statistics.median(sorted_counts[:n//2])
        if n % 2 == 0:
            q3 = statistics.median(sorted_counts[n//2:])
        else:
            q3 = statistics.median(sorted_counts[n//2 + 1:])
        
        iqr = q3 - q1
        outlier_threshold = q3 + (1.5 * iqr)
        
        return {
            'mean': mean,
            'median': median,
            'q1': q1,
            'q3': q3,
            'iqr': iqr,
            'outlier_threshold': outlier_threshold
        }
    
    def calculate_bloat_score(self, package_count: int, mean: float, std_dev: float) -> float:
        """
        Calculate bloat score (z-score).
        
        Formula: (package_count - mean) / std_dev
        
        Args:
            package_count: Number of packages
            mean: Mean package count
            std_dev: Standard deviation
            
        Returns:
            Bloat score (0 = mean, positive = above mean, negative = below mean)
        """
        if std_dev == 0:
            return 0.0
        
        return (package_count - mean) / std_dev
    
    def detect_outliers(self, counts: List[int], threshold: float) -> List[bool]:
        """
        Detect outliers using IQR method.
        
        Args:
            counts: List of package counts
            threshold: Outlier threshold (typically Q3 + 1.5*IQR)
            
        Returns:
            List of boolean flags (True = outlier)
        """
        return [count > threshold for count in counts]
    
    def categorize_bloat(self, bloat_score: float) -> str:
        """
        Categorize bloat level.
        
        Args:
            bloat_score: Calculated bloat score
            
        Returns:
            Category: 'critical', 'warning', or 'normal'
        """
        if bloat_score >= self.BLOAT_CRITICAL:
            return 'critical'
        elif bloat_score >= self.BLOAT_WARNING:
            return 'warning'
        else:
            return 'normal'
    
    def create_histogram_bins(self, counts: List[Tuple[str, int]]) -> List[Dict[str, Any]]:
        """
        Create histogram bins with solution counts.
        
        Args:
            counts: List of (solution_name, package_count) tuples
            
        Returns:
            List of bin dictionaries with range, label, count, solutions
        """
        bins = []
        
        for min_val, max_val, label in self.HISTOGRAM_BINS:
            solutions_in_bin = [
                name for name, count in counts
                if min_val <= count <= max_val or (max_val == float('inf') and count >= min_val)
            ]
            
            bins.append({
                'range': [min_val, max_val if max_val != float('inf') else 1000],
                'label': label,
                'count': len(solutions_in_bin),
                'solutions': solutions_in_bin
            })
        
        return bins
    
    def create_box_plot_data(self, stats: Dict[str, float], outlier_solutions: List[str]) -> Dict[str, Any]:
        """
        Create box plot data structure.
        
        Args:
            stats: Statistical measures
            outlier_solutions: List of outlier solution names
            
        Returns:
            Box plot data dictionary
        """
        return {
            'median': stats['median'],
            'q1': stats['q1'],
            'q3': stats['q3'],
            'whisker_low': stats['q1'] - (1.5 * stats['iqr']),
            'whisker_high': stats['outlier_threshold'],
            'outliers': outlier_solutions
        }
    
    def generate_recommendations(self, analysis: BloatAnalysis) -> List[str]:
        """
        Generate recommendations based on bloat analysis.
        
        Args:
            analysis: Complete bloat analysis
            
        Returns:
            List of recommendation strings
        """
        recommendations = []
        
        # Count critical and warning solutions
        critical_count = sum(1 for s in analysis.solutions if s.category == 'critical')
        warning_count = sum(1 for s in analysis.solutions if s.category == 'warning')
        outlier_count = sum(1 for s in analysis.solutions if s.is_outlier)
        
        # Overall assessment
        if critical_count > 0:
            recommendations.append(
                f"⚠️ {critical_count} solution(s) have critical dependency bloat (>2σ above mean). "
                "Immediate review recommended."
            )
        
        if warning_count > 0:
            recommendations.append(
                f"📊 {warning_count} solution(s) have elevated package counts (1-2σ above mean). "
                "Consider consolidation opportunities."
            )
        
        if outlier_count > 0:
            recommendations.append(
                f"🔍 {outlier_count} outlier(s) detected using IQR method. "
                "These solutions may benefit from dependency audits."
            )
        
        # Specific recommendations
        if analysis.mean > 100:
            recommendations.append(
                "💡 High overall package usage detected (mean >100). "
                "Consider establishing package governance policies."
            )
        
        if analysis.iqr > 50:
            recommendations.append(
                "📈 Wide variation in package usage (IQR >50). "
                "Standardize dependency management across solutions."
            )
        
        # Build time impact
        if critical_count > 0 or outlier_count > 0:
            recommendations.append(
                "⏱️ High package counts impact build times and maintenance. "
                "Review for unused dependencies and consolidation opportunities."
            )
        
        # No issues found
        if not recommendations:
            recommendations.append(
                "✅ Dependency usage is well-distributed. No significant bloat detected."
            )
        
        return recommendations
    
    def analyze(self, data: Optional[Dict[str, Any]] = None) -> BloatAnalysis:
        """
        Perform complete bloat analysis.
        
        Args:
            data: Optional data override
            
        Returns:
            Complete BloatAnalysis object
        """
        if data is None:
            if self.data is None:
                self.load_data()
            data = self.data
        
        # Extract package counts
        counts_with_names = self.extract_package_counts(data)
        counts = [count for _, count in counts_with_names]
        
        if not counts:
            # Return empty analysis
            return BloatAnalysis(
                solutions=[],
                mean=0.0,
                median=0.0,
                q1=0.0,
                q3=0.0,
                iqr=0.0,
                outlier_threshold=0.0,
                histogram_bins=[],
                box_plot_data={},
                recommendations=["No data available for analysis."]
            )
        
        # Calculate statistics
        stats = self.calculate_statistics(counts)
        
        # Calculate standard deviation for bloat scores
        std_dev = statistics.stdev(counts) if len(counts) > 1 else 0.0
        
        # Detect outliers
        outlier_flags = self.detect_outliers(counts, stats['outlier_threshold'])
        
        # Create solution stats
        solution_stats = []
        for (name, count), is_outlier in zip(counts_with_names, outlier_flags):
            bloat_score = self.calculate_bloat_score(count, stats['mean'], std_dev)
            category = self.categorize_bloat(bloat_score)
            
            solution_stats.append(SolutionPackageStats(
                solution_name=name,
                package_count=count,
                bloat_score=bloat_score,
                is_outlier=is_outlier,
                category=category
            ))
        
        # Sort by bloat score (highest first)
        solution_stats.sort(key=lambda x: x.bloat_score, reverse=True)
        
        # Create histogram bins
        histogram_bins = self.create_histogram_bins(counts_with_names)
        
        # Create box plot data
        outlier_solutions = [s.solution_name for s in solution_stats if s.is_outlier]
        box_plot_data = self.create_box_plot_data(stats, outlier_solutions)
        
        # Create analysis object
        analysis = BloatAnalysis(
            solutions=solution_stats,
            mean=stats['mean'],
            median=stats['median'],
            q1=stats['q1'],
            q3=stats['q3'],
            iqr=stats['iqr'],
            outlier_threshold=stats['outlier_threshold'],
            histogram_bins=histogram_bins,
            box_plot_data=box_plot_data,
            recommendations=[]
        )
        
        # Generate recommendations
        analysis.recommendations = self.generate_recommendations(analysis)
        
        return analysis
    
    def export_to_json(self, analysis: BloatAnalysis, output_path: str) -> None:
        """
        Export analysis to JSON file.
        
        Args:
            analysis: BloatAnalysis object
            output_path: Output file path
        """
        output = {
            'statistics': {
                'mean': analysis.mean,
                'median': analysis.median,
                'q1': analysis.q1,
                'q3': analysis.q3,
                'iqr': analysis.iqr,
                'outlier_threshold': analysis.outlier_threshold
            },
            'solutions': [
                {
                    'name': s.solution_name,
                    'package_count': s.package_count,
                    'bloat_score': round(s.bloat_score, 2),
                    'is_outlier': s.is_outlier,
                    'category': s.category
                }
                for s in analysis.solutions
            ],
            'histogram_bins': analysis.histogram_bins,
            'box_plot': analysis.box_plot_data,
            'recommendations': analysis.recommendations
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2)


# CLI usage
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python dependency_bloat_analyzer.py <tech-stack.json> [output.json]")
        sys.exit(1)
    
    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    analyzer = DependencyBloatAnalyzer(input_path)
    analyzer.load_data()
    analysis = analyzer.analyze()
    
    print(f"\n=== Dependency Bloat Analysis ===")
    print(f"Mean: {analysis.mean:.1f} packages")
    print(f"Median: {analysis.median:.1f} packages")
    print(f"Q1: {analysis.q1:.1f}, Q3: {analysis.q3:.1f}, IQR: {analysis.iqr:.1f}")
    print(f"Outlier threshold: {analysis.outlier_threshold:.1f}")
    
    print(f"\n=== Solutions by Bloat Score ===")
    for solution in analysis.solutions[:10]:  # Top 10
        print(f"{solution.solution_name}: {solution.package_count} packages "
              f"(score: {solution.bloat_score:.2f}, {solution.category})")
    
    print(f"\n=== Recommendations ===")
    for rec in analysis.recommendations:
        print(f"• {rec}")
    
    if output_path:
        analyzer.export_to_json(analysis, output_path)
        print(f"\nAnalysis exported to {output_path}")
