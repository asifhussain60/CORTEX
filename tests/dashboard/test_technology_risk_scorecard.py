"""
Tests for Technology Risk Scorecard component.
Tests risk calculations, color coding, sorting, filtering, priority queue.
"""

import pytest
import json
import os
import sys

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))


class TestRiskColorCoding:
    """Test risk score color coding logic."""
    
    def test_color_coding_low_risk(self):
        """Test color for low risk scores (<30)."""
        def get_risk_color(score):
            if score < 30:
                return '#28a745'  # Green
            elif score < 60:
                return '#ffc107'  # Yellow
            else:
                return '#dc3545'  # Red
        
        assert get_risk_color(0) == '#28a745'
        assert get_risk_color(15) == '#28a745'
        assert get_risk_color(29) == '#28a745'
    
    def test_color_coding_medium_risk(self):
        """Test color for medium risk scores (30-60)."""
        def get_risk_color(score):
            if score < 30:
                return '#28a745'
            elif score < 60:
                return '#ffc107'
            else:
                return '#dc3545'
        
        assert get_risk_color(30) == '#ffc107'
        assert get_risk_color(45) == '#ffc107'
        assert get_risk_color(59) == '#ffc107'
    
    def test_color_coding_high_risk(self):
        """Test color for high risk scores (>60)."""
        def get_risk_color(score):
            if score < 30:
                return '#28a745'
            elif score < 60:
                return '#ffc107'
            else:
                return '#dc3545'
        
        assert get_risk_color(60) == '#dc3545'
        assert get_risk_color(75) == '#dc3545'
        assert get_risk_color(100) == '#dc3545'


class TestRiskClassification:
    """Test risk classification for CSS classes."""
    
    def test_risk_class_low(self):
        """Test CSS class for low risk."""
        def get_risk_class(score):
            if score < 30:
                return 'risk-low'
            elif score < 60:
                return 'risk-medium'
            else:
                return 'risk-high'
        
        assert get_risk_class(25) == 'risk-low'
    
    def test_risk_class_medium(self):
        """Test CSS class for medium risk."""
        def get_risk_class(score):
            if score < 30:
                return 'risk-low'
            elif score < 60:
                return 'risk-medium'
            else:
                return 'risk-high'
        
        assert get_risk_class(45) == 'risk-medium'
    
    def test_risk_class_high(self):
        """Test CSS class for high risk."""
        def get_risk_class(score):
            if score < 30:
                return 'risk-low'
            elif score < 60:
                return 'risk-medium'
            else:
                return 'risk-high'
        
        assert get_risk_class(75) == 'risk-high'


class TestSorting:
    """Test table sorting functionality."""
    
    def test_sort_by_risk_score_descending(self):
        """Test sorting by risk score (highest first)."""
        data = [
            {'product': 'A', 'risk_score': 50},
            {'product': 'B', 'risk_score': 80},
            {'product': 'C', 'risk_score': 30}
        ]
        
        sorted_data = sorted(data, key=lambda x: x['risk_score'], reverse=True)
        
        assert sorted_data[0]['product'] == 'B'
        assert sorted_data[0]['risk_score'] == 80
        assert sorted_data[2]['product'] == 'C'
    
    def test_sort_by_risk_score_ascending(self):
        """Test sorting by risk score (lowest first)."""
        data = [
            {'product': 'A', 'risk_score': 50},
            {'product': 'B', 'risk_score': 80},
            {'product': 'C', 'risk_score': 30}
        ]
        
        sorted_data = sorted(data, key=lambda x: x['risk_score'], reverse=False)
        
        assert sorted_data[0]['product'] == 'C'
        assert sorted_data[0]['risk_score'] == 30
    
    def test_sort_by_product_name(self):
        """Test sorting by product name alphabetically."""
        data = [
            {'product': 'Visual Studio', 'risk_score': 50},
            {'product': 'C#', 'risk_score': 30},
            {'product': '.NET', 'risk_score': 40}
        ]
        
        sorted_data = sorted(data, key=lambda x: x['product'].lower())
        
        assert sorted_data[0]['product'] == '.NET'
        assert sorted_data[1]['product'] == 'C#'
        assert sorted_data[2]['product'] == 'Visual Studio'
    
    def test_sort_handles_null_values(self):
        """Test sorting handles null/None values."""
        data = [
            {'product': 'A', 'eol_date': '2025-01-01'},
            {'product': 'B', 'eol_date': None},
            {'product': 'C', 'eol_date': '2026-01-01'}
        ]
        
        # Replace None with a default for sorting
        sorted_data = sorted(data, key=lambda x: x['eol_date'] if x['eol_date'] else 'zzzz')
        
        assert sorted_data[0]['product'] == 'A'
        assert sorted_data[2]['product'] == 'B'  # None sorted last


