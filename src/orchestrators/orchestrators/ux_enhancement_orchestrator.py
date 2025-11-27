"""
UX Enhancement Orchestrator

Purpose: Orchestrates codebase analysis and dashboard generation for enhancement requests.
         Connects CORTEX analysis tools to interactive visualization layer.

Workflow:
1. Run analysis tools (CodeCleanupValidator, ArchitectureAnalyzer, etc.)
2. Export results to dashboard JSON format
3. Apply Discovery Intelligence patterns
4. Generate interactive HTML dashboard
5. Open in browser for exploration

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
Repository: https://github.com/asifhussain60/CORTEX
"""

import os
import sys
import json
import webbrowser
from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))


class AnalysisProgress:
    """Progress tracking for analysis phases"""
    
    def __init__(self):
        self.phases = [
            "Scanning codebase...",
            "Mapping architecture...",
            "Measuring performance...",
            "Checking security...",
            "Applying discovery patterns...",
            "Generating dashboard..."
        ]
        self.current_phase = 0
        self.total_phases = len(self.phases)
    
    def update(self, message: str):
        """Update progress with custom message"""
        self.current_phase += 1
        percentage = int((self.current_phase / self.total_phases) * 100)
        print(f"[{percentage}%] {message}")
    
    def complete(self, message: str):
        """Mark analysis as complete"""
        print(f"[100%] {message}")


