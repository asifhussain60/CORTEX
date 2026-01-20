"""
PHASE 6: Governance Dashboard - Compliance Metrics API

Provides REST endpoints for real-time compliance metrics, domain coverage,
timeline analysis, and individual AC details.
"""

from fastapi import APIRouter, HTTPException
from datetime import datetime
import sqlite3
from typing import Dict, List, Any
import os

router = APIRouter(prefix="/api/compliance", tags=["compliance"])

# Database configuration
DB_PATH = os.path.join(
    os.path.dirname(__file__),
    "../../../cortex_brain/state/governance.db"
)


def get_db_connection():
    """Get SQLite database connection with timeout"""
    conn = sqlite3.connect(DB_PATH, timeout=10.0)
    conn.row_factory = sqlite3.Row
    return conn


@router.get("/coverage", summary="Get AC Coverage Metrics")
async def get_coverage_metrics() -> Dict[str, Any]:
    """
    Get current acceptance criteria coverage statistics.
    
    Returns:
        - total_acs: Total number of acceptance criteria
        - covered_acs: Number of covered ACs
        - coverage_percentage: Coverage as percentage (0-100)
        - timestamp: Current timestamp
    """
    try:
        with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
            cursor = conn.cursor()
            
            # Get total unique ACs
            cursor.execute("SELECT COUNT(DISTINCT ac_id) FROM audit_log")
            total_acs = cursor.fetchone()[0] or 0
            
            # Get completed ACs
            cursor.execute(
                "SELECT COUNT(DISTINCT ac_id) FROM audit_log WHERE operation = 'AC_COMPLETE'"
            )
            covered_acs = cursor.fetchone()[0] or 0
        
        coverage_percentage = (covered_acs / total_acs * 100) if total_acs > 0 else 0
        
        return {
            "total_acs": total_acs,
            "covered_acs": covered_acs,
            "coverage_percentage": round(coverage_percentage, 1),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/by-domain", summary="Get Coverage by Domain")
async def get_coverage_by_domain() -> Dict[str, Dict[str, Any]]:
    """
    Get AC coverage broken down by domain (AR, BR, FR, etc.).
    
    Returns:
        Dictionary with domain codes as keys and coverage stats as values
    """
    try:
        with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
            cursor = conn.cursor()
            
            # Get all unique domains
            cursor.execute(
                "SELECT DISTINCT SUBSTR(ac_id, 1, INSTR(ac_id, '-')-1) as domain FROM audit_log"
            )
            domains_raw = cursor.fetchall()
            
            domains_result = {}
            
            for domain_row in domains_raw:
                domain = domain_row[0]
                
                # Get total ACs for domain
                cursor.execute(
                    f"SELECT COUNT(DISTINCT ac_id) FROM audit_log WHERE ac_id LIKE '{domain}-%'"
                )
                total = cursor.fetchone()[0] or 0
                
                # Get covered ACs for domain
                cursor.execute(
                    f"SELECT COUNT(DISTINCT ac_id) FROM audit_log WHERE ac_id LIKE '{domain}-%' AND operation = 'AC_COMPLETE'"
                )
                covered = cursor.fetchone()[0] or 0
                
                percentage = (covered / total * 100) if total > 0 else 0
                
                domains_result[domain] = {
                    "total": total,
                    "covered": covered,
                    "percentage": round(percentage, 1),
                    "status": "COMPLETE" if percentage == 100 else "IN_PROGRESS"
                }
        
        return domains_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/timeline", summary="Get Compliance Growth Timeline")
async def get_compliance_timeline() -> Dict[str, Any]:
    """
    Get compliance growth over phases (Phase 1-5).
    Shows progression from initial state to 100% coverage.
    
    Returns:
        List of phases with entries, ACs, and coverage percentage
    """
    # Historical data from project progression
    timeline = {
        "phases": [
            {
                "phase": 1,
                "name": "Database Recovery",
                "entries": 145,
                "acs": 6,
                "coverage": 5.0,
                "status": "COMPLETE"
            },
            {
                "phase": 2,
                "name": "Systematic Markers",
                "entries": 993,
                "acs": 46,
                "coverage": 38.3,
                "status": "COMPLETE"
            },
            {
                "phase": 3,
                "name": "Gap Analysis",
                "entries": 1494,
                "acs": 68,
                "coverage": 56.7,
                "status": "COMPLETE"
            },
            {
                "phase": 4,
                "name": "Comprehensive Testing",
                "entries": 2766,
                "acs": 83,
                "coverage": 69.2,
                "status": "COMPLETE"
            },
            {
                "phase": 5,
                "name": "Final Completion",
                "entries": 2877,
                "acs": 120,
                "coverage": 100.0,
                "status": "COMPLETE"
            }
        ]
    }
    return timeline


@router.get("/ac/{ac_id}", summary="Get Details for Specific AC")
async def get_ac_details(ac_id: str) -> Dict[str, Any]:
    """
    Get detailed information for a specific acceptance criterion.
    
    Args:
        ac_id: Acceptance criterion ID (e.g., 'AR-001-01')
    
    Returns:
        AC details including entries, status, history
    """
    try:
        with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get AC entries
            cursor.execute(
                "SELECT operation, context, timestamp FROM audit_log WHERE ac_id = ? ORDER BY timestamp",
                (ac_id,)
            )
            entries = [dict(row) for row in cursor.fetchall()]
            
            if not entries:
                raise HTTPException(status_code=404, detail=f"AC {ac_id} not found")
            
            # Determine status
            statuses = [e['operation'] for e in entries]
            status = "COMPLETE" if "AC_COMPLETE" in statuses else "IN_PROGRESS"
            
            return {
                "ac_id": ac_id,
                "status": status,
                "total_entries": len(entries),
                "history": entries
            }
    except sqlite3.OperationalError as e:
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


@router.get("/stats", summary="Get Overall Statistics")
async def get_overall_stats() -> Dict[str, Any]:
    """
    Get comprehensive overall statistics about the governance framework.
    """
    try:
        with sqlite3.connect(DB_PATH, timeout=10.0) as conn:
            cursor = conn.cursor()
            
            # Total entries
            cursor.execute("SELECT COUNT(*) FROM audit_log")
            total_entries = cursor.fetchone()[0] or 0
            
            # Total unique ACs
            cursor.execute("SELECT COUNT(DISTINCT ac_id) FROM audit_log")
            total_acs = cursor.fetchone()[0] or 0
            
            # Completed ACs
            cursor.execute(
                "SELECT COUNT(DISTINCT ac_id) FROM audit_log WHERE operation = 'AC_COMPLETE'"
            )
            completed_acs = cursor.fetchone()[0] or 0
            
            # Operations breakdown
            cursor.execute(
                "SELECT operation, COUNT(*) FROM audit_log GROUP BY operation"
            )
            operations = {row[0]: row[1] for row in cursor.fetchall()}
            
            # Unique domains
            cursor.execute(
                "SELECT COUNT(DISTINCT SUBSTR(ac_id, 1, INSTR(ac_id, '-')-1)) FROM audit_log"
            )
            domains_count = cursor.fetchone()[0] or 0
        
        coverage = (completed_acs / total_acs * 100) if total_acs > 0 else 0
        
        return {
            "total_entries": total_entries,
            "total_acs": total_acs,
            "completed_acs": completed_acs,
            "coverage_percentage": round(coverage, 1),
            "unique_domains": domains_count,
            "operations": operations,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
