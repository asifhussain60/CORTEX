"""
Governance Telemetry Module

Tracks enforcement agent invocations, violations, and trends.
Provides observability into governance enforcement health.

Authority: Phase 4 - GAP-002 Resolution (Observability & Monitoring)
Author: Asif Hussain
Date: 2026-02-10
"""

import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import json
import logging

logger = logging.getLogger(__name__)


class GovernanceTelemetry:
    """
    Tracks governance enforcement metrics for observability.
    
    Metrics tracked:
    - Agent invocations (count, latency)
    - Violation types and frequencies
    - Enforcement decisions (PASS/WARNING/BLOCKED)
    - Trend analysis over time
    """
    
    def __init__(self, log_dir: Optional[Path] = None):
        """
        Initialize governance telemetry.
        
        Args:
            log_dir: Directory for telemetry logs (default: .cortex/telemetry/)
        """
        self.log_dir = log_dir or Path(".cortex/telemetry")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.current_session: Dict = {
            "session_id": datetime.now().strftime("%Y%m%d-%H%M%S"),
            "start_time": time.time(),
            "agent_invocations": [],
            "violations": [],
            "warnings": [],
        }
    
    def record_agent_invocation(
        self,
        agent_name: str,
        intent: str,
        result: str,
        latency_ms: float,
        violations_count: int = 0,
        warnings_count: int = 0,
    ) -> None:
        """
        Record an enforcement agent invocation.
        
        Args:
            agent_name: Name of the agent (e.g., "MarkdownSuppressionAgent")
            intent: User intent (e.g., "IMPLEMENT", "ANALYZE")
            result: Enforcement result ("PASS", "WARNING", "BLOCKED")
            latency_ms: Agent execution time in milliseconds
            violations_count: Number of violations detected
            warnings_count: Number of warnings issued
        """
        invocation = {
            "timestamp": datetime.now().isoformat(),
            "agent": agent_name,
            "intent": intent,
            "result": result,
            "latency_ms": latency_ms,
            "violations": violations_count,
            "warnings": warnings_count,
        }
        
        self.current_session["agent_invocations"].append(invocation)
        
        logger.info(
            f"Telemetry: {agent_name} | {intent} | {result} | "
            f"{latency_ms:.2f}ms | V:{violations_count} W:{warnings_count}"
        )
    
    def record_violation(
        self,
        rule_id: str,
        violation_message: str,
        file_path: Optional[str] = None,
        agent_name: Optional[str] = None,
    ) -> None:
        """
        Record a governance violation.
        
        Args:
            rule_id: CORE rule ID (e.g., "CORE-002")
            violation_message: Human-readable violation description
            file_path: File path where violation occurred (if applicable)
            agent_name: Agent that detected the violation
        """
        violation = {
            "timestamp": datetime.now().isoformat(),
            "rule_id": rule_id,
            "message": violation_message,
            "file": file_path,
            "agent": agent_name,
        }
        
        self.current_session["violations"].append(violation)
        
        logger.warning(f"Violation: {rule_id} | {violation_message}")
    
    def record_warning(
        self,
        rule_id: str,
        warning_message: str,
        agent_name: Optional[str] = None,
    ) -> None:
        """
        Record a governance warning.
        
        Args:
            rule_id: CORE rule ID (e.g., "CORE-011")
            warning_message: Human-readable warning description
            agent_name: Agent that issued the warning
        """
        warning = {
            "timestamp": datetime.now().isoformat(),
            "rule_id": rule_id,
            "message": warning_message,
            "agent": agent_name,
        }
        
        self.current_session["warnings"].append(warning)
        
        logger.info(f"Warning: {rule_id} | {warning_message}")
    
    def get_session_summary(self) -> Dict:
        """
        Get summary statistics for current session.
        
        Returns:
            Dictionary with session metrics
        """
        total_invocations = len(self.current_session["agent_invocations"])
        
        if total_invocations == 0:
            return {
                "total_invocations": 0,
                "total_violations": 0,
                "total_warnings": 0,
                "avg_latency_ms": 0,
            }
        
        total_latency = sum(
            inv["latency_ms"] for inv in self.current_session["agent_invocations"]
        )
        
        return {
            "session_id": self.current_session["session_id"],
            "duration_sec": time.time() - self.current_session["start_time"],
            "total_invocations": total_invocations,
            "total_violations": len(self.current_session["violations"]),
            "total_warnings": len(self.current_session["warnings"]),
            "avg_latency_ms": total_latency / total_invocations,
            "agents_used": list(set(
                inv["agent"] for inv in self.current_session["agent_invocations"]
            )),
        }
    
    def flush_to_disk(self) -> Path:
        """
        Write current session telemetry to disk.
        
        Returns:
            Path to telemetry log file
        """
        log_file = self.log_dir / f"{self.current_session['session_id']}.json"
        
        with open(log_file, 'w') as f:
            json.dump(self.current_session, f, indent=2)
        
        logger.info(f"Telemetry flushed to {log_file}")
        return log_file
    
    def get_violation_trends(self, days: int = 7) -> Dict[str, List]:
        """
        Analyze violation trends over time.
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Dictionary with trend data by rule_id
        """
        cutoff = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        trends: Dict[str, List] = {}
        
        # Read all telemetry logs from last N days
        for log_file in sorted(self.log_dir.glob("*.json")):
            try:
                with open(log_file, 'r') as f:
                    session = json.load(f)
                
                # Check if session is within timeframe
                session_time = datetime.fromisoformat(
                    session["agent_invocations"][0]["timestamp"]
                ).timestamp() if session.get("agent_invocations") else 0
                
                if session_time < cutoff:
                    continue
                
                # Aggregate violations by rule_id
                for violation in session.get("violations", []):
                    rule_id = violation["rule_id"]
                    if rule_id not in trends:
                        trends[rule_id] = []
                    trends[rule_id].append({
                        "timestamp": violation["timestamp"],
                        "message": violation["message"],
                    })
            
            except Exception as e:
                logger.error(f"Error reading telemetry log {log_file}: {e}")
        
        return trends


# Global telemetry instance
_telemetry_instance: Optional[GovernanceTelemetry] = None


def get_telemetry() -> GovernanceTelemetry:
    """Get or create global telemetry instance."""
    global _telemetry_instance
    if _telemetry_instance is None:
        _telemetry_instance = GovernanceTelemetry()
    return _telemetry_instance
