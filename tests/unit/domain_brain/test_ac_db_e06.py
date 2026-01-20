"""Tests for AC-DB-E06: Version Tracking & Safe Deletion.

Comprehensive test suite validating:
- Import versioning
- Subset detection
- Deletion confirmation workflow
- Version history tracking
"""

import pytest

from cortex.domain_brain.version_manager import (
    VersionedDomainManager,
    DeletionStatus,
)


class TestImportVersioning:
    """Tests for import versioning."""

    @pytest.fixture
    def manager(self) -> VersionedDomainManager:
        """Create manager fixture."""
        return VersionedDomainManager()

    def test_first_import(self, manager: VersionedDomainManager) -> None:
        """Test first import of domain."""
        entities = {"e1", "e2", "e3"}
        version = manager.import_domain("imp_1", "domain1", entities)

        assert version.import_id == "imp_1"
        assert version.domain_id == "domain1"
        assert version.entity_ids == entities
        assert version.import_size == 3
        assert version.previous_import_id is None

    def test_subsequent_import(self, manager: VersionedDomainManager) -> None:
        """Test subsequent import tracks previous."""
        entities1 = {"e1", "e2", "e3"}
        version1 = manager.import_domain("imp_1", "domain1", entities1)

        entities2 = {"e1", "e2", "e3", "e4"}
        version2 = manager.import_domain("imp_2", "domain1", entities2)

        assert version2.previous_import_id == "imp_1"
        assert version2.entity_ids == entities2

    def test_version_history_tracked(self, manager: VersionedDomainManager) -> None:
        """Test version history is tracked."""
        manager.import_domain("imp_1", "domain1", {"e1"})
        manager.import_domain("imp_2", "domain1", {"e1", "e2"})
        manager.import_domain("imp_3", "domain1", {"e1", "e2", "e3"})

        history = manager.get_version_history("domain1")

        assert len(history) == 3
        assert history[0]["import_id"] == "imp_1"
        assert history[2]["import_id"] == "imp_3"


class TestSubsetDetection:
    """Tests for subset detection."""

    @pytest.fixture
    def manager(self) -> VersionedDomainManager:
        """Create manager fixture."""
        return VersionedDomainManager()

    def test_no_subset_full_import(
        self, manager: VersionedDomainManager
    ) -> None:
        """Test full import is not detected as subset."""
        manager.import_domain("imp_1", "domain1", {"e1", "e2", "e3"})

        new_entities = {"e1", "e2", "e3", "e4", "e5"}
        is_subset = manager.detect_subset_import("domain1", new_entities)

        assert is_subset is False

    def test_subset_import_detected(self, manager: VersionedDomainManager) -> None:
        """Test subset import is detected."""
        manager.import_domain("imp_1", "domain1", {"e1", "e2", "e3", "e4", "e5"})

        new_entities = {"e1", "e2", "e3"}
        is_subset = manager.detect_subset_import("domain1", new_entities)

        assert is_subset is True

    def test_no_subset_different_entities(
        self, manager: VersionedDomainManager
    ) -> None:
        """Test different (non-subset) entities are not detected as subset."""
        manager.import_domain("imp_1", "domain1", {"e1", "e2", "e3"})

        new_entities = {"e1", "e4"}  # Not a subset
        is_subset = manager.detect_subset_import("domain1", new_entities)

        assert is_subset is False

    def test_no_subset_first_import(self, manager: VersionedDomainManager) -> None:
        """Test first import cannot be a subset."""
        new_entities = {"e1", "e2"}
        is_subset = manager.detect_subset_import("domain1", new_entities)

        assert is_subset is False


