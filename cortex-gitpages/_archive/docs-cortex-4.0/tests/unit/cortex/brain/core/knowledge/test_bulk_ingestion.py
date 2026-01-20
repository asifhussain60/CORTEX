"""Unit tests for bulk ingestion pipeline.

Tests adapters, filters, transformers, batching, and transactions.
"""

import pytest
from typing import Any, Dict, List
from datetime import datetime

from cortex.brain.core.knowledge.bulk_ingestion import (
    IngestionStatus,
    FilterAction,
    IngestionEntry,
    ProcessingResult,
    AdapterComponent,
    FilterComponent,
    TransformerComponent,
    StandardAdapter,
    ValidationFilter,
    DuplicateFilter,
    EnrichmentTransformer,
    NormalizationTransformer,
    IngestionBatch,
    BulkIngestionStats,
    BulkIngestionPipeline,
    PipelineFactory,
)


# ============================================================================
# Test Fixtures
# ============================================================================


@pytest.fixture
def sample_entries() -> List[Dict[str, Any]]:
    """Sample entry data for testing."""
    return [
        {
            "id": "entry1",
            "title": "Test Entry 1",
            "domain": "api",
            "content": "Content 1",
        },
        {
            "id": "entry2",
            "title": "Test Entry 2",
            "domain": "security",
            "content": "Content 2",
        },
        {
            "id": "entry3",
            "title": "Test Entry 3",
            "domain": "architecture",
            "content": "Content 3",
        },
    ]


@pytest.fixture
def ingestion_entry() -> IngestionEntry:
    """Sample ingestion entry."""
    return IngestionEntry(
        id="test_entry",
        data={"title": "Test", "domain": "api"},
        source="test_adapter",
    )


@pytest.fixture
def bulk_pipeline() -> BulkIngestionPipeline:
    """Create bulk ingestion pipeline for testing."""
    return BulkIngestionPipeline(batch_size=10)


# ============================================================================
# IngestionEntry Tests
# ============================================================================


class TestIngestionEntry:
    """Tests for IngestionEntry."""

    def test_entry_creation(self) -> None:
        """Test creating an ingestion entry."""
        entry = IngestionEntry(
            id="test1",
            data={"title": "Test"},
            source="adapter",
        )

        assert entry.id == "test1"
        assert entry.source == "adapter"

    def test_entry_copy(self, ingestion_entry: IngestionEntry) -> None:
        """Test copying entry."""
        copy = ingestion_entry.copy()

        assert copy.id == ingestion_entry.id
        assert copy.data == ingestion_entry.data

        # Modify copy
        copy.data["new_field"] = "value"
        assert "new_field" not in ingestion_entry.data


# ============================================================================
# ProcessingResult Tests
# ============================================================================


class TestProcessingResult:
    """Tests for ProcessingResult."""

    def test_result_success(self, ingestion_entry: IngestionEntry) -> None:
        """Test successful processing result."""
        result = ProcessingResult(
            entry=ingestion_entry,
            success=True,
            transformed_data=ingestion_entry.data,
        )

        assert result.success is True
        assert result.error is None

    def test_result_failure(self, ingestion_entry: IngestionEntry) -> None:
        """Test failed processing result."""
        result = ProcessingResult(
            entry=ingestion_entry,
            success=False,
            error="Processing failed",
        )

        assert result.success is False
        assert result.error == "Processing failed"


# ============================================================================
# Adapter Tests
# ============================================================================


class TestStandardAdapter:
    """Tests for standard adapter."""

    def test_adapt_single_dict(self) -> None:
        """Test adapting single dictionary."""
        adapter = StandardAdapter()
        data = {"id": "entry1", "title": "Test"}

        entries = adapter.adapt(data)

        assert len(entries) == 1
        assert entries[0].id == "entry1"

    def test_adapt_list(self, sample_entries: List[Dict[str, Any]]) -> None:
        """Test adapting list of entries."""
        adapter = StandardAdapter()
        entries = adapter.adapt(sample_entries)

        assert len(entries) == 3

    def test_adapt_invalid_missing_id(self) -> None:
        """Test adapting entry without ID."""
        adapter = StandardAdapter()
        data = {"title": "No ID"}

        entries = adapter.adapt(data)

        assert len(entries) == 0

    def test_adapt_with_metadata(self) -> None:
        """Test adapting with metadata."""
        adapter = StandardAdapter()
        data = {
            "id": "entry1",
            "title": "Test",
            "_source": "custom_source",
            "_metadata": {"key": "value"},
        }

        entries = adapter.adapt(data)

        assert entries[0].source == "custom_source"
        assert entries[0].metadata["key"] == "value"


