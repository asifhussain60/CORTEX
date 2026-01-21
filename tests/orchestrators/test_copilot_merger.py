"""
Tests for CopilotMerger - CORTEX instructions merger.

TDD Tests for merging CORTEX intelligence with existing repo instructions.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
import tempfile
import shutil


class TestCopilotMergerDiscovery:
    """Tests for discovering existing copilot instructions."""

    def test_find_existing_instructions_in_github_folder(self, tmp_path):
        """Should find copilot-instruction.md in .github folder."""
        from cortex.orchestrators.copilot_merger import CopilotMerger
        
        # Create mock repo structure
        github_dir = tmp_path / ".github"
        github_dir.mkdir()
        instructions_file = github_dir / "copilot-instruction.md"
        instructions_file.write_text("# Existing Instructions\nDo X, Y, Z")
        
        merger = CopilotMerger()
        found = merger.find_existing_instructions(tmp_path)
        
        assert found is not None
        assert found["path"] == instructions_file
        assert "Existing Instructions" in found["content"]

    def test_find_existing_instructions_in_prompts_folder(self, tmp_path):
        """Should find copilot-instruction.md in .github/prompts folder."""
        from cortex.orchestrators.copilot_merger import CopilotMerger
        
        prompts_dir = tmp_path / ".github" / "prompts"
        prompts_dir.mkdir(parents=True)
        instructions_file = prompts_dir / "copilot-instruction.md"
        instructions_file.write_text("# Prompts Instructions\nCustom prompts here")
        
        merger = CopilotMerger()
        found = merger.find_existing_instructions(tmp_path)
        
        assert found is not None
        assert "prompts" in str(found["path"])

    def test_find_cortex_prompt_md(self, tmp_path):
        """Should find CORTEX.prompt.md if it exists."""
        from cortex.orchestrators.copilot_merger import CopilotMerger
        
        prompts_dir = tmp_path / ".github" / "prompts"
        prompts_dir.mkdir(parents=True)
        prompt_file = prompts_dir / "CORTEX.prompt.md"
        prompt_file.write_text("# CORTEX Master Prompt\nCORTEX intelligence")
        
        merger = CopilotMerger()
        found = merger.find_cortex_prompt(tmp_path)
        
        assert found is not None
        assert found["path"] == prompt_file

    def test_no_existing_instructions_returns_none(self, tmp_path):
        """Should return None if no instructions file exists."""
        from cortex.orchestrators.copilot_merger import CopilotMerger
        
        merger = CopilotMerger()
        found = merger.find_existing_instructions(tmp_path)
        
        assert found is None


class TestCopilotMergerParsing:
    """Tests for parsing instruction sections."""

    def test_parse_sections_from_markdown(self):
        """Should parse markdown sections correctly."""
        from cortex.orchestrators.copilot_merger import CopilotMerger
        
        content = """# Main Title

## Section One
Content for section one.

## Section Two
Content for section two.

### Subsection
More content here.
"""
        merger = CopilotMerger()
        sections = merger.parse_sections(content)
        
        assert "Section One" in sections
        assert "Section Two" in sections
        assert "Content for section one" in sections["Section One"]

    def test_extract_project_specific_rules(self):
        """Should extract project-specific rules from instructions."""
        from cortex.orchestrators.copilot_merger import CopilotMerger
        
        content = """# Project Instructions

## Project Rules
- Always use snake_case
- Max 80 chars per line
- Use pytest for testing

## General Info
Some general info here.
"""
        merger = CopilotMerger()
        rules = merger.extract_project_rules(content)
        
        assert len(rules) >= 3
        assert any("snake_case" in rule for rule in rules)

    def test_identify_cortex_sections(self):
        """Should identify sections that came from CORTEX."""
        from cortex.orchestrators.copilot_merger import CopilotMerger
        
        content = """# Instructions

## CORTEX Governance
This is CORTEX-generated content.

## My Custom Rules
This is my own content.

## TIER 0 Rules
More CORTEX content.
"""
        merger = CopilotMerger()
        cortex_sections, user_sections = merger.identify_section_origins(content)
        
        assert "CORTEX Governance" in cortex_sections
        assert "TIER 0 Rules" in cortex_sections
        assert "My Custom Rules" in user_sections


class TestCopilotMergerMerging:
    """Tests for merging instructions."""

    def test_merge_preserves_user_sections(self, tmp_path):
        """Should preserve user-defined sections during merge."""
        from cortex.orchestrators.copilot_merger import CopilotMerger
        
        existing_content = """# My Project Instructions

## My Custom Rules
- Use tabs not spaces
- Always document functions

## Other Custom Section
My special requirements.
"""
        cortex_content = """# CORTEX Instructions

## CORTEX Governance
TIER 0 rules here.

