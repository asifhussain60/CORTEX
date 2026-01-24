asifhussain60: Follow instructions in [CORTEX.prompt.md](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/CORTEX.prompt.md).
refactor and enhance all #file:prompts and their #file:agents . Review the purpose of each and then enhance to cover the entire CORTEX production implementation including all new changes and enhancements by running a discovery cycle for all prompts. Each prompt should first run a discovery cycle is new features could impact their purpose.

e.g. #file:cortex-total-recall.prompt.md and its agent should discover and wire in all new features and existing features with the master orchestrator.

#file:CORTEX.prompt.md and #file:copilot-instruction.md should be designed to wrk perfectly with CORTEX.
Rewrite prompts and agents if you need to. Clean up both folders with by deleting unneeded files.

GitHub Copilot: ## 🧠 CORTEX Analysis & Refactoring
**Author:** Asif Hussain | **Phase:** PHASE-DOC-REMEDIATION | **Orchestrator:** MasterOrchestrator ✅

---

I'll perform a comprehensive discovery cycle to understand all prompts and agents, then refactor them to align with the current CORTEX production implementation. Let me start by gathering the current state of all files. 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-builder.prompt.md#1-1), lines 1 to 150

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-deploy.prompt.md#1-1), lines 1 to 150

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-doc.prompt.md#1-1), lines 1 to 150

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-feedback.prompt.md#1-1), lines 1 to 150

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-git-commit.prompt.md#1-1), lines 1 to 150

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-review.prompt.md#1-1), lines 1 to 150

Now let me continue reading the remaining prompts and agents: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/builder/cortex-builder-continuation.prompt.md)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/planning/cortex-governance.prompt.md)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/planning/cortex-planner.prompt.md)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/utilities/cortex-feedback-agent.prompt.md)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/utilities/cortex-gap-detection.prompt.md)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/utilities/cortex-total-recall-agent.prompt.md)

Now let me read the review-related prompts: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/review/cortex-review-assumptions.prompt.md)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/review/cortex-review-brittleness.prompt.md)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/review/cortex-review-debt.prompt.md)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/review/cortex-review-hallucination.prompt.md)

Now let me read the agent files to understand their structure: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/agents/cortex-builder.md#1-1), lines 1 to 200

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/agents/cortex-review.md)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/agents/cortex-planner.md#1-1), lines 1 to 200

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/agents/cortex-documentation.md#1-1), lines 1 to 200

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/agents/README-AUTONOMOUS.md#1-1), lines 1 to 200

Now let me check the remaining agents and discover the current state of the codebase to understand new features: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/agents)

Searched text for `class.*Orchestrator|def execute|def process` (`**/cortex/orchestrators/**/*.py`), 20 results

Searched text for `@mcp_tool|@tool|register_tool` (`**/cortex/mcp/**/*.py`), 20 results

Let me discover more about the current state of the system: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/orchestrators/core)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/tools)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/brain/core)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/tools/total_recall_agent.py#1-1), lines 1 to 100

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/tools/wiring_validator.py#1-1), lines 1 to 100

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/orchestrators/core/master_orchestrator.py#1-1), lines 1 to 100

Now let me check the current test count and understand the full scope of the system: 

Ran terminal command: find /Users/asifhussain/PROJECTS/CORTEX/cortex -type f -name "*.py" | wc -l

Ran terminal command: head -200 _workspaces/roadmap/cortex-roadmap.yaml 2>/dev/null || head -200 _workspaces/roadmap/cortex-impl-map.yaml 2>/dev/null || echo "Roadmap file not found"

Now I have a comprehensive understanding of the system. Let me now analyze which files should be deleted and which should be rewritten. I'll start by creating the enhanced, consolidated prompts and agents. 

Ran terminal command: ls -la .github/prompts/ && ls -la .github/agents/

Now I have a clear picture. Let me create the consolidated, production-ready prompt and agent structure. I'll:

1. **Delete obsolete/redundant files**
2. **Create unified CORTEX.prompt.md** (master orchestrator system prompt)
3. **Create unified copilot-instruction.md** (companion guide)
4. **Create simplified agent structure with specialized agents**

Let me start by creating the new, enhanced files: 