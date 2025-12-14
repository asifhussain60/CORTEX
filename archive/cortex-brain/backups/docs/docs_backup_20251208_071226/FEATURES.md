# CORTEX Features

**Generated:** 2025-11-21 08:51:59

## Operations (23)

- ⏳ **application_onboarding** - One-command CORTEX deployment with intelligent codebase discovery and contextual questioning
- ⏳ **architecture_planning** - [FUTURE] Collaborative architecture design with guided questions - Advanced planning feature
- ⏳ **brain_health_check** - [DEPRECATED] Use 'maintain_cortex' instead - Comprehensive self-diagnostic that validates all CORTEX components, identifies issues, and suggests optimizations
- ⏳ **brain_protection_check** - [EXPERIMENTAL] Validate CORTEX brain protection rules and integrity - Tier 0 governance handles this automatically
- ⏳ **command_help** - [INTEGRATED] Command discovery integrated into CORTEX help system and natural language interface
- ⏳ **command_search** - [INTEGRATED] Command search integrated into CORTEX help system and natural language interface
- ⏳ **comprehensive_self_review** - [EXPERIMENTAL] Validate all brain protection layers, coding standards, and architecture integrity - Advanced validation feature
- ✅ **cortex_tutorial** - Hands-on walkthrough of CORTEX capabilities with live execution
- ⏳ **deploy_to_app** - [FUTURE] Deploy CORTEX package to target application - Advanced deployment automation feature
- ✅ **design_sync** - Resynchronizes CORTEX design documents with actual implementation, consolidates to single status doc, integrates optimization recommendations, converts verbose MD to YAML schemas
- ✅ **document_cortex** - Comprehensive CORTEX documentation management combining story refresh and documentation updates
- ✅ **enterprise_documentation** - EPM-based comprehensive documentation generation using Entry Point Module (EPM) system for enterprise-grade documentation workflows
- ✅ **environment_setup** - Configure CORTEX development environment on Mac/Windows/Linux
- ✅ **feature_planning** - Interactive feature planning with Work Planner agent - breaks down requirements into executable phases
- ⏳ **interactive_planning** - [INTEGRATED] Interactive planning integrated into feature_planning operation with CORTEX 2.1 capabilities
- ✅ **maintain_cortex** - Comprehensive CORTEX maintenance combining workspace cleanup, system optimization, and health diagnostics
- ⏳ **optimize_cortex** - [DEPRECATED] Use 'maintain_cortex' instead - Holistic architecture review with SKULL tests and automated optimizations
- ✅ **publish_cortex** - Build production-ready package and publish to cortex-publish branch for user deployment
- ⏳ **refactoring_planning** - [FUTURE] Interactive refactoring with clarification questions - Advanced refactoring assistance
- ✅ **regenerate_diagrams** - Analyze CORTEX design and regenerate all visual assets from scratch
- ⏳ **run_tests** - [INTEGRATED] Test execution integrated into maintain_cortex and other operations as validation
- ⏳ **update_documentation** - [DEPRECATED] Use 'document_cortex' instead - Refresh and build CORTEX documentation site
- ⏳ **user_onboarding** - Guided new user experience with interactive learning and hands-on validation

## Modules (45)

