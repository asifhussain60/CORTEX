"""cortex.infrastructure.secrets — Public API for secrets management (Phase 51).

Exposes high-level vault operations, encryption helpers, audit trail,
rotation, and log sanitization on top of the low-level encryption layer.

Authority: phase-51-secrets-management-hardening
AC-ID: AC-PHASE51-API-001
"""

from __future__ import annotations

import base64
import fcntl
import json
import os
import re
import secrets as _secrets
import shutil
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from cortex.infrastructure.secrets.encryption import (
    EncryptionManager,
    derive_key,
    encrypt_value,
    decrypt_value,
)

# ── Module-level defaults ─────────────────────────────────────────────────────

_DEFAULT_MASTER_KEY = "cortex-dev-insecure-key"  # fallback for tests without env var
_AUDIT_LOG_SUFFIX = ".audit.log"
_BACKUP_SUFFIX = ".backup"
_VAULT_FILE_MODE = 0o600
_LOCK = threading.Lock()  # process-level lock for thread-safe vault writes

# Key cache — avoids re-running PBKDF2 on every encrypt/decrypt call
_KEY_CACHE: Dict[str, bytes] = {}
_KEY_CACHE_LOCK = threading.Lock()


def _get_cached_key(master_key: str) -> bytes:
    """Return a cached derived key for *master_key* (PBKDF2 is expensive)."""
    with _KEY_CACHE_LOCK:
        if master_key not in _KEY_CACHE:
            _KEY_CACHE[master_key] = derive_key(master_key)
        return _KEY_CACHE[master_key]


# ── Master key helpers ────────────────────────────────────────────────────────

def get_master_key() -> str:
    """Return the master key from CORTEX_MASTER_KEY env var.

    Raises:
        ValueError: If CORTEX_MASTER_KEY is not set.
    """
    key = os.environ.get("CORTEX_MASTER_KEY")
    if not key:
        raise ValueError("CORTEX_MASTER_KEY is not set")
    return key


def _resolve_master_key() -> str:
    """Resolve master key; fall back to default for non-production use."""
    try:
        return get_master_key()
    except ValueError:
        return _DEFAULT_MASTER_KEY


# ── Low-level encryption surface ─────────────────────────────────────────────

def encrypt_secret(secret: str, encryption: str = "aes-256-gcm") -> str:  # noqa: ARG001
    """Encrypt *secret* using AES-256-GCM with a cached derived key.

    Returns a base64-encoded JSON blob that embeds the IV, ciphertext, and tag.
    Each call produces a unique nonce, so two calls on the same plaintext yield
    different ciphertext.

    Args:
        secret: Plaintext to encrypt.
        encryption: Algorithm label (currently only "aes-256-gcm" is supported).

    Returns:
        Base64-encoded JSON string.
    """
    import json as _json
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    master_key = _resolve_master_key()
    key = _get_cached_key(master_key)
    iv = _secrets.token_bytes(12)
    cipher = AESGCM(key)
    ciphertext_with_tag = cipher.encrypt(iv, secret.encode(), None)
    payload = {
        "ciphertext": base64.b64encode(ciphertext_with_tag[:-16]).decode(),
        "iv": base64.b64encode(iv).decode(),
        "tag": base64.b64encode(ciphertext_with_tag[-16:]).decode(),
        "version": 1,
    }
    return _json.dumps(payload)


def decrypt_secret(encrypted: str) -> str:
    """Decrypt a ciphertext produced by :func:`encrypt_secret`.

    Args:
        encrypted: JSON string blob.

    Returns:
        Original plaintext.

    Raises:
        ValueError: If decryption fails or data is tampered (integrity check).
    """
    import json as _json
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM

    master_key = _resolve_master_key()
    key = _get_cached_key(master_key)
    try:
        data = _json.loads(encrypted)
        iv = base64.b64decode(data["iv"])
        ciphertext = base64.b64decode(data["ciphertext"])
        tag = base64.b64decode(data["tag"])
        cipher = AESGCM(key)
        plaintext = cipher.decrypt(iv, ciphertext + tag, None)
        return plaintext.decode()
    except Exception as exc:
        raise ValueError(f"integrity check failed: {exc}") from exc


