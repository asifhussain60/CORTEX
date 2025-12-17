"""
CORTEX Planning System 4.0 - Audit Trail Viewer CLI

Command-line utility for viewing and analyzing planning system audit logs.

Author: Asif Hussain
GitHub: github.com/asifhussain60/CORTEX

Usage:
    python -m scripts.cli_wrappers.audit_wrapper --plan-id plan-123
    python -m scripts.cli_wrappers.audit_wrapper --session-id session-456
    python -m scripts.cli_wrappers.audit_wrapper --tail 20
    python -m scripts.cli_wrappers.audit_wrapper --stats
    python -m scripts.cli_wrappers.audit_wrapper --timeline --plan-id plan-123
    python -m scripts.cli_wrappers.audit_wrapper --export csv --output report.csv
"""

import argparse
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.operations.modules.orchestration.audit_logger import get_audit_logger


class AuditViewer:
    """Human-friendly audit log viewer."""
    
    def __init__(self):
        """Initialize audit viewer."""
        self.logger = get_audit_logger()
    
    def view_events(
        self,
        plan_id: str = None,
        session_id: str = None,
        event_type: str = None,
        orchestrator: str = None,
        since: str = None,
        until: str = None,
        outcome: str = None,
        tail: int = None,
        timeline: bool = False
    ) -> None:
        """
        View audit events with formatting.
        
        Args:
            plan_id: Filter by plan ID
            session_id: Filter by session ID
            event_type: Filter by event type
            orchestrator: Filter by orchestrator
            since: Events after this date (YYYY-MM-DD)
            until: Events before this date (YYYY-MM-DD)
            outcome: Filter by outcome
            tail: Show last N events
            timeline: Show as timeline visualization
        """
        # Parse dates
        since_dt = datetime.fromisoformat(since) if since else None
        until_dt = datetime.fromisoformat(until) if until else None
        
        # Query events
        events = self.logger.query_events(
            plan_id=plan_id,
            session_id=session_id,
            event_type=event_type,
            orchestrator=orchestrator,
            since=since_dt,
            until=until_dt,
            outcome=outcome,
            limit=tail
        )
        
        if not events:
            print("No events found matching the criteria.")
            return
        
        # Display based on format
        if timeline:
            self._display_timeline(events)
        else:
            self._display_table(events)
    
    def _display_table(self, events: List[Dict[str, Any]]) -> None:
        """Display events in table format."""
        print(f"\n📋 Audit Events ({len(events)} total)\n")
        print("=" * 120)
        
        for event in events:
            timestamp = event.get('timestamp', 'N/A')[:19]  # Trim to seconds
            event_type = event.get('event_type', 'unknown')
            orchestrator = event.get('orchestrator', 'unknown')
            outcome = event.get('outcome', 'unknown')
            
            # Outcome emoji
            outcome_emoji = {
                'success': '✅',
                'failure': '❌',
                'warning': '⚠️'
            }.get(outcome, '❓')
            
            print(f"{timestamp} | {outcome_emoji} {event_type:30s} | {orchestrator:25s}")
            
            # Show key metadata
            metadata = event.get('metadata', {})
            if metadata:
                print(f"           Metadata: {self._format_metadata(metadata)}")
            
            # Show error if present
            if event.get('error_message'):
                print(f"           Error: {event['error_message']}")
            
            # Show duration if present
            if event.get('duration_ms'):
                duration_sec = event['duration_ms'] / 1000
                print(f"           Duration: {duration_sec:.2f}s")
            
            print("-" * 120)
        
        print()
    
    def _display_timeline(self, events: List[Dict[str, Any]]) -> None:
        """Display events as ASCII timeline."""
        # Sort chronologically (oldest first) for timeline
        sorted_events = sorted(events, key=lambda x: x.get('timestamp', ''))
        
        print(f"\n📊 Timeline View ({len(sorted_events)} events)\n")
        print("=" * 100)
        
        for i, event in enumerate(sorted_events):
            timestamp = event.get('timestamp', 'N/A')[11:19]  # Extract time only
            event_type = event.get('event_type', 'unknown')
            outcome = event.get('outcome', 'unknown')
            
            # Outcome emoji
            outcome_emoji = {
                'success': '✅',
                'failure': '❌',
                'warning': '⚠️'
            }.get(outcome, '❓')
            
            # Timeline connector
            if i == 0:
                connector = "●────"
            elif i == len(sorted_events) - 1:
                connector = "│  └─●"
            else:
                connector = "│  ├─●"
            
            print(f"{timestamp} {connector} {outcome_emoji} {event_type}")
            
            # Show key metadata inline
            metadata = event.get('metadata', {})
            if metadata:
                key_info = []
                if 'dor_score' in metadata:
                    key_info.append(f"DoR: {metadata['dor_score']:.0%}")
                if 'iteration' in metadata:
                    key_info.append(f"Iter: {metadata['iteration']}")
                if 'complexity_tier' in metadata:
                    key_info.append(f"Tier: {metadata['complexity_tier']}")
                
                if key_info:
                    print(f"         │      ({', '.join(key_info)})")
        
        print("=" * 100)
        print()
    
    def _format_metadata(self, metadata: Dict[str, Any], max_length: int = 80) -> str:
        """Format metadata for display."""
        items = []
        for key, value in metadata.items():
            if isinstance(value, float) and 0 <= value <= 1:
                # Format as percentage
                items.append(f"{key}={value:.0%}")
            elif isinstance(value, (dict, list)):
                # Skip complex objects
                items.append(f"{key}=[complex]")
            else:
                items.append(f"{key}={value}")
        
        result = ", ".join(items)
        if len(result) > max_length:
            result = result[:max_length - 3] + "..."
        return result
    
    def show_stats(self, days: int = 30) -> None:
        """Display audit statistics."""
        since = datetime.utcnow() - timedelta(days=days)
        stats = self.logger.generate_stats(since=since)
        
        print(f"\n📊 Audit Trail Statistics (Last {days} Days)")
        print("=" * 80)
        print()
        print(f"Total Events:        {stats.get('total_events', 0):,}")
        print(f"Active Sessions:     {stats.get('active_sessions', 0)}")
        print(f"Plans Created:       {stats.get('plans_created', 0)}")
        print(f"Plans Approved:      {stats.get('plans_approved', 0)}")
        print(f"Plans Promoted:      {stats.get('plans_promoted', 0)}")
        print()
        print(f"Avg DoR Score:       {stats.get('avg_dor_score', 0.0):.0%}")
        print(f"Avg Refinement Iterations: {stats.get('avg_refinement_iterations', 0.0):.1f}")
        print(f"Avg Session Duration:      {stats.get('avg_session_duration_minutes', 0.0):.1f} minutes")
        print()
        
        # Event types breakdown
        event_types = stats.get('event_types', {})
        if event_types:
            print("Most Common Event Types:")
            for i, (event_type, count) in enumerate(list(event_types.items())[:10], 1):
                print(f"  {i}. {event_type:30s} ({count:,} events)")
        
        print()
        
        # Outcomes breakdown
        outcomes = stats.get('outcomes', {})
        if outcomes:
            print("Outcomes:")
            for outcome, count in outcomes.items():
                emoji = {
                    'success': '✅',
                    'failure': '❌',
                    'warning': '⚠️'
                }.get(outcome, '❓')
                percentage = (count / stats.get('total_events', 1)) * 100
                print(f"  {emoji} {outcome:10s}: {count:,} ({percentage:.1f}%)")
        
        print()
        print("=" * 80)
        print()
    
    def export_csv(
        self,
        output_path: str,
        plan_id: str = None,
        session_id: str = None,
        since: str = None,
        until: str = None
    ) -> None:
        """Export events to CSV."""
        # Parse dates
        since_dt = datetime.fromisoformat(since) if since else None
        until_dt = datetime.fromisoformat(until) if until else None
        
        # Query events
        events = self.logger.query_events(
            plan_id=plan_id,
            session_id=session_id,
            since=since_dt,
            until=until_dt
        )
        
        if not events:
            print("No events found to export.")
            return
        
        # Export
        self.logger.export_to_csv(events, output_path)
        print(f"✅ Exported {len(events)} events to {output_path}")
    
    def archive_logs(self, days: int = 30) -> None:
        """Archive old logs."""
        print(f"🗄️  Archiving logs older than {days} days...")
        result = self.logger.archive_old_logs(days_threshold=days)
        
        archived = result.get('archived', 0)
        months = result.get('months', [])
        remaining = result.get('remaining', 0)
        
        if archived > 0:
            print(f"✅ Archived {archived:,} events")
            print(f"   Months: {', '.join(months)}")
            print(f"   Remaining in active log: {remaining:,} events")
        else:
            print("No events to archive.")


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="CORTEX Planning System 4.0 - Audit Trail Viewer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # View all events for a plan
  cortex audit --plan-id plan-abc123
  
  # View session timeline
  cortex audit --session-id session-xyz789 --timeline
  
  # View last 20 events
  cortex audit --tail 20
  
  # View events by type
  cortex audit --type plan_refined
  
  # View events in date range
  cortex audit --since 2025-12-01 --until 2025-12-17
  
  # Show statistics
  cortex audit --stats
  
  # Export to CSV
  cortex audit --export csv --output report.csv --plan-id plan-abc123
  
  # Archive old logs
  cortex audit --archive --days 30
        """
    )
    
    # Filter options
    parser.add_argument('--plan-id', help='Filter by plan ID')
    parser.add_argument('--session-id', help='Filter by session ID')
    parser.add_argument('--type', dest='event_type', help='Filter by event type')
    parser.add_argument('--orchestrator', help='Filter by orchestrator name')
    parser.add_argument('--since', help='Events after this date (YYYY-MM-DD)')
    parser.add_argument('--until', help='Events before this date (YYYY-MM-DD)')
    parser.add_argument('--outcome', choices=['success', 'failure', 'warning'],
                        help='Filter by outcome')
    parser.add_argument('--tail', type=int, metavar='N',
                        help='Show last N events')
    
    # Display options
    parser.add_argument('--timeline', action='store_true',
                        help='Display as timeline visualization')
    parser.add_argument('--stats', action='store_true',
                        help='Show statistics summary')
    parser.add_argument('--days', type=int, default=30,
                        help='Days for statistics (default: 30)')
    
    # Export options
    parser.add_argument('--export', choices=['csv'],
                        help='Export format')
    parser.add_argument('--output', help='Output file path for export')
    
    # Archive options
    parser.add_argument('--archive', action='store_true',
                        help='Archive old logs')
    
    args = parser.parse_args()
    
    # Validate
    if args.export and not args.output:
        parser.error("--export requires --output")
    
    # Create viewer
    viewer = AuditViewer()
    
    # Execute command
    if args.stats:
        viewer.show_stats(days=args.days)
    elif args.archive:
        viewer.archive_logs(days=args.days)
    elif args.export:
        viewer.export_csv(
            output_path=args.output,
            plan_id=args.plan_id,
            session_id=args.session_id,
            since=args.since,
            until=args.until
        )
    else:
        viewer.view_events(
            plan_id=args.plan_id,
            session_id=args.session_id,
            event_type=args.event_type,
            orchestrator=args.orchestrator,
            since=args.since,
            until=args.until,
            outcome=args.outcome,
            tail=args.tail,
            timeline=args.timeline
        )


if __name__ == '__main__':
    main()