## Architecture
Standard architecture.
"""
        merger = CopilotMerger()
        merged = merger.merge_instructions(existing_content, cortex_content)
        
        # User sections preserved
        assert "My Custom Rules" in merged
        assert "Use tabs not spaces" in merged
        assert "Other Custom Section" in merged
        
        # CORTEX sections added
        assert "CORTEX" in merged

    def test_merge_updates_cortex_sections(self):
        """Should update existing CORTEX sections with new content."""
        from cortex.orchestrators.copilot_merger import CopilotMerger
        
        existing_content = """# Instructions

## CORTEX Governance
Old CORTEX content v1.0

## My Rules
My content stays.
"""
        cortex_content = """# CORTEX Instructions

## CORTEX Governance
New CORTEX content v2.0

## TIER 0 Rules
New tier 0 rules.
"""
        merger = CopilotMerger()
        merged = merger.merge_instructions(existing_content, cortex_content)
        
        # CORTEX section updated
        assert "New CORTEX content v2.0" in merged
        assert "Old CORTEX content v1.0" not in merged
        
        # User section preserved
        assert "My Rules" in merged

    def test_merge_adds_cortex_header(self):
        """Should add CORTEX header to merged instructions."""
        from cortex.orchestrators.copilot_merger import CopilotMerger
        
        existing = "# My Instructions\nSome content."
        cortex = "# CORTEX\nCORTEX content."
        
        merger = CopilotMerger()
        merged = merger.merge_instructions(existing, cortex)
        
        # Should have CORTEX version marker
        assert "CORTEX" in merged
        assert "Version:" in merged or "version" in merged.lower()

    def test_merge_handles_empty_existing(self):
        """Should handle case where no existing instructions exist."""
        from cortex.orchestrators.copilot_merger import CopilotMerger
        
        cortex_content = """# CORTEX Instructions
Complete CORTEX template here.
"""
        merger = CopilotMerger()
        merged = merger.merge_instructions(None, cortex_content)
        
        assert "CORTEX" in merged
        assert "Complete CORTEX template" in merged


class TestCopilotMergerConflictDetection:
    """Tests for detecting conflicts between instructions."""

    def test_detect_conflicting_rules(self):
        """Should detect conflicting rules between existing and CORTEX."""
        from cortex.orchestrators.copilot_merger import CopilotMerger
        
        existing = "Use spaces for indentation. Max 120 chars per line."
        cortex = "Use tabs for indentation. Max 100 chars per line."
        
        merger = CopilotMerger()
        conflicts = merger.detect_conflicts(existing, cortex)
        
        assert len(conflicts) > 0
        assert any("indent" in c["topic"].lower() for c in conflicts)

    def test_no_conflicts_when_compatible(self):
        """Should return empty list when instructions are compatible."""
        from cortex.orchestrators.copilot_merger import CopilotMerger
        
        existing = "Use pytest for testing. Document all functions."
        cortex = "Follow TDD practices. Use type hints."
        
        merger = CopilotMerger()
        conflicts = merger.detect_conflicts(existing, cortex)
        
        # These are compatible, no direct conflicts
        assert len(conflicts) == 0

    def test_report_conflict_resolution_strategy(self):
        """Should recommend resolution strategy for conflicts."""
        from cortex.orchestrators.copilot_merger import CopilotMerger
        
        conflicts = [
            {"topic": "indentation", "existing": "tabs", "cortex": "spaces"},
            {"topic": "line_length", "existing": "120", "cortex": "100"}
        ]
        
        merger = CopilotMerger()
        strategies = merger.get_resolution_strategies(conflicts)
        
        assert len(strategies) == 2
        assert all("strategy" in s for s in strategies)


class TestCopilotMergerGeneration:
    """Tests for generating merged instruction files."""

    def test_generate_merged_file(self, tmp_path):
        """Should generate merged instruction file."""
        from cortex.orchestrators.copilot_merger import CopilotMerger
        
        # Setup
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        github_dir = repo_path / ".github"
        github_dir.mkdir()
        
        existing_file = github_dir / "copilot-instruction.md"
        existing_file.write_text("# My Instructions\n## My Rules\nCustom rule 1")
        
        merger = CopilotMerger()
        result = merger.generate_merged_file(
            repo_path,
            cortex_template="# CORTEX\n## Governance\nTIER 0 rules"
        )
        
        assert result["success"] is True
        assert result["merged_path"].exists()
        
        content = result["merged_path"].read_text()
        assert "My Rules" in content
        assert "CORTEX" in content

    def test_generate_backup_of_existing(self, tmp_path):
        """Should create backup of existing instructions before overwriting."""
        from cortex.orchestrators.copilot_merger import CopilotMerger
        
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        github_dir = repo_path / ".github"
        github_dir.mkdir()
        
        existing_file = github_dir / "copilot-instruction.md"
        existing_file.write_text("# Original Content\nImportant stuff")
        
        merger = CopilotMerger()
        result = merger.generate_merged_file(
            repo_path,
            cortex_template="# CORTEX\nNew content",
            backup=True
        )
        
        assert result["backup_path"] is not None
        assert result["backup_path"].exists()
        assert "Original Content" in result["backup_path"].read_text()


class TestCopilotMergerCORTEXPrompt:
    """Tests for CORTEX.prompt.md generation."""

    def test_generate_cortex_prompt_md(self, tmp_path):
        """Should generate CORTEX.prompt.md file."""
        from cortex.orchestrators.copilot_merger import CopilotMerger
        
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        
        merger = CopilotMerger()
        result = merger.generate_cortex_prompt(repo_path, project_type="finops")
        
        assert result["success"] is True
        assert result["prompt_path"].exists()
        
        content = result["prompt_path"].read_text()
        assert "CORTEX" in content
        assert "finops" in content.lower() or "FinOps" in content

    def test_regenerate_deletes_old_prompt(self, tmp_path):
        """Should delete old CORTEX.prompt.md when regenerating."""
        from cortex.orchestrators.copilot_merger import CopilotMerger
        
        repo_path = tmp_path / "test_repo"
        prompts_dir = repo_path / ".github" / "prompts"
        prompts_dir.mkdir(parents=True)
        
        old_prompt = prompts_dir / "CORTEX.prompt.md"
        old_prompt.write_text("# Old CORTEX v1.0\nOutdated content")
        
        merger = CopilotMerger()
        result = merger.generate_cortex_prompt(repo_path, regenerate=True)
        
        content = result["prompt_path"].read_text()
        assert "Outdated content" not in content
        assert "CORTEX" in content


class TestCopilotMergerMultiRepo:
    """Tests for multi-repo instruction management."""

    def test_process_multiple_repos(self, tmp_path):
        """Should process instructions for multiple repos."""
        from cortex.orchestrators.copilot_merger import CopilotMerger
        
        # Create multiple mock repos
        repos = []
        for name in ["repo1", "repo2", "repo3"]:
            repo_path = tmp_path / name
            repo_path.mkdir()
            (repo_path / ".github").mkdir()
            repos.append(repo_path)
        
        merger = CopilotMerger()
        results = merger.process_repos(repos, cortex_template="# CORTEX\nTemplate")
        
        assert len(results) == 3
        assert all(r["success"] for r in results)

    def test_respect_repo_specific_overrides(self, tmp_path):
        """Should respect repo-specific instruction overrides."""
        from cortex.orchestrators.copilot_merger import CopilotMerger
        
        repo_path = tmp_path / "special_repo"
        repo_path.mkdir()
        github_dir = repo_path / ".github"
        github_dir.mkdir()
        
        # Create cortex-override.yaml for repo-specific rules
        override_file = github_dir / "cortex-override.yaml"
        override_file.write_text("""
