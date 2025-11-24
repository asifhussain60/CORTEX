"""Task templates and generation strategies."""

from typing import Dict, Any, List
from ...base_agent import AgentRequest


class TaskGenerator:
    """Generates tasks from templates and patterns."""
    
    def __init__(self):
        """Initialize task templates."""
        self.TASK_TEMPLATES = {
            "api_endpoint": [
                {"name": "Define route/endpoint", "base_hours": 0.5},
                {"name": "Implement handler logic", "base_hours": 1.5},
                {"name": "Add validation", "base_hours": 1.0},
                {"name": "Create tests", "base_hours": 1.0},
                {"name": "Update documentation", "base_hours": 0.5}
            ],
            "model_creation": [
                {"name": "Define model schema", "base_hours": 1.0},
                {"name": "Add model methods", "base_hours": 1.5},
                {"name": "Create migrations", "base_hours": 0.5},
                {"name": "Write model tests", "base_hours": 1.0}
            ],
            "authentication": [
                {"name": "Create User model", "base_hours": 1.5},
                {"name": "Implement login/logout", "base_hours": 2.0},
                {"name": "Add password hashing", "base_hours": 1.0},
                {"name": "Create session management", "base_hours": 1.5},
                {"name": "Add authentication tests", "base_hours": 2.0}
            ],
            "ui_component": [
                {"name": "Create component structure", "base_hours": 1.0},
                {"name": "Implement component logic", "base_hours": 2.0},
                {"name": "Add styling", "base_hours": 1.0},
                {"name": "Create component tests", "base_hours": 1.5}
            ]
        }
    
    def match_template(self, request: AgentRequest) -> List[Dict[str, Any]]:
        """Match request to a task template."""
        message_lower = request.user_message.lower()
        
        if any(word in message_lower for word in ["api", "endpoint", "route"]):
            return [dict(task) for task in self.TASK_TEMPLATES["api_endpoint"]]
        
        if any(word in message_lower for word in ["model", "schema", "database"]):
            return [dict(task) for task in self.TASK_TEMPLATES["model_creation"]]
        
        if any(word in message_lower for word in ["auth", "login", "user", "password"]):
            return [dict(task) for task in self.TASK_TEMPLATES["authentication"]]
        
        if any(word in message_lower for word in ["component", "ui", "interface"]):
            return [dict(task) for task in self.TASK_TEMPLATES["ui_component"]]
        
        return []
    
    def create_generic_breakdown(self, request: AgentRequest, complexity: str) -> List[Dict[str, Any]]:
        """Create generic task breakdown based on complexity."""
        base_tasks = [
            {"name": "Research and planning", "base_hours": 1.0},
            {"name": "Implementation", "base_hours": 3.0},
            {"name": "Testing", "base_hours": 1.5},
            {"name": "Documentation", "base_hours": 0.5}
        ]
        
        # Adjust for complexity
        if complexity == "simple":
            multiplier = 0.5
        elif complexity == "complex":
            multiplier = 2.0
            base_tasks.insert(1, {"name": "Design architecture", "base_hours": 2.0})
            base_tasks.append({"name": "Integration testing", "base_hours": 1.5})
        else:
            multiplier = 1.0
        
        # Apply multiplier
        for task in base_tasks:
            task["base_hours"] *= multiplier
        
        return base_tasks
