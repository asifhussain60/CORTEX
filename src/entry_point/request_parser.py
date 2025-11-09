"""
Request Parser for CORTEX Entry Point

Parses user messages into structured AgentRequest objects.
Extracts intent, context, priority, files, and other metadata
from natural language input.
"""

from typing import Dict, Any, Optional, List
import re
from datetime import datetime
from pathlib import Path

from src.cortex_agents.base_agent import AgentRequest
from src.cortex_agents.agent_types import Priority
from src.cortex_agents.utils import (
    extract_file_paths,
    extract_code_intent,
    parse_priority_keywords
)


class RequestParser:
    """
    Parses user messages into structured agent requests.
    
    The RequestParser analyzes natural language input to extract:
    - Intent classification
    - File paths and context
    - Priority keywords
    - Conversation ID for resumption
    - Additional metadata
    
    Example:
        parser = RequestParser()
        
        request = parser.parse(
            "Fix the bug in src/auth.py - this is urgent!",
            conversation_id="conv-123"
        )
        
        # Returns AgentRequest with:
        # - intent: "fix"
        # - context: {"files": ["src/auth.py"]}
        # - priority: CRITICAL (1)
        # - user_message: original message
    """
    
    # Keywords for intent classification
    INTENT_KEYWORDS = {
        "setup": ["setup", "initialize", "install", "configure", "run setup"],
        "health_check": ["health", "status", "check system", "validate system"],
        "plan": ["plan", "design", "architect", "outline", "breakdown", "organize"],
        "code": ["code", "implement", "create", "build", "develop", "write"],
        "test": ["test", "tdd", "verify", "validate", "check"],
        "fix": ["fix", "debug", "resolve", "correct", "repair"],
        "review": ["review", "audit", "examine", "inspect"],
        "commit": ["commit", "save", "checkin"],
        "resume": ["resume", "continue", "restore", "recover"],
        "analyze": ["analyze", "examine", "study", "investigate"],
    }
    
    # Context extraction patterns
    CONTEXT_PATTERNS = {
        "feature": r"\b(feature|functionality|capability)\b",
        "bug": r"\b(bug|error|issue|problem)\b",
        "refactor": r"\b(refactor|restructure|reorganize)\b",
        "performance": r"\b(performance|speed|optimize|efficiency)\b",
        "security": r"\b(security|authentication|authorization|encrypt)\b",
    }
    
    def parse(
        self,
        user_message: str,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AgentRequest:
        """
        Parse user message into AgentRequest.
        
        Args:
            user_message: The user's natural language message
            conversation_id: Optional conversation ID for resumption
            metadata: Optional additional metadata
            
        Returns:
            Structured AgentRequest object
        """
        # Extract components
        intent = self._extract_intent(user_message)
        context = self._extract_context(user_message)
        priority = self._extract_priority(user_message)
        
        # Merge metadata
        if metadata:
            context.update(metadata)
        
        # Create request
        return AgentRequest(
            intent=intent,
            context=context,
            user_message=user_message,
            conversation_id=conversation_id,
            priority=priority,
            metadata={"parsed_at": datetime.now().isoformat()}
        )
    
    def _extract_intent(self, message: str) -> str:
        """
        Extract intent from message.
        
        Args:
            message: User message
            
        Returns:
            Intent string (defaults to "unknown")
        """
        message_lower = message.lower()
        
        # Check for intent keywords
        for intent, keywords in self.INTENT_KEYWORDS.items():
            for keyword in keywords:
                if re.search(rf'\b{keyword}\b', message_lower):
                    return intent
        
        # Use extract_code_intent from utils as fallback
        code_intent = extract_code_intent(message)
        if code_intent:
            return code_intent
        
        return "unknown"
    
    def _extract_context(self, message: str) -> Dict[str, Any]:
        """
        Extract context from message.
        
        Args:
            message: User message
            
        Returns:
            Context dictionary with files, features, etc.
        """
        context: Dict[str, Any] = {}
        
        # Extract file paths
        files = extract_file_paths(message)
        if files:
            context["files"] = files
        
        # Extract code blocks (between backticks)
        code_blocks = re.findall(r'```[\w]*\n(.*?)```', message, re.DOTALL)
        if code_blocks:
            context["code"] = code_blocks[0].strip()
        
        # Extract inline code (single backticks)
        inline_code = re.findall(r'`([^`]+)`', message)
        if inline_code and not files:
            # Might be file references
            potential_files = [c for c in inline_code if '.' in c and '/' in c]
            if potential_files:
                context["files"] = potential_files
        
        # Extract context type
        message_lower = message.lower()
        for ctx_type, pattern in self.CONTEXT_PATTERNS.items():
            if re.search(pattern, message_lower):
                context["type"] = ctx_type
                break
        
        # Extract specific operations
        if "delete" in message_lower or "remove" in message_lower:
            context["operation"] = "delete"
        elif "edit" in message_lower or "modify" in message_lower or "update" in message_lower:
            context["operation"] = "modify"
        elif "create" in message_lower or "add" in message_lower or "new" in message_lower:
            context["operation"] = "create"
        
        return context
    
    def _extract_priority(self, message: str) -> int:
        """
        Extract priority from message.
        
        Args:
            message: User message
            
        Returns:
            Priority level (1-5)
        """
        return parse_priority_keywords(message)
    
    def parse_batch(
        self,
        messages: List[str],
        conversation_id: Optional[str] = None
    ) -> List[AgentRequest]:
        """
        Parse multiple messages into requests.
        
        Args:
            messages: List of user messages
            conversation_id: Optional conversation ID
            
        Returns:
            List of AgentRequest objects
        """
        return [
            self.parse(msg, conversation_id)
            for msg in messages
        ]
    
    def extract_files_from_context(self, context: Dict[str, Any]) -> List[str]:
        """
        Extract file list from context.
        
        Args:
            context: Context dictionary
            
        Returns:
            List of file paths
        """
        files = context.get("files", [])
        if isinstance(files, str):
            return [files]
        return files if isinstance(files, list) else []
    
    def infer_agent_type(self, request: AgentRequest) -> str:
        """
        Infer which agent type should handle this request.
        
        This is a helper for routing decisions.
        
        Args:
            request: The parsed request
            
        Returns:
            Suggested agent type name
        """
        intent = request.intent
        
        # Direct mappings
        mapping = {
            "setup": "CortexSetup",
            "plan": "WorkPlanner",
            "code": "CodeExecutor",
            "test": "TestGenerator",
            "fix": "ErrorCorrector",
            "health_check": "HealthValidator",
            "commit": "CommitHandler",
            "resume": "SessionResumer",
            "analyze": "ScreenshotAnalyzer",
            "review": "ChangeGovernor",
        }
        
        return mapping.get(intent, "IntentRouter")
    
    def validate_request(self, request: AgentRequest) -> tuple[bool, Optional[str]]:
        """
        Validate that request has required fields.
        
        Args:
            request: The request to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check user message
        if not request.user_message or not request.user_message.strip():
            return False, "User message is required"
        
        # Check intent
        if not request.intent:
            return False, "Intent is required"
        
        # Warn about unknown intent (but allow it)
        if request.intent == "unknown":
            return True, "Intent could not be determined - will route to IntentRouter"
        
        return True, None
