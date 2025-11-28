"""
Welcome Banner Agent - Sprint 1 (Rulebook Visibility)

Displays a session-based governance banner to ensure users cannot miss
the CORTEX rulebook at system entry points.

FEATURES:
- Session-based display (once per session)
- Natural language dismissal ("show rules", "got it", etc.)
- Persistent session state tracking
- Non-intrusive UX (shown once, then hidden)

INTEGRATION:
- Triggered by UnifiedEntryPointOrchestrator on first interaction
- Uses Tier 1 database for session state persistence
- Template: rulebook_welcome_banner in response-templates.yaml

USAGE:
    from src.cortex_agents.welcome_banner_agent import WelcomeBannerAgent
    
    agent = WelcomeBannerAgent()
    request = AgentRequest(
        intent="check_session",
        context={"session_id": "abc123"},
        user_message=""
    )
    
    response = agent.execute(request)
    if response.success and response.result.get("show_banner"):
        print(response.result["banner_content"])

SPRINT 1 DAY 1: WelcomeBannerAgent Implementation
Author: Asif Hussain (CORTEX Enhancement System)
Date: November 28, 2025
"""

import sqlite3
import uuid
from datetime import datetime
from typing import Dict, Any, Optional
import logging
import os

from src.cortex_agents.base_agent import BaseAgent, AgentRequest, AgentResponse


