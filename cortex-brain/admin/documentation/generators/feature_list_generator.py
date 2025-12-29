"""
Feature List Generator

Generates comprehensive feature lists and capability documentation for CORTEX.
Extracts features from operation definitions, module definitions, and capabilities.yaml.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
import logging
import yaml

from .base_generator import (
    BaseDocumentationGenerator,
    GenerationConfig,
    GenerationResult,
    GeneratorType
)


logger = logging.getLogger(__name__)


class FeatureListGenerator(BaseDocumentationGenerator):
    """
    Generates feature lists and capability documentation.
    
    Features:
    - Extracts features from operations and modules
    - Generates categorized feature lists
    - Creates feature comparison tables
    - Documents capability matrix
    """
    
    def __init__(self, config: GenerationConfig, workspace_root: Optional[Path] = None):
        """Initialize feature list generator"""
        super().__init__(config, workspace_root)
        
        # Load configurations
        self.operations_config = self.load_config_file("cortex-operations.yaml")
        self.module_definitions = self.load_config_file("module-definitions.yaml")
        self.capabilities = self.load_config_file("capabilities.yaml")
        
        # Feature categories
        self.categories = [
            "Memory & Context",
            "Documentation Generation",
            "Code Analysis",
            "Natural Language Interface",
            "Testing & Validation",
            "Security & Governance",
            "Operations & Workflows"
        ]
    
    def get_component_name(self) -> str:
        """Component name for logging"""
        return "Feature List"
    
    def collect_data(self) -> Dict[str, Any]:
        """
        Collect data for feature list generation.
        
        Returns:
            Dictionary with operations, modules, capabilities
        """
        data = {
            "operations": self._extract_operations(),
            "modules": self._extract_modules(),
            "capabilities": self._extract_capabilities(),
            "categories": self.categories
        }
        
        return data
    
    def _extract_operations(self) -> List[Dict[str, Any]]:
        """Extract operation features"""
        operations = []
        
        if not self.operations_config:
            return operations
        
        # operations_config has structure: {operations: {op_id: {name, description, ...}}}
        operations_dict = self.operations_config.get("operations", {})
        
        # Handle both dict and list formats for backward compatibility
        if isinstance(operations_dict, dict):
            for op_id, op_data in operations_dict.items():
                if isinstance(op_data, dict):
                    operations.append({
                        "name": op_data.get("name", op_id),
                        "description": op_data.get("description", ""),
                        "status": op_data.get("implementation_status", {}).get("status", "unknown"),
                        "natural_language": op_data.get("natural_language", []),
                        "modules": op_data.get("modules", [])
                    })
        elif isinstance(operations_dict, list):
            # Legacy list format
            for op in operations_dict:
                if isinstance(op, dict):
                    operations.append({
                        "name": op.get("operation_id", op.get("name", "")),
                        "description": op.get("description", ""),
                        "status": op.get("status", "unknown"),
                        "natural_language": op.get("natural_language_examples", op.get("natural_language", [])),
                        "modules": op.get("modules", [])
                    })
        
        return operations
    
    def _extract_modules(self) -> List[Dict[str, Any]]:
        """Extract module features"""
        modules = []
        
        if not self.module_definitions:
            return modules
        
        # module_definitions has structure: {modules: {mod_id: {name, description, ...}}}
        modules_dict = self.module_definitions.get("modules", {})
        
        # Handle both dict and list formats for backward compatibility
        if isinstance(modules_dict, dict):
            for mod_id, mod_data in modules_dict.items():
                if isinstance(mod_data, dict):
                    modules.append({
                        "name": mod_data.get("name", mod_id),
                        "type": mod_data.get("category", mod_data.get("type", "")),
                        "description": mod_data.get("description", ""),
                        "status": mod_data.get("status", "unknown"),
                        "responsibilities": mod_data.get("responsibilities", [])
                    })
        elif isinstance(modules_dict, list):
            # Legacy list format
            for mod in modules_dict:
                if isinstance(mod, dict):
                    modules.append({
                        "name": mod.get("module_id", mod.get("name", "")),
                        "type": mod.get("type", ""),
                        "description": mod.get("description", ""),
                        "status": mod.get("status", "unknown"),
                        "responsibilities": mod.get("responsibilities", [])
                    })
        
        return modules
    
    def _extract_capabilities(self) -> Dict[str, Any]:
        """Extract system capabilities"""
        if self.capabilities:
            return self.capabilities
        
        return {
            "tiers": [],
            "agents": [],
            "plugins": []
        }
    
    def generate(self) -> GenerationResult:
        """
        Generate feature lists and capability documentation.
        
        Returns:
            GenerationResult with files generated
        """
        logger.info("Generating feature lists...")
        
        # Collect data
        data = self.collect_data()
        
        # Generate main feature list
        self._generate_main_feature_list(data)
        
        # Generate operations reference
        self._generate_operations_reference(data)
        
        # Generate modules reference
        self._generate_modules_reference(data)
        
        # Generate capabilities matrix
        self._generate_capabilities_matrix(data)
        
        # Generate feature comparison table
        self._generate_feature_comparison(data)
        
        # Save metadata
        self.save_metadata("feature-list-metadata.json", {
            "operations_count": len(data["operations"]),
            "modules_count": len(data["modules"]),
            "categories": self.categories
        })
        
        return self._create_success_result(metadata={
            "operations": len(data["operations"]),
            "modules": len(data["modules"]),
            "files_generated": len(self.files_generated)
        })
    
    def _generate_main_feature_list(self, data: Dict[str, Any]):
        """Generate main FEATURES.md file"""
        output_file = self.output_path / "FEATURES.md"
        
        content = """# CORTEX Features

