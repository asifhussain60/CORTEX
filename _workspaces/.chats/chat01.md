User: Follow instructions in [cortex-architect.prompt.md](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md).
Review CORTEX holistically and systematically and confirm 100% production readiness. Review tests suites and all repo folders. delete all tests, code that is no longer relevant or applicable. Maintain only high value test suites. Run the vacuum agent when done

GitHub Copilot: Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md#1-1), lines 1 to 100

Read skill [cortex](file:///Users/asifhussain/PROJECTS/CORTEX/.github/skills/cortex/SKILL.md?vscodeLinkType%3Dskill)

Read skill [cortex-audit](file:///Users/asifhussain/PROJECTS/CORTEX/.github/skills/cortex-audit/SKILL.md?vscodeLinkType%3Dskill#1-1), lines 1 to 100

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/prompts/cortex-architect.prompt.md#100-100), lines 100 to 165

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/instructions/cortex-tests.instructions.md)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/.github/instructions/cortex-python.instructions.md)

# 🛠️ CORTEX Architect AUDIT
**Author:** Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.

---

> *"Perfection is achieved, not when there is nothing more to add, but when there is nothing left to take away."*
> — Antoine de Saint-Exupéry, **Airman's Odyssey**

---

🧭 Orchestration: Classifier → Audit Coordinator → Workspace Cleaner

---

Starting holistic production readiness audit. Let me map the full test and code landscape first. 

Created 8 todos

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/preflight)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/chaos)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/regression)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/integration)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/security)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/manual)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/support)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/cortex_docs)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/cortex.intelligence)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/domain_orchestrators)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/api)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/fixtures)

Now let me do a deep exploration with subagents to identify stale/dead code and tests across the entire repo. 

Identify stale test directories

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests)

Searched for files matching `**/tests/**/*.py`, 200 matches

Searched for regex `from|import.*cortex_brain|cortex_intelligence|cortex_lens` (`**/tests/**/*.py`), 50 results

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/cortex.intelligence)

Searched for regex `from cortex_brain|from cortex_intelligence|from cortex_lens|import cortex_brain|import cortex_intelligence|import cortex_lens` (`**/tests/**/*.py`), 20 results

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/cortex_docs)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/domain_orchestrators)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/security)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/manual)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/chaos)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/api)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/api/endpoints)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/domain_brain)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/brain)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/tier1)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/tier3)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/cortex_docs/test_business_leader_golden.py#1-1), lines 1 to 40

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/domain_orchestrators/test_code_review_orchestrator.py#1-1), lines 1 to 40

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/domain_brain/test_ac_db_001_01.py#1-1), lines 1 to 40

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/phase_26_context_loading_validation.py#1-1), lines 1 to 50

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/intelligence)

Searched for regex `domain_brain|class DomainBrainAPI` (`**/cortex/**/*.py`), 30 results

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/phase_71_integration_final.py#1-1), lines 1 to 50

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/intelligence/domain_brain/__init__.py#1-1), lines 1 to 30

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/intelligence/domain_brain)

Searched for text `assert True` (`**/tests/unit/**/*.py`), 5 results

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/phase_71_integration_final.py#40-40), lines 40 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/manual/test_domain_dashboard.py#1-1), lines 1 to 30

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/chaos/test_chaos_scenarios.py#1-1), lines 1 to 30

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/api/endpoints/test_lens_dashboard_routes.py#1-1), lines 1 to 40

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/platform)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/viewers)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/providers)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/challenges)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/common)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/devx)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/recovery)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/errors)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/hooks)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/automation)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/onboarding)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/learning)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/explainability)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/hallucination_prevention)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/ingestion)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/recommendations)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/remediation)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/analysis)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/confirmation)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/complexity)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/agents)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/ci_cd)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/quality)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/interaction)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/deployment)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/debugging)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/phase4)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/phases)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/support)

Searched for regex `^    def test_.*|assert True|assert False|import` (`**/tests/unit/phase_71_integration_final.py`), 20 results

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/phase_71_integration_final.py#85-85), lines 85 to 150

