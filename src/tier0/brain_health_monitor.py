"""
Brain Health Monitor

Monitors health and performance of all 3 brain tiers, detects corruption,
generates health reports, and provides CLI dashboard.

Responsibilities:
- Check overall brain health status (healthy/degraded/critical)
- Monitor tier-specific metrics (database size, record counts, FTS5 status)
- Detect database corruption
- Generate human-readable health reports
- Display CLI health dashboard
- Measure query performance

Usage:
    >>> from src.tier0.brain_health_monitor import BrainHealthMonitor
    >>> monitor = BrainHealthMonitor(brain_path="/path/to/cortex-brain")
    >>> health = monitor.check_health()
    >>> print(f"Status: {health['status']}")
    >>> monitor.display_dashboard()

Author: Asif Hussain
Phase: 7.3 - Brain Initialization System
"""

import sqlite3
from pathlib import Path
from typing import Dict, Any
from datetime import datetime
import time


class BrainHealthMonitor:
    """
    Monitors brain health across all 3 tiers.
    
    Provides health checks, corruption detection, reporting,
    and performance monitoring.
    """
    
    def __init__(self, brain_path: str):
        """
        Initialize health monitor with brain path.
        
        Args:
            brain_path: Absolute path to cortex-brain directory
        """
        self.brain_path = Path(brain_path)
        self.tier1_db = self.brain_path / "tier1" / "working_memory.db"
        self.tier2_db = self.brain_path / "tier2" / "knowledge_graph.db"
        self.tier3_db = self.brain_path / "tier3" / "development_context.db"
    
    def check_health(self) -> Dict[str, Any]:
        """
        Check overall brain health.
        
        Aggregates health from all 3 tiers and determines overall status.
        
        Returns:
            Dict with status (healthy/degraded/critical) and tier details
        """
        tier1_health = self.check_tier1()
        tier2_health = self.check_tier2()
        tier3_health = self.check_tier3()
        
        # Determine overall status
        critical_count = sum([
            tier1_health.get('corrupted', False),
            tier2_health.get('corrupted', False),
            tier3_health.get('corrupted', False)
        ])
        
        missing_count = sum([
            not tier1_health.get('database_exists', False),
            not tier2_health.get('database_exists', False),
            not tier3_health.get('database_exists', False)
        ])
        
        if critical_count > 0:
            status = 'critical'
        elif missing_count > 0:
            status = 'degraded'
        else:
            status = 'healthy'
        
        return {
            'status': status,
            'tier1': tier1_health,
            'tier2': tier2_health,
            'tier3': tier3_health,
            'checked_at': datetime.now().isoformat()
        }
    
    def check_tier1(self) -> Dict[str, Any]:
        """
        Check Tier 1 (Working Memory) health.
        
        Returns:
            Dict with database status, version, counts, and size
        """
        if not self.tier1_db.exists():
            return {
                'database_exists': False,
                'schema_version': 0,
                'conversation_count': 0,
                'size_mb': 0
            }
        
        try:
            conn = sqlite3.connect(str(self.tier1_db))
            cursor = conn.cursor()
            
            # Get conversation count
            cursor.execute("SELECT COUNT(*) FROM conversations")
            conversation_count = cursor.fetchone()[0]
            
            # Get schema version
            cursor.execute("""
                SELECT value FROM metadata 
                WHERE key = 'schema_version_tier1'
            """)
            version_row = cursor.fetchone()
            if version_row:
                import json
                schema_version = json.loads(version_row[0])['version']
            else:
                schema_version = 1  # Default
            
            # Get database size
            size_bytes = self.tier1_db.stat().st_size
            size_mb = round(size_bytes / (1024 * 1024), 2)
            
            conn.close()
            
            return {
                'database_exists': True,
                'schema_version': schema_version,
                'conversation_count': conversation_count,
                'size_mb': size_mb,
                'corrupted': False
            }
            
        except (sqlite3.DatabaseError, sqlite3.OperationalError):
            # Database is corrupted
            return {
                'database_exists': True,
                'corrupted': True,
                'error': 'Database corruption detected'
            }
        except Exception as e:
            return {
                'database_exists': True,
                'error': str(e)
            }
    
    def check_tier2(self) -> Dict[str, Any]:
        """
        Check Tier 2 (Knowledge Graph) health.
        
        Returns:
            Dict with database status, pattern/relationship counts, FTS5 status
        """
        if not self.tier2_db.exists():
            return {
                'database_exists': False,
                'pattern_count': 0,
                'relationship_count': 0,
                'fts5_enabled': False
            }
        
        try:
            conn = sqlite3.connect(str(self.tier2_db))
            cursor = conn.cursor()
            
            # Get pattern count
            cursor.execute("SELECT COUNT(*) FROM patterns")
            pattern_count = cursor.fetchone()[0]
            
            # Get relationship count
            cursor.execute("SELECT COUNT(*) FROM relationships")
            relationship_count = cursor.fetchone()[0]
            
            # Check FTS5 enabled
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='pattern_fts'
            """)
            fts5_enabled = cursor.fetchone() is not None
            
            conn.close()
            
            return {
                'database_exists': True,
                'pattern_count': pattern_count,
                'relationship_count': relationship_count,
                'fts5_enabled': fts5_enabled,
                'corrupted': False
            }
            
        except (sqlite3.DatabaseError, sqlite3.OperationalError):
            return {
                'database_exists': True,
                'corrupted': True,
                'error': 'Database corruption detected'
            }
        except Exception as e:
            return {
                'database_exists': True,
                'error': str(e)
            }
    
    def check_tier3(self) -> Dict[str, Any]:
        """
        Check Tier 3 (Development Context) health.
        
        Returns:
            Dict with database status, metrics count, git activity tracking
        """
        if not self.tier3_db.exists():
            return {
                'database_exists': False,
                'metrics_count': 0,
                'git_activity_tracked': False
            }
        
        try:
            conn = sqlite3.connect(str(self.tier3_db))
            cursor = conn.cursor()
            
            # Get metrics count
            cursor.execute("SELECT COUNT(*) FROM code_metrics")
            metrics_count = cursor.fetchone()[0]
            
            # Check if git activity is being tracked
            cursor.execute("SELECT COUNT(*) FROM git_activity")
            git_activity_count = cursor.fetchone()[0]
            git_activity_tracked = git_activity_count > 0
            
            conn.close()
            
            return {
                'database_exists': True,
                'metrics_count': metrics_count,
                'git_activity_tracked': git_activity_tracked,
                'corrupted': False
            }
            
        except (sqlite3.DatabaseError, sqlite3.OperationalError):
            return {
                'database_exists': True,
                'corrupted': True,
                'error': 'Database corruption detected'
            }
        except Exception as e:
            return {
                'database_exists': True,
                'error': str(e)
            }
    
    def generate_report(self) -> str:
        """
        Generate human-readable health report.
        
        Returns:
            Markdown-formatted health report
        """
        health = self.check_health()
        
        report = []
        report.append("# Brain Health Report")
        report.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"**Overall Status:** {health['status'].upper()}")
        report.append("")
        
        # Tier 1 section
        report.append("## Tier 1: Working Memory")
        tier1 = health['tier1']
        if tier1.get('database_exists'):
            if tier1.get('corrupted'):
                report.append("❌ **Status:** CORRUPTED")
            else:
                report.append("✅ **Status:** Healthy")
                report.append(f"- Schema Version: {tier1.get('schema_version', 'Unknown')}")
                report.append(f"- Conversations: {tier1.get('conversation_count', 0)}")
                report.append(f"- Size: {tier1.get('size_mb', 0)} MB")
        else:
            report.append("⚠️ **Status:** Database not found")
        report.append("")
        
        # Tier 2 section
        report.append("## Tier 2: Knowledge Graph")
        tier2 = health['tier2']
        if tier2.get('database_exists'):
            if tier2.get('corrupted'):
                report.append("❌ **Status:** CORRUPTED")
            else:
                report.append("✅ **Status:** Healthy")
                report.append(f"- Patterns: {tier2.get('pattern_count', 0)}")
                report.append(f"- Relationships: {tier2.get('relationship_count', 0)}")
                fts5_status = "Enabled" if tier2.get('fts5_enabled') else "Disabled"
                report.append(f"- FTS5 Search: {fts5_status}")
        else:
            report.append("⚠️ **Status:** Database not found")
        report.append("")
        
        # Tier 3 section
        report.append("## Tier 3: Development Context")
        tier3 = health['tier3']
        if tier3.get('database_exists'):
            if tier3.get('corrupted'):
                report.append("❌ **Status:** CORRUPTED")
            else:
                report.append("✅ **Status:** Healthy")
                report.append(f"- Code Metrics: {tier3.get('metrics_count', 0)}")
                git_status = "Active" if tier3.get('git_activity_tracked') else "Inactive"
                report.append(f"- Git Activity: {git_status}")
        else:
            report.append("⚠️ **Status:** Database not found")
        
        return "\n".join(report)
    
    def display_dashboard(self):
        """
        Display CLI health dashboard.
        
        Prints colored dashboard to stdout.
        """
        health = self.check_health()
        
        print("╔════════════════════════════════════════╗")
        print("║     Brain Health Dashboard             ║")
        print("╚════════════════════════════════════════╝")
        print()
        
        # Overall status
        status_icon = {
            'healthy': '✅',
            'degraded': '⚠️ ',
            'critical': '❌'
        }.get(health['status'], '❓')
        
        print(f"Overall Status: {status_icon} {health['status'].upper()}")
        print()
        
        # Tier 1
        tier1 = health['tier1']
        tier1_icon = '✅' if (tier1.get('database_exists') and not tier1.get('corrupted')) else '❌'
        print(f"{tier1_icon} Tier 1 (Working Memory)")
        if tier1.get('database_exists') and not tier1.get('corrupted'):
            print(f"   └─ Conversations: {tier1.get('conversation_count', 0)}")
        print()
        
        # Tier 2
        tier2 = health['tier2']
        tier2_icon = '✅' if (tier2.get('database_exists') and not tier2.get('corrupted')) else '❌'
        print(f"{tier2_icon} Tier 2 (Knowledge Graph)")
        if tier2.get('database_exists') and not tier2.get('corrupted'):
            print(f"   └─ Patterns: {tier2.get('pattern_count', 0)}")
        print()
        
        # Tier 3
        tier3 = health['tier3']
        tier3_icon = '✅' if (tier3.get('database_exists') and not tier3.get('corrupted')) else '❌'
        print(f"{tier3_icon} Tier 3 (Development Context)")
        if tier3.get('database_exists') and not tier3.get('corrupted'):
            print(f"   └─ Metrics: {tier3.get('metrics_count', 0)}")
        print()
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """
        Get query performance metrics.
        
        Measures average query time for each tier.
        
        Returns:
            Dict with average query times in milliseconds
        """
        metrics = {
            'query_performance': True,
            'tier1_avg_query_ms': 0.0,
            'tier2_avg_query_ms': 0.0,
            'tier3_avg_query_ms': 0.0
        }
        
        # Measure Tier 1
        if self.tier1_db.exists():
            try:
                conn = sqlite3.connect(str(self.tier1_db))
                cursor = conn.cursor()
                
                start = time.perf_counter()
                cursor.execute("SELECT COUNT(*) FROM conversations")
                cursor.fetchone()
                duration_ms = (time.perf_counter() - start) * 1000
                
                metrics['tier1_avg_query_ms'] = round(duration_ms, 2)
                conn.close()
            except:
                metrics['tier1_avg_query_ms'] = 999.99  # Error indicator
        
        # Measure Tier 2
        if self.tier2_db.exists():
            try:
                conn = sqlite3.connect(str(self.tier2_db))
                cursor = conn.cursor()
                
                start = time.perf_counter()
                cursor.execute("SELECT COUNT(*) FROM patterns")
                cursor.fetchone()
                duration_ms = (time.perf_counter() - start) * 1000
                
                metrics['tier2_avg_query_ms'] = round(duration_ms, 2)
                conn.close()
            except:
                metrics['tier2_avg_query_ms'] = 999.99
        
        # Measure Tier 3
        if self.tier3_db.exists():
            try:
                conn = sqlite3.connect(str(self.tier3_db))
                cursor = conn.cursor()
                
                start = time.perf_counter()
                cursor.execute("SELECT COUNT(*) FROM code_metrics")
                cursor.fetchone()
                duration_ms = (time.perf_counter() - start) * 1000
                
                metrics['tier3_avg_query_ms'] = round(duration_ms, 2)
                conn.close()
            except:
                metrics['tier3_avg_query_ms'] = 999.99
        
        return metrics
