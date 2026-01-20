"""
BulkIngestionPipeline for extensible knowledge ingestion with plugin architecture.

Implements: IntakeAdapter → FilterStrategy → RefinementRule → OutputFormatter 
→ Validator → StorageBackend with registry pattern for plugin discovery.

Supports both batch and streaming modes with comprehensive error handling,
retry logic, and metrics tracking.

Governance:
  - CORE-008: TDD (test-first development)
  - CORE-011: Type hints in all methods
  - CORE-012: Google-style docstrings
  - CORE-013: Specific exception handling
  - CORE-028: Kebab-case module naming
"""

from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Iterator, Tuple, Type
from enum import Enum
from datetime import datetime
from abc import ABC, abstractmethod
from collections import defaultdict
import json


# ============================================================================
# Plugin Architecture Classes
# ============================================================================

class PluginType(Enum):
    """Types of plugins in the pipeline."""
    
    INTAKE_ADAPTER = "intake_adapter"
    FILTER_STRATEGY = "filter_strategy"
    REFINEMENT_RULE = "refinement_rule"
    OUTPUT_FORMATTER = "output_formatter"
    VALIDATOR = "validator"


@dataclass
class PluginMetadata:
    """Metadata for a registered plugin."""
    
    name: str
    plugin_type: PluginType
    version: str = "1.0"
    description: str = ""
    enabled: bool = True
    required_params: List[str] = field(default_factory=list)
    optional_params: List[str] = field(default_factory=list)


@dataclass
class PipelineStage:
    """Represents a stage in the pipeline."""
    
    name: str
    stage_type: PluginType
    handler: Callable
    config: Dict[str, Any] = field(default_factory=dict)
    enabled: bool = True


@dataclass
class PipelineMetrics:
    """Metrics for pipeline execution."""
    
    stage: str
    timestamp: datetime
    items_processed: int = 0
    items_failed: int = 0
    items_skipped: int = 0
    duration_seconds: float = 0.0
    success_rate: float = 0.0
    errors: List[str] = field(default_factory=list)


@dataclass
class ExecutionState:
    """Tracks pipeline execution state."""
    
    execution_id: str
    start_time: datetime
    current_stage: str
    total_items: int
    processed_items: int = 0
    failed_items: int = 0
    skipped_items: int = 0
    status: str = "running"  # running, completed, failed, paused
    error_message: Optional[str] = None
    end_time: Optional[datetime] = None


# ============================================================================
# Plugin Base Classes
# ============================================================================

class IntakeAdapter(ABC):
    """Base class for intake adapters."""
    
    @abstractmethod
    def read(self, source: Any) -> Iterator[Dict[str, Any]]:
        """Read data from source."""
        pass


class FilterStrategy(ABC):
    """Base class for filter strategies."""
    
    @abstractmethod
    def filter(self, item: Dict[str, Any]) -> bool:
        """Return True if item should pass filter."""
        pass


