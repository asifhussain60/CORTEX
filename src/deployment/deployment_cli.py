"""
Deployment Orchestrator CLI

Unified command-line interface for CORTEX deployment operations.

Commands:
- deploy: Execute deployment with strategy selection
- validate-gates: Run pre-deployment gate validation
- rollback: Rollback to previous deployment or phase
- status: Show current deployment status
- history: View deployment history
- metrics: Display deployment analytics

Features:
- Strategy selection (canary, blue-green, direct)
- Dry-run mode for validation
- Admin-only operations (skip-gates)
- Checkpoint resume
- Rich output formatting
- Integration with all deployment components

Usage:
    python -m src.deployment.deployment_cli deploy --strategy canary
    python -m src.deployment.deployment_cli validate-gates
    python -m src.deployment.deployment_cli rollback --phase BUILD
    python -m src.deployment.deployment_cli status
    python -m src.deployment.deployment_cli history --limit 20
    python -m src.deployment.deployment_cli metrics --days 7
"""

import argparse
import json
import logging
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Any, List, Optional

from src.orchestrators.deploy_orchestrator import DeployOrchestrator
from src.deployment.gate_validator import GateValidator
from src.deployment.deployment_rollback import DeploymentRollbackManager
from src.deployment.deployment_metrics import DeploymentMetricsCollector
from src.deployment.deployment_strategy import (
    DeploymentStrategyManager,
    StrategyType,
    recommend_strategy
)

logger = logging.getLogger(__name__)


