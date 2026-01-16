"""
Test suite for Knowledge Repository Structure (KN-001-01)
=========================================================
PHASE-12: Knowledge Ecosystem Expansion
AC: KN-001-01 - Knowledge Repository Structure

Validates:
1. 15+ domain folders created with proper naming
2. Schema defined for knowledge entries
3. Metadata requirements documented and enforced
4. Repository structure supports tier3 knowledge governance

Test Pattern: RED tests (expect failures) → implementation → GREEN tests
"""

import os
import json
import pytest
import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


class TestKnowledgeRepositoryStructure:
    """Tests for physical domain folder structure."""

    def test_knowledge_base_directory_exists(self):
        """Verify knowledge repository base directory exists."""
        knowledge_dir = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        assert knowledge_dir.exists(), "Knowledge base directory not found"
        assert knowledge_dir.is_dir(), "Knowledge base is not a directory"

    def test_all_15_domains_created(self):
        """Verify all 15+ required domain directories exist."""
        knowledge_dir = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        
        required_domains = [
            "GOVERNANCE",
            "INTENT-ROUTING",
            "HALLUCINATION-PREVENTION",
            "EXECUTION-ORCHESTRATION",
            "DATA-MANAGEMENT",
            "OBSERVABILITY",
            "SECURITY",
            "API-DESIGN",
            "ML-MODELS",
            "KNOWLEDGE-CURATION",
            "TESTING-VALIDATION",
            "DEPLOYMENT",
            "DOCUMENTATION",
            "PERFORMANCE",
            "ARCHITECTURE",
            "ERROR-HANDLING",
        ]
        
        for domain in required_domains:
            domain_path = knowledge_dir / domain
            assert domain_path.exists(), f"Domain directory not found: {domain}"
            assert domain_path.is_dir(), f"Domain is not a directory: {domain}"

    def test_domain_naming_convention(self):
        """Verify domain names follow kebab-case convention."""
        knowledge_dir = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        
        for item in knowledge_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                # Domains should be UPPERCASE-KEBAB-CASE or single words
                assert item.name.isupper() or item.name == "README.md", \
                    f"Domain name should be uppercase: {item.name}"
                assert " " not in item.name, f"Domain name contains spaces: {item.name}"

    def test_minimum_16_domains_exist(self):
        """Verify at least 16 domain directories (15+ requirement)."""
        knowledge_dir = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        domain_count = sum(1 for item in knowledge_dir.iterdir() 
                          if item.is_dir() and not item.name.startswith("."))
        assert domain_count >= 15, f"Expected 15+ domains, found {domain_count}"


class TestKnowledgeTaxonomy:
    """Tests for knowledge taxonomy definition."""

    def test_knowledge_taxonomy_file_exists(self):
        """Verify KNOWLEDGE-TAXONOMY.yaml exists."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        assert taxonomy_path.exists(), "KNOWLEDGE-TAXONOMY.yaml not found"
        assert taxonomy_path.suffix == ".yaml", "Taxonomy file should be YAML format"

    def test_taxonomy_valid_yaml_syntax(self):
        """Verify taxonomy file contains valid YAML."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        assert data is not None, "Taxonomy YAML is empty or invalid"

    def test_taxonomy_contains_knowledge_domains_section(self):
        """Verify taxonomy defines all knowledge domains."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        assert "knowledge_domains" in data, "Taxonomy missing 'knowledge_domains' section"
        assert isinstance(data["knowledge_domains"], list), "knowledge_domains should be a list"
        assert len(data["knowledge_domains"]) >= 15, "Should define 15+ domains"

    def test_taxonomy_domain_contains_required_fields(self):
        """Verify each domain has required metadata fields."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        required_fields = ["domain_id", "name", "description", "owner", "priority", "tags"]
        
        for domain in data["knowledge_domains"]:
            for field in required_fields:
                assert field in domain, f"Domain missing required field: {field}"
                assert domain[field] is not None, f"Domain field is None: {field}"

    def test_taxonomy_domain_ids_unique(self):
        """Verify all domain IDs are unique."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        domain_ids = [d["domain_id"] for d in data["knowledge_domains"]]
        assert len(domain_ids) == len(set(domain_ids)), "Domain IDs are not unique"

    def test_taxonomy_contains_entry_schema_section(self):
        """Verify taxonomy defines knowledge entry schema."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        assert "knowledge_entry_schema" in data, "Taxonomy missing 'knowledge_entry_schema'"
        schema = data["knowledge_entry_schema"]
        assert "required_fields" in schema, "Schema missing 'required_fields'"
        assert "optional_fields" in schema, "Schema missing 'optional_fields'"


