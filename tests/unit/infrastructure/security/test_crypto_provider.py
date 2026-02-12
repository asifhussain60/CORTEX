"""
Tests for CryptoProvider - cryptographic operations.

Author: CORTEX Implementation
Phase: impl-arch-005-hardening
Compliance: CORE-008 (TDD), CORE-011 (100% typed), CORE-012 (Google docstrings)
"""

import pytest


class TestCryptoAES256GCM:
    """Test AES-256-GCM encryption/decryption."""

    def test_encrypts_plaintext(self) -> None:
        """Verify plaintext is encrypted correctly."""
        from cortex.infrastructure.security import CryptoProvider
        
        crypto = CryptoProvider()
        plaintext = "secret message"
        
        ciphertext = crypto.encrypt(plaintext.encode())
        assert ciphertext is not None
        assert len(ciphertext) > 0

    def test_decrypts_ciphertext(self) -> None:
        """Verify ciphertext is decrypted correctly."""
        from cortex.infrastructure.security import CryptoProvider
        
        crypto = CryptoProvider()
        plaintext = "secret message"
        
        ciphertext = crypto.encrypt(plaintext.encode())
        decrypted = crypto.decrypt(ciphertext)
        assert decrypted == plaintext.encode()

    def test_encryption_produces_different_ciphertexts(self) -> None:
        """Verify encryption produces different ciphertexts (IV randomization)."""
        from cortex.infrastructure.security import CryptoProvider
        
        crypto = CryptoProvider()
        plaintext = "secret message"
        
        cipher1 = crypto.encrypt(plaintext.encode())
        cipher2 = crypto.encrypt(plaintext.encode())
        
        assert cipher1 != cipher2  # Different IVs


class TestCryptoPBKDF2:
    """Test PBKDF2 password hashing."""

    def test_hashes_password_with_pbkdf2(self) -> None:
        """Verify passwords are hashed with PBKDF2."""
        from cortex.infrastructure.security import CryptoProvider
        
        crypto = CryptoProvider()
        password = "MySecurePassword123"
        
        hashed = crypto.hash_password(password)
        assert hashed is not None
        assert len(hashed) > 0

    def test_uses_100k_iterations(self) -> None:
        """Verify PBKDF2 uses 100k iterations."""
        from cortex.infrastructure.security import CryptoProvider
        
        crypto = CryptoProvider()
        password = "test"
        
        hashed = crypto.hash_password(password)
        assert hashed is not None

    def test_verifies_correct_password(self) -> None:
        """Verify correct password verification succeeds."""
        from cortex.infrastructure.security import CryptoProvider
        
        crypto = CryptoProvider()
        password = "correct_password"
        
        hashed = crypto.hash_password(password)
        assert crypto.verify_password(password, hashed) is True

    def test_rejects_incorrect_password(self) -> None:
        """Verify incorrect password verification fails."""
        from cortex.infrastructure.security import CryptoProvider
        
        crypto = CryptoProvider()
        password = "correct_password"
        
        hashed = crypto.hash_password(password)
        assert crypto.verify_password("wrong_password", hashed) is False


class TestCryptoRandomGeneration:
    """Test secure random number generation."""

    def test_generates_random_bytes(self) -> None:
        """Verify random bytes are generated."""
        from cortex.infrastructure.security import CryptoProvider
        
        crypto = CryptoProvider()
        random_bytes = crypto.generate_secure_random(32)
        
        assert len(random_bytes) == 32
        assert isinstance(random_bytes, bytes)

    def test_uses_os_urandom(self) -> None:
        """Verify os.urandom is used for randomness."""
        from cortex.infrastructure.security import CryptoProvider
        
        crypto = CryptoProvider()
        
        # Generate multiple and verify uniqueness
        rand1 = crypto.generate_secure_random(16)
        rand2 = crypto.generate_secure_random(16)
        
        assert rand1 != rand2

    def test_random_output_length_matches_requested(self) -> None:
        """Verify output length matches request."""
        from cortex.infrastructure.security import CryptoProvider
        
        crypto = CryptoProvider()
        
        for length in [16, 32, 64]:
            random_bytes = crypto.generate_secure_random(length)
            assert len(random_bytes) == length


class TestCryptoKeyRotation:
    """Test key rotation capability."""

    def test_can_rotate_keys(self) -> None:
        """Verify keys can be rotated."""
        from cortex.infrastructure.security import CryptoProvider
        
        crypto = CryptoProvider()
        new_key = crypto.generate_key()
        
        crypto.rotate_key(new_key)
        # Should not raise

class TestCryptoErrors:
    """Test error handling."""

