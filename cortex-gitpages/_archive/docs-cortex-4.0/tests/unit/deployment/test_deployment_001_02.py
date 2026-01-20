"""
Tests for AC-DEPLOY-001-02: Blue-Green Deployment Setup

Tests blue-green deployment for zero-downtime updates, traffic switching, and rollback.
"""
import pytest
from src.deployment.blue_green import (
    BlueGreenDeploymentManager, 
    Deployment, 
    DeploymentSlot, 
    DeploymentStatus,
    DeploymentConfig
)
from datetime import datetime


# Test Cases

class TestDeploymentStructure:
    """Test deployment structure and initialization."""
    
    def test_deployment_creation(self):
        """Test creating deployment."""
        now = datetime.now()
        deployment = Deployment(
            slot=DeploymentSlot.GREEN,
            version="1.0.0",
            status=DeploymentStatus.PENDING,
            started_at=now
        )
        assert deployment.slot == DeploymentSlot.GREEN
        assert deployment.version == "1.0.0"
        assert deployment.status == DeploymentStatus.PENDING
    
    def test_deployment_duration(self):
        """Test deployment duration calculation."""
        from datetime import timedelta
        now = datetime.now()
        deployment = Deployment(
            slot=DeploymentSlot.BLUE,
            version="1.0.0",
            status=DeploymentStatus.COMPLETED,
            started_at=now,
            completed_at=now + timedelta(seconds=30)
        )
        assert deployment.get_duration() == 30


class TestBlueGreenDeploymentManager:
    """Test blue-green deployment manager."""
    
    def test_manager_initialization(self):
        """Test manager initialization."""
        config = DeploymentConfig(health_check_endpoint="/health")
        manager = BlueGreenDeploymentManager(config)
        assert manager.active_slot == DeploymentSlot.BLUE
        assert manager.standby_slot == DeploymentSlot.GREEN
    
    def test_start_deployment(self):
        """Test starting deployment."""
        config = DeploymentConfig(health_check_endpoint="/health")
        manager = BlueGreenDeploymentManager(config)
        deployment = manager.start_deployment("1.0.0")
        assert deployment.slot == DeploymentSlot.GREEN
        assert deployment.status == DeploymentStatus.PENDING
        assert deployment.version == "1.0.0"
    
    def test_execute_deployment_success(self):
        """Test successful deployment execution."""
        config = DeploymentConfig(
            health_check_endpoint="/health",
            pre_deployment_checks=[lambda: True],
            post_deployment_checks=[lambda: True]
        )
        manager = BlueGreenDeploymentManager(config)
        deployment = manager.start_deployment("1.0.0")
        result = manager.execute_deployment(deployment)
        assert result is True
        assert deployment.status == DeploymentStatus.COMPLETED
    
    def test_execute_deployment_pre_check_failure(self):
        """Test deployment failure on pre-check."""
        config = DeploymentConfig(
            health_check_endpoint="/health",
            pre_deployment_checks=[lambda: False]
        )
        manager = BlueGreenDeploymentManager(config)
        deployment = manager.start_deployment("1.0.0")
        result = manager.execute_deployment(deployment)
        assert result is False
        assert deployment.status == DeploymentStatus.FAILED
        assert "Pre-deployment check failed" in deployment.error_message
    
    def test_execute_deployment_post_check_failure(self):
        """Test deployment failure on post-check."""
        config = DeploymentConfig(
            health_check_endpoint="/health",
            pre_deployment_checks=[lambda: True],
            post_deployment_checks=[lambda: False]
        )
        manager = BlueGreenDeploymentManager(config)
        deployment = manager.start_deployment("1.0.0")
        result = manager.execute_deployment(deployment)
        assert result is False
        assert deployment.status == DeploymentStatus.FAILED


class TestTrafficSwitching:
    """Test traffic switching."""
    
    def test_switch_traffic_success(self):
        """Test successful traffic switch."""
        config = DeploymentConfig(
            health_check_endpoint="/health",
            pre_deployment_checks=[lambda: True],
            post_deployment_checks=[lambda: True]
        )
        manager = BlueGreenDeploymentManager(config)
        assert manager.active_slot == DeploymentSlot.BLUE
        
        deployment = manager.start_deployment("1.0.0")
        manager.execute_deployment(deployment)
        result = manager.switch_traffic(deployment)
        
        assert result is True
        assert manager.active_slot == DeploymentSlot.GREEN
        assert manager.standby_slot == DeploymentSlot.BLUE
    
    def test_switch_traffic_incomplete_deployment(self):
        """Test traffic switch with incomplete deployment."""
        config = DeploymentConfig(health_check_endpoint="/health")
        manager = BlueGreenDeploymentManager(config)
        
        deployment = manager.start_deployment("1.0.0")
        result = manager.switch_traffic(deployment)
        assert result is False
    
    def test_active_deployment_after_switch(self):
        """Test getting active deployment after switch."""
        config = DeploymentConfig(
            health_check_endpoint="/health",
            pre_deployment_checks=[lambda: True],
            post_deployment_checks=[lambda: True]
        )
        manager = BlueGreenDeploymentManager(config)
        
        deployment = manager.start_deployment("2.0.0")
        manager.execute_deployment(deployment)
        manager.switch_traffic(deployment)
        
        active = manager.get_active_deployment()
        assert active.slot == DeploymentSlot.GREEN
        assert active.version == "2.0.0"


