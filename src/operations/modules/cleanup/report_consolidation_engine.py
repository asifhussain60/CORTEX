"""
Report Consolidation Engine for CORTEX Cleanup

Consolidates duplicate and redundant reports into single comprehensive documents.
Handles system alignment reports, deployment validation, cleanup reports, etc.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, List, Set, Tuple, Optional
from datetime import datetime
from collections import defaultdict
import json
import hashlib
import logging

logger = logging.getLogger(__name__)


class ReportConsolidationEngine:
    """
    Consolidates duplicate and time-series reports.
    
    Strategies:
    1. Time-series consolidation (same type, different dates)
    2. Duplicate detection (identical content)
    3. Archive old versions (keep N most recent)
    """
    
    def __init__(self, reports_dir: Path):
        self.reports_dir = reports_dir
        self.consolidated_count = 0
        self.archived_count = 0
        
    def discover_reports(self) -> Dict[str, List[Path]]:
        """
        Discover all report files grouped by type.
        
        Returns:
            Dict mapping report_type -> list of report files
        """
        report_groups = defaultdict(list)
        
        if not self.reports_dir.exists():
            logger.warning(f"Reports directory does not exist: {self.reports_dir}")
            return {}
        
        # Scan for report files
        for report_file in self.reports_dir.rglob('*'):
            if not report_file.is_file():
                continue
            
            # Categorize by report type
            report_type = self._classify_report(report_file)
            if report_type:
                report_groups[report_type].append(report_file)
        
        return report_groups
    
    def analyze_consolidation_opportunities(
        self,
        report_groups: Dict[str, List[Path]],
        keep_count: int = 5
    ) -> Dict[str, Dict]:
        """
        Analyze which reports can be consolidated or archived.
        
        Args:
            report_groups: Report files grouped by type
            keep_count: Number of recent reports to keep per type
            
        Returns:
            Dict with consolidation recommendations
        """
        recommendations = {}
        
        for report_type, files in report_groups.items():
            if len(files) <= keep_count:
                continue
            
            # Sort by modification time (newest first)
            sorted_files = sorted(files, key=lambda f: f.stat().st_mtime, reverse=True)
            
            keep_files = sorted_files[:keep_count]
            archive_files = sorted_files[keep_count:]
            
            # Calculate space savings
            total_size = sum(f.stat().st_size for f in archive_files)
            
            recommendations[report_type] = {
                'total_count': len(files),
                'keep_count': len(keep_files),
                'archive_count': len(archive_files),
                'keep_files': keep_files,
                'archive_files': archive_files,
                'space_savings_mb': total_size / (1024 * 1024)
            }
        
        return recommendations
    
    def execute_consolidation(
        self,
        recommendations: Dict[str, Dict],
        dry_run: bool = True
    ) -> Dict[str, int]:
        """
        Execute consolidation by archiving old reports.
        
        Args:
            recommendations: From analyze_consolidation_opportunities()
            dry_run: If True, only simulate
            
        Returns:
            Dict with execution stats
        """
        stats = {
            'archived_count': 0,
            'space_freed_mb': 0.0,
            'types_processed': 0
        }
        
        archive_base = self.reports_dir / '.archive'
        
        for report_type, recs in recommendations.items():
            archive_dir = archive_base / report_type
            
            if not dry_run:
                archive_dir.mkdir(parents=True, exist_ok=True)
            
            for old_report in recs['archive_files']:
                if not dry_run:
                    # Move to archive
                    archive_path = archive_dir / old_report.name
                    old_report.rename(archive_path)
                    logger.info(f"  ✓ Archived {old_report.name}")
                else:
                    logger.info(f"  [DRY RUN] Would archive {old_report.name}")
                
                stats['archived_count'] += 1
            
            stats['space_freed_mb'] += recs['space_savings_mb']
            stats['types_processed'] += 1
        
        self.archived_count = stats['archived_count']
        
        return stats
    
    def generate_consolidation_summary(
        self,
        report_groups: Dict[str, List[Path]],
        recommendations: Dict[str, Dict]
    ) -> str:
        """Generate human-readable summary of consolidation"""
        
        lines = [
            "# Report Consolidation Summary",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "",
            "## Overview",
            f"- Total report types: {len(report_groups)}",
            f"- Types to consolidate: {len(recommendations)}",
            "",
            "## Consolidation Plan",
            ""
        ]
        
        for report_type, recs in sorted(recommendations.items()):
            lines.extend([
                f"### {report_type}",
                f"- Total files: {recs['total_count']}",
                f"- Keep recent: {recs['keep_count']}",
                f"- Archive old: {recs['archive_count']}",
                f"- Space savings: {recs['space_savings_mb']:.2f}MB",
                ""
            ])
        
        total_archived = sum(r['archive_count'] for r in recommendations.values())
        total_space = sum(r['space_savings_mb'] for r in recommendations.values())
        
        lines.extend([
            "## Summary",
            f"- **Total files to archive:** {total_archived}",
            f"- **Total space to free:** {total_space:.2f}MB",
            ""
        ])
        
        return '\n'.join(lines)
    
    def _classify_report(self, report_file: Path) -> Optional[str]:
        """Classify report type from filename"""
        
        name_lower = report_file.name.lower()
        
        # Pattern matching for report types
        patterns = {
            'system-alignment': ['system-alignment', 'alignment'],
            'system-maintenance': ['system-maintenance', 'maintenance'],
            'deployment-validation': ['deployment-validation', 'deploy-validation'],
            'architectural-review': ['architectural-review', 'arch-review'],
            'cleanup-execution': ['cleanup-', 'cleanup-dryrun'],
            'optimization': ['optimization-report'],
            'test-results': ['test-results', 'test-report'],
            'phase-reports': ['phase-', 'sprint-']
        }
        
        for report_type, keywords in patterns.items():
            if any(kw in name_lower for kw in keywords):
                return report_type
        
        return None
