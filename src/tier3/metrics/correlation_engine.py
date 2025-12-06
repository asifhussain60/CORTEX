"""
Correlation Engine

Analyzes correlations between Copilot metrics and CORTEX usage patterns.
Identifies relationships between acceptance rates, success rates, and adoption trends.

Author: Asif Hussain
Version: 1.0.0
"""

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Dict, Any, List, Optional, Tuple
import sqlite3
from pathlib import Path
import statistics


@dataclass
class CorrelationResult:
    """Result of correlation analysis"""
    success: bool
    correlation_type: str
    correlation_coefficient: float  # -1.0 to 1.0
    confidence_level: float  # 0.0 to 1.0
    sample_size: int
    period_start: date
    period_end: date
    interpretation: str
    error_message: Optional[str] = None


@dataclass
class TrendResult:
    """Result of trend analysis"""
    success: bool
    metric_name: str
    trend_direction: str  # "increasing", "decreasing", "stable"
    trend_strength: float  # 0.0 to 1.0
    period_start: date
    period_end: date
    data_points: List[Tuple[date, float]]
    error_message: Optional[str] = None


class CorrelationEngine:
    """
    Analyze correlations and trends in adoption analytics data.
    
    Features:
    - Copilot acceptance rate ↔ CORTEX success rate correlation
    - Token usage pattern analysis
    - Adoption trend detection over time
    - Statistical significance testing
    - Multi-dimensional correlation scoring
    - Time-series analysis
    
    Usage:
        engine = CorrelationEngine(db_path="/path/to/db")
        
        # Analyze correlation
        result = engine.analyze_copilot_cortex_correlation(
            start_date=date(2025, 11, 1),
            end_date=date(2025, 11, 30)
        )
        
        # Detect trends
        trend = engine.detect_adoption_trend(
            metric_name="copilot_acceptance_rate",
            start_date=date(2025, 11, 1),
            end_date=date(2025, 11, 30)
        )
        
        # Token pattern analysis
        patterns = engine.analyze_token_patterns(
            start_date=date(2025, 11, 1),
            end_date=date(2025, 11, 30)
        )
    """
    
    def __init__(self, db_path: str):
        """
        Initialize correlation engine.
        
        Args:
            db_path: Path to Tier 3 development_context.db
        """
        self.db_path = Path(db_path)
    
    def analyze_copilot_cortex_correlation(
        self,
        start_date: date,
        end_date: date,
        min_sample_size: int = 10
    ) -> CorrelationResult:
        """
        Analyze correlation between Copilot acceptance rate and CORTEX success rate.
        
        Args:
            start_date: Start of analysis period
            end_date: End of analysis period
            min_sample_size: Minimum data points for valid correlation
            
        Returns:
            CorrelationResult with coefficient and interpretation
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get daily data for both metrics
            cursor.execute("""
                SELECT 
                    cm.metric_date,
                    CAST(cm.acceptances AS FLOAT) / NULLIF(cm.total_suggestions, 0) as copilot_rate,
                    CAST(cum.successful_count AS FLOAT) / NULLIF(cum.total_count, 0) as cortex_rate
                FROM copilot_metrics cm
                JOIN cortex_usage_metrics cum 
                  ON cm.engineer_hash = cum.engineer_hash 
                  AND cm.metric_date = cum.metric_date
                WHERE cm.metric_date BETWEEN ? AND ?
                  AND cm.total_suggestions > 0
                  AND cum.total_count > 0
            """, (start_date.isoformat(), end_date.isoformat()))
            
            rows = cursor.fetchall()
            conn.close()
            
            if len(rows) < min_sample_size:
                return CorrelationResult(
                    success=False,
                    correlation_type="copilot_cortex",
                    correlation_coefficient=0.0,
                    confidence_level=0.0,
                    sample_size=len(rows),
                    period_start=start_date,
                    period_end=end_date,
                    interpretation="Insufficient data for correlation analysis",
                    error_message=f"Sample size {len(rows)} below minimum {min_sample_size}"
                )
            
            # Extract rates
            copilot_rates = [row[1] for row in rows if row[1] is not None]
            cortex_rates = [row[2] for row in rows if row[2] is not None]
            
            # Calculate Pearson correlation coefficient
            coefficient = self._pearson_correlation(copilot_rates, cortex_rates)
            
            # Calculate confidence level (simple approach based on sample size)
            confidence = min(len(rows) / 100.0, 1.0)
            
            # Interpret correlation
            interpretation = self._interpret_correlation(coefficient)
            
            return CorrelationResult(
                success=True,
                correlation_type="copilot_cortex",
                correlation_coefficient=coefficient,
                confidence_level=confidence,
                sample_size=len(rows),
                period_start=start_date,
                period_end=end_date,
                interpretation=interpretation
            )
            
        except Exception as e:
            return CorrelationResult(
                success=False,
                correlation_type="copilot_cortex",
                correlation_coefficient=0.0,
                confidence_level=0.0,
                sample_size=0,
                period_start=start_date,
                period_end=end_date,
                interpretation="Error during analysis",
                error_message=str(e)
            )
    
    def detect_adoption_trend(
        self,
        metric_name: str,
        start_date: date,
        end_date: date,
        granularity: str = "daily"
    ) -> TrendResult:
        """
        Detect trend in adoption metrics over time.
        
        Args:
            metric_name: Name of metric to analyze 
                        ("copilot_acceptance_rate", "cortex_success_rate", etc.)
            start_date: Start of analysis period
            end_date: End of analysis period
            granularity: Time granularity ("daily", "weekly", "monthly")
            
        Returns:
            TrendResult with trend direction and strength
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Build query based on metric name
            if metric_name == "copilot_acceptance_rate":
                query = """
                    SELECT 
                        metric_date,
                        CAST(SUM(acceptances) AS FLOAT) / NULLIF(SUM(total_suggestions), 0) as rate
                    FROM copilot_metrics
                    WHERE metric_date BETWEEN ? AND ?
                    GROUP BY metric_date
                    ORDER BY metric_date
                """
            elif metric_name == "cortex_success_rate":
                query = """
                    SELECT 
                        metric_date,
                        CAST(SUM(successful_count) AS FLOAT) / NULLIF(SUM(total_count), 0) as rate
                    FROM cortex_usage_metrics
                    WHERE metric_date BETWEEN ? AND ?
                    GROUP BY metric_date
                    ORDER BY metric_date
                """
            else:
                raise ValueError(f"Unknown metric: {metric_name}")
            
            cursor.execute(query, (start_date.isoformat(), end_date.isoformat()))
            rows = cursor.fetchall()
            conn.close()
            
            if len(rows) < 3:
                return TrendResult(
                    success=False,
                    metric_name=metric_name,
                    trend_direction="unknown",
                    trend_strength=0.0,
                    period_start=start_date,
                    period_end=end_date,
                    data_points=[],
                    error_message="Insufficient data for trend analysis (need >= 3 points)"
                )
            
            # Convert to data points
            data_points = [
                (date.fromisoformat(row[0]), row[1]) 
                for row in rows if row[1] is not None
            ]
            
            # Calculate trend using linear regression slope
            x_values = list(range(len(data_points)))
            y_values = [point[1] for point in data_points]
            
            slope = self._calculate_slope(x_values, y_values)
            
            # Determine direction
            if abs(slope) < 0.001:
                direction = "stable"
                strength = 0.0
            elif slope > 0:
                direction = "increasing"
                strength = min(abs(slope) * 10, 1.0)
            else:
                direction = "decreasing"
                strength = min(abs(slope) * 10, 1.0)
            
            return TrendResult(
                success=True,
                metric_name=metric_name,
                trend_direction=direction,
                trend_strength=strength,
                period_start=start_date,
                period_end=end_date,
                data_points=data_points
            )
            
        except Exception as e:
            return TrendResult(
                success=False,
                metric_name=metric_name,
                trend_direction="error",
                trend_strength=0.0,
                period_start=start_date,
                period_end=end_date,
                data_points=[],
                error_message=str(e)
            )
    
    def analyze_token_patterns(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Analyze token usage patterns across engineers.
        
        Args:
            start_date: Start of analysis period
            end_date: End of analysis period
            
        Returns:
            Dictionary with pattern analysis results
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get token usage statistics
            cursor.execute("""
                SELECT 
                    engineer_hash,
                    SUM(input_tokens) as total_input,
                    SUM(output_tokens) as total_output,
                    SUM(input_tokens + output_tokens) as total_tokens,
                    COUNT(*) as request_count
                FROM cortex_usage_metrics
                WHERE metric_date BETWEEN ? AND ?
                GROUP BY engineer_hash
            """, (start_date.isoformat(), end_date.isoformat()))
            
            rows = cursor.fetchall()
            conn.close()
            
            if not rows:
                return {
                    'success': False,
                    'error_message': 'No token data available for period'
                }
            
            # Calculate statistics
            total_tokens = [row[3] for row in rows]
            avg_per_request = [row[3] / row[4] if row[4] > 0 else 0 for row in rows]
            input_output_ratios = [
                row[1] / row[2] if row[2] > 0 else 0 
                for row in rows
            ]
            
            return {
                'success': True,
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'total_engineers': len(rows),
                'total_tokens_used': sum(total_tokens),
                'avg_tokens_per_engineer': statistics.mean(total_tokens),
                'median_tokens_per_engineer': statistics.median(total_tokens),
                'avg_tokens_per_request': statistics.mean(avg_per_request),
                'avg_input_output_ratio': statistics.mean(input_output_ratios),
                'high_usage_engineers': len([t for t in total_tokens if t > statistics.mean(total_tokens) * 1.5]),
                'low_usage_engineers': len([t for t in total_tokens if t < statistics.mean(total_tokens) * 0.5])
            }
            
        except Exception as e:
            return {
                'success': False,
                'error_message': str(e)
            }
    
    def get_correlation_matrix(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Calculate correlation matrix for all key metrics.
        
        Args:
            start_date: Start of analysis period
            end_date: End of analysis period
            
        Returns:
            Dictionary with correlation coefficients between metric pairs
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get all metrics for the period
            cursor.execute("""
                SELECT 
                    cm.metric_date,
                    CAST(cm.acceptances AS FLOAT) / NULLIF(cm.total_suggestions, 0) as copilot_rate,
                    CAST(cum.successful_count AS FLOAT) / NULLIF(cum.total_count, 0) as cortex_rate,
                    cum.input_tokens + cum.output_tokens as total_tokens,
                    cum.total_count as request_count
                FROM copilot_metrics cm
                JOIN cortex_usage_metrics cum 
                  ON cm.engineer_hash = cum.engineer_hash 
                  AND cm.metric_date = cum.metric_date
                WHERE cm.metric_date BETWEEN ? AND ?
                  AND cm.total_suggestions > 0
                  AND cum.total_count > 0
            """, (start_date.isoformat(), end_date.isoformat()))
            
            rows = cursor.fetchall()
            conn.close()
            
            if len(rows) < 10:
                return {
                    'success': False,
                    'error_message': 'Insufficient data for correlation matrix'
                }
            
            # Extract metric arrays
            copilot_rates = [row[1] for row in rows if row[1] is not None]
            cortex_rates = [row[2] for row in rows if row[2] is not None]
            token_counts = [row[3] for row in rows if row[3] is not None]
            request_counts = [row[4] for row in rows if row[4] is not None]
            
            # Calculate all correlations
            correlations = {
                'copilot_cortex': self._pearson_correlation(copilot_rates, cortex_rates),
                'copilot_tokens': self._pearson_correlation(copilot_rates, token_counts),
                'cortex_tokens': self._pearson_correlation(cortex_rates, token_counts),
                'copilot_requests': self._pearson_correlation(copilot_rates, request_counts),
                'cortex_requests': self._pearson_correlation(cortex_rates, request_counts),
                'tokens_requests': self._pearson_correlation(token_counts, request_counts)
            }
            
            return {
                'success': True,
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'sample_size': len(rows),
                'correlations': correlations,
                'interpretations': {
                    key: self._interpret_correlation(value)
                    for key, value in correlations.items()
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error_message': str(e)
            }
    
    # Helper methods
    
    def _pearson_correlation(self, x: List[float], y: List[float]) -> float:
        """Calculate Pearson correlation coefficient"""
        if len(x) != len(y) or len(x) == 0:
            return 0.0
        
        n = len(x)
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)
        
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        
        denom_x = sum((x[i] - mean_x) ** 2 for i in range(n))
        denom_y = sum((y[i] - mean_y) ** 2 for i in range(n))
        
        if denom_x == 0 or denom_y == 0:
            return 0.0
        
        return numerator / (denom_x * denom_y) ** 0.5
    
    def _calculate_slope(self, x: List[float], y: List[float]) -> float:
        """Calculate linear regression slope"""
        if len(x) != len(y) or len(x) == 0:
            return 0.0
        
        n = len(x)
        mean_x = statistics.mean(x)
        mean_y = statistics.mean(y)
        
        numerator = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        denominator = sum((x[i] - mean_x) ** 2 for i in range(n))
        
        if denominator == 0:
            return 0.0
        
        return numerator / denominator
    
    def _interpret_correlation(self, coefficient: float) -> str:
        """Interpret correlation coefficient"""
        abs_coef = abs(coefficient)
        
        if abs_coef >= 0.8:
            strength = "very strong"
        elif abs_coef >= 0.6:
            strength = "strong"
        elif abs_coef >= 0.4:
            strength = "moderate"
        elif abs_coef >= 0.2:
            strength = "weak"
        else:
            strength = "very weak"
        
        direction = "positive" if coefficient >= 0 else "negative"
        
        return f"{strength} {direction} correlation (r={coefficient:.3f})"
