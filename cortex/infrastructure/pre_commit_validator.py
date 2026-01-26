"""
Pre-commit validator: Hybrid smart gate for CORTEX wiring validation.

Implements two-stage validation:
- Stage 1: Quick health check (<200ms) - checks registry singleton initialization
- Stage 2: Full validation (triggered if Stage 1 fails) - validates all 23 orchestrators

CORE-026: Git checkpoint before major changes
CORE-027: Audit trail for all operations
CORE-030: Implementation Truth - verify code, not docs
"""

import sqlite3
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
            # Return defaults if config doesn't exist yet
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
    Logs all validation decisions to SQLite database.
    """
    
    def __init__(self, db_path: str = '.cortex/pre_commit_audit.log'):
        """Initialize audit logger with database"""
        self.db_path = db_path
        self._ensure_schema()
    
    def _ensure_schema(self) -> None:
        """Ensure audit log database and tables exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pre_commit_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                allow_commit BOOLEAN,
                validation_time_ms REAL,
                stage_executed TEXT,
                failure_reason TEXT,
                remediation_steps TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        conn.close()
    
    def log_decision(self, decision: HybridGateDecision) -> None:
        """Log a hybrid gate decision"""
        self.log_record({
            'event_type': 'PRE_COMMIT_DECISION',
            'timestamp': decision.decision_timestamp.isoformat(),
            'allow_commit': decision.allow_commit,
            'validation_time_ms': decision.validation_time_ms,
            'stage_executed': decision.stage_executed,
            'failure_reason': decision.failure_reason,
            'remediation_steps': ','.join(decision.remediation_steps) if decision.remediation_steps else '',
        })
    
    def log_health_check(self, result: HealthCheckResult) -> None:
        """Log a health check result"""
        self.log_record({
            'event_type': 'HEALTH_CHECK',
            'timestamp': result.check_timestamp.isoformat(),
            'details': f"healthy={result.is_healthy},total={result.orchestrators_count},wired={result.wired_count}",
        })
    
    def log_record(self, record: Dict[str, object]) -> None:
        """Log a generic audit record"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO pre_commit_audit (
                event_type, timestamp, allow_commit, validation_time_ms,
                stage_executed, failure_reason, remediation_steps, details
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            record.get('event_type', 'UNKNOWN'),
            record.get('timestamp', datetime.now().isoformat()),
            record.get('allow_commit'),
            record.get('validation_time_ms'),
            record.get('stage_executed'),
            record.get('failure_reason', ''),
            record.get('remediation_steps', ''),
            record.get('details', ''),
        ))
        
        conn.commit()
        conn.close()
    
    def get_recent_records(self, limit: int = 10) -> List[Dict[str, object]]:
        """Get recent audit records"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM pre_commit_audit 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        
        records = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return records


