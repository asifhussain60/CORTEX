"""
Tests for Phase 101 — Duplicate File Consolidation (CORE-035).

Validates that renamed classes are accessible via both new canonical names
and backward-compat aliases, and that no import chains are broken.

AC-ID: AC-P101-001
Authority: CORE-008 (TDD), CORE-035 (single canonical implementation)
"""

import pytest


class TestPersonaOrchestratorRename:
    """Phase 101: persona MasterOrchestrator → PersonaOrchestrator."""

    def test_canonical_import(self) -> None:
        """PersonaOrchestrator is importable by canonical name."""
        from cortex.orchestrators.persona.master_orchestrator import PersonaOrchestrator
        assert PersonaOrchestrator is not None

    def test_backward_compat_alias(self) -> None:
        """MasterOrchestrator alias still works for backward compatibility."""
        from cortex.orchestrators.persona.master_orchestrator import MasterOrchestrator
        assert MasterOrchestrator is not None

    def test_alias_points_to_canonical(self) -> None:
        """The alias and canonical name refer to the same class."""
        from cortex.orchestrators.persona.master_orchestrator import (
            MasterOrchestrator,
            PersonaOrchestrator,
        )
        assert MasterOrchestrator is PersonaOrchestrator

    def test_distinct_from_core_master(self) -> None:
        """PersonaOrchestrator is NOT the same class as core MasterOrchestrator."""
        from cortex.orchestrators.persona.master_orchestrator import PersonaOrchestrator
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        assert PersonaOrchestrator is not MasterOrchestrator


class TestEnhancedIntentClassifierRename:
    """Phase 101: intelligence IntentClassifier → EnhancedIntentClassifier."""

    def test_canonical_import(self) -> None:
        """EnhancedIntentClassifier is importable by canonical name."""
        from cortex.intelligence.intent_classifier import EnhancedIntentClassifier
        assert EnhancedIntentClassifier is not None

    def test_backward_compat_alias(self) -> None:
        """IntentClassifier alias still works for backward compatibility."""
        from cortex.intelligence.intent_classifier import IntentClassifier
        assert IntentClassifier is not None

    def test_alias_points_to_canonical(self) -> None:
        """The alias and canonical name refer to the same class."""
        from cortex.intelligence.intent_classifier import (
            IntentClassifier,
            EnhancedIntentClassifier,
        )
        assert IntentClassifier is EnhancedIntentClassifier

    def test_distinct_from_core_classifier(self) -> None:
        """EnhancedIntentClassifier is NOT the same as core IntentClassifier."""
        from cortex.intelligence.intent_classifier import EnhancedIntentClassifier
        from cortex.orchestrators.core.intent_classifier import IntentClassifier
        assert EnhancedIntentClassifier is not IntentClassifier

    def test_classify_intent_convenience_function(self) -> None:
        """The module-level classify_intent() convenience function works."""
        from cortex.intelligence.intent_classifier import classify_intent
        result = classify_intent("fix the login bug")
        assert result is not None
        assert hasattr(result, "intent")
        assert hasattr(result, "confidence")


class TestCrossLayerCoherenceValidatorRename:
    """Phase 101: domain CoherenceValidator → CrossLayerCoherenceValidator."""

    def test_canonical_import(self) -> None:
        """CrossLayerCoherenceValidator is importable by canonical name."""
        from cortex.orchestrators.domain.coherence_validator import CrossLayerCoherenceValidator
        assert CrossLayerCoherenceValidator is not None

    def test_backward_compat_alias(self) -> None:
        """CoherenceValidator alias still works for backward compatibility."""
        from cortex.orchestrators.domain.coherence_validator import CoherenceValidator
        assert CoherenceValidator is not None

    def test_alias_points_to_canonical(self) -> None:
        """The alias and canonical name refer to the same class."""
        from cortex.orchestrators.domain.coherence_validator import (
            CoherenceValidator,
            CrossLayerCoherenceValidator,
        )
        assert CoherenceValidator is CrossLayerCoherenceValidator

    def test_distinct_from_validation_coherence(self) -> None:
        """CrossLayerCoherenceValidator is NOT the same as validation CoherenceValidator."""
        from cortex.orchestrators.domain.coherence_validator import CrossLayerCoherenceValidator
        from cortex.orchestrators.validation.coherence_validator import CoherenceValidator
        assert CrossLayerCoherenceValidator is not CoherenceValidator


