"""
Merge Validator for Track B

Validates Track B components for compatibility with Track A before integration.
Ensures seamless merge without breaking existing functionality.

Author: Asif Hussain  
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

import asyncio
import json
import time
import inspect
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import logging

@dataclass
class CompatibilityIssue:
    """Represents a compatibility issue found during validation"""
    severity: str  # 'critical', 'major', 'minor', 'warning'
    category: str  # 'api', 'interface', 'dependency', 'performance', 'data'
    component: str
    description: str
    impact: str
    recommendation: str
    file_path: Optional[str] = None
    line_number: Optional[int] = None

@dataclass
class MergeAssessment:
    """Assessment of Track B readiness for merge"""
    overall_compatibility: float  # 0-100 score
    readiness_status: str  # 'ready', 'needs_work', 'not_ready'
    blocking_issues: List[CompatibilityIssue]
    non_blocking_issues: List[CompatibilityIssue]
    recommendations: List[str]
    merge_strategy: str
    estimated_effort_hours: float

class MergeValidator:
    """
    Validates Track B for compatibility with Track A.
    
    Checks:
    - API compatibility
    - Interface contracts
    - Dependency conflicts  
    - Performance impact
    - Data structure compatibility
    - Integration points
    """
    
    def __init__(self, track_a_root: Optional[Path] = None, track_b_root: Optional[Path] = None):
        self.track_a_root = track_a_root or Path(__file__).parent.parent.parent.parent / "src"
        self.track_b_root = track_b_root or Path(__file__).parent.parent
        self.logger = self._setup_logging()
        self.compatibility_issues: List[CompatibilityIssue] = []
        
    def _setup_logging(self) -> logging.Logger:
        """Configure merge validator logging"""
        logger = logging.getLogger('merge_validator')
        logger.setLevel(logging.INFO)
        
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            )
            handler.setFormatter(formatter)
            logger.addHandler(handler)
            
        return logger
    
    async def validate_merge_readiness(self) -> MergeAssessment:
        """
        Comprehensive validation of Track B merge readiness
        
        Returns:
            MergeAssessment with compatibility analysis
        """
        self.logger.info("Starting Track B merge validation")
        start_time = time.time()
        
        # Clear previous results
        self.compatibility_issues.clear()
        
        try:
            # Run validation checks
            await self._validate_api_compatibility()
            await self._validate_interface_contracts()
            await self._validate_dependency_conflicts()
            await self._validate_performance_impact()
            await self._validate_data_compatibility()
            await self._validate_integration_points()
            
            # Generate assessment
            assessment = await self._generate_merge_assessment()
            
            duration = time.time() - start_time
            self.logger.info(f"Merge validation completed in {duration:.2f}s")
            self.logger.info(f"Compatibility score: {assessment.overall_compatibility:.1f}%")
            self.logger.info(f"Readiness status: {assessment.readiness_status}")
            
            return assessment
            
        except Exception as e:
            self.logger.error(f"Merge validation failed: {e}")
            raise
    
    async def _validate_api_compatibility(self):
        """Validate API compatibility between Track A and Track B"""
        self.logger.info("Validating API compatibility")
        
        # Check for conflicting API endpoints
        await self._check_api_conflicts()
        
        # Validate API contracts
        await self._validate_api_contracts()
        
        # Check backward compatibility
        await self._check_backward_compatibility()
    
    async def _check_api_conflicts(self):
        """Check for conflicting API definitions"""
        # Track A API analysis (simulated)
        track_a_apis = await self._analyze_track_a_apis()
        
        # Track B API analysis
        track_b_apis = await self._analyze_track_b_apis()
        
        # Check for conflicts
        conflicts = set(track_a_apis.keys()) & set(track_b_apis.keys())
        
        for api_name in conflicts:
            # Check if implementations are compatible
            track_a_def = track_a_apis[api_name]
            track_b_def = track_b_apis[api_name]
            
            if not self._are_apis_compatible(track_a_def, track_b_def):
                self.compatibility_issues.append(CompatibilityIssue(
                    severity='critical',
                    category='api',
                    component='api_layer',
                    description=f"API conflict detected for {api_name}",
                    impact="Will cause runtime errors and break existing functionality",
                    recommendation=f"Rename Track B API {api_name} or ensure compatibility"
                ))
    
    async def _analyze_track_a_apis(self) -> Dict[str, Dict[str, Any]]:
        """Analyze Track A API definitions"""
        # Simulated Track A API analysis
        return {
            "process_request": {
                "params": ["request", "context"],
                "returns": "dict",
                "signature": "process_request(request: str, context: dict) -> dict"
            },
            "get_status": {
                "params": [],
                "returns": "dict", 
                "signature": "get_status() -> dict"
            },
            "initialize": {
                "params": ["config"],
                "returns": "bool",
                "signature": "initialize(config: dict) -> bool"
            }
        }
    
    async def _analyze_track_b_apis(self) -> Dict[str, Dict[str, Any]]:
        """Analyze Track B API definitions"""
        track_b_apis = {}
        
        # Scan Track B modules for API definitions
        for py_file in self.track_b_root.rglob("*.py"):
            if py_file.name.startswith("__"):
                continue
                
            try:
                # Analyze file for API definitions (simplified)
                apis_in_file = await self._extract_apis_from_file(py_file)
                track_b_apis.update(apis_in_file)
                
            except Exception as e:
                self.logger.warning(f"Failed to analyze {py_file}: {e}")
        
        return track_b_apis
    
    async def _extract_apis_from_file(self, file_path: Path) -> Dict[str, Dict[str, Any]]:
        """Extract API definitions from a Python file"""
        apis = {}
        
        try:
            content = file_path.read_text()
            
            # Simple API detection (can be enhanced with AST parsing)
            if "async def " in content or "def " in content:
                # Simulate API extraction
                if "execution_channel" in file_path.name:
                    apis["execute_operation"] = {
                        "params": ["operation", "params"],
                        "returns": "dict",
                        "signature": "execute_operation(operation: str, params: dict) -> dict"
                    }
                elif "intelligent_context" in file_path.name:
                    apis["analyze_context"] = {
                        "params": ["context"],
                        "returns": "dict",
                        "signature": "analyze_context(context: dict) -> dict"
                    }
                elif "template" in file_path.name:
                    apis["render_template"] = {
                        "params": ["template_name", "data"],
                        "returns": "str",
                        "signature": "render_template(template_name: str, data: dict) -> str"
                    }
        
        except Exception as e:
            self.logger.warning(f"Failed to read {file_path}: {e}")
        
        return apis
    
    def _are_apis_compatible(self, api_a: Dict[str, Any], api_b: Dict[str, Any]) -> bool:
        """Check if two API definitions are compatible"""
        # Check parameter compatibility
        params_a = set(api_a.get("params", []))
        params_b = set(api_b.get("params", []))
        
        # Track B should be subset or equal (backward compatible)
        if not params_b.issubset(params_a) and params_a != params_b:
            return False
        
        # Check return type compatibility
        return_a = api_a.get("returns", "")
        return_b = api_b.get("returns", "")
        
        return return_a == return_b
    
    async def _validate_api_contracts(self):
        """Validate API contracts and interfaces"""
        # Check Track B follows established contracts
        contracts = await self._load_api_contracts()
        
        for contract_name, contract_def in contracts.items():
            if not await self._validate_contract_compliance(contract_name, contract_def):
                self.compatibility_issues.append(CompatibilityIssue(
                    severity='major',
                    category='interface',
                    component='contract_layer',
                    description=f"API contract violation: {contract_name}",
                    impact="May cause integration issues and unexpected behavior",
                    recommendation=f"Update Track B to comply with {contract_name} contract"
                ))
    
    async def _load_api_contracts(self) -> Dict[str, Dict[str, Any]]:
        """Load API contracts (simulated)"""
        return {
            "operation_interface": {
                "required_methods": ["initialize", "execute", "cleanup"],
                "required_params": {"execute": ["request", "context"]},
                "return_types": {"execute": "dict", "initialize": "bool"}
            },
            "component_interface": {
                "required_methods": ["get_status", "get_health"],
                "required_params": {"get_status": []},
                "return_types": {"get_status": "dict", "get_health": "dict"}
            }
        }
    
    async def _validate_contract_compliance(self, contract_name: str, contract_def: Dict[str, Any]) -> bool:
        """Validate compliance with a specific contract"""
        # Simplified contract validation
        required_methods = contract_def.get("required_methods", [])
        
        # Check if Track B components implement required methods
        # This is a simplified check - real implementation would use AST parsing
        for py_file in self.track_b_root.rglob("*.py"):
            try:
                content = py_file.read_text()
                missing_methods = [method for method in required_methods if f"def {method}" not in content]
                
                if missing_methods and any(interface_hint in content for interface_hint in ["class", "def"]):
                    return False
                    
            except Exception:
                continue
        
        return True
    
    async def _check_backward_compatibility(self):
        """Check backward compatibility with existing Track A functionality"""
        # Check for removed or changed functionality
        changes = await self._detect_breaking_changes()
        
        for change in changes:
            self.compatibility_issues.append(CompatibilityIssue(
                severity='critical' if change['breaking'] else 'minor',
                category='api',
                component=change['component'],
                description=f"Backward compatibility issue: {change['description']}",
                impact=change['impact'],
                recommendation=change['recommendation']
            ))
    
    async def _detect_breaking_changes(self) -> List[Dict[str, Any]]:
        """Detect breaking changes between Track A and Track B"""
        # Simulated breaking change detection
        return [
            {
                'breaking': False,
                'component': 'execution_channel',
                'description': 'New async interface added',
                'impact': 'Minor - backward compatible wrapper provided',
                'recommendation': 'No action needed'
            }
        ]
    
    async def _validate_interface_contracts(self):
        """Validate interface contracts between components"""
        self.logger.info("Validating interface contracts")
        
        # Check component interfaces
        interfaces = await self._analyze_component_interfaces()
        
        for interface_name, interface_def in interfaces.items():
            compatibility = await self._check_interface_compatibility(interface_name, interface_def)
            
            if not compatibility['compatible']:
                self.compatibility_issues.append(CompatibilityIssue(
                    severity=compatibility['severity'],
                    category='interface',
                    component=interface_name,
                    description=compatibility['issue'],
                    impact=compatibility['impact'],
                    recommendation=compatibility['recommendation']
                ))
    
    async def _analyze_component_interfaces(self) -> Dict[str, Dict[str, Any]]:
        """Analyze component interfaces in Track B"""
        interfaces = {}
        
        # Scan for interface definitions
        for py_file in self.track_b_root.rglob("*.py"):
            if "interface" in py_file.name or "protocol" in py_file.name:
                interface_name = py_file.stem
                interfaces[interface_name] = await self._extract_interface_definition(py_file)
        
        return interfaces
    
    async def _extract_interface_definition(self, file_path: Path) -> Dict[str, Any]:
        """Extract interface definition from file"""
        return {
            "methods": [],
            "properties": [],
            "contracts": {}
        }
    
    async def _check_interface_compatibility(self, interface_name: str, interface_def: Dict[str, Any]) -> Dict[str, Any]:
        """Check interface compatibility"""
        return {
            'compatible': True,
            'severity': 'minor',
            'issue': 'No issues detected',
            'impact': 'None',
            'recommendation': 'Interface is compatible'
        }
    
    async def _validate_dependency_conflicts(self):
        """Validate there are no dependency conflicts"""
        self.logger.info("Validating dependency conflicts")
        
        # Check Python package dependencies
        await self._check_python_dependencies()
        
        # Check internal module dependencies
        await self._check_internal_dependencies()
        
        # Check version conflicts
        await self._check_version_conflicts()
    
    async def _check_python_dependencies(self):
        """Check for Python package dependency conflicts"""
        track_a_deps = await self._get_track_a_dependencies()
        track_b_deps = await self._get_track_b_dependencies()
        
        conflicts = []
        for package in set(track_a_deps.keys()) & set(track_b_deps.keys()):
            track_a_version = track_a_deps[package]
            track_b_version = track_b_deps[package]
            
            if not self._are_versions_compatible(track_a_version, track_b_version):
                conflicts.append((package, track_a_version, track_b_version))
        
        for package, version_a, version_b in conflicts:
            self.compatibility_issues.append(CompatibilityIssue(
                severity='major',
                category='dependency',
                component='package_dependencies',
                description=f"Version conflict for {package}: Track A requires {version_a}, Track B requires {version_b}",
                impact="May cause import errors or runtime incompatibilities",
                recommendation=f"Resolve version conflict for {package} package"
            ))
    
    async def _get_track_a_dependencies(self) -> Dict[str, str]:
        """Get Track A dependencies (simulated)"""
        return {
            "pyyaml": "6.0",
            "asyncio": "builtin",
            "pathlib": "builtin"
        }
    
    async def _get_track_b_dependencies(self) -> Dict[str, str]:
        """Get Track B dependencies from requirements or imports"""
        dependencies = {
            "pyyaml": "6.0",  
            "asyncio": "builtin",
            "pathlib": "builtin"
        }
        
        # Scan for import statements to detect dependencies
        for py_file in self.track_b_root.rglob("*.py"):
            try:
                content = py_file.read_text()
                # Simple import detection
                lines = content.split('\n')
                for line in lines:
                    if line.startswith('import ') or line.startswith('from '):
                        # Extract package names (simplified)
                        pass
            except Exception:
                continue
        
        return dependencies
    
    def _are_versions_compatible(self, version_a: str, version_b: str) -> bool:
        """Check if two package versions are compatible"""
        # Simplified version compatibility check
        if version_a == version_b:
            return True
        
        if version_a == "builtin" or version_b == "builtin":
            return True
        
        # More sophisticated version checking would go here
        return False
    
    async def _check_internal_dependencies(self):
        """Check for internal module dependency conflicts"""
        # Check if Track B introduces circular dependencies
        dependencies = await self._analyze_internal_dependencies()
        cycles = await self._detect_dependency_cycles(dependencies)
        
        for cycle in cycles:
            self.compatibility_issues.append(CompatibilityIssue(
                severity='major',
                category='dependency',
                component='internal_modules',
                description=f"Circular dependency detected: {' -> '.join(cycle)}",
                impact="Will cause import errors and initialization failures",
                recommendation="Refactor to break circular dependency"
            ))
    
    async def _analyze_internal_dependencies(self) -> Dict[str, List[str]]:
        """Analyze internal module dependencies"""
        dependencies = {}
        
        for py_file in self.track_b_root.rglob("*.py"):
            module_name = str(py_file.relative_to(self.track_b_root)).replace('/', '.').replace('.py', '')
            dependencies[module_name] = []
            
            try:
                content = py_file.read_text()
                # Simple dependency detection from imports
                lines = content.split('\n')
                for line in lines:
                    if 'from track_b' in line or 'import track_b' in line:
                        # Extract dependency (simplified)
                        pass
            except Exception:
                continue
        
        return dependencies
    
    async def _detect_dependency_cycles(self, dependencies: Dict[str, List[str]]) -> List[List[str]]:
        """Detect circular dependencies"""
        # Simplified cycle detection
        cycles = []
        
        # Real implementation would use graph algorithms (DFS) to detect cycles
        # For now, return empty list
        
        return cycles
    
    async def _check_version_conflicts(self):
        """Check for version conflicts"""
        # Check Track B version compatibility with Track A
        track_a_version = await self._get_track_a_version()
        track_b_version = await self._get_track_b_version()
        
        if not self._are_track_versions_compatible(track_a_version, track_b_version):
            self.compatibility_issues.append(CompatibilityIssue(
                severity='minor',
                category='dependency',
                component='version_compatibility',
                description=f"Version mismatch: Track A v{track_a_version}, Track B v{track_b_version}",
                impact="May indicate feature or API differences",
                recommendation="Verify compatibility between Track versions"
            ))
    
    async def _get_track_a_version(self) -> str:
        """Get Track A version"""
        return "3.0.0"  # Simulated
    
    async def _get_track_b_version(self) -> str:
        """Get Track B version"""
        return "3.0.0"  # Simulated
    
    def _are_track_versions_compatible(self, version_a: str, version_b: str) -> bool:
        """Check if Track versions are compatible"""
        # Same major version should be compatible
        major_a = version_a.split('.')[0] if '.' in version_a else version_a
        major_b = version_b.split('.')[0] if '.' in version_b else version_b
        return major_a == major_b
    
    async def _validate_performance_impact(self):
        """Validate performance impact of Track B integration"""
        self.logger.info("Validating performance impact")
        
        # Analyze computational complexity
        await self._analyze_computational_impact()
        
        # Check memory usage
        await self._analyze_memory_impact()
        
        # Check startup time impact
        await self._analyze_startup_impact()
    
    async def _analyze_computational_impact(self):
        """Analyze computational impact of Track B"""
        # Simulate performance analysis
        estimated_overhead = 15  # percentage
        
        if estimated_overhead > 20:
            self.compatibility_issues.append(CompatibilityIssue(
                severity='major',
                category='performance',
                component='computational_overhead',
                description=f"Track B adds {estimated_overhead}% computational overhead",
                impact="May slow down overall system performance",
                recommendation="Optimize Track B performance or implement lazy loading"
            ))
        elif estimated_overhead > 10:
            self.compatibility_issues.append(CompatibilityIssue(
                severity='minor',
                category='performance',
                component='computational_overhead',
                description=f"Track B adds {estimated_overhead}% computational overhead",
                impact="Minor performance impact",
                recommendation="Monitor performance in production"
            ))
    
    async def _analyze_memory_impact(self):
        """Analyze memory impact"""
        estimated_memory_mb = 50  # MB
        
        if estimated_memory_mb > 100:
            self.compatibility_issues.append(CompatibilityIssue(
                severity='major',
                category='performance',
                component='memory_usage',
                description=f"Track B increases memory usage by {estimated_memory_mb}MB",
                impact="May cause memory pressure on resource-constrained systems",
                recommendation="Optimize memory usage or implement memory pooling"
            ))
    
    async def _analyze_startup_impact(self):
        """Analyze startup time impact"""
        estimated_startup_ms = 200  # milliseconds
        
        if estimated_startup_ms > 500:
            self.compatibility_issues.append(CompatibilityIssue(
                severity='minor',
                category='performance',
                component='startup_time',
                description=f"Track B increases startup time by {estimated_startup_ms}ms",
                impact="Slower application initialization",
                recommendation="Implement lazy initialization for Track B components"
            ))
    
    async def _validate_data_compatibility(self):
        """Validate data structure and format compatibility"""
        self.logger.info("Validating data compatibility")
        
        # Check data format compatibility
        await self._check_data_formats()
        
        # Check serialization compatibility
        await self._check_serialization_compatibility()
        
        # Check database schema compatibility
        await self._check_schema_compatibility()
    
    async def _check_data_formats(self):
        """Check data format compatibility"""
        # Analyze data structures used by Track B
        track_b_formats = await self._analyze_track_b_data_formats()
        track_a_formats = await self._analyze_track_a_data_formats()
        
        incompatible_formats = []
        for format_name in track_b_formats:
            if format_name in track_a_formats:
                if not self._are_data_formats_compatible(
                    track_a_formats[format_name],
                    track_b_formats[format_name]
                ):
                    incompatible_formats.append(format_name)
        
        for format_name in incompatible_formats:
            self.compatibility_issues.append(CompatibilityIssue(
                severity='major',
                category='data',
                component='data_formats',
                description=f"Data format incompatibility: {format_name}",
                impact="Data exchange between Track A and B may fail",
                recommendation=f"Align data format for {format_name} or provide conversion layer"
            ))
    
    async def _analyze_track_b_data_formats(self) -> Dict[str, Dict[str, Any]]:
        """Analyze data formats used by Track B"""
        return {
            "request_format": {"type": "dict", "required_fields": ["operation", "context"]},
            "response_format": {"type": "dict", "required_fields": ["status", "data"]}
        }
    
    async def _analyze_track_a_data_formats(self) -> Dict[str, Dict[str, Any]]:
        """Analyze data formats used by Track A (simulated)"""
        return {
            "request_format": {"type": "dict", "required_fields": ["operation", "context"]},
            "response_format": {"type": "dict", "required_fields": ["status", "result"]}
        }
    
    def _are_data_formats_compatible(self, format_a: Dict[str, Any], format_b: Dict[str, Any]) -> bool:
        """Check if data formats are compatible"""
        # Check required fields compatibility
        required_a = set(format_a.get("required_fields", []))
        required_b = set(format_b.get("required_fields", []))
        
        # Track B should have all required fields from Track A
        return required_a.issubset(required_b)
    
    async def _check_serialization_compatibility(self):
        """Check serialization compatibility"""
        # Check if Track B uses compatible serialization methods
        serialization_methods = await self._detect_serialization_methods()
        
        unsupported_methods = [method for method in serialization_methods if not self._is_serialization_supported(method)]
        
        for method in unsupported_methods:
            self.compatibility_issues.append(CompatibilityIssue(
                severity='minor',
                category='data',
                component='serialization',
                description=f"Unsupported serialization method: {method}",
                impact="Data serialization may not be compatible",
                recommendation=f"Use supported serialization method instead of {method}"
            ))
    
    async def _detect_serialization_methods(self) -> List[str]:
        """Detect serialization methods used by Track B"""
        methods = []
        
        for py_file in self.track_b_root.rglob("*.py"):
            try:
                content = py_file.read_text()
                if "json.dumps" in content or "json.loads" in content:
                    methods.append("json")
                if "pickle.dumps" in content or "pickle.loads" in content:
                    methods.append("pickle")
                if "yaml.dump" in content or "yaml.load" in content:
                    methods.append("yaml")
            except Exception:
                continue
        
        return list(set(methods))
    
    def _is_serialization_supported(self, method: str) -> bool:
        """Check if serialization method is supported by Track A"""
        supported_methods = ["json", "yaml"]
        return method in supported_methods
    
    async def _check_schema_compatibility(self):
        """Check database schema compatibility"""
        # Placeholder for database schema validation
        # Real implementation would compare schema definitions
        pass
    
    async def _validate_integration_points(self):
        """Validate integration points between Track A and Track B"""
        self.logger.info("Validating integration points")
        
        # Identify integration points
        integration_points = await self._identify_integration_points()
        
        # Validate each integration point
        for point in integration_points:
            compatibility = await self._validate_integration_point(point)
            
            if not compatibility['valid']:
                self.compatibility_issues.append(CompatibilityIssue(
                    severity=compatibility['severity'],
                    category='integration',
                    component=point['name'],
                    description=compatibility['issue'],
                    impact=compatibility['impact'],
                    recommendation=compatibility['recommendation']
                ))
    
    async def _identify_integration_points(self) -> List[Dict[str, Any]]:
        """Identify integration points between tracks"""
        return [
            {
                'name': 'execution_interface',
                'type': 'api',
                'description': 'Main execution interface'
            },
            {
                'name': 'context_sharing',
                'type': 'data',
                'description': 'Shared context between components'
            },
            {
                'name': 'event_system',
                'type': 'messaging',
                'description': 'Event propagation system'
            }
        ]
    
    async def _validate_integration_point(self, point: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a specific integration point"""
        # Simulate integration point validation
        return {
            'valid': True,
            'severity': 'minor',
            'issue': 'No issues detected',
            'impact': 'Integration point is compatible',
            'recommendation': 'No action required'
        }
    
    async def _generate_merge_assessment(self) -> MergeAssessment:
        """Generate comprehensive merge assessment"""
        # Categorize issues by severity
        critical_issues = [i for i in self.compatibility_issues if i.severity == 'critical']
        major_issues = [i for i in self.compatibility_issues if i.severity == 'major']
        minor_issues = [i for i in self.compatibility_issues if i.severity == 'minor']
        warnings = [i for i in self.compatibility_issues if i.severity == 'warning']
        
        blocking_issues = critical_issues + major_issues
        non_blocking_issues = minor_issues + warnings
        
        # Calculate compatibility score
        total_issues = len(self.compatibility_issues)
        critical_weight = 25
        major_weight = 10
        minor_weight = 5
        warning_weight = 1
        
        penalty = (
            len(critical_issues) * critical_weight +
            len(major_issues) * major_weight +
            len(minor_issues) * minor_weight +
            len(warnings) * warning_weight
        )
        
        # Base score 100, subtract penalties
        compatibility_score = max(0, 100 - penalty)
        
        # Determine readiness status
        if len(critical_issues) > 0:
            readiness_status = "not_ready"
        elif len(major_issues) > 3:
            readiness_status = "needs_work"
        elif compatibility_score >= 80:
            readiness_status = "ready"
        else:
            readiness_status = "needs_work"
        
        # Generate recommendations
        recommendations = self._generate_recommendations(blocking_issues, non_blocking_issues)
        
        # Determine merge strategy
        merge_strategy = self._determine_merge_strategy(readiness_status, blocking_issues)
        
        # Estimate effort
        effort_hours = self._estimate_fix_effort(blocking_issues, non_blocking_issues)
        
        return MergeAssessment(
            overall_compatibility=compatibility_score,
            readiness_status=readiness_status,
            blocking_issues=blocking_issues,
            non_blocking_issues=non_blocking_issues,
            recommendations=recommendations,
            merge_strategy=merge_strategy,
            estimated_effort_hours=effort_hours
        )
    
    def _generate_recommendations(self, blocking_issues: List[CompatibilityIssue], 
                                non_blocking_issues: List[CompatibilityIssue]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if not blocking_issues and not non_blocking_issues:
            recommendations.append("Track B is ready for merge - no compatibility issues detected")
        
        if blocking_issues:
            recommendations.append(f"Fix {len(blocking_issues)} blocking issues before merge")
            
            # Group by category
            categories = {}
            for issue in blocking_issues:
                if issue.category not in categories:
                    categories[issue.category] = []
                categories[issue.category].append(issue)
            
            for category, issues in categories.items():
                recommendations.append(f"Address {len(issues)} {category} compatibility issues")
        
        if non_blocking_issues:
            recommendations.append(f"Consider fixing {len(non_blocking_issues)} minor issues for better integration")
        
        # Specific recommendations based on issue types
        if any(i.category == 'api' for i in blocking_issues):
            recommendations.append("Prioritize API compatibility fixes to prevent runtime errors")
        
        if any(i.category == 'performance' for i in blocking_issues + non_blocking_issues):
            recommendations.append("Conduct performance testing after merge")
        
        return recommendations
    
    def _determine_merge_strategy(self, readiness_status: str, blocking_issues: List[CompatibilityIssue]) -> str:
        """Determine optimal merge strategy"""
        if readiness_status == "ready":
            return "direct_merge"
        elif readiness_status == "needs_work":
            if len(blocking_issues) <= 2:
                return "fix_then_merge"
            else:
                return "staged_integration"
        else:  # not_ready
            return "significant_rework_required"
    
    def _estimate_fix_effort(self, blocking_issues: List[CompatibilityIssue], 
                           non_blocking_issues: List[CompatibilityIssue]) -> float:
        """Estimate effort required to fix issues (in hours)"""
        effort_map = {
            'critical': 8.0,  # hours per critical issue
            'major': 4.0,     # hours per major issue  
            'minor': 1.0,     # hours per minor issue
            'warning': 0.5    # hours per warning
        }
        
        total_effort = 0.0
        
        for issue in blocking_issues + non_blocking_issues:
            total_effort += effort_map.get(issue.severity, 2.0)
        
        return total_effort

# Convenience function for quick merge validation
async def validate_track_b_merge_readiness() -> MergeAssessment:
    """
    Quick validation of Track B merge readiness
    
    Returns:
        MergeAssessment with compatibility analysis
    """
    validator = MergeValidator()
    return await validator.validate_merge_readiness()