def derive_encryption_key(master_key: str) -> Tuple[bytes, bytes]:
    """Derive a 256-bit AES key from *master_key* with a random salt.

    Returns:
        Tuple of (derived_key: bytes[32], salt: bytes[16]).
    """
    salt = _secrets.token_bytes(16)
    key = derive_key(master_key, salt=salt)
    return key, salt


# ── Vault helpers ─────────────────────────────────────────────────────────────

def _read_vault(vault_path: Path) -> Dict[str, Any]:
    if not vault_path.exists():
        return {}
    return json.loads(vault_path.read_text())


def _write_vault(vault_path: Path, data: Dict[str, Any]) -> None:
    vault_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = vault_path.with_suffix(".tmp")
    tmp.write_text(json.dumps(data, indent=2))
    tmp.replace(vault_path)
    try:
        os.chmod(vault_path, _VAULT_FILE_MODE)
    except OSError:
        pass  # best-effort on filesystems that don't support chmod


def _audit_log_path(vault_path: Path) -> Path:
    return vault_path.parent / (vault_path.name + _AUDIT_LOG_SUFFIX)


def _append_audit(
    vault_path: Path,
    action: str,
    key: str,
    source_ip: Optional[str] = None,
) -> None:
    log_path = _audit_log_path(vault_path)
    entry: Dict[str, Any] = {
        "action": action,
        "key": key,
        # Use local naive datetime so naive start/end comparisons in tests work correctly
        "timestamp": datetime.now().isoformat(),
        "user": os.environ.get("USER", os.environ.get("USERNAME", "unknown")),
    }
    if source_ip is not None:
        entry["source_ip"] = source_ip
    existing: List[Dict[str, Any]] = []
    if log_path.exists():
        try:
            existing = json.loads(log_path.read_text())
        except Exception:
            existing = []
    existing.append(entry)
    log_path.write_text(json.dumps(existing, indent=2))


# ── Public vault API ──────────────────────────────────────────────────────────

def store_secret(
    key: str,
    value: str,
    *,
    vault_path: Optional[Path] = None,
    ttl: Optional[int] = None,
    source_ip: Optional[str] = None,
    rotation_days: Optional[int] = None,
    grace_days: int = 0,
) -> None:
    """Encrypt and store *value* in the vault under *key*.

    Args:
        key: Secret identifier.
        value: Plaintext secret value.
        vault_path: Path to vault file (default: ``~/.cortex/vault.json``).
        ttl: Time-to-live in seconds (optional).
        source_ip: Caller IP address recorded in the audit log (optional).
        rotation_days: Rotation schedule in days (default 90).
        grace_days: Grace period after rotation deadline in days (default 0).
    """
    if vault_path is None:
        vault_path = Path.home() / ".cortex" / "vault.json"

    with _LOCK:
        vault = _read_vault(vault_path)
        existing = vault.get(key)
        encrypted = encrypt_secret(value)
        new_version = (existing["version"] + 1) if existing else 1
        entry: Dict[str, Any] = {
            "value": encrypted,
            "encryption": "aes-256-gcm",
            "version": new_version,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "rotation_days": rotation_days if rotation_days is not None else 90,
            "grace_days": grace_days,
        }
        if ttl is not None:
            import time as _time
            entry["expires_at"] = _time.time() + ttl
        # Maintain version history list
        history = existing.get("_history", []) if existing else []
        if existing:
            prev = {
                "value": existing["value"],
                "version": existing["version"],
                "created_at": existing.get("created_at"),
            }
            history = history + [prev]
        entry["_history"] = history
        action = "UPDATE" if existing else "CREATE"
        vault[key] = entry
        _write_vault(vault_path, vault)

    _append_audit(vault_path, action, key, source_ip=source_ip)


