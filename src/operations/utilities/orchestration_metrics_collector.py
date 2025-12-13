"""
Orchestration Metrics Collector - Silent background metrics for orchestrator engagement.

**Purpose:** Enable visibility into which orchestrators handle requests and their execution efficiency.
**Performance:** <5ms overhead per metric collection
**Storage:** logs/orchestration-metrics/{YYYY-MM-DD}/events.jsonl (git-ignored)
**Retention:** 30 days auto-archival

**Usage:**
    from src.operations.utilities.orchestration_metrics_collector import with_orchestration_metrics

    @with_orchestration_metrics
    async def my_orchestrator_handler(request):
        # Your orchestrator logic
        return response

**Author:** Asif Hussain
**Feature:** Orchestrator Enhancement Plan v2.0 - Feature 10
"""

import json
import time
import uuid
import functools
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, Optional, List
import logging

logger = logging.getLogger(__name__)


class OrchestrationMetricsCollector:
    """
    Silent background collector for orchestrator engagement metrics.
    
    **Responsibilities:**
    1. Log engagement_start events with event_id, orchestrator_name, timestamp
    2. Log engagement_complete events with matching event_id, duration, outcome
    3. Auto-create daily folders: logs/orchestration-metrics/{YYYY-MM-DD}/
    4. Write JSONL events (one JSON object per line)
    5. Performance: <5ms per operation
    6. Report generation: 7-day aggregation with statistics
    7. Retention policy: Archive data older than 30 days
    """
    
    def __init__(self, base_path: Optional[Path] = None):
        """
        Initialize metrics collector.
        
        Args:
            base_path: Base directory for metrics storage (default: logs/orchestration-metrics)
        """
        if base_path is None:
            # Default to CORTEX project root
            project_root = Path(__file__).resolve().parent.parent.parent.parent
            base_path = project_root / "logs" / "orchestration-metrics"
        
        self.base_path = Path(base_path)
        self._ensure_base_directory()
    
    def _ensure_base_directory(self):
        """Create base directory if it doesn't exist."""
        try:
            self.base_path.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Failed to create metrics base directory: {e}")
    
    def _get_daily_folder(self, timestamp: Optional[datetime] = None) -> Path:
        """
        Get daily folder path for metrics storage.
        
        Args:
            timestamp: Optional timestamp for folder (default: now)
        
        Returns:
            Path to daily folder (e.g., logs/orchestration-metrics/2025-12-08/)
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        date_str = timestamp.strftime("%Y-%m-%d")
        daily_folder = self.base_path / date_str
        
        # Auto-create daily folder
        try:
            daily_folder.mkdir(parents=True, exist_ok=True)
        except Exception as e:
            logger.warning(f"Failed to create daily metrics folder {daily_folder}: {e}")
        
        return daily_folder
    
    def _write_event(self, event: Dict[str, Any], event_id: str, event_type: str):
        """
        Write event to individual JSON file.
        
        File naming: {orchestrator}-{event_id[:8]}-{start|complete}.json
        
        Args:
            event: Event dictionary to log
            event_id: Event ID for filename
            event_type: "start" or "complete"
        """
        try:
            daily_folder = self._get_daily_folder()
            
            # Extract orchestrator name and convert to lowercase for filename
            orchestrator_name = event.get("orchestrator_name", "unknown").lower()
            
            # Create filename: testorchestrator-abc123de-start.json
            filename = f"{orchestrator_name}-{event_id[:8]}-{event_type}.json"
            event_file = daily_folder / filename
            
            # Write event as individual JSON file
            with event_file.open("w") as f:
                json.dump(event, f, indent=2, default=str)
        except Exception as e:
            logger.warning(f"Failed to write metrics event: {e}")
    
    def log_engagement_start(
        self,
        orchestrator_name: str,
        operation_type: str,
        event_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Log orchestrator engagement start event.
        
        Args:
            orchestrator_name: Name of orchestrator (e.g., "PlanningOrchestrator")
            operation_type: Type of operation (e.g., "plan_generation", "test_execution")
            event_id: Optional event ID (auto-generated UUID if not provided)
            metadata: Optional metadata dictionary
        
        Returns:
            event_id for matching with engagement_complete
        """
        start_time = time.time()
        
        if event_id is None:
            event_id = str(uuid.uuid4())
        
        event = {
            "event_type": "start",
            "event_id": event_id,
            "orchestrator_name": orchestrator_name,
            "operation_type": operation_type,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {}
        }
        
        self._write_event(event, event_id, "start")
        
        # Performance tracking
        elapsed_ms = (time.time() - start_time) * 1000
        if elapsed_ms > 5:
            logger.warning(f"Metrics log_engagement_start exceeded 5ms: {elapsed_ms:.2f}ms")
        
        return event_id
    
    def log_engagement_complete(
        self,
        event_id: str,
        status: str = "success",
        result_summary: Optional[str] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[float] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Log orchestrator engagement completion event.
        
        Args:
            event_id: Event ID from log_engagement_start (for matching)
            status: "success" or "error"
            result_summary: Optional summary of result
            error_message: Optional error message if status="error"
            duration_ms: Optional execution duration in milliseconds (calculated if not provided)
            metadata: Optional metadata dictionary
        
        Returns:
            True if logged successfully
        """
        start_time = time.time()
        
        # Get orchestrator name from start event if needed
        daily_folder = self._get_daily_folder()
        start_file_pattern = f"*-{event_id[:8]}-start.json"
        start_files = list(daily_folder.glob(start_file_pattern))
        
        orchestrator_name = "unknown"
        start_timestamp = None
        
        if start_files:
            try:
                with start_files[0].open("r") as f:
                    start_event = json.load(f)
                    orchestrator_name = start_event.get("orchestrator_name", "unknown")
                    start_timestamp = start_event.get("timestamp")
            except Exception:
                pass
        
        # Calculate duration if not provided
        if duration_ms is None and start_timestamp:
            try:
                start_dt = datetime.fromisoformat(start_timestamp)
                now_dt = datetime.now()
                duration_ms = (now_dt - start_dt).total_seconds() * 1000
            except Exception:
                duration_ms = 0.0  # Default if calculation fails
        elif duration_ms is None:
            duration_ms = 0.0  # Default if no start timestamp
        
        event = {
            "event_type": "complete",
            "event_id": event_id,
            "orchestrator_name": orchestrator_name,
            "timestamp": datetime.now().isoformat(),
            "status": status,
            "result_summary": result_summary,
            "error": error_message,  # Use "error" key for test compatibility
            "duration_ms": duration_ms,
            "metadata": metadata or {}
        }
        
        self._write_event(event, event_id, "complete")
        
        # Performance tracking
        elapsed_ms = (time.time() - start_time) * 1000
        if elapsed_ms > 5:
            logger.warning(f"Metrics log_engagement_complete exceeded 5ms: {elapsed_ms:.2f}ms")
        
        return True    
    def generate_report(self, days: int = 7) -> Dict[str, Any]:
        """
        Generate aggregated metrics report for last N days.
        
        Args:
            days: Number of days to include in report (default: 7)
        
        Returns:
            Dictionary with aggregate statistics:
            - total_engagements: Total count
            - by_orchestrator: {orchestrator_name: {count, avg_duration_ms, success_rate}}
            - by_day: {YYYY-MM-DD: count}
            - avg_duration_ms: Overall average
            - success_rate: Overall success percentage
        """
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        all_events = []
        current_date = start_date
        
        # Collect events from all days in range
        while current_date <= end_date:
            daily_folder = self._get_daily_folder(current_date)
            
            if daily_folder.exists():
                try:
                    # Read all JSON files in folder
                    for json_file in daily_folder.glob("*.json"):
                        with json_file.open("r") as f:
                            event = json.load(f)
                            all_events.append(event)
                except Exception as e:
                    logger.warning(f"Failed to read events from {daily_folder}: {e}")
            
            current_date += timedelta(days=1)
        
        # Build statistics
        stats = {
            "total_engagements": 0,
            "orchestrators": {},  # Changed from "by_orchestrator"
            "by_day": {},
            "time_period": f"Last {days} days",  # Added for test compatibility
            "avg_duration_ms": 0.0,
            "success_rate": 0.0
        }
        
        # Group events by event_id for matching start/complete
        events_by_id = {}
        for event in all_events:
            event_id = event.get("event_id")
            if event_id not in events_by_id:
                events_by_id[event_id] = {}
            
            event_type = event.get("event_type")
            if event_type == "start":
                events_by_id[event_id]["engagement_start"] = event
            elif event_type == "complete":
                events_by_id[event_id]["engagement_complete"] = event
        
        # Calculate statistics
        total_duration_ms = 0.0
        successful_count = 0
        
        for event_id, event_pair in events_by_id.items():
            if "engagement_complete" not in event_pair:
                continue  # Incomplete engagement
            
            start_event = event_pair.get("engagement_start", {})
            complete_event = event_pair["engagement_complete"]
            
            orchestrator_name = start_event.get("orchestrator_name", "unknown")
            duration_ms = complete_event.get("duration_ms", 0.0)  # Default to 0 if missing
            
            status = complete_event.get("status", "unknown")
            
            # Track by orchestrator
            if orchestrator_name not in stats["orchestrators"]:
                stats["orchestrators"][orchestrator_name] = {
                    "total_engagements": 0,  # Changed from "count"
                    "total_duration_ms": 0.0,
                    "successful": 0
                }
            
            orch_stats = stats["orchestrators"][orchestrator_name]
            orch_stats["total_engagements"] += 1
            orch_stats["total_duration_ms"] += duration_ms
            if status == "success":
                orch_stats["successful"] += 1
                successful_count += 1
            
            # Track by day
            timestamp_str = complete_event.get("timestamp", "")
            if timestamp_str:
                date_str = timestamp_str.split("T")[0]  # Extract YYYY-MM-DD
                stats["by_day"][date_str] = stats["by_day"].get(date_str, 0) + 1
            
            stats["total_engagements"] += 1
            total_duration_ms += duration_ms
        
        # Calculate averages
        if stats["total_engagements"] > 0:
            stats["avg_duration_ms"] = total_duration_ms / stats["total_engagements"]
            stats["success_rate"] = (successful_count / stats["total_engagements"]) * 100
        
        # Calculate per-orchestrator averages
        for orchestrator_name, orch_stats in stats["orchestrators"].items():
            if orch_stats["total_engagements"] > 0:
                orch_stats["avg_duration_ms"] = orch_stats["total_duration_ms"] / orch_stats["total_engagements"]
                orch_stats["success_rate"] = (orch_stats["successful"] / orch_stats["total_engagements"]) * 100
            
            # Remove internal tracking fields
            del orch_stats["total_duration_ms"]
            del orch_stats["successful"]
        
        return stats
    
    def apply_retention_policy(self, days: int = 30) -> int:
        """
        Archive metrics data older than specified days.
        
        Args:
            days: Number of days to retain (default: 30)
        
        Returns:
            Number of folders archived
        """
        cutoff_date = datetime.now() - timedelta(days=days)
        archived_count = 0
        
        # Find all daily folders
        if not self.base_path.exists():
            return archived_count
        
        for daily_folder in self.base_path.iterdir():
            if not daily_folder.is_dir():
                continue
            
            folder_name = daily_folder.name
            
            # Parse YYYY-MM-DD format
            try:
                folder_date = datetime.strptime(folder_name, "%Y-%m-%d")
            except ValueError:
                continue  # Skip non-date folders
            
            # Check if older than retention period
            if folder_date < cutoff_date:
                # Archive folder (move to archives subdirectory)
                archive_base = self.base_path / "archives"
                archive_base.mkdir(parents=True, exist_ok=True)
                
                archive_dest = archive_base / folder_name
                
                try:
                    # Delete destination if it exists
                    if archive_dest.exists():
                        import shutil
                        shutil.rmtree(archive_dest)
                    
                    daily_folder.rename(archive_dest)
                    archived_count += 1
                    logger.info(f"Archived old metrics: {folder_name}")
                except Exception as e:
                    logger.warning(f"Failed to archive {folder_name}: {e}")
        
        return archived_count


# Global collector instance
_collector = OrchestrationMetricsCollector()


def with_orchestration_metrics(orchestrator_name: str):
    """
    Decorator for automatic orchestrator metrics collection.
    
    Usage:
        @with_orchestration_metrics("MyOrchestrator")
        def my_orchestrator(request):
            return response
    
    Features:
    - Auto-logs engagement_start before function execution
    - Auto-logs engagement_complete after function execution
    - Tracks duration and status (success/error)
    - <5ms overhead per call
    
    Args:
        orchestrator_name: Name of orchestrator for metrics tracking
    """
    
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            
            # Log engagement start
            event_id = _collector.log_engagement_start(
                orchestrator_name=orchestrator_name,
                operation_type=func.__name__
            )
            
            try:
                # Execute orchestrator
                result = func(*args, **kwargs)
                
                # Log engagement complete (success)
                duration_ms = (time.time() - start_time) * 1000
                _collector.log_engagement_complete(
                    event_id=event_id,
                    status="success",
                    duration_ms=duration_ms
                )
                
                return result
            
            except Exception as e:
                # Log engagement complete (error)
                duration_ms = (time.time() - start_time) * 1000
                _collector.log_engagement_complete(
                    event_id=event_id,
                    status="error",
                    error_message=str(e),
                    duration_ms=duration_ms
                )
                
                raise  # Re-raise exception
        
        return wrapper
    
    return decorator
