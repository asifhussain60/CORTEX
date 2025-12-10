"""
Analytics Collector for Observability Orchestrator

Adoption analytics and usage metrics collection.

Features:
- Operation tracking
- Success/failure rates
- Execution time analysis
- Top command tracking
- Team usage patterns

Author: Asif Hussain
Date: December 10, 2025
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
from collections import Counter
import logging

logger = logging.getLogger(__name__)


@dataclass
class OperationRecord:
    """Record of a single operation."""
    operation_id: str
    operation_name: str
    tenant_id: str
    team_id: str
    user_id: str
    started_at: datetime
    completed_at: datetime
    success: bool
    execution_time_seconds: float


class AnalyticsCollector:
    """
    Collects adoption analytics and usage metrics.
    
    Metrics:
    - Total operations
    - Success/failure rates
    - Average execution times
    - Top commands
    - Team usage patterns
    - User activity
    """
    
    def __init__(self):
        """Initialize analytics collector."""
        self.operations: List[OperationRecord] = []
    
    def collect(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        tenant_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Collect analytics for specified time period.
        
        Args:
            start_date: Start of analytics period (default: 30 days ago)
            end_date: End of analytics period (default: now)
            tenant_id: Filter by tenant (default: all tenants)
            
        Returns:
            Analytics data with metrics
        """
        # Default to last 30 days
        if not end_date:
            end_date = datetime.now()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        # Filter operations
        filtered_ops = self._filter_operations(start_date, end_date, tenant_id)
        
        # Calculate metrics
        metrics = self._calculate_metrics(filtered_ops)
        
        return {
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            },
            "tenant_id": tenant_id or "all",
            "metrics": metrics,
            "collected_at": datetime.now().isoformat()
        }
    
    def _filter_operations(
        self,
        start_date: datetime,
        end_date: datetime,
        tenant_id: Optional[str]
    ) -> List[OperationRecord]:
        """Filter operations by date range and tenant."""
        filtered = [
            op for op in self.operations
            if start_date <= op.started_at <= end_date
        ]
        
        if tenant_id:
            filtered = [op for op in filtered if op.tenant_id == tenant_id]
        
        return filtered
    
    def _calculate_metrics(self, operations: List[OperationRecord]) -> Dict[str, Any]:
        """Calculate analytics metrics from operations."""
        if not operations:
            return {
                "total_operations": 0,
                "successful_operations": 0,
                "failed_operations": 0,
                "success_rate": 0.0,
                "avg_execution_time_seconds": 0.0,
                "top_commands": {},
                "team_usage": {}
            }
        
        # Basic counts
        total = len(operations)
        successful = sum(1 for op in operations if op.success)
        failed = total - successful
        
        # Success rate
        success_rate = (successful / total) * 100 if total > 0 else 0.0
        
        # Average execution time
        avg_exec_time = sum(op.execution_time_seconds for op in operations) / total
        
        # Top commands
        command_counts = Counter(op.operation_name for op in operations)
        top_commands = dict(command_counts.most_common(10))
        
        # Team usage
        team_counts = Counter(op.team_id for op in operations)
        team_usage = dict(team_counts)
        
        return {
            "total_operations": total,
            "successful_operations": successful,
            "failed_operations": failed,
            "success_rate": round(success_rate, 2),
            "avg_execution_time_seconds": round(avg_exec_time, 2),
            "top_commands": top_commands,
            "team_usage": team_usage
        }
    
    def record_operation(
        self,
        operation_id: str,
        operation_name: str,
        tenant_id: str,
        team_id: str,
        user_id: str,
        started_at: datetime,
        completed_at: datetime,
        success: bool
    ) -> None:
        """Record a completed operation."""
        execution_time = (completed_at - started_at).total_seconds()
        
        record = OperationRecord(
            operation_id=operation_id,
            operation_name=operation_name,
            tenant_id=tenant_id,
            team_id=team_id,
            user_id=user_id,
            started_at=started_at,
            completed_at=completed_at,
            success=success,
            execution_time_seconds=execution_time
        )
        
        self.operations.append(record)
        logger.debug(f"Recorded operation: {operation_name} ({execution_time:.2f}s)")
