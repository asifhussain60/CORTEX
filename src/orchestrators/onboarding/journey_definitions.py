"""Journey Definitions & Customization."""
from typing import Dict, List, Any
from dataclasses import dataclass

@dataclass
class JourneyDefinition:
    journey_id: str; name: str; role: str; activities: List[str]; checkpoints: int

class JourneyManager:
    """Manages YAML-first journey definitions."""
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
