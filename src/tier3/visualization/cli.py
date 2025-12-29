"""
CLI Interface

Command-line interface for CORTEX adoption analytics.
Provides interactive prompts and configuration wizard.

Author: Asif Hussain
Version: 1.0.0
"""

import argparse
import sys
from datetime import date, timedelta
from pathlib import Path
from typing import Optional
import json

# Import all analytics components
from src.tier3.orchestrators.adoption_analytics_orchestrator import (
    AdoptionAnalyticsOrchestrator,
    CollectionConfig,
    ScheduleType
)
from src.tier3.metrics.roi_calculator import ROICalculator, ROIConfig
from src.tier3.metrics.correlation_engine import CorrelationEngine
from src.tier3.metrics.privacy_safe_export import (
    PrivacySafeExporter,
    ExportConfig,
    ExportFormat,
    AnonymizationLevel
)
from src.tier3.visualization.dashboard_generator import (
    DashboardGenerator,
    DashboardConfig
)
from src.tier3.visualization.report_generator import (
    ReportGenerator,
    ReportConfig,
    ReportFormat,
    ReportFrequency
)
from src.tier3.visualization.real_time_monitor import (
    RealTimeMonitor,
    MonitorConfig
)


class AdoptionAnalyticsCLI:
    """
    Command-line interface for adoption analytics.
    
    Features:
    - Interactive prompts for configuration
    - Subcommands for all major operations
    - Wizard mode for initial setup
    - JSON config file support
    - Progress indicators
    - Error handling with helpful messages
    
    Usage:
        # Collect metrics
        python -m src.tier3.visualization.cli collect --engineers eng1@example.com eng2@example.com
        
        # Generate dashboard
        python -m src.tier3.visualization.cli dashboard --output dashboard.html
        
        # Calculate ROI
        python -m src.tier3.visualization.cli roi --team platform-team
        
        # Export data
        python -m src.tier3.visualization.cli export --format json --output export.json
        
        # Generate report
        python -m src.tier3.visualization.cli report --frequency weekly
        
        # Real-time monitoring
        python -m src.tier3.visualization.cli monitor
        
        # Run configuration wizard
        python -m src.tier3.visualization.cli wizard
    """
    
    def __init__(self):
        """Initialize CLI with argument parser"""
        self.parser = argparse.ArgumentParser(
            description="CORTEX Adoption Analytics CLI",
            formatter_class=argparse.RawDescriptionHelpFormatter
        )
        self._setup_parsers()
    
    def _setup_parsers(self):
        """Setup all subcommand parsers"""
        subparsers = self.parser.add_subparsers(dest='command', help='Available commands')
        
        # Common arguments
        common = argparse.ArgumentParser(add_help=False)
        common.add_argument('--db', type=str, help='Database path', 
                          default='cortex-brain/development_context.db')
        common.add_argument('--config', type=str, help='Config file path')
        
        # Collect command
        collect_parser = subparsers.add_parser('collect', parents=[common],
                                              help='Collect adoption metrics')
        collect_parser.add_argument('--engineers', nargs='+', required=True,
                                   help='Engineer email addresses')
        collect_parser.add_argument('--github-token', type=str, required=True,
                                   help='GitHub personal access token')
        collect_parser.add_argument('--team-id', type=str, help='Team identifier')
        collect_parser.add_argument('--backfill-days', type=int, default=0,
                                   help='Days to backfill (0 = today only)')
        
        # Dashboard command
        dashboard_parser = subparsers.add_parser('dashboard', parents=[common],
                                                help='Generate HTML dashboard')
        dashboard_parser.add_argument('--output', type=str, required=True,
                                     help='Output HTML file path')
        dashboard_parser.add_argument('--days', type=int, default=30,
                                     help='Days of data to include')
        dashboard_parser.add_argument('--theme', choices=['light', 'dark'],
                                     default='light', help='Dashboard theme')
        
        # ROI command
        roi_parser = subparsers.add_parser('roi', parents=[common],
                                          help='Calculate ROI metrics')
        roi_parser.add_argument('--team', type=str, help='Team ID for team ROI')
        roi_parser.add_argument('--engineer', type=str, help='Engineer hash for individual ROI')
        roi_parser.add_argument('--days', type=int, default=30,
                                help='Analysis period in days')
        roi_parser.add_argument('--hourly-cost', type=float, default=50.0,
                               help='Engineer hourly cost (USD)')
        
        # Export command
        export_parser = subparsers.add_parser('export', parents=[common],
                                             help='Export analytics data')
        export_parser.add_argument('--output', type=str, required=True,
                                  help='Output file path')
        export_parser.add_argument('--format', choices=['json', 'csv'],
                                  default='json', help='Export format')
        export_parser.add_argument('--anonymization', 
                                  choices=['none', 'basic', 'full'],
                                  default='full', help='Anonymization level')
        export_parser.add_argument('--days', type=int, default=30,
                                  help='Days of data to export')
        
        # Report command
        report_parser = subparsers.add_parser('report', parents=[common],
                                             help='Generate analytics report')
        report_parser.add_argument('--output', type=str, required=True,
                                  help='Output report file path')
        report_parser.add_argument('--format', choices=['markdown', 'html', 'text'],
                                  default='markdown', help='Report format')
        report_parser.add_argument('--frequency', 
                                  choices=['daily', 'weekly', 'monthly', 'quarterly'],
                                  default='weekly', help='Report frequency')
        
        # Monitor command
        monitor_parser = subparsers.add_parser('monitor', parents=[common],
                                              help='Real-time monitoring')
        monitor_parser.add_argument('--interval', type=int, default=60,
                                   help='Update interval in seconds')
        monitor_parser.add_argument('--acceptance-threshold', type=float, default=0.3,
                                   help='Alert threshold for acceptance rate')
        
        # Wizard command
        subparsers.add_parser('wizard', help='Interactive configuration wizard')
    
    def run(self):
        """Run CLI with parsed arguments"""
        args = self.parser.parse_args()
        
        if not args.command:
            self.parser.print_help()
            return
        
        try:
            if args.command == 'collect':
                self._cmd_collect(args)
            elif args.command == 'dashboard':
                self._cmd_dashboard(args)
            elif args.command == 'roi':
                self._cmd_roi(args)
            elif args.command == 'export':
                self._cmd_export(args)
            elif args.command == 'report':
                self._cmd_report(args)
            elif args.command == 'monitor':
                self._cmd_monitor(args)
            elif args.command == 'wizard':
                self._cmd_wizard()
            
        except Exception as e:
            print(f"❌ Error: {str(e)}", file=sys.stderr)
            sys.exit(1)
    
    def _cmd_collect(self, args):
        """Execute collect command"""
        print(f"📊 Collecting metrics for {len(args.engineers)} engineers...")
        
        config = CollectionConfig(
            db_path=args.db,
            github_token=args.github_token,
            schedule_type=ScheduleType.MANUAL
        )
        
        orchestrator = AdoptionAnalyticsOrchestrator(config)
        
        if args.backfill_days > 0:
            end_date = date.today()
            start_date = end_date - timedelta(days=args.backfill_days)
            print(f"🔄 Backfilling {args.backfill_days} days...")
            result = orchestrator.backfill_metrics(args.engineers, start_date, end_date)
        else:
            results = orchestrator.collect_batch(args.engineers)
            result = {'successful': sum(1 for r in results if r.success)}
        
        print(f"✅ Collection complete: {result.get('successful', 0)} successful")
        
        if args.team_id:
            print(f"📈 Aggregating team metrics for '{args.team_id}'...")
            # Get engineer hashes (simplified - would need proper hash function)
            from src.tier1.working_memory import hash_email
            team_members = [hash_email(e) for e in args.engineers]
            agg_result = orchestrator.aggregate_team_metrics(
                team_id=args.team_id,
                team_members=team_members,
                aggregation_date=date.today()
            )
            print(f"✅ Team aggregation complete")
    
    def _cmd_dashboard(self, args):
        """Execute dashboard command"""
        print(f"🎨 Generating dashboard...")
        
        config = DashboardConfig(
            theme=args.theme,
            include_roi=True,
            include_trends=True
        )
        
        generator = DashboardGenerator(db_path=args.db, config=config)
        
        end_date = date.today()
        start_date = end_date - timedelta(days=args.days)
        
        result = generator.generate_dashboard(
            output_path=args.output,
            start_date=start_date,
            end_date=end_date
        )
        
        if result.success:
            print(f"✅ Dashboard generated: {result.output_path}")
            print(f"🌐 Open in browser: {result.dashboard_url}")
        else:
            print(f"❌ Dashboard generation failed: {result.error_message}")
    
    def _cmd_roi(self, args):
        """Execute ROI command"""
        print(f"💰 Calculating ROI...")
        
        roi_config = ROIConfig(
            engineer_hourly_cost=args.hourly_cost,
            copilot_time_saved_per_acceptance=0.5,
            cortex_time_saved_per_success=2.0
        )
        
        calculator = ROICalculator(db_path=args.db, config=roi_config)
        
        end_date = date.today()
        start_date = end_date - timedelta(days=args.days)
        
        if args.team:
            result = calculator.calculate_team_roi(
                team_id=args.team,
                start_date=start_date,
                end_date=end_date
            )
            print(f"\n📊 Team ROI Report: {args.team}")
        elif args.engineer:
            result = calculator.calculate_engineer_roi(
                engineer_hash=args.engineer,
                start_date=start_date,
                end_date=end_date
            )
            print(f"\n📊 Engineer ROI Report")
        else:
            summary = calculator.get_roi_summary(start_date, end_date)
            print(f"\n📊 Organization ROI Summary")
            print(f"   Total Engineers: {summary['total_engineers']}")
            print(f"   Time Saved: {summary['total_time_saved_hours']:.1f} hours")
            print(f"   Cost Savings: ${summary['total_cost_savings']:,.2f}")
            print(f"   Avg per Engineer: ${summary['avg_cost_savings_per_engineer']:,.2f}")
            return
        
        if result.success:
            print(f"   Copilot Acceptances: {result.copilot_acceptances:,}")
            print(f"   Copilot Time Saved: {result.copilot_time_saved_hours:.1f} hours")
            print(f"   Copilot Cost Savings: ${result.copilot_cost_savings:,.2f}")
            print(f"   CORTEX Successes: {result.cortex_successful_requests:,}")
            print(f"   CORTEX Time Saved: {result.cortex_time_saved_hours:.1f} hours")
            print(f"   CORTEX Cost Savings: ${result.cortex_cost_savings:,.2f}")
            print(f"   ─────────────────────────────────")
            print(f"   Total Time Saved: {result.total_time_saved_hours:.1f} hours")
            print(f"   Total Cost Savings: ${result.total_cost_savings:,.2f}")
            print(f"   ROI: {result.roi_percentage:.1f}%")
        else:
            print(f"❌ ROI calculation failed: {result.error_message}")
    
    def _cmd_export(self, args):
        """Execute export command"""
        print(f"📤 Exporting data...")
        
        config = ExportConfig(
            format=ExportFormat.JSON if args.format == 'json' else ExportFormat.CSV,
            anonymization_level=AnonymizationLevel[args.anonymization.upper()],
            include_team_data=True,
            include_roi_metrics=True
        )
        
        exporter = PrivacySafeExporter(db_path=args.db, config=config)
        
        end_date = date.today()
        start_date = end_date - timedelta(days=args.days)
        
        result = exporter.export_to_file(
            output_path=args.output,
            start_date=start_date,
            end_date=end_date
        )
        
        if result.success:
            print(f"✅ Export complete: {result.output_path}")
            print(f"   Records: {result.record_count}")
            print(f"   Anonymization: {args.anonymization}")
        else:
            print(f"❌ Export failed: {result.error_message}")
    
    def _cmd_report(self, args):
        """Execute report command"""
        print(f"📄 Generating report...")
        
        config = ReportConfig(
            format=ReportFormat[args.format.upper()],
            frequency=ReportFrequency[args.frequency.upper()],
            include_executive_summary=True,
            include_roi_analysis=True
        )
        
        generator = ReportGenerator(db_path=args.db, config=config)
        
        result = generator.generate_report(
            output_path=args.output,
            report_date=date.today()
        )
        
        if result.success:
            print(f"✅ Report generated: {result.output_path}")
            print(f"   Format: {args.format}")
            print(f"   Frequency: {args.frequency}")
        else:
            print(f"❌ Report generation failed: {result.error_message}")
    
    def _cmd_monitor(self, args):
        """Execute monitor command"""
        print(f"📡 Starting real-time monitor...")
        print(f"   Update interval: {args.interval} seconds")
        print(f"   Press Ctrl+C to stop\n")
        
        config = MonitorConfig(
            update_interval_seconds=args.interval,
            acceptance_rate_threshold=args.acceptance_threshold,
            enable_alerts=True
        )
        
        monitor = RealTimeMonitor(db_path=args.db, config=config)
        
        try:
            while True:
                metrics = monitor.get_current_metrics()
                
                print(f"\r⏰ {metrics.timestamp.strftime('%H:%M:%S')} | "
                      f"Engineers: {metrics.active_engineers} | "
                      f"Acceptance: {metrics.copilot_acceptance_rate:.1%} | "
                      f"Success: {metrics.cortex_success_rate:.1%} | "
                      f"Requests: {metrics.total_requests_today}",
                      end='', flush=True)
                
                if metrics.alerts:
                    print()  # New line for alerts
                    for alert in metrics.alerts:
                        icon = "⚠️" if alert.level.value == "warning" else "ℹ️"
                        print(f"{icon} {alert.message}")
                
                import time
                time.sleep(args.interval)
                
        except KeyboardInterrupt:
            print("\n\n✅ Monitoring stopped")
    
    def _cmd_wizard(self):
        """Execute configuration wizard"""
        print("\n" + "="*60)
        print("  CORTEX Adoption Analytics - Configuration Wizard")
        print("="*60 + "\n")
        
        # Database path
        db_path = input("Database path [cortex-brain/development_context.db]: ").strip()
        if not db_path:
            db_path = "cortex-brain/development_context.db"
        
        # GitHub token
        github_token = input("GitHub personal access token: ").strip()
        
        # Engineer emails
        print("\nEngineer email addresses (comma-separated):")
        engineers_input = input("> ").strip()
        engineers = [e.strip() for e in engineers_input.split(',')]
        
        # Team ID
        team_id = input("\nTeam identifier (optional): ").strip()
        
        # ROI hourly cost
        hourly_cost_input = input("\nEngineer hourly cost USD [50]: ").strip()
        hourly_cost = float(hourly_cost_input) if hourly_cost_input else 50.0
        
        # Save config
        config = {
            'db_path': db_path,
            'github_token': github_token,
            'engineers': engineers,
            'team_id': team_id if team_id else None,
            'roi_hourly_cost': hourly_cost
        }
        
        config_path = 'analytics_config.json'
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        print(f"\n✅ Configuration saved to {config_path}")
        print("\nNext steps:")
        print(f"  1. Collect metrics: python -m src.tier3.visualization.cli collect --config {config_path}")
        print(f"  2. Generate dashboard: python -m src.tier3.visualization.cli dashboard --output dashboard.html")
        print(f"  3. Calculate ROI: python -m src.tier3.visualization.cli roi --team {team_id if team_id else 'YOUR_TEAM'}")


def main():
    """Main entry point"""
    cli = AdoptionAnalyticsCLI()
    cli.run()


if __name__ == '__main__':
    main()
