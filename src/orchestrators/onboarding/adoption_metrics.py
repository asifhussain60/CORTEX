"""Adoption Metrics & Analytics Collection."""
from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AdoptionMetrics:
    journeys_started: int; journeys_completed: int; tools_discovered: int; help_requests: int

class MetricsCollector:
    """Collects adoption metrics and analytics."""
    def __init__(self):
        self.metrics: Dict[str, AdoptionMetrics] = {}
        self.events = []
    
    def create_user_metrics(self, user_id: str) -> bool:
        if user_id in self.metrics: return False
        self.metrics[user_id] = AdoptionMetrics(0, 0, 0, 0)
        return True
    
    def record_event(self, user_id: str, event_type: str, data: Dict[str, Any]) -> bool:
        if user_id not in self.metrics: return False
        self.events.append({'user_id': user_id, 'event': event_type, 'data': data, 'ts': datetime.now().isoformat()})
        
        if event_type == 'journey_started':
            self.metrics[user_id].journeys_started += 1
        elif event_type == 'journey_completed':
            self.metrics[user_id].journeys_completed += 1
        elif event_type == 'tool_discovered':
            self.metrics[user_id].tools_discovered += 1
        elif event_type == 'help_requested':
            self.metrics[user_id].help_requests += 1
        return True
    
    def get_metrics(self, user_id: str) -> Any:
        return self.metrics.get(user_id)
    
    def get_adoption_dashboard(self) -> Dict[str, Any]:
        total_started = sum(m.journeys_started for m in self.metrics.values())
        total_completed = sum(m.journeys_completed for m in self.metrics.values())
        total_users = len(self.metrics)
        completion_rate = total_completed / total_started if total_started > 0 else 0
        return {'total_users': total_users, 'journeys_started': total_started, 'journeys_completed': total_completed, 'completion_rate': completion_rate}
