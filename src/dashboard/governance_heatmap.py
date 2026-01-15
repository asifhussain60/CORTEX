"""
Governance Rule Dashboard - Compliance Heatmap
Shows visual representation of rule compliance status across domains and phases.
"""

import sqlite3
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
from pathlib import Path


class GovernanceHeatmapGenerator:
    """Generates compliance heatmap data from governance database."""
    
    def __init__(self, db_path: str = "cortex-brain/state/governance.db"):
        """Initialize heatmap generator."""
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to governance database."""
        self.conn = sqlite3.connect(self.db_path, timeout=10.0)
        self.conn.row_factory = sqlite3.Row
        
    def disconnect(self):
        """Disconnect from database."""
        if self.conn:
            self.conn.close()
            
    def generate_heatmap_data(self) -> Dict[str, Any]:
        """Generate complete heatmap data."""
        self.connect()
        
        try:
            # Get domain compliance summary
            domains = self._get_domain_compliance()
            
            # Get phase readiness
            phases = self._get_phase_readiness()
            
            # Get trend data
            trend = self._get_compliance_trend()
            
            return {
                "generated_at": datetime.now().isoformat(),
                "domains": domains,
                "phases": phases,
                "trend": trend,
                "summary": {
                    "total_acs": self._count_total_acs(),
                    "covered_acs": self._count_covered_acs(),
                    "coverage_percentage": self._calculate_coverage_percentage(),
                    "locked_phases": self._count_locked_phases(),
                    "total_audit_entries": self._count_total_audit_entries()
                }
            }
        finally:
            self.disconnect()
            
    def _get_domain_compliance(self) -> List[Dict[str, Any]]:
        """Get compliance data by domain."""
        cursor = self.conn.cursor()
        
        # Get all ACs and their audit status
        cursor.execute("""
            SELECT 
                ai.ac_id,
                ai.phase,
                CASE WHEN COUNT(al.id) > 0 THEN 1 ELSE 0 END as has_audit
            FROM ac_index ai
            LEFT JOIN audit_log al ON ai.ac_id = al.ac_id
            GROUP BY ai.ac_id
        """)
        
        ac_data = cursor.fetchall()
        
        # Group by domain (first part of AC-ID after AC-)
        domains_dict = {}
        for row in ac_data:
            ac_id = row["ac_id"]  # e.g., "AC-AR-001-01"
            # Extract domain: AC-AR from "AC-AR-001-01"
            domain = ac_id.split('-')[1]  # Get "AR" from "AC-AR-..."
            
            if domain not in domains_dict:
                domains_dict[domain] = {"total": 0, "covered": 0}
            
            domains_dict[domain]["total"] += 1
            if row["has_audit"]:
                domains_dict[domain]["covered"] += 1
        
        domains = []
        for domain, stats in sorted(domains_dict.items()):
            coverage = (stats["covered"] / stats["total"] * 100) if stats["total"] > 0 else 0
            
            domains.append({
                "domain": domain,
                "total_acs": stats["total"],
                "covered_acs": stats["covered"],
                "coverage_percentage": round(coverage, 2),
                "audit_entries": stats["covered"],
                "status": self._get_status(coverage),
                "color": self._get_color(coverage)
            })
            
        return domains
        
    def _get_phase_readiness(self) -> List[Dict[str, Any]]:
        """Get readiness status by phase."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT 
                phase,
                COUNT(DISTINCT ai.ac_id) as total_acs,
                COUNT(DISTINCT al.ac_id) as verified_acs
            FROM ac_index ai
            LEFT JOIN audit_log al ON ai.ac_id = al.ac_id
            GROUP BY phase
            ORDER BY phase
        """)
        
        phases = []
        for row in cursor.fetchall():
            total = row["total_acs"]
            verified = row["verified_acs"] or 0
            readiness = (verified / total * 100) if total > 0 else 0
            
            # Check if phase is locked
            cursor.execute("SELECT locked FROM phase_locks WHERE phase_id = ?", (row["phase"],))
            lock_row = cursor.fetchone()
            is_locked = lock_row and lock_row["locked"] == 1
            
            phases.append({
                "phase": row["phase"],
                "total_acs": total,
                "verified_acs": verified,
                "readiness_percentage": round(readiness, 2),
                "status": "locked" if is_locked else self._get_status(readiness),
                "locked": is_locked,
                "readiness_stage": self._get_readiness_stage(readiness)
            })
            
        return phases
        
    def _get_compliance_trend(self) -> List[Dict[str, Any]]:
        """Get compliance trend over time."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT 
                DATE(timestamp) as date,
                COUNT(DISTINCT ac_id) as new_entries
            FROM audit_log
            GROUP BY DATE(timestamp)
            ORDER BY date DESC
            LIMIT 30
        """)
        
        trend = []
        cumulative = 0
        
        # Sort ascending for trend display
        rows = list(reversed(cursor.fetchall()))
        
        for row in rows:
            cumulative += row["new_entries"] or 0
            trend.append({
                "date": row["date"],
                "new_entries": row["new_entries"],
                "cumulative_entries": cumulative
            })
            
        return trend
        
    def _count_total_acs(self) -> int:
        """Count total AC-IDs."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(DISTINCT ac_id) FROM ac_index")
        return cursor.fetchone()[0] or 0
        
    def _count_covered_acs(self) -> int:
        """Count ACs with audit evidence."""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT COUNT(DISTINCT ai.ac_id) FROM ac_index ai
            JOIN audit_log al ON ai.ac_id = al.ac_id
        """)
        return cursor.fetchone()[0] or 0
        
    def _calculate_coverage_percentage(self) -> float:
        """Calculate overall coverage percentage."""
        total = self._count_total_acs()
        covered = self._count_covered_acs()
        return round((covered / total * 100) if total > 0 else 0, 2)
        
    def _count_locked_phases(self) -> int:
        """Count locked phases."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM phase_locks WHERE locked = 1")
        return cursor.fetchone()[0] or 0
        
    def _count_total_audit_entries(self) -> int:
        """Count total audit log entries."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM audit_log")
        return cursor.fetchone()[0] or 0
        
    def _get_status(self, percentage: float) -> str:
        """Get status label based on percentage."""
        if percentage >= 90:
            return "excellent"
        elif percentage >= 75:
            return "good"
        elif percentage >= 50:
            return "acceptable"
        elif percentage >= 25:
            return "needs-work"
        else:
            return "critical"
            
    def _get_color(self, percentage: float) -> str:
        """Get color code for heatmap."""
        if percentage >= 90:
            return "#10B981"  # Green
        elif percentage >= 75:
            return "#3B82F6"   # Blue
        elif percentage >= 50:
            return "#F59E0B"   # Amber
        elif percentage >= 25:
            return "#EF4444"   # Red
        else:
            return "#7C3AED"   # Violet
            
    def _get_readiness_stage(self, percentage: float) -> str:
        """Get readiness stage name."""
        if percentage >= 100:
            return "READY_FOR_LOCK"
        elif percentage >= 75:
            return "NEAR_READY"
        elif percentage >= 50:
            return "IN_PROGRESS"
        else:
            return "NOT_STARTED"


class PhaseReadinessChecker:
    """4-stage readiness check: governance, audit, tests, docs."""
    
    def __init__(self, db_path: str = "cortex-brain/state/governance.db"):
        """Initialize readiness checker."""
        self.db_path = db_path
        self.conn = None
        
    def connect(self):
        """Connect to database."""
        self.conn = sqlite3.connect(self.db_path, timeout=10.0)
        self.conn.row_factory = sqlite3.Row
        
    def disconnect(self):
        """Disconnect from database."""
        if self.conn:
            self.conn.close()
            
    def check_phase_readiness(self, phase_id: str) -> Dict[str, Any]:
        """Perform 4-stage readiness check on a phase."""
        self.connect()
        
        try:
            # Stage 1: Governance - Do all ACs exist?
            governance_ready = self._check_governance(phase_id)
            
            # Stage 2: Audit - Do we have audit trail?
            audit_ready = self._check_audit(phase_id)
            
            # Stage 3: Tests - Are tests passing?
            tests_ready = self._check_tests(phase_id)
            
            # Stage 4: Docs - Is documentation complete?
            docs_ready = self._check_docs(phase_id)
            
            # Overall readiness
            all_stages_ready = all([
                governance_ready["ready"],
                audit_ready["ready"],
                tests_ready["ready"],
                docs_ready["ready"]
            ])
            
            return {
                "phase_id": phase_id,
                "readiness_stages": {
                    "governance": governance_ready,
                    "audit": audit_ready,
                    "tests": tests_ready,
                    "documentation": docs_ready
                },
                "overall_ready": all_stages_ready,
                "ready_for_lock": all_stages_ready,
                "readiness_percentage": self._calculate_readiness_percentage([
                    governance_ready, audit_ready, tests_ready, docs_ready
                ]),
                "timestamp": datetime.now().isoformat()
            }
        finally:
            self.disconnect()
            
    def _check_governance(self, phase_id: str) -> Dict[str, Any]:
        """Stage 1: Check if all ACs are defined."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as total FROM ac_index WHERE phase = ?
        """, (phase_id,))
        
        total_acs = cursor.fetchone()["total"] or 0
        
        return {
            "stage": "governance",
            "description": "All acceptance criteria defined",
            "ready": total_acs > 0,
            "details": {
                "total_acs": total_acs,
                "required": total_acs > 0
            }
        }
        
    def _check_audit(self, phase_id: str) -> Dict[str, Any]:
        """Stage 2: Check if audit trail exists."""
        cursor = self.conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(DISTINCT ai.ac_id) as covered 
            FROM ac_index ai
            JOIN audit_log al ON ai.ac_id = al.ac_id
            WHERE ai.phase = ?
        """, (phase_id,))
        
        covered = cursor.fetchone()["covered"] or 0
        
        cursor.execute("""
            SELECT COUNT(*) as total FROM ac_index WHERE phase = ?
        """, (phase_id,))
        
        total = cursor.fetchone()["total"] or 0
        coverage = (covered / total * 100) if total > 0 else 0
        
        return {
            "stage": "audit",
            "description": "Audit evidence collected",
            "ready": coverage >= 100,
            "details": {
                "covered_acs": covered,
                "total_acs": total,
                "coverage_percentage": round(coverage, 2),
                "required_coverage": 100
            }
        }
        
    def _check_tests(self, phase_id: str) -> Dict[str, Any]:
        """Stage 3: Check if tests are defined."""
        cursor = self.conn.cursor()
        
        # Count audit log entries with this phase marker
        cursor.execute("""
            SELECT COUNT(*) as entries FROM audit_log 
            WHERE message LIKE ? OR ac_id LIKE ?
        """, (f"%{phase_id}%", f"%{phase_id}%"))
        
        test_entries = cursor.fetchone()["entries"] or 0
        
        return {
            "stage": "tests",
            "description": "Tests created and passing",
            "ready": test_entries > 0,
            "details": {
                "test_entries": test_entries,
                "required": test_entries > 0
            }
        }
        
    def _check_docs(self, phase_id: str) -> Dict[str, Any]:
        """Stage 4: Check if documentation is complete."""
        docs_path = Path(f"docs/{phase_id.lower()}.md")
        
        doc_exists = docs_path.exists()
        doc_size = docs_path.stat().st_size if doc_exists else 0
        has_content = doc_size > 100  # At least 100 bytes
        
        return {
            "stage": "documentation",
            "description": "Documentation complete",
            "ready": has_content,
            "details": {
                "doc_file": str(docs_path),
                "exists": doc_exists,
                "size_bytes": doc_size,
                "required_size": 100
            }
        }
        
    def _calculate_readiness_percentage(self, stages: List[Dict[str, Any]]) -> float:
        """Calculate overall readiness percentage."""
        ready_count = sum(1 for stage in stages if stage["ready"])
        total_stages = len(stages)
        return round((ready_count / total_stages * 100) if total_stages > 0 else 0, 2)


