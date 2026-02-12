"""
ENH-063 P1-009: Configuration Drift Detection and Sync
AC-ENH063-P1-009-001

Detects and resolves configuration drift between:
- cortex/wiring/specifications/wiring.yaml (source of truth)
- cortex/__wiring_contract__.yaml (generated contract)

Components:
1. Configuration loader (parse wiring YAML)
2. Drift detector (compare source vs contract)
3. Sync engine (regenerate contract from source)
4. Validation report (drift metrics)

TDD: Tests in tests/mcp/test_config_drift.py
"""

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml


# ============================================================================
# TYPE DEFINITIONS
# ============================================================================


class DriftType(Enum):
    """Types of configuration drift"""
    MISSING_ORCHESTRATOR = "missing_orchestrator"
    EXTRA_ORCHESTRATOR = "extra_orchestrator"
    MISMATCHED_CAPABILITY = "mismatched_capability"
    MISSING_DEPENDENCY = "missing_dependency"
    INVALID_PRIORITY = "invalid_priority"
    SCHEMA_MISMATCH = "schema_mismatch"


class DriftSeverity(Enum):
    """Severity levels for drift issues"""
    CRITICAL = "critical"  # System may fail
    HIGH = "high"  # Functionality degraded
    MEDIUM = "medium"  # Minor issues
    LOW = "low"  # Cosmetic differences


@dataclass
class DriftIssue:
    """Represents a single configuration drift issue"""
    drift_type: DriftType
    severity: DriftSeverity
    path: str
    description: str
    source_value: Optional[Any] = None
    contract_value: Optional[Any] = None
    remediation: Optional[str] = None

    def __str__(self) -> str:
        return (
            f"[{self.severity.value.upper()}] {self.drift_type.value}: "
            f"{self.description} (path: {self.path})"
        )


@dataclass
class DriftReport:
    """Comprehensive configuration drift report"""
    timestamp: datetime
    source_path: Path
    contract_path: Path
    issues: List[DriftIssue] = field(default_factory=list)
    source_hash: Optional[str] = None
    contract_hash: Optional[str] = None

    def has_drift(self) -> bool:
        """Check if any drift detected"""
        return len(self.issues) > 0

    def critical_issues(self) -> List[DriftIssue]:
        """Get critical severity issues"""
        return [i for i in self.issues if i.severity == DriftSeverity.CRITICAL]

    def high_issues(self) -> List[DriftIssue]:
        """Get high severity issues"""
        return [i for i in self.issues if i.severity == DriftSeverity.HIGH]

    def summary(self) -> str:
        """Generate summary string"""
        if not self.has_drift():
            return "No drift detected"

        by_severity = {}
        for issue in self.issues:
            severity = issue.severity.value
            by_severity[severity] = by_severity.get(severity, 0) + 1

        parts = [f"{count} {severity}" for severity, count in by_severity.items()]
        return f"Drift detected: {', '.join(parts)}"


# ============================================================================
# CONFIGURATION LOADER
# ============================================================================