- ⏳ **apply_narrator_voice** - Transform story with narrator voice
- ⏳ **brain_initialization** - Initialize CORTEX brain tiers
- ⏳ **brain_tests** - Run brain integrity tests
- ⏳ **build_mkdocs_site** - Build complete documentation site
- ⏳ **build_story_preview** - Generate HTML preview of transformed story
- ⏳ **clear_python_cache** - Remove __pycache__ directories
- ⏳ **compress_old_files** - Compress large old files
- ⏳ **conversation_tracking** - Configure conversation capture daemon
- ⏳ **demo_cleanup** - Demonstrate cleanup operation
- ⏳ **demo_completion** - Summary and next steps
- ⏳ **demo_conversation** - Demonstrate conversation memory
- ⏳ **demo_help_system** - Demonstrate help command capabilities
- ⏳ **demo_introduction** - Welcome message and demo flow explanation
- ⏳ **demo_story_refresh** - Show story transformation in action
- ⏳ **deploy_docs_preview** - Deploy story preview to docs site
- ⏳ **deploy_docs_site** - Deploy docs to GitHub Pages
- ⏳ **docs_completion** - Finalize documentation with summary
- ⏳ **generate_api_docs** - Generate API reference documentation
- ⏳ **generate_cleanup_report** - Create cleanup summary report
- ⏳ **generate_diagrams** - Generate architecture diagrams
- ⏳ **git_sync** - Sync project with remote git repository
- ⏳ **load_story_source** - Load original CORTEX story markdown
- ⏳ **load_story_template** - Load story template for transformation
- ⏳ **platform_detection** - Detect OS and configure platform-specific settings
- ⏳ **project_validation** - Validate CORTEX project structure
- ⏳ **python_dependencies** - Install required Python packages
- ⏳ **refresh_design_docs** - Update design documentation files
- ⏳ **remove_old_logs** - Clean up old log files
- ⏳ **remove_orphaned_files** - Clean up orphaned temporary files
- ⏳ **save_story_markdown** - Write transformed story to file
- ⏳ **scan_docstrings** - Extract docstrings from source code
- ⏳ **scan_temporary_files** - Identify temporary files for removal
- ⏳ **setup_completion** - Finalize setup and provide summary
- ⏳ **story_length_manager** - Manage story length and token optimization
- ⏳ **story_refresh_completion** - Finalize story refresh with summary
- ⏳ **tooling_verification** - Verify required tools are available
- ⏳ **update_changelog** - Update CHANGELOG.md
- ⏳ **update_mkdocs_index** - Update documentation index
- ⏳ **update_story_docs** - Update story in documentation site
- ⏳ **vacuum_sqlite_databases** - Optimize SQLite database files
- ⏳ **validate_cleanup_safety** - Ensure cleanup didn't break anything
- ⏳ **validate_doc_links** - Check for broken links in docs
- ⏳ **validate_story_structure** - Ensure story meets structural requirements
- ⏳ **virtual_environment** - Create and configure Python virtual environment
- ⏳ **vision_api** - Configure Google Cloud Vision API

## Plugins (25)

- ✅ **BasePlugin** - Abstract base class for all CORTEX plugins.

All plugins must:
1. Inherit from BasePlugin
2. Implement _get_metadata() method
3. Implement initialize() method
4. Implement execute() method
5. Implement cleanup() method

Example:
```python
class MyPlugin(BasePlugin):
    def _get_metadata(self) -> PluginMetadata:
        return PluginMetadata(
            plugin_id="my_plugin",
            name="My Plugin",
            version="1.0.0",
            category=PluginCategory.WORKFLOW,
            priority=PluginPriority.MEDIUM,
            description="Does something useful",
            author="Your Name",
            dependencies=[],
            hooks=[HookPoint.ON_WORKFLOW_START.value],
            config_schema={}
        )
    
    def initialize(self) -> bool:
        # Setup plugin resources
        return True
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        # Main plugin logic
        return {"success": True}
    
    def cleanup(self) -> bool:
        # Cleanup plugin resources
        return True
```
- ✅ **BrainTransferPlugin** - Brain Transfer Plugin for CORTEX.

Provides:
- Export brain patterns to YAML
- Import brain patterns from YAML
- Intelligent conflict resolution
- Namespace-aware merging
- ✅ **CodeReviewPlugin** - Automated code review plugin for pull requests

Features:
- SOLID principle violation detection
- Security vulnerability scanning
- Performance anti-pattern detection
- Test coverage regression checking
- Code style consistency validation
- Duplicate code detection
- Integration with Azure DevOps, GitHub, GitLab, BitBucket
- ✅ **ConfigurationWizardPlugin** - Configuration Wizard Plugin

Provides incremental, post-setup configuration with intelligent
auto-discovery. Does NOT block initial setup.

Architecture:
- Phase 1: Auto-discovery (scan environment, files, code)
- Phase 2: User confirmation (review discovered items)
- Phase 3: Manual entry (fill gaps)
- Phase 4: Validation (test connections)
- Phase 5: Save to cortex.config.json
- ✅ **ConversationImportPlugin** - Plugin for importing Copilot conversations to CORTEX brain.

Provides dual-channel learning:
- Channel 1: Ambient daemon (execution-focused)
- Channel 2: Manual conversations (strategy-focused)
- ✅ **DocRefreshPlugin** - Orchestrates documentation refresh operations using modular services
- ✅ **InvestigationHtmlIdMappingPlugin** - HTML element ID mapping plugin for investigation router
- ✅ **InvestigationRefactoringPlugin** - Refactoring analysis plugin for investigation router
- ✅ **InvestigationSecurityPlugin** - Security analysis plugin for investigation router
- ✅ **PerformanceTelemetryPlugin** - Collects CORTEX performance and business value metrics for team analytics.