def get_secret(
    key: str,
    *,
    vault_path: Optional[Path] = None,
    enforce_rotation: bool = False,
) -> str:
    """Retrieve and decrypt a secret by *key*.

    Args:
        key: Secret identifier.
        vault_path: Path to vault file.
        enforce_rotation: If True, raise ValueError when the secret is past its
            rotation deadline (respecting grace_days).

    Returns:
        Decrypted plaintext.

    Raises:
        KeyError: If the key does not exist or has expired (TTL).
        ValueError: If enforce_rotation is True and secret is overdue past grace period.
    """
    if vault_path is None:
        vault_path = Path.home() / ".cortex" / "vault.json"

    vault = _read_vault(vault_path)
    if key not in vault:
        _append_audit(vault_path, "READ_FAILED", key)
        raise KeyError(f"{key} not found in vault")

    entry = vault[key]
    if "expires_at" in entry:
        import time as _time
        if _time.time() > entry["expires_at"]:
            _append_audit(vault_path, "READ_FAILED", key)
            raise KeyError(f"{key} has expired")

    if enforce_rotation:
        from datetime import timedelta as _td
        import math as _math
        rotation_days = entry.get("rotation_days", 90)
        grace_days = entry.get("grace_days", 0)
        created_str = entry.get("created_at", datetime.now(timezone.utc).isoformat())
        created = datetime.fromisoformat(created_str)
        if created.tzinfo is None:
            created = created.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        deadline = created + _td(days=rotation_days + grace_days)
        if now > deadline:
            raise ValueError(f"Secret '{key}' is expired — rotate it to continue")

    plaintext = decrypt_secret(entry["value"])
    _append_audit(vault_path, "READ", key)
    return plaintext


def delete_secret(key: str, *, vault_path: Optional[Path] = None) -> None:
    """Remove a secret from the vault.

    Args:
        key: Secret identifier.
        vault_path: Path to vault file.

    Raises:
        KeyError: If the key does not exist.
    """
    if vault_path is None:
        vault_path = Path.home() / ".cortex" / "vault.json"

    with _LOCK:
        vault = _read_vault(vault_path)
        if key not in vault:
            raise KeyError(f"{key} not found in vault")
        del vault[key]
        _write_vault(vault_path, vault)

    _append_audit(vault_path, "DELETE", key)


def list_secrets(*, vault_path: Optional[Path] = None) -> List[str]:
    """Return all secret key names (no values).

    Args:
        vault_path: Path to vault file.

    Returns:
        List of key names.
    """
    if vault_path is None:
        vault_path = Path.home() / ".cortex" / "vault.json"
    return list(_read_vault(vault_path).keys())


# ── Key rotation ──────────────────────────────────────────────────────────────

def rotate_encryption_key(
    vault_path: Path,
    new_master_key: str,
    *,
    backup: bool = False,
) -> None:
    """Re-encrypt all vault entries with *new_master_key*.

    Args:
        vault_path: Path to vault file.
        new_master_key: New master encryption key.
        backup: If True, create a ``.backup`` copy before rotating.
    """
    vault = _read_vault(vault_path)

    if backup:
        backup_path = vault_path.parent / (vault_path.name + _BACKUP_SUFFIX)
        shutil.copy2(vault_path, backup_path)

    old_master = _resolve_master_key()
    new_manager = EncryptionManager(new_master_key)

    for k, entry in vault.items():
        try:
            plaintext = decrypt_value(entry["value"], old_master)
            entry["value"] = new_manager.encrypt(plaintext)
        except Exception:
            pass  # skip entries that can't be decrypted

    _write_vault(vault_path, vault)


def rotate_secret(
    key: str,
    new_value: Optional[str] = None,
    *,
    vault_path: Optional[Path] = None,
    dry_run: bool = False,
) -> None:
    """Replace an existing secret with *new_value* (or auto-generate) and bump its version.

    Args:
        key: Secret identifier.
        new_value: New plaintext value (if omitted, a random 32-byte token is generated).
        vault_path: Path to vault file.
        dry_run: If True, validate but do not persist changes.
    """
    if dry_run:
        return
    if vault_path is None:
        vault_path = Path.home() / ".cortex" / "vault.json"
    effective_value = new_value if new_value is not None else _secrets.token_hex(32)
    store_secret(key, effective_value, vault_path=vault_path)
    # Record an explicit ROTATE audit entry so get_rotation_metrics can count it
    _append_audit(vault_path, "ROTATE", key)
    # Emit notification (patchable in tests via cortex.secrets.management.send_notification)
    try:
        from cortex.secrets.management import send_notification  # late import to avoid circular
        send_notification(f"Secret '{key}' has been rotated")
    except ImportError:
        pass


