"""
ROI Calculator

Calculates return on investment for adoption analytics.
Computes time savings, cost savings, and productivity improvements from Copilot and CORTEX usage.

Author: Asif Hussain
Version: 1.0.0
"""

from dataclasses import dataclass
from datetime import date
from typing import Dict, Any, Optional
import sqlite3
from pathlib import Path


@dataclass
class ROIConfig:
    """Configuration for ROI calculations"""
    engineer_hourly_cost: float = 50.0  # Average engineer hourly cost (USD)
    hours_per_day: float = 8.0  # Working hours per day
    copilot_time_saved_per_acceptance: float = 0.5  # Minutes saved per acceptance
    cortex_time_saved_per_success: float = 2.0  # Minutes saved per successful request
    productivity_multiplier: float = 1.2  # Quality improvement factor


@dataclass
class ROIResult:
    """Result of ROI calculation"""
    success: bool
    period_start: date
    period_end: date
    
    # Copilot metrics
    copilot_acceptances: int = 0
    copilot_time_saved_hours: float = 0.0
    copilot_cost_savings: float = 0.0
    
    # CORTEX metrics
    cortex_successful_requests: int = 0
    cortex_time_saved_hours: float = 0.0
    cortex_cost_savings: float = 0.0
    
    # Combined metrics
    total_time_saved_hours: float = 0.0
    total_cost_savings: float = 0.0
    productivity_improvement: float = 0.0
    
    # ROI percentage
    roi_percentage: float = 0.0
    
    error_message: Optional[str] = None