class TestRollback:
    """Test rollback functionality."""
    
    def test_rollback_success(self):
        """Test successful rollback."""
        config = DeploymentConfig(
            health_check_endpoint="/health",
            pre_deployment_checks=[lambda: True],
            post_deployment_checks=[lambda: True],
            rollback_enabled=True
        )
        manager = BlueGreenDeploymentManager(config)
        
        deployment = manager.start_deployment("1.0.0")
        manager.execute_deployment(deployment)
        manager.switch_traffic(deployment)
        
        assert manager.active_slot == DeploymentSlot.GREEN
        result = manager.rollback()
        assert result is True
        assert manager.active_slot == DeploymentSlot.BLUE
    
    def test_rollback_disabled(self):
        """Test rollback when disabled."""
        config = DeploymentConfig(
            health_check_endpoint="/health",
            rollback_enabled=False
        )
        manager = BlueGreenDeploymentManager(config)
        result = manager.rollback()
        assert result is False
    
    def test_rollback_status_marked(self):
        """Test rollback status is marked."""
        config = DeploymentConfig(
            health_check_endpoint="/health",
            pre_deployment_checks=[lambda: True],
            post_deployment_checks=[lambda: True],
            rollback_enabled=True
        )
        manager = BlueGreenDeploymentManager(config)
        
        deployment = manager.start_deployment("1.0.0")
        manager.execute_deployment(deployment)
        manager.switch_traffic(deployment)
        
        # Get the previous deployment (which is now in standby)
        previous_deployment = manager.get_standby_deployment()
        manager.rollback()
        
        # After rollback, the previous deployment status should be ROLLED_BACK
        assert previous_deployment.status == DeploymentStatus.ROLLED_BACK


class TestDeploymentSlots:
    """Test deployment slot management."""
    
    def test_slot_swap_on_switch(self):
        """Test slots swap on traffic switch."""
        config = DeploymentConfig(
            health_check_endpoint="/health",
            pre_deployment_checks=[lambda: True],
            post_deployment_checks=[lambda: True]
        )
        manager = BlueGreenDeploymentManager(config)
        
        original_active = manager.active_slot
        original_standby = manager.standby_slot
        
        deployment = manager.start_deployment("1.0.0")
        manager.execute_deployment(deployment)
        manager.switch_traffic(deployment)
        
        assert manager.active_slot == original_standby
        assert manager.standby_slot == original_active
    
    def test_multiple_deployments(self):
        """Test multiple deployments."""
        config = DeploymentConfig(
            health_check_endpoint="/health",
            pre_deployment_checks=[lambda: True],
            post_deployment_checks=[lambda: True]
        )
        manager = BlueGreenDeploymentManager(config)
        
        # First deployment
        dep1 = manager.start_deployment("1.0.0")
        manager.execute_deployment(dep1)
        manager.switch_traffic(dep1)
        
        # Second deployment
        dep2 = manager.start_deployment("2.0.0")
        manager.execute_deployment(dep2)
        manager.switch_traffic(dep2)
        
        active = manager.get_active_deployment()
        assert active.version == "2.0.0"


class TestDeploymentConfig:
    """Test deployment configuration."""
    
    def test_config_creation(self):
        """Test creating deployment config."""
        config = DeploymentConfig(
            health_check_endpoint="/health",
            max_deployment_time=600,
            traffic_switch_timeout=120
        )
        assert config.health_check_endpoint == "/health"
        assert config.max_deployment_time == 600
        assert config.traffic_switch_timeout == 120
    
    def test_config_defaults(self):
        """Test deployment config defaults."""
        config = DeploymentConfig(health_check_endpoint="/health")
        assert config.max_deployment_time == 300
        assert config.traffic_switch_timeout == 60
        assert config.rollback_enabled is True


class TestDeploymentStatuses:
    """Test deployment statuses."""
    
    def test_status_transitions(self):
        """Test deployment status transitions."""
        now = datetime.now()
        deployment = Deployment(
            slot=DeploymentSlot.BLUE,
            version="1.0.0",
            status=DeploymentStatus.PENDING,
            started_at=now
        )
        assert deployment.status == DeploymentStatus.PENDING
        
        deployment.status = DeploymentStatus.IN_PROGRESS
        assert deployment.status == DeploymentStatus.IN_PROGRESS
        
        deployment.status = DeploymentStatus.COMPLETED
        assert deployment.status == DeploymentStatus.COMPLETED
    
    def test_all_deployment_statuses(self):
        """Test all deployment status values."""
        assert DeploymentStatus.PENDING.value == "pending"
        assert DeploymentStatus.IN_PROGRESS.value == "in_progress"
        assert DeploymentStatus.COMPLETED.value == "completed"
        assert DeploymentStatus.FAILED.value == "failed"
        assert DeploymentStatus.ROLLED_BACK.value == "rolled_back"
