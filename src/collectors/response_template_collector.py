"""
CORTEX 3.0 - Response Template Metrics Collector
===============================================

Collects real-time metrics on response template usage and performance.
Tracks which templates are used, response quality, and effectiveness.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.

Feature: Quick Win #3 (Week 1)
Effort: 1 hour (response template collector)
Target: Template usage analytics and optimization
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import json
from pathlib import Path

from .base_collector import BaseCollector, CollectorMetric, CollectorPriority


class ResponseTemplateMetricsCollector(BaseCollector):
    """
    Collects metrics on response template usage and performance.
    
    Metrics collected:
    - Template usage frequency
    - Response generation time
    - Template effectiveness scores
    - User feedback patterns
    - Template fallback rates
    """
    
    def __init__(self, brain_path: Optional[str] = None):
        super().__init__(
            collector_id="response_templates",
            name="Response Template Metrics",
            priority=CollectorPriority.CRITICAL,
            collection_interval_seconds=30.0,  # Frequent collection for responsiveness
            brain_path=brain_path
        )
        
        # Template usage tracking
        self.template_usage = {}
        self.template_timings = {}
        self.template_effectiveness = {}
        self.fallback_count = 0
        self.total_responses = 0
        
        # Load response templates for reference
        self.templates = self._load_templates()
    
    def _initialize(self) -> bool:
        """Initialize template metrics collector"""
        try:
            # Verify templates are accessible
            if not self.templates:
                self.logger.warning("No response templates found, metrics will be limited")
            
            self.logger.info("Response template metrics collector initialized")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to initialize template metrics collector: {e}")
            return False
    
    def _load_templates(self) -> Dict[str, Any]:
        """Load response templates from brain"""
        try:
            if not self.brain_path:
                return {}
            
            template_file = self.brain_path / "response-templates.yaml"
            if not template_file.exists():
                return {}
            
            # For now, return empty dict - template loading would happen here
            # In a real implementation, we'd parse the YAML file
            return {}
            
        except Exception as e:
            self.logger.warning(f"Failed to load templates: {e}")
            return {}
    
    def _collect_metrics(self) -> List[CollectorMetric]:
        """Collect response template metrics"""
        metrics = []
        timestamp = datetime.now(timezone.utc)
        
        # Template usage frequency
        if self.template_usage:
            metrics.append(CollectorMetric(
                name="template_usage_frequency",
                value=dict(self.template_usage),
                timestamp=timestamp,
                tags={"type": "usage", "category": "templates"}
            ))
        
        # Average response generation times
        if self.template_timings:
            avg_timings = {
                template: sum(times) / len(times) 
                for template, times in self.template_timings.items()
            }
            metrics.append(CollectorMetric(
                name="template_response_times",
                value=avg_timings,
                timestamp=timestamp,
                tags={"type": "performance", "category": "templates"}
            ))
        
        # Template effectiveness scores
        if self.template_effectiveness:
            metrics.append(CollectorMetric(
                name="template_effectiveness",
                value=dict(self.template_effectiveness),
                timestamp=timestamp,
                tags={"type": "quality", "category": "templates"}
            ))
        
        # Fallback rate (when no template matches)
        fallback_rate = (self.fallback_count / max(self.total_responses, 1)) * 100
        metrics.append(CollectorMetric(
            name="template_fallback_rate",
            value=fallback_rate,
            timestamp=timestamp,
            tags={"type": "fallback", "category": "templates"},
            metadata={"fallback_count": self.fallback_count, "total_responses": self.total_responses}
        ))
        
        # Total template count
        metrics.append(CollectorMetric(
            name="total_templates_available",
            value=len(self.templates),
            timestamp=timestamp,
            tags={"type": "inventory", "category": "templates"}
        ))
        
        return metrics
    
    # Public methods for tracking template usage (called by response system)
    
    def track_template_usage(self, template_name: str, response_time_ms: float) -> None:
        """Track usage of a specific template"""
        # Update usage count
        self.template_usage[template_name] = self.template_usage.get(template_name, 0) + 1
        
        # Track response time
        if template_name not in self.template_timings:
            self.template_timings[template_name] = []
        self.template_timings[template_name].append(response_time_ms)
        
        # Keep only recent timings (last 100)
        if len(self.template_timings[template_name]) > 100:
            self.template_timings[template_name] = self.template_timings[template_name][-100:]
        
        self.total_responses += 1
    
    def track_fallback_usage(self) -> None:
        """Track when no template matched (fallback scenario)"""
        self.fallback_count += 1
        self.total_responses += 1
    
    def track_template_effectiveness(self, template_name: str, effectiveness_score: float) -> None:
        """Track how effective a template was (0.0 - 1.0)"""
        if template_name not in self.template_effectiveness:
            self.template_effectiveness[template_name] = []
        
        self.template_effectiveness[template_name].append(effectiveness_score)
        
        # Keep only recent scores (last 50)
        if len(self.template_effectiveness[template_name]) > 50:
            self.template_effectiveness[template_name] = self.template_effectiveness[template_name][-50:]
    
    def get_template_summary(self) -> Dict[str, Any]:
        """Get summary of template metrics"""
        return {
            "total_templates": len(self.templates),
            "total_responses": self.total_responses,
            "fallback_rate": (self.fallback_count / max(self.total_responses, 1)) * 100,
            "most_used_templates": sorted(
                self.template_usage.items(), 
                key=lambda x: x[1], 
                reverse=True
            )[:5],
            "avg_response_times": {
                template: sum(times) / len(times)
                for template, times in self.template_timings.items()
            }
        }