"""
Feature Auto-Registrar for CORTEX Align Orchestrator v2.0

This module automatically discovers and registers new features in cortex-operations.yaml.
Extracts metadata from Python files and generates properly formatted YAML entries.

Author: Asif Hussain
Date: December 3, 2025
Version: 1.0.0
"""

import ast
import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class OperationMetadata:
    """Metadata extracted from an operation file."""
    name: str
    display_name: str
    description: str
    deployment_tier: str  # user_facing, dual_context, admin_only
    natural_language: List[str] = field(default_factory=list)
    category: str = "general"
    modules: List[str] = field(default_factory=list)
    examples: List[str] = field(default_factory=list)
    version: str = "1.0.0"
    author: str = "Asif Hussain"


@dataclass
class RegistrationResult:
    """Result from feature registration."""
    success: bool
    operation_name: str = ""
    yaml_entry: str = ""
    dry_run: bool = False
    error_message: str = ""
    file_path: Optional[Path] = None


class FeatureAutoRegistrar:
    """Automatically registers discovered features in cortex-operations.yaml."""
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize the auto-registrar.
        
        Args:
            project_root: Path to CORTEX project root. If None, auto-detects.
        """
        self.project_root = project_root or self._detect_project_root()
        self.operations_dir = self.project_root / "src" / "operations"
        self.orchestrators_dir = self.project_root / "src" / "orchestrators"
        self.workflows_dir = self.project_root / "src" / "workflows"
        self.agents_dir = self.project_root / "src" / "cortex_agents"
        self.modules_dir = self.operations_dir / "modules"
        self.operations_yaml = self.project_root / "cortex-operations.yaml"
        
        # Security agents directory (src/agents/security/)
        self.security_agents_dir = self.project_root / "src" / "agents" / "security"
    
    def _detect_project_root(self) -> Path:
        """Auto-detect CORTEX project root."""
        current = Path.cwd()
        
        if (current / "cortex-operations.yaml").exists():
            return current
        
        for parent in current.parents:
            if (parent / "cortex-operations.yaml").exists():
                return parent
        
        raise FileNotFoundError("Cannot detect CORTEX project root")
    
    def extract_module_docstring(self, content: str) -> str:
        """
        Extract module-level docstring from Python file.
        
        Args:
            content: Python file content
        
        Returns:
            Module docstring or empty string
        """
        try:
            tree = ast.parse(content)
            docstring = ast.get_docstring(tree)
            return docstring if docstring else ""
        except Exception as e:
            logger.warning(f"Failed to parse docstring: {e}")
            return ""
    
    def extract_natural_language_triggers(self, content: str, docstring: str) -> List[str]:
        """
        Extract natural language triggers from file content and docstring.
        
        Looks for:
        - Patterns like: "plan feature", "start tdd", "commit and push"
        - Command strings in comments
        - Usage examples in docstrings
        
        Args:
            content: Python file content
            docstring: Module docstring
        
        Returns:
            List of natural language trigger phrases
        """
        triggers = []
        
        # Pattern 1: Look for quoted command strings
        quoted_pattern = r'["\']([a-z][a-z\s]{2,40})["\']'
        matches = re.findall(quoted_pattern, content.lower())
        
        for match in matches:
            # Filter for command-like phrases (verb + noun pattern)
            if any(verb in match for verb in ['plan', 'start', 'run', 'create', 'show', 
                                                'generate', 'deploy', 'commit', 'review',
                                                'analyze', 'check', 'validate', 'update']):
                if match not in triggers:
                    triggers.append(match)
        
        # Pattern 2: Look in docstring for usage examples
        if docstring:
            # Look for lines with commands in backticks
            backtick_pattern = r'`([a-z][a-z\s]{2,40})`'
            doc_matches = re.findall(backtick_pattern, docstring.lower())
            
            for match in doc_matches:
                if match not in triggers and len(match.split()) <= 5:
                    triggers.append(match)
        
        # Pattern 3: Look for "Commands:" or "Quick commands:" sections
        command_section_pattern = r'(?:commands?|triggers?):\s*\n((?:[-*]\s*.+\n?)+)'
        sections = re.findall(command_section_pattern, docstring.lower() if docstring else "", re.MULTILINE)
        
        for section in sections:
            lines = section.strip().split('\n')
            for line in lines:
                # Extract command after bullet point
                cmd = re.sub(r'^[-*]\s*', '', line).strip()
                if cmd and cmd not in triggers:
                    triggers.append(cmd)
        
        # Return top 5 most relevant triggers
        return triggers[:5] if triggers else ["operation name"]
    
    def infer_deployment_tier(self, file_path: Path, content: str) -> str:
        """
        Infer deployment tier from file location and content.
        
        Args:
            file_path: Path to the operation file
            content: File content
        
        Returns:
            'user_facing', 'dual_context', or 'admin_only'
        """
        # Check if in admin directory
        if 'admin' in str(file_path).lower():
            return 'admin_only'
        
        # Check for admin-related keywords
        admin_keywords = ['deploy', 'generate docs', 'alignment', 'cleanup', 'admin']
        if any(keyword in content.lower() for keyword in admin_keywords):
            return 'admin_only'
        
        # Check for dual-context operations
        dual_keywords = ['ado', 'azure devops', 'architecture', 'review']
        if any(keyword in content.lower() for keyword in dual_keywords):
            return 'dual_context'
        
        # Default to user-facing
        return 'user_facing'
    
    def infer_category(self, file_path: Path) -> str:
        """
        Infer operation category from file path and name.
        
        Args:
            file_path: Path to the operation file
        
        Returns:
            Category name
        """
        name = file_path.stem.lower()
        
        category_keywords = {
            'planning': ['plan', 'planning', 'feature'],
            'development': ['tdd', 'test', 'debug', 'develop'],
            'git': ['commit', 'checkpoint', 'rollback', 'git'],
            'review': ['review', 'pr', 'code review'],
            'analysis': ['analyze', 'health', 'rca', 'lint'],
            'deployment': ['deploy', 'release'],
            'maintenance': ['cleanup', 'optimize', 'align'],
            'setup': ['setup', 'onboard', 'install'],
            'documentation': ['docs', 'documentation', 'generate'],
            'reporting': ['report', 'dashboard', 'metrics'],
        }
        
        for category, keywords in category_keywords.items():
            if any(keyword in name for keyword in keywords):
                return category
        
        return 'general'
    
    def extract_usage_examples(self, docstring: str) -> List[str]:
        """
        Extract usage examples from docstring.
        
        Args:
            docstring: Module docstring
        
        Returns:
            List of usage examples
        """
        if not docstring:
            return []
        
        examples = []
        
        # Look for "Example:" or "Examples:" sections
        example_pattern = r'(?:example|usage|quick start)s?:\s*\n((?:(?:[-*]|\d+\.)\s*.+\n?)+)'
        sections = re.findall(example_pattern, docstring.lower(), re.MULTILINE | re.IGNORECASE)
        
        for section in sections:
            lines = section.strip().split('\n')
            for line in lines[:3]:  # Limit to first 3 examples
                # Clean up example text
                example = re.sub(r'^(?:[-*]|\d+\.)\s*', '', line).strip()
                if example and len(example) < 100:
                    examples.append(example)
        
        return examples
    
    def find_related_modules(self, operation_name: str) -> List[str]:
        """
        Find modules related to an operation.
        
        Args:
            operation_name: Name of the operation
        
        Returns:
            List of module names/paths
        """
        modules = []
        
        # Look for matching utility in modules directory
        for category_dir in self.modules_dir.iterdir():
            if not category_dir.is_dir():
                continue
            
            # Look for {operation_name}_utility.py
            utility_file = category_dir / f"{operation_name}_utility.py"
            if utility_file.exists():
                modules.append(f"{operation_name}_utility")
                break
            
            # Look for any utility in category with similar name
            for util_file in category_dir.glob("*_utility.py"):
                if operation_name in util_file.stem:
                    modules.append(util_file.stem)
                    break
        
        return modules if modules else [f"{operation_name}_utility"]
    
    def analyze_operation_file(self, file_path: Path) -> OperationMetadata:
        """
        Extract metadata from an operation file.
        
        Args:
            file_path: Path to operation file
        
        Returns:
            OperationMetadata with extracted information
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            logger.error(f"Failed to read {file_path}: {e}")
            return OperationMetadata(
                name=file_path.stem,
                display_name=file_path.stem.replace('_', ' ').title(),
                description="Description needed",
                deployment_tier="user_facing"
            )
        
        # Extract docstring
        docstring = self.extract_module_docstring(content)
        
        # Extract description (first line of docstring)
        description = "Description needed"
        if docstring:
            lines = [line.strip() for line in docstring.split('\n') if line.strip()]
            if lines:
                description = lines[0]
        
        # Generate display name
        operation_name = file_path.stem
        display_name = operation_name.replace('_', ' ').title()
        
        # Extract natural language triggers
        triggers = self.extract_natural_language_triggers(content, docstring)
        
        # Infer deployment tier
        tier = self.infer_deployment_tier(file_path, content)
        
        # Infer category
        category = self.infer_category(file_path)
        
        # Extract examples
        examples = self.extract_usage_examples(docstring)
        
        # Find related modules
        modules = self.find_related_modules(operation_name)
        
        return OperationMetadata(
            name=operation_name,
            display_name=display_name,
            description=description,
            deployment_tier=tier,
            natural_language=triggers,
            category=category,
            modules=modules,
            examples=examples
        )
    
    def format_triggers(self, triggers: List[str]) -> str:
        """Format natural language triggers for YAML."""
        if not triggers:
            return "    - \"operation name\""
        
        return "\n".join([f"    - \"{trigger}\"" for trigger in triggers])
    
    def format_examples(self, examples: List[str]) -> str:
        """Format examples for YAML."""
        if not examples:
            return "    - \"Example usage needed\""
        
        return "\n".join([f"    - \"{example}\"" for example in examples])
    
    def generate_yaml_entry(self, metadata: OperationMetadata) -> str:
        """
        Generate YAML entry for an operation.
        
        Args:
            metadata: OperationMetadata to convert to YAML
        
        Returns:
            Formatted YAML string
        """
        today = datetime.now().strftime('%Y-%m-%d')
        
        yaml_entry = f"""
  {metadata.name}:
    name: {metadata.display_name}
    description: {metadata.description}
    deployment_tier: {metadata.deployment_tier}
    natural_language:
{self.format_triggers(metadata.natural_language)}
    category: {metadata.category}
    modules:
"""
        
        # Add modules
        for module in metadata.modules:
            yaml_entry += f"    - {module}\n"
        
        # Add profiles
        yaml_entry += f"""    profiles:
      standard:
        description: {metadata.description}
        modules:
"""
        
        for module in metadata.modules:
            yaml_entry += f"        - {module}\n"
        
        # Add implementation status
        yaml_entry += f"""    implementation_status:
      status: ready
      modules_implemented: {len(metadata.modules)}
      modules_total: {len(metadata.modules)}
      completion_percentage: 100
      notes: Auto-discovered and registered by align orchestrator on {today}
"""
        
        # Add examples
        if metadata.examples:
            yaml_entry += f"""    examples:
{self.format_examples(metadata.examples)}
"""
        
        return yaml_entry
    
    def insert_yaml_entry(self, yaml_entry: str) -> None:
        """
        Insert YAML entry into cortex-operations.yaml.
        Inserts at the end of the operations section, before the modules section.
        
        Args:
            yaml_entry: Formatted YAML string to insert
        """
        # Read current YAML line by line
        with open(self.operations_yaml, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # Find the modules section line (this marks end of operations section)
        modules_line_idx = None
        for i, line in enumerate(lines):
            if line.strip() == 'modules:' and i > 100:  # Skip any modules: inside operations
                modules_line_idx = i
                logger.info(f"Found modules: section at line {i+1}")
                break
        
        if modules_line_idx is None:
            # No modules section, try metadata
            for i, line in enumerate(lines):
                if line.strip() == 'metadata:':
                    modules_line_idx = i
                    logger.info(f"Found metadata: section at line {i+1}")
                    break
        
        if modules_line_idx is None:
            # No modules or metadata, append to end
            logger.warning("No modules: or metadata: section found, appending to end")
            modules_line_idx = len(lines)
        
        # Insert the new entry before modules/metadata section
        # Make sure yaml_entry ends with a newline
        if not yaml_entry.endswith('\n'):
            yaml_entry += '\n'
        
        # Insert before modules/metadata line
        lines.insert(modules_line_idx, yaml_entry)
        
        # Write back
        with open(self.operations_yaml, 'w', encoding='utf-8') as f:
            f.writelines(lines)
        
        logger.info(f"Inserted YAML entry at line {modules_line_idx+1}")
    
    def update_statistics(self) -> None:
        """Update statistics section in cortex-operations.yaml."""
        with open(self.operations_yaml, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        # Count operations and modules
        operations = data.get('operations', {})
        total_ops = len(operations)
        
        total_modules = set()
        for op_data in operations.values():
            if 'modules' in op_data and isinstance(op_data['modules'], list):
                total_modules.update(op_data['modules'])
        
        # Update statistics
        if 'statistics' not in data:
            data['statistics'] = {}
        
        data['statistics']['total_operations'] = total_ops
        data['statistics']['total_modules'] = len(total_modules)
        data['statistics']['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Write back
        with open(self.operations_yaml, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        logger.info(f"Updated statistics: {total_ops} operations, {len(total_modules)} modules")
    
    def add_changelog_entry(self, operation_name: str) -> None:
        """
        Add changelog entry for newly registered operation.
        
        Args:
            operation_name: Name of the operation
        """
        with open(self.operations_yaml, 'r', encoding='utf-8') as f:
            content = f.read()
        
        today = datetime.now().strftime('%Y-%m-%d')
        
        # Find changelog section
        changelog_pattern = r'(changelog:\s*\n(?:  .*\n)*)'
        match = re.search(changelog_pattern, content)
        
        if match:
            # Insert new entry at the top of changelog
            changelog_section = match.group(1)
            new_entry = f"  - version: auto-registered\n    date: {today}\n    changes:\n    - Auto-registered {operation_name} operation\n"
            
            # Insert after "changelog:\n"
            insert_pos = match.start() + len("changelog:\n")
            new_content = content[:insert_pos] + new_entry + content[insert_pos:]
            
            with open(self.operations_yaml, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            logger.info(f"Added changelog entry for {operation_name}")
    
    def register_feature(self, operation_name: str, dry_run: bool = False) -> RegistrationResult:
        """
        Register a new feature in cortex-operations.yaml.
        
        Args:
            operation_name: Name of the operation to register
            dry_run: If True, generate YAML but don't write to file
        
        Returns:
            RegistrationResult with status and details
        """
        try:
            # Find operation file - check all possible locations
            search_locations = [
                (self.operations_dir, "operations"),
                (self.orchestrators_dir, "orchestrators"),
                (self.workflows_dir, "workflows"),
                (self.agents_dir, "cortex_agents"),
                (self.security_agents_dir, "security_agents"),
            ]
            
            file_path = None
            location_type = None
            
            for location_dir, loc_type in search_locations:
                potential_file = location_dir / f"{operation_name}.py"
                if potential_file.exists():
                    file_path = potential_file
                    location_type = loc_type
                    break
            
            # If not found in top-level, try modules
            if not file_path:
                for category_dir in self.modules_dir.iterdir():
                    if not category_dir.is_dir():
                        continue
                    
                    potential_file = category_dir / f"{operation_name}.py"
                    if potential_file.exists():
                        file_path = potential_file
                        location_type = "modules"
                        break
            
            if not file_path:
                return RegistrationResult(
                    success=False,
                    operation_name=operation_name,
                    error_message=f"Operation file not found: {operation_name}.py (checked operations/, orchestrators/, workflows/, cortex_agents/, and modules/)"
                )
            
            # Analyze operation
            metadata = self.analyze_operation_file(file_path)
            
            # Generate YAML entry
            yaml_entry = self.generate_yaml_entry(metadata)
            
            if dry_run:
                return RegistrationResult(
                    success=True,
                    operation_name=operation_name,
                    yaml_entry=yaml_entry,
                    dry_run=True,
                    file_path=file_path
                )
            
            # Insert into YAML
            self.insert_yaml_entry(yaml_entry)
            
            # Update statistics
            self.update_statistics()
            
            # Add changelog entry
            self.add_changelog_entry(operation_name)
            
            return RegistrationResult(
                success=True,
                operation_name=operation_name,
                yaml_entry=yaml_entry,
                file_path=file_path
            )
        
        except Exception as e:
            logger.error(f"Failed to register {operation_name}: {e}", exc_info=True)
            return RegistrationResult(
                success=False,
                operation_name=operation_name,
                error_message=str(e)
            )
    
    def batch_register(self, operation_names: List[str], dry_run: bool = False) -> Dict[str, RegistrationResult]:
        """
        Register multiple operations.
        
        Args:
            operation_names: List of operation names to register
            dry_run: If True, don't write to file
        
        Returns:
            Dict mapping operation names to RegistrationResults
        """
        results = {}
        
        for op_name in operation_names:
            result = self.register_feature(op_name, dry_run=dry_run)
            results[op_name] = result
        
        return results


def main():
    """CLI entry point for standalone registration."""
    import sys
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) < 2:
        print("Usage: python -m src.operations.modules.realignment.feature_auto_registrar <operation_name> [--dry-run]")
        sys.exit(1)
    
    operation_name = sys.argv[1]
    dry_run = '--dry-run' in sys.argv
    
    try:
        registrar = FeatureAutoRegistrar()
        result = registrar.register_feature(operation_name, dry_run=dry_run)
        
        if result.success:
            if dry_run:
                print(f"\n✅ DRY RUN - Generated YAML for: {operation_name}\n")
                print(result.yaml_entry)
            else:
                print(f"\n✅ Successfully registered: {operation_name}")
                print(f"   File: {result.file_path}")
        else:
            print(f"\n❌ Failed to register: {operation_name}")
            print(f"   Error: {result.error_message}")
            sys.exit(1)
    
    except Exception as e:
        logger.error(f"Registration failed: {e}", exc_info=True)
        sys.exit(2)


if __name__ == "__main__":
    main()
