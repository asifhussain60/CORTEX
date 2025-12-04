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
    output_path: Optional[Path] = None  # Path where results were written


class OnboardingOrchestrator:
    """
    Orchestrates application onboarding workflow.
    
    Workflow:
    1. Analyze application (CodeQualityAnalyzer, SecurityScanner, PerformanceMetrics)
    2. Transform analyzer outputs to dashboard format (DashboardDataAdapter)
    3. Generate dashboard data files
    4. Provide dashboard URL to user
    
    Modes:
    - Production mode (test_mode=False): Embedded in user repo, standard output paths
    - Testing mode (test_mode=True): Standalone CORTEX testing external repos,
      outputs to cortex-brain/documents/onboarded-apps/{project-name}/
    """
    
    def __init__(self, project_root: Path, test_mode: bool = False):
        """
        Initialize onboarding orchestrator.
        
        Args:
            project_root: Path to project root (CORTEX root in test mode, user repo in production)
            test_mode: If True, outputs to onboarded-apps/ for testing. If False, standard production paths.
        """
        self.project_root = project_root
        self.test_mode = test_mode
        self.cortex_root = self._find_cortex_root()
        
        logger.info(f"OnboardingOrchestrator initialized")
        logger.info(f"  Mode: {'TEST' if test_mode else 'PRODUCTION'}")
        logger.info(f"  Project Root: {self.project_root}")
        logger.info(f"  CORTEX Root: {self.cortex_root}")
    
    def _find_cortex_root(self) -> Path:
        """Find CORTEX installation root (standalone or embedded)."""
        # In test mode, project_root IS the cortex root
        if self.test_mode:
            if (self.project_root / "cortex-brain").exists():
                return self.project_root
            else:
                raise ValueError(f"Test mode requires cortex-brain in {self.project_root}")
        
        # Production mode: search upwards from user project
        current = self.project_root
        while current.parent != current:
            if (current / "cortex-brain").exists():
                return current
            current = current.parent
        
        # Fallback: assume project_root is CORTEX root
        return self.project_root
    
    def _should_scan_file(self, file_path: Path) -> bool:
        """
        Determine if file should be scanned during analysis.
        
        Excludes:
        - Hidden directories (.git, .venv, .pytest_cache, etc.)
        - Build artifacts (__pycache__, node_modules, dist, build)
        - Binary files (.pyc, .so, .dll, .exe)
        - Large data files (.pack, .idx)
        
        Args:
            file_path: Path to check
        
        Returns:
            True if file should be scanned, False otherwise
        """
        # Convert to string for pattern matching
        path_str = str(file_path)
        
        # Exclude patterns (gitignore-style)
        exclude_patterns = [
            '/.git/',
            '/.venv/',
            '/venv/',
            '/.env/',
            '/__pycache__/',
            '/.pytest_cache/',
            '/node_modules/',
            '/.tox/',
            '/dist/',
            '/build/',
            '/.egg-info/',
            '/.mypy_cache/',
            '/.coverage',
            '/htmlcov/',
            '/.idea/',
            '/.vscode/',
            '/.vs/',
            '/bin/',
            '/obj/',
        ]
        
        # Check if path contains any exclude pattern
        for pattern in exclude_patterns:
            if pattern in path_str.replace('\\', '/'):
                return False
        
        # Exclude binary extensions
        binary_extensions = {
            '.pyc', '.pyo', '.pyd', '.so', '.dll', '.exe', '.bin',
            '.pack', '.idx', '.rev', '.db', '.sqlite', '.sqlite3'
        }
        
        if file_path.suffix.lower() in binary_extensions:
            return False
        
        # Include only specific source code extensions (if extension present)
        if file_path.suffix:
            source_extensions = {
                '.py', '.js', '.ts', '.jsx', '.tsx',
                '.cs', '.java', '.go', '.rb', '.php',
                '.cpp', '.c', '.h', '.hpp',
                '.rs', '.swift', '.kt', '.scala',
                '.sql', '.yaml', '.yml', '.json', '.xml',
                '.md', '.txt', '.sh', '.ps1', '.bat'
            }
            return file_path.suffix.lower() in source_extensions
        
        return True  # Include files without extension
    
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
            
            # Step 5: Generate architecture graph
            logger.info("Step 5: Generating architecture graph...")
            architecture = self._generate_architecture_graph(project_path)
            
            # Step 6: Analyze technology stack
            logger.info("Step 6: Analyzing technology stack...")
            tech_stack = self._analyze_tech_stack(project_path)
            
            # Step 7: Generate recommendations
            logger.info("Step 7: Generating recommendations...")
            recommendations = self._generate_recommendations(
                vulnerabilities, quality_issues, tech_stack, architecture
            )
            
            # Step 8: Generate UML diagrams
            logger.info("Step 8: Generating UML diagrams...")
            uml_diagram = self._generate_uml_diagram(project_path)
            
            # Step 9: Generate interactive dashboard...
            logger.info("Step 9: Generating interactive dashboard...")
            dashboard_url, output_path = self._generate_dashboard_html(
                project_info,
                quality_issues,
                quality_score,
                vulnerabilities,
                metrics,
                architecture,
                tech_stack,
                recommendations,
                uml_diagram,
                project_name
            )
            
            # Step 10: Validate dashboard functionality
            logger.info("Step 10: Validating dashboard functionality...")
            validation_success, validation_report = self._validate_dashboard(output_path)
            
            if not validation_success:
                logger.warning("⚠️ Dashboard validation found issues")
                logger.warning(f"Errors: {validation_report['summary']['errors']}")
                logger.warning(f"Warnings: {validation_report['summary']['warnings']}")
                
                # Save validation report
                report_path = output_path / 'dashboard_validation_report.json'
                import json
                with open(report_path, 'w', encoding='utf-8') as f:
                    json.dump(validation_report, f, indent=2)
                logger.info(f"Validation report saved: {report_path}")
            else:
                logger.info("✅ Dashboard validation passed all tests")
            
            logger.info(f"✅ Onboarding complete! Dashboard: {dashboard_url}")
            
            return OnboardingResult(
                success=True,
                project_name=project_name,
                analysis_timestamp=datetime.now().isoformat(),
                quality_score=quality_score,
                security_issues=len(vulnerabilities),
                performance_metrics=len(metrics),
                dashboard_url=dashboard_url,
                errors=errors,
                output_path=output_path
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
                errors=errors,
                output_path=None
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
            if file_path.is_file() and self._should_scan_file(file_path):
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
            import sys
            sys.path.insert(0, str(self.cortex_root / "src"))
            from agents.optimization_health_monitor import CodeQualityAnalyzer, CodeQualityIssue
            
            # Note: CodeQualityAnalyzer.analyze_quality() requires ImplementationData
            # For onboarding, we'll do simplified file-level quality checks
            
            # Analyze all Python files (extend for other languages)
            quality_issues = []
            total_files = 0
            for file_path in project_path.rglob('*.py'):
                if self._should_scan_file(file_path):
                    total_files += 1
                    try:
                        # Simple quality checks: file size, complexity indicators
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            lines = content.splitlines()
                            
                            # Check file size
                            if len(lines) > 500:
                                quality_issues.append(type('Issue', (), {
                                    'severity': 'medium',
                                    'description': f'Large file ({len(lines)} lines)',
                                    'file_path': str(file_path)
                                })())
                            
                            # Check for TODO/FIXME
                            if 'TODO' in content or 'FIXME' in content:
                                quality_issues.append(type('Issue', (), {
                                    'severity': 'low',
                                    'description': 'Contains TODO/FIXME comments',
                                    'file_path': str(file_path)
                                })())
                                
                    except Exception as e:
                        logger.warning(f"Failed to analyze {file_path}: {e}")
            
            # Simple formula: 100 - (issues * penalty)
            critical_count = sum(1 for i in quality_issues if getattr(i, 'severity', '') == 'critical')
            high_count = sum(1 for i in quality_issues if getattr(i, 'severity', '') == 'high')
            medium_count = sum(1 for i in quality_issues if getattr(i, 'severity', '') == 'medium')
            
            penalty = (critical_count * 10) + (high_count * 5) + (medium_count * 2)
            quality_score = max(0.0, min(100.0, 100.0 - penalty))
            
            logger.info(f"Quality analysis complete: {total_files} files analyzed, {len(quality_issues)} issues found")
            
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
            import sys
            sys.path.insert(0, str(self.cortex_root / "src"))
            from plugins.code_review_plugin import SecurityScanner
            
            scanner = SecurityScanner()
            
            # Scan all source files
            vulnerabilities = []
            for file_path in project_path.rglob('*'):
                if file_path.is_file() and self._should_scan_file(file_path):
                    try:
                        # Read file content
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                        
                        # Determine language from extension
                        ext_to_lang = {
                            '.py': 'python', '.js': 'javascript', '.ts': 'typescript',
                            '.cs': 'csharp', '.java': 'java', '.php': 'php'
                        }
                        language = ext_to_lang.get(file_path.suffix.lower(), 'unknown')
                        
                        # Scan file (correct API: scan(file_path, content, language))
                        vulns = scanner.scan(str(file_path), content, language)
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
            # Import performance telemetry (correct class name: PerformanceTelemetryPlugin)
            import sys
            sys.path.insert(0, str(self.cortex_root / "src"))
            
            # Placeholder: PerformanceTelemetryPlugin tracks CORTEX operations, not external code
            # For onboarding, we return empty metrics (could be extended to measure analysis time)
            return []
            
        except Exception as e:
            logger.error(f"Performance metrics collection failed: {e}")
            return []
    
    def _generate_architecture_graph(self, project_path: Path) -> Dict[str, Any]:
        """Generate architecture graph using ArchitectureGraphBuilder."""
        try:
            import sys
            sys.path.insert(0, str(self.cortex_root / "src"))
            from operations.architecture_graph_builder import ArchitectureGraphBuilder
            
            builder = ArchitectureGraphBuilder(project_path)
            
            # Find Python files to analyze
            python_files = [
                f for f in project_path.rglob('*.py')
                if self._should_scan_file(f)
            ]
            
            logger.info(f"Building architecture graph from {len(python_files)} Python files...")
            architecture = builder.build_graph(python_files)
            
            return architecture
            
        except Exception as e:
            logger.error(f"Architecture graph generation failed: {e}")
            return {'nodes': [], 'links': [], 'metadata': {}}
    
    def _analyze_tech_stack(self, project_path: Path) -> Dict[str, Any]:
        """Analyze technology stack using TechStackAnalyzer."""
        try:
            import sys
            sys.path.insert(0, str(self.cortex_root / "src"))
            from operations.techstack_analyzer import TechStackAnalyzer
            
            analyzer = TechStackAnalyzer(project_path)
            tech_stack = analyzer.analyze()
            
            return tech_stack
            
        except Exception as e:
            logger.error(f"Tech stack analysis failed: {e}")
            return {'languages': [], 'frameworks': [], 'dependencies': {}}
    
    def _generate_recommendations(
        self,
        vulnerabilities: List[Any],
        quality_issues: List[Any],
        tech_stack: Dict[str, Any],
        architecture: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate recommendations using RecommendationsEngine."""
        try:
            import sys
            sys.path.insert(0, str(self.cortex_root / "src"))
            from operations.recommendations_engine import RecommendationsEngine
            
            engine = RecommendationsEngine()
            recommendations = engine.generate_recommendations(
                vulnerabilities, quality_issues, tech_stack, architecture
            )
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Recommendations generation failed: {e}")
            return []
    
    def _generate_uml_diagram(self, project_path: Path) -> str:
        """Generate UML class diagram using UMLDiagramRenderer."""
        try:
            import sys
            sys.path.insert(0, str(self.cortex_root / "src"))
            
            # Check if graphviz is available
            try:
                import graphviz
            except ImportError:
                logger.info("graphviz not installed - skipping UML generation (optional feature)")
                return ""
            
            from use_cases.render_uml_diagrams import UMLDiagramRenderer
            
            renderer = UMLDiagramRenderer(str(project_path))
            
            # Analyze Python files
            python_files = [
                f for f in project_path.rglob('*.py')
                if self._should_scan_file(f)
            ]
            
            # Limit to prevent performance issues (max 100 files)
            if len(python_files) > 100:
                logger.info(f"Limiting UML generation to 100 most relevant files (found {len(python_files)})")
                python_files = python_files[:100]
            
            for py_file in python_files:
                try:
                    renderer.analyze_python_file(py_file)
                except Exception as e:
                    logger.debug(f"Failed to analyze {py_file} for UML: {e}")
            
            # Generate SVG diagram
            if renderer.classes:
                diagram_svg = renderer.render_svg()
                return diagram_svg
            else:
                return ""
            
        except Exception as e:
            logger.warning(f"UML diagram generation skipped: {e}")
            return ""
    
    def _generate_dashboard_html(
        self,
        project_info: Dict[str, Any],
        quality_issues: List[Any],
        quality_score: float,
        vulnerabilities: List[Any],
        metrics: List[Any],
        architecture: Dict[str, Any],
        tech_stack: Dict[str, Any],
        recommendations: List[Dict[str, Any]],
        uml_diagram: str,
        project_name: str
    ) -> tuple[str, Path]:
        """
        Generate interactive dashboard HTML using DashboardGenerator.
        
        Returns:
            Tuple of (dashboard_url, output_path)
        """
        try:
            import sys
            import json
            sys.path.insert(0, str(self.cortex_root / "src"))
            from operations.dashboard_generator import generate_dashboard_html
            
            # Determine output path based on mode
            if self.test_mode:
                # Testing mode: output to onboarded-apps/{project-name}/
                output_dir = (
                    self.cortex_root / "cortex-brain" / "documents" / 
                    "onboarded-apps" / project_name.lower().replace(" ", "-")
                )
                output_dir.mkdir(parents=True, exist_ok=True)
                
                # Write raw data files for inspection
                (output_dir / "project_info.json").write_text(
                    json.dumps(project_info, indent=2, ensure_ascii=False),
                    encoding='utf-8'
                )
                (output_dir / "quality_score.json").write_text(
                    json.dumps({"score": quality_score, "issue_count": len(quality_issues)}, indent=2),
                    encoding='utf-8'
                )
                (output_dir / "security_scan.json").write_text(
                    json.dumps({"vulnerability_count": len(vulnerabilities)}, indent=2),
                    encoding='utf-8'
                )
                (output_dir / "performance_metrics.json").write_text(
                    json.dumps({"metric_count": len(metrics)}, indent=2),
                    encoding='utf-8'
                )
                (output_dir / "architecture.json").write_text(
                    json.dumps(architecture, indent=2, ensure_ascii=False),
                    encoding='utf-8'
                )
                (output_dir / "techstack.json").write_text(
                    json.dumps(tech_stack, indent=2, ensure_ascii=False),
                    encoding='utf-8'
                )
                (output_dir / "recommendations.json").write_text(
                    json.dumps(recommendations, indent=2, ensure_ascii=False),
                    encoding='utf-8'
                )
                
                # Create summary report
                summary_path = output_dir / "onboarding_summary.md"
                summary_content = f"""# {project_info['name']} - Onboarding Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Project Overview
- **Files:** {project_info['files']}
- **Lines of Code:** {project_info['lines']:,}
- **Languages:** {', '.join(project_info['languages'])}

## Quality Analysis
- **Score:** {quality_score:.1f}/100
- **Issues Found:** {len(quality_issues)}

## Security Analysis
- **Vulnerabilities:** {len(vulnerabilities)}

## Architecture
- **Nodes:** {architecture.get('metadata', {}).get('total_nodes', 0)}
- **Relationships:** {architecture.get('metadata', {}).get('total_edges', 0)}

## Technology Stack
- **Languages:** {tech_stack.get('statistics', {}).get('total_languages', 0)}
- **Frameworks:** {tech_stack.get('statistics', {}).get('total_frameworks', 0)}
- **Dependencies:** {tech_stack.get('statistics', {}).get('total_dependencies', 0)}

## Recommendations
- **Total:** {len(recommendations)}
- **Critical:** {sum(1 for r in recommendations if r.get('priority') == 'critical')}
- **High:** {sum(1 for r in recommendations if r.get('priority') == 'high')}

## Files Generated
- `project_info.json` - Project metadata
- `quality_score.json` - Code quality analysis
- `security_scan.json` - Security vulnerability scan
- `performance_metrics.json` - Performance telemetry
- `architecture.json` - Architecture graph (D3.js format)
- `techstack.json` - Technology stack analysis
- `recommendations.json` - Prioritized recommendations
- `dashboard.html` - Interactive dashboard (NEW!)

## Next Steps
1. Open interactive dashboard: `dashboard.html`
2. Review security vulnerabilities
3. Use CORTEX for TDD workflow: `start tdd`
4. Plan features with DoR/DoD: `plan feature`
"""
                summary_path.write_text(summary_content, encoding='utf-8')
                
                # Generate interactive dashboard HTML
                template_path = self.cortex_root / "templates" / "interactive-dashboard-template.html"
                dashboard_path = output_dir / "dashboard.html"
                
                quality_data = {
                    "score": quality_score,
                    "issues": [{
                        "type": str(getattr(i, "type", "unknown")),
                        "severity": str(getattr(i, "severity", "medium")),
                        "file": str(getattr(i, "file_path", ""))
                    } for i in quality_issues[:100]]
                }
                
                security_data = {
                    "vulnerabilities": len(vulnerabilities),
                    "issues": [{
                        "type": str(getattr(v, "vulnerability_type", "unknown")),
                        "severity": str(getattr(v, "severity", "medium")),
                        "file": str(getattr(v, "file_path", ""))
                    } for v in vulnerabilities[:100]]
                }
                
                generate_dashboard_html(
                    template_path=template_path,
                    output_path=dashboard_path,
                    title=f"{project_name} - Application Dashboard",
                    project_info=project_info,
                    quality_data=quality_data,
                    security_data=security_data,
                    architecture_data=architecture,
                    techstack_data=tech_stack,
                    recommendations_data=recommendations,
                    uml_diagram=uml_diagram
                )
                
                dashboard_url = f"file:///{dashboard_path}"
                return dashboard_url, output_dir
                
            else:
                # Production mode: standard dashboard location
                from operations.dashboard_data_adapter import DashboardDataAdapter
                
                adapter = DashboardDataAdapter(self.cortex_root)
                adapter.generate_full_dashboard_data(
                    project_info,
                    quality_issues,
                    quality_score,
                    vulnerabilities,
                    metrics
                )
                
                dashboard_path = (
                    self.cortex_root / "cortex-brain" / "documents" / 
                    "analysis" / "dashboard" / "dashboard.html"
                )
                
                return f"file://{dashboard_path}", dashboard_path.parent
            
        except ImportError as e:
            logger.error(f"Failed to import required module: {e}")
            raise
        except Exception as e:
            logger.error(f"Dashboard data generation failed: {e}")
            raise
    
    def _validate_dashboard(self, output_dir: Path) -> tuple:
        """
        Validate dashboard functionality comprehensively.
        
        Tests:
        - All 7 tabs load with data
        - JavaScript functions present
        - Interactive elements work
        - Visualizations configured
        - Data structure correct
        
        Args:
            output_dir: Directory containing dashboard.html and data files
        
        Returns:
            Tuple of (success: bool, report: dict)
        """
        try:
            from operations.dashboard_validator_v2 import DashboardValidator
            
            dashboard_path = output_dir / 'dashboard.html'
            
            if not dashboard_path.exists():
                logger.error(f"Dashboard not found: {dashboard_path}")
                return False, {
                    'success': False,
                    'error': 'Dashboard file not found',
                    'path': str(dashboard_path)
                }
            
            validator = DashboardValidator(output_dir, dashboard_path)
            success, report = validator.validate_all()
            
            # Print summary
            if success:
                logger.info(f"✅ Dashboard validation: {report['summary']['passed_tests']}/{report['summary']['total_tests']} tests passed")
            else:
                logger.warning(f"⚠️ Dashboard validation: {report['summary']['failed_tests']} tests failed")
                logger.warning(f"   Errors: {report['summary']['errors']}, Warnings: {report['summary']['warnings']}")
            
            return success, report
            
        except ImportError as e:
            logger.error(f"Failed to import dashboard validator: {e}")
            return False, {'success': False, 'error': f'Import error: {e}'}
        except Exception as e:
            logger.error(f"Dashboard validation failed: {e}")
            return False, {'success': False, 'error': str(e)}


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
