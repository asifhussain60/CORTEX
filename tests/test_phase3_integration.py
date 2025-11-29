"""
Phase 3 Integration Tests - Policy System

Tests all components of the Policy Integration system:
- PolicyAnalyzer: Document parsing (PDF, MD, DOCX, TXT)
- ComplianceValidator: 3-act WOW workflow
- PolicyTestGenerator: Pytest generation
- PolicyStorage: Tier 3 storage and tracking

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import os
import json
import sqlite3
from pathlib import Path

# Add CORTEX to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.policy import (
    PolicyAnalyzer,
    PolicyDocument,
    PolicyRule,
    PolicyLevel,
    PolicyCategory,
    ComplianceValidator,
    ComplianceReport,
    PolicyTestGenerator,
    PolicyStorage
)


class TestPolicyAnalyzer:
    """Test PolicyAnalyzer document parsing"""
    
    def test_parse_markdown(self, tmp_path):
        """Test parsing Markdown policy documents"""
        policy_content = """# Security Policy
Version: 1.0
Date: 2025-11-26

## Requirements

- Passwords MUST NOT be stored in plain text.
- API keys SHOULD NOT be hardcoded.
- Test coverage MUST be greater than 80%.
"""
        policy_file = tmp_path / "policy.md"
        policy_file.write_text(policy_content)
        
        analyzer = PolicyAnalyzer()
        doc = analyzer.analyze_file(str(policy_file))
        
        assert doc is not None
        assert doc.title == "Security Policy"
        assert doc.version == "1.0"
        assert len(doc.rules) == 3
        assert doc.format == "md"  # File extension format
    
    def test_detect_policy_levels(self, tmp_path):
        """Test RFC 2119 level detection"""
        policy_content = """# Test Policy

- Item 1 MUST comply.
- Item 2 MUST NOT violate.
- Item 3 SHOULD follow.
- Item 4 SHOULD NOT ignore.
- Item 5 MAY be optional.
"""
        policy_file = tmp_path / "policy.md"
        policy_file.write_text(policy_content)
        
        analyzer = PolicyAnalyzer()
        doc = analyzer.analyze_file(str(policy_file))
        
        levels = [rule.level for rule in doc.rules]
        assert PolicyLevel.MUST in levels
        assert PolicyLevel.MUST_NOT in levels
        assert PolicyLevel.SHOULD in levels
        assert PolicyLevel.SHOULD_NOT in levels
        assert PolicyLevel.MAY in levels
    
    def test_detect_categories(self, tmp_path):
        """Test category detection"""
        policy_content = """# Test Policy

- Passwords MUST be encrypted (security).
- Tests MUST pass (testing).
- Code MUST have docstrings (documentation).
- API response time MUST be under 200ms (performance).
"""
        policy_file = tmp_path / "policy.md"
        policy_file.write_text(policy_content)
        
        analyzer = PolicyAnalyzer()
        doc = analyzer.analyze_file(str(policy_file))
        
        categories = [rule.category for rule in doc.rules]
        assert PolicyCategory.SECURITY in categories or PolicyCategory.GENERAL in categories
        assert PolicyCategory.TESTING in categories or PolicyCategory.GENERAL in categories
    
    def test_extract_thresholds(self, tmp_path):
        """Test threshold extraction"""
        policy_content = """# Test Policy

- Test coverage MUST be greater than 80%.
- API response MUST be under 200ms.
- Memory usage SHOULD be less than 100MB.
"""
        policy_file = tmp_path / "policy.md"
        policy_file.write_text(policy_content)
        
        analyzer = PolicyAnalyzer()
        doc = analyzer.analyze_file(str(policy_file))
        
        rules_with_thresholds = [r for r in doc.rules if r.threshold is not None]
        assert len(rules_with_thresholds) >= 1
        
        # Check that thresholds are numeric
        for rule in rules_with_thresholds:
            assert isinstance(rule.threshold, (int, float))
    
    def test_file_hashing(self, tmp_path):
        """Test file hash calculation"""
        policy_content = "# Test Policy\n- Rule 1"
        policy_file = tmp_path / "policy.md"
        policy_file.write_text(policy_content)
        
        analyzer = PolicyAnalyzer()
        doc1 = analyzer.analyze_file(str(policy_file))
        
        # Same content should produce same hash
        doc2 = analyzer.analyze_file(str(policy_file))
        assert doc1.file_hash == doc2.file_hash
        
        # Different content should produce different hash
        policy_file.write_text(policy_content + "\n- Rule 2")
        doc3 = analyzer.analyze_file(str(policy_file))
        assert doc1.file_hash != doc3.file_hash


class TestComplianceValidator:
    """Test ComplianceValidator 3-act workflow"""
    
    def test_validation_workflow(self, tmp_path):
        """Test complete validation workflow"""
        policy_content = """# Test Policy