# ============================================================================
# Filter Tests
# ============================================================================


class TestValidationFilter:
    """Tests for validation filter."""

    def test_filter_valid_entry(self, ingestion_entry: IngestionEntry) -> None:
        """Test filtering valid entry."""
        filter_comp = ValidationFilter()
        action = filter_comp.filter(ingestion_entry)

        assert action == FilterAction.ACCEPT

    def test_filter_missing_required_field(self, ingestion_entry: IngestionEntry) -> None:
        """Test filtering entry missing required field."""
        filter_comp = ValidationFilter(require_fields=["domain"])
        action = filter_comp.filter(ingestion_entry)

        # Entry has domain, so should pass
        assert action == FilterAction.ACCEPT

    def test_filter_missing_field_fails(self) -> None:
        """Test filtering entry without required field."""
        entry = IngestionEntry(
            id="test",
            data={"title": "No domain"},
        )
        filter_comp = ValidationFilter(require_fields=["domain"])
        action = filter_comp.filter(entry)

        assert action == FilterAction.REJECT

    def test_filter_invalid_id(self) -> None:
        """Test filtering entry with invalid ID."""
        entry = IngestionEntry(
            id="",  # Empty ID
            data={"title": "Test"},
        )
        filter_comp = ValidationFilter()
        action = filter_comp.filter(entry)

        assert action == FilterAction.REJECT


class TestDuplicateFilter:
    """Tests for duplicate filter."""

    def test_filter_first_entry(self, ingestion_entry: IngestionEntry) -> None:
        """Test filtering first occurrence."""
        filter_comp = DuplicateFilter()
        action = filter_comp.filter(ingestion_entry)

        assert action == FilterAction.ACCEPT

    def test_filter_duplicate(self, ingestion_entry: IngestionEntry) -> None:
        """Test filtering duplicate entry."""
        filter_comp = DuplicateFilter()

        # First call
        filter_comp.filter(ingestion_entry)

        # Second call with same ID
        action = filter_comp.filter(ingestion_entry)

        assert action == FilterAction.REJECT

    def test_filter_multiple_entries(self) -> None:
        """Test filtering multiple entries."""
        filter_comp = DuplicateFilter()

        entries = [
            IngestionEntry(id="1", data={}),
            IngestionEntry(id="2", data={}),
            IngestionEntry(id="1", data={}),  # Duplicate
            IngestionEntry(id="3", data={}),
        ]

        results = [filter_comp.filter(e) for e in entries]

        assert results == [
            FilterAction.ACCEPT,
            FilterAction.ACCEPT,
            FilterAction.REJECT,
            FilterAction.ACCEPT,
        ]


# ============================================================================
# Transformer Tests
# ============================================================================


class TestEnrichmentTransformer:
    """Tests for enrichment transformer."""

    def test_enrich_entry(self, ingestion_entry: IngestionEntry) -> None:
        """Test enriching entry."""
        transformer = EnrichmentTransformer(
            enrichment_fields={"enriched": True, "source_system": "test"}
        )
        transformed = transformer.transform(ingestion_entry)

        assert transformed.data["enriched"] is True
        assert transformed.data["source_system"] == "test"

    def test_enrich_preserves_original(self, ingestion_entry: IngestionEntry) -> None:
        """Test that enrichment preserves original fields."""
        transformer = EnrichmentTransformer(enrichment_fields={"new_field": "value"})
        transformed = transformer.transform(ingestion_entry)

        # Original fields should still exist
        assert "title" in transformed.data
        assert transformed.data["domain"] == "api"


class TestNormalizationTransformer:
    """Tests for normalization transformer."""

    def test_normalize_strings(self) -> None:
        """Test normalizing string fields."""
        entry = IngestionEntry(
            id="test",
            data={"title": "  Test Title  ", "domain": "  API  "},
        )
        transformer = NormalizationTransformer()
        transformed = transformer.transform(entry)

        assert transformed.data["title"] == "test title"
        assert transformed.data["domain"] == "api"

    def test_normalize_sets_metadata(self, ingestion_entry: IngestionEntry) -> None:
        """Test that normalization sets metadata."""
        transformer = NormalizationTransformer()
        transformed = transformer.transform(ingestion_entry)

        assert transformed.metadata["normalized"] is True