Tracked Metrics:
1. Performance: Latency, success rates, error patterns, trends
2. Cost Savings: Token optimization ($$$), API cost avoidance
3. Productivity: Commits, PRs, velocity, code quality
4. Copilot Enhancement: Memory hits, context utilization, suggestion quality
5. Quality: Bug reduction, test coverage, code review efficiency

Engineer Attribution:
- Name, email, machine hostname
- Machine specs (CPU, RAM, platform)
- Installation date, CORTEX version

Use Case: Internal team analytics and executive ROI reporting
- ✅ **PhaseTrackerPlugin** - Phase tracking plugin for CORTEX workflow management.

Features:
- Create and manage phase tracking for projects
- Track progress, blockers, time estimates
- Support multi-track development
- Integration with CORTEX agents and operations
- ✅ **PlatformSwitchPlugin** - Handles platform switching for CORTEX development.

Automates:
1. Git pull latest code
2. Environment setup for platform
3. Brain tests validation
4. Tooling and dependencies verification
- ✅ **Plugin** - Comprehensive Cleanup Plugin for CORTEX
- ✅ **PluginCategory** - Plugin categories for organization
- ✅ **PluginCommandRegistry** - Central registry for all plugin commands.

Features:
- Automatic conflict detection
- O(1) command lookup
- Auto-generated help text
- Plugin discovery

Usage:
    registry = PluginCommandRegistry()
    
    # Plugin registers commands during initialization
    registry.register_command(CommandMetadata(
        command="/mac",
        natural_language_equivalent="switched to mac",
        plugin_id="platform_switch",
        ...
    ))
    
    # Router expands commands
    expanded = registry.expand_command("/mac")
    # → "switched to mac"
- ✅ **PluginConfig** - Complete plugin configuration
- ✅ **PluginManager** - Manages plugin lifecycle and execution.

Responsibilities:
- Plugin discovery and loading
- Hook registration and execution
- Plugin dependency resolution
- Configuration management
- ✅ **PluginMetadata** - Standardized metadata for all plugins
- ✅ **PluginPriority** - Plugin execution priority
- ✅ **PluginProcessor** - Process and execute YAML-based plugins
- ✅ **PluginRegistry** - Central registry for plugin management.

Responsibilities:
- Plugin discovery and loading
- Plugin lifecycle management (init, execute, cleanup)
- Plugin metadata and capability tracking
- Natural language command routing
- ✅ **PluginRegistryCrawler** - Inventories CORTEX plugin system to analyze:
- Registered plugins (active/inactive)
- Natural language patterns
- Command registry entries
- Plugin health and initialization
- ✅ **PluginType** - Plugin categories
- ✅ **SweeperPlugin** - Aggressive file sweeper - moves clutter to Recycle Bin (reversible).

Usage:
    sweeper = SweeperPlugin()
    sweeper.initialize()
    results = sweeper.execute({"workspace_root": "/path/to/cortex"})
- ✅ **SystemRefactorPlugin** - Plugin for critical system review and automated refactoring.

Capabilities:
- Analyze test coverage across all layers
- Identify gaps in brain protection, plugins, modules
- Execute REFACTOR phase for tests in GREEN state
- Generate comprehensive review reports
- Automate gap-filling through test generation

## Agents (25)

- ✅ **AgentExecutionError** - Raised when agent execution fails
- ✅ **AgentExecutor** - Executes specific agents based on routing decisions.

This class takes routing decisions from IntentRouter and actually
instantiates and executes the appropriate specialist agents.
- ✅ **AgentMessage** - Message format for agent-to-agent communication in workflows.

Used for orchestrating multi-agent workflows like TDD cycle.

Attributes:
    from_agent: Name of the sending agent
    to_agent: Name of the receiving agent
    command: Command/action to perform
    payload: Data payload for the command
    correlation_id: Optional ID to correlate related messages

Example:
    message = AgentMessage(
        from_agent="workflow-orchestrator",
        to_agent="test-generator",
        command="create_test",
        payload={"task": "auth", "expect_failure": True}
    )
- ✅ **AgentMetrics** - Metrics for agent performance tracking
- ✅ **AgentNotFoundError** - Raised when no agent can handle a request
- ✅ **AgentRequest** - Standard request format for all agents.