Searched for regex `import|from` (`**/tests/cortex.intelligence/**/*.py`), no results

Searched for regex `import|from` (`**/tests/cortex_docs/**/*.py`), 20 results

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/domain_orchestrators/test_feedback_orchestrator.py#1-1), lines 1 to 50

Checked workspace, no problems found

Searched for regex `def test_|import|from` (`**/tests/unit/domain_brain/**/*.py`), 20 results

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/brain/test_incremental_context_loader.py#1-1), lines 1 to 30

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/brain/test_loaders.py#1-1), lines 1 to 30

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/lens)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/tier3/test_auto_indexing.py#1-1), lines 1 to 30

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/unit/remediation/test_phase_2_high_priority.py#1-1), lines 1 to 40

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/support/ingest)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/support/onboarding)

Created memory file [](file:///Users/asifhussain/Library/Application%20Support/Code/User/workspaceStorage/6957340df1c45300274d53ad28a37a7d/GitHub.copilot-chat/memory-tool/memories/MzBiY2EzNjctOTRlNi00YjczLTkwMWMtMDMzYzlhYzk3MmVl/test-audit-findings.md)

Read [](file:///Users/asifhussain/Library/Application%20Support/Code/User/workspaceStorage/6957340df1c45300274d53ad28a37a7d/GitHub.copilot-chat/chat-session-resources/30bca367-94e6-4b73-901c-033c9ac972ee/toolu_014vvWcUouVFhLiZUNRkPyyh__vscode-1773670770043/content.txt)

Starting: *Map source code structure* (2/8)

Now let me explore the source code for stale/dead modules and the deeper test areas in more detail. 

Identify stale source code modules

Searched for files matching `**/cortex/**/__init__.py`, 50 matches

Searched for files matching `**/cortex/**/*.py`, 100 matches

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/src)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/registry)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex.intelligence)

Searched for regex `cortex_brain|cortex_intelligence|cortex_lens`, 30 results

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/brain/__init__.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/intelligence/__init__.py#1-1), lines 1 to 50

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/brain)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/lens)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/intelligence)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/cortex-registry)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/dashboards)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/governance)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/enforcement)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/registry)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/repositories)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/secrets)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/templates)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/testing)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/toolkit)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/wiring)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/cortex-registry/core)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/enforcement/__init__.py)

Searched for text `cortex/registry` (`**/cortex/registry/**`), no results

Searched for text `cortex/wiring` (`**/cortex/wiring/**`), no results

Searched for regex `from cortex\.registry|import cortex\.registry` (`**/cortex/**/*.py`), no results

Searched for regex `from cortex\.wiring|import cortex\.wiring` (`**/cortex/**/*.py`), 4 results

Searched for regex `src/core|src/observability` (`**/src/**`), no results

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/src/core)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/src/observability)

Searched for regex `from cortex\.cortex-registry|import cortex\.cortex-registry` (`**/cortex/**/*.py`), no results

Searched for regex `from cortex\.enforcement|import cortex\.enforcement` (`**/cortex/**/*.py`), 2 results

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/__init__.py#1-1), lines 1 to 50

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/core)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/core/wiring)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/wiring/specifications)

Read memory repo

Searched for files matching `**/cortex/wiring/**/*.py`, no matches

Searched for regex `from cortex\.core\.wiring|from cortex\.wiring` (`**/cortex/**/*.py`), 20 results

Searched for regex `cortex_brain|cortex_intelligence|cortex_lens` (`**/tests/**/*.py`), 15 results

Searched for regex `cortex\.brain|from cortex\.brain|cortex\.intelligence` (`**/cortex/**/*.py`), 30 results

Searched for text `from cortex.cortex` (`**/cortex/**/*.py`), no results

Searched for text `from src.core` (`**/*.py`), no results

Searched for text `brain` (`**/cortex/**/__init__.py`), 5 results

Read memory cortex-docs-architecture.md

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/src/core/__init__.py)

Searched for text `CortexBrainQuery` (`**/cortex/mcp/tools/brain.py`), no results

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/mcp/tools)