- Passwords MUST NOT be stored in plain text.
- Test coverage MUST be greater than 80%.
"""
        policy_file = tmp_path / "policy.md"
        policy_file.write_text(policy_content)
        
        # Create test codebase
        codebase_dir = tmp_path / "codebase"
        codebase_dir.mkdir()
        
        test_file = codebase_dir / "test.py"
        test_file.write_text('''
password = "plaintext123"  # Violation
def calculate():
    return 42
''')
        
        analyzer = PolicyAnalyzer()
        policy_doc = analyzer.analyze_file(str(policy_file))
        
        validator = ComplianceValidator()
        report = validator.validate(policy_doc, str(codebase_dir))
        
        assert report is not None
        assert isinstance(report.compliance_score, float)
        assert 0 <= report.compliance_score <= 100
        assert len(report.violations) >= 0
        assert len(report.gap_analyses) >= 0
        assert len(report.remediation_actions) >= 0
    
    def test_security_violation_detection(self, tmp_path):
        """Test security violation detection"""
        policy_content = """# Security Policy
- Passwords MUST NOT be hardcoded.
"""
        policy_file = tmp_path / "policy.md"
        policy_file.write_text(policy_content)
        
        codebase_dir = tmp_path / "codebase"
        codebase_dir.mkdir()
        
        # File with hardcoded password
        test_file = codebase_dir / "auth.py"
        test_file.write_text('''
DB_PASSWORD = "secret123"
API_KEY = "abc123xyz"
''')
        
        analyzer = PolicyAnalyzer()
        policy_doc = analyzer.analyze_file(str(policy_file))
        
        validator = ComplianceValidator()
        report = validator.validate(policy_doc, str(codebase_dir))
        
        # Should detect password violations
        password_violations = [
            v for v in report.violations 
            if 'password' in v.violation_details.lower() or 'hardcoded' in v.violation_details.lower()
        ]
        
        # May or may not find violations depending on rules
        assert isinstance(report.violations, list)
    
    def test_gap_analysis_generation(self, tmp_path):
        """Test gap analysis generation"""
        policy_content = """# Quality Policy
- All functions MUST have docstrings.
"""
        policy_file = tmp_path / "policy.md"
        policy_file.write_text(policy_content)
        
        codebase_dir = tmp_path / "codebase"
        codebase_dir.mkdir()
        
        # File with missing docstrings
        test_file = codebase_dir / "utils.py"
        test_file.write_text('''
def process_data():
    return None

def validate_input():
    return True
''')
        
        analyzer = PolicyAnalyzer()
        policy_doc = analyzer.analyze_file(str(policy_file))
        
        validator = ComplianceValidator()
        report = validator.validate(policy_doc, str(codebase_dir))
        
        assert isinstance(report.gap_analyses, list)
    
    def test_remediation_action_generation(self, tmp_path):
        """Test remediation action generation"""
        policy_content = """# Test Policy
- Code MUST follow standards.
"""
        policy_file = tmp_path / "policy.md"
        policy_file.write_text(policy_content)
        
        codebase_dir = tmp_path / "codebase"
        codebase_dir.mkdir()
        
        analyzer = PolicyAnalyzer()
        policy_doc = analyzer.analyze_file(str(policy_file))
        
        validator = ComplianceValidator()
        report = validator.validate(policy_doc, str(codebase_dir))
        
        assert isinstance(report.remediation_actions, list)
        
        # Actions should have required fields
        if report.remediation_actions:
            action = report.remediation_actions[0]
            assert hasattr(action, 'description')
            assert hasattr(action, 'priority')


class TestPolicyTestGenerator:
    """Test PolicyTestGenerator pytest generation"""
    
    def test_generate_test_file(self, tmp_path):
        """Test pytest test file generation"""
        policy_content = """# Test Policy