# ============================================================================
# IngestionBatch Tests
# ============================================================================


class TestIngestionBatch:
    """Tests for ingestion batches."""

    def test_batch_creation(self) -> None:
        """Test creating batch."""
        entries = [IngestionEntry(id=str(i), data={}) for i in range(5)]
        batch = IngestionBatch(batch_id="BATCH-001", entries=entries)

        assert batch.batch_id == "BATCH-001"
        assert len(batch.entries) == 5
        assert batch.status == IngestionStatus.PENDING

    def test_batch_success_count(self) -> None:
        """Test counting successful entries."""
        entries = [IngestionEntry(id=str(i), data={}) for i in range(3)]
        batch = IngestionBatch(batch_id="BATCH-001", entries=entries)

        # Add results
        for entry in entries[:2]:
            batch.results.append(
                ProcessingResult(entry=entry, success=True)
            )
        batch.results.append(
            ProcessingResult(entry=entries[2], success=False, error="Failed")
        )

        assert batch.get_success_count() == 2
        assert batch.get_failure_count() == 1

    def test_batch_success_rate(self) -> None:
        """Test calculating success rate."""
        entries = [IngestionEntry(id=str(i), data={}) for i in range(10)]
        batch = IngestionBatch(batch_id="BATCH-001", entries=entries)

        # 8 successes, 2 failures
        for i in range(8):
            batch.results.append(
                ProcessingResult(entry=entries[i], success=True)
            )
        for i in range(8, 10):
            batch.results.append(
                ProcessingResult(entry=entries[i], success=False)
            )

        assert batch.get_success_rate() == 0.8


# ============================================================================
# BulkIngestionStats Tests
# ============================================================================


class TestBulkIngestionStats:
    """Tests for ingestion statistics."""

    def test_stats_initialization(self) -> None:
        """Test stats initialization."""
        stats = BulkIngestionStats()

        assert stats.total_entries == 0
        assert stats.successful == 0

    def test_stats_throughput(self) -> None:
        """Test throughput calculation."""
        stats = BulkIngestionStats(
            total_entries=3000,
            successful=2850,
            failed=150,
            duration_seconds=1.0,
        )

        assert stats.throughput == 3000.0

    def test_stats_success_rate(self) -> None:
        """Test success rate calculation."""
        stats = BulkIngestionStats(
            total_entries=100,
            successful=85,
            failed=15,
        )

        assert stats.success_rate == 0.85


# ============================================================================
# BulkIngestionPipeline Tests
# ============================================================================


class TestBulkIngestionPipeline:
    """Tests for bulk ingestion pipeline."""

    def test_pipeline_initialization(self, bulk_pipeline: BulkIngestionPipeline) -> None:
        """Test pipeline initialization."""
        assert bulk_pipeline.batch_size == 10
        assert len(bulk_pipeline.adapters) == 0

    def test_add_adapter(self, bulk_pipeline: BulkIngestionPipeline) -> None:
        """Test adding adapter."""
        adapter = StandardAdapter()
        bulk_pipeline.add_adapter(adapter)

        assert len(bulk_pipeline.adapters) == 1

    def test_add_filter(self, bulk_pipeline: BulkIngestionPipeline) -> None:
        """Test adding filter."""
        filter_comp = ValidationFilter()
        bulk_pipeline.add_filter(filter_comp)

        assert len(bulk_pipeline.filters) == 1

    def test_add_transformer(self, bulk_pipeline: BulkIngestionPipeline) -> None:
        """Test adding transformer."""
        transformer = EnrichmentTransformer()
        bulk_pipeline.add_transformer(transformer)

        assert len(bulk_pipeline.transformers) == 1

    def test_ingest_small_batch(self, bulk_pipeline: BulkIngestionPipeline, sample_entries: List[Dict[str, Any]]) -> None:
        """Test ingesting small batch."""
        stats = bulk_pipeline.ingest(sample_entries)

        assert stats.total_entries == 3

    def test_ingest_large_batch(self, bulk_pipeline: BulkIngestionPipeline) -> None:
        """Test ingesting large batch."""
        # Create 100 entries
        entries = [
            {"id": f"entry{i}", "title": f"Title {i}"}
            for i in range(100)
        ]

        stats = bulk_pipeline.ingest(entries)

        assert stats.total_entries == 100

    def test_get_stats(self, bulk_pipeline: BulkIngestionPipeline, sample_entries: List[Dict[str, Any]]) -> None:
        """Test retrieving statistics."""
        bulk_pipeline.ingest(sample_entries)
        stats = bulk_pipeline.get_stats()

        assert stats.total_entries == 3

    def test_get_batch_history(self, bulk_pipeline: BulkIngestionPipeline, sample_entries: List[Dict[str, Any]]) -> None:
        """Test retrieving batch history."""
        bulk_pipeline.ingest(sample_entries)
        history = bulk_pipeline.get_batch_history()

        assert len(history) >= 1

    def test_get_specific_batch(self, bulk_pipeline: BulkIngestionPipeline, sample_entries: List[Dict[str, Any]]) -> None:
        """Test retrieving specific batch."""
        bulk_pipeline.ingest(sample_entries)
        history = bulk_pipeline.get_batch_history()

        if history:
            batch_id = history[0].batch_id
            batch = bulk_pipeline.get_batch(batch_id)
            assert batch is not None
            assert batch.batch_id == batch_id

    def test_get_nonexistent_batch(self, bulk_pipeline: BulkIngestionPipeline) -> None:
        """Test getting non-existent batch."""
        batch = bulk_pipeline.get_batch("NONEXISTENT")

        assert batch is None