class TestKnowledgeEntrySchema:
    """Tests for knowledge entry schema definition."""

    def test_schema_defines_entry_id_field(self):
        """Verify schema defines entry_id field with format."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        schema = data["knowledge_entry_schema"]["required_fields"]
        assert "entry_id" in schema, "Schema missing entry_id field"
        assert "format" in schema["entry_id"], "entry_id missing format specification"
        assert "KE-" in schema["entry_id"]["format"], "entry_id format should start with KE-"

    def test_schema_defines_title_field(self):
        """Verify schema defines title field with max_length."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        schema = data["knowledge_entry_schema"]["required_fields"]
        assert "title" in schema, "Schema missing title field"
        assert "max_length" in schema["title"], "title missing max_length"

    def test_schema_defines_domain_enum(self):
        """Verify schema defines domain field with valid enum values."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        schema = data["knowledge_entry_schema"]["required_fields"]
        assert "domain" in schema, "Schema missing domain field"
        assert "enum" in schema["domain"], "domain missing enum values"
        assert len(schema["domain"]["enum"]) >= 15, "domain enum should list 15+ domains"

    def test_schema_defines_content_field(self):
        """Verify schema defines content field with minimum length."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        schema = data["knowledge_entry_schema"]["required_fields"]
        assert "content" in schema, "Schema missing content field"
        assert "min_length" in schema["content"], "content missing min_length"

    def test_schema_defines_ac_ids_field(self):
        """Verify schema defines ac_ids field with pattern."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        schema = data["knowledge_entry_schema"]["required_fields"]
        assert "ac_ids" in schema, "Schema missing ac_ids field"
        assert "pattern" in schema["ac_ids"], "ac_ids missing pattern"
        assert "AC-" in schema["ac_ids"]["pattern"], "ac_ids pattern should reference AC-IDs"

    def test_schema_defines_timestamp_fields(self):
        """Verify schema defines created_at and timestamps."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        schema = data["knowledge_entry_schema"]["required_fields"]
        assert "created_at" in schema, "Schema missing created_at field"
        assert schema["created_at"]["type"] == "datetime", "created_at should be datetime type"

    def test_schema_defines_optional_fields(self):
        """Verify schema defines optional fields like quality_score."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        optional = data["knowledge_entry_schema"]["optional_fields"]
        assert "quality_score" in optional, "Missing quality_score optional field"
        assert "related_entries" in optional, "Missing related_entries optional field"
        assert "expert_review" in optional, "Missing expert_review optional field"

    def test_schema_quality_score_range(self):
        """Verify quality_score field has proper 0.0-1.0 range."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        quality_score = data["knowledge_entry_schema"]["optional_fields"]["quality_score"]
        assert quality_score["min"] == 0.0, "quality_score minimum should be 0.0"
        assert quality_score["max"] == 1.0, "quality_score maximum should be 1.0"


class TestMetadataRequirements:
    """Tests for metadata validation rules."""

    def test_taxonomy_defines_validation_rules(self):
        """Verify taxonomy defines validation rules section."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        assert "metadata_requirements" in data, "Missing metadata_requirements section"
        assert "validation_rules" in data["metadata_requirements"], "Missing validation_rules"

    def test_validation_rules_include_ac_id_format(self):
        """Verify validation includes AC-ID format rule."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        rules = data["metadata_requirements"]["validation_rules"]
        ac_id_rule = [r for r in rules if "AC-ID" in r or "AC-" in r]
        assert len(ac_id_rule) > 0, "Missing AC-ID format validation rule"

    def test_validation_rules_include_uniqueness_requirement(self):
        """Verify validation includes uniqueness requirement."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        rules = data["metadata_requirements"]["validation_rules"]
        uniqueness_rule = [r for r in rules if "unique" in r.lower()]
        assert len(uniqueness_rule) > 0, "Missing uniqueness validation rule"

    def test_taxonomy_defines_governance_rules(self):
        """Verify taxonomy defines governance rules section."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        assert "governance_rules" in data["metadata_requirements"], "Missing governance_rules"
        rules = data["metadata_requirements"]["governance_rules"]
        assert isinstance(rules, list), "governance_rules should be a list"
        assert len(rules) > 0, "governance_rules should not be empty"

    def test_governance_rules_include_database_logging(self):
        """Verify governance includes database logging requirement."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        rules = data["metadata_requirements"]["governance_rules"]
        db_rule = [r for r in rules if "governance.db" in r or "database" in r.lower()]
        assert len(db_rule) > 0, "Missing database logging governance rule"

    def test_governance_rules_include_audit_requirement(self):
        """Verify governance includes audit trail requirement."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        rules = data["metadata_requirements"]["governance_rules"]
        audit_rule = [r for r in rules if "audit" in r.lower() or "modification" in r.lower()]
        assert len(audit_rule) > 0, "Missing audit trail governance rule"


class TestDirectoryStructureDocumentation:
    """Tests for directory structure documentation."""

    def test_taxonomy_documents_directory_structure(self):
        """Verify taxonomy documents the directory structure."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        assert "directory_structure" in data, "Missing directory_structure documentation"
        structure = data["directory_structure"]
        assert "cortex-brain/tier3/knowledge/" in structure, "Structure should show hierarchy"

    def test_taxonomy_structure_shows_all_domains(self):
        """Verify documented structure shows all 16+ domains."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        structure = data["directory_structure"]
        # Count domain entries in structure (lines with ├── or └──)
        domain_lines = [line for line in structure.split('\n') 
                       if ('├──' in line or '└──' in line) and '/' in line]
        assert len(domain_lines) >= 15, f"Structure should show 15+ domains, found {len(domain_lines)}"


