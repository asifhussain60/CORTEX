"""Integration tests — Verify skill-prompt routing after consolidation (Phase M7-b).

Check that:
1. Each skill references the correct detail-prompt-file
2. All detail prompts are marked non-production-admin
3. No circular skill→prompt dependencies
4. Skill-first routing works correctly
"""
from __future__ import annotations

import pathlib
import re
import yaml

import pytest

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
SKILLS_DIR = CORTEX_ROOT / ".github" / "skills"
PROMPTS_DIR = CORTEX_ROOT / ".github" / "prompts"


def _load_yaml_frontmatter(file_path: pathlib.Path) -> dict:
    """Extract YAML frontmatter from markdown file."""
    content = file_path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}


class TestSkillPromptRouting:
    """Verify skill-prompt wiring after M7-b consolidation."""

    def test_skills_reference_detail_prompts(self) -> None:
        """Each skill with detail-prompt-file references a valid prompt."""
        violations: list[str] = []
        for skill_file in SKILLS_DIR.rglob("SKILL.md"):
            frontmatter = _load_yaml_frontmatter(skill_file)
            detail_prompt = frontmatter.get("detail-prompt-file")
            if not detail_prompt:
                continue
            
            # Resolve relative path
            prompt_path = (skill_file.parent / detail_prompt).resolve()
            if not prompt_path.exists():
                violations.append(
                    f"{skill_file.relative_to(CORTEX_ROOT)}: "
                    f"detail-prompt-file '{detail_prompt}' does not exist"
                )
        
        assert not violations, f"Invalid detail-prompt-file references:\n" + "\n".join(violations)

    def test_detail_prompts_are_non_production_admin(self) -> None:
        """All detail prompts must be marked scope: non-production-admin."""
        expected_detail_prompts = {
            "cortex-architect.prompt.md",
            "cortex-architecture-review.prompt.md",
            "cortex-doc.prompt.md",
            "cortex-sync.prompt.md",
            "cortex-total-recall.prompt.md",
            "cortex-trainer.prompt.md",
        }
        
        violations: list[str] = []
        for prompt_file in PROMPTS_DIR.glob("*.prompt.md"):
            if prompt_file.name not in expected_detail_prompts:
                continue
            
            frontmatter = _load_yaml_frontmatter(prompt_file)
            scope = frontmatter.get("scope")
            
            # Architect is production-critical
            if prompt_file.name == "cortex-architect.prompt.md":
                # Should NOT have scope: non-production-admin
                if scope == "non-production-admin":
                    violations.append(
                        f"{prompt_file.name}: Should NOT have scope: non-production-admin (is production-critical)"
                    )
            else:
                # All others must be non-production-admin
                if scope != "non-production-admin":
                    violations.append(
                        f"{prompt_file.name}: Missing scope: non-production-admin"
                    )
        
        assert not violations, f"Scope marker violations:\n" + "\n".join(violations)

    def test_cortex_agent_references_cortex_prompt(self) -> None:
        """CORTEX.agent.md must reference CORTEX.prompt.md."""
        agent_file = CORTEX_ROOT / ".github" / "agents" / "CORTEX.agent.md"
        frontmatter = _load_yaml_frontmatter(agent_file)
        
        system_prompt = frontmatter.get("system-prompt-file")
        assert system_prompt == "../prompts/CORTEX.prompt.md", (
            f"CORTEX.agent.md must reference CORTEX.prompt.md, got: {system_prompt}"
        )

    def test_cortex_prompt_is_production(self) -> None:
        """CORTEX.prompt.md must NOT have scope: non-production-admin."""
        prompt_file = PROMPTS_DIR / "CORTEX.prompt.md"
        frontmatter = _load_yaml_frontmatter(prompt_file)
        
        scope = frontmatter.get("scope")
        assert scope != "non-production-admin", (
            "CORTEX.prompt.md must be production (no scope: non-production-admin)"
        )

    def test_no_skill_circular_dependencies(self) -> None:
        """Verify no bidirectional skill↔prompt circular dependencies."""
        # Build map of detail-prompt file → skills using it
        prompt_to_skills: dict[str, list[str]] = {}
        
        for skill_file in SKILLS_DIR.rglob("SKILL.md"):
            frontmatter = _load_yaml_frontmatter(skill_file)
            detail_prompt = frontmatter.get("detail-prompt-file")
            if detail_prompt:
                skill_name = skill_file.parent.name
                if detail_prompt not in prompt_to_skills:
                    prompt_to_skills[detail_prompt] = []
                prompt_to_skills[detail_prompt].append(skill_name)
        
        # Check: no detail prompt should reference back to any skill
        # (This would be a circular dependency)
        violations: list[str] = []
        for detail_prompt_path in prompt_to_skills:
            # Resolve to actual file
            prompt_file = (SKILLS_DIR / detail_prompt_path).resolve()
            if not prompt_file.exists():
                continue
            
            content = prompt_file.read_text(encoding="utf-8")
            # Check if it references any skill directory
            if ".github/skills/" in content:
                violations.append(
                    f"Detail prompt {detail_prompt_path} has circular reference to skills"
                )
        
        assert not violations, f"Circular dependencies detected:\n" + "\n".join(violations)

    def test_routing_through_cortex_agent(self) -> None:
        """Verify routing flow: user → CORTEX.agent.md → CORTEX.prompt.md → skills."""
        # Check CORTEX.agent.md
        agent = CORTEX_ROOT / ".github" / "agents" / "CORTEX.agent.md"
        agent_name = _load_yaml_frontmatter(agent).get("name")
        assert agent_name == "CORTEX", "CORTEX.agent.md must have name: CORTEX"
        
        # Check CORTEX.prompt.md exists and is referenced
        prompt = CORTEX_ROOT / ".github" / "prompts" / "CORTEX.prompt.md"
        assert prompt.exists(), "CORTEX.prompt.md must exist"
        
        # Check skills are discoverable
        skill_files = list(SKILLS_DIR.rglob("SKILL.md"))
        assert len(skill_files) > 0, "No skills found"
        
        # Check each skill has its discovery metadata
        for skill_file in skill_files:
            frontmatter = _load_yaml_frontmatter(skill_file)
            assert "name" in frontmatter, f"{skill_file}: Missing name in frontmatter"
            assert "description" in frontmatter, f"{skill_file}: Missing description in frontmatter"


class TestArchiveIntegration:
    """Verify archive directory for historical prompts."""

    def test_archive_readme_exists(self) -> None:
        """Archive README documents the consolidation."""
        archive_readme = PROMPTS_DIR / "_archived" / "README.md"
        assert archive_readme.exists(), "_archived/README.md must exist for consolidation history"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
