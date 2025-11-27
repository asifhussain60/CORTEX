"""
Documentation Generator - Auto-generate documentation templates for undocumented features

Generates:
- Module documentation (.md files)
- API reference sections
- Usage examples
- Integration guides

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import ast
import re
from pathlib import Path
from typing import Dict, List, Optional


class DocumentationGenerator:
    """Generates documentation templates for undocumented features"""
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.modules_dir = self.project_root / ".github" / "prompts" / "modules"
    
    def generate_documentation_template(self, feature_name: str, feature_path: str,
                                       docstring: Optional[str] = None,
                                       methods: Optional[List[str]] = None) -> Dict[str, str]:
        """
        Generate documentation template for a feature
        
        Args:
            feature_name: Name of orchestrator/agent (e.g., "PaymentOrchestrator")
            feature_path: Path to feature file
            docstring: Feature's docstring (optional)
            methods: List of public methods (optional, will extract if not provided)
        
        Returns:
            Dictionary with keys: doc_content, doc_path, section_title
        """
        # Extract methods if not provided
        if methods is None:
            methods = self._extract_public_methods(feature_path)
        
        # Determine documentation path
        doc_path = self._determine_doc_path(feature_name)
        
        # Extract purpose from docstring
        purpose = self._extract_purpose(docstring) if docstring else f"{feature_name} operations"
        
        # Generate documentation content
        doc_content = self._generate_module_documentation(feature_name, purpose, methods)
        
        # Generate section title for CORTEX.prompt.md
        section_title = self._generate_section_title(feature_name)
        
        return {
            "doc_content": doc_content,
            "doc_path": str(doc_path),
            "section_title": section_title,
            "feature_name": feature_name,
            "purpose": purpose
        }
    
    def _extract_public_methods(self, feature_path: str) -> List[Dict[str, str]]:
        """Extract public methods with docstrings using AST"""
        try:
            file_path = self.project_root / feature_path
            if not file_path.exists():
                return []
            
            with open(file_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            methods = []
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    for item in node.body:
                        if isinstance(item, ast.FunctionDef):
                            # Skip private methods
                            if not item.name.startswith('_'):
                                docstring = ast.get_docstring(item) or "No description available"
                                methods.append({
                                    "name": item.name,
                                    "docstring": docstring.split('\n')[0]  # First line only
                                })
            
            return methods
        
        except Exception:
            return []
    
    def _extract_purpose(self, docstring: str) -> str:
        """Extract first sentence from docstring"""
        if not docstring:
            return "Feature operations"
        
        lines = [line.strip() for line in docstring.split('\n') if line.strip()]
        if not lines:
            return "Feature operations"
        
        first_line = lines[0].strip('"\'')
        match = re.match(r'^([^.!?]+[.!?])', first_line)
        if match:
            return match.group(1).strip()
        
        return first_line[:100]
    
    def _determine_doc_path(self, feature_name: str) -> Path:
        """Determine where documentation file should be created"""
        # Convert PaymentOrchestrator -> payment-orchestrator-guide.md
        filename = self._to_kebab_case(feature_name) + "-guide.md"
        return self.modules_dir / filename
    
    def _to_kebab_case(self, name: str) -> str:
        """Convert PascalCase to kebab-case"""
        # Insert hyphen before uppercase letters
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1-\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1-\2', s1).lower()
    
    def _generate_section_title(self, feature_name: str) -> str:
        """Generate section title (remove Orchestrator/Agent suffix)"""
        return re.sub(r'(Orchestrator|Agent)$', '', feature_name)
    
    def _generate_module_documentation(self, feature_name: str, purpose: str,
                                      methods: List[Dict[str, str]]) -> str:
        """Generate complete module documentation"""
        section_title = self._generate_section_title(feature_name)
        
        doc = f"""# {section_title} Guide

**Purpose:** {purpose}

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Source-Available (Use Allowed, No Contributions)

---

## Overview

{purpose}

**Key Features:**
- [Feature 1]
- [Feature 2]
- [Feature 3]

---

## Usage

### Basic Usage

```python
from {self._get_import_path(feature_name)} import {feature_name}

# Initialize
orchestrator = {feature_name}()

# Execute
result = orchestrator.execute()
```

### Natural Language Commands

**Commands:**
- `[command 1]` - [Description]
- `[command 2]` - [Description]

**Examples:**
```
User: "[example command]"
CORTEX: [Expected response]
```

---

## API Reference

### Class: `{feature_name}`

{purpose}

"""
        # Add method documentation
        if methods:
            doc += "#### Methods\n\n"
            for method in methods:
                # Handle both dict and string methods
                if isinstance(method, dict):
                    method_name = method.get('name', 'unknown')
                    method_doc = method.get('docstring', 'No description available')
                else:
                    method_name = str(method)
                    method_doc = 'No description available'
                
                doc += f"**`{method_name}()`**\n\n"
                doc += f"{method_doc}\n\n"
                doc += "**Parameters:**\n- [param]: [description]\n\n"
                doc += "**Returns:**\n- [return type]: [description]\n\n"
                doc += "---\n\n"
        
        doc += """## Configuration

**Required:**
- [Configuration item 1]
- [Configuration item 2]

**Optional:**
- [Configuration item 3]

---

## Examples

### Example 1: [Scenario Name]

```python
# [Example code]
```

**Output:**
```
[Expected output]
```

---

## Integration

**Entry Points:**
- [Entry point 1]
- [Entry point 2]

**Dependencies:**
- [Dependency 1]
- [Dependency 2]

**See Also:**
- [Related documentation]

---

## Troubleshooting

**Issue:** [Common problem]  
**Solution:** [How to fix]

**Issue:** [Another problem]  
**Solution:** [How to fix]

---

**Last Updated:** [Date]  
**Version:** 1.0
"""
        return doc
    
    def _get_import_path(self, feature_name: str) -> str:
        """Generate likely import path for a feature"""
        # Common patterns
        if "Orchestrator" in feature_name:
            return "src.operations.orchestrators"
        elif "Agent" in feature_name:
            return "src.agents"
        else:
            return "src"
    
    def generate_batch_documentation(self, undocumented_features: List[Dict[str, any]]) -> List[Dict[str, str]]:
        """
        Generate documentation templates for multiple undocumented features
        
        Args:
            undocumented_features: List of dicts with keys: name, path, docstring, methods
        
        Returns:
            List of documentation templates (one per feature)
        """
        docs = []
        
        for feature in undocumented_features:
            doc = self.generate_documentation_template(
                feature_name=feature.get("name", "Unknown"),
                feature_path=feature.get("path", ""),
                docstring=feature.get("docstring"),
                methods=feature.get("methods")
            )
            docs.append(doc)
        
        return docs
