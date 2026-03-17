"""CryptoProvider compatibility implementation for security tests."""

import binascii
import hashlib
import os
import secrets

from cryptography.hazmat.primitives.ciphers.aead import AESGCM


class CryptoProvider:
    """Provides encryption, password hashing, and secure random utilities."""

    KEY_SIZE = 32
    NONCE_SIZE = 12
    HASH_ITERATIONS = 100000

    def __init__(self) -> None:
        self.current_key: bytes = self.generate_key()
        self.key_versions: dict = {}

    def generate_key(self, size: int = KEY_SIZE) -> bytes:
        if size <= 0:
            raise ValueError("Key size must be positive")
        return os.urandom(size)

    def rotate_key(self, new_key: bytes) -> None:
        if len(new_key) != self.KEY_SIZE:
            raise ValueError(f"Key must be {self.KEY_SIZE} bytes")
        self.current_key = new_key

    def generate_secure_random(self, length: int) -> bytes:
        if length <= 0:
            raise ValueError("Length must be positive")
        return os.urandom(length)

    def encrypt(self, plaintext: bytes) -> bytes:
        """Encrypt plaintext and return nonce+ciphertext bytes."""
        if not isinstance(plaintext, (bytes, bytearray)):
            raise ValueError("Plaintext must be bytes")

        nonce = self.generate_secure_random(self.NONCE_SIZE)
        aes = AESGCM(self.current_key)
        ciphertext = aes.encrypt(nonce, bytes(plaintext), None)
        return nonce + ciphertext

    def decrypt(self, encrypted_payload: bytes) -> bytes:
        """Decrypt nonce+ciphertext payload and return plaintext bytes."""
        if len(encrypted_payload) <= self.NONCE_SIZE:
            raise ValueError("Invalid encrypted payload")

        nonce = encrypted_payload[: self.NONCE_SIZE]
        ciphertext = encrypted_payload[self.NONCE_SIZE :]
        aes = AESGCM(self.current_key)
        return aes.decrypt(nonce, ciphertext, None)

    def hash_password(self, password: str) -> str:
        if not password:
            raise ValueError("Password required")

        salt = os.urandom(16)
        hash_bytes = hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            self.HASH_ITERATIONS,
            dklen=32,
        )
        return f"{binascii.hexlify(salt).decode()}${binascii.hexlify(hash_bytes).decode()}"

    def verify_password(self, password: str, hashed_password: str) -> bool:
        try:
            salt_hex, hash_hex = hashed_password.split("$", 1)
            salt = binascii.unhexlify(salt_hex)
            expected = binascii.unhexlify(hash_hex)
            candidate = hashlib.pbkdf2_hmac(
                "sha256",
                password.encode("utf-8"),
                salt,
                self.HASH_ITERATIONS,
                dklen=32,
            )
            return secrets.compare_digest(candidate, expected)
        except (ValueError, binascii.Error):
            return False


__all__ = ["CryptoProvider"]
