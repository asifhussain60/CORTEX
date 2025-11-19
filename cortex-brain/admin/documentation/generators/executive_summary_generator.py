"""
Executive Summary Generator

Generates high-level executive summary documentation for CORTEX project.
Extracts key metrics, architecture overview, capabilities, and status from codebase.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
import yaml
import logging

from .base_generator import (
    BaseDocumentationGenerator,
    GenerationConfig,
    GenerationResult,
    GeneratorType
)

logger = logging.getLogger(__name__)


class ExecutiveSummaryGenerator(BaseDocumentationGenerator):
    """
    Generate executive summary documentation.
    
    Collects high-level information about CORTEX:
    - Project overview and mission
    - Key capabilities and features
    - Architecture summary (4-tier memory + dual-hemisphere agents)
    - Current implementation status
    - Test coverage and quality metrics
    - Recent milestones and achievements
    """
    
    def __init__(self, config: GenerationConfig, workspace_root: Optional[Path] = None):
        super().__init__(config, workspace_root)
        self.docs_path = self.workspace_root / "docs"
        self.brain_path = self.workspace_root / "cortex-brain"
        
    def get_component_name(self) -> str:
        return "Executive Summary"
    
    def collect_data(self) -> Dict[str, Any]:
        """
        Collect data for executive summary.
        
        Returns:
            Dictionary containing:
            - project_info: Name, version, description
            - architecture: High-level architecture overview
            - capabilities: Key capabilities list
            - status: Implementation and test status
            - metrics: Quality metrics (test coverage, pass rate, etc.)
            - milestones: Recent achievements
        """
        data = {
            "generated_at": datetime.now().isoformat(),
            "project_info": self._collect_project_info(),
            "architecture": self._collect_architecture_summary(),
            "capabilities": self._collect_capabilities(),
            "status": self._collect_status(),
            "metrics": self._collect_metrics(),
            "milestones": self._collect_milestones()
        }
        
        return data
    
    def _collect_project_info(self) -> Dict[str, Any]:
        """Collect basic project information"""
        # Load from cortex.config.json or fallback to defaults
        config_file = self.workspace_root / "cortex.config.json"
        if config_file.exists():
            try:
                import json
                with open(config_file) as f:
                    config = json.load(f)
                    return {
                        "name": config.get("name", "CORTEX"),
                        "version": config.get("version", "3.0"),
                        "description": config.get("description", "Memory and context system for GitHub Copilot"),
                        "author": "Asif Hussain",
                        "copyright": "© 2024-2025 Asif Hussain. All rights reserved."
                    }
            except Exception as e:
                self.record_warning(f"Failed to load cortex.config.json: {e}")
        
        # Fallback defaults
        return {
            "name": "CORTEX",
            "version": "3.0",
            "description": "Memory and context system for GitHub Copilot",
            "author": "Asif Hussain",
            "copyright": "© 2024-2025 Asif Hussain. All rights reserved."
        }
    
    def _collect_architecture_summary(self) -> Dict[str, Any]:
        """Collect high-level architecture information"""
        return {
            "model": "Dual-Hemisphere Brain Architecture",
            "tiers": [
                {
                    "name": "Tier 0: Instinct",
                    "purpose": "Immutable governance rules (22 SKULL rules)",
                    "storage": "cortex-brain/brain-protection-rules.yaml"
                },
                {
                    "name": "Tier 1: Working Memory",
                    "purpose": "Short-term conversation memory (last 20 conversations)",
                    "storage": "cortex-brain/tier1/conversations.db (SQLite)"
                },
                {
                    "name": "Tier 2: Knowledge Graph",
                    "purpose": "Long-term pattern learning and workflow templates",
                    "storage": "cortex-brain/tier2/knowledge-graph.db (SQLite)"
                },
                {
                    "name": "Tier 3: Context Intelligence",
                    "purpose": "Git analysis, file stability, session analytics",
                    "storage": "cortex-brain/tier3/context-intelligence.db (SQLite)"
                }
            ],
            "hemispheres": {
                "right_brain": {
                    "role": "Strategic Planning",
                    "agents": [
                        "Intent Router",
                        "Work Planner",
                        "Screenshot Analyzer",
                        "Change Governor",
                        "Brain Protector"
                    ]
                },
                "left_brain": {
                    "role": "Tactical Execution",
                    "agents": [
                        "Code Executor",
                        "Test Generator",
                        "Error Corrector",
                        "Health Validator",
                        "Commit Handler"
                    ]
                }
            },
            "coordination": "Corpus Callosum (message queue system)"
        }
    
    def _collect_capabilities(self) -> Dict[str, List[str]]:
        """Collect key capabilities from capabilities.yaml if available"""
        capabilities_file = self.brain_path / "capabilities.yaml"
        
        if capabilities_file.exists():
            try:
                with open(capabilities_file) as f:
                    caps_data = yaml.safe_load(f)
                    if caps_data and isinstance(caps_data, dict):
                        return caps_data
            except Exception as e:
                self.record_warning(f"Failed to load capabilities.yaml: {e}")
        
        # Fallback to core capabilities
        return {
            "memory_management": [
                "Last 20 conversation history (FIFO queue)",
                "Entity tracking (files, classes, functions)",
                "Context continuity across sessions"
            ],
            "pattern_learning": [
                "Intent pattern recognition",
                "File relationship tracking",
                "Workflow template storage"
            ],
            "intelligence": [
                "Git commit analysis (last 30 days)",
                "File stability classification",
                "Session productivity analytics"
            ],
            "operations": [
                "Interactive feature planning",
                "Setup and configuration",
                "Documentation generation",
                "Code optimization",
                "Test execution"
            ]
        }
    
    def _collect_status(self) -> Dict[str, Any]:
        """Collect current implementation status from live brain sources"""
        # Load from module-definitions.yaml (SINGLE SOURCE OF TRUTH)
        module_defs_path = self.brain_path / "module-definitions.yaml"
        operations_path = self.workspace_root / "cortex-operations.yaml"
        
        status = {
            "modules": {"total": 0, "implemented": 0, "pending": 0, "percentage": 0.0},
            "operations": {"total": 0, "ready": 0, "in_progress": 0, "percentage": 0.0},
            "phase": "Unknown"
        }
        
        # Load module definitions
        if module_defs_path.exists():
            try:
                with open(module_defs_path) as f:
                    module_data = yaml.safe_load(f)
                    
                    metadata = module_data.get("metadata", {})
                    status["modules"]["total"] = metadata.get("total_modules", 0)
                    status["modules"]["implemented"] = metadata.get("modules_implemented", 0)
                    status["modules"]["pending"] = metadata.get("modules_pending", 0)
                    status["modules"]["percentage"] = metadata.get("completion_percentage", 0.0)
                    
            except Exception as e:
                self.record_warning(f"Failed to load module-definitions.yaml: {e}")
        
        # Load operations
        if operations_path.exists():
            try:
                with open(operations_path) as f:
                    ops_data = yaml.safe_load(f)
                    
                    operations = ops_data.get("operations", {})
                    status["operations"]["total"] = len(operations)
                    
                    ready_count = 0
                    in_progress_count = 0
                    
                    for op_id, op_data in operations.items():
                        impl_status = op_data.get("implementation_status", {})
                        op_status = impl_status.get("status", "pending")
                        
                        if op_status == "ready":
                            ready_count += 1
                        elif op_status == "in_progress":
                            in_progress_count += 1
                    
                    status["operations"]["ready"] = ready_count
                    status["operations"]["in_progress"] = in_progress_count
                    status["operations"]["percentage"] = round(
                        ready_count / len(operations) * 100, 1
                    ) if operations else 0.0
                    
            except Exception as e:
                self.record_warning(f"Failed to load cortex-operations.yaml: {e}")
        
        # Determine current phase from latest completion reports
        reports_path = self.brain_path / "documents" / "reports"
        if reports_path.exists():
            try:
                completion_reports = sorted(
                    reports_path.glob("*COMPLETION*.md"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True
                )
                
                if completion_reports:
                    # Extract phase from most recent report
                    latest_report = completion_reports[0].name
                    if "PHASE-0" in latest_report:
                        status["phase"] = "Phase 0 Complete (Test Stabilization)"
                    elif "PHASE-1" in latest_report:
                        status["phase"] = "Phase 1 Complete (Dual-Channel Memory)"
                    elif "PHASE-2" in latest_report:
                        status["phase"] = "Phase 2 Complete"
                    elif "PHASE-3" in latest_report:
                        status["phase"] = "Phase 3 Complete"
                    elif "TRACK-A" in latest_report:
                        status["phase"] = "Track A Complete"
                    else:
                        status["phase"] = "Development in Progress"
            except Exception as e:
                self.record_warning(f"Failed to determine phase from reports: {e}")
        
        return status
    
    def _collect_metrics(self) -> Dict[str, Any]:
        """Collect quality metrics from live test results and brain data"""
        metrics = {
            "test_coverage": "Unknown",
            "test_pass_rate": "Unknown",
            "total_tests": 0,
            "passing_tests": 0,
            "skipped_tests": 0,
            "failed_tests": 0,
            "code_quality": "Unknown"
        }
        
        # Try to load from pytest cache
        pytest_cache = self.workspace_root / ".pytest_cache"
        if pytest_cache.exists():
            try:
                # Read from lastfailed or .pytest_cache/v/cache/stepwise
                cache_dir = pytest_cache / "v" / "cache"
                if cache_dir.exists():
                    # Look for nodeids or lastfailed
                    lastfailed_path = cache_dir / "lastfailed"
                    if lastfailed_path.exists():
                        import json
                        with open(lastfailed_path) as f:
                            lastfailed = json.load(f)
                            metrics["failed_tests"] = len(lastfailed)
            except Exception as e:
                self.record_warning(f"Failed to load pytest cache: {e}")
        
        # Try to load actual metrics from health reports (LIVE DATA)
        health_reports = self.brain_path / "health-reports"
        if health_reports.exists():
            try:
                # Find most recent health report
                reports = list(health_reports.glob("health-*.json"))
                if reports:
                    reports.sort(key=lambda p: p.stat().st_mtime, reverse=True)
                    latest = reports[0]
                    
                    import json
                    with open(latest) as f:
                        health_data = json.load(f)
                        
                        # Extract metrics if available
                        if "test_metrics" in health_data:
                            tm = health_data["test_metrics"]
                            metrics.update({
                                "total_tests": tm.get("total", 0),
                                "passing_tests": tm.get("passing", 0),
                                "skipped_tests": tm.get("skipped", 0),
                                "failed_tests": tm.get("failed", 0),
                                "test_coverage": tm.get("coverage", "Unknown"),
                                "test_pass_rate": tm.get("pass_rate", "Unknown")
                            })
                        
                        # Code quality assessment
                        if "code_quality" in health_data:
                            metrics["code_quality"] = health_data["code_quality"]
                        elif metrics["total_tests"] > 0:
                            # Calculate based on pass rate
                            pass_rate = (metrics["passing_tests"] / metrics["total_tests"]) * 100
                            if pass_rate >= 95:
                                metrics["code_quality"] = "Production Ready"
                            elif pass_rate >= 90:
                                metrics["code_quality"] = "Stable"
                            elif pass_rate >= 80:
                                metrics["code_quality"] = "Beta"
                            else:
                                metrics["code_quality"] = "Alpha"
            except Exception as e:
                self.record_warning(f"Failed to load health reports: {e}")
        
        # If no health reports, try to run pytest collect to get count
        if metrics["total_tests"] == 0:
            try:
                import subprocess
                result = subprocess.run(
                    ["pytest", "--collect-only", "-q"],
                    cwd=self.workspace_root,
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                
                # Parse output for test count
                for line in result.stdout.split('\n'):
                    if " test" in line and "selected" in line:
                        # Extract number from "X tests selected"
                        parts = line.split()
                        if parts and parts[0].isdigit():
                            metrics["total_tests"] = int(parts[0])
                        break
            except Exception as e:
                self.record_warning(f"Failed to collect test count: {e}")
        
        # Calculate pass rate if we have data
        if metrics["total_tests"] > 0:
            non_skipped = metrics["total_tests"] - metrics["skipped_tests"]
            if non_skipped > 0:
                pass_rate = (metrics["passing_tests"] / non_skipped) * 100
                metrics["test_pass_rate"] = f"{pass_rate:.1f}%"
        
        return metrics
    
    def _collect_milestones(self) -> List[Dict[str, str]]:
        """Collect recent milestones from actual completion reports (LIVE DATA)"""
        milestones = []
        
        # Scan completion reports in brain
        reports_path = self.brain_path / "documents" / "reports"
        if reports_path.exists():
            try:
                completion_reports = sorted(
                    reports_path.glob("*COMPLETION*.md"),
                    key=lambda p: p.stat().st_mtime,
                    reverse=True
                )
                
                for report_path in completion_reports[:10]:  # Check last 10 reports
                    try:
                        content = report_path.read_text(encoding='utf-8')
                        
                        # Extract date from filename or file mtime
                        date = datetime.fromtimestamp(report_path.stat().st_mtime).strftime("%Y-%m-%d")
                        
                        # Extract title from report name
                        title = report_path.stem.replace("-", " ").replace("_", " ").title()
                        
                        # Try to extract description from first paragraph
                        lines = content.split('\n')
                        description = ""
                        for line in lines[1:20]:  # Check first 20 lines
                            line = line.strip()
                            if line and not line.startswith('#') and not line.startswith('*'):
                                description = line
                                break
                        
                        if not description:
                            # Fallback: extract from title or use generic
                            if "PHASE-0" in report_path.name:
                                description = "Test stabilization and pragmatic MVP approach implemented"
                            elif "PHASE-1" in report_path.name:
                                description = "Dual-channel memory architecture with conversation management"
                            elif "PHASE-2" in report_path.name:
                                description = "Documentation reorganization and EPM enhancement"
                            elif "PHASE-3" in report_path.name:
                                description = "Advanced features and optimization"
                            else:
                                description = "Milestone completed successfully"
                        
                        milestones.append({
                            "date": date,
                            "title": title,
                            "description": description[:200]  # Limit description length
                        })
                        
                        if len(milestones) >= 5:
                            break
                            
                    except Exception as e:
                        self.record_warning(f"Failed to parse report {report_path.name}: {e}")
                        continue
                        
            except Exception as e:
                self.record_warning(f"Failed to scan completion reports: {e}")
        
        # If no milestones found from reports, create from known achievements
        if not milestones:
            self.record_warning("No completion reports found - using generic milestones")
            milestones = [
                {
                    "date": datetime.now().strftime("%Y-%m-%d"),
                    "title": "CORTEX 3.0 Development",
                    "description": "Ongoing development of memory architecture and documentation system"
                }
            ]
        
        return milestones
    
    def generate(self) -> GenerationResult:
        """
        Generate executive summary markdown document.
        
        Creates EXECUTIVE-SUMMARY.md in docs/ folder with high-level overview.
        """
        self.start_time = datetime.now()
        
        # Collect data
        data = self.collect_data()
        
        # Generate markdown
        summary_file = self.docs_path / "EXECUTIVE-SUMMARY.md"
        
        try:
            content = self._generate_markdown(data)
            
            with open(summary_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.record_file_generated(summary_file)
            
            # Save metadata
            metadata = {
                "generated_at": data["generated_at"],
                "project_version": data["project_info"]["version"],
                "modules_implemented": data["status"]["modules"]["percentage"],
                "operations_ready": data["status"]["operations"]["percentage"]
            }
            self.save_metadata("executive-summary-metadata.json", metadata)
            
            return self._create_success_result(metadata)
            
        except Exception as e:
            self.record_error(f"Failed to generate executive summary: {e}")
            return self._create_failed_result(str(e))
    
    def _generate_markdown(self, data: Dict[str, Any]) -> str:
        """Generate markdown content from collected data"""
        project = data["project_info"]
        arch = data["architecture"]
        caps = data["capabilities"]
        status = data["status"]
        metrics = data["metrics"]
        milestones = data["milestones"]
        
        md = f"""# CORTEX Executive Summary

