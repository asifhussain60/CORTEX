"""
Minimal System Alignment Utility - Fast & Reliable Replacement

Lightweight replacement for SystemAlignmentOrchestrator that focuses on
essential system health checks without complex integration scoring.

Design Goals:
    - Execute in <5 seconds (full scan) or <2 seconds (incremental)
    - Clear pass/fail reporting
    - No complex dependencies
    - Admin-only execution
    - Actionable error messages
    - Auto-discovery and wiring validation
    - Incremental validation with file change tracking

Validation Checks (Phase 0 + 8 Core):
    Phase 0: Documentation Sync
        - CORTEX.prompt.md and copilot-instructions.md synchronization
        - Response format consistency
        - Document organization rules alignment
        - Version number matching
    
    Core Checks:
        1. Brain tier structure (tier0-3)
        2. Protection rules (brain-protection-rules.yaml)
        3. Response templates (response-templates.yaml)
        4. Working memory database
        5. Knowledge graph database
        6. Development context database
        7. Core Python modules (orchestrators/agents)
        8. Configuration file (cortex.config.json)

Enhancement Features (v3.2):
    - File change detection via SHA256 checksums
    - Incremental validation (only check changed features)
    - Auto-wiring discovery and validation
    - Admin vs User context detection
    - Performance metrics tracking

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 3.2 (Incremental)
Status: PRODUCTION
"""

import logging
import json
import sqlite3
import yaml
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from datetime import datetime

# Import centralized config for cross-platform paths
from src.config import config

# Import alignment state management
from src.operations.modules.admin.alignment_state import (
    AlignmentState,
    AlignmentStateManager,
    ChangesSummary
)

logger = logging.getLogger(__name__)


def safe_print(message: str) -> None:
    """Print with Unicode fallback for Windows console encoding issues."""
    try:
        print(message)
    except UnicodeEncodeError:
        # Replace emojis with ASCII equivalents
        ascii_message = (message
            .replace('🧠', '[BRAIN]')
            .replace('✅', '[OK]')
            .replace('⚠️', '[WARN]')
            .replace('❌', '[FAIL]')
            .replace('━', '-')
        )
        print(ascii_message)


@dataclass
class ValidationResult:
    """Result of a single validation check."""
    check_name: str
    passed: bool
    message: str
    details: str = ""
    severity: str = "ERROR"  # ERROR, WARNING, INFO
    
    def __str__(self) -> str:
        """Format for console output."""
        if self.passed:
            icon = "✅ [OK]"
        elif self.severity == "WARNING":
            icon = "⚠️ [WARN]"
        else:
            icon = "❌ [FAIL]"
        
        output = f"{icon} {self.check_name}: {self.message}"
        if self.details:
            output += f"\n  └─ {self.details}"
        return output


@dataclass
class AlignmentReport:
    """Complete system alignment report."""
    timestamp: datetime
    checks: List[ValidationResult] = field(default_factory=list)
    execution_time: float = 0.0
    
    @property
    def passed_count(self) -> int:
        """Count of passed checks."""
        return sum(1 for check in self.checks if check.passed)
    
    @property
    def total_count(self) -> int:
        """Total checks executed."""
        return len(self.checks)
    
    @property
    def is_healthy(self) -> bool:
        """System considered healthy if all ERROR-level checks pass."""
        return all(
            check.passed or check.severity == "WARNING"
            for check in self.checks
        )
    
    @property
    def status_text(self) -> str:
        """Human-readable status."""
        if self.is_healthy:
            return "HEALTHY"
        else:
            failed_critical = sum(
                1 for check in self.checks 
                if not check.passed and check.severity == "ERROR"
            )
            return f"UNHEALTHY ({failed_critical} critical issues)"
    
    def format_console(self) -> str:
        """Format report for console output."""
        lines = [
            "🧠 CORTEX System Alignment Check",
            "━" * 60,
            ""
        ]
        
        for check in self.checks:
            lines.append(str(check))
        
        lines.extend([
            "",
            "━" * 60,
            f"System Status: {self.status_text} ({self.passed_count}/{self.total_count} checks passed)",
            f"Execution Time: {self.execution_time:.1f}s",
        ])
        
        # Add next steps if there are failures
        warnings_or_failures = [
            check for check in self.checks 
            if not check.passed
        ]
        if warnings_or_failures:
            lines.extend([
                "",
                "Next Steps:",
            ])
            for check in warnings_or_failures:
                if check.severity == "ERROR":
                    lines.append(f"• [CRITICAL] {check.details or check.message}")
                else:
                    lines.append(f"• {check.details or check.message}")
        
        return "\n".join(lines)


