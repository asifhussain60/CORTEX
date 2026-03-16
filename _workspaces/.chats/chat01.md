User: Follow instructions in [cortex-architect.prompt.md](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md).
confirm my understanding. CORTEX-V2 will use claude code as the basis of its operations using agents, subagents, SKILLS etc. but use CORTEX governance, orchestration, Workflow Composer, VSCode GitHub Copilot Chat Session rendering User Response Template(s) for feedback? Is this understanding ocrrect? My company has standardized Claude Code orchestration as the company standard which means all applicaiton should follow the agent, subagent, skills, claude.md folder struture, business rules etc. Based on this change, how should CORTEX be redesigned in this V2 version for maximum compatibility with orgnaizational standards and requirements.

GitHub Copilot: # 🧠 CORTEX QUERY
**Author:** Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.

---

> *"The best architectures are those that adapt to the needs of both the system and its stewards, harmonizing innovation with governance."*
> — Asif Hussain, **CORTEX Design Principles**

---

🧭 Orchestration: Classifier → Architect

---

## Intent Reflection

You are confirming your understanding of the CORTEX-V2 direction:  
- CORTEX-V2 will use Claude Code’s agent/subagent/skills model as the operational foundation.
- CORTEX governance, orchestration, Workflow Composer, and VSCode Copilot Chat rendering will remain for user interaction and compliance.
- Your company mandates Claude Code orchestration, agent/skill structure, and business rules as the standard for all applications.
- You want to know how CORTEX should be redesigned in V2 to maximize compatibility with these organizational standards.

---

## Golden Response Format

### 1. Confirmed Understanding

Your summary is correct:
- CORTEX-V2 will adopt the Claude agent/subagent/skills execution model as the operational backbone.
- CORTEX-specific governance, orchestration, workflow, and response rendering (including VSCode Copilot Chat and User Response Templates) will remain as the compliance and user-facing layer.
- All application logic, business rules, and folder structures must align with the Claude Code (agent/skill/claude.md) standard.

---

### 2. Key Redesign Principles for CORTEX-V2

**a. Agent/Skill-First Architecture**
- All operational logic should be encapsulated in agents and skills, following the Claude Code pattern.
- Each agent/subagent should have a clear, single responsibility and be discoverable via a registry.

**b. Strict Separation of Concerns**
- **Execution Layer:** Claude-style agents/skills/subagents for all business and technical logic.
- **Governance Layer:** CORTEX governance, audit, and compliance checks remain as wrappers/enforcers.
- **Orchestration Layer:** CORTEX orchestrators (MasterOrchestrator, AuditCoordinator, etc.) route requests to agents/skills as per workflow templates.
- **Rendering Layer:** All user feedback, chat, and output must use CORTEX’s inline VSCode Copilot Chat and User Response Templates.

**c. Unified Workflow and Registry**
- Maintain a single source of truth for agent/skill registration (e.g., `AGENT-INDEX.md`, `SKILL.md`).
- Workflow Composer should orchestrate agent/skill invocation based on workflow templates, not hardcoded logic.

**d. Compatibility and Extensibility**
- All new features and workflows must be implemented as agents/skills, not monolithic modules.
- Existing CORTEX features should be refactored into skills/agents where possible.
- Maintain backward compatibility for governance and audit pipelines.

**e. Documentation and Discoverability**
- All agents, skills, and workflows must be documented in the `claude.md` or equivalent, following company standards.
- Ensure prompt, skill, and agent instructions are always up to date and referenced in the registry.

---

### 3. Recommended Redesign Actions

1. **Refactor Core Logic:**  
   Move all business and orchestration logic into Claude-style agents and skills.

2. **Registry Alignment:**  
   Ensure all agents/skills are registered in a canonical index and discoverable by orchestrators.

3. **Governance Wrapping:**  
   Wrap all agent/skill execution with CORTEX governance, audit, and compliance checks.

4. **Workflow Composer Integration:**  
   Route all workflows through the Workflow Composer, which delegates to agents/skills as per templates.

5. **Response Rendering:**  
   Enforce all user-facing output through CORTEX’s VSCode Copilot Chat and User Response Templates.

6. **Documentation:**  
   Maintain up-to-date documentation for all agents, skills, and workflows in the required `claude.md` format.

---

### 4. Compatibility Checklist

- [x] Agent/skill structure matches Claude Code standard.
- [x] All orchestration and governance logic remains CORTEX-compliant.
- [x] Workflow Composer is the only entry point for workflow execution.
- [x] User feedback and output use CORTEX inline rendering.
- [x] All business rules and folder structures follow company standards.

---

### 5. Next Steps

- Audit current CORTEX codebase for non-agent/skill logic.
- Plan phased migration of legacy modules into agents/skills.
- Update registry and documentation to reflect new structure.
- Validate with organizational standards and run compliance checks.

---

### ⚡ If you say proceed, I will:
1. Generate a migration plan for CORTEX-V2 agent/skill refactoring.
2. Identify legacy modules needing conversion.
3. Draft a sample agent/skill and registry entry.
4. Outline governance and workflow integration steps.

Let me know if you want to proceed with the migration plan or need further clarification.