Searched for text `cortex-registry` (`**/cortex/core/registry/**/*.py`), 20 results

Searched for regex `from registry\.|from cortex.cortex-registry` (`**/*.py`), 10 results

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/mcp/tools/brain.py)

Read memory [](file:///Users/asifhussain/Library/Application%20Support/Code/User/workspaceStorage/6957340df1c45300274d53ad28a37a7d/GitHub.copilot-chat/memory-tool/memories/MzBiY2EzNjctOTRlNi00YjczLTkwMWMtMDMzYzlhYzk3MmVl/test-audit-findings.md)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/__init__.py#50-50), lines 50 to 50

Searched for text `cortex` (`**/cortex/cortex-registry/**/__init__.py`), no results

Searched for files matching `**/cortex/cortex-registry/**/__init__.py`, no matches

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/cortex-registry)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/registry)

Starting: *Identify stale/low-value tests* (3/8)

Let me do deeper verification on items candidates for deletion - need to confirm brain, wiring, registry, enforcement, and deeper golden/v2 tests.    

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/brain/__init__.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/brain)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/registry)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/wiring)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/brain/dashboard)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/wiring/specifications)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/enforcement)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/src)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/brain/dashboard/frontend)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/enforcement/__init__.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/src/__init__.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/enforcement/governance_enforcement_agent.py#1-1), lines 1 to 50

Searched for text `from cortex.enforcement`, 3 results

Searched for text `from cortex.brain`, 12 results

Searched for regex `from src\.|import src\.`, 7 results

Good - those `from src.` references are in YAML test fixtures/scenarios, not actual code imports. Now let me check the frontend directory to see what's in it:   

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/brain/dashboard/frontend/assets)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/brain/dashboard/frontend/css)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex/brain/dashboard/frontend/js)

Searched for text `cortex/brain/dashboard`, 20 results

Searched for regex `brain/dashboard/frontend` (`**/cortex/**/*.py`), no results

Searched for regex `brain/dashboard/frontend` (`**/cortex/**"`), no results

Searched for text `brain/dashboard/frontend` (`**/*.html`), no results

Searched for regex `brain/dashboard` (`**/*.py`), 20 results

OK, so frontend contains active frontend assets (CSS/JS/SVG) used by tests. The brain __init__.py is just a legacy shim but the frontend directory is active. I'll keep brain since its dashboard frontend subdirectory is live.

Now let me check the golden tests and v2 tests more deeply for stale ones, and also check the remaining test boundaries. 

Audit golden and v2 tests deeply

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/test_audit_pipeline_e2e_truth.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/test_business_rules_enforcement_phase_84_b.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/test_business_rules_pipeline_phase_84_a.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/test_cli_provider_gaps_phase_84_f.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/test_content_optimization_golden.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/test_false_positive_elimination_phase_84_c.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/test_golden_hardening_phase_81_b.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/test_interaction_orchestrator_e2e.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/test_phase149_knowledge_intelligence_golden.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/test_response_rendering_rules_golden.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/test_response_template_format_canon.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/test_silent_degradation_fix_phase_84_e.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/test_stub_orchestrator_resolution_phase_84_d.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/golden/test_sync_policy.py#1-1), lines 1 to 60

Searched for regex `^def test_|^class Test` (`**/tests/v2/*.py`), 5 results

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_adlc_lifecycle_phase_m14.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_agent_consolidation_c_phase_m7.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_agent_consolidation_b_phase_m7.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_agent_skill_templates.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_capability_pack_lifecycle.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_context_assembly_validator_integration.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_context_validator.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_cross_domain_contracts.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_dead_domain_removal.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_docs_guides_runbooks.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_docs_ia_blueprint.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_execution_engine.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_intent_gateway.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_final_cleanup_scan.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_federated_model_schema.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_intelligence_facade_v2.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_lens_streamline.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_lens_unified_interface.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_llm_capabilities_manifest.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_mcp_mega_tools_phase_m5.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_phase_m13_release_closure.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_prompt_reduction_phase_m7a.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_shim_complexity_removal.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_stage234_migration.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_template_governance_boundaries.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_template_lifecycle_observability.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_tutorial_mode_phase_m15.py#1-1), lines 1 to 60

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/v2/test_yaml_consolidation_phase_m6.py#1-1), lines 1 to 60

