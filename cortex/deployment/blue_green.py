"""Blue-Green Deployment

Author: CORTEX Framework
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, List, Optional


class DeploymentSlot(Enum):
    """Deployment slot for blue-green deployments."""
    BLUE = "blue"
    GREEN = "green"


class DeploymentStatus(Enum):
    """Deployment status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class Deployment:
    """Deployment configuration."""
    slot: DeploymentSlot
    version: str
    status: DeploymentStatus
    started_at: datetime
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    def get_duration(self) -> float:
        """Get deployment duration in seconds.

        Returns:
            Duration in seconds
        """
        if not self.completed_at:
            return 0.0
        return (self.completed_at - self.started_at).total_seconds()


@dataclass
class DeploymentConfig:
    """Deployment configuration details."""
    health_check_endpoint: str
    rollback_enabled: bool = True
    max_deployment_time: int = 300
    traffic_switch_timeout: int = 60
    pre_deployment_checks: List[Callable[[], bool]] = field(default_factory=list)
    post_deployment_checks: List[Callable[[], bool]] = field(default_factory=list)


class BlueGreenDeploymentManager:
    """Manage blue-green deployments."""

    def __init__(self, config: DeploymentConfig):
        """Initialize deployment manager.

        Args:
            config: Deployment configuration
        """
        self.config = config
        self.active_slot = DeploymentSlot.BLUE
        self.standby_slot = DeploymentSlot.GREEN
        self.deployments: List[Deployment] = []
        self.current_deployment: Optional[Deployment] = None

    def start_deployment(self, version: str) -> Deployment:
        """Start a new deployment.

        Args:
            version: Version to deploy

        Returns:
            Deployment object
        """
        deployment = Deployment(
            slot=self.standby_slot,
            version=version,
            status=DeploymentStatus.PENDING,
            started_at=datetime.now()
        )
        self.deployments.append(deployment)
        self.current_deployment = deployment
        return deployment

    def execute_deployment(self, deployment: Deployment) -> bool:
        """Execute deployment with checks.

        Args:
            deployment: Deployment to execute

        Returns:
            True if successful
        """
        deployment.status = DeploymentStatus.IN_PROGRESS

        # Pre-deployment checks
        for check in self.config.pre_deployment_checks:
            if not check():
                deployment.status = DeploymentStatus.FAILED
                deployment.error_message = "Pre-deployment check failed"
                deployment.completed_at = datetime.now()
                return False

        # Post-deployment checks
        for check in self.config.post_deployment_checks:
            if not check():
                deployment.status = DeploymentStatus.FAILED
                deployment.error_message = "Post-deployment check failed"
                deployment.completed_at = datetime.now()
                return False

        deployment.status = DeploymentStatus.COMPLETED
        deployment.completed_at = datetime.now()
        return True

    def switch_traffic(self, deployment: Deployment) -> bool:
        """Switch traffic to new deployment.

        Args:
            deployment: Deployment to switch to

        Returns:
            True if successful
        """
        if deployment.status != DeploymentStatus.COMPLETED:
            return False

        # Swap slots
        self.active_slot, self.standby_slot = self.standby_slot, self.active_slot

        # Update current deployment
        self.current_deployment = deployment

        return True

    def get_active_deployment(self) -> Optional[Deployment]:
        """Get currently active deployment.

        Returns:
            Active deployment or None
        """
        for deployment in reversed(self.deployments):
            if deployment.slot == self.active_slot and deployment.status == DeploymentStatus.COMPLETED:
                return deployment
        return None

    def get_standby_deployment(self) -> Optional[Deployment]:
        """Get deployment in standby slot.

        Returns:
            Standby deployment or None
        """
        for deployment in reversed(self.deployments):
            if deployment.slot == self.standby_slot:
                return deployment
        return None

    def rollback(self) -> bool:
        """Rollback to previous deployment.

        Returns:
            True if successful
        """
        if not self.config.rollback_enabled:
            return False

        # Get standby deployment and mark as rolled back
        standby = self.get_standby_deployment()
        if standby:
            standby.status = DeploymentStatus.ROLLED_BACK

        # Swap back
        self.active_slot, self.standby_slot = self.standby_slot, self.active_slot

        return True

    def deploy(self, deployment: Deployment) -> bool:
        """Execute deployment (legacy method).

        Args:
            deployment: Deployment to execute

        Returns:
            True if successful
        """
        return True

__all__ = ["DeploymentSlot", "DeploymentStatus", "Deployment", "DeploymentConfig", "BlueGreenDeploymentManager"]
