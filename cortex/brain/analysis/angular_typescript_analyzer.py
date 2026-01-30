"""
Phase 8.5: Angular/TypeScript Analyzer for LENS Intelligence

Analyzes Angular/TypeScript code for components, services, and edge cases.
Provides CORTEX LENS with expert knowledge of Angular patterns and anti-patterns.

AC-ID: AC-PHASE-8.5-03 (Task LENS-MS-003)

CORE Governance:
  - CORE-008: TDD - Tests provided first
  - CORE-011: Type hints on all methods
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-027: Audit trail logging

Author: Asif Hussain
Created: 2026-01-30
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path
import re
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger


@dataclass
class AngularAnalysisResult:
    """
    Result of Angular/TypeScript code analysis.
    
    Attributes:
        file_path: Path to analyzed file
        components: List of Angular components
        services: List of services
        observables: RxJS observable usage
        http_calls: HTTP client calls
        router_config: Router configuration
        edge_cases: Detected edge cases and anti-patterns
        complexity_score: Overall complexity (0-100)
    """
    file_path: str
    components: List[Dict[str, Any]]
    services: List[Dict[str, Any]]
    observables: List[Dict[str, Any]]
    http_calls: List[Dict[str, Any]]
    router_config: List[Dict[str, Any]]
    edge_cases: List[Dict[str, Any]]
    complexity_score: int


class AngularTypeScriptAnalyzer:
    """
    Analyzes Angular/TypeScript code for structure, patterns, and edge cases.
    
    Expert in:
    - Angular components (lifecycle hooks, templates)
    - RxJS observables (subscriptions, memory leaks)
    - Router configuration (lazy loading, guards)
    - HTTP client (error handling, interceptors)
    - Edge cases (unsafe innerHTML, memory leaks, unsubscribed observables)
    
    Example:
        analyzer = AngularTypeScriptAnalyzer()
        result = analyzer.analyze_file(Path("app.component.ts"))
        
        print(f"Components: {len(result.components)}")
        print(f"Observables: {len(result.observables)}")
        print(f"Edge cases: {len(result.edge_cases)}")
    """
    
    def __init__(self) -> None:
        """Initialize Angular/TypeScript analyzer."""
        self.logger = EnhancedAuditLogger.instance()
        
        # Angular pattern regexes
        self.patterns = {
            "component": re.compile(r"@Component\s*\(\{"),
            "service": re.compile(r"@Injectable\s*\(\{"),
            "observable": re.compile(r"Observable<|\.subscribe\(|\.pipe\("),
            "http_call": re.compile(r"this\.http\.(get|post|put|delete|patch)"),
            "router": re.compile(r"RouterModule\.forRoot|RouterModule\.forChild"),
            "lifecycle": re.compile(r"(ngOnInit|ngOnDestroy|ngAfterViewInit|ngOnChanges)"),
            "unsubscribe": re.compile(r"\.unsubscribe\(\)|takeUntil|take\("),
            "inner_html": re.compile(r"\[innerHTML\]|\binnerHTML\s*="),
            "any_type": re.compile(r":\s*any\b"),
        }
        
        self.logger.log_operation_complete(
            ac_id="AC-PHASE-8.5-03",
            operation="ANGULAR_ANALYZER_INIT",
            success=True,
            details={"patterns_loaded": len(self.patterns)},
        )
    
    def analyze_file(self, file_path: Path) -> AngularAnalysisResult:
        """
        Analyze Angular/TypeScript file for structure and patterns.
        
        AC-PHASE-8.5-03: Extract Angular code intelligence
        
        Args:
            file_path: Path to TypeScript source file
        
        Returns:
            AngularAnalysisResult: Analysis results with edge cases
        
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not TypeScript (.ts extension)
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if file_path.suffix.lower() != ".ts":
            raise ValueError(f"Not a TypeScript file: {file_path}")
        
        try:
            # Read file content
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")
            
            # Extract components
            components = self._extract_components(content, lines)
            services = self._extract_services(content, lines)
            observables = self._extract_observables(content, lines)
            http_calls = self._extract_http_calls(content, lines)
            router_config = self._extract_router_config(content, lines)
            
            # Detect edge cases
            edge_cases = self._detect_edge_cases(content, lines)
            
            # Calculate complexity
            complexity = self._calculate_complexity(
                len(components), len(services), len(observables), len(http_calls)
            )
            
            result = AngularAnalysisResult(
                file_path=str(file_path),
                components=components,
                services=services,
                observables=observables,
                http_calls=http_calls,
                router_config=router_config,
                edge_cases=edge_cases,
                complexity_score=complexity,
            )
            
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.5-03",
                operation="ANGULAR_ANALYSIS_COMPLETE",
                success=True,
                details={
                    "file": str(file_path),
                    "components": len(components),
                    "observables": len(observables),
                    "edge_cases": len(edge_cases),
                    "complexity": complexity,
                },
            )
            
            return result
        
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.5-03",
                operation="ANGULAR_ANALYSIS_ERROR",
                success=False,
                details={"file": str(file_path), "error": str(e)},
            )
            raise
    
    def _extract_components(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract Angular component definitions."""
        components = []
        for i, line in enumerate(lines, 1):
            if self.patterns["component"].search(line):
                # Extract component class name (next ~10 lines)
                class_name = None
                for j in range(i, min(i + 10, len(lines))):
                    class_match = re.search(r"export\s+class\s+(\w+)", lines[j])
                    if class_match:
                        class_name = class_match.group(1)
                        break
                
                components.append({
                    "name": class_name or "UnknownComponent",
                    "line": i,
                    "type": "component",
                })
        return components
    
    def _extract_services(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract service definitions."""
        services = []
        for i, line in enumerate(lines, 1):
            if self.patterns["service"].search(line):
                class_name = None
                for j in range(i, min(i + 10, len(lines))):
                    class_match = re.search(r"export\s+class\s+(\w+)", lines[j])
                    if class_match:
                        class_name = class_match.group(1)
                        break
                
                services.append({
                    "name": class_name or "UnknownService",
                    "line": i,
                    "type": "service",
                })
        return services
    
    def _extract_observables(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract RxJS observable usage."""
        observables = []
        for i, line in enumerate(lines, 1):
            if self.patterns["observable"].search(line):
                observables.append({
                    "line": i,
                    "snippet": line.strip(),
                    "has_subscribe": ".subscribe(" in line,
                    "has_pipe": ".pipe(" in line,
                })
        return observables
    
    def _extract_http_calls(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract HTTP client calls."""
        http_calls = []
        for i, line in enumerate(lines, 1):
            match = self.patterns["http_call"].search(line)
            if match:
                http_calls.append({
                    "line": i,
                    "method": match.group(1),
                    "snippet": line.strip(),
                })
        return http_calls
    
    def _extract_router_config(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """Extract router configuration."""
        router_config = []
        for i, line in enumerate(lines, 1):
            if self.patterns["router"].search(line):
                router_config.append({
                    "line": i,
                    "type": "forRoot" if "forRoot" in line else "forChild",
                    "snippet": line.strip(),
                })
        return router_config
    
    def _detect_edge_cases(self, content: str, lines: List[str]) -> List[Dict[str, Any]]:
        """
        Detect Angular edge cases and anti-patterns.
        
        Edge cases:
        - Memory leaks (unsubscribed observables)
        - Unsafe innerHTML bindings (XSS risk)
        - Missing HTTP error handling
        - Missing lifecycle cleanup (ngOnDestroy)
        - Any type usage (type safety)
        """
        edge_cases = []
        
        # Check for unsubscribed observables
        subscribe_lines = [i for i, line in enumerate(lines, 1) if ".subscribe(" in line]
        
        for sub_line in subscribe_lines:
            # Check if there's unsubscribe in next 20 lines or ngOnDestroy
            has_cleanup = False
            for j in range(sub_line, min(sub_line + 20, len(lines))):
                if self.patterns["unsubscribe"].search(lines[j]):
                    has_cleanup = True
                    break
            
            # Also check for ngOnDestroy in class
            has_ng_destroy = any(
                "ngOnDestroy" in line
                for line in lines[max(0, sub_line - 50):min(sub_line + 50, len(lines))]
            )
            
            if not has_cleanup and not has_ng_destroy:
                edge_cases.append({
                    "type": "memory_leak",
                    "severity": "high",
                    "line": sub_line,
                    "message": "Observable subscription without cleanup - memory leak",
                })
        
        # Check for unsafe innerHTML
        for i, line in enumerate(lines, 1):
            if self.patterns["inner_html"].search(line):
                edge_cases.append({
                    "type": "unsafe_html",
                    "severity": "critical",
                    "line": i,
                    "message": "Unsafe innerHTML binding - XSS vulnerability",
                })
        
        # Check for HTTP calls without error handling
        for i, line in enumerate(lines, 1):
            if self.patterns["http_call"].search(line):
                # Check if error handler exists in next 5 lines
                has_error_handler = any(
                    "catchError" in lines[j] or "error =>" in lines[j]
                    for j in range(i, min(i + 5, len(lines)))
                    if j < len(lines)
                )
                
                if not has_error_handler:
                    edge_cases.append({
                        "type": "missing_error_handler",
                        "severity": "medium",
                        "line": i,
                        "message": "HTTP call without error handling",
                    })
        
        # Check for 'any' type usage
        for i, line in enumerate(lines, 1):
            if self.patterns["any_type"].search(line):
                edge_cases.append({
                    "type": "any_type",
                    "severity": "low",
                    "line": i,
                    "message": "Using 'any' type - reduces type safety",
                })
        
        return edge_cases
    
    def _calculate_complexity(
        self,
        component_count: int,
        service_count: int,
        observable_count: int,
        http_count: int,
    ) -> int:
        """Calculate overall complexity score (0-100)."""
        complexity = (
            (component_count * 8) +
            (service_count * 6) +
            (observable_count * 3) +
            (http_count * 4)
        )
        
        return min(100, complexity)