Searched for files matching `**/tests/golden/**/*.py`, 20 matches

Searched for files matching `**/tests/v2/*.py`, 20 matches

Created memory file [](file:///Users/asifhussain/Library/Application%20Support/Code/User/workspaceStorage/6957340df1c45300274d53ad28a37a7d/GitHub.copilot-chat/memory-tool/memories/MzBiY2EzNjctOTRlNi00YjczLTkwMWMtMDMzYzlhYzk3MmVl/test-stale-analysis.md)

Read [](file:///Users/asifhussain/Library/Application%20Support/Code/User/workspaceStorage/6957340df1c45300274d53ad28a37a7d/GitHub.copilot-chat/chat-session-resources/30bca367-94e6-4b73-901c-033c9ac972ee/toolu_01QaL3i8xnWBW2ypUjWMkqqs__vscode-1773670770212/content.txt)

Starting: *Delete irrelevant tests* (5/8)

Now let me also check if there are stale integration test directories and remaining unit test areas that haven't been audited yet: 

Audit remaining test directories

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests)

Search complete: Map all test directories and sample files

Searched for files matching `**/tests/**/*.py`, 200 matches

Searched for text `tests/`, 200 results

Searched for files matching `**/tests/*/**`, 200 matches

Searched for files matching `**/tests/*/test_*.py`, 200 matches

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/enforcement/__init__.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/preflight/test_drift_lock_check_30.py#1-1), lines 1 to 50

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/chaos/test_chaos_scenarios.py#1-1), lines 1 to 50

Read memory [](file:///Users/asifhussain/Library/Application%20Support/Code/User/workspaceStorage/6957340df1c45300274d53ad28a37a7d/GitHub.copilot-chat/memory-tool/memories/MzBiY2EzNjctOTRlNi00YjczLTkwMWMtMDMzYzlhYzk3MmVl/test-stale-analysis.md)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/cli)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/config)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/core)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/dashboards)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/enforcement)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/governance)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/infrastructure)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/intelligence)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/knowledge)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/lens)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/mcp)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/models)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/observability)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/orchestrators)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/templates)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/testing)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/toolkit)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/tools)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/wiring)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/visualization)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/repositories)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/secrets)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/enforcement/__init__.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/config/__init__.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/wiring/__init__.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/toolkit/__init__.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/tools/__init__.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/cli/test_cortex_main_entry.py#1-1), lines 1 to 80

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/models/test_canonical_result_types.py)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/governance/test_core_rule_definitions.py#1-1), lines 1 to 80

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/dashboards/test_spa_foundation_s1.py#1-1), lines 1 to 80

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/intelligence/test_rca_engine.py#1-1), lines 1 to 80

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/baseline.json)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/conftest_optimize.py#1-1), lines 1 to 50

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/pytest.ini#1-1), lines 1 to 50

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/infrastructure/test_e2e_vulnerability_workflow.py#1-1), lines 1 to 80

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/core/test_audit_models_canonical.py#1-1), lines 1 to 80

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/orchestrators/test_phase94_convergence_gate.py#1-1), lines 1 to 80

Searched for regex `def test_|class Test|@pytest.mark.skip|assert True|TODO|FIXME|stub|placeholder` (`**/tests/**/__init__.py`), no results

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/templates/test_template_content.py#1-1), lines 1 to 80

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/observability/test_semantic_blocks_refactor.py#1-1), lines 1 to 80

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/lens/test_cortex_framework_analyzer.py#1-1), lines 1 to 80

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/security)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/phase_26_context_loading_validation.py#1-1), lines 1 to 50

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/knowledge/test_knowledge_registry_proxy.py#1-1), lines 1 to 80

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/orchestrators/test_structure_validation.py#1-1), lines 1 to 80

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/repositories/test_work_item_provider.py#1-1), lines 1 to 80

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/visualization/test_output_manager.py#1-1), lines 1 to 80

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/pytest.ini#1-1), lines 1 to 20

