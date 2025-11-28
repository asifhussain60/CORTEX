"""
Compliance Summary Module - Sprint 1 Day 2

Provides quick compliance status retrieval for help system integration.

This module retrieves governance compliance metrics and formats them
for display in the help command's "Compliance At-A-Glance" section.

USAGE:
    from src.utils.compliance_summary import get_compliance_summary
    
    summary = get_compliance_summary()
    print(summary)  # "✅ 85% compliant (27/32 rules passing)"

INTEGRATION:
- Used by help_table template for real-time compliance display
- Lightweight queries (< 50ms response time)
- Fallback to cached data if governance system unavailable

SPRINT 1 DAY 2: Help Enhancement Integration
Author: Asif Hussain (CORTEX Enhancement System)
Date: November 28, 2025
"""

import logging
import os
from typing import Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


def get_compliance_summary(quick: bool = True) -> str:
    """
    Get a quick compliance summary for help display.
    
    Args:
        quick: If True, return cached/fast summary. If False, calculate fresh metrics.
    
    Returns:
        Formatted compliance summary string suitable for help display.
        Example: "✅ 85% compliant (27/32 rules passing)"
    """
    try:
        if quick:
            # Fast path: Use cached or estimate
            return _get_quick_compliance_summary()
        else:
            # Slow path: Calculate fresh metrics
            return _calculate_compliance_summary()
    
    except Exception as e:
        logger.warning(f"Failed to get compliance summary: {e}")
        return "⚠️ Compliance status unavailable (say 'compliance' for full report)"


def _get_quick_compliance_summary() -> str:
    """
    Get fast compliance summary using cached data or estimates.
    
    Returns:
        Formatted compliance summary string.
    """
    # Check for compliance database
    project_root = Path(__file__).parent.parent.parent
    compliance_db = project_root / "cortex-brain" / "cortex-compliance.db"
    
    if compliance_db.exists():
        # Try to read last known compliance
        try:
            import sqlite3
            conn = sqlite3.connect(str(compliance_db))
            cursor = conn.cursor()
            
            # Check if compliance_summary table exists
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='compliance_summary'
            """)
            
            if cursor.fetchone():
                # Get latest compliance summary
                cursor.execute("""
                    SELECT compliance_percentage, rules_passing, total_rules, status
                    FROM compliance_summary
                    ORDER BY last_updated DESC
                    LIMIT 1
                """)
                
                row = cursor.fetchone()
                conn.close()
                
                if row:
                    percentage, passing, total, status = row
                    icon = _get_compliance_icon(percentage)
                    return f"{icon} {percentage}% compliant ({passing}/{total} rules passing)"
            
            conn.close()
        
        except Exception as e:
            logger.debug(f"Could not read compliance from database: {e}")
    
    # Fallback: Estimate based on system health
    return _estimate_compliance_from_health()


def _calculate_compliance_summary() -> str:
    """
    Calculate fresh compliance metrics (slower but accurate).
    
    Returns:
        Formatted compliance summary string.
    """
    try:
        # Try to import governance checker
        from src.governance.compliance_checker import ComplianceChecker
        
        checker = ComplianceChecker()
        result = checker.check_quick()
        
        if result.get("success"):
            metrics = result.get("metrics", {})
            percentage = metrics.get("compliance_percentage", 0)
            passing = metrics.get("rules_passing", 0)
            total = metrics.get("total_rules", 0)
            
            icon = _get_compliance_icon(percentage)
            return f"{icon} {percentage}% compliant ({passing}/{total} rules passing)"
    
    except ImportError:
        logger.debug("ComplianceChecker not available, using estimation")
    except Exception as e:
        logger.warning(f"Compliance calculation failed: {e}")
    
    # Fallback to estimation
    return _estimate_compliance_from_health()


def _estimate_compliance_from_health() -> str:
    """
    Estimate compliance based on system health metrics.
    
    Returns:
        Estimated compliance summary string.
    """
    try:
        # Try to get system health from metrics database
        project_root = Path(__file__).parent.parent.parent
        metrics_db = project_root / "cortex_metrics.db"
        
        if metrics_db.exists():
            import sqlite3
            conn = sqlite3.connect(str(metrics_db))
            cursor = conn.cursor()
            
            # Get latest health score
            cursor.execute("""
                SELECT overall_health FROM system_health
                ORDER BY timestamp DESC LIMIT 1
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            if row:
                health = int(row[0])
                # Estimate compliance from health (rough correlation)
                estimated_compliance = min(95, health + 10)
                icon = _get_compliance_icon(estimated_compliance)
                return f"{icon} ~{estimated_compliance}% compliant (estimated from system health: {health}%)"
    
    except Exception as e:
        logger.debug(f"Could not estimate from health: {e}")
    
    # Ultimate fallback
    return "✅ Governance active (say 'compliance' for detailed status)"


def _get_compliance_icon(percentage: float) -> str:
    """
    Get appropriate icon based on compliance percentage.
    
    Args:
        percentage: Compliance percentage (0-100)
    
    Returns:
        Emoji icon representing compliance level.
    """
    if percentage >= 90:
        return "✅"
    elif percentage >= 75:
        return "⚠️"
    elif percentage >= 50:
        return "🔶"
    else:
        return "❌"


def get_detailed_compliance_status() -> Dict[str, Any]:
    """
    Get detailed compliance status with all metrics.
    
    This is the full version used by the compliance dashboard.
    
    Returns:
        Dict with detailed compliance data including:
            - compliance_percentage: Overall compliance percentage
            - rules_passing: Number of rules passing
            - total_rules: Total number of rules
            - failing_rules: List of failing rules
            - warnings: List of warnings
            - last_checked: Timestamp of last check
    """
    try:
        from src.governance.compliance_checker import ComplianceChecker
        
        checker = ComplianceChecker()
        return checker.check_full()
    
    except ImportError:
        logger.error("ComplianceChecker not available")
        return {
            "success": False,
            "error": "ComplianceChecker module not found",
            "compliance_percentage": 0,
            "rules_passing": 0,
            "total_rules": 0,
            "failing_rules": [],
            "warnings": ["Compliance system not fully initialized"]
        }
    
    except Exception as e:
        logger.error(f"Failed to get detailed compliance status: {e}")
        return {
            "success": False,
            "error": str(e),
            "compliance_percentage": 0,
            "rules_passing": 0,
            "total_rules": 0,
            "failing_rules": [],
            "warnings": [f"Compliance check failed: {str(e)}"]
        }


# Convenience function for template integration
def compliance_summary_for_template() -> str:
    """
    Get compliance summary formatted specifically for template injection.
    
    This is the function called by response templates via {compliance_summary}.
    
    Returns:
        Template-ready compliance summary string.
    """
    return get_compliance_summary(quick=True)
