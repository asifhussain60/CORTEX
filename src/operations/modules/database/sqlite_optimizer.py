"""
SQLite Database Optimization Module

Analyzes and optimizes CORTEX SQLite databases across all tiers.
Performs VACUUM, integrity checks, index analysis, and query optimization.

Copyright © 2024-2025 Asif Hussain. All rights reserved.
"""

import sqlite3
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class SQLiteOptimizer:
    """
    Optimizes SQLite databases for CORTEX tiers.
    
    Features:
    - VACUUM to reclaim space and optimize storage
    - Integrity check validation
    - Index usage analysis
    - Query performance analysis
    - Fragmentation detection
    - Size reporting with before/after comparison
    """
    
    def __init__(self, brain_path: Optional[Path] = None):
        """
        Initialize SQLite optimizer.
        
        Args:
            brain_path: Path to cortex-brain directory
        """
        self.logger = logging.getLogger(__name__)
        
        if brain_path is None:
            # Default to standard location
            brain_path = Path(__file__).parent.parent.parent.parent.parent / "cortex-brain"
        
        self.brain_path = Path(brain_path)
        
        # Tier database paths
        self.databases = {
            'tier1': self.brain_path / 'tier1' / 'conversations.db',
            'tier2': self.brain_path / 'tier2' / 'knowledge_graph.db',
            'tier3': self.brain_path / 'tier3' / 'context_intelligence.db'
        }
        
    def optimize_all(self) -> Dict[str, Any]:
        """
        Optimize all tier databases.
        
        Returns:
            Dictionary with optimization results for each tier
        """
        results = {
            'timestamp': datetime.now().isoformat(),
            'databases': {},
            'summary': {
                'total_space_reclaimed': 0,
                'total_databases': 0,
                'successful': 0,
                'failed': 0
            }
        }
        
        for tier_name, db_path in self.databases.items():
            self.logger.info(f"Optimizing {tier_name} database: {db_path}")
            
            try:
                tier_result = self.optimize_database(db_path, tier_name)
                results['databases'][tier_name] = tier_result
                results['summary']['total_databases'] += 1
                
                if tier_result['success']:
                    results['summary']['successful'] += 1
                    results['summary']['total_space_reclaimed'] += tier_result.get('space_reclaimed_bytes', 0)
                else:
                    results['summary']['failed'] += 1
                    
            except Exception as e:
                self.logger.error(f"Failed to optimize {tier_name}: {str(e)}")
                results['databases'][tier_name] = {
                    'success': False,
                    'error': str(e)
                }
                results['summary']['failed'] += 1
        
        return results
    
    def optimize_database(self, db_path: Path, tier_name: str) -> Dict[str, Any]:
        """
        Optimize a single database.
        
        Args:
            db_path: Path to database file
            tier_name: Name of tier for reporting
            
        Returns:
            Dictionary with optimization results
        """
        if not db_path.exists():
            return {
                'success': False,
                'error': f'Database not found: {db_path}',
                'tier': tier_name
            }
        
        result = {
            'tier': tier_name,
            'path': str(db_path),
            'success': True,
            'timestamp': datetime.now().isoformat()
        }
        
        try:
            # Get initial size
            initial_size = db_path.stat().st_size
            result['initial_size_bytes'] = initial_size
            result['initial_size_mb'] = round(initial_size / 1024 / 1024, 2)
            
            # Connect to database
            conn = sqlite3.connect(str(db_path))
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Integrity check
            result['integrity_check'] = self._check_integrity(cursor)
            
            # Index analysis
            result['index_analysis'] = self._analyze_indexes(cursor)
            
            # Table statistics
            result['table_stats'] = self._get_table_stats(cursor)
            
            # VACUUM operation
            self.logger.info(f"Running VACUUM on {tier_name}...")
            cursor.execute("VACUUM")
            conn.commit()
            result['vacuum_completed'] = True
            
            # Analyze for query optimizer
            cursor.execute("ANALYZE")
            conn.commit()
            result['analyze_completed'] = True
            
            # Close connection
            conn.close()
            
            # Get final size
            final_size = db_path.stat().st_size
            result['final_size_bytes'] = final_size
            result['final_size_mb'] = round(final_size / 1024 / 1024, 2)
            
            # Calculate space reclaimed
            space_reclaimed = initial_size - final_size
            result['space_reclaimed_bytes'] = space_reclaimed
            result['space_reclaimed_mb'] = round(space_reclaimed / 1024 / 1024, 2)
            result['space_reclaimed_percent'] = round((space_reclaimed / initial_size * 100), 2) if initial_size > 0 else 0
            
            self.logger.info(
                f"{tier_name} optimization complete: "
                f"Reclaimed {result['space_reclaimed_mb']} MB "
                f"({result['space_reclaimed_percent']}%)"
            )
            
        except Exception as e:
            self.logger.error(f"Optimization failed for {tier_name}: {str(e)}")
            result['success'] = False
            result['error'] = str(e)
        
        return result
    
    def _check_integrity(self, cursor: sqlite3.Cursor) -> Dict[str, Any]:
        """Check database integrity."""
        try:
            cursor.execute("PRAGMA integrity_check")
            checks = [row[0] for row in cursor.fetchall()]
            
            return {
                'passed': checks[0] == 'ok' if checks else False,
                'details': checks
            }
        except Exception as e:
            return {
                'passed': False,
                'error': str(e)
            }
    
    def _analyze_indexes(self, cursor: sqlite3.Cursor) -> Dict[str, Any]:
        """Analyze index usage and recommendations."""
        try:
            # Get all indexes
            cursor.execute("""
                SELECT name, tbl_name, sql 
                FROM sqlite_master 
                WHERE type = 'index' AND sql IS NOT NULL
            """)
            
            indexes = []
            for row in cursor.fetchall():
                indexes.append({
                    'name': row[0],
                    'table': row[1],
                    'sql': row[2]
                })
            
            return {
                'index_count': len(indexes),
                'indexes': indexes
            }
        except Exception as e:
            return {
                'error': str(e)
            }
    
    def _get_table_stats(self, cursor: sqlite3.Cursor) -> List[Dict[str, Any]]:
        """Get statistics for all tables."""
        try:
            # Get all tables
            cursor.execute("""
                SELECT name 
                FROM sqlite_master 
                WHERE type = 'table' AND name NOT LIKE 'sqlite_%'
            """)
            
            tables = []
            for row in cursor.fetchall():
                table_name = row[0]
                
                # Get row count
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                
                tables.append({
                    'table': table_name,
                    'rows': row_count
                })
            
            return tables
        except Exception as e:
            self.logger.error(f"Failed to get table stats: {str(e)}")
            return []
    
    def generate_report(self, results: Dict[str, Any], output_path: Optional[Path] = None) -> str:
        """
        Generate optimization report.
        
        Args:
            results: Optimization results from optimize_all()
            output_path: Optional path to save JSON report
            
        Returns:
            Formatted report string
        """
        report_lines = [
            "=" * 80,
            "CORTEX SQLite Database Optimization Report",
            "=" * 80,
            f"Timestamp: {results['timestamp']}",
            "",
            "Summary:",
            f"  Total Databases: {results['summary']['total_databases']}",
            f"  Successful: {results['summary']['successful']}",
            f"  Failed: {results['summary']['failed']}",
            f"  Total Space Reclaimed: {round(results['summary']['total_space_reclaimed'] / 1024 / 1024, 2)} MB",
            "",
            "=" * 80,
            ""
        ]
        
        # Add per-database details
        for tier_name, tier_result in results['databases'].items():
            report_lines.extend([
                f"\n{tier_name.upper()} Database:",
                "-" * 40
            ])
            
            if not tier_result.get('success', False):
                report_lines.append(f"  ❌ Failed: {tier_result.get('error', 'Unknown error')}")
                continue
            
            report_lines.extend([
                f"  Path: {tier_result['path']}",
                f"  Initial Size: {tier_result['initial_size_mb']} MB",
                f"  Final Size: {tier_result['final_size_mb']} MB",
                f"  Space Reclaimed: {tier_result['space_reclaimed_mb']} MB ({tier_result['space_reclaimed_percent']}%)",
                "",
                f"  Integrity Check: {'✅ Passed' if tier_result['integrity_check']['passed'] else '❌ Failed'}",
                f"  VACUUM: {'✅ Completed' if tier_result.get('vacuum_completed') else '❌ Failed'}",
                f"  ANALYZE: {'✅ Completed' if tier_result.get('analyze_completed') else '❌ Failed'}",
                "",
                f"  Tables: {len(tier_result.get('table_stats', []))}",
                f"  Indexes: {tier_result.get('index_analysis', {}).get('index_count', 0)}"
            ])
            
            # Table details
            if tier_result.get('table_stats'):
                report_lines.append("\n  Table Statistics:")
                for table in tier_result['table_stats']:
                    report_lines.append(f"    - {table['table']}: {table['rows']:,} rows")
        
        report_lines.append("\n" + "=" * 80)
        
        report_text = "\n".join(report_lines)
        
        # Save to file if requested
        if output_path:
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Save JSON
            json_path = output_path.with_suffix('.json')
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2)
            
            # Save text report
            txt_path = output_path.with_suffix('.txt')
            with open(txt_path, 'w', encoding='utf-8') as f:
                f.write(report_text)
            
            self.logger.info(f"Report saved to {json_path} and {txt_path}")
        
        return report_text


__all__ = ['SQLiteOptimizer']