override_rules:
  - section: "Code Style"
    rule: "Use 4 spaces indentation"
preserve_sections:
  - "Custom Section"
""")
        
        merger = CopilotMerger()
        overrides = merger.load_repo_overrides(repo_path)
        
        assert "override_rules" in overrides
        assert "preserve_sections" in overrides


class TestCopilotMergerAuditIntegration:
    """Tests for audit trail integration."""

    def test_log_merge_operation_to_audit(self, tmp_path):
        """Should log merge operations to shared audit trail."""
        from cortex.orchestrators.copilot_merger import CopilotMerger
        from cortex.orchestrators import shared_audit_trail
        
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        (repo_path / ".github").mkdir()
        
        with patch.object(shared_audit_trail, 'SharedAuditTrail') as mock_audit:
            mock_instance = MagicMock()
            mock_audit.return_value = mock_instance
            
            merger = CopilotMerger(audit_enabled=True)
            
            merger.generate_merged_file(
                repo_path,
                cortex_template="# CORTEX\nContent"
            )
            
            # Verify audit was called
            mock_instance.log_operation.assert_called()

    def test_audit_records_preserved_sections(self, tmp_path):
        """Should record which sections were preserved in audit."""
        from cortex.orchestrators.copilot_merger import CopilotMerger
        from cortex.orchestrators import shared_audit_trail
        
        repo_path = tmp_path / "test_repo"
        repo_path.mkdir()
        github_dir = repo_path / ".github"
        github_dir.mkdir()
        
        existing = github_dir / "copilot-instruction.md"
        existing.write_text("# Instructions\n## My Custom Rules\nKeep this")
        
        with patch.object(shared_audit_trail, 'SharedAuditTrail') as mock_audit:
            mock_instance = MagicMock()
            mock_audit.return_value = mock_instance
            
            merger = CopilotMerger(audit_enabled=True)
            
            result = merger.generate_merged_file(
                repo_path,
                cortex_template="# CORTEX\nTemplate"
            )
            
            assert "preserved_sections" in result
            assert "My Custom Rules" in result["preserved_sections"]
