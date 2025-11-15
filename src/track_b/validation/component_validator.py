"""
Component Validator for Track B

Validates individual CORTEX Track B components including execution channel,
intelligent context system, template integration, and platform optimization.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

import asyncio
import inspect
import importlib
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import logging

@dataclass
class ComponentValidationResult:
    """Result of component validation"""
    component_name: str
    status: str  # 'valid', 'invalid', 'warning', 'error'
    issues: List[str]
    metrics: Dict[str, Any]
    timestamp: float
    duration: float

@dataclass
class ComponentMetrics:
    """Metrics for component health assessment"""
    import_success: bool
    class_count: int
    function_count: int
    async_function_count: int
    dependency_count: int
    test_coverage: float
    performance_score: float
    complexity_score: float

class ComponentValidator:
    """
    Validates Track B components for correctness, completeness, and performance.
    
    Provides:
    - Import validation
    - API contract validation  
    - Performance assessment
    - Dependency analysis
    - Code quality metrics
    """
    
    def __init__(self, track_b_root: Optional[Path] = None):
        self.track_b_root = track_b_root or Path(__file__).parent.parent
        self.logger = self._setup_logging()
        self.validation_results: List[ComponentValidationResult] = []
        
    def _setup_logging(self) -> logging.Logger:
        """Configure component validator logging"""
        logger = logging.getLogger('component_validator')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    async def validate_all_components(self) -> Dict[str, Any]:
        """
        Validate all Track B components
        
        Returns:
            Comprehensive validation report
        """
        self.logger.info("Starting Track B component validation")
        start_time = time.time()
        
        # Define components to validate
        components = [
            "execution_channel",
            "intelligent_context",
            "template_system", 
            "platform",
            "validation"
        ]
        
        # Validate each component
        for component in components:
            await self._validate_component(component)
        
        # Generate summary
        duration = time.time() - start_time
        summary = self._generate_validation_summary(duration)
        
        self.logger.info(f"Component validation completed in {duration:.2f}s")
        return summary
    
    async def _validate_component(self, component_name: str):
        """Validate a specific component"""
        start_time = time.time()
        issues = []
        metrics = ComponentMetrics(
            import_success=False,
            class_count=0,
            function_count=0,
            async_function_count=0,
            dependency_count=0,
            test_coverage=0.0,
            performance_score=0.0,
            complexity_score=0.0
        )
        
        try:
            # Test import
            module_path = f"track_b.{component_name}"
            try:
                module = importlib.import_module(module_path)
                metrics.import_success = True
                self.logger.info(f"✓ {component_name} import successful")
            except ImportError as e:
                issues.append(f"Import failed: {e}")
                self.logger.error(f"✗ {component_name} import failed: {e}")
                
                # Try to validate structure without import
                await self._validate_component_structure(component_name, issues, metrics)
                
                result = ComponentValidationResult(
                    component_name=component_name,
                    status="invalid",
                    issues=issues,
                    metrics=metrics.__dict__,
                    timestamp=time.time(),
                    duration=time.time() - start_time
                )
                self.validation_results.append(result)
                return
            
            # Analyze module contents
            await self._analyze_module_contents(module, component_name, issues, metrics)
            
            # Validate API contracts
            await self._validate_api_contracts(module, component_name, issues)
            
            # Assess performance
            await self._assess_component_performance(module, component_name, metrics)
            
            # Calculate overall status
            status = self._determine_component_status(issues, metrics)
            
            result = ComponentValidationResult(
                component_name=component_name,
                status=status,
                issues=issues,
                metrics=metrics.__dict__,
                timestamp=time.time(),
                duration=time.time() - start_time
            )
            
            self.validation_results.append(result)
            
        except Exception as e:
            issues.append(f"Validation error: {e}")
            
            result = ComponentValidationResult(
                component_name=component_name,
                status="error",
                issues=issues,
                metrics=metrics.__dict__,
                timestamp=time.time(),
                duration=time.time() - start_time
            )
            self.validation_results.append(result)
    
    async def _validate_component_structure(self, component_name: str, issues: List[str], metrics: ComponentMetrics):
        """Validate component structure without importing"""
        component_path = self.track_b_root / component_name
        
        if not component_path.exists():
            issues.append(f"Component directory not found: {component_path}")
            return
        
        # Check for __init__.py
        init_file = component_path / "__init__.py"
        if not init_file.exists():
            issues.append(f"__init__.py missing in {component_name}")
        
        # Count Python files
        python_files = list(component_path.rglob("*.py"))
        if len(python_files) == 0:
            issues.append(f"No Python files found in {component_name}")
        
        # Basic structure validation
        expected_patterns = {
            "execution_channel": ["ambient_daemon", "file_monitor", "git_monitor", "terminal_tracker"],
            "intelligent_context": ["ml_analyzer", "proactive_warnings", "pattern_detector", "context_inference"],
            "template_system": ["template_engine", "response_generator", "template_optimizer"],
            "platform": ["macos_optimizer", "zsh_integration", "xcode_compat"],
            "validation": ["test_framework", "component_validator", "integration_tester", "merge_validator"]
        }
        
        if component_name in expected_patterns:
            for expected_file in expected_patterns[component_name]:
                expected_path = component_path / f"{expected_file}.py"
                if not expected_path.exists():
                    issues.append(f"Expected file missing: {expected_file}.py")
    
    async def _analyze_module_contents(self, module: Any, component_name: str, issues: List[str], metrics: ComponentMetrics):
        """Analyze module contents for classes, functions, etc."""
        try:
            # Count classes and functions
            for name in dir(module):
                if name.startswith('_'):
                    continue
                    
                attr = getattr(module, name)
                
                if inspect.isclass(attr):
                    metrics.class_count += 1
                elif inspect.isfunction(attr):
                    metrics.function_count += 1
                    if asyncio.iscoroutinefunction(attr):
                        metrics.async_function_count += 1
            
            # Check for required exports
            required_exports = {
                "execution_channel": ["AmbientDaemon", "FileMonitor", "GitMonitor", "TerminalTracker"],
                "intelligent_context": ["MLAnalyzer", "ProactiveWarnings", "PatternDetector", "ContextInference"],
                "template_system": ["TemplateEngine", "ResponseGenerator", "TemplateOptimizer"],
                "platform": ["MacOSOptimizer", "ZshIntegration", "XcodeCompatibility"],
                "validation": ["MacOSTestFramework", "ComponentValidator", "IntegrationTester", "MergeValidator"]
            }
            
            if component_name in required_exports:
                for required_export in required_exports[component_name]:
                    if not hasattr(module, required_export):
                        issues.append(f"Required export missing: {required_export}")
            
        except Exception as e:
            issues.append(f"Module analysis failed: {e}")
    
    async def _validate_api_contracts(self, module: Any, component_name: str, issues: List[str]):
        """Validate API contracts and interfaces"""
        try:
            # Check for common interface methods
            component_interfaces = {
                "execution_channel": {
                    "AmbientDaemon": ["start", "stop", "is_running"],
                    "FileMonitor": ["start_monitoring", "stop_monitoring", "add_watch"],
                    "GitMonitor": ["install_hooks", "uninstall_hooks", "get_status"],
                    "TerminalTracker": ["start_tracking", "stop_tracking", "get_activity"]
                },
                "intelligent_context": {
                    "MLAnalyzer": ["analyze_code", "get_insights", "train_model"],
                    "ProactiveWarnings": ["check_warnings", "add_rule", "get_active_warnings"],
                    "PatternDetector": ["detect_patterns", "learn_pattern", "get_confidence"],
                    "ContextInference": ["infer_context", "update_context", "get_context"]
                }
            }
            
            if component_name in component_interfaces:
                for class_name, methods in component_interfaces[component_name].items():
                    if hasattr(module, class_name):
                        cls = getattr(module, class_name)
                        for method_name in methods:
                            if not hasattr(cls, method_name):
                                issues.append(f"{class_name} missing method: {method_name}")
            
        except Exception as e:
            issues.append(f"API contract validation failed: {e}")
    
    async def _assess_component_performance(self, module: Any, component_name: str, metrics: ComponentMetrics):
        """Assess component performance characteristics"""
        try:
            # Simple performance scoring based on structure
            base_score = 70.0
            
            # Bonus for async support
            if metrics.async_function_count > 0:
                base_score += 10.0
            
            # Bonus for proper class organization
            if metrics.class_count >= 2:
                base_score += 10.0
            
            # Bonus for comprehensive API
            if metrics.function_count >= 5:
                base_score += 10.0
            
            metrics.performance_score = min(100.0, base_score)
            
            # Simple complexity scoring
            complexity = metrics.class_count + metrics.function_count * 0.5
            metrics.complexity_score = min(100.0, complexity)
            
        except Exception as e:
            self.logger.warning(f"Performance assessment failed for {component_name}: {e}")
            metrics.performance_score = 0.0
            metrics.complexity_score = 0.0
    
    def _determine_component_status(self, issues: List[str], metrics: ComponentMetrics) -> str:
        """Determine overall component status"""
        if not metrics.import_success:
            return "invalid"
        
        # Count issue severity
        critical_issues = len([issue for issue in issues if "missing" in issue.lower() or "failed" in issue.lower()])
        warning_issues = len(issues) - critical_issues
        
        if critical_issues > 0:
            return "invalid"
        elif warning_issues > 2:
            return "warning"
        elif metrics.performance_score < 50:
            return "warning"
        else:
            return "valid"
    
    def _generate_validation_summary(self, total_duration: float) -> Dict[str, Any]:
        """Generate validation summary report"""
        total_components = len(self.validation_results)
        valid_components = len([r for r in self.validation_results if r.status == "valid"])
        invalid_components = len([r for r in self.validation_results if r.status == "invalid"])
        warning_components = len([r for r in self.validation_results if r.status == "warning"])
        error_components = len([r for r in self.validation_results if r.status == "error"])
        
        health_score = (valid_components / total_components * 100) if total_components > 0 else 0
        
        # Aggregate metrics
        total_classes = sum(r.metrics.get('class_count', 0) for r in self.validation_results)
        total_functions = sum(r.metrics.get('function_count', 0) for r in self.validation_results)
        total_async_functions = sum(r.metrics.get('async_function_count', 0) for r in self.validation_results)
        avg_performance = sum(r.metrics.get('performance_score', 0) for r in self.validation_results) / total_components if total_components > 0 else 0
        
        return {
            "timestamp": time.time(),
            "duration": total_duration,
            "summary": {
                "total_components": total_components,
                "valid": valid_components,
                "invalid": invalid_components,
                "warnings": warning_components,
                "errors": error_components,
                "health_score": health_score
            },
            "aggregate_metrics": {
                "total_classes": total_classes,
                "total_functions": total_functions,
                "total_async_functions": total_async_functions,
                "average_performance_score": avg_performance
            },
            "component_results": [
                {
                    "component": r.component_name,
                    "status": r.status,
                    "issues_count": len(r.issues),
                    "performance_score": r.metrics.get('performance_score', 0),
                    "duration": r.duration
                } for r in self.validation_results
            ],
            "detailed_issues": {
                r.component_name: r.issues for r in self.validation_results if r.issues
            }
        }
    
    async def validate_component_dependencies(self, component_name: str) -> Dict[str, Any]:
        """Validate dependencies for a specific component"""
        try:
            component_path = self.track_b_root / component_name
            dependencies = []
            issues = []
            
            # Scan Python files for imports
            for py_file in component_path.rglob("*.py"):
                try:
                    content = py_file.read_text()
                    lines = content.split('\n')
                    
                    for line in lines:
                        line = line.strip()
                        if line.startswith('import ') or line.startswith('from '):
                            # Extract import
                            if 'import' in line:
                                parts = line.split()
                                if len(parts) >= 2:
                                    module_name = parts[1].split('.')[0]
                                    if module_name not in dependencies:
                                        dependencies.append(module_name)
                
                except Exception as e:
                    issues.append(f"Failed to scan {py_file}: {e}")
            
            # Validate dependencies
            missing_deps = []
            for dep in dependencies:
                if dep in ['sys', 'os', 'pathlib', 'typing', 'dataclasses', 'asyncio']:
                    continue  # Standard library
                
                try:
                    importlib.import_module(dep)
                except ImportError:
                    missing_deps.append(dep)
            
            return {
                "component": component_name,
                "dependencies": dependencies,
                "missing_dependencies": missing_deps,
                "issues": issues,
                "dependency_health": len(missing_deps) == 0
            }
            
        except Exception as e:
            return {
                "component": component_name,
                "error": str(e),
                "dependency_health": False
            }
    
    def get_component_health_report(self) -> Dict[str, Any]:
        """Get comprehensive component health report"""
        if not self.validation_results:
            return {"error": "No validation results available"}
        
        # Component health scores
        component_scores = {}
        for result in self.validation_results:
            score = 100.0
            
            # Deduct for issues
            score -= len(result.issues) * 10
            
            # Factor in performance
            perf_score = result.metrics.get('performance_score', 0)
            score = (score + perf_score) / 2
            
            # Minimum score of 0
            component_scores[result.component_name] = max(0, score)
        
        overall_health = sum(component_scores.values()) / len(component_scores)
        
        return {
            "overall_health_score": overall_health,
            "component_scores": component_scores,
            "health_status": "excellent" if overall_health >= 90 else "good" if overall_health >= 70 else "fair" if overall_health >= 50 else "poor",
            "recommendations": self._generate_health_recommendations(component_scores)
        }
    
    def _generate_health_recommendations(self, component_scores: Dict[str, float]) -> List[str]:
        """Generate health improvement recommendations"""
        recommendations = []
        
        # Find components with low scores
        for component, score in component_scores.items():
            if score < 50:
                recommendations.append(f"Critical: {component} needs immediate attention (score: {score:.1f})")
            elif score < 70:
                recommendations.append(f"Warning: {component} needs improvement (score: {score:.1f})")
        
        # General recommendations
        if all(score >= 80 for score in component_scores.values()):
            recommendations.append("All components are in good health")
        
        return recommendations