# ============================================================================
# Pipeline Factory Tests
# ============================================================================


class TestPipelineFactory:
    """Tests for pipeline factory."""

    def test_create_standard_pipeline(self) -> None:
        """Test creating standard pipeline."""
        pipeline = PipelineFactory.create_standard_pipeline()

        assert len(pipeline.adapters) >= 1
        assert len(pipeline.filters) >= 1
        assert len(pipeline.transformers) >= 1

    def test_create_custom_pipeline(self) -> None:
        """Test creating custom pipeline."""
        adapters = [StandardAdapter()]
        filters = [ValidationFilter()]
        transformers = [EnrichmentTransformer()]

        pipeline = PipelineFactory.create_custom_pipeline(
            adapters=adapters,
            filters=filters,
            transformers=transformers,
        )

        assert len(pipeline.adapters) == 1
        assert len(pipeline.filters) == 1
        assert len(pipeline.transformers) == 1

    def test_standard_pipeline_ingestion(self, sample_entries: List[Dict[str, Any]]) -> None:
        """Test ingestion with standard pipeline."""
        pipeline = PipelineFactory.create_standard_pipeline(batch_size=10)
        stats = pipeline.ingest(sample_entries)

        assert stats.total_entries == 3


# ============================================================================
# Integration Tests
# ============================================================================


class TestPipelineIntegration:
    """Integration tests for bulk ingestion."""

    def test_end_to_end_processing(self) -> None:
        """Test end-to-end processing."""
        pipeline = PipelineFactory.create_standard_pipeline()

        raw_data = [
            {"id": f"entry{i}", "title": f"Entry {i}", "domain": "api"}
            for i in range(50)
        ]

        stats = pipeline.ingest(raw_data)

        assert stats.total_entries == 50
        assert stats.throughput > 0

    def test_throughput_performance(self) -> None:
        """Test pipeline throughput performance."""
        pipeline = BulkIngestionPipeline(batch_size=1000)
        pipeline.add_adapter(StandardAdapter())
        pipeline.add_filter(DuplicateFilter())

        # Create 3000 entries
        entries = [
            {"id": f"entry{i}", "data": f"content{i}"}
            for i in range(3000)
        ]

        stats = pipeline.ingest(entries)

        # Should process at reasonable speed
        assert stats.throughput > 1000  # At least 1000 entries/sec

    def test_batch_isolation(self) -> None:
        """Test that batches are isolated."""
        pipeline = BulkIngestionPipeline(batch_size=5)

        entries1 = [
            {"id": f"batch1_entry{i}", "value": i}
            for i in range(3)
        ]
        entries2 = [
            {"id": f"batch2_entry{i}", "value": i}
            for i in range(3)
        ]

        pipeline.ingest(entries1)
        pipeline.ingest(entries2)

        history = pipeline.get_batch_history()
        assert len(history) == 2