class PreCommitValidator:
    """
    Hybrid smart gate validator for pre-commit checks.
    
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
        Checks if DatabaseBackedRegistry is initialized and has all 23 wired.
        """
        # Check cache first
        if self._is_cache_valid():
            assert self._health_check_cache is not None
            return self._health_check_cache
        
        try:
            # Import registry
            from cortex.orchestrators import get_database_registry
            
            # Try to get registry instance
            try:
                _ = get_database_registry()
            except Exception as e:
                return HealthCheckResult(
                    is_healthy=False,
                    error_message=f"Registry not initialized: {str(e)}"
                )
            
            # Get stats
            stats = self.get_registry_stats()
            total = stats.get('total', 0)
            wired = stats.get('wired', 0)
            
            # Verify counts
            if total < self.config.expected_orchestrator_count:
                result = HealthCheckResult(
                    is_healthy=False,
                    orchestrators_count=total,
                    wired_count=wired,
                    error_message=f"Expected {self.config.expected_orchestrator_count} orchestrators, found {total}"
                )
                self.audit_logger.log_health_check(result)
                return result
            
            if wired < self.config.expected_orchestrator_count:
                result = HealthCheckResult(
                    is_healthy=False,
                    orchestrators_count=total,
                    wired_count=wired,
                    error_message=f"{total - wired} orchestrators not wired"
                )
                self.audit_logger.log_health_check(result)
                return result
            
            # All healthy
            result = HealthCheckResult(
                is_healthy=True,
                orchestrators_count=total,
                wired_count=wired
            )
            
            # Cache result
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
        """Get orchestrator registry statistics"""
        try:
            db_path = '.cortex/orchestrator_registry.db'
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT COUNT(*), SUM(wired) FROM orchestrators
            """)
            total, wired = cursor.fetchone()
            conn.close()
            
            return {'total': total or 0, 'wired': wired or 0}
        except Exception as e:
            logger.error(f"Failed to get registry stats: {e}")
            return {'total': 0, 'wired': 0}
    
    def full_wiring_validation(self) -> WiringValidationResult:
        """
        Stage 2: Full wiring validation.
        Comprehensive check of all orchestrators, schemas, and MCP adapters.
        """
        start_time = time.time()
        result = WiringValidationResult(is_valid=True)
        
        try:
            # Get all orchestrators
            orchestrators = self.get_all_orchestrators()
            result.total_orchestrators = len(orchestrators)
            result.wired_orchestrators = sum(1 for o in orchestrators if o.get('wired', 0))
            result.unwired_count = result.total_orchestrators - result.wired_orchestrators
            
            # Check for unwired orchestrators
            result.unwired_orchestrators = [o for o in orchestrators if not o.get('wired', 0)]
            if result.unwired_orchestrators:
                result.is_valid = False
                unwired_names = [str(o.get('name', 'Unknown')) for o in result.unwired_orchestrators]
                result.remediation_steps.append(
                    f"❌ Found {result.unwired_count} unwired orchestrators: "
                    f"{', '.join(unwired_names)}"
                )
                result.remediation_steps.append(
                    "→ Run: python -m cortex.scripts.phase_3_database_registry_init"
                )
            
            # Verify schema integrity
            result.schema_valid = self._verify_schema_integrity()
            result.schema_tables = self._get_schema_tables()
            if not result.schema_valid:
                result.is_valid = False
                result.remediation_steps.append(
                    "❌ Database schema mismatch detected"
                )
                result.remediation_steps.append(
                    "→ Run: python -c 'from cortex.orchestrators import initialize_registry; initialize_registry()'"
                )
            
            # Verify MCP adapter exposure
            result.mcp_adapters_exposed = self._verify_mcp_adapters()
            result.exposed_adapter_count = sum(
                1 for o in orchestrators 
                if self._has_mcp_adapter(str(o.get('name', 'Unknown')))
            )
            if not result.mcp_adapters_exposed:
                result.is_valid = False
                result.remediation_steps.append(
                    "❌ Not all MCP adapters are exposed"
                )
                result.remediation_steps.append(
                    "→ Verify: cortex/mcp/adapters/ has all 23 adapter files"
                )
            
            result.validation_time_ms = (time.time() - start_time) * 1000
            return result
            
        except Exception as e:
            result.is_valid = False
            result.remediation_steps.append(f"❌ Validation error: {str(e)}")
            result.validation_time_ms = (time.time() - start_time) * 1000
            return result
    
    def get_all_orchestrators(self) -> List[Dict[str, object]]:
        """Get all orchestrators from registry"""
        try:
            db_path = '.cortex/orchestrator_registry.db'
            conn = sqlite3.connect(db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT id, name, module_path, class_name, wired, category 
                FROM orchestrators 
                ORDER BY id
            """)
            
            orchestrators = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            return orchestrators
        except Exception as e:
            logger.error(f"Failed to get orchestrators: {e}")
            return []
    
    def _verify_schema_integrity(self) -> bool:
        """Verify database schema matches expected structure"""
        try:
            db_path = '.cortex/orchestrator_registry.db'
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check for required table
            cursor.execute("""
                SELECT name FROM sqlite_master 
                WHERE type='table' AND name='orchestrators'
            """)
            
            has_table = cursor.fetchone() is not None
            conn.close()
            
            return has_table
        except Exception as e:
            logger.error(f"Schema verification failed: {e}")
            return False
    
    def _get_schema_tables(self) -> List[str]:
        """Get list of tables in orchestrator registry"""
        try:
            db_path = '.cortex/orchestrator_registry.db'
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT name FROM sqlite_master WHERE type='table'
            """)
            
            tables = [row[0] for row in cursor.fetchall()]
            conn.close()
            
            return tables
        except Exception as e:
            logger.error(f"Failed to get tables: {e}")
            return []
    
    def _verify_mcp_adapters(self) -> bool:
        """Verify MCP adapters are exposed for all orchestrators"""
        try:
            mcp_adapters_dir = Path('cortex/mcp/adapters')
            if not mcp_adapters_dir.exists():
                return False
            
            # Count adapter files
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
        
        # Stage 1: Quick health check
        health_result = self.quick_health_check()
        
        if health_result.is_healthy:
            # Fast path: Allow commit immediately
            decision = HybridGateDecision(
                allow_commit=True,
                decision_type=DecisionType.FAST_PATH,
                validation_time_ms=(time.time() - start_time) * 1000,
                stage_executed="STAGE_1",
                full_validation_triggered=False,
            )
            self.audit_logger.log_decision(decision)
            return decision
        
        # Stage 1 failed, run Stage 2
        full_result = self.full_wiring_validation()
        
        if full_result.is_valid:
            # Fallback path: Stage 2 recovered
            decision = HybridGateDecision(
                allow_commit=True,
                decision_type=DecisionType.FALLBACK_PATH,
                validation_time_ms=(time.time() - start_time) * 1000,
                stage_executed="STAGE_1_2",
                full_validation_triggered=True,
            )
        else:
            # Both stages failed
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
