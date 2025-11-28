"""
Wiring Validator - Entry Point Mapping Validation

Validates that orchestrators are properly wired to entry points:
- Checks trigger → orchestrator mapping
- Detects orphaned triggers (no orchestrator)
- Detects ghost features (orchestrator but no trigger)
- Validates naming conventions
- Validates documented commands have routing triggers

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
import re
import yaml
from pathlib import Path
from typing import Dict, Any, List, Set, Tuple

logger = logging.getLogger(__name__)


class WiringValidator:
    """
    Entry point wiring validator.
    
    Validates that all user-facing entry points (response templates)
    are properly connected to orchestrator implementations.
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize wiring validator.
        
        Args:
            project_root: Root directory of CORTEX project
        """
        self.project_root = Path(project_root)
        self._documented_commands_cache = None
        self._routing_triggers_cache = None
    
    def validate_wiring(
        self,
        discovered_orchestrators: Dict[str, Dict[str, Any]],
        entry_points: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Validate entry point wiring.
        
        Args:
            discovered_orchestrators: Dict of discovered orchestrators
            entry_points: Dict of entry points from templates
        
        Returns:
            Validation results with orphaned/ghost features
        """
        results = {
            "total_entry_points": len(entry_points),
            "total_orchestrators": len(discovered_orchestrators),
            "wired_orchestrators": set(),
            "orphaned_triggers": [],
            "ghost_features": [],
            "wiring_suggestions": []
        }
        
        # Check each entry point
        for trigger, metadata in entry_points.items():
            expected_orch = metadata.get("expected_orchestrator")
            
            if not expected_orch:
                # No orchestrator expected (e.g., help commands)
                continue
            
            if expected_orch in discovered_orchestrators:
                # Properly wired
                results["wired_orchestrators"].add(expected_orch)
            else:
                # Orphaned trigger
                results["orphaned_triggers"].append({
                    "trigger": trigger,
                    "expected_orchestrator": expected_orch,
                    "template": metadata.get("template")
                })
                
                # Generate suggestion
                suggestion = self._generate_wiring_suggestion(trigger, expected_orch)
                results["wiring_suggestions"].append(suggestion)
        
        # Check for ghost features (orchestrators without entry points)
        for orch_name in discovered_orchestrators.keys():
            # Skip admin-only orchestrators
            if "admin" in orch_name.lower() or "system" in orch_name.lower():
                continue
            
            if orch_name not in results["wired_orchestrators"]:
                results["ghost_features"].append({
                    "orchestrator": orch_name,
                    "suggestion": f"Add entry point trigger for {orch_name}"
                })
        
        results["wired_count"] = len(results["wired_orchestrators"])
        results["orphaned_count"] = len(results["orphaned_triggers"])
        results["ghost_count"] = len(results["ghost_features"])
        
        return results
    
    def _generate_wiring_suggestion(self, trigger: str, orchestrator_name: str) -> Dict[str, str]:
        """
        Generate wiring suggestion for orphaned trigger.
        
        Args:
            trigger: Trigger phrase
            orchestrator_name: Expected orchestrator name
        
        Returns:
            Suggestion dict with code snippet
        """
        # Extract feature name from orchestrator
        feature_name = orchestrator_name.replace("Orchestrator", "").lower()
        
        return {
            "trigger": trigger,
            "orchestrator": orchestrator_name,
            "action": "create_orchestrator",
            "template": f"""
# Create missing orchestrator: {orchestrator_name}

from src.operations.base_operation_module import BaseOperationModule, OperationResult, OperationStatus

class {orchestrator_name}(BaseOperationModule):
    \"\"\"
    {feature_name.replace('_', ' ').title()} orchestrator.
    
    Triggered by: {trigger}
    \"\"\"
    
    def get_metadata(self):
        return OperationModuleMetadata(
            module_id="{feature_name}",
            name="{feature_name.replace('_', ' ').title()}",
            description="TODO: Add description",
            phase=OperationPhase.PROCESSING
        )
    
    def execute(self, context):
        # TODO: Implement feature logic
        return OperationResult(
            success=True,
            status=OperationStatus.SUCCESS,
            message="Feature executed successfully"
        )
""".strip()
        }
    
    def check_orchestrator_wired(
        self,
        orchestrator_name: str,
        entry_points: Dict[str, Dict[str, Any]]
    ) -> bool:
        """
        Check if specific orchestrator is wired to entry point.
        
        Args:
            orchestrator_name: Orchestrator class name
            entry_points: Dict of entry points
        
        Returns:
            True if orchestrator is wired
        """
        for trigger, metadata in entry_points.items():
            expected = metadata.get("expected_orchestrator")
            if expected == orchestrator_name:
                return True
        
        return False
    
    def get_wiring_status(
        self,
        orchestrator_name: str,
        entry_points: Dict[str, Dict[str, Any]]
    ) -> str:
        """
        Get wiring status for orchestrator.
        
        Args:
            orchestrator_name: Orchestrator class name
            entry_points: Dict of entry points
        
        Returns:
            Status: 'wired', 'unwired', or 'admin'
        """
        # Check if admin-only
        if "admin" in orchestrator_name.lower() or "system" in orchestrator_name.lower():
            return "admin"
        
        # Check if wired
        if self.check_orchestrator_wired(orchestrator_name, entry_points):
            return "wired"
        
        return "unwired"
    
    def validate_command_documentation(self) -> Dict[str, Any]:
        """
        Validate that all documented commands have routing triggers.
        
        Scans CORTEX.prompt.md for documented commands (- `command` - description)
        and verifies each has corresponding routing triggers in response-templates.yaml.
        
        Returns:
            Validation results with documented_but_not_routed commands
        """
        results = {
            "total_documented_commands": 0,
            "commands_with_routing": 0,
            "documented_but_not_routed": [],
            "validation_passed": True
        }
        
        try:
            # Extract documented commands from CORTEX.prompt.md
            documented_commands = self._extract_documented_commands()
            results["total_documented_commands"] = len(documented_commands)
            
            # Get routing triggers from response-templates.yaml
            routing_triggers = self._extract_routing_triggers()
            
            # Cross-reference
            for cmd_info in documented_commands:
                command = cmd_info["command"]
                description = cmd_info["description"]
                source_file = cmd_info["source_file"]
                
                # Check if command appears in any routing trigger
                found_in_routing = False
                for trigger_group, triggers in routing_triggers.items():
                    for trigger in triggers:
                        if command.lower() in trigger.lower() or trigger.lower() in command.lower():
                            found_in_routing = True
                            break
                    if found_in_routing:
                        break
                
                if found_in_routing:
                    results["commands_with_routing"] += 1
                else:
                    results["documented_but_not_routed"].append({
                        "command": command,
                        "description": description,
                        "source_file": source_file,
                        "suggested_trigger_group": self._suggest_trigger_group_name(command)
                    })
                    results["validation_passed"] = False
            
        except Exception as e:
            logger.error(f"Command documentation validation failed: {e}")
            results["error"] = str(e)
            results["validation_passed"] = False
        
        return results
    
    def _extract_documented_commands(self) -> List[Dict[str, str]]:
        """
        Extract documented commands from CORTEX.prompt.md.
        
        Looks for patterns like:
        - `command name` - Description
        
        Returns:
            List of command dictionaries with command, description, source_file
        """
        if self._documented_commands_cache is not None:
            return self._documented_commands_cache
        
        commands = []
        prompt_file = self.project_root / ".github" / "prompts" / "CORTEX.prompt.md"
        
        if not prompt_file.exists():
            logger.warning(f"CORTEX.prompt.md not found at {prompt_file}")
            self._documented_commands_cache = commands
            return commands
        
        try:
            content = prompt_file.read_text(encoding='utf-8')
            # Pattern: - `command` - description
            pattern = r'^\s*-\s*`([^`]+)`\s*-\s*(.+)$'
            
            for line in content.split('\n'):
                match = re.match(pattern, line)
                if match:
                    command = match.group(1).strip()
                    description = match.group(2).strip()
                    
                    # Skip non-command entries (examples, placeholders)
                    if any(skip in command.lower() for skip in ['[', 'example', 'todo', 'tbd']):
                        continue
                    
                    commands.append({
                        "command": command,
                        "description": description,
                        "source_file": "CORTEX.prompt.md"
                    })
            
            self._documented_commands_cache = commands
            logger.info(f"Extracted {len(commands)} documented commands from CORTEX.prompt.md")
            
        except Exception as e:
            logger.error(f"Failed to extract documented commands: {e}")
        
        return commands
    
    def _extract_routing_triggers(self) -> Dict[str, List[str]]:
        """
        Extract routing triggers from response-templates.yaml.
        
        Returns:
            Dict mapping trigger group names to lists of trigger phrases
        """
        if self._routing_triggers_cache is not None:
            return self._routing_triggers_cache
        
        routing_triggers = {}
        templates_file = self.project_root / "cortex-brain" / "response-templates.yaml"
        
        if not templates_file.exists():
            logger.warning(f"response-templates.yaml not found at {templates_file}")
            self._routing_triggers_cache = routing_triggers
            return routing_triggers
        
        try:
            with open(templates_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Extract routing section
            routing = data.get('routing', {})
            
            for key, value in routing.items():
                if key.endswith('_triggers') and isinstance(value, list):
                    routing_triggers[key] = value
            
            self._routing_triggers_cache = routing_triggers
            logger.info(f"Extracted {len(routing_triggers)} trigger groups from response-templates.yaml")
            
        except Exception as e:
            logger.error(f"Failed to extract routing triggers: {e}")
        
        return routing_triggers
    
    def _suggest_trigger_group_name(self, command: str) -> str:
        """
        Suggest routing trigger group name for a command.
        
        Args:
            command: Command string (e.g., 'cache status')
        
        Returns:
            Suggested trigger group name (e.g., 'cache_status_triggers')
        """
        # Clean command and convert to snake_case
        clean_cmd = command.lower()
        clean_cmd = re.sub(r'[^a-z0-9\s]', '', clean_cmd)
        clean_cmd = clean_cmd.strip().replace(' ', '_')
        
        return f"{clean_cmd}_triggers"