class ROICalculator:
    """
    Calculate return on investment for adoption analytics.
    
    Features:
    - Time savings calculation (Copilot acceptances + CORTEX successes)
    - Cost savings estimation (time * hourly rate)
    - Productivity improvement (quality multiplier)
    - Engineer-level and team-level ROI
    - Configurable rates and multipliers
    - Historical trend analysis
    
    Usage:
        config = ROIConfig(
            engineer_hourly_cost=60.0,
            copilot_time_saved_per_acceptance=0.5,
            cortex_time_saved_per_success=2.0
        )
        
        calculator = ROICalculator(
            db_path="/path/to/db",
            config=config
        )
        
        # Engineer ROI
        roi = calculator.calculate_engineer_roi(
            engineer_hash="abc123...",
            start_date=date(2025, 11, 1),
            end_date=date(2025, 11, 30)
        )
        
        # Team ROI
        team_roi = calculator.calculate_team_roi(
            team_id="platform-team",
            start_date=date(2025, 11, 1),
            end_date=date(2025, 11, 30)
        )
    """
    
    def __init__(self, db_path: str, config: Optional[ROIConfig] = None):
        """
        Initialize ROI calculator.
        
        Args:
            db_path: Path to Tier 3 development_context.db
            config: ROIConfig with calculation parameters (optional)
        """
        self.db_path = Path(db_path)
        self.config = config or ROIConfig()
    
    def calculate_engineer_roi(
        self,
        engineer_hash: str,
        start_date: date,
        end_date: date
    ) -> ROIResult:
        """
        Calculate ROI for single engineer over date range.
        
        Args:
            engineer_hash: Anonymized engineer identifier
            start_date: Start of period (inclusive)
            end_date: End of period (inclusive)
            
        Returns:
            ROIResult with calculated savings and improvements
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get Copilot metrics
            cursor.execute("""
                SELECT SUM(acceptances)
                FROM copilot_metrics
                WHERE engineer_hash = ?
                  AND metric_date BETWEEN ? AND ?
            """, (engineer_hash, start_date.isoformat(), end_date.isoformat()))
            
            copilot_acceptances = cursor.fetchone()[0] or 0
            
            # Calculate Copilot time savings
            copilot_time_saved_minutes = (
                copilot_acceptances * self.config.copilot_time_saved_per_acceptance
            )
            copilot_time_saved_hours = copilot_time_saved_minutes / 60.0
            copilot_cost_savings = (
                copilot_time_saved_hours * self.config.engineer_hourly_cost
            )
            
            # Get CORTEX metrics
            cursor.execute("""
                SELECT SUM(successful_count)
                FROM cortex_usage_metrics
                WHERE engineer_hash = ?
                  AND metric_date BETWEEN ? AND ?
            """, (engineer_hash, start_date.isoformat(), end_date.isoformat()))
            
            cortex_successful = cursor.fetchone()[0] or 0
            
            # Calculate CORTEX time savings
            cortex_time_saved_minutes = (
                cortex_successful * self.config.cortex_time_saved_per_success
            )
            cortex_time_saved_hours = cortex_time_saved_minutes / 60.0
            cortex_cost_savings = (
                cortex_time_saved_hours * self.config.engineer_hourly_cost
            )
            
            # Combined totals
            total_time_saved_hours = copilot_time_saved_hours + cortex_time_saved_hours
            total_cost_savings = copilot_cost_savings + cortex_cost_savings
            
            # Productivity improvement (time saved * quality multiplier)
            productivity_improvement = (
                total_cost_savings * self.config.productivity_multiplier
            )
            
            # Calculate ROI percentage
            # Assuming license cost is negligible or already amortized
            roi_percentage = (
                (productivity_improvement / self.config.engineer_hourly_cost) * 100
                if self.config.engineer_hourly_cost > 0
                else 0.0
            )
            
            conn.close()
            
            return ROIResult(
                success=True,
                period_start=start_date,
                period_end=end_date,
                copilot_acceptances=copilot_acceptances,
                copilot_time_saved_hours=copilot_time_saved_hours,
                copilot_cost_savings=copilot_cost_savings,
                cortex_successful_requests=cortex_successful,
                cortex_time_saved_hours=cortex_time_saved_hours,
                cortex_cost_savings=cortex_cost_savings,
                total_time_saved_hours=total_time_saved_hours,
                total_cost_savings=total_cost_savings,
                productivity_improvement=productivity_improvement,
                roi_percentage=roi_percentage
            )
            
        except Exception as e:
            return ROIResult(
                success=False,
                period_start=start_date,
                period_end=end_date,
                error_message=str(e)
            )
    
    def calculate_team_roi(
        self,
        team_id: str,
        start_date: date,
        end_date: date
    ) -> ROIResult:
        """
        Calculate ROI for team using aggregated data.
        
        Args:
            team_id: Team identifier
            start_date: Start of period (inclusive)
            end_date: End of period (inclusive)
            
        Returns:
            ROIResult with team-level savings
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get team aggregation data
            cursor.execute("""
                SELECT 
                    SUM(copilot_total_suggestions * copilot_acceptance_rate) as total_acceptances,
                    SUM(cortex_total_requests * cortex_success_rate) as total_successful,
                    AVG(team_size) as avg_team_size
                FROM team_aggregations
                WHERE team_id = ?
                  AND aggregation_date BETWEEN ? AND ?
            """, (team_id, start_date.isoformat(), end_date.isoformat()))
            
            row = cursor.fetchone()
            copilot_acceptances = int(row[0] or 0)
            cortex_successful = int(row[1] or 0)
            team_size = int(row[2] or 0)
            
            # Calculate time savings
            copilot_time_saved_minutes = (
                copilot_acceptances * self.config.copilot_time_saved_per_acceptance
            )
            copilot_time_saved_hours = copilot_time_saved_minutes / 60.0
            copilot_cost_savings = (
                copilot_time_saved_hours * self.config.engineer_hourly_cost
            )
            
            cortex_time_saved_minutes = (
                cortex_successful * self.config.cortex_time_saved_per_success
            )
            cortex_time_saved_hours = cortex_time_saved_minutes / 60.0
            cortex_cost_savings = (
                cortex_time_saved_hours * self.config.engineer_hourly_cost
            )
            
            # Combined totals
            total_time_saved_hours = copilot_time_saved_hours + cortex_time_saved_hours
            total_cost_savings = copilot_cost_savings + cortex_cost_savings
            
            # Productivity improvement
            productivity_improvement = (
                total_cost_savings * self.config.productivity_multiplier
            )
            
            # ROI percentage
            total_cost = team_size * self.config.engineer_hourly_cost * self.config.hours_per_day
            roi_percentage = (
                (productivity_improvement / total_cost) * 100
                if total_cost > 0
                else 0.0
            )
            
            conn.close()
            
            return ROIResult(
                success=True,
                period_start=start_date,
                period_end=end_date,
                copilot_acceptances=copilot_acceptances,
                copilot_time_saved_hours=copilot_time_saved_hours,
                copilot_cost_savings=copilot_cost_savings,
                cortex_successful_requests=cortex_successful,
                cortex_time_saved_hours=cortex_time_saved_hours,
                cortex_cost_savings=cortex_cost_savings,
                total_time_saved_hours=total_time_saved_hours,
                total_cost_savings=total_cost_savings,
                productivity_improvement=productivity_improvement,
                roi_percentage=roi_percentage
            )
            
        except Exception as e:
            return ROIResult(
                success=False,
                period_start=start_date,
                period_end=end_date,
                error_message=str(e)
            )
    
    def get_roi_summary(
        self,
        start_date: date,
        end_date: date
    ) -> Dict[str, Any]:
        """
        Get organization-wide ROI summary.
        
        Args:
            start_date: Start of period (inclusive)
            end_date: End of period (inclusive)
            
        Returns:
            Dictionary with aggregated ROI metrics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Organization totals
            cursor.execute("""
                SELECT 
                    COUNT(DISTINCT engineer_hash) as total_engineers,
                    SUM(acceptances) as total_acceptances
                FROM copilot_metrics
                WHERE metric_date BETWEEN ? AND ?
            """, (start_date.isoformat(), end_date.isoformat()))
            
            cop_row = cursor.fetchone()
            total_engineers = cop_row[0] or 0
            total_copilot_acceptances = cop_row[1] or 0
            
            cursor.execute("""
                SELECT SUM(successful_count) as total_successful
                FROM cortex_usage_metrics
                WHERE metric_date BETWEEN ? AND ?
            """, (start_date.isoformat(), end_date.isoformat()))
            
            total_cortex_successful = cursor.fetchone()[0] or 0
            
            conn.close()
            
            # Calculate org-wide savings
            copilot_time_saved_hours = (
                total_copilot_acceptances * self.config.copilot_time_saved_per_acceptance / 60.0
            )
            cortex_time_saved_hours = (
                total_cortex_successful * self.config.cortex_time_saved_per_success / 60.0
            )
            total_time_saved_hours = copilot_time_saved_hours + cortex_time_saved_hours
            
            total_cost_savings = total_time_saved_hours * self.config.engineer_hourly_cost
            productivity_improvement = total_cost_savings * self.config.productivity_multiplier
            
            return {
                'success': True,
                'period_start': start_date.isoformat(),
                'period_end': end_date.isoformat(),
                'total_engineers': total_engineers,
                'total_time_saved_hours': round(total_time_saved_hours, 2),
                'total_cost_savings': round(total_cost_savings, 2),
                'productivity_improvement': round(productivity_improvement, 2),
                'avg_time_saved_per_engineer': round(
                    total_time_saved_hours / total_engineers, 2
                ) if total_engineers > 0 else 0.0,
                'avg_cost_savings_per_engineer': round(
                    total_cost_savings / total_engineers, 2
                ) if total_engineers > 0 else 0.0
            }
            
        except Exception as e:
            return {
                'success': False,
                'error_message': str(e)
            }
