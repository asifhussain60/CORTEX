```markdown
# Tutorial 03 — Getting Started: Customizing CORTEX

> **Duration:** 8 minutes · **Audience:** Tech Leads, Platform Engineers, Advanced Users
> **Depth:** 🔴 Tutorial — hands-on customization with real code
> **Prerequisites:** Tutorials 01-02 (comfortable using CORTEX), concept Video 04 (understands governance), concept Video 08 (understands workflow template engine)
> **Goal:** User can add a custom governance rule, create an MCP tool, and modify orchestrator behavior

---

## ⚠️ VISUAL IDENTITY — MANDATORY

> **ALL visuals** must use the CORTEX dark glassmorphism palette. Background: `#0a0e27`. Panels: `rgba(26, 31, 58, 0.7)` with `rgba(255, 255, 255, 0.1)` borders and 10-20px backdrop blur. Primary accent: `#00d4ff` (cyan). Secondary accent: `#7b61ff` (purple). Success: `#00ff88`. Warning: `#ffa500`. Danger: `#ff4444`. Info: `#3b82f6`. Text: `#ffffff` (primary), `#a0a6c0` (secondary). Glow: `0 0 20px rgba(0, 212, 255, 0.3)`. Shadow: `0 8px 32px rgba(0, 0, 0, 0.37)`.
>
> **Logo watermark:** CORTEX logo embossed bottom-right corner, 15-25% opacity, ~6% frame width, throughout entire video.
>
> **Typography:** Space Grotesk (headings, bold, fade-in with upward slide), Inter (body, fade), JetBrains Mono (code/labels, character-by-character reveal).

---

## PROMPT

Create an 8-minute animated tutorial video titled **"Getting Started: Customizing CORTEX"** using the visual identity above. Guide advanced users through three customization scenarios: adding a governance rule, creating an MCP tool, and modifying orchestrator configuration.

### Scene 1 — Why Customize? (0:00 – 0:45)

**Open on:** A glassmorphic "spectrum" showing CORTEX's flexibility.

**Left end:** "Out of the Box" — 38 CORE rules, 28 MCP tools, 51 orchestrators (all defaults)
**Right end:** "Fully Customized" — Your rules, your tools, your workflows

**The slider moves from left toward center:**
> "Most teams start with defaults and customize over time. This video shows you how."

**Three customization paths** appear as glassmorphic cards:

1. **Add a Governance Rule** — Enforce team-specific standards
2. **Create an MCP Tool** — Add custom capabilities to Copilot
3. **Configure Orchestrators** — Adjust behavior and priorities

**Narration:** "CORTEX is designed to grow with your team. Let's walk through each customization path."

### Scene 2 — Path 1: Adding a Governance Rule (0:45 – 3:00)

**Scenario:** Your team requires all API endpoints to have rate limiting. You want to enforce this automatically.

**Step 1: Choose the rule tier**

A glassmorphic tier diagram appears (from Video 4):
```
Tier 0: SKULL (Immutable) — CORE rules, can't change
Tier 1: Business         — Company-wide policies
Tier 2: Engineering      — Team standards ← YOUR RULE HERE
Tier 3: Learned          — Patterns from analysis
```

**Narration:** "Your rule is an engineering standard, so it goes in Tier 2."

**Step 2: Create the rule file**

File tree shows: `cortex-registry/core/tier2-engineering/`

New file created: `TEAM-001-api-rate-limiting.yaml`

**YAML content types in** (JetBrains Mono):

```yaml
rule_id: TEAM-001
title: API Rate Limiting Required
tier: 2
severity: P1
description: |
  All API endpoints must implement rate limiting to prevent abuse.
  
enforcement:
  scope: 
    - "cortex/api/**/*.py"
    - "cortex/routes/**/*.py"
  pattern:
    type: ast
    match: |
      # Function decorated with @app.route or @router.* 
      # must also have @rate_limit decorator
    violation_message: "API endpoint missing @rate_limit decorator"
    
auto_fix:
  enabled: true
  action: "Add @rate_limit(calls=100, period=60) decorator"
  
references:
  - "https://owasp.org/API-Security/"
```

