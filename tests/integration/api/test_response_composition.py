"""
Tests for Response Composition - Multi-source aggregation and formatting.

Tests cover:
- ResponseComposer: Different composition strategies
- ResponseAggregator: Combining multiple sources
- ResponseFormatter: Format conversion (JSON, XML, HTML, etc.)
- ResponseValidator: Response quality validation
- Integration: End-to-end response composition
"""

import pytest
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json
from datetime import datetime


class CompositionStrategy(Enum):
    """Response composition strategies."""
    SEQUENTIAL = "sequential"
    PARALLEL = "parallel"
    MERGE = "merge"
    PRIORITY = "priority"


class ResponseFormat(Enum):
    """Supported response formats."""
    JSON = "json"
    XML = "xml"
    HTML = "html"
    PLAIN_TEXT = "plain_text"
    MARKDOWN = "markdown"


@dataclass
class ResponseMetadata:
    """Metadata about a response."""
    source: str
    timestamp: datetime = field(default_factory=datetime.now)
    status_code: int = 200
    latency_ms: float = 0.0


@dataclass
class Response:
    """Individual response from a source."""
    data: Dict[str, Any]
    metadata: ResponseMetadata
    source: str = ""


class ResponseComposer:
    """Base class for response composition strategies."""

    def __init__(self, strategy: CompositionStrategy):
        """Initialize response composer.
        
        Args:
            strategy: Composition strategy to use.
        """
        self.strategy = strategy
        self._responses: List[Response] = []

    def add_response(self, response: Response) -> None:
        """Add a response to compose.
        
        Args:
            response: Response to add.
        """
        self._responses.append(response)

    def compose(self) -> Dict[str, Any]:
        """Compose responses according to strategy.
        
        Returns:
            Composed response.
        """
        if self.strategy == CompositionStrategy.SEQUENTIAL:
            return self._compose_sequential()
        elif self.strategy == CompositionStrategy.PARALLEL:
            return self._compose_parallel()
        elif self.strategy == CompositionStrategy.MERGE:
            return self._compose_merge()
        elif self.strategy == CompositionStrategy.PRIORITY:
            return self._compose_priority()
        return {}

    def _compose_sequential(self) -> Dict[str, Any]:
        """Compose responses sequentially."""
        result = {"responses": []}
        for response in self._responses:
            result["responses"].append({
                "source": response.metadata.source,
                "data": response.data,
                "status_code": response.metadata.status_code,
                "latency_ms": response.metadata.latency_ms,
            })
        return result

    def _compose_parallel(self) -> Dict[str, Any]:
        """Compose responses as parallel execution."""
        return {
            "composition_type": "parallel",
            "response_count": len(self._responses),
            "total_latency_ms": sum(r.metadata.latency_ms for r in self._responses),
            "responses": [r.data for r in self._responses],
        }

    def _compose_merge(self) -> Dict[str, Any]:
        """Merge responses into single response."""
        merged = {}
        for response in self._responses:
            merged.update(response.data)
        return {"merged_data": merged}

    def _compose_priority(self) -> Dict[str, Any]:
        """Select response based on priority."""
        if not self._responses:
            return {}
        # Return first response (highest priority)
        return self._responses[0].data