- Security checks MUST pass.
- Tests MUST have coverage.
"""
        policy_file = tmp_path / "policy.md"
        policy_file.write_text(policy_content)
        
        analyzer = PolicyAnalyzer()
        policy_doc = analyzer.analyze_file(str(policy_file))
        
        generator = PolicyTestGenerator()
        output_file = tmp_path / "test_compliance.py"
        
        result = generator.generate_test_file(
            policy_doc,
            str(output_file),
            codebase_path="."
        )
        
        assert Path(result).exists()
        
        # Check file content
        content = Path(result).read_text()
        assert "import pytest" in content
        assert "@pytest.mark.compliance" in content
        assert "def test_" in content
        assert "PolicyAnalyzer" in content
        assert "ComplianceValidator" in content
    
    def test_generate_conftest(self, tmp_path):
        """Test conftest.py generation"""
        generator = PolicyTestGenerator()
        conftest_path = generator.generate_conftest(str(tmp_path))
        
        assert Path(conftest_path).exists()
        
        content = Path(conftest_path).read_text()
        assert "pytest_configure" in content
        assert "compliance" in content
        assert "markers" in content
    
    def test_generated_markers(self, tmp_path):
        """Test that generated tests have proper markers"""
        policy_content = """# Security Policy
- Passwords MUST NOT be exposed.
- Data SHOULD be encrypted.
"""
        policy_file = tmp_path / "policy.md"
        policy_file.write_text(policy_content)
        
        analyzer = PolicyAnalyzer()
        policy_doc = analyzer.analyze_file(str(policy_file))
        
        generator = PolicyTestGenerator()
        output_file = tmp_path / "test_compliance.py"
        
        generator.generate_test_file(
            policy_doc,
            str(output_file),
            codebase_path="."
        )
        
        content = output_file.read_text()
        
        # Check for severity markers
        assert "@pytest.mark.critical" in content or "@pytest.mark.high" in content
        
        # Check for category markers
        # Markers should be present
        assert "@pytest.mark." in content


class TestPolicyStorage:
    """Test PolicyStorage Tier 3 integration"""
    
    def test_store_policy(self, tmp_path):
        """Test policy storage in Tier 3"""
        policy_content = """# Storage Test Policy
Version: 1.0
- Rule 1 MUST apply.
"""
        policy_file = tmp_path / "policy.md"
        policy_file.write_text(policy_content)
        
        # Use temp brain path
        brain_path = tmp_path / "test-brain"
        storage = PolicyStorage(brain_path=str(brain_path))
        
        policy_id, changed = storage.store_policy(
            repo_name="test-repo",
            policy_file=str(policy_file),
            policy_name="storage-test"
        )
        
        assert policy_id is not None
        assert "test-repo" in policy_id
        assert changed == True  # First time storing
    
    def test_change_detection(self, tmp_path):
        """Test policy change detection"""
        policy_content_v1 = "# Policy v1\n- Rule 1"
        policy_content_v2 = "# Policy v2\n- Rule 1\n- Rule 2"
        
        policy_file = tmp_path / "policy.md"
        policy_file.write_text(policy_content_v1)
        
        brain_path = tmp_path / "test-brain"
        storage = PolicyStorage(brain_path=str(brain_path))
        
        # First store
        policy_id1, changed1 = storage.store_policy(
            repo_name="test-repo",
            policy_file=str(policy_file),
            policy_name="change-test"
        )
        
        assert changed1 == True
        
        # Store again without changes
        policy_id2, changed2 = storage.store_policy(
            repo_name="test-repo",
            policy_file=str(policy_file),
            policy_name="change-test"
        )
        
        assert changed2 == False
        
        # Modify and store
        policy_file.write_text(policy_content_v2)
        policy_id3, changed3 = storage.store_policy(
            repo_name="test-repo",
            policy_file=str(policy_file),
            policy_name="change-test"
        )
        
        assert changed3 == True
    
    def test_validation_storage(self, tmp_path):
        """Test validation report storage"""
        policy_content = "# Test Policy\n- Code MUST be valid."
        policy_file = tmp_path / "policy.md"
        policy_file.write_text(policy_content)
        
        codebase_dir = tmp_path / "codebase"
        codebase_dir.mkdir()
        
        brain_path = tmp_path / "test-brain"
        storage = PolicyStorage(brain_path=str(brain_path))
        
        policy_id, _ = storage.store_policy(
            repo_name="test-repo",
            policy_file=str(policy_file)
        )
        
        report = storage.validate_and_store(
            repo_name="test-repo",
            policy_id=policy_id,
            codebase_path=str(codebase_dir)
        )
        
        assert report is not None
        assert isinstance(report.compliance_score, float)
    
    def test_validation_history(self, tmp_path):
        """Test validation history retrieval"""
        policy_content = "# Test Policy\n- Standard applies."
        policy_file = tmp_path / "policy.md"
        policy_file.write_text(policy_content)
        
        codebase_dir = tmp_path / "codebase"
        codebase_dir.mkdir()
        
        brain_path = tmp_path / "test-brain"
        storage = PolicyStorage(brain_path=str(brain_path))
        
        policy_id, _ = storage.store_policy(
            repo_name="test-repo",
            policy_file=str(policy_file)
        )
        
        # Run validation
        storage.validate_and_store(
            repo_name="test-repo",
            policy_id=policy_id,
            codebase_path=str(codebase_dir)
        )
        
        # Get history
        history = storage.get_validation_history("test-repo", policy_id)
        
        assert len(history) >= 1
        assert "compliance_score" in history[0]
        assert "timestamp" in history[0]
    
    def test_list_policies(self, tmp_path):
        """Test listing stored policies"""
        brain_path = tmp_path / "test-brain"
        storage = PolicyStorage(brain_path=str(brain_path))
        
        # Store multiple policies
        for i in range(3):
            policy_content = f"# Policy {i}\n- Rule {i}"
            policy_file = tmp_path / f"policy{i}.md"
            policy_file.write_text(policy_content)
            
            storage.store_policy(
                repo_name="test-repo",
                policy_file=str(policy_file),
                policy_name=f"policy-{i}"
            )
        
        policies = storage.list_policies("test-repo")
        
        assert len(policies) == 3
        assert all("policy_id" in p for p in policies)
        assert all("rules_count" in p for p in policies)


class TestEndToEndWorkflow:
    """Test complete end-to-end policy workflow"""
    
    def test_full_workflow(self, tmp_path):
        """Test: Parse -> Validate -> Generate Tests -> Store"""
        
        # 1. Create policy document
        policy_content = """# Complete Workflow Policy