**Governance badges** appear as the YAML builds:
- `rule_id: TEAM-001` → CORTEX naming convention ✅
- `severity: P1` → Will block commits ✅
- `auto_fix: enabled` → Autonomous remediation ✅

**Step 3: Test the rule**

Terminal shows:
```bash
# Run the governance validation suite
python3 -m pytest tests/governance/ -k "TEAM-001"
```

Test output:
```
tests/governance/test_team_rules.py::test_team_001_detects_missing_rate_limit PASSED ✅
tests/governance/test_team_rules.py::test_team_001_allows_rate_limited_endpoint PASSED ✅
```

**Step 4: Rule in action**

Show a developer trying to commit an API endpoint without `@rate_limit`:
- `git commit` triggers
- EnforcementOrchestrator scans
- TEAM-001 violation detected (amber flash)
- Violation card appears with auto-fix suggestion
- Developer applies fix → commit succeeds

**Analogy overlay** (`#a0a6c0`): *"You just taught CORTEX a new rule. It will enforce it automatically — forever."*

### Scene 3 — Path 2: Creating an MCP Tool (3:00 – 5:30)

**Scenario:** Your team frequently needs to check API response times. You want a tool in Copilot Chat to do this.

**Callback to Video 6:** A brief visual reference to the MCP architecture (2-second flashback, dimmed).

**Step 1: Create the tool file**

File tree shows: `cortex/mcp/tools/`

New file created: `check_api_latency.py`

**Python code types in:**

```python
"""MCP tool for checking API endpoint latency."""
import asyncio
import time
from cortex.mcp.registry import register_tool
from cortex.core.validation import validate_orchestrator_context


@register_tool(
    name="cortex_check_api_latency",
    description="Check response latency for an API endpoint"
)
async def check_api_latency(
    endpoint: str,
    method: str = "GET",
    timeout: float = 5.0,
    orchestrator_context: dict | None = None,
) -> dict:
    """Check API endpoint response latency.

    Args:
        endpoint: The URL to check.
        method: HTTP method (GET, POST, etc.).
        timeout: Request timeout in seconds.
        orchestrator_context: MCP routing context.

    Returns:
        Dict with latency metrics and status.
    """
    # Guard pattern — required by CORTEX authoring rules
    if orchestrator_context is not None:
        validate_orchestrator_context(orchestrator_context)
    
    start = time.perf_counter()
    # ... implementation using aiohttp or httpx ...
    latency_ms = (time.perf_counter() - start) * 1000
    
    return {
        "endpoint": endpoint,
        "method": method,
        "latency_ms": round(latency_ms, 2),
        "status": "healthy" if latency_ms < 200 else "slow",
    }
```

**Highlight the guard pattern** (zoom in, glassmorphic annotation):
```python
if orchestrator_context is not None:
    validate_orchestrator_context(orchestrator_context)
```
> "This pattern is REQUIRED — it allows tests to call the tool directly without MasterOrchestrator."

**Step 2: Register the tool**

Show `cortex/mcp/registry/mcp_registry.py` — the new tool appears in the registration list.

Counter updates: 28 → 29 registered tools.

**Step 3: Write the test first (TDD)**

**Callback to Video 5:** The TDD heartbeat pulses red briefly.

```python
# tests/mcp/test_check_api_latency.py
import pytest
from cortex.mcp.tools.check_api_latency import check_api_latency


class TestCheckApiLatency:
    """Tests for the API latency checker."""

    @pytest.mark.asyncio
    async def test_returns_latency_metrics(self):
        """Should return latency in milliseconds."""
        result = await check_api_latency(
            endpoint="https://example.com",
            orchestrator_context=None,  # Direct test invocation
        )
        assert "latency_ms" in result
        assert result["latency_ms"] > 0

    @pytest.mark.asyncio
    async def test_marks_slow_endpoints(self):
        """Endpoints over 200ms should be marked slow."""
        # ... mock slow response ...
```

Test runs → green ✅

**Step 4: Use the tool in Copilot Chat**

VS Code reloads. Copilot Chat input:
```
Check the latency of https://api.example.com/users
```

Copilot selects `cortex_check_api_latency` (tool tile glows). Response:

```
📊 API Latency Check

Endpoint: https://api.example.com/users
Method: GET
Latency: 87.34ms
Status: ✅ healthy

Threshold: <200ms = healthy, ≥200ms = slow
```

**Analogy overlay:** *"You just extended Copilot with a custom capability. It's now part of your team's toolkit."*

### Scene 4 — Path 3: Configuring Orchestrators (5:30 – 7:15)

**Scenario:** You want to adjust how aggressively CORTEX challenges requests (increase the challenge gate threshold).

**Step 1: Understand the configuration**

Show the configuration hierarchy:
```
cortex-registry/config/
├── orchestrators/
│   ├── master_orchestrator.yaml
│   ├── intent_router.yaml
│   └── tdd_orchestrator.yaml
├── governance/
│   └── enforcement.yaml
└── tools/
    └── mcp_config.yaml
```

**Step 2: Modify the configuration**

Open `cortex-registry/config/orchestrators/intent_router.yaml`:

```yaml
# Intent Router Configuration
intent_router:
  confidence_thresholds:
    direct_route: 0.85        # ≥ this → route immediately
    clarify_route: 0.60       # ≥ this → route with question
    reject_threshold: 0.30    # < this → ask user to rephrase
  
  challenge_gate:
    enabled: true
    risk_threshold: 0.4       # ← CHANGE THIS to 0.6
    scope_file_limit: 3       # Challenge if >3 files affected
  
  lens_auto_fetch:
    implement: true
    fix: true
    refactor: true
    query: false
```

**Animation:** The `risk_threshold` value changes from `0.4` to `0.6` with a cyan highlight.

**What this means** (glassmorphic info card):
> "Before: Challenge gate triggers at 40% risk. After: Only triggers at 60% risk. Fewer challenges, faster flow — but less safety net."

**Step 3: Validate the change**

Terminal:
```bash
# Validate all configuration files
python3 scripts/validate_governance_alignment.py
```

Output:
```
✅ Configuration validated
- intent_router.yaml: valid
- No breaking changes detected
- Risk threshold adjusted: 0.4 → 0.6 (within safe range)
```

**Step 4: See the effect**

Show two side-by-side scenarios:
- **Before (0.4 threshold):** Request triggers challenge (amber panel)
- **After (0.6 threshold):** Same request proceeds directly (cyan flow)

**Warning callout** (amber):
> "Higher thresholds = fewer challenges = faster flow, but you miss more potential issues. Choose carefully."

### Scene 5 — The Customization Pyramid (7:15 – 8:00)

**A pyramid diagram** materializes:

```
                    ▲
                   /|\
                  / | \
                 /  |  \
                /   |   \
               / TOOLS  \      ← Custom MCP tools
              /    |     \
             /-----------\
            / ORCHESTRATORS\   ← Configure behavior
           /       |        \
          /------------------\
         /    GOVERNANCE      \  ← Add rules (most common)
        /          |           \
       /------------------------\
      /         DEFAULTS         \  ← Start here (38 rules, 28 tools)
     /----------------------------\
```

Each layer glows as it's described:
- **Base (Defaults):** Where everyone starts
- **Governance:** Most common customization — add team rules
- **Orchestrators:** Adjust behavior without code changes
- **Tools:** Maximum customization — extend capabilities

**Key principle** (glassmorphic card):
> "Start with defaults. Customize governance first. Only add tools when you need capabilities CORTEX doesn't have."

**Closing text** (Space Grotesk):
**"Your standards. Enforced forever. Without you lifting a finger."**

**Vision callback:**
> *"The rules you just added will protect every commit by every engineer on your team — automatically. Go build the product."*

Logo pulse. End card.

---

## Notes

- This video is for ADVANCED users — assumes understanding of Videos 1-9.
- All customization examples are REAL and can be implemented in the actual CORTEX codebase.
- The governance rule example (TEAM-001) follows the actual YAML schema used in `cortex-registry/core/`.
- The MCP tool example includes the required guard pattern (`if orchestrator_context is not None`).
- Configuration paths match the real CORTEX repository structure.
- Sound design: configuration changes = soft "click"; validation pass = chime; pyramid layer activation = ascending tone.
- The pyramid diagram is the key takeaway — users should understand the customization hierarchy.

```