class TestSecretsAuditTrailRename:
    """Phase 101: secrets AuditTrail → SecretsAuditTrail."""

    def test_canonical_import(self) -> None:
        """SecretsAuditTrail is importable by canonical name."""
        from cortex.infrastructure.secrets.audit_trail import SecretsAuditTrail
        assert SecretsAuditTrail is not None

    def test_backward_compat_alias(self) -> None:
        """AuditTrail alias still works for backward compatibility."""
        from cortex.infrastructure.secrets.audit_trail import AuditTrail
        assert AuditTrail is not None

    def test_alias_points_to_canonical(self) -> None:
        """The alias and canonical name refer to the same class."""
        from cortex.infrastructure.secrets.audit_trail import (
            AuditTrail,
            SecretsAuditTrail,
        )
        assert AuditTrail is SecretsAuditTrail

    def test_distinct_from_observability_audit_trail(self) -> None:
        """SecretsAuditTrail is NOT the same as observability AuditTrail."""
        from cortex.infrastructure.secrets.audit_trail import SecretsAuditTrail
        from cortex.observability.audit_trail import AuditTrail
        assert SecretsAuditTrail is not AuditTrail

    def test_subclasses_use_new_base(self) -> None:
        """Subclasses inherit from SecretsAuditTrail."""
        from cortex.infrastructure.secrets.audit_trail import (
            SecretsAuditTrail,
            AuditTrailWithSignatures,
            ComplianceAuditTrail,
            ComprehensiveAuditTrail,
        )
        assert issubclass(AuditTrailWithSignatures, SecretsAuditTrail)
        assert issubclass(ComplianceAuditTrail, SecretsAuditTrail)
        assert issubclass(ComprehensiveAuditTrail, SecretsAuditTrail)


class TestSecretsErrorRename:
    """Phase 101: secrets StorageError/PermissionError rename."""

    def test_canonical_import(self) -> None:
        """SecretsStorageError and SecretsPermissionError are importable."""
        from cortex.infrastructure.secrets.errors import SecretsStorageError, SecretsPermissionError
        assert SecretsStorageError is not None
        assert SecretsPermissionError is not None

    def test_backward_compat_aliases(self) -> None:
        """Old names still work via aliases."""
        from cortex.infrastructure.secrets.errors import StorageError, PermissionError
        assert StorageError is not None
        assert PermissionError is not None

    def test_aliases_point_to_canonical(self) -> None:
        """Aliases reference canonical classes."""
        from cortex.infrastructure.secrets.errors import (
            StorageError,
            SecretsStorageError,
            PermissionError as SecretsPerm,
            SecretsPermissionError,
        )
        assert StorageError is SecretsStorageError
        assert SecretsPerm is SecretsPermissionError

    def test_inheritance_chain(self) -> None:
        """Renamed errors still inherit from SecretsError."""
        from cortex.infrastructure.secrets.errors import (
            SecretsError,
            SecretsStorageError,
            SecretsPermissionError,
        )
        assert issubclass(SecretsStorageError, SecretsError)
        assert issubclass(SecretsPermissionError, SecretsError)


class TestDatabaseManagerClose:
    """Phase 101: DatabaseManager.close() no longer a bare pass."""

    def test_close_clears_data(self) -> None:
        """close() should clear internal data dict."""
        from cortex.infrastructure.database import DatabaseManager
        db = DatabaseManager.__new__(DatabaseManager)
        db._initialized = False
        db.__init__()
        db._data["test"] = "value"
        db.close()
        assert db._data == {}
