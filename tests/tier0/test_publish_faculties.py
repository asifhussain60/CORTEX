#!/usr/bin/env python3
"""
SKULL-007: CORTEX Faculty Integrity Test

Ensures published CORTEX package contains ALL essential components for full operation.
This test verifies that no critical faculties are lost during publish process.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path


class TestCORTEXFaculties:
    """Test that all CORTEX essential faculties exist in publish package."""
    
    @pytest.fixture
    def publish_cortex(self):
        """Path to published CORTEX package."""
        return Path(__file__).parent.parent.parent / 'publish' / 'CORTEX'
    
    def test_publish_folder_exists(self, publish_cortex):
        """Verify publish/CORTEX folder exists."""
        assert publish_cortex.exists(), "publish/CORTEX folder not found - run publish script first"
    
    # ============================================================
    # TIER 0: BRAIN PROTECTION (SKULL Layer)
    # ============================================================
    
    def test_tier0_brain_protection_exists(self, publish_cortex):
        """Tier 0: Brain protection rules and protector."""
        tier0_files = [
            'cortex-brain/protection/brain-protection-rules.yaml',  # SKULL rules
            'src/tier0/__init__.py',
            'src/tier0/brain_protector.py',
        ]
        
        for file_path in tier0_files:
            full_path = publish_cortex / file_path
            assert full_path.exists(), f"Tier 0 MISSING: {file_path} - CORTEX cannot enforce quality without SKULL!"
    
    # ============================================================
    # TIER 1: WORKING MEMORY (Conversation Tracking)
    # ============================================================
    
    def test_tier1_conversation_memory_exists(self, publish_cortex):
        """Tier 1: Conversation memory system."""
        tier1_files = [
            'src/tier1/__init__.py',
            'src/tier1/conversation_manager.py',  # Main conversation API
            'src/tier1/working_memory.py',
        ]
        
        for file_path in tier1_files:
            full_path = publish_cortex / file_path
            assert full_path.exists(), f"Tier 1 MISSING: {file_path} - CORTEX cannot remember conversations!"
    
    # ============================================================
    # TIER 2: KNOWLEDGE GRAPH (Pattern Learning)
    # ============================================================
    
    def test_tier2_knowledge_graph_exists(self, publish_cortex):
        """Tier 2: Knowledge graph and pattern storage."""
        tier2_files = [
            'src/tier2/__init__.py',
            'src/tier2/knowledge_graph/__init__.py',
            'src/tier2/knowledge_graph/database/schema.py',
            'cortex-brain/learning/knowledge-graph.yaml',
        ]
        
        for file_path in tier2_files:
            full_path = publish_cortex / file_path
            assert full_path.exists(), f"Tier 2 MISSING: {file_path} - CORTEX cannot learn patterns!"
    
    # ============================================================
    # TIER 3: DEVELOPMENT CONTEXT (Project Intelligence)
    # ============================================================
    
    def test_tier3_development_context_exists(self, publish_cortex):
        """Tier 3: Development context and project intelligence."""
        tier3_files = [
            'src/tier3/__init__.py',
            'src/tier3/context_intelligence.py',  # Updated from context_manager.py
        ]
        
        for file_path in tier3_files:
            full_path = publish_cortex / file_path
            assert full_path.exists(), f"Tier 3 MISSING: {file_path} - CORTEX cannot understand project context!"
    
    # ============================================================
    # 10 SPECIALIST AGENTS (Left + Right Brain)
    # ============================================================
    
    def test_specialist_agents_exist(self, publish_cortex):
        """Specialist agents: modular architecture with strategic/tactical split."""
        # Core agent files (base classes and utilities)
        agent_files = [
            'src/cortex_agents/__init__.py',
            'src/cortex_agents/base_agent.py',
            'src/cortex_agents/intent_router.py',  # Intent detection
            'src/cortex_agents/error_corrector.py',  # Error correction
            'src/cortex_agents/commit_handler.py',  # Git commits
        ]
        
        # Check for modular agent directories (actual implementation structure)
        agent_dirs = [
            'src/cortex_agents/strategic',  # Strategic agents
            'src/cortex_agents/tactical',   # Tactical agents
            'src/cortex_agents/code_executor',  # Code execution module
            'src/cortex_agents/test_generator',  # Test generation module
            'src/cortex_agents/health_validator',  # Health validation module
            'src/cortex_agents/work_planner',  # Work planning module
        ]
        
        missing_agents = []
        for file_path in agent_files:
            full_path = publish_cortex / file_path
            if not full_path.exists():
                missing_agents.append(file_path)
        
        missing_dirs = []
        for dir_path in agent_dirs:
            full_path = publish_cortex / dir_path
            if not full_path.exists():
                missing_dirs.append(dir_path)
        
        all_missing = missing_agents + missing_dirs
        assert len(all_missing) == 0, f"AGENTS MISSING ({len(all_missing)}): {all_missing} - CORTEX cannot coordinate work!"
    
    # ============================================================
    # OPERATIONS (User-Facing Workflows)
    # ============================================================
    
    def test_operations_framework_exists(self, publish_cortex):
        """Operations framework and orchestrator."""
        ops_files = [
            'src/operations/__init__.py',
            'src/operations/operations_orchestrator.py',
            'cortex-operations.yaml',
        ]
        
        for file_path in ops_files:
            full_path = publish_cortex / file_path
            assert full_path.exists(), f"Operations MISSING: {file_path} - CORTEX cannot execute workflows!"
    
    def test_user_operations_exist(self, publish_cortex):
        """User-facing operations (setup, cleanup, onboarding, etc.)."""
        # Updated to match current operations structure
        user_ops = [
            'src/operations/modules/__init__.py',  # Operations modules init
            'src/operations/modules/cleanup',  # Cleanup directory
            'src/operations/modules/brain_initialization_module.py',  # Brain setup
        ]
        
        # Check for operations directory exists
        ops_modules = publish_cortex / 'src/operations/modules'
        assert ops_modules.exists(), "Operations modules directory MISSING!"
        
        for file_path in user_ops:
            full_path = publish_cortex / file_path
            assert full_path.exists(), f"User operation MISSING: {file_path}"
    
    def test_admin_operations_excluded(self, publish_cortex):
        """Admin operations should NOT exist in user package."""
        # These should NOT exist - admin only
        admin_ops = [
            'src/operations/modules/design_sync',  # Admin development tool
        ]
        
        for file_path in admin_ops:
            full_path = publish_cortex / file_path
            assert not full_path.exists(), f"Admin operation should be EXCLUDED: {file_path}"
    
    # ============================================================
    # PLUGINS (Extensibility)
    # ============================================================
    
    def test_plugin_system_exists(self, publish_cortex):
        """Plugin system for extensibility."""
        # Check for plugin directory and core files
        plugin_dir = publish_cortex / 'src/plugins'
        assert plugin_dir.exists(), "Plugin directory MISSING - CORTEX cannot extend functionality!"
        
        # Core plugin files (command_registry.py is the plugin registry)
        plugin_files = [
            'src/plugins/base_plugin.py',
            'src/plugins/command_registry.py',  # Plugin/command registry
        ]
        
        for file_path in plugin_files:
            full_path = publish_cortex / file_path
            assert full_path.exists(), f"Plugin system MISSING: {file_path} - CORTEX cannot extend functionality!"
    
    # ============================================================
    # ENTRY POINTS (GitHub Copilot Integration)
    # ============================================================
    
    def test_entry_points_exist(self, publish_cortex):
        """CORTEX entry points for GitHub Copilot."""
        entry_files = [
            '.github/prompts/CORTEX.prompt.md',
            '.github/copilot-instructions.md',
        ]
        
        for file_path in entry_files:
            full_path = publish_cortex / file_path
            assert full_path.exists(), f"Entry point MISSING: {file_path} - Copilot cannot find CORTEX!"
    
    # ============================================================
    # DOCUMENTATION (User Guides)
    # ============================================================
    
    def test_documentation_exists(self, publish_cortex):
        """User documentation files for learning CORTEX."""
        # Documentation is now in .github/prompts/modules/
        doc_files = [
            '.github/prompts/CORTEX.prompt.md',  # Main entry point
            '.github/prompts/modules/response-format.md',
            '.github/prompts/modules/document-organization.md',
            '.github/prompts/modules/planning-system.md',
            '.github/prompts/modules/template-system.md',
        ]
        
        for file_path in doc_files:
            full_path = publish_cortex / file_path
            assert full_path.exists(), f"Documentation MISSING: {file_path} - Users cannot learn CORTEX!"
    
    # ============================================================
    # CONFIGURATION & TEMPLATES
    # ============================================================
    
    def test_configuration_exists(self, publish_cortex):
        """Configuration files and templates."""
        config_files = [
            'cortex.config.template.json',  # Template only (no machine paths)
            'cortex-brain/templates/response-templates.yaml',
            'requirements.txt',
        ]
        
        for file_path in config_files:
            full_path = publish_cortex / file_path
            assert full_path.exists(), f"Configuration MISSING: {file_path}"
    
    def test_setup_guide_exists(self, publish_cortex):
        """SETUP-FOR-COPILOT.md inside CORTEX folder."""
        setup_file = publish_cortex / 'SETUP-FOR-COPILOT.md'
        assert setup_file.exists(), "SETUP-FOR-COPILOT.md MISSING - Users don't know how to install!"
    
    # ============================================================
    # LEGAL & README
    # ============================================================
    
    def test_legal_files_exist(self, publish_cortex):
        """Legal and README files."""
        legal_files = [
            'LICENSE',
            'README.md',
        ]
        
        for file_path in legal_files:
            full_path = publish_cortex / file_path
            assert full_path.exists(), f"Legal file MISSING: {file_path}"
    
    # ============================================================
    # PRIVACY: NO LEAKS ALLOWED
    # ============================================================
    
    def test_no_machine_specific_config(self, publish_cortex):
        """Ensure cortex.config.json (with machine paths) is NOT published."""
        banned_files = [
            'cortex.config.json',  # Contains AHHOME and absolute paths
            'cortex.config.example.json',  # Same issue
            '.platform_state.json',  # Machine state
        ]
        
        for file_path in banned_files:
            full_path = publish_cortex / file_path
            assert not full_path.exists(), f"PRIVACY LEAK: {file_path} contains machine-specific paths!"
    
    def test_no_dev_artifacts(self, publish_cortex):
        """Ensure development artifacts are excluded."""
        banned_artifacts = [
            'tests',  # Test suite (dev only)
            '__pycache__',
            '.pytest_cache',
            'logs',
        ]
        
        for artifact in banned_artifacts:
            full_path = publish_cortex / artifact
            assert not full_path.exists(), f"Development artifact should be excluded: {artifact}"
    
    # ============================================================
    # COMPREHENSIVE FACULTY CHECK
    # ============================================================
    
    def test_cortex_fully_operational(self, publish_cortex):
        """Comprehensive check: all faculties present."""
        faculties = {
            'Tier 0 (SKULL)': publish_cortex / 'src/tier0/brain_protector.py',
            'Tier 1 (Memory)': publish_cortex / 'src/tier1/conversation_manager.py',
            'Tier 2 (Knowledge)': publish_cortex / 'src/tier2/knowledge_graph',
            'Tier 3 (Context)': publish_cortex / 'src/tier3',
            'Agents': publish_cortex / 'src/cortex_agents',
            'Operations': publish_cortex / 'src/operations/operations_orchestrator.py',
            'Plugins': publish_cortex / 'src/plugins/base_plugin.py',
            'Entry Point': publish_cortex / '.github/prompts/CORTEX.prompt.md',
            'Documentation': publish_cortex / '.github/prompts/modules',
            'Setup Guide': publish_cortex / 'SETUP-FOR-COPILOT.md',
        }
        
        missing = []
        for faculty_name, faculty_path in faculties.items():
            if not faculty_path.exists():
                missing.append(faculty_name)
        
        assert len(missing) == 0, f"CORTEX INCOMPLETE! Missing faculties: {missing}"
        
        # If we get here, CORTEX is fully operational! ✅
        print("\n✅ CORTEX FULLY OPERATIONAL - All faculties present!")
        print("   - Tier 0 (SKULL): Quality protection")
        print("   - Tier 1 (Memory): Conversation tracking")
        print("   - Tier 2 (Knowledge): Pattern learning")
        print("   - Tier 3 (Context): Project intelligence")
        print("   - 10 Specialist Agents: Coordinated work")
        print("   - Operations: User workflows")
        print("   - Plugins: Extensibility")
        print("   - Entry Points: Copilot integration")
        print("   - Documentation: User guides")
        print("   - Setup: Installation instructions")
