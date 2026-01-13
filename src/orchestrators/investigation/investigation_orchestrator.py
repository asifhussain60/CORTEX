"""
Investigation Orchestrator v2 - Root Cause Analysis.

Autonomous orchestrator for investigating issues:
- Log file analysis
- Error pattern detection
- Dependency graph analysis
- Timeline reconstruction
- Solution recommendations

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
import re
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime
from enum import Enum
from collections import defaultdict

from src.orchestrators.base.base_orchestrator_v4 import (
    BaseOrchestratorV4,
    PhaseStatus,
    PhaseResult
)
from src.orchestrators.base.base_orchestrator import (
from src.response_templates.layered_template_renderer import LayeredTemplateRenderer
    OrchestratorResult,
    OrchestratorStatus
)


class InvestigationPhase(Enum):
    """Investigation phases."""
    LOG_ANALYSIS = "log_analysis"
    ERROR_DETECTION = "error_detection"
    DEPENDENCY_ANALYSIS = "dependency_analysis"
    TIMELINE_RECONSTRUCTION = "timeline_reconstruction"
    RECOMMENDATION = "recommendation"


class InvestigationResult:
    """Container for investigation results."""
    
    def __init__(self, phase: InvestigationPhase, findings: Dict[str, Any]):
        self.phase = phase
        self.findings = findings
        self.timestamp = datetime.now().isoformat()


        self.template_renderer = LayeredTemplateRenderer()
class InvestigationOrchestratorV2(BaseOrchestratorV4):
    """
    Investigation Orchestrator v2 - Root cause analysis.
    
    Features:
    - Multi-source log aggregation
    - Pattern-based error detection
    - Dependency impact analysis
    - Event timeline reconstruction
    - AI-powered solution recommendations
    - Investigation report generation
    
    Usage:
        orchestrator = InvestigationOrchestratorV2(workspace_root="/path/to/workspace")
        result = orchestrator.execute(
            context={"issue": "Connection failures"}
        )
    """
    
    def __init__(self, workspace_root: str, config_path: Optional[str] = None):
        """
        Initialize Investigation Orchestrator v2.
        
        Args:
            workspace_root: Path to workspace root
            config_path: Optional path to configuration file
        """
        super().__init__(config_path=config_path)
        self.workspace_root = workspace_root
        self.logger = logging.getLogger("cortex.orchestrators.investigation_v2")
        self.investigation_results: List[InvestigationResult] = []
    
    def execute(self, context: Dict[str, Any]) -> OrchestratorResult:
        """
        Execute investigation workflow.
        
        Args:
            context: Investigation context
            
        Returns:
            OrchestratorResult with findings
        """
        self.logger.info("Starting investigation")
        
        try:
            # Execute investigation phases
            log_analysis = self._analyze_logs()
            error_patterns = self._detect_error_patterns()
            dependencies = self._analyze_dependencies()
            timeline = self._reconstruct_timeline()
            
            # Generate recommendations
            analysis_data = {
                "errors": log_analysis.get("errors", []),
                "patterns": error_patterns.get("patterns", []),
                "dependencies": dependencies.get("dependencies", [])
            }
            recommendations = self._generate_recommendations(analysis_data)
            
            return OrchestratorResult(
                success=True,
                status=OrchestratorStatus.SUCCESS,
                message="Investigation completed successfully",
                data={
                    "investigation_complete": True,
                    "log_analysis": log_analysis,
                    "error_patterns": error_patterns,
                    "dependencies": dependencies,
                    "timeline": timeline,
                    "recommendations": recommendations
                }
            )
        
        except Exception as e:
            self.logger.error(f"Investigation failed: {e}")
            return OrchestratorResult(
                success=False,
                status=OrchestratorStatus.FAILURE,
                message=f"Investigation failed: {str(e)}",
                data={"error": str(e)}
            )
    
    def _analyze_logs(self) -> Dict[str, Any]:
        """Analyze log files for errors and warnings."""
        self.logger.info("Analyzing logs")
        
        errors = []
        warnings = []
        
        # Find log files
        workspace_path = Path(self.workspace_root)
        log_dirs = [
            workspace_path / "logs",
            workspace_path / "cortex-brain" / "audit-logs"
        ]
        
        for log_dir in log_dirs:
            if not log_dir.exists():
                continue
            
            for log_file in log_dir.rglob("*.log"):
                try:
                    content = log_file.read_text()
                    
                    # Extract errors
                    error_lines = [
                        line for line in content.split('\n')
                        if 'ERROR' in line.upper()
                    ]
                    errors.extend(error_lines[:10])  # Limit to 10 per file
                    
                    # Extract warnings
                    warning_lines = [
                        line for line in content.split('\n')
                        if 'WARN' in line.upper()
                    ]
                    warnings.extend(warning_lines[:10])
                
                except Exception as e:
                    self.logger.warning(f"Could not read {log_file}: {e}")
        
        return {
            "errors": errors,
            "warnings": warnings,
            "error_count": len(errors),
            "warning_count": len(warnings)
        }
    
    def _detect_error_patterns(self) -> Dict[str, Any]:
        """Detect common error patterns."""
        self.logger.info("Detecting error patterns")
        
        patterns = []
        
        # Common error patterns
        pattern_signatures = {
            "connection_timeout": r"(timeout|timed out|connection.*fail)",
            "authentication_failure": r"(auth.*fail|unauthorized|403|401)",
            "resource_not_found": r"(not found|404|missing.*file)",
            "permission_denied": r"(permission denied|access denied|forbidden)",
            "out_of_memory": r"(out of memory|oom|memory.*exceeded)",
        }
        
        # Check workspace for patterns (simplified)
        detected_patterns = defaultdict(int)
        
        workspace_path = Path(self.workspace_root)
        log_dir = workspace_path / "logs"
        
        if log_dir.exists():
            for log_file in log_dir.rglob("*.log"):
                try:
                    content = log_file.read_text().lower()
                    
                    for pattern_name, pattern_regex in pattern_signatures.items():
                        if re.search(pattern_regex, content, re.IGNORECASE):
                            detected_patterns[pattern_name] += 1
                
                except Exception:
                    pass
        
        patterns = [
            {"pattern": name, "occurrences": count}
            for name, count in detected_patterns.items()
        ]
        
        return {
            "patterns": patterns,
            "detected": patterns,
            "count": len(patterns)
        }
    
    def _analyze_dependencies(self) -> Dict[str, Any]:
        """Analyze dependency relationships."""
        self.logger.info("Analyzing dependencies")
        
        dependencies = []
        
        # Check for requirements.txt
        workspace_path = Path(self.workspace_root)
        requirements_file = workspace_path / "requirements.txt"
        
        if requirements_file.exists():
            try:
                content = requirements_file.read_text()
                deps = [
                    line.split('==')[0].strip()
                    for line in content.split('\n')
                    if line.strip() and not line.startswith('#')
                ]
                dependencies = deps[:20]  # Limit to 20
            except Exception as e:
                self.logger.warning(f"Could not read requirements: {e}")
        
        return {
            "dependencies": dependencies,
            "graph": {"nodes": dependencies, "edges": []},
            "count": len(dependencies)
        }
    
    def _reconstruct_timeline(self) -> Dict[str, Any]:
        """Reconstruct event timeline from logs."""
        self.logger.info("Reconstructing timeline")
        
        events = []
        
        # Parse log timestamps (simplified)
        workspace_path = Path(self.workspace_root)
        log_dir = workspace_path / "logs"
        
        if log_dir.exists():
            for log_file in log_dir.rglob("*.log"):
                try:
                    content = log_file.read_text()
                    
                    # Extract timestamped lines (simplified regex)
                    timestamp_pattern = r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})'
                    
                    for line in content.split('\n')[:50]:  # Limit to 50 lines
                        match = re.search(timestamp_pattern, line)
                        if match:
                            events.append({
                                "timestamp": match.group(1),
                                "message": line[match.end():].strip()[:100]
                            })
                
                except Exception:
                    pass
        
        # Sort by timestamp
        events.sort(key=lambda x: x.get("timestamp", ""))
        
        return {
            "timeline": events,
            "events": events,
            "count": len(events)
        }
    
    def _generate_recommendations(self, analysis_data: Dict[str, Any]) -> List[str]:
        """Generate solution recommendations."""
        self.logger.info("Generating recommendations")
        
        recommendations = []
        
        errors = analysis_data.get("errors", [])
        patterns = analysis_data.get("patterns", [])
        
        # Pattern-based recommendations
        pattern_names = [p.get("pattern") if isinstance(p, dict) else p for p in patterns]
        
        if "connection_timeout" in pattern_names or any("timeout" in str(e).lower() for e in errors):
            recommendations.append("Increase connection timeout values in configuration")
            recommendations.append("Check network connectivity and firewall rules")
        
        if "authentication_failure" in pattern_names:
            recommendations.append("Verify authentication credentials are correct")
            recommendations.append("Check token expiration and refresh logic")
        
        if "resource_not_found" in pattern_names:
            recommendations.append("Verify file paths and resource locations")
            recommendations.append("Check deployment configuration")
        
        if "out_of_memory" in pattern_names:
            recommendations.append("Increase allocated memory limits")
            recommendations.append("Review and optimize memory-intensive operations")
        
        # Default recommendations
        if not recommendations:
            recommendations = [
                "Review recent code changes for potential issues",
                "Check application logs for detailed error messages",
                "Verify all dependencies are up to date",
                "Run diagnostic health checks"
            ]
        
        return recommendations
