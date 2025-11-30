"""
Session Banner Handler - Sprint 1 (Rulebook Visibility)

Provides session initialization and welcome banner display logic
for CORTEX entry points.

This module should be called at the start of any CORTEX interaction
to ensure rulebook visibility.

USAGE:
    from src.entry_point.session_banner_handler import SessionBannerHandler
    
    # At start of CORTEX interaction
    handler = SessionBannerHandler()
    banner_result = handler.check_and_display_banner(session_id)
    
    if banner_result["show_banner"]:
        print(banner_result["banner_content"])

INTEGRATION POINTS:
- UnifiedEntryPointOrchestrator
- System initialization flows
- Interactive session starts

SPRINT 1 DAY 1: Session Banner Integration
Author: Asif Hussain (CORTEX Enhancement System)
Date: November 28, 2025
"""

import logging
from typing import Dict, Any, Optional

from src.cortex_agents.welcome_banner_agent import WelcomeBannerAgent
from src.cortex_agents.base_agent import AgentRequest


class SessionBannerHandler:
    """
    Handles session-based governance banner display at CORTEX entry points.
    
    Features:
    - Automatic session ID generation if none provided
    - Once-per-session banner display
    - Template-based banner content
    - Session state persistence
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize session banner handler.
        
        Args:
            db_path: Optional custom database path
        """
        self.logger = logging.getLogger(__name__)
        self.banner_agent = WelcomeBannerAgent(db_path=db_path)
        self.logger.info("SessionBannerHandler initialized")
    
    def check_and_display_banner(self, session_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Check if banner should be displayed and return banner content if needed.
        
        Args:
            session_id: Optional session identifier. If None, new session created.
        
        Returns:
            Dict with keys:
                - show_banner (bool): Whether to display banner
                - banner_content (str): Banner text (if show_banner=True)
                - session_id (str): Current/new session ID
                - is_new_session (bool): Whether session was just created
        """
        # Check session state
        check_request = AgentRequest(
            intent="check_session",
            context={"session_id": session_id},
            user_message=""
        )
        
        check_response = self.banner_agent.execute(check_request)
        
        if not check_response.success:
            self.logger.error(f"Session check failed: {check_response.error}")
            return {
                "show_banner": False,
                "banner_content": "",
                "session_id": session_id or "",
                "is_new_session": False,
                "error": check_response.error
            }
        
        session_data = check_response.result
        show_banner = session_data.get("show_banner", False)
        current_session_id = session_data.get("session_id", session_id)
        is_new_session = session_data.get("is_new_session", False)
        
        # Get banner content if needed
        banner_content = ""
        if show_banner:
            content_request = AgentRequest(
                intent="get_banner_content",
                context={},
                user_message=""
            )
            
            content_response = self.banner_agent.execute(content_request)
            
            if content_response.success:
                banner_content = content_response.result.get("banner_text", "")
            else:
                self.logger.warning(f"Failed to get banner content: {content_response.error}")
        
        return {
            "show_banner": show_banner,
            "banner_content": banner_content,
            "session_id": current_session_id,
            "is_new_session": is_new_session
        }
    
    def mark_banner_shown(self, session_id: str) -> bool:
        """
        Mark that banner has been shown for this session.
        
        Should be called after displaying the banner to the user.
        
        Args:
            session_id: Session identifier
        
        Returns:
            True if successfully marked, False otherwise
        """
        mark_request = AgentRequest(
            intent="mark_shown",
            context={"session_id": session_id},
            user_message=""
        )
        
        mark_response = self.banner_agent.execute(mark_request)
        
        if not mark_response.success:
            self.logger.error(f"Failed to mark banner as shown: {mark_response.error}")
            return False
        
        self.logger.info(f"Banner marked as shown for session: {session_id}")
        return True
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get statistics about banner displays across all sessions.
        
        Returns:
            Dict with session metrics
        """
        return self.banner_agent.get_session_stats()


# Convenience function for quick integration
def display_welcome_banner_if_needed(session_id: Optional[str] = None) -> Optional[str]:
    """
    Quick integration function for displaying welcome banner.
    
    Usage:
        from src.entry_point.session_banner_handler import display_welcome_banner_if_needed
        
        # At start of CORTEX interaction
        session_id = display_welcome_banner_if_needed(session_id)
    
    Args:
        session_id: Optional existing session ID
    
    Returns:
        Session ID (new or existing)
    """
    handler = SessionBannerHandler()
    result = handler.check_and_display_banner(session_id)
    
    if result["show_banner"]:
        print("\n" + result["banner_content"] + "\n")
        handler.mark_banner_shown(result["session_id"])
    
    return result["session_id"]
