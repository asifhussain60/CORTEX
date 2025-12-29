"""
CopilotIntegration: Optional bridge to GitHub Copilot Chat context APIs.

Provides enhanced context when available, fails gracefully when not.
"""

from pathlib import Path
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class CopilotIntegration:
    """
    Bridge to GitHub Copilot Chat context APIs.
    
    This is an OPTIONAL enhancement. CORTEX works without it.
    When available, provides:
    - Active file detection
    - Workspace folder identification
    - Git repo root
    """
    
    def __init__(self):
        self._available = False
        self._check_availability()
    
    def _check_availability(self):
        """
        Check if GitHub Copilot context is available.
        
        Note: In POC, this always returns False. In production, would check
        for Copilot Chat API integration.
        """
        # TODO: Implement actual Copilot API detection
        # For now, check if we're in a Copilot Chat context
        # This would be provided by the entry point parsing
        self._available = False
        logger.debug("Copilot integration: unavailable (POC mode)")
    
    def get_context(self) -> Optional[Dict[str, Any]]:
        """
        Get workspace context from GitHub Copilot.
        
        Returns:
            Dict with repo_root, cortex_root, active_file, etc., or None if unavailable
        """
        if not self._available:
            return None
        
        try:
            # TODO: Implement actual Copilot API calls
            # Would parse Copilot Chat context parameters like:
            # - #file references
            # - @workspace scope
            # - Active editor context
            
            # POC: Return None (graceful degradation)
            return None
        
        except Exception as e:
            logger.debug(f"Copilot context unavailable: {e}")
            return None
    
    def parse_chat_params(self, chat_params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Parse context from GitHub Copilot Chat parameters.
        
        This would be called by CORTEX entry point when invoked via Copilot Chat.
        
        Args:
            chat_params: Parameters from Copilot Chat (file references, workspace, etc.)
        
        Returns:
            Parsed context dict or None
        """
        try:
            # Extract active file
            active_file = chat_params.get('active_file')
            if active_file:
                active_file = Path(active_file)
            
            # Extract workspace folders
            workspace_folders = chat_params.get('workspace_folders', [])
            
            # Find CORTEX folder (has cortex-brain/)
            cortex_root = None
            for folder in workspace_folders:
                folder_path = Path(folder)
                if (folder_path / "cortex-brain").exists():
                    cortex_root = folder_path
                    break
            
            # Find repo root (folder containing active file or current workspace)
            repo_root = None
            if active_file:
                # Walk up from active file to find git root
                current = active_file.parent
                while current != current.parent:
                    if (current / ".git").exists():
                        repo_root = current
                        break
                    current = current.parent
            
            if not repo_root and workspace_folders:
                # Use first non-CORTEX workspace folder
                for folder in workspace_folders:
                    folder_path = Path(folder)
                    if folder_path != cortex_root:
                        repo_root = folder_path
                        break
            
            if repo_root and cortex_root:
                return {
                    'repo_root': repo_root,
                    'cortex_root': cortex_root,
                    'active_file': active_file,
                    'workspace_folders': [Path(f) for f in workspace_folders],
                }
            
            return None
        
        except Exception as e:
            logger.debug(f"Failed to parse Copilot Chat params: {e}")
            return None
    
    @property
    def available(self) -> bool:
        """Check if Copilot integration is available."""
        return self._available