class ResponseAggregator:
    """Aggregates responses from multiple sources."""

    def __init__(self):
        """Initialize aggregator."""
        self._responses: List[Response] = []
        self._aggregation_time = 0.0

    def add_response(self, response: Response) -> None:
        """Add response to aggregation.
        
        Args:
            response: Response to add.
        """
        self._responses.append(response)

    def aggregate(self) -> Dict[str, Any]:
        """Aggregate all responses.
        
        Returns:
            Aggregated response data.
        """
        if not self._responses:
            return {}

        # Collect data from all sources
        aggregated: Dict[str, Any] = {
            "source_count": len(self._responses),
            "sources": {},
            "combined_data": {},
            "aggregation_metadata": {
                "timestamp": datetime.now().isoformat(),
                "total_latency_ms": sum(r.metadata.latency_ms for r in self._responses),
                "avg_latency_ms": (
                    sum(r.metadata.latency_ms for r in self._responses) / len(self._responses)
                    if self._responses else 0.0
                ),
            }
        }

        # Add individual responses
        for response in self._responses:
            aggregated["sources"][response.metadata.source] = {
                "data": response.data,
                "status_code": response.metadata.status_code,
                "latency_ms": response.metadata.latency_ms,
            }
            # Merge data
            combined: Dict[str, Any] = aggregated.get("combined_data", {})
            combined.update(response.data)
            aggregated["combined_data"] = combined

        return aggregated

    def get_aggregation_stats(self) -> Dict[str, Any]:
        """Get aggregation statistics.
        
        Returns:
            Statistics about aggregation.
        """
        return {
            "response_count": len(self._responses),
            "successful_responses": len([r for r in self._responses if r.metadata.status_code == 200]),
            "avg_latency_ms": (
                sum(r.metadata.latency_ms for r in self._responses) / len(self._responses)
                if self._responses else 0.0
            ),
            "max_latency_ms": max((r.metadata.latency_ms for r in self._responses), default=0.0),
            "min_latency_ms": min((r.metadata.latency_ms for r in self._responses), default=0.0),
        }


class ResponseFormatter:
    """Formats responses in different output formats."""

    def __init__(self):
        """Initialize formatter."""
        pass

    def format(
        self, data: Dict[str, Any], format_type: ResponseFormat
    ) -> str:
        """Format data in specified format.
        
        Args:
            data: Data to format.
            format_type: Output format.
            
        Returns:
            Formatted string.
        """
        if format_type == ResponseFormat.JSON:
            return self._format_json(data)
        elif format_type == ResponseFormat.XML:
            return self._format_xml(data)
        elif format_type == ResponseFormat.HTML:
            return self._format_html(data)
        elif format_type == ResponseFormat.PLAIN_TEXT:
            return self._format_plain_text(data)
        elif format_type == ResponseFormat.MARKDOWN:
            return self._format_markdown(data)
        return str(data)

    def _format_json(self, data: Dict[str, Any]) -> str:
        """Format as JSON."""
        return json.dumps(data, indent=2, default=str)

    def _format_xml(self, data: Dict[str, Any]) -> str:
        """Format as XML."""
        lines = ['<?xml version="1.0" encoding="UTF-8"?>']
        lines.append('<root>')
        for key, value in data.items():
            lines.append(f"  <{key}>{value}</{key}>")
        lines.append('</root>')
        return '\n'.join(lines)

    def _format_html(self, data: Dict[str, Any]) -> str:
        """Format as HTML."""
        lines = ['<html>', '<body>']
        for key, value in data.items():
            lines.append(f"<p><strong>{key}:</strong> {value}</p>")
        lines.extend(['</body>', '</html>'])
        return '\n'.join(lines)

    def _format_plain_text(self, data: Dict[str, Any]) -> str:
        """Format as plain text."""
        lines: List[str] = []
        for key, value in data.items():
            lines.append(f"{key}: {value}")
        return '\n'.join(lines)

    def _format_markdown(self, data: Dict[str, Any]) -> str:
        """Format as markdown."""
        lines: List[str] = []
        for key, value in data.items():
            lines.append(f"**{key}:** {value}")
        return '\n'.join(lines)


