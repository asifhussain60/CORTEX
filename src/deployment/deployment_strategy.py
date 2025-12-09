"""
Deployment Strategy System

Implements progressive deployment strategies for safe production rollouts:
- Canary Deployment: Gradual rollout (10% → 50% → 100%) with validation
- Blue-Green Deployment: Zero-downtime environment switching
- Direct Deployment: Standard deployment without progressive stages

Features:
- Configurable deployment strategies
- Smoke test execution between stages
- Automatic rollback on failures
- Health monitoring during rollout
- Strategy recommendation engine
- State persistence for resume/rollback

Integration:
- Works with deploy orchestrator for strategy-aware deployments
- Uses deployment metrics for health tracking
- Integrates with rollback system for failure recovery
"""

import json
import logging
from dataclasses import dataclass, field, asdict
from datetime import datetime, timedelta
from enum import Enum
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
import yaml
import time

logger = logging.getLogger(__name__)


class StrategyType(Enum):
    """Deployment strategy types"""
    CANARY = "canary"
    BLUE_GREEN = "blue_green"
    DIRECT = "direct"


class StageStatus(Enum):
    """Stage execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class CanaryConfig:
    """Canary deployment configuration"""
    stages: List[int]  # Percentage rollout stages (e.g., [10, 50, 100])
    stage_duration_minutes: int = 5
    health_check_interval_seconds: int = 30
    smoke_tests_required: bool = True
    auto_rollback_on_failure: bool = True
    
    def __post_init__(self):
        """Validate canary configuration"""
        if not self.stages or self.stages[-1] != 100:
            raise ValueError("Canary stages must end with 100%")
        
        if self.stages != sorted(self.stages):
            raise ValueError("Canary stages must be in ascending order")
        
        if any(stage <= 0 or stage > 100 for stage in self.stages):
            raise ValueError("Stage percentages must be between 1 and 100")


@dataclass
class BlueGreenConfig:
    """Blue-green deployment configuration"""
    warmup_duration_minutes: int = 2
    smoke_tests_required: bool = True
    auto_switch_on_success: bool = True
    keep_old_environment_hours: int = 24
    monitor_duration_after_switch_minutes: int = 10


@dataclass
class DeploymentStage:
    """Individual deployment stage"""
    percentage: int
    status: StageStatus = StageStatus.PENDING
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    health_checks: List[Dict[str, Any]] = field(default_factory=list)
    smoke_test_result: Optional['SmokeTestResult'] = None


@dataclass
class SmokeTestResult:
    """Smoke test execution result"""
    stage_percentage: int
    passed: bool
    tests_run: int
    tests_passed: int
    tests_failed: int
    failure_reasons: List[str] = field(default_factory=list)
    executed_at: datetime = field(default_factory=datetime.now)


@dataclass
class StrategyConfig:
    """Base strategy configuration"""
    strategy_type: StrategyType
    canary: Optional[CanaryConfig] = None
    blue_green: Optional[BlueGreenConfig] = None
    smoke_tests: Dict[str, List[str]] = field(default_factory=dict)


@dataclass
class DeploymentStrategy:
    """Deployment strategy execution state"""
    strategy_type: StrategyType
    deployment_id: str
    config: Union[CanaryConfig, BlueGreenConfig, None] = None
    stages: List[DeploymentStage] = field(default_factory=list)
    current_stage_index: int = 0
    status: StageStatus = StageStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Initialize strategy based on type"""
        if self.strategy_type == StrategyType.CANARY and isinstance(self.config, CanaryConfig):
            self.stages = [
                DeploymentStage(percentage=pct) 
                for pct in self.config.stages
            ]
        elif self.strategy_type == StrategyType.BLUE_GREEN:
            # Blue-green has implicit stages: deploy green, validate, switch
            self.stages = [
                DeploymentStage(percentage=100)  # Single full deployment to green
            ]
            self.metadata['blue_environment'] = 'active'
            self.metadata['green_environment'] = 'deploying'
    
    def get_current_stage(self) -> Optional[DeploymentStage]:
        """Get current deployment stage"""
        if 0 <= self.current_stage_index < len(self.stages):
            return self.stages[self.current_stage_index]
        return None
    
    def advance_stage(self):
        """Advance to next deployment stage"""
        current = self.get_current_stage()
        if current:
            current.status = StageStatus.COMPLETED
            current.completed_at = datetime.now()
        
        self.current_stage_index += 1