class TestKnowledgeRepositoryIntegration:
    """Integration tests for repository structure."""

    def test_physical_structure_matches_taxonomy_definition(self):
        """Verify physical directory structure matches taxonomy definition."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        knowledge_dir = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Get domain IDs from taxonomy
        taxonomy_domains = set(d["domain_id"] for d in data["knowledge_domains"])
        
        # Get actual directories
        actual_domains = set(item.name for item in knowledge_dir.iterdir() 
                            if item.is_dir() and not item.name.startswith("."))
        
        # Remove files that aren't domains
        actual_domains = actual_domains - {"__pycache__"}
        
        assert taxonomy_domains == actual_domains, \
            f"Mismatch between taxonomy and actual domains.\nTaxonomy: {taxonomy_domains}\nActual: {actual_domains}"

    def test_repository_supports_entry_creation_pattern(self):
        """Verify repository structure supports knowledge entry creation pattern."""
        knowledge_dir = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        
        # Each domain directory should be writable
        for domain_dir in knowledge_dir.iterdir():
            if domain_dir.is_dir() and not domain_dir.name.startswith("."):
                # Verify we can access the directory
                assert os.access(str(domain_dir), os.W_OK), \
                    f"Domain directory not writable: {domain_dir.name}"

    def test_knowledge_repository_version_tracking(self):
        """Verify repository includes version information."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        assert "version" in data, "Taxonomy missing version"
        assert "created_at" in data, "Taxonomy missing created_at"
        assert "status" in data, "Taxonomy missing status"

    def test_knowledge_repository_governance_reference(self):
        """Verify repository references correct AC-ID."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        assert "ac_id" in data, "Taxonomy missing ac_id"
        assert data["ac_id"] == "KN-001-01", f"Expected ac_id KN-001-01, got {data['ac_id']}"


class TestDomainREADMEs:
    """Tests for domain README files."""

    def test_each_domain_has_readme(self):
        """Verify each domain directory has a README.md file."""
        knowledge_dir = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        
        for domain_dir in knowledge_dir.iterdir():
            if domain_dir.is_dir() and not domain_dir.name.startswith("."):
                readme_path = domain_dir / "README.md"
                assert readme_path.exists(), f"Domain {domain_dir.name} missing README.md"

    def test_domain_readme_contains_domain_name(self):
        """Verify each README includes the domain name."""
        knowledge_dir = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        
        for domain_dir in knowledge_dir.iterdir():
            if domain_dir.is_dir() and not domain_dir.name.startswith("."):
                readme_path = domain_dir / "README.md"
                with open(readme_path, 'r') as f:
                    content = f.read()
                assert domain_dir.name in content, \
                    f"Domain README doesn't mention domain name: {domain_dir.name}"


class TestEdgeCases:
    """Edge case tests for repository structure."""

    def test_domain_names_no_special_characters(self):
        """Verify domain names contain only valid characters."""
        knowledge_dir = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        
        valid_chars = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_")
        
        for item in knowledge_dir.iterdir():
            if item.is_dir() and not item.name.startswith("."):
                for char in item.name:
                    assert char in valid_chars, \
                        f"Domain name contains invalid character '{char}': {item.name}"

    def test_repository_structure_consistent(self):
        """Verify repository structure is consistent across all domains."""
        knowledge_dir = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        
        # All domains should at least have README.md
        for domain_dir in knowledge_dir.iterdir():
            if domain_dir.is_dir() and not domain_dir.name.startswith("."):
                readme = domain_dir / "README.md"
                assert readme.exists(), f"Missing README.md in {domain_dir.name}"

    def test_no_duplicate_domain_directories(self):
        """Verify no duplicate domain directories exist."""
        knowledge_dir = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge"
        
        domain_names = [item.name for item in knowledge_dir.iterdir() 
                       if item.is_dir() and not item.name.startswith(".")]
        assert len(domain_names) == len(set(domain_names)), "Duplicate domain directories found"

    def test_entry_id_format_validation(self):
        """Verify entry ID format is properly documented."""
        taxonomy_path = Path(__file__).parent.parent.parent / "cortex-brain" / "tier3" / "knowledge" / "KNOWLEDGE-TAXONOMY.yaml"
        with open(taxonomy_path, 'r') as f:
            data = yaml.safe_load(f)
        
        entry_id_format = data["knowledge_entry_schema"]["required_fields"]["entry_id"]["format"]
        assert "{DOMAIN}" in entry_id_format, "Format missing {DOMAIN} placeholder"
        assert "{NNN}" in entry_id_format, "Format missing {NNN} placeholder for sequence"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
