"""
Generate Technical CORTEX Doc Module - Story Refresh Operation

This module generates Technical-CORTEX.md with comprehensive technical details
extracted from CORTEX-UNIFIED-ARCHITECTURE.yaml.

Author: Asif Hussain
Version: 2.0 (Mode-aware with architecture-driven generation)
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationPhase,
    OperationStatus
)

logger = logging.getLogger(__name__)


class GenerateTechnicalCortexDocModule(BaseOperationModule):
    """
    Generate Technical-CORTEX.md from architecture data.
    
    This module creates comprehensive technical documentation covering:
    - System architecture (4-tier brain)
    - 10 specialist agents (LEFT/RIGHT brain)
    - Plugin system
    - Memory architecture
    - Test coverage & metrics
    - Development guide
    
    What it does:
        1. Extracts all technical details from architecture evaluation context
        2. Generates sections for tiers, agents, plugins, metrics
        3. Adds code examples and configuration guidance
        4. Writes to Technical-CORTEX.md
    """
    
    def _get_metadata(self) -> OperationModuleMetadata:
        """Get module metadata."""
        return OperationModuleMetadata(
            module_id="generate_technical_cortex_doc",
            name="Generate Technical CORTEX Doc",
            description="Generate Technical-CORTEX.md from architecture data",
            version="2.0",
            author="Asif Hussain",
            dependencies=["evaluate_cortex_architecture"],
            config_schema={
                "output_dir": {
                    "type": "string",
                    "description": "Output directory path",
                    "required": False
                }
            }
        )
    
    def validate(self, context: Dict[str, Any]) -> OperationResult:
        """
        Validate prerequisites.
        
        Args:
            context: Shared context dictionary
        
        Returns:
            OperationResult indicating validation status
        """
        # Check architecture data
        if 'feature_inventory' not in context:
            return OperationResult(
                success=False,
                status=OperationStatus.VALIDATION_FAILED,
                message="Missing feature_inventory in context (run evaluate_cortex_architecture first)"
            )
        
        return OperationResult(
            success=True,
            status=OperationStatus.VALIDATED,
            message="Prerequisites validated"
        )
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Generate Technical-CORTEX.md.
        
        Args:
            context: Shared context dictionary
        
        Returns:
            OperationResult with generation status
        """
        try:
            logger.info("Generating Technical-CORTEX.md...")
            
            # Step 1: Get output path
            output_dir = Path(context.get('output_dir', 'docs/story/CORTEX-STORY'))
            output_dir.mkdir(parents=True, exist_ok=True)
            output_path = output_dir / 'Technical-CORTEX.md'
            
            # Step 2: Create backup if exists
            if output_path.exists():
                backup_dir = output_dir / '.backups'
                backup_dir.mkdir(exist_ok=True)
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                backup_path = backup_dir / f'Technical-CORTEX_{timestamp}.md'
                output_path.rename(backup_path)
                logger.info(f"Backed up existing file to {backup_path}")
            
            # Step 3: Extract architecture data
            feature_inventory = context.get('feature_inventory', {})
            implementation_status = context.get('implementation_status', {})
            architecture_patterns = context.get('architecture_patterns', {})
            
            tiers = feature_inventory.get('tiers', [])
            agents = feature_inventory.get('agents', [])
            plugins = feature_inventory.get('plugins', [])
            
            # Step 4: Generate content
            content = self._generate_technical_doc(
                tiers=tiers,
                agents=agents,
                plugins=plugins,
                implementation_status=implementation_status,
                architecture_patterns=architecture_patterns
            )
            
            # Step 5: Write file
            output_path.write_text(content, encoding='utf-8')
            logger.info(f"Technical doc written: {output_path}")
            
            # Store in context
            context['technical_doc_path'] = output_path
            context['technical_doc_content'] = content
            
            return OperationResult(
                success=True,
                status=OperationStatus.COMPLETED,
                message=f"Technical doc generated: {output_path.name}",
                data={
                    "output_path": str(output_path),
                    "sections": 8,
                    "tiers_documented": len(tiers),
                    "agents_documented": len(agents),
                    "plugins_documented": len(plugins)
                }
            )
            
        except Exception as e:
            logger.error(f"Failed to generate technical doc: {e}", exc_info=True)
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Technical doc generation failed: {e}"
            )
    
    def _generate_technical_doc(
        self,
        tiers: List[Dict],
        agents: List[Dict],
        plugins: List[Dict],
        implementation_status: Dict,
        architecture_patterns: Dict
    ) -> str:
        """
        Generate complete technical documentation.
        
        Args:
            tiers: List of tier definitions
            agents: List of agent definitions
            plugins: List of plugin definitions
            implementation_status: Implementation metrics
            architecture_patterns: Architecture pattern data
        
        Returns:
            Complete markdown content
        """
        sections = []
        
        # Header
        sections.append(self._generate_header())
        
        # Overview
        sections.append(self._generate_overview(tiers, agents, plugins))
        
        # Architecture section
        sections.append(self._generate_architecture_section(tiers))
        
        # Agents section
        sections.append(self._generate_agents_section(agents))
        
        # Plugins section
        sections.append(self._generate_plugins_section(plugins))
        
        # Implementation status
        sections.append(self._generate_implementation_section(implementation_status))
        
        # Development guide
        sections.append(self._generate_development_guide(architecture_patterns))
        
        # Footer
        sections.append(self._generate_footer())
        
        return '\n\n'.join(sections)
    
    def _generate_header(self) -> str:
        """Generate document header."""
        return f"""# Technical Deep-Dive: CORTEX 2.0

**The Complete Technical Guide to the Cognitive Framework**

*Generated: {datetime.now().strftime('%B %d, %Y')}*  
*Version: CORTEX 2.0*

---

> **Note**: This is the technical companion to [THE-AWAKENING-OF-CORTEX.md](THE-AWAKENING-OF-CORTEX.md).  
> For the narrative story, read that file first.

---"""
    
    def _generate_overview(
        self,
        tiers: List[Dict],
        agents: List[Dict],
        plugins: List[Dict]
    ) -> str:
        """Generate overview section."""
        return f"""## Overview

CORTEX (Cognitive Operations & Reasoning TEXture) transforms GitHub Copilot from an amnesiac assistant into a continuously improving development partner.

**Key Metrics:**
- **{len(tiers)} Brain Tiers**: Hierarchical memory architecture
- **{len(agents)} Specialist Agents**: LEFT (tactical) and RIGHT (strategic) brain
- **{len(plugins)} Plugins**: Extensible capability system
- **SQLite Memory**: Last 20 conversations preserved
- **YAML Knowledge**: Accumulated patterns and learnings

**Architecture Philosophy:**
- **Tier 0 (Instinct)**: Immutable governance rules
- **Tier 1 (Memory)**: Conversation history (SQLite)
- **Tier 2 (Knowledge)**: Learned patterns (YAML)
- **Tier 3 (Context)**: Development metrics (Git, tests, coverage)"""
    
    def _generate_architecture_section(self, tiers: List[Dict]) -> str:
        """Generate architecture section."""
        content = ["## Architecture: The 4-Tier Brain", ""]
        
        for tier in tiers:
            tier_id = tier.get('id', 'unknown')
            name = tier.get('name', 'Unknown')
            description = tier.get('description', '')
            storage = tier.get('storage_type', 'N/A')
            
            content.append(f"### Tier {tier_id}: {name}")
            content.append("")
            content.append(description)
            content.append("")
            content.append(f"**Storage**: {storage}")
            content.append("")
            
            # Add key files
            key_files = tier.get('key_files', [])
            if key_files:
                content.append("**Key Files:**")
                for file_path in key_files:
                    content.append(f"- `{file_path}`")
                content.append("")
            
            # Add operations
            operations = tier.get('operations', [])
            if operations:
                content.append("**Operations:**")
                for op in operations:
                    content.append(f"- {op}")
                content.append("")
        
        return '\n'.join(content)
    
    def _generate_agents_section(self, agents: List[Dict]) -> str:
        """Generate agents section."""
        content = ["## The 10 Specialist Agents", ""]
        
        # Group by brain hemisphere
        left_brain = [a for a in agents if a.get('hemisphere') == 'LEFT']
        right_brain = [a for a in agents if a.get('hemisphere') == 'RIGHT']
        
        content.append("### LEFT BRAIN: Tactical Execution")
        content.append("")
        for agent in left_brain:
            name = agent.get('name', 'Unknown')
            role = agent.get('role', '')
            capabilities = agent.get('capabilities', [])
            
            content.append(f"#### {name}")
            content.append(f"**Role**: {role}")
            content.append("")
            if capabilities:
                content.append("**Capabilities:**")
                for cap in capabilities:
                    content.append(f"- {cap}")
                content.append("")
        
        content.append("### RIGHT BRAIN: Strategic Planning")
        content.append("")
        for agent in right_brain:
            name = agent.get('name', 'Unknown')
            role = agent.get('role', '')
            capabilities = agent.get('capabilities', [])
            
            content.append(f"#### {name}")
            content.append(f"**Role**: {role}")
            content.append("")
            if capabilities:
                content.append("**Capabilities:**")
                for cap in capabilities:
                    content.append(f"- {cap}")
                content.append("")
        
        return '\n'.join(content)
    
    def _generate_plugins_section(self, plugins: List[Dict]) -> str:
        """Generate plugins section."""
        content = ["## Plugin System", ""]
        content.append("CORTEX uses an extensible plugin architecture. All plugins inherit from `BasePlugin`.")
        content.append("")
        
        for plugin in plugins:
            plugin_id = plugin.get('plugin_id', 'unknown')
            name = plugin.get('name', 'Unknown')
            description = plugin.get('description', '')
            commands = plugin.get('commands', [])
            
            content.append(f"### {name}")
            content.append(f"**ID**: `{plugin_id}`")
            content.append("")
            content.append(description)
            content.append("")
            
            if commands:
                content.append("**Commands:**")
                for cmd in commands:
                    cmd_name = cmd.get('command', '/unknown')
                    cmd_desc = cmd.get('description', '')
                    content.append(f"- `{cmd_name}`: {cmd_desc}")
                content.append("")
        
        # Add plugin development guide
        content.append("### Creating a New Plugin")
        content.append("")
        content.append("```python")
        content.append("from src.plugins.base_plugin import BasePlugin, PluginMetadata")
        content.append("")
        content.append("class MyPlugin(BasePlugin):")
        content.append("    def _get_metadata(self) -> PluginMetadata:")
        content.append("        return PluginMetadata(")
        content.append('            plugin_id="my_plugin",')
        content.append('            name="My Plugin",')
        content.append('            version="1.0",')
        content.append('            description="Does something cool"')
        content.append("        )")
        content.append("")
        content.append("    def initialize(self) -> bool:")
        content.append("        # Setup logic")
        content.append("        return True")
        content.append("")
        content.append("    def execute(self, request: str, context: Dict) -> Dict:")
        content.append("        # Main logic")
        content.append('        return {"status": "success"}')
        content.append("")
        content.append("def register() -> BasePlugin:")
        content.append("    return MyPlugin()")
        content.append("```")
        content.append("")
        
        return '\n'.join(content)
    
    def _generate_implementation_section(self, implementation_status: Dict) -> str:
        """Generate implementation status section."""
        content = ["## Implementation Status", ""]
        
        tests_passing = implementation_status.get('tests_passing', 0)
        test_coverage = implementation_status.get('test_coverage', 0)
        token_reduction = implementation_status.get('token_reduction', 0)
        
        content.append(f"**Tests Passing**: {tests_passing}")
        content.append(f"**Test Coverage**: {test_coverage}%")
        content.append(f"**Token Optimization**: {token_reduction}% reduction")
        content.append("")
        
        recent_changes = implementation_status.get('recent_changes', [])
        if recent_changes:
            content.append("### Recent Changes")
            content.append("")
            for change in recent_changes:
                content.append(f"- {change}")
            content.append("")
        
        return '\n'.join(content)
    
    def _generate_development_guide(self, architecture_patterns: Dict) -> str:
        """Generate development guide section."""
        content = ["## Development Guide", ""]
        
        content.append("### Running Tests")
        content.append("```bash")
        content.append("# Run all tests")
        content.append("pytest")
        content.append("")
        content.append("# Run specific suite")
        content.append("pytest tests/plugins/")
        content.append("")
        content.append("# Test coverage")
        content.append("pytest --cov=src")
        content.append("```")
        content.append("")
        
        content.append("### Configuration")
        content.append("CORTEX uses `cortex.config.json` for multi-machine paths:")
        content.append("```json")
        content.append("{")
        content.append('  "machine_name": "your-machine-name",')
        content.append('  "paths": {')
        content.append('    "cortex_root": "/absolute/path/to/CORTEX"')
        content.append("  }")
        content.append("}")
        content.append("```")
        content.append("")
        
        content.append("### Key Patterns")
        content.append("")
        for pattern_name, pattern_desc in architecture_patterns.items():
            content.append(f"**{pattern_name}**:")
            content.append(f"- {pattern_desc}")
            content.append("")
        
        return '\n'.join(content)
    
    def _generate_footer(self) -> str:
        """Generate document footer."""
        return """---

**Related Documentation:**
- [THE-AWAKENING-OF-CORTEX.md](THE-AWAKENING-OF-CORTEX.md) - Narrative story
- [Image-Prompts.md](Image-Prompts.md) - Visual journey
- [History.md](History.md) - Evolution timeline

---

*This technical guide provides comprehensive implementation details for developers working with CORTEX.*  
*For the engaging narrative version, see THE-AWAKENING-OF-CORTEX.md*

---

**THE END**"""
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """
        Rollback by removing generated file.
        
        Args:
            context: Shared context dictionary
        
        Returns:
            True if rollback succeeded
        """
        try:
            tech_doc_path = context.get('technical_doc_path')
            
            if tech_doc_path and Path(tech_doc_path).exists():
                Path(tech_doc_path).unlink()
                logger.info(f"Removed technical doc: {tech_doc_path}")
            
            # Clear context
            context.pop('technical_doc_path', None)
            context.pop('technical_doc_content', None)
            
            return True
        
        except Exception as e:
            logger.error(f"Rollback failed: {e}", exc_info=True)
            return False
    
    def should_run(self, context: Dict[str, Any]) -> bool:
        """
        Determine if module should run.
        
        Args:
            context: Shared context dictionary
        
        Returns:
            True if architecture data available
        """
        return 'feature_inventory' in context
    
    def get_progress_message(self) -> str:
        """Get progress message."""
        return "Generating technical documentation from architecture..."


def register() -> BaseOperationModule:
    """Register this module."""
    return GenerateTechnicalCortexDocModule()
