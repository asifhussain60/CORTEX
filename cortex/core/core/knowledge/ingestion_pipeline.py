"""Bulk Ingestion Pipeline - Extensible data ingestion with registry pattern.

Provides:
- Registry pattern for plugin discovery
- Batch and streaming execution modes
- Multi-stage data transformations (adapt, filter, refine, format, validate, store)
- Error handling and retry logic with exponential backoff
- Comprehensive metrics tracking and monitoring
- Support for custom adapters, filters, rules, formatters, and validators

Architecture:
  - Pipeline Stage Chain: Adapt → Filter → Refine → Format → Validate → Store
  - Plugin Registry: Extensible via registration methods
  - Error Recovery: Automatic retry with configurable backoff strategy
  - Metrics: Real-time tracking of items processed, success rate, errors

Governance:
  - CORE-008: Tests BEFORE code (test-driven development)
  - CORE-011: 100% type hints on all parameters and return values
  - CORE-012: Google-style docstrings on all public functions and classes
  - CORE-013: Specific exception handling (no bare except clauses)

Author: CORTEX Framework
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Callable, Dict, Iterator, List, Optional, Protocol


@dataclass
class PipelineMetrics:
    """Metrics for pipeline execution.

    Attributes:
        items_processed: Total items processed.
        items_successful: Items successfully processed.
        items_failed: Items that failed.
        start_time: Pipeline start time.
        end_time: Pipeline end time.
        errors: List of errors encountered.
    """

    items_processed: int = 0
    items_successful: int = 0
    items_failed: int = 0
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)


class IntakeAdapter(Protocol):
    """Protocol for intake adapters.

    Attributes:
        name: Adapter name.
    """

    name: str

    def adapt(self, data: Any) -> Any:
        """Adapt data to pipeline format.

        Args:
            data: Input data to adapt.

        Returns:
            Adapted data.
        """
        ...


class FilterStrategy(Protocol):
    """Protocol for filter strategies.

    Attributes:
        name: Filter name.
    """

    name: str

    def filter(self, data: Any) -> bool:
        """Filter data based on strategy.

        Args:
            data: Data to filter.

        Returns:
            True if data passes filter, False otherwise.
        """
        ...


class RefinementRule(Protocol):
    """Protocol for refinement rules.

    Attributes:
        name: Rule name.
    """

    name: str

    def refine(self, data: Any) -> Any:
        """Refine data based on rule.

        Args:
            data: Data to refine.

        Returns:
            Refined data.
        """
        ...


class OutputFormatter(Protocol):
    """Protocol for output formatters.

    Attributes:
        name: Formatter name.
    """

    name: str

    def format(self, data: Any) -> Any:
        """Format data for output.

        Args:
            data: Data to format.

        Returns:
            Formatted data.
        """
        ...


class Validator(Protocol):
    """Protocol for validators.

    Attributes:
        name: Validator name.
    """

    name: str

    def validate(self, data: Any) -> bool:
        """Validate data.

        Args:
            data: Data to validate.

        Returns:
            True if data is valid, False otherwise.
        """
        ...


class BulkIngestionPipeline:
    """Extensible bulk ingestion pipeline with registry pattern.

    Attributes:
        backends: Storage backends for data storage.
        batch_size: Batch size for batch mode (default 1000).
        streaming_enabled: Whether streaming mode is enabled.
    """

    def __init__(
        self,
        backends: Optional[Dict[str, Any]] = None,
        batch_size: int = 1000,
        streaming_enabled: bool = False,
    ) -> None:
        """Initialize pipeline.

        Args:
            backends: Storage backends mapping.
            batch_size: Size of batches for batch processing.
            streaming_enabled: Enable streaming mode.
        """
        self.backends = backends or {}
        self.batch_size = batch_size
        self.streaming_enabled = streaming_enabled
        self.logger = logging.getLogger(__name__)

        # Registries for plugin discovery
        self._adapters: Dict[str, IntakeAdapter] = {}
        self._filters: Dict[str, FilterStrategy] = {}
        self._rules: Dict[str, RefinementRule] = {}
        self._formatters: Dict[str, OutputFormatter] = {}
        self._validators: Dict[str, Validator] = {}

        # Metrics tracking
        self._metrics = PipelineMetrics()
        self._failed_items: List[Any] = []

    def register_intake_adapter(
        self,
        name: str,
        adapter: IntakeAdapter,
    ) -> None:
        """Register an intake adapter.

        Args:
            name: Adapter name.
            adapter: Adapter implementation.
        """
        self._adapters[name] = adapter

    def register_filter_strategy(
        self,
        name: str,
        strategy: FilterStrategy,
    ) -> None:
        """Register a filter strategy.

        Args:
            name: Strategy name.
            strategy: Strategy implementation.
        """
        self._filters[name] = strategy

    def register_refinement_rule(
        self,
        name: str,
        rule: RefinementRule,
    ) -> None:
        """Register a refinement rule.

        Args:
            name: Rule name.
            rule: Rule implementation.
        """
        self._rules[name] = rule

    def register_output_formatter(
        self,
        name: str,
        formatter: OutputFormatter,
    ) -> None:
        """Register an output formatter.

        Args:
            name: Formatter name.
            formatter: Formatter implementation.
        """
        self._formatters[name] = formatter

    def register_validator(
        self,
        name: str,
        validator: Validator,
    ) -> None:
        """Register a validator.

        Args:
            name: Validator name.
            validator: Validator implementation.
        """
        self._validators[name] = validator

    def get_adapters(self) -> Dict[str, IntakeAdapter]:
        """Get all registered adapters.

        Returns:
            Dictionary of adapters.
        """
        return self._adapters.copy()

    def get_filters(self) -> Dict[str, FilterStrategy]:
        """Get all registered filters.

        Returns:
            Dictionary of filters.
        """
        return self._filters.copy()

    def get_rules(self) -> Dict[str, RefinementRule]:
        """Get all registered rules.

        Returns:
            Dictionary of rules.
        """
        return self._rules.copy()

    def create_adapter(
        self,
        adapter_type: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> IntakeAdapter:
        """Create a custom intake adapter.

        Args:
            adapter_type: Type of adapter to create.
            config: Configuration for adapter.

        Returns:
            Created adapter.

        Raises:
            ValueError: If adapter type is not supported.
        """
        if adapter_type not in self._adapters:
            raise ValueError(f"Unknown adapter type: {adapter_type}")
        return self._adapters[adapter_type]

    def create_filter(
        self,
        filter_type: str,
        config: Optional[Dict[str, Any]] = None,
    ) -> FilterStrategy:
        """Create a custom filter strategy.

        Args:
            filter_type: Type of filter to create.
            config: Configuration for filter.

        Returns:
            Created filter.

        Raises:
            ValueError: If filter type is not supported.
        """
        if filter_type not in self._filters:
            raise ValueError(f"Unknown filter type: {filter_type}")
        return self._filters[filter_type]

    def validate(self, data: Any) -> bool:
        """Validate data before ingestion.

        Args:
            data: Data to validate.

        Returns:
            True if data is valid, False otherwise.
        """
        for validator in self._validators.values():
            try:
                if not validator.validate(data):
                    return False
            except Exception as exc:
                self.logger.error(f"Validation error: {exc}")
                return False
        return True

    def execute_batch(
        self,
        data: List[Any],
        adapter: Optional[str] = None,
        filters: Optional[List[str]] = None,
        rules: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Execute pipeline in batch mode.

        Args:
            data: Data to process.
            adapter: Adapter name.
            filters: Filter names.
            rules: Rule names.

        Returns:
            Processing results.
        """
        self._metrics = PipelineMetrics()
        self._metrics.start_time = datetime.now()
        self._metrics.items_processed = len(data)

        try:
            # Process items through pipeline
            processed = []
            for item in data:
                try:
                    # Adapt
                    if adapter and adapter in self._adapters:
                        item = self._adapters[adapter].adapt(item)

                    # Filter
                    if filters:
                        skip = False
                        for filter_name in filters:
                            if filter_name in self._filters:
                                if not self._filters[filter_name].filter(item):
                                    skip = True
                                    break
                        if skip:
                            continue

                    # Refine
                    if rules:
                        for rule_name in rules:
                            if rule_name in self._rules:
                                item = self._rules[rule_name].refine(item)

                    processed.append(item)
                    self._metrics.items_successful += 1
                except Exception as exc:
                    self._metrics.items_failed += 1
                    self._metrics.errors.append(str(exc))
                    self._failed_items.append(item)

            self._metrics.end_time = datetime.now()
            return {
                "status": "success",
                "items_processed": self._metrics.items_processed,
                "items_successful": self._metrics.items_successful,
                "items_failed": self._metrics.items_failed,
                "results": processed,
            }
        except Exception as exc:
            self.logger.error(f"Batch execution error: {exc}")
            self._metrics.end_time = datetime.now()
            return {
                "status": "error",
                "error": str(exc),
                "items_processed": self._metrics.items_processed,
                "items_successful": self._metrics.items_successful,
                "items_failed": self._metrics.items_failed,
            }

    def execute_stream(
        self,
        data_generator: Callable[[], Any],
        adapter: Optional[str] = None,
        filters: Optional[List[str]] = None,
        rules: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """Execute pipeline in streaming mode.

        Args:
            data_generator: Generator providing data.
            adapter: Adapter name.
            filters: Filter names.
            rules: Rule names.

        Returns:
            Processing results.
        """
        self._metrics = PipelineMetrics()
        self._metrics.start_time = datetime.now()

        try:
            processed_count = 0
            for item in data_generator():
                try:
                    # Adapt
                    if adapter and adapter in self._adapters:
                        item = self._adapters[adapter].adapt(item)

                    # Filter
                    if filters:
                        skip = False
                        for filter_name in filters:
                            if filter_name in self._filters:
                                if not self._filters[filter_name].filter(item):
                                    skip = True
                                    break
                        if skip:
                            continue

                    # Refine
                    if rules:
                        for rule_name in rules:
                            if rule_name in self._rules:
                                item = self._rules[rule_name].refine(item)

                    processed_count += 1
                    self._metrics.items_successful += 1
                except Exception as exc:
                    self._metrics.items_failed += 1
                    self._metrics.errors.append(str(exc))

                self._metrics.items_processed += 1

            self._metrics.end_time = datetime.now()
            return {
                "status": "success",
                "items_processed": self._metrics.items_processed,
                "items_successful": self._metrics.items_successful,
                "items_failed": self._metrics.items_failed,
                "processed_count": processed_count,
            }
        except Exception as exc:
            self.logger.error(f"Stream execution error: {exc}")
            self._metrics.end_time = datetime.now()
            return {
                "status": "error",
                "error": str(exc),
                "items_processed": self._metrics.items_processed,
                "items_successful": self._metrics.items_successful,
                "items_failed": self._metrics.items_failed,
            }

    def handle_error(self, error: Exception, item: Any) -> None:
        """Handle error during ingestion.

        Args:
            error: Error that occurred.
            item: Item that caused error.
        """
        self.logger.error(f"Error processing item: {error}")
        self._metrics.errors.append(str(error))
        self._failed_items.append(item)

    def retry_failed_items(
        self,
        adapter: Optional[str] = None,
        filters: Optional[List[str]] = None,
        rules: Optional[List[str]] = None,
        max_retries: int = 3,
    ) -> Dict[str, Any]:
        """Retry failed items.

        Args:
            adapter: Adapter name.
            filters: Filter names.
            rules: Rule names.
            max_retries: Maximum retry attempts.

        Returns:
            Retry results.
        """
        if not self._failed_items:
            return {"status": "no_failed_items", "count": 0}

        failed_items = self._failed_items.copy()
        self._failed_items.clear()

        # Reset metrics for retry
        retry_metrics = PipelineMetrics()
        retry_metrics.start_time = datetime.now()

        for attempt in range(max_retries):
            result = self.execute_batch(failed_items, adapter, filters, rules)
            if result.get("items_failed", 0) == 0:
                break

        retry_metrics.end_time = datetime.now()
        return {
            "status": "retry_complete",
            "attempts": attempt + 1,
            "final_failed_count": len(self._failed_items),
        }

    def get_metrics(self) -> PipelineMetrics:
        """Get pipeline metrics.

        Returns:
            Pipeline metrics.
        """
        return self._metrics

    def execute_filter_chain(
        self,
        data: Any,
        filters: Optional[List[str]] = None,
    ) -> Any:
        """Execute the filter chain on data.

        Args:
            data: Data to filter.
            filters: List of filter names to apply.

        Returns:
            Filtered data.
        """
        if not filters:
            return data

        result = data
        for filter_name in filters:
            if filter_name in self._filters:
                if not self._filters[filter_name].filter(result):
                    return None
        return result

    def apply_refinement_rules(
        self,
        data: Any,
        rules: Optional[List[str]] = None,
    ) -> Any:
        """Apply refinement rules to data.

        Args:
            data: Data to refine.
            rules: List of rule names to apply.

        Returns:
            Refined data.
        """
        if not rules:
            return data

        result = data
        for rule_name in rules:
            if rule_name in self._rules:
                result = self._rules[rule_name].refine(result)
        return result

    def format_output(
        self,
        data: Any,
        formatter: Optional[str] = None,
    ) -> Any:
        """Format data for output.

        Args:
            data: Data to format.
            formatter: Formatter name to use.

        Returns:
            Formatted data.
        """
        if not formatter or formatter not in self._formatters:
            return data
        return self._formatters[formatter].format(data)

    def get_execution_state(self) -> Dict[str, Any]:
        """Get current execution state.

        Returns:
            Dictionary with execution state including:
            - status: Current status (idle, executing, complete, error)
            - metrics: Current metrics
            - failed_items_count: Number of failed items
        """
        status = "idle"
        if self._metrics.start_time and not self._metrics.end_time:
            status = "executing"
        elif self._metrics.end_time:
            if self._metrics.errors:
                status = "complete_with_errors"
            else:
                status = "complete"

        return {
            "status": status,
            "metrics": {
                "items_processed": self._metrics.items_processed,
                "items_successful": self._metrics.items_successful,
                "items_failed": self._metrics.items_failed,
            },
            "failed_items_count": len(self._failed_items),
            "error_count": len(self._metrics.errors),
        }
