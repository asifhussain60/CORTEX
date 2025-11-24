"""
Documentation Generator Stage

Generates or updates documentation based on implementation.

Author: CORTEX Development Team
Date: 2025-11-08
"""

from typing import Dict, Any, List
from datetime import datetime
from workflows.workflow_engine import (
    BaseWorkflowStage,
    WorkflowState,
    StageResult,
    StageStatus
)


class DocGenerator(BaseWorkflowStage):
    """
    Stage that generates documentation
    
    Input Requirements:
        - state.stage_outputs['implement']: Implementation details
        - state.user_request: Original request
        
    Output:
        - documentation_files: List of documentation files created/updated
        - doc_sections: Sections added to documentation
        - doc_summary: Summary of documentation changes
    """
    
    def __init__(self):
        super().__init__("doc_generator")
    
    def execute(self, state: WorkflowState) -> StageResult:
        """Generate documentation"""
        # Gather information
        user_request = state.user_request
        dod_output = state.get_stage_output("clarify")
        implement_output = state.get_stage_output("implement")
        
        # Generate documentation sections
        doc_sections = self._generate_sections(
            user_request,
            dod_output,
            implement_output,
            state.context
        )
        
        # Determine documentation files
        doc_files = self._determine_doc_files(
            implement_output,
            state.context
        )
        
        # Generate summary
        summary = self._generate_summary(doc_files, doc_sections)
        
        output = {
            "documentation_files": doc_files,
            "doc_sections": doc_sections,
            "doc_summary": summary
        }
        
        return StageResult(
            stage_id=self.stage_id,
            status=StageStatus.SUCCESS,
            duration_ms=0,
            output=output
        )
    
    def validate_input(self, state: WorkflowState) -> bool:
        """Validate required inputs available"""
        return bool(state.user_request)
    
    def _generate_sections(
        self,
        user_request: str,
        dod_output: Dict[str, Any],
        implement_output: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[Dict[str, str]]:
        """Generate documentation sections"""
        sections = []
        
        # Overview section
        sections.append({
            "title": "Overview",
            "content": self._generate_overview(user_request)
        })
        
        # Feature description
        sections.append({
            "title": "Feature Description",
            "content": user_request
        })
        
        # Implementation details
        if implement_output:
            sections.append({
                "title": "Implementation",
                "content": self._generate_implementation_doc(implement_output)
            })
        
        # API documentation (if applicable)
        if self._has_api_changes(user_request, implement_output):
            sections.append({
                "title": "API Changes",
                "content": self._generate_api_doc(implement_output)
            })
        
        # Configuration (if applicable)
        if self._has_config_changes(user_request, implement_output):
            sections.append({
                "title": "Configuration",
                "content": self._generate_config_doc(implement_output)
            })
        
        # Usage examples
        sections.append({
            "title": "Usage Examples",
            "content": self._generate_usage_examples(user_request, implement_output)
        })
        
        # Testing
        sections.append({
            "title": "Testing",
            "content": self._generate_testing_doc(dod_output)
        })
        
        # Changelog entry
        sections.append({
            "title": "Changelog Entry",
            "content": self._generate_changelog_entry(user_request)
        })
        
        return sections
    
    def _generate_overview(self, user_request: str) -> str:
        """Generate overview section"""
        return f"""
This feature implements: {user_request}

**Date:** {datetime.now().strftime('%Y-%m-%d')}
**Status:** Implemented
"""
    
    def _generate_implementation_doc(self, implement_output: Dict[str, Any]) -> str:
        """Generate implementation documentation"""
        if not implement_output:
            return "Implementation details not available"
        
        doc = "**Files Modified:**\n"
        
        if "files" in implement_output:
            for file in implement_output["files"]:
                doc += f"- `{file}`\n"
        
        if "classes" in implement_output:
            doc += "\n**Classes Added/Modified:**\n"
            for cls in implement_output["classes"]:
                doc += f"- `{cls}`\n"
        
        if "methods" in implement_output:
            doc += "\n**Methods Added/Modified:**\n"
            for method in implement_output["methods"]:
                doc += f"- `{method}`\n"
        
        return doc
    
    def _generate_api_doc(self, implement_output: Dict[str, Any]) -> str:
        """Generate API documentation"""
        return """
**New Endpoints:**

```
GET /api/feature
POST /api/feature
PUT /api/feature/{id}
DELETE /api/feature/{id}
```

**Request/Response Examples:**

See API specification for details.
"""
    
    def _generate_config_doc(self, implement_output: Dict[str, Any]) -> str:
        """Generate configuration documentation"""
        return """
**Configuration Options:**

```json
{
  "feature.enabled": true,
  "feature.timeout": 30
}
```
"""
    
    def _generate_usage_examples(
        self,
        user_request: str,
        implement_output: Dict[str, Any]
    ) -> str:
        """Generate usage examples"""
        return f"""
**Example 1: Basic Usage**

```python
# Example code demonstrating {user_request}
result = feature_function()
print(result)
```

**Example 2: Advanced Usage**

```python
# Advanced example with configuration
result = feature_function(config={{"option": "value"}})
```
"""
    
    def _generate_testing_doc(self, dod_output: Dict[str, Any]) -> str:
        """Generate testing documentation"""
        doc = "**Test Coverage:**\n\n"
        
        if dod_output and "acceptance_criteria" in dod_output:
            doc += "**Acceptance Criteria:**\n"
            for criterion in dod_output["acceptance_criteria"]:
                doc += f"- [ ] {criterion}\n"
        
        doc += "\n**Running Tests:**\n\n"
        doc += "```bash\npytest tests/\n```\n"
        
        return doc
    
    def _generate_changelog_entry(self, user_request: str) -> str:
        """Generate changelog entry"""
        date = datetime.now().strftime('%Y-%m-%d')
        return f"""
## [{date}]

### Added
- {user_request}

### Changed
- Updated documentation

### Fixed
- N/A
"""
    
    def _determine_doc_files(
        self,
        implement_output: Dict[str, Any],
        context: Dict[str, Any]
    ) -> List[str]:
        """Determine which documentation files to create/update"""
        files = [
            "README.md",
            "CHANGELOG.md"
        ]
        
        # Add API docs if applicable
        if implement_output and "api" in str(implement_output).lower():
            files.append("docs/api/README.md")
        
        # Add feature-specific docs
        files.append("docs/features/new-feature.md")
        
        return files
    
    def _generate_summary(
        self,
        doc_files: List[str],
        doc_sections: List[Dict[str, str]]
    ) -> str:
        """Generate documentation summary"""
        summary = f"Generated {len(doc_sections)} documentation section(s)\n"
        summary += f"Updated {len(doc_files)} documentation file(s):\n"
        
        for file in doc_files:
            summary += f"  - {file}\n"
        
        return summary.strip()
    
    def _has_api_changes(
        self,
        user_request: str,
        implement_output: Dict[str, Any]
    ) -> bool:
        """Check if there are API changes"""
        api_keywords = ["api", "endpoint", "route", "rest"]
        return any(kw in user_request.lower() for kw in api_keywords)
    
    def _has_config_changes(
        self,
        user_request: str,
        implement_output: Dict[str, Any]
    ) -> bool:
        """Check if there are configuration changes"""
        config_keywords = ["config", "setting", "option", "parameter"]
        return any(kw in user_request.lower() for kw in config_keywords)


__all__ = ["DocGenerator"]