class ResponseValidator:
    """Validates response quality and completeness."""

    def __init__(self):
        """Initialize validator."""
        pass

    def validate(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Validate response.
        
        Args:
            response: Response to validate.
            
        Returns:
            Validation results.
        """
        checks: Dict[str, bool] = {}
        issues: List[str] = []

        # Check completeness
        checks["completeness"] = self._check_completeness(response)
        
        # Check consistency
        checks["consistency"] = self._check_consistency(response)
        
        # Check security
        checks["security"] = self._check_security(response)
        
        # Determine overall validity
        is_valid = all(checks.values()) and len(issues) == 0
        
        results: Dict[str, Any] = {
            "is_valid": is_valid,
            "checks": checks,
            "issues": issues,
        }

        return results

    def _check_completeness(self, response: Dict[str, Any]) -> bool:
        """Check if response is complete.
        
        Args:
            response: Response to check.
            
        Returns:
            True if complete, False otherwise.
        """
        # A response is complete if it has content
        return len(response) > 0

    def _check_consistency(self, response: Dict[str, Any]) -> bool:
        """Check if response is consistent.
        
        Args:
            response: Response to check.
            
        Returns:
            True if consistent, False otherwise.
        """
        # All values should be present and valid
        return all(v is not None for v in response.values())

    def _check_security(self, response: Dict[str, Any]) -> bool:
        """Check security aspects of response.
        
        Args:
            response: Response to check.
            
        Returns:
            True if secure, False otherwise.
        """
        # Check for sensitive data patterns (simplified)
        response_str = str(response).lower()
        sensitive_patterns = ["password", "secret", "token"]
        for pattern in sensitive_patterns:
            if pattern in response_str:
                return False
        return True


# Tests

class TestResponseComposer:
    """Tests for ResponseComposer."""

    def test_composer_sequential_strategy(self) -> None:
        """Test sequential composition."""
        composer = ResponseComposer(CompositionStrategy.SEQUENTIAL)
        
        response1 = Response(
            data={"key1": "value1"},
            metadata=ResponseMetadata(source="source1", latency_ms=100.0),
            source="source1"
        )
        response2 = Response(
            data={"key2": "value2"},
            metadata=ResponseMetadata(source="source2", latency_ms=150.0),
            source="source2"
        )
        
        composer.add_response(response1)
        composer.add_response(response2)
        
        result = composer.compose()
        assert "responses" in result
        assert len(result["responses"]) == 2

    def test_composer_parallel_strategy(self) -> None:
        """Test parallel composition."""
        composer = ResponseComposer(CompositionStrategy.PARALLEL)
        
        response1 = Response(
            data={"data": "value1"},
            metadata=ResponseMetadata(source="source1", latency_ms=100.0),
        )
        composer.add_response(response1)
        
        result = composer.compose()
        assert result["composition_type"] == "parallel"
        assert result["response_count"] == 1

    def test_composer_merge_strategy(self) -> None:
        """Test merge composition."""
        composer = ResponseComposer(CompositionStrategy.MERGE)
        
        response1 = Response(
            data={"key1": "value1"},
            metadata=ResponseMetadata(source="source1"),
        )
        response2 = Response(
            data={"key2": "value2"},
            metadata=ResponseMetadata(source="source2"),
        )
        
        composer.add_response(response1)
        composer.add_response(response2)
        
        result = composer.compose()
        assert "merged_data" in result
        assert "key1" in result["merged_data"]
        assert "key2" in result["merged_data"]

    def test_composer_priority_strategy(self) -> None:
        """Test priority composition."""
        composer = ResponseComposer(CompositionStrategy.PRIORITY)
        
        response1 = Response(
            data={"priority": "high"},
            metadata=ResponseMetadata(source="source1"),
        )
        response2 = Response(
            data={"priority": "low"},
            metadata=ResponseMetadata(source="source2"),
        )
        
        composer.add_response(response1)
        composer.add_response(response2)
        
        result = composer.compose()
        assert result["priority"] == "high"


class TestResponseAggregator:
    """Tests for ResponseAggregator."""

    def test_aggregator_combines_responses(self) -> None:
        """Test aggregator combines responses."""
        aggregator = ResponseAggregator()
        
        response1 = Response(
            data={"key1": "value1"},
            metadata=ResponseMetadata(source="source1", latency_ms=100.0),
        )
        response2 = Response(
            data={"key2": "value2"},
            metadata=ResponseMetadata(source="source2", latency_ms=150.0),
        )
        
        aggregator.add_response(response1)
        aggregator.add_response(response2)
        
        result = aggregator.aggregate()
        assert result["source_count"] == 2
        assert "source1" in result["sources"]
        assert "source2" in result["sources"]

    def test_aggregator_computes_statistics(self) -> None:
        """Test aggregator computes statistics."""
        aggregator = ResponseAggregator()
        
        aggregator.add_response(Response(
            data={"data": "value1"},
            metadata=ResponseMetadata(source="source1", latency_ms=100.0),
        ))
        aggregator.add_response(Response(
            data={"data": "value2"},
            metadata=ResponseMetadata(source="source2", latency_ms=200.0),
        ))
        
        stats = aggregator.get_aggregation_stats()
        assert stats["response_count"] == 2
        assert stats["successful_responses"] == 2
        assert stats["avg_latency_ms"] == 150.0


class TestResponseFormatter:
    """Tests for ResponseFormatter."""

    def test_formatter_json(self) -> None:
        """Test JSON formatting."""
        formatter = ResponseFormatter()
        data = {"key": "value", "nested": {"inner": "data"}}
        result = formatter.format(data, ResponseFormat.JSON)
        assert "key" in result
        assert "value" in result

    def test_formatter_xml(self) -> None:
        """Test XML formatting."""
        formatter = ResponseFormatter()
        data = {"key": "value"}
        result = formatter.format(data, ResponseFormat.XML)
        assert "<?xml" in result
        assert "<key>value</key>" in result

    def test_formatter_html(self) -> None:
        """Test HTML formatting."""
        formatter = ResponseFormatter()
        data = {"key": "value"}
        result = formatter.format(data, ResponseFormat.HTML)
        assert "<html>" in result
        assert "<p>" in result

    def test_formatter_plain_text(self) -> None:
        """Test plain text formatting."""
        formatter = ResponseFormatter()
        data = {"key": "value"}
        result = formatter.format(data, ResponseFormat.PLAIN_TEXT)
        assert "key: value" in result

    def test_formatter_markdown(self) -> None:
        """Test markdown formatting."""
        formatter = ResponseFormatter()
        data = {"key": "value"}
        result = formatter.format(data, ResponseFormat.MARKDOWN)
        assert "**key:**" in result


class TestResponseValidator:
    """Tests for ResponseValidator."""

    def test_validator_validates_complete_response(self) -> None:
        """Test validator validates complete response."""
        validator = ResponseValidator()
        response = {"data": "value", "status_code": 200}
        result = validator.validate(response)
        assert result["is_valid"] is True

    def test_validator_checks_completeness(self) -> None:
        """Test validator checks completeness."""
        validator = ResponseValidator()
        response = {"data": "value"}
        result = validator.validate(response)
        assert "completeness" in result["checks"]

    def test_validator_checks_security(self) -> None:
        """Test validator checks security."""
        validator = ResponseValidator()
        response = {"data": "value"}
        result = validator.validate(response)
        assert result["checks"]["security"] is True


class TestResponseCompositionIntegration:
    """Integration tests for response composition."""

    def test_composition_aggregation_integration(self) -> None:
        """Test composition and aggregation together."""
        aggregator = ResponseAggregator()
        composer = ResponseComposer(CompositionStrategy.MERGE)
        
        response1 = Response(
            data={"source1_key": "source1_value"},
            metadata=ResponseMetadata(source="source1", latency_ms=100.0),
        )
        response2 = Response(
            data={"source2_key": "source2_value"},
            metadata=ResponseMetadata(source="source2", latency_ms=200.0),
        )
        
        aggregator.add_response(response1)
        aggregator.add_response(response2)
        composer.add_response(response1)
        composer.add_response(response2)
        
        aggregated = aggregator.aggregate()
        composed = composer.compose()
        
        assert aggregated["source_count"] == 2
        assert "merged_data" in composed

    def test_full_response_pipeline(self) -> None:
        """Test full response processing pipeline."""
        # Aggregate responses
        aggregator = ResponseAggregator()
        aggregator.add_response(Response(
            data={"key1": "value1"},
            metadata=ResponseMetadata(source="source1", latency_ms=100.0),
        ))
        
        aggregated = aggregator.aggregate()
        
        # Format response
        formatter = ResponseFormatter()
        json_output = formatter.format(aggregated, ResponseFormat.JSON)
        
        # Validate response
        validator = ResponseValidator()
        validation = validator.validate(aggregated)
        
        assert validation["is_valid"] is True
        assert isinstance(json_output, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
