"""
Context Validator

Phase 5 Task 5.8: Context Validator Implementation
Validates execution context sufficiency with auto-retrieval for missing dependencies.

Features:
- Pre-execution context validation
- Dependency graph analysis
- Auto-retrieval from knowledge graph
- Context quality assessment
- Type checking and freshness validation

Author: CORTEX Development Team
Version: 1.0.0
Created: 2025-12-21
"""

import logging
from typing import Dict, Any, List, Optional, Type
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class ContextQuality(Enum):
    """Context quality levels"""
    EXCELLENT = "excellent"  # All required + optional, no issues
    GOOD = "good"            # All required, some optional, minor issues
    ACCEPTABLE = "acceptable"  # All required, quality issues present
    INSUFFICIENT = "insufficient"  # Missing required context


@dataclass
class ContextValidation:
    """Result of context validation"""
    has_requirements: bool
    missing_required: List[str] = field(default_factory=list)
    missing_optional: List[str] = field(default_factory=list)
    quality_issues: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    retrieved_items: Dict[str, Any] = field(default_factory=dict)
    quality: ContextQuality = ContextQuality.INSUFFICIENT
    
    def is_valid(self) -> bool:
        """Check if context is valid for execution"""
        return self.has_requirements
    
    def get_quality_score(self) -> float:
        """Calculate quality score (0-100)"""
        if not self.has_requirements:
            return 0.0
        
        score = 100.0
        
        # Deduct for missing optional
        if self.missing_optional:
            score -= min(20.0, len(self.missing_optional) * 5)
        
        # Deduct for quality issues
        if self.quality_issues:
            score -= min(30.0, len(self.quality_issues) * 10)
        
        return max(0.0, score)