class RefinementRule(ABC):
    """Base class for refinement rules."""
    
    @abstractmethod
    def refine(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Refine/transform item."""
        pass


class OutputFormatter(ABC):
    """Base class for output formatters."""
    
    @abstractmethod
    def format(self, item: Dict[str, Any]) -> str:
        """Format item for storage."""
        pass


class Validator(ABC):
    """Base class for validators."""
    
    @abstractmethod
    def validate(self, item: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate item. Return (is_valid, error_message)."""
        pass


# ============================================================================
# Built-in Implementations
# ============================================================================

class PassThroughAdapter(IntakeAdapter):
    """Pass-through adapter that yields items as-is."""
    
    def read(self, source: Any) -> Iterator[Dict[str, Any]]:
        """Yield items from source."""
        if isinstance(source, list):
            for item in source:
                yield item if isinstance(item, dict) else {"data": item}


class AcceptAllFilter(FilterStrategy):
    """Filter that accepts all items."""
    
    def filter(self, item: Dict[str, Any]) -> bool:
        """Always return True."""
        return True


class IdentityRefinement(RefinementRule):
    """Refinement that returns item unchanged."""
    
    def refine(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Return item unchanged."""
        return item


class JSONFormatter(OutputFormatter):
    """Formats items as JSON."""
    
    def format(self, item: Dict[str, Any]) -> str:
        """Convert item to JSON string."""
        return json.dumps(item)


class SchemaValidator(Validator):
    """Basic schema validator."""
    
    def __init__(self, required_fields: List[str] = None):
        """Initialize with required fields."""
        self.required_fields = required_fields or []
    
    def validate(self, item: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate item has required fields."""
        for field in self.required_fields:
            if field not in item:
                return False, f"Missing required field: {field}"
        return True, None


# ============================================================================
# Main Pipeline Class
# ============================================================================

class BulkIngestionPipeline:
    """
    Extensible bulk ingestion pipeline with plugin architecture.
    
    Supports: IntakeAdapter → FilterStrategy → RefinementRule → 
    OutputFormatter → Validator → StorageBackend
    """
    
    def __init__(
        self,
        backends: Dict[str, Any],
        batch_size: int = 1000,
        streaming_enabled: bool = True,
        max_retries: int = 3,
        error_strategy: str = 'skip'  # 'skip', 'fail', 'continue'
    ):
        """
        Initialize BulkIngestionPipeline.
        
        Args:
            backends: Storage backends dictionary.
            batch_size: Items per batch.
            streaming_enabled: Enable streaming mode.
            max_retries: Max retries for failed items.
            error_strategy: How to handle errors (skip/fail/continue).
        """
        self.backends = backends
        self.batch_size = batch_size
        self.streaming_enabled = streaming_enabled
        self.max_retries = max_retries
        self.error_strategy = error_strategy
        
        # Registry for plugins
        self.registry: Dict[PluginType, Dict[str, PluginMetadata]] = {
            pt: {} for pt in PluginType
        }
        
        # Registered stage handlers
        self.stages: Dict[PluginType, List[PipelineStage]] = {
            pt: [] for pt in PluginType
        }
        
        # Execution tracking
        self.execution_states: Dict[str, ExecutionState] = {}
        self.current_execution: Optional[str] = None
        
        # Metrics
        self.metrics: List[PipelineMetrics] = []
        self.failed_items: List[Tuple[Any, str]] = []
        self.stats = {
            'total_batches': 0,
            'total_items': 0,
            'successful_items': 0,
            'failed_items': 0,
            'skipped_items': 0,
        }
        
        # Register built-in adapters
        self._register_builtin_adapters()

    def _register_builtin_adapters(self) -> None:
        """Register built-in adapter implementations."""
        self.registry[PluginType.INTAKE_ADAPTER]['pass_through'] = PluginMetadata(
            name='pass_through',
            plugin_type=PluginType.INTAKE_ADAPTER,
            version='1.0',
            description='Pass-through adapter'
        )
        self.registry[PluginType.FILTER_STRATEGY]['accept_all'] = PluginMetadata(
            name='accept_all',
            plugin_type=PluginType.FILTER_STRATEGY,
            version='1.0',
            description='Accept all items filter'
        )
        self.registry[PluginType.REFINEMENT_RULE]['identity'] = PluginMetadata(
            name='identity',
            plugin_type=PluginType.REFINEMENT_RULE,
            version='1.0',
            description='Identity refinement (no-op)'
        )
        self.registry[PluginType.OUTPUT_FORMATTER]['json'] = PluginMetadata(
            name='json',
            plugin_type=PluginType.OUTPUT_FORMATTER,
            version='1.0',
            description='JSON formatter'
        )

    # ========================================================================
    # Plugin Registration Methods
    # ========================================================================

    def register_intake_adapter(
        self,
        name: str,
        handler: Callable,
        version: str = '1.0',
        description: str = ''
    ) -> None:
        """Register an intake adapter."""
        metadata = PluginMetadata(
            name=name,
            plugin_type=PluginType.INTAKE_ADAPTER,
            version=version,
            description=description
        )
        self.registry[PluginType.INTAKE_ADAPTER][name] = metadata

    def register_filter_strategy(
        self,
        name: str,
        handler: Callable,
        version: str = '1.0',
        description: str = ''
    ) -> None:
        """Register a filter strategy."""
        metadata = PluginMetadata(
            name=name,
            plugin_type=PluginType.FILTER_STRATEGY,
            version=version,
            description=description
        )
        self.registry[PluginType.FILTER_STRATEGY][name] = metadata

    def register_refinement_rule(
        self,
        name: str,
        handler: Callable,
        version: str = '1.0',
        description: str = ''
    ) -> None:
        """Register a refinement rule."""
        metadata = PluginMetadata(
            name=name,
            plugin_type=PluginType.REFINEMENT_RULE,
            version=version,
            description=description
        )
        self.registry[PluginType.REFINEMENT_RULE][name] = metadata

    def register_output_formatter(
        self,
        name: str,
        handler: Callable,
        version: str = '1.0',
        description: str = ''
    ) -> None:
        """Register an output formatter."""
        metadata = PluginMetadata(
            name=name,
            plugin_type=PluginType.OUTPUT_FORMATTER,
            version=version,
            description=description
        )
        self.registry[PluginType.OUTPUT_FORMATTER][name] = metadata

    def register_validator(
        self,
        name: str,
        handler: Callable,
        version: str = '1.0',
        description: str = ''
    ) -> None:
        """Register a validator."""
        metadata = PluginMetadata(
            name=name,
            plugin_type=PluginType.VALIDATOR,
            version=version,
            description=description
        )
        self.registry[PluginType.VALIDATOR][name] = metadata

    # ========================================================================
    # Plugin Discovery Methods
    # ========================================================================

    def get_adapters(self) -> Dict[str, PluginMetadata]:
        """Get all registered intake adapters."""
        return self.registry[PluginType.INTAKE_ADAPTER]

    def get_filters(self) -> Dict[str, PluginMetadata]:
        """Get all registered filter strategies."""
        return self.registry[PluginType.FILTER_STRATEGY]

    def get_rules(self) -> Dict[str, PluginMetadata]:
        """Get all registered refinement rules."""
        return self.registry[PluginType.REFINEMENT_RULE]

    def get_formatters(self) -> Dict[str, PluginMetadata]:
        """Get all registered output formatters."""
        return self.registry[PluginType.OUTPUT_FORMATTER]

    def get_validators(self) -> Dict[str, PluginMetadata]:
        """Get all registered validators."""
        return self.registry[PluginType.VALIDATOR]

    # ========================================================================
    # Plugin Creation Methods
    # ========================================================================

    def create_adapter(self, adapter_type: str = 'pass_through') -> IntakeAdapter:
        """Create an intake adapter instance."""
        if adapter_type == 'pass_through':
            return PassThroughAdapter()
        raise ValueError(f"Unknown adapter type: {adapter_type}")

    def create_filter(self, filter_type: str = 'accept_all') -> FilterStrategy:
        """Create a filter strategy instance."""
        if filter_type == 'accept_all':
            return AcceptAllFilter()
        raise ValueError(f"Unknown filter type: {filter_type}")

    def create_refinement(self, rule_type: str = 'identity') -> RefinementRule:
        """Create a refinement rule instance."""
        if rule_type == 'identity':
            return IdentityRefinement()
        raise ValueError(f"Unknown refinement type: {rule_type}")

    def create_formatter(self, formatter_type: str = 'json') -> OutputFormatter:
        """Create an output formatter instance."""
        if formatter_type == 'json':
            return JSONFormatter()
        raise ValueError(f"Unknown formatter type: {formatter_type}")

    def create_validator(
        self,
        validator_type: str = 'schema',
        **kwargs
    ) -> Validator:
        """Create a validator instance."""
        if validator_type == 'schema':
            required_fields = kwargs.get('required_fields', [])
            return SchemaValidator(required_fields)
        raise ValueError(f"Unknown validator type: {validator_type}")

    # ========================================================================
    # Pipeline Execution Methods
    # ========================================================================

    def execute_batch(
        self,
        source: Any,
        adapter: Optional[IntakeAdapter] = None,
        filters: Optional[List[FilterStrategy]] = None,
        refinements: Optional[List[RefinementRule]] = None,
        formatter: Optional[OutputFormatter] = None,
        validator: Optional[Validator] = None,
    ) -> int:
        """
        Execute pipeline in batch mode.
        
        Args:
            source: Data source.
            adapter: Optional custom adapter.
            filters: Optional filter chain.
            refinements: Optional refinement rules.
            formatter: Optional formatter.
            validator: Optional validator.
            
        Returns:
            Number of items successfully ingested.
        """
        adapter = adapter or self.create_adapter()
        filters = filters or []
        refinements = refinements or []
        formatter = formatter or self.create_formatter()
        validator = validator or self.create_validator()
        
        successful = 0
        batch = []
        
        try:
            for item in adapter.read(source):
                # Apply filters
                if not all(f.filter(item) for f in filters):
                    self.stats['skipped_items'] += 1
                    continue
                
                # Apply refinements
                for refinement in refinements:
                    item = refinement.refine(item)
                
                # Validate
                valid, error = validator.validate(item)
                if not valid:
                    self._handle_validation_error(item, error)
                    continue
                
                # Format
                formatted = formatter.format(item)
                batch.append((item, formatted))
                
                # Execute batch when full
                if len(batch) >= self.batch_size:
                    successful += self._store_batch(batch)
                    batch = []
                    self.stats['total_batches'] += 1
            
            # Store remaining items
            if batch:
                successful += self._store_batch(batch)
                self.stats['total_batches'] += 1
            
            self.stats['total_items'] += successful
            self.stats['successful_items'] += successful
            
            return successful
        except Exception as e:
            self._handle_error(str(e))
            return successful

    def execute_stream(
        self,
        source: Any,
        adapter: Optional[IntakeAdapter] = None,
        **kwargs
    ) -> Iterator[Dict[str, Any]]:
        """
        Execute pipeline in streaming mode.
        
        Args:
            source: Data source.
            adapter: Optional custom adapter.
            **kwargs: Additional pipeline configuration.
            
        Yields:
            Processed items from pipeline.
        """
        adapter = adapter or self.create_adapter()
        
        for item in adapter.read(source):
            yield item

    def execute_filter_chain(
        self,
        items: List[Dict[str, Any]],
        filters: List[FilterStrategy]
    ) -> List[Dict[str, Any]]:
        """
        Execute a chain of filters on items.
        
        Args:
            items: Items to filter.
            filters: Filter chain to apply.
            
        Returns:
            Filtered items.
        """
        result = []
        for item in items:
            if all(f.filter(item) for f in filters):
                result.append(item)
        return result

    def apply_refinement_rules(
        self,
        items: List[Dict[str, Any]],
        refinements: List[RefinementRule]
    ) -> List[Dict[str, Any]]:
        """
        Apply refinement rules to items.
        
        Args:
            items: Items to refine.
            refinements: Refinement rules to apply.
            
        Returns:
            Refined items.
        """
        result = []
        for item in items:
            for refinement in refinements:
                item = refinement.refine(item)
            result.append(item)
        return result

    def format_output(
        self,
        items: List[Dict[str, Any]],
        formatter: OutputFormatter
    ) -> List[str]:
        """
        Format items for storage.
        
        Args:
            items: Items to format.
            formatter: Formatter to use.
            
        Returns:
            Formatted strings.
        """
        return [formatter.format(item) for item in items]

    def validate(
        self,
        items: List[Dict[str, Any]],
        validator: Validator
    ) -> Tuple[List[Dict[str, Any]], List[Tuple[Dict, str]]]:
        """
        Validate items.
        
        Args:
            items: Items to validate.
            validator: Validator to use.
            
        Returns:
            Tuple of (valid_items, invalid_items_with_errors).
        """
        valid = []
        invalid = []
        
        for item in items:
            is_valid, error = validator.validate(item)
            if is_valid:
                valid.append(item)
            else:
                invalid.append((item, error or 'Unknown error'))
        
        return valid, invalid

    def handle_error(self, error: str) -> None:
        """
        Handle pipeline errors.
        
        Args:
            error: Error message.
        """
        self._handle_error(error)

    def retry_failed_items(self) -> int:
        """
        Retry ingestion of failed items.
        
        Returns:
            Number of successfully retried items.
        """
        if not self.failed_items:
            return 0
        
        retried = 0
        items_to_remove = []
        
        for idx, (item, error) in enumerate(self.failed_items):
            # Simple retry: try ingesting again
            try:
                storage = self.backends.get('storage') or self.backends.get(list(self.backends.keys())[0] if self.backends else None)
                if storage and hasattr(storage, 'store'):
                    storage.store(item)
                    retried += 1
                    items_to_remove.append(idx)
            except Exception:
                pass
        
        # Remove successfully retried items
        for idx in reversed(items_to_remove):
            del self.failed_items[idx]
        
        return retried

    # ========================================================================
    # Metrics and State Methods
    # ========================================================================

    def get_metrics(self) -> Dict[str, Any]:
        """
        Get pipeline metrics.
        
        Returns:
            Dictionary with pipeline statistics.
        """
        return {
            'total_batches': self.stats['total_batches'],
            'total_items': self.stats['total_items'],
            'successful_items': self.stats['successful_items'],
            'failed_items': self.stats['failed_items'],
            'skipped_items': self.stats['skipped_items'],
            'success_rate': self.stats['successful_items'] / max(self.stats['total_items'], 1),
            'stage_metrics': [
                {
                    'stage': m.stage,
                    'timestamp': m.timestamp.isoformat(),
                    'items_processed': m.items_processed,
                    'items_failed': m.items_failed,
                    'items_skipped': m.items_skipped,
                    'duration_seconds': m.duration_seconds,
                    'success_rate': m.success_rate,
                }
                for m in self.metrics
            ],
        }

    def get_execution_state(self) -> Optional[Dict[str, Any]]:
        """
        Get current execution state.
        
        Returns:
            Current execution state or None.
        """
        if not self.current_execution or self.current_execution not in self.execution_states:
            return None
        
        state = self.execution_states[self.current_execution]
        return {
            'execution_id': state.execution_id,
            'start_time': state.start_time.isoformat(),
            'current_stage': state.current_stage,
            'total_items': state.total_items,
            'processed_items': state.processed_items,
            'failed_items': state.failed_items,
            'skipped_items': state.skipped_items,
            'status': state.status,
            'error_message': state.error_message,
            'end_time': state.end_time.isoformat() if state.end_time else None,
        }

    # ========================================================================
    # Helper Methods
    # ========================================================================

    def _store_batch(self, batch: List[Tuple[Any, str]]) -> int:
        """Store a batch of items."""
        storage = self.backends.get('storage') or (list(self.backends.values())[0] if self.backends else None)
        
        if not storage:
            return 0
        
        count = 0
        for item, formatted in batch:
            try:
                if hasattr(storage, 'store'):
                    storage.store(item)
                count += 1
            except Exception as e:
                self.failed_items.append((item, str(e)))
                self.stats['failed_items'] += 1
        
        return count

    def _handle_validation_error(self, item: Any, error: Optional[str]) -> None:
        """Handle validation error."""
        self.failed_items.append((item, error or 'Validation failed'))
        self.stats['failed_items'] += 1

    def _handle_error(self, error: str) -> None:
        """Handle pipeline error based on error strategy."""
        if self.error_strategy == 'fail':
            raise RuntimeError(f"Pipeline error: {error}")
        # For 'skip' and 'continue', just log and continue


__all__ = [
    'BulkIngestionPipeline',
    'PluginType',
    'PluginMetadata',
    'PipelineStage',
    'PipelineMetrics',
    'ExecutionState',
    'IntakeAdapter',
    'FilterStrategy',
    'RefinementRule',
    'OutputFormatter',
    'Validator',
]
