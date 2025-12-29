#!/usr/bin/env python3
"""
CORTEX CLI - Command-line interface for CORTEX conversation tracking

This CLI bridges the gap between Copilot Chat and Python tracking.

Usage:
    python cortex_cli.py "Add authentication to login page"
    python cortex_cli.py --validate
    python cortex_cli.py --session-info
    
Environment:
    CORTEX_BRAIN_PATH: Path to cortex-brain directory (default: auto-detect)
"""

import sys
import json
import argparse
from pathlib import Path
from datetime import datetime

# Add CORTEX to path - must add parent directory for package imports to work
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent

# Critical: Add PROJECT_ROOT to sys.path so "CORTEX.src" imports work
sys.path.insert(0, str(PROJECT_ROOT))

# Now we can import using the package structure
from CORTEX.src.entry_point.cortex_entry import CortexEntry


class CortexCLI:
    """Command-line interface for CORTEX"""
    
    def __init__(self, brain_path: str = None):
        """Initialize CLI with brain path"""
        if brain_path is None:
            brain_path = str(PROJECT_ROOT / "cortex-brain")
        
        self.brain_path = Path(brain_path)
        self.entry = None
    
    def _ensure_initialized(self):
        """Lazy initialize CortexEntry"""
        if self.entry is None:
            print(f"🧠 Initializing CORTEX...", file=sys.stderr)
            self.entry = CortexEntry(
                brain_path=str(self.brain_path),
                enable_logging=True
            )
    
    def process_message(self, message: str, intent: str = None, format_type: str = "text"):
        """
        Process a user message through CORTEX
        
        Args:
            message: User message
            intent: Optional intent hint (PLAN, EXECUTE, TEST, etc.)
            format_type: Output format (text, json, markdown)
        
        Returns:
            Response string
        """
        self._ensure_initialized()
        
        metadata = {}
        if intent:
            metadata['intent_hint'] = intent
        
        print(f"📝 Processing: {message[:50]}...", file=sys.stderr)
        
        response = self.entry.process(
            user_message=message,
            resume_session=True,
            format_type=format_type,
            metadata=metadata
        )
        
        return response
    
    def validate(self) -> bool:
        """
        Validate conversation tracking is working
        
        Returns:
            True if validation passes
        """
        import sqlite3
        
        db_path = self.brain_path / "tier1" / "conversations.db"
        
        if not db_path.exists():
            print(f"❌ Database not found: {db_path}", file=sys.stderr)
            return False
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check conversations
            cursor.execute("SELECT COUNT(*) FROM conversations")
            conv_count = cursor.fetchone()[0]
            
            # Check messages
            cursor.execute("SELECT COUNT(*) FROM messages")
            msg_count = cursor.fetchone()[0]
            
            # Check recent activity
            cursor.execute("""
                SELECT COUNT(*) FROM messages 
                WHERE timestamp > datetime('now', '-1 day')
            """)
            recent_count = cursor.fetchone()[0]
            
            conn.close()
            
            print(f"✅ Conversations: {conv_count}")
            print(f"✅ Messages: {msg_count}")
            print(f"✅ Recent (24h): {recent_count}")
            
            if msg_count == 0:
                print("⚠️  WARNING: No messages in database!")
                return False
            
            return True
            
        except Exception as e:
            print(f"❌ Validation error: {e}", file=sys.stderr)
            return False
    
    def session_info(self) -> dict:
        """
        Get current session information
        
        Returns:
            Session info dict
        """
        self._ensure_initialized()
        
        info = self.entry.get_session_info()
        
        if info:
            print(f"📊 Session Information:")
            print(f"   Conversation ID: {info.get('conversation_id')}")
            print(f"   Started: {info.get('start_time')}")
            print(f"   Messages: {info.get('message_count')}")
            print(f"   Status: {info.get('status')}")
        else:
            print("ℹ️  No active session")
        
        return info
    
    def end_session(self):
        """End current session"""
        self._ensure_initialized()
        self.entry.end_session()
        print("✅ Session ended")


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="CORTEX CLI - Conversation tracking bridge",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a message
  python cortex_cli.py "Create authentication tests"
  
  # Process with intent hint
  python cortex_cli.py -i PLAN "Design user authentication flow"
  
  # Validate tracking
  python cortex_cli.py --validate
  
  # Check session
  python cortex_cli.py --session-info
  
  # End session
  python cortex_cli.py --end-session
        """
    )
    
    parser.add_argument(
        'message',
        nargs='?',
        help='User message to process'
    )
    
    parser.add_argument(
        '-i', '--intent',
        choices=['PLAN', 'EXECUTE', 'TEST', 'VALIDATE', 'GOVERN', 'ASK'],
        help='Intent classification hint'
    )
    
    parser.add_argument(
        '-f', '--format',
        choices=['text', 'json', 'markdown'],
        default='text',
        help='Output format (default: text)'
    )
    
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Validate conversation tracking system'
    )
    
    parser.add_argument(
        '--session-info',
        action='store_true',
        help='Show current session information'
    )
    
    parser.add_argument(
        '--end-session',
        action='store_true',
        help='End current session'
    )
    
    parser.add_argument(
        '--brain-path',
        help='Path to cortex-brain directory'
    )
    
    args = parser.parse_args()
    
    # Initialize CLI
    cli = CortexCLI(brain_path=args.brain_path)
    
    # Handle commands
    if args.validate:
        success = cli.validate()
        sys.exit(0 if success else 1)
    
    elif args.session_info:
        cli.session_info()
        sys.exit(0)
    
    elif args.end_session:
        cli.end_session()
        sys.exit(0)
    
    elif args.message:
        # Process message
        try:
            response = cli.process_message(
                args.message,
                intent=args.intent,
                format_type=args.format
            )
            
            print("\n" + "="*60)
            print(response)
            print("="*60)
            
            # Show session info
            print("\n📊 Session:", file=sys.stderr)
            info = cli.entry.get_session_info()
            if info:
                print(f"   ID: {info['conversation_id']}", file=sys.stderr)
                print(f"   Messages: {info['message_count']}", file=sys.stderr)
            
            sys.exit(0)
            
        except Exception as e:
            print(f"\n❌ Error: {e}", file=sys.stderr)
            sys.exit(1)
    
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