class ContextValidator:
    """
    Validates execution context sufficiency with auto-retrieval.
    
    Capabilities:
    - Validates required vs optional context
    - Auto-retrieves missing context from knowledge graph
    - Infers context from existing data
    - Checks context quality (completeness, freshness, types)
    - Provides actionable recommendations
    """
    
    def __init__(self, knowledge_graph: Optional[Any] = None):
        """
        Initialize context validator.
        
        Args:
            knowledge_graph: Knowledge graph for context retrieval (optional)
        """
        self.kg = knowledge_graph
        self._metrics = {
            "total_validations": 0,
            "valid_contexts": 0,
            "auto_retrievals": 0,
            "inference_attempts": 0,
            "quality_checks": 0
        }
    
    async def validate_context_sufficiency(
        self,
        context: Dict[str, Any],
        execution_plan: Dict[str, Any]
    ) -> ContextValidation:
        """
        Validate context before execution with auto-retrieval.
        
        Args:
            context: Current execution context
            execution_plan: Plan specifying required/optional context
            
        Returns:
            ContextValidation with validation results and enriched context
        """
        self._metrics["total_validations"] += 1
        
        logger.info("🔍 Validating context sufficiency...")
        
        # Extract requirements
        required = execution_plan.get('required_context', [])
        optional = execution_plan.get('optional_context', [])
        
        # Check required items
        missing_required = [key for key in required if key not in context]
        missing_optional = [key for key in optional if key not in context]
        
        logger.info(f"  Required: {len(required)} items, Missing: {len(missing_required)}")
        logger.info(f"  Optional: {len(optional)} items, Missing: {len(missing_optional)}")
        
        # Attempt auto-retrieval for missing required
        retrieved = {}
        if missing_required:
            logger.info(f"🔍 Auto-retrieving {len(missing_required)} missing items...")
            retrieved = await self._retrieve_missing_context(
                missing_required.copy(),  # Use copy to preserve original list
                context
            )
            
            # Update context with successfully retrieved items
            for key, value in retrieved.items():
                if value is not None:
                    context[key] = value
            
            # Re-check after retrieval
            missing_required = [key for key in required if key not in context]
            
            if retrieved:
                self._metrics["auto_retrievals"] += len(retrieved)
                logger.info(f"✅ Retrieved {len(retrieved)} items: {list(retrieved.keys())}")
        
        # Check quality
        quality_issues = await self._check_context_quality(context, execution_plan)
        
        # Determine overall quality
        has_requirements = len(missing_required) == 0
        quality = self._determine_quality(
            has_requirements,
            missing_optional,
            quality_issues
        )
        
        if has_requirements:
            self._metrics["valid_contexts"] += 1
        
        validation = ContextValidation(
            has_requirements=has_requirements,
            missing_required=missing_required,
            missing_optional=missing_optional,
            quality_issues=quality_issues,
            context=context,
            retrieved_items=retrieved,
            quality=quality
        )
        
        # Log summary
        logger.info(f"📊 Validation complete: {quality.value.upper()}")
        logger.info(f"  Score: {validation.get_quality_score():.1f}/100")
        if missing_required:
            logger.warning(f"  ⚠️ Missing required: {missing_required}")
        if quality_issues:
            logger.warning(f"  ⚠️ Quality issues: {len(quality_issues)}")
        
        return validation
    
    async def _retrieve_missing_context(
        self,
        missing_keys: List[str],
        existing_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Auto-retrieve missing context from knowledge graph or inference.
        
        Args:
            missing_keys: List of missing context keys
            existing_context: Current context for hints
            
        Returns:
            Dictionary of retrieved context items
        """
        retrieved = {}
        
        for key in missing_keys:
            # Try knowledge graph retrieval
            if self.kg:
                value = await self._query_knowledge_graph(
                    key,
                    existing_context
                )
                if value:
                    retrieved[key] = value
                    logger.info(f"  ✅ Retrieved {key} from knowledge graph")
                    continue
            
            # Try inference from existing context
            inferred = await self._infer_context_value(key, existing_context)
            if inferred is not None:
                retrieved[key] = inferred
                logger.info(f"  💡 Inferred {key} from existing context")
                self._metrics["inference_attempts"] += 1
            else:
                logger.warning(f"  ❌ Could not retrieve or infer {key}")
        
        return retrieved
    
    async def _query_knowledge_graph(
        self,
        key: str,
        hint_context: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Query knowledge graph for missing context.
        
        Args:
            key: Context key to retrieve
            hint_context: Existing context for query hints
            
        Returns:
            Retrieved value or None
        """
        if not self.kg:
            return None
        
        try:
            # Check if knowledge graph has query method
            if hasattr(self.kg, 'query'):
                return await self.kg.query(
                    category='execution_context',
                    key=key,
                    hint=hint_context
                )
            
            # Fallback: try get method
            if hasattr(self.kg, 'get'):
                return self.kg.get(key)
        
        except Exception as e:
            logger.error(f"Knowledge graph query failed for {key}: {e}")
        
        return None
    
    async def _infer_context_value(
        self,
        key: str,
        existing_context: Dict[str, Any]
    ) -> Optional[Any]:
        """
        Infer missing context value from existing context.
        
        Inference strategies:
        - Derive from related keys (e.g., project_root from file_path)
        - Use defaults based on key patterns
        - Extract from composite values
        
        Args:
            key: Missing context key
            existing_context: Current context
            
        Returns:
            Inferred value or None
        """
        # Strategy 1: Derive from file paths
        if key == 'project_root' and 'file_path' in existing_context:
            # Extract project root from file path
            file_path = existing_context['file_path']
            if isinstance(file_path, str):
                # Simple heuristic: find common project indicators
                for indicator in ['/src/', '/tests/', '/lib/', '/.git/']:
                    if indicator in file_path:
                        return file_path.split(indicator)[0]
        
        # Strategy 2: Derive from repository info
        if key == 'repository_name' and 'repository_url' in existing_context:
            repo_url = existing_context['repository_url']
            if isinstance(repo_url, str):
                # Extract name from URL
                return repo_url.rstrip('/').split('/')[-1].replace('.git', '')
        
        # Strategy 3: Default values for common keys
        defaults = {
            'language': 'python',
            'framework': 'unknown',
            'test_framework': 'pytest',
            'complexity': 'medium',
            'priority': 'normal'
        }
        
        if key in defaults:
            logger.info(f"  Using default value for {key}: {defaults[key]}")
            return defaults[key]
        
        # Strategy 4: Extract from composite values
        if key.endswith('_count') and key.replace('_count', 's') in existing_context:
            # e.g., file_count from files list
            source_key = key.replace('_count', 's')
            source_value = existing_context[source_key]
            if isinstance(source_value, (list, tuple, set)):
                return len(source_value)
        
        return None
    
    async def _check_context_quality(
        self,
        context: Dict[str, Any],
        execution_plan: Dict[str, Any]
    ) -> List[str]:
        """
        Check context quality (completeness, freshness, types).
        
        Args:
            context: Current context
            execution_plan: Plan with quality requirements
            
        Returns:
            List of quality issues
        """
        self._metrics["quality_checks"] += 1
        issues = []
        
        # Check 1: Empty or None values
        for key, value in context.items():
            if value is None:
                issues.append(f"{key} is None")
            elif isinstance(value, str) and value.strip() == '':
                issues.append(f"{key} is empty string")
            elif isinstance(value, (list, dict)) and len(value) == 0:
                issues.append(f"{key} is empty collection")
        
        # Check 2: Stale timestamps
        if 'timestamp' in context:
            try:
                timestamp = context['timestamp']
                if isinstance(timestamp, str):
                    timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                
                if isinstance(timestamp, datetime):
                    age = datetime.now() - timestamp.replace(tzinfo=None)
                    max_age = timedelta(hours=24)
                    
                    if age > max_age:
                        issues.append(f"Context is {age.days} days old (may be stale)")
            except Exception as e:
                issues.append(f"Invalid timestamp format: {e}")
        
        # Check 3: Type requirements
        type_requirements = execution_plan.get('context_types', {})
        for key, expected_type in type_requirements.items():
            if key in context:
                actual_value = context[key]
                
                # Handle type strings
                if isinstance(expected_type, str):
                    expected_type = self._get_type_from_string(expected_type)
                
                if expected_type and not isinstance(actual_value, expected_type):
                    issues.append(
                        f"{key} should be {expected_type.__name__}, "
                        f"got {type(actual_value).__name__}"
                    )
        
        # Check 4: Value constraints
        constraints = execution_plan.get('context_constraints', {})
        for key, constraint in constraints.items():
            if key in context:
                value = context[key]
                
                # Check min/max for numeric values
                if 'min' in constraint and isinstance(value, (int, float)):
                    if value < constraint['min']:
                        issues.append(f"{key} ({value}) below minimum ({constraint['min']})")
                
                if 'max' in constraint and isinstance(value, (int, float)):
                    if value > constraint['max']:
                        issues.append(f"{key} ({value}) exceeds maximum ({constraint['max']})")
                
                # Check allowed values
                if 'allowed' in constraint and value not in constraint['allowed']:
                    issues.append(
                        f"{key} value '{value}' not in allowed list: {constraint['allowed']}"
                    )
        
        return issues
    
    def _determine_quality(
        self,
        has_requirements: bool,
        missing_optional: List[str],
        quality_issues: List[str]
    ) -> ContextQuality:
        """
        Determine overall context quality.
        
        Args:
            has_requirements: Whether all required context present
            missing_optional: List of missing optional items
            quality_issues: List of quality issues
            
        Returns:
            ContextQuality enum value
        """
        if not has_requirements:
            return ContextQuality.INSUFFICIENT
        
        if not missing_optional and not quality_issues:
            return ContextQuality.EXCELLENT
        
        if not missing_optional and len(quality_issues) <= 2:
            return ContextQuality.GOOD
        
        return ContextQuality.ACCEPTABLE
    
    def _get_type_from_string(self, type_string: str) -> Optional[Type]:
        """Convert type string to actual type"""
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
            'tuple': tuple,
            'set': set
        }
        return type_map.get(type_string.lower())
    
    def get_metrics(self) -> Dict[str, int]:
        """Get validation metrics"""
        return self._metrics.copy()
    
    def reset_metrics(self):
        """Reset all metrics to zero"""
        for key in self._metrics:
            self._metrics[key] = 0
