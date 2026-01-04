"""
Phase 5: Refactoring Plan

Generates prioritized refactoring tasks based on previous analysis phases.

Author: Asif Hussain
Created: January 3, 2026
"""

import logging
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


class RefactoringPlanPhase:
    """Phase 5: Generate prioritized refactoring plan."""
    
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute refactoring plan generation.
        
        Returns:
            Dictionary containing prioritized refactoring tasks
        """
        logger.info("Phase 5: Generating refactoring plan")
        
        results = {
            "refactoring_tasks": [],
            "priority_high": 0,
            "priority_medium": 0,
            "priority_low": 0,
            "estimated_effort_hours": 0
        }
        
        try:
            # Gather findings from previous phases
            phase_results = self.orchestrator.state.get("results", {})
            
            # Create tasks from quality issues
            if "QualityAssessment" in phase_results:
                quality_tasks = self._create_quality_tasks(phase_results["QualityAssessment"])
                results["refactoring_tasks"].extend(quality_tasks)
            
            # Create tasks from duplicates
            if "DuplicateDetection" in phase_results:
                duplicate_tasks = self._create_duplicate_tasks(phase_results["DuplicateDetection"])
                results["refactoring_tasks"].extend(duplicate_tasks)
            
            # Create tasks from performance issues
            if "PerformanceAnalysis" in phase_results:
                perf_tasks = self._create_performance_tasks(phase_results["PerformanceAnalysis"])
                results["refactoring_tasks"].extend(perf_tasks)
            
            # Create tasks from security issues
            if "SecurityAudit" in phase_results:
                security_tasks = self._create_security_tasks(phase_results["SecurityAudit"])
                results["refactoring_tasks"].extend(security_tasks)
            
            # Prioritize and estimate
            results["refactoring_tasks"] = self._prioritize_tasks(results["refactoring_tasks"])
            
            # Count by priority
            for task in results["refactoring_tasks"]:
                priority = task.get("priority", "low")
                if priority == "high":
                    results["priority_high"] += 1
                elif priority == "medium":
                    results["priority_medium"] += 1
                else:
                    results["priority_low"] += 1
                
                results["estimated_effort_hours"] += task.get("effort_hours", 1)
            
            logger.info(f"Refactoring plan generated: {len(results['refactoring_tasks'])} tasks, "
                       f"{results['estimated_effort_hours']} hours estimated")
            
        except Exception as e:
            logger.error(f"Refactoring plan generation failed: {e}", exc_info=True)
            results["error"] = str(e)
        
        return results
    
    def _create_quality_tasks(self, quality_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create refactoring tasks from quality issues."""
        tasks = []
        
        # Group issues by file and type
        issues_by_file = {}
        for issue in quality_results.get("issues", []):
            file_path = issue.get("file", "unknown")
            if file_path not in issues_by_file:
                issues_by_file[file_path] = []
            issues_by_file[file_path].append(issue)
        
        # Create tasks per file
        for file_path, issues in issues_by_file.items():
            high_severity = [i for i in issues if i.get("severity") == "error"]
            
            if high_severity:
                tasks.append({
                    "id": f"quality-{len(tasks)+1}",
                    "title": f"Fix quality issues in {Path(file_path).name}",
                    "type": "quality",
                    "file": file_path,
                    "description": f"Fix {len(high_severity)} high-severity quality issues",
                    "issues_count": len(issues),
                    "priority": "high" if len(high_severity) > 3 else "medium",
                    "effort_hours": min(8, len(issues) * 0.5),
                    "steps": [
                        "Review quality issues in file",
                        "Fix high-severity errors first",
                        "Address warnings and conventions",
                        "Run tests to validate fixes"
                    ]
                })
        
        return tasks
    
    def _create_duplicate_tasks(self, duplicate_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create refactoring tasks from duplicate code."""
        tasks = []
        
        for idx, suggestion in enumerate(duplicate_results.get("consolidation_suggestions", [])):
            tasks.append({
                "id": f"duplicate-{idx+1}",
                "title": f"Consolidate duplicate {suggestion['block_type']}",
                "type": "duplicate",
                "description": f"Consolidate {suggestion['duplicate_count']} duplicate instances",
                "duplicate_count": suggestion["duplicate_count"],
                "priority": "medium",
                "effort_hours": suggestion["duplicate_count"] * 1,
                "steps": suggestion.get("refactoring_steps", [])
            })
        
        return tasks
    
    def _create_performance_tasks(self, perf_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create refactoring tasks from performance issues."""
        tasks = []
        
        # Group hotspots by type
        hotspots_by_type = {}
        for hotspot in perf_results.get("hotspots", []):
            htype = hotspot.get("type", "unknown")
            if htype not in hotspots_by_type:
                hotspots_by_type[htype] = []
            hotspots_by_type[htype].append(hotspot)
        
        for htype, hotspots in hotspots_by_type.items():
            if hotspots:
                severity = hotspots[0].get("severity", "low")
                tasks.append({
                    "id": f"performance-{htype}",
                    "title": f"Optimize {htype.replace('_', ' ')}",
                    "type": "performance",
                    "description": f"Fix {len(hotspots)} performance hotspots",
                    "hotspot_count": len(hotspots),
                    "priority": "high" if severity == "high" else "medium",
                    "effort_hours": len(hotspots) * 2,
                    "files": list(set(h["file"] for h in hotspots)),
                    "steps": [
                        "Profile affected code sections",
                        "Apply recommended optimizations",
                        "Measure performance improvement",
                        "Add performance tests"
                    ]
                })
        
        return tasks
    
    def _create_security_tasks(self, security_results: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create refactoring tasks from security issues."""
        tasks = []
        
        for item in security_results.get("remediation_plan", []):
            tasks.append({
                "id": f"security-{item['type']}",
                "title": f"Fix {item['type'].replace('_', ' ')} vulnerabilities",
                "type": "security",
                "description": f"Address {item['count']} security issues",
                "vulnerability_count": item["count"],
                "priority": item["priority"],
                "effort_hours": item["count"] * 1.5,
                "files": item.get("files", []),
                "remediation": item.get("remediation", ""),
                "steps": [
                    "Review all affected files",
                    "Apply security fixes",
                    "Add input validation",
                    "Test security improvements"
                ]
            })
        
        return tasks
    
    def _prioritize_tasks(self, tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Prioritize tasks by impact and effort."""
        priority_order = {"high": 3, "medium": 2, "low": 1}
        
        # Sort by priority (high first), then by effort (low first)
        sorted_tasks = sorted(
            tasks,
            key=lambda t: (
                -priority_order.get(t.get("priority", "low"), 1),
                t.get("effort_hours", 999)
            )
        )
        
        return sorted_tasks


from pathlib import Path
