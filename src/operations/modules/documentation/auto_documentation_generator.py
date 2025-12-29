"""
Automatic Documentation Generator - Learning library automation.

Generates comprehensive documentation for all Tier 3/4 operations,
creating learning artifacts in standardized folder structure.

Copyright © 2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class DocumentationSet:
    """Complete documentation set for a component."""
    readme: str
    context: str
    architecture: str
    implementation_guide: str
    test_strategy: str
    research_notes: str


class AutoDocumentationGenerator:
    """Generate automatic documentation for learning library."""
    
    def __init__(self, project_root: Path = None):
        """
        Initialize documentation generator.
        
        Args:
            project_root: Root directory of CORTEX project
        """
        self.project_root = project_root or Path.cwd()
        self.learning_base = self.project_root / "cortex-brain" / "learning"
        
        # Documentation categories
        self.categories = {
            'orchestration': 'Orchestrator designs and patterns',
            'routing': 'Router and analyzer implementations',
            'intelligence': 'AI/ML components and learning systems',
            'analysis': 'AST and code analysis tools',
            'testing': 'TDD patterns and test strategies'
        }
        
        # Document templates
        self.templates = self._initialize_templates()
        
    def _initialize_templates(self) -> Dict[str, str]:
        """Initialize document templates."""
        return {
            'readme': '''# {component_name}

**Component ID:** `{component_id}`  
**Version:** {version}  
**Category:** {category}  
**Generated:** {timestamp}

---

## Overview

{description}

## Key Features

{key_features}

## Quick Start

{quickstart}

## Usage Example

```python
{usage_example}
```

## Dependencies

{dependencies}

## Documentation

- [Context](context.md) - Problem statement and requirements
- [Architecture](architecture.md) - Design and structure
- [Implementation Guide](implementation-guide.md) - Development details
- [Test Strategy](test-strategy.md) - Testing approach
- [Research Notes](research-notes.md) - Learnings and decisions

---

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
''',
            
            'context': '''# {component_name} - Context

**Component ID:** `{component_id}`  
**Generated:** {timestamp}

---

## Problem Statement

{problem_statement}

## Requirements

### Functional Requirements

{functional_requirements}

### Non-Functional Requirements

{non_functional_requirements}

## Use Cases

{use_cases}

## Success Criteria

{success_criteria}

---

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
''',
            
            'architecture': '''# {component_name} - Architecture

**Component ID:** `{component_id}`  
**Generated:** {timestamp}

---

## Architecture Overview

{architecture_overview}

## Component Structure

{component_structure}

## Data Flow

{data_flow}

## Key Interfaces

{key_interfaces}

## Integration Points

{integration_points}

## Design Decisions

{design_decisions}

---

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
''',
            
            'implementation_guide': '''# {component_name} - Implementation Guide

**Component ID:** `{component_id}`  
**Generated:** {timestamp}

---

## Implementation Overview

{implementation_overview}

## Core Components

{core_components}

## Key Algorithms

{key_algorithms}

## Error Handling

{error_handling}

## Performance Considerations

{performance_considerations}

## Extension Points

{extension_points}

---

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
''',
            
            'test_strategy': '''# {component_name} - Test Strategy

**Component ID:** `{component_id}`  
**Generated:** {timestamp}

---

## Test Overview

{test_overview}

## Test Coverage

{test_coverage}

## Unit Tests

{unit_tests}

## Integration Tests

{integration_tests}

## Test Data

{test_data}

## Continuous Testing

{continuous_testing}

---

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
''',
            
            'research_notes': '''# {component_name} - Research Notes

**Component ID:** `{component_id}`  
**Generated:** {timestamp}

---

## Research Summary

{research_summary}

## Alternative Approaches

{alternative_approaches}

## Trade-offs

{trade_offs}

## Lessons Learned

{lessons_learned}

## Future Enhancements

{future_enhancements}

## References

{references}

---

**Author:** Asif Hussain | **GitHub:** github.com/asifhussain60/CORTEX
'''
        }
        
    def generate_documentation(
        self,
        component_name: str,
        category: str,
        context: Dict[str, Any]
    ) -> DocumentationSet:
        """
        Generate complete documentation set for component.
        
        Args:
            component_name: Name of component (e.g., "planning_orchestrator")
            category: Documentation category
            context: Component context (code, design, decisions)
            
        Returns:
            Complete documentation set
        """
        logger.info(f"Generating documentation for {component_name} ({category})")
        
        # Validate category
        if category not in self.categories:
            logger.warning(f"Unknown category '{category}', defaulting to 'orchestration'")
            category = 'orchestration'
        
        # Create category folder if not exists
        category_path = self.learning_base / category
        category_path.mkdir(parents=True, exist_ok=True)
        
        # Create component folder
        component_path = category_path / component_name
        component_path.mkdir(exist_ok=True)
        
        # Generate each document type
        docs = DocumentationSet(
            readme=self._generate_readme(component_name, category, context),
            context=self._generate_context(component_name, context),
            architecture=self._generate_architecture(component_name, context),
            implementation_guide=self._generate_implementation_guide(component_name, context),
            test_strategy=self._generate_test_strategy(component_name, context),
            research_notes=self._generate_research_notes(component_name, context)
        )
        
        # Write documents to files
        self._write_documentation(component_path, docs)
        
        logger.info(f"Documentation written to {component_path}")
        
        return docs
        
    def _generate_readme(
        self,
        component: str,
        category: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate README.md - Overview & quickstart."""
        return self.templates['readme'].format(
            component_name=component.replace('_', ' ').title(),
            component_id=component,
            version=context.get('version', '1.0.0'),
            category=category,
            description=context.get('description', 'No description provided'),
            quickstart=self._generate_quickstart(context),
            key_features=self._format_features(context.get('features', [])),
            usage_example=context.get('usage_example', '# TODO: Add usage example'),
            dependencies=self._format_dependencies(context.get('dependencies', [])),
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
    def _generate_context(self, component: str, context: Dict[str, Any]) -> str:
        """Generate context.md - Problem statement & requirements."""
        return self.templates['context'].format(
            component_name=component.replace('_', ' ').title(),
            component_id=component,
            problem_statement=context.get('problem_statement', 'No problem statement provided'),
            functional_requirements=self._format_list(
                context.get('functional_requirements', ['No functional requirements specified'])
            ),
            non_functional_requirements=self._format_list(
                context.get('non_functional_requirements', ['No non-functional requirements specified'])
            ),
            use_cases=self._format_list(context.get('use_cases', ['No use cases specified'])),
            success_criteria=self._format_list(
                context.get('success_criteria', ['No success criteria specified'])
            ),
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
    def _generate_architecture(self, component: str, context: Dict[str, Any]) -> str:
        """Generate architecture.md - Design & structure."""
        return self.templates['architecture'].format(
            component_name=component.replace('_', ' ').title(),
            component_id=component,
            architecture_overview=context.get('architecture_overview', 'No architecture overview provided'),
            component_structure=context.get('component_structure', 'No component structure specified'),
            data_flow=context.get('data_flow', 'No data flow description provided'),
            key_interfaces=self._format_list(context.get('key_interfaces', ['No interfaces specified'])),
            integration_points=self._format_list(
                context.get('integration_points', ['No integration points specified'])
            ),
            design_decisions=self._format_list(
                context.get('design_decisions', ['No design decisions documented'])
            ),
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
    def _generate_implementation_guide(
        self,
        component: str,
        context: Dict[str, Any]
    ) -> str:
        """Generate implementation-guide.md - Development details."""
        return self.templates['implementation_guide'].format(
            component_name=component.replace('_', ' ').title(),
            component_id=component,
            implementation_overview=context.get(
                'implementation_overview',
                'No implementation overview provided'
            ),
            core_components=self._format_list(
                context.get('core_components', ['No core components specified'])
            ),
            key_algorithms=context.get('key_algorithms', 'No algorithms described'),
            error_handling=context.get('error_handling', 'No error handling strategy specified'),
            performance_considerations=context.get(
                'performance_considerations',
                'No performance considerations documented'
            ),
            extension_points=self._format_list(
                context.get('extension_points', ['No extension points identified'])
            ),
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
    def _generate_test_strategy(self, component: str, context: Dict[str, Any]) -> str:
        """Generate test-strategy.md - Testing approach."""
        return self.templates['test_strategy'].format(
            component_name=component.replace('_', ' ').title(),
            component_id=component,
            test_overview=context.get('test_overview', 'No test overview provided'),
            test_coverage=context.get('test_coverage', 'No test coverage metrics available'),
            unit_tests=self._format_list(context.get('unit_tests', ['No unit tests specified'])),
            integration_tests=self._format_list(
                context.get('integration_tests', ['No integration tests specified'])
            ),
            test_data=context.get('test_data', 'No test data strategy specified'),
            continuous_testing=context.get(
                'continuous_testing',
                'No continuous testing strategy specified'
            ),
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
    def _generate_research_notes(self, component: str, context: Dict[str, Any]) -> str:
        """Generate research-notes.md - Learnings & decisions."""
        return self.templates['research_notes'].format(
            component_name=component.replace('_', ' ').title(),
            component_id=component,
            research_summary=context.get('research_summary', 'No research summary provided'),
            alternative_approaches=self._format_list(
                context.get('alternative_approaches', ['No alternatives explored'])
            ),
            trade_offs=self._format_list(context.get('trade_offs', ['No trade-offs documented'])),
            lessons_learned=self._format_list(
                context.get('lessons_learned', ['No lessons learned recorded'])
            ),
            future_enhancements=self._format_list(
                context.get('future_enhancements', ['No future enhancements planned'])
            ),
            references=self._format_list(context.get('references', ['No references provided'])),
            timestamp=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        )
        
    def _generate_quickstart(self, context: Dict[str, Any]) -> str:
        """Generate quickstart section."""
        steps = context.get('quickstart_steps', [
            'Install dependencies',
            'Import the module',
            'Initialize the component',
            'Execute core functionality'
        ])
        
        return '\n'.join(f'{i+1}. {step}' for i, step in enumerate(steps))
        
    def _format_features(self, features: List[str]) -> str:
        """Format feature list."""
        if not features:
            return '- No features specified'
        return '\n'.join(f'- {feature}' for feature in features)
        
    def _format_dependencies(self, dependencies: List[str]) -> str:
        """Format dependency list."""
        if not dependencies:
            return '- No external dependencies'
        return '\n'.join(f'- `{dep}`' for dep in dependencies)
        
    def _format_list(self, items: List[str]) -> str:
        """Format generic list."""
        if not items:
            return '- None specified'
        return '\n'.join(f'- {item}' for item in items)
        
    def _write_documentation(self, component_path: Path, docs: DocumentationSet) -> None:
        """Write documentation files to disk."""
        files = {
            'README.md': docs.readme,
            'context.md': docs.context,
            'architecture.md': docs.architecture,
            'implementation-guide.md': docs.implementation_guide,
            'test-strategy.md': docs.test_strategy,
            'research-notes.md': docs.research_notes
        }
        
        for filename, content in files.items():
            file_path = component_path / filename
            file_path.write_text(content, encoding='utf-8')
            logger.debug(f"Written {filename} to {file_path}")
            
    def validate_structure(self) -> bool:
        """
        Validate learning library folder structure.
        
        Returns:
            True if structure is valid
        """
        if not self.learning_base.exists():
            logger.error(f"Learning library base not found: {self.learning_base}")
            return False
            
        for category in self.categories:
            category_path = self.learning_base / category
            if not category_path.exists():
                logger.warning(f"Category folder missing: {category_path}")
                category_path.mkdir(parents=True, exist_ok=True)
                
        return True
        
    def list_documented_components(self, category: str = None) -> List[Dict[str, str]]:
        """
        List all documented components.
        
        Args:
            category: Optional category filter
            
        Returns:
            List of component info dicts
        """
        components = []
        
        categories = [category] if category else self.categories.keys()
        
        for cat in categories:
            category_path = self.learning_base / cat
            if not category_path.exists():
                continue
                
            for component_path in category_path.iterdir():
                if not component_path.is_dir():
                    continue
                    
                readme_path = component_path / 'README.md'
                if readme_path.exists():
                    components.append({
                        'name': component_path.name,
                        'category': cat,
                        'path': str(component_path)
                    })
                    
        return components