def generate_dashboard_html(heatmap_data: Dict[str, Any]) -> str:
    """Generate HTML dashboard for heatmap visualization."""
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>CORTEX Governance Heatmap</title>
        <script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/3.9.1/chart.min.js"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
            .container {{ max-width: 1400px; margin: 0 auto; padding: 20px; }}
            .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 8px; margin-bottom: 30px; }}
            .header h1 {{ font-size: 2em; margin-bottom: 10px; }}
            .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }}
            .stat-card {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .stat-value {{ font-size: 2em; font-weight: bold; color: #667eea; }}
            .stat-label {{ color: #666; margin-top: 5px; }}
            .heatmap {{ background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 30px; }}
            .heatmap-row {{ display: grid; grid-template-columns: 150px 1fr; gap: 10px; margin-bottom: 15px; }}
            .domain-name {{ font-weight: 500; padding: 10px; }}
            .heatmap-bar {{ display: flex; height: 30px; border-radius: 4px; align-items: center; justify-content: flex-end; padding-right: 10px; color: white; font-weight: 500; }}
            .phase-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); gap: 15px; margin-top: 20px; }}
            .phase-card {{ background: white; padding: 15px; border-radius: 8px; text-align: center; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }}
            .phase-card .status {{ font-size: 0.9em; color: #666; margin-top: 10px; }}
            .status.excellent {{ color: #10B981; }}
            .status.good {{ color: #3B82F6; }}
            .status.acceptable {{ color: #F59E0B; }}
            .status.needs-work {{ color: #EF4444; }}
            .status.critical {{ color: #7C3AED; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>CORTEX Governance Heatmap</h1>
                <p>Real-time compliance and readiness dashboard</p>
            </div>
            
            <div class="stats">
                <div class="stat-card">
                    <div class="stat-value">{heatmap_data["summary"]["coverage_percentage"]}%</div>
                    <div class="stat-label">AC Coverage</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{heatmap_data["summary"]["covered_acs"]}/{heatmap_data["summary"]["total_acs"]}</div>
                    <div class="stat-label">ACs Verified</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{heatmap_data["summary"]["locked_phases"]}</div>
                    <div class="stat-label">Phases Locked</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{heatmap_data["summary"]["total_audit_entries"]}</div>
                    <div class="stat-label">Audit Entries</div>
                </div>
            </div>
            
            <div class="heatmap">
                <h2>Domain Compliance Heatmap</h2>
                {''.join([f'''
                <div class="heatmap-row">
                    <div class="domain-name">{d["domain"]}</div>
                    <div class="heatmap-bar" style="width: {d["coverage_percentage"]}%; background: {d["color"]};">
                        {d["coverage_percentage"]}%
                    </div>
                </div>
                ''' for d in heatmap_data["domains"][:10]])}
            </div>
            
            <div class="phase-grid">
                {''.join([f'''
                <div class="phase-card">
                    <strong>{p["phase"]}</strong>
                    <div style="font-size: 1.5em; margin: 10px 0;">{p["readiness_percentage"]}%</div>
                    <div class="status {p["status"]}">
                        {p["readiness_stage"].replace("_", " ").title()}
                    </div>
                    {'<div style="color: green; margin-top: 5px;">🔒 LOCKED</div>' if p["locked"] else ''}
                </div>
                ''' for p in heatmap_data["phases"]])}
            </div>
        </div>
    </body>
    </html>
    """


if __name__ == "__main__":
    # Generate and display heatmap
    generator = GovernanceHeatmapGenerator()
    heatmap_data = generator.generate_heatmap_data()
    
    print(json.dumps(heatmap_data, indent=2))