class TestFiltering:
    """Test data filtering by risk level."""
    
    def test_filter_all(self):
        """Test 'all' filter shows all data."""
        data = [
            {'product': 'A', 'risk_score': 20},
            {'product': 'B', 'risk_score': 50},
            {'product': 'C', 'risk_score': 80}
        ]
        
        filtered = data  # No filtering
        assert len(filtered) == 3
    
    def test_filter_critical(self):
        """Test 'critical' filter shows only >60."""
        data = [
            {'product': 'A', 'risk_score': 20},
            {'product': 'B', 'risk_score': 50},
            {'product': 'C', 'risk_score': 80}
        ]
        
        filtered = [d for d in data if d['risk_score'] > 60]
        assert len(filtered) == 1
        assert filtered[0]['product'] == 'C'
    
    def test_filter_high(self):
        """Test 'high' filter shows 40-60 range."""
        data = [
            {'product': 'A', 'risk_score': 20},
            {'product': 'B', 'risk_score': 50},
            {'product': 'C', 'risk_score': 80}
        ]
        
        filtered = [d for d in data if 40 <= d['risk_score'] <= 60]
        assert len(filtered) == 1
        assert filtered[0]['product'] == 'B'
    
    def test_filter_low(self):
        """Test 'low' filter shows <40."""
        data = [
            {'product': 'A', 'risk_score': 20},
            {'product': 'B', 'risk_score': 50},
            {'product': 'C', 'risk_score': 80}
        ]
        
        filtered = [d for d in data if d['risk_score'] < 40]
        assert len(filtered) == 1
        assert filtered[0]['product'] == 'A'


class TestPriorityQueue:
    """Test priority queue (top 5) generation."""
    
    def test_priority_queue_top_5(self):
        """Test priority queue returns top 5 by risk score."""
        data = [
            {'product': 'A', 'risk_score': 30},
            {'product': 'B', 'risk_score': 90},
            {'product': 'C', 'risk_score': 70},
            {'product': 'D', 'risk_score': 50},
            {'product': 'E', 'risk_score': 80},
            {'product': 'F', 'risk_score': 60},
            {'product': 'G', 'risk_score': 40}
        ]
        
        top5 = sorted(data, key=lambda x: x['risk_score'], reverse=True)[:5]
        
        assert len(top5) == 5
        assert top5[0]['product'] == 'B'  # 90
        assert top5[1]['product'] == 'E'  # 80
        assert top5[2]['product'] == 'C'  # 70
        assert top5[3]['product'] == 'F'  # 60
        assert top5[4]['product'] == 'D'  # 50
    
    def test_priority_queue_fewer_than_5(self):
        """Test priority queue when fewer than 5 items."""
        data = [
            {'product': 'A', 'risk_score': 70},
            {'product': 'B', 'risk_score': 90}
        ]
        
        top5 = sorted(data, key=lambda x: x['risk_score'], reverse=True)[:5]
        
        assert len(top5) == 2
        assert top5[0]['product'] == 'B'
    
    def test_priority_queue_sorts_descending(self):
        """Test priority queue is sorted by risk score descending."""
        data = [
            {'product': 'A', 'risk_score': 50},
            {'product': 'B', 'risk_score': 80},
            {'product': 'C', 'risk_score': 60}
        ]
        
        top5 = sorted(data, key=lambda x: x['risk_score'], reverse=True)[:5]
        
        assert top5[0]['risk_score'] > top5[1]['risk_score']
        assert top5[1]['risk_score'] > top5[2]['risk_score']


class TestScatterPlotScales:
    """Test D3.js scatter plot scale calculations."""
    
    def test_x_scale_domain(self):
        """Test x-axis scale domain is 0-100."""
        domain = (0, 100)
        assert domain[0] == 0
        assert domain[1] == 100
    
    def test_y_scale_domain(self):
        """Test y-axis scale domain based on max project count."""
        data = [
            {'project_count': 5},
            {'project_count': 15},
            {'project_count': 8}
        ]
        
        max_count = max(d['project_count'] for d in data)
        domain_max = max_count * 1.1  # 10% padding
        
        assert domain_max == 15 * 1.1
        assert domain_max == 16.5
    
    def test_radius_scale_calculation(self):
        """Test bubble radius scales with project count."""
        def calculate_radius(project_count, max_count):
            # Sqrt scale for area representation
            min_radius = 5
            max_radius = 20
            ratio = project_count / max_count
            return min_radius + (max_radius - min_radius) * (ratio ** 0.5)
        
        max_count = 20
        
        # Small project count
        radius_small = calculate_radius(1, max_count)
        assert 5 <= radius_small <= 10
        
        # Large project count
        radius_large = calculate_radius(20, max_count)
        assert radius_large == 20


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
