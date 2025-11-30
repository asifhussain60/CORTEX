#!/usr/bin/env python3
"""
Onboarding Orchestrator

Manages application onboarding workflow including analysis and dashboard data generation.
Triggered when CORTEX onboards a new user application.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import logging
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


@dataclass
class OnboardingResult:
    """Result of application onboarding."""
    success: bool
    project_name: str
    analysis_timestamp: str
    quality_score: float
    security_issues: int
    performance_metrics: int
    dashboard_url: str
    errors: List[str]


class OnboardingOrchestrator:
    """
    Orchestrates application onboarding workflow.
    
    Workflow:
    1. Analyze application (CodeQualityAnalyzer, SecurityScanner, PerformanceMetrics)
    2. Transform analyzer outputs to dashboard format (DashboardDataAdapter)
    3. Generate dashboard data files
    4. Provide dashboard URL to user
    """
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.cortex_root = self._find_cortex_root()
    
    def _find_cortex_root(self) -> Path:
        """Find CORTEX installation root (standalone or embedded)."""
        # Check if we're in a CORTEX subdirectory
        current = self.project_root
        while current.parent != current:
            if (current / "cortex-brain").exists():
                return current
            current = current.parent
        
        # Fallback: assume project_root is CORTEX root
        return self.project_root
    
    def onboard_application(
        self,
        project_path: Path,
        project_name: Optional[str] = None
    ) -> OnboardingResult:
        """
        Onboard user application with full analysis and dashboard generation.
        
        Args:
            project_path: Path to user application to analyze
            project_name: Optional project name (defaults to directory name)
        
        Returns:
            OnboardingResult with success status and dashboard URL
        """
        logger.info(f"Starting application onboarding: {project_path}")
        
        errors = []
        project_name = project_name or project_path.name
        
        try:
            # Step 1: Gather project metadata
            logger.info("Step 1: Gathering project metadata...")
            project_info = self._gather_project_info(project_path, project_name)
            
            # Step 2: Run code quality analysis
            logger.info("Step 2: Running code quality analysis...")
            quality_issues, quality_score = self._run_quality_analysis(project_path)
            
            # Step 3: Run security scan
            logger.info("Step 3: Running security scan...")
            vulnerabilities = self._run_security_scan(project_path)
            
            # Step 4: Collect performance metrics
            logger.info("Step 4: Collecting performance metrics...")
            metrics = self._collect_performance_metrics(project_path)
            
            # Step 5: Generate dashboard data
            logger.info("Step 5: Generating dashboard data...")
            dashboard_url = self._generate_dashboard_data(
                project_info,
                quality_issues,
                quality_score,
                vulnerabilities,
                metrics
            )
            
            logger.info(f"✅ Onboarding complete! Dashboard: {dashboard_url}")
            
            return OnboardingResult(
                success=True,
                project_name=project_name,
                analysis_timestamp=datetime.now().isoformat(),
                quality_score=quality_score,
                security_issues=len(vulnerabilities),
                performance_metrics=len(metrics),
                dashboard_url=dashboard_url,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"❌ Onboarding failed: {e}")
            errors.append(str(e))
            
            return OnboardingResult(
                success=False,
                project_name=project_name,
                analysis_timestamp=datetime.now().isoformat(),
                quality_score=0.0,
                security_issues=0,
                performance_metrics=0,
                dashboard_url="",
                errors=errors
            )
    
    def _gather_project_info(self, project_path: Path, project_name: str) -> Dict[str, Any]:
        """Gather basic project metadata."""
        # Count files and lines
        total_files = 0
        total_lines = 0
        languages = set()
        
        # Language detection by extension
        extension_map = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.ts': 'TypeScript',
            '.cs': 'C#',
            '.java': 'Java',
            '.go': 'Go',
            '.rb': 'Ruby',
            '.php': 'PHP'
        }
        
        for file_path in project_path.rglob('*'):
            if file_path.is_file():
                total_files += 1
                
                # Count lines
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        total_lines += sum(1 for _ in f)
                except:
                    pass
                
                # Detect language
                ext = file_path.suffix.lower()
                if ext in extension_map:
                    languages.add(extension_map[ext])
        
        return {
            "name": project_name,
            "version": "1.0.0",  # TODO: Detect from package files
            "files": total_files,
            "lines": total_lines,
            "languages": sorted(list(languages))
        }
    
    def _run_quality_analysis(self, project_path: Path):
        """Run CodeQualityAnalyzer on project."""
        try:
            # Import analyzer
            import sys
            sys.path.insert(0, str(self.cortex_root / "src"))
            from agents.optimization_health_monitor import CodeQualityAnalyzer, CodeQualityIssue
            
            analyzer = CodeQualityAnalyzer()
            
            # Analyze all Python files (extend for other languages)
            quality_issues = []
            for file_path in project_path.rglob('*.py'):
                try:
                    issues = analyzer.analyze_file(file_path)
                    quality_issues.extend(issues)
                except Exception as e:
                    logger.warning(f"Failed to analyze {file_path}: {e}")
            
            # Calculate overall score (0-100)
            # Simple formula: 100 - (issues * penalty)
            critical_count = sum(1 for i in quality_issues if getattr(i, 'severity', '') == 'critical')
            high_count = sum(1 for i in quality_issues if getattr(i, 'severity', '') == 'high')
            medium_count = sum(1 for i in quality_issues if getattr(i, 'severity', '') == 'medium')
            
            penalty = (critical_count * 10) + (high_count * 5) + (medium_count * 2)
            quality_score = max(0.0, min(100.0, 100.0 - penalty))
            
            return quality_issues, quality_score
            
        except ImportError as e:
            logger.error(f"Failed to import CodeQualityAnalyzer: {e}")
            return [], 50.0  # Default score if analyzer unavailable
        except Exception as e:
            logger.error(f"Quality analysis failed: {e}")
            return [], 50.0
    
    def _run_security_scan(self, project_path: Path):
        """Run SecurityScanner on project."""
        try:
            # Import scanner
            import sys
            sys.path.insert(0, str(self.cortex_root / "src"))
            from plugins.code_review_plugin import SecurityScanner
            
            scanner = SecurityScanner()
            
            # Scan all files
            vulnerabilities = []
            for file_path in project_path.rglob('*'):
                if file_path.is_file():
                    try:
                        vulns = scanner.scan_file(file_path)
                        vulnerabilities.extend(vulns)
                    except Exception as e:
                        logger.warning(f"Failed to scan {file_path}: {e}")
            
            return vulnerabilities
            
        except ImportError as e:
            logger.error(f"Failed to import SecurityScanner: {e}")
            return []
        except Exception as e:
            logger.error(f"Security scan failed: {e}")
            return []
    
    def _collect_performance_metrics(self, project_path: Path):
        """Collect performance metrics from project."""
        try:
            # Import performance telemetry
            import sys
            sys.path.insert(0, str(self.cortex_root / "src"))
            from plugins.performance_telemetry_plugin import PerformanceTelemetry
            
            telemetry = PerformanceTelemetry()
            
            # Collect metrics
            metrics = telemetry.collect_metrics(project_path)
            
            return metrics
            
        except ImportError as e:
            logger.error(f"Failed to import PerformanceTelemetry: {e}")
            return []
        except Exception as e:
            logger.error(f"Performance metrics collection failed: {e}")
            return []
    
    def _generate_dashboard_data(
        self,
        project_info: Dict[str, Any],
        quality_issues: List[Any],
        quality_score: float,
        vulnerabilities: List[Any],
        metrics: List[Any]
    ) -> str:
        """Generate dashboard data using DashboardDataAdapter."""
        try:
            # Import adapter
            import sys
            sys.path.insert(0, str(self.cortex_root / "src"))
            from operations.dashboard_data_adapter import DashboardDataAdapter
            
            adapter = DashboardDataAdapter(self.cortex_root)
            
            # Generate full dashboard data
            adapter.generate_full_dashboard_data(
                project_info,
                quality_issues,
                quality_score,
                vulnerabilities,
                metrics
            )
            
            # Return dashboard URL
            dashboard_path = self.cortex_root / "cortex-brain" / "documents" / "analysis" / "dashboard" / "dashboard.html"
            
            # Return relative URL for local viewing
            return f"file://{dashboard_path}"
            
        except ImportError as e:
            logger.error(f"Failed to import DashboardDataAdapter: {e}")
            raise
        except Exception as e:
            logger.error(f"Dashboard data generation failed: {e}")
            raise


def main():
    """CLI entry point for testing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Onboard application to CORTEX")
    parser.add_argument("project_path", type=Path, help="Path to application to onboard")
    parser.add_argument("--name", help="Project name (defaults to directory name)")
    
    args = parser.parse_args()
    
    orchestrator = OnboardingOrchestrator(Path.cwd())
    result = orchestrator.onboard_application(args.project_path, args.name)
    
    if result.success:
        print(f"✅ Onboarding successful!")
        print(f"   Project: {result.project_name}")
        print(f"   Quality Score: {result.quality_score:.1f}/100")
        print(f"   Security Issues: {result.security_issues}")
        print(f"   Performance Metrics: {result.performance_metrics}")
        print(f"   Dashboard: {result.dashboard_url}")
    else:
        print(f"❌ Onboarding failed:")
        for error in result.errors:
            print(f"   • {error}")
        return 1
    
    return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