**Generated:** {data["generated_at"][:10]}  
**Version:** {project["version"]}  
**Status:** {status["phase"]}

---

## 🎯 Mission

{project["description"]}

CORTEX transforms GitHub Copilot from a brilliant amnesiac into an experienced team member with memory, learning, and contextual intelligence.

---

## 🏗️ Architecture

**Model:** {arch["model"]}

### Memory Tiers

"""
        
        for tier in arch["tiers"]:
            md += f"**{tier['name']}**  \n"
            md += f"- Purpose: {tier['purpose']}  \n"
            md += f"- Storage: `{tier['storage']}`  \n\n"
        
        md += f"""### Agent System

**Right Brain (Strategic):** {', '.join(arch['hemispheres']['right_brain']['agents'])}  
**Left Brain (Tactical):** {', '.join(arch['hemispheres']['left_brain']['agents'])}  
**Coordination:** {arch['coordination']}

---

## 🚀 Key Capabilities

"""
        
        for category, features in caps.items():
            md += f"### {category.replace('_', ' ').title()}\n\n"
            for feature in features:
                md += f"- {feature}\n"
            md += "\n"
        
        md += f"""---

## 📊 Implementation Status

### Modules
- **Total:** {status['modules']['total']}
- **Implemented:** {status['modules']['implemented']} ({status['modules']['percentage']}%)

