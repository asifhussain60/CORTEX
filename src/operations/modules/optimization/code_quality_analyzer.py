"""
Code Quality Analyzer

Analyzes code quality metrics using CORTEX admin optimizer.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0
"""

import logging
import subprocess
import json
from pathlib import Path
from typing import Dict, Any

logger = logging.getLogger(__name__)


class CodeQualityAnalyzer:
    """
    Analyzes code quality metrics using CORTEX admin optimizer.
    
    Runs the comprehensive CORTEX optimizer tool which provides:
    - Token usage analysis (prompt efficiency, YAML optimization)
    - YAML validation (brain file integrity, schema compliance)
    - Plugin health checks (metadata completeness, registration)
    - Database optimization (SQLite performance, indexes)
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize CodeQualityAnalyzer.
        
        Args:
            project_root: Project root directory
        """
        self.project_root = project_root
    
    def analyze(self) -> Dict[str, Any]:
        """
        Run code quality analysis.
        
        Returns:
            Dict with insights, issues, and stats
        """
        insights = []
        issues = []
        stats = {}
        
        logger.info("Running CORTEX admin optimizer for code quality metrics...")
        
        try:
            # Run the admin optimizer tool
            result = subprocess.run(
                ['python', 'scripts/admin/cortex_optimizer.py', 'analyze', '--report', 'json'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                # Parse JSON output
                try:
                    optimizer_results = json.loads(result.stdout)
                    overall_score = optimizer_results.get('overall_score', 0)
                    
                    insights.append(f"Overall optimization score: {overall_score}/100")
                    
                    # Process individual analyzer results
                    for analyzer_result in optimizer_results.get('results', []):
                        category = analyzer_result.get('category', 'Unknown')
                        score = analyzer_result.get('score', 0)
                        analyzer_issues = analyzer_result.get('issues', [])
                        recommendations = analyzer_result.get('recommendations', [])
                        
                        # Add score to insights
                        status_emoji = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
                        insights.append(f"{status_emoji} {category}: {score}/100")
                        
                        # Add issues
                        if analyzer_issues:
                            issues.extend(analyzer_issues[:3])  # Top 3 issues per category
                        
                        # Store stats
                        stats[category.lower().replace(' ', '_')] = {
                            'score': score,
                            'issue_count': len(analyzer_issues),
                            'recommendations': len(recommendations)
                        }
                    
                    # Overall health
                    if overall_score < 60:
                        issues.append(f"CRITICAL: Overall optimization score below 60 ({overall_score}/100)")
                    elif overall_score < 80:
                        issues.append(f"WARNING: Overall optimization score below 80 ({overall_score}/100)")
                    
                except json.JSONDecodeError as e:
                    logger.warning(f"Failed to parse optimizer JSON output: {e}")
                    insights.append("Optimizer ran but output parse failed")
            else:
                # Optimizer failed, fall back to basic analysis
                logger.warning(f"CORTEX optimizer failed (exit code {result.returncode}), using fallback analysis")
                insights.append("⚠️ Optimizer failed, using basic analysis")
                
                # Fallback: Basic file counting
                src_dir = self.project_root / 'src'
                if src_dir.exists():
                    py_files = list(src_dir.rglob('*.py'))
                    insights.append(f"{len(py_files)} Python files")
                    
                    init_files = list(src_dir.rglob('__init__.py'))
                    insights.append(f"{len(init_files)} package markers")
                    
                    stats = {
                        'python_files': len(py_files),
                        'packages': len(init_files)
                    }
                else:
                    issues.append("Source directory not found")
        
        except subprocess.TimeoutExpired:
            logger.error("CORTEX optimizer timed out")
            issues.append("Optimizer execution timeout")
        except Exception as e:
            logger.error(f"Error running CORTEX optimizer: {e}")
            issues.append(f"Optimizer error: {str(e)}")
        
        return {
            'insights': insights,
            'issues': issues,
            'stats': stats
        }
