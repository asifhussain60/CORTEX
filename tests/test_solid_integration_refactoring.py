"""
Test SOLID Integration with RefactoringIntelligence

Tests the integration of SOLIDPrincipleEnforcer and DependencyGraph
into the code smell detection workflow.
"""

import pytest
from pathlib import Path
from src.workflows.refactoring_intelligence import CodeSmellDetector, CodeSmellType


class TestSOLIDIntegration:
    """Test SOLID violation detection in RefactoringIntelligence."""
    
    def test_detect_srp_violation(self):
        """Test: Detects SRP violations via SOLIDPrincipleEnforcer."""
        detector = CodeSmellDetector()
        
        # Code with SRP violation (god class)
        code = """
class UserManager:
    def create_user(self):
        pass
    
    def validate_email(self):
        pass
    
    def send_welcome_email(self):
        pass
    
    def log_user_creation(self):
        pass
    
    def update_user_stats(self):
        pass
"""
        
        smells = detector.analyze_file("test.py", code)
        
        # Should detect SRP violation or god class
        srp_smells = [s for s in smells if s.smell_type in (CodeSmellType.SRP_VIOLATION, CodeSmellType.GOD_CLASS)]
        
        # At least one violation detected
        assert len(srp_smells) > 0, "Should detect SRP violation or god class"
    
    def test_detect_coupling_violation(self):
        """Test: Detects tight coupling via DependencyGraph."""
        detector = CodeSmellDetector()
        
        # Code with many imports (tight coupling)
        code = """
import os
import sys
import json
import yaml
import requests
import numpy
import pandas
import matplotlib
import sklearn
import torch
import tensorflow
import flask
import django
import fastapi
import sqlalchemy
import redis
"""
        
        smells = detector.analyze_file("test.py", code)
        
        # Should detect tight coupling
        coupling_smells = [s for s in smells if s.smell_type == CodeSmellType.TIGHT_COUPLING]
        
        assert len(coupling_smells) > 0, "Should detect tight coupling with many imports"
    
    def test_solid_detection_does_not_break_existing_analysis(self):
        """Test: SOLID detection doesn't interfere with existing smell detection."""
        detector = CodeSmellDetector()
        
        # Code with long method (existing smell)
        code = """
def process_data():
    # Line 1
    data = load_data()
    # Line 3
    cleaned = clean_data(data)
    # Line 5
    transformed = transform_data(cleaned)
    # Line 7
    validated = validate_data(transformed)
    # Line 9
    enriched = enrich_data(validated)
    # Line 11
    normalized = normalize_data(enriched)
    # Line 13
    filtered = filter_data(normalized)
    # Line 15
    aggregated = aggregate_data(filtered)
    # Line 17
    sorted_data = sort_data(aggregated)
    # Line 19
    formatted = format_data(sorted_data)
    # Line 21
    exported = export_data(formatted)
    # Line 23
    logged = log_export(exported)
    # Line 25
    notified = send_notifications(logged)
    # Line 27
    archived = archive_data(notified)
    # Line 29
    cleaned_up = cleanup_temp_files(archived)
    # Line 31
    reported = generate_report(cleaned_up)
    # Line 33
    finalized = finalize_process(reported)
    # Line 35
    return finalized
"""
        
        smells = detector.analyze_file("test.py", code)
        
        # Should still detect long method
        long_method_smells = [s for s in smells if s.smell_type == CodeSmellType.LONG_METHOD]
        
        assert len(long_method_smells) > 0, "Should still detect existing smell types"
    
    def test_solid_detection_graceful_failure(self):
        """Test: SOLID detection fails gracefully if components unavailable."""
        detector = CodeSmellDetector()
        
        # Simple valid code
        code = """
def hello():
    print("Hello")
"""
        
        # Should not crash even if SOLID components fail
        try:
            smells = detector.analyze_file("test.py", code)
            # If we get here, no exception was raised (good!)
            assert True
        except Exception as e:
            pytest.fail(f"SOLID detection should not crash analysis: {e}")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
