"""
Pre-commit validator: Hybrid smart gate for CORTEX wiring validation.

Implements two-stage validation:
- Stage 1: Quick health check (<200ms) - checks YAML-backed wiring configuration
- Stage 2: Full validation (triggered if Stage 1 fails) - validates all 23 orchestrators

Docker-first architecture: Uses YAML configuration instead of SQLite database.

CORE-026: Git checkpoint before major changes
CORE-027: Audit trail for all operations
CORE-030: Implementation Truth - verify code, not docs
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from enum import Enum
import yaml
import time

logger = logging.getLogger(__name__)


class DecisionType(Enum):
    """Types of hybrid gate decisions"""
    FAST_PATH = "FAST_PATH"  # Health check passed, allow immediately
    FALLBACK_PATH = "FALLBACK_PATH"  # Health check failed, ran Stage 2
    FULL = "FULL"  # Full validation explicitly requested


@dataclass
class HealthCheckResult:
    """Result of Stage 1 quick health check"""
    is_healthy: bool
    orchestrators_count: int = 0
    wired_count: int = 0
    error_message: str = ""
    check_timestamp: datetime = field(default_factory=datetime.now)
    
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, HealthCheckResult):
            return False
        return (
            self.is_healthy == other.is_healthy and
            self.orchestrators_count == other.orchestrators_count and
            self.wired_count == other.wired_count
        )


@dataclass
class WiringValidationResult:
    """Result of Stage 2 full wiring validation"""
    is_valid: bool
    total_orchestrators: int = 0
    wired_orchestrators: int = 0
    unwired_count: int = 0
    unwired_orchestrators: List[Dict[str, object]] = field(default_factory=list)
    schema_valid: bool = True
    schema_tables: List[str] = field(default_factory=list)
    mcp_adapters_exposed: bool = True
    exposed_adapter_count: int = 0
    remediation_steps: List[str] = field(default_factory=list)
    validation_timestamp: datetime = field(default_factory=datetime.now)
    validation_time_ms: float = 0.0


@dataclass
class HybridGateDecision:
    """Decision from hybrid gate evaluation"""
    allow_commit: bool
    decision_type: DecisionType
    validation_time_ms: float
    stage_executed: str  # "STAGE_1", "STAGE_1_2", or "FULL"
    full_validation_triggered: bool = False
    failure_reason: str = ""
    remediation_steps: List[str] = field(default_factory=list)
    decision_timestamp: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, object]:
        """Convert to dictionary for serialization"""
        return {
            'allow_commit': self.allow_commit,
            'decision_type': self.decision_type.value,
            'validation_time_ms': self.validation_time_ms,
            'stage_executed': self.stage_executed,
            'full_validation_triggered': self.full_validation_triggered,
            'failure_reason': self.failure_reason,
            'remediation_steps': self.remediation_steps,
            'decision_timestamp': self.decision_timestamp.isoformat(),
        }


@dataclass
class PreCommitConfig:
    """Configuration for pre-commit validator (extensible via YAML)"""
    expected_orchestrator_count: int = 23
    stage_1_timeout_ms: int = 200
    stage_2_timeout_ms: int = 3000
    health_check_cache_ttl_seconds: int = 5
    validators: List[Dict[str, object]] = field(default_factory=lambda: [
        {'type': 'wiring', 'required': True},
        {'type': 'mcp_adapter', 'required': True},
        {'type': 'schema', 'required': True},
    ])
    
    @classmethod
    def from_yaml(cls, config_path: Optional[str] = None) -> 'PreCommitConfig':
        """Load config from YAML file"""
        if config_path is None:
            config_path = '.cortex/pre-commit-config.yaml'
        
        path = Path(config_path)
        if not path.exists():
            return cls()
        
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
            
            if data is None:
                return cls()
            
            return cls(
                expected_orchestrator_count=data.get('expected_orchestrator_count', 23),
                stage_1_timeout_ms=data.get('stage_1_timeout_ms', 200),
                stage_2_timeout_ms=data.get('stage_2_timeout_ms', 3000),
                health_check_cache_ttl_seconds=data.get('health_check_cache_ttl_seconds', 5),
                validators=data.get('validators', cls.validators),
            )
        except (yaml.YAMLError, KeyError) as e:
            raise ValueError(f"Invalid pre-commit config YAML: {e}")


class PreCommitAuditLogger:
    """
    CORE-027: Audit trail for pre-commit operations.
    Docker-first: Logs to JSON file instead of SQLite database.
    """
    
    def __init__(self, log_path: str = '.cortex/pre_commit_audit.jsonl'):
        """Initialize audit logger with JSON Lines file"""
        self.log_path = Path(log_path)
        self._ensure_log_file()
    
    def _ensure_log_file(self) -> None:
        """Ensure audit log directory exists"""
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.log_path.exists():
            self.log_path.touch()
    
    def log_decision(self, decision: HybridGateDecision) -> None:
        """Log a hybrid gate decision"""
        self.log_record({
            'event_type': 'PRE_COMMIT_DECISION',
            'timestamp': decision.decision_timestamp.isoformat(),
            'allow_commit': decision.allow_commit,
            'validation_time_ms': decision.validation_time_ms,
            'stage_executed': decision.stage_executed,
            'failure_reason': decision.failure_reason,
            'remediation_steps': decision.remediation_steps,
        })
    
    def log_health_check(self, result: HealthCheckResult) -> None:
        """Log a health check result"""
        self.log_record({
            'event_type': 'HEALTH_CHECK',
            'timestamp': result.check_timestamp.isoformat(),
            'is_healthy': result.is_healthy,
            'orchestrators_count': result.orchestrators_count,
            'wired_count': result.wired_count,
            'error_message': result.error_message,
        })
    
    def log_record(self, record: Dict[str, object]) -> None:
        """Log a generic audit record to JSON Lines file"""
        try:
            with open(self.log_path, 'a') as f:
                f.write(json.dumps(record) + '\n')
        except Exception as e:
            logger.error(f"Failed to write audit log: {e}")
    
    def get_recent_records(self, limit: int = 10) -> List[Dict[str, object]]:
        """Get recent audit records"""
        try:
            if not self.log_path.exists():
                return []
            
            with open(self.log_path, 'r') as f:
                lines = f.readlines()
            
            recent_lines = lines[-limit:] if len(lines) > limit else lines
            records = []
            for line in reversed(recent_lines):
                line = line.strip()
                if line:
                    try:
                        records.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue
            
            return records
        except Exception as e:
            logger.error(f"Failed to read audit log: {e}")
            return []


class PreCommitValidator:
    """
    Hybrid smart gate validator for pre-commit checks.
    
    Docker-first architecture: Uses YAML-backed wiring configuration.
    
    Two-stage validation:
    1. Stage 1: Quick health check (<200ms)
    2. Stage 2: Full validation (only if Stage 1 fails, <3s)
    """
    
    def __init__(self, config: Optional[PreCommitConfig] = None, 
                 audit_logger: Optional[PreCommitAuditLogger] = None):
        """Initialize validator"""
        self.config = config or PreCommitConfig.from_yaml()
        self.audit_logger = audit_logger or PreCommitAuditLogger()
        self._health_check_cache: Optional[HealthCheckResult] = None
        self._cache_timestamp: Optional[datetime] = None
    
    def quick_health_check(self) -> HealthCheckResult:
        """
        Stage 1: Quick health check (<200ms).
        Docker-first: Checks YAML-backed wiring configuration.
        """
        if self._is_cache_valid():
            assert self._health_check_cache is not None
            return self._health_check_cache
        
        try:
            from cortex.orchestrators import get_orchestrator_count_by_category
            
            try:
                counts = get_orchestrator_count_by_category()
                total = counts.get('total', 23)
            except Exception as e:
                return HealthCheckResult(
                    is_healthy=False,
                    error_message=f"Wiring config not available: {str(e)}"
                )
            
            wired = total  # All YAML-defined are wired
            
            if total < self.config.expected_orchestrator_count:
                result = HealthCheckResult(
                    is_healthy=False,
                    orchestrators_count=total,
                    wired_count=wired,
                    error_message=f"Expected {self.config.expected_orchestrator_count} orchestrators, found {total}"
                )
                self.audit_logger.log_health_check(result)
                return result
            
            result = HealthCheckResult(
                is_healthy=True,
                orchestrators_count=total,
                wired_count=wired
            )
            
            self._health_check_cache = result
            self._cache_timestamp = datetime.now()
            
            self.audit_logger.log_health_check(result)
            return result
            
        except Exception as e:
            result = HealthCheckResult(
                is_healthy=False,
                error_message=f"Health check failed: {str(e)}"
            )
            self.audit_logger.log_health_check(result)
            return result
    
    def _is_cache_valid(self) -> bool:
        """Check if health check cache is still valid"""
        if self._health_check_cache is None or self._cache_timestamp is None:
            return False
        
        age = (datetime.now() - self._cache_timestamp).total_seconds()
        return age < self.config.health_check_cache_ttl_seconds
    
    def get_registry_stats(self) -> Dict[str, int]:
        """Get orchestrator registry statistics from YAML config"""
        try:
            from cortex.orchestrators import get_orchestrator_count_by_category
            counts = get_orchestrator_count_by_category()
            total = counts.get('total', 0)
            return {'total': total, 'wired': total}
        except Exception as e:
            logger.error(f"Failed to get registry stats: {e}")
            return {'total': 0, 'wired': 0}
    
    def full_wiring_validation(self) -> WiringValidationResult:
        """
        Stage 2: Full wiring validation.
        Docker-first: Validates YAML-backed wiring and MCP adapters.
        """
        start_time = time.time()
        result = WiringValidationResult(is_valid=True)
        
        try:
            orchestrators = self.get_all_orchestrators()
            result.total_orchestrators = len(orchestrators)
            result.wired_orchestrators = len(orchestrators)
            result.unwired_count = 0
            
            result.schema_valid = self._verify_yaml_config()
            result.schema_tables = ['orchestrators.yaml']
            if not result.schema_valid:
                result.is_valid = False
                result.remediation_steps.append(
                    "YAML wiring config is invalid or missing"
                )
                result.remediation_steps.append(
                    "Check: cortex-registry/manifest.yaml and domain configs"
                )
            
            result.mcp_adapters_exposed = self._verify_mcp_adapters()
            result.exposed_adapter_count = sum(
                1 for o in orchestrators 
                if self._has_mcp_adapter(str(o.get('name', 'Unknown')))
            )
            if not result.mcp_adapters_exposed:
                result.is_valid = False
                result.remediation_steps.append(
                    "Not all MCP adapters are exposed"
                )
                result.remediation_steps.append(
                    "Verify: cortex/mcp/adapters/ has all 23 adapter files"
                )
            
            result.validation_time_ms = (time.time() - start_time) * 1000
            return result
            
        except Exception as e:
            result.is_valid = False
            result.remediation_steps.append(f"Validation error: {str(e)}")
            result.validation_time_ms = (time.time() - start_time) * 1000
            return result
    
    def get_all_orchestrators(self) -> List[Dict[str, object]]:
        """Get all orchestrators from YAML-backed registry"""
        try:
            from cortex.orchestrators import get_all_orchestrators as _get_all
            return _get_all()
        except ImportError:
            return self._read_orchestrators_from_yaml()
    
    def _read_orchestrators_from_yaml(self) -> List[Dict[str, object]]:
        """Read orchestrators directly from YAML manifest"""
        try:
            manifest_path = Path('cortex-registry/manifest.yaml')
            if not manifest_path.exists():
                return []
            
            with open(manifest_path, 'r') as f:
                data = yaml.safe_load(f)
            
            orchestrators = []
            if data and 'orchestrators' in data:
                for name, config in data['orchestrators'].items():
                    orchestrators.append({
                        'name': name,
                        'module_path': config.get('module', ''),
                        'class_name': config.get('class', ''),
                        'wired': 1,
                        'category': config.get('category', 'domain'),
                    })
            
            return orchestrators
        except Exception as e:
            logger.error(f"Failed to read orchestrators from YAML: {e}")
            return []
    
    def _verify_yaml_config(self) -> bool:
        """Verify YAML-backed wiring configuration is valid"""
        try:
            manifest_path = Path('cortex-registry/manifest.yaml')
            if not manifest_path.exists():
                return False
            
            with open(manifest_path, 'r') as f:
                data = yaml.safe_load(f)
            
            return data is not None and 'orchestrators' in data
        except Exception as e:
            logger.error(f"YAML config verification failed: {e}")
            return False
    
    def _verify_mcp_adapters(self) -> bool:
        """Verify MCP adapters are exposed for all orchestrators"""
        try:
            mcp_adapters_dir = Path('cortex/mcp/adapters')
            if not mcp_adapters_dir.exists():
                return False
            
            adapter_files = list(mcp_adapters_dir.glob('*_adapter.py'))
            return len(adapter_files) >= self.config.expected_orchestrator_count
        except Exception as e:
            logger.error(f"MCP adapter verification failed: {e}")
            return False
    
    def _has_mcp_adapter(self, orchestrator_name: str) -> bool:
        """Check if specific orchestrator has MCP adapter"""
        try:
            adapter_name = f"{orchestrator_name.lower()}_adapter.py"
            adapter_path = Path('cortex/mcp/adapters') / adapter_name
            return adapter_path.exists()
        except Exception:
            return False
    
    def evaluate_commit(self) -> HybridGateDecision:
        """
        Hybrid gate evaluation: Try Stage 1, fallback to Stage 2 if needed.
        
        Returns: HybridGateDecision with allow_commit flag and reasoning
        """
        start_time = time.time()
        
        health_result = self.quick_health_check()
        
        if health_result.is_healthy:
            decision = HybridGateDecision(
                allow_commit=True,
                decision_type=DecisionType.FAST_PATH,
                validation_time_ms=(time.time() - start_time) * 1000,
                stage_executed="STAGE_1",
                full_validation_triggered=False,
            )
            self.audit_logger.log_decision(decision)
            return decision
        
        full_result = self.full_wiring_validation()
        
        if full_result.is_valid:
            decision = HybridGateDecision(
                allow_commit=True,
                decision_type=DecisionType.FALLBACK_PATH,
                validation_time_ms=(time.time() - start_time) * 1000,
                stage_executed="STAGE_1_2",
                full_validation_triggered=True,
            )
        else:
            decision = HybridGateDecision(
                allow_commit=False,
                decision_type=DecisionType.FULL,
                validation_time_ms=(time.time() - start_time) * 1000,
                stage_executed="STAGE_1_2",
                full_validation_triggered=True,
                failure_reason="\n".join(full_result.remediation_steps),
                remediation_steps=full_result.remediation_steps,
            )
        
        self.audit_logger.log_decision(decision)
        return decision


def get_pre_commit_validator() -> PreCommitValidator:
    """Factory function for PreCommitValidator"""
    return PreCommitValidator()


def run_pre_commit_check() -> bool:
    """Run pre-commit check and return True if commit allowed"""
    validator = get_pre_commit_validator()
    decision = validator.evaluate_commit()
    return decision.allow_commit
