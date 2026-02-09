# AC_START: AC-PHASE59-S3-001
# Tests for Repository Fingerprinting (Phase 59, Stage 3)
# Purpose: Validate fast repository architecture fingerprinting

import pytest
import numpy as np
from pathlib import Path
from cortex.lens.ml_patterns.repository_fingerprinting import (
    RepositoryFingerprinter,
    RepositoryFingerprint,
    FingerprintComponent,
)


class TestRepositoryFingerprint:
    """Test suite for repository fingerprint structure."""
    
    def test_create_fingerprint(self):
        """T1: Create repository fingerprint with components."""
        components = [
            FingerprintComponent(
                name="api",
                complexity=0.7,
                size=1500,
                modularity=0.85,
            ),
            FingerprintComponent(
                name="core",
                complexity=0.6,
                size=2000,
                modularity=0.80,
            ),
        ]
        
        fingerprint = RepositoryFingerprint(
            repository_id="test-repo",
            components=components,
            total_complexity=0.65,
            total_modularity=0.825,
        )
        
        assert fingerprint.repository_id == "test-repo"
        assert len(fingerprint.components) == 2
        assert fingerprint.total_complexity == 0.65
    
    def test_fingerprint_to_vector(self):
        """T2: Convert fingerprint to feature vector."""
        components = [
            FingerprintComponent("api", 0.7, 1500, 0.85),
            FingerprintComponent("core", 0.6, 2000, 0.80),
        ]
        
        fingerprint = RepositoryFingerprint(
            repository_id="test-repo",
            components=components,
            total_complexity=0.65,
            total_modularity=0.825,
        )
        
        vector = fingerprint.to_vector()
        
        assert isinstance(vector, np.ndarray)
        assert len(vector) > 0
        assert np.all((vector >= 0) & (vector <= 1))


class TestRepositoryFingerprinter:
    """Test suite for repository fingerprinting engine."""
    
    def test_initialize_fingerprinter(self):
        """T3: Initialize repository fingerprinter."""
        fingerprinter = RepositoryFingerprinter()
        
        assert fingerprinter is not None
        assert hasattr(fingerprinter, "generate_fingerprint")
    
    def test_generate_fingerprint_from_features(self):
        """T4: Generate fingerprint from extracted features."""
        fingerprinter = RepositoryFingerprinter()
        
        # Mock repository features
        repo_features = {
            "components": ["api", "core", "utils"],
            "avg_complexity": 0.65,
            "total_size": 5500,
            "avg_modularity": 0.82,
        }
        
        fingerprint = fingerprinter.generate_fingerprint(
            repository_id="test-repo",
            features=repo_features,
        )
        
        assert isinstance(fingerprint, RepositoryFingerprint)
        assert fingerprint.repository_id == "test-repo"
        assert len(fingerprint.components) > 0
    
    def test_fingerprint_consistency(self):
        """T5: Fingerprints are consistent for same input."""
        fingerprinter = RepositoryFingerprinter()
        
        repo_features = {
            "components": ["api", "core"],
            "avg_complexity": 0.65,
            "total_size": 3500,
            "avg_modularity": 0.82,
        }
        
        fp1 = fingerprinter.generate_fingerprint("repo1", repo_features)
        fp2 = fingerprinter.generate_fingerprint("repo1", repo_features)
        
        # Fingerprints should be identical (same input)
        assert np.allclose(fp1.to_vector(), fp2.to_vector())
    
    def test_fingerprint_hash(self):
        """T6: Generate hash fingerprint for fast comparison."""
        fingerprinter = RepositoryFingerprinter()
        
        repo_features = {
            "components": ["api", "core"],
            "avg_complexity": 0.65,
            "total_size": 3500,
            "avg_modularity": 0.82,
        }
        
        fingerprint = fingerprinter.generate_fingerprint("repo1", repo_features)
        fp_hash = fingerprinter.hash_fingerprint(fingerprint)
        
        assert isinstance(fp_hash, str)
        assert len(fp_hash) > 0
    
    def test_fingerprint_comparison(self):
        """T7: Compare two repository fingerprints."""
        fingerprinter = RepositoryFingerprinter()
        
        # Create two similar fingerprints
        features1 = {
            "components": ["api", "core"],
            "avg_complexity": 0.65,
            "total_size": 3500,
            "avg_modularity": 0.82,
        }
        
        features2 = {
            "components": ["api", "core", "utils"],
            "avg_complexity": 0.66,
            "total_size": 3600,
            "avg_modularity": 0.81,
        }
        
        fp1 = fingerprinter.generate_fingerprint("repo1", features1)
        fp2 = fingerprinter.generate_fingerprint("repo2", features2)
        
        similarity = fingerprinter.compare_fingerprints(fp1, fp2)
        
        assert 0 <= similarity <= 1
        assert similarity > 0.8  # Should be similar
    
    def test_distinct_fingerprints(self):
        """T8: Different repos produce distinct fingerprints."""
        fingerprinter = RepositoryFingerprinter()
        
        # Very different features
        features1 = {
            "components": ["api"],
            "avg_complexity": 0.3,
            "total_size": 500,
            "avg_modularity": 0.95,
        }
        
        features2 = {
            "components": ["monolith"],
            "avg_complexity": 0.9,
            "total_size": 50000,
            "avg_modularity": 0.2,
        }
        
        fp1 = fingerprinter.generate_fingerprint("repo1", features1)
        fp2 = fingerprinter.generate_fingerprint("repo2", features2)
        
        similarity = fingerprinter.compare_fingerprints(fp1, fp2)
        
        assert similarity < 0.55  # Should be different (allow some margin)
    
    def test_fingerprint_batch_generation(self):
        """T9: Generate fingerprints for batch of repositories."""
        fingerprinter = RepositoryFingerprinter()
        
        repos = {
            "repo1": {
                "components": ["api", "core"],
                "avg_complexity": 0.65,
                "total_size": 3500,
                "avg_modularity": 0.82,
            },
            "repo2": {
                "components": ["web", "api"],
                "avg_complexity": 0.70,
                "total_size": 4000,
                "avg_modularity": 0.78,
            },
        }
        
        fingerprints = fingerprinter.generate_batch_fingerprints(repos)
        
        assert len(fingerprints) == 2
        assert "repo1" in fingerprints
        assert "repo2" in fingerprints
    
    def test_fingerprint_dimension_consistency(self):
        """T10: All fingerprints have consistent dimension."""
        fingerprinter = RepositoryFingerprinter()
        
        repos = {
            "repo1": {
                "components": ["api"],
                "avg_complexity": 0.5,
                "total_size": 1000,
                "avg_modularity": 0.9,
            },
            "repo2": {
                "components": ["api", "core", "utils", "web"],
                "avg_complexity": 0.7,
                "total_size": 10000,
                "avg_modularity": 0.7,
            },
        }
        
        fingerprints = fingerprinter.generate_batch_fingerprints(repos)
        
        dims = [len(fp.to_vector()) for fp in fingerprints.values()]
        
        # All dimensions should be the same
        assert len(set(dims)) == 1


# AC_COMPLETE: AC-PHASE59-S3-001 ✅ 10/10 tests
