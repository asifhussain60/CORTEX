"""
Intent Router Auto-Fixer for CORTEX Align v2.0

Automatically adds missing operations to the intent router with appropriate triggers.
Analyzes operation files to extract natural language triggers and adds them to the
routing configuration.

Author: Asif Hussain
Date: December 3, 2025
Version: 1.0.0
"""

import re
import yaml
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class IntentRouterFix:
    """Result of adding operation to intent router."""
    success: bool
    operation_name: str
    triggers: List[str]
    error_message: str = ""


class IntentRouterAutoFixer:
    """Automatically adds missing operations to intent router."""
    
    def __init__(self, cortex_root: Path):
        """
        Initialize the intent router auto-fixer.
        
        Args:
            cortex_root: Root directory of CORTEX installation
        """
        self.cortex_root = cortex_root
        self.operations_yaml = cortex_root / "cortex-operations.yaml"
        self.response_templates = cortex_root / "cortex-brain" / "response-templates.yaml"
    
    def extract_triggers_from_operation(self, operation_name: str) -> List[str]:
        """
        Extract natural language triggers for an operation.
        
        Args:
            operation_name: Name of the operation (e.g., 'align', 'tdd')
        
        Returns:
            List of natural language trigger phrases
        """
        triggers = []
        
        # Try to find the operation file
        operations_dir = self.cortex_root / "src" / "operations"
        op_file = operations_dir / f"{operation_name}.py"
        
        if not op_file.exists():
            # Try modules directory
            modules_dir = operations_dir / "modules"
            for subdir in modules_dir.iterdir():
                if subdir.is_dir():
                    potential_file = subdir / f"{operation_name}.py"
                    if potential_file.exists():
                        op_file = potential_file
                        break
        
        if op_file.exists():
            try:
                content = op_file.read_text(encoding='utf-8')
                
                # Extract from docstring
                doc_pattern = r'"""(.*?)"""'
                doc_match = re.search(doc_pattern, content, re.DOTALL)
                if doc_match:
                    docstring = doc_match.group(1)
                    
                    # Look for usage patterns
                    usage_patterns = [
                        r'(?:Usage|Commands?|Triggers?):\s*\n((?:[-*]\s*.+\n?)+)',
                        r'`([a-z][a-z\s]{2,40})`',
                        r'["\']([a-z][a-z\s]{2,40})["\']'
                    ]
                    
                    for pattern in usage_patterns:
                        matches = re.findall(pattern, docstring.lower())
                        for match in matches:
                            if isinstance(match, str):
                                clean = re.sub(r'^[-*]\s*', '', match).strip()
                                if clean and len(clean.split()) <= 5:
                                    triggers.append(clean)
            except Exception as e:
                logger.warning(f"Failed to extract triggers from {op_file}: {e}")
        
        # Generate default triggers based on operation name
        if not triggers:
            triggers = self._generate_default_triggers(operation_name)
        
        # Remove duplicates and limit to 5
        return list(dict.fromkeys(triggers))[:5]
    
    def _generate_default_triggers(self, operation_name: str) -> List[str]:
        """
        Generate default triggers based on operation name.
        
        Args:
            operation_name: Name of the operation
        
        Returns:
            List of default trigger phrases
        """
        # Convert snake_case to space-separated
        readable = operation_name.replace('_', ' ')
        
        triggers = [
            operation_name,  # Direct name
            readable,  # Space-separated name
        ]
        
        # Add verb variations
        common_verbs = ['run', 'start', 'execute', 'show', 'display']
        for verb in common_verbs[:2]:  # Limit to 2 verbs
            triggers.append(f"{verb} {readable}")
        
        return triggers
    
    def add_to_intent_router(
        self, 
        operation_name: str, 
        triggers: Optional[List[str]] = None,
        dry_run: bool = False
    ) -> IntentRouterFix:
        """
        Add operation to intent router configuration.
        
        Args:
            operation_name: Name of the operation to add
            triggers: Optional list of trigger phrases (auto-extracted if None)
            dry_run: If True, don't modify files
        
        Returns:
            IntentRouterFix result
        """
        try:
            # Extract triggers if not provided
            if triggers is None:
                triggers = self.extract_triggers_from_operation(operation_name)
            
            if not triggers:
                return IntentRouterFix(
                    success=False,
                    operation_name=operation_name,
                    triggers=[],
                    error_message="No triggers could be generated"
                )
            
            # Load cortex-operations.yaml
            if not self.operations_yaml.exists():
                return IntentRouterFix(
                    success=False,
                    operation_name=operation_name,
                    triggers=triggers,
                    error_message="cortex-operations.yaml not found"
                )
            
            with open(self.operations_yaml, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
            
            # Ensure operations section exists
            if 'operations' not in config:
                config['operations'] = {}
            
            # Check if operation already exists
            if operation_name in config['operations']:
                # Update triggers if missing
                existing_op = config['operations'][operation_name]
                if 'natural_language' not in existing_op or not existing_op['natural_language']:
                    existing_op['natural_language'] = triggers
                    if not dry_run:
                        self._save_yaml(config)
                    return IntentRouterFix(
                        success=True,
                        operation_name=operation_name,
                        triggers=triggers
                    )
                else:
                    return IntentRouterFix(
                        success=True,
                        operation_name=operation_name,
                        triggers=existing_op['natural_language'],
                        error_message="Operation already has triggers"
                    )
            
            # Add new operation entry
            config['operations'][operation_name] = {
                'natural_language': triggers,
                'deployment_tier': 'user_facing',  # Default
                'description': f"Operation: {operation_name.replace('_', ' ').title()}",
                'category': 'general',
                'version': '1.0.0',
                'author': 'Asif Hussain'
            }
            
            if not dry_run:
                self._save_yaml(config)
            
            return IntentRouterFix(
                success=True,
                operation_name=operation_name,
                triggers=triggers
            )
            
        except Exception as e:
            logger.error(f"Failed to add {operation_name} to intent router: {e}")
            return IntentRouterFix(
                success=False,
                operation_name=operation_name,
                triggers=triggers or [],
                error_message=str(e)
            )
    
    def _save_yaml(self, config: Dict) -> None:
        """
        Save YAML configuration with proper formatting.
        
        Args:
            config: Configuration dictionary to save
        """
        # Create backup
        backup_path = self.operations_yaml.with_suffix('.yaml.backup')
        if self.operations_yaml.exists():
            self.operations_yaml.rename(backup_path)
        
        try:
            with open(self.operations_yaml, 'w', encoding='utf-8') as f:
                yaml.dump(
                    config, 
                    f, 
                    default_flow_style=False,
                    sort_keys=False,
                    allow_unicode=True,
                    indent=2
                )
            logger.info(f"✅ Updated {self.operations_yaml}")
        except Exception as e:
            # Restore backup on error
            if backup_path.exists():
                backup_path.rename(self.operations_yaml)
            raise e
    
    def fix_missing_operations(
        self, 
        missing_operations: List[str],
        dry_run: bool = False
    ) -> List[IntentRouterFix]:
        """
        Fix multiple missing operations at once.
        
        Args:
            missing_operations: List of operation names to add
            dry_run: If True, don't modify files
        
        Returns:
            List of IntentRouterFix results
        """
        results = []
        
        for op_name in missing_operations:
            result = self.add_to_intent_router(op_name, dry_run=dry_run)
            results.append(result)
            
            if result.success:
                logger.info(f"   ✅ Added {op_name} to intent router with triggers: {result.triggers}")
            else:
                logger.warning(f"   ⚠️  Could not add {op_name}: {result.error_message}")
        
        return results