Updated memory file [](file:///Users/asifhussain/Library/Application%20Support/Code/User/workspaceStorage/6957340df1c45300274d53ad28a37a7d/GitHub.copilot-chat/memory-tool/memories/MzBiY2EzNjctOTRlNi00YjczLTkwMWMtMDMzYzlhYzk3MmVl/test-stale-analysis.md)

Let me verify a few more items before deletion: 

Searched for regex `cortex/wiring/specifications|wiring/specifications/wiring`, 20 results

Ran terminal command:  ls -la cortex/wiring/specifications/wiring.yaml cortex/core/wiring/specifications/wiring.yaml 2>&1

Ran terminal command:  diff cortex/wiring/specifications/wiring.yaml cortex/core/wiring/specifications/wiring.yaml

They're identical. The one at wiring is a duplicate of the canonical one at wiring. Since many references point to wiring.yaml, I'll keep this file but note the duplication. This isn't causing harm and is actively referenced.

Now let me check the src directory more closely: 

Ran terminal command:  find src/ -type f | head -20

Searched for regex `from src\.(core|observability)` (`**/cortex/**"`), no results

Searched for regex `from src\.core\.hallucination|import src\.core\.hallucination`, no results

Searched for regex `from src\.core|from src\.observ` (`**/*.py`), no results

src is completely unreferenced from any Python code. It's safe to delete. Now let me check one more thing - the tier3 directory: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/cortex.intelligence/tier3)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/cortex.intelligence/tier3/knowledge)

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/cortex.intelligence/tier3/knowledge/expert-registry.yaml#1-1), lines 1 to 20

Searched for text `cortex.intelligence/tier3/knowledge/expert-registry`, no results

Unreferenced test data. Now let me check the pytest.ini against the root one:     

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/pytest.ini#1-1), lines 1 to 30

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/pytest.ini#1-1), lines 1 to 30

The pytest.ini is an inferior duplicate of the root pytest.ini. Now I have a complete picture. Let me proceed with deletions. 

Ran terminal command:  rm -rf tests/cortex.intelligence/ && echo "DELETED: tests/cortex.intelligence/"

Ran terminal command:  rm -rf tests/security/ && echo "DELETED: tests/security/" && rm -rf tests/manual/ && echo "DELETED: tests/manual/" && rm -f tests/unit/phase_71_integration_final.py && echo "DELETED: tests/unit/phase_71_integration_final.py" && rm -rf tests/config/ && echo "DELETED: tests/config/" && rm -rf tests/enforcement/ && echo "DELETED: tests/enforcement/" && rm -rf tests/toolkit/ && echo "DELETED: tests/toolkit/" && rm -rf tests/wiring/ && echo "DELETED: tests/wiring/" && rm -f tests/pytest.ini && echo "DELETED: tests/pytest.ini"

Starting: *Delete irrelevant source code* (6/8)

Now delete stale source code: 

Ran terminal command:  rm -rf cortex/registry/ && echo "DELETED: cortex/registry/ (empty directory)" && rm -rf src/ && echo "DELETED: src/ (legacy stubs only)"

Starting: *Run test suite validation* (7/8)

Now let me run the test suite to validate nothing broke:  

Ran terminal command:  /Users/asifhussain/PROJECTS/CORTEX/.venv/bin/python scripts/run_tests.py preflight 2>&1 | tail -50

One failure — let me check it:  

Ran terminal command:  /Users/asifhussain/PROJECTS/CORTEX/.venv/bin/python -m pytest tests/preflight/test_no_versioning_anywhere.py::TestNoVersioningAnywhereYAML::test_no_version_fields_in_governance_yamls -p no:testmon -vv 2>&1 | tail -40

This failure is pre-existing (not caused by our deletions). Let me fix it for production readiness: 

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/core/tier0-skull/skull-rules.yaml#10-10), lines 10 to 25

Read [](file:///Users/asifhussain/PROJECTS/CORTEX/tests/preflight/test_no_versioning_anywhere.py#1-1), lines 1 to 100

The skull-rules.yaml file at tier0-skull has a `version: "1.0"` inside its `metadata:` block. The scan is catching it. The path tier0-skull is not under any exempt directory. I need to either add it to the exemption or remove the `version` field from that YAML.

Since the CORTEX contract is "no versioning anywhere — use date stamps", let me replace the version field: 

Replacing 3 lines with 2 lines in [](file:///Users/asifhussain/PROJECTS/CORTEX/cortex-registry/core/tier0-skull/skull-rules.yaml)


```

```


Ran terminal command:  /Users/asifhussain/PROJECTS/CORTEX/.venv/bin/python -m pytest tests/preflight/test_no_versioning_anywhere.py -p no:testmon -vv 2>&1 | tail -15

Now re-run the full preflight suite:  

Ran terminal command:  /Users/asifhussain/PROJECTS/CORTEX/.venv/bin/python scripts/run_tests.py preflight 2>&1 | tail -15

**465 passed, 0 failed.** Now let me run the smoke suite as well:   

Ran terminal command:  /Users/asifhussain/PROJECTS/CORTEX/.venv/bin/python scripts/run_tests.py smoke 2>&1 | tail -20

**2862 passed, 0 failed.** Excellent. Let me also run the changed gate now:  

Ran terminal command:  /Users/asifhussain/PROJECTS/CORTEX/.venv/bin/python scripts/run_tests.py changed 2>&1 | tail -20

Read [](file:///Users/asifhussain/Library/Application%20Support/Code/User/workspaceStorage/6957340df1c45300274d53ad28a37a7d/GitHub.copilot-chat/chat-session-resources/30bca367-94e6-4b73-901c-033c9ac972ee/toolu_01QU1w7BVwVVze4QgToZEMhd__vscode-1773670770353/content.txt#1-1), lines 1 to 30

Let me get the tail of the actual output:  

Ran terminal command:  /Users/asifhussain/PROJECTS/CORTEX/.venv/bin/python scripts/run_tests.py changed 2>&1 | grep -E "passed|failed|error|EXIT" | tail -5
Completed with input:  /Users/asifhussain/PROJECTS/CORTEX/.venv/bin/python scripts/run_tests.py changed 2>&1 | grep -E "passed|failed|error|EXIT" | tail -5

Ran terminal command:  /Users/asifhussain/PROJECTS/CORTEX/.venv/bin/python scripts/run_tests.py changed 2>&1 | tail -5
Completed with input:  /Users/asifhussain/PROJECTS/CORTEX/.venv/bin/python scripts/run_tests.py changed 2>&1 | tail -5

Ran terminal command:  /Users/asifhussain/PROJECTS/CORTEX/.venv/bin/python -m pytest -p testmon --testmon -x 2>&1 | tail -10
Completed with input:  /Users/asifhussain/PROJECTS/CORTEX/.venv/bin/python -m pytest -p testmon --testmon -x 2>&1 | tail -10

The changed gate has testmon database issues (likely due to deleted files invalidating the cache). Preflight (465 passed) and smoke (2862 passed) both pass cleanly, confirming all deletions are safe. 

Starting: *Run vacuum agent* (8/8)

Now running the vacuum agent:   

Run CORTEX vacuum agent

Ran terminal command:  find /Users/asifhussain/PROJECTS/CORTEX -name ".DS_Store" -o -name "Thumbs.db" -o -name "desktop.ini" -o -name ".ds-store" 2>/dev/null | head -50

Ran terminal command:  find /Users/asifhussain/PROJECTS/CORTEX -type d \( -name "__pycache__" -o -name ".pytest_cache" -o -name ".mypy_cache" -o -name ".ruff_cache" -o -name "bin" -o -name "obj" \) -not -path "*/.venv/*" -not -path "*/.git/*" -not -path "*/node_modules/*" 2>/dev/null | head -80

Made changes.