"""
CORTEX Debug System Integration
Connects debug functionality to main orchestrator and entry points.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from pathlib import Path
from typing import Optional, Dict, Any
import sys

from .debug_agent import DebugAgent


class DebugSystemIntegration:
    """
    Integrates debug system with CORTEX orchestrator and entry points.
    """
    
    def __init__(self, brain_root: Path):
        self.brain_root = Path(brain_root)
        self.debug_agent = DebugAgent(brain_root)
        
        # Register debug commands
        self.debug_commands = {
            'debug': self._handle_debug_command,
            'trace': self._handle_debug_command,
            'instrument': self._handle_debug_command,
            'stop debug': self._handle_stop_debug,
            'end debug': self._handle_stop_debug,
            'debug status': self._handle_debug_status,
            'debug report': self._handle_debug_report,
            'debug history': self._handle_debug_history,
        }
    
    def process_message(self, user_message: str) -> Optional[Dict[str, Any]]:
        """
        Process user message for debug intents.
        
        Args:
            user_message: User's natural language message
        
        Returns:
            Debug response dict if debug intent detected, None otherwise
        """
        # Detect debug intent
        intent = self.debug_agent.detect_debug_intent(user_message)
        
        if not intent:
            return None
        
        # Handle debug action
        action = intent.get('action')
        target = intent.get('target')
        
        if action == 'start':
            return self._start_debug_session(target, user_message)
        
        elif action == 'stop':
            return self._stop_debug_session(target)
        
        return None
    
    def _start_debug_session(self, target: Optional[str], original_message: str) -> Dict[str, Any]:
        """Start a debug session."""
        try:
            session = self.debug_agent.start_debug_session(target=target)
            
            # Auto-instrument if target specified and module found
            instrumented_count = 0
            if target and session.target_module:
                try:
                    instrumented_count = self.debug_agent.instrument_module(
                        session=session,
                        module_path=session.target_module
                    )
                except Exception:
                    # Module instrumentation failed, but session still valid
                    pass
            
            response_text = self.debug_agent.format_debug_response('start', session)
            if instrumented_count > 0:
                response_text += f"\n\n✅ Instrumented {instrumented_count} functions automatically."
            
            return {
                'intent': 'DEBUG',
                'action': 'start',
                'session_id': session.session_id,
                'response': response_text,
                'success': True
            }
        
        except Exception as e:
            return {
                'intent': 'DEBUG',
                'action': 'start',
                'response': f"Failed to start debug session: {str(e)}",
                'success': False,
                'error': str(e)
            }
    
    def _stop_debug_session(self, session_id: Optional[str]) -> Dict[str, Any]:
        """Stop a debug session."""
        try:
            summary = self.debug_agent.stop_debug_session(session_id=session_id)
            response_text = self.debug_agent.format_debug_response('stop', summary)
            
            return {
                'intent': 'DEBUG',
                'action': 'stop',
                'response': response_text,
                'summary': summary,
                'success': True
            }
        
        except Exception as e:
            return {
                'intent': 'DEBUG',
                'action': 'stop',
                'response': f"Failed to stop debug session: {str(e)}",
                'success': False,
                'error': str(e)
            }
    
    def _handle_debug_command(self, args: str) -> Dict[str, Any]:
        """Handle generic debug command."""
        return self.process_message(f"debug {args}")
    
    def _handle_stop_debug(self, args: str = "") -> Dict[str, Any]:
        """Handle stop debug command."""
        return self._stop_debug_session(args if args else None)
    
    def _handle_debug_status(self, args: str = "") -> Dict[str, Any]:
        """Handle debug status command."""
        active_sessions = self.debug_agent.manager.get_active_sessions()
        
        if not active_sessions:
            return {
                'intent': 'DEBUG',
                'action': 'status',
                'response': "No active debug sessions.",
                'success': True
            }
        
        reports = []
        for session_id in active_sessions:
            report = self.debug_agent.get_session_report(session_id)
            reports.append(self.debug_agent.format_debug_response('report', report))
        
        return {
            'intent': 'DEBUG',
            'action': 'status',
            'response': "\n\n".join(reports),
            'active_sessions': active_sessions,
            'success': True
        }
    
    def _handle_debug_report(self, session_id: str) -> Dict[str, Any]:
        """Handle debug report command."""
        if not session_id:
            return self._handle_debug_status()
        
        try:
            report = self.debug_agent.get_session_report(session_id)
            response_text = self.debug_agent.format_debug_response('report', report)
            
            return {
                'intent': 'DEBUG',
                'action': 'report',
                'response': response_text,
                'report': report,
                'success': True
            }
        
        except Exception as e:
            return {
                'intent': 'DEBUG',
                'action': 'report',
                'response': f"Failed to get debug report: {str(e)}",
                'success': False,
                'error': str(e)
            }
    
    def _handle_debug_history(self, limit: str = "10") -> Dict[str, Any]:
        """Handle debug history command."""
        try:
            limit_int = int(limit) if limit else 10
            history = self.debug_agent.manager.get_session_history(limit=limit_int)
            
            if not history:
                return {
                    'intent': 'DEBUG',
                    'action': 'history',
                    'response': "No debug session history found.",
                    'success': True
                }
            
            response_lines = ["📊 **Debug Session History:**\n"]
            for record in history:
                status_emoji = "🟢" if record['status'] == "active" else "⚪"
                response_lines.append(
                    f"{status_emoji} **{record['session_id']}**\n"
                    f"   - Module: {record['target_module'] or 'N/A'}\n"
                    f"   - Started: {record['start_time']}\n"
                    f"   - Functions: {len(record.get('instrumented_functions', []))}"
                )
            
            return {
                'intent': 'DEBUG',
                'action': 'history',
                'response': "\n".join(response_lines),
                'history': history,
                'success': True
            }
        
        except Exception as e:
            return {
                'intent': 'DEBUG',
                'action': 'history',
                'response': f"Failed to get debug history: {str(e)}",
                'success': False,
                'error': str(e)
            }
    
    def get_debug_capabilities(self) -> Dict[str, Any]:
        """Get debug system capabilities for documentation."""
        return {
            'name': 'Debug System',
            'version': '1.0.0',
            'description': 'Runtime instrumentation and debug logging without source modification',
            'commands': [
                {
                    'trigger': 'debug [target]',
                    'description': 'Start debug session for target module/function',
                    'examples': ['debug planner', 'debug authentication', 'debug PlannerAgent']
                },
                {
                    'trigger': 'stop debug',
                    'description': 'Stop active debug session',
                    'examples': ['stop debug', 'end debug session']
                },
                {
                    'trigger': 'debug status',
                    'description': 'Show active debug sessions',
                    'examples': ['debug status', 'show debug sessions']
                },
                {
                    'trigger': 'debug report [session_id]',
                    'description': 'Get detailed report for debug session',
                    'examples': ['debug report auth-abc123']
                },
                {
                    'trigger': 'debug history',
                    'description': 'Show recent debug session history',
                    'examples': ['debug history', 'show debug history']
                }
            ],
            'features': [
                'Zero source file modification',
                'Automatic cleanup on session end',
                'Function call tracking and timing',
                'Variable capture (args, returns)',
                'Error tracking and logging',
                'Session history and replay',
                'Multi-session support'
            ],
            'storage': {
                'logs': 'cortex-brain/debug-sessions/[session-id]/',
                'database': 'cortex-brain/tier1-working-memory.db'
            }
        }


def create_debug_integration(brain_root: Path) -> DebugSystemIntegration:
    """Factory function to create debug integration."""
    return DebugSystemIntegration(brain_root)


# Convenience functions for direct use
def start_debug(target: Optional[str] = None, brain_root: Optional[Path] = None) -> Any:
    """Quick start debug session."""
    if brain_root is None:
        brain_root = Path(__file__).parent.parent
    
    integration = create_debug_integration(brain_root)
    result = integration.process_message(f"debug {target}" if target else "debug")
    return result


def stop_debug(session_id: Optional[str] = None, brain_root: Optional[Path] = None) -> Any:
    """Quick stop debug session."""
    if brain_root is None:
        brain_root = Path(__file__).parent.parent
    
    integration = create_debug_integration(brain_root)
    result = integration._stop_debug_session(session_id)
    return result