Attributes:
    intent: The classified user intent (e.g., "plan", "code", "test")
    context: Additional context information (files, settings, etc.)
    user_message: Original user message text
    conversation_id: Optional ID linking to Tier 1 conversation
    priority: Request priority level (default: NORMAL)
    metadata: Additional metadata for the request

Example:
    request = AgentRequest(
        intent="plan",
        context={"feature": "authentication"},
        user_message="Add user authentication"
    )
- ✅ **AgentResponse** - Standard response format for all agents.

Attributes:
    success: Whether the agent executed successfully
    result: The main result/output from the agent
    message: Human-readable message describing the outcome
    metadata: Additional metadata about the execution
    agent_name: Name of the agent that generated this response
    duration_ms: Execution time in milliseconds
    next_actions: Suggested follow-up actions
    error: Optional error message if execution failed

Example:
    response = AgentResponse(
        success=True,
        result={"tasks": ["Create auth model", "Add login route"]},
        message="Feature broken down into 2 tasks",
        agent_name="WorkPlanner"
    )
- ✅ **AgentRole** - Enhanced agent roles for 3.0
- ✅ **AgentTask** - Task for agent execution
- ✅ **AgentTier** - Agent hierarchy tiers
- ✅ **AgentTimeoutError** - Raised when agent execution exceeds timeout
- ✅ **AgentType** - Categories of specialist agents
- ✅ **ArchitectAgent** - Strategic agent for architectural analysis with automatic brain saving.

Performs deep architectural analysis including:
- Shell structure analysis (layout, navigation, panels)
- Routing system mapping (states, URLs, templates)
- View injection pattern documentation
- Feature directory structure analysis
- Component interaction flows

Key Features:
- Automatic namespace detection (e.g., ksessions_architecture)
- Structured analysis data persistence
- Cross-session memory via Tier 2 Knowledge Graph
- User confirmation of brain saves

Example:
    architect = ArchitectAgent("Architect", tier1_api, tier2_kg, tier3_context)
    
    request = AgentRequest(
        intent="analyze_architecture",
        context={"workspace_path": "/path/to/KSESSIONS"},
        user_message="crawl shell.html to understand KSESSIONS architecture"
    )
    
    response = architect.execute(request)
    # Analysis automatically saved to brain with namespace: ksessions_architecture
- ✅ **BaseAgent** - Base class for all CORTEX agents.

Provides common functionality including:
- Logging configuration
- Metrics tracking  
- Error handling
- Execution timing
- Health monitoring
- ✅ **BrainIngestionAdapterAgent** - Adapter to bridge interface differences
- ✅ **BrainIngestionAgent** - Abstract base class for brain ingestion agent
- ✅ **BrainIngestionAgentImpl** - Implementation of Brain Ingestion Agent that extracts feature intelligence
and stores it in CORTEX brain tiers.
- ✅ **CodeReviewerAgent** - Specialized agent for code quality analysis
- ✅ **CortexAgentError** - Base exception for all CORTEX agent errors
- ✅ **DependencyAnalyzerAgent** - Specialized agent for dependency analysis
- ✅ **EnhancedAgentSystem** - Main enhanced agent system for CORTEX 3.0
- ✅ **InteractivePlannerAgent** - Interactive Planning Agent - CORTEX 2.1

Collaborative planning through guided dialogue. Detects ambiguity
in user requests, asks up to 5 clarifying questions, and creates
refined implementation plans based on answers.

Features:
- Confidence-based routing (auto-detect when to ask questions)
- Question budget (max 5 questions per session)
- User controls: skip, done, back, restart, abort
- Session persistence (can resume interrupted sessions)
- User preference learning (adapts over time)

Workflow:
1. Detect ambiguity in user request
2. If confidence < 60%, enter interactive mode
3. Ask up to 5 clarifying questions (one at a time)
4. Build refined plan from answers
5. Confirm plan with user
6. Execute or save for later

Example:
    planner = InteractivePlannerAgent("Planner", tier1, tier2, tier3)
    
    request = AgentRequest(
        intent="plan",
        context={},
        user_message="Refactor authentication"
    )
    
    response = planner.execute(request)
    # Returns session with questions to ask
- ✅ **LearningCaptureAgent** - Agent that automatically captures lessons learned from various sources.

Sources:
- Operation execution results (success/failure patterns)
- Error traces and exceptions
- Git commit messages and diffs
- Ambient daemon events (file changes, terminal output, errors)
- SKULL protection violations
- ✅ **MultiAgentOrchestrator** - Orchestrates multi-agent workflows
- ✅ **SubAgent** - Base class for specialized sub-agents
