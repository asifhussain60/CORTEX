"""
Command handlers for /persona and /detail commands.

Implements command parsing and execution for persona/depth management.

AC_START: AC-PHASE37.3-004
"""

from typing import Dict, Any, List, Optional
import re

from cortex.orchestrators.core.persona_loader import PersonaLoader
from cortex.orchestrators.core.depth_manager import DepthManager


class PersonaCommandHandler:
    """Handle /persona command execution."""
    
    def __init__(self):
        """Initialize command handler."""
        self.persona_loader = PersonaLoader()
        self.current_persona: Optional[str] = None
    
    def execute(self, command: str) -> Dict[str, Any]:
        """Execute /persona command.
        
        Args:
            command: Full command string (e.g., "/persona set engineer")
        
        Returns:
            Result dictionary with success, message, and relevant data
        """
        # Parse command
        parts = command.strip().split()
        if len(parts) < 2:
            return {
                "success": False,
                "message": "Usage: /persona [set|show|list] [persona_id]"
            }
        
        subcommand = parts[1].lower()
        
        if subcommand == "set":
            return self._handle_set(parts)
        elif subcommand == "show":
            return self._handle_show()
        elif subcommand == "list":
            return self._handle_list()
        else:
            return {
                "success": False,
                "message": f"Unknown subcommand: {subcommand}"
            }
    
    def _handle_set(self, parts: List[str]) -> Dict[str, Any]:
        """Handle /persona set command."""
        if len(parts) < 3:
            return {
                "success": False,
                "message": "Usage: /persona set <persona_id>"
            }
        
        persona_id = parts[2].lower()
        
        # Resolve alias if needed
        persona = self.persona_loader.get_persona(persona_id)
        if not persona:
            return {
                "success": False,
                "message": f"Invalid persona ID: {persona_id}. Use /persona list to see available personas."
            }
        
        self.current_persona = persona.id
        return {
            "success": True,
            "persona_id": persona.id,
            "message": f"✅ Persona set to: {persona.id.replace('_', ' ').title()}"
        }
    
    def _handle_show(self) -> Dict[str, Any]:
        """Handle /persona show command."""
        if not self.current_persona:
            persona_id = "engineer"  # Default
        else:
            persona_id = self.current_persona
        
        persona = self.persona_loader.get_persona(persona_id)
        return {
            "success": True,
            "persona_id": persona.id,
            "message": f"📋 Current persona: {persona.id.replace('_', ' ').title()}\n"
                      f"Format: {persona.format}, Code: {'Shown' if persona.show_code else 'Hidden'}"
        }
    
    def _handle_list(self) -> Dict[str, Any]:
        """Handle /persona list command."""
        personas = self.persona_loader.list_personas()
        
        return {
            "success": True,
            "personas": personas,
            "message": f"📚 Available personas:\n" + "\n".join(f"  - {p}" for p in personas)
        }


class DetailCommandHandler:
    """Handle /detail command execution."""
    
    def __init__(self):
        """Initialize command handler."""
        self.persona_loader = PersonaLoader()
        self.depth_manager = DepthManager()
    
    def execute(self, command: str) -> Dict[str, Any]:
        """Execute /detail command.
        
        Args:
            command: Full command string (e.g., "/detail set detailed 3")
        
        Returns:
            Result dictionary with success, message, and relevant data
        """
        # Parse command
        parts = command.strip().split()
        if len(parts) < 2:
            return {
                "success": False,
                "message": "Usage: /detail [set|show|reset] [depth_id] [turns]"
            }
        
        subcommand = parts[1].lower()
        
        if subcommand == "set":
            return self._handle_set(parts)
        elif subcommand == "show":
            return self._handle_show()
        elif subcommand == "reset":
            return self._handle_reset()
        else:
            return {
                "success": False,
                "message": f"Unknown subcommand: {subcommand}"
            }
    
    def _handle_set(self, parts: List[str]) -> Dict[str, Any]:
        """Handle /detail set command."""
        if len(parts) < 3:
            return {
                "success": False,
                "message": "Usage: /detail set <depth_id> [turns]"
            }
        
        depth_id = parts[2].lower()
        
        # Validate depth
        depth = self.persona_loader.get_depth_level(depth_id)
        if not depth:
            return {
                "success": False,
                "message": f"Invalid depth level: {depth_id}"
            }
        
        # Parse turns if provided
        turns = None
        if len(parts) >= 4:
            try:
                turns = int(parts[3])
            except ValueError:
                return {
                    "success": False,
                    "message": "Turns must be an integer"
                }
        
        # Set override
        if turns:
            self.depth_manager.set_override(depth_id, turns=turns)
        else:
            self.depth_manager.set_override(depth_id, sticky=True)
        
        result = {
            "success": True,
            "depth_id": depth_id,
            "message": f"✅ Detail level set to: {depth_id.title()} ({depth.word_limit} words)"
        }
        
        if turns:
            result["turns"] = turns
            result["message"] += f" for {turns} turns"
        
        return result
    
    def _handle_show(self) -> Dict[str, Any]:
        """Handle /detail show command."""
        override = self.depth_manager.get_override()
        
        if override:
            depth_id = override.depth_id
            depth = self.persona_loader.get_depth_level(depth_id)
            
            msg = f"📊 Current detail level: {depth_id.title()} ({depth.word_limit} words)"
            if not override.sticky:
                msg += f"\n   Remaining turns: {override.turns_remaining}"
            
            return {
                "success": True,
                "depth_id": depth_id,
                "message": msg
            }
        else:
            # Use persona default
            depth_id = self.depth_manager.get_persona_default() or "standard"
            depth = self.persona_loader.get_depth_level(depth_id)
            
            return {
                "success": True,
                "depth_id": depth_id,
                "message": f"📊 Current detail level: {depth_id.title()} ({depth.word_limit} words) [persona default]"
            }
    
    def _handle_reset(self) -> Dict[str, Any]:
        """Handle /detail reset command."""
        self.depth_manager.clear_override()
        
        return {
            "success": True,
            "message": "✅ Detail level reset to persona default"
        }


# AC_COMPLETE: AC-PHASE37.3-004 ✅ PersonaCommandHandler + DetailCommandHandler implemented
