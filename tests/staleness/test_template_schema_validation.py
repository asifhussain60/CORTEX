"""
Template Schema Validation Tests

Ensures response templates stay synchronized with metric collectors.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import yaml
from pathlib import Path
from typing import Dict, Set

from src.metrics.brain_metrics_collector import BrainMetricsCollector


class TestTemplateSchemaValidation:
    """Validate template placeholders match collector output."""
    
    @pytest.fixture
    def templates(self) -> Dict:
        """Load response templates."""
        template_file = Path('cortex-brain/response-templates.yaml')
        with open(template_file, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data['templates']
    
    @pytest.fixture
    def collector(self) -> BrainMetricsCollector:
        """Create metrics collector."""
        return BrainMetricsCollector()
    
    def test_schema_version_matches(self, templates):
        """Verify global schema version is defined."""
        template_file = Path('cortex-brain/response-templates.yaml')
        with open(template_file, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        assert 'schema_version' in data, "Templates must declare schema_version"
        assert data['schema_version'] == BrainMetricsCollector.SCHEMA_VERSION, \
            f"Schema mismatch: templates={data['schema_version']}, collector={BrainMetricsCollector.SCHEMA_VERSION}"
    
    def test_brain_performance_placeholders(self, templates, collector):
        """Verify brain_performance_session template placeholders exist in collector output."""
        
        template = templates['brain_performance_session']
        
        # Get collector output
        metrics = collector.get_brain_performance_metrics()
        
        # Extract required fields from template
        required_fields = template.get('required_fields', [])
        
        # Verify all required fields exist in metrics
        missing = []
        for field in required_fields:
            if field not in metrics:
                missing.append(field)
        
        assert len(missing) == 0, \
            f"Collector missing required fields: {missing}. Update BrainMetricsCollector to include these fields."
    
    def test_token_optimization_placeholders(self, templates, collector):
        """Verify token_optimization_session template placeholders exist in collector output."""
        
        template = templates['token_optimization_session']
        
        # Get collector output
        metrics = collector.get_token_optimization_metrics()
        
        # Extract required fields from template
        required_fields = template.get('required_fields', [])
        
        # Verify all required fields exist in metrics
        missing = []
        for field in required_fields:
            if field not in metrics:
                missing.append(field)
        
        assert len(missing) == 0, \
            f"Collector missing required fields: {missing}. Update BrainMetricsCollector to include these fields."
    
    def test_all_template_placeholders_documented(self, templates):
        """Verify all templates with context_needed=true declare required_fields."""
        
        missing_required_fields = []
        
        for template_id, template in templates.items():
            if template.get('context_needed') and not template.get('required_fields'):
                missing_required_fields.append(template_id)
        
        assert len(missing_required_fields) == 0, \
            f"Templates missing required_fields: {missing_required_fields}"
    
    def test_collector_includes_schema_version(self, collector):
        """Verify collector returns schema_version in all metric methods."""
        
        brain_metrics = collector.get_brain_performance_metrics()
        assert 'schema_version' in brain_metrics, \
            "get_brain_performance_metrics() must include schema_version"
        
        token_metrics = collector.get_token_optimization_metrics()
        assert 'schema_version' in token_metrics, \
            "get_token_optimization_metrics() must include schema_version"
    
    def test_fallback_template_exists(self, templates):
        """Verify fallback template exists for schema mismatches."""
        
        assert 'brain_performance_legacy' in templates, \
            "Missing fallback template 'brain_performance_legacy' for schema mismatches"
    
    def test_no_orphaned_placeholders(self, templates, collector):
        """Detect placeholders in templates that don't exist in any collector."""
        
        import re
        
        # Get all collector outputs
        brain_metrics = collector.get_brain_performance_metrics()
        token_metrics = collector.get_token_optimization_metrics()
        health_metrics = collector.get_brain_health_diagnostics()
        
        all_collector_keys = set(brain_metrics.keys()) | set(token_metrics.keys()) | set(health_metrics.keys())
        
        orphaned = {}
        
        for template_id, template in templates.items():
            content = template.get('content', '')
            
            # Extract all {{placeholder}} patterns
            placeholders = re.findall(r'\{\{([^}#/]+)\}\}', content)
            
            # Check each placeholder
            for placeholder in placeholders:
                placeholder = placeholder.strip()
                if placeholder not in all_collector_keys and placeholder not in ['if', 'else', 'endif']:
                    if template_id not in orphaned:
                        orphaned[template_id] = []
                    orphaned[template_id].append(placeholder)
        
        # Allow some common template helpers
        allowed_orphans = {'recent_patterns', 'optimization_details', 'top_consumers', 
                          'warnings', 'recommendations', 'next_steps'}
        
        # Filter out allowed orphans
        for template_id in list(orphaned.keys()):
            orphaned[template_id] = [p for p in orphaned[template_id] if p not in allowed_orphans]
            if not orphaned[template_id]:
                del orphaned[template_id]
        
        assert len(orphaned) == 0, \
            f"Orphaned placeholders found (not in any collector): {orphaned}"


class TestDocumentationStaleness:
    """Detect stale documentation that doesn't match implementation."""
    
    @pytest.fixture
    def templates(self) -> Dict:
        """Load response templates."""
        template_file = Path('cortex-brain/response-templates.yaml')
        with open(template_file, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        return data['templates']
    
    def test_entry_point_schema_version(self):
        """Verify entry point mentions current schema version."""
        
        entry_point = Path('.github/prompts/CORTEX.prompt.md')
        content = entry_point.read_text(encoding='utf-8')
        
        # Entry point should mention schema versioning
        assert 'schema' in content.lower() or 'version' in content.lower(), \
            "Entry point should mention schema versioning for transparency"
    
    def test_template_last_updated_recent(self, templates):
        """Verify templates have been updated recently (within 90 days)."""
        
        template_file = Path('cortex-brain/response-templates.yaml')
        with open(template_file, encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if 'last_updated' in data:
            from datetime import datetime, timedelta
            last_updated = datetime.fromisoformat(data['last_updated'])
            age_days = (datetime.now() - last_updated).days
            
            assert age_days < 90, \
                f"Templates haven't been updated in {age_days} days (last: {data['last_updated']}). Consider reviewing."
    
    def test_no_hardcoded_counts_in_templates(self, templates):
        """Verify templates don't contain hardcoded module counts."""
        
        import re
        
        hardcoded_patterns = [
            r'\d+/\d+ modules',  # "37/86 modules"
            r'\d+% complete',    # "43% complete"
            r'\d+ tests passing', # "82 tests passing"
        ]
        
        violations = {}
        
        for template_id, template in templates.items():
            content = template.get('content', '')
            
            for pattern in hardcoded_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                if matches:
                    if template_id not in violations:
                        violations[template_id] = []
                    violations[template_id].extend(matches)
        
        assert len(violations) == 0, \
            f"Templates contain hardcoded counts that will become stale: {violations}"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
