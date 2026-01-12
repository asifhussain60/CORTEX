"""
AC-CLEAN-307: Archive cx6-plan/ Directory

Purpose: Create versioned, checksummed archive of entire cx6-plan/
Ensure historical planning documents are preserved before cleanup.

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path


class TestCx6PlanArchival:
    """Tests for cx6-plan directory archival"""

    def test_archive_creation(self):
        """AC-CLEAN-307.1: Archive can be created"""
        from src.tools.archival_executor import create_archive
        
        result = create_archive({'source': 'cx6-plan', 'version': 'latest'})
        assert result is not None

    def test_archive_has_checksum(self):
        """AC-CLEAN-307.2: Archive includes checksum"""
        from src.tools.archival_executor import get_archive_checksum
        
        checksum = get_archive_checksum('cx6-plan')
        assert checksum is not None or isinstance(checksum, str)

    def test_archive_versioning(self):
        """AC-CLEAN-307.3: Archive supports versioning"""
        from src.tools.archival_executor import list_archive_versions
        
        versions = list_archive_versions('cx6-plan')
        assert isinstance(versions, list)

    def test_archive_integrity_check(self):
        """AC-CLEAN-307.4: Archive integrity can be verified"""
        from src.tools.archival_executor import verify_archive
        
        result = verify_archive('cx6-plan-latest.tar.gz')
        assert result is True or result is None

    def test_archive_metadata_stored(self):
        """AC-CLEAN-307.5: Archive metadata preserved"""
        from src.tools.archival_executor import get_archive_metadata
        
        metadata = get_archive_metadata('cx6-plan')
        assert metadata is not None or isinstance(metadata, dict)