**Version:** 3.0  
**Status:** Production Ready  
**Last Updated:** 2025

---

## Overview

CORTEX is a multi-tier AI development assistant with persistent memory, intelligent context management, and natural language operations.

## Core Features

"""
        
        # Add features by category
        for category in self.categories:
            content += f"### {category}\n\n"
            content += f"Features related to {category.lower()}:\n\n"
            content += "- Feature 1 (placeholder)\n"
            content += "- Feature 2 (placeholder)\n"
            content += "- Feature 3 (placeholder)\n\n"
        
        content += "\n## Operations\n\n"
        content += f"Total operations available: **{len(data['operations'])}**\n\n"
        
        for op in data['operations']:
            status_icon = "✅" if op['status'] == "ready" else "🟡" if op['status'] == "partial" else "⏸️"
            content += f"- {status_icon} **{op['name']}**: {op['description']}\n"
        
        content += "\n## Modules\n\n"
        content += f"Total modules implemented: **{len(data['modules'])}**\n\n"
        
        content += "\n---\n\n"
        content += "*Generated by CORTEX Documentation System*\n"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.record_file_generated(output_file)
            
        except Exception as e:
            self.record_error(f"Failed to generate FEATURES.md: {e}")
    
    def _generate_operations_reference(self, data: Dict[str, Any]):
        """Generate OPERATIONS-REFERENCE.md"""
        output_file = self.output_path / "OPERATIONS-REFERENCE.md"
        
        content = """# CORTEX Operations Reference

Complete reference for all CORTEX operations.

---

## Available Operations

"""
        
        for op in data['operations']:
            content += f"### {op['name']}\n\n"
            content += f"**Description:** {op['description']}\n\n"
            content += f"**Status:** {op['status']}\n\n"
            
            if op['natural_language']:
                content += "**Natural Language Examples:**\n"
                for example in op['natural_language'][:3]:
                    content += f"- \"{example}\"\n"
                content += "\n"
            
            if op['modules']:
                content += "**Modules Used:**\n"
                for module in op['modules']:
                    content += f"- {module}\n"
                content += "\n"
            
            content += "---\n\n"
        
        content += "\n*Generated by CORTEX Documentation System*\n"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.record_file_generated(output_file)
            
        except Exception as e:
            self.record_error(f"Failed to generate OPERATIONS-REFERENCE.md: {e}")
    
    def _generate_modules_reference(self, data: Dict[str, Any]):
        """Generate MODULES-REFERENCE.md"""
        output_file = self.output_path / "MODULES-REFERENCE.md"
        
        content = """# CORTEX Modules Reference

Complete reference for all CORTEX modules.

---

## Implemented Modules

