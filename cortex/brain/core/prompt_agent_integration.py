"""
Prompt/Agent Integration.

CORTEX.prompt.md integration, agent lazy loading,
response format compliance, and exit gate validation.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 33 Stage 5 specification
"""

import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional, List

logger = logging.getLogger(__name__)


class IntegrationError(Exception):
    """Base exception for integration errors."""
    pass


class ResponseFormat:
    """
    Response format validator and formatter.
    
    Ensures all responses follow response-format-standards.md.
    """
    
    REQUIRED_HEADER_PATTERN = r"##\s*🧠\s*CORTEX"
    
    def validate(self, response: str) -> bool:
        """
        Validate response format.
        
        Args:
            response: Response text to validate
            
        Returns:
            bool: True if valid format
        """
        if not response or not isinstance(response, str):
            return False
        
        # Check for CORTEX header
        has_header = bool(re.search(self.REQUIRED_HEADER_PATTERN, response))
        
        return has_header
    
    def add_header(self, content: str, orchestrator: str) -> str:
        """
        Add CORTEX header to content.
        
        Args:
            content: Content to format
            orchestrator: Orchestrator name
            
        Returns:
            str: Formatted content with header
        """
        header = f"""## 🧠 CORTEX Implementation
**Author:** Asif Hussain | **Orchestrator:** {orchestrator} ✅

---

"""
        return header + content


class AgentLoader:
    """
    Agent lazy loader.
    
    Loads agents on-demand based on intent, implements caching.
    """
    
    # Intent to agent mapping
    INTENT_AGENT_MAP = {
        "IMPLEMENT": "TDDAgent",
        "FIX": "TDDAgent",
        "REFACTOR": "RefactoringAgent",
        "ANALYZE": "LENSAgent",
        "TEST": "TDDAgent",
        "AUDIT": "AuditAgent",
        "DESIGN": "ArchitectAgent",
    }
    
    def __init__(self):
        """Initialize agent loader."""
        self._loaded_agents: Dict[str, Any] = {}
        logger.info("AgentLoader initialized")
    
    def is_loaded(self, agent_name: str) -> bool:
        """
        Check if agent is already loaded.
        
        Args:
            agent_name: Name of agent
            
        Returns:
            bool: True if loaded
        """
        return agent_name in self._loaded_agents
    
    def load_agent(self, agent_name: str, intent: str) -> Optional[Any]:
        """
        Load agent on demand.
        
        Args:
            agent_name: Name of agent to load
            intent: Intent triggering load
            
        Returns:
            Optional[Any]: Loaded agent or None
        """
        # Check cache first
        if self.is_loaded(agent_name):
            logger.debug(f"Agent {agent_name} already loaded (cache hit)")
            return self._loaded_agents[agent_name]
        
        # Simulate agent loading (production would load actual agent)
        logger.info(f"Loading agent: {agent_name} for intent: {intent}")
        
        # Create placeholder agent
        agent = {
            "name": agent_name,
            "intent": intent,
            "loaded": True,
        }
        
        # Cache agent
        self._loaded_agents[agent_name] = agent
        
        return agent
    
    def get_agent_for_intent(self, intent: str) -> str:
        """
        Get agent name for intent.
        
        Args:
            intent: Intent type
            
        Returns:
            str: Agent name
        """
        return self.INTENT_AGENT_MAP.get(intent, "MasterAgent")


class ExitGate:
    """
    Exit gate validator.
    
    Validates task completion, detects markdown vacuum candidates.
    """
    
    # Vacuum patterns (files that should be cleaned up)
    VACUUM_PATTERNS = [
        r"PHASE-\d+.*\.md",  # Any PHASE-* markdown files
        r".*-report\.md",
        r".*-summary\.md",
        r"completion-.*\.md",
    ]
    
    # Preserve patterns (legitimate docs)
    PRESERVE_PATTERNS = [
        r"README\.md",
        r"docs/.*\.md",
        r"\.github/.*\.md",
        r"LICENSE\.md",
    ]
    
    def validate(self, result: Dict[str, Any]) -> bool:
        """
        Validate completion result.
        
        Args:
            result: Execution result
            
        Returns:
            bool: True if passes exit gate
        """
        success = result.get("success", False)
        violations = result.get("violations", 0)
        
        # Must be successful with no violations
        passed = success and violations == 0
        
        return passed
    
    def detect_vacuum_candidates(self, files: List[str]) -> List[str]:
        """
        Detect files that should be vacuumed (ENH-036).
        
        Args:
            files: List of file paths
            
        Returns:
            List[str]: Files to vacuum
        """
        candidates = []
        
        for file_path in files:
            # Skip if matches preserve pattern
            if any(re.match(pattern, file_path) for pattern in self.PRESERVE_PATTERNS):
                continue
            
            # Check if matches vacuum pattern
            if any(re.search(pattern, file_path) for pattern in self.VACUUM_PATTERNS):
                candidates.append(file_path)
        
        return candidates


class PromptAgentIntegration:
    """
    Prompt/Agent Integration System.
    
    Coordinates prompt loading, agent management, response formatting,
    and exit gate validation.
    """
    
    def __init__(self):
        """Initialize integration system."""
        self.formatter = ResponseFormat()
        self.agent_loader = AgentLoader()
        self.exit_gate = ExitGate()
        
        logger.info("PromptAgentIntegration initialized")
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process request with full integration.
        
        Args:
            request: Request to process
            
        Returns:
            Dict: Response with formatted output
        """
        intent = request.get("intent", "ANALYZE")
        user_input = request.get("user_input", "")
        
        # Load appropriate agent
        agent_name = self.agent_loader.get_agent_for_intent(intent)
        agent = self.agent_loader.load_agent(agent_name, intent)
        
        # Process (placeholder)
        content = f"Processed {intent} intent: {user_input[:50]}..."
        
        # Format response
        formatted_output = self.formatter.add_header(content, agent_name)
        
        return {
            "orchestrator": agent_name,
            "formatted_output": formatted_output,
            "intent": intent,
        }
    
    def validate_completion(self, result: Dict[str, Any]) -> bool:
        """
        Validate completion via exit gate.
        
        Args:
            result: Execution result
            
        Returns:
            bool: True if passes exit gate
        """
        return self.exit_gate.validate(result)
    
    def load_prompt(self, prompt_name: str) -> Optional[str]:
        """
        Load prompt from .github/prompts/.
        
        Args:
            prompt_name: Name of prompt file
            
        Returns:
            Optional[str]: Prompt content or None
        """
        prompt_path = Path(".github/prompts") / prompt_name
        
        try:
            if prompt_path.exists():
                with open(prompt_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.info(f"Loaded prompt: {prompt_name}")
                return content
            else:
                logger.warning(f"Prompt not found: {prompt_name}")
                return None
        except Exception as e:
            logger.error(f"Error loading prompt {prompt_name}: {e}")
            return None
