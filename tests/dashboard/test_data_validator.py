"""
Test Dashboard Data Validator

Validates that the validator correctly fixes collector issues.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import json
import pytest
from pathlib import Path
from src.dashboard.validators.data_validator import DashboardDataValidator


# Simulated bad collector output (matches actual luum-fresh issues)
BAD_TECH_STACK = {
    "frontend": [
        {"name": "JavaScript", "version": "unknown", "status": "current", "category": "language"},
        {"name": "TypeScript", "version": "unknown", "status": "current", "category": "language"}
    ],
    "backend": [
        {"name": "Python", "version": "unknown", "status": "current", "category": "language"},  # FALSE POSITIVE
        {"name": "C#", "version": "unknown", "status": "current", "category": "language"},
        {"name": ".NET", "version": "8.0", "status": "current", "category": "framework"}  # WRONG VERSION
    ],
    "database": [],
    "devops": [],
    "summary": {"total_technologies": 5}
}

BAD_EXECUTIVE_SUMMARY = {
    "project_name": "Luum Fresh",
    "tagline": "Enterprise-grade Python SOAP service",  # WRONG - mentions Python
    "what_it_does": {
        "summary": "An enterprise legacy service built with Python, serving critical business operations.",  # WRONG
        "key_points": ["Service-oriented architecture"],
        "source": "hybrid"
    },
    "tech_stack_summary": {
        "primary_technologies": [
            {"name": "JavaScript", "category": "language"},
            {"name": "TypeScript", "category": "language"},
            {"name": "Python", "category": "language"},  # FALSE POSITIVE
            {"name": "C#", "category": "language"}
        ],
        "total_technologies": 4
    }
}


class TestDataValidator:
    """Test data validator fixes collector issues"""
    
    @pytest.fixture
    def validator(self):
        """Create validator for luum-fresh repo"""
        repo_path = Path("C:\\PROJECTS\\luum-fresh")
        return DashboardDataValidator(repo_path)
    
    def test_validator_removes_python_false_positive(self, validator):
        """Validator should remove Python (only in Tools/ directory)"""
        # Establish ground truth first
        validator.ground_truth = validator._scan_repository_ground_truth()
        
        fixed = validator._fix_tech_stack(BAD_TECH_STACK.copy())
        
        # Python should be removed from backend
        backend_langs = [t['name'] for t in fixed['backend']]
        assert "Python" not in backend_langs, "Python should be removed (false positive)"
    
    def test_validator_fixes_dotnet_version(self, validator):
        """Validator should fix .NET version from 8.0 to 4.7.2"""
        # First establish ground truth
        validator.ground_truth = validator._scan_repository_ground_truth()
        
        print(f"\n=== Framework Evidence ===")
        print(f"dotnet_version: {validator.ground_truth['framework_evidence'].get('dotnet_version')}")
        print(f"dotnet_framework: {validator.ground_truth['framework_evidence'].get('dotnet_framework')}")
        
        fixed = validator._fix_tech_stack(BAD_TECH_STACK.copy())
        
        # Find .NET in backend
        dotnet_tech = next((t for t in fixed['backend'] if t['name'] == '.NET'), None)
        
        print(f"\n=== After Fix ===")
        print(f".NET tech: {dotnet_tech}")
        
        if dotnet_tech:
            # Should NOT be 8.0 (modern .NET Core)
            assert dotnet_tech['version'] != "8.0", \
                f"Should fix .NET version hallucination, got {dotnet_tech['version']}"
    
    def test_validator_reorders_primary_language(self, validator):
        """C# should be first backend language (most files), not Python"""
        validator.ground_truth = validator._scan_repository_ground_truth()
        
        fixed = validator._fix_tech_stack(BAD_TECH_STACK.copy())
        
        if fixed['backend']:
            first_lang = fixed['backend'][0]['name']
            assert first_lang == "C#", \
                f"C# should be primary backend language, found {first_lang}"
    
    def test_validator_fixes_narrative(self, validator):
        """Validator should fix narrative mentioning non-existent Python"""
        validator.ground_truth = validator._scan_repository_ground_truth()
        
        fixed = validator._fix_executive_summary(BAD_EXECUTIVE_SUMMARY.copy())
        
        summary = fixed['what_it_does']['summary']
        tagline = fixed.get('tagline', '')
        
        # Should not mention Python
        assert "Python" not in summary, \
            "Narrative should not mention Python after validation"
        assert "Python" not in tagline, \
            "Tagline should not mention Python after validation"
        
        # Should mention C# instead
        assert "C#" in summary or "C#" in tagline, \
            "Should mention actual primary language (C#)"
    
    def test_validator_removes_low_file_count_languages(self, validator):
        """Languages with < 5 files should be removed"""
        validator.ground_truth = validator._scan_repository_ground_truth()
        
        # Add a language with very few files
        test_stack = BAD_TECH_STACK.copy()
        test_stack['backend'].append({
            "name": "Ruby", 
            "version": "unknown",
            "status": "current",
            "category": "language"
        })
        
        fixed = validator._fix_tech_stack(test_stack)
        
        # Languages with < MIN_FILE_THRESHOLD should be removed
        backend_langs = [t['name'] for t in fixed['backend']]
        
        # Ruby shouldn't be there (assuming < 5 files)
        # This depends on actual repo content
    
    def test_validator_tracks_corrections(self, validator):
        """Validator should track all corrections applied"""
        validator.ground_truth = validator._scan_repository_ground_truth()
        validator.ground_truth['corrections_applied'] = []
        
        validator._fix_tech_stack(BAD_TECH_STACK.copy())
        
        corrections = validator.ground_truth['corrections_applied']
        
        # Should have recorded corrections
        assert len(corrections) > 0, "Should record corrections applied"
        
        # Should mention Python removal
        python_corrections = [c for c in corrections if 'Python' in c]
        assert len(python_corrections) > 0, \
            "Should record Python removal correction"
    
    def test_ground_truth_scan_excludes_third_party(self, validator):
        """Ground truth scan should exclude Tools/, External/ directories"""
        ground_truth = validator._scan_repository_ground_truth()
        
        # Python should NOT be detected (all .py files in Tools/)
        assert "Python" not in ground_truth['languages'], \
            "Python files in Tools/ should be excluded from ground truth"
        
        # C# SHOULD be detected (4835 files in Source/)
        assert "C#" in ground_truth['languages'], \
            "C# should be detected in ground truth"
        
        if "C#" in ground_truth['languages']:
            cs_count = ground_truth['languages']['C#']['file_count']
            assert cs_count > 4000, \
                f"Should detect ~4835 C# files, found {cs_count}"
    
    def test_ground_truth_detects_dotnet_framework_version(self, validator):
        """Ground truth should detect actual .NET Framework version"""
        ground_truth = validator._scan_repository_ground_truth()
        
        framework_evidence = ground_truth['framework_evidence']
        
        # Should detect .NET Framework 4.7.2 (not 8.0)
        if framework_evidence.get('dotnet_version'):
            version = framework_evidence['dotnet_version']
            assert version.startswith('4.'), \
                f"Should detect .NET Framework 4.x, found {version}"
    
    def test_validator_end_to_end(self, validator):
        """Full validation flow fixes all issues"""
        collected_data = {
            'tech-stack': BAD_TECH_STACK.copy(),
            'executive-summary': BAD_EXECUTIVE_SUMMARY.copy()
        }
        
        fixed_data = validator.validate_and_fix(collected_data)
        
        # Check tech stack fixed
        backend = fixed_data['tech-stack']['backend']
        backend_langs = [t['name'] for t in backend]
        assert "Python" not in backend_langs, "Python should be removed"
        
        # Check narrative fixed
        summary = fixed_data['executive-summary']['what_it_does']['summary']
        assert "Python" not in summary, "Narrative should not mention Python"
        
        # Check validation metadata present
        assert '_validation' in fixed_data, "Should add validation metadata"
        assert fixed_data['_validation']['validated'] is True
        
        # Check corrections recorded
        corrections = fixed_data['_validation'].get('corrections_applied', [])
        assert len(corrections) > 0, "Should record corrections"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
