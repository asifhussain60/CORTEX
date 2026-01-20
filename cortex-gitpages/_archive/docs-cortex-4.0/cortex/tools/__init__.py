"""
CORTEX Tools Module

CLI tools unified under single entry point.
All tools should be registered here and invoked via toolkit.py.

See toolkit.py for the main entry point.

This package contains tools for orchestrator development and template management:
- TemplateParser: Parse and validate orchestrator templates
- ToolGenerator: Generate tooling and utilities from templates
- OrchestratorScaffolder: Generate orchestrator code from templates
- ScaffolderTemplate: Template types for scaffolding
- TemplateValidator: Validate template consistency and completeness
- TemplateTestFramework: Testing framework for templates
"""

# Lazy imports to avoid circular dependencies
def get_template_parser():
    from cortex.tools.template_parser import TemplateParser
    return TemplateParser

def get_tool_generator():
    from cortex.tools.tool_generator import ToolGenerator
    return ToolGenerator

def get_orchestrator_scaffolder():
    from cortex.tools.orchestrator_scaffolder import OrchestratorScaffolder
    return OrchestratorScaffolder

def get_template_validator():
    from cortex.tools.template_validator import TemplateValidator
    return TemplateValidator

def get_testing_framework():
    from cortex.tools.testing_framework import TemplateTestFramework
    return TemplateTestFramework

__all__ = [
    'get_template_parser',
    'get_tool_generator',
    'get_orchestrator_scaffolder',
    'get_template_validator',
    'get_testing_framework',
]
