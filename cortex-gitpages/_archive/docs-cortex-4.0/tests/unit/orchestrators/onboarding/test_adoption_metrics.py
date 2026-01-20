"""Adoption Metrics & Analytics tests."""
import pytest
from typing import Dict, Any
from dataclasses import dataclass
from datetime import datetime

@dataclass
class AdoptionMetrics:
    journeys_started: int; journeys_completed: int; tools_discovered: int; help_requests: int

class MetricsCollector:
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

class TestMetrics:
    def setup_method(self):
        self.collector = MetricsCollector()
    
    def test_create_user_metrics(self):
        assert self.collector.create_user_metrics("user1") is True
    
    def test_record_journey_started(self):
        self.collector.create_user_metrics("user1")
        assert self.collector.record_event("user1", "journey_started", {}) is True
        assert self.collector.get_metrics("user1").journeys_started == 1
    
    def test_record_journey_completed(self):
        self.collector.create_user_metrics("user1")
        self.collector.record_event("user1", "journey_started", {})
        self.collector.record_event("user1", "journey_completed", {})
        assert self.collector.get_metrics("user1").journeys_completed == 1
    
    def test_record_tool_discovered(self):
        self.collector.create_user_metrics("user1")
        self.collector.record_event("user1", "tool_discovered", {'tool': 't1'})
        assert self.collector.get_metrics("user1").tools_discovered == 1
    
    def test_record_help_requested(self):
        self.collector.create_user_metrics("user1")
        self.collector.record_event("user1", "help_requested", {'topic': 'help'})
        assert self.collector.get_metrics("user1").help_requests == 1
    
    def test_adoption_dashboard(self):
        self.collector.create_user_metrics("user1")
        self.collector.create_user_metrics("user2")
        self.collector.record_event("user1", "journey_started", {})
        self.collector.record_event("user1", "journey_completed", {})
        self.collector.record_event("user2", "journey_started", {})
        
        dashboard = self.collector.get_adoption_dashboard()
        assert dashboard['total_users'] == 2
        assert dashboard['journeys_started'] == 2
        assert dashboard['journeys_completed'] == 1
        assert dashboard['completion_rate'] == 0.5