class DeploymentCLI:
    """Deployment CLI interface"""
    
    def __init__(self, workspace_root: str = None, is_admin: bool = False):
        self.workspace_root = Path(workspace_root) if workspace_root else Path.cwd()
        self.is_admin = is_admin
        
        # Initialize components
        self.orchestrator = DeployOrchestrator(str(self.workspace_root))
        self.gate_validator = GateValidator(str(self.workspace_root))
        self.rollback_manager = DeploymentRollbackManager(str(self.workspace_root))
        self.metrics_collector = DeploymentMetricsCollector(str(self.workspace_root))
        self.strategy_manager = DeploymentStrategyManager(str(self.workspace_root))
    
    def deploy(
        self,
        strategy: Optional[str] = None,
        dry_run: bool = False,
        skip_gates: bool = False,
        checkpoint_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute deployment"""
        try:
            # Check admin privileges for skip-gates
            if skip_gates and not self.is_admin:
                raise PermissionError("Admin privileges required for --skip-gates")
            
            # Dry-run mode: validate without deploying
            if dry_run:
                logger.info("Running deployment validation (dry-run mode)")
                return self.orchestrator.validate_deployment()
            
            # Resume from checkpoint if specified
            if checkpoint_id:
                logger.info(f"Resuming deployment from checkpoint: {checkpoint_id}")
                return self.orchestrator.resume_from_checkpoint(checkpoint_id)
            
            # Execute deployment with strategy
            logger.info(f"Starting deployment with strategy: {strategy or 'default'}")
            return self.orchestrator.deploy(strategy=strategy, skip_gates=skip_gates)
            
        except Exception as e:
            logger.error(f"Deployment failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def validate_gates(self, category: Optional[str] = None) -> Dict[str, Any]:
        """Validate deployment gates"""
        try:
            if category:
                logger.info(f"Validating {category} gates")
                return self.gate_validator.validate_category(category)
            else:
                logger.info("Validating all gates")
                return self.gate_validator.validate_all_gates()
        except Exception as e:
            logger.error(f"Gate validation failed: {e}")
            return {'passed': False, 'error': str(e)}
    
    def rollback(self, phase: Optional[str] = None) -> Dict[str, Any]:
        """Rollback deployment"""
        try:
            if phase:
                logger.info(f"Rolling back to phase: {phase}")
                return self.rollback_manager.rollback_to_phase(phase)
            else:
                logger.info("Rolling back to latest snapshot")
                return self.rollback_manager.rollback_latest()
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
            return {'success': False, 'error': str(e)}
    
    def status(self) -> Dict[str, Any]:
        """Get current deployment status"""
        try:
            return self.orchestrator.get_status()
        except Exception as e:
            logger.error(f"Failed to get status: {e}")
            return {'error': str(e)}
    
    def history(
        self,
        limit: int = 10,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get deployment history"""
        try:
            return self.metrics_collector.get_deployment_history(
                limit=limit,
                status=status
            )
        except Exception as e:
            logger.error(f"Failed to get history: {e}")
            return []
    
    def metrics(self, days: int = 7) -> Dict[str, Any]:
        """Get deployment metrics"""
        try:
            return self.metrics_collector.generate_report(days=days)
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return {'error': str(e)}
    
    def get_health_score(self, days: int = 7) -> int:
        """Calculate deployment health score"""
        try:
            return self.metrics_collector.calculate_health_score(days=days)
        except Exception as e:
            logger.error(f"Failed to calculate health score: {e}")
            return 0
    
    def check_metrics_alerts(self, days: int = 7) -> List[Dict[str, Any]]:
        """Check for metrics-based alerts"""
        try:
            return self.metrics_collector.check_health_thresholds(days=days)
        except Exception as e:
            logger.error(f"Failed to check alerts: {e}")
            return []
    
    def format_output(self, result: Dict[str, Any], command: str) -> str:
        """Format command output for display"""
        if command == 'deploy':
            return self._format_deploy_output(result)
        elif command == 'validate-gates':
            return self._format_validation_output(result)
        elif command == 'rollback':
            return self._format_rollback_output(result)
        elif command == 'status':
            return self._format_status_output(result)
        elif command == 'metrics':
            return self._format_metrics_output(result)
        else:
            return json.dumps(result, indent=2)
    
    def _format_deploy_output(self, result: Dict[str, Any]) -> str:
        """Format deployment output"""
        if result.get('success'):
            output = [
                "=" * 60,
                "✅ DEPLOYMENT SUCCESSFUL",
                "=" * 60,
                f"Deployment ID: {result.get('deployment_id', 'N/A')}",
                f"Duration: {result.get('duration', 0)} seconds",
                f"Gates Passed: {result.get('gates_passed', 0)}",
            ]
            
            if 'strategy' in result:
                output.append(f"Strategy: {result['strategy']}")
            
            if 'stages_completed' in result:
                output.append(f"Stages Completed: {result['stages_completed']}")
            
            return "\n".join(output)
        else:
            output = [
                "=" * 60,
                "❌ DEPLOYMENT FAILED",
                "=" * 60,
                f"Error: {result.get('error', 'Unknown error')}"
            ]
            return "\n".join(output)
    
    def _format_validation_output(self, result: Dict[str, Any]) -> str:
        """Format validation output"""
        if result.get('passed'):
            output = [
                "✅ ALL GATES PASSED",
                f"Gates Passed: {result.get('gates_passed', 0)}/{result.get('gates_total', 0)}"
            ]
            return "\n".join(output)
        else:
            output = [
                "❌ GATE VALIDATION FAILED",
                f"Gates Passed: {result.get('gates_passed', 0)}/{result.get('gates_total', 0)}",
                f"Gates Failed: {result.get('gates_failed', 0)}",
                "",
                "Failures:"
            ]
            
            for failure in result.get('failures', []):
                output.append(f"  • {failure['gate']}: {failure['reason']}")
                if 'remediation' in failure:
                    output.append(f"    Remediation: {failure['remediation']}")
            
            return "\n".join(output)
    
    def _format_rollback_output(self, result: Dict[str, Any]) -> str:
        """Format rollback output"""
        if result.get('success'):
            output = [
                "✅ ROLLBACK SUCCESSFUL",
                f"Rolled back to: {result.get('rolled_back_to', 'N/A')}",
                f"Rollback type: {result.get('rollback_type', 'N/A')}"
            ]
            
            if 'validation' in result:
                val = result['validation']
                output.extend([
                    "",
                    "Post-rollback Validation:",
                    f"  Git Status: {val.get('git_status', 'unknown')}",
                    f"  Tests Passing: {val.get('tests_passing', False)}",
                    f"  Gates Valid: {val.get('gates_valid', False)}"
                ])
            
            return "\n".join(output)
        else:
            return f"❌ ROLLBACK FAILED: {result.get('error', 'Unknown error')}"
    
    def _format_status_output(self, result: Dict[str, Any]) -> str:
        """Format status output"""
        if result.get('active'):
            output = [
                "📊 ACTIVE DEPLOYMENT",
                f"Deployment ID: {result.get('deployment_id', 'N/A')}",
                f"Current Phase: {result.get('current_phase', 'UNKNOWN')}",
                f"Progress: {result.get('progress', '0%')}",
                f"Started: {result.get('started_at', 'N/A')}"
            ]
        else:
            output = [
                "⚪ NO ACTIVE DEPLOYMENT",
                f"Last Deployment: {result.get('last_deployment', 'N/A')}",
                f"Last Status: {result.get('last_status', 'UNKNOWN')}"
            ]
        
        return "\n".join(output)
    
    def _format_metrics_output(self, metrics: Dict[str, Any]) -> str:
        """Format metrics output"""
        output = [
            "=" * 60,
            "📈 DEPLOYMENT METRICS",
            "=" * 60,
            f"Average Duration: {metrics.get('average_duration', 0):.1f} seconds",
            f"Success Rate: {metrics.get('success_rate', 0) * 100:.1f}%",
            f"Total Deployments: {metrics.get('total_deployments', 0)}",
            f"Rollback Count: {metrics.get('rollback_count', 0)}"
        ]
        
        if 'health_score' in metrics:
            score = metrics['health_score']
            status = "🟢 Healthy" if score > 80 else "🟡 Degraded" if score > 60 else "🔴 Unhealthy"
            output.append(f"Health Score: {score}/100 ({status})")
        
        return "\n".join(output)
    
    def format_metrics_table(self, metrics: Dict[str, Any]) -> str:
        """Format metrics as table"""
        return self._format_metrics_output(metrics)


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command-line arguments"""
    parser = argparse.ArgumentParser(
        description='CORTEX Deployment Orchestrator CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Deploy with canary strategy
  python -m src.deployment.deployment_cli deploy --strategy canary

  # Dry-run deployment (validation only)
  python -m src.deployment.deployment_cli deploy --dry-run

  # Deploy with blue-green strategy
  python -m src.deployment.deployment_cli deploy --strategy blue-green

  # Validate all gates
  python -m src.deployment.deployment_cli validate-gates

  # Rollback to BUILD phase
  python -m src.deployment.deployment_cli rollback --phase BUILD

  # Check deployment status
  python -m src.deployment.deployment_cli status

  # View deployment history
  python -m src.deployment.deployment_cli history --limit 20

  # View deployment metrics
  python -m src.deployment.deployment_cli metrics --days 7

  # Admin: Deploy with gates skipped
  python -m src.deployment.deployment_cli deploy --skip-gates
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Deploy command
    deploy_parser = subparsers.add_parser('deploy', help='Execute deployment')
    deploy_parser.add_argument(
        '--strategy',
        choices=['canary', 'blue-green', 'direct'],
        help='Deployment strategy (default: auto-select)'
    )
    deploy_parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate deployment without executing'
    )
    deploy_parser.add_argument(
        '--skip-gates',
        action='store_true',
        help='Skip gate validation (admin only)'
    )
    deploy_parser.add_argument(
        '--checkpoint-id',
        help='Resume deployment from checkpoint'
    )
    
    # Validate-gates command
    validate_parser = subparsers.add_parser('validate-gates', help='Validate deployment gates')
    validate_parser.add_argument(
        '--category',
        choices=['critical', 'warning', 'info'],
        help='Validate specific gate category'
    )
    
    # Rollback command
    rollback_parser = subparsers.add_parser('rollback', help='Rollback deployment')
    rollback_parser.add_argument(
        '--phase',
        choices=['PRE_FLIGHT', 'BUILD', 'DEPLOY', 'VERIFY'],
        help='Rollback to specific phase'
    )
    
    # Status command
    subparsers.add_parser('status', help='Show deployment status')
    
    # History command
    history_parser = subparsers.add_parser('history', help='View deployment history')
    history_parser.add_argument(
        '--limit',
        type=int,
        default=10,
        help='Number of deployments to show (default: 10)'
    )
    history_parser.add_argument(
        '--status',
        choices=['COMPLETED', 'FAILED', 'ROLLED_BACK'],
        help='Filter by deployment status'
    )
    
    # Metrics command
    metrics_parser = subparsers.add_parser('metrics', help='Display deployment metrics')
    metrics_parser.add_argument(
        '--days',
        type=int,
        default=7,
        help='Number of days to analyze (default: 7)'
    )
    
    return parser.parse_args(args)


def handle_deploy_command(cli: DeploymentCLI, args: argparse.Namespace) -> int:
    """Handle deploy command"""
    result = cli.deploy(
        strategy=args.strategy,
        dry_run=args.dry_run,
        skip_gates=args.skip_gates,
        checkpoint_id=getattr(args, 'checkpoint_id', None)
    )
    
    print(cli.format_output(result, 'deploy'))
    return 0 if result.get('success') or result.get('valid') else 1


def handle_validate_gates_command(cli: DeploymentCLI, args: argparse.Namespace) -> int:
    """Handle validate-gates command"""
    result = cli.validate_gates(category=getattr(args, 'category', None))
    
    print(cli.format_output(result, 'validate-gates'))
    return 0 if result.get('passed') else 1


def handle_rollback_command(cli: DeploymentCLI, args: argparse.Namespace) -> int:
    """Handle rollback command"""
    result = cli.rollback(phase=getattr(args, 'phase', None))
    
    print(cli.format_output(result, 'rollback'))
    return 0 if result.get('success') else 1


def handle_status_command(cli: DeploymentCLI, args: argparse.Namespace) -> int:
    """Handle status command"""
    result = cli.status()
    
    print(cli.format_output(result, 'status'))
    return 0


def handle_history_command(cli: DeploymentCLI, args: argparse.Namespace) -> int:
    """Handle history command"""
    history = cli.history(
        limit=args.limit,
        status=getattr(args, 'status', None)
    )
    
    if not history:
        print("No deployment history found")
        return 0
    
    print("=" * 80)
    print("📜 DEPLOYMENT HISTORY")
    print("=" * 80)
    
    for deployment in history:
        print(f"\nDeployment ID: {deployment.get('deployment_id', 'N/A')}")
        print(f"  Timestamp: {deployment.get('timestamp', 'N/A')}")
        print(f"  Status: {deployment.get('status', 'UNKNOWN')}")
        print(f"  Duration: {deployment.get('duration', 0)} seconds")
    
    return 0


def handle_metrics_command(cli: DeploymentCLI, args: argparse.Namespace) -> int:
    """Handle metrics command"""
    metrics = cli.metrics(days=args.days)
    
    print(cli.format_output(metrics, 'metrics'))
    
    # Check for alerts
    alerts = cli.check_metrics_alerts(days=args.days)
    if alerts:
        print("\n⚠️  ALERTS:")
        for alert in alerts:
            level_emoji = "🔴" if alert.get('level') == 'CRITICAL' else "🟡"
            print(f"  {level_emoji} {alert.get('message', 'Unknown alert')}")
    
    return 0


def main():
    """Main CLI entry point"""
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)8s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Parse arguments
    args = parse_args()
    
    if not args.command:
        parse_args(['--help'])
        sys.exit(1)
    
    # Determine if user is admin (simplified check - enhance with actual auth)
    is_admin = False  # TODO: Implement proper admin check
    
    # Initialize CLI
    cli = DeploymentCLI(is_admin=is_admin)
    
    # Route to command handler
    try:
        if args.command == 'deploy':
            exit_code = handle_deploy_command(cli, args)
        elif args.command == 'validate-gates':
            exit_code = handle_validate_gates_command(cli, args)
        elif args.command == 'rollback':
            exit_code = handle_rollback_command(cli, args)
        elif args.command == 'status':
            exit_code = handle_status_command(cli, args)
        elif args.command == 'history':
            exit_code = handle_history_command(cli, args)
        elif args.command == 'metrics':
            exit_code = handle_metrics_command(cli, args)
        else:
            logger.error(f"Unknown command: {args.command}")
            exit_code = 1
        
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        logger.info("\nOperation cancelled by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