class TestDeletionWorkflow:
    """Tests for deletion confirmation workflow."""

    @pytest.fixture
    def manager(self) -> VersionedDomainManager:
        """Create manager fixture."""
        return VersionedDomainManager()

    def test_deletion_request_created(
        self, manager: VersionedDomainManager
    ) -> None:
        """Test deletion request creation."""
        entities_to_delete = {"e4", "e5"}
        request = manager.request_deletion(
            "del_1", "domain1", entities_to_delete, "Subset re-upload"
        )

        assert request.request_id == "del_1"
        assert request.domain_id == "domain1"
        assert request.status == DeletionStatus.PENDING
        assert request.entities_to_delete == entities_to_delete

    def test_deletion_confirmation(self, manager: VersionedDomainManager) -> None:
        """Test deletion confirmation."""
        manager.request_deletion("del_1", "domain1", {"e4", "e5"})

        success = manager.confirm_deletion("del_1", "admin1")

        assert success is True

        request = manager.deletion_requests["del_1"]
        assert request.status == DeletionStatus.CONFIRMED
        assert request.confirmed_by == "admin1"

    def test_deletion_revert(self, manager: VersionedDomainManager) -> None:
        """Test deletion revert."""
        manager.request_deletion("del_1", "domain1", {"e4", "e5"})
        manager.confirm_deletion("del_1")

        success = manager.revert_deletion("del_1")

        assert success is True

        request = manager.deletion_requests["del_1"]
        assert request.status == DeletionStatus.REVERTED

    def test_pending_deletions_query(self, manager: VersionedDomainManager) -> None:
        """Test querying pending deletions."""
        manager.request_deletion("del_1", "domain1", {"e4"})
        manager.request_deletion("del_2", "domain1", {"e5"})
        manager.confirm_deletion("del_2")

        pending = manager.get_pending_deletions()

        assert len(pending) == 1
        assert pending[0]["request_id"] == "del_1"

    def test_safe_deletion_workflow(
        self, manager: VersionedDomainManager
    ) -> None:
        """Test complete safe deletion workflow."""
        # Import version 1
        manager.import_domain("imp_1", "domain1", {"e1", "e2", "e3", "e4", "e5"})

        # Import version 2 is a subset
        new_entities = {"e1", "e2", "e3"}
        is_subset = manager.detect_subset_import("domain1", new_entities)
        assert is_subset is True

        # Request deletion
        entities_to_delete = {"e4", "e5"}
        request = manager.request_deletion("del_1", "domain1", entities_to_delete)
        assert request.status == DeletionStatus.PENDING

        # Confirm deletion
        manager.confirm_deletion("del_1", "admin1")
        assert manager.deletion_requests["del_1"].status == DeletionStatus.CONFIRMED


class TestStatusReporting:
    """Tests for status reporting."""

    @pytest.fixture
    def manager(self) -> VersionedDomainManager:
        """Create manager fixture."""
        return VersionedDomainManager()

    def test_status_reporting(self, manager: VersionedDomainManager) -> None:
        """Test comprehensive status reporting."""
        manager.import_domain("imp_1", "domain1", {"e1", "e2"})
        manager.import_domain("imp_2", "domain2", {"e1", "e2", "e3"})

        manager.request_deletion("del_1", "domain1", {"e2"})

        status = manager.get_status()

        assert status["domains_tracked"] == 2
        assert status["total_imports"] == 2
        assert status["pending_deletions"] == 1


class TestEdgeCases:
    """Tests for edge cases."""

    @pytest.fixture
    def manager(self) -> VersionedDomainManager:
        """Create manager fixture."""
        return VersionedDomainManager()

    def test_empty_import(self, manager: VersionedDomainManager) -> None:
        """Test import with empty entity set."""
        version = manager.import_domain("imp_1", "domain1", set())

        assert version.entity_ids == set()
        assert version.import_size == 0

    def test_multiple_domains_tracked(
        self, manager: VersionedDomainManager
    ) -> None:
        """Test tracking of multiple domains."""
        manager.import_domain("imp_1", "domain1", {"e1", "e2"})
        manager.import_domain("imp_2", "domain2", {"e1", "e2", "e3"})
        manager.import_domain("imp_3", "domain3", {"e1"})

        status = manager.get_status()

        assert status["domains_tracked"] == 3

    def test_invalid_deletion_revert(self, manager: VersionedDomainManager) -> None:
        """Test reverting non-existent deletion."""
        success = manager.revert_deletion("del_nonexistent")

        assert success is False

    def test_large_entity_set(self, manager: VersionedDomainManager) -> None:
        """Test handling of large entity sets."""
        entities = {f"entity_{i}" for i in range(1000)}
        version = manager.import_domain("imp_1", "domain1", entities)

        assert len(version.entity_ids) == 1000
        assert version.import_size == 1000

    def test_subset_with_large_set(self, manager: VersionedDomainManager) -> None:
        """Test subset detection with large entity sets."""
        large_set = {f"entity_{i}" for i in range(1000)}
        manager.import_domain("imp_1", "domain1", large_set)

        small_set = {f"entity_{i}" for i in range(100)}
        is_subset = manager.detect_subset_import("domain1", small_set)

        assert is_subset is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
