import pytest
from src.tools.archival_executor import archive_evidence_bundles

class TestEvidenceBundlesArchival:
    def test_evidence_bundles_archive(self):
        config = {'source': 'evidence/', 'destination': 'archive/'}
        result = archive_evidence_bundles(config)
        assert result['success'] is True
    
    def test_evidence_bundles_timestamp(self):
        config = {'source': 'evidence/', 'destination': 'archive/'}
        result = archive_evidence_bundles(config)
        assert 'timestamp' in result
    
    def test_evidence_bundles_count(self):
        config = {'source': 'evidence/', 'destination': 'archive/'}
        result = archive_evidence_bundles(config)
        assert 'bundles_archived' in result
