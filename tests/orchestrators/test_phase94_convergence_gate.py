"""
Phase 94 — Universal Convergence Gate (CORE-068)
RED tests: governance rule, template schema, prompt/agent convergence mandates.

Tests verify:
1. CORE-068 exists in skull-rules.yaml with correct schema
2. Phase template (_template.yaml) has mandatory convergence_gate: block
3. cortex-architect.prompt.md has convergence steps in IMPLEMENT/FIX/REFACTOR modes
4. CORTEX.prompt.md has convergence in FIX mode and checklist
5. cortex-executor.md agent has convergence after Sweep Gate
6. cortex-vacuum.md agent has convergence rescan loop
7. cortex-debugger.md agent has convergence after fix-plan
8. refresh_prompt_suite.py has convergence drift detection
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parent.parent.parent
SKULL_RULES = ROOT / "cortex-registry" / "core" / "tier0-skull" / "skull-rules.yaml"
PHASE_TEMPLATE = ROOT / "cortex-registry" / "planning" / "phases" / "_template.yaml"
ARCHITECT_PROMPT = ROOT / ".github" / "prompts" / "cortex-architect.prompt.md"
CORTEX_PROMPT = ROOT / ".github" / "prompts" / "CORTEX.prompt.md"
EXECUTOR_AGENT = ROOT / ".github" / "agents" / "core" / "cortex-executor.md"
VACUUM_AGENT = ROOT / ".github" / "agents" / "support" / "cortex-vacuum.md"
DEBUGGER_AGENT = ROOT / ".github" / "agents" / "support" / "cortex-debugger.md"
REFRESH_SCRIPT = ROOT / "scripts" / "refresh_prompt_suite.py"
COPILOT_INSTRUCTIONS = ROOT / ".github" / "copilot-instructions.md"


# ============================================================================
# GAP-94-01: CORE-068 governance rule in skull-rules.yaml
# ============================================================================

class TestCore068GovernanceRule:
    """CORE-068 must exist in skull-rules.yaml with correct schema."""

    @pytest.fixture(autouse=True)
    def _load_rules(self) -> None:
        text = SKULL_RULES.read_text()
        self.rules_text = text
        # Parse just the rules list
        data = yaml.safe_load(text)
        rules = []
        if isinstance(data, dict) and "rules" in data:
            rules = data["rules"]
        elif isinstance(data, dict):
            # skull-rules has nested structure — find all rule_id entries
            pass
        self.rules_text = text

    def test_core_068_rule_id_exists(self) -> None:
        """CORE-068 rule_id must appear in skull-rules.yaml."""
        assert "rule_id: CORE-068" in self.rules_text, (
            "CORE-068 (Universal Convergence Gate) not found in skull-rules.yaml"
        )

    def test_core_068_has_tier_0(self) -> None:
        """CORE-068 must be tier 0 (immutable)."""
        # Find the CORE-068 block and check tier
        idx = self.rules_text.find("rule_id: CORE-068")
        assert idx != -1, "CORE-068 not found"
        block = self.rules_text[idx:idx + 2000]
        assert "tier: 0" in block, "CORE-068 must be tier 0"

    def test_core_068_has_severity_p0(self) -> None:
        """CORE-068 must have severity P0."""
        idx = self.rules_text.find("rule_id: CORE-068")
        assert idx != -1, "CORE-068 not found"
        block = self.rules_text[idx:idx + 2000]
        assert "severity: P0" in block, "CORE-068 must have severity P0"

    def test_core_068_applies_to_code_modifying_intents(self) -> None:
        """CORE-068 must list IMPLEMENT, FIX, REFACTOR, AUDIT, DEBUG, VACUUM, HEALTH."""
        idx = self.rules_text.find("rule_id: CORE-068")
        assert idx != -1, "CORE-068 not found"
        block = self.rules_text[idx:idx + 3000]
        for intent in ["IMPLEMENT", "FIX", "REFACTOR", "AUDIT", "DEBUG", "VACUUM", "HEALTH"]:
            assert intent in block, f"CORE-068 must apply to {intent} intent"

    def test_core_068_exempts_read_only_intents(self) -> None:
        """CORE-068 must exempt QUERY, DESIGN, PLAN, DIGEST, REPHRASE."""
        idx = self.rules_text.find("rule_id: CORE-068")
        assert idx != -1, "CORE-068 not found"
        block = self.rules_text[idx:idx + 3000]
        assert "exempt" in block.lower(), "CORE-068 must have exempt section"
        for intent in ["QUERY", "DESIGN", "PLAN", "DIGEST", "REPHRASE"]:
            assert intent in block, f"CORE-068 must exempt {intent}"

    def test_core_068_references_detect_fix_rescan_primitive(self) -> None:
        """CORE-068 must reference the detect-fix-rescan-loop primitive."""
        idx = self.rules_text.find("rule_id: CORE-068")
        assert idx != -1, "CORE-068 not found"
        block = self.rules_text[idx:idx + 3000]
        assert "detect-fix-rescan-loop" in block or "detect_fix_rescan" in block, (
            "CORE-068 must reference detect-fix-rescan-loop primitive"
        )

    def test_core_068_has_max_cycles(self) -> None:
        """CORE-068 must specify max_cycles default."""
        idx = self.rules_text.find("rule_id: CORE-068")
        assert idx != -1, "CORE-068 not found"
        block = self.rules_text[idx:idx + 3000]
        assert "max_cycles" in block, "CORE-068 must specify max_cycles"

    def test_core_068_depends_on_core_064_and_core_008(self) -> None:
        """CORE-068 must declare dependency on CORE-064 and CORE-008."""
        idx = self.rules_text.find("rule_id: CORE-068")
        assert idx != -1, "CORE-068 not found"
        block = self.rules_text[idx:idx + 12000]
        assert "CORE-064" in block, "CORE-068 must depend on CORE-064"
        assert "CORE-008" in block, "CORE-068 must depend on CORE-008"


# ============================================================================
# GAP-94-02: Phase template convergence_gate: mandatory block
# ============================================================================

class TestPhaseTemplateConvergenceGate:
    """Phase template must include mandatory convergence_gate: block."""

    @pytest.fixture(autouse=True)
    def _load_template(self) -> None:
        self.template_text = PHASE_TEMPLATE.read_text()

    def test_convergence_gate_block_exists(self) -> None:
        """_template.yaml must contain convergence_gate: block."""
        assert "convergence_gate:" in self.template_text, (
            "Phase template missing mandatory convergence_gate: block"
        )

    def test_convergence_gate_has_detect_step(self) -> None:
        """convergence_gate must have detect_step field."""
        assert "detect_step:" in self.template_text, (
            "convergence_gate missing detect_step field"
        )

    def test_convergence_gate_has_fix_step(self) -> None:
        """convergence_gate must have fix_step field."""
        assert "fix_step:" in self.template_text, (
            "convergence_gate missing fix_step field"
        )

    def test_convergence_gate_has_success_predicate(self) -> None:
        """convergence_gate must have success_predicate field."""
        assert "success_predicate:" in self.template_text, (
            "convergence_gate missing success_predicate field"
        )

    def test_convergence_gate_has_max_cycles(self) -> None:
        """convergence_gate must have max_cycles field."""
        # Check within template convergence_gate context
        assert "max_cycles:" in self.template_text, (
            "convergence_gate missing max_cycles field"
        )

    def test_convergence_gate_has_primitive_ref(self) -> None:
        """convergence_gate must reference detect-fix-rescan-loop primitive."""
        assert "detect-fix-rescan-loop" in self.template_text, (
            "convergence_gate missing reference to detect-fix-rescan-loop primitive"
        )

    def test_convergence_gate_blocks_ac_complete(self) -> None:
        """convergence_gate must have blocks_ac_complete: true."""
        assert "blocks_ac_complete: true" in self.template_text, (
            "convergence_gate must block AC_COMPLETE until convergence achieved"
        )

    def test_convergence_gate_references_core_068(self) -> None:
        """Template must reference CORE-068 in governance_authority."""
        assert "CORE-068" in self.template_text, (
            "Phase template must reference CORE-068 in governance_authority"
        )


# ============================================================================
# GAP-94-03: cortex-architect.prompt.md convergence in IMPLEMENT/FIX/REFACTOR
# ============================================================================

class TestArchitectPromptConvergence:
    """cortex-architect.prompt.md must have convergence steps in code-modifying modes."""

    @pytest.fixture(autouse=True)
    def _load_prompt(self) -> None:
        self.prompt_text = ARCHITECT_PROMPT.read_text()

    def test_implement_mode_has_convergence_gate(self) -> None:
        """IMPLEMENT mode sequence must include convergence gate step."""
        # Find IMPLEMENT section and check for convergence
        idx = self.prompt_text.find("## ⚡ IMPLEMENT MODE")
        assert idx != -1, "IMPLEMENT MODE section not found"
        section = self.prompt_text[idx:idx + 2000]
        assert re.search(r"[Cc]onvergence", section), (
            "IMPLEMENT mode missing convergence gate step"
        )

    def test_fix_mode_has_convergence_gate(self) -> None:
        """FIX mode sequence must include convergence gate step."""
        idx = self.prompt_text.find("## 🔧 FIX MODE")
        assert idx != -1, "FIX MODE section not found"
        section = self.prompt_text[idx:idx + 2000]
        assert re.search(r"[Cc]onvergence", section), (
            "FIX mode missing convergence gate step"
        )

    def test_refactor_mode_has_convergence_gate(self) -> None:
        """REFACTOR mode sequence must include convergence gate step."""
        idx = self.prompt_text.find("## ♻️ REFACTOR MODE")
        assert idx != -1, "REFACTOR MODE section not found"
        section = self.prompt_text[idx:idx + 2000]
        assert re.search(r"[Cc]onvergence", section), (
            "REFACTOR mode missing convergence gate step"
        )

    def test_universal_convergence_section_exists(self) -> None:
        """A dedicated Universal Convergence Gate section must exist."""
        assert "Universal Convergence Gate" in self.prompt_text or "CORE-068" in self.prompt_text, (
            "cortex-architect.prompt.md missing Universal Convergence Gate section or CORE-068 reference"
        )

    def test_convergence_references_detect_fix_rescan(self) -> None:
        """Prompt must reference detect-fix-rescan-loop primitive."""
        assert "detect-fix-rescan" in self.prompt_text or "detect→fix→rescan" in self.prompt_text, (
            "cortex-architect.prompt.md missing detect-fix-rescan reference"
        )


# ============================================================================
# GAP-94-04: CORTEX.prompt.md convergence in FIX mode + checklist
# ============================================================================

class TestCortexPromptConvergence:
    """CORTEX.prompt.md must have convergence in FIX mode and operation checklist."""

    @pytest.fixture(autouse=True)
    def _load_prompt(self) -> None:
        self.prompt_text = CORTEX_PROMPT.read_text()

    def test_fix_mode_has_convergence(self) -> None:
        """FIX mode in CORTEX.prompt.md must include convergence step."""
        idx = self.prompt_text.find("## 🔧 FIX MODE")
        assert idx != -1, "FIX MODE section not found in CORTEX.prompt.md"
        section = self.prompt_text[idx:idx + 2000]
        assert re.search(r"[Cc]onvergence", section), (
            "CORTEX.prompt.md FIX mode missing convergence step"
        )

    def test_checklist_has_convergence(self) -> None:
        """Operation checklist must include convergence gate item."""
        # The checklist is the "Every operation:" section
        assert re.search(r"[Cc]onvergence.*[Gg]ate|[Cc]onvergence.*clean|rescan.*clean", self.prompt_text), (
            "CORTEX.prompt.md operation checklist missing convergence gate item"
        )

    def test_core_068_referenced(self) -> None:
        """CORTEX.prompt.md must reference CORE-068."""
        assert "CORE-068" in self.prompt_text, (
            "CORTEX.prompt.md missing CORE-068 reference"
        )


# ============================================================================
# GAP-94-05: cortex-executor.md convergence after Sweep Gate
# ============================================================================

class TestExecutorAgentConvergence:
    """cortex-executor.md must have convergence loop after Sweep Gate."""

    @pytest.fixture(autouse=True)
    def _load_agent(self) -> None:
        self.agent_text = EXECUTOR_AGENT.read_text()

    def test_convergence_in_execution_flow(self) -> None:
        """Execution flow must include convergence gate."""
        assert re.search(r"[Cc]onvergence", self.agent_text), (
            "cortex-executor.md missing convergence in execution flow"
        )

    def test_convergence_after_sweep_gate(self) -> None:
        """Convergence must appear after Sweep Gate in the flow."""
        sweep_idx = self.agent_text.find("Sweep Gate")
        assert sweep_idx != -1, "Sweep Gate not found in cortex-executor.md"
        after_sweep = self.agent_text[sweep_idx:]
        assert re.search(r"[Cc]onvergence", after_sweep), (
            "Convergence must appear after Sweep Gate"
        )

    def test_core_068_referenced(self) -> None:
        """cortex-executor.md must reference CORE-068."""
        assert "CORE-068" in self.agent_text, (
            "cortex-executor.md missing CORE-068 reference"
        )


# ============================================================================
# GAP-94-06: cortex-vacuum.md convergence rescan loop
# ============================================================================

class TestVacuumAgentConvergence:
    """cortex-vacuum.md must have convergence rescan loop."""

    @pytest.fixture(autouse=True)
    def _load_agent(self) -> None:
        self.agent_text = VACUUM_AGENT.read_text()

    def test_convergence_exists(self) -> None:
        """cortex-vacuum.md must mention convergence or rescan loop."""
        assert re.search(r"[Cc]onvergence|rescan|re-scan", self.agent_text), (
            "cortex-vacuum.md missing convergence/rescan loop"
        )

    def test_core_068_referenced(self) -> None:
        """cortex-vacuum.md must reference CORE-068."""
        assert "CORE-068" in self.agent_text, (
            "cortex-vacuum.md missing CORE-068 reference"
        )


# ============================================================================
# GAP-94-07: cortex-debugger.md convergence after fix-plan
# ============================================================================

class TestDebuggerAgentConvergence:
    """cortex-debugger.md must have convergence after fix-plan execution."""

    @pytest.fixture(autouse=True)
    def _load_agent(self) -> None:
        self.agent_text = DEBUGGER_AGENT.read_text()

    def test_convergence_exists(self) -> None:
        """cortex-debugger.md must mention convergence or rescan loop."""
        assert re.search(r"[Cc]onvergence|rescan|re-scan", self.agent_text), (
            "cortex-debugger.md missing convergence/rescan loop"
        )

    def test_core_068_referenced(self) -> None:
        """cortex-debugger.md must reference CORE-068."""
        assert "CORE-068" in self.agent_text, (
            "cortex-debugger.md missing CORE-068 reference"
        )


# ============================================================================
# GAP-94-08: refresh_prompt_suite.py convergence drift detection
# ============================================================================

class TestRefreshScriptConvergence:
    """refresh_prompt_suite.py must detect convergence-related drift."""

    @pytest.fixture(autouse=True)
    def _load_script(self) -> None:
        self.script_text = REFRESH_SCRIPT.read_text()

    def test_convergence_drift_detection(self) -> None:
        """Script must check for convergence-related drift."""
        assert re.search(r"convergence|CORE.068", self.script_text), (
            "refresh_prompt_suite.py missing convergence drift detection"
        )


# ============================================================================
# GAP-94-09: copilot-instructions.md CORE-068 reference
# ============================================================================

class TestCopilotInstructionsConvergence:
    """copilot-instructions.md must reference CORE-068."""

    @pytest.fixture(autouse=True)
    def _load_file(self) -> None:
        self.text = COPILOT_INSTRUCTIONS.read_text()

    def test_core_068_in_rules_table(self) -> None:
        """CORE-068 must appear in the CORE rules table."""
        assert "CORE-068" in self.text, (
            "copilot-instructions.md missing CORE-068 in development standards"
        )

    def test_convergence_gate_mentioned(self) -> None:
        """Convergence gate must be mentioned in copilot-instructions.md."""
        assert re.search(r"[Cc]onvergence", self.text), (
            "copilot-instructions.md missing convergence gate reference"
        )