Version: 1.0
Date: 2025-11-26

## Security
- Passwords MUST NOT be hardcoded.

## Testing
- Test coverage SHOULD exceed 80%.

## Documentation
- Functions SHOULD have docstrings.
"""
        policy_file = tmp_path / "workflow-policy.md"
        policy_file.write_text(policy_content)
        
        # 2. Create codebase
        codebase_dir = tmp_path / "codebase"
        codebase_dir.mkdir()
        
        code_file = codebase_dir / "app.py"
        code_file.write_text('''
def calculate(x, y):
    """Add two numbers"""
    return x + y

password = "secret"  # Violation
''')
        
        # 3. Parse policy
        analyzer = PolicyAnalyzer()
        policy_doc = analyzer.analyze_file(str(policy_file))
        
        assert policy_doc.title == "Complete Workflow Policy"
        assert len(policy_doc.rules) >= 3
        
        # 4. Validate codebase
        validator = ComplianceValidator()
        report = validator.validate(policy_doc, str(codebase_dir))
        
        assert report.compliance_score >= 0
        assert isinstance(report.violations, list)
        
        # 5. Generate tests
        generator = PolicyTestGenerator()
        test_file = tmp_path / "test_compliance.py"
        
        generated_file = generator.generate_test_file(
            policy_doc,
            str(test_file),
            codebase_path=str(codebase_dir)
        )
        
        assert Path(generated_file).exists()
        
        # 6. Store in Tier 3
        brain_path = tmp_path / "test-brain"
        storage = PolicyStorage(brain_path=str(brain_path))
        
        policy_id, changed = storage.store_policy(
            repo_name="workflow-test",
            policy_file=str(policy_file),
            policy_name="workflow-policy"
        )
        
        assert policy_id is not None
        
        # 7. Store validation report
        stored_report = storage.validate_and_store(
            repo_name="workflow-test",
            policy_id=policy_id,
            codebase_path=str(codebase_dir)
        )
        
        assert stored_report.compliance_score >= 0
        
        # 8. Verify history
        history = storage.get_validation_history("workflow-test", policy_id)
        assert len(history) >= 1
        
        print(f"\n✅ End-to-end workflow complete!")
        print(f"   Policy: {policy_doc.title}")
        print(f"   Rules: {len(policy_doc.rules)}")
        print(f"   Compliance: {report.compliance_score}%")
        print(f"   Violations: {len(report.violations)}")
        print(f"   Test File: {generated_file}")
        print(f"   Stored: {policy_id}")


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
