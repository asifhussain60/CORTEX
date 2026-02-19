"""
Tests for .github folder protection in vacuum orchestrator.

AC-ID: VACUUM-GITHUB-GUARD-001
Governance: CORE-008 (TDD mandatory)

Covers:
- Protected files are never proposed for deletion
- Deprecated files (DEPRECATED-*.md) are safe vacuum targets
- Informational root files (AGENT-INDEX.md, README.md in agents/ and prompts/)
  are treated as low-risk candidates only when strategy is AGGRESSIVE
- Active prompts (*.prompt.md) are always protected
- Active agent specs (agents/**/*.md without DEPRECATED- prefix) are protected
- .github subfolder roots comply with CORTEX naming governance (no non-governed files)
- GithubFolderGuard.is_protected returns correct values for all edge cases
"""

import pytest
from pathlib import Path

from cortex_intelligence.memory.tier1_learned.orchestrators.cleaners.github_folder_guard import (
    GithubFolderGuard,
    GithubFileClassification,
)


# =============================================================================
# FIXTURES
# =============================================================================


@pytest.fixture
def guard():
    """GithubFolderGuard instance for testing."""
    return GithubFolderGuard()


# =============================================================================
# HELPER
# =============================================================================


def p(rel: str) -> Path:
    """Convert relative string to Path for readability."""
    return Path(rel)


# =============================================================================
# ALWAYS-PROTECTED: active prompts
# =============================================================================


class TestPromptFilesAlwaysProtected:
    """*.prompt.md files in .github/prompts/ must NEVER be deleted."""

    def test_cortex_architect_prompt_is_protected(self, guard):
        assert guard.is_protected(p(".github/prompts/cortex-architect.prompt.md"))

    def test_cortex_prompt_md_is_protected(self, guard):
        assert guard.is_protected(p(".github/prompts/CORTEX.prompt.md"))

    def test_any_prompt_md_is_protected(self, guard):
        assert guard.is_protected(p(".github/prompts/my-agent.prompt.md"))

    def test_classify_prompt_returns_protected(self, guard):
        result = guard.classify(p(".github/prompts/cortex-architect.prompt.md"))
        assert result == GithubFileClassification.PROTECTED


# =============================================================================
# ALWAYS-PROTECTED: active agent specs
# =============================================================================


class TestActiveAgentSpecsAlwaysProtected:
    """Agent spec .md files without DEPRECATED- prefix are always protected."""

    def test_cortex_md_in_agents_core_is_protected(self, guard):
        assert guard.is_protected(p(".github/agents/core/CORTEX.md"))

    def test_cortex_architect_agent_is_protected(self, guard):
        assert guard.is_protected(p(".github/agents/core/cortex-architect.md"))

    def test_cortex_auditor_is_protected(self, guard):
        assert guard.is_protected(p(".github/agents/core/cortex-auditor.md"))

    def test_architecture_integrity_agent_is_protected(self, guard):
        assert guard.is_protected(p(".github/agents/core/architecture-integrity-agent.md"))

    def test_education_agent_is_protected(self, guard):
        assert guard.is_protected(p(".github/agents/education/cortex-ask-coordinator.md"))

    def test_orchestration_agent_is_protected(self, guard):
        assert guard.is_protected(p(".github/agents/orchestration/cortex-universal-orchestration.md"))

    def test_support_debugger_is_protected(self, guard):
        assert guard.is_protected(p(".github/agents/support/cortex-debugger.md"))

    def test_support_vacuum_agent_is_protected(self, guard):
        assert guard.is_protected(p(".github/agents/support/cortex-vacuum.md"))

    def test_classify_active_agent_returns_protected(self, guard):
        result = guard.classify(p(".github/agents/core/cortex-architect.md"))
        assert result == GithubFileClassification.PROTECTED


# =============================================================================
# ALWAYS-PROTECTED: non-md files in agents (Python, etc.)
# =============================================================================


class TestNonMarkdownFilesAlwaysProtected:
    """Non-.md files in .github (scripts, py, etc.) must never be vacuum targets."""

    def test_python_impl_in_agents_is_protected(self, guard):
        assert guard.is_protected(p(".github/agents/core/PHASE4-METHODS-IMPLEMENTATION-REFERENCE.py"))

    def test_py_script_in_agents_is_protected(self, guard):
        assert guard.is_protected(p(".github/agents/core/response-template-generator.py"))

    def test_workflow_yaml_is_protected(self, guard):
        assert guard.is_protected(p(".github/workflows/ci.yml"))

    def test_hook_script_is_protected(self, guard):
        assert guard.is_protected(p(".github/hooks/pre-commit"))


# =============================================================================
# ALWAYS-PROTECTED: reference docs inside prompts/
# =============================================================================


class TestPromptReferenceDocsProtected:
    """Files under .github/prompts/reference/ are protected as setup references."""

    def test_mcp_setup_guide_is_protected(self, guard):
        assert guard.is_protected(p(".github/prompts/reference/mcp-setup-guide.md"))

    def test_any_file_under_prompts_reference_is_protected(self, guard):
        assert guard.is_protected(p(".github/prompts/reference/any-guide.md"))


# =============================================================================
# ALWAYS-PROTECTED: templates that are active
# =============================================================================