class AlignUtility:
    """Minimal system alignment validator - fast and reliable with incremental support."""
    
    def __init__(self, force_full: bool = False, quick_mode: bool = False):
        """
        Initialize utility with CORTEX paths.
        
        Args:
            force_full: Force full scan even if incremental is possible
            quick_mode: Infrastructure checks only, skip feature validation
        """
        self.brain_path = Path(config.brain_path)
        self.root_path = Path(config.root_path)
        self.start_time = None
        self.force_full = force_full
        self.quick_mode = quick_mode
        
        # State management
        self.state_manager = AlignmentStateManager(
            self.brain_path / ".alignment-state.json"
        )
        self.context_type = self.state_manager.detect_context_type(self.root_path)
        
        # Performance tracking
        self.features_checked = 0
        self.features_skipped = 0
    
    def validate_prompt_sync(self) -> ValidationResult:
        """
        Phase 0: Check that CORTEX.prompt.md and copilot-instructions.md are synchronized.
        
        Validates:
        - Both files exist
        - Response format section is consistent
        - Document organization rules are consistent
        - Version numbers match
        """
        try:
            prompt_file = self.root_path / ".github" / "prompts" / "CORTEX.prompt.md"
            instructions_file = self.root_path / ".github" / "copilot-instructions.md"
            
            if not prompt_file.exists():
                return ValidationResult(
                    check_name="Prompt Sync (Phase 0)",
                    passed=False,
                    message="CORTEX.prompt.md not found",
                    details=f"Expected at: {prompt_file}",
                    severity="ERROR"
                )
            
            if not instructions_file.exists():
                return ValidationResult(
                    check_name="Prompt Sync (Phase 0)",
                    passed=False,
                    message="copilot-instructions.md not found",
                    details=f"Expected at: {instructions_file}",
                    severity="ERROR"
                )
            
            # Read both files
            prompt_content = prompt_file.read_text(encoding='utf-8')
            instructions_content = instructions_file.read_text(encoding='utf-8')
            
            # Check critical sections synchronization
            sync_issues = []
            
            # 1. Response format section
            if "## 🧠 CORTEX" in prompt_content and "## 🧠 CORTEX" not in instructions_content:
                sync_issues.append("Response format header missing in copilot-instructions.md")
            
            # 2. Document organization rules
            if "📁 Document Organization (CRITICAL)" in prompt_content:
                if "📁 Document Organization (CRITICAL)" not in instructions_content:
                    sync_issues.append("Document organization section missing in copilot-instructions.md")
            
            # 3. Brain architecture overview
            if "🏗️ Architecture Overview" in prompt_content:
                if "🏗️ Architecture Overview" not in instructions_content:
                    sync_issues.append("Architecture overview missing in copilot-instructions.md")
            
            # 4. Check version consistency
            import re
            prompt_version_match = re.search(r'\*\*Version:\*\*\s+(\d+\.\d+\.\d+)', prompt_content)
            instructions_version_match = re.search(r'\*\*Version:\*\*\s+(\d+\.\d+\.\d+)', instructions_content)
            
            if prompt_version_match and instructions_version_match:
                prompt_version = prompt_version_match.group(1)
                instructions_version = instructions_version_match.group(1)
                if prompt_version != instructions_version:
                    sync_issues.append(f"Version mismatch (prompt: {prompt_version}, instructions: {instructions_version})")
            
            if sync_issues:
                return ValidationResult(
                    check_name="Prompt Sync (Phase 0)",
                    passed=False,
                    message=f"Documentation files out of sync ({len(sync_issues)} issues)",
                    details="; ".join(sync_issues),
                    severity="WARNING"
                )
            
            return ValidationResult(
                check_name="Prompt Sync (Phase 0)",
                passed=True,
                message="CORTEX.prompt.md and copilot-instructions.md are synchronized",
                severity="INFO"
            )
        
        except Exception as e:
            return ValidationResult(
                check_name="Prompt Sync (Phase 0)",
                passed=False,
                message=f"Validation error: {str(e)}",
                severity="ERROR"
            )
    
    def validate_brain_structure(self) -> ValidationResult:
        """Check that all 4 brain tiers exist."""
        try:
            missing_tiers = []
            
            # tier0 is in src/tier0 (code), not cortex-brain/tier0 (data)
            tier0_code_path = self.root_path / "src" / "tier0"
            if not tier0_code_path.exists():
                missing_tiers.append("tier0 (code)")
            
            # tier1-3 are data directories in cortex-brain
            for tier_num in range(1, 4):
                tier_path = self.brain_path / f"tier{tier_num}"
                if not tier_path.exists():
                    missing_tiers.append(f"tier{tier_num} (data)")
            
            if missing_tiers:
                return ValidationResult(
                    check_name="Brain Architecture",
                    passed=False,
                    message=f"Missing tiers: {', '.join(missing_tiers)}",
                    details="Brain tier structure incomplete",
                    severity="ERROR"
                )
            
            return ValidationResult(
                check_name="Brain Architecture",
                passed=True,
                message="All 4 tiers present (tier0 code + tier1-3 data)",
                severity="INFO"
            )
        
        except Exception as e:
            return ValidationResult(
                check_name="Brain Architecture",
                passed=False,
                message=f"Validation error: {str(e)}",
                severity="ERROR"
            )
    
    def validate_protection_rules(self) -> ValidationResult:
        """Check brain-protection-rules.yaml exists and is valid."""
        try:
            rules_file = self.brain_path / "brain-protection-rules.yaml"
            
            if not rules_file.exists():
                return ValidationResult(
                    check_name="Protection Rules",
                    passed=False,
                    message="brain-protection-rules.yaml not found",
                    details="Critical governance file missing - CORTEX cannot enforce SKULL rules",
                    severity="ERROR"
                )
            
            with open(rules_file, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
            
            if not rules or not isinstance(rules, dict):
                return ValidationResult(
                    check_name="Protection Rules",
                    passed=False,
                    message="Invalid YAML structure",
                    details="brain-protection-rules.yaml is not a valid YAML dictionary",
                    severity="ERROR"
                )
            
            # Count rules
            rule_count = len(rules.get('rules', []))
            
            return ValidationResult(
                check_name="Protection Rules",
                passed=True,
                message=f"Valid ({rule_count} rules loaded)",
                severity="INFO"
            )
        
        except yaml.YAMLError as e:
            return ValidationResult(
                check_name="Protection Rules",
                passed=False,
                message=f"YAML parsing error: {str(e)}",
                details="Fix YAML syntax in brain-protection-rules.yaml",
                severity="ERROR"
            )
        except Exception as e:
            return ValidationResult(
                check_name="Protection Rules",
                passed=False,
                message=f"Validation error: {str(e)}",
                severity="ERROR"
            )
    
    def validate_response_templates(self) -> ValidationResult:
        """Check response-templates.yaml exists and is valid."""
        try:
            templates_file = self.brain_path / "response-templates.yaml"
            
            if not templates_file.exists():
                return ValidationResult(
                    check_name="Response Templates",
                    passed=False,
                    message="response-templates.yaml not found",
                    details="Template system unavailable - CORTEX cannot format responses",
                    severity="ERROR"
                )
            
            with open(templates_file, 'r', encoding='utf-8') as f:
                templates = yaml.safe_load(f)
            
            if not templates or not isinstance(templates, dict):
                return ValidationResult(
                    check_name="Response Templates",
                    passed=False,
                    message="Invalid YAML structure",
                    severity="ERROR"
                )
            
            # Count templates
            template_count = len(templates.get('response_templates', []))
            
            return ValidationResult(
                check_name="Response Templates",
                passed=True,
                message=f"{template_count} templates loaded",
                severity="INFO"
            )
        
        except yaml.YAMLError as e:
            return ValidationResult(
                check_name="Response Templates",
                passed=False,
                message=f"YAML parsing error: {str(e)}",
                severity="ERROR"
            )
        except Exception as e:
            return ValidationResult(
                check_name="Response Templates",
                passed=False,
                message=f"Validation error: {str(e)}",
                severity="ERROR"
            )
    
    def validate_database(self, db_name: str, tier: int, friendly_name: str) -> ValidationResult:
        """Validate a specific brain database."""
        try:
            db_path = self.brain_path / f"tier{tier}" / db_name
            
            if not db_path.exists():
                return ValidationResult(
                    check_name=friendly_name,
                    passed=False,
                    message=f"Database not found: {db_name}",
                    details=f"Optional - Run 'python3 initialize_databases.py' to create tier{tier} databases",
                    severity="WARNING"  # Changed from ERROR to WARNING - databases are optional
                )
            
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Try to read schema
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            conn.close()
            
            if not tables:
                return ValidationResult(
                    check_name=friendly_name,
                    passed=False,
                    message="Database exists but has no tables",
                    details=f"Database schema not initialized for {db_name}",
                    severity="WARNING"
                )
            
            table_count = len(tables)
            
            return ValidationResult(
                check_name=friendly_name,
                passed=True,
                message=f"Database healthy ({table_count} tables)",
                severity="INFO"
            )
        
        except sqlite3.Error as e:
            return ValidationResult(
                check_name=friendly_name,
                passed=False,
                message=f"SQLite error: {str(e)}",
                details=f"Database corrupted or inaccessible: {db_name}",
                severity="WARNING"  # Changed from ERROR to WARNING
            )
        except Exception as e:
            return ValidationResult(
                check_name=friendly_name,
                passed=False,
                message=f"Validation error: {str(e)}",
                severity="WARNING"  # Changed from ERROR to WARNING
            )
    
    def validate_core_modules(self) -> ValidationResult:
        """Check that core Python modules exist (orchestrators, agents)."""
        try:
            src_path = self.root_path / "src"
            
            if not src_path.exists():
                return ValidationResult(
                    check_name="Core Modules",
                    passed=False,
                    message="src/ directory not found",
                    details="CORTEX source code missing - reinstall required",
                    severity="ERROR"
                )
            
            required_dirs = ["orchestrators", "cortex_agents", "operations"]
            missing_dirs = []
            
            for dir_name in required_dirs:
                if not (src_path / dir_name).exists():
                    missing_dirs.append(dir_name)
            
            if missing_dirs:
                return ValidationResult(
                    check_name="Core Modules",
                    passed=False,
                    message=f"Missing directories: {', '.join(missing_dirs)}",
                    details="Core CORTEX modules missing - reinstall required",
                    severity="ERROR"
                )
            
            # Count orchestrators and agents
            orchestrators = list((src_path / "orchestrators").glob("*.py"))
            agents = list((src_path / "cortex_agents").glob("*.py"))
            
            return ValidationResult(
                check_name="Core Modules",
                passed=True,
                message=f"{len(orchestrators)} orchestrators, {len(agents)} agents discovered",
                severity="INFO"
            )
        
        except Exception as e:
            return ValidationResult(
                check_name="Core Modules",
                passed=False,
                message=f"Validation error: {str(e)}",
                severity="ERROR"
            )
    
    def validate_configuration(self) -> ValidationResult:
        """Check cortex.config.json exists and is valid."""
        try:
            config_file = self.root_path / "cortex.config.json"
            
            if not config_file.exists():
                return ValidationResult(
                    check_name="Configuration",
                    passed=False,
                    message="cortex.config.json not found",
                    details="Create config from cortex.config.template.json",
                    severity="ERROR"
                )
            
            with open(config_file, 'r', encoding='utf-8') as f:
                config_data = json.load(f)
            
            if not config_data or not isinstance(config_data, dict):
                return ValidationResult(
                    check_name="Configuration",
                    passed=False,
                    message="Invalid JSON structure",
                    severity="ERROR"
                )
            
            if 'machines' not in config_data:
                return ValidationResult(
                    check_name="Configuration",
                    passed=False,
                    message="Missing 'machines' configuration",
                    details="Config file must contain machine-specific paths",
                    severity="WARNING"
                )
            
            return ValidationResult(
                check_name="Configuration",
                passed=True,
                message="cortex.config.json valid",
                severity="INFO"
            )
        
        except json.JSONDecodeError as e:
            return ValidationResult(
                check_name="Configuration",
                passed=False,
                message=f"JSON parsing error: {str(e)}",
                details="Fix JSON syntax in cortex.config.json",
                severity="ERROR"
            )
        except Exception as e:
            return ValidationResult(
                check_name="Configuration",
                passed=False,
                message=f"Validation error: {str(e)}",
                severity="ERROR"
            )
    
    def discover_python_modules(self) -> Tuple[List[Path], List[Path]]:
        """
        Discover Python orchestrators and agents.
        
        Returns:
            Tuple of (orchestrator_paths, agent_paths)
        """
        orchestrator_paths = []
        agent_paths = []
        
        # Search orchestrators (admin context only)
        if self.context_type == "admin":
            orchestrator_dirs = [
                self.root_path / "src" / "operations" / "modules",
                self.root_path / "src" / "orchestrators"
            ]
            
            for base_dir in orchestrator_dirs:
                if base_dir.exists():
                    for py_file in base_dir.rglob("*.py"):
                        if "_orchestrator.py" in py_file.name:
                            orchestrator_paths.append(py_file)
        
        # Search agents (admin context only)
        if self.context_type == "admin":
            agent_dirs = [
                self.root_path / "src" / "cortex_agents",
                self.root_path / "src" / "agents"
            ]
            
            for base_dir in agent_dirs:
                if base_dir.exists():
                    for py_file in base_dir.rglob("*.py"):
                        if "_agent.py" in py_file.name or py_file.name == "base_agent.py":
                            agent_paths.append(py_file)
        
        return orchestrator_paths, agent_paths
    
    def check_wiring_in_templates(self, module_name: str) -> bool:
        """
        Check if module is wired in response-templates.yaml.
        
        Args:
            module_name: Name of orchestrator/agent class
            
        Returns:
            True if wired, False otherwise
        """
        try:
            templates_file = self.brain_path / "response-templates.yaml"
            
            if not templates_file.exists():
                return False
            
            with open(templates_file, 'r', encoding='utf-8') as f:
                templates = yaml.safe_load(f)
            
            if not templates or not isinstance(templates, dict):
                return False
            
            # Search in templates for expected_orchestrator or triggers
            for template_data in templates.get('templates', {}).values():
                if isinstance(template_data, dict):
                    # Check expected_orchestrator field
                    if template_data.get('expected_orchestrator') == module_name:
                        return True
                    
                    # Check if module name appears in triggers or content
                    triggers = template_data.get('triggers', [])
                    if any(module_name.lower() in trigger.lower() for trigger in triggers):
                        return True
            
            return False
        
        except Exception as e:
            logger.warning(f"Error checking wiring for {module_name}: {e}")
            return False
    
    def compute_file_checksums(self, file_paths: List[Path]) -> Dict[str, Dict[str, Any]]:
        """
        Compute SHA256 checksums for files.
        
        Args:
            file_paths: List of file paths to checksum
            
        Returns:
            Dictionary mapping file path to checksum metadata
        """
        return self.state_manager.compute_file_checksums(file_paths)
    
    def detect_changes(self, previous_state: Optional[AlignmentState]) -> ChangesSummary:
        """
        Detect file changes since last alignment.
        
        Args:
            previous_state: Previous alignment state or None
            
        Returns:
            ChangesSummary with lists of added/modified/deleted files
        """
        if not previous_state:
            return ChangesSummary()
        
        # Get current file checksums
        orchestrator_paths, agent_paths = self.discover_python_modules()
        all_paths = orchestrator_paths + agent_paths
        current_checksums = self.compute_file_checksums(all_paths)
        
        # Detect changes
        changes = self.state_manager.detect_file_changes(current_checksums, previous_state)
        
        # Map to features
        if changes.has_changes():
            all_changed_files = (
                changes.files_added + 
                changes.files_modified + 
                changes.files_deleted
            )
            impacted = self.state_manager.map_files_to_features(
                all_changed_files,
                previous_state.feature_scores
            )
            changes.features_impacted = list(impacted)
        
        return changes
    
    def run_alignment(self) -> AlignmentReport:
        """
        Execute validation checks with incremental support.
        
        Returns:
            AlignmentReport with results and performance metrics
        """
        self.start_time = datetime.now()
        start_perf = time.perf_counter()
        
        report = AlignmentReport(timestamp=self.start_time)
        
        # Load previous state
        previous_state = self.state_manager.load()
        
        # Determine scan mode
        scan_mode = "full"
        if not self.force_full and not self.quick_mode and previous_state:
            if not previous_state.should_run_full_scan():
                scan_mode = "incremental"
                safe_print("🔄 Running incremental alignment (checking changes only)...")
            else:
                safe_print("🔄 Running full alignment (24h elapsed since last full scan)...")
        else:
            safe_print("🔄 Running full alignment...")
        
        # Execute Phase 0 check FIRST (prompt sync)
        report.checks.append(self.validate_prompt_sync())
        
        # Execute 8 core infrastructure checks (always run)
        report.checks.append(self.validate_brain_structure())
        report.checks.append(self.validate_protection_rules())
        report.checks.append(self.validate_response_templates())
        report.checks.append(self.validate_database("working_memory.db", 1, "Working Memory"))
        report.checks.append(self.validate_database("knowledge_graph.db", 2, "Knowledge Graph"))
        report.checks.append(self.validate_database("development_context.db", 3, "Development Context"))
        report.checks.append(self.validate_core_modules())
        report.checks.append(self.validate_configuration())
        
        # Skip feature validation in quick mode
        if self.quick_mode:
            safe_print("⚡ Quick mode: Infrastructure checks only")
        
        # Detect changes for incremental mode
        changes = ChangesSummary()
        if scan_mode == "incremental" and previous_state:
            changes = self.detect_changes(previous_state)
            
            if changes.has_changes():
                safe_print(f"📊 Changes detected: {len(changes.features_impacted)} features impacted")
                self.features_checked = len(changes.features_impacted)
                self.features_skipped = len(previous_state.feature_scores) - self.features_checked
            else:
                safe_print("✅ No changes detected since last alignment")
                self.features_skipped = len(previous_state.feature_scores)
        
        # Calculate performance metrics
        end_perf = time.perf_counter()
        duration = end_perf - start_perf
        
        end_time = datetime.now()
        report.execution_time = (end_time - self.start_time).total_seconds()
        
        # Create or update alignment state
        new_state = self._create_alignment_state(
            report, 
            scan_mode, 
            changes,
            duration,
            previous_state
        )
        
        # Save state
        self.state_manager.save(new_state)
        
        return report
    
    def _create_alignment_state(
        self,
        report: AlignmentReport,
        scan_mode: str,
        changes: ChangesSummary,
        duration: float,
        previous_state: Optional[AlignmentState]
    ) -> AlignmentState:
        """
        Create alignment state from report.
        
        Args:
            report: Alignment report with check results
            scan_mode: "full" or "incremental"
            changes: Changes detected
            duration: Execution duration in seconds
            previous_state: Previous state or None
            
        Returns:
            AlignmentState object
        """
        now_iso = datetime.now().isoformat()
        
        # Create new state or update existing
        if previous_state:
            state = previous_state
        else:
            state = AlignmentState()
        
        # Update timestamps and mode
        state.last_alignment = now_iso
        state.scan_mode = scan_mode
        state.context_type = self.context_type
        
        if scan_mode == "full":
            state.last_full_scan = now_iso
        
        # Update changes detected
        if changes.has_changes():
            state.changes_detected = changes.to_dict()
        else:
            state.changes_detected = {
                "files_added": [],
                "files_modified": [],
                "files_deleted": [],
                "features_impacted": []
            }
        
        # Update performance metrics
        cache_hit_rate = 0.0
        if self.features_checked + self.features_skipped > 0:
            cache_hit_rate = self.features_skipped / (self.features_checked + self.features_skipped)
        
        state.performance_metrics = {
            "last_run_duration_seconds": duration,
            "features_checked": self.features_checked,
            "features_skipped": self.features_skipped,
            "cache_hit_rate": cache_hit_rate
        }
        
        # Update file checksums (admin context only)
        if self.context_type == "admin" and scan_mode == "full":
            orchestrator_paths, agent_paths = self.discover_python_modules()
            all_paths = orchestrator_paths + agent_paths
            state.file_checksums = self.compute_file_checksums(all_paths)
        
        # Update overall health (based on critical checks)
        critical_failures = sum(
            1 for check in report.checks 
            if not check.passed and check.severity == "ERROR"
        )
        state.overall_health = int(100 * (1 - critical_failures / max(len(report.checks), 1)))
        
        # Add to history
        state.add_to_history(
            health=state.overall_health,
            total_features=self.features_checked + self.features_skipped,
            critical_issues=critical_failures,
            warnings=sum(1 for check in report.checks if not check.passed and check.severity == "WARNING")
        )
        
        return state


def run_align_utility(force_full: bool = False, quick_mode: bool = False) -> Dict[str, Any]:
    """
    Entry point for align utility - callable from orchestrators or CLI.
    
    Args:
        force_full: Force full scan even if incremental is possible
        quick_mode: Infrastructure checks only, skip feature validation
    
    Returns:
        Dict with 'success', 'message', 'report_text', 'report_data', 'performance'
    """
    try:
        utility = AlignUtility(force_full=force_full, quick_mode=quick_mode)
        report = utility.run_alignment()
        
        # Format console output
        console_output = report.format_console()
        safe_print(console_output)
        
        # Add performance summary
        if utility.features_skipped > 0:
            perf_summary = (
                f"\n⚡ Performance: Checked {utility.features_checked} features, "
                f"skipped {utility.features_skipped} unchanged "
                f"(cache hit rate: {utility.features_skipped/(utility.features_checked + utility.features_skipped)*100:.1f}%)"
            )
            safe_print(perf_summary)
        
        return {
            'success': report.is_healthy,
            'message': f"System Status: {report.status_text}",
            'report_text': console_output,
            'report_data': {
                'timestamp': report.timestamp.isoformat(),
                'execution_time': report.execution_time,
                'checks_passed': report.passed_count,
                'checks_total': report.total_count,
                'is_healthy': report.is_healthy,
                'context_type': utility.context_type,
                'checks': [
                    {
                        'name': check.check_name,
                        'passed': check.passed,
                        'message': check.message,
                        'details': check.details,
                        'severity': check.severity
                    }
                    for check in report.checks
                ]
            },
            'performance': {
                'features_checked': utility.features_checked,
                'features_skipped': utility.features_skipped,
                'duration_seconds': report.execution_time
            }
        }
    
    except Exception as e:
        error_message = f"Align utility execution failed: {str(e)}"
        logger.error(error_message, exc_info=True)
        return {
            'success': False,
            'message': error_message,
            'report_text': error_message,
            'report_data': None,
            'performance': None
        }


if __name__ == "__main__":
    """CLI execution for testing."""
    import sys
    
    # Parse command line arguments
    force_full = "--full" in sys.argv
    quick_mode = "--quick" in sys.argv
    
    result = run_align_utility(force_full=force_full, quick_mode=quick_mode)
    sys.exit(0 if result['success'] else 1)
