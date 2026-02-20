"""Journey Definitions & Customization tests."""
import pytest
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class JourneyDefinition:
    journey_id: str; name: str; role: str; activities: List[str]; checkpoints: int

class JourneyManager:
    def __init__(self):
        self.journeys: Dict[str, JourneyDefinition] = {}
        self.journey_yaml = {}
    
    def register_journey(self, definition: JourneyDefinition) -> bool:
        if definition.journey_id in self.journeys: return False
        self.journeys[definition.journey_id] = definition
        return True
    
    def get_journeys_by_role(self, role: str) -> List[JourneyDefinition]:
        return [j for j in self.journeys.values() if j.role == role or j.role == "general"]
    
    def load_journey_yaml(self, journey_id: str, yaml_config: Dict[str, Any]) -> bool:
        if journey_id not in self.journeys: return False
        self.journey_yaml[journey_id] = yaml_config
        return True
    
    def validate_journey_sequence(self, journey_id: str) -> bool:
        if journey_id not in self.journey_yaml: return False
        config = self.journey_yaml[journey_id]
        return 'activities' in config and len(config['activities']) > 0

class TestJourneyDefinitions:
    def setup_method(self):
        self.manager = JourneyManager()
    
    def test_register_journey(self):
        j = JourneyDefinition("j1", "Standard", "general", ["a1", "a2"], 2)
        assert self.manager.register_journey(j) is True
    
    def test_get_journeys_by_role(self):
        j1 = JourneyDefinition("j1", "Developer", "developer", ["a1"], 1)
        self.manager.register_journey(j1)
        journeys = self.manager.get_journeys_by_role("developer")
        assert len(journeys) == 1
    
    def test_load_journey_yaml(self):
        j = JourneyDefinition("j1", "Test", "general", [], 0)
        self.manager.register_journey(j)
        yaml_config = {'activities': ['a1', 'a2'], 'checkpoints': 2}
        assert self.manager.load_journey_yaml("j1", yaml_config) is True
    
    def test_validate_journey_sequence(self):
        j = JourneyDefinition("j1", "Test", "general", [], 0)
        self.manager.register_journey(j)
        yaml_config = {'activities': ['a1', 'a2']}
        self.manager.load_journey_yaml("j1", yaml_config)
        assert self.manager.validate_journey_sequence("j1") is True
    
    def test_six_base_journeys(self):
        journeys = [
            JourneyDefinition("standard", "Standard Onboarding", "general", ["intro", "tools", "survey"], 3),
            JourneyDefinition("beginner", "Beginner-Friendly", "general", ["basics", "simple"], 2),
            JourneyDefinition("advanced", "Advanced", "general", ["complex", "integration"], 2),
            JourneyDefinition("analyst", "Analyst-Role", "analyst", ["data", "analysis"], 2),
            JourneyDefinition("developer", "Developer-Role", "developer", ["code", "integration"], 2),
            JourneyDefinition("pm", "PM-Role", "pm", ["planning", "roadmap"], 2),
        ]
        for j in journeys:
            assert self.manager.register_journey(j) is True
        assert len(self.manager.journeys) == 6