class TestActiveTemplatesProtected:
    """Active template .md files are protected."""

    def test_cortex_response_templates_is_protected(self, guard):
        assert guard.is_protected(p(".github/templates/cortex-response-templates.md"))

    def test_chat_vs_terminal_guide_is_protected(self, guard):
        assert guard.is_protected(p(".github/templates/chat-vs-terminal-guide.md"))


# =============================================================================
# VACUUM-ELIGIBLE: DEPRECATED-* files
# =============================================================================


class TestDeprecatedFilesAreVacuumEligible:
    """Files with DEPRECATED- prefix are legitimate vacuum targets."""

    def test_deprecated_cortex_designer_is_eligible(self, guard):
        assert not guard.is_protected(p(".github/agents/core/DEPRECATED-cortex-designer.md"))

    def test_deprecated_mcp_gateway_is_eligible(self, guard):
        assert not guard.is_protected(p(".github/agents/core/DEPRECATED-cortex-mcp-gateway.md"))

    def test_deprecated_planning_orchestrator_is_eligible(self, guard):
        assert not guard.is_protected(p(".github/agents/core/DEPRECATED-planning-orchestrator.md"))

    def test_any_deprecated_prefix_md_is_eligible(self, guard):
        assert not guard.is_protected(p(".github/agents/support/DEPRECATED-old-tool.md"))

    def test_classify_deprecated_returns_vacuum_eligible(self, guard):
        result = guard.classify(p(".github/agents/core/DEPRECATED-cortex-designer.md"))
        assert result == GithubFileClassification.VACUUM_ELIGIBLE


# =============================================================================
# VACUUM-ELIGIBLE: informational root files
# =============================================================================


class TestInformationalRootFilesAreEligible:
    """README.md and index files in folder roots are informational and vacuum-eligible."""

    def test_agent_index_md_is_eligible(self, guard):
        assert not guard.is_protected(p(".github/agents/AGENT-INDEX.md"))

    def test_agents_readme_is_eligible(self, guard):
        assert not guard.is_protected(p(".github/agents/README.md"))

    def test_prompts_readme_is_eligible(self, guard):
        assert not guard.is_protected(p(".github/prompts/README.md"))

    def test_classify_agent_index_returns_vacuum_eligible(self, guard):
        result = guard.classify(p(".github/agents/AGENT-INDEX.md"))
        assert result == GithubFileClassification.VACUUM_ELIGIBLE


# =============================================================================
# NOT A .github PATH — guard ignores it
# =============================================================================


class TestNonGithubPathsAreIgnored:
    """GithubFolderGuard only governs .github/ — other paths are not its concern."""

    def test_regular_readme_outside_github_not_evaluated(self, guard):
        """Guard returns None/UNRELATED for files outside .github/."""
        result = guard.classify(p("docs/README.md"))
        assert result == GithubFileClassification.UNRELATED

    def test_cortex_md_outside_github_not_evaluated(self, guard):
        result = guard.classify(p("cortex/agents/CORTEX.md"))
        assert result == GithubFileClassification.UNRELATED

    def test_is_protected_raises_for_non_github_path(self, guard):
        """is_protected raises ValueError for paths outside .github/ to avoid misuse."""
        with pytest.raises(ValueError, match=r"\.github"):
            guard.is_protected(p("some/other/file.md"))


# =============================================================================
# NAMING GOVERNANCE: subfolder roots
# =============================================================================


class TestSubfolderNamingGovernance:
    """Subfolders inside .github/ must follow lowercase-kebab naming."""

    def test_well_named_subfolder_passes(self, guard):
        assert guard.is_valid_subfolder_name("agents") is True
        assert guard.is_valid_subfolder_name("prompts") is True
        assert guard.is_valid_subfolder_name("templates") is True
        assert guard.is_valid_subfolder_name("cortex-config") is True

    def test_uppercase_subfolder_fails_governance(self, guard):
        assert guard.is_valid_subfolder_name("AGENTS") is False

    def test_mixed_case_subfolder_fails_governance(self, guard):
        assert guard.is_valid_subfolder_name("Agents") is False

    def test_underscore_subfolder_fails_governance(self, guard):
        assert guard.is_valid_subfolder_name("my_agents") is False

    def test_numeric_start_fails_governance(self, guard):
        assert guard.is_valid_subfolder_name("1agents") is False

    def test_empty_name_fails(self, guard):
        assert guard.is_valid_subfolder_name("") is False

    def test_find_governance_violations_in_github(self, guard, tmp_path):
        """Detect subfolders with non-compliant names."""
        # Create compliant and non-compliant subfolders
        github_dir = tmp_path / ".github"
        (github_dir / "agents").mkdir(parents=True)
        (github_dir / "BAD_FOLDER").mkdir(parents=True)
        (github_dir / "Also-Bad").mkdir(parents=True)
        (github_dir / "good-folder").mkdir(parents=True)

        violations = guard.find_naming_violations(github_dir)
        violation_names = {v.name for v in violations}

        assert "BAD_FOLDER" in violation_names
        assert "Also-Bad" in violation_names
        assert "agents" not in violation_names
        assert "good-folder" not in violation_names
