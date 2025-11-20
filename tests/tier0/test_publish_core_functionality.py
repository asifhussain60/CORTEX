#!/usr/bin/env python3
"""
CORTEX Core Functionality Publish Tests

Ensures published package contains ALL core functionality:
- Crawlers (SQL, Oracle, API, etc.)
- Planning System (Feature Planning, ADO Planning)
- TDD Workflow Components
- Response Templates
- Setup Operations
- Development Operations

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary

SKULL Protection:
- SKULL-006: No development artifacts published
- SKULL-007: All user-facing functionality included
"""

import pytest
from pathlib import Path


class TestPublishCoreFunctionality:
    """Verify all core CORTEX functionality is included in publish package."""
    
    @pytest.fixture
    def publish_cortex_path(self) -> Path:
        """Get path to publish/CORTEX folder."""
        repo_root = Path(__file__).parent.parent.parent
        return repo_root / 'publish' / 'CORTEX'
    
    @pytest.fixture
    def source_root(self) -> Path:
        """Get path to CORTEX source root."""
        return Path(__file__).parent.parent.parent
    
    # ============================================================================
    # Crawlers
    # ============================================================================
    
    def test_sql_crawler_included(self, publish_cortex_path: Path):
        """
        SKULL-007: Verify SQL crawler is published.
        
        Required for database discovery and schema analysis.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        sql_crawler = publish_cortex_path / 'src' / 'crawlers' / 'sql_crawler.py'
        
        assert sql_crawler.exists(), (
            f"SKULL-007 VIOLATION: SQL crawler missing from publish!\n"
            f"Expected: {sql_crawler}\n"
            f"Impact: Users cannot analyze database schemas"
        )
    
    def test_oracle_crawler_included(self, publish_cortex_path: Path):
        """
        SKULL-007: Verify Oracle crawler is published.
        
        Required for Oracle database integration (enterprise feature).
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        oracle_crawler = publish_cortex_path / 'src' / 'crawlers' / 'oracle_crawler.py'
        
        assert oracle_crawler.exists(), (
            f"SKULL-007 VIOLATION: Oracle crawler missing from publish!\n"
            f"Expected: {oracle_crawler}\n"
            f"Impact: Enterprise users cannot analyze Oracle databases"
        )
    
    def test_api_crawler_included(self, publish_cortex_path: Path):
        """
        SKULL-007: Verify API crawler is published.
        
        Required for REST API discovery and documentation.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        api_crawler = publish_cortex_path / 'src' / 'crawlers' / 'api_crawler.py'
        
        assert api_crawler.exists(), (
            f"SKULL-007 VIOLATION: API crawler missing from publish!\n"
            f"Expected: {api_crawler}\n"
            f"Impact: Users cannot discover REST APIs"
        )
    
    def test_codebase_crawler_included(self, publish_cortex_path: Path):
        """
        SKULL-007: Verify codebase crawler is published.
        
        Required for application onboarding and code analysis.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        codebase_crawler = publish_cortex_path / 'src' / 'crawlers' / 'codebase_crawler.py'
        
        assert codebase_crawler.exists(), (
            f"SKULL-007 VIOLATION: Codebase crawler missing from publish!\n"
            f"Expected: {codebase_crawler}\n"
            f"Impact: Application onboarding will fail"
        )
    
    # ============================================================================
    # Planning System
    # ============================================================================
    
    def test_feature_planning_operation_included(self, publish_cortex_path: Path):
        """
        SKULL-007: Verify feature planning operation is published.
        
        Required for interactive feature planning workflow.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        # Check operation file exists
        planning_op = publish_cortex_path / 'src' / 'operations' / 'feature_planning.py'
        
        assert planning_op.exists(), (
            f"SKULL-007 VIOLATION: Feature planning operation missing from publish!\n"
            f"Expected: {planning_op}\n"
            f"Impact: Users cannot use 'plan a feature' command"
        )
    
    def test_ado_planning_operation_included(self, publish_cortex_path: Path):
        """
        SKULL-007: Verify ADO planning operation is published.
        
        Required for Azure DevOps work item planning.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        # Check operation file exists
        ado_op = publish_cortex_path / 'src' / 'operations' / 'ado_planning.py'
        
        assert ado_op.exists(), (
            f"SKULL-007 VIOLATION: ADO planning operation missing from publish!\n"
            f"Expected: {ado_op}\n"
            f"Impact: Users cannot use 'plan ado feature' command"
        )
    
    def test_work_planner_module_included(self, publish_cortex_path: Path):
        """
        SKULL-007: Verify Work Planner module is published.
        
        Required for DoR/DoD/AC generation and planning workflows.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        # Check Work Planner module
        work_planner = publish_cortex_path / 'src' / 'cortex_agents' / 'work_planner.py'
        
        assert work_planner.exists(), (
            f"SKULL-007 VIOLATION: Work Planner module missing from publish!\n"
            f"Expected: {work_planner}\n"
            f"Impact: Planning workflows will fail"
        )
    
    def test_planning_templates_included(self, publish_cortex_path: Path):
        """
        SKULL-007: Verify planning templates are published.
        
        Required for ADO forms and feature planning documents.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        # Check response templates (includes planning templates)
        templates = publish_cortex_path / 'cortex-brain' / 'response-templates.yaml'
        
        assert templates.exists(), (
            f"SKULL-007 VIOLATION: Response templates missing from publish!\n"
            f"Expected: {templates}\n"
            f"Impact: Planning responses will fail"
        )
        
        # Verify planning-specific templates exist in file
        import yaml
        with open(templates, 'r', encoding='utf-8') as f:
            templates_data = yaml.safe_load(f)
        
        planning_templates = [
            'work_planner_success',
            'planning_dor_incomplete',
            'planning_dor_complete',
            'planning_security_review',
            'ado_created',
            'ado_resumed',
            'ado_search_results'
        ]
        
        templates_dict = templates_data.get('templates', {})
        missing = [t for t in planning_templates if t not in templates_dict]
        
        assert not missing, (
            f"SKULL-007 VIOLATION: Planning templates missing from response-templates.yaml!\n"
            f"Missing: {missing}\n"
            f"Impact: Planning commands will return generic responses"
        )
    
    # ============================================================================
    # TDD Workflow
    # ============================================================================
    
    def test_tester_agent_included(self, publish_cortex_path: Path):
        """
        SKULL-007: Verify Tester agent is published.
        
        Required for TDD workflow and test generation.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        tester = publish_cortex_path / 'src' / 'cortex_agents' / 'tester.py'
        
        assert tester.exists(), (
            f"SKULL-007 VIOLATION: Tester agent missing from publish!\n"
            f"Expected: {tester}\n"
            f"Impact: TDD workflow will fail"
        )
    
    def test_validator_agent_included(self, publish_cortex_path: Path):
        """
        SKULL-007: Verify Validator agent is published.
        
        Required for code quality validation and DoD enforcement.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        validator = publish_cortex_path / 'src' / 'cortex_agents' / 'validator.py'
        
        assert validator.exists(), (
            f"SKULL-007 VIOLATION: Validator agent missing from publish!\n"
            f"Expected: {validator}\n"
            f"Impact: Quality validation will fail"
        )
    
    def test_executor_agent_included(self, publish_cortex_path: Path):
        """
        SKULL-007: Verify Executor agent is published.
        
        Required for code implementation in TDD workflow.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        executor = publish_cortex_path / 'src' / 'cortex_agents' / 'executor.py'
        
        assert executor.exists(), (
            f"SKULL-007 VIOLATION: Executor agent missing from publish!\n"
            f"Expected: {executor}\n"
            f"Impact: Code implementation will fail"
        )
    
    # ============================================================================
    # Response Templates
    # ============================================================================
    
    def test_response_templates_comprehensive(self, publish_cortex_path: Path):
        """
        SKULL-007: Verify all critical response templates are published.
        
        Required for intelligent question routing and contextual responses.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        templates_file = publish_cortex_path / 'cortex-brain' / 'response-templates.yaml'
        
        assert templates_file.exists(), (
            f"SKULL-007 VIOLATION: response-templates.yaml missing!\n"
            f"Expected: {templates_file}"
        )
        
        import yaml
        with open(templates_file, 'r', encoding='utf-8') as f:
            templates_data = yaml.safe_load(f)
        
        # Critical templates that MUST exist
        critical_templates = [
            'help_table',
            'help_detailed',
            'quick_start',
            'status_check',
            'success_general',
            'error_general',
            'work_planner_success',
            'planning_dor_incomplete',
            'planning_dor_complete',
            'executor_success',
            'tester_success',
            'fallback'
        ]
        
        templates_dict = templates_data.get('templates', {})
        missing = [t for t in critical_templates if t not in templates_dict]
        
        assert not missing, (
            f"SKULL-007 VIOLATION: Critical response templates missing!\n"
            f"Missing: {missing}\n"
            f"Impact: Core CORTEX responses will fail"
        )
    
    # ============================================================================
    # Setup Operations
    # ============================================================================
    
    def test_environment_setup_operation_included(self, publish_cortex_path: Path):
        """
        SKULL-007: Verify environment_setup operation is published.
        
        Required for initial CORTEX setup in user applications.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        setup_op = publish_cortex_path / 'src' / 'operations' / 'environment_setup.py'
        
        assert setup_op.exists(), (
            f"SKULL-007 VIOLATION: environment_setup operation missing from publish!\n"
            f"Expected: {setup_op}\n"
            f"Impact: Users cannot run 'setup environment' command"
        )
    
    def test_application_onboarding_operation_included(self, publish_cortex_path: Path):
        """
        SKULL-007: Verify application_onboarding operation is published.
        
        Required for intelligent application onboarding workflow.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        onboarding_op = publish_cortex_path / 'src' / 'operations' / 'application_onboarding.py'
        
        assert onboarding_op.exists(), (
            f"SKULL-007 VIOLATION: application_onboarding operation missing from publish!\n"
            f"Expected: {onboarding_op}\n"
            f"Impact: 'onboard this application' command will fail"
        )
    
    def test_migration_scripts_included(self, publish_cortex_path: Path):
        """
        SKULL-007: Verify database migration scripts are published.
        
        Required for initializing CORTEX brain databases.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        migration_scripts = [
            'scripts/cortex/migrate-all-tiers.py',
            'cortex-brain/migrate_brain_db.py'
        ]
        
        missing = []
        for script in migration_scripts:
            script_path = publish_cortex_path / script
            if not script_path.exists():
                missing.append(script)
        
        assert not missing, (
            f"SKULL-007 VIOLATION: Migration scripts missing from publish!\n"
            f"Missing: {missing}\n"
            f"Impact: Brain initialization will fail"
        )
    
    # ============================================================================
    # Development Operations
    # ============================================================================
    
    def test_cleanup_operation_included(self, publish_cortex_path: Path):
        """
        SKULL-007: Verify workspace_cleanup operation is published.
        
        Required for cleaning up old files and maintaining workspace health.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        cleanup_op = publish_cortex_path / 'src' / 'operations' / 'workspace_cleanup.py'
        
        assert cleanup_op.exists(), (
            f"SKULL-007 VIOLATION: workspace_cleanup operation missing from publish!\n"
            f"Expected: {cleanup_op}\n"
            f"Impact: Users cannot run 'cleanup' command"
        )
    
    def test_demo_operation_included(self, publish_cortex_path: Path):
        """
        SKULL-007: Verify cortex_demo operation is published.
        
        Required for showcasing CORTEX capabilities to new users.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        demo_op = publish_cortex_path / 'src' / 'operations' / 'cortex_demo.py'
        
        assert demo_op.exists(), (
            f"SKULL-007 VIOLATION: cortex_demo operation missing from publish!\n"
            f"Expected: {demo_op}\n"
            f"Impact: Users cannot run demo to learn CORTEX"
        )
    
    # ============================================================================
    # Core Infrastructure
    # ============================================================================
    
    def test_all_10_agents_included(self, publish_cortex_path: Path):
        """
        SKULL-007: Verify all 10 specialist agents are published.
        
        Required for CORTEX multi-agent architecture.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        required_agents = [
            'intent_detector.py',
            'planner.py',
            'executor.py',
            'tester.py',
            'validator.py',
            'pattern_matcher.py',
            'architect.py',
            'documenter.py',
            'work_planner.py',
            'health_validator.py'
        ]
        
        agents_dir = publish_cortex_path / 'src' / 'cortex_agents'
        
        assert agents_dir.exists(), (
            f"SKULL-007 VIOLATION: cortex_agents directory missing from publish!\n"
            f"Expected: {agents_dir}\n"
            f"Impact: All agent functionality will fail"
        )
        
        missing_agents = []
        for agent in required_agents:
            agent_path = agents_dir / agent
            if not agent_path.exists():
                missing_agents.append(agent)
        
        assert not missing_agents, (
            f"SKULL-007 VIOLATION: Required agents missing from publish!\n"
            f"Missing: {missing_agents}\n"
            f"Impact: Multi-agent workflows will fail"
        )
    
    def test_tier0_brain_protector_included(self, publish_cortex_path: Path):
        """
        SKULL-007: Verify Tier 0 brain protector is published.
        
        Required for brain protection and SKULL rule enforcement.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        brain_protector = publish_cortex_path / 'src' / 'tier0' / 'brain_protector.py'
        
        assert brain_protector.exists(), (
            f"SKULL-007 VIOLATION: Brain protector missing from publish!\n"
            f"Expected: {brain_protector}\n"
            f"Impact: Brain protection will not work"
        )
        
        # Verify brain-protection-rules.yaml exists
        protection_rules = publish_cortex_path / 'cortex-brain' / 'brain-protection-rules.yaml'
        
        assert protection_rules.exists(), (
            f"SKULL-007 VIOLATION: Brain protection rules missing from publish!\n"
            f"Expected: {protection_rules}\n"
            f"Impact: SKULL rules will not be enforced"
        )
    
    def test_tier1_conversation_manager_included(self, publish_cortex_path: Path):
        """
        SKULL-007: Verify Tier 1 conversation manager is published.
        
        Required for conversation tracking and context injection.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        conv_manager = publish_cortex_path / 'src' / 'tier1' / 'conversation_manager.py'
        
        assert conv_manager.exists(), (
            f"SKULL-007 VIOLATION: Conversation manager missing from publish!\n"
            f"Expected: {conv_manager}\n"
            f"Impact: Conversation tracking will not work"
        )
    
    def test_tier2_knowledge_graph_included(self, publish_cortex_path: Path):
        """
        SKULL-007: Verify Tier 2 knowledge graph is published.
        
        Required for pattern learning and intelligent context.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        knowledge_graph = publish_cortex_path / 'src' / 'tier2' / 'knowledge_graph'
        
        assert knowledge_graph.exists(), (
            f"SKULL-007 VIOLATION: Knowledge graph missing from publish!\n"
            f"Expected: {knowledge_graph}\n"
            f"Impact: Pattern learning will not work"
        )
        
        # Verify schema.py exists
        schema = knowledge_graph / 'database' / 'schema.py'
        
        assert schema.exists(), (
            f"SKULL-007 VIOLATION: Knowledge graph schema missing from publish!\n"
            f"Expected: {schema}\n"
            f"Impact: Database initialization will fail"
        )
    
    # ============================================================================
    # Admin Operations (MUST NOT BE INCLUDED)
    # ============================================================================
    
    def test_design_sync_not_included(self, publish_cortex_path: Path):
        """
        SKULL-006: Verify design_sync operation is NOT published.
        
        This is an admin-only development tool.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        design_sync = publish_cortex_path / 'src' / 'operations' / 'design_sync.py'
        
        assert not design_sync.exists(), (
            f"SKULL-006 VIOLATION: Admin operation 'design_sync' found in publish!\n"
            f"Location: {design_sync}\n"
            f"Impact: Admin development tool exposed to end users"
        )
    
    def test_enterprise_documentation_not_included(self, publish_cortex_path: Path):
        """
        SKULL-006: Verify enterprise_documentation operation is NOT published.
        
        This is an admin-only documentation orchestrator.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        enterprise_doc = publish_cortex_path / 'src' / 'operations' / 'enterprise_documentation.py'
        
        assert not enterprise_doc.exists(), (
            f"SKULL-006 VIOLATION: Admin operation 'enterprise_documentation' found in publish!\n"
            f"Location: {enterprise_doc}\n"
            f"Impact: Admin documentation tool exposed to end users"
        )
    
    def test_admin_scripts_not_included(self, publish_cortex_path: Path):
        """
        SKULL-006: Verify admin scripts are NOT published.
        
        Admin scripts should only be in CORTEX development environment.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        admin_scripts = [
            'sync_plugin_commands.py',
            'update_operations_status.py',
            'measure_token_reduction.py',
            'design_sync_orchestrator.py',
            'enterprise_documentation_orchestrator.py'
        ]
        
        scripts_dir = publish_cortex_path / 'scripts'
        
        if not scripts_dir.exists():
            return  # No scripts directory, all good
        
        found_admin_scripts = []
        for admin_script in admin_scripts:
            script_path = scripts_dir / admin_script
            if script_path.exists():
                found_admin_scripts.append(admin_script)
        
        assert not found_admin_scripts, (
            f"SKULL-006 VIOLATION: Admin scripts found in publish!\n"
            f"Found: {found_admin_scripts}\n"
            f"Impact: Admin tools exposed to end users"
        )
    
    def test_admin_folder_not_included(self, publish_cortex_path: Path):
        """
        SKULL-006: Verify cortex-brain/admin/ folder is NOT published.
        
        Admin folder contains development tools and orchestrators.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        admin_folder = publish_cortex_path / 'cortex-brain' / 'admin'
        
        assert not admin_folder.exists(), (
            f"SKULL-006 VIOLATION: Admin folder found in publish!\n"
            f"Location: {admin_folder}\n"
            f"Impact: Admin development tools exposed to end users"
        )
    
    def test_docs_folder_not_included(self, publish_cortex_path: Path):
        """
        SKULL-006: Verify docs/ folder is NOT published.
        
        Docs folder contains admin documentation, image prompts, and narratives.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        docs_folder = publish_cortex_path / 'docs'
        
        assert not docs_folder.exists(), (
            f"SKULL-006 VIOLATION: Docs folder found in publish!\n"
            f"Location: {docs_folder}\n"
            f"Impact: Admin documentation exposed to end users"
        )


