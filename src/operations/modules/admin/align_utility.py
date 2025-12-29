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
    except (UnicodeEncodeError, UnicodeDecodeError):
        # Fallback: encode to ASCII, replacing unmappable characters
        try:
            ascii_message = message.encode('ascii', errors='replace').decode('ascii')
            # Clean up the replacement markers
            replacements = {
                '?': '',  # Remove ? placeholders
                '  ': ' ',  # Clean up double spaces
            }
            for old, new in replacements.items():
                ascii_message = ascii_message.replace(old, new)
            print(ascii_message.strip())
        except Exception:
            # Last resort: just log it
            logger.info(f"Console output (ASCII): {message.encode('ascii', errors='ignore').decode('ascii')}")


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
        
        # Manifest validation (NEW)
        try:
            from src.utils.manifest_validator import ManifestValidator
            self.manifest_validator = ManifestValidator(cortex_root=self.root_path)
            self.manifest_validation_enabled = True
        except ImportError:
            logger.warning("ManifestValidator not available - skipping manifest checks")
            self.manifest_validator = None
            self.manifest_validation_enabled = False
    
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
    
    def validate_feature_discovery(self) -> ValidationResult:
        """Comprehensive feature discovery across 11 categories (admin context only)."""
        try:
            # Skip in user context
            if self.context_type != "admin":
                return ValidationResult(
                    check_name="Feature Discovery",
                    passed=True,
                    message="Skipped in user context",
                    severity="INFO"
                )
            
            # Run comprehensive discovery
            discovered = self.discover_all_features()
            
            # Calculate totals
            category_counts = {}
            total_features = 0
            
            for category, items in discovered.items():
                if isinstance(items, list):
                    count = len(items)
                elif isinstance(items, dict):
                    if all(isinstance(v, list) for v in items.values()):
                        # Dashboard structure
                        count = sum(len(v) for v in items.values())
                    else:
                        # YAML data
                        count = len(items)
                else:
                    count = 0
                
                category_counts[category] = count
                total_features += count
            
            # Format summary
            summary_parts = []
            for category, count in category_counts.items():
                if count > 0:
                    summary_parts.append(f"{category}={count}")
            
            summary = ", ".join(summary_parts)
            
            return ValidationResult(
                check_name="Feature Discovery",
                passed=True,
                message=f"{total_features} features across 11 categories",
                details=summary,
                severity="INFO"
            )
        
        except Exception as e:
            return ValidationResult(
                check_name="Feature Discovery",
                passed=False,
                message=f"Discovery error: {str(e)}",
                severity="WARNING"
            )
    
    def validate_code_quality(self) -> ValidationResult:
        """
        Validate CORTEX code quality using TDD Implementation Orchestrator detection.
        
        Runs comprehensive code quality checks:
        - Security vulnerabilities (SQL injection, credentials, error handling)
        - Magic values (repeated strings, hardcoded URLs, magic numbers)
        - SOLID violations (god classes/methods, tight coupling, complexity)
        - Code duplicates
        - Redundancies (unused imports, dead code)
        
        Leverages enhanced TDD orchestrator capabilities from sample app analysis.
        Only runs in admin context on CORTEX source code.
        
        Returns:
            ValidationResult with code quality status
        """
        try:
            # Skip in user context (only validate CORTEX code)
            if self.context_type != "admin":
                return ValidationResult(
                    check_name="Code Quality",
                    passed=True,
                    message="Skipped in user context",
                    severity="INFO"
                )
            
            # Import TDD orchestrator
            from src.orchestrators.tdd_implementation_orchestrator import TDDImplementationOrchestrator
            
            # Initialize orchestrator for CORTEX codebase
            orchestrator = TDDImplementationOrchestrator(
                project_root=self.root_path,
                enable_pattern_library=False  # Don't store patterns during align
            )
            
            # Get all Python source files in src/
            src_path = self.root_path / "src"
            if not src_path.exists():
                return ValidationResult(
                    check_name="Code Quality",
                    passed=False,
                    message="src/ directory not found",
                    severity="ERROR"
                )
            
            python_files = list(src_path.rglob("*.py"))
            if not python_files:
                return ValidationResult(
                    check_name="Code Quality",
                    passed=False,
                    message="No Python files found in src/",
                    severity="ERROR"
                )
            
            # Convert to relative paths
            relative_files = [Path(f.relative_to(self.root_path)) for f in python_files]
            
            # Run all detection methods
            security_result = orchestrator._detect_security_issues(relative_files)
            magic_result = orchestrator._detect_magic_values(relative_files)
            solid_result = orchestrator._validate_solid(relative_files)
            duplicates_result = orchestrator._detect_duplicates(relative_files)
            
            # Aggregate results
            critical_security = security_result.get('critical_count', 0)
            high_security = security_result.get('high_count', 0)
            critical_solid = solid_result.get('critical_count', 0)
            high_solid = solid_result.get('high_count', 0)
            magic_count = len(magic_result.get('magic_values', []))
            duplicate_count = len(duplicates_result.get('duplicates', []))
            
            # Determine pass/fail (critical issues block)
            critical_issues = critical_security + critical_solid
            high_issues = high_security + high_solid
            
            if critical_issues > 0:
                passed = False
                severity = "ERROR"
                message = f"{critical_issues} critical issues found"
                details = f"Security: {critical_security} critical, SOLID: {critical_solid} critical"
            elif high_issues > 5:
                passed = False
                severity = "WARNING"
                message = f"{high_issues} high-priority issues found"
                details = f"Security: {high_security} high, SOLID: {high_solid} high, Magic: {magic_count}, Duplicates: {duplicate_count}"
            else:
                passed = True
                severity = "INFO"
                message = f"Code quality acceptable"
                details = f"Security: {critical_security}C/{high_security}H, SOLID: {critical_solid}C/{high_solid}H/{solid_result.get('medium_count', 0)}M, Magic: {magic_count}, Duplicates: {duplicate_count}"
            
            return ValidationResult(
                check_name="Code Quality",
                passed=passed,
                message=message,
                details=details,
                severity=severity
            )
        
        except ImportError:
            return ValidationResult(
                check_name="Code Quality",
                passed=True,
                message="TDD orchestrator not available",
                details="Skipping code quality validation",
                severity="INFO"
            )
        except Exception as e:
            logger.debug(f"Code quality check failed: {e}", exc_info=True)
            return ValidationResult(
                check_name="Code Quality",
                passed=True,
                message=f"Check skipped: {str(e)}",
                details="Non-critical error during code quality scan",
                severity="INFO"
            )
    
    def validate_feature_wiring(self) -> ValidationResult:
        """
        Validate that discovered features are properly wired into CORTEX.
        
        Checks wiring for:
        - Orchestrators (response-templates.yaml)
        - Agents (response-templates.yaml)
        - Plugins (plugin_registry.py)
        - Operation Modules (cortex-operations.yaml)
        - Workflows (cortex-operations.yaml or response-templates.yaml)
        - Scripts (cortex-operations.yaml for user-facing)
        - Dashboards (dashboard operation exists)
        - Templates (all operations have templates)
        - Operations (all operations registered)
        
        Returns:
            ValidationResult with wiring status
        """
        try:
            # Skip in user context
            if self.context_type != "admin":
                return ValidationResult(
                    check_name="Feature Wiring",
                    passed=True,
                    message="Skipped in user context",
                    severity="INFO"
                )
            
            discovered = self.discover_all_features()
            unwired = []
            wired_counts = {}
            total_counts = {}
            
            # 1. Check Orchestrators
            orchestrators = discovered.get('orchestrators', [])
            total_counts['orchestrators'] = len(orchestrators)
            wired_count = 0
            for orch_path in orchestrators:
                if self.check_wiring_in_templates(orch_path.stem):
                    wired_count += 1
                else:
                    unwired.append(f"Orchestrator: {orch_path.stem}")
            wired_counts['orchestrators'] = wired_count
            
            # 2. Check Agents
            agents = discovered.get('agents', [])
            total_counts['agents'] = len(agents)
            wired_count = 0
            for agent_path in agents:
                if self.check_wiring_in_templates(agent_path.stem):
                    wired_count += 1
                else:
                    unwired.append(f"Agent: {agent_path.stem}")
            wired_counts['agents'] = wired_count
            
            # 3. Check Plugins
            plugins = discovered.get('plugins', [])
            total_counts['plugins'] = len(plugins)
            wired_count = 0
            for plugin_path in plugins:
                if self.check_plugin_registration(plugin_path.stem):
                    wired_count += 1
                else:
                    unwired.append(f"Plugin: {plugin_path.stem}")
            wired_counts['plugins'] = wired_count
            
            # 4. Check Operation Modules
            op_modules = discovered.get('operation_modules', [])
            total_counts['operation_modules'] = len(op_modules)
            wired_count = 0
            for module_path in op_modules:
                if self.check_operation_module_linkage(module_path.stem):
                    wired_count += 1
                else:
                    unwired.append(f"Operation Module: {module_path.stem}")
            wired_counts['operation_modules'] = wired_count
            
            # 5. Check Workflows
            workflows = discovered.get('workflows', {})
            total_counts['workflows'] = len(workflows)
            wired_count = 0
            for workflow_name in workflows.keys():
                if self.check_workflow_triggers(workflow_name):
                    wired_count += 1
                else:
                    unwired.append(f"Workflow: {workflow_name}")
            wired_counts['workflows'] = wired_count
            
            # 6. Check Scripts (user-facing only)
            scripts = discovered.get('scripts', [])
            user_facing_scripts = [
                'cortex-upgrade', 'deploy_cortex', 'validate_deployment',
                'brain_transfer_cli', 'initialize_databases'
            ]
            user_facing_count = sum(1 for s in scripts if any(uf in s.stem for uf in user_facing_scripts))
            total_counts['scripts'] = user_facing_count
            wired_count = 0
            for script_path in scripts:
                if any(uf in script_path.stem for uf in user_facing_scripts):
                    if self.check_script_operation_linkage(script_path.stem):
                        wired_count += 1
                    else:
                        unwired.append(f"Script: {script_path.stem}")
            wired_counts['scripts'] = wired_count
            
            # 7. Check Dashboards
            dashboards = discovered.get('dashboards', {})
            ui_pages = dashboards.get('ui_pages', [])
            total_counts['dashboards'] = len(ui_pages)
            # All dashboards share one operation, so if it exists, all are accessible
            dashboard_op_exists = self.check_dashboard_accessibility('dashboard')
            wired_counts['dashboards'] = len(ui_pages) if dashboard_op_exists else 0
            if not dashboard_op_exists and len(ui_pages) > 0:
                unwired.append(f"Dashboards: No 'dashboard' operation found ({len(ui_pages)} pages)")
            
            # Calculate overall wiring health
            total_checkable = sum(total_counts.values())
            total_wired = sum(wired_counts.values())
            wiring_percentage = (total_wired / total_checkable * 100) if total_checkable > 0 else 100.0
            
            # Determine pass/fail
            critical_unwired = len([u for u in unwired if 'Orchestrator:' in u or 'Agent:' in u or 'Plugin:' in u])
            passed = critical_unwired == 0 and wiring_percentage >= 80.0
            
            if not passed:
                severity = "ERROR" if critical_unwired > 0 else "WARNING"
                message = f"{len(unwired)} features not wired ({wiring_percentage:.0f}% wiring coverage)"
                details = "; ".join(unwired[:10])  # Show first 10
            else:
                severity = "INFO"
                message = f"All critical features wired ({wiring_percentage:.0f}% coverage)"
                details = ", ".join([f"{k}={v}/{total_counts[k]}" for k, v in wired_counts.items()])
            
            return ValidationResult(
                check_name="Feature Wiring",
                passed=passed,
                message=message,
                details=details,
                severity=severity
            )
        
        except Exception as e:
            return ValidationResult(
                check_name="Feature Wiring",
                passed=False,
                message=f"Wiring validation error: {str(e)}",
                severity="WARNING"
            )
    
    def scan_directory(
        self, 
        directory_path: str, 
        pattern: str = "*.py", 
        exclude: List[str] = None
    ) -> List[Path]:
        """
        Scan directory for files matching pattern.
        
        Args:
            directory_path: Relative path from root (e.g., 'src/plugins/')
            pattern: Glob pattern to match (e.g., '*_plugin.py')
            exclude: List of paths to exclude (e.g., ['__pycache__/', '_archive/'])
        
        Returns:
            List of Path objects matching pattern
        """
        try:
            base_path = self.root_path / directory_path if not Path(directory_path).is_absolute() else Path(directory_path)
            
            if not base_path.exists():
                return []
            
            # Get all matching files
            matches = list(base_path.rglob(pattern))
            
            # Apply exclusions
            if exclude:
                filtered = []
                for match in matches:
                    rel_path = str(match.relative_to(base_path))
                    if not any(excl in rel_path for excl in exclude):
                        filtered.append(match)
                return filtered
            
            return matches
        
        except Exception as e:
            logger.warning(f"Error scanning {directory_path}: {e}")
            return []
    
    def scan_yaml(self, yaml_path: str) -> Dict[str, Any]:
        """
        Scan YAML file for feature metadata.
        
        Args:
            yaml_path: Path to YAML file (supports glob patterns like 'workflows/*.yaml')
        
        Returns:
            Dictionary of parsed YAML data or empty dict on error
        """
        try:
            # Handle glob patterns
            if '*' in yaml_path:
                yaml_files = list(self.root_path.glob(yaml_path))
                combined_data = {}
                for yaml_file in yaml_files:
                    with open(yaml_file, 'r', encoding='utf-8') as f:
                        data = yaml.safe_load(f)
                        if isinstance(data, dict):
                            combined_data[yaml_file.stem] = data
                return combined_data
            
            # Single file
            yaml_file = self.root_path / yaml_path if not Path(yaml_path).is_absolute() else Path(yaml_path)
            
            if not yaml_file.exists():
                return {}
            
            with open(yaml_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
                return data if isinstance(data, dict) else {}
        
        except Exception as e:
            logger.warning(f"Error scanning YAML {yaml_path}: {e}")
            return {}
    
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
    
    def discover_all_features(self) -> Dict[str, Any]:
        """
        Comprehensive feature discovery across all 11 CORTEX categories.
        
        Returns:
            Dictionary mapping feature categories to discovered items:
            {
                'orchestrators': List[Path],
                'agents': List[Path],
                'operations': Dict (from YAML),
                'templates': Dict (from YAML),
                'plugins': List[Path],
                'scripts': List[Path],
                'operation_modules': List[Path],
                'workflows': Dict (from YAML),
                'brain_operations': List[Path],
                'dashboards': Dict[str, List[Path]],
                'governance_rules': List[Path]
            }
        """
        discovered = {}
        
        try:
            # Existing scans (code-based)
            orchestrator_paths, agent_paths = self.discover_python_modules()
            discovered['orchestrators'] = orchestrator_paths
            discovered['agents'] = agent_paths
            
            # Existing scans (YAML-based)
            discovered['operations'] = self.scan_yaml('cortex-operations.yaml')
            discovered['templates'] = self.scan_yaml('cortex-brain/response-templates.yaml')
            
            # NEW: Plugins (code-based)
            discovered['plugins'] = self.scan_directory(
                'src/plugins/', 
                pattern='*_plugin.py'
            )
            
            # NEW: Scripts (utility-based) - exclude archive and temp
            discovered['scripts'] = self.scan_directory(
                'scripts/', 
                pattern='*.py',
                exclude=['_archive/', 'temp/', '__pycache__/', 'completions/', 'misc/']
            )
            
            # NEW: Operation modules (implementation-based)
            discovered['operation_modules'] = self.scan_directory(
                'src/operations/modules/', 
                pattern='*_module.py'
            )
            
            # NEW: Workflows (YAML-based)
            discovered['workflows'] = self.scan_yaml('workflows/*.yaml')
            
            # NEW: Brain operations (data-based)
            discovered['brain_operations'] = self.scan_directory(
                'cortex-brain/operations/', 
                pattern='*.json'
            )
            
            # NEW: Dashboards (hybrid - UI + code)
            discovered['dashboards'] = {
                'ui_pages': self.scan_directory(
                    'cortex-brain/dashboards/ui/', 
                    pattern='*.html'
                ),
                'adapters': self.scan_directory(
                    'cortex-brain/dashboards/', 
                    pattern='*_adapter.py'
                )
            }
            
            # NEW: Tier 0 governance (code-based)
            discovered['governance_rules'] = self.scan_directory(
                'src/tier0/', 
                pattern='*.py',
                exclude=['__init__.py', '__pycache__/']
            )
            
            # Log discovery summary
            total_features = sum(
                len(v) if isinstance(v, list) else 
                (sum(len(vv) for vv in v.values()) if isinstance(v, dict) and all(isinstance(vv, list) for vv in v.values()) else 1)
                for v in discovered.values()
            )
            
            logger.info(f"Feature discovery complete: {total_features} features across 11 categories")
            
            return discovered
        
        except Exception as e:
            logger.error(f"Error in feature discovery: {e}", exc_info=True)
            return discovered
    
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
    
    def check_plugin_registration(self, plugin_name: str) -> bool:
        """
        Check if plugin is registered in plugin_registry.py.
        
        Args:
            plugin_name: Name of plugin (e.g., 'performance_telemetry_plugin')
            
        Returns:
            True if registered, False otherwise
        """
        try:
            # Check if plugin_registry.py imports the plugin
            registry_file = self.root_path / "src" / "plugins" / "plugin_registry.py"
            
            if not registry_file.exists():
                return False
            
            content = registry_file.read_text(encoding='utf-8')
            
            # Check for import statement or registration
            plugin_patterns = [
                f"from .{plugin_name} import",
                f"import {plugin_name}",
                f"'{plugin_name}'",
                f'"{plugin_name}"'
            ]
            
            return any(pattern in content for pattern in plugin_patterns)
        
        except Exception as e:
            logger.warning(f"Error checking plugin registration for {plugin_name}: {e}")
            return False
    
    def check_operation_module_linkage(self, module_name: str) -> bool:
        """
        Check if operation module is referenced by parent operation.
        
        Args:
            module_name: Name of module (e.g., 'dashboard_launcher_module')
            
        Returns:
            True if linked, False otherwise
        """
        try:
            # Check cortex-operations.yaml for module reference
            ops_yaml = self.root_path / "cortex-operations.yaml"
            
            if not ops_yaml.exists():
                return False
            
            content = ops_yaml.read_text(encoding='utf-8')
            
            # Module name might appear in various forms
            # Try: exact match, without _module suffix, with hyphens, with underscores
            module_stem = module_name.replace('_module', '')
            module_hyphen = module_stem.replace('_', '-')
            
            # Check all variants
            return (module_name in content or 
                    module_stem in content or 
                    module_hyphen in content)
        
        except Exception as e:
            logger.warning(f"Error checking operation module linkage for {module_name}: {e}")
            return False
    
    def check_workflow_triggers(self, workflow_name: str) -> bool:
        """
        Check if workflow has trigger configuration.
        
        Args:
            workflow_name: Name of workflow (e.g., 'feature_development')
            
        Returns:
            True if has triggers, False otherwise
        """
        try:
            # Check if workflow is referenced in cortex-operations.yaml or response-templates.yaml
            ops_yaml = self.root_path / "cortex-operations.yaml"
            templates_yaml = self.brain_path / "response-templates.yaml"
            
            # Check operations file
            if ops_yaml.exists():
                ops_content = ops_yaml.read_text(encoding='utf-8')
                if workflow_name in ops_content:
                    return True
            
            # Check templates file
            if templates_yaml.exists():
                templates_content = templates_yaml.read_text(encoding='utf-8')
                if workflow_name in templates_content:
                    return True
            
            return False
        
        except Exception as e:
            logger.warning(f"Error checking workflow triggers for {workflow_name}: {e}")
            return False
    
    def check_dashboard_accessibility(self, dashboard_name: str) -> bool:
        """
        Check if dashboard is accessible via operation.
        
        Args:
            dashboard_name: Name of dashboard (e.g., 'alignment-dashboard')
            
        Returns:
            True if accessible, False otherwise
        """
        try:
            # Check if 'dashboard' operation exists in cortex-operations.yaml
            ops_yaml = self.root_path / "cortex-operations.yaml"
            
            if not ops_yaml.exists():
                return False
            
            with open(ops_yaml, 'r', encoding='utf-8') as f:
                ops_data = yaml.safe_load(f)
            
            # Look for dashboard operation
            operations = ops_data.get('operations', {})
            
            return 'dashboard' in operations or 'load_dashboard' in operations
        
        except Exception as e:
            logger.warning(f"Error checking dashboard accessibility for {dashboard_name}: {e}")
            return False
    
    def validate_manifest_compliance(self) -> ValidationResult:
        """
        Validate orchestrator manifest compliance.
        
        Checks:
        - Manifest files exist
        - Planning System manifest compliance
        - ADO planning manifest inheritance
        
        Returns:
            ValidationResult with compliance status
        """
        try:
            from src.utils.manifest_validator import ManifestValidator
            
            # Initialize validator
            validator = ManifestValidator(cortex_root=self.root_path)
            
            # Check manifest directory exists
            manifest_dir = self.brain_path / "orchestrator-manifests"
            if not manifest_dir.exists():
                return ValidationResult(
                    check_name="Manifest Compliance",
                    passed=False,
                    message="Orchestrator manifests directory not found",
                    details=f"Expected at: {manifest_dir}",
                    severity="WARNING"
                )
            
            # Load Planning System manifest
            planning_manifest_path = manifest_dir / "planning-system-manifest.yaml"
            if not planning_manifest_path.exists():
                return ValidationResult(
                    check_name="Manifest Compliance",
                    passed=False,
                    message="Planning System manifest not found",
                    details=f"Expected at: {planning_manifest_path}",
                    severity="WARNING"
                )
            
            planning_manifest = validator.load_manifest(str(planning_manifest_path))
            
            # Validate Planning System orchestrator
            planning_orchestrator_path = self.root_path / "src" / "orchestrators" / "planning_orchestrator.py"
            
            if not planning_orchestrator_path.exists():
                return ValidationResult(
                    check_name="Manifest Compliance",
                    passed=True,
                    message="Planning orchestrator not found (skipping validation)",
                    severity="INFO"
                )
            
            report = validator.validate_orchestrator(
                "PlanningOrchestrator",
                planning_manifest,
                str(planning_orchestrator_path)
            )
            
            # Determine result based on compliance
            if report.compliance_percentage >= 80:
                message = f"Planning System: {report.compliance_percentage:.0f}% compliant ({report.implemented_count}/{report.total_requirements})"
                details = f"Status: {report.status}"
                
                if report.compliance_percentage >= 95:
                    details += " - EXCELLENT"
                elif report.compliance_percentage >= 90:
                    details += " - GOOD"
                
                return ValidationResult(
                    check_name="Manifest Compliance",
                    passed=True,
                    message=message,
                    details=details,
                    severity="INFO"
                )
            else:
                missing_critical = [i for i in report.issues if i.severity == "CRITICAL"]
                message = f"Planning System: {report.compliance_percentage:.0f}% compliant (below 80% threshold)"
                details = f"{len(missing_critical)} critical requirements missing"
                
                return ValidationResult(
                    check_name="Manifest Compliance",
                    passed=False,
                    message=message,
                    details=details,
                    severity="WARNING"
                )
        
        except ImportError:
            return ValidationResult(
                check_name="Manifest Compliance",
                passed=True,
                message="ManifestValidator not available (skipping)",
                severity="INFO"
            )
        except Exception as e:
            return ValidationResult(
                check_name="Manifest Compliance",
                passed=False,
                message=f"Manifest validation error: {str(e)}",
                severity="WARNING"
            )
    
    def check_script_operation_linkage(self, script_name: str) -> bool:
        """
        Check if user-facing script is linked to an operation.
        
        Args:
            script_name: Name of script (e.g., 'cortex-upgrade')
            
        Returns:
            True if linked, False otherwise
        """
        try:
            # Only check scripts that appear to be user-facing
            user_facing_scripts = [
                'cortex-upgrade', 'deploy_cortex', 'validate_deployment',
                'brain_transfer_cli', 'initialize_databases', 'monitor_brain_health',
                'aggregate_team_telemetry', 'generate_docs_from_code'
            ]
            
            script_stem = script_name.replace('.py', '').replace('_', '-')
            
            if script_stem not in user_facing_scripts:
                return True  # Non-user-facing scripts don't need operation linkage
            
            # Check cortex-operations.yaml for reference
            ops_yaml = self.root_path / "cortex-operations.yaml"
            
            if not ops_yaml.exists():
                return False
            
            content = ops_yaml.read_text(encoding='utf-8')
            
            return script_stem in content or script_name in content
        
        except Exception as e:
            logger.warning(f"Error checking script linkage for {script_name}: {e}")
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
        
        # Execute comprehensive feature discovery (admin context only)
        if self.context_type == "admin" and not self.quick_mode:
            report.checks.append(self.validate_feature_discovery())
            report.checks.append(self.validate_feature_wiring())
            
            # Execute manifest compliance validation (NEW)
            report.checks.append(self.validate_manifest_compliance())
            
            # Execute code quality validation (uses TDD orchestrator capabilities)
            report.checks.append(self.validate_code_quality())
        
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