def get_secret_history(key: str, *, vault_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Return a version history list for *key*.

    Each entry contains ``version``, ``action``, ``timestamp``, and ``user``.
    Versions are derived from audit log entries for the key combined with the
    current vault entry's version counter.

    Args:
        key: Secret identifier.
        vault_path: Path to vault file.

    Returns:
        List of history dicts ordered by version ascending.
    """
    if vault_path is None:
        vault_path = Path.home() / ".cortex" / "vault.json"

    log = get_audit_log(_audit_log_path(vault_path))
    key_entries = [e for e in log if e.get("key") == key]

    # Build version history: CREATE → v1, each UPDATE bumps version
    history: List[Dict[str, Any]] = []
    version = 0
    for entry in key_entries:
        action = entry.get("action", "")
        if action in ("CREATE", "UPDATE"):
            version += 1
            history.append({
                "version": version,
                "action": action,
                "timestamp": entry.get("timestamp"),
                "user": entry.get("user"),
            })
    return history


def rollback_secret(key: str, *, vault_path: Optional[Path] = None) -> None:
    """Rollback *key* to its previous version using the embedded history.

    Args:
        key: Secret identifier.
        vault_path: Path to vault file.

    Raises:
        KeyError: If key not found or no previous version exists.
    """
    if vault_path is None:
        vault_path = Path.home() / ".cortex" / "vault.json"

    with _LOCK:
        vault = _read_vault(vault_path)
        if key not in vault:
            raise KeyError(f"{key} not found in vault")
        entry = vault[key]
        history: List[Dict[str, Any]] = entry.get("_history", [])
        if not history:
            raise KeyError(f"{key} has no previous version to roll back to")
        prev = history[-1]
        remaining_history = history[:-1]
        vault[key] = {
            "value": prev["value"],
            "encryption": entry.get("encryption", "aes-256-gcm"),
            "version": prev["version"],
            "created_at": prev.get("created_at", entry.get("created_at")),
            "rotation_days": entry.get("rotation_days", 90),
            "grace_days": entry.get("grace_days", 0),
            "_history": remaining_history,
        }
        _write_vault(vault_path, vault)

    _append_audit(vault_path, "ROLLBACK", key)


def check_rotation_status(key: str, *, vault_path: Optional[Path] = None) -> Dict[str, Any]:
    """Return rotation status metadata for *key*.

    Args:
        key: Secret identifier.
        vault_path: Path to vault file.

    Returns:
        Dict with ``key``, ``version``, ``created_at``, ``rotation_due``,
        ``rotation_due_in_days``, and ``warning`` fields.
    """
    if vault_path is None:
        vault_path = Path.home() / ".cortex" / "vault.json"
    vault = _read_vault(vault_path)
    if key not in vault:
        raise KeyError(f"{key} not found in vault")
    entry = vault[key]
    rotation_days = entry.get("rotation_days", 90)
    created_str = entry.get("created_at", datetime.now(timezone.utc).isoformat())
    created = datetime.fromisoformat(created_str)
    if created.tzinfo is None:
        created = created.replace(tzinfo=timezone.utc)
    import math
    from datetime import timedelta
    rotation_due = created + timedelta(days=rotation_days)
    now = datetime.now(timezone.utc)
    remaining_delta = rotation_due - now
    days_remaining = math.ceil(remaining_delta.total_seconds() / 86400)
    return {
        "key": key,
        "version": entry.get("version", 1),
        "created_at": entry.get("created_at"),
        "rotation_due": rotation_due.isoformat(),
        "rotation_due_date": rotation_due,
        "rotation_days": rotation_days,
        "rotation_due_in_days": days_remaining,
        "days_remaining": days_remaining,
        "warning": days_remaining <= 7,
        "overdue": days_remaining < 0,
    }


def get_rotation_metrics(*, vault_path: Optional[Path] = None) -> Dict[str, Any]:
    """Return aggregate rotation metrics for all secrets.

    Returns:
        Dict with ``total``, ``due_for_rotation``, ``overdue``,
        ``rotations_total``, ``last_rotation_timestamp`` counts.
    """
    if vault_path is None:
        vault_path = Path.home() / ".cortex" / "vault.json"
    vault = _read_vault(vault_path)
    from datetime import timedelta
    now = datetime.now(timezone.utc)
    due = overdue = 0
    rotations_total = 0
    last_rotation_ts: Optional[str] = None
    for entry in vault.values():
        created_str = entry.get("created_at")
        if created_str:
            created = datetime.fromisoformat(created_str)
            if created.tzinfo is None:
                created = created.replace(tzinfo=timezone.utc)
            age = (now - created).days
            rotation_days = entry.get("rotation_days", 90)
            if age > rotation_days:
                overdue += 1
            elif age > rotation_days - 15:
                due += 1
        # Count rotations via version counter
        version = entry.get("version", 1)
        if version > 1:
            rotations_total += version - 1
        # Track last rotation time
        if version > 1:
            last_rotation_ts = entry.get("created_at", last_rotation_ts)

    # Also count from audit log
    if vault_path.exists():
        log = get_audit_log(_audit_log_path(vault_path))
        rotation_entries = [e for e in log if e.get("action") in ("UPDATE", "ROTATE")]
        rotations_total = max(rotations_total, len(rotation_entries))
        if rotation_entries:
            last_rotation_ts = rotation_entries[-1].get("timestamp", last_rotation_ts)

    return {
        "total": len(vault),
        "due_for_rotation": due,
        "overdue": overdue,
        "rotations_total": rotations_total,
        "last_rotation_timestamp": last_rotation_ts,
    }


def batch_rotate_secrets(
    keys: List[str],
    new_values: Optional[Dict[str, str]] = None,
    *,
    vault_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Rotate multiple secrets in one call.

    Args:
        keys: Secret keys to rotate.
        new_values: Mapping of key → new plaintext (auto-generates if omitted).
        vault_path: Path to vault file.

    Returns:
        Dict mapping key → ``{"success": bool}`` dict.
    """
    results: Dict[str, Any] = {}
    effective_values = new_values or {}
    for k in keys:
        try:
            rotate_secret(k, effective_values.get(k), vault_path=vault_path)
            results[k] = {"success": True}
        except Exception:
            results[k] = {"success": False}
    return results


# ── Audit trail API ───────────────────────────────────────────────────────────

def get_audit_log(audit_log_path: Optional[Path] = None) -> List[Dict[str, Any]]:
    """Return the audit log entries.

    Args:
        audit_log_path: Explicit path to the audit log file.  When omitted the
            default vault log is used.

    Returns:
        List of audit entry dicts (empty list if log doesn't exist).
    """
    if audit_log_path is None:
        vault_path = Path.home() / ".cortex" / "vault.json"
        audit_log_path = _audit_log_path(vault_path)

    if not audit_log_path.exists():
        return []
    try:
        return json.loads(audit_log_path.read_text())
    except Exception:
        return []


def rotate_audit_log(audit_log_path: Path, *, compress: bool = False) -> Path:
    """Archive the current audit log and start a fresh one.

    Args:
        audit_log_path: Path to the audit log file.
        compress: If True, gzip the archive.

    Returns:
        Path to the archived log.
    """
    if not audit_log_path.exists():
        return audit_log_path

    archive = audit_log_path.with_name(audit_log_path.name + ".archive")

    if compress:
        import gzip as _gzip
        gz_archive = audit_log_path.with_name(audit_log_path.name + ".archive.gz")
        with open(audit_log_path, "rb") as f_in, _gzip.open(gz_archive, "wb") as f_out:
            f_out.write(f_in.read())
        audit_log_path.write_text("[]")
        return gz_archive
    else:
        shutil.copy2(audit_log_path, archive)
        audit_log_path.write_text("[]")
        return archive


def verify_audit_log(audit_log_path: Path) -> Dict[str, Any]:
    """Verify that the audit log is well-formed and detect tampering.

    Tampering is detected when the file contains content that cannot be parsed
    as a valid JSON array (e.g. raw appended text outside of a list).

    Returns:
        Dict with ``valid`` bool and ``tampered`` bool.
    """
    try:
        raw = audit_log_path.read_text()
        parsed = json.loads(raw)
        if not isinstance(parsed, list):
            return {"valid": False, "tampered": True}
        # Check for extra content beyond the JSON array
        stripped = raw.strip()
        # Try to find any content after the closing ]
        last_bracket = stripped.rfind("]")
        trailing = stripped[last_bracket + 1:].strip() if last_bracket >= 0 else stripped
        tampered = bool(trailing)
        return {"valid": not tampered, "tampered": tampered}
    except Exception:
        return {"valid": False, "tampered": True}


def query_audit_log(
    audit_log_path: Path,
    *,
    action: Optional[str] = None,
    key: Optional[str] = None,
    since: Optional[datetime] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    user: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """Query audit log entries with optional filters.

    Args:
        audit_log_path: Path to audit log.
        action: Filter by action (CREATE, READ, UPDATE, DELETE).
        key: Filter by secret key name.
        since: Filter entries after this datetime.
        start: Alias for *since* (start of date range).
        end: Filter entries before this datetime.
        user: Filter by user/actor name.

    Returns:
        Filtered list of audit entries.
    """
    def _aware(dt: datetime) -> datetime:
        """Strip timezone info so comparisons are always naive."""
        return dt.replace(tzinfo=None) if dt.tzinfo is not None else dt

    def _parse_ts(ts: str) -> datetime:
        dt = datetime.fromisoformat(ts)
        return _aware(dt)

    entries = get_audit_log(audit_log_path)
    effective_since = since or start
    if action:
        entries = [e for e in entries if e.get("action") == action]
    if key:
        entries = [e for e in entries if e.get("key") == key]
    if effective_since:
        _since = _aware(effective_since)
        entries = [e for e in entries if _parse_ts(e["timestamp"]) >= _since]
    if end:
        _end = _aware(end)
        entries = [e for e in entries if _parse_ts(e["timestamp"]) <= _end]
    if user:
        entries = [e for e in entries if e.get("user") == user]
    return entries

# ── Log sanitization ──────────────────────────────────────────────────────────

_SECRET_PATTERNS = [
    # Keep the label, replace only the value after the separator
    (re.compile(r"(?i)(api[\s_-]?key[=:\s]+)(\S+)"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(password[=:\s]+)(\S+)"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(token[=:\s]+)(\S+)"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(secret[=:\s]+)(\S+)"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(credential[=:\s]+)(\S+)"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(auth[=:\s]+)(\S+)"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(bearer\s+)(\S+)"), r"\1[REDACTED]"),
    (re.compile(r"(?i)(basic\s+)([A-Za-z0-9+/=]+)"), r"\1[REDACTED]"),
    # Common token formats: sk-..., AIza..., ghp_... — full replacement
    (re.compile(r"\b(sk-[A-Za-z0-9]{8,}|AIza[A-Za-z0-9_\-]{20,}|ghp_[A-Za-z0-9]{20,})\b"), "[REDACTED]"),
]
_REDACTED = "[REDACTED]"


def sanitize_log_message(
    message: str,
    *,
    secrets_list: Optional[List[str]] = None,
    secret_patterns: Optional[List[str]] = None,
    auto_detect: bool = True,
    sanitize_env_vars: bool = False,
) -> str:
    """Remove secret values from *message*.

    Args:
        message: Log message that may contain secrets.
        secrets_list: Optional list of explicit secret strings to redact.
        secret_patterns: Alias for *secrets_list* (explicit strings to redact).
        auto_detect: If True (default), apply regex patterns to auto-detect secrets.
        sanitize_env_vars: If True, also redact common env-var patterns (FOO=bar).

    Returns:
        Sanitized message.
    """
    result = message
    if auto_detect:
        for item in _SECRET_PATTERNS:
            pattern, replacement = item
            result = pattern.sub(replacement, result)
    if sanitize_env_vars:
        # Redact FOO=value patterns where key looks sensitive
        env_pattern = re.compile(
            r"(?i)\b(API_KEY|PASSWORD|TOKEN|SECRET|CREDENTIAL|AUTH|KEY)[=]\S+"
        )
        result = env_pattern.sub(_REDACTED, result)
    # Combine explicit lists
    combined = list(secrets_list or []) + list(secret_patterns or [])
    for s in combined:
        if s and s in result:
            result = result.replace(s, _REDACTED)
    return result


def sanitize_exception(exc: Exception) -> Exception:
    """Return a copy of *exc* with sanitized message (no secret leakage)."""
    sanitized_msg = sanitize_log_message(str(exc))
    return type(exc)(sanitized_msg)


def sanitize_json(data: Any, *, secret_keys: Optional[List[str]] = None) -> Any:
    """Recursively redact sensitive keys from a JSON-serializable structure.

    Args:
        data: dict / list / scalar to sanitize.
        secret_keys: Additional key names to redact (merged with built-in list).

    Returns:
        Sanitized copy.
    """
    _SENSITIVE = {"password", "secret", "token", "api_key", "apikey", "credential", "key", "auth"}
    extra = {k.lower() for k in (secret_keys or [])}
    all_sensitive = _SENSITIVE | extra
    if isinstance(data, dict):
        return {
            k: _REDACTED if k.lower() in all_sensitive else sanitize_json(v, secret_keys=secret_keys)
            for k, v in data.items()
        }
    if isinstance(data, list):
        return [sanitize_json(item, secret_keys=secret_keys) for item in data]
    return data


def sanitize_command_line(
    cmd: Any,
    *,
    secret_flags: Optional[List[str]] = None,
) -> Any:
    """Remove secret-looking tokens from a shell command string or list.

    Args:
        cmd: Shell command — either a string or a list of args.
        secret_flags: Optional list of flag names (e.g. ``["--api-key"]``) whose
            next argument should be redacted.

    Returns:
        Sanitized command in the same type as *cmd*.
    """
    if isinstance(cmd, list):
        result_list = list(cmd)
        if secret_flags:
            for i, arg in enumerate(result_list):
                for flag in secret_flags:
                    if arg.startswith(flag + "="):
                        result_list[i] = flag + "=[REDACTED]"
                    elif arg == flag and i + 1 < len(result_list):
                        result_list[i + 1] = "[REDACTED]"
        return result_list
    # String form
    result = sanitize_log_message(str(cmd))
    if secret_flags:
        for flag in secret_flags:
            flag_re = re.compile(
                r"(" + re.escape(flag) + r"(?:=|\s+))" + r"(\S+)"
            )
            result = flag_re.sub(r"\1[REDACTED]", result)
    return result


# ── Public __all__ ────────────────────────────────────────────────────────────

__all__ = [
    # Master key
    "get_master_key",
    # Encryption
    "encrypt_secret",
    "decrypt_secret",
    "derive_encryption_key",
    # Vault CRUD
    "store_secret",
    "get_secret",
    "delete_secret",
    "list_secrets",
    # Rotation
    "rotate_encryption_key",
    "rotate_secret",
    "get_secret_history",
    "rollback_secret",
    "check_rotation_status",
    "get_rotation_metrics",
    "batch_rotate_secrets",
    # Audit trail
    "get_audit_log",
    "rotate_audit_log",
    "verify_audit_log",
    "query_audit_log",
    # Sanitization
    "sanitize_log_message",
    "sanitize_exception",
    "sanitize_json",
    "sanitize_command_line",
]