class TestPublishUserExperience:
    """Test published package from user's perspective."""
    
    @pytest.fixture
    def publish_cortex_path(self) -> Path:
        """Get path to publish/CORTEX folder."""
        repo_root = Path(__file__).parent.parent.parent
        return repo_root / 'publish' / 'CORTEX'
    
    def test_setup_instructions_exist(self, publish_cortex_path: Path):
        """
        Verify setup instructions exist for users.
        
        Users need clear instructions to get started.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        setup_file = publish_cortex_path / 'SETUP-FOR-COPILOT.md'
        
        assert setup_file.exists(), (
            f"User experience issue: Setup instructions missing!\n"
            f"Expected: {setup_file}\n"
            f"Impact: Users won't know how to install CORTEX"
        )
    
    def test_entry_point_exists(self, publish_cortex_path: Path):
        """
        Verify CORTEX.prompt.md entry point exists.
        
        Required for Copilot to find and load CORTEX.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        entry_point = publish_cortex_path / '.github' / 'prompts' / 'CORTEX.prompt.md'
        
        assert entry_point.exists(), (
            f"User experience issue: Entry point missing!\n"
            f"Expected: {entry_point}\n"
            f"Impact: Copilot cannot find CORTEX"
        )
    
    def test_requirements_file_exists(self, publish_cortex_path: Path):
        """
        Verify requirements.txt exists.
        
        Users need to install dependencies.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        requirements = publish_cortex_path / 'requirements.txt'
        
        assert requirements.exists(), (
            f"User experience issue: requirements.txt missing!\n"
            f"Expected: {requirements}\n"
            f"Impact: Users cannot install dependencies"
        )
    
    def test_license_file_exists(self, publish_cortex_path: Path):
        """
        Verify LICENSE file exists.
        
        Legal requirement for distribution.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        license_file = publish_cortex_path / 'LICENSE'
        
        assert license_file.exists(), (
            f"Legal issue: LICENSE file missing!\n"
            f"Expected: {license_file}\n"
            f"Impact: Cannot legally distribute"
        )
    
    def test_readme_exists(self, publish_cortex_path: Path):
        """
        Verify README.md exists.
        
        Users need overview and quick start guide.
        """
        if not publish_cortex_path.exists():
            pytest.skip("No publish folder found - run publish script first")
        
        readme = publish_cortex_path / 'README.md'
        
        assert readme.exists(), (
            f"User experience issue: README.md missing!\n"
            f"Expected: {readme}\n"
            f"Impact: Users have no overview or quick start"
        )