class WelcomeBannerAgent(BaseAgent):
    """
    Manages session-based governance banner display.
    
    Ensures rulebook visibility without UX annoyance by tracking
    whether banner has been shown in current session.
    
    Attributes:
        db_path: Path to Tier 1 working memory database
        logger: Standard Python logger instance
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize WelcomeBannerAgent with database connection.
        
        Args:
            db_path: Optional custom database path. Defaults to Tier 1 database.
        """
        self.logger = logging.getLogger(__name__)
        
        # Default to Tier 1 working memory database
        if db_path is None:
            project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
            self.db_path = os.path.join(project_root, "cortex-brain", "tier1-working-memory.db")
        else:
            self.db_path = db_path
        
        # Initialize session state table
        self._initialize_session_table()
        
        self.logger.info(f"WelcomeBannerAgent initialized (db: {self.db_path})")
    
    def _initialize_session_table(self) -> None:
        """
        Create session_state table if it doesn't exist.
        
        Schema:
            session_id TEXT PRIMARY KEY - Unique session identifier
            rulebook_banner_shown INTEGER - Boolean flag (0/1)
            first_interaction_time TEXT - ISO timestamp of first interaction
            last_updated TEXT - ISO timestamp of last update
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS session_state (
                    session_id TEXT PRIMARY KEY,
                    rulebook_banner_shown INTEGER DEFAULT 0,
                    first_interaction_time TEXT NOT NULL,
                    last_updated TEXT NOT NULL
                )
            """)
            
            conn.commit()
            conn.close()
            
            self.logger.debug("Session state table initialized successfully")
            
        except sqlite3.Error as e:
            self.logger.error(f"Failed to initialize session table: {e}")
            raise
    
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Check if this agent can handle the request.
        
        Handles:
        - check_session: Check if banner should be shown
        - mark_shown: Mark banner as shown for session
        - get_banner_content: Retrieve banner template content
        
        Args:
            request: AgentRequest with intent and context
        
        Returns:
            True if intent matches one of the supported operations
        """
        supported_intents = ["check_session", "mark_shown", "get_banner_content"]
        return request.intent in supported_intents
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute the welcome banner operation.
        
        Operations:
        - check_session: Verify if banner should be displayed
        - mark_shown: Record that banner was shown
        - get_banner_content: Get formatted banner text
        
        Args:
            request: AgentRequest with intent and context
        
        Returns:
            AgentResponse with operation result
        """
        start_time = datetime.now()
        
        try:
            if request.intent == "check_session":
                result = self._check_session(request.context.get("session_id"))
            elif request.intent == "mark_shown":
                result = self._mark_banner_shown(request.context.get("session_id"))
            elif request.intent == "get_banner_content":
                result = self._get_banner_content()
            else:
                return AgentResponse(
                    success=False,
                    result={},
                    message=f"Unsupported intent: {request.intent}",
                    agent_name="WelcomeBannerAgent",
                    error=f"Intent '{request.intent}' not recognized"
                )
            
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            return AgentResponse(
                success=True,
                result=result,
                message=f"Welcome banner operation completed: {request.intent}",
                agent_name="WelcomeBannerAgent",
                duration_ms=duration
            )
            
        except Exception as e:
            self.logger.error(f"WelcomeBannerAgent execution failed: {e}", exc_info=True)
            duration = (datetime.now() - start_time).total_seconds() * 1000
            
            return AgentResponse(
                success=False,
                result={},
                message=f"Welcome banner operation failed: {str(e)}",
                agent_name="WelcomeBannerAgent",
                duration_ms=duration,
                error=str(e)
            )
    
    def _check_session(self, session_id: Optional[str]) -> Dict[str, Any]:
        """
        Check if banner should be shown for this session.
        
        Creates new session if session_id is None or not found.
        
        Args:
            session_id: Optional session identifier
        
        Returns:
            Dict with keys:
                - show_banner (bool): Whether to display banner
                - session_id (str): Current/new session ID
                - is_new_session (bool): Whether session was just created
        """
        # Generate new session if none provided
        if session_id is None:
            session_id = str(uuid.uuid4())
            self._create_session(session_id)
            return {
                "show_banner": True,
                "session_id": session_id,
                "is_new_session": True
            }
        
        # Check existing session
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT rulebook_banner_shown
                FROM session_state
                WHERE session_id = ?
            """, (session_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row is None:
                # Session doesn't exist, create it
                self._create_session(session_id)
                return {
                    "show_banner": True,
                    "session_id": session_id,
                    "is_new_session": True
                }
            else:
                # Session exists, check if banner was shown
                banner_shown = bool(row[0])
                return {
                    "show_banner": not banner_shown,
                    "session_id": session_id,
                    "is_new_session": False
                }
        
        except sqlite3.Error as e:
            self.logger.error(f"Session check failed: {e}")
            raise
    
    def _create_session(self, session_id: str) -> None:
        """
        Create a new session entry in the database.
        
        Args:
            session_id: Unique session identifier
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute("""
                INSERT INTO session_state (
                    session_id,
                    rulebook_banner_shown,
                    first_interaction_time,
                    last_updated
                ) VALUES (?, 0, ?, ?)
            """, (session_id, now, now))
            
            conn.commit()
            conn.close()
            
            self.logger.debug(f"Created new session: {session_id}")
            
        except sqlite3.Error as e:
            self.logger.error(f"Session creation failed: {e}")
            raise
    
    def _mark_banner_shown(self, session_id: str) -> Dict[str, Any]:
        """
        Mark that banner has been shown for this session.
        
        Args:
            session_id: Session identifier
        
        Returns:
            Dict with confirmation status
        """
        if not session_id:
            raise ValueError("session_id is required to mark banner as shown")
        
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            now = datetime.now().isoformat()
            
            cursor.execute("""
                UPDATE session_state
                SET rulebook_banner_shown = 1,
                    last_updated = ?
                WHERE session_id = ?
            """, (now, session_id))
            
            rows_updated = cursor.rowcount
            conn.commit()
            conn.close()
            
            if rows_updated == 0:
                raise ValueError(f"Session {session_id} not found")
            
            self.logger.debug(f"Marked banner as shown for session: {session_id}")
            
            return {
                "success": True,
                "session_id": session_id,
                "banner_shown": True
            }
            
        except sqlite3.Error as e:
            self.logger.error(f"Failed to mark banner as shown: {e}")
            raise
    
    def _get_banner_content(self) -> Dict[str, Any]:
        """
        Get formatted banner content for display.
        
        Returns:
            Dict with banner text and metadata
        """
        banner_text = """
╔══════════════════════════════════════════════════════════════════════════╗
║                  🧠 CORTEX GOVERNANCE RULES ACTIVE                       ║
╔══════════════════════════════════════════════════════════════════════════╗

CORTEX operates under strict governance rules to ensure quality and safety.

📋 KEY RULES:
- All feature work requires Definition of Ready (DoR) before starting
- All completions require Definition of Done (DoD) validation
- Git checkpoint required before high-risk operations
- Test coverage ≥80% for all production code
- Architecture review for structural changes

📖 QUICK ACCESS:
- Say "show rules" or "rulebook" to see full governance document
- Say "help" to see available commands (includes governance section)
- Say "compliance" to check your current compliance status

✨ DISMISSAL:
- This banner appears once per session
- Say "got it" or continue with your request to proceed

Full Rulebook: cortex-brain/brain-protection-rules.yaml
╚══════════════════════════════════════════════════════════════════════════╝
"""
        
        return {
            "banner_text": banner_text.strip(),
            "dismissal_phrases": ["got it", "show rules", "rulebook", "help", "compliance"],
            "rulebook_path": "cortex-brain/brain-protection-rules.yaml"
        }
    
    def get_session_stats(self) -> Dict[str, Any]:
        """
        Get statistics about session banner displays.
        
        Returns:
            Dict with session metrics:
                - total_sessions: Total number of sessions
                - banners_shown: Sessions where banner was shown
                - sessions_active: Sessions where banner not yet shown
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT 
                    COUNT(*) as total_sessions,
                    SUM(CASE WHEN rulebook_banner_shown = 1 THEN 1 ELSE 0 END) as banners_shown,
                    SUM(CASE WHEN rulebook_banner_shown = 0 THEN 1 ELSE 0 END) as sessions_active
                FROM session_state
            """)
            
            row = cursor.fetchone()
            conn.close()
            
            return {
                "total_sessions": row[0] or 0,
                "banners_shown": row[1] or 0,
                "sessions_active": row[2] or 0
            }
            
        except sqlite3.Error as e:
            self.logger.error(f"Failed to get session stats: {e}")
            return {
                "total_sessions": 0,
                "banners_shown": 0,
                "sessions_active": 0,
                "error": str(e)
            }
