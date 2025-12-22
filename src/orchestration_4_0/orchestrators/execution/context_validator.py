"""
Context Validator for Execution Orchestrator

Validates execution context sufficiency with auto-retrieval capabilities.

Author: Asif Hussain
Version: 1.0
"""

from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging

from .schemas import ContextValidation


class ContextValidator:
    """
    Validate execution context sufficiency.
    
    Features:
    - Check required vs optional context
    - Auto-retrieve missing context from knowledge graph
    - Validate context quality (completeness, freshness, validity)
    - Infer missing values from existing context
    """
    
    def __init__(
        self,
        knowledge_graph: Optional[Any] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize context validator.
        
        Args:
            knowledge_graph: Optional knowledge graph for auto-retrieval
            logger: Optional logger instance
        """
        self.kg = knowledge_graph
        self.logger = logger or logging.getLogger(__name__)
    
    async def validate_context_sufficiency(
        self,
        context: Dict[str, Any],
        execution_plan: Dict[str, Any]
    ) -> ContextValidation:
        """
        Validate context before execution.
        Auto-retrieve missing items if possible.
        
        Args:
            context: Execution context to validate
            execution_plan: Plan defining required/optional context
            
        Returns:
            ContextValidation with validation results
        """
        required = execution_plan.get('required_context', [])
        optional = execution_plan.get('optional_context', [])
        
        self.logger.debug(f"🔍 Validating context (required={len(required)}, optional={len(optional)})")
        
        # Check required items
        missing_required = [key for key in required if key not in context]
        missing_optional = [key for key in optional if key not in context]
        
        # Attempt auto-retrieval for missing required items
        auto_retrieved = {}
        if missing_required:
            self.logger.info(f"🔍 Auto-retrieving missing context: {missing_required}")
            auto_retrieved = await self._retrieve_missing_context(
                missing_required,
                context
            )
            context.update(auto_retrieved)
            
            # Re-check after retrieval
            missing_required = [key for key in required if key not in context]
        
        # Check context quality
        quality_issues = await self._check_context_quality(context, execution_plan)
        
        validation = ContextValidation(
            has_requirements=len(missing_required) == 0,
            missing_required=missing_required,
            missing_optional=missing_optional,
            quality_issues=quality_issues,
            context=context,
            auto_retrieved=auto_retrieved
        )
        
        if validation.is_valid:
            self.logger.info("✅ Context validation passed")
        else:
            self.logger.warning(
                f"⚠️ Context validation failed: "
                f"missing_required={missing_required}, "
                f"quality_issues={len(quality_issues)}"
            )
        
        return validation
    
    async def _retrieve_missing_context(
        self,
        missing_keys: List[str],
        existing_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Auto-retrieve missing context from knowledge graph or inference.
        
        Args:
            missing_keys: Keys to retrieve
            existing_context: Existing context for hints
            
        Returns:
            Retrieved context items
        """
        retrieved = {}
        
        for key in missing_keys:
            # Try knowledge graph first
            if self.kg:
                value = await self._query_knowledge_graph(key, existing_context)
                if value is not None:
                    retrieved[key] = value
                    self.logger.info(f"✅ Retrieved '{key}' from knowledge graph")
                    continue
            
            # Try inference from existing context
            inferred = await self._infer_context_value(key, existing_context)
            if inferred is not None:
                retrieved[key] = inferred
                self.logger.info(f"💡 Inferred '{key}' from existing context")
            else:
                self.logger.warning(f"❌ Could not retrieve or infer '{key}'")
        
        return retrieved
    
    async def _query_knowledge_graph(
        self,
        key: str,
        hint: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Query knowledge graph for missing context.
        
        Args:
            key: Context key to retrieve
            hint: Existing context for hints
            
        Returns:
            Retrieved value or None
        """
        if not self.kg:
            return None
        
        try:
            # Try direct query
            value = await self.kg.query(
                category='execution_context',
                key=key,
                hint=hint
            )
            return value
        except Exception as e:
            self.logger.debug(f"Knowledge graph query failed for '{key}': {e}")
            return None
    
    async def _infer_context_value(
        self,
        key: str,
        existing_context: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Infer missing value from existing context.
        
        Args:
            key: Context key to infer
            existing_context: Existing context
            
        Returns:
            Inferred value or None
        """
        # Common inference patterns
        inferences = {
            'workspace': lambda ctx: ctx.get('workspace_root') or ctx.get('project_path'),
            'project_name': lambda ctx: ctx.get('workspace', '').split('/')[-1] if ctx.get('workspace') else None,
            'language': lambda ctx: self._infer_language(ctx.get('files', [])),
            'framework': lambda ctx: self._infer_framework(ctx.get('files', [])),
        }
        
        if key in inferences:
            try:
                return inferences[key](existing_context)
            except Exception as e:
                self.logger.debug(f"Inference failed for '{key}': {e}")
        
        return None
    
    def _infer_language(self, files: List[str]) -> Optional[str]:
        """Infer programming language from files"""
        if not files:
            return None
        
        # Count file extensions
        extensions = {}
        for file in files:
            ext = file.split('.')[-1] if '.' in file else None
            if ext:
                extensions[ext] = extensions.get(ext, 0) + 1
        
        # Map extensions to languages
        lang_map = {
            'py': 'python',
            'js': 'javascript',
            'ts': 'typescript',
            'cs': 'csharp',
            'java': 'java',
            'go': 'go',
            'rb': 'ruby',
        }
        
        # Return most common language
        if extensions:
            most_common_ext = max(extensions, key=extensions.get)
            return lang_map.get(most_common_ext)
        
        return None
    
    def _infer_framework(self, files: List[str]) -> Optional[str]:
        """Infer framework from files"""
        file_str = ' '.join(files).lower()
        
        frameworks = {
            'react': ['package.json', 'react'],
            'vue': ['package.json', 'vue'],
            'angular': ['angular.json'],
            'django': ['manage.py', 'settings.py'],
            'flask': ['app.py', 'flask'],
            'fastapi': ['main.py', 'fastapi'],
            'express': ['package.json', 'express'],
        }
        
        for framework, indicators in frameworks.items():
            if all(ind in file_str for ind in indicators):
                return framework
        
        return None
    
    async def _check_context_quality(
        self,
        context: Dict[str, Any],
        execution_plan: Dict[str, Any]
    ) -> List[str]:
        """
        Check context quality (completeness, freshness, validity).
        
        Args:
            context: Context to check
            execution_plan: Plan with quality requirements
            
        Returns:
            List of quality issues
        """
        issues = []
        
        # Check for empty values
        for key, value in context.items():
            if value is None or (isinstance(value, str) and value.strip() == ''):
                issues.append(f"'{key}' is empty")
        
        # Check for stale data
        if 'timestamp' in context:
            try:
                timestamp = context['timestamp']
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp)
                
                age = datetime.now() - timestamp
                max_age_hours = execution_plan.get('max_context_age_hours', 24)
                
                if age > timedelta(hours=max_age_hours):
                    issues.append(
                        f"Context is {age.days} days old (max allowed: {max_age_hours} hours)"
                    )
            except Exception as e:
                self.logger.debug(f"Could not check timestamp: {e}")
        
        # Check for required types
        type_requirements = execution_plan.get('context_types', {})
        for key, expected_type_name in type_requirements.items():
            if key in context:
                value = context[key]
                expected_type = self._resolve_type(expected_type_name)
                
                if expected_type and not isinstance(value, expected_type):
                    issues.append(
                        f"'{key}' should be {expected_type_name}, "
                        f"got {type(value).__name__}"
                    )
        
        return issues
    
    def _resolve_type(self, type_name: str) -> Optional[type]:
        """Resolve type name to Python type"""
        type_map = {
            'str': str,
            'string': str,
            'int': int,
            'integer': int,
            'float': float,
            'bool': bool,
            'boolean': bool,
            'list': list,
            'dict': dict,
            'set': set,
        }
        return type_map.get(type_name.lower())
