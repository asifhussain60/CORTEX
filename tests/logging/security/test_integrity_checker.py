"""
Tests for IntegrityChecker - Audit Trail Integrity Verification.

TDD Phase: RED
Tests SHA-256 checksums, tamper detection, and signature verification.
"""

import pytest
import hashlib
import json
import tempfile
from pathlib import Path
from datetime import datetime

from src.logging.security.integrity_checker import (
    IntegrityChecker,
    IntegrityViolation,
    ChecksumMismatch,
    TamperDetected,
    SignatureInvalid
)


@pytest.fixture
def temp_log_dir():
    """Create temporary directory for log files."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def integrity_checker(temp_log_dir):
    """Create IntegrityChecker instance."""
    return IntegrityChecker(log_dir=temp_log_dir)


@pytest.fixture
def sample_log_file(temp_log_dir):
    """Create a sample log file."""
    log_file = temp_log_dir / "test.log"
    content = "Test log entry\n"
    log_file.write_text(content)
    return log_file


class TestIntegrityCheckerInitialization:
    """Test IntegrityChecker initialization."""

    def test_init_creates_metadata_dir(self, temp_log_dir):
        """Should create .integrity metadata directory."""
        checker = IntegrityChecker(log_dir=temp_log_dir)
        metadata_dir = temp_log_dir / ".integrity"
        assert metadata_dir.exists()
        assert metadata_dir.is_dir()

    def test_init_with_custom_algorithm(self, temp_log_dir):
        """Should accept custom hash algorithm."""
        checker = IntegrityChecker(
            log_dir=temp_log_dir,
            algorithm="sha512"
        )
        assert checker.algorithm == "sha512"

    def test_init_default_algorithm(self, temp_log_dir):
        """Should default to SHA-256."""
        checker = IntegrityChecker(log_dir=temp_log_dir)
        assert checker.algorithm == "sha256"


class TestChecksumGeneration:
    """Test checksum generation."""

    def test_generate_checksum_for_file(self, integrity_checker, sample_log_file):
        """Should generate SHA-256 checksum for file."""
        checksum = integrity_checker.generate_checksum(sample_log_file)
        assert isinstance(checksum, str)
        assert len(checksum) == 64  # SHA-256 produces 64 hex chars

    def test_generate_checksum_empty_file(self, integrity_checker, temp_log_dir):
        """Should handle empty files."""
        empty_file = temp_log_dir / "empty.log"
        empty_file.touch()
        checksum = integrity_checker.generate_checksum(empty_file)
        # SHA-256 of empty string
        expected = hashlib.sha256(b"").hexdigest()
        assert checksum == expected

    def test_generate_checksum_nonexistent_file(self, integrity_checker, temp_log_dir):
        """Should raise FileNotFoundError for nonexistent files."""
        fake_file = temp_log_dir / "nonexistent.log"
        with pytest.raises(FileNotFoundError):
            integrity_checker.generate_checksum(fake_file)

    def test_checksum_deterministic(self, integrity_checker, sample_log_file):
        """Should generate same checksum for same content."""
        checksum1 = integrity_checker.generate_checksum(sample_log_file)
        checksum2 = integrity_checker.generate_checksum(sample_log_file)
        assert checksum1 == checksum2

    def test_checksum_different_for_modified_file(self, integrity_checker, sample_log_file):
        """Should generate different checksum when file changes."""
        checksum1 = integrity_checker.generate_checksum(sample_log_file)
        
        # Modify file
        with open(sample_log_file, "a") as f:
            f.write("Additional content\n")
        
        checksum2 = integrity_checker.generate_checksum(sample_log_file)
        assert checksum1 != checksum2


class TestChecksumStorage:
    """Test checksum metadata storage."""

    def test_store_checksum(self, integrity_checker, sample_log_file):
        """Should store checksum in metadata file."""
        checksum = integrity_checker.generate_checksum(sample_log_file)
        integrity_checker.store_checksum(sample_log_file, checksum)
        
        metadata_file = integrity_checker._get_metadata_path(sample_log_file)
        assert metadata_file.exists()

    def test_stored_metadata_format(self, integrity_checker, sample_log_file):
        """Should store metadata in JSON format with required fields."""
        checksum = integrity_checker.generate_checksum(sample_log_file)
        integrity_checker.store_checksum(sample_log_file, checksum)
        
        metadata_file = integrity_checker._get_metadata_path(sample_log_file)
        metadata = json.loads(metadata_file.read_text())
        
        assert "checksum" in metadata
        assert "algorithm" in metadata
        assert "timestamp" in metadata
        assert "file_size" in metadata
        assert metadata["checksum"] == checksum
        assert metadata["algorithm"] == "sha256"

    def test_retrieve_stored_checksum(self, integrity_checker, sample_log_file):
        """Should retrieve stored checksum."""
        original_checksum = integrity_checker.generate_checksum(sample_log_file)
        integrity_checker.store_checksum(sample_log_file, original_checksum)
        
        retrieved_checksum = integrity_checker.get_stored_checksum(sample_log_file)
        assert retrieved_checksum == original_checksum

    def test_retrieve_nonexistent_checksum(self, integrity_checker, sample_log_file):
        """Should return None for files without stored checksum."""
        retrieved = integrity_checker.get_stored_checksum(sample_log_file)
        assert retrieved is None


class TestTamperDetection:
    """Test tamper detection."""

    def test_verify_unmodified_file(self, integrity_checker, sample_log_file):
        """Should pass verification for unmodified file."""
        checksum = integrity_checker.generate_checksum(sample_log_file)
        integrity_checker.store_checksum(sample_log_file, checksum)
        
        result = integrity_checker.verify_integrity(sample_log_file)
        assert result is True

    def test_detect_modified_file(self, integrity_checker, sample_log_file):
        """Should detect file modification."""
        checksum = integrity_checker.generate_checksum(sample_log_file)
        integrity_checker.store_checksum(sample_log_file, checksum)
        
        # Tamper with file
        with open(sample_log_file, "a") as f:
            f.write("TAMPERED CONTENT\n")
        
        with pytest.raises(TamperDetected) as exc_info:
            integrity_checker.verify_integrity(sample_log_file, strict=True)
        
        assert "tampered" in str(exc_info.value).lower()

    def test_detect_truncated_file(self, integrity_checker, sample_log_file):
        """Should detect file truncation."""
        checksum = integrity_checker.generate_checksum(sample_log_file)
        integrity_checker.store_checksum(sample_log_file, checksum)
        
        # Truncate file
        sample_log_file.write_text("")
        
        with pytest.raises(TamperDetected):
            integrity_checker.verify_integrity(sample_log_file, strict=True)

    def test_verify_returns_false_in_non_strict_mode(self, integrity_checker, sample_log_file):
        """Should return False instead of raising in non-strict mode."""
        checksum = integrity_checker.generate_checksum(sample_log_file)
        integrity_checker.store_checksum(sample_log_file, checksum)
        
        # Modify file
        with open(sample_log_file, "a") as f:
            f.write("Modified\n")
        
        result = integrity_checker.verify_integrity(sample_log_file, strict=False)
        assert result is False


class TestBatchVerification:
    """Test batch integrity verification."""

    def test_verify_multiple_files(self, integrity_checker, temp_log_dir):
        """Should verify multiple files at once."""
        files = []
        for i in range(3):
            log_file = temp_log_dir / f"test_{i}.log"
            log_file.write_text(f"Log entry {i}\n")
            checksum = integrity_checker.generate_checksum(log_file)
            integrity_checker.store_checksum(log_file, checksum)
            files.append(log_file)
        
        results = integrity_checker.verify_batch(files)
        assert len(results) == 3
        assert all(results.values())

    def test_batch_identifies_tampered_files(self, integrity_checker, temp_log_dir):
        """Should identify which files are tampered in batch."""
        files = []
        for i in range(3):
            log_file = temp_log_dir / f"test_{i}.log"
            log_file.write_text(f"Log entry {i}\n")
            checksum = integrity_checker.generate_checksum(log_file)
            integrity_checker.store_checksum(log_file, checksum)
            files.append(log_file)
        
        # Tamper with middle file
        with open(files[1], "a") as f:
            f.write("TAMPERED\n")
        
        results = integrity_checker.verify_batch(files)
        assert results[files[0]] is True
        assert results[files[1]] is False
        assert results[files[2]] is True


class TestChecksumChain:
    """Test immutable checksum chain (blockchain-inspired)."""

    def test_create_chain_entry(self, integrity_checker, sample_log_file):
        """Should create chain entry linking to previous checksum."""
        checksum1 = integrity_checker.generate_checksum(sample_log_file)
        chain_entry1 = integrity_checker.create_chain_entry(
            sample_log_file,
            checksum1
        )
        
        assert "checksum" in chain_entry1
        assert "previous_hash" in chain_entry1
        assert "timestamp" in chain_entry1
        assert chain_entry1["previous_hash"] is None  # First entry

    def test_chain_links_to_previous(self, integrity_checker, sample_log_file):
        """Should link subsequent entries to previous hash."""
        # First entry
        checksum1 = integrity_checker.generate_checksum(sample_log_file)
        entry1 = integrity_checker.create_chain_entry(sample_log_file, checksum1)
        
        # Modify and create second entry
        with open(sample_log_file, "a") as f:
            f.write("New line\n")
        
        checksum2 = integrity_checker.generate_checksum(sample_log_file)
        entry2 = integrity_checker.create_chain_entry(sample_log_file, checksum2)
        
        assert entry2["previous_hash"] == entry1["entry_hash"]

    def test_verify_chain_integrity(self, integrity_checker, temp_log_dir):
        """Should verify entire chain is unbroken."""
        log_file = temp_log_dir / "chained.log"
        log_file.write_text("Entry 1\n")
        
        # Create chain
        checksums = []
        for i in range(3):
            with open(log_file, "a") as f:
                f.write(f"Entry {i+1}\n")
            checksum = integrity_checker.generate_checksum(log_file)
            integrity_checker.create_chain_entry(log_file, checksum)
            checksums.append(checksum)
        
        # Verify chain
        chain_valid = integrity_checker.verify_chain(log_file)
        assert chain_valid is True


class TestSignatureVerification:
    """Test digital signature verification."""

    def test_sign_checksum(self, integrity_checker, sample_log_file):
        """Should generate signature for checksum."""
        checksum = integrity_checker.generate_checksum(sample_log_file)
        signature = integrity_checker.sign_checksum(checksum, key="test_key")
        
        assert isinstance(signature, str)
        assert len(signature) > 0

    def test_verify_valid_signature(self, integrity_checker, sample_log_file):
        """Should verify valid signature."""
        checksum = integrity_checker.generate_checksum(sample_log_file)
        signature = integrity_checker.sign_checksum(checksum, key="test_key")
        
        is_valid = integrity_checker.verify_signature(
            checksum,
            signature,
            key="test_key"
        )
        assert is_valid is True

    def test_reject_invalid_signature(self, integrity_checker, sample_log_file):
        """Should reject invalid signature."""
        checksum = integrity_checker.generate_checksum(sample_log_file)
        fake_signature = "invalid_signature_data"
        
        is_valid = integrity_checker.verify_signature(
            checksum,
            fake_signature,
            key="test_key"
        )
        assert is_valid is False

    def test_reject_signature_with_wrong_key(self, integrity_checker, sample_log_file):
        """Should reject signature verified with wrong key."""
        checksum = integrity_checker.generate_checksum(sample_log_file)
        signature = integrity_checker.sign_checksum(checksum, key="key1")
        
        is_valid = integrity_checker.verify_signature(
            checksum,
            signature,
            key="key2"  # Different key
        )
        assert is_valid is False


class TestIntegrityReport:
    """Test integrity audit reporting."""

    def test_generate_integrity_report(self, integrity_checker, temp_log_dir):
        """Should generate comprehensive integrity report."""
        # Create multiple files
        for i in range(3):
            log_file = temp_log_dir / f"test_{i}.log"
            log_file.write_text(f"Content {i}\n")
            checksum = integrity_checker.generate_checksum(log_file)
            integrity_checker.store_checksum(log_file, checksum)
        
        report = integrity_checker.generate_report(temp_log_dir)
        
        assert "total_files" in report
        assert "verified_files" in report
        assert "tampered_files" in report
        assert "missing_checksums" in report
        assert report["total_files"] == 3
        assert report["verified_files"] == 3

    def test_report_includes_tampered_files(self, integrity_checker, temp_log_dir):
        """Should list tampered files in report."""
        files = []
        for i in range(3):
            log_file = temp_log_dir / f"test_{i}.log"
            log_file.write_text(f"Content {i}\n")
            checksum = integrity_checker.generate_checksum(log_file)
            integrity_checker.store_checksum(log_file, checksum)
            files.append(log_file)
        
        # Tamper with one file
        with open(files[1], "a") as f:
            f.write("TAMPERED\n")
        
        report = integrity_checker.generate_report(temp_log_dir)
        
        assert report["tampered_files"] == 1
        assert len(report["tampered_list"]) == 1
        assert files[1].name in str(report["tampered_list"][0])