### Operations
- **Total:** {status['operations']['total']}
- **Ready:** {status['operations']['ready']} ({status['operations']['percentage']}%)

### Quality Metrics
- **Test Coverage:** {metrics['test_coverage']}
- **Test Pass Rate:** {metrics['test_pass_rate']}
- **Total Tests:** {metrics['total_tests']} ({metrics['passing_tests']} passing, {metrics['skipped_tests']} skipped)
- **Code Quality:** {metrics['code_quality']}

---

## 🏆 Recent Milestones

"""
        
        for milestone in milestones[:5]:  # Show last 5
            md += f"**{milestone['date']}** - {milestone['title']}  \n"
            md += f"{milestone['description']}  \n\n"
        
        md += f"""---

## 📚 Documentation

- **Setup Guide:** `prompts/shared/setup-guide.md`
- **Story:** `prompts/shared/story.md` (The Intern with Amnesia)
- **Technical Reference:** `prompts/shared/technical-reference.md`
- **Agents Guide:** `prompts/shared/agents-guide.md`
- **Operations Reference:** `prompts/shared/operations-reference.md`

---

**{project['copyright']}**  
**License:** Proprietary - See LICENSE file
"""
        
        return md
    
    def validate(self) -> bool:
        """
        Validate generated executive summary.
        
        Checks:
        - EXECUTIVE-SUMMARY.md exists
        - File is not empty
        - Contains required sections
        """
        summary_file = self.docs_path / "EXECUTIVE-SUMMARY.md"
        
        if not summary_file.exists():
            self.record_error("EXECUTIVE-SUMMARY.md not found")
            return False
        
        try:
            content = summary_file.read_text(encoding='utf-8')
            
            if len(content) < 500:
                self.record_error("Executive summary too short (< 500 chars)")
                return False
            
            required_sections = [
                "# CORTEX Executive Summary",
                "## 🎯 Mission",
                "## 🏗️ Architecture",
                "## 🚀 Key Capabilities",
                "## 📊 Implementation Status",
                "## 🏆 Recent Milestones"
            ]
            
            for section in required_sections:
                if section not in content:
                    self.record_error(f"Missing section: {section}")
                    return False
            
            logger.info("Executive summary validation passed")
            return True
            
        except Exception as e:
            self.record_error(f"Validation error: {e}")
            return False