class ConfigurationLoader:
    """Load and parse wiring YAML configurations"""

    def __init__(self, workspace_root: Optional[Path] = None):
        """
        Initialize configuration loader.

        Args:
            workspace_root: Root directory of CORTEX workspace
        """
        self.workspace_root = workspace_root or Path.cwd()
        self.logger = logging.getLogger(__name__)

    def load_source_config(self) -> Dict[str, Any]:
        """
        Load source wiring configuration.

        Returns:
            Parsed wiring.yaml dictionary

        Raises:
            FileNotFoundError: If wiring.yaml not found
        """
        wiring_path = self.workspace_root / "cortex" / "wiring" / "specifications" / "wiring.yaml"

        if not wiring_path.exists():
            raise FileNotFoundError(f"Source config not found: {wiring_path}")

        with open(wiring_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        self.logger.info(f"Loaded source config: {wiring_path}")
        return config

    def load_contract_config(self) -> Dict[str, Any]:
        """
        Load contract wiring configuration.

        Returns:
            Parsed __wiring_contract__.yaml dictionary

        Raises:
            FileNotFoundError: If contract not found
        """
        contract_path = self.workspace_root / "cortex" / "__wiring_contract__.yaml"

        if not contract_path.exists():
            raise FileNotFoundError(f"Contract not found: {contract_path}")

        with open(contract_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        self.logger.info(f"Loaded contract config: {contract_path}")
        return config

    def compute_hash(self, config: Dict[str, Any]) -> str:
        """
        Compute SHA256 hash of configuration.

        Args:
            config: Configuration dictionary

        Returns:
            Hex digest of configuration hash
        """
        # Serialize to canonical YAML for stable hashing
        yaml_str = yaml.dump(config, sort_keys=True, default_flow_style=False)
        return hashlib.sha256(yaml_str.encode("utf-8")).hexdigest()


# ============================================================================
# DRIFT DETECTOR
# ============================================================================


class DriftDetector:
    """Detect configuration drift between source and contract"""

    def __init__(self, loader: ConfigurationLoader):
        """
        Initialize drift detector.

        Args:
            loader: Configuration loader instance
        """
        self.loader = loader
        self.logger = logging.getLogger(__name__)

    def detect_drift(self) -> DriftReport:
        """
        Detect drift between source and contract.

        Returns:
            DriftReport with all detected issues
        """
        source_path = self.loader.workspace_root / "cortex" / "wiring" / "specifications" / "wiring.yaml"
        contract_path = self.loader.workspace_root / "cortex" / "__wiring_contract__.yaml"

        # Load configurations
        try:
            source_config = self.loader.load_source_config()
            contract_config = self.loader.load_contract_config()
        except FileNotFoundError as e:
            self.logger.error(f"Configuration file missing: {e}")
            return DriftReport(
                timestamp=datetime.now(),
                source_path=source_path,
                contract_path=contract_path,
                issues=[
                    DriftIssue(
                        drift_type=DriftType.SCHEMA_MISMATCH,
                        severity=DriftSeverity.CRITICAL,
                        path="root",
                        description=str(e),
                        remediation="Run wiring generation script"
                    )
                ]
            )

        # Compute hashes
        source_hash = self.loader.compute_hash(source_config)
        contract_hash = self.loader.compute_hash(contract_config)

        # Initialize report
        report = DriftReport(
            timestamp=datetime.now(),
            source_path=source_path,
            contract_path=contract_path,
            source_hash=source_hash,
            contract_hash=contract_hash
        )

        # If hashes match, no drift
        if source_hash == contract_hash:
            self.logger.info("No drift detected (hashes match)")
            return report

        # Perform detailed comparison
        self._compare_orchestrators(source_config, contract_config, report)
        self._compare_capabilities(source_config, contract_config, report)
        self._compare_dependencies(source_config, contract_config, report)

        self.logger.info(f"Drift detected: {report.summary()}")
        return report

    def _compare_orchestrators(
        self,
        source: Dict[str, Any],
        contract: Dict[str, Any],
        report: DriftReport
    ) -> None:
        """Compare orchestrators between source and contract"""
        source_orcks = set(source.get("orchestrators", {}).keys())
        contract_orcks = set(contract.get("orchestrators", {}).keys())

        # Missing orchestrators (in source but not contract)
        missing = source_orcks - contract_orcks
        for orch_name in missing:
            report.issues.append(
                DriftIssue(
                    drift_type=DriftType.MISSING_ORCHESTRATOR,
                    severity=DriftSeverity.CRITICAL,
                    path=f"orchestrators.{orch_name}",
                    description=f"Orchestrator '{orch_name}' in source but missing from contract",
                    source_value=orch_name,
                    contract_value=None,
                    remediation="Regenerate contract from source"
                )
            )

        # Extra orchestrators (in contract but not source)
        extra = contract_orcks - source_orcks
        for orch_name in extra:
            report.issues.append(
                DriftIssue(
                    drift_type=DriftType.EXTRA_ORCHESTRATOR,
                    severity=DriftSeverity.HIGH,
                    path=f"orchestrators.{orch_name}",
                    description=f"Orchestrator '{orch_name}' in contract but not in source",
                    source_value=None,
                    contract_value=orch_name,
                    remediation="Remove from contract or add to source"
                )
            )

    def _compare_capabilities(
        self,
        source: Dict[str, Any],
        contract: Dict[str, Any],
        report: DriftReport
    ) -> None:
        """Compare orchestrator capabilities"""
        source_orcks = source.get("orchestrators", {})
        contract_orcks = contract.get("orchestrators", {})

        common_names = set(source_orcks.keys()) & set(contract_orcks.keys())

        for orch_name in common_names:
            source_caps = set(source_orcks[orch_name].get("capabilities", []))
            contract_caps = set(contract_orcks[orch_name].get("capabilities", []))

            if source_caps != contract_caps:
                report.issues.append(
                    DriftIssue(
                        drift_type=DriftType.MISMATCHED_CAPABILITY,
                        severity=DriftSeverity.MEDIUM,
                        path=f"orchestrators.{orch_name}.capabilities",
                        description=f"Capabilities mismatch for '{orch_name}'",
                        source_value=list(source_caps),
                        contract_value=list(contract_caps),
                        remediation="Sync capabilities from source to contract"
                    )
                )

    def _compare_dependencies(
        self,
        source: Dict[str, Any],
        contract: Dict[str, Any],
        report: DriftReport
    ) -> None:
        """Compare orchestrator dependencies"""
        source_orcks = source.get("orchestrators", {})
        contract_orcks = contract.get("orchestrators", {})

        common_names = set(source_orcks.keys()) & set(contract_orcks.keys())

        for orch_name in common_names:
            source_deps = set(source_orcks[orch_name].get("depends_on", []))
            contract_deps = set(contract_orcks[orch_name].get("depends_on", []))

            missing_deps = source_deps - contract_deps
            for dep in missing_deps:
                report.issues.append(
                    DriftIssue(
                        drift_type=DriftType.MISSING_DEPENDENCY,
                        severity=DriftSeverity.HIGH,
                        path=f"orchestrators.{orch_name}.depends_on",
                        description=f"Dependency '{dep}' missing from contract",
                        source_value=dep,
                        contract_value=None,
                        remediation="Add dependency to contract"
                    )
                )


# ============================================================================
# SYNC ENGINE
# ============================================================================


class ConfigSyncEngine:
    """Synchronize contract from source configuration"""

    def __init__(self, loader: ConfigurationLoader):
        """
        Initialize sync engine.

        Args:
            loader: Configuration loader instance
        """
        self.loader = loader
        self.logger = logging.getLogger(__name__)

    def sync_contract(self, dry_run: bool = False) -> bool:
        """
        Synchronize contract from source.

        Args:
            dry_run: If True, don't write changes

        Returns:
            True if sync successful, False otherwise
        """
        try:
            source_config = self.loader.load_source_config()
        except FileNotFoundError as e:
            self.logger.error(f"Cannot sync: {e}")
            return False

        contract_path = self.loader.workspace_root / "cortex" / "__wiring_contract__.yaml"

        if dry_run:
            self.logger.info(f"[DRY RUN] Would sync contract to: {contract_path}")
            return True

        # Write updated contract
        with open(contract_path, "w", encoding="utf-8") as f:
            yaml.dump(source_config, f, sort_keys=False, default_flow_style=False)

        self.logger.info(f"Synced contract from source: {contract_path}")
        return True


# ============================================================================
# GLOBAL INSTANCES
# ============================================================================

_config_loader: Optional[ConfigurationLoader] = None
_drift_detector: Optional[DriftDetector] = None
_sync_engine: Optional[ConfigSyncEngine] = None


def get_config_loader(workspace_root: Optional[Path] = None) -> ConfigurationLoader:
    """Get global configuration loader instance"""
    global _config_loader
    if _config_loader is None:
        _config_loader = ConfigurationLoader(workspace_root)
    return _config_loader


def get_drift_detector(workspace_root: Optional[Path] = None) -> DriftDetector:
    """Get global drift detector instance"""
    global _drift_detector
    if _drift_detector is None:
        loader = get_config_loader(workspace_root)
        _drift_detector = DriftDetector(loader)
    return _drift_detector


def get_sync_engine(workspace_root: Optional[Path] = None) -> ConfigSyncEngine:
    """Get global sync engine instance"""
    global _sync_engine
    if _sync_engine is None:
        loader = get_config_loader(workspace_root)
        _sync_engine = ConfigSyncEngine(loader)
    return _sync_engine


def reset_global_instances() -> None:
    """Reset all global instances (for testing)"""
    global _config_loader, _drift_detector, _sync_engine
    _config_loader = None
    _drift_detector = None
    _sync_engine = None
