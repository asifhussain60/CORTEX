"""
Performance tests and benchmarks for CORTEX system.

This package contains performance benchmarks and load tests for:
- Mediator throughput and latency
- Repository operations (read/write)
- Search and query performance
- End-to-end workflow scenarios

Benchmarks use pytest-benchmark for accurate measurements.
Target metrics:
- Mediator: <50ms p95 latency
- Repository reads: <10ms average
- Repository writes: <20ms average
- Search operations: <200ms for semantic search
"""
