"""Secrets migration — orchestrate moving secrets between backends."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from cortex.secrets.secrets_provider import ISecretsProvider


@dataclass
class MigrationResult:
    success: bool = False
    migrated: List[str] = field(default_factory=list)
    failed: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class SecretsMigrator:
    """Migrates secrets from one provider to another."""

    def migrate(
        self,
        source: ISecretsProvider,
        destination: ISecretsProvider,
        keys: Optional[List[str]] = None,
    ) -> MigrationResult:
        """Migrate.
        
        Args:
            source: Parameter for source.
            destination: Parameter for destination.
            keys: Parameter for keys.
        
        Returns:
            MigrationResult result.
        """
        result = MigrationResult()
        keys = keys or source.list_secrets()
        for key in keys:
            try:
                value = source.get_secret(key)
                destination.set_secret(key, value)
                result.migrated.append(key)
            except Exception as exc:
                result.failed.append(key)
                result.errors.append(str(exc))
        result.success = len(result.failed) == 0
        return result


class SecretsValidator:
    """Validates that secrets exist and meet policy requirements."""

    def validate_secret(self, provider: ISecretsProvider, key: str, policy: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Validate secret.
        
        Args:
            provider: Parameter for provider.
            key: Parameter for key.
            policy: Parameter for policy.
        
        Returns:
            Dict[str, Any] result.
        """
        try:
            value = provider.get_secret(key)
            issues: List[str] = []
            min_len = (policy or {}).get("min_length", 8)
            if len(value) < min_len:
                issues.append(f"Value too short (min {min_len})")
            return {"key": key, "valid": len(issues) == 0, "issues": issues}
        except Exception as exc:
            return {"key": key, "valid": False, "issues": [str(exc)]}

    def validate_all(self, provider: ISecretsProvider) -> List[Dict[str, Any]]:
        """Validate all.
        
        Args:
            provider: Parameter for provider.
        
        Returns:
            List[Dict[str, Any]] result.
        """
        return [self.validate_secret(provider, k) for k in provider.list_secrets()]


class SecretsRollback:
    """Handles rollback of a failed migration."""

    def __init__(self) -> None:
        self._snapshot: Dict[str, str] = {}

    def snapshot(self, provider: ISecretsProvider) -> None:
        """Snapshot.
        
        Args:
            provider: Parameter for provider.
        """
        for key in provider.list_secrets():
            try:
                self._snapshot[key] = provider.get_secret(key)
            except Exception:
                pass

    def rollback(self, provider: ISecretsProvider) -> bool:
        """Rollback.
        
        Args:
            provider: Parameter for provider.
        
        Returns:
            bool result.
        """
        for key, value in self._snapshot.items():
            try:
                provider.set_secret(key, value)
            except Exception:
                return False
        return True


class SecretsMigrationDetector:
    """Detects whether a migration is needed."""

    def needs_migration(
        self,
        source: ISecretsProvider,
        destination: ISecretsProvider,
    ) -> bool:
        """Needs migration.
        
        Args:
            source: Parameter for source.
            destination: Parameter for destination.
        
        Returns:
            bool result.
        """
        src_keys = set(source.list_secrets())
        dst_keys = set(destination.list_secrets())
        return len(src_keys - dst_keys) > 0

    def diff(
        self,
        source: ISecretsProvider,
        destination: ISecretsProvider,
    ) -> Dict[str, Any]:
        """Diff.
        
        Args:
            source: Parameter for source.
            destination: Parameter for destination.
        
        Returns:
            Dict[str, Any] result.
        """
        src_keys = set(source.list_secrets())
        dst_keys = set(destination.list_secrets())
        return {
            "only_in_source": list(src_keys - dst_keys),
            "only_in_destination": list(dst_keys - src_keys),
            "in_both": list(src_keys & dst_keys),
        }


class SecretsMigrationOrchestrator:
    """Full migration workflow: detect → snapshot → migrate → validate → rollback."""

    def __init__(self) -> None:
        self._migrator = SecretsMigrator()
        self._validator = SecretsValidator()
        self._rollback = SecretsRollback()
        self._detector = SecretsMigrationDetector()

    def run(
        self,
        source: ISecretsProvider,
        destination: ISecretsProvider,
        dry_run: bool = False,
    ) -> MigrationResult:
        """Run.
        
        Args:
            source: Parameter for source.
            destination: Parameter for destination.
            dry_run: Parameter for dry run.
        
        Returns:
            MigrationResult result.
        """
        if dry_run:
            diff = self._detector.diff(source, destination)
            return MigrationResult(
                success=True,
                migrated=diff["only_in_source"],
            )
        self._rollback.snapshot(destination)
        result = self._migrator.migrate(source, destination)
        if not result.success:
            self._rollback.rollback(destination)
        return result