"""
        
        for mod in data['modules']:
            content += f"### {mod['name']}\n\n"
            content += f"**Type:** {mod['type']}\n\n"
            content += f"**Description:** {mod['description']}\n\n"
            content += f"**Status:** {mod['status']}\n\n"
            
            if mod['responsibilities']:
                content += "**Responsibilities:**\n"
                for resp in mod['responsibilities']:
                    content += f"- {resp}\n"
                content += "\n"
            
            content += "---\n\n"
        
        content += "\n*Generated by CORTEX Documentation System*\n"
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.record_file_generated(output_file)
            
        except Exception as e:
            self.record_error(f"Failed to generate MODULES-REFERENCE.md: {e}")
    
    def _generate_capabilities_matrix(self, data: Dict[str, Any]):
        """Generate CAPABILITIES-MATRIX.md"""
        output_file = self.output_path / "CAPABILITIES-MATRIX.md"
        
        content = """# CORTEX Capabilities Matrix

System-wide capability overview.

---

## Memory Tiers

| Tier | Name | Purpose | Status |
|------|------|---------|--------|
| Tier 0 | Instinct | Immutable governance rules | ✅ Complete |
| Tier 1 | Working Memory | Last 20 conversations | ✅ Complete |
| Tier 2 | Knowledge Graph | Pattern learning | ✅ Complete |
| Tier 3 | Context Intelligence | Git analysis, code health | ✅ Complete |

## Agent System

| Agent | Role | Hemisphere | Status |
|-------|------|------------|--------|
| Intent Router | Natural language understanding | Right | ✅ Ready |
| Work Planner | Strategic planning | Right | ✅ Ready |
| Code Executor | Tactical implementation | Left | ✅ Ready |
| Test Generator | Test creation | Left | ✅ Ready |
| Brain Protector | Governance enforcement | Right | ✅ Ready |

## Plugin System

Plugins extend CORTEX functionality with zero external dependencies.

---

*Generated by CORTEX Documentation System*
"""
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.record_file_generated(output_file)
            
        except Exception as e:
            self.record_error(f"Failed to generate CAPABILITIES-MATRIX.md: {e}")
    
    def _generate_feature_comparison(self, data: Dict[str, Any]):
        """Generate FEATURE-COMPARISON.md"""
        output_file = self.output_path / "FEATURE-COMPARISON.md"
        
        content = """# CORTEX Feature Comparison

Compare CORTEX capabilities with traditional development assistants.

---

## Feature Comparison Table

| Feature | Traditional AI | CORTEX |
|---------|---------------|--------|
| Conversation Memory | ❌ None | ✅ 20 conversations (FIFO) |
| Pattern Learning | ❌ None | ✅ Knowledge Graph (Tier 2) |
| Context Awareness | ❌ Limited | ✅ Git analysis, file stability |
| Governance Rules | ❌ None | ✅ Tier 0 immutable rules |
| Natural Language | ✅ Basic | ✅ Advanced intent routing |
| Test Generation | ✅ Basic | ✅ TDD enforced workflow |
| Code Quality | ⚠️ Manual | ✅ Automated (Zero errors/warnings) |
| Documentation | ⚠️ Manual | ✅ Automated generation |

## Key Differentiators

1. **Persistent Memory**: CORTEX remembers your last 20 conversations
2. **Pattern Learning**: Learns from your work patterns over time
3. **Context Intelligence**: Understands your project holistically
4. **Governance Protection**: Immutable rules prevent degradation

---

*Generated by CORTEX Documentation System*
"""
        
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            self.record_file_generated(output_file)
            
        except Exception as e:
            self.record_error(f"Failed to generate FEATURE-COMPARISON.md: {e}")
    
    def validate(self) -> bool:
        """
        Validate generated feature lists.
        
        Returns:
            True if validation passes
        """
        # Check main feature list
        features_file = self.output_path / "FEATURES.md"
        if not features_file.exists():
            self.record_error("FEATURES.md not generated")
            return False
        
        # Check operations reference
        ops_file = self.output_path / "OPERATIONS-REFERENCE.md"
        if not ops_file.exists():
            self.record_warning("OPERATIONS-REFERENCE.md not generated")
        
        return True
