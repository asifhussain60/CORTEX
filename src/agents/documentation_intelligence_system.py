#!/usr/bin/env python3
"""
Documentation Intelligence System

Compares actual implementation with existing documentation to identify gaps,
generate new content, and update cross-references automatically.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass, field
import logging

# Import the implementation data structures
from .implementation_discovery_engine import ImplementationData, CodeElement, APIEndpoint

logger = logging.getLogger(__name__)

@dataclass
class DocumentationGap:
    """Represents a gap between documentation and implementation"""
    gap_type: str  # 'missing_doc', 'outdated_doc', 'broken_link', 'incorrect_example'
    severity: str  # 'critical', 'high', 'medium', 'low'
    description: str
    affected_file: str
    suggested_fix: str
    code_element: Optional[str] = None  # Class/function that needs documenting

@dataclass
class DocumentationUpdate:
    """Represents an update to be made to documentation"""
    file_path: str
    update_type: str  # 'create', 'modify', 'delete'
    content: str
    section: Optional[str] = None  # Section within file to update
    reason: str = ""

@dataclass
class CrossReference:
    """Represents a cross-reference between documentation and code"""
    source_file: str
    target_file: str
    reference_type: str  # 'api_reference', 'code_example', 'class_link'
    line_number: int
    is_valid: bool = True

@dataclass
class DocumentationUpdates:
    """Complete documentation update plan"""
    feature_name: str
    update_timestamp: datetime
    
    # Gap analysis
    gaps_found: List[DocumentationGap] = field(default_factory=list)
    
    # Planned updates
    file_updates: List[DocumentationUpdate] = field(default_factory=list)
    
    # Cross-references  
    broken_references: List[CrossReference] = field(default_factory=list)
    new_references: List[CrossReference] = field(default_factory=list)
    
    # Generated content
    api_documentation: Dict[str, str] = field(default_factory=dict)  # endpoint -> doc
    class_documentation: Dict[str, str] = field(default_factory=dict)  # class -> doc
    example_code: List[str] = field(default_factory=list)
    
    # Metrics
    documentation_coverage_before: float = 0.0
    documentation_coverage_after: float = 0.0
    gaps_resolved: int = 0


class DocumentationGapAnalyzer:
    """Analyzes gaps between implementation and documentation"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        
    def analyze_gaps(self, implementation_data: ImplementationData) -> List[DocumentationGap]:
        """Find documentation gaps for the implemented feature"""
        gaps = []
        
        # Check for missing class documentation
        gaps.extend(self._check_class_documentation(implementation_data.new_classes))
        
        # Check for missing API documentation
        gaps.extend(self._check_api_documentation(implementation_data.new_endpoints))
        
        # Check for outdated documentation
        gaps.extend(self._check_outdated_documentation(implementation_data))
        
        # Check for broken links
        gaps.extend(self._check_broken_references())
        
        logger.info(f"Found {len(gaps)} documentation gaps")
        return gaps
    
    def _check_class_documentation(self, classes: List[CodeElement]) -> List[DocumentationGap]:
        """Check if new classes have proper documentation"""
        gaps = []
        
        for cls in classes:
            if not cls.docstring or len(cls.docstring.strip()) < 10:
                gap = DocumentationGap(
                    gap_type="missing_doc",
                    severity="high",
                    description=f"Class {cls.name} lacks documentation",
                    affected_file=cls.file_path,
                    suggested_fix=f"Add comprehensive docstring to class {cls.name}",
                    code_element=cls.name
                )
                gaps.append(gap)
                
        return gaps
    
    def _check_api_documentation(self, endpoints: List[APIEndpoint]) -> List[DocumentationGap]:
        """Check if new API endpoints have documentation"""
        gaps = []
        
        for endpoint in endpoints:
            # Check if endpoint is documented in API docs
            api_doc_exists = self._find_api_documentation(endpoint)
            
            if not api_doc_exists:
                gap = DocumentationGap(
                    gap_type="missing_doc",
                    severity="critical",
                    description=f"API endpoint {endpoint.method} {endpoint.path} is not documented",
                    affected_file=endpoint.file_path,
                    suggested_fix=f"Create API documentation for {endpoint.method} {endpoint.path}",
                    code_element=f"{endpoint.method} {endpoint.path}"
                )
                gaps.append(gap)
                
        return gaps
    
    def _find_api_documentation(self, endpoint: APIEndpoint) -> bool:
        """Check if an API endpoint is documented"""
        # Look for API documentation files
        api_doc_patterns = [
            '**/api.md',
            '**/API.md', 
            '**/api-reference.md',
            '**/swagger.yaml',
            '**/openapi.yaml'
        ]
        
        for pattern in api_doc_patterns:
            for doc_file in self.workspace_path.rglob(pattern):
                try:
                    with open(doc_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                    # Simple check for endpoint path in documentation
                    if endpoint.path in content:
                        return True
                        
                except Exception as e:
                    logger.warning(f"Failed to read doc file {doc_file}: {e}")
                    
        return False
    
    def _check_outdated_documentation(self, implementation_data: ImplementationData) -> List[DocumentationGap]:
        """Check for documentation that might be outdated"""
        gaps = []
        
        # Find all markdown files
        doc_files = list(self.workspace_path.rglob("*.md"))
        
        for doc_file in doc_files:
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Check for references to modified files
                for file_change in implementation_data.files_changed:
                    if file_change.change_type == 'modified':
                        file_name = Path(file_change.file_path).name
                        
                        if file_name in content:
                            gap = DocumentationGap(
                                gap_type="outdated_doc",
                                severity="medium",
                                description=f"Documentation in {doc_file.name} may be outdated due to changes in {file_name}",
                                affected_file=str(doc_file),
                                suggested_fix=f"Review and update documentation referencing {file_name}"
                            )
                            gaps.append(gap)
                            
            except Exception as e:
                logger.warning(f"Failed to analyze doc file {doc_file}: {e}")
                
        return gaps
    
    def _check_broken_references(self) -> List[DocumentationGap]:
        """Check for broken links in documentation"""
        gaps = []
        
        doc_files = list(self.workspace_path.rglob("*.md"))
        
        for doc_file in doc_files:
            try:
                with open(doc_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                # Find markdown links
                link_pattern = r'\[([^\]]+)\]\(([^)]+)\)'
                
                for match in re.finditer(link_pattern, content):
                    link_text = match.group(1)
                    link_path = match.group(2)
                    
                    # Skip external links
                    if link_path.startswith(('http://', 'https://', 'mailto:')):
                        continue
                        
                    # Check if referenced file exists
                    if link_path.startswith('#'):
                        # Internal anchor - would need more sophisticated check
                        continue
                        
                    referenced_file = self.workspace_path / link_path
                    if not referenced_file.exists():
                        gap = DocumentationGap(
                            gap_type="broken_link",
                            severity="medium", 
                            description=f"Broken link in {doc_file.name}: {link_text} -> {link_path}",
                            affected_file=str(doc_file),
                            suggested_fix=f"Fix or remove broken link to {link_path}"
                        )
                        gaps.append(gap)
                        
            except Exception as e:
                logger.warning(f"Failed to check links in {doc_file}: {e}")
                
        return gaps


class ContentGenerator:
    """Generates new documentation content based on implementation"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        
    def generate_api_documentation(self, endpoints: List[APIEndpoint]) -> Dict[str, str]:
        """Generate API documentation for new endpoints"""
        api_docs = {}
        
        for endpoint in endpoints:
            doc_content = self._generate_endpoint_doc(endpoint)
            key = f"{endpoint.method} {endpoint.path}"
            api_docs[key] = doc_content
            
        return api_docs
    
    def _generate_endpoint_doc(self, endpoint: APIEndpoint) -> str:
        """Generate documentation for a single API endpoint"""
        template = f"""### {endpoint.method} {endpoint.path}

**Description:** {self._infer_endpoint_description(endpoint)}

**Handler:** `{endpoint.handler_function}` in `{endpoint.file_path}`

**Parameters:**
{self._generate_parameter_docs(endpoint)}

**Response:**
```json
{{
  "status": "success",
  "data": {{}}
}}
```

**Example Request:**
```bash
curl -X {endpoint.method} "http://localhost:8000{endpoint.path}"
```

**Implementation Location:** Line {endpoint.line_number} in `{endpoint.file_path}`

---
"""
        return template
    
    def _infer_endpoint_description(self, endpoint: APIEndpoint) -> str:
        """Infer description from endpoint path and method"""
        path_parts = endpoint.path.strip('/').split('/')
        
        if endpoint.method == 'GET':
            if len(path_parts) == 1:
                return f"Retrieve {path_parts[0]} data"
            else:
                return f"Get {' '.join(path_parts).replace('_', ' ')}"
        elif endpoint.method == 'POST':
            return f"Create new {path_parts[0] if path_parts else 'resource'}"
        elif endpoint.method == 'PUT':
            return f"Update {path_parts[0] if path_parts else 'resource'}"
        elif endpoint.method == 'DELETE':
            return f"Delete {path_parts[0] if path_parts else 'resource'}"
        else:
            return f"Handle {endpoint.method} request for {endpoint.path}"
    
    def _generate_parameter_docs(self, endpoint: APIEndpoint) -> str:
        """Generate parameter documentation"""
        if endpoint.parameters:
            param_docs = []
            for param in endpoint.parameters:
                param_docs.append(f"- `{param}`: Description needed")
            return '\n'.join(param_docs)
        else:
            return "- None"
    
    def generate_class_documentation(self, classes: List[CodeElement]) -> Dict[str, str]:
        """Generate class documentation"""
        class_docs = {}
        
        for cls in classes:
            doc_content = self._generate_class_doc(cls)
            class_docs[cls.name] = doc_content
            
        return class_docs
    
    def _generate_class_doc(self, cls: CodeElement) -> str:
        """Generate documentation for a single class"""
        template = f"""## {cls.name}

**File:** `{cls.file_path}` (Line {cls.line_number})

**Description:** {cls.docstring if cls.docstring else 'Description needed'}

**Usage:**
```python
from {self._get_module_path(cls.file_path)} import {cls.name}

# Create instance
instance = {cls.name}()
```

**Methods:**
- Methods documentation needed (extracted from code analysis)

**Example:**
```python
# Example usage needed
```

---
"""
        return template
    
    def _get_module_path(self, file_path: str) -> str:
        """Convert file path to Python module path"""
        rel_path = Path(file_path).relative_to(self.workspace_path)
        module_parts = rel_path.with_suffix('').parts
        return '.'.join(module_parts)
    
    def generate_example_code(self, implementation_data: ImplementationData) -> List[str]:
        """Generate code examples for the feature"""
        examples = []
        
        # Generate API usage examples
        for endpoint in implementation_data.new_endpoints:
            example = self._generate_api_example(endpoint)
            examples.append(example)
            
        # Generate class usage examples
        for cls in implementation_data.new_classes:
            example = self._generate_class_example(cls)
            examples.append(example)
            
        return examples
    
    def _generate_api_example(self, endpoint: APIEndpoint) -> str:
        """Generate example for API endpoint usage"""
        return f"""
# Example: Using {endpoint.method} {endpoint.path}

```python
import requests

response = requests.{endpoint.method.lower()}(
    "http://localhost:8000{endpoint.path}"
)

if response.status_code == 200:
    data = response.json()
    print(data)
```
"""
    
    def _generate_class_example(self, cls: CodeElement) -> str:
        """Generate example for class usage"""
        return f"""
# Example: Using {cls.name}

```python
from {self._get_module_path(cls.file_path)} import {cls.name}

# Create and use instance
{cls.name.lower()} = {cls.name}()
# Add usage example here
```
"""


class CrossReferenceManager:
    """Manages cross-references between documentation and code"""
    
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        
    def update_cross_references(self, implementation_data: ImplementationData) -> Tuple[List[CrossReference], List[CrossReference]]:
        """Update cross-references, return (broken, new)"""
        broken_refs = []
        new_refs = []
        
        # Find documentation files
        doc_files = list(self.workspace_path.rglob("*.md"))
        
        for doc_file in doc_files:
            try:
                broken, new = self._process_doc_file(doc_file, implementation_data)
                broken_refs.extend(broken)
                new_refs.extend(new)
            except Exception as e:
                logger.warning(f"Failed to process cross-references in {doc_file}: {e}")
                
        return broken_refs, new_refs
    
    def _process_doc_file(self, doc_file: Path, implementation_data: ImplementationData) -> Tuple[List[CrossReference], List[CrossReference]]:
        """Process a single documentation file for cross-references"""
        broken_refs = []
        new_refs = []
        
        with open(doc_file, 'r', encoding='utf-8') as f:
            content = f.read()
            lines = content.split('\n')
            
        # Check existing references
        for line_num, line in enumerate(lines, 1):
            # Find file references
            file_refs = re.findall(r'`([^`]+\.(?:py|cs|js|ts))`', line)
            for file_ref in file_refs:
                ref_path = self.workspace_path / file_ref
                
                if not ref_path.exists():
                    broken_ref = CrossReference(
                        source_file=str(doc_file),
                        target_file=file_ref,
                        reference_type='file_link',
                        line_number=line_num,
                        is_valid=False
                    )
                    broken_refs.append(broken_ref)
                    
        # Generate new references for new code elements
        for cls in implementation_data.new_classes:
            new_ref = CrossReference(
                source_file=str(doc_file),
                target_file=cls.file_path,
                reference_type='class_link',
                line_number=0,  # Will be determined during insertion
                is_valid=True
            )
            new_refs.append(new_ref)
            
        return broken_refs, new_refs


class DocumentationIntelligenceSystem:
    """
    Main system that coordinates gap analysis, content generation,
    and cross-reference management to create comprehensive documentation updates.
    """
    
    def __init__(self, workspace_path: str):
        self.workspace_path = workspace_path
        self.gap_analyzer = DocumentationGapAnalyzer(workspace_path)
        self.content_generator = ContentGenerator(workspace_path)
        self.reference_manager = CrossReferenceManager(workspace_path)
        
    async def generate_documentation_updates(self, implementation_data: ImplementationData) -> DocumentationUpdates:
        """
        Main orchestration method that generates complete documentation updates
        for an implemented feature.
        """
        logger.info(f"Starting documentation intelligence for feature: {implementation_data.feature_name}")
        
        # Analyze documentation gaps
        gaps = self.gap_analyzer.analyze_gaps(implementation_data)
        
        # Generate new content
        api_docs = self.content_generator.generate_api_documentation(implementation_data.new_endpoints)
        class_docs = self.content_generator.generate_class_documentation(implementation_data.new_classes)
        examples = self.content_generator.generate_example_code(implementation_data)
        
        # Update cross-references
        broken_refs, new_refs = self.reference_manager.update_cross_references(implementation_data)
        
        # Create file updates
        file_updates = self._create_file_updates(gaps, api_docs, class_docs, examples)
        
        # Calculate coverage metrics
        coverage_before = self._calculate_documentation_coverage_before(implementation_data)
        coverage_after = self._calculate_documentation_coverage_after(gaps, file_updates)
        
        updates = DocumentationUpdates(
            feature_name=implementation_data.feature_name,
            update_timestamp=datetime.now(),
            gaps_found=gaps,
            file_updates=file_updates,
            broken_references=broken_refs,
            new_references=new_refs,
            api_documentation=api_docs,
            class_documentation=class_docs,
            example_code=examples,
            documentation_coverage_before=coverage_before,
            documentation_coverage_after=coverage_after,
            gaps_resolved=len([g for g in gaps if g.severity in ['critical', 'high']])
        )
        
        logger.info(f"Documentation intelligence complete for {implementation_data.feature_name}: "
                   f"{len(gaps)} gaps found, {len(file_updates)} files to update, "
                   f"coverage {coverage_before:.1f}% → {coverage_after:.1f}%")
        
        return updates
    
    def _create_file_updates(self, gaps: List[DocumentationGap], 
                           api_docs: Dict[str, str], class_docs: Dict[str, str],
                           examples: List[str]) -> List[DocumentationUpdate]:
        """Create file update plans based on gaps and generated content"""
        updates = []
        
        # Create API documentation file
        if api_docs:
            api_content = self._combine_api_docs(api_docs)
            updates.append(DocumentationUpdate(
                file_path="docs/api-reference.md",
                update_type="create",
                content=api_content,
                reason="Generated API documentation for new endpoints"
            ))
            
        # Create class documentation
        if class_docs:
            class_content = self._combine_class_docs(class_docs)
            updates.append(DocumentationUpdate(
                file_path="docs/class-reference.md", 
                update_type="create",
                content=class_content,
                reason="Generated class documentation for new classes"
            ))
            
        # Create examples documentation
        if examples:
            examples_content = '\n'.join(examples)
            updates.append(DocumentationUpdate(
                file_path="docs/examples.md",
                update_type="modify",
                content=examples_content,
                section="## New Examples",
                reason="Added code examples for new features"
            ))
            
        # Address critical gaps
        for gap in gaps:
            if gap.severity == "critical":
                update = DocumentationUpdate(
                    file_path=gap.affected_file,
                    update_type="modify",
                    content=f"# TODO: {gap.suggested_fix}",
                    reason=f"Address critical documentation gap: {gap.description}"
                )
                updates.append(update)
                
        return updates
    
    def _combine_api_docs(self, api_docs: Dict[str, str]) -> str:
        """Combine individual API docs into a single document"""
        header = f"""# API Reference

Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This document contains API documentation for newly implemented endpoints.

"""
        combined = header + '\n'.join(api_docs.values())
        return combined
    
    def _combine_class_docs(self, class_docs: Dict[str, str]) -> str:
        """Combine individual class docs into a single document"""
        header = f"""# Class Reference

Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

This document contains class documentation for newly implemented classes.

"""
        combined = header + '\n'.join(class_docs.values())
        return combined
    
    def _calculate_documentation_coverage_before(self, implementation_data: ImplementationData) -> float:
        """Calculate documentation coverage before updates"""
        total_elements = len(implementation_data.new_classes) + len(implementation_data.new_functions) + len(implementation_data.new_endpoints)
        
        if total_elements == 0:
            return 100.0
            
        documented_elements = 0
        
        # Count classes with docstrings
        for cls in implementation_data.new_classes:
            if cls.docstring and len(cls.docstring.strip()) > 10:
                documented_elements += 1
                
        # Count functions with docstrings
        for func in implementation_data.new_functions:
            if func.docstring and len(func.docstring.strip()) > 10:
                documented_elements += 1
                
        # API endpoints are rarely documented initially
        # documented_elements += 0 for endpoints
        
        return (documented_elements / total_elements) * 100
    
    def _calculate_documentation_coverage_after(self, gaps: List[DocumentationGap], 
                                              file_updates: List[DocumentationUpdate]) -> float:
        """Calculate estimated documentation coverage after updates"""
        # This is a simplified calculation
        # In reality, would need to analyze the actual content being created
        
        critical_gaps = len([g for g in gaps if g.severity == 'critical'])
        high_gaps = len([g for g in gaps if g.severity == 'high'])
        
        # Assume file updates will resolve most critical and high priority gaps
        coverage_improvement = min((critical_gaps * 20 + high_gaps * 10), 50)
        
        # Start with current coverage and add improvement
        base_coverage = 30  # Rough estimate for new code
        estimated_coverage = min(base_coverage + coverage_improvement, 95)
        
        return estimated_coverage


if __name__ == "__main__":
    # Test documentation intelligence
    import asyncio
    from .implementation_discovery_engine import ImplementationData, CodeElement, APIEndpoint
    
    async def test_documentation_intelligence():
        # Create test implementation data
        test_data = ImplementationData(
            feature_name="test_auth_feature",
            discovery_timestamp=datetime.now(),
            new_classes=[
                CodeElement(
                    name="AuthService",
                    element_type="class",
                    file_path="src/auth/auth_service.py",
                    line_number=10,
                    docstring="Service for handling authentication"
                )
            ],
            new_endpoints=[
                APIEndpoint(
                    path="/auth/login",
                    method="POST", 
                    handler_function="login",
                    file_path="src/auth/routes.py",
                    line_number=25
                )
            ]
        )
        
        system = DocumentationIntelligenceSystem("/Users/asifhussain/PROJECTS/CORTEX")
        updates = await system.generate_documentation_updates(test_data)
        
        print(f"Documentation Intelligence Results for {updates.feature_name}:")
        print(f"- Gaps found: {len(updates.gaps_found)}")
        print(f"- File updates: {len(updates.file_updates)}")
        print(f"- API docs generated: {len(updates.api_documentation)}")
        print(f"- Class docs generated: {len(updates.class_documentation)}")
        print(f"- Coverage: {updates.documentation_coverage_before:.1f}% → {updates.documentation_coverage_after:.1f}%")
        print(f"- Gaps resolved: {updates.gaps_resolved}")
    
    asyncio.run(test_documentation_intelligence())