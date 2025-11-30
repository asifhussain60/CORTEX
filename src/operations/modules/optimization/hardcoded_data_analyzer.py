"""
Hardcoded Data Analyzer

Scans for hardcoded data violations in CORTEX code.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

import logging
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class HardcodedDataAnalyzer:
    """
    AGGRESSIVE hardcoded data detection.
    
    Scans for:
    - Hardcoded file paths (absolute paths, platform-specific)
    - Mock data in production code
    - Fallback mechanisms returning fake values
    - Test fixtures with hardcoded values
    - Placeholder data masquerading as real data
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize HardcodedDataAnalyzer.
        
        Args:
            project_root: Project root directory
        """
        self.project_root = project_root
    
    def analyze(self) -> Dict[str, Any]:
        """
        Run hardcoded data scan.
        
        Returns:
            Dict with hardcoded data violations
        """
        logger.info("Running AGGRESSIVE hardcoded data scan...")
        
        try:
            from .hardcoded_data_cleaner_module import HardcodedDataCleanerModule
            
            cleaner = HardcodedDataCleanerModule(project_root=self.project_root)
            result = cleaner.execute({
                'project_root': self.project_root,
                'scan_paths': ['src', 'tests'],
                'exclude_patterns': ['__pycache__', '.git', 'dist', '.venv', 'node_modules'],
                'fail_on_critical': False  # Don't fail optimization, just report
            })
            
            if result.success or result.status.name == 'FAILED':  # Both success and fail states have data
                metrics_data = result.data.get('metrics', {})
                violations = result.data.get('violations', [])
                
                insights = []
                issues = []
                
                # Summarize findings
                total_violations = metrics_data.get('violations_found', 0)
                critical = metrics_data.get('critical_violations', 0)
                high = metrics_data.get('high_violations', 0)
                
                if total_violations == 0:
                    insights.append("✅ No hardcoded data violations found!")
                else:
                    if critical > 0:
                        issues.append(f"CRITICAL: {critical} hardcoded paths or mock data in production")
                    if high > 0:
                        issues.append(f"HIGH: {high} fallback values or hardcoded returns")
                    
                    insights.append(f"Scanned {metrics_data.get('files_scanned', 0)} files")
                    insights.append(f"Found {total_violations} violations")
                    
                    # Top violation types
                    violations_by_type = metrics_data.get('violations_by_type', {})
                    for v_type, count in sorted(violations_by_type.items(), key=lambda x: x[1], reverse=True)[:3]:
                        insights.append(f"  - {v_type}: {count}")
                
                logger.info(f"Hardcoded data scan complete: {total_violations} violations")
                
                return {
                    'insights': insights,
                    'issues': issues,
                    'stats': metrics_data,
                    'violations': violations[:10],  # Top 10 violations for context
                    'full_report': result.data.get('report', '')
                }
            else:
                return {'issues': ['Hardcoded data scan failed']}
        
        except ImportError as e:
            logger.warning(f"Hardcoded data cleaner module not available: {e}")
            return {'issues': ['Hardcoded data cleaner not installed']}
        except Exception as e:
            logger.error(f"Error during hardcoded data scan: {e}")
            return {'issues': [f'Hardcoded data scan error: {str(e)}']}