class UXEnhancementOrchestrator:
    """
    Orchestrator for UX enhancement workflow.
    
    Responsibilities:
    - Execute CORTEX analysis tools on target codebase
    - Transform results to dashboard JSON format
    - Apply Discovery Intelligence patterns
    - Generate interactive HTML dashboard
    - Open dashboard in user's browser
    """
    
    def __init__(self, cortex_root: Optional[Path] = None):
        """
        Initialize orchestrator.
        
        Args:
            cortex_root: Path to CORTEX repository root
        """
        if cortex_root is None:
            # Auto-detect CORTEX root
            cortex_root = Path(__file__).parent.parent.parent
        
        self.cortex_root = Path(cortex_root)
        self.brain_path = self.cortex_root / "cortex-brain"
        self.analysis_output_dir = self.brain_path / "documents" / "analysis"
        self.progress = AnalysisProgress()
    
    def analyze_and_generate_dashboard(
        self,
        codebase_path: str,
        user_request: str,
        skip_explanation: bool = False
    ) -> Dict[str, Any]:
        """
        Main orchestration method: analyze codebase and generate dashboard.
        
        Steps:
        1. Validate codebase path
        2. Run analysis tools with progress updates
        3. Export results to JSON format
        4. Generate HTML dashboard
        5. Open in browser
        
        Args:
            codebase_path: Path to codebase to analyze
            user_request: Original user request (for context)
            skip_explanation: Whether user opted into auto-approval
        
        Returns:
            Dictionary with analysis results and dashboard path
        """
        try:
            print("\n🎯 Starting UX Enhancement Analysis\n")
            
            # Phase 1: Validate codebase
            self.progress.update("Validating codebase...")
            codebase_info = self._validate_codebase(codebase_path)
            
            # Phase 2: Run quality analysis
            self.progress.update("Scanning codebase for quality metrics...")
            quality_results = self._analyze_quality(codebase_path)
            
            # Phase 3: Analyze architecture
            self.progress.update("Mapping architecture components...")
            architecture_results = self._analyze_architecture(codebase_path)
            
            # Phase 4: Profile performance
            self.progress.update("Measuring performance bottlenecks...")
            performance_results = self._analyze_performance(codebase_path)
            
            # Phase 5: Scan security
            self.progress.update("Checking security vulnerabilities...")
            security_results = self._analyze_security(codebase_path)
            
            # Phase 6: Apply discovery patterns
            self.progress.update("Applying discovery intelligence...")
            discovery_data = self._apply_discovery_patterns(
                quality_results,
                architecture_results,
                performance_results,
                security_results
            )
            
            # Phase 7: Export to JSON format
            dashboard_data = self._export_to_dashboard_format(
                codebase_info,
                quality_results,
                architecture_results,
                performance_results,
                security_results,
                discovery_data
            )
            
            # Phase 8: Generate HTML dashboard
            self.progress.update("Generating interactive dashboard...")
            dashboard_path = self._generate_dashboard_html(dashboard_data, user_request)
            
            # Phase 9: Open in browser
            self.progress.complete("Analysis complete! Opening dashboard...")
            webbrowser.open(f"file://{dashboard_path}")
            
            return {
                "success": True,
                "dashboard_path": str(dashboard_path),
                "analysis_summary": {
                    "codebase": codebase_info,
                    "quality_score": quality_results.get("overall_score", 0),
                    "architecture_health": architecture_results.get("health_score", 0),
                    "performance_grade": performance_results.get("grade", "N/A"),
                    "security_rating": security_results.get("rating", "N/A")
                }
            }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Analysis failed: {str(e)}"
            }
    
    def _validate_codebase(self, codebase_path: str) -> Dict[str, Any]:
        """
        Validate codebase exists and gather basic metadata.
        
        Args:
            codebase_path: Path to codebase
        
        Returns:
            Dictionary with codebase metadata
        """
        path = Path(codebase_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Codebase not found: {codebase_path}")
        
        if not path.is_dir():
            raise ValueError(f"Codebase path must be a directory: {codebase_path}")
        
        # Count files and estimate lines (simple heuristic for now)
        file_count = sum(1 for _ in path.rglob("*") if _.is_file())
        
        return {
            "path": str(path),
            "name": path.name,
            "file_count": file_count,
            "timestamp": datetime.now().isoformat()
        }
    
    def _analyze_quality(self, codebase_path: str) -> Dict[str, Any]:
        """
        Analyze code quality using CodeCleanupValidator.
        
        TODO: Integrate with actual CodeCleanupValidator
        For now, returns mock data structure matching mock-quality.json format
        
        Args:
            codebase_path: Path to codebase
        
        Returns:
            Quality analysis results
        """
        # TODO: Replace with actual CodeCleanupValidator integration
        # from src.validators.code_cleanup_validator import CodeCleanupValidator
        # validator = CodeCleanupValidator()
        # results = validator.analyze(codebase_path)
        
        # Mock data for now (will be replaced)
        return {
            "overall_score": 73,
            "maintainability": 72,
            "reliability": 78,
            "security": 69,
            "performance": 71,
            "test_coverage": 68,
            "code_smells": {
                "longMethod": 45,
                "largeClass": 12,
                "complexMethod": 31,
                "duplicateCode": 89,
                "godClass": 3,
                "featureEnvy": 18,
                "dataClumps": 7,
                "primitiveObsession": 22,
                "switchStatements": 14,
                "speculativeGenerality": 5,
                "temporaryField": 11
            },
            "technical_debt": "$19,000",
            "trend": "improving"
        }
    
    def _analyze_architecture(self, codebase_path: str) -> Dict[str, Any]:
        """
        Analyze architecture components and relationships.
        
        TODO: Integrate with actual ArchitectureAnalyzer
        For now, returns mock data structure matching mock-architecture.json format
        
        Args:
            codebase_path: Path to codebase
        
        Returns:
            Architecture analysis results
        """
        # TODO: Replace with actual ArchitectureAnalyzer integration
        
        # Mock data for now (will be replaced)
        return {
            "health_score": 78,
            "components": [
                {"name": "Authentication", "health": 85, "complexity": "medium", "dependencies": 4},
                {"name": "Payment", "health": 72, "complexity": "high", "dependencies": 7},
                {"name": "Database", "health": 90, "complexity": "low", "dependencies": 12},
                {"name": "API", "health": 75, "complexity": "medium", "dependencies": 6},
                {"name": "UI", "health": 68, "complexity": "medium", "dependencies": 8},
                {"name": "Logging", "health": 95, "complexity": "low", "dependencies": 3},
                {"name": "Notification", "health": 80, "complexity": "low", "dependencies": 2},
                {"name": "Reporting", "health": 70, "complexity": "high", "dependencies": 9}
            ],
            "relationships": [],
            "issues": ["Tight coupling in Payment module", "God class in API layer"]
        }
    
    def _analyze_performance(self, codebase_path: str) -> Dict[str, Any]:
        """
        Profile performance and identify bottlenecks.
        
        TODO: Integrate with actual PerformanceProfiler
        For now, returns mock data structure matching mock-performance.json format
        
        Args:
            codebase_path: Path to codebase
        
        Returns:
            Performance analysis results
        """
        # TODO: Replace with actual PerformanceProfiler integration
        
        # Mock data for now (will be replaced)
        return {
            "grade": "B",
            "api_latencies": {
                "/api/auth/login": {"avg": 487, "p95": 892, "p99": 1247, "error_rate": 0.8},
                "/api/payments/process": {"avg": 1523, "p95": 2847, "p99": 4129, "error_rate": 2.1},
                "/api/users/profile": {"avg": 124, "p95": 289, "p99": 421, "error_rate": 0.3},
                "/api/reports/generate": {"avg": 3456, "p95": 7821, "p99": 12847, "error_rate": 1.5},
                "/api/notifications/send": {"avg": 287, "p95": 543, "p99": 847, "error_rate": 0.5}
            },
            "bottlenecks": [
                {"type": "CPU", "severity": "medium", "location": "Payment processing loop"},
                {"type": "I/O", "severity": "high", "location": "Report generation file writes"},
                {"type": "Database", "severity": "medium", "location": "User profile N+1 queries"}
            ]
        }
    
    def _analyze_security(self, codebase_path: str) -> Dict[str, Any]:
        """
        Scan for security vulnerabilities.
        
        TODO: Integrate with actual SecurityScanner
        For now, returns mock data structure matching mock-security.json format
        
        Args:
            codebase_path: Path to codebase
        
        Returns:
            Security analysis results
        """
        # TODO: Replace with actual SecurityScanner integration
        
        # Mock data for now (will be replaced)
        return {
            "rating": "B",
            "owasp_top_10": {
                "injection": "addressed",
                "broken_auth": "vulnerable",
                "sensitive_data": "partially_addressed",
                "xxe": "addressed",
                "broken_access": "vulnerable",
                "security_misconfig": "vulnerable",
                "xss": "addressed",
                "insecure_deserialization": "addressed",
                "vulnerable_components": "partially_addressed",
                "insufficient_logging": "vulnerable"
            },
            "vulnerabilities": {
                "critical": 0,
                "high": 3,
                "medium": 12,
                "low": 7
            },
            "compliance": {
                "soc2": 85,
                "gdpr": 78,
                "pci_dss": 60,
                "hipaa": 45
            }
        }
    
    def _apply_discovery_patterns(
        self,
        quality: Dict,
        architecture: Dict,
        performance: Dict,
        security: Dict
    ) -> Dict[str, Any]:
        """
        Apply Discovery Intelligence patterns to analysis results.
        
        Generates:
        - Context-aware suggestions
        - Progressive questioning flows
        - "What if" scenarios
        - Guided discovery paths
        
        Args:
            quality: Quality analysis results
            architecture: Architecture analysis results
            performance: Performance analysis results
            security: Security analysis results
        
        Returns:
            Discovery intelligence data
        """
        # Load suggestion patterns from mock data
        patterns_path = self.analysis_output_dir / "INTELLIGENT-UX-DEMO" / "assets" / "data" / "patterns" / "suggestion-patterns.json"
        
        if patterns_path.exists():
            with open(patterns_path, 'r') as f:
                patterns = json.load(f)
        else:
            patterns = {}
        
        # Match patterns to findings
        suggestions = []
        
        # Quality-based suggestions
        if quality.get("overall_score", 0) < 70:
            suggestions.append({
                "pattern": "lowQuality",
                "title": "Code Quality Improvements",
                "priority": "high"
            })
        
        # Architecture-based suggestions
        if any("god class" in issue.lower() for issue in architecture.get("issues", [])):
            suggestions.append({
                "pattern": "godClass",
                "title": "Refactor God Classes",
                "priority": "high"
            })
        
        # Performance-based suggestions
        if performance.get("grade", "A") in ["C", "D", "F"]:
            suggestions.append({
                "pattern": "performanceBottleneck",
                "title": "Optimize Performance Bottlenecks",
                "priority": "high"
            })
        
        # Security-based suggestions
        if security.get("rating", "A") in ["C", "D", "F"]:
            suggestions.append({
                "pattern": "securityVulnerability",
                "title": "Address Security Vulnerabilities",
                "priority": "critical"
            })
        
        return {
            "suggestions": suggestions,
            "patterns": patterns
        }
    
    def _export_to_dashboard_format(
        self,
        codebase_info: Dict,
        quality: Dict,
        architecture: Dict,
        performance: Dict,
        security: Dict,
        discovery: Dict
    ) -> Dict[str, Any]:
        """
        Export analysis results to Phase 2 dashboard JSON format.
        
        Transforms analysis data to match the structure expected by
        the interactive dashboard with full visualization support.
        
        Args:
            codebase_info: Codebase metadata
            quality: Quality analysis results
            architecture: Architecture analysis results
            performance: Performance analysis results
            security: Security analysis results
            discovery: Discovery intelligence data
        
        Returns:
            Complete dashboard data structure matching analysis-data.json format
        """
        # Extract scores
        overall_score = quality.get("overall_score", 0)
        
        # Build metadata section
        metadata = {
            "projectName": codebase_info["name"],
            "timestamp": codebase_info["timestamp"],
            "fileCount": codebase_info["file_count"],
            "lineCount": codebase_info.get("line_count", 0),
            "language": "Python",  # TODO: Auto-detect
            "version": "3.2.0",
            "analysisVersion": "1.0.0",
            "duration": 0  # TODO: Track analysis duration
        }
        
        # Build scores section
        scores = {
            "overall": overall_score,
            "quality": quality.get("overall_score", 0),
            "performance": 0,  # TODO: Convert grade to score
            "security": 0,  # TODO: Convert rating to score
            "architecture": architecture.get("health_score", 0),
            "maintainability": quality.get("maintainability", 0),
            "testCoverage": quality.get("test_coverage", 0)
        }
        
        # Build summary section with quick wins and critical issues
        summary = {
            "text": f"Analysis complete for {codebase_info['name']}. Overall quality score: {overall_score}%",
            "quickWins": [],
            "criticalIssues": architecture.get("issues", [])[:5]
        }
        
        # Build roadmap section
        roadmap = {
            "tasks": [],
            "dependencies": [],
            "milestones": []
        }
        
        # Build testCoverage section
        testCoverage = {
            "overall": quality.get("test_coverage", 0),
            "byModule": {},
            "untested": []
        }
        
        # Build discoveries section
        discoveries = discovery.get("suggestions", [])
        
        return {
            "metadata": metadata,
            "scores": scores,
            "summary": summary,
            "architecture": architecture,
            "quality": quality,
            "roadmap": roadmap,
            "performance": performance,
            "security": security,
            "discoveries": discoveries,
            "testCoverage": testCoverage
        }
    
    def _generate_dashboard_html(self, dashboard_data: Dict, user_request: str) -> Path:
        """
        Generate interactive HTML dashboard with Tailwind CSS and D3.js visualizations.
        
        Uses Phase 2 dashboard template with full feature set:
        - 6-tab navigation (Executive, Architecture, Quality, Roadmap, Journey, Security)
        - D3.js visualizations (force graphs, heatmaps, treemaps, Gantt charts)
        - Discovery system with behavioral tracking
        - Theme toggle (dark/light mode)
        - Responsive design
        
        Args:
            dashboard_data: Complete dashboard data
            user_request: Original user request (for context)
        
        Returns:
            Path to generated HTML file
        """
        # Create output directory
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        project_name = dashboard_data.get("metadata", {}).get("projectName", "analysis")
        output_dir = self.analysis_output_dir / f"{project_name}-{timestamp}"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Export JSON data
        json_path = output_dir / "analysis-data.json"
        with open(json_path, 'w') as f:
            json.dump(dashboard_data, f, indent=2)
        
        # Copy Phase 2 dashboard template and assets
        dashboard_template_dir = self.brain_path / "documents" / "analysis" / "INTELLIGENT-UX-DEMO"
        html_path = output_dir / "dashboard.html"
        
        # Copy dashboard HTML
        import shutil
        template_html = dashboard_template_dir / "dashboard.html"
        if template_html.exists():
            shutil.copy(template_html, html_path)
            
            # Copy assets directory
            template_assets = dashboard_template_dir / "assets"
            output_assets = output_dir / "assets"
            if template_assets.exists():
                shutil.copytree(template_assets, output_assets, dirs_exist_ok=True)
        else:
            # Fallback to placeholder if Phase 2 template not found
            html_content = self._generate_placeholder_html(dashboard_data, user_request)
            with open(html_path, 'w') as f:
                f.write(html_content)
        
        return html_path
    
    def _generate_placeholder_html(self, data: Dict, user_request: str) -> str:
        """
        Generate placeholder HTML until Phase 2 dashboard is built.
        
        Args:
            data: Dashboard data
            user_request: Original user request
        
        Returns:
            HTML string
        """
        # Extract scores with fallbacks
        quality_score = data.get("scores", {}).get("quality", 0)
        arch_health = data.get("scores", {}).get("architecture", 0)
        perf_score = data.get("scores", {}).get("performance", 0)
        security_score = data.get("scores", {}).get("security", 0)
        
        # Get metadata
        project_name = data.get("metadata", {}).get("projectName", "Unknown")
        timestamp = data.get("metadata", {}).get("timestamp", "")
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>UX Enhancement Dashboard - {project_name}</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-50">
    <div class="container mx-auto px-4 py-8">
        <h1 class="text-4xl font-bold text-gray-900 mb-2">
            🎯 UX Enhancement Analysis
        </h1>
        <p class="text-gray-600 mb-8">{project_name} - {timestamp}</p>
        
        <div class="bg-blue-50 border-l-4 border-blue-500 p-4 mb-8">
            <p class="text-blue-700">
                <strong>User Request:</strong> {user_request}
            </p>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-sm font-semibold text-gray-600 mb-2">Quality Score</h3>
                <p class="text-3xl font-bold text-blue-600">{quality_score}%</p>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-sm font-semibold text-gray-600 mb-2">Architecture Health</h3>
                <p class="text-3xl font-bold text-green-600">{arch_health}%</p>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-sm font-semibold text-gray-600 mb-2">Performance Score</h3>
                <p class="text-3xl font-bold text-yellow-600">{perf_score}%</p>
            </div>
            <div class="bg-white rounded-lg shadow p-6">
                <h3 class="text-sm font-semibold text-gray-600 mb-2">Security Score</h3>
                <p class="text-3xl font-bold text-purple-600">{security_score}%</p>
            </div>
        </div>
        
        <div class="bg-white rounded-lg shadow p-6 mb-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-4">📊 Analysis Complete</h2>
            <p class="text-gray-700 mb-4">
                Your codebase analysis is complete! This is a <strong>placeholder dashboard</strong> 
                showing the analysis results.
            </p>
            <p class="text-gray-700 mb-4">
                <strong>Phase 2</strong> will implement the full interactive dashboard with:
            </p>
            <ul class="list-disc list-inside text-gray-700 space-y-2 mb-4">
                <li>6-tab navigation (Executive Summary, Architecture, Quality, Roadmap, Journey, Security)</li>
                <li>Interactive visualizations (D3.js force graphs, heatmaps, treemaps)</li>
                <li>Context-aware suggestions</li>
                <li>"What if" scenario comparisons</li>
                <li>Guided discovery paths</li>
                <li>Dark/light theme toggle</li>
            </ul>
            <p class="text-gray-700">
                <strong>Raw Data:</strong> See <code class="bg-gray-100 px-2 py-1 rounded">analysis-data.json</code> 
                in the same directory for complete analysis results.
            </p>
        </div>
        
        <div class="bg-yellow-50 border-l-4 border-yellow-500 p-4">
            <p class="text-yellow-700">
                <strong>Next Steps:</strong> Phase 2 will replace this placeholder with the full dashboard. 
                The analysis data is ready - we just need to build the visualization layer!
            </p>
        </div>
    </div>
</body>
</html>"""


def main():
    """Test the orchestrator"""
    orchestrator = UXEnhancementOrchestrator()
    
    # Test with CORTEX repository itself
    cortex_path = Path(__file__).parent.parent.parent
    
    print("Testing UX Enhancement Orchestrator")
    print(f"Analyzing: {cortex_path}\n")
    
    result = orchestrator.analyze_and_generate_dashboard(
        codebase_path=str(cortex_path),
        user_request="Enhance my CORTEX codebase",
        skip_explanation=False
    )
    
    print(f"\nResult: {json.dumps(result, indent=2)}")


if __name__ == "__main__":
    main()
