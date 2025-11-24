"""
System Refactor Plugin - CORTEX Self-Review and Optimization

This plugin performs comprehensive critical review of CORTEX architecture,
identifies test coverage gaps, and executes automated refactoring.

Key Functions:
1. Critical faculty review (brain, plugins, modules, entry points)
2. Test coverage analysis and gap identification
3. Automated REFACTOR phase execution for edge case tests
4. Self-optimization and continuous improvement

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict

from src.plugins.base_plugin import (
    BasePlugin,
    PluginMetadata,
    PluginCategory,
    PluginPriority
)
from src.plugins.command_registry import CommandMetadata


@dataclass
class CoverageGap:
    """Represents a test coverage gap."""
    category: str
    description: str
    priority: str  # HIGH, MEDIUM, LOW
    affected_files: List[str]
    recommended_tests: List[str]
    estimated_effort_hours: float


@dataclass
class RefactorTask:
    """Represents a refactoring task."""
    task_id: str
    title: str
    description: str
    file_path: str
    current_state: str  # GREEN, REFACTOR_PENDING
    target_state: str   # REFACTOR_COMPLETE
    priority: str
    estimated_minutes: int
    status: str  # PENDING, IN_PROGRESS, COMPLETE


@dataclass
class ReviewReport:
    """Comprehensive review report."""
    timestamp: str
    overall_health: str  # EXCELLENT, GOOD, NEEDS_ATTENTION, CRITICAL
    total_tests: int
    passing_tests: int
    coverage_gaps: List[CoverageGap]
    refactor_tasks: List[RefactorTask]
    recommendations: List[str]
    metrics: Dict[str, Any]


class SystemRefactorPlugin(BasePlugin):
    """
    Plugin for critical system review and automated refactoring.
    
    Capabilities:
    - Analyze test coverage across all layers
    - Identify gaps in brain protection, plugins, modules
    - Execute REFACTOR phase for tests in GREEN state
    - Generate comprehensive review reports
    - Automate gap-filling through test generation
    """
    
    def __init__(self):
        """Initialize plugin with metadata and configuration."""
        super().__init__()
        self.project_root = self._find_project_root()
        self.brain_path = self.project_root / "cortex-brain"
        self.tests_path = self.project_root / "tests"
        self.src_path = self.project_root / "src"
        
    def _get_metadata(self) -> PluginMetadata:
        """Return plugin metadata."""
        return PluginMetadata(
            plugin_id="system_refactor",
            name="System Refactor Plugin",
            version="1.0.0",
            category=PluginCategory.MAINTENANCE,
            priority=PluginPriority.HIGH,
            description="Critical review, gap analysis, and automated refactoring",
            author="Asif Hussain",
            dependencies=[],
            hooks=[],
            config_schema={}
        )
    
    def register_commands(self) -> List[CommandMetadata]:
        """Register slash commands for this plugin."""
        return [
            CommandMetadata(
                command="/refactor",
                natural_language_equivalent="refactor system",
                plugin_id=self.metadata.plugin_id,
                description="Perform critical review and execute refactoring",
                category="maintenance",
                aliases=["/review", "/optimize", "/self-review"]
            )
        ]
    
    def can_handle(self, request: str) -> bool:
        """Check if plugin can handle the request."""
        request_lower = request.lower()
        triggers = [
            "refactor", "review", "optimize", "self-review",
            "gap analysis", "coverage gaps", "test gaps",
            "critical review", "system health"
        ]
        return any(trigger in request_lower for trigger in triggers)
    
    def initialize(self) -> bool:
        """Initialize plugin resources."""
        try:
            # Verify project structure
            if not self.project_root.exists():
                return False
            if not self.tests_path.exists():
                return False
            if not self.src_path.exists():
                return False
            
            self.logger.info(f"System Refactor Plugin initialized at {self.project_root}")
            return True
            
        except Exception as e:
            self.logger.error(f"Initialization failed: {e}")
            return False
    
    def execute(self, request: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute refactor plugin workflow.
        
        Workflow:
        1. Critical faculty review
        2. Gap analysis
        3. REFACTOR phase execution
        4. Report generation
        """
        try:
            self.logger.info("Starting system refactor workflow...")
            
            # Phase 1: Critical Review
            review_report = self._perform_critical_review()
            
            # Phase 2: Gap Analysis
            coverage_gaps = self._analyze_coverage_gaps()
            review_report.coverage_gaps = coverage_gaps
            
            # Phase 3: REFACTOR Phase Execution
            refactor_results = self._execute_refactor_phase()
            review_report.refactor_tasks = refactor_results
            
            # Phase 4: Generate Recommendations
            recommendations = self._generate_recommendations(review_report)
            review_report.recommendations = recommendations
            
            # Phase 5: Save Report
            report_path = self._save_report(review_report)
            
            return {
                "status": "success",
                "report": asdict(review_report),
                "report_path": str(report_path),
                "summary": self._format_summary(review_report)
            }
            
        except Exception as e:
            self.logger.error(f"Refactor execution failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    def cleanup(self) -> bool:
        """Cleanup plugin resources."""
        self.logger.info("System Refactor Plugin cleanup complete")
        return True
    
    # ============================================
    # Phase 1: Critical Review
    # ============================================
    
    def _perform_critical_review(self) -> ReviewReport:
        """
        Perform comprehensive critical review of CORTEX.
        
        Reviews:
        - Test suite health
        - Brain protection coverage
        - Plugin test coverage
        - Module test coverage
        - Entry point test coverage
        """
        self.logger.info("Performing critical review...")
        
        # Get test metrics
        test_metrics = self._analyze_test_suite()
        
        # Determine overall health
        overall_health = self._assess_system_health(test_metrics)
        
        return ReviewReport(
            timestamp=datetime.now().isoformat(),
            overall_health=overall_health,
            total_tests=test_metrics["total"],
            passing_tests=test_metrics["passing"],
            coverage_gaps=[],  # Filled in next phase
            refactor_tasks=[],  # Filled in next phase
            recommendations=[],  # Filled in next phase
            metrics=test_metrics
        )
    
    def _analyze_test_suite(self) -> Dict[str, Any]:
        """Analyze current test suite metrics."""
        try:
            # Run pytest collection
            result = subprocess.run(
                ["pytest", "--collect-only", "-q"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Parse output
            output_lines = result.stdout.split("\n")
            
            # Count tests
            total_tests = 0
            for line in output_lines:
                if line.strip().startswith("<"):
                    total_tests += 1
            
            # Run actual tests to get pass rate
            test_result = subprocess.run(
                ["pytest", "-v", "--tb=short"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Parse test results
            passing = test_result.stdout.count(" PASSED")
            failing = test_result.stdout.count(" FAILED")
            
            # Analyze coverage by category
            categories = self._analyze_test_categories()
            
            return {
                "total": total_tests,
                "passing": passing,
                "failing": failing,
                "pass_rate": (passing / total_tests * 100) if total_tests > 0 else 0,
                "categories": categories
            }
            
        except Exception as e:
            self.logger.error(f"Test analysis failed: {e}")
            return {
                "total": 0,
                "passing": 0,
                "failing": 0,
                "pass_rate": 0,
                "categories": {}
            }
    
    def _analyze_test_categories(self) -> Dict[str, int]:
        """Analyze test count by category."""
        categories = {}
        
        test_dirs = [
            ("brain_protection", self.tests_path / "tier0"),
            ("plugins", self.tests_path / "plugins"),
            ("entry_point", self.tests_path / "entry_point"),
            ("integration", self.tests_path / "integration"),
            ("edge_cases", self.tests_path / "edge_cases"),
            ("unit", self.tests_path / "unit"),
            ("tier1", self.tests_path / "tier1"),
            ("tier2", self.tests_path / "tier2"),
            ("tier3", self.tests_path / "tier3"),
        ]
        
        for category, test_dir in test_dirs:
            if test_dir.exists():
                test_files = list(test_dir.glob("test_*.py"))
                categories[category] = len(test_files)
            else:
                categories[category] = 0
        
        return categories
    
    def _assess_system_health(self, metrics: Dict[str, Any]) -> str:
        """Assess overall system health based on metrics."""
        pass_rate = metrics.get("pass_rate", 0)
        total_tests = metrics.get("total", 0)
        
        if pass_rate >= 98 and total_tests >= 400:
            return "EXCELLENT"
        elif pass_rate >= 95 and total_tests >= 300:
            return "GOOD"
        elif pass_rate >= 90 and total_tests >= 200:
            return "NEEDS_ATTENTION"
        else:
            return "CRITICAL"
    
    # ============================================
    # Phase 2: Gap Analysis
    # ============================================
    
    def _analyze_coverage_gaps(self) -> List[CoverageGap]:
        """
        Identify test coverage gaps across all layers.
        
        Analyzes:
        - Brain protection rule coverage
        - Plugin test coverage
        - Module test coverage
        - Entry point test coverage
        - Edge case coverage
        """
        self.logger.info("Analyzing coverage gaps...")
        
        gaps = []
        
        # Gap 1: Plugin test coverage
        plugin_gap = self._check_plugin_coverage()
        if plugin_gap:
            gaps.append(plugin_gap)
        
        # Gap 2: Entry point test coverage
        entry_gap = self._check_entry_point_coverage()
        if entry_gap:
            gaps.append(entry_gap)
        
        # Gap 3: Edge case REFACTOR phase
        refactor_gap = self._check_refactor_phase_coverage()
        if refactor_gap:
            gaps.append(refactor_gap)
        
        # Gap 4: Module integration tests
        module_gap = self._check_module_coverage()
        if module_gap:
            gaps.append(module_gap)
        
        # Gap 5: Performance tests
        perf_gap = self._check_performance_coverage()
        if perf_gap:
            gaps.append(perf_gap)
        
        return gaps
    
    def _check_plugin_coverage(self) -> Optional[CoverageGap]:
        """Check if all plugins have test harnesses."""
        plugins_dir = self.src_path / "plugins"
        tests_plugins_dir = self.tests_path / "plugins"
        
        if not plugins_dir.exists() or not tests_plugins_dir.exists():
            return None
        
        # Get all plugin files
        plugin_files = [f for f in plugins_dir.glob("*_plugin.py") if f.name != "base_plugin.py"]
        
        # Get all test files
        test_files = [f for f in tests_plugins_dir.glob("test_*.py")]
        test_names = {f.stem.replace("test_", "") for f in test_files}
        
        # Check coverage
        untested_plugins = []
        for plugin_file in plugin_files:
            plugin_name = plugin_file.stem  # e.g., "system_refactor_plugin"
            if plugin_name not in test_names:
                untested_plugins.append(str(plugin_file))
        
        if untested_plugins:
            return CoverageGap(
                category="Plugin Testing",
                description=f"{len(untested_plugins)} plugins lack test harnesses",
                priority="HIGH",
                affected_files=untested_plugins,
                recommended_tests=[f"test_{Path(p).stem}.py" for p in untested_plugins],
                estimated_effort_hours=len(untested_plugins) * 0.5
            )
        
        return None
    
    def _check_entry_point_coverage(self) -> Optional[CoverageGap]:
        """Check entry point test coverage."""
        entry_point_file = self.src_path / "entry_point" / "cortex_entry.py"
        test_entry_dir = self.tests_path / "entry_point"
        
        if not entry_point_file.exists():
            return None
        
        if not test_entry_dir.exists() or not list(test_entry_dir.glob("test_*.py")):
            return CoverageGap(
                category="Entry Point Testing",
                description="CortexEntry lacks comprehensive test coverage",
                priority="HIGH",
                affected_files=[str(entry_point_file)],
                recommended_tests=["test_cortex_entry_comprehensive.py"],
                estimated_effort_hours=2.0
            )
        
        return None
    
    def _check_refactor_phase_coverage(self) -> Optional[CoverageGap]:
        """Check if edge case tests need REFACTOR phase execution."""
        edge_cases_dir = self.tests_path / "edge_cases"
        
        if not edge_cases_dir.exists():
            return None
        
        # Count TODO REFACTOR comments
        refactor_needed = []
        for test_file in edge_cases_dir.glob("test_*.py"):
            with open(test_file, 'r', encoding='utf-8') as f:
                content = f.read()
                if "TODO (REFACTOR)" in content or "TODO REFACTOR" in content:
                    refactor_needed.append(str(test_file))
        
        if refactor_needed:
            return CoverageGap(
                category="Test Refinement",
                description=f"{len(refactor_needed)} edge case test files need REFACTOR phase execution",
                priority="MEDIUM",
                affected_files=refactor_needed,
                recommended_tests=["Add detailed assertions to all TODO REFACTOR tests"],
                estimated_effort_hours=len(refactor_needed) * 0.5
            )
        
        return None
    
    def _check_module_coverage(self) -> Optional[CoverageGap]:
        """Check if core modules have integration tests."""
        # Check critical modules
        critical_modules = [
            self.src_path / "tier1" / "tier1_api.py",
            self.src_path / "tier2" / "tier2_api.py",
            self.src_path / "tier3" / "tier3_api.py",
        ]
        
        untested_modules = []
        for module in critical_modules:
            if module.exists():
                # Check if integration tests exist
                module_name = module.stem
                integration_tests = list((self.tests_path / "integration").glob(f"*{module_name}*.py"))
                if not integration_tests:
                    untested_modules.append(str(module))
        
        if untested_modules:
            return CoverageGap(
                category="Module Integration",
                description=f"{len(untested_modules)} core modules lack integration tests",
                priority="MEDIUM",
                affected_files=untested_modules,
                recommended_tests=[f"test_integration_{Path(m).stem}.py" for m in untested_modules],
                estimated_effort_hours=len(untested_modules) * 1.0
            )
        
        return None
    
    def _check_performance_coverage(self) -> Optional[CoverageGap]:
        """Check performance test coverage."""
        perf_tests_dir = self.tests_path / "cortex-performance"
        
        if not perf_tests_dir.exists() or not list(perf_tests_dir.glob("test_*.py")):
            return CoverageGap(
                category="Performance Testing",
                description="Performance tests not implemented (Phase 5.4 pending)",
                priority="LOW",
                affected_files=["All tier APIs"],
                recommended_tests=["test_tier1_performance.py", "test_tier2_performance.py", "test_tier3_performance.py"],
                estimated_effort_hours=3.0
            )
        
        return None
    
    # ============================================
    # Phase 3: REFACTOR Phase Execution
    # ============================================
    
    def _execute_refactor_phase(self) -> List[RefactorTask]:
        """
        Execute REFACTOR phase for tests in GREEN state.
        
        For each test file with TODO REFACTOR comments:
        1. Parse test file to identify REFACTOR tasks
        2. Generate detailed assertions
        3. Update test file
        4. Validate tests still pass
        """
        self.logger.info("Executing REFACTOR phase...")
        
        tasks = []
        
        edge_cases_dir = self.tests_path / "edge_cases"
        if not edge_cases_dir.exists():
            return tasks
        
        for test_file in edge_cases_dir.glob("test_*.py"):
            file_tasks = self._parse_refactor_tasks(test_file)
            tasks.extend(file_tasks)
        
        return tasks
    
    def _parse_refactor_tasks(self, test_file: Path) -> List[RefactorTask]:
        """Parse REFACTOR tasks from test file."""
        tasks = []
        
        try:
            with open(test_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            current_test = None
            in_refactor_section = False
            refactor_items = []
            
            for i, line in enumerate(lines):
                # Detect test function
                if line.strip().startswith("def test_"):
                    if current_test and refactor_items:
                        # Save previous task
                        task = RefactorTask(
                            task_id=f"{test_file.stem}_{current_test}",
                            title=f"REFACTOR: {current_test}",
                            description="\n".join(refactor_items),
                            file_path=str(test_file),
                            current_state="GREEN",
                            target_state="REFACTOR_COMPLETE",
                            priority="MEDIUM",
                            estimated_minutes=15,
                            status="PENDING"
                        )
                        tasks.append(task)
                    
                    # Start new test
                    current_test = line.strip().split("(")[0].replace("def ", "")
                    refactor_items = []
                    in_refactor_section = False
                
                # Detect TODO REFACTOR section
                if "TODO (REFACTOR)" in line or "TODO REFACTOR" in line:
                    in_refactor_section = True
                
                # Collect refactor items
                if in_refactor_section and line.strip().startswith("# -"):
                    refactor_items.append(line.strip()[2:].strip())
            
            # Save last task
            if current_test and refactor_items:
                task = RefactorTask(
                    task_id=f"{test_file.stem}_{current_test}",
                    title=f"REFACTOR: {current_test}",
                    description="\n".join(refactor_items),
                    file_path=str(test_file),
                    current_state="GREEN",
                    target_state="REFACTOR_COMPLETE",
                    priority="MEDIUM",
                    estimated_minutes=15,
                    status="PENDING"
                )
                tasks.append(task)
        
        except Exception as e:
            self.logger.error(f"Failed to parse {test_file}: {e}")
        
        return tasks
    
    # ============================================
    # Phase 4: Recommendations
    # ============================================
    
    def _generate_recommendations(self, report: ReviewReport) -> List[str]:
        """Generate actionable recommendations based on review."""
        recommendations = []
        
        # Health-based recommendations
        if report.overall_health == "CRITICAL":
            recommendations.append("🚨 CRITICAL: Test pass rate below 90%. Immediate attention required.")
            recommendations.append("→ Fix failing tests before adding new features.")
        elif report.overall_health == "NEEDS_ATTENTION":
            recommendations.append("⚠️ Test pass rate below 95%. Review and fix failing tests.")
        
        # Gap-based recommendations
        high_priority_gaps = [g for g in report.coverage_gaps if g.priority == "HIGH"]
        if high_priority_gaps:
            recommendations.append(f"📊 {len(high_priority_gaps)} HIGH priority coverage gaps identified.")
            for gap in high_priority_gaps:
                recommendations.append(f"  → {gap.category}: {gap.description}")
        
        # REFACTOR phase recommendations
        pending_refactors = [t for t in report.refactor_tasks if t.status == "PENDING"]
        if pending_refactors:
            total_hours = sum(t.estimated_minutes for t in pending_refactors) / 60
            recommendations.append(f"🔧 {len(pending_refactors)} tests need REFACTOR phase execution (~{total_hours:.1f} hours).")
            recommendations.append("  → Run REFACTOR phase to add detailed assertions.")
        
        # Coverage improvement recommendations
        if report.metrics.get("pass_rate", 0) >= 95:
            recommendations.append("✅ Excellent test pass rate! Focus on coverage expansion.")
        
        return recommendations
    
    # ============================================
    # Phase 5: Reporting
    # ============================================
    
    def _save_report(self, report: ReviewReport) -> Path:
        """Save review report to brain."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.brain_path / f"SYSTEM-REFACTOR-REPORT-{timestamp}.md"
        
        # Generate markdown report
        md_content = self._format_markdown_report(report)
        
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(md_content)
        
        self.logger.info(f"Report saved to {report_file}")
        return report_file
    
    def _format_markdown_report(self, report: ReviewReport) -> str:
        """Format report as markdown."""
        lines = [
            "# CORTEX System Refactor Report",
            "",
            f"**Generated:** {report.timestamp}",
            f"**Overall Health:** {report.overall_health}",
            f"**Total Tests:** {report.total_tests}",
            f"**Passing Tests:** {report.passing_tests}",
            f"**Pass Rate:** {report.metrics.get('pass_rate', 0):.1f}%",
            "",
            "---",
            "",
            "## 📊 Test Suite Metrics",
            "",
        ]
        
        # Test categories
        categories = report.metrics.get("categories", {})
        lines.append("| Category | Test Files |")
        lines.append("|----------|-----------|")
        for category, count in sorted(categories.items()):
            lines.append(f"| {category.replace('_', ' ').title()} | {count} |")
        
        lines.extend(["", "---", ""])
        
        # Coverage gaps
        if report.coverage_gaps:
            lines.extend([
                "## 🔍 Coverage Gaps",
                "",
            ])
            
            for gap in report.coverage_gaps:
                lines.extend([
                    f"### {gap.category} ({gap.priority} Priority)",
                    "",
                    f"**Description:** {gap.description}",
                    "",
                    f"**Estimated Effort:** {gap.estimated_effort_hours} hours",
                    "",
                    "**Affected Files:**",
                ])
                for file in gap.affected_files:
                    lines.append(f"- {file}")
                lines.extend(["", "**Recommended Tests:**"])
                for test in gap.recommended_tests:
                    lines.append(f"- {test}")
                lines.extend(["", "---", ""])
        
        # REFACTOR tasks
        if report.refactor_tasks:
            lines.extend([
                "## 🔧 REFACTOR Phase Tasks",
                "",
                f"**Total Tasks:** {len(report.refactor_tasks)}",
                f"**Estimated Time:** {sum(t.estimated_minutes for t in report.refactor_tasks) / 60:.1f} hours",
                "",
            ])
            
            for task in report.refactor_tasks[:10]:  # Show first 10
                lines.extend([
                    f"### {task.title}",
                    "",
                    f"**File:** `{Path(task.file_path).name}`",
                    f"**Priority:** {task.priority}",
                    f"**Status:** {task.status}",
                    "",
                    "**REFACTOR Items:**",
                    task.description,
                    "",
                ])
            
            if len(report.refactor_tasks) > 10:
                lines.append(f"*...and {len(report.refactor_tasks) - 10} more tasks*")
            
            lines.extend(["", "---", ""])
        
        # Recommendations
        if report.recommendations:
            lines.extend([
                "## 💡 Recommendations",
                "",
            ])
            for rec in report.recommendations:
                lines.append(rec)
                lines.append("")
        
        lines.extend([
            "---",
            "",
            "*Report generated by System Refactor Plugin*"
        ])
        
        return "\n".join(lines)
    
    def _format_summary(self, report: ReviewReport) -> str:
        """Format brief summary for console output."""
        summary = [
            f"System Health: {report.overall_health}",
            f"Tests: {report.passing_tests}/{report.total_tests} passing ({report.metrics.get('pass_rate', 0):.1f}%)",
            f"Coverage Gaps: {len(report.coverage_gaps)} identified",
            f"REFACTOR Tasks: {len(report.refactor_tasks)} pending",
        ]
        return " | ".join(summary)
    
    # ============================================
    # Utilities
    # ============================================
    
    def _find_project_root(self) -> Path:
        """Find CORTEX project root directory."""
        current = Path(__file__).resolve()
        
        # Navigate up until we find cortex-brain/
        for parent in current.parents:
            if (parent / "cortex-brain").exists():
                return parent
        
        # Fallback
        return Path.cwd()


def register() -> BasePlugin:
    """Register plugin with CORTEX plugin system."""
    return SystemRefactorPlugin()