class DeploymentStrategyManager:
    """Manages deployment strategy execution"""
    
    def __init__(self, workspace_root: str = None):
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        self.config_dir = self.workspace_root / "cortex-brain" / "config"
        self.strategy_states_dir = self.workspace_root / "cortex-brain" / "deployments" / "strategies"
        self.strategy_states_dir.mkdir(parents=True, exist_ok=True)
        
        self.default_config = self._load_default_config()
    
    def _load_default_config(self) -> Dict[str, Any]:
        """Load default strategy configuration"""
        config_path = self.config_dir / "deployment-strategies.yaml"
        
        if config_path.exists():
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        
        # Return built-in defaults
        return {
            'canary': {
                'stages': [10, 50, 100],
                'stage_duration_minutes': 5,
                'health_check_interval_seconds': 30,
                'smoke_tests_required': True,
                'auto_rollback_on_failure': True
            },
            'blue_green': {
                'warmup_duration_minutes': 2,
                'smoke_tests_required': True,
                'auto_switch_on_success': True,
                'keep_old_environment_hours': 24,
                'monitor_duration_after_switch_minutes': 10
            },
            'smoke_tests': {
                'standard': ['health_check', 'api_validation', 'database_connectivity'],
                'critical_features': ['tdd_workflow', 'planning_system', 'ado_operations'],
                'health_check': ['system_health', 'disk_space', 'memory_usage'],
                'api_validation': ['response_templates', 'agent_instantiation']
            }
        }
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return self.default_config
    
    def create_strategy(
        self,
        strategy_type: StrategyType,
        deployment_id: str,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> DeploymentStrategy:
        """Create deployment strategy"""
        if strategy_type == StrategyType.CANARY:
            config_dict = custom_config or self.default_config.get('canary', {})
            config = CanaryConfig(**config_dict)
        elif strategy_type == StrategyType.BLUE_GREEN:
            config_dict = custom_config or self.default_config.get('blue_green', {})
            config = BlueGreenConfig(**config_dict)
        else:
            config = None
        
        strategy = DeploymentStrategy(
            strategy_type=strategy_type,
            deployment_id=deployment_id,
            config=config
        )
        
        logger.info(f"Created {strategy_type.value} strategy for deployment {deployment_id}")
        return strategy
    
    def run_smoke_tests(
        self,
        strategy: DeploymentStrategy,
        stage_index: int = 0
    ) -> SmokeTestResult:
        """Run smoke tests for deployment stage"""
        stage = strategy.stages[stage_index] if stage_index < len(strategy.stages) else None
        percentage = stage.percentage if stage else 100
        
        logger.info(f"Running smoke tests for {percentage}% stage")
        
        # Execute smoke tests
        result = self._execute_smoke_tests(
            deployment_id=strategy.deployment_id,
            test_suite='standard',
            stage_percentage=percentage
        )
        
        if stage:
            stage.smoke_test_result = result
        
        return result
    
    def _execute_smoke_tests(
        self,
        deployment_id: str,
        test_suite: str = 'standard',
        stage_percentage: int = 100
    ) -> SmokeTestResult:
        """Execute smoke tests (to be implemented with actual test execution)"""
        # Placeholder - actual implementation would run real smoke tests
        tests = self.default_config.get('smoke_tests', {}).get(test_suite, [])
        tests_run = len(tests) if tests else 5
        
        return SmokeTestResult(
            stage_percentage=stage_percentage,
            passed=True,
            tests_run=tests_run,
            tests_passed=tests_run,
            tests_failed=0
        )
    
    def execute_canary_stage(
        self,
        strategy: DeploymentStrategy,
        stage_index: int
    ) -> Dict[str, Any]:
        """Execute single canary deployment stage"""
        if stage_index >= len(strategy.stages):
            return {'success': False, 'reason': 'invalid_stage_index'}
        
        stage = strategy.stages[stage_index]
        stage.status = StageStatus.IN_PROGRESS
        stage.started_at = datetime.now()
        
        logger.info(f"Executing canary stage {stage_index + 1}/{len(strategy.stages)} ({stage.percentage}%)")
        
        # Run smoke tests if required
        if isinstance(strategy.config, CanaryConfig) and strategy.config.smoke_tests_required:
            smoke_result = self.run_smoke_tests(strategy, stage_index)
            
            if not smoke_result.passed:
                if strategy.config.auto_rollback_on_failure:
                    logger.warning(f"Smoke tests failed at {stage.percentage}% - triggering rollback")
                    stage.status = StageStatus.FAILED
                    return {
                        'success': False,
                        'rollback_triggered': True,
                        'reason': 'smoke_test_failure',
                        'failures': smoke_result.failure_reasons
                    }
        
        # Monitor health during stage duration
        if isinstance(strategy.config, CanaryConfig):
            health_checks = self.monitor_stage_health(
                strategy,
                stage_index,
                duration_minutes=strategy.config.stage_duration_minutes
            )
            stage.health_checks = health_checks
        
        stage.status = StageStatus.COMPLETED
        stage.completed_at = datetime.now()
        
        return {
            'success': True,
            'rollback_triggered': False,
            'stage_percentage': stage.percentage
        }
    
    def monitor_stage_health(
        self,
        strategy: DeploymentStrategy,
        stage_index: int,
        duration_minutes: int
    ) -> List[Dict[str, Any]]:
        """Monitor health during canary stage"""
        if not isinstance(strategy.config, CanaryConfig):
            return []
        
        health_checks = []
        interval_seconds = strategy.config.health_check_interval_seconds
        num_checks = max(1, (duration_minutes * 60) // interval_seconds)
        
        for i in range(num_checks):
            health_checks.append({
                'timestamp': datetime.now().isoformat(),
                'healthy': True,  # Placeholder - actual health check logic
                'check_number': i + 1
            })
        
        return health_checks
    
    def execute_canary_deployment(
        self,
        deployment_id: str,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute complete canary deployment"""
        strategy = self.create_strategy(
            StrategyType.CANARY,
            deployment_id,
            custom_config
        )
        
        stages_completed = 0
        
        for stage_idx in range(len(strategy.stages)):
            result = self.execute_canary_stage(strategy, stage_idx)
            
            if not result['success']:
                return {
                    'success': False,
                    'rollback_triggered': result.get('rollback_triggered', False),
                    'failed_at_stage': strategy.stages[stage_idx].percentage,
                    'stages_completed': stages_completed
                }
            
            stages_completed += 1
        
        return {
            'success': True,
            'stages_completed': stages_completed,
            'final_percentage': 100
        }
    
    def deploy_to_green_environment(
        self,
        strategy: DeploymentStrategy
    ) -> Dict[str, Any]:
        """Deploy to inactive (green) environment"""
        if strategy.strategy_type != StrategyType.BLUE_GREEN:
            return {'success': False, 'reason': 'not_blue_green_strategy'}
        
        logger.info("Deploying to green environment")
        
        # Placeholder - actual deployment logic
        strategy.metadata['green_environment'] = 'deployed'
        
        return {
            'success': True,
            'target_environment': 'green',
            'active_environment': 'blue'
        }
    
    def warmup_environment(
        self,
        strategy: DeploymentStrategy,
        environment: str,
        duration_minutes: int
    ) -> Dict[str, Any]:
        """Warm up environment before switching traffic"""
        logger.info(f"Warming up {environment} environment for {duration_minutes} minutes")
        
        # Placeholder - actual warmup logic (cache priming, connection pooling, etc.)
        return {
            'warmed_up': True,
            'environment': environment,
            'duration_minutes': duration_minutes
        }
    
    def run_smoke_tests_on_environment(
        self,
        strategy: DeploymentStrategy,
        environment: str
    ) -> SmokeTestResult:
        """Run smoke tests on specific environment"""
        logger.info(f"Running smoke tests on {environment} environment")
        
        return self._execute_smoke_tests(
            deployment_id=strategy.deployment_id,
            test_suite='standard'
        )
    
    def switch_active_environment(
        self,
        strategy: DeploymentStrategy,
        from_env: str,
        to_env: str
    ) -> Dict[str, Any]:
        """Switch active environment (traffic routing)"""
        logger.info(f"Switching traffic from {from_env} to {to_env}")
        
        switch_time = datetime.now()
        
        # Update strategy metadata
        strategy.metadata['blue_environment'] = 'inactive' if to_env == 'green' else 'active'
        strategy.metadata['green_environment'] = 'active' if to_env == 'green' else 'inactive'
        strategy.metadata['switch_time'] = switch_time.isoformat()
        
        return {
            'success': True,
            'old_active': from_env,
            'new_active': to_env,
            'switch_time': switch_time.isoformat()
        }
    
    def monitor_environment_health(
        self,
        environment: str,
        duration_minutes: int = 5
    ) -> Dict[str, Any]:
        """Monitor environment health after switch"""
        logger.info(f"Monitoring {environment} environment health")
        
        # Placeholder - actual health monitoring
        return {
            'healthy': True,
            'environment': environment,
            'monitored_duration_minutes': duration_minutes
        }
    
    def rollback_to_blue(
        self,
        strategy: DeploymentStrategy
    ) -> Dict[str, Any]:
        """Rollback to blue environment"""
        logger.warning("Rolling back to blue environment")
        
        # Switch traffic back to blue
        result = self.switch_active_environment(strategy, 'green', 'blue')
        
        return {
            'success': result['success'],
            'active_environment': 'blue',
            'rollback_time': datetime.now().isoformat()
        }
    
    def cleanup_old_environment(
        self,
        strategy: DeploymentStrategy,
        environment: str,
        keep_hours: int
    ) -> Dict[str, Any]:
        """Schedule cleanup of old environment"""
        logger.info(f"Scheduling cleanup of {environment} environment after {keep_hours} hours")
        
        cleanup_after = datetime.now() + timedelta(hours=keep_hours)
        
        strategy.metadata[f'{environment}_cleanup_scheduled'] = cleanup_after.isoformat()
        
        return {
            'scheduled': True,
            'environment': environment,
            'cleanup_after_hours': keep_hours,
            'cleanup_time': cleanup_after.isoformat()
        }
    
    def execute_blue_green_deployment(
        self,
        deployment_id: str,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute complete blue-green deployment"""
        strategy = self.create_strategy(
            StrategyType.BLUE_GREEN,
            deployment_id,
            custom_config
        )
        
        # 1. Deploy to green environment
        deploy_result = self.deploy_to_green_environment(strategy)
        if not deploy_result['success']:
            return {'success': False, 'stage': 'deploy_green', 'reason': 'deployment_failed'}
        
        # 2. Warm up green environment
        if isinstance(strategy.config, BlueGreenConfig):
            warmup_result = self.warmup_environment(
                strategy,
                'green',
                strategy.config.warmup_duration_minutes
            )
        
        # 3. Run smoke tests on green
        smoke_result = self.run_smoke_tests_on_environment(strategy, 'green')
        if not smoke_result.passed:
            return {
                'success': False,
                'stage': 'smoke_tests',
                'reason': 'smoke_tests_failed',
                'failures': smoke_result.failure_reasons
            }
        
        # 4. Switch traffic to green
        switch_result = self.switch_active_environment(strategy, 'blue', 'green')
        if not switch_result['success']:
            return {'success': False, 'stage': 'switch', 'reason': 'switch_failed'}
        
        # 5. Monitor green environment health
        health = self.monitor_environment_health('green', duration_minutes=10)
        if not health['healthy']:
            # Rollback to blue
            self.rollback_to_blue(strategy)
            return {'success': False, 'stage': 'post_switch_monitoring', 'reason': 'health_degraded'}
        
        # 6. Schedule cleanup of blue environment
        if isinstance(strategy.config, BlueGreenConfig):
            self.cleanup_old_environment(
                strategy,
                'blue',
                strategy.config.keep_old_environment_hours
            )
        
        return {
            'success': True,
            'switched_to': 'green',
            'old_environment_cleanup_scheduled': True
        }
    
    def execute_strategy(
        self,
        strategy_type: StrategyType,
        deployment_id: str,
        validate_each_stage: bool = True,
        validate_switch: bool = True,
        custom_config: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute deployment strategy end-to-end"""
        start_time = datetime.now()
        
        if strategy_type == StrategyType.CANARY:
            result = self.execute_canary_deployment(deployment_id, custom_config)
            result['strategy_type'] = 'canary'
        elif strategy_type == StrategyType.BLUE_GREEN:
            result = self.execute_blue_green_deployment(deployment_id, custom_config)
            result['strategy_type'] = 'blue_green'
            result['environment_switched'] = result.get('success', False)
        else:
            result = {'success': True, 'strategy_type': 'direct'}
        
        end_time = datetime.now()
        result['total_duration_minutes'] = (end_time - start_time).total_seconds() / 60
        
        return result
    
    def save_strategy_state(
        self,
        strategy: DeploymentStrategy
    ) -> str:
        """Save strategy state to disk"""
        filename = f"{strategy.deployment_id}-strategy.json"
        filepath = self.strategy_states_dir / filename
        
        # Convert to dict (handling datetime serialization)
        state_dict = {
            'strategy_type': strategy.strategy_type.value,
            'deployment_id': strategy.deployment_id,
            'current_stage_index': strategy.current_stage_index,
            'status': strategy.status.value,
            'created_at': strategy.created_at.isoformat(),
            'metadata': strategy.metadata,
            'stages': [
                {
                    'percentage': stage.percentage,
                    'status': stage.status.value,
                    'started_at': stage.started_at.isoformat() if stage.started_at else None,
                    'completed_at': stage.completed_at.isoformat() if stage.completed_at else None
                }
                for stage in strategy.stages
            ]
        }
        
        with open(filepath, 'w') as f:
            json.dump(state_dict, f, indent=2)
        
        logger.info(f"Saved strategy state to {filepath}")
        return str(filepath)
    
    def load_strategy_state(
        self,
        deployment_id: str
    ) -> Optional[DeploymentStrategy]:
        """Load strategy state from disk"""
        filename = f"{deployment_id}-strategy.json"
        filepath = self.strategy_states_dir / filename
        
        if not filepath.exists():
            logger.warning(f"Strategy state not found: {filepath}")
            return None
        
        with open(filepath, 'r') as f:
            state_dict = json.load(f)
        
        # Reconstruct strategy
        strategy_type = StrategyType(state_dict['strategy_type'])
        
        strategy = DeploymentStrategy(
            strategy_type=strategy_type,
            deployment_id=state_dict['deployment_id'],
            current_stage_index=state_dict['current_stage_index'],
            status=StageStatus(state_dict['status']),
            created_at=datetime.fromisoformat(state_dict['created_at']),
            metadata=state_dict['metadata']
        )
        
        # Reconstruct stages
        strategy.stages = [
            DeploymentStage(
                percentage=stage_dict['percentage'],
                status=StageStatus(stage_dict['status']),
                started_at=datetime.fromisoformat(stage_dict['started_at']) if stage_dict['started_at'] else None,
                completed_at=datetime.fromisoformat(stage_dict['completed_at']) if stage_dict['completed_at'] else None
            )
            for stage_dict in state_dict['stages']
        ]
        
        logger.info(f"Loaded strategy state from {filepath}")
        return strategy
    
    def execute_smoke_tests(
        self,
        deployment_id: str,
        test_suite: str = 'standard'
    ) -> SmokeTestResult:
        """Execute smoke tests"""
        return self._execute_smoke_tests(deployment_id, test_suite, stage_percentage=100)


def load_strategy_config(config_path: str) -> StrategyConfig:
    """Load strategy configuration from YAML file"""
    with open(config_path, 'r') as f:
        config_dict = yaml.safe_load(f)
    
    strategy_type = StrategyType(config_dict.get('strategy_type', 'direct'))
    
    canary_config = None
    if 'canary' in config_dict:
        canary_config = CanaryConfig(**config_dict['canary'])
    
    blue_green_config = None
    if 'blue_green' in config_dict:
        blue_green_config = BlueGreenConfig(**config_dict['blue_green'])
    
    return StrategyConfig(
        strategy_type=strategy_type,
        canary=canary_config,
        blue_green=blue_green_config,
        smoke_tests=config_dict.get('smoke_tests', {})
    )


def recommend_strategy(
    deployment_size: str = 'medium',
    risk_level: str = 'medium',
    criticality: str = 'production',
    requires_zero_downtime: bool = False
) -> Dict[str, Any]:
    """Recommend deployment strategy based on deployment characteristics"""
    
    # Zero-downtime requirement → blue-green
    if requires_zero_downtime:
        return {
            'strategy': StrategyType.BLUE_GREEN,
            'reason': 'zero_downtime requirement - blue-green ensures no downtime during switch',
            'confidence': 0.95
        }
    
    # High risk or large deployment → canary
    if risk_level == 'high' or deployment_size == 'large':
        return {
            'strategy': StrategyType.CANARY,
            'reason': f'high_risk or large deployment - gradual rollout minimizes impact',
            'confidence': 0.90
        }
    
    # Production + medium risk → canary
    if criticality == 'production' and risk_level == 'medium':
        return {
            'strategy': StrategyType.CANARY,
            'reason': 'production environment with medium risk - progressive validation recommended',
            'confidence': 0.80
        }
    
    # Low risk or dev environment → direct
    return {
        'strategy': StrategyType.DIRECT,
        'reason': 'low_risk deployment - direct deployment sufficient',
        'confidence': 0.75
    }
